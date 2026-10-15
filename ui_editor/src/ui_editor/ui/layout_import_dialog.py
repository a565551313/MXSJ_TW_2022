"""本地布局导入的包内地址选择，不枚举未知 0SLF 名字。"""

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

from ..core.layout_import import validate_layout_path


class LayoutImportDialog(QDialog):
    def __init__(self, filename: str, paths: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入布局：包内完整路径")
        self.resize(660, 200)
        layout = QVBoxLayout(self)
        label = QLabel(
            f"本地文件：{filename}\n"
            "选择已有布局路径将确认替换；手填新路径将在保存时新增。\n"
            "只导入布局，不自动带图片，也不自动接脚本。"
        )
        label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(label)
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo.addItems(sorted(set(paths), key=str.casefold))
        completer = QCompleter(self.combo.model(), self.combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combo.setCompleter(completer)
        self.combo.setEditText(filename)
        layout.addWidget(self.combo)
        self.path = ""
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        try:
            self.path = validate_layout_path(self.combo.currentText())
        except ValueError as exc:
            QMessageBox.warning(self, "包内路径无效", str(exc))
            return
        super().accept()
