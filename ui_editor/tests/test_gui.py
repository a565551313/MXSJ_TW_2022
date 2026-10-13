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


if __name__ == "__main__":
    unittest.main()
