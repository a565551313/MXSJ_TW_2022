"""单文档导入流程、待入包树节点及保存失败状态；Qt offscreen。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    from ui_editor.ui.batch_import import BatchImportDialog
    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False

from test_layout_import import layout, raw

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.errors import PackError
from ui_editor.core.model import LayoutDocument


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.src = self.root / "source.fls"
        self.src.write_bytes(pack_build.build_archive([raw("image/a.bin", b"KEEP")]))
        self.original = self.src.read_bytes()
        self.local = self.root / "import.dlg"
        self.local.write_bytes(dlg_codec.dump_bytes(layout("New")))
        self.window = MainWindow()
        self.window.open_pack_file(str(self.src))
        self.window._set_document(LayoutDocument.from_dicts(layout("Editing"), None))
        self.old_doc = self.window.doc

    def tearDown(self):
        self.window.doc = None
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def import_dlg(self, path="custom/new.dlg", *, accepted=True, confirm=True,
                   entries=None):
        """走批量导入入口：对话框只回「用户选了哪些文件、各写哪个路径」。"""
        dialog = mock.Mock()
        dialog.exec.return_value = (QDialog.Accepted if accepted
                                    else QDialog.Rejected)
        dialog.entries.return_value = (
            [(self.local, path)] if entries is None else entries)
        with (
            mock.patch(
                "ui_editor.ui.import_queue.BatchImportDialog",
                return_value=dialog,
            ),
            mock.patch(
                "ui_editor.ui.main_window.QMessageBox.question",
                return_value=QMessageBox.Yes if confirm else QMessageBox.No,
            ),
            mock.patch("ui_editor.ui.main_window.QMessageBox.warning") as warning,
        ):
            self.window.import_pack_layout(str(self.src))
        return warning

    def test_new_pending_preview_and_no_original_write(self):
        self.import_dlg()
        doc = self.window.doc
        self.assertTrue(doc.pending_pack_import)
        self.assertTrue(doc.dirty)
        self.assertEqual(doc.source_pack, (str(self.src), "custom/new.dlg"))
        self.assertEqual(doc.to_dicts(), layout("New"))
        leaf = self.window.resource_panel._pending_item
        self.assertIn("待入新包", leaf.text(0))
        self.assertTrue(leaf.parent().isExpanded())
        with mock.patch.object(self.window, "_confirm_discard") as discard:
            self.window.resource_panel._on_double_click(leaf)
            discard.assert_not_called()
        self.assertIs(self.window.doc, doc)
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_cancel_address_and_cancel_unsaved_keep_old(self):
        self.import_dlg(accepted=False)
        self.assertIs(self.window.doc, self.old_doc)
        self.old_doc.dirty = True
        self.import_dlg(confirm=False)
        self.assertIs(self.window.doc, self.old_doc)
        self.assertIsNone(self.window.resource_panel._pending_item)

    def test_invalid_import_keeps_old_and_does_not_prompt_discard(self):
        self.local.write_bytes(b"UI_INFO = [__import__('os')]")
        warning = self.import_dlg()
        warning.assert_called_once()
        self.assertIs(self.window.doc, self.old_doc)
        self.assertIsNone(self.window.resource_panel._pending_item)

    def test_replacement_cancel_and_baseline(self):
        other = self.root / "other.fls"
        other.write_bytes(
            pack_build.build_archive(
                [raw("custom/old.dlg", dlg_codec.dump_bytes(layout()))]
            )
        )
        # Import targets this source, not a same-name layout in other packs.
        self.window.resolver.mount_pack(other)
        self.src.write_bytes(other.read_bytes())
        # 「替换」在批量对话框里已经确认过；这里取消的是「丢弃当前未保存改动」
        self.old_doc.dirty = True
        self.import_dlg("custom/old.dlg", confirm=False)
        self.assertIs(self.window.doc, self.old_doc)
        self.import_dlg("custom/old.dlg")
        self.assertTrue(any(c.field == "sTitle" for c in self.window.doc.changes()))
        out = self.root / "replace.fls"
        report = self.window.write_pack_copy(str(out))
        self.assertTrue(report["ok"])
        self.assertFalse(report["layout_added"])

    def test_save_failure_preserves_pending_doc_history_and_tree(self):
        self.import_dlg()
        doc = self.window.doc
        leaf = self.window.resource_panel._pending_item
        history = list(doc._history)
        with mock.patch.object(
            pack_build, "_verify_copy", side_effect=PackError("failed")
        ):
            with self.assertRaises(PackError):
                self.window.write_pack_copy(str(self.root / "failed.fls"))
        self.assertIs(self.window.doc, doc)
        self.assertTrue(doc.pending_pack_import)
        self.assertTrue(doc.dirty)
        self.assertEqual(doc._history, history)
        self.assertIs(self.window.resource_panel._pending_item, leaf)
        self.assertFalse((self.root / "failed.fls").exists())
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_save_mounts_new_pack_custom_name_reopens_and_single_pending_removed(self):
        self.import_dlg()
        out = self.root / "saved.fls"
        report = self.window.write_pack_copy(str(out))
        self.assertTrue(report["ok"])
        self.assertTrue(report["layout_added"])
        self.assertEqual(report["entries_after"], 2)
        self.assertFalse(self.window.doc.pending_pack_import)
        self.assertFalse(self.window.doc.dirty)
        self.assertIsNone(self.window.resource_panel._pending_item)
        self.assertIn("custom/new.dlg", self.window.resolver.scan_layouts(str(out)))
        self.window._open_pack_layout(str(out), "custom/new.dlg")
        self.assertEqual(self.window.doc.to_dicts(), layout("New"))
        self.assertEqual(self.src.read_bytes(), self.original)

    def test_discard_pending_clears_ghost_and_confirm_even_if_clean(self):
        self.import_dlg()
        self.window.doc.dirty = False  # undo/export cannot clear pending status
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question", return_value=QMessageBox.No
        ) as question:
            self.assertFalse(self.window._confirm_discard())
            question.assert_called_once()
        self.window._set_document(LayoutDocument.from_dicts(layout(), None))
        self.assertIsNone(self.window.resource_panel._pending_item)
        self.assertNotIn(("pack", str(self.src)), self.window.resource_panel._roots)

    def test_exact_pack_lookup_not_first_mounted_copy(self):
        first, second = self.root / "first.fls", self.root / "second.fls"
        for path, title in [(first, "First"), (second, "Second")]:
            path.write_bytes(
                pack_build.build_archive(
                    [raw("dialog/cateroom.dlg", dlg_codec.dump_bytes(layout(title)))]
                )
            )
            self.window.open_pack_file(str(path))
        self.window._open_pack_layout(str(second), "dialog/cateroom.dlg")
        self.assertEqual(self.window.doc.to_dicts(), layout("Second"))

    def test_context_menu_only_pack_root(self):
        self.import_dlg()  # 有待入包布局时显示包根；纯资源包默认不入树
        panel = self.window.resource_panel
        root = panel._roots[("pack", str(self.src))]
        seen = []
        panel.import_pack_layout.disconnect(self.window.import_pack_layout)
        panel.import_pack_layout.connect(seen.append)
        with (
            mock.patch.object(panel._tree, "itemAt", return_value=root),
            mock.patch("ui_editor.ui.resource_menu.QMenu") as menu,
        ):
            action = mock.Mock()
            menu.return_value.addAction.side_effect = [action, mock.Mock()]
            panel._show_context_menu(QPoint())
            self.assertEqual(
                menu.return_value.addAction.call_args_list[0].args[0],
                "把本地布局放进这个包…（可多选）",
            )
            action.triggered.connect.call_args.args[0]()
        self.assertEqual(seen, [str(self.src)])
        self.import_dlg()
        with (
            mock.patch.object(panel._tree, "itemAt", return_value=panel._pending_item),
            mock.patch("ui_editor.ui.resource_menu.QMenu") as menu,
        ):
            panel._show_context_menu(QPoint())
            menu.assert_not_called()

    def test_batch_dialog_paths_and_statuses(self):
        local_a = self.root / "a.dlg"
        local_b = self.root / "b.dlg"
        for path in (local_a, local_b):
            path.write_bytes(self.local.read_bytes())
        dialog = BatchImportDialog(
            str(self.src), ["custom/new.dlg", "login/old.dlg"])
        dialog.add_local_files([str(local_a), str(local_b), str(local_a)])
        self.assertEqual([row.path for row in dialog.rows],
                         ["a.dlg", "b.dlg"], "同一文件不重复排队")
        dialog.rows[0].path = "custom/new.dlg"   # 与包内已有布局同名
        dialog.rows[1].path = "topic/c.dlg"
        dialog._refresh()
        self.assertEqual([row.status for row in dialog.rows], ["新增", "新增"])
        self.assertEqual(dialog.compute_statuses(), ["替换", "新增"])
        dialog.rows[1].path = "custom/new.dlg"   # 两行同路径
        self.assertEqual(dialog.compute_statuses(), ["替换", "重复"])
        dialog.rows[1].path = "../逃出去.dlg"
        self.assertEqual(dialog.compute_statuses(), ["替换", "无效路径"])
        with mock.patch(
            "ui_editor.ui.batch_import.QMessageBox.warning"
        ) as warning:
            dialog.accept()
            warning.assert_called_once()
        dialog.rows[1].path = "topic/c.dlg"
        dialog._refresh()
        dialog.accept()
        self.assertEqual(dialog.entries(),
                         [(local_a, "custom/new.dlg"), (local_b, "topic/c.dlg")])
        dialog.deleteLater()


    def test_batch_dialog_normalizes_paths(self):
        """表格里看到的路径就是写进包的路径：去空格、反斜杠转 /。"""
        local = self.root / "n.dlg"
        local.write_bytes(self.local.read_bytes())
        dialog = BatchImportDialog(str(self.src), [])
        dialog.add_local_files([str(local)])
        dialog.rows[0].path = "  custom\\sub\\a.dlg  "
        dialog._refresh()
        self.assertEqual(dialog.rows[0].path, "custom/sub/a.dlg")
        self.assertEqual(dialog.compute_statuses(), ["新增"])
        self.assertEqual(dialog.entries(), [(local, "custom/sub/a.dlg")])
        dialog.deleteLater()

    def test_batch_dialog_keeps_folder_structure(self):
        folder = self.root / "ui_pack"
        (folder / "login").mkdir(parents=True)
        (folder / "login" / "regform.dlg").write_bytes(self.local.read_bytes())
        (folder / "main.dlg").write_bytes(self.local.read_bytes())
        dialog = BatchImportDialog(str(self.src), [])
        self.assertEqual(dialog.add_local_dir(folder), 2)
        self.assertEqual(sorted(row.path for row in dialog.rows),
                         ["login/regform.dlg", "main.dlg"])
        dialog.prefix_edit.setText("gameui/")
        dialog.apply_prefix()
        self.assertEqual(sorted(row.path for row in dialog.rows),
                         ["gameui/login/regform.dlg", "gameui/main.dlg"])
        dialog.deleteLater()

    def test_save_review_declares_layout_add(self):
        self.import_dlg()
        dialog = mock.Mock()
        dialog.exec.return_value = QDialog.Rejected
        with mock.patch(
            "ui_editor.ui.save_workflows.SaveReviewDialog", return_value=dialog
        ) as review:
            self.assertFalse(
                self.window._confirm_save_review(
                    str(self.root / "new.fls"), to_pack=True
                )
            )
        self.assertIn("新增 custom/new.dlg", review.call_args.kwargs["layout_notice"])
        self.assertTrue(self.window.doc.pending_pack_import)
