"""Tests for the fake probe backend and the tool registry wiring."""

import asyncio
import json

import pytest

from mxsj_client_mcp.core.protocol import ErrorCode, make_request
from mxsj_client_mcp.mcp.server import MxsjMcpServer
from mxsj_client_mcp.mcp.tools import ToolCallContext, ToolRegistry
from mxsj_client_mcp.transports.backend import BackendResult
from mxsj_client_mcp.transports.fake_probe import FakeProbeBackend


@pytest.fixture
def backend():
    return FakeProbeBackend()


def test_fake_probe_read_only_methods(backend):
    for method in [
        "probe.heartbeat",
        "probe.get_runtime",
        "probe.get_modules",
        "probe.get_native_api",
        "probe.get_report",
        "probe.read_log",
    ]:
        req = make_request(backend.latest_session(), method)
        res = backend.handle_request(req)
        assert res.ok, f"{method} should succeed: {res.error_detail}"
        assert res.result is not None


def test_fake_probe_rejects_control_methods(backend):
    req = make_request(backend.latest_session(), "probe.invoke")
    res = backend.handle_request(req)
    assert not res.ok
    assert res.error_code.value == "E_NOT_ALLOWED"


def test_fake_probe_report_has_baseline_sha(backend):
    req = make_request(backend.latest_session(), "probe.get_report")
    res = backend.handle_request(req)
    sha = res.result["client_build"]["baseline_sha256"]
    assert sha.startswith("8b6e9266")


def test_tool_registry_ping(backend):
    reg = ToolRegistry(backend)
    ctx = ToolCallContext(session=backend.latest_session(), mcp_client="test")
    out = asyncio.run(reg.call("client_ping", {}, ctx))
    text = out[0].text
    assert '"ok": true' in text


def test_tool_registry_unknown_tool(backend):
    reg = ToolRegistry(backend)
    ctx = ToolCallContext(session=backend.latest_session(), mcp_client="test")
    out = asyncio.run(reg.call("client_hack", {}, ctx))
    assert '"ok": false' in out[0].text


def test_server_exposes_six_readonly_tools():
    server = MxsjMcpServer(FakeProbeBackend())

    async def _collect():
        tools = await server.list_tools()
        return {t.name for t in tools}

    names = asyncio.run(_collect())
    assert len(names) == 6
    assert "client_get_probe_report" in names
    assert "client_read_probe_log" in names
    assert "client_invoke_allowed_action" not in names


def test_backend_rejects_invalid_envelopes_and_pagination(backend):
    req = make_request("wrong", "probe.heartbeat")
    assert backend.handle_request(req).error_code == ErrorCode.SESSION
    req.session = backend.latest_session()
    req.v = 2
    assert backend.handle_request(req).error_code == ErrorCode.PROTOCOL_VERSION
    req.v = 1
    req.kind = "event"
    assert not backend.handle_request(req).ok
    for params in ({"limit": -1}, {"offset": True}, {"limit": "x"}, {"extra": 1}):
        req = make_request(backend.latest_session(), "probe.read_log", params)
        assert not backend.handle_request(req).ok


def test_tool_validates_pagination_and_preserves_report_hash(backend):
    reg = ToolRegistry(backend)
    ctx = ToolCallContext(session=backend.latest_session(), mcp_client="test")
    for arguments in ({"limit": -1}, {"offset": True}, {"limit": "x"}, {"extra": 1}):
        result = asyncio.run(reg.call("client_read_probe_log", arguments, ctx))
        assert json.loads(result[0].text)["ok"] is False
    result = asyncio.run(reg.call("client_get_probe_report", {}, ctx))
    build = json.loads(result[0].text)["result"]["client_build"]
    assert build["baseline_sha256"].startswith("8b6e9266")


def test_tool_does_not_expose_backend_error_details(backend, monkeypatch):
    monkeypatch.setattr(backend, "handle_request", lambda _: BackendResult(
        ok=False, error_code=ErrorCode.INTERNAL, error_detail="password=hunter2"
    ))
    ctx = ToolCallContext(session=backend.latest_session(), mcp_client="test")
    result = asyncio.run(ToolRegistry(backend).call("client_ping", {}, ctx))
    assert "hunter2" not in result[0].text


def test_fake_response_does_not_expose_mutable_backend_state(backend):
    req = make_request(backend.latest_session(), "probe.get_modules")
    backend.handle_request(req).result["modules"][0]["name"] = "changed"
    assert backend.handle_request(req).result["modules"][0]["name"] == "boot"
