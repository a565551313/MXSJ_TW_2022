from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from test_gui import QT_ERROR

from script_editor.core.services.module_browser import ModuleReport
from script_editor.core.services.recovery_candidates import RecoveryCandidate
from script_editor.core.services.recovery_process import run_bounded

if not QT_ERROR:
    import sys

    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication, QPushButton

    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class CandidateGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.window = Window(self.root)
        self.report = ModuleReport(
            self.root / "source.fls",
            "a" * 64,
            0,
            "entry",
            "py25",
            b"module.py".hex(),
            "b" * 64,
            "first=1\n",
            True,
            "listing",
            (),
            "",
            (
                RecoveryCandidate("uncompyle6", "v", "complete", "first=1\n"),
                RecoveryCandidate(
                    "pycdc",
                    "v",
                    "partial",
                    "second=2\n",
                    ("partial",),
                    b"second=2\n",
                    b"first error\nsecond error",
                ),
            ),
        )

    def tearDown(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temporary.cleanup()

    def test_other_candidate_opens_fresh_tab_without_overwriting_dirty_edits(self):
        original = self.window.open_recovery_candidate(self.report)
        original.editor.insertPlainText("# user's modifications\n")
        before = original.editor.toPlainText()
        other = original.findChild(QPushButton, "openCandidate_pycdc")
        other.click()
        candidate = self.window.current()
        self.assertIsNot(candidate, original)
        self.assertEqual(self.window.tabs.count(), 2)
        self.assertEqual(original.editor.toPlainText(), before)
        self.assertTrue(original.editor.document().isModified())
        self.assertEqual(candidate.editor.toPlainText(), "second=2\n")
        self.assertFalse(candidate.recovery.complete)
        self.assertEqual(candidate.recovery.selected_engine, "pycdc")
        self.assertEqual(candidate.source_kind, "recovered-draft")
        self.assertFalse(candidate.editor.isReadOnly())

    def test_reopening_existing_candidate_preserves_its_edits(self):
        report = self.report.for_candidate(1)
        tab = self.window.open_recovery_candidate(report)
        tab.editor.insertPlainText("# more changes\n")
        before = tab.editor.toPlainText()
        again = self.window.open_recovery_candidate(report)
        self.assertIs(again, tab)
        self.assertEqual(again.editor.toPlainText(), before)
        self.assertEqual(self.window.tabs.count(), 1)

    def test_candidate_information_does_not_claim_semantic_or_syntax_verification(self):
        tab = self.window.open_recovery_candidate(self.report)
        info = tab.module_pages.widget(2).toPlainText()
        self.assertIn('"syntax_checked": false', info)
        self.assertIn('"semantics_verified": false', info)
        self.assertEqual(tab.module_pages.count(), 5)

    def test_cancel_button_stops_recovery_and_keeps_dirty_buffer(self):
        tab = self.window.add_source(self.root / "user.py", text="KEEP\n")
        tab.editor.document().setModified(True)
        cancel = threading.Event()
        completed = []
        self.window.task(
            lambda: run_bounded(
                [sys.executable, "-c", "import time;time.sleep(8)"], cancel=cancel
            ),
            completed.append,
            cancel=cancel,
        )
        buttons = self.window.statusBar().findChildren(QPushButton)
        next(b for b in buttons if b.text().startswith("取消恢复")).click()
        loop, timer = QEventLoop(), QTimer()
        timer.setInterval(10)
        timer.timeout.connect(lambda: None if self.window.jobs else loop.quit())
        timer.start()
        QTimer.singleShot(3000, loop.quit)
        loop.exec()
        timer.stop()
        self.assertFalse(self.window.jobs)
        self.assertFalse(completed)
        self.assertEqual(tab.editor.toPlainText(), "KEEP\n")
        self.assertTrue(tab.editor.document().isModified())
        self.assertIn("取消", self.window.statusBar().currentMessage())
