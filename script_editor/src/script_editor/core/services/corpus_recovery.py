"""External drafts; exact strict byte reproduction alone admits repair parameters."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from ..inspection.native import inspect_module
from ..vm.compression import inflate
from ..vm.marshal_tree import Code, parse
from ..vm.py25 import codec
from ..vm.py25.keys import KeyProfile, read_catalog
from ..vm.py27 import codec as py27
from .module_browser import ModuleReport
from .recovery_candidates import DRAFT_HEADER, RecoveryCandidate, best_candidate


def standard_ref(row):
    return next(
        (r for r in row["artifacts"] if r["path"].endswith("/standard.pyc")), None
    )


def verified_parameters(index, archive, catalog):
    """Return a NEW catalog's bytes, never mutate or silently install original keys."""
    if archive.vm != "py25":
        raise ValueError("data使用独立VM2.7，无需也不能套用script五段参数")
    catalog.verify(archive)
    raw = read_catalog(catalog.path)
    original = json.loads(raw)
    updated = json.loads(raw)
    accepted, rejected = [], {}
    for entry in index.repair_indices:
        row = index.row(archive, entry)
        tr = row.get("transpile", {})
        try:
            baseline = {k: original[str(entry)][k] for k in ("keys", "bounds")}
            prior = tr["original_parameters"]
            if (
                not isinstance(prior, dict)
                or set(prior) != {"keys", "bounds"}
                or any(
                    not isinstance(prior[k], list)
                    or any(type(v) is not int for v in prior[k])
                    for k in ("keys", "bounds")
                )
                or prior != baseline
            ):
                raise ValueError("原参数与当前确认目录不符")
            ref = standard_ref(row)
            if ref is None:
                raise ValueError("无标准pyc，不采用参数")
            expected = index.artifact(row, ref, 64 * 1024 * 1024)
            expanded = inflate(archive.read_stored(entry))
            profile = KeyProfile(
                archive.fingerprint(),
                entry,
                archive.entries[entry].identity,
                hashlib.sha256(archive.read_stored(entry)).hexdigest(),
                catalog.sha256,
                tuple(tr["keys"]),
                tuple(tr["bounds"]),
                len(expanded),
            )
            profile.validate(archive, entry)
            actual = codec.decode(profile.crypt(expanded), padding=True)
            filename = parse(actual[8:]).fields[5].value
            if not filename or b"\0" in filename or len(filename) > 8192:
                raise ValueError("嵌入文件名不支持")
            if actual != expected:
                raise ValueError("本侧严格解码与语料pyc不完全相同")
            updated[str(entry)].update(
                keys=list(profile.keys), bounds=list(profile.bounds)
            )
            accepted.append(entry)
        except (ValueError, KeyError, TypeError, OSError, AttributeError) as exc:
            rejected[entry] = str(exc)
    archive._assert_unchanged()
    return (
        json.dumps(updated, ensure_ascii=False, indent=2).encode("utf8"),
        tuple(accepted),
        rejected,
    )


def corpus_report(index, archive, entry, catalog=None):
    try:
        return _corpus_report(index, archive, entry, catalog)
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError("语料引擎记录结构非法") from exc


def _corpus_report(index, archive, entry, catalog):
    if archive.vm == "py25" and entry == 1288:
        # The standard browser enforces exclusion before payload/preview.
        from .module_browser import read_module

        return read_module(archive, entry, catalog)
    row = index.row(archive, entry)
    if archive.entries[entry].directory:
        raise ValueError("data目录不是脚本，请选择.pyo条目")
    ref = standard_ref(row)
    candidates, notes = (
        [],
        [
            "外部研究候选；编译记录不代表本机验证或业务语义正确。",
            "阅读/编辑与安全发布分离；不沿用研究转译器的NOP/局部修补。",
        ],
    )
    if archive.vm == "py27":
        diagnostics = row.get("diagnostics", [])
        if not isinstance(diagnostics, list) or any(
            not isinstance(v, str) for v in diagnostics
        ):
            raise ValueError("data语料诊断结构非法")
        notes.extend(diagnostics)
    standard_sha, filename, verified = "", "", False
    candidate_sha = ""
    if ref is not None:
        pyc = index.artifact(row, ref, 64 * 1024 * 1024)
        if (
            pyc[:4] != (codec.MAGIC if archive.vm == "py25" else py27.MAGIC)
            or len(pyc) < 9
            or (archive.vm == "py25" and pyc[4:8] != bytes(4))
        ):
            raise ValueError("语料pyc头不符")
        candidate_sha = hashlib.sha256(pyc).hexdigest()
        code = parse(pyc[8:])
        if not isinstance(code, Code):
            raise ValueError("语料pyc不含模块code")
        name = code.fields[5].value
        if isinstance(name, bytes) and len(name) <= 8192:
            filename = name.hex()
        try:
            actual, strict_name, _ = inspect_module(archive, entry, catalog)
            standard_sha = hashlib.sha256(actual).hexdigest()
            verified = actual == pyc
            if verified:
                filename = strict_name.hex()
            else:
                notes.append("语料pyc与原包严格解码不同，不能当已核验来源采用。")
        except (ValueError, KeyError, OSError) as exc:
            notes.append("原包严格来源尚未接通：" + str(exc))
    for engine, data in row["engines"].items():
        if engine not in {"uncompyle6", "pycdc"}:
            raise ValueError("未知语料引擎")
        raw = index.artifact(row, data["stdout"])
        stderr = index.artifact(row, data["stderr"])
        variants = [
            c
            for c in data["candidates"]
            if c.get("candidate_kind") == "source_heuristic"
        ]
        source, status = "", data["status"]
        if data.get("has_source_body") and variants:
            selected = variants[-1]
            text = index.artifact(row, selected).decode("utf8", "strict")
            if any(
                line.strip() and not line.lstrip().startswith("#")
                for line in text.splitlines()
            ):
                source = (
                    text
                    if text.startswith(
                        DRAFT_HEADER + f"# MXSJ-RECOVERY-VM: {archive.vm}\n"
                    )
                    else DRAFT_HEADER + f"# MXSJ-RECOVERY-VM: {archive.vm}\n" + text
                )
        if status not in {"complete", "partial", "failed", "timeout"}:
            raise ValueError("未知语料状态")
        diagnostics = list(notes)
        if data.get("raw_invalid_utf8") or b"\0" in raw:
            if status == "complete":
                status = "partial"
            diagnostics.append("原输出存在非UTF8/NUL；显示稿不冒充原始字节保真。")
        if not source and status in {"complete", "partial"}:
            status = "failed"
        candidates.append(
            RecoveryCandidate(
                engine,
                data["engine_version"],
                status,
                source,
                tuple(diagnostics + data.get("diagnostics", [])),
                raw,
                stderr,
                data.get("raw_kind", "corpus-engine-bytes"),
                data.get("binary_sha256", ""),
                data.get("source_sha256", ""),
                index.artifact(row, data["trace_stdout"])
                if "trace_stdout" in data
                else b"",
                evidence={
                    "manifest_sha256": index.ref.sha256,
                    "historical_process_status": data.get(
                        "process_status", data["status"]
                    ),
                    "stdout": data["stdout"],
                    "stderr": data["stderr"],
                    "historical_selected_syntax": selected.get("syntax_checks", {})
                    .get("2.5.6" if archive.vm == "py25" else "2.7.13", {})
                    .get("result")
                    if source
                    else None,
                    "variants": [
                        {
                            k: c[k]
                            for k in ("path", "sha256", "bytes", "transform")
                            if k in c
                        }
                        for c in variants
                    ],
                    "historical_raw_syntax_checks": {
                        k: v.get("result")
                        for k, v in data.get("raw_syntax_checks", {}).items()
                        if isinstance(v, dict)
                    },
                },
            )
        )
    syntax_preferred = [
        c
        for c in candidates
        if c.source
        and (c.evidence or {}).get("historical_selected_syntax", {})
        and c.evidence["historical_selected_syntax"].get("status") == "pass"
    ]
    selected = best_candidate(syntax_preferred or candidates) if candidates else None
    report = ModuleReport(
        archive.path,
        archive.fingerprint(),
        entry,
        archive.entries[entry].identity,
        archive.vm,
        filename,
        standard_sha,
        selected.source if selected else "",
        selected.complete if selected else False,
        "",
        tuple(notes),
        "",
        tuple(candidates),
        selected.engine if selected else "",
    )
    return replace(
        report,
        corpus_manifest_sha256=index.ref.sha256,
        candidate_pyc_sha256=candidate_sha,
        origin_verified=verified,
    )
