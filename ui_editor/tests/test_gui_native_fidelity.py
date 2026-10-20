"""画布原生还原度：切片贴合、运行时隐藏、保真度角标、诊断分项（Qt/offscreen）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QBuffer, QByteArray  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402

from ui_editor.core import diagnostics, painters, runtime_state  # noqa: E402
from ui_editor.core.model import LayoutDocument, Widget  # noqa: E402
from ui_editor.core.painters import PaintContext  # noqa: E402


def png_bytes(width, height, color=(255, 0, 0, 255)) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGBA8888)
    image.fill(QColor(*color))
    buffer = QBuffer()
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(QByteArray(buffer.data()))


def blank_png(width, height) -> bytes:
    return png_bytes(width, height, (0, 0, 0, 0))


class FakeAssets:
    """按名字给字节的假解析器（够 painters 用）。"""

    def __init__(self, files):
        self.files = dict(files)

    def fetch_bytes(self, name):
        return self.files.get(name.replace("/", "\\"))

    def fetch_image(self, name):
        if name.endswith(("\\", "/")):
            # 目录型基路径：按拼名族把各块拼成帧列表（与真解析器同规则）
            from ui_editor.core import dir_base
            key = name.replace("/", "\\")

            def exists(candidate):
                return candidate.replace("/", "\\") in self.files

            chosen = dir_base.plan(key, exists)
            if chosen is None:
                return None
            images = []
            for piece in chosen.pieces:
                frames = self._load(piece)
                if not frames:
                    return None
                images.append(frames[0])
            return images
        return self._load(name)

    def _load(self, name):
        data = self.fetch_bytes(name)
        if data is None:
            return None
        image = QImage.fromData(data)
        return None if image.isNull() else [image]

    def fetch_slice(self, name):
        from ui_editor.core import dir_base
        from ui_editor.core.assets import SliceRecipe, image_is_blank
        if not name.endswith(("\\", "/")):
            return None
        key = name.replace("/", "\\")

        def exists(candidate):
            return candidate.replace("/", "\\") in self.files

        chosen = dir_base.plan(key, exists)
        if chosen is None or chosen.kind not in ("h_state", "h_slice",
                                                 "v_slice", "nine_slice"):
            return None
        pieces = chosen.state_pieces(0)   # 三态按钮取 0 号态（常态）
        images = [self._load(piece) for piece in pieces]
        if any(image is None for image in images):
            return None
        flat = [image[0] for image in images if image is not None]
        blank = frozenset(i for i, image in enumerate(flat)
                          if image_is_blank(image))
        kind = "h_slice" if chosen.kind == "h_state" else chosen.kind
        return SliceRecipe(kind, pieces, tuple(flat), blank)

    def frame_size(self, name):
        frames = self._load(name)
        if not frames:
            return None
        return frames[0].width(), frames[0].height()


def render(widget, assets, *, state="normal", size=(200, 60)) -> QImage:
    ctx = PaintContext(assets=assets, button_state=state)
    image = QImage(size[0], size[1], QImage.Format.Format_RGBA8888)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    try:
        painters.paint_widget(painter, widget, ctx)
    finally:
        painter.end()
    return image


def pixel(image, x, y):
    color = image.pixelColor(int(x), int(y))
    return (color.red(), color.green(), color.blue(), color.alpha())


def color_share(image, expected, tol: int = 20) -> float:
    """图像里「接近 expected」的不透明像素占比。

    皮肤可能带渐变、圆角边框，文字抗锯齿也会盖住中心那几个像素，
    所以不挑固定采样点：按色差容差统计面积，再看主色是不是它。
    """
    total = image.width() * image.height()
    if not total:
        return 0.0
    hit = 0
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() == 0:
                continue
            if all(abs(color_channel - want) <= tol for color_channel, want in zip(
                    (color.red(), color.green(), color.blue()),
                    expected[:3], strict=True)):
                hit += 1
    return hit / total


class _NeedsGui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])


class TestSliceRendering(_NeedsGui):
    """切割线来自切片资源本身：角固定、边/中心拉伸（不再是固定三等分）。"""

    def setUp(self):
        base = "frame\\"
        files = {}
        # 九片：四角红、上边绿、左边蓝、中心白 …用不同颜色区分拉伸行为
        # 九片按实测命名：中列是 top/middle、middle/middle、bottom/middle
        colors = {
            "top/left.png": (255, 0, 0, 255),
            "top/middle.png": (0, 255, 0, 255),
            "top/right.png": (255, 0, 0, 255),
            "middle/left.png": (0, 0, 255, 255),
            "middle/middle.png": (255, 255, 255, 255),
            "middle/right.png": (0, 0, 255, 255),
            "bottom/left.png": (255, 0, 0, 255),
            "bottom/middle.png": (0, 255, 0, 255),
            "bottom/right.png": (255, 0, 0, 255),
        }
        for piece, color in colors.items():
            files[(base + piece).replace("/", "\\")] = png_bytes(10, 6, color)
        self.assets = FakeAssets(files)
        self.widget = Widget({"sWidgetType": "CFrame", "sName": "f",
                              "sFileName": base, "iWidth": 200,
                              "iHeight": 60})

    def test_corner_kept_edge_stretched(self):
        image = render(self.widget, self.assets)
        self.assertEqual(pixel(image, 2, 2), (255, 0, 0, 255))       # 角 10×6
        self.assertEqual(pixel(image, 9, 2), (255, 0, 0, 255))
        self.assertEqual(pixel(image, 11, 2), (0, 255, 0, 255))      # 上边拉伸
        self.assertEqual(pixel(image, 100, 3), (0, 255, 0, 255))
        self.assertEqual(pixel(image, 2, 30), (0, 0, 255, 255))      # 左边拉伸
        self.assertEqual(pixel(image, 100, 30), (255, 255, 255, 255))  # 中心
        self.assertEqual(pixel(image, 197, 57), (255, 0, 0, 255))    # 右下角原位

    def test_corner_size_follows_resource_not_thirds(self):
        """角块 10px 宽：第 12 列已经是上边（拉伸区），不是 66px 处。"""
        image = render(self.widget, self.assets)
        self.assertEqual(pixel(image, 12, 2), (0, 255, 0, 255))
        self.assertNotEqual(pixel(image, 12, 2), (255, 0, 0, 255))

    def test_target_smaller_than_corners_does_not_overflow(self):
        small = Widget({"sWidgetType": "CFrame", "sName": "s",
                        "sFileName": "frame\\", "iWidth": 12, "iHeight": 8})
        image = render(small, self.assets, size=(12, 8))
        self.assertEqual(pixel(image, 11, 7)[3], 255)   # 右下角仍画到边
        self.assertEqual(pixel(image, 0, 0), (255, 0, 0, 255))

    def test_transparent_piece_is_skipped(self):
        base = "nine\\"
        files = {}
        for piece in ("top/left.png", "top/middle.png", "top/right.png",
                      "middle/left.png", "middle/middle.png",
                      "middle/right.png", "bottom/left.png",
                      "bottom/middle.png", "bottom/right.png"):
            files[(base + piece).replace("/", "\\")] = png_bytes(5, 5)
        files[(base + "middle/middle.png").replace("/", "\\")] = blank_png(5, 5)
        widget = Widget({"sWidgetType": "CFrame", "sName": "n",
                         "sFileName": base, "iWidth": 100, "iHeight": 50})
        image = render(widget, FakeAssets(files), size=(100, 50))
        self.assertEqual(pixel(image, 50, 25)[3], 0)   # 中心没铺白底

    def test_h_slice_draws_ends_and_stretch(self):
        files = {
            "h\\left1.png": png_bytes(8, 20, (255, 0, 0, 255)),
            "h\\middle.png": png_bytes(30, 20, (0, 255, 0, 255)),
            "h\\right2.png": png_bytes(12, 20, (0, 0, 255, 255)),
        }
        widget = Widget({"sWidgetType": "CHFrame", "sName": "h",
                         "sFileName": "h\\", "iWidth": 120, "iHeight": 24})
        image = render(widget, FakeAssets(files), size=(120, 24))
        self.assertEqual(pixel(image, 2, 10), (255, 0, 0, 255))
        self.assertEqual(pixel(image, 60, 10), (0, 255, 0, 255))
        self.assertEqual(pixel(image, 115, 10), (0, 0, 255, 255))


class TestRuntimeVisibility(_NeedsGui):
    def test_hidden_widget_differs_from_missing_resource(self):
        hidden = Widget({"sWidgetType": "CBitmapFrame", "sName": "h",
                         "sFileName": "gone.png", "iWidth": 60, "iHeight": 30,
                         "bShow": 0})
        missing = Widget({"sWidgetType": "CBitmapFrame", "sName": "m",
                          "sFileName": "gone.png", "iWidth": 60, "iHeight": 30})
        assets = FakeAssets({})
        a = render(hidden, assets, size=(60, 30))
        b = render(missing, assets, size=(60, 30))
        self.assertNotEqual([a.pixelColor(x, y).name() for x in range(0, 60, 6)
                             for y in range(0, 30, 6)],
                            [b.pixelColor(x, y).name() for x in range(0, 60, 6)
                             for y in range(0, 30, 6)])

    def test_hidden_keeps_bShow_label_and_does_not_become_placeholder(self):
        hidden = Widget({"sWidgetType": "CBitmapFrame", "sName": "h",
                         "sFileName": "bg.png", "iWidth": 80, "iHeight": 40,
                         "bShow": 0})
        assets = FakeAssets({"bg.png": png_bytes(80, 40, (0, 120, 255, 255))})
        image = render(hidden, assets, size=(80, 40))
        alpha = [image.pixelColor(x, 20).alpha() for x in (5, 20, 40)]
        self.assertTrue(all(0 < value < 255 for value in alpha))  # 压暗不是消失
        self.assertEqual(runtime_state.state_of(hidden), runtime_state.HIDDEN)


class TestCanvasBadge(_NeedsGui):

    def _window(self):
        from ui_editor.ui.main_window import MainWindow
        return MainWindow()

    def test_badge_only_for_non_native(self):
        from ui_editor.core import fidelity
        window = self._window()
        try:
            window.new_layout()
            doc = window.doc
            frame = doc.roots[0]
            approx = doc.new_widget("CPngNineFrame", parent=frame)
            approx.props["sFileName"] = "single.png"
            text_only = doc.new_widget("CTextFrame", parent=frame)
            window._refresh_structure()
            item = window.scene.item_for(approx)
            self.assertTrue(item.fidelity)      # 取不到资源 → 占位（模拟）
            self.assertNotEqual(item.fidelity[0].level, fidelity.NATIVE)
            self.assertEqual(window.scene.item_for(text_only).fidelity, [])
        finally:
            if window.doc is not None:
                window.doc.dirty = False
            window.close()
            window.deleteLater()
            self._app.processEvents()

    def test_fidelity_label_updates_on_selection(self):
        window = self._window()
        try:
            window.new_layout()
            doc = window.doc
            frame = doc.roots[0]
            widget = doc.new_widget("CTextFrame", parent=frame)
            window._refresh_structure()
            window._select_widget(widget)
            self.assertIn("无图片素材", window._fidelity_label.text())
        finally:
            if window.doc is not None:
                window.doc.dirty = False
            window.close()
            window.deleteLater()
            self._app.processEvents()

    def test_status_bar_labels_survive_busy_task(self):
        """常驻标签不能被忙碌遮罩/状态栏重建弄丢（曾整栏被替换销毁）。"""
        from shiboken6 import isValid
        window = self._window()
        try:
            window.run_busy("测试", lambda handle: None)
            self.assertTrue(isValid(window._fidelity_label))
            self.assertTrue(isValid(window._zoom_label))
            labels = [child for child in window.statusBar().children()
                      if type(child).__name__ == "QLabel"]
            self.assertGreaterEqual(len(labels), 2)
        finally:
            if window.doc is not None:
                window.doc.dirty = False
            window.close()
            window.deleteLater()
            self._app.processEvents()


class TestDiagnosticsVisibility(unittest.TestCase):
    def _doc(self, **props):
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        widget = doc.new_widget("CBitmapFrame", parent=frame)
        widget.props.update(props)
        return doc

    def test_hidden_and_missing_are_different_codes(self):
        doc = self._doc(sFileName="gone.png", bShow=0)
        found = diagnostics.diagnose(doc, resource_exists=lambda name: False)
        codes = [issue.code for issue in found]
        self.assertIn("RUNTIME_HIDDEN", codes)
        self.assertIn("RESOURCE_MISSING", codes)   # 两件事同时报，不合并

    def test_not_loaded_has_its_own_code(self):
        doc = self._doc(sFileName="a.png", bLoad=0)
        found = diagnostics.diagnose(doc, resource_exists=lambda name: True)
        codes = [issue.code for issue in found]
        self.assertIn("RUNTIME_NOT_LOADED", codes)
        self.assertNotIn("RESOURCE_MISSING", codes)

    def test_hidden_is_hint_not_warning(self):
        doc = self._doc(bShow=0)
        found = diagnostics.diagnose(doc)
        entry = next(i for i in found if i.code == "RUNTIME_HIDDEN")
        self.assertEqual(entry.severity, "提示")

    def test_single_image_nine_slice_marked_approx(self):
        doc = self._doc(sWidgetType="CPngNineFrame", sFileName="btn.png")
        found = diagnostics.diagnose(doc, resource_exists=lambda name: True)
        self.assertIn("RENDER_APPROX", [issue.code for issue in found])

    def test_style_skin_is_reported_as_style_not_missing(self):
        from ui_editor.core.styles import StyleBook
        book = StyleBook.parse_bytes(
            (Path(__file__).parent / "fixtures" / "ui_mini.lst").read_bytes())
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        button = doc.new_widget("CTextButton", parent=frame)
        button.props.update({"sName": "一级按钮",
                             "sFileName": "combdialog4\\三态按钮\\一级按钮\\",
                             "iStyle": 0, "sText": "确定"})
        found = diagnostics.diagnose(doc, styles=book,
                                     resource_exists=lambda name: False)
        codes = [issue.code for issue in found]
        self.assertIn("RENDER_STYLE_SKIN", codes)
        self.assertNotIn("RESOURCE_MISSING", codes)
        entry = next(i for i in found if i.code == "RENDER_STYLE_SKIN")
        self.assertEqual(entry.severity, "提示")
        self.assertIn("iStyle=0", entry.message)

    def test_image_backed_button_is_not_style_skin(self):
        from ui_editor.core.styles import StyleBook
        book = StyleBook.parse_bytes(
            (Path(__file__).parent / "fixtures" / "ui_mini.lst").read_bytes())
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        button = doc.new_widget("CTextButton", parent=frame)
        button.props.update({"sName": "b", "sFileName": "ui\\btn.png",
                             "iStyle": 0})
        found = diagnostics.diagnose(doc, styles=book,
                                     resource_exists=lambda name: True)
        self.assertNotIn("RENDER_STYLE_SKIN", [i.code for i in found])

    def test_sliced_dir_base_is_not_marked_approx(self):
        doc = self._doc(sWidgetType="CPngNineFrame", sFileName="nine\\")
        found = diagnostics.diagnose(doc, resource_exists=lambda name: True)
        self.assertNotIn("RENDER_APPROX", [issue.code for issue in found])




class TestDrawnSourceBadge(_NeedsGui):
    """角标必须跟着「实际怎么画的」走，不能只看 sFileName。

    用户实测：`combdialog4\\三态按钮\\一级按钮\\` 这种目录型基路径拼不出切片时，
    按钮按 ui.lst 的 iStyle 画出了皮肤（改 iStyle 颜色会变），角标却报占位。
    """

    def setUp(self):
        from ui_editor.core.styles import StyleBook
        self.book = StyleBook.parse_bytes(
            (Path(__file__).parent / "fixtures" / "ui_mini.lst").read_bytes())
        self.base = "combdialog4\\三态按钮\\一级按钮\\"

    def _ctx(self, assets, skins=None):
        ctx = PaintContext(assets=assets, styles=self.book)
        if skins:
            ctx.code_skins = skins
        return ctx

    def _widget(self, **props):
        data = {"sWidgetType": "CTextButton", "sName": "一级按钮",
                "sFileName": self.base, "iWidth": 60, "iHeight": 24,
                "sText": "确定"}
        data.update(props)
        return Widget(data)

    def _one(self, name):
        from ui_editor.core import fidelity
        from ui_editor.ui.canvas import FidelityView
        return fidelity.markers(self.widget_, FidelityView(self.ctx))

    def _render(self):
        image = QImage(60, 24, QImage.Format.Format_RGBA8888)
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image)
        try:
            painters.paint_widget(painter, self.widget_, self.ctx)
        finally:
            painter.end()
        return image

    def test_istyle_color_drawn_and_badge_says_style_not_placeholder(self):
        from ui_editor.core import fidelity
        from ui_editor.core.painters import resolve_source
        self.widget_ = self._widget(iStyle=0)
        self.ctx = self._ctx(FakeAssets({}))
        image = self._render()
        self.assertGreaterEqual(  # 浅黄占主体，说明走的是样式表皮肤
            color_share(image, (255, 255, 198)), 0.5)
        self.assertEqual(resolve_source(self.widget_, self.ctx),
                         "style_skin")
        found = self._one("x")
        self.assertEqual([m.code for m in found], ["style_skin"])
        self.assertEqual(found[0].level, fidelity.APPROX)

    def test_changing_istyle_changes_color_but_never_says_placeholder(self):
        colors, codes = [], []
        for index in (0, 1):
            self.widget_ = self._widget(iStyle=index)
            self.ctx = self._ctx(FakeAssets({}))
            colors.append(pixel(self._render(), 30, 12))
            codes.extend(m.code for m in self._one("x"))
        self.assertNotEqual(colors[0], colors[1])       # 颜色确实随 iStyle 变
        self.assertNotIn("missing_placeholder", codes)

    def test_plain_button_without_style_is_editor_default_not_placeholder(self):
        self.widget_ = self._widget(sWidgetType="CButton", iStyle=99,
                                    sFileName="")
        self.ctx = self._ctx(FakeAssets({}))
        found = self._one("x")
        self.assertEqual([m.code for m in found], ["button_style"])

    def test_progress_without_image_is_editor_default(self):
        self.widget_ = Widget({"sWidgetType": "CProgress", "sName": "p",
                               "sBgFileName": "ui\\bar.png",
                               "iWidth": 60, "iHeight": 24})
        self.ctx = self._ctx(FakeAssets({}))
        self.assertEqual([m.code for m in self._one("x")], ["editor_default"])

    def test_code_skin_badge_is_not_placeholder(self):
        from ui_editor.core.script_index import SkinRef
        skin = SkinRef("login", 1, "C", "f", "CreateBtn", "skins\\btn.png",
                       "开始", None)
        self.widget_ = self._widget(sWidgetType="CButton", iStyle=None,
                                    sFileName=self.base)
        self.ctx = self._ctx(
            FakeAssets({"skins\\btn.png": png_bytes(60, 24,
                                                     (255, 0, 0, 255))}),
            skins={"一级按钮": skin})
        self.assertGreaterEqual(
            color_share(self._render(), (255, 0, 0)), 0.5)
        found = self._one("x")
        self.assertEqual([m.code for m in found], ["code_skin"])
        self.assertIn("脚本现造", found[0].text)

    def test_true_missing_still_placeholder(self):
        self.widget_ = Widget({"sWidgetType": "CBitmapFrame", "sName": "m",
                               "sFileName": "gone.png",
                               "iWidth": 60, "iHeight": 24})
        self.ctx = self._ctx(FakeAssets({}))
        found = self._one("x")
        self.assertEqual([m.code for m in found], ["missing_placeholder"])

    def test_dir_base_missing_placeholder_mentions_slices(self):
        self.widget_ = self._widget(sWidgetType="CFrame", iStyle=None)
        self.ctx = self._ctx(FakeAssets({}))
        found = self._one("x")
        self.assertEqual(found[0].code, "missing_placeholder")
        self.assertIn("切片族", found[0].text)

    def test_text_button_dir_base_that_composes_uses_slices(self):
        """目录型基路径能拼出九片时，文字按钮也按切片画（不再整图拉伸）。"""
        files = {}
        for piece in ("top/left.png", "top/middle.png", "top/right.png",
                      "middle/left.png", "middle/middle.png", "middle/right.png",
                      "bottom/left.png", "bottom/middle.png", "bottom/right.png"):
            files[(self.base + piece).replace("/", "\\")] = png_bytes(
                5, 5, (0, 200, 255, 255))
        self.widget_ = self._widget()
        self.ctx = self._ctx(FakeAssets(files))
        image = self._render()
        self.assertGreaterEqual(
            color_share(image, (0, 200, 255)), 0.5)
        self.assertEqual([m.code for m in self._one("x")], ["native_nine_slice"])

    def test_text_button_state_slices_are_native_and_draw_state_zero(self):
        """三态按钮的 ``0l/0c/0r`` 是横三片：常态按切片画，且标「原生」。

        实测：``combdialog4\\三态按钮\\一级按钮\\`` 里是 0l/0c/0r … 2l/2c/2r，
        共 3 态、每态 3 块；老逻辑只认 ``0.png`` 连号，整族一条都画不出来。
        """
        files = {}
        for state, color in enumerate(((0, 200, 255, 255),
                                       (255, 160, 0, 255),
                                       (120, 120, 120, 255))):
            for side, width in (("l", 6), ("c", 20), ("r", 6)):
                name = f"{self.base}{state}{side}.png"
                files[name.replace("/", "\\")] = png_bytes(width, 24, color)
        self.widget_ = self._widget()
        self.ctx = self._ctx(FakeAssets(files))
        image = self._render()
        self.assertGreaterEqual(color_share(image, (0, 200, 255)), 0.5)
        self.assertEqual([m.code for m in self._one("x")], ["native_h_slice"])

    def test_three_state_images_stay_frames_not_placeholders(self):
        """``0/1/2.png`` 整图三态的按钮（CButton）画 0 号帧，不报占位。"""
        files = {}
        for state, color in enumerate(((0, 200, 255, 255),
                                       (255, 160, 0, 255),
                                       (120, 120, 120, 255))):
            files[(self.base + f"{state}.png").replace("/", "\\")] = png_bytes(
                60, 24, color)
        self.widget_ = self._widget(sWidgetType="CButton")
        self.ctx = self._ctx(FakeAssets(files))
        image = self._render()
        self.assertGreaterEqual(color_share(image, (0, 200, 255)), 0.5)
        codes = [m.code for m in self._one("x")]
        self.assertNotIn("missing_placeholder", codes)


if __name__ == "__main__":
    unittest.main()
