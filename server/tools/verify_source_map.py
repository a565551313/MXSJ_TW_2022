#!/usr/bin/env python3
"""Read-only verification of curated FLS filenames. Does not execute game scripts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

SERVER = Path(__file__).resolve().parents[1]
REPO = SERVER.parent
sys.path.insert(0, str(REPO))
from tools.decompiler.batch_decompile import Py25MarshalTranspiler, XTABS


def main() -> int:
    mapping = json.loads((SERVER / "docs/source_map.json").read_text(encoding="utf-8"))
    archive = (REPO / mapping["archive"]).read_bytes()
    if hashlib.sha256(archive).hexdigest() != mapping["archive_sha256"]:
        print("FAIL: archive hash differs; review provenance rather than trusting old references.")
        return 1
    keys_db = json.loads((REPO / "tools/decompiler/script_fls_keys.json").read_text(encoding="utf-8"))
    index_offset = struct.unpack_from("<I", archive, 8)[0]
    references = {r["entry_index"]: r for m in mapping["modules"] for r in m["references"]}
    failures = []
    for idx, ref in sorted(references.items()):
        try:
            eid, a, b, c = struct.unpack_from("<IIII", archive, index_offset + idx * 16)
            size = ((a * eid + 0xDF25E) & 0xFFFFFFFF) ^ b
            offset = ((b * idx * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
            expanded = zlib.decompress(archive[offset:offset + size])
            info = keys_db[str(idx)]
            keys, bounds = info["keys"], info["bounds"]
            points = [0] + bounds + [len(expanded)]
            decoded = b"".join(expanded[points[i]:points[i + 1]].translate(XTABS[keys[i]]) for i in range(5))
            transpiler = Py25MarshalTranspiler(decoded, expanded, keys, bounds)
            transpiler.transpile_object()
            if transpiler.filename != ref["current_filename"]:
                raise ValueError(f"filename differs: {transpiler.filename!r}")
        except Exception as exc:
            failures.append((idx, str(exc)))
    for idx, reason in failures:
        print(f"FAIL entry {idx}: {reason}")
    print(f"Filename verification: {len(references) - len(failures)}/{len(references)}; not gameplay verification.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
