# -*- mode: python ; coding: utf-8 -*-
"""Windows onedir GUI. Legacy compilers are external, never onefile-extracted."""
from PyInstaller.utils.hooks import collect_submodules

# No onefile switch: legacy runtimes need a persistent audited external folder.
a = Analysis(
    ["run.py"], pathex=["src"], binaries=[],
    datas=[("src/script_editor/data/compile_legacy.py", "script_editor/data")],
    hiddenimports=collect_submodules(
        "script_editor", filter=lambda n: not n.startswith("script_editor.data")
    ), hookspath=[],
    runtime_hooks=[], excludes=["tkinter", "matplotlib", "numpy", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], [], exclude_binaries=True,
    name="MXSJScriptEditor", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False, disable_windowed_traceback=False,
    target_arch=None,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="MXSJScriptEditor")
