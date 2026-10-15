from __future__ import annotations

import difflib

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QLineEdit,
    QMenu,
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
        for key in ("save", "associate", "big5", "gbk"):
            self.ui_actions[key].setEnabled(editable)
        self.ui_actions["standard"].setEnabled(
            bool(editable and tab.vm.currentData() in self.compilers)
        )
        self.ui_actions["undo"].setEnabled(
            bool(editable and tab.editor.document().isUndoAvailable())
        )
        self.ui_actions["redo"].setEnabled(
            bool(editable and tab.editor.document().isRedoAvailable())
        )
        for key in ("find", "goto", "developer"):
            self.ui_actions[key].setEnabled(bool(tab and not self.jobs))
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
        self.package_count.setText(f"{len(self.archives)} 个包 · 原包只读")
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
            for j in range(root.childCount()):
                child = root.child(j)
                entry = archive.entries[j]
                label = (
                    f"#{entry.index}  · ID {entry.identity}"
                    if archive.kind == "0slf"
                    else f"#{entry.index}  · {entry.identity}"
                )
                embedded = self.module_names.get((archive.path, entry.index))
                if embedded:
                    label += f"  {embedded}"
                binding = bindings.get((archive.path, entry.index))
                if binding:
                    label += f" ← {binding.source.name}"
                child.setText(0, label)
                child.setToolTip(
                    0,
                    f"身份：{entry.identity}\n"
                    + (
                        str(binding.source)
                        if binding
                        else "双击读取包内模块并尝试恢复；未关联源码"
                    ),
                )
                child.setIcon(0, file_icon)

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
            rows.append(("关联", "与所选条目匹配" if binding else "未与所选条目关联"))
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
        menu.addAction("另开语料候选（保留当前稿）", self.open_corpus_module)
        associate = menu.addAction("关联当前源码到此条目…", self.associate)
        associate.setEnabled(
            bool(
                self.selected()
                and self.tabs.currentWidget()
                and not self.tabs.currentWidget().reference
                and not self.jobs
            )
        )
        menu.exec(self.tree.viewport().mapToGlobal(point))
