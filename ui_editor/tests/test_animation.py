"""动画模型回归：保留非连续帧号和时长。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.animation import build_animation  # noqa: E402


class TestAnimationModel(unittest.TestCase):
    def test_non_contiguous_frame_ids_keep_duration(self):
        first, second, third = object(), object(), object()
        asset = build_animation(
            "effect/test.spr",
            ((0, 5), (2, 9), (10, 12)),
            [first, second, third],
        )
        self.assertEqual(
            [(frame.frame_id, frame.duration) for frame in asset.frames],
            [(0, 5), (2, 9), (10, 12)],
        )
        self.assertIs(asset.frames[1].image, third)
        self.assertIs(asset.frames[2].image, None)
        self.assertFalse(asset.complete)

    def test_empty_table_uses_image_order(self):
        images = [object(), object()]
        asset = build_animation("x.spr", (), images)
        self.assertEqual([frame.frame_id for frame in asset.frames], [0, 1])
        self.assertEqual(asset.images, tuple(images))


if __name__ == "__main__":
    unittest.main()
