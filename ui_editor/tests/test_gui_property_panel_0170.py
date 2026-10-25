"""GUI：属性面板 0.17.0 三件事——可编辑下拉、中文名 tooltip、iAlign 下拉。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QLabel

from ui_editor.core.defaults_data import DEFAULT_PROPS


class TestPropertyPanel0170(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.panel = self.window.props_panel

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _select(self, widget):
        self.window._select_widget(widget)

    def _labels(self):
        out = []
        for row in range(self.panel._form.rowCount()):
            item = self.panel._form.itemAt(
                row * 2, )  # label role items come first per row
            w = item.widget()
            if isinstance(w, QLabel):
                out.append(w)
        return out

    def test_new_key_is_editable_combo(self):
        combo = self.panel._new_key
        self.assertIsInstance(combo, QComboBox)
        self.assertTrue(combo.isEditable())

    def test_candidates_exclude_existing_include_census(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        self._select(button)
        items = [self.panel._new_key.itemText(i)
                 for i in range(self.panel._new_key.count())]
        # 普查存在但 CButton 模板没有的键应在候选里
        self.assertIn("iAlign", items)
        self.assertIn("sText", items)
        # 当前控件已有的键不应重复出现
        for key in button.props:
            self.assertNotIn(key, items)
        # 候选就是普查并集减去已有（lChildren 除外）
        expect = [k for k in sorted({k for d in DEFAULT_PROPS.values()
                                     for k in d})
                  if k not in button.props and k != "lChildren"]
        self.assertEqual(items, expect)

    def test_no_selection_combo_disabled(self):
        self.panel.set_widget(None)
        self.assertFalse(self.panel._new_key.isEnabled())

    def test_add_via_combo_selection(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        self._select(button)
        self.panel._new_key.setCurrentText("iAlign")
        self.panel._new_value.setText("4")
        self.panel._add_property()
        self.assertEqual(button.props.get("iAlign"), 4)

    def test_free_text_still_works(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        self._select(button)
        self.panel._new_key.setCurrentText("iMyOwn")
        self.panel._new_value.setText("7")
        self.panel._add_property()
        self.assertEqual(button.props.get("iMyOwn"), 7)

    def test_label_tooltips(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        self._select(button)
        labels = {w.text(): w.toolTip() for w in self._labels()}
        self.assertIn("相对父控件", labels.get("iX", ""))
        # sName 的简体释义已含原生名，tooltip 不重复附注
        self.assertTrue(labels.get("sName", "").startswith("控件名"))
        self.assertNotIn("原生名", labels.get("sName", ""))
        # 简体释义不含繁体原生名的键要附注（iMsgId：消息号 vs 原生「消息id」）
        self.assertIn("原生名：消息id", labels.get("iMsgId", ""))
        # 未知键不编造：手工加一个怪键后无 tooltip
        button.props["iZzz"] = 1
        self.panel._rebuild()
        labels = {w.text(): w.toolTip() for w in self._labels()}
        self.assertEqual(labels.get("iZzz", ""), "")

    def test_combo_tooltip_follows_text(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        self._select(button)
        self.panel._new_key.setCurrentText("iAlign")
        self.assertIn("对齐", self.panel._new_key.toolTip())

    def test_ialign_editor_is_named_combo_for_button(self):
        button = self.doc.new_widget("CButton", parent=self.frame)
        button.props["iAlign"] = 4
        self._select(button)
        editor = self.panel._make_editor("iAlign", 4)
        editor.setParent(self.panel)   # 随窗销毁，不做孤儿 deleteLater
        self.assertIsInstance(editor, QComboBox)
        texts = [editor.itemText(i) for i in range(editor.count())]
        self.assertEqual(texts[0], "0 左上")
        self.assertEqual(texts[4], "4 居中")
        self.assertEqual(editor.currentIndex(), 4)

    def test_ialign_editor_old_scheme_for_text_frame(self):
        frame = self.doc.new_widget("CTextFrame", parent=self.frame)
        self._select(frame)
        editor = self.panel._make_editor("iAlign", 1)
        editor.setParent(self.panel)
        self.assertIsInstance(editor, QComboBox)
        texts = [editor.itemText(i) for i in range(editor.count())]
        self.assertEqual(texts, ["0 右对齐", "1 居中", "2 左对齐"])

    def test_ialign_change_moves_text(self):
        """改 iAlign 后绘制对齐立即跟随（功能 5 的验收点）。

        不栅格化：spy ``_draw_text`` 收到的对齐旗标（``_paint_text_overlay``
        只把 painter 透传给它），证明「属性 → 绘制」链路是活的。
        """
        from PySide6.QtCore import QRectF

        from ui_editor.core import painters

        button = self.doc.new_widget("CTextButton", parent=self.frame)
        button.props["sText"] = "登录"
        button.set_geometry(x=0, y=0, width=120, height=44)
        ctx = self.window.ctx
        seen = []
        original = painters._draw_text

        def spy(p, rect, text, font, color,
                align_flags=painters._TOP_LEFT, rich=False):
            seen.append(align_flags)

        painters._draw_text = spy
        try:
            def flags_for(align):
                if align is None:
                    button.props.pop("iAlign", None)
                else:
                    button.props["iAlign"] = align
                seen.clear()
                painters._paint_text_overlay(
                    None, button, ctx, QRectF(0, 0, 120, 44))
                self.assertEqual(len(seen), 1)
                return seen[0]

            A = Qt.AlignmentFlag
            self.assertEqual(flags_for(1), A.AlignTop | A.AlignHCenter)
            self.assertEqual(flags_for(6), A.AlignBottom | A.AlignLeft)
            self.assertEqual(flags_for(5), A.AlignVCenter | A.AlignRight)
            self.assertEqual(flags_for(None),
                             A.AlignTop | A.AlignHCenter)
        finally:
            painters._draw_text = original


if __name__ == "__main__":
    unittest.main()
