"""Read original HELLO code objects without importing/executing game modules."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

SAMPLES = {
    "data/script.fls": "8b6e9266bbe91fa77763df7bb2890d55c"
    "968c558b8d4b5e415f27febaf6c0d72",
    "tools/decompiler/script_fls_keys.json": "43bb090d09b95e234292829e7d5ce1495"
    "d53c0ec2ee4e9727d09aac3d97daceb",
}


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    for name, expected in SAMPLES.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"input hash mismatch: {name}")
    spec = importlib.util.spec_from_file_location(
        "build_script_index", root / "tools/script_link/build_script_index.py"
    )
    si = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(si)
    keys = json.loads(
        (root / "tools/decompiler/script_fls_keys.json").read_text(encoding="utf-8")
    )
    found = 0
    for index, _entry_id, packed in si.read_entries(root / "data/script.fls"):
        if index not in (3176, 4082):
            continue
        info = keys[str(index)]
        raw = si.bd._decode_segments(packed, info["keys"], info["bounds"])
        pyc, filename = si.bd._transpile_once(raw, packed, info["keys"], info["bounds"])
        if not pyc:
            raise ValueError(f"cannot parse entry {index}")
        code = si._Reader(pyc[8:]).object()
        for path, child in si.walk_codes(code):
            if not (
                (index == 4082 and path[-1] == "S2CHello")
                or (index == 3176 and path[-2:] == ("CNet", "__init__"))
            ):
                continue
            found += 1
            print(index, filename, path)
            print("names:", repr(child.names))
            for offset, op, arg in si.iter_ops(child):
                if index == 4082 and offset > 205:
                    break
                value = ""
                if op == 100:
                    value = repr(child.consts[arg])
                elif op in (90, 95, 97, 101, 105, 108, 109, 116):
                    value = repr(child.names[arg])
                print(f"{offset} {op} {arg} {value}".rstrip())
    if found != 2:
        raise AssertionError(f"expected 2 original code objects; got {found}")


if __name__ == "__main__":
    main()
