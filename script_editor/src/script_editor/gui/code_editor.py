from __future__ import annotations

import re
from array import array
from itertools import accumulate

from PySide6.QtCore import QEvent, QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFontDatabase,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QToolTip, QWidget

from ..core.inspection.legacy_text import hint_for_position, readings


class Highlight(QSyntaxHighlighter):
    # Consume strings and comments together, so a # inside a string isn't a comment.
    tokens = re.compile(
        r"(?P<triple>[uUrRbB]{0,2}(?:\"\"\"|'''))"
        r"|(?P<string>[uUrRbB]{0,2}(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'))"
        r"|(?P<comment>\#.*)"
        r"|(?P<word>\b[A-Za-z_]\w*\b)"
        r"|(?P<number>\b(?:0[xX][0-9a-fA-F]+|[0-9]+(?:\.[0-9]+)?)[lLjJ]?\b)"
    )
    keywords = set(
        "def class return if else elif try except finally for while import from as "
        "pass raise with yield lambda None True False and or not in is print exec "
        "global del break continue assert except finally".split()
    )
    colors = {
        "triple": "#287148",
        "string": "#287148",
        "comment": "#7a8394",
        "word": "#7053a6",
        "number": "#ad6416",
    }

    def color(self, text, start, end, kind):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.colors[kind]))
        begin = self.units[start]
        length = self.units[end] - begin
        self.setFormat(begin, length, fmt)
        if kind in ("triple", "string") and "\\x" in text[start:end]:
            self.mark_readable(begin, length, text[start:end])

    def mark_readable(self, begin, length, literal):
        """Dotted underline marks bytes with a readable MBCS reading.

        This is a hint that a hover preview exists; the text itself is
        untouched, and nothing here can modify or re-emit the literal.
        """
        if not readings(literal):
            return
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self.colors["string"]))
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.DotLine)
        fmt.setUnderlineColor(QColor("#2f6f4f"))
        self.setFormat(begin, length, fmt)

    @staticmethod
    def closing(text, delimiter, start=0):
        while (end := text.find(delimiter, start)) >= 0:
            before = text[:end]
            if (len(before) - len(before.rstrip("\\"))) % 2 == 0:
                return end
            start = end + 1
        return -1

    def highlightBlock(self, text):
        self.units = array(
            "I", accumulate((2 if ord(c) > 0xFFFF else 1 for c in text), initial=0)
        )
        state, pos = self.previousBlockState(), 0
        self.setCurrentBlockState(0)
        if state in (1, 2):
            delimiter = "'" * 3 if state == 1 else '"' * 3
            end = self.closing(text, delimiter)
            if end < 0:
                self.color(text, 0, len(text), "triple")
                self.setCurrentBlockState(state)
                return
            pos = end + 3
            self.color(text, 0, pos, "triple")
        while match := self.tokens.search(text, pos):
            kind, end = match.lastgroup, match.end()
            if kind == "triple":
                delimiter = match.group()[-3:]
                close = self.closing(text, delimiter, end)
                if close < 0:
                    self.setCurrentBlockState(1 if delimiter.startswith("'") else 2)
                    self.color(text, match.start(), len(text), kind)
                    return
                end = close + 3
            if kind != "word" or match.group() in self.keywords:
                self.color(text, match.start(), end, kind)
            pos = end


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
        self.setMouseTracking(True)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setCenterOnScroll(True)
        self._match_block = None
        self._match_range = None
        self.cursorPositionChanged.connect(self.highlight_line)
        # Offsets go stale the moment the text changes; a highlight on the
        # wrong characters is worse than no highlight.
        self.document().contentsChanged.connect(self._drop_match)
        self.highlight_line()
        self.gutter = Gutter(self)
        self.highlight = Highlight(self.document())
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.blockCountChanged.connect(self.update_margin)
        self.updateRequest.connect(self.update_gutter)
        self.update_margin()

    def hover_hint(self, position):
        """Read-only MBCS reading of the byte literal under the cursor."""
        cursor = self.cursorForPosition(position)
        return hint_for_position(cursor.block().text(), cursor.positionInBlock())

    def _show_hint(self, event):
        hint = self.hover_hint(event.pos())
        if not hint:
            QToolTip.hideText()
            return False
        QToolTip.showText(event.globalPos(), hint, self)
        return True

    def viewportEvent(self, event):
        # Tooltips are delivered to the scroll area's viewport, not to the
        # editor itself, so both routes are handled.
        if event.type() == QEvent.Type.ToolTip and self._show_hint(event):
            return True
        return super().viewportEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.ToolTip and self._show_hint(event):
            return True
        return super().event(event)

    def _drop_match(self):
        if self._match_block is not None or self._match_range is not None:
            self._match_block = None
            self._match_range = None
            self.highlight_line()

    def set_match_line(self, block=None):
        """Mark the line of a search hit; ``None`` clears the mark.

        The caret line alone (alpha 24) is too faint to spot after the view
        jumps, so a hit gets a warm full-width band *and* its exact text
        swiped in a stronger tone of the same hue.
        """
        self._match_block = block
        self.highlight_line()

    def match_line(self):
        return getattr(self, "_match_block", None)

    def mark_selection(self, start, end):
        """Stronger band for the exact matched characters (or clear it)."""
        self._match_range = None if start is None else (start, end)
        self.highlight_line()

    def highlight_line(self):
        selections = []
        color = self.palette().highlight().color()
        color.setAlpha(24)
        current = QTextEdit.ExtraSelection()
        current.format.setBackground(color)
        current.format.setProperty(
            QTextFormat.Property.FullWidthSelection, True
        )
        current.cursor = self.textCursor()
        current.cursor.clearSelection()
        selections.append(current)

        block = self.match_line()
        document = self.document()
        if block is not None and block.isValid() and block.document() is document:
            band = QColor("#ffe9a8")  # 命中整行：不透明淡黄，压在深色主题文字上也清楚
            line = QTextEdit.ExtraSelection()
            line.format.setBackground(band)
            line.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            line.cursor = QTextCursor(block)
            line.cursor.clearSelection()
            selections.append(line)
            if self._match_range:
                start, end = self._match_range
                start = max(start, block.position())
                end = min(end, block.position() + block.length() - 1)
                if start < end:
                    hit = QTextEdit.ExtraSelection()
                    hit.format.setBackground(
                        QColor("#ffb347")  # 命中文字本身更深一段
                    )
                    hit.cursor = QTextCursor(document)
                    hit.cursor.setPosition(start)
                    hit.cursor.setPosition(
                        end, QTextCursor.MoveMode.KeepAnchor
                    )
                    selections.append(hit)
        self.setExtraSelections(selections)

    def mark_find(self, needle, flags=None):
        """Mark the first match of ``needle`` at/after the caret, if any.

        Used by the find bar so the whole hit line is obvious, not just the
        selected characters.
        """
        self._match_range = None
        if not needle:
            self.set_match_line(None)
            return False
        cursor = self.textCursor()
        found = self.document().find(
            needle, cursor, flags if flags is not None else QTextDocument.FindFlag(0)
        )
        if found.isNull():
            self.set_match_line(None)
            return False
        self._match_range = (found.selectionStart(), found.selectionEnd())
        self.set_match_line(found.block())
        return True

    def indent_selection(self, outdent=False):
        if self.isReadOnly():
            return
        cursor = self.textCursor()
        if not cursor.hasSelection() and not outdent:
            cursor.insertText(" " * (4 - cursor.positionInBlock() % 4))
            return
        first = self.document().findBlock(cursor.selectionStart())
        end = cursor.selectionEnd()
        last = self.document().findBlock(end)
        if cursor.hasSelection() and last.position() == end and last != first:
            last = last.previous()
        edits = []
        block = first
        while block.isValid():
            text = block.text()
            count = (
                1
                if text.startswith("\t")
                else min(4, len(text) - len(text.lstrip(" ")))
            )
            edits.append((block.position(), count))
            if block == last:
                break
            block = block.next()
        cursor.beginEditBlock()
        for position, count in reversed(edits):
            cursor.setPosition(position)
            if outdent:
                cursor.setPosition(position + count, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
            else:
                cursor.insertText("    ")
        cursor.endEditBlock()
        cursor.setPosition(first.position())
        cursor.setPosition(
            last.position() + len(last.text().encode("utf-16-le")) // 2,
            QTextCursor.MoveMode.KeepAnchor,
        )
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if self.isReadOnly():
            return super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            self.indent_selection(
                event.key() == Qt.Key.Key_Backtab
                or bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            )
            return
        if (
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and not event.modifiers()
        ):
            cursor = self.textCursor()
            prefix = (
                cursor.block()
                .text()
                .encode("utf-16-le")[: cursor.positionInBlock() * 2]
                .decode("utf-16-le")
            )
            indent = re.match(r"[ \t]*", prefix).group()
            if (
                prefix.rstrip().endswith(":")
                and not prefix.lstrip().startswith("#")
                and cursor.block().userState() not in (1, 2)
            ):
                indent += "\t" if "\t" in indent else "    "
            cursor.beginEditBlock()
            cursor.insertText("\n" + indent)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            return
        super().keyPressEvent(event)

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
