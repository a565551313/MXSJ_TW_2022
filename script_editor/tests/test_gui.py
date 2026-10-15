from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fixtures import data_bytes, script_bytes

QT_ERROR = ""
try:
    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtGui import QTextCursor
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QMessageBox, QToolBar, QTreeWidgetItem

except ImportError as exc:
    QT_ERROR = str(exc)

if not QT_ERROR:
    from script_editor.gui.window import Window


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-gui-")
        self.root = Path(self.temp.name)
        self.window = Window(self.root)
        self.source = self.root / "test.py"
        self.source.write_text("x = 1\n", encoding="utf-8")

    def tearDown(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_large_tree_uses_supported_qt_without_none_reference_corruption(self):
        from PySide6 import __version__ as qt_version

        from script_editor import GUI_VERSION

        self.assertEqual(qt_version, GUI_VERSION)
        # Reproduces the 6.12.0 / Python3.11 failure without touching game data.
        root = QTreeWidgetItem(["6000 records"])
        for i in range(6000):
            child = QTreeWidgetItem([str(i)])
            child.setData(0, Qt.ItemDataRole.UserRole, ("record", i))
            root.addChild(child)
        self.assertEqual(root.childCount(), 6000)

    def test_package_selector_switches_independent_vm_without_rebinding_source(self):
        self.test_two_archives_have_separate_identity_and_vm()
        self.window.add_source(self.source)
        original_vm = self.window.current().vm.currentData()
        self.window.archive_selector.setCurrentIndex(2)
        self.assertTrue(self.window.tree.topLevelItem(0).isHidden())
        self.assertFalse(self.window.tree.topLevelItem(1).isHidden())
        self.assertEqual(self.window.selected_archive().vm, "py27")
        self.assertEqual(self.window.current().vm.currentData(), original_vm)
        self.assertFalse(self.window.native_action.isEnabled())
        self.window.archive_selector.setCurrentIndex(0)
        self.assertFalse(self.window.tree.topLevelItem(0).isHidden())

    def test_workspace_toolbar_shares_real_actions_and_welcome(self):
        toolbar = self.window.findChild(QToolBar, "mainToolbar")
        self.assertIn(self.window.native_action, toolbar.actions())
        self.assertIs(self.window.pages.currentWidget(), self.window.welcome)
        self.assertFalse(self.window.ui_actions["save"].isEnabled())
        self.window.add_source(self.source)
        self.assertIs(self.window.pages.currentWidget(), self.window.tabs)
        self.assertTrue(self.window.ui_actions["save"].isEnabled())
        self.assertFalse(self.window.native_action.isEnabled())
        self.window.close_tab(0)
        self.assertIs(self.window.pages.currentWidget(), self.window.welcome)

    def test_outline_reference_jump_and_real_opened_source_diff(self):
        text = "class Panel:\n def show(self):\n  self.GetObject('account')\n"
        self.source.write_text(text, encoding="utf-8")
        self.window.add_source(self.source)
        self.window.analyze_source()
        self.assertEqual(self.window.symbols.topLevelItemCount(), 1)
        self.assertEqual(self.window.symbols.topLevelItem(0).childCount(), 1)
        self.assertEqual(self.window.references.topLevelItemCount(), 1)
        self.window.jump_item(self.window.references.topLevelItem(0))
        self.assertEqual(self.window.current().editor.textCursor().blockNumber(), 2)
        self.window.current().editor.insertPlainText("# changed\n")
        self.window.analyze_source()
        self.assertIn("+# changed", self.window.diff.toPlainText())
        self.window.save_tab(self.window.current())
        self.window.analyze_source()
        self.assertIn("+# changed", self.window.diff.toPlainText())
        self.assertEqual(self.window.current().opened_text, text)

    def test_search_case_whole_word_unicode_and_single_undo(self):
        self.window.add_source(self.source, text="😀 x xx X x\n")
        self.window.find.setText("x")
        self.window.replacement.setText("測試")
        self.window.whole_words.setChecked(True)
        self.window.replace_all()
        editor = self.window.current().editor
        self.assertEqual(editor.toPlainText(), "😀 測試 xx X 測試\n")
        editor.undo()
        self.assertEqual(editor.toPlainText(), "😀 x xx X x\n")
        self.window.match_case.setChecked(False)
        self.window.replace_all()
        self.assertEqual(editor.toPlainText(), "😀 測試 xx 測試 測試\n")

    def test_current_replacement_does_not_replace_partial_word(self):
        self.window.add_source(self.source, text="xx x")
        self.window.find.setText("x")
        self.window.replacement.setText("new")
        self.window.whole_words.setChecked(True)
        cursor = self.window.current().editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(1, QTextCursor.MoveMode.KeepAnchor)
        self.window.current().editor.setTextCursor(cursor)
        self.window.replace_current()
        self.assertEqual(self.window.current().editor.toPlainText(), "xx x")
        self.window.replace_current()
        self.assertEqual(self.window.current().editor.toPlainText(), "xx new")

    def test_reference_toolbar_and_indentation_cannot_change_text(self):
        self.window.add_source(self.source, reference=True)
        editor = self.window.current().editor
        original = editor.toPlainText()
        for key in ("save", "associate", "standard", "big5", "gbk", "undo", "redo"):
            self.assertFalse(self.window.ui_actions[key].isEnabled(), key)
        editor.indent_selection()
        self.window.edit_command("undo")
        self.assertEqual(editor.toPlainText(), original)
        self.assertFalse(self.window.current().vm.isEnabled())

    def test_smart_indent_and_block_indent_are_undoable(self):
        self.window.add_source(self.source, text="def show():")
        editor = self.window.current().editor
        editor.moveCursor(QTextCursor.MoveOperation.End)
        QTest.keyClick(editor, Qt.Key.Key_Return)
        self.assertEqual(editor.toPlainText(), "def show():\n    ")
        editor.undo()
        self.assertEqual(editor.toPlainText(), "def show():")
        editor.setPlainText("a\nb\n")
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        editor.setTextCursor(cursor)
        editor.indent_selection()
        self.assertEqual(editor.toPlainText(), "    a\n    b\n")
        editor.undo()
        self.assertEqual(editor.toPlainText(), "a\nb\n")

    def test_highlighting_keeps_comments_inside_strings_and_multiline_state(self):
        self.window.add_source(
            self.source,
            text='x = "# not a comment"\ns = """begin\nreturn # string\nend"""\n',
        )
        document = self.window.current().editor.document()
        self.window.current().editor.highlight.rehighlight()
        first = document.firstBlock()
        self.assertEqual(document.findBlockByLineNumber(1).userState(), 2)
        self.assertEqual(document.findBlockByLineNumber(2).userState(), 2)
        self.assertEqual(document.findBlockByLineNumber(3).userState(), 0)
        string_color = next(
            r.format.foreground().color().name()
            for r in first.layout().formats()
            if r.start <= 6 < r.start + r.length
        )
        self.assertEqual(string_color, "#287148")

    def test_dock_layout_persists_only_with_explicit_settings(self):
        settings = QSettings(
            str(self.root / "test-settings.ini"), QSettings.Format.IniFormat
        )
        first = Window(self.root, settings=settings)
        first.property_dock.hide()
        first.close()
        second = Window(self.root, settings=settings)
        self.assertTrue(second.property_dock.isHidden())
        second.reset_workspace()
        self.assertFalse(second.property_dock.isHidden())
        second.close()
        first.deleteLater()
        second.deleteLater()

    def test_startup_checks_both_vms_without_open_tab(self):
        def compiler(vm, root):
            return SimpleNamespace(
                vm=vm,
                version="2.5.6" if vm == "py25" else "2.7.13",
                bits=32,
                executable=root / vm / "python.exe",
            )

        with patch(
            "script_editor.gui.build_actions.bundled_compiler", side_effect=compiler
        ) as probe:
            with patch.object(
                self.window, "task", side_effect=lambda fn, done: done(fn())
            ):
                self.window.initialize_compilers()
        self.assertEqual(
            [call.args[0] for call in probe.call_args_list], ["py25", "py27"]
        )
        self.assertEqual(set(self.window.compilers), {"py25", "py27"})
        self.assertIn("2/2", self.window.statusBar().currentMessage())
        self.assertFalse(self.window.native_action.isEnabled())

    def test_failed_startup_clears_stale_compilers_but_keeps_source_available(self):
        self.window.compilers["py25"] = object()
        with patch(
            "script_editor.gui.build_actions.bundled_compiler",
            side_effect=ValueError("bad inventory"),
        ):
            with patch.object(
                self.window, "task", side_effect=lambda fn, done: done(fn())
            ):
                self.window.initialize_compilers()
        self.assertEqual(self.window.compilers, {})
        self.assertIn("bad inventory", self.window.info.toPlainText())
        self.window.add_source(self.source)
        self.assertFalse(self.window.current().editor.isReadOnly())

    def test_window_native_build_disabled(self):
        self.window.show()
        self.app.processEvents()
        actions = [
            a for menu in self.window.menuBar().actions() for a in menu.menu().actions()
        ]
        self.assertFalse(
            next(a for a in actions if "生成原生新包" in a.text()).isEnabled()
        )

    def test_dirty_source_close_cancel_and_save(self):
        self.window.add_source(self.source)
        tab = self.window.current()
        tab.editor.insertPlainText("# changed\n")
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel
        ):
            self.window.close_tab(0)
        self.assertEqual(self.window.tabs.count(), 1)
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Save
        ):
            self.window.close_tab(0)
        self.assertEqual(self.window.tabs.count(), 0)
        self.assertIn("# changed", self.source.read_text(encoding="utf-8"))

    def test_replace_all_is_one_undo_and_duplicate_tab_not_added(self):
        self.window.add_source(self.source)
        self.window.add_source(self.source)
        self.assertEqual(self.window.tabs.count(), 1)
        self.window.find.setText("x")
        self.window.replacement.setText("value")
        self.window.replace_all()
        self.assertIn("value", self.window.current().editor.toPlainText())
        self.window.current().editor.undo()
        self.assertEqual(self.window.current().editor.toPlainText(), "x = 1\n")

    def test_two_archives_have_separate_identity_and_vm(self):
        from script_editor.core.archives.document import ArchiveDocument

        for name, data in [("script.fls", script_bytes()), ("data.fls", data_bytes())]:
            path = self.root / name
            path.write_bytes(data)
            self.window.add_archive(ArchiveDocument(path))
        self.assertEqual(self.window.tree.topLevelItemCount(), 2)
        for i, vm in enumerate(("py25", "py27")):
            item = self.window.tree.topLevelItem(i).child(0)
            archive, _ = item.data(0, Qt.ItemDataRole.UserRole)
            self.assertEqual(archive.vm, vm)

    def test_reference_source_cannot_compile_save_or_associate(self):
        self.window.add_source(self.source, reference=True)
        self.assertTrue(self.window.current().editor.isReadOnly())
        with self.assertRaises(ValueError):
            self.window.editable()
        with self.assertRaises(ValueError):
            self.window.save_tab(self.window.current())
        self.window.find.setText("x")
        self.window.replacement.setText("changed")
        self.window.replace_all()
        self.assertEqual(self.window.current().editor.toPlainText(), "x = 1\n")

    def test_project_dirty_close_cancel(self):
        self.window.project_dirty = True
        with patch.object(
            QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel
        ):
            self.assertFalse(self.window.confirm_project())
