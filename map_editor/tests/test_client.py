"""Tests for the client-discovery, scene-table, config and view-model layers.

These are the layers that make the editor directory-independent, and they run
headless (no Qt import), so they execute in CI and in sandboxes where
``QtWidgets`` cannot even be loaded.
"""
from __future__ import annotations

import json
import os
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import CLIENT_ROOT, SAMPLES, SCRIPT_FLS  # noqa: E402

from map_editor.client.config import Config, config_dir  # noqa: E402
from map_editor.client.discovery import DiscoveryError, discover  # noqa: E402
from map_editor.client.scene_table import SceneTable  # noqa: E402
from map_editor.client.scriptfls import (  # noqa: E402
    FlsArchive,
    FlsError,
    decode_directory,
)
from map_editor.core.mapfile import MAGIC  # noqa: E402
from map_editor.ui.viewmodel import LAYERS, EditorViewModel  # noqa: E402

REPO = CLIENT_ROOT or Path("/nonexistent")
needs_samples = unittest.skipUnless(SAMPLES.is_dir(), f"no samples at {SAMPLES}")
needs_fls = unittest.skipUnless(SCRIPT_FLS.is_file(), f"no script.fls at {SCRIPT_FLS}")


class TmpCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="map_editor_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def fake_map(self, rel: str, width: int = 2000, height: int = 1500) -> Path:
        """Write a file with a valid 0.1M header and 49 self-consistent offsets."""
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        n = -(-width // 320) * (-(-height // 240))
        head = bytearray(MAGIC + struct.pack("<II", width, height))
        first = 12 + 4 * n + 8
        for i in range(n):
            head += struct.pack("<I", first + i * 200)
        head += struct.pack("<I", 12 + 4 * n + 4)
        head += struct.pack("<I", 0)
        p.write_bytes(bytes(head) + b"\x00" * (n * 200))
        return p


class TestDiscovery(TmpCase):
    def test_finds_maps_in_nested_folders_by_content(self) -> None:
        self.fake_map("map/2101.map")
        self.fake_map("patch/2024/sub/2111.map")
        self.fake_map("weird place/2112.map")
        (self.tmp / "map" / "not_a_map.map").write_bytes(b"JUNK" + b"\x00" * 64)
        (self.tmp / "readme.txt").write_text("hello", encoding="utf-8")

        layout = discover(self.tmp)
        self.assertEqual([m.scene_key for m in layout.maps], ["2101", "2111", "2112"])
        self.assertTrue(layout.ok)

    def test_rejects_nonexistent_and_file_roots(self) -> None:
        with self.assertRaises(DiscoveryError):
            discover(self.tmp / "nope")
        f = self.tmp / "afile"
        f.write_text("x", encoding="utf-8")
        with self.assertRaises(DiscoveryError):
            discover(f)

    def test_prunes_listed_directories(self) -> None:
        self.fake_map("map/2101.map")
        self.fake_map(".git/objects/9999.map")
        self.fake_map("node_modules/x/8888.map")
        layout = discover(self.tmp)
        self.assertEqual([m.scene_key for m in layout.maps], ["2101"])
        self.assertTrue(any(p.name == ".git" for p in layout.pruned))

    def test_finds_script_fls_preferring_data_dir(self) -> None:
        self.fake_map("map/2101.map")
        (self.tmp / "loose").mkdir()
        (self.tmp / "loose" / "script.fls").write_bytes(b"0SLF" + b"\x00" * 32)
        (self.tmp / "data").mkdir()
        (self.tmp / "data" / "script.fls").write_bytes(b"0SLF" + b"\x00" * 32)
        layout = discover(self.tmp)
        self.assertEqual(layout.script_fls.parent.name, "data")

    def test_max_files_bound_is_respected(self) -> None:
        for i in range(5):
            self.fake_map(f"map/{2100 + i}.map")
        layout = discover(self.tmp, max_files=3)
        self.assertLessEqual(len(layout.maps), 3)

    @needs_samples
    def test_real_repo_finds_the_five_samples(self) -> None:
        layout = discover(REPO)
        keys = [m.scene_key for m in layout.maps]
        for expected in ("2101", "2111", "2112", "2122", "2303"):
            self.assertIn(expected, keys)
        self.assertIsNotNone(layout.script_fls)
        self.assertEqual(layout.script_fls.name, "script.fls")
        self.assertIsNotNone(layout.main_exe)


class TestSceneTable(unittest.TestCase):
    def test_loads_shipped_table(self) -> None:
        table = SceneTable.load()
        self.assertGreaterEqual(len(table), 100, "shipped scene table looks empty")
        meta = table.get("2101")
        self.assertIsNotNone(meta)
        self.assertEqual((meta.width, meta.height), (2000, 1500))
        self.assertTrue(meta.name)

    def test_normalizes_keys(self) -> None:
        table = SceneTable.load()
        for key in ("2101", "2101.map", 2101, " 2101 "):
            self.assertEqual(table.normalize(key), "2101")
            if table.get(key):
                self.assertEqual(table.get(key).key, "2101")

    def test_missing_table_degrades_gracefully(self) -> None:
        empty = SceneTable.load("/nonexistent/nope.json")
        self.assertEqual(len(empty), 0)
        self.assertIsNone(empty.get("2101"))
        self.assertEqual(empty.display_name("2101"), "场景 2101")


class TestConfig(TmpCase):
    def test_roundtrip_and_recent_ordering(self) -> None:
        home = self.tmp / "home"
        os.environ["MAP_EDITOR_HOME"] = str(home)
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)
        self.assertEqual(config_dir(), home)

        cfg = Config.load()
        self.assertEqual(cfg.client_root, "")
        cfg.remember_root("/games/mxsj")
        cfg.remember_root("/games/other")
        cfg.remember_root("/games/mxsj")
        self.assertEqual(cfg.recent_roots, ["/games/mxsj", "/games/other"])
        cfg.show_grid = True
        saved = cfg.save()
        self.assertTrue(saved.is_file())

        again = Config.load()
        self.assertEqual(again.client_root, "/games/mxsj")
        self.assertTrue(again.show_grid)

    def test_corrupt_config_falls_back_to_defaults(self) -> None:
        home = self.tmp / "home2"
        home.mkdir(parents=True)
        (home / "config.json").write_text("{not json", encoding="utf-8")
        os.environ["MAP_EDITOR_HOME"] = str(home)
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)
        cfg = Config.load()
        self.assertEqual(cfg.client_root, "")
        self.assertTrue(cfg.show_texture)

    def test_unknown_keys_are_ignored(self) -> None:
        home = self.tmp / "home3"
        home.mkdir(parents=True)
        (home / "config.json").write_text(
            json.dumps({"client_root": "/x", "from_the_future": 1}), encoding="utf-8")
        os.environ["MAP_EDITOR_HOME"] = str(home)
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)
        self.assertEqual(Config.load().client_root, "/x")


@needs_fls
class TestFlsArchive(unittest.TestCase):
    def test_header_and_reference_entries(self) -> None:
        """Offsets/lengths must match tools/fls_batch_decoder.py exactly."""
        expected = {1301: (12165414, 2416, 7868),
                    400: (16922856, 2229, 4790),
                    3970: (20751983, 5825, 12802)}
        with FlsArchive(SCRIPT_FLS) as arc:
            self.assertEqual(arc.count, 5002)
            self.assertEqual(arc.directory_offset, 0x173EB22)
            for idx, (off, clen, exp_len) in expected.items():
                with self.subTest(entry=idx):
                    rec = arc.record(idx)
                    self.assertEqual(rec.payload_offset, off)
                    self.assertEqual(rec.compressed_length, clen)
                    self.assertEqual(len(arc.expanded(idx)), exp_len)

    def test_out_of_range_entry(self) -> None:
        with FlsArchive(SCRIPT_FLS) as arc:
            with self.assertRaises(FlsError):
                arc.record(arc.count)

    def test_directory_transform_is_pure(self) -> None:
        raw = (1, 2, 3, 4)
        self.assertEqual(decode_directory(7, raw), decode_directory(7, raw))


@needs_samples
class TestViewModel(TmpCase):
    def setUp(self) -> None:
        super().setUp()
        os.environ["MAP_EDITOR_HOME"] = str(self.tmp / "cfg")
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)
        self.vm = EditorViewModel(config=Config())

    def test_scan_then_list_rows_with_real_dimensions(self) -> None:
        import math
        self.vm.set_client_root(SAMPLES)
        rows = self.vm.rows
        on_disk = len(list(SAMPLES.glob("*.map")))
        self.assertEqual(len(rows), on_disk)
        for r in rows:
            self.assertFalse(r.broken, r.error)
            self.assertGreater(r.width, 0)
            # Sector count must equal ceil(w/320)*ceil(h/240) for every size.
            self.assertEqual(r.sectors,
                             math.ceil(r.width / 320) * math.ceil(r.height / 240),
                             f"{r.key}: {r.width}x{r.height}")
        self.assertIn(f"{on_disk} 张地图", self.vm.status_line())

    def test_open_map_updates_state_and_locate(self) -> None:
        self.vm.set_client_root(SAMPLES)
        doc = self.vm.open_map("2303")
        self.assertEqual(self.vm.state.current_key, "2303")
        self.assertEqual(self.vm.state.current_records, 32)
        info = self.vm.locate(1159, 1205)
        self.assertTrue(info["inside"])
        self.assertEqual(info["cell"], (57, 60))
        self.assertIsNotNone(info["cell_value"])
        self.assertEqual(info["sector"], (60 // 12) * 7 + (57 // 16))
        outside = self.vm.locate(99999, 0)
        self.assertFalse(outside["inside"])
        self.assertIsNone(outside["cell_value"])
        doc.close()

    def test_layers_are_validated_and_persisted(self) -> None:
        for name in LAYERS:
            self.vm.set_layer(name, False)
            self.assertFalse(self.vm.layer(name))
        self.vm.set_layer("grid", True)
        self.assertTrue(self.vm.layer("grid"))
        with self.assertRaises(KeyError):
            self.vm.set_layer("nope", True)
        path = self.vm.save_config()
        self.assertTrue(path.is_file())
        self.assertFalse(Config.load().show_texture)
        self.assertTrue(Config.load().show_grid)

    def test_export_json_contains_every_sector(self) -> None:
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2303")
        out = self.vm.export_json(self.tmp / "out" / "2303.json")
        doc = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(doc["scene_key"], "2303")
        self.assertEqual(len(doc["sectors"]), 49)
        self.assertEqual(len(doc["prefix_records"]), 32)
        self.assertEqual(doc["prefix_records"][0]["x"], 1159)
        self.assertEqual(doc["sector_grid"], [7, 7])
        self.assertEqual(doc["cell_px"], 20)
        # All GIRB payloads hash identically — the constant-trailer finding.
        self.assertEqual(len({s["girb_sha256"] for s in doc["sectors"]}), 1)
        self.vm.close_map()

    def test_export_png_roundtrips_dimensions(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")
        out = self.vm.export_png(self.tmp / "out" / "region.png", (100, 100, 420, 340))
        with Image.open(out) as im:
            self.assertEqual(im.size, (320, 240))
        self.vm.close_map()

    def test_render_without_open_map_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            self.vm.render(0, 0, 10, 10)

    def test_export_json_refuses_to_overwrite_the_open_source_map(self) -> None:
        """PR #25 review item 2: export must never touch client source files.

        Reproduces the exact regression (JSON export truncating a live
        ``.map`` file in place) on an isolated copy, then asserts the file
        is untouched byte-for-byte -- not just "still parses".
        """
        import hashlib

        from map_editor.ui.viewmodel import ExportBlockedError

        src = SAMPLES / "2101.map"
        before = hashlib.sha256(src.read_bytes()).hexdigest()
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")
        with self.assertRaises(ExportBlockedError):
            self.vm.export_json(src)
        self.vm.close_map()
        after = hashlib.sha256(src.read_bytes()).hexdigest()
        self.assertEqual(before, after, "source .map was modified by a blocked export")

    def test_export_json_refuses_any_discovered_map_not_only_the_open_one(self) -> None:
        """The guard must cover every scanned map, not just the open document."""
        import hashlib

        from map_editor.ui.viewmodel import ExportBlockedError

        other = SAMPLES / "2111.map"
        before = hashlib.sha256(other.read_bytes()).hexdigest()
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")      # a *different* map is open
        with self.assertRaises(ExportBlockedError):
            self.vm.export_json(other)
        self.vm.close_map()
        self.assertEqual(before, hashlib.sha256(other.read_bytes()).hexdigest())

    def test_export_json_refuses_an_equivalent_unresolved_path(self) -> None:
        """A ``..``-laden or relative alias of the same file must be caught too."""
        from map_editor.ui.viewmodel import ExportBlockedError

        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")
        alias = SAMPLES / "." / ".." / SAMPLES.name / "2101.map"
        with self.assertRaises(ExportBlockedError):
            self.vm.export_json(alias)
        self.vm.close_map()

    def test_export_png_refuses_to_overwrite_a_source_map(self) -> None:
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        from map_editor.ui.viewmodel import ExportBlockedError

        src = SAMPLES / "2101.map"
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")
        with self.assertRaises(ExportBlockedError):
            self.vm.export_png(src)
        self.vm.close_map()

    def test_export_json_to_a_new_path_still_works_after_the_guard(self) -> None:
        """The guard must not false-positive on ordinary, safe export targets."""
        self.vm.set_client_root(SAMPLES)
        self.vm.open_map("2101")
        out = self.vm.export_json(self.tmp / "out" / "not_a_source_file.json")
        self.assertTrue(out.is_file())
        self.vm.close_map()

    def test_unknown_key_raises(self) -> None:
        self.vm.set_client_root(SAMPLES)
        with self.assertRaises(KeyError):
            self.vm.open_map("9999")


if __name__ == "__main__":
    unittest.main(verbosity=2)


@needs_samples
class TestCollisionLayer(TmpCase):
    """The confirmed part of GIRB: geometry, region query, and failure reporting."""

    def setUp(self) -> None:
        super().setUp()
        os.environ["MAP_EDITOR_HOME"] = str(self.tmp / "cfg")
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)
        self.vm = EditorViewModel(config=Config())
        self.vm.set_client_root(SAMPLES)

    def test_region_geometry_is_8px_cells(self) -> None:
        self.vm.open_map("2101")
        reg = self.vm.collision_region(0, 0, 320, 240)
        self.assertEqual((reg["cols"], reg["rows"]), (40, 30))
        self.assertEqual(reg["cell_px"], 8)
        self.assertEqual(len(reg["values"]), 1200)
        self.vm.close_map()

    def test_region_spanning_four_sectors(self) -> None:
        # 300..340 px -> cells 37..42 (crosses the 40-cell sector boundary);
        # 220..260 px -> cells 27..32 (crosses the 30-cell boundary).  So the
        # region touches a 2x2 block of sectors.
        self.vm.open_map("2101")
        reg = self.vm.collision_region(300, 220, 340, 260)
        self.assertEqual((reg["cols"], reg["rows"]), (6, 6))
        self.assertEqual(len(reg["values"]), 36)
        self.assertEqual(reg["decoded"], 4)
        self.assertEqual(reg["failed"], 0)
        self.vm.close_map()

    def test_undecodable_sector_yields_none_not_an_error(self) -> None:
        self.vm.open_map("1034")
        st = self.vm.collision_stats()
        if st["failed"] == 0:
            self.skipTest("decoder now handles 1034; nothing to check")
        reg = self.vm.collision_region(0, 0, 320, 240)
        self.assertTrue(any(v is None for v in reg["values"]) or reg["failed"] == 0)
        self.vm.close_map()

    def test_collision_at_outside_map_is_none(self) -> None:
        self.vm.open_map("2101")
        doc = self.vm.document
        self.assertIsNone(doc.collision_at(-1, 0))
        self.assertIsNone(doc.collision_at(999999, 0))
        self.vm.close_map()

    def test_girb_report_covers_every_map(self) -> None:
        report = self.vm.girb_report()
        keys = {r["key"] for r in report}
        self.assertEqual(keys, {r.key for r in self.vm.rows})
        for r in report:
            if not r.get("error"):
                self.assertEqual(r["decoded"] + r["failed"], r["sectors"])

    def test_new_layers_are_registered_and_persisted(self) -> None:
        for name in ("collision", "collision_grid"):
            self.assertIn(name, LAYERS)
            self.vm.set_layer(name, True)
            self.assertTrue(self.vm.layer(name))
        self.vm.save_config()
        again = Config.load()
        self.assertTrue(again.show_collision)
        self.assertTrue(again.show_collision_grid)

    def test_cli_girb_report_runs(self) -> None:
        import io
        from contextlib import redirect_stdout

        from map_editor.cli import main
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--scan", str(SAMPLES), "--girb-report"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("GIRB字节", text)
        self.assertIn("40x30", text)
