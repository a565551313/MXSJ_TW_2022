"""Per-operation ContextVar correlation, including asyncio.to_thread workers."""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps

from mxsj_local_server.core.contracts.common import RequestContext
from mxsj_local_server.core.observability.events import (
    DEFAULT_EVENTS,
    TRACE,
    safe_error,
)


@dataclass
class Observation:
    logger: object
    fields: dict = field(default_factory=dict)
    replay: bool = False
    takeover: bool = False


CURRENT: ContextVar[Observation | None] = ContextVar("mxsj_observation", default=None)


def trace_id():
    scope = CURRENT.get()
    return scope.fields["trace_id"] if scope is not None else uuid.uuid4().hex


def mark(*, replay=False, takeover=False, **fields):
    scope = CURRENT.get()
    if scope is not None:
        scope.replay |= replay
        scope.takeover |= takeover
        # The sink, not the caller, enforces the final field whitelist.
        scope.fields.update(fields)


def note(event, *, error_code=None):
    scope = CURRENT.get()
    if scope is not None:
        scope.logger.emit(
            event,
            outcome="failed" if error_code else "succeeded",
            error_code=error_code,
            **scope.fields,
        )


def observed(event):
    """No argument/result repr; business success only after awaited commit returns.

    Cancellation of a to_thread waiter has unknown outcome. The worker may still
    commit; its database events keep the inherited trace and no false rollback is
    reported. This is diagnostics, not a transactional audit/outbox.
    """

    def decorate(method):
        @wraps(method)
        async def call(self, *args, **kwargs):
            logger = self.events
            fields = {"realm_id": self.realm_id, "trace_id": uuid.uuid4().hex}
            ctx = next(
                (v for v in (*args, *kwargs.values()) if isinstance(v, RequestContext)),
                None,
            )
            if ctx is not None:
                fields.update(
                    {
                        "account_id": ctx.account_id,
                        "character_id": ctx.character_id,
                        "session_epoch": ctx.session_epoch,
                        "operation_id": ctx.operation_id,
                    }
                )
                if isinstance(ctx.trace_id, str) and TRACE.fullmatch(ctx.trace_id):
                    fields["trace_id"] = ctx.trace_id
            scope = Observation(logger, fields)
            token = CURRENT.set(scope)
            start = time.monotonic_ns()
            try:
                result = await method(self, *args, **kwargs)
                if event == "account.provision":
                    fields["account_id"] = result
                elif event == "account.authenticate":
                    fields["account_id"] = result.account_id
                elif event == "character.create":
                    fields["character_id"] = result.character_id
                fields["duration_ms"] = (time.monotonic_ns() - start) // 1_000_000
                logger.emit(
                    event, outcome="replayed" if scope.replay else "succeeded", **fields
                )
                if scope.takeover:
                    logger.emit("session.takeover", **fields)
                return result
            except asyncio.CancelledError:
                logger.emit(
                    event, outcome="unknown", error_code="CANCELLED_UNKNOWN", **fields
                )
                raise
            except Exception as exc:
                fields["duration_ms"] = (time.monotonic_ns() - start) // 1_000_000
                logger.emit(
                    event,
                    outcome="failed",
                    error_code=safe_error(exc),
                    exception=exc,
                    **fields,
                )
                raise
            finally:
                CURRENT.reset(token)

        return call

    return decorate


@contextmanager
def span(logger, event):
    scope = CURRENT.get()
    fields = dict(scope.fields) if scope is not None else {"trace_id": uuid.uuid4().hex}
    start = time.monotonic_ns()
    try:
        yield
    except Exception as exc:
        fields["duration_ms"] = (time.monotonic_ns() - start) // 1_000_000
        logger.emit(
            event, outcome="failed", error_code=safe_error(exc), exception=exc, **fields
        )
        if safe_error(exc) == "TEMPORARILY_UNAVAILABLE":
            logger.emit(
                "database.busy", outcome="failed", error_code=safe_error(exc), **fields
            )
        raise
    else:
        fields["duration_ms"] = (time.monotonic_ns() - start) // 1_000_000
        logger.emit(event, **fields)


def observed_sync(event):
    def decorate(method):
        @wraps(method)
        def call(self, *args, **kwargs):
            with span(getattr(self, "events", DEFAULT_EVENTS), event):
                return method(self, *args, **kwargs)

        return call

    return decorate


@contextmanager
def bind(logger, *, realm_id):
    """Bootstrap scope for schema/startup events; nested use cases get own traces."""
    scope = Observation(logger, {"realm_id": realm_id, "trace_id": uuid.uuid4().hex})
    token = CURRENT.set(scope)
    try:
        yield scope.fields
    finally:
        CURRENT.reset(token)
