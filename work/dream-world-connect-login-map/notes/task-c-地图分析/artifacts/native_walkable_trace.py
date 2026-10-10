#!/usr/bin/env python3
"""Audit mx.exe IsWalkable binding and 16-bit grid comparison, read-only."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[5]


def trace(path: Path) -> str:
    data = path.read_bytes()
    name_offset = data.find(b"IsWalkable\0")
    if not 0x2aee00 <= name_offset < 0x3d9e00:
        raise ValueError("IsWalkable not found in .rdata")
    name_vma = 0x6b0000 + name_offset - 0x2aee00
    ptr = data.find(struct.pack("<I", name_vma))
    if ptr < 0:
        raise ValueError("IsWalkable method table reference not found")
    target = struct.unpack_from("<I", data, ptr + 4)[0]
    lines = [f"source {path}", f"sha256 {hashlib.sha256(data).hexdigest()}",
             f"IsWalkable name file offset=0x{name_offset:x} VMA=0x{name_vma:x}",
             f"method table name pointer file offset=0x{ptr:x}, adjacent function VMA=0x{target:x}"]
    for start, end, description in [(target, target + 0x70, "Python binding"),
                                    (0x4bbb00, 0x4bbb54, "pathfinding grid comparison"),
                                    (0x4baebf, 0x4baf2a, "pathfinding coordinate scaling (signed divide by 20)"),
                                    (0x4b8d3c, 0x4b8d54, "LLEC data loading")]:
        if shutil.which("objdump"):
            p = subprocess.run(["objdump", "-d", "-M", "intel", str(path),
                                f"--start-address=0x{start:x}", f"--stop-address=0x{end:x}"],
                               capture_output=True, text=True, timeout=60)
            if p.returncode:
                raise RuntimeError(p.stderr)
            lines.append(f"-- {description} VMA 0x{start:x}..0x{end:x} --\n{p.stdout}")
    lines.append("Observation: binding 0x488a00 calls 0x4bbb00. 0x4bbb00 reads a 16-bit grid element and compares it with a threshold. 0x4baebf..0x4baf27 reduces coordinates to 20-pixel grid cells (signed multiply by 0x66666667, shift right 3). Linkage from raw LLEC bytes to this grid is NOT established by these snippets.")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", type=Path, default=ROOT / "mx.exe")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    content = trace(args.exe)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
