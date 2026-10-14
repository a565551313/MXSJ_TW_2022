"""单文档导入流程、待入包树节点及保存失败状态；Qt offscreen。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    from ui_editor.ui.layout_import_dialog import LayoutImportDialog
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

    def import_dlg(self, path="custom/new.dlg", *, accepted=True, confirm=True):
        dialog = mock.Mock(path=path)
        dialog.exec.return_value = QDialog.Accepted if accepted else QDialog.Rejected
        with (
            mock.patch(
                "ui_editor.ui.main_window.QFileDialog.getOpenFileName",
                return_value=(str(self.local), ""),
            ),
            mock.patch(
                "ui_editor.ui.main_window.LayoutImportDialog", return_value=dialog
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
        root = self.window.resource_panel._roots[("pack", str(self.src))]
        self.assertEqual(root.childCount(), 0)

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
        panel = self.window.resource_panel
        root = panel._roots[("pack", str(self.src))]
        seen = []
        panel.import_pack_layout.disconnect(self.window.import_pack_layout)
        panel.import_pack_layout.connect(seen.append)
        with (
            mock.patch.object(panel._tree, "itemAt", return_value=root),
            mock.patch("ui_editor.ui.panels.QMenu") as menu,
        ):
            panel._show_context_menu(QPoint())
            action = menu.return_value.addAction.return_value
            self.assertEqual(
                menu.return_value.addAction.call_args.args[0], "导入布局文件…"
            )
            action.triggered.connect.call_args.args[0]()
        self.assertEqual(seen, [str(self.src)])
        self.import_dlg()
        with (
            mock.patch.object(panel._tree, "itemAt", return_value=panel._pending_item),
            mock.patch("ui_editor.ui.panels.QMenu") as menu,
        ):
            panel._show_context_menu(QPoint())
            menu.assert_not_called()

    def test_path_combo_search_manual_and_validation(self):
        dialog = LayoutImportDialog("local.dlg", ["dialog/a.dlg", "login/b.dlg"])
        self.assertTrue(dialog.combo.isEditable())
        self.assertEqual(dialog.combo.completer().filterMode(), Qt.MatchContains)
        dialog.combo.setEditText("custom/new.dlg")
        dialog.accept()
        self.assertEqual(dialog.path, "custom/new.dlg")
        dialog.combo.setEditText("../bad.dlg")
        with mock.patch(
            "ui_editor.ui.layout_import_dialog.QMessageBox.warning"
        ) as warning:
            dialog.accept()
            warning.assert_called_once()
        dialog.deleteLater()

    def test_save_review_declares_layout_add(self):
        self.import_dlg()
        dialog = mock.Mock()
        dialog.exec.return_value = QDialog.Rejected
        with mock.patch(
            "ui_editor.ui.main_window.SaveReviewDialog", return_value=dialog
        ) as review:
            self.assertFalse(
                self.window._confirm_save_review(
                    str(self.root / "new.fls"), to_pack=True
                )
            )
        self.assertIn("新增 custom/new.dlg", review.call_args.kwargs["layout_notice"])
        self.assertTrue(self.window.doc.pending_pack_import)
