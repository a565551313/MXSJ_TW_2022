"""选图窗「把图片放进包」支持 .spr（0.19.0，用户拍板 auto_pair）。

* 文件过滤器含 ``*.spr``（.igs 不被挤掉）；
* 单张 .spr：按**原字节**挂账，并自动连带磁盘上同名 ``.igs``/``.png``
  像素搭档（.igs 优先）；
* 磁盘无搭档 → 只挂 .spr，标签直说「有帧表而无像素」；
* 搭档已在包里 → 不重复挂账，标签直说「包内已有」；
* ``[images]`` 变体（像素指到外部 .fls 包）→ 标签点明不随本次导入；
* 多张 .spr 一次选：沿用 0.18.0 多张 .igs 规矩（前缀 + 原文件名 +
  确认清单），连带搭档在清单里成行；搭档已在本批选择里则不重复；
* .spr 与普通图片混选：拒绝；.spr 与 .igs 混选：允许（same_as_igs）。
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
        QListWidget,
        QMessageBox,
    )

    from ui_editor.ui.image_picker import ResourcePickerDialog

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False

_PICK = "ui_editor.ui.image_picker.QFileDialog.getOpenFileNames"


def _fake_ask(res_path):
    """替身 _ask_new_image：固定回 (资源路径, 不转精灵)。"""
    def fake(default_path, multi, can_convert):
        return (res_path, False)
    return fake


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class SprAddTests(unittest.TestCase):
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

    def _add_single(self, src_file: str, res_path: str) -> None:
        with mock.patch(_PICK, return_value=([src_file], "")), \
                mock.patch.object(self.dialog, "_ask_new_image",
                                  side_effect=_fake_ask(res_path)):
            self.dialog._choose_add()

    # -- 过滤器 ---------------------------------------------------------
    def test_filter_includes_spr(self):
        with mock.patch(_PICK, return_value=([], "")) as ask:
            self.dialog._choose_add()
        self.assertIn("*.spr", ask.call_args[0][3])
        self.assertIn("*.igs", ask.call_args[0][3])   # 旧格式不被挤掉

    # -- 单张 .spr + 像素搭档 --------------------------------------------
    def test_single_spr_pairs_igs(self):
        spr = self._write("a.spr", b"SPR")
        self._write("a.igs", b"PIX")
        self._add_single(spr, "dir\\a.spr")
        self.assertEqual(self.staged, {"dir\\a.spr": b"SPR",
                                       "dir\\a.igs": b"PIX"})
        text = self.dialog._count.text()
        self.assertIn("已挂账 dir\\a.spr", text)
        self.assertIn("连带挂账像素搭档 dir\\a.igs", text)

    def test_single_spr_pairs_png_fallback(self):
        spr = self._write("a.spr", b"SPR")
        self._write("a.png", b"PIX")
        self._add_single(spr, "dir\\a.spr")
        self.assertEqual(self.staged, {"dir\\a.spr": b"SPR",
                                       "dir\\a.png": b"PIX"})

    def test_single_spr_igs_wins_over_png(self):
        spr = self._write("a.spr", b"SPR")
        self._write("a.igs", b"IGS")
        self._write("a.png", b"PNG")
        self._add_single(spr, "dir\\a.spr")
        self.assertEqual(self.staged, {"dir\\a.spr": b"SPR",
                                       "dir\\a.igs": b"IGS"})

    def test_single_spr_without_pair_says_pixels_missing(self):
        spr = self._write("a.spr", b"SPR")
        self._add_single(spr, "dir\\a.spr")
        self.assertEqual(self.staged, {"dir\\a.spr": b"SPR"})
        self.assertIn("未找到同名 .igs/.png", self.dialog._count.text())

    def test_single_spr_pair_already_in_pack(self):
        self.dialog.close()
        self.dialog.deleteLater()
        self.dialog = ResourcePickerDialog(
            None, "测试选图窗", ["dir\\a.igs", "dir\\exists.png"], "",
            lambda path: None,
            on_stage=lambda name, data: self.staged.__setitem__(name, data),
            exists=lambda name: name in ("dir\\a.igs", "dir\\exists.png"),
            browse_only=True)
        spr = self._write("a.spr", b"SPR")
        self._write("a.igs", b"PIX")
        self._add_single(spr, "dir\\a.spr")
        # 搭档不重复挂账，但要说清楚像素现成
        self.assertEqual(self.staged, {"dir\\a.spr": b"SPR"})
        self.assertIn("包内已有 dir\\a.igs", self.dialog._count.text())

    def test_single_spr_images_variant_points_outside(self):
        """[images] 变体：像素在外部 .fls 包，本次导入带不上，标签点明。"""
        spr = self._write("a.spr", b"\x00\x01\x02\x03")
        fake_text = ("[images]\n"
                     "FileName1=magic0307.igs\n"
                     "PackageName=magic\n"
                     "BranchPath=res\\\n"
                     "PalPro=0\n")
        with mock.patch("ui_editor.core.spr_desc.decode_spr_text",
                        return_value=fake_text):
            self._add_single(spr, "dir\\a.spr")
        text = self.dialog._count.text()
        self.assertIn("外部包", text)
        self.assertIn("magic", text)

    # -- 多张 .spr：0.18.0 多张 .igs 规矩 + 连带 --------------------------
    def test_multi_spr_igs_dedupe(self):
        """搭档就在本批选择里 → 清单/挂账各一份，不重复。"""
        spr = self._write("a.spr", b"S")
        igs = self._write("a.igs", b"P")

        def accept_with_prefix(dialog_self):
            edit = dialog_self.findChild(QLineEdit)
            self.assertIsNotNone(edit)
            edit.setText("pre")   # 不带分隔符：应自动补成 pre\
            return QDialog.DialogCode.Accepted

        with mock.patch(_PICK, return_value=([spr, igs], "")), \
                mock.patch.object(QDialog, "exec", new=accept_with_prefix):
            self.dialog._choose_add()
        self.assertEqual(self.staged, {"pre\\a.spr": b"S",
                                       "pre\\a.igs": b"P"})
        self.assertIn("已挂账 2 个 .igs/.spr", self.dialog._count.text())

    def test_multi_spr_pair_listed_and_staged(self):
        spr_a = self._write("a.spr", b"S1")
        spr_b = self._write("b.spr", b"S2")
        self._write("a.igs", b"P")     # a.spr 的磁盘搭档；b.spr 没有
        seen: list[str] = []

        def accept_peek_listing(dialog_self):
            edit = dialog_self.findChild(QLineEdit)
            edit.setText("pre")
            listing = dialog_self.findChild(QListWidget)
            self.assertIsNotNone(listing)
            seen.extend(listing.item(i).text()
                        for i in range(listing.count()))
            return QDialog.DialogCode.Accepted

        with mock.patch(_PICK, return_value=([spr_a, spr_b], "")), \
                mock.patch.object(QDialog, "exec", new=accept_peek_listing):
            self.dialog._choose_add()
        self.assertEqual(seen, ["pre\\a.spr",
                                "pre\\a.igs（连带像素搭档）",
                                "pre\\b.spr"])
        self.assertEqual(self.staged, {"pre\\a.spr": b"S1",
                                       "pre\\a.igs": b"P",
                                       "pre\\b.spr": b"S2"})
        self.assertIn("已挂账 3 个 .igs/.spr", self.dialog._count.text())

    # -- 混选规则 ---------------------------------------------------------
    def test_spr_with_plain_image_rejected(self):
        spr = self._write("a.spr", b"S")
        png = self._write("b.png", b"P")
        with mock.patch(_PICK, return_value=([spr, png], "")), \
                mock.patch.object(QMessageBox, "warning") as warn:
            self.dialog._choose_add()
        self.assertEqual(self.staged, {})
        warn.assert_called_once()
        self.assertIn("不能混选", warn.call_args[0][1])

    def test_spr_plus_igs_mix_allowed(self):
        spr = self._write("a.spr", b"S")
        igs = self._write("b.igs", b"G")   # 名字不同：不是 a.spr 的搭档
        with mock.patch(_PICK, return_value=([spr, igs], "")), \
                mock.patch.object(
                    QDialog, "exec",
                    new=lambda dialog_self: QDialog.DialogCode.Accepted), \
                mock.patch.object(QMessageBox, "warning") as warn:
            self.dialog._choose_add()
        warn.assert_not_called()
        self.assertEqual(self.staged, {"a.spr": b"S", "b.igs": b"G"})


if __name__ == "__main__":
    unittest.main()
