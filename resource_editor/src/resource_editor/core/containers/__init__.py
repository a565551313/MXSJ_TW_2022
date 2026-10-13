"""资源包容器层：按魔数分发到 0SLF / FLS\\x00 两种实现。

打开一律是惰性的：只解析头部与目录建立索引，条目负载按需
从源文件读取（见 :mod:`readers`），多大的包也是秒开；
保存时未改动条目从源文件流式拷贝，不经过内存。
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO

from ..errors import ContainerError
from . import fls0slf, flsdata
from .readers import BytesReader, FileReader, RandomReader

KIND_0SLF = "0slf"
KIND_FLSDATA = "flsdata"


class Archive:
    """统一容器视图：惰性索引 + 当前条目元数据。

    ``extra_metas`` 是与当前条目序平行的元数据列表，文档层在
    增删条目时同步维护；``_orig_metas`` / spans 是打开时的快照，
    ``read_stored(origin)`` 按原始序号读取未改动条目的存储字节。
    """

    def __init__(self, kind: str, reader: RandomReader,
                 index0: fls0slf.Fls0SlfIndex | None = None,
                 indexd: flsdata.FlsDataIndex | None = None):
        self.kind = kind
        self._reader = reader
        self._index0 = index0
        self._indexd = indexd
        if kind == KIND_0SLF:
            assert index0 is not None
            self.extra_metas: list = list(index0.metas)
            self.header = b""
        else:
            assert indexd is not None
            self.extra_metas = list(indexd.metas)
            self.header = indexd.header

    # ---------------------------------------------------------- 打开 ----
    @property
    def reader(self) -> RandomReader:
        return self._reader

    @property
    def orig_count(self) -> int:
        """打开时的条目数（原始序号空间大小）。"""
        if self.kind == KIND_0SLF:
            assert self._index0 is not None
            return self._index0.count
        assert self._indexd is not None
        return self._indexd.count

    def close(self) -> None:
        self._reader.close()

    # ---------------------------------------------------------- 读取 ----
    def read_stored(self, origin: int) -> bytes:
        """按原始序号读取条目的存储字节（0SLF 即负载；data 为 deflate 流）。"""
        if self.kind == KIND_0SLF:
            assert self._index0 is not None
            span = self._index0.spans[origin]
            return self._reader.read_at(span.offset, span.length)
        assert self._indexd is not None
        meta = self._indexd.metas[origin]
        span = self._indexd.spans[origin]
        if meta.is_dir or span.csize == 0:
            return b""
        return self._reader.read_at(span.data_offset, span.csize)

    def stored_len(self, origin: int) -> int:
        """按原始序号返回存储字节长度（不读负载）。"""
        if self.kind == KIND_0SLF:
            assert self._index0 is not None
            return self._index0.spans[origin].length
        assert self._indexd is not None
        return self._indexd.spans[origin].csize

    def content_len(self, origin: int) -> int:
        """按原始序号返回内容视图长度（不读负载）。"""
        if self.kind == KIND_0SLF:
            return self.stored_len(origin)
        assert self._indexd is not None
        return self._indexd.spans[origin].usize

    def stored_head(self, origin: int, size: int = 512) -> bytes:
        """按原始序号读取存储字节头部（类型嗅探用，至多 size 字节）。"""
        if self.kind == KIND_0SLF:
            assert self._index0 is not None
            span = self._index0.spans[origin]
            return self._reader.read_at(
                span.offset, min(size, span.length))
        return self.read_stored(origin)[:size]

    # ---------------------------------------------------------- 构建 ----
    def write_pack(
        self,
        out: BinaryIO,
        items: list[tuple[str, object]],
        progress: Callable[[int, int], None] | None = None,
    ) -> None:
        """流式写出整个包到 out（需可 seek）。

        ``items`` 与 ``extra_metas`` 平行：``("orig", 原始序号)`` 表示
        该条未改动、从源文件流式拷贝；``("data", 存储字节)`` 表示
        写入给定字节。progress(done, total) 可选进度回调。
        """
        total = len(items)
        if self.kind == KIND_0SLF:
            self._write_0slf(out, items, progress, total)
        else:
            self._write_flsdata(out, items, progress, total)

    def _report(self, progress, done: int, total: int) -> None:
        if progress is not None and (done % 256 == 0 or done == total):
            progress(done, total)

    def _write_0slf(self, out, items, progress, total) -> None:
        reader = self._reader
        index0 = self._index0
        assert index0 is not None

        def write_entry(i: int, dest: BinaryIO) -> int:
            tag, value = items[i]
            if tag == "orig":
                span = index0.spans[int(value)]
                reader.copy_to(span.offset, span.length, dest)
                return span.length
            data = bytes(value)  # type: ignore[arg-type]
            dest.write(data)
            return len(data)

        def wrapped(i: int, dest: BinaryIO) -> int:
            n = write_entry(i, dest)
            self._report(progress, i + 1, total)
            return n

        fls0slf.write_stream(out, self.extra_metas, wrapped)

    def _write_flsdata(self, out, items, progress, total) -> None:
        reader = self._reader
        indexd = self._indexd
        assert indexd is not None
        metas = self.extra_metas

        def write_local(i: int, dest: BinaryIO) -> tuple[int, int, int]:
            tag, value = items[i]
            meta = metas[i]
            if tag == "orig" and not _meta_differs(meta, indexd.metas[int(value)]):
                span = indexd.spans[int(value)]
                reader.copy_to(span.local_offset, span.local_len, dest)
                result = (span.crc, span.csize, span.usize)
            else:
                stored = (self.read_stored(int(value)) if tag == "orig"
                          else bytes(value))  # type: ignore[arg-type]
                result = flsdata.write_local_record(dest, meta, stored)
            self._report(progress, i + 1, total)
            return result

        flsdata.write_stream(out, self.header, metas, write_local)

    def build(self, payloads: list[bytes]) -> bytes:
        """用新的存储字节列表重建整个包字节（小包/测试用；大包用 write_pack）。"""
        import io

        bio = io.BytesIO()
        self.write_pack(bio, [("data", p) for p in payloads])
        return bio.getvalue()


def _meta_differs(cur: flsdata.EntryMeta, orig: flsdata.EntryMeta) -> bool:
    """data.fls 元数据是否被改过（改名等）——改过则不能整段照抄本地记录。"""
    return ((cur.name, cur.w1, cur.w2, cur.w3)
            != (orig.name, orig.w1, orig.w2, orig.w3))


def open_archive(data: bytes) -> Archive:
    """按魔数解析内存中的包字节（惰性索引，负载从内存按需取）。"""
    return _open_with_reader(BytesReader(data))


def open_archive_path(path: str | Path) -> Archive:
    """按魔数惰性打开磁盘上的包（只读目录，负载不进内存）。"""
    return _open_with_reader(FileReader(path))


def _open_with_reader(reader: RandomReader) -> Archive:
    try:
        magic = reader.read_at(0, 4)
        if magic == fls0slf.MAGIC:
            return Archive(KIND_0SLF, reader,
                           index0=fls0slf.parse_index(reader))
        if magic == flsdata.MAGIC:
            return Archive(KIND_FLSDATA, reader,
                           indexd=flsdata.parse_index(reader))
    except Exception:
        reader.close()
        raise
    reader.close()
    raise ContainerError(f"未知资源包魔数：{magic!r}")
