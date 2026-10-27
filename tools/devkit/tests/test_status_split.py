"""STATUS 拆分（当前状态 / 历史归档）的结构回归测试。

**为什么要有这个测试**：2026-10-27 把 `docs/STATUS.md` 的历史部分（§3 红灯
3.1–3.82、§4–§7 与历史轮次条目）拆到 `docs/archive/STATUS_HISTORY.md`。
拆分本身容易引入三类静默损坏：

1. **内容丢失**——搬运时少复制了段落；
2. **链接断裂**——正文相对链接随层级变化而失效；
3. **锚点失效**——外部引用 `§3.x` 找不到对应小节。

这个测试把这三条钉住。纯标准库，不依赖 PySide6 / Pillow。
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATUS = ROOT / "docs" / "STATUS.md"
HISTORY = ROOT / "docs" / "archive" / "STATUS_HISTORY.md"
ARCHIVE_README = ROOT / "docs" / "archive" / "README.md"

LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
HEADING = re.compile(r"^#{2,6}\s+(3\.\d+(?:\.\d+)?)\s", re.M)
ANCHOR = re.compile(r'<a id="(s3-[0-9\-]+)"></a>')

# 拆分时**有意**做过措辞微调的原文行。新增例外必须写明理由。
ALLOWED_REWORDED = (
    # 原句在 STATUS.md §2 末尾；拆到归档后该行不再位于「以下」的历史段之前，
    # 故去掉「以下」二字，语义不变。
    "- 以下旧 §4–§7 也是历史管理记录；当前等待项／下一步以本节为准。",
    # §2「脚本编辑器」这一行是**活的当前态声明**，必须跟着
    # `script_editor/pyproject.toml` 的版本走（`check_doc_versions.py` 会把它
    # 当成漂移报 ERROR）：0.6.0.dev12 落地时该单元格由 0.6.0.dev9 改为
    # 0.6.0.dev12，并补上宽松模式与 2026-10-27 的实测口径。
    # **这一行是唯一允许随版本更新的现有行**；原文仍可从 git 历史与
    # `docs/STATUS.md` 顶部 0.6.0.dev12 轮次条目查到，没有内容丢失。
    '| 脚本编辑器 | **0.6.0.dev9**，未登记包自动验证（逐条严格解码后采纳）、工作区四项修复、Python 3.15 按宿主选择 Qt、双 VM 原生构建 | 2026-10-23：本机 Linux 全量 **367 项：241 通过、120 跳过、4 失败、2 错误**；其中 4 失败/2 错误与 master 逐条相同（缺 `xdis`、无 Qt），非本轮引入。新增 12 项解码判定用例全过，含真实 r5/r4 包。GUI 新用例在本机无法执行（缺 Qt 运行库），Windows 未验，见 §3.15.9 |',
)


class SplitStructureTests(unittest.TestCase):
    """两份文件都存在，职责分明。"""

    def test_both_files_exist(self):
        self.assertTrue(STATUS.is_file(), "docs/STATUS.md 应存在")
        self.assertTrue(HISTORY.is_file(), "docs/archive/STATUS_HISTORY.md 应存在")

    def test_status_is_a_current_state_snapshot(self):
        """STATUS.md 应回到「当前状态快照」的体量，不该再是几千行。"""
        lines = STATUS.read_text(encoding="utf-8").splitlines()
        self.assertLess(
            len(lines),
            800,
            f"docs/STATUS.md 仍有 {len(lines)} 行，拆分目标没达到（应 <800 行）",
        )

    def test_history_holds_the_numbered_sections(self):
        """历史小节应搬到归档文件，且 §编号保持。"""
        text = HISTORY.read_text(encoding="utf-8")
        nums = set(HEADING.findall(text))
        self.assertGreater(len(nums), 80, "归档文件应含 80+ 个 §3.x 小节")
        for must in ("3.1", "3.2", "3.49", "3.51", "3.79", "3.81", "3.82"):
            self.assertIn(must, nums, f"归档文件应保留 §{must}")

    def test_status_links_to_history(self):
        """STATUS.md 必须指向归档文件，否则读者找不到历史。"""
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("STATUS_HISTORY.md", text)


class NoContentLostTests(unittest.TestCase):
    """拆分不能丢内容。"""

    # **拆分前的基线提交**（最后一次还含 4,334 行完整 STATUS.md 的提交）。
    #
    # ⚠️ 这里**不能**用 `HEAD`：拆分本身已被提交后，HEAD 里的
    # `docs/STATUS.md` 就是拆分后的 381 行版本，测试会拿新文件跟它自己比，
    # 永远通过、再也抓不到内容丢失（gitar-bot 在 PR #92 上指出的问题）。
    # 基线必须钉死到**拆分前**那一个提交。
    PRE_SPLIT_REV = "bc69491"

    def _original_status(self) -> str:
        proc = subprocess.run(
            ["git", "show", f"{self.PRE_SPLIT_REV}:docs/STATUS.md"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
        )
        if proc.returncode != 0:
            self.skipTest(
                f"取不到拆分前的 docs/STATUS.md（{self.PRE_SPLIT_REV} 不可达，"
                "可能是浅克隆或历史被改写）"
            )
        return proc.stdout

    def test_baseline_is_actually_the_pre_split_file(self):
        """**自证**：基线必须真的是拆分前那份 4,334 行的文件。

        防止有人把 `PRE_SPLIT_REV` 改成一个拆分后的提交，测试又变成
        「拿自己跟自己比」而静默通过。
        """
        original = self._original_status()
        lines = original.splitlines()
        self.assertGreater(
            len(lines),
            2000,
            f"{self.PRE_SPLIT_REV}:docs/STATUS.md 只有 {len(lines)} 行，"
            "不像拆分前的完整文件——基线可能指错了提交",
        )
        # 拆分前的文件应含已归档的 §3 小节标题
        self.assertIn(
            "## 3. 红灯与已知问题", original, "基线应含 §3 标题"
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """去 markdown 链接语法与标点，只留正文语义。"""
        text = re.sub(r"\[([^\]\n]*)\]\([^)\n]*\)", r"\1", text)
        text = re.sub(r"[`*_#>|<>（）()\[\]　\s]", "", text)
        return text

    def test_every_original_line_survives(self):
        """拆分前的每一行正文，都还能在两份新文件里找到。

        **允许的例外**：拆分时有 1 行做了措辞微调（把「以下旧 §4–§7 也是历史
        管理记录」改成「旧 §4–§7 也是历史管理记录」，因为新位置已不再是
        「以下」）。这类有意改动列在 `ALLOWED_REWORDED` 里显式登记，
        **新增例外必须写明理由**，不能默默放宽判定。
        """
        original = self._original_status()
        combined = self._normalize(
            STATUS.read_text(encoding="utf-8")
        ) + self._normalize(HISTORY.read_text(encoding="utf-8"))
        missing = []
        for index, line in enumerate(original.splitlines(), 1):
            stripped = line.strip()
            if not stripped:
                continue
            normalized = self._normalize(stripped)
            if not normalized:
                continue
            if normalized in combined:
                continue
            if any(self._normalize(old) == normalized for old in ALLOWED_REWORDED):
                continue
            missing.append((index, stripped[:120]))
        self.assertEqual(
            missing,
            [],
            "以下原文行在拆分后找不到对应内容：\n"
            + "\n".join(f"  {i}: {t}" for i, t in missing),
        )


class AnchorTests(unittest.TestCase):
    """§3.x 小节要有稳定锚点，供外部链接。"""

    def test_every_numbered_section_has_anchor(self):
        text = HISTORY.read_text(encoding="utf-8")
        anchors = set(ANCHOR.findall(text))
        for num in HEADING.findall(text):
            expected = "s3-" + num.replace(".", "-")
            self.assertIn(
                expected,
                anchors,
                f"§{num} 缺显式锚点 {expected}（外部链接会断）",
            )

    def test_anchors_are_unique(self):
        """锚点必须**唯一**。

        重名锚点会让后一个同名小节的链接**指不到**（浏览器只认第一个），
        而「锚点存在」的检查是过的——所以必须单独查重复。
        （拆分轮遗留：master 并行工作记录里的 `### 3.30` 与主线 `### 3.30`
        共用了 `s3-3-30`，已改为 `s3-master-3-30`。）
        """
        text = HISTORY.read_text(encoding="utf-8")
        seen: dict[str, int] = {}
        dupes: dict[str, list[int]] = {}
        for match in ANCHOR.finditer(text):
            line = text[: match.start()].count("\n") + 1
            anchor = match.group(1)
            seen[anchor] = seen.get(anchor, 0) + 1
            dupes.setdefault(anchor, []).append(line)
        repeated = {k: v for k, v in dupes.items() if len(v) > 1}
        self.assertEqual(
            repeated,
            {},
            "锚点重名会让后一个小节的链接指不到："
            + repr({k: v for k, v in sorted(repeated.items())}),
        )

    def test_all_external_anchors_resolve(self):
        """仓库里所有指向归档文件的锚点链接都必须能落地。"""
        broken = []
        for path in ROOT.rglob("*.md"):
            sp = path.as_posix()
            if ".git/" in sp:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(
                r"\]\(([^)\n]*STATUS_HISTORY\.md)#([A-Za-z0-9\-_]+)\)", text
            ):
                rel, anchor = match.group(1), match.group(2)
                target = (path.resolve().parent / rel).resolve()
                if not target.exists():
                    broken.append(f"{sp}: 文件不存在 {rel}")
                    continue
                if f'id="{anchor}"' not in target.read_text(encoding="utf-8"):
                    broken.append(f"{sp}: 锚点不存在 #{anchor}")
        self.assertEqual(broken, [], "锚点链接失效：\n" + "\n".join(broken))


class LinkTests(unittest.TestCase):
    """拆分后正文相对链接不能断。"""

    def test_archive_internal_links_resolve(self):
        """归档文件里的相对链接要按新层级修正。"""
        broken = []
        for match in LINK.finditer(HISTORY.read_text(encoding="utf-8")):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            base = target.split("#")[0]
            if not base:
                continue
            if not (HISTORY.resolve().parent / base).exists():
                broken.append(target)
        self.assertEqual(
            broken, [], "归档文件里失效的相对链接：\n" + "\n".join(sorted(set(broken)))
        )

    def test_status_internal_links_resolve(self):
        broken = []
        for match in LINK.finditer(STATUS.read_text(encoding="utf-8")):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            base = target.split("#")[0]
            if not base:
                continue
            if not (STATUS.resolve().parent / base).exists():
                broken.append(target)
        self.assertEqual(
            broken,
            [],
            "STATUS.md 里失效的相对链接：\n" + "\n".join(sorted(set(broken))),
        )


class NoDanglingStatusRefsTests(unittest.TestCase):
    """不该再有指向「已搬走的 STATUS §3.x」的裸引用。

    **判定范围**：只抓**指向 STATUS 的路径或链接**形式——
    ``STATUS.md` §3.1``、``[STATUS §3.5](docs/STATUS.md)``、``STATUS§3.51``。
    纯叙述里提到「STATUS 没有 §5.2」这类**说明性文字**不算悬挂引用，
    否则本文档自己在解释拆分规则时就会被自己的测试判为失败。
    """

    # 形如 `` `docs/STATUS.md` §3.1 `` —— 反引号里必须包着**路径**
    PATH_LIKE = re.compile(r"`[^`\n]*STATUS\.md`[^§\n]{0,12}§\s*(3\.\d+|[4-7])\b")
    # 形如 STATUS§3.51 —— 无空格粘连写法
    GLUED = re.compile(r"(?<![A-Z_])STATUS§\s*(3\.\d+|[4-7])\b")
    # Markdown 链接，标签里点名 STATUS
    MD_LINK = re.compile(
        r"\[(?P<label>[^\]\n]*STATUS[^\]\n]*)\]\((?P<target>[^)\n]*)\)"
    )

    def _offenders(self) -> list[str]:
        out: list[str] = []
        for path in ROOT.rglob("*.md"):
            sp = path.as_posix()
            if ".git/" in sp or sp.endswith("docs/archive/STATUS_HISTORY.md"):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for index, line in enumerate(text.splitlines(), 1):
                if "STATUS_HISTORY" in line:
                    continue
                hit = self.PATH_LIKE.search(line) or self.GLUED.search(line)
                if hit:
                    out.append(f"{sp}:{index} {line.strip()[:110]}")
                    continue
                for match in self.MD_LINK.finditer(line):
                    label = match.group("label")
                    target = match.group("target")
                    if "STATUS" not in label:
                        continue
                    if re.search(r"§\s*(3\.\d+|[4-7])\b", label) and (
                        "STATUS_HISTORY" not in label
                        and not target.rstrip("/").endswith("STATUS_HISTORY.md")
                    ):
                        out.append(f"{sp}:{index} {line.strip()[:110]}")
        return out

    def test_no_bare_refs_to_moved_sections(self):
        offenders = self._offenders()
        self.assertEqual(
            offenders,
            [],
            "以下引用仍指向已归档的 STATUS 小节，应改指 STATUS_HISTORY：\n"
            + "\n".join(offenders),
        )


class ArchiveIndexTests(unittest.TestCase):
    """归档文件要在归档索引里登记（项目归档约定第 2 条）。"""

    def test_registered_in_archive_readme(self):
        text = ARCHIVE_README.read_text(encoding="utf-8")
        self.assertIn("STATUS_HISTORY.md", text)
        self.assertIn("[STATUS_HISTORY.md](STATUS_HISTORY.md)", text)


if __name__ == "__main__":
    unittest.main()
