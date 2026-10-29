"""GUI：Big5 属性提交即转繁，编辑器回灌且保存不丢字符。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication, QLineEdit, QPlainTextEdit

from ui_editor.core import dlg_codec


class TestGuiSmartTranscode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.doc.text_encoding = "big5"
        self.text = self.doc.new_widget(
            "CTextFrameEx", parent=self.doc.roots[0])
        self.text.props["sText"] = "原始文字"
        self.window._refresh_structure()
        self.window._select_widget(self.text)
        self.panel = self.window.props_panel

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _editor(self, displayed: str) -> QPlainTextEdit:
        matches = [edit for edit in self.panel.findChildren(QPlainTextEdit)
                   if edit.toPlainText() == displayed]
        self.assertEqual(len(matches), 1, matches)
        return matches[0]

    def test_editing_finished_converts_model_editor_and_big5_bytes(self):
        edit = self._editor("原始文字")
        edit.setPlainText("#Y注册#n")
        edit.editingFinished.emit()
        self.assertEqual(self.text.props["sText"], "#Y註冊#n")
        self.assertEqual(edit.toPlainText(), "#Y註冊#n")
        self.assertTrue(self.doc.dirty)
        data = dlg_codec.dump_bytes(
            self.doc.to_native_dicts(), text_encoding=self.doc.text_encoding)
        self.assertIn("#Y註冊#n".encode("big5"), data)

    def test_same_normalized_model_value_still_updates_editor(self):
        self.text.props["sText"] = "註冊"
        self.panel._rebuild()
        edit = self._editor("註冊")
        edit.setPlainText("注册")
        edit.editingFinished.emit()
        self.assertEqual(self.text.props["sText"], "註冊")
        self.assertEqual(edit.toPlainText(), "註冊")

    def test_gbk_keeps_user_simplified_and_saves_gbk(self):
        self.doc.text_encoding = "gbk"
        edit = self._editor("原始文字")
        edit.setPlainText("注册账号")
        edit.editingFinished.emit()
        self.assertEqual(self.text.props["sText"], "注册账号")
        self.assertEqual(edit.toPlainText(), "注册账号")
        data = dlg_codec.dump_bytes(
            self.doc.to_native_dicts(), text_encoding="gbk")
        self.assertIn("注册账号".encode("gbk"), data)

    def test_unencodable_input_is_visible_then_strict_save_fails(self):
        edit = self._editor("原始文字")
        edit.setPlainText("注册😀")
        edit.editingFinished.emit()
        self.assertEqual(self.text.props["sText"], "註冊😀")
        self.assertEqual(edit.toPlainText(), "註冊😀")
        with self.assertRaises(UnicodeEncodeError):
            dlg_codec.dump_bytes(
                self.doc.to_native_dicts(), text_encoding="big5")

    def test_sequence_display_text_also_updates_its_editor(self):
        self.text.props["sTitles"] = ("原始", "文字")
        self.panel._rebuild()
        matches = [edit for edit in self.panel.findChildren(QLineEdit)
                   if edit.text() == "原始, 文字"]
        self.assertEqual(len(matches), 1, matches)
        edit = matches[0]
        edit.setText("注册, 简体")
        edit.editingFinished.emit()
        self.assertEqual(self.text.props["sTitles"], ("註冊", "簡體"))
        self.assertEqual(edit.text(), "註冊, 簡體")

    def test_add_display_text_property_uses_same_conversion(self):
        del self.text.props["sText"]
        self.panel._rebuild()
        self.panel._new_key.setCurrentText("sText")
        self.panel._new_value.setText("注册")
        self.panel._add_property()
        self.assertEqual(self.text.props["sText"], "註冊")
        self.assertEqual(self._editor("註冊").toPlainText(), "註冊")


if __name__ == "__main__":
    unittest.main()
