"""Shared account use cases. Provisioning is an offline operator action only."""

from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
from collections.abc import Callable

from mxsj_server.contracts.common import (
    CommandReceipt,
    CommandSource,
    DomainError,
    RequestContext,
)
from mxsj_server.modules.account.contracts import LoginRequest, LoginResult
from mxsj_server.modules.account.domain.security import (
    account_key,
    encode_password,
    password_bytes,
    verify_password,
)
from mxsj_server.observability.events import DEFAULT_EVENTS, EventLogger
from mxsj_server.observability.tracing import mark, observed
from mxsj_server.persistence.ports import Store
from mxsj_server.runtime.sessions import fence, operation_id
from mxsj_server.runtime.tickets import ticket_digest


class AccountService:
    def __init__(
        self,
        store: Store,
        realm_id: int,
        clock: Callable[[], int],
        ttl_ms: int,
        events: EventLogger | None = None,
    ):
        self.store, self.realm_id, self.clock = store, realm_id, clock
        self.events = events if events is not None else DEFAULT_EVENTS
        self.ttl_ms = ttl_ms
        # Equal-cost password work for unknown accounts (never a valid login).
        self.dummy = encode_password(secrets.token_urlsafe(32).encode("ascii"))

    @observed("account.provision")
    async def provision(self, name: str, credential: bytes) -> int:
        """Trusted local operator, not a player API or auto-registration on login."""
        key, credential = account_key(name), password_bytes(credential)

        def create() -> int:
            encoded = encode_password(credential)
            with self.store.transaction() as uow:
                if uow.accounts.by_name(key) is not None:
                    raise DomainError("ALREADY_EXISTS")
                return uow.accounts.insert(key, encoded)

        return await asyncio.to_thread(create)

    @observed("account.authenticate")
    async def authenticate(self, request: LoginRequest) -> LoginResult:
        if request.protocol_version != "operator-utf8-v1":
            raise DomainError(
                "UNSUPPORTED_PROTOCOL", "Legacy credential adapter pending"
            )
        key, credential = (
            account_key(request.account_name),
            password_bytes(request.credential),
        )

        def login() -> LoginResult:
            with self.store.transaction() as uow:
                account = uow.accounts.by_name(key)
            valid = verify_password(
                credential,
                account.password_hash if account is not None else self.dummy,
            )
            if account is None or not valid:
                raise DomainError("UNAUTHENTICATED")
            ticket = secrets.token_urlsafe(32)
            with self.store.transaction() as uow:
                # Re-read after hashing: changed credentials must not race login.
                fresh = uow.accounts.by_name(key)
                if fresh != account:
                    raise DomainError("UNAUTHENTICATED")
                expiry = self.clock() + self.ttl_ms
                previous = uow.sessions.current(account.account_id, self.realm_id)
                new_session = uow.sessions.replace(
                    account.account_id, self.realm_id, ticket_digest(ticket), expiry
                )
            mark(
                takeover=previous is not None and previous.expires_at_ms > self.clock(),
                session_epoch=new_session.epoch,
            )
            return LoginResult(
                account_id=account.account_id,
                session_ticket=ticket,
                expires_at_ms=expiry,
            )

        return await asyncio.to_thread(login)

    @observed("account.revoke")
    async def revoke_sessions(
        self,
        ctx: RequestContext,
        *,
        account_id: int,
        reason: str,
    ) -> CommandReceipt:
        if account_id != ctx.account_id or ctx.realm_id != self.realm_id:
            raise DomainError("FORBIDDEN")
        if not isinstance(reason, str) or not 1 <= len(reason) <= 128:
            raise DomainError("INVALID_ARGUMENT")

        operation_id(ctx.operation_id)
        if ctx.source != CommandSource.CLIENT or type(ctx.session_epoch) is not int:
            raise DomainError("UNAUTHENTICATED")
        fingerprint = hashlib.sha256(
            json.dumps(
                ["account.revoke/v1", account_id, ctx.session_epoch, reason],
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        def revoke() -> CommandReceipt:
            with self.store.transaction() as uow:
                # A retry of this exact trusted pre-revoke context may retrieve
                # its receipt. It cannot perform any further mutation after logout.
                previous = uow.operations.get(
                    account_id, self.realm_id, ctx.operation_id
                )
                if previous is not None:
                    if previous.request_hash != fingerprint:
                        raise DomainError("IDEMPOTENCY_CONFLICT")
                    mark(replay=True)
                    return CommandReceipt(
                        operation_id=ctx.operation_id,
                        revision=json.loads(previous.response)["epoch"],
                    )
                fence(uow, ctx, self.realm_id, self.clock())
                epoch = uow.sessions.revoke(account_id, self.realm_id)
                uow.operations.put(
                    account_id,
                    self.realm_id,
                    ctx.operation_id,
                    fingerprint,
                    json.dumps({"epoch": epoch}),
                )
            return CommandReceipt(operation_id=ctx.operation_id, revision=epoch)

        return await asyncio.to_thread(revoke)
