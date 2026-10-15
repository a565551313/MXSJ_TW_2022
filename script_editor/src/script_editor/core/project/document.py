"""Portable project descriptors; source associations require an exact package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument


@dataclass(frozen=True)
class Binding:
    archive: Path
    fingerprint: str
    vm: str
    index: int
    identity: str
    source: Path
    filename_hex: str = ""
    built_source_sha256: str = ""
    source_kind: str = "authored"
    recovery_sha256: str = ""

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
        if self.source_kind not in {"authored", "recovered-reviewed"}:
            raise ValueError("未核验恢复稿/参考稿不能作为可发布源码关联")
        if self.source_kind == "recovered-reviewed" and (
            len(self.recovery_sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.recovery_sha256)
        ):
            raise ValueError("恢复源码缺少原标准字节码来源摘要")
        if (
            archive.path != self.archive.resolve()
            or archive.vm != self.vm
            or archive.fingerprint() != self.fingerprint
            or not 0 <= self.index < len(archive.entries)
            or archive.entries[self.index].identity != self.identity
            or archive.entries[self.index].directory
        ):
            raise ValueError("项目与当前包指纹/模块身份不符，拒绝套用源码关联")


def save_project(path: Path, bindings: list[Binding], catalogs=()):
    from .storage import save_state

    save_state(path, bindings, catalogs)


def load_project(path: Path) -> list[Binding]:
    from .storage import load_state

    return list(load_state(path).bindings)
