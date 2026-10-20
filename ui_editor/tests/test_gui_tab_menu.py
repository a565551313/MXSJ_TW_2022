"""工具栏角标开关 + 标签右键菜单（关闭当前/左侧/右侧/其他/全部）。"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class _NeedsGui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self._opened = 0

    def tearDown(self):
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def open_tabs(self, count, *, dirty=False):
        """开 count 个新标签，并清掉脏标记（除非要测确认流程）。"""
        for _ in range(count):
            self.window.new_layout()
            self._opened += 1
            self.window.doc.dirty = dirty
        return list(self.window._sessions)

    def menu_items(self, index):
        menu = self.window.build_tab_context_menu(index)
        return {action.text(): action for action in menu.actions()
                if action.text()}


class TestBadgeToggle(_NeedsGui):
    def test_toolbar_has_badge_action_checked_by_default(self):
        action = self.window._badges_action
        self.assertTrue(action.isCheckable())
        self.assertTrue(action.isChecked())
        self.assertEqual(action.iconText(), "角标")
        self.assertTrue(self.window.ctx.show_badges)
        texts = [a.iconText() for a in self.window._toolbar.actions()]
        self.assertIn("角标", texts)

    def _badge_pixels(self, node) -> bytes:
        from PySide6.QtCore import QBuffer, QByteArray
        from PySide6.QtGui import QColor, QImage, QPainter

        image = QImage(max(1, int(node.boundingRect().width())),
                       max(1, int(node.boundingRect().height())),
                       QImage.Format.Format_RGBA8888)
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image)
        try:
            node._paint_fidelity_badge(painter)
        finally:
            painter.end()
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        return bytes(QByteArray(buffer.data()))

    def test_toggle_off_stops_drawing_badges(self):
        self.window.new_layout()
        doc = self.window.doc
        doc.dirty = False
        item = doc.new_widget("CBitmapFrame", parent=doc.roots[0])
        item.props.update({"sFileName": "gone.png", "iWidth": 60,
                           "iHeight": 30})
        self.window._refresh_structure()
        node = self.window.scene.item_for(item)
        self.assertTrue(node.fidelity)          # 有可标的东西

        drawn = self._badge_pixels(node)
        self.window._badges_action.setChecked(False)
        self.assertFalse(self.window.ctx.show_badges)
        blank = self._badge_pixels(node)
        self.assertNotEqual(drawn, blank)       # 关掉后不再画角标

    def test_toggle_back_on_and_status_message(self):
        self.window._toggle_badges(False)
        self.assertIn("已隐藏", self.window.statusBar().currentMessage())
        self.window._toggle_badges(True)
        self.assertTrue(self.window.ctx.show_badges)
        self.assertIn("已显示", self.window.statusBar().currentMessage())

    def test_fidelity_label_unaffected_by_badge_toggle(self):
        """角标关掉后，状态栏那条文字说明仍然可用。"""
        self.window.new_layout()
        doc = self.window.doc
        doc.dirty = False
        widget = doc.new_widget("CTextFrame", parent=doc.roots[0])
        self.window._refresh_structure()
        self.window._select_widget(widget)
        before = self.window._fidelity_label.text()
        self.window._toggle_badges(False)
        self.assertEqual(self.window._fidelity_label.text(), before)


class TestTabContextMenu(_NeedsGui):
    def test_menu_entries(self):
        self.open_tabs(3)
        items = self.menu_items(1)
        self.assertEqual(list(items), [
            "锁定标签", "关闭当前标签", "关闭左侧全部标签",
            "关闭右侧全部标签", "关闭其他标签", "关闭全部标签"])

    def test_enablement_at_edges(self):
        self.open_tabs(3)
        first = self.menu_items(0)
        self.assertTrue(first["关闭当前标签"].isEnabled())
        self.assertFalse(first["关闭左侧全部标签"].isEnabled())
        self.assertTrue(first["关闭右侧全部标签"].isEnabled())
        last = self.menu_items(2)
        self.assertFalse(last["关闭右侧全部标签"].isEnabled())
        self.assertTrue(last["关闭左侧全部标签"].isEnabled())

    def test_single_tab_menu_disables_multi_actions(self):
        self.open_tabs(1)
        items = self.menu_items(0)
        self.assertTrue(items["关闭当前标签"].isEnabled())
        self.assertTrue(items["关闭全部标签"].isEnabled())
        self.assertFalse(items["关闭左侧全部标签"].isEnabled())
        self.assertFalse(items["关闭右侧全部标签"].isEnabled())
        self.assertFalse(items["关闭其他标签"].isEnabled())

    def test_empty_state_has_no_menu(self):
        self.window.build_tab_context_menu(-1)   # 不崩
        self.assertEqual(len(self.window._sessions), 0)

    def test_close_current_tab(self):
        self.open_tabs(3)
        self.window._activate_session(1)
        self.menu_items(1)["关闭当前标签"].trigger()
        self.assertEqual(len(self.window._sessions), 2)
        self.assertEqual(self.window._tab_bar.count(), 2)

    def test_close_left_tabs(self):
        sessions = self.open_tabs(4)
        keep = sessions[2]
        self.window._close_tab_range(0, 2)
        self.assertEqual(len(self.window._sessions), 2)
        self.assertIn(keep, self.window._sessions)
        self.assertEqual(self.window._tab_bar.count(), 2)

    def test_close_right_tabs(self):
        sessions = self.open_tabs(4)
        keep = sessions[1]
        self.menu_items(1)["关闭右侧全部标签"].trigger()
        self.assertEqual(self.window._sessions, [sessions[0], keep])

    def test_close_all_left_to_empty_state(self):
        self.open_tabs(3)
        self.menu_items(2)["关闭全部标签"].trigger()
        self.assertEqual(self.window._sessions, [])
        self.assertIsNone(self.window.doc)
        self.assertEqual(self.window._tab_bar.count(), 0)
        self.window._update_title()
        self.assertIn("未打开布局", self.window.windowTitle())

    def test_close_others_keeps_one(self):
        sessions = self.open_tabs(4)
        self.window._close_tab_except(1)
        self.assertEqual(self.window._sessions, [sessions[1]])
        self.assertIs(self.window.doc, sessions[1].doc)

    def test_dirty_tab_asks_and_can_be_kept(self):
        sessions = self.open_tabs(3)
        sessions[1].doc.dirty = True
        dirty = sessions[1].doc
        with mock.patch.object(
                self.window, "_confirm_discard",
                side_effect=lambda doc: doc is not dirty):
            closed = self.window._close_tab_range(0, 3)
        self.assertEqual(closed, 2)
        self.assertEqual(self.window._sessions, [sessions[1]])
        self.assertIn("跳过", self.window.statusBar().currentMessage())

    def test_confirm_yes_closes_dirty_tab(self):
        sessions = self.open_tabs(2)
        sessions[0].doc.dirty = True
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True) as confirm:
            self.window._close_tab_range(0, 2)
        self.assertEqual(confirm.call_count, 2)   # 只在脏的那个真的问
        self.assertEqual(self.window._sessions, [])
        self.assertTrue(all(call.args[0] is sessions[0].doc
                            or call.args[0] is sessions[1].doc
                            for call in confirm.call_args_list))

    def test_closing_active_tab_activates_neighbour(self):
        sessions = self.open_tabs(3)
        self.window._activate_session(2)
        self.window._close_tab_range(2, 3)
        self.assertIs(self.window.doc, sessions[1].doc)

    def test_right_click_activates_that_tab(self):
        self.open_tabs(3)
        self.window._activate_session(0)
        tab_rect = self.window._tab_bar.tabRect(2)
        with mock.patch.object(self.window, "_exec_tab_menu") as execute:
            self.window._show_tab_context_menu(tab_rect.center())
        execute.assert_called_once()
        self.assertEqual(self.window._tab_bar.currentIndex(), 2)


class TestTabLock(_NeedsGui):
    """锁定只是标签会话状态：批量关闭跳过，单独关闭照旧。"""

    def test_menu_toggles_lock_text(self):
        self.open_tabs(2)
        self.assertIn("锁定标签", self.menu_items(0))
        self.menu_items(0)["锁定标签"].trigger()
        self.assertTrue(self.window._sessions[0].locked)
        self.assertIn("解锁标签", self.menu_items(0))
        self.menu_items(0)["解锁标签"].trigger()
        self.assertFalse(self.window._sessions[0].locked)

    def test_locked_tab_shows_mark_and_tooltip(self):
        self.open_tabs(2)
        self.assertTrue(self.window._tab_bar.tabIcon(0).isNull())
        self.window._set_tab_locked(0, True)
        self.assertFalse(self.window._tab_bar.tabIcon(0).isNull())
        self.assertIn("锁定", self.window._tab_bar.tabToolTip(0))
        self.window._set_tab_locked(0, False)
        self.assertTrue(self.window._tab_bar.tabIcon(0).isNull())
        self.assertEqual(self.window._tab_bar.tabToolTip(0), "")

    def test_lock_does_not_dirty_document(self):
        sessions = self.open_tabs(1)
        self.window._set_tab_locked(0, True)
        self.assertFalse(sessions[0].doc.dirty)
        self.assertIn("已锁定", self.window.statusBar().currentMessage())

    def test_close_all_skips_locked_tabs(self):
        sessions = self.open_tabs(4)
        self.window._set_tab_locked(1, True)
        self.window._set_tab_locked(3, True)
        self.window._close_tab_range(0, 4)
        self.assertEqual(self.window._sessions, [sessions[1], sessions[3]])
        self.assertEqual(self.window._tab_bar.count(), 2)
        message = self.window.statusBar().currentMessage()
        self.assertIn("已关闭 2 个标签", message)
        self.assertIn("2 个已锁定", message)

    def test_close_others_skips_locked(self):
        sessions = self.open_tabs(4)
        self.window._set_tab_locked(0, True)
        self.window._close_tab_except(2)
        self.assertEqual(self.window._sessions,
                         [sessions[0], sessions[2]])
        self.assertIn("1 个已锁定", self.window.statusBar().currentMessage())

    def test_close_left_and_right_skip_locked(self):
        sessions = self.open_tabs(5)
        self.window._set_tab_locked(1, True)
        self.window._set_tab_locked(4, True)
        self.window._close_tab_range(0, 5)
        self.assertEqual(self.window._sessions, [sessions[1], sessions[4]])

    def test_single_tab_close_still_closes_locked(self):
        sessions = self.open_tabs(2)
        self.window._set_tab_locked(0, True)
        self.window._close_tab(0)
        self.assertEqual(self.window._sessions, [sessions[1]])

    def test_locked_dirty_tab_is_not_confirmed(self):
        sessions = self.open_tabs(2)
        sessions[0].doc.dirty = True
        self.window._set_tab_locked(0, True)
        with mock.patch.object(self.window, "_confirm_discard",
                               side_effect=lambda doc: doc is not sessions[0].doc):
            self.window._close_tab_range(0, 2)
        self.assertEqual(self.window._sessions, [sessions[0]])
        self.assertIn("1 个已锁定", self.window.statusBar().currentMessage())

    def test_marks_follow_tab_removal(self):
        sessions = self.open_tabs(3)
        self.window._set_tab_locked(2, True)
        self.window._close_tab(0)
        self.assertEqual(self.window._sessions, [sessions[1], sessions[2]])
        self.assertTrue(self.window._tab_bar.tabIcon(0).isNull())
        self.assertFalse(self.window._tab_bar.tabIcon(1).isNull())
        self.assertTrue(sessions[2].locked)

    def test_lock_state_is_per_session_not_document(self):
        sessions = self.open_tabs(2)
        self.window._set_tab_locked(1, True)
        self.assertFalse(sessions[0].locked)
        self.assertNotIn("locked", sessions[0].doc.__dict__)


if __name__ == "__main__":
    unittest.main()
