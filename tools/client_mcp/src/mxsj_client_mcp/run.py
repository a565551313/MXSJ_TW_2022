"""Run the read-only MCP server over stdio or loopback Streamable HTTP."""

import argparse
import os

import anyio
from mcp.server.stdio import stdio_server

from .mcp.server import MxsjMcpServer
from .transports.fake_probe import FakeProbeBackend


def build_server(backend=None):
    return MxsjMcpServer(backend if backend is not None else FakeProbeBackend())


def build_backend(args):
    if args.report_file:
        from .transports.ipc_probe import FileProbeBackend

        return FileProbeBackend(args.report_file)
    if args.probe == "ipc":
        if args.ipc_port is None or not args.ipc_token:
            raise ValueError("--probe ipc requires --ipc-port and --ipc-token")
        from .transports.ipc_probe import IpcProbeBackend

        return IpcProbeBackend(args.ipc_host, args.ipc_port, args.ipc_token)
    return FakeProbeBackend()


async def run_stdio(backend=None):
    server = build_server(backend).get_lowlevel_server()
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


async def run_http(backend=None, *, host="127.0.0.1", port=8765, token=None):
    import uvicorn

    from .transports.http import create_http_app

    if not token:
        raise ValueError("HTTP transport requires --http-token or MXSJ_MCP_HTTP_TOKEN")
    app = create_http_app(
        build_server(backend).get_lowlevel_server(),
        token=token,
        host=host,
        port=port,
    )
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
        lifespan="on",
    )
    server = uvicorn.Server(config)
    await server.serve()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mxsj-client-mcp")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--probe", choices=["fake", "ipc"], default="fake")
    parser.add_argument("--ipc-host", default="127.0.0.1")
    parser.add_argument("--ipc-port", type=int)
    parser.add_argument("--ipc-token")
    parser.add_argument("--report-file")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--http-token", default=os.environ.get("MXSJ_MCP_HTTP_TOKEN"))
    args = parser.parse_args(argv)
    try:
        backend = build_backend(args)
    except ValueError as exc:
        parser.error(str(exc))
    if args.transport == "stdio":
        anyio.run(run_stdio, backend)
    else:
        from .transports.http import LOOPBACK_HOSTS

        if not args.http_token:
            parser.error("HTTP transport requires --http-token or MXSJ_MCP_HTTP_TOKEN")
        if args.host not in LOOPBACK_HOSTS:
            parser.error("HTTP transport is loopback-only in this version")
        if not 1 <= args.port <= 65535:
            parser.error("HTTP port is invalid")

        async def _run_http():
            await run_http(
                backend, host=args.host, port=args.port, token=args.http_token
            )

        anyio.run(_run_http)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
