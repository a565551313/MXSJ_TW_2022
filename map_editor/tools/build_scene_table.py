#!/usr/bin/env python3
"""Regenerate ``data/scenes_tw_v2_27_2.json`` from repository ground truth.

Combines verified static tables without executing any game bytecode:
1. ``server/docs/csv_checks/staging/mapdata_scene_dictionary.csv`` (entry 1301)
2. ``server/docs/csv_checks/staging/sceneid2name_minimap_scenes.csv`` (entry 400)
3. ``server/docs/csv_checks/staging/npcposdata_records.csv`` (entry 2601)
4. ``server/docs/csv_checks/staging/npcname2realnamedata_alias_to_realname.csv`` (1799)
5. ``server/docs/csv_checks/staging/minimapnpcpos_pos_records.csv`` (entry 2804)
6. ``tools/data-export/scenes.json``
7. Static constant extraction (``Py25MarshalWalker``, no ``eval``/``exec``) from
   ``data/script.fls``:
   * entry ``4589`` (``mxgame/map/map.py``): ``NEW_RPL_MAP``, ``RPL_MAP_BLK``
   * entry ``4532`` (``data/minimap_data.py``): ``DATA`` (scene portals / ``jumpPos``)
   * entry ``2428`` (``data/mappos.py``): ``MAPNAME2POS`` (arrival coordinates)
   * entry ``4495`` (``data/scenename2sounddata.py``): ``DATA`` (scene BGM ids)
   * entry ``595``  (``data/yardtable/yardmaptable.py``): ``DATA`` (courtyard maps)
   * entry ``633``  (``data/fubenmapdata.py``): ``DATA`` (dungeon resource ids)
   * entry ``2558`` (``mxgame/map/mapdefine.py``): special home/guild/kitchen ids
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path


def _dec(blob: object) -> str:
    if isinstance(blob, str):
        return blob
    if isinstance(blob, bytes):
        for enc in ("cp950", "big5-hkscs", "gb18030"):
            try:
                return blob.decode(enc)
            except UnicodeDecodeError:
                continue
        return blob.decode("latin1", errors="replace")
    return str(blob)


@lru_cache(maxsize=4)
def _archive_for(repo: Path):
    import map_npc_reproduction as mnr  # type: ignore[import-not-found]

    return mnr.Archive(repo)


def _extract_fls_tables(repo: Path, idx: int) -> dict[str, object]:
    tools_dir = repo / "server" / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    import map_npc_reproduction as mnr  # type: ignore[import-not-found]

    arc = _archive_for(repo.resolve())
    meta = arc.keydb[str(idx)]
    bounds = mnr.CANDIDATE_BOUNDS.get(idx) or meta["bounds"]
    decoded = mnr.xor_decode(arc.payload(idx), meta["keys"], bounds)
    co = mnr.Py25MarshalWalker(decoded).read()
    tables, _ = mnr.extract_assignments(co)
    return {_dec(k): v["value"] for k, v in tables.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="../..", help="仓库根目录")
    ap.add_argument("--out", default="data/scenes_tw_v2_27_2.json")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    staging = repo / "server" / "docs" / "csv_checks" / "staging"
    scene_csv = staging / "mapdata_scene_dictionary.csv"
    mini_csv = staging / "sceneid2name_minimap_scenes.csv"
    npc_csv = staging / "npcposdata_records.csv"
    alias_csv = staging / "npcname2realnamedata_alias_to_realname.csv"
    minimap_npc_csv = staging / "minimapnpcpos_pos_records.csv"
    scenes_json_path = repo / "tools" / "data-export" / "scenes.json"

    for p in (scene_csv, mini_csv):
        if not p.is_file():
            raise SystemExit(f"[错误] 找不到 {p}")

    scenes: dict[str, dict] = {}
    name_to_ids: dict[str, list[str]] = defaultdict(list)
    with scene_csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            key = f"{int(row['scene_id']):04d}"
            scenes[key] = {
                "name": row["name"],
                "w": int(row["w"]),
                "h": int(row["h"]),
            }
            name_to_ids[row["name"]].append(key)

    minimap: dict[str, str] = {}
    with mini_csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            k = f"{int(row['scene_id']):04d}"
            minimap[k] = row["name"]
            if k not in scenes:
                scenes[k] = {"name": row["name"], "w": None, "h": None}
            name_to_ids[row["name"]].append(k)

    if scenes_json_path.is_file():
        for entry in json.loads(scenes_json_path.read_text(encoding="utf-8")):
            k = f"{int(entry['scene_id']):04d}"
            sname = entry["scene_name"]
            if k not in scenes:
                scenes[k] = {"name": sname, "w": None, "h": None}
            scenes[k]["category"] = entry.get("category", "")
            name_to_ids[sname].append(k)

    # Pull static tables from data/script.fls if present in the repo checkout.
    new_rpl_map: dict[str, str] = {}
    rpl_map_blk: dict[str, str] = {}
    portals_by_key: dict[str, list[dict]] = defaultdict(list)
    arrival_by_key: dict[str, list[int]] = {}
    bgm_by_name: dict[str, str] = {}

    if not (repo / "data" / "script.fls").is_file():
        print(
            "[警告] 找不到 data/script.fls：静态替换表、传送点、到达格与 BGM "
            "不会从客户端脚本提取；生成的场景表可能不完整。",
            file=sys.stderr,
        )
    else:
        t_map = _extract_fls_tables(repo, 4589)
        for src_id, dst_raw in dict(t_map.get("NEW_RPL_MAP", {})).items():  # type: ignore[arg-type]
            new_rpl_map[f"{int(src_id):04d}"] = _dec(dst_raw)
        for src_id, dst_raw in dict(t_map.get("RPL_MAP_BLK", {})).items():  # type: ignore[arg-type]
            rpl_map_blk[f"{int(src_id):04d}"] = _dec(dst_raw)

        t_mini = _extract_fls_tables(repo, 4532)
        for raw_sid, pts in dict(t_mini.get("DATA", {})).items():  # type: ignore[arg-type]
            sid = 1054 if int(raw_sid) == 30 else int(raw_sid)
            skey = f"{sid:04d}"
            for coord, info in sorted(pts.items()):
                info_dec = {_dec(ik): iv for ik, iv in info.items()}
                jpos = info_dec.get("jumpPos") or coord
                portals_by_key[skey].append(
                    {
                        "sx": int(coord[0]),
                        "sy": int(coord[1]),
                        "jump_sx": int(jpos[0]),
                        "jump_sy": int(jpos[1]),
                        "name": _dec(info_dec.get("name") or b""),
                        "desc": _dec(info_dec.get("desc") or b""),
                        "npc_id": info_dec.get("npcID"),
                    }
                )

        t_pos = _extract_fls_tables(repo, 2428)
        for raw_name, coord in dict(t_pos.get("MAPNAME2POS", {})).items():  # type: ignore[arg-type]
            sname = _dec(raw_name)
            for k in name_to_ids.get(sname, ()):
                arrival_by_key[k] = [int(coord[0]), int(coord[1])]

        t_bgm = _extract_fls_tables(repo, 4495)
        for raw_name, raw_bgm in dict(t_bgm.get("DATA", {})).items():  # type: ignore[arg-type]
            bgm_by_name[_dec(raw_name)] = _dec(raw_bgm)

        t_yard = _extract_fls_tables(repo, 595)
        for yid, yinfo in dict(t_yard.get("DATA", {})).items():  # type: ignore[arg-type]
            yk = f"{int(yid):04d}"
            yd = {_dec(ik): iv for ik, iv in yinfo.items()}
            msz = yd.get("mapsize") or (None, None)
            grade = yd.get("grade", "")
            scenes.setdefault(
                yk,
                {
                    "name": f"玩家庭院 ({grade}級)",
                    "w": msz[0],
                    "h": msz[1],
                    "category": "家園/庭院",
                },
            )

        t_fuben = _extract_fls_tables(repo, 633)
        for fid in list(t_fuben.get("DATA", ())):  # type: ignore[arg-type]
            fk = f"{int(fid):04d}"
            scenes.setdefault(
                fk,
                {
                    "name": f"副本場景 ({fk})",
                    "w": None,
                    "h": None,
                    "category": "師門/副本",
                },
            )

        t_def = _extract_fls_tables(repo, 2558)
        special_labels = {
            "1000": "系統測試底圖 (1000)",
            "1038": "迷宮/地宮備用底圖 (1038)",
            "1046": "古塔備用底圖 (1046)",
            "1048": "迷宮備用底圖 (1048)",
            "1050": "地宮備用底圖 (1050)",
            "1056": "活動備用底圖 (1056)",
            "1160": "英靈殿關聯底圖 (1160)",
            "1325": "新手劇情場景 (1325)",
            "2001": "戰鬥背景底圖 (2001)",
            "2002": "戰鬥背景底圖 (2002)",
            "2123": "玩家之家室內 (2123)",
            "2124": "玩家豪宅室內 (2124)",
            "2125": "玩家閣樓室內 (2125)",
            "2201": _dec(t_def.get("GROUP_MAP_ATUOFIND_NAME", "幫派地圖")),
            "2202": "幫戰比武場",
            "2203": "幫派總壇內殿 (2203)",
            "2302": "師道殿室內 (十二門派共用)",
            "2303": scenes.get("2303", {}).get("name") or "室內大廳 (2303)",
            "2423": "夢想廚房 (2423)",
            "2505": "大型主題庭院 (2505)",
        }
        for sk, sname in special_labels.items():
            scenes.setdefault(sk, {"name": sname, "w": None, "h": None})

    # Attach NPCs from verified staging CSVs (server scene 30 -> map 1054 明月城).
    alias_to_real: dict[str, str] = {}
    if alias_csv.is_file():
        with alias_csv.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                alias_to_real[row["alias"]] = row["real_name"]

    npcs_by_key: dict[str, list[dict]] = defaultdict(list)
    seen_npc_keys: set[tuple[str, int, int, str]] = set()
    if npc_csv.is_file():
        with npc_csv.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                raw_scene = int(row["scene_id"])
                mapped_id = 1054 if raw_scene == 30 else raw_scene
                skey = f"{mapped_id:04d}"
                if not row.get("x") or not row.get("y"):
                    continue
                sx, sy = int(row["x"]), int(row["y"])
                disp = row.get("display_name") or ""
                real = (
                    row.get("real_name")
                    or alias_to_real.get(disp)
                    or disp
                )
                sig = (skey, sx, sy, real)
                if sig in seen_npc_keys:
                    continue
                seen_npc_keys.add(sig)
                npcs_by_key[skey].append(
                    {
                        "npc_id": int(row["npcid"]),
                        "name": real,
                        "alias": disp if disp != real else "",
                        "sx": sx,
                        "sy": sy,
                        "dir": int(row["field5"]) if row.get("field5") else 0,
                        "shape": str(row.get("shape") or ""),
                    }
                )

    if minimap_npc_csv.is_file():
        with minimap_npc_csv.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                raw_scene = int(row["scene_id"])
                mapped_id = 1054 if raw_scene == 30 else raw_scene
                skey = f"{mapped_id:04d}"
                sdisp = row.get("scene_display_name") or ""
                if sdisp and skey not in scenes:
                    scenes[skey] = {"name": sdisp, "w": None, "h": None}
                if not row.get("x") or not row.get("y"):
                    continue
                sx, sy = int(row["x"]), int(row["y"])
                disp = row.get("display_name") or ""
                real = (
                    row.get("real_name")
                    or alias_to_real.get(disp)
                    or disp
                )
                sig = (skey, sx, sy, real)
                if sig in seen_npc_keys:
                    continue
                seen_npc_keys.add(sig)
                npcs_by_key[skey].append(
                    {
                        "npc_id": int(row["npcid"]),
                        "name": real,
                        "alias": disp if disp != real else "",
                        "sx": sx,
                        "sy": sy,
                        "dir": int(row["field5"]) if row.get("field5") else 0,
                        "shape": str(row.get("shape") or ""),
                    }
                )

    for k, row in scenes.items():
        bgm = bgm_by_name.get(row["name"])
        if bgm:
            row["bgm"] = bgm
        if k in new_rpl_map:
            row["active_map_stem"] = new_rpl_map[k]
        if k in arrival_by_key:
            row["arrival_cell"] = arrival_by_key[k]
        if k in portals_by_key:
            row["portals"] = portals_by_key[k]
        if k in npcs_by_key:
            row["npcs"] = npcs_by_key[k]

    sizes = {
        (v["w"], v["h"])
        for v in scenes.values()
        if v.get("w") is not None and v.get("h") is not None
    }
    doc = {
        "schema": 2,
        "source": (
            "data/script.fls entries 400, 595, 633, 1301, 1799, 2428, 2558, "
            "2601, 2804, 4495, 4532, 4589"
        ),
        "client": "MXSJ TW v2.27.2",
        "note": (
            "Regenerate with tools/build_scene_table.py; "
            "the editor works without this file."
        ),
        "scene_count": len(scenes),
        "distinct_sizes": len(sizes),
        "new_rpl_map": dict(sorted(new_rpl_map.items())),
        "rpl_map_blk": dict(sorted(rpl_map_blk.items())),
        "scenes": dict(sorted(scenes.items())),
        "minimap_names": dict(sorted(minimap.items())),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    total_npcs = sum(len(v) for v in npcs_by_key.values())
    total_portals = sum(len(v) for v in portals_by_key.values())
    print(
        f"写出 {out}: {len(scenes)} 个场景, {len(sizes)} 种尺寸, "
        f"{len(minimap)} 个小地图名, {len(new_rpl_map)} 条 NEW_RPL_MAP, "
        f"{total_portals} 个传送点, {total_npcs} 个 NPC"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
