"""IDE workspace assembly, no file/VM transformations in the UI layer."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from .workspace_actions import WorkspaceActions
from .workspace_menus import WorkspaceMenus


class Workspace(WorkspaceActions, WorkspaceMenus):
    def dock(self, name, title, widget, area):
        dock = QDockWidget(title, self)
        dock.setObjectName(name)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        return dock

    def build_workspace(self):
        self.setDockNestingEnabled(True)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["条目下标 / 记录身份", "字节"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 205)
        self.tree.setUniformRowHeights(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.package_menu)
        self.tree.itemDoubleClicked.connect(lambda *_: self.open_associated())
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("搜索条目 ID / data 路径…")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self.filter_tree)
        navigation = QWidget()
        nav_box = QVBoxLayout(navigation)
        nav_box.setContentsMargins(6, 6, 6, 6)
        self.archive_selector = QComboBox()
        self.archive_selector.addItem("全部已打开的包", None)
        self.archive_selector.currentIndexChanged.connect(self.select_archive_scope)
        nav_box.addWidget(self.archive_selector)
        nav_box.addWidget(self.filter)
        nav_box.addWidget(self.tree)
        self.package_count = QLabel("尚未打开包 · 原包只读")
        nav_box.addWidget(self.package_count)
        self.package_dock = self.dock(
            "packages", "包与模块", navigation, Qt.DockWidgetArea.LeftDockWidgetArea
        )

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.welcome = self.welcome_page()
        self.pages = QStackedWidget()
        self.pages.addWidget(self.welcome)
        self.pages.addWidget(self.tabs)
        center = QWidget()
        box = QVBoxLayout(center)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        box.addWidget(self.pages, 1)
        self.search_bar = QWidget()
        search = QVBoxLayout(self.search_bar)
        find_row, replace_row = QHBoxLayout(), QHBoxLayout()
        self.find = QLineEdit()
        self.find.setPlaceholderText("查找文本")
        self.find.returnPressed.connect(self.find_next)
        self.replacement = QLineEdit()
        self.replacement.setPlaceholderText("替换为")
        self.match_case = QCheckBox("区分大小写")
        self.match_case.setChecked(True)
        self.whole_words = QCheckBox("整词")
        find_row.addWidget(self.find, 1)
        find_row.addWidget(self.match_case)
        find_row.addWidget(self.whole_words)
        replace_row.addWidget(self.replacement, 1)
        for title, callback, row in [
            ("上一个", self.find_previous, find_row),
            ("下一个", self.find_next, find_row),
            ("关闭", self.search_bar.hide, find_row),
            ("替换", self.replace_current, replace_row),
            ("全部替换", self.replace_all, replace_row),
        ]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            row.addWidget(button)
        search.addLayout(find_row)
        search.addLayout(replace_row)
        box.addWidget(self.search_bar)
        self.search_bar.hide()
        self.setCentralWidget(center)

        self.properties = QTreeWidget()
        self.properties.setHeaderLabels(["属性", "值"])
        self.properties.setColumnWidth(0, 90)
        self.properties.setAlternatingRowColors(True)
        self.property_dock = self.dock(
            "properties",
            "来源与状态",
            self.properties,
            Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self.symbols = QTreeWidget()
        self.symbols.setHeaderLabels(["类 / 函数", "行"])
        self.symbols.setColumnWidth(0, 190)
        self.symbols.itemActivated.connect(self.jump_item)
        self.symbols.itemClicked.connect(self.jump_item)
        self.outline_dock = self.dock(
            "outline", "源码大纲", self.symbols, Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.splitDockWidget(
            self.property_dock, self.outline_dock, Qt.Orientation.Vertical
        )

        self.info = QPlainTextEdit()
        self.info.setReadOnly(True)
        self.info.setPlaceholderText("操作结果、编译器自检及失败原因显示在这里。")
        self.references = QTreeWidget()
        self.references.setHeaderLabels(
            ["行", "类型（静态线索，未挂载验证）", "引用内容"]
        )
        self.references.setColumnWidth(0, 50)
        self.references.setColumnWidth(1, 230)
        self.references.itemActivated.connect(self.jump_item)
        self.references.itemClicked.connect(self.jump_item)
        self.diff = QPlainTextEdit()
        self.diff.setReadOnly(True)
        self.diff.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output_tabs = QTabWidget()
        self.output_tabs.addTab(self.info, "操作与诊断")
        self.output_tabs.addTab(self.references, "布局 / 控件引用")
        self.output_tabs.addTab(self.diff, "源码差异 · 对比打开时")
        self.output_dock = self.dock(
            "output",
            "检查工作台",
            self.output_tabs,
            Qt.DockWidgetArea.BottomDockWidgetArea,
        )
        self.resizeDocks(
            [self.package_dock, self.property_dock],
            [280, 290],
            Qt.Orientation.Horizontal,
        )
        self.resizeDocks([self.output_dock], [190], Qt.Orientation.Vertical)
        self.cursor_status, self.file_status, self.compiler_status = (
            QLabel(),
            QLabel(),
            QLabel(),
        )
        for label in (self.compiler_status, self.file_status, self.cursor_status):
            label.setContentsMargins(10, 0, 10, 0)
            self.statusBar().addPermanentWidget(label)
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.setInterval(220)
        self.analysis_timer.timeout.connect(self.analyze_source)
        self.ui_actions = {}

    def welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(46, 30, 46, 30)
        layout.addStretch()
        title = QLabel("MXSJ 脚本工作台")
        font = title.font()
        font.setPointSize(25)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        subtitle = QLabel("SCRIPT  ·  CPython 2.5.6     /     DATA  ·  CPython 2.7.13")
        layout.addWidget(subtitle)
        layout.addSpacing(24)
        for text, detail, callback in [
            ("打开脚本包", "只读浏览 script.fls / data.fls", self.open_archive),
            ("打开可信源码", "编辑自己的 UTF-8 .py，不执行模块", self.open_source),
            ("继续已有项目", "恢复包与源码关联，继续生成新包", self.open_project),
            ("打开只读参考", "参考稿不参与保存、关联或编译", self.open_reference),
        ]:
            row = QHBoxLayout()
            button = QPushButton(text)
            button.setMinimumSize(145, 35)
            button.clicked.connect(callback)
            row.addWidget(button)
            row.addWidget(QLabel(detail), 1)
            layout.addLayout(row)
        layout.addSpacing(28)
        note = QLabel(
            "工作流\n打开包与源码 → 核对 VM → 关联条目 → 预编译清单\n"
            "→ 生成新名字的包\n\n"
            "保存 .py、保存项目、生成游戏包彼此独立。\n"
            "原包只读；无可信源码的条目不自动反编译。"
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def reset_workspace(self):
        for dock, area in [
            (self.package_dock, Qt.DockWidgetArea.LeftDockWidgetArea),
            (self.property_dock, Qt.DockWidgetArea.RightDockWidgetArea),
            (self.outline_dock, Qt.DockWidgetArea.RightDockWidgetArea),
            (self.output_dock, Qt.DockWidgetArea.BottomDockWidgetArea),
        ]:
            dock.setFloating(False)
            self.addDockWidget(area, dock)
            dock.show()
        self.splitDockWidget(
            self.property_dock, self.outline_dock, Qt.Orientation.Vertical
        )
        self.resizeDocks(
            [self.package_dock, self.property_dock],
            [280, 290],
            Qt.Orientation.Horizontal,
        )
        self.resizeDocks([self.output_dock], [190], Qt.Orientation.Vertical)
