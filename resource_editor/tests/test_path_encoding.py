"""路径编码策略：不可 GBK 编码的路径不得被静默替换（分析报告 P2-2）。

与 UI 编辑器同一处修正：``encode("gbk", "replace")`` 会把不可编码字符换成
``?`` 再算哈希，等于拿另一个路径去查/去写。现在统一走
:func:`resource_editor.core.mxhash.path_hash`（严格、失败抛错），
查询侧把「不可编码」视为「引擎同样寻址不到」。
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core import names  # noqa: E402
from resource_editor.core.containers import fls0slf  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.mxhash import mx_hash  # noqa: E402

BAD_NAME = "dialog4/bad\udcff.png"
#: UTF-8 存得下、GBK 编不出来的字符（字典文件里真实可能出现）
BAD_TEXT_NAME = "dialog4/bad\u2603.dlg"


def _make_0slf_doc() -> PackDocument:
    payloads = [b"hello", b"\x89PNG fake"]
    metas = [fls0slf.EntryMeta(entry_id=index, r1=0)
             for index in range(len(payloads))]
    return PackDocument.from_bytes(fls0slf.build(payloads, metas))


class KnownPathTests(unittest.TestCase):
    """随包路径字典：不可编码的条目跳过并留痕。"""

    def setUp(self):
        self.addCleanup(self._reset)
        self._reset()

    @staticmethod
    def _reset():
        names._KNOWN_CACHE = None
        names._UNENCODABLE.clear()

    def test_skips_unencodable_and_records_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = Path(tmp) / "known_paths.txt"
            catalog.write_text(
                "# 注释\ndialog4/good.dlg\n" + BAD_TEXT_NAME + "\n"
                "combdialog4/also_good.dlg\n", encoding="utf-8")
            original = names._catalog_file
            names._catalog_file = lambda: catalog
            try:
                table = names.known_path_hashes()
                skipped = names.unencodable_known_paths()
            finally:
                names._catalog_file = original
        self.assertEqual(sorted(table.values()),
                         ["combdialog4/also_good.dlg", "dialog4/good.dlg"])
        self.assertEqual(skipped, [BAD_TEXT_NAME])
        # 「替换成 ?」的那个哈希绝不能混进字典
        self.assertNotIn(mx_hash(BAD_TEXT_NAME.encode("gbk", "replace")), table)

    def test_real_catalog_has_no_unencodable_paths(self):
        table = names.known_path_hashes()
        self.assertGreater(len(table), 2000)  # 随包字典 2,901 条布局路径
        self.assertEqual(names.unencodable_known_paths(), [])


class DocumentPathTests(unittest.TestCase):
    """文档侧：查路径返回 None，写路径抛明确的 ValueError。"""

    def test_index_by_path_misses_unencodable(self):
        doc = _make_0slf_doc()
        self.assertIsNone(doc.index_by_path(BAD_NAME))
        self.assertIsNone(doc.index_by_path("dialog4/not-there.dlg"))

    def test_index_by_path_finds_native_hash(self):
        payloads = [b"payload"]
        entry_id = mx_hash(b"DIALOG4/FOUND.PNG")
        doc = PackDocument.from_bytes(fls0slf.build(
            payloads, [fls0slf.EntryMeta(entry_id=entry_id, r1=0)]))
        self.assertEqual(doc.index_by_path("dialog4/found.png"), 0)

    def test_add_entry_for_path_rejects_unencodable(self):
        doc = _make_0slf_doc()
        with self.assertRaises(ValueError) as ctx:
            doc.add_entry_for_path(b"data", BAD_NAME)
        self.assertIn("GBK", str(ctx.exception))
        self.assertEqual(doc.count, 2, "拒绝时不得改动文档")

    def test_add_entry_for_path_uses_the_same_hash_as_engine(self):
        doc = _make_0slf_doc()
        index = doc.add_entry_for_path(b"data", r"Dialog4\New.PNG")
        self.assertEqual(index, 2)
        meta = doc.archive.extra_metas[index]
        self.assertEqual(meta.entry_id, mx_hash(b"DIALOG4/NEW.PNG"))


if __name__ == "__main__":
    unittest.main()
