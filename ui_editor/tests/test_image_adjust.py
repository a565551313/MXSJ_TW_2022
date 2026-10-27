"""0.20.0 批处理核心（纯 Pillow，无 Qt）：缩放/亮度/饱和度/保真护栏。

钉死的规则：
* 尺寸数学（百分比、目标框 fit、拉伸、单边受限、最短 1px）；
* 恒等参数零扰动（像素逐个相等）；
* **alpha 保真**：ImageEnhance 直接混合 RGBA 会把透明像素的 alpha 拉向
  255（游戏精灵全靠透明像素定位）——拆通道增强后 alpha 必须一个等级
  都不动，这是本模块存在的核心理由，单独回归；
* 普通图片按原格式重编码（PNG/JPEG），GIF 与垃圾字节拒收；
* .igs 往返：恒等参数下形状/透明等级全保（I0 的 RGB565 调色板必有
  轻微再量化、按容差断言；T0 是 RGB888、精确色钉死），百分比缩放
  逐帧生效；帧锚点非 (0,0)、魔数不可重编码（T4 等）、非精灵字节
  一律拒收——忠实优先，绝不悄悄挪帧或降级格式。
"""
import io
import struct
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PIL import Image  # noqa: E402

from ui_editor.core import image_adjust, sprite, sprite_encode  # noqa: E402


def png_bytes(size=(8, 6), color=(200, 30, 30, 255)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", size, color).save(buf, format="PNG")
    return buf.getvalue()


def jpeg_bytes(size=(8, 6)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buf, format="JPEG")
    return buf.getvalue()


def frame_image() -> Image.Image:
    """8x6：左上 4x3 不透明红，其余全透明（精灵的典型形态）。"""
    img = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
    for x in range(4):
        for y in range(3):
            img.putpixel((x, y), (200, 30, 30, 255))
    return img


def igs_bytes(magic="I0") -> bytes:
    return sprite_encode.encode_frames([frame_image()], magic)


class AdjustedSizeTests(unittest.TestCase):
    P = staticmethod(image_adjust.AdjustParams)

    def test_none_keeps_size(self):
        self.assertEqual(image_adjust.adjusted_size(8, 6, self.P()), (8, 6))

    def test_percent_scales_both_dims(self):
        p = self.P(scale_mode="percent", percent=200)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (16, 12))

    def test_percent_floor_is_one_pixel(self):
        p = self.P(scale_mode="percent", percent=5)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (1, 1))

    def test_target_fit_keeps_aspect(self):
        p = self.P(scale_mode="target", target_w=40, target_h=40)
        # 8x6 装进 40x40 框：scale=min(5, 6.67)=5 → 40x30
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (40, 30))

    def test_target_stretch_without_keep_aspect(self):
        p = self.P(scale_mode="target", target_w=10, target_h=10,
                   keep_aspect=False)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (10, 10))

    def test_target_one_dim_free(self):
        p = self.P(scale_mode="target", target_w=16, target_h=0)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (16, 12))
        p2 = self.P(scale_mode="target", target_w=0, target_h=12)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p2), (16, 12))

    def test_target_both_zero_is_noop(self):
        p = self.P(scale_mode="target", target_w=0, target_h=0)
        self.assertEqual(image_adjust.adjusted_size(8, 6, p), (8, 6))

    def test_illegal_size_rejected(self):
        with self.assertRaises(image_adjust.AdjustError):
            image_adjust.adjusted_size(0, 6, self.P())

    def test_identity_flag(self):
        self.assertTrue(self.P().is_identity())
        self.assertFalse(self.P(brightness=1.5).is_identity())
        self.assertFalse(self.P(saturation=0.5).is_identity())
        self.assertFalse(self.P(scale_mode="percent").is_identity())


class AdjustImageTests(unittest.TestCase):
    def test_identity_params_pixel_noop(self):
        img = frame_image()
        out = image_adjust.adjust_image(img, image_adjust.AdjustParams())
        self.assertEqual(list(out.getdata()), list(img.getdata()))

    def test_percent_doubles(self):
        out = image_adjust.adjust_image(
            frame_image(),
            image_adjust.AdjustParams(scale_mode="percent", percent=200))
        self.assertEqual(out.size, (16, 12))

    def test_brightness_raises_gray(self):
        img = Image.new("RGB", (2, 2), (100, 100, 100))
        out = image_adjust.adjust_image(
            img, image_adjust.AdjustParams(brightness=1.5))
        self.assertEqual(out.getpixel((0, 0)), (150, 150, 150))

    def test_saturation_zero_grays_red(self):
        img = Image.new("RGB", (2, 2), (200, 30, 30))
        out = image_adjust.adjust_image(
            img, image_adjust.AdjustParams(saturation=0.0))
        r, g, b = out.getpixel((0, 0))
        self.assertEqual((r, g, b), (g, g, g))

    def test_alpha_survives_enhance(self):
        """核心回归：不拆通道的话透明像素 alpha 会被拉向 255。"""
        out = image_adjust.adjust_image(
            frame_image(),
            image_adjust.AdjustParams(brightness=1.5, saturation=0.5))
        self.assertEqual(out.getpixel((7, 5))[3], 0)    # 透明仍全透明
        self.assertEqual(out.getpixel((0, 0))[3], 255)  # 不透明仍不透明

    def test_p_mode_with_transparency_normalizes(self):
        img = Image.new("P", (2, 2))
        img.putpalette([0] * 768)
        img.info["transparency"] = 0
        self.assertEqual(image_adjust.normalize_mode(img).mode, "RGBA")

    def test_l_mode_normalizes_to_rgb(self):
        self.assertEqual(
            image_adjust.normalize_mode(Image.new("L", (2, 2), 7)).mode,
            "RGB")


class ProcessPlainTests(unittest.TestCase):
    def test_png_roundtrip_scaled(self):
        out = image_adjust.process_plain(
            png_bytes(),
            image_adjust.AdjustParams(scale_mode="percent", percent=200))
        with Image.open(io.BytesIO(out)) as img:
            self.assertEqual(img.format, "PNG")
            self.assertEqual(img.size, (16, 12))

    def test_jpeg_stays_jpeg(self):
        out = image_adjust.process_plain(
            jpeg_bytes(), image_adjust.AdjustParams(brightness=1.2))
        with Image.open(io.BytesIO(out)) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertEqual(img.mode, "RGB")

    def test_gif_rejected(self):
        buf = io.BytesIO()
        Image.new("RGB", (4, 4), (255, 0, 0)).convert("P").save(
            buf, format="GIF")
        with self.assertRaises(image_adjust.AdjustError) as ctx:
            image_adjust.process_plain(buf.getvalue(),
                                       image_adjust.AdjustParams())
        self.assertIn("不在批处理范围", str(ctx.exception))

    def test_garbage_rejected(self):
        with self.assertRaises(image_adjust.AdjustError) as ctx:
            image_adjust.process_plain(b"not an image at all",
                                       image_adjust.AdjustParams())
        self.assertIn("无法识别", str(ctx.exception))


class ProcessSpriteTests(unittest.TestCase):
    def test_noop_roundtrip_preserves_shape_and_alpha(self):
        out = image_adjust.process_sprite(igs_bytes(),
                                          image_adjust.AdjustParams())
        spr = sprite.decode_sprite(out)
        self.assertEqual(spr.magic, "I0")
        self.assertEqual(len(spr.frames), 1)
        frame = spr.frames[0]
        self.assertEqual((frame.width, frame.height), (8, 6))
        img = Image.frombytes("RGBA", (8, 6), frame.rgba)
        self.assertEqual(img.getpixel((7, 5)), (0, 0, 0, 0))   # 透明仍透明
        self.assertEqual(img.getpixel((0, 0))[3], 255)         # 不透明仍不透明
        # I0 是 RGB565 调色板：重编码必有轻微再量化（步长 ≤8.2/4/8.2），
        # 颜色按容差断言；精确色由 T0（RGB888）用例钉死。
        r, g, b, _a = img.getpixel((0, 0))
        self.assertAlmostEqual(r, 200, delta=5)
        self.assertAlmostEqual(g, 30, delta=5)
        self.assertAlmostEqual(b, 30, delta=5)

    def test_percent_scales_frames(self):
        out = image_adjust.process_sprite(
            igs_bytes(),
            image_adjust.AdjustParams(scale_mode="percent", percent=200))
        frame = sprite.decode_sprite(out).frames[0]
        self.assertEqual((frame.width, frame.height), (16, 12))

    def test_t0_noop_roundtrip_exact_colors(self):
        """T0 是 RGB888 调色板：恒等往返精确保色（I0 的 RGB565 做不到）。"""
        out = image_adjust.process_sprite(igs_bytes("T0"),
                                          image_adjust.AdjustParams())
        spr = sprite.decode_sprite(out)
        self.assertEqual(spr.magic, "T0")
        img = Image.frombytes("RGBA", (8, 6), spr.frames[0].rgba)
        self.assertEqual(img.getpixel((0, 0)), (200, 30, 30, 255))
        self.assertEqual(img.getpixel((7, 5)), (0, 0, 0, 0))

    def test_nonzero_anchor_rejected(self):
        data = bytearray(igs_bytes())
        struct.pack_into("<H", data, 14, 3)   # 首帧锚点 kx：0 → 3
        with self.assertRaises(image_adjust.AdjustError) as ctx:
            image_adjust.process_sprite(bytes(data),
                                        image_adjust.AdjustParams())
        self.assertIn("锚点", str(ctx.exception))

    def test_unencodable_magic_rejected(self):
        fake = sprite.Sprite(
            magic="T4", frame_count=1, canvas_w=8, canvas_h=6,
            frames=[sprite.SpriteFrame(8, 6, b"\x00" * 192)])
        with mock.patch("ui_editor.core.sprite.decode_sprite",
                        return_value=fake):
            with self.assertRaises(image_adjust.AdjustError) as ctx:
                image_adjust.process_sprite(igs_bytes(),
                                            image_adjust.AdjustParams())
        self.assertIn("只能编码 I0/T0/I1", str(ctx.exception))

    def test_garbage_sprite_rejected(self):
        with self.assertRaises(image_adjust.AdjustError) as ctx:
            image_adjust.process_sprite(b"garbage bytes, not a sprite",
                                        image_adjust.AdjustParams())
        self.assertIn("不是可解码的精灵", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
