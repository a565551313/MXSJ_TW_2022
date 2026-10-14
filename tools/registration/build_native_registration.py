#!/usr/bin/env python3
"""註冊界面原生重做（第二期，含五帳號勾選）打包器。

產出一個新的 script.fls（原包不動），只改兩條：
  * 條目 337（login/mainpage）：9 字節定寬補丁——把「申請會員」分支的
    IsTWServer 謂詞換成 False，讓既有的 register 流程入口在台服生效
    （與舊 v1 已實機驗證的補丁逐字節相同）。
  * 條目 4007（login/register）：整模塊換成本目錄 register.py 的重寫版
    （CPython 2.5.6 編譯 -> pack_and_encrypt 混淆/加密/重打包）。

其餘 5000 條的壓縮負載逐字節原樣保留。構建後自動驗證：
337 只差那 9 字節且可轉譯、4007 轉譯回的代碼對象/常量符合源碼、
無網絡調用名殘留、其餘條目負載全等。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_SHA256 = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
ENTRY_MAINPAGE = 337
ENTRY_REGISTER = 4007


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


batch = load_module("mx_batch", ROOT / "tools/decompiler/batch_decompile.py")
pack = load_module("mx_pack", ROOT / "tools/decompiler/pack_and_encrypt.py")
decoder = load_module("mx_decoder", ROOT / "tools/fls_batch_decoder.py")

INV = pack.INV_PY25_MAP
STD_NOP = 9
STD_LOAD_GLOBAL = 116
STD_LOAD_FAST = 124
STD_LOAD_ATTR = 105
STD_CALL_FUNCTION = 131


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_entries(arch: bytes):
    count = struct.unpack_from("<I", arch, 4)[0]
    idx_offset = struct.unpack_from("<I", arch, 8)[0]
    rows = []
    for idx in range(count):
        raw = struct.unpack_from("<IIII", arch, idx_offset + idx * 16)
        dec = pack.decode_0slf_entry(idx, raw)
        comp = arch[dec["data_offset"] : dec["data_offset"] + dec["comp_len"]]
        rows.append({"idx": idx, "raw": raw, "dec": dec, "comp": comp})
    return rows


def decrypt_entry(row, keys_db) -> bytes:
    exp = zlib.decompress(row["comp"])
    info = keys_db[str(row["idx"])]
    keys, bounds = info["keys"], info["bounds"]
    pts = [0] + list(bounds) + [len(exp)]
    return b"".join(
        bytes(exp[pts[i] : pts[i + 1]]).translate(batch.XTABS[keys[i]])
        for i in range(5)
    )


def encode_ins(std_op: int, arg: int | None) -> bytes:
    duoyi = INV[std_op]
    if duoyi >= 0x5F:
        return bytes([duoyi]) + struct.pack("<H", arg)
    return bytes([duoyi])


def code_objects(tree_root):
    """Yield (path, code-object-dict) from MarshalReader output."""

    def walk(node, prefix=""):
        if not (isinstance(node, dict) and "code" in node):
            return
        name = node["name"].decode("ascii", "replace")
        path = f"{prefix}/{name}".strip("/") if name != "<module>" else ""
        yield path, node
        for value in node["consts"]:
            yield from walk(value, path)

    yield from walk(tree_root)


def normalized(code: bytes):
    result = []
    at = 0
    while at < len(code):
        raw = code[at]
        if raw not in batch.PY25_MAP:
            raise ValueError(f"unknown duoyi opcode 0x{raw:02x} at {at}")
        size = 3 if raw >= 0x5F else 1
        arg = int.from_bytes(code[at + 1 : at + 3], "little") if size == 3 else None
        result.append((at, batch.PY25_MAP[raw], arg))
        at += size
    return result


def patch_mainpage(duoyi_marshal: bytes) -> bytes:
    reader = decoder.MarshalReader(duoyi_marshal)
    tree_root = reader.read()
    if reader.pos != len(duoyi_marshal):
        raise ValueError("mainpage marshal not fully consumed")
    targets = {p: c for p, c in code_objects(tree_root)}
    co = targets.get("CMainPage/OnMessage")
    if co is None:
        raise ValueError("CMainPage/OnMessage not found")
    code = bytes(co["code"])
    names = co["names"]
    varnames = co["varnames"]
    expect = (
        encode_ins(STD_LOAD_FAST, varnames.index(b"misc"))
        + encode_ins(STD_LOAD_ATTR, names.index(b"IsTWServer"))
        + encode_ins(STD_CALL_FUNCTION, 0)
    )
    if len(expect) != 9 or code[102:111] != expect:
        raise ValueError("TW predicate fingerprint mismatch at 102")
    replacement = encode_ins(STD_LOAD_GLOBAL, names.index(b"False"))
    replacement += encode_ins(STD_NOP, None) * (9 - len(replacement))
    new_code = code[:102] + replacement + code[111:]
    seq = normalized(new_code)
    starts = {at for at, _, _ in seq} | {len(new_code)}
    limits = (
        len(co["consts"]),
        len(co["names"]),
        len(co["varnames"]),
        len(co["freevars"]) + len(co["cellvars"]),
        len(new_code),
    )
    if not batch.check_py25_co_code(new_code, limits)[0]:
        raise ValueError("patched co_code failed validation")
    for at, op, arg in seq:
        if op in (113, 119) and arg not in starts:
            raise ValueError("unaligned absolute jump after patch")
        if op in (93, 110, 111, 112, 120, 121, 122) and at + 3 + arg not in starts:
            raise ValueError("unaligned relative jump after patch")
    start = duoyi_marshal.index(code)
    if duoyi_marshal.count(code) != 1:
        raise ValueError("co_code bytes not unique in marshal")
    patched = duoyi_marshal[:start] + new_code + duoyi_marshal[start + len(code) :]
    return patched, start + 102, start + 111


def build_archive(arch: bytes, rows, replacements: dict[int, bytes]) -> bytes:
    first_offset = min(r["dec"]["data_offset"] for r in rows)
    out = bytearray(arch[:first_offset])
    new_dir = bytearray()
    for row in rows:
        comp = replacements.get(row["idx"], row["comp"])
        doff = len(out)
        out.extend(comp)
        nt = pack.encode_0slf_dir_entry(
            row["idx"], row["raw"][0], row["raw"][1], len(comp), doff, row["dec"]["f1"]
        )
        new_dir.extend(struct.pack("<IIII", *nt))
    new_idx_offset = len(out)
    out.extend(new_dir)
    struct.pack_into("<I", out, 8, new_idx_offset)
    return bytes(out)


def transpile(dec: bytes, exp: bytes, info) -> bytes:
    tr = batch.Py25MarshalTranspiler(dec, exp, info["keys"], info["bounds"])
    tr.transpile_object()
    return bytes(tr.out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, default=ROOT / "data/script.fls")
    ap.add_argument(
        "--keys", type=Path, default=ROOT / "tools/decompiler/script_fls_keys.json"
    )
    ap.add_argument(
        "--python25",
        type=Path,
        required=True,
        help="CPython 2.5.6 interpreter (see build_python25.sh)",
    )
    ap.add_argument(
        "--source", type=Path, default=Path(__file__).with_name("register.py")
    )
    ap.add_argument(
        "--output", type=Path, default=Path(__file__).with_name("out") / "script.fls"
    )
    args = ap.parse_args()
    for source in (args.archive, args.keys, args.source):
        aliases_source = args.output.resolve() == source.resolve()
        if args.output.exists() and source.exists():
            aliases_source = aliases_source or args.output.samefile(source)
        if aliases_source:
            raise SystemExit(f"refusing to overwrite an input file: {source}")

    arch = args.archive.read_bytes()
    if sha256(arch) != BASE_SHA256:
        raise SystemExit(f"base archive sha256 mismatch: {sha256(arch)}")
    keys_db = json.loads(args.keys.read_text(encoding="utf-8"))
    rows = read_entries(arch)
    by_idx = {r["idx"]: r for r in rows}

    # 1) 用 CPython 2.5.6 編譯重寫版 register
    pyc_path = args.output.parent / "register_compiled.pyc"
    pyc_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(args.python25),
            str(Path(__file__).with_name("compile_with_py25.py")),
            str(args.source),
            str(pyc_path),
        ],
        check=True,
    )
    pyc_bytes = pyc_path.read_bytes()

    # 2) 兩條替換負載
    info_reg = keys_db[str(ENTRY_REGISTER)]
    orig_exp_reg = zlib.decompress(by_idx[ENTRY_REGISTER]["comp"])
    new_exp_reg = pack.encrypt_5seg_xor(
        pack.obfuscate_py25_pyc_bytes(pyc_bytes),
        info_reg["keys"],
        info_reg["bounds"],
        orig_len=len(orig_exp_reg),
    )

    info_main = keys_db[str(ENTRY_MAINPAGE)]
    duoyi_main = decrypt_entry(by_idx[ENTRY_MAINPAGE], keys_db)
    patched_main, win_lo, win_hi = patch_mainpage(duoyi_main)
    orig_exp_main = zlib.decompress(by_idx[ENTRY_MAINPAGE]["comp"])
    new_exp_main = pack.encrypt_5seg_xor(
        patched_main,
        info_main["keys"],
        info_main["bounds"],
        orig_len=len(orig_exp_main),
    )

    replacements = {
        ENTRY_REGISTER: zlib.compress(new_exp_reg, 9),
        ENTRY_MAINPAGE: zlib.compress(new_exp_main, 9),
    }
    out = build_archive(arch, rows, replacements)
    args.output.write_bytes(out)
    print(f"[+] wrote {args.output} ({len(out)} bytes) sha256={sha256(out)}")

    # 3) 驗證
    out_rows = read_entries(out)
    assert len(out_rows) == len(rows), "entry count changed"
    assert [r["raw"][0] for r in out_rows] == [r["raw"][0] for r in rows], (
        "entry identities/order changed"
    )
    out_by_idx = {r["idx"]: r for r in out_rows}
    for index, row in by_idx.items():
        if index not in (ENTRY_MAINPAGE, ENTRY_REGISTER):
            assert row["comp"] == out_by_idx[index]["comp"], (
                f"untouched compressed payload changed: {index}"
            )
    changed = [
        i
        for i in by_idx
        if zlib.decompress(by_idx[i]["comp"]) != zlib.decompress(out_by_idx[i]["comp"])
    ]
    assert changed == [ENTRY_MAINPAGE, ENTRY_REGISTER], f"unexpected changed: {changed}"

    dec_main_new = decrypt_entry(out_by_idx[ENTRY_MAINPAGE], keys_db)
    diffs = [i for i in range(len(duoyi_main)) if duoyi_main[i] != dec_main_new[i]]
    assert diffs and all(win_lo <= i < win_hi for i in diffs), (
        "mainpage diff out of window"
    )
    assert dec_main_new == patched_main, "mainpage round-trip mismatch"
    std_main = transpile(
        dec_main_new, zlib.decompress(out_by_idx[ENTRY_MAINPAGE]["comp"]), info_main
    )
    assert b"mainpage" in std_main

    dec_reg_new = decrypt_entry(out_by_idx[ENTRY_REGISTER], keys_db)
    # Known authored bytes must not go through heuristic seam repair: that
    # solver may "repair" a valid LOAD_FAST into STORE_NAME near an old bound.
    from authored_marshal import restore_authored_pyc

    std_reg = restore_authored_pyc(
        dec_reg_new, pack.obfuscate_py25_pyc_bytes(pyc_bytes),
        batch.transpile_py25_code,
    )
    assert std_reg[8:] == pyc_bytes[8:], "compiled marshal round-trip mismatch"
    roundtrip_path = args.output.parent / "register_roundtrip.pyc"
    roundtrip_path.write_bytes(std_reg)
    sys.path.insert(0, str(ROOT / "tools/script_link"))
    from build_script_index import parse_pyc, walk_codes

    root_code = parse_pyc(std_reg)
    names_all = set()
    funcs = set()
    texts = []
    for path, code in walk_codes(root_code):
        funcs.add("/".join(path))
        for n in code.names:
            if isinstance(n, (bytes, bytearray)):
                names_all.add(bytes(n))
        for c in code.consts:
            if isinstance(c, str):
                texts.append(c)
            elif isinstance(c, (bytes, bytearray)):
                try:
                    texts.append(bytes(c).decode("utf-8"))
                except UnicodeDecodeError:
                    pass
    for banned in (b"CHttpObject", b"gameurl", b"REGISTER_URL", b"OpenUrl"):
        assert banned not in names_all, f"banned name present: {banned}"
    for need in (
        "CRegTermsPanel",
        "CRegFormPanel",
        "CConfirm",
        "Show",
        "Step",
        "BuildRegistrationAccounts",
        "SetRegisterFive",
        "OnRegistrationComplete",
    ):
        assert any(need in f for f in funcs), f"missing function: {need}"
    raw_consts = set()
    for _path, code in walk_codes(root_code):
        for c in code.consts:
            if isinstance(c, (bytes, bytearray)):
                raw_consts.add(bytes(c))
    stub = "伺服器尚未開放註冊，請稍後再試".encode("big5")
    assert stub in raw_consts, "stub Big5 bytes missing"
    assert not any(
        isinstance(c, str) and "伺服器" in c
        for path, code in walk_codes(root_code)
        for c in code.consts
    ), "stub leaked as unicode"
    for path in (b"login/regterms.dlg", b"login/regform.dlg"):
        assert path in raw_consts, f"layout path missing: {path!r}"
    for name in (b"CIMGCHECKBOX", b"CImageCheckBox", b"SetCheck", b"IsSelected"):
        assert name in names_all, f"native checkbox API missing: {name!r}"
    with tempfile.TemporaryDirectory(prefix="mx-registration-smoke-") as cwd:
        subprocess.run(
            [
                str(args.python25.resolve()),
                str(Path(__file__).with_name("harness.py2")),
                str(roundtrip_path.resolve()),
            ],
            cwd=cwd,
            check=True,
        )
    print("[+] verify OK: only 337/4007 changed; mainpage diff = 9 bytes;")
    print("    full compiled marshal round-trip + packed-module Py2.5 smoke OK;")
    print("    no network call names remain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
