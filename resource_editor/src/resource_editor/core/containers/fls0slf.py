"""``0SLF`` 容器（script/skill/skill2/passive/effect/magicres5.fls）读写。

布局（已对 TW v2.27.2 全部 6 个包验证）：

* 头 12 字节：``0SLF`` 魔数、u32 条目数 @4、u32 目录偏移 @8。
* 目录为 count 条 16 字节记录 ``<IIII (entry_id, r1, r2, r3)>``，
  其中真实的负载长度与偏移被混淆，用 :func:`decode_directory`
  的闭式变换还原（与客户端一致，常量来自既有逆向成果）。
* 负载即条目的"存储字节"：美术包为原始字节，script.fls 为 zlib 流。
  本模块只搬运存储字节，不做任何解压。

打开方式有两种：:func:`parse` 把负载全部读入内存（小包/测试用）；
:func:`parse_index` 只读头部与目录，给出每条负载在源中的位置
（惰性打开，大包用这个，与文件大小无关地秒开）。

重打包策略：16 字节头 + 负载按条目顺序拼接 + 目录重编码；
每条目保留原始 ``(entry_id, r1)``，未改动条目逐字节一致。
"""
from __future__ import annotations

import io
import struct
from collections.abc import Callable
from dataclasses import dataclass
from typing import BinaryIO

from ..errors import ContainerError
from .readers import BytesReader, RandomReader

MAGIC = b"0SLF"
MASK32 = 0xFFFFFFFF
DIR_RECORD_SIZE = 16
HEADER_SIZE = 16
MAX_ENTRIES = 100_000_000


def decode_directory(index: int, raw: tuple[int, int, int, int]) -> tuple[int, int]:
    """还原一条目录记录，返回 ``(compressed_length, payload_offset)``。"""
    entry_id, r1, r2, r3 = raw
    clen = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    doff = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return clen, doff


def encode_directory(index: int, entry_id: int, r1: int, clen: int, doff: int) -> bytes:
    """把 ``(entry_id, r1, clen, doff)`` 编码为 16 字节目录记录。"""
    r2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ clen) & MASK32
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ doff) & MASK32
    return struct.pack("<IIII", entry_id, r1, r2, r3)


@dataclass
class EntryMeta:
    """重打包时需要保留的每条目目录字段。"""

    entry_id: int
    r1: int


@dataclass(frozen=True)
class EntrySpan:
    """一条负载在源文件中的位置（惰性读取用）。"""

    offset: int
    length: int


@dataclass
class Fls0SlfIndex:
    """0SLF 包的惰性索引：元数据 + 每条负载的位置。"""

    metas: list[EntryMeta]
    spans: list[EntrySpan]

    @property
    def count(self) -> int:
        return len(self.metas)


@dataclass
class Fls0SlfArchive:
    """一个已解析的 0SLF 包：存储字节列表 + 对应元数据。"""

    payloads: list[bytes]
    metas: list[EntryMeta]

    @property
    def count(self) -> int:
        return len(self.payloads)


def parse_index(reader: RandomReader) -> Fls0SlfIndex:
    """只读头部与目录，返回惰性索引；reader 需有 read_at/size。"""
    head = reader.read_at(0, 12)
    if len(head) < 12 or head[:4] != MAGIC:
        raise ContainerError("不是 0SLF 资源包（魔数不符）")
    count, dir_offset = struct.unpack_from("<II", head, 4)
    if not 0 < count < MAX_ENTRIES:
        raise ContainerError(f"条目数异常：{count}")
    dir_size = count * DIR_RECORD_SIZE
    if dir_offset + dir_size > reader.size:
        raise ContainerError("目录区越界，文件可能损坏")
    dir_data = reader.read_at(dir_offset, dir_size)
    if len(dir_data) < dir_size:
        raise ContainerError("目录区读取不完整，文件可能损坏")
    metas: list[EntryMeta] = []
    spans: list[EntrySpan] = []
    for index in range(count):
        raw = struct.unpack_from("<IIII", dir_data, index * DIR_RECORD_SIZE)
        clen, doff = decode_directory(index, raw)
        if doff + clen > reader.size:
            raise ContainerError(f"条目 {index} 负载越界，文件可能损坏")
        metas.append(EntryMeta(entry_id=raw[0], r1=raw[1]))
        spans.append(EntrySpan(offset=doff, length=clen))
    return Fls0SlfIndex(metas=metas, spans=spans)


def parse(data: bytes) -> Fls0SlfArchive:
    """解析 0SLF 包字节（负载全量读入内存），失败抛 ContainerError。"""
    reader = BytesReader(data)
    index = parse_index(reader)
    payloads = [
        reader.read_at(span.offset, span.length) for span in index.spans
    ]
    return Fls0SlfArchive(payloads=payloads, metas=index.metas)


def write_stream(
    out: BinaryIO,
    metas: list[EntryMeta],
    write_entry: Callable[[int, BinaryIO], int],
) -> None:
    """流式写出 0SLF 包：write_entry(i, out) 写第 i 条负载并返回其长度。

    out 需可 seek（临时文件即可）：先写占位头，负载与目录写完后回填。
    """
    out.write(bytes(HEADER_SIZE))
    records = bytearray()
    for index, meta in enumerate(metas):
        offset = out.tell()
        clen = write_entry(index, out)
        records.extend(
            encode_directory(index, meta.entry_id, meta.r1, clen, offset))
    dir_offset = out.tell()
    out.write(bytes(records))
    out.seek(0)
    out.write(struct.pack("<4sIII", MAGIC, len(metas), dir_offset, 0))
    out.seek(dir_offset + len(records))


def build(payloads: list[bytes], metas: list[EntryMeta]) -> bytes:
    """把存储字节与元数据构建为完整的 0SLF 包字节。"""
    if len(payloads) != len(metas):
        raise ContainerError("负载与元数据条数不一致")

    def write_entry(index: int, out: BinaryIO) -> int:
        out.write(payloads[index])
        return len(payloads[index])

    bio = io.BytesIO()
    write_stream(bio, metas, write_entry)
    return bio.getvalue()
