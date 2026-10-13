# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the MXSJ 资源编辑器 (resource_editor).

Build on Windows:      build_exe.bat
Single-file EXE:       set RESOURCE_EDITOR_ONEFILE=1  then run build_exe.bat again
Linux dry run only:    pyinstaller --noconfirm --clean resource_editor.spec
                       (proves hiddenimports/datas are complete; no .exe)
"""
import os

from PyInstaller.utils.hooks import collect_submodules

ONEFILE = os.environ.get("RESOURCE_EDITOR_ONEFILE", "0") == "1"

# known_paths.txt (the harvested path dictionary) is looked up as
# ``Path(__file__).resolve().parent.parent / "data"`` from inside the frozen
# package, so it must land under ``resource_editor/data`` in the bundle.
datas = [("src/resource_editor/data", "resource_editor/data")]

hiddenimports = collect_submodules("resource_editor")

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
    name="ResourceEditor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,              # GUI app: double-click opens the window directly
    disable_windowed_traceback=False,
    target_arch=None,
)

if not ONEFILE:
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, name="ResourceEditor",
    )
