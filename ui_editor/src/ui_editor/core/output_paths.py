"""输出路径保护：识别文件别名，并约束导出目录边界（零 Qt）。"""
from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path


def guard_output(
    target: str | Path,
    sources: Iterable[str | Path],
    root: str | Path | None = None,
) -> None:
    """拒绝源文件、硬/软链接别名，以及越出导出根目录的目标。

    检查应在写入前执行；桌面工具假定输出目录不被其他进程恶意
    并发更换。已有文件符号链接一律拒绝，不跟随链接写入。
    """
    target = Path(target)
    resolved = target.resolve()
    if root is not None:
        try:
            resolved.relative_to(Path(root).resolve())
        except ValueError as exc:
            raise ValueError(f"输出路径越出导出目录：{target}") from exc
    for source in sources:
        source = Path(source)
        same = resolved == source.resolve()
        if not same and target.exists() and source.exists():
            same = os.path.samefile(target, source)
        if same:
            raise ValueError(f"拒绝覆盖源资源或其别名：{target}")
    if target.is_symlink():
        raise ValueError(f"拒绝写入符号链接：{target}")
