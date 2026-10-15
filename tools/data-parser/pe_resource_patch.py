#!/usr/bin/env python3
"""把新的资源载荷**原位**写回 PE 的 `.rsrc`（长度必须一致），并可选剥掉失效的签名。

用途：启动器的按钮/页签文字画在 `.rsrc` 那张 PNG 里，改完图要能塞回去。因为只换载荷、
不动目录与节表，所以偏移全都不变 —— 这是最安全的改法；代价是**新载荷必须与原载荷同长度**
（`skin_label_patch.py --pad-to` 就是为此把 PNG 湊成原字節數）。

    python3 tools/data-parser/pe_resource_patch.py mxLauncher.exe mxLauncher_new.exe \\
        --type PNG --name 1 --payload new.png --strip-signature

原檔從不修改；輸出是新檔。寫完會自己再讀一遍核對（哈希比對），不符就報錯不留半成品。
改完 Authenticode 簽名必然失效（預設連目錄一起剝掉，看起來就是「未簽名」）。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
import struct
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_loader = importlib.machinery.SourceFileLoader(
    "pe_resource_dump", str(_HERE / "pe_resource_dump.py")
)
_spec = importlib.util.spec_from_loader("pe_resource_dump", _loader)
prd = importlib.util.module_from_spec(_spec)
_loader.exec_module(prd)

SECURITY_DIR_INDEX = 4
PE32_DIR_BASE = 96
PE32PLUS_DIR_BASE = 112


def find_payload(data: bytes, want_type: str, want_name: str,
                 lang: int | None = None) -> dict:
    """找出目標資源在**檔案裡**的偏移與長度。"""
    pe = prd.PEImage(data)
    for rec in prd.walk_resources(pe):
        label = prd.type_label(rec["type"])
        name = str(rec["name"])
        if label != want_type or name != want_name:
            continue
        if lang is not None and rec["lang"] != lang:
            continue
        off = pe.offset_of(rec["rva"])
        return {
            "type": label, "name": rec["name"], "lang": rec["lang"],
            "rva": rec["rva"], "offset": off, "size": rec["size"],
            "sha256": hashlib.sha256(data[off : off + rec["size"]]).hexdigest(),
        }
    raise LookupError(f"找不到資源 {want_type}/{want_name}"
                      + (f"/{lang}" if lang is not None else ""))


def splice(data: bytes, offset: int, payload: bytes, size: int) -> bytes:
    """原位替換：長度不同就拒絕（動了長度會扯到節表與目錄，這個工具不做）。"""
    if len(payload) != size:
        raise ValueError(f"載荷長度不符：新的 {len(payload)} B，資源要 {size} B")
    if offset + size > len(data):
        raise ValueError("資源偏移超出檔案長度")
    return data[:offset] + payload + data[offset + size :]


def _last_section_end(data: bytes, pe_off: int, opt: int) -> int:
    _, nsec, _, _, _, size_opt, _ = struct.unpack_from("<HHIIIHH", data, pe_off + 4)
    end = 0
    for i in range(nsec):
        so = opt + size_opt + i * 40
        rawsize, rawptr = struct.unpack_from("<II", data, so + 16)
        end = max(end, rawptr + rawsize)
    return end


def strip_signature(data: bytes) -> bytes:
    """簽名目錄清零，並砍掉附在檔尾的證書資料。

    改過載荷之後簽名必然對不上；留一段壞簽名不如直接做成「未簽名」，訊息更乾淨。
    """
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    opt = pe_off + 4 + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    base = {0x10B: PE32_DIR_BASE, 0x20B: PE32PLUS_DIR_BASE}[magic]
    entry = opt + base + 8 * SECURITY_DIR_INDEX
    _rva, size = struct.unpack_from("<II", data, entry)
    if not size:
        return data
    out = bytearray(data)
    struct.pack_into("<II", out, entry, 0, 0)
    cut = _last_section_end(data, pe_off, opt)
    if cut < len(out):
        out = out[:cut]
    return bytes(out)


def patch(src: Path, dst: Path, payload: bytes, want_type: str, want_name: str,
          lang: int | None = None, strip: bool = False) -> dict:
    data = src.read_bytes()
    found = find_payload(data, want_type, want_name, lang)
    if len(payload) != found["size"]:
        raise ValueError(
            f"載荷長度必須是 {found['size']} B（拿到 {len(payload)} B）；"
            "用 skin_label_patch.py --pad-to 把圖湊成同樣長度"
        )
    out = splice(data, found["offset"], payload, found["size"])
    if strip:
        out = strip_signature(out)
    # 自核對：重新讀一次輸出檔，確認資源已經是新載荷
    back = find_payload(out, want_type, want_name, found["lang"])
    if back["sha256"] != hashlib.sha256(payload).hexdigest():
        raise RuntimeError("寫回後校驗不一致，輸出檔未產生")
    dst.write_bytes(out)
    return {
        "kind": "pe_resource_patch",
        "src": str(src),
        "dst": str(dst),
        "src_bytes": len(data),
        "src_sha256": hashlib.sha256(data).hexdigest(),
        "dst_bytes": len(out),
        "dst_sha256": hashlib.sha256(out).hexdigest(),
        "resource": found,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "payload_bytes": len(payload),
        "signature_stripped": bool(strip),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path, help="要改的 exe/dll（唯讀）")
    ap.add_argument("dst", type=Path, help="輸出檔（已存在會拒絕覆寫）")
    ap.add_argument("--type", dest="rtype", required=True,
                    help="資源型別名，如 PNG / BITMAP / RCDATA")
    ap.add_argument("--name", required=True, help="資源名（數字 id 或名字串）")
    ap.add_argument("--lang", type=int, default=None, help="語言 id（預設不限）")
    ap.add_argument("--payload", type=Path, required=True, help="新的資源內容檔案")
    ap.add_argument("--strip-signature", action="store_true",
                    help="順帶剝掉已失效的 Authenticode")
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()
    if args.dst.exists():
        print(f"[!] {args.dst} 已存在，拒絕覆寫（先改名或刪掉）", file=sys.stderr)
        return 2
    report = patch(
        args.src, args.dst, args.payload.read_bytes(), args.rtype, args.name, args.lang,
        args.strip_signature,
    )
    text = json.dumps(report, ensure_ascii=False, indent=1) + "\n"
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
