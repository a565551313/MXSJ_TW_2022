"""Headless offscreen PySide6 GUI tests for ``EditorWindow`` and ``MapCanvas``."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

REPO = Path(__file__).resolve().parents[2]
SAMPLES = REPO / "map"
DRIVE_CORPUS = Path(
    os.environ.get(
        "MXSJ_MAP_CORPUS",
        str(Path(tempfile.gettempdir()) / "mxsj_map" / "extracted"),
    )
)

try:
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False

_APP_KEEPALIVE = None


@unittest.skipUnless(QT_AVAILABLE and SAMPLES.is_dir(), "PySide6 GUI unavailable")
class TestEditorGuiOffscreen(unittest.TestCase):
    def test_workbench_renders_edits_undoes_and_captures_screenshots(self) -> None:
        global _APP_KEEPALIVE
        from map_editor.client.config import Config
        from map_editor.ui.viewmodel import EditorViewModel
        from map_editor.ui.widgets import STUDIO_QSS, EditorWindow, _install_cjk_fonts

        app = QApplication.instance() or QApplication([])
        _APP_KEEPALIVE = app
        app.setStyleSheet(STUDIO_QSS)
        _install_cjk_fonts(app)

        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config.load(Path(tmp) / "gui_cfg.json")
            scan_dir = DRIVE_CORPUS if DRIVE_CORPUS.is_dir() else SAMPLES
            cfg.remember_root(scan_dir)
            vm = EditorViewModel(config=cfg)
            win = EditorWindow(vm)
            win.resize(1540, 940)
            win.show()
            win._open_root(str(scan_dir))
            app.processEvents()

            target_key = "test_new2_1054" if DRIVE_CORPUS.is_dir() else "2303"
            for r_idx, r_obj in enumerate(win._filtered_rows):
                if r_obj.key == target_key:
                    win.table.selectRow(r_idx)
                    break
            win.canvas.center_on_world(1600, 1220, zoom=0.72)

            # Walk-only interaction state must not leak into other categories or maps.
            vm.state.brush_radius = 2
            win._select_main_category("walk")
            win._select_walk_mode("pen_dot")
            self.assertEqual(vm.state.brush_radius, 0)
            win._select_walk_mode("brush")
            self.assertEqual(vm.state.brush_radius, 2)
            win._select_walk_mode("pen_path")
            win.canvas._pen_nodes = [(100, 100), (160, 120)]
            win._after_document_opened()
            self.assertEqual(win.canvas._pen_nodes, [])
            self.assertTrue(win.canvas.pen_path_mode)
            win._select_main_category("browse")
            self.assertFalse(win.canvas.pen_path_mode)
            self.assertFalse(win.canvas.eraser_mode)
            self.assertEqual(win.canvas._pen_nodes, [])
            win.selected_object_lbl.setText("stale object")
            win.entity_tabs.setCurrentIndex(1)
            self.assertEqual(
                win.selected_object_lbl.text(), "从下方 NPC 或传送点列表选择对象"
            )
            win.entity_tabs.setCurrentIndex(0)

            # Pick two walkable points near NPCs for live CAStar demonstration
            ents = vm.current_entities()
            walk_npcs = [n for n in ents["npcs"] if n["walkable"]]
            if len(walk_npcs) >= 4:
                p0 = (walk_npcs[0]["px"], walk_npcs[0]["py"])
                p1 = (walk_npcs[3]["px"], walk_npcs[3]["py"])
                vm.simulate_path(p0, p1)
                win.canvas.center_on_world(
                    (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, zoom=0.68
                )
            else:
                vm.simulate_path((1220, 1340), (1680, 1460))

            win._toggle_layer("walkability", True)
            win._toggle_layer("mask_cutout", True)
            vm.paint_cell_rect(1460, 1120, 1560, 1180, value=1)
            vm.paint_lightmap_at(1500, 1150, nibble=14, radius=4)
            win.canvas.invalidate_caches()
            win._on_cursor_moved(1520, 1380)
            app.processEvents()

            shot1 = win.grab()
            self.assertEqual((shot1.width(), shot1.height()), (1540, 940))

            # Exercise contextual tools, inspector, and the lower entity list.
            win._select_main_category("mask")
            app.processEvents()
            shot2 = win.grab()
            self.assertEqual((shot2.width(), shot2.height()), (1540, 940))
            win.entity_tabs.setCurrentIndex(1)
            app.processEvents()
            shot3 = win.grab()
            self.assertEqual((shot3.width(), shot3.height()), (1540, 940))

            shot_dir = Path(tempfile.gettempdir()) / "mxsj_map" / "screenshots"
            if shot_dir.parent.is_dir():
                shot_dir.mkdir(parents=True, exist_ok=True)
                shot1.save(str(shot_dir / "workbench_main.png"))
                shot2.save(str(shot_dir / "workbench_masks.png"))
                shot3.save(str(shot_dir / "workbench_entities.png"))

            # Undo clean so window closes cleanly without dirty dialog prompt
            while vm.can_undo:
                vm.undo()
            win.close()
            win.deleteLater()
            app.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)
