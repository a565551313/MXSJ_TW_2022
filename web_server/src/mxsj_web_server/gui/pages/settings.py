"""Separate public/admin network policies, editable without opening any socket."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Rules(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["IP／CIDR", "备注", "到期 Unix 秒（0 永久）"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)
        add, remove = QPushButton("新增规则"), QPushButton("删除选中规则")
        add.clicked.connect(lambda: self.add(["127.0.0.1/32", "", 0]))
        remove.clicked.connect(self.remove)
        layout.addWidget(add)
        layout.addWidget(remove)
        self.table.itemChanged.connect(self.changed)

    def remove(self):
        if self.table.currentRow() >= 0:
            self.table.removeRow(self.table.currentRow())
            self.changed.emit()

    def add(self, values):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, value in enumerate(values):
            self.table.setItem(row, i, QTableWidgetItem(str(value)))
        self.changed.emit()

    def apply(self, rules):
        self.table.setRowCount(0)
        for rule in rules:
            self.add([rule["cidr"], rule["note"], rule["expires"]])

    def value(self):
        rows = []
        for row in range(self.table.rowCount()):
            values = [self.table.item(row, i).text() for i in range(3)]
            rows.append(
                {"cidr": values[0], "note": values[1], "expires": int(values[2])}
            )
        return rows


class PolicyPage(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.host, self.origin = QLineEdit(), QLineEdit()
        self.port, self.limit = QSpinBox(), QSpinBox()
        self.port.setRange(1, 65535)
        self.limit.setRange(10, 10000)
        self.mode = QComboBox()
        for title, value in [
            ("不限制来源", "allow"),
            ("黑名单", "black"),
            ("白名单（拒绝优先）", "white"),
        ]:
            self.mode.addItem(title, value)
        for label, widget in [
            ("监听 IP", self.host),
            ("监听端口", self.port),
            ("对外地址（含协议）", self.origin),
            ("访问模式", self.mode),
            ("每 IP 每分钟上限", self.limit),
        ]:
            form.addRow(label, widget)
        layout.addLayout(form)
        self.rules = QTabWidget()
        self.black, self.white = Rules(), Rules()
        self.rules.addTab(self.black, "黑名单")
        self.rules.addTab(self.white, "白名单")
        layout.addWidget(self.rules)
        layout.addWidget(
            QLabel("可信反向代理 CIDR（每行一个；未列出的来源不能伪造转发 IP）：")
        )
        self.proxies = QTextEdit()
        self.proxies.setMaximumHeight(75)
        layout.addWidget(self.proxies)
        for widget in (self.host, self.origin, self.proxies):
            widget.textChanged.connect(self.changed)
        self.port.valueChanged.connect(self.changed)
        self.limit.valueChanged.connect(self.changed)
        self.mode.currentIndexChanged.connect(self.changed)
        self.black.changed.connect(self.changed)
        self.white.changed.connect(self.changed)

    def apply(self, raw):
        self.host.setText(raw["host"])
        self.port.setValue(raw["port"])
        self.origin.setText(raw["origin"])
        self.mode.setCurrentIndex(self.mode.findData(raw["mode"]))
        self.limit.setValue(raw["requests_per_minute"])
        self.black.apply(raw["black"])
        self.white.apply(raw["white"])
        self.proxies.setPlainText("\n".join(raw["trusted_proxies"]))

    def value(self):
        return {
            "host": self.host.text(),
            "port": self.port.value(),
            "origin": self.origin.text().rstrip("/"),
            "mode": self.mode.currentData(),
            "black": self.black.value(),
            "white": self.white.value(),
            "trusted_proxies": [
                line.strip()
                for line in self.proxies.toPlainText().splitlines()
                if line.strip()
            ],
            "requests_per_minute": self.limit.value(),
        }
