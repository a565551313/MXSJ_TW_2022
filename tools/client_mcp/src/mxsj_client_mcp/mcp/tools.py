"""Read-only MCP tool surface (M3).

Each tool maps to a probe method from docs/PROTOCOL.md §8 / docs/MCP_CLIENTS.md §2.
All six tools are read-only and may run concurrently. Control tools (M4+) are
deliberately absent so the server cannot perform mutating actions yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp.types import TextContent, Tool

from ..core.protocol import ErrorCode, make_request
from ..core.redact import redact
from ..transports.backend import BackendResult, ProbeBackend, result_to_message

# Tool name -> probe method. The MCP client never talks to the probe IPC directly.
TOOL_METHODS: dict[str, str] = {
    "client_ping": "probe.heartbeat",
    "client_get_runtime_info": "probe.get_runtime",
    "client_get_module_status": "probe.get_modules",
    "client_get_native_api_status": "probe.get_native_api",
    "client_get_probe_report": "probe.get_report",
    "client_read_probe_log": "probe.read_log",
}

TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="client_ping",
        description="Check whether the MCP server has a live probe session.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="client_get_runtime_info",
        description="Read client VM / process / thread basic info (read-only).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="client_get_module_status",
        description="Read script module load status (read-only).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="client_get_native_api_status",
        description="Read native module availability (no dangerous calls).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="client_get_probe_report",
        description="Read the aggregated read-only probe report.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="client_read_probe_log",
        description="Read the probe's own redacted log (read-only).",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "offset": {"type": "integer", "minimum": 0},
            },
        },
    ),
]


@dataclass
class ToolCallContext:
    """Per-call context the server passes to a tool handler."""

    session: str
    mcp_client: str


def _text(data: Any) -> list[TextContent]:
    import json

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    return [TextContent(type="text", text=payload)]


class ToolRegistry:
    """Dispatches MCP tool calls to the probe backend."""

    def __init__(self, backend: ProbeBackend) -> None:
        self._backend = backend

    def list_tools(self) -> list[Tool]:
        return list(TOOL_DEFINITIONS)

    def _dispatch(self, method: str, session: str) -> BackendResult:
        req = make_request(session, method)
        res = self._backend.handle_request(req)
        # Convert to a response message just to reuse error shaping; the result
        # payload is what the tool returns.
        _ = result_to_message(req, res)
        return res

    async def call(
        self, name: str, arguments: dict[str, Any], ctx: ToolCallContext
    ) -> list[TextContent]:
        if name not in TOOL_METHODS:
            return _text(
                {
                    "ok": False,
                    "error": {
                        "code": ErrorCode.NOT_ALLOWED.value,
                        "detail": f"unknown tool {name}",
                    },
                }
            )
        method = TOOL_METHODS[name]
        session = ctx.session
        if session is None:
            return _text(
                {
                    "ok": False,
                    "error": {
                        "code": ErrorCode.SESSION.value,
                        "detail": "no probe session registered",
                    },
                }
            )
        params: dict[str, Any] = {}
        allowed = {"limit", "offset"} if name == "client_read_probe_log" else set()
        if not isinstance(arguments, dict) or set(arguments) - allowed:
            return _text(
                {
                    "ok": False,
                    "error": {
                        "code": ErrorCode.NOT_ALLOWED.value,
                        "detail": "invalid arguments",
                    },
                }
            )
        if name == "client_read_probe_log":
            limit, offset = arguments.get("limit", 50), arguments.get("offset", 0)
            if (
                type(limit) is not int
                or not 1 <= limit <= 200
                or type(offset) is not int
                or offset < 0
            ):
                return _text(
                    {
                        "ok": False,
                        "error": {
                            "code": ErrorCode.NOT_ALLOWED.value,
                            "detail": "invalid pagination",
                        },
                    }
                )
            params = {"limit": limit, "offset": offset}
        # Route through the backend as a real request so protocol validation
        # and method whitelist are exercised uniformly.
        req = make_request(session, method, params)
        res = self._backend.handle_request(req)
        if not res.ok:
            return _text(
                {
                    "ok": False,
                    "error": {
                        "code": (res.error_code or ErrorCode.INTERNAL).value,
                        "detail": "probe request failed",
                    },
                }
            )
        return _text({"ok": True, "result": redact(res.result)})
