"""替换布局：资源树右键、包内/散装两条落盘路径、拒绝与失败不改动目标。"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.mxhash import mx_hash


def layout(title: str, children: int = 0) -> list[dict]:
    kids = [
        {"sWidgetType": "CTextFrame", "sName": f"child{i}", "sText": title,
         "iX": 10 * i, "iY": 5, "iWidth": 40, "iHeight": 20}
        for i in range(children)
    ]
    return [{"sWidgetType": "CMainFrame", "sName": "root",
             "sTitle": title, "lChildren": kids}]


def raw_entry(name: str, data: bytes):
    entry_id = mx_hash(name.encode("gbk"))
    return pack_build.RawEntry(entry_id, pack_build.fresh_r1(entry_id), data)


class _NeedsGui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # 目标：散装 a.dlg（1 个控件）；来源：b.dlg（3 个控件）
        self.target = self.root / "a.dlg"
        self.target.write_bytes(dlg_codec.dump_bytes(layout("舊", 0)))
        self.source = self.root / "b.dlg"
        self.source.write_bytes(dlg_codec.dump_bytes(layout("新", 2)))
        # 目标：包内 dialog/a.dlg
        self.pack = self.root / "ui.fls"
        self.pack.write_bytes(pack_build.build_archive([
            raw_entry("dialog/a.dlg", dlg_codec.dump_bytes(layout("包舊", 0))),
            raw_entry("image/keep.bin", b"KEEP"),
        ]))
        self.pack_bytes = self.pack.read_bytes()
        self.window = MainWindow()

    def tearDown(self):
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
                session.doc.pending_pack_import = False
        if self.window.doc is not None:
            self.window.doc.dirty = False
            self.window.doc.pending_pack_import = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def open_loose(self):
        self.window.open_layout_file(str(self.target))
        self.window.doc.dirty = False
        return self.window.doc


class TestResourceMenu(_NeedsGui):
    def menu(self, data, *, missing=False, on_replace=None):
        from ui_editor.ui.resource_menu import build_resource_menu
        return build_resource_menu(
            self.window, data, missing=missing,
            on_export=mock.Mock(), on_import=mock.Mock(),
            on_open_path=mock.Mock(),
            on_replace=on_replace or mock.Mock())

    def texts(self, menu):
        return [a.text() for a in menu.actions() if a.text()]

    def test_loose_file_menu_has_replace(self):
        menu = self.menu(("file", str(self.target)))
        self.assertEqual(self.texts(menu), ["导出布局…", "替换布局…"])

    def test_pack_layout_menu_has_replace(self):
        menu = self.menu(("pack", str(self.pack), "dialog/a.dlg"))
        self.assertIn("替换布局…", self.texts(menu))

    def test_missing_layout_disables_replace(self):
        menu = self.menu(("pack", str(self.pack), "dialog/gone.dlg"),
                         missing=True)
        items = {a.text(): a for a in menu.actions() if a.text()}
        self.assertFalse(items["替换布局…"].isEnabled())
        self.assertFalse(items["导出布局…"].isEnabled())

    def test_packroot_menu_has_no_replace(self):
        menu = self.menu(("packroot", str(self.pack)))
        self.assertNotIn("替换布局…", self.texts(menu))

    def test_unknown_node_has_no_menu(self):
        self.assertIsNone(self.menu(("dirroot", str(self.root))))

    def test_trigger_hands_over_source_tuple(self):
        calls = []
        menu = self.menu(("file", str(self.target)), on_replace=calls.append)
        items = {a.text(): a for a in menu.actions() if a.text()}
        items["替换布局…"].trigger()
        self.assertEqual(calls, [("file", str(self.target))])

    def test_pack_trigger_hands_over_pack_tuple(self):
        calls = []
        data = ("pack", str(self.pack), "dialog/a.dlg")
        menu = self.menu(data, on_replace=calls.append)
        items = {a.text(): a for a in menu.actions() if a.text()}
        items["替换布局…"].trigger()
        self.assertEqual(calls, [data])


class TestReplaceLoose(_NeedsGui):
    def test_replace_loose_keeps_name_and_path(self):
        old = self.open_loose()
        self.assertTrue(self.window.replace_layout_with(
            ("file", str(self.target)), str(self.source)))
        doc = self.window.doc
        self.assertEqual(len(self.window._sessions), 1)
        self.assertEqual(doc.source_path, str(self.target))
        self.assertIsNone(doc.source_pack)
        self.assertEqual(len(doc.all_widgets()), 3)
        self.assertTrue(doc.dirty)
        self.assertFalse(doc.pending_pack_import)
        self.assertIsNot(doc, old)
        # 不动磁盘原文件：替换只是载入内存，保存才落盘
        self.assertEqual(
            dlg_codec.parse_bytes(self.target.read_bytes(),
                                  text_encoding="big5")[0],
            layout("舊", 0))

    def test_status_explains_how_to_persist(self):
        self.open_loose()
        self.window.replace_layout_with(("file", str(self.target)),
                                        str(self.source))
        message = self.window.statusBar().currentMessage()
        self.assertIn("替换", message)
        self.assertIn("保存", message)
        self.assertIn("a.dlg", message)

    def test_replace_opens_target_when_not_open(self):
        self.assertTrue(self.window.replace_layout_with(
            ("file", str(self.target)), str(self.source)))
        self.assertEqual(len(self.window._sessions), 1)
        self.assertEqual(self.window._sessions[0].key,
                         ("file", str(self.target)))
        self.assertEqual(len(self.window.doc.all_widgets()), 3)

    def test_refuse_replacing_with_itself(self):
        old = self.open_loose()
        with mock.patch("ui_editor.ui.replace_layout.QMessageBox.warning") as warn:
            self.assertFalse(self.window.replace_layout_with(
                ("file", str(self.target)), str(self.target)))
        warn.assert_called_once()
        self.assertIs(self.window.doc, old)
        self.assertFalse(old.dirty)

    def test_unparsable_source_keeps_target(self):
        old = self.open_loose()
        broken = self.root / "broken.dlg"
        broken.write_bytes(b"UI_INFO = [f()]")
        with mock.patch("ui_editor.ui.replace_layout.QMessageBox.warning") as warn:
            self.assertFalse(self.window.replace_layout_with(
                ("file", str(self.target)), str(broken)))
        warn.assert_called_once()
        self.assertIs(self.window.doc, old)
        self.assertEqual(len(old.all_widgets()), 1)

    def test_dirty_target_kept_when_user_says_no(self):
        old = self.open_loose()
        old.dirty = True
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=False):
            self.assertFalse(self.window.replace_layout_with(
                ("file", str(self.target)), str(self.source)))
        self.assertIs(self.window.doc, old)
        self.assertEqual(len(old.all_widgets()), 1)

    def test_dialog_asks_for_file_then_replaces(self):
        self.open_loose()
        with mock.patch(
                "ui_editor.ui.replace_layout.QFileDialog.getOpenFileName",
                return_value=(str(self.source), "")) as chooser:
            self.window.replace_layout_dialog(("file", str(self.target)))
        chooser.assert_called_once()
        self.assertEqual(len(self.window.doc.all_widgets()), 3)

    def test_dialog_cancel_changes_nothing(self):
        old = self.open_loose()
        with mock.patch(
                "ui_editor.ui.replace_layout.QFileDialog.getOpenFileName",
                return_value=("", "")):
            self.window.replace_layout_dialog(("file", str(self.target)))
        self.assertIs(self.window.doc, old)
        self.assertEqual(len(old.all_widgets()), 1)


class TestReplaceInPack(_NeedsGui):
    def test_replace_pack_layout_keeps_pack_path_and_untouched_source(self):
        data = ("pack", str(self.pack), "dialog/a.dlg")
        self.assertTrue(self.window.replace_layout_with(
            data, str(self.source)))
        doc = self.window.doc
        self.assertEqual(self.window._sessions[0].key, data)
        self.assertEqual(doc.source_pack, (str(self.pack), "dialog/a.dlg"))
        self.assertIsNone(doc.source_path)
        self.assertTrue(doc.pending_pack_import)
        self.assertTrue(doc.dirty)
        self.assertEqual(len(doc.all_widgets()), 3)
        self.assertEqual(self.pack.read_bytes(), self.pack_bytes)

    def test_replacement_shows_up_in_change_list(self):
        data = ("pack", str(self.pack), "dialog/a.dlg")
        self.window.replace_layout_with(data, str(self.source))
        changes = self.window.doc.changes()
        self.assertTrue(changes)
        messages = self.window.statusBar().currentMessage()
        self.assertIn("原包未修改", messages)
        self.assertIn("存包", messages)

    def test_invalid_source_rejected_and_pack_untouched(self):
        broken = self.root / "broken.dlg"
        broken.write_bytes(b"\x00\x01binary")
        data = ("pack", str(self.pack), "dialog/a.dlg")
        with mock.patch("ui_editor.ui.replace_layout.QMessageBox.warning") as warn:
            self.assertFalse(self.window.replace_layout_with(data, str(broken)))
        warn.assert_called_once()
        self.assertEqual(self.window._sessions, [])
        self.assertEqual(self.pack.read_bytes(), self.pack_bytes)

    def test_replace_second_time_updates_same_tab(self):
        data = ("pack", str(self.pack), "dialog/a.dlg")
        self.window.replace_layout_with(data, str(self.source))
        again = self.root / "c.dlg"
        again.write_bytes(dlg_codec.dump_bytes(layout("再換", 1)))
        # 第二次替换时同键标签已是「待入新包」，按流程要先确认丢弃
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True):
            self.assertTrue(self.window.replace_layout_with(data, str(again)))
        self.assertEqual(len(self.window._sessions), 1)
        self.assertEqual(len(self.window.doc.all_widgets()), 2)

    def test_second_replace_keeps_pending_marker(self):
        """替换已打开的包内布局后，资源树仍要显示「待入新包」叶子。"""
        data = ("pack", str(self.pack), "dialog/a.dlg")
        self.window.replace_layout_with(data, str(self.source))
        self.assertIsNotNone(self.window.resource_panel._pending_item)
        again = self.root / "c.dlg"
        again.write_bytes(dlg_codec.dump_bytes(layout("再換", 1)))
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True):
            self.assertTrue(self.window.replace_layout_with(data, str(again)))
        item = self.window.resource_panel._pending_item
        self.assertIsNotNone(item)
        self.assertIn("待入新包", item.text(0))
        self.assertTrue(self.window.doc.pending_pack_import)

    def test_second_replace_reveals_pending_leaf(self):
        data = ("pack", str(self.pack), "dialog/a.dlg")
        self.window.replace_layout_with(data, str(self.source))
        self.window._activate_session(0)
        self.window.resource_panel.clear_pending()
        self.assertIsNone(self.window.resource_panel._pending_item)
        again = self.root / "c.dlg"
        again.write_bytes(dlg_codec.dump_bytes(layout("再換", 1)))
        with mock.patch.object(self.window, "_confirm_discard",
                               return_value=True):
            self.window.replace_layout_with(data, str(again))
        item = self.window.resource_panel._pending_item
        self.assertIsNotNone(item)
        self.assertIs(self.window.resource_panel._tree.currentItem(), item)


if __name__ == "__main__":
    unittest.main()
