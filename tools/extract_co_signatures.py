#!/usr/bin/env python3
"""Dump per-code-object names/varnames/consts for decoded FLS entries (Task B, mall protocol).

Usage:
  python3 tools/extract_co_signatures.py --archive data/script.fls --indices 1498,1848 --out /tmp/co
Writes <out>/co<idx>.json. Read-only w.r.t. the game archive.
Heuristic used downstream: a C2S* sender's sub-command id is the first non-negative int
constant of its code object; PacketPrepare/C2GS_* name gives the base opcode.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import fls_batch_decoder as d

def _s(x):
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else x

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default="data/script.fls")
    ap.add_argument("--indices", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    arch = open(a.archive, "rb").read()
    for idx in [int(x) for x in a.indices.split(",") if x.strip()]:
        e = d.extract_entry(arch, idx)
        r = d.decode_entry_auto(e["exp"])
        if r["status"] not in ("ok", "suspect"):
            print(f"entry{idx}: {r['status']}"); continue
        out = []
        for co in r["reader"].code_objects:
            out.append({"name": _s(co.get("name")),
                        "argcount": co.get("argcount"),
                        "varnames": [_s(v) for v in (co.get("varnames") or [])],
                        "names": [_s(v) for v in (co.get("names") or [])],
                        "consts": [_s(c) if not isinstance(c, dict) else "<code>" for c in (co.get("consts") or [])]})
        with open(os.path.join(a.out, f"co{idx}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1, default=str)
        print(f"entry{idx}: {len(out)} code objects, status={r['status']}")

if __name__ == "__main__":
    main()
