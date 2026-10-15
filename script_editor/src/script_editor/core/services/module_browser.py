"""Strict package -> standard pyc -> separate decompiler process -> editable draft.

No target imports/exec, no invented pass stubs, no automatic source trust.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

from ..inspection.native import inspect_module
from ..vm.marshal_tree import parse
from .pycdc_engine import discover_pycdc
from .recovery_candidates import (
    RecoveryCandidate,
    best_candidate,
    primary_candidate,
    pycdc_candidate,
)
from .recovery_process import RecoveryCancelled, RecoveryProcessError, run_bounded


@dataclass(frozen=True)
class ModuleReport:
    archive: Path
    fingerprint: str
    index: int
    identity: str
    vm: str
    filename_hex: str
    standard_sha256: str
    source: str
    complete: bool
    disassembly: str
    diagnostics: tuple[str, ...]
    stored_preview: str
    candidates: tuple[RecoveryCandidate, ...] = ()
    selected_engine: str = "uncompyle6"
    corpus_manifest_sha256: str = ""
    candidate_pyc_sha256: str = ""
    origin_verified: bool = True

    def for_candidate(self, index):
        candidate = self.candidates[index]
        if not candidate.source:
            raise ValueError("此候选没有源码主体，请查看诊断")
        return replace(
            self,
            source=candidate.source,
            complete=candidate.complete,
            diagnostics=candidate.diagnostics,
            selected_engine=candidate.engine,
        )

    def metadata(self):
        return {
            "archive": str(self.archive),
            "archive_sha256": self.fingerprint,
            "index": self.index,
            "identity": self.identity,
            "vm": self.vm,
            "filename_bytes": self.filename_hex,
            "standard_pyc_sha256": self.standard_sha256,
            "decompiler_completed": self.complete,
            "compiled_and_reviewed": False,
            "source_status": "recovered-draft-not-original-not-reviewed",
            "diagnostics": list(self.diagnostics),
            "stored_preview_hex": self.stored_preview,
            "selected_engine": self.selected_engine,
            "corpus_manifest_sha256": self.corpus_manifest_sha256,
            "candidate_pyc_sha256": self.candidate_pyc_sha256,
            "origin_verified": self.origin_verified,
            "candidates": [c.metadata() for c in self.candidates],
        }


def _recover_primary(pyc: bytes, vm: str, *, timeout=30, cancel=None):
    if vm not in {"py25", "py27"}:
        raise ValueError("unknown recovery VM")
    if (
        pyc[:4]
        != {"py25": bytes.fromhex("b3f20d0a"), "py27": bytes.fromhex("03f30d0a")}[vm]
    ):
        raise ValueError("recovery magic/VM mismatch")
    parse(pyc[8:])  # Bounded validation before any third-party parser sees data.
    if getattr(sys, "frozen", False):
        worker = (
            Path(sys.executable).resolve().parent
            / "recovery-worker/MXSJRecoveryWorker.exe"
        )
        command = [str(worker)]
    else:
        worker = Path(__file__).resolve().parents[2] / "data/recovery_worker.py"
        command = [sys.executable, "-E", str(worker)]
    if not worker.is_file():
        raise ValueError(
            "缺少独立恢复引擎；源码运行请通过bootstrap安装依赖，EXE请完整重新构建"
        )
    with tempfile.TemporaryDirectory(prefix="mx-recovery-") as temporary:
        root = Path(temporary)
        source, output = root / "standard.pyc", root / "result.json"
        source.write_bytes(pyc)
        try:
            arguments = [
                *command,
                "--input",
                str(source),
                "--output",
                str(output),
                "--vm",
                vm,
            ]
            if cancel is not None:
                bounded = run_bounded(
                    arguments, timeout=timeout, cancel=cancel, cwd=root
                )
                if bounded.status == "cancelled":
                    raise RecoveryCancelled("恢复已取消；原包及已有编辑未修改")
                if bounded.status != "finished":
                    raise RecoveryProcessError(bounded.status)
                completed = subprocess.CompletedProcess(arguments, bounded.returncode)
            else:
                completed = subprocess.run(
                    arguments,
                    cwd=root,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=timeout,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        except subprocess.TimeoutExpired as exc:
            raise RecoveryProcessError("timeout") from exc
        if completed.returncode or not output.is_file():
            raise ValueError(f"恢复引擎失败，退出码{completed.returncode}")
        with output.open("rb") as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024:
            raise ValueError("recovery result exceeds limit")
        result = json.loads(raw)
        if (
            not isinstance(result, dict)
            or result.get("engine_protocol") != "mxsj-recovery/2"
            or not isinstance(result.get("source"), str)
            or not isinstance(result.get("disassembly"), str)
            or type(result.get("complete")) is not bool
            or not isinstance(result.get("diagnostics"), list)
            or not all(isinstance(d, str) for d in result["diagnostics"])
        ):
            raise ValueError(
                "invalid recovery result：恢复引擎版本或输出协议不符，"
                "请完整解压/重新构建新版"
            )
        if (
            len(result["source"]) > 3 * 1024 * 1024
            or len(result["disassembly"]) > 3 * 1024 * 1024
        ):
            raise ValueError("recovery text exceeds limit")
        for key in ("raw_source", "worker_stdout", "worker_stderr"):
            if key in result and (
                not isinstance(result[key], str) or len(result[key]) > 2 * 1024 * 1024
            ):
                raise ValueError("invalid bounded recovery diagnostic")
        return result


def recover_standard(pyc: bytes, vm: str, *, timeout=30, pycdc=None, cancel=None):
    # Validate before discovery/copying/executing either parser.
    if vm not in {"py25", "py27"} or pyc[:4] != {
        "py25": bytes.fromhex("b3f20d0a"),
        "py27": bytes.fromhex("03f30d0a"),
    }.get(vm):
        raise ValueError("recovery magic/VM mismatch")
    parse(pyc[8:])
    if cancel is not None and cancel.is_set():
        raise RecoveryCancelled("恢复已取消")
    notes = []
    if pycdc is None:
        try:
            pycdc = discover_pycdc()
        except (OSError, ValueError, TypeError) as exc:
            notes.append("第二引擎未启用：" + str(exc))
    try:
        result = _recover_primary(pyc, vm, timeout=timeout, cancel=cancel)
        primary = primary_candidate(result)
    except RecoveryCancelled:
        raise
    except (OSError, ValueError) as exc:
        if pycdc is None:
            raise
        result = {"disassembly": "", "diagnostics": []}
        primary = RecoveryCandidate(
            "uncompyle6",
            "3.9.4.dev0",
            getattr(exc, "status", "failed"),
            "",
            (str(exc),),
        )
    candidates = [primary]
    if pycdc is not None:
        try:
            candidates.append(
                pycdc_candidate(pycdc, pyc, vm, timeout=timeout, cancel=cancel)
            )
        except RecoveryCancelled:
            raise
        except (OSError, ValueError) as exc:
            candidates.append(
                RecoveryCandidate(
                    "pycdc", str(pycdc.source_commit), "failed", "", (str(exc),)
                )
            )
    else:
        notes.append("未安装通过清单校验的第二引擎；当前仅使用uncompyle6。")
    selected = best_candidate(candidates)
    return {
        **result,
        "source": selected.source,
        "complete": selected.complete,
        "diagnostics": [*selected.diagnostics, *notes],
        "candidates": tuple(candidates),
        "selected_engine": selected.engine,
    }


def read_module(archive, index, catalog=None, *, pycdc=None, cancel=None, timeout=30):
    if archive.vm == "py25" and index == 1288:
        # Policy exclusion precedes payload, source name, preview and recovery.
        archive._assert_unchanged()
        return ModuleReport(
            archive.path,
            archive.fingerprint(),
            index,
            archive.entries[index].identity,
            archive.vm,
            "",
            "",
            "",
            False,
            "",
            ("excluded_by_policy：1288不生成源码、pyc或存储预览。",),
            "",
            (),
            "",
        )
    metadata = archive.entry_metadata(index)
    oversized = archive.entries[index].size > 64 * 1024 * 1024
    if oversized:
        span = archive.index.spans[index]
        offset = span.offset if archive.kind == "0slf" else span.data_offset
        stored = archive.reader.read_at(offset, 256)
    else:
        stored = archive.read_stored(index)
    fingerprint = archive.fingerprint()
    filename, standard_sha = "", ""
    result = {"source": "", "complete": False, "disassembly": "", "diagnostics": []}
    try:
        if oversized:
            raise ValueError(
                "存储负载超过64MiB浏览限制，只展示前256字节；未分配整个条目"
            )
        standard, name, _ = inspect_module(archive, index, catalog)
        filename = name.hex()
        standard_sha = hashlib.sha256(standard).hexdigest()
        result = recover_standard(
            standard, archive.vm, pycdc=pycdc, cancel=cancel, timeout=timeout
        )
    except (OSError, ValueError, KeyError) as exc:
        result["diagnostics"] = [f"不能恢复此条目：{exc}"]
    archive._assert_unchanged()
    return ModuleReport(
        archive.path,
        fingerprint,
        index,
        metadata["identity"],
        archive.vm,
        filename,
        standard_sha,
        result["source"],
        result["complete"],
        result["disassembly"],
        tuple(result["diagnostics"]),
        stored[:256].hex(" "),
        result.get("candidates", ()),
        result.get("selected_engine", ""),
    )
