from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtGui import QAction, QBrush, QColor, QTextCursor
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTreeWidgetItem,
)

from .. import __version__
from ..core.archives.document import ArchiveDocument
from ..core.inspection.encoding import byte_literal
from ..core.inspection.legacy_text import previews as literal_previews
from ..core.inspection.legacy_text import summary as literal_summary
from ..core.services.bundled_catalog import resolve_catalog
from ..core.services.files import SourceRevision, read_source_snapshot, save_source
from ..core.services.module_browser import RecoverySessionCache
from ..core.services.module_paths import index_script_paths
from ..core.services.package_selfcheck import index_with_cache
from ..core.services.verdict_cache import VerdictCache, default_cache_root
from .build_actions import BuildActions
from .corpus_actions import CorpusActions
from .jobs import Job, Progress
from .literal_preview import LiteralReportDialog
from .module_actions import ModuleActions
from .project_actions import ProjectActions
from .source_tab import SourceTab
from .workspace import HEAVY_ENTRY_BYTES, Workspace


class Window(
    Workspace, ModuleActions, ProjectActions, BuildActions, CorpusActions, QMainWindow
):
    def __init__(self, runtime_root: Path, settings=None):
        super().__init__()
        self.runtime_root = runtime_root
        self.settings = settings
        self.archives: list[ArchiveDocument] = []
        self.bindings = []
        self.catalogs = []
        self.corpora = {}
        self.corpus_refs = []
        self.saved_workspace = {}
        self.built_texts = {}
        self.module_names = {}
        self.project_dirty = False
        self.compilers = {}
        self.jobs = set()
        # Session-scoped engine results and per-user package verdicts. A hit
        # only avoids recomputation; neither is ever a source-trust signal.
        self.recovery_cache = RecoverySessionCache()
        self.literal_dialog = None
        self.verdict_cache = VerdictCache(default_cache_root(), __version__)
        self.progress = Progress()
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(200)
        self.progress_timer.timeout.connect(self.refresh_progress)
        self.setWindowTitle(f"MXSJ 脚本工作台 {__version__} · 实验版")
        screen = self.screen().availableGeometry()
        self.resize(
            min(1440, max(960, screen.width() - 60)),
            min(900, max(640, screen.height() - 80)),
        )
        self.build_workspace()
        self.build_menus()
        self.tree.itemSelectionChanged.connect(self.show_entry)
        self.tabs.currentChanged.connect(self.refresh_native_action)
        self.refresh_native_action()
        self.statusBar().showMessage("就绪 · 原包只读，所有写包生成新文件")
        if settings is not None:
            try:
                geometry, state = (
                    settings.value("geometry"),
                    settings.value("workspace"),
                )
                if geometry is not None:
                    self.restoreGeometry(geometry)
                if state is not None:
                    self.restoreState(state, 1)
            except (TypeError, ValueError):
                pass  # Damaged local preferences cannot prevent opening source.

    def refresh_progress(self):
        done, total, phase = self.progress.snapshot()
        if total <= 0:
            self.progress_bar.hide()
            return
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(done)
        if phase:
            self.progress_bar.setFormat(phase + " %v/%m")
        self.progress_bar.show()

    def fail(self, message):
        self.info.setPlainText(str(message))
        self.output_tabs.setCurrentWidget(self.info)
        self.output_dock.show()
        QMessageBox.warning(self, "操作未完成", str(message))

    def task(self, function, complete, *, cancel=None):
        if self.jobs:
            return
        job = Job(function)
        self.jobs.add(job)
        actions = [
            (action, action.isEnabled()) for action in self.findChildren(QAction)
        ]
        dock_states = [
            (dock, dock.isEnabled()) for dock in self.findChildren(QDockWidget)
        ]
        for dock, _ in dock_states:
            dock.setEnabled(False)
        self.centralWidget().setEnabled(False)
        self.menuBar().setEnabled(False)
        for action, _ in actions:
            action.setEnabled(False)
        self.statusBar().showMessage("后台处理中…")
        self.progress.finish()
        self.progress_bar.hide()
        self.progress_timer.start()
        cancel_button = None
        if cancel is not None:
            cancel_button = QPushButton("取消恢复（保留已有编辑）")
            cancel_button.clicked.connect(lambda: cancel.set())
            self.statusBar().addPermanentWidget(cancel_button)

        def finish(result, error=False):
            self.jobs.discard(job)
            self.progress_timer.stop()
            self.progress.finish()
            self.progress_bar.hide()
            if cancel_button is not None:
                self.statusBar().removeWidget(cancel_button)
                cancel_button.deleteLater()
            self.centralWidget().setEnabled(True)
            for dock, enabled in dock_states:
                dock.setEnabled(enabled)
            self.menuBar().setEnabled(True)
            for action, enabled in actions:
                action.setEnabled(enabled)
            self.refresh_native_action()
            self.statusBar().showMessage("就绪 · 原生写包需关联源码并通过清单确认")
            if cancel is not None and cancel.is_set():
                self.statusBar().showMessage("恢复已取消；原包及已有编辑未修改")
                return
            if error:
                self.fail(result)
            else:
                try:
                    complete(result)
                except Exception as exc:
                    self.fail(exc)

        job.signals.done.connect(
            lambda result: finish(result), Qt.ConnectionType.QueuedConnection
        )
        job.signals.failed.connect(
            lambda error: finish(error, True), Qt.ConnectionType.QueuedConnection
        )
        QThreadPool.globalInstance().start(job)

    def add_archive(self, document):
        if any(a.path == document.path for a in self.archives):
            document.close()
            return
        root = QTreeWidgetItem([f"{document.path.name} / {document.vm}（候选VM）", ""])
        root.setToolTip(0, str(document.path))
        root.setData(0, Qt.ItemDataRole.UserRole + 1, document)
        for entry in document.entries:
            child = QTreeWidgetItem([entry.identity, str(entry.size)])
            child.setData(0, Qt.ItemDataRole.UserRole, (document, entry.index))
            if entry.size >= HEAVY_ENTRY_BYTES:
                # Measured: only a handful of entries are this big, and they
                # dominate recovery latency (up to ~25 s), so warn before the
                # user waits instead of silently blocking the window.
                child.setToolTip(
                    0,
                    f"大模块：存储 {entry.size:,} 字节。单次恢复可能耗时数十秒，"
                    "任务栏可取消；反汇编与源码分开生成。",
                )
                child.setForeground(0, QBrush(QColor("#b35900")))
            root.addChild(child)
        self.tree.addTopLevelItem(root)
        self.archives.append(document)
        self.module_names = {
            key: name
            for key, name in self.module_names.items()
            if key[0] != document.path
        }
        self.module_names.update(
            ((document.path, index), name)
            for index, name in document.module_paths.items()
        )
        root.setExpanded(True)
        self.workspace_refresh()
        try:
            self.filter_tree(self.filter.text())
        except Exception:
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(root))
            self.archives.remove(document)
            raise

    def open_archive(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "打开script.fls或data.fls", "", "FLS (*.fls)"
        )
        if name:

            def prepare():
                document = ArchiveDocument(Path(name))
                try:
                    # Pins first (cheap). Unlisted packages are decoded entry by
                    # entry and adopted on that evidence; nothing is guessed.
                    catalog, warning, check = resolve_catalog(
                        document,
                        self.runtime_root,
                        self.verdict_cache,
                        progress=self.progress.update,
                    )
                    if catalog is None:
                        # A broken/missing optional asset must not hide the
                        # package, and a refused catalog leaves names unknown.
                        index_script_paths(document, None)
                    elif not document.module_paths:
                        self.progress.update(0, len(document.entries), "读取模块路径")
                        index_with_cache(
                            document,
                            catalog,
                            self.verdict_cache,
                            tool_version=__version__,
                            progress=self.progress.update,
                        )
                    self.progress.finish()
                except Exception:
                    document.close()
                    raise
                return document, catalog, warning, check

            def complete(result):
                document, catalog, warning, check = result
                if any(a.path == document.path for a in self.archives):
                    document.close()
                    return
                try:
                    self.add_archive(document)
                except Exception:
                    document.close()
                    raise
                if catalog is not None:
                    self.catalogs.append(catalog)
                    self.project_dirty = True
                    if check is not None:
                        self.info.setPlainText(
                            "已自动套用内置解码参数（未登记的新包，逐条试解后采纳）。\n"
                            + check.report()
                            + "\n双击条目尝试恢复编辑；匹配参数不等于源码可信。"
                        )
                    else:
                        self.info.setPlainText(
                            "已按完整包指纹自动匹配内置解码参数，并核对参数SHA256。"
                            "\n原包/已登记测试派生包均逐条严格解码；双击条目尝试恢复编辑。\n匹配参数不等于源码可信或全部模块均已支持。"
                        )
                elif warning:
                    self.info.setPlainText("内置参数不可用，原包仍可浏览：" + warning)
                elif check is not None:
                    self.info.setPlainText(
                        "未能自动套用内置解码参数。\n"
                        + check.report()
                        + "\n包仍可浏览；可用「编译 → 选择当前包的 XOR 目录」"
                        "指定匹配的参数文件。"
                    )
                elif document.vm == "py25":
                    self.info.setPlainText(
                        "此script包指纹不在内置参数授权匹配范围；未自动套用。"
                        "\n派生包请打开对应项目；其他包请显式选择已核实的解码参数JSON。"
                    )

            self.task(prepare, complete)

    def filter_tree(self, text):
        for i in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(i)
            scope = self.archive_selector.currentData()
            root.setHidden(
                bool(scope and root.data(0, Qt.ItemDataRole.UserRole + 1).path != scope)
            )
            for j in range(root.childCount()):
                item = root.child(j)
                archive, index = item.data(0, Qt.ItemDataRole.UserRole)
                searchable = (
                    (item.text(0) + f" #{index} " + archive.entries[index].identity)
                    .replace("\\", "/")
                    .casefold()
                )
                item.setHidden(text.replace("\\", "/").casefold() not in searchable)
            if text:
                root.setExpanded(True)

    def selected(self):
        item = self.tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None

    def show_entry(self):
        self.refresh_native_action()
        selected = self.selected()
        if selected:
            archive, index = selected
            try:
                metadata = archive.entry_metadata(index)
                if archive.kind == "0slf":
                    metadata["module_path"] = self.module_names.get(
                        (archive.path, index), ""
                    )
                    metadata["path_diagnostic"] = archive.module_path_errors.get(
                        index, ""
                    )
                binding = next(
                    (
                        b
                        for b in self.bindings
                        if b.archive == archive.path and b.index == index
                    ),
                    None,
                )
                if binding:
                    metadata["source_status"] = "user-associated-not-game-verified"
                    metadata["source_kind"] = binding.source_kind
                    metadata["recovery_sha256"] = binding.recovery_sha256
                    metadata["source_path"] = str(binding.source)
                    metadata["built_source_sha256"] = (
                        binding.built_source_sha256 or "未知"
                    )
            except Exception as exc:
                self.info.setPlainText(str(exc))
                return
            self.info.setPlainText(
                str(archive.path)
                + "\n"
                + json.dumps(metadata, ensure_ascii=False, indent=2)
                + "\n双击读取包内模块并尝试恢复；草稿可编辑另存，写包前须检查并采用。"
            )

    def add_source(
        self,
        path,
        vm="py25",
        reference=False,
        text=None,
        source_kind=None,
        source_revision=None,
    ):
        path = path.resolve()
        for i in range(self.tabs.count()):
            if self.tabs.widget(i).path == path:
                if self.tabs.widget(i).reference != reference or (
                    source_kind is not None
                    and self.tabs.widget(i).source_kind != source_kind
                ):
                    raise ValueError("该文件已按另一来源类型打开，请先关闭原标签")
                self.tabs.setCurrentIndex(i)
                return self.tabs.widget(i)
        if text is None:
            text, source_revision = read_source_snapshot(path)
        tab = SourceTab(
            path,
            text,
            vm,
            reference,
            source_kind,
            source_revision,
        )
        label = ("[参考] " if reference else "") + path.name
        self.tabs.addTab(tab, label)
        self.tabs.setCurrentWidget(tab)
        self.tabs.setTabToolTip(self.tabs.indexOf(tab), str(path))

        def changed(dirty):
            self.refresh_tab_title(tab)

        tab.editor.document().modificationChanged.connect(changed)
        tab.editor.document().modificationChanged.connect(self.refresh_native_action)
        tab.editor.undoAvailable.connect(self.refresh_native_action)
        tab.editor.redoAvailable.connect(self.refresh_native_action)
        tab.editor.textChanged.connect(self.analysis_timer.start)
        tab.editor.textChanged.connect(lambda: setattr(self, "project_dirty", True))
        tab.editor.cursorPositionChanged.connect(self.update_cursor)
        tab.vm.currentIndexChanged.connect(self.refresh_native_action)
        tab.vm.currentIndexChanged.connect(lambda: setattr(self, "project_dirty", True))
        tab.adopt_button.clicked.connect(self.adopt_recovery)
        self.refresh_tab_title(tab)
        self.refresh_native_action()
        return tab

    def refresh_tab_title(self, tab):
        prefix = {
            "reference": "[参考] ",
            "recovered-draft": "[恢复草稿] ",
            "recovered-reviewed": "[恢复源码] ",
            "module-unavailable": "[条目信息] ",
        }.get(tab.source_kind, "")
        label = (
            prefix
            + tab.path.name
            + (" *" if tab.editor.document().isModified() else "")
        )
        self.tabs.setTabText(self.tabs.indexOf(tab), label)
        self.tabs.setTabToolTip(self.tabs.indexOf(tab), str(tab.path))

    def open_source(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "打开UTF-8源码或已另存的恢复草稿", "", "Python (*.py)"
        )
        if name:
            try:
                text, revision = read_source_snapshot(Path(name))
                if "MXSJ-RECOVERED-DRAFT" in "\n".join(text.splitlines()[:3]):
                    vm = (
                        "py27"
                        if "# MXSJ-RECOVERY-VM: py27" in text.splitlines()[:3]
                        else "py25"
                    )
                    self.add_source(
                        Path(name),
                        vm=vm,
                        text=text,
                        source_kind="recovered-draft",
                        source_revision=revision,
                    )
                    return
                reply = QMessageBox.question(
                    self,
                    "确认源码来源",
                    "这是您确认可编译的真实/自写源码，而非反编译参考稿吗？\n"
                    "选“否”将只读打开，禁止保存、关联和编译。",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel,
                )
                if reply != QMessageBox.StandardButton.Cancel:
                    self.add_source(
                        Path(name),
                        reference=reply == QMessageBox.StandardButton.No,
                        text=text,
                        source_revision=revision,
                    )
            except Exception as exc:
                self.fail(exc)

    def open_reference(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "只读查看参考文本", "", "Text (*.py *.txt)"
        )
        if name:
            try:
                self.add_source(Path(name), reference=True)
            except Exception as exc:
                self.fail(exc)

    def editable(self):
        tab = self.current()
        if tab.reference:
            raise ValueError("参考稿只读，禁止保存、关联、修改或编译")
        return tab

    def current(self):
        tab = self.tabs.currentWidget()
        if tab is None:
            raise ValueError("请先打开源码")
        return tab

    def save_tab(self, tab):
        if self.jobs:
            raise ValueError("后台任务期间不能保存源码")
        if tab.reference:
            raise ValueError("参考稿不能保存为可信源码")
        if tab.source_kind == "recovered-draft":
            saved = self.save_draft(tab)
            if saved is None:
                raise ValueError("已取消另存恢复草稿，编辑内容保留")
            if saved:
                return
        self.assert_writable_target(tab.path)
        save_source(
            tab.path,
            tab.editor.toPlainText(),
            [a.path for a in self.archives] + [c.path for c in self.catalogs],
            expected=tab.source_revision,
        )
        tab.source_revision = SourceRevision(
            hashlib.sha256(tab.editor.toPlainText().encode("utf-8")).hexdigest()
        )
        self.project_dirty = True
        tab.editor.document().setModified(False)

    def save_current(self):
        try:
            self.save_tab(self.current())
        except Exception as exc:
            self.fail(exc)

    def confirm_tab(self, tab):
        if not tab.editor.document().isModified():
            return True
        if self.saved_workspace.get(tab.path) == tab.editor.toPlainText():
            return True  # Current buffer is durably saved inside the project.
        reply = QMessageBox.question(
            self,
            "源码未保存",
            f"保存 {tab.path.name}？",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Save:
            try:
                self.save_tab(tab)
            except Exception as exc:
                self.fail(exc)
                return False
        return True

    def close_tab(self, index):
        tab = self.tabs.widget(index)
        if self.confirm_tab(tab):
            self.tabs.removeTab(index)
            tab.deleteLater()
            self.project_dirty = True

    def encode(self, codec):
        try:
            cursor = self.editable().editor.textCursor()
            if not cursor.hasSelection():
                raise ValueError("仅选择文案/路径的内容，不要包含引号或u前缀")
            literal = byte_literal(cursor.selectedText().replace("\u2029", "\n"), codec)
            if (
                QMessageBox.question(
                    self,
                    "替换选择文本为字节字面量",
                    "选择内容应不含引号/u前缀。不会自动修改其它字符串。\n" + literal,
                    defaultButton=QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                cursor.insertText(literal)
        except Exception as exc:
            self.fail(exc)

    def preview_byte_literals(self):
        """Show a read-only comparison of readable MBCS byte literals.

        Nothing is written: the decoded text is a display artefact only, since
        the client compares the original bytes at run time.
        """
        try:
            tab = self.current()
            source = tab.editor.toPlainText()
            records = literal_previews(source)
            if not records:
                self.statusBar().showMessage(
                    "未发现可解码的 \\xNN 字节字面量；源码未改动", 6000
                )
                return
            counts = literal_summary(records)
            dialog = LiteralReportDialog(self, records, tab.path.name)
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            dialog.show()
            self.literal_dialog = dialog
            self.statusBar().showMessage(
                f"可读对照：{counts['literals']} 处字面量 / {counts['lines']} 行"
                f"（{'/'.join(counts['codecs'])}）· 只读，源码未改动",
                8000,
            )
        except Exception as exc:
            self.fail(exc)

    def find_next(self, backwards=False):
        tab = self.tabs.currentWidget()
        if tab and self.find.text():
            editor = tab.editor
            flags = self.search_flags(backwards)
            if not editor.find(self.find.text(), flags):
                cursor = editor.textCursor()
                cursor.movePosition(
                    QTextCursor.MoveOperation.End
                    if backwards
                    else QTextCursor.MoveOperation.Start
                )
                editor.setTextCursor(cursor)
                if not editor.find(self.find.text(), flags):
                    self.statusBar().showMessage("未找到匹配文本", 3500)

    def replace_all(self):
        tab = self.tabs.currentWidget()
        if not tab or tab.reference or self.jobs or not self.find.text():
            return
        document = tab.editor.document()
        cursor = QTextCursor(document)
        matches = []
        while True:
            cursor = document.find(self.find.text(), cursor, self.search_flags())
            if cursor.isNull():
                break
            matches.append((cursor.selectionStart(), cursor.selectionEnd()))
        edit = QTextCursor(document)
        edit.beginEditBlock()
        for start, end in reversed(matches):
            edit.setPosition(start)
            edit.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            edit.insertText(self.replacement.text())
        edit.endEditBlock()
        self.statusBar().showMessage(
            f"已替换 {len(matches)} 处 · Ctrl+Z 一次撤销", 3500
        )

    def closeEvent(self, event):
        if self.jobs or not all(
            self.confirm_tab(self.tabs.widget(i)) for i in range(self.tabs.count())
        ):
            event.ignore()
            return
        if not self.confirm_project():
            event.ignore()
            return
        self.analysis_timer.stop()
        if self.settings is not None:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("workspace", self.saveState(1))
        for archive in self.archives:
            archive.close()
        event.accept()
