"""Redaction helpers for probe reports and logs.

Per docs/SECURITY.md §6 the system must never return real account, password,
ticket, key, private-key material, full chat content, real email or machine
sensitive identifiers. This module provides a structural redactor that walks a
JSON-like structure and masks values tied to sensitive keys or patterns.
"""

from __future__ import annotations

import re
from typing import Any

# Key name substrings (lowercased) that always mark a sensitive field.
SENSITIVE_KEY_SUBSTRINGS = (
    "password",
    "passwd",
    "pwd",
    "ticket",
    "token",
    "secret",
    "credential",
    "cookie",
    "account",
    "email",
    "mail",
    "private_key",
    "apikey",
)

REDACTED = "[REDACTED]"
REDACTED_EMAIL = "[REDACTED_EMAIL]"

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Long hex/base64 blobs are likely key/token material when found in values.
_SECRET_RE = re.compile(r"^[A-Za-z0-9+/=_\-]{40,}$")


def _is_sensitive_key(key: str) -> bool:
    lowered = re.sub(r"[^a-z0-9]", "", key.lower())
    return any(sub.replace("_", "") in lowered for sub in SENSITIVE_KEY_SUBSTRINGS)


def _redact_string(value: str) -> str:
    if _EMAIL_RE.search(value):
        return _EMAIL_RE.sub(REDACTED_EMAIL, value)
    if _SECRET_RE.match(value):
        return REDACTED
    return value


def redact(value: Any) -> Any:
    """Recursively redact a JSON-like structure in place-safe manner.

    Returns a new structure; the original is not mutated. Sensitive keys are
    replaced by ``[REDACTED]``; string values matching email or long secret
    patterns are masked.
    """
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(str(key)):
                out[key] = REDACTED
            elif (key in {"baseline_sha256", "script_fls_sha256"}
                  and isinstance(item, str)
                  and re.fullmatch(r"[0-9a-fA-F]{64}", item)):
                out[key] = item
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def redact_report(data: Any) -> Any:
    """Alias for :func:`redact` with a domain-specific name."""
    return redact(data)
