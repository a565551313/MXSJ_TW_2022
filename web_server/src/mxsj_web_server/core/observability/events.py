"""Bounded sanitized diagnostics; database audit is separate from rotating logs."""

from __future__ import annotations

import json
import logging
import os
import threading
from collections import deque
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

EVENTS = {
    "service.start",
    "service.stop",
    "service.pause",
    "service.resume",
    "service.failed",
    "access",
    "denied",
    "login.ok",
    "login.failed",
    "logout",
    "draft.save",
    "release.build",
    "release.activate",
    "settings.save",
    "password.reset",
    "sessions.revoke",
    "failure",
}


class StrictHandler(RotatingFileHandler):
    def _open(self):
        path = Path(self.baseFilename)
        if path.is_symlink() or (
            path.exists() and (not path.is_file() or path.stat().st_nlink != 1)
        ):
            raise ValueError("Unsafe log path")
        fd = os.open(
            path,
            os.O_CREAT | os.O_APPEND | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        return os.fdopen(fd, "a", encoding="utf-8")

    def handleError(self, record):  # noqa: N802  # Standard logging hook.
        raise OSError("LOG_WRITE_FAILED") from None


class Events:
    def __init__(self, directory):
        self.lock = threading.RLock()
        self.rows = deque(maxlen=1000)
        self.failures = 0
        self.degraded = False
        self.closed = False
        path = directory / "web_server.jsonl"
        for n in range(6):
            p = path if n == 0 else directory / f"web_server.jsonl.{n}"
            if p.is_symlink() or (
                p.exists() and (not p.is_file() or p.stat().st_nlink != 1)
            ):
                raise ValueError("日志目标无效")
        fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        os.close(fd)
        self.handler = StrictHandler(
            path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )

    def emit(
        self,
        event,
        *,
        service="system",
        actor="system",
        status=0,
        ip="",
        path="",
        duration_ms=0,
    ):
        with self.lock:
            if self.closed:
                return
            try:
                if (
                    event not in EVENTS
                    or service not in {"system", "public", "admin"}
                    or actor not in {"system", "local", "admin"}
                ):
                    raise ValueError("Invalid event")
                # Caller passes canonical registered path, never original URL/query.
                row = {
                    "time": datetime.now(timezone.utc).isoformat(),
                    "event": event,
                    "service": service,
                    "actor": actor,
                    "status": int(status),
                    "ip": ip[:64],
                    "path": path[:64],
                    "duration_ms": max(0, int(duration_ms)),
                }
                self.rows.append(row)
                text = json.dumps(row, ensure_ascii=True)
                self.handler.handle(
                    logging.LogRecord("web.events", 20, "", 0, text, (), None)
                )
                self.degraded = False
            except Exception:
                self.failures += 1
                if not self.degraded:
                    try:
                        os.write(2, b"WEB_LOGGING_DEGRADED\n")
                    except OSError:
                        pass
                self.degraded = True

    def snapshot(self):
        with self.lock:
            return {
                "rows": list(self.rows),
                "failures": self.failures,
                "degraded": self.degraded,
            }

    def close(self):
        with self.lock:
            self.closed = True
            try:
                self.handler.close()
            except Exception:
                self.failures += 1
                self.degraded = True
