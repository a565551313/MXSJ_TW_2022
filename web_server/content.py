"""Compatibility CLI; content implementation lives only in the package core."""

from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from mxsj_web_server.app import content_main

    raise SystemExit(content_main())
