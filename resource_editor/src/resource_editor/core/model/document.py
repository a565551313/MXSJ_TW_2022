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
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

from .. import names as _names
from ..codecs import detect
from ..containers import (
    KIND_0SLF,
    KIND_FLSDATA,
    Archive,
    fls0slf,
    flsdata,
    open_archive,
    open_archive_path,
)
from ..mxhash import mx_hash


@dataclass
class _Slot:
    """一条目在打开后会话中的状态。"""

    origin: int | None                 # 原包序号；None=新增条目
    stored: bytes | None = None        # 改动后的存储字节；None=用原始
    dirty: bool = False                # 当前字节是否与原始不同
    history: list[tuple[bytes | None, bool]] = field(default_factory=list)
    path_name: str | None = None       # 按路径导入时登记的真名


class PackDocument:
    """一个已打开的资源包及其全部条目的编辑状态。"""

    def __init__(self, archive: Archive, path: Path | None = None):
        self.archive = archive
        self.path = path
        self.source_paths: set[Path] = {path} if path is not None else set()
        self._slots: list[_Slot] = [
            _Slot(origin=i) for i in range(archive.orig_count)
        ]
        self._kind_cache: dict[int, detect.EntryKind] = {}
        self._names: dict[int, str] | None = None  # 原始序号→真名

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

    # ---------------------------------------------------- 真名识别 ----
    def resolve_names(self) -> int:
        """为 0SLF 条目识别真名，返回识别出的条数（幂等）。

        字典命中给 .dlg 条目命名，再读这些布局扒出其引用的图片
        路径反查目录（详见 core.names）。识别需读种子条目负载，
        打开大包时应由后台任务调用；label() 首次被问到也会惰性
        触发。识别失败绝不影响文档可用性。
        """
        if self.archive.kind != "0slf":
            return 0
        if self._names is None:
            try:
                entry_ids = [meta.entry_id
                             for meta in self.archive.extra_metas]
                self._names = _names.build_name_map(
                    entry_ids, self.archive.read_stored)
            except Exception:
                self._names = {}
        return len(self._names)

    @property
    def named_count(self) -> int:
        """已识别真名的条数（未解析时为 0，不触发解析）。"""
        return len(self._names) if self._names else 0

    def true_name(self, index: int) -> str | None:
        """条目真名（导出命名用）：认不出返回 None，不回退序号。"""
        if self.archive.kind == KIND_FLSDATA:
            meta = self.archive.extra_metas[index]
            return meta.name if not meta.is_dir else None
        slot = self._slots[index]
        if slot.path_name:
            return slot.path_name
        self.resolve_names()
        origin = slot.origin
        if origin is not None and self._names:
            return self._names.get(origin)
        return None

    def label(self, index: int) -> str:
        """条目显示名：data.fls 用文件名；0SLF 优先真名，未识别出真名时回退序号。"""
        if self.archive.kind == KIND_FLSDATA:
            return self.archive.extra_metas[index].name
        slot = self._slots[index]
        if slot.path_name:
            return slot.path_name
        self.resolve_names()
        origin = slot.origin
        if origin is not None and self._names:
            name = self._names.get(origin)
            if name:
                return name
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
                fls0slf.EntryMeta(entry_id=entry_id,
                                  r1=fls0slf.fresh_r1(entry_id))
            )
            stored = content
        self._slots.append(_Slot(origin=None, stored=stored))
        return self.count - 1

    def index_by_path(self, res_path: str) -> int | None:
        """按资源路径查条目序号（0SLF：算 mx_hash 对 entry_id）。"""
        if self.archive.kind != "0slf":
            return None
        entry_id = mx_hash(res_path.encode("gbk", "replace"))
        for index, meta in enumerate(self.archive.extra_metas):
            if meta.entry_id == entry_id:
                return index
        return None

    def add_entry_for_path(self, content: bytes, res_path: str) -> int:
        """按资源路径追加条目：entry_id 用路径哈希，游戏才查得到。

        路径已在包中时抛 ValueError（调用方应改走替换）。仅 0SLF：
        data.fls 是名目录式容器，用 add_entry 并提供 name。
        """
        if self.archive.kind == KIND_FLSDATA:
            raise ValueError("data.fls 请用 add_entry 并提供文件名")
        existing = self.index_by_path(res_path)
        if existing is not None:
            raise ValueError(
                f"路径已存在于条目 {existing}，请改用替换")
        entry_id = mx_hash(res_path.encode("gbk", "replace"))
        self.archive.extra_metas.append(
            fls0slf.EntryMeta(entry_id=entry_id,
                              r1=fls0slf.fresh_r1(entry_id)))
        self._slots.append(_Slot(origin=None, stored=content,
                                 path_name=res_path))
        return self.count - 1

    def delete_entry(self, index: int) -> None:
        del self.archive.extra_metas[index]
        del self._slots[index]
        self._kind_cache.clear()

    # ---------------------------------------------------------- 保存 ----
    @contextmanager
    def preserve_write_order(self) -> Iterator[None]:
        """保存失败时恢复写前槽位顺序，避免 GUI 旧下标指向别的条目。

        write_to 为逐条校验对齐目录顺序；成功后 mark_saved 重建基线，
        发布前任一异常则撤销排序，不撤销用户本来的编辑。
        """
        archive = self.archive
        slots = list(self._slots)
        metas = list(archive.extra_metas)
        try:
            yield
        except BaseException:
            if self.archive is archive:
                self._slots = slots
                archive.extra_metas = metas
                self._kind_cache.clear()
            raise

    def changed_indexes(self) -> set[int]:
        """内容与原包不同（或新增）的条目下标集合。

        写后校验据此区分责任：被改动/新增的精灵试解码失败要拦，
        未改动的原始精灵解不开只是本机解码器未覆盖其变体——字节
        逐字未动，不拦保存。下标以当前槽位顺序为准（保存对齐
        后即文件顺序），故须在 write_to 之后调用。
        """
        return {i for i, slot in enumerate(self._slots)
                if slot.stored is not None}

    def _sort_slots_for_write(self) -> None:
        """保存对齐（仅 0SLF）：槽位与目录元数据按 entry_id 升序排列。

        引擎按有序目录寻址，写出的目录必须升序（见 fls0slf 模块
        文档）；先把文档顺序与将写出的文件顺序对齐，保存后按
        下标逐条校验（verifier）才成立。名字映射走槽位的原包
        序号，不受排序影响；按下标的种类缓存须清掉。
        """
        metas = self.archive.extra_metas
        order = sorted(range(len(self._slots)),
                       key=lambda i: metas[i].entry_id)
        if order == list(range(len(self._slots))):
            return
        self._slots = [self._slots[i] for i in order]
        self.archive.extra_metas = [metas[i] for i in order]
        self._kind_cache.clear()

    def write_to(
        self,
        out: BinaryIO,
        progress: Callable[[int, int], None] | None = None,
    ) -> None:
        """把当前文档流式写入 out（未改动条目从源文件拷贝）。"""
        if self.archive.kind == KIND_0SLF:
            self._sort_slots_for_write()
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
        # 路径哈希包不存真名：保留本会话导入时登记的名字，不能
        # 在保存后的槽位重建中丢失；旧名字缓存按原下标，必须重建。
        imported = {}
        if self.archive.kind == KIND_0SLF:
            imported = {
                meta.entry_id: slot.path_name
                for meta, slot in zip(
                    self.archive.extra_metas, self._slots, strict=True
                )
                if slot.path_name
            }
        # 新路径已发布且不是源包；先取得新句柄，再释放旧基线。
        # 若新文件打开失败，旧文档仍可读取，不留下已关闭的归档。
        new_archive = open_archive_path(path)
        self.archive.close()
        self.archive = new_archive
        self.path = path
        self.source_paths.add(path)
        self._slots = [
            _Slot(origin=i, path_name=imported.get(meta.entry_id))
            if self.archive.kind == KIND_0SLF else _Slot(origin=i)
            for i, meta in enumerate(self.archive.extra_metas)
        ]
        self._names = None
        self._kind_cache.clear()
