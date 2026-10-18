"""Shared character use cases: ownership, fencing, atomic idempotent creation."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Callable
from dataclasses import asdict

from mxsj_server.contracts.common import CommandReceipt, DomainError, RequestContext
from mxsj_server.modules.character.contracts import CharacterView, CreateCharacter
from mxsj_server.modules.character.domain.creation import CreationPolicy
from mxsj_server.observability.events import DEFAULT_EVENTS, EventLogger
from mxsj_server.observability.tracing import mark, observed
from mxsj_server.persistence.ports import Store
from mxsj_server.runtime.sessions import fence


class CharacterService:
    def __init__(
        self,
        store: Store,
        realm_id: int,
        clock: Callable[[], int],
        policy: CreationPolicy,
        events: EventLogger | None = None,
    ):
        self.events = events if events is not None else DEFAULT_EVENTS
        self.store, self.realm_id, self.clock, self.policy = (
            store,
            realm_id,
            clock,
            policy,
        )

    @observed("character.list")
    async def list_characters(self, ctx: RequestContext) -> tuple[CharacterView, ...]:
        def load():
            with self.store.transaction() as uow:
                fence(uow, ctx, self.realm_id, self.clock())
                return uow.characters.list_owned(ctx.account_id, self.realm_id)

        return await asyncio.to_thread(load)

    @observed("character.create")
    async def create(
        self, ctx: RequestContext, request: CreateCharacter
    ) -> CharacterView:
        name, key = self.policy.validate(request)
        payload = json.dumps(
            [
                "character.create/v1",
                name,
                request.appearance_template_id,
                request.school_id,
            ],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        def create():
            with self.store.transaction() as uow:
                fence(uow, ctx, self.realm_id, self.clock())
                previous = uow.operations.get(
                    ctx.account_id, self.realm_id, ctx.operation_id
                )
                if previous is not None:
                    if previous.request_hash != fingerprint:
                        raise DomainError("IDEMPOTENCY_CONFLICT")
                    mark(replay=True)
                    return CharacterView(**json.loads(previous.response))
                if (
                    len(uow.characters.list_owned(ctx.account_id, self.realm_id))
                    >= self.policy.max_characters
                ):
                    raise DomainError("CHARACTER_LIMIT")
                if uow.characters.name_exists(self.realm_id, key):
                    raise DomainError("NAME_TAKEN")
                view = uow.characters.insert(
                    ctx.account_id,
                    self.realm_id,
                    name,
                    key,
                    request.appearance_template_id,
                    request.school_id,
                    self.policy.initial_level,
                )
                uow.operations.put(
                    ctx.account_id,
                    self.realm_id,
                    ctx.operation_id,
                    fingerprint,
                    json.dumps(asdict(view), sort_keys=True, separators=(",", ":")),
                )
            # Exiting the transaction (including commit) must succeed before returning.
            return view

        return await asyncio.to_thread(create)

    @observed("character.enter_world")
    async def enter_world(
        self,
        ctx: RequestContext,
        *,
        character_id: int,
    ) -> CommandReceipt:
        def check():
            with self.store.transaction() as uow:
                fence(uow, ctx, self.realm_id, self.clock())
                if (
                    uow.characters.owned(ctx.account_id, self.realm_id, character_id)
                    is None
                ):
                    raise DomainError("FORBIDDEN")
            raise DomainError("NOT_IMPLEMENTED", "World/protocol migration is pending")

        return await asyncio.to_thread(check)
