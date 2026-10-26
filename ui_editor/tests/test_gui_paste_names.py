"""GUI：复制粘贴自动重命名（BTN → BTN_1 → BTN_2 → …）＋剪贴板负载校验。"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class TestPasteRenames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(x=0, y=0, width=600, height=400)
        self.button = self._add("CButton", "BTN", 20, 20)
        self.window._refresh_structure()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        # 控件复制会把自定义 mime 数据留在全局剪贴板上；沙箱 Qt 在解释器
        # 退出时回收它可能段错误（base 提交同样复现）。测完就清掉，
        # 免得下一个测试/退出阶段接手这块全局状态。
        self._app.clipboard().clear()
        self.window.deleteLater()
        self._app.processEvents()

    def _add(self, wtype, name, x, y, parent=None):
        widget = self.doc.new_widget(wtype, parent=parent or self.frame)
        widget.name = name
        widget.set_geometry(x=x, y=y, width=80, height=24)
        return widget

    def _copy_paste(self, widget):
        self.window._select_widget(widget)
        self.window.copy_selected_widgets()
        self.window.paste_widgets()
        return self.window.current_selection()

    def test_sequential_suffixes(self):
        first = self._copy_paste(self.button)
        self.assertEqual(first.name, "BTN_1")
        self.window._select_widget(first)
        self.window.copy_selected_widgets()
        self.window.paste_widgets()
        second = self.window.current_selection()
        self.assertEqual(second.name, "BTN_1_1")
        self.window.paste_widgets()
        third = self.window.current_selection()
        self.assertEqual(third.name, "BTN_1_2")

    def test_paste_original_twice(self):
        first = self._copy_paste(self.button)
        second = self._copy_paste(self.button)  # 再复制原件一次
        self.assertEqual((first.name, second.name), ("BTN_1", "BTN_2"))
        self.assertEqual(self.button.name, "BTN")

    def test_all_names_unique_in_document(self):
        for _ in range(3):
            self._copy_paste(self.button)
        names = [w.name for w in self.doc.all_widgets()]
        self.assertEqual(len(names), len(set(names)))

    def test_paste_status_mentions_rename(self):
        self.window._select_widget(self.button)
        self.window.copy_selected_widgets()
        self.window.paste_widgets()
        message = self.window.statusBar().currentMessage()
        self.assertIn("自动改名", message)
        self.assertIn("BTN_1", message)

    def test_subtree_children_also_renamed(self):
        child = self._add("CTextFrame", "txt", 0, 0, parent=self.button)
        child.set_geometry(x=2, y=2, width=40, height=16)
        self.window._refresh_structure()
        clone = self._copy_paste(self.button)
        self.assertEqual(clone.name, "BTN_1")
        self.assertEqual([c.name for c in clone.children], ["txt_1"])
        # 原件子树不受影响
        self.assertEqual(self.button.name, "BTN")
        self.assertEqual([c.name for c in self.button.children], ["txt"])

    def test_paste_is_single_undo_step(self):
        self.doc.checkpoint()  # 以当前状态为基线
        before = len(self.doc.all_widgets())
        self._copy_paste(self.button)
        self.assertEqual(len(self.doc.all_widgets()), before + 1)
        self.doc.undo()
        self.assertEqual(len(self.doc.all_widgets()), before)

    def test_unreferenced_copy_keeps_name(self):
        """不重名时保持原名（例如原件已删除后再粘贴）。"""
        self.window._select_widget(self.button)
        self.window.copy_selected_widgets()
        self.doc.remove_widget(self.button)
        self.window._refresh_structure()
        self.window.paste_widgets()
        self.assertEqual(self.window.current_selection().name, "BTN")


class TestPastePayloadValidation(unittest.TestCase):
    """PR #89 审查修复：系统剪贴板共享，坏负载必须挡在门外。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self._app.clipboard().clear()
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _paste_text(self, text: str) -> int:
        """把文本塞进系统剪贴板再粘贴；返回文档控件总数（前后对比用）。"""
        self._app.clipboard().setText(text)
        self.window.paste_widgets()
        return len(self.doc.all_widgets())

    def test_payload_without_swidgettype_rejected(self):
        before = len(self.doc.all_widgets())
        after = self._paste_text('[{"sName": "x", "iX": 1}]')
        self.assertEqual(after, before)

    def test_payload_bad_lchildren_rejected(self):
        before = len(self.doc.all_widgets())
        after = self._paste_text(
            '[{"sWidgetType": "CButton", "lChildren": {"a": 1}}]')
        self.assertEqual(after, before)

    def test_nested_child_missing_type_rejected(self):
        before = len(self.doc.all_widgets())
        after = self._paste_text(
            '[{"sWidgetType": "CFrame", "lChildren": [{"sName": "c"}]}]')
        self.assertEqual(after, before)

    def test_from_dict_valueerror_reports_status(self):
        """兜底分支：from_dict 抛 ValueError 时给用户状态栏提示，不甩 Traceback。"""
        before = len(self.doc.all_widgets())
        statuses: list[str] = []
        with mock.patch.object(self.window, "_update_status",
                               side_effect=statuses.append), \
                mock.patch("ui_editor.ui.clipboard.Widget.from_dict",
                           side_effect=ValueError("坏数据")):
            after = self._paste_text('[{"sWidgetType": "CButton"}]')
        self.assertEqual(after, before)
        self.assertTrue(any("不是有效的控件数据" in s for s in statuses),
                        statuses)


if __name__ == "__main__":
    unittest.main()
