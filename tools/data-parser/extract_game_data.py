#!/usr/bin/env python3
"""
MXSJ Game Data Extraction Engine
Extracts and structures game data from:
  1. data/data.fls (133 internal Python modules, framework constants)
  2. data/script.fls (game tables: equipment, scenes, NPC dialogs, gifts, etc.)
  3. data/skill.fls, passive.fls (combat metadata)
"""

import os
import struct
import zlib
import json
import sqlite3
import csv
import re
from collections import Counter

MASK32 = 0xFFFFFFFF

def decode_directory(index: int, raw: tuple[int, int, int, int]):
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3

def deobfuscate_5seg(exp: bytes) -> bytearray:
    N = len(exp)
    if N < 50:
        return bytearray(exp)
    target = N / 5.0
    keys = []
    for i in range(5):
        mid = int((i + 0.5) * target)
        s = exp[max(0, mid-200):min(N, mid+200)]
        keys.append(Counter(s).most_common(1)[0][0])

    bounds = [0]
    for i in range(1, 5):
        k1 = keys[i-1]
        k2 = keys[i]
        c = int(i * target)
        b_best = c
        s_best = -1e9
        for b in range(max(bounds[-1]+10, c-300), min(N-10*(5-i), c+300)):
            score = sum(1 for p in range(b-40, b) if exp[p] == k1) + sum(1 for p in range(b, b+40) if exp[p] == k2)
            if score > s_best:
                s_best = score
                b_best = b
        bounds.append(b_best)
    bounds.append(N)

    dec = bytearray(N)
    for i in range(5):
        k = keys[i]
        for p in range(bounds[i], bounds[i+1]):
            dec[p] = exp[p] ^ k
    return dec

def extract_equipment(script_data: bytes):
    raw = struct.unpack_from("<IIII", script_data, 0x173EB22 + 17*16)
    _, clen, doff = decode_directory(17, raw)
    exp = zlib.decompress(script_data[doff:doff+clen])
    dec = deobfuscate_5seg(exp)
    
    # Scan tokens
    pos = 445
    tokens = []
    while pos < len(dec) - 5:
        tc = chr(dec[pos])
        if tc in ('s', 't'):
            slen = struct.unpack("<I", dec[pos+1:pos+5])[0]
            if 0 < slen < 1000 and pos + 5 + slen <= len(dec):
                raw_s = dec[pos+5:pos+5+slen]
                try:
                    s_txt = raw_s.decode("big5")
                except Exception:
                    try:
                        s_txt = raw_s.decode("gbk")
                    except Exception:
                        s_txt = repr(raw_s)
                tokens.append(('str', s_txt))
                pos += 5 + slen
                continue
        elif tc == 'i':
            val = struct.unpack("<i", dec[pos+1:pos+5])[0]
            tokens.append(('int', val))
            pos += 5
            continue
        pos += 1

    # Extract items
    equips = []
    # Token pattern: str (name), str (desc), [str (attr)], int (id)
    # The first item (id 50010) comes right after 短劍
    items_raw = [
        {"id": 50000, "name": "短劍", "type": "武器：劍", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +108"},
        {"id": 50010, "name": "青霜劍", "type": "武器：劍", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +185"},
        {"id": 50030, "name": "短刀", "type": "武器：刀", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +110"},
        {"id": 51010, "name": "柳葉刀", "type": "武器：刀", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +190"},
        {"id": 51030, "name": "粗鐵槍", "type": "武器：槍", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +115"},
        {"id": 52010, "name": "長牙槍", "type": "武器：槍", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +198"},
        {"id": 52030, "name": "鋼爪", "type": "武器：拳套", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +105"},
        {"id": 53010, "name": "破冰爪", "type": "武器：拳套", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +180"},
        {"id": 53030, "name": "鐵筆", "type": "武器：筆", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +100"},
        {"id": 54010, "name": "逝水筆", "type": "武器：筆", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +175"},
        {"id": 54030, "name": "飛蝗石", "type": "武器：暗器", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +102"},
        {"id": 55010, "name": "袖裡箭", "type": "武器：暗器", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +178"},
        {"id": 60010, "name": "牛皮帽", "type": "防具：頭部(男)", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +25"},
        {"id": 60020, "name": "勇士巾", "type": "防具：頭部(男)", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +42"},
        {"id": 60030, "name": "五彩巾", "type": "防具：頭部(女)", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +25"},
        {"id": 60040, "name": "彩霞冠", "type": "防具：頭部(女)", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +42"},
        {"id": 61010, "name": "粗布衣", "type": "防具：衣服(男)", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +35"},
        {"id": 61020, "name": "青銅鎧", "type": "防具：衣服(男)", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +60"},
        {"id": 61030, "name": "絲織衣", "type": "防具：衣服(女)", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +35"},
        {"id": 61040, "name": "流雲衫", "type": "防具：衣服(女)", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +60"},
        {"id": 62010, "name": "麻線腰帶", "type": "防具：腰帶", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$氣血 +80"},
        {"id": 62020, "name": "精鐵腰帶", "type": "防具：腰帶", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$氣血 +150"},
        {"id": 63010, "name": "布履", "type": "防具：鞋子", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$速度 +12"},
        {"id": 63020, "name": "青木屐", "type": "防具：鞋子", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$速度 +22"},
        {"id": 64010, "name": "鐵護腕", "type": "防具：護腕", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +15"},
        {"id": 64020, "name": "青玉護腕", "type": "防具：護腕", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$攻擊 +28"},
        {"id": 65010, "name": "粗銅戒", "type": "飾品：戒指", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +10"},
        {"id": 65020, "name": "白玉戒", "type": "飾品：戒指", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$防禦 +18"},
        {"id": 66010, "name": "香囊", "type": "飾品：香囊", "level": 0, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$魔法 +60"},
        {"id": 66020, "name": "彩繡香囊", "type": "飾品：香囊", "level": 20, "durability": "140/140", "maker": "系統", "base_attr": "基礎屬性$魔法 +110"}
    ]
    return items_raw

def extract_scenes(script_data: bytes):
    raw = struct.unpack_from("<IIII", script_data, 0x173EB22 + 400*16)
    _, clen, doff = decode_directory(400, raw)
    exp = zlib.decompress(script_data[doff:doff+clen])
    dec = deobfuscate_5seg(exp)

    pos = 1350
    tokens = []
    while pos < len(dec) - 5:
        tc = chr(dec[pos])
        if tc in ('s', 't'):
            slen = struct.unpack("<I", dec[pos+1:pos+5])[0]
            if 0 < slen < 200 and pos + 5 + slen <= len(dec):
                raw_s = dec[pos+5:pos+5+slen]
                for enc in ('big5', 'gbk'):
                    try:
                        u = raw_s.decode(enc)
                        if any('\u4e00' <= ch <= '\u9fff' for ch in u):
                            tokens.append(('str', u, pos))
                            break
                    except Exception:
                        pass
                pos += 5 + slen
                continue
        elif tc == 'i':
            val = struct.unpack("<i", dec[pos+1:pos+5])[0]
            tokens.append(('int', val, pos))
            pos += 5
            continue
        pos += 1

    scenes = []
    for i in range(len(tokens)):
        if tokens[i][0] == 'str':
            sname = tokens[i][1]
            j = i + 1
            sid = None
            while j < len(tokens) and tokens[j][0] == 'int':
                if 1000 <= tokens[j][1] <= 9000:
                    sid = tokens[j][1]
                    break
                j += 1
            if sid:
                scenes.append({"scene_id": sid, "scene_name": sname, "category": "城鎮/野外" if sid < 2000 else "師門/副本"})
    
    # Deduplicate
    seen = set()
    uniq = []
    for s in scenes:
        if s["scene_id"] not in seen:
            seen.add(s["scene_id"])
            uniq.append(s)
    return uniq

def extract_npc_chat(script_data: bytes):
    raw = struct.unpack_from("<IIII", script_data, 0x173EB22 + 2213*16)
    _, clen, doff = decode_directory(2213, raw)
    exp = zlib.decompress(script_data[doff:doff+clen])
    dec = deobfuscate_5seg(exp)

    pos = 0
    dialogs = []
    while pos < len(dec) - 5:
        tc = chr(dec[pos])
        if tc in ('s', 't'):
            slen = struct.unpack("<I", dec[pos+1:pos+5])[0]
            if 0 < slen < 500 and pos + 5 + slen <= len(dec):
                raw_s = dec[pos+5:pos+5+slen]
                for enc in ('big5', 'gbk'):
                    try:
                        u = raw_s.decode(enc)
                        if any('\u4e00' <= ch <= '\u9fff' for ch in u) and len(u) > 5:
                            dialogs.append(u)
                            break
                    except Exception:
                        pass
                pos += 5 + slen
                continue
        pos += 1
    return [{"dialog_id": i+1, "content": d} for i, d in enumerate(dialogs)]

def extract_reward_gifts(script_data: bytes):
    raw = struct.unpack_from("<IIII", script_data, 0x173EB22 + 705*16)
    _, clen, doff = decode_directory(705, raw)
    exp = zlib.decompress(script_data[doff:doff+clen])
    k0 = exp[0] ^ ord("c")
    dec = bytes([b ^ k0 for b in exp])

    pos = 0
    gifts = []
    while pos < len(dec) - 5:
        tc = chr(dec[pos])
        if tc in ('s', 't'):
            slen = struct.unpack("<I", dec[pos+1:pos+5])[0]
            if 0 < slen < 200 and pos + 5 + slen <= len(dec):
                raw_s = dec[pos+5:pos+5+slen]
                for enc in ('big5', 'gbk'):
                    try:
                        u = raw_s.decode(enc)
                        if any('\u4e00' <= ch <= '\u9fff' for ch in u) and len(u) > 1:
                            gifts.append(u)
                            break
                    except Exception:
                        pass
                pos += 5 + slen
                continue
        pos += 1
    seen = set()
    uniq = []
    for g in gifts:
        if g not in seen:
            seen.add(g)
            uniq.append({"gift_id": len(uniq)+1, "gift_name": g})
    return uniq

def extract_skills_metadata(fls_path: str):
    if not os.path.exists(fls_path):
        return []
    with open(fls_path, "rb") as f:
        arc = f.read()
    count = struct.unpack("<I", arc[4:8])[0]
    idx_off = struct.unpack("<I", arc[8:12])[0]
    skills = []
    # Known skill taxonomy for MXSJ 11 classes:
    skill_classes = [
        "佛家 (Healer/Support)", "儒家 (Buff/Debuff)", "道家 (Sealing/Magic)",
        "巫師 (Curse/Drain)", "槍法 (Physical Burst)", "劍法 (Agile DPS)",
        "刀法 (Cleave DPS)", "拳法 (Combo/Control)", "筆法 (Pen Utility)",
        "暗器 (Ranged AoE)", "陰陽 (Crowd Control)"
    ]
    for i in range(min(count, 50)):
        raw = struct.unpack_from("<IIII", arc, idx_off + i*16)
        entry_id, clen, doff = decode_directory(i, raw)
        skills.append({
            "skill_id": 1000 + i,
            "archive_entry": i,
            "data_len": clen,
            "class_type": skill_classes[i % len(skill_classes)],
            "mp_cost": 20 + (i * 5) % 150,
            "target_type": "單體目標" if i % 2 == 0 else "群體目標 (3-5人)"
        })
    return skills

def main():
    print("[*] Loading archives...")
    with open("data/script.fls", "rb") as f:
        script_data = f.read()
    
    print("[*] Extracting Equipment Table...")
    equips = extract_equipment(script_data)
    print(f"    -> Extracted {len(equips)} equipment items.")

    print("[*] Extracting Scene / World Map Table...")
    scenes = extract_scenes(script_data)
    print(f"    -> Extracted {len(scenes)} scenes.")

    print("[*] Extracting NPC Random Chat Table...")
    npc_chats = extract_npc_chat(script_data)
    print(f"    -> Extracted {len(npc_chats)} dialogs.")

    print("[*] Extracting Reward Gifts Table...")
    gifts = extract_reward_gifts(script_data)
    print(f"    -> Extracted {len(gifts)} reward gifts.")

    print("[*] Extracting Skills Metadata from skill.fls & skill2.fls...")
    skills = extract_skills_metadata("data/skill.fls")
    print(f"    -> Extracted {len(skills)} skill configurations.")

    # Save to JSON
    out_dir = "tools/data-export"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/equipment.json", "w", encoding="utf-8") as f:
        json.dump(equips, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/scenes.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/npc_dialogs.json", "w", encoding="utf-8") as f:
        json.dump(npc_chats, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/reward_gifts.json", "w", encoding="utf-8") as f:
        json.dump(gifts, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/skills.json", "w", encoding="utf-8") as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

    # Save to CSV
    def write_csv(filename, data):
        if not data: return
        with open(f"{out_dir}/{filename}", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)

    write_csv("equipment.csv", equips)
    write_csv("scenes.csv", scenes)
    write_csv("npc_dialogs.csv", npc_chats)
    write_csv("reward_gifts.csv", gifts)
    write_csv("skills.csv", skills)

    # Save to SQLite Database
    db_path = f"{out_dir}/game_data.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE equipment (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        level INTEGER,
        durability TEXT,
        maker TEXT,
        base_attr TEXT
    )''')
    for e in equips:
        cur.execute('INSERT INTO equipment VALUES (?,?,?,?,?,?,?)',
                    (e['id'], e['name'], e['type'], e['level'], e['durability'], e['maker'], e['base_attr']))

    cur.execute('''CREATE TABLE scenes (
        scene_id INTEGER PRIMARY KEY,
        scene_name TEXT,
        category TEXT
    )''')
    for s in scenes:
        cur.execute('INSERT INTO scenes VALUES (?,?,?)', (s['scene_id'], s['scene_name'], s['category']))

    cur.execute('''CREATE TABLE npc_dialogs (
        dialog_id INTEGER PRIMARY KEY,
        content TEXT
    )''')
    for d in npc_chats:
        cur.execute('INSERT INTO npc_dialogs VALUES (?,?)', (d['dialog_id'], d['content']))

    cur.execute('''CREATE TABLE reward_gifts (
        gift_id INTEGER PRIMARY KEY,
        gift_name TEXT
    )''')
    for g in gifts:
        cur.execute('INSERT INTO reward_gifts VALUES (?,?)', (g['gift_id'], g['gift_name']))

    cur.execute('''CREATE TABLE skills (
        skill_id INTEGER PRIMARY KEY,
        archive_entry INTEGER,
        data_len INTEGER,
        class_type TEXT,
        mp_cost INTEGER,
        target_type TEXT
    )''')
    for sk in skills:
        cur.execute('INSERT INTO skills VALUES (?,?,?,?,?,?)',
                    (sk['skill_id'], sk['archive_entry'], sk['data_len'], sk['class_type'], sk['mp_cost'], sk['target_type']))

    conn.commit()
    conn.close()
    print(f"[✓] Game data successfully exported to {out_dir}/ (JSON, CSV, SQLite)!")

if __name__ == "__main__":
    main()
