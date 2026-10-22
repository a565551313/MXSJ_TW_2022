"""绘制保真度与运行时可见状态的纯逻辑回归（无 Qt）。"""

from __future__ import annotations

import unittest

from ui_editor.core import fidelity, runtime_state
from ui_editor.core.model import Widget


class FakeView:
    """只回答保真度需要的三个问题（+ 可选的绘制来源）。"""

    def __init__(self, slices=None, frames=None, sizes=None, source=None):
        self._slices = slices or {}
        self._frames = frames or {}
        self._sizes = sizes or {}
        self._source = source

    def source_kind(self, widget):
        return self._source

    def slice_kind(self, name):
        return self._slices.get(name)

    def frame_count(self, name):
        return self._frames.get(name, 0)

    def image_size(self, name):
        return self._sizes.get(name)


def widget(wtype="CButton", **props):
    base = {"sWidgetType": wtype, "sName": "w", "iWidth": 100, "iHeight": 30}
    base.update(props)
    return Widget(base)


def codes(w, view, state="normal"):
    return [m.code for m in fidelity.markers(w, view, state)]


class TestRuntimeState(unittest.TestCase):
    def test_truthy_forms(self):
        for value in (True, 1, "1", "true", "YES", [1]):
            self.assertIs(runtime_state.truthy(value), True, value)
        for value in (False, 0, "0", "false", "no", [0]):
            self.assertIs(runtime_state.truthy(value), False, value)
        self.assertIsNone(runtime_state.truthy("不知道"))

    def test_hidden_not_loaded_shown(self):
        self.assertEqual(runtime_state.state_of(widget(bShow=0)),
                         runtime_state.HIDDEN)
        self.assertEqual(runtime_state.state_of(widget(bLoad=0)),
                         runtime_state.NOT_LOADED)
        self.assertEqual(runtime_state.state_of(widget(bShow=1, bLoad=1)),
                         runtime_state.SHOWN)
        self.assertEqual(runtime_state.state_of(widget(bShow="false")),
                         runtime_state.HIDDEN)

    def test_hidden_wins_over_not_loaded(self):
        self.assertEqual(runtime_state.state_of(widget(bShow=0, bLoad=0)),
                         runtime_state.HIDDEN)

    def test_missing_field_is_unknown_not_false(self):
        plain = Widget({"sWidgetType": "CButton", "sName": "x"})
        self.assertEqual(runtime_state.state_of(plain), runtime_state.UNKNOWN)
        self.assertNotEqual(runtime_state.state_of(plain),
                            runtime_state.HIDDEN)

    def test_describe_never_says_missing(self):
        for state in (runtime_state.HIDDEN, runtime_state.NOT_LOADED):
            text = runtime_state.describe(state)
            self.assertNotIn("缺图", text)
            self.assertNotIn("未找到", text)


class TestFidelityMarkers(unittest.TestCase):
    def test_slice_family_is_native(self):
        view = FakeView(slices={"a\\": "nine_slice"},
                        frames={"a\\": 1})
        w = widget("CPngNineFrame", sFileName="a\\")
        self.assertIn("native_nine_slice", codes(w, view))
        levels = {m.level for m in fidelity.markers(w, view)}
        self.assertEqual(levels, {fidelity.NATIVE})

    def test_single_image_nine_is_approx(self):
        view = FakeView(frames={"btn.png": 1}, sizes={"btn.png": (64, 64)})
        w = widget("CPngNineFrame", sFileName="btn.png", iWidth=200)
        found = codes(w, view)
        self.assertIn("nine_fixed_thirds", found)

    def test_1to1_image_is_native_but_stretch_is_approx(self):
        view = FakeView(frames={"a.png": 1}, sizes={"a.png": (100, 30)})
        same = widget(sFileName="a.png")
        self.assertIn("native_1to1", codes(same, view))
        bigger = widget(sFileName="a.png", iWidth=300)
        self.assertIn("stretched_image", codes(bigger, view))

    def test_missing_resource_is_simulated_placeholder(self):
        w = widget(sFileName="gone.png")
        found = codes(w, FakeView())
        self.assertEqual(found, ["missing_placeholder"])
        self.assertEqual(fidelity.markers(w, FakeView())[0].level,
                         fidelity.SIMULATED)

    def test_button_state_by_frame_order_is_approx(self):
        view = FakeView(frames={"b.png": 4}, sizes={"b.png": (100, 30)})
        w = widget(sFileName="b.png")
        found = codes(w, view, "pressed")
        self.assertIn("state_by_frame_order", found)

    def test_button_state_without_frames_is_simulated(self):
        view = FakeView(frames={"b.png": 1}, sizes={"b.png": (100, 30)})
        w = widget(sFileName="b.png")
        found = codes(w, view, "pressed")
        self.assertIn("state_overlay", found)
        self.assertNotIn("state_by_frame_order", found)

    def test_runtime_hidden_marker_is_native_fact(self):
        w = widget(sFileName="a.png", bShow=0)
        view = FakeView(frames={"a.png": 1}, sizes={"a.png": (100, 30)})
        found = fidelity.markers(w, view)
        self.assertEqual(found[0].code, "runtime_hidden")
        self.assertIn("进游戏不显示", found[0].text)

    def test_auto_size_image_is_not_reported_as_missing(self):
        """iWidth/iHeight=0 的控件按图片自身尺寸画，不能说成「无图片素材」。

        真包 2,708 篇布局里 25,708 处图片字段有 23,391 处没写尺寸
        （2026-10-22 实测），登录按钮就是这种：旧实现返回空标注，状态栏
        显示「无图片素材：按控件类型/样式表绘制」——明明画的是真图。
        """
        view = FakeView(frames={"b\\": 3}, sizes={"b\\": (120, 44)})
        w = widget("CButton", sFileName="b\\", iWidth=0, iHeight=0)
        found = fidelity.markers(w, view)
        self.assertEqual([m.code for m in found], ["native_first_frame"])
        self.assertEqual(found[0].level, fidelity.NATIVE)
        self.assertIn("3 帧", found[0].text)
        self.assertTrue(fidelity.summary(w, view).startswith(fidelity.NATIVE))
        self.assertNotIn("无图片素材", fidelity.summary(w, view))

    def test_multi_frame_normal_state_mentions_state_mapping(self):
        """多帧整图：常态画 0 号帧，其余帧是状态；序号语义必须写明未核实。"""
        view = FakeView(frames={"b.png": 4}, sizes={"b.png": (120, 44)})
        w = widget("CButton", sFileName="b.png", iWidth=120, iHeight=44)
        found = fidelity.markers(w, view)
        self.assertEqual([m.code for m in found], ["native_first_frame"])
        self.assertIn("序号语义未核实", found[0].text)
        self.assertLessEqual(len(found[0].text), 60)
        # 尺寸对不上：整套拉伸，仍是「近似」
        bigger = widget("CButton", sFileName="b.png", iWidth=300, iHeight=30)
        stretched = fidelity.markers(bigger, view)
        self.assertEqual([m.code for m in stretched], ["stretched_image"])

    def test_widget_without_image_has_no_markers(self):
        w = widget("CTextFrame", sText="hi")
        self.assertEqual(fidelity.markers(w, FakeView()), [])
        self.assertIn("无图片素材", fidelity.summary(w, FakeView()))

    def test_summary_picks_worst_level(self):
        view = FakeView(slices={"a\\": "h_slice"}, frames={"a\\": 1})
        w = widget("CFrame", sFileName="a\\")
        self.assertTrue(fidelity.summary(w, view).startswith(fidelity.NATIVE))

    def test_drawn_source_drives_the_badge(self):
        """画的是皮肤就不能标占位：来源由绘制层给，角标照着标。"""
        w = widget("CTextButton", sFileName="a\\")
        cases = {
            "style_skin": ("样式表", fidelity.APPROX, "style_skin"),
            "button_style": ("编辑器默认色", fidelity.SIMULATED,
                             "button_style"),
            "editor_default": ("默认配色", fidelity.SIMULATED,
                               "editor_default"),
            "code_skin": ("脚本现造", fidelity.APPROX, "code_skin"),
            "placeholder": ("占位框", fidelity.SIMULATED,
                            "missing_placeholder"),
        }
        for source, (word, level, code) in cases.items():
            found = fidelity.markers(w, FakeView(source=source))
            self.assertEqual(len(found), 1, source)
            self.assertEqual(found[0].level, level, source)
            self.assertIn(word, found[0].text, source)
            self.assertEqual(found[0].code, code, source)

    def test_no_image_type_reports_nothing(self):
        w = widget("CTextFrame", sFileName="a.png")
        self.assertEqual(fidelity.markers(w, FakeView(source="none")), [])

    def test_dir_base_placeholder_says_slices(self):
        w = widget("CFrame", sFileName="dir\\")
        found = fidelity.markers(w, FakeView(source="placeholder"))
        self.assertIn("切片族", found[0].text)

    def test_marker_palette_has_all_levels(self):
        for level in (fidelity.NATIVE, fidelity.APPROX, fidelity.SIMULATED):
            self.assertIn(level, fidelity.MARKERS)


if __name__ == "__main__":
    unittest.main()
