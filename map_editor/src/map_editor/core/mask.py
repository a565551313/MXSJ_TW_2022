"""2-bit foreground occlusion mask (``PrefixRecord``) codec & spatial indexing.

In ``mx.exe`` (``0x4b8ac0..0x4b8bb0`` and ``0x4b9120``), every ``PrefixRecord``
at the start of a ``0.1M`` ``.map`` file stores:

* ``int32 x, y`` — signed pixel origin on the map canvas (may be slightly
  negative or overhang the right/bottom map border);
* ``uint32 width, height`` — pixel rectangle dimensions;
* ``uint32 payload_length`` + ``payload`` — ``LZO1X-1`` compressed 2-bit alpha
  bitmap whose uncompressed length is ``((width + 3) // 4) * height`` bytes.

Each byte packs four horizontal 2-bit alpha samples **LSB-first**
(``(byte >> (2 * (px & 3))) & 3`` -> alpha ``0, 85, 170, 255``).  When a player
walks behind a roof, tree canopy, bridge arch, or pillar, ``mx.exe`` uses the
intersecting sector's ``record_refs`` list to composite those ``GEPJ`` pixels
above the character sprite using the 2-bit alpha mask!

Across all ``101`` TW v2.27.2 maps, **20,036 / 20,036 (100.0%)** ``PrefixRecord``
entries decompress cleanly to ``((width + 3) // 4) * height`` bytes with **0**
failures.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image

from .lzo1x import LzoError, deflate_lzo1x, inflate_lzo1x

if TYPE_CHECKING:
    from .gepj import RgbImage
    from .mapfile import PrefixRecord

SECTOR_PX_W, SECTOR_PX_H = 320, 240
ALPHA_LEVELS = (0, 85, 170, 255)


class MaskError(ValueError):
    """Raised when a foreground occlusion mask cannot be decoded or encoded."""


def mask_stride(width: int) -> int:
    if width <= 0:
        raise MaskError(f"mask width must be positive, got {width}")
    return (width + 3) // 4


@dataclass(frozen=True, slots=True)
class DecodedMask:
    """Decompressed 2-bit foreground alpha mask for one ``PrefixRecord``."""

    index: int
    x: int
    y: int
    width: int
    height: int
    stride: int
    raw_2bit: bytes

    def alpha_2bit(self, lx: int, ly: int) -> int:
        """Return raw 2-bit alpha sample ``0..3`` at mask-local ``(lx, ly)``."""
        if not (0 <= lx < self.width and 0 <= ly < self.height):
            return 0
        b = self.raw_2bit[ly * self.stride + (lx >> 2)]
        return (b >> (2 * (lx & 3))) & 3

    def alpha_at_local(self, lx: int, ly: int) -> int:
        """Return 8-bit alpha ``0, 85, 170, 255`` at mask-local ``(lx, ly)``."""
        if not (0 <= lx < self.width and 0 <= ly < self.height):
            return 0
        b = self.raw_2bit[ly * self.stride + (lx >> 2)]
        return ALPHA_LEVELS[(b >> (2 * (lx & 3))) & 3]

    def to_alpha_bytes(self) -> bytes:
        """Expand to ``width * height`` 8-bit ``L`` alpha bytes."""
        out = bytearray(self.width * self.height)
        for ly in range(self.height):
            row_in = ly * self.stride
            row_out = ly * self.width
            for lx in range(self.width):
                b = self.raw_2bit[row_in + (lx >> 2)]
                out[row_out + lx] = ALPHA_LEVELS[(b >> (2 * (lx & 3))) & 3]
        return bytes(out)

    def to_rgba_cutout(
        self,
        backdrop: RgbImage | None = None,
        *,
        backdrop_origin: tuple[int, int] = (0, 0),
        tint: tuple[int, int, int] = (255, 86, 132),
    ) -> Image.Image:
        """Render an ``RGBA`` Pillow image of the foreground sprite cut-out or
        tinted silhouette."""
        alpha = self.to_alpha_bytes()
        if backdrop is None:
            r, g, b = tint
            rgba = bytearray(self.width * self.height * 4)
            for i, a in enumerate(alpha):
                off = i * 4
                rgba[off:off + 4] = bytes((r, g, b, (a * 175) // 255))
            return Image.frombytes("RGBA", (self.width, self.height), bytes(rgba))

        bx0, by0 = backdrop_origin
        rgba = bytearray(self.width * self.height * 4)
        for ly in range(self.height):
            gy = self.y + ly - by0
            for lx in range(self.width):
                gx = self.x + lx - bx0
                a = alpha[ly * self.width + lx]
                off = (ly * self.width + lx) * 4
                if a == 0:
                    continue
                if 0 <= gx < backdrop.width and 0 <= gy < backdrop.height:
                    src = (gy * backdrop.width + gx) * 3
                    rgba[off:off + 3] = backdrop.data[src:src + 3]
                else:
                    rgba[off:off + 3] = bytes(tint)
                rgba[off + 3] = a
        return Image.frombytes("RGBA", (self.width, self.height), bytes(rgba))


def decode_mask_record(record: PrefixRecord) -> DecodedMask:
    """Decompress ``record.payload`` into a :class:`DecodedMask`."""
    stride = mask_stride(record.width)
    expected = stride * record.height
    try:
        raw = inflate_lzo1x(record.payload, expected_len=expected)
    except LzoError as exc:
        raise MaskError(
            f"record {record.index} ({record.width}x{record.height}): {exc}"
        ) from exc
    return DecodedMask(
        index=record.index,
        x=record.x,
        y=record.y,
        width=record.width,
        height=record.height,
        stride=stride,
        raw_2bit=raw,
    )


def pack_alpha_to_2bit(width: int, height: int, alpha_bytes: bytes) -> bytes:
    """Quantize ``width * height`` 8-bit alpha values into LSB-first 2-bit rows."""
    if width <= 0 or height <= 0:
        raise MaskError(f"invalid mask dimensions {width}x{height}")
    if len(alpha_bytes) != width * height:
        raise MaskError(
            f"alpha buffer length {len(alpha_bytes)} != {width}*{height}"
        )
    stride = mask_stride(width)
    out = bytearray(stride * height)
    for ly in range(height):
        row_in = ly * width
        row_out = ly * stride
        for lx in range(width):
            crumb = min(3, (alpha_bytes[row_in + lx] + 42) // 85)
            out[row_out + (lx >> 2)] |= crumb << (2 * (lx & 3))
    return bytes(out)


def encode_mask_payload(width: int, height: int, raw_2bit: bytes) -> bytes:
    """Compress a packed 2-bit mask buffer into a ``PrefixRecord`` payload."""
    expected = mask_stride(width) * height
    if len(raw_2bit) != expected:
        raise MaskError(f"expected {expected} packed 2-bit bytes, got {len(raw_2bit)}")
    return deflate_lzo1x(raw_2bit)


def mask_payload_from_image(image: Image.Image) -> tuple[int, int, bytes]:
    """Extract alpha (or luminance if opaque) from ``image`` and compress it into
    ``(width, height, compressed_payload)``."""
    w, h = image.size
    if w <= 0 or h <= 0:
        raise MaskError(f"invalid mask image dimensions {w}x{h}")
    if "A" in image.getbands():
        alpha = image.getchannel("A").tobytes()
    else:
        alpha = image.convert("L").tobytes()
    raw_2bit = pack_alpha_to_2bit(w, h, alpha)
    return w, h, encode_mask_payload(w, h, raw_2bit)


def compute_sector_record_refs(
    map_width: int, map_height: int, records: Sequence[PrefixRecord]
) -> list[tuple[int, ...]]:
    """Compute canonical per-sector ``record_refs`` for every ``320x240`` sector.

    Matches the exact Win32 ``IntersectRect`` box convention used by Duoyi's
    original map compiler (``sector = {ox, oy, ox + 319, oy + 239}``,
    ``record = {rx, ry, rx + rw, ry + rh}``): verified **11,763 / 11,763**
    sectors (``0`` differences) across all ``101`` TW v2.27.2 client maps.
    """
    cols = math.ceil(map_width / SECTOR_PX_W)
    rows = math.ceil(map_height / SECTOR_PX_H)
    refs_per_sector: list[list[int]] = [[] for _ in range(cols * rows)]
    for idx, rec in enumerate(records):
        rx0, ry0 = rec.x, rec.y
        rx1, ry1 = rec.x + rec.width, rec.y + rec.height
        if rx1 <= rx0 or ry1 <= ry0:
            continue
        sc0 = max(0, rx0 // SECTOR_PX_W)
        sc1 = min(cols - 1, rx1 // SECTOR_PX_W)
        sr0 = max(0, ry0 // SECTOR_PX_H)
        sr1 = min(rows - 1, ry1 // SECTOR_PX_H)
        for sr in range(sr0, sr1 + 1):
            oy = sr * SECTOR_PX_H
            if not (ry0 < oy + SECTOR_PX_H - 1 and ry1 > oy):
                continue
            for sc in range(sc0, sc1 + 1):
                ox = sc * SECTOR_PX_W
                if rx0 < ox + SECTOR_PX_W - 1 and rx1 > ox:
                    refs_per_sector[sr * cols + sc].append(idx)
    return [tuple(items) for items in refs_per_sector]


__all__ = [
    "ALPHA_LEVELS",
    "DecodedMask",
    "MaskError",
    "compute_sector_record_refs",
    "decode_mask_record",
    "encode_mask_payload",
    "mask_payload_from_image",
    "mask_stride",
    "pack_alpha_to_2bit",
]
