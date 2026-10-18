"""Editable content widgets; parsing and validation belong to core services."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TextPage(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title + " — 保存草稿不等于发布；严格 Big5 输出"))
        self.editor = QTextEdit()
        layout.addWidget(self.editor)


class ServersPage(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("五字段基础列表；reserve/type 为不透明字段，未开放可选 ID／附加段。")
        )
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["分组", "名称", "IPv4", "端口", "reserve", "type"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)
        controls = QHBoxLayout()
        for label, callback in [
            ("新增", self.add_row),
            ("删除", self.remove_row),
            ("上移", lambda: self.move(-1)),
            ("下移", lambda: self.move(1)),
        ]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            controls.addWidget(button)
        layout.addLayout(controls)
        self.table.itemChanged.connect(self.changed)

    def add_row(self, values=None):
        values = (
            values
            if isinstance(values, list)
            else ["測試區", "新區服", "127.0.0.1", "3134", "3", "&"]
        )
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, value in enumerate(values):
            self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.changed.emit()

    def remove_row(self):
        if self.table.currentRow() >= 0:
            self.table.removeRow(self.table.currentRow())
            self.changed.emit()

    def move(self, offset):
        row, target = self.table.currentRow(), self.table.currentRow() + offset
        if row < 0 or not 0 <= target < self.table.rowCount():
            return
        for column in range(6):
            a, b = self.table.takeItem(row, column), self.table.takeItem(target, column)
            self.table.setItem(row, column, b)
            self.table.setItem(target, column, a)
        self.table.setCurrentCell(target, 0)
        self.changed.emit()

    def apply(self, groups):
        self.table.setRowCount(0)
        for group in groups:
            for server in group["servers"]:
                self.add_row(
                    [
                        group["name"],
                        server["name"],
                        server["ip"],
                        server["port"],
                        server["reserve"],
                        server["type"],
                    ]
                )

    def value(self):
        groups = {}
        for row in range(self.table.rowCount()):
            values = [
                self.table.item(row, c).text() if self.table.item(row, c) else ""
                for c in range(6)
            ]
            groups.setdefault(values[0], []).append(
                {
                    "name": values[1],
                    "ip": values[2],
                    "port": int(values[3]),
                    "reserve": values[4],
                    "type": values[5],
                }
            )
        return [{"name": name, "servers": servers} for name, servers in groups.items()]
