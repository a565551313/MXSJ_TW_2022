from __future__ import annotations

import difflib

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMessageBox,
    QStyle,
    QTreeWidgetItem,
)

from ..core.inspection.references import inspect_references
from ..core.inspection.symbols import outline


class WorkspaceActions:
    def workspace_refresh(self):
        tab = self.tabs.currentWidget()
        self.pages.setCurrentWidget(self.tabs if tab else self.welcome)
        editable = bool(tab and not tab.reference and not self.jobs)
        for key in ("save", "save_as", "big5", "gbk", "cut", "copy", "paste"):
            action = self.ui_actions.get(key)
            if action is not None:
                action.setEnabled(editable)
        self.ui_actions["undo"].setEnabled(
            bool(editable and tab.editor.document().isUndoAvailable())
        )
        self.ui_actions["redo"].setEnabled(
            bool(editable and tab.editor.document().isRedoAvailable())
        )
        for key in ("find", "replace", "find_in_files", "replace_in_files"):
            action = self.ui_actions.get(key)
            if action is not None:
                action.setEnabled(bool(tab and not self.jobs))
        for key in ("export_decrypted", "export_encrypted"):
            action = self.ui_actions.get(key)
            if action is not None:
                action.setEnabled(bool(self.archives and not self.jobs))
        self.compiler_status.setText(f"编译器 {len(self.compilers)}/2 已探测")
        self.file_status.setText(
            "恢复草稿（可编辑，待核验）"
            if tab and tab.source_kind == "recovered-draft"
            else "条目详情（尚不能恢复）"
            if tab and tab.source_kind == "module-unavailable"
            else "只读参考"
            if tab and tab.reference
            else "UTF-8 源码"
            if tab
            else "未打开源码"
        )
        self.package_count.setText(
            f"{len(self.archives)} 个包 · F5 写回 / F6 另存"
        )
        self.refresh_package_labels()
        self.update_cursor()
        self.analysis_timer.start()

    def refresh_package_labels(self):
        revision = (
            tuple((b.archive, b.index, b.source) for b in self.bindings),
            tuple(a.path for a in self.archives),
            tuple(self.module_names.items()),
        )
        if getattr(self, "_navigation_revision", None) == revision:
            return
        self._navigation_revision = revision
        current = self.archive_selector.currentData()
        self.archive_selector.blockSignals(True)
        self.archive_selector.clear()
        self.archive_selector.addItem(f"全部已打开的包（{len(self.archives)}）", None)
        for archive in self.archives:
            self.archive_selector.addItem(
                f"{archive.path.name} · {archive.vm}", archive.path
            )
            self.archive_selector.setItemData(
                self.archive_selector.count() - 1,
                str(archive.path),
                Qt.ItemDataRole.ToolTipRole,
            )
        self.archive_selector.setCurrentIndex(
            max(0, self.archive_selector.findData(current))
        )
        self.archive_selector.blockSignals(False)
        bindings = {(b.archive, b.index): b for b in self.bindings}
        file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        for i in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(i)
            archive = root.data(0, Qt.ItemDataRole.UserRole + 1)
            root.setIcon(0, folder_icon)
            root.setText(
                0,
                f"{archive.path.name} / {archive.vm} · "
                f"{len(archive.entries)} 条（候选VM）",
            )
            if archive.kind == "0slf":
                count = sum(
                    (archive.path, e.index) in self.module_names
                    for e in archive.entries
                )
                root.setToolTip(
                    0,
                    f"{archive.path}\n已读取路径 {count}/{len(archive.entries)}；"
                    "路径不代表源码已恢复或可信",
                )
            for j in range(root.childCount()):
                child = root.child(j)
                entry = archive.entries[j]
                embedded = self.module_names.get((archive.path, entry.index))
                label = (
                    embedded or f"[路径未读取] 条目 #{entry.index}"
                    if archive.kind == "0slf"
                    else entry.identity.replace("\\", "/")
                )
                binding = bindings.get((archive.path, entry.index))
                if binding:
                    label += f" ← {binding.source.name}"
                child.setText(0, label)
                child.setToolTip(
                    0,
                    f"条目：#{entry.index} · ID {entry.identity}\n"
                    + (
                        "内嵌模块路径：" + embedded + "\n"
                        if embedded
                        else archive.module_path_errors.get(entry.index, "路径尚未读取")
                        + "\n"
                        if archive.kind == "0slf"
                        else "包内路径：" + entry.identity + "\n"
                    )
                    + (
                        str(binding.source)
                        if binding
                        else "双击读取包内模块并尝试恢复；未关联源码"
                    ),
                )
                child.setIcon(0, file_icon)
        self.filter_tree(self.filter.text())

    def select_archive_scope(self, *_):
        self.tree.setCurrentItem(None)
        self.filter_tree(self.filter.text())
        selected = self.archive_selector.currentData()
        if selected:
            for i in range(self.tree.topLevelItemCount()):
                root = self.tree.topLevelItem(i)
                if root.data(0, Qt.ItemDataRole.UserRole + 1).path == selected:
                    self.tree.setCurrentItem(root)
                    root.setExpanded(True)
                    self.tree.scrollToItem(root)
                    break
        self.refresh_native_action()

    def update_cursor(self):
        tab = self.tabs.currentWidget()
        if tab:
            cursor = tab.editor.textCursor()
            prefix = (
                cursor.block()
                .text()
                .encode("utf-16-le")[: cursor.positionInBlock() * 2]
            )
            column = len(prefix.decode("utf-16-le").expandtabs(4)) + 1
            self.cursor_status.setText(
                f"行 {cursor.blockNumber() + 1}  列 {column}  ·  {tab.vm.currentData()}"
            )
        else:
            self.cursor_status.setText("就绪")

    def analyze_source(self):
        tab = self.tabs.currentWidget()
        self.symbols.clear()
        self.references.clear()
        self.properties.clear()
        selected = self.selected()
        rows = []
        if selected:
            archive, index = selected
            rows += [
                ("原包", str(archive.path)),
                ("条目", archive.entries[index].identity),
                (
                    "包内路径",
                    self.module_names.get((archive.path, index), "路径未读取")
                    if archive.kind == "0slf"
                    else archive.entries[index].identity,
                ),
                ("包 VM", archive.vm),
            ]
        if not selected:
            archive = self.selected_archive()
            if archive:
                rows += [
                    ("原包", str(archive.path)),
                    ("候选 VM", archive.vm),
                    ("条目数", str(len(archive.entries))),
                ]
        if not tab:
            self.diff.setPlainText(
                "打开源码后，对比编辑内容与打开时的文本。不是反编译或游戏包差异。"
            )
        else:
            text = tab.editor.toPlainText()
            rows += [
                ("源码", str(tab.path)),
                ("编译 VM", tab.vm.currentData()),
                ("来源", tab.mode_label.text()),
                ("未保存", "是" if tab.editor.document().isModified() else "否"),
                ("编码", "UTF-8"),
                ("行数", str(tab.editor.blockCount())),
            ]
            binding = self.active_binding()
            rows.append(
                ("写入目标", "可写回所选条目" if binding else "未绑定条目（不可写包）")
            )
            if len(text) + len(tab.opened_text) > 500_000:
                self.diff.setPlainText(
                    "大型源码暂停自动差异/大纲/引用扫描；编辑、保存和严格构建不受影响。"
                )
            else:
                parents = []
                for symbol in outline(text)[:1000]:
                    item = QTreeWidgetItem(
                        [
                            ("类  " if symbol.kind == "class" else "函数  ")
                            + symbol.name,
                            str(symbol.line),
                        ]
                    )
                    item.setData(0, Qt.ItemDataRole.UserRole, (tab.path, symbol.line))
                    while parents and parents[-1][0] >= symbol.column:
                        parents.pop()
                    if parents:
                        parents[-1][1].addChild(item)
                    else:
                        self.symbols.addTopLevelItem(item)
                    item.setExpanded(True)
                    parents.append((symbol.column, item))
                for hint in inspect_references(text)[:1000]:
                    item = QTreeWidgetItem([str(hint.line), hint.kind, hint.text])
                    item.setData(0, Qt.ItemDataRole.UserRole, (tab.path, hint.line))
                    self.references.addTopLevelItem(item)
                changes = "".join(
                    difflib.unified_diff(
                        tab.opened_text.splitlines(keepends=True),
                        text.splitlines(keepends=True),
                        fromfile="打开时的源码",
                        tofile="当前编辑区",
                    )
                )
                if len(changes) > 200_000:
                    changes = changes[:200_000] + "\n[差异超过显示上限，后续未显示]"
                self.diff.setPlainText(
                    changes
                    or "当前文本与打开时一致。保存源码不会伪造游戏包的文本基线。"
                )
        for key, value in rows:
            item = QTreeWidgetItem([key, value])
            item.setToolTip(1, value)
            self.properties.addTopLevelItem(item)

    def jump_item(self, item, _column=0):
        target = item.data(0, Qt.ItemDataRole.UserRole)
        tab = self.tabs.currentWidget()
        if target and tab and tab.path == target[0]:
            self.move_to_line(target[1])

    def move_to_line(self, line):
        tab = self.tabs.currentWidget()
        if tab:
            block = tab.editor.document().findBlockByLineNumber(line - 1)
            if block.isValid():
                tab.editor.setTextCursor(QTextCursor(block))
                tab.editor.centerCursor()
                tab.editor.setFocus()

    def goto_line(self):
        tab = self.tabs.currentWidget()
        if tab:
            line, ok = QInputDialog.getInt(
                self, "转到行", "行号", 1, 1, tab.editor.blockCount()
            )
            if ok:
                self.move_to_line(line)

    def edit_command(self, command):
        tab = self.tabs.currentWidget()
        if self.jobs:
            return
        focused = QApplication.focusWidget()
        if isinstance(focused, QLineEdit):
            getattr(focused, command)()
        elif tab and not tab.reference:
            getattr(tab.editor, command)()

    def show_search(self):
        self.search_bar.show()
        tab = self.tabs.currentWidget()
        if tab and tab.editor.textCursor().hasSelection():
            text = tab.editor.textCursor().selectedText()
            if "\u2029" not in text:
                self.find.setText(text)
        self.find.setFocus()
        self.find.selectAll()

    def show_replace(self):
        """Ctrl+H: same bar as find, with the replacement row already visible."""
        self.show_search()
        self.replacement.setFocus()
        self.replacement.selectAll()

    def source_tabs(self):
        """Editable, non-reference tabs in opening order."""
        tabs = []
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            if not tab.reference:
                tabs.append(tab)
        return tabs

    def find_in_files(self):
        """List every match in the open sources; nothing is modified."""
        needle = self.find.text().strip()
        if not needle:
            self.show_search()
            self.statusBar().showMessage("先在上方输入要查找的文本", 6000)
            return
        hits, wrapped = [], 0
        for tab in self.source_tabs():
            text = tab.editor.toPlainText()
            start = 0
            while True:
                found = text.find(needle, start)
                if found < 0:
                    break
                line = text.count("\n", 0, found) + 1
                hits.append(f"{tab.path.name}:{line}: {needle}")
                start = found + len(needle)
                wrapped += 1
                if wrapped > 5000:
                    break
            if wrapped > 5000:
                break
        self.info.setPlainText(
            (f"在已打开的源码中找到 {len(hits)} 处：\n\n" if hits
             else "已打开的源码里没有这个文本：")
            + "\n".join(hits)
        )
        self.output_tabs.setCurrentWidget(self.info)
        self.output_dock.show()
        self.statusBar().showMessage(f"在文件中查找：{len(hits)} 处", 6000)

    def replace_in_files(self):
        """Replace across open editable sources, one undo step per file."""
        needle, replacement = self.find.text(), self.replacement.text()
        if not needle:
            self.statusBar().showMessage("先在上方输入要替换的文本", 6000)
            return
        targets = [
            tab for tab in self.source_tabs() if needle in tab.editor.toPlainText()
        ]
        if not targets:
            self.statusBar().showMessage("已打开的源码里没有这个文本", 6000)
            return
        if (
            QMessageBox.question(
                self,
                "在文件中替换",
                f"将在 {len(targets)} 个已打开的源码里替换「{needle}」"
                f"→「{replacement}」。\n每个文件可用一次 Ctrl+Z 撤销；"
                "不会保存，也不会写包。继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        total = 0
        for tab in targets:
            text = tab.editor.toPlainText()
            total += text.count(needle)
            cursor = QTextCursor(tab.editor.document())
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.insertText(text.replace(needle, replacement))
            cursor.endEditBlock()
        self.statusBar().showMessage(
            f"已在 {len(targets)} 个文件里替换 {total} 处 · 未保存", 8000
        )

    def search_flags(self, backwards=False):
        flags = QTextDocument.FindFlag(0)
        if self.match_case.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if backwards:
            flags |= QTextDocument.FindFlag.FindBackward
        return flags

    def find_previous(self):
        self.find_next(backwards=True)

    def replace_current(self):
        tab = self.tabs.currentWidget()
        if not tab or tab.reference or self.jobs or not self.find.text():
            return
        cursor = tab.editor.textCursor()
        # Re-find at the selection start, so whole-word/case rules are honored.
        start = QTextCursor(tab.editor.document())
        start.setPosition(cursor.selectionStart())
        match = tab.editor.document().find(self.find.text(), start, self.search_flags())
        if (
            not match.isNull()
            and match.selectionStart() == cursor.selectionStart()
            and match.selectionEnd() == cursor.selectionEnd()
        ):
            match.insertText(self.replacement.text())
            tab.editor.setTextCursor(match)
        self.find_next()

    def open_associated(self):
        selected = self.selected()
        if not selected:
            return
        archive, index = selected
        binding = next(
            (
                b
                for b in self.bindings
                if b.archive == archive.path and b.index == index
            ),
            None,
        )
        if binding:
            try:
                self.add_source(
                    binding.source, vm=binding.vm, source_kind=binding.source_kind
                )
            except (OSError, ValueError) as exc:
                self.fail(exc)
        else:
            self.open_package_module()

    def package_menu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return
        self.tree.setCurrentItem(item)
        menu = QMenu(self)
        menu.addAction("打开条目 / 恢复源码", self.open_associated)
        menu.addAction(
            "重新读取未恢复条目", lambda: self.open_package_module(reload=True)
        )
        menu.exec(self.tree.viewport().mapToGlobal(point))
