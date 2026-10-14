"""布局导入与新增包条目：临时合成包，不触碰客户端原包。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.errors import DlgError, PackError
from ui_editor.core.layout_import import prepare_layout_import, validate_layout_path
from ui_editor.core.mxhash import mx_hash
from ui_editor.core.pack import FlsPack


def layout(title="Old"):
    return [
        {"sWidgetType": "CMainFrame", "sName": "root", "sTitle": title, "lChildren": []}
    ]


def raw(name, data):
    entry_id = mx_hash(name.encode("gbk"))
    return pack_build.RawEntry(entry_id, pack_build.fresh_r1(entry_id), data)


class TestLayoutImport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.src = Path(self.temp.name) / "source.fls"
        self.out = Path(self.temp.name) / "new.fls"
        self.old = dlg_codec.dump_bytes(layout())
        self.new = dlg_codec.dump_bytes(layout("New"))
        self.original = pack_build.build_archive(
            [raw("dialog/a.dlg", self.old), raw("image/keep.bin", b"KEEP")]
        )
        self.src.write_bytes(self.original)

    def test_path_normalize_and_reject(self):
        self.assertEqual(validate_layout_path(" login\\测试.dlg "), "login/测试.dlg")
        for path in [
            "",
            "a.txt",
            "/a.dlg",
            "C:/a.dlg",
            "C:a.dlg",
            "../a.dlg",
            "x//a.dlg",
            "x/./a.dlg",
            "a\x00.dlg",
            "x:a.dlg",
            "😀.dlg",
        ]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_layout_path(path)

    def test_new_and_replacement_baselines(self):
        with FlsPack(self.src) as pack:
            doc, replacing = prepare_layout_import(pack, "new/a.dlg", self.new)
            self.assertFalse(replacing)
            self.assertTrue(doc.pending_pack_import)
            self.assertTrue(doc.dirty)
            self.assertTrue(doc.changes())
            doc, replacing = prepare_layout_import(pack, "dialog/a.dlg", self.new)
            self.assertTrue(replacing)
            self.assertTrue(any(change.field == "sTitle" for change in doc.changes()))
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_reject_non_layout_and_unsafe_source(self):
        with FlsPack(self.src) as pack:
            with self.assertRaises(DlgError):
                prepare_layout_import(pack, "image/keep.bin.dlg", b"UI_INFO = [f()]")
        other = Path(self.temp.name) / "other.fls"
        other.write_bytes(pack_build.build_archive([raw("bad/a.dlg", b"BINARY")]))
        with FlsPack(other) as pack, self.assertRaises(PackError):
            prepare_layout_import(pack, "bad/a.dlg", self.new)

    def test_encoding_check(self):
        bad = layout()
        bad[0]["sTitle"] = "😀"
        with FlsPack(self.src) as pack, self.assertRaises(ValueError):
            prepare_layout_import(pack, "new/a.dlg", dlg_codec.dump_bytes(bad))

    def test_missing_still_rejected_by_default(self):
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(self.src, "new/a.dlg", self.new, self.out)
        self.assertFalse(self.out.exists())

    def test_add_readback_sorted_seeds_and_unchanged_original(self):
        info = pack_build.patch_pack_copy(
            self.src,
            "new/a.dlg",
            self.new,
            self.out,
            allow_create=True,
            extra_entries={"image/new.bin": b"NEW"},
        )
        self.assertTrue(info["layout_added"])
        self.assertEqual(info["images_added"], ["image/new.bin"])
        with FlsPack(self.src) as before, FlsPack(self.out) as after:
            self.assertEqual(after.count, before.count + 2)
            self.assertEqual(after.entry_ids, sorted(after.entry_ids))
            for entry_id in before.entry_ids:
                self.assertEqual(before.read_id(entry_id), after.read_id(entry_id))
            self.assertEqual(
                dlg_codec.parse_bytes(
                    pack_build.unpack_packed_text(after.read_named("new/a.dlg"))
                )[0],
                layout("New"),
            )
        rows = pack_build.parse_archive(self.out.read_bytes())
        self.assertTrue(all(row.r1 for row in rows))
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_empty_archive_remains_rejected(self):
        self.src.write_bytes(pack_build.build_archive([]))
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src, "new/a.dlg", self.new, self.out, allow_create=True
            )
        self.assertFalse(self.out.exists())

    def test_rebuild_fallback_add(self):
        with mock.patch.object(
            pack_build,
            "patch_raw_entry_in_file",
            side_effect=pack_build._RebuildNeeded("fixture"),
        ):
            info = pack_build.patch_pack_copy(
                self.src,
                "new/a.dlg",
                self.new,
                self.out,
                allow_create=True,
                extra_entries={"image/keep.bin": b"REPLACED"},
            )
        self.assertEqual(info["mode"], "rebuild")
        with FlsPack(self.out) as after:
            self.assertEqual(after.read_named("image/keep.bin"), b"REPLACED")
            self.assertEqual(after.read_named("new/a.dlg"), self.new)

    def test_actual_zero_seed_rebuild_and_unchanged_payload(self):
        entry_id = mx_hash(b"image/a.bin")
        payload = b"KEEP"
        head = pack_build._HEADER.pack(b"0SLF", 1, 12 + len(payload))
        r2 = 0x0DF25E ^ len(payload)
        r3 = 0x0D59D16C ^ 12
        self.src.write_bytes(
            head + payload + pack_build._RECORD.pack(entry_id, 0, r2, r3)
        )
        info = pack_build.patch_pack_copy(
            self.src, "new/a.dlg", self.new, self.out, allow_create=True
        )
        self.assertEqual(info["mode"], "rebuild")
        with FlsPack(self.out) as after:
            self.assertEqual(after.read_named("image/a.bin"), payload)
        self.assertTrue(
            all(row.r1 for row in pack_build.parse_archive(self.out.read_bytes()))
        )

    def test_sequential_imports_continue_from_new_package(self):
        pack_build.patch_pack_copy(
            self.src, "new/a.dlg", self.new, self.out, allow_create=True
        )
        second = self.out.with_name("second.fls")
        pack_build.patch_pack_copy(
            self.out, "new/b.dlg", self.old, second, allow_create=True
        )
        with FlsPack(second) as after:
            self.assertEqual(after.count, 4)
            self.assertEqual(after.read_named("new/a.dlg"), self.new)
            self.assertEqual(after.read_named("new/b.dlg"), self.old)

    def test_verified_failure_keeps_existing_output_and_no_temp(self):
        self.out.write_bytes(b"previous output")
        with mock.patch.object(
            pack_build, "_verify_copy", side_effect=PackError("readback failed")
        ):
            with self.assertRaises(PackError):
                pack_build.patch_pack_copy(
                    self.src, "new/a.dlg", self.new, self.out, allow_create=True
                )
        self.assertEqual(self.out.read_bytes(), b"previous output")
        self.assertFalse(list(self.out.parent.glob("*.tmp")))
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_protect_source_and_extra_hash_collision(self):
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src, "new/a.dlg", self.new, self.src, allow_create=True
            )
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.src,
                "new/a.dlg",
                self.new,
                self.out,
                allow_create=True,
                extra_entries={"NEW\\A.DLG": b"collision"},
            )
        self.assertFalse(self.out.exists())
