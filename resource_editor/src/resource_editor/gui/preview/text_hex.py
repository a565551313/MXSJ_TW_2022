"""文本与十六进制只读预览。"""
from __future__ import annotations

import json

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QPlainTextEdit, QWidget

_HEX_LIMIT = 192 * 1024


class TextPreview(QPlainTextEdit):
    """JSON/文本条目预览（JSON 自动格式化）。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))

    def set_content(self, content: bytes) -> None:
        text = None
        stripped = content.strip()
        if stripped[:1] in (b"{", b"["):
            try:
                obj = json.loads(stripped.decode("utf-8"))
                text = json.dumps(obj, ensure_ascii=False, indent=2)
            except (ValueError, UnicodeDecodeError):
                text = None
        if text is None:
            text = content.decode("utf-8", errors="replace")
        self.setPlainText(text)


class HexPreview(QPlainTextEdit):
    """二进制条目十六进制预览（超长时截断并标注）。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))

    def set_content(self, content: bytes, note: str = "") -> None:
        shown = content[:_HEX_LIMIT]
        lines = []
        if note:
            lines.append(f"# {note}")
        for off in range(0, len(shown), 16):
            chunk = shown[off:off + 16]
            hexs = " ".join(f"{b:02x}" for b in chunk)
            asc = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
            lines.append(f"{off:08x}  {hexs:<47}  {asc}")
        if len(content) > _HEX_LIMIT:
            lines.append(f"# …已截断，总长 {len(content)} 字节")
        self.setPlainText("\n".join(lines))
