"""文档模型与保存流程测试（合成包，不依赖真实数据）。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.containers import fls0slf, flsdata  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.services.saver import save_document  # noqa: E402


def _make_0slf_doc() -> PackDocument:
    payloads = [b"hello", b"\x89PNG fake", b""]
    metas = [fls0slf.EntryMeta(entry_id=i, r1=0) for i in range(3)]
    return PackDocument.from_bytes(fls0slf.build(payloads, metas))


class TestDocument0Slf(unittest.TestCase):
    def test_replace_revert_undo(self):
        doc = _make_0slf_doc()
        self.assertFalse(doc.is_dirty(0))
        doc.replace_content(0, b"changed")
        self.assertTrue(doc.is_dirty(0))
        self.assertTrue(doc.undo(0))
        self.assertEqual(doc.stored(0), b"hello")
        doc.replace_content(0, b"changed")
        doc.revert(0)
        self.assertEqual(doc.stored(0), b"hello")
        self.assertFalse(doc.is_dirty(0))

    def test_add_delete(self):
        doc = _make_0slf_doc()
        idx = doc.add_entry(b"new entry")
        self.assertEqual(idx, 3)
        doc.delete_entry(1)
        self.assertEqual(doc.count, 3)
        PackDocument.from_bytes(doc.build_bytes())  # 构建结果可重解析

    def test_save_with_backup(self):
        doc = _make_0slf_doc()
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "test.fls"
            save_document(doc, target)
            self.assertTrue(target.exists())
            doc.replace_content(0, b"v2")
            save_document(doc, target)
            self.assertTrue(target.with_suffix(".fls.bak").exists())
            reopened = PackDocument.open(target)
            self.assertEqual(reopened.stored(0), b"v2")
            self.assertFalse(reopened.is_modified)


class TestDocumentFlsData(unittest.TestCase):
    def test_untouched_stored_bytes_preserved(self):
        header = b"FLS\x00" + bytes(60)
        metas = [
            flsdata.EntryMeta(name="a.pyo", w1=8),
            flsdata.EntryMeta(name="b.pyo", w1=8),
        ]
        stored = [flsdata.deflate(b"aaa" * 50), flsdata.deflate(b"bbb" * 50)]
        archive = flsdata.FlsDataArchive(header=header, payloads=[], metas=metas)
        doc = PackDocument.from_bytes(flsdata.build(archive, stored))
        before = [doc.stored(i) for i in range(doc.count)]
        doc.replace_content(0, b"zzz" * 60)
        rebuilt = PackDocument.from_bytes(doc.build_bytes())
        self.assertEqual(rebuilt.stored(1), before[1])  # 未改条目逐字节一致
        self.assertEqual(rebuilt.content(0), b"zzz" * 60)
        self.assertEqual(rebuilt.content(1), b"bbb" * 50)


if __name__ == "__main__":
    unittest.main()
