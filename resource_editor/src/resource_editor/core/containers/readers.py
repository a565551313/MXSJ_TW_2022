"""随机读抽象：惰性打开资源包时只读目录，条目负载按需读取。

* :class:`FileReader` 用 ``os.pread`` 按偏移读，不把整文件载入内存，
  1GB 级资源包也只占条目数级别的内存；pread 无共享文件指针，线程安全。
* :class:`BytesReader` 服务于内存中的字节（测试与合成包）。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO, Protocol

_CHUNK = 1024 * 1024


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
    """按偏移读取磁盘文件，不整文件载入内存。"""

    def __init__(self, path: str | Path):
        self._fd = os.open(path, os.O_RDONLY)
        self._size = os.fstat(self._fd).st_size
        self._closed = False

    @property
    def size(self) -> int:
        return self._size

    def read_at(self, offset: int, size: int) -> bytes:
        if size <= 0:
            return b""
        chunks = []
        got = 0
        while got < size:
            chunk = os.pread(self._fd, size - got, offset + got)
            if not chunk:
                break
            chunks.append(chunk)
            got += len(chunk)
        return b"".join(chunks)

    def copy_to(self, offset: int, length: int, out: BinaryIO) -> None:
        """把 [offset, offset+length) 分块拷贝到 out（保存大包时用）。"""
        done = 0
        while done < length:
            chunk = os.pread(self._fd, min(_CHUNK, length - done),
                             offset + done)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            os.close(self._fd)
