"""目录型基路径拼名规则的纯逻辑回归（无 Qt，沙箱可跑）。"""

from __future__ import annotations

import unittest

from ui_editor.core import dir_base


def exists_from(*names: str):
    known = set(names)

    def exists(name: str) -> bool:
        return name in known

    return exists


class TestDirBase(unittest.TestCase):
    def test_is_dir_base(self):
        self.assertTrue(dir_base.is_dir_base("a\\b\\"))
        self.assertTrue(dir_base.is_dir_base("a/b/"))
        self.assertFalse(dir_base.is_dir_base("a/b.png"))
        self.assertFalse(dir_base.is_dir_base(""))

    def test_frame_series_verified_sound_button(self):
        """声音按钮\\关闭\\ 同款：0/1/2.png 三帧，3.png 缺席即停。"""
        base = "combdialog4\\新登陆界面\\三态按钮\\声音按钮\\关闭\\"
        exists = exists_from(base + "0.png", base + "1.png", base + "2.png")
        chosen = dir_base.plan(base, exists)
        self.assertIsNotNone(chosen)
        assert chosen is not None
        self.assertEqual(chosen.kind, "frames")
        self.assertEqual(
            chosen.pieces,
            (base + "0.png", base + "1.png", base + "2.png"),
        )

    def test_frame_series_requires_zero_frame(self):
        """没有 0 号帧不算序号帧族（GetInitPath 从 0.png 起）。"""
        base = "dir/"
        self.assertIsNone(dir_base.frame_series(base, exists_from(base + "1.png")))
        self.assertIsNone(dir_base.plan(base, exists_from(base + "1.png")))

    def test_frame_series_igs_fallback_and_cap(self):
        base = "x/"
        names = [base + "0.igs", base + "1.png", base + "2.igs"]
        names += [base + f"{i}.png" for i in range(3, 20)]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "frames")
        self.assertEqual(len(chosen.pieces), dir_base.FRAME_MAX)
        self.assertEqual(chosen.pieces[0], base + "0.igs")

    def test_h_slice_variants(self):
        base = "输入底框/"
        chosen = dir_base.plan(
            base,
            exists_from(base + "left1.png", base + "middle.png", base + "right2.png"),
        )
        assert chosen is not None
        self.assertEqual(chosen.kind, "h_slice")
        self.assertEqual(
            chosen.pieces,
            (base + "left1.png", base + "middle.png", base + "right2.png"),
        )
        chosen = dir_base.plan(
            base,
            exists_from(base + "left.png", base + "middle.png", base + "right.png"),
        )
        assert chosen is not None
        self.assertEqual(chosen.kind, "h_slice")
        self.assertEqual(chosen.pieces[0], base + "left.png")
        # 缺 middle 不算整族
        self.assertIsNone(
            dir_base.plan(base, exists_from(base + "left.png", base + "right.png"))
        )

    def test_v_slice(self):
        base = "框/"
        chosen = dir_base.plan(
            base,
            exists_from(base + "top.png", base + "middle.png", base + "bottom.png"),
        )
        assert chosen is not None
        self.assertEqual(chosen.kind, "v_slice")

    def test_nine_slice(self):
        """整组九片优先于竖三片（九片集含 top/middle/bottom，不能被抢先）。"""
        base = "上文字底/"
        pieces = (
            "top/left.png",
            "top.png",
            "top/right.png",
            "middle/left.png",
            "middle.png",
            "middle/right.png",
            "bottom/left.png",
            "bottom.png",
            "bottom/right.png",
        )
        chosen = dir_base.plan(base, exists_from(*(base + p for p in pieces)))
        assert chosen is not None
        self.assertEqual(chosen.kind, "nine_slice")
        self.assertEqual(len(chosen.pieces), 9)

    def test_priority_frames_then_slices(self):
        base = "b/"
        names = [
            base + "0.png",
            base + "left1.png",
            base + "middle.png",
            base + "right2.png",
        ]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "frames")
        # 无 0 号帧时横片优先于九片
        names = [
            base + "left.png",
            base + "middle.png",
            base + "right.png",
            base + "top/left.png",
            base + "top.png",
            base + "top/right.png",
            base + "middle/left.png",
            base + "middle/right.png",
            base + "bottom/left.png",
            base + "bottom.png",
            base + "bottom/right.png",
        ]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "h_slice")

    def test_plan_rejects_file_names_and_dead_dirs(self):
        self.assertIsNone(dir_base.plan("images/a.png", exists_from("images/a.png")))
        self.assertIsNone(dir_base.plan("dead\\", exists_from("dead\\0.png.bak")))

    def test_bg_single_family(self):
        # 官服 1019 实测 6 例：整目录一张 bg.png，单图族兜底出整图
        base = "mainmenu3\\任务栏\\透明底框\\"
        chosen = dir_base.plan(base, exists_from(base + "bg.png"))
        assert chosen is not None
        self.assertEqual(chosen.kind, "single")
        self.assertEqual(chosen.pieces, (base + "bg.png",))
        # 有整族拼图/序号帧时不让位给单图
        base = "x\\"
        names = [base + "0.png", base + "1.png", base + "bg.png"]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "frames")


if __name__ == "__main__":
    unittest.main()
