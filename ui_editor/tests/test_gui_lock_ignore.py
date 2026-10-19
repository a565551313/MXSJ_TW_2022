"""GUI：锁定控件在画布上被完全无视（点不到、选不中、框选不到）。

用户要求：锁定后在画布中「完全无视它」「完全点不到」。仍照常绘制
（含右上角挂锁），解锁走控件树的锁图标。
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FIXTURE = Path(__file__).parent / "fixtures" / "original_style.dlg"


class TestLockedWidgetIgnoredOnCanvas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.open_layout_file(str(FIXTURE))
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(width=400, height=300)
        self.button = self.doc.roots[1]
        self.doc.set_parent(self.button, self.frame)
        self.button.set_geometry(x=20, y=30, width=100, height=40)
        self.window._refresh_structure()
        self.item = self.window.scene.item_for(self.button)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _lock(self):
        self.window._apply_lock([self.button], True)

    def test_locked_item_takes_no_mouse_buttons(self):
        from PySide6.QtCore import Qt

        self._lock()
        self.assertEqual(self.item.acceptedMouseButtons(),
                         Qt.MouseButton.NoButton)

    def test_locked_item_is_neither_selectable_nor_movable(self):
        from PySide6.QtWidgets import QGraphicsItem

        self._lock()
        flags = self.item.flags()
        self.assertFalse(
            flags & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.assertFalse(flags & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def test_setting_selected_programmatically_has_no_effect(self):
        self._lock()
        self.item.setSelected(True)
        self.assertFalse(self.item.isSelected())
        self.assertEqual(self.window.scene.selectedItems(), [])

    def test_locking_selected_widget_drops_canvas_selection(self):
        self.window._select_widget(self.button)
        self.assertIn(self.item, self.window.scene.selectedItems())
        self._lock()
        self.assertNotIn(self.item, self.window.scene.selectedItems())
        # 面板/树仍指向它，方便查看或解锁
        self.assertIs(self.window.current_selection(), self.button)

    def test_hit_test_falls_through_to_widget_below(self):
        from PySide6.QtCore import QPointF

        self._lock()
        view = self.window.view
        pos = view.mapFromScene(self.item.mapToScene(QPointF(5, 5)))
        self.assertIsNot(view.widget_at(pos), self.button)
        self.assertIs(view.widget_at(pos), self.frame)
        # 解锁后又能点到
        self.window._apply_lock([self.button], False)
        self.assertIs(view.widget_at(pos), self.button)

    def test_tree_selection_does_not_select_locked_on_canvas(self):
        self._lock()
        self.window._select_widget(self.button)  # 相当于在控件树点它
        self.assertNotIn(self.item, self.window.scene.selectedItems())
        self.assertIs(self.window.current_selection(), self.button)

    def test_locked_widget_is_skipped_by_rubber_band(self):
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QPainterPath

        self._lock()
        scene = self.window.scene
        path = QPainterPath()
        rect = self.item.mapRectToScene(QRectF(0, 0, 100, 40))
        path.addRect(rect)
        scene.setSelectionArea(path)  # 与拖框同一套选择逻辑
        # 框住的范围里还有未锁定的父控件，但锁定的这个不能被选中
        self.assertNotIn(self.item, scene.selectedItems())

    def test_unlock_restores_interaction(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QGraphicsItem

        self._lock()
        self.window._apply_lock([self.button], False)
        flags = self.item.flags()
        self.assertTrue(flags & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.assertTrue(flags & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        buttons = self.item.acceptedMouseButtons()
        self.assertTrue(buttons & Qt.MouseButton.LeftButton)
        self.assertTrue(buttons & Qt.MouseButton.RightButton)
        self.item.setSelected(True)
        self.assertTrue(self.item.isSelected())

    def test_lock_badge_still_painted_flag_kept(self):
        """锁定只是不交互，仍然显示（挂锁徽标由 paint 按 locked 画）。"""
        self._lock()
        self.assertTrue(self.button.locked)
        self.assertTrue(self.item.isVisible())
        self.assertIsNotNone(self.window.scene.item_for(self.button))

    def test_snapping_ignores_locked_siblings(self):
        from PySide6.QtCore import QPointF

        sibling = self.doc.new_widget("CButton", parent=self.frame)
        sibling.set_geometry(x=200, y=100, width=60, height=20)
        self.window._refresh_structure()
        self.window._apply_lock([sibling], True)  # 锁住参照物
        item = self.window.scene.item_for(self.button)
        # 挪到锁定兄弟控件的边缘附近：不吸附、不画参考线
        item._snapped_position(QPointF(199, 99))
        self.assertEqual(self.window.scene._guides_x, [])
        self.assertEqual(self.window.scene._guides_y, [])


if __name__ == "__main__":
    unittest.main()


class TestRubberBandFromLockedArea(unittest.TestCase):
    """锁定控件那块区域当空白画布：可以从上面按住拖框选别的控件。"""

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.resize(1000, 700)
        self.window.show()
        self.window.new_layout()  # 干净画布，避免夹具控件叠在上面
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(x=10, y=10, width=400, height=300)
        self.locked = self._add("CBox", 20, 20, 100, 40)
        self.first = self._add("CButton", 170, 30, 60, 24)
        self.second = self._add("CTextFrame", 170, 70, 60, 24)
        self.window._refresh_structure()
        self.window.view.fit_content()
        self.window._apply_lock([self.locked], True)
        self.window._select_widget(None)
        self._app.processEvents()

    def _add(self, wtype, x, y, w, h):
        widget = self.doc.new_widget(wtype, parent=self.frame)
        widget.set_geometry(x=x, y=y, width=w, height=h)
        return widget

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _drag_from_locked(self, end_scene):
        from PySide6.QtCore import QPointF, Qt
        from PySide6.QtTest import QTest

        view = self.window.view
        viewport = view.viewport()
        start = view.mapFromScene(QPointF(40, 40))  # 锁定控件内部
        end = view.mapFromScene(end_scene)
        self.assertTrue(view._locked_top(start))
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(viewport, start + (end - start) * 0.5, 10)
        QTest.mouseMove(viewport, end, 10)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, end)
        self._app.processEvents()

    def test_drag_from_locked_area_selects_other_widgets(self):
        from PySide6.QtCore import QPointF

        self._drag_from_locked(QPointF(280, 110))
        selected = {getattr(item, "widget", None) for item
                    in self.window.scene.selectedItems()}
        self.assertIn(self.first, selected)
        self.assertIn(self.second, selected)
        self.assertNotIn(self.locked, selected)
        self.assertIn("已选中", self.window.statusBar().currentMessage())

    def test_drag_from_locked_area_does_not_move_parent(self):
        from PySide6.QtCore import QPointF

        before = (self.frame.x, self.frame.y)
        self._drag_from_locked(QPointF(280, 110))
        self.assertEqual((self.frame.x, self.frame.y), before)
        self.assertEqual((self.first.x, self.first.y), (170, 30))

    def test_small_drag_from_locked_area_keeps_click_through(self):
        from PySide6.QtCore import QPointF, Qt
        from PySide6.QtTest import QTest

        view = self.window.view
        start = view.mapFromScene(QPointF(40, 40))
        QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        self._app.processEvents()
        selected = [getattr(item, "widget", None) for item
                    in self.window.scene.selectedItems()]
        self.assertEqual(selected, [self.frame])  # 单击仍穿透到下层

    def test_band_from_locked_area_never_selects_locked(self):
        from PySide6.QtCore import QPointF

        self._drag_from_locked(QPointF(400, 320))  # 框住整块父控件
        self.assertFalse(self.window.scene.item_for(self.locked).isSelected())
        self.assertIn(self.first,
                      {getattr(i, "widget", None) for i
                       in self.window.scene.selectedItems()})
