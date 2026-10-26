#!/usr/bin/env python3
"""mxmain_rtti 的回歸測試。

兩種樣本：自己蓋的最小 PE（鎖住欄位順序與步長），以及倉庫根的 `mxmain.dll`
（鎖住實測數字與幾個已知答案：std 例外五層鏈、`CMainWnd` 三層繼承、
`CCommonWnd` 只有一個虛表槽、`CLZWDecompress` 的第 2 槽等於
`notes/native_tcp_channel.md` 記的 0x4c5e40）。
"""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
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
    rdata[0x400:0x408] = struct.pack("<II", COL_BAR, FUNC_C)
    # 虛表後面接字串：0x696969（"ii"）落在 .text 範圍內，必須被擋掉
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

    def test_trailing_string_blob_is_not_a_slot(self):
        # 0x696969 落在 .text 內，是 "ii" 字串被讀成指標；必須在它前面停住
        bar = self.classes[".?AVCBar@@"]
        self.assertEqual(bar["virtual_slots"], [hex(FUNC_C)])

    def test_hierarchy_is_self_then_base(self):
        bar = self.classes[".?AVCBar@@"]
        names = [b["name"] for b in bar["bases"]]
        self.assertEqual(names, [".?AVCBar@@", ".?AVCFoo@@"])
        self.assertEqual(bar["bases"][1]["mdisp"], 0)

    def test_vfptr_write_site(self):
        foo = self.classes[".?AVCFoo@@"]
        sites = [int(s["site_va"], 16) for s in foo["vfptr_writes"]]
        self.assertIn(CTOR_FOO + 5, sites)  # 55 8b ec | c7 06 | imm32

    def test_summary_counts(self):
        summary = self.report["summary"]
        self.assertEqual(summary["with_object_locator"], 2)
        self.assertEqual(summary["with_vftable"], 2)
        self.assertEqual(summary["vftable_slot_counts"], {"1": 1, "2": 1})
        self.assertEqual(summary["hierarchy_errors"], [])

    def test_input_is_never_touched(self):
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        mrtti.build_report(self.path)
        self.assertEqual(before, hashlib.sha256(self.path.read_bytes()).hexdigest())


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
        self.assertEqual(summary["with_object_locator"], 305)
        self.assertEqual(summary["with_vftable"], 305)
        self.assertEqual(summary["hierarchy_errors"], [])

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
