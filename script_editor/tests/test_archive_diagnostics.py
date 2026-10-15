"""Read-only report and Windows seek/read regression; no Qt/compiler needed."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fixtures import script_bytes

from script_editor.core.archives import readers
from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.errors import ContainerError

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "archive_diagnosis", ROOT / "diagnose_archive.py"
)
diagnosis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnosis)


class ArchiveDiagnosticTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "script.fls"
        self.path.write_bytes(script_bytes(b"SECRET-PAYLOAD-NOT-IN-REPORT"))

    def test_valid_report_retains_only_header_directory_hashes_not_payload(self):
        original = self.path.read_bytes()
        report = diagnosis.inspect_archive(self.path)
        self.assertEqual(report["status"], "bounds-pass")
        self.assertEqual(report["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(report["invalid_count"], 0)
        self.assertTrue(report["stable_during_diagnostic"])
        self.assertNotIn("SECRET-PAYLOAD", json.dumps(report))
        self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_first_payload_has_exact_offsets_and_no_repair(self):
        raw = bytearray(self.path.read_bytes())
        directory = struct.unpack_from("<I", raw, 8)[0]
        struct.pack_into("<I", raw, directory + 12, 0xD59D16C ^ directory)
        self.path.write_bytes(raw)
        report = diagnosis.inspect_archive(self.path)
        self.assertEqual(report["status"], "payload-bounds-failed")
        self.assertEqual(report["invalid_records"][0]["index"], 0)
        self.assertEqual(report["invalid_records"][0]["offset"], directory)
        self.assertEqual(self.path.read_bytes(), raw)
        with self.assertRaisesRegex(ContainerError, f"目录范围=\\[{directory},"):
            ArchiveDocument(self.path)

    def test_truncated_directory_not_confused_with_bad_payload(self):
        self.path.write_bytes(self.path.read_bytes()[:-1])
        self.assertEqual(
            diagnosis.inspect_archive(self.path)["status"], "directory-outside-file"
        )

    def test_wrong_magic_and_short_header(self):
        for data in (b"", b"0SLF", b"FLS\0" + bytes(20)):
            with self.subTest(data=data):
                self.path.write_bytes(data)
                self.assertEqual(
                    diagnosis.inspect_archive(self.path)["status"], "not-a-0slf-header"
                )

    def test_extreme_count_is_bounded_without_reading_huge_directory(self):
        self.path.write_bytes(struct.pack("<4sII", b"0SLF", 100_000_000, 12))
        self.assertEqual(
            diagnosis.inspect_archive(self.path)["status"],
            "entry-count-outside-diagnostic-limit",
        )

    def test_windows_seek_read_path_preserves_binary_payload(self):
        payload = b"\x1a\r\n\x00\xff" * 64
        self.path.write_bytes(script_bytes(payload))
        with patch.object(readers, "_PREAD", None):
            with ArchiveDocument(self.path) as doc:
                self.assertEqual(doc.read_stored(0), payload)
        self.assertEqual(diagnosis.inspect_archive(self.path)["status"], "bounds-pass")
