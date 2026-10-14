"""M3.1 吸附/对齐/分布纯计算测试。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import snap  # noqa: E402


class TestSnapPosition(unittest.TestCase):
    def test_snaps_left_edge_within_threshold(self):
        # 邻居左边缘 102，被拖物左边缘 99（差 3 < 阈值 6）→ 贴齐
        x, _y, gx, _gy = snap.snap_position(
            (99, 300, 40, 20), [(102, 10, 40, 20)], None, 6)
        self.assertEqual(x, 102)
        self.assertEqual(gx, [102])

    def test_center_and_right_anchors(self):
        # 右边缘：被拖物右=138，邻居右=140 → x=100；中线亦然
        x, _y, _gx, _gy = snap.snap_position(
            (98, 0, 40, 20), [(100, 0, 40, 20)], None, 6)
        self.assertEqual(x, 100)

    def test_no_snap_outside_threshold(self):
        x, _y, gx, _gy = snap.snap_position(
            (90, 0, 40, 20), [(100, 0, 40, 20)], None, 6)
        self.assertEqual(x, 90)
        self.assertEqual(gx, [])

    def test_parent_edges_participate(self):
        x, y, gx, gy = snap.snap_position(
            (4, 186, 40, 20), [], (300, 200), 6)
        self.assertEqual(x, 0)          # 贴父容器左边缘
        self.assertEqual(y, 180)        # 底边贴父容器底（200-20）
        self.assertEqual(gx, [0])
        self.assertEqual(gy, [200])


class TestAlign(unittest.TestCase):
    def test_modes(self):
        ref = (100, 50, 80, 40)
        target = (10, 10, 20, 10)
        self.assertEqual(snap.align_position(ref, target, "left"),
                         (100, 10))
        self.assertEqual(snap.align_position(ref, target, "hcenter"),
                         (130, 10))
        self.assertEqual(snap.align_position(ref, target, "right"),
                         (160, 10))
        self.assertEqual(snap.align_position(ref, target, "top"),
                         (10, 50))
        self.assertEqual(snap.align_position(ref, target, "vcenter"),
                         (10, 65))
        self.assertEqual(snap.align_position(ref, target, "bottom"),
                         (10, 80))


class TestDistribute(unittest.TestCase):
    def test_equal_gaps_keep_ends(self):
        rects = [(0, 0, 10, 10), (25, 0, 10, 10), (100, 0, 10, 10)]
        out = snap.distribute_positions(rects, "x")
        xs = [p[0] for p in out]
        # 首尾不动 0 与 100，中间等间距：间隔 = (110-30)/2 = 40
        self.assertEqual(xs, [0, 50, 100])

    def test_too_few_unchanged(self):
        rects = [(0, 0, 10, 10), (50, 0, 10, 10)]
        self.assertEqual(snap.distribute_positions(rects, "x"),
                         [(0, 0), (50, 0)])


if __name__ == "__main__":
    unittest.main()
