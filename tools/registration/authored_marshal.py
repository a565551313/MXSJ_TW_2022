"""Strict inverse for VERIFIED authored Py2.5 marshal; no boundary guessing.

Original game entries still use the existing repair-aware transpiler. New code
must first match its freshly obfuscated bytes exactly (including zero padding).
This parser preserves every marshal byte except mapped co_code opcodes. It never
executes code and never repairs tags, headers, encryption boundaries or operands.
"""

from __future__ import annotations

import struct
from collections.abc import Callable

MAGIC = b"\xb3\xf2\x0d\x0a\0\0\0\0"


def restore_authored_pyc(
    decrypted: bytes, expected_obfuscated: bytes,
    translate_code: Callable[[bytes], bytes],
) -> bytes:
    if (not decrypted.startswith(expected_obfuscated)
            or any(decrypted[len(expected_obfuscated):])):
        raise ValueError("authored payload differs from exact obfuscated input")
    data = expected_obfuscated
    pos = 0
    out = bytearray()

    def take(size: int) -> bytes:
        nonlocal pos
        if size < 0 or pos + size > len(data):
            raise ValueError("truncated authored marshal")
        result = data[pos:pos + size]
        pos += size
        return result

    def copy(size: int) -> bytes:
        value = take(size)
        out.extend(value)
        return value

    def walk(depth: int = 0) -> None:
        if depth > 100:
            raise ValueError("authored marshal nesting limit")
        tag = copy(1)
        if tag in (b"0", b"N", b"F", b"T", b"S", b"."):
            return
        if tag in (b"i", b"R"):
            copy(4)
        elif tag in (b"I", b"g"):
            copy(8)
        elif tag == b"y":
            copy(16)
        elif tag == b"l":
            size = struct.unpack("<i", copy(4))[0]
            copy(abs(size) * 2)
        elif tag in (b"s", b"t", b"u"):
            copy(struct.unpack("<I", copy(4))[0])
        elif tag in (b"f", b"x"):
            for _ in range(2 if tag == b"x" else 1):
                copy(copy(1)[0])
        elif tag in (b"(", b"[", b"<", b">"):
            size = struct.unpack("<I", copy(4))[0]
            if size > len(data):
                raise ValueError("invalid authored container size")
            for _ in range(size):
                walk(depth + 1)
        elif tag == b"{":
            while pos < len(data) and data[pos:pos + 1] != b"0":
                walk(depth + 1)
                walk(depth + 1)
            if copy(1) != b"0":
                raise ValueError("invalid authored dictionary end")
        elif tag == b"c":
            copy(16)
            if copy(1) != b"s":
                raise ValueError("authored co_code must be a raw string")
            size = struct.unpack("<I", copy(4))[0]
            code = take(size)
            mapped = translate_code(code)
            if len(mapped) != size:
                raise ValueError("authored code translation changed byte width")
            out.extend(mapped)
            for _ in range(7):  # consts/names/vars/free/cells/filename/name
                walk(depth + 1)
            copy(4)  # firstlineno
            walk(depth + 1)  # lnotab
        else:
            raise ValueError(f"unknown authored marshal tag {tag!r}")

    walk()
    if pos != len(data):
        raise ValueError("trailing authored marshal bytes")
    return MAGIC + bytes(out)
