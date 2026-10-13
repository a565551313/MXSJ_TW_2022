"""精灵编解码测试：真实包全量解码 + 编码往返像素一致。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PIL import Image  # noqa: E402

from resource_editor.core.codecs import detect  # noqa: E402
from resource_editor.core.codecs.sprite import (  # noqa: E402
    EncodeError,
    decode_sprite,
    encode_sprite,
    sprite_bytes_from_files,
)
from resource_editor.core.model.document import PackDocument  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"


def _sprites_of(pack: str):
    doc = PackDocument.open(DATA_DIR / pack)
    for i in range(doc.count):
        if doc.entry_kind(i) is detect.EntryKind.SPRITE:
            yield i, doc.content(i)


@unittest.skipUnless(DATA_DIR.exists(), "缺少 data 目录")
class TestDecodeRealSprites(unittest.TestCase):
    def test_all_sprites_decode(self):
        total = 0
        for pack in ("skill.fls", "skill2.fls", "passive.fls", "effect.fls"):
            for _i, payload in _sprites_of(pack):
                sprite = decode_sprite(payload)
                self.assertGreater(sprite.frame_count, 0)
                total += 1
        self.assertEqual(total, 807)


@unittest.skipUnless(DATA_DIR.exists(), "缺少 data 目录")
class TestEncodeRoundtrip(unittest.TestCase):
    def _roundtrip(self, pack: str, index: int):
        doc = PackDocument.open(DATA_DIR / pack)
        sprite = decode_sprite(doc.content(index))
        images = [sprite.render_frame(fi) for fi in range(sprite.frame_count)]
        keys = [(f[0], f[1]) for f in sprite.frames]
        encoded, _pal, report = encode_sprite(
            images, keys, sprite.canvas_w, sprite.canvas_h,
            sprite.center_x, sprite.center_y,
            magic=sprite.magic, base_palette=sprite.palette,
        )
        back = decode_sprite(encoded)
        for fi in range(sprite.frame_count):
            self.assertEqual(
                back.render_frame(fi).tobytes(), images[fi].tobytes(),
                msg=f"{pack}[{index}] 帧 {fi} 往返不一致",
            )
        self.assertEqual(report.pixels_over_tolerance, 0)

    def test_roundtrip_samples(self):
        for pack, index in (("skill.fls", 0), ("skill.fls", 10),
                            ("skill2.fls", 3), ("passive.fls", 5),
                            ("effect.fls", 0), ("effect.fls", 38)):
            with self.subTest(pack=pack, index=index):
                self._roundtrip(pack, index)


class TestEncodeSynthetic(unittest.TestCase):
    def test_wide_row_overflow_i0(self):
        # 红蓝交替的不透明行会产生 >255 字节的行，I0(u8 行长) 必须拒绝
        img = Image.new("RGBA", (300, 2), (0, 0, 0, 0))
        for x in range(300):
            img.putpixel((x, 0), (255, 0, 0, 255) if x % 2 else (0, 0, 255, 255))
        with self.assertRaises(EncodeError):
            encode_sprite([img], [(0, 0)], 300, 2, 0, 0, magic="I0")
        # 全透明宽行只有 EOL，合法
        blank = Image.new("RGBA", (300, 2), (0, 0, 0, 0))
        encode_sprite([blank], [(0, 0)], 300, 2, 0, 0, magic="I0")

    def test_i1_wide(self):
        img = Image.new("RGBA", (300, 3), (255, 0, 0, 255))
        img.putpixel((10, 1), (0, 0, 255, 128))
        encoded, _pal, report = encode_sprite(
            [img], [(0, 0)], 300, 3, 0, 0, magic="I1")
        back = decode_sprite(encoded)
        self.assertEqual(back.magic, "I1")
        self.assertEqual(back.render_frame(0).size, (300, 3))
        # alpha 量化到 31 级，固有误差不超过半级（255/31/2≈4.1）
        self.assertLessEqual(report.max_alpha_error, 4)


if __name__ == "__main__":
    unittest.main()


class TestSpriteFromFiles(unittest.TestCase):
    """多帧文件转精灵：自然序成帧、解码帧数与尺寸一致。"""

    def test_two_frames_roundtrip(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new("RGBA", (9, 5), (10, 200, 30, 255)).save(
                root / "02.png")
            Image.new("RGBA", (7, 5), (200, 30, 30, 255)).save(
                root / "01.png")
            data, count, _report = sprite_bytes_from_files(
                [str(root / "02.png"), str(root / "01.png")])
            self.assertEqual(count, 2)
            decoded = decode_sprite(data)
            self.assertEqual(decoded.frame_count, 2)
            # 01.png 在前：画布取最大帧尺寸 9x5
            self.assertEqual((decoded.canvas_w, decoded.canvas_h), (9, 5))
