"""原生 .dlg 与编辑器内部统一使用父相对坐标的边界测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec  # noqa: E402
from ui_editor.core.model import LayoutDocument  # noqa: E402


def native_layout(child_x: int = 10, child_y: int = 10) -> list[dict]:
    return [{
        "sWidgetType": "CMainFrame", "sName": "A",
        "iX": 500, "iY": 300, "iWidth": 800, "iHeight": 600,
        "lChildren": [{
            "sWidgetType": "CTextFrameEx", "sName": "B",
            "iX": child_x, "iY": child_y, "iWidth": 100, "iHeight": 100,
            "sText": "原生坐标", "lChildren": [{
                "sWidgetType": "CBox", "sName": "C",
                "iX": 10, "iY": 10,
                "iWidth": 20, "iHeight": 20, "lChildren": [],
            }],
        }],
    }]


class TestNativeCoordinates(unittest.TestCase):
    def test_load_preserves_each_native_child_parent_relative_position(self):
        doc = LayoutDocument.from_native_dicts(native_layout(), None)
        root = doc.roots[0]
        child = root.children[0]
        grandchild = child.children[0]
        self.assertEqual((child.x, child.y), (10, 10))
        self.assertEqual(doc.abs_position(child), (510, 310))
        self.assertEqual((grandchild.x, grandchild.y), (10, 10))
        self.assertEqual(doc.abs_position(grandchild), (520, 320))
        self.assertEqual(doc.to_native_dicts(), native_layout())

    def test_editor_example_writes_10_10_not_absolute_510_310(self):
        doc = LayoutDocument.from_native_dicts(native_layout(), None)
        child = doc.roots[0].children[0]
        child.set_geometry(x=10, y=10)
        native = doc.to_native_dicts()
        saved_child = native[0]["lChildren"][0]
        self.assertEqual((saved_child["iX"], saved_child["iY"]), (10, 10))
        self.assertNotEqual((saved_child["iX"], saved_child["iY"]), (510, 310))

    def test_real_shaped_native_child_does_not_jump_on_load_or_resave(self):
        # 真包 dialog/equip/bagua_takeout.dlg 的代表性父子坐标：
        # 父 (247,88)，子 (43,117) 是父内偏移，不是画布绝对位置。
        original = native_layout(child_x=43, child_y=117)
        original[0]["iX"], original[0]["iY"] = 247, 88
        doc = LayoutDocument.from_native_dicts(original, None)
        child = doc.roots[0].children[0]
        self.assertEqual((child.x, child.y), (43, 117))
        self.assertEqual(doc.abs_position(child), (290, 205))
        self.assertEqual(doc.to_native_dicts(), original)
        reopened = LayoutDocument.from_native_dicts(doc.to_native_dicts(), None)
        self.assertEqual(reopened.to_native_dicts(), original)

    def test_negative_child_offset_is_native_relative_data_not_offscreen(self):
        # 真包 dialog/give/give_appearance.dlg 的 btn_down=(-16,2)。
        original = native_layout(child_x=-16, child_y=2)
        original[0]["iX"], original[0]["iY"] = 355, 316
        doc = LayoutDocument.from_native_dicts(original, None)
        child = doc.roots[0].children[0]
        self.assertEqual((child.x, child.y), (-16, 2))
        self.assertEqual(doc.abs_position(child), (339, 318))
        self.assertEqual(doc.to_native_dicts(), original)

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
        self.assertEqual(raw[0]["lChildren"][0]["iX"], 10)
        self.assertEqual(raw[0]["lChildren"][0]["iY"], 10)
        reopened = LayoutDocument.from_native_dicts(raw, md5)
        reopened_child = reopened.roots[0].children[0]
        self.assertEqual((reopened_child.x, reopened_child.y), (10, 10))
        self.assertEqual(reopened.abs_position(reopened_child), (510, 310))

    def test_missing_intermediate_coordinates_are_not_invented(self):
        raw = [{"sWidgetType": "CMainFrame", "iX": 500, "iY": 300,
                "lChildren": [{"sWidgetType": "CBox", "iY": "bad",
                               "lChildren": [{"sWidgetType": "CBox",
                                              "iX": 520, "iY": 320,
                                              "lChildren": []}]}]}]
        doc = LayoutDocument.from_native_dicts(raw, None)
        child = doc.roots[0].children[0]
        grandchild = child.children[0]
        self.assertNotIn("iX", child.props)
        self.assertEqual(child.props["iY"], "bad")
        self.assertEqual((grandchild.x, grandchild.y), (520, 320))
        self.assertEqual(doc.to_native_dicts(), raw)

    def test_invalid_or_missing_coordinates_are_not_invented(self):
        raw = [{"sWidgetType": "CBox", "iX": "bad", "lChildren": [
            {"sWidgetType": "CBox", "iY": 20, "lChildren": []}
        ]}]
        doc = LayoutDocument.from_native_dicts(raw, None)
        self.assertEqual(doc.to_native_dicts(), raw)
        self.assertNotIn("iX", doc.to_native_dicts()[0]["lChildren"][0])


if __name__ == "__main__":
    unittest.main()
