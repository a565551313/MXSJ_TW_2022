"""Single administrator, salted scrypt credentials, expiring in-memory sessions."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time


def password_hash(password):
    if not isinstance(password, str) or not 12 <= len(password) <= 256:
        raise ValueError("管理员密码需要 12..256 个字符")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    return salt.hex() + ":" + digest.hex()


def verify(password, encoded):
    if not isinstance(password, str) or not 0 < len(password) <= 256 or not encoded:
        return False
    salt, expected = encoded.split(":")
    actual = hashlib.scrypt(
        password.encode("utf-8"), salt=bytes.fromhex(salt), n=16384, r=8, p=1
    )
    return hmac.compare_digest(actual.hex(), expected)


class Sessions:
    def __init__(self):
        self.entries = {}

    def create(self):
        now = time.monotonic()
        self.entries = {k: v for k, v in self.entries.items() if v["expires"] > now}
        if len(self.entries) >= 32:
            raise ValueError("管理会话数量已达上限")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        self.entries[self.key(token)] = {"csrf": csrf, "expires": now + 1800}
        return token, csrf

    @staticmethod
    def key(token):
        return hashlib.sha256(token.encode("ascii", errors="replace")).hexdigest()

    def get(self, token):
        session = self.entries.get(self.key(token))
        if session and session["expires"] > time.monotonic():
            return session
        self.entries.pop(self.key(token), None)
        return None

    def revoke(self, token):
        self.entries.pop(self.key(token), None)

    def clear(self):
        self.entries.clear()
