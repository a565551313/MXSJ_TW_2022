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

            # Switch to mask preview tab and audit tab to exercise every tab render
            win.right_tabs.setCurrentIndex(2)
            app.processEvents()
            shot2 = win.grab()
            self.assertEqual((shot2.width(), shot2.height()), (1540, 940))

            shot_dir = Path(tempfile.gettempdir()) / "mxsj_map" / "screenshots"
            if shot_dir.parent.is_dir():
                shot_dir.mkdir(parents=True, exist_ok=True)
                shot1.save(str(shot_dir / "workbench_main.png"))
                shot2.save(str(shot_dir / "workbench_masks.png"))
                win.right_tabs.setCurrentIndex(3)
                app.processEvents()
                win.grab().save(str(shot_dir / "workbench_entities.png"))

            # Undo clean so window closes cleanly without dirty dialog prompt
            while vm.can_undo:
                vm.undo()
            win.close()
            win.deleteLater()
            app.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)
