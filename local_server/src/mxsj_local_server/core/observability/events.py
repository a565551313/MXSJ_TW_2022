"""Allowlisted structured diagnostics; never serialize requests or exceptions."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import stat
import sys
import threading
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

EVENTS = frozenset(
    {
        "process.start",
        "process.stop",
        "process.failed",
        "config.validated",
        "console.rejected",
        "database.initialize",
        "database.check",
        "database.transaction",
        "database.busy",
        "account.provision",
        "account.authenticate",
        "account.revoke",
        "session.context",
        "session.takeover",
        "session.expired",
        "session.stale",
        "character.list",
        "character.create",
        "character.enter_world",
    }
)
ERROR_CODES = frozenset(
    {
        "INVALID_ARGUMENT",
        "UNAUTHENTICATED",
        "FORBIDDEN",
        "ALREADY_EXISTS",
        "UNSUPPORTED_PROTOCOL",
        "STORAGE_ERROR",
        "SCHEMA_MISMATCH",
        "IDEMPOTENCY_CONFLICT",
        "CHARACTER_LIMIT",
        "NAME_TAKEN",
        "NOT_IMPLEMENTED",
        "TEMPORARILY_UNAVAILABLE",
        "INTERNAL_ERROR",
        "CANCELLED_UNKNOWN",
        "CONFIGURATION_ERROR",
        "INTERRUPTED",
    }
)
OUTCOMES = frozenset({"started", "succeeded", "failed", "replayed", "unknown"})
LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
NUMERIC_FIELDS = frozenset(
    {
        "realm_id",
        "account_id",
        "character_id",
        "session_epoch",
        "duration_ms",
    }
)
TRACE = re.compile(r"[a-f0-9]{32}\Z")


def emergency() -> None:
    """Last-resort fixed message; no logger recursion, input or exception text."""
    try:
        os.write(
            2, b"MXSJ_LOGGING_DEGRADED: diagnostic output failed; check log storage.\n"
        )
    except OSError:
        pass  # Both output channels can fail; no durable audit guarantee is made.


def safe_exception(exc: BaseException) -> dict:
    # No str/repr, traceback formatting, source text, locals, cause or args.
    kind = type(exc).__name__
    if kind not in {
        "ValueError",
        "TypeError",
        "KeyError",
        "OSError",
        "RuntimeError",
        "DomainError",
        "OperationalError",
        "IntegrityError",
        "DatabaseError",
        "PermissionError",
        "CancelledError",
        "KeyboardInterrupt",
    }:
        kind = "Exception"
    frames = []
    tb = exc.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        # Only trusted server/launcher code locations; omit arbitrary plugin paths.
        path = Path(code.co_filename)
        if "mxsj_local_server.core" in path.parts or path.parent.name == "local_server":
            frames.append(
                {"file": path.name, "function": code.co_name, "line": tb.tb_lineno}
            )
        tb = tb.tb_next
    return {"type": kind, "frames": frames[-8:]}


def safe_error(exc: BaseException) -> str:
    code = getattr(exc, "code", None)
    return code if isinstance(code, str) and code in ERROR_CODES else "INTERNAL_ERROR"


def guard_file(path: Path) -> None:
    if path.is_symlink():
        raise ValueError("Unsafe logging path")
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Unsafe logging file")


def private_open(path: Path, flags: int):
    guard_file(path)
    fd = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise ValueError("Unsafe logging file")
    return fd


class DirectoryLease:
    """One process per log directory; OS releases lock on process crash."""

    def __init__(self, path: Path):
        self.fd = private_open(path, os.O_CREAT | os.O_RDWR)
        try:
            if os.name == "nt":
                import msvcrt

                if os.fstat(self.fd).st_size == 0:
                    os.write(self.fd, b"0")
                os.lseek(self.fd, 0, os.SEEK_SET)
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl  # win-ok: POSIX branch; Windows uses msvcrt above

                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(self.fd)
            raise

    def close(self):
        # Closing the sole descriptor releases the OS lock on both platforms.
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


class StrictRotatingHandler(RotatingFileHandler):
    def _open(self):
        fd = private_open(
            Path(self.baseFilename), os.O_WRONLY | os.O_CREAT | os.O_APPEND
        )
        return os.fdopen(fd, "a", encoding="utf-8", newline="\n")

    def handleError(self, record):  # noqa: N802  # standard logging hook
        # logging's default handler prints exception/record internals. Never use it.
        raise OSError("Diagnostic write failed") from None

    def emit(self, record):
        # Directory is operator-owned; hostile concurrent file replacement is
        # outside this local adapter's threat model. Refuse obvious aliases.
        for suffix in ("", *(f".{n}" for n in range(1, self.backupCount + 1))):
            guard_file(Path(self.baseFilename + suffix))
        super().emit(record)


class EventLogger:
    """Process-scoped sink; not attached to root logging or third-party handlers.

    Runtime write failures are observable but never replace a business result.
    Config/file-open failures instead abort startup before business work begins.
    """

    def __init__(self, *, console=None, handler=None, lease=None, level="INFO"):
        if level not in LEVELS:
            raise ValueError("Invalid log level")
        self.console = console
        self.handler, self.lease, self.level = handler, lease, LEVELS[level]
        self.lock = threading.RLock()
        self.failures = 0
        self.degraded = False
        self.closed = False

    @classmethod
    def open(cls, directory: Path, *, max_bytes=5_242_880, backups=5, level="INFO"):
        if type(max_bytes) is not int or not 4096 <= max_bytes <= 104_857_600:
            raise ValueError("Log max_bytes must be 4096..104857600")
        if type(backups) is not int or not 1 <= backups <= 20 or level not in LEVELS:
            raise ValueError("Invalid logging policy")
        directory = Path(directory).absolute()
        if any(p.is_symlink() for p in (directory, *directory.parents)):
            raise ValueError("Unsafe logging directory")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        lease = DirectoryLease(directory / ".writer.lock")
        try:
            path = directory / "server.jsonl"
            for suffix in ("", *(f".{n}" for n in range(1, backups + 1))):
                guard_file(Path(str(path) + suffix))
            handler = StrictRotatingHandler(
                path,
                maxBytes=max_bytes,
                backupCount=backups,
                encoding="utf-8",
            )
            return cls(handler=handler, lease=lease, level=level)
        except BaseException:
            lease.close()
            raise

    def health(self) -> dict:
        with self.lock:
            return {"failures": self.failures, "degraded": self.degraded}

    def emit(
        self,
        event: str,
        *,
        outcome="succeeded",
        error_code=None,
        exception: BaseException | None = None,
        **fields,
    ) -> None:
        try:
            self._emit(
                event,
                outcome=outcome,
                error_code=error_code,
                exception=exception,
                **fields,
            )
        except Exception:
            # Formatting/serialization failures must not replace committed results.
            self._failure()

    def _emit(self, event, *, outcome, error_code, exception, **fields):
        # Fail closed on payload shape: only whitelisted scalar fields survive.
        if (
            not isinstance(event, str)
            or not isinstance(outcome, str)
            or event not in EVENTS
            or outcome not in OUTCOMES
        ):
            self._failure()
            return
        code = (
            error_code
            if isinstance(error_code, str) and error_code in ERROR_CODES
            else None
        )
        level = "INFO"
        if outcome == "failed":
            level = (
                "ERROR"
                if code in {"INTERNAL_ERROR", "STORAGE_ERROR", "SCHEMA_MISMATCH"}
                else "WARNING"
            )
        elif outcome == "unknown":
            level = "WARNING"
        elif event == "database.transaction":
            level = "DEBUG"
        if LEVELS[level] < self.level:
            return
        row = {
            "time": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": level,
            "event": event,
            "component": event.split(".")[0],
            "outcome": outcome,
        }
        for key in NUMERIC_FIELDS:
            value = fields.get(key)
            if type(value) is int and 0 <= value <= 2**63 - 1:
                row[key] = value
        trace = fields.get("trace_id")
        if isinstance(trace, str) and TRACE.fullmatch(trace):
            row["trace_id"] = trace
        operation = fields.get("operation_id")
        if isinstance(operation, str) and len(operation) <= 128:
            # An operation id is caller supplied: do not print a secret planted in it.
            row["operation_id_sha256"] = hashlib.sha256(
                operation.encode("utf-8", errors="replace")
            ).hexdigest()
        if code:
            row["error_code"] = code
        if exception is not None:
            row["exception"] = safe_exception(exception)
        text = json.dumps(row, ensure_ascii=True, separators=(",", ":"))
        with self.lock:
            failed = False
            if self.closed:
                self._failure()
                return
            if self.handler is not None:
                try:
                    record = logging.LogRecord(
                        "mxsj.events", LEVELS[level], "", 0, text, (), None
                    )
                    self.handler.handle(record)
                except Exception:
                    failed = True
            try:
                stream = self.console if self.console is not None else sys.stderr
                stream.write(text + "\n")
                stream.flush()
            except Exception:
                failed = True
            if failed:
                self._failure()
            else:
                self.degraded = False

    def _failure(self):
        with self.lock:
            self.failures += 1
            if not self.degraded:
                emergency()
            self.degraded = True

    def close(self):
        with self.lock:
            if self.closed:
                return
            try:
                if self.handler is not None:
                    self.handler.close()
            except Exception:
                self._failure()
            finally:
                if self.lease is not None:
                    try:
                        self.lease.close()
                    except Exception:
                        self._failure()
                self.closed = True


DEFAULT_EVENTS = EventLogger()  # Console only; file ownership is a bootstrap concern.
