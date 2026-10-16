from __future__ import annotations

import os
from pathlib import Path

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_submodules

HERE = Path(globals()["SPECPATH"])
ONEFILE = os.environ.get("MXSJ_MANUAL_ONEFILE") == "1"
datas = [
    (str(HERE / name), f"manual_content/{name}")
    for name in (
        "schema", "coordination", "inventory", "annotations", "reviews", "guides"
    )
]
datas += [(str(HERE / "src/mxsj_manual/assets"), "mxsj_manual/assets")]
a = Analysis(
    [str(HERE / "run.py")],
    pathex=[str(HERE / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("mxsj_manual"),
    excludes=["tkinter", "matplotlib", "numpy", "pytest", "PySide6.QtWebEngineWidgets"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    *([a.binaries, a.datas] if ONEFILE else []),
    [],
    name="MXSJScriptManual",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    exclude_binaries=not ONEFILE,
)
if not ONEFILE:
    coll = COLLECT(
        exe, a.binaries, a.datas, strip=False, upx=False, name="MXSJScriptManual"
    )
