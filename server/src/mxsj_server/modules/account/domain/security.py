"""Credential rules; no database, network or client-module imports."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets

from mxsj_server.contracts.common import DomainError

SCRYPT_N = 16384
SCRYPT_R = 8
SCRYPT_P = 1


def account_key(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9_]{2,31}", name
    ):
        raise DomainError(
            "INVALID_ARGUMENT", "Account name must be 3-32 ASCII characters"
        )
    return name.lower()


def password_bytes(value: bytes) -> bytes:
    if not isinstance(value, bytes) or not 12 <= len(value) <= 128:
        raise DomainError("INVALID_ARGUMENT", "Password must be 12-128 UTF-8 bytes")
    try:
        text = value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise DomainError("INVALID_ARGUMENT", "Password must be UTF-8") from exc
    if any(ord(c) < 32 or ord(c) == 127 for c in text):
        raise DomainError("INVALID_ARGUMENT", "Password contains control characters")
    return value


def derive(value: bytes, salt: bytes) -> bytes:
    return hashlib.scrypt(
        value, salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32
    )


def encode_password(value: bytes) -> str:
    salt = secrets.token_bytes(16)
    return f"scrypt-v1${salt.hex()}${derive(password_bytes(value), salt).hex()}"


def verify_password(value: bytes, encoded: str) -> bool:
    try:
        version, salt_hex, expected_hex = encoded.split("$")
        salt, expected = bytes.fromhex(salt_hex), bytes.fromhex(expected_hex)
        if version != "scrypt-v1" or len(salt) != 16 or len(expected) != 32:
            raise ValueError("invalid credential record")
    except (ValueError, AttributeError) as exc:
        # Corrupt credentials must never fall back to accepting a password.
        raise DomainError("STORAGE_ERROR", "Invalid credential record") from exc
    return hmac.compare_digest(derive(value, salt), expected)
