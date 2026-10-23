"""Schema1/2 associations and schema3 embedded edit snapshots; no compiler paths."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..services.corpus_manifest import CorpusRef
from ..services.files import atomic_write, read_source
from ..vm.py25.keys import read_catalog
from .document import Binding
from .workspace import EditorState, pack_editor, unpack_editor


@dataclass(frozen=True)
class CatalogRef:
    archive: Path
    fingerprint: str
    path: Path
    sha256: str

    def verify(self, archive):
        if (
            archive.path != self.archive.resolve()
            or archive.fingerprint() != self.fingerprint
        ):
            raise ValueError("XOR目录的包来源已过期")
        if hashlib.sha256(read_catalog(self.path)).hexdigest() != self.sha256:
            raise ValueError("XOR目录文件发生变化，须重新确认来源")


@dataclass(frozen=True)
class ProjectState:
    bindings: tuple[Binding, ...]
    catalogs: tuple[CatalogRef, ...] = ()
    editors: tuple[EditorState, ...] = ()
    corpora: tuple[CorpusRef, ...] = ()


def _digest(value):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise ValueError("非法SHA256")


def save_state(path: Path, bindings, catalogs=(), *, editors=(), corpora=()):
    bindings, catalogs = tuple(bindings), tuple(catalogs)
    editors, corpora = tuple(editors), tuple(corpora)
    if len(editors) > 128 or len(corpora) > 128:
        raise ValueError("项目工作区条目过多")
    estimated = 0
    for editor in editors:
        estimated += len(editor.text.encode("utf8"))
        if editor.report is not None:
            estimated += len(editor.report.source.encode("utf8")) + len(
                editor.report.disassembly.encode("utf8")
            )
            for candidate in editor.report.candidates:
                estimated += len(candidate.source.encode("utf8"))
                estimated += sum(
                    len(raw) * 2
                    for raw in (
                        candidate.stdout,
                        candidate.stderr,
                        candidate.trace_stdout,
                    )
                )
    if estimated > 48 * 1024 * 1024:
        raise ValueError("项目缓冲区过大，请拆分工作区；编辑仍保留")
    if not path.name.endswith(".mxscript.json"):
        raise ValueError("项目文件必须为.mxscript.json")

    def portable(target):
        try:
            return os.path.relpath(target, path.parent)
        except ValueError:  # Different Windows volumes cannot have a relative path.
            return str(target.resolve())

    rows, refs = [], []
    for binding in bindings:
        row = asdict(binding)
        row["archive"] = portable(binding.archive)
        row["source"] = portable(binding.source)
        row["status"] = "user-associated-not-native-verified"
        rows.append(row)
    for catalog in catalogs:
        row = asdict(catalog)
        row["archive"] = portable(catalog.archive)
        row["path"] = portable(catalog.path)
        refs.append(row)
    protected = [p for b in bindings for p in (b.archive, b.source)]
    protected += [p for c in catalogs for p in (c.archive, c.path)]
    corpus_rows = []
    for ref in corpora:
        corpus_rows.append(
            {
                "archive": portable(ref.archive),
                "fingerprint": ref.fingerprint,
                "path": portable(ref.path),
                "sha256": ref.sha256,
            }
        )
    protected += [e.path for e in editors]
    protected += [e.report.archive for e in editors if e.report is not None]
    protected += [
        e.report.target_archive
        for e in editors
        if e.report is not None and e.report.target_archive is not None
    ]
    protected += [p for c in corpora for p in (c.archive, c.path)]
    if any(
        path.resolve().is_relative_to(c.path.parent.parent.resolve()) for c in corpora
    ):
        raise ValueError("语料目录只读；请在其外部保存项目")
    doc = {"schema": 3 if editors or corpora else 2, "bindings": rows, "catalogs": refs}
    if doc["schema"] == 3:
        doc.update(
            editors=[pack_editor(e, portable) for e in editors], corpora=corpus_rows
        )
    raw = json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError("项目超过64MiB，请拆分工作区；未保存的编辑仍保留")
    atomic_write(path, raw, protected)


def load_state(path: Path) -> ProjectState:
    with path.open("rb") as stream:
        raw = stream.read(64 * 1024 * 1024 + 1)
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError("项目超过64MiB")
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except RecursionError as exc:
        raise ValueError("项目嵌套过深") from exc
    if (
        not isinstance(doc, dict)
        or type(doc.get("schema")) is not int
        or doc.get("schema") not in (1, 2, 3)
        or not isinstance(doc.get("bindings"), list)
    ):
        raise ValueError("不支持的项目格式")
    bindings, catalogs, archives, seen = [], [], {}, set()

    def archive(name):
        target = (path.parent / name).resolve(strict=True)
        if target not in archives:
            archives[target] = ArchiveDocument(target)
        return archives[target]

    try:
        snapshots = (
            {
                (path.parent / row["path"]).resolve(): row
                for row in doc.get("editors", [])
            }
            if doc["schema"] == 3
            else {}
        )
        for row in doc["bindings"]:
            source = (path.parent / row["source"]).resolve()
            if source not in snapshots:
                read_source(
                    source
                )  # Legacy/unopened sources still need disk preflight.
            # Embedded snapshots are fully validated below before returning any state.
            a = archive(row["archive"])
            if row["vm"] not in {"py25", "py27"} or type(row["index"]) is not int:
                raise ValueError("非法VM/条目下标")
            _digest(row["fingerprint"])
            filename, baseline = (
                row.get("filename_hex", ""),
                row.get("built_source_sha256", ""),
            )
            if not isinstance(filename, str) or len(filename) > 16384:
                raise ValueError("非法嵌入文件名")
            bytes.fromhex(filename)
            if baseline:
                _digest(baseline)
            kind = row.get("source_kind", "authored")
            recovery_sha = row.get("recovery_sha256", "")
            if not isinstance(kind, str) or kind not in {
                "authored",
                "recovered-reviewed",
            }:
                raise ValueError("不支持的源码来源类型，未核验草稿不能写入关联")
            if recovery_sha or kind == "recovered-reviewed":
                _digest(recovery_sha)
            binding = Binding(
                a.path,
                row["fingerprint"],
                row["vm"],
                row["index"],
                row["identity"],
                source,
                filename,
                baseline,
                kind,
                recovery_sha,
            )
            binding.verify(a)
            key = (a.path, binding.index)
            if key in seen:
                raise ValueError("项目中模块关联重复")
            seen.add(key)
            bindings.append(binding)
        seen.clear()
        for row in doc.get("catalogs", []):
            a = archive(row["archive"])
            _digest(row["fingerprint"])
            _digest(row["sha256"])
            ref = CatalogRef(
                a.path,
                row["fingerprint"],
                (path.parent / row["path"]).resolve(strict=True),
                row["sha256"],
            )
            if a.vm != "py25" or a.path in seen:
                raise ValueError("非法或重复XOR目录关联")
            ref.verify(a)
            seen.add(a.path)
            catalogs.append(ref)
        editors, corpora = [], []
        if doc["schema"] == 3:
            for key in ("editors", "corpora"):
                if (
                    not isinstance(doc.get(key, []), list)
                    or len(doc.get(key, [])) > 128
                ):
                    raise ValueError("项目工作区条目非法或过多")
            for row in doc.get("editors", []):
                editor = unpack_editor(row, path.parent, archive, _digest)
                if editor.path in {e.path for e in editors}:
                    raise ValueError("项目编辑区路径重复")
                if editor.source_kind == "recovered-reviewed" and not any(
                    b.source == editor.path
                    and b.source_kind == editor.source_kind
                    and b.vm == editor.vm
                    for b in bindings
                ):
                    raise ValueError("未采用的编辑区不能冒充已核对源码")
                if any(
                    b.source == editor.path
                    and (b.vm != editor.vm or b.source_kind != editor.source_kind)
                    for b in bindings
                ):
                    raise ValueError("项目编辑区与源码关联类型/VM冲突")
                editors.append(editor)
            for row in doc.get("corpora", []):
                a = archive(row["archive"])
                _digest(row["fingerprint"])
                _digest(row["sha256"])
                if (
                    a.vm not in {"py25", "py27"}
                    or a.fingerprint() != row["fingerprint"]
                    or any(c.archive == a.path for c in corpora)
                ):
                    raise ValueError("项目语料来源不符或重复")
                # Missing external corpus does not discard embedded user drafts.
                corpora.append(
                    CorpusRef(
                        a.path,
                        row["fingerprint"],
                        (path.parent / row["path"]).resolve(),
                        row["sha256"],
                    )
                )
        return ProjectState(
            tuple(bindings), tuple(catalogs), tuple(editors), tuple(corpora)
        )
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError("项目结构/字段非法") from exc
    finally:
        for a in archives.values():
            a.close()
