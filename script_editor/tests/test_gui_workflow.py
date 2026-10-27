from __future__ import annotations

import os
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from test_gui import QT_ERROR
from test_workflow import make_state

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import inspect_compiler
from script_editor.core.project.storage import ProjectState, save_state
from script_editor.core.services.workflow import Snapshot, prepare_build

if not QT_ERROR:
    from PySide6.QtCore import QEventLoop, QThread, QTimer
    from PySide6.QtWidgets import QApplication

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class GuiWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-m3-gui-")
        self.root = Path(self.temp.name)
        self.state = make_state(self.root)
        self.window = Window(self.root)

    def tearDown(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def install(self):
        binding = self.state.bindings[0]
        self.window.add_source(binding.source)
        self.window.add_archive(ArchiveDocument(binding.archive))
        self.window.bindings = list(self.state.bindings)
        self.window.catalogs = list(self.state.catalogs)
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(0))
        self.window.refresh_native_action()

    def plan(self):
        exe = os.environ.get("MXSJ_PY25")
        if not exe:
            self.skipTest("actual standard 2.5.6 required")
        self.install()
        compiler = inspect_compiler(Path(exe), "py25")
        self.window.register_compiler(compiler)
        tab = self.window.current()
        tab.editor.insertPlainText("# unsaved\nx=123\n")
        return prepare_build(
            Snapshot(
                self.state.bindings[0], tab.editor.toPlainText(), "py25", unsaved=True
            ),
            compiler,
            self.state.catalogs[0],
        )

    def test_write_actions_need_a_package_and_its_compiler(self):
        """F5/F6 gate on the package, not on a hand-made association.

        The old rule required a matching (selection, tab, VM) triple because
        "关联" was a manual step. It is automatic now: the actions are enabled
        when a package is selected and its VM had a compiler self-check pass.
        """
        self.install()
        self.assertFalse(self.window.write_action.isEnabled())
        self.assertFalse(self.window.generate_action.isEnabled())
        self.window.compilers["py25"] = object()
        self.window.refresh_native_action()
        self.assertTrue(self.window.write_action.isEnabled())
        self.assertTrue(self.window.generate_action.isEnabled())
        # Selecting a different VM's package does not inherit that compiler.
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(1))
        self.window.compilers.clear()
        self.window.refresh_native_action()
        self.assertFalse(self.window.write_action.isEnabled())

    def test_stale_preview_cannot_start_publish(self):
        plan = self.plan()
        self.window.current().editor.insertPlainText("# newer\n")
        with (
            patch.object(self.window, "task") as task,
            patch.object(self.window, "fail") as fail,
        ):
            self.window.publish_plan(plan, self.root / "never.fls")
        task.assert_not_called()
        fail.assert_called_once()
        self.assertFalse((self.root / "never.fls").exists())

    def test_success_adopts_exact_output_preserves_dirty_text_undo_and_baselines(self):
        plan = self.plan()
        tab = self.window.current()
        before = tab.editor.toPlainText()
        disk = tab.path.read_bytes()
        self.window.built_texts[(plan.snapshot.binding.archive, 1)] = "other baseline"
        result = self.window.publish_for_gui(plan, self.root / "new.fls", self.state)
        self.window.adopt_build(plan, result)
        self.assertEqual(self.window.bindings[0].archive, result[0].output)
        self.assertEqual(self.window.selected()[0].path, result[0].output)
        self.assertEqual(self.window.tree.topLevelItemCount(), 1)
        self.assertEqual(tab.editor.toPlainText(), before)
        self.assertTrue(tab.editor.document().isModified())
        self.assertTrue(tab.editor.document().isUndoAvailable())
        self.assertEqual(tab.path.read_bytes(), disk)
        self.assertEqual(
            self.window.built_texts[(result[0].output, 1)], "other baseline"
        )
        self.assertTrue(self.window.project_dirty)

    def test_already_published_but_ui_failure_is_not_reported_as_build_failure(self):
        plan = self.plan()
        result = self.window.publish_for_gui(plan, self.root / "new.fls", self.state)
        with patch.object(
            self.window, "add_archive", side_effect=ValueError("UI failure")
        ):
            self.window.adopt_build(plan, result)
        self.assertTrue(result[0].output.exists())
        self.assertEqual(self.window.bindings, list(self.state.bindings))
        self.assertIn("新包已成功生成", self.window.info.toPlainText())
        self.assertTrue(self.window.current().editor.document().isModified())

    def test_project_adoption_rolls_back_partial_widgets(self):
        self.window.add_source(self.state.bindings[0].source)
        old_tab = self.window.current()
        old_tab.editor.insertPlainText("# retain dirty undo\n")
        other = self.root / "other.py"
        other.write_text("x=9\n", encoding="utf-8")
        state = replace(
            self.state, bindings=(replace(self.state.bindings[0], source=other),)
        )
        project = self.root / "new.mxscript.json"
        save_state(project, state.bindings, state.catalogs)
        prepared = self.window.prepare_project(project)
        original = self.window.add_source

        def fail_after_add(*args, **kwargs):
            original(*args, **kwargs)
            raise ValueError("widget failure after add")

        with patch.object(self.window, "add_source", side_effect=fail_after_add):
            with self.assertRaises(ValueError):
                self.window.adopt_project(prepared)
        self.assertEqual(self.window.tabs.count(), 1)
        self.assertIs(self.window.current(), old_tab)
        self.assertEqual(self.window.tree.topLevelItemCount(), 0)
        self.assertEqual(self.window.archives, [])
        self.assertEqual(self.window.bindings, [])
        self.assertTrue(old_tab.editor.document().isModified())
        self.assertTrue(old_tab.editor.document().isUndoAvailable())

    def test_project_cross_vm_same_source_rejected_before_any_mutation(self):
        other = make_state(self.root, "py27")
        state = ProjectState(
            self.state.bindings
            + (replace(other.bindings[0], source=self.state.bindings[0].source),),
            self.state.catalogs,
        )
        project = self.root / "conflict.mxscript.json"
        save_state(project, state.bindings, state.catalogs)
        with self.assertRaises(ValueError):
            self.window.adopt_project(self.window.prepare_project(project))
        self.assertEqual(self.window.tabs.count(), 0)
        self.assertEqual(self.window.archives, [])
        self.assertEqual(self.window.bindings, [])

    def test_real_worker_callback_runs_on_gui_thread_and_restores_actions(self):
        loop = QEventLoop()
        main_ident = threading.get_ident()
        called = []
        release = threading.Event()

        def work():
            release.wait(2)
            return threading.get_ident()

        def complete(worker_ident):
            called.append(
                (worker_ident, threading.get_ident(), QThread.currentThread())
            )
            loop.quit()

        self.window.task(work, complete)
        self.assertFalse(self.window.centralWidget().isEnabled())
        self.assertTrue(
            all(
                not a.isEnabled()
                for a in self.window.findChildren(type(self.window.native_action))
            )
        )
        release.set()
        QTimer.singleShot(3000, loop.quit)
        loop.exec()
        self.assertTrue(called, "worker callback not delivered")
        self.assertNotEqual(called[0][0], main_ident)
        self.assertEqual(called[0][1], main_ident)
        self.assertEqual(called[0][2], self.app.thread())
        self.assertFalse(self.window.jobs)
        self.assertTrue(self.window.centralWidget().isEnabled())
