from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "manual_content"
    return Path(__file__).resolve().parents[2]
