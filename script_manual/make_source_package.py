#!/usr/bin/env python3
"""Build a source-only Windows manual test ZIP outside a clean checkout.

Maintainer command; needs Git, not Qt or game archives. Users do not need Git
for running the delivered manual, self-checking or building its EXE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

PREFIXES = (
    "script_manual/",
    "script_editor/src/script_editor/core/",
    "tools/devkit/",
)
EXTRAS = {
    "AGENTS.md",
    ".gitattributes",
    "ruff.toml",
    "docs/STATUS.md",
    "docs/ARENA_SANDBOX_RECOVERY.md",
    "docs/templates/AGENT_CHECKPOINT.md",
    "docs/PYTHON_TOOL_CONVENTIONS.md",
    "script_editor/src/script_editor/__init__.py",
    "tools/decompiler/batch_decompile.py",
    "tools/decompiler/recover_entries.py",
    "tools/decompiler/test_recover_entries.py",
}
FORBIDDEN = {".fls", ".exe", ".dll", ".pyo", ".pyc", ".zip", ".whl"}
PACKAGE_ROOT = "MXSJScriptManual-source-0.1.0.dev3"


def safe_file(repo: Path, relative: str) -> Path:
    parts = PurePosixPath(relative).parts
    if (
        not parts
        or PurePosixPath(relative).is_absolute()
        or any(
            p in {".", "..", ".git", ".venv", "__pycache__", "node_modules"} or ":" in p
            for p in parts
        )
        or "\\" in relative
    ):
        raise ValueError(f"Unsafe package path: {relative}")
    path = repo / relative
    for part in (path, *path.parents):
        if part == repo:
            break
        if part.is_symlink():
            raise ValueError(f"Package symlink rejected: {relative}")
    if not path.resolve().is_relative_to(repo.resolve()) or not path.is_file():
        raise ValueError(f"Missing or escaping package file: {relative}")
    if path.suffix.lower() in FORBIDDEN:
        raise ValueError(f"Binary/game input excluded: {relative}")
    return path


def select_files(repo: Path, tracked: list[str]) -> list[str]:
    available = set(tracked)
    selected = {
        p
        for p in tracked
        if p.startswith(PREFIXES)
        or p in EXTRAS
        or p.startswith("docs/evidence/script_manual_")
    }
    # Include only the actual evidence dependencies; never copy a whole corpus.
    for relative in sorted(selected):
        if not relative.startswith("script_manual/annotations/"):
            continue
        path = safe_file(repo, relative)
        if path.suffix != ".json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("entry_index") == 1288:
            raise ValueError("Protected entry must never have an annotation")
        for source in record["sources"]:
            name = source["path"]
            if name not in available:
                raise ValueError(f"Evidence is not tracked: {name}")
            raw = safe_file(repo, name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != source["sha256"]:
                raise ValueError(f"Evidence hash mismatch: {name}")
            selected.add(name)
    for name in selected:
        safe_file(repo, name)
    return sorted(selected)


def build_package(repo: Path, tracked: list[str], output: Path, commit: str):
    repo = repo.resolve()
    output = output.resolve()
    if output.is_relative_to(repo):
        raise ValueError("ZIP output must be outside the repository")
    if output.exists():
        raise FileExistsError(output)
    files = {
        name: safe_file(repo, name).read_bytes() for name in select_files(repo, tracked)
    }
    readme = "script_manual/WINDOWS_TEST.md"
    if readme in files:
        files["README_FIRST.md"] = files[readme]
    manifest = {
        "kind": "source-only manual Windows test package; not game/EXE acceptance",
        "source_commit": commit,
        "game_archives_native_compiler_binaries_credentials_included": False,
        "shared_parser_scope": "core source dependencies for N1 synthetic tests; "
        "not a script editor distribution; no keys/game packages",
        "files": {
            name: {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            for name, raw in sorted(files.items())
        },
    }
    files["PACKAGE_MANIFEST.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream, zipfile.ZipFile(stream, "w") as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(f"{PACKAGE_ROOT}/{name}", (2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
        for name, item in manifest["files"].items():
            raw = archive.read(f"{PACKAGE_ROOT}/{name}")
            if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError(f"ZIP member hash mismatch: {name}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=repo)

    if git("status", "--porcelain", "--untracked-files=no").strip():
        parser.error("Commit the tracked source changes before packaging")
    commit = git("rev-parse", "HEAD").decode().strip()
    tracked = git("ls-files", "-z").decode("utf-8").strip("\0").split("\0")
    manifest = build_package(repo, tracked, args.output, commit)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "source_commit": commit,
                "members": len(manifest["files"]) + 1,
                "bytes": args.output.stat().st_size,
                "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
