from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QStyle, QToolBar


class WorkspaceMenus:
    def action(self, menu, key, text, callback, shortcut=None, icon=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(self.style().standardIcon(icon))
        action.triggered.connect(callback)
        menu.addAction(action)
        self.ui_actions[key] = action
        return action

    def build_menus(self):
        sp = QStyle.StandardPixmap
        file_menu = self.menuBar().addMenu("文件")
        self.action(
            file_menu,
            "open_pack",
            "打开脚本包…",
            self.open_archive,
            "Ctrl+O",
            sp.SP_DirOpenIcon,
        )
        self.action(
            file_menu,
            "open_source",
            "打开可信源码…",
            self.open_source,
            "Ctrl+Shift+O",
            sp.SP_FileIcon,
        )
        self.action(file_menu, "reference", "打开只读参考…", self.open_reference)
        file_menu.addSeparator()
        self.action(
            file_menu,
            "save",
            "保存当前源码",
            self.save_current,
            "Ctrl+S",
            sp.SP_DialogSaveButton,
        )
        self.action(
            file_menu,
            "save_project",
            "保存项目…",
            self.save_project,
            "Ctrl+Shift+S",
            sp.SP_DialogSaveButton,
        )
        self.action(
            file_menu, "project", "打开项目…", self.open_project, None, sp.SP_DirIcon
        )
        corpus = self.menuBar().addMenu("恢复语料")
        self.action(corpus, "import_corpus", "导入全量候选清单…", self.import_corpus)
        self.action(
            corpus, "data_corpus", "生成data全量候选清单…", self.generate_data_corpus
        )
        self.action(
            corpus, "corpus_entry", "另开当前条目的语料候选", self.open_corpus_module
        )
        self.action(
            corpus,
            "verified_keys",
            "核验修复参数并另存新目录…",
            self.export_verified_catalog,
        )
        edit = self.menuBar().addMenu("编辑")
        self.action(
            edit,
            "undo",
            "撤销",
            lambda: self.edit_command("undo"),
            "Ctrl+Z",
            sp.SP_ArrowBack,
        )
        self.action(
            edit,
            "redo",
            "重做",
            lambda: self.edit_command("redo"),
            "Ctrl+Y",
            sp.SP_ArrowForward,
        )
        edit.addSeparator()
        self.action(
            edit,
            "find",
            "查找 / 替换",
            self.show_search,
            "Ctrl+F",
            sp.SP_FileDialogContentsView,
        )
        self.action(edit, "goto", "转到行…", self.goto_line, "Ctrl+G")
        encoding = self.menuBar().addMenu("编码")
        self.action(
            encoding, "big5", "选中文案 → Big5 字节…", lambda: self.encode("big5")
        )
        self.action(encoding, "gbk", "选中路径 → GBK 字节…", lambda: self.encode("gbk"))
        build = self.menuBar().addMenu("编译")
        self.action(
            build,
            "associate",
            "关联源码到选中条目…",
            self.associate,
            None,
            sp.SP_FileLinkIcon,
        )
        self.action(build, "catalog", "选择当前包的 XOR 目录…", self.configure_catalog)
        self.native_action = self.action(
            build,
            "native",
            "生成原生新包：预编译与清单…",
            self.preview_native,
            "F6",
            sp.SP_ArrowRight,
        )
        build.addSeparator()
        self.action(build, "standard", "仅导出标准 .pyc…", self.compile)
        self.action(
            build,
            "check",
            "重新检查两套内置编译器",
            self.initialize_compilers,
            None,
            sp.SP_BrowserReload,
        )
        self.action(
            build, "developer", "选择当前 VM 的开发编译器…", self.select_compiler
        )
        view = self.menuBar().addMenu("视图")
        self.dock_actions = []
        for dock in (
            self.package_dock,
            self.property_dock,
            self.outline_dock,
            self.output_dock,
        ):
            toggle = dock.toggleViewAction()
            self.dock_actions.append(toggle)
            view.addAction(toggle)
        view.addSeparator()
        self.action(view, "reset", "恢复默认工作区", self.reset_workspace)
        self.menu_handles = [file_menu, edit, encoding, build, view]
        # Keep menuAction wrappers alive during action enumeration (Qt ownership).
        self.menu_actions = [menu.menuAction() for menu in self.menu_handles]
        toolbar = QToolBar("常用操作", self)
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(23, 23))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        short = {
            "open_pack": "打开包",
            "open_source": "打开源码",
            "save": "保存源码",
            "project": "打开项目",
            "save_project": "保存项目",
            "undo": "撤销",
            "redo": "重做",
            "find": "查找",
            "associate": "关联条目",
            "native": "生成新包",
            "check": "检查编译器",
        }
        for key in short:
            action = self.ui_actions[key]
            action.setIconText(short[key])
            toolbar.addAction(action)
            if key in {"save_project", "find"}:
                toolbar.addSeparator()
