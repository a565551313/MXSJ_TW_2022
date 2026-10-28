"""One click, one package: 写入原包 (F5) and 生成新包 (F6).

Both verbs do exactly the same work; only the destination differs.

* **写入原包** overwrites the package the modules belong to, keeping one rolling
  ``<name>.fls.bak`` of the previous bytes.
* **生成新包** asks for a file name once (a name that must not exist yet) and
  leaves the original untouched.

Neither asks for a "mode", a manifest review or a second confirmation. Every
check still runs in a worker thread against a temporary package: compile with
the pinned compiler, audit, native round-trip, rewrite, read back every entry,
verify the digest — and only then swap.

A module that no longer fits its fixed XOR slot is grown automatically
(``allow_resize=True``); the result text says so, because the client has never
been observed loading a resized entry.
"""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt

from ..core.archives.document import ArchiveDocument
from ..core.project.storage import ProjectState
from ..core.services.files import read_source
from ..core.services.loose_save import batch_summary, changed_bindings, rejection
from ..core.services.native_build import BACKUP_SUFFIX, install_over_source
from ..core.services.workflow import Snapshot, prepare_package, publish_package


class WritePackageMixin:
    """``F5`` writes the package back, ``F6`` writes a new one."""

    # -- helpers -------------------------------------------------------
    def current_package(self):
        """The package this action targets: selection first, then the open tab."""
        archive = self.selected_archive()
        if archive is not None:
            return archive
        tab = self.tabs.currentWidget()
        binding = self.binding_for_source(tab.path) if tab is not None else None
        if binding is not None:
            found = next((a for a in self.archives if a.path == binding.archive), None)
            if found is not None:
                return found
        if len(self.archives) == 1:
            # One package open: it is unmistakably the target.
            return self.archives[0]
        return None

    def binding_for_source(self, path):
        return next((b for b in self.bindings if b.source == path), None)

    def tab_for_source(self, path):
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            if tab.path == path:
                return tab
        return None

    def retry_unverified_draft(self, archive, *, in_place):
        """``F5`` on a draft whose automatic verification failed: try again.

        A failed verification leaves the tab editable but unbound, so there is
        nothing to write. Pressing ``F5`` therefore means "I fixed it — check
        again", and a passing check goes straight on to the write. Returns
        ``False`` when the current tab is not such a draft.
        """
        tab = self.tabs.currentWidget()
        origin = getattr(tab, "recovery", None) if tab is not None else None
        if origin is None or getattr(tab, "reference", False):
            return False
        if origin.current_archive != archive.path:
            return False
        bound = {b.source for b in self.bindings if b.archive == archive.path}
        if tab.path in bound:
            return False
        action = self.write_in_place if in_place else self.generate_new_package
        started = self.auto_adopt(tab, archive, origin.index, origin, then=action)
        if started:
            self.statusBar().showMessage("正在重新校验草稿；通过后立即写包…")
        return started

    def package_candidates(self, archive):
        """Bindings of ``archive`` whose text no longer matches the package."""

        def read_text(binding):
            tab = self.tab_for_source(binding.source)
            if tab is not None and tab.reference:
                raise OSError("参考稿只读，不能写入包")
            if tab is not None:
                return tab.editor.toPlainText()
            return read_source(binding.source)

        return changed_bindings(self.bindings, archive, read_text)

    def package_is_writable(self):
        archive = self.current_package()
        return bool(
            archive is not None
            and not self.jobs
            and archive.vm in getattr(self, "compilers", {})
        )

    # -- the two actions -----------------------------------------------
    def write_in_place(self):
        try:
            self._write_package(in_place=True)
        except Exception as exc:
            self.fail(exc)

    def generate_new_package(self):
        try:
            self._write_package(in_place=False)
        except Exception as exc:
            self.fail(exc)

    def _write_package(self, *, in_place):
        if self.jobs:
            raise ValueError("后台任务进行中；请等它结束后再写包")
        archive = self.current_package()
        if archive is None:
            raise ValueError(
                "先在左侧选一个包（或双击包内条目），再点「写入原包」/「生成新包」"
            )
        compiler = self.compilers.get(archive.vm)
        if compiler is None:
            raise ValueError(
                f"还没检查过 {archive.vm} 的编译器：点工具栏「检查编译器」，"
                "自检通过后才能写包"
            )
        if self.retry_unverified_draft(archive, in_place=in_place):
            return
        bound = [b for b in self.bindings if b.archive == archive.path]
        if not bound:
            raise ValueError(
                "这个包还没有可写源码：双击包内条目 → 自动恢复并校验 → "
                "编辑后按 F5 写回（或 F6 另存新包）"
            )
        candidates, problems = self.package_candidates(archive)
        if not candidates:
            tab = self.tabs.currentWidget()
            dirty = (
                tab is not None
                and not tab.reference
                and tab.editor.document().isModified()
            )
            if dirty:
                self.save_tab(tab)
            if problems:
                raise ValueError(rejection(candidates, problems))
            self.statusBar().showMessage(
                "没有需要写入的改动：编辑区编译结果与包内字节一致"
                "（只改注释/空白不影响包）",
                9000,
            )
            return

        destination = None
        same_name = False
        if not in_place:
            asked = self._ask_destination(archive)
            if asked is None:
                return
            destination, same_name = asked

        listed = batch_summary(
            candidates,
            problems,
            lambda binding: self.module_names.get(
                (archive.path, binding.index), binding.source.name
            ),
        )
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
        catalog = self.catalog_for(archive)
        state = ProjectState(tuple(self.bindings), tuple(self.catalogs))
        baselines = dict(self.built_texts)
        protected = (
            tuple(a.path for a in self.archives)
            + tuple(c.path for c in self.catalogs)
            + tuple(b.source for b in self.bindings)
        )

        # Release our own read handle before the file is replaced: Windows
        # refuses MoveFileEx while any handle is open, even with no game running.
        self.detach_archive(archive)

        def prepare():
            plan = prepare_package(
                snapshots, compiler, catalog, baselines, allow_resize=True
            )
            if not plan.entries:
                return plan, None, None, None
            # Saving under the original name keeps every check: the package is
            # built and verified as a brand-new file under a temporary name,
            # then the original is renamed to ``<name>_bak`` and the new bytes
            # take its place. Only the last two renames differ.
            staging = (
                destination.with_name(
                    f".{destination.name}.generating-{os.getpid()}.fls"
                )
                if same_name
                else destination
            )
            report, new_state = publish_package(
                plan,
                state,
                destination=staging,
                in_place=in_place,
                backup=in_place,
                allow_resize=True,
                protected=protected,
            )
            backup = None
            if same_name:
                backup = install_over_source(
                    archive.path,
                    staging,
                    expected_sha256=report.source_sha256,
                )
                report = replace(report, output=archive.path)
            return plan, report, new_state, backup

        def complete(result):
            plan, report, new_state, backup = result
            if report is None:
                self.finish_no_changes(archive, plan, listed)
                return
            self.adopt_write(
                archive,
                plan,
                report,
                new_state,
                unsaved,
                listed,
                generated=same_name,
                backup=backup,
            )

        def failed(_error):
            # Nothing on disk changed; put the reader back anyway.
            self.restore_archive(archive)

        self.task(prepare, complete, on_error=failed)

    def _ask_destination(self, archive):
        """One file dialog for 生成新包, prefilled with the original name.

        Returns ``(target, same_name)``, or ``None`` when the dialog is
        cancelled. Choosing the original name is allowed: the old package is
        renamed to ``<name>_bak`` first, so nothing is lost. Any *other*
        existing file is still refused — 生成新包 never overwrites a stranger's
        file.
        """
        name = self.ask_save_file(
            "generate_package",
            "生成新包（默认与原包同名；同名保存会把原包改名成 <包名>_bak）",
            str(archive.path),
            "FLS (*.fls)",
        )
        if not name:
            return None
        target = Path(name if name.lower().endswith(".fls") else name + ".fls")
        same_name = target.resolve() == archive.path.resolve()
        if target.exists() and not same_name:
            raise ValueError(
                f"{target.name} 已经存在；生成新包不会覆盖别的文件，请换个名字"
            )
        if not same_name:
            self.assert_writable_target(target)
        return target, same_name

    # -- outcome -------------------------------------------------------
    def finish_no_changes(self, old_archive, plan, listed=""):
        self.restore_archive(old_archive)
        self.statusBar().showMessage(
            "没有写入：源码与包内字节完全等价（例如只改了注释）。" + listed, 12000
        )

    def adopt_write(
        self, old_archive, plan, report, state, unsaved=(), listed="",
        *, generated=False, backup=None,
    ):
        """Reopen the rewritten package and re-point the UI at it."""
        new = ArchiveDocument(report.output)
        moved = report.output.resolve() != old_archive.path.resolve()
        try:
            new.module_paths = dict(old_archive.module_paths)
            new.module_path_errors = dict(old_archive.module_path_errors)
            self.repoint_archive(old_archive, new)
        except Exception:
            new.close()
            raise
        self.bindings, self.catalogs = list(state.bindings), list(state.catalogs)
        if moved:
            # Keyed by package path; in-place writes keep their keys.
            def moved_key(key):
                if key[0] == old_archive.path:
                    return (report.output.resolve(), key[1])
                return key

            self.module_names = {
                moved_key(key): name for key, name in self.module_names.items()
            }
            self.built_texts = {
                moved_key(key): text for key, text in self.built_texts.items()
            }
        for entry in plan.entries:
            binding = entry.snapshot.binding
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

        resized = [
            entry.snapshot.binding.index
            for entry in plan.entries
            if entry.resized
        ]
        if backup is None:
            backup = report.output.with_name(report.output.name + BACKUP_SUFFIX)
        if generated:
            where = "已生成新包（同原包名，旧包已改名备份）"
        else:
            where = "已写入原包" if not moved else "已生成新包并切换来源"
        lines = [
            f"{where}：{report.output}",
            f"改动 {len(report.modified_indexes)} 条；"
            f"其余 {report.unchanged_entries} 条未动",
            f"新 SHA256：{report.output_sha256}",
        ]
        if not moved:
            lines.append(f"旧字节备份：{backup}")
        lines.append("写前编译/审计、写后整包回读逐条比对均已通过。")
        if resized:
            lines.append(
                f"注意：{len(resized)} 条按新长度重算"
                f"（条目 {sorted(resized)}，实验功能）。"
                "本机校验通过，客户端加载这种变长条目从未实测过。"
            )
        if unsaved:
            lines.append("以下草稿只用了编辑区内容，未写入 .py：" + "、".join(unsaved))
        if listed:
            lines.append("本次范围：\n" + listed)
        if moved:
            lines.append(
                "要换包：编辑器读完就会放开句柄，现在可以直接在资源管理器里"
                "把原包改名、再把新包改成它的名字；换完点「文件 → 重新读取"
                "已打开的包」即可，不必关掉编辑器。"
            )
        self.info.setPlainText("\n".join(lines))
        self.statusBar().showMessage(
            f"{where}：{len(report.modified_indexes)} 条改动"
            + (f" · 备份 {backup.name}" if not moved else ""),
            9000,
        )

    # -- handle lifetime -----------------------------------------------
    def detach_archive(self, archive):
        """Close our own reader for the file that is about to be replaced."""
        try:
            archive.close()
        except (OSError, ValueError):
            pass  # Already closed or never opened; nothing to release.

    def restore_archive(self, closed):
        """Re-open a package we detached but did not manage to replace."""
        if not closed.path.is_file():
            return
        try:
            reopened = ArchiveDocument(closed.path)
        except Exception as exc:  # noqa: BLE001 - never mask the original error
            self.statusBar().showMessage(
                f"原包未能重新打开（{exc}）；原文件未被本次操作修改", 12000
            )
            return
        reopened.module_paths = dict(closed.module_paths)
        reopened.module_path_errors = dict(closed.module_path_errors)
        self.repoint_archive(closed, reopened)
        self.workspace_refresh()

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
