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
        if chosen is None or chosen.kind not in ("h_slice", "v_slice",
                                                 "nine_slice"):
            return None
        images = [self._load(piece) for piece in chosen.pieces]
        if any(image is None for image in images):
            return None
        flat = [image[0] for image in images if image is not None]
        blank = frozenset(i for i, image in enumerate(flat)
                          if image_is_blank(image))
        return SliceRecipe(chosen.kind, chosen.pieces, tuple(flat), blank)

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
        colors = {
            "top/left.png": (255, 0, 0, 255),
            "top.png": (0, 255, 0, 255),
            "top/right.png": (255, 0, 0, 255),
            "middle/left.png": (0, 0, 255, 255),
            "middle.png": (255, 255, 255, 255),
            "middle/right.png": (0, 0, 255, 255),
            "bottom/left.png": (255, 0, 0, 255),
            "bottom.png": (0, 255, 0, 255),
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
        for piece in ("top/left.png", "top.png", "top/right.png",
                      "middle/left.png", "middle/right.png",
                      "bottom/left.png", "bottom.png", "bottom/right.png"):
            files[(base + piece).replace("/", "\\")] = png_bytes(5, 5)
        files[(base + "middle.png").replace("/", "\\")] = blank_png(5, 5)
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

    def test_sliced_dir_base_is_not_marked_approx(self):
        doc = self._doc(sWidgetType="CPngNineFrame", sFileName="nine\\")
        found = diagnostics.diagnose(doc, resource_exists=lambda name: True)
        self.assertNotIn("RENDER_APPROX", [issue.code for issue in found])


if __name__ == "__main__":
    unittest.main()
