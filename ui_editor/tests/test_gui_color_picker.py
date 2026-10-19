"""GUI：颜色属性取色块（写回保持原表示形式）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.model import Widget  # noqa: E402


def make_panel(props):
    from PySide6.QtWidgets import QApplication

    from ui_editor.ui.property_panel import PropertyPanel

    app = QApplication.instance() or QApplication([])
    panel = PropertyPanel()
    widget = Widget(dict(props))
    panel.set_widget(widget)
    return app, panel, widget


class TestColorPicker(unittest.TestCase):
    def tearDown(self):
        for widget in getattr(self, "_panels", []):
            widget.deleteLater()

    def _panel(self, props):
        app, panel, model = make_panel(props)
        self._app = app
        self._panels = getattr(self, "_panels", []) + [panel]
        return panel, model

    def test_int_color_gets_swatch_and_keeps_int_type(self):
        from PySide6.QtWidgets import QLineEdit, QToolButton

        panel, model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "iColor": 0xFF0000})
        buttons = panel.findChildren(QToolButton)
        swatches = [b for b in buttons if "颜色" in b.toolTip()]
        self.assertTrue(swatches)
        self.assertIn("rgb(255,0,0)", swatches[0].styleSheet())
        edit = panel.findChildren(QLineEdit)[0]
        edit.setText("#00ff00")
        edit.editingFinished.emit()
        self.assertIsInstance(model.props["iColor"], int)
        self.assertEqual(model.props["iColor"], 0x00FF00)

    def test_string_color_keeps_string_format(self):
        from PySide6.QtWidgets import QLineEdit

        panel, model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "sColor": "255, 0, 0"})
        edit = panel.findChildren(QLineEdit)[0]
        edit.setText("1, 2, 3")
        edit.editingFinished.emit()
        self.assertEqual(model.props["sColor"], "1, 2, 3")

    def test_text_property_has_no_swatch(self):
        from PySide6.QtWidgets import QToolButton

        panel, _model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "sText": "hello"})
        swatches = [b for b in panel.findChildren(QToolButton)
                    if "颜色" in b.toolTip()]
        self.assertEqual(swatches, [])

    def test_list_color_falls_back_to_plain_editor(self):
        from PySide6.QtWidgets import QToolButton

        panel, _model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10,
            "lNormalColor": [255, 255, 255]})
        swatches = [b for b in panel.findChildren(QToolButton)
                    if "颜色" in b.toolTip()]
        self.assertEqual(swatches, [])


if __name__ == "__main__":
    unittest.main()
