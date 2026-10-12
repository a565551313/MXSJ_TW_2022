#!/usr/bin/env python3
"""Capture real Agent H review-API responses into `fixtures/h_api/`.

Why this exists
---------------
The review browser must be tested against the *actual* backend contract, not a
frontend-invented one. This script records real HTTP responses from Agent H's
running service (PR #22 / `server/apps/review_api`) into small JSON files, which
are then committed so unit tests can replay genuine payloads without a server.

It never invents or edits values: every file is the response body as returned by
the server, plus a sidecar entry in `manifest.json` describing exactly which
request produced it (path, query, status, response sha256).

Usage
-----
    # start Agent H's service first (see docs/review_browser/BACKEND.md), then:
    python3 fixtures/capture_h_api.py --base http://127.0.0.1:8000
    python3 fixtures/capture_h_api.py --base http://127.0.0.1:8000 --check

`--check` re-requests every capture and fails if any body differs, so the
committed evidence can be re-verified against a live backend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
OUT_DIR = HERE / "h_api"

#: H's contract paths (server/docs/review_browser/API_CONTRACT.md, v1.0.0).
PREFIX = "/api/v1/review"

#: dataset_id -> (file, sample limit). Samples are the canonical per-dataset
#: captures the replay server pages over; totals inside them are the real dataset
#: totals returned by the API. Datasets the UI browses row by row are captured
#: with limit=500 so real multi-page navigation is reproducible; datasets whose
#: whole content fits in one response are captured completely.
DATASET_SAMPLES: list[tuple[str, int]] = [
    ("items", 500),
    ("pets", 500),
    ("pet_skill_candidates", 500),
    ("pet_required_skills", 500),
    ("pet_aptitudes", 500),
    ("pet_aptitude_missing", 500),
    ("pet_skills", 500),
    ("pet_skill_overwrites", 500),
    ("pet_skill_name_matches", 500),
    ("mapdata_parent_scene", 500),
    ("mapdata_scene_dictionary", 500),
    ("minimapnpcpos_pos_records", 500),
    ("minimapnpcpos_wenzi_entries", 500),
    ("npcname2realnamedata_alias_to_realname", 500),
    ("npcposdata_records", 500),
    ("sceneid2name_minimap_scenes", 500),
]

#: Every dataset id in contract section 3.1 (metadata is captured for all of them).
DATASET_IDS: list[str] = [
    "items",
    "pets",
    "pet_skill_candidates",
    "pet_required_skills",
    "pet_aptitudes",
    "pet_aptitude_missing",
    "pet_skills",
    "pet_skill_overwrites",
    "pet_skill_name_matches",
    "mapdata_parent_scene",
    "mapdata_scene_dictionary",
    "minimapnpcpos_pos_records",
    "minimapnpcpos_wenzi_entries",
    "npc_2601_vs_2804_agreement",
    "npcname2realnamedata_alias_to_realname",
    "npcposdata_records",
    "sceneid2name_minimap_scenes",
]

#: Skills the UI can open as a detail page: every candidate-name match of the
#: demo pets (108, 118, 308, 319, 329, 355, 557, 562), the skills reached from the
#: list (101, 229) and every skill id that appears in the overwrite evidence the
#: anomalies page shows (4236, 4573-4581).
SKILL_DETAIL_IDS: list[int] = [
    101,
    108,
    118,
    229,
    308,
    319,
    329,
    355,
    557,
    562,
    4236,
    4573,
    4574,
    4575,
    4576,
    4577,
    4578,
    4579,
    4581,
]

#: (capture id, method, path, query pairs) - exactly the requests the frontend
#: issues, plus contract error cases.
CAPTURES: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    # --- batch / health / dataset metadata -----------------------------------
    ("health", "GET", f"{PREFIX}/health", []),
    ("batch", "GET", f"{PREFIX}/batch", []),
    ("datasets", "GET", f"{PREFIX}/datasets", []),
    ("dataset_meta_items", "GET", f"{PREFIX}/datasets/items", []),
    ("dataset_meta_pet_aptitudes", "GET", f"{PREFIX}/datasets/pet_aptitudes", []),
    ("dataset_meta_npcposdata_records", "GET", f"{PREFIX}/datasets/npcposdata_records", []),
    # --- item queries ---------------------------------------------------------
    ("item_11", "GET", f"{PREFIX}/datasets/items/records/11", []),
    ("item_12", "GET", f"{PREFIX}/datasets/items/records/12", []),
    ("item_41052", "GET", f"{PREFIX}/datasets/items/records/41052", []),
    ("items_q_lurong", "GET", f"{PREFIX}/datasets/items/records", [("q", "鹿茸")]),
    # --- pet queries ----------------------------------------------------------
    ("pet_2010", "GET", f"{PREFIX}/datasets/pets/records/2010", []),
    ("pet_2800", "GET", f"{PREFIX}/datasets/pets/records/2800", []),
    ("pet_3010", "GET", f"{PREFIX}/datasets/pets/records/3010", []),
    ("pet_4011", "GET", f"{PREFIX}/datasets/pets/records/4011", []),
    ("pets_q_maocaotuan", "GET", f"{PREFIX}/datasets/pets/records", [("q", "毛草團")]),
    ("aptitude_2010", "GET", f"{PREFIX}/datasets/pet_aptitudes/records", [("client_shape_id", "2010")]),
    ("aptitude_2800", "GET", f"{PREFIX}/datasets/pet_aptitudes/records", [("client_shape_id", "2800")]),
    ("aptitude_4011", "GET", f"{PREFIX}/datasets/pet_aptitudes/records", [("client_shape_id", "4011")]),
    (
        "aptitude_missing_3010",
        "GET",
        f"{PREFIX}/datasets/pet_aptitude_missing/records",
        [("client_shape_id", "3010")],
    ),
    (
        "candidates_4011",
        "GET",
        f"{PREFIX}/datasets/pet_skill_candidates/records",
        [("client_shape_id", "4011"), ("sort_by", "sequence"), ("order", "asc")],
    ),
    (
        "candidates_2010",
        "GET",
        f"{PREFIX}/datasets/pet_skill_candidates/records",
        [("client_shape_id", "2010"), ("sort_by", "sequence"), ("order", "asc")],
    ),
    (
        "candidates_2790",
        "GET",
        f"{PREFIX}/datasets/pet_skill_candidates/records",
        [("client_shape_id", "2790"), ("sort_by", "sequence"), ("order", "asc")],
    ),
    (
        "candidates_2800",
        "GET",
        f"{PREFIX}/datasets/pet_skill_candidates/records",
        [("client_shape_id", "2800"), ("sort_by", "sequence"), ("order", "asc")],
    ),
    (
        "candidates_3010",
        "GET",
        f"{PREFIX}/datasets/pet_skill_candidates/records",
        [("client_shape_id", "3010"), ("sort_by", "sequence"), ("order", "asc")],
    ),
    (
        "aptitude_3010",
        "GET",
        f"{PREFIX}/datasets/pet_aptitudes/records",
        [("client_shape_id", "3010")],
    ),
    (
        "aptitude_missing_2800",
        "GET",
        f"{PREFIX}/datasets/pet_aptitude_missing/records",
        [("client_shape_id", "2800")],
    ),
    (
        "aptitude_missing_4011",
        "GET",
        f"{PREFIX}/datasets/pet_aptitude_missing/records",
        [("client_shape_id", "4011")],
    ),
    (
        "required_2800",
        "GET",
        f"{PREFIX}/datasets/pet_required_skills/records",
        [("client_shape_id", "2800")],
    ),
    (
        "required_3010",
        "GET",
        f"{PREFIX}/datasets/pet_required_skills/records",
        [("client_shape_id", "3010")],
    ),
    (
        "required_4011",
        "GET",
        f"{PREFIX}/datasets/pet_required_skills/records",
        [("client_shape_id", "4011")],
    ),
    (
        "required_2030",
        "GET",
        f"{PREFIX}/datasets/pet_required_skills/records",
        [("client_shape_id", "2030")],
    ),
    (
        "required_2010_empty",
        "GET",
        f"{PREFIX}/datasets/pet_required_skills/records",
        [("client_shape_id", "2010")],
    ),
    # --- skill queries --------------------------------------------------------
    ("skills_q_hit", "GET", f"{PREFIX}/datasets/pet_skills/records", [("q", "高級命中")]),
    (
        "name_matches_gaoji",
        "GET",
        f"{PREFIX}/datasets/pet_skill_name_matches/records",
        [("skill_name_raw", "高級命中")],
    ),
    (
        "name_matches_zhongji",
        "GET",
        f"{PREFIX}/datasets/pet_skill_name_matches/records",
        [("skill_name_raw", "終級命中")],
    ),
    # --- anomaly endpoints ----------------------------------------------------
    ("quarantine_all", "GET", f"{PREFIX}/quarantine", []),
    ("quarantine_2954", "GET", f"{PREFIX}/quarantine", [("entry_index", "2954")]),
    (
        "quarantine_2954_2800",
        "GET",
        f"{PREFIX}/quarantine",
        [("entry_index", "2954"), ("record_key", "2800")],
    ),
    (
        "quarantine_2954_3010",
        "GET",
        f"{PREFIX}/quarantine",
        [("entry_index", "2954"), ("record_key", "3010")],
    ),
    (
        "quarantine_2954_4011",
        "GET",
        f"{PREFIX}/quarantine",
        [("entry_index", "2954"), ("record_key", "4011")],
    ),
    ("overwrites_all", "GET", f"{PREFIX}/overwrites", []),
    ("overwrites_key_4573", "GET", f"{PREFIX}/overwrites", [("key", "4573")]),
    ("missing_aptitudes", "GET", f"{PREFIX}/missing-aptitudes", []),
    ("ambiguous_skills", "GET", f"{PREFIX}/ambiguous-skills", []),
    # --- NPC / map queries ----------------------------------------------------
    (
        "npc_2601_zero_count",
        "GET",
        f"{PREFIX}/datasets/npcposdata_records/records",
        [("npcid", "0"), ("limit", "1")],
    ),
    (
        "npc_2601_total",
        "GET",
        f"{PREFIX}/datasets/npcposdata_records/records",
        [("limit", "1")],
    ),
    (
        "npc_2601_scene_1005",
        "GET",
        f"{PREFIX}/datasets/npcposdata_records/records",
        [("scene_id", "1005"), ("limit", "100")],
    ),
    (
        "npc_2804_zero_count",
        "GET",
        f"{PREFIX}/datasets/minimapnpcpos_pos_records/records",
        [("npcid", "0"), ("limit", "1")],
    ),
    (
        "npc_2804_total",
        "GET",
        f"{PREFIX}/datasets/minimapnpcpos_pos_records/records",
        [("limit", "1")],
    ),
    (
        "npc_2601_scene_1001",
        "GET",
        f"{PREFIX}/datasets/npcposdata_records/records",
        [("scene_id", "1001")],
    ),
    (
        "npc_2601_q_chefu",
        "GET",
        f"{PREFIX}/datasets/npcposdata_records/records",
        [("q", "車伕")],
    ),
    (
        "npc_2804_scene_1001",
        "GET",
        f"{PREFIX}/datasets/minimapnpcpos_pos_records/records",
        [("scene_id", "1001")],
    ),
    (
        "npc_2804_q_chefu",
        "GET",
        f"{PREFIX}/datasets/minimapnpcpos_pos_records/records",
        [("q", "車伕")],
    ),
    (
        "npc_2804_scene_1005",
        "GET",
        f"{PREFIX}/datasets/minimapnpcpos_pos_records/records",
        [("scene_id", "1005"), ("limit", "100")],
    ),
    (
        "agreement_page_1",
        "GET",
        f"{PREFIX}/datasets/npc_2601_vs_2804_agreement/records",
        [("offset", "0"), ("limit", "25")],
    ),
    (
        "agreement_scene_1001",
        "GET",
        f"{PREFIX}/datasets/npc_2601_vs_2804_agreement/records",
        [("scene_id", "1001"), ("limit", "25")],
    ),
    # --- contract error cases -------------------------------------------------
    ("error_dataset_not_found", "GET", f"{PREFIX}/datasets/unknown_table", []),
    (
        "error_record_not_found",
        "GET",
        f"{PREFIX}/datasets/items/records/999999",
        [],
    ),
    (
        "error_invalid_parameter",
        "GET",
        f"{PREFIX}/datasets/items/records",
        [("limit", "0")],
    ),
    ("error_method_not_allowed", "POST", f"{PREFIX}/batch", []),
]


def records_path(dataset_id: str, limit: int, offset: int = 0) -> tuple[str, list[tuple[str, str]]]:
    return (
        f"{PREFIX}/datasets/{dataset_id}/records",
        [("offset", str(offset)), ("limit", str(limit))],
    )


def full_capture_list() -> list[tuple[str, str, str, list[tuple[str, str]]]]:
    captures: list[tuple[str, str, str, list[tuple[str, str]]]] = []

    # Metadata for every dataset id the contract exposes (17 ids), so pages that
    # look up a dataset's columns/rows never fall back to guessing.
    for dataset_id in DATASET_IDS:
        captures.append((f"dataset_meta_{dataset_id}", "GET", f"{PREFIX}/datasets/{dataset_id}", []))


    # Canonical samples first, so the replay server always has a base sample.
    for dataset_id, limit in DATASET_SAMPLES:
        path, query = records_path(dataset_id, limit)
        captures.append((f"records_{dataset_id}_limit{limit}", "GET", path, query))

    # Whole agreement dataset: needed to compute per-category counts completely.
    for offset in (0, 500):
        path, query = records_path("npc_2601_vs_2804_agreement", 500, offset)
        captures.append((f"records_npc_2601_vs_2804_agreement_offset{offset}", "GET", path, query))

    # Per-skill detail requests: the skill row, its overwrite evidence (if any)
    # and its name matches. The UI issues exactly these three when a skill is
    # opened, so each combination is captured instead of guessed.
    for skill_id in SKILL_DETAIL_IDS:
        captures.append(
            (f"skill_record_{skill_id}", "GET", f"{PREFIX}/datasets/pet_skills/records/{skill_id}", [])
        )
        captures.append(
            (f"overwrites_key_{skill_id}", "GET", f"{PREFIX}/overwrites", [("key", str(skill_id))])
        )
        captures.append(
            (
                f"name_matches_by_skill_{skill_id}",
                "GET",
                f"{PREFIX}/datasets/pet_skill_name_matches/records",
                [("skill_id", str(skill_id))],
            )
        )

    captures.extend(CAPTURES)
    return captures


def request(base: str, method: str, path: str, query: list[tuple[str, str]]) -> tuple[int, bytes]:
    url = base.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, method=method, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:  # expected for the error-case captures
        return error.code, error.read()


def normalise(body: bytes) -> str:
    """Pretty JSON with a trailing newline; keys keep the server's order."""
    parsed: Any = json.loads(body.decode("utf-8"))
    return json.dumps(parsed, ensure_ascii=False, indent=1) + "\n"


def canonical_query(query: list[tuple[str, str]]) -> str:
    return urllib.parse.urlencode(sorted(query))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000", help="Agent H service base URL")
    parser.add_argument("--check", action="store_true", help="verify captures against a live server")
    parser.add_argument(
        "--note",
        default="Agent H review API, PR #22 head 9f6ab439a2ecdee37b59b99ddf95e77691490a0f",
        help="provenance note stored in manifest.json",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_entries: list[dict[str, Any]] = []
    failures: list[str] = []

    for capture_id, method, path, query in full_capture_list():
        status, body = request(args.base, method, path, query)
        text = normalise(body)
        target = OUT_DIR / f"{capture_id}.json"
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

        if args.check:
            if not target.exists():
                failures.append(f"{capture_id}: missing committed file")
                continue
            current = target.read_text(encoding="utf-8")
            if current != text:
                failures.append(
                    f"{capture_id}: body differs (committed {hashlib.sha256(current.encode()).hexdigest()[:12]}, "
                    f"live {digest[:12]})"
                )
        else:
            target.write_text(text, encoding="utf-8")

        manifest_entries.append(
            {
                "id": capture_id,
                "method": method,
                "path": path,
                "query": canonical_query(query),
                "status": status,
                "file": f"{capture_id}.json",
                "sha256": digest,
                "bytes": len(text.encode("utf-8")),
            }
        )

    if not args.check:
        # Drop captures that are no longer part of the set, so the committed
        # evidence can never mix old requests with new ones.
        produced = {f"{entry['id']}.json" for entry in manifest_entries}
        for stale in sorted(OUT_DIR.glob("*.json")):
            if stale.name not in produced and stale.name != "manifest.json":
                stale.unlink()
                print(f"removed stale capture {stale.name}")

    if args.check:
        if failures:
            for failure in failures:
                print(f"FAIL {failure}", file=sys.stderr)
            return 1
        print(f"OK: all {len(manifest_entries)} captures match the live backend at {args.base}")
        return 0

    manifest = {
        "_capture": {
            "produced_by": "fixtures/capture_h_api.py",
            "backend": "server/apps/review_api (Agent H)",
            "provenance": args.note,
            "contract": "server/docs/review_browser/API_CONTRACT.md v1.0.0",
            "note": (
                "Real HTTP responses committed as test evidence. Records arrays for large datasets are "
                "the first N rows (limit shown in the query); 'total' is the real dataset total. "
                "Bodies are byte-stable: re-running --check against the same backend commit must match."
            ),
            "capture_count": len(manifest_entries),
        },
        "captures": manifest_entries,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    total = sum(entry["bytes"] for entry in manifest_entries)
    print(f"wrote {len(manifest_entries)} captures ({total} bytes) into {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
