"""随机读抽象：惰性打开资源包时只读目录，条目负载按需读取。

* :class:`FileReader` 按偏移读，不把整文件载入内存，
  1GB 级资源包也只占条目数级别的内存；
* :class:`BytesReader` 服务于内存中的字节（测试与合成包）。

跨平台说明：``os.pread`` 是 POSIX 专属，Windows 的 ``os`` 模块
没有它 —— Windows 上退化为「加锁 seek+read」（锁只串行化定位读
本身，负载解码仍在锁外并行）。另外 Windows 打开文件必须带
``O_BINARY``，否则文本模式会折叠 CRLF、把 0x1A 当作 EOF，
静默毁坏二进制负载。0.2.0 在真实 Windows 上报
``module 'os' has no attribute 'pread'`` 就是前者所致。
"""
from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import BinaryIO, Protocol

_CHUNK = 1024 * 1024

# Windows 无 pread；其余平台用 pread 做无共享文件指针的定位读。
_PREAD = getattr(os, "pread", None)
# Windows 需要 O_BINARY 关掉文本模式转换，POSIX 无此标志。
_OPEN_FLAGS = os.O_RDONLY | getattr(os, "O_BINARY", 0)


class RandomReader(Protocol):
    """随机读来源协议：FileReader 与 BytesReader 均实现之。"""

    @property
    def size(self) -> int: ...

    def read_at(self, offset: int, size: int) -> bytes: ...

    def copy_to(self, offset: int, length: int, out: BinaryIO) -> None: ...

    def close(self) -> None: ...


class BytesReader:
    """把内存字节当作可随机读的来源。"""

    def __init__(self, data: bytes):
        self._data = data

    @property
    def size(self) -> int:
        return len(self._data)

    def read_at(self, offset: int, size: int) -> bytes:
        return self._data[offset:offset + size]

    def copy_to(self, offset: int, length: int, out: BinaryIO) -> None:
        out.write(self._data[offset:offset + length])

    def close(self) -> None:
        pass


class FileReader:
    """按偏移读取磁盘文件，不整文件载入内存。

    有 ``os.pread`` 时用它做无状态定位读（天然线程安全）；没有
    （Windows）时用一把锁串行化 ``lseek + read``，读到的数据在
    锁外返回，多线程嗅探/解码不受这个锁影响正确性。
    """

    def __init__(self, path: str | Path):
        self._fd = os.open(path, _OPEN_FLAGS)
        self._size = os.fstat(self._fd).st_size
        self._closed = False
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        return self._size

    def _read_some(self, size: int, offset: int) -> bytes:
        """在 offset 处至多读 size 字节（允许短读，调用方循环补齐）。"""
        if _PREAD is not None:
            return _PREAD(self._fd, size, offset)
        with self._lock:
            os.lseek(self._fd, offset, os.SEEK_SET)
            return os.read(self._fd, size)

    def read_at(self, offset: int, size: int) -> bytes:
        if size <= 0:
            return b""
        chunks = []
        got = 0
        while got < size:
            chunk = self._read_some(size - got, offset + got)
            if not chunk:
                break
            chunks.append(chunk)
            got += len(chunk)
        return b"".join(chunks)

    def copy_to(self, offset: int, length: int, out: BinaryIO) -> None:
        """把 [offset, offset+length) 分块拷贝到 out（保存大包时用）。"""
        done = 0
        while done < length:
            chunk = self._read_some(min(_CHUNK, length - done),
                                    offset + done)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            os.close(self._fd)
