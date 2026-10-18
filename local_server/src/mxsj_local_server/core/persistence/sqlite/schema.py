"""Versioned SQLite schema for the first local-runtime slice."""

from __future__ import annotations

import hashlib

APPLICATION_ID = 0x4D58534A
VERSION = 1
STATEMENTS = (
    """CREATE TABLE schema_migrations (
        version INTEGER PRIMARY KEY, checksum TEXT NOT NULL)""",
    """CREATE TABLE accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_key TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL)""",
    """CREATE TABLE sessions (
        account_id INTEGER NOT NULL REFERENCES accounts(account_id),
        realm_id INTEGER NOT NULL CHECK(realm_id > 0),
        epoch INTEGER NOT NULL CHECK(epoch > 0),
        ticket_hash TEXT UNIQUE,
        expires_at_ms INTEGER NOT NULL,
        PRIMARY KEY(account_id, realm_id))""",
    """CREATE TABLE characters (
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL REFERENCES accounts(account_id),
        realm_id INTEGER NOT NULL CHECK(realm_id > 0),
        name TEXT NOT NULL, name_key TEXT NOT NULL,
        appearance INTEGER NOT NULL CHECK(appearance > 0),
        school_id INTEGER NOT NULL CHECK(school_id > 0),
        level INTEGER NOT NULL CHECK(level > 0),
        revision INTEGER NOT NULL CHECK(revision > 0),
        UNIQUE(realm_id, name_key))""",
    "CREATE INDEX characters_owner ON characters(account_id, realm_id)",
    """CREATE TABLE operations (
        account_id INTEGER NOT NULL REFERENCES accounts(account_id),
        realm_id INTEGER NOT NULL CHECK(realm_id > 0),
        operation_id TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response TEXT NOT NULL,
        PRIMARY KEY(account_id, realm_id, operation_id))""",
)
CHECKSUM = hashlib.sha256("\n".join(STATEMENTS).encode("utf-8")).hexdigest()
