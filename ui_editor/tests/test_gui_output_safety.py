"""主窗口输出护栏：拒绝原包，失败不丢失文档关联与脏状态。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication

    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.errors import PackError
from ui_editor.core.model import LayoutDocument
from ui_editor.core.mxhash import mx_hash


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiOutputSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "source.fls"
        self.path = "login/test.dlg"
        plain = dlg_codec.dump_bytes([{"sName": "frame", "sWidgetType":
                                      "CMainFrame", "iWidth": 100}])
        self.raw = pack_build.build_archive([
            pack_build.RawEntry(mx_hash(self.path.encode()), 7, plain)])
        self.src.write_bytes(self.raw)
        self.window = MainWindow()
        self.addCleanup(self.cleanup_window)
        self.window.resolver.mount_pack(self.src)
        self.window.doc = LayoutDocument.from_dicts(*dlg_codec.parse_bytes(plain))
        self.window.doc.source_pack = (str(self.src), self.path)
        self.window.doc.dirty = True

    def cleanup_window(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_write_pack_rejects_hardlink_and_keeps_document(self):
        alias = self.root / "alias.fls"
        os.link(self.src, alias)
        with self.assertRaises(PackError):
            self.window.write_pack_copy(str(alias))
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertTrue(self.window.doc.dirty)
        self.assertEqual(self.window.doc.source_pack, (str(self.src), self.path))

    def test_save_as_cannot_write_layout_text_into_source_pack(self):
        with mock.patch("ui_editor.ui.main_window.QMessageBox.warning"):
            self.assertFalse(self.window.save_as(str(self.src)))
        self.assertEqual(self.src.read_bytes(), self.raw)
        self.assertTrue(self.window.doc.dirty)
        self.assertEqual(self.window.doc.source_pack, (str(self.src), self.path))

    def test_png_export_rejects_source_before_rendering(self):
        with mock.patch(
            "ui_editor.ui.workflows.QFileDialog.getSaveFileName",
            return_value=(str(self.src), ""),
        ), mock.patch("ui_editor.ui.main_window.QMessageBox.warning"), \
                mock.patch.object(self.window.view, "export_image") as render:
            self.window.export_png()
        render.assert_not_called()
        self.assertEqual(self.src.read_bytes(), self.raw)
