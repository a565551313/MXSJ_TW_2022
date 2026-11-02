"""Read-only 0SLF inventory and stored-payload comparison.

Usage: python tools/client_mcp/script_fls_compare.py --current PATH
       --baseline PATH --report NEW_PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path

MASK = 0xFFFFFFFF
MAX_ENTRIES = 1_000_000
CHUNK = 1024 * 1024


def _hash_range(stream, offset: int, length: int) -> str:
    stream.seek(offset)
    digest = hashlib.sha256()
    while length:
        block = stream.read(min(length, CHUNK))
        if not block:
            raise ValueError("unexpected end of file")
        digest.update(block)
        length -= len(block)
    return digest.hexdigest()


def inventory(path: Path) -> tuple[dict, dict[int, dict]]:
    """Read metadata and hash stored bytes without decoding their content."""
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        size = before.st_size
        header = stream.read(12)
        if len(header) != 12 or header[:4] != b"0SLF":
            raise ValueError("invalid 0SLF header")
        count, directory = struct.unpack_from("<II", header, 4)
        if not 0 < count <= MAX_ENTRIES:
            raise ValueError("entry count outside bounds")
        if directory < 12 or directory + count * 16 > size:
            raise ValueError("directory outside bounds")
        stream.seek(directory)
        records = stream.read(count * 16)
        if len(records) != count * 16:
            raise ValueError("truncated directory")
        entries = {}
        for index, (entry_id, r1, r2, r3) in enumerate(
            struct.iter_unpack("<IIII", records)
        ):
            if entry_id in entries:
                raise ValueError(f"duplicate entry ID: {entry_id}")
            length = (((r1 * entry_id + 0x0DF25E) & MASK) ^ r2) & MASK
            offset = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ r3) & MASK
            if offset > size or length > size - offset:
                raise ValueError(f"entry {index} payload outside bounds")
            entries[entry_id] = {
                "index": index,
                "sha256": _hash_range(stream, offset, length),
            }
        file_hash = _hash_range(stream, 0, size)
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size, after.st_mtime_ns, after.st_ctime_ns
        ):
            raise ValueError("input changed during inspection")
    return {"size_bytes": size, "sha256": file_hash, "entry_count": count}, entries


def compare(current: Path, baseline: Path) -> dict:
    current_summary, current_entries = inventory(current)
    baseline_summary, baseline_entries = inventory(baseline)
    changes = []
    counts = {"added": 0, "removed": 0, "index_changed": 0, "payload_changed": 0}
    for entry_id in sorted(current_entries.keys() | baseline_entries.keys()):
        old, new = baseline_entries.get(entry_id), current_entries.get(entry_id)
        if old is None:
            kinds = ["added"]
        elif new is None:
            kinds = ["removed"]
        else:
            kinds = []
            if old["index"] != new["index"]:
                kinds.append("index_changed")
            if old["sha256"] != new["sha256"]:
                kinds.append("payload_changed")
        if kinds:
            for kind in kinds:
                counts[kind] += 1
            changes.append(
                {"id": entry_id, "changes": kinds, "baseline": old, "current": new}
            )
    return {"baseline": baseline_summary, "current": current_summary,
            "summary": counts, "changes": changes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report_path = args.report.resolve()
        if report_path in {args.current.resolve(), args.baseline.resolve()}:
            raise ValueError("report path aliases an input")
        result = compare(args.current, args.baseline)
        # Exclusive creation rejects existing paths, including hard links and symlinks.
        with args.report.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(result, output, indent=2, ensure_ascii=False)
            output.write("\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
