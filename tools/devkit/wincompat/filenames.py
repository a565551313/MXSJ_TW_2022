"""文件名 / 路径层面的 Windows 兼容检查。

输入是相对检查根目录的 POSIX 风格路径列表（通常来自 ``git ls-files``），
因此这里只看字符串本身，唯一碰文件系统的是符号链接判断。
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from wincompat.model import Finding, make_finding

ILLEGAL_CHARS = frozenset('<>:"|?*')
RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
#: 相对路径超过这个长度就提示：用户的仓库根已经是 ``D:\Lager\夢想世界\`` 这类目录，
#: 再加上 MAX_PATH=260 的限制，留 60 个字符给盘符和上级目录并不宽裕。
MAX_RELATIVE_PATH = 200


def _component_findings(rel: str, part: str) -> list[Finding]:
    findings: list[Finding] = []
    bad = sorted({ch for ch in part if ch in ILLEGAL_CHARS or ord(ch) < 32})
    if bad:
        shown = " ".join(repr(ch) for ch in bad)
        findings.append(make_finding(rel, 0, "WIN101", f"'{part}' 含 {shown}"))
    stem = part.split(".", 1)[0].upper()
    if stem in RESERVED_NAMES:
        findings.append(make_finding(rel, 0, "WIN102", f"'{part}'"))
    if part and part != part.rstrip(" ."):
        findings.append(make_finding(rel, 0, "WIN103", f"'{part}'"))
    return findings


def check_paths(rel_paths: Iterable[str], root: Path | None = None) -> list[Finding]:
    """检查一组相对路径。``root`` 给定时额外检查符号链接。"""
    findings: list[Finding] = []
    seen_lower: dict[str, str] = {}
    reported_collisions: set[str] = set()

    for rel in sorted(set(rel_paths)):
        parts = rel.split("/")
        for part in parts:
            findings.extend(_component_findings(rel, part))
        if len(rel) > MAX_RELATIVE_PATH:
            findings.append(make_finding(rel, 0, "WIN105", f"{len(rel)} 字符"))
        for depth in range(1, len(parts) + 1):
            prefix = "/".join(parts[:depth])
            key = prefix.lower()
            previous = seen_lower.setdefault(key, prefix)
            if previous != prefix and key not in reported_collisions:
                reported_collisions.add(key)
                findings.append(
                    make_finding(rel, 0, "WIN104", f"'{prefix}' 与 '{previous}'")
                )
        if root is not None and (root / rel).is_symlink():
            findings.append(make_finding(rel, 0, "WIN106"))
    return findings
