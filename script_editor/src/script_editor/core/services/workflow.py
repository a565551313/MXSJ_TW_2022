"""Immutable preview/commit/rebase workflow, independent of Qt widgets."""

from __future__ import annotations

import difflib
import hashlib
import tempfile
import zlib
from dataclasses import dataclass, replace
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..compiler.runner import Compiler, audit_standard, compile_standard
from ..inspection.native import inspect_module
from ..inspection.references import inspect_references
from ..project.document import Binding
from ..project.storage import CatalogRef, ProjectState
from ..vm.py25 import codec as py25
from ..vm.py27 import codec as py27
from .native_build import Replacement, build_package, encode_replacement


def text_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    binding: Binding
    text: str
    vm: str
    reference: bool = False
    unsaved: bool = False


@dataclass(frozen=True)
class PreparedBuild:
    snapshot: Snapshot
    compiler: Compiler
    replacement: Replacement
    catalog: CatalogRef | None
    filename: bytes
    source_sha256: str
    standard_sha256: str
    old_stored_size: int
    new_stored_size: int
    payload_changed: bool
    diff: str
    hints: tuple = ()


def prepare_build(
    snapshot: Snapshot, compiler: Compiler, catalog=None, baseline_text=None
):
    binding = snapshot.binding
    if snapshot.reference or snapshot.vm != binding.vm or compiler.vm != binding.vm:
        raise ValueError("参考稿或VM不匹配，禁止构建")
    with ArchiveDocument(binding.archive) as archive:
        binding.verify(archive)
        _, filename, profile = inspect_module(archive, binding.index, catalog)
        if binding.filename_hex and bytes.fromhex(binding.filename_hex) != filename:
            raise ValueError("关联的嵌入文件名发生变化，拒绝编译")
        with tempfile.TemporaryDirectory(prefix="mxscript-prepare-") as temp:
            path = Path(temp) / "fresh.pyc"
            compile_standard(compiler, snapshot.text, filename, path)
            pyc = path.read_bytes()
        audit_standard(compiler, pyc)
        replacement = Replacement(binding.index, binding.identity, pyc)
        native = encode_replacement(archive, replacement, profile)
        if binding.vm == "py25":
            from ..vm.compression import inflate

            restored = py25.decode(
                profile.crypt(inflate(native)), header=pyc[:8], padding=True
            )
            stored = native
        else:
            restored, stored = py27.decode(native), zlib.compress(native, 9)[2:-4]
        if restored != pyc:
            raise ValueError("预编译原生往返未全字节相等；不允许进入写包确认")
        old = archive.read_stored(binding.index)
    if (
        baseline_text is not None
        and text_sha(baseline_text) != binding.built_source_sha256
    ):
        raise ValueError("会话源码差异基线已过期")
    diff = (
        "无可靠旧源码文本基线，仅比较摘要；不使用反编译稿作为基线。"
        if baseline_text is None
        else "".join(
            difflib.unified_diff(
                baseline_text.splitlines(True),
                snapshot.text.splitlines(True),
                fromfile="上次成功构建源码",
                tofile="当前编辑区",
            )
        )
    )
    return PreparedBuild(
        snapshot,
        compiler,
        replacement,
        catalog,
        filename,
        text_sha(snapshot.text),
        hashlib.sha256(pyc).hexdigest(),
        len(old),
        len(stored),
        old != stored,
        diff,
        inspect_references(snapshot.text),
    )


def publish_build(
    plan: PreparedBuild, destination: Path, state: ProjectState, *, protected=()
):
    """No mutation: failures leave caller's source, bindings and baselines intact."""
    binding = plan.snapshot.binding
    if (
        plan.snapshot.reference
        or plan.snapshot.vm != binding.vm
        or plan.compiler.vm != binding.vm
        or text_sha(plan.snapshot.text) != plan.source_sha256
        or hashlib.sha256(plan.replacement.standard_pyc).hexdigest()
        != plan.standard_sha256
        or (plan.replacement.index, plan.replacement.identity)
        != (binding.index, binding.identity)
    ):
        raise ValueError("预编译清单快照不一致")
    keys = [(b.archive, b.index) for b in state.bindings]
    if len(keys) != len(set(keys)) or len({c.archive for c in state.catalogs}) != len(
        state.catalogs
    ):
        raise ValueError("项目存在重复关联")
    if binding not in state.bindings or not plan.payload_changed:
        raise ValueError("关联已过期或无存储改动，不生成新包")
    with ArchiveDocument(binding.archive) as archive:
        for item in state.bindings:
            if item.archive == binding.archive:
                item.verify(archive)
        if plan.catalog is not None and plan.catalog not in state.catalogs:
            raise ValueError("XOR目录关联已过期")
        _, filename, profile = inspect_module(archive, binding.index, plan.catalog)
        if filename != plan.filename:
            raise ValueError("原模块嵌入文件名已变化")
    protected = tuple(protected) + tuple(
        p for b in state.bindings for p in (b.archive, b.source)
    )
    protected += tuple(c.path for c in state.catalogs)
    report = build_package(
        binding.archive,
        destination,
        source_sha256=binding.fingerprint,
        replacements=(plan.replacement,),
        compiler=plan.compiler,
        profiles={} if profile is None else {binding.index: profile},
        protected=protected,
    )
    # Pure metadata transition; source files and dirty editor buffers are NOT saved.
    bindings, catalogs = [], []
    for item in state.bindings:
        if item.archive == binding.archive:
            item = replace(
                item, archive=report.output.resolve(), fingerprint=report.output_sha256
            )
            if item.index == binding.index:
                item = replace(
                    item,
                    filename_hex=plan.filename.hex(),
                    built_source_sha256=plan.source_sha256,
                )
        bindings.append(item)
    for ref in state.catalogs:
        if ref.archive == binding.archive:
            ref = replace(
                ref, archive=report.output.resolve(), fingerprint=report.output_sha256
            )
        catalogs.append(ref)
    return report, ProjectState(tuple(bindings), tuple(catalogs))
