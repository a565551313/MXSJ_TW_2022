"""Run the M3 fake-probe MCP server over stdio."""

import argparse

import anyio
from mcp.server.stdio import stdio_server

from .mcp.server import MxsjMcpServer
from .transports.fake_probe import FakeProbeBackend


def build_server(backend=None):
    return MxsjMcpServer(backend if backend is not None else FakeProbeBackend())


async def run_stdio(backend=None):
    server = build_server(backend).get_lowlevel_server()
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mxsj-client-mcp")
    parser.add_argument("--transport", choices=["stdio"], default="stdio")
    parser.add_argument("--probe", choices=["fake", "ipc"], default="fake")
    parser.add_argument("--ipc-host", default="127.0.0.1")
    parser.add_argument("--ipc-port", type=int)
    parser.add_argument("--ipc-token")
    parser.add_argument("--report-file")
    args = parser.parse_args(argv)
    backend = None
    if args.report_file:
        from .transports.ipc_probe import FileProbeBackend
        backend = FileProbeBackend(args.report_file)
    elif args.probe == "ipc":
        if args.ipc_port is None or not args.ipc_token:
            parser.error("--probe ipc requires --ipc-port and --ipc-token")
        from .transports.ipc_probe import IpcProbeBackend
        backend = IpcProbeBackend(
            args.ipc_host, args.ipc_port, args.ipc_token
        )
    anyio.run(run_stdio, backend)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
