"""Same-origin JSON administration; single admin identity, no anonymous writes."""

from __future__ import annotations

import hmac
import json
from http.cookies import SimpleCookie
from urllib.parse import urlsplit

from mxsj_web_server.core.manager import Conflict
from mxsj_web_server.core.security.auth import verify


def response(status, payload):
    return (
        status,
        {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
        },
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )


def cookie(token, origin, remove=False):
    secure = "; Secure" if origin.startswith("https:") else ""
    return (
        f"mxsj_admin={token}; Path=/; HttpOnly; SameSite=Strict; "
        f"Max-Age={0 if remove else 1800}{secure}"
    )


def handle_admin(manager, method, path, headers, body, address):
    with manager.lock:
        config = manager.services["admin"]["active_config"]
        if not config:
            return response(503, {"error": "后台已停止"})
        origin = config["origin"]
        if headers.get("Host", "").lower() != urlsplit(origin).netloc.lower():
            return response(403, {"error": "管理域名不匹配"})
    result = _handle(manager, method, path, headers, body, address, origin)
    result[1].update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Cache-Control": "no-store",
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self'; "
                "style-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
                "base-uri 'none'; form-action 'self'"
            ),
        }
    )
    return result


def _handle(manager, method, path, headers, body, address, origin):
    if method == "GET" and path in {"/", "/static/admin.js", "/static/style.css"}:
        name = "index.html" if path == "/" else path.rsplit("/", 1)[1]
        mime = {
            "index.html": "text/html",
            "admin.js": "application/javascript",
            "style.css": "text/css",
        }[name]
        return 200, {"Content-Type": mime + "; charset=utf-8"}, manager.static[name]
    if method not in {"GET", "POST"}:
        return response(405, {"error": "不支持的方法"})
    data = {}
    if method == "POST":
        if headers.get("Origin") != origin:
            return response(403, {"error": "请求来源不匹配"})
        if headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            return response(415, {"error": "仅接受 JSON"})
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            return response(400, {"error": "请求必须为对象"})
    jar = SimpleCookie()
    try:
        jar.load(headers.get("Cookie", ""))
        token = jar["mxsj_admin"].value if "mxsj_admin" in jar else ""
    except Exception:
        token = ""
    with manager.lock:
        service = manager.services["admin"]
        if manager.closed or service["status"] not in {"running", "paused"}:
            return response(503, {"error": "后台已停止"})
        if path == "/api/login" and method == "POST":
            # Fixed global + IP budgets; never trust arbitrary forwarded IPs here.
            if not manager.limiter.allow(
                ("login", address), 5
            ) or not manager.limiter.allow(("login", "global"), 30):
                return response(429, {"error": "登录尝试过多，请稍后重试"})
            if not verify(data.get("password"), manager.state["credential"]):
                manager.events.emit(
                    "login.failed", service="admin", ip=address, status=401
                )
                return response(401, {"error": "凭据无效"})
            manager.sessions.revoke(token)
            token, csrf = manager.sessions.create()
            result = response(200, {"csrf": csrf})
            result[1]["Set-Cookie"] = cookie(token, origin)
            manager.events.emit(
                "login.ok", service="admin", actor="admin", ip=address, status=200
            )
            return result
        session = manager.sessions.get(token)
        if not session:
            return response(401, {"error": "请登录，或会话已失效"})
        if method == "POST" and not hmac.compare_digest(
            headers.get("X-CSRF-Token", ""), session["csrf"]
        ):
            return response(403, {"error": "CSRF 校验失败"})
        if method == "GET":
            if path == "/api/session":
                return response(200, {"csrf": session["csrf"]})
            if path == "/api/state":
                return response(200, manager.snapshot())
            if path == "/api/logs":
                return response(
                    200,
                    {
                        "diagnostics": manager.events.snapshot(),
                        "audit": manager.audit(),
                    },
                )
            return response(404, {"error": "接口不存在"})
        if path == "/api/logout":
            manager.sessions.revoke(token)
            result = response(200, {"ok": True})
            result[1]["Set-Cookie"] = cookie("", origin, True)
            manager.events.emit("logout", service="admin", actor="admin")
            return result
        if path == "/api/preview":
            if "content" in data:
                from mxsj_web_server.core.publishing.versions import preview

                return response(200, {"preview": preview(data["content"])})
            return response(200, manager.inspect(data.get("id")))
        if service["status"] == "paused":
            return response(423, {"error": "后台已暂停，仅允许查看和预览"})
        try:
            if path == "/api/draft":
                result = manager.save_draft(data["content"], data["revision"], "admin")
            elif path == "/api/build":
                result = manager.create_release(data["revision"], "admin")
            elif path == "/api/activate":
                result = manager.activate(data["id"], data["revision"], "admin")
            elif path == "/api/settings":
                result = manager.save_settings(
                    data["settings"], data["revision"], "admin"
                )
            elif path == "/api/revoke":
                manager.revoke_sessions("admin")
                return response(200, {"ok": True})
            elif path != "/api/control":
                return response(404, {"error": "接口不存在"})
            else:
                result = None
        except Conflict:
            return response(409, {"error": "版本冲突，请重新加载并合并修改"})
        except (ValueError, KeyError):
            return response(400, {"error": "内容、版本或设置无效"})
    # Do not hold state lock across listener shutdown or operation-lock acquisition.
    if path == "/api/control":
        try:
            result = manager.remote_control(token, data.get("action"))
        except ValueError:
            return response(409, {"error": "服务状态或权限不允许此操作"})
    return response(200, result)
