"""GUI 冒烟：开布局、加控件、改属性、保存、新建、导出（offscreen）。"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
            with mock.patch("ui_editor.ui.main_window.SaveReviewDialog.exec",
                            return_value=1):
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


class TestTopLevelWidgets(unittest.TestCase):
    """加顶级控件 + 把已有控件提升为顶级（入口行为）。"""

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

    def test_add_root_and_promote(self):
        w = self.window
        w.open_layout_file(str(FIXTURE))
        doc = w.doc
        assert doc is not None
        main = doc.roots[0]
        roots_before = len(doc.roots)

        w.palette_panel.current_type = lambda: "CButton"  # type: ignore[method-assign]
        w._select_widget(main)
        w._add_root_from_tree()  # 选中了主窗口也照样加在顶层
        top = w.current_selection()
        self.assertEqual(top.wtype, "CButton")
        self.assertIsNone(top.parent)
        self.assertEqual(len(doc.roots), roots_before + 1)

        w._select_widget(main)
        w.add_widget("CButton")  # 先挂到主窗口下
        child = w.current_selection()
        self.assertIs(child.parent, main)
        w.promote_selected_to_root()
        self.assertIsNone(child.parent)
        self.assertIn(child, doc.roots)


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


class TestSaveToPack(unittest.TestCase):
    """M1 写回：从包打开 -> 改 -> 生成新包 -> 回读一致、原包不动。"""

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

    def test_write_pack_copy_verified(self):
        import tempfile

        from ui_editor.core.assets import AssetResolver

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "interface_mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            before_bytes = pack_path.read_bytes()
            self.window.open_pack_file(str(pack_path))
            self.window._open_pack_layout(
                str(pack_path), "dialog/cateroom.dlg")
            doc = self.window.doc
            self.assertIsNotNone(doc)
            doc.roots[0].props["sTitle"] = "改過的新標題"
            doc.dirty = True
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertIsNotNone(report)
            self.assertTrue(report.get("ok"), report)
            self.assertEqual(pack_path.read_bytes(), before_bytes)  # 原包不动
            self.assertFalse(doc.dirty)
            fresh = AssetResolver()
            fresh.mount_pack(out)
            try:
                got = fresh.fetch_dlg("dialog/cateroom.dlg")
            finally:
                fresh.close()
            self.assertIsNotNone(got)
            self.assertEqual(got[0][0]["sTitle"], "改過的新標題")


class TestSaveToPackWithStagedImage(unittest.TestCase):
    """选图窗新加的图被布局引用时，随布局一并写进新包并销账。"""

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

    def test_staged_image_written_with_pack(self):
        import tempfile

        from ui_editor.core.assets import AssetResolver

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "interface_mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            self.window.open_pack_file(str(pack_path))
            self.window._open_pack_layout(
                str(pack_path), "dialog/cateroom.dlg")
            doc = self.window.doc
            self.assertIsNotNone(doc)
            staged_path = "newdir\\我的背景.png"
            self.window.resolver.stage_image(staged_path, b"\x89PNGnewpic")
            doc.roots[0].props["sFileName"] = staged_path
            doc.dirty = True
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertIsNotNone(report)
            self.assertTrue(report.get("ok"), report)
            self.assertEqual(report.get("images_added"), 1)
            self.assertEqual(self.window.resolver.staged_images(), {})
            fresh = AssetResolver()
            fresh.mount_pack(out)
            try:
                self.assertEqual(fresh.fetch_bytes(staged_path),
                                 b"\x89PNGnewpic")
            finally:
                fresh.close()


class TestSaveWithUnreferencedStagedImage(unittest.TestCase):
    """挂账新图未被当前布局引用时：保存成功但必须明示未写入。

    回归背景：用户反馈「图片始终存不进去，保存成功但重开还是
    原数」——旧弹窗只字不提有几张图真进了新包，没引用到的图被
    静默漏过。报告须列出 stages_unreferenced 与新包总条数。
    """

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

    def test_unreferenced_staged_image_flagged_not_written(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "interface_mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            self.window.open_pack_file(str(pack_path))
            self.window._open_pack_layout(
                str(pack_path), "dialog/cateroom.dlg")
            doc = self.window.doc
            self.assertIsNotNone(doc)
            self.window.resolver.stage_image(
                "newdir\\未用上的圖.png", b"\x89PNGunused")
            doc.dirty = True
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertTrue(report.get("ok"), report)
            self.assertEqual(report.get("images_added"), 0)
            self.assertEqual(report.get("staged_unreferenced"),
                             ["newdir\\未用上的圖.png"])
            self.assertEqual(report.get("entries_after"), 1)  # 原包 1 条、无新增
            # 账未销：还在挂账里，可换个布局再保存写入
            self.assertIn("newdir\\未用上的圖.png",
                          self.window.resolver.staged_images())
            from ui_editor.core.pack import FlsPack
            with FlsPack(out) as pack:
                self.assertEqual(pack.count, 1)
                self.assertFalse(pack.contains("newdir\\未用上的圖.png"))


class TestCanvasClipboardAndContextMenu(unittest.TestCase):
    """画布右键菜单与复制/粘贴/删除：剪贴板往返、多选删除、撤销恢复。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        import tempfile

        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self._tmp = tempfile.TemporaryDirectory()
        pack_path = Path(self._tmp.name) / "interface_mini.fls"
        pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
        self.window.open_pack_file(str(pack_path))
        self.window._open_pack_layout(
            str(pack_path), "dialog/cateroom.dlg")
        self.doc = self.window.doc
        self.assertIsNotNone(self.doc)

    def tearDown(self):
        # 本组创建的 QMimeData 归剪贴板所有；在 QApplication/解释器
        # 析构前清掉测试数据，避免 offscreen 后端的销毁顺序崩溃。
        # 仅测试清理，不在产品退出时清空用户剪贴板。
        self._app.clipboard().clear()
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _add_button(self, parent=None):
        widget = self.doc.new_widget("CButton", parent=parent)
        self.window._refresh_structure()
        return widget

    def _select(self, *widgets):
        self.window.scene.clearSelection()
        for w in widgets:
            item = self.window.scene.item_for(w)
            self.assertIsNotNone(item)
            item.setSelected(True)
        self._app.processEvents()

    def test_copy_paste_offsets_and_undo(self):
        button = self._add_button(parent=self.doc.roots[0])
        self.doc.checkpoint()  # 与窗口「添加控件」流程一致：落一步
        self._select(button)
        self.window.copy_selected_widgets()
        from PySide6.QtGui import QGuiApplication
        mime = QGuiApplication.clipboard().mimeData()
        self.assertTrue(mime.hasFormat(self.window._MIME_WIDGETS))
        self.assertTrue(self.window._act_paste.isEnabled())
        before = len(self.doc.roots[0].children)
        self.window.paste_widgets()
        siblings = self.doc.roots[0].children
        self.assertEqual(len(siblings), before + 1)
        pasted = siblings[siblings.index(button) + 1]
        self.assertEqual(pasted.name, button.name)
        self.assertEqual((pasted.x, pasted.y), (button.x + 16, button.y + 16))
        self.assertTrue(self.doc.undo())  # 整组粘贴一步可撤销
        self.assertEqual(len(self.doc.roots[0].children), before)

    def test_paste_without_selection_goes_to_roots(self):
        button = self._add_button(parent=self.doc.roots[0])
        self._select(button)
        self.window.copy_selected_widgets()
        self.window.scene.clearSelection()
        self.window._selected = None
        n_roots = len(self.doc.roots)
        self.window.paste_widgets()
        self.assertEqual(len(self.doc.roots), n_roots + 1)

    def test_delete_multiple_and_undo(self):
        parent = self.doc.roots[0]
        b1 = self._add_button(parent=parent)
        b2 = self._add_button(parent=parent)
        self.doc.checkpoint()  # 添加落一步，删除才能单独撤销
        self._select(b1, b2)
        self.window.delete_selected()  # 无子控件，不弹确认
        names = {w.name for w in parent.children}
        self.assertNotIn(b1.name, names)
        self.assertNotIn(b2.name, names)
        self.assertTrue(self.doc.undo())
        fresh = {w.name for w in self.doc.roots[0].children}  # 撤销后是新对象树
        self.assertIn(b1.name, fresh)
        self.assertIn(b2.name, fresh)

    def test_delete_parent_with_children_confirms(self):
        from unittest import mock

        from PySide6.QtWidgets import QMessageBox

        frame = self.doc.roots[0]
        self._add_button(parent=frame)  # 给 frame 加一个子控件触发确认分支
        self._select(frame)
        with mock.patch.object(
                QMessageBox, "question",
                return_value=QMessageBox.StandardButton.No):
            self.window.delete_selected()
        self.assertIn(frame, self.doc.roots)  # 选了 No，什么都不删
        with mock.patch.object(
                QMessageBox, "question",
                return_value=QMessageBox.StandardButton.Yes):
            self.window.delete_selected()
        self.assertNotIn(frame, self.doc.roots)
        self.assertEqual(self.doc.to_dicts(), [])  # 子控件一并删除

    def test_context_menu_actions_and_enablement(self):
        button = self._add_button(parent=self.doc.roots[0])
        menu = self.window.build_canvas_context_menu(button)
        actions = menu.actions()
        self.assertIn(self.window._act_copy, actions)
        self.assertIn(self.window._act_paste, actions)
        self.assertIn(self.window._act_delete, actions)
        self.assertTrue(self.window._act_copy.isEnabled())  # 右击已选中它
        self.window.scene.clearSelection()
        self.window._selected = None
        self.window.build_canvas_context_menu(None)
        self.assertFalse(self.window._act_copy.isEnabled())  # 无选择则禁用

    def test_edit_keys_act_on_text_when_input_focused(self):
        """焦点在文本框时 Ctrl+C/Delete 作用于文字，不得动控件。"""
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtWidgets import QLineEdit

        button = self._add_button(parent=self.doc.roots[0])
        self._select(button)
        self.window.show()
        edit = QLineEdit(self.window)
        self.window.statusBar().addWidget(edit)  # 入布局、真可见才抢得到焦点
        edit.show()
        edit.setText("hello")
        edit.selectAll()
        self.window.activateWindow()
        edit.setFocus()
        self._app.processEvents()
        self.assertIs(self.window._focused_text_editor(), edit)
        self.window._edit_copy()
        clipboard = QGuiApplication.clipboard()
        self.assertEqual(clipboard.text(), "hello")
        self.assertFalse(clipboard.mimeData().hasFormat(
            self.window._MIME_WIDGETS))
        self.window._edit_delete()
        self.assertEqual(edit.text(), "")  # 删的是选中的文字
        self.assertIn(button, self.doc.roots[0].children)  # 控件毫发无损
        self.window.hide()

    def test_view_context_event_reports_widget(self):
        from PySide6.QtGui import QContextMenuEvent

        button = self._add_button(parent=self.doc.roots[0])
        view = self.window.view
        self.window.show()
        self._app.processEvents()
        item = self.window.scene.item_for(button)
        center = item.sceneBoundingRect().center()
        local = view.mapFromScene(center)
        global_pos = view.viewport().mapToGlobal(local)
        seen = []
        view.context_menu_handler = lambda gp, w: seen.append(w)
        event = QContextMenuEvent(
            QContextMenuEvent.Reason.Mouse, local, global_pos)
        view.contextMenuEvent(event)
        self.assertEqual(seen, [button])
        self.window.hide()


class TestScriptLinkGui(unittest.TestCase):
    """脚本联动第一期：开布局自动关联、面板详情、代码皮肤绘制。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        import tempfile

        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self._tmp = tempfile.TemporaryDirectory()
        pack_path = Path(self._tmp.name) / "interface_mini.fls"
        pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
        self.window.open_pack_file(str(pack_path))
        self.window._open_pack_layout(
            str(pack_path), "dialog/cateroom.dlg")
        self.doc = self.window.doc
        self.assertIsNotNone(self.doc)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _fake_index(self):
        from ui_editor.core.script_index import ScriptIndex
        return ScriptIndex({
            "modules": [[7, "script/fake/panel.py"]],
            "layouts": {"dialog/cateroom.dlg": {
                "m": [0],
                "o": {"root": [[0, "CFakePanel", "__init__", 0]],
                      "prev": [[0, "CFakePanel", "__init__", 1]]},
                "s": {"prev": [[0, "CFakePanel", "__init__",
                                "CFakeButton", "fake/btn.igs", "上一頁", 5]]},
            }},
        })

    def test_open_layout_links_script_and_panel(self):
        w = self.window
        w.script_index = self._fake_index()
        note = w._apply_script_link(w.doc)
        self.assertIn("1 个模块引用此布局", note)
        self.assertIsNotNone(w.script_panel._link)
        self.assertIn("prev", w.ctx.code_skins)
        self.assertEqual(w.ctx.code_skins["prev"].skin, "fake/btn.igs")
        names = {w.script_panel._names.item(i).text()
                 for i in range(w.script_panel._names.count())}
        self.assertTrue(any(n.startswith("prev") for n in names))
        self.assertTrue(any(n.startswith("root") for n in names))
        root = w.doc.roots[0]
        w._select_widget(root)
        self.assertIn("被脚本按名取用", w.script_panel._detail.text())
        w._select_by_name("root")
        self.assertIs(w._selected, root)
        self.assertIn("代码皮肤", w.statusBar().currentMessage() + note)

    def test_code_skin_paints_pixmap(self):
        from PySide6.QtGui import QColor, QImage, QPainter, QPixmap

        from ui_editor.core.model import Widget
        from ui_editor.core.painters import _paint_code_skin
        from ui_editor.core.script_index import SkinRef

        pixmap = QPixmap(20, 10)
        pixmap.fill(QColor(200, 30, 30))

        class _Ctx:
            code_skins = {"prev": SkinRef(
                module="m.py", entry=1, cls="C", func="__init__",
                factory="CFakeButton", skin="fake/btn.igs",
                text="", msgid=5)}
            button_state = "normal"
            show_names = False

            def pixmap(self, name, frame=0):
                return pixmap if name == "fake/btn.igs" else None

        widget = Widget({"sWidgetType": "CButton", "sName": "prev",
                         "iWidth": 20, "iHeight": 10})
        image = QImage(20, 10, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0))
        painter = QPainter(image)
        self.assertTrue(_paint_code_skin(painter, widget, _Ctx()))
        painter.end()
        self.assertEqual(QColor(image.pixel(10, 5)).red(), 200)
        # 没有绑定的控件不接管
        other = Widget({"sWidgetType": "CButton", "sName": "other",
                        "iWidth": 20, "iHeight": 10})
        painter = QPainter(image)
        self.assertFalse(_paint_code_skin(painter, other, _Ctx()))
        painter.end()


class TestWidgetLockGui(unittest.TestCase):
    """控件锁定：锁后拖不动/缩不了/删不掉，解锁恢复；撤销不丢锁。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        import tempfile

        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self._tmp = tempfile.TemporaryDirectory()
        pack_path = Path(self._tmp.name) / "interface_mini.fls"
        pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
        self.window.open_pack_file(str(pack_path))
        self.window._open_pack_layout(
            str(pack_path), "dialog/cateroom.dlg")
        self.doc = self.window.doc
        self.assertIsNotNone(self.doc)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _add_button(self, parent=None):
        widget = self.doc.new_widget(
            "CButton", parent=parent or self.doc.roots[0])
        widget.set_geometry(x=10, y=10, width=100, height=50)
        self.window._refresh_structure()
        return widget

    def _drag_handle(self, widget, dx, dy):
        from PySide6.QtCore import QEvent, QPointF
        from PySide6.QtWidgets import QGraphicsSceneMouseEvent

        item = self.window.scene.item_for(widget)
        item.setSelected(True)
        start_scene = item.mapToScene(QPointF(100, 50))

        def _event(etype, scene_pos):
            ev = QGraphicsSceneMouseEvent(etype)
            ev.setPos(QPointF(100, 50))
            ev.setScenePos(scene_pos)
            return ev

        item.mousePressEvent(
            _event(QEvent.Type.GraphicsSceneMousePress, start_scene))
        item.mouseMoveEvent(_event(
            QEvent.Type.GraphicsSceneMouseMove,
            start_scene + QPointF(dx, dy)))
        item.mouseReleaseEvent(
            _event(QEvent.Type.GraphicsSceneMouseRelease,
                   start_scene + QPointF(dx, dy)))

    def test_toolbar_toggle_lock_flags_and_no_dirty(self):
        from PySide6.QtWidgets import QGraphicsItem, QToolBar

        w = self.window
        button = self._add_button()
        w._select_widget(button)
        self.assertIn(w._act_lock,
                      w.findChildren(QToolBar)[0].actions())
        self.assertEqual(w._act_lock.iconText(), "锁定")
        self.assertFalse(w._act_lock.icon().isNull())
        self.assertEqual(w._act_lock.shortcut().toString(), "Ctrl+L")
        self.assertTrue(w._act_lock.isEnabled())
        w.doc.dirty = False  # 模拟已保存基线，看锁定是否会乱标脏
        w._act_lock.trigger()
        self.assertTrue(button.locked)
        self.assertTrue(w._act_lock.isChecked())
        item = w.scene.item_for(button)
        self.assertFalse(item.flags()
                         & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.assertTrue(item.flags()
                        & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.assertFalse(w.doc.dirty)   # 锁定只是编辑器状态，不标脏
        self.assertFalse(w.doc.can_undo)  # 也不进撤销时间线
        w._act_lock.trigger()
        self.assertFalse(button.locked)
        self.assertFalse(w._act_lock.isChecked())
        item = w.scene.item_for(button)
        self.assertTrue(item.flags()
                        & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def test_locked_cannot_resize_or_delete_until_unlocked(self):
        w = self.window
        button = self._add_button()
        w._select_widget(button)
        w._act_lock.trigger()
        self._drag_handle(button, 50, 10)  # 拖右下把手：应纹丝不动
        self.assertEqual((button.width, button.height), (100, 50))
        w.delete_selected()  # 锁着删不掉
        self.assertIn(button, self.doc.roots[0].children)
        self.assertIn("锁定", w.statusBar().currentMessage())
        w._act_lock.trigger()  # 解锁后删得掉
        w.delete_selected()
        self.assertNotIn(button.name,
                         {c.name for c in self.doc.roots[0].children})

    def test_parent_with_locked_child_cannot_be_deleted(self):
        w = self.window
        frame = self.doc.roots[0]
        button = self._add_button(parent=frame)
        w._select_widget(button)
        w._act_lock.trigger()
        w._select_widget(frame)
        w.delete_selected()
        self.assertIn(frame, self.doc.roots)
        self.assertIn(button, frame.children)

    def test_lock_survives_undo_and_context_menu_has_it(self):
        w = self.window
        button = self._add_button()
        self.doc.checkpoint()
        w._select_widget(button)
        w._act_lock.trigger()
        menu = w.build_canvas_context_menu(button)
        self.assertIn(w._act_lock, menu.actions())
        button.set_geometry(x=60)
        self.doc.checkpoint()
        w.undo()  # 历史重建对象，锁定按路径恢复
        fresh = {c.name: c for c in self.doc.roots[0].children}
        self.assertIn(button.name, fresh)
        self.assertTrue(fresh[button.name].locked)
        self.assertEqual(fresh[button.name].x, 10)

    def test_tree_lock_column_toggles_and_syncs(self):
        w = self.window
        button = self._add_button()
        panel = w.tree_panel
        tree = panel._tree
        self.assertEqual(tree.columnCount(), 2)
        item = panel._items[id(button)]
        self.assertFalse(item.icon(1).isNull())  # 默认开锁图标
        self.assertIn("未锁定", item.toolTip(1))
        # 点名字列选中：控件树选中要真同步到主窗口（顺带回归）
        tree.setCurrentItem(item)
        self._app.processEvents()
        self.assertIs(w._selected, button)
        # 点锁列：锁定，且画布工具栏勾选与图标同步
        panel._on_item_clicked(item, 1)
        self.assertTrue(button.locked)
        self.assertIn("已锁定", item.toolTip(1))
        self.assertTrue(w._act_lock.isChecked())
        # 再点一次解锁
        panel._on_item_clicked(item, 1)
        self.assertFalse(button.locked)
        self.assertIn("未锁定", item.toolTip(1))
        # 从工具栏锁定，树图标也要跟着变
        w._act_lock.trigger()
        self.assertTrue(button.locked)
        self.assertIn("已锁定", panel._items[id(button)].toolTip(1))
        w._act_lock.trigger()

    def test_locked_parent_children_still_draggable(self):
        from PySide6.QtWidgets import QGraphicsItem

        w = self.window
        frame = self.doc.roots[0]
        button = self._add_button(parent=frame)
        w._select_widget(frame)
        w._act_lock.trigger()
        self.assertTrue(frame.locked)
        self.assertFalse(button.locked)
        item = w.scene.item_for(button)
        self.assertTrue(item.flags()
                        & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self._drag_handle(button, 50, 10)  # 子控件照常缩放
        self.assertEqual((button.width, button.height), (150, 60))


class TestAspectResize(unittest.TestCase):
    """等比缩放：工具栏开关、边/角把手按原比例缩放、Shift 临时等比。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        import tempfile

        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self._tmp = tempfile.TemporaryDirectory()
        pack_path = Path(self._tmp.name) / "interface_mini.fls"
        pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
        self.window.open_pack_file(str(pack_path))
        self.window._open_pack_layout(
            str(pack_path), "dialog/cateroom.dlg")
        self.doc = self.window.doc
        self.assertIsNotNone(self.doc)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _add_button(self):
        widget = self.doc.new_widget("CButton", parent=self.doc.roots[0])
        widget.set_geometry(x=10, y=10, width=100, height=50)
        self.window._refresh_structure()
        return widget

    def _drag_handle(self, widget, handle_pos, dx, dy, modifiers=None):
        from PySide6.QtCore import QEvent, QPointF, Qt
        from PySide6.QtWidgets import QGraphicsSceneMouseEvent

        if modifiers is None:
            modifiers = Qt.KeyboardModifier.NoModifier
        item = self.window.scene.item_for(widget)
        item.setSelected(True)
        start_scene = item.mapToScene(QPointF(*handle_pos))

        def _event(etype, scene_pos):
            ev = QGraphicsSceneMouseEvent(etype)
            ev.setPos(QPointF(*handle_pos))
            ev.setScenePos(scene_pos)
            ev.setModifiers(modifiers)
            return ev

        item.mousePressEvent(
            _event(QEvent.Type.GraphicsSceneMousePress, start_scene))
        item.mouseMoveEvent(_event(
            QEvent.Type.GraphicsSceneMouseMove,
            start_scene + QPointF(dx, dy)))
        item.mouseReleaseEvent(
            _event(QEvent.Type.GraphicsSceneMouseRelease,
                   start_scene + QPointF(dx, dy)))

    def test_aspect_math(self):
        from ui_editor.ui.canvas import aspect_resize

        # 角把手：宽的相对变化更大，按宽定比例（100x50 原点不动）
        self.assertEqual(aspect_resize("se", 10, 20, 100, 50, 50, 10),
                         (10, 20, 150, 75))
        # 角把手：高的相对变化更大，底边固定（上拉 30 → 高 80 宽 160）
        self.assertEqual(aspect_resize("ne", 10, 20, 100, 50, -20, -30),
                         (10, -10, 160, 80))
        # 右边把手：高度跟宽走，垂直居中
        self.assertEqual(aspect_resize("e", 10, 20, 100, 50, 30, 0),
                         (10, 12.5, 130, 65))
        # 左边把手：右边固定（往右拖 20 → 宽 80 高 40）
        self.assertEqual(aspect_resize("w", 10, 20, 100, 50, 20, 0),
                         (30, 25, 80, 40))
        # 顶边把手：宽度跟高走，水平居中（下压 10 → 高 40 宽 80）
        self.assertEqual(aspect_resize("n", 10, 20, 100, 50, 0, 10),
                         (20, 30, 80, 40))
        # 缩到极小仍保比例且不低于 8px
        x, y, w, h = aspect_resize("se", 10, 20, 100, 50, -98, -48)
        self.assertEqual((w, h), (16, 8))
        self.assertEqual(w / h, 2.0)
        # 原尺寸非法时原样返回，不除零
        self.assertEqual(aspect_resize("se", 1, 2, 0, 50, 5, 5),
                         (1, 2, 0, 50))

    def test_toolbar_toggle_and_drag_keeps_ratio(self):
        from PySide6.QtWidgets import QToolBar

        w = self.window
        button = self._add_button()
        bars = w.findChildren(QToolBar)
        self.assertIn(w._act_aspect, bars[0].actions())
        self.assertEqual(w._act_aspect.iconText(), "等比")
        self.assertFalse(w._act_aspect.icon().isNull())
        self.assertFalse(w.scene.keep_aspect)
        # 关着：自由缩放（拖右下角 +50/+10 → 150x60，比例变了）
        self._drag_handle(button, (100, 50), 50, 10)
        self.assertEqual((button.width, button.height), (150, 60))
        button.set_geometry(x=10, y=10, width=100, height=50)
        self.window.scene.refresh_widget(button)
        # 打开等比：同样拖法 → 150x75（保持 2:1）
        w._act_aspect.trigger()
        self.assertTrue(w.scene.keep_aspect)
        self._drag_handle(button, (100, 50), 50, 10)
        self.assertEqual((button.width, button.height), (150, 75))

    def test_shift_temporarily_keeps_ratio(self):
        from PySide6.QtCore import Qt

        button = self._add_button()
        self.assertFalse(self.window.scene.keep_aspect)
        self._drag_handle(button, (100, 50), 50, 10,
                          modifiers=Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual((button.width, button.height), (150, 75))


class TestZoomCallbackAfterTeardown(unittest.TestCase):
    """窗口销毁中画布补发缩放信号不得炸（0.5.0 原生反馈的崩溃）。

    _on_zoom_changed 若只判 hasattr，标签 C++ 对象已删时 setText
    抛 RuntimeError: libshiboken ... already deleted。
    """

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_zoom_handler_survives_deleted_label(self):
        from shiboken6 import delete, isValid

        from ui_editor.ui.main_window import MainWindow

        window = MainWindow()
        delete(window._zoom_label)  # 强制删 C++ 对象（复现销毁中补发信号）
        self.assertFalse(isValid(window._zoom_label))
        window._on_zoom_changed(1.5)  # 不得抛 RuntimeError
        window.close()
        window.deleteLater()
        self._app.processEvents()


class TestImagePicker(unittest.TestCase):
    """从资源包选择图片：对话框过滤/选择 + 属性面板已接解析器。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_filter_and_select(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        paths = ["combdialog4\\底板\\a.png",
                 "combdialog4\\新登陸介面\\底板800.png",
                 "dialog\\other.jpg"]
        dialog = ResourcePickerDialog(None, "t", paths, paths[0])
        self.assertEqual(dialog.selected_path(), paths[0])  # 当前值预选
        dialog._search.setText("底板800")
        self.assertEqual(dialog._list.count(), 1)
        item = dialog._list.item(0)
        dialog._list.setCurrentItem(item)
        self.assertEqual(dialog.selected_path(), paths[1])
        dialog._search.setText("")
        self.assertEqual(dialog._list.count(), 3)
        dialog.close()

    def test_export_writes_png_and_sprite_frames(self):
        import tempfile

        from PySide6.QtGui import QImage

        from ui_editor.ui.image_export import export_image_files

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            # 真 PNG：原样写出
            written = export_image_files(
                "a\\b.png", b"\x89PNG\r\n\x1a\nDATA", None, out_dir)
            self.assertEqual(written, [out_dir / "b.png"])
            self.assertEqual((out_dir / "b.png").read_bytes(),
                             b"\x89PNG\r\n\x1a\nDATA")
            # 精灵字节 + 帧：转成逐帧 PNG
            frame = QImage(3, 2, QImage.Format.Format_ARGB32)
            frame.fill(0xFF336699)
            sprite_data = b"I0" + b"\x00" * 30
            written = export_image_files(
                "a\\hero.png", sprite_data, [frame, frame], out_dir)
            self.assertEqual([p.name for p in written],
                             ["hero-0.png", "hero-1.png"])
            back = QImage(str(written[0]))
            self.assertEqual((back.width(), back.height()), (3, 2))

    def test_stage_one_collects_and_selects(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        staged: dict = {}
        dialog = ResourcePickerDialog(
            None, "t", ["a\\x.png"], "", None,
            on_stage=lambda p, d: staged.update({p: d}))
        dialog._stage_one("newdir\\pic.png", b"BYTES")
        self.assertEqual(staged, {"newdir\\pic.png": b"BYTES"})
        self.assertEqual(dialog.selected_path(), "newdir\\pic.png")
        dialog.close()

    def test_export_handler_receives_selection(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        got: list = []
        dialog = ResourcePickerDialog(
            None, "t", ["a\\x.png", "a\\y.png"], "", None,
            export_handler=got.extend)
        dialog._list.item(1).setSelected(True)
        dialog._choose_export()
        self.assertEqual(got, ["a\\y.png"])
        dialog.close()

    def test_add_staged_marks_and_selects(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        staged: dict = {}
        dialog = ResourcePickerDialog(
            None, "t", ["a\\x.png"], "", None,
            on_stage=lambda p, d: staged.update({p: d}))
        dialog.add_staged_path("newdir\\pic.png")
        self.assertEqual(dialog.selected_path(), "newdir\\pic.png")
        texts = [dialog._list.item(r).text()
                 for r in range(dialog._list.count())]
        self.assertTrue(any("（新）" in t for t in texts))
        dialog.close()

    def test_external_button_requests_fallback(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        dialog = ResourcePickerDialog(None, "t", ["a\\x.png"])
        dialog._choose_external()
        self.assertTrue(dialog.external_requested)

    def test_main_window_wires_resolver_to_props(self):
        from ui_editor.ui.main_window import MainWindow

        window = MainWindow()
        try:
            self.assertIs(window.props_panel.assets, window.resolver)
        finally:
            window.close()
            window.deleteLater()
            self._app.processEvents()


class TestUndoRedoGui(unittest.TestCase):
    """窗口层撤销：加控件可退、几何提交合并、选择按路径恢复。"""

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

    def test_undo_removes_added_widget_then_redo(self):
        w = self.window
        w.open_layout_file(str(FIXTURE))
        doc = w.doc
        assert doc is not None
        base = len(doc.all_widgets())
        w._select_widget(doc.roots[0])
        w.add_widget("CButton")
        self.assertEqual(len(doc.all_widgets()), base + 1)
        button = w.current_selection()
        path = w._selection_path(button)
        w.undo()
        self.assertEqual(len(doc.all_widgets()), base)
        w.redo()
        self.assertEqual(len(doc.all_widgets()), base + 1)
        # 选择按路径恢复到重建出来的按钮对象
        self.assertIsNotNone(w.current_selection())
        self.assertEqual(w._selection_path(w.current_selection()), path)

    def test_property_change_merges_into_one_step(self):
        w = self.window
        w.open_layout_file(str(FIXTURE))
        doc = w.doc
        assert doc is not None
        main = doc.roots[0]
        before = list(main.props.get("sTitle", ""))
        for text in ("甲", "乙", "丙"):
            main.props["sTitle"] = text
            w._on_property_changed(main, "sTitle")
        w.undo()
        self.assertEqual(
            w.doc.roots[0].props.get("sTitle", ""), "".join(before))
        self.assertFalse(w.doc.can_undo)  # 只用了一步就退完


class TestToolbar(unittest.TestCase):
    """顶部工具栏：高频动作齐备，撤销按钮与历史状态同步。"""

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

    def test_toolbar_actions_and_undo_state(self):
        from PySide6.QtWidgets import QToolBar

        w = self.window
        bars = w.findChildren(QToolBar)
        self.assertTrue(bars)
        actions = bars[0].actions()
        for expected in (w._act_open_file, w._act_open_pack, w._act_save,
                         w._act_save_pack, w._act_export_png,
                         w._undo_action, w._redo_action):
            self.assertIn(expected, actions)
            self.assertFalse(expected.icon().isNull())  # 带图标按钮
        from PySide6.QtCore import Qt as _Qt
        self.assertEqual(
            bars[0].toolButtonStyle(),
            _Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # 图标下带短字
        self.assertEqual(w._act_open_file.iconText(), "打开")
        self.assertEqual(w._act_save_pack.iconText(), "存包")
        self.assertFalse(w._undo_action.isEnabled())  # 没文档时不可撤销
        w.open_layout_file(str(FIXTURE))
        self.assertFalse(w._undo_action.isEnabled())  # 刚打开还没改
        doc = w.doc
        assert doc is not None
        w._select_widget(doc.roots[0])
        w.add_widget("CButton")
        self.assertTrue(w._undo_action.isEnabled())   # 改完可撤销
        self.assertFalse(w._redo_action.isEnabled())
        w.undo()
        self.assertTrue(w._redo_action.isEnabled())


class TestAlignGridZoom(unittest.TestCase):
    """M3.1：画布对齐/网格/缩放百分比入口行为。"""

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

    def _select_widgets(self, widgets):
        for item in self.window.scene.items():
            if hasattr(item, "widget") and item.widget in widgets:
                item.setSelected(True)

    def test_align_left_to_reference(self):
        w = self.window
        w.open_layout_file(str(FIXTURE))
        doc = w.doc
        assert doc is not None
        # 该布局的 UI_INFO 是平级列表：四个控件都是顶层同级
        _frame, button, box, image = doc.roots
        self._select_widgets([button, box, image])
        w.apply_alignment("left")  # 基准=文档顺序最靠前者（按钮 x=10）
        self.assertEqual(box.x, button.x)
        self.assertEqual(image.x, button.x)
        w.undo()  # 对齐算一步，可退回（撤销会重建对象，从文档读）
        self.assertEqual(w.doc.roots[2].x, 0)

    def test_grid_toggle_and_zoom_label(self):
        w = self.window
        self.assertFalse(w.scene.show_grid)
        w._act_grid.trigger()
        self.assertTrue(w.scene.show_grid)
        w.view.actual_size()
        self.assertEqual(w._zoom_label.text(), "缩放 100%")
        w.view.zoom_changed.emit(2.5)
        self.assertEqual(w._zoom_label.text(), "缩放 250%")


class TestButtonStatePreview(unittest.TestCase):
    """M3.2：竖条三态图在按下态预览画中段、正常态整图，像素不同。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()

    def tearDown(self):
        self.window.ctx.button_state = "normal"
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_pressed_state_changes_rendered_pixels(self):
        import tempfile

        from PySide6.QtGui import QColor, QImage, QPainter

        with tempfile.TemporaryDirectory() as tmp:
            strip = QImage(80, 72, QImage.Format.Format_ARGB32)
            painter = QPainter(strip)
            painter.fillRect(0, 0, 80, 24, QColor(200, 0, 0))
            painter.fillRect(0, 24, 80, 24, QColor(0, 200, 0))
            painter.fillRect(0, 48, 80, 24, QColor(0, 0, 200))
            painter.end()
            strip_path = Path(tmp) / "strip.png"
            self.assertTrue(strip.save(str(strip_path)))

            w = self.window
            w.new_layout()
            doc = w.doc
            assert doc is not None
            w.resolver.mount_dir(tmp)
            frame = doc.roots[0]
            w._select_widget(frame)
            w.add_widget("CButton")
            button = w.current_selection()
            button.set_geometry(x=10, y=20, width=80, height=24)
            button.props["sFileName"] = "strip.png"
            w.scene.refresh_all()

            def sample() -> tuple[int, int, int]:
                image = w.view.export_image()
                rect = w.scene.itemsBoundingRect()
                color = image.pixelColor(int(50 - rect.left()),
                                         int(26 - rect.top()))
                return color.red(), color.green(), color.blue()

            normal = sample()
            w.set_button_state("pressed")
            pressed = sample()
            self.assertNotEqual(normal, pressed)
            # 按下态取竖条中段（纯绿），各分量以绿为主
            self.assertGreater(pressed[1], 150)
            self.assertLess(pressed[0], 80)
