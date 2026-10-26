"""选图窗「把图片放进包」支持 .igs（0.18.0）。

* 文件过滤器含 ``*.igs``（以前只能用「所有文件」绕进去）；
* 单张 .igs：按**原字节**挂账，绝不进精灵转换（can_convert=False）；
* 多张 .igs 一次选：按「目录前缀 + 原文件名」逐张挂账，确认框
  逐行列出最终包内路径，前缀可改；默认前缀 = 当前选中项的目录；
* .igs 与普通图片混选：拒绝，什么都不挂（与拼名族「整个族只能是
  .igs」的既有规矩一致）；
* 多张普通图片仍要求转精灵（旧规则不动）。
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

try:
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QLineEdit,
        QMessageBox,
    )

    from ui_editor.ui.image_picker import ResourcePickerDialog

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False

_PICK = "ui_editor.ui.image_picker.QFileDialog.getOpenFileNames"


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class IgsAddTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.staged: dict[str, bytes] = {}
        self.dialog = ResourcePickerDialog(
            None, "测试选图窗", ["dir\\exists.png"], "",
            lambda path: None,
            on_stage=lambda name, data: self.staged.__setitem__(name, data),
            exists=lambda name: name == "dir\\exists.png",
            browse_only=True)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def _write(self, name: str, data: bytes) -> str:
        path = self.root / name
        path.write_bytes(data)
        return str(path)

    # -- 过滤器 ---------------------------------------------------------
    def test_filter_includes_igs(self):
        with mock.patch(_PICK, return_value=([], "")) as ask:
            self.dialog._choose_add()
        self.assertIn("*.igs", ask.call_args[0][3])

    # -- 混选拒绝 -------------------------------------------------------
    def test_mixed_selection_rejected(self):
        a = self._write("a.igs", b"IGS-A")
        b = self._write("b.png", b"PNG-B")
        with mock.patch(_PICK, return_value=([a, b], "")), \
                mock.patch.object(QMessageBox, "warning") as warn:
            self.dialog._choose_add()
        self.assertEqual(self.staged, {})
        warn.assert_called_once()
        self.assertIn("不能混选", warn.call_args[0][1])

    # -- 单张 .igs：原字节挂账，不走转换 --------------------------------
    def test_single_igs_staged_raw_without_convert(self):
        a = self._write("a.igs", b"IGS-RAW-BYTES")
        asked: dict = {}

        def fake_ask(default_path, multi, can_convert):
            asked.update(default=default_path, multi=multi,
                         can_convert=can_convert)
            return ("dir\\a.igs", False)

        with mock.patch(_PICK, return_value=([a], "")), \
                mock.patch.object(self.dialog, "_ask_new_image",
                                  side_effect=fake_ask):
            self.dialog._choose_add()
        self.assertEqual(self.staged, {"dir\\a.igs": b"IGS-RAW-BYTES"})
        self.assertFalse(asked["can_convert"])   # .igs 不给「转精灵」勾选
        self.assertFalse(asked["multi"])

    # -- 多张 .igs：前缀 + 原文件名逐张挂账 ------------------------------
    def test_multi_igs_staged_each_with_edited_prefix(self):
        a = self._write("a.igs", b"A")
        b = self._write("b.igs", b"B")

        def accept_with_prefix(dialog_self):
            edit = dialog_self.findChild(QLineEdit)
            self.assertIsNotNone(edit)
            edit.setText("pre")   # 不带分隔符：应自动补成 pre\
            return QDialog.DialogCode.Accepted

        with mock.patch(_PICK, return_value=([a, b], "")), \
                mock.patch.object(QDialog, "exec", new=accept_with_prefix):
            self.dialog._choose_add()
        self.assertEqual(self.staged,
                         {"pre\\a.igs": b"A", "pre\\b.igs": b"B"})
        self.assertIn("已挂账 2 个 .igs", self.dialog._count.text())

    def test_multi_igs_default_prefix_from_selection(self):
        a = self._write("a.igs", b"A")
        b = self._write("b.igs", b"B")
        self.dialog._select_path("dir\\exists.png")
        captured: dict = {}

        def accept_keep_default(dialog_self):
            edit = dialog_self.findChild(QLineEdit)
            captured["prefix"] = edit.text()
            return QDialog.DialogCode.Accepted

        with mock.patch(_PICK, return_value=([a, b], "")), \
                mock.patch.object(QDialog, "exec", new=accept_keep_default):
            self.dialog._choose_add()
        self.assertEqual(captured["prefix"], "dir\\")
        self.assertEqual(self.staged,
                         {"dir\\a.igs": b"A", "dir\\b.igs": b"B"})

    def test_multi_igs_cancel_stages_nothing(self):
        a = self._write("a.igs", b"A")
        b = self._write("b.igs", b"B")
        with mock.patch(_PICK, return_value=([a, b], "")), \
                mock.patch.object(
                    QDialog, "exec",
                    new=lambda dialog_self: QDialog.DialogCode.Rejected):
            self.dialog._choose_add()
        self.assertEqual(self.staged, {})

    # -- 计数只算真挂上的（PR #89 审查修复） -----------------------------
    def test_multi_igs_count_only_actually_staged(self):
        """取消同名替换的那张不计入「已挂账 N 个」，按钮计数也不虚高。"""
        self.dialog.close()
        self.dialog.deleteLater()
        self.dialog = ResourcePickerDialog(
            None, "测试选图窗", ["a.igs", "dir\\exists.png"], "",
            lambda path: None,
            on_stage=lambda name, data: self.staged.__setitem__(name, data),
            exists=lambda name: name in ("a.igs", "dir\\exists.png"),
            browse_only=True)
        a = self._write("a.igs", b"A")
        b = self._write("b.igs", b"B")
        with mock.patch(_PICK, return_value=([a, b], "")), \
                mock.patch.object(
                    QDialog, "exec",
                    new=lambda dialog_self: QDialog.DialogCode.Accepted), \
                mock.patch.object(
                    QMessageBox, "question",
                    return_value=QMessageBox.StandardButton.No):
            self.dialog._choose_add()
        # a.igs 与包内同名、替换确认点了「否」→ 只挂上 b.igs
        self.assertEqual(self.staged, {"b.igs": b"B"})
        self.assertIn("已挂账 1 个 .igs", self.dialog._count.text())

    # -- 旧规则不动：多张普通图片必须转精灵 ------------------------------
    def test_multi_images_still_need_convert(self):
        p1 = self._write("p1.png", b"1")
        p2 = self._write("p2.png", b"2")
        with mock.patch(_PICK, return_value=([p1, p2], "")), \
                mock.patch.object(self.dialog, "_ask_new_image",
                                  return_value=("x", False)), \
                mock.patch.object(QMessageBox, "information") as info:
            self.dialog._choose_add()
        self.assertEqual(self.staged, {})
        info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
