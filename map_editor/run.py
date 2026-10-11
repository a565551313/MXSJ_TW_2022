#!/usr/bin/env python3
"""Entry point for the MXSJ map editor.

    python run.py --gui --client-root "D:/Games/MXSJ"   # 图形界面
    python run.py --scan "D:/Games/MXSJ"                # 终端列出全部地图
    python run.py --scan . --export-json 2101:out.json  # 导出结构 JSON

Packaged on Windows by build.bat -> dist/MapEditor/MapEditor.exe
"""
from __future__ import annotations

import sys
from pathlib import Path

# Works from a source checkout and from a PyInstaller bundle (where the package
# is already importable and this insert is a harmless no-op).
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from map_editor.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
