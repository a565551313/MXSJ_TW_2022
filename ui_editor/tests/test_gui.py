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
            with mock.patch("ui_editor.ui.save_workflows.SaveReviewDialog.exec",
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


def _multi_pack_bytes(entries) -> bytes:
    """自建微型 0SLF 包：``[(包内路径, 原始字节)]``，任意条数。"""
    import struct

    from ui_editor.core.mxhash import mx_hash

    body = bytearray()
    meta = []
    offset = 12
    for name, payload in entries:
        meta.append((mx_hash(name.encode("gbk")), 12345, len(payload), offset))
        body += payload
        offset += len(payload)
    head = b"0SLF" + struct.pack("<II", len(entries), offset)

    def record(index, entry_id, r1, clen, doff):
        r2 = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ clen) & 0xFFFFFFFF
        r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF)
              ^ doff) & 0xFFFFFFFF
        return struct.pack("<IIII", entry_id, r1, r2, r3)

    return head + bytes(body) + b"".join(
        record(index, *item) for index, item in enumerate(meta))


def _write_png(path, red: int = 40):
    """写一张真 PNG（新建族要按内容/后缀处理，伪头不行）。"""
    from PySide6.QtGui import QColor, QImage

    image = QImage(9, 12, QImage.Format.Format_ARGB32)
    image.fill(QColor(red, 70, 130))
    assert image.save(str(path))
    return str(path)


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
        from ui_editor.ui import workflows as workflow_module
        from ui_editor.ui.main_window import MainWindow

        window = MainWindow()
        small_catalog = ["dialog/cateroom.dlg", "dialog/gone.dlg"]
        old_main = workflow_module.known_layout_paths
        old_assets = assets_module.known_layout_paths
        workflow_module.known_layout_paths = lambda: list(small_catalog)
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
            workflow_module.known_layout_paths = old_main
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

    def test_resource_dir_hides_pack_without_layouts(self):
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
            self.assertFalse(any("item.fls" in t for t in self._visible_texts()))
            self.assertIsNotNone(self.window.resolver.pack_for(Path(tmp) / "item.fls"))
            self.window.refresh_sources()
            self.assertEqual(self.window.resource_panel.root_count(), 1)
            self.assertFalse(any("item.fls" in t for t in self._visible_texts()))

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


class TestSaveNewFamilyToPack(unittest.TestCase):
    """新建的拼名族随布局写进新包：布局只引用目录，子图也要一起写。"""

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

    def test_staged_family_written_with_pack(self):
        import tempfile

        from ui_editor.core import dlg_codec
        from ui_editor.core.assets import AssetResolver

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root", "lChildren": [
                {"sWidgetType": "CTextButton", "sName": "login",
                 "sFileName": ""}]}],
            md5="0" * 32)
        key = b"\x5a\xa5\x11\x7e"
        packed = bytes(b ^ key[i & 3] for i, b in enumerate(plain))
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "interface_mini.fls"
            pack_path.write_bytes(_multi_pack_bytes([
                ("dialog/fam.dlg", packed)]))
            self.window.open_pack_file(str(pack_path))
            self.window._open_pack_layout(str(pack_path), "dialog/fam.dlg")
            doc = self.window.doc
            widget = next(item for item in doc.all_widgets()
                          if item.props.get("sName") == "login")
            payloads = {}
            src_dir = Path(tmp) / "src"
            src_dir.mkdir()
            for index, name in enumerate(("0l", "0c", "0r")):
                path = _write_png(src_dir / f"{name}.png", 40 + index)
                data = Path(path).read_bytes()
                payloads[name] = data
                self.window.resolver.stage_image(
                    base + name + ".png", data)
            widget.props["sFileName"] = base
            doc.dirty = True
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertIsNotNone(report)
            self.assertTrue(report.get("ok"), report)
            # 布局只引用目录：子图若没被认成"被引用"，这里会是 0
            self.assertEqual(report.get("images_added"), 3)
            self.assertEqual(report.get("staged_unreferenced"), [])
            self.assertEqual(self.window.resolver.staged_images(), {})
            fresh = AssetResolver()
            fresh.mount_pack(out)
            try:
                got = fresh.fetch_dlg("dialog/fam.dlg")
                self.assertIsNotNone(got)
                self.assertEqual(got[0][0]["lChildren"][0]["sFileName"], base)
                for name, data in payloads.items():
                    self.assertEqual(fresh.fetch_bytes(base + name + ".png"),
                                     data)
                # 包里齐了整族 → 解析器能拼出这张按钮
                self.assertTrue(fresh.fetch_image(base))
            finally:
                fresh.close()


class TestSaveFamilyOverExistingButton(unittest.TestCase):
    """指向已有按钮的目录 = 替换它那几张图（不是新增），报告要如实计数。"""

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

    def test_family_into_existing_directory_replaces_pieces(self):
        import tempfile

        from ui_editor.core import dlg_codec
        from ui_editor.core.assets import AssetResolver

        base = "test/btn\\"
        old_data = {name: f"\x89PNGold{name}".encode()
                    for name in ("0l", "0c", "0r")}
        plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root", "lChildren": [
                {"sWidgetType": "CTextButton", "sName": "login",
                 "sFileName": base}]}],
            md5="0" * 32)
        key = b"\x5a\xa5\x11\x7e"
        packed = bytes(b ^ key[i & 3] for i, b in enumerate(plain))
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "interface_mini.fls"
            pack_path.write_bytes(_multi_pack_bytes(
                [("dialog/fam.dlg", packed)]
                + [(f"test/btn/{name}.png", data)
                   for name, data in old_data.items()]))
            self.window.open_pack_file(str(pack_path))
            self.window._open_pack_layout(str(pack_path), "dialog/fam.dlg")
            src_dir = Path(tmp) / "src"
            src_dir.mkdir()
            new_data = {}
            for index, name in enumerate(("0l", "0c", "0r")):
                path = _write_png(src_dir / f"{name}.png", 90 + index)
                new_data[name] = Path(path).read_bytes()
                self.window.resolver.stage_image(
                    "test/btn/" + name + ".png", new_data[name])
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertIsNotNone(report)
            self.assertTrue(report.get("ok"), report)
            self.assertEqual(report.get("images_added"), 0)
            self.assertEqual(report.get("images_replaced"), 3)
            fresh = AssetResolver()
            fresh.mount_pack(out)
            try:
                for name, data in new_data.items():
                    self.assertEqual(
                        fresh.fetch_bytes("test/btn/" + name + ".png"), data)
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
                "newdir/未用上的圖.png", b"\x89PNGunused")
            doc.dirty = True
            out = str(Path(tmp) / "interface_patched.fls")
            report = self.window.write_pack_copy(out)
            self.assertTrue(report.get("ok"), report)
            self.assertEqual(report.get("images_added"), 0)
            # 0.11.0 起挂账键统一成 "/" 分隔（报告与挂账同一写法）
            self.assertEqual(report.get("staged_unreferenced"),
                             ["newdir/未用上的圖.png"])
            self.assertEqual(report.get("entries_after"), 1)  # 原包 1 条、无新增
            # 账未销：还在挂账里，可换个布局再保存写入
            self.assertIn("newdir/未用上的圖.png",
                          self.window.resolver.staged_images())
            from ui_editor.core.pack import FlsPack
            with FlsPack(out) as pack:
                self.assertEqual(pack.count, 1)
                self.assertFalse(pack.contains("newdir/未用上的圖.png"))


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
        # 重名的副本自动加后缀（BTN → BTN_1），避免顶掉脚本对原名的认领
        self.assertEqual(pasted.name, f"{button.name}_1")
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
        # 根控件在迷你包里是 0x0（靠图片撑开），这里显式给大画布，
        # 免得子控件缩放被「父就是子画布」的夹取规则挡住。
        self.doc.roots[0].set_geometry(width=400, height=300)
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
        # 锁定后画布完全无视它：连可选标志都不给（点不到/选不中）
        self.assertFalse(item.flags()
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
        # 根控件在迷你包里是 0x0（靠图片撑开），显式给大画布，
        # 让等比缩放的数值不被父矩形夹住。
        self.doc.roots[0].set_geometry(width=400, height=300)
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

    def test_dir_base_family_listed_and_selectable(self):
        """目录型基路径（按钮三态）要能选：标签带族说明，选中回写目录路径。"""
        from ui_editor.ui.image_picker import ResourcePickerDialog

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        paths = [base, "combdialog4\\新登陆界面\\底板.png"]
        dialog = ResourcePickerDialog(
            None, "t", paths, "", None,
            family_label=lambda _p: "三态横片 · 2 态")
        labels = [dialog._list.item(row).text()
                  for row in range(dialog._list.count())]
        self.assertIn("登录按钮（三态横片 · 2 态）", labels)
        self.assertTrue(dialog._only_families.isVisibleTo(dialog))
        dialog._list.setCurrentItem(dialog._list.item(0))
        self.assertEqual(dialog.selected_path(), base)
        self.assertIn("拼名族", dialog._list.item(0).toolTip())
        # 「只看拼名族」把普通图片滤掉
        dialog._only_families.setChecked(True)
        self.assertEqual(dialog._list.count(), 1)
        dialog.close()

    def test_plain_files_hide_family_filter(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        dialog = ResourcePickerDialog(None, "t", ["a\\b.png"], "")
        self.assertFalse(dialog._only_families.isVisibleTo(dialog))
        self.assertEqual(dialog._list.count(), 1)
        dialog.close()

    def test_family_labels_are_cached_between_filters(self):
        """族标签要探文件系统：搜索框每敲一个字不能把几百个族重算一遍。"""
        from ui_editor.ui.image_picker import ResourcePickerDialog

        bases = ["combdialog4\\按钮\\登录按钮\\",
                 "combdialog4\\按钮\\注册按钮\\",
                 "combdialog4\\按钮\\退出按钮\\"]
        calls: list = []

        def label(path):
            calls.append(path)
            return "按钮横片 · 1 态"

        dialog = ResourcePickerDialog(
            None, "t", bases + ["a\\bg.png"], "", None, family_label=label)
        self.assertEqual(sorted(calls), sorted(bases))   # 打开时算一次
        calls.clear()
        for text in ("按", "按钮", "登录", ""):
            dialog._search.setText(text)
            dialog._refilter()
        self.assertEqual(calls, [])                      # 之后都走缓存
        dialog.close()

    def test_property_panel_lists_dir_base_family(self):
        """属性面板「从资源包选择」要列出拼名族，选中即写进 sFileName。"""
        from PySide6.QtWidgets import QDialog, QFileDialog, QLineEdit

        from ui_editor.core.model import Widget
        from ui_editor.ui.property_panel import PropertyPanel

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        other = "combdialog4\\新登陆界面\\三态按钮\\注册按钮\\"
        assets = mock.Mock()
        assets._packs = [object()]
        assets.candidates_with_staged.return_value = [base, other, "a\\bg.png"]
        pieces = {family + name + ".png"
                  for family in (base, other)
                  for name in ("0l", "0c", "0r", "1l", "1c", "1r")}
        assets.resource_exists.side_effect = (
            lambda name: name.replace("/", "\\") in pieces)
        assets.fetch_image.return_value = None
        assets.pack_paths = []
        panel = PropertyPanel()
        widget = Widget({"sWidgetType": "CTextButton", "sName": "b",
                         "sFileName": ""})
        panel._widget = widget
        panel.assets = assets
        edit = QLineEdit()
        captured: dict = {}

        def fake_dialog(_parent, _title, paths, current="", thumb=None,
                        on_stage=None, export_handler=None,
                        family_label=None, **_kwargs):
            captured["paths"] = list(paths)
            captured["family_label"] = family_label
            captured["kwargs"] = _kwargs
            handle = mock.Mock()
            handle.exec.return_value = QDialog.DialogCode.Accepted
            handle.selected_path.return_value = base
            handle.external_requested = False
            return handle

        def fake_dialog2(_parent, _title, paths, current="", thumb=None,
                         on_stage=None, export_handler=None,
                         family_label=None, **kwargs):
            captured["export_handler"] = export_handler
            return fake_dialog(_parent, _title, paths, current, thumb,
                               on_stage, export_handler, family_label, **kwargs)

        with mock.patch("ui_editor.ui.image_picker.ResourcePickerDialog",
                        side_effect=fake_dialog2):
            self.assertTrue(panel._browse_from_pack("sFileName", edit))
        self.assertIn(base, captured["paths"])
        self.assertIn("按钮横片", captured["family_label"](base))
        # 新建族要按控件类型预选族类型，并知道包里有没有同名条目
        self.assertEqual(captured["kwargs"]["widget_type"], "CTextButton")
        self.assertIs(captured["kwargs"]["exists"], assets.resource_exists)
        self.assertEqual(widget.props["sFileName"], base)
        self.assertEqual(edit.text(), base)

        # 在选图窗里对拼名族点「导出图片…」：按族内每块子图导出
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
        assets.fetch_bytes.side_effect = lambda name: png
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    QFileDialog, "getExistingDirectory", return_value=tmp), \
                    mock.patch.object(QFileDialog, "getSaveFileName") as save, \
                    mock.patch("ui_editor.ui.property_panel.QMessageBox"):
                captured["export_handler"]([base])
            self.assertFalse(save.called)   # 族不该走「另存为单文件」
            names = sorted(p.name for p in Path(tmp).iterdir())
            self.assertEqual(names, ["0c.png", "0l.png", "0r.png",
                                     "1c.png", "1l.png", "1r.png"])
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    QFileDialog, "getExistingDirectory", return_value=tmp), \
                    mock.patch.object(QFileDialog, "getSaveFileName") as save, \
                    mock.patch("ui_editor.ui.property_panel.QMessageBox"):
                captured["export_handler"]([base, other])
            self.assertFalse(save.called)
            self.assertEqual(
                sorted(p.name for p in Path(tmp).iterdir()),
                ["注册按钮-0c.png", "注册按钮-0l.png", "注册按钮-0r.png",
                 "注册按钮-1c.png", "注册按钮-1l.png", "注册按钮-1r.png",
                 "登录按钮-0c.png", "登录按钮-0l.png", "登录按钮-0r.png",
                 "登录按钮-1c.png", "登录按钮-1l.png", "登录按钮-1r.png"])

        # 族里有子图读不出：要明说，不能悄悄少导一张
        def picky(name):
            if name.endswith("0c.png"):
                raise ValueError("坏图")
            return png

        assets.fetch_bytes.side_effect = picky
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    QFileDialog, "getExistingDirectory", return_value=tmp), \
                    mock.patch("ui_editor.ui.property_panel.QMessageBox") as box:
                captured["export_handler"]([base])
            self.assertEqual(len(list(Path(tmp).iterdir())), 5)  # 6 块少 1
            message = box.information.call_args[0][2]
        self.assertIn("子图读不出", message)
        self.assertIn("0c.png", message)
        panel.deleteLater()

    def test_family_dialog_maps_by_name_not_order(self):
        """文件名叫 0l/0c/0r 时按名字对应，选择顺序打乱也不会配错。"""
        from PySide6.QtWidgets import QDialogButtonBox

        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 40 + index)
                     for index, name in enumerate(("0r", "0l", "0c"))]
            dialog = FamilyImportDialog(None, files, "", "h_state", ".png")
            dialog._base.setText("combdialog4\\新登陆界面\\登录按钮\\")
            pairs, error = dialog._family_pairs()
            self.assertIsNone(error)
            self.assertEqual([rel for rel, _path in pairs],
                             ["0l", "0c", "0r"])          # 族内顺序
            self.assertEqual([Path(path).name for _rel, path in pairs],
                             ["0l.png", "0c.png", "0r.png"])
            self.assertIn("按名字对应", dialog._hint.text())
            self.assertIn("0l.png", dialog._preview.toPlainText())
            ok = dialog._buttons.button(
                QDialogButtonBox.StandardButton.Ok)
            self.assertTrue(ok.isEnabled())
            dialog.close()

    def test_exported_whole_images_are_not_turned_into_slices(self):
        """3 张整图（导出回来的 0/1/2.png）默认必须是序号帧，不是按钮横片。

        旧实现无条件按控件类型来：按钮控件 + 0/1/2.png → 0l/0c/0r，
        三张**整**按钮图各取三分之一拼成一条（用户报「三张图拼在一起」）。
        """
        from ui_editor.ui.image_picker import choose_family_kind

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{index}.png", 20 + index)
                     for index in range(3)]
            self.assertEqual(choose_family_kind(files, "CTextButton"),
                             "frames")
            self.assertEqual(choose_family_kind(files, None), "frames")
            # 文件名已经是族内名（0l/0c/0r）就当按钮横片
            slices = [_write_png(Path(tmp) / f"0{side}.png", 20 + index)
                      for index, side in enumerate("lcr")]
            self.assertEqual(choose_family_kind(slices, "CTextButton"),
                             "h_state")

    def test_position_words_follow_the_widget(self):
        """left/middle/right 是"位置"：按钮上要 0l/0c/0r，边框上才是 h_slice。"""
        from ui_editor.ui.image_picker import choose_family_kind

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 20 + index)
                     for index, name in enumerate(
                         ("left", "middle", "right"))]
            self.assertEqual(choose_family_kind(files, "CTextButton"),
                             "h_state")
            self.assertEqual(choose_family_kind(files, "CHPngFrame"),
                             "h_slice")
            # 没有控件类型时不该瞎猜成按钮
            self.assertEqual(choose_family_kind(files, None), "h_slice")

    def test_family_dialog_preview_differs_by_kind(self):
        """保存前就要能看出"拼成一条"还是"一整张"：预览图必须不同。"""
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{index}.png", 20 + index)
                     for index in range(3)]
            shots = {}
            for kind in ("h_state", "frames"):
                dialog = FamilyImportDialog(None, files, "", kind, ".png")
                pixmap = dialog._pic.pixmap()
                self.assertIsNotNone(pixmap)
                shots[kind] = (pixmap.width(), pixmap.height())
                self.assertIn("拼出来是这样", dialog._pic_caption.text())
                dialog.close()
        # 按钮横片 = 三片并排（宽约 3 倍）；序号帧 = 一张
        self.assertGreater(shots["h_state"][0], shots["frames"][0] * 2)

    def test_picker_says_what_is_inside_a_directory(self):
        """选中一个目录型基路径时，要直接说明里面有哪些图、游戏怎么用。"""
        from ui_editor.ui.image_picker import ResourcePickerDialog

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        dialog = ResourcePickerDialog(
            None, "t", [base], base, None,
            family_label=lambda _p: "按钮横片 · 1 态",
            family_pieces=lambda _p: ["0l.png", "0c.png", "0r.png"],
            family_kind=lambda _p: "h_state")
        dialog._list.setCurrentItem(dialog._list.item(0))
        detail = dialog._detail.text()
        self.assertTrue(dialog._detail.isVisibleTo(dialog))
        self.assertIn("0l.png", detail)
        self.assertIn("拉伸", detail)        # 说明它是一片而不是一整张
        dialog.close()

    def test_family_dialog_explains_how_many_images_are_a_button(self):
        """最容易犯迷糊的地方：3 张 = 1 个状态，不是"必须三态"。"""
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            three = [_write_png(Path(tmp) / f"{name}.png")
                     for name in ("0l", "0c", "0r")]
            dialog = FamilyImportDialog(None, three, "", "h_state", ".png")
            summary = dialog.summary_text()
            self.assertIn("3 张 = 按钮的 1 个状态", summary)
            self.assertIn("拉伸", summary)
            # 用户报「3 张整图被拼成一条」：这里必须直说每张只是三分之一，
            # 并指向序号帧
            self.assertIn("三分之一", summary)
            self.assertNotIn("**", summary)   # 界面上不该出现 markdown 记号
            self.assertIn("序号帧", summary)
            dialog.close()

            six = [_write_png(Path(tmp) / f"{index}{side}.png", 20 + index)
                   for index in (0, 1) for side in "lcr"]
            dialog = FamilyImportDialog(None, six, "", "h_state", ".png")
            self.assertIn("2 个状态", dialog.summary_text())
            self.assertIn("常态", dialog.summary_text())
            dialog.close()

            nine = [_write_png(Path(tmp) / f"{row}-{column}.png",
                               20 + index)
                    for index, (row, column) in enumerate(
                        (r, c) for r in ("top", "middle", "bottom")
                        for c in ("left", "middle", "right"))]
            dialog = FamilyImportDialog(None, nine, "", "nine_slice", ".png")
            self.assertIn("四角不动", dialog.summary_text())
            dialog.close()

    def test_family_dialog_blocks_four_images_for_a_button(self):
        from PySide6.QtWidgets import QDialogButtonBox

        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{index}.png", 20 + index)
                     for index in range(4)]
            dialog = FamilyImportDialog(None, files, "", "h_state", ".png")
            dialog._base.setText("a\\b\\")
            self.assertIn("不是 3 的倍数", dialog.summary_text())
            self.assertFalse(dialog._buttons.button(
                QDialogButtonBox.StandardButton.Ok).isEnabled())
            dialog.close()

    def test_suggest_free_base_skips_taken_names(self):
        from ui_editor.ui.image_picker import suggest_free_base

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        taken = {base + name + ".png" for name in ("0l", "0c", "0r")}
        self.assertEqual(suggest_free_base(base, lambda _b: 0), base)
        self.assertEqual(
            suggest_free_base(base, lambda candidate: sum(
                1 for name in ("0l", "0c", "0r")
                if candidate + name + ".png" in taken)),
            "combdialog4\\新登陆界面\\三态按钮\\登录按钮_2\\")

    def test_family_dialog_warns_before_overwriting_a_button(self):
        """目录已经是别的按钮的素材：必须红字说明会替换，并给出换目录的办法。"""
        from PySide6.QtWidgets import QDialogButtonBox

        from ui_editor.ui.image_picker import FamilyImportDialog

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        taken = {base + name + ".png" for name in ("0l", "0c", "0r")}
        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 30 + index)
                     for index, name in enumerate(("0l", "0c", "0r"))]
            dialog = FamilyImportDialog(
                None, files, base, "h_state", ".png",
                lambda name: name in taken)
            self.assertIn("已经有 3 张同名图", dialog._warning.text())
            self.assertIn("替换", dialog._warning.text())
            self.assertIn("（替换）", dialog._preview.toPlainText())
            ok = dialog._buttons.button(
                QDialogButtonBox.StandardButton.Ok)
            self.assertEqual(ok.text(), "替换 3 张")
            self.assertTrue(dialog._free_btn.isVisibleTo(dialog))
            dialog._use_free_base()
            self.assertEqual(dialog._base.text(),
                             "combdialog4\\新登陆界面\\三态按钮\\登录按钮_2\\")
            self.assertEqual(dialog._warning.text(), "")
            self.assertEqual(ok.text(), "写入新族")
            dialog.close()

    def test_family_dialog_counts_other_extension_as_conflict(self):
        """目录里已有 .igs 一族、现在导入 PNG：也必须算冲突。

        只看 self.ext 会漏掉它：保存后目录里 .png 与 .igs 并存，而
        dir_base 先试 .png——原按钮的图就被顶掉了，「换新目录」还会把
        这个并不空的目录当成空闲目录。
        """
        from PySide6.QtWidgets import QDialogButtonBox

        from ui_editor.ui.image_picker import FamilyImportDialog

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        taken = {base + name + ".igs" for name in ("0l", "0c", "0r")}
        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 40 + index)
                     for index, name in enumerate(("0l", "0c", "0r"))]
            dialog = FamilyImportDialog(
                None, files, base, "h_state", ".png",
                lambda name: name in taken)
            self.assertIn("已经有 3 张同名图", dialog._warning.text())
            ok = dialog._buttons.button(
                QDialogButtonBox.StandardButton.Ok)
            self.assertEqual(ok.text(), "替换 3 张")
            dialog._use_free_base()
            self.assertEqual(dialog._base.text(),
                             "combdialog4\\新登陆界面\\三态按钮\\登录按钮_2\\")
            self.assertEqual(ok.text(), "写入新族")
            dialog.close()

    def test_family_dialog_no_warning_for_a_new_directory(self):
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png")
                     for name in ("0l", "0c", "0r")]
            dialog = FamilyImportDialog(
                None, files, "新目录\\", "h_state", ".png",
                lambda _name: False)
            self.assertEqual(dialog._warning.text(), "")
            self.assertFalse(dialog._free_btn.isVisibleTo(dialog))
            dialog.close()

    def test_family_dialog_orders_unknown_names_by_filename(self):
        """文件名认不出左右/上下时：按文件名自然排序依次对应，并给出命名建议。"""
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / name, 60 + index)
                     for index, name in enumerate(
                         ("a.png", "b.png", "c.png"))]
            dialog = FamilyImportDialog(None, files, "", "h_slice", ".png")
            dialog._base.setText("a\\b\\")
            pairs, _error = dialog._family_pairs()
            self.assertEqual([rel for rel, _path in pairs],
                             ["left", "middle", "right"])
            self.assertEqual([Path(path).name for _rel, path in pairs],
                             ["a.png", "b.png", "c.png"])
            self.assertIn("已按文件名排序", dialog._hint.text())
            self.assertIn("命名建议", dialog._hint.text())
            dialog.close()

    def test_family_dialog_recognises_chinese_piece_names(self):
        """自己起名也能认：左/中/右、左上/右下 都按名字对应，与选择顺序无关。"""
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            names = ["右", "左", "中"]
            files = [_write_png(Path(tmp) / f"{name}.png", 70 + index)
                     for index, name in enumerate(names)]
            dialog = FamilyImportDialog(None, files, "", "h_state", ".png")
            pairs, _error = dialog._family_pairs()
            self.assertEqual([rel for rel, _path in pairs],
                             ["0l", "0c", "0r"])
            self.assertEqual([Path(path).name for _rel, path in pairs],
                             ["左.png", "中.png", "右.png"])
            self.assertEqual(dialog.order_rule, "alias")
            self.assertIn("按文件名认出", dialog._hint.text())
            dialog.close()

    def test_widget_type_wins_over_left_middle_right_names(self):
        """按钮控件 + 文件叫 left/middle/right：要写 0l/0c/0r，不是横三片。

        写成 left.png/middle.png/right.png，游戏找 0l/0c/0r 就什么也画不出来。
        """
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 60 + index)
                     for index, name in enumerate(("left", "middle", "right"))]
            dialog = FamilyImportDialog(None, files, "", "h_state", ".png")
            pairs, _error = dialog._family_pairs()
            self.assertEqual([rel for rel, _p in pairs],
                             ["0l", "0c", "0r"])
            self.assertIn("文件名更像", dialog._hint.text())
            dialog.close()

    def test_nine_slice_names_override_button_default(self):
        """9 张按 top-left… 命名时，即使控件是按钮也按九片处理。"""
        from PySide6.QtWidgets import QDialog

        from ui_editor.ui.image_picker import (
            FamilyImportDialog,
            ResourcePickerDialog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{row}-{column}.png", 20 + index)
                     for index, (row, column) in enumerate(
                         (r, c) for r in ("top", "middle", "bottom")
                         for c in ("left", "middle", "right"))]
            dialog = ResourcePickerDialog(
                None, "t", [], "", None,
                on_stage=lambda _p, _d: None,
                widget_type="CTextButton",
                exists=lambda _name: False)
            seen = {}

            def auto_accept(inner):
                seen["kind"] = inner._kind.currentData()
                inner.accept()
                return QDialog.DialogCode.Accepted

            with mock.patch(
                    "ui_editor.ui.image_picker.QFileDialog.getOpenFileNames",
                    return_value=(files, "")), \
                    mock.patch.object(FamilyImportDialog, "exec", auto_accept):
                dialog._choose_family()
            self.assertEqual(seen["kind"], "nine_slice")
            dialog.close()

    def test_family_dialog_natural_sorts_numbered_names(self):
        """10.png 不能被排到 2.png 前面。"""
        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / name, 80 + index)
                     for index, name in enumerate(
                         ("10.png", "2.png", "1.png"))]
            dialog = FamilyImportDialog(None, files, "", "frames", ".png")
            pairs, _error = dialog._family_pairs()
            self.assertEqual([Path(path).name for _rel, path in pairs],
                             ["1.png", "2.png", "10.png"])
            self.assertEqual([rel for rel, _path in pairs], ["0", "1", "2"])
            dialog.close()

    def test_family_dialog_rejects_file_name_as_directory(self):
        from PySide6.QtWidgets import QDialogButtonBox

        from ui_editor.ui.image_picker import FamilyImportDialog

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png")
                     for name in ("0l", "0c", "0r")]
            dialog = FamilyImportDialog(None, files, "", "h_state", ".png")
            dialog._base.setText("combdialog4\\新登陆界面\\登录按钮.png")
            ok = dialog._buttons.button(
                QDialogButtonBox.StandardButton.Ok)
            self.assertFalse(ok.isEnabled())
            self.assertIn("这是文件名", dialog._hint.text())
            # 补成目录就放行
            dialog._base.setText("combdialog4\\新登陆界面\\登录按钮")
            self.assertTrue(ok.isEnabled())
            self.assertEqual(dialog._normalised_base()[0],
                             "combdialog4\\新登陆界面\\登录按钮\\")
            dialog.close()

    def test_new_family_stages_all_pieces_and_selects_directory(self):
        """3 张图 → 一个按钮：整族挂账、选中目录、候选里只剩族。"""
        from PySide6.QtWidgets import QDialog

        from ui_editor.ui.image_picker import (
            FamilyImportDialog,
            ResourcePickerDialog,
        )

        base = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"
        staged: dict = {}
        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 30 + index)
                     for index, name in enumerate(("0l", "0c", "0r"))]
            dialog = ResourcePickerDialog(
                None, "t", [], "", None,
                on_stage=lambda path, data: staged.update({path: data}),
                widget_type="CTextButton",
                exists=lambda name: False)

            def auto_accept(inner):
                inner._base.setText(base)
                inner.accept()
                return QDialog.DialogCode.Accepted

            with mock.patch(
                    "ui_editor.ui.image_picker.QFileDialog.getOpenFileNames",
                    return_value=(files, "")), \
                    mock.patch.object(FamilyImportDialog, "exec", auto_accept):
                dialog._choose_family()
            self.assertEqual(sorted(staged), [base + "0c.png", base + "0l.png",
                                              base + "0r.png"])
            self.assertEqual(dialog.selected_path(), base)
            self.assertEqual(dialog._list.count(), 1)   # 只列族本身
            self.assertIn("已挂账 3 张子图", dialog._count.text())
            dialog.close()

    def test_family_payloads_keep_caller_paths_as_keys(self):
        """payloads 的键必须就是传进来的原串：_stage_family 拿它取图。

        ``str(Path(name))`` 会规范化分隔符（Windows 上前斜杠→反斜杠），
        两边的键对不上就是 KeyError，新建族整条流程挂掉。
        """
        from ui_editor.ui.image_picker import prepare_family_payloads

        with tempfile.TemporaryDirectory() as tmp:
            files = [_write_png(Path(tmp) / f"{name}.png", 20 + index)
                     for index, name in enumerate(("0l", "0c", "0r"))]
            # 带 "./" 的写法：Path 会把它规范化掉，原串不会
            odd = [f"{tmp}/./{Path(path).name}" for path in files]
            payloads, ext = prepare_family_payloads(odd)
            self.assertEqual(ext, ".png")
            self.assertEqual(set(payloads), set(odd))

    def test_new_family_mixes_igs_and_images_rejected(self):
        from ui_editor.ui.image_picker import prepare_family_payloads

        with tempfile.TemporaryDirectory() as tmp:
            png = _write_png(Path(tmp) / "0l.png")
            igs = Path(tmp) / "0c.igs"
            igs.write_bytes(b"I0" + b"\x00" * 20)
            with self.assertRaises(ValueError) as caught:
                prepare_family_payloads([png, str(igs)])
            self.assertIn("同一种扩展名", str(caught.exception))

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

    def test_stage_one_rejects_bad_name_with_message(self):
        """名字含 GBK 不可编码字符：拦下来并弹提示（不能静默）。"""
        from ui_editor.ui.image_picker import ResourcePickerDialog

        staged: dict = {}
        dialog = ResourcePickerDialog(
            None, "t", [], "", None,
            on_stage=lambda p, d: staged.update({p: d}))
        dialog._on_stage = mock.Mock(side_effect=ValueError(
            "资源路径含 GBK 不可编码字符：'images/😀.png'"))
        with mock.patch(
                "ui_editor.ui.image_picker.QMessageBox.warning") as warning:
            dialog._stage_one("images/😀.png", b"X")
        self.assertEqual(staged, {})
        self.assertIn("这个名字不能用", warning.call_args[0][1])
        self.assertNotIn("images/😀.png", dialog.selected_path() or "")
        dialog.close()

    def test_export_handler_receives_selection(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        got: list = []
        dialog = ResourcePickerDialog(
            None, "t", ["a\\x.png", "a\\y.png"], "", None,
            export_handler=lambda paths, _dlg: got.extend(paths))
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


class TestWidgetTreeHeader(unittest.TestCase):
    """控件树名称列拉伸占满面板宽（回归：列宽够却显示 …）。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_name_column_stretches_lock_column_fixed(self):
        from PySide6.QtWidgets import QHeaderView

        from ui_editor.ui.panels import WidgetTreePanel

        panel = WidgetTreePanel()
        tree = panel._tree
        self.assertEqual(tree.columnCount(), 2)
        header = tree.header()
        self.assertEqual(header.sectionResizeMode(0),
                         QHeaderView.ResizeMode.Stretch)
        self.assertEqual(header.sectionResizeMode(1),
                         QHeaderView.ResizeMode.Fixed)
        # 锁图标列固定为窄列（不同样式会带 1~2px 边距）
        self.assertLessEqual(tree.columnWidth(1), 30)
        self.assertGreaterEqual(tree.columnWidth(1), 24)
        self.assertFalse(header.stretchLastSection())
