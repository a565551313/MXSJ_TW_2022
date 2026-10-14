from __future__ import annotations

from ..marshal_tree import emit, parse
from . import forward, inverse

MAGIC = bytes.fromhex("03f30d0a")


def encode(pyc: bytes) -> bytes:
    if pyc[:4] != MAGIC or len(pyc) < 9:
        raise ValueError("VM27 requires standard CPython2.7 pyc")

    def convert(code, lnotab, _):
        split, count, boundaries = forward.split(code)
        return split, forward.lines(lnotab, boundaries), count

    return pyc[:8] + emit(parse(pyc[8:]), convert, native27=True)


def decode(native: bytes) -> bytes:
    if native[:4] != MAGIC or len(native) < 9:
        raise ValueError("bad native VM27 header")

    def convert(code, lnotab, extra):
        joined, offsets = inverse.join(code, extra)
        return joined, inverse.lines(lnotab, offsets), 0

    return native[:8] + emit(parse(native[8:], native27=True), convert)
