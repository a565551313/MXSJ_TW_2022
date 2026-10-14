"""真实窗口时间线、批量一步、保存取消与旧解码回调护栏（合成包）。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox

    from resource_editor.gui.main_window import MainWindow
    from resource_editor.gui.save_review import SaveReviewDialog
    from resource_editor.gui.workers import Job

    HAS_QT = True
except ImportError:
    HAS_QT = False

from resource_editor.core.containers import fls0slf, flsdata
from resource_editor.core.model.document import PackDocument


def snapshot(doc):
    return [
        (meta.entry_id if doc.kind == "0slf" else meta.name, doc.content(i))
        for i, meta in enumerate(doc.archive.extra_metas)
    ]


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.fls"
        self.original = fls0slf.build(
            [b"A", b"B"], [fls0slf.EntryMeta(entry_id=i + 100, r1=7) for i in range(2)]
        )
        self.source.write_bytes(self.original)
        self.window = MainWindow()
        self.sync = mock.patch.object(self.window, "_register_job", self.run_job_sync)
        self.sync.start()
        self.window.set_workspace(self.root)
        with mock.patch.object(self.window, "_run_job", self.run_job_sync):
            self.window.open_pack(str(self.source))

    @staticmethod
    def run_job_sync(job, done, *args, **kwargs):
        done(job._fn(lambda *progress: None))

    def tearDown(self):
        self.sync.stop()
        self.window._busy = False
        with mock.patch(
            "resource_editor.gui.main_window.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ):
            self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_global_actions_work_without_selection(self):
        w, doc = self.window, self.window._doc
        doc.add_entry(b"new")
        w._current = -1
        w._update_actions()
        self.assertTrue(w._act_undo.isEnabled())
        self.assertFalse(w._act_redo.isEnabled())
        w._apply_history(False)
        self.assertEqual(doc.count, 2)
        self.assertTrue(w._act_redo.isEnabled())
        self.assertIn("待重做", w._history_list.item(0).text())
        w._apply_history(True)
        self.assertEqual(doc.count, 3)
        self.assertFalse(w._act_redo.isEnabled())
        self.assertEqual(w._grid._kinds, [doc.entry_kind(i) for i in range(doc.count)])

    def test_selection_follows_identity_after_index_shift(self):
        w, doc = self.window, self.window._doc
        doc.delete_entry(0)
        w._reload_grid(select=0)  # 原条目 B 移到下标 0
        w._apply_history(False)
        self.assertEqual(w._current, 1)
        self.assertEqual(doc.content(w._current), b"B")
        w._apply_history(True)
        self.assertEqual(w._current, 0)
        self.assertEqual(doc.content(w._current), b"B")

    def test_batch_path_import_mixes_replace_and_add_in_one_step(self):
        w, doc = self.window, self.window._doc
        doc.add_entry_for_path(b"old", "same/old.bin")
        before = snapshot(doc)
        first, second = self.root / "first.bin", self.root / "second.bin"
        first.write_bytes(b"replacement")
        second.write_bytes(b"addition")
        with (
            mock.patch(
                "resource_editor.gui.main_window.MainWindow._choose_resource_path",
                side_effect=[("same/old.bin", True), ("same/new.bin", True)],
            ),
            mock.patch(
                "resource_editor.gui.main_window.QMessageBox.question",
                return_value=QMessageBox.Yes,
            ),
        ):
            w._import_files_by_path([str(first), str(second)])
        self.assertEqual(len(doc.history.applied), 2)
        self.assertEqual(doc.history.undo_label, "按路径批量导入")
        w._apply_history(False)
        self.assertEqual(snapshot(doc), before)
        w._apply_history(True)
        self.assertEqual(doc.content(doc.index_by_path("same/new.bin")), b"addition")

    def test_batch_partial_read_failure_keeps_successes_as_one_step(self):
        w, doc = self.window, self.window._doc
        first = self.root / "first.bin"
        first.write_bytes(b"new")
        with mock.patch(
            "resource_editor.gui.main_window.MainWindow._choose_resource_path",
            side_effect=[("new/first.bin", True), ("new/missing.bin", True)],
        ):
            w._import_files_by_path([str(first), str(self.root / "missing.bin")])
        self.assertEqual(len(doc.history.applied), 1)
        self.assertEqual(doc.count, 3)
        w._apply_history(False)
        self.assertEqual(doc.count, 2)

    def test_data_multi_import_is_one_step(self):
        w = self.window
        archive = flsdata.FlsDataArchive(
            header=b"FLS\0" + bytes(60),
            payloads=[],
            metas=[flsdata.EntryMeta(name="old")],
        )
        doc = PackDocument.from_bytes(flsdata.build(archive, [flsdata.deflate(b"old")]))
        w._docs["synthetic-data"] = doc
        w._kinds_map["synthetic-data"] = [doc.entry_kind(0)]
        w._activate_pack("synthetic-data")
        first, second = self.root / "one", self.root / "two"
        first.write_bytes(b"one")
        second.write_bytes(b"two")
        with (
            mock.patch(
                "resource_editor.gui.main_window.QFileDialog.getOpenFileNames",
                return_value=([str(first), str(second)], ""),
            ),
            mock.patch(
                "resource_editor.gui.main_window.QInputDialog.getText",
                side_effect=[("one", True), ("two", True)],
            ),
        ):
            w.import_entries_multi()
        self.assertEqual(len(doc.history.applied), 1)
        w._apply_history(False)
        self.assertEqual(snapshot(doc), [("old", b"old")])
        w._apply_history(True)
        self.assertEqual(doc.count, 3)

    def test_cancel_save_does_not_write_or_reset_history(self):
        w, doc = self.window, self.window._doc
        doc.replace_content(0, b"edit")
        target = self.root / "new.fls"
        changes = doc.changes()
        with (
            mock.patch(
                "resource_editor.gui.main_window.QFileDialog.getSaveFileName",
                return_value=(str(target), ""),
            ),
            mock.patch(
                "resource_editor.gui.main_window.SaveReviewDialog.exec", return_value=0
            ),
            mock.patch("resource_editor.gui.main_window.save_document") as saver,
        ):
            w.save_file(False)
        saver.assert_not_called()
        self.assertFalse(target.exists())
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertTrue(doc.can_undo)
        self.assertEqual(doc.changes(), changes)
        self.assertEqual(doc.path, self.source)

    def test_review_lists_real_delta_and_sizes(self):
        doc = self.window._doc
        doc.replace_content(0, b"edit")
        doc.delete_entry(1)
        doc.add_entry(b"new")
        dialog = SaveReviewDialog(doc.changes(), self.root / "new.fls", self.window)
        self.assertEqual(dialog.table.topLevelItemCount(), 3)
        row = dialog.table.topLevelItem(0)
        self.assertEqual([row.text(i) for i in (0, 3, 4)], ["修改", "1", "4"])
        dialog.deleteLater()

    def test_background_finish_cannot_unlock_blocking_save(self):
        w = self.window
        blocking, background = object(), object()
        w._busy, w._blocking_job = True, blocking
        w._job_callbacks[background] = (lambda _r: None, lambda _e: None)
        with mock.patch.object(w, "sender", return_value=background):
            w._dispatch_finished(None)
        self.assertTrue(w._busy)
        self.assertFalse(w._act_undo.isEnabled())
        self.assertFalse(w._act_save.isEnabled())
        w._job_callbacks[blocking] = (lambda _r: None, lambda _e: None)
        with mock.patch.object(w, "sender", return_value=blocking):
            w._dispatch_finished(None)
        self.assertFalse(w._busy)
        self.assertTrue(w._act_save.isEnabled())

    def test_stale_thumbnail_and_sprite_callbacks_are_discarded(self):
        w = self.window
        pending = []

        def capture(job, done, *args, **kwargs):
            pending.append((job, done))

        with mock.patch.object(w, "_register_job", capture):
            w._thumb_cache.clear()
            w._ensure_page_thumbnails()
            thumbnail_callback = pending[-1][1]
            w._show_sprite(0)
            sprite_callback = pending[-1][1]
            w._preview_epoch += 1  # 与结构重建/撤销一致的过期状态
            with (
                mock.patch.object(w, "_on_thumbnails") as thumbs,
                mock.patch.object(w, "_on_sprite_decoded") as sprite,
            ):
                thumbnail_callback({0: object()})
                sprite_callback(object())
            thumbs.assert_not_called()
            sprite.assert_not_called()

    def test_blocking_start_disables_history_and_error_restores_it(self):
        w = self.window
        w._doc.add_entry(b"new")
        job = Job(lambda _p: None, "synthetic save")
        with mock.patch.object(w, "_register_job"):
            w._run_job(job, lambda _r: None)
        self.assertFalse(w._act_undo.isEnabled())
        w._job_callbacks[job.signals] = (None, lambda _e: None)
        with mock.patch.object(w, "sender", return_value=job.signals):
            w._dispatch_error("synthetic failure")
        self.assertTrue(w._act_undo.isEnabled())
        self.assertTrue(w._doc.can_undo)

    def test_empty_pack_clears_preview_but_can_undo(self):
        w, doc = self.window, self.window._doc
        with doc.edit_group("delete all"):
            while doc.count:
                doc.delete_entry(0)
        w._reload_grid()
        self.assertEqual(w._current, -1)
        self.assertIsNone(w._sprite)
        self.assertTrue(w._act_undo.isEnabled())
        self.assertFalse(w._act_delete.isEnabled())
        self.assertEqual(w._text_preview.toPlainText(), "")
        w._apply_history(False)
        self.assertEqual(doc.count, 2)
        self.assertEqual(w._current, 0)

    def test_history_is_per_pack_and_switch_updates_actions(self):
        w = self.window
        first_key, first = w._current_key, w._doc
        first.add_entry(b"new")
        w._reload_grid(select=0)
        second = PackDocument.from_bytes(self.original)
        second._names = {}
        w._docs["second"] = second
        w._kinds_map["second"] = [second.entry_kind(i) for i in range(second.count)]
        w._activate_pack("second")
        self.assertFalse(w._act_undo.isEnabled())
        second.replace_content(0, b"second-edit")
        w._after_entry_changed(0)
        w._activate_pack(first_key)
        self.assertTrue(w._act_undo.isEnabled())
        w._apply_history(False)
        self.assertEqual(first.count, 2)
        self.assertEqual(second.content(0), b"second-edit")
        self.assertTrue(second.can_undo)

    def test_editable_text_keeps_native_undo_but_readonly_preview_uses_document(self):
        w, doc = self.window, self.window._doc
        doc.add_entry(b"new")
        w._reload_grid(select=0)
        editor = QLineEdit("A", w)
        editor.insert("B")
        with mock.patch.object(w, "focusWidget", return_value=editor):
            w.undo_entry()
            self.assertEqual(editor.text(), "A")
            self.assertEqual(doc.count, 3)
            w.redo_entry()
            self.assertEqual(editor.text(), "AB")
            self.assertEqual(doc.count, 3)
        with mock.patch.object(w, "focusWidget", return_value=w._text_preview):
            w.undo_entry()
        self.assertEqual(doc.count, 2)
        self.assertTrue(doc.can_redo)
