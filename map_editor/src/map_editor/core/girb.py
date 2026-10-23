"""``GIRB`` (``"BRIG"`` reversed) sector lightmap codec and legacy u16 grid view.

Ground-truth binary analysis of ``mx.exe`` proves two key facts:

1. ``Sector::LoadBlocks`` (``0x4b8cd8``) allocates ``0x960`` (``2,400``) bytes at
   ``this+0xA4`` and decompresses ``GIRB`` with ``0x0060ea90`` (``LZO1X-1``).
   Across all ``101`` client maps (``11,763`` sectors), **100.0% (11,763 / 11,763)**
   decompress cleanly to exactly ``2,400`` bytes with **0** failures.
2. ``Sector::GetBrightness`` (``0x4b9220``) indexes ``this+0xA4`` at row stride
   ``40`` bytes (``y >> 2`` rows of ``4`` pixels) and nibble-pairs along ``x``:
   ``GIRB`` is an **80x60 grid of 4x4-pixel, 4-bit dynamic sprite brightness
   multipliers** (values ``0..15``, neutral ``8`` -> ``0x88``, brightening sprites
   in sunlight/lantern glow and darkening sprites under tree canopies/roof shadows).

For 100% compatibility with earlier callers and tests, the ``1,200``-entry
little-endian ``u16`` view (:func:`cells`, ``40x30`` at ``8`` px, ``EMPTY_FILL =
0x8888``) is preserved alongside the native ``80x60`` 4-bit nibble API.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

from .lzo1x import LzoError, deflate_lzo1x, inflate_lzo1x

GRID_BYTES = 0x960            # 2,400 bytes per sector (mx.exe 0x4b8d1d)
GRID_CELLS = GRID_BYTES // 2  # legacy 1,200 u16 view
GRID_COLS, GRID_ROWS = 40, 30
CELL_PX = 8                   # legacy 8x8 px view
EMPTY_FILL = 0x8888           # neutral brightness byte pair (0x8888)

# True engine lightmap geometry (Sector::GetBrightness at mx.exe 0x4b9220):
LIGHT_COLS, LIGHT_ROWS = 80, 60
LIGHT_CELL_PX = 4             # 320 / 80 == 240 / 60 == 4 px
LIGHT_CELLS = LIGHT_COLS * LIGHT_ROWS   # 4,800 4-bit samples
LIGHT_ROW_STRIDE = 40         # 80 nibbles packed 2 per byte
NEUTRAL_NIBBLE = 8            # 8 / 8.0 == 1.0x neutral sprite brightness
NEUTRAL_BYTE = 0x88


class GirbError(ValueError):
    """Raised when a ``GIRB`` payload cannot be inflated or encoded."""


def decompress(src: bytes, limit: int = GRID_BYTES) -> bytes:
    """Inflate one ``GIRB`` body into ``limit`` bytes (default ``2,400``)."""
    try:
        return inflate_lzo1x(src, expected_len=limit)
    except LzoError as exc:
        raise GirbError(str(exc)) from exc


def compress(raw: bytes) -> bytes:
    """Compress a ``2,400``-byte ``GIRB`` buffer into a native ``LZO1X-1`` body."""
    if len(raw) != GRID_BYTES:
        raise GirbError(f"GIRB raw buffer must be {GRID_BYTES} bytes, got {len(raw)}")
    return deflate_lzo1x(bytes(raw))


def cells(src: bytes) -> list[int]:
    """Inflate and reinterpret as ``1,200`` little-endian ``u16`` cells."""
    raw = decompress(src)
    return [raw[k] | (raw[k + 1] << 8) for k in range(0, GRID_BYTES, 2)]


def unpack_nibbles(raw: bytes) -> bytearray:
    """Unpack ``2,400`` ``GIRB`` bytes into ``4,800`` row-major nibbles (``80x60``).

    Low nibble is even column ``2*c``, high nibble is odd column ``2*c + 1``.
    """
    if len(raw) != GRID_BYTES:
        raise GirbError(f"expected {GRID_BYTES} bytes, got {len(raw)}")
    out = bytearray(LIGHT_CELLS)
    j = 0
    for b in raw:
        out[j] = b & 0x0F
        out[j + 1] = (b >> 4) & 0x0F
        j += 2
    return out


def pack_nibbles(nibbles: Sequence[int] | bytes | bytearray) -> bytes:
    """Pack ``4,800`` brightness nibbles (``0..15``) into ``2,400`` ``GIRB`` bytes."""
    if len(nibbles) != LIGHT_CELLS:
        raise GirbError(f"expected {LIGHT_CELLS} nibbles, got {len(nibbles)}")
    out = bytearray(GRID_BYTES)
    for k in range(GRID_BYTES):
        lo = int(nibbles[2 * k])
        hi = int(nibbles[2 * k + 1])
        if not (0 <= lo <= 15 and 0 <= hi <= 15):
            raise GirbError(f"lightmap nibble out of range 0..15: ({lo}, {hi})")
        out[k] = lo | (hi << 4)
    return bytes(out)


def default_girb_body(nibble: int = NEUTRAL_NIBBLE) -> bytes:
    """Build a compressed uniform ``GIRB`` body filled with ``nibble`` (``0..15``)."""
    if not 0 <= nibble <= 15:
        raise GirbError(f"nibble {nibble} outside 0..15")
    fill_byte = nibble | (nibble << 4)
    return compress(bytes([fill_byte]) * GRID_BYTES)


def apply_lightmap_to_sector_rgb(rgb_data: bytes, nibbles: Sequence[int] | bytes,
                                 strength: float = 1.0) -> bytes:
    """Modulate a ``320x240`` RGB buffer by an ``80x60`` 4-bit ``GIRB`` lightmap.

    ``nibble == 8`` preserves the original RGB pixel unchanged; ``< 8`` dims into
    canopy/roof shadow and ``> 8`` brightens in sunlit/lantern regions.
    """
    if len(rgb_data) != 320 * 240 * 3:
        raise GirbError(f"expected 320x240x3 RGB bytes, got {len(rgb_data)}")
    if len(nibbles) != LIGHT_CELLS:
        raise GirbError(f"expected {LIGHT_CELLS} nibbles, got {len(nibbles)}")

    # Precompute 16x256 lookup table so shading an entire 320x240 sector takes <1ms.
    luts: list[bytes] = []
    for nib in range(16):
        factor = 1.0 + strength * ((nib - NEUTRAL_NIBBLE) / float(NEUTRAL_NIBBLE))
        luts.append(bytes(min(255, max(0, int(round(c * factor)))) for c in range(256)))

    out = bytearray(rgb_data)
    for ly in range(LIGHT_ROWS):
        row_nib_base = ly * LIGHT_COLS
        for lx in range(LIGHT_COLS):
            nib = nibbles[row_nib_base + lx]
            if nib == NEUTRAL_NIBBLE:
                continue
            lut = luts[nib]
            px0, py0 = lx * LIGHT_CELL_PX, ly * LIGHT_CELL_PX
            for dy in range(LIGHT_CELL_PX):
                base = ((py0 + dy) * 320 + px0) * 3
                for k in range(base, base + LIGHT_CELL_PX * 3):
                    out[k] = lut[out[k]]
    return bytes(out)


def render_lightmap_heatmap_rgba(
    width: int,
    height: int,
    nibble_lookup: Callable[[int, int], int],
    *,
    x0: int = 0,
    y0: int = 0,
) -> bytes:
    """Render an ``width x height`` RGBA heatmap for lightmap cells starting at
    pixel origin ``(x0, y0)``."""
    out = bytearray(width * height * 4)
    for py in range(height):
        ly = (y0 + py) // LIGHT_CELL_PX
        for px in range(width):
            lx = (x0 + px) // LIGHT_CELL_PX
            nib = nibble_lookup(lx, ly)
            if nib == NEUTRAL_NIBBLE:
                continue
            off = (py * width + px) * 4
            if nib > NEUTRAL_NIBBLE:
                alpha = min(210, 35 + (nib - NEUTRAL_NIBBLE) * 24)
                out[off:off + 4] = bytes((255, 214, 74, alpha))
            else:
                alpha = min(220, 35 + (NEUTRAL_NIBBLE - nib) * 23)
                out[off:off + 4] = bytes((48, 86, 214, alpha))
    return bytes(out)


__all__ = [
    "CELL_PX",
    "EMPTY_FILL",
    "GRID_BYTES",
    "GRID_CELLS",
    "GRID_COLS",
    "GRID_ROWS",
    "GirbError",
    "LIGHT_CELLS",
    "LIGHT_CELL_PX",
    "LIGHT_COLS",
    "LIGHT_ROWS",
    "LIGHT_ROW_STRIDE",
    "NEUTRAL_BYTE",
    "NEUTRAL_NIBBLE",
    "apply_lightmap_to_sector_rgb",
    "cells",
    "compress",
    "decompress",
    "default_girb_body",
    "pack_nibbles",
    "render_lightmap_heatmap_rgba",
    "unpack_nibbles",
]
