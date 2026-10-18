"""Composition root: SQLite is selected here, not inside business use cases."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from mxsj_local_server.core.modules.account.application.service import AccountService
from mxsj_local_server.core.modules.character.application.service import (
    CharacterService,
)
from mxsj_local_server.core.modules.character.domain.creation import CreationPolicy
from mxsj_local_server.core.observability.events import DEFAULT_EVENTS, EventLogger
from mxsj_local_server.core.persistence.ports import Store
from mxsj_local_server.core.persistence.sqlite.store import SQLiteStore
from mxsj_local_server.core.runtime.sessions import SessionAuthority


@dataclass(frozen=True)
class Services:
    accounts: AccountService
    characters: CharacterService
    sessions: SessionAuthority
    events: EventLogger


def compose(
    store: Store,
    *,
    realm_id: int,
    policy: CreationPolicy,
    session_ttl_ms: int = 3_600_000,
    clock: Callable[[], int] | None = None,
    events: EventLogger | None = None,
) -> Services:
    if type(realm_id) is not int or not 1 <= realm_id <= 65535:
        raise ValueError("Invalid realm_id")
    if type(session_ttl_ms) is not int or not 60_000 <= session_ttl_ms <= 86_400_000:
        raise ValueError("Session TTL must be 1 minute to 1 day")
    clock = clock or (lambda: time.time_ns() // 1_000_000)
    events = events if events is not None else getattr(store, "events", DEFAULT_EVENTS)
    return Services(
        AccountService(store, realm_id, clock, session_ttl_ms, events),
        CharacterService(store, realm_id, clock, policy, events),
        SessionAuthority(store, realm_id, clock, events),
        events,
    )


def open_local(
    path: Path,
    *,
    realm_id: int,
    policy: CreationPolicy,
    session_ttl_ms: int,
    events: EventLogger | None = None,
) -> Services:
    store = SQLiteStore(path, events=events)
    store.check()  # Never silently initialize on service start.
    return compose(
        store,
        realm_id=realm_id,
        policy=policy,
        session_ttl_ms=session_ttl_ms,
        events=events,
    )
