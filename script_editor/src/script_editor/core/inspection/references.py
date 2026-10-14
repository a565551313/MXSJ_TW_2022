"""Static hints for authored Python2 text; not API/layout existence proofs."""

from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass


@dataclass(frozen=True)
class Hint:
    line: int
    kind: str
    text: str


def _literal(token):
    match = re.fullmatch(r"[uUrR]?(['\"])(.*)\1", token)
    if not match:
        return None
    body = match.group(2)
    if token[:1].lower() == "r":
        return body
    # Decode only explicit bytes/quotes/backslashes. No eval or guessed codec.
    parts = re.findall(r"\\x[0-9a-fA-F]{2}|\\.|[^\\]", body)
    result = bytearray()
    for part in parts:
        if part.startswith("\\x") and len(part) == 4:
            result.append(int(part[2:], 16))
        elif part in ("\\\\", "\\'", '\\"'):
            result.extend(part[1:].encode("ascii"))
        elif len(part) == 1 and ord(part) < 128:
            result.append(ord(part))
        else:
            return body  # Non-ASCII/dynamic hint, not a claim about engine bytes.
    return "".join(chr(b) if 32 <= b < 127 else f"\\x{b:02x}" for b in result)


def inspect_references(text: str) -> tuple[Hint, ...]:
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type not in (
                tokenize.COMMENT,
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
            ):
                tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        pass  # Partial hints are NOT syntax validation. The exact compiler is.
    result = []
    for i, token in enumerate(tokens):
        if token.type == tokenize.STRING:
            value = _literal(token.string)
            if value and ".dlg" in value.lower():
                result.append(Hint(token.start[0], "布局线索（未挂载验证）", value))
            if (
                i >= 2
                and tokens[i - 1].string == "("
                and tokens[i - 2].string in {"GetObject", "GetChild"}
            ):
                result.append(
                    Hint(
                        token.start[0],
                        "控件名线索（未验证）",
                        value or "动态/未知字面量",
                    )
                )
        if (
            token.type == tokenize.NAME
            and token.string == "FONT_EDIT"
            and i >= 1
            and tokens[i - 1].string == "."
        ):
            result.append(
                Hint(
                    token.start[0],
                    "原生API警告",
                    "FONT_EDIT在本客户端曾确认缺失，请核对原生接口",
                )
            )
    return tuple(result)
