"""固定视口标尺：Ctrl+R、独立网格、缩放/滚动与几何回归。"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QToolBar

    from ui_editor.core.model import LayoutDocument, Widget
    from ui_editor.ui.main_window import MainWindow
    from ui_editor.ui.rulers import RULER_THICKNESS, ruler_step

    HAS_QT = True
except ImportError:  # pragma: no cover - 无 Qt 环境
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class RulerStepTests(unittest.TestCase):
    def test_nice_steps_follow_zoom(self):
        self.assertEqual(ruler_step(1.0), 100)
        self.assertEqual(ruler_step(2.0), 50)
        self.assertEqual(ruler_step(0.5), 200)
        for scale in (0.08, 0.5, 1.0, 2.0, 8.0):
            self.assertGreaterEqual(ruler_step(scale) * scale, 72)
        self.assertGreater(ruler_step(0), 0)


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class ViewportRulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.new_layout()
        self.window.doc.roots[0].set_geometry(width=800, height=600)
        self.window._refresh_structure()
        self.window.resize(1000, 700)
        self.window.show()
        self._app.processEvents()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_ctrl_r_action_toggles_fixed_rulers(self):
        window = self.window
        action = window._act_rulers
        self.assertEqual(action.shortcut().toString(), "Ctrl+R")
        self.assertIn(action, window.findChildren(QToolBar)[0].actions())
        self.assertFalse(action.icon().isNull())
        self.assertFalse(window.view.rulers.visible)
        baseline = window.view.viewport().geometry()
        action.trigger()
        self._app.processEvents()
        self.assertTrue(action.isChecked())
        self.assertTrue(window.view.rulers.visible)
        self.assertTrue(window.view.rulers.horizontal.isVisible())
        self.assertTrue(window.view.rulers.vertical.isVisible())
        self.assertFalse(window.scene.show_grid)  # Ctrl+R 不顺带开网格
        action.trigger()
        self._app.processEvents()
        self.assertFalse(window.view.rulers.visible)
        self.assertFalse(window.view.rulers.horizontal.isVisible())
        # 关闭只撤掉 24px 标尺边距；QGraphicsView 自身边框保持原样。
        self.assertEqual(window.view.viewport().geometry().x(), baseline.x())
        self.assertEqual(window.view.viewport().geometry().y(), baseline.y())

    def test_grid_and_rulers_are_independent(self):
        self.window._act_rulers.trigger()
        self.window._act_grid.trigger()
        self.assertTrue(self.window.view.rulers.visible)
        self.assertTrue(self.window.scene.show_grid)
        self.window._act_rulers.trigger()
        self.assertFalse(self.window.view.rulers.visible)
        self.assertTrue(self.window.scene.show_grid)

    def test_rulers_stay_on_viewport_edges_after_resize_and_scroll(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        self._app.processEvents()

        def assert_geometry():
            viewport = view.viewport().geometry()
            horizontal = view.rulers.horizontal.geometry()
            vertical = view.rulers.vertical.geometry()
            self.assertEqual((horizontal.x(), horizontal.y()),
                             (viewport.x(), 0))
            self.assertEqual(horizontal.width(), viewport.width())
            self.assertEqual(horizontal.height(), RULER_THICKNESS)
            self.assertEqual((vertical.x(), vertical.y()),
                             (0, viewport.y()))
            self.assertEqual(vertical.width(), RULER_THICKNESS)
            self.assertEqual(vertical.height(), viewport.height())
            self.assertEqual(view.rulers.corner.geometry().width(),
                             RULER_THICKNESS)

        assert_geometry()
        before = view.rulers.horizontal._scene_range()
        view.horizontalScrollBar().setValue(
            min(100, view.horizontalScrollBar().maximum()))
        self._app.processEvents()
        after = view.rulers.horizontal._scene_range()
        if view.horizontalScrollBar().maximum() > 0:
            self.assertNotEqual(after, before)
        assert_geometry()
        self.window.resize(1100, 760)
        self._app.processEvents()
        assert_geometry()

    def test_zoom_changes_ruler_scale_without_moving_strip(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        geometry = view.rulers.horizontal.geometry()
        self.assertEqual(view.rulers.horizontal._scale(), 1.0)
        view.scale(2.0, 2.0)
        view.rulers.update()
        self.assertEqual(view.rulers.horizontal._scale(), 2.0)
        self.assertEqual(ruler_step(view.rulers.horizontal._scale()), 50)
        self.assertEqual(view.rulers.horizontal.geometry(), geometry)
        view.fit_content()
        self.assertGreater(view.rulers.horizontal._scale(), 0)

    def _drag(self, widget, start: QPoint, end: QPoint) -> None:
        QTest.mousePress(widget, Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(widget, end)
        QTest.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=end)
        self._app.processEvents()

    def test_mouse_drags_horizontal_guide_out_of_top_ruler(self):
        window = self.window
        view = window.view
        view.set_rulers_visible(True)
        view.actual_size()
        self._app.processEvents()
        strip = view.rulers.horizontal
        viewport = view.viewport()
        target = viewport.rect().center()
        end = strip.mapFromGlobal(viewport.mapToGlobal(target))
        native_before = window.doc.to_native_dicts()
        window.doc.dirty = False

        self._drag(strip, QPoint(80, 12), end)

        expected = view.mapToScene(target).y()
        self.assertEqual(window.scene.manual_guides()[0], [])
        self.assertEqual(len(window.scene.manual_guides()[1]), 1)
        self.assertAlmostEqual(window.scene.manual_guides()[1][0], expected)
        self.assertFalse(window.doc.dirty)
        self.assertEqual(window.doc.to_native_dicts(), native_before)

    def test_mouse_drags_vertical_guide_out_of_left_ruler(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        self._app.processEvents()
        strip = view.rulers.vertical
        viewport = view.viewport()
        target = viewport.rect().center()
        end = strip.mapFromGlobal(viewport.mapToGlobal(target))

        self._drag(strip, QPoint(12, 80), end)

        expected = view.mapToScene(target).x()
        self.assertEqual(self.window.scene.manual_guides()[1], [])
        self.assertEqual(len(self.window.scene.manual_guides()[0]), 1)
        self.assertAlmostEqual(self.window.scene.manual_guides()[0][0], expected)

    def test_mouse_moves_existing_horizontal_guide_on_viewport(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        self._app.processEvents()
        viewport = view.viewport()
        scene_x = view.mapToScene(viewport.rect().center()).x()
        self.window.scene.set_ruler_guides([], [120])
        start = view.mapFromScene(QPointF(scene_x, 120))
        end = start + QPoint(40, 60)

        self._drag(viewport, start, end)

        expected = view.mapToScene(end).y()
        self.assertEqual(len(self.window.scene.manual_guides()[1]), 1)
        self.assertAlmostEqual(self.window.scene.manual_guides()[1][0], expected)

    def test_mouse_drags_existing_vertical_guide_back_to_ruler_to_delete(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        self._app.processEvents()
        viewport = view.viewport()
        scene_y = view.mapToScene(viewport.rect().center()).y()
        self.window.scene.set_ruler_guides([120], [])
        start = view.mapFromScene(QPointF(120, scene_y))
        end = viewport.mapFromGlobal(
            view.rulers.vertical.mapToGlobal(QPoint(12, 80)))

        self._drag(viewport, start, end)

        self.assertEqual(self.window.scene.manual_guides(), ([], []))

    def test_guide_drag_uses_zoomed_and_scrolled_scene_coordinates(self):
        view = self.window.view
        view.set_rulers_visible(True)
        view.actual_size()
        view.scale(2.0, 2.0)
        view.horizontalScrollBar().setValue(
            view.horizontalScrollBar().maximum() // 2)
        view.verticalScrollBar().setValue(
            view.verticalScrollBar().maximum() // 2)
        self._app.processEvents()
        strip = view.rulers.vertical
        viewport = view.viewport()
        target = viewport.rect().center()
        end = strip.mapFromGlobal(viewport.mapToGlobal(target))

        self._drag(strip, QPoint(12, 80), end)

        expected = view.mapToScene(target).x()
        self.assertGreater(view.horizontalScrollBar().maximum(), 0)
        self.assertEqual(len(self.window.scene.manual_guides()[0]), 1)
        self.assertAlmostEqual(self.window.scene.manual_guides()[0][0], expected)

    def test_manual_guides_are_isolated_per_document(self):
        scene = self.window.scene
        first = self.window.doc
        second = LayoutDocument.from_dicts(first.to_dicts(), None)
        first.dirty = False
        scene.set_ruler_guides([123], [234])

        scene.set_document(second)
        self.assertEqual(scene.manual_guides(), ([], []))
        scene.set_ruler_guides([50], [60])
        scene.set_document(first)
        self.assertEqual(scene.manual_guides(), ([123], [234]))
        scene.set_document(second)
        self.assertEqual(scene.manual_guides(), ([50], [60]))
        self.assertFalse(first.dirty)
        self.assertFalse(second.dirty)

    def test_manual_guides_snap_items_but_not_transient_guide_state(self):
        scene = self.window.scene
        self.window.doc.dirty = False
        scene.set_ruler_guides([100], [100])
        item = scene.items()[0]

        snapped = item._snapped_position(QPointF(98, 98))

        self.assertEqual((snapped.x(), snapped.y()), (100, 100))
        scene.set_guides([], [])
        self.assertEqual(scene.manual_guides(), ([100], [100]))
        self.assertFalse(self.window.doc.dirty)

    def test_manual_guides_snap_nested_items_in_parent_coordinates(self):
        scene = self.window.scene
        root = self.window.doc.roots[0]
        root.set_geometry(x=500, y=300)
        child = Widget({"sWidgetType": "CButton", "sName": "child",
                        "iX": 0, "iY": 0, "iWidth": 40, "iHeight": 20},
                       parent=root)
        root.children.append(child)
        scene.set_document(self.window.doc)
        scene.set_ruler_guides([510], [310])
        item = scene.item_for(child)

        snapped = item._snapped_position(QPointF(8, 8))

        self.assertEqual((snapped.x(), snapped.y()), (10, 10))


if __name__ == "__main__":
    unittest.main()
