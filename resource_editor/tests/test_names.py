"""0SLF 真名识别：字典命中 .dlg、扒取其图片引用、未命中的回退序号。"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core import names  # noqa: E402
from resource_editor.core.containers import fls0slf  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.mxhash import mx_hash  # noqa: E402

DLG_PATH = "dialog/test.dlg"
IMG_REF = "combdialog4\\新登陸介面\\底板\\賬號輸入底\\底板800.png"
KEY = b"\x5a\xa5\x11\x7e"


def _dlg_stored() -> bytes:
    # 真实 .dlg 是类 JSON 文本：路径在双引号里、反斜杠转义双写
    escaped = IMG_REF.replace("\\", "\\\\")
    text = (
        "# -*- coding: gbk -*-\nUI_INFO = [\n"
        f'{{"sWidgetType": "CImage", "sFileName": "{escaped}"}}\n]\n'
    ).encode("gbk")
    return bytes(b ^ KEY[i & 3] for i, b in enumerate(text))


def _archive() -> tuple[bytes, list[bytes]]:
    payloads = [_dlg_stored(), b"\x89PNG\r\n\x1a\n" + b"x" * 32,
                b"\x00\x01\x02\x03"]
    metas = [
        fls0slf.EntryMeta(
            entry_id=mx_hash(DLG_PATH.encode("gbk")), r1=7),
        fls0slf.EntryMeta(
            entry_id=mx_hash(IMG_REF.encode("gbk")), r1=8),
        fls0slf.EntryMeta(entry_id=0xDEADBEEF, r1=9),
    ]
    return fls0slf.build(payloads, metas), payloads


class TestNamePrimitives(unittest.TestCase):
    def test_unpack_dlg_text_xor_and_plain(self):
        stored = _dlg_stored()
        plain = names.unpack_dlg_text(stored)
        self.assertIsNotNone(plain)
        assert plain is not None
        self.assertTrue(plain.startswith(b"# -*- coding: gbk -*-"))
        self.assertEqual(names.unpack_dlg_text(plain), plain)
        self.assertIsNone(names.unpack_dlg_text(b"\x89PNG garbage bytes"))

    def test_extract_resource_paths(self):
        plain = names.unpack_dlg_text(_dlg_stored())
        assert plain is not None
        self.assertEqual(names.extract_resource_paths(plain), [IMG_REF])
        self.assertEqual(
            names.extract_resource_paths("沒有路徑的純文字".encode("gbk")),
            [])

    def test_build_name_map_two_levels(self):
        _raw, payloads = _archive()
        ids = [mx_hash(DLG_PATH.encode("gbk")),
               mx_hash(IMG_REF.encode("gbk")), 0xDEADBEEF]
        result = names.build_name_map(
            ids, lambda i: payloads[i],
            known={ids[0]: DLG_PATH})
        self.assertEqual(result, {0: DLG_PATH, 1: IMG_REF})


class TestDocumentLabels(unittest.TestCase):
    def test_labels_with_patched_dictionary(self):
        raw, _payloads = _archive()
        known = {mx_hash(DLG_PATH.encode("gbk")): DLG_PATH}
        with mock.patch.object(names, "_KNOWN_CACHE", known):
            doc = PackDocument.from_bytes(raw)
            self.assertEqual(doc.resolve_names(), 2)
            self.assertEqual(doc.named_count, 2)
            self.assertEqual(doc.label(0), DLG_PATH)
            self.assertEqual(doc.label(1), IMG_REF)
            self.assertEqual(doc.label(2), "条目 2")  # 无名回退序号
            doc.close()

    def test_real_dictionary_misses_stay_numbered(self):
        raw, _payloads = _archive()
        doc = PackDocument.from_bytes(raw)
        self.assertEqual(doc.label(2), "条目 2")
        doc.close()


class TestPathImport(unittest.TestCase):
    """按路径导入：entry_id=路径哈希、立刻有真名、重名拒绝。"""

    NEW_PATH = "combdialog4\\新登陸介面\\我的新圖.png"

    def test_add_entry_for_path(self):
        raw, _payloads = _archive()
        doc = PackDocument.from_bytes(raw)
        index = doc.add_entry_for_path(b"\x89PNGdata", self.NEW_PATH)
        self.assertEqual(index, 3)
        # 编号必须是路径哈希，游戏才按名查得到
        self.assertEqual(doc.archive.extra_metas[index].entry_id,
                         mx_hash(self.NEW_PATH.encode("gbk")))
        self.assertEqual(doc.label(index), self.NEW_PATH)
        self.assertEqual(doc.true_name(index), self.NEW_PATH)
        self.assertEqual(doc.content(index), b"\x89PNGdata")
        self.assertEqual(doc.index_by_path(self.NEW_PATH), index)
        doc.close()

    def test_existing_path_rejected_and_lookup(self):
        raw, _payloads = _archive()
        doc = PackDocument.from_bytes(raw)
        # 包里原有的条目按路径也能查到（不依赖字典）
        self.assertEqual(doc.index_by_path(DLG_PATH), 0)
        with self.assertRaises(ValueError):
            doc.add_entry_for_path(b"x", DLG_PATH)
        self.assertIsNone(doc.index_by_path("nope/nothing.png"))
        doc.close()


if __name__ == "__main__":
    unittest.main()
