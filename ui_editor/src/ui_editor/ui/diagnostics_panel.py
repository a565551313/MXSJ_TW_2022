"""静态诊断面板：刷新、按树路径定位、会话内标记有意设计。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.diagnostics import Diagnostic
from ..core.review import path_label


class DiagnosticsPanel(QWidget):
    refresh_requested = Signal()
    path_chosen = Signal(object)

    def __init__(self):
        super().__init__()
        self._issues: list[Diagnostic] = []
        self._ignored: set[int] = set()
        self._stale = True
        layout = QVBoxLayout(self)
        self._summary = QLabel("静态检查，非引擎真值；请刷新。")
        self._summary.setWordWrap(True)
        layout.addWidget(self._summary)
        buttons = QHBoxLayout()
        refresh = QPushButton("刷新诊断")
        refresh.clicked.connect(self.refresh_requested.emit)
        buttons.addWidget(refresh)
        self._ignore = QPushButton("标记为有意设计（本次结果）")
        self._ignore.clicked.connect(self._ignore_selected)
        buttons.addWidget(self._ignore)
        restore = QPushButton("显示所有提示")
        restore.clicked.connect(self._restore)
        buttons.addWidget(restore)
        layout.addLayout(buttons)
        self.table = QTreeWidget()
        self.table.setHeaderLabels(["级别", "规则", "控件位置/字段", "说明"])
        self.table.itemClicked.connect(self._locate)
        layout.addWidget(self.table)

    def reset(self) -> None:
        self._issues.clear()
        self._ignored.clear()
        self.table.clear()
        self.mark_stale()

    def mark_stale(self) -> None:
        self._stale = True
        self._ignore.setEnabled(False)
        self._summary.setText(
            "结果待刷新/已过期；定位已暂停。静态检查不能替代游戏验收。"
        )

    def set_issues(self, issues: list[Diagnostic]) -> None:
        self._issues = issues
        self._ignored.clear()
        self._stale = False
        self._ignore.setEnabled(True)
        self._render()

    def _render(self) -> None:
        self.table.clear()
        for index, issue in enumerate(self._issues):
            if index in self._ignored:
                continue
            location = (
                (path_label(issue.path) + " · ") if issue.path is not None else ""
            ) + issue.field
            row = QTreeWidgetItem([issue.severity, issue.code, location, issue.message])
            row.setData(0, Qt.ItemDataRole.UserRole, index)
            row.setToolTip(3, issue.message)
            self.table.addTopLevelItem(row)
        errors = sum(issue.severity == "错误" for issue in self._issues)
        warnings = sum(issue.severity == "警告" for issue in self._issues)
        self._summary.setText(
            f"错误 {errors} · 警告 {warnings} · 本次隐藏 {len(self._ignored)}。"
            "点行定位；刷新会恢复所有提示，不写入布局。"
        )

    def _locate(self, row, _column) -> None:
        if self._stale:
            return
        issue = self._issues[row.data(0, Qt.ItemDataRole.UserRole)]
        if issue.path is not None:
            self.path_chosen.emit(issue.path)

    def _ignore_selected(self) -> None:
        if self._stale:
            return
        for row in self.table.selectedItems():
            index = row.data(0, Qt.ItemDataRole.UserRole)
            issue = self._issues[index]
            if issue.severity != "错误" and issue.code != "STATIC_ONLY":
                self._ignored.add(index)
        self._render()

    def _restore(self) -> None:
        if self._stale:
            return
        self._ignored.clear()
        self._render()
