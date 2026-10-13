"""文件收集、调度与汇总。

优先用 ``git ls-files``（已跟踪 + 未忽略的新文件）拿到仓库视角的文件列表，
这样被 ``.gitignore`` 忽略的客户端二进制、虚拟环境不会被扫到；不在 git 仓库里
或没有 git 时退回到 ``os.walk``。
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from wincompat.batch import BATCH_SUFFIXES, check_batch_file
from wincompat.filenames import check_paths
from wincompat.model import Finding, Severity
from wincompat.pysource import check_python_bytes

#: 默认排除（相对根目录的前缀或 fnmatch 模式）。反编译输出是机器生成的线索文本，
#: 不是会交付到 Windows 的代码。
DEFAULT_EXCLUDES: tuple[str, ...] = (
    "tools/decompiler/output/",
    ".git/",
    "node_modules/",
    "__pycache__/",
    "dist/",
    "build/",
    ".venv/",
    "venv/",
)
SKIP_DIR_NAMES = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
)


@dataclass
class CheckOptions:
    root: Path
    paths: list[str] = field(default_factory=lambda: ["."])
    since: str | None = None
    excludes: tuple[str, ...] = DEFAULT_EXCLUDES
    use_git: bool = True


@dataclass
class CheckResult:
    findings: list[Finding]
    scanned_files: int
    listed_paths: int
    source: str  # "git" / "walk"

    def count(self, severity: Severity) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    def exit_code(self, strict: bool = False) -> int:
        threshold = Severity.WARNING if strict else Severity.ERROR
        return 1 if any(f.severity >= threshold for f in self.findings) else 0


# -- 文件列表 -------------------------------------------------------------


def _git(root: Path, *args: str) -> list[str] | None:
    """运行 git 并按 NUL 分隔返回输出；调用方自己放好 ``-z``（必须在 ``--`` 之前）。"""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    raw = completed.stdout.decode("utf-8", errors="surrogateescape")
    return [item for item in raw.split("\0") if item]


def git_root(start: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(completed.stdout.strip())


def list_repo_files(root: Path) -> list[str] | None:
    """已跟踪 + 未忽略的未跟踪文件（POSIX 相对路径）；不是 git 仓库时返回 None。"""
    return _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")


def list_changed_files(root: Path, since: str) -> list[str] | None:
    """相对 ``since`` 新增 / 修改 / 重命名的已跟踪文件 + 未忽略的未跟踪文件。"""
    changed = _git(root, "diff", "-z", "--name-only", "--diff-filter=ACMR", since, "--")
    if changed is None:
        return None
    untracked = _git(root, "ls-files", "-z", "--others", "--exclude-standard") or []
    return sorted(set(changed) | set(untracked))


def walk_files(root: Path) -> list[str]:
    found: list[str] = []
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR_NAMES)
        base = Path(current).relative_to(root).as_posix()
        for name in sorted(filenames):
            found.append(name if base == "." else f"{base}/{name}")
    return found


# -- 过滤 -----------------------------------------------------------------


def _normalize_prefix(root: Path, raw: str) -> str:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    try:
        rel = candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = Path(raw).as_posix()
    return "" if rel == "." else rel


def _excluded(rel: str, excludes: Iterable[str]) -> bool:
    for pattern in excludes:
        if pattern.endswith("/"):
            if rel.startswith(pattern) or f"/{pattern}" in f"/{rel}":
                return True
        elif fnmatch.fnmatch(rel, pattern) or rel == pattern:
            return True
    return False


def _under(rel: str, prefixes: list[str]) -> bool:
    for prefix in prefixes:
        if prefix == "" or rel == prefix or rel.startswith(prefix + "/"):
            return True
    return False


# -- 主流程 ---------------------------------------------------------------


def run_checks(options: CheckOptions) -> CheckResult:
    root = options.root.resolve()
    source = "walk"
    all_files: list[str] | None = None
    if options.use_git:
        all_files = list_repo_files(root)
        if all_files is not None:
            source = "git"
    if all_files is None:
        all_files = walk_files(root)

    all_files = [f for f in all_files if not _excluded(f, options.excludes)]
    prefixes = [_normalize_prefix(root, p) for p in options.paths]

    if options.since and source == "git":
        selected = list_changed_files(root, options.since) or []
        selected = [f for f in selected if not _excluded(f, options.excludes)]
    else:
        selected = list(all_files)
    selected = [f for f in selected if _under(f, prefixes) and (root / f).is_file()]

    findings: list[Finding] = []
    # 文件名检查永远看全量（大小写冲突需要完整目录视图），再按路径范围筛选输出。
    name_scope = [f for f in all_files if _under(f, prefixes)]
    findings.extend(check_paths(name_scope, root))

    scanned = 0
    for rel in selected:
        suffix = Path(rel).suffix.lower()
        if suffix == ".py":
            findings.extend(check_python_bytes(rel, (root / rel).read_bytes()))
        elif suffix in BATCH_SUFFIXES:
            findings.extend(check_batch_file(rel, (root / rel).read_bytes()))
        else:
            continue
        scanned += 1

    return CheckResult(
        findings=sorted(set(findings)),
        scanned_files=scanned,
        listed_paths=len(name_scope),
        source=source,
    )
