"""M3.2 按钮状态取图判定（帧/竖条/模拟）纯逻辑测试。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.painters import state_slice  # noqa: E402


class TestStateSlice(unittest.TestCase):
    def test_prefers_sprite_frame(self):
        self.assertEqual(
            state_slice(80, 24, 80, 24, frame_count=4, state_idx=2),
            ("frame", 2))

    def test_vertical_strip_when_no_frames(self):
        # 80x72 单图、按钮 80x24 → 三段竖条，第 1 段（按下）
        self.assertEqual(
            state_slice(80, 72, 80, 24, frame_count=1, state_idx=1),
            ("strip", (0, 24, 80, 24)))

    def test_strip_index_out_of_range_falls_back(self):
        self.assertIsNone(
            state_slice(80, 48, 80, 24, frame_count=1, state_idx=3))

    def test_plain_image_simulated(self):
        self.assertIsNone(
            state_slice(80, 24, 80, 24, frame_count=1, state_idx=1))


if __name__ == "__main__":
    unittest.main()
