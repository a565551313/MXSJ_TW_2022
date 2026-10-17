"""多实现同源回归：精灵格式在两个编辑器里的落点必须给出同一结果。

`ui_editor/core/sprite.py`（无 Pillow，输出 RGBA 字节）与
`resource_editor/core/codecs/sprite.py`（Pillow 落点）曾各自演化、靠 docstring
声明「保持一致」（`docs/analysis/ui_editor_analysis_20261016.md` P1-2）。
本测试用三种输入交叉验证：**仓库里的真实精灵**、两边编码器产出的字节、
手工构造的真彩（T4）流。格式常量另由 `mx_common/sprite_format.py` 统一，
其语义（alpha 折算）在这里对旧公式逐点钉住。

跑法：`python3 -m unittest discover -s tools/devkit/tests`
"""

from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
for rel in ("ui_editor/src", "resource_editor/src"):
    path = str(REPO_ROOT / rel)
    if path not in sys.path:
        sys.path.insert(0, path)

import ui_editor.core.sprite as ui_sprite  # noqa: E402
import ui_editor.core.sprite_encode as ui_encode  # noqa: E402
from PIL import Image  # noqa: E402  (资源编辑器编码路径依赖 Pillow)
from resource_editor.core.codecs import sprite as res_sprite  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.sprite_format import (  # noqa: E402
    ALPHA_LEVELS,
    OPAQUE,
    alpha_to_level,
    level_to_alpha,
)

SKILL_PACK = REPO_ROOT / "data" / "skill.fls"


def to_rgba(img: Image.Image) -> bytes:
    """PIL → RGBA 字节；alpha=0 的像素一律归零（两边解码器都这么输出）。"""
    raw = bytearray(img.convert("RGBA").tobytes())
    for i in range(0, len(raw), 4):
        if raw[i + 3] == 0:
            raw[i] = raw[i + 1] = raw[i + 2] = 0
    return bytes(raw)


def ui_frames(data: bytes) -> list[tuple[int, int, bytes]]:
    """UI 落点：[(宽, 高, RGBA 字节), ...]（alpha=0 时 RGB 已为 0）。"""
    decoded = ui_sprite.decode_sprite(data)
    return [(f.width, f.height, f.rgba) for f in decoded.frames]


def res_frames(data: bytes) -> list[tuple[int, int, bytes]]:
    """资源编辑器落点：[(宽, 高, RGBA 字节), ...]（SKIP 像素涂成 (0,0,0,0)）。"""
    decoded = res_sprite.decode_sprite(data)
    out: list[tuple[int, int, bytes]] = []
    for index in range(len(decoded.frames)):
        image = decoded.render_frame(index)
        _kx, _ky, width, height = decoded.frames[index]
        out.append((width, height, to_rgba(image)))
    return out


def make_image(width: int, height: int, pixels: list[tuple[int, int, int, int]]):
    """按行主序像素表造 RGBA 图（长度必须 = width * height）。"""
    assert len(pixels) == width * height
    image = Image.new("RGBA", (width, height))
    image.putdata(pixels)
    return image


def q5(value: int) -> int:
    """5 位量化取整值（R/B 通道）——用于构造无损往返的测试色。"""
    return round(value * 31 / 255) * 255 // 31


def q6(value: int) -> int:
    """6 位量化取整值（G 通道）。"""
    return round(value * 63 / 255) * 255 // 63


def first_sprite_bytes(pack_path: Path) -> bytes:
    """从真实 0SLF 包里取第一条精灵字节（按魔数判定）。"""
    with FlsPack(pack_path) as pack:
        for entry_id in pack.entry_ids:
            data = pack.read_id(entry_id)
            if data and data[:2] in ui_sprite.MAGICS:
                return data
    raise AssertionError(f"{pack_path} 里没有精灵条目")


class RealSpriteParityTests(unittest.TestCase):
    """仓库内真实精灵（唯一一份：`data/skill.fls` 里的 I0）。"""

    @classmethod
    def setUpClass(cls):
        if not SKILL_PACK.is_file():
            raise unittest.SkipTest(f"缺少真实资源包：{SKILL_PACK}")
        cls.data = first_sprite_bytes(SKILL_PACK)

    def test_both_decoders_agree_frame_by_frame(self):
        ui = ui_frames(self.data)
        res = res_frames(self.data)
        self.assertEqual(len(ui), len(res))
        self.assertGreater(len(ui), 0)
        for index, (a, b) in enumerate(zip(ui, res, strict=True)):
            self.assertEqual(a, b, f"第 {index} 帧两个解码器不一致")

    def test_metadata_and_pixel_shape(self):
        ui = ui_sprite.decode_sprite(self.data)
        res = res_sprite.decode_sprite(self.data)
        self.assertEqual(ui.magic, res.magic)
        self.assertEqual(ui.canvas_w, res.canvas_w)
        self.assertEqual(ui.canvas_h, res.canvas_h)
        self.assertEqual(ui.frame_count, res.frame_count)
        for width, height, rgba in ui_frames(self.data):
            self.assertEqual(len(rgba), width * height * 4)


class EncoderCrossTests(unittest.TestCase):
    """两边编码器产出的字节，必须都能被两边解码器读出同一结果。"""

    def build(self):
        # 2×2：不透明红、全透明、不透明绿、半透明蓝（等级 16 = level_to_alpha）
        half = level_to_alpha(16)
        pixels = [(q5(255), q6(0), q5(0), OPAQUE),
                  (q5(0), q6(0), q5(0), 0),
                  (q5(0), q6(255), q5(0), OPAQUE),
                  (q5(0), q6(0), q5(255), half)]
        return make_image(2, 2, pixels)

    def assert_decodes_to(self, data: bytes, expected: list[tuple[int, int, bytes]]):
        ui = ui_frames(data)
        res = res_frames(data)
        self.assertEqual(ui, res, "两个解码器对同一字节流给出不同结果")
        self.assertEqual(ui, expected, "解码结果与源图不符（非格式近似，属不一致）")

    def test_ui_encoder_output(self):
        image = self.build()
        data = ui_encode.encode_frames([image], "I0")
        expected = [(2, 2, to_rgba(image))]
        self.assert_decodes_to(data, expected)

    def test_resource_encoder_output(self):
        image = self.build()
        data, _palette, _report = res_sprite.encode_sprite(
            [image], [(0, 0)], 2, 2, 0, 0, magic="I0")
        expected = [(2, 2, to_rgba(image))]
        self.assert_decodes_to(data, expected)

    def test_wide_image_falls_back_to_i1_and_stays_parity(self):
        width, height = 200, 2
        pixels = [(q5(255), q6(255), q5(255), OPAQUE)] * (width * height)
        image = make_image(width, height, pixels)
        ui_data = ui_encode.encode_frames([image], "I1")
        res_data, _palette, _report = res_sprite.encode_sprite(
            [image], [(0, 0)], width, height, 0, 0, magic="I1")
        expected = [(width, height, to_rgba(image))]
        self.assertEqual(ui_data[:2], b"I1")
        self.assert_decodes_to(ui_data, expected)
        self.assert_decodes_to(res_data, expected)


class TrueColorParityTests(unittest.TestCase):
    """T4（真彩、行长 u8）没有一个仓库内编码器，手工构造后两边都得读对。"""

    def build_t4(self) -> tuple[bytes, bytes]:
        rgb = (0x11, 0x22, 0x33), (0x44, 0x55, 0x66)
        row = bytes([0x40 | 2]) + b"".join(bytes(c) for c in rgb) + b"\x00"
        padded = row + b"\x00" * (-len(row) % 4)
        out = bytearray()
        out += struct.pack("<2sHHHHHH", b"T4", 1, 1, 2, 1, 0, 0)
        out += struct.pack("<HHHH", 0, 0, 2, 1)
        out += struct.pack("<I", 1)              # 总行数
        out += struct.pack("<B", len(padded))    # T4 行长表是 u8
        out += padded
        expected = b"".join(bytes(c) + b"\xff" for c in rgb)
        return bytes(out), expected

    def test_both_decoders_read_direct_color(self):
        data, expected = self.build_t4()
        ui = ui_frames(data)
        res = res_frames(data)
        self.assertEqual(ui, res)
        self.assertEqual(ui, [(2, 1, expected)])


class AlphaHelperTests(unittest.TestCase):
    """共享真源里的 alpha 折算必须与两个编辑器原先的私有公式逐点等值。"""

    @staticmethod
    def old_level_to_alpha(level: int) -> int:
        return level * 255 // 31

    @staticmethod
    def old_alpha_to_level(alpha: int) -> int:
        if alpha >= 255:
            return 255
        if alpha <= 0:
            return 0
        return max(1, min(30, round(alpha * 31 / 255)))

    def test_level_to_alpha_matches_old_formula(self):
        for level in range(ALPHA_LEVELS):
            with self.subTest(level=level):
                self.assertEqual(level_to_alpha(level),
                                 self.old_level_to_alpha(level))

    def test_alpha_to_level_matches_old_formula(self):
        for alpha in range(256):
            with self.subTest(alpha=alpha):
                self.assertEqual(alpha_to_level(alpha),
                                 self.old_alpha_to_level(alpha))

    def test_editors_use_the_shared_helpers(self):
        """编辑器里的私有名必须是本包共享模块的别名，而不是各自另写的副本。"""
        from resource_editor.core.sprite_format import (
            alpha_to_level as res_alpha,
        )
        from resource_editor.core.sprite_format import (
            level_to_alpha as res_level,
        )
        from ui_editor.core.sprite_format import (
            alpha_to_level as ui_alpha,
        )
        from ui_editor.core.sprite_format import (
            level_to_alpha as ui_level,
        )

        self.assertIs(ui_encode._alpha_to_level, ui_alpha)
        self.assertIs(res_sprite._alpha_to_level, res_alpha)
        self.assertIs(res_sprite._level_to_alpha, res_level)
        # 两份副本（各编辑器一份）必须等值：vendor 之后被手改就会在这里红
        for value in range(256):
            self.assertEqual(ui_alpha(value), res_alpha(value))
        for value in range(ALPHA_LEVELS):
            self.assertEqual(ui_level(value), res_level(value))
        self.assertEqual(alpha_to_level(254), res_alpha(254))
        self.assertEqual(res_sprite.OPAQUE, OPAQUE)
        self.assertEqual(res_sprite.SPRITE_MAGICS, ui_sprite.MAGICS)


if __name__ == "__main__":
    unittest.main()
