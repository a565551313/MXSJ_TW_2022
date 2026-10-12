"""Optional scene-name table.

A ``.map`` file carries no name — only pixel dimensions.  Human-readable scene
names live in ``data/script.fls``, behind an obfuscation layer this editor does
not re-implement (see :mod:`map_editor.client.scriptfls`).  So names are shipped
as a generated sidecar, ``data/scenes_tw_v2_27_2.json``, and everything degrades
gracefully when it is missing: the editor still lists every map with its real
dimensions read from the file header.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

TABLE_FILENAME = "scenes_tw_v2_27_2.json"
_PACKAGED_DIRNAME = "map_editor_data"


def default_table_path() -> Path:
    """Where the shipped scene table lives.

    Checked in order: ``MAP_EDITOR_SCENE_TABLE``, the PyInstaller bundle
    (``sys._MEIPASS``), the source tree's ``data/`` directory, and finally the
    user config directory so a user can drop in a regenerated table.
    """
    env = os.environ.get("MAP_EDITOR_SCENE_TABLE")
    if env:
        return Path(env).expanduser()
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        p = Path(bundle) / _PACKAGED_DIRNAME / TABLE_FILENAME
        if p.is_file():
            return p
    here = Path(__file__).resolve()
    for parent in here.parents:                 # src/map_editor/client -> project root
        cand = parent / "data" / TABLE_FILENAME
        if cand.is_file():
            return cand
    from .config import config_dir
    return config_dir() / TABLE_FILENAME


@dataclass(frozen=True, slots=True)
class SceneMeta:
    key: str
    name: str
    width: int | None
    height: int | None
    minimap_name: str | None


class SceneTable:
    """Maps a ``%04d`` scene key to its name and declared size."""

    def __init__(self, scenes: dict[str, dict] | None = None,
                 minimap: dict[str, str] | None = None,
                 source: Path | None = None) -> None:
        self._scenes = scenes or {}
        self._minimap = minimap or {}
        self.source = source

    @classmethod
    def load(cls, path: Path | str | None = None) -> "SceneTable":
        p = Path(path) if path else default_table_path()
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        return cls(doc.get("scenes") or {}, doc.get("minimap_names") or {}, p)

    def __len__(self) -> int:
        return len(self._scenes)

    def __bool__(self) -> bool:
        return bool(self._scenes)

    @staticmethod
    def normalize(key: str | int) -> str:
        s = str(key).strip()
        if s.lower().endswith(".map"):
            s = s[:-4]
        return s.zfill(4)

    def get(self, key: str | int) -> SceneMeta | None:
        k = self.normalize(key)
        row = self._scenes.get(k)
        if row is None:
            return None
        return SceneMeta(
            key=k,
            name=row.get("name") or k,
            width=row.get("w"),
            height=row.get("h"),
            minimap_name=self._minimap.get(k),
        )

    def display_name(self, key: str | int) -> str:
        meta = self.get(key)
        return meta.name if meta else f"场景 {self.normalize(key)}"

    def keys(self) -> list[str]:
        return sorted(self._scenes)


__all__ = ["SceneMeta", "SceneTable", "TABLE_FILENAME", "default_table_path"]
