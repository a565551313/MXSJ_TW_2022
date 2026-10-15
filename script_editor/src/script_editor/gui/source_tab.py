from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..core.compiler.profiles import PROFILES
from .code_editor import CodeEditor


class SourceTab(QWidget):
    def __init__(self, path: Path, text: str, vm="py25", reference=False):
        super().__init__()
        self.path, self.reference, self.opened_text = path, reference, text
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
        path_label = QLabel(str(path))
        path_label.setToolTip(str(path))
        path_label.setWordWrap(True)
        path_label.setTextFormat(Qt.TextFormat.PlainText)
        mode = QLabel("只读参考 · 禁止编译" if reference else "可信源码 · UTF-8")
        mode.setObjectName("sourceMode")
        header = QHBoxLayout()
        header.addWidget(mode)
        header.addStretch()
        header.addWidget(self.vm)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 2)
        layout.addLayout(header)
        layout.addWidget(path_label)
        layout.addWidget(self.editor, 1)
