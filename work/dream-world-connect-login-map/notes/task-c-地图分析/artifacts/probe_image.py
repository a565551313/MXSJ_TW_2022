#!/usr/bin/env python3
"""Reproduce GEPJ-to-JPEG repair failures without keeping deceptive PNG outputs.

Requires local ImageMagick `convert`; no network. Uses a temporary directory.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "work/dream-world-connect-login-map/tools"))
from map_parser import parse_map


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("map", type=Path)
    ap.add_argument("--sector", type=int, default=16)
    args = ap.parse_args()
    if shutil.which("convert") is None:
        print("convert missing: test unavailable (no installation attempted)")
        return
    doc = parse_map(args.map)
    if not 0 <= args.sector < 49:
        ap.error("sector must be 0-48")
    image = doc["sectors"][args.sector]["image"]
    with args.map.open("rb") as stream:
        stream.seek(image["offset"])
        raw = stream.read(image["length"])
    assert raw.startswith(b"\xff\xd8\xff\xa0")
    simple = raw[:2] + raw[4:] + b"\xff\xd9"
    sos = simple.find(b"\xff\xda")
    if sos < 0:
        ap.error("no SOS marker found")
    modified = simple[:sos + 2] + b"\x00\x0c" + simple[sos + 4:sos + 11] + b"\x00\x3f\x00" + simple[sos + 11:]
    with tempfile.TemporaryDirectory(prefix="mxsj-gepj-probe-") as temp:
        for name, data in (("remove_a0_add_eoi", simple), ("also_expand_sos", modified)):
            output = str(Path(temp) / (name + ".png"))
            run = subprocess.run(["convert", "jpeg:-", output], input=data, capture_output=True, timeout=15)
            print(f"{name}: return={run.returncode}; png_created={Path(output).exists()}; stderr={run.stderr.decode('utf-8', 'replace')[:420]!r}")
    print("Temporary outputs removed. Even return=0 with warnings is not a validated image decoder.")


if __name__ == "__main__":
    main()
