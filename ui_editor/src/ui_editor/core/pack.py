"""``0SLF`` 资源包的只读容器（惰性索引 + 按路径哈希取条目）。

布局（与客户端一致，常量来自逆向结论）：头 12 字节为魔数
``0SLF``、u32 条目数、u32 目录偏移；目录为 count 条 16 字节记录
``<IIII (entry_id, r1, r2, r3)>``，真实长度/偏移由
:func:`decode_directory` 的闭式变换还原。打开时只读头部与目录，
614 MB 级大包亦可秒开；负载按需读取。

包内不存文件名：条目靠资源路径的 :func:`mx_hash` 寻址，
:func:`FlsPack.read_named` 即引擎的运行时查表方式。
"""

from __future__ import annotations

import struct
from pathlib import Path

from .errors import PackError
from .mxhash import mx_hash

MAGIC = b"0SLF"
MASK32 = 0xFFFFFFFF
DIR_RECORD_SIZE = 16
MAX_ENTRIES = 100_000_000

__all__ = ["FlsPack", "decode_directory"]


def decode_directory(index: int, raw: tuple[int, int, int, int]) -> tuple[int, int]:
    """还原一条目录记录，返回 ``(payload_length, payload_offset)``。"""
    entry_id, r1, r2, r3 = raw
    clen = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    doff = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return clen, doff


class FlsPack:
    """一个已打开的 0SLF 包：只保留索引，负载按需读。"""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._fh = open(self.path, "rb")
        try:
            self._spans, self._by_id = self._read_index()
        except Exception:
            self._fh.close()
            raise

    def _read_index(self) -> tuple[list[tuple[int, int]], dict[int, int]]:
        fh = self._fh
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(0)
        head = fh.read(12)
        if len(head) < 12 or head[:4] != MAGIC:
            raise PackError(f"不是 0SLF 资源包（魔数不符）：{self.path}")
        count, dir_offset = struct.unpack_from("<II", head, 4)
        if not 0 < count < MAX_ENTRIES:
            raise PackError(f"条目数异常：{count}（{self.path}）")
        dir_size = count * DIR_RECORD_SIZE
        if dir_offset + dir_size > size:
            raise PackError(f"目录区越界，文件可能损坏：{self.path}")
        fh.seek(dir_offset)
        dir_data = fh.read(dir_size)
        if len(dir_data) < dir_size:
            raise PackError(f"目录区读取不完整：{self.path}")
        spans: list[tuple[int, int]] = []
        by_id: dict[int, int] = {}
        for index in range(count):
            raw = struct.unpack_from("<IIII", dir_data, index * DIR_RECORD_SIZE)
            clen, doff = decode_directory(index, raw)
            if doff + clen > size:
                raise PackError(f"条目 {index} 负载越界：{self.path}")
            spans.append((doff, clen))
            by_id.setdefault(raw[0], index)
        return spans, by_id

    @property
    def count(self) -> int:
        return len(self._spans)

    def read_index(self, index: int) -> bytes:
        """按条目下标读取存储字节。"""
        offset, length = self._spans[index]
        self._fh.seek(offset)
        data = self._fh.read(length)
        if len(data) != length:
            raise PackError(f"条目 {index} 读取不完整：{self.path}")
        return data

    def contains(self, name: str) -> bool:
        """仅按路径哈希判断包里是否有该资源（不读负载，目录核对用）。"""
        if not name or not name.strip("\\/ "):
            return False
        return mx_hash(name.encode("gbk", "replace")) in self._by_id

    def read_named(self, name: str) -> bytes | None:
        """按资源路径读取条目（引擎查表方式），没有返回 None。"""
        if not name or not name.strip("\\/ "):
            return None
        entry_id = mx_hash(name.encode("gbk", "replace"))
        index = self._by_id.get(entry_id)
        if index is None:
            return None
        return self.read_index(index)

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> FlsPack:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
