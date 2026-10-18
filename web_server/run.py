"""Lightweight source/frozen entry point; never installs dependencies."""

from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    if not getattr(sys, "frozen", False):
        sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from mxsj_web_server.app import entry_main

    raise SystemExit(entry_main())
