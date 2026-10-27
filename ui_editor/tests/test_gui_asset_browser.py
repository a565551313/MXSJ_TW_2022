"""GUI：工具栏「资源」按钮与浏览模式选图窗（0.17.0 功能 1）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPushButton


class TestAssetBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self.window.new_layout()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def test_toolbar_button_style(self):
        action = self.window._act_assets
        self.assertEqual(action.iconText(), "资源")
        self.assertIn("浏览资源", action.toolTip())
        self.assertFalse(action.icon().isNull())
        texts = [a.iconText() for a in self.window._toolbar.actions()
                 if a.text()]
        self.assertIn("资源", texts)

    def test_no_pack_gives_hint_not_dialog(self):
        self.window.browse_resources()
        self.assertIn("还没挂载资源包",
                      self.window.statusBar().currentMessage())

    def test_browse_only_dialog_shape(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        dialog = ResourcePickerDialog(
            self.window, "浏览资源", ["a.png", "b.png"],
            on_stage=lambda path, data: None,
            export_handler=lambda paths, host=None: None,
            browse_only=True)
        self.addCleanup(dialog.deleteLater)
        box = dialog.findChild(QDialogButtonBox)
        self.assertIsNotNone(box)
        self.assertTrue(
            box.button(QDialogButtonBox.StandardButton.Close) is not None)
        self.assertTrue(
            box.button(QDialogButtonBox.StandardButton.Ok) is None)
        # 资源级操作保留：导出副本 / 把图片放进包 / 拼名族
        labels = [b.text() for b in dialog.findChildren(QPushButton)]
        self.assertIn("导出副本…", labels)
        self.assertIn("把图片放进包…", labels)
        self.assertIn("几张图组成按钮（拼名族）…", labels)
        # 浏览模式没有「只填包外文件名」（那是写属性路径的入口）
        self.assertNotIn("只填包外文件名…", labels)

    def test_browse_mode_without_stage_hides_external(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        dialog = ResourcePickerDialog(
            self.window, "浏览资源", ["a.png"], browse_only=True)
        self.addCleanup(dialog.deleteLater)
        labels = [b.text() for b in dialog.findChildren(QPushButton)]
        self.assertNotIn("只填包外文件名…", labels)
        self.assertNotIn("把图片放进包…", labels)

    def test_normal_mode_unchanged(self):
        from ui_editor.ui.image_picker import ResourcePickerDialog

        dialog = ResourcePickerDialog(
            self.window, "从包里选图片", ["a.png"], on_stage=None)
        self.addCleanup(dialog.deleteLater)
        box = dialog.findChild(QDialogButtonBox)
        self.assertTrue(
            box.button(QDialogButtonBox.StandardButton.Ok) is not None)
        labels = [b.text() for b in dialog.findChildren(QPushButton)]
        self.assertIn("只填包外文件名…", labels)

    def test_build_browser_dialog_with_stub_assets(self):
        from ui_editor.ui.asset_browser import build_browser_dialog

        class StubAssets:
            _packs = ["x.fls"]
            pack_paths = []

            def fetch_image(self, path):
                return None

            def family_plan(self, path):
                return None

            def family_pieces(self, path):
                return ()

            def resource_exists(self, name):
                return False

            def stage_image(self, path, data):
                pass

            def fetch_bytes(self, name):
                return None

        dialog = build_browser_dialog(self.window, StubAssets(),
                                      ["gameui/a.png"])
        self.addCleanup(dialog.deleteLater)
        self.assertIsInstance(dialog, QDialog)
        self.assertTrue(dialog._browse_only)
        self.assertIn("浏览资源", dialog.windowTitle())


if __name__ == "__main__":
    unittest.main()
