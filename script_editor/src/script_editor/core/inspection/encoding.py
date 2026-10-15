"""Explicit conversion of selected text only, not whole-source transcoding."""

from __future__ import annotations


def byte_literal(text: str, encoding: str) -> str:
    if encoding not in {"big5", "gbk"}:
        raise ValueError("只支持Big5文案或GBK路径")
    # Every byte is escaped: ASCII quotes, backslashes and newlines are safe too.
    return "'" + "".join(f"\\x{b:02x}" for b in text.encode(encoding)) + "'"
