"""Tests for the protocol message model and redaction."""

import json

import pytest

from mxsj_client_mcp.core.protocol import (
    PROTOCOL_VERSION,
    ErrorCode,
    Message,
    is_method_allowed,
    make_error_response,
    make_request,
    make_response,
)
from mxsj_client_mcp.core.redact import redact


def _roundtrip(msg):
    raw = msg.encode()
    return type(msg).decode(raw)


def test_request_encode_decode_roundtrip():
    req = make_request("session-1", "probe.heartbeat", {"a": 1})
    assert req.v == PROTOCOL_VERSION
    assert req.kind == "request"
    back = _roundtrip(req)
    assert back.id == req.id
    assert back.session == req.session
    assert back.method == "probe.heartbeat"
    assert back.params == {"a": 1}
    assert back.ts


def test_response_roundtrip_carries_request_id():
    req = make_request("session-1", "probe.heartbeat")
    resp = make_response(req, ok=True, result={"alive": True})
    assert resp.id == req.id
    assert resp.ok is True
    assert resp.result == {"alive": True}
    back = _roundtrip(resp)
    assert back.id == req.id and back.ok is True


def test_error_response_shape():
    req = make_request("s", "probe.heartbeat")
    err = make_error_response(req, ErrorCode.NOT_ALLOWED, "nope")
    assert err.ok is False
    assert err.error == {"code": "E_NOT_ALLOWED", "detail": "nope"}


def test_message_size_limit_enforced():
    request = make_request("s", "probe.heartbeat")
    big = make_response(request, ok=True, result="x" * (300 * 1024))
    try:
        big.encode()
    except ValueError:
        pass
    else:
        raise AssertionError("expected size error")


def test_method_allowlist_read_only():
    assert is_method_allowed("probe.heartbeat")
    assert is_method_allowed("probe.get_report")
    assert not is_method_allowed("probe.invoke")
    assert not is_method_allowed("probe.run_scenario")


def test_redact_masks_sensitive_keys():
    data = {
        "account": "alice",
        "password": "secret123",
        "ticket": "long-token-1234567890abcdef",
        "modules": [{"name": "boot"}],
        "note": "contact me at alice@example.invalid",
    }
    out = redact(data)
    assert out["password"] == "[REDACTED]"
    assert out["ticket"] == "[REDACTED]"
    assert out["account"] == "[REDACTED]"  # account is a sensitive key
    assert out["modules"][0]["name"] == "boot"
    assert "[REDACTED_EMAIL]" in out["note"]


def test_redact_long_secret_string():
    data = {"token_field": "x" * 48}
    out = redact(data)
    assert out["token_field"] == "[REDACTED]"


def test_json_serializable():
    # ensure encode output is valid JSON
    msg = make_request("s", "probe.heartbeat", {"k": [1, 2, 3]})
    obj = json.loads(msg.encode().decode("utf-8"))
    assert obj["params"]["k"] == [1, 2, 3]


@pytest.mark.parametrize("changes", [
    {"v": True}, {"kind": "other"}, {"id": 12},
    {"session": ""}, {"params": []},
])
def test_decode_rejects_invalid_envelope(changes):
    obj = make_request("s", "probe.heartbeat").to_dict()
    obj.update(changes)
    with pytest.raises(ValueError):
        Message.decode(json.dumps(obj).encode())


def test_redact_normalizes_sensitive_key_separators():
    assert redact({"api-key": "abc", "privateKey": "abc"}) == {
        "api-key": "[REDACTED]", "privateKey": "[REDACTED]"}

