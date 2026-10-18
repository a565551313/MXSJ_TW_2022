# Windows GUI entry; CLI/headless source deployment remains available.
import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path(SPECPATH)
onefile = os.environ.get("WEB_SERVER_ONEFILE") == "1"
a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[(str(root / "src/mxsj_web_server/data"), "mxsj_web_server/data"),
           (str(root / "src/mxsj_web_server/web/admin/static"), "mxsj_web_server/web/admin/static")],
    hiddenimports=collect_submodules("mxsj_web_server"),
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries if onefile else [], a.datas if onefile else [],
    exclude_binaries=not onefile,
    name="MXSJWebServer", debug=False, strip=False, upx=False, console=False,
)
if not onefile:
    coll = COLLECT(
        exe, a.binaries, a.datas, strip=False, upx=False, name="MXSJWebServer"
    )
