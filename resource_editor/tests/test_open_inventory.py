"""大包显示不等全量嗅探；后台结果跨编辑/换基线不能回灌。"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from resource_editor.core.containers import fls0slf
from resource_editor.core.model.document import PackDocument
from resource_editor.core.names import build_name_map

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication

    from resource_editor.gui.main_window import MainWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False


def document(count=3000):
    return PackDocument.from_bytes(
        fls0slf.build(
            [b"DATA"] * count,
            [fls0slf.EntryMeta(entry_id=100 + i, r1=7) for i in range(count)],
        )
    )


class TestQuickNames(unittest.TestCase):
    def test_dictionary_only_never_reads_payload(self):
        reader = mock.Mock(side_effect=AssertionError("must not read"))
        self.assertEqual(
            build_name_map([123], reader, {123: "x/a.dlg"}, references=False),
            {0: "x/a.dlg"},
        )
        reader.assert_not_called()

    def test_label_all_entries_does_not_trigger_reference_scan(self):
        doc = document()
        with mock.patch.object(
            doc.archive, "read_stored", side_effect=AssertionError("no payload")
        ) as read:
            self.assertEqual(len([doc.label(i) for i in range(doc.count)]), 3000)
            read.assert_not_called()
        doc.close()


@unittest.skipUnless(HAS_QT, "Qt unavailable")
class TestInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.doc = document()
        self.window._docs["test"] = self.doc
        self.window._kinds_map["test"] = [None] * self.doc.count

    def tearDown(self):
        self.window._docs.clear()
        self.window.close()
        self.doc.close()

    def test_open_phase_does_not_sniff_all_entries(self):
        jobs = []
        with (
            mock.patch(
                "resource_editor.gui.main_window.PackDocument.open",
                return_value=self.doc,
            ),
            mock.patch.object(
                self.doc, "entry_kind", side_effect=AssertionError("sniff")
            ),
            mock.patch.object(self.window, "_activate_pack"),
            mock.patch.object(self.window, "_schedule_inventory"),
            mock.patch.object(
                self.window,
                "_run_job",
                side_effect=lambda job, done: jobs.append((job, done)),
            ),
        ):
            self.window.open_pack("fresh.fls")
            job, done = jobs[0]
            result = job._fn(lambda *args: None)
            self.assertEqual(result[1], [None] * self.doc.count)
            done(result)

    def test_only_one_inventory_job_per_pack(self):
        with mock.patch.object(self.window, "_register_job") as register:
            self.window._schedule_inventory("test")
            self.window._schedule_inventory("test")
        self.assertEqual(register.call_count, 1)

    def test_stale_inventory_requeues_without_overwriting_types(self):
        jobs = []
        with mock.patch.object(
            self.window,
            "_register_job",
            side_effect=lambda *args, **kw: jobs.append((args, kw)),
        ):
            self.window._schedule_inventory("test")
            self.doc.replace_content(0, b"NEW")
            jobs[0][0][1]((["stale"] * self.doc.count, 0))
        self.assertEqual(self.window._kinds_map["test"], [None] * self.doc.count)
        self.assertEqual(len(jobs), 2)

    def test_inventory_updates_grid_without_clearing_multiselect(self):
        self.window._current_key = "test"
        self.window._grid.set_document(self.doc, [None] * self.doc.count)
        self.window._grid.set_selection_mode(True)
        self.window._grid._selected_set = {4, 55}
        self.window._grid.goto_page(2)
        page = self.window._grid.current_page
        with mock.patch.object(self.window, "_register_job") as register:
            self.window._schedule_inventory("test")
        job, callback = register.call_args.args[:2]
        callback(job._fn(lambda *args: None))
        self.assertEqual(self.window._grid._selected_set, {4, 55})
        self.assertEqual(self.window._grid.current_page, page)
