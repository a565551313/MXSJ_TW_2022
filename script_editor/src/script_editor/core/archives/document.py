"""Lazy read-only package workspace. An index is NOT verified module source."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..errors import ContainerError
from . import fls0slf, flsdata
from .readers import FileReader


@dataclass(frozen=True)
class Entry:
    index: int
    identity: str
    size: int
    directory: bool = False


class ArchiveDocument:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve(strict=True)
        self.reader = FileReader(self.path)
        self._revision = self.reader.revision
        self._fingerprint = None
        try:
            magic = self.reader.read_at(0, 4)
            if magic == fls0slf.MAGIC:
                self.kind = "0slf"
                self.vm = "py25"
                self.index = fls0slf.parse_index(self.reader)
                self.entries = [
                    Entry(i, f"{m.entry_id:08X}", span.length)
                    for i, (m, span) in enumerate(
                        zip(self.index.metas, self.index.spans, strict=True)
                    )
                ]
            elif magic == flsdata.MAGIC:
                self.kind = "flsdata"
                self.vm = "py27"
                self.index = flsdata.parse_index(self.reader)
                self.entries = [
                    Entry(i, m.name, s.csize, m.is_dir)
                    for i, (m, s) in enumerate(
                        zip(self.index.metas, self.index.spans, strict=True)
                    )
                ]
            else:
                raise ContainerError("不支持的容器头；不是script/data FLS")
            self._assert_unchanged()
        except Exception:
            self.reader.close()
            raise

    def _assert_unchanged(self):
        info = self.path.stat()
        current = (
            info.st_dev,
            info.st_ino,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        )
        if current != self._revision or self.reader.revision != self._revision:
            raise ContainerError(
                "源包打开后发生变化或被替换，请重新打开；拒绝使用旧索引"
            )

    def fingerprint(self) -> str:
        self._assert_unchanged()
        if self._fingerprint is None:
            digest = hashlib.sha256()
            for offset in range(0, self.reader.size, 1024 * 1024):
                digest.update(
                    self.reader.read_at(
                        offset, min(1024 * 1024, self.reader.size - offset)
                    )
                )
            self._assert_unchanged()
            self._fingerprint = digest.hexdigest()
        return self._fingerprint

    def read_stored(self, index: int) -> bytes:
        self._assert_unchanged()
        if not 0 <= index < len(self.entries):
            raise IndexError(index)
        span = self.index.spans[index]
        if self.kind == "0slf":
            return self.reader.read_at(span.offset, span.length)
        return self.reader.read_at(span.data_offset, span.csize)

    def entry_metadata(self, index: int) -> dict:
        self._assert_unchanged()
        if not 0 <= index < len(self.entries):
            raise IndexError(index)
        entry = self.entries[index]
        result = {
            "index": index,
            "identity": entry.identity,
            "vm": self.vm,
            "stored_bytes": entry.size,
            "source_status": "无可信源码 / 只读",
        }
        if self.kind == "0slf":
            m = self.index.metas[index]
            result["flags"] = ((m.entry_id * 0x2F05B + 0x16B38) & 0xFFFFFFFF) ^ m.r1
        else:
            result["crc32"] = self.index.spans[index].crc
            result["directory"] = entry.directory
        return result

    def close(self):
        self.reader.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
