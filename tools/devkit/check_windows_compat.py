#!/usr/bin/env python3
"""Windows 兼容性静态检查：在 Linux 上开发、交付到 Windows 之前必跑。

    python3 tools/devkit/check_windows_compat.py                 # 整个仓库
    python3 tools/devkit/check_windows_compat.py resource_editor # 只看某个工具目录
    python3 tools/devkit/check_windows_compat.py --since origin/master --strict
    python3 tools/devkit/check_windows_compat.py --json report.json
    python3 tools/devkit/check_windows_compat.py --list-rules

退出码：0 = 没有需要处理的发现；1 = 有 ERROR（``--strict`` 时 WARNING 也算）；
2 = 参数错误。规则说明与人工清单见 ``docs/PYTHON_TOOL_CONVENTIONS.md`` §5。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from wincompat import RULES, CheckOptions, Severity, run_checks  # noqa: E402
from wincompat.runner import DEFAULT_EXCLUDES, git_root  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_windows_compat.py",
        description=(
            "检查文件名、.bat 脚本与 Python 源码里会在 Windows 上出问题的地方。"
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="要检查的目录或文件（相对当前目录），默认整个仓库",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="仓库根目录（默认自动用 git 顶层目录，不在仓库里时用当前目录）",
    )
    parser.add_argument(
        "--since",
        metavar="REF",
        help="只扫描相对该 git 引用有改动的文件（文件名检查仍看全量）",
    )
    parser.add_argument("--strict", action="store_true", help="WARNING 也导致退出码 1")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="追加排除（目录前缀以 / 结尾，或 fnmatch 模式）；可重复",
    )
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help=f"不使用默认排除 {', '.join(DEFAULT_EXCLUDES)}",
    )
    parser.add_argument(
        "--no-git", action="store_true", help="不用 git 列文件，直接遍历目录"
    )
    parser.add_argument("--json", type=Path, metavar="FILE", help="把结果另存为 JSON")
    parser.add_argument("--quiet", action="store_true", help="只打印汇总")
    parser.add_argument("--list-rules", action="store_true", help="列出规则后退出")
    return parser


def _print_rules() -> None:
    for code, (severity, title) in RULES.items():
        print(f"{code}  {severity.name:7}  {title}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.list_rules:
        _print_rules()
        return 0

    root = args.root or git_root(Path.cwd()) or Path.cwd()
    if not root.is_dir():
        parser.error(f"根目录不存在：{root}")

    excludes = () if args.no_default_excludes else DEFAULT_EXCLUDES
    options = CheckOptions(
        root=root,
        paths=args.paths,
        since=args.since,
        excludes=tuple(excludes) + tuple(args.exclude),
        use_git=not args.no_git,
    )
    result = run_checks(options)

    if not args.quiet:
        for finding in result.findings:
            print(finding.format())
    counts = Counter(f.severity for f in result.findings)
    print(
        f"[wincompat] 根目录 {root}；文件列表来源 {result.source}；"
        f"文件名检查 {result.listed_paths} 项，"
        f"源码/脚本扫描 {result.scanned_files} 个；"
        f"ERROR {counts[Severity.ERROR]}，WARNING {counts[Severity.WARNING]}，"
        f"INFO {counts[Severity.INFO]}"
    )
    if args.json:
        payload = {
            "root": str(root),
            "source": result.source,
            "scanned_files": result.scanned_files,
            "listed_paths": result.listed_paths,
            "findings": [f.as_dict() for f in result.findings],
        }
        args.json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return result.exit_code(strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
