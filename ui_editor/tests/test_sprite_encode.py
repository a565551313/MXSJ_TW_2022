"""普通图片 → 游戏精灵编码：UI 编辑器自己能解、帧数尺寸对。"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image  # noqa: E402

from ui_editor.core import sprite, sprite_encode  # noqa: E402
from ui_editor.core.errors import Cancelled  # noqa: E402


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


class TestFrameFileHooks(unittest.TestCase):
    """批量转精灵的进度/取消钩子（忙碌遮罩接入用）。"""

    class Recorder:
        def __init__(self):
            self.calls = []

        def report(self, done, total, text):
            self.calls.append((done, total, text))

    def _files(self, root: Path, n: int = 3) -> list[str]:
        paths = []
        for i in range(n):
            path = root / f"{i:02d}.png"
            _img(6, 4, (i * 40, 90, 120, 255)).save(path)
            paths.append(str(path))
        return paths

    def test_load_frame_files_progress_to_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._files(root, 3)
            rec = TestFrameFileHooks.Recorder()
            frames = sprite_encode.load_frame_files(paths, progress=rec.report)
            self.assertEqual(len(frames), 3)
            self.assertTrue(rec.calls)
            self.assertEqual({c[1] for c in rec.calls}, {3})
            self.assertEqual(rec.calls[-1][0], 2)  # done 从 0 起报，收尾 n-1

    def test_load_frame_files_cancel_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._files(root, 3)

            def stop():
                return True

            with self.assertRaises(Cancelled):
                sprite_encode.load_frame_files(paths, cancelled=stop)

    def test_sprite_bytes_from_files_passes_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._files(root, 2)
            rec = TestFrameFileHooks.Recorder()
            data, count = sprite_encode.sprite_bytes_from_files(
                paths, progress=rec.report, cancelled=lambda: False)
            self.assertEqual(count, 2)
            self.assertTrue(sprite.is_sprite(data))
            self.assertTrue(rec.calls)


class TestDirectColorSprites(unittest.TestCase):
    """T4/T5 真彩精灵（无调色板、token 后跟 RGB；与资源编辑器同源）。

    2026-10-14 在真实 item.fls 样本上定版，UI 编辑器挂载
    item.fls 取图时同样会碰到，先解码再喂 QImage 的路径须通。
    """

    @staticmethod
    def _bytes(magic: bytes) -> bytes:
        import struct

        rows = [
            bytes([0xC1, 0x42, 255, 0, 0, 0, 255, 0,
                   0x30, 0, 0, 255, 0x00]),
            bytes([0x02, 31, 10, 20, 30, 0x82, 200, 100, 50, 0x00]),
        ]
        pad = (-sum(len(r) for r in rows)) % 4
        rows[-1] += b"\x00" * pad
        lens = [len(r) for r in rows]
        out = struct.pack("<2sHHHHHH", magic, 1, 1, 4, 2, 0, 0)
        out += struct.pack("<HHHH", 0, 0, 4, 2)
        out += struct.pack("<I", 2)
        if magic == b"T5":
            out += b"".join(struct.pack("<H", n) for n in lens)
        else:
            out += bytes(lens)
        return out + b"".join(rows)

    def test_t4_t5_decode(self):
        for magic in (b"T4", b"T5"):
            with self.subTest(magic=magic):
                data = self._bytes(magic)
                self.assertTrue(sprite.is_sprite(data))
                decoded = sprite.decode_sprite(data)
                self.assertEqual(decoded.frame_count, 1)
                frame = decoded.frames[0]
                self.assertEqual((frame.width, frame.height), (4, 2))
                rgba = frame.rgba

                def px(x, y, rgba=rgba):
                    i = (y * 4 + x) * 4
                    return tuple(rgba[i:i + 4])

                self.assertEqual(px(0, 0), (0, 0, 0, 0))
                self.assertEqual(px(1, 0), (255, 0, 0, 255))
                self.assertEqual(px(3, 0), (0, 0, 255, 16 * 255 // 31))
                self.assertEqual(px(0, 1), (10, 20, 30, 255))
                self.assertEqual(px(3, 1), (200, 100, 50, 255))


class TestI4DirectColor(unittest.TestCase):
    """I4 = 行内 2 字节 RGB565、无调色板的真彩精灵。

    2026-10-20 在 interface.fls 的 .igs 上定版：``combdialog2\\杂图\\
    聊天气泡左\\`` / ``聊天底图\\right\\`` 的九片与
    ``combdialog\\游戏知道\\三宫\\知道蓝分割线\\`` 的横三片全是 I4。
    夹具就是包里的原始字节（逐字节抄录），断言尺寸与颜色。
    """

    #: combdialog\\游戏知道\\三宫\\知道蓝分割线\\left.igs（50×2，整片纯蓝）
    BLUE = bytes.fromhex(
        "49340100010032000200000000000000000032000200020000000404"
        "b2bc0400b2bc0400")

    def test_i4_decodes_rgb565(self):
        data = self.BLUE
        self.assertTrue(sprite.is_sprite(data))
        decoded = sprite.decode_sprite(data)
        self.assertEqual(decoded.magic, "I4")
        frame = decoded.frames[0]
        self.assertEqual((frame.width, frame.height), (50, 2))
        # 0x04bc → RGB565 小端 → (0, 149, 230)，与「蓝分割线」的命名相符
        for index in (0, 49 * 4):
            self.assertEqual(tuple(frame.rgba[index:index + 4]),
                             (0, 149, 230, 255))

    def test_i4_with_truncated_row_is_not_mistaken_for_3byte(self):
        """按 3 字节 RGB 解会把行读穿：解析器必须按 DIRECT_COLOR_BYTES 取 2。"""
        from ui_editor.core.sprite_format import DIRECT_COLOR_BYTES
        self.assertEqual(DIRECT_COLOR_BYTES[b"I4"], 2)
        self.assertEqual(DIRECT_COLOR_BYTES[b"T4"], 3)


class TestT1PaletteWide(unittest.TestCase):
    """T1 = T0 的 u16 行长变体（调色板 256×RGB888）。

    2026-10-19 在 interface.fls 的 .spr 姊媚精灵（烟2_.igs 等 21 例）
    上按「Σ行长=像素流长」定版；u8 假说被 Σ 精确相等否证。
    """

    @staticmethod
    def _bytes() -> bytes:
        import struct

        rows = [
            bytes([0xC1, 0x42, 0x07, 0x08, 0x2F, 0x09, 0x00]),
            bytes([0x02, 0x1F, 0x05, 0x82, 0x06, 0x00]),
        ]
        pad = (-sum(len(r) for r in rows)) % 4
        rows[-1] += b"\x00" * pad
        lens = [len(r) for r in rows]
        pal = bytearray()
        for i in range(256):
            pal += bytes((i, (2 * i) & 0xFF, 255 - i))
        out = struct.pack("<2sHHHHHH", b"T1", 1, 1, 4, 2, 0, 0)
        out += struct.pack("<HHHH", 0, 0, 4, 2)
        out += struct.pack("<I", 2)
        out += b"".join(struct.pack("<H", n) for n in lens)  # T1：u16 行长
        out += bytes(pal)
        return out + b"".join(rows)

    def test_t1_decode(self):
        data = self._bytes()
        self.assertTrue(sprite.is_sprite(data))
        decoded = sprite.decode_sprite(data)
        self.assertEqual(decoded.frame_count, 1)
        frame = decoded.frames[0]
        self.assertEqual((frame.width, frame.height), (4, 2))
        rgba = frame.rgba

        def px(x, y, rgba=rgba):
            i = (y * 4 + x) * 4
            return tuple(rgba[i:i + 4])

        self.assertEqual(px(0, 0), (0, 0, 0, 0))
        self.assertEqual(px(1, 0), (7, 14, 248, 255))
        self.assertEqual(px(2, 0), (8, 16, 247, 255))
        self.assertEqual(px(3, 0), (9, 18, 246, 15 * 255 // 31))
        self.assertEqual(px(0, 1), (5, 10, 250, 255))
        self.assertEqual(px(2, 1), (6, 12, 249, 255))


if __name__ == "__main__":
    unittest.main()
