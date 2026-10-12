#!/usr/bin/env python3
"""Build `batch001.sample.json`: a small UI fixture subset of batch_001.

Purpose
-------
The review browser is a read-only frontend for the Python review API. For UI
work (and for automated tests) we need a few *real* rows to render. This script
copies an explicit, small selection of rows out of the frozen batch_001 review
CSVs into a JSON file. It never invents a value: every string below comes from
`server/docs/csv_checks/batch_001/`.

Boundaries
----------
* Read-only with respect to batch_001, the exporter, the profiles and the
  client files: this script only opens files for reading.
* The output is a *fixture*, not a data source. The app's default run mode never
  loads it; the explicit fixture mode (`npm run dev:fixture`) and the test suite
  do, and both are clearly marked as non-integration.

Usage
-----
    python3 fixtures/build_fixture_sample.py            # rewrites the fixture
    python3 fixtures/build_fixture_sample.py --check    # verify byte equality
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
BATCH_DIR = REPO_ROOT / "server" / "docs" / "csv_checks" / "batch_001"
OUT_PATH = pathlib.Path(__file__).resolve().parent / "batch001.sample.json"

# Explicit selection: 9 named rows plus every 114th row of the frozen
# items.csv (deterministic; regenerating on the same input yields the same set).
ITEM_IDS = [
    "11", "12", "9003", "9004", "9005", "9017",
    "10011", "10190", "10396", "14122", "14296", "14455",
    "20213", "20522", "20831", "21232", "22213", "25110",
    "25433", "25710", "25856", "26355", "26626", "26835",
    "27108", "27252", "27426", "27570", "27744", "27918",
    "28127", "28501", "28810", "29128", "29346", "30021",
    "30203", "30527", "41052", "41057", "43043", "50070",
    "54270", "60000", "66010", "70167", "70607", "70734",
    "70917", "71038", "71152", "71326", "71529", "71643",
    "72156", "72325", "72454", "72576", "72690", "72808",
    "72922", "73036", "73151", "73265", "73387", "73511",
    "73629", "73751", "81007",
]
PET_IDS = ["2010", "2030", "2790", "2800", "3010", "4011", "4021", "4022"]
SCENE_IDS = ["1001", "1004", "1005", "1010", "1023", "1039", "1040", "1084", "1179"]
NPC_SCENE_IDS = ["1001", "1005", "1010"]


def read_csv(relative: str) -> list[dict[str, str]]:
    path = BATCH_DIR / relative
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json(relative: str) -> Any:
    with (BATCH_DIR / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with (BATCH_DIR / relative).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def select(rows: list[dict[str, str]], column: str, wanted: list[str]) -> list[dict[str, str]]:
    wanted_set = set(wanted)
    return [row for row in rows if row.get(column) in wanted_set]


def build_batch_overview(manifest: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    tabledef = manifest["files"]
    csv_files = sum(1 for name in tabledef if name.endswith(".csv"))
    # manifest.json itself is an output of the batch, so it is added explicitly;
    # 17 CSV + 5 JSON/JSONL = 22 files, matching server/docs/csv_checks/BATCH_001.md.
    generated_files = len(tabledef) + 1
    tables = []
    for entry, stats in sorted(validation["tables"].items()):
        label_by_file = {
            "items.csv": "道具名称 / 原始描述 / 类别代码 / 图片映射",
            "pets.csv": "宠物主表",
            "pet_aptitudes.csv": "宠物资质（十个原始字段名）",
            "petskill_placeholder": "",
        }
        csv_file = {
            "1945": "items.csv",
            "2027": "pets.csv",
            "2954": "pet_aptitudes.csv",
            "3205": "pet_skills.csv",
        }.get(entry, "")
        missing = validation["missing_aptitude_count"] if entry == "2954" else None
        tables.append(
            {
                "table_key": entry,
                "label": label_by_file.get(csv_file, tabledef.get(csv_file, {}).get("notes", "")),
                "csv_file": csv_file,
                "source_entry": int(entry),
                "source_table": tabledef.get(csv_file, {}).get("source_table", ""),
                "source_records": stats["source_records"],
                "review_csv_records": stats["review_csv_records"],
                "quarantined_records": stats["quarantined_records"],
                "missing_records": missing,
                "review_status": manifest["status"],
            }
        )

    return {
        "batch_id": manifest["batch"],
        "status": manifest["status"],
        "native_verified": manifest["native_verified"],
        "review_notice": (
            "FIXTURE 子集说明：本文件仅从 batch_001 复制了少量真实行用于界面走查与自动化测试；"
            "批次级计数来自 batch_001 的 validation.json / manifest.json。它不构成接口联调结果。"
        ),
        "generated_files": generated_files,
        "csv_files": csv_files,
        "tables": tables,
        "checks": validation["checks"],
        "counters": {
            "items": validation["tables"]["1945"]["review_csv_records"],
            "pets": validation["tables"]["2027"]["review_csv_records"],
            "pet_aptitudes": validation["tables"]["2954"]["review_csv_records"],
            "pet_aptitude_missing": validation["missing_aptitude_count"],
            "pet_skills": validation["tables"]["3205"]["review_csv_records"],
            "skill_write_count": validation["skill_write_count"],
            "skill_unique_count": validation["skill_unique_count"],
            "skill_overwrite_count": validation["skill_overwrite_count"],
            "quarantined_record_count": validation["quarantined_record_count"],
            "pet_skill_names": validation["pet_skill_names"],
        },
        "ambiguous_pet_skill_names": validation["ambiguous_pet_skill_names"],
        "limitations": manifest["limitations"],
        "input_hashes": manifest["inputs"],
    }


def build_map_datasets(manifest: dict[str, Any], scenes: list[str]) -> dict[str, Any]:
    definitions = [
        ("mapdata_scene_dictionary", "maps_npcs/mapdata_scene_dictionary.csv", "scene_id", SCENE_IDS),
        ("mapdata_parent_scene", "maps_npcs/mapdata_parent_scene.csv", "scene_id", SCENE_IDS),
        (
            "sceneid2name_minimap_scenes",
            "maps_npcs/sceneid2name_minimap_scenes.csv",
            "scene_id",
            SCENE_IDS,
        ),
        (
            "npcname2realnamedata_alias_to_realname",
            "maps_npcs/npcname2realnamedata_alias_to_realname.csv",
            "alias",
            [],
        ),
    ]
    datasets = []
    for key, relative, key_column, wanted in definitions:
        all_rows = read_csv(relative)
        rows = select(all_rows, key_column, wanted) if wanted else all_rows[:6]
        meta = manifest["files"][relative]
        datasets.append(
            {
                "dataset_key": key,
                "csv_file": relative,
                "source_entry": meta.get("source_entry"),
                "source_table": meta.get("source_table"),
                "rows": len(rows),
                "total_rows_in_batch": meta.get("rows"),
                "primary_key": meta.get("primary_key", []),
                "columns": meta.get("columns", []),
                "notes": (
                    (meta.get("notes") or "")
                    + " ［FIXTURE：仅含本样本文件中的 "
                    + str(len(rows))
                    + " 行；批次内该表共 "
                    + str(meta.get("rows"))
                    + " 行。］"
                ).strip(),
                "review_status": manifest["status"],
                "rows_data": rows,
            }
        )
    return {"datasets": datasets}


def build_npc_sources(manifest: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    specs = {
        "npcposdata_2601": ("maps_npcs/npcposdata_records.csv", 2601, ["scene_id", "record_index"]),
        "minimapnpcpos_2804": (
            "maps_npcs/minimapnpcpos_pos_records.csv",
            2804,
            ["scene_id", "scene_display_name", "record_index"],
        ),
    }
    for key, (relative, entry, primary_key) in specs.items():
        all_rows = read_csv(relative)
        rows = select(all_rows, "scene_id", NPC_SCENE_IDS)
        zero = sum(1 for row in all_rows if row.get("npcid", "").strip() == "0")
        meta = manifest["files"][relative]
        out[key] = {
            "source_info": {
                "source": key,
                "source_entry": entry,
                "source_table": meta.get("source_table"),
                "csv_file": relative,
                "primary_key": primary_key,
                "total": len(all_rows),
                "total_in_fixture": len(rows),
                "zero_npcid_records": zero,
                "review_status": manifest["status"],
            },
            "rows": rows,
        }
    return out


def build_agreement() -> dict[str, Any]:
    all_rows = read_csv("maps_npcs/npc_2601_vs_2804_agreement.csv")
    counts: dict[str, int] = {}
    for row in all_rows:
        counts[row["agreement"]] = counts.get(row["agreement"], 0) + 1
    interesting = {
        "identical_sequence",
        "content_difference",
        "only_in_minimapnpcpos_2804",
        "identical_multiset_different_order",
        "only_in_npcposdata_2601",
    }
    picked: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in all_rows:
        agreement = row["agreement"]
        if agreement in interesting and agreement not in seen:
            picked.append(row)
            seen.add(agreement)
    for row in all_rows:
        if row["scene_id"] in {"1001", "1005"} and row not in picked:
            picked.append(row)
        if len(picked) >= 14:
            break
    return {"rows": picked, "agreement_counts": counts, "total_rows_in_batch": len(all_rows)}


def build_anomalies(manifest: dict[str, Any]) -> dict[str, Any]:
    quarantine = []
    for record in read_jsonl("quarantine.jsonl"):
        quarantine.append(
            {
                "anomaly_id": f"{record['entry_index']}:{record['record_key']}",
                "entry_index": record["entry_index"],
                "table": record["table"],
                "record_key": record["record_key"],
                "reasons": record["reasons"],
                "native_verified": record["native_verified"],
                "value_under_applied_profile": record["value_under_applied_profile"],
            }
        )

    ambiguous = [
        row
        for row in read_csv("pet_skill_name_matches.csv")
        if row["ambiguous"] == "true"
    ]

    return {
        "batch_id": manifest["batch"],
        "status": manifest["status"],
        "native_verified": manifest["native_verified"],
        "quarantine": quarantine,
        "missing_aptitudes": read_csv("pet_aptitude_missing.csv"),
        "ambiguous_skill_names": ambiguous,
        "skill_overwrites": read_csv("pet_skill_overwrites.csv"),
        "overwrite_evidence": read_jsonl("overwrite_evidence.jsonl"),
    }


def build() -> dict[str, Any]:
    manifest = read_json("manifest.json")
    validation = read_json("validation.json")

    all_pets = read_csv("pets.csv")
    pets = select(all_pets, "client_shape_id", PET_IDS)
    pet_id_set = {row["client_shape_id"] for row in pets}

    all_aptitudes = read_csv("pet_aptitudes.csv")
    pet_aptitudes = select(all_aptitudes, "client_shape_id", PET_IDS)

    all_candidates = read_csv("pet_skill_candidates.csv")
    pet_skill_candidates = [row for row in all_candidates if row["client_shape_id"] in pet_id_set]

    all_required = read_csv("pet_required_skills.csv")
    pet_required_skills = [row for row in all_required if row["client_shape_id"] in pet_id_set]

    referenced_names = {row["skill_name_raw"] for row in pet_skill_candidates} | {
        row["skill_name_raw"] for row in pet_required_skills
    }
    all_matches = read_csv("pet_skill_name_matches.csv")
    pet_skill_name_matches = [row for row in all_matches if row["skill_name_raw"] in referenced_names]

    matched_skill_ids = {row["skill_id"] for row in pet_skill_name_matches}
    overwrite_ids = {row["skill_id"] for row in read_csv("pet_skill_overwrites.csv")}
    all_skills = read_csv("pet_skills.csv")
    skills = [
        row
        for row in all_skills
        if row["skill_id"] in (matched_skill_ids | overwrite_ids)
    ]

    all_items = read_csv("items.csv")
    items = select(all_items, "client_shape_id", ITEM_IDS)

    maps = build_map_datasets(manifest, SCENE_IDS)
    npcs = build_npc_sources(manifest)
    agreement = build_agreement()

    payload = {
        "_fixture": {
            "kind": "ui_fixture_subset",
            "not_a_data_source": True,
            "is_integration_evidence": False,
            "warning": (
                "仅用于界面走查与自动化测试。默认运行模式（npm run dev）不加载本文件；"
                "API 失败时不会回退到这里。不要把 fixture 模式的结果当成接口联调通过。"
            ),
            "built_by": "fixtures/build_fixture_sample.py",
            "built_from": "server/docs/csv_checks/batch_001/",
            "values_are_copied_rows": True,
            "selection": {
                "item_ids": ITEM_IDS,
                "pet_ids": PET_IDS,
                "scene_ids": SCENE_IDS,
                "npc_scene_ids": NPC_SCENE_IDS,
                "pet_skill_name_filter": sorted(referenced_names),
            },
            "counts": {
                "items": len(items),
                "pets": len(pets),
                "pet_aptitudes": len(pet_aptitudes),
                "pet_skill_candidates": len(pet_skill_candidates),
                "pet_required_skills": len(pet_required_skills),
                "pet_skill_name_matches": len(pet_skill_name_matches),
                "skills": len(skills),
            },
            "source_file_sha256": {
                name: manifest["files"][name]["sha256"]
                for name in sorted(manifest["files"])
                if "sha256" in manifest["files"][name]
            },
        },
        "batch": build_batch_overview(manifest, validation),
        "items": items,
        "pets": pets,
        "pet_aptitudes": pet_aptitudes,
        "pet_aptitude_missing": read_csv("pet_aptitude_missing.csv"),
        "pet_skill_candidates": pet_skill_candidates,
        "pet_required_skills": pet_required_skills,
        "pet_skill_name_matches": pet_skill_name_matches,
        "skills": skills,
        "pet_skill_overwrites": read_csv("pet_skill_overwrites.csv"),
        "maps": maps,
        "npcs": npcs,
        "agreement": agreement,
        "anomalies": build_anomalies(manifest),
    }
    return payload


def serialise(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify byte equality instead of writing")
    args = parser.parse_args()

    text = serialise(build())

    if args.check:
        if not OUT_PATH.exists():
            print(f"missing {OUT_PATH}", file=sys.stderr)
            return 1
        current = OUT_PATH.read_text(encoding="utf-8")
        if current != text:
            print(f"{OUT_PATH} differs from freshly extracted fixture", file=sys.stderr)
            return 1
        print(f"OK: {OUT_PATH} matches ({len(text)} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()})")
        return 0

    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(text)} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
