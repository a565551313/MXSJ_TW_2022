"""Comprehensive tests for full map-editor read/edit/compile/save/audit features
and full 101-map corpus verification when the external Google Drive corpus is
available."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from map_editor.cli import main
from map_editor.client.config import Config
from map_editor.client.scene_table import SceneTable
from map_editor.core import (
    GepjError,
    PrefixRecord,
    apply_blk_to_map,
    client_px_to_server_cell,
    compress,
    compute_sector_record_refs,
    create_map_file,
    decode_mask_record,
    decompress,
    deflate_lzo1x,
    encode_mask_payload,
    extract_blk_from_map,
    find_path,
    inflate_lzo1x,
    open_map,
    pack_nibbles,
    read_blk,
    render_region,
    server_cell_to_client_px,
    unpack_nibbles,
    write_blk,
)
from map_editor.ui.viewmodel import EditorViewModel, ExportBlockedError

REPO = Path(__file__).resolve().parents[2]
SAMPLES = REPO / "map"
DRIVE_CORPUS = Path(
    os.environ.get(
        "MXSJ_MAP_CORPUS",
        str(Path(tempfile.gettempdir()) / "mxsj_map" / "extracted"),
    )
)


class TestLzo1xAndGirbRoundTrip(unittest.TestCase):
    def test_lzo1x_roundtrip_varied_payloads(self) -> None:
        payloads = [
            b"",
            b"A",
            b"ABCDEFG",
            b"\x88" * 2400,
            bytes((i * 37 + (i // 19)) & 0xFF for i in range(2400)),
            (b"\x55\xaa\x00\xff" * 900) + b"TAIL!",
        ]
        for orig in payloads:
            comp = deflate_lzo1x(orig)
            self.assertEqual(inflate_lzo1x(comp), orig)

    def test_girb_4bit_nibble_pack_unpack_roundtrip(self) -> None:
        nibbles = [(x + y * 3) & 0xF for y in range(60) for x in range(80)]
        packed = pack_nibbles(nibbles)
        comp = compress(packed)
        raw = decompress(comp)
        self.assertEqual(len(raw), 2400)
        self.assertEqual(list(unpack_nibbles(raw)), nibbles)

    def test_all_shipped_samples_serialize_byte_for_byte(self) -> None:
        if not SAMPLES.is_dir():
            self.skipTest("no sample maps directory")
        for mp in sorted(SAMPLES.glob("*.map")):
            orig = mp.read_bytes()
            with open_map(mp) as doc:
                rebuilt = doc.to_bytes()
            self.assertEqual(rebuilt, orig, f"mismatch on {mp.name}")


class TestMaskBlkAndPathfinding(unittest.TestCase):
    def test_oversized_mask_is_rejected_before_decompression(self) -> None:
        from map_editor.core.mask import MaskError, decode_mask_record

        record = PrefixRecord(0, 0, 0, 0, 100_000, 100_000, 1, b"x")
        with self.assertRaises(MaskError):
            decode_mask_record(record)

    def test_mask_2bit_roundtrip_and_cutout(self) -> None:
        from map_editor.core.mask import pack_alpha_to_2bit

        w, h = 45, 33
        grid = [
            (px + py * 2) & 3 for py in range(h) for px in range(w)
        ]
        alpha = bytes(v * 85 for v in grid)
        packed = pack_alpha_to_2bit(w, h, alpha)
        comp = encode_mask_payload(w, h, packed)
        rec = PrefixRecord(0, 0, 10, 20, w, h, len(comp), comp)
        dm = decode_mask_record(rec)
        for py in range(h):
            for px in range(w):
                self.assertEqual(
                    dm.alpha_2bit(px, py), grid[py * w + px]
                )

    def test_server_client_coordinate_bijection(self) -> None:
        w, h = 4800, 3600
        for sx in (0, 1, 67, 239):
            for sy in (0, 1, 81, 179):
                px, py = server_cell_to_client_px(sx, sy, w, h)
                rsx, rsy = client_px_to_server_cell(px, py, w, h)
                self.assertEqual((rsx, rsy), (sx, sy))

    def test_blk_roundtrip_and_castar_wall_detour(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            mp = create_map_file(tdir / "arena.map", 640, 480)
            with open_map(mp) as doc:
                doc.paint_cells_line(8, 0, 8, 9, 1)
                blk_path = tdir / "arena.blk"
                blk = extract_blk_from_map(doc)
                write_blk(blk, blk_path)
                re_blk = read_blk(blk_path)
                self.assertEqual(re_blk.cells, blk.cells)
                apply_blk_to_map(doc, re_blk)

                path = find_path(
                    doc.header.grid_columns,
                    doc.header.grid_rows,
                    lambda cx, cy: (doc.cell_at_index(cx, cy) or 0) % 2 == 0,
                    (2, 2),
                    (14, 2),
                )
                self.assertTrue(path.found)
                for cx, cy in path.cells:
                    self.assertEqual((doc.cell_at_index(cx, cy) or 0) & 1, 0)


class TestFullEditorWorkflowUndoAndGuards(unittest.TestCase):
    def test_verified_save_failure_preserves_destination_and_reopens_document(
        self,
    ) -> None:
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.map"
            target = Path(tmp) / "existing.map"
            create_map_file(source, 640, 480)
            target.write_bytes(b"known-good-destination")
            doc = open_map(source)
            original_target = target.read_bytes()
            with patch(
                "map_editor.core.mapfile.open_map",
                side_effect=ValueError("bad verify"),
            ):
                with self.assertRaisesRegex(ValueError, "bad verify"):
                    doc.save(target, verify=True)
            self.assertEqual(target.read_bytes(), original_target)
            self.assertEqual(len(doc.read_cells(doc.sector(0))), 192)
            original_source = source.read_bytes()
            with patch(
                "map_editor.core.mapfile.open_map",
                side_effect=ValueError("bad in-place verify"),
            ):
                with self.assertRaisesRegex(ValueError, "bad in-place verify"):
                    doc.save(source, verify=True)
            self.assertEqual(source.read_bytes(), original_source)
            self.assertEqual(len(doc.read_cells(doc.sector(0))), 192)
            doc.close()

    def test_save_verifies_sector_jpeg_before_replacing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.map"
            target = Path(tmp) / "existing.map"
            create_map_file(source, 640, 480)
            target.write_bytes(b"known-good")
            doc = open_map(source)
            sector = doc.sector(0)
            doc.set_raw_sector_image(
                0, sector.segment_lengths, bytes(sector.image_length)
            )
            with self.assertRaises(GepjError):
                doc.save(target, verify=True)
            self.assertEqual(target.read_bytes(), b"known-good")
            doc.close()

    def test_create_map_verification_failure_preserves_existing_destination(
        self,
    ) -> None:
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing.map"
            target.write_bytes(b"known-good")
            with patch(
                "map_editor.core.mapfile.open_map",
                side_effect=ValueError("invalid generated map"),
            ):
                with self.assertRaisesRegex(ValueError, "invalid generated map"):
                    create_map_file(target, 640, 480)
            self.assertEqual(target.read_bytes(), b"known-good")
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])

    def test_failed_map_switch_keeps_current_unsaved_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            current = Path(tmp) / "current.map"
            replacement = Path(tmp) / "replacement.map"
            create_map_file(current, 640, 480)
            create_map_file(replacement, 640, 480)
            vm = EditorViewModel(config=Config.load(Path(tmp) / "cfg.json"))
            doc = vm.open_map_file(current)
            vm.paint_cell_brush(40, 40, value=1)
            with self.assertRaises(FileNotFoundError):
                vm.open_map_file(Path(tmp) / "missing.map", discard_changes=True)
            self.assertIs(vm.document, doc)
            self.assertTrue(vm.dirty)
            with self.assertRaisesRegex(RuntimeError, "未保存修改"):
                vm.open_map_file(replacement)
            vm.open_map_file(replacement, discard_changes=True)
            self.assertFalse(vm.dirty)
            vm.close_map()

    def test_full_edit_undo_redo_save_and_trailing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            art_path = tdir / "world.png"
            art = Image.new("RGB", (640, 480), (42, 92, 66))
            draw = ImageDraw.Draw(art)
            draw.rectangle((80, 60, 560, 420), outline=(220, 190, 90), width=12)
            art.save(art_path)

            src_map = tdir / "client" / "9001.map"
            src_map.parent.mkdir(parents=True)
            rc = main(["--build-map", f"{art_path}:{src_map}"])
            self.assertEqual(rc, 0)
            self.assertTrue(src_map.is_file())

            original_before_rejected_build = src_map.read_bytes()
            rejected = main(
                [
                    "--build-map",
                    f"{art_path}:{src_map}",
                    "--client-root",
                    str(src_map.parent),
                ]
            )
            self.assertEqual(rejected, 1)
            self.assertEqual(src_map.read_bytes(), original_before_rejected_build)

            src_bytes_clean = src_map.read_bytes()
            src_map.write_bytes(src_bytes_clean + b"\xde\xad\xbe\xef" * 64)

            cfg = Config.load(tdir / "cfg.json")
            vm = EditorViewModel(config=cfg)
            vm.set_client_root(tdir / "client")
            doc = vm.open_map("9001")
            self.assertEqual(doc.trailing_bytes, 256)

            with self.assertRaises(ExportBlockedError):
                vm.save_map(src_map)
            with self.assertRaises(ExportBlockedError):
                vm.save_map(src_map, allow_overwrite_source=True)

            orig_cell = doc.cell_at(100, 100)
            orig_light = doc.lightmap_at(100, 100)

            vm.paint_cell_rect(100, 100, 180, 160, value=2)
            self.assertEqual(doc.cell_at(100, 100), 2)

            vm.paint_lightmap_at(100, 100, nibble=14, radius=2)
            self.assertEqual(doc.lightmap_at(100, 100), 14)

            mask_img = Image.new("RGBA", (48, 36), (255, 255, 255, 220))
            midx = vm.import_mask_image(mask_img, 300, 220)
            self.assertEqual(len(doc.records), 1)
            vm.move_mask_record(midx, 310, 225)
            self.assertEqual((doc.records[0].x, doc.records[0].y), (310, 225))

            for _ in range(4):
                self.assertIsNotNone(vm.undo())
            self.assertEqual(len(doc.records), 0)
            self.assertEqual(doc.lightmap_at(100, 100), orig_light)
            self.assertEqual(doc.cell_at(100, 100), orig_cell)

            for _ in range(4):
                self.assertIsNotNone(vm.redo())

            out_map = tdir / "out" / "9001_edited.map"
            vm.save_map(out_map)
            self.assertFalse(vm.dirty)
            vm.undo()
            self.assertTrue(vm.dirty)
            vm.redo()
            self.assertFalse(vm.dirty)
            vm.export_blk(tdir / "out" / "9001.blk")
            vm.export_walkability_png(tdir / "out" / "9001_walk.png")
            vm.export_lightmap_png(tdir / "out" / "9001_light.png")
            vm.export_mask_png(0, tdir / "out" / "9001_mask0.png")

            with open_map(out_map) as verify_doc:
                self.assertEqual(verify_doc.trailing_bytes, 0)
                self.assertEqual(verify_doc.cell_at(100, 100), 2)
                self.assertEqual(verify_doc.lightmap_at(100, 100), 14)
                self.assertEqual(len(verify_doc.records), 1)
                self.assertEqual(
                    (verify_doc.records[0].x, verify_doc.records[0].y),
                    (310, 225),
                )
                rendered = render_region(
                    verify_doc, 0, 0, 320, 240, apply_lighting=True
                )
                self.assertEqual((rendered.width, rendered.height), (320, 240))

            vm.config.save_mode = "loose"
            copy_src = tdir / "loose_copy.map"
            copy_src.write_bytes(out_map.read_bytes())
            vm.open_map_file(copy_src)
            vm.paint_cell_brush(40, 40, value=3, radius=0)
            vm.save_map(copy_src, allow_overwrite_source=True)
            vm.close_map()

            audit_vm = EditorViewModel(config=Config.load(tdir / "audit.json"))
            audit_vm.set_client_root(tdir / "out")
            audit_vm.open_map("9001_edited")
            report = audit_vm.audit_current_map()
            self.assertGreater(report["walkability"]["walkable_cells"], 0)
            self.assertEqual(
                report["walkability"]["walkable_cells"]
                + report["walkability"]["blocked_cells"],
                report["walkability"]["total_cells"],
            )
            audit_vm.close_map()
            self.assertEqual(
                main(["--scan", str(tdir / "out"), "--audit", "9001_edited"]), 0
            )
            self.assertEqual(
                main(
                    [
                        "--scan",
                        str(tdir / "out"),
                        "--find-path",
                        "9001_edited:20,20:400,300",
                    ]
                ),
                0,
            )


@unittest.skipUnless(
    DRIVE_CORPUS.is_dir(), "Google Drive full 101-map corpus not present"
)
class TestFullGoogleDriveCorpus(unittest.TestCase):
    def test_all_101_maps_parse_decode_scene_resolve_and_roundtrip(self) -> None:
        st = SceneTable.load()
        maps = sorted(DRIVE_CORPUS.glob("*.map"))
        self.assertEqual(len(maps), 101)
        total_sectors = 0
        total_masks = 0
        for mp in maps:
            self.assertIsNotNone(st.get(mp.stem), f"missing scene meta for {mp.stem}")
            raw = mp.read_bytes()
            with open_map(mp) as doc:
                expected_refs = compute_sector_record_refs(
                    doc.header.width, doc.header.height, doc.records
                )
                for sec in doc.iter_sectors():
                    self.assertIsNotNone(doc.lightmap_nibbles(sec.index))
                    self.assertEqual(sec.record_refs, expected_refs[sec.index])
                for r in doc.records:
                    dm = decode_mask_record(r)
                    self.assertEqual((dm.width, dm.height), (r.width, r.height))
                rebuilt = doc.to_bytes()
                active_len = len(raw) - doc.trailing_bytes
                self.assertEqual(rebuilt, raw[:active_len], f"diff in {mp.name}")
                total_sectors += doc.header.sector_count
                total_masks += len(doc.records)
        self.assertEqual(total_sectors, 11763)
        self.assertEqual(total_masks, 20036)


if __name__ == "__main__":
    unittest.main(verbosity=2)
