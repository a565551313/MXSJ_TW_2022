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
import sys
import tempfile
import unittest
from pathlib import Path
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
