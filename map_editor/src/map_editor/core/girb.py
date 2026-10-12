"""Decompress the ``GIRB`` block payload.

``GIRB`` is the per-sector collision grid.  ``mx.exe`` handles it at
``0x4b8cd8``: read the block body, ``new[0x960]`` (2400 bytes), store the pointer
at ``this+0xA4``, then call ``0x60ea90`` to inflate the body into it.

``0x60ea90`` is an LZ77 with four match classes and LZ4-style trailing literals.
Measured facts this implementation reproduces:

* A 22-byte body — the value found in every sector of maps with no obstacles —
  inflates to **exactly 2400 bytes of ``0x88``**, i.e. 1200 u16 cells all equal
  to ``0x8888``.  That is the "no data" fill value.
* 2400 bytes = 1200 u16 = a 40x30 grid, which is a 320x240 sector at **8x8 pixels
  per cell**.  Cross-check on map 1034: 234 sectors x 1200 = 280,800 cells, and
  the sector-padded canvas is 18*320 x 13*240 = 5760 x 3120 -> 720 x 390 =
  280,800 cells at 8 px each.  Exact match.
* The runtime walkability test at ``0x4bbb00`` indexes a **u16** array
  (``cmp %di,(%eax,%ecx,2)``), consistent with this layout.

**Status (measured, not assumed).**  Uniform sectors — every sector of an
interior map, and all 195 of map 2504 — inflate correctly: 244/244 and 195/195.
Sectors that actually carry obstacles still fail: 73/238 on 1034 and 38/196 on
1035, always as an out-of-range match offset part-way through, which means the
token stream desyncs rather than the geometry being wrong.  Two real bugs were
found and fixed while measuring this (the ``>= 0x40`` length is ``(t>>5)+1``
because 0x60eb85 pre-decrements, and a token ``< 0x10`` arriving after trailing
literals takes the 0x60ec73 class, not the 0x60eb29 one).  Whatever decodes is
always exactly 2400 bytes, so the geometry below is solid; the remaining work is
the token stream, not the layout.

Byte-level semantics, transcribed from the disassembly:

===========================  ==============================================
token ``> 0x11``             literal run of ``token - 0x11`` bytes
token ``0x10..0x1f``         match; offset ``0x4000 + (u16>>2) + ((t&8)<<11)``;
                             offset 0 means end of stream
token ``0x20..0x3f``         match; offset ``1 + (u16>>2)``
token ``>= 0x40``            match; offset ``1 + ((t>>2)&7) + (byte<<3)``;
                             length ``(t>>5) + 1`` (0x60eb85 pre-decrements)
token ``< 0x10`` after a literal run (0x60eb29)
                             3-byte match; offset ``0x801 + (byte<<2) + (t>>2)``
token ``< 0x10`` after trailing literals (0x60ec73)
                             2-byte match; offset ``1 + (byte<<2) + (t>>2)``
length                       ``accumulated + 2`` for the 0x60ec2d classes
trailing literals            ``(src[i-2]) & 3`` bytes after every match
===========================  ==============================================
"""
from __future__ import annotations

GRID_BYTES = 0x960            # 2400, the fixed allocation at mx.exe 0x4b8d1d
GRID_CELLS = GRID_BYTES // 2  # 1200 u16
GRID_COLS, GRID_ROWS = 40, 30
CELL_PX = 8                   # 320/40 == 240/30
EMPTY_FILL = 0x8888           # every cell of an obstacle-free sector


class GirbError(ValueError):
    """Raised when a GIRB body cannot be inflated."""


def decompress(src: bytes, limit: int = GRID_BYTES) -> bytes:
    """Inflate one GIRB body.  Returns the raw bytes (``limit`` long in practice)."""
    payload = len(src)
    buf = bytearray(src) + b"\x00" * (payload * 3 + 16)   # client used new[length*4]
    out = bytearray()
    i = 0

    def u16(k: int) -> int:
        # Reading past the buffer used to surface as a bare IndexError, which
        # escaped collision_cells() and aborted the whole map.  It means an
        # earlier token was mis-parsed, so report it as a decode failure.
        if k < 0 or k + 1 >= len(buf):
            raise GirbError(f"token reads past the {len(buf)}-byte buffer at {k}")
        return buf[k] | (buf[k + 1] << 8)

    def token() -> int:
        """Next token byte, bounds-checked against the real payload.

        ``buf`` is deliberately padded well past the payload, so a desynced
        stream can walk off the end of the real data and keep going until it
        hits the end of the padding -- which surfaced to callers as a bare
        ``IndexError`` and aborted the entire map.  Running past the payload
        is a decode failure; report it as one.
        """
        nonlocal i
        if i >= payload:
            raise GirbError(f"token stream ran past the {payload}-byte payload at {i}")
        v = buf[i]
        i += 1
        return v

    def copy_match(offset: int, length: int) -> None:
        if offset <= 0 or offset > len(out):
            raise GirbError(f"match offset {offset} out of range at out={len(out)}")
        start = len(out) - offset
        for k in range(length):               # byte-wise: matches may overlap
            out.append(out[start + k])

    def literal(count: int) -> None:
        nonlocal i
        if i + count > payload:
            raise GirbError(f"literal run of {count} runs past the {payload}-byte payload")
        out.extend(buf[i:i + count])
        i += count

    def run_length(base: int, addend: int) -> int:
        """The 0xff-chain extension used by the long-match classes.

        A well-formed stream never runs past its own payload, so doing so means
        an earlier token was mis-parsed; report it instead of reading padding.
        """
        nonlocal i
        total = base
        if i < payload and buf[i] == 0:
            while i < payload and buf[i] == 0:
                i += 1
                total += 0xFF
        if i >= payload:
            raise GirbError(f"length extension ran past the {payload}-byte payload")
        total += addend + buf[i]
        i += 1
        return total

    def match_after_trail(t: int) -> bool:
        """Token read right after trailing literals (0x60ecad -> 0x60eb67).

        This jump is unconditional, so t < 0x10 falls through 0x60eba8 and
        0x60ebda to 0x60ec73 — a *different* short-match class than 0x60eb29:
        offset ``1 + (nb<<2) + (t>>2)`` and length 2, versus 0x801-based and 3.
        """
        nonlocal i
        if t >= 0x10:
            return match_hi(t)
        nb = buf[i]
        i += 1
        copy_match(1 + (nb << 2) + (t >> 2), 2)
        return True

    def match_hi(t: int) -> bool:
        """Handle token >= 0x10.  Returns False at end of stream."""
        nonlocal i
        if t >= 0x40:
            # 0x60eb85 pre-decrements before the 2-byte head copy, so this class
            # is one byte shorter than the 0x60ec2d classes.
            length = (t >> 5) + 1
            offset = 1 + ((t >> 2) & 7) + (buf[i] << 3)
            i += 1
        elif t >= 0x20:
            length = t & 0x1F
            length = run_length(length, 0x1F) if length == 0 else length
            off16 = u16(i)
            i += 2
            offset = 1 + (off16 >> 2)
            length += 2
        else:                                   # 0x10..0x1f
            length = t & 7
            length = run_length(length, 7) if length == 0 else length
            off16 = u16(i)
            i += 2
            total_off = ((t & 8) << 11) + (off16 >> 2)
            if total_off == 0:
                return False                    # end-of-stream marker
            offset = 0x4000 + total_off
            length += 2
        copy_match(offset, length)
        return True

    def literal_run_token() -> bool:
        """Token read at 0x60eabc: t < 0x10 means a LITERAL run here."""
        nonlocal i
        t = buf[i]
        i += 1
        if t >= 0x10:
            return match_hi(t)
        if t == 0:
            total = 0
            if i < payload and buf[i] == 0:
                while i < payload and buf[i] == 0:
                    i += 1
                    total += 0xFF
            if i >= payload:
                raise GirbError(
                    f"zero-run extension ran past the {payload}-byte payload")
            total += 0x0F + buf[i]
            i += 1
        else:
            total = t
        out.extend(buf[i:i + 4])              # 0x60eae5: one u32 first
        i += 4
        total -= 1
        while total >= 4:
            out.extend(buf[i:i + 4])
            i += 4
            total -= 4
        if total:
            literal(total)
        return True

    def short_match_token() -> bool:
        """Token read at 0x60eb29: t < 0x10 means a 3-BYTE MATCH here."""
        t = token()
        if t < 0x10:
            nb = token()
            copy_match(0x801 + (nb << 2) + (t >> 2), 3)
            return True
        return match_hi(t)

    # ---- leading literal run (mx.exe 0x60ea9b) ----
    t = buf[i]
    if t > 0x11:
        i += 1
        count = t - 0x11
        literal(count)
        if count < 4:
            # 0x60eca0 already consumed the short run; next token is a match
            t = buf[i]
            i += 1
            if not match_hi(t):
                return bytes(out[:limit])
        else:
            short_match_token()
    else:
        if not literal_run_token():
            return bytes(out[:limit])

    # ---- alternating: match -> trailing literals -> literal run -> match ... ----
    after_literal_run = False
    while True:
        trail = buf[i - 2] & 3                  # 0x60ec90
        while trail:
            literal(trail)
            t = token()
            if not match_after_trail(t):
                return bytes(out[:limit])
            trail = buf[i - 2] & 3
        if after_literal_run:
            if not short_match_token():         # 0x60eb29
                break
            after_literal_run = False
        else:
            if not literal_run_token():         # 0x60ec97 -> 0x60eabc
                break
            after_literal_run = True
    return bytes(out[:limit])


def cells(src: bytes) -> list[int]:
    """Inflate and reinterpret as 1200 little-endian u16 cells."""
    raw = decompress(src)
    if len(raw) < GRID_BYTES:
        raise GirbError(f"expected {GRID_BYTES} bytes, got {len(raw)}")
    return [raw[k] | (raw[k + 1] << 8) for k in range(0, GRID_BYTES, 2)]


__all__ = ["CELL_PX", "EMPTY_FILL", "GRID_BYTES", "GRID_CELLS", "GRID_COLS",
           "GRID_ROWS", "GirbError", "cells", "decompress"]
