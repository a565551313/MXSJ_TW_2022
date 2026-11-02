"""Read-only MCP server backed by a probe transport."""

from mcp.server.lowlevel import Server

from .tools import ToolCallContext, ToolRegistry


class MxsjMcpServer:
    def __init__(self, backend):
        self._backend = backend
        self._tools = ToolRegistry(backend)
        self._server = Server("mxsj-client-mcp")

        @self._server.list_tools()
        async def list_tools():
            return self._tools.list_tools()

        @self._server.call_tool()
        async def call_tool(name, arguments):
            ctx = ToolCallContext(
                session=self._backend.latest_session(), mcp_client="stdio"
            )
            return await self._tools.call(name, arguments or {}, ctx)

    def get_lowlevel_server(self):
        return self._server

    async def list_tools(self):
        return self._tools.list_tools()
