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
    QListWidget,
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
from ..core.guide_render import guide_html
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
        self.workspace_pages = QTabWidget()
        layout.addWidget(self.workspace_pages, 1)
        guide_page = QWidget()
        guide_layout = QVBoxLayout(guide_page)
        notice = QLabel(
            "先选实际任务，阅读流程、修改位置、检查方案及证据。"
            "专题草稿未独审，不把目录数/模块审核数当专题完成数。"
        )
        notice.setWordWrap(True)
        guide_layout.addWidget(notice)
        self.guide_query = QLineEdit()
        self.guide_query.setPlaceholderText(
            "找任务：公告、注册、验证码、Enter、退出、战斗…"
        )
        self.guide_query.setAccessibleName("开发专题搜索")
        guide_layout.addWidget(self.guide_query)
        guide_splitter = QSplitter()
        self.guide_list = QListWidget()
        self.guide_browser = QTextBrowser()
        self.guide_browser.setOpenLinks(False)
        self.guide_browser.setOpenExternalLinks(False)
        self.guide_browser.anchorClicked.connect(self.follow_link)
        guide_splitter.addWidget(self.guide_list)
        guide_splitter.addWidget(self.guide_browser)
        guide_splitter.setSizes([330, 920])
        guide_layout.addWidget(guide_splitter, 1)
        self.workspace_pages.addTab(guide_page, "开发任务 / 专题")
        module_page = QWidget()
        module_layout = QVBoxLayout(module_page)
        self.workspace_pages.addTab(module_page, "模块字典 / 目录")
        self.guide_query.textChanged.connect(self.filter_guides)
        self.guide_list.currentRowChanged.connect(self.select_guide)
        self.query = QLineEdit()
        self.query.setPlaceholderText(
            "搜索：中文功能 / 包内路径 / 函数名（多词同时匹配）"
        )
        self.query.setClearButtonEnabled(True)
        self.query.setAccessibleName("手册全文搜索")
        module_layout.addWidget(self.query)
        filters = QHBoxLayout()
        self.domain, self.review = QComboBox(), QComboBox()
        self.domain.addItem("全部领域", "")
        self.review.addItem("全部审核状态", "")
        for value, title in REVIEWS.items():
            self.review.addItem(title, value)
        filters.addWidget(self.domain)
        filters.addWidget(self.review)
        module_layout.addLayout(filters)
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
        module_layout.addWidget(splitter, 1)
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
            f"专题 {len(catalog.guides)} 篇草稿（非独审通过）；"
            "目录、模块说明、专题覆盖分别计，不是全量讲解。"
        )
        self.domain.blockSignals(True)
        self.domain.clear()
        self.domain.addItem("全部领域", "")
        for domain in sorted({row["domain"] for row in catalog.modules}):
            self.domain.addItem(domain, domain)
        self.domain.blockSignals(False)
        self.filter()
        self.filter_guides()
        if not self.catalog.guides:
            self.workspace_pages.setCurrentIndex(1)
        self.statusBar().showMessage(
            f"{catalog.baseline['analysis_id']} · {len(catalog.warnings)} 条警告 · 只读"
        )

    def filter_guides(self):
        if self.catalog is None:
            return
        self.guide_rows = self.catalog.search_guides(self.guide_query.text())
        self.guide_list.blockSignals(True)
        self.guide_list.clear()
        for guide in self.guide_rows:
            suffix = "（引用已过期）" if guide["stale_dependencies"] else "（草稿）"
            self.guide_list.addItem(guide["title"] + suffix)
        self.guide_list.blockSignals(False)
        if self.guide_rows:
            selected = getattr(self, "guide_selected_id", None)
            index = next(
                (i for i, g in enumerate(self.guide_rows) if g["id"] == selected), 0
            )
            self.guide_list.setCurrentRow(index)
        else:
            self.guide_browser.setPlainText(
                "没有匹配的开发专题；这里尚未覆盖该任务，不用函数名列表冒充讲解。"
            )

    def select_guide(self, index):
        if 0 <= index < len(getattr(self, "guide_rows", [])):
            self.guide_selected_id = self.guide_rows[index]["id"]
            self.guide_browser.setHtml(guide_html(self.guide_rows[index]))

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
        if url.fragment().startswith("guide-step-"):
            self.guide_browser.scrollToAnchor(url.fragment())
            return
        params = parse_qs(url.fragment())
        identity = params.get("module", [None])[0]
        if identity is None or self.catalog is None:
            return
        self.workspace_pages.setCurrentIndex(1)
        self.query.clear()
        self.domain.setCurrentIndex(0)
        self.review.setCurrentIndex(0)
        self.filter()
        for index, row in enumerate(self.model.rows):
            if row["id"] == identity:
                self.table.selectRow(index)
                section = params.get("section", ["overview"])[0]
                sections = ["overview", "functions", "resources", "evidence"]
                tab = sections.index(section) if section in sections else 0
                self.tabs.setCurrentIndex(tab)
                anchor = ""
                function = params.get("function", [None])[0]
                if section == "functions" and row["annotation"]:
                    for number, item in enumerate(row["annotation"]["functions"]):
                        if item["name"] == function:
                            anchor = f"function-{number}"
                            break
                if section == "evidence":
                    anchor = "evidence-" + params.get("evidence", [""])[0]
                if anchor:
                    self.browsers[tab].scrollToAnchor(anchor)
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
        coverage = self.catalog.coverage() if self.catalog else None
        scope = (
            f"当前目录{coverage['indexed']} / 说明{coverage['annotated']} / "
            f"有限通过{coverage['accepted']}。"
            if coverage
            else "目录未加载。"
        )
        QMessageBox.information(
            self,
            "关于",
            f"MXSJ 脚本开发手册 {__version__}\n"
            "独立只读工具；源码JSON是唯一底稿。\n"
            f"{scope}\n"
            "目录登记、函数记录、模块有限审核和专题草稿分别计，不是全量讲解。\n"
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
