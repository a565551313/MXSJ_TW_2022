"""资源解析测试：自建微型 0SLF 包（含明文 lst、精灵、XOR 布局）。"""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec  # noqa: E402
from ui_editor.core.assets import AssetResolver, unpack_packed_text  # noqa: E402
from ui_editor.core.mxhash import mx_hash  # noqa: E402

MASK = 0xFFFFFFFF


def _record(index, entry_id, r1, clen, doff):
    r2 = (((r1 * entry_id + 0x0DF25E) & MASK) ^ clen) & MASK
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ doff) & MASK
    return struct.pack("<IIII", entry_id, r1, r2, r3)


def build_pack(entries):
    body = bytearray()
    meta = []
    offset = 12
    for name, payload in entries:
        meta.append((mx_hash(name.encode("gbk")), 12345, len(payload), offset))
        body += payload
        offset += len(payload)
    head = b"0SLF" + struct.pack("<II", len(entries), offset)
    directory = b"".join(_record(i, *m) for i, m in enumerate(meta))
    return head + bytes(body) + directory


def make_sprite() -> bytes:
    palette = bytearray(512)
    struct.pack_into("<H", palette, 5 * 2, 0xF800)  # 红
    struct.pack_into("<H", palette, 7 * 2, 0x07E0)  # 绿
    row1 = bytes([0x42, 5, 7])             # LIT 两像素：红、绿
    row2 = bytes([0x82, 7, 0, 0, 0])       # REP 两像素绿 + 对齐填充
    return (struct.pack("<2sHHHHHH", b"I0", 1, 1, 2, 2, 0, 0)
            + struct.pack("<HHHH", 0, 0, 2, 2)
            + struct.pack("<I", 2) + bytes([3, 5])
            + bytes(palette) + row1 + row2)


def make_recorder(calls: list):
    """具名进度记录器（unittest 探针不用 lambda）。"""

    def record(done, total, text):
        calls.append((done, total, text))

    return record


def xor4(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i & 3] for i, b in enumerate(data))


class TestAssetResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        lst = Path(__file__).parent / "fixtures" / "ui_mini.lst"
        dlg_plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root",
              "lChildren": []}], md5="0" * 32)
        entries = [
            ("ui.lst", lst.read_bytes()),
            ("test/pic.igs", make_sprite()),
            ("dialog/test.dlg", xor4(dlg_plain, b"\x5a\xa5\x11\x7e")),
        ]
        self._tmp = tempfile.TemporaryDirectory()
        pack_path = Path(self._tmp.name) / "mini.fls"
        pack_path.write_bytes(build_pack(entries))
        self.resolver = AssetResolver()
        self.resolver.mount_pack(pack_path)

    def tearDown(self):
        self.resolver.close()
        self._tmp.cleanup()

    def test_media_candidates_from_named_layouts(self):
        # 用真实目录里的布局名 booth.dlg 作种子：它引用的图在包
        # 里有才入清单，引用了但包里没有的被过滤掉
        dlg_plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root",
              "lChildren": [
                  {"sWidgetType": "CImage", "sFileName": "test/pic.igs"},
                  {"sWidgetType": "CImage",
                   "sFileName": "test/gone.png"}]}],
            md5="0" * 32)
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "cand.fls"
            pack_path.write_bytes(build_pack([
                ("test/pic.igs", make_sprite()),
                ("booth.dlg", xor4(dlg_plain, b"\x5a\xa5\x11\x7e")),
            ]))
            resolver = AssetResolver()
            resolver.mount_pack(pack_path)
            try:
                self.assertEqual(resolver.media_candidates(),
                                 ["test/pic.igs"])
            finally:
                resolver.close()

    def test_media_candidates_include_dir_base_family(self):
        """目录型基路径（三态按钮）要进候选清单，否则选图窗根本选不到。"""
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
        dlg_plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root",
              "lChildren": [
                  {"sWidgetType": "CTextButton",
                   "sFileName": "test/btn\\"},
                  # 只有 0l、缺 0c/0r：拼不出整族，不能进清单
                  {"sWidgetType": "CImage", "sFileName": "test/broken\\"}]}],
            md5="0" * 32)
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "fam.fls"
            pack_path.write_bytes(build_pack([
                ("test/btn/0l.png", png), ("test/btn/0c.png", png),
                ("test/btn/0r.png", png), ("test/broken/0l.png", png),
                ("booth.dlg", xor4(dlg_plain, b"\x5a\xa5\x11\x7e")),
            ]))
            resolver = AssetResolver()
            resolver.mount_pack(pack_path)
            try:
                candidates = resolver.media_candidates()
                self.assertIn("test/btn\\", candidates)
                self.assertNotIn("test/broken\\", candidates)
                self.assertNotIn("test/btn/0l.png", candidates)
            finally:
                resolver.close()

    def test_staged_family_listed_as_one_directory(self):
        """新建族挂账后：候选列族本身，不把每张子图单独列出来。"""
        self.resolver.stage_image("fam/btn/0l.png", b"\x89PNGL")
        self.resolver.stage_image("fam/btn/0c.png", b"\x89PNGC")
        self.resolver.stage_image("fam/btn/0r.png", b"\x89PNGR")
        self.resolver.stage_image("fam/solo.png", b"\x89PNGS")
        families = self.resolver.staged_families()
        self.assertEqual(list(families), ["fam\\btn\\"])
        self.assertEqual(len(families["fam\\btn\\"]), 3)
        candidates = self.resolver.candidates_with_staged()
        self.assertIn("fam\\btn\\", candidates)
        self.assertIn("fam/solo.png", candidates)
        self.assertNotIn("fam/btn/0l.png", candidates)

    def test_staged_nine_slice_folds_to_base_not_rows(self):
        """九片的子图挂在 top/ 等子目录下，族仍是外层目录，不能拆成三个族。"""
        self.resolver.stage_image("ui/panel/top/left.png", b"P")
        self.resolver.stage_image("ui/panel/top/middle.png", b"P")
        self.resolver.stage_image("ui/panel/top/right.png", b"P")
        self.resolver.stage_image("ui/panel/middle/left.png", b"P")
        self.resolver.stage_image("ui/panel/middle/middle.png", b"P")
        self.resolver.stage_image("ui/panel/middle/right.png", b"P")
        self.resolver.stage_image("ui/panel/bottom/left.png", b"P")
        self.resolver.stage_image("ui/panel/bottom/middle.png", b"P")
        self.resolver.stage_image("ui/panel/bottom/right.png", b"P")
        families = self.resolver.staged_families()
        self.assertEqual(list(families), ["ui\\panel\\"])
        self.assertEqual(len(families["ui\\panel\\"]), 9)
        candidates = self.resolver.candidates_with_staged()
        self.assertEqual(candidates, ["ui\\panel\\"])

    def test_staged_family_needs_the_whole_set(self):
        # 半套（缺 0c/0r）不是族：不能折叠，否则用户看不到那几张
        self.resolver.stage_image("fam/half/0l.png", b"\x89PNGL")
        self.resolver.stage_image("fam/half/1l.png", b"\x89PNG1L")
        self.assertEqual(self.resolver.staged_families(), {})
        self.assertIn("fam/half/0l.png",
                      self.resolver.candidates_with_staged())

    def test_media_candidates_progress_hook(self):
        # 忙碌遮罩：首次整理清单报真实进度（done 单调 → total）
        dlg_plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CMainFrame", "sName": "root",
              "lChildren": [
                  {"sWidgetType": "CImage", "sFileName": "test/pic.igs"}]}],
            md5="0" * 32)
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "cand.fls"
            pack_path.write_bytes(build_pack([
                ("test/pic.igs", make_sprite()),
                ("booth.dlg", xor4(dlg_plain, b"\x5a\xa5\x11\x7e")),
            ]))
            resolver = AssetResolver()
            resolver.mount_pack(pack_path)
            try:
                calls = []
                resolver.media_candidates(
                    progress=make_recorder(calls))
                self.assertTrue(calls, "应有进度回调")
                self.assertEqual({c[1] for c in calls}, {1})  # 1 条已知布局
                self.assertEqual(calls[-1][0], 1)
                # 缓存命中后不再回调（一次性重活）
                calls.clear()
                self.assertEqual(resolver.media_candidates(
                    progress=make_recorder(calls)), ["test/pic.igs"])
                self.assertEqual(calls, [])
            finally:
                resolver.close()

    def test_staged_images_roundtrip(self):
        # 选图窗挂账：预览直读、候选清单包含、写包后可销账
        self.resolver.stage_image("new/pic.png", b"\x89PNGstaged")
        self.assertEqual(self.resolver.fetch_bytes("new/pic.png"),
                         b"\x89PNGstaged")
        self.assertEqual(self.resolver.fetch_bytes("new\\pic.png"),
                         b"\x89PNGstaged")  # 分隔符写法不同也命中
        self.assertIn("new/pic.png",
                      self.resolver.candidates_with_staged())
        self.resolver.discard_staged(["new/pic.png"])
        self.assertEqual(self.resolver.staged_images(), {})

    def test_fetch_styles(self):
        book = self.resolver.fetch_styles()
        self.assertIsNotNone(book)
        self.assertEqual(len(book.fonts), 2)

    def test_fetch_xored_dlg(self):
        result = self.resolver.fetch_dlg("dialog/test.dlg")
        self.assertIsNotNone(result)
        dicts, md5 = result
        self.assertEqual(dicts[0]["sWidgetType"], "CMainFrame")
        self.assertEqual(md5, "0" * 32)

    def test_fetch_missing(self):
        self.assertIsNone(self.resolver.fetch_dlg("dialog/none.dlg"))
        self.assertIsNone(self.resolver.fetch_bytes("nope.png"))

    def test_loose_resource_paths_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "resources"
            root.mkdir()
            outside = Path(tmp) / "outside.png"
            outside.write_bytes(b"outside")
            resolver = AssetResolver()
            resolver.add_loose_dir(root)
            try:
                self.assertIsNone(resolver.fetch_bytes("missing.png"))
                absolute = str(outside.resolve())
                for name in ("../outside.png", absolute,
                             "C:\\\\outside.png"):
                    with self.subTest(name=name):
                        with self.assertRaises(ValueError):
                            resolver.fetch_bytes(name)
            finally:
                resolver.close()

    def test_staged_resource_path_is_validated(self):
        with self.assertRaises(ValueError):
            self.resolver.stage_image("../escape.png", b"data")

    def test_fetch_sprite_image(self):
        frames = self.resolver.fetch_image("test/pic.igs")
        self.assertIsNotNone(frames)
        self.assertEqual(len(frames), 1)
        image = frames[0]
        self.assertEqual((image.width(), image.height()), (2, 2))
        red = image.pixelColor(0, 0)
        green = image.pixelColor(1, 0)
        self.assertEqual((red.red(), red.green(), red.blue()), (255, 0, 0))
        self.assertEqual((green.red(), green.green()), (0, 255))


class TestUnpackText(unittest.TestCase):
    def test_plain_passthrough(self):
        data = "# -*- coding: gbk -*-\nUI_INFO = []\n".encode("gbk")
        self.assertEqual(unpack_packed_text(data), data)

    def test_xor_roundtrip(self):
        plain = dlg_codec.dump_bytes(
            [{"sWidgetType": "CBox", "sName": "框", "lChildren": []}])
        packed = xor4(plain, b"\x01\x02\x03\x04")
        self.assertEqual(unpack_packed_text(packed), plain)


if __name__ == "__main__":
    unittest.main()
