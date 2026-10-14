"""``FLS\\x00`` 容器（仅 data.fls）读写。

布局（已对 TW v2.27.2 的 data.fls 全量验证，133 条中央目录记录）：

* 前 64 字节为固定头（``FLS\\x00`` + 版本字段等），本地条目自偏移 64 起。
* 每条本地记录：18 字节本地头 ``<IHIII``＝签名 ``0xA0975237``、w1、
  CRC32（**解压后**内容的 CRC）、压缩长、原始长，其后是 raw-deflate 流。
* 中央目录位于文件尾前：位置由尾部 8 字节的首 u32 给出；每条记录
  ``<IHHHIIIIH``＝签名 ``0x87F2017C``、w1/w2/w3、CRC、压缩长、原始长、
  本地偏移、名长，其后是 XOR 0xA5 混淆的 GBK 文件名。
* 尾部 8 字节：u32 中央目录偏移 + u32 ``0xA1985237``。
* 名字以 ``\\`` 结尾者为目录项（无负载，中央目录中长度为 0）。

本模块以"解压后内容"为条目内容视图，存储字节为 raw-deflate 流。
打开方式有两种：:func:`parse` 全量读入内存（小包/测试用）；
:func:`parse_index` 只读头部与中央目录（惰性打开用）。
重打包时未改动条目把原本地记录整段照抄，逐字节一致。
"""
from __future__ import annotations

import io
import struct
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import BinaryIO

from ..errors import ContainerError
from .readers import BytesReader, RandomReader

MAGIC = b"FLS\x00"
LOCAL_SIG = 0xA0975237
CD_SIG = 0x87F2017C
TRAILER_MAGIC = 0xA1985237
NAME_XOR = 0xA5
HEADER_SIZE = 64
LOCAL_HEADER_SIZE = 18
DEFAULT_W1 = 8


@dataclass
class EntryMeta:
    """重打包时需要保留的每条目字段。"""

    name: str
    w1: int = DEFAULT_W1
    w2: int = 0
    w3: int = 0

    @property
    def is_dir(self) -> bool:
        return self.name.endswith("\\") or self.name.endswith("/")


@dataclass(frozen=True)
class EntrySpan:
    """一条本地记录在源文件中的位置与校验字段快照（惰性读取用）。

    ``local_len`` 是本地头+负载（乃至条间填充）的整段长度：
    流式重打包未改动条目时按它整段照抄，与原文件逐字节一致。
    """

    local_offset: int
    local_len: int
    csize: int
    usize: int
    crc: int

    @property
    def data_offset(self) -> int:
        return self.local_offset + LOCAL_HEADER_SIZE


@dataclass
class FlsDataIndex:
    """data.fls 的惰性索引：固定头 + 元数据 + 本地记录位置。"""

    header: bytes
    metas: list[EntryMeta]
    spans: list[EntrySpan]

    @property
    def count(self) -> int:
        return len(self.metas)


@dataclass
class FlsDataArchive:
    """一个已解析的 data.fls 包：存储字节（deflate 流）+ 元数据。"""

    header: bytes
    payloads: list[bytes]
    metas: list[EntryMeta]

    @property
    def count(self) -> int:
        return len(self.payloads)


def inflate(stored: bytes) -> bytes:
    """把 raw-deflate 存储字节解压为内容视图。"""
    try:
        return zlib.decompress(stored, -15)
    except zlib.error as exc:
        raise ContainerError(f"条目解压失败：{exc}") from exc


def deflate(content: bytes) -> bytes:
    """把内容视图压缩为 raw-deflate 存储字节。"""
    return zlib.compress(content, 9)[2:-4]


def _decode_name(raw: bytes) -> str:
    return bytes(b ^ NAME_XOR for b in raw).decode("gbk", errors="replace")


def _encode_name(name: str) -> bytes:
    return bytes(b ^ NAME_XOR for b in name.encode("gbk"))


def parse_index(reader: RandomReader) -> FlsDataIndex:
    """只读固定头与中央目录，返回惰性索引。"""
    size = reader.size
    if size < HEADER_SIZE + 8:
        raise ContainerError("不是 FLS\\x00 资源包（魔数不符）")
    head = reader.read_at(0, HEADER_SIZE)
    if head[:4] != MAGIC:
        raise ContainerError("不是 FLS\\x00 资源包（魔数不符）")
    cd_offset = struct.unpack_from("<I", reader.read_at(size - 8, 8), 0)[0]
    if not HEADER_SIZE <= cd_offset < size - 8:
        raise ContainerError("中央目录偏移异常，文件可能损坏")
    cd_data = reader.read_at(cd_offset, size - 8 - cd_offset)
    raw_records = []
    pos = 0
    while pos < len(cd_data):
        if pos + 28 > len(cd_data):
            raise ContainerError("中央目录记录截断，文件可能损坏")
        sig = struct.unpack_from("<I", cd_data, pos)[0]
        if sig != CD_SIG:
            raise ContainerError(f"中央目录签名异常 @ {cd_offset + pos:#x}")
        w1, w2, w3 = struct.unpack_from("<HHH", cd_data, pos + 4)
        crc, csize, usize, l_off = struct.unpack_from("<IIII", cd_data, pos + 10)
        name_len = struct.unpack_from("<H", cd_data, pos + 26)[0]
        name = _decode_name(cd_data[pos + 28:pos + 28 + name_len])
        pos += 28 + name_len
        raw_records.append((w1, w2, w3, crc, csize, usize, l_off, name))
    metas: list[EntryMeta] = []
    spans: list[EntrySpan] = []
    for i, (w1, w2, w3, crc, csize, usize, l_off, name) in enumerate(
            raw_records):
        next_off = (raw_records[i + 1][6] if i + 1 < len(raw_records)
                    else cd_offset)
        if l_off < HEADER_SIZE or next_off < l_off:
            raise ContainerError(f"条目 {name} 本地偏移异常")
        metas.append(EntryMeta(name=name, w1=w1, w2=w2, w3=w3))
        spans.append(EntrySpan(
            local_offset=l_off,
            local_len=next_off - l_off,
            csize=csize, usize=usize, crc=crc,
        ))
    return FlsDataIndex(header=head, metas=metas, spans=spans)


def parse(data: bytes) -> FlsDataArchive:
    """解析 data.fls 包字节（负载全量读入内存），失败抛 ContainerError。"""
    reader = BytesReader(data)
    index = parse_index(reader)
    payloads: list[bytes] = []
    for meta, span in zip(index.metas, index.spans, strict=True):
        if meta.is_dir or span.csize == 0:
            payloads.append(b"")
        else:
            payloads.append(reader.read_at(span.data_offset, span.csize))
    return FlsDataArchive(
        header=index.header, payloads=payloads, metas=index.metas)


def write_local_record(
    out: BinaryIO, meta: EntryMeta, stored: bytes
) -> tuple[int, int, int]:
    """以给定存储字节写一条本地记录，返回 (crc, csize, usize)。"""
    if meta.is_dir:
        out.write(struct.pack("<IHIII", LOCAL_SIG, 0, 0, 0, 0))
        return 0, 0, 0
    content = inflate(stored) if stored else b""
    crc = zlib.crc32(content) & 0xFFFFFFFF
    out.write(struct.pack(
        "<IHIII", LOCAL_SIG, meta.w1, crc, len(stored), len(content)))
    out.write(stored)
    return crc, len(stored), len(content)


def write_stream(
    out: BinaryIO,
    header: bytes,
    metas: list[EntryMeta],
    write_local: Callable[[int, BinaryIO], tuple[int, int, int]],
) -> None:
    """流式写出 data.fls 包：write_local(i, out) 写第 i 条本地记录
    （本地头+负载），返回该条的 (crc, csize, usize) 供中央目录使用。"""
    out.write(header)
    cd_records = []
    for index, meta in enumerate(metas):
        l_off = out.tell()
        crc, csize, usize = write_local(index, out)
        cd_records.append((meta, crc, csize, usize, l_off))
    cd_offset = out.tell()
    for meta, crc, csize, usize, l_off in cd_records:
        name_raw = _encode_name(meta.name)
        out.write(struct.pack(
            "<IHHHIIIIH",
            CD_SIG, meta.w1, meta.w2, meta.w3,
            crc, csize, usize, l_off, len(name_raw),
        ))
        out.write(name_raw)
    out.write(struct.pack("<II", cd_offset, TRAILER_MAGIC))


def build(archive: FlsDataArchive, payloads: list[bytes]) -> bytes:
    """按给定存储字节重建完整的 data.fls 包字节。

    ``payloads`` 与 ``archive.metas`` 一一对应；目录项负载忽略。
    CRC/长度按每条目的解压内容重新计算，未改动条目的存储字节
    原样写入，因此其 CRC/长度与原包一致。
    """
    if len(payloads) != len(archive.metas):
        raise ContainerError("负载与元数据条数不一致")
    bio = io.BytesIO()
    write_stream(
        bio, archive.header, archive.metas,
        lambda i, out: write_local_record(out, archive.metas[i], payloads[i]),
    )
    return bio.getvalue()
