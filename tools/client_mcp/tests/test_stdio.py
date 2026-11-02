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


def test_stdio_reads_cpython25_report_file(tmp_path):
    async def exercise():
        root = Path(__file__).resolve().parents[1]
        report = tmp_path / "mxsj_probe_report.txt"
        report.write_text(
            "{'runtime': {'python_version': [2, 5, 0], 'pid': None}, "
            "'modules': {'modules': []}, 'native_api': {'status': 'unknown', "
            "'apis': []}, 'probe_version': '0.1.0'}",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root / "src")
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mxsj_client_mcp.run", "--report-file", str(report)],
            env=env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                ping = await session.call_tool("client_ping", {})
                assert json.loads(ping.content[0].text)["result"]["alive"] is True
                response = await session.call_tool("client_get_probe_report", {})
                payload = json.loads(response.content[0].text)
                assert payload["ok"] is True
                assert payload["result"]["runtime"]["python_version"] == [2, 5, 0]
                assert payload["result"]["probe_version"] == "0.1.0"

    asyncio.run(exercise())
