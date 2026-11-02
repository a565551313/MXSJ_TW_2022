"""Exercise the installed entry point through a real MCP stdio session."""

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_stdio_tools_and_log_pagination():
    async def exercise():
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root / "src")
        executable = os.environ.get("CLIENT_MCP_TEST_EXE")
        params = StdioServerParameters(
            command=executable or sys.executable,
            args=[] if executable else ["-m", "mxsj_client_mcp.run"],
            env=env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert len(tools.tools) == 6
                ping = await session.call_tool("client_ping", {})
                assert json.loads(ping.content[0].text)["result"]["alive"]
                for name in (
                    "client_get_runtime_info",
                    "client_get_module_status",
                    "client_get_native_api_status",
                    "client_get_probe_report",
                ):
                    response = await session.call_tool(name, {})
                    assert not response.isError
                    assert json.loads(response.content[0].text)["ok"] is True
                result = await session.call_tool(
                    "client_read_probe_log", {"limit": 1, "offset": 1}
                )
                page = json.loads(result.content[0].text)["result"]
                assert page["limit"] == 1
                assert page["offset"] == 1
                assert page["entries"] == []

    asyncio.run(exercise())
