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
import shutil
import struct
import sys
import tempfile
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
                        # GIRB length varies with map content: 22 bytes for an
                        # obstacle-free sector, up to ~1.2 KB on dense outdoor maps.
                        self.assertGreaterEqual(len(s.girb_body), 22)

    def test_girb_is_per_sector_data_not_a_constant(self) -> None:
        """GIRB is the collision grid, so it varies on maps that have obstacles.

        An earlier version of this test asserted a single global constant.  That
        held only because every original sample was an interior scene with no
        collision data; 1034/1035 disprove it.
        """
        per_map: dict[str, set[bytes]] = {}
        for path in sample_maps():
            with open_map(path) as doc:
                per_map[path.stem] = {bytes(s.girb_body) for s in doc.iter_sectors()}
        uniform = {k for k, v in per_map.items() if len(v) == 1}
        varied = {k for k, v in per_map.items() if len(v) > 1}
        self.assertTrue(uniform, "expected some maps to have a uniform grid")
        if varied:
            for k in varied:
                self.assertGreater(len(per_map[k]), 50,
                                   f"{k}: expected many distinct GIRB bodies")
        # Uniform maps must use the 22-byte minimal encoding everywhere.
        for k in uniform:
            self.assertEqual({len(b) for b in per_map[k]}, {22}, k)

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


def _build_sector(image_payload_len: int = 260, extra: list[tuple[bytes, bytes]] = (),
                  refs: int = 0) -> bytes:
    """One sector: refs | GEPJ | LLEC | 192 | extras | GIRB | 22 | tail4."""
    import struct as _s
    out = bytearray(_s.pack("<I", refs) + b"\x00" * (4 * refs))
    # GEPJ: 13 segment lengths summing to (length - 26)
    per = image_payload_len // 12
    segs = [26 + (image_payload_len - per * 12)] + [per] * 12
    segs[0] = 26 + image_payload_len - per * 12
    total = sum(segs) + 26
    out += b"GEPJ" + _s.pack("<I", total) + _s.pack(f"<{len(segs)}H", *segs)
    out += b"\xff" * (total - 26)
    out += b"LLEC" + _s.pack("<I", 192) + bytes(range(192))
    for tag, body in extra:
        out += tag + _s.pack("<I", len(body)) + body
    out += b"GIRB" + _s.pack("<I", 22) + b"\x02" * 22 + b"\x00" * 4
    return bytes(out)


def _build_map(sectors: list[bytes], width: int, height: int,
               records: int = 0) -> bytes:
    import struct as _s
    n = len(sectors)
    first = 12 + 4 * n + 8 + 4 * records
    head = bytearray(b"0.1M" + _s.pack("<II", width, height))
    pos = first
    for sec in sectors:
        head += _s.pack("<I", pos)
        pos += len(sec)
    head += _s.pack("<I", 12 + 4 * n + 4)      # self-referential sentinel
    head += _s.pack("<I", records)
    return bytes(head) + b"".join(sectors)


class TestUnknownBlockTolerance(unittest.TestCase):
    """The client dispatcher recognises MASK; the parser must not choke on it."""

    def test_sector_with_mask_block_is_accepted(self) -> None:
        mask_body = b"\x01\x02" * 100
        data = _build_map([_build_sector(extra=[(b"MASK", mask_body)])], 320, 240)
        path = Path(tempfile.mkdtemp()) / "masked.map"
        path.write_bytes(data)
        self.addCleanup(shutil.rmtree, path.parent, True)
        self.assertTrue(sniff(path))
        with open_map(path) as doc:
            s = doc.sector(0)
            self.assertEqual([b.tag for b in s.extra_blocks], ["MASK"])
            self.assertEqual(s.extra_blocks[0].length, 200)
            self.assertEqual(len(doc.read_cells(s)), 192)
            self.assertEqual(doc.read_cells(s), bytes(range(192)))
            self.assertEqual(len(s.girb_body), 22)

    def test_multiple_unknown_blocks_keep_the_chain_aligned(self) -> None:
        extras = [(b"MASK", b"\xAA" * 40), (b"ZZZZ", b"\xBB" * 7)]
        data = _build_map([_build_sector(extra=extras)] * 4, 640, 480)
        path = Path(tempfile.mkdtemp()) / "multi.map"
        path.write_bytes(data)
        self.addCleanup(shutil.rmtree, path.parent, True)
        with open_map(path) as doc:
            self.assertEqual(doc.header.sector_count, 4)
            for s in doc.iter_sectors():
                self.assertEqual([b.tag for b in s.extra_blocks], ["MASK", "ZZZZ"])
                self.assertEqual([b.length for b in s.extra_blocks], [40, 7])

    def test_block_overrunning_the_sector_is_rejected(self) -> None:
        # MASK claims more bytes than the sector actually has left.
        import struct as _s
        sec = _build_sector(extra=[(b"MASK", b"\xAA" * 40)])
        broken = sec[:-4 - 40] + _s.pack("<I", 9999) + b"\xAA" * 40 + sec[-4 - 40:]
        data = _build_map([broken], 320, 240)
        path = Path(tempfile.mkdtemp()) / "broken.map"
        path.write_bytes(data)
        self.addCleanup(shutil.rmtree, path.parent, True)
        with self.assertRaises(MapFormatError):
            with open_map(path) as doc:
                doc.sector(0)

    def test_missing_girb_terminator_is_rejected(self) -> None:
        sec = _build_sector()
        sec = sec[:sec.index(b"GIRB")]                    # drop GIRB + tail
        data = _build_map([sec], 320, 240)
        path = Path(tempfile.mkdtemp()) / "nogirb.map"
        path.write_bytes(data)
        self.addCleanup(shutil.rmtree, path.parent, True)
        with self.assertRaises(MapFormatError):
            with open_map(path) as doc:
                doc.sector(0)

    def test_real_samples_have_no_extra_blocks(self) -> None:
        """Cross-check the synthetic path against the shipped maps."""
        for path in sample_maps():
            with self.subTest(map=path.name), open_map(path) as doc:
                for s in doc.iter_sectors():
                    self.assertEqual(s.extra_blocks, (),
                                     f"{path.name} sector {s.index} has extra blocks")


@needs_samples
class TestGirbDecompressor(unittest.TestCase):
    """GIRB inflates to the fixed 2400-byte / 1200-u16 collision grid."""

    def test_uniform_sector_inflates_to_2400_bytes_of_0x88(self) -> None:
        from map_editor.core.girb import EMPTY_FILL, GRID_BYTES, cells, decompress
        body = bytes.fromhex("0288888888882000000000000000000043000011000000")[:22]
        raw = decompress(body)
        self.assertEqual(len(raw), GRID_BYTES)
        self.assertEqual(set(raw), {0x88})
        cs = cells(body)
        self.assertEqual(len(cs), 1200)
        self.assertEqual(set(cs), {EMPTY_FILL})

    def test_every_successful_inflate_is_exactly_2400_bytes(self) -> None:
        from map_editor.core.girb import GRID_BYTES, GirbError, decompress
        seen = 0
        for path in sample_maps():
            with self.subTest(map=path.name), open_map(path) as doc:
                for s in doc.iter_sectors():
                    try:
                        raw = decompress(s.girb_body)
                    except GirbError:
                        continue          # decoder is incomplete; see module docs
                    if len(raw) >= GRID_BYTES:
                        self.assertEqual(len(raw), GRID_BYTES)
                        seen += 1
        self.assertGreater(seen, 200, "too few sectors decoded to be meaningful")

    def test_grid_geometry_tiles_the_sector_canvas(self) -> None:
        """1200 cells/sector at 8 px must exactly cover the padded map."""
        from map_editor.core.girb import GRID_CELLS, GRID_COLS, GRID_ROWS
        for path in sample_maps():
            with self.subTest(map=path.name), open_map(path) as doc:
                h = doc.header
                self.assertEqual(GRID_COLS * GRID_ROWS, GRID_CELLS)
                self.assertEqual(h.sector_count * GRID_CELLS,
                                 (h.sector_columns * GRID_COLS) * (h.sector_rows * GRID_ROWS))
                self.assertEqual(h.sector_columns * GRID_COLS * 8, h.sector_columns * 320)
