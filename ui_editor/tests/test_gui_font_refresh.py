"""iFont 微调立即提交，QPainter 随即采用字体表对应的新字号。"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtWidgets import QApplication, QFormLayout, QSpinBox

    from ui_editor.core import painters
    from ui_editor.core.styles import StyleBook
    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 无 Qt 环境
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class FontRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.new_layout()
        book = StyleBook.parse_text(
            "[Font]\n宋体 12 400 0\n宋体 24 700 0\n")
        self.window._set_styles(book, "测试字体表")
        self.text = self.window.doc.new_widget(
            "CTextFrameEx", parent=self.window.doc.roots[0])
        self.text.set_geometry(x=20, y=20, width=250, height=80)
        self.text.props.update({"sText": "字号测试", "iFont": 0})
        self.window._refresh_structure()
        self.window._select_widget(self.text)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _font_spin(self) -> QSpinBox:
        form = self.window.props_panel._form
        for row in range(form.rowCount()):
            label_item = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
            label = label_item.widget() if label_item is not None else None
            if label is not None and label.text() == "iFont":
                field = form.itemAt(row, QFormLayout.ItemRole.FieldRole).widget()
                spin = (field if isinstance(field, QSpinBox)
                        else field.findChild(QSpinBox))
                self.assertIsInstance(spin, QSpinBox)
                return spin
        self.fail("iFont 属性行不存在")

    def test_spin_value_change_repaints_with_new_font_size_immediately(self):
        sizes = []
        original = painters._draw_text

        def spy(painter, rect, text, font, color,
                align_flags=painters._TOP_LEFT, rich=False):
            if text == "字号测试":
                sizes.append(font.pixelSize())
            return original(painter, rect, text, font, color,
                            align_flags, rich)

        def paint():
            image = QImage(300, 120, QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            try:
                self.window.scene.item_for(self.text).paint(painter, None)
            finally:
                painter.end()

        painters._draw_text = spy
        try:
            paint()
            self.assertEqual(sizes[-1], 12)
            spin = self._font_spin()
            spin.setValue(1)  # 只发 valueChanged；不发 editingFinished
            self._app.processEvents()
            self.assertEqual(self.text.props["iFont"], 1)
            paint()
            self.assertEqual(sizes[-1], 24)
            self.assertNotEqual(sizes[-1], sizes[0])
            spin.setValue(0)
            self._app.processEvents()
            paint()
            self.assertEqual(sizes[-1], 12)
        finally:
            painters._draw_text = original


if __name__ == "__main__":
    unittest.main()
