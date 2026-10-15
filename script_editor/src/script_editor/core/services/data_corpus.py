"""Build an external VM2.7 candidate cache; never execute recovered code.

Only data/FLS entries, using the existing strict codec and isolated parsers.
A new destination is reserved; a usable manifest is published LAST. Cancelled
or failed runs retain an INCOMPLETE marker and are never silently imported.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

from ..compiler.runner import CompilerError, compile_standard
from ..inspection.native import inspect_module
from .corpus_manifest import MAX_ROW, load_corpus
from .files import publish_new
from .module_browser import recover_standard
from .recovery_process import RecoveryCancelled


def build_data_corpus(
    archive, destination, *, pycdc=None, compiler=None, timeout=10, cancel=None
):
    if archive.vm != "py27" or archive.kind != "flsdata":
        raise ValueError("此入口仅构建data.fls VM2.7语料，不重跑script全量研究语料")
    if not 0 < timeout <= 120:
        raise ValueError("单引擎超时必须在0到120秒之间")
    if compiler is not None and compiler.vm != "py27":
        raise ValueError("data语法检查必须用标准2.7.13，不使用2.5编译器")

    def cancelled():
        if cancel is not None and cancel.is_set():
            raise RecoveryCancelled("data语料生成已取消；原包未修改，未发布可用清单")

    cancelled()
    fingerprint = archive.fingerprint()
    root = Path(destination).absolute()
    root.mkdir(exist_ok=False)  # No replacement, including existing symlinks.
    incomplete = root / "INCOMPLETE.txt"
    publish_new(
        incomplete, b"Unfinished candidate cache. Do not import.\n", (archive.path,)
    )
    full = root / "full"
    full.mkdir()
    rows, counts = [], Counter()
    syntax = Counter()
    for entry in archive.entries:
        cancelled()
        row = dict(
            schema_version=1,
            index_base=0,
            archive_sha256=fingerprint,
            archive_vm="py27",
            entry_index=entry.index,
            entry_identity=entry.identity,
            directory=entry.directory,
            status="directory" if entry.directory else "failed",
            engines={},
            artifacts=[],
        )
        rows.append(row)
        if entry.directory:
            counts["directory"] += 1
            continue  # Do not read a directory's payload or invoke a parser.
        base = full / "entries" / f"{entry.index:04d}"

        def artifact(name, raw, base=base):
            if len(raw) > 8 * 1024 * 1024:
                raise ValueError("data候选产物超过8MiB；未发布可用清单")
            target = base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            publish_new(target, raw, (archive.path,))
            return dict(
                path=target.relative_to(root).as_posix(),
                bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(),
            )

        try:
            standard, filename, _ = inspect_module(archive, entry.index)
            row["artifacts"].append(artifact("standard.pyc", standard))
            counts["strict_decoded"] += 1
            result = recover_standard(
                standard, "py27", timeout=timeout, pycdc=pycdc, cancel=cancel
            )
        except RecoveryCancelled:
            raise
        except (OSError, ValueError, KeyError) as exc:
            row["diagnostics"] = [str(exc)]
            counts["failed"] += 1
            continue
        for candidate in result["candidates"]:
            data = dict(
                engine_version=candidate.version,
                status=candidate.status
                if candidate.status in {"complete", "partial", "timeout", "failed"}
                else "failed",
                process_status=candidate.status,
                has_source_body=bool(candidate.source),
                raw_invalid_utf8=False,
                raw_kind=candidate.raw_kind,
                binary_sha256=candidate.binary_sha256,
                source_sha256=candidate.source_sha256,
                diagnostics=list(candidate.diagnostics),
                candidates=[],
            )
            try:
                candidate.stdout.decode("utf8", "strict")
            except UnicodeDecodeError:
                data["raw_invalid_utf8"] = True
            for key, raw in (
                ("stdout", candidate.stdout),
                ("stderr", candidate.stderr),
                ("trace_stdout", candidate.trace_stdout),
            ):
                data[key] = artifact(f"raw/{candidate.engine}/{key}", raw)
            if candidate.source:
                ref = artifact(
                    f"candidates/{candidate.engine}/display.py",
                    candidate.source.encode("utf8"),
                )
                ref.update(
                    candidate_kind="source_heuristic",
                    transform="editor-rendered-draft; raw output kept separately",
                    syntax_checks={},
                )
                if compiler is not None:
                    cancelled()
                    with tempfile.TemporaryDirectory(prefix="mx-data-syntax-") as temp:
                        try:
                            compile_standard(
                                compiler,
                                candidate.source,
                                filename,
                                Path(temp) / "syntax.pyc",
                            )
                            checked = {"status": "pass"}
                        except CompilerError as exc:
                            checked = {"status": "fail", "diagnostic": str(exc)}
                    ref["syntax_checks"][compiler.version] = {"result": checked}
                    syntax[checked["status"]] += 1
                data["candidates"].append(ref)
            row["engines"][candidate.engine] = data
        candidates = result["candidates"]
        row["status"] = (
            "complete"
            if any(c.complete for c in candidates)
            else "partial"
            if any(c.source for c in candidates)
            else "failed"
        )
        counts[row["status"]] += 1
        if any(c.source for c in candidates):
            counts["editable_candidates"] += 1
        if any(
            r.get("syntax_checks", {}).get("2.7.13", {}).get("result", {}).get("status")
            == "pass"
            for data in row["engines"].values()
            for r in data["candidates"]
        ):
            counts["entries_with_syntax_pass"] += 1
        counts["both_engines"] += int(len(candidates) == 2)
    cancelled()
    archive._assert_unchanged()
    summary = dict(
        schema=1,
        archive_sha256=fingerprint,
        archive_vm="py27",
        entries=len(rows),
        counts=dict(counts),
        candidate_syntax=dict(syntax),
        compiler=compiler.version if compiler else None,
        target_executed=False,
        semantic_verification=False,
    )
    lines = [json.dumps(row, ensure_ascii=False).encode("utf8") + b"\n" for row in rows]
    if any(len(line) > MAX_ROW for line in lines):
        raise ValueError("data语料行超过导入限制；未发布可用清单")
    publish_new(
        root / "summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2).encode("utf8"),
    )
    manifest = full / "manifest.audited.jsonl"
    cancelled()
    publish_new(manifest, b"".join(lines), (archive.path,))
    index = load_corpus(archive, manifest)
    incomplete.unlink()
    return index, summary
