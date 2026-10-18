"""Only known read-only player resources; never expose management APIs."""

from __future__ import annotations

from mxsj_web_server.web.responses import reply


def serve_public(manager, method, path, headers):
    with manager.lock:
        if manager.services["public"]["status"] != "running":
            return reply(503, {"error": "公开服务暂停或停止"})
        app = manager.published
    if method not in {"GET", "HEAD"}:
        return reply(405, {"error": "只读服务"})
    if path == "/healthz":
        return reply(
            200, {"service": "web_server", "status": "ok", "published": app is not None}
        )
    if path not in {"/news.txt", "/service.txt", "/server.txt"}:
        return reply(404, {"error": "未提供该资源"})
    if app is None:
        return reply(503, {"error": "尚未发布内容"})
    response = []
    iterable = app(
        {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "HTTP_IF_NONE_MATCH": headers.get("If-None-Match", ""),
        },
        lambda status, h: response.extend([int(status.split()[0]), dict(h)]),
    )
    response[1].pop(
        "Content-Length", None
    )  # Transport computes length; HEAD handled below.
    body = b"".join(iterable)
    if method == "HEAD":
        # Preserve GET entity size; listener suppresses transmission for HEAD.
        body = app.assets[path].body
    return response[0], response[1], body
