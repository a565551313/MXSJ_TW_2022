"""保存模式：严格（原包只读）与宽松（直接写原包）。

用户要的是工具栏上一个「模式」下拉：严格模式保持现在的行为，宽松模式
把改动直接写进原包；切到宽松必须二次确认。这里锁住五件事：

* 默认严格，两个菜单项与勾选状态正确；
* 切宽松要确认，点「否」不生效、点「是」才切并写进设置；
* 宽松模式 Ctrl+S 直接改原包：不问输出路径、不生成第二个包、
  再点一次仍是同一个原包（第二次是覆盖写，不是又造一个包）；
* 切回严格后不再写原包，下一次保存重新问输出包；
* 宽松模式下批量导入的布局也随同一次保存进原包。
"""

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
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    from ui_editor.core import dlg_codec
    from ui_editor.core.assets import AssetResolver
    from ui_editor.core.pack import FlsPack
    from ui_editor.ui.batch_import import BatchImportDialog
    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False

from test_gui import _mini_pack_bytes  # noqa: E402

RES = "dialog/cateroom.dlg"


def _title(pack: Path) -> str | None:
    """从包里回读 sTitle（全新解析器，避免读缓存）。"""
    resolver = AssetResolver()
    resolver.mount_pack(str(pack))
    try:
        got = resolver.fetch_pack_dlg(str(pack), RES)
        return None if got is None else got[0][0].get("sTitle")
    finally:
        resolver.close()


def _dlg(title: str) -> bytes:
    return dlg_codec.dump_bytes(
        [{"sWidgetType": "CMainFrame", "sTitle": title, "lChildren": []}],
        md5="0" * 32)


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class SaveModeTests(unittest.TestCase):
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
        self.window.doc.roots[0].props["sTitle"] = "edited"
        self.asked: list[str] = []
        self.reviews: list[dict] = []
        self.infos: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

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
        return question

    def _save(self, *, output: str | None = None):
        """走真实 save()：记下有没有问输出路径、清单参数与提示。"""
        self.asked.clear()
        self.reviews.clear()
        self.warnings.clear()

        def ask(*_args, **_kwargs):
            self.asked.append("asked")
            if output is None:
                return ("", "")
            return (output, "")

        def review(*args, **kwargs):
            dialog = mock.Mock()
            dialog.exec.return_value = QDialog.Accepted
            self.reviews.append({"args": args, "kwargs": kwargs,
                                 "dialog": dialog})
            return dialog

        with mock.patch(
                "ui_editor.ui.save_workflows.QFileDialog.getSaveFileName",
                ask), \
             mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog",
                review), \
             mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.information",
                lambda _p, title, text, *a, **k: self.infos.append(
                    (title, str(text)))), \
             mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.warning",
                lambda _p, title, text, *a, **k: self.warnings.append(
                    (title, str(text)))):
            self.window.save()

    def _import(self, files: list[tuple[Path, str]]) -> None:
        dialog = BatchImportDialog(
            str(self.src), self.window.resolver.scan_layouts(str(self.src)),
            self.window)
        for local, res_path in files:
            dialog.add_local_files([str(local)])
            dialog.rows[-1].path = res_path
        dialog._refresh()
        with mock.patch(
                "ui_editor.ui.import_queue.BatchImportDialog",
                return_value=dialog), \
             mock.patch.object(dialog, "exec", return_value=QDialog.Accepted):
            self.window.import_pack_layout(str(self.src))
        dialog.deleteLater()

    def _local(self, name: str, title: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_dlg(title))
        return path

    # -- 默认与切换 ---------------------------------------------------
    def test_default_is_strict_and_menu_has_two_modes(self):
        self.assertEqual(self.window.save_mode(), "strict")
        self.assertEqual(self.window._mode_btn.text(), "模式")
        self.assertEqual(self.window._mode_btn.objectName(), "saveModeButton")
        actions = self.window._mode_actions
        self.assertEqual(set(actions), {"strict", "loose"})
        self.assertTrue(actions["strict"].isChecked())
        self.assertFalse(actions["loose"].isChecked())
        self.assertEqual(self.window._mode_btn.styleSheet(), "",
                         "严格模式不该有红字")

    def test_switch_to_loose_asks_and_no_keeps_strict(self):
        question = self._switch("loose", answer=QMessageBox.StandardButton.No)
        question.assert_called_once()
        text = question.call_args.args[2]
        self.assertIn("直接改写", text)
        self.assertIn("备份", text)
        self.assertEqual(self.window.save_mode(), "strict")
        self.assertTrue(self.window._mode_actions["strict"].isChecked())
        self.assertNotEqual(self.settings.value("save_mode"), "loose",
                            "被拒绝的切换不能写进设置")

    def test_switch_to_loose_confirmed_marks_ui_red(self):
        question = self._switch("loose")
        question.assert_called_once()
        self.assertEqual(self.window.save_mode(), "loose")
        self.assertEqual(self.settings.value("save_mode"), "loose")
        self.assertTrue(self.window._mode_actions["loose"].isChecked())
        self.assertFalse(self.window._mode_actions["strict"].isChecked())
        self.assertIn("c0392b", self.window._mode_btn.styleSheet())
        self.assertIn("宽松", self.window._source_label.text())
        self.assertIn("宽松", self.window.windowTitle())
        self.assertIn("宽松", self.window.statusBar().currentMessage())

    def test_switch_back_to_strict_does_not_ask(self):
        self._switch("loose")
        with mock.patch("ui_editor.ui.save_mode.QMessageBox") as question:
            question.StandardButton = QMessageBox.StandardButton
            question.Icon = QMessageBox.Icon
            self.window.choose_save_mode("strict")
        question.assert_not_called()
        self.assertEqual(self.window.save_mode(), "strict")

    def test_mode_is_remembered_across_restart(self):
        self.settings.setValue("save_mode", "loose")
        with mock.patch("ui_editor.ui.main_window.QSettings",
                        return_value=self.settings):
            window = MainWindow()
        try:
            self.assertEqual(window.save_mode(), "loose",
                             "重启后保持上次的模式")
            self.assertIn("c0392b", window._mode_btn.styleSheet())
            self.assertIn("宽松", window._mode_btn.toolTip())
        finally:
            window.close()
            window.deleteLater()
            self._app.processEvents()

    # -- 严格模式：原包只读 -------------------------------------------
    def test_strict_save_writes_new_pack_and_keeps_source(self):
        before = self.src.read_bytes()
        out = str(self.root / "interface_edited.fls")
        self._save(output=out)
        self.assertEqual(self.asked, ["asked"], "严格模式第一次要问输出包")
        self.assertEqual(self.warnings, [])
        self.assertEqual(self.src.read_bytes(), before, "原包一个字节不能动")
        self.assertTrue(Path(out).is_file())
        self.assertEqual(_title(Path(out)), "edited")
        self.assertEqual(self.window.doc.output_pack, out)

    def test_strict_mode_still_refuses_writing_the_source(self):
        before = self.src.read_bytes()
        with mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.warning",
                lambda _p, title, text, *a, **k: self.warnings.append(
                    (title, str(text)))):
            ok = self.window._save_to_pack(str(self.src))
        self.assertFalse(ok)
        self.assertEqual(self.warnings[0][0], "保存前检查失败")
        self.assertEqual(self.src.read_bytes(), before)

    # -- 宽松模式：直接写原包 -----------------------------------------
    def test_loose_save_overwrites_source_without_asking(self):
        self._switch("loose")
        before = self.src.read_bytes()
        self._save()
        self.assertEqual(self.asked, [], "宽松模式不该问输出路径")
        self.assertEqual(self.warnings, [])
        self.assertNotEqual(self.src.read_bytes(), before, "原包应被改写")
        self.assertEqual(_title(self.src), "edited", "原包里能读回新内容")
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls"], "宽松模式不生成新包")
        self.assertIn("已直接写回原包",
                      self.window.statusBar().currentMessage())
        self.assertIn("没有留备份",
                      self.window.statusBar().currentMessage())

    def test_loose_second_save_keeps_same_pack(self):
        self._switch("loose")
        self._save()
        first = self.src.read_bytes()
        self.window.doc.roots[0].props["sTitle"] = "second"
        self._save()
        self.assertEqual(self.asked, [])
        self.assertEqual(self.warnings, [])
        self.assertEqual(_title(self.src), "second")
        self.assertNotEqual(self.src.read_bytes(), first)
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls"])

    def test_loose_review_says_in_place(self):
        self._switch("loose")
        self._save()
        self.assertEqual(len(self.reviews), 1)
        self.assertTrue(self.reviews[0]["kwargs"].get("in_place"),
                        "宽松模式的保存清单要说「直接改写原包」")

    def test_loose_batch_import_goes_into_source_in_one_save(self):
        self._switch("loose")
        files = [self._local(f"ui/i{i}.dlg", f"I{i}") for i in range(2)]
        self._import([(path, f"custom/i{i}.dlg")
                      for i, path in enumerate(files)])
        self._save()
        self.assertEqual(self.asked, [])
        self.assertEqual(self.warnings, [])
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls"])
        with FlsPack(self.src) as pack:
            for i in range(2):
                self.assertTrue(pack.contains(f"custom/i{i}.dlg"), i)
        self.assertEqual(self.window._pending_imports, {})

    def test_switch_back_to_strict_forgets_in_place_output(self):
        self._switch("loose")
        self._save()
        self.assertEqual(self.window.doc.output_pack, str(self.src))
        self._switch("strict")
        self.assertIsNone(self.window.doc.output_pack,
                          "切回严格必须忘掉「输出包就是原包」这件事")
        out = str(self.root / "interface_edited.fls")
        self._save(output=out)
        self.assertEqual(self.asked, ["asked"], "严格模式重新问输出包")
        self.assertEqual(_title(Path(out)), "edited")
        self.assertTrue(Path(out).is_file())


    def test_loose_ignores_earlier_new_pack_and_writes_origin(self):
        """按用户口径：宽松模式一律回原包，不管之前存过哪个新包。"""
        out = str(self.root / "interface_edited.fls")
        self._save(output=out)
        self.assertEqual(self.window.doc.output_pack, out)
        self._switch("loose")
        before_source = self.src.read_bytes()
        before_new = Path(out).read_bytes()
        self.window.doc.roots[0].props["sTitle"] = "loose"
        self._save()
        self.assertEqual(self.asked, [], "宽松模式不该再问路径")
        self.assertEqual(_title(self.src), "loose", "改动要落到原包")
        self.assertNotEqual(self.src.read_bytes(), before_source)
        self.assertEqual(Path(out).read_bytes(), before_new,
                         "之前那个新包不该被继续写")

    def test_loose_import_queue_targets_origin_pack(self):
        """严格模式存过新包后再切宽松：导入的布局也进原包。"""
        out = str(self.root / "interface_edited.fls")
        self._save(output=out)
        self._switch("loose")
        local = self._local("ui/q.dlg", "Q")
        self._import([(local, "q/q.dlg")])
        self._save()
        self.assertEqual(self.asked, [])
        self.assertEqual(self.warnings, [])
        with FlsPack(self.src) as pack:
            self.assertTrue(pack.contains("q/q.dlg"))
        with FlsPack(out) as pack:
            self.assertFalse(pack.contains("q/q.dlg"),
                             "之前的新包不该被写")

    def test_front_source_hint_changes_with_mode(self):
        from ui_editor.ui.status_text import place_hint, place_text

        doc = self.window.doc
        self.assertIn("来源只读", place_hint(doc))
        self.assertIn("宽松模式", place_hint(doc, loose=True))
        self.assertIn("直接改写原包", place_hint(doc, loose=True))
        self.assertIn("原地写回", place_text(doc, loose=True))


if __name__ == "__main__":
    unittest.main()
