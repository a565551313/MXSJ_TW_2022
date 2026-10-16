-- SQLite development-prototype schema for the registration-to-map loop.
-- This is not the production PostgreSQL migration chain.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS realms (
    realm_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('online', 'maintenance', 'offline'))
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL UNIQUE,
    password_salt BLOB NOT NULL,
    password_hash BLOB NOT NULL,
    disabled INTEGER NOT NULL DEFAULT 0 CHECK (disabled IN (0, 1)),
    created_at_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS map_templates (
    map_template_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    spawn_x INTEGER NOT NULL,
    spawn_y INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    realm_id INTEGER NOT NULL REFERENCES realms(realm_id),
    account_id INTEGER NOT NULL REFERENCES accounts(account_id),
    name TEXT NOT NULL,
    appearance_template_id INTEGER NOT NULL,
    school_id INTEGER NOT NULL,
    level INTEGER NOT NULL CHECK (level >= 1),
    revision INTEGER NOT NULL CHECK (revision >= 1),
    created_at_ms INTEGER NOT NULL,
    UNIQUE (realm_id, account_id, name)
);

CREATE TABLE IF NOT EXISTS account_sessions (
    realm_id INTEGER NOT NULL REFERENCES realms(realm_id),
    account_id INTEGER NOT NULL REFERENCES accounts(account_id),
    ticket_hash BLOB NOT NULL UNIQUE,
    session_epoch INTEGER NOT NULL CHECK (session_epoch >= 1),
    expires_at_ms INTEGER NOT NULL,
    selected_character_id INTEGER REFERENCES characters(character_id),
    updated_at_ms INTEGER NOT NULL,
    PRIMARY KEY (realm_id, account_id)
);

CREATE TABLE IF NOT EXISTS idempotency_records (
    realm_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    operation_id TEXT NOT NULL,
    request_fingerprint BLOB NOT NULL,
    result_character_id INTEGER NOT NULL REFERENCES characters(character_id),
    created_at_ms INTEGER NOT NULL,
    PRIMARY KEY (realm_id, account_id, operation_id),
    FOREIGN KEY (realm_id) REFERENCES realms(realm_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE IF NOT EXISTS map_instances (
    map_instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    realm_id INTEGER NOT NULL REFERENCES realms(realm_id),
    map_template_id INTEGER NOT NULL REFERENCES map_templates(map_template_id),
    created_at_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS character_positions (
    character_id INTEGER PRIMARY KEY REFERENCES characters(character_id),
    map_instance_id INTEGER NOT NULL REFERENCES map_instances(map_instance_id),
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    revision INTEGER NOT NULL CHECK (revision >= 1),
    updated_at_ms INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_characters_account ON characters(realm_id, account_id);
CREATE INDEX IF NOT EXISTS idx_map_instances_realm ON map_instances(realm_id, map_instance_id);
