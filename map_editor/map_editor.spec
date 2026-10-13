# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the MXSJ map editor.

Build on Windows:      build_exe.bat
Single-file EXE:       set MAP_EDITOR_ONEFILE=1  then run build_exe.bat again
Linux dry run only:    pyinstaller --noconfirm --clean map_editor.spec
                       (proves hiddenimports/datas are complete; no .exe)
"""
import os

from PyInstaller.utils.hooks import collect_submodules

ONEFILE = os.environ.get("MAP_EDITOR_ONEFILE", "0") == "1"

# The scene-name table is data, not code: bundle it so the EXE carries its own
# copy and stays independent of wherever it is copied to.
datas = [("data", "map_editor_data")]

hiddenimports = ["map_editor", "map_editor.core", "map_editor.client", "map_editor.ui"]
hiddenimports += collect_submodules("map_editor")

a = Analysis(
    ["run.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries if ONEFILE else [],
    a.datas if ONEFILE else [],
    [],
    # onedir: binaries/datas go to COLLECT below; without this flag PyInstaller
    # treats the EXE as onefile and COLLECT then fails (caught by the Linux dry run).
    exclude_binaries=not ONEFILE,
    name="MapEditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,              # GUI app; use --cli via a console build if needed
    disable_windowed_traceback=False,
    target_arch=None,
)

if not ONEFILE:
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, name="MapEditor",
    )
