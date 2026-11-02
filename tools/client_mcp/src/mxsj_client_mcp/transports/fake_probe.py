"""In-process fake probe backend for Linux development mode (M3).

It emulates a probe running inside the client's script VM, answering the
read-only method set from docs/PROTOCOL.md §4 with synthetic but structured
data. It is NOT a real client and its passing tests must never be reported as
Windows native-acceptance (see docs/ARCHITECTURE.md §3.2 and §5).
"""

from __future__ import annotations

import copy
import time
from typing import Any

from ..core.protocol import (
    PROBE_VERSION,
    PROTOCOL_VERSION,
    ErrorCode,
    Message,
    new_session_id,
)
from .backend import BackendResult, ProbeBackend

# Synthetic baseline sha from docs (locked baseline). The fake probe reports a
# derived test-package sha so the report schema is exercised.
_FAKE_BASELINE_SHA = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
_FAKE_PACKAGE_SHA = "f" * 64


class FakeProbeBackend(ProbeBackend):
    """Emulates a read-only client probe in-process."""

    def __init__(self, *, probe_session: str | None = None) -> None:
        self._session = probe_session or new_session_id()
        self._modules = [
            {"name": "boot", "state": "loaded", "vm": "py25"},
            {"name": "login", "state": "loaded", "vm": "py25"},
            {"name": "ui", "state": "loaded", "vm": "py25"},
            {"name": "net", "state": "loaded", "vm": "py27"},
        ]
        self._native_api = [
            {"name": "GetWindowTextA", "available": True},
            {"name": "SendMessageW", "available": True},
            {"name": "CreateFileW", "available": False},
        ]
        self._log: list[dict[str, Any]] = [
            {
                "ts": "2026-11-02T00:00:00+08:00",
                "level": "info",
                "msg": "fake probe started",
            },
        ]

    # -- ProbeBackend interface -------------------------------------------

    def latest_session(self) -> str | None:
        return self._session

    def handle_event(self, evt: Message) -> None:
        # The fake probe registers itself on a hello event carrying data.
        if evt.event == "probe.hello" and isinstance(evt.data, dict):
            claimed = evt.data.get("session")
            if claimed:
                self._session = str(claimed)

    def handle_request(self, req: Message) -> BackendResult:
        if type(req.v) is not int or req.v != PROTOCOL_VERSION:
            return BackendResult(ok=False, error_code=ErrorCode.PROTOCOL_VERSION)
        if req.kind != "request":
            return BackendResult(ok=False, error_code=ErrorCode.NOT_ALLOWED)
        if req.session != self._session:
            return BackendResult(ok=False, error_code=ErrorCode.SESSION)
        if not isinstance(req.params, dict):
            return BackendResult(ok=False, error_code=ErrorCode.NOT_ALLOWED)
        method = req.method
        if not isinstance(method, str):
            return BackendResult(
                ok=False,
                error_code=ErrorCode.NOT_ALLOWED,
                error_detail="missing method",
            )
        if method not in {
            "probe.heartbeat",
            "probe.get_runtime",
            "probe.get_modules",
            "probe.get_native_api",
            "probe.get_report",
            "probe.read_log",
        }:
            return BackendResult(
                ok=False,
                error_code=ErrorCode.NOT_ALLOWED,
                error_detail=f"method {method} not in read-only stage",
            )
        handler = getattr(self, f"_m_{method.split('.')[-1]}", None)
        if handler is None:
            return BackendResult(
                ok=False,
                error_code=ErrorCode.INTERNAL,
                error_detail=f"no handler for {method}",
            )
        if method == "probe.read_log":
            params = req.params
            limit, offset = params.get("limit", 50), params.get("offset", 0)
            if (
                set(params) - {"limit", "offset"}
                or type(limit) is not int
                or not 1 <= limit <= 200
                or type(offset) is not int
                or offset < 0
            ):
                return BackendResult(
                    ok=False,
                    error_code=ErrorCode.NOT_ALLOWED,
                    error_detail="invalid pagination",
                )
            return BackendResult(
                ok=True, result=copy.deepcopy(handler(limit=limit, offset=offset))
            )
        if req.params:
            return BackendResult(
                ok=False,
                error_code=ErrorCode.NOT_ALLOWED,
                error_detail="unexpected parameters",
            )
        return BackendResult(ok=True, result=copy.deepcopy(handler()))

    # -- read-only method handlers ---------------------------------------

    def _m_heartbeat(self) -> dict[str, Any]:
        return {
            "alive": True,
            "main_loop_ticks": 1,
            "session": self._session,
        }

    def _m_get_runtime(self) -> dict[str, Any]:
        return {
            "vm": "py25",
            "vm_version": "2.5.6",
            "pid": 4242,
            "threads": 8,
            "uptime_s": int(time.time()) % 100000,
            "clock": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }

    def _m_get_modules(self) -> dict[str, Any]:
        return {
            "count": len(self._modules),
            "modules": list(self._modules),
        }

    def _m_get_native_api(self) -> dict[str, Any]:
        return {
            "count": len(self._native_api),
            "apis": list(self._native_api),
        }

    def _m_get_report(self) -> dict[str, Any]:
        return {
            "probe_version": PROBE_VERSION,
            "protocol_version": PROTOCOL_VERSION,
            "client_build": {
                "script_fls_sha256": _FAKE_PACKAGE_SHA,
                "baseline_sha256": _FAKE_BASELINE_SHA,
                "vm": "py25",
            },
            "capabilities": [
                "runtime",
                "modules",
                "native_api_status",
                "probe_log",
            ],
            "runtime": self._m_get_runtime(),
            "modules": self._m_get_modules(),
            "native_api": self._m_get_native_api(),
        }

    def _m_read_log(self, *, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        page = self._log[offset : offset + limit]
        return {
            "total": len(self._log),
            "offset": offset,
            "limit": limit,
            "entries": list(page),
        }

    def read_log_paged(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        return self._m_read_log(limit=limit, offset=offset)
