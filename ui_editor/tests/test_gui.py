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
