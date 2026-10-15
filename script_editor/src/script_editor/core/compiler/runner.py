"""Exact-version subprocess compiler. No imports/execution of target modules."""

from __future__ import annotations

import codecs
import hashlib
import re
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..services.files import atomic_write, guard_output
from .bundles import BundleError, BundlePin, digest_file, load_bundle
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
    bundle: BundlePin | None = None

    @property
    def protected(self):
        return self.bundle.protected if self.bundle else (self.executable,)


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


def _verify_bundle(bundle):
    if bundle is not None:
        try:
            bundle.verify()
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise CompilerError(f"内置编译器整套审计失败：{exc}") from exc


def inspect_compiler(
    executable: Path, vm: str, *, bundle: BundlePin | None = None
) -> Compiler:
    profile = PROFILES[vm]
    _verify_bundle(bundle)
    if bundle is not None and (
        bundle.vm != vm or bundle.executable.resolve() != Path(executable).resolve()
    ):
        raise CompilerError("内置编译器来源关联不符")
    executable = Path(executable).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="mxscript-probe-") as temp:
        output = _run(executable, ["-c", PROBE], Path(temp))
    _verify_bundle(bundle)
    expected = f"{profile.version} {profile.magic.hex()} "
    if output not in {(expected + "32").encode(), (expected + "64").encode()}:
        raise CompilerError(f"必须使用标准CPython {profile.version}，版本或魔数不符")
    bits = int(output.split()[-1])
    if sys.platform == "win32" and bits != 32:
        raise CompilerError("Windows发行版要求x86编译器")
    executable_sha = digest_file(executable)
    if bundle is not None and executable_sha != dict(bundle.files)["python.exe"]:
        raise CompilerError("内置编译器EXE在探测后发生变化")
    return Compiler(
        executable,
        vm,
        profile.version,
        bits,
        executable_sha,
        bundle,
    )


def bundled_compiler(vm: str, root: Path) -> Compiler:
    """Verify every runtime file before invoking its exact standard compiler."""
    if sys.platform != "win32":
        raise CompilerError("内置运行时仅供Windows x86；此平台不能执行")
    try:
        pin = load_bundle(vm, root)
    except BundleError as exc:
        raise CompilerError(str(exc)) from exc
    return inspect_compiler(pin.executable, vm, bundle=pin)


def compile_standard(
    compiler: Compiler,
    source: str,
    filename: str | bytes,
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
    guard_output(destination, (*protected, *compiler.protected))
    fresh = inspect_compiler(compiler.executable, compiler.vm, bundle=compiler.bundle)
    if fresh != compiler:
        raise CompilerError("编译器在检查后发生变化，拒绝编译")
    helper = DATA / "compile_legacy.py"
    with tempfile.TemporaryDirectory(prefix="mxscript-compile-") as temp:
        work = Path(temp)
        src, pyc = work / "source.py", work / "standard.pyc"
        src.write_bytes(source.encode("utf-8"))
        # ASCII descriptor lets a legacy runtime handle Unicode source filenames.
        logical = work / "filename.txt"
        logical.write_bytes(
            filename if isinstance(filename, bytes) else filename.encode("utf-8")
        )
        _verify_bundle(compiler.bundle)
        _run(compiler.executable, [str(helper), str(src), str(pyc), str(logical)], work)
        data = pyc.read_bytes()
        _verify_bundle(compiler.bundle)
    if len(data) < 9 or data[:4] != PROFILES[compiler.vm].magic:
        raise CompilerError("编译产物魔数或头长度不符")
    if data[4:8] != struct.pack("<I", 0):
        raise CompilerError("编译产物时间戳不符")
    atomic_write(destination, data, (*protected, *compiler.protected, helper))
    return hashlib.sha256(data).hexdigest()


def audit_standard(compiler: Compiler, pyc: bytes) -> None:
    """Marshal-read only authored output with the exact runtime, no target exec."""
    if pyc[:4] != PROFILES[compiler.vm].magic:
        raise CompilerError("audit VM/magic mismatch")
    if (
        inspect_compiler(compiler.executable, compiler.vm, bundle=compiler.bundle)
        != compiler
    ):
        raise CompilerError("compiler changed before marshal audit")
    with tempfile.TemporaryDirectory(prefix="mxscript-audit-") as temp:
        work = Path(temp)
        path = work / "authored.pyc"
        path.write_bytes(pyc)
        _verify_bundle(compiler.bundle)
        _run(compiler.executable, [str(DATA / "audit_legacy.py"), str(path)], work)
        _verify_bundle(compiler.bundle)
