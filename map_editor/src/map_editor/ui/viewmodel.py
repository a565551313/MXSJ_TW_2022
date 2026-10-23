"""Editor view model — all editor state, editing commands, undo/redo, pathfinding,
and export/save safety guards, with **zero Qt dependencies**.

Every state transition, tool stroke, mask edit, tile replacement, ``.blk`` sync,
A* path simulation, and strict/loose save check lives here so headless tests
exercise 100% of real editor behavior without importing ``PySide6``.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from ..client.config import Config
from ..client.discovery import ClientLayout, DiscoveryError, discover
from ..client.scene_table import SceneMeta, SceneTable
from ..core import (
    BlkGrid,
    MapDocument,
    MapFormatError,
    PathResult,
    RgbImage,
    analyze_walkability,
    apply_blk_to_map,
    client_px_to_server_cell,
    compute_sector_record_refs,
    create_map_file,
    extract_blk_from_map,
    find_path,
    is_shaded,
    is_walkable,
    open_map,
    read_blk,
    render_region,
    server_cell_to_client_px,
    write_blk,
)
from ..core.girb import LIGHT_CELL_PX, NEUTRAL_NIBBLE
from ..core.mapfile import CELL_PX, SECTOR_PX_H, SECTOR_PX_W

LAYERS = (
    "texture",
    "lit_preview",
    "walkability",
    "grid",
    "records",
    "mask_cutout",
    "sector_bounds",
    "collision",
    "collision_grid",
    "entities",
    "path",
)

TOOLS = (
    "pan",
    "cell_brush",
    "cell_rect",
    "cell_line",
    "cell_fill",
    "light_brush",
    "path_sim",
    "mask_select",
)

MAX_UNDO_STEPS = 100
Progress = Callable[[str], None]


class ExportBlockedError(RuntimeError):
    """Raised when a save or export target would overwrite a protected client
    source file under strict protection mode."""


def _normalized_path(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path.absolute()
    return os.path.normcase(str(resolved))


def _same_file_or_path(a: Path, b: Path) -> bool:
    try:
        if a.exists() and b.exists():
            return os.path.samefile(a, b)
    except OSError:
        pass
    return _normalized_path(a) == _normalized_path(b)


@dataclass(slots=True)
class UndoCommand:
    label: str
    undo: Callable[[], None]
    redo: Callable[[], None]
    before_token: int = 0
    after_token: int = 0


@dataclass(slots=True)
class MapRow:
    """One row of the discovered map table."""

    key: str
    name: str
    width: int
    height: int
    sectors: int
    size: int
    path: Path
    records: int = 0
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
    active_tool: str = "pan"
    brush_cell_value: int = 1
    brush_radius: int = 0
    light_value: int = 12
    light_radius: int = 3
    selected_record: int | None = None
    path_start: tuple[int, int] | None = None
    path_goal: tuple[int, int] | None = None
    last_path: PathResult | None = None
    layers: dict[str, bool] = field(default_factory=lambda: {n: True for n in LAYERS})
    errors: list[str] = field(default_factory=list)


class EditorViewModel:
    """Owns all model state, editing actions, undo/redo, and export/save guards."""

    def __init__(
        self,
        config: Config | None = None,
        scene_table: SceneTable | None = None,
    ) -> None:
        self.config = config if config is not None else Config.load()
        self.scenes = (
            scene_table
            if scene_table is not None
            else SceneTable.load(self.config.scene_table or None)
        )
        self.layout: ClientLayout | None = None
        self.state = EditorState(
            layers={n: bool(getattr(self.config, f"show_{n}", False)) for n in LAYERS}
        )
        self._doc: MapDocument | None = None
        self._rows: list[MapRow] = []
        self._undo_stack: list[UndoCommand] = []
        self._redo_stack: list[UndoCommand] = []
        self._state_token = 0
        self._next_state_token = 1
        self._saved_state_token = 0

    # -- client root discovery --------------------------------------------
    def set_client_root(
        self, root: str | Path, progress: Progress | None = None
    ) -> None:
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
                    rows.append(
                        MapRow(
                            m.scene_key,
                            name,
                            h.width,
                            h.height,
                            h.sector_count,
                            m.size,
                            m.path,
                            records=h.record_count,
                        )
                    )
            except (MapFormatError, OSError) as exc:
                rows.append(
                    MapRow(m.scene_key, name, 0, 0, 0, m.size, m.path, 0, str(exc))
                )
                self.state.errors.append(f"{m.path.name}: {exc}")
        self._rows = rows
        return rows

    def row(self, key: str) -> MapRow | None:
        for r in self.rows:
            if r.key == key:
                return r
        return None

    # -- open / create / close --------------------------------------------
    @property
    def document(self) -> MapDocument | None:
        return self._doc

    def _activate_doc(self, doc: MapDocument, key: str, name: str) -> MapDocument:
        self._doc = doc
        h = doc.header
        self.state.current_key = key
        self.state.current_name = name or f"场景 {key}"
        self.state.current_size = (h.width, h.height)
        self.state.current_sectors = h.sector_count
        self.state.current_records = len(doc.records)
        self.state.cursor = None
        self.state.selected_record = 0 if doc.records else None
        self.state.path_start = None
        self.state.path_goal = None
        self.state.last_path = None
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._state_token = 0
        self._next_state_token = 1
        self._saved_state_token = 0
        return doc

    def open_map(self, key: str | MapRow) -> MapDocument:
        row = key if isinstance(key, MapRow) else self.row(str(key))
        if row is None:
            raise KeyError(f"unknown map key: {key}")
        if row.broken:
            raise MapFormatError(f"{row.path.name}: {row.error}")
        self.close_map()
        doc = open_map(row.path)
        return self._activate_doc(doc, row.key, row.name)

    def open_map_file(self, path: str | Path) -> MapDocument:
        """Open any standalone ``.map`` file directly from disk."""
        p = Path(path)
        self.close_map()
        doc = open_map(p)
        meta = self.scenes.get(p.stem)
        return self._activate_doc(doc, p.stem, meta.name if meta else "")

    def create_new_map(
        self,
        dest: str | Path,
        width: int,
        height: int,
        *,
        image: Image.Image | RgbImage | Path | str | None = None,
        bg_color: tuple[int, int, int] = (28, 36, 44),
        default_cell: int = 0,
        default_light: int = NEUTRAL_NIBBLE,
        quality: int = 92,
    ) -> MapDocument:
        target = self._guard_export_target(dest)
        created = create_map_file(
            target,
            width,
            height,
            image=image,
            bg_color=bg_color,
            default_cell=default_cell,
            default_light=default_light,
            quality=quality,
        )
        return self.open_map_file(created)

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
        self.state.selected_record = None
        self.state.path_start = None
        self.state.path_goal = None
        self.state.last_path = None
        self._undo_stack.clear()
        self._redo_stack.clear()

    # -- undo / redo engine -----------------------------------------------
    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def dirty(self) -> bool:
        return bool(
            self._doc
            and (self._doc.dirty or self._state_token != self._saved_state_token)
        )

    def _push_command(self, cmd: UndoCommand) -> None:
        cmd.before_token = self._state_token
        cmd.after_token = self._next_state_token
        self._next_state_token += 1
        self._state_token = cmd.after_token
        self._undo_stack.append(cmd)
        if len(self._undo_stack) > MAX_UNDO_STEPS:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        if self._doc is not None:
            self.state.current_records = len(self._doc.records)

    def undo(self) -> str | None:
        if not self._undo_stack:
            return None
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._state_token = cmd.before_token
        self._redo_stack.append(cmd)
        if self._doc is not None:
            self._doc.dirty = self._state_token != self._saved_state_token
            self.state.current_records = len(self._doc.records)
        return cmd.label

    def redo(self) -> str | None:
        if not self._redo_stack:
            return None
        cmd = self._redo_stack.pop()
        cmd.redo()
        self._state_token = cmd.after_token
        self._undo_stack.append(cmd)
        if self._doc is not None:
            self._doc.dirty = self._state_token != self._saved_state_token
            self.state.current_records = len(self._doc.records)
        return cmd.label

    # -- layers & tools ---------------------------------------------------
    def set_layer(self, name: str, on: bool) -> None:
        if name not in LAYERS:
            raise KeyError(f"unknown layer {name!r}; expected one of {LAYERS}")
        self.state.layers[name] = on
        setattr(self.config, f"show_{name}", on)

    def layer(self, name: str) -> bool:
        return self.state.layers.get(name, False)

    def set_tool(self, tool: str) -> None:
        if tool not in TOOLS:
            raise KeyError(f"unknown tool {tool!r}; expected one of {TOOLS}")
        self.state.active_tool = tool

    # -- coordinate & entity queries --------------------------------------
    def locate(self, x: int, y: int) -> dict:
        """Translate client pixel ``(x, y)`` into full client + server coordinates."""
        doc = self._require_doc()
        h = doc.header
        inside = 0 <= x < h.width and 0 <= y < h.height
        cval = doc.cell_at(x, y) if inside else None
        sx, sy = client_px_to_server_cell(x, y, h.width, h.height)
        info: dict = {
            "x": x,
            "y": y,
            "inside": inside,
            "cell": (x // CELL_PX, y // CELL_PX),
            "server_cell": (sx, sy),
            "cell_value": cval,
            "walkable": is_walkable(cval) if cval is not None else None,
            "shaded": is_shaded(cval) if cval is not None else None,
            "light": doc.lightmap_at(x, y) if inside else None,
        }
        if inside:
            cx, cy = x // CELL_PX, y // CELL_PX
            sc, sr = cx // 16, cy // 12
            info["sector"] = sr * h.sector_columns + sc
            info["sector_cell"] = (sc, sr)
        self.state.cursor = (x, y)
        return info

    def current_meta(self) -> SceneMeta | None:
        if not self.state.current_key:
            return None
        return self.scenes.get(self.state.current_key)

    def current_entities(self) -> dict:
        """Project NPCs, portals, and arrival cell onto client pixel coordinates."""
        doc = self._require_doc()
        meta = self.current_meta()
        if meta is None:
            return {"npcs": [], "portals": [], "arrival": None}
        w, h = doc.header.width, doc.header.height
        npcs = []
        for n in meta.npcs:
            px, py = server_cell_to_client_px(n.sx, n.sy, w, h)
            cv = doc.cell_at(px, py)
            npcs.append(
                {
                    "npc_id": n.npc_id,
                    "name": n.name,
                    "alias": n.alias,
                    "sx": n.sx,
                    "sy": n.sy,
                    "px": px,
                    "py": py,
                    "cell_value": cv,
                    "walkable": is_walkable(cv),
                }
            )
        portals = []
        for p in meta.portals:
            px, py = server_cell_to_client_px(p.sx, p.sy, w, h)
            portals.append(
                {
                    "name": p.name,
                    "desc": p.desc,
                    "sx": p.sx,
                    "sy": p.sy,
                    "px": px,
                    "py": py,
                    "npc_id": p.npc_id,
                }
            )
        arrival = None
        if meta.arrival_cell is not None:
            ax, ay = server_cell_to_client_px(
                meta.arrival_cell[0], meta.arrival_cell[1], w, h
            )
            arrival = {
                "sx": meta.arrival_cell[0],
                "sy": meta.arrival_cell[1],
                "px": ax,
                "py": ay,
            }
        return {"npcs": npcs, "portals": portals, "arrival": arrival}

    # -- cell / lightmap / mask / tile editing commands -------------------
    def record_cell_changes(
        self, changed: dict[tuple[int, int], int], new_value: int, label: str
    ) -> int:
        """Commit an arbitrary map of ``{(cx, cy): old_value}`` onto the undo stack."""
        if not changed:
            return 0
        doc = self._require_doc()
        snapshot = dict(changed)

        def _do_undo() -> None:
            for (cx, cy), old in snapshot.items():
                doc.set_cell(cx, cy, old)

        def _do_redo() -> None:
            for cx, cy in snapshot:
                doc.set_cell(cx, cy, new_value)

        self._push_command(UndoCommand(label, _do_undo, _do_redo))
        return len(snapshot)

    def paint_cell_brush(
        self, px: int, py: int, value: int | None = None, radius: int | None = None
    ) -> int:
        doc = self._require_doc()
        val = self.state.brush_cell_value if value is None else value
        rad = self.state.brush_radius if radius is None else radius
        changed = doc.paint_cells_brush(px // CELL_PX, py // CELL_PX, val, rad)
        return self.record_cell_changes(changed, val, f"行走画笔 ({len(changed)} 格)")

    def paint_cell_rect(
        self, px0: int, py0: int, px1: int, py1: int, value: int | None = None
    ) -> int:
        doc = self._require_doc()
        val = self.state.brush_cell_value if value is None else value
        changed = doc.paint_cells_rect(
            px0 // CELL_PX, py0 // CELL_PX, px1 // CELL_PX, py1 // CELL_PX, val
        )
        return self.record_cell_changes(changed, val, f"矩形填充 ({len(changed)} 格)")

    def paint_cell_line(
        self,
        px0: int,
        py0: int,
        px1: int,
        py1: int,
        value: int | None = None,
        radius: int | None = None,
    ) -> int:
        doc = self._require_doc()
        val = self.state.brush_cell_value if value is None else value
        rad = self.state.brush_radius if radius is None else radius
        changed = doc.paint_cells_line(
            px0 // CELL_PX,
            py0 // CELL_PX,
            px1 // CELL_PX,
            py1 // CELL_PX,
            val,
            rad,
        )
        return self.record_cell_changes(changed, val, f"直线绘制 ({len(changed)} 格)")

    def flood_fill_cells_at(
        self, px: int, py: int, value: int | None = None
    ) -> int:
        doc = self._require_doc()
        val = self.state.brush_cell_value if value is None else value
        changed = doc.flood_fill_cells(px // CELL_PX, py // CELL_PX, val)
        return self.record_cell_changes(changed, val, f"区域填充 ({len(changed)} 格)")

    def record_light_changes(
        self, changed: dict[tuple[int, int], int], new_nibble: int, label: str
    ) -> int:
        if not changed:
            return 0
        doc = self._require_doc()
        snapshot = dict(changed)

        def _do_undo() -> None:
            for (lx, ly), old in snapshot.items():
                doc.set_lightmap_nibble(lx, ly, old)

        def _do_redo() -> None:
            for lx, ly in snapshot:
                doc.set_lightmap_nibble(lx, ly, new_nibble)

        self._push_command(UndoCommand(label, _do_undo, _do_redo))
        return len(snapshot)

    def paint_lightmap_at(
        self,
        px: int,
        py: int,
        nibble: int | None = None,
        radius: int | None = None,
    ) -> int:
        doc = self._require_doc()
        nib = self.state.light_value if nibble is None else nibble
        rad = self.state.light_radius if radius is None else radius
        changed = doc.paint_lightmap_brush(
            px // LIGHT_CELL_PX, py // LIGHT_CELL_PX, nib, rad
        )
        return self.record_light_changes(
            changed, nib, f"光照画笔 ({len(changed)} 采样)"
        )

    def reset_sector_lightmap_at(
        self, px: int, py: int, nibble: int = NEUTRAL_NIBBLE
    ) -> None:
        doc = self._require_doc()
        sc, sr = px // SECTOR_PX_W, py // SECTOR_PX_H
        if not (
            0 <= sc < doc.header.sector_columns
            and 0 <= sr < doc.header.sector_rows
        ):
            return
        sidx = sr * doc.header.sector_columns + sc
        old_nibs = bytearray(
            doc.lightmap_nibbles(sidx) or ([NEUTRAL_NIBBLE] * 4800)
        )
        doc.reset_sector_lightmap(sidx, nibble)

        def _do_undo() -> None:
            doc._nibbles[sidx] = bytearray(old_nibs)
            doc._flush_sector_lightmap(sidx)

        def _do_redo() -> None:
            doc.reset_sector_lightmap(sidx, nibble)

        self._push_command(UndoCommand(f"重置扇区 #{sidx} 光照", _do_undo, _do_redo))

    def replace_sector_tile(
        self,
        sector_index: int,
        image: Image.Image | RgbImage | Path | str,
        *,
        quality: int = 92,
    ) -> None:
        doc = self._require_doc()
        if isinstance(image, (Path, str)):
            with Image.open(image) as im:
                rgb = RgbImage.from_pil(im.resize((SECTOR_PX_W, SECTOR_PX_H)))
        else:
            rgb = image if isinstance(image, RgbImage) else RgbImage.from_pil(image)
        old_seg, old_pay = doc.replace_sector_image(sector_index, rgb, quality=quality)
        new_seg, new_pay = (
            doc.sector(sector_index).segment_lengths,
            doc.read_image_payload(doc.sector(sector_index)),
        )
        self._push_command(
            UndoCommand(
                f"替换扇区 #{sector_index} 底图",
                lambda: doc.set_raw_sector_image(sector_index, old_seg, old_pay),
                lambda: doc.set_raw_sector_image(sector_index, new_seg, new_pay),
            )
        )

    def import_full_map_image(
        self, image: Image.Image | RgbImage | Path | str, *, quality: int = 92
    ) -> None:
        doc = self._require_doc()
        old_tiles = {
            s.index: (s.segment_lengths, doc.read_image_payload(s))
            for s in doc.iter_sectors()
        }
        doc.import_full_image(image, quality=quality)
        new_tiles = {
            s.index: (s.segment_lengths, doc.read_image_payload(s))
            for s in doc.iter_sectors()
        }

        def _restore(tiles: dict[int, tuple[tuple[int, ...], bytes]]) -> None:
            for idx, (sl, pay) in tiles.items():
                doc.set_raw_sector_image(idx, sl, pay)

        self._push_command(
            UndoCommand(
                "导入整张地图底图",
                lambda: _restore(old_tiles),
                lambda: _restore(new_tiles),
            )
        )

    def import_mask_image(
        self, image: Image.Image | Path | str, x: int, y: int
    ) -> int:
        doc = self._require_doc()
        before_recs = list(doc.records)
        before_refs = dict(doc._ref_overrides)
        added = doc.add_record_from_image(image, x, y)
        after_recs = list(doc.records)
        after_refs = dict(doc._ref_overrides)
        self.state.selected_record = added.index
        self._push_command(
            UndoCommand(
                f"新增前景遮罩 #{added.index}",
                lambda: doc.set_records_state(before_recs, before_refs),
                lambda: doc.set_records_state(after_recs, after_refs),
            )
        )
        return added.index

    def move_mask_record(self, index: int, new_x: int, new_y: int) -> None:
        doc = self._require_doc()
        before_recs = list(doc.records)
        before_refs = dict(doc._ref_overrides)
        doc.move_record(index, new_x, new_y)
        after_recs = list(doc.records)
        after_refs = dict(doc._ref_overrides)
        self._push_command(
            UndoCommand(
                f"移动前景遮罩 #{index} -> ({new_x}, {new_y})",
                lambda: doc.set_records_state(before_recs, before_refs),
                lambda: doc.set_records_state(after_recs, after_refs),
            )
        )

    def delete_mask_record(self, index: int) -> None:
        doc = self._require_doc()
        before_recs = list(doc.records)
        before_refs = dict(doc._ref_overrides)
        doc.remove_record(index)
        after_recs = list(doc.records)
        after_refs = dict(doc._ref_overrides)
        if self.state.selected_record is not None:
            self.state.selected_record = (
                min(self.state.selected_record, len(after_recs) - 1)
                if after_recs
                else None
            )
        self._push_command(
            UndoCommand(
                f"删除前景遮罩 #{index}",
                lambda: doc.set_records_state(before_recs, before_refs),
                lambda: doc.set_records_state(after_recs, after_refs),
            )
        )

    # -- pathfinding & health audit ---------------------------------------
    def simulate_path(
        self, start_px: tuple[int, int], goal_px: tuple[int, int]
    ) -> PathResult:
        doc = self._require_doc()
        h = doc.header
        scell = (start_px[0] // CELL_PX, start_px[1] // CELL_PX)
        gcell = (goal_px[0] // CELL_PX, goal_px[1] // CELL_PX)
        res = find_path(
            h.grid_columns,
            h.grid_rows,
            lambda cx, cy: is_walkable(doc.cell_at_index(cx, cy)),
            scell,
            gcell,
        )
        self.state.path_start = start_px
        self.state.path_goal = goal_px
        self.state.last_path = res
        return res

    def audit_current_map(self) -> dict:
        doc = self._require_doc()
        h = doc.header
        walk = analyze_walkability(
            h.grid_columns,
            h.grid_rows,
            lambda cx, cy: (
                1 if (value := doc.cell_at_index(cx, cy)) is None else value
            ),
        )
        canonical_refs = compute_sector_record_refs(h.width, h.height, doc.records)
        ref_mismatches = sum(
            1 for s in doc.iter_sectors() if s.record_refs != canonical_refs[s.index]
        )
        non_neutral_sectors = 0
        min_nib, max_nib = 15, 0
        for sidx in range(h.sector_count):
            nibs = doc.lightmap_nibbles(sidx)
            if nibs is not None:
                lo, hi = min(nibs), max(nibs)
                min_nib = min(min_nib, lo)
                max_nib = max(max_nib, hi)
                if lo != NEUTRAL_NIBBLE or hi != NEUTRAL_NIBBLE:
                    non_neutral_sectors += 1
        ents = self.current_entities()
        blocked_npcs = [n["name"] for n in ents["npcs"] if not n["walkable"]]
        return {
            "key": self.state.current_key,
            "name": self.state.current_name,
            "width": h.width,
            "height": h.height,
            "sectors": h.sector_count,
            "trailing_bytes": doc.trailing_bytes,
            "records": len(doc.records),
            "out_of_bounds_records": len(doc.out_of_bounds_records()),
            "sector_ref_mismatches": ref_mismatches,
            "girb_non_neutral_sectors": non_neutral_sectors,
            "girb_nibble_range": [min_nib, max_nib],
            "walkability": walk,
            "npc_count": len(ents["npcs"]),
            "blocked_npcs": blocked_npcs,
            "portal_count": len(ents["portals"]),
        }

    # -- rendering & collision region queries -----------------------------
    def collision_region(self, x0: int, y0: int, x1: int, y1: int) -> dict:
        from ..core.girb import CELL_PX as CPX
        from ..core.girb import GRID_COLS, GRID_ROWS

        doc = self._require_doc()
        h = doc.header
        cx0, cy0 = x0 // CPX, y0 // CPX
        cx1 = min(-(-x1 // CPX), h.sector_columns * GRID_COLS)
        cy1 = min(-(-y1 // CPX), h.sector_rows * GRID_ROWS)
        cx0, cy0 = max(0, cx0), max(0, cy0)
        if cx1 <= cx0 or cy1 <= cy0:
            return {
                "cols": 0,
                "rows": 0,
                "cell_px": CPX,
                "values": [],
                "decoded": 0,
                "failed": 0,
            }
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
                values.append(
                    None
                    if vals is None
                    else vals[(cy % GRID_ROWS) * GRID_COLS + (cx % GRID_COLS)]
                )
        return {
            "origin_cell": (cx0, cy0),
            "cols": cx1 - cx0,
            "rows": cy1 - cy0,
            "cell_px": CPX,
            "values": values,
            "decoded": decoded,
            "failed": failed,
        }

    def collision_stats(self) -> dict:
        return self._require_doc().collision_stats()

    def girb_report(self) -> list[dict]:
        out: list[dict] = []
        for r in self.rows:
            if r.broken:
                out.append({"key": r.key, "name": r.name, "error": r.error})
                continue
            try:
                self.open_map(r)
                st = self.collision_stats()
                lengths = sorted(
                    {len(s.girb_body) for s in self._require_doc().iter_sectors()}
                )
                st.update(
                    {
                        "key": r.key,
                        "name": r.name,
                        "size": f"{r.width}x{r.height}",
                        "girb_len_min": lengths[0],
                        "girb_len_max": lengths[-1],
                    }
                )
                out.append(st)
                self.close_map()
            except Exception as exc:
                out.append({"key": r.key, "name": r.name, "error": str(exc)})
                self.close_map()
        return out

    def render(
        self, x0: int, y0: int, x1: int, y1: int, *, apply_lighting: bool = False
    ) -> RgbImage:
        doc = self._require_doc()
        return render_region(doc, x0, y0, x1, y1, apply_lighting=apply_lighting)

    # -- save & export guards + writers -----------------------------------
    def _protected_source_paths(self) -> list[Path]:
        paths: list[Path] = []
        if self._doc is not None:
            paths.append(Path(self._doc.path))
        if self.layout is not None:
            paths.extend(Path(m.path) for m in self.layout.maps)
        return paths

    def is_protected_source_path(self, dest: str | Path) -> Path | None:
        target = Path(dest)
        for protected in self._protected_source_paths():
            if _same_file_or_path(target, protected):
                return protected
        return None

    def _guard_export_target(
        self, dest: str | Path, *, allow_loose_overwrite: bool = False
    ) -> Path:
        target = Path(dest)
        hit = self.is_protected_source_path(target)
        if hit is not None:
            if allow_loose_overwrite and self.config.save_mode == "loose":
                return target
            raise ExportBlockedError(
                f"拒绝覆盖源地图 {hit}（当前为严苛保护模式；"
                "请使用“另存为”输出到新路径，或显式切换为宽松模式并二次确认）。"
            )
        return target

    def save_map(
        self, dest: str | Path, *, allow_overwrite_source: bool = False
    ) -> Path:
        """Save current map as a verified ``0.1M`` ``.map`` container."""
        target = self._guard_export_target(
            dest, allow_loose_overwrite=allow_overwrite_source
        )
        doc = self._require_doc()
        result = doc.save(target, verify=True)
        self._saved_state_token = self._state_token
        return result

    def export_blk(self, dest: str | Path) -> Path:
        target = self._guard_export_target(dest)
        doc = self._require_doc()
        grid: BlkGrid = extract_blk_from_map(doc)
        write_blk(grid, target)
        return target

    def import_blk(self, src: str | Path) -> int:
        doc = self._require_doc()
        grid = read_blk(src)
        before = extract_blk_from_map(doc)
        apply_blk_to_map(doc, grid)
        after = extract_blk_from_map(doc)
        changed_count = sum(
            1 for a, b in zip(before.cells, after.cells, strict=True) if a != b
        )
        self._push_command(
            UndoCommand(
                f"导入 .blk ({grid.width}x{grid.height})",
                lambda: apply_blk_to_map(doc, before),
                lambda: apply_blk_to_map(doc, after),
            )
        )
        return changed_count

    def export_walkability_png(self, dest: str | Path) -> Path:
        p = self._guard_export_target(dest)
        doc = self._require_doc()
        w, h = doc.header.grid_columns, doc.header.grid_rows
        palette = {
            0: (46, 204, 113),
            1: (231, 76, 60),
            2: (52, 198, 226),
            3: (155, 89, 182),
        }
        rgb = bytearray(w * h * 3)
        for cy in range(h):
            for cx in range(w):
                v = doc.cell_at_index(cx, cy) or 0
                off = (cy * w + cx) * 3
                rgb[off:off + 3] = bytes(palette.get(v, (241, 196, 15)))
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("RGB", (w, h), bytes(rgb)).save(p)
        return p

    def export_lightmap_png(self, dest: str | Path) -> Path:
        p = self._guard_export_target(dest)
        doc = self._require_doc()
        lw, lh = doc.header.light_columns, doc.header.light_rows
        gray = bytearray(lw * lh)
        for ly in range(lh):
            for lx in range(lw):
                nib = doc.lightmap_at_index(lx, ly)
                gray[ly * lw + lx] = (NEUTRAL_NIBBLE if nib is None else nib) * 17
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("L", (lw, lh), bytes(gray)).save(p)
        return p

    def export_mask_png(
        self, index: int, dest: str | Path, *, cutout: bool = True
    ) -> Path:
        p = self._guard_export_target(dest)
        doc = self._require_doc()
        dm = doc.decode_record(index)
        backdrop: RgbImage | None = None
        bx0 = max(0, dm.x)
        by0 = max(0, dm.y)
        bx1 = min(doc.header.width, dm.x + dm.width)
        by1 = min(doc.header.height, dm.y + dm.height)
        if cutout and bx1 > bx0 and by1 > by0:
            backdrop = render_region(doc, bx0, by0, bx1, by1)
        im = dm.to_rgba_cutout(backdrop, backdrop_origin=(bx0, by0))
        p.parent.mkdir(parents=True, exist_ok=True)
        im.save(p)
        return p

    def export_json(self, dest: str | Path, *, include_cells: bool = False) -> Path:
        dest = self._guard_export_target(dest)
        doc = self._require_doc()
        h = doc.header
        payload: dict = {
            "format": "map-editor/export",
            "version": 2,
            "source": str(doc.path),
            "client_root": self.state.client_root,
            "scene_key": self.state.current_key,
            "scene_name": self.state.current_name,
            "width": h.width,
            "height": h.height,
            "trailing_bytes": doc.trailing_bytes,
            "sector_count": h.sector_count,
            "sector_grid": [h.sector_columns, h.sector_rows],
            "logical_grid_cells": [h.grid_columns, h.grid_rows],
            "cell_px": CELL_PX,
            "sectors": [
                {
                    "index": s.index,
                    "row": s.row,
                    "col": s.col,
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
                {
                    "index": r.index,
                    "x": r.x,
                    "y": r.y,
                    "w": r.width,
                    "h": r.height,
                    "payload_length": r.payload_length,
                    "payload_head": r.payload[:32].hex(),
                }
                for r in doc.records
            ],
        }
        if include_cells:
            payload["cells"] = [
                {"sector": s.index, "values": list(doc.read_cells(s))}
                for s in doc.iter_sectors()
            ]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        return dest

    def export_png(
        self,
        dest: str | Path,
        region: tuple[int, int, int, int] | None = None,
        *,
        apply_lighting: bool = False,
    ) -> Path:
        p = self._guard_export_target(dest)
        doc = self._require_doc()
        box = region or (0, 0, doc.header.width, doc.header.height)
        img = render_region(doc, *box, apply_lighting=apply_lighting)
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("RGB", (img.width, img.height), img.data).save(p)
        return p

    # -- status & config --------------------------------------------------
    def status_line(self) -> str:
        s = self.state
        if not s.client_root and not s.current_key:
            return s.status
        parts: list[str] = []
        if s.client_root:
            parts.append(f"{s.map_count} 张地图 · 扫描 {s.scanned_files} 个文件")
        if s.current_key:
            mod = " *未保存*" if self.dirty else ""
            parts.append(
                f"当前 {s.current_key} {s.current_name}{mod} "
                f"{s.current_size[0]}x{s.current_size[1]} "
                f"({s.current_sectors} 扇区 / {s.current_records} 遮罩)"
            )
        if s.cursor:
            parts.append(f"光标 {s.cursor[0]},{s.cursor[1]}")
        return " · ".join(parts)

    def save_config(self) -> Path:
        return self.config.save()

    def _require_doc(self) -> MapDocument:
        if self._doc is None:
            raise RuntimeError("no map is open")
        return self._doc


def _sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()[:16]


__all__ = [
    "DiscoveryError",
    "EditorState",
    "EditorViewModel",
    "ExportBlockedError",
    "Iterable",
    "LAYERS",
    "MAX_UNDO_STEPS",
    "MapRow",
    "TOOLS",
    "UndoCommand",
]
