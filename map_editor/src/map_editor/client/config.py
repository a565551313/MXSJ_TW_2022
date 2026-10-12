"""Persistent settings, stored in the **user's home directory**.

The editor must run from anywhere — a PyInstaller EXE dropped on the desktop, a
USB stick, ``C:\\tools\\`` — and still remember which client the user pointed it
at.  Nothing is ever written next to the executable, because that folder may be
read-only (``Program Files``) or ephemeral.

Location: ``$MAP_EDITOR_HOME`` if set, else ``~/.map_editor`` on POSIX and
``%APPDATA%\\MapEditor`` on Windows.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_DIRNAME = ".map_editor"
WINDOWS_DIRNAME = "MapEditor"
CONFIG_FILENAME = "config.json"
MAX_RECENT = 10


def config_dir() -> Path:
    override = os.environ.get("MAP_EDITOR_HOME")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / WINDOWS_DIRNAME
    return Path.home() / APP_DIRNAME


@dataclass(slots=True)
class Config:
    client_root: str = ""
    recent_roots: list[str] = field(default_factory=list)
    scene_table: str = ""
    # Layer visibility, persisted so the workspace looks the same next launch.
    show_texture: bool = True
    show_grid: bool = False
    show_records: bool = True
    show_sector_bounds: bool = True
    show_collision: bool = False
    show_collision_grid: bool = False
    # Value used to decide "walkable" in the LLEC grid.  0/1 are the only values
    # whose meaning is supported by evidence; everything else is unclassified,
    # so the threshold stays conservative until the format is understood.
    walkable_threshold: int = 1
    zoom: float = 1.0
    window: dict = field(default_factory=dict)

    # -- io ---------------------------------------------------------------
    @property
    def path(self) -> Path:
        return config_dir() / CONFIG_FILENAME

    @classmethod
    def load(cls, path: Path | str | None = None) -> "Config":
        p = Path(path) if path else config_dir() / CONFIG_FILENAME
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        if not isinstance(raw, dict):
            return cls()
        known = {f for f in cls.__slots__}                     # type: ignore[attr-defined]
        return cls(**{k: v for k, v in raw.items() if k in known})

    def save(self, path: Path | str | None = None) -> Path:
        p = Path(path) if path else self.path
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(self), ensure_ascii=False, indent=2)
        # Write-then-rename so a crash cannot leave a half-written config.
        fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=p.name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload)
            os.replace(tmp, p)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return p

    # -- helpers ----------------------------------------------------------
    def remember_root(self, root: str | Path) -> None:
        s = str(Path(root).expanduser())
        self.client_root = s
        self.recent_roots = [s] + [r for r in self.recent_roots if r != s]
        self.recent_roots = self.recent_roots[:MAX_RECENT]


__all__ = ["Config", "config_dir"]
