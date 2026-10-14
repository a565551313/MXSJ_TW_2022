from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core.archives.document import ArchiveDocument
from ..core.compiler.profiles import PROFILES
from ..core.compiler.runner import bundled_compiler, compile_standard, inspect_compiler
from ..core.inspection.encoding import byte_literal
from ..core.project.document import Binding, load_project, save_project
from ..core.services.files import read_source, save_source
from .code_editor import CodeEditor
from .jobs import Job


class SourceTab(QWidget):
    def __init__(self, path: Path, text: str, vm="py25", reference=False):
        super().__init__()
        self.path = path
        self.reference = reference
        self.editor = CodeEditor()
        self.editor.setPlainText(text)
        self.editor.setReadOnly(reference)
        self.editor.document().setModified(False)
        self.vm = QComboBox()
        for key, profile in PROFILES.items():
            self.vm.addItem(profile.label, key)
        self.vm.setCurrentIndex(self.vm.findData(vm))
        layout = QVBoxLayout(self)
        layout.addWidget(self.vm)
        layout.addWidget(self.editor)


class Window(QMainWindow):
    def __init__(self, runtime_root: Path):
        super().__init__()
        self.runtime_root = runtime_root
        self.archives: list[ArchiveDocument] = []
        self.bindings: list[Binding] = []
        self.project_dirty = False
        self.compilers = {}
        self.jobs = set()
        self.setWindowTitle(f"MXSJ 脚本编辑器 {__version__} · 基础版（原生写包未启用）")
        self.resize(1180, 760)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["包 / 条目（内容尚未解码验证）", "存储字节"])
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("筛选条目ID或data路径")
        self.filter.textChanged.connect(self.filter_tree)
        left = QWidget()
        layout = QVBoxLayout(left)
        layout.addWidget(self.filter)
        layout.addWidget(self.tree)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setAcceptRichText(False)
        self.info.setPlainText(
            "原包只读。当前仅索引容器，不代表已验证所有条目均为脚本。\n"
            "无源码条目只读；仅手工打开自己确认来源的UTF-8源码。\n"
            "关联仅记录用户选择，不自动证明与原条目语义一致。\n"
            "标准.pyc不是原生脚本载荷，不能放进游戏。\n"
            "内置编译器空清单时禁用；可显式选择标准开发编译器。"
        )
        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.info)
        splitter.setSizes([260, 650, 270])
        body = QWidget()
        box = QVBoxLayout(body)
        banner = QLabel("M1 · 源码保存 ≠ 游戏写包；反编译稿不能当作可信源码")
        banner.setWordWrap(True)
        box.addWidget(banner)
        box.addWidget(splitter)
        search = QHBoxLayout()
        self.find = QLineEdit()
        self.find.setPlaceholderText("查找（字面文本）")
        self.replacement = QLineEdit()
        self.replacement.setPlaceholderText("替换文本")
        search.addWidget(self.find)
        search.addWidget(self.replacement)
        for name, callback in [
            ("下一个", self.find_next),
            ("替换全部", self.replace_all),
        ]:
            button = QPushButton(name)
            button.clicked.connect(callback)
            search.addWidget(button)
        box.addLayout(search)
        self.setCentralWidget(body)
        file_menu = self.menuBar().addMenu("文件")
        for text, shortcut, fn in [
            ("打开脚本包索引…", "Ctrl+O", self.open_archive),
            ("打开已确认来源的UTF-8源码…", "Ctrl+Shift+O", self.open_source),
            ("打开参考文本（只读，不编译）…", "", self.open_reference),
            ("保存当前源码", "Ctrl+S", self.save_current),
            ("关联当前源码到选中条目…", "", self.associate),
            ("保存项目…", "", self.save_project),
            ("打开项目…", "", self.open_project),
        ]:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(fn)
            file_menu.addAction(action)
        edit = self.menuBar().addMenu("编码")
        for text, codec in [
            ("选中文案→Big5字节字面量…", "big5"),
            ("选中路径→GBK字节字面量…", "gbk"),
        ]:
            action = edit.addAction(text)
            action.triggered.connect(lambda checked=False, c=codec: self.encode(c))
        build = self.menuBar().addMenu("编译")
        build.addAction("选择/检查当前VM的标准编译器…", self.select_compiler)
        build.addAction("检查当前VM的内置编译器", self.check_bundled)
        build.addAction("仅编译为标准.pyc…", self.compile)
        native = build.addAction("生成原生新包（M2核心已实现，界面待接入）")
        native.setEnabled(False)
        self.tree.itemSelectionChanged.connect(self.show_entry)
        self.statusBar().showMessage("就绪 · 无原生写包能力")

    def fail(self, message):
        QMessageBox.warning(self, "操作未完成", str(message))

    def task(self, function, complete):
        if self.jobs:
            return
        job = Job(function)
        self.jobs.add(job)
        self.centralWidget().setEnabled(False)
        self.menuBar().setEnabled(False)
        self.statusBar().showMessage("后台处理中…")

        def finish(result, error=False):
            self.jobs.discard(job)
            self.centralWidget().setEnabled(True)
            self.menuBar().setEnabled(True)
            self.statusBar().showMessage("就绪 · 无原生写包能力")
            if error:
                self.fail(result)
            else:
                try:
                    complete(result)
                except Exception as exc:
                    self.fail(exc)

        job.signals.done.connect(lambda result: finish(result))
        job.signals.failed.connect(lambda error: finish(error, True))
        QThreadPool.globalInstance().start(job)

    def add_archive(self, document):
        if any(a.path == document.path for a in self.archives):
            document.close()
            return
        self.archives.append(document)
        root = QTreeWidgetItem([f"{document.path.name} / {document.vm}（候选VM）", ""])
        root.setToolTip(0, str(document.path))
        self.tree.addTopLevelItem(root)
        for entry in document.entries:
            child = QTreeWidgetItem([entry.identity, str(entry.size)])
            child.setData(0, Qt.ItemDataRole.UserRole, (document, entry.index))
            root.addChild(child)
        self.filter_tree(self.filter.text())

    def open_archive(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "打开script.fls或data.fls", "", "FLS (*.fls)"
        )
        if name:
            self.task(lambda: ArchiveDocument(Path(name)), self.add_archive)

    def filter_tree(self, text):
        for i in range(self.tree.topLevelItemCount()):
            root = self.tree.topLevelItem(i)
            for j in range(root.childCount()):
                item = root.child(j)
                item.setHidden(text.casefold() not in item.text(0).casefold())
            root.setExpanded(bool(text))

    def selected(self):
        item = self.tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole) if item else None

    def show_entry(self):
        selected = self.selected()
        if selected:
            archive, index = selected
            try:
                metadata = archive.entry_metadata(index)
            except Exception as exc:
                self.info.setPlainText(str(exc))
                return
            self.info.setPlainText(
                str(archive.path)
                + "\n"
                + json.dumps(metadata, ensure_ascii=False, indent=2)
                + "\n索引识别≠已验证模块。无原生解码/可编译源码。"
            )

    def add_source(self, path, vm="py25", reference=False):
        path = path.resolve()
        for i in range(self.tabs.count()):
            if self.tabs.widget(i).path == path:
                if self.tabs.widget(i).reference != reference:
                    raise ValueError("该文件已按另一来源类型打开，请先关闭原标签")
                self.tabs.setCurrentIndex(i)
                return
        tab = SourceTab(path, read_source(path), vm, reference)
        label = ("[参考] " if reference else "") + path.name
        self.tabs.addTab(tab, label)
        self.tabs.setCurrentWidget(tab)
        self.tabs.setTabToolTip(self.tabs.indexOf(tab), str(path))

        def changed(dirty):
            self.tabs.setTabText(
                self.tabs.indexOf(tab), label + (" *" if dirty else "")
            )

        tab.editor.document().modificationChanged.connect(changed)

    def open_source(self):
        name, _ = QFileDialog.getOpenFileName(
            self, "打开自己的UTF-8源码；不要选反编译稿", "", "Python (*.py)"
        )
        if name:
            try:
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
                        Path(name), reference=reply == QMessageBox.StandardButton.No
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
        if tab.reference:
            raise ValueError("参考稿不能保存为可信源码")
        save_source(tab.path, tab.editor.toPlainText(), [a.path for a in self.archives])
        tab.editor.document().setModified(False)

    def save_current(self):
        try:
            self.save_tab(self.current())
        except Exception as exc:
            self.fail(exc)

    def confirm_tab(self, tab):
        if not tab.editor.document().isModified():
            return True
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

    def associate(self):
        try:
            tab = self.editable()
            selected = self.selected()
            if not selected:
                raise ValueError("请选中包条目")
            archive, index = selected
            if tab.vm.currentData() != archive.vm:
                raise ValueError("源码的候选VM与条目不同，请先显式确认VM")
            if (
                QMessageBox.question(
                    self,
                    "确认来源（不证明与原模块一致）",
                    "关联仅记录您的源码选择，不验证反编译准确性。继续？",
                    defaultButton=QMessageBox.StandardButton.No,
                )
                != QMessageBox.StandardButton.Yes
            ):
                return

            def complete(binding):
                self.bindings = [
                    b
                    for b in self.bindings
                    if (b.archive, b.index) != (archive.path, index)
                ] + [binding]
                self.project_dirty = True
                self.info.setPlainText(
                    "已记录用户关联，未通过原生回读验证。请保存项目。"
                )

            self.task(lambda: Binding.associate(archive, index, tab.path), complete)
        except Exception as exc:
            self.fail(exc)

    def save_project(self):
        name, _ = QFileDialog.getSaveFileName(
            self,
            "保存关联项目（不复制包或源码）",
            "",
            "Script project (*.mxscript.json)",
        )
        if name:
            try:
                path = Path(name)
                if not name.endswith(".mxscript.json"):
                    path = Path(name + ".mxscript.json")
                save_project(path, self.bindings)
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
            "保存当前源码关联项目？",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Save:
            return self.save_project()
        return True

    def open_project(self):
        if not self.confirm_project():
            return
        name, _ = QFileDialog.getOpenFileName(
            self, "打开项目并检查包指纹", "", "Script project (*.mxscript.json)"
        )
        if name:

            def complete(bindings):
                self.bindings = bindings
                self.project_dirty = False
                for binding in bindings:
                    if not any(a.path == binding.archive for a in self.archives):
                        self.add_archive(ArchiveDocument(binding.archive))
                    self.add_source(binding.source, binding.vm)

            self.task(lambda: load_project(Path(name)), complete)

    def select_compiler(self):
        try:
            vm = self.current().vm.currentData()
            name, _ = QFileDialog.getOpenFileName(
                self, f"选择标准CPython {PROFILES[vm].version}"
            )
            if name:
                self.task(
                    lambda: inspect_compiler(Path(name), vm), self.register_compiler
                )
        except Exception as exc:
            self.fail(exc)

    def register_compiler(self, compiler):
        self.compilers[compiler.vm] = compiler
        self.info.setPlainText(
            f"{compiler.vm} / CPython {compiler.version} / "
            f"{compiler.bits}bit\n{compiler.executable}\n"
            f"SHA256 {compiler.sha256}\n仅编译，不执行目标模块。"
        )

    def check_bundled(self):
        try:
            vm = self.current().vm.currentData()
            self.task(
                lambda: bundled_compiler(vm, self.runtime_root), self.register_compiler
            )
        except Exception as exc:
            self.fail(exc)

    def compile(self):
        try:
            tab = self.editable()
            compiler = self.compilers.get(tab.vm.currentData())
            if compiler is None:
                raise ValueError("当前VM没有已验证的编译器；请先检查内置或显式选择")
            name, _ = QFileDialog.getSaveFileName(
                self, "仅生成标准pyc；不能直接用于游戏", "", "Standard bytecode (*.pyc)"
            )
            if not name:
                return
            target = Path(name if name.lower().endswith(".pyc") else name + ".pyc")
            text = tab.editor.toPlainText()
            protected = tuple(
                [a.path for a in self.archives]
                + [self.tabs.widget(i).path for i in range(self.tabs.count())]
            )
            self.task(
                lambda: compile_standard(
                    compiler, text, str(tab.path), target, protected
                ),
                lambda digest: self.info.setPlainText(
                    f"标准.pyc编译成功（未写原生包）\nSHA256 {digest}"
                ),
            )
        except Exception as exc:
            self.fail(exc)

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

    def find_next(self):
        if self.tabs.currentWidget() and self.find.text():
            editor = self.current().editor
            if not editor.find(self.find.text()):
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                editor.setTextCursor(cursor)
                editor.find(self.find.text())

    def replace_all(self):
        if (
            self.tabs.currentWidget()
            and self.find.text()
            and not self.current().reference
        ):
            editor = self.current().editor
            text = editor.toPlainText()
            changed = text.replace(self.find.text(), self.replacement.text())
            if changed != text:
                cursor = editor.textCursor()
                cursor.beginEditBlock()
                cursor.select(QTextCursor.SelectionType.Document)
                cursor.insertText(changed)
                cursor.endEditBlock()

    def closeEvent(self, event):
        if self.jobs or not all(
            self.confirm_tab(self.tabs.widget(i)) for i in range(self.tabs.count())
        ):
            event.ignore()
            return
        if not self.confirm_project():
            event.ignore()
            return
        for archive in self.archives:
            archive.close()
        event.accept()
