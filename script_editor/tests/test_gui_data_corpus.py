from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import data_fixture
from test_data_corpus import candidates
from test_gui import QT_ERROR

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.services.corpus_manifest import load_corpus
from script_editor.core.services.corpus_recovery import corpus_report
from script_editor.core.services.data_corpus import build_data_corpus

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class DataCorpusGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / "data.fls"
        self.path.write_bytes(data_fixture())
        self.window = Window(self.root)
        self.windows = [self.window]
        self.archive = ArchiveDocument(self.path)
        self.window.add_archive(self.archive)
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(1))
        self.output = self.root / "cache"

    def tearDown(self):
        for window in self.windows:
            for i in range(window.tabs.count()):
                window.tabs.widget(i).editor.document().setModified(False)
            window.project_dirty = False
            window.close()
            window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def build(self):
        with patch(
            "script_editor.core.services.data_corpus.recover_standard",
            return_value={"candidates": candidates()},
        ):
            return build_data_corpus(self.archive, self.output)[0]

    def test_data_generation_action_builds_and_associates_vm27_corpus(self):
        self.assertIn("data_corpus", self.window.ui_actions)
        with (
            patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(self.output), "")
            ),
            patch.object(
                self.window, "task", side_effect=lambda work, done, **kw: done(work())
            ),
            patch(
                "script_editor.core.services.pycdc_engine.discover_pycdc",
                return_value=None,
            ),
            patch(
                "script_editor.core.services.data_corpus.recover_standard",
                return_value={"candidates": candidates()},
            ),
        ):
            self.window.generate_data_corpus()
        self.assertEqual(len(self.window.corpus_refs), 1)
        self.assertEqual(self.window.corpus_refs[0].archive, self.path)
        self.assertIn("VM2.7", self.window.info.toPlainText())
        self.assertEqual(self.path.read_bytes(), data_fixture())

    def test_failed_generation_does_not_mask_live_recovery_with_empty_cache(self):
        with (
            patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(self.output), "")
            ),
            patch.object(
                self.window, "task", side_effect=lambda work, done, **kw: done(work())
            ),
            patch(
                "script_editor.core.services.pycdc_engine.discover_pycdc",
                return_value=None,
            ),
            patch(
                "script_editor.core.services.data_corpus.recover_standard",
                side_effect=ValueError("missing engine"),
            ),
        ):
            self.window.generate_data_corpus()
        self.assertFalse(self.window.corpus_refs)
        self.assertIn("未自动关联缓存", self.window.info.toPlainText())

    def test_data_manifest_import_is_not_blocked_by_script_only_guard(self):
        index = self.build()
        with (
            patch.object(
                QFileDialog, "getOpenFileName", return_value=(str(index.ref.path), "")
            ),
            patch.object(
                QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
            ),
            patch.object(
                self.window, "task", side_effect=lambda work, done, **kw: done(work())
            ),
        ):
            self.window.import_corpus()
        self.assertEqual(self.window.corpus_refs, [index.ref])

    def test_package_open_and_project_resume_preserve_vm27_edited_candidate(self):
        index = self.build()
        self.window.adopt_corpus(index)
        with patch.object(
            self.window, "task", side_effect=lambda work, done, **kw: done(work())
        ):
            self.window.open_package_module()
        tab = self.window.current()
        self.assertEqual(tab.source_kind, "recovered-draft")
        self.assertEqual(tab.vm.currentData(), "py27")
        tab.editor.insertPlainText("# KEEP DATA EDIT\n")
        text = tab.editor.toPlainText()
        project = self.root / "data-work.mxscript.json"
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(project), "")
        ):
            self.assertTrue(self.window.save_project())
        window = Window(self.root)
        self.windows.append(window)
        window.adopt_project(window.prepare_project(project))
        self.assertEqual(window.current().editor.toPlainText(), text)
        self.assertEqual(window.current().vm.currentData(), "py27")
        self.assertEqual(window.current().recovery.candidates[1].stdout, b"x='\xff'\n")
        self.assertEqual(window.corpus_refs, [index.ref])
        self.assertFalse(window.bindings)

    def test_data_xor_action_does_not_install_script_catalog(self):
        failures = []
        with patch.object(self.window, "fail", side_effect=failures.append):
            self.window.export_verified_catalog()
        self.assertEqual(len(failures), 1)
        self.assertIn("data无需五段参数", failures[0])
        self.assertFalse(self.window.catalogs)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
@unittest.skipUnless(
    os.environ.get("MXSJ_DATA_CORPUS"), "opt-in actual data corpus required"
)
class RealDataCorpusGuiTests(unittest.TestCase):
    def test_all_121_real_data_scripts_open_as_editable_vm27_tabs(self):
        app = QApplication.instance() or QApplication([])
        window = Window(Path(os.environ["MXSJ_M2_REPO"]) / "script_editor")
        archive = ArchiveDocument(Path(os.environ["MXSJ_M2_REPO"]) / "data/data.fls")
        window.add_archive(archive)
        index = load_corpus(
            archive,
            Path(os.environ["MXSJ_DATA_CORPUS"]) / "full/manifest.audited.jsonl",
        )
        window.adopt_corpus(index)
        opened = 0
        try:
            for entry in archive.entries:
                if entry.directory:
                    continue
                report = corpus_report(index, archive, entry.index)
                tab = window.open_recovery_candidate(report)
                with self.subTest(entry=entry.index):
                    self.assertTrue(tab.editor.toPlainText())
                    self.assertFalse(tab.editor.isReadOnly())
                    self.assertEqual(tab.editor.toPlainText(), report.source)
                    self.assertEqual(tab.vm.currentData(), "py27")
                    self.assertTrue(tab.recovery.origin_verified)
                opened += 1
                window.tabs.removeTab(window.tabs.indexOf(tab))
                tab.deleteLater()
                app.processEvents()
            self.assertEqual(opened, 121)
        finally:
            for i in range(window.tabs.count()):
                window.tabs.widget(i).editor.document().setModified(False)
            window.project_dirty = False
            window.close()
            window.deleteLater()
            app.processEvents()
