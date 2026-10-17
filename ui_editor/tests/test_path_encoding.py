"""路径编码策略：不可 GBK 编码的路径不得被静默替换（分析报告 P2-2）。

旧写法 ``mx_hash(name.encode("gbk", "replace"))`` 会把不可编码字符换成
``?``，于是算出来的是**另一个路径**的哈希——查得到/查不到都不可信。
现在统一走 :func:`ui_editor.core.mxhash.path_hash`（严格编码、失败抛错），
查询侧把「不可编码」当作「引擎也寻址不到」处理，目录表侧跳过并留痕。
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import catalog, dlg_codec, pack_build  # noqa: E402
from ui_editor.core.errors import PackError  # noqa: E402
from ui_editor.core.mxhash import mx_hash, path_hash  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402

REAL_PACK = REPO_ROOT / "data" / "passive.fls"
#: 代理对（surrogateescape 读进来的原始字节）：包内路径查询的真实来源
BAD_NAME = "dialog4/bad\udcff.png"
#: 目录/字典文件能用 UTF-8 存、但 GBK 编不出来的字符（U+2603 雪人）
BAD_TEXT_NAME = "dialog4/bad\u2603.dlg"


class PathHashTests(unittest.TestCase):
    def test_matches_engine_normalisation(self):
        self.assertEqual(path_hash("Dialog4\\A.dlg"),
                         mx_hash(b"DIALOG4/A.DLG"))

    def test_raises_instead_of_silently_replacing(self):
        # 旧写法：两个不同路径会被折叠成同一个哈希，且不报错
        self.assertEqual(BAD_NAME.encode("gbk", "replace"),
                         b"dialog4/bad?.png")
        with self.assertRaises(ValueError) as ctx:
            path_hash(BAD_NAME)
        self.assertIn("GBK", str(ctx.exception))

    def test_replaced_hash_would_look_up_a_different_path(self):
        replaced = mx_hash(BAD_NAME.encode("gbk", "replace"))
        self.assertNotEqual(replaced, path_hash("dialog4/bad.png"))


class PackLookupTests(unittest.TestCase):
    """查询侧：不可编码的名称 = 引擎寻址不到 = 未命中，而不是换个名字去查。"""

    def setUp(self):
        if not REAL_PACK.is_file():
            self.skipTest(f"缺少真实资源包：{REAL_PACK}")
        self.pack = FlsPack(REAL_PACK)
        self.addCleanup(self.pack.close)

    def test_unencodable_name_is_a_miss(self):
        self.assertIsNone(self.pack.entry_id_for(BAD_NAME))
        self.assertFalse(self.pack.contains(BAD_NAME))
        self.assertIsNone(self.pack.read_named(BAD_NAME))

    def test_empty_and_blank_names_are_still_misses(self):
        for name in ("", "   ", "\\", "/"):
            with self.subTest(name=name):
                self.assertIsNone(self.pack.entry_id_for(name))
                self.assertFalse(self.pack.contains(name))


class CatalogTests(unittest.TestCase):
    """目录表：不可编码的路径跳过并留痕，不再参与整包相交。"""

    def setUp(self):
        self.addCleanup(self._reset)
        self._reset()

    @staticmethod
    def _reset():
        catalog._HASH_CACHE = None
        catalog._UNENCODABLE.clear()

    def test_skips_unencodable_and_records_them(self):
        original = catalog.known_layout_paths
        catalog.known_layout_paths = lambda: [
            "dialog4/good.dlg", BAD_TEXT_NAME, "combdialog4/also_good.dlg"]
        try:
            table = catalog.known_layout_hashes()
            skipped = catalog.unencodable_layout_paths()
        finally:
            catalog.known_layout_paths = original
        self.assertEqual(sorted(table.values()),
                         ["combdialog4/also_good.dlg", "dialog4/good.dlg"])
        self.assertEqual(skipped, [BAD_TEXT_NAME])
        # 跳过的那条不能以「替换后的名字」混进索引
        self.assertNotIn(mx_hash(BAD_TEXT_NAME.encode("gbk", "replace")), table)

    def test_real_catalog_has_no_unencodable_paths(self):
        table = catalog.known_layout_hashes()
        self.assertGreater(len(table), 2000)  # 随包目录 2,903 条
        self.assertEqual(catalog.unencodable_layout_paths(), [])


class WritePathTests(unittest.TestCase):
    """写包侧：附加资源名不可编码时必须在写之前拒绝，而不是静默换个哈希写进去。"""

    def test_unencodable_extra_is_rejected_before_publishing(self):
        if not REAL_PACK.is_file():
            self.skipTest(f"缺少真实资源包：{REAL_PACK}")
        plain = dlg_codec.dump_bytes([{
            "sWidgetType": "CMainFrame", "sName": "PathEnc", "iWidth": 10,
        }])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.fls"
            with self.assertRaises(PackError) as ctx:
                pack_build.patch_pack_copy(
                    REAL_PACK, "dialog4/path_enc.dlg", plain, out,
                    extra_entries={BAD_NAME: b"not-an-image"},
                    allow_create=True)
            self.assertIn("GBK", str(ctx.exception))
            self.assertFalse(out.exists(), "失败时不得留下输出文件")


if __name__ == "__main__":
    unittest.main()
