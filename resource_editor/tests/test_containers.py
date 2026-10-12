"""容器层测试：合成包往返 + 真实包解析/重打包一致性。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.containers import fls0slf, flsdata  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
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
        self.assertEqual(
            [(m.entry_id, m.r1) for m in parsed.metas],
            [(m.entry_id, m.r1) for m in metas],
        )


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
