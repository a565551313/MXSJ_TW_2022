"""Add the guarded probe hook to a 0SLF ``script.fls`` in place.

The hook is a bytecode-level edit of ``mainpage``'s module code: the trailing
``LOAD_CONST None; RETURN_VALUE`` pair is replaced by

```python
try:
    import mxsj_probe
    mxsj_probe.write_report()
except:
    pass
```

so a missing or failing probe can never stop the client from starting.  The
whole package is rebuilt with the native directory formulas, every untouched
entry keeps its stored bytes, and the result is verified before it replaces
the input file.  Nothing here compiles Python source: the VM25 modules are
edited as marshalled code objects, exactly like the shipped ones.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

MASK = 0xFFFFFFFF
MAGIC = b"0SLF"
MAINPAGE_ID = 276057508
MAINPAGE_NAME = b"mainpage"
PROBE_NAME = b"mxsj_probe"
WRITE_NAME = b"write_report"

# CPython 2.5 standard opcodes used by the hook.
OP_POP_TOP = 1
OP_RETURN_VALUE = 83
OP_POP_BLOCK = 87
OP_END_FINALLY = 88
OP_STORE_NAME = 90
OP_LOAD_CONST = 100
OP_LOAD_NAME = 101
OP_LOAD_ATTR = 105
OP_IMPORT_NAME = 107
OP_JUMP_FORWARD = 110
OP_SETUP_EXCEPT = 121
OP_CALL_FUNCTION = 131


def _require_script_editor(repo_root: Path):
    """Import the strict VM25 helpers from the in-repo script editor."""
    for extra in (repo_root / "script_editor" / "src", repo_root):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    from mx_common.mxhash import mx_hash  # noqa: PLC0415
    from script_editor.core.vm import marshal_tree  # noqa: PLC0415
    from script_editor.core.vm.py25 import cipher, codec  # noqa: PLC0415
    from script_editor.core.vm.tables import PY25_MAP  # noqa: PLC0415

    return mx_hash, marshal_tree, cipher, codec, PY25_MAP


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def read_directory(data: bytes) -> list[dict]:
    """Decode every 0SLF directory record with the native formulas."""
    if data[:4] != MAGIC:
        raise ValueError("input is not a 0SLF package")
    count, directory = struct.unpack_from("<II", data, 4)
    if not 0 < count <= 1_000_000:
        raise ValueError("0SLF entry count is outside bounds")
    if directory < 12 or directory + count * 16 > len(data):
        raise ValueError("0SLF directory is outside the file")
    entries = []
    previous = None
    for index in range(count):
        entry_id, r1, r2, r3 = struct.unpack_from("<IIII", data, directory + index * 16)
        if previous is not None and entry_id <= previous:
            raise ValueError("0SLF directory is not sorted by entry ID")
        previous = entry_id
        length = (((r1 * entry_id + 0x0DF25E) & MASK) ^ r2) & MASK
        offset = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ r3) & MASK
        if offset < 12 or offset > len(data) or length > len(data) - offset:
            raise ValueError(f"0SLF entry {index} payload is outside the file")
        entries.append(
            {
                "index": index,
                "id": entry_id,
                "r1": r1,
                "r2": r2,
                "r3": r3,
                "length": length,
                "offset": offset,
            }
        )
    return entries


def _payload(data: bytes, entry: dict) -> bytes:
    return data[entry["offset"] : entry["offset"] + entry["length"]]


def decrypt(
    stored: bytes, name: bytes, entry_id: int, cipher, mx_hash
) -> tuple[bytes, tuple, tuple]:
    """Inflate, decrypt and prove the entry belongs to ``name``."""
    plain = zlib.decompress(stored)
    seed = cipher.module_seed(name)
    keys = cipher.sequence(seed)
    bounds = cipher.bounds_from_seed(seed, len(plain))
    decoded = cipher.xor_segments(plain, keys, bounds)
    if cipher._import_name(decoded) != name or mx_hash(name + b".s") != entry_id:
        raise ValueError(f"entry {entry_id} is not the {name!r} module")
    return decoded, keys, bounds


def encrypt(plain: bytes, name: bytes, cipher) -> bytes:
    """Encrypt with native parameters derived from the module name and size."""
    seed = cipher.module_seed(name)
    keys = cipher.sequence(seed)
    bounds = cipher.bounds_from_seed(seed, len(plain))
    return zlib.compress(cipher.xor_segments(plain, keys, bounds), 9)


def _intern_atom(value: bytes, marshal_tree):
    return marshal_tree.Atom(b"t", b"t" + struct.pack("<I", len(value)) + value, value)


def _ins(op: int, arg: int = 0) -> bytes:
    """Encode one CPython 2.5 instruction in standard opcode space."""
    if op >= 90:
        return bytes([op]) + struct.pack("<H", arg)
    if arg:
        raise ValueError("opcode without argument cannot carry one")
    return bytes([op])


def hook_bytes(names_start: int) -> bytes:
    """Assemble the guarded hook; ``names_start`` is the first new name index.

    Layout (offsets relative to the hook start)::

        0   SETUP_EXCEPT -> 29 (handler)
        3   LOAD_CONST -1 ; LOAD_CONST None ; IMPORT_NAME
        12  STORE_NAME ; LOAD_NAME ; LOAD_ATTR ; CALL_FUNCTION 0
        24  POP_TOP ; POP_BLOCK ; JUMP_FORWARD -> 33 (end)
        29  POP_TOP x3 ; END_FINALLY
        33  LOAD_CONST None ; RETURN_VALUE
    """
    probe_name = names_start
    write_name = names_start + 1
    try_body = b"".join(
        [
            _ins(OP_LOAD_CONST, 0),  # -1 (import level, as the compiler emits)
            _ins(OP_LOAD_CONST, 1),  # None (fromlist)
            _ins(OP_IMPORT_NAME, probe_name),
            _ins(OP_STORE_NAME, probe_name),
            _ins(OP_LOAD_NAME, probe_name),
            _ins(OP_LOAD_ATTR, write_name),
            _ins(OP_CALL_FUNCTION, 0),
            _ins(OP_POP_TOP),
            _ins(OP_POP_BLOCK),
        ]
    )
    handler = b"".join([_ins(OP_POP_TOP)] * 3) + _ins(OP_END_FINALLY)
    end = _ins(OP_LOAD_CONST, 1) + _ins(OP_RETURN_VALUE)
    # SETUP_EXCEPT jumps to the handler, which sits right after the jump over it.
    jump_over = _ins(OP_JUMP_FORWARD, len(handler))
    setup = _ins(OP_SETUP_EXCEPT, len(try_body) + len(jump_over))
    return setup + try_body + jump_over + handler + end


def _truncate_tail(code: bytes, consts) -> bytes:
    """Drop the module's final ``LOAD_CONST None; RETURN_VALUE`` pair."""
    if len(code) < 4 or code[-4] != OP_LOAD_CONST or code[-1] != OP_RETURN_VALUE:
        raise ValueError("module code does not end with LOAD_CONST/RETURN_VALUE")
    const_index = code[-3] | (code[-2] << 8)
    if consts[const_index].tag != b"N":
        raise ValueError("module code does not return None")
    return code[:-4]


def _has_hook(names: list[bytes]) -> bool:
    return PROBE_NAME in names and WRITE_NAME in names


def _atom_value(atom) -> bytes:
    if atom.tag in (b"s", b"t", b"u", b"R"):
        return atom.value or b""
    return b""


def verify_hook_layout(code: bytes, start: int) -> None:
    """Prove the appended instructions form a well-formed guarded block."""
    if code[start] != OP_SETUP_EXCEPT:
        raise ValueError("hook does not start with SETUP_EXCEPT")
    handler = start + 3 + int.from_bytes(code[start + 1 : start + 3], "little")
    if code[handler] != OP_POP_TOP:
        raise ValueError("SETUP_EXCEPT does not reach the handler")
    jump = code.index(OP_JUMP_FORWARD, start, handler)
    end = jump + 3 + int.from_bytes(code[jump + 1 : jump + 3], "little")
    if end != handler + 4:
        raise ValueError("handler size does not match the jump target")
    if code[end] != OP_LOAD_CONST or code[end + 3] != OP_RETURN_VALUE:
        raise ValueError("hook does not return None on the success path")


def build_hook_source(root, marshal_tree, codec):
    """Return native marshal bytes for ``root`` with the hook appended."""
    consts = root.fields[0].items
    names = [_atom_value(atom) for atom in root.fields[1].items]
    if _has_hook(names):
        raise ValueError("hook is already present")
    # ``root`` already comes from ``codec.decode``: its code is standard VM25.
    code = _truncate_tail(root.code, consts)
    code += hook_bytes(names_start=len(names))
    header = bytearray(root.header)
    stacksize = struct.unpack_from("<i", header, 8)[0]
    struct.pack_into("<i", header, 8, max(stacksize, 3))
    new_names = root.fields[1].items + (
        _intern_atom(PROBE_NAME, marshal_tree),
        _intern_atom(WRITE_NAME, marshal_tree),
    )
    fields = (root.fields[0], marshal_tree.Group(b"(", new_names)) + root.fields[2:]
    edited = marshal_tree.Code(
        bytes(header), code, fields, root.firstline, root.lnotab, root.extra
    )
    standard = marshal_tree.emit(
        edited, lambda code, lines, extra: (code, lines, extra)
    )
    return codec.encode(codec.MAGIC + bytes(4) + standard)


def rebuild(data: bytes, entries: list[dict], target: dict, stored: bytes) -> bytes:
    """Reassemble the archive with one replaced payload and a fresh directory."""
    payload = bytearray()
    directory = bytearray()
    for entry in entries:
        chunk = stored if entry["index"] == target["index"] else _payload(data, entry)
        offset = len(payload) + 12
        length = len(chunk)
        payload.extend(chunk)
        r2 = (((entry["r1"] * entry["id"] + 0x0DF25E) & MASK) ^ length) & MASK
        r3 = (((r2 * entry["index"] * 0x00F718FE + 0x0D59D16C) & MASK) ^ offset) & MASK
        directory.extend(struct.pack("<IIII", entry["id"], entry["r1"], r2, r3))
    header = MAGIC + struct.pack("<II", len(entries), len(payload) + 12)
    return header + bytes(payload) + bytes(directory)


def patch(
    src: Path | str, *, write: bool = True, repo_root: Path | None = None
) -> dict:
    """Add the guarded hook to ``src`` and return a verification report."""
    path = Path(src)
    data = path.read_bytes()
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    mx_hash, marshal_tree, cipher, codec, _ = _require_script_editor(root)
    entries = read_directory(data)
    target = next((e for e in entries if e["id"] == MAINPAGE_ID), None)
    if target is None:
        raise ValueError("package has no mainpage entry")
    old_stored = _payload(data, target)
    plain, _, _ = decrypt(old_stored, MAINPAGE_NAME, MAINPAGE_ID, cipher, mx_hash)
    std_root = marshal_tree.parse(codec.decode(plain)[8:])
    names = [_atom_value(atom) for atom in std_root.fields[1].items]
    if _has_hook(names):
        raise FileExistsError("probe hook is already present")
    new_native = build_hook_source(std_root, marshal_tree, codec)
    new_stored = encrypt(new_native, MAINPAGE_NAME, cipher)
    rebuilt = rebuild(data, entries, target, new_stored)

    # ---- verification before anything is written ----
    check_entries = read_directory(rebuilt)
    if len(check_entries) != len(entries):
        raise ValueError("entry count changed")
    stored = {}
    for old_entry, new_entry in zip(entries, check_entries, strict=True):
        if new_entry["id"] != old_entry["id"]:
            raise ValueError("entry order changed")
        chunk = _payload(rebuilt, new_entry)
        stored[new_entry["index"]] = chunk
        if new_entry["index"] != target["index"]:
            if new_entry["length"] != old_entry["length"]:
                raise ValueError("untouched entry length changed")
            if chunk != _payload(data, old_entry):
                raise ValueError("untouched entry payload changed")
    check_plain, _, _ = decrypt(
        stored[target["index"]], MAINPAGE_NAME, MAINPAGE_ID, cipher, mx_hash
    )
    check_root = marshal_tree.parse(codec.decode(check_plain)[8:])
    check_names = [_atom_value(atom) for atom in check_root.fields[1].items]
    if not _has_hook(check_names):
        raise ValueError("hook missing after rebuild")
    # Both roots come from ``codec.decode``: their code is already standard.
    verify_hook_layout(check_root.code, len(std_root.code) - 4)
    for chunk in stored.values():
        zlib.decompress(chunk)

    report = {
        "format": "mxsj-client-mcp-probe-hook-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package": str(path),
        "entry_count": len(entries),
        "entry_id": MAINPAGE_ID,
        "entry_index": target["index"],
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
        "probe_entry_present": any(
            e["id"] == mx_hash(PROBE_NAME + b".s") for e in entries
        ),
    }
    if write:
        temporary = path.with_name(path.name + ".new")
        temporary.write_bytes(rebuilt)
        os.replace(temporary, path)
        if _sha256(path) != report["after"]["sha256"]:
            raise ValueError("written package hash mismatch")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="给 script.fls 加上受保护的探针钩子")
    parser.add_argument("--package", type=Path, default=None)
    parser.add_argument("--check", action="store_true", help="只检查，不写回")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    package = args.package or (root / "data" / "script.fls")
    try:
        report = patch(package, write=not args.check, repo_root=root)
    except FileExistsError:
        print("这个包已经有探针钩子了，不需要再加。")
        return 0
    except (OSError, ValueError) as exc:
        print(f"处理失败：{exc}")
        return 2
    action = "只检查，没有写回" if args.check else "已写回"
    print("=" * 60)
    print(" 探针钩子处理完成")
    print("-" * 60)
    print(f" 包：{report['package']}")
    print(f" 条目数：{report['entry_count']}（mainpage 第 {report['entry_index']} 条）")
    print(f" 修改前 SHA-256：{report['before']['sha256']}")
    print(f" 修改后 SHA-256：{report['after']['sha256']}")
    print(f" 结果：{action}")
    print("=" * 60)
    if not args.check:
        report_dir = Path(__file__).resolve().parents[1] / "runtime"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "probe_hook_report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f" 记录：{report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
