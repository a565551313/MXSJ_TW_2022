"""Trusted-context construction plus transaction-time session fencing."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable

from mxsj_local_server.core.contracts.common import (
    CommandSource,
    DomainError,
    RequestContext,
)
from mxsj_local_server.core.observability.events import DEFAULT_EVENTS, EventLogger
from mxsj_local_server.core.observability.tracing import mark, note, observed, trace_id
from mxsj_local_server.core.persistence.ports import Store, UnitOfWork
from mxsj_local_server.core.runtime.tickets import ticket_digest


def operation_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value):
        raise DomainError("INVALID_ARGUMENT", "Invalid operation_id")
    return value


def fence(uow: UnitOfWork, ctx: RequestContext, realm: int, now_ms: int) -> None:
    """Called under the mutation transaction, not just before enqueueing work."""
    operation_id(ctx.operation_id)
    if (
        ctx.source != CommandSource.CLIENT
        or ctx.realm_id != realm
        or type(ctx.account_id) is not int
        or ctx.account_id <= 0
        or type(ctx.session_epoch) is not int
    ):
        raise DomainError("UNAUTHENTICATED")
    row = uow.sessions.current(ctx.account_id, realm)
    if row is None or row.epoch != ctx.session_epoch:
        note("session.stale", error_code="UNAUTHENTICATED")
        raise DomainError("UNAUTHENTICATED")
    if row.expires_at_ms <= now_ms:
        note("session.expired", error_code="UNAUTHENTICATED")
        raise DomainError("UNAUTHENTICATED")


class SessionAuthority:
    def __init__(
        self,
        store: Store,
        realm_id: int,
        clock: Callable[[], int],
        events: EventLogger | None = None,
    ):
        self.store, self.realm_id, self.clock = store, realm_id, clock
        self.events = events if events is not None else DEFAULT_EVENTS

    @observed("session.context")
    async def context(
        self,
        ticket: str,
        op_id: str,
        *,
        character_id: int | None = None,
    ) -> RequestContext:
        mark(operation_id=op_id)
        digest, op_id = ticket_digest(ticket), operation_id(op_id)
        if character_id is not None and (
            type(character_id) is not int or character_id <= 0
        ):
            raise DomainError("INVALID_ARGUMENT")

        def load() -> RequestContext:
            with self.store.transaction() as uow:
                row = uow.sessions.by_ticket(digest)
                if row is None or row.realm_id != self.realm_id:
                    raise DomainError("UNAUTHENTICATED")
                mark(account_id=row.account_id, session_epoch=row.epoch)
                if row.expires_at_ms <= self.clock():
                    note("session.expired", error_code="UNAUTHENTICATED")
                    raise DomainError("UNAUTHENTICATED")
                if (
                    character_id is not None
                    and uow.characters.owned(row.account_id, row.realm_id, character_id)
                    is None
                ):
                    raise DomainError("FORBIDDEN")
                return RequestContext(
                    operation_id=op_id,
                    trace_id=trace_id(),
                    realm_id=row.realm_id,
                    account_id=row.account_id,
                    character_id=character_id,
                    session_epoch=row.epoch,
                    source=CommandSource.CLIENT,
                )

        return await asyncio.to_thread(load)
