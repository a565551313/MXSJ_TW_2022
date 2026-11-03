"""Make the client-side probe resident: start a native 1 Hz timer at import.

The client already ships a script-level timer module (``timer.Timer``); game
scripts use it for repeating callbacks (``timer.Timer(0.1, self.CheckStep,
iRepeat=-1)``).  Reusing it means the probe can keep rewriting its report while
the client runs, without sockets, threads or a game-loop patch.

What this module adds to ``mxsj_probe`` (about 60 bytes of module code plus one
small function):

```python
def _tick():
    try:
        write_report()
    except:
        pass

try:
    import timer
    _TIMER = timer.Timer(1, _tick, -1)
except:
    pass
```

Every part is inside ``try/except``: if the timer module is missing or the
call fails, the client behaves exactly as before.  ``_TIMER`` is a module
global on purpose - dropping the last reference would cancel the timer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path

from patch_package import (
    _atom_value,
    _ins,
    _intern_atom,
    _payload,
    _require_script_editor,
    _sha256,
    decrypt,
    encrypt,
    read_directory,
    rebuild,
    verify_hook_layout,
)

PROBE_ID = 2537560296
PROBE_NAME = b"mxsj_probe"
TIMER_SECONDS = 1
OP_MAKE_FUNCTION = 132
TICK_NAME = "_tick"
TIMER_GLOBAL = "_TIMER"


def _int_atom(value: int):
    return struct.unpack("<i", struct.pack("<i", value))[0]


def _guard_block(body: bytes) -> bytes:
    """Wrap ``body`` (stack-neutral) in SETUP_EXCEPT .. END_FINALLY."""
    handler = b"".join([_ins(1)] * 3) + _ins(88)
    jump = _ins(110, len(handler))
    setup = _ins(121, len(body) + len(jump))
    return setup + body + jump + handler


def build_tick_code(marshal_tree, filename: bytes):
    """Build ``def _tick(): try: write_report() except: pass``."""
    body = b"".join(
        [
            _ins(116, 0),  # LOAD_GLOBAL write_report
            _ins(131, 0),  # CALL_FUNCTION 0
            _ins(1),  # POP_TOP
        ]
    )
    code = _guard_block(body) + _ins(100, 0) + _ins(83)
    fields = (
        marshal_tree.Group(
            b"(", (marshal_tree.Atom(b"N", b"N", None),)
        ),  # consts: (None,)
        marshal_tree.Group(
            b"(", (_intern_atom(b"write_report", marshal_tree),)
        ),  # names
        marshal_tree.Group(b"(", ()),  # varnames (no arguments)
        marshal_tree.Group(b"(", ()),  # freevars
        marshal_tree.Group(b"(", ()),  # cellvars
        marshal_tree.Atom(
            b"s", b"s" + struct.pack("<I", len(filename)) + filename, filename
        ),
        marshal_tree.Atom(
            b"s", b"s" + struct.pack("<I", len(TICK_NAME)) + b"_tick", b"_tick"
        ),
    )
    return marshal_tree.Code(
        struct.pack("<iiii", 0, 0, 3, 0x41),  # argcount, nlocals, stacksize, flags
        code,
        fields,
        struct.pack("<i", 1),
        b"",
    )


def build_module(root, marshal_tree):
    """Return the probe module with the timer bootstrap appended."""
    names = [_atom_value(atom) for atom in root.fields[1].items]
    consts = list(root.fields[0].items)
    if TICK_NAME.encode() in names:
        raise FileExistsError("resident timer is already present")

    tick_code = build_tick_code(marshal_tree, _atom_value(root.fields[5]))
    consts.append(tick_code)
    consts.append(
        marshal_tree.Atom(b"i", b"i" + struct.pack("<i", TIMER_SECONDS), None)
    )
    tick_index = len(consts) - 2
    seconds_index = len(consts) - 1

    new_name_atoms = tuple(root.fields[1].items) + tuple(
        _intern_atom(extra, marshal_tree)
        for extra in (TICK_NAME.encode(), b"timer", b"Timer", TIMER_GLOBAL.encode())
    )
    n_tick, n_timer, n_Timer, n_holder = (
        len(names),
        len(names) + 1,
        len(names) + 2,
        len(names) + 3,
    )

    code = root.code
    if code[-4] != 100 or code[-1] != 83:  # LOAD_CONST ..; RETURN_VALUE
        raise ValueError("module code does not end with LOAD_CONST/RETURN_VALUE")
    head, tail = code[:-4], code[-4:]

    start = b"".join(
        [
            _ins(100, tick_index),
            _ins(OP_MAKE_FUNCTION, 0),
            _ins(90, n_tick),
        ]
    )
    start_timer = b"".join(
        [
            _ins(100, 1),  # -1 (import level)
            _ins(100, 2),  # None (fromlist)
            _ins(107, n_timer),
            _ins(90, n_timer),
            _ins(101, n_timer),
            _ins(105, n_Timer),
            _ins(100, seconds_index),
            _ins(101, n_tick),
            _ins(100, 1),  # -1 = repeat
            _ins(131, 3),
            _ins(90, n_holder),
        ]
    )
    appended = start + _guard_block(start_timer)

    header = bytearray(root.header)
    stacksize = struct.unpack_from("<i", header, 8)[0]
    struct.pack_into("<i", header, 8, max(stacksize, 6))
    fields = (
        marshal_tree.Group(b"(", tuple(consts)),
        marshal_tree.Group(b"(", new_name_atoms),
    ) + root.fields[2:]
    return marshal_tree.Code(
        bytes(header),
        head + appended + tail,
        fields,
        root.firstline,
        root.lnotab,
        root.extra,
    )


def _verify(native: bytes, marshal_tree, codec) -> dict:
    """Re-parse the emitted native module and check the timer bootstrap."""
    root = marshal_tree.parse(codec.decode(native)[8:])
    names = [_atom_value(atom) for atom in root.fields[1].items]
    consts = root.fields[0].items
    for required in (TICK_NAME.encode(), b"timer", b"Timer", TIMER_GLOBAL.encode()):
        if required not in names:
            raise ValueError(f"{required!r} missing from module names")
    tick = next(
        c
        for c in consts
        if getattr(c, "tag", b"") == b"c"
        and _atom_value(c.fields[6]) == TICK_NAME.encode()
    )
    tick_names = [_atom_value(atom) for atom in tick.fields[1].items]
    if tick_names != [b"write_report"]:
        raise ValueError("timer callback lost its global reference")
    if tick.code[0] != 121 or tick.code[-1] != 83:
        raise ValueError("timer callback layout is wrong")
    verify_hook_layout(tick.code, 0)
    code = root.code
    setup = code.index(121, max(0, len(code) - 90))
    handler = setup + 3 + int.from_bytes(code[setup + 1 : setup + 3], "little")
    if code[handler] != 1:
        raise ValueError("timer bootstrap handler is misaligned")
    return {
        "module_names": [n.decode("latin1") for n in names],
        "tick_instructions": len(tick.code),
        "module_stacksize": struct.unpack_from("<i", root.header, 8)[0],
    }


def patch(package, *, write: bool = True, repo_root: Path | None = None) -> dict:
    """Install the resident timer bootstrap into the probe entry."""
    path = Path(package)
    data = path.read_bytes()
    root_dir = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    mx_hash, marshal_tree, cipher, codec, _ = _require_script_editor(root_dir)
    entries = read_directory(data)
    target = next((e for e in entries if e["id"] == PROBE_ID), None)
    if target is None:
        raise ValueError("package has no mxsj_probe entry")
    old_stored = _payload(data, target)
    plain, _, _ = decrypt(old_stored, PROBE_NAME, PROBE_ID, cipher, mx_hash)
    std_root = marshal_tree.parse(codec.decode(plain)[8:])
    edited = build_module(std_root, marshal_tree)
    standard = marshal_tree.emit(
        edited, lambda code, lines, extra: (code, lines, extra)
    )
    new_native = codec.encode(codec.MAGIC + bytes(4) + standard)
    new_stored = encrypt(new_native, PROBE_NAME, cipher)
    rebuilt = rebuild(data, entries, target, new_stored)

    check_entries = read_directory(rebuilt)
    for old_entry, new_entry in zip(entries, check_entries, strict=True):
        chunk = _payload(rebuilt, new_entry)
        if new_entry["index"] != target["index"]:
            if chunk != _payload(data, old_entry):
                raise ValueError("untouched entry changed")
        if new_entry["id"] == PROBE_ID:
            verified_stored = chunk
    native_after, _, _ = decrypt(verified_stored, PROBE_NAME, PROBE_ID, cipher, mx_hash)
    details = _verify(native_after, marshal_tree, codec)

    report = {
        "format": "mxsj-client-mcp-resident-probe-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package": str(path),
        "entry_count": len(entries),
        "entry_index": target["index"],
        "entry_id": PROBE_ID,
        "timer_seconds": TIMER_SECONDS,
        "before": {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
            "stored_bytes": len(old_stored),
        },
        "after": {
            "sha256": hashlib.sha256(rebuilt).hexdigest(),
            "size": len(rebuilt),
            "stored_bytes": len(new_stored),
        },
        "details": details,
    }
    if write:
        temporary = path.with_name(path.name + ".new")
        temporary.write_bytes(rebuilt)
        os.replace(temporary, path)
        if _sha256(path) != report["after"]["sha256"]:
            raise ValueError("written package hash mismatch")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="给探针加上常驻定时器")
    parser.add_argument("--package", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    package = args.package or (root / "data" / "script.fls")
    try:
        report = patch(package, write=not args.check, repo_root=root)
    except FileExistsError:
        print("探针已经带上常驻定时器了，不需要再加。")
        return 0
    except (OSError, ValueError) as exc:
        print(f"处理失败：{exc}")
        return 2
    print("=" * 60)
    print(" 常驻探针处理完成")
    print("-" * 60)
    print(f" 包：{report['package']}")
    print(f" 探针条目：{report['entry_id']}（第 {report['entry_index']} 条）")
    print(f" 心跳间隔：{report['timer_seconds']} 秒")
    print(f" 修改前 SHA-256：{report['before']['sha256']}")
    print(f" 修改后 SHA-256：{report['after']['sha256']}")
    print("=" * 60)
    if not args.check:
        out = Path(__file__).resolve().parents[1] / "runtime"
        out.mkdir(parents=True, exist_ok=True)
        (out / "resident_probe_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
