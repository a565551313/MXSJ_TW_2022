#!/usr/bin/env python3
"""Test the 2303 prefix records as image rectangles and their sector references.

Tests *all* 32 records against source-file bytes and sector indices; no client writes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "work/dream-world-connect-login-map/tools"))
from map_parser import parse_map


def analyze(path: Path) -> dict:
    doc = parse_map(path)
    refs = {i: [] for i in range(len(doc["prefix_records"]))}
    for sector in doc["sectors"]:
        for ref in sector["record_references"]:
            refs[ref].append(sector["index"])
    checks = []
    for record in doc["prefix_records"]:
        rect = record["bounds_px"]
        x, y, w, h = (rect[k] for k in ("x", "y", "width", "height"))
        first_col = x // 320
        last_col = (x + w - 1) // 320
        expected = [row * 7 + col for row in range(y // 240, (y + h - 1) // 240 + 1)
                    for col in range(first_col, last_col + 1)]
        actual = sorted(refs[record["index"]])
        checks.append({
            "index": record["index"], "bounds_px": rect,
            "length_matches_20_plus_payload": record["length"] == 20 + record["payload_length"],
            "predicted_320x240_sectors": expected,
            "actual_sectors": actual,
            "sector_match": expected == actual,
        })
    return {"source": str(path), "hypothesis": "rectangular prefix objects; row-major 7 columns of 320x240 px sectors",
            "records": checks, "all_lengths_match": all(c["length_matches_20_plus_payload"] for c in checks),
            "all_references_match": all(c["sector_match"] for c in checks),
            "reference_total": sum(len(c["actual_sectors"]) for c in checks)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("map", type=Path)
    ap.add_argument("--output", type=Path, help="optional JSON result")
    args = ap.parse_args()
    result = analyze(args.map)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(result['records'])} records, {result['reference_total']} references, "
          f"length check={result['all_lengths_match']}, 320x240 check={result['all_references_match']}")
    if not result["all_lengths_match"] or not result["all_references_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
