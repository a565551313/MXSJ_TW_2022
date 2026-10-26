#!/usr/bin/env python3
"""mxmain_rtti 的回歸測試。

兩種樣本：自己蓋的最小 PE（鎖住欄位順序與步長），以及倉庫根的 `mxmain.dll`
（鎖住實測數字與幾個已知答案：std 例外五層鏈、`CMainWnd` 三層繼承、
`CCommonWnd` 只有一個虛表槽、`CLZWDecompress` 的第 2 槽等於
`notes/native_tcp_channel.md` 記的 0x4c5e40）。
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.machinery
import importlib.util
import io
import struct
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("mxmain_rtti.py")
_loader = importlib.machinery.SourceFileLoader("mxmain_rtti", str(MODULE))
_spec = importlib.util.spec_from_loader("mxmain_rtti", _loader)
mrtti = importlib.util.module_from_spec(_spec)
sys.modules["mxmain_rtti"] = mrtti  # dataclass 需要模組已登記在 sys.modules
_loader.exec_module(mrtti)

IMAGE_BASE = 0x400000
FILE_ALIGN = 0x200

TEXT_RVA = 0x1000
RDATA_RVA = 0x3000
DATA_RVA = 0x5000

# 合成的類別
TD_FOO = IMAGE_BASE + DATA_RVA + 0x100
TD_BAR = IMAGE_BASE + DATA_RVA + 0x140
COL_FOO = IMAGE_BASE + RDATA_RVA + 0x100
COL_BAR = IMAGE_BASE + RDATA_RVA + 0x200
# 虛表的第 -1 格存 COL 指標（在 .rdata+0x300 / +0x400），+4 起才是槽位
VT_FOO = IMAGE_BASE + RDATA_RVA + 0x304
VT_BAR = IMAGE_BASE + RDATA_RVA + 0x404
FUNC_A = IMAGE_BASE + TEXT_RVA + 0x100
FUNC_B = IMAGE_BASE + TEXT_RVA + 0x120
FUNC_C = IMAGE_BASE + TEXT_RVA + 0x140
CTOR_FOO = IMAGE_BASE + TEXT_RVA + 0x200
CTOR_BAR = IMAGE_BASE + TEXT_RVA + 0x220
REG_WRITE = IMAGE_BASE + TEXT_RVA + 0x240


def type_descriptor(name: str, vfptr: int = 0x0077CB64) -> bytes:
    return struct.pack("<II", vfptr, 0) + name.encode("latin-1") + b"\x00"


def hierarchy(block_off: int, bases: list[int]) -> bytes:
    """CHD + BCA + 每個基底的 28 位元組描述符；`block_off` 是這塊在 .rdata 內的位移。"""
    bca_off = 16
    bcd_off = bca_off + 4 * len(bases)
    base_va = IMAGE_BASE + RDATA_RVA + block_off
    blob = bytearray()
    blob += struct.pack("<IIII", 0, 0, len(bases), base_va + bca_off)
    for index in range(len(bases)):
        blob += struct.pack("<I", base_va + bcd_off + 28 * index)
    for index, td in enumerate(bases):
        blob += struct.pack(
            "<IIIIIII", td, len(bases) - index - 1, 0, 0xFFFFFFFF, 0, 0x40, 0
        )
    return bytes(blob)


def build_fake_pe() -> bytes:
    # .text：三個函式入口 + 一個構造函式把虛表寫進 (%esi)
    text = bytearray(b"\xcc" * 0x300)
    for at in (0x100, 0x120, 0x140):
        text[at : at + 4] = b"\x55\x8b\xec\xc3"
    ctor_at = 0x200
    text[ctor_at : ctor_at + 10] = (
        b"\x55\x8b\xec" + b"\xc7\x06" + struct.pack("<I", VT_FOO) + b"\xc3"
    )
    # 帶 disp8 的形式：c7 46 08 <imm32> —— 只看「imm 前兩格是 C7 xx」會漏掉
    disp_at = 0x220
    text[disp_at : disp_at + 11] = (
        b"\x55\x8b\xec" + b"\xc7\x46\x08" + struct.pack("<I", VT_BAR) + b"\xc3"
    )
    # 暫存器形式：c7 c0 <imm32> 寫的是 eax，不是 vfptr，必須被擋
    reg_at = 0x240
    text[reg_at : reg_at + 10] = b"\xc7\xc0" + struct.pack("<I", VT_FOO)
    # 假入口：位元組 0x0F 開頭，落在 .text 內但不像函式入口
    text[0x180] = 0x0F

    # .rdata：兩個 COL + 兩塊 CHD/BCA/BCD + 兩張虛表
    rdata = bytearray(b"\x00" * 0x800)
    foo_hierarchy = hierarchy(0x500, [TD_FOO])
    bar_hierarchy = hierarchy(0x600, [TD_BAR, TD_FOO])
    rdata[0x100:0x114] = struct.pack(
        "<IIIII", 0, 0, 0, TD_FOO, IMAGE_BASE + RDATA_RVA + 0x500
    )
    rdata[0x200:0x214] = struct.pack(
        "<IIIII", 0, 0, 0, TD_BAR, IMAGE_BASE + RDATA_RVA + 0x600
    )
    rdata[0x500 : 0x500 + len(foo_hierarchy)] = foo_hierarchy
    rdata[0x600 : 0x600 + len(bar_hierarchy)] = bar_hierarchy
    rdata[0x300:0x30C] = struct.pack("<III", COL_FOO, FUNC_A, FUNC_B)
    rdata[0x400:0x40C] = struct.pack(
        "<III", COL_BAR, FUNC_C, IMAGE_BASE + TEXT_RVA + 0x180
    )
    # 再後面接字串：0x696969（"ii"）落在 .text 範圍內，也必須被擋掉
    rdata[0x40C:0x414] = b"iiiiiiii"

    # .data：兩個 TypeDescriptor
    data = bytearray(b"\x00" * 0x200)
    foo = type_descriptor(".?AVCFoo@@")
    bar = type_descriptor(".?AVCBar@@")
    data[0x100 : 0x100 + len(foo)] = foo
    data[0x140 : 0x140 + len(bar)] = bar

    blobs = {
        ".text": (TEXT_RVA, 0x400, bytes(text)),
        ".rdata": (RDATA_RVA, 0x800, bytes(rdata)),
        ".data": (DATA_RVA, 0x200, bytes(data)),
    }

    def section(name: str, vsize: int, rva: int, raw: int, raw_size: int) -> bytes:
        return name.encode("latin-1").ljust(8, b"\x00") + struct.pack(
            "<IIIIIIHHI", vsize, rva, raw_size, raw, 0, 0, 0, 0, 0x40000040
        )

    opt_size = 224
    head = bytearray(b"MZ" + b"\x00" * 0x3A + struct.pack("<I", 0x40))
    head += b"PE\x00\x00"
    head += struct.pack("<HHIIIHH", 0x14C, len(blobs), 0, 0, 0, opt_size, 0x0102)
    opt = bytearray(opt_size)
    struct.pack_into("<H", opt, 0, 0x10B)
    struct.pack_into("<I", opt, 28, IMAGE_BASE)
    head += bytes(opt)
    cursor = FILE_ALIGN
    body = bytearray()
    for name, (rva, raw_size, payload) in blobs.items():
        head += section(name, len(payload), rva, cursor, raw_size)
        body += payload.ljust(raw_size, b"\x00")
        cursor += raw_size
    return bytes(head.ljust(FILE_ALIGN, b"\x00")) + bytes(body)


class SyntheticPeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "fake.dll"
        self.path.write_bytes(build_fake_pe())
        self.report = mrtti.build_report(self.path)
        self.classes = {c["name"]: c for c in self.report["classes"]}

    def tearDown(self):
        self.tmp.cleanup()

    def test_type_descriptors_found(self):
        self.assertEqual(set(self.classes), {".?AVCFoo@@", ".?AVCBar@@"})
        self.assertEqual(self.report["summary"]["type_descriptors"], 2)

    def test_object_locator_and_vftable(self):
        foo = self.classes[".?AVCFoo@@"]
        self.assertEqual(foo["object_locator_va"], hex(COL_FOO))
        self.assertEqual(foo["vftable_va"], hex(VT_FOO))
        self.assertEqual(foo["virtual_slots"], [hex(FUNC_A), hex(FUNC_B)])

    def test_fake_pointer_and_trailing_string_stop_the_scan(self):
        # 槽位後面刻意放了兩個假指標：一個目標是 0x0F 開頭的位元組（不像函式入口），
        # 另一個是 "iiii"（0x69696969）——兩者都落在 .text 內，看起來完全合法。
        # 掃描必須停在 FUNC_C 之後，兩個都不能被當成槽。
        bar = self.classes[".?AVCBar@@"]
        self.assertEqual(bar["virtual_slots"], [hex(FUNC_C)])

    def test_hierarchy_is_self_then_base(self):
        bar = self.classes[".?AVCBar@@"]
        names = [b["name"] for b in bar["bases"]]
        self.assertEqual(names, [".?AVCBar@@", ".?AVCFoo@@"])
        self.assertEqual(bar["bases"][1]["mdisp"], 0)

    def test_vfptr_write_site_is_instruction_start(self):
        # 55 8b ec | c7 06 | imm32 → 指令在 CTOR_FOO+3，立即數在 CTOR_FOO+5
        foo = self.classes[".?AVCFoo@@"]
        site = [s for s in foo["vfptr_writes"] if s["site_va"] == hex(CTOR_FOO + 3)]
        self.assertEqual(len(site), 1)
        self.assertEqual(site[0]["imm_va"], hex(CTOR_FOO + 5))

    def test_vfptr_write_with_displacement_is_found(self):
        # c7 46 08 <imm32>：只比對「imm 前兩格」會漏掉這種寫法
        bar = self.classes[".?AVCBar@@"]
        sites = {s["site_va"]: s for s in bar["vfptr_writes"]}
        self.assertIn(hex(CTOR_BAR + 3), sites)
        self.assertEqual(sites[hex(CTOR_BAR + 3)]["imm_va"], hex(CTOR_BAR + 6))

    def test_vfptr_write_to_register_is_not_counted(self):
        # c7 c0 <imm32> 寫的是 eax，不是 vfptr
        foo = self.classes[".?AVCFoo@@"]
        self.assertNotIn(hex(REG_WRITE), [s["site_va"] for s in foo["vfptr_writes"]])

    def test_summary_counts(self):
        summary = self.report["summary"]
        self.assertEqual(summary["with_object_locator"], 2)
        self.assertEqual(summary["with_vftable"], 2)
        self.assertEqual(summary["vftable_slot_counts"], {"1": 1, "2": 1})
        self.assertEqual(summary["with_secondary_vftable"], 0)
        self.assertEqual(summary["hierarchy_errors"], [])

    def test_input_is_never_touched(self):
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        mrtti.build_report(self.path)
        self.assertEqual(before, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_output_may_not_alias_the_input(self):
        # --md/--json 指向映像本身（同一路徑、symlink、硬連結）時必須在解析前就拒絕，
        # 否則 write_text() 會把剛解析完的映像截斷成 0 位元組。
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        for target in (self.path, self.path.with_suffix(".md")):
            if target != self.path:
                target.unlink(missing_ok=True)
                target.hardlink_to(self.path)
            with (
                self.assertRaises(SystemExit),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                mrtti.main([str(self.path), "--md", str(target)])
        self.assertEqual(before, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_output_next_to_input_is_allowed(self):
        out = Path(self.tmp.name) / "report.md"
        self.assertEqual(mrtti.main([str(self.path), "--md", str(out)]), 0)
        self.assertIn("CFoo", out.read_text(encoding="utf-8"))


CLIENT = Path(__file__).resolve().parents[2] / "mxmain.dll"
CLIENT_SHA256 = "637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d"


@unittest.skipUnless(CLIENT.is_file(), "倉庫根沒有 mxmain.dll")
class RealClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mrtti.build_report(CLIENT)
        cls.classes = {c["name"]: c for c in cls.report["classes"]}

    def test_locked_input_digest(self):
        self.assertEqual(self.report["summary"]["sha256"], CLIENT_SHA256)

    def test_counts(self):
        summary = self.report["summary"]
        self.assertEqual(summary["type_descriptors"], 352)
        # 329 條 locator 分佈在 309 個類上：305 條主 locator（offset=cd=0）
        # + 24 條次要 locator（多重繼承的 vfptr，CEF 與 4 個 std 流類）
        self.assertEqual(summary["with_object_locator"], 309)
        self.assertEqual(summary["with_vftable"], 305)
        # 24 條次要 locator → 18 個類、24 張次要虛表（4 個 std 流類只有次要表）
        self.assertEqual(summary["with_secondary_vftable"], 18)
        self.assertEqual(summary["secondary_vftables"], 24)
        self.assertEqual(summary["hierarchy_errors"], [])

    def test_secondary_vftables_are_kept(self):
        # 次要 vfptr 的 COL 帶非零 offset／cd；只收 offset=cd=0 會把整批丟掉
        cef = self.classes[".?AVCefApp@@"]
        self.assertEqual(
            [(item["offset"], item["cd"]) for item in cef["secondary_vftables"]],
            [(8, 0)],
        )
        self.assertTrue(cef["secondary_vftables"][0]["virtual_slots"])

    def test_secondary_only_class_keeps_table_and_writes(self):
        # 只有次要 locator 的類（虛擬基底 → vfptr 帶位移）不能連虛表與錨點一起消失
        stream = self.classes[".?AV?$basic_istream@DU?$char_traits@D@std@@@std@@"]
        self.assertIsNone(stream["vftable_va"])
        self.assertEqual(
            [item["vftable_va"] for item in stream["secondary_vftables"]],
            ["0x797c7c"],
        )
        self.assertTrue(stream["vfptr_writes"])

    def test_vfptr_write_count(self):
        # 完整解 ModRM/SIB/disp 後：307 個類、1,346 處（含次要虛表）。
        # 舊版只認 c7 06 這種無位移形式，得到 292 類 / 919 處，漏掉 400+ 處。
        summary = self.report["summary"]
        self.assertEqual(summary["with_vfptr_writes"], 307)
        self.assertEqual(
            sum(len(c["vfptr_writes"]) for c in self.report["classes"]), 1346
        )

    def test_std_exception_chain_order(self):
        # 這條鏈是 MSVC 的真實繼承，用來證明 BCD 步長 28 與欄位順序解對了
        chain = [b["name"] for b in self.classes[".?AVfailure@ios_base@std@@"]["bases"]]
        self.assertEqual(
            chain,
            [
                ".?AVfailure@ios_base@std@@",
                ".?AVsystem_error@std@@",
                ".?AV_System_error@std@@",
                ".?AVruntime_error@std@@",
                ".?AVexception@std@@",
            ],
        )

    def test_window_class_chain(self):
        chain = [b["name"] for b in self.classes[".?AVCMainWnd@@"]["bases"]]
        self.assertEqual(
            chain, [".?AVCMainWnd@@", ".?AVCCommonWnd@@", ".?AVCGameWnd@@"]
        )

    def test_clzw_write_site_is_instruction_not_immediate(self):
        # notes/mxmain_rtti_class_map.md §5 的「0x4c5d57 處 c7 06」是立即數位址；
        # 指令起始是 0x4c5d55
        writes = self.classes[".?AVCLZWDecompress@@"]["vfptr_writes"]
        pairs = [(w["site_va"], w["imm_va"]) for w in writes]
        self.assertIn(("0x4c5d55", "0x4c5d57"), pairs)

    def test_single_slot_vftable(self):
        # 窗口類別只有虛析構：這一格是 scalar deleting destructor
        common = self.classes[".?AVCCommonWnd@@"]
        self.assertEqual(common["virtual_slots"], ["0x44b2a0"])

    def test_lzw_slot_matches_native_note(self):
        # notes/native_tcp_channel.md 記的 0x4c5e40 是 CLZWDecompress 的第 2 個虛擬槽
        self.assertIn("0x4c5e40", self.classes[".?AVCLZWDecompress@@"]["virtual_slots"])

    def test_aligned_assumption_would_lose_classes(self):
        # 0x5c6085（std 例外的 deleting destructor）是奇數位址：不准對齊假設
        slots = self.classes[".?AVinvalid_argument@std@@"]["virtual_slots"]
        self.assertEqual(slots[0], "0x5c6085")


if __name__ == "__main__":
    sys.exit(unittest.main())
