#!/usr/bin/env python3
"""Reproduce Task C inventory, magic/offset tests and failed zlib probes; read-only."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib

REPO = Path(__file__).resolve().parents[5]


def inventory(root: Path) -> dict:
    data = root / "data"
    maps = root / "map"
    files = sorted(p for p in data.rglob("*") if p.is_file()) if data.exists() else []
    maps_found = sorted(maps.glob("*.map")) if maps.exists() else []
    findings = {"data_files": [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size} for p in files],
                "data_named_map_or_scene": [str(p.relative_to(root)) for p in files if any(t in p.name.lower() for t in ("map", "scene", "terrain"))],
                "standalone_map_files": [],
                "standalone_image_files": [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (".dds", ".tga", ".jpg", ".jpeg", ".png") and ".git" not in p.parts and "work" not in p.parts]}
    for p in maps_found:
        data = p.read_bytes()
        offsets = list(struct.unpack_from("<49I", data, 12))
        sector = data[offsets[0]:offsets[1]]
        # Expected failures are recorded explicitly, not discarded.
        zlib_trials = {}
        for at in (0, 4, 8, 12, offsets[0]):
            try:
                result = zlib.decompress(data[at:])
                zlib_trials[str(at)] = f"success: {len(result)} bytes"
            except zlib.error as exc:
                zlib_trials[str(at)] = f"failed: {exc}"
        findings["standalone_map_files"].append({
            "path": str(p.relative_to(root)), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "first_32_hex": data[:32].hex(),
            "header_u32_le_at_4_8_208_212": [struct.unpack_from("<I", data, a)[0] for a in (4, 8, 208, 212)],
            "sector_0_offset": offsets[0], "sector_offsets_strictly_increasing": all(a < b for a, b in zip(offsets, offsets[1:])),
            "sector_0_prefix_hex": sector[:48].hex(),
            "marker_occurrences": {x.decode("ascii"): data.count(x) for x in (b"GEPJ", b"LLEC", b"GIRB")},
            "zlib_trials": zlib_trials,
        })
    return findings


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=REPO)
    ap.add_argument("--output", type=Path, help="write a deterministic JSON evidence snapshot")
    args = ap.parse_args()
    result = inventory(args.root.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
