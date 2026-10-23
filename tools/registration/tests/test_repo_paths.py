"""仓库路径在 Windows 上必须可检出。

2026-10-23 的实事故：`tools/registration/photo\\register_diag.txt` 被提交进仓库
（反斜杠是文件名的一部分）。POSIX 允许这种名字，Windows 不允许，于是别人
`git pull` 时整个检出被中止：

    error: invalid_path 'tools/registration/photo\\register_diag.txt'

成因是 `register.py` 的 `_Diag()` 写死 Windows 路径 `photo\\register_diag.txt`，
而 `harness.py2` 在 POSIX 上就地运行它，反斜杠被当成普通字符。修法：
harness 先 chdir 到 `out/harness/` 再执行，`tools/registration/.gitignore` 再加
`photo*` 兜底；本文件负责「谁再提交这种路径就挂测试」。
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
HARNESS = HERE / "harness.py2"

# Windows 文件名里不允许的字符（/ 是分隔符，不在此列），外加控制字符。
BAD_CHARS = re.compile(r'[<>:"\\|?*\x00-\x1f]')
# 保留设备名，任何扩展名都不行。
RESERVED = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$", re.IGNORECASE)


def tracked_paths() -> list[str]:
    """索引里的所有路径（相对仓库根，正斜杠）。

    用 `ls-files` 而不是 `ls-tree HEAD`：它反映的是「下一次提交会带上的东西」，
    所以刚 `git add` 了坏路径、还没提交时就能拦住。
    """
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True,
        check=True,
    ).stdout
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


class RepoPathsTest(unittest.TestCase):
    def test_no_tracked_path_contains_backslash(self):
        """反斜杠会让 Windows 检出直接失败（invalid_path）。"""
        bad = [p for p in tracked_paths() if "\\" in p]
        self.assertEqual(bad, [], f"这些路径在 Windows 上无法检出：{bad}")

    def test_tracked_paths_are_windows_portable(self):
        """字符集、结尾点/空格、保留设备名——这三类都会让 Windows 拒收。"""
        bad = []
        for path in tracked_paths():
            for part in path.split("/"):
                if BAD_CHARS.search(part) or part.endswith((".", " ")):
                    bad.append((path, part))
                    break
                if RESERVED.match(part):
                    bad.append((path, part))
                    break
        self.assertEqual(bad, [], f"这些路径在 Windows 上无法检出：{bad}")

    def test_harness_writes_outside_the_repo(self):
        """harness 必须先 chdir 到 out/harness，再 exec 被测模块。

        顺序错了日志就会落在仓库目录里（名字带反斜杠），正是这次事故的成因。
        """
        source = HARNESS.read_text(encoding="utf-8")
        chdir_at = source.index("os.chdir(_WORKDIR)")
        exec_at = source.index("exec code in g")
        self.assertLess(chdir_at, exec_at, "chdir 必须在 exec 之前")
        # 落到 out/ 下面（该目录已在 .gitignore 里）。
        self.assertIn("_HARNESS_DIR, 'out', 'harness'", source)

    def test_diag_log_pattern_is_ignored(self):
        """`photo*` 必须在 .gitignore 里兜底，防止手动 add 再犯。"""
        ignore = (HERE / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("photo*", ignore)

    def test_register_diag_path_is_still_the_windows_one(self):
        """`register.py` 里的 `_Diag` 路径不能改。

        它不是笔误：客户端是 Windows 程序，日志就该写 `photo\\register_diag.txt`。
        改了会让 `co_lnotab` 变、出货包哈希变（2026-10-23 已证实），
        所以治的是「怎么跑测试」，不是「代码里怎么写」。
        """
        source = (HERE / "register.py").read_text(encoding="utf-8")
        self.assertIn('open("photo\\\\register_diag.txt", "ab")', source)


if __name__ == "__main__":
    unittest.main()
