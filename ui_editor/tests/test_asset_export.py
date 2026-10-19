"""导出素材：格式识别、原样字节、重名序号、.spr 连带帧图。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import asset_export  # noqa: E402
from ui_editor.core.model import Widget  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
GIF = b"GIF89a" + b"\x00" * 16
BMP = b"BM" + b"\x00" * 16
WAV = b"RIFF\x00\x00\x00\x00WAVEfmt " + b"\x00" * 8
OGG = b"OggS" + b"\x00" * 16
MP3 = b"ID3" + b"\x00" * 16
TGA = b"\x00" * 20 + b"TRUEVISION-XFILE." + b"\x00"


class FakeAssets:
    def __init__(self, files):
        self.files = dict(files)
        self.pack_paths = []
        self.requested: list[str] = []

    def fetch_bytes(self, name):
        self.requested.append(name)
        return self.files.get(name.replace("/", "\\"))


class TestDetectExtension(unittest.TestCase):
    def test_real_formats(self):
        cases = [(PNG, ".png"), (JPG, ".jpg"), (GIF, ".gif"), (BMP, ".bmp"),
                 (WAV, ".wav"), (OGG, ".ogg"), (MP3, ".mp3"), (TGA, ".tga")]
        for data, ext in cases:
            self.assertEqual(asset_export.detect_extension(data, "x.png"),
                             ext, ext)

    def test_misnamed_resource_uses_content(self):
        # 资源路径写 .png，实际是 JPG 字节：导出按真实格式
        self.assertEqual(asset_export.detect_extension(JPG, "btn\\a.png"),
                         ".jpg")

    def test_unknown_keeps_original_extension(self):
        self.assertEqual(
            asset_export.detect_extension(b"\x00\x01\x02", "a\\b.igs"),
            ".igs")
        self.assertEqual(asset_export.detect_extension(None, "a\\b.spr"),
                         ".spr")

    def test_sprite_keeps_resource_extension(self):
        # 20 字节以上的精灵头（I0/T0 等），扩展名沿用资源路径
        sprite = b"I0" + b"\x00" * 60
        self.assertEqual(asset_export.detect_extension(sprite, "a\\b.igs"),
                         ".igs")
        self.assertEqual(asset_export.detect_extension(sprite, "a\\b.png"),
                         ".png")


class TestAssetPaths(unittest.TestCase):
    def test_collects_all_fields_in_order(self):
        widget = Widget({
            "sWidgetType": "CProgress", "sName": "p",
            "sFileName": "a.png", "sBgFileName": "b.png",
            "sBarFileName": "c.png", "sSoundPath": "d.wav"})
        self.assertEqual(
            [name for _k, name in asset_export.asset_paths_of(widget)],
            ["a.png", "b.png", "c.png", "d.wav"])

    def test_skips_empty_and_dedupes(self):
        widget = Widget({
            "sWidgetType": "CButton", "sName": "b",
            "sFileName": "a.png", "sBgFileName": "a.png",
            "sBarFileName": "  "})
        self.assertEqual(len(asset_export.asset_paths_of(widget)), 1)

    def test_widget_without_assets(self):
        widget = Widget({"sWidgetType": "CTextFrame", "sName": "t"})
        self.assertEqual(asset_export.asset_paths_of(widget), [])


class TestExportRaw(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _widget(self, **props):
        base = {"sWidgetType": "CButton", "sName": "b"}
        base.update(props)
        return Widget(base)

    def test_writes_original_bytes_with_true_extension(self):
        assets = FakeAssets({"img\\a.png": JPG})
        widget = self._widget(sFileName="img\\a.png")
        written, missing = asset_export.export_raw_assets(
            assets, widget, self.dest)
        self.assertEqual(missing, [])
        self.assertEqual(len(written), 1)
        out = written[0]
        self.assertEqual(out.name, "a.jpg")
        self.assertEqual(out.read_bytes(), JPG)   # 字节原样，不做转换

    def test_png_stays_png(self):
        assets = FakeAssets({"a.png": PNG})
        written, _missing = asset_export.export_raw_assets(
            assets, self._widget(sFileName="a.png"), self.dest)
        self.assertEqual(written[0].name, "a.png")
        self.assertEqual(written[0].read_bytes(), PNG)

    def test_multiple_assets_named_distinctly(self):
        assets = FakeAssets({"a\\btn.png": PNG, "b\\btn.png": PNG,
                             "s\\click.wav": WAV})
        widget = self._widget(sFileName="a\\btn.png",
                              sBgFileName="b\\btn.png",
                              sSoundPath="s\\click.wav")
        written, _missing = asset_export.export_raw_assets(
            assets, widget, self.dest)
        self.assertEqual([p.name for p in written],
                         ["btn.png", "btn-2.png", "click.wav"])

    def test_missing_resource_reported(self):
        assets = FakeAssets({})
        written, missing = asset_export.export_raw_assets(
            assets, self._widget(sFileName="gone.png"), self.dest)
        self.assertEqual(written, [])
        self.assertEqual(missing, ["gone.png"])

    def test_repeat_export_does_not_overwrite(self):
        assets = FakeAssets({"a.png": PNG})
        widget = self._widget(sFileName="a.png")
        first, _ = asset_export.export_raw_assets(assets, widget, self.dest)
        second, _ = asset_export.export_raw_assets(assets, widget, self.dest)
        self.assertEqual(first[0].name, "a.png")
        self.assertEqual(second[0].name, "a-2.png")

    def test_spr_exports_frame_sources_too(self):
        from ui_editor.core import spr_desc

        # .spr = 4 字节循环 XOR 的 INI：按同样算法造一个能解回的样本
        plain = b"[frames]\n0 100\n[images]\nFileName1=real.igs\n"
        key = b"!@#$"
        repeated = (key * (len(plain) // 4 + 1))[:len(plain)]
        descriptor = (int.from_bytes(plain, "little")
                      ^ int.from_bytes(repeated, "little")).to_bytes(
                          len(plain), "little")
        self.assertIn("[images]", spr_desc.decode_spr_text(descriptor))
        assets = FakeAssets({"anim\\x.spr": descriptor,
                             "anim\\real.igs": PNG})
        widget = self._widget(sFileName="anim\\x.spr")
        written, _missing = asset_export.export_raw_assets(
            assets, widget, self.dest)
        names = [p.name for p in written]
        self.assertIn("x.spr", names)
        self.assertIn("real.png", names)          # 按真实格式改成 .png
        self.assertEqual(
            [p for p in written if p.name == "x.spr"][0].read_bytes(),
            descriptor)


if __name__ == "__main__":
    unittest.main()
