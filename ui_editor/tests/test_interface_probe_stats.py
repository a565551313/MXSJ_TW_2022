"""interface_probe 的新增统计（图片头尺寸 / 切片尺寸 / 按钮状态摸底，无 Qt）。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import interface_probe as probe  # noqa: E402


def png(width: int, height: int) -> bytes:
    return (b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
            + width.to_bytes(4, "big") + height.to_bytes(4, "big"))


def gif(width: int, height: int) -> bytes:
    return b"GIF89a" + width.to_bytes(2, "little") + height.to_bytes(2, "little")


def jpeg(width: int, height: int) -> bytes:
    app0 = b"\xff\xe0" + (16).to_bytes(2, "big") + b"JFIF\x00" + b"\x00" * 9
    sof = (b"\xff\xc0" + (17).to_bytes(2, "big") + b"\x08"
           + height.to_bytes(2, "big") + width.to_bytes(2, "big")
           + b"\x03" + b"\x00" * 9)
    return b"\xff\xd8" + app0 + sof


class FakePack:
    def __init__(self, files):
        self.files = files

    def contains(self, name):
        return name in self.files

    def read_named(self, name):
        return self.files.get(name)


class TestImageSize(unittest.TestCase):
    def test_png_gif_jpeg(self):
        self.assertEqual(probe.image_size(png(48, 24)), (48, 24))
        self.assertEqual(probe.image_size(gif(12, 30)), (12, 30))
        self.assertEqual(probe.image_size(jpeg(64, 32)), (64, 32))

    def test_unknown_returns_none(self):
        self.assertIsNone(probe.image_size(b"not an image"))
        self.assertIsNone(probe.image_size(b""))


class TestSliceStats(unittest.TestCase):
    def test_piece_sizes_are_reported(self):
        """切片尺寸来自资源本身：这是「切割线」的唯一证据。"""
        pack = FakePack({
            "f\\top/left.png": png(9, 7),
            "f\\top.png": png(20, 7),
            "f\\top/right.png": png(11, 7),
        })
        plans = {"f\\": {"kind": "h_slice",
                         "pieces": ["f\\top/left.png", "f\\top.png",
                                    "f\\top/right.png"]}}
        stats = probe.slice_stats(pack, None, plans)
        self.assertEqual(stats["families"], {"h_slice": 1})
        sizes = stats["samples"][0]["sizes"]
        self.assertEqual(sizes["f\\top/left.png"], (9, 7))
        self.assertEqual(sizes["f\\top/right.png"], (11, 7))

    def test_non_slice_families_are_ignored(self):
        plans = {"a\\": {"kind": "frames", "pieces": ["a\\0.png"]}}
        stats = probe.slice_stats(FakePack({}), None, plans)
        self.assertEqual(stats["families"], {})


class TestButtonStateStats(unittest.TestCase):
    def test_counts_state_fields_and_ratios(self):
        pack = FakePack({"b.png": png(60, 40)})
        layouts = [{
            "sWidgetType": "CMainFrame", "lChildren": [
                {"sWidgetType": "CButton", "sFileName": "b.png",
                 "iHeight": 20},
                {"sWidgetType": "CButton", "sFileName": "b.png",
                 "iHeight": 20, "sDownImageName": "b2.png",
                 "sMouseOverImageName": "b3.png"},
            ]}]
        stats = probe.button_state_stats(layouts, pack, None)
        self.assertEqual(stats["state_fields"],
                         {"sDownImageName": 1, "sMouseOverImageName": 1})
        self.assertEqual(stats["height_ratio"], {2.0: 2})

    def test_dir_base_buttons_are_skipped(self):
        layouts = [{"sWidgetType": "CButton", "sFileName": "dir\\",
                    "iHeight": 20}]
        stats = probe.button_state_stats(layouts, FakePack({}), None)
        self.assertEqual(stats["height_ratio"], {})


if __name__ == "__main__":
    unittest.main()
