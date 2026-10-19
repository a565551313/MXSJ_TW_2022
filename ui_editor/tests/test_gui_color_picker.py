"""GUI：颜色属性取色块（写回保持原表示形式）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.model import Widget  # noqa: E402


def color_edit(panel, text):
    """找到颜色行自己的输入框（面板底部还有「新属性名/值」两个输入框）。"""
    from PySide6.QtWidgets import QLineEdit

    for edit in panel.findChildren(QLineEdit):
        if edit.text() == text:
            return edit
    raise AssertionError(f"找不到文本为 {text!r} 的输入框")


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
        from PySide6.QtWidgets import QToolButton

        panel, model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "iColor": 0xFF0000})
        buttons = panel.findChildren(QToolButton)
        swatches = [b for b in buttons if "颜色" in b.toolTip()]
        self.assertTrue(swatches)
        self.assertIn("rgb(255,0,0)", swatches[0].styleSheet())
        edit = color_edit(panel, "16711680")
        edit.setText("#00ff00")
        edit.editingFinished.emit()
        self.assertIsInstance(model.props["iColor"], int)
        self.assertEqual(model.props["iColor"], 0x00FF00)

    def test_string_color_keeps_string_format(self):

        panel, model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "sColor": "255, 0, 0"})
        edit = color_edit(panel, "255, 0, 0")
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

    def test_list_color_gets_one_swatch_per_group(self):
        from PySide6.QtWidgets import QToolButton

        panel, model = self._panel({
            "sWidgetType": "CTextFrame", "sName": "t", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10,
            "lColor": [91, 255, 226, 0, 73, 80]})
        swatches = [b for b in panel.findChildren(QToolButton)
                    if "组颜色" in b.toolTip()]
        self.assertEqual(len(swatches), 2)
        self.assertIn("rgb(91,255,226)", swatches[0].styleSheet())
        self.assertIn("rgb(0,73,80)", swatches[1].styleSheet())

    def test_list_color_pick_keeps_type_and_length(self):
        from unittest import mock

        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog, QToolButton

        panel, model = self._panel({
            "sWidgetType": "CTextFrame", "sName": "t", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10,
            "lColor": [91, 255, 226, 0, 73, 80]})
        swatches = [b for b in panel.findChildren(QToolButton)
                    if "组颜色" in b.toolTip()]
        with mock.patch.object(QColorDialog, "getColor",
                               return_value=QColor(10, 20, 30)):
            swatches[1].click()
        self.assertIsInstance(model.props["lColor"], list)
        self.assertEqual(len(model.props["lColor"]), 6)
        self.assertEqual(model.props["lColor"], [91, 255, 226, 10, 20, 30])

    def test_empty_list_offers_add_group(self):
        from PySide6.QtWidgets import QToolButton

        panel, _model = self._panel({
            "sWidgetType": "CTextFrame", "sName": "t", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "lColor": []})
        buttons = [b for b in panel.findChildren(QToolButton)
                   if "添加一组颜色" in b.toolTip()]
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].text(), "＋")

    def test_list_text_edit_keeps_list_type(self):

        panel, model = self._panel({
            "sWidgetType": "CTextFrame", "sName": "t", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10, "lColor": [1, 2, 3]})
        edit = color_edit(panel, "1, 2, 3")
        edit.setText("9, 8, 7")
        edit.editingFinished.emit()
        self.assertEqual(model.props["lColor"], [9, 8, 7])

    def test_invalid_list_falls_back_to_plain_editor(self):
        from PySide6.QtWidgets import QToolButton

        panel, _model = self._panel({
            "sWidgetType": "CButton", "sName": "b", "iX": 0, "iY": 0,
            "iWidth": 10, "iHeight": 10,
            "lNormalColor": [255, 255, 255, 0]})
        swatches = [b for b in panel.findChildren(QToolButton)
                    if "颜色" in b.toolTip()]
        self.assertEqual(swatches, [])

if __name__ == "__main__":
    unittest.main()
