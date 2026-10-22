"""批量写包：一次复制、一次校验，把多个布局条目写进同一个新包。

批量导入本地布局（0.15.0）依赖这条链路：不能「每个布局各写一遍整包」，
也不能为了省事跳过校验。这里锁住四件事：

* 多个布局（新增 + 替换混着）一次写进去，全部能按原生密钥读回；
* 未改条目逐字节不变，源包一个字节不动；
* 声明与实际不符时校验会拒绝（不静默放过）；
* 输入不合法（空清单、附加图片入口混进 .dlg）当场报错。
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.errors import PackError  # noqa: E402
from ui_editor.core.mxhash import mx_hash  # noqa: E402
from ui_editor.core.native_layout import (  # noqa: E402
    decode_native,
    encode_layout,
    path_bytes,
)
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.pack_build import (  # noqa: E402
    _RebuildNeeded,
    patch_pack_copy,
    patch_pack_copy_many,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_pack_build import _archive, _dlg  # noqa: E402


def _source(tmp: Path) -> Path:
    """源包：一个旧布局 + 两个普通资源（模拟真包里的图片/脚本）。"""
    path = tmp / "source.fls"
    path.write_bytes(_archive([
        ("dialog/existing.dlg", _dlg("Old"), b"\x00\x00\x00\x00"),
        ("image/keep.png", b"KEEP-PNG", b"\x00\x00\x00\x00"),
        ("script/main.bin", b"KEEP-BIN", b"\x00\x00\x00\x00"),
    ]))
    return path


class BatchWriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = _source(self.root)
        self.original = self.src.read_bytes()

    def _read(self, pack: FlsPack, path: str) -> bytes:
        return decode_native(pack.read_named(path),
                             mx_hash(path_bytes(path)))

    def test_writes_added_and_replaced_layouts_in_one_pack(self):
        out = self.root / "out.fls"
        layouts = {
            "dialog/existing.dlg": _dlg("New"),        # 替换
            "dialog/brand_new.dlg": _dlg("A"),      # 新增
            "login/deep/regform.dlg": _dlg("B"),    # 新增（带子目录）
        }
        info = patch_pack_copy_many(
            str(self.src), layouts, str(out),
            extra_entries={"image/new.png": b"NEW-PNG"},
            allow_create=True)
        self.assertTrue(info["layout_added"])
        self.assertEqual(sorted(info["layouts_added"]),
                         ["dialog/brand_new.dlg", "login/deep/regform.dlg"])
        self.assertEqual(info["layouts_replaced"], ["dialog/existing.dlg"])
        self.assertEqual(info["images_added"], ["image/new.png"])
        # 源包一个字节都不动
        self.assertEqual(self.src.read_bytes(), self.original)

        with FlsPack(out) as pack:
            ids = pack.entry_ids
            self.assertEqual(ids, sorted(ids), "目录必须保持升序")
            for path, plain in layouts.items():
                self.assertEqual(self._read(pack, path), plain, path)
            self.assertEqual(pack.read_named("image/new.png"), b"NEW-PNG")
            # 未改资源逐字节不变
            self.assertEqual(pack.read_named("image/keep.png"), b"KEEP-PNG")
            self.assertEqual(pack.read_named("script/main.bin"), b"KEEP-BIN")

    def test_single_entry_api_still_works(self):
        out = self.root / "single.fls"
        info = patch_pack_copy(str(self.src), "dialog/existing.dlg",
                               _dlg("Single"), str(out), allow_create=True)
        self.assertIn(info["mode"], ("inplace", "relocated"))
        self.assertFalse(info["layout_added"])
        with FlsPack(out) as pack:
            self.assertEqual(self._read(pack, "dialog/existing.dlg"), _dlg("Single"))

    def test_empty_layout_list_is_rejected(self):
        with self.assertRaises(PackError):
            patch_pack_copy_many(str(self.src), {}, str(self.root / "x.fls"))

    def test_dlg_path_through_image_channel_is_rejected(self):
        with self.assertRaises(PackError):
            patch_pack_copy_many(
                str(self.src), {"dialog/a.dlg": _dlg("A")},
                str(self.root / "x.fls"),
                extra_entries={"dialog/b.dlg": _dlg("B")},
                allow_create=True)

    def test_invalid_layout_path_is_rejected(self):
        with self.assertRaises(PackError):
            patch_pack_copy_many(
                str(self.src), {"../逃出去.dlg": _dlg("A")},
                str(self.root / "x.fls"), allow_create=True)
        self.assertFalse((self.root / "x.fls").exists())

    def test_rebuild_fallback_writes_every_layout(self):
        """病态包（目录乱序）整体重组时，批量里的每个布局都要落地。"""
        out = self.root / "rebuilt.fls"
        layouts = {"dialog/a.dlg": _dlg("A"), "dialog/b.dlg": _dlg("B")}
        with mock.patch(
            "ui_editor.core.pack_build.patch_raw_entry_in_file",
            side_effect=_RebuildNeeded("合成回退"),
        ):
            info = patch_pack_copy_many(
                str(self.src), layouts, str(out), allow_create=True)
        self.assertEqual(info["mode"], "rebuild")
        with FlsPack(out) as pack:
            for path, plain in layouts.items():
                self.assertEqual(self._read(pack, path), plain, path)

    def test_declared_add_mismatch_is_rejected(self):
        """写包方声称新增了一个本来就在包里的布局 → 校验必须拒绝。"""
        from ui_editor.core import publish

        out = self.root / "mismatch.fls"
        patch_pack_copy_many(
            str(self.src),
            {"dialog/existing.dlg": _dlg("Edited"),
             "dialog/a.dlg": _dlg("A"), "dialog/b.dlg": _dlg("B")},
            str(out), extra_entries={"image/new.png": b"NEW"},
            allow_create=True)
        # 实际新增的是 a/b；写包方却把「本来就在包里的 existing」也报成新增
        report = publish.verify_structure(
            src_pack=str(self.src), out_path=str(out),
            res_path="dialog/existing.dlg", extras={},
            info={"images_added": ["image/new.png"],
                  "changed_ids": [],
                  "layouts_added": ["dialog/existing.dlg", "dialog/a.dlg"]},
            layout_paths=["dialog/existing.dlg", "dialog/a.dlg",
                          "dialog/b.dlg"])
        self.assertIn("error", report)
        self.assertIn("声明与源包不符", report.get("error", ""))

    def test_verify_structure_accepts_batch_layouts(self):
        from ui_editor.core import publish
        from ui_editor.core.mxhash import mx_hash
        from ui_editor.core.native_layout import encode_layout

        out = self.root / "batch.fls"
        layouts = {"dialog/a.dlg": _dlg("A"), "dialog/b.dlg": _dlg("B")}
        info = patch_pack_copy_many(
            str(self.src), layouts, str(out), allow_create=True)
        report = publish.verify_structure(
            src_pack=str(self.src), out_path=str(out),
            res_path="dialog/a.dlg", extras={}, info=info,
            layout_paths=list(layouts))
        self.assertNotIn("error", report)
        # 顺手确认存储字节确实按各自路径密钥加密（不是同一把钥匙）
        with FlsPack(out) as pack:
            for path in layouts:
                stored = pack.read_named(path)
                self.assertNotEqual(stored, layouts[path])
                self.assertEqual(stored, encode_layout(
                    layouts[path], mx_hash(path_bytes(path))))
                self.assertEqual(mx_hash(path_bytes(path)),
                                 mx_hash(path.encode("gbk")))

    def test_progress_reports_each_layout(self):
        out = self.root / "progress.fls"
        seen: list[str] = []
        patch_pack_copy_many(
            str(self.src),
            {"dialog/a.dlg": _dlg("A"), "dialog/b.dlg": _dlg("B")},
            str(out), allow_create=True,
            progress=lambda done, total, text: seen.append(text))
        self.assertTrue(any("写入布局 1/2" in text for text in seen), seen)
        self.assertTrue(any("写入布局 2/2" in text for text in seen), seen)

    def test_output_is_a_single_file_not_one_pack_per_layout(self):
        out = self.root / "one.fls"
        patch_pack_copy_many(
            str(self.src),
            {f"dialog/new{i}.dlg": _dlg(f"Row{i}") for i in range(3)},
            str(out), allow_create=True)
        self.assertEqual(sorted(p.name for p in self.root.glob("*.fls")),
                         ["one.fls", "source.fls"])
        with FlsPack(out) as pack:
            self.assertEqual(pack.count, 6)  # 源包 3 条 + 新增 3 个布局

    def test_extra_entries_can_overwrite_existing_image(self):
        out = self.root / "img.fls"
        patch_pack_copy_many(
            str(self.src), {"dialog/existing.dlg": _dlg("Edited")}, str(out),
            extra_entries={"image/keep.png": b"NEW-KEEP"})
        with FlsPack(out) as pack:
            self.assertEqual(pack.read_named("image/keep.png"), b"NEW-KEEP")
            self.assertEqual(pack.read_named("script/main.bin"), b"KEEP-BIN")

    def test_layout_storage_uses_its_own_path_key(self):
        """每个布局各按自己的路径密钥加密，不共用一把钥匙。"""
        from ui_editor.core.native_layout import path_bytes as pb

        out = self.root / "keys.fls"
        layouts = {"dialog/a.dlg": _dlg("A"), "dialog/b.dlg": _dlg("B")}
        patch_pack_copy_many(str(self.src), layouts, str(out),
                             allow_create=True)
        with FlsPack(out) as pack:
            stored_a = pack.read_named("dialog/a.dlg")
            stored_b = pack.read_named("dialog/b.dlg")
        self.assertNotEqual(stored_a, stored_b)
        self.assertEqual(stored_a, encode_layout(
            layouts["dialog/a.dlg"], mx_hash(pb("dialog/a.dlg"))))
        self.assertEqual(stored_b, encode_layout(
            layouts["dialog/b.dlg"], mx_hash(pb("dialog/b.dlg"))))


if __name__ == "__main__":
    unittest.main()
