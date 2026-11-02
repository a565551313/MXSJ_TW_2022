"""Read-only localhost IPC backend for a running client probe."""

from __future__ import annotations

import ast
import json
import socket
import struct

from ..core.protocol import PROTOCOL_VERSION, ErrorCode, Message, new_session_id
from .backend import BackendResult, ProbeBackend

MAX_REPORT_BYTES = 256 * 1024


def _parse_report(raw: bytes) -> dict:
    """Parse a bounded probe report without executing code.

    The modern host prefers JSON.  The CPython 2.5 client probe writes
    ``repr(report)`` because the old VM has no stdlib ``json``; accept that
    Python-literal form via ``ast.literal_eval`` only after JSON fails.
    """
    if len(raw) > MAX_REPORT_BYTES:
        raise ValueError("probe report exceeds size limit")
    text = raw.decode("utf-8")
    try:
        value = json.loads(text)
    except ValueError:
        try:
            value = ast.literal_eval(text)
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError) as exc:
            raise ValueError("probe report is not JSON or a Python literal") from exc
    if not isinstance(value, dict):
        raise ValueError("probe report must be an object")
    return value

_METHODS = {
    "probe.heartbeat": "heartbeat",
    "probe.get_runtime": "runtime",
    "probe.get_modules": "modules",
    "probe.get_native_api": "native_api",
    "probe.get_report": "report",
    "probe.read_log": "read_log",
}


class FileProbeBackend(ProbeBackend):
    """Read a bounded report file emitted by a client-side probe."""

    def __init__(self, report_path: str):
        self._path = report_path
        self._session = new_session_id()

    def latest_session(self) -> str | None:
        return self._session

    def handle_event(self, evt: Message) -> None:
        return None

    def handle_request(self, req: Message) -> BackendResult:
        if req.session != self._session:
            return BackendResult(False, error_code=ErrorCode.SESSION)
        try:
            with open(self._path, "rb") as stream:
                raw = stream.read(MAX_REPORT_BYTES + 1)
            value = _parse_report(raw)
        except (OSError, ValueError, TypeError):
            return BackendResult(False, error_code=ErrorCode.INTERNAL)
        if req.method == "probe.get_report":
            return BackendResult(True, result=value)
        if req.method == "probe.get_runtime":
            return BackendResult(True, result=value.get("runtime", {}))
        if req.method == "probe.get_modules":
            return BackendResult(True, result=value.get("modules", {}))
        if req.method == "probe.get_native_api":
            return BackendResult(True, result=value.get("native_api", {}))
        if req.method == "probe.heartbeat":
            return BackendResult(True, result={"alive": True})
        return BackendResult(False, error_code=ErrorCode.NOT_ALLOWED)


class IpcProbeBackend(ProbeBackend):
    """Bridge MCP read-only calls to an authenticated localhost probe."""

    def __init__(self, host: str, port: int, token: str, timeout: float = 5.0):
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("IPC backend host must be localhost")
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError("IPC backend port is invalid")
        if not isinstance(token, str) or not token:
            raise ValueError("IPC backend token is required")
        self._host = host
        self._port = port
        self._token = token
        self._timeout = timeout
        self._session = new_session_id()

    def latest_session(self) -> str | None:
        return self._session

    def handle_event(self, evt: Message) -> None:
        return None

    def _request(self, method: str, params: dict) -> dict:
        payload = {"type": "hello", "token": self._token, "v": 1}
        request = {"type": "request", "id": "request", "method": method,
                   "params": params}
        family = socket.AF_INET6 if self._host == "::1" else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(self._timeout)
            sock.connect((self._host, self._port))
            for item in (payload,):
                self._send(sock, item)
                hello = self._recv(sock)
                if hello.get("ok") is not True:
                    raise OSError("probe handshake rejected")
            self._send(sock, request)
            return self._recv(sock)

    @staticmethod
    def _send(sock: socket.socket, value: dict) -> None:
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        if len(raw) > 256 * 1024:
            raise OSError("probe message exceeds size limit")
        sock.sendall(struct.pack(">I", len(raw)) + raw)

    @staticmethod
    def _recv(sock: socket.socket) -> dict:
        header = b""
        while len(header) < 4:
            chunk = sock.recv(4 - len(header))
            if not chunk:
                raise OSError("probe connection closed")
            header += chunk
        size = struct.unpack(">I", header)[0]
        if size > 256 * 1024:
            raise OSError("probe message exceeds size limit")
        raw = b""
        while len(raw) < size:
            chunk = sock.recv(size - len(raw))
            if not chunk:
                raise OSError("probe connection closed")
            raw += chunk
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise OSError("probe response is not an object")
        return value

    def handle_request(self, req: Message) -> BackendResult:
        if type(req.v) is not int or req.v != PROTOCOL_VERSION:
            return BackendResult(False, error_code=ErrorCode.PROTOCOL_VERSION)
        if req.session != self._session:
            return BackendResult(False, error_code=ErrorCode.SESSION)
        method = _METHODS.get(req.method)
        if method is None:
            return BackendResult(False, error_code=ErrorCode.NOT_ALLOWED)
        params = req.params if isinstance(req.params, dict) else {}
        if req.method != "probe.read_log" and params:
            return BackendResult(False, error_code=ErrorCode.NOT_ALLOWED)
        try:
            response = self._request(method, params)
        except (OSError, ValueError, json.JSONDecodeError):
            return BackendResult(False, error_code=ErrorCode.INTERNAL)
        if response.get("ok") is not True:
            return BackendResult(False, error_code=ErrorCode.INTERNAL)
        return BackendResult(True, result=response.get("result"))


__all__ = ["FileProbeBackend", "IpcProbeBackend"]
