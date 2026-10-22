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


def dangling_link(test, path, target):
    """建一个悬空符号链接；系统不允许时跳过该用例（Windows 默认无权限）。"""
    try:
        path.symlink_to(target)
    except (OSError, NotImplementedError):
        test.skipTest("当前系统不允许创建符号链接")


class FakeAssets:
    def __init__(self, files):
        self.files = dict(files)
        self.pack_paths = []
        self.requested: list[str] = []

    def fetch_bytes(self, name):
        self.requested.append(name)
        return self.files.get(name.replace("/", "\\"))

    def resource_exists(self, name):
        return name.replace("/", "\\") in self.files


DIR_BASE = "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\"


def dir_files(family, data=PNG):
    """目录型基路径的子图夹具：``family`` 是族内相对路径（如 ``0l.png``）。"""
    return {(DIR_BASE + piece).replace("/", "\\"): data
            for piece in family}


class TestDirBaseExport(unittest.TestCase):
    """目录型基路径要按拼名族展开，不能拿基路径本身去取字节。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _widget(self, **props):
        return Widget({"sWidgetType": "CTextButton", "sName": "登录按钮",
                       "sFileName": DIR_BASE, **props})

    def test_export_paths_expands_family(self):
        family = [f"{index}{side}.png" for index in (0, 1) for side in "lcr"]
        assets = FakeAssets(dir_files(family))
        paths = asset_export.export_paths(assets, DIR_BASE)
        self.assertEqual(len(paths), 6)
        self.assertTrue(all(path.startswith(DIR_BASE) for path in paths))
        self.assertEqual(asset_export.export_paths(assets, "img\\btn.png"),
                         ["img\\btn.png"])

    def test_raw_export_writes_every_state_piece(self):
        family = [f"{index}{side}.png" for index in (0, 1) for side in "lcr"]
        files = dir_files(family)
        written, missing = asset_export.export_raw_assets(
            FakeAssets(files), self._widget(), self.dest)
        self.assertEqual(missing, [])
        self.assertEqual(sorted(p.name for p in written),
                         ["0c.png", "0l.png", "0r.png",
                          "1c.png", "1l.png", "1r.png"])
        self.assertEqual((self.dest / "1c.png").read_bytes(),
                         files[(DIR_BASE + "1c.png")])

    def test_nine_slice_piece_names_keep_the_row(self):
        family = [f"{row}/{column}.png"
                  for row in ("top", "middle", "bottom")
                  for column in ("left", "middle", "right")]
        written, _missing = asset_export.export_raw_assets(
            FakeAssets(dir_files(family)), self._widget(), self.dest)
        self.assertEqual(len(written), 9)
        self.assertEqual(
            sorted(p.name for p in written),
            ["bottom-left.png", "bottom-middle.png", "bottom-right.png",
             "middle-left.png", "middle-middle.png", "middle-right.png",
             "top-left.png", "top-middle.png", "top-right.png"])
        # 九片同名不同行：不能挤成 left.png / left-2.png
        self.assertNotIn("left.png", {p.name for p in written})

    def test_unresolved_family_is_reported_with_reason(self):
        # 只有 0l：0c/0r 缺失 → 拼不出族，要说明原因而不是报「找不到」
        assets = FakeAssets(dir_files(["0l.png"]))
        written, missing = asset_export.export_raw_assets(
            assets, self._widget(), self.dest)
        self.assertEqual(written, [])
        self.assertEqual(len(missing), 1)
        self.assertIn("目录型基路径", missing[0])
        self.assertIn("拼不出整族子图", missing[0])
        # 基路径本身从没被当成资源去取字节
        self.assertNotIn(DIR_BASE, assets.requested)

    def test_pieces_are_deduped_across_widgets(self):
        family = [f"{index}{side}.png" for index in (0, 1) for side in "lcr"]
        assets = FakeAssets(dir_files(family))
        seen: set[str] = set()
        first, _ = asset_export.export_raw_assets(
            assets, self._widget(), self.dest, seen=seen)
        second, missing = asset_export.export_raw_assets(
            assets, self._widget(), self.dest, seen=seen)
        self.assertEqual(len(first), 6)
        self.assertEqual(second, [])
        self.assertEqual(missing, [])
        self.assertEqual(len(list(self.dest.iterdir())), 6)

    def test_piece_stem_keeps_family_path(self):
        self.assertEqual(
            asset_export.dir_piece_stem(DIR_BASE + "0l.png", DIR_BASE), "0l")
        self.assertEqual(
            asset_export.dir_piece_stem(DIR_BASE + "top/left.png", DIR_BASE),
            "top-left")
        self.assertEqual(
            asset_export.dir_piece_name(DIR_BASE + "top/left.igs", DIR_BASE),
            "top-left.igs")
        # 批量导出多个族时的前缀
        self.assertEqual(
            asset_export.dir_piece_stem(DIR_BASE + "0l.png", DIR_BASE,
                                        "登录按钮-"),
            "登录按钮-0l")
        self.assertEqual(
            asset_export.dir_piece_name(DIR_BASE + "top/left.igs", DIR_BASE,
                                        "登录按钮-"),
            "登录按钮-top-left.igs")

    def test_unreadable_piece_is_reported(self):
        """族里某块取不出（None / 被拒）时不能把残族当完整导出。"""
        family = [f"{index}{side}.png" for index in (0, 1) for side in "lcr"]

        class HalfReadable(FakeAssets):
            def __init__(self, files, unavailable, exc=None):
                super().__init__(files)
                self.unavailable = set(unavailable)
                self.exc = exc

            def resource_exists(self, name):
                key = name.replace("/", "\\")
                return key in self.files or key in self.unavailable

            def fetch_bytes(self, name):
                key = name.replace("/", "\\")
                if key in self.unavailable and self.exc is not None:
                    raise self.exc
                return super().fetch_bytes(name)

        for exc in (None, ValueError("资源路径被拒绝")):
            with self.subTest(exc=exc):
                dest = Path(tempfile.mkdtemp(dir=self.dest))
                files = dir_files(family)
                del files[DIR_BASE + "0c.png"]     # 索引里有、取字节取不到
                assets = HalfReadable(files,
                                      [DIR_BASE + "0c.png"], exc)
                written, missing = asset_export.export_raw_assets(
                    assets, self._widget(), dest)
                self.assertEqual(len(written), 5)
                self.assertNotIn("0c.png", {p.name for p in written})
                self.assertEqual(len(missing), 1)
                self.assertIn("0c.png", missing[0])
                self.assertIn("子图读取失败", missing[0])

    def test_family_prefixes_disambiguate_same_named_folders(self):
        other = DIR_BASE.replace("登录按钮", "注册按钮")
        prefixes = asset_export.family_prefixes([DIR_BASE, other])
        self.assertEqual(prefixes[DIR_BASE], "登录按钮-")
        self.assertEqual(prefixes[other], "注册按钮-")
        # 单族批次不加前缀，文件名保持 0l.png
        self.assertEqual(asset_export.family_prefixes([DIR_BASE, DIR_BASE]), {})
        # 混在普通图片里的唯一族也不加前缀
        self.assertEqual(
            asset_export.family_prefixes([DIR_BASE, "img\\btn.png"]), {})
        # 两族末级同名时退到上一级
        deep_a = "combdialog4\\a\\登录按钮\\"
        deep_b = "combdialog5\\b\\登录按钮\\"
        deep = asset_export.family_prefixes([deep_a, deep_b])
        self.assertEqual(deep[deep_a], "a-登录按钮-")
        self.assertEqual(deep[deep_b], "b-登录按钮-")

    def test_batch_prefix_keeps_families_apart(self):
        other = DIR_BASE.replace("登录按钮", "注册按钮")
        family = ["0l.png", "0c.png", "0r.png"]
        files = dir_files(family)
        files.update({(other + piece).replace("/", "\\"): PNG
                      for piece in family})
        assets = FakeAssets(files)
        prefixes = asset_export.family_prefixes([DIR_BASE, other])
        first, _ = asset_export.export_raw_assets(
            assets, self._widget(), self.dest, family_prefixes=prefixes)
        second, _ = asset_export.export_raw_assets(
            assets, self._widget(sFileName=other), self.dest,
            family_prefixes=prefixes)
        names = {p.name for p in first + second}
        self.assertEqual(len([p for p in first if p.name.startswith("登录按钮-")]),
                         3)
        self.assertEqual(len([p for p in second if p.name.startswith("注册按钮-")]),
                         3)
        self.assertEqual(names, {"登录按钮-0l.png", "登录按钮-0c.png",
                                 "登录按钮-0r.png", "注册按钮-0l.png",
                                 "注册按钮-0c.png", "注册按钮-0r.png"})


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

    def test_invalid_path_is_reported_not_raised(self):
        """resolver 对非法路径抛 ValueError 时，导出降级为「缺失」。"""

        class StrictAssets(FakeAssets):
            def fetch_bytes(self, name):
                if name.startswith(("/", "C:")):
                    raise ValueError(f"资源路径必须是包内相对路径：{name!r}")
                return super().fetch_bytes(name)

        assets = StrictAssets({"ok.png": PNG})
        widget = self._widget(sFileName="C:\\abs\\evil.png",
                              sBgFileName="ok.png")
        written, missing = asset_export.export_raw_assets(
            assets, widget, self.dest)
        self.assertEqual([p.name for p in written], ["ok.png"])
        self.assertEqual(len(missing), 1)

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


class TestBatchExport(unittest.TestCase):
    """批量导出：同一资源只导一次、被拒绝不中断、`.spr` 帧图也不重复。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _widget(self, **props):
        base = {"sWidgetType": "CButton", "sName": "b"}
        base.update(props)
        return Widget(base)

    def test_shared_asset_exported_once_across_widgets(self):
        assets = FakeAssets({"img\\bg.png": PNG})
        seen: set[str] = set()
        written = []
        for _ in range(3):
            files, _missing = asset_export.export_raw_assets(
                assets, self._widget(sFileName="img\\bg.png"), self.dest,
                seen=seen)
            written.extend(files)
        self.assertEqual([p.name for p in written], ["bg.png"])
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),
                         ["bg.png"])

    def test_separator_spelling_counts_as_same_resource(self):
        assets = FakeAssets({"img\\bg.png": PNG})
        seen: set[str] = set()
        widgets = [self._widget(sFileName="img\\bg.png"),
                   self._widget(sFileName="img/bg.png")]
        written = []
        for widget in widgets:
            files, _missing = asset_export.export_raw_assets(
                assets, widget, self.dest, seen=seen)
            written.extend(files)
        self.assertEqual([p.name for p in written], ["bg.png"])

    def test_distinct_resources_with_same_basename_keep_both(self):
        other = PNG + b"OTHER"
        assets = FakeAssets({"a\\btn.png": PNG, "b\\btn.png": other})
        seen: set[str] = set()
        written = []
        for widget in (self._widget(sFileName="a\\btn.png"),
                       self._widget(sFileName="b\\btn.png")):
            files, _missing = asset_export.export_raw_assets(
                assets, widget, self.dest, seen=seen)
            written.extend(files)
        # 两份真素材都保留：后写的加序号，不覆盖也不丢。
        self.assertEqual([p.name for p in written],
                         ["btn.png", "btn-2.png"])
        self.assertEqual((self.dest / "btn.png").read_bytes(), PNG)
        self.assertEqual((self.dest / "btn-2.png").read_bytes(), other)

    def test_spr_frame_source_not_duplicated(self):
        from ui_editor.core import spr_desc

        plain = b"[frames]\n0 100\n[images]\nFileName1=real.igs\n"
        key = b"!@#$"
        repeated = (key * (len(plain) // 4 + 1))[:len(plain)]
        descriptor = (int.from_bytes(plain, "little")
                      ^ int.from_bytes(repeated, "little")).to_bytes(
                          len(plain), "little")
        self.assertIn("[images]", spr_desc.decode_spr_text(descriptor))
        assets = FakeAssets({"anim\\x.spr": descriptor,
                             "anim\\y.spr": descriptor,
                             "anim\\real.igs": PNG})
        seen: set[str] = set()
        written = []
        for widget in (self._widget(sFileName="anim\\x.spr"),
                       self._widget(sFileName="anim\\y.spr")):
            files, _missing = asset_export.export_raw_assets(
                assets, widget, self.dest, seen=seen)
            written.extend(files)
        self.assertEqual([p.name for p in written],
                         ["x.spr", "real.png", "y.spr"])

    def test_rejected_target_does_not_abort_remaining(self):
        # 导出目录里预存一个悬空符号链接，命中 guard_output 的「拒写符号链接」。
        dangling_link(self, self.dest / "a.png", self.dest / "missing")
        assets = FakeAssets({"a.png": PNG, "ok.png": PNG})
        widget = self._widget(sFileName="a.png", sBgFileName="ok.png")
        rejected: list[tuple[str, str]] = []
        written, _missing = asset_export.export_raw_assets(
            assets, widget, self.dest, rejected=rejected)
        self.assertEqual([p.name for p in written], ["ok.png"])
        self.assertEqual([name for name, _why in rejected], ["a.png"])
        self.assertIn("符号链接", rejected[0][1])
        self.assertFalse((self.dest / "missing").exists())

    def test_rejected_still_raises_without_collector(self):
        dangling_link(self, self.dest / "a.png", self.dest / "missing")
        assets = FakeAssets({"a.png": PNG})
        with self.assertRaises(ValueError):
            asset_export.export_raw_assets(
                assets, self._widget(sFileName="a.png"), self.dest)


if __name__ == "__main__":
    unittest.main()
