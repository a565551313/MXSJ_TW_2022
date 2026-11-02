"""Local TCP IPC tests for the Python 2.5-compatible probe transport."""

import os
import socket
import sys
import threading

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(ROOT, "client_probe")
if PROBE not in sys.path:
    sys.path.insert(0, PROBE)

import ipc  # noqa: E402


def _server(listener, token, calls, errors):
    def handler(method, params):
        calls.append((method, params))
        return {"method": method, "params": params}

    try:
        ipc.serve_once(listener, token, handler, timeout=2.0)
    except Exception as exc:
        errors.append(exc)


def _listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    return sock


def test_client_request_handshake_and_json_data_round_trip():
    listener = _listener()
    calls, errors = [], []
    thread = threading.Thread(target=_server, args=(listener, "secret", calls, errors))
    thread.start()
    try:
        result = ipc.client_request(
            "127.0.0.1",
            listener.getsockname()[1],
            "secret",
            "report",
            {"text": "__import__('os').system('echo nope')"},
            timeout=2.0,
        )
    finally:
        thread.join(3.0)
        listener.close()
    assert not errors
    assert result["ok"] is True
    assert result["result"]["params"]["text"].startswith("__import__")
    assert calls == [("report", result["result"]["params"])]


def test_control_method_and_wrong_host_are_rejected():
    with pytest.raises(ipc.ProbeIpcError):
        ipc.client_request("192.0.2.1", 1, "secret", "report")
    with pytest.raises(ipc.ProbeIpcError):
        ipc.client_request("localhost", 1, "secret", "invoke")


def test_wrong_token_is_rejected_and_handler_is_not_called():
    listener = _listener()
    calls, errors = [], []
    thread = threading.Thread(target=_server, args=(listener, "right", calls, errors))
    thread.start()
    try:
        with pytest.raises(ipc.ProbeIpcError):
            ipc.client_request(
                "127.0.0.1",
                listener.getsockname()[1],
                "wrong",
                "heartbeat",
                timeout=2.0,
            )
    finally:
        thread.join(3.0)
        listener.close()
    assert calls == []
    assert errors


def test_message_size_limit_is_enforced():
    listener = _listener()
    calls, errors = [], []
    thread = threading.Thread(target=_server, args=(listener, "secret", calls, errors))
    thread.start()
    try:
        with pytest.raises(ipc.ProbeIpcError):
            ipc.client_request(
                "127.0.0.1",
                listener.getsockname()[1],
                "secret",
                "report",
                {"x": "a" * 100},
                timeout=2.0,
                max_message_bytes=64,
            )
    finally:
        thread.join(3.0)
        listener.close()
    assert calls == []


def test_all_read_only_methods_are_accepted():
    for method in ipc.READONLY_METHODS:
        listener = _listener()
        calls, errors = [], []
        thread = threading.Thread(
            target=_server, args=(listener, "secret", calls, errors)
        )
        thread.start()
        try:
            result = ipc.client_request(
                "localhost",
                listener.getsockname()[1],
                "secret",
                method,
                timeout=2.0,
            )
        finally:
            thread.join(3.0)
            listener.close()
        assert not errors
        assert result["ok"] is True
        assert calls[0][0] == method
