"""Package-backed recovery drafts. Editing does not grant source trust."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path
from threading import Event

from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..core.project.document import Binding
from ..core.services.files import SourceRevision, save_new_source
from ..core.services.module_browser import read_module
from ..core.services.module_paths import display_module_path
from ..core.services.workflow import Snapshot, prepare_build


class ModuleActions:
    def open_package_module(self, reload=False):
        if self.jobs:
            return
        selected = self.selected()
        if not selected:
            return
        archive, index = selected
        existing = next(
            (
                self.tabs.widget(i)
                for i in range(self.tabs.count())
                if getattr(self.tabs.widget(i), "recovery", None)
                and self.tabs.widget(i).recovery.current_archive == archive.path
                and self.tabs.widget(i).recovery.index == index
            ),
            None,
        )
        if existing is not None:
            self.tabs.setCurrentWidget(existing)
            if not reload:
                if (
                    existing.source_kind != "module-unavailable"
                    or existing.editor.document().isModified()
                    or self.catalog_for(archive) is None
                ):
                    return
                # Retry an untouched old failure tab after catalog association
                # becomes available. Never replace an editable recovery draft.
            if existing.source_kind != "module-unavailable":
                self.fail(
                    "已有恢复稿/源码保留，不能重新读取覆盖编辑。请先另存并关闭该标签。"
                )
                return
        catalog = self.catalog_for(archive)

        def complete(report):
            if existing is not None:
                self.tabs.removeTab(self.tabs.indexOf(existing))
                existing.deleteLater()
            virtual = archive.path.parent / (
                f".{archive.path.name}.{index}.recovered.py"
            )
            fallback = "# 此条目未恢复为源码，不生成pass占位稿。\n# " + "\n# ".join(
                report.diagnostics
            )
            tab = self.add_source(
                virtual,
                vm=report.vm,
                text=report.source or fallback,
                reference=not bool(report.source),
                source_kind="recovered-draft"
                if report.source
                else "module-unavailable",
            )
            tab.draft_saved = False
            tab.attach_report(report)
            tab.candidate_requested.connect(self.open_recovery_candidate)
            if report.filename_hex:
                try:
                    self.module_names[(report.archive, report.index)] = (
                        display_module_path(bytes.fromhex(report.filename_hex))
                    )
                except ValueError:
                    pass  # An invalid name must not discard a recovered draft.
            if report.source:
                tab.editor.document().setModified(True)
            self.info.setPlainText(
                (
                    "恢复引擎已返回文本（非原始源码，尚未编译核验）"
                    if report.complete
                    else "恢复未完成/不支持此条目"
                )
                + "\n"
                + "\n".join(report.diagnostics)
                + "\n可编辑恢复草稿；写包前须检查并人工核对采用。"
            )
            self.output_dock.show()
            self.refresh_native_action()

        cancel = Event()

        def recover():
            if any(r.archive == archive.path for r in self.corpus_refs):
                from ..core.services.corpus_recovery import corpus_report

                try:
                    return corpus_report(
                        self.corpus_for(archive), archive, index, catalog
                    )
                except (OSError, ValueError) as exc:
                    result = read_module(
                        archive,
                        index,
                        catalog,
                        cancel=cancel,
                        cache=getattr(self, "recovery_cache", None),
                    )
                    return replace(
                        result,
                        diagnostics=("语料不可用：" + str(exc), *result.diagnostics),
                    )
            return read_module(
                archive,
                index,
                catalog,
                cancel=cancel,
                cache=self.recovery_cache,
            )

        self.task(
            recover,
            complete,
            cancel=cancel,
        )

    def open_recovery_candidate(self, report):
        # A fresh tab, never mutate/replace a user's current candidate or edits.
        suffix = (
            "." + report.corpus_manifest_sha256[:12]
            if report.corpus_manifest_sha256
            else ""
        )
        virtual = report.archive.parent / (
            f".{report.archive.name}.{report.index}.{report.selected_engine}{suffix}.recovered.py"
        )
        for i in range(self.tabs.count()):
            existing = self.tabs.widget(i)
            origin = existing.recovery
            same_origin = origin is not None and (
                origin.current_archive,
                origin.current_fingerprint,
                origin.index,
                origin.selected_engine,
                origin.corpus_manifest_sha256,
                origin.candidate_pyc_sha256,
            ) == (
                report.current_archive,
                report.current_fingerprint,
                report.index,
                report.selected_engine,
                report.corpus_manifest_sha256,
                report.candidate_pyc_sha256,
            )
            if existing.path == virtual.resolve() or same_origin:
                self.tabs.setCurrentWidget(existing)
                return existing
        tab = self.add_source(
            virtual, vm=report.vm, text=report.source, source_kind="recovered-draft"
        )
        tab.draft_saved = False
        tab.attach_report(report)
        tab.candidate_requested.connect(self.open_recovery_candidate)
        tab.editor.document().setModified(True)
        return tab

    def save_draft(self, tab):
        if tab.draft_saved:
            return False  # The caller uses the normal save for its own document.
        name, _ = QFileDialog.getSaveFileName(
            self,
            "另存恢复草稿（新.py，不覆盖现有文件；不会自动获得源码身份）",
            f"recovered_{tab.vm.currentData()}.py",
            "Python (*.py)",
        )
        if not name:
            return None
        path = Path(name if name.lower().endswith(".py") else name + ".py").resolve()
        protected = tuple(a.path for a in self.archives) + tuple(
            c.path for c in self.catalogs
        )
        protected += tuple(b.source for b in self.bindings)
        self.assert_writable_target(path)
        save_new_source(path, tab.editor.toPlainText(), protected)
        tab.path, tab.draft_saved = path, True
        tab.source_revision = SourceRevision(
            hashlib.sha256(tab.editor.toPlainText().encode("utf-8")).hexdigest()
        )
        self.project_dirty = True
        tab.path_label.setToolTip(str(path))
        tab.editor.document().setModified(False)
        self.refresh_tab_title(tab)
        return True

    def adopt_recovery(self):
        try:
            tab = self.current()
            if self.jobs or tab.source_kind != "recovered-draft":
                raise ValueError("请先打开包内条目的恢复草稿")
            selected = self.selected()
            if not selected:
                raise ValueError("请选择此恢复稿对应的包内条目")
            archive, index = selected
            if tab.vm.currentData() != archive.vm:
                raise ValueError("草稿VM与选中包不一致，请显式核对后再选择")
            origin = tab.recovery
            if origin and (
                origin.current_archive != archive.path
                or origin.index != index
                or origin.current_fingerprint != archive.fingerprint()
            ):
                raise ValueError("恢复稿来源与当前选中条目/包指纹不符")
            if (
                origin
                and not origin.complete
                and tab.editor.toPlainText() == origin.source
            ):
                raise ValueError(
                    "此恢复稿未完整生成，未经修订不能直接采用。可另存草稿、补齐并检查逻辑后再试。"
                )
            compiler = self.compilers.get(archive.vm)
            if compiler is None:
                raise ValueError("请先检查此VM的编译器，再检查恢复稿")
            if self.save_draft(tab) is None:
                return
            text = tab.editor.toPlainText()
            catalog = self.catalog_for(archive)

            def prepare():
                from ..core.inspection.native import inspect_module

                standard, filename, _ = inspect_module(archive, index, catalog)
                if origin and origin.target_archive is not None and (
                    hashlib.sha256(standard).hexdigest() != origin.standard_sha256
                ):
                    raise ValueError(
                        "继续采用目标的标准字节码已变化；保留原稿，禁止采用"
                    )
                if origin and (
                    (origin.corpus_manifest_sha256 and not origin.candidate_pyc_sha256)
                    or (
                        origin.candidate_pyc_sha256
                        and hashlib.sha256(standard).hexdigest()
                        != origin.candidate_pyc_sha256
                    )
                ):
                    raise ValueError(
                        "外部语料pyc与原包严格来源不同；可编辑草稿，但不能据此采用发布"
                    )
                binding = replace(
                    Binding.associate(archive, index, tab.path),
                    filename_hex=filename.hex(),
                    source_kind="recovered-reviewed",
                    recovery_sha256=hashlib.sha256(standard).hexdigest(),
                )
                return prepare_build(
                    Snapshot(binding, text, archive.vm), compiler, catalog
                )

            def complete(plan):
                if tab.editor.toPlainText() != text:
                    raise ValueError("编辑文本已变化，请重新检查")
                if (
                    QMessageBox.question(
                        self,
                        "恢复稿检查通过，是否人工核对采用？",
                        "已通过真实编译、严格原生转换和完整回读；这不证明反编译逻辑正确。\n"
                        "只有您已检查/修复业务逻辑时才选择是。会记录为恢复源码，不冒充原始源码。\n"
                        "本操作不生成游戏包；之后仍须预编译清单并输出新包。",
                        defaultButton=QMessageBox.StandardButton.No,
                    )
                    != QMessageBox.StandardButton.Yes
                ):
                    return
                self.bindings = [
                    b
                    for b in self.bindings
                    if (b.archive, b.index) != (archive.path, index)
                ] + [plan.snapshot.binding]
                tab.source_kind = "recovered-reviewed"
                tab.update_mode()
                self.project_dirty = True
                self.refresh_tab_title(tab)
                self.refresh_native_action()
                self.info.setPlainText(
                    "已记录人工核对的恢复源码，可F6预编译并生成新包。原包未修改。"
                )

            self.task(prepare, complete)
        except Exception as exc:
            self.fail(exc)
