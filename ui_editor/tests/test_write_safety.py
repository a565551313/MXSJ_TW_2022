"""写包安全回归：仅操作临时合成包，不依赖 Qt 或真实客户端。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.errors import PackError
from ui_editor.core.mxhash import mx_hash


class TestWriteSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "source.fls"
        self.out = self.root / "new.fls"
        self.path = "login/test.dlg"
        self.old = dlg_codec.dump_bytes([{"sName": "old", "iWidth": 100}])
        self.new = dlg_codec.dump_bytes([{"sName": "new", "iWidth": 200}])
        self.raw = pack_build.build_archive([
            pack_build.RawEntry(mx_hash(self.path.encode("gbk")), 7, self.old),
            pack_build.RawEntry(mx_hash(b"untouched.bin"), 9, b"untouched"),
        ])
        self.src.write_bytes(self.raw)

    def test_rejects_source_and_normalized_alias(self):
        for target in [self.src, self.root / "." / self.src.name]:
            with self.subTest(target=target), self.assertRaises(PackError):
                pack_build.patch_pack_copy(self.src, self.path, self.new, target)
            self.assertEqual(self.src.read_bytes(), self.raw)

    def test_rejects_hardlink_without_truncating_source(self):
        os.link(self.src, self.out)
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertEqual(self.out.read_bytes(), self.raw)

    def test_rejects_symlink_without_touching_source(self):
        try:
            self.out.symlink_to(self.src)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_failure_does_not_replace_existing_output(self):
        self.out.write_bytes(b"existing output")
        with mock.patch.object(
            pack_build, "patch_dlg_entry_in_file", side_effect=PackError("failed")
        ), self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertEqual(self.out.read_bytes(), b"existing output")
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["new.fls", "source.fls"])

    def test_copy_preserves_source_and_untouched_payload(self):
        pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertEqual(self.src.read_bytes(), self.raw)
        entries = {e.entry_id: e.stored
                   for e in pack_build.parse_archive(self.out.read_bytes())}
        self.assertEqual(entries[mx_hash(b"untouched.bin")], b"untouched")
        self.assertEqual(pack_build.unpack_packed_text(
            entries[mx_hash(self.path.encode("gbk"))]), self.new)

    def test_rejects_other_mounted_source(self):
        other = self.root / "other.fls"
        other.write_bytes(self.raw)
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src, self.path, self.new, other, protected_paths=[other])
        self.assertEqual(other.read_bytes(), self.raw)

    def test_detects_corruption_even_when_span_is_unchanged(self):
        self.out.write_bytes(b"old output")
        original_patch = pack_build.patch_dlg_entry_in_file

        def corrupt(path, res_path, plain):
            info = original_patch(path, res_path, plain)
            with pack_build.FlsPack(path) as pack:
                offset, _ = pack.span_of(mx_hash(b"untouched.bin"))
            with open(path, "r+b") as fh:
                fh.seek(offset)
                fh.write(b"CORRUPTED")
            return info

        with mock.patch.object(pack_build, "patch_dlg_entry_in_file", corrupt), \
                self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertEqual(self.out.read_bytes(), b"old output")
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_partial_extra_failure_is_not_published(self):
        self.out.write_bytes(b"old output")
        original_patch = pack_build.patch_raw_entry_in_file
        calls = 0

        def fail_second(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PackError("second extra failed")
            return original_patch(*args)

        with mock.patch.object(pack_build, "patch_raw_entry_in_file", fail_second), \
                self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src, self.path, self.new, self.out,
                extra_entries={"a.bin": b"A", "b.bin": b"B"})
        self.assertEqual(self.out.read_bytes(), b"old output")
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["new.fls", "source.fls"])

    def test_publish_failure_cleans_temporary_file(self):
        with mock.patch.object(pack_build.os, "replace",
                               side_effect=PermissionError("locked")), \
                self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, self.path, self.new, self.out)
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.root.iterdir()), [self.src])

    def test_layout_cannot_be_overwritten_by_extra(self):
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src, self.path, self.new, self.out,
                extra_entries={self.path: b"not a layout"})
        self.assertFalse(self.out.exists())
        self.assertEqual(self.src.read_bytes(), self.raw)
