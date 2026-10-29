"""固定视口标尺：Ctrl+R、独立网格、缩放/滚动与几何回归。"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
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

    def _blank_scene_point(self) -> QPointF:
        root = self.window.doc.roots[0]
        self.window.view.actual_size()
        # set_document 在控件外预留 40px；左边距是真实的空白画布。
        point = QPointF(root.x - 20, root.y + root.height / 2)
        self.window.view.centerOn(point)
        self._app.processEvents()
        self.assertTrue(self.window.view.viewport().rect().contains(
            self.window.view.mapFromScene(point)))
        self.assertIsNone(
            self.window.view.itemAt(self.window.view.mapFromScene(point)))
        return point

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
        scene_point = self._blank_scene_point()
        viewport = view.viewport()
        self.window.scene.set_ruler_guides([], [scene_point.y()])
        start = view.mapFromScene(scene_point)
        end = start + QPoint(40, 60)

        self._drag(viewport, start, end)

        expected = view.mapToScene(end).y()
        self.assertEqual(len(self.window.scene.manual_guides()[1]), 1)
        self.assertAlmostEqual(self.window.scene.manual_guides()[1][0], expected)

    def test_mouse_drags_existing_vertical_guide_back_to_ruler_to_delete(self):
        view = self.window.view
        view.set_rulers_visible(True)
        scene_point = self._blank_scene_point()
        viewport = view.viewport()
        self.window.scene.set_ruler_guides([scene_point.x()], [])
        start = view.mapFromScene(scene_point)
        end = viewport.mapFromGlobal(
            view.rulers.vertical.mapToGlobal(QPoint(12, 80)))

        self._drag(viewport, start, end)

        self.assertEqual(self.window.scene.manual_guides(), ([], []))

    def test_scene_items_have_priority_over_shared_guide_edge(self):
        view = self.window.view
        root = self.window.doc.roots[0]
        view.set_rulers_visible(True)
        view.actual_size()
        center = view.mapToScene(view.viewport().rect().center())
        root.set_geometry(x=int(center.x()) - 40,
                          y=int(center.y()) - 60, width=80, height=120)
        self.window._refresh_structure()
        item = self.window.scene.item_for(root)
        view.centerOn(QPointF(root.x + root.width / 2,
                              root.y + root.height / 2))
        self.window.scene.set_ruler_guides([root.x], [])
        item.setSelected(True)
        self._app.processEvents()
        start = view.mapFromScene(QPointF(root.x, root.y + 80))
        self.assertTrue(view.viewport().rect().contains(start))
        self.assertIsNotNone(view.itemAt(start))

        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=start)
        orientation = view.rulers._drag_orientation
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton,
                           pos=start)

        self.assertIsNone(orientation)
        self.assertEqual(self.window.scene.manual_guides()[0], [root.x])

        grip = self.window.scene._grips[id(item)]
        grip_center = grip.mapToScene(grip.boundingRect().center())
        self.window.scene.set_ruler_guides([grip_center.x()], [])
        view.centerOn(grip_center)
        self._app.processEvents()
        grip_point = view.mapFromScene(grip_center)
        self.assertIs(view.itemAt(grip_point), grip)
        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=grip_point)
        orientation = view.rulers._drag_orientation
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton,
                           pos=grip_point)
        self.assertIsNone(orientation)
        self.assertEqual(self.window.scene.manual_guides()[0],
                         [grip_center.x()])

    def test_hidden_rulers_do_not_start_viewport_guide_drag(self):
        view = self.window.view
        view.set_rulers_visible(False)
        center = self._blank_scene_point()
        self.window.scene.set_ruler_guides([center.x()], [])
        self._app.processEvents()
        point = view.mapFromScene(center)
        self.assertTrue(view.viewport().rect().contains(point))

        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=point)
        orientation = view.rulers._drag_orientation
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton,
                           pos=point)

        self.assertIsNone(orientation)
        self.assertEqual(self.window.scene.manual_guides()[0], [center.x()])

    def test_click_near_guide_preserves_exact_position(self):
        view = self.window.view
        view.set_rulers_visible(True)
        center = self._blank_scene_point()
        self.window.scene.set_ruler_guides([center.x()], [])
        self._app.processEvents()
        point = view.mapFromScene(center) + QPoint(3, 0)
        self.assertTrue(view.viewport().rect().contains(point))
        self.assertGreater(abs(view.mapToScene(point).x() - center.x()), 1)

        QTest.mousePress(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=point)
        orientation = view.rulers._drag_orientation
        QTest.mouseRelease(view.viewport(), Qt.MouseButton.LeftButton,
                           pos=point)

        self.assertIsNotNone(orientation)
        self.assertEqual(self.window.scene.manual_guides()[0], [center.x()])

    def test_ruler_callback_exception_is_reported(self):
        event = mock.Mock()
        event.globalPosition.return_value = QPointF(20, 20)
        with (
            mock.patch.object(
                self.window.view.rulers, "update_ruler_drag",
                side_effect=RuntimeError("ruler boom"),
            ),
            mock.patch("ui_editor.ui.rulers.QMessageBox", create=True) as box,
        ):
            self.window.view.rulers.horizontal.mouseMoveEvent(event)
        box.warning.assert_called_once()
        self.assertIn("ruler boom", str(box.warning.call_args))

    def test_viewport_callback_exception_is_reported(self):
        self.window.view.set_rulers_visible(True)
        event = mock.Mock()
        event.type.return_value = QEvent.Type.MouseButtonPress
        event.button.return_value = Qt.MouseButton.LeftButton
        event.position.return_value = QPointF(4, 4)
        with (
            mock.patch.object(
                self.window.view.rulers, "_guide_at",
                side_effect=RuntimeError("viewport boom"),
            ),
            mock.patch("ui_editor.ui.rulers.QMessageBox", create=True) as box,
        ):
            accepted = self.window.view.rulers.eventFilter(
                self.window.view.viewport(), event)
        self.assertFalse(accepted)
        box.warning.assert_called_once()
        self.assertIn("viewport boom", str(box.warning.call_args))

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
