"""Bind an external catalog to exact package and stored-entry digests.

No directory discovery or boundary estimation. Catalog is factual decode data
(not an account credential); callers supply both digest pins, including the
bundled catalog selected by an exact original/registered-test-package SHA.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from ...archives.document import ArchiveDocument
from ..compression import inflate


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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

    def validate(self, archive: ArchiveDocument, index: int):
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

    def crypt(self, data: bytes) -> bytes:
        if len(data) != self.expanded_size:
            raise ValueError("XOR payload length changed; boundary rescaling forbidden")
        points = (0, *self.bounds, len(data))
        return b"".join(
            data[points[i] : points[i + 1]].translate(
                bytes(n ^ self.keys[i] for n in range(256))
            )
            for i in range(5)
        )


def read_catalog(path: Path) -> bytes:
    # Bounded even if the file grows; do not allocate a whole untrusted catalog.
    with path.open("rb") as stream:
        raw = stream.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError("XOR catalog exceeds 16MiB safety limit")
    return raw


def load_profile(
    archive: ArchiveDocument,
    index: int,
    catalog: Path,
    *,
    archive_sha256: str,
    catalog_sha256: str,
) -> KeyProfile:
    if (
        archive.kind != "0slf"
        or type(index) is not int
        or not 0 <= index < len(archive.entries)
    ):
        raise ValueError("not a script container entry")
    if archive.fingerprint() != archive_sha256:
        raise ValueError("source package digest pin mismatch")
    raw = read_catalog(catalog)
    if len(raw) > 16 * 1024 * 1024 or sha(raw) != catalog_sha256:
        raise ValueError("XOR catalog digest pin mismatch")
    info = json.loads(raw.decode("utf-8-sig"))[str(index)]
    stored = archive.read_stored(index)
    profile = KeyProfile(
        archive_sha256,
        index,
        archive.entries[index].identity,
        sha(stored),
        catalog_sha256,
        tuple(info["keys"]),
        tuple(info["bounds"]),
        len(inflate(stored)),
    )
    profile.validate(archive, index)
    return profile
