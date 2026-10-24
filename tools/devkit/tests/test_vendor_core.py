"""``mx_common/`` 与编辑器副本的分发一致性测试。

背景（`docs/analysis/ui_editor_analysis_20261016.md` P1-2）：同一份格式代码
曾在两个编辑器里各存一份、靠人记得同步。现在真源在 ``mx_common/``，副本由
``tools/devkit/vendor_core.py`` 生成——本测试把「必须同步」变成机器判定。
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

DEVKIT = Path(__file__).resolve().parents[1]
REPO_ROOT = DEVKIT.parents[1]
if str(DEVKIT) not in sys.path:
    sys.path.insert(0, str(DEVKIT))

import vendor_core  # noqa: E402


class VendorDriftTests(unittest.TestCase):
    def test_repo_copies_match_mx_common(self):
        """仓库里 8 份副本必须与真源逐字节一致（改真源后忘了分发即红）。"""
        problems = vendor_core.check()
        self.assertEqual(
            problems, [],
            "副本漂移：\n  - " + "\n  - ".join(problems)
            + "\n修复：python3 tools/devkit/vendor_core.py --write")

    def test_banner_and_body_are_verbatim(self):
        """副本 = 生成横幅 + 真源全文（横幅不得吞掉模块 docstring）。"""
        for path, wanted in vendor_core.expected_files().items():
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                text = vendor_core.load_text(path)
                self.assertTrue(text.startswith("# 自动生成，请勿手改："))
                name = wanted.split("mx_common/", 1)[1].split(" 复制")[0]
                self.assertEqual(text, vendor_core.rendered(name))
                body = text.split("\n", 4)[4]
                self.assertTrue(body.startswith('"""'),
                                "横幅之后应当仍是模块 docstring")

    def test_write_is_idempotent(self):
        """干净树上 --write 不应改动任何文件（否则说明比较规则不稳定）。

        在临时目录复刻「真源 + 已分发副本」后验证，不直接写真实仓库：
        本测试曾对仓库树跑 write()，把 9 份副本改写成的 LF 与 Windows
        autocrlf 检出的 CRLF 互相打架，工作树被写脏
        （docs/analysis/windows_acceptance_20261024.md §5.1）。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "mx_common"
            source.mkdir()
            for name in vendor_core.DESTINATIONS:
                shutil.copyfile(vendor_core.SOURCE_DIR / name, source / name)
            with mock.patch.object(vendor_core, "REPO_ROOT", root), \
                    mock.patch.object(vendor_core, "SOURCE_DIR", source):
                first = vendor_core.write()
                self.assertEqual(
                    len(first), len(vendor_core.expected_files()),
                    "临时树首次分发应写下全部副本")
                self.assertEqual(
                    vendor_core.write(), [],
                    "第二次 --write 必须是空操作（读/写规则必须自洽）")
                self.assertEqual(vendor_core.check(), [])

    def test_crlf_checkout_is_not_drift(self):
        """回归：CRLF 检出（Windows autocrlf）不得判为漂移，也不该被「修」。

        行尾由签出策略决定，不是内容变更；比较必须发生在行尾归一化之后。
        旧实现按字节读，CRLF 副本必报漂移——本测试即复现该旧 bug。
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "mx_common"
            source.mkdir()
            for name in vendor_core.DESTINATIONS:
                shutil.copyfile(vendor_core.SOURCE_DIR / name, source / name)
            with mock.patch.object(vendor_core, "REPO_ROOT", root), \
                    mock.patch.object(vendor_core, "SOURCE_DIR", source):
                vendor_core.write()
                for path in vendor_core.expected_files():
                    path.write_bytes(
                        path.read_bytes().replace(b"\n", b"\r\n"))
                self.assertEqual(vendor_core.check(), [])
                self.assertEqual(vendor_core.write(), [])
                self.assertEqual(vendor_core.diff(), "")

    def test_check_detects_and_write_repairs_drift(self):
        """钉子测试：故意改一个字符，--check 必须报出来，--write 必须修回。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "mx_common"
            source.mkdir()
            (source / "mxhash.py").write_text(
                '"""真源。"""\n\nVALUE = 1\n', encoding="utf-8")
            target = root / "tool" / "core" / "mxhash.py"
            target.parent.mkdir(parents=True)
            target.write_text("# 已经漂移\nVALUE = 2\n", encoding="utf-8")
            with mock.patch.object(vendor_core, "REPO_ROOT", root), \
                    mock.patch.object(vendor_core, "SOURCE_DIR", source), \
                    mock.patch.object(vendor_core, "DESTINATIONS",
                                      {"mxhash.py": ("tool/core/mxhash.py",)}):
                self.assertEqual(len(vendor_core.check()), 1)
                changed = vendor_core.write()
                self.assertEqual(changed, [target])
                self.assertEqual(vendor_core.check(), [])

    def test_shared_sources_stay_dependency_free(self):
        """真源只能依赖标准库：core 层不许 import Qt/Pillow，否则副本会拖垮它。"""
        banned = ("PySide6", "PyQt", "PIL")
        for name in vendor_core.DESTINATIONS:
            text = vendor_core.load_text(vendor_core.SOURCE_DIR / name)
            for module in banned:
                with self.subTest(module=name, banned=module):
                    self.assertNotIn(f"import {module}", text)
                    self.assertNotIn(f"from {module}", text)


if __name__ == "__main__":
    unittest.main()
