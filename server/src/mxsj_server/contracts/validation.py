"""Runtime validation helpers for trusted internal request contexts.

These checks are defense in depth at application boundaries. They do not
authenticate a caller, prove character ownership, or replace authorization.
"""
from __future__ import annotations

from mxsj_server.contracts.common import CommandSource, DomainError, RequestContext

_MAX_CONTEXT_ID_LENGTH = 128


def validate_request_context(
    ctx: RequestContext,
    *,
    require_character: bool = False,
) -> None:
    """Reject malformed context before application code uses its identity fields.

    RequestContext is frozen but Python type hints are not runtime validation.
    The transport layer must never construct it directly from client-supplied data.
    """
    if not isinstance(ctx, RequestContext):
        raise DomainError("INVALID_ARGUMENT", "invalid request context")

    for field_name, value in (
        ("operation_id", ctx.operation_id),
        ("trace_id", ctx.trace_id),
    ):
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > _MAX_CONTEXT_ID_LENGTH
        ):
            raise DomainError("INVALID_ARGUMENT", f"invalid {field_name}")

    if not _is_positive_int(ctx.realm_id):
        raise DomainError("INVALID_ARGUMENT", "invalid realm_id")

    if ctx.account_id is not None and not _is_positive_int(ctx.account_id):
        raise DomainError("INVALID_ARGUMENT", "invalid account_id")

    if ctx.character_id is not None and not _is_positive_int(ctx.character_id):
        raise DomainError("INVALID_ARGUMENT", "invalid character_id")

    if ctx.session_epoch is not None and not _is_positive_int(ctx.session_epoch):
        raise DomainError("INVALID_ARGUMENT", "invalid session_epoch")

    if ctx.character_id is not None and ctx.account_id is None:
        raise DomainError("INVALID_ARGUMENT", "character requires account identity")

    if ctx.session_epoch is not None and ctx.account_id is None:
        raise DomainError("INVALID_ARGUMENT", "session epoch requires account identity")

    if not isinstance(ctx.source, CommandSource):
        raise DomainError("INVALID_ARGUMENT", "invalid command source")

    if ctx.source is CommandSource.CLIENT:
        if ctx.account_id is None or ctx.session_epoch is None:
            raise DomainError("UNAUTHENTICATED", "authenticated session required")

    if require_character and ctx.character_id is None:
        raise DomainError("INVALID_STATE", "character context required")


def _is_positive_int(value: object) -> bool:
    """Return true for positive integers, explicitly excluding bool."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
