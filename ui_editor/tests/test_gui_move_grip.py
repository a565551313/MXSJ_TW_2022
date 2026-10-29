"""画布移动手柄（0.18.0）：选中控件右上角外侧一按就能搬走。

锁死用户抱怨的「有的情况长按拖不动」：
* 普通拖动会被两种规则冻住——子控件 ≥ 父控件时被父矩形夹死、
  祖先同时被选中时被拒绝；手柄拖动（强制移动）全部绕过；
* 手柄在控件右上角**外侧**、场景级顶层图元，重叠控件盖不住它；
* 锁定控件没有手柄（锁定照旧不能动）；真搬动过松手记一步撤销，
  没搬动不记；多选时所有最高层选中项一起搬，后代不重复位移；
* 普通拖动的规则一字不改（吸附/夹取/祖先冻结照旧），手柄跟随
  控件移动与属性面板改几何。
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtWidgets import QApplication, QGraphicsSceneMouseEvent

    from ui_editor.core.assets import AssetResolver
    from ui_editor.core.model import LayoutDocument, Widget
    from ui_editor.core.painters import PaintContext
    from ui_editor.ui import canvas
    from ui_editor.ui.canvas import _GRIP, LayoutScene, MoveGripItem

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False


def _doc() -> LayoutDocument:
    """父 100x80 里装一个 200x100 的子控件：子 ≥ 父，普通拖动被冻死。"""
    parent = Widget({"sWidgetType": "CFrame", "sName": "parent",
                     "iX": 0, "iY": 0, "iWidth": 100, "iHeight": 80})
    child = Widget({"sWidgetType": "CButton", "sName": "child",
                    "iX": 0, "iY": 0, "iWidth": 200, "iHeight": 100},
                   parent=parent)
    parent.children.append(child)
    return LayoutDocument(roots=[parent])


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class MoveGripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.geometry: list = []
        self.commits: list = []
        self.ctx = PaintContext(AssetResolver())
        self.doc = _doc()
        self.scene = LayoutScene(
            self.ctx, self.geometry.append, self.commits.append)
        # 吸附恒等：这组测的是夹取与祖先冻结，不是吸附
        patcher = mock.patch.object(
            canvas.snap, "snap_position",
            side_effect=lambda rect, others, parent_size, threshold:
                (rect[0], rect[1], [], []))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.scene.set_document(self.doc)
        self.parent = self.doc.roots[0]
        self.child = self.doc.roots[0].children[0]
        self.parent_item = self.scene.item_for(self.parent)
        self.child_item = self.scene.item_for(self.child)

    def tearDown(self):
        self.scene.set_document(None)
        self._app.processEvents()

    def _grip_of(self, item):
        grip = self.scene._grips.get(id(item))
        self.assertIsInstance(grip, MoveGripItem)
        return grip

    # -- 出现/消失 -----------------------------------------------------
    def test_grip_appears_on_selection_outside_top_right(self):
        self.assertEqual(self.scene._grips, {})
        self.child_item.setSelected(True)
        grip = self._grip_of(self.child_item)
        self.assertIsNone(grip.parentItem())    # 场景级顶层，不随父图元裁剪
        self.assertEqual(grip.zValue(), 1e6)    # 重叠控件盖不住
        # 子控件 (0,0) 200x100：手柄在右上角再往外挪一点，不盖控件本体
        self.assertAlmostEqual(grip.pos().x(), 200 + 5)
        self.assertAlmostEqual(grip.pos().y(), -_GRIP - 5)
        self.child_item.setSelected(False)
        self.assertEqual(self.scene._grips, {})

    def test_locked_widget_has_no_grip(self):
        self.child_item.setSelected(True)
        self.assertIn(id(self.child_item), self.scene._grips)
        self.child.locked = True
        self.child_item.apply_lock()   # 锁定：取消选中，手柄随之消失
        self.assertEqual(self.scene._grips, {})
        self.assertFalse(self.child_item.isSelected())
        self.child_item.setSelected(True)   # 锁定的选不中 → 不会有手柄
        self.assertFalse(self.child_item.isSelected())
        self.assertEqual(self.scene._grips, {})

    def test_set_document_clears_grips(self):
        self.child_item.setSelected(True)
        self.assertEqual(len(self.scene._grips), 1)
        self.scene.set_document(_doc())   # 换文档：账本清零，不悬空
        self.assertEqual(self.scene._grips, {})

    # -- 普通拖动规则一字不改（两种「拖不动」照旧） --------------------
    def test_normal_drag_still_clamped_and_ancestor_frozen(self):
        self.child_item.setPos(50, 30)   # 子 ≥ 父：夹回 (0,0)
        self.assertEqual((self.child.x, self.child.y), (0, 0))
        self.parent_item.setSelected(True)
        self.child_item.setSelected(True)
        self.child_item.setPos(40, 20)   # 祖先已选中：拒绝，原地不动
        self.assertEqual((self.child.x, self.child.y), (0, 0))

    # -- 手柄拖动 = 强制移动 -------------------------------------------
    def test_grip_drag_bypasses_parent_clamp(self):
        self.child_item.setSelected(True)
        grip = self._grip_of(self.child_item)
        start = QPointF(grip.pos())
        grip.begin_drag(start)
        grip.drag_to(QPointF(start.x() + 60, start.y() + 40))
        grip.finish_drag()
        self.assertEqual((self.child.x, self.child.y), (60, 40))
        self.assertEqual(self.commits, [self.child])   # 松手记一步撤销

    def test_grip_drag_with_ancestor_selected_moves_subtree_once(self):
        self.parent_item.setSelected(True)
        self.child_item.setSelected(True)
        self.assertEqual(len(self.scene._grips), 2)
        grip = self._grip_of(self.child_item)
        start = QPointF(grip.pos())
        grip.begin_drag(start)
        grip.drag_to(QPointF(start.x() + 50, start.y() + 30))
        grip.finish_drag()
        # 父子同选只搬最高层父项；子的局部坐标不变，场景位置跟随一次。
        self.assertEqual((self.parent.x, self.parent.y), (50, 30))
        self.assertEqual((self.child.x, self.child.y), (0, 0))
        self.assertEqual(self.doc.abs_position(self.child), (50, 30))
        self.assertEqual(self.commits, [self.parent])

    def _add_selected_root(self):
        other = self.doc.new_widget("CButton")
        other.set_geometry(x=300, y=200, width=60, height=24)
        self.scene.set_document(self.doc)
        self.parent_item = self.scene.item_for(self.parent)
        self.child_item = self.scene.item_for(self.child)
        return other, self.scene.item_for(other)

    def test_grip_drag_moves_every_selected_widget_together(self):
        other, other_item = self._add_selected_root()
        self.child_item.setSelected(True)
        other_item.setSelected(True)
        grip = self._grip_of(self.child_item)
        start = QPointF(grip.pos())
        grip.begin_drag(start)
        grip.drag_to(QPointF(start.x() + 60, start.y() + 40))
        grip.finish_drag()
        self.assertEqual((self.child.x, self.child.y), (60, 40))
        self.assertEqual((other.x, other.y), (360, 240))
        self.assertEqual((self.parent.x, self.parent.y), (0, 0))
        self.assertEqual(self.commits, [self.child])  # 整组只提交一次

    def test_group_drag_excludes_selected_roots_from_snap_candidates(self):
        other, other_item = self._add_selected_root()
        self.parent_item.setSelected(True)
        other_item.setSelected(True)
        other_rect = (300.0, 200.0, 60.0, 24.0)
        candidates = []

        def spy(rect, others, parent_size, threshold):
            candidates.append(others)
            return rect[0], rect[1], [], []

        with mock.patch.object(canvas.snap, "snap_position", side_effect=spy):
            # 普通拖动保持旧行为：另一个根仍可作为吸附参考。
            self.parent_item._snapped_position(QPointF(2, 2))
            self.assertEqual(candidates[-1], [other_rect])
            grip = self._grip_of(self.parent_item)
            start = QPointF(grip.pos())
            grip.begin_drag(start)
            grip.drag_to(QPointF(start.x() + 2, start.y() + 2))
            grip.finish_drag()
        self.assertGreater(len(candidates), 1)
        self.assertTrue(all(other_rect not in others
                            for others in candidates[1:]), candidates)

    def test_group_grip_is_one_undo_and_redo_step(self):
        other, other_item = self._add_selected_root()
        self.child_item.setSelected(True)
        other_item.setSelected(True)
        self.doc.reset_history()
        original_callbacks = {
            item: item.on_commit for item in self.scene._items.values()}
        try:
            for item in original_callbacks:
                item.on_commit = lambda _widget: self.doc.checkpoint()
            grip = self._grip_of(self.child_item)
            start = QPointF(grip.pos())
            grip.begin_drag(start)
            grip.drag_to(QPointF(start.x() + 60, start.y() + 40))
            grip.finish_drag()
            self.assertTrue(self.doc.undo())  # 一步回到整组拖动前
            self.assertEqual((self.doc.roots[0].children[0].x,
                              self.doc.roots[0].children[0].y), (0, 0))
            self.assertEqual((self.doc.roots[1].x, self.doc.roots[1].y),
                             (300, 200))
            self.assertTrue(self.doc.redo())
            self.assertEqual((self.doc.roots[0].children[0].x,
                              self.doc.roots[0].children[0].y), (60, 40))
            self.assertEqual((self.doc.roots[1].x, self.doc.roots[1].y),
                             (360, 240))
        finally:
            for item, original in original_callbacks.items():
                item.on_commit = original

    def test_grip_drag_zero_movement_commits_nothing(self):
        self.child_item.setSelected(True)
        grip = self._grip_of(self.child_item)
        start = QPointF(grip.pos())
        grip.begin_drag(start)
        grip.drag_to(QPointF(start))
        grip.finish_drag()
        grip.finish_drag()   # 重复松手不重复记步
        self.assertEqual(self.commits, [])
        self.assertEqual((self.child.x, self.child.y), (0, 0))

    def test_child_grip_follows_selected_parent_move(self):
        """PR #89 审查修复：父被搬动时，选中的子控件手柄也要跟上（原先留在旧位置）。"""
        self.parent_item.setSelected(True)
        self.child_item.setSelected(True)
        child_grip = self._grip_of(self.child_item)
        # 普通拖动父控件：子图元自己的 itemChange 不触发，手柄靠级联同步
        self.parent_item.setPos(30, 20)
        self.assertAlmostEqual(child_grip.pos().x(), 30 + 200 + 5)
        self.assertAlmostEqual(child_grip.pos().y(), 20 - _GRIP - 5)
        # 父控件的手柄强制移动同样级联
        parent_grip = self._grip_of(self.parent_item)
        start = QPointF(parent_grip.pos())
        parent_grip.begin_drag(start)
        parent_grip.drag_to(QPointF(start.x() + 10, start.y() + 10))
        parent_grip.finish_drag()
        self.assertAlmostEqual(child_grip.pos().x(), 40 + 200 + 5)
        self.assertAlmostEqual(child_grip.pos().y(), 30 - _GRIP - 5)
        self.assertEqual(self.commits, [self.parent])   # 只记被握的那个

    def test_resize_moves_own_grip(self):
        """PR #89 审查修复：缩放走 _syncing 不经 itemChange，手柄要显式跟到新角落。"""
        self.parent_item.setSelected(True)
        grip = self._grip_of(self.parent_item)
        self.parent_item._press_geom = (0, 0, 100, 80)   # 相当于按压把手
        self.parent_item._resize_handle = "se"
        self.parent_item._resize_start = (
            0.0, 0.0, 100.0, 80.0, QPointF(100, 80))
        ev = QGraphicsSceneMouseEvent()
        ev.setButton(Qt.MouseButton.LeftButton)
        ev.setScenePos(QPointF(130, 100))   # 右下角拖到 130x100
        self.parent_item.mouseMoveEvent(ev)
        self.assertEqual((self.parent.width, self.parent.height), (130, 100))
        self.assertAlmostEqual(grip.pos().x(), 130 + 5)
        self.assertAlmostEqual(grip.pos().y(), -_GRIP - 5)
        rel = QGraphicsSceneMouseEvent()
        rel.setButton(Qt.MouseButton.LeftButton)
        self.parent_item.mouseReleaseEvent(rel)
        self.assertEqual(self.commits, [self.parent])   # 缩放松手记一步

    def test_grip_follows_normal_drag_and_panel_refresh(self):
        self.parent_item.setSelected(True)
        grip = self._grip_of(self.parent_item)
        self.parent_item.setPos(30, 20)   # 根图元没有父矩形约束
        self.assertAlmostEqual(grip.pos().x(), 30 + 100 + 5)
        self.assertAlmostEqual(grip.pos().y(), 20 - _GRIP - 5)
        # 属性面板改几何 → refresh_widget 也要把手柄对齐到新角落
        self.parent.props["iX"] = 60
        self.parent.props["iY"] = 50
        self.scene.refresh_widget(self.parent)
        self.assertAlmostEqual(grip.pos().x(), 60 + 100 + 5)
        self.assertAlmostEqual(grip.pos().y(), 50 - _GRIP - 5)


if __name__ == "__main__":
    unittest.main()
