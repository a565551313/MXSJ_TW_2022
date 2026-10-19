"""GUI：画布按住拖框多选（真实鼠标事件，offscreen）。

回归用户需求「画布中需要有按住鼠标拖动多选的功能」：空白处按下拖动
→ 擦到的控件全部选中；在控件上按下仍是拖动控件本身，不拖框。
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FIXTURE = Path(__file__).parent / "fixtures" / "original_style.dlg"


class TestRubberBandMultiSelect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from PySide6.QtCore import Qt

        from ui_editor.ui.main_window import MainWindow

        assert Qt  # 导入即用，保持与真实事件同一套枚举
        self.window = MainWindow()
        self.window.resize(1000, 700)
        self.window.show()
        self.window.open_layout_file(str(FIXTURE))
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(x=0, y=0, width=400, height=300)
        self.first = self._add("CButton", 20, 20)
        self.second = self._add("CTextFrame", 120, 20)
        self.window._refresh_structure()
        self.window.view.actual_size()
        self.window._select_widget(None)
        self._app.processEvents()

    def _add(self, wtype, x, y):
        widget = self.doc.new_widget(wtype, parent=self.frame)
        widget.set_geometry(x=x, y=y, width=60, height=24)
        return widget

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _view(self):
        return self.window.view

    def _drag(self, start, end):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest

        viewport = self._view().viewport()
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(viewport, end, 10)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, end)
        self._app.processEvents()

    def _empty_start(self):
        """场景左上角之外的空白处（视图坐标）。"""
        from PySide6.QtCore import QPoint

        corner = self._view().mapFromScene(self.window.scene.sceneRect()
                                           .topLeft())
        return corner + QPoint(2, 2)

    def test_drag_on_empty_area_selects_multiple(self):
        from PySide6.QtCore import QPointF

        start = self._empty_start()
        end = self._view().mapFromScene(QPointF(200, 60))
        self._drag(start, end)
        selected = {getattr(item, "widget", None) for item
                    in self.window.scene.selectedItems()}
        self.assertIn(self.first, selected)
        self.assertIn(self.second, selected)
        self.assertGreaterEqual(len(selected), 2)
        # 多选时属性面板取文档顺序第一个，状态栏报数量
        self.assertIsNotNone(self.window.current_selection())
        self.assertIn("已选中", self.window.statusBar().currentMessage())

    def test_drag_outside_widgets_selects_nothing(self):
        from PySide6.QtCore import QPoint

        start = self._empty_start()
        self._drag(start, start + QPoint(6, 6))
        self.assertEqual(self.window.scene.selectedItems(), [])

    def test_press_on_widget_drags_widget_not_band(self):
        """在控件上按下是拖控件本身：只选中它一个，座标跟着动。

        夹具里控件互相叠放，先问视图「这个点上是哪个图元」，再对它断言，
        避免假设我们的控件在最上层。
        """
        from PySide6.QtCore import QPoint, QPointF, Qt
        from PySide6.QtTest import QTest

        view = self._view()
        start = view.mapFromScene(QPointF(30, 30))
        hit = view.itemAt(start)
        self.assertIsNotNone(hit)
        widget = hit.widget
        before = (widget.x, widget.y)
        viewport = view.viewport()
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, start)
        QTest.mouseMove(viewport, start + QPoint(30, 0), 10)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier,
                           start + QPoint(30, 0))
        self._app.processEvents()
        selected = self.window.scene.selectedItems()
        self.assertEqual(len(selected), 1)      # 不是框选
        self.assertIs(selected[0], hit)
        self.assertTrue(hit.isSelected())
        self.assertNotEqual((widget.x, widget.y), before)


if __name__ == "__main__":
    unittest.main()
