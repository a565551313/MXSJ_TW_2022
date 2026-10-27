"""Read-only dialog for the byte-literal对照 report.

Everything shown here is display only.  The decoded text is never written back
to a source file, a project document or a package, because the client compares
the original MBCS bytes at run time.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ..core.inspection.legacy_text import DISPLAY_ONLY, report_text


class LiteralReportDialog(QDialog):
    """Non-modal, copyable comparison report.  No editing, no saving."""

    def __init__(self, parent=None, records=(), title=""):
        super().__init__(parent)
        self.setWindowTitle("字节字面量可读对照（只读）")
        self.resize(980, 720)
        self.setModal(False)
        text, truncated = report_text(records, title)
        self.body = QPlainTextEdit(self)
        self.body.setReadOnly(True)
        self.body.setPlainText(text)
        self.body.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        note = QLabel(DISPLAY_ONLY + ("（列表已截断）" if truncated else ""), self)
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.PlainText)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        copy = QPushButton("复制全部", self)
        buttons.addButton(copy, QDialogButtonBox.ButtonRole.ActionRole)
        copy.clicked.connect(
            lambda: QGuiApplication.clipboard().setText(self.body.toPlainText())
        )
        buttons.rejected.connect(self.close)
        layout = QVBoxLayout(self)
        layout.addWidget(note)
        layout.addWidget(self.body, 1)
        layout.addWidget(buttons)
