"""Scene metadata, ``NEW_RPL_MAP`` / ``RPL_MAP_BLK`` aliases, NPCs & portals.

A ``.map`` file carries no name — only pixel dimensions.  Human-readable scene
names, runtime file replacements (``NEW_RPL_MAP``), portals (``minimap_data``),
arrival cells (``mappos``), BGM tracks, and NPC spawn coordinates are shipped in
``data/scenes_tw_v2_27_2.json`` and degrade gracefully when absent.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

TABLE_FILENAME = "scenes_tw_v2_27_2.json"
_PACKAGED_DIRNAME = "map_editor_data"
_VARIANT_RE = re.compile(r"^(?:test_)?(?:new2?_)?(\d+)$", re.IGNORECASE)


def default_table_path() -> Path:
    """Where the shipped scene table lives."""
    env = os.environ.get("MAP_EDITOR_SCENE_TABLE")
    if env:
        return Path(env).expanduser()
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        p = Path(bundle) / _PACKAGED_DIRNAME / TABLE_FILENAME
        if p.is_file():
            return p
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "data" / TABLE_FILENAME
        if cand.is_file():
            return cand
    from .config import config_dir

    return config_dir() / TABLE_FILENAME


@dataclass(frozen=True, slots=True)
class PortalInfo:
    sx: int
    sy: int
    jump_sx: int
    jump_sy: int
    name: str
    desc: str = ""
    npc_id: int | None = None


@dataclass(frozen=True, slots=True)
class NpcSpawn:
    npc_id: int
    name: str
    alias: str
    sx: int
    sy: int
    direction: int = 0
    shape: str = ""


@dataclass(frozen=True, slots=True)
class SceneMeta:
    key: str
    name: str
    width: int | None
    height: int | None
    minimap_name: str | None
    category: str = ""
    bgm: str = ""
    active_map_stem: str = ""
    variant_tag: str = ""
    arrival_cell: tuple[int, int] | None = None
    portals: tuple[PortalInfo, ...] = ()
    npcs: tuple[NpcSpawn, ...] = ()


class SceneTable:
    """Maps a ``%04d`` scene id or replacement stem (e.g. ``test_new2_1054``)
    to its full scene metadata."""

    def __init__(
        self,
        scenes: dict[str, dict] | None = None,
        minimap: dict[str, str] | None = None,
        source: Path | None = None,
        *,
        new_rpl_map: dict[str, str] | None = None,
        rpl_map_blk: dict[str, str] | None = None,
    ) -> None:
        self._scenes = scenes or {}
        self._minimap = minimap or {}
        self.new_rpl_map = new_rpl_map or {}
        self.rpl_map_blk = rpl_map_blk or {}
        self._stem_to_scene_id: dict[str, str] = {
            stem.lower(): sid for sid, stem in self.new_rpl_map.items()
        }
        self.source = source

    @classmethod
    def load(cls, path: Path | str | None = None) -> SceneTable:
        p = Path(path) if path else default_table_path()
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        return cls(
            doc.get("scenes") or {},
            doc.get("minimap_names") or {},
            p,
            new_rpl_map=doc.get("new_rpl_map") or {},
            rpl_map_blk=doc.get("rpl_map_blk") or {},
        )

    def __len__(self) -> int:
        return len(self._scenes)

    def __bool__(self) -> bool:
        return bool(self._scenes)

    @staticmethod
    def normalize(key: str | int) -> str:
        s = str(key).strip()
        if s.lower().endswith(".map"):
            s = s[:-4]
        return s.zfill(4) if s.isdigit() else s

    def base_scene_id(self, key: str | int) -> tuple[str, str]:
        """Return ``(canonical_4digit_id, variant_tag)`` for ``key``."""
        norm = self.normalize(key)
        low = norm.lower()
        if norm in self._scenes:
            active = self.new_rpl_map.get(norm, "")
            if active and active.lower() != low:
                return norm, f"舊版 -> {active}"
            return norm, ""
        if low in self._stem_to_scene_id:
            sid = self._stem_to_scene_id[low]
            return sid, ("現行" if not norm.isdigit() else "")
        m = _VARIANT_RE.match(norm)
        if m:
            sid = m.group(1).zfill(4)
            active = self.new_rpl_map.get(sid, "")
            if active and active.lower() == low:
                return sid, "現行"
            if not norm.isdigit():
                prefix = norm[: norm.rfind("_")]
                return sid, f"歷史 {prefix}"
        return norm, ""

    def get(self, key: str | int) -> SceneMeta | None:
        base_id, vtag = self.base_scene_id(key)
        row = self._scenes.get(base_id)
        if row is None:
            return None
        base_name = row.get("name") or base_id
        display = f"{base_name} [{vtag}]" if vtag else base_name
        raw_arr = row.get("arrival_cell")
        arr = (int(raw_arr[0]), int(raw_arr[1])) if raw_arr else None
        portals = tuple(
            PortalInfo(
                sx=int(p["sx"]),
                sy=int(p["sy"]),
                jump_sx=int(p["jump_sx"]),
                jump_sy=int(p["jump_sy"]),
                name=str(p.get("name") or ""),
                desc=str(p.get("desc") or ""),
                npc_id=p.get("npc_id"),
            )
            for p in (row.get("portals") or ())
        )
        npcs = tuple(
            NpcSpawn(
                npc_id=int(n["npc_id"]),
                name=str(n.get("name") or ""),
                alias=str(n.get("alias") or ""),
                sx=int(n["sx"]),
                sy=int(n["sy"]),
                direction=int(n.get("dir") or 0),
                shape=str(n.get("shape") or ""),
            )
            for n in (row.get("npcs") or ())
        )
        return SceneMeta(
            key=base_id,
            name=display,
            width=row.get("w"),
            height=row.get("h"),
            minimap_name=self._minimap.get(base_id),
            category=str(row.get("category") or ""),
            bgm=str(row.get("bgm") or ""),
            active_map_stem=str(row.get("active_map_stem") or ""),
            variant_tag=vtag,
            arrival_cell=arr,
            portals=portals,
            npcs=npcs,
        )

    def display_name(self, key: str | int) -> str:
        meta = self.get(key)
        return meta.name if meta else f"场景 {self.normalize(key)}"

    def keys(self) -> list[str]:
        return sorted(self._scenes)


__all__ = [
    "NpcSpawn",
    "PortalInfo",
    "SceneMeta",
    "SceneTable",
    "TABLE_FILENAME",
    "default_table_path",
]
