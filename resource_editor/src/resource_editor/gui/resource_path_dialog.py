"""可搜索、可手填的包内路径选择；0SLF 仅列已识别路径，不编造名字。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from ..core.resource_paths import validate_resource_path


class ResourcePathDialog(QDialog):
    def __init__(self, filename: str, paths: list[str], default: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择包内资源路径")
        self.resize(680, 210)
        layout = QVBoxLayout(self)
        label = QLabel(
            f"导入文件：{filename}\n"
            "下拉仅列当前包已识别的路径，可输入关键词搜索，也可手填新路径。\n"
            "选已有路径会询问替换；新路径不会自动接到布局或脚本。"
        )
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo.addItems(sorted(set(paths), key=str.casefold))
        completer = QCompleter(self.combo.model(), self.combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combo.setCompleter(completer)
        self.combo.setEditText(default)
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.path = ""

    def accept(self) -> None:
        try:
            self.path = validate_resource_path(self.combo.currentText())
        except (ValueError, UnicodeEncodeError) as exc:
            QMessageBox.warning(self, "资源路径无效", str(exc))
            return
        super().accept()
