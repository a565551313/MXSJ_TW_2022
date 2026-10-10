#!/usr/bin/env python3
"""Headless tests for Tk GUI data helpers and offline browser GUI generation."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[5]
TOOLS = ROOT / "work/dream-world-connect-login-map/tools"
sys.path.insert(0, str(TOOLS))
from map_parser import parse_map
from map_viewer import build_grid
from map_gui import REPO, cell_at, cell_runs, discover, records_at
from map_gui_html import build_payload, generate


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = parse_map(ROOT / "map/2303.map")
        cls.grid = build_grid(cls.doc)

    def test_repository_path_and_available_maps(self):
        self.assertEqual(REPO, ROOT)
        maps = discover(ROOT / "map", TOOLS / "map-textures")
        self.assertEqual(sorted(maps), ["2101", "2111", "2112", "2122", "2303"])
        for source, png in maps.values():
            self.assertTrue(source.is_file() and png.is_file())

    def test_cells_and_boundaries(self):
        self.assertEqual(cell_at(self.grid, 725, 1085, 2000, 1500), 2)
        self.assertIsNone(cell_at(self.grid, -1, 0, 2000, 1500))
        self.assertIsNone(cell_at(self.grid, 2000, 20, 2000, 1500))
        self.assertIsNone(cell_at(self.grid, 100, 1500, 2000, 1500))
        self.assertEqual(cell_at(self.grid, 100, 20, 2000, 1500), self.grid[1][5])

    def test_object_hit_testing(self):
        records = self.doc["prefix_records"]
        self.assertIn(0, records_at(records, 1159, 1205))
        self.assertNotIn(0, records_at(records, 1219, 1238))
        self.assertEqual(records_at(records, 0, 0), [])

    def test_runs_have_original_raw_values_and_are_cropped(self):
        runs = list(cell_runs(self.grid, 2000, 1500))
        self.assertTrue(runs)
        for x, y, width, value in runs:
            self.assertTrue(0 <= x < 2000 and 0 <= y < 1500)
            self.assertLessEqual(x + width, 2000)
            self.assertEqual(value, self.grid[y // 20][x // 20])
            self.assertNotEqual(value, 0)

    def test_embedded_html_is_self_contained(self):
        maps = build_payload(ROOT / "map", TOOLS / "map-textures")
        self.assertEqual(len(maps), 5)
        for item in maps:
            self.assertTrue(item["img"].startswith("data:image/png;base64,"))
            self.assertEqual(len(item["cells"]), 112 * 84)
        self.assertEqual(len(maps[-1]["records"]), 32)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "maps.html"
            count, size = generate(ROOT / "map", TOOLS / "map-textures", output)
            text = output.read_text(encoding="utf-8")
            self.assertEqual(count, 5)
            self.assertEqual(len(text.encode("utf-8")), size)
            self.assertEqual(text.count("data:image/png;base64,"), 5)
            self.assertNotIn("__PAYLOAD__", text)
            self.assertNotIn("<script src=", text)
            self.assertNotIn("fetch(", text)
            if shutil.which("node"):
                script = text.split("<script>", 1)[1].split("</script>", 1)[0]
                script_file = Path(temp) / "gui.js"
                script_file.write_text(script, encoding="utf-8")
                subprocess.run(["node", "--check", str(script_file)], check=True, capture_output=True)

    def test_external_directory_not_limited_to_five_ids(self):
        # Mimics a user-provided map outside the repository's map/ directory.
        # This reuses a known-format sample; it does NOT validate unknown formats.
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            maps, textures = base / "external_maps", base / "external_png"
            maps.mkdir()
            textures.mkdir()
            shutil.copyfile(ROOT / "map/2111.map", maps / "9999.map")
            shutil.copyfile(TOOLS / "map-textures/2111.png", textures / "9999.png")
            self.assertEqual(list(discover(maps, textures)), ["9999"])
            payload = build_payload(maps, textures)
            self.assertEqual([item["id"] for item in payload], ["9999"])
            count, _ = generate(maps, textures, base / "external.html")
            self.assertEqual(count, 1)
            self.assertTrue((base / "external.html").is_file())

    def test_missing_maps_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            empty = Path(temp)
            with self.assertRaisesRegex(ValueError, "没有找到"):
                generate(empty, empty, empty / "maps.html")


if __name__ == "__main__":
    unittest.main()
