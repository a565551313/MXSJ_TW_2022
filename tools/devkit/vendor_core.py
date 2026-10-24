#!/usr/bin/env python3
"""把 ``mx_common/`` 的共享模块分发（复制）到各编辑器的 ``core/`` 下。

为什么是复制：编辑器要能在一个只有 Python + PySide6 的目录里双击运行
（``bootstrap.py`` 不 ``pip install`` 本仓库的任何包），见 ``mx_common/README.md``。
本脚本把「多处副本」这件事变成**可校验的机械操作**：副本 = 生成横幅 + 真源全文，
行尾归一化后比对（CRLF/CR 一律按 LF 语义比较，签出行尾不算漂移），写入恒为 LF，
漂移即失败。

用法（仓库根目录）：

* ``python3 tools/devkit/vendor_core.py --check``  只校验，0 = 没有漂移（退出码 0/1）
* ``python3 tools/devkit/vendor_core.py --diff``   打印漂移的 unified diff
* ``python3 tools/devkit/vendor_core.py --write``  按真源重写副本
* ``python3 tools/devkit/vendor_core.py --list``   列出分发关系

``tools/devkit/tests/test_vendor_core.py`` 会在单元测试里跑 ``--check``，
所以漂移在测试里就红，不依赖人记得跑。
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "mx_common"

BANNER_TEMPLATE = (
    "# 自动生成，请勿手改：由 tools/devkit/vendor_core.py 从\n"
    "# mx_common/{name} 复制（字节相同）。\n"
    "# 改共享逻辑：改 mx_common/{name} → --write；校验：--check\n"
    "# 详细说明见 mx_common/README.md。\n"
)

#: 模块名 -> 分发目标（相对仓库根）
DESTINATIONS: dict[str, tuple[str, ...]] = {
    "mxhash.py": (
        "ui_editor/src/ui_editor/core/mxhash.py",
        "resource_editor/src/resource_editor/core/mxhash.py",
        "script_editor/src/script_editor/core/mxhash.py",
    ),
    "native_layout.py": (
        "ui_editor/src/ui_editor/core/native_layout.py",
        "resource_editor/src/resource_editor/core/native_layout.py",
    ),
    "output_paths.py": (
        "ui_editor/src/ui_editor/core/output_paths.py",
        "resource_editor/src/resource_editor/core/output_paths.py",
    ),
    "sprite_format.py": (
        "ui_editor/src/ui_editor/core/sprite_format.py",
        "resource_editor/src/resource_editor/core/sprite_format.py",
    ),
}


def load_text(path: Path) -> str:
    """按通用行尾读文本：CRLF/CR/LF 一律归一成 ``\\n`` 再参与比较。

    行尾由签出策略决定（Windows ``core.autocrlf=true`` 会把检出的文本
    统一改成 CRLF），不是内容变更；按字节读会把 CRLF 检出误判成副本
    漂移（docs/analysis/windows_acceptance_20261024.md §5.1）。
    """
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def store_text(path: Path, text: str) -> None:
    """恒写 LF（与真源一致，不受 OS 行尾影响）。"""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def rendered(name: str) -> str:
    """真源 + 生成横幅（横幅在最前，保持模块 docstring 仍是第一条语句）。"""
    return BANNER_TEMPLATE.format(name=name) + load_text(SOURCE_DIR / name)


def expected_files() -> dict[Path, str]:
    """{仓库内绝对路径: 期望内容}。"""
    plan: dict[Path, str] = {}
    for name, targets in DESTINATIONS.items():
        text = rendered(name)
        for rel in targets:
            plan[REPO_ROOT / rel] = text
    return plan


def missing_sources() -> list[str]:
    return [name for name in DESTINATIONS
            if not (SOURCE_DIR / name).is_file()]


def check() -> list[str]:
    """返回漂移说明列表；空列表 = 一致。"""
    problems: list[str] = []
    for name in missing_sources():
        problems.append(f"真源缺失：mx_common/{name}")
    for path, wanted in expected_files().items():
        rel = path.relative_to(REPO_ROOT)
        if not path.is_file():
            problems.append(f"副本缺失：{rel}")
            continue
        actual = load_text(path)
        if actual != wanted:
            problems.append(f"副本与真源不一致：{rel}")
    return problems


def write() -> list[Path]:
    """按真源重写全部副本，返回被改动的路径。"""
    changed: list[Path] = []
    for path, wanted in expected_files().items():
        if path.is_file() and load_text(path) == wanted:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        store_text(path, wanted)
        changed.append(path)
    return changed


def diff() -> str:
    """漂移处的 unified diff（真源 → 现文件）。"""
    chunks: list[str] = []
    for path, wanted in expected_files().items():
        rel = str(path.relative_to(REPO_ROOT))
        actual = load_text(path) if path.is_file() else ""
        if actual == wanted:
            continue
        chunks.append("".join(difflib.unified_diff(
            actual.splitlines(keepends=True),
            wanted.splitlines(keepends=True),
            fromfile=f"{rel} (现文件)",
            tofile=f"{rel} (应为：mx_common 真源)",
        )))
    return "".join(chunks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="mx_common/ → 编辑器 core/ 的共享模块分发器")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="只校验（默认），有漂移时退出码 1")
    group.add_argument("--write", action="store_true", help="按真源重写副本")
    group.add_argument("--diff", action="store_true", help="打印漂移的 diff")
    group.add_argument("--list", action="store_true", help="列出分发关系")
    args = parser.parse_args(argv)

    if args.list:
        for name, targets in DESTINATIONS.items():
            print(f"mx_common/{name}")
            for rel in targets:
                print(f"    -> {rel}")
        return 0

    if args.write:
        changed = write()
        for path in changed:
            print(f"已写入 {path.relative_to(REPO_ROOT)}")
        print(f"共 {len(changed)} 个副本被更新"
              f"（真源 {len(DESTINATIONS)} 个模块）。")
        return 0

    if args.diff:
        text = diff()
        print(text if text else "没有漂移。")
        return 1 if text else 0

    problems = check()
    if problems:
        print("[vendor_core] 发现漂移（应改 mx_common/ 真源后重新分发）：",
              file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        print("  修复：python3 tools/devkit/vendor_core.py --write",
              file=sys.stderr)
        return 1
    print(f"[vendor_core] OK：{len(DESTINATIONS)} 个模块的副本与 mx_common/ "
          f"真源逐字节一致（共 {len(expected_files())} 份副本）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
