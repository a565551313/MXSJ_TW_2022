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

    def test_map_list_column_stretches_to_viewport(self) -> None:
        """左侧地图列表隐藏表头后，唯一列必须显式 Stretch。

        回归防护：缺 setSectionResizeMode(0, Stretch) 时列宽锁死默认
        100px，行卡片被挤在窄条、面板右侧大片空白（「宽但挤」）。
        """
        global _APP_KEEPALIVE
        from map_editor.client.config import Config
        from map_editor.ui.viewmodel import EditorViewModel
        from map_editor.ui.widgets import EditorWindow

        app = QApplication.instance() or QApplication([])
        _APP_KEEPALIVE = app

        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config.load(Path(tmp) / "gui_cfg.json")
            cfg.remember_root(SAMPLES)
            vm = EditorViewModel(config=cfg)
            win = EditorWindow(vm)
            win.resize(1540, 940)
            win.show()
            win._open_root(str(SAMPLES))
            app.processEvents()

            self.assertGreater(win.table.rowCount(), 0)
            viewport_w = win.table.viewport().width()
            # 布局确已生效（left 面板最小 225px，减布局边距后视口应 >150px）
            self.assertGreater(viewport_w, 150)
            # Stretch 后列宽与视口一致，行卡片随之铺满
            self.assertEqual(win.table.columnWidth(0), viewport_w)
            card = win.table.cellWidget(0, 0)
            self.assertEqual(card.width(), viewport_w)

            win.close()
            win.deleteLater()
            app.processEvents()

    def test_entity_tables_use_fixed_headers(self) -> None:
        """底部 NPC/传送点列表为固定表头文字表格。

        NPC 七列：编号/NPC/模型ID/朝向/服务端坐标/像素坐标/状态；
        传送点五列：编号/传送点/服务端坐标/跳转坐标/描述。
        行内为纯文字单元格（不再使用卡片 cellWidget）。
        """
        global _APP_KEEPALIVE
        from PySide6.QtCore import Qt
        from map_editor.client.config import Config
        from map_editor.ui.viewmodel import EditorViewModel
        from map_editor.ui.widgets import EditorWindow

        app = QApplication.instance() or QApplication([])
        _APP_KEEPALIVE = app

        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config.load(Path(tmp) / "gui_cfg.json")
            cfg.remember_root(SAMPLES)
            vm = EditorViewModel(config=cfg)
            win = EditorWindow(vm)
            win.resize(1540, 940)
            win.show()
            win._open_root(str(SAMPLES))
            app.processEvents()

            npc_table = win.entity_tables["npcs"]
            portal_table = win.entity_tables["portals"]
            self.assertEqual(npc_table.columnCount(), 7)
            self.assertEqual(
                [npc_table.horizontalHeaderItem(c).text() for c in range(7)],
                ["编号", "NPC", "模型ID", "朝向", "服务端坐标", "像素坐标", "状态"],
            )
            self.assertEqual(portal_table.columnCount(), 5)
            self.assertEqual(
                [portal_table.horizontalHeaderItem(c).text() for c in range(5)],
                ["编号", "传送点", "服务端坐标", "跳转坐标", "描述"],
            )
            # 表头常驻可见（回归：旧实现把表头隐藏、后 3 列 setColumnHidden）
            self.assertFalse(npc_table.horizontalHeader().isHidden())
            self.assertFalse(portal_table.horizontalHeader().isHidden())
            self.assertFalse(npc_table.isColumnHidden(2))  # 模型ID
            self.assertFalse(npc_table.isColumnHidden(6))  # 状态
            # 列宽按内容定、文字居中（回归：名称列曾 Stretch 到 442px 难扫读）
            self.assertEqual(npc_table.columnWidth(1), 170)
            self.assertLessEqual(
                sum(npc_table.columnWidth(c) for c in range(7)),
                npc_table.viewport().width() + 1,
            )
            self.assertEqual(
                npc_table.horizontalHeader().defaultAlignment(),
                Qt.AlignmentFlag.AlignCenter,
            )

            # 选中含 NPC 的样例地图 1034，校验行数据形态
            target = next(
                (r for r in win._filtered_rows if r.key == "1034"), None
            )
            if target is None:
                self.skipTest("样例目录中无地图 1034")
            win.table.selectRow(win._filtered_rows.index(target))
            app.processEvents()

            self.assertEqual(npc_table.rowCount(), 1)
            # 传送点 = 2 个传送点 + 1 行出生点（默认落点，置顶）
            self.assertEqual(portal_table.rowCount(), 3)
            self.assertEqual(portal_table.item(0, 1).text(), "默认落点")
            self.assertEqual(portal_table.item(0, 4).text(), "出生点")
            self.assertEqual(npc_table.item(0, 0).text(), "4427")  # npc_id
            self.assertEqual(npc_table.item(0, 1).text(), "組隊集結人")
            self.assertEqual(npc_table.item(0, 2).text(), "zdjjr")  # 模型ID=shape
            self.assertEqual(npc_table.item(0, 3).text(), "0")  # 朝向 dir
            self.assertRegex(
                npc_table.item(0, 4).text(), r"^\d+,\d+$"
            )  # 服务端坐标
            self.assertRegex(
                npc_table.item(0, 5).text(), r"^\d+,\d+$"
            )  # 像素坐标
            self.assertIn(npc_table.item(0, 6).text(), ("可通行", "阻挡格"))
            # 纯文字行：首列不再是卡片 cellWidget
            self.assertIsNone(npc_table.cellWidget(0, 0))
            # 单元格文字居中
            for column in range(7):
                self.assertEqual(
                    npc_table.item(0, column).textAlignment(),
                    Qt.AlignmentFlag.AlignCenter,
                )

            # 传送点行：编号/名称/服务端/跳转/描述 五列均有值（无 npc_id 显示 —）
            for row in range(portal_table.rowCount()):
                for column in range(5):
                    self.assertTrue(portal_table.item(row, column).text())

            # 选中行后检查器标签镜像整行（含表头）
            npc_table.selectRow(0)
            app.processEvents()
            self.assertIn("编号 4427", win.selected_object_lbl.text())
            self.assertIn("模型ID zdjjr", win.selected_object_lbl.text())

            win.close()
            win.deleteLater()
            app.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)
