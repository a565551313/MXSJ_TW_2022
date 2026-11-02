"""IPC protocol model between the MCP server and the client-internal probe.

This is NOT the game TCP protocol and NOT the MCP protocol itself. It is the
local test channel that the MCP server uses to talk to a probe running inside
the client's script VM. The message envelope follows docs/PROTOCOL.md.

Stage M3 only deals with the read-only method set; control methods are declared
here for the whitelist but not callable yet.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 256 * 1024  # 256 KiB, per docs/PROTOCOL.md §7
DEFAULT_REQUEST_TIMEOUT_S = 5.0
PROBE_VERSION = "0.1.0"


class ErrorCode(str, Enum):
    """Protocol error codes, mirroring docs/PROTOCOL.md §6."""

    PROTOCOL_VERSION = "E_PROTOCOL_VERSION"
    SESSION = "E_SESSION"
    TIMEOUT = "E_TIMEOUT"
    NOT_ALLOWED = "E_NOT_ALLOWED"
    BUSY = "E_BUSY"
    CLIENT_STATE = "E_CLIENT_STATE"
    NATIVE_API = "E_NATIVE_API"
    REDACTED = "E_REDACTED"
    INTERNAL = "E_INTERNAL"


# Read-only stage (M2/M3). These may be dispatched to the probe.
READONLY_METHODS = {
    "probe.hello",
    "probe.heartbeat",
    "probe.get_runtime",
    "probe.get_modules",
    "probe.get_native_api",
    "probe.get_report",
    "probe.read_log",
}

# Control stage (M4+). Declared for the whitelist, not callable in M3.
CONTROL_METHODS = {
    "probe.get_ui_state",
    "probe.get_game_state",
    "probe.invoke",
    "probe.run_scenario",
}


@dataclass
class Message:
    """A single protocol message envelope.

    ``id`` is always a string. ``kind`` is one of request/response/event.
    ``session`` is a session uuid string. ``ts`` is an ISO-8601 timestamp.
    """

    v: int
    kind: str
    id: str
    session: str
    method: str | None = None
    event: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    result: Any | None = None
    ok: bool | None = None
    error: dict[str, Any] | None = None
    data: Any | None = None
    ts: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "v": self.v,
            "kind": self.kind,
            "id": self.id,
            "session": self.session,
            "ts": self.ts,
        }
        if self.method is not None:
            d["method"] = self.method
        if self.event is not None:
            d["event"] = self.event
        if self.params:
            d["params"] = self.params
        if self.result is not None:
            d["result"] = self.result
        if self.ok is not None:
            d["ok"] = self.ok
        if self.error is not None:
            d["error"] = self.error
        if self.data is not None:
            d["data"] = self.data
        return d

    def encode(self) -> bytes:
        """Serialize to UTF-8 JSON bytes, enforcing the size limit."""
        raw = json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))
        data = raw.encode("utf-8")
        if len(data) > MAX_MESSAGE_BYTES:
            raise ValueError(
                f"message exceeds {MAX_MESSAGE_BYTES} bytes "
                f"({len(data)})"
            )
        return data

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Message:
        if not isinstance(d, dict):
            raise ValueError("message must be an object")
        if (type(d.get("v")) is not int or not isinstance(d.get("kind"), str)
                or d["kind"] not in {"request", "response", "event"}):
            raise ValueError("invalid message version or kind")
        if any(not isinstance(d.get(key), str) or not d[key]
               for key in ("id", "session")):
            raise ValueError("invalid message identity")
        if "params" in d and not isinstance(d["params"], dict):
            raise ValueError("params must be an object")
        return cls(
            v=d["v"],
            kind=d["kind"],
            id=d["id"],
            session=d["session"],
            method=d.get("method"),
            event=d.get("event"),
            params=d.get("params") or {},
            result=d.get("result"),
            ok=d.get("ok"),
            error=d.get("error"),
            data=d.get("data"),
            ts=d.get("ts", ""),
        )

    @classmethod
    def decode(cls, raw: bytes) -> Message:
        if len(raw) > MAX_MESSAGE_BYTES:
            raise ValueError(
                f"message exceeds {MAX_MESSAGE_BYTES} bytes ({len(raw)})"
            )
        return cls.from_dict(json.loads(raw.decode("utf-8")))


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def new_session_id() -> str:
    return f"session-{uuid.uuid4().hex}"


def new_message_id(prefix: str = "req") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def make_request(
    session: str,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    id_prefix: str = "req",
) -> Message:
    """Build a request message for a probe method."""
    return Message(
        v=PROTOCOL_VERSION,
        kind="request",
        id=new_message_id(id_prefix),
        session=session,
        method=method,
        params=params or {},
        ts=_now_iso(),
    )


def make_response(
    req: Message,
    ok: bool,
    result: Any = None,
    error: dict[str, Any] | None = None,
) -> Message:
    """Build a response message that answers a request."""
    return Message(
        v=PROTOCOL_VERSION,
        kind="response",
        id=req.id,
        session=req.session,
        ok=ok,
        result=result,
        error=error,
        ts=_now_iso(),
    )


def make_event(
    session: str, event: str, data: Any = None, *, id_prefix: str = "evt"
) -> Message:
    """Build an event message (e.g. probe.hello)."""
    return Message(
        v=PROTOCOL_VERSION,
        kind="event",
        id=new_message_id(id_prefix),
        session=session,
        event=event,
        data=data,
        ts=_now_iso(),
    )


def make_error_response(req: Message, code: ErrorCode, detail: str) -> Message:
    """Build a standard error response for a request."""
    return make_response(
        req,
        ok=False,
        error={"code": code.value, "detail": detail},
    )


def is_method_allowed(method: str) -> bool:
    """Return True if the method belongs to the callable read-only stage."""
    return method in READONLY_METHODS
