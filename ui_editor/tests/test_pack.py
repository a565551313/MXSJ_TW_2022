"""0SLF index integrity tests."""

from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.errors import PackError  # noqa: E402
from ui_editor.core.mxhash import mx_hash  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402

_MASK = 0xFFFFFFFF


def _record(index: int, entry_id: int, r1: int, length: int,
            offset: int) -> bytes:
    r2 = (((r1 * entry_id + 0x0DF25E) & _MASK) ^ length) & _MASK
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & _MASK)
           ^ offset) & _MASK
    return struct.pack("<IIII", entry_id, r1, r2, r3)


def _pack_with_duplicate_id() -> bytes:
    payload = b"ab"
    entry_id = mx_hash(b"duplicate/a.png")
    offset = 12
    directory_offset = offset + len(payload) * 2
    header = b"0SLF" + struct.pack("<II", 2, directory_offset)
    records = b"".join(
        _record(index, entry_id, 12345, len(payload), offset + index * 2)
        for index in range(2)
    )
    return header + payload + payload + records


class TestFlsPackIntegrity(unittest.TestCase):
    def test_duplicate_entry_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.fls"
            path.write_bytes(_pack_with_duplicate_id())
            with self.assertRaises(PackError):
                FlsPack(path)


if __name__ == "__main__":
    unittest.main()
