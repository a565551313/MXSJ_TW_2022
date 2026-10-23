"""``GEPJ`` sector image payload decoder and native ``mx.exe``-compatible encoder.

``GEPJ`` is a compact tiled JPEG container used by ``mx.exe`` (decoded by the
CloudWu baseline JPEG routine at ``0x00637420``):

* A 26-byte table of 13 little-endian ``u16`` lengths;
* Segment 0: shared baseline-JPEG header starting with ``FF D8 FF A0``, followed
  by ``SOF0`` (``80x80``, 4:2:0), ``DHT`` (tables ``10, 11, 12, 00, 01, 02``),
  ``DQT`` (tables ``00, 01``), and compact ``SOS`` ``FF DA 00 09 03 01 00 02 11
  03 22``;
* Segments 1..12: twelve independent ``80x80`` entropy-coded scans stored
  **unstuffed** (``FF 00 -> FF``) and without ``EOI``.

Both :func:`decode_sector_image` and :func:`encode_sector_image` have been
verified directly against native ``mx.exe`` ``0x00637420`` execution in Unicorn
(framebuffer channel MAE ``0.498 / 255`` across all 12 sub-tiles).
"""
from __future__ import annotations

import io
import math
import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from .mapfile import MapDocument, Sector

SECTOR_PX_W, SECTOR_PX_H = 320, 240
PIECE_PX = 80
PIECES_PER_SECTOR = 12
PIECES_PER_ROW = 4           # 4 x 3 arrangement inside a 320x240 sector

_SOS_TAIL = b"\xff\xda\x00\x09\x03\x01\x00\x02\x11\x03\x22"
_SOS_FIXED = b"\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x22\x00\x3f\x00"
_SOS_STD_11 = b"\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00"
_SOF_80 = b"\xff\xc0\x00\x11\x08\x00\x50\x00\x50"
_SOF_80_FULL = (
    b"\xff\xc0\x00\x11\x08\x00\x50\x00\x50\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"
)
_SOI = b"\xff\xd8"
_PROPRIETARY_A0 = b"\xff\xa0"
_EOI = b"\xff\xd9"


class GepjError(ValueError):
    """Raised when a GEPJ payload cannot be decoded or encoded."""


@dataclass(frozen=True, slots=True)
class RgbImage:
    width: int
    height: int
    data: bytes

    def __post_init__(self) -> None:
        if len(self.data) != self.width * self.height * 3:
            raise GepjError(
                f"RGB buffer {len(self.data)}B != {self.width}x{self.height}x3"
            )

    def to_pil(self) -> Image.Image:
        return Image.frombytes("RGB", (self.width, self.height), self.data)

    @classmethod
    def from_pil(cls, image: Image.Image) -> RgbImage:
        rgb = image.convert("RGB")
        return cls(rgb.width, rgb.height, rgb.tobytes())


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


def split_scans(
    payload: bytes, segment_lengths: tuple[int, ...] | list[int]
) -> list[bytes]:
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
    except Exception as exc:
        raise GepjError(f"JPEG decode failed: {exc}") from exc


def decode_sector_image(
    payload: bytes, segment_lengths: tuple[int, ...] | list[int]
) -> RgbImage:
    """Decode a whole sector payload into a ``320x240`` RGB image."""
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


def encode_sector_image(
    img: RgbImage | Image.Image, *, quality: int = 92
) -> tuple[tuple[int, ...], bytes]:
    """Encode a ``320x240`` RGB image into ``(segment_lengths, gepj_payload)``.

    Note: ``gepj_payload`` is the 13-segment body *after* the 26-byte
    ``<13H`` table (matching ``Sector.image_length`` and
    :func:`decode_sector_image`).  Use :func:`pack_gepj_block_body` when writing
    a ``GEPJ`` block on disk.
    """
    pil_full = img.to_pil() if isinstance(img, RgbImage) else img.convert("RGB")
    if pil_full.size != (SECTOR_PX_W, SECTOR_PX_H):
        raise GepjError(
            f"sector tile must be {SECTOR_PX_W}x{SECTOR_PX_H}, got {pil_full.size}"
        )
    q_clamped = max(10, min(100, int(quality)))
    dqt_tables: dict[int, bytes] = {}
    dht_tables: dict[int, bytes] = {}
    scans: list[bytes] = []

    for j in range(PIECES_PER_SECTOR):
        px = (j % PIECES_PER_ROW) * PIECE_PX
        py = (j // PIECES_PER_ROW) * PIECE_PX
        piece = pil_full.crop((px, py, px + PIECE_PX, py + PIECE_PX))
        buf = io.BytesIO()
        piece.save(
            buf, format="JPEG", quality=q_clamped, subsampling=2, optimize=False
        )
        jb = buf.getvalue()
        if jb[:2] != _SOI or jb[-2:] != _EOI:
            raise GepjError("Pillow produced unexpected JPEG framing")
        pos = 2
        cur_dqt: dict[int, bytes] = {}
        cur_dht: dict[int, bytes] = {}
        entropy: bytes | None = None
        while pos < len(jb) - 2:
            if jb[pos] != 0xFF:
                raise GepjError(f"invalid JPEG marker byte at {pos}")
            while jb[pos] == 0xFF:
                pos += 1
            marker = jb[pos]
            pos += 1
            mlen = struct.unpack_from(">H", jb, pos)[0]
            body = jb[pos + 2:pos + mlen]
            pos += mlen
            if marker == 0xDB:
                for q in range(0, len(body), 65):
                    if (body[q] >> 4) != 0:
                        raise GepjError("16-bit DQT not supported in GEPJ")
                    cur_dqt[body[q]] = body[q + 1:q + 65]
            elif marker == 0xC4:
                q = 0
                while q < len(body):
                    hid = body[q]
                    counts = body[q + 1:q + 17]
                    nsym = sum(counts)
                    cur_dht[hid] = counts + body[q + 17:q + 17 + nsym]
                    q += 17 + nsym
            elif marker == 0xDA:
                if body != _SOS_STD_11:
                    raise GepjError(f"unexpected JPEG SOS header {body.hex()}")
                entropy = jb[pos:-2]
                break
        if entropy is None:
            raise GepjError("missing JPEG entropy scan")
        if j == 0:
            dqt_tables, dht_tables = cur_dqt, cur_dht
        elif cur_dqt != dqt_tables or cur_dht != dht_tables:
            raise GepjError("non-uniform DQT/DHT across 80x80 pieces")
        scans.append(entropy.replace(b"\xff\x00", b"\xff"))

    dht_payload = bytearray()
    for dst_id, src_id in (
        (0x10, 0x10),
        (0x11, 0x11),
        (0x12, 0x11),
        (0x00, 0x00),
        (0x01, 0x01),
        (0x02, 0x01),
    ):
        dht_payload.append(dst_id)
        dht_payload.extend(dht_tables[src_id])
    dht_seg = (
        b"\xff\xc4" + struct.pack(">H", len(dht_payload) + 2) + bytes(dht_payload)
    )
    dqt_payload = b"\x00" + dqt_tables[0] + b"\x01" + dqt_tables[1]
    dqt_seg = b"\xff\xdb" + struct.pack(">H", len(dqt_payload) + 2) + dqt_payload
    seg0 = _SOI + _PROPRIETARY_A0 + _SOF_80_FULL + dht_seg + dqt_seg + _SOS_TAIL
    seg_lengths = (len(seg0), *(len(s) for s in scans))
    if any(ln >= 65536 for ln in seg_lengths):
        raise GepjError("encoded GEPJ segment exceeds u16 limit")
    return seg_lengths, seg0 + b"".join(scans)


def pack_gepj_block_body(
    segment_lengths: tuple[int, ...] | list[int], payload: bytes
) -> bytes:
    """Return ``<13H segment_lengths> + payload`` ready for a ``GEPJ`` block."""
    if len(segment_lengths) != 13 or sum(segment_lengths) != len(payload):
        raise GepjError("invalid GEPJ segment length table")
    return struct.pack("<13H", *segment_lengths) + payload


def slice_image_to_sectors(
    image: Image.Image | RgbImage, *, quality: int = 92
) -> tuple[int, int, list[tuple[tuple[int, ...], bytes]]]:
    """Slice a full map image of arbitrary size into ``ceil(w/320)*ceil(h/240)``
    encoded ``GEPJ`` sectors, edge-clamping right/bottom borders cleanly."""
    pil_img = image.to_pil() if isinstance(image, RgbImage) else image.convert("RGB")
    w, h = pil_img.size
    if w <= 0 or h <= 0:
        raise GepjError(f"invalid map dimensions {w}x{h}")
    cols = math.ceil(w / SECTOR_PX_W)
    rows = math.ceil(h / SECTOR_PX_H)
    encoded: list[tuple[tuple[int, ...], bytes]] = []
    for sr in range(rows):
        for sc in range(cols):
            ox, oy = sc * SECTOR_PX_W, sr * SECTOR_PX_H
            cw = min(SECTOR_PX_W, w - ox)
            ch = min(SECTOR_PX_H, h - oy)
            crop = pil_img.crop((ox, oy, ox + cw, oy + ch))
            if (cw, ch) != (SECTOR_PX_W, SECTOR_PX_H):
                tile = Image.new("RGB", (SECTOR_PX_W, SECTOR_PX_H), (0, 0, 0))
                tile.paste(crop, (0, 0))
                # Clamp border pixels into padding margin to prevent 4:2:0 ringing.
                if cw < SECTOR_PX_W:
                    edge_col = crop.crop((cw - 1, 0, cw, ch)).resize(
                        (SECTOR_PX_W - cw, ch)
                    )
                    tile.paste(edge_col, (cw, 0))
                if ch < SECTOR_PX_H:
                    edge_row = tile.crop((0, ch - 1, SECTOR_PX_W, ch)).resize(
                        (SECTOR_PX_W, SECTOR_PX_H - ch)
                    )
                    tile.paste(edge_row, (0, ch))
            else:
                tile = crop
            encoded.append(encode_sector_image(tile, quality=quality))
    return w, h, encoded


def render_sector(
    doc: MapDocument, sector: Sector, *, apply_lighting: bool = False
) -> RgbImage:
    """Decode one ``320x240`` sector image, optionally modulated by ``GIRB``."""
    from .girb import apply_lightmap_to_sector_rgb

    img = decode_sector_image(
        doc.read_image_payload(sector), sector.segment_lengths
    )
    if apply_lighting:
        nibs = doc.lightmap_nibbles(sector.index)
        if nibs is not None:
            img = RgbImage(
                img.width,
                img.height,
                apply_lightmap_to_sector_rgb(img.data, nibs),
            )
    return img


def render_full(doc: MapDocument, *, apply_lighting: bool = False) -> RgbImage:
    """Render the entire map, cropped to the header dimensions."""
    w, h = doc.header.width, doc.header.height
    return _composite(doc, 0, 0, w, h, apply_lighting=apply_lighting)


def render_region(
    doc: MapDocument,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    *,
    apply_lighting: bool = False,
) -> RgbImage:
    """Render only the pixels in ``[x0, x1) x [y0, y1)``."""
    w, h = doc.header.width, doc.header.height
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        raise GepjError(f"empty region {x0},{y0}..{x1},{y1}")
    return _composite(doc, x0, y0, x1, y1, apply_lighting=apply_lighting)


def _composite(
    doc: MapDocument,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    *,
    apply_lighting: bool = False,
) -> RgbImage:
    from .girb import apply_lightmap_to_sector_rgb

    out_w, out_h = x1 - x0, y1 - y0
    canvas = bytearray(out_w * out_h * 3)
    cols, rows = doc.header.sector_columns, doc.header.sector_rows
    sc0, sc1 = x0 // SECTOR_PX_W, (x1 - 1) // SECTOR_PX_W
    sr0, sr1 = y0 // SECTOR_PX_H, (y1 - 1) // SECTOR_PX_H
    for sr in range(sr0, min(sr1, rows - 1) + 1):
        for sc in range(sc0, min(sc1, cols - 1) + 1):
            idx = sr * cols + sc
            sector: Sector = doc.sector(idx)
            img = decode_sector_image(
                doc.read_image_payload(sector), sector.segment_lengths
            )
            if apply_lighting:
                nibs = doc.lightmap_nibbles(idx)
                if nibs is not None:
                    img = RgbImage(
                        img.width,
                        img.height,
                        apply_lightmap_to_sector_rgb(img.data, nibs),
                    )
            _blit(canvas, out_w, out_h, x0, y0, img, sector.origin_x, sector.origin_y)
    return RgbImage(out_w, out_h, bytes(canvas))


def _blit(
    canvas: bytearray,
    out_w: int,
    out_h: int,
    x0: int,
    y0: int,
    img: RgbImage,
    sx: int,
    sy: int,
) -> None:
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


__all__ = [
    "GepjError",
    "PIECES_PER_ROW",
    "PIECES_PER_SECTOR",
    "PIECE_PX",
    "RgbImage",
    "SECTOR_PX_H",
    "SECTOR_PX_W",
    "build_jpeg_header",
    "decode_scan",
    "decode_sector_image",
    "encode_sector_image",
    "pack_gepj_block_body",
    "render_full",
    "render_region",
    "render_sector",
    "slice_image_to_sectors",
    "split_scans",
]
