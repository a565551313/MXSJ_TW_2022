"""Qt tests are explicitly skipped if native libraries are unavailable."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
try:
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QToolBar

    from mxsj_web_server.app import create_manager
    from mxsj_web_server.gui.main_window import MainWindow

    QT_ERROR = ""
except (ImportError, OSError) as exc:
    QT_ERROR = str(exc)


@unittest.skipIf(bool(QT_ERROR), "Qt unavailable: " + QT_ERROR)
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.manager = create_manager(Path(self.tmp.name))
        self.window = MainWindow(self.manager)
        self.window.timer.stop()
        self.wait()

    def wait(self):
        for _ in range(200):
            QApplication.processEvents()
            if not self.window.busy:
                return
            QTest.qWait(10)
        self.fail("GUI worker did not finish")

    def tearDown(self):
        self.window.timer.stop()
        self.wait()
        self.manager.close()
        self.window.allow_close = True
        self.window.tray.hide()
        self.window.close()
        self.window.deleteLater()
        QApplication.processEvents()
        self.tmp.cleanup()

    def test_toolbar_order_and_separate_states(self):
        toolbar = self.window.findChild(QToolBar, "mainToolbar")
        names = [a.text() for a in toolbar.actions() if a.text()]
        self.assertEqual(
            names,
            [
                "启动",
                "暂停",
                "重启",
                "停止",
                "校验",
                "预览",
                "启动",
                "暂停",
                "重启",
                "停止",
                "帮助",
                "设置",
            ],
        )
        self.assertTrue(self.window.actions["public.start"].isEnabled())
        self.assertFalse(self.window.actions["public.stop"].isEnabled())
        self.assertTrue(self.window.actions["admin.start"].isEnabled())

    def test_initial_content_and_dirty_tracking(self):
        original = self.window.news.editor.toPlainText()
        self.assertTrue(original)
        self.assertFalse(self.window.dirty)
        self.window.news.editor.setPlainText("新的測試公告")
        self.assertTrue(self.window.dirty)
        self.window.save_content()
        self.wait()
        self.assertFalse(self.window.dirty)
        self.assertEqual(self.manager.snapshot()["draft"]["news"], "新的測試公告")

    def test_settings_and_local_core_boundary(self):
        data = {k: page.value() for k, page in self.window.policies.items()}
        self.assertEqual(data, self.manager.snapshot()["settings"])
        self.assertEqual(self.window.pages.count(), 7)
        self.assertFalse(self.window.allow_close)
