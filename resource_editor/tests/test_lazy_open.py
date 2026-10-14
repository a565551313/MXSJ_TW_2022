"""惰性打开测试：大包只建索引秒开、按需读取正确、流式保存往返。"""
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.containers import fls0slf  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.services.saver import save_document  # noqa: E402
from resource_editor.core.services.verifier import verify_saved  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_FLS = REPO_ROOT / "data" / "skill.fls"


def _make_big_pack(path: Path, target_entries: int = 20000) -> list[bytes]:
    """用真实 payload 循环拼一个条目数很多的 0SLF 包，返回负载真相。"""
    parsed = fls0slf.parse(SKILL_FLS.read_bytes())
    payloads = []
    metas = []
    for i in range(target_entries):
        payloads.append(parsed.payloads[i % parsed.count])
        metas.append(fls0slf.EntryMeta(entry_id=i, r1=0))
    path.write_bytes(fls0slf.build(payloads, metas))
    return payloads


@unittest.skipUnless(SKILL_FLS.exists(), "缺少 data/skill.fls")
class TestLazyOpen(unittest.TestCase):
    def test_big_pack_opens_by_index_only(self):
        with tempfile.TemporaryDirectory() as td:
            big = Path(td) / "big.fls"
            truth = _make_big_pack(big)
            t0 = time.perf_counter()
            doc = PackDocument.open(big)
            elapsed = time.perf_counter() - t0
            # 只建索引：打开远快于读完整个文件，更不能逐条解码
            self.assertLess(elapsed, 1.0)
            self.assertEqual(doc.count, len(truth))
            # 按需读取与真相一致（头/中/尾抽查）
            for i in (0, 1, 9999, len(truth) - 1):
                self.assertEqual(doc.content(i), truth[i])
                self.assertEqual(doc.stored_len(i), len(truth[i]))
            doc.close()

    def test_streaming_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            big = Path(td) / "big.fls"
            truth = _make_big_pack(big, target_entries=2000)
            doc = PackDocument.open(big)
            doc.replace_content(5, b"replaced-entry-bytes")
            out = Path(td) / "saved.fls"
            save_document(doc, out)
            report = verify_saved(out, doc.count, doc.stored)
            self.assertTrue(report.ok, msg="; ".join(report.messages))
            reopened = PackDocument.open(out)
            self.assertEqual(reopened.content(5), b"replaced-entry-bytes")
            self.assertEqual(reopened.content(6), truth[6])  # 未改条目一致
            self.assertFalse(reopened.is_modified)
            reopened.close()
            doc.close()


if __name__ == "__main__":
    unittest.main()
