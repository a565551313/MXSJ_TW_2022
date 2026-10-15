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

    def test_save_new_copy_preserves_previous_baseline(self):
        doc = _make_0slf_doc()
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "test.fls"
            save_document(doc, target)
            self.assertTrue(target.exists())
            first = target.read_bytes()
            doc.replace_content(0, b"v2")
            next_target = Path(td) / "next.fls"
            save_document(doc, next_target)
            self.assertEqual(target.read_bytes(), first)
            reopened = PackDocument.open(next_target)
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


class TestSaveWithDecoderGapSprites(unittest.TestCase):
    """原包自带解码器覆盖外的精灵，未改动不得拦下整包保存。

    回归背景（真实 interface.fls）：仅新增一条无关条目，保存必
    填的逐条试解码却栽在两条原包精灵上（大头精灵/行数变体），
    整包保存被拒。字节逐字比对才是硬闸门；未改动的精灵解不开
    只记 sprite_undecodable 提示，被改动/新增的才拦截。
    """

    FAKE_SPRITE = b"I0" + b"\xff" * 10  # 精灵魔数但体是坏的

    def _make_doc(self) -> PackDocument:
        payloads = [b"plain", self.FAKE_SPRITE, b"other"]
        metas = [fls0slf.EntryMeta(entry_id=i, r1=0) for i in range(3)]
        return PackDocument.from_bytes(fls0slf.build(payloads, metas))

    def test_untouched_gap_sprite_does_not_block_save(self):
        from resource_editor.core.errors import SaveError  # noqa: F401

        doc = self._make_doc()
        doc.add_entry_for_path(b"NEWPNG", "interface\\新增圖.png")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "saved.fls"
            report = save_document(doc, out)  # 不得抛 SaveError
            self.assertTrue(report.ok, msg="; ".join(report.messages))
            self.assertEqual(report.sprite_undecodable, 1)
            reopened = PackDocument.open(out)
            self.assertEqual(reopened.stored(1), self.FAKE_SPRITE)
            reopened.close()
        doc.close()

    def test_modified_gap_sprite_blocks_save(self):
        from resource_editor.core.errors import SaveError

        doc = self._make_doc()
        doc.replace_content(1, self.FAKE_SPRITE + b"v2")  # 改动后成图条目
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "saved.fls"
            with self.assertRaises(SaveError):
                save_document(doc, out)
        doc.close()


if __name__ == "__main__":
    unittest.main()
