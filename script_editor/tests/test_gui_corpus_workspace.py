from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from corpus_fixtures import fixture
from test_gui import QT_ERROR

from script_editor.core.services.corpus_manifest import load_corpus
from script_editor.core.services.corpus_recovery import corpus_report

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication, QFileDialog

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class CorpusWorkspaceGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        archive, catalog, manifest, _ = fixture(self.root)
        self.window = Window(self.root)
        self.windows = [self.window]
        self.window.add_archive(archive)
        self.window.catalogs = [catalog]
        self.corpus = load_corpus(archive, manifest)
        self.window.adopt_corpus(self.corpus)
        self.report = corpus_report(self.corpus, archive, 0, catalog)
        self.tab = self.window.open_recovery_candidate(self.report)
        self.project = self.root / "work.mxscript.json"

    def tearDown(self):
        for window in self.windows:
            for i in range(window.tabs.count()):
                window.tabs.widget(i).editor.document().setModified(False)
            window.project_dirty = False
            window.close()
            window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def save(self):
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(self.project), "")
        ):
            self.assertTrue(self.window.save_project())

    def new_window(self):
        window = Window(self.root)
        self.windows.append(window)
        return window

    def test_project_restores_unsaved_text_candidates_diagnostics_and_vm(self):
        self.tab.editor.insertPlainText("# KEEP MY EDITS\n")
        text = self.tab.editor.toPlainText()
        self.save()
        self.assertFalse(self.tab.path.exists())
        window = self.new_window()
        window.adopt_project(window.prepare_project(self.project))
        tab = window.current()
        self.assertEqual(tab.editor.toPlainText(), text)
        self.assertEqual(tab.recovery, self.report)
        self.assertTrue(tab.editor.document().isModified())
        self.assertEqual(tab.vm.currentData(), "py25")
        self.assertFalse(tab.vm.isEnabled())
        self.assertEqual(tab.source_kind, "recovered-draft")
        self.assertFalse(window.bindings)
        self.assertEqual(tab.module_pages.count(), 5)
        self.assertEqual(window.corpus_refs, [self.corpus.ref])

    def test_reopen_project_keeps_existing_dirty_buffer_and_undo_history(self):
        self.save()
        self.tab.editor.insertPlainText("# NEWER UNSAVED TEXT\n")
        before = self.tab.editor.toPlainText()
        self.window.adopt_project(self.window.prepare_project(self.project))
        self.assertIs(self.window.current(), self.tab)
        self.assertEqual(self.tab.editor.toPlainText(), before)
        self.assertTrue(self.tab.editor.document().isUndoAvailable())
        self.assertTrue(self.window.project_dirty)

    def test_saving_project_is_enough_to_close_without_saving_py_files(self):
        self.tab.editor.insertPlainText("# project-only draft\n")
        self.save()
        with patch(
            "script_editor.gui.window.QMessageBox.question",
            side_effect=AssertionError("no prompt required"),
        ):
            self.assertTrue(self.window.confirm_tab(self.tab))
        self.assertTrue(self.tab.editor.document().isModified())
        self.assertFalse(self.tab.path.exists())

    def test_missing_corpus_does_not_discard_restored_edit_buffer(self):
        self.tab.editor.insertPlainText("# OFFLINE\n")
        self.save()
        self.corpus.ref.path.unlink()
        window = self.new_window()
        window.adopt_project(window.prepare_project(self.project))
        self.assertIn("# OFFLINE", window.current().editor.toPlainText())
        self.assertEqual(window.current().recovery.candidates[1].stdout, b"x='\xff'\n")

    def test_conflicting_snapshot_is_preflighted_without_adding_widgets(self):
        self.save()
        doc = json.loads(self.project.read_bytes())
        doc["editors"][0]["vm"] = "py27"
        self.project.write_text(json.dumps(doc), encoding="utf8")
        before = self.tab.editor.toPlainText()
        with self.assertRaises(ValueError):
            self.window.prepare_project(self.project)
        self.assertEqual(self.window.tabs.count(), 1)
        self.assertEqual(self.tab.editor.toPlainText(), before)

    def test_imported_candidate_does_not_replace_native_engine_tab(self):
        from dataclasses import replace

        native = self.window.open_recovery_candidate(
            replace(self.report, corpus_manifest_sha256="")
        )
        native.editor.insertPlainText("# Native edit\n")
        before = native.editor.toPlainText()
        corpus = self.window.open_recovery_candidate(self.report)
        self.assertIsNot(corpus, native)
        self.assertEqual(native.editor.toPlainText(), before)
        self.assertEqual(self.window.tabs.count(), 2)

    def test_corpus_actions_are_real_menu_entries(self):
        for key in ("import_corpus", "corpus_entry", "verified_keys"):
            self.assertIn(key, self.window.ui_actions)
            self.assertTrue(self.window.ui_actions[key].isEnabled())

    def test_candidate_reopen_after_save_as_preserves_renamed_dirty_buffer(self):
        renamed = self.root / "my-draft.py"
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(renamed), "")
        ):
            self.assertTrue(self.window.save_draft(self.tab))
        self.tab.editor.insertPlainText("# MORE CHANGES\n")
        before = self.tab.editor.toPlainText()
        tab = self.window.open_recovery_candidate(self.report)
        self.assertIs(tab, self.tab)
        self.assertEqual(tab.path, renamed)
        self.assertEqual(tab.editor.toPlainText(), before)
        self.assertEqual(self.window.tabs.count(), 1)

    def test_verify_catalog_action_writes_new_file_and_leaves_original_untouched(self):
        directory = self.root / "repair"
        directory.mkdir()
        archive, catalog, manifest, _ = fixture(directory, repair=True)
        before = catalog.path.read_bytes()
        self.window.add_archive(archive)
        self.window.catalogs.append(catalog)
        self.window.adopt_corpus(load_corpus(archive, manifest))
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(1).child(0))
        output = self.root / "verified.json"
        with (
            patch.object(
                self.window, "task", side_effect=lambda work, done: done(work())
            ),
            patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(output), "")
            ),
        ):
            self.window.export_verified_catalog()
        self.assertTrue(output.is_file())
        self.assertEqual(catalog.path.read_bytes(), before)
        ref = self.window.catalog_for(archive)
        self.assertEqual(ref.path, output)
        from script_editor.core.inspection.native import inspect_module

        self.assertTrue(inspect_module(archive, 0, ref)[0])
        self.assertTrue(self.window.project_dirty)

    def test_unverified_external_pyc_cannot_reach_native_prepare(self):
        from dataclasses import replace
        from types import SimpleNamespace

        self.tab.recovery = replace(
            self.report, candidate_pyc_sha256="0" * 64, origin_verified=False
        )
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(0))
        self.window.compilers["py25"] = SimpleNamespace(vm="py25")
        failed = []
        with (
            patch.object(
                self.window, "task", side_effect=lambda work, done: done(work())
            ),
            patch.object(
                self.window, "fail", side_effect=lambda exc: failed.append(str(exc))
            ),
            patch.object(
                QFileDialog,
                "getSaveFileName",
                return_value=(str(self.root / "draft.py"), ""),
            ),
            patch(
                "script_editor.gui.module_actions.prepare_build",
                side_effect=AssertionError("must not publish"),
            ),
        ):
            self.window.adopt_recovery()
            self.tab.recovery = replace(
                self.report, candidate_pyc_sha256="", origin_verified=False
            )
            self.window.adopt_recovery()
        self.assertEqual(len(failed), 2)
        self.assertIn("外部语料pyc与原包严格来源不同", failed[0])
        self.assertFalse(self.window.bindings)
        self.assertEqual(self.tab.source_kind, "recovered-draft")

    def test_draft_save_as_cannot_write_into_corpus_directory(self):
        target = self.corpus.root / "new-draft.py"
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(target), "")
        ):
            with self.assertRaisesRegex(ValueError, "语料目录只读"):
                self.window.save_draft(self.tab)
        self.assertFalse(target.exists())
        self.assertTrue(self.tab.editor.document().isModified())

    def test_authored_snapshot_can_reopen_with_source_file_missing(self):
        from script_editor.core.project.document import Binding

        source = self.root / "authored.py"
        source.write_text("disk = 1\n", encoding="utf8")
        tab = self.window.add_source(source, "py25", source_kind="authored")
        self.window.bindings.append(
            Binding.associate(self.window.archives[0], 0, source)
        )
        tab.editor.insertPlainText("# embedded only\n")
        expected = tab.editor.toPlainText()
        self.save()
        source.unlink()
        window = self.new_window()
        window.adopt_project(window.prepare_project(self.project))
        opened = next(
            window.tabs.widget(i)
            for i in range(window.tabs.count())
            if window.tabs.widget(i).path == source
        )
        self.assertEqual(opened.editor.toPlainText(), expected)
        self.assertEqual(opened.source_kind, "authored")
        self.assertFalse(source.exists())
