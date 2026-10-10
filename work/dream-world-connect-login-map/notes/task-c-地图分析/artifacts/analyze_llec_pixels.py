#!/usr/bin/env python3
"""Offline comparison of raw LLEC values with recovered PNG brightness.

This establishes image correlation only, not runtime collision semantics.
Reads the PNGs produced by gepj_decoder.py (RGB, filter type 0).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "work/dream-world-connect-login-map/tools"))
from map_parser import parse_map


def png_rgb(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not PNG")
    pos = 8
    idat = bytearray()
    width = height = 0
    while pos < len(data):
        size = struct.unpack_from(">I", data, pos)[0]
        tag = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + size]
        crc = struct.unpack_from(">I", data, pos + 8 + size)[0]
        if zlib.crc32(tag + payload) != crc:
            raise ValueError("PNG CRC mismatch")
        if tag == b"IHDR":
            width, height, bits, color, _, _, _ = struct.unpack(">IIBBBBB", payload)
            if (bits, color) != (8, 2):
                raise ValueError("need 8-bit RGB PNG")
        if tag == b"IDAT":
            idat.extend(payload)
        pos += size + 12
        if tag == b"IEND":
            break
    decompressed = zlib.decompress(idat)
    row_size = width * 3
    if len(decompressed) != (row_size + 1) * height:
        raise ValueError("bad PNG dimensions")
    rgb = bytearray()
    for y in range(height):
        row = decompressed[y * (row_size + 1):(y + 1) * (row_size + 1)]
        if row[0] != 0:
            raise ValueError("need unfiltered PNG from own decoder")
        rgb.extend(row[1:])
    return width, height, bytes(rgb)


def analyze(map_path: Path, image_path: Path) -> dict:
    doc = parse_map(map_path)
    width, height, rgb = png_rgb(image_path)
    if (width, height) != (doc["header"]["width"], doc["header"]["height"]):
        raise ValueError("map and image dimensions mismatch")
    stat = defaultdict(lambda: {"cells": 0, "pixels_sampled": 0, "black_pixels": 0, "bright_pixels": 0})
    special = []
    # 20px cell, sample 4x4 interior pixels per cell, avoid border aliasing.
    for sector in doc["sectors"]:
        for j, value in enumerate(sector["cells"]):
            x = (sector["index"] % 7) * 320 + (j % 16) * 20
            y = (sector["index"] // 7) * 240 + (j // 16) * 20
            if x >= width or y >= height:
                continue
            group = str(value) if value in (0, 1) else "other"
            if value not in (0, 1):
                special.append({"x": x, "y": y, "raw_value": value})
            entry = stat[group]
            entry["cells"] += 1
            for yy in (3, 8, 13, 18):
                for xx in (3, 8, 13, 18):
                    if x + xx >= width or y + yy >= height:
                        continue
                    k = ((y + yy) * width + x + xx) * 3
                    level = max(rgb[k:k+3])
                    entry["pixels_sampled"] += 1
                    entry["black_pixels"] += level < 16
                    entry["bright_pixels"] += level >= 64
    return {"map": map_path.name, "source_png": image_path.name, "groups": dict(stat),
            "nonbinary_in_bounds": special}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    mroot = args.root / "map"
    proot = args.root / "work/dream-world-connect-login-map/tools/map-textures"
    results = []
    for path in sorted(mroot.glob("*.map")):
        png = proot / (path.stem + ".png")
        result = analyze(path, png)
        results.append(result)
        print(path.name, {k: (s["cells"], round(s["black_pixels"] / s["pixels_sampled"], 4))
                              for k, s in result["groups"].items()})
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
