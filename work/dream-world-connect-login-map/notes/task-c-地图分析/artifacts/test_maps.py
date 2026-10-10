#!/usr/bin/env python3
"""Re-run format invariants, offset cross-checks and negative tests without game file writes."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "work/dream-world-connect-login-map/tools"))
from map_parser import MapFormatError, parse_map, parse_map_bytes
from map_viewer import build_grid, render_ascii, render_svg, render_image_overlay, probe_cell
from gepj_decoder import ImageDecodeError, unpack_gepj, decode_jpeg, write_rgb_png
from analyze_records import analyze
from analyze_llec_pixels import analyze as compare_pixels
import shutil
import tempfile


class MapTests(unittest.TestCase):
    def test_all_samples(self):
        for p in sorted((ROOT / "map").glob("*.map")):
            with self.subTest(p=p.name):
                doc = parse_map(p)
                self.assertEqual(len(doc["sectors"]), 49)
                self.assertEqual(sum(doc["cell_value_counts"].values()), 49 * 192)
                self.assertEqual(doc["header"]["width"], 2000)
                self.assertEqual(doc["header"]["height"], 1500)
                self.assertEqual(len(doc["prefix_records"]), 32 if p.stem == "2303" else 0)
                data = p.read_bytes()
                for s in doc["sectors"]:
                    at = s["cell_offset"]
                    self.assertEqual(s["cells"], list(data[at:at + 192]))
                grid = build_grid(doc)
                self.assertEqual((len(grid), len(grid[0])), (84, 112))
                self.assertIn("<svg", render_svg(doc))
                self.assertIn("raw LLEC", render_ascii(doc))
        doc = parse_map(ROOT / "map/2303.map")
        self.assertEqual({ref for s in doc["sectors"] for ref in s["record_references"]}, set(range(32)))
        self.assertIn('record 0', render_svg(doc, overlay_records=True))
        check = analyze(ROOT / "map/2303.map")
        self.assertTrue(check["all_lengths_match"])
        self.assertTrue(check["all_references_match"])
        self.assertEqual(check["reference_total"], 61)

    def test_in_bounds_llec_nonbinary_only_2(self):
        for path in sorted((ROOT / "map").glob("*.map")):
            doc = parse_map(path)
            special = []
            for sector in doc["sectors"]:
                for j, value in enumerate(sector["cells"]):
                    x = sector["index"] % 7 * 320 + j % 16 * 20
                    y = sector["index"] // 7 * 240 + j // 16 * 20
                    if x < 2000 and y < 1500 and value not in (0, 1):
                        special.append(value)
            self.assertGreater(len(special), 0)
            self.assertEqual(set(special), {2})

    def test_probe_raw_llec(self):
        doc = parse_map(ROOT / "map/2111.map")
        self.assertEqual(probe_cell(doc, 705, 984)["raw_llec_byte"], 2)
        with self.assertRaises(ValueError):
            probe_cell(doc, 2000, 100)

    def test_llec_pixel_correlation(self):
        path = ROOT / "map/2111.map"
        png = ROOT / "work/dream-world-connect-login-map/tools/map-textures/2111.png"
        if not png.exists():
            self.skipTest("run gepj_decoder.py first to generate comparison PNG")
        result = compare_pixels(path, png)["groups"]
        self.assertLess(result["0"]["black_pixels"] / result["0"]["pixels_sampled"], 0.01)
        self.assertGreater(result["1"]["black_pixels"] / result["1"]["pixels_sampled"], 0.7)

    def test_gepj_segments_all_five_maps(self):
        for path in sorted((ROOT / "map").glob("*.map")):
            doc = parse_map(path)
            with path.open("rb") as src:
                for sector in doc["sectors"]:
                    img = sector["image"]
                    src.seek(img["offset"])
                    payload = src.read(img["length"])
                    with self.subTest(file=path.name, sector=sector["index"]):
                        header, jpeg_parts = unpack_gepj(payload, img["segment_lengths_u16_le"])
                        self.assertEqual(len(jpeg_parts), 12)
                        self.assertTrue(all(jpeg.startswith(b"\xff\xd8\xff\xc0") and jpeg.endswith(b"\xff\xd9")
                                            for jpeg in jpeg_parts))
        if shutil.which("convert"):
            path = ROOT / "map/2111.map"
            doc = parse_map(path)
            img = doc["sectors"][16]["image"]
            with path.open("rb") as src:
                src.seek(img["offset"])
                payload = src.read(img["length"])
            _, pieces = unpack_gepj(payload, img["segment_lengths_u16_le"])
            rgb = decode_jpeg(pieces[6])
            self.assertEqual(len(rgb), 80 * 80 * 3)
            self.assertGreater(len(set(rgb)), 100)

    def test_gepj_reject_bad_segment_and_png(self):
        path = ROOT / "map/2101.map"
        doc = parse_map(path)
        img = doc["sectors"][0]["image"]
        with path.open("rb") as src:
            src.seek(img["offset"])
            payload = src.read(img["length"])
        sizes = img["segment_lengths_u16_le"].copy()
        sizes[1] += 1
        with self.assertRaises(ImageDecodeError):
            unpack_gepj(payload, sizes)
        with tempfile.TemporaryDirectory() as tmp:
            png_path = Path(tmp) / "tiny.png"
            write_rgb_png(png_path, 1, 1, bytes([12, 34, 56]))
            self.assertEqual(png_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            with self.assertRaises(ValueError):
                render_image_overlay(doc, png_path.read_bytes())

    def test_bad_magic(self):
        data = bytearray((ROOT / "map/2101.map").read_bytes())
        data[0] = 0
        with self.assertRaises(MapFormatError):
            parse_map_bytes(data)

    def test_bad_offset(self):
        data = bytearray((ROOT / "map/2101.map").read_bytes())
        data[12:16] = (999999).to_bytes(4, "little")
        with self.assertRaises(MapFormatError):
            parse_map_bytes(data)

    def test_bad_section_size(self):
        data = bytearray((ROOT / "map/2101.map").read_bytes())
        first = int.from_bytes(data[12:16], "little")
        data[first+8:first+12] = (1218).to_bytes(4, "little")
        with self.assertRaises(MapFormatError):
            parse_map_bytes(data)

    def test_truncation(self):
        data = (ROOT / "map/2101.map").read_bytes()
        with self.assertRaises(MapFormatError):
            parse_map_bytes(data[:-8])

    def test_bad_record_length(self):
        data = bytearray((ROOT / "map/2303.map").read_bytes())
        first_record = int.from_bytes(data[216:220], "little")
        data[first_record+16:first_record+20] = (10_000).to_bytes(4, "little")
        with self.assertRaises(MapFormatError):
            parse_map_bytes(data)


if __name__ == "__main__":
    unittest.main()
