"""Read-only 0SLF opening diagnostics. Standard Python only; no game execution.

Report contains hashes and directory metadata, NEVER payloads, source, or keys.
Run alongside bootstrap.py, optionally dragging a script.fls onto the BAT launcher.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import time
from pathlib import Path

MAX_RECORDS = 1_000_000


def inspect_archive(path: Path) -> dict:
    """Read the actual file in binary mode; retain at most eight suspect rows."""
    report = {
        "schema": 1,
        "diagnostic": "script-open-boundaries-v2",
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "file_name": path.name,
        "payloads_included": False,
        "keys_included": False,
        "modified_input": False,
    }
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        report["file_bytes"] = before.st_size
        sha = hashlib.sha256()
        while block := stream.read(1024 * 1024):
            sha.update(block)
        report["sha256"] = sha.hexdigest()
        stream.seek(0)
        header = stream.read(12)
        report["header_hex"] = header.hex()
        if len(header) != 12 or header[:4] != b"0SLF":
            report["status"] = "not-a-0slf-header"
        else:
            count, directory = struct.unpack_from("<II", header, 4)
            end = directory + count * 16
            report.update(entries=count, directory_offset=directory, directory_end=end)
            if not 0 < count <= MAX_RECORDS:
                report["status"] = "entry-count-outside-diagnostic-limit"
            elif directory < 12 or end > before.st_size:
                report["status"] = "directory-outside-file"
            else:
                stream.seek(directory)
                examples, invalid, invalid_count = [], [], 0
                directory_sha = hashlib.sha256()
                for index in range(count):
                    raw = stream.read(16)
                    if len(raw) != 16:
                        report["status"] = "directory-short-read"
                        break
                    directory_sha.update(raw)
                    entry_id, r1, r2, r3 = struct.unpack("<IIII", raw)
                    length = ((r1 * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ r2
                    offset = ((r2 * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ r3
                    in_file = offset >= 12 and offset + length <= before.st_size
                    overlap = offset < end and offset + length > directory
                    valid = in_file and not overlap
                    row = dict(
                        index=index,
                        raw_hex=raw.hex(),
                        offset=offset,
                        length=length,
                        end=offset + length,
                        within_pre_directory=offset >= 12
                        and offset + length <= directory,
                        within_file=in_file,
                        overlaps_directory=overlap,
                        valid_payload_region=valid,
                    )
                    if index < 4:
                        examples.append(row)
                    if not valid:
                        invalid_count += 1
                        if len(invalid) < 8:
                            invalid.append(row)
                else:
                    report["status"] = (
                        "bounds-pass" if not invalid_count else "payload-bounds-failed"
                    )
                report.update(
                    first_records=examples,
                    invalid_records=invalid,
                    invalid_count=invalid_count,
                    directory_sha256=directory_sha.hexdigest(),
                )
        after = os.fstat(stream.fileno())
        report["stable_during_diagnostic"] = (
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) == (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        if not report["stable_during_diagnostic"]:
            report["status"] = "input-changed-during-diagnostic"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", type=Path)
    args = parser.parse_args(argv)
    path = args.archive
    if path is None:
        name = input("请把报错的 script.fls 拖入此窗口，再按回车（空白取消）：").strip()
        if not name:
            print("Cancelled; no files changed.")
            return 0
        path = Path(name.strip('"'))
    report = inspect_archive(path)
    output = (
        Path(__file__).resolve().parent
        / f"script-open-diagnostic-{time.time_ns()}.json"
    )
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("Read-only diagnosis:", report["status"])
    print("Report:", output)
    print(
        "Send only this JSON report, NOT the game archive. No payloads/keys included."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, EOFError) as exc:
        print("Diagnosis failed:", exc, file=sys.stderr)
        raise SystemExit(1) from None
