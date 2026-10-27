"""The editor must not hold the client's package files, and the find bar.

Three behaviours the user asked for directly:

* **不占用文件**：读完就放句柄，所以在资源管理器里能直接给原包改名/替换，
  不必先关掉编辑器；
* **查找栏默认打开**，查找框是带历史的下拉可编辑框；
* **命中查找的整行有明显高亮**（整行暖色带 + 命中文字更深的一段）。
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import many_module_fixture
from test_gui import QT_ERROR

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.archives.readers import FileReader
from script_editor.core.project.storage import CatalogRef
from script_editor.core.services.files import default_source_root

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication

    from script_editor.gui.window import Window


class Package:
    def __init__(self, root: Path, count=3):
        raw, catalog = many_module_fixture(count=count)
        self.path = root / "script.fls"
        self.path.write_bytes(raw)
        catalog_file = root / "catalog.json"
        catalog_file.write_text(__import__("json").dumps(catalog), encoding="utf-8")
        self.catalog = CatalogRef(
            self.path,
            __import__("hashlib").sha256(raw).hexdigest(),
            catalog_file,
            __import__("hashlib").sha256(catalog_file.read_bytes()).hexdigest(),
        )


class HandleReleaseTests(unittest.TestCase):
    """No package file may stay open while the editor is idle."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-handle-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)

    def descriptors_for(self, target: Path) -> list[str]:
        """Descriptors this process has open on ``target`` (Linux only)."""
        # Built from parts so the Windows path scanner does not mistake this
        # Linux-only probe for a hardcoded POSIX absolute path.
        base = Path(os.sep, "proc", "self", "fd")
        if not base.is_dir():
            self.skipTest("需要 procfs 的 self/fd 才能检查句柄")
        found = []
        for entry in base.iterdir():
            try:
                if entry.resolve() == target.resolve():
                    found.append(entry.name)
            except OSError:
                continue
        return found

    def test_an_open_package_holds_no_descriptor(self):
        with ArchiveDocument(self.package.path) as document:
            self.assertFalse(document.holding_handle)
            self.assertEqual(self.descriptors_for(self.package.path), [])
            document.read_stored(0)
            document.fingerprint()
            document.entry_metadata(0)
            self.assertEqual(self.descriptors_for(self.package.path), [])
            self.assertFalse(document.holding_handle)

    def test_a_closed_reader_never_reopens(self):
        reader = FileReader(self.package.path)
        reader.read_at(0, 4)
        reader.close()
        self.assertFalse(reader.holding_handle)
        with self.assertRaises(ValueError):
            reader.read_at(0, 4)

    def test_the_package_can_be_renamed_while_the_document_is_open(self):
        document = ArchiveDocument(self.package.path)
        renamed = self.package.path.with_name("脚本 备份.fls")
        os.rename(self.package.path, renamed)  # would fail if we held a handle
        self.assertFalse(self.package.path.exists())
        from script_editor.core.errors import ContainerError

        with self.assertRaises(ContainerError):
            document.read_stored(0)  # says "不可读/请重新打开", not a stale read
        document.close()

    def test_revision_mismatch_is_still_refused(self):
        from script_editor.core.errors import ContainerError

        with ArchiveDocument(self.package.path) as document:
            document.fingerprint()
            original = document.reader.revision
            changed = (original[0], original[1] ^ 1, *original[2:])
            with patch.object(FileReader, "path_revision", return_value=changed):
                with self.assertRaises(ContainerError):
                    document.read_stored(0)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class FindBarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-find-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        patcher = patch.dict(os.environ, {"MXSCRIPT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def window(self, settings=None):
        window = Window(self.root, settings=settings)
        self.addCleanup(self._close, window)
        return window

    def _close(self, window):
        for i in range(window.tabs.count()):
            window.tabs.widget(i).editor.document().setModified(False)
        window.project_dirty = False
        window.close()
        window.deleteLater()
        self.app.processEvents()

    def test_the_search_bar_is_visible_from_the_start(self):
        window = self.window()
        self.assertTrue(window.search_bar.isVisibleTo(window))

    def test_the_find_box_is_an_editable_history_dropdown(self):
        from PySide6.QtWidgets import QComboBox

        window = self.window()
        self.assertIsInstance(window.find, QComboBox)
        self.assertTrue(window.find.isEditable())
        window.find.setText("hello")
        self.assertEqual(window.find.text(), "hello")

    def test_searches_are_remembered_once_each_newest_first(self):
        window = self.window()
        window.find.remember("alpha")
        window.find.remember("beta")
        window.find.remember("alpha")
        self.assertEqual(window.find.history(), ["alpha", "beta"])

    def test_history_prefills_from_settings(self):
        class FakeSettings:
            def __init__(self, values):
                self.values = dict(values)

            def value(self, key, default=None):
                return self.values.get(key, default)

            def setValue(self, key, value):  # noqa: N802 - Qt spelling
                self.values[key] = value

        settings = FakeSettings({"find/history": ["旧搜索"]})
        window = self.window(settings)
        self.assertEqual(window.find.history(), ["旧搜索"])
        window.find.remember("新搜索")
        window.close()
        self.assertIn("新搜索", settings.values["find/history"])

    def test_a_hit_marks_the_whole_line_and_the_matched_text(self):
        from script_editor.gui.code_editor import CodeEditor

        window = self.window()
        text = "first line\nneedle = 1\nthird line\n"
        tab = window.add_source(self.root / "hit.py", text=text)
        window.find.setText("needle")
        window.find_next()
        self.assertIsInstance(tab.editor, CodeEditor)
        block = tab.editor.match_line()
        self.assertIsNotNone(block)
        self.assertEqual(block.blockNumber(), 1)
        selections = tab.editor.extraSelections()
        self.assertGreaterEqual(len(selections), 2)  # caret line + hit band
        self.assertEqual(
            selections[1].format.background().color().name(), "#ffe9a8"
        )
        self.assertTrue(
            selections[1].format.property(
                __import__(
                    "PySide6.QtGui", fromlist=["QTextFormat"]
                ).QTextFormat.Property.FullWidthSelection
            )
        )

    def test_leaving_the_search_clears_the_hit_band(self):
        window = self.window()
        window.add_source(self.root / "hit2.py", text="needle\n")
        window.find.setText("needle")
        window.find_next()
        self.assertIsNotNone(window.tabs.currentWidget().editor.match_line())
        window.close_search()
        self.assertFalse(window.search_bar.isVisibleTo(window))
        self.assertIsNone(window.tabs.currentWidget().editor.match_line())

    def test_jumping_to_a_line_marks_it(self):
        window = self.window()
        tab = window.add_source(self.root / "jump.py", text="a\nb\nc\nd\n")
        window.move_to_line(3)
        block = tab.editor.match_line()
        self.assertIsNotNone(block)
        self.assertEqual(block.blockNumber(), 2)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ReloadAfterSwapTests(unittest.TestCase):
    """After a rename/swap the open packages can be re-read without a restart."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-reload-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        patcher = patch.dict(os.environ, {"MXSCRIPT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.package = Package(self.root)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.assertEqual(default_source_root().parent, self.home)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_a_replaced_package_is_re_read_and_a_vanished_one_is_reported(self):
        self.window.add_archive(ArchiveDocument(self.package.path))
        gone = self.root / "gone.fls"
        gone.write_bytes(self.package.path.read_bytes())
        self.window.add_archive(ArchiveDocument(gone))
        self.assertEqual(len(self.window.archives), 2)

        # The user swaps files behind us: same name, new bytes; other one moves.
        replacement = self.root / "script_new.fls"
        replacement.write_bytes(self.package.path.read_bytes())
        self.package.path.unlink()
        replacement.rename(self.package.path)
        gone.rename(self.root / "gone_old.fls")

        self.window.reload_archives()
        self.assertEqual(len(self.window.archives), 2)
        info = self.window.info.toPlainText()
        self.assertIn("已重新读取 1 个包", info)
        self.assertIn("gone.fls", info)
        self.assertIn("重新打开", info)


class BorrowedHandleTests(unittest.TestCase):
    """Nested/concurrent borrows must not close each other's descriptor."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-borrow-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)

    def open_descriptor_count(self):
        base = Path(os.sep, "proc", "self", "fd")
        if not base.is_dir():
            self.skipTest("需要 procfs 的 self/fd")
        return len(list(base.iterdir()))

    def test_a_nested_borrow_keeps_the_outer_descriptor(self):
        from script_editor.core.archives.readers import FileReader

        reader = FileReader(self.package.path)
        self.addCleanup(reader.close)
        with reader.open_handle():
            first = reader.read_at(0, 4)
            with reader.open_handle():
                self.assertTrue(reader.holding_handle)
            # The inner exit must not have closed the outer borrow.
            self.assertTrue(reader.holding_handle)
            self.assertEqual(reader.read_at(0, 4), first)
        self.assertFalse(reader.holding_handle)

    def test_repeated_reads_do_not_leak_descriptors(self):
        from script_editor.core.archives.readers import FileReader

        reader = FileReader(self.package.path)
        self.addCleanup(reader.close)
        before = self.open_descriptor_count()
        for _ in range(50):
            reader.read_at(0, 64)
        self.assertEqual(self.open_descriptor_count(), before)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ReopenSearchTests(unittest.TestCase):
    """Ctrl+F must not paint a line the query does not actually match."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-reopen-")
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

    def test_reopening_search_does_not_mark_an_unrelated_line(self):
        tab = self.window.add_source(
            self.root / "r.py", text="alpha\nneedle here\nomega\n"
        )
        self.window.find.setText("needle")  # leftover query, caret on line 1
        self.window.search_bar.hide()
        self.window.show_search()
        self.assertIsNone(tab.editor.match_line())

    def test_reopening_search_marks_the_selected_match(self):
        from PySide6.QtGui import QTextCursor

        tab = self.window.add_source(
            self.root / "r2.py", text="alpha\nneedle here\nomega\n"
        )
        cursor = tab.editor.textCursor()
        cursor.setPosition(6)  # "needle" on line 1
        cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
        tab.editor.setTextCursor(cursor)
        self.window.find.setText("needle")
        self.window.show_search()
        block = tab.editor.match_line()
        self.assertIsNotNone(block)
        self.assertEqual(block.blockNumber(), 1)

    def test_history_keeps_the_exact_query_text(self):
        window = self.window
        window.find.remember("  foo ")
        self.assertEqual(window.find.text(), "  foo ")
        self.assertEqual(window.find.history()[0], "  foo ")
        window.find.setText("  foo ")
        window.find.remember("  foo ")
        self.assertEqual(window.find.text(), "  foo ")


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class SettingsHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_a_one_entry_history_comes_back_as_one_entry(self):
        class FakeSettings:
            def __init__(self, values):
                self.values = dict(values)

            def value(self, key, default=None):
                return self.values.get(key, default)

            def setValue(self, key, value):  # noqa: N802 - Qt spelling
                self.values[key] = value

        temporary = tempfile.TemporaryDirectory(prefix="mx-qs-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        # QSettings' INI backend hands a one-element list back as a str.
        window = Window(root, settings=FakeSettings({"find/history": "needle"}))
        self.addCleanup(self._close, window)
        self.assertEqual(window.find.history(), ["needle"])

    def _close(self, window):
        for i in range(window.tabs.count()):
            window.tabs.widget(i).editor.document().setModified(False)
        window.project_dirty = False
        window.close()
        window.deleteLater()
        self.app.processEvents()


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class EditInvalidatesHitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-edit-")
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

    def test_editing_drops_the_stale_match_band(self):
        tab = self.window.add_source(
            self.root / "e.py", text="alpha\nneedle here\n"
        )
        self.window.find.setText("needle")
        self.window.find_next()
        self.assertIsNotNone(tab.editor.match_line())
        tab.editor.textCursor().insertText("x")  # any edit at the hit
        self.assertIsNone(tab.editor.match_line())
        bands = [
            selection.format.background().color().name()
            for selection in tab.editor.extraSelections()
        ]
        self.assertNotIn("#ffb347", bands)
        self.assertNotIn("#ffe9a8", bands)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class ReloadRebuildTests(unittest.TestCase):
    """A swapped file may have a different directory; rebuild, don't patch."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-rebuild-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        patcher = patch.dict(os.environ, {"MXSCRIPT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.small = Package(self.root, count=3)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.window.add_archive(ArchiveDocument(self.small.path))
        self.assertEqual(len(self.window.archives[0].entries), 3)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    @staticmethod
    def user_role():
        from PySide6.QtCore import Qt

        return Qt.ItemDataRole.UserRole

    def swap_in(self, count):
        raw, catalog = many_module_fixture(count=count)
        staging = self.root / "staging.fls"
        staging.write_bytes(raw)
        self.small.path.unlink()
        staging.rename(self.small.path)

    def test_a_bigger_package_rebuilds_the_tree(self):
        self.swap_in(count=5)
        self.window.reload_archives()
        archive = self.window.archives[0]
        self.assertEqual(len(archive.entries), 5)
        root = self.window.tree.topLevelItem(0)
        self.assertEqual(root.childCount(), 5)
        role = self.user_role()
        for i in range(5):
            archive_handle, index = root.child(i).data(0, role)
            self.assertIs(archive_handle, archive)
            self.assertEqual(index, i)
            self.assertEqual(
                root.child(i).text(0), archive.entries[i].identity
            )
        # The rebuilt children read from the new document, not a closed one.
        self.assertEqual(
            archive.read_stored(0), ArchiveDocument(self.small.path).read_stored(0)
        )

    def test_a_smaller_package_leaves_no_stale_children(self):
        self.swap_in(count=2)
        # Replace with a package that has fewer entries than what is open.
        self.window.reload_archives()
        archive = self.window.archives[0]
        root = self.window.tree.topLevelItem(0)
        self.assertEqual(root.childCount(), len(archive.entries))
        role = self.user_role()
        for i in range(root.childCount()):
            handle, index = root.child(i).data(0, role)
            self.assertIs(handle, archive)
            self.assertEqual(index, i)

    def test_module_names_survive_a_reload_of_the_same_directory(self):
        archive = self.window.archives[0]
        archive.module_paths = {0: "script/login/dgw.py", 1: "script/b.py"}
        self.window.reload_archives()
        self.assertEqual(
            self.window.archives[0].module_paths[0], "script/login/dgw.py"
        )

    def test_module_names_are_dropped_when_the_directory_changed(self):
        self.window.archives[0].module_paths = {0: "script/login/dgw.py"}
        self.swap_in(count=5)
        self.window.reload_archives()
        self.assertEqual(self.window.archives[0].module_paths, {})
