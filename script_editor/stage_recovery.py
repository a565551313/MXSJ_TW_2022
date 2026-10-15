"""Stage the separate GPL program, licenses and corresponding source archives."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    target = args.destination.resolve(strict=True)
    program = target / "recovery-worker"
    if program.exists():
        raise ValueError("恢复程序目标已存在；拒绝覆盖")
    shutil.copytree(root / "dist/MXSJRecoveryWorker", program)
    sources = program / "corresponding-source"
    sources.mkdir()
    shutil.copyfile(
        root / "src/script_editor/data/recovery_worker.py",
        sources / "recovery_worker.py",
    )
    shutil.copyfile(root / "recovery_worker.spec", sources / "recovery_worker.spec")
    shutil.copytree(root / "licenses/recovery", sources / "licenses")
    from script_editor.recovery_dependencies import checked_recovery_source

    archive = checked_recovery_source(root)
    shutil.copyfile(archive, sources / archive.name)
    # Keep full upstream sources with the independent binary, not just URLs.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--no-binary=:all:",
            "--dest",
            str(sources),
            "xdis==6.3.0",
            "spark-parser==1.9.0",
            "six==1.17.0",
            "click==8.5.0",
        ],
        check=True,
    )
    from script_editor.core.compiler.runner import bundled_compiler, compile_standard

    with tempfile.TemporaryDirectory(prefix="mx-worker-smoke-") as temporary:
        temporary = Path(temporary)
        for vm in ("py25", "py27"):
            compiler = bundled_compiler(vm, root)
            source, result = temporary / (vm + ".pyc"), temporary / (vm + ".json")
            compile_standard(compiler, "worker_smoke = 1\n", b"worker_smoke.py", source)
            subprocess.run(
                [
                    str(program / "MXSJRecoveryWorker.exe"),
                    "--input",
                    str(source),
                    "--output",
                    str(result),
                    "--vm",
                    vm,
                ],
                timeout=30,
                check=True,
            )
            report = json.loads(result.read_text(encoding="utf-8"))
            if not report.get("complete") or "worker_smoke" not in report.get(
                "source", ""
            ):
                raise ValueError("独立恢复EXE实际smoke失败，禁止宣称完整构建")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
