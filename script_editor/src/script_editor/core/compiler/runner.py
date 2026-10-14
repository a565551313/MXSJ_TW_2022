"""Exact-version subprocess compiler. No imports/execution of target modules."""

from __future__ import annotations

import codecs
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..services.files import atomic_write, guard_output
from .profiles import PROFILES

PROBE = (
    'import sys,imp;sys.stdout.write("%d.%d.%d %s %d" % '
    '(sys.version_info[:3]+("".join("%02x" % ord(c) for c in imp.get_magic()),'
    "(64 if sys.maxint > 2147483647 else 32))))"
)
DATA = Path(__file__).resolve().parents[2] / "data"


class CompilerError(ValueError):
    pass


@dataclass(frozen=True)
class Compiler:
    executable: Path
    vm: str
    version: str
    bits: int
    sha256: str


def _run(executable: Path, args: list[str], cwd: Path):
    try:
        result = subprocess.run(
            [str(executable), "-E", "-S", *args],
            cwd=cwd,
            capture_output=True,
            timeout=30,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CompilerError("编译器启动失败或超过30秒") from exc
    if result.returncode:
        # The helper emits coordinates, never source lines or string values.
        detail = result.stderr.decode("ascii", errors="replace")[:200]
        raise CompilerError(f"编译器退出码{result.returncode}：{detail}")
    return result.stdout


def inspect_compiler(executable: Path, vm: str) -> Compiler:
    profile = PROFILES[vm]
    executable = Path(executable).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="mxscript-probe-") as temp:
        output = _run(executable, ["-c", PROBE], Path(temp))
    expected = f"{profile.version} {profile.magic.hex()} "
    if output not in {(expected + "32").encode(), (expected + "64").encode()}:
        raise CompilerError(f"必须使用标准CPython {profile.version}，版本或魔数不符")
    bits = int(output.split()[-1])
    if sys.platform == "win32" and bits != 32:
        raise CompilerError("Windows发行版要求x86编译器")
    return Compiler(
        executable,
        vm,
        profile.version,
        bits,
        hashlib.sha256(executable.read_bytes()).hexdigest(),
    )


def bundled_compiler(vm: str, root: Path) -> Compiler:
    """Manifest has actual artifacts only. Empty manifest means unavailable."""
    try:
        manifest = json.loads(
            (root / "runtimes" / "manifest.json").read_text(encoding="utf-8-sig")
        )
    except (OSError, ValueError) as exc:
        raise CompilerError("内置编译器清单缺失或无效；编译禁用") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != 1
        or not isinstance(manifest.get("compilers"), list)
    ):
        raise CompilerError("不支持的编译器清单格式；编译禁用")
    candidates = [
        item
        for item in manifest["compilers"]
        if item["vm"] == vm and item["platform"] == sys.platform
    ]
    if len(candidates) != 1:
        raise CompilerError("未安装/未验证此VM的内置编译器；编译禁用")
    item = candidates[0]
    base = (root / "runtimes").resolve()
    exe = (base / item["executable"]).resolve(strict=True)
    if not exe.is_relative_to(base):
        raise CompilerError("编译器清单路径越界")
    # Check digest BEFORE launching any executable named by a manifest.
    if hashlib.sha256(exe.read_bytes()).hexdigest() != item["sha256"]:
        raise CompilerError("内置编译器SHA256不匹配")
    return inspect_compiler(exe, vm)


def compile_standard(
    compiler: Compiler,
    source: str,
    filename: str,
    destination: Path,
    protected: tuple[Path, ...] = (),
) -> str:
    """Compile UTF-8 text to a standard pyc, NOT a native encrypted payload."""
    if destination.suffix.lower() != ".pyc":
        raise CompilerError("这里只能生成标准.pyc，不是原生包")
    for line in source.splitlines()[:2]:
        declaration = re.match(r"^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)", line)
        if declaration and codecs.lookup(declaration.group(1)).name != "utf-8":
            raise CompilerError(
                "编辑器源码是UTF-8；请显式修正文件头编码，不做整文件Big5/GBK转码"
            )
    guard_output(destination, (*protected, compiler.executable))
    fresh = inspect_compiler(compiler.executable, compiler.vm)
    if fresh != compiler:
        raise CompilerError("编译器在检查后发生变化，拒绝编译")
    helper = DATA / "compile_legacy.py"
    with tempfile.TemporaryDirectory(prefix="mxscript-compile-") as temp:
        work = Path(temp)
        src, pyc = work / "source.py", work / "standard.pyc"
        src.write_bytes(source.encode("utf-8"))
        # ASCII descriptor lets a legacy runtime handle Unicode source filenames.
        logical = work / "filename.txt"
        logical.write_bytes(filename.encode("utf-8"))
        _run(compiler.executable, [str(helper), str(src), str(pyc), str(logical)], work)
        data = pyc.read_bytes()
    if len(data) < 9 or data[:4] != PROFILES[compiler.vm].magic:
        raise CompilerError("编译产物魔数或头长度不符")
    if data[4:8] != struct.pack("<I", 0):
        raise CompilerError("编译产物时间戳不符")
    atomic_write(destination, data, (*protected, compiler.executable, helper))
    return hashlib.sha256(data).hexdigest()


def audit_standard(compiler: Compiler, pyc: bytes) -> None:
    """Marshal-read only authored output with the exact runtime, no target exec."""
    if pyc[:4] != PROFILES[compiler.vm].magic:
        raise CompilerError("audit VM/magic mismatch")
    if inspect_compiler(compiler.executable, compiler.vm) != compiler:
        raise CompilerError("compiler changed before marshal audit")
    with tempfile.TemporaryDirectory(prefix="mxscript-audit-") as temp:
        work = Path(temp)
        path = work / "authored.pyc"
        path.write_bytes(pyc)
        _run(compiler.executable, [str(DATA / "audit_legacy.py"), str(path)], work)
