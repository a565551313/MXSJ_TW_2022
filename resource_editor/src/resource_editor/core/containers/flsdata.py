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

本模块以"解压后内容"为条目内容视图，存储字节为 raw-deflate 流；
重打包时未改动条目沿用原存储字节逐字节写入。
"""
from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

from ..errors import ContainerError

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


def parse(data: bytes) -> FlsDataArchive:
    """解析 data.fls 包字节，失败抛 :class:`ContainerError`。"""
    if len(data) < HEADER_SIZE + 8 or data[:4] != MAGIC:
        raise ContainerError("不是 FLS\\x00 资源包（魔数不符）")
    cd_offset = struct.unpack_from("<I", data, len(data) - 8)[0]
    if not HEADER_SIZE <= cd_offset < len(data) - 8:
        raise ContainerError("中央目录偏移异常，文件可能损坏")
    payloads: list[bytes] = []
    metas: list[EntryMeta] = []
    pos = cd_offset
    while pos < len(data) - 8:
        sig = struct.unpack_from("<I", data, pos)[0]
        if sig != CD_SIG:
            raise ContainerError(f"中央目录签名异常 @ {pos:#x}")
        w1, w2, w3 = struct.unpack_from("<HHH", data, pos + 4)
        _crc, csize, _usize, l_off = struct.unpack_from("<IIII", data, pos + 10)
        name_len = struct.unpack_from("<H", data, pos + 26)[0]
        name = _decode_name(data[pos + 28:pos + 28 + name_len])
        pos += 28 + name_len
        meta = EntryMeta(name=name, w1=w1, w2=w2, w3=w3)
        if meta.is_dir or csize == 0:
            payloads.append(b"")
        else:
            start = l_off + LOCAL_HEADER_SIZE
            if start + csize > len(data):
                raise ContainerError(f"条目 {name} 负载越界")
            payloads.append(data[start:start + csize])
        metas.append(meta)
    return FlsDataArchive(
        header=data[:HEADER_SIZE], payloads=payloads, metas=metas
    )


def build(archive: FlsDataArchive, payloads: list[bytes]) -> bytes:
    """按给定存储字节重建完整的 data.fls 包字节。

    ``payloads`` 与 ``archive.metas`` 一一对应；目录项负载忽略。
    CRC/长度按每条目的解压内容重新计算，未改动条目的存储字节
    原样写入，因此其 CRC/长度与原包一致。
    """
    if len(payloads) != len(archive.metas):
        raise ContainerError("负载与元数据条数不一致")
    out = bytearray(archive.header)
    cd_records: list[tuple[EntryMeta, int, int, int, int]] = []
    for meta, stored in zip(archive.metas, payloads, strict=True):
        l_off = len(out)
        if meta.is_dir:
            out.extend(struct.pack("<IHIII", LOCAL_SIG, 0, 0, 0, 0))
            cd_records.append((meta, 0, 0, 0, l_off))
            continue
        content = inflate(stored) if stored else b""
        crc = zlib.crc32(content) & 0xFFFFFFFF
        out.extend(
            struct.pack(
                "<IHIII", LOCAL_SIG, meta.w1, crc, len(stored), len(content)
            )
        )
        out.extend(stored)
        cd_records.append((meta, crc, len(stored), len(content), l_off))
    cd_offset = len(out)
    for meta, crc, csize, usize, l_off in cd_records:
        name_raw = _encode_name(meta.name)
        out.extend(
            struct.pack(
                "<IHHHIIIIH",
                CD_SIG, meta.w1, meta.w2, meta.w3,
                crc, csize, usize, l_off, len(name_raw),
            )
        )
        out.extend(name_raw)
    out.extend(struct.pack("<II", cd_offset, TRAILER_MAGIC))
    return bytes(out)
