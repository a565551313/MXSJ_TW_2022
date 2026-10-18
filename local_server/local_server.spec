# Build on Windows only. The console needs an external --config file.
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root / "src")],
    binaries=[], datas=[], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="MXSJLocalServer", debug=False, strip=False, upx=False, console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="MXSJLocalServer")
