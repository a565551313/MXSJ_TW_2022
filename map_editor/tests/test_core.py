"""Core format-engine tests.

Run from the project root:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

Sample maps come from ``MXSJ_MAP_SAMPLES`` (default ``../MXSJ_TW_2022/map``).
Tests that need real maps are skipped when the samples are absent, so the suite
still passes on a clean checkout.
"""
from __future__ import annotations

import math
import os
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import SAMPLES, reference_png_dir          # noqa: E402

from map_editor.core import (                     # noqa: E402
    GepjError, MapDocument, MapFormatError, decode_sector_image, open_map, render_full,
    render_region, sniff,
)
from map_editor.core.mapfile import (             # noqa: E402
    CELLS_PER_SECTOR, detect_sector_count, read_header,
)

def sample_maps() -> list[Path]:
    if not SAMPLES.is_dir():
        return []
    return sorted(p for p in SAMPLES.glob("*.map") if sniff(p))


def needs_samples(fn):
    return unittest.skipUnless(sample_maps(), f"no sample maps under {SAMPLES}")(fn)


class TestSectorCountDerivation(unittest.TestCase):
    """The sector count must be derived, never hardcoded (real maps have 25..800)."""

    def _build(self, n: int, width: int, height: int, records: int = 0) -> bytes:
        """Synthesise a minimal valid header: N offsets + self-pointer + records."""
        header = bytearray(b"0.1M" + struct.pack("<II", width, height))
        first_data = 12 + 4 * n + 4 + 4 + 4 * records
        # Offsets must be strictly increasing; pad them past the header.
        for i in range(n):
            header += struct.pack("<I", first_data + i * 200)
        header += struct.pack("<I", 12 + 4 * n + 4)      # self-referential sentinel
        header += struct.pack("<I", records)
        return bytes(header)

    def test_derives_various_sector_counts(self) -> None:
        import io
        for n, w, h in ((49, 2000, 1500), (100, 3200, 2400), (800, 10000, 6000),
                        (25, 1600, 1200), (30, 1588, 1220)):
            with self.subTest(sectors=n):
                data = self._build(n, w, h)
                fh = io.BytesIO(data)
                self.assertEqual(detect_sector_count(fh, len(data)), n)

    def test_rejects_non_map(self) -> None:
        import io
        with self.assertRaises(MapFormatError):
            read_header(io.BytesIO(b"NOPE" + b"\x00" * 512), 516)


@needs_samples
class TestParseAllSamples(unittest.TestCase):
    def test_all_samples_parse_and_self_check(self) -> None:
        maps = sample_maps()
        self.assertGreaterEqual(len(maps), 5)
        for path in maps:
            with self.subTest(map=path.name):
                with open_map(path) as doc:
                    h = doc.header
                    self.assertEqual(h.sector_count,
                                     math.ceil(h.width / 320) * math.ceil(h.height / 240))
                    # Forces every sector through the tag + length-identity checks.
                    for s in doc.iter_sectors():
                        self.assertEqual(len(doc.read_cells(s)), CELLS_PER_SECTOR)
                        self.assertEqual(len(s.girb_body), 22)

    def test_girb_is_constant_across_all_sectors(self) -> None:
        seen: set[bytes] = set()
        for path in sample_maps():
            with open_map(path) as doc:
                for s in doc.iter_sectors():
                    seen.add(s.girb_body + s.girb_trailer)
        self.assertEqual(len(seen), 1, f"GIRB bodies differ: {seen}")

    def test_cell_lookup_matches_sector_bytes(self) -> None:
        with open_map(sample_maps()[0]) as doc:
            h = doc.header
            for px, py in ((0, 0), (19, 19), (20, 20), (h.width - 1, h.height - 1)):
                expected = doc.read_cells(doc.sector(
                    (py // 20 // 12) * h.sector_columns + (px // 20 // 16)
                ))[(py // 20 % 12) * 16 + (px // 20 % 16)]
                self.assertEqual(doc.cell_at(px, py), expected, f"cell at {px},{py}")
            self.assertIsNone(doc.cell_at(-1, 0))
            self.assertIsNone(doc.cell_at(h.width, 0))


@needs_samples
class TestGepjDecoder(unittest.TestCase):
    def test_sector_image_dimensions(self) -> None:
        with open_map(sample_maps()[0]) as doc:
            s = doc.sector(0)
            img = decode_sector_image(doc.read_image_payload(s), s.segment_lengths)
            self.assertEqual((img.width, img.height), (320, 240))

    def test_bad_payload_rejected(self) -> None:
        with open_map(sample_maps()[0]) as doc:
            s = doc.sector(0)
            with self.assertRaises(GepjError):
                decode_sector_image(b"\x00" * 40, s.segment_lengths)

    def test_pillow_matches_reference_png(self) -> None:
        """Prove the Pillow path reproduces the ImageMagick-produced reference."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        ref_dir = reference_png_dir()
        if ref_dir is None:
            self.skipTest("no reference PNG directory found")
        checked = 0
        for path in sample_maps():
            ref = ref_dir / f"{path.stem}.png"
            if not ref.is_file():
                continue
            with self.subTest(map=path.name), Image.open(ref) as im, open_map(path) as doc:
                expected = im.convert("RGB")
                got = render_full(doc)
                self.assertEqual((got.width, got.height), expected.size)
                self.assertEqual(got.data, expected.tobytes(),
                                 f"{path.name}: Pillow decode differs from ImageMagick reference")
            checked += 1
        self.assertGreater(checked, 0, "no reference PNG matched a sample map")


@needs_samples
class TestRegionRendering(unittest.TestCase):
    """Region rendering must equal the same crop of a full render (UI relies on it)."""

    def test_region_equals_crop_of_full(self) -> None:
        path = sample_maps()[0]
        with open_map(path) as doc:
            full = render_full(doc)
            for box in ((0, 0, 100, 80), (319, 239, 400, 300), (1500, 1200, 2000, 1500)):
                with self.subTest(box=box):
                    x0, y0, x1, y1 = box
                    region = render_region(doc, x0, y0, x1, y1)
                    w = full.width
                    expect = bytearray()
                    for y in range(y0, y1):
                        src = (y * w + x0) * 3
                        expect += full.data[src:src + (x1 - x0) * 3]
                    self.assertEqual(region.data, bytes(expect))

    def test_region_outside_map_rejected(self) -> None:
        with open_map(sample_maps()[0]) as doc:
            with self.assertRaises(GepjError):
                render_region(doc, 5000, 5000, 6000, 6000)

    def test_region_touching_only_one_sector_decodes_one_sector(self) -> None:
        """Performance contract: a small viewport must not decode all 49 sectors."""
        path = sample_maps()[0]
        with open_map(path) as doc:
            render_region(doc, 10, 10, 60, 60)
            self.assertEqual(len(doc._sectors), 1,
                             "a 50x50 region should touch exactly one sector")


if __name__ == "__main__":
    unittest.main(verbosity=2)
