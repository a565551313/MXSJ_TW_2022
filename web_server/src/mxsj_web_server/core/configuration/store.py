"""Private SQLite state; publication pointer and audit commit together."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, directory: Path):
        self.directory = directory.absolute()
        if any(p.is_symlink() for p in (self.directory, *self.directory.parents)):
            raise ValueError("管理目录不能是链接")
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.lease = None
        try:
            self.lease = self._private(".controller.lock")
            if os.name == "nt":
                import msvcrt

                if os.fstat(self.lease).st_size == 0:
                    os.write(self.lease, b"0")
                os.lseek(self.lease, 0, os.SEEK_SET)
                msvcrt.locking(self.lease, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl  # win-ok: Windows uses msvcrt locking above.

                fcntl.flock(self.lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.path = self.directory / "management.sqlite3"
            os.close(self._private("management.sqlite3"))
            db = self.connection()
            try:
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS state (
                    id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS releases (
                    id TEXT PRIMARY KEY, created INTEGER NOT NULL, body TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY, created INTEGER NOT NULL,
                    actor TEXT NOT NULL, event TEXT NOT NULL, target TEXT NOT NULL);
                """)
            finally:
                db.close()
        except BaseException:
            self.close()
            raise

    def _private(self, name):
        path = self.directory / name
        if path.is_symlink() or (
            path.exists() and (not path.is_file() or path.stat().st_nlink != 1)
        ):
            raise ValueError("管理文件不能是链接或特殊文件")
        return os.open(
            path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600
        )

    def connection(self):
        db = sqlite3.connect(self.path, timeout=2)
        db.execute("PRAGMA synchronous=FULL")
        return db

    def load(self):
        db = self.connection()
        try:
            row = db.execute("SELECT body FROM state WHERE id=1").fetchone()
            return json.loads(row[0]) if row else None
        finally:
            db.close()

    def commit(self, state, event, actor, target="", release=None):
        import time

        db = self.connection()
        try:
            with db:
                if release:
                    db.execute(
                        "INSERT INTO releases VALUES(?,?,?)",
                        (
                            release,
                            int(time.time()),
                            json.dumps(state["draft"], ensure_ascii=False),
                        ),
                    )
                db.execute(
                    "INSERT OR REPLACE INTO state VALUES(1,?)",
                    (json.dumps(state, ensure_ascii=False),),
                )
                db.execute(
                    "INSERT INTO audit(created,actor,event,target) VALUES(?,?,?,?)",
                    (int(time.time()), actor, event, target),
                )
        finally:
            db.close()

    def releases(self):
        db = self.connection()
        try:
            return [
                {"id": row[0], "created": row[1]}
                for row in db.execute(
                    "SELECT id,created FROM releases ORDER BY created DESC, id DESC"
                )
            ]
        finally:
            db.close()

    def release(self, identity):
        db = self.connection()
        try:
            row = db.execute(
                "SELECT body FROM releases WHERE id=?", (identity,)
            ).fetchone()
            if not row:
                raise ValueError("发布版本不存在")
            return json.loads(row[0])
        finally:
            db.close()

    def audit(self):
        db = self.connection()
        try:
            return [
                dict(
                    zip(("id", "created", "actor", "event", "target"), row, strict=True)
                )
                for row in db.execute(
                    "SELECT id,created,actor,event,target FROM audit "
                    "ORDER BY id DESC LIMIT 500"
                )
            ]
        finally:
            db.close()

    def close(self):
        if self.lease is not None:
            os.close(self.lease)
            self.lease = None
