"""SQL mapping only; authorization and policy belong to shared services."""

from __future__ import annotations

import sqlite3

from mxsj_server.modules.character.contracts import CharacterView
from mxsj_server.persistence.ports import AccountRow, OperationRow, SessionRow


class AccountRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection

    def by_name(self, name_key: str) -> AccountRow | None:
        row = self.db.execute(
            "SELECT account_id, name_key, password_hash FROM accounts WHERE name_key=?",
            (name_key,),
        ).fetchone()
        return AccountRow(*row) if row else None

    def insert(self, name_key: str, password_hash: str) -> int:
        cursor = self.db.execute(
            "INSERT INTO accounts(name_key,password_hash) VALUES (?,?)",
            (name_key, password_hash),
        )
        return cursor.lastrowid


class SessionRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection

    def by_ticket(self, digest: str) -> SessionRow | None:
        row = self.db.execute(
            "SELECT account_id,realm_id,epoch,expires_at_ms FROM sessions "
            "WHERE ticket_hash=?",
            (digest,),
        ).fetchone()
        return SessionRow(*row) if row else None

    def current(self, account_id: int, realm_id: int) -> SessionRow | None:
        row = self.db.execute(
            "SELECT account_id,realm_id,epoch,expires_at_ms FROM sessions "
            "WHERE account_id=? AND realm_id=?",
            (account_id, realm_id),
        ).fetchone()
        return SessionRow(*row) if row else None

    def replace(
        self,
        account_id: int,
        realm_id: int,
        digest: str,
        expires_at_ms: int,
    ) -> SessionRow:
        self.db.execute(
            "INSERT INTO sessions(account_id,realm_id,epoch,ticket_hash,expires_at_ms) "
            "VALUES (?,?,1,?,?) ON CONFLICT(account_id,realm_id) DO UPDATE SET "
            "epoch=sessions.epoch+1,ticket_hash=excluded.ticket_hash,"
            "expires_at_ms=excluded.expires_at_ms",
            (account_id, realm_id, digest, expires_at_ms),
        )
        return self.current(account_id, realm_id)

    def revoke(self, account_id: int, realm_id: int) -> int:
        self.db.execute(
            "UPDATE sessions SET epoch=epoch+1,ticket_hash=NULL,expires_at_ms=0 "
            "WHERE account_id=? AND realm_id=?",
            (account_id, realm_id),
        )
        return self.current(account_id, realm_id).epoch


class CharacterRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection

    def list_owned(self, account_id: int, realm_id: int) -> tuple[CharacterView, ...]:
        rows = self.db.execute(
            "SELECT character_id,name,level,school_id,revision FROM characters "
            "WHERE account_id=? AND realm_id=? ORDER BY character_id",
            (account_id, realm_id),
        ).fetchall()
        return tuple(CharacterView(**dict(row)) for row in rows)

    def owned(
        self,
        account_id: int,
        realm_id: int,
        character_id: int,
    ) -> CharacterView | None:
        row = self.db.execute(
            "SELECT character_id,name,level,school_id,revision FROM characters "
            "WHERE account_id=? AND realm_id=? AND character_id=?",
            (account_id, realm_id, character_id),
        ).fetchone()
        return CharacterView(**dict(row)) if row else None

    def name_exists(self, realm_id: int, name_key: str) -> bool:
        return (
            self.db.execute(
                "SELECT 1 FROM characters WHERE realm_id=? AND name_key=?",
                (realm_id, name_key),
            ).fetchone()
            is not None
        )

    def insert(
        self,
        account_id: int,
        realm_id: int,
        name: str,
        name_key: str,
        appearance: int,
        school: int,
        level: int,
    ) -> CharacterView:
        cursor = self.db.execute(
            "INSERT INTO characters(account_id,realm_id,name,name_key,appearance,"
            "school_id,level,revision) VALUES (?,?,?,?,?,?,?,1)",
            (account_id, realm_id, name, name_key, appearance, school, level),
        )
        return self.owned(account_id, realm_id, cursor.lastrowid)


class OperationRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection

    def get(
        self,
        account_id: int,
        realm_id: int,
        operation_id: str,
    ) -> OperationRow | None:
        row = self.db.execute(
            "SELECT request_hash,response FROM operations "
            "WHERE account_id=? AND realm_id=? AND operation_id=?",
            (account_id, realm_id, operation_id),
        ).fetchone()
        return OperationRow(*row) if row else None

    def put(
        self,
        account_id: int,
        realm_id: int,
        operation_id: str,
        request_hash: str,
        response: str,
    ) -> None:
        self.db.execute(
            "INSERT INTO operations VALUES (?,?,?,?,?)",
            (account_id, realm_id, operation_id, request_hash, response),
        )


class SQLiteUnitOfWork:
    def __init__(self, connection: sqlite3.Connection):
        self.accounts = AccountRepository(connection)
        self.sessions = SessionRepository(connection)
        self.characters = CharacterRepository(connection)
        self.operations = OperationRepository(connection)
