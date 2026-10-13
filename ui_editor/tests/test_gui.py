"""GUI 冒烟：开布局、加控件、改属性、保存、新建、导出（offscreen）。"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FIXTURE = Path(__file__).parent / "fixtures" / "original_style.dlg"


class TestMainWindowFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False  # 测试收尾：跳过丢弃确认
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_open_add_edit_save(self):
        w = self.window
        w.open_layout_file(str(FIXTURE))
        self.assertIsNotNone(w.doc)
        self.assertEqual(len(w.doc.all_widgets()), 5)
        main = w.doc.roots[0]
        self.assertEqual(main.wtype, "CMainFrame")

        w._select_widget(main)
        w.add_widget("CButton")  # 加到选中的主窗口下
        self.assertEqual(len(w.doc.all_widgets()), 6)
        button = w.current_selection()
        self.assertEqual(button.wtype, "CButton")
        self.assertIs(button.parent, main)

        button.props["iX"] = 33
        w._on_property_changed(button, "iX")
        item = w.scene.item_for(button)
        self.assertIsNotNone(item)
        self.assertEqual(int(item.pos().x()), 33)

        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "out.dlg")
            self.assertTrue(w.save_as(target))
            from ui_editor.core import dlg_codec
            from ui_editor.core.model import LayoutDocument
            dicts, _ = dlg_codec.parse_bytes(Path(target).read_bytes())
            again = LayoutDocument.from_dicts(dicts, None)
            self.assertEqual(again.to_dicts(), w.doc.to_dicts())
        w.doc.dirty = False

    def test_new_layout_and_export(self):
        w = self.window
        w.new_layout()
        self.assertIsNotNone(w.doc)
        self.assertEqual(len(w.doc.roots), 1)
        image = w.view.export_image()
        self.assertFalse(image.isNull())
        colors = {image.pixel(0, 0), image.pixel(10, 10),
                  image.pixel(image.width() // 2, image.height() // 2)}
        self.assertGreater(len(colors), 1)


def _mini_pack_bytes(res_name: str = "dialog/test.dlg") -> bytes:
    """自建微型 0SLF 包：一个 XOR 加密的 .dlg 条目。"""
    import struct

    from ui_editor.core import dlg_codec
    from ui_editor.core.mxhash import mx_hash

    plain = dlg_codec.dump_bytes(
        [{"sWidgetType": "CMainFrame", "sName": "root", "lChildren": []}],
        md5="0" * 32)
    key = b"\x5a\xa5\x11\x7e"
    packed = bytes(b ^ key[i & 3] for i, b in enumerate(plain))
    entry_id = mx_hash(res_name.encode("gbk"))
    offset = 12
    r1 = 12345
    r2 = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ len(packed)) & 0xFFFFFFFF
    r3 = (((r2 * 0 * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ offset) & 0xFFFFFFFF
    head = b"0SLF" + struct.pack("<II", 1, offset + len(packed))
    return head + packed + struct.pack("<IIII", entry_id, r1, r2, r3)


class TestOpenFromPack(unittest.TestCase):
    """从资源包打开：直接选包入树；无布局返回 0；树打开保真。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_pack_with_layouts_goes_to_tree(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            count = self.window.open_pack_file(str(pack_path))
            self.assertEqual(count, 1)
            self.assertEqual(self.window.resource_panel.root_count(), 1)
            self.assertIsNone(self.window.doc)  # 只入树，不自动打开

    def test_pack_without_layouts_returns_zero(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "itemish.fls"
            pack_path.write_bytes(_mini_pack_bytes("data/junk.bin"))
            count = self.window.open_pack_file(str(pack_path))
            self.assertEqual(count, 0)
            self.assertEqual(self.window.resource_panel.root_count(), 0)

    def test_open_pack_layout_after_tree_add(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            self.window.open_pack_file(str(pack_path))
            first_root = self.window.resource_panel._tree.topLevelItem(0)
            # 再双击打开：包根不能被拆掉重挂（树跳动回归）
            self.window._open_pack_layout(
                str(pack_path), "dialog/cateroom.dlg")
            self.assertIsNotNone(self.window.doc)
            self.assertEqual(self.window.doc.roots[0].wtype, "CMainFrame")
            self.assertEqual(
                self.window.doc.source_pack[1], "dialog/cateroom.dlg")
            self.assertEqual(self.window.resource_panel.root_count(), 1)
            self.assertIs(
                self.window.resource_panel._tree.topLevelItem(0), first_root)


class TestMainPackMissingList(unittest.TestCase):
    """近乎全量的主 UI 包：树上追加包内缺失（灰显）名单。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_missing_appended_for_main_pack(self):
        import tempfile

        from ui_editor.core import assets as assets_module
        from ui_editor.ui import main_window as main_module
        from ui_editor.ui.main_window import MainWindow

        window = MainWindow()
        small_catalog = ["dialog/cateroom.dlg", "dialog/gone.dlg"]
        old_main = main_module.known_layout_paths
        old_assets = assets_module.known_layout_paths
        main_module.known_layout_paths = lambda: list(small_catalog)
        assets_module.known_layout_paths = lambda: list(small_catalog)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                pack_path = Path(tmp) / "ui.fls"
                pack_path.write_bytes(
                    _mini_pack_bytes("dialog/cateroom.dlg"))
                count = window.open_pack_file(str(pack_path))
                self.assertEqual(count, 1)
                root = window.resource_panel._tree.topLevelItem(0)
                self.assertEqual(root.childCount(), 2)  # 1 活 + 1 灰显
                self.assertIn("包内缺失", root.text(0))
        finally:
            main_module.known_layout_paths = old_main
            assets_module.known_layout_paths = old_assets
            if window.doc is not None:
                window.doc.dirty = False
            window.close()
            window.deleteLater()
            self._app.processEvents()


class TestCatalog(unittest.TestCase):
    def test_catalog_loaded(self):
        from ui_editor.core.catalog import known_layout_paths
        paths = known_layout_paths()
        self.assertGreaterEqual(len(paths), 2900)
        self.assertTrue(all(p.endswith(".dlg") for p in paths))


if __name__ == "__main__":
    unittest.main()


class TestResourceTree(unittest.TestCase):
    """资源树：包/目录入树、累加不移除、散装目录严格过滤。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    @staticmethod
    def _tree_texts(window) -> list[str]:
        texts = []

        def visit(item):
            texts.append(item.text(0))
            for i in range(item.childCount()):
                visit(item.child(i))

        tree = window.resource_panel._tree
        for i in range(tree.topLevelItemCount()):
            visit(tree.topLevelItem(i))
        return texts

    def test_resource_dir_mounts_pack_into_tree(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            self.window.open_resource_dir(tmp)
            panel = self.window.resource_panel
            self.assertEqual(panel.root_count(), 1)
            texts = self._tree_texts(self.window)
            self.assertTrue(any("mini.fls" in t for t in texts))
            self.assertIn("dialog/cateroom.dlg", texts)
            # 再挂一个散装目录：只追加，不顶掉已有包节点
            loose = Path(tmp) / "loose"
            loose.mkdir()
            (loose / "x.dlg").write_bytes(b"UI_INFO = []\n")
            self.window.open_layout_dir(str(loose))
            self.assertEqual(panel.root_count(), 2)

    def test_loose_dir_filters_non_dlg(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.dlg").write_bytes(b"UI_INFO = []\n")
            (root / "junk.txt").write_text("x", encoding="utf-8")
            sub = root / "only_text"
            sub.mkdir()
            (sub / "readme.md").write_text("x", encoding="utf-8")
            sub2 = root / "has_dlg"
            sub2.mkdir()
            (sub2 / "b.dlg").write_bytes(b"UI_INFO = []\n")
            self.window.open_layout_dir(tmp)
            texts = self._tree_texts(self.window)
            self.assertIn("a.dlg", texts)
            self.assertIn("b.dlg", texts)
            self.assertNotIn("junk.txt", texts)
            self.assertNotIn("readme.md", texts)
            self.assertNotIn("only_text", texts)


class TestResourceDirFilterAndSearch(unittest.TestCase):
    """无布局包过滤 + 树上方按名称查找布局。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _visible_texts(self) -> list[str]:
        texts = []

        def visit(item):
            if not item.isHidden():
                texts.append(item.text(0))
                for i in range(item.childCount()):
                    visit(item.child(i))

        tree = self.window.resource_panel._tree
        for i in range(tree.topLevelItemCount()):
            visit(tree.topLevelItem(i))
        return texts

    def test_resource_dir_skips_pack_without_layouts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ui.fls").write_bytes(
                _mini_pack_bytes("dialog/cateroom.dlg"))
            (Path(tmp) / "item.fls").write_bytes(
                _mini_pack_bytes("data/junk.bin"))
            self.window.open_resource_dir(tmp)
            self.assertEqual(self.window.resource_panel.root_count(), 1)
            self.assertTrue(any(
                "ui.fls" in t for t in self._visible_texts()))

    def test_search_filters_layouts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            for name in ("service.dlg", "equip.dlg", "init.dlg"):
                (Path(tmp) / name).write_bytes(b"UI_INFO = []\n")
            self.window.open_layout_dir(tmp)
            panel = self.window.resource_panel
            panel._search.setText("serv")
            visible = self._visible_texts()
            self.assertIn("service.dlg", visible)
            self.assertNotIn("equip.dlg", visible)
            self.assertNotIn("init.dlg", visible)
            panel._search.setText("")
            visible = self._visible_texts()
            for name in ("service.dlg", "equip.dlg", "init.dlg"):
                self.assertIn(name, visible)


class TestGenerationMarks(unittest.TestCase):
    """资源树着色：现役绿色、包内缺失灰色斜体、搜索能找到缺失项。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.panels import ResourceTreePanel
        self.panel = ResourceTreePanel()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self._app.processEvents()

    def test_leaf_colors_and_missing(self):
        from PySide6.QtGui import QColor

        self.panel.add_pack(
            "D:/game/data/interface.fls",
            ["dialog4/activity/2021summer/main.dlg"],
            ["dialog/gone.dlg"])
        root = self.panel._tree.topLevelItem(0)
        self.assertEqual(root.childCount(), 2)
        live = root.child(0)
        missing = root.child(1)
        self.assertEqual(
            live.foreground(0).color(), QColor("#1a7f37"))
        self.assertEqual(
            missing.foreground(0).color(), QColor("#8a8a8a"))
        self.assertTrue(missing.font(0).italic())
        # 搜索仍能找到包内缺失项（方便确认死引用）
        self.panel._search.setText("gone")
        self.assertFalse(missing.isHidden())
        self.assertTrue(live.isHidden())
