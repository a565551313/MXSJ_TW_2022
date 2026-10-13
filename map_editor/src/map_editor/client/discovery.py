"""Locate game data inside an arbitrary client installation.

The whole point of this module is that the editor must never assume where it was
installed or where the client lives.  The user picks a **client root**; we walk
it and identify everything by content, not by path:

* ``*.map`` files are accepted only when their first four bytes are ``0.1M``, so
  unrelated files with a ``.map`` extension are ignored and maps stored in any
  subfolder are still found.  ``mx.exe`` formats the filename as ``%04d.map``
  with **no directory prefix**, so the real install layout is unknown and a
  recursive scan is the only safe answer.
* ``data/script.fls`` is found by name plus the ``FLS\\0`` signature; it holds
  the scene dictionary that gives each map its id and real name.

Scanning is bounded (depth, file count, per-file probe size) so pointing the tool
at a whole drive fails gracefully instead of hanging.
"""
from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ..core.mapfile import MAGIC, sniff

# ``script.fls`` and friends use ``0SLF``; ``data.fls`` uses ``FLS\0``.
FLS_MAGICS = (b"0SLF", b"FLS\x00")
DEFAULT_MAX_FILES = 200_000
DEFAULT_MAX_DEPTH = 12
# Directories that can never contain map data and are expensive to walk.
PRUNE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv",
    "$recycle.bin", "system volume information", "windows", "winsxs",
}


class DiscoveryError(RuntimeError):
    """Raised when the chosen root cannot be scanned at all."""


@dataclass(slots=True)
class MapFile:
    path: Path
    size: int

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def scene_key(self) -> str:
        """The ``%04d`` id the client uses for this file."""
        return self.stem


@dataclass(slots=True)
class ClientLayout:
    root: Path
    maps: list[MapFile] = field(default_factory=list)
    script_fls: Path | None = None
    main_exe: Path | None = None
    scanned_files: int = 0
    elapsed_s: float = 0.0
    pruned: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.maps)

    def by_scene_key(self, key: str) -> MapFile | None:
        for m in self.maps:
            if m.scene_key == key:
                return m
        return None

    def summary(self) -> dict:
        return {
            "root": str(self.root),
            "map_count": len(self.maps),
            "script_fls": str(self.script_fls) if self.script_fls else None,
            "main_exe": str(self.main_exe) if self.main_exe else None,
            "scanned_files": self.scanned_files,
            "elapsed_s": round(self.elapsed_s, 3),
        }


def _is_fls(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            head = fh.read(4)
    except OSError:
        return False
    return head in FLS_MAGICS


def discover(
    root: str | Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    progress: Callable[[int, Path], None] | None = None,
    prune: Iterable[str] | None = None,
) -> ClientLayout:
    """Walk ``root`` and return every verified ``0.1M`` map plus ``script.fls``.

    ``progress`` is called as ``progress(scanned_files, current_path)`` roughly
    every 200 files so a UI can show a live counter.
    """
    base = Path(root).expanduser()
    if not base.exists():
        raise DiscoveryError(f"path does not exist: {base}")
    if not base.is_dir():
        raise DiscoveryError(f"not a directory: {base}")

    prune_set = {p.lower() for p in (prune if prune is not None else PRUNE_DIRS)}
    layout = ClientLayout(root=base)
    started = time.monotonic()
    root_depth = len(base.parts)
    maps: list[MapFile] = []
    fls_candidates: list[Path] = []
    exe_candidates: list[Path] = []
    count = 0

    for dirpath, dirnames, filenames in os.walk(base, onerror=lambda e: None):
        depth = len(Path(dirpath).parts) - root_depth
        if depth >= max_depth:
            dirnames[:] = []
        kept = []
        for d in dirnames:
            if d.lower() in prune_set:
                layout.pruned.append(Path(dirpath) / d)
            else:
                kept.append(d)
        dirnames[:] = sorted(kept)

        for name in sorted(filenames):
            count += 1
            if count > max_files:
                layout.elapsed_s = time.monotonic() - started
                layout.scanned_files = count
                layout.maps = sorted(maps, key=lambda m: m.scene_key)
                return layout
            path = Path(dirpath) / name
            low = name.lower()
            if low.endswith(".map"):
                if sniff(path):
                    try:
                        size = path.stat().st_size
                    except OSError:
                        size = 0
                    maps.append(MapFile(path=path, size=size))
            elif low == "script.fls" and _is_fls(path):
                fls_candidates.append(path)
            elif low in ("mx.exe", "mxmain.dll"):
                exe_candidates.append(path)
            if progress and count % 200 == 0:
                progress(count, path)

    layout.maps = sorted(maps, key=lambda m: m.scene_key)
    # Prefer data/script.fls, then the shallowest match.
    fls_candidates.sort(key=lambda p: (p.parent.name.lower() != "data", len(p.parts)))
    layout.script_fls = fls_candidates[0] if fls_candidates else None
    exe_candidates.sort(key=lambda p: (p.name.lower() != "mx.exe", len(p.parts)))
    layout.main_exe = exe_candidates[0] if exe_candidates else None
    layout.scanned_files = count
    layout.elapsed_s = time.monotonic() - started
    return layout


def describe(layout: ClientLayout) -> str:
    """One-line human summary used by the UI status bar and the CLI."""
    if not layout.ok:
        return (f"{layout.root}: no 0.1M map files found "
                f"({layout.scanned_files} files scanned)")
    sizes = {f"{m.size}" for m in layout.maps}
    return (f"{len(layout.maps)} maps under {layout.root} "
            f"({len(sizes)} distinct sizes, {layout.scanned_files} files scanned in "
            f"{layout.elapsed_s:.2f}s)"
            + (f", script.fls: {layout.script_fls.name}" if layout.script_fls
               else ", no script.fls"))


__all__ = ["ClientLayout", "DiscoveryError", "MapFile", "MAGIC", "describe", "discover"]
