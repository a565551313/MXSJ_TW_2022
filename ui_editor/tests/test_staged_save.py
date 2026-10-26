"""「保存新资源（N）」：只把挂账新图写回包，布局一个字不动（0.18.0）。

锁死四件事：
* 核心链：``patch_pack_copy_many(layouts={})`` 只写 ``extra_entries``——
  新增/替换图片条目，其它条目（含所有布局）逐字节保真；空写拒绝；
  ``verify_written_pack(res_path=None)`` 的「只写资源」校验形态通过、
  且仍能抓住回读不一致；
* 主窗口：严格模式写编辑器输出包（没存过先问一次路径并记住），
  宽松模式就地写原包、不生成第二个包；两种模式布局条目字节不变、
  文档脏状态不变、成功后才清挂账；
* 没挂账/确认框点「否」/没打开包内布局：什么都不写；
* 浏览窗按钮：文案带全部挂账数、0 挂账禁用、点击走宿主写包并回报。
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
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication, QMessageBox

    from ui_editor.core import pack_build, publish
    from ui_editor.core.assets import AssetResolver
    from ui_editor.core.errors import PackError
    from ui_editor.core.mxhash import mx_hash
    from ui_editor.core.pack import FlsPack
    from ui_editor.ui.asset_browser import build_browser_dialog
    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False

from test_gui import _mini_pack_bytes  # noqa: E402

RES = "dialog/cateroom.dlg"


def _raw(name: str, data: bytes):
    entry_id = mx_hash(name.encode("gbk"))
    return pack_build.RawEntry(entry_id, pack_build.fresh_r1(entry_id), data)


def _entry_bytes(pack_path, name: str) -> bytes | None:
    with FlsPack(str(pack_path)) as pack:
        return pack.read_id(mx_hash(name.encode("gbk")))


def _fresh_read_back(pack_path, res_path, names):
    """与保存链同款的全新解析器回读（res_path=None = 只写资源）。"""
    fresh = AssetResolver()
    fresh.mount_pack(str(pack_path))
    try:
        got = None if res_path is None else fresh.fetch_dlg(res_path)
        dicts = None if got is None else got[0]
        return dicts, {name: fresh.fetch_bytes(name) for name in names}
    finally:
        fresh.close()


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class StagedOnlyPackTests(unittest.TestCase):
    """核心层：layouts={} 的补丁复制 + 「只写资源」校验。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.src = self.root / "source.fls"
        self.src.write_bytes(pack_build.build_archive([
            _raw("image/a.bin", b"KEEP"),
            _raw("dialog/x.dlg", b"DLG-BYTES"),
        ]))
        self.out = self.root / "out.fls"

    def tearDown(self):
        self._tmp.cleanup()

    def test_staged_only_write_adds_and_replaces_without_layouts(self):
        info = pack_build.patch_pack_copy_many(
            str(self.src), {}, str(self.out),
            extra_entries={"image/n1.png": b"N1", "image/a.bin": b"CHANGED"})
        self.assertEqual(sorted(info["images_added"]), ["image/n1.png"])
        self.assertEqual(info["images_replaced"], ["image/a.bin"])
        self.assertEqual(info["layouts_added"], [])
        self.assertIsNone(info["layout_path"])
        self.assertEqual(_entry_bytes(self.out, "image/n1.png"), b"N1")
        self.assertEqual(_entry_bytes(self.out, "image/a.bin"), b"CHANGED")
        # 布局条目与其它资源一个字节都没动
        self.assertEqual(_entry_bytes(self.out, "dialog/x.dlg"), b"DLG-BYTES")
        # 源包分毫未动
        self.assertEqual(_entry_bytes(self.src, "image/a.bin"), b"KEEP")

    def test_empty_write_rejected(self):
        with self.assertRaises(PackError):
            pack_build.patch_pack_copy_many(str(self.src), {}, str(self.out))

    def test_verify_written_pack_resources_only(self):
        extras = {"image/n1.png": b"N1"}
        info = pack_build.patch_pack_copy_many(
            str(self.src), {}, str(self.out), extra_entries=dict(extras))
        report = publish.verify_written_pack(
            src_pack=str(self.src), out_path=str(self.out), res_path=None,
            extras=extras, expected_dicts=None, info=info,
            read_back=_fresh_read_back, extra_layouts={}, trusted_copy=True)
        self.assertTrue(report.get("ok"), report)
        # 回读不一致仍要抓得住：字节对不上 = 校验失败
        bad = publish.verify_written_pack(
            src_pack=str(self.src), out_path=str(self.out), res_path=None,
            extras={"image/n1.png": b"WRONG"}, expected_dicts=None,
            info=info, read_back=_fresh_read_back, extra_layouts={},
            trusted_copy=True)
        self.assertIn("回读不一致", bad.get("error", ""))
        self.assertFalse(bad["ok"])


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class StagedSaveWindowTests(unittest.TestCase):
    """主窗口层：目标决议跟随保存模式，布局与脏状态一概不碰。"""

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.settings = QSettings(str(self.root / "settings.ini"),
                                  QSettings.Format.IniFormat)
        with mock.patch("ui_editor.ui.main_window.QSettings",
                        return_value=self.settings):
            self.window = MainWindow()
        self.src = self.root / "interface.fls"
        self.src.write_bytes(_mini_pack_bytes(RES))
        self.window.open_pack_file(str(self.src))
        self.window._open_pack_layout(str(self.src), RES)
        self.assertIsNotNone(self.window.doc)

    def tearDown(self):
        for session in self.window._sessions:
            if session.doc is not None:
                session.doc.dirty = False
                session.doc.pending_pack_import = False
        self.window._pending_imports.clear()
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    # -- 工具 ---------------------------------------------------------
    def _switch(self, mode: str, *, answer=QMessageBox.StandardButton.Yes):
        box = mock.Mock()
        box.exec.return_value = answer
        patcher = mock.patch("ui_editor.ui.save_mode.QMessageBox",
                             return_value=box)
        question = patcher.start()
        # 只替换弹窗本身，枚举与常量仍用真的（否则返回值比不上）
        question.StandardButton = QMessageBox.StandardButton
        question.Icon = QMessageBox.Icon
        try:
            self.window.choose_save_mode(mode)
        finally:
            patcher.stop()

    # -- 严格模式：写编辑器输出包 --------------------------------------
    def test_strict_writes_output_pack_without_touching_layouts(self):
        self.window.resolver.stage_image("image/new1.png", b"PNG1")
        self.window.resolver.stage_image("image/new2.igs", b"IGS2")
        layout_before = _entry_bytes(self.src, RES)
        dirty_before = self.window.doc.dirty
        out = self.root / "out.fls"
        titles: list[str] = []

        def yes(*args):
            titles.append(str(args[1]))
            return QMessageBox.StandardButton.Yes

        with mock.patch.object(QMessageBox, "question", side_effect=yes), \
                mock.patch(
                    "ui_editor.ui.save_targets.QFileDialog.getSaveFileName",
                    return_value=(str(out), "")):
            report = self.window.save_staged_resources()
        self.assertIsNotNone(report)
        self.assertTrue(report.get("ok"), report)
        self.assertIn("只保存新资源", titles)
        self.assertTrue(out.exists())
        self.assertEqual(_entry_bytes(out, "image/new1.png"), b"PNG1")
        self.assertEqual(_entry_bytes(out, "image/new2.igs"), b"IGS2")
        # 布局条目原样复制，一个字节没动
        self.assertEqual(_entry_bytes(out, RES), layout_before)
        # 原包分毫未动
        self.assertEqual(_entry_bytes(self.src, RES), layout_before)
        self.assertIsNone(_entry_bytes(self.src, "image/new1.png"))
        # 成功才销账；目标决议与 Ctrl+S 同款（记住输出包、来源迁移）
        self.assertEqual(self.window.resolver.staged_images(), {})
        self.assertEqual(self.window.doc.output_pack, str(out))
        self.assertEqual(self.window.doc.source_pack[0], str(out))
        self.assertEqual(self.window.doc.origin_pack, str(self.src))
        # 布局的脏/干净状态不受影响（本次没写布局）
        self.assertEqual(self.window.doc.dirty, dirty_before)
        self.assertEqual(sorted(report["staged_written"]),
                         ["image/new1.png", "image/new2.igs"])

    # -- 宽松模式：就地写原包 ------------------------------------------
    def test_loose_writes_origin_pack_in_place(self):
        self._switch("loose")
        self.window.resolver.stage_image("image/n.png", b"N")
        layout_before = _entry_bytes(self.src, RES)
        with mock.patch.object(
                QMessageBox, "question",
                return_value=QMessageBox.StandardButton.Yes):
            report = self.window.save_staged_resources()
        self.assertIsNotNone(report)
        self.assertTrue(report.get("ok"), report)
        # 写进的就是原包本身，且没有生成第二个包
        self.assertEqual(_entry_bytes(self.src, "image/n.png"), b"N")
        self.assertEqual(_entry_bytes(self.src, RES), layout_before)
        self.assertFalse((self.root / "out.fls").exists())
        self.assertEqual(
            [p.name for p in self.root.iterdir()],
            sorted(["interface.fls", "settings.ini"]))
        self.assertEqual(self.window.resolver.staged_images(), {})
        self.assertEqual(self.window.doc.source_pack[0], str(self.src))

    # -- 不写的三种情况 -------------------------------------------------
    def test_no_staging_no_write(self):
        before = self.src.read_bytes()
        with mock.patch.object(QMessageBox, "information") as info:
            report = self.window.save_staged_resources()
        self.assertIsNone(report)
        info.assert_called_once()
        self.assertEqual(self.src.read_bytes(), before)

    def test_confirm_cancel_keeps_everything(self):
        self.window.resolver.stage_image("image/n.png", b"N")
        before = self.src.read_bytes()
        out = self.root / "out.fls"
        # 严格模式目标决议会先问一次输出包路径（与 Ctrl+S 同款顺序），
        # 模态框必须一并打桩，否则测试会挂在原生对话框上。
        with mock.patch.object(
                QMessageBox, "question",
                return_value=QMessageBox.StandardButton.No), \
                mock.patch(
                    "ui_editor.ui.save_targets.QFileDialog.getSaveFileName",
                    return_value=(str(out), "")):
            report = self.window.save_staged_resources()
        self.assertIsNone(report)
        self.assertEqual(self.src.read_bytes(), before)
        self.assertFalse(out.exists())   # 点「否」= 什么都没写
        self.assertEqual(sorted(self.window.resolver.staged_images()),
                         ["image/n.png"])   # 挂账保留

    def test_requires_pack_document(self):
        saved_doc = self.window.doc
        self.window.doc = None
        try:
            self.window.resolver.stage_image("image/n.png", b"N")
            with mock.patch.object(QMessageBox, "information") as info:
                report = self.window.save_staged_resources()
            self.assertIsNone(report)
            info.assert_called_once()
            self.assertEqual(sorted(self.window.resolver.staged_images()),
                             ["image/n.png"])
        finally:
            self.window.doc = saved_doc

    # -- 浏览窗按钮 ------------------------------------------------------
    def test_browser_button_reflects_count_and_invokes_host(self):
        self.window.resolver.stage_image("image/n.png", b"N")
        calls: list[bool] = []

        def handler() -> bool:
            # 模拟真实宿主：写包成功后销账
            calls.append(True)
            self.window.resolver.discard_staged(["image/n.png"])
            return True

        dialog = build_browser_dialog(
            self.window, self.window.resolver, ["image/n.png"],
            save_staged=handler)
        try:
            btn = dialog._save_staged_btn
            self.assertIsNotNone(btn)
            self.assertIn("（1）", btn.text())
            self.assertTrue(btn.isEnabled())
            btn.click()
            self.assertEqual(calls, [True])
            # 成功销账后：计数归零、按钮禁用
            self.assertIn("（0）", btn.text())
            self.assertFalse(btn.isEnabled())
        finally:
            dialog.close()
            dialog.deleteLater()
            self._app.processEvents()

        # 没有挂账：按钮禁用；不传 save_staged：按钮不出现
        dialog2 = build_browser_dialog(
            self.window, self.window.resolver, [], save_staged=handler)
        try:
            self.assertIn("（0）", dialog2._save_staged_btn.text())
            self.assertFalse(dialog2._save_staged_btn.isEnabled())
        finally:
            dialog2.close()
            dialog2.deleteLater()
        dialog3 = build_browser_dialog(
            self.window, self.window.resolver, [])
        try:
            self.assertIsNone(dialog3._save_staged_btn)
        finally:
            dialog3.close()
            dialog3.deleteLater()
            self._app.processEvents()

    def test_browser_handler_maps_report_to_bool(self):
        with mock.patch.object(self.window, "save_staged_resources",
                               return_value={"ok": True}):
            self.assertTrue(self.window._browser_save_staged())
        with mock.patch.object(self.window, "save_staged_resources",
                               return_value=None):
            self.assertFalse(self.window._browser_save_staged())
        with mock.patch.object(self.window, "save_staged_resources",
                               return_value={"ok": False, "error": "x"}):
            self.assertFalse(self.window._browser_save_staged())


if __name__ == "__main__":
    unittest.main()
