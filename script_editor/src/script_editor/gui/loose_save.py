"""Loose mode: ``Ctrl+S`` compiles and writes straight back into the package.

Only the *target* differs from the strict path. Every step that proves the new
bytes are right still runs, in a worker thread, against a temporary package:

1. each changed module is compiled with the exact bundled compiler and audited;
2. the native payload is encoded and decoded back, byte for byte;
3. the whole package is rewritten and re-read, every untouched entry compared;
4. the previous package is copied to ``<name>.fls.bak``;
5. only then is the original atomically replaced, and the new file re-hashed.

Nothing is remembered about "which modules changed" beyond
``Binding.built_source_sha256``: a module is written when its current text does
not match the source that produced the bytes already in the package.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from ..core.archives.document import ArchiveDocument
from ..core.project.storage import ProjectState
from ..core.services.client_install import client_root_for
from ..core.services.files import read_source
from ..core.services.loose_save import batch_summary, changed_bindings, rejection
from ..core.services.native_build import BACKUP_SUFFIX
from ..core.services.workflow import Snapshot, prepare_package, publish_package


class LooseSaveMixin:
    """``Ctrl+S`` in loose mode: save sources, compile, overwrite the package."""

    # -- helpers -------------------------------------------------------
    def loose_archive(self):
        """The package this save targets: selection first, then the open tab."""
        archive = self.selected_archive()
        if archive is not None:
            return archive
        tab = self.tabs.currentWidget()
        binding = self.binding_for_source(tab.path) if tab is not None else None
        if binding is None:
            return None
        return next((a for a in self.archives if a.path == binding.archive), None)

    def binding_for_source(self, path):
        return next((b for b in self.bindings if b.source == path), None)

    def tab_for_source(self, path):
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            if tab.path == path:
                return tab
        return None

    def loose_candidates(self, archive):
        """Bindings of ``archive`` whose text no longer matches the package.

        Open tabs win over the file on disk; a read-only reference tab is never
        a write candidate.
        """
        def read_text(binding):
            tab = self.tab_for_source(binding.source)
            if tab is not None and tab.reference:
                raise OSError("参考稿只读，不能写回")
            if tab is not None:
                return tab.editor.toPlainText()
            return read_source(binding.source)

        return changed_bindings(self.bindings, archive, read_text)

    def can_loose_save(self):
        """Only route Ctrl+S here when this package actually has bound sources.

        A missing compiler is *not* hidden: it raises inside :meth:`loose_save`
        with an actionable message instead of silently saving just the .py.
        """
        archive = self.loose_archive()
        if archive is None:
            return False
        return any(
            binding.archive == archive.path and binding.vm == archive.vm
            for binding in self.bindings
        )

    # -- the action ----------------------------------------------------
    def loose_save(self):
        if self.jobs:
            raise ValueError("后台任务进行中；请等它结束后再写回原包")
        archive = self.loose_archive()
        if archive is None:
            raise ValueError("请先选中要写回的包，或打开它的一条条目")
        if archive.vm not in self.compilers:
            raise ValueError(
                f"尚未通过自检的标准编译器：{archive.vm}；"
                "宽松模式仍然需要真实编译器，请先「编译 → 检查编译器」"
            )
        candidates, problems = self.loose_candidates(archive)
        if not candidates:
            # Nothing to write is not an error: Ctrl+S still means "save my
            # work", so the .py is written and the package is left alone.
            tab = self.tabs.currentWidget()
            dirty = bool(
                tab is not None
                and not tab.reference
                and tab.editor.document().isModified()
            )
            if dirty:
                self.save_tab(tab)
            if problems:
                raise ValueError(rejection(candidates, problems))
            self.statusBar().showMessage(
                "宽松模式：这个包没有内容变动，未写回原包（.py 已保存）", 8000
            )
            return
        if not self.confirm_loose_write(archive, candidates, problems):
            self.statusBar().showMessage("已取消写回原包；编辑内容保留", 6000)
            return

        # Sources first: a package newer than its .py would look dirty forever.
        # A draft that was never written to disk has no .py to save yet; its
        # buffer text is what gets compiled, and the dialog says so.
        unsaved = []
        for candidate in candidates:
            tab = self.tab_for_source(candidate.binding.source)
            if tab is None or not tab.editor.document().isModified():
                continue
            if tab.draft_saved:
                self.save_tab(tab)
            else:
                unsaved.append(tab.path.name)
        snapshots = tuple(
            Snapshot(
                candidate.binding,
                candidate.text,
                candidate.binding.vm,
                False,
                bool(
                    (tab := self.tab_for_source(candidate.binding.source)) is not None
                    and tab.editor.document().isModified()
                ),
            )
            for candidate in candidates
        )
        compiler = self.compilers[archive.vm]
        catalog = self.catalog_for(archive)
        state = ProjectState(tuple(self.bindings), tuple(self.catalogs))
        baselines = dict(self.built_texts)
        protected = (
            tuple(a.path for a in self.archives)
            + tuple(c.path for c in self.catalogs)
            + tuple(b.source for b in self.bindings)
        )

        def work():
            plan = prepare_package(snapshots, compiler, catalog, baselines)
            report, new_state = publish_package(
                plan, state, in_place=True, backup=True, protected=protected
            )
            return plan, report, new_state

        self.task(
            work, lambda result: self.adopt_loose_write(archive, *result, unsaved)
        )

    # -- confirmation --------------------------------------------------
    def confirm_loose_write(self, archive, candidates, problems):
        """Ask once per save where the risk is real.

        No dialog is needed when the user is already in loose mode and the
        package is a working copy: switching the mode was the consent. An
        explicit "写回原包" menu action outside loose mode, and every package
        inside a game client install, still ask.
        """
        root = client_root_for(archive.path)
        if root is None and self.loose_mode():
            return True
        listed = batch_summary(
            candidates,
            problems,
            lambda binding: self.module_names.get(
                (archive.path, binding.index), binding.source.name
            ),
        )
        where = (
            f"这个包在游戏客户端目录里：\n{root}\n"
            "客户端的这一份副本无法从别处恢复。\n\n"
            if root is not None
            else "当前不是宽松模式，这次只写这一遍。\n\n"
        )
        text = (
            where
            + f"将直接改写：{archive.path}\n\n"
            f"要写回的条目（{len(candidates)} 条）：\n{listed}"
            f"\n\n覆盖前会把原包复制成 {archive.path.name}{BACKUP_SUFFIX}。\n"
            "继续写入吗？"
        )
        box = QMessageBox(
            QMessageBox.Icon.Warning,
            "写入客户端原包（宽松模式）",
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self,
        )
        box.button(QMessageBox.StandardButton.Yes).setText("写入原包")
        box.button(QMessageBox.StandardButton.No).setText("取消")
        box.setDefaultButton(QMessageBox.StandardButton.No)
        return box.exec() == QMessageBox.StandardButton.Yes

    # -- adoption ------------------------------------------------------
    def adopt_loose_write(self, old_archive, plan, report, state, unsaved=()):
        """Reopen the rewritten package and re-point the UI at the new bytes."""
        new = ArchiveDocument(report.output)
        try:
            # Navigation metadata is entry-identity based and did not change, so
            # re-scanning 5,001 modules (seconds) would buy nothing.
            new.module_paths = dict(old_archive.module_paths)
            new.module_path_errors = dict(old_archive.module_path_errors)
            self.repoint_archive(old_archive, new)
        except Exception:
            new.close()
            raise
        self.bindings, self.catalogs = list(state.bindings), list(state.catalogs)
        for entry in plan.entries:
            binding = entry.snapshot.binding
            # Baseline key matches what F6 records, so a later diff is correct.
            self.built_texts[(report.output.resolve(), binding.index)] = (
                entry.snapshot.text
            )
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            origin = tab.recovery
            if origin is not None and origin.current_archive == old_archive.path:
                tab.update_recovery_target(origin.continue_after_build(report, new))
        self.project_dirty = True
        self._navigation_revision = None
        self.refresh_native_action()
        self.workspace_refresh()
        backup = report.output.with_name(report.output.name + BACKUP_SUFFIX)
        self.info.setPlainText(
            f"已写回原包（宽松模式）：{report.output}\n"
            f"改动条目：{report.modified_indexes}；未改条目：{report.unchanged_entries}\n"
            f"新 SHA256：{report.output_sha256}\n"
            f"旧字节已备份：{backup}\n"
            + (
                "以下草稿只用了编辑区内容，未写入 .py：" + "、".join(unsaved) + "\n"
                if unsaved
                else ""
            )
            + "写前编译/审计、写后回读校验均已通过；游戏内表现仍未验收。"
        )
        self.statusBar().showMessage(
            f"已写回原包：{len(report.modified_indexes)} 条改动 · 备份 {backup.name}",
            8000,
        )

    def repoint_archive(self, old, new):
        """Swap one open package for its rewritten version, keeping tree state."""
        root = None
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole + 1) is old:
                root = item
                break
        old.close()
        self.archives = [new if item is old else item for item in self.archives]
        if root is None:
            self.add_archive(new)
            return
        root.setData(0, Qt.ItemDataRole.UserRole + 1, new)
        root.setText(0, f"{new.path.name} / {new.vm}（候选VM）")
        root.setToolTip(0, str(new.path))
        for i in range(min(root.childCount(), len(new.entries))):
            child = root.child(i)
            child.setData(0, Qt.ItemDataRole.UserRole, (new, i))
            child.setText(1, str(new.entries[i].size))
