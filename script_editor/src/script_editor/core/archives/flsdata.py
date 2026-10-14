"""``FLS\\x00`` 容器（仅 data.fls）只读索引。

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
此独立基础版没有写包入口；不判断条目是否是有效脚本。
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

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
    try:
        return bytes(b ^ NAME_XOR for b in raw).decode("gbk")
    except UnicodeDecodeError as exc:
        raise ContainerError("目录文件名不是有效GBK，拒绝丢字替换") from exc


def parse_index(reader: RandomReader) -> FlsDataIndex:
    """只读固定头与中央目录，返回惰性索引。"""
    size = reader.size
    if size < HEADER_SIZE + 8:
        raise ContainerError("不是 FLS\\x00 资源包（魔数不符）")
    head = reader.read_at(0, HEADER_SIZE)
    if head[:4] != MAGIC:
        raise ContainerError("不是 FLS\\x00 资源包（魔数不符）")
    cd_offset, trailer = struct.unpack("<II", reader.read_at(size - 8, 8))
    if trailer != TRAILER_MAGIC:
        raise ContainerError("FLS尾部魔数不符")
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
        if pos + 28 + name_len > len(cd_data):
            raise ContainerError("中央目录文件名截断")
        name = _decode_name(cd_data[pos + 28 : pos + 28 + name_len])
        pos += 28 + name_len
        raw_records.append((w1, w2, w3, crc, csize, usize, l_off, name))
    metas: list[EntryMeta] = []
    spans: list[EntrySpan] = []
    for i, (w1, w2, w3, crc, csize, usize, l_off, name) in enumerate(raw_records):
        next_off = raw_records[i + 1][6] if i + 1 < len(raw_records) else cd_offset
        if (
            l_off < HEADER_SIZE
            or next_off > cd_offset
            or l_off + LOCAL_HEADER_SIZE + csize > next_off
        ):
            raise ContainerError(f"条目 {name} 本地偏移异常")
        local = reader.read_at(l_off, LOCAL_HEADER_SIZE)
        if len(local) != LOCAL_HEADER_SIZE:
            raise ContainerError("本地头截断")
        sig, local_w1, local_crc, local_csize, local_usize = struct.unpack(
            "<IHIII", local
        )
        if sig != LOCAL_SIG or (local_crc, local_csize, local_usize) != (
            crc,
            csize,
            usize,
        ):
            raise ContainerError("本地记录与中央目录不符")
        if not name.endswith(("/", "\\")) and local_w1 != w1:
            raise ContainerError("本地记录标志与目录不符")
        metas.append(EntryMeta(name=name, w1=w1, w2=w2, w3=w3))
        spans.append(
            EntrySpan(
                local_offset=l_off,
                local_len=next_off - l_off,
                csize=csize,
                usize=usize,
                crc=crc,
            )
        )
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
    return FlsDataArchive(header=index.header, payloads=payloads, metas=index.metas)
