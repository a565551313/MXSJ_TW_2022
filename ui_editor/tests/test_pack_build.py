"""0SLF 写回：替换条目后重开校验，未动条目存储字节不变。"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec  # noqa: E402
from ui_editor.core.assets import unpack_packed_text  # noqa: E402
from ui_editor.core.mxhash import mx_hash  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.pack_build import (  # noqa: E402
    build_archive,
    parse_archive,
    patch_pack_copy,
    replace_dlg_entry,
)


def _archive(specs: list[tuple[str, bytes, bytes]]) -> bytes:
    """specs: (资源路径, 明文, 4 字节密钥)；密钥全零=明文存储。"""
    entries = []
    payload = bytearray()
    offset = 12
    for i, (name, plain, key) in enumerate(specs):
        stored = bytes(b ^ key[j & 3] for j, b in enumerate(plain))
        entry_id = mx_hash(name.encode("gbk"))
        r1 = 1000 + i * 77
        clen, doff = len(stored), offset
        r2 = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ clen) & 0xFFFFFFFF
        r3 = (((r2 * i * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF)
              ^ doff) & 0xFFFFFFFF
        entries.append((entry_id, r1, r2, r3))
        payload.extend(stored)
        offset += clen
    head = b"0SLF" + struct.pack("<II", len(specs), offset)
    return head + bytes(payload) + b"".join(
        struct.pack("<IIII", *e) for e in entries)


def _dlg(title: str) -> bytes:
    return dlg_codec.dump_bytes(
        [{"sWidgetType": "CMainFrame", "sTitle": title, "lChildren": []}],
        md5="0" * 32)


class TestReplaceDlgEntry(unittest.TestCase):
    def setUp(self):
        self.key_a = b"\x5a\xa5\x11\x7e"
        self.key_b = b"\x01\x02\x03\x04"
        self.original = _archive([
            ("dialog/a.dlg", _dlg("甲"), self.key_a),
            ("dialog/b.dlg", _dlg("乙"), self.key_b),
            ("ui.lst", b"[Font]\n\xa7\xba\xc5\xe9 12 400 0\n", b"\0" * 4),
        ])

    def test_replace_keeps_other_entries_stored_bytes(self):
        import tempfile

        new_plain = _dlg("改過的標題而且更長一些")
        out = replace_dlg_entry(self.original, "dialog/a.dlg", new_plain)
        before = parse_archive(self.original)
        after = parse_archive(out)
        self.assertEqual(len(before), len(after))
        self.assertEqual(after[1].stored, before[1].stored)  # b 字节不变
        self.assertEqual(after[2].stored, before[2].stored)  # ui.lst 不变
        # 目标条目：同密钥、解开后是新明文
        self.assertEqual(unpack_packed_text(after[0].stored), new_plain)
        self.assertEqual(after[0].stored[:4],
                         bytes(x ^ y for x, y in zip(
                             new_plain[:4], self.key_a, strict=True)))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.fls"
            target.write_bytes(out)
            with FlsPack(target) as pack:
                self.assertEqual(pack.count, 3)
                dicts, _ = dlg_codec.parse_bytes(
                    unpack_packed_text(pack.read_named("dialog/a.dlg")))
                self.assertEqual(dicts[0]["sTitle"], "改過的標題而且更長一些")

    def test_rebuild_is_identity_for_plain_copy(self):
        entries = parse_archive(self.original)
        out = build_archive(entries)
        again = parse_archive(out)
        self.assertEqual([e.stored for e in again],
                         [e.stored for e in entries])

    def test_reject_unknown_and_invalid(self):
        from ui_editor.core.errors import PackError

        with self.assertRaises(PackError):
            replace_dlg_entry(self.original, "dialog/nope.dlg", _dlg("丙"))
        with self.assertRaises(PackError):
            replace_dlg_entry(
                self.original, "dialog/a.dlg", b"not a dlg at all")


class TestPatchPackCopy(unittest.TestCase):
    """快速补丁：复制+原位/迁移，源包不动，他条字节不变。"""

    def setUp(self):
        self.key_a = b"\x5a\xa5\x11\x7e"
        self.key_b = b"\x01\x02\x03\x04"
        self.original = _archive([
            ("dialog/a.dlg", _dlg("一個比較長的標題"), self.key_a),
            ("dialog/b.dlg", _dlg("乙"), self.key_b),
        ])

    @staticmethod
    def _read_title(pack_path, name):
        with FlsPack(pack_path) as pack:
            dicts, _ = dlg_codec.parse_bytes(
                unpack_packed_text(pack.read_named(name)))
            return dicts[0]["sTitle"]

    def test_shorter_edit_patches_in_place(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(self.original)
            info = patch_pack_copy(src, "dialog/a.dlg", _dlg("短"), out)
            self.assertEqual(info["mode"], "inplace")
            self.assertEqual(src.read_bytes(), self.original)  # 源包不动
            self.assertEqual(out.stat().st_size, len(self.original))
            self.assertEqual(self._read_title(out, "dialog/a.dlg"), "短")
            before = parse_archive(self.original)
            after = parse_archive(out.read_bytes())
            self.assertEqual(after[1].stored, before[1].stored)

    def test_longer_edit_relocates_entry(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(self.original)
            long_title = "改過的標題而且比原來長很多很多"
            info = patch_pack_copy(
                src, "dialog/a.dlg", _dlg(long_title), out)
            self.assertEqual(info["mode"], "relocated")
            self.assertEqual(src.read_bytes(), self.original)
            self.assertGreater(out.stat().st_size, len(self.original))
            self.assertEqual(
                self._read_title(out, "dialog/a.dlg"), long_title)
            before = parse_archive(self.original)
            after = parse_archive(out.read_bytes())
            self.assertEqual(after[1].stored, before[1].stored)

    def test_patch_same_file_directly(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "only.fls"
            pack.write_bytes(self.original)
            info = patch_pack_copy(pack, "dialog/a.dlg", _dlg("短"), pack)
            self.assertEqual(info["mode"], "inplace")
            self.assertEqual(pack.stat().st_size, len(self.original))
            self.assertEqual(self._read_title(pack, "dialog/a.dlg"), "短")
            self.assertEqual(self._read_title(pack, "dialog/b.dlg"), "乙")

    def test_reject_unknown_before_copying(self):
        import tempfile

        from ui_editor.core.errors import PackError

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(self.original)
            with self.assertRaises(PackError):
                patch_pack_copy(src, "dialog/nope.dlg", _dlg("丙"), out)
            self.assertFalse(out.exists())  # 失败不落半成品


if __name__ == "__main__":
    unittest.main()
