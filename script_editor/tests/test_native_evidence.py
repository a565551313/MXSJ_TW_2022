"""Optional independent PE-dispatch check; only stdlib, no DLL/module loading."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import unittest
from pathlib import Path

from script_editor.core.vm.tables import PY27_MAP


class DispatchEvidence(unittest.TestCase):
    def test_snapshot_numbers_match_the_strict_table(self):
        record = json.loads(
            (Path(__file__).parent / "evidence" / "py27_dispatch.json").read_text(
                encoding="utf-8"
            )
        )
        for row in record["rows"]:
            if row["standard_py27"] is not None:
                self.assertEqual(PY27_MAP[row["native"]], row["standard_py27"])

    def test_current_dll_dispatch_without_executing_it(self):
        location = os.environ.get("MXSJ_M2_REPO")
        if not location:
            self.skipTest("opt-in read-only DLL evidence input required")
        record = json.loads(
            (Path(__file__).parent / "evidence" / "py27_dispatch.json").read_text(
                encoding="utf-8"
            )
        )
        data = (Path(location) / record["input"]["file"]).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), record["input"]["sha256"])
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        self.assertEqual(data[pe : pe + 4], b"PE\0\0")
        sections = struct.unpack_from("<H", data, pe + 6)[0]
        opt_size = struct.unpack_from("<H", data, pe + 20)[0]
        image_base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
        start = pe + 24 + opt_size
        segments = []
        for i in range(sections):
            size, rva, rawsize, rawoff = struct.unpack_from(
                "<IIII", data, start + i * 40 + 8
            )
            segments.append((rva, max(size, rawsize), rawoff))

        def read(rva, length):
            for base, size, raw in segments:
                if base <= rva and rva + length <= base + size:
                    return data[raw + rva - base : raw + rva - base + length]
            raise AssertionError("invalid RVA in evidence")

        index_table = int(record["index_table_rva"], 16)
        jump_table = int(record["jump_table_rva"], 16)
        for row in record["rows"]:
            index = read(index_table + row["native"], 1)[0]
            handler = struct.unpack("<I", read(jump_table + index * 4, 4))[0]
            self.assertEqual(index, row["index"])
            self.assertEqual(handler, int(row["handler"], 16))
            self.assertEqual(read(handler - image_base, 32).hex(), row["head_hex"])
