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


class TestFamilyNaming(unittest.TestCase):
    """新建族：按张数与控件类型给出族内拼名，并能按文件名认回族类型。"""

    def test_piece_names_follow_measured_families(self):
        self.assertEqual(dir_base.piece_names("h_state", 3),
                         ("0l", "0c", "0r"))
        self.assertEqual(dir_base.piece_names("h_state", 6),
                         ("0l", "0c", "0r", "1l", "1c", "1r"))
        self.assertEqual(dir_base.piece_names("h_slice", 3),
                         ("left", "middle", "right"))
        self.assertEqual(dir_base.piece_names("v_slice", 3),
                         ("top", "middle", "bottom"))
        self.assertEqual(dir_base.piece_names("frames", 3), ("0", "1", "2"))
        self.assertEqual(dir_base.piece_names("single", 1), ("bg",))
        nine = dir_base.piece_names("nine_slice", 9)
        self.assertEqual(len(nine), 9)
        self.assertEqual(nine[0], "top/left")
        self.assertEqual(nine[-1], "bottom/right")

    def test_piece_names_reject_wrong_counts(self):
        # 拼名族要整族齐装：张数不对写进包也拼不出来
        self.assertIsNone(dir_base.piece_names("h_state", 4))
        self.assertIsNone(dir_base.piece_names("h_state", 2))
        self.assertIsNone(dir_base.piece_names("nine_slice", 8))
        self.assertIsNone(dir_base.piece_names("h_slice", 4))
        self.assertIsNone(dir_base.piece_names("single", 2))
        self.assertIsNone(dir_base.piece_names("frames", 0))
        self.assertIsNone(dir_base.piece_names("frames", 99))
        self.assertIsNone(dir_base.piece_names("unknown", 3))

    def test_match_kind_from_exported_names(self):
        """导出再导回来：文件名就是族内名（导出的 top-left 还原成 top/left）。"""
        self.assertEqual(
            dir_base.match_kind(["0l.png", "0c.png", "0r.png"]), "h_state")
        self.assertEqual(
            dir_base.match_kind(["left.png", "middle.png", "right.png"]),
            "h_slice")
        self.assertEqual(
            dir_base.match_kind(["top.png", "middle.png", "bottom.png"]),
            "v_slice")
        self.assertEqual(
            dir_base.match_kind(["0.png", "1.png", "2.png"]), "frames")
        self.assertEqual(dir_base.match_kind(["bg.png"]), "single")
        nine = [f"{row}-{column}.png"
                for row in ("top", "middle", "bottom")
                for column in ("left", "middle", "right")]
        self.assertEqual(dir_base.match_kind(nine), "nine_slice")

    def test_match_kind_is_order_insensitive(self):
        self.assertEqual(
            dir_base.match_kind(["0r.png", "0l.png", "0c.png"]), "h_state")

    def test_match_kind_returns_none_for_unknown_names(self):
        self.assertIsNone(dir_base.match_kind(["a.png", "b.png", "c.png"]))
        self.assertIsNone(dir_base.match_kind([]))

    def test_guess_kind_prefers_widget_type(self):
        # 名字认不出时按真包多数派：按钮多是一整张一态（CTextButton 53:35）
        self.assertEqual(dir_base.guess_kind(3, "CTextButton"), "frames")
        self.assertEqual(dir_base.guess_kind(3, "CHPagePngButton"), "frames")
        self.assertEqual(dir_base.guess_kind(3, "CHPngFrame"), "h_slice")
        self.assertEqual(dir_base.guess_kind(3, "CVFrame"), "v_slice")
        self.assertEqual(dir_base.guess_kind(9, "CPngNineFrame"), "nine_slice")
        # 9 张收不进序号帧（上限 8），退回按钮的位置词选择：3 态横片
        self.assertEqual(dir_base.guess_kind(9, "CTextButton"), "h_state")
        # 控件预选与张数对不上时退回按张数判断
        self.assertEqual(dir_base.guess_kind(9, "CHPngFrame"), "nine_slice")
        self.assertEqual(dir_base.guess_kind(1, None), "single")
        self.assertEqual(dir_base.guess_kind(2, None), "frames")
        self.assertIsNone(dir_base.guess_kind(0, None))

    def test_widget_tables_follow_measured_pack(self):
        """两张控件表各司其职：位置词歧义 vs 名字认不出。

        真包（interface.fls，729 个目录型基路径）逐类型实测：按钮的基路径
        多数是整图（CTextButton 53 / CHPagePngButton 16 / CVPagePngButton 11），
        横片只是少数（35 / 10 / 0）。
        """
        for widget in ("CTextButton", "CHPagePngButton", "CVPagePngButton"):
            self.assertEqual(dir_base.WIDGET_KINDS[widget], "h_state")
            self.assertEqual(dir_base.WIDGET_DEFAULT_KINDS[widget], "frames")
        for widget in ("CPngNineFrame", "CFrame", "CBorder"):
            self.assertEqual(dir_base.WIDGET_DEFAULT_KINDS[widget], "nine_slice")
        for widget in ("CHPngFrame", "CHFrame", "CProgress"):
            self.assertEqual(dir_base.WIDGET_DEFAULT_KINDS[widget], "h_slice")
        for widget in ("CVPngFrame", "CVFrame"):
            self.assertEqual(dir_base.WIDGET_DEFAULT_KINDS[widget], "v_slice")
        self.assertEqual(dir_base.WIDGET_DEFAULT_KINDS["CButton"], "frames")
        self.assertIn("WIDGET_DEFAULT_KINDS", dir_base.__all__)


class TestNamingRecognition(unittest.TestCase):
    """自己给图起名：左右/上下/中英缩写都认得出来。"""

    def test_chinese_three_pieces(self):
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["左", "中", "右"], "h_state"), ["0l", "0c", "0r"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["右", "左", "中"], "h_state"), ["0r", "0l", "0c"])

    def test_english_three_pieces(self):
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["left", "middle", "right"], "h_state"), ["0l", "0c", "0r"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["L", "C", "R"], "h_state"), ["0l", "0c", "0r"])

    def test_state_index_prefix(self):
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["1r", "0l", "1c", "0c", "1l", "0r"], "h_state"),
            ["1r", "0l", "1c", "0c", "1l", "0r"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["0左", "0中", "0右"], "h_state"), ["0l", "0c", "0r"])
        # 只导出第 2 态的 3 张（1l/1c/1r）：单态族里状态号多余，当这一族
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["1l", "1c", "1r"], "h_state"), ["0l", "0c", "0r"])
        # 多态时状态号必须对得上（6 张只有 0/1 两态），越界交回调用方
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["0l", "0c", "0r", "3l", "3c", "3r"], "h_state"))

    def test_nine_slice_chinese_and_shortcuts(self):
        nine = ["左上", "上中", "右上", "左中", "中中", "右中",
                "左下", "中下", "右下"]
        self.assertEqual(dir_base.map_stems_to_pieces(nine, "nine_slice"), [
            "top/left", "top/middle", "top/right",
            "middle/left", "middle/middle", "middle/right",
            "bottom/left", "bottom/middle", "bottom/right"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["tl", "tm", "tr", "ml", "mm", "mr", "bl", "bm", "br"],
            "nine_slice")[4], "middle/middle")
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["top_left", "top_middle", "top_right",
             "middle_left", "middle_middle", "middle_right",
             "bottom_left", "bottom_middle", "bottom_right"],
            "nine_slice")[0], "top/left")

    def test_vertical_aliases_do_not_crash_horizontal_families(self):
        """上/中/下 选在按钮上：认不出横向的边，交回调用方，不能抛异常。

        旧实现把 ``top`` 直接塞进 ``_H_SIDES.index()``，整个选图窗打不开。
        """
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["上", "中", "下"], "h_state"))
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["top", "middle", "bottom"], "h_state"))

    def test_non_ascii_digits_are_not_parsed(self):
        """``①``/``²`` 的 str.isdigit() 为真但 int() 会抛；只认 ASCII 数字。"""
        self.assertIsNone(dir_base.map_stems_to_pieces(["①"], "frames"))
        self.assertIsNone(dir_base.map_stems_to_pieces(["²"], "frames"))
        self.assertIsNone(dir_base.map_stems_to_pieces(["①l", "①c", "①r"],
                                                       "h_state"))

    def test_slices_and_frames(self):
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["L", "M", "R"], "h_slice"), ["left", "middle", "right"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["上", "中", "下"], "v_slice"), ["top", "middle", "bottom"])
        self.assertEqual(dir_base.map_stems_to_pieces(
            ["frame0", "frame1", "frame2"], "frames"), ["0", "1", "2"])

    def test_duplicates_and_unknown_fall_back(self):
        # 两张都叫"左"：认不出唯一对应，交回调用方按顺序
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["左", "左", "右"], "h_state"))
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["a", "b", "c"], "h_slice"))
        # 张数不合法也不认
        self.assertIsNone(dir_base.map_stems_to_pieces(
            ["左", "中"], "h_state"))

    def test_naming_hint_mentions_the_expected_names(self):
        self.assertIn("0l", dir_base.naming_hint("h_state", 3))
        self.assertIn("左", dir_base.naming_hint("h_state", 3))
        self.assertIn("top-left", dir_base.naming_hint("nine_slice", 9))
        self.assertIn("frame0", dir_base.naming_hint("frames", 3))


class TestProbePieces(unittest.TestCase):
    """「这个目录里到底有什么」：包里只有哈希，只能按候选名逐个问。"""

    def test_probe_lists_every_known_spelling(self):
        known = {
            "a/btn/0l.png", "a/btn/0c.png", "a/btn/0r.png",
            "a/btn/left1.png", "a/btn/weird.png",
        }
        found = dir_base.probe_pieces(
            "a/btn/", lambda name: name.replace("\\", "/") in known)
        # 认得的三种列出来；认不出的 weird.png 不该冒充
        self.assertEqual(set(found), {"0l.png", "0c.png", "0r.png",
                                      "left1.png"})

    def test_probe_covers_frames_and_nine_slice(self):
        known = {"a/x/0.png", "a/x/1.png", "a/x/top-left.png",
                 "a/x/middle/right.igs"}
        found = dir_base.probe_pieces(
            "a/x/", lambda name: name.replace("\\", "/") in known)
        self.assertIn("0.png", found)
        self.assertIn("1.png", found)
        self.assertIn("top-left.png", found)
        self.assertIn("middle/right.igs", found)

    def test_probe_empty_directory_is_empty(self):
        self.assertEqual(dir_base.probe_pieces("a/none/", lambda _n: False), ())
        self.assertEqual(dir_base.probe_pieces("a/none", lambda _n: True), ())
