"""Schema2 project metadata, no compiler paths, keys or copied source contents."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..services.files import atomic_write, read_source
from ..vm.py25.keys import read_catalog
from .document import Binding


@dataclass(frozen=True)
class CatalogRef:
    archive: Path
    fingerprint: str
    path: Path
    sha256: str

    def verify(self, archive):
        if (
            archive.path != self.archive.resolve()
            or archive.fingerprint() != self.fingerprint
        ):
            raise ValueError("XOR目录的包来源已过期")
        if hashlib.sha256(read_catalog(self.path)).hexdigest() != self.sha256:
            raise ValueError("XOR目录文件发生变化，须重新确认来源")


@dataclass(frozen=True)
class ProjectState:
    bindings: tuple[Binding, ...]
    catalogs: tuple[CatalogRef, ...] = ()


def _digest(value):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise ValueError("非法SHA256")


def save_state(path: Path, bindings, catalogs=()):
    bindings, catalogs = tuple(bindings), tuple(catalogs)
    if not path.name.endswith(".mxscript.json"):
        raise ValueError("项目文件必须为.mxscript.json")

    def portable(target):
        try:
            return os.path.relpath(target, path.parent)
        except ValueError:  # Different Windows volumes cannot have a relative path.
            return str(target.resolve())

    rows, refs = [], []
    for binding in bindings:
        row = asdict(binding)
        row["archive"] = portable(binding.archive)
        row["source"] = portable(binding.source)
        row["status"] = "user-associated-not-native-verified"
        rows.append(row)
    for catalog in catalogs:
        row = asdict(catalog)
        row["archive"] = portable(catalog.archive)
        row["path"] = portable(catalog.path)
        refs.append(row)
    protected = [p for b in bindings for p in (b.archive, b.source)]
    protected += [p for c in catalogs for p in (c.archive, c.path)]
    atomic_write(
        path,
        json.dumps(
            {"schema": 2, "bindings": rows, "catalogs": refs},
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        protected,
    )


def load_state(path: Path) -> ProjectState:
    doc = json.loads(path.read_text(encoding="utf-8-sig"))
    if doc.get("schema") not in (1, 2) or not isinstance(doc.get("bindings"), list):
        raise ValueError("不支持的项目格式")
    bindings, catalogs, archives, seen = [], [], {}, set()

    def archive(name):
        target = (path.parent / name).resolve(strict=True)
        if target not in archives:
            archives[target] = ArchiveDocument(target)
        return archives[target]

    try:
        for row in doc["bindings"]:
            source = (path.parent / row["source"]).resolve(strict=True)
            read_source(source)  # Preflight ALL files before GUI adoption.
            a = archive(row["archive"])
            if row["vm"] not in {"py25", "py27"} or type(row["index"]) is not int:
                raise ValueError("非法VM/条目下标")
            _digest(row["fingerprint"])
            filename, baseline = (
                row.get("filename_hex", ""),
                row.get("built_source_sha256", ""),
            )
            if not isinstance(filename, str) or len(filename) > 16384:
                raise ValueError("非法嵌入文件名")
            bytes.fromhex(filename)
            if baseline:
                _digest(baseline)
            binding = Binding(
                a.path,
                row["fingerprint"],
                row["vm"],
                row["index"],
                row["identity"],
                source,
                filename,
                baseline,
            )
            binding.verify(a)
            key = (a.path, binding.index)
            if key in seen:
                raise ValueError("项目中模块关联重复")
            seen.add(key)
            bindings.append(binding)
        seen.clear()
        for row in doc.get("catalogs", []):
            a = archive(row["archive"])
            _digest(row["fingerprint"])
            _digest(row["sha256"])
            ref = CatalogRef(
                a.path,
                row["fingerprint"],
                (path.parent / row["path"]).resolve(strict=True),
                row["sha256"],
            )
            if a.vm != "py25" or a.path in seen:
                raise ValueError("非法或重复XOR目录关联")
            ref.verify(a)
            seen.add(a.path)
            catalogs.append(ref)
        return ProjectState(tuple(bindings), tuple(catalogs))
    finally:
        for a in archives.values():
            a.close()
