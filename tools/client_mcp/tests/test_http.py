"""Loopback Streamable HTTP transport tests.

These tests exercise the real MCP HTTP client against a subprocess server.
They do not prove Windows game-client acceptance; they prove the host transport.
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_port(port: int, proc: subprocess.Popen, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            stderr = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(f"server exited early: {stderr}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise TimeoutError("HTTP server did not start")


def _server(args, env=None):
    full_env = os.environ.copy()
    full_env["PYTHONPATH"] = str(ROOT / "src")
    if env:
        full_env.update(env)
    return subprocess.Popen(
        [sys.executable, "-m", "mxsj_client_mcp.run", *args],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=full_env,
        text=True,
    )


def test_http_requires_bearer_token(tmp_path):
    port = _free_port()
    report = tmp_path / "report.txt"
    report.write_text(
        "{'probe_version': '0.1.0', 'runtime': {'python_version': [2, 5, 0]}, "
        "'modules': {'modules': []}, 'native_api': {'status': 'unknown', 'apis': []}}",
        encoding="utf-8",
    )
    proc = _server(
        [
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--http-token",
            "test-token",
            "--report-file",
            str(report),
        ]
    )
    try:
        _wait_port(port, proc)
        url = f"http://127.0.0.1:{port}/mcp"
        assert httpx.get(url, timeout=5).status_code == 401
        assert (
            httpx.get(
                url, headers={"Authorization": "Bearer wrong"}, timeout=5
            ).status_code
            == 401
        )

        async def exercise():
            headers = {"Authorization": "Bearer test-token"}
            async with httpx.AsyncClient(headers=headers, timeout=30) as http_client:
                async with streamable_http_client(url, http_client=http_client) as (
                    read,
                    write,
                    _,
                ):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        assert len(tools.tools) == 6
                        ping = await session.call_tool("client_ping", {})
                        assert (
                            json.loads(ping.content[0].text)["result"]["alive"] is True
                        )
                        response = await session.call_tool(
                            "client_get_probe_report", {}
                        )
                        payload = json.loads(response.content[0].text)
                        assert payload["ok"] is True
                        assert payload["result"]["runtime"]["python_version"] == [
                            2,
                            5,
                            0,
                        ]

        asyncio.run(exercise())
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_http_two_clients_read_concurrently():
    port = _free_port()
    proc = _server(
        [
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--http-token",
            "test-token",
        ]
    )
    try:
        _wait_port(port, proc)
        url = f"http://127.0.0.1:{port}/mcp"

        async def client_once():
            headers = {"Authorization": "Bearer test-token"}
            async with httpx.AsyncClient(headers=headers, timeout=30) as http_client:
                async with streamable_http_client(url, http_client=http_client) as (
                    read,
                    write,
                    _,
                ):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        response = await session.call_tool(
                            "client_get_probe_report", {}
                        )
                        payload = json.loads(response.content[0].text)
                        assert payload["ok"] is True
                        return payload["result"]["probe_version"]

        async def exercise():
            return await asyncio.gather(client_once(), client_once())

        versions = asyncio.run(exercise())
        assert len(versions) == 2
        assert all(isinstance(v, str) and v for v in versions)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_http_rejects_bad_host_origin_and_oversized_body():
    port = _free_port()
    proc = _server(
        [
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--http-token",
            "test-token",
        ]
    )
    try:
        _wait_port(port, proc)
        url = f"http://127.0.0.1:{port}/mcp"
        auth = {"Authorization": "Bearer test-token"}
        assert (
            httpx.get(
                url, headers={**auth, "Host": "evil.example"}, timeout=5
            ).status_code
            == 421
        )
        assert (
            httpx.get(
                url, headers={**auth, "Origin": "http://evil.example"}, timeout=5
            ).status_code
            == 403
        )
        response = httpx.post(
            url,
            headers={
                **auth,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            content=b" " * (256 * 1024 + 1),
            timeout=5,
        )
        assert response.status_code == 413
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_http_rejects_non_loopback_host():
    port = _free_port()
    proc = _server(
        [
            "--transport",
            "http",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--http-token",
            "test-token",
        ]
    )
    try:
        proc.wait(timeout=10)
        assert proc.returncode != 0
        stderr = proc.stderr.read() if proc.stderr else ""
        assert "loopback-only" in stderr
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
