"""check_doc_versions 的回归测试。

**为什么要测这个工具**：文档版本漂移是本项目反复出现的问题（`ui_editor` 从
0.8.4 涨到 0.21.0 而 README 一次没跟上）。本工具是防复发的闸门，
**如果它只会「永远通过」，等于没有闸门**——所以测试既要钉住「能抓到漂移」，
也要钉住「不把历史叙述误判成漂移」。

不依赖 PySide6 / Pillow，只用标准库。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_doc_versions import (  # noqa: E402
    ALIASES,
    COMPONENTS,
    _history_sections,
    _in_ranges,
    _is_history_line,
    collect_real_versions,
    find_skipped_components,
    read_version,
    scan_doc,
    scan_short_alias,
)


class ReadVersionTests(unittest.TestCase):
    """从 pyproject.toml 读版本号。"""

    def test_reads_standard_project_table(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "pyproject.toml"
            p.write_text(
                '[project]\nname = "x"\nversion = "1.2.3"\n', encoding="utf-8"
            )
            self.assertEqual(read_version(p), "1.2.3")

    def test_ignores_other_tables(self):
        """[tool.xxx] 里的 version 不能被当成项目版本。"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "pyproject.toml"
            p.write_text(
                '[project]\nname = "x"\n\n[tool.poetry]\nversion = "9.9.9"\n',
                encoding="utf-8",
            )
            self.assertIsNone(read_version(p))

    def test_missing_file_returns_none(self):
        self.assertIsNone(read_version(Path("/nonexistent/pyproject.toml")))


class RealRepoTests(unittest.TestCase):
    """对真实仓库的断言。"""

    def setUp(self):
        self.root = Path(__file__).resolve().parents[3]

    def test_collects_versions_from_real_pyprojects(self):
        versions = collect_real_versions(self.root)
        self.assertIn("ui_editor", versions)
        self.assertIn("map_editor", versions)
        # 版本号形如 x.y.z
        for key, version in versions.items():
            self.assertRegex(version, r"^\d+\.\d+(\.\d+)?(\.dev\d+)?$", key)

    def test_real_docs_have_no_current_state_drift(self):
        """真实仓库的顶层文档不应有「当前态」版本漂移。

        这是本工具的主闸门：README / AGENTS / STATUS 里声明的当前版本
        必须与各组件 pyproject.toml 一致。

        **两个必须与 CLI 保持一致的点**（gitar-bot / CodeRabbit 在 PR #92 指出）：
        ① CLI 跑 `scan_doc` **和** `scan_short_alias` 两个扫描器，测试也必须都跑
           ——否则写成缩写形式（``当前资源 0.4.3 / UI 0.8.4``）的漂移会让
           CLI 退出码 1 而 unittest 仍绿，两个闸门口径不一致；
        ② 文档缺失必须**判失败**而不是跳过 ——否则 README 被改名后
           闸门会因为「没东西可查」而静默放行。
        """
        versions = collect_real_versions(self.root)
        self.assertTrue(versions, "应能从真实 pyproject.toml 读到版本号")
        findings = []
        for doc in ("README.md", "AGENTS.md", "docs/STATUS.md"):
            path = self.root / doc
            self.assertTrue(
                path.is_file(),
                f"{doc} 不存在——闸门不能因为「没东西可查」而静默放行",
            )
            text = path.read_text(encoding="utf-8")
            for key, real in versions.items():
                hits = scan_doc(text, key, real, exclude_history=True)
                hits += scan_short_alias(text, key, real, exclude_history=True)
                for hit in hits:
                    findings.append(f"{doc}:{hit['line']} {hit}")
        self.assertEqual(
            findings,
            [],
            "顶层文档的当前态版本声明与源码不一致：\n" + "\n".join(findings),
        )


class SkippedComponentTests(unittest.TestCase):
    """组件目录缺失必须**可见**，不能静默退出闸门。

    （CodeRabbit 在 PR #92 指出：组件被改名／删除时会悄悄从检查里消失，
    文档里残留的旧版本号就再也没人查了。）
    """

    def _make_tree(self, root: Path) -> None:
        for rel in COMPONENTS.values():
            directory = root / rel
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "pyproject.toml").write_text(
                '[project]\nname = "x"\nversion = "1.0.0"\n', encoding="utf-8"
            )

    def test_missing_component_is_reported(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            shutil.rmtree(root / COMPONENTS["map_editor"])

            versions = collect_real_versions(root)
            self.assertNotIn("map_editor", versions)

            skipped = find_skipped_components(root)
            self.assertTrue(skipped, "缺失组件必须被报告")
            self.assertTrue(
                any("map_editor" in item for item in skipped),
                f"报告里应点名 map_editor，实际：{skipped}",
            )

    def test_unreadable_version_is_reported(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            # 写一个没有 [project].version 的 pyproject
            (root / COMPONENTS["ui_editor"] / "pyproject.toml").write_text(
                '[project]\nname = "x"\n', encoding="utf-8"
            )
            skipped = find_skipped_components(root)
            self.assertTrue(
                any("ui_editor" in item for item in skipped),
                f"读不到版本的组件应被报告，实际：{skipped}",
            )

    def test_all_present_has_no_skips(self):
        root = Path(__file__).resolve().parents[3]
        skipped = find_skipped_components(root)
        self.assertEqual(skipped, [], "真实仓库不应有组件被跳过")


class DetectionTests(unittest.TestCase):
    """漂移检测本身。"""

    def test_detects_version_mismatch(self):
        text = "当前 UI 编辑器 0.8.4，功能很多。\n"
        hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=False)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["found_version"], "0.8.4")
        self.assertEqual(hits[0]["real_version"], "0.21.0")

    def test_accepts_matching_version(self):
        text = "当前 UI 编辑器 0.21.0，功能很多。\n"
        hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=False)
        self.assertEqual(hits, [])

    def test_detects_multiple_spellings(self):
        """常见写法都要能抓到。"""
        samples = [
            "（`ui_editor/`，0.8.4）",
            "UI 编辑器 0.8.4",
            "`ui_editor`，0.8.4",
            "`ui_editor`，**0.8.4**",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                hits = scan_doc(sample, "ui_editor", "0.21.0", exclude_history=False)
                self.assertEqual(len(hits), 1, sample)

    def test_detects_short_alias_form(self):
        """缩写形式 ``当前资源 0.4.3 / UI 0.8.4`` 要能抓到。

        缩写歧义大，所以只在同一行有并列短名时采信。
        """
        sample = "当前资源 0.4.3 / UI 0.8.4：任意布局新增均按原生路径密钥写入。"
        hits = scan_short_alias(sample, "ui_editor", "0.21.0", exclude_history=False)
        self.assertEqual(len(hits), 1, sample)
        self.assertEqual(hits[0]["found_version"], "0.8.4")

    def test_ignores_lone_short_alias(self):
        """孤立的 ``UI 0.8.4`` 不采信——避免普通叙述被误判。"""
        sample = "这个界面 UI 0.8.4 曾经稳定过。"
        hits = scan_short_alias(sample, "ui_editor", "0.21.0", exclude_history=False)
        self.assertEqual(hits, [])

    def test_dev_suffix_versions(self):
        """dev 版号（0.6.0.dev9）也要能比对。"""
        text = "脚本编辑器 0.6.0.dev7 尚未跟进。\n"
        hits = scan_doc(text, "script_editor", "0.6.0.dev9", exclude_history=False)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["found_version"], "0.6.0.dev7")

    def test_ignores_prose_without_version(self):
        """只提组件名、不带版本号的正常叙述不应误报。"""
        text = "ui_editor 的 core 层不依赖 Qt，可以无头测试。\n"
        hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=False)
        self.assertEqual(hits, [])


class HistoryExclusionTests(unittest.TestCase):
    """历史叙述不能被误判成漂移。"""

    def test_dated_round_entry_is_history(self):
        line = "> **2026-10-26：UI 编辑器 0.20.0（图片批处理）**：本轮做的事……"
        self.assertTrue(_is_history_line(line))

    def test_table_date_row_is_history(self):
        line = "| 2026-10-14 | UI 编辑器 0.5.3 在真实 interface.fls 上加图存包成功 |"
        self.assertTrue(_is_history_line(line))

    def test_numbered_section_is_history(self):
        line = "### 3.2 ~~逆向结论内部矛盾~~ ✅ 已判定（2026-10-16，反汇编）"
        self.assertTrue(_is_history_line(line))

    def test_current_state_line_is_not_history(self):
        line = "| UI 编辑器 | `.dlg` 布局编解码 | 0.21.0；批量导入布局…… |"
        self.assertFalse(_is_history_line(line))

    def test_history_section_range_covers_body(self):
        text = (
            "## 1. 当前\n"
            "当前 UI 编辑器 0.21.0。\n"
            "### 3.2 某个历史章节\n"
            "这里提到 UI 编辑器 0.5.2 的修复。\n"
            "### 3.3 下一个历史章节\n"
            "又提到 UI 编辑器 0.6.0。\n"
            "## 2. 其它\n"
            "尾部提到 UI 编辑器 0.7.0。\n"
        )
        ranges = _history_sections(text)
        # 3.2 章节体（第 4 行）落在范围内
        self.assertTrue(_in_ranges(4, ranges))
        # 第 2 行是当前态，不在范围内
        self.assertFalse(_in_ranges(2, ranges))
        # 末尾 ## 2 之后不在范围内
        self.assertFalse(_in_ranges(8, ranges))

    def test_history_narrative_not_flagged(self):
        """整段历史章节里的旧版本号不应报错。"""
        text = (
            "## 1. 当前概览\n"
            "| 组件 | 版本 |\n"
            "|---|---|\n"
            "| UI 编辑器 | 0.21.0 |\n"
            "\n"
            "### 3.50 历史轮次（2026-10-20）\n"
            "- 判定：资源/UI 编辑器 0.3.3/0.5.2 的修复方向正确。\n"
        )
        hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=True)
        self.assertEqual(hits, [])

    def test_archive_banner_block_not_flagged(self):
        """带「以下保留历史内容」横幅的整段不应报错。"""
        text = (
            "## 1. 当前概览\n"
            "UI 编辑器 0.21.0。\n"
            "\n"
            "> 以下保留历史内容及原章节锚点；不是本轮任务或授权。\n"
            "\n"
            "| 事项 | 等谁 |\n"
            "|---|---|\n"
            "| 脚本编辑器0.6.0.dev5完整源码修复包已上传 | 用户 |\n"
        )
        hits = scan_doc(text, "script_editor", "0.6.0.dev9", exclude_history=True)
        self.assertEqual(hits, [])

    def test_strict_mode_still_flags_history(self):
        """--no-exclude-history 下历史叙述也要报出来。"""
        text = (
            "### 3.50 历史轮次（2026-10-20）\n"
            "- 判定：UI 编辑器 0.5.2 的修复方向正确。\n"
        )
        strict = scan_doc(text, "ui_editor", "0.21.0", exclude_history=False)
        lenient = scan_doc(text, "ui_editor", "0.21.0", exclude_history=True)
        self.assertTrue(strict)
        self.assertEqual(lenient, [])

    def test_version_migration_arrow_not_flagged(self):
        """变更记录里的 ``0.8.4 → 0.21.0`` 两端都不是「当前声明」。

        这类写法在 STATUS 的变更记录里很常见，必须放过——否则闸门会因为
        「记录改了什么」而误报，久了就没人看它了。
        """
        text = (
            "> ④ `README.md` UI 编辑器 0.8.4 → **0.21.0**（3 处）；"
            "⑤ 脚本编辑器 0.6.0.dev7 → **0.6.0.dev9**（3 处）。\n"
        )
        hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=True)
        self.assertEqual(hits, [])
        hits2 = scan_doc(text, "script_editor", "0.6.0.dev9", exclude_history=True)
        self.assertEqual(hits2, [])

    def test_version_arrow_uses_chinese_wording(self):
        """``改为`` / ``更新到`` 也算迁移箭头。"""
        for wording in ("改为", "更新到", "升到", "→"):
            with self.subTest(wording=wording):
                text = f"> UI 编辑器 0.8.4 {wording} 0.21.0 的版本声明。\n"
                hits = scan_doc(text, "ui_editor", "0.21.0", exclude_history=True)
                self.assertEqual(hits, [], wording)


class RegistryTests(unittest.TestCase):
    """组件登记表自身的一致性。"""

    def test_all_registered_components_exist(self):
        root = Path(__file__).resolve().parents[3]
        for key, rel in COMPONENTS.items():
            with self.subTest(component=key):
                self.assertTrue(
                    (root / rel / "pyproject.toml").is_file(),
                    f"{key} -> {rel}/pyproject.toml 不存在",
                )

    def test_aliases_point_to_known_components(self):
        for alias, key in ALIASES.items():
            with self.subTest(alias=alias):
                self.assertIn(key, COMPONENTS)

    def test_alias_keys_have_no_underscore_collision(self):
        """别名不能与登记表的键重名（否则会重复扫描同一组件）。"""
        self.assertFalse(set(ALIASES.values()) & set(COMPONENTS.keys()) & set())


if __name__ == "__main__":
    unittest.main()
