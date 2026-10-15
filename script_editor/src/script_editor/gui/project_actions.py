from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..core.archives.document import ArchiveDocument
from ..core.inspection.native import inspect_module
from ..core.project.document import Binding, save_project
from ..core.project.storage import load_state
from ..core.project.workspace import EditorState
from ..core.services.bundled_catalog import bundled_catalog
from ..core.services.files import read_source


class ProjectActions:
    def associate(self):
        try:
            tab = self.editable()
            if tab.source_kind == "recovered-draft":
                self.adopt_recovery()
                return
            selected = self.selected()
            if not selected:
                raise ValueError("请选中条目")
            archive, index = selected
            if tab.vm.currentData() != archive.vm:
                raise ValueError("源码与条目的VM不一致")
            if (
                QMessageBox.question(
                    self,
                    "确认源码对应条目",
                    "真实源码与此条目的业务对应关系由您确认。继续？",
                    defaultButton=QMessageBox.StandardButton.No,
                )
                != QMessageBox.StandardButton.Yes
            ):
                return
            catalog = self.catalog_for(archive)
            source_path = tab.path

            def prepare():
                binding = Binding.associate(archive, index, source_path)
                _, filename, _ = inspect_module(archive, index, catalog)
                return replace(binding, filename_hex=filename.hex())

            def complete(binding):
                self.bindings = [
                    b
                    for b in self.bindings
                    if (b.archive, b.index) != (archive.path, index)
                ] + [binding]
                self.project_dirty = True
                self.refresh_native_action()
                self.info.setPlainText(
                    "已严格读取原模块并关联源码；业务语义仍须人工确认。"
                )

            self.task(prepare, complete)
        except Exception as exc:
            self.fail(exc)

    def save_project(self):
        name, _ = QFileDialog.getSaveFileName(
            self,
            "保存项目（含编辑缓冲区/草稿；不复制原包）",
            "",
            "Project (*.mxscript.json)",
        )
        if not name:
            return False
        try:
            path = Path(
                name if name.endswith(".mxscript.json") else name + ".mxscript.json"
            )
            editors = tuple(
                EditorState(
                    tab.path,
                    tab.vm.currentData(),
                    tab.source_kind,
                    tab.editor.toPlainText(),
                    tab.editor.document().isModified(),
                    tab.draft_saved,
                    tab.recovery,
                )
                for tab in (self.tabs.widget(i) for i in range(self.tabs.count()))
                if not (
                    tab.recovery
                    and tab.recovery.vm == "py25"
                    and tab.recovery.index == 1288
                )
            )
            save_project(
                path,
                self.bindings,
                self.catalogs,
                editors=editors,
                corpora=tuple(self.corpus_refs),
            )
            self.saved_workspace = {e.path: e.text for e in editors}
            self.project_dirty = False
            return True
        except Exception as exc:
            self.fail(exc)
            return False

    def confirm_project(self):
        if not self.project_dirty:
            return True
        reply = QMessageBox.question(
            self,
            "项目关联未保存",
            "保存当前项目关联与编辑缓冲区/候选草稿？",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        return self.save_project() if reply == QMessageBox.StandardButton.Save else True

    def open_project(self):
        if not self.confirm_project():
            return
        name, _ = QFileDialog.getOpenFileName(
            self,
            "只打开可信项目（将读取其引用的本地文件）",
            "",
            "Project (*.mxscript.json)",
        )
        if not name:
            return
        if (
            QMessageBox.question(
                self,
                "确认项目来源",
                "确认项目来源可信？将读取关联的本地文件。未采用草稿不会自动取得发布资格。",
                defaultButton=QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self.task(lambda: self.prepare_project(Path(name)), self.adopt_project)

    def prepare_project(self, path):
        state = load_state(path)
        snapshots = {e.path: e.text for e in state.editors}
        texts = {
            b.source: snapshots[b.source]
            if b.source in snapshots
            else read_source(b.source)
            for b in state.bindings
        }
        documents = []
        catalogs = list(state.catalogs)
        try:
            paths = (
                {b.archive for b in state.bindings}
                | {c.archive for c in state.catalogs}
                | {e.report.archive for e in state.editors if e.report is not None}
                | {c.archive for c in state.corpora}
            )
            for path in paths:
                archive = ArchiveDocument(path)
                documents.append(archive)
                for binding in state.bindings:
                    if binding.archive == path:
                        binding.verify(archive)
                for catalog in state.catalogs:
                    if catalog.archive == path:
                        catalog.verify(archive)
                if not any(c.archive == path for c in catalogs):
                    # Older projects can have entry-information tabs but no XOR
                    # reference. Add only a valid exact-pin asset; never replace
                    # an explicit project association or block draft restoration
                    # because the optional bundled asset is unavailable.
                    try:
                        catalog = bundled_catalog(archive, self.runtime_root)
                    except (OSError, ValueError):
                        catalog = None
                    if catalog is not None:
                        catalogs.append(catalog)
            return replace(state, catalogs=tuple(catalogs)), texts, documents
        except Exception:
            for archive in documents:
                archive.close()
            raise

    def adopt_project(self, prepared):
        state, texts, documents = prepared
        old_tab = self.tabs.currentWidget()
        old_item = self.tree.currentItem()
        old_tabs = {self.tabs.widget(i) for i in range(self.tabs.count())}
        old_archives = set(self.archives)
        try:
            # One source tab has one explicit VM; reject conflicts before mutation.
            source_vms = {}
            for binding in state.bindings:
                if source_vms.setdefault(binding.source, binding.vm) != binding.vm:
                    raise ValueError("同一源码被关联到不同VM；请拆分为两个源码文件")
                for tab in old_tabs:
                    if tab.path == binding.source and (
                        tab.reference
                        or tab.source_kind != binding.source_kind
                        or tab.vm.currentData() != binding.vm
                    ):
                        raise ValueError(
                            "已打开的源码类型/VM与项目冲突；请先关闭冲突标签"
                        )
            for editor in state.editors:
                for tab in old_tabs:
                    if tab.path != editor.path:
                        continue
                    if (
                        tab.vm.currentData() != editor.vm
                        or tab.source_kind != editor.source_kind
                    ):
                        raise ValueError("已打开编辑区与项目类型/VM冲突，原稿保留")
                    if tab.recovery is not None and editor.report is not None:
                        if (
                            tab.recovery.archive,
                            tab.recovery.index,
                            tab.recovery.fingerprint,
                        ) != (
                            editor.report.archive,
                            editor.report.index,
                            editor.report.fingerprint,
                        ):
                            raise ValueError("已打开编辑区来源与项目冲突，原稿保留")
            for archive in documents:
                old = next((a for a in self.archives if a.path == archive.path), None)
                if old is not None:
                    old._assert_unchanged()
                else:
                    archive._assert_unchanged()
                    self.add_archive(archive)
            for binding in state.bindings:
                self.add_source(
                    binding.source,
                    binding.vm,
                    text=texts[binding.source],
                    source_kind=binding.source_kind,
                )
            for editor in state.editors:
                tab = self.add_source(
                    editor.path,
                    editor.vm,
                    reference=editor.source_kind in {"reference", "module-unavailable"},
                    text=editor.text,
                    source_kind=editor.source_kind,
                )
                if tab in old_tabs:
                    continue  # NEVER replace an open buffer or its undo/report state.
                tab.editor.setPlainText(editor.text)
                tab.draft_saved = editor.draft_saved and editor.path.is_file()
                if editor.report is not None:
                    tab.attach_report(editor.report)
                    tab.candidate_requested.connect(self.open_recovery_candidate)
                tab.editor.document().setModified(editor.modified)
                self.refresh_tab_title(tab)
        except Exception:
            # Roll back only widgets/readers created in this attempt. Existing
            # dirty buffers, undo history, associations and baselines stay intact.
            for i in range(self.tabs.count() - 1, -1, -1):
                tab = self.tabs.widget(i)
                if tab not in old_tabs:
                    self.tabs.removeTab(i)
                    tab.deleteLater()
            for i in range(self.tree.topLevelItemCount() - 1, -1, -1):
                root = self.tree.topLevelItem(i)
                if root.data(0, Qt.ItemDataRole.UserRole + 1) not in old_archives:
                    self.tree.takeTopLevelItem(i)
            self.archives[:] = [a for a in self.archives if a in old_archives]
            if old_tab is not None:
                self.tabs.setCurrentWidget(old_tab)
            if old_item is not None:
                self.tree.setCurrentItem(old_item)
            self.refresh_native_action()
            raise
        finally:
            for archive in documents:
                if archive not in self.archives:
                    archive.close()
        self.bindings, self.catalogs = list(state.bindings), list(state.catalogs)
        self.built_texts.clear()
        self.corpus_refs = list(state.corpora)
        self.corpora.clear()  # Verify lazily; embedded drafts also work offline.
        self.saved_workspace = {e.path: e.text for e in state.editors}
        self.project_dirty = any(
            tab.editor.toPlainText() != self.saved_workspace.get(tab.path)
            for tab in old_tabs
            if tab.editor.document().isModified()
        )
        self.refresh_native_action()
