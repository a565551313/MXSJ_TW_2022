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
        """九片按实测命名：中列是 ``*/middle``，没有平铺的 top/middle/bottom。"""
        base = "combdialog\\内框架\\"
        pieces = [f"{row}/{col}.igs"
                  for row in ("top", "middle", "bottom")
                  for col in ("left", "middle", "right")]
        chosen = dir_base.plan(base, exists_from(*(base + p for p in pieces)))
        assert chosen is not None
        self.assertEqual(chosen.kind, "nine_slice")
        self.assertEqual(len(chosen.pieces), 9)
        self.assertEqual(chosen.pieces[1], base + "top/middle.igs")
        self.assertEqual(chosen.pieces[4], base + "middle/middle.igs")
        # 老版本的平铺命名不该再命中九片（真语料 0 命中）
        legacy = ("top/left.png", "top.png", "top/right.png",
                  "middle/left.png", "middle.png", "middle/right.png",
                  "bottom/left.png", "bottom.png", "bottom/right.png")
        chosen = dir_base.plan(
            "old/", exists_from(*("old/" + p for p in legacy)))
        self.assertNotEqual(getattr(chosen, "kind", None), "nine_slice")

    def test_h_state_family(self):
        """三态横片：0l/0c/0r … 连号，状态数记在 plan 上。"""
        base = "combdialog4\\三态按钮\\黄色分页按钮\\"
        names = []
        for index in range(4):
            names += [f"{base}{index}{side}.png" for side in "lcr"]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "h_state")
        self.assertEqual(chosen.states, 4)
        self.assertEqual(chosen.state_pieces(0),
                         (base + "0l.png", base + "0c.png", base + "0r.png"))
        self.assertEqual(chosen.state_pieces(2),
                         (base + "2l.png", base + "2c.png", base + "2r.png"))
        # 缺一块即整态作废，不半态成族
        broken = [base + "0l.png", base + "0c.png", base + "0r.png",
                  base + "1l.png", base + "1r.png"]
        chosen = dir_base.plan(base, exists_from(*broken))
        assert chosen is not None
        self.assertEqual(chosen.states, 1)

    def test_single_middle_piece(self):
        """整目录只有九片正中一块：按单图兜底（combdialog\\主框架\\石纹\\）。"""
        base = "combdialog\\主框架\\石纹\\"
        chosen = dir_base.plan(base, exists_from(base + "middle/middle.igs"))
        assert chosen is not None
        self.assertEqual(chosen.kind, "single")
        self.assertEqual(chosen.pieces, (base + "middle/middle.igs",))

    def test_priority_slices_then_frames(self):
        """拼图族压过整图族（实测 CProgress 既有 0.png 又有 left/middle/right）。"""
        base = "combdialog4\\杂图\\经验进度条\\"
        names = [base + "0.png", base + "left.png", base + "middle.png",
                 base + "right.png"]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "h_slice")
        # 九片压过横三片：48 个 CPngNineFrame 基路径两种都有
        names = [
            base + "left.png",
            base + "middle.png",
            base + "right.png",
        ] + [f"{base}{row}/{col}.png"
             for row in ("top", "middle", "bottom")
             for col in ("left", "middle", "right")]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "nine_slice")
        # 没有任何拼图族时才轮到序号帧
        names = [base + "0.png", base + "1.png", base + "2.png"]
        chosen = dir_base.plan(base, exists_from(*names))
        assert chosen is not None
        self.assertEqual(chosen.kind, "frames")

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
