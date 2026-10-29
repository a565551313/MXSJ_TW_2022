"""原生 .dlg 绝对坐标与编辑器父相对坐标的边界测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec  # noqa: E402
from ui_editor.core.model import LayoutDocument  # noqa: E402


def native_layout(child_x: int = 510, child_y: int = 310) -> list[dict]:
    return [{
        "sWidgetType": "CMainFrame", "sName": "A",
        "iX": 500, "iY": 300, "iWidth": 800, "iHeight": 600,
        "lChildren": [{
            "sWidgetType": "CTextFrameEx", "sName": "B",
            "iX": child_x, "iY": child_y, "iWidth": 100, "iHeight": 100,
            "sText": "原生坐标", "lChildren": [{
                "sWidgetType": "CBox", "sName": "C",
                "iX": child_x + 10, "iY": child_y + 10,
                "iWidth": 20, "iHeight": 20, "lChildren": [],
            }],
        }],
    }]


class TestNativeCoordinates(unittest.TestCase):
    def test_load_converts_each_native_child_to_parent_relative(self):
        doc = LayoutDocument.from_native_dicts(native_layout(), None)
        root = doc.roots[0]
        child = root.children[0]
        grandchild = child.children[0]
        self.assertEqual((child.x, child.y), (10, 10))
        self.assertEqual(doc.abs_position(child), (510, 310))
        self.assertEqual((grandchild.x, grandchild.y), (10, 10))
        self.assertEqual(doc.abs_position(grandchild), (520, 320))
        self.assertEqual(doc.to_native_dicts(), native_layout())

    def test_editor_example_writes_510_310_not_10_10(self):
        doc = LayoutDocument.from_native_dicts(native_layout(), None)
        child = doc.roots[0].children[0]
        child.set_geometry(x=10, y=10)
        native = doc.to_native_dicts()
        saved_child = native[0]["lChildren"][0]
        self.assertEqual((saved_child["iX"], saved_child["iY"]), (510, 310))
        self.assertNotEqual((saved_child["iX"], saved_child["iY"]), (10, 10))

    def test_existing_native_file_does_not_jump_on_load_or_second_save(self):
        # 旧档里的 B=(10,10) 在游戏就在画布 (10,10)，不是 A 内 (10,10)。
        original = native_layout(child_x=10, child_y=10)
        doc = LayoutDocument.from_native_dicts(original, None)
        child = doc.roots[0].children[0]
        self.assertEqual((child.x, child.y), (-490, -290))
        self.assertEqual(doc.abs_position(child), (10, 10))
        self.assertEqual(doc.to_native_dicts(), original)
        reopened = LayoutDocument.from_native_dicts(doc.to_native_dicts(), None)
        self.assertEqual(reopened.to_native_dicts(), original)

    def test_set_parent_then_save_and_codec_reopen_keep_visual_position(self):
        doc = LayoutDocument.from_dicts([
            {"sWidgetType": "CMainFrame", "sName": "A",
             "iX": 500, "iY": 300, "iWidth": 800, "iHeight": 600,
             "lChildren": []},
            {"sWidgetType": "CBox", "sName": "B",
             "iX": 510, "iY": 310, "iWidth": 100, "iHeight": 100,
             "lChildren": []},
        ], None)
        parent, child = doc.roots
        doc.set_parent(child, parent)
        child.set_geometry(x=10, y=10)
        payload = dlg_codec.dump_bytes(doc.to_native_dicts())
        raw, md5 = dlg_codec.parse_bytes(payload)
        self.assertEqual(raw[0]["lChildren"][0]["iX"], 510)
        self.assertEqual(raw[0]["lChildren"][0]["iY"], 310)
        reopened = LayoutDocument.from_native_dicts(raw, md5)
        reopened_child = reopened.roots[0].children[0]
        self.assertEqual((reopened_child.x, reopened_child.y), (10, 10))
        self.assertEqual(reopened.abs_position(reopened_child), (510, 310))

    def test_invalid_or_missing_coordinates_are_not_invented(self):
        raw = [{"sWidgetType": "CBox", "iX": "bad", "lChildren": [
            {"sWidgetType": "CBox", "iY": 20, "lChildren": []}
        ]}]
        doc = LayoutDocument.from_native_dicts(raw, None)
        self.assertEqual(doc.to_native_dicts(), raw)
        self.assertNotIn("iX", doc.to_native_dicts()[0]["lChildren"][0])


if __name__ == "__main__":
    unittest.main()
