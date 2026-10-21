"""GUI：画布右键「导出素材」（原格式 / 转成图片）。"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 16


def dangling_link(test, path, target):
    """建一个悬空符号链接；系统不允许时跳过该用例（Windows 默认无权限）。"""
    try:
        path.symlink_to(target)
    except (OSError, NotImplementedError):
        test.skipTest("当前系统不允许创建符号链接")


class TestCanvasExportAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self._tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self._tmp.name)
        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(x=0, y=0, width=400, height=300)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _widget(self, wtype="CButton", **props):
        widget = self.doc.new_widget(wtype, parent=self.frame)
        widget.props.update(props)
        self.window._refresh_structure()
        return widget

    def _fake_resolver(self, files):
        resolver = mock.Mock()
        resolver.pack_paths = []
        resolver.fetch_bytes.side_effect = (
            lambda name: files.get(name.replace("/", "\\")))
        return resolver

    def _menu_titles(self, menu):
        return [action.text() for action in menu.actions()]

    def test_menu_has_export_entry_with_submenu(self):
        widget = self._widget(sFileName="a\\btn.png")
        self.window._select_widget(widget)
        menu = self.window.build_canvas_context_menu(widget)
        titles = self._menu_titles(menu)
        self.assertIn("导出素材", titles)
        submenu = next(a.menu() for a in menu.actions()
                       if a.text() == "导出素材")
        subs = self._menu_titles(submenu)
        self.assertTrue(any("按原格式" in text for text in subs))
        self.assertTrue(any("转成图片" in text for text in subs))

    def test_widget_without_assets_shows_disabled_hint(self):
        widget = self._widget("CTextFrame")
        menu = self.window.build_canvas_context_menu(widget)
        submenu = next(a.menu() for a in menu.actions()
                       if a.text() == "导出素材")
        actions = submenu.actions()
        self.assertEqual(len(actions), 1)
        self.assertIn("没有图片或音效素材", actions[0].text())
        self.assertFalse(actions[0].isEnabled())

    def test_export_raw_writes_original_format(self):
        widget = self._widget(sFileName="img\\btn.png")
        self.window.resolver = self._fake_resolver({"img\\btn.png": JPG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([widget])
        written = sorted(p.name for p in self.dest.iterdir())
        self.assertEqual(written, ["btn.jpg"])       # 内容其实是 JPG
        self.assertEqual((self.dest / "btn.jpg").read_bytes(), JPG)
        self.assertIn("已导出", self.window.statusBar().currentMessage())

    def test_export_multiple_fields(self):
        widget = self._widget(sFileName="a\\btn.png",
                              sBgFileName="b\\bg.png")
        self.window.resolver = self._fake_resolver({
            "a\\btn.png": PNG, "b\\bg.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([widget])
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["bg.png", "btn.png"])

    def test_export_missing_resource_reports(self):
        widget = self._widget(sFileName="gone.png")
        self.window.resolver = self._fake_resolver({})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([widget])
        self.assertEqual(list(self.dest.iterdir()), [])
        self.assertIn("没有可导出的素材",
                      self.window.statusBar().currentMessage())

    def test_cancelled_directory_does_nothing(self):
        widget = self._widget(sFileName="a.png")
        self.window.resolver = self._fake_resolver({"a.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=""):
            self.window.export_widget_assets([widget])
        self.assertEqual(list(self.dest.iterdir()), [])

    def _resolver_with_frames(self, files):
        resolver = self._fake_resolver(files)
        resolver.fetch_image.return_value = None
        return resolver

    def test_convert_same_basename_does_not_overwrite(self):
        png_a = PNG + b"A"
        png_b = PNG + b"B"
        w1 = self._widget(sFileName="a\\btn.png")
        w2 = self._widget(sFileName="b\\btn.png")
        self.window.resolver = self._resolver_with_frames({
            "a\\btn.png": png_a, "b\\btn.png": png_b})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([w1, w2], convert=True)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["btn-2.png", "btn.png"])
        self.assertEqual((self.dest / "btn.png").read_bytes(), png_a)
        self.assertEqual((self.dest / "btn-2.png").read_bytes(), png_b)
        self.assertIn("已导出", self.window.statusBar().currentMessage())

    def test_convert_shared_asset_exported_once(self):
        w1 = self._widget(sFileName="img\\bg.png")
        w2 = self._widget("CButton", sFileName="img\\bg.png")
        self.window.resolver = self._resolver_with_frames({
            "img\\bg.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([w1, w2], convert=True)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["bg.png"])

    def test_raw_shared_asset_exported_once(self):
        w1 = self._widget(sFileName="img\\bg.png")
        w2 = self._widget("CButton", sFileName="img\\bg.png")
        self.window.resolver = self._fake_resolver({"img\\bg.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([w1, w2])
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["bg.png"])

    def test_rejected_target_reported_without_losing_the_rest(self):
        # 导出目录里预存悬空符号链接：第一个控件被拒，第二个照常导出。
        dangling_link(self, self.dest / "btn.png", self.dest / "missing")
        w1 = self._widget(sFileName="a\\btn.png")
        w2 = self._widget("CButton", sFileName="ok\\keep.png")
        self.window.resolver = self._fake_resolver({
            "a\\btn.png": PNG, "ok\\keep.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([w1, w2])
        self.assertTrue((self.dest / "keep.png").exists())
        message = self.window.statusBar().currentMessage()
        self.assertIn("已导出", message)
        self.assertIn("被拒绝", message)
        self.assertIn("btn.png", message)

    def test_all_rejected_reports_reason(self):
        dangling_link(self, self.dest / "btn.png", self.dest / "missing")
        widget = self._widget(sFileName="a\\btn.png")
        self.window.resolver = self._fake_resolver({"a\\btn.png": PNG})
        with mock.patch.object(self.window, "_asset_export_dir",
                               return_value=str(self.dest)):
            self.window.export_widget_assets([widget])
        message = self.window.statusBar().currentMessage()
        self.assertIn("被拒绝", message)
        self.assertIn("符号链接", message)


if __name__ == "__main__":
    unittest.main()
