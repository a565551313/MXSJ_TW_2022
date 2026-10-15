# -*- mode: python ; coding: utf-8 -*-
"""Independent GPL recovery program; does not import/link the editor package."""
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

a = Analysis(
    ["src/script_editor/data/recovery_worker.py"], pathex=[], binaries=[], datas=sum(
        (copy_metadata(name) for name in ("uncompyle6", "xdis", "spark-parser", "six", "click")), []
    ),
    hiddenimports=(collect_submodules("uncompyle6") + collect_submodules("xdis")
                   + collect_submodules("spark_parser")),
    hookspath=[], runtime_hooks=[], excludes=["PySide6", "script_editor", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], [], exclude_binaries=True,
          name="MXSJRecoveryWorker", console=False, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name="MXSJRecoveryWorker", upx=False)
