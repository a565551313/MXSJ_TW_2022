"""输出保护与保存后的真名关联回归（仅临时合成包，无 Qt）。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from resource_editor.core import names
from resource_editor.core.containers import fls0slf
from resource_editor.core.errors import SaveError
from resource_editor.core.model.document import PackDocument
from resource_editor.core.mxhash import mx_hash
from resource_editor.core.services import exporter
from resource_editor.core.services.saver import save_document


class TestOutputSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "source.fls"
        self.name = "source.fls"
        self.raw = fls0slf.build(
            [b"entry bytes"],
            [fls0slf.EntryMeta(entry_id=mx_hash(b"source.fls"), r1=7)],
        )
        self.src.write_bytes(self.raw)
        patcher = mock.patch.object(names, "_KNOWN_CACHE", {
            mx_hash(b"source.fls"): self.name,
        })
        patcher.start()
        self.addCleanup(patcher.stop)
        self.doc = PackDocument.open(self.src)
        self.addCleanup(self.doc.close)

    def test_export_cannot_overwrite_source(self):
        report = exporter.export_entries(self.doc, [0], self.root)
        self.assertEqual(report["failed"], [0])
        self.assertEqual(report["files"], 0)
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_export_rejects_hardlink(self):
        out = self.root / "out"
        out.mkdir()
        os.link(self.src, out / self.name)
        report = exporter.export_entries(self.doc, [0], out)
        self.assertEqual(report["failed"], [0])
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_export_cannot_escape_through_symlink_directory(self):
        out = self.root / "out"
        out.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (out / "folder").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        self.doc._slots[0].path_name = "folder/file.bin"
        report = exporter.export_entries(self.doc, [0], out)
        self.assertEqual(report["failed"], [0])
        self.assertEqual(list(outside.iterdir()), [])

    def test_single_export_cannot_follow_source_symlink(self):
        out = self.root / "out"
        out.mkdir()
        target = out / "source_0000.txt"
        try:
            target.symlink_to(self.src)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        with self.assertRaises(ValueError):
            exporter.export_entry(self.doc, 0, out)
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_save_rejects_source_and_hardlink(self):
        alias = self.root / "alias.fls"
        os.link(self.src, alias)
        self.doc.replace_content(0, b"new")
        for target in [self.src, alias]:
            with self.subTest(target=target), self.assertRaises(SaveError):
                save_document(self.doc, target)
            self.assertEqual(self.src.read_bytes(), self.raw)
            self.assertTrue(self.doc.is_modified)

    def test_export_to_new_directory_succeeds(self):
        out = self.root / "out"
        report = exporter.export_entries(self.doc, [0], out)
        self.assertEqual(report["failed"], [])
        self.assertEqual((out / self.name).read_bytes(), b"entry bytes")
        self.assertEqual(self.src.read_bytes(), self.raw)

    def test_save_failure_preserves_old_target_and_document(self):
        from resource_editor.core.services.verifier import VerifyReport

        target = self.root / "output.fls"
        target.write_bytes(b"old output")
        self.doc.replace_content(0, b"modified")
        with mock.patch(
            "resource_editor.core.services.saver.verify_saved",
            return_value=VerifyReport(ok=False, messages=["injected failure"]),
        ), self.assertRaises(SaveError):
            save_document(self.doc, target)
        self.assertEqual(target.read_bytes(), b"old output")
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertEqual(self.doc.content(0), b"modified")
        self.assertTrue(self.doc.is_modified)
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_save_uses_unique_temp_not_existing_source_alias(self):
        target = self.root / "output.fls"
        os.link(self.src, target.with_suffix(".fls.tmp"))
        save_document(self.doc, target)
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertEqual(target.read_bytes(), self.raw)
        with self.assertRaises(SaveError):
            save_document(self.doc, self.src)  # 历史基线仍受保护

    def test_save_rejects_other_open_pack(self):
        other = self.root / "other.fls"
        other.write_bytes(self.raw)
        with self.assertRaises(SaveError):
            save_document(self.doc, other, protected_paths=[other])
        self.assertEqual(other.read_bytes(), self.raw)

    def test_export_protects_other_pack_in_source_directory(self):
        other = self.root / "other.fls"
        other.write_bytes(self.raw)
        self.doc._slots[0].path_name = "other.fls"
        report = exporter.export_entries(self.doc, [0], self.root)
        self.assertEqual(report["failed"], [0])
        self.assertEqual(other.read_bytes(), self.raw)

    def test_export_preflights_all_sprite_frames(self):
        out = self.root / "out"
        out.mkdir()
        os.link(self.src, out / "sprite_f01.png")
        sprite = mock.Mock(frame_count=2)
        with self.assertRaises(ValueError):
            exporter.export_sprite_frames(sprite, out, "sprite", [self.src])
        sprite.render_frame.assert_not_called()
        self.assertFalse((out / "sprite_f00.png").exists())
        self.assertEqual(self.src.read_bytes(), self.raw)



class TestNamesAfterSave(unittest.TestCase):
    def test_failed_save_restores_order_and_edit_state(self):
        from resource_editor.core.services.verifier import VerifyReport

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.fls"
            source.write_bytes(fls0slf.build(
                [b"A", b"B"], [fls0slf.EntryMeta(entry_id=eid, r1=7)
                                 for eid in [0xFFFFFFFE, 0xFFFFFFFF]]))
            doc = PackDocument.open(source)
            self.addCleanup(doc.close)
            doc.replace_content(0, b"edited A")
            doc.add_entry_for_path(b"NEW", "new/image.bin")
            ids = [meta.entry_id for meta in doc.archive.extra_metas]
            payloads = [doc.content(i) for i in range(doc.count)]
            with mock.patch(
                "resource_editor.core.services.saver.verify_saved",
                return_value=VerifyReport(ok=False, messages=["failed"]),
            ), self.assertRaises(SaveError):
                save_document(doc, root / "output.fls")
            self.assertEqual([meta.entry_id for meta in doc.archive.extra_metas],
                             ids)
            self.assertEqual([doc.content(i) for i in range(doc.count)], payloads)
            self.assertTrue(doc.is_modified)
            self.assertEqual(doc.true_name(2), "new/image.bin")
            self.assertFalse((root / "output.fls").exists())

    def test_insert_before_named_entries_then_save_and_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = ["images/a.bin", "images/b.bin"]
            pairs = sorted((mx_hash(p.encode("gbk")), p, p.encode())
                           for p in paths)
            known = {entry_id: name for entry_id, name, _ in pairs}
            raw = fls0slf.build(
                [payload for _, _, payload in pairs],
                [fls0slf.EntryMeta(entry_id=eid, r1=7)
                 for eid, _, _ in pairs],
            )
            src = root / "src.fls"
            src.write_bytes(raw)
            with mock.patch.object(names, "_KNOWN_CACHE", known):
                doc = PackDocument.open(src)
                self.addCleanup(doc.close)
                doc.resolve_names()
                new_name = next(
                    f"new/{i}.bin" for i in range(100)
                    if mx_hash(f"new/{i}.bin".encode()) < pairs[0][0]
                )
                doc.add_entry_for_path(b"NEW", new_name)
                save_document(doc, root / "first.fls")
                expected = {name: payload for _, name, payload in pairs}
                expected[new_name] = b"NEW"
                for i in range(doc.count):
                    self.assertEqual(doc.content(i), expected[doc.true_name(i)])
                save_document(doc, root / "second.fls")
                report = exporter.export_entries(doc, list(range(doc.count)),
                                                 root / "export")
                self.assertEqual(report["failed"], [])
                for name, payload in expected.items():
                    self.assertEqual((root / "export" / name).read_bytes(), payload)
                self.assertEqual(src.read_bytes(), raw)
