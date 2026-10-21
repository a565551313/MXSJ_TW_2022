"""工具栏「编码」「帧」两个下拉按钮：外观与对齐/按钮态一致，帧用横向滑块。"""

from __future__ import annotations

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

    def tearDown(self):
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
                session.doc.pending_pack_import = False
        if self.window.doc is not None:
            self.window.doc.dirty = False
            self.window.doc.pending_pack_import = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()


class TestDropdownLook(_NeedsGui):
    """三个下拉按钮（对齐/按钮态/编码/帧）外观必须同一套。"""

    def style_of(self, button):
        from PySide6.QtWidgets import QToolButton
        self.assertIsInstance(button, QToolButton)
        return (button.toolButtonStyle(), button.popupMode())

    def test_encoding_and_frame_match_align_and_state_buttons(self):
        expected = self.style_of(self.window._align_btn)
        for button in (self.window._encoding_btn, self.window._frame_btn,
                       self.window._button_state_btn):
            with self.subTest(button=button.text()):
                self.assertEqual(self.style_of(button), expected)

    def test_short_labels_on_toolbar(self):
        self.assertEqual(self.window._encoding_btn.text(), "编码")
        self.assertEqual(self.window._frame_btn.text(), "帧")
        self.assertFalse(self.window._encoding_btn.icon().isNull())
        self.assertFalse(self.window._frame_btn.icon().isNull())

    def test_old_widgets_are_gone_from_toolbar(self):
        from PySide6.QtWidgets import QComboBox, QSpinBox
        widgets = self.window._toolbar.findChildren(QComboBox)
        spinners = self.window._toolbar.findChildren(QSpinBox)
        self.assertEqual(widgets, [])
        self.assertEqual(spinners, [])
        self.assertIn(self.window._encoding_btn, self.window._toolbar.findChildren(
            type(self.window._encoding_btn)))
        self.assertIn(self.window._frame_btn, self.window._toolbar.findChildren(
            type(self.window._frame_btn)))

    def test_encoding_menu_items(self):
        menu = self.window._encoding_btn.menu()
        texts = [action.text() for action in menu.actions()]
        self.assertEqual(texts, ["Big5（繁体）", "GBK（简体）", "UTF-8"])
        for action in menu.actions():
            self.assertTrue(action.isCheckable())
        self.assertTrue(self.window._encoding_actions["big5"].isChecked())
        self.assertFalse(self.window._encoding_actions["gbk"].isChecked())


class TestEncodingButton(_NeedsGui):
    def test_choosing_item_switches_encoding_and_checks_only_that_one(self):
        self.window.change_text_encoding("gbk")
        self.assertEqual(self.window.resolver.text_encoding, "gbk")
        checked = [codec for codec, action in self.window._encoding_actions.items()
                   if action.isChecked()]
        self.assertEqual(checked, ["gbk"])

    def test_clicking_current_item_stays_checked(self):
        action = self.window._encoding_actions["big5"]
        action.setChecked(False)     # 模拟菜单点了一下把勾去掉
        action.trigger()
        self.assertEqual(self.window.resolver.text_encoding, "big5")
        self.assertTrue(action.isChecked())

    def test_cancelled_switch_restores_checkmark(self):
        self.window.new_layout()
        self.window.doc.dirty = True
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=False):
            self.window.change_text_encoding("gbk")
        self.assertEqual(self.window.resolver.text_encoding, "big5")
        self.assertTrue(self.window._encoding_actions["big5"].isChecked())
        self.assertFalse(self.window._encoding_actions["gbk"].isChecked())

    def test_button_tooltip_mentions_paths_stay_gbk(self):
        self.assertIn("GBK", self.window._encoding_btn.toolTip())


class TestFrameButton(_NeedsGui):
    def _document_with_spr(self, frames):
        """造一个引用 .spr 的布局，并让资源解析返回 frames 帧。"""
        self.window.new_layout()
        doc = self.window.doc
        doc.dirty = False
        widget = doc.new_widget("CBitmapFrame", parent=doc.roots[0])
        widget.props["sFileName"] = "effect/test.spr"
        asset = mock.Mock(frames=[mock.Mock(frame_id=i, duration=80,
                                            image=None) for i in range(frames)])
        self.window.resolver.fetch_animation = mock.Mock(return_value=asset)
        return doc

    def test_frame_slider_lives_in_dropdown(self):
        from PySide6.QtWidgets import QSlider
        self.assertIsInstance(self.window._frame_slider, QSlider)
        menu = self.window._frame_btn.menu()
        actions = menu.actions()
        self.assertEqual(len(actions), 1)
        widget = actions[0].defaultWidget()
        self.assertIsNotNone(widget)
        self.assertIs(self.window._frame_slider.parent(), widget)
        self.assertIs(self.window._frame_readout.parent(), widget)

    def test_slider_is_horizontal(self):
        from PySide6.QtCore import Qt
        self.assertEqual(self.window._frame_slider.orientation(),
                         Qt.Orientation.Horizontal)

    def test_range_follows_spr_frames(self):
        self._document_with_spr(5)
        self.window._refresh_animation_frame_control()
        self.assertEqual(self.window._frame_slider.maximum(), 4)
        self.assertEqual(self.window._frame_slider.minimum(), 0)

    def test_no_spr_means_zero_range(self):
        self.window.new_layout()
        self.window.doc.dirty = False
        self.window._refresh_animation_frame_control()
        self.assertEqual(self.window._frame_slider.maximum(), 0)

    def test_dragging_slider_changes_preview_frame(self):
        self._document_with_spr(6)
        self.window._refresh_animation_frame_control()
        self.window._frame_slider.setValue(3)
        self.assertEqual(self.window.ctx.animation_frame, 3)
        self.assertEqual(self.window._frame_readout.text(), "预览帧 3 / 5")

    def test_readout_and_tooltip_update(self):
        self._document_with_spr(4)
        self.window._refresh_animation_frame_control()
        self.assertIn("0 / 3", self.window._frame_readout.text())
        self.window._frame_slider.setValue(2)
        self.assertIn("2 / 3", self.window._frame_readout.text())
        self.assertIn("2 / 3", self.window._frame_btn.toolTip())

    def test_shrinking_range_moves_canvas_to_clamped_frame(self):
        """帧数变少时滑块被夹，画布必须跟着换帧（旧实现只改读数）。"""
        self._document_with_spr(7)
        self.window._refresh_animation_frame_control()
        self.window._frame_slider.setValue(6)
        self.assertEqual(self.window.ctx.animation_frame, 6)
        self._document_with_spr(4)          # 只剩 0..3
        self.window._refresh_animation_frame_control()
        self.assertEqual(self.window._frame_slider.value(), 3)
        self.assertEqual(self.window.ctx.animation_frame, 3)
        self.assertIn("3 / 3", self.window._frame_readout.text())

    def test_unchanged_frame_is_kept_on_refresh(self):
        """帧数没变时刷新不应把当前预览帧打回 0。"""
        self._document_with_spr(5)
        self.window._refresh_animation_frame_control()
        self.window._frame_slider.setValue(3)
        self.window._refresh_animation_frame_control()
        self.assertEqual(self.window._frame_slider.value(), 3)
        self.assertEqual(self.window.ctx.animation_frame, 3)

    def test_status_message_still_explains_frame(self):
        self._document_with_spr(3)
        self.window._refresh_animation_frame_control()
        self.window._frame_slider.setValue(1)
        self.assertIn("动画预览帧：1", self.window.statusBar().currentMessage())


if __name__ == "__main__":
    unittest.main()
