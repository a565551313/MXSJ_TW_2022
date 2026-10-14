"""保存后的网格/选择按 entry_id 重建；用同步任务启动器测试真实用例。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication, QMessageBox

    from resource_editor.gui.main_window import MainWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False

from resource_editor.core import names
from resource_editor.core.containers import fls0slf
from resource_editor.core.mxhash import mx_hash


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiSaveSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_save_rebuilds_grid_and_preserves_selected_entry_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, target = root / "source.fls", root / "new.fls"
            pairs = sorted((mx_hash(p.encode()), p, p.encode())
                           for p in ["images/a.bin", "images/b.bin"])
            original = fls0slf.build(
                [payload for _, _, payload in pairs],
                [fls0slf.EntryMeta(entry_id=eid, r1=7) for eid, _, _ in pairs])
            source.write_bytes(original)
            with mock.patch.object(names, "_KNOWN_CACHE", {
                eid: name for eid, name, _ in pairs
            }):
                window = MainWindow()
                try:
                    # 仅替换调度，不替换解析、排序、保存与界面更新。
                    def run(job, done, *args, **kwargs):
                        done(job._fn(lambda *progress: None))

                    with mock.patch.object(window, "_run_job", run), \
                            mock.patch.object(window, "_register_job", run):
                        window.set_workspace(root)
                        window.open_pack(str(source))
                        doc = window._doc
                        new_name = next(
                            f"new/{i}.bin" for i in range(100)
                            if mx_hash(f"new/{i}.bin".encode()) < pairs[0][0])
                        doc.add_entry_for_path(b"NEW", new_name)
                        selected_name = "images/a.bin"
                        selected_before = doc.index_by_path(selected_name)
                        window._reload_grid(select=selected_before)
                        with mock.patch(
                            "resource_editor.gui.main_window."
                            "QFileDialog.getSaveFileName",
                            return_value=(str(target), ""),
                        ):
                            window.save_file(False)
                        self.assertEqual(source.read_bytes(), original)
                        self.assertEqual(doc.path, target)
                        selected_after = doc.index_by_path(selected_name)
                        self.assertNotEqual(selected_before, selected_after)
                        self.assertEqual(window._current, selected_after)
                        self.assertEqual(doc.content(window._current),
                                         selected_name.encode())
                        self.assertEqual(window._grid._kinds,
                                         [doc.entry_kind(i)
                                          for i in range(doc.count)])
                        self.assertEqual(doc.true_name(doc.index_by_path(new_name)),
                                         new_name)
                finally:
                    for doc in window._docs.values():
                        # 测试异常时不弹退出确认，文件仍由临时目录隔离。
                        for slot in doc._slots:
                            slot.dirty = False
                    with mock.patch(
                        "resource_editor.gui.main_window.QMessageBox.question",
                        return_value=QMessageBox.Yes,
                    ):
                        window.close()
                    window.deleteLater()
                    self.app.processEvents()
