"""Explicit authorized catalog pins, never directory discovery or key guessing."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from ..project.storage import CatalogRef
from ..vm.py25.keys import read_catalog

# Exact original/authorized derivative pins only. The 4bf1 package is the
# direct-bytecode package the user confirmed opens/lists/loads on 2026-10-17.
# Catalog associations authorize native parameter calibration, not source trust
# or engine acceptance of future recompiled packages. Unknown packages stay off.
BUNDLED_CATALOGS = {
    "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678": (
        "script-original.json",
        "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
    ),
    "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72": (
        "script-original.json",
        "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
    ),
    "c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1": (
        "script-original.json",
        "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
    ),
    # 2026-10-23 註冊腳本改版（build=2027-10-22d）打包出的派生包：只換了
    # 條目 4007（register）與 337（mainpage 的 9 字節定寬補丁），其餘 5000 條
    # 負載與原包逐字節一致，因此同一份已授權參數表適用。派生包按完整包
    # 指紋登記，仍然不按檔名/目錄/部分條目推定。
    "a45e0e49ed336367a1bf00b5377229c5c48de2c30ac2b61f9bf7d67549a445b9": (
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
    copied = set()
    for row in report:
        # Several exact package fingerprints may refer to the same pinned asset.
        if row["file"] not in copied:
            shutil.copyfile(root / "decoding" / row["file"], target / row["file"])
            copied.add(row["file"])
    audit_catalogs(destination)
    return report
