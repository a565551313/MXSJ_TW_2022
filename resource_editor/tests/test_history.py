"""文档增量时间线与改动清单：仅内存/临时合成包。"""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from resource_editor.core.changes import counts
from resource_editor.core.containers import fls0slf, flsdata
from resource_editor.core.errors import SaveError
from resource_editor.core.history import History
from resource_editor.core.model.document import PackDocument
from resource_editor.core.mxhash import mx_hash
from resource_editor.core.services.saver import save_document


def make_doc(kind="0slf"):
    if kind == "0slf":
        data = fls0slf.build(
            [b"A", b"B", b"C"],
            [fls0slf.EntryMeta(entry_id=i + 100, r1=7) for i in range(3)],
        )
    else:
        archive = flsdata.FlsDataArchive(
            header=b"FLS\0" + bytes(60),
            payloads=[],
            metas=[flsdata.EntryMeta(name=n) for n in ("a", "b", "c")],
        )
        data = flsdata.build(archive, [flsdata.deflate(p) for p in (b"A", b"B", b"C")])
    doc = PackDocument.from_bytes(data)
    doc._names = {}  # 独立于真实布局名字词库，不读取任何真实包
    return doc


def snapshot(doc):
    return {
        meta.entry_id if doc.kind == "0slf" else meta.name: doc.content(i)
        for i, meta in enumerate(doc.archive.extra_metas)
    }


class TestDocumentHistory(unittest.TestCase):
    def test_noop_does_not_make_history(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"A")
        doc.revert(0)
        self.assertFalse(doc.can_undo)
        self.assertFalse(doc.undo())
        self.assertFalse(doc.redo())
        self.assertEqual(doc.changes(), [])

    def test_global_interleaved_replace_and_redo(self):
        for kind in ("0slf", "flsdata"):
            with self.subTest(kind=kind):
                doc = make_doc(kind)
                self.addCleanup(doc.close)
                original = snapshot(doc)
                doc.replace_content(0, b"AA")
                doc.replace_content(1, b"BB")
                edited = snapshot(doc)
                self.assertTrue(doc.undo())
                self.assertEqual(doc.content(0), b"AA")
                self.assertEqual(doc.content(1), b"B")
                self.assertTrue(doc.undo(0))  # 兼容旧参数，但文档全局撤销
                self.assertEqual(snapshot(doc), original)
                self.assertFalse(doc.is_modified)
                self.assertEqual(doc.changes(), [])
                self.assertTrue(doc.redo())
                self.assertTrue(doc.redo())
                self.assertEqual(snapshot(doc), edited)

    def test_add_delete_equal_slots_use_identity(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        a = doc.add_entry(b"same")
        first_id = doc.archive.extra_metas[a].entry_id
        b = doc.add_entry(b"same")
        second_id = doc.archive.extra_metas[b].entry_id
        self.assertTrue(doc.undo())
        self.assertIn(first_id, snapshot(doc))
        self.assertNotIn(second_id, snapshot(doc))
        doc.redo()
        doc.delete_entry(a)
        self.assertNotIn(first_id, snapshot(doc))
        self.assertIn(second_id, snapshot(doc))
        doc.undo()
        self.assertEqual(doc.content(a), b"same")

    def test_revert_is_undoable(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.revert(0)
        self.assertFalse(doc.is_modified)
        self.assertEqual(doc.changes(), [])
        doc.undo()
        self.assertEqual(doc.content(0), b"edit")
        self.assertTrue(doc.is_modified)
        doc.redo()
        self.assertEqual(doc.content(0), b"A")

    def test_batch_mixed_is_one_step(self):
        for kind in ("0slf", "flsdata"):
            with self.subTest(kind=kind):
                doc = make_doc(kind)
                self.addCleanup(doc.close)
                original = snapshot(doc)
                with doc.edit_group("batch"):
                    doc.replace_content(0, b"EDIT")
                    doc.delete_entry(1)
                    if kind == "0slf":
                        doc.add_entry_for_path(b"new", "image/new.bin")
                    else:
                        doc.add_entry(b"new", "new")
                edited = snapshot(doc)
                self.assertEqual(len(doc.history.applied), 1)
                self.assertEqual(
                    counts(doc.changes()), {"新增": 1, "修改": 1, "删除": 1}
                )
                doc.undo()
                self.assertEqual(snapshot(doc), original)
                self.assertFalse(doc.is_modified)
                doc.redo()
                self.assertEqual(snapshot(doc), edited)

    def test_batch_exception_rolls_back_and_keeps_redo(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.undo()
        original = snapshot(doc)
        with self.assertRaises(RuntimeError), doc.edit_group("failed"):
            doc.delete_entry(0)
            doc.add_entry(b"new")
            raise RuntimeError("synthetic failure")
        self.assertEqual(snapshot(doc), original)
        self.assertTrue(doc.can_redo)
        self.assertFalse(doc.can_undo)
        doc.redo()
        self.assertEqual(doc.content(0), b"edit")

    def test_empty_group_keeps_redo_and_nested_group_is_one_step(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.undo()
        with doc.edit_group("empty"):
            pass
        self.assertTrue(doc.can_redo)
        with doc.edit_group("outer"):
            doc.replace_content(0, b"one")
            with doc.edit_group("inner"):
                doc.replace_content(1, b"two")
        self.assertFalse(doc.can_redo)
        self.assertEqual(len(doc.history.applied), 1)
        self.assertEqual(doc.history.undo_label, "outer")
        doc.undo()
        self.assertEqual(doc.content(0), b"A")
        self.assertEqual(doc.content(1), b"B")

    def test_new_edit_truncates_redo(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.undo()
        doc.add_entry(b"new")
        self.assertFalse(doc.can_redo)

    def test_failed_add_keeps_redo(self):
        doc = make_doc("flsdata")
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.undo()
        with self.assertRaises(ValueError):
            doc.add_entry(b"duplicate", "a")
        self.assertTrue(doc.can_redo)

    def test_sorting_does_not_retarget_commands(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        original = snapshot(doc)
        # generic add generates low ID 3; sorting moves it to index zero.
        doc.add_entry(b"new")
        doc.replace_content(0, b"changed-A")
        doc.delete_entry(1)
        edited = snapshot(doc)
        doc.write_to(io.BytesIO())
        self.assertEqual(doc.archive.extra_metas[0].entry_id, 3)
        doc.undo()  # restore B using stable neighbor identities
        doc.undo()  # restore A, not low-ID added entry
        doc.undo()  # remove the exact newly-created slot
        self.assertEqual(snapshot(doc), original)
        self.assertFalse(doc.is_modified)
        self.assertEqual(doc.changes(), [])
        while doc.redo():
            pass
        self.assertEqual(snapshot(doc), edited)

    def test_build_bytes_without_mark_saved_keeps_history(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.add_entry(b"new")
        blob = doc.build_bytes()
        self.assertTrue(doc.can_undo)
        rebuilt = PackDocument.from_bytes(blob)
        self.addCleanup(rebuilt.close)
        self.assertEqual(snapshot(doc), snapshot(rebuilt))
        doc.undo()
        doc.undo()
        self.assertFalse(doc.is_modified)

    def test_cannot_write_mid_batch(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        with self.assertRaises(ValueError), doc.edit_group("pending"):
            doc.add_entry(b"new")
            doc.build_bytes()
        self.assertFalse(doc.is_modified)
        self.assertFalse(doc.can_undo)

    def test_limits_are_incremental_and_keep_latest_large_step(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.history = History(limit=2, byte_limit=5)
        doc.replace_content(0, b"one")
        doc.replace_content(1, b"two")
        self.assertEqual(len(doc.history.applied), 1)
        doc.replace_content(2, b"huge-latest")
        self.assertEqual(len(doc.history.applied), 1)
        doc.undo()
        self.assertEqual(doc.content(2), b"C")
        self.assertTrue(doc.is_modified)  # older applied edits remain, not lost
        doc.redo()
        self.assertEqual(doc.content(2), b"huge-latest")
        doc.history = History(limit=2, byte_limit=1000)
        for i in range(4):
            doc.replace_content(0, str(i).encode())
        self.assertEqual(len(doc.history.applied), 2)

    def test_change_list_omits_cancelled_add_and_preserves_names(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        idx = doc.add_entry_for_path(b"new", "images/new.bin")
        self.assertEqual(doc.changes()[0].name, "images/new.bin")
        doc.delete_entry(idx)
        self.assertEqual(doc.changes(), [])
        self.assertFalse(doc.is_modified)
        doc.undo()
        self.assertEqual(doc.true_name(idx), "images/new.bin")
        doc.redo()
        self.assertEqual(doc.changes(), [])

    def test_changes_do_not_read_payloads(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.replace_content(0, b"edit")
        doc.delete_entry(1)
        doc.add_entry(b"new")
        doc._names = None  # 清单也不能为了认名偷偷读取未改动布局负载
        with mock.patch.object(doc.archive, "read_stored", side_effect=AssertionError):
            changes = doc.changes()
        self.assertEqual(counts(changes), {"新增": 1, "修改": 1, "删除": 1})
        self.assertEqual(changes[0].before_size, 1)
        self.assertEqual(changes[0].after_size, 4)

    def test_names_resolve_in_original_index_space_after_delete(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.delete_entry(0)
        doc.add_entry(b"new")
        doc._names = None
        with mock.patch(
            "resource_editor.core.names.build_name_map", return_value={1: "original-B"}
        ) as build:
            doc.resolve_names()
        self.assertEqual(build.call_args.args[0], [100, 101, 102])
        self.assertEqual(doc.true_name(0), "original-B")

    def test_saved_baseline_clears_history_for_both_containers(self):
        for kind in ("0slf", "flsdata"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                doc = make_doc(kind)
                self.addCleanup(doc.close)
                doc.replace_content(0, b"edit")
                doc.delete_entry(1)
                doc.add_entry(b"new", "new")
                expected = snapshot(doc)
                save_document(doc, Path(temp) / "new.fls")
                self.assertEqual(snapshot(doc), expected)
                self.assertFalse(doc.can_undo)
                self.assertFalse(doc.can_redo)
                self.assertFalse(doc.is_modified)
                self.assertEqual(doc.changes(), [])
                doc.replace_content(0, b"next")
                self.assertTrue(doc.undo())
                self.assertEqual(snapshot(doc), expected)

    def test_failed_verify_keeps_timeline_and_baseline(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        doc.add_entry(b"new")
        doc.replace_content(0, b"edit")
        expected = snapshot(doc)
        changes = doc.changes()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "new.fls"
            with mock.patch(
                "resource_editor.core.services.saver.verify_saved",
                side_effect=ValueError("synthetic verify failure"),
            ):
                with self.assertRaises(SaveError):
                    save_document(doc, target)
            self.assertFalse(target.exists())
        self.assertEqual(snapshot(doc), expected)
        self.assertEqual(doc.changes(), changes)
        self.assertEqual(len(doc.history.applied), 2)
        doc.undo()
        self.assertEqual(doc.content(0), b"A")
        doc.redo()
        self.assertEqual(snapshot(doc), expected)

    def test_path_import_name_and_hash_survive_redo(self):
        doc = make_doc()
        self.addCleanup(doc.close)
        name = "new/path.png"
        doc.add_entry_for_path(b"new", name)
        doc.undo()
        doc.redo()
        index = doc.index_by_path(name)
        self.assertEqual(doc.true_name(index), name)
        self.assertEqual(
            doc.archive.extra_metas[index].entry_id, mx_hash(name.encode("gbk"))
        )

    def test_data_directory_delete_undo_and_save_preserve_slot_count(self):
        archive = flsdata.FlsDataArchive(
            header=b"FLS\0" + bytes(60),
            payloads=[],
            metas=[
                flsdata.EntryMeta(name="folder/"),
                flsdata.EntryMeta(name="folder/a", w1=8, w2=12),
            ],
        )
        doc = PackDocument.from_bytes(
            flsdata.build(archive, [b"", flsdata.deflate(b"A")])
        )
        self.addCleanup(doc.close)
        doc.delete_entry(0)
        self.assertEqual(doc.changes()[0].operation, "删除")
        doc.undo()
        self.assertTrue(doc.archive.extra_metas[0].is_dir)
        self.assertFalse(doc.is_modified)
        doc.add_entry(b"new", "folder/new")
        with tempfile.TemporaryDirectory() as temp:
            save_document(doc, Path(temp) / "new.fls")
            self.assertEqual(doc.count, 3)
            self.assertEqual(len(doc._slots), doc.archive.orig_count)
            self.assertEqual(doc.content(0), b"")
            self.assertEqual(doc.content(1), b"A")
            self.assertTrue(doc.archive.extra_metas[0].is_dir)
            self.assertEqual(doc.archive.extra_metas[1].w2, 12)
            self.assertEqual(doc.changes(), [])

    def test_type_sniff_finishing_after_edit_cannot_cache_old_content_kind(self):
        from resource_editor.core.codecs import detect

        doc = make_doc()
        self.addCleanup(doc.close)
        original_sniff = detect.sniff_prefix
        changed = False

        def delayed_sniff(prefix):
            nonlocal changed
            if not changed:
                changed = True
                # 模拟后台读头已开始、主线程修改后旧嗅探才返回。
                doc.replace_content(0, b"\x89PNG\r\n\x1a\n")
            return original_sniff(prefix)

        with mock.patch.object(detect, "sniff_prefix", side_effect=delayed_sniff):
            self.assertEqual(doc.entry_kind(0), detect.EntryKind.PNG)
        self.assertEqual(doc.entry_kind(0), detect.EntryKind.PNG)
        doc.undo()
        self.assertEqual(doc.entry_kind(0), detect.EntryKind.TEXT)
