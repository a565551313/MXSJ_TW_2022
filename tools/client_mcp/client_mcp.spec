# -*- mode: python ; coding: utf-8 -*-
"""Windows console build for the stdio MCP server."""
import os

from PyInstaller.utils.hooks import collect_submodules

ONEFILE = os.environ.get("CLIENT_MCP_ONEFILE") == "1"
a = Analysis(
    ["run.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("mxsj_client_mcp"),
    excludes=["tkinter", "matplotlib", "numpy", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries if ONEFILE else [], a.datas if ONEFILE else [],
    [], exclude_binaries=not ONEFILE, name="ClientMCP", debug=False,
    strip=False, upx=False, console=True,
)
if not ONEFILE:
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="ClientMCP")
