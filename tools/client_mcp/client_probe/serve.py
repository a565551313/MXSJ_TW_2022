"""Run the read-only probe IPC endpoint from a client-side Python VM."""

import socket

import ipc
import mxsj_probe


def serve(listener, token):
    """Serve one authenticated report request on an already-bound listener."""
    def handler(method, params):
        report = mxsj_probe.get_report({})
        if method == "heartbeat":
            return {"alive": True}
        if method == "runtime":
            return report["runtime"]
        if method == "modules":
            return report["modules"]
        if method == "native_api":
            return report["native_api"]
        if method == "report":
            return report
        if method == "read_log":
            return {"items": [], "total": 0,
                    "limit": params.get("limit", 50),
                    "offset": params.get("offset", 0)}
        raise ValueError("unsupported method")

    return ipc.serve_once(listener, token, handler)


def write_snapshot(path='mxsj_probe_report.txt', state=None):
    return mxsj_probe.write_report(path, state)


def bind_localhost(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", port))
    listener.listen(1)
    return listener
