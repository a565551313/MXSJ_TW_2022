from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.compiler.profiles import PROFILES
from .code_editor import CodeEditor


class SourceTab(QWidget):
    def __init__(
        self, path: Path, text: str, vm="py25", reference=False, source_kind=None
    ):
        super().__init__()
        self.path, self.reference, self.opened_text = path, reference, text
        self.source_kind = source_kind or ("reference" if reference else "authored")
        self.recovery = None
        self.draft_saved = path.is_file()
        self.editor = CodeEditor()
        self.editor.setPlainText(text)
        self.editor.setReadOnly(reference)
        self.editor.document().setModified(False)
        self.vm = QComboBox()
        for key, profile in PROFILES.items():
            self.vm.addItem(profile.label, key)
        self.vm.setCurrentIndex(self.vm.findData(vm))
        self.vm.setEnabled(not reference)
        self.vm.setToolTip("显式选择编译VM；不会自动转换源码或字节码")
        path_label = self.path_label = QLabel(str(path))
        path_label.setToolTip(str(path))
        path_label.setWordWrap(True)
        path_label.setTextFormat(Qt.TextFormat.PlainText)
        mode = self.mode_label = QLabel()
        self.update_mode()
        mode.setObjectName("sourceMode")
        header = QHBoxLayout()
        self.adopt_button = QPushButton("检查并采用为源码…")
        self.adopt_button.setVisible(self.source_kind == "recovered-draft")
        header.addWidget(mode)
        header.addWidget(self.adopt_button)
        header.addStretch()
        header.addWidget(self.vm)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 2)
        layout.addLayout(header)
        if "# uncompyle6 version 3.9.3" in text[:1024]:
            warning = self.legacy_warning = QLabel(
                "旧恢复引擎可能把集合常量值写成下标。请保留修改，重新从包恢复后对比合并并核验；不自动覆盖此稿。"
            )
            warning.setWordWrap(True)
            warning.setTextFormat(Qt.TextFormat.PlainText)
            layout.addWidget(warning)
        layout.addWidget(path_label)
        layout.addWidget(self.editor, 1)

    def update_mode(self):
        names = {
            "authored": "用户确认源码 · UTF-8",
            "reference": "只读参考 · 禁止编译",
            "recovered-draft": "恢复草稿 · 可编辑 · 未核验，不能直接写包",
            "recovered-reviewed": "人工核对的恢复源码 · 客户端语义未验收",
            "module-unavailable": "包内条目 · 尚不能恢复源码，详见模块信息",
        }
        self.mode_label.setText(names[self.source_kind])
        if hasattr(self, "adopt_button"):
            self.adopt_button.setVisible(self.source_kind == "recovered-draft")

    def attach_report(self, report):
        import json

        self.recovery = report
        self.vm.setEnabled(False)
        self.path_label.setText(
            "恢复来源（原包）："
            f"{report.archive.name} · #{report.index} · {report.identity}\n"
            + repr(bytes.fromhex(report.filename_hex))
        )
        body = QTabWidget()
        self.layout().removeWidget(self.editor)
        body.addTab(self.editor, "恢复草稿" if report.source else "读取结果")
        for title, text in (
            (
                "反汇编",
                report.disassembly
                or "未生成标准字节码反汇编；请看模块信息中的具体原因。",
            ),
            ("模块信息", json.dumps(report.metadata(), ensure_ascii=False, indent=2)),
        ):
            pane = QPlainTextEdit()
            pane.setReadOnly(True)
            pane.setPlainText(text)
            body.addTab(pane, title)
        self.layout().addWidget(body, 1)
        self.module_pages = body
