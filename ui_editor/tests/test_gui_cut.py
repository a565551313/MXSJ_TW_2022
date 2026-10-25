"""GUI：画布右键菜单「剪切控件」（0.17.0 功能 4）。"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class TestCutWidgets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from PySide6.QtWidgets import QMessageBox

        from ui_editor.ui.main_window import MainWindow

        # 删除/剪切带子树或引用时会弹确认框；离屏无人点，统一自动 Yes
        # （护栏本身另有 test_gui_lock_ignore / test_gui_review 覆盖）。
        # 只替 question 方法、保留真枚举，比较才成立。
        patcher = mock.patch.object(
            QMessageBox, "question",
            return_value=QMessageBox.StandardButton.Yes)
        self._question = patcher.start()
        self.addCleanup(patcher.stop)

        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.button = self.doc.new_widget("CButton", parent=self.frame)
        self.button.name = "BTN"
        self.button.set_geometry(x=20, y=20, width=80, height=24)
        self.child = self.doc.new_widget("CTextFrame", parent=self.button)
        self.window._refresh_structure()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self._app.clipboard().clear()
        self.window.deleteLater()
        self._app.processEvents()

    def test_context_menu_has_cut(self):
        self.window._select_widget(self.button)
        menu = self.window.build_canvas_context_menu(self.button)
        texts = [a.text() for a in menu.actions()]
        self.assertIn("剪切控件", texts)
        # 剪切排在复制前面
        self.assertLess(texts.index("剪切控件"), texts.index("复制控件"))
        menu.deleteLater()

    def test_cut_then_paste(self):
        self.window._select_widget(self.button)
        self.window.cut_selected_widgets()
        self.assertNotIn(self.button, self.doc.all_widgets())
        self.window._select_widget(self.frame)
        self.window.paste_widgets()
        widgets = self.doc.all_widgets()
        names = [w.name for w in widgets]
        # 原名已空出：粘回来仍叫 BTN，但必须是新对象（整棵子树一起）
        self.assertIn("BTN", names)
        self.assertNotIn(self.button, widgets)
        pasted = [w for w in widgets if w.name == "BTN"][0]
        self.assertEqual(len(pasted.children), 1)

    def test_cut_is_one_undo_step(self):
        self.window.doc.checkpoint()
        self.window._select_widget(self.button)
        self.window.cut_selected_widgets()
        self.assertNotIn(self.button, self.doc.all_widgets())
        self.assertTrue(self.window.doc.can_undo)
        self.window.doc.undo()
        # 撤销一步就整棵回来（含子控件），不需要第二步
        restored = [w for w in self.doc.all_widgets() if w.name == "BTN"]
        self.assertEqual(len(restored), 1)
        self.assertEqual(len(restored[0].children), 1)

    def test_cut_locked_widget_blocked(self):
        self.button.locked = True
        self.window._select_widget(self.button)
        self.window.cut_selected_widgets()
        # 锁定护栏：文档不动（剪贴板留副本，与多数编辑器一致）
        self.assertIn(self.button, self.doc.all_widgets())

    def test_cut_cancel_keeps_document(self):
        from PySide6.QtWidgets import QMessageBox
        self._question.return_value = QMessageBox.StandardButton.No
        self.window._select_widget(self.button)
        self.window.cut_selected_widgets()
        self.assertIn(self.button, self.doc.all_widgets())

    def test_edit_menu_and_shortcut(self):
        from PySide6.QtWidgets import QMenu

        self.assertEqual(self.window._act_cut.shortcut().toString(),
                         "Ctrl+X")
        menus = self.window.menuBar().findChildren(QMenu)
        edit = [m for m in menus if m.title().startswith("编辑")]
        self.assertTrue(edit)
        self.assertIn(self.window._act_cut, edit[0].actions())
        # 置灰联动
        self.window._select_widget(self.button)
        self.window._sync_edit_actions()
        self.assertTrue(self.window._act_cut.isEnabled())
        self.window.scene.clearSelection()
        self.window._sync_edit_actions()
        self.assertFalse(self.window._act_cut.isEnabled())


if __name__ == "__main__":
    unittest.main()
