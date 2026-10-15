"""Untrusted source candidates; engine completion never grants source trust."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .recovery_process import RecoveryCancelled

DRAFT_HEADER = (
    "# coding: utf-8\n"
    "# MXSJ-RECOVERED-DRAFT: not original source; review before publishing\n"
)


@dataclass(frozen=True)
class RecoveryCandidate:
    engine: str
    version: str
    status: str
    source: str
    diagnostics: tuple[str, ...] = ()
    stdout: bytes = b""
    stderr: bytes = b""
    raw_kind: str = "engine-bytes"
    binary_sha256: str = ""
    source_sha256: str = ""
    trace_stdout: bytes = b""

    @property
    def complete(self):
        return self.status == "complete" and bool(self.source.strip())

    def metadata(self):
        return {
            "engine": self.engine,
            "version": self.version,
            "status": self.status,
            "completion_is_heuristic": True,
            "syntax_checked": False,
            "semantics_verified": False,
            "source_sha256": hashlib.sha256(self.source.encode("utf-8")).hexdigest(),
            "binary_sha256": self.binary_sha256,
            "engine_source_sha256": self.source_sha256,
            "raw_kind": self.raw_kind,
            "stdout_sha256": hashlib.sha256(self.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(self.stderr).hexdigest(),
            "trace_stdout_sha256": hashlib.sha256(self.trace_stdout).hexdigest(),
            "trace_stdout_bytes": len(self.trace_stdout),
            "stdout_bytes": len(self.stdout),
            "stderr_bytes": len(self.stderr),
            "diagnostics": list(self.diagnostics),
        }


def primary_candidate(result):
    source = result["source"]
    if not any(
        line.strip() and not line.lstrip().startswith("#")
        for line in source.splitlines()
    ):
        source = ""
    return RecoveryCandidate(
        "uncompyle6",
        "3.9.4.dev0",
        "complete"
        if result["complete"] and source.strip()
        else ("partial" if source.strip() else "failed"),
        source,
        tuple(result["diagnostics"]),
        result.get("raw_source", "").encode("utf-8"),
        result.get("worker_stderr", "").encode("utf-8"),
        "lossless-compatibility-rendered-utf8-not-pristine-engine-bytes",
        trace_stdout=result.get("worker_stdout", "").encode("utf-8"),
    )


def pycdc_candidate(engine, pyc, vm, *, timeout=30, cancel=None):
    output = engine.run(pyc, timeout=timeout, cancel=cancel)
    if output.status == "cancelled":
        raise RecoveryCancelled("恢复已取消；原包及已有编辑未修改")
    raw = output.stdout
    text = raw.decode("utf-8", errors="backslashreplace")
    notes = ["第二引擎输出只作恢复候选；未验证语法或业务逻辑。"]
    status = "complete"
    if output.status != "finished":
        status = output.status
        notes.append("pycdc 进程未正常完成：" + output.status)
    elif output.returncode != 0 or not raw.strip():
        status = "failed"
        notes.append(f"pycdc 退出码 {output.returncode}，保留原始诊断。")
    elif "# WARNING: Decompyle incomplete" in text:
        status = "partial"
        notes.append("pycdc 明示不完整；即使语法可编译，也不能当完整模块。")
    try:
        raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        if status == "complete":
            status = "partial"
        notes.append("原始输出含非UTF-8字节；显示候选已转义，未作逐字节还原。")
    if b"\x00" in raw:
        if status == "complete":
            status = "partial"
        notes.append("原始输出含NUL，须修复并核验，不能直接采用。")
    # Do not turn a header-only/crash diagnostic into an editable source stub.
    body = any(
        line.strip() and not line.lstrip().startswith("#") for line in text.splitlines()
    )
    source = (DRAFT_HEADER + f"# MXSJ-RECOVERY-VM: {vm}\n" + text) if body else ""
    if not source and status == "complete":
        status = "failed"
        notes.append("只有引擎头注释，没有源码主体。")
    return RecoveryCandidate(
        "pycdc",
        engine.source_commit,
        status,
        source,
        tuple(notes),
        output.stdout,
        output.stderr,
        "engine-bytes",
        engine.binary_sha256,
        engine.source_sha256,
    )


def best_candidate(candidates):
    for candidate in candidates:
        if candidate.complete:
            return candidate
    # Among partial drafts show the most text, not a header-only primary result.
    # This is a display choice only, never a correctness/completeness score.
    return max(candidates, key=lambda c: len(c.source))
