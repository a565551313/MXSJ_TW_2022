#!/usr/bin/env python3
"""Read-only, offline audit of mx.exe's GEPJ segment-table loading routine."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[5]


def trace(exe: Path) -> str:
    raw = exe.read_bytes()
    lines = [f"sample: {exe}", f"sha256: {hashlib.sha256(raw).hexdigest()}"]
    for signature in (b"GEPJ", b"LLEC", b"GIRB"):
        at = raw.find(signature)
        lines.append(f"first {signature.decode('ascii')} bytes at file offset 0x{at:x}")
    if shutil.which("objdump") is None:
        lines.append("objdump unavailable; disassembly skipped")
    else:
        proc = subprocess.run(["objdump", "-d", "-M", "intel", str(exe),
                               "--start-address=0x4b8e9d", "--stop-address=0x4b8f37"],
                              capture_output=True, text=True, timeout=60)
        if proc.returncode:
            raise RuntimeError(proc.stderr)
        lines.append("-- mx.exe .text at VMA 0x4b8e9d..0x4b8f37 --")
        lines.append(proc.stdout)
        lines.append("0x4b8ea2 pushes 0x1a (26 bytes) for GEPJ segment lengths; ")
        lines.append("0x4b8ee0..0x4b8f26 accumulates 13 little-endian uint16 into a prefix offset table.")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", type=Path, default=ROOT / "mx.exe")
    ap.add_argument("--output", type=Path, help="optional local evidence text")
    args = ap.parse_args()
    text = trace(args.exe)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
