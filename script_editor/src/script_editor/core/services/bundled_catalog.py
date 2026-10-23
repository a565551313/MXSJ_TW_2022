"""Authorized catalog asset, plus pins for packages we have already seen.

Two different things live here on purpose:

* ``ORIGINAL_CATALOG`` -- the single authorized parameter asset (file name and
  SHA256). It is the only key material the tool ships.
* ``BUNDLED_CATALOGS`` -- whole-package fingerprints we have already verified
  against that asset. It is a cache of past verdicts, not the permission: an
  unlisted package is verified entry by entry in
  :mod:`script_editor.core.services.package_selfcheck` and adopted when its
  parameters demonstrably decode it.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from ..errors import ResourceEditorError
from ..project.storage import CatalogRef
from ..vm.py25.keys import read_catalog
from .package_selfcheck import verify_with_catalog

# The one authorized parameter asset. Keys and boundaries come from here; no
# API in this tool derives them from the package under inspection.
ORIGINAL_CATALOG = (
    "script-original.json",
    "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
)

# Exact original/authorized derivative pins: whole-package fingerprints that
# have already been decoded successfully with ORIGINAL_CATALOG. The 4bf1
# package is the direct-bytecode package the user confirmed opens/lists/loads
# on 2026-10-17. Being listed is only a shortcut -- an unlisted package is
# verified entry by entry (package_selfcheck) and adopted when the parameters
# demonstrably decode it. No filename, directory or partial-entry inference.
_PINNED_PACKAGES = (
    "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678",
    "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72",
    "c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1",
    # 2026-10-23 註冊腳本改版（build=2027-10-22d）：只換了條目 4007（register）
    # 與 337（mainpage 的 9 字節定寬補丁），其餘 5000 條負載與原包逐字節一致。
    "a45e0e49ed336367a1bf00b5377229c5c48de2c30ac2b61f9bf7d67549a445b9",
)

BUNDLED_CATALOGS = {digest: ORIGINAL_CATALOG for digest in _PINNED_PACKAGES}


def builtin_catalog(root: Path) -> Path:
    """The shipped parameter asset, digest-checked. Not tied to a package."""
    return checked_catalog(root, *ORIGINAL_CATALOG)


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


def resolve_catalog(archive, root: Path):
    """Decide the decode parameters for a package that is being opened.

    Returns ``(ref, warning, check)``:

    * ``ref``     -- the catalog to attach, or None when nothing was adopted
    * ``warning`` -- why the shipped asset itself is unusable (empty otherwise)
    * ``check``   -- the whole-package verdict when the package was not pinned

    A pinned package keeps the old fast path (no scan here; the caller indexes
    names). An unlisted package is decoded entry by entry and adopted on that
    evidence, which is what makes future rebuilds open without re-registering.
    """
    try:
        ref = bundled_catalog(archive, root)
    except (OSError, ValueError, ResourceEditorError) as exc:
        return None, str(exc), None
    if ref is not None or archive.vm != "py25":
        return ref, "", None
    try:
        check = verify_with_catalog(archive, builtin_catalog(root))
    except (OSError, ValueError, ResourceEditorError) as exc:
        return None, str(exc), None
    if check.accepted:
        check.apply(archive)
        return check.ref, "", check
    return None, "", check


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
    copied = set()
    for row in report:
        # Several exact package fingerprints may refer to the same pinned asset.
        if row["file"] not in copied:
            shutil.copyfile(root / "decoding" / row["file"], target / row["file"])
            copied.add(row["file"])
    audit_catalogs(destination)
    return report
