"""Locate the game client used by the test suite.

The tests must not assume where the project is checked out.  Walk up from this
file looking for something that *is* a client root: a folder holding ``*.map``
files with the ``0.1M`` signature and/or ``data/script.fls``.  ``MXSJ_REPO``
overrides the search.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def _looks_like_client(d: Path) -> bool:
    return (d / "data" / "script.fls").is_file() or bool(list(d.glob("map/*.map")))


def find_client_root() -> Path | None:
    override = os.environ.get("MXSJ_REPO")
    if override:
        p = Path(override).expanduser()
        return p if p.is_dir() else None
    for candidate in [PROJECT, *PROJECT.parents]:
        if _looks_like_client(candidate):
            return candidate
        nested = candidate / "MXSJ_TW_2022"
        if nested.is_dir() and _looks_like_client(nested):
            return nested
    return None


CLIENT_ROOT = find_client_root()
SAMPLES = CLIENT_ROOT / "map" if CLIENT_ROOT else PROJECT / "no-samples"
SCRIPT_FLS = (CLIENT_ROOT / "data" / "script.fls" if CLIENT_ROOT
              else PROJECT / "no-script.fls")


def reference_png_dir() -> Path | None:
    """PNGs produced by the older ImageMagick-based decoder, used as ground truth."""
    if not CLIENT_ROOT:
        return None
    cand = (CLIENT_ROOT / "work" / "dream-world-connect-login-map"
            / "tools" / "map-textures")
    return cand if cand.is_dir() else None


if str(PROJECT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT / "src"))
