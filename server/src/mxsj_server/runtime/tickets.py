"""Opaque session ticket parsing; do not log the input."""

from __future__ import annotations

import hashlib
import re

from mxsj_server.contracts.common import DomainError


def ticket_digest(ticket: str) -> str:
    if not isinstance(ticket, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", ticket):
        raise DomainError("UNAUTHENTICATED")
    return hashlib.sha256(ticket.encode("ascii")).hexdigest()
