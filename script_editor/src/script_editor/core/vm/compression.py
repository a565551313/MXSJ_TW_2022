from __future__ import annotations

import zlib

from .marshal_tree import MAX_MARSHAL


def inflate(stored: bytes, *, raw=False) -> bytes:
    stream = zlib.decompressobj(-15 if raw else 15)
    result = stream.decompress(stored, MAX_MARSHAL + 1)
    if len(result) > MAX_MARSHAL or stream.unconsumed_tail:
        raise ValueError("expanded entry exceeds 64MiB limit")
    if not stream.eof or stream.unused_data:
        raise ValueError("truncated or concatenated compressed entry")
    return result
