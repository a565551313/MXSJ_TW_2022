from __future__ import annotations

import re

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class Highlight(QSyntaxHighlighter):
    def highlightBlock(self, text):
        rules = [
            (
                r"\b(?:def|class|return|if|else|elif|try|except|finally|for|while|"
                r"import|from|as|pass|raise|with|yield|lambda|None|True|False|"
                r"and|or|not|in|is|print|exec|global|del|break|continue)\b",
                "#7053a6",
            ),
            (r"""(?:[uUrRbB])?(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')""", "#277148"),
            (r"#.*", "#777777"),
        ]
        for pattern, color in rules:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            for match in re.finditer(pattern, text):
                # Qt indexes UTF-16 units, not Python Unicode code points.
                start = len(text[: match.start()].encode("utf-16-le")) // 2
                length = len(match.group().encode("utf-16-le")) // 2
                self.setFormat(start, length, fmt)


class Gutter(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.gutter_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_gutter(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.gutter = Gutter(self)
        self.highlight = Highlight(self.document())
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.blockCountChanged.connect(self.update_margin)
        self.updateRequest.connect(self.update_gutter)
        self.update_margin()

    def gutter_width(self):
        return 12 + self.fontMetrics().horizontalAdvance("9") * len(
            str(max(1, self.blockCount()))
        )

    def update_margin(self, *_):
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def update_gutter(self, rect, dy):
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.gutter.setGeometry(
            QRect(rect.left(), rect.top(), self.gutter_width(), rect.height())
        )

    def paint_gutter(self, event):
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), self.palette().alternateBase())
        painter.setPen(self.palette().text().color())
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        while block.isValid() and top <= event.rect().bottom():
            height = round(self.blockBoundingRect(block).height())
            if block.isVisible() and top + height >= event.rect().top():
                painter.drawText(
                    0,
                    top,
                    self.gutter.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(number + 1),
                )
            top += height
            block = block.next()
            number += 1
