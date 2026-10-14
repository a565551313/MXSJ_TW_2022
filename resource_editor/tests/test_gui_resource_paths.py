"""可搜索/手填资源路径对话框与导入替换确认。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    from resource_editor.gui.main_window import MainWindow
    from resource_editor.gui.resource_path_dialog import ResourcePathDialog

    HAS_QT = True
except ImportError:
    HAS_QT = False

from resource_editor.core.containers import fls0slf
from resource_editor.core.model.document import PackDocument


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiResourcePaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.doc = PackDocument.from_bytes(
            fls0slf.build([b"unknown"], [fls0slf.EntryMeta(entry_id=100, r1=7)])
        )
        self.doc._names = {}
        self.doc.add_entry_for_path(b"OLD", "login/existing.bin")
        self.window = MainWindow()
        self.window._docs["synthetic"] = self.doc
        self.window._current_key = "synthetic"
        self.window._current = 1

    def tearDown(self):
        self.window._docs.clear()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.doc.archive.close()
        self.temp.cleanup()

    def test_editable_contains_case_insensitive_and_manual_path(self):
        dialog = ResourcePathDialog("local.bin", ["ui/a.bin", "login/b.bin"], "new.bin")
        self.assertTrue(dialog.combo.isEditable())
        self.assertEqual(dialog.combo.completer().filterMode(), Qt.MatchContains)
        self.assertEqual(dialog.combo.completer().caseSensitivity(), Qt.CaseInsensitive)
        dialog.combo.completer().setCompletionPrefix("GIN")
        self.assertEqual(dialog.combo.completer().completionCount(), 1)
        dialog.combo.setEditText("custom/new.bin")
        dialog.accept()
        self.assertEqual(dialog.path, "custom\\new.bin")
        dialog.deleteLater()

    def test_bad_path_warns_and_does_not_accept(self):
        dialog = ResourcePathDialog("local.bin", [], "../bad.bin")
        with mock.patch("resource_editor.gui.resource_path_dialog.QMessageBox.warning"):
            dialog.accept()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(dialog.path, "")
        dialog.deleteLater()

    def test_import_picker_uses_existing_names_and_cancel_safe(self):
        dialog = mock.Mock(path="")
        dialog.exec.return_value = QDialog.Rejected
        with mock.patch(
            "resource_editor.gui.main_window.ResourcePathDialog", return_value=dialog
        ) as picker:
            self.assertEqual(
                self.window._choose_resource_path("local.bin"), ("", False)
            )
        self.assertEqual(picker.call_args.args[1], ["login/existing.bin"])
        self.assertEqual(picker.call_args.args[2], "login/existing.bin")

    def test_replacement_no_keeps_bytes_and_history(self):
        local = self.root / "local.bin"
        local.write_bytes(b"NEW")
        history = list(self.doc.history.applied)
        with (
            mock.patch.object(
                self.window,
                "_choose_resource_path",
                return_value=("login/existing.bin", True),
            ),
            mock.patch(
                "resource_editor.gui.main_window.QMessageBox.question",
                return_value=QMessageBox.No,
            ) as question,
        ):
            self.window._import_files_by_path([str(local)])
        self.assertEqual(self.doc.content(1), b"OLD")
        self.assertEqual(self.doc.history.applied, history)
        self.assertEqual(question.call_args.args[-1], QMessageBox.No)
