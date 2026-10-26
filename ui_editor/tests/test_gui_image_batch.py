"""0.20.0 GUI：浏览窗「批量处理…」——参数窗、执行链、选图窗集成。

钉死的规则（用户拍板：入口=浏览窗、操作=最小三样、范围=普通图+.igs、
预览=首图前后对比+清单确认）：
* 参数窗默认全恒等（不缩放、100%、亮度/饱和度 100%），磁盘模式默认
  且没选目录不放行；accept 后才有 plan；
* 输出清单：磁盘模式=目录+原文件名，挂账模式=原包路径+「同名替换
  包内原资源」标注；
* run_batch：挂账模式吐调整后字节（PNG/.igs 都验尺寸）、磁盘模式写
  文件且重名自动 -2 后缀永不覆盖、单项失败进清单不中断整批；
* 选图窗集成：fetch_bytes 回调才出「批量处理…」按钮；没选中给指引；
  范围外后缀（.spr）拒收并给一句话原因；端到端（补丁参数窗）挂账
  成功且计数文案落地；_stage_one(confirm_same_name=False) 不再逐张问
  同名替换（批处理窗已一次性确认）。

0.21.0 增独立入口（工具栏「批图」）测试：磁盘进磁盘出、不挂包也能用；
参数窗恒 can_stage=False（磁盘文件没有包内路径，无从挂账）；文件夹
模式只扫顶层不递归；范围外后缀/读不到的文件拒收给一句话原因、不中断
整批；原文件一律不动，输出经真 run_batch 落盘。
"""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PIL import Image
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QMessageBox,
        QPushButton,
    )

    from ui_editor.core import image_adjust, sprite, sprite_encode
    from ui_editor.core.image_adjust import AdjustParams
    from ui_editor.ui.image_batch import (
        BatchPlan,
        ImageBatchDialog,
        run_batch,
    )
    from ui_editor.ui.image_picker import ResourcePickerDialog

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False

_ROLE = Qt.ItemDataRole.UserRole if HAS_QT else None


def png_bytes(size=(8, 6), color=(200, 30, 30, 255)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", size, color).save(buf, format="PNG")
    return buf.getvalue()


def frame_image():
    img = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
    for x in range(4):
        for y in range(3):
            img.putpixel((x, y), (200, 30, 30, 255))
    return img


def igs_bytes() -> bytes:
    return sprite_encode.encode_frames([frame_image()], "I0")


def batch_items():
    return [("dir\\a.png", "image", png_bytes()),
            ("dir\\b.igs", "igs", igs_bytes())]


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class ImageBatchDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name) / "out"
        self.items = batch_items()

    def tearDown(self):
        self._tmp.cleanup()

    def _dialog(self, **kw):
        dialog = ImageBatchDialog(None, self.items, **kw)
        self.addCleanup(dialog.deleteLater)
        return dialog

    # -- 默认与形状 -----------------------------------------------------
    def test_defaults_are_identity(self):
        dialog = self._dialog()
        self.assertEqual(dialog._mode_combo.currentIndex(), 0)
        self.assertEqual(dialog._percent_spin.value(), 100)
        self.assertEqual(dialog._bright_spin.value(), 100)
        self.assertEqual(dialog._sat_spin.value(), 100)
        self.assertTrue(dialog._radio_disk.isChecked())
        self.assertTrue(dialog._radio_stage.isEnabled())
        self.assertTrue(dialog._keep_aspect.isChecked())
        self.assertIsNone(dialog.plan)
        self.assertTrue(dialog._params().is_identity())
        self.assertFalse(dialog._percent_spin.isEnabled())  # 不缩放都禁用
        self.assertFalse(dialog._tw_spin.isEnabled())

    def test_stage_radio_disabled_without_callback(self):
        dialog = self._dialog(can_stage=False)
        self.assertFalse(dialog._radio_stage.isEnabled())

    def test_target_spins_prefilled_with_first_size(self):
        dialog = self._dialog()
        self.assertEqual((dialog._tw_spin.value(), dialog._th_spin.value()),
                         (8, 6))

    def test_preview_pixmaps_rendered(self):
        dialog = self._dialog()
        self.assertFalse(dialog._before_label.pixmap().isNull())
        self.assertFalse(dialog._after_label.pixmap().isNull())
        self.assertIn("a.png", dialog._info.text())

    def test_preview_works_on_bounded_copy(self):
        """大图预览只动有界工作副本（PR #90：全分辨率逐步重算会卡死）。"""
        big = png_bytes(size=(2000, 1500))
        dialog = ImageBatchDialog(None, [("d\\big.png", "image", big)])
        self.addCleanup(dialog.deleteLater)
        self.assertEqual(dialog._preview_src.size, (2000, 1500))
        self.assertEqual(dialog._preview_work.size, (360, 270))
        self.assertFalse(dialog._preview_before_pm.isNull())
        self.assertEqual((dialog._tw_spin.value(), dialog._th_spin.value()),
                         (2000, 1500))          # 参数预填仍按真实尺寸
        dialog._mode_combo.setCurrentIndex(1)
        dialog._percent_spin.setValue(200)       # 720×540 ≤ 上限 → 照常出图
        self.assertFalse(dialog._after_label.pixmap().isNull())
        dialog._percent_spin.setValue(500)       # 真实输出巨幅 → 直说并略过
        self.assertIn("预览从略", dialog._after_label.text())
        self.assertIn("10000×7500", dialog._after_label.text())

    def test_preview_memory_error_shows_note(self):
        dialog = self._dialog()
        with mock.patch.object(image_adjust, "adjust_image",
                               side_effect=MemoryError):
            dialog._refresh_preview()
        self.assertIn("预览内存不足", dialog._after_label.text())
        self.assertTrue(dialog._after_label.pixmap().isNull())

    # -- accept → plan ---------------------------------------------------
    def test_accept_requires_dir_in_disk_mode(self):
        dialog = self._dialog()
        with mock.patch.object(QMessageBox, "warning") as warn:
            dialog._on_accept()
        self.assertIsNone(dialog.plan)
        warn.assert_called_once()
        self.assertIn("还没选输出目录", warn.call_args[0][1])
        dialog._dir_edit.setText(str(self.out))
        dialog._on_accept()
        self.assertIsNotNone(dialog.plan)
        self.assertEqual(dialog.plan.mode, "disk")
        self.assertEqual(dialog.plan.out_dir, str(self.out))
        self.assertTrue(dialog.plan.params.is_identity())

    def test_accept_stage_mode_carries_params(self):
        dialog = self._dialog()
        dialog._radio_stage.setChecked(True)
        dialog._mode_combo.setCurrentIndex(1)
        dialog._percent_spin.setValue(200)
        dialog._bright_spin.setValue(150)
        dialog._on_accept()
        self.assertEqual(dialog.plan.mode, "stage")
        self.assertEqual(dialog.plan.params.scale_mode, "percent")
        self.assertEqual(dialog.plan.params.percent, 200)
        self.assertAlmostEqual(dialog.plan.params.brightness, 1.5)
        self.assertEqual(dialog._bright_slider.value(), 150)  # 滑杆同步

    # -- 输出清单 ---------------------------------------------------------
    def test_listing_disk_shows_target_paths(self):
        dialog = self._dialog()
        texts = [dialog._listing.item(i).text()
                 for i in range(dialog._listing.count())]
        self.assertEqual(texts,
                         ["a.png（选好输出目录后显示完整路径）",
                          "b.igs（选好输出目录后显示完整路径）"])
        dialog._dir_edit.setText("out\\dir")
        texts = [dialog._listing.item(i).text()
                 for i in range(dialog._listing.count())]
        self.assertEqual(texts, ["out\\dir\\a.png", "out\\dir\\b.igs"])

    def test_listing_predicts_collision_suffix(self):
        """输出目录已有同名 → 清单显示真正会落盘的 -2 名（PR #90）。"""
        self.out.mkdir(parents=True)
        (self.out / "a.png").write_bytes(b"old")
        dialog = self._dialog()
        dialog._dir_edit.setText(str(self.out))
        texts = [dialog._listing.item(i).text()
                 for i in range(dialog._listing.count())]
        self.assertEqual(texts, [f"{self.out}\\a-2.png",
                                 f"{self.out}\\b.igs"])

    def test_listing_reserves_names_within_batch(self):
        """同批两项同名：第二项预演成 -2（与逐张落盘的 unique_target 一致）。"""
        items = [("d1\\x.png", "image", png_bytes()),
                 ("d2\\x.png", "image", png_bytes())]
        dialog = ImageBatchDialog(None, items)
        self.addCleanup(dialog.deleteLater)
        dialog._dir_edit.setText(str(self.out))
        texts = [dialog._listing.item(i).text()
                 for i in range(dialog._listing.count())]
        self.assertEqual(texts, [f"{self.out}\\x.png",
                                 f"{self.out}\\x-2.png"])

    def test_listing_stage_marks_replacement(self):
        dialog = self._dialog()
        dialog._radio_stage.setChecked(True)
        texts = [dialog._listing.item(i).text()
                 for i in range(dialog._listing.count())]
        self.assertEqual(texts,
                         ["dir\\a.png（同名替换包内原资源）",
                          "dir\\b.igs（同名替换包内原资源）"])


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class RunBatchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name) / "out"
        self.items = batch_items()

    def tearDown(self):
        self._tmp.cleanup()

    def test_stage_mode_emits_adjusted_bytes(self):
        staged: dict[str, bytes] = {}
        plan = BatchPlan(AdjustParams(scale_mode="percent", percent=200),
                         "stage")
        ok, failed = run_batch(
            self.items, plan,
            stage=lambda name, data: staged.__setitem__(name, data) or True)
        self.assertEqual(ok, ["dir\\a.png", "dir\\b.igs"])
        self.assertEqual(failed, [])
        with Image.open(io.BytesIO(staged["dir\\a.png"])) as img:
            self.assertEqual(img.format, "PNG")
            self.assertEqual(img.size, (16, 12))
        frame = sprite.decode_sprite(staged["dir\\b.igs"]).frames[0]
        self.assertEqual((frame.width, frame.height), (16, 12))

    def test_disk_mode_writes_files_never_overwrites(self):
        plan = BatchPlan(AdjustParams(brightness=1.2), "disk", str(self.out))
        ok, failed = run_batch(self.items, plan)
        self.assertEqual(len(ok), 2)
        self.assertEqual(failed, [])
        self.assertTrue((self.out / "a.png").is_file())
        self.assertTrue((self.out / "b.igs").is_file())
        ok2, _failed2 = run_batch(self.items, plan)
        self.assertEqual(len(ok2), 2)
        # 重名自动 -2 后缀，原有输出一字节没动
        self.assertTrue((self.out / "a-2.png").is_file())
        self.assertTrue((self.out / "b-2.igs").is_file())
        self.assertTrue((self.out / "a.png").is_file())

    def test_stage_refusal_counted_as_failure(self):
        plan = BatchPlan(AdjustParams(), "stage")
        ok, failed = run_batch(self.items, plan,
                               stage=lambda name, data: False)
        self.assertEqual(ok, [])
        self.assertEqual(len(failed), 2)
        self.assertIn("未挂账", failed[0])

    def test_bad_item_does_not_stop_batch(self):
        items = self.items + [("dir\\bad.igs", "igs", b"garbage")]
        staged: dict[str, bytes] = {}
        plan = BatchPlan(AdjustParams(), "stage")
        ok, failed = run_batch(
            items, plan,
            stage=lambda name, data: staged.__setitem__(name, data) or True)
        self.assertEqual(len(ok), 2)
        self.assertEqual(len(failed), 1)
        self.assertIn("dir\\bad.igs", failed[0])


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class PickerBatchEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.staged: dict[str, bytes] = {}
        self.store = {"dir\\a.png": png_bytes(), "dir\\b.igs": igs_bytes()}
        self.dialog = ResourcePickerDialog(
            None, "测试浏览窗", list(self.store) + ["dir\\c.spr"], "",
            lambda path: None,
            on_stage=lambda name, data: self.staged.__setitem__(name, data),
            exists=lambda name: name in self.store,
            fetch_bytes=lambda name: self.store.get(name),
            browse_only=True)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()
        self._app.processEvents()

    def _select(self, *paths):
        hits = 0
        for i in range(self.dialog._list.count()):
            item = self.dialog._list.item(i)
            if str(item.data(_ROLE)) in paths:
                item.setSelected(True)
                hits += 1
        self.assertEqual(hits, len(paths))

    # -- 入口与分筛 -------------------------------------------------------
    def test_batch_button_needs_fetch_bytes(self):
        labels = [b.text() for b in self.dialog.findChildren(QPushButton)]
        self.assertIn("批量处理…", labels)
        plain = ResourcePickerDialog(
            None, "无回调", ["a.png"], "", lambda path: None,
            browse_only=True)
        self.addCleanup(plain.deleteLater)
        labels2 = [b.text() for b in plain.findChildren(QPushButton)]
        self.assertNotIn("批量处理…", labels2)

    def test_no_selection_gives_hint(self):
        with mock.patch.object(QMessageBox, "information") as info:
            self.dialog._batch_process()
        info.assert_called_once()
        self.assertIn("还没选图片", info.call_args[0][1])
        self.assertEqual(self.staged, {})

    def test_unsupported_selection_rejected_with_reason(self):
        self._select("dir\\c.spr")
        with mock.patch.object(QMessageBox, "warning") as warn:
            self.dialog._batch_process()
        warn.assert_called_once()
        self.assertIn("选中的都不能批处理", warn.call_args[0][1])
        self.assertIn(".spr 不在批处理范围", warn.call_args[0][2])
        self.assertEqual(self.staged, {})

    def test_fetch_error_rejected_but_batch_continues(self):
        """fetch_bytes 抛异常（坏包条目/非法路径）→ 单项拒收、整批照跑（PR #90）。"""
        self.dialog.close()
        self.dialog.deleteLater()

        def fetch(name):
            if name == "dir\\b.igs":
                raise ValueError("条目损坏")
            return self.store.get(name)

        self.dialog = ResourcePickerDialog(
            None, "测试浏览窗", list(self.store) + ["dir\\c.spr"], "",
            lambda path: None,
            on_stage=lambda name, data: self.staged.__setitem__(name, data),
            exists=lambda name: name in self.store,
            fetch_bytes=fetch,
            browse_only=True)
        self._select("dir\\a.png", "dir\\b.igs")
        plan = BatchPlan(AdjustParams(), "stage")
        with mock.patch("ui_editor.ui.image_batch.ImageBatchDialog") as cls, \
                mock.patch.object(QMessageBox, "warning") as warn:
            cls.return_value.exec.return_value = QDialog.DialogCode.Accepted
            cls.return_value.plan = plan
            self.dialog._batch_process()
        self.assertEqual(set(self.staged), {"dir\\a.png"})
        warn.assert_called_once()
        self.assertIn("有些没能处理", warn.call_args[0][1])
        self.assertIn("dir\\b.igs：包内读不到字节（条目损坏）",
                      warn.call_args[0][2])
        self.assertIn("批量处理完成 1 张", self.dialog._count.text())

    # -- 端到端（补丁参数窗） ----------------------------------------------
    def test_batch_stage_flow_end_to_end(self):
        self._select("dir\\a.png", "dir\\b.igs")
        plan = BatchPlan(AdjustParams(scale_mode="percent", percent=200),
                         "stage")
        with mock.patch("ui_editor.ui.image_batch.ImageBatchDialog") as cls:
            cls.return_value.exec.return_value = QDialog.DialogCode.Accepted
            cls.return_value.plan = plan
            self.dialog._batch_process()
        self.assertEqual(set(self.staged), {"dir\\a.png", "dir\\b.igs"})
        with Image.open(io.BytesIO(self.staged["dir\\a.png"])) as img:
            self.assertEqual(img.size, (16, 12))
        frame = sprite.decode_sprite(self.staged["dir\\b.igs"]).frames[0]
        self.assertEqual((frame.width, frame.height), (16, 12))
        self.assertIn("批量处理完成 2 张", self.dialog._count.text())
        self.assertIn("已挂账", self.dialog._count.text())

    def test_batch_cancel_stages_nothing(self):
        self._select("dir\\a.png")
        with mock.patch("ui_editor.ui.image_batch.ImageBatchDialog") as cls:
            cls.return_value.exec.return_value = QDialog.DialogCode.Rejected
            cls.return_value.plan = None
            self.dialog._batch_process()
        self.assertEqual(self.staged, {})

    # -- 同名替换确认的批量豁免 --------------------------------------------
    def test_stage_one_confirm_suppression(self):
        with mock.patch.object(
                QMessageBox, "question",
                return_value=QMessageBox.StandardButton.No) as ask:
            self.assertFalse(self.dialog._stage_one("dir\\a.png", b"X"))
        ask.assert_called_once()
        # 批处理路径：清单里一次性确认过，不再逐张问
        self.assertTrue(self.dialog._stage_one(
            "dir\\a.png", b"X", confirm_same_name=False))
        self.assertEqual(self.staged["dir\\a.png"], b"X")


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class StandaloneDiskBatchTests(unittest.TestCase):
    """0.21.0 工具栏「批图」独立入口：磁盘进磁盘出，不用挂包。

    钉死：不挂包、不打开任何布局也能批处理；参数窗恒 can_stage=False
    （磁盘文件没有包内路径，无从挂账）；文件夹模式只扫顶层（不递归，
    防误吞整棵大树）；范围外后缀 / 读不到的文件拒收并各给一句话原因、
    不中断整批；原文件一律不动，输出经真 run_batch 落盘（端到端验证）。
    """

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.out_dir = self.root / "out"
        self.captured: dict = {}

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

    # -- 补丁目标与替身 -----------------------------------------------------
    _PICK = "ui_editor.ui.asset_browser.QFileDialog.getOpenFileNames"
    _PICK_DIR = ("ui_editor.ui.asset_browser."
                 "QFileDialog.getExistingDirectory")
    _DLG = "ui_editor.ui.image_batch.ImageBatchDialog"
    _WARN = "ui_editor.ui.asset_browser.QMessageBox.warning"

    def _fake_dialog(self, parent, items, suggested_dir="", can_stage=True):
        """参数窗替身：记下构造参数，plan 直接给磁盘计划（真执行）。"""
        self.captured.update(items=items, suggested_dir=suggested_dir,
                             can_stage=can_stage)
        dlg = mock.Mock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.plan = BatchPlan(
            AdjustParams(scale_mode="percent", percent=200),
            "disk", str(self.out_dir))
        return dlg

    def _write_sources(self):
        a = self.root / "a.png"
        a.write_bytes(png_bytes())
        b = self.root / "b.igs"
        b.write_bytes(igs_bytes())
        return a, b

    # -- 工具栏接线 ---------------------------------------------------------
    def test_toolbar_split_button_and_menu(self):
        btn = self.window._batch_btn
        self.assertEqual(btn.text(), "批图")
        self.assertFalse(btn.icon().isNull())
        self.assertEqual([a.text() for a in btn.menu().actions()],
                         ["选图片文件批处理…", "选文件夹批处理…"])
        self.assertIn(btn, self.window._toolbar.findChildren(type(btn)))

    # -- 文件模式 -----------------------------------------------------------
    def test_files_flow_end_to_end_disk_only(self):
        a, b = self._write_sources()
        assets = getattr(self.window, "resolver", None)
        self.assertTrue(assets is None or not assets._packs)  # 没挂包
        status = mock.Mock()
        with mock.patch.object(self.window, "_update_status", status), \
                mock.patch(self._PICK, return_value=([str(a), str(b)], "")), \
                mock.patch(self._DLG, self._fake_dialog):
            self.window.batch_images_from_disk()
        self.assertFalse(self.captured["can_stage"])
        self.assertEqual([p for p, _k, _d in self.captured["items"]],
                         [str(a), str(b)])
        self.assertEqual([k for _p, k, _d in self.captured["items"]],
                         ["image", "igs"])
        self.assertEqual(self.captured["suggested_dir"], str(self.root))
        # 真 run_batch 落盘：200% → 16×12；原文件一个字节不动
        with Image.open(self.out_dir / "a.png") as out_img:
            self.assertEqual(out_img.size, (16, 12))
        frame = sprite.decode_sprite(
            (self.out_dir / "b.igs").read_bytes()).frames[0]
        self.assertEqual((frame.width, frame.height), (16, 12))
        self.assertEqual(a.read_bytes(), png_bytes())
        self.assertEqual(b.read_bytes(), igs_bytes())
        status.assert_called_once()
        self.assertIn("图像批处理完成 2 张", status.call_args[0][0])
        self.assertIn(str(self.out_dir), status.call_args[0][0])

    def test_rejected_listed_but_batch_continues(self):
        good = self.root / "a.png"
        good.write_bytes(png_bytes())
        bad = self.root / "x.txt"
        bad.write_text("x", encoding="utf-8")
        gone = str(self.root / "missing.png")
        with mock.patch(self._PICK,
                        return_value=([str(good), str(bad), gone], "")), \
                mock.patch(self._DLG, self._fake_dialog), \
                mock.patch(self._WARN) as warn:
            self.window.batch_images_from_disk()
        self.assertTrue((self.out_dir / "a.png").is_file())  # 能处理的照做
        warn.assert_called_once()
        text = warn.call_args[0][2]
        self.assertIn("x.txt：.txt 不在批处理范围", text)
        self.assertIn("missing.png：读不到文件", text)

    def test_all_rejected_dialog_never_opens(self):
        bad = self.root / "x.txt"
        bad.write_text("x", encoding="utf-8")
        with mock.patch(self._PICK, return_value=([str(bad)], "")), \
                mock.patch(self._DLG) as dlg, \
                mock.patch(self._WARN) as warn:
            self.window.batch_images_from_disk()
        dlg.assert_not_called()
        self.assertIn("选中的都不能批处理", warn.call_args[0][1])

    def test_cancel_is_silent(self):
        with mock.patch(self._PICK, return_value=([], "")), \
                mock.patch(self._DLG) as dlg, \
                mock.patch(self._WARN) as warn:
            self.window.batch_images_from_disk()
        dlg.assert_not_called()
        warn.assert_not_called()

    # -- 文件夹模式 ---------------------------------------------------------
    def test_folder_flow_scans_top_level_only(self):
        (self.root / "a.png").write_bytes(png_bytes())
        (self.root / "notes.txt").write_text("x", encoding="utf-8")
        sub = self.root / "sub"
        sub.mkdir()
        (sub / "c.png").write_bytes(png_bytes())
        with mock.patch(self._PICK_DIR, return_value=str(self.root)), \
                mock.patch(self._DLG, self._fake_dialog):
            self.window.batch_folder_from_disk()
        self.assertEqual(
            [Path(p).name for p, _k, _d in self.captured["items"]],
            ["a.png"])          # 不钻子文件夹、不捞 .txt
        self.assertEqual(self.captured["suggested_dir"], str(self.root))
        self.assertTrue((self.out_dir / "a.png").is_file())

    def test_folder_without_images_reports_status(self):
        (self.root / "notes.txt").write_text("x", encoding="utf-8")
        status = mock.Mock()
        with mock.patch.object(self.window, "_update_status", status), \
                mock.patch(self._PICK_DIR, return_value=str(self.root)), \
                mock.patch(self._DLG) as dlg:
            self.window.batch_folder_from_disk()
        dlg.assert_not_called()
        self.assertIn("没找到可批处理的图片", status.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
