"""下拉候选只来自真实现存条目；路径校验不需要 Qt。"""

from __future__ import annotations

import unittest
from unittest import mock

from resource_editor.core.containers import fls0slf, flsdata
from resource_editor.core.model.document import PackDocument
from resource_editor.core.resource_paths import validate_resource_path


class TestResourcePaths(unittest.TestCase):
    def test_normalize_and_reject_non_resource_paths(self):
        self.assertEqual(validate_resource_path(" ui/image.png "), "ui\\image.png")
        for path in [
            "",
            "/image.png",
            "C:\\image.png",
            "C:image.png",
            "../image.png",
            "ui//image.png",
            "ui/./image.png",
            "a\x00.png",
            "😀.png",
        ]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_resource_path(path)

    def test_0slf_only_known_existing_excludes_deleted_and_unknown(self):
        doc = PackDocument.from_bytes(
            fls0slf.build(
                [b"A", b"B", b"C"],
                [fls0slf.EntryMeta(entry_id=i + 100, r1=7) for i in range(3)],
            )
        )
        with mock.patch.object(doc, "resolve_names"):
            doc._names = {0: "ui/a.png", 1: "ui/b.png"}
            self.assertEqual(doc.known_resource_paths(), ["ui/a.png", "ui/b.png"])
            doc.delete_entry(0)
            self.assertEqual(doc.known_resource_paths(), ["ui/b.png"])
            doc.add_entry_for_path(b"NEW", "ui/new.png")
            self.assertEqual(doc.known_resource_paths(), ["ui/b.png", "ui/new.png"])
            doc.history.undo()
            self.assertEqual(doc.known_resource_paths(), ["ui/b.png"])
        doc.archive.close()

    def test_flsdata_excludes_directories(self):
        archive = flsdata.FlsDataArchive(
            header=b"FLS\0" + bytes(60),
            payloads=[],
            metas=[
                flsdata.EntryMeta(name="folder/"),
                flsdata.EntryMeta(name="folder/a.bin"),
            ],
        )
        doc = PackDocument.from_bytes(
            flsdata.build(archive, [b"", flsdata.deflate(b"A")])
        )
        self.assertEqual(doc.known_resource_paths(), ["folder/a.bin"])
        doc.archive.close()
