from __future__ import annotations

from functools import partial
from pathlib import Path
from urllib.parse import parse_qs

from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTableView,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core.catalog import load_catalog
from ..core.export import export_site
from ..core.render import REVIEWS, detail_html
from .jobs import Job
from .models import ModuleModel


class ManualWindow(QMainWindow):
    def __init__(self, content_root: Path, parent=None):
        super().__init__(parent)
        self.root, self.catalog, self.selected = content_root, None, None
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.jobs, self.token, self.closing = {}, 0, False
        self.setWindowTitle(f"MXSJ 客户端脚本开发手册 {__version__} · 阶段样板")
        self.resize(1280, 840)
        self._make_actions()
        self._make_workspace()
        self.statusBar().showMessage("正在加载结构化目录；不执行游戏源码…")
        self.load()

    def _make_actions(self):
        file_menu = self.menuBar().addMenu("文件(&F)")
        self.actions = []
        for title, shortcut, handler in (
            ("打开手册数据目录…", "Ctrl+O", self.open_content),
            ("重新校验并加载", "Ctrl+R", self.load),
            ("核对仓库证据摘要和行号…", "", self.verify_evidence),
            ("导出离线手册到新目录…", "Ctrl+E", self.export),
        ):
            action = QAction(title, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(lambda checked=False, fn=handler: fn())
            file_menu.addAction(action)
            self.actions.append(action)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        help_menu = self.menuBar().addMenu("帮助(&H)")
        help_menu.addAction("关于 / 使用边界", self.about)

    def _make_workspace(self):
        top = QWidget()
        layout = QVBoxLayout(top)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(10)
        layout.addWidget(QLabel("<h2>MXSJ / 客户端脚本手册</h2>"))
        self.coverage = QLabel("目录加载中…")
        self.coverage.setWordWrap(True)
        layout.addWidget(self.coverage)
        self.query = QLineEdit()
        self.query.setPlaceholderText(
            "搜索：中文功能 / 包内路径 / 函数名（多词同时匹配）"
        )
        self.query.setClearButtonEnabled(True)
        self.query.setAccessibleName("手册全文搜索")
        layout.addWidget(self.query)
        filters = QHBoxLayout()
        self.domain, self.review = QComboBox(), QComboBox()
        self.domain.addItem("全部领域", "")
        self.review.addItem("全部审核状态", "")
        for value, title in REVIEWS.items():
            self.review.addItem(title, value)
        filters.addWidget(self.domain)
        filters.addWidget(self.review)
        layout.addLayout(filters)
        splitter = QSplitter()
        self.table = QTableView()
        self.model = ModuleModel(self)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setWordWrap(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.setColumnWidth(1, 65)
        self.table.setColumnWidth(2, 110)
        self.tabs = QTabWidget()
        self.browsers = []
        for title in ("模块职责", "类与函数", "关联与修改", "证据与来源"):
            browser = QTextBrowser()
            browser.setOpenLinks(False)
            browser.setOpenExternalLinks(False)
            browser.anchorClicked.connect(self.follow_link)
            self.browsers.append(browser)
            self.tabs.addTab(browser, title)
        splitter.addWidget(self.table)
        splitter.addWidget(self.tabs)
        splitter.setSizes([520, 730])
        layout.addWidget(splitter, 1)
        self.setCentralWidget(top)
        self.setStyleSheet(
            "QMainWindow{background:#f2f5f9;}"
            "QLineEdit,QComboBox{padding:6px;border:1px solid #c4d2df;"
            "border-radius:4px;background:white;}"
            "QTextBrowser{background:white;border:1px solid #cfdae4;padding:12px;}"
            "QTableView{background:white;alternate-background-color:#f4f7fa;"
            "border:1px solid #cfdae4;selection-background-color:#d9eaf7;"
            "selection-color:#153d5a;}"
            "QTabBar::tab{padding:8px 14px;}"
        )
        self.table.selectionModel().currentRowChanged.connect(self.select)
        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(160)
        self.debounce.timeout.connect(self.filter)
        self.query.textChanged.connect(lambda: self.debounce.start())
        self.domain.currentIndexChanged.connect(self.filter)
        self.review.currentIndexChanged.connect(self.filter)

    def _start(self, function, callback):
        self.token += 1
        job = Job(self.token, function)
        self.jobs[self.token] = (job, callback)
        job.signals.finished.connect(self._finished)
        for action in self.actions:
            action.setEnabled(False)
        self.pool.start(job)

    def _finished(self, token, result, error):
        _, callback = self.jobs.pop(token)
        if not self.jobs:
            for action in self.actions:
                action.setEnabled(True)
        if self.closing:
            if not self.jobs:
                self.close()
            return
        if error:
            self.statusBar().showMessage("失败：保留当前手册；详细原因见错误窗口。")
            message = QMessageBox(self)
            message.setWindowTitle("手册操作失败（未执行游戏源码）")
            message.setText(error.strip().splitlines()[-1])
            message.setDetailedText(error)
            message.exec()
        else:
            callback(result)

    def load(self, repository=None, *, root=None):
        if self.jobs:
            return
        self.statusBar().showMessage("后台校验并加载…")
        root = self.root if root is None else root
        self._start(
            partial(load_catalog, root, repository=repository),
            lambda catalog: self.loaded(catalog, root),
        )

    def loaded(self, catalog, root):
        self.root, self.catalog = root, catalog
        coverage = catalog.coverage()
        self.coverage.setText(
            f"阶段样板 · 目录 {coverage['indexed']}/{coverage['expected_entries']} · "
            f"已写说明 {coverage['annotated']} · 审核通过 {coverage['accepted']} · "
            "自动提取 / 推测 / 作者静态核对 / 实机记录分别标注，不能互相替代。"
        )
        self.domain.blockSignals(True)
        self.domain.clear()
        self.domain.addItem("全部领域", "")
        for domain in sorted({row["domain"] for row in catalog.modules}):
            self.domain.addItem(domain, domain)
        self.domain.blockSignals(False)
        self.filter()
        self.statusBar().showMessage(
            f"{catalog.baseline['analysis_id']} · {len(catalog.warnings)} 条警告 · 只读"
        )

    def filter(self):
        if self.catalog is None:
            return
        rows = self.catalog.search(
            self.query.text(), self.domain.currentData(), self.review.currentData()
        )
        self.model.replace(rows)
        if rows:
            self.table.selectRow(0)
        else:
            self.selected = None
            for browser in self.browsers:
                browser.setPlainText(
                    "没有匹配结果。目录不完整，搜不到不等于功能不存在。"
                )
        self.statusBar().showMessage(f"匹配 {len(rows)} 个模块；主列表按路径显示。")

    def select(self, index, previous=None):
        if not index.isValid() or index.row() >= len(self.model.rows):
            return
        self.selected = self.model.rows[index.row()]
        for browser, section in zip(
            self.browsers,
            ("overview", "functions", "resources", "evidence"),
            strict=True,
        ):
            browser.setHtml(detail_html(self.selected, section))

    def follow_link(self, url):
        identity = parse_qs(url.fragment()).get("module", [None])[0]
        if identity is None or self.catalog is None:
            return
        self.query.clear()
        self.domain.setCurrentIndex(0)
        self.review.setCurrentIndex(0)
        self.filter()
        for index, row in enumerate(self.model.rows):
            if row["id"] == identity:
                self.table.selectRow(index)
                self.tabs.setCurrentIndex(0)
                return
        self.statusBar().showMessage("关联模块尚未编入本阶段目录。")

    def open_content(self):
        name = QFileDialog.getExistingDirectory(
            self, "选择含coordination/schema的手册目录"
        )
        if name:
            self.load(root=Path(name))

    def verify_evidence(self):
        name = QFileDialog.getExistingDirectory(self, "选择证据所属仓库根目录（只读）")
        if name:
            self.load(repository=Path(name))

    def export(self):
        if self.catalog is None:
            return
        name, _ = QFileDialog.getSaveFileName(
            self,
            "导出目录名称（必须不存在，不是HTML文件名）",
            str(Path.home() / "MXSJ脚本手册"),
        )
        if name:
            self._start(
                partial(export_site, self.catalog, Path(name), content_root=self.root),
                lambda path: self.statusBar().showMessage(f"已导出：{path}"),
            )

    def about(self):
        QMessageBox.information(
            self,
            "关于",
            f"MXSJ 脚本开发手册 {__version__}\n"
            "独立只读工具；源码JSON是唯一底稿。\n"
            "目前20条目录和1份待复核格式样板，不是全量说明。\n"
            "来源摘要/行号校验不代表反编译正确，不运行游戏脚本。\n"
            "Windows/EXE/游戏验收尚未进行。",
        )

    def closeEvent(self, event):
        if self.jobs:
            self.closing = True
            self.statusBar().showMessage("正在等候当前只读任务结束后关闭…")
            event.ignore()
        else:
            self.pool.waitForDone()
            event.accept()
