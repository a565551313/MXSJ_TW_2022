"""Shared management use cases. GUI and HTTP never duplicate publication rules."""

from __future__ import annotations

import copy
import json
import threading
import uuid
from pathlib import Path

from mxsj_web_server.core.configuration.settings import defaults, validate
from mxsj_web_server.core.configuration.store import Store
from mxsj_web_server.core.content import render
from mxsj_web_server.core.observability.events import Events
from mxsj_web_server.core.publishing.versions import application, difference, preview
from mxsj_web_server.core.runtime.listener import Listener
from mxsj_web_server.core.security.access import Limiter
from mxsj_web_server.core.security.auth import Sessions, password_hash


class Conflict(ValueError):
    pass


class Manager:
    def __init__(
        self, directory: Path, initial: dict, static_directory: Path, request_handler
    ):
        render(initial)
        self.lock = threading.RLock()
        self.operations = threading.RLock()
        self.request_handler = request_handler
        self.store = Store(directory)
        self.closed = False
        try:
            self.events = Events(self.store.directory)
            self.state = self.store.load()
            if self.state is None:
                self.state = {
                    "revision": 0,
                    "draft": initial,
                    "active": None,
                    "settings": defaults(),
                    "credential": None,
                }
                self.store.commit(self.state, "initialize", "local")
            validate(self.state["settings"])
            render(self.state["draft"])
            self.published = (
                application(self.store.release(self.state["active"]))
                if self.state["active"]
                else None
            )
            self.services = {
                kind: {"status": "stopped", "listener": None, "active_config": None}
                for kind in ("public", "admin")
            }
            self.sessions = Sessions()
            self.limiter = Limiter()
            self.static = {
                name: (static_directory / name).read_bytes()
                for name in ("index.html", "admin.js", "style.css")
            }
        except BaseException:
            if hasattr(self, "events"):
                self.events.close()
            self.store.close()
            raise

    def snapshot(self):
        with self.lock:
            return {
                "revision": self.state["revision"],
                "draft": copy.deepcopy(self.state["draft"]),
                "active": self.state["active"],
                "settings": copy.deepcopy(self.state["settings"]),
                "has_password": bool(self.state["credential"]),
                "releases": self.store.releases(),
                "services": {
                    k: {
                        "status": v["status"],
                        "active_config": copy.deepcopy(v["active_config"]),
                    }
                    for k, v in self.services.items()
                },
                "sessions": len(self.sessions.entries),
                "logging": self.events.snapshot(),
            }

    def _change(self, changes, revision, event, actor, target="", release=None):
        if self.closed:
            raise ValueError("管理器已关闭")
        if type(revision) is not int or revision != self.state["revision"]:
            raise Conflict("数据已被其他入口修改，请重新加载后合并")
        state = {**self.state, **copy.deepcopy(changes), "revision": revision + 1}
        self.store.commit(state, event, actor, target, release)
        self.state = state
        self.events.emit(event, actor=actor)
        return self.snapshot()

    def save_draft(self, raw, revision, actor="local"):
        render(raw)
        with self.lock:
            return self._change({"draft": raw}, revision, "draft.save", actor)

    def create_release(self, revision, actor="local"):
        with self.lock:
            if len(self.store.releases()) >= 200:
                raise ValueError("版本数量上限 200，请先离线备份维护")
            identity = uuid.uuid4().hex
            return self._change(
                {}, revision, "release.build", actor, identity, identity
            )

    def activate(self, identity, revision, actor="local"):
        with self.lock:
            app = application(self.store.release(identity))
            result = self._change(
                {"active": identity}, revision, "release.activate", actor, identity
            )
            self.published = app  # Same lock as serving; only after durable commit.
            return result

    def save_settings(self, settings, revision, actor="local"):
        settings = validate(settings)
        with self.lock:
            if actor == "admin":
                for key in ("host", "port", "origin"):
                    if settings["admin"][key] != self.state["settings"]["admin"][key]:
                        raise ValueError("后台监听地址、端口及域名只能由本地修改")
            return self._change(
                {"settings": settings}, revision, "settings.save", actor
            )

    def set_password(self, password):
        credential = password_hash(password)
        with self.lock:
            result = self._change(
                {"credential": credential},
                self.state["revision"],
                "password.reset",
                "local",
            )
            self.sessions.clear()
            return result

    def revoke_sessions(self, actor="local"):
        with self.lock:
            result = self._change({}, self.state["revision"], "sessions.revoke", actor)
            self.sessions.clear()
            return result

    def inspect(self, identity=None):
        with self.lock:
            raw = self.store.release(identity) if identity else self.state["draft"]
            old = (
                self.store.release(self.state["active"]) if self.state["active"] else {}
            )
            return {
                "content": copy.deepcopy(raw),
                "preview": preview(raw),
                "difference": difference(old, raw),
            }

    def audit(self):
        with self.lock:
            return self.store.audit()

    def control(self, kind, action, actor="local"):
        if kind not in self.services or action not in {
            "start",
            "pause",
            "resume",
            "restart",
            "stop",
        }:
            raise ValueError("未知服务操作")
        if kind == "admin" and actor != "local":
            raise ValueError("后台开关只允许本地操作")
        with self.operations:
            if action == "restart":
                self._stop(kind, actor)
                self._start(kind, actor)
            elif action == "start":
                self._start(kind, actor)
            elif action == "stop":
                self._stop(kind, actor)
            else:
                with self.lock:
                    service = self.services[kind]
                    expected = "running" if action == "pause" else "paused"
                    if service["status"] != expected:
                        raise ValueError("服务状态不允许该操作")
                    service["status"] = "paused" if action == "pause" else "running"
                    self.events.emit("service." + action, service=kind, actor=actor)
        return self.snapshot()

    def remote_control(self, token, action):
        with self.operations:
            with self.lock:
                if (
                    self.closed
                    or self.services["admin"]["status"] != "running"
                    or not self.sessions.get(token)
                ):
                    raise ValueError("后台会话或状态已失效")
            return self.control("public", action, "admin")

    def _start(self, kind, actor):
        with self.lock:
            if self.closed or self.services[kind]["status"] != "stopped":
                raise ValueError("服务未停止或管理器已关闭")
            if kind == "admin" and not self.state["credential"]:
                raise ValueError("请先在本地设置管理员密码")
            config = copy.deepcopy(self.state["settings"][kind])
            self.services[kind]["status"] = "starting"
        try:
            listener = Listener(
                config, lambda *args: self.request_handler(self, kind, *args)
            )
        except Exception:
            with self.lock:
                self.services[kind]["status"] = "stopped"
                self.events.emit("service.failed", service=kind, actor=actor)
            raise ValueError("启动失败：检查地址、端口占用及权限") from None
        with self.lock:
            self.services[kind].update(
                status="running", listener=listener, active_config=config
            )
            self.events.emit("service.start", service=kind, actor=actor)

    def _stop(self, kind, actor):
        with self.lock:
            service = self.services[kind]
            listener = service["listener"]
            service["status"] = "stopping"
            if kind == "admin":
                self.sessions.clear()
        if listener:
            listener.stop()
        with self.lock:
            service.update(status="stopped", listener=None, active_config=None)
            self.events.emit("service.stop", service=kind, actor=actor)

    def close(self):
        # Independent services, stop admin first; no new mutation after state gate.
        with self.operations:
            if self.closed:
                return
            self._stop("admin", "local")
            self._stop("public", "local")
            with self.lock:
                self.closed = True
                self.events.close()
                self.store.close()

    def export_logs(self, path: Path):
        with self.lock:
            data = {"diagnostics": self.events.snapshot(), "audit": self.store.audit()}
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
