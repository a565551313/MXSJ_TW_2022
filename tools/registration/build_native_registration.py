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

基線：默認釘住 `data/script.fls`（`BASE_SHA256`）。要拿客戶端現行檔
（例如已經打過補丁的舊出貨包）重做時，傳 `--archive <檔>` +
`--base-sha256 <該檔 SHA>`；此時若 337 已是補丁形態，工具會明確提示
「原樣保留」而不是重複寫入。`--report <path>` 在驗證通過後落一份 JSON
構建記錄（基線/源碼/產物三者 SHA + 實際改動的條目號）。
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
import time
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


TW_PATCH_AT = 102
TW_PATCH_LEN = 9


def tw_predicate_window(code: bytes, names, varnames) -> tuple[str, bytes]:
    """判定 mainpage 的 IsTWServer 謂詞窗口現狀（純函數，便於單測）。

    回傳 (狀態, 替換位元組)：
      * `clean`   —— 基線未補，窗口正是 `misc.IsTWServer()` 調用，可以補；
      * `patched` —— 基線已含**同一個** 9 字節補丁（即上一版本工具的產物），
                     重補無意義，調用方應原樣保留；
      其餘一律 raise：認不得的基線絕不靜默重打包。
    """
    expect = (
        encode_ins(STD_LOAD_FAST, varnames.index(b"misc"))
        + encode_ins(STD_LOAD_ATTR, names.index(b"IsTWServer"))
        + encode_ins(STD_CALL_FUNCTION, 0)
    )
    replacement = encode_ins(STD_LOAD_GLOBAL, names.index(b"False"))
    replacement += encode_ins(STD_NOP, None) * (TW_PATCH_LEN - len(replacement))
    if len(expect) != TW_PATCH_LEN:
        raise ValueError(f"TW predicate encoding is not {TW_PATCH_LEN} bytes")
    window = code[TW_PATCH_AT : TW_PATCH_AT + TW_PATCH_LEN]
    if window == expect:
        return "clean", replacement
    if window == replacement:
        return "patched", replacement
    raise ValueError(
        "TW predicate fingerprint mismatch at "
        f"{TW_PATCH_AT}: got {window.hex()} —— 基線不是本工具認得的 mainpage"
        "（既非未補形態也非已補形態），拒絕盲目重打包"
    )


def patch_mainpage(duoyi_marshal: bytes) -> tuple[bytes, int, int, str]:
    """回傳 (負載, 窗口起, 窗口迄, 狀態)。狀態：`patched` | `kept`。"""
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
    state, replacement = tw_predicate_window(code, names, varnames)
    if state == "patched":
        return duoyi_marshal, TW_PATCH_AT, TW_PATCH_AT + TW_PATCH_LEN, "kept"
    new_code = code[:TW_PATCH_AT] + replacement + code[TW_PATCH_AT + TW_PATCH_LEN :]
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
    return patched, start + TW_PATCH_AT, start + TW_PATCH_AT + TW_PATCH_LEN, "patched"


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
    ap.add_argument(
        "--base-sha256",
        default=BASE_SHA256,
        help="允許的基線 SHA-256；默認釘住倉庫 data/script.fls。"
        "換基線（例如用客戶端現行檔）時顯式傳入該檔的 SHA-256",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=None,
        help="驗證通過後寫出 JSON 構建記錄（基線/源碼/產物 SHA、337 處理方式）",
    )
    args = ap.parse_args()
    for source in (args.archive, args.keys, args.source):
        aliases_source = args.output.resolve() == source.resolve()
        if args.output.exists() and source.exists():
            aliases_source = aliases_source or args.output.samefile(source)
        if aliases_source:
            raise SystemExit(f"refusing to overwrite an input file: {source}")

    arch = args.archive.read_bytes()
    base_sha = sha256(arch)
    if base_sha != args.base_sha256:
        raise SystemExit(
            f"base archive sha256 mismatch: {base_sha}\n"
            f"  期望 {args.base_sha256}（默認釘住倉庫 data/script.fls）\n"
            f"  若確認要用這份基線：--base-sha256 {base_sha}"
        )
    print(f"[i] base {args.archive} sha256={base_sha}")
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
    patched_main, win_lo, win_hi, main_state = patch_mainpage(duoyi_main)
    orig_exp_main = zlib.decompress(by_idx[ENTRY_MAINPAGE]["comp"])
    new_exp_main = pack.encrypt_5seg_xor(
        patched_main,
        info_main["keys"],
        info_main["bounds"],
        orig_len=len(orig_exp_main),
    )

    replacements = {ENTRY_REGISTER: zlib.compress(new_exp_reg, 9)}
    if main_state == "patched":
        replacements[ENTRY_MAINPAGE] = zlib.compress(new_exp_main, 9)
    else:
        print(
            f"[note] 基線 entry {ENTRY_MAINPAGE} 已含同一個 {TW_PATCH_LEN} 字節補丁"
            f"（偏移 {win_lo}），本次原樣保留，不重複寫入。"
        )
    expected_changed = [
        i for i in (ENTRY_MAINPAGE, ENTRY_REGISTER) if i in replacements
    ]
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
    assert changed == expected_changed, f"unexpected changed: {changed}"

    dec_main_new = decrypt_entry(out_by_idx[ENTRY_MAINPAGE], keys_db)
    if main_state == "patched":
        diffs = [i for i in range(len(duoyi_main)) if duoyi_main[i] != dec_main_new[i]]
        assert diffs and all(win_lo <= i < win_hi for i in diffs), (
            "mainpage diff out of window"
        )
    else:
        assert dec_main_new == duoyi_main, "mainpage payload altered although kept"
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
        # 2026-10-15 實機回歸教訓：清理調試脚手架時把「開頁失敗的兜底與日誌」
        # 一起刪了，結果客戶端吞異常、點同意沒反應。這三個名字不得消失。
        "_CreateFormEdit",
        "_DiagFailure",
        "_RecoverEntry",
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
    for path in (b"login_new/agreement.dlg", b"login_new/register2027.dlg"):
        assert path in raw_consts, f"layout path missing: {path!r}"
    # 2026-10-22 換版式：勾選框改成版式自帶的三態按鈕，走原生 .dlg 勾選接口
    # （loginin.py 讀「我同意」用的就是 GetObject(...).IsSelected()）。
    for name in (b"IsSelected", b"SetSelect", b"GetObject"):
        assert name in names_all, f"native checkbox API missing: {name!r}"
    for name in (b"CIMGCHECKBOX", b"CImageCheckBox"):
        assert name not in names_all, f"stale checkbox helper still used: {name!r}"
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
    main_note = (
        f"entry {ENTRY_MAINPAGE} diff = {TW_PATCH_LEN} bytes"
        if main_state == "patched"
        else f"entry {ENTRY_MAINPAGE} 保留基線已補形態"
    )
    print(f"[+] verify OK: changed = {changed}; {main_note};")
    print("    full compiled marshal round-trip + packed-module Py2.5 smoke OK;")
    print("    no network call names remain.")

    if args.report:
        report = {
            "kind": "registration_build",
            "built_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "base": {
                "path": str(args.archive.resolve()),
                "bytes": len(arch),
                "sha256": base_sha,
                "entries": len(rows),
                "pinned_by_default": BASE_SHA256,
            },
            "keys": {
                "path": str(args.keys.resolve()),
                "sha256": sha256(args.keys.read_bytes()),
            },
            "source": {
                "path": str(args.source.resolve()),
                "sha256": sha256(args.source.read_bytes()),
            },
            "python25": str(args.python25),
            "compiled_pyc": {"bytes": len(pyc_bytes), "sha256": sha256(pyc_bytes)},
            "mainpage": {
                "entry": ENTRY_MAINPAGE,
                "state": main_state,
                "window": [win_lo, win_hi],
            },
            "changed_entries": changed,
            "output": {
                "path": str(args.output.resolve()),
                "bytes": len(out),
                "sha256": sha256(out),
            },
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[+] report -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
