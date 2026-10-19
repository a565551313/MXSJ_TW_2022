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
import threading
from pathlib import Path

from .errors import PackError
from .mxhash import path_hash

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
        # 后台任务与界面绘制可能并发取条目：seek+read 必须整体串行。
        self._io_lock = threading.Lock()
        try:
            self._spans, self._by_id, self._ids = self._read_index()
        except Exception:
            self._fh.close()
            raise

    def _read_index(self) -> tuple[list[tuple[int, int]], dict[int, int],
                                   list[int]]:
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
        ids: list[int] = []
        for index in range(count):
            raw = struct.unpack_from("<IIII", dir_data, index * DIR_RECORD_SIZE)
            clen, doff = decode_directory(index, raw)
            if doff + clen > size:
                raise PackError(f"条目 {index} 负载越界：{self.path}")
            spans.append((doff, clen))
            by_id.setdefault(raw[0], index)
            ids.append(raw[0])
        return spans, by_id, ids

    @property
    def count(self) -> int:
        return len(self._spans)

    @property
    def entry_ids(self) -> list[int]:
        """目录中的条目号列表（按目录顺序；真实包恒为升序）。"""
        return self._ids

    def span_of(self, entry_id: int) -> tuple[int, int] | None:
        """按条目号查 (负载偏移, 长度)；不在包中返回 None。"""
        index = self._by_id.get(entry_id)
        return None if index is None else self._spans[index]

    def read_id(self, entry_id: int) -> bytes | None:
        """按条目号读存储字节；不在包中返回 None。"""
        index = self._by_id.get(entry_id)
        return None if index is None else self.read_index(index)

    def read_index(self, index: int) -> bytes:
        """按条目下标读取存储字节（内部加锁，支持并发调用）。"""
        offset, length = self._spans[index]
        with self._io_lock:
            self._fh.seek(offset)
            data = self._fh.read(length)
        if len(data) != length:
            raise PackError(f"条目 {index} 读取不完整：{self.path}")
        return data

    @staticmethod
    def entry_id_for(name: str) -> int | None:
        """路径 → entry_id；空名或 GBK 不可编码时返回 None（不静默替换）。"""
        if not name or not name.strip("\\/ "):
            return None
        try:
            return path_hash(name)
        except ValueError:
            return None

    def contains(self, name: str) -> bool:
        """仅按路径哈希判断包里是否有该资源（不读负载，目录核对用）。

        名称无法按 GBK 编码时返回 False：引擎用同样的字节寻址，它也查不到。
        旧实现用 ``encode("gbk", "replace")`` 把不可编码字符换成 ``?``，
        等于**拿另一个路径去查**（分析报告 P2-2）。
        """
        digest = self.entry_id_for(name)
        return digest is not None and digest in self._by_id

    def matched_paths(self, hash_to_path: dict[int, str]) -> list[str]:
        """从 {路径哈希: 路径} 映射里挑出本包实际包含的路径（已排序）。"""
        return sorted(path for eid, path in hash_to_path.items()
                      if eid in self._by_id)

    def read_named(self, name: str) -> bytes | None:
        """按资源路径读取条目（引擎查表方式），没有返回 None。

        不可按 GBK 编码的名称视为不存在，理由同 :meth:`contains`。
        """
        entry_id = self.entry_id_for(name)
        index = None if entry_id is None else self._by_id.get(entry_id)
        if index is None:
            return None
        return self.read_index(index)

    def close(self) -> None:
        with self._io_lock:
            self._fh.close()

    def __enter__(self) -> FlsPack:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
