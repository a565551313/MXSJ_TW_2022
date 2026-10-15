"""Strict width-preserving opcode conversion. No heuristic LOAD/STORE repairs."""

from __future__ import annotations

from ..marshal_tree import emit, parse
from ..tables import PY25_MAP

MAGIC = bytes.fromhex("b3f20d0a")
FORWARD = {standard: native for native, standard in PY25_MAP.items()}


def map_code(code: bytes, *, inverse=False) -> bytes:
    mapping = PY25_MAP if inverse else FORWARD
    threshold = 95 if inverse else 90
    result = bytearray(code)
    pos = 0
    while pos < len(code):
        opcode = code[pos]
        if opcode not in mapping:
            raise ValueError(f"unmapped VM25 opcode {opcode} at {pos}")
        width = 3 if opcode >= threshold else 1
        if pos + width > len(code):
            raise ValueError("truncated VM25 instruction")
        result[pos] = mapping[opcode]
        if (mapping[opcode] >= (90 if inverse else 95)) != (width == 3):
            raise ValueError("VM25 opcode width mismatch")
        pos += width
    return bytes(result)


def encode(pyc: bytes) -> bytes:
    if pyc[:4] != MAGIC or len(pyc) < 9:
        raise ValueError("VM25 requires standard CPython2.5 pyc")
    root = parse(pyc[8:])
    return emit(root, lambda code, lines, _: (map_code(code), lines, 0))


def decode(native: bytes, header: bytes = MAGIC + bytes(4), *, padding=False) -> bytes:
    if len(header) != 8 or header[:4] != MAGIC:
        raise ValueError("bad VM25 header")
    root = parse(native, zero_padding=padding)
    return header + emit(
        root, lambda code, lines, _: (map_code(code, inverse=True), lines, 0)
    )
