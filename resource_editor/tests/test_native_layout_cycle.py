"""Normal import/edit/save cycles must write native .dlg, not plaintext packages."""

import struct
import tempfile
import unittest
from pathlib import Path

from resource_editor.core.containers import fls0slf
from resource_editor.core.errors import SaveError
from resource_editor.core.model.document import PackDocument
from resource_editor.core.native_layout import encode_layout, plain_if_layout
from resource_editor.core.services.saver import save_document


def plain(width):
    # Mixed bytes are preserved, not reserialized or converted to Unicode text.
    return (
        b'# -*- coding: gbk -*-\n# user revision\nUI_INFO = [{"sName":"root",'
        b'"sWidgetType":"CBox","iWidth":'
        + str(width).encode()
        + b',"sText":"\\xbdT\\xa9w","lChildren":[]}]\n'
    )


def native_read(stored, entry_id):
    # Independent native formula, never infer a key from the output's header.
    key = struct.pack("<I", ((entry_id + 0x9234AB) & 0xFFFFFFFF) ^ 0x937F4912)
    return bytes(value ^ key[i % 4] for i, value in enumerate(stored))


class TestNativeLayoutCycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "base.fls"
        self.source.write_bytes(
            fls0slf.build([b"UNRELATED"], [fls0slf.EntryMeta(1, 12345)])
        )
        self.original = self.source.read_bytes()
        self.doc = PackDocument.open(self.source)
        self.addCleanup(self.doc.close)

    def test_future_layout_import_reopen_modify_save_again(self):
        # Arbitrary future layout, not a special case for registration paths.
        path = "future/new_window.dlg"
        index = self.doc.add_entry_for_path(plain(300), path)
        entry_id = self.doc.archive.extra_metas[index].entry_id
        self.assertEqual(native_read(self.doc.stored(index), entry_id), plain(300))
        first = self.root / "first.fls"
        self.assertTrue(save_document(self.doc, first).ok)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.doc.close()
        self.doc = PackDocument.open(first)
        self.addCleanup(self.doc.close)
        index = self.doc.index_by_path(path)
        self.doc.replace_for_path(index, plain(841), path)
        second = self.root / "second.fls"
        self.assertTrue(save_document(self.doc, second).ok)
        index = self.doc.index_by_path(path)
        self.assertEqual(native_read(self.doc.stored(index), entry_id), plain(841))
        self.assertEqual(
            self.doc.stored(
                next(
                    i
                    for i, meta in enumerate(self.doc.archive.extra_metas)
                    if meta.entry_id == 1
                )
            ),
            b"UNRELATED",
        )

    def test_plain_legacy_or_native_import_is_normalized(self):
        from resource_editor.core.mxhash import mx_hash

        path = "login/regform.dlg"
        entry_id = mx_hash(path.encode())
        blob = plain(304)
        legacy = bytes(value ^ b"BAD!"[i % 4] for i, value in enumerate(blob))
        for data in (blob, legacy, encode_layout(blob, entry_id)):
            index = self.doc.index_by_path(path)
            if index is None:
                index = self.doc.add_entry_for_path(data, path)
            else:
                self.doc.replace_for_path(index, data, path)
            self.assertEqual(native_read(self.doc.stored(index), entry_id), blob)

    def test_undo_redo_preserves_encoded_edit_history(self):
        path = "future/undo.dlg"
        index = self.doc.add_entry_for_path(plain(1), path)
        old = self.doc.stored(index)
        self.doc.replace_for_path(index, plain(2), path)
        new = self.doc.stored(index)
        self.assertTrue(self.doc.undo())
        self.assertEqual(self.doc.stored(index), old)
        self.assertTrue(self.doc.redo())
        self.assertEqual(self.doc.stored(index), new)

    def test_save_refuses_advanced_raw_plaintext_layout(self):
        path = "future/raw.dlg"
        index = self.doc.add_entry_for_path(plain(1), path)
        self.doc.replace_stored(index, plain(2))  # Explicit raw API bypasses encoder.
        output = self.root / "output.fls"
        output.write_bytes(b"EXISTING OUTPUT")
        with self.assertRaises(SaveError):
            save_document(self.doc, output)
        self.assertEqual(output.read_bytes(), b"EXISTING OUTPUT")
        self.doc.replace_stored(index, b"INVALID")
        with self.assertRaises(SaveError):
            save_document(self.doc, output)
        self.assertEqual(output.read_bytes(), b"EXISTING OUTPUT")
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(list(self.root.glob("*.tmp")))
        self.doc.replace_content(index, plain(2))
        self.assertTrue(save_document(self.doc, output).ok)

    def test_invalid_layout_and_unencodable_path_do_not_mutate(self):
        count = self.doc.count
        for data, path in (
            (b"INVALID", "new/no.dlg"),
            (plain(1), "new/\U0001f600.dlg"),
            (b"# -*- coding: gbk -*-\nUI_INFO=evil()\n", "new/call.dlg"),
        ):
            with self.assertRaises(ValueError):
                self.doc.add_entry_for_path(data, path)
            self.assertEqual(self.doc.count, count)
            self.assertFalse(self.doc.can_undo)

    def test_chinese_gbk_path_and_slash_alias_roundtrip(self):
        path = "界面/测试.dlg"
        index = self.doc.add_entry_for_path(plain(300), " 界面\\测试.dlg ")
        entry_id = self.doc.archive.extra_metas[index].entry_id
        self.doc.replace_for_path(index, plain(301), path)
        self.assertEqual(native_read(self.doc.stored(index), entry_id), plain(301))
        output = self.root / "chinese.fls"
        self.assertTrue(save_document(self.doc, output).ok)
        self.assertIsNotNone(self.doc.index_by_path(path))

    def test_nonlayout_resources_stay_opaque(self):
        data = b"opaque bytes # coding things"
        index = self.doc.add_entry_for_path(data, "new/data.bin")
        self.assertEqual(self.doc.stored(index), data)
        self.assertIsNone(plain_if_layout(data))
        text = b"# -*- coding: gbk -*-\nGENERIC_MODULE = 1\n"
        index = self.doc.add_entry_for_path(text, "new/module.py")
        self.doc.replace_content(index, text)
        self.assertEqual(self.doc.stored(index), text)
        self.assertIsNone(plain_if_layout(text))


if __name__ == "__main__":
    unittest.main()
