"""``.blk`` / ``_second.blk`` walkability grid codec & coordinate transforms.

Ground-truth binary analysis of ``mx.exe`` (``LoadBlk`` ``0x484de0``,
``LoadSecondLayer`` ``0x4854d5``, coordinate transforms ``0x487700..0x48838e``)
and ``data/script.fls`` entry ``2717`` (``maptools.ReadBlk``) proves:

1. Logical cell size is ``20x20`` pixels:
   ``W_cells = (width_px + 19) // 20``, ``H_cells = (height_px + 19) // 20``.
2. In-bounds ``LLEC`` bytes in all ``101`` client maps (``2,256,779`` cells) are
   strictly ``{0, 1, 2, 3}``:
   * bit ``0`` (``cell & 1``): ``0`` = walkable floor (``0x7575`` in ``CAStar``),
     ``1`` = blocked obstacle (``0xFFFF`` in ``CAStar``);
   * bit ``1`` (``cell & 2``): ``0`` = normal lighting, ``2`` = shaded cell
     (character sprites draw semi-transparent/tinted even outside explicit foreground
     ``PrefixRecord`` masks).
3. ``.blk`` file binary layout: ``<HH`` ``(W_cells, H_cells)`` followed by
   ``W_cells * H_cells`` bytes stored in **server bottom-up row order**
   (``cy_client = H_cells - 1 - sy_server``).
4. Exact coordinate conversions matching ``mx.exe``:
   * ``ServerPos (sx, sy) <-> ClientPos (px, py)``:
     ``px = sx * 20 + 10``, ``py = (H_cells - sy) * 20 - 10``;
     inverse ``sx = px // 20``, ``sy = H_cells - (py // 20) - 1``.
   * ``ServerPixelPos (x, y) <-> ClientPos (x, H_cells * 20 - y - 1)``.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mapfile import MapDocument

CELL_PX = 20
CELL_WALKABLE = 0          # walkable, normal
CELL_BLOCKED = 1           # obstacle, normal
CELL_SHADED_WALKABLE = 2   # walkable, shaded/masked sprite state
CELL_SHADED_BLOCKED = 3    # obstacle, shaded/masked sprite state

ASTAR_COST_WALKABLE = 0x7575
ASTAR_COST_BLOCKED = 0xFFFF

CELL_LABELS = {
    CELL_WALKABLE: "可通行 (0)",
    CELL_BLOCKED: "阻挡障碍 (1)",
    CELL_SHADED_WALKABLE: "阴影可走 (2)",
    CELL_SHADED_BLOCKED: "阴影阻挡 (3)",
}


class BlkError(ValueError):
    """Raised when a ``.blk`` payload or grid has invalid dimensions or bytes."""


def is_walkable(cell_value: int | None) -> bool:
    """True when ``cell_value`` permits movement in ``CAStar`` (``(v & 1) == 0``)."""
    if cell_value is None:
        return False
    return (cell_value & 1) == 0


def is_shaded(cell_value: int | None) -> bool:
    """True when ``cell_value`` sets the cell-level shade flag (``(v & 2) != 0``)."""
    if cell_value is None:
        return False
    return (cell_value & 2) != 0


def grid_dimensions(width_px: int, height_px: int) -> tuple[int, int]:
    """Return ``(W_cells, H_cells)`` matching ``mx.exe`` ``(dim + 19) // 20``."""
    return (width_px + CELL_PX - 1) // CELL_PX, (height_px + CELL_PX - 1) // CELL_PX


def server_cell_to_client_px(
    sx: int, sy: int, width_px: int, height_px: int
) -> tuple[int, int]:
    """Exact port of ``mx.exe`` ``ServerPos2ClientPos`` (``0x487700``)."""
    _, h_cells = grid_dimensions(width_px, height_px)
    return sx * CELL_PX + 10, (h_cells - sy) * CELL_PX - 10


def client_px_to_server_cell(
    px: int, py: int, width_px: int, height_px: int
) -> tuple[int, int]:
    """Exact port of ``mx.exe`` ``ClientPos2ServerPos`` (``0x487780``)."""
    _, h_cells = grid_dimensions(width_px, height_px)
    return px // CELL_PX, h_cells - (py // CELL_PX) - 1


def client_cell_to_server_cell(cx: int, cy: int, h_cells: int) -> tuple[int, int]:
    return cx, h_cells - 1 - cy


def server_cell_to_client_cell(sx: int, sy: int, h_cells: int) -> tuple[int, int]:
    return sx, h_cells - 1 - sy


def server_pixel_to_client_px(
    x: int, y: int, width_px: int, height_px: int
) -> tuple[int, int]:
    """Exact port of ``mx.exe`` ``ServerPixelPos <-> ClientPos`` (``0x488200``)."""
    _, h_cells = grid_dimensions(width_px, height_px)
    return x, h_cells * CELL_PX - y - 1


@dataclass(slots=True)
class BlkGrid:
    """Server/client ``.blk`` walkability grid in server ``(sx, sy)`` coordinates.

    Row ``sy == 0`` is the **bottom** cell row of the map (``cy_client == height - 1``),
    matching ``maptools.ReadBlk`` and ``mx.exe`` ``CMap::LoadBlk``.
    """

    width: int
    height: int
    cells: bytearray

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise BlkError(f"invalid .blk dimensions {self.width}x{self.height}")
        if len(self.cells) != self.width * self.height:
            raise BlkError(
                f".blk cell length {len(self.cells)} != {self.width}*{self.height}"
            )

    def at_server(self, sx: int, sy: int) -> int:
        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise IndexError(f"server cell ({sx}, {sy}) out of bounds")
        return self.cells[sy * self.width + sx]

    def set_server(self, sx: int, sy: int, value: int) -> None:
        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise IndexError(f"server cell ({sx}, {sy}) out of bounds")
        self.cells[sy * self.width + sx] = value & 0xFF

    def at_client(self, cx: int, cy: int) -> int:
        sy = self.height - 1 - cy
        return self.at_server(cx, sy)

    def set_client(self, cx: int, cy: int, value: int) -> None:
        sy = self.height - 1 - cy
        self.set_server(cx, sy, value)

    def to_bytes(self) -> bytes:
        return struct.pack("<HH", self.width, self.height) + bytes(self.cells)

    @classmethod
    def from_bytes(cls, data: bytes) -> BlkGrid:
        if len(data) < 4:
            raise BlkError(f".blk data too short ({len(data)} bytes)")
        w, h = struct.unpack_from("<HH", data, 0)
        if w <= 0 or h <= 0 or len(data) != 4 + w * h:
            raise BlkError(
                f".blk size mismatch: header declares {w}x{h} "
                f"({4 + w * h} bytes), got {len(data)} bytes"
            )
        return cls(w, h, bytearray(data[4:]))


def read_blk(source: Path | str | bytes) -> BlkGrid:
    data = source if isinstance(source, bytes) else Path(source).read_bytes()
    return BlkGrid.from_bytes(data)


def write_blk(grid: BlkGrid, dest: Path | str | None = None) -> bytes:
    raw = grid.to_bytes()
    if dest is not None:
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
    return raw


def extract_blk_from_map(doc: MapDocument) -> BlkGrid:
    """Extract an in-bounds :class:`BlkGrid` from ``doc``'s ``LLEC`` sectors."""
    w_cells = doc.header.grid_columns
    h_cells = doc.header.grid_rows
    buf = bytearray(w_cells * h_cells)
    for cy in range(h_cells):
        sy = h_cells - 1 - cy
        row_off = sy * w_cells
        for cx in range(w_cells):
            val = doc.cell_at_index(cx, cy)
            buf[row_off + cx] = 1 if val is None else val
    return BlkGrid(w_cells, h_cells, buf)


def apply_blk_to_map(doc: MapDocument, grid: BlkGrid) -> None:
    """Synchronize a :class:`BlkGrid` back into ``doc``'s ``LLEC`` cells."""
    w_cells = doc.header.grid_columns
    h_cells = doc.header.grid_rows
    if (grid.width, grid.height) != (w_cells, h_cells):
        raise BlkError(
            f".blk grid {grid.width}x{grid.height} does not match map grid "
            f"{w_cells}x{h_cells}"
        )
    for cy in range(h_cells):
        for cx in range(w_cells):
            doc.set_cell(cx, cy, grid.at_client(cx, cy))


__all__ = [
    "ASTAR_COST_BLOCKED",
    "ASTAR_COST_WALKABLE",
    "BlkError",
    "BlkGrid",
    "CELL_BLOCKED",
    "CELL_LABELS",
    "CELL_PX",
    "CELL_SHADED_BLOCKED",
    "CELL_SHADED_WALKABLE",
    "CELL_WALKABLE",
    "apply_blk_to_map",
    "client_cell_to_server_cell",
    "client_px_to_server_cell",
    "extract_blk_from_map",
    "grid_dimensions",
    "is_shaded",
    "is_walkable",
    "read_blk",
    "server_cell_to_client_cell",
    "server_cell_to_client_px",
    "server_pixel_to_client_px",
    "write_blk",
]
