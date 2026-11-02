"""Small Python 2.5-compatible localhost probe IPC transport.

The wire format is a four-byte big-endian length followed by one UTF-8 JSON
object.  A connection starts with a token handshake.  Only the documented
read-only methods are dispatched; JSON is treated as data and never executed.
"""

try:
    import json
except ImportError:
    # Python 2.5 has no stdlib json; deployments may provide simplejson.
    import simplejson as json
import socket
import struct
import sys

PROTOCOL_VERSION = 1
DEFAULT_MAX_MESSAGE_BYTES = 256 * 1024
DEFAULT_TIMEOUT = 5.0
READONLY_METHODS = (
    "heartbeat",
    "runtime",
    "modules",
    "native_api",
    "report",
    "read_log",
)


class ProbeIpcError(Exception):
    pass


class ProbeIpcTimeout(ProbeIpcError):
    pass


def _send_all(sock, data):
    view = data
    while view:
        sent = sock.send(view)
        if not sent:
            raise ProbeIpcError("socket closed while sending")
        view = view[sent:]


def _recv_exact(sock, size):
    chunks = []
    remaining = size
    while remaining:
        try:
            chunk = sock.recv(remaining)
        except (socket.timeout, OSError):  # noqa: UP041
            raise ProbeIpcTimeout("socket receive timed out")  # noqa: B904
        if not chunk:
            raise ProbeIpcError("socket closed while receiving")
        chunks.append(chunk)
        remaining -= len(chunk)
    if not chunks:
        return ""
    if sys.version_info[0] < 3:  # noqa: UP036
        return "".join(chunks)
    return bytes(bytearray().join(chunks))  # noqa: UP018


def _encode(value, max_message_bytes):
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        raise ProbeIpcError("request is not JSON encodable")  # noqa: B904
    data = text.encode("utf-8")
    if len(data) > max_message_bytes:
        raise ProbeIpcError("message exceeds size limit")
    return struct.pack(">I", len(data)) + data


def _decode(sock, max_message_bytes):
    header = _recv_exact(sock, 4)
    size = struct.unpack(">I", header)[0]
    if size > max_message_bytes:
        raise ProbeIpcError("message exceeds size limit")
    raw = _recv_exact(sock, size)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, TypeError):
        raise ProbeIpcError("invalid JSON message")  # noqa: B904
    if not isinstance(value, dict):
        raise ProbeIpcError("message must be an object")
    return value


def _handshake(sock, token, max_message_bytes):
    hello = _decode(sock, max_message_bytes)
    if hello.get("type") != "hello" or hello.get("token") != token:
        _send_all(sock, _encode({"ok": False, "error": "E_AUTH"}, max_message_bytes))
        raise ProbeIpcError("invalid token handshake")
    _send_all(
        sock,
        _encode(
            {"ok": True, "type": "hello", "v": PROTOCOL_VERSION}, max_message_bytes
        ),
    )


def _request_error(request, code):
    return {"id": request.get("id"), "ok": False, "error": code}


def serve_once(
    listener,
    token,
    handler,
    timeout=DEFAULT_TIMEOUT,
    max_message_bytes=DEFAULT_MAX_MESSAGE_BYTES,
):
    """Accept and serve one authenticated request.

    ``listener`` is a bound/listening socket. ``handler(method, params)`` is
    called only for the six read-only method names and must return JSON data.
    The accepted socket is always closed before returning.
    """
    listener.settimeout(timeout)
    conn, _ = listener.accept()
    try:
        conn.settimeout(timeout)
        _handshake(conn, token, max_message_bytes)
        request = _decode(conn, max_message_bytes)
        method = request.get("method")
        if request.get("type") not in (None, "request"):
            response = _request_error(request, "E_PROTOCOL")
        elif method not in READONLY_METHODS:
            response = _request_error(request, "E_NOT_ALLOWED")
        elif not isinstance(request.get("params", {}), dict):
            response = _request_error(request, "E_PROTOCOL")
        else:
            try:
                result = handler(method, request.get("params", {}))
                response = {"id": request.get("id"), "ok": True, "result": result}
            except Exception:
                response = _request_error(request, "E_INTERNAL")
        _send_all(conn, _encode(response, max_message_bytes))
        return response
    finally:
        conn.close()


def client_request(
    host,
    port,
    token,
    method,
    params=None,
    timeout=DEFAULT_TIMEOUT,
    max_message_bytes=DEFAULT_MAX_MESSAGE_BYTES,
):
    """Send one authenticated read-only request to localhost TCP."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ProbeIpcError("IPC host must be localhost")
    if method not in READONLY_METHODS:
        raise ProbeIpcError("method is not read-only")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise ProbeIpcError("params must be an object")
    sock = socket.socket(
        socket.AF_INET6 if host == "::1" else socket.AF_INET, socket.SOCK_STREAM
    )
    try:
        sock.settimeout(timeout)
        sock.connect((host, port))
        _send_all(
            sock,
            _encode(
                {"type": "hello", "token": token, "v": PROTOCOL_VERSION},
                max_message_bytes,
            ),
        )
        hello = _decode(sock, max_message_bytes)
        if hello.get("ok") is not True:
            raise ProbeIpcError("handshake rejected")
        request = {
            "type": "request",
            "id": "request",
            "method": method,
            "params": params,
        }
        _send_all(sock, _encode(request, max_message_bytes))
        return _decode(sock, max_message_bytes)
    except (socket.timeout, OSError):  # noqa: UP041
        raise ProbeIpcTimeout("socket operation timed out")  # noqa: B904
    finally:
        sock.close()
