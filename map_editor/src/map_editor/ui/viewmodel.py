"""Editor view model — all editor state and actions, with **no Qt dependency**.

Splitting this out of the widgets is deliberate.  The Qt layer in
``widgets.py`` is a thin binding; every decision (which maps exist, what a row
shows, which region to render, what an export contains) lives here and is
covered by ``tests/test_viewmodel.py``, which runs headless.  That keeps the
risky logic verifiable on machines that cannot import ``QtWidgets`` at all.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from ..client.config import Config
from ..client.discovery import ClientLayout, DiscoveryError, discover
from ..client.scene_table import SceneTable
from ..core import MapDocument, MapFormatError, open_map, render_region
from ..core.mapfile import CELL_PX

LAYERS = ("texture", "grid", "records", "sector_bounds", "collision", "collision_grid")
Progress = Callable[[str], None]


@dataclass(slots=True)
class MapRow:
    """One row of the map list."""
    key: str
    name: str
    width: int
    height: int
    sectors: int
    size: int
    path: Path
    error: str = ""

    @property
    def label(self) -> str:
        return f"{self.key}  {self.name}" if self.name else self.key

    @property
    def broken(self) -> bool:
        return bool(self.error)


@dataclass(slots=True)
class EditorState:
    client_root: str = ""
    status: str = "未选择客户端目录"
    scanned_files: int = 0
    map_count: int = 0
    current_key: str = ""
    current_name: str = ""
    current_size: tuple[int, int] = (0, 0)
    current_sectors: int = 0
    current_records: int = 0
    cursor: tuple[int, int] | None = None
    layers: dict[str, bool] = field(default_factory=lambda: {n: True for n in LAYERS})
    errors: list[str] = field(default_factory=list)


class EditorViewModel:
    """Owns the model side of the editor."""

    def __init__(self, config: Config | None = None,
                 scene_table: SceneTable | None = None) -> None:
        self.config = config if config is not None else Config.load()
        self.scenes = scene_table if scene_table is not None else SceneTable.load(
            self.config.scene_table or None)
        self.layout: ClientLayout | None = None
        self.state = EditorState(layers={
            "texture": self.config.show_texture,
            "grid": self.config.show_grid,
            "records": self.config.show_records,
            "sector_bounds": self.config.show_sector_bounds,
            "collision": self.config.show_collision,
            "collision_grid": self.config.show_collision_grid,
        })
        self._doc: MapDocument | None = None
        self._rows: list[MapRow] = []

    # -- client root ------------------------------------------------------
    def set_client_root(self, root: str | Path, progress: Progress | None = None) -> None:
        """Scan a client directory.  Raises :class:`DiscoveryError` if unusable."""
        def cb(count: int, _path: Path) -> None:
            if progress:
                progress(f"已扫描 {count} 个文件…")

        layout = discover(root, progress=cb)
        self.layout = layout
        self.config.remember_root(layout.root)
        self.state.client_root = str(layout.root)
        self.state.scanned_files = layout.scanned_files
        self.state.map_count = len(layout.maps)
        self._rows = []
        self.state.errors = []
        if progress:
            progress(f"发现 {len(layout.maps)} 张地图")

    @property
    def rows(self) -> list[MapRow]:
        """Map list rows, lazily reading each header for real dimensions."""
        if self._rows or self.layout is None:
            return self._rows
        rows: list[MapRow] = []
        for m in self.layout.maps:
            meta = self.scenes.get(m.scene_key)
            name = meta.name if meta else ""
            try:
                with open_map(m.path) as doc:
                    h = doc.header
                    rows.append(MapRow(m.scene_key, name, h.width, h.height,
                                       h.sector_count, m.size, m.path))
            except (MapFormatError, OSError) as exc:
                rows.append(MapRow(m.scene_key, name, 0, 0, 0, m.size, m.path, str(exc)))
                self.state.errors.append(f"{m.path.name}: {exc}")
        self._rows = rows
        return rows

    def row(self, key: str) -> MapRow | None:
        for r in self.rows:
            if r.key == key:
                return r
        return None

    # -- open / close -----------------------------------------------------
    @property
    def document(self) -> MapDocument | None:
        return self._doc

    def open_map(self, key: str | MapRow) -> MapDocument:
        row = key if isinstance(key, MapRow) else self.row(str(key))
        if row is None:
            raise KeyError(f"unknown map key: {key}")
        if row.broken:
            raise MapFormatError(f"{row.path.name}: {row.error}")
        self.close_map()
        self._doc = open_map(row.path)
        h = self._doc.header
        self.state.current_key = row.key
        self.state.current_name = row.name or f"场景 {row.key}"
        self.state.current_size = (h.width, h.height)
        self.state.current_sectors = h.sector_count
        self.state.current_records = h.record_count
        self.state.cursor = None
        return self._doc

    def close_map(self) -> None:
        if self._doc is not None:
            self._doc.close()
            self._doc = None
        self.state.current_key = ""
        self.state.current_name = ""
        self.state.current_size = (0, 0)
        self.state.current_sectors = 0
        self.state.current_records = 0
        self.state.cursor = None

    # -- layers -----------------------------------------------------------
    def set_layer(self, name: str, on: bool) -> None:
        if name not in LAYERS:
            raise KeyError(f"unknown layer {name!r}; expected one of {LAYERS}")
        self.state.layers[name] = on
        setattr(self.config, f"show_{name}", on)

    def layer(self, name: str) -> bool:
        return self.state.layers.get(name, False)

    # -- coordinate handling ---------------------------------------------
    def locate(self, x: int, y: int) -> dict:
        """Translate a pixel coordinate into map/cell/sector facts."""
        doc = self._require_doc()
        h = doc.header
        inside = 0 <= x < h.width and 0 <= y < h.height
        info = {
            "x": x, "y": y, "inside": inside,
            "cell": (x // CELL_PX, y // CELL_PX),
            "cell_value": doc.cell_at(x, y) if inside else None,
        }
        if inside:
            cx, cy = x // CELL_PX, y // CELL_PX
            sc, sr = cx // 16, cy // 12
            info["sector"] = sr * h.sector_columns + sc
            info["sector_cell"] = (sc, sr)
        self.state.cursor = (x, y)
        return info

    # -- rendering --------------------------------------------------------
    # -- collision (GIRB) -------------------------------------------------
    def collision_region(self, x0: int, y0: int, x1: int, y1: int) -> dict:
        """Collision-grid cells covering a pixel region.

        Returns row-major values plus geometry, with ``None`` for cells whose
        sector could not be inflated.  Pure data, so the Qt layer only paints.
        """
        from ..core.girb import CELL_PX, GRID_COLS, GRID_ROWS
        doc = self._require_doc()
        h = doc.header
        cx0, cy0 = x0 // CELL_PX, y0 // CELL_PX
        cx1 = min(-(-(x1) // CELL_PX), h.sector_columns * GRID_COLS)
        cy1 = min(-(-(y1) // CELL_PX), h.sector_rows * GRID_ROWS)
        cx0, cy0 = max(0, cx0), max(0, cy0)
        if cx1 <= cx0 or cy1 <= cy0:
            return {"cols": 0, "rows": 0, "cell_px": CELL_PX, "values": [],
                    "decoded": 0, "failed": 0}
        values: list[int | None] = []
        decoded = failed = 0
        touched: set[int] = set()
        for cy in range(cy0, cy1):
            for cx in range(cx0, cx1):
                sc, sr = cx // GRID_COLS, cy // GRID_ROWS
                index = sr * h.sector_columns + sc
                if index >= h.sector_count:
                    values.append(None)
                    continue
                vals = doc.collision_cells(doc.sector(index))
                if index not in touched:
                    touched.add(index)
                    if vals is None:
                        failed += 1
                    else:
                        decoded += 1
                values.append(None if vals is None
                              else vals[(cy % GRID_ROWS) * GRID_COLS + (cx % GRID_COLS)])
        return {"origin_cell": (cx0, cy0), "cols": cx1 - cx0, "rows": cy1 - cy0,
                "cell_px": CELL_PX, "values": values,
                "decoded": decoded, "failed": failed}

    def collision_stats(self) -> dict:
        return self._require_doc().collision_stats()

    def girb_report(self) -> list[dict]:
        """Per-map GIRB decode report — what to send back when a map misbehaves."""
        out: list[dict] = []
        for r in self.rows:
            if r.broken:
                out.append({"key": r.key, "name": r.name, "error": r.error})
                continue
            try:
                self.open_map(r)
                st = self.collision_stats()
                lengths = sorted({len(s.girb_body) for s in self._require_doc().iter_sectors()})
                st.update({"key": r.key, "name": r.name,
                           "size": f"{r.width}x{r.height}",
                           "girb_len_min": lengths[0], "girb_len_max": lengths[-1]})
                out.append(st)
                self.close_map()
            except Exception as exc:
                out.append({"key": r.key, "name": r.name, "error": str(exc)})
                self.close_map()
        return out

    def render(self, x0: int, y0: int, x1: int, y1: int):
        doc = self._require_doc()
        return render_region(doc, x0, y0, x1, y1)

    # -- export -----------------------------------------------------------
    def export_json(self, dest: str | Path, *, include_cells: bool = False) -> Path:
        doc = self._require_doc()
        h = doc.header
        payload: dict = {
            "format": "map-editor/export",
            "version": 1,
            "source": str(doc.path),
            "client_root": self.state.client_root,
            "scene_key": self.state.current_key,
            "scene_name": self.state.current_name,
            "width": h.width,
            "height": h.height,
            "sector_count": h.sector_count,
            "sector_grid": [h.sector_columns, h.sector_rows],
            "logical_grid_cells": [h.grid_columns, h.grid_rows],
            "cell_px": CELL_PX,
            "sectors": [
                {
                    "index": s.index, "row": s.row, "col": s.col,
                    "origin": [s.origin_x, s.origin_y],
                    "record_refs": list(s.record_refs),
                    "image_bytes": s.image_length,
                    "segment_lengths": list(s.segment_lengths),
                    "girb_sha256": _sha(s.girb_body + s.girb_trailer),
                    "extra_blocks": [
                        {"tag": b.tag, "offset": b.offset, "length": b.length}
                        for b in s.extra_blocks
                    ],
                }
                for s in doc.iter_sectors()
            ],
            "collision": doc.collision_stats(),
            "prefix_records": [
                {"index": r.index, "x": r.x, "y": r.y, "w": r.width, "h": r.height,
                 "payload_length": r.payload_length,
                 "payload_head": r.payload[:32].hex()}
                for r in doc.records
            ],
        }
        if include_cells:
            payload["cells"] = [
                {"sector": s.index, "values": list(doc.read_cells(s))}
                for s in doc.iter_sectors()
            ]
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        return p

    def export_png(self, dest: str | Path, region: tuple[int, int, int, int] | None = None) -> Path:
        """Write a PNG.  Pillow writes the file, so no external tool is needed."""
        from PIL import Image
        doc = self._require_doc()
        box = region or (0, 0, doc.header.width, doc.header.height)
        img = render_region(doc, *box)
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("RGB", (img.width, img.height), img.data).save(p)
        return p

    # -- status -----------------------------------------------------------
    def status_line(self) -> str:
        s = self.state
        if not s.client_root:
            return s.status
        head = f"{s.map_count} 张地图 · 扫描 {s.scanned_files} 个文件"
        if s.current_key:
            head += (f" · 当前 {s.current_key} {s.current_name} "
                     f"{s.current_size[0]}x{s.current_size[1]} "
                     f"({s.current_sectors} 扇区 / {s.current_records} 记录)")
        if s.cursor:
            head += f" · 光标 {s.cursor[0]},{s.cursor[1]}"
        return head

    def save_config(self) -> Path:
        return self.config.save()

    # -- internals --------------------------------------------------------
    def _require_doc(self) -> MapDocument:
        if self._doc is None:
            raise RuntimeError("no map is open")
        return self._doc


def _sha(blob: bytes) -> str:
    import hashlib
    return hashlib.sha256(blob).hexdigest()[:16]


__all__ = ["EditorState", "EditorViewModel", "LAYERS", "MapRow", "DiscoveryError",
           "Iterable"]
