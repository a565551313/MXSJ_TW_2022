"""写回校验（`core/publish.py`）的直接测试——零 Qt，不需要窗口。

抽出这段 verifier 的目的就是「最危险的保存链能独立测」（分析报告建议④）。
这里用 `pack_build.dump_archive` 造合成包做**逐条反例**：条目数、目录升序、
条目集合、未列条目被改、回读不一致都要各自被抓到；最后再用真实
`data/passive.fls` 跑一次端到端（此前只有 GUI 测试间接覆盖）。
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec, pack_build, publish  # noqa: E402
from ui_editor.core.model import LayoutDocument  # noqa: E402
from ui_editor.core.mxhash import path_hash  # noqa: E402
from ui_editor.core.native_layout import (  # noqa: E402
    HEADER,
    decode_native,
    encode_layout,
    plain_if_layout,
)
from ui_editor.core.pack import FlsPack  # noqa: E402

REAL_PACK = REPO_ROOT / "data" / "passive.fls"
RES_PATH = "dialog4/publish_test.dlg"
IMAGE_PATH = "dialog4/publish_img.png"
NEW_PATH = "dialog4/publish_new.png"
LAYOUT_ID = path_hash(RES_PATH)
IMAGE_ID = path_hash(IMAGE_PATH)
OTHER_ID = path_hash("dialog4/other.png")
IMAGE_BYTES = b"\x89PNG publish-test"
EXPECTED_DICTS = [{"sWidgetType": "CMainFrame", "sName": "Publish"}]


def write_pack(path: Path, entries: list[pack_build.RawEntry], *,
               sort: bool = True) -> None:
    """写一个合成 0SLF 包；``sort=False`` 故意保留乱序目录。"""
    ordered = sorted(entries, key=lambda e: e.entry_id) if sort else entries
    with open(path, "wb") as handle:
        pack_build.dump_archive(ordered, handle)


def entry(entry_id: int, stored: bytes) -> pack_build.RawEntry:
    return pack_build.RawEntry(entry_id, pack_build.fresh_r1(entry_id), stored)


def src_entries() -> list[pack_build.RawEntry]:
    return [entry(LAYOUT_ID, b"old layout bytes"), entry(OTHER_ID, b"other")]


def info(images_added=(IMAGE_PATH,), *, layout_added: bool = False,
         changed_ids=None) -> dict:
    return {
        "images_added": list(images_added),
        "images_replaced": [],
        "changed_ids": ([LAYOUT_ID, IMAGE_ID] if changed_ids is None
                        else list(changed_ids)),
        "layout_added": layout_added,
    }


def good_read_back(expected=EXPECTED_DICTS, extras=None):
    """注入用的回读钩子：返回给定内容（默认与期望一致）。"""
    extras = {IMAGE_PATH: IMAGE_BYTES} if extras is None else extras

    def read_back(_pack_path, _res_path, names):
        return expected, {name: extras.get(name) for name in names}

    return read_back


def core_read_back(pack_path, res_path, names):
    """零 Qt 的真实回读：FlsPack + 原生密钥解码 + dlg 解析。"""
    with FlsPack(pack_path) as pack:
        stored = pack.read_named(res_path)
        dicts = None
        if stored is not None:
            try:
                plain = decode_native(stored, path_hash(res_path))
            except ValueError:
                plain = plain_if_layout(stored) or stored
            dicts, _md5 = dlg_codec.parse_bytes(plain)
        return dicts, {name: pack.read_named(name) for name in names}


class EngineFindsTests(unittest.TestCase):
    """二分寻址模拟本身（`0x60E690` lower_bound + 相等判定）。"""

    def test_finds_and_misses(self):
        ids = [0x10, 0x20, 0x30]
        self.assertTrue(publish.engine_finds(ids, 0x10))
        self.assertTrue(publish.engine_finds(ids, 0x30))
        self.assertFalse(publish.engine_finds(ids, 0x25))
        self.assertFalse(publish.engine_finds(ids, 0x40))
        self.assertFalse(publish.engine_finds([], 0x10))

    def test_directory_sorted(self):
        self.assertTrue(publish.directory_is_sorted([1, 2, 3]))
        self.assertTrue(publish.directory_is_sorted([]))
        self.assertFalse(publish.directory_is_sorted([1, 3, 2]))


class StructureTests(unittest.TestCase):
    """结构检查的逐条反例。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "src.fls"
        write_pack(self.src, src_entries())

    def out_path(self, name: str = "out.fls") -> Path:
        return self.root / name

    def verify(self, out: Path, *, info_dict=None, extras=None) -> dict:
        return publish.verify_written_pack(
            src_pack=self.src, out_path=out, res_path=RES_PATH,
            extras={IMAGE_PATH: IMAGE_BYTES} if extras is None else extras,
            expected_dicts=EXPECTED_DICTS,
            info=info() if info_dict is None else info_dict,
            read_back=good_read_back())

    def test_good_copy_passes(self):
        out = self.out_path()
        entries = src_entries() + [entry(IMAGE_ID, IMAGE_BYTES)]
        entries[0] = entry(LAYOUT_ID, b"rewritten layout bytes")
        write_pack(out, entries)
        report = self.verify(out)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["entries_after"], 3)
        self.assertEqual(report["changed_entries"], 1)

    def test_count_mismatch(self):
        out = self.out_path()
        write_pack(out, src_entries())  # 没有写入新图
        report = self.verify(out)
        self.assertFalse(report["ok"])
        self.assertIn("条目数变化", report["error"])

    def test_unsorted_directory(self):
        out = self.out_path()
        entries = src_entries() + [entry(IMAGE_ID, IMAGE_BYTES)]
        write_pack(out, list(reversed(entries)), sort=False)
        report = self.verify(out)
        self.assertFalse(report["ok"])
        self.assertIn("未按条目号升序", report["error"])

    def test_entry_set_mismatch(self):
        out = self.out_path()
        # 条数对得上，但目标布局的条目号被换成了别的路径
        entries = [entry(OTHER_ID, b"other"),
                   entry(path_hash("dialog4/hijack.png"), b"hijack"),
                   entry(IMAGE_ID, IMAGE_BYTES)]
        write_pack(out, entries)
        report = self.verify(out)
        self.assertFalse(report["ok"])
        self.assertIn("条目集合与预期不符", report["error"])

    def test_unlisted_entry_changed_bytewise(self):
        out = self.out_path()
        entries = src_entries() + [entry(IMAGE_ID, IMAGE_BYTES)]
        entries[0] = entry(LAYOUT_ID, b"rewritten layout bytes")
        # 未列入 changed_ids 的条目被悄悄改了存储字节
        entries[1] = entry(OTHER_ID, b"other MUTATED")
        write_pack(out, entries)
        report = self.verify(out)
        self.assertFalse(report["ok"])
        self.assertIn("被意外改变", report["error"])

    def test_layout_added_counts_towards_total(self):
        out = self.out_path()
        entries = src_entries() + [entry(IMAGE_ID, IMAGE_BYTES)]
        write_pack(out, entries)  # 目标布局本来就在包里
        report = self.verify(out, info_dict=info(layout_added=True))
        self.assertFalse(report["ok"])
        self.assertIn("条目数变化", report["error"])


class ReadbackTests(unittest.TestCase):
    """回读检查的反例（结构正确，只有回读不一致）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "src.fls"
        write_pack(self.src, src_entries())
        self.out = self.root / "out.fls"
        entries = src_entries() + [entry(IMAGE_ID, IMAGE_BYTES)]
        entries[0] = entry(LAYOUT_ID, b"rewritten layout bytes")
        write_pack(self.out, entries)

    def verify(self, read_back) -> dict:
        return publish.verify_written_pack(
            src_pack=self.src, out_path=self.out, res_path=RES_PATH,
            extras={IMAGE_PATH: IMAGE_BYTES}, expected_dicts=EXPECTED_DICTS,
            info=info(), read_back=read_back)

    def test_layout_content_differs(self):
        report = self.verify(good_read_back(expected=[{"sName": "Other"}]))
        self.assertFalse(report["ok"])
        self.assertIn("回读内容与当前文档不一致", report["error"])

    def test_layout_readback_missing(self):
        report = self.verify(good_read_back(expected=None))
        self.assertFalse(report["ok"])
        self.assertIn("回读目标布局失败", report["error"])

    def test_image_readback_differs(self):
        report = self.verify(good_read_back(extras={IMAGE_PATH: b"other"}))
        self.assertFalse(report["ok"])
        self.assertIn("回读不一致", report["error"])

    def test_readback_exception_is_reported_not_raised(self):
        def boom(_pack_path, _res_path, _names):
            raise RuntimeError("解析器炸了")

        report = self.verify(boom)
        self.assertFalse(report["ok"])
        self.assertIn("写回校验失败", report["error"])


class RealPackEndToEndTests(unittest.TestCase):
    """真实包端到端：写出新包 → 用零 Qt 回读钩子跑完整校验。"""

    def test_written_pack_verifies_with_core_readback(self):
        if not REAL_PACK.is_file():
            self.skipTest(f"缺少真实资源包：{REAL_PACK}")
        plain = HEADER + b"\n# MD5: " + b"0" * 32 + b"\n\nUI_INFO = [\n\t{\n" \
            b'\t\t"sWidgetType": "CMainFrame",\n\t\t"sName": "publish_e2e",' \
            b'\n\t\t"iWidth": 10,\n\t\t"iHeight": 8,\n\t},\n]\n'
        expected = dlg_codec.parse_bytes(plain)[0]
        res_path = "dialog4/publish_e2e.dlg"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.fls"
            info_dict = pack_build.patch_pack_copy(
                REAL_PACK, res_path, plain, out,
                extra_entries={IMAGE_PATH: IMAGE_BYTES}, allow_create=True)
            report = publish.verify_written_pack(
                src_pack=REAL_PACK, out_path=out, res_path=res_path,
                extras={IMAGE_PATH: IMAGE_BYTES}, expected_dicts=expected,
                info=info_dict, read_back=core_read_back)
            self.assertTrue(report["ok"], report)
            before = pack_build.parse_archive(REAL_PACK.read_bytes())
            self.assertEqual(report["entries_after"], len(before) + 2)
            # 新增布局 + 新增图片：原有条目一条都没被重写
            # （changed_entries 只统计**原本就在包里**、且字节确实变了的条目）
            self.assertEqual(report["changed_entries"], 0)
            self.assertEqual(
                publish.classify_target_path(
                    REAL_PACK, res_path, plain).storage, "absent")
            # 对「编辑器自己写出的原生条目」再分类：明文一致 → 字节不变
            again = publish.classify_target_path(out, res_path, plain)
            self.assertEqual(again.storage, "native")
            self.assertFalse(again.layout_rewritten)
            self.assertTrue(again.byte_identical)
            # 复现 P2-1 的反面：无改动再保存一次，目标条目字节逐字节不变
            out2 = Path(tmp) / "out2.fls"
            pack_build.patch_pack_copy(out, res_path, plain, out2,
                                       extra_entries={IMAGE_PATH: IMAGE_BYTES})
            with FlsPack(out) as first, FlsPack(out2) as second:
                self.assertEqual(first.read_named(res_path),
                                 second.read_named(res_path))
            # 改一个字段 → 明确报「版式重写」
            dicts, _ = dlg_codec.parse_bytes(plain)
            dicts[0]["iWidth"] = dicts[0]["iWidth"] + 1
            edited = dlg_codec.dump_bytes(dicts)
            self.assertTrue(
                publish.classify_target_path(
                    out, res_path, edited).layout_rewritten)


class SaveEncodingTests(unittest.TestCase):
    """写回前的编码闸门（原来在窗口里，现在可脱窗测试）。"""

    @staticmethod
    def clean_doc() -> LayoutDocument:
        return LayoutDocument.from_dicts([{
            "sWidgetType": "CMainFrame", "sName": "root",
            "iWidth": 10, "iHeight": 10,
        }], None)

    def test_clean_document_and_extras_pass(self):
        publish.require_save_encoding(self.clean_doc(),
                                      {IMAGE_PATH: IMAGE_BYTES})

    def test_unencodable_extra_name_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            publish.require_save_encoding(
                self.clean_doc(), {"dialog4/bad\u2603.png": IMAGE_BYTES})
        self.assertIn("GBK", str(ctx.exception))

    def test_unencodable_layout_field_is_rejected(self):
        doc = LayoutDocument.from_dicts([{
            "sWidgetType": "CButton", "sName": "b",
            "sFileName": "images/\u2603.png",
        }], None)
        issues = publish.save_encoding_issues(doc, {})
        self.assertEqual([issue.code for issue in issues], ["ENCODING"])
        with self.assertRaises(ValueError):
            publish.require_save_encoding(doc, {})


class SaveReviewPlanTests(unittest.TestCase):
    """保存前清单的数据部分（图片行/提示），原先混在窗口方法里。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = Path(self.tmp.name) / "pack.fls"
        # 包里已有 IMAGE_PATH（应判为「替换图片」），没有 NEW_PATH
        write_pack(self.pack, [entry(LAYOUT_ID, b"layout"),
                               entry(IMAGE_ID, IMAGE_BYTES)])

    def plan(self, **kwargs) -> publish.SavePlan:
        staged = kwargs.pop("staged", {
            IMAGE_PATH: IMAGE_BYTES, NEW_PATH: b"new", "dialog4/idle.png": b"x"})
        extras = kwargs.pop("extras", {
            IMAGE_PATH: IMAGE_BYTES, NEW_PATH: b"new"})
        params = dict(target="out.fls", to_pack=True, issues=[], staged=staged,
                      extras=extras, pack_path=self.pack, res_path=RES_PATH)
        params.update(kwargs)
        return publish.save_review_plan(**params)

    def test_pack_plan_labels_replaced_added_and_unreferenced(self):
        plan = self.plan()
        rows = {name: kind for kind, name, _size in plan.images}
        self.assertEqual(rows[IMAGE_PATH], "替换图片")
        self.assertEqual(rows[NEW_PATH], "新增图片")
        self.assertEqual(rows["dialog4/idle.png"], "未引用，跳过并保留待入包")
        sizes = {name: size for _kind, name, size in plan.images}
        self.assertEqual(sizes[NEW_PATH], 3)

    def test_pending_import_notice_says_added_or_replaced(self):
        plan = self.plan(pending_pack_import=True)      # 布局已在包里 → 替换
        self.assertIn("替换 " + RES_PATH, plan.notice)
        plan = self.plan(pending_pack_import=True,
                         res_path="dialog4/brand_new.dlg")   # 包里没有 → 新增
        self.assertIn("新增 dialog4/brand_new.dlg", plan.notice)

    def test_loose_save_lists_everything_as_not_embedded(self):
        plan = self.plan(to_pack=False, pack_path=None)
        self.assertEqual(plan.notice, "")
        self.assertTrue(plan.images)
        self.assertTrue(all(kind == "散装保存不嵌入，保留待入包"
                            for kind, _name, _size in plan.images))

    def test_extra_encoding_issues_only_added_for_pack_saves(self):
        bad = {"dialog4/bad\u2603.png": b"x"}
        self.assertEqual(len(self.plan(extras=bad, staged=bad).issues), 1)
        self.assertEqual(
            len(self.plan(to_pack=False, extras=bad, staged=bad).issues), 0)


def legacy_cipher(plain: bytes, key: bytes = b"\x11\x22\x33\x44") -> bytes:
    """旧版编辑器写出的 4 字节循环 XOR 密文（0.5.2 之前那条路）。

    读取兼容侧从密文头 4 字节反推密钥（假定明文以 ``# -*-`` 开头），
    所以任取非零 key 都能被 :func:`plain_if_layout` 认出来；key 全零
    时密文等于明文，按明文归类（两种写法本来就分不开）。
    """
    repeated = (key * (len(plain) // 4 + 1))[:len(plain)]
    return bytes(a ^ b for a, b in zip(plain, repeated, strict=True))


class TargetWriteTests(unittest.TestCase):
    """目标条目会被怎么写（分析报告 P2-1 的落地，零 Qt）。"""

    ENTRY_ID = LAYOUT_ID
    PLAIN = HEADER + b'\n# MD5: 0\n\nUI_INFO = [\n\t{\n\t\t"sWidgetType"' \
        b': "CMainFrame",\n\t\t"sName": "tw",\n\t},\n]\n'

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def pack_with(self, stored: bytes | None) -> Path:
        path = self.root / "pack.fls"
        entries = [] if stored is None else [entry(self.ENTRY_ID, stored)]
        entries.append(entry(OTHER_ID, b"\x89PNG not a layout"))
        write_pack(path, entries)
        return path

    def classify(self, stored: bytes | None, plain: bytes | None = None):
        return publish.classify_target_write(
            stored, self.ENTRY_ID, self.PLAIN if plain is None else plain)

    def test_absent_entry_is_a_new_layout(self):
        result = self.classify(None)
        self.assertEqual(result.storage, "absent")
        self.assertFalse(result.layout_rewritten)
        self.assertIn("新增", result.summary)

    def test_native_same_plain_keeps_entry_bytes(self):
        stored = encode_layout(self.PLAIN, self.ENTRY_ID)
        result = self.classify(stored)
        self.assertEqual(result.storage, "native")
        self.assertFalse(result.layout_rewritten)
        self.assertFalse(result.migrated)
        self.assertTrue(result.byte_identical)
        self.assertIn("字节不变", result.summary)

    def test_native_different_plain_is_a_layout_rewrite(self):
        stored = encode_layout(legacy_style_plain(), self.ENTRY_ID)
        result = self.classify(stored)          # 新明文是编辑器序列化结果
        self.assertEqual(result.storage, "native")
        self.assertTrue(result.layout_rewritten)
        self.assertIn("版式按编辑器序列化重写", result.summary)

    def test_plaintext_storage_migrates_without_rewrite(self):
        result = self.classify(self.PLAIN)
        self.assertEqual(result.storage, "plaintext")
        self.assertEqual((result.migrated, result.layout_rewritten), (True, False))
        self.assertIn("迁移为原生路径密钥", result.summary)

    def test_legacy_key_storage_migrates_and_may_rewrite(self):
        stored = legacy_cipher(self.PLAIN)
        self.assertEqual(plain_if_layout(stored), self.PLAIN)  # 读取兼容认得
        result = self.classify(stored)
        self.assertEqual(result.storage, "legacy")
        self.assertTrue(result.migrated)
        self.assertFalse(result.layout_rewritten)
        self.assertIn("旧密钥存储", result.summary)

    def test_unreadable_storage_is_reported_not_guessed(self):
        result = self.classify(b"\x89PNG\r\n\x1a\n" + b"x" * 40)
        self.assertEqual(result.storage, "unreadable")
        self.assertIn("拒绝替换", result.summary)

    def test_classify_target_path_reads_the_source_pack(self):
        stored = encode_layout(self.PLAIN, self.ENTRY_ID)
        pack = self.pack_with(stored)
        result = publish.classify_target_path(pack, RES_PATH, self.PLAIN)
        self.assertEqual(result.storage, "native")
        self.assertTrue(result.byte_identical)
        # 路径不在包里 → 新增；图片条目 → 不可识别（写回会拒绝）
        self.assertEqual(
            publish.classify_target_path(pack, "ui/missing.dlg",
                                         self.PLAIN).storage, "absent")
        self.assertEqual(
            publish.classify_target_path(pack, "dialog4/other.png",
                                         self.PLAIN).storage, "unreadable")

    def test_plan_carries_target_summary_first(self):
        stored = encode_layout(legacy_style_plain(), self.ENTRY_ID)
        pack = self.pack_with(stored)
        plan = publish.save_review_plan(
            target="out.fls", to_pack=True, issues=[],
            staged={}, extras={}, pack_path=pack, res_path=RES_PATH,
            new_plain=self.PLAIN)
        self.assertIsNotNone(plan.target_write)
        self.assertEqual(plan.target_write.storage, "native")
        self.assertTrue(plan.notice.startswith("目标条目："))


def legacy_style_plain() -> bytes:
    """一份「非编辑器版式」的等价布局：字段顺序与写法都不同，结构一致。"""
    return (HEADER + b"\n# MD5: 0123456789abcdef\n\nUI_INFO = [\n"
            b'    {\n        "sName": "tw",\n'
            b'        "sWidgetType": "CMainFrame",\n    },\n]\n')


if __name__ == "__main__":
    unittest.main()
