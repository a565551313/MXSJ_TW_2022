"""Bounded legacy marshal syntax tree. Never constructs or executes code objects.

Preserve raw scalar bytes, interned-string order and all metadata. Native27 has
an extra uint32 before co_code. Transformable code/lnotab must be raw strings:
interned/reference representations are unknown rather than guessed/repaired.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAX_MARSHAL = 64 * 1024 * 1024


@dataclass(frozen=True)
class Atom:
    tag: bytes
    raw: bytes
    value: bytes | None = None


@dataclass(frozen=True)
class Group:
    tag: bytes
    items: tuple


@dataclass(frozen=True)
class Code:
    header: bytes
    code: bytes
    fields: tuple
    firstline: bytes
    lnotab: bytes
    extra: int = 0
    tag: bytes = b"c"


class Reader:
    def __init__(self, data: bytes, native27=False):
        if len(data) > MAX_MARSHAL:
            raise ValueError("marshal exceeds 64MiB safety limit")
        self.data, self.pos, self.native27 = data, 0, native27
        self.intern_values = []
        self.interns = 0
        self.nodes = 0

    def take(self, n: int) -> bytes:
        if n < 0 or n > len(self.data) - self.pos:
            raise ValueError("truncated marshal")
        result = self.data[self.pos : self.pos + n]
        self.pos += n
        return result

    def uint(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def raw_string(self) -> bytes:
        if self.take(1) != b"s":
            raise ValueError("transformed code/lnotab must be raw marshal strings")
        return self.take(self.uint())

    def walk(self, depth=0):
        self.nodes += 1
        if depth > 100 or self.nodes > 1_000_000:
            raise ValueError("marshal nesting/node limit")
        start = self.pos
        tag = self.take(1)
        resolved = None
        if tag in (b"N", b"F", b"T", b"S", b"."):
            pass
        elif tag in (b"i", b"I", b"g", b"y"):
            self.take({b"i": 4, b"I": 8, b"g": 8, b"y": 16}[tag])
        elif tag == b"R":
            index = self.uint()
            if index >= self.interns:
                raise ValueError("invalid marshal intern reference")
            resolved = self.intern_values[index]
        elif tag == b"l":
            count = abs(struct.unpack("<i", self.take(4))[0])
            digits = self.take(count * 2)
            if any(value[0] >= 32768 for value in struct.iter_unpack("<H", digits)):
                raise ValueError("invalid marshal long digit")
        elif tag in (b"s", b"t", b"u"):
            value = self.take(self.uint())
            resolved = value
            if tag == b"t":
                self.interns += 1
                self.intern_values.append(value)
            if tag == b"u":
                value.decode("utf-8")
        elif tag in (b"f", b"x"):
            for _ in range(2 if tag == b"x" else 1):
                self.take(self.take(1)[0])
        elif tag in (b"(", b"[", b"<", b">"):
            count = self.uint()
            if count > len(self.data) - self.pos:
                raise ValueError("impossible marshal container count")
            return Group(tag, tuple(self.walk(depth + 1) for _ in range(count)))
        elif tag == b"{":
            items = []
            while self.data[self.pos : self.pos + 1] != b"0":
                items.extend((self.walk(depth + 1), self.walk(depth + 1)))
            self.take(1)
            return Group(tag, tuple(items))
        elif tag == b"c":
            header = self.take(16)
            if any(n < 0 for n in struct.unpack("<iiii", header)):
                raise ValueError("negative code header field")
            extra = self.uint() if self.native27 else 0
            code = self.raw_string()
            fields = tuple(self.walk(depth + 1) for _ in range(7))
            if any(n.tag != b"(" for n in fields[:5]):
                raise ValueError("code tuple metadata invalid")
            if any(n.tag not in (b"s", b"t", b"R") for n in fields[5:]):
                raise ValueError("code filename/name invalid")
            firstline = self.take(4)
            lnotab = self.raw_string()
            if len(lnotab) % 2:
                raise ValueError("odd co_lnotab length")
            return Code(header, code, fields, firstline, lnotab, extra)
        else:
            raise ValueError(f"unknown marshal tag {tag!r} at {start}")
        return Atom(tag, self.data[start : self.pos], resolved)


def parse(data: bytes, *, native27=False, zero_padding=False) -> Code:
    reader = Reader(data, native27)
    root = reader.walk()
    if not isinstance(root, Code):
        raise ValueError("module marshal root must be a code object")
    tail = data[reader.pos :]
    if tail and (not zero_padding or any(tail)):
        raise ValueError("trailing/nonzero marshal data")
    return root


def emit(root: Code, transform, *, native27=False) -> bytes:
    """Encode with a caller's code/line transform; every other byte is preserved."""
    out = []

    def string(data):
        return b"s" + struct.pack("<I", len(data)) + data

    def walk(node):
        if isinstance(node, Atom):
            out.append(node.raw)
        elif isinstance(node, Group):
            out.append(node.tag)
            if node.tag != b"{":
                out.append(struct.pack("<I", len(node.items)))
            for child in node.items:
                walk(child)
            if node.tag == b"{":
                out.append(b"0")
        else:
            code, lines, extra = transform(node.code, node.lnotab, node.extra)
            out.extend((b"c", node.header))
            if native27:
                out.append(struct.pack("<I", extra))
            out.append(string(code))
            for field in node.fields:
                walk(field)
            out.extend((node.firstline, string(lines)))

    walk(root)
    return b"".join(out)
