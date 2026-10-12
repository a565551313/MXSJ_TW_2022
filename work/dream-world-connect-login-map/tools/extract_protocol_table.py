#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the authoritative C2GS/GS2C opcode table from `data/script.fls` entry 3970.

Why this exists
---------------
The old `notes/protocol-commands-values.md` listed 5 hand-copied command numbers
(0x0001/0x0002/0x0003/0x0010/0x00FF) with **no evidence source** (WI-013).  The real
table lives in the client script `script\\protocol.py` = `data/script.fls` entry
**3970**.  This tool reads it out of the archive itself, so the numbers stop being
"claimed" and become reproducible.

How it works (no guessing)
--------------------------
entry 3970 is a flat constant module: 413 `co_names` (incl. `__doc__`) and a
`co_code` of exactly 2476 bytes = 412 x (LOAD_CONST 3B + STORE_NAME 3B).  So the
name<->value pairing can be recovered by linearly walking the instruction stream
with the hand-verified S-box map in `pydis26.py` (HAVE_ARGUMENT = 0x5F).

Nothing here executes recovered game code; it only decodes marshal + bytecode.

Usage
-----
    # decode + extract from the real archive (writes artifacts next to this tool)
    python3 tools/extract_protocol_table.py

    # extract from an already-decoded marshal
    python3 tools/extract_protocol_table.py --marshal /tmp/entry3970.marshal.bin

    # also diff against constants hardcoded in the repo's mock server
    python3 tools/extract_protocol_table.py --cross-check-mock ../../mock_server.py
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
REPO = CASE.parent.parent
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(HERE))

from fls_batch_decoder import MarshalReader  # noqa: E402
import pydis26  # noqa: E402

ENTRY = 3970
HAVE_ARGUMENT = 0x5F  # guest VM threshold, see notes/opcode_mapping_and_decompilation.md


def decode_entry(archive: Path, index: int, outdir: Path) -> Path:
    """Run the repo's own decoder; do not reimplement the 5-segment XOR here."""
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(REPO / "tools" / "fls_batch_decoder.py"),
         "--archive", str(archive), "--index", str(index), "--output", str(outdir)],
        check=True, capture_output=True, text=True,
    )
    hits = sorted(outdir.glob(f"entry{index}.marshal.bin"))
    if not hits:
        raise SystemExit(f"decoder produced no marshal for entry {index}")
    return hits[0]


def walk_assignments(marshal_path: Path):
    """Yield (offset, name, value, encoding_bytes) for every `NAME = <int const>`."""
    root = MarshalReader(marshal_path.read_bytes()).read()
    names = [pydis26.s(x) for x in root["names"]]
    consts = root["consts"]
    code = root["code"]
    i, n, pairs, unknown = 0, len(code), [], []
    while i < n:
        enc = code[i]
        if enc not in pydis26.MAP:
            unknown.append((i, enc))
            i += 1
            continue
        std, has = pydis26.MAP[enc]
        op = code[i + 1] | (code[i + 2] << 8) if has else None
        if std == 100:  # LOAD_CONST
            if i + 3 < n and code[i + 3] in pydis26.MAP:
                std2, has2 = pydis26.MAP[code[i + 3]]
                if has2 and std2 in (90, 96):  # STORE_NAME / STORE_GLOBAL
                    op2 = code[i + 4] | (code[i + 5] << 8)
                    value = consts[op] if op < len(consts) else None
                    nm = names[op2] if op2 < len(names) else None
                    pairs.append({
                        "offset": i,
                        "name": nm,
                        "value": value,
                        "is_int": isinstance(value, int) and not isinstance(value, bool),
                        "load_const_enc": "0x%02x" % enc,
                        "store_enc": "0x%02x" % code[i + 3],
                    })
                    i += 6
                    continue
        i += 3 if has else 1
    return root, pairs, unknown


def cross_check_mock(mock_path: Path, table: dict) -> list[dict]:
    """Compare `NAME = <int>` literals in a Python file against the client table."""
    rows = []
    for m in re.finditer(r"^(C2GS_[A-Z0-9_]+|GS2C_[A-Z0-9_]+)\s*=\s*(\d+)\s*$",
                         mock_path.read_text(encoding="utf-8", errors="replace"),
                         re.MULTILINE):
        name, val = m.group(1), int(m.group(2))
        real = table.get(name)
        rows.append({
            "name": name,
            "mock_value": val,
            "client_value": real,
            "status": "match" if real == val
                      else ("missing_in_client" if real is None else "MISMATCH"),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", default=str(REPO / "data" / "script.fls"))
    ap.add_argument("--marshal", help="skip decoding, read this marshal directly")
    ap.add_argument("--outdir", default=str(CASE / "artifacts" / "protocol_table"))
    ap.add_argument("--cross-check-mock", action="append", default=[],
                    help="python file with hardcoded C2GS_/GS2C_ constants to diff")
    args = ap.parse_args()

    if args.marshal:
        marshal_path = Path(args.marshal)
    else:
        with tempfile.TemporaryDirectory() as td:
            marshal_path = decode_entry(Path(args.archive), ENTRY, Path(td) / "dec")
            data = marshal_path.read_bytes()
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        marshal_path = outdir / f"entry{ENTRY}.marshal.bin"
        marshal_path.write_bytes(data)

    root, pairs, unknown = walk_assignments(marshal_path)
    filename = pydis26.s(root["filename"])
    table, non_int = {}, []
    for p in pairs:
        if p["is_int"]:
            table[p["name"]] = p["value"]
        else:
            non_int.append(p)

    # docstring is names[0]; report it to prove we decoded the right module.
    # NOTE: pydis26.s() tries big5hkscs first, which mangles GBK strings.  This
    # archive mixes encodings (entry 3970 is GBK, the item/pet tables are CP950),
    # so always show the raw bytes and both decodings.
    doc = root["consts"][0] if root["consts"] else b""
    doc_readings = {}
    if isinstance(doc, bytes):
        for enc in ("gbk", "cp950", "big5hkscs", "utf-8"):
            try:
                doc_readings[enc] = doc.decode(enc)
            except Exception:
                doc_readings[enc] = None

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / "protocol_opcodes.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "value", "direction", "code_offset",
                    "load_const_enc", "store_enc"])
        for p in sorted(pairs, key=lambda x: x["offset"]):
            if not p["is_int"]:
                continue
            direction = ("C2GS" if p["name"].startswith("C2GS_")
                         else "GS2C" if p["name"].startswith("GS2C_") else "?")
            w.writerow([p["name"], p["value"], direction, p["offset"],
                        p["load_const_enc"], p["store_enc"]])

    json_path = outdir / "protocol_opcodes.json"
    json_path.write_text(json.dumps({
        "source": {"archive": str(args.archive), "entry": ENTRY,
                   "client_filename": filename,
                   "module_docstring_raw_hex": doc.hex() if isinstance(doc, bytes) else None,
                   "module_docstring_decodings": doc_readings,
                   "co_names": len(root["names"]), "co_consts": len(root["consts"]),
                   "co_code_len": len(root["code"])},
        "method": "linear co_code walk with pydis26.MAP (HAVE_ARGUMENT=0x5F); "
                  "LOAD_CONST+STORE_NAME pairing; no game code executed",
        "counts": {"assignments": len(pairs), "int_constants": len(table),
                   "non_int_assignments": len(non_int),
                   "unmapped_opcodes": len(unknown)},
        "unmapped_offsets": unknown[:20],
        "non_int_assignments": [
            {**p, "value": pydis26.s(p["value"]) if isinstance(p["value"], bytes)
             else p["value"]} for p in non_int
        ],
        "opcodes": table,
        "value_collisions": {
            str(v): sorted(k for k, vv in table.items() if vv == v)
            for v in sorted({vv for vv in table.values()})
            if sum(1 for vv in table.values() if vv == v) > 1
        },
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"client file      : {filename}")
    print(f"module docstring : raw={doc.hex() if isinstance(doc, bytes) else None}")
    for enc, txt in doc_readings.items():
        print(f"                   {enc:11s}-> {txt!r}")
    print(f"co_names={len(root['names'])} co_consts={len(root['consts'])} "
          f"co_code={len(root['code'])}B")
    print(f"assignments      : {len(pairs)}  (int={len(table)}, non-int={len(non_int)})")
    print(f"unmapped opcodes : {len(unknown)}")
    c2gs = sum(1 for k in table if k.startswith("C2GS_"))
    gs2c = sum(1 for k in table if k.startswith("GS2C_"))
    print(f"direction split  : C2GS={c2gs}  GS2C={gs2c}  other={len(table)-c2gs-gs2c}")
    for probe in ("GS2C_HELLO", "C2GS_ANSWERHELLO", "C2GS_LOGIN_ACCOUNT_ENTER",
                  "GS2C_LOGIN_ACCOUNT_INFO", "GS2C_LOGIN_PLAYER_INFO",
                  "C2GS_HEART_BEAT", "GS2C_HEART_BEAT", "C2GS_SELECT_SERVER",
                  "GS2C_SELSERVER", "GS2C_PROP_INIT", "GS2C_MAP_SCENE_M"):
        print(f"  {probe:28s} = {table.get(probe, 'NOT FOUND')}")
    print(f"wrote            : {csv_path}\n                   {json_path}")

    bad = 0
    for mock in args.cross_check_mock:
        rows = cross_check_mock(Path(mock), table)
        mism = [r for r in rows if r["status"] == "MISMATCH"]
        absent = [r for r in rows if r["status"] == "missing_in_client"]
        print(f"\ncross-check {mock}: {len(rows)} constants, "
              f"{len(rows)-len(mism)-len(absent)} match, "
              f"{len(mism)} MISMATCH (fail), {len(absent)} not in client (warning)")
        for r in absent:
            print(f"  [warning: not in client table] {r['name']} = {r['mock_value']}")
        for r in mism:
            print(f"  [MISMATCH] {r['name']}: mock={r['mock_value']} "
                  f"client={r['client_value']}")
            bad += 1
    if bad:
        print(f"\nFAIL: {bad} constant(s) disagree with the client table.")
    else:
        print("\nOK: no constant disagrees with the client table "
              "(names absent from it are this project's own aliases).")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
