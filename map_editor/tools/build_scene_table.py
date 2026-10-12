#!/usr/bin/env python3
"""Regenerate the shipped scene-name table.

Scene names live in ``data/script.fls`` behind a 5-segment XOR + Python 2.7
marshal layer.  This script does **not** re-implement that; it reads the tables
that the repository's existing, already-verified extraction produced:

    server/docs/csv_checks/staging/mapdata_scene_dictionary.csv      (104 rows)
    server/docs/csv_checks/staging/sceneid2name_minimap_scenes.csv   ( 57 rows)

Usage:
    python tools/build_scene_table.py --repo ../.. --out data/scenes_tw_v2_27_2.json

If you have a *newer* client, re-extract those two CSVs first and rerun this.
The editor keeps working without the table; it simply shows "场景 2101" instead
of a name, and all geometry still comes straight from the .map files.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../..", help="仓库根目录")
    ap.add_argument("--out", default="data/scenes_tw_v2_27_2.json")
    args = ap.parse_args()

    staging = Path(args.repo) / "server" / "docs" / "csv_checks" / "staging"
    scene_csv = staging / "mapdata_scene_dictionary.csv"
    mini_csv = staging / "sceneid2name_minimap_scenes.csv"
    for p in (scene_csv, mini_csv):
        if not p.is_file():
            raise SystemExit(f"[错误] 找不到 {p}")

    scenes: dict[str, dict] = {}
    with scene_csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            key = f"{int(row['scene_id']):04d}"
            scenes[key] = {"name": row["name"], "w": int(row["w"]), "h": int(row["h"])}

    minimap: dict[str, str] = {}
    with mini_csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            minimap[f"{int(row['scene_id']):04d}"] = row["name"]

    sizes = {(v["w"], v["h"]) for v in scenes.values()}
    doc = {
        "schema": 1,
        "source": "data/script.fls entries 1301 (scene dictionary) and 400 (minimap names)",
        "client": "MXSJ TW v2.27.2",
        "note": "Regenerate with tools/build_scene_table.py; the editor works without this file.",
        "scene_count": len(scenes),
        "distinct_sizes": len(sizes),
        "scenes": dict(sorted(scenes.items())),
        "minimap_names": dict(sorted(minimap.items())),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"写出 {out}: {len(scenes)} 个场景, {len(sizes)} 种尺寸, "
          f"{len(minimap)} 个小地图名")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
