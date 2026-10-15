"""Audit/copy exactly two declared runtimes. Never download or invent binaries."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from .bundles import BundleError, _plain_directory, digest_file, load_bundle
from .runner import audit_standard, bundled_compiler, compile_standard


def audit_runtimes(root: Path, *, execute=False):
    pins = tuple(load_bundle(vm, root) for vm in ("py25", "py27"))
    if pins[0].manifest_sha256 != pins[1].manifest_sha256:
        raise BundleError("两套运行时读取了不同版本清单")
    records = []
    for pin in pins:
        record = {
            "vm": pin.vm,
            "manifest_sha256": pin.manifest_sha256,
            "files": dict(pin.files),
            "execution": "not-executed",
        }
        if execute:
            if sys.platform != "win32":
                raise BundleError("Windows运行时执行验收只能在真实Windows进行")
            compiler = bundled_compiler(pin.vm, root)
            with tempfile.TemporaryDirectory(prefix="mxscript-runtime-smoke-") as temp:
                work = Path(temp)
                sentinel = work / "must-not-execute"
                # This source is compiled, never executed. The logical filename
                # separately exercises exact non-UTF8 bytes in compile().
                source = (
                    "# coding: utf-8\ntitle=u'測試'\n"
                    "def outer(x):\n def inner(y):\n  return x+y\n return inner\n"
                    f"open({str(sentinel)!r},'w').write('EXECUTED')\n"
                    "raise RuntimeError('DO NOT EXECUTE')\n"
                )
                output = work / "smoke.pyc"
                compile_standard(compiler, source, b"login/\xff-test.py", output)
                audit_standard(compiler, output.read_bytes())
                if sentinel.exists():
                    raise BundleError("严重错误：编译验收执行了目标源码")
                record["standard_pyc_sha256"] = digest_file(output)
            record.update(
                version=compiler.version,
                bits=compiler.bits,
                execution="compile-and-marshal-only-passed",
            )
        pin.verify()
        records.append(record)
    for pin in pins:
        pin.verify()
    return {
        "schema": 1,
        "status": "windows-runtime-smoke-passed" if execute else "static-only",
        "native_game_acceptance": "not-tested",
        "provenance": "local manifest declarations; not a signature/build proof",
        "compilers": records,
    }


def stage_runtimes(source: Path, destination: Path, *, execute=False):
    """Create a NEW runtimes folder in an existing application distribution.

    Refuse all preexisting targets; copy exact manifest-listed files, validate the
    copied bytes again, and remove only the directory created by this attempt on
    failure. No GUI EXE or existing runtime tree is deleted here.
    """
    audit_runtimes(source, execute=False)
    pins = tuple(load_bundle(vm, source) for vm in ("py25", "py27"))
    if pins[0].manifest_sha256 != pins[1].manifest_sha256:
        raise BundleError("复制前清单发生变化")
    _plain_directory(destination)
    source_base = (source / "runtimes").resolve()
    if destination.resolve().is_relative_to(source_base):
        raise BundleError("发行目标不能位于输入运行时目录内")
    target = destination / "runtimes"
    target.mkdir()  # Exclusive: never remove/replace a directory we did not create.
    try:
        for pin in pins:
            for name, _ in pin.files:
                relative = pin.root.relative_to(pin.manifest.parent) / name
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(pin.root / name, path)
        shutil.copyfile(pins[0].manifest, target / "manifest.json")
        if digest_file(target / "manifest.json") != pins[0].manifest_sha256:
            raise BundleError("复制期间runtime清单发生变化")
        for pin in pins:
            pin.verify()
        return audit_runtimes(destination, execute=execute)
    except Exception:
        shutil.rmtree(target)
        raise
