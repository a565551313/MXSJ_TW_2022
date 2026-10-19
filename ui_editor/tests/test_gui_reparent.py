"""GUI：置父/升除级、右键菜单、拖框多选与父内拖动的联动。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FIXTURE = Path(__file__).parent / "fixtures" / "original_style.dlg"


class TestReparentCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self.window.open_layout_file(str(FIXTURE))

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_reparent_moves_into_parent_and_keeps_inside(self):
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        w._select_widget(other)
        w.reparent_to(main)
        self.assertIs(other.parent, main)
        self.assertGreaterEqual(other.x, 0)
        self.assertGreaterEqual(other.y, 0)
        self.assertLessEqual(other.x + other.width, main.width)
        self.assertLessEqual(other.y + other.height, main.height)
        self.assertIs(w.current_selection(), other)
        self.assertIsNotNone(w.tree_panel._items.get(id(other)))

    def test_promote_to_top_keeps_absolute_position(self):
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        w._select_widget(other)
        w.reparent_to(main)
        inside = w.doc.abs_position(other)
        w.promote_selected_to_root()
        self.assertIsNone(other.parent)
        self.assertEqual(w.doc.abs_position(other), inside)

    def test_locked_widget_is_refused(self):
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        other.locked = True
        w._select_widget(other)
        w.reparent_to(main)
        self.assertIsNone(other.parent)
        self.assertIn("锁定", w.statusBar().currentMessage())

    def test_canvas_menu_has_parent_submenu_and_promote(self):
        w = self.window
        w._select_widget(w.doc.roots[0])
        menu = w.build_canvas_context_menu(w.doc.roots[0])
        titles = [a.text() for a in menu.actions()]
        self.assertIn("设为顶级", titles)
        submenus = [a for a in menu.actions() if a.menu() is not None]
        self.assertTrue(any(a.text() == "置父" for a in submenus))
        parent_menu = next(a.menu() for a in submenus if a.text() == "置父")
        labels = [a.text() for a in parent_menu.actions()]
        self.assertFalse(any("(没有可选的父控件)" in t for t in labels))
        self.assertFalse(any(w.doc.roots[0].name in t for t in labels))

    def test_tree_menu_exists(self):
        from PySide6.QtWidgets import QTreeWidget
        w = self.window
        tree = w.tree_panel.findChild(QTreeWidget)
        self.assertIsNotNone(tree)
        self.assertTrue(w.tree_panel._indent_btn is not None)
        self.assertFalse(w.tree_panel._indent_btn.isEnabled())  # 未选中

    def test_arrow_buttons_state(self):
        w = self.window
        main = w.doc.roots[0]
        w._select_widget(main)
        self.assertFalse(w.tree_panel._outdent_btn.isEnabled())  # 已在顶层
        child = main.children[0] if main.children else None
        if child is None:
            w.add_widget("CBox")
            child = w.current_selection()
        w._select_widget(child)
        self.assertTrue(w.tree_panel._outdent_btn.isEnabled())

    def test_view_uses_rubber_band(self):
        from PySide6.QtWidgets import QGraphicsView
        self.assertEqual(self.window.view.dragMode(),
                         QGraphicsView.DragMode.RubberBandDrag)
        self.assertEqual(
            self.window.view.rubberBandSelectionMode().name,
            "IntersectsItemShape")

    def test_child_drag_is_clamped_inside_parent(self):
        from PySide6.QtCore import QPointF
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        w._select_widget(other)
        w.reparent_to(main)
        item = w.scene.item_for(other)
        clamped = item._clamped_position(QPointF(99999, 99999))
        self.assertLessEqual(clamped.x() + item._width, main.width)
        self.assertLessEqual(clamped.y() + item._height, main.height)

    def test_nested_selection_freezes_child_position(self):
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QGraphicsItem
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        w._select_widget(other)
        w.reparent_to(main)
        parent_item = w.scene.item_for(main)
        child_item = w.scene.item_for(other)
        parent_item.setSelected(True)
        child_item.setSelected(True)
        before = child_item.pos()
        returned = child_item.itemChange(
            QGraphicsItem.GraphicsItemChange.ItemPositionChange,
            QPointF(50, 50))
        self.assertEqual(returned, before)

    def test_lock_does_not_block_child_drag(self):
        w = self.window
        main = w.doc.roots[0]
        other = w.doc.roots[1]
        w._select_widget(other)
        w.reparent_to(main)
        main.locked = True
        w.scene.item_for(main).apply_lock()
        w.scene.item_for(other).apply_lock()
        from PySide6.QtWidgets import QGraphicsItem

        movable = QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        self.assertFalse(w.scene.item_for(main).flags() & movable)
        self.assertTrue(w.scene.item_for(other).flags() & movable)


if __name__ == "__main__":
    unittest.main()
