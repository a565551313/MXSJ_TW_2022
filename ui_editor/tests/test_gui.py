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


class _FakePackDialog:
    """替身：替代文件选择对话框，直接回填包路径与资源路径。"""

    pack_path = ""
    res_path = ""

    def __init__(self, parent, last_dir):
        pass

    def exec(self):
        from PySide6.QtWidgets import QDialog
        return QDialog.DialogCode.Accepted

    def values(self):
        return (self.pack_path, self.res_path)


class TestOpenFromPack(unittest.TestCase):
    """回归：从资源包打开布局（0.1.0 在 Windows 上因此处属性误用崩溃）。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_open_from_pack(self):
        import tempfile

        from ui_editor.ui import main_window as main_module
        from ui_editor.ui.main_window import MainWindow

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "mini.fls"
            pack_path.write_bytes(_mini_pack_bytes())
            _FakePackDialog.pack_path = str(pack_path)
            _FakePackDialog.res_path = "dialog/test.dlg"
            original = main_module._PackOpenDialog
            main_module._PackOpenDialog = _FakePackDialog
            window = MainWindow()
            try:
                window.open_from_pack()
                self.assertIsNotNone(window.doc)
                self.assertEqual(window.doc.roots[0].wtype, "CMainFrame")
                self.assertEqual(window.doc.source_pack[1], "dialog/test.dlg")
            finally:
                main_module._PackOpenDialog = original
                if window.doc is not None:
                    window.doc.dirty = False
                window.close()
                window.deleteLater()
                self._app.processEvents()


if __name__ == "__main__":
    unittest.main()


class TestPackOpenDialog(unittest.TestCase):
    """从资源包打开对话框：选包后自动列出包内已知布局。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_scan_lists_known_layout(self):
        import tempfile

        from ui_editor.ui.main_window import _PackOpenDialog

        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "mini.fls"
            pack_path.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
            dialog = _PackOpenDialog(None, "")
            dialog._pack_edit.setText(str(pack_path))
            dialog._scan_current_pack()
            self.assertIn("dialog/cateroom.dlg", dialog._found)
            self.assertEqual(dialog.values()[1], "dialog/cateroom.dlg")
            dialog._path_edit.setText("dialog/manual.dlg")
            self.assertEqual(dialog.values()[1], "dialog/manual.dlg")
            dialog.close()
            dialog.deleteLater()
            self._app.processEvents()

    def test_catalog_loaded(self):
        from ui_editor.core.catalog import known_layout_paths
        paths = known_layout_paths()
        self.assertGreaterEqual(len(paths), 2900)
        self.assertTrue(all(p.endswith(".dlg") for p in paths))


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
