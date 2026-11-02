"""Local Streamable HTTP transport with bearer-token authentication.

The first HTTP version is intentionally loopback-only.  It exposes the same
read-only MCP tool surface as stdio and does not enable control operations.
"""

from __future__ import annotations

import hmac
from contextlib import asynccontextmanager

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount

MAX_HTTP_BODY_BYTES = 256 * 1024
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _host_header_values(host: str, port: int) -> list[str]:
    if host == "::1":
        return [f"[::1]:{port}", f"localhost:{port}"]
    return [f"127.0.0.1:{port}", f"localhost:{port}"]


def _origin_header_values(host: str, port: int) -> list[str]:
    return [f"http://{value}" for value in _host_header_values(host, port)]


def create_http_app(
    mcp_server,
    *,
    token: str,
    host: str = "127.0.0.1",
    port: int = 8765,
):
    """Create a Starlette ASGI app serving MCP at ``/mcp``.

    ``token`` is required and compared in constant time.  DNS-rebinding
    protection is enabled with explicit loopback Host/Origin allowlists.
    """
    if not isinstance(token, str) or not token:
        raise ValueError("HTTP token is required")
    if host not in LOOPBACK_HOSTS:
        raise ValueError("HTTP transport is loopback-only in this version")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("HTTP port is invalid")

    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=_host_header_values(host, port),
        allowed_origins=_origin_header_values(host, port),
    )
    manager = StreamableHTTPSessionManager(
        app=mcp_server,
        json_response=True,
        stateless=False,
        security_settings=security,
        max_request_body_size=MAX_HTTP_BODY_BYTES,
        max_sessions=16,
    )
    expected = b"Bearer " + token.encode("utf-8")

    async def authenticated_mcp(scope, receive, send):
        if scope["type"] == "http":
            if scope.get("path") not in ("/mcp", "/mcp/"):
                response = JSONResponse(
                    {"ok": False, "error": "not_found"}, status_code=404
                )
                await response(scope, receive, send)
                return
            authorization = b""
            for key, value in scope.get("headers", []):
                if key.lower() == b"authorization":
                    authorization = value
                    break
            if not hmac.compare_digest(authorization, expected):
                response = JSONResponse(
                    {"ok": False, "error": "unauthorized"}, status_code=401
                )
                await response(scope, receive, send)
                return
        await manager.handle_request(scope, receive, send)

    @asynccontextmanager
    async def lifespan(app):
        async with manager.run():
            yield

    return Starlette(
        routes=[Mount("/", app=authenticated_mcp)],
        lifespan=lifespan,
    )


__all__ = ["create_http_app"]
