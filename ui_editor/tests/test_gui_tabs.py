"""GUI 冒烟：多标签打开/切换/关闭（offscreen）。

锁住 0.9.0 语义：双击/打开=新标签；同来源重开=切回旧标签且不丢
未保存编辑；新建=新标签；关闭标签先确认；标签带未保存星标。
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _write_dlg(path: Path, name: str) -> None:
    from ui_editor.core import dlg_codec

    path.write_bytes(dlg_codec.dump_bytes(
        [{"sWidgetType": "CMainFrame", "sName": name, "lChildren": []}],
        md5="0" * 32))


class TestLayoutTabs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.window = MainWindow()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        _write_dlg(self.root / "a.dlg", "alpha")
        _write_dlg(self.root / "b.dlg", "beta")

    def tearDown(self):
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def test_open_two_layouts_keeps_both_tabs(self):
        self.window.open_layout_file(str(self.root / "a.dlg"))
        self.window.open_layout_file(str(self.root / "b.dlg"))
        self.assertEqual(len(self.window._sessions), 2)
        self.assertEqual(self.window._tab_bar.count(), 2)
        self.assertEqual(self.window.doc.display_name, "b.dlg")
        self.window._tab_bar.setCurrentIndex(0)
        self.assertIs(self.window.doc, self.window._sessions[0].doc)
        self.assertEqual(self.window.doc.display_name, "a.dlg")

    def test_reopen_switches_to_existing_tab_and_keeps_edits(self):
        self.window.open_layout_file(str(self.root / "a.dlg"))
        first = self.window.doc
        first.dirty = True
        self.window.open_layout_file(str(self.root / "a.dlg"))
        self.assertEqual(len(self.window._sessions), 1)
        self.assertIs(self.window.doc, first)
        self.assertTrue(self.window.doc.dirty)

    def test_new_layout_opens_new_tabs(self):
        self.window.new_layout()
        self.window.new_layout()
        self.assertEqual(len(self.window._sessions), 2)
        self.assertIs(self.window.doc, self.window._sessions[1].doc)

    def test_tab_switch_and_dirty_star(self):
        self.window.open_layout_file(str(self.root / "a.dlg"))
        self.window.open_layout_file(str(self.root / "b.dlg"))
        self.window.doc.dirty = True
        self.window._update_title()
        self.assertIn("*", self.window._tab_bar.tabText(1))
        self.assertNotIn("*", self.window._tab_bar.tabText(0))
        self.window._tab_bar.setCurrentIndex(0)
        self.assertIs(self.window.doc, self.window._sessions[0].doc)

    def test_close_tab_confirms_and_removes(self):
        self.window.open_layout_file(str(self.root / "a.dlg"))
        self.window.doc.dirty = True
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True) as asked:
            self.window._close_tab(0)
        asked.assert_called_once()
        self.assertEqual(len(self.window._sessions), 0)
        self.assertIsNone(self.window.doc)
        self.assertEqual(self.window._tab_bar.count(), 0)

    def test_close_tab_cancel_keeps_session(self):
        self.window.open_layout_file(str(self.root / "a.dlg"))
        self.window.doc.dirty = True
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=False):
            self.window._close_tab(0)
        self.assertEqual(len(self.window._sessions), 1)
        self.assertIsNotNone(self.window.doc)

    def test_close_last_tab_returns_empty_state(self):
        self.window.new_layout()
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True):
            self.window._close_tab(0)
        self.assertIsNone(self.window.doc)
        self.assertEqual(self.window._tab_bar.count(), 0)
        self.assertEqual(self.window.tree_panel._items, {})


if __name__ == "__main__":
    unittest.main()
