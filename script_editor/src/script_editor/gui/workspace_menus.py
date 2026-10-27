"""Menus and toolbar: three ideas, no jargon.

The editor is a place to open a package, edit a module and put the bytes back.
Everything else is either an export or a diagnostic. The menu tree is therefore
deliberately small:

* 文件 — local ``.py`` files and ``.fls`` packages, save, exit;
* 语料 — dump a package's entries (decrypted or as stored);
* 编辑 — the usual editor commands plus find/replace;
* 编码 — MBCS byte literals (unchanged);
* 编译 — **写入原包** (F5) and **生成新包** (F6), one click each;
* 视图 — dock visibility.

There is no mode switch and no "association" step: a recovery draft is verified
and bound automatically (see :mod:`script_editor.gui.module_actions`).
"""

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
            file_menu, "new_file", "新建 .py 文件…", self.new_source_file,
            "Ctrl+N", sp.SP_FileIcon,
        )
        self.action(
            file_menu, "open_source", "打开 .py 文件…", self.open_source,
            "Ctrl+Shift+O", sp.SP_FileIcon,
        )
        self.action(
            file_menu, "open_source_dir", "打开 .py 目录…", self.open_source_dir,
        )
        file_menu.addSeparator()
        self.action(
            file_menu, "save", "保存", self.save_current,
            "Ctrl+S", sp.SP_DialogSaveButton,
        )
        self.action(
            file_menu, "save_as", "另存为…", self.save_source_as,
            "Ctrl+Shift+S", sp.SP_DialogSaveButton,
        )
        file_menu.addSeparator()
        self.action(
            file_menu, "open_pack", "打开脚本文件…", self.open_archive,
            "Ctrl+O", sp.SP_DirOpenIcon,
        )
        self.action(
            file_menu, "open_pack_dir", "打开脚本目录…", self.open_archive_dir,
            None, sp.SP_DirIcon,
        )
        self.action(
            file_menu, "reload_packs", "重新读取已打开的包（改名/替换后用）",
            self.reload_archives, None, sp.SP_BrowserReload,
        )
        file_menu.addSeparator()
        self.action(file_menu, "quit", "退出", self.close, "Ctrl+Q")

        corpus = self.menuBar().addMenu("语料")
        self.action(
            corpus, "export_decrypted", "导出全量解密语料…",
            lambda: self.export_corpus(encrypted=False),
        )
        self.action(
            corpus, "export_encrypted", "导出全量加密语料…",
            lambda: self.export_corpus(encrypted=True),
        )

        edit = self.menuBar().addMenu("编辑")
        self.action(
            edit, "undo", "撤销", lambda: self.edit_command("undo"),
            "Ctrl+Z", sp.SP_ArrowBack,
        )
        self.action(
            edit, "redo", "恢复", lambda: self.edit_command("redo"),
            "Ctrl+Y", sp.SP_ArrowForward,
        )
        edit.addSeparator()
        self.action(
            edit, "cut", "剪切", lambda: self.edit_command("cut"), "Ctrl+X"
        )
        self.action(
            edit, "copy", "复制", lambda: self.edit_command("copy"), "Ctrl+C"
        )
        self.action(
            edit, "paste", "粘贴", lambda: self.edit_command("paste"), "Ctrl+V"
        )
        edit.addSeparator()
        self.action(
            edit, "find", "查找…", self.show_search, "Ctrl+F",
            sp.SP_FileDialogContentsView,
        )
        self.action(
            edit, "replace", "替换…", self.show_replace, "Ctrl+H",
            sp.SP_FileDialogContentsView,
        )
        edit.addSeparator()
        self.action(
            edit, "find_in_files", "在文件中查找…", self.find_in_files,
            "Ctrl+Shift+F",
        )
        self.action(
            edit, "replace_in_files", "在文件中替换…", self.replace_in_files,
            "Ctrl+Shift+H",
        )

        encoding = self.menuBar().addMenu("编码")
        self.action(
            encoding, "big5", "选中文案 → Big5 字节…", lambda: self.encode("big5")
        )
        self.action(
            encoding, "gbk", "选中路径 → GBK 字节…", lambda: self.encode("gbk")
        )
        encoding.addSeparator()
        self.action(
            encoding, "literals", "字节字面量 → 可读对照（只读）…",
            self.preview_byte_literals, None, sp.SP_FileDialogDetailedView,
        )

        build = self.menuBar().addMenu("编译")
        self.write_action = self.action(
            build, "write", "写入原包", self.write_in_place,
            "F5", sp.SP_DialogSaveButton,
        )
        self.generate_action = self.action(
            build, "generate", "生成新包", self.generate_new_package,
            "F6", sp.SP_ArrowRight,
        )
        # Historical name used by the window's refresh plumbing.
        self.native_action = self.generate_action

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

        self.menu_handles = [file_menu, corpus, edit, encoding, build, view]
        # Keep menuAction wrappers alive during action enumeration (Qt ownership).
        self.menu_actions = [menu.menuAction() for menu in self.menu_handles]

        # Compiler self-check is a diagnostic, not a build step: it lives on
        # the toolbar only, so the 编译 menu stays two plain verbs.
        check = QAction("检查编译器", self)
        check.setIcon(self.style().standardIcon(sp.SP_BrowserReload))
        check.setToolTip("重新核验两套内置 CPython 编译器（版本 / 魔数 / 整套 SHA）")
        check.triggered.connect(self.initialize_compilers)
        self.ui_actions["check"] = check

        toolbar = QToolBar("常用操作", self)
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(23, 23))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        short = {
            "open_pack": "打开",
            "open_pack_dir": "目录",
            "save": "保存",
            "undo": "撤销",
            "redo": "恢复",
            "find": "查找",
            "write": "写入原包",
            "generate": "生成新包",
            "check": "检查编译器",
        }
        for key in short:
            action = self.ui_actions[key]
            action.setIconText(short[key])
            if key in {"save", "find"}:
                toolbar.addSeparator()
            toolbar.addAction(action)
