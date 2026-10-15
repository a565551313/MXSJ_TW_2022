#!/usr/bin/env python3
"""把皮肤 PNG 上的文字标签换成别的写法（繁→简、改词），并可选钉成原文件大小。

为什么要这个：启动器的按钮/页签文字**画在皮肤图里**（`.rsrc` 里那张 PNG），所以
「字是繁体」这件事不用改 exe、也不用碰码页 —— 改图就行。做法是按行取背景主色填掉
旧字（保留渐变，比纯色块自然），再用系统里已有的字体重画新字。

    python3 tools/data-parser/skin_label_patch.py in.png out.png --labels labels.json
    python3 tools/data-parser/skin_label_patch.py in.png out.png --labels labels.json \\
        --pad-to 545162          # 產出與原資源同長度，可直接原位替換 .rsrc 裡的負載

labels.json 是一組長方形：{"text": "进入游戏", "box": [x0, y0, x1, y1],
"size": 22, "fill": "#ffffff", "stroke": "#2b3a7a", "anchor": "mm",
"fill_mode": "median"}；`fill_mode` 可選 mode（众數）/ median（中位，細線多時用這個）/
lerp（兩端插值，漸層按鈕用這個）。
只給 box 起點與寬高亦可，未給 size 時按 box 高度自動推。純函式（row_mode_fill /
pad_png）都有回歸測試。
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None


def row_mode_fill(img, box):
    """用「每行的众数色」填掉矩形裡的舊字（適合平坦底：取众数就不會碰倒漸層）。"""
    x0, y0, x1, y1 = box
    px = img.load()
    for y in range(y0, y1):
        row = [px[x, y][:3] for x in range(x0, x1)]
        fill = Counter(row).most_common(1)[0][0]
        for x in range(x0, x1):
            px[x, y] = fill + (px[x, y][3] if img.mode == "RGBA" else 255,)
    return img


def row_median_fill(img, box):
    """每行取「中位色」填掉舊字：橫向有細線/漸層時比众數穩（众數會被抗鋸齒打散）。"""
    x0, y0, x1, y1 = box
    px = img.load()
    for y in range(y0, y1):
        cols = [px[x, y][:3] for x in range(x0, x1)]
        med = tuple(sorted(c[i] for c in cols)[len(cols) // 2] for i in range(3))
        for x in range(x0, x1):
            px[x, y] = med + (px[x, y][3] if img.mode == "RGBA" else 255,)
    return img


def row_lerp_fill(img, box, probe=6):
    """漸層底專用：取框外左右兩側的背景色，在框裡逐像素線性插值。

    按鈕這類「同一行左右不同色」的底，用众數填會露出一塊平的；兩端插值就看不出來。
    """
    x0, y0, x1, y1 = box
    px = img.load()
    xa = max(0, x0 - probe)
    xb = min(img.width - 1, x1 - 1 + probe)
    for y in range(y0, y1):
        left = px[xa, y][:3]
        right = px[xb, y][:3]
        span = max(1, xb - xa)
        for x in range(x0, x1):  # 以探點為端點插值，框邊才不會出現接不上的階梯
            t = (x - xa) / span
            col = tuple(round(left[c] + (right[c] - left[c]) * t) for c in range(3))
            px[x, y] = col + (px[x, y][3] if img.mode == "RGBA" else 255,)
    return img


IEND_TAIL = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def _chunk(tag: bytes, payload: bytes) -> bytes:
    crc = struct.pack(">I", __import__("zlib").crc32(tag + payload) & 0xFFFFFFFF)
    return struct.pack(">I", len(payload)) + tag + payload + crc


def pad_png(data: bytes, target: int, note: str = "patched") -> bytes:
    """在 IEND 前插一個 tEXt 註釋塊，把 PNG 湊到恰好 target 位元組。"""
    if not data.endswith(IEND_TAIL):
        raise ValueError("不是以 IEND 結尾的 PNG，拒絕改寫")
    if target < len(data):
        raise ValueError(f"目標 {target} 比現有 {len(data)} 還小，湊不出來")
    room = target - len(data)
    block = _chunk(b"tEXt", b"Comment\x00" + note.encode("latin-1", "replace"))
    slack = room - len(block)
    if slack < 0:
        raise ValueError(f"至少需要 {len(block)} 位元組空間才能插入註釋塊")
    payload = b"Comment\x00" + note.encode("latin-1", "replace") + b"\x00" * slack
    block = _chunk(b"tEXt", payload)
    if len(block) != room:  # 收斂一次：slack 演算法的自校驗
        raise ValueError(f"填充算錯：得到 {len(block)}，要 {room}")
    return data[: -len(IEND_TAIL)] + block + IEND_TAIL


def measure_box(img, box, thr=26):
    """在给定窗口里找「跟背景差很多的像素」的外接框 —— 用来对齐旧字的位置。"""
    from statistics import median

    x0, y0, x1, y1 = box
    px = img.load()
    ink = []
    for y in range(y0, y1):
        vals = [sum(px[x, y][:3]) / 3 for x in range(x0, x1)]
        m = median(vals)
        for x, v in enumerate(vals):
            if abs(v - m) > thr:
                ink.append((x0 + x, y))
    if not ink:
        return None
    xs = [p[0] for p in ink]
    ys = [p[1] for p in ink]
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


_FILLERS = {"lerp": row_lerp_fill, "median": row_median_fill}


def apply_labels(img, labels, font_path):
    draw = ImageDraw.Draw(img)
    for lab in labels:
        box = tuple(lab["box"])
        rect = measure_box(img, lab["measure"]) if lab.get("measure") else None
        box = rect or box
        wipe = tuple(lab.get("fill_box") or box)
        if lab.get("fill_rows", True):
            filler = _FILLERS.get(lab.get("fill_mode", "mode"), row_mode_fill)
            filler(img, wipe)
        size = int(lab.get("size") or round((box[3] - box[1]) * 1.05))
        font = ImageFont.truetype(font_path, size)
        # 以框的中心放字；填過之後框裡就是乾淨背景，不會再被舊字帶偏
        cx = (box[0] + box[2]) // 2
        cy = (box[1] + box[3]) // 2
        draw.text(
            (cx, cy),
            lab["text"],
            font=font,
            fill=lab.get("fill", "#ffffff"),
            stroke_width=int(lab.get("stroke_width", 1)),
            stroke_fill=lab.get("stroke"),
            anchor=lab.get("anchor", "mm"),
        )
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--pad-to", type=int, default=None)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()

    if Image is None:
        print("[!] 需要 Pillow：pip install pillow", file=sys.stderr)
        return 2
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    src = Image.open(args.src)
    has_alpha = src.mode == "RGBA"
    img = src.convert("RGBA" if has_alpha else "RGB")
    apply_labels(img, labels, str(args.font))
    img.save(args.dst, "PNG", optimize=True)
    data = args.dst.read_bytes()
    note = {
        "kind": "skin_label_patch",
        "src": str(args.src),
        "dst": str(args.dst),
        "labels": [lab["text"] for lab in labels],
        "bytes_before": len(data),
    }
    if args.pad_to:
        data = pad_png(data, args.pad_to, note="mxsj skin label patch")
        args.dst.write_bytes(data)
        note["bytes_after_pad"] = len(data)
    if args.report:
        args.report.write_text(
            json.dumps(note, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    print(f"[+] {args.src.name} -> {args.dst}（{len(data)} B，標籤 {len(labels)} 個）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
