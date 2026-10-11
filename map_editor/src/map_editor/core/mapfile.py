"""Map file format engine for MXSJ ``.map`` (``0.1M``) files.

Design constraints that came from measured facts, not assumptions:

* The sector count is **not** stored explicitly.  The header holds ``N`` absolute
  file offsets starting at byte 12, and the u32 at ``12 + 4*N`` contains its own
  address plus 4 (a self-referential pointer).  Scanning for that sentinel yields
  ``N`` without hardcoding it.  Verified on all five sample maps (N=49 each).
* Sector layout is ``ceil(width / 320) x ceil(height / 240)``.  The five samples
  are 2000x1500 -> 7x7=49, which matches.  The client scene table contains 24
  different sizes up to 10000x6000 -> 32x25=800 sectors, so nothing here may
  assume 49 or 7x7.
* Sector length identity: ``246 + 4*refs + image_length``.
* The ``GIRB`` trailer was byte-identical in 245/245 sectors of the samples; it
  is round-tripped verbatim rather than interpreted.

Pure standard library, no Qt import, so it stays testable headlessly.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

MAGIC = b"0.1M"
SECTOR_PX_W, SECTOR_PX_H = 320, 240
CELL_PX = 20                 # mx.exe 0x4baebf: signed divide by 20
CELL_COLS_PER_SECTOR, CELL_ROWS_PER_SECTOR = 16, 12
CELLS_PER_SECTOR = CELL_COLS_PER_SECTOR * CELL_ROWS_PER_SECTOR   # 192
GEPJ_TAG = b"GEPJ"
LLEC_TAG = b"LLEC"
GIRB_TAG = b"GIRB"
GEPJ_SEGMENTS = 13           # 1 shared header + 12 independent 80x80 scans
PIECE_PX = 80                # each scan is an 80x80 JPEG
MAX_SCAN_SECTORS = 4096      # bound for the sentinel scan


class MapFormatError(ValueError):
    """Raised when a file is not a readable ``0.1M`` map."""


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
    if any(b <= a for a, b in zip(offsets, offsets[1:])):
        raise MapFormatError("sector offset table is not strictly increasing")
    # With no prefix records the first sector starts exactly at 12 + 4N + 8,
    # so this must be a strict inequality.
    if offsets[0] < 12 + 4 * n + 8:
        raise MapFormatError("first sector offset overlaps the header")

    fh.seek(12 + 4 * n + 4)
    (record_count,) = struct.unpack("<I", fh.read(4))
    if record_count > 1_000_000:
        raise MapFormatError(f"implausible prefix-record count {record_count}")
    record_offsets: tuple[int, ...] = ()
    if record_count:
        record_offsets = struct.unpack(f"<{record_count}I", fh.read(4 * record_count))
        if any(b <= a for a, b in zip(record_offsets, record_offsets[1:])):
            raise MapFormatError("prefix-record offset table is not increasing")

    columns, rows = math.ceil(width / SECTOR_PX_W), math.ceil(height / SECTOR_PX_H)
    if columns * rows != n:
        raise MapFormatError(
            f"sector count {n} != ceil({width}/320)*ceil({height}/240)={columns * rows}")

    return MapHeader(
        width=width, height=height, sector_count=n, sector_columns=columns,
        sector_rows=rows, record_count=record_count, sector_offsets=offsets,
        record_offsets=record_offsets, file_length=file_length,
    )


def read_sector(fh: BinaryIO, header: MapHeader, index: int) -> Sector:
    offset = header.sector_offsets[index]
    end = (header.sector_offsets[index + 1] if index + 1 < header.sector_count
           else header.file_length)
    fh.seek(offset)
    (refs,) = struct.unpack("<I", fh.read(4))
    if refs > 1_000_000:
        raise MapFormatError(f"sector {index}: implausible reference count {refs}")
    refs_tuple: tuple[int, ...] = ()
    if refs:
        refs_tuple = struct.unpack(f"<{refs}I", fh.read(4 * refs))

    cursor = offset + 4 + 4 * refs
    fh.seek(cursor)
    if fh.read(4) != GEPJ_TAG:
        raise MapFormatError(f"sector {index}: GEPJ tag missing at {cursor}")
    (image_length,) = struct.unpack("<I", fh.read(4))
    if image_length < GEPJ_SEGMENTS * 2:
        raise MapFormatError(f"sector {index}: image length {image_length} too small")
    segment_lengths = struct.unpack(f"<{GEPJ_SEGMENTS}H", fh.read(2 * GEPJ_SEGMENTS))
    if sum(segment_lengths) != image_length - 2 * GEPJ_SEGMENTS:
        raise MapFormatError(
            f"sector {index}: segment lengths sum to {sum(segment_lengths)}, "
            f"expected {image_length - 2 * GEPJ_SEGMENTS}")
    image_offset = cursor + 8 + 2 * GEPJ_SEGMENTS

    cells_offset = cursor + 8 + image_length
    fh.seek(cells_offset)
    if fh.read(4) != LLEC_TAG:
        raise MapFormatError(f"sector {index}: LLEC tag missing at {cells_offset}")
    (cell_count,) = struct.unpack("<I", fh.read(4))
    if cell_count != CELLS_PER_SECTOR:
        raise MapFormatError(f"sector {index}: LLEC length {cell_count} != 192")

    girb_offset = cells_offset + 8 + cell_count
    fh.seek(girb_offset)
    if fh.read(4) != GIRB_TAG:
        raise MapFormatError(f"sector {index}: GIRB tag missing at {girb_offset}")
    (girb_len,) = struct.unpack("<I", fh.read(4))
    girb_body = fh.read(girb_len)
    girb_trailer = fh.read(4)
    if len(girb_body) != girb_len:
        raise MapFormatError(f"sector {index}: truncated GIRB body")

    expected = 246 + 4 * refs + image_length
    if end - offset != expected:
        raise MapFormatError(
            f"sector {index}: length {end - offset} != 246+4*{refs}+{image_length}={expected}")

    return Sector(
        index=index, row=index // header.sector_columns, col=index % header.sector_columns,
        offset=offset, length=end - offset, record_refs=refs_tuple,
        image_offset=image_offset, image_length=image_length - 2 * GEPJ_SEGMENTS,
        segment_lengths=segment_lengths, cells_offset=cells_offset + 8,
        girb_offset=girb_offset, girb_body=girb_body, girb_trailer=girb_trailer,
    )


def read_prefix_records(fh: BinaryIO, header: MapHeader) -> tuple[PrefixRecord, ...]:
    out: list[PrefixRecord] = []
    for i, off in enumerate(header.record_offsets):
        fh.seek(off)
        x, y, w, h, plen = struct.unpack("<5I", fh.read(20))
        if not 0 <= x and not 0 <= y:
            raise MapFormatError(f"record {i}: negative origin")
        if x + w > header.width or y + h > header.height:
            raise MapFormatError(f"record {i}: rect {x},{y} {w}x{h} outside map")
        payload = fh.read(plen)
        if len(payload) != plen:
            raise MapFormatError(f"record {i}: truncated payload")
        out.append(PrefixRecord(i, off, x, y, w, h, plen, payload))
    return tuple(out)


class MapDocument:
    """Lazy, read-only view of one ``.map`` file.

    Nothing is loaded until asked for, so a 10000x6000 map (800 sectors,
    60 M pixels) costs only a header parse until a tile is requested.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._fh = self.path.open("rb")
        self._fh.seek(0, 2)
        length = self._fh.tell()
        try:
            self.header = read_header(self._fh, length)
            self.records = read_prefix_records(self._fh, self.header)
        except Exception:
            self._fh.close()
            raise
        self._sectors: dict[int, Sector] = {}

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> "MapDocument":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- accessors ---------------------------------------------------------
    @property
    def sector_count(self) -> int:
        return self.header.sector_count

    def sector(self, index: int) -> Sector:
        if not 0 <= index < self.header.sector_count:
            raise IndexError(f"sector index {index} out of range")
        if index not in self._sectors:
            self._sectors[index] = read_sector(self._fh, self.header, index)
        return self._sectors[index]

    def iter_sectors(self) -> "Iterator[Sector]":
        return (self.sector(i) for i in range(self.header.sector_count))

    def read_image_payload(self, sector: Sector) -> bytes:
        self._fh.seek(sector.image_offset)
        data = self._fh.read(sector.image_length)
        if len(data) != sector.image_length:
            raise MapFormatError(f"sector {sector.index}: truncated GEPJ payload")
        return data

    def read_cells(self, sector: Sector) -> bytes:
        self._fh.seek(sector.cells_offset)
        cells = self._fh.read(CELLS_PER_SECTOR)
        if len(cells) != CELLS_PER_SECTOR:
            raise MapFormatError(f"sector {sector.index}: truncated LLEC cells")
        return cells

    def cell_at(self, x: int, y: int) -> int | None:
        """Raw LLEC byte for a pixel coordinate, or None outside the sector grid."""
        cx, cy = x // CELL_PX, y // CELL_PX
        if not 0 <= cx < self.header.grid_columns or not 0 <= cy < self.header.grid_rows:
            return None
        sc, sr = cx // CELL_COLS_PER_SECTOR, cy // CELL_ROWS_PER_SECTOR
        index = sr * self.header.sector_columns + sc
        if index >= self.header.sector_count:
            return None
        cells = self.read_cells(self.sector(index))
        return cells[(cy % CELL_ROWS_PER_SECTOR) * CELL_COLS_PER_SECTOR + cx % CELL_COLS_PER_SECTOR]

    def summary(self) -> dict:
        h = self.header
        return {
            "path": str(self.path),
            "file_length": h.file_length,
            "width": h.width,
            "height": h.height,
            "sector_count": h.sector_count,
            "sector_grid": f"{h.sector_columns}x{h.sector_rows}",
            "logical_grid_cells": f"{h.grid_columns}x{h.grid_rows}",
            "prefix_records": h.record_count,
        }


def open_map(path: Path | str) -> MapDocument:
    return MapDocument(Path(path))
