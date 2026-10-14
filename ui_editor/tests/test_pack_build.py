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
    RawEntry,
    build_archive,
    fresh_r1,
    parse_archive,
    patch_pack_copy,
    patch_raw_entry_in_file,
    replace_dlg_entry,
)


def _by_id(entries):
    """parse_archive 结果按条目号索引（写回后目录为升序，勿按序号认条目）。"""
    return {e.entry_id: e for e in entries}


def _archive(specs: list[tuple[str, bytes, bytes]]) -> bytes:
    """specs: (资源路径, 明文, 4 字节密钥)；密钥全零=明文存储。

    目录按 entry_id 升序写（真实包的目录不变量）。
    """
    specs = sorted(specs, key=lambda s: mx_hash(s[0].encode("gbk")))
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
        before = _by_id(parse_archive(self.original))
        after = _by_id(parse_archive(out))
        self.assertEqual(len(before), len(after))
        id_b = mx_hash("dialog/b.dlg".encode("gbk"))
        id_lst = mx_hash("ui.lst".encode("gbk"))
        id_a = mx_hash("dialog/a.dlg".encode("gbk"))
        self.assertEqual(after[id_b].stored, before[id_b].stored)
        self.assertEqual(after[id_lst].stored, before[id_lst].stored)
        # 目标条目：同密钥、解开后是新明文
        self.assertEqual(unpack_packed_text(after[id_a].stored), new_plain)
        self.assertEqual(after[id_a].stored[:4],
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
        self.assertEqual(
            {e.entry_id: e.stored for e in again},
            {e.entry_id: e.stored for e in entries})
        # 重组后目录升序（真实包不变量）
        ids = [e.entry_id for e in again]
        self.assertEqual(ids, sorted(ids))

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
            before = _by_id(parse_archive(self.original))
            after = _by_id(parse_archive(out.read_bytes()))
            id_b = mx_hash("dialog/b.dlg".encode("gbk"))
            self.assertEqual(after[id_b].stored, before[id_b].stored)

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
            before = _by_id(parse_archive(self.original))
            after = _by_id(parse_archive(out.read_bytes()))
            id_b = mx_hash("dialog/b.dlg".encode("gbk"))
            self.assertEqual(after[id_b].stored, before[id_b].stored)

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


class TestPatchWithExtraEntries(unittest.TestCase):
    """随布局写入附加条目：新图按路径新增、已有路径替换内容。"""

    def test_add_new_and_replace_existing(self):
        import tempfile

        key = b"\x5a\xa5\x11\x7e"
        original = _archive([
            ("dialog/a.dlg", _dlg("甲"), key),
            ("dialog/b.dlg", _dlg("乙"), key),
            ("ui.lst", b"[Font]\nABC\n", b"\0" * 4),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(original)
            info = patch_pack_copy(
                src, "dialog/a.dlg", _dlg("新標題"), out,
                extra_entries={"newdir/pic.png": b"\x89PNGdata",
                               "ui.lst": b"[Font]\nXYZ\n"})
            self.assertEqual(info["images_added"], ["newdir/pic.png"])
            self.assertEqual(info["images_replaced"], ["ui.lst"])
            self.assertEqual(src.read_bytes(), original)  # 源包不动
            with FlsPack(out) as pack:
                self.assertEqual(pack.count, 4)  # 3 + 新增 1
                self.assertEqual(pack.read_named("newdir/pic.png"),
                                 b"\x89PNGdata")
                self.assertEqual(pack.read_named("ui.lst"),
                                 b"[Font]\nXYZ\n")
                dicts, _ = dlg_codec.parse_bytes(unpack_packed_text(
                    pack.read_named("dialog/a.dlg")))
                self.assertEqual(dicts[0]["sTitle"], "新標題")
            after = _by_id(parse_archive(out.read_bytes()))
            before = _by_id(parse_archive(original))
            id_b = mx_hash("dialog/b.dlg".encode("gbk"))
            self.assertEqual(after[id_b].stored, before[id_b].stored)


def _engine_index(ids: list[int], entry_id: int):
    """模拟引擎按有序目录二分寻址：返回下标，找不到返回 None。"""
    import bisect

    j = bisect.bisect_left(ids, entry_id)
    return j if j < len(ids) and ids[j] == entry_id else None


class TestAddEntryDirectoryInvariants(unittest.TestCase):
    """新增条目必须维持目录不变量：升序、r1 非零、二分可寻。

    回归背景：旧实现把新记录追加到目录尾且 r1=0，自家线性解析
    看不出问题，引擎按有序目录寻址却扑空（新图丢失、重开计数
    变少、进游戏卡屏）。以下断言全部走二分查找与按号比对。
    """

    @staticmethod
    def _pack_bytes(id_payloads: list[tuple[int, bytes]]) -> bytes:
        entries = [RawEntry(eid, 1000 + i, payload)
                   for i, (eid, payload) in enumerate(id_payloads)]
        return build_archive(entries)

    def _assert_invariants(self, pack_path, expected: dict[int, bytes]):
        with FlsPack(pack_path) as pack:
            ids = pack.entry_ids
            self.assertEqual(pack.count, len(expected))
            self.assertEqual(ids, sorted(ids))  # 目录升序
            for eid, payload in expected.items():
                at = _engine_index(ids, eid)
                self.assertIsNotNone(at, f"二分查找不到 {eid}")
                self.assertEqual(pack.read_id(eid), payload)
        for entry in parse_archive(Path(pack_path).read_bytes()):
            self.assertNotEqual(entry.r1, 0, "真实包 r1 无一为 0")

    def test_add_inserts_in_sorted_position(self):
        import tempfile

        base = [(1000, b"A" * 10), (2000, b"B" * 20), (3000, b"C" * 30)]
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "t.fls"
            pack.write_bytes(self._pack_bytes(base))
            info = patch_raw_entry_in_file(pack, 2500, b"NEW" * 7)
            self.assertEqual(info["mode"], "added")
            self.assertEqual(info["target_index"], 2)  # 插在 2000 与 3000 间
            self._assert_invariants(pack, {**dict(base), 2500: b"NEW" * 7})

    def test_add_at_head_and_tail(self):
        import tempfile

        base = [(1000, b"A"), (2000, b"B")]
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "t.fls"
            pack.write_bytes(self._pack_bytes(base))
            patch_raw_entry_in_file(pack, 500, b"HEAD")
            patch_raw_entry_in_file(pack, 9000, b"TAIL")
            self._assert_invariants(
                pack, {1000: b"A", 2000: b"B", 500: b"HEAD", 9000: b"TAIL"})

    def test_fresh_r1_nonzero_and_deterministic(self):
        for eid in (0, 1, 12345, 0xFFFFFFFF, 0x9E3779B1):
            self.assertNotEqual(fresh_r1(eid), 0)
            self.assertEqual(fresh_r1(eid), fresh_r1(eid))

    def test_build_archive_sorts_and_fixes_zero_r1(self):
        entries = [RawEntry(3000, 0, b"C"), RawEntry(1000, 0, b"A")]
        out = build_archive(entries)
        parsed = parse_archive(out)
        self.assertEqual([e.entry_id for e in parsed], [1000, 3000])
        self.assertTrue(all(e.r1 != 0 for e in parsed))
        self.assertEqual({e.entry_id: e.stored for e in parsed},
                         {1000: b"A", 3000: b"C"})

    def test_patch_pack_copy_adds_two_images_sorted(self):
        import tempfile

        key = b"\x5a\xa5\x11\x7e"
        original = _archive([
            ("dialog/a.dlg", _dlg("甲"), key),
            ("dialog/b.dlg", _dlg("乙"), key),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(original)
            info = patch_pack_copy(
                src, "dialog/a.dlg", _dlg("新標題"), out,
                extra_entries={"newdir/p1.png": b"P1",
                               "newdir/p2.png": b"P2"})
            self.assertEqual(sorted(info["images_added"]),
                             ["newdir/p1.png", "newdir/p2.png"])
            self.assertEqual(info["changed_ids"],
                             [mx_hash("dialog/a.dlg".encode("gbk"))])
            before = _by_id(parse_archive(original))
            after = _by_id(parse_archive(out.read_bytes()))
            id_b = mx_hash("dialog/b.dlg".encode("gbk"))
            self.assertEqual(after[id_b].stored, before[id_b].stored)
            with FlsPack(out) as pack:
                self.assertEqual(pack.count, 4)
                self.assertEqual(pack.entry_ids, sorted(pack.entry_ids))
                for name in ("dialog/a.dlg", "newdir/p1.png",
                             "newdir/p2.png"):
                    eid = mx_hash(name.encode("gbk"))
                    self.assertIsNotNone(
                        _engine_index(pack.entry_ids, eid), name)

    def test_add_to_real_effect_pack(self):
        import tempfile

        real = (Path(__file__).resolve().parents[2]
                / "data" / "effect.fls")
        if not real.exists():
            self.skipTest("仓库 data/effect.fls 不存在")
        new_id = mx_hash("interface\\__ui_editor_probe.png".encode("gbk"))
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "effect.fls"
            pack.write_bytes(real.read_bytes())
            with FlsPack(pack) as before:
                snapshot = {eid: before.read_id(eid)
                            for eid in before.entry_ids}
            self.assertNotIn(new_id, snapshot)
            patch_raw_entry_in_file(pack, new_id, b"PROBE-PNG")
            expected = {**snapshot, new_id: b"PROBE-PNG"}
            self._assert_invariants(pack, expected)

    def test_save_heals_append_style_broken_directory(self):
        """旧版写坏的包（目录乱序）普通保存一次应整包修复。"""
        import tempfile

        key = b"\x5a\xa5\x11\x7e"
        specs = [("dialog/a.dlg", _dlg("甲"), key),
                 ("dialog/b.dlg", _dlg("乙"), key)]
        rows = []
        payload = bytearray()
        offset = 12
        for name, plain, k in specs:
            stored = bytes(b ^ k[j & 3] for j, b in enumerate(plain))
            rows.append((mx_hash(name.encode("gbk")), 777,
                         len(stored), offset, stored))
            payload.extend(stored)
            offset += len(stored)
        rows.sort(key=lambda r: r[0])
        rows.reverse()  # 故意把目录写成降序（旧版追加式坏包）
        records = bytearray()
        for index, (eid, r1, clen, doff, _s) in enumerate(rows):
            r2 = (((r1 * eid + 0x0DF25E) & 0xFFFFFFFF) ^ clen) & 0xFFFFFFFF
            r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF)
                  ^ doff) & 0xFFFFFFFF
            records.extend(struct.pack("<IIII", eid, r1, r2, r3))
        broken = (b"0SLF" + struct.pack("<II", len(rows), offset)
                  + bytes(payload) + bytes(records))
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "broken.fls"
            out = Path(tmp) / "out.fls"
            src.write_bytes(broken)
            info = patch_pack_copy(src, "dialog/a.dlg", _dlg("修復"), out)
            self.assertEqual(info["mode"], "rebuild")
            with FlsPack(out) as pack:
                self.assertEqual(pack.entry_ids, sorted(pack.entry_ids))
                dicts, _ = dlg_codec.parse_bytes(unpack_packed_text(
                    pack.read_named("dialog/a.dlg")))
                self.assertEqual(dicts[0]["sTitle"], "修復")
                dicts, _ = dlg_codec.parse_bytes(unpack_packed_text(
                    pack.read_named("dialog/b.dlg")))
                self.assertEqual(dicts[0]["sTitle"], "乙")


if __name__ == "__main__":
    unittest.main()
