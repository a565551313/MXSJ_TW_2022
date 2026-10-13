"""容器层测试：合成包往返 + 真实包解析/重打包一致性。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.containers import fls0slf, flsdata  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.mxhash import mx_hash  # noqa: E402
from resource_editor.core.services.verifier import verify_rebuilt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
KNOWN_COUNTS = {
    "script.fls": 5002,
    "data.fls": 133,
    "magicres5.fls": 152,
    "skill.fls": 342,
    "skill2.fls": 454,
    "passive.fls": 41,
    "effect.fls": 65,
}


class TestFls0SlfSynthetic(unittest.TestCase):
    def test_roundtrip(self):
        payloads = [b"I0 fake", b"", b"\x00\x01\x02" * 100]
        metas = [fls0slf.EntryMeta(entry_id=100 + i, r1=i * 7) for i in range(3)]
        blob = fls0slf.build(payloads, metas)
        parsed = fls0slf.parse(blob)
        self.assertEqual(parsed.payloads, payloads)
        # r1=0 写出时换非零值（真实包无一为 0），其余原样保留
        self.assertEqual(
            [(m.entry_id, m.r1) for m in parsed.metas],
            [(100, fls0slf.fresh_r1(100)), (101, 7), (102, 14)],
        )

    def test_build_sorts_directory_engine_findable(self):
        """目录恒按 entry_id 升序写：乱序输入、二分寻址、按号回读。

        回归背景：新增条目旧实现追加到目录尾且 r1=0，引擎按有序
        目录寻址扑空（进游戏卡屏）。写出必须维持升序不变量。
        """
        import bisect
        import struct

        payloads = [b"ccc", b"a", b"bb"]
        metas = [fls0slf.EntryMeta(entry_id=eid, r1=0)
                 for eid in (3000, 1000, 2000)]
        blob = fls0slf.build(payloads, metas)
        count, dir_offset = struct.unpack_from("<II", blob, 4)
        ids = [struct.unpack_from("<IIII", blob,
                                  dir_offset + i * 16)[0]
               for i in range(count)]
        self.assertEqual(ids, [1000, 2000, 3000])
        parsed = fls0slf.parse(blob)
        by_id = {m.entry_id: p for m, p in
                 zip(parsed.metas, parsed.payloads, strict=True)}
        self.assertEqual(by_id, {1000: b"a", 2000: b"bb", 3000: b"ccc"})
        for eid in ids:  # 模拟引擎二分寻址：每条都得命中
            j = bisect.bisect_left(ids, eid)
            self.assertTrue(j < len(ids) and ids[j] == eid)
        self.assertTrue(all(m.r1 != 0 for m in parsed.metas))

    def test_add_by_path_save_keeps_engine_findable(self):
        """按路径新增 -> 保存 -> 重开：新图二分可寻、目录升序。"""
        import bisect
        import struct

        doc = PackDocument.from_bytes(fls0slf.build(
            [b"old"], [fls0slf.EntryMeta(entry_id=1000, r1=5)]))
        doc.add_entry_for_path(b"NEWPNG", "interface\\新增圖.png")
        blob = doc.build_bytes()
        parsed = fls0slf.parse(blob)
        count, dir_offset = struct.unpack_from("<II", blob, 4)
        ids = [struct.unpack_from("<IIII", blob,
                                  dir_offset + i * 16)[0]
               for i in range(count)]
        self.assertEqual(ids, sorted(ids))
        new_id = mx_hash("interface\\新增圖.png".encode("gbk"))
        j = bisect.bisect_left(ids, new_id)
        self.assertTrue(j < len(ids) and ids[j] == new_id)
        by_id = {m.entry_id: p for m, p in
                 zip(parsed.metas, parsed.payloads, strict=True)}
        self.assertEqual(by_id[new_id], b"NEWPNG")
        self.assertEqual(by_id[1000], b"old")
        doc.close()


class TestFlsDataSynthetic(unittest.TestCase):
    def test_roundtrip(self):
        header = b"FLS\x00" + bytes(60)
        metas = [
            flsdata.EntryMeta(name="dir\\", w1=0),
            flsdata.EntryMeta(name="a.pyo", w1=8, w2=1, w3=2),
            flsdata.EntryMeta(name="dir\\b.pyo", w1=8),
        ]
        contents = [b"", b"print('hello')\n" * 30, bytes(range(256)) * 3]
        stored = [b""] + [flsdata.deflate(c) for c in contents[1:]]
        archive = flsdata.FlsDataArchive(header=header, payloads=[], metas=metas)
        blob = flsdata.build(archive, stored)
        parsed = flsdata.parse(blob)
        self.assertEqual([m.name for m in parsed.metas],
                         [m.name for m in metas])
        for i, content in enumerate(contents):
            got = b"" if parsed.metas[i].is_dir else flsdata.inflate(
                parsed.payloads[i])
            self.assertEqual(got, content)


@unittest.skipUnless(DATA_DIR.exists(), "缺少 data 目录")
class TestRealPacks(unittest.TestCase):
    def test_all_packs_parse_and_rebuild(self):
        for name, count in KNOWN_COUNTS.items():
            path = DATA_DIR / name
            if not path.exists():
                continue
            with self.subTest(pack=name):
                doc = PackDocument.open(path)
                self.assertEqual(doc.count, count)
                built = doc.build_bytes()
                report = verify_rebuilt(
                    built, [doc.stored(i) for i in range(doc.count)])
                self.assertTrue(report.ok, msg="; ".join(report.messages))


if __name__ == "__main__":
    unittest.main()
