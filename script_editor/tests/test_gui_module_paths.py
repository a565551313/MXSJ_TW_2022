from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import data_fixture, script_fixture
from test_gui import QT_ERROR

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.project.storage import CatalogRef, save_state

if not QT_ERROR:
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication, QFileDialog

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ModulePathGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.window = Window(self.root)
        self.errors = []
        self.fail_patch = patch.object(self.window, "fail", self.errors.append)
        self.fail_patch.start()
        self.addCleanup(self.fail_patch.stop)
        payload, rows = script_fixture(
            two_modules=True, filename=b"script\\login\\register.py"
        )
        self.package = self.root / "script.fls"
        self.package.write_bytes(payload)
        self.fingerprint = hashlib.sha256(payload).hexdigest()
        folder = self.root / "decoding"
        folder.mkdir()
        self.catalog = folder / "script-original.json"
        self.catalog.write_text(json.dumps(rows), encoding="utf-8")
        self.digest = hashlib.sha256(self.catalog.read_bytes()).hexdigest()

    def tearDown(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def wait(self):
        loop, timer = QEventLoop(), QTimer()
        timer.setInterval(10)
        timer.timeout.connect(lambda: None if self.window.jobs else loop.quit())
        timer.start()
        QTimer.singleShot(10000, loop.quit)
        if self.window.jobs:
            loop.exec()
        timer.stop()
        self.assertFalse(self.window.jobs)
        self.assertFalse(self.errors, self.errors)

    def open_archive(self):
        with (
            patch(
                "script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS",
                {self.fingerprint: (self.catalog.name, self.digest)},
            ),
            patch.object(
                QFileDialog, "getOpenFileName", return_value=(str(self.package), "")
            ),
        ):
            self.window.open_archive()
            self.wait()
        return self.window.tree.topLevelItem(0)

    def test_open_shows_paths_before_any_double_click_no_binding_or_source(self):
        root = self.open_archive()
        self.assertEqual(root.child(0).text(0), "script/login/register.py")
        self.assertEqual(root.child(1).text(0), "script/login/register.py")
        self.assertNotIn("b'", root.child(0).text(0))
        self.assertNotIn("ID", root.child(0).text(0))
        self.assertIn("ID 00000064", root.child(0).toolTip(0))
        self.assertIn("路径未读取", root.child(2).text(0))
        self.assertEqual(self.window.tabs.count(), 0)
        self.assertFalse(self.window.bindings)
        self.window.filter.setText("LOGIN/register")
        self.assertFalse(root.child(0).isHidden())
        self.assertTrue(root.child(2).isHidden())
        self.window.tree.setCurrentItem(root.child(1))
        self.assertEqual(self.window.selected()[1], 1)
        self.window.filter.setText("script\\login")
        self.assertFalse(root.child(1).isHidden())
        self.window.filter.setText("#1")
        self.assertTrue(root.child(0).isHidden())
        self.assertFalse(root.child(1).isHidden())
        self.window.filter.setText("00000064")
        self.assertFalse(root.child(0).isHidden())
        self.assertTrue(root.child(1).isHidden())

    def test_project_reopen_also_indexes_paths_without_touching_dirty_buffer(self):
        project = self.root / "sample.mxscript.json"
        save_state(
            project,
            (),
            (
                CatalogRef(
                    self.package.resolve(),
                    self.fingerprint,
                    self.catalog,
                    self.digest,
                ),
            ),
        )
        tab = self.window.add_source(self.root / "mine.py", text="keep = 1\n")
        tab.editor.insertPlainText("# edits\n")
        text = tab.editor.toPlainText()
        self.window.task(
            lambda: self.window.prepare_project(project), self.window.adopt_project
        )
        self.wait()
        self.assertEqual(
            self.window.tree.topLevelItem(0).child(0).text(0),
            "script/login/register.py",
        )
        self.assertEqual(tab.editor.toPlainText(), text)
        self.assertTrue(tab.editor.document().isUndoAvailable())
        self.assertFalse(self.window.bindings)

    def test_data_paths_still_come_from_directory_and_keep_pyo_suffix(self):
        path = self.root / "data.fls"
        path.write_bytes(data_fixture())
        self.window.add_archive(ArchiveDocument(path))
        root = self.window.tree.topLevelItem(0)
        self.assertEqual(root.child(1).text(0), "lib/sample.pyo")
        self.assertFalse(self.window.module_names)

    def test_manual_catalog_confirmation_reindexes_existing_unknown_package(self):
        from PySide6.QtWidgets import QMessageBox

        with (
            patch("script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS", {}),
            patch.object(
                QFileDialog, "getOpenFileName", return_value=(str(self.package), "")
            ),
        ):
            self.window.open_archive()
            self.wait()
        root = self.window.tree.topLevelItem(0)
        self.assertIn("路径未读取", root.child(0).text(0))
        self.window.tree.setCurrentItem(root)
        with (
            patch.object(
                QFileDialog, "getOpenFileName", return_value=(str(self.catalog), "")
            ),
            patch.object(
                QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
            ),
        ):
            self.window.configure_catalog()
            self.wait()
        self.assertEqual(root.child(0).text(0), "script/login/register.py")
        self.assertFalse(self.window.bindings)

    def test_declining_catalog_never_publishes_scanned_names(self):
        from PySide6.QtWidgets import QMessageBox

        self.window.add_archive(ArchiveDocument(self.package))
        root = self.window.tree.topLevelItem(0)
        self.window.tree.setCurrentItem(root)
        with (
            patch.object(
                QFileDialog, "getOpenFileName", return_value=(str(self.catalog), "")
            ),
            patch.object(
                QMessageBox, "question", return_value=QMessageBox.StandardButton.No
            ),
        ):
            self.window.configure_catalog()
            self.wait()
        self.assertIn("路径未读取", root.child(0).text(0))
        self.assertFalse(self.window.module_names)
        self.assertFalse(self.window.catalogs)
        self.assertFalse(self.window.archives[0].module_paths)
