#!/usr/bin/env python3
"""皮膚改字 + 資源原位寫回這支工具的回归测试。

关注三件容易做错的事：① 填充要「只盖掉字、不破坏渐变/细线」；② 湊 PNG 長度只能在
IEND 前插塊、不能重壓（重壓會改字節數 → 沒法原位替換）；③ 寫回 `.rsrc` 必須長度一致，
長度不一致要直接拒絕，不能偷偷改節表。
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(HERE / f"{name}.py"))
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


slp = load("skin_label_patch")
prp = load("pe_resource_patch")

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def fake_png(extra: int = 0) -> bytes:
    """湊一個「看起來像 PNG」的位元組串（有 IHDR/IEND），專門測 pad_png 的邊界。"""
    ihdr = struct.pack(">IIBBBBB", 4, 4, 8, 6, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x80" * 16 for _ in range(4))
    idat = zlib.compress(raw)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(
            ">I", zlib.crc32(tag + payload) & 0xFFFFFFFF
        )

    pad = chunk(b"tEXt", b"Comment\x00" + b"x" * extra) if extra else b""
    head = chunk(b"IHDR", ihdr)
    body = chunk(b"IDAT", idat)
    return b"\x89PNG\r\n\x1a\n" + head + pad + body + IEND


class PadPngTests(unittest.TestCase):
    def test_pads_to_exact_size(self):
        src = fake_png()
        target = len(src) + 300
        out = slp.pad_png(src, target)
        self.assertEqual(len(out), target)
        self.assertTrue(out.endswith(IEND))
        self.assertTrue(out.startswith(b"\x89PNG\r\n\x1a\n"))
        # 原有的 IHDR/IDAT 一個位元組都不能動
        i = src.index(b"IDAT")
        self.assertIn(src[i : i + 8], out)  # 原有區塊原封不動

    def test_rejects_when_too_small_or_not_png(self):
        src = fake_png(extra=500)
        with self.assertRaises(ValueError):
            slp.pad_png(src, len(src) - 10)
        with self.assertRaises(ValueError):
            slp.pad_png(b"BM\x00" * 40, 5000)

    def test_rejects_when_no_room_for_chunk(self):
        src = fake_png()
        with self.assertRaises(ValueError):
            slp.pad_png(src, len(src) + 3)


@unittest.skipIf(Image is None, "需要 Pillow")
class FillTests(unittest.TestCase):
    def test_row_mode_and_median_erase_text(self):
        img = Image.new("RGB", (40, 10), (200, 200, 200))
        px = img.load()
        for x in range(12, 27):  # 「舊字」只占每行的一小段，背景仍是多数
            for y in range(3, 7):
                px[x, y] = (10, 10, 10)
        for fill in (slp.row_mode_fill, slp.row_median_fill):
            work = img.copy()
            fill(work, (5, 0, 35, 10))
            out = work.load()
            seen = {out[x, y] for y in range(10) for x in range(5, 35)}
            self.assertEqual(seen, {(200, 200, 200)}, f"{fill.__name__} 沒擦乾淨")

    def test_lerp_keeps_horizontal_gradient(self):
        img = Image.new("RGB", (60, 6))
        px = img.load()
        for y in range(6):
            for x in range(60):
                px[x, y] = (x * 4, 10, 0)  # 橫向漸層
            for x in range(20, 40):
                px[x, y] = (255, 255, 255)  # 舊字
        slp.row_lerp_fill(img, (20, 0, 40, 6), probe=6)
        out = img.load()
        for y in range(6):
            vals = [out[x, y][0] for x in range(14, 46)]
            # 框裡要平滑（與框外漸層接得上，不能有階梯）
            self.assertEqual(vals, sorted(vals), f"第 {y} 行不單調")
            self.assertEqual([out[19, y][0], out[20, y][0]], [76, 80])
            self.assertEqual([out[39, y][0], out[40, y][0]], [156, 160])

    def test_apply_labels_uses_fill_box(self):
        img = Image.new("RGB", (60, 30), (200, 200, 200))
        px = img.load()
        for x in range(5, 55, 3):  # 像筆畫一樣稀疏散布的舊字
            for y in range(5, 25):
                px[x, y] = (0, 0, 0)
        labels = [
            {"text": "新", "box": [20, 8, 40, 22], "size": 12,
             "fill_box": [5, 5, 55, 25]}
        ]
        font = Path(__file__).resolve().parents[2] / "Fonts" / "simhei.ttf"
        if not font.exists():
            self.skipTest("客戶端目錄沒有可用的 ttf")
        slp.apply_labels(img, labels, str(font))
        out = img.load()
        self.assertEqual(out[8, 6], (200, 200, 200))  # fill_box 裡的舊字被擦掉
        self.assertTrue(
            any(
                out[x, y] != (200, 200, 200)
                for x in range(20, 40)
                for y in range(8, 22)
            ),
            "新字沒画上：框內仍是純背景",
        )


class SpliceTests(unittest.TestCase):
    def test_length_mismatch_is_refused(self):
        data = bytearray(b"\x00" * 100)
        with self.assertRaises(ValueError):
            prp.splice(bytes(data), 10, b"\xff" * 5, 8)

    def test_same_length_swap_only_touches_payload(self):
        data = b"A" * 20 + b"B" * 10 + b"C" * 20
        out = prp.splice(data, 20, b"X" * 10, 10)
        self.assertEqual(out, b"A" * 20 + b"X" * 10 + b"C" * 20)


@unittest.skipUnless((HERE.parents[1] / "mxLauncher.exe").exists(), "需要客戶端目錄")
class RealLauncherPatchTests(unittest.TestCase):
    SRC = HERE.parents[1] / "mxLauncher.exe"

    def test_finds_the_skin_png(self):
        info = prp.find_payload(self.SRC.read_bytes(), "PNG", "1")
        self.assertEqual(info["size"], 545162)
        self.assertEqual(info["lang"], 2052)
        self.assertEqual(len(info["sha256"]), 64)

    def test_missing_resource_raises(self):
        with self.assertRaises(LookupError):
            prp.find_payload(self.SRC.read_bytes(), "PNG", "9999")

    def test_patch_is_verifiable_and_reversible(self):
        data = self.SRC.read_bytes()
        info = prp.find_payload(data, "PNG", "1")
        payload = data[info["offset"] : info["offset"] + info["size"]]
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "out.exe"
            report = prp.patch(self.SRC, dst, payload, "PNG", "1")
            # 拿原載荷寫回去，整個檔案必須逐位元組相同
            self.assertEqual(report["src_sha256"], report["dst_sha256"])
            # 換一張「同長度」的圖進去，再讀出來都必須是新圖（這就是原位替換的閉環）
            swapped = slp.pad_png(fake_png(), len(payload))
            dst2 = Path(tmp) / "out2.exe"
            prp.patch(self.SRC, dst2, swapped, "PNG", "1")
            info = prp.find_payload(dst2.read_bytes(), "PNG", "1")
            info2 = prp.find_payload(dst2.read_bytes(), "PNG", "1")
            blob = dst2.read_bytes()
            lo, hi = info2["offset"], info2["offset"] + info2["size"]
            got = blob[lo:hi]
            self.assertEqual(got, swapped)

    def test_wrong_length_is_refused_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "out.exe"
            with self.assertRaises(ValueError):
                prp.patch(self.SRC, dst, b"too short", "PNG", "1")
            self.assertFalse(dst.exists())  # 拒絕時不能留半成品


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=2))
