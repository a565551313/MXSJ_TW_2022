"""批量导入：多个本地布局排一次队，Ctrl+S 一次全部写进新包。

用户报的原话是「每导入一个布局文件都得保存一次，一次只能选择一个布局
文件，没法批量导入」。这里锁住三件事：多选/整个文件夹都能排队、保存
只写一次包、写完之后队列和树都干净。
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from PySide6.QtWidgets import QApplication, QDialog

    from ui_editor.core import dlg_codec
    from ui_editor.core.pack import FlsPack
    from ui_editor.core.pack_build import build_archive
    from ui_editor.ui.batch_import import BatchImportDialog
    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False


def _dlg(title: str) -> bytes:
    return dlg_codec.dump_bytes(
        [{"sWidgetType": "CMainFrame", "sTitle": title, "lChildren": []}],
        md5="0" * 32)


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class BatchImportGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.src = self.root / "interface.fls"
        self.src.write_bytes(build_archive_raw(_dlg("Base")))
        self.window = MainWindow()
        self.window.open_pack_file(str(self.src))
        self._dialogs: list[BatchImportDialog] = []

    def tearDown(self):
        # 关窗会逐个确认「待入新包」的文档；测试里直接放行，别弹模态框。
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
                session.doc.pending_pack_import = False
        if self.window.doc is not None:
            self.window.doc.dirty = False
            self.window.doc.pending_pack_import = False
        self.window._pending_imports.clear()
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    # -- 工具 ---------------------------------------------------------
    def _local(self, name: str, title: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_dlg(title))
        return path

    def _import(self, entries: list[tuple[Path, str]]) -> None:
        """走真实入口：用真 BatchImportDialog 装好行，只把 exec 换成 Accepted。"""
        known = self.window.resolver.scan_layouts(str(self.src))
        dialog = BatchImportDialog(str(self.src), known, self.window)
        for local, res_path in entries:
            dialog.add_local_files([str(local)])
            dialog.rows[-1].path = res_path
        dialog._refresh()
        self._dialogs.append(dialog)
        with mock.patch(
                "ui_editor.ui.import_queue.BatchImportDialog",
                return_value=dialog), \
             mock.patch.object(dialog, "exec", return_value=QDialog.Accepted):
            self.window.import_pack_layout(str(self.src))

    def _save(self) -> str:
        out = str(self.root / "interface_edited.fls")
        with mock.patch(
                "ui_editor.ui.save_workflows.QFileDialog.getSaveFileName",
                lambda *a, **k: (out, "")), \
             mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog.exec",
                return_value=1), \
             mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.information",
                lambda *a, **k: None), \
             mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.warning",
                lambda *a, **k: None):
            self.window.save()
        return out

    def _pending(self) -> list[str]:
        return [item.text(0).replace("（待入新包）", "")
                for item in self.window.resource_panel._pending_items]

    def _has(self, pack: str, path: str) -> bool:
        """包内是否存在这个路径键（不依赖内置布局名单）。"""
        with FlsPack(pack) as handle:
            return handle.contains(path)

    # -- 导入排队 -----------------------------------------------------
    def test_three_files_queue_once_and_one_save_writes_all(self):
        files = [self._local(f"ui/a{i}.dlg", f"A{i}") for i in range(3)]
        self._import([(path, f"custom/a{i}.dlg")
                      for i, path in enumerate(files)])
        self.assertEqual(self.window.doc.source_pack,
                         (str(self.src), "custom/a0.dlg"))
        self.assertTrue(self.window.doc.pending_pack_import)
        self.assertEqual(self._pending(),
                         ["custom/a0.dlg", "custom/a1.dlg", "custom/a2.dlg"])
        self.assertIn("3 个布局", self.window.statusBar().currentMessage())
        self.assertIn("Ctrl+S", self.window.statusBar().currentMessage())

        out = self._save()
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls", "interface_edited.fls"],
                         "批量导入只写一个新包，不是一个布局一个包")
        self.assertEqual(self.window._pending_imports, {},
                         "保存成功后队列要清空")
        self.assertEqual(self.window.resource_panel._pending_items, [])
        for i in range(3):
            self.assertTrue(self._has(out, f"custom/a{i}.dlg"), i)
        message = self.window.statusBar().currentMessage()
        self.assertIn("2 个导入布局", message)  # 当前打开的那个另外算
        # 源包一个字节没动
        self.assertEqual(self.src.read_bytes(), build_archive_raw(_dlg("Base")))

    def test_second_batch_joins_queue_and_same_output(self):
        first = [self._local(f"ui/f{i}.dlg", f"F{i}") for i in range(2)]
        self._import([(path, f"p/f{i}.dlg") for i, path in enumerate(first)])
        self._save()
        second = [self._local(f"ui/s{i}.dlg", f"S{i}") for i in range(2)]
        self._import([(path, f"p/s{i}.dlg") for i, path in enumerate(second)])
        self.assertEqual(self._pending(), ["p/s0.dlg", "p/s1.dlg"])
        out = self._save()
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls", "interface_edited.fls"])
        for path in ("p/f0.dlg", "p/f1.dlg", "p/s0.dlg", "p/s1.dlg"):
            self.assertTrue(self._has(out, path), path)

    def test_review_lists_batched_layouts_before_writing(self):
        files = [self._local(f"ui/r{i}.dlg", f"R{i}") for i in range(2)]
        self._import([(path, f"q/r{i}.dlg") for i, path in enumerate(files)])
        dialog = mock.Mock()
        dialog.exec.return_value = QDialog.Rejected
        with mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog",
                return_value=dialog) as review:
            self.window._confirm_save_review(
                str(self.root / "x.fls"), to_pack=True)
        layouts = review.call_args.kwargs["layouts"]
        self.assertEqual(sorted(kind for kind, _name, _size in layouts),
                         ["新增布局"])
        self.assertEqual([name for _kind, name, _size in layouts],
                         ["q/r1.dlg"],
                         "当前打开的那个在「布局改动」页，队列其它布局列在这里")

    def test_double_click_pending_opens_queued_not_pack(self):
        files = [self._local(f"ui/d{i}.dlg", f"D{i}") for i in range(3)]
        self._import([(path, f"n/d{i}.dlg") for i, path in enumerate(files)])
        self.window._open_pack_layout(str(self.src), "n/d2.dlg")
        self.assertEqual(self.window.doc.source_pack,
                         (str(self.src), "n/d2.dlg"))
        self.assertEqual(self.window.doc.to_dicts()[0]["sTitle"], "D2")
        self.assertNotIn("n/d2.dlg", self.window._pending_imports[str(self.src)])
        self.assertIn("n/d2.dlg", self._pending())

    def test_restore_pending_items_after_tree_reset(self):
        files = [self._local(f"ui/k{i}.dlg", f"K{i}") for i in range(2)]
        self._import([(path, f"m/k{i}.dlg") for i, path in enumerate(files)])
        self.window.resource_panel.reset_sources()
        self.window.resource_panel.add_pack(
            str(self.src), self.window.resolver.scan_layouts(str(self.src)))
        self.window._restore_pending_items()
        self.assertEqual(self._pending(), ["m/k0.dlg", "m/k1.dlg"])

    def test_import_skips_broken_file_and_keeps_the_rest(self):
        self._local("ui/ok.dlg", "OK")
        bad = self.root / "ui" / "bad.dlg"
        bad.write_bytes(b"UI_INFO = [__import__('os')]")
        warnings: list[tuple[str, str]] = []
        known = self.window.resolver.scan_layouts(str(self.src))
        dialog = BatchImportDialog(str(self.src), known, self.window)
        dialog.add_local_dir(self.root / "ui")
        dialog._refresh()
        self._dialogs.append(dialog)
        with mock.patch(
                "ui_editor.ui.import_queue.BatchImportDialog",
                return_value=dialog), \
             mock.patch.object(dialog, "exec", return_value=QDialog.Accepted), \
             mock.patch(
                "ui_editor.ui.main_window.QMessageBox.warning",
                lambda _p, title, text, *a, **k: warnings.append((title, text))):
            self.window.import_pack_layout(str(self.src))
        self.assertEqual(self.window.doc.source_pack[1], "ok.dlg")
        self.assertEqual(self._pending(), ["ok.dlg"])
        self.assertTrue(any("部分布局没能导入" in title
                            for title, _text in warnings))

    def test_cancel_dialog_changes_nothing(self):
        files = [self._local("ui/z.dlg", "Z")]
        known = self.window.resolver.scan_layouts(str(self.src))
        dialog = BatchImportDialog(str(self.src), known, self.window)
        dialog.add_local_files([str(files[0])])
        dialog._refresh()
        self._dialogs.append(dialog)
        before = self.window.doc
        with mock.patch(
                "ui_editor.ui.import_queue.BatchImportDialog",
                return_value=dialog), \
             mock.patch.object(dialog, "exec", return_value=QDialog.Rejected):
            self.window.import_pack_layout(str(self.src))
        self.assertIs(self.window.doc, before)
        self.assertEqual(self.window._pending_imports, {})
        self.assertEqual(self.window.resource_panel._pending_items, [])


def build_archive_raw(plain: bytes) -> bytes:
    """只有一个布局的微型包（原生路径密钥写密文）。"""
    from ui_editor.core.mxhash import mx_hash
    from ui_editor.core.native_layout import encode_layout, path_bytes

    path = "dialog/base.dlg"
    entry_id = mx_hash(path_bytes(path))
    stored = encode_layout(plain, entry_id)
    return build_archive([_raw_entry(entry_id, stored)])


def _raw_entry(entry_id: int, stored: bytes):
    from ui_editor.core.pack_build import RawEntry, fresh_r1

    return RawEntry(entry_id, fresh_r1(entry_id), stored)


if __name__ == "__main__":
    unittest.main()
