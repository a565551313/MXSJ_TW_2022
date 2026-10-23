"""Map file format engine (reader, editor, and byte-verified serializer) for
MXSJ ``.map`` (``0.1M``) containers.

Verified invariants across all **101 / 101** TW v2.27.2 client ``.map`` files
(``11,763`` sectors, ``20,036`` ``PrefixRecord`` masks, ``266`` MB total):

* Header layout:
  ``b"0.1M" | u32 width | u32 height | u32[N] sector_offsets | u32 mask_tbl |
  u32 M | u32[M] record_offsets | PrefixRecord[0..M-1] | Sector[0..N-1]``
  where ``N = ceil(width / 320) * ceil(height / 240)`` and ``mask_tbl ==
  12 + 4 * N + 4`` (self-referential sentinel pointing to ``M``).
* ``98 / 101`` client maps end at the exact byte after ``Sector[N - 1]``'s
  4-byte ``GIRB`` terminator (``00 00 00 00``), and :meth:`MapDocument.to_bytes`
  reproduces every one of those ``98`` files **SHA-256 identically**.
* ``3 / 101`` client maps (``test_new2_1054.map`` ``+541`` B, ``test_1005.map``
  ``+9,889`` B, ``test_2302.map`` ``+18,951`` B) contain unreferenced dead tail
  bytes left behind by an earlier ``fopen("rb+")`` in-place save without
  ``SetEndOfFile``.  ``read_sector`` records those bytes in
  ``MapDocument.trailing_bytes`` rather than rejecting the map.

Pure Python + Pillow (for image slicing), zero Qt imports.
"""
from __future__ import annotations

import math
import os
import struct
import tempfile
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, replace
from itertools import pairwise
from pathlib import Path
from typing import BinaryIO

from PIL import Image

from .blk import BlkGrid
from .gepj import (
    RgbImage,
    decode_sector_image,
    encode_sector_image,
    pack_gepj_block_body,
    slice_image_to_sectors,
)
from .girb import (
    GRID_BYTES,
    LIGHT_CELL_PX,
    LIGHT_COLS,
    LIGHT_ROWS,
    NEUTRAL_NIBBLE,
    GirbError,
    cells,
    compress,
    decompress,
    default_girb_body,
    pack_nibbles,
    unpack_nibbles,
)
from .mask import (
    MAX_MAP_MASK_PIXELS,
    DecodedMask,
    compute_sector_record_refs,
    decode_mask_record,
    mask_payload_from_image,
)

MAGIC = b"0.1M"
SECTOR_PX_W, SECTOR_PX_H = 320, 240
CELL_PX = 20                 # mx.exe 0x4baebf: signed divide by 20
CELL_COLS_PER_SECTOR, CELL_ROWS_PER_SECTOR = 16, 12
CELLS_PER_SECTOR = CELL_COLS_PER_SECTOR * CELL_ROWS_PER_SECTOR   # 192
GEPJ_TAG = b"GEPJ"
LLEC_TAG = b"LLEC"
GIRB_TAG = b"GIRB"
GEPJ_SEGMENTS = 13           # 1 shared header + 12 independent 80x80 scans
MAX_BLOCKS_PER_SECTOR = 64   # guard against a corrupt chain looping forever
PIECE_PX = 80                # each scan is an 80x80 JPEG
MAX_SCAN_SECTORS = 4096      # bound for the sentinel scan
DEFAULT_GIRB_TRAILER = b"\x00\x00\x00\x00"


class MapFormatError(ValueError):
    """Raised when a file is not a readable or valid ``0.1M`` map."""


@dataclass(frozen=True, slots=True)
class MapHeader:
    width: int
    height: int
    sector_count: int
    sector_columns: int
    sector_rows: int
    record_count: int
    sector_offsets: tuple[int, ...]
    record_offsets: tuple[int, ...]
    file_length: int

    @property
    def grid_columns(self) -> int:
        """Logical walkable-grid columns (cells are 20x20 px, cropped to the map)."""
        return math.ceil(self.width / CELL_PX)

    @property
    def grid_rows(self) -> int:
        return math.ceil(self.height / CELL_PX)

    @property
    def light_columns(self) -> int:
        return self.sector_columns * LIGHT_COLS

    @property
    def light_rows(self) -> int:
        return self.sector_rows * LIGHT_ROWS


@dataclass(frozen=True, slots=True)
class Block:
    """A sector block whose tag is preserved verbatim across round-trips."""

    tag: str
    offset: int          # offset of the 4-byte tag
    length: int          # payload length, excluding tag + u32
    raw_tag: bytes = b""
    payload: bytes = b""

    @property
    def payload_offset(self) -> int:
        return self.offset + 8


@dataclass(frozen=True, slots=True)
class Sector:
    index: int
    row: int
    col: int
    offset: int
    length: int
    record_refs: tuple[int, ...]
    image_offset: int
    image_length: int
    segment_lengths: tuple[int, ...]
    cells_offset: int
    girb_offset: int
    girb_body: bytes
    girb_trailer: bytes
    extra_blocks: tuple[Block, ...] = ()

    @property
    def origin_x(self) -> int:
        return self.col * SECTOR_PX_W

    @property
    def origin_y(self) -> int:
        return self.row * SECTOR_PX_H


@dataclass(frozen=True, slots=True)
class PrefixRecord:
    index: int
    offset: int
    x: int
    y: int
    width: int
    height: int
    payload_length: int
    payload: bytes

    @property
    def total_length(self) -> int:
        return 20 + self.payload_length


def sniff(path: Path) -> bool:
    """Cheap check used by client discovery: is this plausibly a ``0.1M`` map?"""
    try:
        with path.open("rb") as fh:
            return fh.read(4) == MAGIC
    except OSError:
        return False


def detect_sector_count(fh: BinaryIO, file_length: int) -> int:
    """Find N via the self-referential u32 at ``12 + 4*N`` (== its own offset + 4)."""
    for n in range(1, MAX_SCAN_SECTORS + 1):
        at = 12 + 4 * n
        if at + 4 > file_length:
            break
        fh.seek(at)
        raw = fh.read(4)
        if len(raw) < 4:
            break
        if struct.unpack("<I", raw)[0] == at + 4:
            return n
    raise MapFormatError("sector-count sentinel not found; not a 0.1M map")


def read_header(fh: BinaryIO, file_length: int) -> MapHeader:
    fh.seek(0)
    head = fh.read(12)
    if len(head) < 12 or head[:4] != MAGIC:
        raise MapFormatError(f"missing {MAGIC!r} signature")
    width, height = struct.unpack_from("<II", head, 4)
    if not 0 < width <= 100_000 or not 0 < height <= 100_000:
        raise MapFormatError(f"implausible dimensions {width}x{height}")

    n = detect_sector_count(fh, file_length)
    fh.seek(12)
    offsets = struct.unpack(f"<{n}I", fh.read(4 * n))
    if any(b <= a for a, b in pairwise(offsets)):
        raise MapFormatError("sector offset table is not strictly increasing")
    if offsets[0] < 12 + 4 * n + 8:
        raise MapFormatError("first sector offset overlaps the header")

    fh.seek(12 + 4 * n + 4)
    (record_count,) = struct.unpack("<I", fh.read(4))
    if record_count > 1_000_000:
        raise MapFormatError(f"implausible prefix-record count {record_count}")
    record_offsets: tuple[int, ...] = ()
    if record_count:
        record_offsets = struct.unpack(f"<{record_count}I", fh.read(4 * record_count))
        if any(b <= a for a, b in pairwise(record_offsets)):
            raise MapFormatError("prefix-record offset table is not increasing")

    columns, rows = math.ceil(width / SECTOR_PX_W), math.ceil(height / SECTOR_PX_H)
    if columns * rows != n:
        raise MapFormatError(
            f"sector count {n} != ceil({width}/320)*ceil({height}/240)"
            f"={columns * rows}"
        )

    return MapHeader(
        width=width,
        height=height,
        sector_count=n,
        sector_columns=columns,
        sector_rows=rows,
        record_count=record_count,
        sector_offsets=offsets,
        record_offsets=record_offsets,
        file_length=file_length,
    )


def read_sector(fh: BinaryIO, header: MapHeader, index: int) -> Sector:
    offset = header.sector_offsets[index]
    is_last = index + 1 == header.sector_count
    end = header.file_length if is_last else header.sector_offsets[index + 1]
    fh.seek(offset)
    ref_raw = fh.read(4)
    if len(ref_raw) < 4:
        raise MapFormatError(f"sector {index}: truncated ref header")
    (refs,) = struct.unpack("<I", ref_raw)
    if refs > 1_000_000:
        raise MapFormatError(f"sector {index}: implausible reference count {refs}")
    refs_tuple: tuple[int, ...] = ()
    if refs:
        refs_tuple = struct.unpack(f"<{refs}I", fh.read(4 * refs))

    cursor = offset + 4 + 4 * refs
    image_offset: int | None = None
    image_length = 0
    segment_lengths: tuple[int, ...] = ()
    cells_offset: int | None = None
    girb_offset: int | None = None
    girb_body = b""
    girb_trailer = b""
    extra: list[Block] = []

    terminated = False
    for _ in range(MAX_BLOCKS_PER_SECTOR):
        if cursor + 8 > end:
            break
        fh.seek(cursor)
        tag = fh.read(4)
        (length,) = struct.unpack("<I", fh.read(4))
        body = cursor + 8
        if length < 0 or body + length > end:
            raise MapFormatError(
                f"sector {index}: block {tag!r} at {cursor} declares length {length}, "
                f"which runs past the sector end {end}"
            )
        if tag == GEPJ_TAG:
            if image_offset is not None:
                raise MapFormatError(f"sector {index}: duplicate GEPJ block")
            if length < GEPJ_SEGMENTS * 2:
                raise MapFormatError(f"sector {index}: image length {length} too small")
            segment_lengths = struct.unpack(
                f"<{GEPJ_SEGMENTS}H", fh.read(2 * GEPJ_SEGMENTS)
            )
            if sum(segment_lengths) != length - 2 * GEPJ_SEGMENTS:
                raise MapFormatError(
                    f"sector {index}: segment lengths sum to {sum(segment_lengths)}, "
                    f"expected {length - 2 * GEPJ_SEGMENTS}"
                )
            image_offset = body + 2 * GEPJ_SEGMENTS
            image_length = length - 2 * GEPJ_SEGMENTS
        elif tag == LLEC_TAG:
            if length != CELLS_PER_SECTOR:
                raise MapFormatError(f"sector {index}: LLEC length {length} != 192")
            cells_offset = body
        elif tag == GIRB_TAG:
            girb_offset = cursor
            girb_body = fh.read(length)
            if len(girb_body) != length:
                raise MapFormatError(f"sector {index}: truncated GIRB body")
            girb_trailer = fh.read(4)
            if len(girb_trailer) != 4:
                raise MapFormatError(f"sector {index}: truncated 4-byte GIRB trailer")
            cursor = body + length + 4
            terminated = True
            break
        else:
            payload = fh.read(length)
            if len(payload) != length:
                raise MapFormatError(f"sector {index}: truncated extra block {tag!r}")
            extra.append(Block(_tag_name(tag), cursor, length, tag, payload))
        cursor = body + length

    if not terminated:
        raise MapFormatError(
            f"sector {index}: no GIRB terminator before sector end {end}"
        )
    if image_offset is None:
        raise MapFormatError(f"sector {index}: no GEPJ image block")
    if cells_offset is None:
        raise MapFormatError(f"sector {index}: no LLEC block")
    if not is_last and cursor != end:
        raise MapFormatError(
            f"sector {index}: blocks end at {cursor}, expected {end}"
        )
    if is_last and cursor > end:
        raise MapFormatError(
            f"sector {index}: blocks overrun file end ({cursor} > {end})"
        )

    return Sector(
        index=index,
        row=index // header.sector_columns,
        col=index % header.sector_columns,
        offset=offset,
        length=cursor - offset,
        record_refs=refs_tuple,
        image_offset=image_offset,
        image_length=image_length,
        segment_lengths=segment_lengths,
        cells_offset=cells_offset,
        girb_offset=girb_offset,
        girb_body=girb_body,
        girb_trailer=girb_trailer,
        extra_blocks=tuple(extra),
    )


def _tag_name(tag: bytes) -> str:
    try:
        return tag.decode("ascii")
    except UnicodeDecodeError:
        return tag.hex()


def read_prefix_records(fh: BinaryIO, header: MapHeader) -> tuple[PrefixRecord, ...]:
    out: list[PrefixRecord] = []
    for i, off in enumerate(header.record_offsets):
        fh.seek(off)
        x, y, w, h, plen = struct.unpack("<2i3I", fh.read(20))
        if not 0 < w <= header.width * 4 or not 0 < h <= header.height * 4:
            raise MapFormatError(f"record {i}: implausible size {w}x{h}")
        if plen > 1 << 24:
            raise MapFormatError(f"record {i}: implausible payload {plen}")
        payload = fh.read(plen)
        if len(payload) != plen:
            raise MapFormatError(f"record {i}: truncated payload")
        out.append(PrefixRecord(i, off, x, y, w, h, plen, payload))
    return tuple(out)


class MapDocument:
    """Lazy reader + in-memory non-destructive editor + byte-accurate serializer
    for ``0.1M`` ``.map`` files."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._fh: BinaryIO = self.path.open("rb")
        self._fh.seek(0, 2)
        length = self._fh.tell()
        try:
            self.header = read_header(self._fh, length)
            self._records: list[PrefixRecord] = list(
                read_prefix_records(self._fh, self.header)
            )
        except Exception:
            self._fh.close()
            raise
        self._sectors: dict[int, Sector] = {}
        self._collision: dict[int, list[int] | None] = {}
        self._nibbles: dict[int, bytearray | None] = {}
        self._decoded_masks: dict[int, DecodedMask] = {}
        # Mutable overlays: untouched sectors read straight from self._fh!
        self._cell_overrides: dict[int, bytearray] = {}
        self._image_overrides: dict[int, tuple[tuple[int, ...], bytes]] = {}
        self._girb_overrides: dict[int, bytes] = {}
        self._ref_overrides: dict[int, tuple[int, ...]] = {}
        self.second_layer: BlkGrid | None = None
        self.dirty: bool = False

    @property
    def records(self) -> tuple[PrefixRecord, ...]:
        return tuple(self._records)

    @property
    def trailing_bytes(self) -> int:
        last = self.sector(self.header.sector_count - 1)
        return self.header.file_length - (last.offset + last.length)

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> MapDocument:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- sector & image accessors -----------------------------------------
    @property
    def sector_count(self) -> int:
        return self.header.sector_count

    def sector(self, index: int) -> Sector:
        if not 0 <= index < self.header.sector_count:
            raise IndexError(f"sector index {index} out of range")
        if index not in self._sectors:
            self._sectors[index] = read_sector(self._fh, self.header, index)
        base = self._sectors[index]
        refs = self._ref_overrides.get(index, base.record_refs)
        img_override = self._image_overrides.get(index)
        girb_body = self._girb_overrides.get(index, base.girb_body)
        if (
            refs is base.record_refs
            and img_override is None
            and girb_body is base.girb_body
        ):
            return base
        seg_lens = (
            img_override[0] if img_override is not None else base.segment_lengths
        )
        img_len = (
            len(img_override[1]) if img_override is not None else base.image_length
        )
        return replace(
            base,
            record_refs=refs,
            segment_lengths=seg_lens,
            image_length=img_len,
            girb_body=girb_body,
        )

    def iter_sectors(self) -> Iterator[Sector]:
        return (self.sector(i) for i in range(self.header.sector_count))

    def read_image_payload(self, sector: Sector) -> bytes:
        override = self._image_overrides.get(sector.index)
        if override is not None:
            return override[1]
        self._fh.seek(sector.image_offset)
        data = self._fh.read(sector.image_length)
        if len(data) != sector.image_length:
            raise MapFormatError(f"sector {sector.index}: truncated GEPJ payload")
        return data

    def replace_sector_image(
        self, sector_index: int, image: RgbImage | Image.Image, *, quality: int = 92
    ) -> tuple[tuple[int, ...], bytes]:
        """Encode and replace the ``320x240`` ``GEPJ`` tile of ``sector_index``."""
        _ = self.sector(sector_index)
        old = (
            self.sector(sector_index).segment_lengths,
            self.read_image_payload(self.sector(sector_index)),
        )
        encoded = encode_sector_image(image, quality=quality)
        self._image_overrides[sector_index] = encoded
        self.dirty = True
        return old

    def set_raw_sector_image(
        self, sector_index: int, seg_lengths: tuple[int, ...], payload: bytes
    ) -> None:
        _ = self.sector(sector_index)
        self._image_overrides[sector_index] = (seg_lengths, payload)
        self.dirty = True

    def import_full_image(
        self, image: Image.Image | RgbImage | Path | str, *, quality: int = 92
    ) -> None:
        """Replace every sector tile across the current map from a full-map image."""
        if isinstance(image, (Path, str)):
            with Image.open(image) as im:
                pil = im.convert("RGB")
        elif isinstance(image, RgbImage):
            pil = image.to_pil()
        else:
            pil = image.convert("RGB")
        if pil.size != (self.header.width, self.header.height):
            pil = pil.resize((self.header.width, self.header.height), Image.LANCZOS)
        _, _, encoded_sectors = slice_image_to_sectors(pil, quality=quality)
        for idx, (seg_lens, payload) in enumerate(encoded_sectors):
            _ = self.sector(idx)
            self._image_overrides[idx] = (seg_lens, payload)
        self.dirty = True

    # -- LLEC walkability & shade cell editing ----------------------------
    def read_cells(self, sector: Sector) -> bytes:
        override = self._cell_overrides.get(sector.index)
        if override is not None:
            return bytes(override)
        self._fh.seek(sector.cells_offset)
        raw = self._fh.read(CELLS_PER_SECTOR)
        if len(raw) != CELLS_PER_SECTOR:
            raise MapFormatError(f"sector {sector.index}: truncated LLEC cells")
        return raw

    def _mutable_sector_cells(self, sector_index: int) -> bytearray:
        buf = self._cell_overrides.get(sector_index)
        if buf is None:
            buf = bytearray(self.read_cells(self.sector(sector_index)))
            self._cell_overrides[sector_index] = buf
        return buf

    def cell_at_index(self, cx: int, cy: int) -> int | None:
        """Return ``LLEC`` byte at client cell ``(cx, cy)`` or ``None`` if outside."""
        if not (0 <= cx < self.header.grid_columns and 0 <= cy < self.header.grid_rows):
            return None
        sc, sr = cx // CELL_COLS_PER_SECTOR, cy // CELL_ROWS_PER_SECTOR
        index = sr * self.header.sector_columns + sc
        if index >= self.header.sector_count:
            return None
        raw = self.read_cells(self.sector(index))
        return raw[(cy % CELL_ROWS_PER_SECTOR) * CELL_COLS_PER_SECTOR
                   + (cx % CELL_COLS_PER_SECTOR)]

    def cell_at(self, x: int, y: int) -> int | None:
        """Raw ``LLEC`` byte for a pixel coordinate, or ``None`` outside map bounds."""
        return self.cell_at_index(x // CELL_PX, y // CELL_PX)

    def set_cell(self, cx: int, cy: int, value: int) -> int | None:
        """Set client cell ``(cx, cy)`` to ``value`` (``0..255``); returns previous."""
        if not (0 <= cx < self.header.grid_columns and 0 <= cy < self.header.grid_rows):
            return None
        if not 0 <= value <= 255:
            raise ValueError(f"cell byte out of range: {value}")
        sc, sr = cx // CELL_COLS_PER_SECTOR, cy // CELL_ROWS_PER_SECTOR
        index = sr * self.header.sector_columns + sc
        buf = self._mutable_sector_cells(index)
        slot = (
            (cy % CELL_ROWS_PER_SECTOR) * CELL_COLS_PER_SECTOR
            + (cx % CELL_COLS_PER_SECTOR)
        )
        prev = buf[slot]
        if prev != value:
            buf[slot] = value
            self.dirty = True
        return prev

    def paint_cells_brush(
        self, center_cx: int, center_cy: int, value: int, radius: int = 0
    ) -> dict[tuple[int, int], int]:
        """Paint square brush of radius ``radius`` cells; returns ``{(cx,cy): old}``."""
        changed: dict[tuple[int, int], int] = {}
        r = max(0, int(radius))
        for cy in range(center_cy - r, center_cy + r + 1):
            for cx in range(center_cx - r, center_cx + r + 1):
                prev = self.set_cell(cx, cy, value)
                if prev is not None and prev != value:
                    changed[(cx, cy)] = prev
        return changed

    def paint_cells_rect(
        self, cx0: int, cy0: int, cx1: int, cy1: int, value: int
    ) -> dict[tuple[int, int], int]:
        changed: dict[tuple[int, int], int] = {}
        x_lo, x_hi = sorted((cx0, cx1))
        y_lo, y_hi = sorted((cy0, cy1))
        for cy in range(max(0, y_lo), min(self.header.grid_rows - 1, y_hi) + 1):
            for cx in range(max(0, x_lo), min(self.header.grid_columns - 1, x_hi) + 1):
                prev = self.set_cell(cx, cy, value)
                if prev is not None and prev != value:
                    changed[(cx, cy)] = prev
        return changed

    def paint_cells_line(
        self, cx0: int, cy0: int, cx1: int, cy1: int, value: int, radius: int = 0
    ) -> dict[tuple[int, int], int]:
        """Bresenham cell line brush from ``(cx0, cy0)`` to ``(cx1, cy1)``."""
        changed: dict[tuple[int, int], int] = {}
        dx = abs(cx1 - cx0)
        dy = -abs(cy1 - cy0)
        sx = 1 if cx0 < cx1 else -1
        sy = 1 if cy0 < cy1 else -1
        err = dx + dy
        x, y = cx0, cy0
        while True:
            for k, old in self.paint_cells_brush(x, y, value, radius).items():
                changed.setdefault(k, old)
            if x == cx1 and y == cy1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return changed

    def flood_fill_cells(
        self, start_cx: int, start_cy: int, value: int
    ) -> dict[tuple[int, int], int]:
        """4-connected bucket fill of matching ``LLEC`` cells."""
        target = self.cell_at_index(start_cx, start_cy)
        if target is None or target == value:
            return {}
        changed: dict[tuple[int, int], int] = {}
        q = deque([(start_cx, start_cy)])
        seen = {(start_cx, start_cy)}
        while q:
            cx, cy = q.popleft()
            old = self.set_cell(cx, cy, value)
            if old is not None and old != value:
                changed[(cx, cy)] = old
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if (
                    (nx, ny) not in seen
                    and 0 <= nx < self.header.grid_columns
                    and 0 <= ny < self.header.grid_rows
                    and self.cell_at_index(nx, ny) == target
                ):
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return changed

    # -- GIRB lightmap & legacy collision u16 API -------------------------
    def collision_cells(self, sector: Sector) -> list[int] | None:
        """The 1,200 u16 cells of one sector, or ``None`` if corrupted."""
        if sector.index not in self._collision:
            try:
                self._collision[sector.index] = cells(sector.girb_body)
            except (GirbError, IndexError):
                self._collision[sector.index] = None
        return self._collision[sector.index]

    def lightmap_nibbles(self, sector_index: int) -> bytearray | None:
        """Return mutable ``4,800``-entry ``80x60`` brightness array (``0..15``)."""
        if sector_index not in self._nibbles:
            sec = self.sector(sector_index)
            try:
                raw = decompress(sec.girb_body, limit=GRID_BYTES)
                self._nibbles[sector_index] = unpack_nibbles(raw)
            except GirbError:
                self._nibbles[sector_index] = None
        return self._nibbles[sector_index]

    def lightmap_at_index(self, lx: int, ly: int) -> int | None:
        if not (
            0 <= lx < self.header.light_columns
            and 0 <= ly < self.header.light_rows
        ):
            return None
        sc, sr = lx // LIGHT_COLS, ly // LIGHT_ROWS
        nibs = self.lightmap_nibbles(sr * self.header.sector_columns + sc)
        if nibs is None:
            return None
        return nibs[(ly % LIGHT_ROWS) * LIGHT_COLS + (lx % LIGHT_COLS)]

    def lightmap_at(self, x: int, y: int) -> int | None:
        return self.lightmap_at_index(x // LIGHT_CELL_PX, y // LIGHT_CELL_PX)

    def _flush_sector_lightmap(self, sector_index: int) -> None:
        nibs = self._nibbles.get(sector_index)
        if nibs is None:
            return
        raw = pack_nibbles(nibs)
        self._girb_overrides[sector_index] = compress(raw)
        self._collision.pop(sector_index, None)
        self.dirty = True

    def set_lightmap_nibble(self, lx: int, ly: int, nibble: int) -> int | None:
        if not 0 <= nibble <= 15:
            raise GirbError(f"lightmap nibble must be 0..15, got {nibble}")
        if not (
            0 <= lx < self.header.light_columns
            and 0 <= ly < self.header.light_rows
        ):
            return None
        sc, sr = lx // LIGHT_COLS, ly // LIGHT_ROWS
        sidx = sr * self.header.sector_columns + sc
        nibs = self.lightmap_nibbles(sidx)
        if nibs is None:
            nibs = bytearray([NEUTRAL_NIBBLE] * (LIGHT_COLS * LIGHT_ROWS))
            self._nibbles[sidx] = nibs
        slot = (ly % LIGHT_ROWS) * LIGHT_COLS + (lx % LIGHT_COLS)
        prev = nibs[slot]
        if prev != nibble:
            nibs[slot] = nibble
            self._flush_sector_lightmap(sidx)
        return prev

    def paint_lightmap_brush(
        self, center_lx: int, center_ly: int, nibble: int, radius: int = 2
    ) -> dict[tuple[int, int], int]:
        changed: dict[tuple[int, int], int] = {}
        r = max(0, int(radius))
        touched_sectors: set[int] = set()
        for ly in range(center_ly - r, center_ly + r + 1):
            for lx in range(center_lx - r, center_lx + r + 1):
                if not (
                    0 <= lx < self.header.light_columns
                    and 0 <= ly < self.header.light_rows
                ):
                    continue
                sc, sr = lx // LIGHT_COLS, ly // LIGHT_ROWS
                sidx = sr * self.header.sector_columns + sc
                nibs = self.lightmap_nibbles(sidx)
                if nibs is None:
                    nibs = bytearray([NEUTRAL_NIBBLE] * (LIGHT_COLS * LIGHT_ROWS))
                    self._nibbles[sidx] = nibs
                slot = (ly % LIGHT_ROWS) * LIGHT_COLS + (lx % LIGHT_COLS)
                prev = nibs[slot]
                if prev != nibble:
                    nibs[slot] = nibble
                    changed[(lx, ly)] = prev
                    touched_sectors.add(sidx)
        for sidx in touched_sectors:
            self._flush_sector_lightmap(sidx)
        return changed

    def reset_sector_lightmap(
        self, sector_index: int, nibble: int = NEUTRAL_NIBBLE
    ) -> None:
        self._nibbles[sector_index] = bytearray(
            [nibble] * (LIGHT_COLS * LIGHT_ROWS)
        )
        self._flush_sector_lightmap(sector_index)

    def collision_at(self, x: int, y: int) -> int | None:
        from .girb import CELL_PX as CPX
        from .girb import GRID_COLS, GRID_ROWS

        cx, cy = x // CPX, y // CPX
        sc, sr = cx // GRID_COLS, cy // GRID_ROWS
        if (
            not 0 <= sc < self.header.sector_columns
            or not 0 <= sr < self.header.sector_rows
        ):
            return None
        index = sr * self.header.sector_columns + sc
        if index >= self.header.sector_count:
            return None
        values = self.collision_cells(self.sector(index))
        if values is None:
            return None
        return values[(cy % GRID_ROWS) * GRID_COLS + (cx % GRID_COLS)]

    def collision_stats(self) -> dict:
        decoded = failed = 0
        seen: set[int] = set()
        for s in self.iter_sectors():
            values = self.collision_cells(s)
            if values is None:
                failed += 1
            else:
                decoded += 1
                seen.update(values)
        return {
            "sectors": self.header.sector_count,
            "decoded": decoded,
            "failed": failed,
            "distinct_values": len(seen),
            "uniform": len(seen) <= 1,
        }

    # -- Foreground occlusion masks (PrefixRecord) ------------------------
    def out_of_bounds_records(self) -> list[PrefixRecord]:
        h = self.header
        return [
            r
            for r in self._records
            if r.x < 0
            or r.y < 0
            or r.x + r.width > h.width
            or r.y + r.height > h.height
        ]

    def decode_record(self, index: int) -> DecodedMask:
        if index not in self._decoded_masks:
            record = self._records[index]
            cached_pixels = sum(
                mask.width * mask.height for mask in self._decoded_masks.values()
            )
            if cached_pixels + record.width * record.height > MAX_MAP_MASK_PIXELS:
                raise MapFormatError(
                    "decoded foreground masks exceed the "
                    f"{MAX_MAP_MASK_PIXELS:,}-pixel per-map safety budget"
                )
            self._decoded_masks[index] = decode_mask_record(record)
        return self._decoded_masks[index]

    def rebuild_sector_refs(self) -> None:
        refs_list = compute_sector_record_refs(
            self.header.width, self.header.height, self._records
        )
        for idx, refs in enumerate(refs_list):
            self._ref_overrides[idx] = refs
        self.header = replace(self.header, record_count=len(self._records))
        self.dirty = True

    def _reindex_records(self) -> None:
        self._records = [
            PrefixRecord(
                i, 0, r.x, r.y, r.width, r.height, len(r.payload), r.payload
            )
            for i, r in enumerate(self._records)
        ]
        self._decoded_masks.clear()

    def add_record_from_image(
        self, image: Image.Image | Path | str, x: int, y: int
    ) -> PrefixRecord:
        if isinstance(image, (Path, str)):
            with Image.open(image) as im:
                w, h, payload = mask_payload_from_image(im)
        else:
            w, h, payload = mask_payload_from_image(image)
        rec = PrefixRecord(len(self._records), 0, x, y, w, h, len(payload), payload)
        self._records.append(rec)
        self._reindex_records()
        self.rebuild_sector_refs()
        return self._records[-1]

    def move_record(self, index: int, new_x: int, new_y: int) -> tuple[int, int]:
        rec = self._records[index]
        old = (rec.x, rec.y)
        self._records[index] = replace(rec, x=new_x, y=new_y)
        self._decoded_masks.pop(index, None)
        self.rebuild_sector_refs()
        return old

    def remove_record(self, index: int) -> PrefixRecord:
        removed = self._records.pop(index)
        self._reindex_records()
        self.rebuild_sector_refs()
        return removed

    def set_records_state(
        self,
        records: list[PrefixRecord],
        ref_overrides: dict[int, tuple[int, ...]],
    ) -> None:
        self._records = list(records)
        self._decoded_masks.clear()
        self._ref_overrides = dict(ref_overrides)
        self.header = replace(self.header, record_count=len(self._records))
        self.dirty = True

    # -- Container serialization & verified atomic save -------------------
    def _serialize_sector(self, index: int) -> bytes:
        sec = self.sector(index)
        img_payload = self.read_image_payload(sec)
        gepj_body = pack_gepj_block_body(sec.segment_lengths, img_payload)
        llec_body = self.read_cells(sec)
        out = bytearray()
        out.extend(struct.pack("<I", len(sec.record_refs)))
        if sec.record_refs:
            out.extend(struct.pack(f"<{len(sec.record_refs)}I", *sec.record_refs))
        out.extend(GEPJ_TAG)
        out.extend(struct.pack("<I", len(gepj_body)))
        out.extend(gepj_body)
        out.extend(LLEC_TAG)
        out.extend(struct.pack("<I", len(llec_body)))
        out.extend(llec_body)
        for blk in sec.extra_blocks:
            raw_tag = (
                blk.raw_tag
                if len(blk.raw_tag) == 4
                else blk.tag.encode("ascii")[:4]
            )
            out.extend(raw_tag)
            out.extend(struct.pack("<I", len(blk.payload)))
            out.extend(blk.payload)
        out.extend(GIRB_TAG)
        out.extend(struct.pack("<I", len(sec.girb_body)))
        out.extend(sec.girb_body)
        out.extend(sec.girb_trailer if len(sec.girb_trailer) == 4
                   else DEFAULT_GIRB_TRAILER)
        return bytes(out)

    def to_bytes(self) -> bytes:
        """Serialize the complete ``0.1M`` container to bytes."""
        n = self.header.sector_count
        m = len(self._records)
        mask_table_off = 12 + 4 * n + 4
        cursor = mask_table_off + 4 + 4 * m

        record_offsets: list[int] = []
        record_blobs: list[bytes] = []
        for rec in self._records:
            record_offsets.append(cursor)
            blob = struct.pack(
                "<2i3I", rec.x, rec.y, rec.width, rec.height, len(rec.payload)
            ) + rec.payload
            record_blobs.append(blob)
            cursor += len(blob)

        sector_offsets: list[int] = []
        sector_blobs: list[bytes] = []
        for idx in range(n):
            sector_offsets.append(cursor)
            sblob = self._serialize_sector(idx)
            sector_blobs.append(sblob)
            cursor += len(sblob)

        out = bytearray()
        out.extend(MAGIC)
        out.extend(struct.pack("<II", self.header.width, self.header.height))
        out.extend(struct.pack(f"<{n}I", *sector_offsets))
        out.extend(struct.pack("<I", mask_table_off))
        out.extend(struct.pack("<I", m))
        if m:
            out.extend(struct.pack(f"<{m}I", *record_offsets))
        for rblob in record_blobs:
            out.extend(rblob)
        for sblob in sector_blobs:
            out.extend(sblob)
        return bytes(out)

    def save(self, dest: Path | str, *, verify: bool = True) -> Path:
        """Atomically write ``0.1M`` bytes to ``dest`` and verify by re-opening."""
        target = Path(dest)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Materialize full output bytes BEFORE touching target so even an in-place
        # save onto self.path never races self._fh!
        raw_out = self.to_bytes()
        in_place = False
        try:
            in_place = target.exists() and os.path.samefile(target, self.path)
        except OSError:
            in_place = False

        if in_place:
            self.close()

        fd, tmp_name = tempfile.mkstemp(
            dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "wb") as out_fh:
                out_fh.write(raw_out)
                out_fh.flush()
                os.fsync(out_fh.fileno())
            if verify:
                with open_map(Path(tmp_name)) as check_doc:
                    if (
                        check_doc.header.width != self.header.width
                        or check_doc.header.height != self.header.height
                        or check_doc.header.sector_count != self.header.sector_count
                        or len(check_doc.records) != len(self._records)
                        or check_doc.trailing_bytes != 0
                    ):
                        raise MapFormatError(
                            f"post-write verification failed for {target}"
                        )
                    for sector in check_doc.iter_sectors():
                        _ = check_doc.read_cells(sector)
                        decode_sector_image(
                            check_doc.read_image_payload(sector),
                            sector.segment_lengths,
                        )
            os.replace(tmp_name, target)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            if in_place and self.path.exists():
                self._fh = self.path.open("rb")
            raise

        if in_place:
            self.path = target
            self._fh = self.path.open("rb")
            self._fh.seek(0, 2)
            length = self._fh.tell()
            self.header = read_header(self._fh, length)
            self._records = list(read_prefix_records(self._fh, self.header))
            self._sectors.clear()
            self._cell_overrides.clear()
            self._image_overrides.clear()
            self._girb_overrides.clear()
            self._ref_overrides.clear()
            self._collision.clear()
            self._nibbles.clear()
            self._decoded_masks.clear()
        self.dirty = False
        return target

    def summary(self) -> dict:
        h = self.header
        return {
            "path": str(self.path),
            "file_length": h.file_length,
            "trailing_bytes": self.trailing_bytes,
            "width": h.width,
            "height": h.height,
            "sector_count": h.sector_count,
            "sector_grid": f"{h.sector_columns}x{h.sector_rows}",
            "logical_grid_cells": f"{h.grid_columns}x{h.grid_rows}",
            "prefix_records": len(self._records),
            "dirty": self.dirty,
        }


def build_new_map_bytes(
    width: int,
    height: int,
    *,
    image: Image.Image | RgbImage | None = None,
    bg_color: tuple[int, int, int] = (28, 36, 44),
    default_cell: int = 0,
    default_light: int = NEUTRAL_NIBBLE,
    quality: int = 92,
) -> bytes:
    """Create a brand-new, complete ``0.1M`` ``.map`` binary stream from scratch
    (either solid canvas ``bg_color`` or sliced from ``image``)."""
    if not (32 <= width <= 100_000 and 32 <= height <= 100_000):
        raise MapFormatError(f"invalid new map size {width}x{height}")
    if image is None:
        base_img = Image.new("RGB", (width, height), bg_color)
    elif isinstance(image, RgbImage):
        base_img = image.to_pil()
    else:
        base_img = image.convert("RGB")
    if base_img.size != (width, height):
        base_img = base_img.resize((width, height), Image.LANCZOS)

    _, _, encoded_sectors = slice_image_to_sectors(base_img, quality=quality)
    n = len(encoded_sectors)
    girb_body = default_girb_body(default_light)
    llec_body = bytes([default_cell & 0xFF]) * CELLS_PER_SECTOR
    mask_table_off = 12 + 4 * n + 4
    cursor = mask_table_off + 4

    sector_offsets: list[int] = []
    sector_blobs: list[bytes] = []
    for seg_lens, payload in encoded_sectors:
        sector_offsets.append(cursor)
        gepj_body = pack_gepj_block_body(seg_lens, payload)
        sblob = (
            struct.pack("<I", 0)
            + GEPJ_TAG
            + struct.pack("<I", len(gepj_body))
            + gepj_body
            + LLEC_TAG
            + struct.pack("<I", CELLS_PER_SECTOR)
            + llec_body
            + GIRB_TAG
            + struct.pack("<I", len(girb_body))
            + girb_body
            + DEFAULT_GIRB_TRAILER
        )
        sector_blobs.append(sblob)
        cursor += len(sblob)

    out = bytearray()
    out.extend(MAGIC)
    out.extend(struct.pack("<II", width, height))
    out.extend(struct.pack(f"<{n}I", *sector_offsets))
    out.extend(struct.pack("<I", mask_table_off))
    out.extend(struct.pack("<I", 0))
    for sblob in sector_blobs:
        out.extend(sblob)
    return bytes(out)


def create_map_file(
    dest: Path | str,
    width: int,
    height: int,
    *,
    image: Image.Image | RgbImage | Path | str | None = None,
    bg_color: tuple[int, int, int] = (28, 36, 44),
    default_cell: int = 0,
    default_light: int = NEUTRAL_NIBBLE,
    quality: int = 92,
) -> Path:
    """Create, write, and verify a new ``.map`` file on disk."""
    target = Path(dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(image, (Path, str)):
        with Image.open(image) as im:
            raw = build_new_map_bytes(
                width,
                height,
                image=im.convert("RGB"),
                bg_color=bg_color,
                default_cell=default_cell,
                default_light=default_light,
                quality=quality,
            )
    else:
        raw = build_new_map_bytes(
            width,
            height,
            image=image,
            bg_color=bg_color,
            default_cell=default_cell,
            default_light=default_light,
            quality=quality,
        )
    fd, tmp_name = tempfile.mkstemp(
        dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as out_fh:
            out_fh.write(raw)
            out_fh.flush()
            os.fsync(out_fh.fileno())
        with open_map(Path(tmp_name)) as check_doc:
            if (check_doc.header.width, check_doc.header.height) != (width, height):
                raise MapFormatError(
                    f"new map verification failed for {target}: dimensions differ"
                )
            for sector in check_doc.iter_sectors():
                _ = check_doc.read_cells(sector)
                decode_sector_image(
                    check_doc.read_image_payload(sector), sector.segment_lengths
                )
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return target


def open_map(path: Path | str) -> MapDocument:
    return MapDocument(Path(path))
