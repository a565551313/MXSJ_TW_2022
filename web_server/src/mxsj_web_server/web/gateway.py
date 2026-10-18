"""Shared HTTP boundary: no raw request logging, no public management routes."""

from __future__ import annotations

import ipaddress
import time

from mxsj_web_server.core.security.access import client_ip, in_networks, permitted
from mxsj_web_server.web.admin.api import handle_admin
from mxsj_web_server.web.public.routes import serve_public
from mxsj_web_server.web.responses import reply

REGISTERED = {
    "/",
    "/healthz",
    "/news.txt",
    "/service.txt",
    "/server.txt",
    "/static/admin.js",
    "/static/style.css",
    "/api/login",
    "/api/session",
    "/api/logout",
    "/api/state",
    "/api/draft",
    "/api/preview",
    "/api/build",
    "/api/activate",
    "/api/settings",
    "/api/control",
    "/api/logs",
    "/api/revoke",
}


def dispatch(manager, kind, method, path, headers, body, peer):
    start = time.monotonic()
    address = ""
    try:
        with manager.lock:
            if manager.closed or manager.services[kind]["status"] not in {
                "running",
                "paused",
            }:
                return reply(503, {"error": "服务已停止"})
            policy = manager.state["settings"][kind]
            address = client_ip(
                peer, headers.get("X-Forwarded-For", ""), policy["trusted_proxies"]
            )
            allowed = permitted(address, policy)
            active = manager.services[kind]["active_config"]
            if kind == "admin" and active and active["origin"].startswith("https:"):
                allowed = allowed and in_networks(
                    ipaddress.ip_address(peer), policy["trusted_proxies"]
                )
            rate = manager.limiter.allow((kind, address), policy["requests_per_minute"])
        if not allowed or not rate:
            result = reply(403 if not allowed else 429, {"error": "访问受限"})
            manager.events.emit("denied", service=kind, ip=address, status=result[0])
        elif kind == "admin":
            result = handle_admin(manager, method, path, headers, body, address)
        else:
            result = serve_public(manager, method, path, headers)
    except ValueError:
        result = reply(400, {"error": "输入无效，请检查格式"})
    except Exception:
        manager.events.emit("failure", service=kind, status=500)
        result = reply(500, {"error": "内部错误，请检查诊断日志"})
    manager.events.emit(
        "access",
        service=kind,
        ip=address,
        path=path if path in REGISTERED else "/<unregistered>",
        status=result[0],
        duration_ms=int((time.monotonic() - start) * 1000),
    )
    return result
