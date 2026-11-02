"""Build a non-destructive client probe package from an explicit ``script.fls``.

The builder accepts only a caller-supplied file named ``script.fls``.  It validates
its digest and 0SLF directory, copies bytes without decoding them, and creates a
new package directory outside the repository.  No existing path is ever opened
for writing.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path

MASK = 0xFFFFFFFF
_CHUNK = 1024 * 1024
_REQUIRED_PROBE_NAMES = {
    "PROBE_VERSION",
    "get_runtime",
    "get_modules",
    "get_native_api",
    "get_report",
}
_PROBE_FILES = ("mxsj_probe.py", "ipc.py", "serve.py")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(_CHUNK):
            digest.update(block)
    return digest.hexdigest()


def _validate_fls(path: Path) -> dict:
    """Validate the complete 0SLF directory and return stable inventory facts."""
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12 or header[:4] != b"0SLF":
            raise ValueError("input is not a 0SLF package")
        count, directory = struct.unpack_from("<II", header, 4)
        if not 0 < count <= 1_000_000:
            raise ValueError("0SLF entry count is outside bounds")
        if directory < 12 or directory + count * 16 > size:
            raise ValueError("0SLF directory is outside file bounds")
        stream.seek(directory)
        records = stream.read(count * 16)
        if len(records) != count * 16:
            raise ValueError("truncated 0SLF directory")
        seen: set[int] = set()
        previous = None
        for index, (entry_id, r1, r2, r3) in enumerate(
            struct.iter_unpack("<IIII", records)
        ):
            if entry_id in seen:
                raise ValueError(f"duplicate 0SLF entry ID: {entry_id}")
            if previous is not None and entry_id <= previous:
                raise ValueError("0SLF directory is not sorted by entry ID")
            previous = entry_id
            seen.add(entry_id)
            length = (((r1 * entry_id + 0x0DF25E) & MASK) ^ r2) & MASK
            offset = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ r3) & MASK
            if offset > size or length > size - offset:
                raise ValueError(f"0SLF entry {index} payload is outside bounds")
    return {"entry_count": count, "directory_offset": directory}


def _validate_probe_source(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError("probe source must be a regular, non-alias file")
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"probe source is not valid Python: {exc}") from exc
    names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    names.update(
        node.targets[0].id
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    )
    missing = sorted(_REQUIRED_PROBE_NAMES - names)
    if missing:
        raise ValueError("probe source is missing: " + ", ".join(missing))
    return {
        "sha256": _sha256(path),
        "path": path.name,
        "files": [name for name in _PROBE_FILES if path.with_name(name).is_file()],
    }


def build_package(
    script_fls: str | os.PathLike[str],
    output_dir: str | os.PathLike[str],
    *,
    expected_sha256: str,
    probe_source: str | os.PathLike[str] | None = None,
    include_probe_source: bool = False,
) -> dict:
    """Build and return the manifest for a fresh package directory."""
    source = Path(script_fls)
    destination = Path(output_dir)
    if source.name != "script.fls":
        raise ValueError("input must be an explicitly selected script.fls")
    if source.is_symlink() or not source.is_file() or source.stat().st_nlink != 1:
        raise ValueError("input must be a regular, non-alias script.fls")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ValueError("expected_sha256 must be a 64-character SHA-256")
    expected_sha256 = expected_sha256.lower()
    if any(char not in "0123456789abcdef" for char in expected_sha256):
        raise ValueError("expected_sha256 is not hexadecimal")
    source = source.resolve(strict=True)
    repo_root = Path(__file__).resolve().parents[3]
    resolved_destination = destination.resolve()
    if resolved_destination == repo_root or repo_root in resolved_destination.parents:
        raise ValueError("output directory must be outside the repository")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"output directory already exists: {destination}")
    actual_sha256 = _sha256(source)
    if actual_sha256 != expected_sha256:
        raise ValueError("script.fls SHA-256 does not match expected_sha256")
    fls_facts = _validate_fls(source)
    probe_path = (
        Path(probe_source)
        if probe_source is not None
        else Path(__file__).with_name("mxsj_probe.py")
    )
    if (
        probe_path.is_symlink()
        or not probe_path.is_file()
        or probe_path.stat().st_nlink != 1
    ):
        raise ValueError("probe source must be a regular, non-alias file")
    source_info = _validate_probe_source(probe_path)
    for filename in _PROBE_FILES[1:]:
        extra = probe_path.with_name(filename)
        if extra.is_symlink() or not extra.is_file() or extra.stat().st_nlink != 1:
            raise ValueError("probe companion must be a regular, non-alias file")
        ast.parse(extra.read_text(encoding="utf-8"), filename=str(extra))

    # mkdir is intentionally exclusive; a race or pre-existing target is fatal.
    destination.mkdir(parents=True, exist_ok=False)
    try:
        copied = destination / "script.fls"
        with source.open("rb") as source_stream, copied.open("xb") as target:
            shutil.copyfileobj(source_stream, target, length=_CHUNK)
        if _sha256(copied) != actual_sha256:
            raise ValueError("copied script.fls SHA-256 verification failed")
        copied_probe_files = []
        if source_info is not None and include_probe_source:
            for filename in _PROBE_FILES:
                probe_file = probe_path.with_name(filename)
                probe_target = destination / filename
                with (
                    probe_file.open("rb") as source_stream,
                    probe_target.open("xb") as target,
                ):
                    shutil.copyfileobj(source_stream, target, length=_CHUNK)
                copied_probe_files.append(filename)
        manifest = {
            "format": "mxsj-client-mcp-probe-package-v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "name": "script.fls",
                "sha256": actual_sha256,
                "size_bytes": source.stat().st_size,
            },
            "package": {
                "script_fls": "script.fls",
                "probe_source": (
                    copied_probe_files if source_info and include_probe_source else []
                ),
            },
            "fls": fls_facts,
            "probe_source": source_info,
        }
        manifest_path = destination / "manifest.json"
        with manifest_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    except Exception:
        # Keep a failed fresh directory intact for diagnosis; never touch source.
        raise
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-fls", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--probe-source", type=Path)
    parser.add_argument("--include-probe-source", action="store_true")
    args = parser.parse_args(argv)
    try:
        build_package(
            args.script_fls,
            args.output_dir,
            expected_sha256=args.expected_sha256,
            probe_source=args.probe_source,
            include_probe_source=args.include_probe_source,
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
