"""Local configuration parsing; never reads formal-server configuration."""

from __future__ import annotations

import json
from pathlib import Path

from mxsj_local_server.core.modules.character.domain.creation import CreationPolicy


def read_config(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if set(raw) - {"logging"} != {"database", "realm_id", "session_ttl_ms", "creation"}:
        raise ValueError("Unknown or missing configuration keys")
    creation = raw["creation"]
    if set(creation) != {"max_characters", "allowed_pairs"}:
        raise ValueError("Unknown creation policy keys")
    if not isinstance(raw["database"], str) or not raw["database"]:
        raise ValueError("Invalid database path")
    if type(raw["realm_id"]) is not int or not 1 <= raw["realm_id"] <= 65535:
        raise ValueError("Invalid realm_id")
    if (
        type(raw["session_ttl_ms"]) is not int
        or not 60_000 <= raw["session_ttl_ms"] <= 86_400_000
    ):
        raise ValueError("Invalid session_ttl_ms")
    policy = CreationPolicy(
        frozenset(tuple(pair) for pair in creation["allowed_pairs"]),
        creation["max_characters"],
    )
    db = Path(raw["database"])
    if not db.is_absolute():
        db = path.absolute().parent / db
    logs = raw.get("logging", {})
    if not isinstance(logs, dict) or set(logs) - {
        "directory",
        "max_bytes",
        "backups",
        "level",
    }:
        raise ValueError("Invalid logging keys")
    directory = logs.get("directory", "var/logs")
    if not isinstance(directory, str) or not directory:
        raise ValueError("Invalid log directory")
    directory = Path(directory)
    if not directory.is_absolute():
        directory = path.absolute().parent / directory
    log_options = {
        "directory": directory,
        "max_bytes": logs.get("max_bytes", 5_242_880),
        "backups": logs.get("backups", 5),
        "level": logs.get("level", "INFO"),
    }
    return db, raw["realm_id"], raw["session_ttl_ms"], policy, log_options
