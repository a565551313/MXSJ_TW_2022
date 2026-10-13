"""资源包文档模型：打开的包、条目状态、修改/撤销、增删。

打开是惰性的：文档只持有容器索引与"改动覆盖层"。每条目一个槽位
（:class:`_Slot`）：``origin`` 是它在原包中的序号（None 表示新增），
``stored`` 是改动后的存储字节（None 表示未改动、按需从源文件读）。
因此打开多大的包都只占条目数级别的内存，保存时未改动条目由容器层
从源文件流式拷贝。文档只持有"存储字节"（容器层概念）；内容视图
（GUI 预览/替换所见）由容器类型决定：0SLF 的存储字节即内容；
data.fls 的内容是其 raw-deflate 存储字节的解压结果。
"""
from __future__ import annotations

import io
import zlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

from ..codecs import detect
from ..containers import (
    KIND_FLSDATA,
    Archive,
    fls0slf,
    flsdata,
    open_archive,
    open_archive_path,
)


@dataclass
class _Slot:
    """一条目在打开后会话中的状态。"""

    origin: int | None                 # 原包序号；None=新增条目
    stored: bytes | None = None        # 改动后的存储字节；None=用原始
    dirty: bool = False                # 当前字节是否与原始不同
    history: list[tuple[bytes | None, bool]] = field(default_factory=list)


class PackDocument:
    """一个已打开的资源包及其全部条目的编辑状态。"""

    def __init__(self, archive: Archive, path: Path | None = None):
        self.archive = archive
        self.path = path
        self._slots: list[_Slot] = [
            _Slot(origin=i) for i in range(archive.orig_count)
        ]
        self._kind_cache: dict[int, detect.EntryKind] = {}

    # ---------------------------------------------------------- 打开 ----
    @classmethod
    def open(cls, path: str | Path) -> PackDocument:
        """惰性打开磁盘上的包：只读目录索引，负载不进内存。"""
        p = Path(path)
        return cls(open_archive_path(p), path=p)

    @classmethod
    def from_bytes(cls, data: bytes) -> PackDocument:
        return cls(open_archive(data))

    def close(self) -> None:
        self.archive.close()

    def reopen_source(self) -> None:
        """按原路径重开归档，编辑状态（槽位/历史）保持不变。

        保存收尾时先释放源文件读句柄才能在 Windows 上覆盖原文件；
        若覆盖失败，用这个方法把句柄按原样接回来，文档继续可用。
        内存文档（from_bytes）没有源路径，句柄本就无需释放，跳过。
        """
        if self.path is not None:
            self.archive = open_archive_path(self.path)

    # ---------------------------------------------------------- 查询 ----
    @property
    def count(self) -> int:
        return len(self._slots)

    @property
    def kind(self) -> str:
        return self.archive.kind

    def stored(self, index: int) -> bytes:
        """条目当前的存储字节（未改动条目按需从源文件读取）。"""
        slot = self._slots[index]
        if slot.stored is not None:
            return slot.stored
        assert slot.origin is not None
        return self.archive.read_stored(slot.origin)

    def stored_len(self, index: int) -> int:
        """条目存储字节长度（未改动条目不读负载）。"""
        slot = self._slots[index]
        if slot.stored is not None:
            return len(slot.stored)
        assert slot.origin is not None
        return self.archive.stored_len(slot.origin)

    def content(self, index: int) -> bytes:
        """条目的内容视图字节（data.fls 为解压结果，余者同存储字节）。"""
        if self.archive.kind == KIND_FLSDATA:
            meta = self.archive.extra_metas[index]
            if meta.is_dir:
                return b""
            return flsdata.inflate(self.stored(index))
        return self.stored(index)

    def content_len(self, index: int) -> int:
        """条目内容视图长度（未改动条目不读负载、不解压）。"""
        slot = self._slots[index]
        if slot.origin is not None and slot.stored is None:
            return self.archive.content_len(slot.origin)
        return len(self.content(index))

    def entry_kind(self, index: int) -> detect.EntryKind:
        """条目类型（只嗅探头部，结果缓存；改动条目自动失效）。"""
        kind = self._kind_cache.get(index)
        if kind is None:
            kind = detect.sniff_prefix(self._content_head(index))
            self._kind_cache[index] = kind
        return kind

    def _content_head(self, index: int) -> bytes:
        """内容视图的前 512 字节（嗅探用，尽量不读全条）。"""
        slot = self._slots[index]
        if self.archive.kind == KIND_FLSDATA:
            meta = self.archive.extra_metas[index]
            if meta.is_dir:
                return b""
            stored = (slot.stored if slot.stored is not None
                      else self.archive.read_stored(slot.origin))  # type: ignore[arg-type]
            try:
                return zlib.decompressobj(-15).decompress(stored, 512)
            except zlib.error:
                return stored[:512]
        if slot.stored is not None:
            return slot.stored[:512]
        assert slot.origin is not None
        return self.archive.stored_head(slot.origin, 512)

    def label(self, index: int) -> str:
        """条目显示名：data.fls 用文件名，0SLF 用序号。"""
        if self.archive.kind == KIND_FLSDATA:
            return self.archive.extra_metas[index].name
        return f"条目 {index}"

    def is_dirty(self, index: int) -> bool:
        return self._slots[index].dirty

    @property
    def dirty_count(self) -> int:
        return sum(1 for slot in self._slots if slot.dirty)

    @property
    def is_modified(self) -> bool:
        if self.dirty_count > 0:
            return True
        return [s.origin for s in self._slots] != list(
            range(self.archive.orig_count))

    # ---------------------------------------------------------- 修改 ----
    def _set_stored(self, index: int, stored: bytes) -> None:
        slot = self._slots[index]
        slot.history.append((slot.stored, slot.dirty))
        slot.stored = stored
        slot.dirty = (
            slot.origin is not None
            and stored != self.archive.read_stored(slot.origin)
        )
        self._kind_cache.pop(index, None)

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
        slot = self._slots[index]
        if slot.origin is None:
            return  # 新增条目没有"打开时状态"可还原
        if slot.dirty or slot.stored is not None:
            slot.history.append((slot.stored, slot.dirty))
            slot.stored = None
            slot.dirty = False
            self._kind_cache.pop(index, None)

    def undo(self, index: int) -> bool:
        """撤销该条目最近一次修改；无可撤销时返回 False。"""
        slot = self._slots[index]
        if not slot.history:
            return False
        slot.stored, slot.dirty = slot.history.pop()
        self._kind_cache.pop(index, None)
        return True

    def add_entry(self, content: bytes, name: str | None = None) -> int:
        """追加新条目，返回新条目序号。data.fls 必须提供 name。"""
        if self.archive.kind == KIND_FLSDATA:
            if not name:
                raise ValueError("data.fls 新增条目必须提供文件名")
            self.archive.extra_metas.append(flsdata.EntryMeta(name=name))
            stored = flsdata.deflate(content)
        else:
            entry_id = len(self._slots)
            self.archive.extra_metas.append(
                fls0slf.EntryMeta(entry_id=entry_id, r1=0)
            )
            stored = content
        self._slots.append(_Slot(origin=None, stored=stored))
        return self.count - 1

    def delete_entry(self, index: int) -> None:
        del self.archive.extra_metas[index]
        del self._slots[index]
        self._kind_cache.clear()

    # ---------------------------------------------------------- 保存 ----
    def write_to(
        self,
        out: BinaryIO,
        progress: Callable[[int, int], None] | None = None,
    ) -> None:
        """把当前文档流式写入 out（未改动条目从源文件拷贝）。"""
        items: list[tuple[str, object]] = []
        for slot in self._slots:
            if slot.stored is not None:
                items.append(("data", slot.stored))
            else:
                assert slot.origin is not None
                items.append(("orig", slot.origin))
        self.archive.write_pack(out, items, progress)

    def build_bytes(self) -> bytes:
        """构建整个包的新字节（不落盘；大包请用 write_to 流式保存）。"""
        bio = io.BytesIO()
        self.write_to(bio)
        return bio.getvalue()

    def mark_saved(self, path: Path) -> None:
        """保存成功后同步基线：以新文件重建索引，改动状态清零。"""
        self.archive.close()
        self.archive = open_archive_path(path)
        self.path = path
        self._slots = [
            _Slot(origin=i) for i in range(self.archive.orig_count)
        ]
        self._kind_cache.clear()
