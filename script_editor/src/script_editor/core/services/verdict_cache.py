"""Content-addressed cache of past whole-package decode verdicts.

The pin table in :mod:`bundled_catalog` calls itself "a cache of past verdicts",
but until now nothing survived the process: every open of a package older than
that short list re-decoded all 5,001 entries, and opening the same package again
in a new session started from zero (about 5.5-6.5 s per open on the reference
machine).

What may be cached is deliberately narrow:

* **not** source, drafts, or anything that could be mistaken for a trusted
  source — only "these parameters decode this package" plus the embedded module
  paths that the very same pass produced (navigation metadata);
* keyed by **package SHA-256 + catalog SHA-256 + tool version + policy**, so a
  different package, a different parameter table, a changed exclusion policy or
  a newer decoder can never be served an older verdict;
* revalidated on load against the live archive (fingerprint, entry count, index
  bounds); anything unexpected discards the cache entry and re-scans.

A cache hit therefore reproduces exactly the verdict a fresh scan would produce
for the same inputs, and skips only recomputing it. It never raises on damaged
or hostile files: a broken cache is simply ignored.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from ..policy import POLICY_EXCLUDED

SCHEMA = 1
MAX_CACHED_ENTRIES = 100_000
MAX_CACHE_BYTES = 16 * 1024 * 1024


def _digest(value) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


def policy_fingerprint() -> str:
    """Identify the exclusion policy so a policy change invalidates verdicts."""
    body = "|".join(f"{vm}:{index}" for vm, index in sorted(POLICY_EXCLUDED))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def default_cache_root() -> Path:
    """Per-user cache directory; the tool never writes inside the game folder."""
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CACHE_HOME")
    if base:
        return Path(base) / "MXSJScriptEditor" / "verdicts"
    return Path.home() / ".cache" / "mxsj-script-editor" / "verdicts"


@dataclass(frozen=True)
class PackageVerdict:
    """One whole-package decode verdict, safe to persist by content digest."""

    archive_sha256: str
    catalog_sha256: str
    tool_version: str
    policy: str
    vm: str
    entries: int
    accepted: bool
    passed: int
    failures: tuple = ()
    paths: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)
    elapsed: float = 0.0

    def row(self) -> dict:
        return {
            "schema": SCHEMA,
            "archive_sha256": self.archive_sha256,
            "catalog_sha256": self.catalog_sha256,
            "tool_version": self.tool_version,
            "policy": self.policy,
            "vm": self.vm,
            "entries": self.entries,
            "accepted": self.accepted,
            "passed": self.passed,
            "failures": [[index, reason] for index, reason in self.failures],
            "paths": {str(index): name for index, name in sorted(self.paths.items())},
            "errors": {str(index): why for index, why in sorted(self.errors.items())},
            "elapsed": round(self.elapsed, 3),
        }

    def matches(self, archive, catalog_sha256: str) -> bool:
        """True only when this verdict was produced for these exact inputs."""
        return (
            _digest(self.archive_sha256)
            and self.archive_sha256 == archive.fingerprint()
            and _digest(catalog_sha256)
            and self.catalog_sha256 == catalog_sha256
            and self.policy == policy_fingerprint()
            and self.vm == archive.vm
            and self.entries == len(archive.entries)
        )

    def apply(self, archive) -> None:
        archive.module_paths = dict(self.paths)
        archive.module_path_errors = dict(self.errors)


def _parse_row(row, tool_version: str) -> PackageVerdict:
    if not isinstance(row, dict) or row.get("schema") != SCHEMA:
        raise ValueError("缓存格式不符")
    archive_sha, catalog_sha = row.get("archive_sha256"), row.get("catalog_sha256")
    if not _digest(archive_sha) or not _digest(catalog_sha):
        raise ValueError("缓存摘要非法")
    if row.get("tool_version") != tool_version:
        raise ValueError("缓存版本不符")
    policy = row.get("policy")
    if not isinstance(policy, str) or policy != policy_fingerprint():
        raise ValueError("缓存策略不符")
    vm, entries = row.get("vm"), row.get("entries")
    if vm not in {"py25", "py27"}:
        raise ValueError("缓存VM非法")
    if type(entries) is not int or not 0 < entries <= MAX_CACHED_ENTRIES:
        raise ValueError("缓存条目数非法")
    if type(row.get("passed")) is not int or not 0 <= row["passed"] <= entries:
        raise ValueError("缓存通过数非法")
    if type(row.get("accepted")) is not bool:
        raise ValueError("缓存判定非法")

    def index_map(value, limit):
        if not isinstance(value, dict) or len(value) > limit:
            raise ValueError("缓存索引表非法")
        result = {}
        for key, text in value.items():
            try:
                index = int(key)
            except (TypeError, ValueError):
                raise ValueError("缓存索引非法") from None
            if not 0 <= index < entries or not isinstance(text, str) or len(text) > 8192:
                raise ValueError("缓存索引/文本非法")
            result[index] = text
        return result

    paths = index_map(row.get("paths"), entries)
    errors = index_map(row.get("errors"), entries)
    failures = row.get("failures")
    if not isinstance(failures, list) or len(failures) > entries:
        raise ValueError("缓存失败列表非法")
    pairs = []
    for item in failures:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or type(item[0]) is not int
            or not 0 <= item[0] < entries
            or not isinstance(item[1], str)
            or len(item[1]) > 2048
        ):
            raise ValueError("缓存失败项非法")
        pairs.append((item[0], item[1]))
    elapsed = row.get("elapsed", 0.0)
    if type(elapsed) not in {int, float} or not 0 <= elapsed <= 3600:
        elapsed = 0.0
    return PackageVerdict(
        archive_sha256=archive_sha,
        catalog_sha256=catalog_sha,
        tool_version=tool_version,
        policy=policy,
        vm=vm,
        entries=entries,
        accepted=row["accepted"],
        passed=row["passed"],
        failures=tuple(pairs),
        paths=paths,
        errors=errors,
        elapsed=float(elapsed),
    )


class VerdictCache:
    """One JSON file per package digest under ``root``; never required to work."""

    def __init__(self, root: Path, tool_version: str):
        self.root = Path(root)
        self.tool_version = str(tool_version)

    def path_for(self, archive_sha256: str) -> Path:
        if not _digest(archive_sha256):
            raise ValueError("非法包摘要")
        return self.root / f"{archive_sha256}.json"

    def load(self, archive, catalog_sha256: str) -> PackageVerdict | None:
        """Return a verdict for exactly these inputs, or None. Never raises."""
        try:
            if not _digest(archive.fingerprint()):
                return None
            path = self.path_for(archive.fingerprint())
            if not path.is_file() or path.stat().st_size > MAX_CACHE_BYTES:
                return None
            with path.open("rb") as stream:
                raw = stream.read(MAX_CACHE_BYTES + 1)
            if len(raw) > MAX_CACHE_BYTES:
                return None
            verdict = _parse_row(json.loads(raw.decode("utf-8")), self.tool_version)
        except (OSError, ValueError, TypeError, AttributeError, RecursionError):
            return None
        if not verdict.matches(archive, catalog_sha256):
            return None
        try:
            archive._assert_unchanged()
        except ValueError:
            return None
        return verdict

    def store(self, archive, verdict: PackageVerdict) -> bool:
        """Persist atomically. Returns False instead of failing an open."""
        try:
            if verdict.archive_sha256 != archive.fingerprint():
                return False
            self.root.mkdir(parents=True, exist_ok=True)
            raw = json.dumps(
                verdict.row(), ensure_ascii=False, sort_keys=True, indent=1
            ).encode("utf-8")
            if len(raw) > MAX_CACHE_BYTES:
                return False
            fd, temporary = tempfile.mkstemp(prefix=".verdict-", dir=self.root)
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(raw)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temporary, self.path_for(verdict.archive_sha256))
            finally:
                Path(temporary).unlink(missing_ok=True)
        except OSError:
            return False
        return True

    def discard(self, archive) -> None:
        try:
            self.path_for(archive.fingerprint()).unlink(missing_ok=True)
        except (OSError, ValueError):
            pass
