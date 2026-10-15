#!/usr/bin/env python3
"""從 PE 的 `.rsrc` 裡把資源取出來：位圖 / PNG / 光標 / 圖標 / 對話框版式 / 字串表。

為什麼要有這個工具：啟動器與客戶端都是原生二進位，**反不出源碼**（邊界與實測
數據見 `notes/client_binary_reversibility.md`），但它們外掛的皮膚圖、對話框版式、
提示文案是按標準 Windows 資源格式备好的，靜態就能整份取出。要對「啟動/更新線」
或「啟動器皮膚」下判斷時用它取證，不要靠 `strings` 猜。

    python3 tools/data-parser/pe_resource_dump.py mxLauncher.exe --summary
    python3 tools/data-parser/pe_resource_dump.py mxLauncher.exe --dump out/launch_rsrc

輸入檔全程唯讀；產物只寫進 `--dump` 指定的目錄（不給就不寫盤）。解碼不了的條目
一律留原字節並在 manifest 裡記明原因，不靜默丟棄。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

# 標準資源型別號；不在表裡的（如自訂型別名）原樣保留名字
CURSOR, BITMAP, ICON, MENU, DIALOG, STRING = 1, 2, 3, 4, 5, 6
ACCEL, RCDATA, GROUP_CURSOR, GROUP_ICON, VERSION, MANIFEST = 9, 10, 12, 14, 16, 24
TYPE_NAMES = {
    CURSOR: "CURSOR",
    BITMAP: "BITMAP",
    ICON: "ICON",
    MENU: "MENU",
    DIALOG: "DIALOG",
    STRING: "STRING",
    ACCEL: "ACCEL",
    RCDATA: "RCDATA",
    GROUP_CURSOR: "GROUP_CURSOR",
    GROUP_ICON: "GROUP_ICON",
    VERSION: "VERSION",
    MANIFEST: "MANIFEST",
}
# 群組型別 → 它引用的子資源型別
GROUP_CHILD = {GROUP_ICON: ICON, GROUP_CURSOR: CURSOR}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
STR_REF = re.compile(r"string-table #(\d+)")
# 預定義控制項類別序號（#128=Button…），解版式時翻回人話
CLASS_ORDINALS = {
    80: "Button",
    81: "Edit",
    82: "Static",
    83: "ListBox",
    84: "ComboBox",
    85: "Scroll Bar",
    128: "Button",
    130: "Static",
    131: "Edit",
    132: "ListBox",
    133: "ComboBox",
    134: "ScrollBar",
    137: "ComboLBox",
    32770: "#32770",
}
DS_SETFONT = 0x40


class PEError(ValueError):
    pass


def u16(buf: bytes, at: int) -> int:
    return struct.unpack_from("<H", buf, at)[0]


def align4(at: int) -> int:
    return (at + 3) & ~3


class PEImage:
    """只解析到「找到 .rsrc 並能把 RVA 換成檔案偏移」，夠資源用。"""

    def __init__(self, data: bytes):
        self.data = data
        if data[:2] != b"MZ":
            raise PEError("不是 MZ 開頭的 PE 檔案")
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe_off : pe_off + 4] != b"PE\0\0":
            raise PEError("找不到 PE 簽章")
        coff = pe_off + 4
        _, nsec, _, _, _, size_opt, _ = struct.unpack_from("<HHIIIHH", data, coff)
        opt = coff + 20
        magic = u16(data, opt)
        base = {0x10B: opt + 96, 0x20B: opt + 112}.get(magic)
        if base is None:
            raise PEError(f"不認識的可选頭 magic={magic:#x}")
        self.res_rva, self.res_size = struct.unpack_from("<II", data, base + 8 * 2)
        if not self.res_rva:
            raise PEError("這個 PE 沒有資源目錄")
        self.sections = []
        for i in range(nsec):
            so = opt + size_opt + i * 40
            name = data[so : so + 8].rstrip(b"\0").decode("latin-1", "replace")
            vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, so + 8)
            self.sections.append((name, vaddr, vsize, rawsize, rawptr))

    def offset_of(self, rva: int) -> int:
        for _name, vaddr, vsize, rawsize, rawptr in self.sections:
            if vaddr <= rva < vaddr + max(vsize, rawsize):
                return rawptr + (rva - vaddr)
        raise PEError(f"RVA {rva:#x} 不在任何節內")

    def read(self, rva: int, size: int) -> bytes:
        at = self.offset_of(rva)
        return self.data[at : at + size]


def _read_name(pe: PEImage, field: int) -> str | int:
    """名字欄位：高位為 1 時是「相對於 .rsrc 起點」的 Unicode 名字串。"""
    if not field & 0x80000000:
        return field & 0xFFFF
    # 名字串格式：WORD 字元數 + 緊接的 UTF-16（無終止符）
    at = pe.offset_of(pe.res_rva + (field & 0x7FFFFFFF))
    length = u16(pe.data, at)
    return pe.data[at + 2 : at + 2 + length * 2].decode("utf-16-le", "replace")


def walk_resources(pe: PEImage) -> list[dict]:
    """展開資源目錄（型別 → 名稱/ID → 語言）→ [{type, name, lang, rva, size, cp}]。"""
    leaves: list[dict] = []

    def visit(dir_rva: int, path: tuple) -> None:
        hdr = pe.offset_of(dir_rva)
        named, ids = struct.unpack_from("<HH", pe.data, hdr + 12)
        for i in range(named + ids):
            field_name, field_data = struct.unpack_from(
                "<II", pe.data, hdr + 16 + i * 8
            )
            key = _read_name(pe, field_name)
            if field_data & 0x80000000:
                visit(pe.res_rva + (field_data & 0x7FFFFFFF), path + (key,))
                continue
            at = pe.offset_of(pe.res_rva + (field_data & 0x7FFFFFFF))
            rva, size, cp = struct.unpack_from("<III", pe.data, at)
            leaves.append({"path": path + (key,), "rva": rva, "size": size, "cp": cp})

    visit(pe.res_rva, ())
    out = []
    for rec in leaves:
        path = list(rec.pop("path")) + [1033] * 3
        rec["type"], rec["name"], rec["lang"] = path[0], path[1], path[2]
        out.append(rec)
    return out


def type_label(what) -> str:
    return TYPE_NAMES.get(what, str(what))


def safe_part(value) -> str:
    """資源名字串可能含控制字元（自訂型別常這樣），檔名先淨化；摘要仍留原值。"""
    if isinstance(value, int):
        return str(value)
    cleaned = SAFE_CHARS.sub("_", value.replace("\x00", "")).strip("._")
    return cleaned[:40] or "name"


def build_bitmap(raw: bytes) -> bytes:
    """DIB（BITMAPINFOHEADER 起頭）補上 14 位元組 BMP 檔頭。"""
    hdrsize = struct.unpack_from("<I", raw, 0)[0]
    comp = struct.unpack_from("<I", raw, 16)[0]
    extra = 12 if comp == 3 else 0  # BI_BITFIELDS 的三個遮罩在 DIB 頭之後
    size = 14 + len(raw)
    return b"BM" + struct.pack("<IHHI", size, 0, 0, 14 + hdrsize + extra) + raw


def build_group(raw: bytes, children: dict) -> bytes:
    """GROUP_ICON/GROUP_CURSOR → .ico/.cur：標頭 + 目錄項 + 子資源串接。

    群組裡的目錄項是 14 位元組（最後是子資源 id），輸出檔的目錄項是 16 位元組
    （同樣位置換成資料偏移），所以要逐項改寫。
    """
    if len(raw) < 6:
        raise PEError("群組頭太短")
    kind, count = u16(raw, 2), u16(raw, 4)
    if kind not in (1, 2) or count == 0:
        raise PEError(f"不認識的群組頭 kind={kind} count={count}")
    if len(raw) < 6 + 14 * count:
        raise PEError("群組目錄長度不足")
    items = []
    for i in range(count):
        width, height, colors, _res, planes, bits, _size, resid = struct.unpack_from(
            "<BBBBHHIH", raw, 6 + i * 14
        )
        if resid not in children:
            raise PEError(f"群組引用的 #{resid} 不存在")
        items.append((width, height, colors, planes, bits, children[resid]))
    out = bytearray(struct.pack("<HHH", 0, kind, len(items)))
    offset = 6 + 16 * len(items)
    table = bytearray()
    data = bytearray()
    for width, height, colors, planes, bits, blob in items:
        table += struct.pack(
            "<BBBBHHII", width, height, colors, 0, planes, bits, len(blob), offset
        )
        data += blob
        offset += len(blob)
    return bytes(out + table + data)


def _take_string(raw: bytes, at: int, as_class: bool = False) -> tuple[str, int]:
    """版式裡的名字串：0xFFFF + WORD（類別序號，或指向字串表的 id），否則 NUL
    結尾的 UTF-16（空字串就是一個 NUL，所以不能先跳一格）。"""
    if u16(raw, at) == 0xFFFF:
        val = u16(raw, at + 2)
        if as_class:
            return f"#{CLASS_ORDINALS.get(val) or val}", at + 4
        return f"string-table #{val}", at + 4
    end = at
    while end + 1 < len(raw) and u16(raw, end):
        end += 2
    return raw[at:end].decode("utf-16-le", "replace"), end + 2


def _take_controls(raw: bytes, at: int, count: int, ex: bool) -> tuple[list, int]:
    """控制項清單；ex=True 是 DLGITEMTEMPLATEEX（多 helpID、id 為 DWORD）。"""
    controls = []
    for idx in range(count):
        if idx:  # 每項從 DWORD 邊界開始
            at = align4(at)
        if ex:
            help_id, exstyle, style, cx2, cy2, cwx, cwy, cid = struct.unpack_from(
                "<IIIhhhhI", raw, at
            )
            at += 24
        else:
            style, exstyle, cx2, cy2, cwx, cwy, cid = struct.unpack_from(
                "<IIhhhhH", raw, at
            )
            help_id = None
            at += 18
        ccls, at = _take_string(raw, at, as_class=True)
        ctext, at = _take_string(raw, at)
        extra = u16(raw, at)
        at += 2
        data = raw[at : at + extra].hex() if extra else None
        at += extra
        controls.append(
            {
                "id": None if cid in (0xFFFFFFFF, 0xFFFF) else cid,
                "class": ccls,
                "text": ctext,
                "style": style,
                "exstyle": exstyle,
                "help_id": help_id,
                "rect": [cx2, cy2, cwx, cwy],
                "creation_data": data,
            }
        )
    return controls, at


def decode_dialog(raw: bytes) -> dict:
    """對話框版式 → dict。DLGTEMPLATE（18 B 頭）與 DLGTEMPLATEEX（26 B 頭）都吃；
    解完必須剛好吃掉整個 buffer，否則視為解錯，呼叫端保留原字節。"""
    if len(raw) < 24:
        raise PEError("對話框模板太短")
    ex = struct.unpack_from("<HH", raw, 0) == (1, 0xFFFF)
    if ex:
        head = struct.unpack_from("<IIIHhhhh", raw, 4)
        help_id, exstyle, style, count, x, y, cx, cy = head
        at = 26
    else:
        style, exstyle, count, x, y, cx, cy = struct.unpack_from("<IIHhhhh", raw, 0)
        help_id, at = None, 18
    menu, at = _take_string(raw, at)
    cls, at = _take_string(raw, at, as_class=True)
    title, at = _take_string(raw, at)
    font = None
    if style & DS_SETFONT:  # 字型段：字号（EX 還多粗細/字集）+ 字型名
        point = u16(raw, at)
        at += 2
        weight = charset = None
        if ex and point:
            weight = u16(raw, at)
            charset = raw[at + 2]
            at = align4(at + 3)
        name, at = _take_string(raw, at)
        font = {"name": name, "pointsize": point, "weight": weight, "charset": charset}
    controls, at = _take_controls(raw, align4(at), count, ex)
    if at != len(raw):
        raise PEError(f"{'EX' if ex else 'classic'} 停在 {at}，應為 {len(raw)}")
    return {
        "template": "DLGTEMPLATEEX" if ex else "DLGTEMPLATE",
        "style": style,
        "exstyle": exstyle,
        "help_id": help_id,
        "rect": [x, y, cx, cy],
        "menu": menu,
        "window_class": cls,
        "title": title,
        "font": font,
        "controls": controls,
    }


def decode_string_block(block_id: int, raw: bytes) -> dict:
    """RT_STRING：一個 block 最多 16 條，每條先給 UTF-16 字元數（0 表示該槽空缺）。"""
    out = {}
    at = 0
    for slot in range(16):
        if at + 2 > len(raw):
            break
        nchars = u16(raw, at)
        at += 2
        if not nchars:
            continue
        out[str(block_id * 16 + slot)] = raw[at : at + nchars * 2].decode(
            "utf-16-le", "replace"
        )
        at += nchars * 2
    return out


def decode_version(raw: bytes) -> dict:
    """VS_VERSIONINFO：取固定欄位與 StringFileInfo 字串表。"""
    out: dict = {}
    length = u16(raw, 0)
    end = raw.find(b"\x00\x00", 6)
    at = align4(end + 2) if end != -1 else 6
    if at + 52 <= len(raw):
        _, _, filevs, prodvs, mask, flags = struct.unpack_from("<IIQQII", raw, at)
        def quad(value: int) -> str:
            return ".".join(str((value >> s) & 0xFFFF) for s in (48, 32, 16, 0))

        out["file_version"] = quad(filevs)
        out["product_version"] = quad(prodvs)
        out["file_flags_mask"] = mask
        out["file_flags"] = flags
    strings: dict = {}

    def scan(lo: int, hi: int) -> None:
        pos = lo
        while pos + 6 <= hi:
            total = u16(raw, pos)
            vlen = u16(raw, pos + 2)
            typ = u16(raw, pos + 4)
            if total <= 0 or pos + total > hi:
                break
            nend = raw.find(b"\x00\x00", pos + 6)
            name = (
                raw[pos + 6 : nend].decode("utf-16-le", "replace") if nend != -1 else ""
            )
            after = align4(nend + 2) if nend != -1 else pos + total
            if name in ("StringFileInfo", "VarFileInfo"):
                scan(after, pos + total)
            elif typ == 1 and vlen:
                value = raw[after : after + vlen * 2].decode("utf-16-le", "replace")
                strings[name] = value.rstrip("\x00")
            pos = align4(pos + total)

    scan(at, min(length if length > 0 else len(raw), len(raw)))
    out["strings"] = strings
    return out


def dump(path: Path, outdir: Path | None = None, verbose: bool = False) -> dict:
    """把一個 PE 的資源解碼/落地，回傳摘要（型別統計、版式、字串表、版本）。"""
    data = path.read_bytes()
    pe = PEImage(data)
    entries = walk_resources(pe)
    for rec in entries:
        rec["bytes"] = pe.read(rec["rva"], rec["size"])
    # 子資源按 id 索引，供 GROUP_* 組裝 .ico/.cur
    children: dict = {}
    for rec in entries:
        if isinstance(rec["name"], int) and rec["type"] in (ICON, CURSOR):
            children[(rec["type"], rec["name"])] = rec["bytes"]

    counts: dict = {}
    files: list[str] = []
    text: dict = {}
    manifest: list[dict] = []
    dialogs: dict = {}
    dialog_files: dict = {}
    strings: dict = {}
    for rec in entries:
        label = type_label(rec["type"])
        counts[label] = counts.get(label, 0) + 1
        name = rec["name"]
        raw = rec["bytes"]
        stem = f"{label}_{safe_part(name)}"
        item: dict = {
            "type": label,
            "name": name,
            "lang": rec["lang"],
            "size": rec["size"],
            "bytes_sha256": hashlib.sha256(raw).hexdigest()[:16],
        }
        if not isinstance(name, int):
            item["raw_name"] = repr(name)
        ext = "bin"
        payload: bytes | str = raw
        dlg_key = None
        if label == "BITMAP":
            ext, payload = "bmp", build_bitmap(raw)
        elif rec["type"] in GROUP_CHILD:
            want = GROUP_CHILD[rec["type"]]
            kids = {rid: blob for (t, rid), blob in children.items() if t == want}
            try:
                payload = build_group(raw, kids)
                ext = "cur" if want == CURSOR else "ico"
            except PEError as exc:
                item["note"] = f"群組未能組裝：{exc}"
        elif label == "DIALOG":
            try:
                decoded = decode_dialog(raw)
            except Exception as exc:  # 自訂版式等異常情況留證據，不假裝成功
                item["note"] = f"版式未解：{exc!r}"
            else:
                ext = "json"
                payload = json.dumps(decoded, ensure_ascii=False, indent=1)
                dlg_key = str(name)
                dialogs[dlg_key] = decoded
        elif label == "VERSION":
            info = decode_version(raw)
            ext, payload = "json", json.dumps(info, ensure_ascii=False, indent=1)
            text["version"] = info
        elif label == "STRING":
            block = name if isinstance(name, int) else 0
            found = decode_string_block(block, raw)
            ext, payload = "json", json.dumps(found, ensure_ascii=False, indent=1)
            strings.update(found)
        elif label == "MANIFEST":
            ext, payload = "xml", raw.decode("utf-8", "replace")
        elif raw[:8] == PNG_MAGIC:
            ext = "png"
        filename = f"{stem}.{ext}"
        item["file"], item["ext"] = filename, ext
        if dlg_key:  # 檔名算出來之後才記得住，補全字串表時要照這個檔覆寫
            dialog_files[dlg_key] = filename
        files.append(filename)
        manifest.append(item)
        if outdir is not None:
            outdir.mkdir(parents=True, exist_ok=True)
            target = outdir / filename
            if isinstance(payload, bytes):
                target.write_bytes(payload)
            else:
                target.write_text(payload, encoding="utf-8")
    # 對話框裡的 "string-table #N" 用同一份資源的字串表補全，省去人工對照
    if strings:
        for dlg in dialogs.values():
            for ctr in dlg.get("controls", []):
                hit = STR_REF.match(ctr.get("text") or "")
                if hit and hit.group(1) in strings:
                    ctr["text"] = strings[hit.group(1)]
        # 已寫盤的 JSON 同步更新
        if outdir is not None:
            for key, decoded in dialogs.items():
                (outdir / dialog_files[key]).write_text(
                    json.dumps(decoded, ensure_ascii=False, indent=1), encoding="utf-8"
                )
    if dialogs:
        text["dialogs"] = dialogs
    if strings:
        text["strings"] = strings
    summary = {
        "kind": "pe_resource_summary",
        "input": str(path),
        "input_bytes": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "entries": len(entries),
        "types": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "text": text,
        "files": files,
    }
    if outdir is not None:
        (outdir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        summary["outdir"] = str(outdir)
    if verbose:
        digest = summary["input_sha256"][:16]
        print(
            f"[i] {path.name}  {len(data)} B  sha256={digest}…  資源條目 {len(entries)}"
        )
        for key, val in summary["types"].items():
            print(f"    {key:<14} {val}")
        vs = text.get("version", {}).get("strings") or {}
        if vs:
            joined = "; ".join(f"{k}={vs[k]}" for k in sorted(vs)[:6])
            print(f"    version: {joined}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="要讀的 exe/dll（全程唯讀）")
    ap.add_argument("--dump", type=Path, default=None, help="把資源寫進這個目錄")
    ap.add_argument("--json", type=Path, default=None, help="摘要另存成 JSON")
    ap.add_argument("--summary", action="store_true", help="列印型別統計與版本資訊")
    args = ap.parse_args()
    summary = dump(args.input, args.dump, verbose=args.summary or args.dump is not None)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(f"[+] summary -> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
