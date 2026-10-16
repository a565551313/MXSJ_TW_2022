"""Schema3 edit snapshots, separate from publishable source bindings."""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from pathlib import Path

from ..services.module_browser import ModuleReport
from ..services.recovery_candidates import RecoveryCandidate

MAX_TEXT = 8 * 1024 * 1024 + 4096


@dataclass(frozen=True)
class EditorState:
    path: Path
    vm: str
    source_kind: str
    text: str
    modified: bool
    draft_saved: bool
    report: ModuleReport | None = None


def pack_editor(editor, portable):
    text(editor.text)
    if editor.report and editor.report.vm == "py25" and editor.report.index == 1288:
        raise ValueError("项目不能保存1288恢复内容")
    row = asdict(editor)
    if editor.report is not None:
        text(editor.report.source)
        text(editor.report.disassembly)
        for candidate in editor.report.candidates:
            text(candidate.source)
            if any(
                len(value) > MAX_TEXT
                for value in (
                    candidate.stdout,
                    candidate.stderr,
                    candidate.trace_stdout,
                )
            ):
                raise ValueError("候选原始输出超过项目大小限制")
    row["path"] = portable(editor.path)
    if editor.report is not None:
        row["report"]["archive"] = portable(editor.report.archive)
        for candidate in row["report"]["candidates"]:
            for key in ("stdout", "stderr", "trace_stdout"):
                candidate[key] = base64.b64encode(candidate[key]).decode("ascii")
    return row


def text(value):
    if not isinstance(value, str) or len(value.encode("utf8")) > MAX_TEXT:
        raise ValueError("项目文字超过8MiB或类型错误")
    return value


def unpack_editor(row, parent, archive, check_digest):
    try:
        vm, kind = row["vm"], row["source_kind"]
        if vm not in {"py25", "py27"} or kind not in {
            "authored",
            "reference",
            "recovered-draft",
            "recovered-reviewed",
            "module-unavailable",
        }:
            raise ValueError("项目编辑区类型/VM非法")
        if type(row["modified"]) is not bool or type(row["draft_saved"]) is not bool:
            raise ValueError("项目编辑区状态非法")
        report = row.get("report")
        if report is not None:
            report = dict(report)
            a = archive(report["archive"])
            index = report["index"]
            if (
                type(index) is not int
                or not 0 <= index < len(a.entries)
                or a.fingerprint() != report["fingerprint"]
                or vm != a.vm
                or report["vm"] != vm
                or a.entries[index].identity != report["identity"]
            ):
                raise ValueError("项目恢复来源与原包不符")
            if vm == "py25" and index == 1288:
                raise ValueError("项目不能保存1288恢复内容")
            report["archive"] = a.path
            for key in (
                "standard_sha256",
                "corpus_manifest_sha256",
                "candidate_pyc_sha256",
            ):
                if report.get(key):
                    check_digest(report[key])
            filename = report["filename_hex"]
            if not isinstance(filename, str) or len(filename) > 16384:
                raise ValueError("项目嵌入文件名非法")
            bytes.fromhex(filename)
            for key in ("source", "disassembly", "stored_preview"):
                text(report[key])
            if (
                type(report["complete"]) is not bool
                or type(report.get("origin_verified", True)) is not bool
            ):
                raise ValueError("项目恢复标记非法")
            if (
                not isinstance(report["candidates"], list)
                or len(report["candidates"]) > 8
            ):
                raise ValueError("项目候选过多")
            candidates = []
            for candidate in report["candidates"]:
                candidate = dict(candidate)
                text(candidate["source"])
                if candidate["engine"] not in {"uncompyle6", "pycdc"}:
                    raise ValueError("项目引擎非法")
                for key in ("stdout", "stderr", "trace_stdout"):
                    encoded = candidate[key]
                    if (
                        not isinstance(encoded, str)
                        or len(encoded) > MAX_TEXT * 4 // 3 + 8
                    ):
                        raise ValueError("项目原始输出超过限制")
                    candidate[key] = base64.b64decode(encoded, validate=True)
                    if len(candidate[key]) > MAX_TEXT:
                        raise ValueError("项目原始输出超过限制")
                candidate["diagnostics"] = tuple(
                    text(v) for v in candidate["diagnostics"]
                )
                candidates.append(RecoveryCandidate(**candidate))
            report["candidates"] = tuple(candidates)
            report["diagnostics"] = tuple(text(v) for v in report["diagnostics"])
            report = ModuleReport(**report)
        if kind == "module-unavailable" and report is None:
            raise ValueError("条目信息缺来源")
        if not isinstance(row["path"], str) or len(row["path"]) > 8192:
            raise ValueError("编辑区路径非法")
        return EditorState(
            (parent / row["path"]).resolve(),
            vm,
            kind,
            text(row["text"]),
            row["modified"],
            row["draft_saved"],
            report,
        )
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError("项目编辑区数据非法") from exc
