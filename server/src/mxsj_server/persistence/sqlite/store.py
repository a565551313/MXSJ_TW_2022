"""Explicit migration, fail-closed opens and serialized SQLite transactions."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from mxsj_server.contracts.common import DomainError
from mxsj_server.persistence.sqlite import schema
from mxsj_server.persistence.sqlite.repositories import SQLiteUnitOfWork


class SQLiteStore:
    def __init__(self, path: Path, *, timeout: float = 2.0):
        path = Path(path).absolute()
        if path.suffix.lower() not in {".sqlite3", ".sqlite", ".db"}:
            raise ValueError("Database path must end in .sqlite3, .sqlite or .db")
        self.path, self.timeout = path, timeout
        self._guard_path()

    def _guard_path(self):
        # Local operator owns the directory; hostile concurrent path replacement
        # is outside this adapter's threat model. Do not follow obvious aliases.
        if any(p.is_symlink() for p in (self.path, *self.path.parents)):
            raise ValueError("Database path must not contain symbolic links")
        if self.path.exists() and self.path.stat().st_nlink > 1:
            raise ValueError("Database must not be a hard-link alias")
        for suffix in ("-journal", "-wal", "-shm"):
            if Path(str(self.path) + suffix).is_symlink():
                raise ValueError("Database sidecar must not be a symbolic link")

    def _connect(self, *, create: bool = False) -> sqlite3.Connection:
        self._guard_path()
        uri = self.path.as_uri() + ("?mode=rwc" if create else "?mode=rw")
        conn = sqlite3.connect(
            uri, uri=True, timeout=self.timeout, isolation_level=None
        )
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA synchronous=FULL")
        except BaseException:
            conn.close()
            raise
        return conn

    @staticmethod
    def _validate(conn):
        if (
            conn.execute("PRAGMA application_id").fetchone()[0] != schema.APPLICATION_ID
            or conn.execute("PRAGMA user_version").fetchone()[0] != schema.VERSION
        ):
            raise DomainError(
                "SCHEMA_MISMATCH", "Explicit init-db / migration required"
            )
        row = conn.execute(
            "SELECT checksum FROM schema_migrations WHERE version=?",
            (schema.VERSION,),
        ).fetchone()
        if row is None or row[0] != schema.CHECKSUM:
            raise DomainError("SCHEMA_MISMATCH", "Migration checksum differs")

    def initialize(self) -> None:
        """Operator-only, idempotent; refuse unknown schemas without repair/reset."""
        if not self.path.parent.is_dir():
            raise ValueError("Create a private database directory first")
        self._guard_path()
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass  # Existing bytes are inspected, never truncated or chmod-ed.
        else:
            os.close(fd)
        with self._connection(create=True) as conn:
            conn.execute("BEGIN IMMEDIATE")
            app_id = conn.execute("PRAGMA application_id").fetchone()[0]
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if app_id == schema.APPLICATION_ID:
                self._validate(conn)
            else:
                tables = conn.execute("SELECT name FROM sqlite_master").fetchall()
                if app_id != 0 or version != 0 or tables:
                    raise DomainError(
                        "SCHEMA_MISMATCH", "Refusing an unrelated database"
                    )
                for statement in schema.STATEMENTS:
                    conn.execute(statement)
                conn.execute(
                    "INSERT INTO schema_migrations VALUES (?,?)",
                    (schema.VERSION, schema.CHECKSUM),
                )
                conn.execute(f"PRAGMA application_id={schema.APPLICATION_ID}")
                conn.execute(f"PRAGMA user_version={schema.VERSION}")
            conn.commit()

    @contextmanager
    def _connection(self, *, create: bool = False) -> Iterator[sqlite3.Connection]:
        conn = None
        try:
            conn = self._connect(create=create)
            yield conn
        except sqlite3.Error as exc:
            code = getattr(exc, "sqlite_errorcode", 0) & 0xFF
            if code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}:
                raise DomainError(
                    "TEMPORARILY_UNAVAILABLE", "Database busy; retry same operation_id"
                ) from exc
            raise DomainError(
                "STORAGE_ERROR", "Database operation failed; no success acknowledged"
            ) from exc
        finally:
            if conn is not None:
                try:
                    if conn.in_transaction:
                        conn.rollback()
                finally:
                    conn.close()

    def check(self) -> None:
        """No auto-creation or migration. Missing/corrupt databases fail closed."""
        with self._connection() as conn:
            self._validate(conn)
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise DomainError("STORAGE_ERROR", "Database integrity check failed")
            if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise DomainError("STORAGE_ERROR", "Foreign key integrity check failed")

    @contextmanager
    def transaction(self) -> Iterator[SQLiteUnitOfWork]:
        with self._connection() as conn:
            # One writer, including session fence and idempotency lookup. A
            # PostgreSQL implementation must replace this with explicit locks.
            conn.execute("BEGIN IMMEDIATE")
            self._validate(conn)
            yield SQLiteUnitOfWork(conn)
            conn.commit()
