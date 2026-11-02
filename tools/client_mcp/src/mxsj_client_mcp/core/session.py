"""Session and control-lock bookkeeping for the MCP server.

The server tracks MCP client sessions, probe sessions and (future) control
locks. In the read-only stage (M3) only probe session registration, heartbeat
and report storage are used; the control lock is implemented but not opened.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .protocol import ErrorCode, new_session_id

# How long a probe session may be idle before it is considered stale.
SESSION_IDLE_TIMEOUT_S = 30.0


@dataclass
class ProbeSession:
    """One registered probe session."""

    session_id: str
    probe_version: str = ""
    protocol_version: int = 0
    client_build: dict[str, Any] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    last_report: dict[str, Any] | None = None
    probe_log: list[dict[str, Any]] = field(default_factory=list)

    def touch(self) -> None:
        self.last_seen = time.time()

    def is_stale(self) -> bool:
        return (time.time() - self.last_seen) > SESSION_IDLE_TIMEOUT_S


class SessionRegistry:
    """Holds the currently active probe sessions keyed by session id."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, ProbeSession] = {}

    def register_hello(self, *, probe_version: str, protocol_version: int,
                       client_build: dict[str, Any],
                       capabilities: list[str]) -> ProbeSession:
        with self._lock:
            session = ProbeSession(
                session_id=new_session_id(),
                probe_version=probe_version,
                protocol_version=protocol_version,
                client_build=client_build,
                capabilities=capabilities,
            )
            self._sessions[session.session_id] = session
            return session

    def get(self, session_id: str) -> ProbeSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def heartbeat(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.touch()
            return True

    def store_report(self, session_id: str, report: dict[str, Any]) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.last_report = report
            session.touch()
            return True

    def append_log(self, session_id: str, entry: dict[str, Any]) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.probe_log.append(entry)
            session.touch()
            return True

    def prune_stale(self) -> int:
        with self._lock:
            stale = [sid for sid, s in self._sessions.items() if s.is_stale()]
            for sid in stale:
                del self._sessions[sid]
            return len(stale)


@dataclass
class ControlLock:
    """Exclusive control lock for future control operations (M4+).

    Read-only stage never acquires it. The lock has a holder id and an
    expiry so a crashed client cannot occupy the client forever.
    """

    holder: str | None = None
    acquired_at: float = 0.0
    expires_at: float = 0.0

    def try_acquire(
        self, holder: str, *, ttl_s: float = 60.0
    ) -> tuple[bool, ErrorCode | None]:
        now = time.time()
        if self.holder is not None and self.expires_at > now:
            return False, ErrorCode.BUSY
        self.holder = holder
        self.acquired_at = now
        self.expires_at = now + ttl_s
        return True, None

    def release(self, holder: str) -> bool:
        if self.holder != holder:
            return False
        self.holder = None
        self.acquired_at = 0.0
        self.expires_at = 0.0
        return True

    def is_held(self) -> bool:
        return self.holder is not None and self.expires_at > time.time()


def make_client_session_id() -> str:
    """Stable unique id for an MCP client connection."""
    return f"mcp-{uuid.uuid4().hex[:12]}"
