"""Executable prototype for the registration-to-map game loop.

This adapter is intentionally SQLite/stdlib-only so the first loop can be run
and tested without inventing a client wire protocol or installing dependencies.
It is a development prototype, not the planned PostgreSQL production adapter.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mxsj_server.contracts.common import DomainError

_PASSWORD_ITERATIONS = 310_000
_PASSWORD_MIN_LENGTH = 10
_ACCOUNT_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
_CHARACTER_RE = re.compile(r"^[\w\u4e00-\u9fff-]{2,16}$", re.UNICODE)
_TICKET_TTL_MS = 12 * 60 * 60 * 1000
_DEFAULT_MAP_TEMPLATE_ID = 1
_DEFAULT_X = 10
_DEFAULT_Y = 10


@dataclass(frozen=True, slots=True)
class Realm:
    realm_id: int
    name: str
    status: str


@dataclass(frozen=True, slots=True)
class Character:
    character_id: int
    name: str
    level: int
    school_id: int
    revision: int


@dataclass(frozen=True, slots=True)
class MapEntry:
    character_id: int
    map_instance_id: int
    map_template_id: int
    x: int
    y: int
    revision: int


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise DomainError("INVALID_ARGUMENT", f"invalid {field}")
    return value


def _required_text(value: Any, field: str, *, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise DomainError("INVALID_ARGUMENT", f"invalid {field}")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise DomainError("INVALID_ARGUMENT", f"invalid {field}")
    return value.strip()


class GameLoopService:
    """Synchronous transaction-oriented service for the first playable flow."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        migration = Path(__file__).resolve().parents[3] / "migrations" / "0001_playable_loop.sql"
        schema = migration.read_text(encoding="utf-8")
        with closing(self._connect()) as connection:
            connection.executescript(schema)
            connection.execute(
                "INSERT OR IGNORE INTO realms(realm_id, name, status) VALUES(1, '开发区', 'online')"
            )
            connection.execute(
                "INSERT OR IGNORE INTO map_templates(map_template_id, name, spawn_x, spawn_y) "
                "VALUES(?, '起始地图（开发占位）', ?, ?)",
                (_DEFAULT_MAP_TEMPLATE_ID, _DEFAULT_X, _DEFAULT_Y),
            )

    def register(self, account_name: str, password: str) -> dict[str, Any]:
        name = _required_text(account_name, "account_name", maximum=32)
        if not _ACCOUNT_RE.fullmatch(name):
            raise DomainError("INVALID_ARGUMENT", "account name must be 3-32 ASCII letters, digits, _, . or -")
        if not isinstance(password, str) or not _PASSWORD_MIN_LENGTH <= len(password) <= 128:
            raise DomainError("INVALID_ARGUMENT", "password length must be 10-128 characters")
        if any(ord(c) < 32 or ord(c) == 127 for c in password):
            raise DomainError("INVALID_ARGUMENT", "invalid password")
        normalized = name.casefold()
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS)
        try:
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute(
                    "INSERT INTO accounts(account_name, normalized_name, password_salt, password_hash, created_at_ms) "
                    "VALUES(?, ?, ?, ?, ?)",
                    (name, normalized, salt, digest, _now_ms()),
                )
                account_id = int(cursor.lastrowid)
                connection.commit()
        except sqlite3.IntegrityError as exc:
            raise DomainError("CONFLICT", "account name already exists") from exc
        return {"account_id": account_id, "account_name": name}

    def list_realms(self) -> tuple[Realm, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT realm_id, name, status FROM realms WHERE status = 'online' ORDER BY realm_id"
            ).fetchall()
        return tuple(Realm(int(r["realm_id"]), str(r["name"]), str(r["status"])) for r in rows)

    def select_realm(self, realm_id: int) -> Realm:
        realm_id = _positive_int(realm_id, "realm_id")
        with self._connect() as connection:
            row = connection.execute(
                "SELECT realm_id, name, status FROM realms WHERE realm_id = ? AND status = 'online'",
                (realm_id,),
            ).fetchone()
        if row is None:
            raise DomainError("NOT_FOUND", "realm not found or unavailable")
        return Realm(int(row["realm_id"]), str(row["name"]), str(row["status"]))

    def login(self, account_name: str, password: str, realm_id: int) -> dict[str, Any]:
        name = _required_text(account_name, "account_name", maximum=32)
        if not isinstance(password, str) or not password or len(password) > 128:
            raise DomainError("UNAUTHENTICATED", "invalid account name or password")
        realm = self.select_realm(realm_id)
        with self._connect() as connection:
            account = connection.execute(
                "SELECT account_id, account_name, password_salt, password_hash, disabled "
                "FROM accounts WHERE normalized_name = ?",
                (name.casefold(),),
            ).fetchone()
            if account is None or account["disabled"]:
                raise DomainError("UNAUTHENTICATED", "invalid account name or password")
            candidate = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes(account["password_salt"]), _PASSWORD_ITERATIONS
            )
            if not hmac.compare_digest(candidate, bytes(account["password_hash"])):
                raise DomainError("UNAUTHENTICATED", "invalid account name or password")
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT session_epoch FROM account_sessions WHERE realm_id = ? AND account_id = ?",
                (realm.realm_id, int(account["account_id"])),
            ).fetchone()
            epoch = (int(row["session_epoch"]) + 1) if row else 1
            ticket = secrets.token_urlsafe(32)
            ticket_hash = hashlib.sha256(ticket.encode("ascii")).digest()
            expires_at = _now_ms() + _TICKET_TTL_MS
            connection.execute(
                "INSERT INTO account_sessions(realm_id, account_id, ticket_hash, session_epoch, expires_at_ms, "
                "selected_character_id, updated_at_ms) VALUES(?, ?, ?, ?, ?, NULL, ?) "
                "ON CONFLICT(realm_id, account_id) DO UPDATE SET ticket_hash=excluded.ticket_hash, "
                "session_epoch=excluded.session_epoch, expires_at_ms=excluded.expires_at_ms, "
                "selected_character_id=NULL, updated_at_ms=excluded.updated_at_ms",
                (realm.realm_id, int(account["account_id"]), ticket_hash, epoch, expires_at, _now_ms()),
            )
            connection.commit()
        return {
            "account_id": int(account["account_id"]),
            "account_name": str(account["account_name"]),
            "realm_id": realm.realm_id,
            "session_ticket": ticket,
            "session_epoch": epoch,
            "expires_at_ms": expires_at,
        }

    def _authenticated_session(
        self, connection: sqlite3.Connection, ticket: str, *, realm_id: int
    ) -> sqlite3.Row:
        if not isinstance(ticket, str) or not 20 <= len(ticket) <= 128:
            raise DomainError("UNAUTHENTICATED", "valid session ticket required")
        realm_id = _positive_int(realm_id, "realm_id")
        ticket_hash = hashlib.sha256(ticket.encode("ascii", errors="ignore")).digest()
        row = connection.execute(
            "SELECT s.realm_id, s.account_id, s.ticket_hash, s.session_epoch, s.expires_at_ms, "
            "s.selected_character_id FROM account_sessions s JOIN accounts a USING(account_id) "
            "WHERE s.realm_id = ? AND s.ticket_hash = ? AND a.disabled = 0",
            (realm_id, ticket_hash),
        ).fetchone()
        if row is None or int(row["expires_at_ms"]) <= _now_ms():
            raise DomainError("UNAUTHENTICATED", "session expired or revoked")
        return row

    def create_character(
        self,
        ticket: str,
        realm_id: int,
        operation_id: str,
        name: str,
        *,
        appearance_template_id: int = 1,
        school_id: int = 1,
    ) -> Character:
        operation_id = _required_text(operation_id, "operation_id", maximum=128)
        name = _required_text(name, "character_name", maximum=16)
        if not _CHARACTER_RE.fullmatch(name):
            raise DomainError("INVALID_ARGUMENT", "character name must be 2-16 letters, digits, Chinese characters, _ or -")
        appearance_template_id = _positive_int(appearance_template_id, "appearance_template_id")
        school_id = _positive_int(school_id, "school_id")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            session = self._authenticated_session(connection, ticket, realm_id=realm_id)
            prior = connection.execute(
                "SELECT result_character_id, request_fingerprint FROM idempotency_records "
                "WHERE realm_id=? AND account_id=? AND operation_id=?",
                (realm_id, int(session["account_id"]), operation_id),
            ).fetchone()
            fingerprint = hashlib.sha256(
                json.dumps([name, appearance_template_id, school_id], ensure_ascii=False, separators=(",", ":")).encode()
            ).digest()
            if prior:
                if not hmac.compare_digest(bytes(prior["request_fingerprint"]), fingerprint):
                    raise DomainError("CONFLICT", "operation_id reused with different request")
                row = connection.execute(
                    "SELECT character_id, name, level, school_id, revision FROM characters "
                    "WHERE character_id=? AND account_id=? AND realm_id=?",
                    (int(prior["result_character_id"]), int(session["account_id"]), realm_id),
                ).fetchone()
                if row is None:
                    raise DomainError("INVALID_STATE", "idempotency result is unavailable")
                connection.commit()
                return _character(row)
            count = connection.execute(
                "SELECT COUNT(*) AS n FROM characters WHERE account_id=? AND realm_id=?",
                (int(session["account_id"]), realm_id),
            ).fetchone()["n"]
            if int(count) >= 4:
                raise DomainError("INVALID_STATE", "character limit reached")
            cursor = connection.execute(
                "INSERT INTO characters(realm_id, account_id, name, appearance_template_id, school_id, "
                "level, revision, created_at_ms) VALUES(?, ?, ?, ?, ?, 1, 1, ?)",
                (realm_id, int(session["account_id"]), name, appearance_template_id, school_id, _now_ms()),
            )
            character_id = int(cursor.lastrowid)
            connection.execute(
                "INSERT INTO idempotency_records(realm_id, account_id, operation_id, request_fingerprint, "
                "result_character_id, created_at_ms) VALUES(?, ?, ?, ?, ?, ?)",
                (realm_id, int(session["account_id"]), operation_id, fingerprint, character_id, _now_ms()),
            )
            row = connection.execute(
                "SELECT character_id, name, level, school_id, revision FROM characters WHERE character_id=?",
                (character_id,),
            ).fetchone()
            connection.commit()
        return _character(row)

    def list_characters(self, ticket: str, realm_id: int) -> tuple[Character, ...]:
        with self._connect() as connection:
            session = self._authenticated_session(connection, ticket, realm_id=realm_id)
            rows = connection.execute(
                "SELECT character_id, name, level, school_id, revision FROM characters "
                "WHERE realm_id=? AND account_id=? ORDER BY character_id",
                (realm_id, int(session["account_id"])),
            ).fetchall()
        return tuple(_character(row) for row in rows)

    def select_character(self, ticket: str, realm_id: int, character_id: int) -> Character:
        character_id = _positive_int(character_id, "character_id")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            session = self._authenticated_session(connection, ticket, realm_id=realm_id)
            row = connection.execute(
                "SELECT character_id, name, level, school_id, revision FROM characters "
                "WHERE character_id=? AND realm_id=? AND account_id=?",
                (character_id, realm_id, int(session["account_id"])),
            ).fetchone()
            if row is None:
                raise DomainError("FORBIDDEN", "character does not belong to this account in this realm")
            connection.execute(
                "UPDATE account_sessions SET selected_character_id=?, updated_at_ms=? "
                "WHERE realm_id=? AND account_id=? AND session_epoch=?",
                (character_id, _now_ms(), realm_id, int(session["account_id"]), int(session["session_epoch"])),
            )
            connection.commit()
        return _character(row)

    def enter_map(self, ticket: str, realm_id: int) -> MapEntry:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            session = self._authenticated_session(connection, ticket, realm_id=realm_id)
            character_id = session["selected_character_id"]
            if character_id is None:
                raise DomainError("INVALID_STATE", "select a character before entering the map")
            character = connection.execute(
                "SELECT character_id FROM characters WHERE character_id=? AND account_id=? AND realm_id=?",
                (int(character_id), int(session["account_id"]), realm_id),
            ).fetchone()
            if character is None:
                raise DomainError("FORBIDDEN", "selected character ownership check failed")
            template = connection.execute(
                "SELECT map_template_id, spawn_x, spawn_y FROM map_templates WHERE map_template_id=?",
                (_DEFAULT_MAP_TEMPLATE_ID,),
            ).fetchone()
            if template is None:
                raise DomainError("INVALID_STATE", "no starting map configured")
            current = connection.execute(
                "SELECT map_instance_id, revision FROM character_positions WHERE character_id=?",
                (int(character_id),),
            ).fetchone()
            if current is None:
                cursor = connection.execute(
                    "INSERT INTO map_instances(realm_id, map_template_id, created_at_ms) VALUES(?, ?, ?)",
                    (realm_id, int(template["map_template_id"]), _now_ms()),
                )
                instance_id = int(cursor.lastrowid)
                x, y, revision = int(template["spawn_x"]), int(template["spawn_y"]), 1
                connection.execute(
                    "INSERT INTO character_positions(character_id, map_instance_id, x, y, revision, updated_at_ms) "
                    "VALUES(?, ?, ?, ?, ?, ?)",
                    (int(character_id), instance_id, x, y, revision, _now_ms()),
                )
            else:
                instance_id, revision = int(current["map_instance_id"]), int(current["revision"])
                position = connection.execute(
                    "SELECT x, y FROM character_positions WHERE character_id=?",
                    (int(character_id),),
                ).fetchone()
                x, y = int(position["x"]), int(position["y"])
            connection.commit()
        return MapEntry(int(character_id), instance_id, int(template["map_template_id"]), x, y, revision)


def _character(row: sqlite3.Row) -> Character:
    return Character(
        character_id=int(row["character_id"]),
        name=str(row["name"]),
        level=int(row["level"]),
        school_id=int(row["school_id"]),
        revision=int(row["revision"]),
    )
