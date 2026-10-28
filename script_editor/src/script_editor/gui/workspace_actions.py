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
        for key in (
            "save", "save_as", "big5", "gbk", "cut", "copy", "paste",
        ):
            action = self.ui_actions.get(key)
            if action is not None:
                action.setEnabled(editable)
        # 全部保存 looks at every tab: focusing a read-only reference tab must
        # not take away the only way to save the dirty ones behind it.
        save_all = self.ui_actions.get("save_all")
        if save_all is not None:
            save_all.setEnabled(
                not self.jobs
                and any(
                    not self.tabs.widget(i).reference
                    and self.tabs.widget(i).editor.document().isModified()
                    for i in range(self.tabs.count())
                )
            )
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
            # Keyed on the tab's own source: F5/F6 resolve their target exactly
            # this way, so this row must not depend on a tree selection.
            binding = self.binding_for_source(tab.path)
            rows.append(
                ("写入目标", "可写回所属条目" if binding else "未绑定条目（不可写包）")
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
                # Jumping from 大纲/查找结果也该让人一眼看到落在哪一行。
                tab.editor.mark_selection(None, None)
                tab.editor.set_match_line(block)

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
        # Only a real match may be painted as a hit: the query may be left over
        # from an earlier search while the caret sits on an unrelated line.
        if tab is not None:
            needle = self.find.text()
            cursor = tab.editor.textCursor()
            selected = cursor.selectedText().replace("\u2029", "\n")
            if needle and selected == needle:
                tab.editor.mark_selection(
                    cursor.selectionStart(), cursor.selectionEnd()
                )
                tab.editor.set_match_line(cursor.block())
            else:
                tab.editor.set_match_line(None)

    def close_search(self):
        """Hide the bar and drop the hit band it put on the editor."""
        self.clear_hits()
        self.search_bar.hide()

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
        hits, truncated = [], False
        for tab in self.source_tabs():
            document = tab.editor.document()
            ranges, complete = self.text_matches(document, needle, limit=5000)
            truncated = truncated or not complete
            for start, _end in ranges:
                line = document.findBlock(start).blockNumber() + 1
                hits.append(f"{tab.path.name}:{line}: {needle}")
        note = (
            f"（已到 {len(hits)} 处上限，结果不完整，请缩小查找范围）"
            if truncated
            else ""
        )
        self.info.setPlainText(
            (f"在已打开的源码中找到 {len(hits)} 处{note}：\n\n" if hits
             else "已打开的源码里没有这个文本：")
            + "\n".join(hits)
        )
        self.output_tabs.setCurrentWidget(self.info)
        self.output_dock.show()
        self.statusBar().showMessage(
            f"在文件中查找：{len(hits)} 处{note}", 6000
        )

    def text_matches(self, document, needle, limit=10000):
        """``(ranges, complete)`` for ``needle`` under the search bar's options.

        ``str.replace`` would ignore 「区分大小写」/「全字匹配」, so replacing
        ``x``→``value`` with whole words on would also rewrite ``max`` — and the
        count would disagree with what 单文件替换 would do.

        The scan is bounded, so it says whether it stopped early: a caller must
        never replace "the matches I found" as if that were every match.
        """
        cursor = QTextCursor(document)
        ranges = []
        while True:
            cursor = document.find(needle, cursor, self.search_flags())
            if cursor.isNull():
                return ranges, True
            ranges.append((cursor.selectionStart(), cursor.selectionEnd()))
            if len(ranges) > limit:  # a pathological file must not hang the UI
                return ranges, False

    def replace_in_files(self):
        """Replace across open editable sources, one undo step per file."""
        needle, replacement = self.find.text(), self.replacement.text()
        if not needle:
            self.statusBar().showMessage("先在上方输入要替换的文本", 6000)
            return
        targets, too_many = [], []
        for tab in self.source_tabs():  # 参考稿只读，本就不在其中
            ranges, complete = self.text_matches(tab.editor.document(), needle)
            if not complete:
                too_many.append(tab.path.name)
            if ranges:
                targets.append((tab, ranges))
        if too_many:
            # Never replace "the first 10001" and call it done.
            self.statusBar().showMessage(
                f"「{needle}」在 {'、'.join(too_many)} 里超过 10000 处，"
                "为免只改一半，未做任何替换；请用更长的查找文本缩小范围",
                12000,
            )
            return
        if not targets:
            self.statusBar().showMessage("已打开的源码里没有这个文本", 6000)
            return
        rules = []
        if self.match_case.isChecked():
            rules.append("区分大小写")
        if self.whole_words.isChecked():
            rules.append("全字匹配")
        rule_note = ("（按上方勾选：" + "、".join(rules) + "）") if rules else ""
        if (
            QMessageBox.question(
                self,
                "在文件中替换",
                f"将在 {len(targets)} 个已打开的源码里替换「{needle}」"
                f"→「{replacement}」{rule_note}。\n每个文件可用一次 Ctrl+Z 撤销；"
                "不会保存，也不会写包。继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        total = 0
        for tab, ranges in targets:
            cursor = QTextCursor(tab.editor.document())
            cursor.beginEditBlock()
            # Back to front: earlier offsets stay valid while later ones change.
            for start, end in reversed(ranges):
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                cursor.insertText(replacement)
            cursor.endEditBlock()
            total += len(ranges)
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
            self.mark_hit(tab.editor, self.find.text())
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

    def commit_filter_search(self):
        """Enter in the tree search box remembers the query for next time."""
        self.filter.remember(self.filter.text())
        self.filter_tree(self.filter.text())

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
        # "Remove the file" = stop showing this package; nothing on disk is
        # touched, which is why it needs no confirmation.
        archive = self.archive_for_item(item)
        if archive is not None:
            menu.addSeparator()
            menu.addAction(
                f"移除文件（{archive.path.name}）",
                lambda: self.remove_archive(archive),
            )
        menu.exec(self.tree.viewport().mapToGlobal(point))

    def archive_for_item(self, item):
        """The package a tree row belongs to (root or entry row alike)."""
        while item is not None:
            archive = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if archive is not None:
                return archive
            item = item.parent()
        return None

    def remove_archive(self, archive):
        """Drop one open package from the workspace; the file stays on disk."""
        if self.jobs:
            # A recovery or a write is reading this archive right now; pulling
            # its document + bindings out from under the worker fails it in a
            # way the user cannot connect to the click they made.
            self.statusBar().showMessage("后台任务进行中；结束后再移除包", 6000)
            return
        owners = [
            self.tabs.widget(i)
            for i in range(self.tabs.count())
            if getattr(getattr(self.tabs.widget(i), "recovery", None),
                       "current_archive", None) == archive.path
        ]
        for tab in owners:
            # Cancelling one prompt aborts the whole removal: half-removed
            # packages are how a tab ends up pointing at nothing.
            if not self.confirm_tab(tab):
                return
        for i in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(i)
            if root.data(0, Qt.ItemDataRole.UserRole + 1) is archive:
                self.tree.takeTopLevelItem(i)
                break
        for index in range(self.tabs.count() - 1, -1, -1):
            tab = self.tabs.widget(index)
            origin = getattr(tab, "recovery", None)
            if origin is not None and origin.current_archive == archive.path:
                self.tabs.removeTab(index)
                tab.deleteLater()
        try:
            archive.close()
        except (OSError, ValueError):
            pass
        self.archives = [a for a in self.archives if a is not archive]
        self.bindings = [b for b in self.bindings if b.archive != archive.path]
        self.catalogs = [c for c in self.catalogs if c.archive != archive.path]
        self.module_names = {
            key: name for key, name in self.module_names.items()
            if key[0] != archive.path
        }
        self.project_dirty = True
        self._navigation_revision = None
        self.refresh_package_labels()
        self.workspace_refresh()
        self.statusBar().showMessage(
            f"已从工作台移除 {archive.path.name}（文件未被修改；"
            f"如需再编辑用「打开脚本文件」）", 9000
        )
