"""Portable project descriptors; source associations require an exact package."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..services.files import atomic_write


@dataclass(frozen=True)
class Binding:
    archive: Path
    fingerprint: str
    vm: str
    index: int
    identity: str
    source: Path

    @classmethod
    def associate(cls, archive: ArchiveDocument, index: int, source: Path):
        if not 0 <= index < len(archive.entries):
            raise IndexError(index)
        entry = archive.entries[index]
        if entry.directory:
            raise ValueError("目录条目不能关联源码")
        return cls(
            archive.path,
            archive.fingerprint(),
            archive.vm,
            index,
            entry.identity,
            source.resolve(strict=True),
        )

    def verify(self, archive: ArchiveDocument):
        if (
            archive.path != self.archive.resolve()
            or archive.vm != self.vm
            or archive.fingerprint() != self.fingerprint
            or not 0 <= self.index < len(archive.entries)
            or archive.entries[self.index].identity != self.identity
            or archive.entries[self.index].directory
        ):
            raise ValueError("项目与当前包指纹/模块身份不符，拒绝套用源码关联")


def save_project(path: Path, bindings: list[Binding]):
    if not path.name.endswith(".mxscript.json"):
        raise ValueError("项目文件必须为.mxscript.json")
    rows = []
    for item in bindings:
        rows.append(
            {
                "archive": os.path.relpath(item.archive, path.parent),
                "source": os.path.relpath(item.source, path.parent),
                "fingerprint": item.fingerprint,
                "vm": item.vm,
                "index": item.index,
                "identity": item.identity,
                "status": "user-associated-not-native-verified",
            }
        )
    data = json.dumps(
        {"schema": 1, "bindings": rows}, ensure_ascii=False, indent=2
    ).encode("utf-8")
    atomic_write(path, data, [p for b in bindings for p in (b.archive, b.source)])


def load_project(path: Path) -> list[Binding]:
    doc = json.loads(path.read_text(encoding="utf-8-sig"))
    if doc.get("schema") != 1 or not isinstance(doc.get("bindings"), list):
        raise ValueError("不支持的项目格式")
    result = []
    seen = set()
    for row in doc["bindings"]:
        if row["vm"] not in {"py25", "py27"} or type(row["index"]) is not int:
            raise ValueError("非法VM/条目下标")
        archive = (path.parent / row["archive"]).resolve(strict=True)
        source = (path.parent / row["source"]).resolve(strict=True)
        binding = Binding(
            archive,
            row["fingerprint"],
            row["vm"],
            row["index"],
            row["identity"],
            source,
        )
        key = (archive, binding.index)
        if key in seen:
            raise ValueError("项目中模块关联重复")
        seen.add(key)
        with ArchiveDocument(archive) as document:
            binding.verify(document)
        result.append(binding)
    return result
