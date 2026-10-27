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
from .native_build import (
    Replacement,
    build_package,
    encode_replacement_detailed,
)


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
    resized: bool = False


def prepare_build(
    snapshot: Snapshot,
    compiler: Compiler,
    catalog=None,
    baseline_text=None,
    *,
    allow_resize=False,
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
        encoded = encode_replacement_detailed(
            archive, replacement, profile, allow_resize=allow_resize
        )
        native, resized = encoded.stored, encoded.resized
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
        resized,
    )


@dataclass(frozen=True)
class PackagePlan:
    """Several changed modules of ONE package, prepared in a single pass.

    Loose mode writes a whole package's pending edits at once; using one plan
    keeps the "preview first, then commit" property instead of fanning out into
    independent publishes that could half-succeed.
    """

    archive: Path
    vm: str
    compiler: Compiler
    catalog: CatalogRef | None
    entries: tuple[PreparedBuild, ...]
    #: ``(index, source_sha256)`` for modules that compiled to the bytes the
    #: package already holds. Their new text *is* what is stored now, so a
    #: caller may refresh ``built_source_sha256`` and stop re-compiling them.
    unchanged: tuple[tuple[int, str], ...] = ()

    @property
    def indexes(self):
        return tuple(entry.snapshot.binding.index for entry in self.entries)

    @property
    def unchanged_indexes(self):
        return tuple(index for index, _ in self.unchanged)

    @property
    def source_sha256(self):
        if not self.entries:
            raise ValueError("清单里没有需要写回的改动")
        return self.entries[0].snapshot.binding.fingerprint


def prepare_package(
    snapshots, compiler, catalog=None, baselines=None, *, allow_resize=False
):
    """Prepare every binding of one package that would change stored bytes."""
    snapshots = tuple(snapshots)
    if not snapshots:
        raise ValueError("没有可写回的源码：请先为条目关联源码")
    archive, vm = snapshots[0].binding.archive, snapshots[0].binding.vm
    seen = set()
    for snapshot in snapshots:
        if snapshot.binding.archive != archive or snapshot.binding.vm != vm:
            raise ValueError("一次写回只能针对同一个包与同一个VM")
        if snapshot.vm != vm or compiler.vm != vm:
            raise ValueError("源码VM与包VM不一致，禁止写回")
        if snapshot.binding.index in seen:
            raise ValueError("同一条目在一次写回里出现了两次")
        seen.add(snapshot.binding.index)
        if snapshot.binding.fingerprint != snapshots[0].binding.fingerprint:
            raise ValueError("关联指向了不同版本的原包，请重新关联")
    baselines = baselines or {}
    entries, unchanged = [], []
    for snapshot in snapshots:
        key = (snapshot.binding.archive, snapshot.binding.index)
        plan = prepare_build(
            snapshot, compiler, catalog, baselines.get(key), allow_resize=allow_resize
        )
        if plan.payload_changed:
            entries.append(plan)
        else:
            unchanged.append((snapshot.binding.index, plan.source_sha256))
    # An empty plan is a normal outcome (e.g. a comment-only edit compiles to
    # the same pyc), not an error: the caller reports "nothing to write" and
    # refreshes the baselines so the next save is quiet too.
    return PackagePlan(
        archive, vm, compiler, catalog, tuple(entries), tuple(unchanged)
    )


def _validate_package_plan(plan: PackagePlan, state: ProjectState):
    if not plan.entries:
        raise ValueError("清单为空")
    keys = [(b.archive, b.index) for b in state.bindings]
    if len(keys) != len(set(keys)) or len({c.archive for c in state.catalogs}) != len(
        state.catalogs
    ):
        raise ValueError("项目存在重复关联")
    if plan.catalog is not None and plan.catalog not in state.catalogs:
        raise ValueError("XOR目录关联已过期")
    for entry in plan.entries:
        binding = entry.snapshot.binding
        if (
            entry.snapshot.reference
            or entry.snapshot.vm != binding.vm
            or entry.compiler.vm != binding.vm
            or entry.snapshot.binding.archive != plan.archive
            or text_sha(entry.snapshot.text) != entry.source_sha256
            or hashlib.sha256(entry.replacement.standard_pyc).hexdigest()
            != entry.standard_sha256
            or (entry.replacement.index, entry.replacement.identity)
            != (binding.index, binding.identity)
            or binding not in state.bindings
        ):
            raise ValueError("预编译清单快照不一致")


def publish_package(
    plan: PackagePlan,
    state: ProjectState,
    destination: Path | None = None,
    *,
    in_place: bool = False,
    backup: bool = True,
    allow_resize: bool = False,
    protected=(),
):
    """Write every prepared module of ``plan`` into one package.

    ``in_place`` overwrites ``plan.archive`` itself (loose mode) after an
    independent readback of the temporary package; otherwise ``destination``
    must be a brand-new file. Either way the original is never half-written.
    """
    _validate_package_plan(plan, state)
    target = Path(plan.archive) if in_place else destination
    if target is None:
        raise ValueError("严格模式必须指定新的输出包名")
    with ArchiveDocument(plan.archive) as archive:
        for item in state.bindings:
            if item.archive == plan.archive:
                item.verify(archive)
        profiles = {}
        for entry in plan.entries:
            index = entry.snapshot.binding.index
            _, filename, profile = inspect_module(archive, index, plan.catalog)
            if filename != entry.filename:
                raise ValueError("原模块嵌入文件名已变化")
            if profile is not None:
                # Key profiles are entry-bound; one package can need several.
                profiles[index] = profile
    protected = tuple(protected) + tuple(
        p for b in state.bindings for p in (b.archive, b.source)
    )
    protected += tuple(c.path for c in state.catalogs)
    report = build_package(
        plan.archive,
        target,
        source_sha256=plan.source_sha256,
        replacements=tuple(entry.replacement for entry in plan.entries),
        compiler=plan.compiler,
        profiles=profiles,
        protected=protected,
        in_place=in_place,
        backup=backup,
        allow_resize=allow_resize,
    )
    # Index -> source digest whose bytes the package now holds. Written entries
    # come from the plan; ``unchanged`` ones compiled to the bytes that were
    # already stored, so their new text is the baseline too. Leaving those stale
    # would make every later save recompile the same modules and keep counting
    # them as candidates. Bindings are unique per (archive, index) — enforced
    # above — so an index identifies exactly one binding.
    written = {entry.snapshot.binding.index: entry for entry in plan.entries}
    same_bytes = dict(plan.unchanged)
    bindings, catalogs = [], []
    for item in state.bindings:
        if item.archive == plan.archive:
            item = replace(
                item,
                archive=report.output.resolve(),
                fingerprint=report.output_sha256,
            )
            entry = written.get(item.index)
            if entry is not None and entry.snapshot.binding.source != item.source:
                entry = None  # Another source file now owns this entry.
            if entry is not None:
                item = replace(
                    item,
                    filename_hex=entry.filename.hex(),
                    built_source_sha256=entry.source_sha256,
                )
            elif item.index in same_bytes:
                item = replace(
                    item, built_source_sha256=same_bytes[item.index]
                )
        bindings.append(item)
    for ref in state.catalogs:
        if ref.archive == plan.archive:
            ref = replace(
                ref,
                archive=report.output.resolve(),
                fingerprint=report.output_sha256,
            )
        catalogs.append(ref)
    return report, ProjectState(tuple(bindings), tuple(catalogs))


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
        # The plan carries the consent: ``resized`` is only ever True when it was
        # prepared with the experimental flag, so publishing must match.
        allow_resize=plan.resized,
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
