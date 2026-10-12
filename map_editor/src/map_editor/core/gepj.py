"""GEPJ image payload decoder.

``GEPJ`` is not a standard JPEG.  Each sector payload is a 26-byte table of 13
little-endian u16 lengths followed by 13 byte ranges:

* segment 0 is a shared JPEG header that ends right after the SOS component
  selectors, and carries a proprietary ``FF A0`` marker after ``SOI``;
* segments 1..12 are twelve *independent* 80x80 entropy-coded scans, stored
  **unstuffed** (literal ``FF`` is not followed by ``00``).

To decode one scan we rebuild a normal JPEG: drop ``FF A0``, widen the SOS length
from ``0009`` to ``000C`` and append the missing ``00 3F 00`` spectral-selection
bytes, re-stuff ``FF -> FF 00``, and add ``EOI``.  The twelve 80x80 pieces then
tile into a 320x240 sector, and sectors tile into the full map.

The reference implementation in
``work/dream-world-connect-login-map/tools/gepj_decoder.py`` shells out to
ImageMagick ``convert``.  That is unusable in a distributed EXE, so this module
decodes with Pillow instead.  ``tests/test_gepj.py`` proves the two agree.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image

from .mapfile import PIECE_PX, SECTOR_PX_H, SECTOR_PX_W, MapDocument, Sector

PIECES_PER_SECTOR = 12
PIECES_PER_ROW = 4           # 4 x 3 arrangement inside a 320x240 sector

_SOS_TAIL = b"\xff\xda\x00\x09\x03\x01\x00\x02\x11\x03\x22"
_SOS_FIXED = b"\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x22\x00\x3f\x00"
_SOF_80 = b"\xff\xc0\x00\x11\x08\x00\x50\x00\x50"
_SOI = b"\xff\xd8"
_PROPRIETARY_A0 = b"\xff\xa0"
_EOI = b"\xff\xd9"


class GepjError(ValueError):
    """Raised when a GEPJ payload cannot be turned into pixels."""


@dataclass(frozen=True, slots=True)
class RgbImage:
    width: int
    height: int
    data: bytes

    def __post_init__(self) -> None:
        if len(self.data) != self.width * self.height * 3:
            raise GepjError(
                f"RGB buffer {len(self.data)}B != {self.width}x{self.height}x3")


def build_jpeg_header(payload: bytes, head_len: int) -> bytes:
    """Repair the shared GEPJ header into a standard baseline-JPEG header."""
    if payload[:4] != _SOI + _PROPRIETARY_A0:
        raise GepjError(f"unknown GEPJ preamble {payload[:4]!r}")
    header = payload[:head_len]
    if not header.endswith(_SOS_TAIL):
        raise GepjError("unsupported GEPJ scan header")
    if _SOF_80 not in header:
        raise GepjError("unsupported JPEG piece dimensions (expected 80x80)")
    return _SOI + header[4:-11] + _SOS_FIXED


def split_scans(payload: bytes, segment_lengths: tuple[int, ...] | list[int]) -> list[bytes]:
    """Return the twelve raw, unstuffed 80x80 scan streams."""
    if len(segment_lengths) != 13 or any(n < 1 for n in segment_lengths):
        raise GepjError("expected 13 nonempty GEPJ segments")
    if sum(segment_lengths) != len(payload):
        raise GepjError("GEPJ segment lengths do not sum to the payload length")
    head_len = segment_lengths[0]
    parts: list[bytes] = []
    at = head_len
    for size in segment_lengths[1:]:
        parts.append(payload[at:at + size])
        at += size
    if len(parts) != PIECES_PER_SECTOR:
        raise GepjError(f"expected {PIECES_PER_SECTOR} scans, got {len(parts)}")
    return parts


def decode_scan(jpeg_header: bytes, scan: bytes) -> bytes:
    """Decode one 80x80 scan to RGB bytes using Pillow (no external process)."""
    blob = jpeg_header + scan.replace(b"\xff", b"\xff\x00") + _EOI
    try:
        with Image.open(io.BytesIO(blob)) as img:
            img.load()
            rgb = img.convert("RGB")
            if rgb.size != (PIECE_PX, PIECE_PX):
                raise GepjError(f"scan decoded to {rgb.size}, expected 80x80")
            return rgb.tobytes()
    except GepjError:
        raise
    except Exception as exc:                      # PIL raises many types
        raise GepjError(f"JPEG decode failed: {exc}") from exc


def decode_sector_image(payload: bytes, segment_lengths: tuple[int, ...] | list[int]) -> RgbImage:
    """Decode a whole sector payload into a 320x240 RGB image."""
    head_len = segment_lengths[0]
    jpeg_header = build_jpeg_header(payload, head_len)
    canvas = bytearray(SECTOR_PX_W * SECTOR_PX_H * 3)
    for j, scan in enumerate(split_scans(payload, segment_lengths)):
        pixels = decode_scan(jpeg_header, scan)
        x = (j % PIECES_PER_ROW) * PIECE_PX
        y = (j // PIECES_PER_ROW) * PIECE_PX
        for row in range(PIECE_PX):
            dest = ((y + row) * SECTOR_PX_W + x) * 3
            src = row * PIECE_PX * 3
            canvas[dest:dest + PIECE_PX * 3] = pixels[src:src + PIECE_PX * 3]
    return RgbImage(SECTOR_PX_W, SECTOR_PX_H, bytes(canvas))


def render_full(doc: MapDocument) -> RgbImage:
    """Render the entire map, cropped to the header dimensions.

    Fine for the sample maps; the UI should prefer :func:`render_region` because
    a 10000x6000 map is 60 M pixels (180 MB of RGB).
    """
    w, h = doc.header.width, doc.header.height
    return _composite(doc, 0, 0, w, h)


def render_region(doc: MapDocument, x0: int, y0: int, x1: int, y1: int) -> RgbImage:
    """Render only the pixels in ``[x0,x1) x [y0,y1)``.

    Sectors that do not intersect the region are never decoded, which is what
    makes a 800-sector map usable interactively.
    """
    w, h = doc.header.width, doc.header.height
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        raise GepjError(f"empty region {x0},{y0}..{x1},{y1}")
    return _composite(doc, x0, y0, x1, y1)


def _composite(doc: MapDocument, x0: int, y0: int, x1: int, y1: int) -> RgbImage:
    out_w, out_h = x1 - x0, y1 - y0
    canvas = bytearray(out_w * out_h * 3)
    cols, rows = doc.header.sector_columns, doc.header.sector_rows
    sc0, sc1 = x0 // SECTOR_PX_W, (x1 - 1) // SECTOR_PX_W
    sr0, sr1 = y0 // SECTOR_PX_H, (y1 - 1) // SECTOR_PX_H
    for sr in range(sr0, min(sr1, rows - 1) + 1):
        for sc in range(sc0, min(sc1, cols - 1) + 1):
            sector: Sector = doc.sector(sr * cols + sc)
            img = decode_sector_image(doc.read_image_payload(sector), sector.segment_lengths)
            _blit(canvas, out_w, out_h, x0, y0, img, sector.origin_x, sector.origin_y)
    return RgbImage(out_w, out_h, bytes(canvas))


def _blit(canvas: bytearray, out_w: int, out_h: int, x0: int, y0: int,
          img: RgbImage, sx: int, sy: int) -> None:
    """Copy the intersection of ``img`` (at sector origin) into the crop buffer."""
    dx0, dy0 = max(x0, sx), max(y0, sy)
    dx1 = min(x0 + out_w, sx + img.width)
    dy1 = min(y0 + out_h, sy + img.height)
    if dx1 <= dx0 or dy1 <= dy0:
        return
    row_bytes = (dx1 - dx0) * 3
    for y in range(dy0, dy1):
        src = ((y - sy) * img.width + (dx0 - sx)) * 3
        dest = ((y - y0) * out_w + (dx0 - x0)) * 3
        canvas[dest:dest + row_bytes] = img.data[src:src + row_bytes]
