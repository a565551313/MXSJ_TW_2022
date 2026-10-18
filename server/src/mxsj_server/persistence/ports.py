"""Database-neutral ports for the first account/character transaction slice.

Adapters must serialize writers and fence sessions in the same transaction as
character changes. A PostgreSQL adapter must provide equivalent row locking;
implementing these signatures alone is not sufficient.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Protocol

from mxsj_server.modules.character.contracts import CharacterView


@dataclass(frozen=True)
class AccountRow:
    account_id: int
    name_key: str
    password_hash: str = field(repr=False)


@dataclass(frozen=True)
class SessionRow:
    account_id: int
    realm_id: int
    epoch: int
    expires_at_ms: int


@dataclass(frozen=True)
class OperationRow:
    request_hash: str
    response: str


class Accounts(Protocol):
    def by_name(self, name_key: str) -> AccountRow | None: ...
    def insert(self, name_key: str, password_hash: str) -> int: ...


class Sessions(Protocol):
    def by_ticket(self, digest: str) -> SessionRow | None: ...
    def current(self, account_id: int, realm_id: int) -> SessionRow | None: ...
    def replace(
        self, account_id: int, realm_id: int, digest: str, expires_at_ms: int
    ) -> SessionRow: ...
    def revoke(self, account_id: int, realm_id: int) -> int: ...


class Characters(Protocol):
    def list_owned(
        self, account_id: int, realm_id: int
    ) -> tuple[CharacterView, ...]: ...
    def owned(
        self, account_id: int, realm_id: int, character_id: int
    ) -> CharacterView | None: ...
    def name_exists(self, realm_id: int, name_key: str) -> bool: ...
    def insert(
        self,
        account_id: int,
        realm_id: int,
        name: str,
        name_key: str,
        appearance: int,
        school: int,
        level: int,
    ) -> CharacterView: ...


class Operations(Protocol):
    def get(
        self, account_id: int, realm_id: int, operation_id: str
    ) -> OperationRow | None: ...
    def put(
        self,
        account_id: int,
        realm_id: int,
        operation_id: str,
        request_hash: str,
        response: str,
    ) -> None: ...


class UnitOfWork(Protocol):
    accounts: Accounts
    sessions: Sessions
    characters: Characters
    operations: Operations


class Store(Protocol):
    def transaction(self) -> AbstractContextManager[UnitOfWork]:
        """Commit only on successful exit; rollback every exceptional exit."""
        ...
