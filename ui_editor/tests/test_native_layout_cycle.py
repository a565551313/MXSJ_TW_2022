"""New/imported/edited layouts use native storage throughout normal save cycles."""

import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.errors import PackError
from ui_editor.core.model import LayoutDocument
from ui_editor.core.mxhash import mx_hash
from ui_editor.core.pack import FlsPack


def native_read(stored, path):
    value = ((mx_hash(path.encode("gbk")) + 0x9234AB) & 0xFFFFFFFF) ^ 0x937F4912
    key = struct.pack("<I", value)
    return bytes(value ^ key[i % 4] for i, value in enumerate(stored))


def layout(width):
    return dlg_codec.dump_bytes(
        [
            {
                "sName": "root",
                "sWidgetType": "CBox",
                "iWidth": width,
                "iHeight": 120,
                "sText": "測試標題",
                "lChildren": [],
            }
        ]
    )


class TestNativeLayoutCycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "base.fls"
        self.base = pack_build.build_archive([pack_build.RawEntry(1, 12345, b"KEEP")])
        self.source.write_bytes(self.base)

    def test_future_layout_create_reopen_edit_and_save_again(self):
        path = "future/new_screen.dlg"
        first, second = self.root / "first.fls", self.root / "second.fls"
        original = layout(300)
        pack_build.patch_pack_copy(
            self.source, path, original, first, allow_create=True
        )
        with FlsPack(first) as pack:
            stored = pack.read_named(path)
            self.assertNotEqual(stored, original)
            self.assertEqual(native_read(stored, path), original)
            dictionaries, md5 = dlg_codec.parse_bytes(
                pack_build.unpack_packed_text(stored)
            )
        doc = LayoutDocument.from_dicts(dictionaries, md5)
        doc.roots[0].props["iWidth"] = 842
        edited = dlg_codec.dump_bytes(doc.to_dicts())
        pack_build.patch_pack_copy(first, path, edited, second)
        with FlsPack(second) as pack:
            self.assertEqual(native_read(pack.read_named(path), path), edited)
            self.assertEqual(pack.read_id(1), b"KEEP")
        self.assertEqual(self.source.read_bytes(), self.base)
        with FlsPack(first) as pack:
            self.assertEqual(native_read(pack.read_named(path), path), original)

    def test_existing_plaintext_and_wrong_key_are_migrated_when_saved(self):
        path = "login/regform.dlg"
        original = layout(320)
        for key in (b"\0" * 4, b"BAD!"):
            self.source.write_bytes(
                pack_build.build_archive(
                    [
                        pack_build.RawEntry(1, 12345, b"KEEP"),
                        pack_build.RawEntry(
                            mx_hash(path.encode()),
                            2468,
                            bytes(
                                value ^ key[i % 4] for i, value in enumerate(original)
                            ),
                        ),
                    ]
                )
            )
            unchanged_source = self.source.read_bytes()
            output = self.root / "corrected.fls"
            pack_build.patch_pack_copy(self.source, path, original, output)
            with FlsPack(output) as pack:
                self.assertEqual(native_read(pack.read_named(path), path), original)
                self.assertEqual(pack.read_id(1), b"KEEP")
            self.assertEqual(self.source.read_bytes(), unchanged_source)

    def test_rebuild_fallback_also_uses_native_cipher(self):
        path = "future/rebuild.dlg"
        output = self.root / "rebuilt.fls"
        with patch.object(
            pack_build,
            "patch_raw_entry_in_file",
            side_effect=pack_build._RebuildNeeded("synthetic fallback"),
        ):
            pack_build.patch_pack_copy(
                self.source, path, layout(40), output, allow_create=True
            )
        with FlsPack(output) as pack:
            self.assertEqual(native_read(pack.read_named(path), path), layout(40))

    def test_native_readback_rejects_self_consistent_wrong_key_output(self):
        path = "future/validation.dlg"
        output = self.root / "out.fls"
        output.write_bytes(b"PREVIOUS OUTPUT")
        original_create = pack_build._create_layout_copy

        def broken_writer(src, candidate, path, plain, extras):
            result = original_create(src, candidate, path, plain, extras)
            # Simulate the old bug. Its own guessed-header reader can still parse this!
            pack_build.patch_raw_entry_in_file(candidate, mx_hash(path.encode()), plain)
            return result

        with patch.object(pack_build, "_create_layout_copy", side_effect=broken_writer):
            with self.assertRaises(PackError):
                pack_build.patch_pack_copy(
                    self.source, path, layout(40), output, allow_create=True
                )
        self.assertEqual(output.read_bytes(), b"PREVIOUS OUTPUT")
        self.assertEqual(self.source.read_bytes(), self.base)

    def test_native_input_is_not_double_encrypted(self):
        from ui_editor.core.native_layout import encode_layout

        path = "future/native_input.dlg"
        blob = layout(400)
        encoded = encode_layout(blob, mx_hash(path.encode()))
        output = self.root / "native_input.fls"
        pack_build.patch_pack_copy(
            self.source, path, encoded, output, allow_create=True
        )
        with FlsPack(output) as pack:
            self.assertEqual(pack.read_named(path), encoded)
            self.assertEqual(native_read(pack.read_named(path), path), blob)

    def test_extra_image_entry_cannot_bypass_layout_encoder(self):
        output = self.root / "extras.fls"
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy(
                self.source,
                "future/main.dlg",
                layout(400),
                output,
                extra_entries={"future/bypass.dlg": layout(401)},
                allow_create=True,
            )
        self.assertFalse(output.exists())
        self.assertEqual(self.source.read_bytes(), self.base)

    def test_native_key_vectors_and_case_separator_equivalence(self):
        from ui_editor.core.native_layout import key_for_path

        self.assertEqual(key_for_path("login/regterms.dlg").hex(), "a9bd00b5")
        self.assertEqual(key_for_path("login/regform.dlg").hex(), "f94b3e60")
        self.assertEqual(
            key_for_path("login/regform.dlg"), key_for_path("LOGIN\\REGFORM.DLG")
        )
        for path in ("C:/bad.dlg", "../bad.dlg", "future/\U0001f600.dlg"):
            with self.assertRaises(ValueError):
                key_for_path(path)


if __name__ == "__main__":
    unittest.main()
