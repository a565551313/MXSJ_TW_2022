#!/usr/bin/env python3
"""pe_resource_dump 的回歸測試。

鎖住我們踩過的坑：資源的名稱/資料偏移一律相對 `.rsrc` 起點；名字串是「WORD 字元數 +
UTF-16」；版式字串是「NUL 結尾的 UTF-16」（不是長度前綴）；群組目錄項 14 B 而輸出目錄項
16 B；DLGTEMPLATEEX 的控制項 id 是 DWORD。做法是自己蓋一個最小 PE 餵進去，最後再用真的
`mxLauncher.exe`（在倉庫根時）核對條目數與解碼結果。
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("pe_resource_dump.py")
_loader = importlib.machinery.SourceFileLoader("pe_resource_dump", str(MODULE))
_spec = importlib.util.spec_from_loader("pe_resource_dump", _loader)
prd = importlib.util.module_from_spec(_spec)
_loader.exec_module(prd)

FILE_ALIGN = 0x200
RES_RVA = 0x2000


def u16s(text: str) -> bytes:
    return text.encode("utf-16-le") + b"\x00\x00"


def pad4(data: bytes) -> bytes:
    return data + b"\x00" * ((4 - len(data) % 4) % 4)


def align4(value: int) -> int:
    return (value + 3) & ~3


def dir_node(entries: list, named: int = 0) -> bytes:
    """資源目錄節點（16 B 頭：保留 4 + 時間 4 + 版本 2+2 + 具名數 2 + id 數 2）。"""
    return struct.pack(
        "<IIHHHH", 0, 0, 0, 0, named, len(entries) - named
    ) + b"".join(
        struct.pack("<II", a, b) for a, b in entries
    )


class ResBuilder:
    """把 .rsrc 的內容蓋出來：所有 offset 都以 .rsrc 起點為基準（跟 Windows 一致）。"""

    def __init__(self):
        self.buf = bytearray()

    def put(self, data: bytes) -> int:
        at = len(self.buf)
        self.buf += pad4(data)
        return at

    def leaf(self, payload: bytes, lang: int = 1033) -> int:
        at = self.put(payload)
        return self.put(struct.pack("<III", RES_RVA + at, len(payload), lang))

    def tree(self, name_field: int, id_field: int, payload: bytes) -> tuple:
        """回傳 (型別欄位, 該型別的下一層目錄位置)；下一層目錄只有 id→資料 一條。"""
        de = self.leaf(payload)
        names_at = self.put(dir_node([(id_field, de)]))
        return name_field, names_at


def classic_dialog() -> bytes:
    """DLGTEMPLATE：1 個 Static，標題 &New；字串全部 NUL 結尾 UTF-16。"""
    raw = struct.pack("<IIHhhhh", 0x80C800C8, 0, 1, 1, 2, 183, 70)
    raw += b"\x00\x00" + b"\x00\x00" + b"\x00\x00"  # menu / class / title 皆空
    raw += struct.pack("<H", 8) + u16s("MS Shell Dlg")
    raw = raw.ljust(align4(len(raw)), b"\x00")
    raw += struct.pack("<IIhhhhH", 0x50000003, 0, 6, 5, 123, 8, 0xFFFF)
    raw += b"\xff\xff\x82\x00" + u16s("&New") + struct.pack("<H", 0)
    return raw


def ex_dialog() -> bytes:
    """DLGTEMPLATEEX：26 B 頭 + 字型段（point/weight/charset）+ 1 個控制項。"""
    raw = struct.pack("<HHIIIHhhhh", 1, 0xFFFF, 0, 0, 0x80C80048, 1, 0, 0, 60, 20)
    raw += b"\x00\x00" + b"\x00\x00" + u16s("T")
    raw += struct.pack("<HH", 9, 400) + b"\x00\x00" + u16s("MS Shell Dlg")
    raw = raw.ljust(align4(len(raw)), b"\x00")
    raw += struct.pack("<IIIhhhhI", 0, 0, 0x50000003, 1, 2, 3, 4, 0xFFFFFFFF)
    raw += b"\xff\xff\x82\x00" + u16s("hi") + struct.pack("<H", 0)
    return raw


def build_fake_pe() -> bytes:
    dib = struct.pack("<IiiHHIIiiII", 40, 2, 1, 1, 24, 0, 6, 0, 0, 0, 0) + b"\xff" * 6
    icon = struct.pack(
        "<IiiHHIIiiII", 40, 1, 2, 1, 32, 0, 4, 0, 0, 0, 0
    ) + b"\xff" * 4 + b"\x00" * 4
    strings = (
        struct.pack("<HH", 0, 3) + "abc".encode("utf-16-le") + b"\x00\x00"
    )
    group = struct.pack("<HHH", 0, 1, 1) + struct.pack(
        "<BBBBHHIH", 1, 1, 0, 0, 1, 32, len(icon), 1
    )
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20

    b = ResBuilder()
    root_at = b.put(b"\x00" * 80)  # 根目錄要擺在 .rsrc 開頭，先預留位置
    png_name_at = b.put(struct.pack("<H", 3) + "PNG".encode("utf-16-le"))
    children = []
    children.append(b.tree(2, 101, dib))
    children.append(b.tree(3, 1, icon))
    children.append(b.tree(6, 1, strings))
    children.append(b.tree(5, 100, ex_dialog()))
    children.append(b.tree(14, 149, group))
    children.append(b.tree(png_name_at | 0x80000000, 1, png))
    children.append(b.tree(5, 7, classic_dialog()))
    entries = sorted(children, key=lambda c: not (c[0] & 0x80000000))  # 具名型別排前面
    root = pad4(dir_node([(t, off | 0x80000000) for t, off in entries], named=1))
    assert len(root) <= 80, len(root)
    b.buf[root_at : root_at + len(root)] = root
    res = bytes(b.buf)
    res_padded = res + b"\x00" * (-len(res) % FILE_ALIGN)

    def section(name: str, vsize: int, vaddr: int, rawsize: int, rawptr: int) -> bytes:
        return name.encode("latin-1").ljust(8, b"\x00") + struct.pack(
            "<IIIIIIHHI", vsize, vaddr, rawsize, rawptr, 0, 0, 0, 0, 0x40000040
        )

    opt_size = 224
    head = bytearray(b"MZ" + b"\x00" * 0x3A + struct.pack("<I", 0x40))
    head += b"PE\x00\x00"
    head += struct.pack("<HHIIIHH", 0x14C, 2, 0, 0, 0, opt_size, 0x0102)
    opt = bytearray(opt_size)
    struct.pack_into("<H", opt, 0, 0x10B)  # PE32
    # DataDirectory[RESOURCE]
    struct.pack_into("<II", opt, 96 + 8 * 2, RES_RVA, len(res))
    head += bytes(opt)
    head += section(".text", 0x1000, 0x1000, FILE_ALIGN, FILE_ALIGN)
    head += section(".rsrc", len(res), RES_RVA, len(res_padded), 2 * FILE_ALIGN)
    head = head.ljust(FILE_ALIGN, b"\x00")
    return bytes(head) + b"\xcc" * FILE_ALIGN + res_padded


class DecoderTests(unittest.TestCase):
    def test_bitmap_gets_file_header(self):
        dib = struct.pack(
            "<IiiHHIIiiII", 40, 2, 1, 1, 24, 0, 6, 0, 0, 0, 0
        ) + b"\xff" * 6
        out = prd.build_bitmap(dib)
        self.assertEqual(out[:2], b"BM")
        self.assertEqual(struct.unpack_from("<I", out, 2)[0], len(out))
        self.assertEqual(struct.unpack_from("<I", out, 10)[0], 54)  # bfOffBits
        self.assertEqual(out[14:], dib)

    def test_string_block_skips_empty_slots(self):
        raw = b"\x00\x00" + struct.pack("<H", 3)
        raw += "abc".encode("utf-16-le") + b"\x00\x00"
        self.assertEqual(prd.decode_string_block(2, raw), {"33": "abc"})

    def test_group_icon_rewrites_offsets(self):
        kids = {1: b"A" * 4, 2: b"B" * 6}
        raw = struct.pack("<HHH", 0, 1, 2) + b"".join(
            struct.pack("<BBBBHHIH", 1, 1, 0, 0, 1, 32, size, rid)
            for rid, size in ((1, 4), (2, 6))
        )
        out = prd.build_group(raw, kids)
        self.assertEqual(out[:6], struct.pack("<HHH", 0, 1, 2))
        self.assertEqual(out[-10:], b"A" * 4 + b"B" * 6)
        for i, size in enumerate((4, 6)):
            off = struct.unpack_from("<I", out, 6 + 16 * i + 12)[0]
            self.assertEqual(out[off : off + size], bytes([ord("A") + i]) * size)
        with self.assertRaises(prd.PEError):
            prd.build_group(struct.pack("<HHH", 0, 1, 1) + b"\x00" * 14, {})

    def test_dialog_string_encoding(self):
        take = prd._take_string
        self.assertEqual(take(u16s("Hello") + b"\x11\x22", 0), ("Hello", 12))
        self.assertEqual(take(b"\x00\x00" + b"\x33\x44", 0), ("", 2))
        self.assertEqual(take(b"\xff\xff\x82\x00", 0, as_class=True), ("#Static", 4))
        self.assertEqual(take(b"\xff\xff\x80\x00", 0), ("string-table #128", 4))

    def test_classic_dialog_round_trip(self):
        decoded = prd.decode_dialog(classic_dialog())
        self.assertEqual(decoded["template"], "DLGTEMPLATE")
        self.assertEqual(decoded["rect"], [1, 2, 183, 70])
        self.assertEqual(decoded["font"]["pointsize"], 8)
        ctr = decoded["controls"][0]
        got = (ctr["class"], ctr["text"], ctr["id"])
        self.assertEqual(got, ("#Static", "&New", None))

    def test_ex_dialog_round_trip(self):
        decoded = prd.decode_dialog(ex_dialog())
        self.assertEqual(decoded["template"], "DLGTEMPLATEEX")
        self.assertEqual(decoded["title"], "T")
        self.assertEqual(decoded["font"]["weight"], 400)
        ctr = decoded["controls"][0]
        got = (ctr["class"], ctr["text"], ctr["rect"])
        self.assertEqual(got, ("#Static", "hi", [1, 2, 3, 4]))

    def test_truncated_template_is_rejected_not_guessed(self):
        with self.assertRaises(prd.PEError):
            prd.decode_dialog(b"\x01\x00\xff\xff" + b"\x00" * 40)


class FakePeTests(unittest.TestCase):
    def setUp(self):
        self.blob = build_fake_pe()

    def test_walk_finds_every_leaf(self):
        pe = prd.PEImage(self.blob)
        recs = prd.walk_resources(pe)
        keyed = sorted((prd.type_label(r["type"]), r["name"]) for r in recs)
        self.assertEqual(
            keyed,
            sorted(
                [("BITMAP", 101), ("ICON", 1), ("STRING", 1), ("DIALOG", 100),
                 ("DIALOG", 7), ("GROUP_ICON", 149), ("PNG", 1)]
            ),
        )

    def test_named_type_string_is_read(self):
        pe = prd.PEImage(self.blob)
        labels = {prd.type_label(r["type"]) for r in prd.walk_resources(pe)}
        self.assertIn("PNG", labels)

    def test_dump_writes_readable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "fake.exe"
            src.write_bytes(self.blob)
            out = Path(tmp) / "r"
            summary = prd.dump(src, out)
            files_wrong = ["GROUP_ICON_149.ico", "BITMAP_101.bmp"]
            names = {p.name for p in out.iterdir()}
            # 單張 ICON/CURSOR 是裸 DIB（.bin）；能直接開的是群組組出來的 .ico/.cur
            for expect in ("BITMAP_101.bmp", "ICON_1.bin", "GROUP_ICON_149.ico",
                           "DIALOG_100.json", "DIALOG_7.json", "PNG_1.png",
                           "STRING_1.json", "manifest.json"):
                self.assertIn(expect, names)
            bmp = (out / "BITMAP_101.bmp").read_bytes()
            self.assertEqual((bmp[:2], bmp[14:18]), (b"BM", struct.pack("<I", 40)))
            ico = (out / "GROUP_ICON_149.ico").read_bytes()
            # 首張圖的資料偏移 = 6 + 16
            self.assertEqual(struct.unpack_from("<I", ico, 18)[0], 22)
            dlg = json.loads((out / "DIALOG_100.json").read_text(encoding="utf-8"))
            self.assertEqual(dlg["controls"][0]["text"], "hi")
            for name in files_wrong:  # 群組檔不能被版式覆寫
                self.assertFalse((out / name).read_bytes().startswith(b"{"))
            # block 1 的第 1 槽 → id = 1*16 + 1（RT_STRING 的編號規則）
            self.assertEqual(summary["text"]["strings"], {"17": "abc"})
            self.assertEqual(summary["entries"], 7)

    def test_input_file_is_never_touched(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "fake.exe"
            src.write_bytes(self.blob)
            before = src.read_bytes()
            prd.dump(src, Path(tmp) / "o")
            self.assertEqual(src.read_bytes(), before)


@unittest.skipUnless(
    (Path(__file__).resolve().parents[2] / "mxLauncher.exe").exists(),
    "需要客戶端目錄（mxLauncher.exe 不在倉庫根時跳過）",
)
class RealLauncherTests(unittest.TestCase):
    def test_launcher_resources_decode(self):
        src = Path(__file__).resolve().parents[2] / "mxLauncher.exe"
        summary = prd.dump(src, None)
        self.assertEqual(summary["entries"], 86)
        self.assertEqual(summary["types"]["BITMAP"], 30)
        self.assertEqual(summary["types"]["DIALOG"], 5)
        # 5 個版式全部要解得開；解不開會被標 note，不會假裝成功
        self.assertEqual(len(summary["text"]["dialogs"]), 5)
        self.assertEqual(summary["text"]["dialogs"]["100"]["title"], "梦想世界更新程序")
        self.assertEqual(summary["text"]["version"]["file_version"], "128.0.1.0")
        self.assertGreaterEqual(len(summary["text"]["strings"]), 80)


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=2))
