"""Independent 0SLF layouts: table before, amid or after payloads.

The report replay uses ONLY the eight directory rows supplied by the user;
it is not the user's full 5002-entry archive or game-logic validation.
"""

from __future__ import annotations

import io
import struct
import tempfile
import unittest
from pathlib import Path

from fixtures import script_bytes

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.archives.fls0slf import parse, parse_index
from script_editor.core.archives.verify import envelope
from script_editor.core.archives.writer import write_script
from script_editor.core.errors import ContainerError

PAYLOADS = (b"module-zero", b"module-one\r\n\x1a", b"module-two")


def layout(directory_after):
    """Hand-encode sorted IDs, non-directory physical order and opaque bytes."""
    physical = (2, 0, 1)
    out = bytearray(struct.pack("<4sIII", b"0SLF", 3, 0, 0xCAFEBABE))
    out.extend(b"UNREFERENCED-OLD-BODY")
    offsets = {}
    for position in range(4):
        if position == directory_after:
            directory = len(out)
            out.extend(bytes(48))
        if position < 3:
            i = physical[position]
            offsets[i] = len(out)
            out.extend(PAYLOADS[i] + b"OPAQUE-GAP" + bytes([i]))
    out.extend(b"OPAQUE-TRAILER")
    struct.pack_into("<I", out, 8, directory)
    for i, payload in enumerate(PAYLOADS):
        entry_id, r1 = 100 + i, 17 + i
        r2 = ((entry_id * r1 + 0xDF25E) & 0xFFFFFFFF) ^ len(payload)
        r3 = ((r2 * i * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ offsets[i]
        struct.pack_into("<IIII", out, directory + i * 16, entry_id, r1, r2, r3)
    return bytes(out)


class ScriptLayoutTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source.fls"
        self.target = self.root / "new.fls"

    def exercise(self, position, changes):
        before = layout(position)
        self.source.write_bytes(before)
        with ArchiveDocument(self.source) as source:
            out = io.BytesIO()
            write_script(source, changes, out)
            self.target.write_bytes(out.getvalue())
            with ArchiveDocument(self.target) as result:
                envelope(source, result, changes)
                self.assertEqual(source.index.metas, result.index.metas)
                for i, payload in enumerate(PAYLOADS):
                    self.assertEqual(result.read_stored(i), changes.get(i, payload))
                self.assertEqual(
                    result.reader.size,
                    len(before)
                    + sum(
                        len(value) - len(PAYLOADS[i]) for i, value in changes.items()
                    ),
                )
                if not changes:
                    self.assertEqual(out.getvalue(), before)
        self.assertEqual(self.source.read_bytes(), before)

    def test_all_four_directory_positions_and_grow_shrink_multi_noop(self):
        for position in range(4):
            for changes in (
                {},
                {0: b"X"},
                {0: b"LONGER" * 30},
                {0: b"A", 1: b"B" * 50},
            ):
                with self.subTest(position=position, changes=changes):
                    self.exercise(position, changes)

    def test_table_at_header_end_is_valid_with_post_directory_payload(self):
        payload = b"stored"
        r2 = (17 * 4007 + 0xDF25E) ^ len(payload)
        data = struct.pack("<4sII", b"0SLF", 1, 12)
        data += struct.pack("<IIII", 4007, 17, r2, 0xD59D16C ^ 28) + payload
        self.assertEqual(parse(data).payloads, [payload])

    def test_recorded_eight_user_rows_are_valid_post_directory_spans(self):
        # Remaining 4994 rows/payloads were NOT included in the user's JSON.
        rows = bytes.fromhex(
            "4c9108004c910800382045671d912b0c"
            "3a0c09000c90850e5f237d9de9900e2a"
            "9bf10f003ff9081dc3b6d2a1f04b795b"
            "cbf81b004184912ba4c16b7744b03053"
            "562823001d37153a09eac15c39e90020"
            "d1113b00eba4a9483237aa984a13ae78"
            "db7a5900c7914457286e5e03b1117bec"
            "36855b00921cc36577d7f3fc1a787622"
        )

        class MetadataOnlyReader:
            size = 48_449_597

            def read_at(self, offset, size):
                if (offset, size) == (0, 12):
                    # Reduced row count for replay, offsets/bytes remain EXACT.
                    return struct.pack("<4sII", b"0SLF", 8, 24_184_785)
                if (offset, size) == (24_184_785, len(rows)):
                    return rows
                raise AssertionError("index parser must not read any payload")

        result = parse_index(MetadataOnlyReader())
        self.assertEqual(result.spans[0].offset, 24_264_817)
        self.assertEqual(result.spans[0].length, 214)
        for a, b in zip(result.spans, result.spans[1:], strict=False):
            self.assertEqual(a.offset + a.length, b.offset)
        self.assertEqual(result.spans[-1].offset + result.spans[-1].length, 24_321_613)

    def test_header_directory_overlap_and_actual_eof_overflow_remain_rejected(self):
        original = script_bytes(b"x" * 10)
        directory = struct.unpack_from("<I", original, 8)[0]
        table_end = directory + 16
        cases = (
            (0, 1),
            (11, 1),
            (directory - 1, 2),
            (directory, 1),
            (table_end - 1, 2),
            (len(original), 1),
            (0xFFFFFFFF, 16),
        )
        for offset, length in cases:
            with self.subTest(offset=offset, length=length):
                data = bytearray(original)
                r2 = (17 * 4007 + 0xDF25E) ^ length
                struct.pack_into("<II", data, directory + 8, r2, 0xD59D16C ^ offset)
                with self.assertRaises(ContainerError):
                    parse(bytes(data))

    def test_crossing_directory_with_valid_eof_range_still_rejected(self):
        data = bytearray(layout(1))
        directory = struct.unpack_from("<I", data, 8)[0]
        r2 = (17 * 100 + 0xDF25E) ^ 100
        struct.pack_into("<II", data, directory + 8, r2, 0xD59D16C ^ (directory - 1))
        data.extend(bytes(100))
        with self.assertRaises(ContainerError):
            parse(bytes(data))

    def test_envelope_rejects_opaque_gap_corruption_and_directory_relocation(self):
        self.source.write_bytes(layout(0))
        self.target.write_bytes(layout(3))
        with ArchiveDocument(self.source) as old, ArchiveDocument(self.target) as new:
            with self.assertRaises(ValueError):
                envelope(old, new, {})
        damaged = bytearray(layout(0))
        damaged[16] ^= 1  # Unreferenced prefix byte, NOT a directory/payload.
        self.target.write_bytes(damaged)
        with ArchiveDocument(self.source) as old, ArchiveDocument(self.target) as new:
            with self.assertRaises(ValueError):
                envelope(old, new, {})

    def test_post_directory_reopen_can_continue_editing_without_losing_first_edit(self):
        self.source.write_bytes(layout(0))
        with ArchiveDocument(self.source) as old:
            first = io.BytesIO()
            write_script(old, {0: b"FIRST-EDIT"}, first)
        self.target.write_bytes(first.getvalue())
        with ArchiveDocument(self.target) as saved:
            second = io.BytesIO()
            write_script(saved, {1: b"SECOND-EDIT"}, second)
            continued = self.root / "continued.fls"
            continued.write_bytes(second.getvalue())
            with ArchiveDocument(continued) as reopened:
                envelope(saved, reopened, {1: b"SECOND-EDIT"})
                self.assertEqual(reopened.read_stored(0), b"FIRST-EDIT")
                self.assertEqual(reopened.read_stored(1), b"SECOND-EDIT")
                self.assertEqual(reopened.read_stored(2), PAYLOADS[2])

    def test_native_build_post_directory_full_codec_readback(self):
        # The standard-compiler audit is explicitly mocked: this tests storage
        # and the independent native codec, NOT Windows/compiler execution.
        import hashlib
        import json
        import sys
        from unittest.mock import patch

        from native_fixtures import minimal_pyc, script_fixture

        from script_editor.core.compiler.runner import Compiler
        from script_editor.core.services.native_build import Replacement, build_package
        from script_editor.core.vm.py25.keys import load_profile

        before, catalog = script_fixture()
        count, old_directory = struct.unpack_from("<II", before, 4)
        table_size = count * 16
        out = bytearray(
            before[:16] + before[old_directory : old_directory + table_size]
        )
        out.extend(before[16:old_directory] + before[old_directory + table_size :])
        struct.pack_into("<I", out, 8, 16)
        for i in range(count):
            _, _, r2, r3 = struct.unpack_from("<IIII", before, old_directory + i * 16)
            old_offset = ((r2 * i * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ r3
            new_r3 = ((r2 * i * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ (
                old_offset + table_size
            )
            struct.pack_into("<I", out, 16 + i * 16 + 12, new_r3)
        self.source.write_bytes(out)
        pin = hashlib.sha256(out).hexdigest()
        catalog_path = self.root / "catalog.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        with ArchiveDocument(self.source) as archive:
            profile = load_profile(
                archive,
                0,
                catalog_path,
                archive_sha256=pin,
                catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
            )
            identity = archive.entries[0].identity
        expected = minimal_pyc("py25", 17)
        with patch("script_editor.core.services.native_build.audit_standard"):
            report = build_package(
                self.source,
                self.target,
                source_sha256=pin,
                replacements=(Replacement(0, identity, expected),),
                compiler=Compiler(
                    Path(sys.executable), "py25", "test-only", 64, "test"
                ),
                profiles={0: profile},
            )
        self.assertEqual(report.unchanged_entries, 2)
        self.assertEqual(self.source.read_bytes(), out)
        with ArchiveDocument(self.target) as result:
            self.assertEqual(struct.unpack("<I", result.reader.read_at(8, 4))[0], 16)
            self.assertTrue(all(span.offset >= 64 for span in result.index.spans))
