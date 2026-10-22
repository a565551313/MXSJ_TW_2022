"""保存去向：Ctrl+S 记住输出包、不再叠 _patched、不碰源包；文件名/状态栏。

背景（0.14.0）：旧版包内布局按 Ctrl+S 会弹「存回资源包 / 另存为散装」，
选了「存回」还要再选一次路径；默认名是「当前来源包名 + _patched」，
而第一次保存后来源变成了新包，于是连续保存得到
``interface_patched_patched_patched.fls``（实测）。这里锁住新行为：

* 第一次问一次路径（默认 ``<原包名>_edited.fls``），之后静默写回同一个包；
* 输出包是编辑器自己的，允许被下次保存覆盖；游戏原包永远拒绝；
* 标题栏与状态栏都要写清「来源只读 / Ctrl+S 写到哪里」。
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication

    from ui_editor.core.assets import AssetResolver
    from ui_editor.ui.main_window import MainWindow
    from ui_editor.ui.status_text import place_hint, place_text, window_title

    HAS_QT = True
except ImportError:
    HAS_QT = False

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_gui import _mini_pack_bytes  # noqa: E402  (复用微型包构造)


def _layout_title(pack: Path, res_path: str = "dialog/cateroom.dlg"):
    """从包里回读这篇布局的 sTitle（用全新解析器，避免读缓存）。"""
    resolver = AssetResolver()
    resolver.mount_pack(str(pack))
    try:
        got = resolver.fetch_pack_dlg(str(pack), res_path)
        return None if got is None else got[0][0].get("sTitle")
    finally:
        resolver.close()


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class SaveTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.window = MainWindow()
        self.src = self.root / "interface.fls"
        self.src.write_bytes(_mini_pack_bytes("dialog/cateroom.dlg"))
        self.window.open_pack_file(str(self.src))
        self.window._open_pack_layout(str(self.src), "dialog/cateroom.dlg")
        self.assertIsNotNone(self.window.doc)
        self.asked: list[str] = []
        self.reviews: list[int] = []
        self.infos: list[tuple[str, str]] = []

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    # -- 工具 ---------------------------------------------------------
    def _patch_save(self, *, warnings=None, answers=None):
        """拦掉文件框与所有模态弹窗，返回 ExitStack 给 ``with`` 用。

        漏掉任何一个 ``QMessageBox`` 都会在 offscreen 下真弹模态框——
        测试会挂在这里而不是失败，所以四个入口一次全盖住。
        """
        import contextlib

        def fake_dialog(_parent, _title, default, *_args, **_kwargs):
            self.asked.append(default)
            if answers is None:
                return default, ""
            return answers.pop(0), ""

        def fake_warning(_parent, title, text, *_args, **_kwargs):
            if warnings is not None:
                warnings.append((title, text))
            return None

        def fake_review(_dialog):
            self.reviews.append(1)
            return 1

        def fake_info(_parent, title, text, *_args, **_kwargs):
            self.infos.append((title, text))

        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch(
            "ui_editor.ui.save_workflows.QFileDialog.getSaveFileName",
            fake_dialog))
        stack.enter_context(mock.patch(
            "ui_editor.ui.save_workflows.SaveReviewDialog.exec",
            fake_review))
        stack.enter_context(mock.patch(
            "ui_editor.ui.save_workflows.QMessageBox.information", fake_info))
        stack.enter_context(mock.patch(
            "ui_editor.ui.save_workflows.QMessageBox.warning", fake_warning))
        return stack

    def _edit(self, title: str) -> None:
        self.window.doc.roots[0].props["sTitle"] = title
        self.window.doc.dirty = True

    # -- 断言 ---------------------------------------------------------
    def test_save_asks_once_then_writes_silently(self):
        with self._patch_save():
            self._edit("第一次")
            self.window.save()
            self.assertEqual(len(self.asked), 1, "第一次保存应该问一次路径")
            self.assertEqual(Path(self.asked[0]).name, "interface_edited.fls")

            self._edit("第二次")
            self.window.save()
            self.assertEqual(len(self.asked), 1, "第二次保存不该再问路径")

        out = Path(self.window.doc.output_pack)
        self.assertTrue(out.is_file())
        self.assertEqual(_layout_title(out), "第二次")
        # 目录里只有原包与一个输出包：不再产生 _patched 尾巴
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["interface.fls", "interface_edited.fls"])

    def test_after_first_save_everything_is_silent(self):
        """第一次问路径 + 看一次清单；之后 Ctrl+S 不弹任何框。"""
        with self._patch_save():
            self._edit("第一次")
            self.window.save()
            self.assertEqual(len(self.asked), 1)
            self.assertEqual(len(self.reviews), 1, "第一次保存看一次清单")
            first = self.window.statusBar().currentMessage()
            self.assertIn("已写回", first)
            self.assertIn("不再询问", first)

            self._edit("第二次")
            self.window.save()
            self.assertEqual(len(self.asked), 1, "不再问路径")
            self.assertEqual(len(self.reviews), 1, "不再弹保存清单")
            self.assertEqual(self.infos, [], "成功后不该再弹模态框")
            second = self.window.statusBar().currentMessage()
            self.assertIn("已写回", second)
            self.assertNotIn("不再询问", second)

    def test_second_save_reports_in_place_not_fake_zero(self):
        """同一文件原地写回时，不能拿「写前的自己」比出「改变 0 条」。"""
        with self._patch_save():
            self._edit("第一次")
            self.window.save()
            self._edit("第二次")
            self.window.save()
        msg = self.window.statusBar().currentMessage()
        self.assertIn("就地写回", msg)
        self.assertNotIn("改变 0 条", msg)

    def test_output_name_does_not_stack_suffixes(self):
        with self._patch_save():
            self._edit("第一次")
            self.window.save()
        self.assertEqual(Path(self.window._default_output_pack()).name,
                         "interface_edited2.fls",
                         "另存为的默认名要绕过已有的输出包，不能叠 _patched")

    def test_second_save_keeps_one_output_pack(self):
        with self._patch_save():
            for i in range(3):
                self._edit(f"第{i}次")
                self.window.save()
        names = sorted(p.name for p in self.root.glob("*.fls"))
        self.assertEqual(len(names), 2, names)
        self.assertEqual(_layout_title(Path(self.window.doc.output_pack)), "第2次")

    def test_save_refuses_the_source_pack(self):
        warnings: list[str] = []
        with self._patch_save(warnings=warnings):
            before = self.src.read_bytes()
            self._edit("改成源包")
            self.assertFalse(self.window._save_to_pack(str(self.src)))
        self.assertEqual(self.src.read_bytes(), before, "源包一个字节都不能动")
        self.assertTrue(warnings, "至少要弹一次拒绝原因")
        self.assertIn("拒绝", warnings[-1][1])

    def test_title_and_status_name_source_and_target(self):
        self.assertIn("还没写回新包", self.window.windowTitle())
        self.assertIn("interface.fls", self.window._source_label.text())
        self.assertIn("第一次 Ctrl+S", self.window._source_label.text())

        with self._patch_save():
            self._edit("第一次")
            self.window.save()

        self.assertIn("interface.fls → interface_edited.fls",
                      self.window.windowTitle())
        hint = self.window._source_label.text()
        self.assertIn("来源只读：interface.fls", hint)
        self.assertIn("Ctrl+S 写回：interface_edited.fls", hint)

    def test_status_text_pure_functions(self):
        class Doc:
            source_pack = ("D:/client/interface.fls", "dialog/a.dlg")
            output_pack = None
            source_path = None
            origin_pack = None
            display_name = "a.dlg"
            dirty = False
            pending_pack_import = False

        doc = Doc()
        self.assertEqual(place_text(doc),
                         "（interface.fls，还没写回新包）")
        self.assertIn("第一次 Ctrl+S", place_hint(doc))
        doc.output_pack = "D:/out/interface_edited.fls"
        doc.origin_pack = "D:/client/interface.fls"
        self.assertEqual(place_text(doc),
                         "（interface.fls → interface_edited.fls）")
        self.assertIn("Ctrl+S 写回：interface_edited.fls", place_hint(doc))
        self.assertIn("interface.fls → interface_edited.fls",
                      window_title(doc, "9.9.9"))


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class FileMenuShapeTests(unittest.TestCase):
    """文件菜单只有三段：打开 / 保存 / 导出副本，旧名不再出现。"""

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.file_menu = self.window._file_menu

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _items(self):
        return [a.text() for a in self.file_menu.actions() if a.text()]

    def test_no_duplicate_open_verbs(self):
        items = self._items()
        opens = [text for text in items if text.startswith("打开")]
        self.assertEqual(opens, ["打开"], items)
        self.assertNotIn("从资源包打开布局…", items)
        self.assertNotIn("从资源目录打开布局…", items)

    def test_three_groups_exist(self):
        items = self._items()
        for expected in ("打开", "保存（回到它来的地方）", "另存为", "导出副本"):
            self.assertIn(expected, items)

    def test_open_submenu_lists_four_sources(self):
        open_menu = self.window._open_menu
        sub = [a.text() for a in open_menu.actions() if a.text()]
        self.assertEqual(sub[0], "布局文件（.dlg）…")
        self.assertIn("布局目录（一个文件夹里的 .dlg）…", sub)
        self.assertIn("资源包（.fls，先挂到左边树）…", sub)
        self.assertIn("资源目录（整个客户端目录）…", sub)
        self.assertIn("最近打开", sub)

    def test_export_submenu_lists_three_copies(self):
        export_menu = self.window._export_menu
        sub = [a.text() for a in export_menu.actions() if a.text()]
        self.assertEqual(sub, ["布局原文件（.dlg 原字节）…",
                               "画布预览图（PNG）…",
                               "控件素材图片…"])


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class RecentOpenTests(unittest.TestCase):
    """「最近打开」：去重、限条数、文件没了就自动剔掉。"""

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from PySide6.QtCore import QSettings

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.window = MainWindow()
        # 用临时 ini，不碰用户真实的编辑器设置
        self.settings = QSettings(str(self.root / "settings.ini"),
                                  QSettings.Format.IniFormat)
        self.window._settings = self.settings

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self._tmp.cleanup()

    def test_roundtrip_dedupes_and_limits(self):
        for i in range(12):
            self.window._remember_recent("dlg", f"D:/layouts/a{i}.dlg")
        entries = self.window._recent_entries()
        self.assertEqual(len(entries), self.window.RECENT_LIMIT)
        self.assertEqual(entries[0], ("dlg", "D:/layouts/a11.dlg"))
        self.window._remember_recent("dlg", "D:/layouts/a11.dlg")
        self.assertEqual(self.window._recent_entries()[0],
                         ("dlg", "D:/layouts/a11.dlg"))
        self.assertEqual(len(self.window._recent_entries()),
                         self.window.RECENT_LIMIT)

    def test_missing_file_is_dropped_quietly(self):
        gone = self.root / "gone.dlg"
        self.window._remember_recent("dlg", str(gone))
        self.assertEqual(len(self.window._recent_entries()), 1)
        self.window.open_recent("dlg", str(gone))
        self.assertEqual(self.window._recent_entries(), [])
        self.assertIn("不在了", self.window.statusBar().currentMessage())

    def test_same_name_from_two_folders_is_distinguishable(self):
        self.window._remember_recent("dlg", "D:/a/interface.dlg")
        self.window._remember_recent("dlg", "D:/b/interface.dlg")
        from ui_editor.ui.file_menu import rebuild_recent_menu

        rebuild_recent_menu(self.window)
        texts = [a.text() for a in self.window._recent_menu.actions() if a.text()]
        self.assertIn("布局：interface.dlg（a）", texts)
        self.assertIn("布局：interface.dlg（b）", texts)

    def test_clear(self):
        self.window._remember_recent("pack", str(self.root / "x.fls"))
        self.window.clear_recent()
        self.assertEqual(self.window._recent_entries(), [])
