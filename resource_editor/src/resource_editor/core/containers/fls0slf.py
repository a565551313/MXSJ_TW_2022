"""``0SLF`` 容器（script/skill/skill2/passive/effect/magicres5.fls）读写。

布局（已对 TW v2.27.2 全部 6 个包验证）：

* 头 12 字节：``0SLF`` 魔数、u32 条目数 @4、u32 目录偏移 @8。
* 目录为 count 条 16 字节记录 ``<IIII (entry_id, r1, r2, r3)>``，
  其中真实的负载长度与偏移被混淆，用 :func:`decode_directory`
  的闭式变换还原（与客户端一致，常量来自既有逆向成果）。
* 负载即条目的"存储字节"：美术包为原始字节，script.fls 为 zlib 流。
  本模块只搬运存储字节，不做任何解压。

重打包策略：16 字节头 + 负载按条目顺序拼接 + 目录重编码；
每条目保留原始 ``(entry_id, r1)``，未改动条目逐字节一致。
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

from ..errors import ContainerError

MAGIC = b"0SLF"
MASK32 = 0xFFFFFFFF
DIR_RECORD_SIZE = 16
HEADER_SIZE = 16


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


@dataclass
class Fls0SlfArchive:
    """一个已解析的 0SLF 包：存储字节列表 + 对应元数据。"""

    payloads: list[bytes]
    metas: list[EntryMeta]

    @property
    def count(self) -> int:
        return len(self.payloads)


def parse(data: bytes) -> Fls0SlfArchive:
    """解析 0SLF 包字节，失败抛 :class:`ContainerError`。"""
    if len(data) < 12 or data[:4] != MAGIC:
        raise ContainerError("不是 0SLF 资源包（魔数不符）")
    count, dir_offset = struct.unpack_from("<II", data, 4)
    if not 0 < count < 1_000_000:
        raise ContainerError(f"条目数异常：{count}")
    dir_end = dir_offset + count * DIR_RECORD_SIZE
    if dir_end > len(data):
        raise ContainerError("目录区越界，文件可能损坏")
    payloads: list[bytes] = []
    metas: list[EntryMeta] = []
    for index in range(count):
        raw = struct.unpack_from("<IIII", data, dir_offset + index * DIR_RECORD_SIZE)
        clen, doff = decode_directory(index, raw)
        if doff + clen > len(data):
            raise ContainerError(f"条目 {index} 负载越界，文件可能损坏")
        payloads.append(data[doff:doff + clen])
        metas.append(EntryMeta(entry_id=raw[0], r1=raw[1]))
    return Fls0SlfArchive(payloads=payloads, metas=metas)


def build(payloads: list[bytes], metas: list[EntryMeta]) -> bytes:
    """把存储字节与元数据构建为完整的 0SLF 包字节。"""
    if len(payloads) != len(metas):
        raise ContainerError("负载与元数据条数不一致")
    body = bytearray()
    records = bytearray()
    for index, (payload, meta) in enumerate(
            zip(payloads, metas, strict=True)):
        offset = HEADER_SIZE + len(body)
        body.extend(payload)
        records.extend(
            encode_directory(index, meta.entry_id, meta.r1, len(payload), offset)
        )
    dir_offset = HEADER_SIZE + len(body)
    header = struct.pack("<4sIII", MAGIC, len(payloads), dir_offset, 0)
    return header + bytes(body) + bytes(records)
