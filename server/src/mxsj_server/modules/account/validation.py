"""Validation for the pre-authentication account request boundary.

This module validates input shape only. Credential verification, password hashing,
rate limiting, protocol allow-listing, ticket issuance, and persistence are separate
responsibilities and are not implemented here.
"""
from __future__ import annotations

from mxsj_server.contracts.common import DomainError
from mxsj_server.modules.account.contracts import LoginRequest

_MAX_ACCOUNT_NAME_LENGTH = 128
_MAX_CREDENTIAL_BYTES = 4096
_MAX_PROTOCOL_VERSION_LENGTH = 64


def validate_login_request(request: LoginRequest) -> None:
    """Reject malformed login requests before expensive authentication work."""
    if not isinstance(request, LoginRequest):
        raise DomainError("INVALID_ARGUMENT", "invalid login request")

    if (
        not isinstance(request.account_name, str)
        or not request.account_name.strip()
        or len(request.account_name) > _MAX_ACCOUNT_NAME_LENGTH
        or _contains_control_characters(request.account_name)
    ):
        raise DomainError("INVALID_ARGUMENT", "invalid account name")

    if (
        not isinstance(request.credential, bytes)
        or not request.credential
        or len(request.credential) > _MAX_CREDENTIAL_BYTES
    ):
        raise DomainError("INVALID_ARGUMENT", "invalid credential payload")

    if (
        not isinstance(request.protocol_version, str)
        or not request.protocol_version.strip()
        or len(request.protocol_version) > _MAX_PROTOCOL_VERSION_LENGTH
        or _contains_control_characters(request.protocol_version)
    ):
        raise DomainError("INVALID_ARGUMENT", "invalid protocol version")


def _contains_control_characters(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)
