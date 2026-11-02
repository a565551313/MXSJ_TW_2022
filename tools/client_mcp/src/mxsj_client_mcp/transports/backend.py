"""Probe backend abstraction.

The MCP server talks to a probe through :class:`ProbeBackend`. Two implementations
exist:

* :class:`~mxsj_client_mcp.transports.fake_probe.FakeProbeBackend` — runs in-process
  on Linux for protocol/transport/test verification (M3 dev mode).
* (future) a real IPC backend that connects to a probe inside the Windows client
  via named pipe / loopback TCP / file polling (M2/M3 Windows mode).

The backend is deliberately transport-agnostic: the server only sees request/event
messages and structured results.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any

from ..core.protocol import ErrorCode, Message, make_error_response, make_response


@dataclass
class BackendResult:
    """Outcome of dispatching one probe request through the backend."""

    ok: bool
    result: Any | None = None
    error_code: ErrorCode | None = None
    error_detail: str = ""


class ProbeBackend(abc.ABC):
    """Common interface for every probe backend."""

    @abc.abstractmethod
    def handle_request(self, req: Message) -> BackendResult:
        """Handle one request message and return a structured result."""

    @abc.abstractmethod
    def handle_event(self, evt: Message) -> None:
        """Consume one event message (e.g. probe.hello)."""

    @abc.abstractmethod
    def latest_session(self) -> str | None:
        """Return the most recently registered probe session id, if any."""


def result_to_message(req: Message, res: BackendResult) -> Message:
    """Wrap a :class:`BackendResult` back into a protocol response message."""
    if res.ok:
        return make_response(req, ok=True, result=res.result)
    code = res.error_code or ErrorCode.INTERNAL
    return make_error_response(req, code, res.error_detail)


__all__ = [
    "BackendResult",
    "ProbeBackend",
    "result_to_message",
]
