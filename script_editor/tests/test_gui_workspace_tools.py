"""Workspace ergonomics: remembered searches, save-all, tab locks, backups.

Pinned here:

* the tree search box is the same history drop-down as the find bar, and its
  history is saved separately from the find history;
* 全部保存 writes every modified tab (locked tabs included);
* a locked tab survives 关闭全部文件 / 关闭左边文件 / 关闭右边文件, and is
  closed once it is unlocked;
* file dialogs start where the last one ended;
* 生成新包 keeps the original name *without* losing the old package: it becomes
  ``<name>_bak`` (one rolling copy);
* the diagnostics dock starts out twice as tall as it used to.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from native_fixtures import minimal_pyc, script_fixture
from test_gui import QT_ERROR

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import Compiler
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import CatalogRef
from script_editor.core.services.native_build import (
    BACKUP_RENAME_SUFFIX,
    install_over_source,
)

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication, QFileDialog

    from script_editor.gui.window import Window
    from script_editor.gui.workspace import SearchField


class FakeSettings:
    """Minimal QSettings stand-in that keeps values in a dict."""

    def __init__(self, values=None):
        self.values = dict(values or {})

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):  # noqa: N802 - Qt spelling
        self.values[key] = value


def sync(work, done, *, cancel=None, on_error=None, **_options):
    """Run a Window job inline, including its error path."""
    try:
        result = work()
    except Exception as exc:  # noqa: BLE001 - mirrors Window.task
        if on_error is not None:
            on_error(exc)
        return
    done(result)


class InstallOverSourceTests(unittest.TestCase):
    """Core: the same-name 生成新包 swap."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-install-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_the_old_package_becomes_underscore_bak(self):
        original = self.root / "a.fls"
        original.write_bytes(b"old-bytes")
        output = self.root / "a.fls.new"
        output.write_bytes(b"new-bytes")
        digest = hashlib.sha256(b"old-bytes").hexdigest()
        backup = install_over_source(original, output, expected_sha256=digest)
        self.assertEqual(backup.name, "a.fls" + BACKUP_RENAME_SUFFIX)
        self.assertEqual(backup.read_bytes(), b"old-bytes")
        self.assertEqual(original.read_bytes(), b"new-bytes")
        self.assertFalse(output.exists())

    def test_a_changed_original_is_refused(self):
        original = self.root / "b.fls"
        original.write_bytes(b"changed")
        output = self.root / "b.fls.new"
        output.write_bytes(b"new")
        with self.assertRaisesRegex(ValueError, "被改动"):
            install_over_source(
                original,
                output,
                expected_sha256=hashlib.sha256(b"original").hexdigest(),
            )
        self.assertEqual(original.read_bytes(), b"changed")
        self.assertTrue(output.exists())


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class TreeSearchHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_window(self, settings=None):
        temporary = tempfile.TemporaryDirectory(prefix="mx-tree-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        window = Window(root, settings=settings)
        self.addCleanup(self._close, window)
        return window

    def _close(self, window):
        for i in range(window.tabs.count()):
            window.tabs.widget(i).editor.document().setModified(False)
        window.project_dirty = False
        window.close()
        window.deleteLater()
        self.app.processEvents()

    def test_the_tree_filter_is_the_history_dropdown(self):
        window = self.make_window()
        self.assertIsInstance(window.filter, SearchField)
        self.assertEqual(window.filter.objectName(), "treeFilter")

    def test_enter_remembers_the_query(self):
        window = self.make_window()
        window.filter.setText("login")
        window.commit_filter_search()
        self.assertEqual(window.filter.history(), ["login"])
        window.filter.setText("mainpage")
        window.commit_filter_search()
        self.assertEqual(window.filter.history(), ["mainpage", "login"])

    def test_the_tree_history_is_separate_from_the_find_history(self):
        settings = FakeSettings(
            {"filter/history": ["tree-only"], "find/history": ["find-only"]}
        )
        window = self.make_window(settings)
        self.assertEqual(window.filter.history(), ["tree-only"])
        self.assertEqual(window.find.history(), ["find-only"])
        window.close()
        self.assertEqual(settings.values["filter/history"], ["tree-only"])

    def test_filtering_still_hides_non_matching_rows(self):
        raw, _catalog = script_fixture()
        temporary = tempfile.TemporaryDirectory(prefix="mx-tree-rows-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        package = root / "script.fls"
        package.write_bytes(raw)
        window = self.make_window()
        window.add_archive(ArchiveDocument(package))
        window.filter_tree("#1")
        hidden = [
            window.tree.topLevelItem(0).child(i).isHidden()
            for i in range(window.tree.topLevelItem(0).childCount())
        ]
        self.assertIn(False, hidden)
        self.assertIn(True, hidden)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class SaveAllTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-saveall-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.errors = []
        patch.object(self.window, "fail", self.errors.append).start()
        self.addCleanup(patch.stopall)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def tab(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return self.window.add_source(path, text=text)

    def test_every_modified_tab_is_written(self):
        first = self.tab("one.py", "A = 1\n")
        second = self.tab("two.py", "B = 2\n")
        first.editor.insertPlainText("A2 = 2\n")
        second.editor.insertPlainText("B2 = 3\n")
        self.window.save_all()
        self.assertEqual(self.errors, [])
        self.assertIn("A2", (self.root / "one.py").read_text(encoding="utf-8"))
        self.assertIn("B2", (self.root / "two.py").read_text(encoding="utf-8"))
        self.assertFalse(first.editor.document().isModified())
        self.assertFalse(second.editor.document().isModified())

    def test_clean_tabs_are_left_alone(self):
        clean = self.tab("clean.py", "C = 3\n")
        self.window.save_all()
        self.assertEqual(self.errors, [])
        self.assertEqual((self.root / "clean.py").read_text(encoding="utf-8"),
                         "C = 3\n")
        self.assertFalse(clean.editor.document().isModified())

    def test_save_all_is_on_the_toolbar_right_after_save(self):
        from PySide6.QtWidgets import QToolBar

        toolbar = self.window.findChild(QToolBar, "mainToolbar")
        texts = [a.iconText() or a.text() for a in toolbar.actions() if a.text()]
        self.assertEqual(texts[texts.index("保存") + 1], "全部保存")


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class TabLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-lock-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.window = Window(self.root)
        self.addCleanup(self._close)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def tab(self, name):
        path = self.root / name
        path.write_text("X = 1\n", encoding="utf-8")
        return self.window.add_source(path, text="X = 1\n")

    def test_a_locked_tab_survives_close_all(self):
        first, second = self.tab("a.py"), self.tab("b.py")
        self.window.set_tab_locked(first, True)
        self.window.close_all_tabs()
        self.assertEqual(self.window.tabs.count(), 1)
        self.assertIs(self.window.tabs.widget(0), first)
        self.assertIn("🔒", self.window.tabs.tabText(0))
        self.assertNotIn(second, [self.window.tabs.widget(0)])

    def test_unlocking_lets_it_close(self):
        first = self.tab("c.py")
        self.window.set_tab_locked(first, True)
        self.window.close_all_tabs()
        self.assertEqual(self.window.tabs.count(), 1)
        self.window.set_tab_locked(first, False)
        self.window.close_all_tabs()
        self.assertEqual(self.window.tabs.count(), 0)

    def test_closing_one_side_skips_locked_tabs(self):
        first, second, third = self.tab("d.py"), self.tab("e.py"), self.tab("f.py")
        self.window.set_tab_locked(second, True)
        self.window.close_side(2, left=True)  # close left of "f.py"
        remaining = [
            self.window.tabs.widget(i) for i in range(self.window.tabs.count())
        ]
        self.assertEqual(remaining, [second, third])
        self.assertIsNot(remaining[0], first)

    def test_closing_the_right_side(self):
        first, second, third = self.tab("g.py"), self.tab("h.py"), self.tab("i.py")
        self.window.close_side(0, left=False)  # close right of "g.py"
        self.assertEqual(self.window.tabs.count(), 1)
        self.assertIs(self.window.tabs.widget(0), first)
        self.assertNotIn(second.path, [self.window.tabs.widget(0).path])
        self.assertIsNot(third, self.window.tabs.widget(0))


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class DialogDirectoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-dirs-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.settings = FakeSettings()
        self.window = Window(self.root, settings=self.settings)
        self.addCleanup(self._close)
        self.packages = self.root / "packages"
        self.packages.mkdir()
        self.other = self.root / "elsewhere"
        self.other.mkdir()

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_a_chosen_file_teaches_the_next_dialog(self):
        chosen = self.packages / "a.fls"
        chosen.write_bytes(b"x")
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=(str(chosen), "")
        ) as dialog:
            self.assertEqual(
                self.window.ask_open_file("pack", "打开", "FLS (*.fls)"), str(chosen)
            )
        self.assertEqual(self.settings.values["dir/pack"], str(self.packages))
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=("", "")
        ) as dialog:
            self.window.ask_open_file("pack", "打开", "FLS (*.fls)")
        self.assertEqual(dialog.call_args.args[2], str(self.packages))

    def test_a_directory_dialog_is_remembered_too(self):
        with patch.object(
            QFileDialog, "getExistingDirectory", return_value=str(self.other)
        ):
            self.window.ask_open_dir("pack_dir", "打开脚本目录")
        self.assertEqual(self.settings.values["dir/pack_dir"], str(self.other))
        with patch.object(
            QFileDialog, "getExistingDirectory", return_value=""
        ) as dialog:
            self.window.ask_open_dir("pack_dir", "打开脚本目录")
        self.assertEqual(dialog.call_args.args[2], str(self.other))

    def test_cancelling_keeps_the_previous_directory(self):
        self.settings.values["dir/source"] = str(self.other)
        with patch.object(QFileDialog, "getOpenFileName", return_value=("", "")):
            self.assertFalse(self.window.ask_open_file("source", "打开", "*.py"))
        self.assertEqual(self.settings.values["dir/source"], str(self.other))


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class GenerateSameNameTests(unittest.TestCase):
    """生成新包 defaulting to the original name keeps the old bytes as _bak."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-samename-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.errors = []
        patch.object(self.window, "fail", self.errors.append).start()
        self.addCleanup(patch.stopall)
        self.window.add_archive(ArchiveDocument(self.package.path))
        self.window.catalogs = [self.package.catalog]
        self.window.bindings = self.package.bindings(self.root)
        self.window.compilers["py25"] = Compiler(
            Path(sys.executable), "py25", "unit-test", 64, "t"
        )

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_the_default_name_is_the_original(self):
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=("", "")
        ) as dialog:
            self.assertIsNone(self.window._ask_destination(self.window.archives[0]))
        self.assertEqual(dialog.call_args.args[2], str(self.package.path))

    def test_saving_under_the_original_name_backs_it_up(self):
        with (
            patch(COMPILE, fake_compile()),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch("script_editor.core.services.native_build.audit_standard"),
            patch.object(
                QFileDialog,
                "getSaveFileName",
                return_value=(str(self.package.path), ""),
            ),
            patch.object(self.window, "task", side_effect=sync),
        ):
            self.window.generate_new_package()
        self.assertEqual(self.errors, [])
        backup = self.package.path.with_name(
            self.package.path.name + BACKUP_RENAME_SUFFIX
        )
        self.assertEqual(backup.read_bytes(), self.package.before)
        self.assertNotEqual(self.package.path.read_bytes(), self.package.before)
        self.assertFalse(
            self.package.path.with_name(self.package.path.name + ".bak").exists()
        )
        text = self.window.info.toPlainText()
        self.assertIn("已生成新包", text)
        self.assertIn(backup.name, text)
        # The window kept working on a live document for the same path.
        self.assertEqual(
            [a.path for a in self.window.archives], [self.package.path]
        )

    def test_another_existing_file_is_still_refused(self):
        other = self.root / "someone-elses.fls"
        other.write_bytes(b"not mine")
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(other), "")
        ):
            with self.assertRaisesRegex(ValueError, "不会覆盖别的文件"):
                self.window._ask_destination(self.window.archives[0])
        self.assertEqual(other.read_bytes(), b"not mine")


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class DockHeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_the_diagnostics_dock_starts_twice_as_tall(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-dock-")
        self.addCleanup(temporary.cleanup)
        window = Window(Path(temporary.name))
        self.addCleanup(self._close, window)
        window.resize(1200, 900)
        window.show()
        self.app.processEvents()
        self.assertGreaterEqual(window.output_dock.height(), 300)

    def _close(self, window):
        window.close()
        window.deleteLater()
        self.app.processEvents()


def fake_compile(seed=5):
    """Compile stub: the exact pyc a pinned CPython would have produced."""

    def compile_standard(_compiler, _source, _filename, destination, protected=()):
        pyc = minimal_pyc("py25", seed)
        destination.write_bytes(pyc)
        return hashlib.sha256(pyc).hexdigest()

    return compile_standard


COMPILE = "script_editor.core.services.workflow.compile_standard"


class Package:
    """A synthetic script package plus the catalog that decodes it."""

    def __init__(self, root: Path, *, two_modules=True):
        raw, catalog = script_fixture(two_modules=two_modules)
        self.path = root / "script.fls"
        self.path.write_bytes(raw)
        self.before = raw
        self.digest = hashlib.sha256(raw).hexdigest()
        catalog_file = root / "catalog.json"
        catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
        self.catalog = CatalogRef(
            self.path,
            self.digest,
            catalog_file,
            hashlib.sha256(catalog_file.read_bytes()).hexdigest(),
        )

    def bindings(self, source_root: Path, indexes=(0,)):
        result = []
        with ArchiveDocument(self.path) as archive:
            for index in indexes:
                source = source_root / f"module{index}.py"
                source.write_text(f"VALUE = {index}\n", encoding="utf-8")
                result.append(
                    Binding(
                        self.path,
                        self.digest,
                        "py25",
                        index,
                        archive.entries[index].identity,
                        source.resolve(),
                        "",
                        "",
                        "authored",
                        "",
                    )
                )
        return result


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ReloadRetryTests(unittest.TestCase):
    """「重新读取」walks the whole open flow before calling a path gone."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-retry-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.window.add_archive(ArchiveDocument(self.package.path))

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_a_failed_quick_read_reruns_the_open_flow(self):
        from script_editor.gui import window as window_module

        original = window_module.ArchiveDocument
        calls = []

        def fail_first(path):
            calls.append(path)
            if len(calls) == 1:
                raise OSError("目录暂时读不出来")
            return original(path)

        with patch.object(window_module, "ArchiveDocument", side_effect=fail_first):
            self.window.reload_archives()
        self.assertEqual(len(calls), 2)  # quick read + the retry
        self.assertEqual(len(self.window.archives), 1)
        self.assertIn("已重新读取 1 个包", self.window.info.toPlainText())

    def test_a_path_that_is_really_gone_is_reported_and_kept(self):
        self.package.path.unlink()
        self.window.reload_archives()
        # The row stays so the package can be renamed back and re-read; the
        # report says what happened, and 右键 → 移除文件 is the way to drop it.
        self.assertEqual(len(self.window.archives), 1)
        self.assertIn("读不到", self.window.info.toPlainText())
        self.window.remove_archive(self.window.archives[0])
        self.assertEqual(self.window.archives, [])
        self.assertEqual(self.window.tree.topLevelItemCount(), 0)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ReviewFixTests(unittest.TestCase):
    """Regressions for the review of 0.6.0.dev16."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-review-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.settings = FakeSettings()
        self.window = Window(self.root, settings=self.settings)
        self.addCleanup(self._close)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def tab(self, name, text="X = 1\n"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return self.window.add_source(path, text=text)

    # -- 标签右键：QTabWidget 没有 tabAt -------------------------------
    def test_a_click_on_a_tab_is_resolved_to_that_tab(self):
        first, second = self.tab("a.py"), self.tab("b.py")
        self.window.resize(900, 600)
        self.window.show()
        self.app.processEvents()
        bar = self.window.tabs.tabBar()
        point = self.window.tabs.mapFromGlobal(
            bar.mapToGlobal(bar.tabRect(0).center())
        )
        # QTabWidget has no tabAt; this used to raise AttributeError.
        self.assertEqual(self.window.tab_index_at(point), 0)
        self.assertIs(self.window.tabs.widget(0), first)
        self.assertIsNot(second, first)

    def test_a_click_outside_the_tab_bar_finds_nothing(self):
        self.tab("c.py")
        self.window.resize(900, 600)
        self.window.show()
        self.app.processEvents()
        self.assertEqual(
            self.window.tab_index_at(self.window.tabs.rect().bottomRight()), -1
        )

    def menu_texts(self, tab):
        return [a.text() for a in self.window.tab_menu_for(tab).actions() if a.text()]

    def test_the_tab_menu_lists_the_promised_entries(self):
        first = self.tab("d.py")
        texts = self.menu_texts(first)
        self.assertEqual(
            texts,
            [
                "关闭当前文件",
                "关闭左边文件",
                "关闭右边文件",
                "关闭全部文件",
                "锁定文件",
                "保存",
                "另存为…",
                "全部保存",
            ],
        )
        self.window.set_tab_locked(first, True)
        texts = self.menu_texts(first)
        self.assertIn("解锁文件", texts)
        self.assertNotIn("锁定文件", texts)

    # -- 对话框目录 --------------------------------------------------
    def test_a_bare_suggestion_is_joined_onto_the_remembered_directory(self):
        target = self.root / "out"
        target.mkdir()
        self.settings.values["dir/source_save_as"] = str(target)
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=("", "")
        ) as dialog:
            self.window.ask_save_file(
                "source_save_as", "另存为", "draft.py", "Python (*.py)"
            )
        self.assertEqual(dialog.call_args.args[2], str(target / "draft.py"))

    def test_an_absolute_suggestion_wins(self):
        other = self.root / "elsewhere"
        other.mkdir()
        suggestion = self.root / "packages" / "a.fls"
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=("", "")
        ) as dialog:
            self.window.ask_save_file("pack", "生成新包", str(suggestion), "*.fls")
        self.assertEqual(dialog.call_args.args[2], str(suggestion))
        self.assertEqual(other.name, "elsewhere")

    def test_a_directory_with_a_dot_keeps_its_own_path(self):
        dotted = self.root / "MX.2022"
        dotted.mkdir()
        with patch.object(
            QFileDialog, "getExistingDirectory", return_value=str(dotted)
        ):
            self.window.ask_open_dir("pack_dir", "打开脚本目录")
        self.assertEqual(self.settings.values["dir/pack_dir"], str(dotted))

    # -- 移除文件 ----------------------------------------------------
    def test_removal_is_refused_while_a_job_runs(self):
        raw, _catalog = script_fixture()
        package = self.root / "script.fls"
        package.write_bytes(raw)
        self.window.add_archive(ArchiveDocument(package))
        self.window.jobs.add(object())
        self.window.remove_archive(self.window.archives[0])
        self.assertEqual(len(self.window.archives), 1)
        self.assertEqual(self.window.tree.topLevelItemCount(), 1)
        self.window.jobs.clear()

    def test_cancelling_a_prompt_aborts_the_removal(self):
        raw, _catalog = script_fixture()
        package = self.root / "script.fls"
        package.write_bytes(raw)
        archive = ArchiveDocument(package)
        self.window.add_archive(archive)
        tab = self.tab("draft.py")
        tab.recovery = SimpleNamespace(current_archive=package.resolve())
        tab.editor.insertPlainText("# dirty\n")
        with patch.object(self.window, "confirm_tab", return_value=False):
            self.window.remove_archive(archive)
        self.assertEqual(len(self.window.archives), 1)
        self.assertEqual(self.window.tree.topLevelItemCount(), 1)
        self.assertEqual(self.window.tabs.count(), 1)

    # -- 全部保存的可用性 --------------------------------------------
    def test_save_all_stays_enabled_behind_a_reference_tab(self):
        self.tab("d.py").editor.insertPlainText("# dirty\n")
        reference = self.tab("ref.py", "R = 1\n")
        reference.reference = True
        self.window.tabs.setCurrentWidget(reference)
        self.window.workspace_refresh()
        self.assertTrue(self.window.ui_actions["save_all"].isEnabled())
        self.assertFalse(self.window.ui_actions["save"].isEnabled())

    def test_save_all_is_disabled_when_nothing_is_dirty(self):
        self.tab("e.py")
        self.window.workspace_refresh()
        self.assertFalse(self.window.ui_actions["save_all"].isEnabled())


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class SameNameStateTests(unittest.TestCase):
    """After a same-name 生成新包 the workspace must know the final path."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-state-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.errors = []
        patch.object(self.window, "fail", self.errors.append).start()
        self.addCleanup(patch.stopall)
        self.window.add_archive(ArchiveDocument(self.package.path))
        self.window.catalogs = [self.package.catalog]
        self.window.bindings = self.package.bindings(self.root)
        self.window.compilers["py25"] = Compiler(
            Path(sys.executable), "py25", "unit-test", 64, "t"
        )

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def run_same_name(self):
        with (
            patch(COMPILE, fake_compile()),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch("script_editor.core.services.native_build.audit_standard"),
            patch.object(
                QFileDialog,
                "getSaveFileName",
                return_value=(str(self.package.path), ""),
            ),
            patch.object(self.window, "task", side_effect=sync),
        ):
            self.window.generate_new_package()

    def test_bindings_follow_the_file_to_its_final_name(self):
        self.run_same_name()
        self.assertEqual(self.errors, [])
        final = self.package.path.resolve()
        self.assertEqual([b.archive for b in self.window.bindings], [final])
        self.assertEqual([c.archive for c in self.window.catalogs], [final])
        # The next write finds them: this is what used to fail with
        # "这个包还没有可写源码".
        archive = self.window.archives[0]
        self.assertIsNotNone(self.window.catalog_for(archive))

    def test_a_refused_swap_leaves_no_hidden_staging_package(self):
        def refuse(*_args, **_kwargs):
            raise ValueError("原包在保存期间被改动")

        with patch("script_editor.gui.write_package.install_over_source", refuse):
            self.run_same_name()
        stale = [
            path.name
            for path in self.root.iterdir()
            if ".generating-" in path.name
        ]
        self.assertEqual(stale, [])
        self.assertEqual(self.package.path.read_bytes(), self.package.before)


class BackupDigestTests(unittest.TestCase):
    """install_over_source re-checks the bytes it is about to keep."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-bakdigest-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_an_unreadable_backup_is_put_back_before_failing(self):
        from script_editor.core.services import native_build

        source = self.root / "a.fls"
        source.write_bytes(b"old")
        output = self.root / "new.fls"
        output.write_bytes(b"new")
        digest = hashlib.sha256(b"old").hexdigest()
        calls = {"n": 0}

        def flaky(path):
            calls["n"] += 1
            if calls["n"] == 1:
                return digest
            raise PermissionError("被索引器锁住")

        with patch.object(native_build, "_sha256_file", flaky):
            with self.assertRaises(PermissionError):
                native_build.install_over_source(source, output, expected_sha256=digest)
        # The package name is never left empty: the bytes are back where they were.
        self.assertEqual(source.read_bytes(), b"old")
        self.assertFalse(
            source.with_name(source.name + BACKUP_RENAME_SUFFIX).exists()
        )
        self.assertTrue(output.is_file())

    def test_a_copy_that_changed_during_the_rename_is_put_back(self):
        from script_editor.core.services import native_build

        source = self.root / "a.fls"
        source.write_bytes(b"old")
        output = self.root / "new.fls"
        output.write_bytes(b"new")
        digest = hashlib.sha256(b"old").hexdigest()
        real = native_build._sha256_file
        calls = {"n": 0}

        def flaky(path):
            calls["n"] += 1
            return digest if calls["n"] == 1 else hashlib.sha256(b"other").hexdigest()

        with patch.object(native_build, "_sha256_file", flaky):
            with self.assertRaisesRegex(ValueError, "备份期间被改动"):
                native_build.install_over_source(source, output, expected_sha256=digest)
        self.assertTrue(source.is_file())
        self.assertEqual(source.read_bytes(), b"old")
        self.assertTrue(output.is_file())
        self.assertEqual(calls["n"], 2)
        self.assertIs(real, native_build._sha256_file)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class UnsavedDraftTests(unittest.TestCase):
    """A draft with no file behind it must still prompt before closing."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-unsaved-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        patcher = patch.dict(os.environ, {"MXSCRIPT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.window = Window(self.root)
        self.addCleanup(self._close)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def draft(self, *, complete=True):
        raw, _catalog = script_fixture()
        package = self.root / "script.fls"
        package.write_bytes(raw)
        archive = ArchiveDocument(package)
        self.window.add_archive(archive)
        text = "# coding: utf-8\nVALUE = 1\n"
        tab = self.window.add_source(
            self.root / "draft.py",
            text=text,
            source_kind="recovered-draft",
            vm="py25",
        )
        tab.draft_saved = False
        report = SimpleNamespace(
            source=text, complete=complete, archive=package, index=0,
            filename_hex=b"authored.py".hex(),
        )
        return tab, archive, report

    def test_no_compiler_means_the_text_is_still_unsaved(self):
        tab, archive, report = self.draft()
        self.assertFalse(self.window.auto_adopt(tab, archive, 0, report))
        self.assertTrue(tab.editor.document().isModified())
        self.assertEqual(tab.binding_state, "no-compiler")

    def test_an_incomplete_recovery_counts_as_unsaved(self):
        tab, archive, report = self.draft(complete=False)
        self.assertFalse(self.window.auto_adopt(tab, archive, 0, report))
        self.assertTrue(tab.editor.document().isModified())

    def test_a_failed_verification_counts_as_unsaved(self):
        from script_editor.core.compiler.runner import Compiler

        tab, archive, report = self.draft()
        self.window.compilers["py25"] = Compiler(
            Path(sys.executable), "py25", "unit-test", 64, "t"
        )

        def boom(*_args, **_kwargs):
            raise ValueError("编译失败")

        with patch(
            "script_editor.gui.module_actions.inspect_module", boom
        ), patch.object(self.window, "task", side_effect=sync):
            self.window.auto_adopt(tab, archive, 0, report)
        self.assertEqual(tab.binding_state, "failed")
        self.assertTrue(tab.editor.document().isModified())
