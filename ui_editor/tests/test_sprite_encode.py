"""普通图片 → 游戏精灵编码：UI 编辑器自己能解、帧数尺寸对。"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image  # noqa: E402

from ui_editor.core import sprite, sprite_encode  # noqa: E402


def _img(w: int, h: int, color) -> Image.Image:
    img = Image.new("RGBA", (w, h), color)
    for x in range(min(3, w)):  # 角上点几笔，避免整帧全透明
        img.putpixel((x, 0), (255, 255, 255, 255))
    return img


class TestSpriteEncode(unittest.TestCase):
    def test_multi_frame_roundtrip_via_ui_decoder(self):
        frames = [_img(10, 6, (200, 30, 30, 255)),
                  _img(8, 6, (30, 30, 200, 255))]
        data = sprite_encode.encode_frames(frames)
        self.assertTrue(sprite.is_sprite(data))
        decoded = sprite.decode_sprite(data)
        self.assertEqual(decoded.frame_count, 2)
        self.assertEqual((decoded.canvas_w, decoded.canvas_h), (10, 6))
        frame0 = decoded.frames[0]
        self.assertEqual((frame0.width, frame0.height), (10, 6))
        self.assertEqual((decoded.frames[1].width,
                          decoded.frames[1].height), (8, 6))

    def test_files_natural_order_and_gif_expand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _img(6, 4, (255, 0, 0, 255)).save(root / "10.png")
            _img(6, 4, (0, 255, 0, 255)).save(root / "02.png")
            gif_frames = [_img(5, 5, (1, 2, 3, 255)),
                          _img(5, 5, (4, 5, 6, 255))]
            gif_frames[0].save(
                root / "anim.gif", save_all=True,
                append_images=gif_frames[1:], duration=80, loop=0)
            data, count = sprite_encode.sprite_bytes_from_files(
                [str(root / "10.png"), str(root / "anim.gif"),
                 str(root / "02.png")])
            # 顺序按文件名：02.png、10.png、anim.gif（展开 2 帧）
            self.assertEqual(count, 4)
            decoded = sprite.decode_sprite(data)
            self.assertEqual(decoded.frame_count, 4)


if __name__ == "__main__":
    unittest.main()
