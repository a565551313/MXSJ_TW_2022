"""Read raw entries out of an MXSJ ``0SLF`` archive (``data/script.fls``).

Container layout, verified against the 24,454,082-byte ``script.fls`` of the TW
v2.27.2 client:

* ``0SLF`` magic at 0, ``u32`` entry count at 4 (5002 for ``script.fls``),
  ``u32`` directory offset at 8 (``0x173EB22``).
* The directory holds ``count`` 16-byte records of ``<IIII``
  ``(entry_id, r1, r2, r3)``.  The real payload offset and compressed length are
  **obfuscated** and recovered by a closed-form transform (``decode_directory``)
  that mixes the record with the entry index.
* The payload is zlib-compressed.  Decompressing yields a further **5-segment
  single-byte XOR** layer wrapping a Python 2.7 marshal code object.

Scope note — this module deliberately stops at the zlib layer.  Undoing the
5-segment XOR needs the heuristic boundary/key search implemented in
``tools/fls_batch_decoder.py``; duplicating that here would add risk without
helping the map editor.  Scene *names* therefore come from
:mod:`map_editor.client.scene_table`, while map geometry — the part the editor
actually edits — is read straight from the ``.map`` files.
"""
from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"0SLF"
MASK32 = 0xFFFFFFFF
DIR_RECORD_SIZE = 16


class FlsError(RuntimeError):
    """Raised when an ``0SLF`` archive cannot be read."""


@dataclass(frozen=True, slots=True)
class FlsRecord:
    index: int
    entry_id: int
    payload_offset: int
    compressed_length: int


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def decode_directory(index: int, raw: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Invert the directory obfuscation.

    Mirrors the transform used by ``tools/fls_batch_decoder.py``:
    ``f1`` is a scrambled id, ``f2`` the compressed length, ``f3`` the offset.
    """
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3


class FlsArchive:
    """Random access to the entries of one ``0SLF`` file."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        with self.path.open("rb") as fh:
            head = fh.read(12)
        if len(head) < 12 or head[:4] != MAGIC:
            raise FlsError(f"{self.path}: bad magic {head[:4]!r}, expected {MAGIC!r}")
        self.count = u32(head, 4)
        self.directory_offset = u32(head, 8)
        if not 0 < self.count < 1_000_000:
            raise FlsError(f"{self.path}: implausible entry count {self.count}")
        self._fh = self.path.open("rb")

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> "FlsArchive":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def record(self, index: int) -> FlsRecord:
        if not 0 <= index < self.count:
            raise FlsError(f"entry {index} out of range (count={self.count})")
        self._fh.seek(self.directory_offset + index * DIR_RECORD_SIZE)
        raw = struct.unpack("<IIII", self._fh.read(DIR_RECORD_SIZE))
        _f1, clen, doff = decode_directory(index, raw)
        return FlsRecord(index, raw[0], doff, clen)

    def compressed(self, index: int) -> bytes:
        rec = self.record(index)
        self._fh.seek(rec.payload_offset)
        blob = self._fh.read(rec.compressed_length)
        if len(blob) != rec.compressed_length:
            raise FlsError(f"entry {index}: truncated payload")
        return blob

    def expanded(self, index: int) -> bytes:
        """zlib-decompressed entry body (still XOR-obfuscated, see module docstring)."""
        try:
            return zlib.decompress(self.compressed(index))
        except zlib.error as exc:
            raise FlsError(f"entry {index}: zlib failed: {exc}") from exc

    def summary(self) -> dict:
        return {"path": str(self.path), "magic": MAGIC.decode(),
                "entry_count": self.count,
                "directory_offset": self.directory_offset}


__all__ = ["FlsArchive", "FlsError", "FlsRecord", "MAGIC", "decode_directory", "u32"]
