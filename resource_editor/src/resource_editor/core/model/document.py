"""资源包文档模型：打开的包、条目状态、修改/撤销、增删。

文档只持有"存储字节"（容器层概念）。内容视图（GUI 预览/替换所见）
由容器类型决定：0SLF 的存储字节即内容；data.fls 的内容是其
raw-deflate 存储字节的解压结果。未改动条目的存储字节永不被改写，
重打包时逐字节原样输出。
"""
from __future__ import annotations

from pathlib import Path

from ..codecs import detect
from ..containers import KIND_FLSDATA, Archive, fls0slf, flsdata, open_archive


class PackDocument:
    """一个已打开的资源包及其全部条目的编辑状态。"""

    def __init__(self, archive: Archive, path: Path | None = None):
        self.archive = archive
        self.path = path
        self._payloads: list[bytes] = list(archive.payloads)
        self._original: list[bytes] = list(archive.payloads)
        self._history: list[list[bytes]] = [[] for _ in archive.payloads]

    # ---------------------------------------------------------- 打开 ----
    @classmethod
    def open(cls, path: str | Path) -> PackDocument:
        p = Path(path)
        return cls(open_archive(p.read_bytes()), path=p)

    @classmethod
    def from_bytes(cls, data: bytes) -> PackDocument:
        return cls(open_archive(data))

    # ---------------------------------------------------------- 查询 ----
    @property
    def count(self) -> int:
        return len(self._payloads)

    @property
    def kind(self) -> str:
        return self.archive.kind

    def stored(self, index: int) -> bytes:
        """条目当前的存储字节。"""
        return self._payloads[index]

    def content(self, index: int) -> bytes:
        """条目的内容视图字节（data.fls 为解压结果，余者同存储字节）。"""
        if self.archive.kind == KIND_FLSDATA:
            meta = self.archive.extra_metas[index]
            if meta.is_dir:
                return b""
            return flsdata.inflate(self._payloads[index])
        return self._payloads[index]

    def entry_kind(self, index: int) -> detect.EntryKind:
        return detect.sniff(self.content(index))

    def label(self, index: int) -> str:
        """条目显示名：data.fls 用文件名，0SLF 用序号。"""
        if self.archive.kind == KIND_FLSDATA:
            return self.archive.extra_metas[index].name
        return f"条目 {index}"

    def is_dirty(self, index: int) -> bool:
        return self._payloads[index] != self._original[index]

    @property
    def dirty_count(self) -> int:
        return sum(1 for i in range(self.count) if self.is_dirty(i))

    @property
    def is_modified(self) -> bool:
        return self.count != len(self._original) or self.dirty_count > 0

    # ---------------------------------------------------------- 修改 ----
    def _set_stored(self, index: int, stored: bytes) -> None:
        self._history[index].append(self._payloads[index])
        self._payloads[index] = stored

    def replace_content(self, index: int, content: bytes) -> None:
        """以内容视图字节替换条目（data.fls 自动重新压缩）。"""
        if self.archive.kind == KIND_FLSDATA:
            self._set_stored(index, flsdata.deflate(content))
        else:
            self._set_stored(index, content)

    def replace_stored(self, index: int, stored: bytes) -> None:
        """直接替换存储字节（高级用法，如整条目原始数据替换）。"""
        self._set_stored(index, stored)

    def revert(self, index: int) -> None:
        """把条目恢复到打开时的字节（记入撤销栈，可再撤销回来）。"""
        if self.is_dirty(index):
            self._set_stored(index, self._original[index])

    def undo(self, index: int) -> bool:
        """撤销该条目最近一次修改；无可撤销时返回 False。"""
        if not self._history[index]:
            return False
        self._payloads[index] = self._history[index].pop()
        return True

    def add_entry(self, content: bytes, name: str | None = None) -> int:
        """追加新条目，返回新条目序号。data.fls 必须提供 name。"""
        if self.archive.kind == KIND_FLSDATA:
            if not name:
                raise ValueError("data.fls 新增条目必须提供文件名")
            self.archive.extra_metas.append(flsdata.EntryMeta(name=name))
            self._payloads.append(flsdata.deflate(content))
        else:
            entry_id = len(self._payloads)
            self.archive.extra_metas.append(
                fls0slf.EntryMeta(entry_id=entry_id, r1=0)
            )
            self._payloads.append(content)
        self._original.append(self._payloads[-1])
        self._history.append([])
        return self.count - 1

    def delete_entry(self, index: int) -> None:
        del self.archive.extra_metas[index]
        del self._payloads[index]
        del self._original[index]
        del self._history[index]

    # ---------------------------------------------------------- 保存 ----
    def build_bytes(self) -> bytes:
        """构建整个包的新字节（不落盘）。"""
        return self.archive.build(list(self._payloads))

    def mark_saved(self, path: Path) -> None:
        """保存成功后同步基线（当前字节成为新的"原始"状态）。"""
        self.path = path
        self._original = list(self._payloads)
        self._history = [[] for _ in self._payloads]
