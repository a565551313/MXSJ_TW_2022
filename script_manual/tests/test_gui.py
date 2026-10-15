from __future__ import annotations

import os
import time
from unittest import skipIf
from unittest.mock import patch

from support import Fixture

try:
    from PySide6.QtCore import QUrl
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QMessageBox

    from mxsj_manual.gui.window import ManualWindow
except ImportError:
    if os.environ.get("MXSJ_MANUAL_REQUIRE_GUI") == "1":
        raise
    ManualWindow = None


@skipIf(ManualWindow is None, "PySide6/系统Qt库缺失；GUI未执行，不计通过")
class GuiTests(Fixture):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        super().setUp()
        self.window = ManualWindow(self.root)
        self.window.show()
        self.wait_idle()
        self.addCleanup(self.close_window)

    def close_window(self):
        self.wait_idle()
        self.window.close()
        self.app.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 10
        while self.window.jobs and time.monotonic() < deadline:
            QTest.qWait(10)
        self.assertFalse(self.window.jobs, "GUI后台任务未完成")
        self.app.processEvents()

    def search(self, text):
        self.window.query.setText(text)
        QTest.qWait(200)
        self.assertEqual(self.window.model.rowCount(), 1)

    def test_path_first_list_and_coverage(self):
        self.assertEqual(self.window.model.rowCount(), 20)
        self.assertEqual(self.window.model.HEADERS[0], "包内路径")
        self.assertIn("20/5135", self.window.coverage.text())

    def test_search_chinese_and_function_and_path(self):
        for query in ("公告", "refreshbulletin", "login/mainpage"):
            with self.subTest(query=query):
                self.search(query)
                self.assertEqual(self.window.selected["entry_index"], 337)

    def test_tabs_show_functions_branches_resources_evidence(self):
        self.search("公告")
        overview, functions, resources, evidence = [
            b.toPlainText() for b in self.window.browsers
        ]
        self.assertIn("原包对应未验证", overview)
        self.assertIn("msgid == 30", functions)
        self.assertIn("news.txt", resources)
        self.assertIn("SHA256", evidence)
        self.assertIn("待审核", overview)

    def test_unknown_module_does_not_fake_explanation(self):
        self.search("script/main.py")
        self.assertIn("尚未解释", self.window.browsers[0].toPlainText())

    def test_filters_and_empty_state(self):
        index = self.window.domain.findData("network")
        self.window.domain.setCurrentIndex(index)
        self.assertEqual(self.window.model.rowCount(), 4)
        self.window.query.setText("公告")
        QTest.qWait(200)
        self.assertEqual(self.window.model.rowCount(), 0)
        self.assertIsNone(self.window.selected)
        self.assertIn("目录不完整", self.window.browsers[0].toPlainText())

    def test_internal_module_link_navigates_by_identity(self):
        self.search("公告")
        sha = self.window.selected["archive_sha256"]
        self.window.follow_link(QUrl(f"#module={sha}%3A4007"))
        self.assertEqual(self.window.selected["entry_index"], 4007)
        self.assertEqual(self.window.tabs.currentIndex(), 0)

    def test_invalid_content_load_retains_previous_root_and_catalog(self):
        previous = self.window.catalog
        root = self.window.root
        with patch.object(
            QMessageBox, "exec", return_value=QMessageBox.StandardButton.Ok
        ):
            self.window.load(root=self.repo / "missing")
            self.wait_idle()
        self.assertIs(self.window.catalog, previous)
        self.assertEqual(self.window.root, root)
        self.assertTrue(all(action.isEnabled() for action in self.window.actions))

    def test_close_waits_for_background_jobs_without_orphan_threads(self):
        self.window.load(repository=self.repo)
        self.window.close()
        self.assertTrue(self.window.closing)
        self.wait_idle()
        self.assertFalse(self.window.isVisible())
        self.assertEqual(self.window.pool.activeThreadCount(), 0)

    def test_readonly_evidence_check_does_not_approve(self):
        self.window.load(repository=self.repo)
        self.wait_idle()
        self.search("公告")
        self.assertEqual(
            self.window.selected["evidence_status"], "verified_bytes_and_lines"
        )
        self.assertEqual(self.window.catalog.coverage()["accepted"], 0)

    def test_menu_reload_does_not_pass_boolean_as_repository(self):
        self.window.actions[1].trigger()
        self.wait_idle()
        self.assertIsNotNone(self.window.catalog)
        self.assertFalse(self.window.jobs)

    def test_reading_area_receives_vertical_space_not_banner(self):
        self.assertLess(self.window.coverage.height(), 120)
        self.assertGreater(self.window.table.height(), self.window.height() / 2)
