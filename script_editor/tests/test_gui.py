from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fixtures import data_bytes, script_bytes

QT_ERROR = ""
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QMessageBox

except ImportError as exc:
    QT_ERROR = str(exc)

if not QT_ERROR:
    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-gui-")
        self.root = Path(self.temp.name)
        self.window = Window(self.root)
        self.source = self.root / "test.py"
        self.source.write_text("x = 1\n", encoding="utf-8")

    def tearDown(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_startup_checks_both_vms_without_open_tab(self):
        def compiler(vm, root):
            return SimpleNamespace(
                vm=vm,
                version="2.5.6" if vm == "py25" else "2.7.13",
                bits=32,
                executable=root / vm / "python.exe",
            )

        with patch(
            "script_editor.gui.build_actions.bundled_compiler", side_effect=compiler
        ) as probe:
            with patch.object(
                self.window, "task", side_effect=lambda fn, done: done(fn())
            ):
                self.window.initialize_compilers()
        self.assertEqual(
            [call.args[0] for call in probe.call_args_list], ["py25", "py27"]
        )
        self.assertEqual(set(self.window.compilers), {"py25", "py27"})
        self.assertIn("2/2", self.window.statusBar().currentMessage())
        self.assertFalse(self.window.native_action.isEnabled())

    def test_failed_startup_clears_stale_compilers_but_keeps_source_available(self):
        self.window.compilers["py25"] = object()
        with patch(
            "script_editor.gui.build_actions.bundled_compiler",
            side_effect=ValueError("bad inventory"),
        ):
            with patch.object(
                self.window, "task", side_effect=lambda fn, done: done(fn())
            ):
                self.window.initialize_compilers()
        self.assertEqual(self.window.compilers, {})
        self.assertIn("bad inventory", self.window.info.toPlainText())
        self.window.add_source(self.source)
        self.assertFalse(self.window.current().editor.isReadOnly())

    def test_window_native_build_disabled(self):
        self.window.show()
        self.app.processEvents()
        actions = [
            a for menu in self.window.menuBar().actions() for a in menu.menu().actions()
        ]
        self.assertFalse(
            next(a for a in actions if "生成原生新包" in a.text()).isEnabled()
        )

    def test_dirty_source_close_cancel_and_save(self):
        self.window.add_source(self.source)
        tab = self.window.current()
        tab.editor.insertPlainText("# changed\n")
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel
        ):
            self.window.close_tab(0)
        self.assertEqual(self.window.tabs.count(), 1)
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Save
        ):
            self.window.close_tab(0)
        self.assertEqual(self.window.tabs.count(), 0)
        self.assertIn("# changed", self.source.read_text(encoding="utf-8"))

    def test_replace_all_is_one_undo_and_duplicate_tab_not_added(self):
        self.window.add_source(self.source)
        self.window.add_source(self.source)
        self.assertEqual(self.window.tabs.count(), 1)
        self.window.find.setText("x")
        self.window.replacement.setText("value")
        self.window.replace_all()
        self.assertIn("value", self.window.current().editor.toPlainText())
        self.window.current().editor.undo()
        self.assertEqual(self.window.current().editor.toPlainText(), "x = 1\n")

    def test_two_archives_have_separate_identity_and_vm(self):
        from script_editor.core.archives.document import ArchiveDocument

        for name, data in [("script.fls", script_bytes()), ("data.fls", data_bytes())]:
            path = self.root / name
            path.write_bytes(data)
            self.window.add_archive(ArchiveDocument(path))
        self.assertEqual(self.window.tree.topLevelItemCount(), 2)
        for i, vm in enumerate(("py25", "py27")):
            item = self.window.tree.topLevelItem(i).child(0)
            archive, _ = item.data(0, Qt.ItemDataRole.UserRole)
            self.assertEqual(archive.vm, vm)

    def test_reference_source_cannot_compile_save_or_associate(self):
        self.window.add_source(self.source, reference=True)
        self.assertTrue(self.window.current().editor.isReadOnly())
        with self.assertRaises(ValueError):
            self.window.editable()
        with self.assertRaises(ValueError):
            self.window.save_tab(self.window.current())
        self.window.find.setText("x")
        self.window.replacement.setText("changed")
        self.window.replace_all()
        self.assertEqual(self.window.current().editor.toPlainText(), "x = 1\n")

    def test_project_dirty_close_cancel(self):
        self.window.project_dirty = True
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel
        ):
            self.assertFalse(self.window.confirm_project())
