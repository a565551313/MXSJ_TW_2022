"""Bind an external catalog to exact package and stored-entry digests.

No directory discovery or boundary estimation. Catalog keys are evidence,
not cipher boundaries: calibrate using native arithmetic. Incomplete research
rows additionally require a matching native name seed and directory hash.
Callers still supply both digest pins for the exact package and catalog.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path

from ...archives.document import ArchiveDocument
from ...policy import require_module_allowed
from ..compression import inflate
from .cipher import bounds_from_keys, resolve_parameters, xor_segments


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inflate_script(archive: ArchiveDocument, index: int) -> bytes:
    """Strict zlib, except the exact user-accepted fixed-slot probe's 10 zeros.

    This is a whole-package SHA pin plus entry index, not a general permission
    for trailing data. Every other package/entry retains strict EOF checking.
    """
    require_module_allowed(archive.vm, index)
    stored = archive.read_stored(index)
    if (
        archive.fingerprint()
        == "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678"
        and index == 918
    ):
        if not stored.endswith(bytes(10)):
            raise ValueError("accepted direct-package slot padding differs")
        stored = stored[:-10]
    return inflate(stored)


@dataclass(frozen=True)
class KeyProfile:
    archive_sha256: str
    index: int
    identity: str
    stored_sha256: str
    catalog_sha256: str
    keys: tuple[int, ...]
    bounds: tuple[int, ...]
    expanded_size: int

    def calibrated(self, archive: ArchiveDocument):
        # Never modify the pinned research catalog or trust parse-only seams.
        self._validate_catalog(archive, self.index)
        try:
            calibrated = replace(
                self, bounds=bounds_from_keys(self.keys, self.expanded_size)
            )
        except ValueError:
            data = inflate_script(archive, self.index)
            if len(data) != self.expanded_size:
                raise ValueError("XOR profile expanded length mismatch") from None
            keys, bounds = resolve_parameters(
                data, self.keys, self.bounds, int(self.identity, 16)
            )
            calibrated = replace(self, keys=keys, bounds=bounds)
        calibrated.validate(archive, self.index)
        return calibrated

    def _validate_catalog(self, archive: ArchiveDocument, index: int):
        require_module_allowed(archive.vm, index)
        if (
            archive.kind != "0slf"
            or index != self.index
            or archive.fingerprint() != self.archive_sha256
            or archive.entries[index].identity != self.identity
            or sha(archive.read_stored(index)) != self.stored_sha256
        ):
            raise ValueError("XOR profile does not match exact source package/entry")
        if (
            len(self.keys) != 5
            or len(self.bounds) != 4
            or any(type(k) is not int or not 0 <= k <= 255 for k in self.keys)
            or any(type(b) is not int for b in self.bounds)
            or list(self.bounds) != sorted(self.bounds)
            or not 0 <= self.bounds[0] <= self.bounds[-1] <= self.expanded_size
        ):
            raise ValueError("invalid five-segment XOR profile")

    def validate(self, archive: ArchiveDocument, index: int):
        self._validate_catalog(archive, index)
        try:
            expected = self.keys, bounds_from_keys(self.keys, self.expanded_size)
        except ValueError:
            data = inflate_script(archive, index)
            if len(data) != self.expanded_size:
                raise ValueError("XOR profile expanded length mismatch") from None
            expected = resolve_parameters(
                data, self.keys, self.bounds, int(self.identity, 16)
            )
        if (self.keys, self.bounds) != expected:
            raise ValueError("XOR parameters differ from native cipher arithmetic")

    def crypt(self, data: bytes) -> bytes:
        if len(data) != self.expanded_size:
            raise ValueError("XOR payload length changed; boundary rescaling forbidden")
        return xor_segments(data, self.keys, self.bounds)


def read_catalog(path: Path) -> bytes:
    # Bounded even if the file grows; do not allocate a whole untrusted catalog.
    with path.open("rb") as stream:
        raw = stream.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError("XOR catalog exceeds 16MiB safety limit")
    return raw


#: Parsed catalogs by (path, size, mtime_ns, inode). Purely an in-memory cache
#: of a derived value: the file is still read through :func:`read_catalog` on a
#: miss and the digest returned to callers is recomputed from those exact bytes
#: on every call, so a changed file can never be served as an older verdict.
_CATALOG_CACHE: dict[tuple, tuple[bytes, dict]] = {}
_CATALOG_CACHE_LIMIT = 4


def clear_catalog_cache() -> None:
    """Drop memoised catalogs (tests and explicit re-reads)."""
    _CATALOG_CACHE.clear()


def catalog_snapshot(path: Path) -> tuple[dict, str]:
    """Return ``(rows, sha256)`` for a catalog without re-parsing it per entry.

    A whole-package scan used to re-read and re-parse the 426 KB authorized
    table once per entry (about 5 ms each, ~25 s over 5,001 entries). The rows
    are immutable evidence: nothing here may be edited, and a missing or
    malformed table still raises.
    """
    resolved = Path(path)
    try:
        info = os.stat(resolved)
        key = (str(resolved), info.st_size, info.st_mtime_ns, info.st_ino)
    except OSError:
        key = None
    cached = _CATALOG_CACHE.get(key) if key is not None else None
    if cached is None:
        raw = read_catalog(resolved)
        rows = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(rows, dict):
            raise ValueError("XOR catalog is not a JSON object")
        if key is not None:
            if len(_CATALOG_CACHE) >= _CATALOG_CACHE_LIMIT:
                _CATALOG_CACHE.clear()
            _CATALOG_CACHE[key] = (raw, rows)
    else:
        raw, rows = cached
    return rows, sha(raw)


def load_profile(
    archive: ArchiveDocument,
    index: int,
    catalog: Path,
    *,
    archive_sha256: str,
    catalog_sha256: str,
) -> KeyProfile:
    require_module_allowed(archive.vm, index)
    if (
        archive.kind != "0slf"
        or type(index) is not int
        or not 0 <= index < len(archive.entries)
    ):
        raise ValueError("not a script container entry")
    if archive.fingerprint() != archive_sha256:
        raise ValueError("source package digest pin mismatch")
    rows, digest = catalog_snapshot(catalog)
    if digest != catalog_sha256:
        raise ValueError("XOR catalog digest pin mismatch")
    info = rows[str(index)]
    stored = archive.read_stored(index)
    profile = KeyProfile(
        archive_sha256,
        index,
        archive.entries[index].identity,
        sha(stored),
        catalog_sha256,
        tuple(info["keys"]),
        tuple(info["bounds"]),
        len(inflate_script(archive, index)),
    )
    profile = profile.calibrated(archive)
    profile.validate(archive, index)
    return profile
