"""Strict package -> standard pyc -> separate decompiler process -> editable draft.

No target imports/exec, no invented pass stubs, no automatic source trust.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..inspection.native import inspect_module
from ..vm.marshal_tree import parse


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
        }


def recover_standard(pyc: bytes, vm: str, *, timeout=30):
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
            completed = subprocess.run(
                [*command, "--input", str(source), "--output", str(output), "--vm", vm],
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError("恢复引擎超过时间限制；模块未执行、原包未修改") from exc
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
                "invalid recovery result：恢复引擎版本或输出协议不符，请完整解压/重新构建新版"
            )
        if (
            len(result["source"]) > 3 * 1024 * 1024
            or len(result["disassembly"]) > 3 * 1024 * 1024
        ):
            raise ValueError("recovery text exceeds limit")
        return result


def read_module(archive, index, catalog=None):
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
        result = recover_standard(standard, archive.vm)
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
    )
