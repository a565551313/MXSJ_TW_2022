r"""Display-only reading of legacy MBCS byte literals from recovered source.

Decompilers render Python 2 ``str`` constants as latin-1 codepoints, so a
Big5 message such as ``只能使用`` comes back as ``'\xa5u\xaf\xe0...'``.  These
constants are *not* Unicode text: at run time the client compares the raw
MBCS bytes, so rewriting the literal would change behaviour.  This module only
builds a readable rendering for display, previews and reports.  Nothing here
returns source that may be saved, compiled or written back into a package.

A rendering is offered only when the *whole* literal body is an exact byte
string (Python 2 ``str`` semantics) and decodes strictly with one candidate
codec and re-encodes to the identical bytes.  Otherwise the escape text is
kept unchanged and the caller must show it as written.

The same bytes are frequently valid in more than one codec (a Big5 message
read as GBK, or a GBK resource path read as Big5), and no byte stream can
prove which was intended.  Candidates are therefore returned in preference
order instead of being silently collapsed to one guess.
"""

from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass

#: Taiwan client text first, GBK-authored resource paths second.  Order is a
#: preference for the primary reading, never a claim about the bytes.
CODECS = ("cp950", "gbk")

#: One maximal ``\xNN`` run.  Only explicit byte escapes are candidates;
#: ``\n``, ``\\`` or ``\u4e2d`` are never rewritten.
ESCAPE_RUN = re.compile(r"(?:\\x[0-9a-fA-F]{2})+")

#: Bounds so a 4 MB module cannot turn a preview into a UI stall.
MAX_RECORDS = 4096

_HEX = frozenset("0123456789abcdefABCDEF")
_OCTAL = frozenset("01234567")
_SIMPLE_ESCAPES = {
    "n": 0x0A,
    "t": 0x09,
    "r": 0x0D,
    "v": 0x0B,
    "f": 0x0C,
    "a": 0x07,
    "b": 0x08,
    "0": 0x00,
    "\\": 0x5C,
    "'": 0x27,
    '"': 0x22,
}

#: Where a literal may start: a short prefix, then one of the four quotes.
#: The body is deliberately **not** part of this pattern (see :func:`_literals`).
_OPEN = re.compile(
    r"""(?P<prefix>[uUbB]{0,2}[rR]?|[rR][uUbB]{0,2})"""
    r"""(?P<quote>\"\"\"|'''|\"|')"""
)


def _literals(line: str):
    """Yield ``(start, end, prefix, quote)`` for closed literals on one line.

    A regex body cannot do this without either being wrong or being slow:

    * lazy (``[\\s\\S]*?``) — stops at an escaped quote, so ``'\\xa5u\\''`` is cut
      short and the hover hint disagrees with the highlighter;
    * greedy with ``\\\\[\\s\\S]`` pairs — re-scans to the end of the line for every
      quote it fails to close; measured **0.8 s for a 16 KB line** of ``aaa\\'``
      repeats (quadratic), which would freeze the editor on hover.

    This scanner is deterministic and linear: it walks the body once, lets a
    backslash take the next character with it, and remembers which quotes
    already failed to close — everything at or after that position fails for
    the same quote again.
    """
    failed_at: dict[str, int] = {}
    for match in _OPEN.finditer(line):
        quote = match.group("quote")
        start = match.start()
        floor = failed_at.get(quote)
        if floor is not None and start >= floor:
            continue
        index, size = match.end(), len(line)
        end = None
        while index < size:
            char = line[index]
            if char == "\\":
                index += 2  # The escape owns the next character, quote or not.
                continue
            if line.startswith(quote, index):
                end = index + len(quote)
                break
            index += 1
        if end is None:
            failed_at[quote] = start
            continue
        yield start, end, match.group("prefix"), quote


@dataclass(frozen=True)
class Reading:
    """One codec's reading of a legacy byte literal (display text only)."""

    codec: str
    text: str


@dataclass(frozen=True)
class LiteralPreview:
    """A string literal whose bytes can be read as legacy text."""

    line: int
    column: int
    raw: str
    readings: tuple[Reading, ...]

    @property
    def text(self):
        return self.readings[0].text

    @property
    def codec(self):
        return self.readings[0].codec


def literal_bytes(body: str):
    """Return the exact Python 2 ``str`` bytes of a literal body, or ``None``.

    ``None`` means "no claim": already-Unicode text (raw non-ASCII), octal or
    ``\\u`` escapes and malformed escapes are all refused rather than guessed.
    """
    if not body:
        return None
    out = bytearray()
    index = 0
    size = len(body)
    while index < size:
        char = body[index]
        if char != "\\":
            code = ord(char)
            if not 0x20 <= code < 0x7F:
                return None
            out.append(code)
            index += 1
            continue
        following = body[index + 1 : index + 2]
        if following == "x":
            pair = body[index + 2 : index + 4]
            if len(pair) != 2 or not set(pair) <= _HEX:
                return None
            out.append(int(pair, 16))
            index += 4
            continue
        if following in _SIMPLE_ESCAPES and following:
            if following == "0" and body[index + 2 : index + 3] in _OCTAL:
                return None  # "\0" + octal digit is one octal escape, not NUL.
            out.append(_SIMPLE_ESCAPES[following])
            index += 2
            continue
        if following == "\n":
            index += 2  # Explicit line continuation contributes no byte.
            continue
        return None
    return bytes(out)


def decode_bytes(data: bytes, codecs=CODECS):
    """Every exact reading of ``data``, primary first, deduplicated by text."""
    readings = []
    seen = set()
    for codec in codecs:
        try:
            text = data.decode(codec)
            exact = text.encode(codec) == data
        except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
            continue
        if not exact or not any(ord(char) > 0x7F for char in text):
            continue
        if text in seen:
            continue
        seen.add(text)
        readings.append(Reading(codec, text))
    return tuple(readings)


def _render(prefix: str, quote: str, text: str):
    """Re-quote decoded text so the preview stays visibly a literal."""
    escaped = []
    for char in text:
        code = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char in quote:
            escaped.append("\\" + char)
        elif code < 0x20 or code == 0x7F:
            escaped.append(f"\\x{code:02x}")
        else:
            escaped.append(char)
    return prefix + quote + "".join(escaped) + quote


def split_literal(literal: str):
    """Return ``(prefix, quote, body)`` for a single string literal."""
    for start, end, prefix, quote in _literals(literal):
        if start != 0 or end != len(literal):
            return None
        inside = len(quote)
        return prefix, quote, literal[len(prefix) + inside : end - inside]
    return None


def readings(literal: str, codecs=CODECS):
    """All display readings of one literal, primary first (may be empty)."""
    parts = split_literal(literal)
    if parts is None:
        return ()
    prefix, quote, body = parts
    if {"r", "u"} & set(prefix.lower()):
        # Raw strings hold backslashes as data; ``u'...'`` holds code points,
        # not the MBCS bytes the client compares.
        return ()
    if "\\x" not in body:
        return ()
    data = literal_bytes(body)
    if not data:
        return ()
    return tuple(
        Reading(reading.codec, _render(prefix, quote, reading.text))
        for reading in decode_bytes(data, codecs)
    )


def readable_literal(literal: str, codecs=CODECS):
    """The primary reading of one literal, or ``None`` when none is exact."""
    found = readings(literal, codecs)
    return found[0] if found else None


@dataclass(frozen=True)
class ScanResult:
    """Preview records plus whether scanning reached the end of the source.

    Recovered files are Python 2, and Python 3's tokenizer is explicitly not
    meant for invalid input: ``10L``, ``0777`` or an unclosed bracket can make
    it stop early. Hints after that point would then be missing without anyone
    noticing, so the caller is told instead of being handed a short list.
    """

    records: tuple
    complete: bool = True
    reason: str = ""

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        return iter(self.records)


def scan(source: str, codecs=CODECS, limit: int = MAX_RECORDS) -> ScanResult:
    """Collect readable renderings for one source text, in source order."""
    records = []
    stopped = ""
    held = max(1, int(limit))
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type != tokenize.STRING or "\\x" not in token.string:
                continue
            found = readings(token.string, codecs)
            if not found:
                continue
            records.append(
                LiteralPreview(token.start[0], token.start[1], token.string, found)
            )
            if len(records) >= held:
                return ScanResult(
                    tuple(records),
                    False,
                    f"已达 {held} 条预览上限，其余未收集",
                )
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        where = exc.args[0] if exc.args else type(exc).__name__
        stopped = f"分词在「{where}」处停止，其后的字面量未收集"
    return ScanResult(tuple(records), not stopped, stopped)


def previews(source: str, codecs=CODECS, limit: int = MAX_RECORDS):
    """Readable renderings only; use :func:`scan` when completeness matters."""
    return scan(source, codecs, limit).records


def line_previews(line: str, codecs=CODECS):
    """Readable renderings for the string literals of one physical line.

    Used for hover hints, where tokenizing the whole document would be wasted
    work.  Multi-line triple-quoted literals are not served here.
    """
    records = []
    for start, end, _prefix, _quote in _literals(line):
        literal = line[start:end]
        if "\\x" not in literal:
            continue
        found = readings(literal, codecs)
        if not found:
            continue
        records.append(LiteralPreview(0, start, literal, found))
    return tuple(records)


def clamp(text: str, limit: int = 240) -> str:
    """One-line, bounded rendering so a hint never floods the screen."""
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def summary(records) -> dict:
    """Counts for a status line or dialog header."""
    return {
        "literals": len(records),
        "codecs": sorted({record.codec for record in records}),
        "lines": len({record.line for record in records}),
    }


#: Shown above every hint and report: the reader must know this is not source.
DISPLAY_ONLY = "只读预览 · 源码字节未改 · 不可用于替换或编译"

RAW_LIMIT = 400
REPORT_LIMIT = 400_000


def format_hint(record) -> str:
    """Hover text for one literal: every exact reading, primary first."""
    lines = [DISPLAY_ONLY]
    for reading in record.readings:
        lines.append(f"{reading.codec}: {clamp(reading.text, 200)}")
    return "\n".join(lines)


def hint_for_position(line: str, column: int) -> str:
    """Hover text for the literal at ``column`` on one physical line."""
    for record in line_previews(line):
        end = record.column + len(record.raw)
        if record.column <= column < end:
            return format_hint(record)
    return ""


def report_text(records, title: str = "", limit: int = REPORT_LIMIT):
    """Build the read-only report body and say whether it was truncated."""
    counts = summary(records)
    lines = [
        "# 字节字面量可读对照 · " + DISPLAY_ONLY,
        f"# 文件：{title}" if title else "# 文件：（未命名）",
        f"# 共 {counts['literals']} 处字面量，分布在 {counts['lines']} 行；"
        f"读法：{'/'.join(counts['codecs']) or '无'}",
        "# 这些字面量是 MBCS 字节串（Python2 str），游戏按原始字节比较。",
        "# 同一串字节可能同时是合法 Big5 与合法 GBK：多种读法全部列出，不做取舍。",
        "# 本文件不再被任何流程读取：不写回源码、不参与编译、不打包。",
        "-" * 60,
    ]
    body = []
    used = sum(len(line) + 1 for line in lines)
    truncated = False
    for record in records:
        block = [f"第 {record.line} 行", f"  原文: {clamp(record.raw, RAW_LIMIT)}"]
        for reading in record.readings:
            block.append(f"  {reading.codec:<5}: {clamp(reading.text, RAW_LIMIT)}")
        block.append("")
        size = sum(len(line) + 1 for line in block)
        if used + size > limit:
            truncated = True
            break
        used += size
        body.extend(block)
    if truncated:
        body.append(f"（结果超过 {limit} 字符上限，其余字面量未列出）")
    return "\n".join(lines + body), truncated
