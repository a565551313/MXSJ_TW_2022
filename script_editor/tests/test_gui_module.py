from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_module_browser as browser_tests
from test_gui import QT_ERROR
from test_workflow import make_state

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import inspect_compiler
from script_editor.core.project.storage import save_state
from script_editor.core.services.workflow import Snapshot, prepare_build

if not QT_ERROR:
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class GuiModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mx-recovery-gui-")
        self.root = Path(self.temp.name)
        self.window = Window(self.root)
        self.errors = []
        self.patcher = patch.object(self.window, "fail", self.errors.append)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def compiler(self, vm):
        executable = os.environ.get("MXSJ_" + vm.upper())
        if not executable:
            self.skipTest("actual standard compiler required: " + vm)
        return inspect_compiler(Path(executable), vm)

    def wait_jobs(self):
        loop, timer = QEventLoop(), QTimer()
        timer.setInterval(10)
        timer.timeout.connect(lambda: None if self.window.jobs else loop.quit())
        timer.start()
        QTimer.singleShot(10000, loop.quit)
        if self.window.jobs:
            loop.exec()
        timer.stop()
        self.assertFalse(self.window.jobs, "real worker timed out")
        self.assertFalse(self.errors, self.errors)

    def install(self, state):
        binding = state.bindings[0]
        self.window.add_archive(ArchiveDocument(binding.archive))
        self.window.catalogs.extend(state.catalogs)
        self.window.tree.setCurrentItem(
            self.window.tree.topLevelItem(
                self.window.tree.topLevelItemCount() - 1
            ).child(binding.index)
        )
        # Deliberately NO source files or bindings installed in the editor.

    def test_unbound_missing_catalog_opens_entry_tab_with_reason(self):
        self.install(make_state(self.root))
        self.window.catalogs = []
        self.window.open_associated()
        self.wait_jobs()
        tab = self.window.current()
        self.assertEqual(tab.source_kind, "module-unavailable")
        self.assertTrue(tab.editor.isReadOnly())
        self.assertEqual(tab.module_pages.count(), 3)
        self.assertIn("XOR", tab.module_pages.widget(2).toPlainText())
        self.assertFalse(self.window.bindings)
        self.assertFalse(self.window.native_action.isEnabled())
        self.assertFalse((self.root / "new.fls").exists())

    def test_both_vms_real_unbound_open_edit_review_publish_and_project_reopen(self):
        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                state, compiler, sentinel = (
                    browser_tests.ModuleBrowserTests.make_original(self, vm)
                )
                self.install(state)
                binding_count = len(self.window.bindings)
                self.window.register_compiler(compiler)
                self.window.open_associated()
                self.wait_jobs()
                tab = self.window.current()
                self.assertEqual(tab.source_kind, "recovered-draft")
                self.assertFalse(tab.editor.isReadOnly())
                self.assertEqual(len(self.window.bindings), binding_count)
                self.assertFalse(self.window.native_action.isEnabled())
                tab.editor.moveCursor(QTextCursor.MoveOperation.End)
                tab.editor.insertPlainText("\nGUI_RECOVERY_EDIT = 77\n")
                path = self.root / (vm + "-gui-recovered.py")
                with patch.object(
                    QFileDialog, "getSaveFileName", return_value=(str(path), "")
                ):
                    self.window.save_current()
                self.assertTrue(path.is_file())
                self.assertEqual(tab.source_kind, "recovered-draft")
                with patch.object(
                    QMessageBox, "question", return_value=QMessageBox.StandardButton.No
                ):
                    self.window.associate()
                    self.wait_jobs()
                self.assertEqual(tab.source_kind, "recovered-draft")
                self.assertEqual(len(self.window.bindings), binding_count)
                with patch.object(
                    QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
                ):
                    self.window.associate()
                    self.wait_jobs()
                self.assertEqual(tab.source_kind, "recovered-reviewed")
                self.assertTrue(self.window.native_action.isEnabled())
                binding = self.window.active_binding()
                self.assertEqual(binding.recovery_sha256, tab.recovery.standard_sha256)
                plan = prepare_build(
                    Snapshot(binding, tab.editor.toPlainText(), vm),
                    compiler,
                    self.window.catalog_for(self.window.selected()[0]),
                )
                destination = self.root / (vm + "-gui-new.fls")
                self.window.publish_plan(plan, destination)
                self.wait_jobs()
                self.assertTrue(destination.is_file())
                self.assertEqual(self.window.active_binding().archive, destination)
                self.assertFalse(sentinel.exists())
                project = self.root / (vm + "-gui.mxscript.json")
                save_state(project, self.window.bindings, self.window.catalogs)
                prepared = self.window.prepare_project(project)
                self.window.adopt_project(prepared)
                self.assertEqual(
                    self.window.current().source_kind, "recovered-reviewed"
                )
                self.assertIn("恢复源码", self.window.current().mode_label.text())
                self.assertFalse(self.window.current().editor.isReadOnly())

    def test_cancelling_first_save_keeps_recovery_dirty_and_untrusted(self):
        state, compiler, _ = browser_tests.ModuleBrowserTests.make_original(
            self, "py25"
        )
        self.install(state)
        self.window.register_compiler(compiler)
        self.window.open_associated()
        self.wait_jobs()
        tab = self.window.current()
        self.assertTrue(tab.editor.document().isModified())
        with patch.object(QFileDialog, "getSaveFileName", return_value=("", "")):
            self.window.adopt_recovery()
        self.assertEqual(tab.source_kind, "recovered-draft")
        self.assertTrue(tab.editor.document().isModified())
        self.assertFalse(self.window.bindings)
        self.assertFalse(tab.path.exists())

    def test_saved_recovery_file_reopens_as_editable_untrusted_correct_vm(self):
        path = self.root / "saved.py"
        path.write_text(
            "# coding: utf-8\n# MXSJ-RECOVERED-DRAFT\n# MXSJ-RECOVERY-VM: py27\nx=1\n",
            encoding="utf-8",
        )
        with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
            self.window.open_source()
        tab = self.window.current()
        self.assertEqual(tab.source_kind, "recovered-draft")
        self.assertEqual(tab.vm.currentData(), "py27")
        self.assertFalse(tab.editor.isReadOnly())
        self.assertFalse(self.window.bindings)
        self.assertFalse(self.window.native_action.isEnabled())
