"""Explicit authorized catalog pins, never directory discovery or key guessing."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from ..project.storage import CatalogRef
from ..vm.py25.keys import read_catalog

# User explicitly authorized this one original-package catalog on 2026-10-15.
# A derived/new package must use its verified project association, not this map.
BUNDLED_CATALOGS = {
    "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72": (
        "script-original.json",
        "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
    ),
}


def checked_catalog(root: Path, name: str, digest: str) -> Path:
    path = root.resolve() / "decoding" / name
    if hashlib.sha256(read_catalog(path)).hexdigest() != digest:
        raise ValueError("内置解码参数SHA256不符，拒绝使用；请重新完整解压工具")
    return path


def bundled_catalog(archive, root: Path):
    if archive.vm != "py25":
        return None
    fingerprint = archive.fingerprint()
    spec = BUNDLED_CATALOGS.get(fingerprint)
    if spec is None:
        return None
    path = checked_catalog(root, *spec)
    return CatalogRef(archive.path, fingerprint, path, spec[1])


def audit_catalogs(root: Path):
    return [
        {"archive_sha256": archive_sha, "file": name, "sha256": digest}
        for archive_sha, (name, digest) in BUNDLED_CATALOGS.items()
        if checked_catalog(root, name, digest)
    ]


def stage_catalogs(root: Path, destination: Path):
    report = audit_catalogs(root)
    target = destination.resolve(strict=True) / "decoding"
    # An existing folder is always refused, including failed/partial old builds.
    target.mkdir()
    for row in report:
        shutil.copyfile(root / "decoding" / row["file"], target / row["file"])
    audit_catalogs(destination)
    return report
