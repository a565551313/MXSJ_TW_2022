# Console-only offline demonstration; Windows build required.
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "run.py")], pathex=[str(root / "src")],
    binaries=[], datas=[], hiddenimports=[], hookspath=[],
    hooksconfig={}, runtime_hooks=[], excludes=["tkinter", "numpy", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="MXSJNativeChannel",
    debug=False, strip=False, upx=False, console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               name="MXSJNativeChannel")
