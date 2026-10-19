"""切片几何的纯逻辑回归（无 Qt，沙箱可跑）。

切割线全部来自资源切片本身的像素尺寸；这里钉住边界、非等宽、透明块。
"""

from __future__ import annotations

import unittest

from ui_editor.core import slicing


def pieces(*sizes: tuple[int, int]) -> tuple[slicing.Piece, ...]:
    return tuple(slicing.Piece(w, h) for w, h in sizes)


def rects(plan, target_w, target_h, blank=frozenset()):
    return [(c.index, c.dst) for c in
            slicing.layout(plan, target_w, target_h, blank)]


class TestNineSlice(unittest.TestCase):
    def plan(self, corner_w=10, corner_h=8):
        return slicing.nine_slice(pieces(
            (corner_w, corner_h), (corner_w, corner_h), (corner_w, corner_h),
            (corner_w, corner_h), (corner_w, corner_h), (corner_w, corner_h),
            (corner_w, corner_h), (corner_w, corner_h), (corner_w, corner_h),
        ))

    def test_corners_keep_native_size_edges_and_center_stretch(self):
        cells = dict(rects(self.plan(10, 8), 100, 60))
        self.assertEqual(cells[0], (0.0, 0.0, 10.0, 8.0))      # 左上
        self.assertEqual(cells[1], (10.0, 0.0, 80.0, 8.0))     # 上边只横向拉伸
        self.assertEqual(cells[2], (90.0, 0.0, 10.0, 8.0))     # 右上
        self.assertEqual(cells[3], (0.0, 8.0, 10.0, 44.0))     # 左边只纵向拉伸
        self.assertEqual(cells[4], (10.0, 8.0, 80.0, 44.0))    # 中心双向
        self.assertEqual(cells[8], (90.0, 52.0, 10.0, 8.0))    # 右下

    def test_no_gaps_and_no_overlaps(self):
        cells = dict(rects(self.plan(7, 5), 123, 77))
        xs = sorted({round(c[0], 3) for c in cells.values()})
        self.assertEqual(xs, [0.0, 7.0, 116.0])
        for index in (0, 3, 6):
            self.assertAlmostEqual(cells[index][0] + cells[index][2], 7.0)
        for index in (2, 5, 8):
            self.assertAlmostEqual(cells[index][0] + cells[index][2], 123.0)

    def test_non_equal_corner_widths_use_largest_piece(self):
        plan = slicing.nine_slice(pieces(
            (10, 8), (30, 8), (14, 8),
            (10, 8), (30, 8), (14, 8),
            (10, 8), (30, 8), (14, 8),
        ))
        cells = dict(rects(plan, 100, 60))
        self.assertEqual(cells[0][2], 10.0)   # 左列取最大宽 10
        self.assertEqual(cells[2][2], 14.0)   # 右列取最大宽 14
        self.assertEqual(cells[2][0], 86.0)   # 右边紧贴右缘
        self.assertEqual(cells[1][2], 76.0)   # 中间吃掉剩余

    def test_non_equal_row_heights(self):
        plan = slicing.nine_slice(pieces(
            (10, 6), (10, 9), (10, 6),
            (10, 6), (10, 9), (10, 6),
            (10, 12), (10, 9), (10, 12),
        ))
        cells = dict(rects(plan, 100, 60))
        self.assertEqual(cells[0][3], 9.0)    # 上行取最大高 9
        self.assertEqual(cells[6][3], 12.0)   # 下行取最大高 12
        self.assertEqual(cells[6][1], 48.0)   # 底边贴底

    def test_target_smaller_than_corners_shrinks_proportionally(self):
        cells = dict(rects(self.plan(10, 8), 15, 12))
        left = cells[0][2]
        right = cells[2][2]
        self.assertAlmostEqual(left + right, 15.0)
        self.assertAlmostEqual(left, 7.5)
        self.assertAlmostEqual(cells[2][0] + right, 15.0)  # 不越界
        self.assertNotIn(1, cells)                         # 中间压到 0 不出格

    def test_zero_target_never_negative(self):
        for w, h in ((0, 0), (1, 1), (-5, -5)):
            for _index, dst in rects(self.plan(), w, h):
                self.assertGreaterEqual(dst[2], 0.0)
                self.assertGreaterEqual(dst[3], 0.0)

    def test_blank_pieces_are_skipped(self):
        """整块全透明的切片不画：底下内容露出，其它块位置不变。"""
        normal = dict(rects(self.plan(10, 8), 100, 60))
        skipped = dict(rects(self.plan(10, 8), 100, 60, frozenset({4})))
        self.assertNotIn(4, skipped)
        for index in (0, 1, 2, 3, 5, 6, 7, 8):
            self.assertEqual(skipped[index], normal[index])

    def test_piece_count_is_validated(self):
        with self.assertRaises(ValueError):
            slicing.SlicePlan("nine_slice", pieces((1, 1), (1, 1)))
        with self.assertRaises(ValueError):
            slicing.SlicePlan("圆形切片", pieces((1, 1)))


class TestThreeWaySlices(unittest.TestCase):
    def test_h_slice_ends_fixed_middle_stretched(self):
        plan = slicing.h_slice(*pieces((12, 20), (40, 20), (16, 20)))
        cells = dict(rects(plan, 200, 30))
        self.assertEqual(cells[0], (0.0, 0.0, 12.0, 30.0))
        self.assertEqual(cells[1], (12.0, 0.0, 172.0, 30.0))
        self.assertEqual(cells[2], (184.0, 0.0, 16.0, 30.0))

    def test_h_slice_small_target(self):
        plan = slicing.h_slice(*pieces((12, 20), (40, 20), (16, 20)))
        cells = dict(rects(plan, 14, 30))
        self.assertAlmostEqual(cells[0][2] + cells[2][2], 14.0)
        self.assertNotIn(1, cells)   # 中间压到 0 不出格

    def test_v_slice_ends_fixed_middle_stretched(self):
        plan = slicing.v_slice(*pieces((20, 9), (20, 30), (20, 11)))
        cells = dict(rects(plan, 50, 100))
        self.assertEqual(cells[0], (0.0, 0.0, 50.0, 9.0))
        self.assertEqual(cells[1], (0.0, 9.0, 50.0, 80.0))
        self.assertEqual(cells[2], (0.0, 89.0, 50.0, 11.0))

    def test_v_slice_small_target(self):
        plan = slicing.v_slice(*pieces((20, 9), (20, 30), (20, 11)))
        cells = dict(rects(plan, 50, 10))
        self.assertAlmostEqual(cells[0][3] + cells[2][3], 10.0)
        self.assertNotIn(1, cells)   # 中间压到 0 不出格


class TestPlainStretch(unittest.TestCase):
    def test_single_piece_fills_target(self):
        cells = rects(slicing.stretch(slicing.Piece(32, 32)), 100, 40)
        self.assertEqual(cells, [(0, (0.0, 0.0, 100.0, 40.0))])

    def test_src_is_whole_piece(self):
        cells = slicing.layout(slicing.stretch(slicing.Piece(32, 16)), 100, 40)
        self.assertEqual(cells[0].src, (0.0, 0.0, 32.0, 16.0))


if __name__ == "__main__":
    unittest.main()
