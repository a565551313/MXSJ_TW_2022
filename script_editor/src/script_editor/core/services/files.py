"""Source/project/output IO with alias protection and atomic publication."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from pathlib import Path


def guard_output(path: Path, protected: Iterable[Path] = ()) -> Path:
    path = Path(path).absolute()
    if path.suffix.lower() == ".fls":
        raise ValueError("普通文档IO禁止写FLS；须使用受限原生构建入口")
    if path.is_symlink():
        raise ValueError("拒绝覆盖符号链接")
    for source in protected:
        source = Path(source)
        if path.resolve() == source.resolve() or (
            path.exists() and source.exists() and path.samefile(source)
        ):
            raise ValueError("输出不能是输入或其别名")
    return path


def atomic_write(path: Path, data: bytes, protected: Iterable[Path] = ()) -> None:
    protected = tuple(protected)
    path = guard_output(path, protected)
    fd, temporary = tempfile.mkstemp(prefix=".mxscript-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        guard_output(path, protected)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_source(path: Path) -> str:
    # Strict UTF-8 only. Never silently decode Big5/GBK and rewrite the file.
    return path.read_text(encoding="utf-8-sig")


def save_source(path: Path, text: str, protected: Iterable[Path] = ()) -> None:
    if path.suffix.lower() != ".py":
        raise ValueError("源码必须保存为.py；源码与包输出分离")
    atomic_write(path, text.encode("utf-8"), protected)


def save_new_source(path: Path, text: str, protected: Iterable[Path] = ()) -> None:
    """Publish a new .py without overwriting any existing path, including races."""
    if path.suffix.lower() != ".py":
        raise ValueError("源码必须保存为.py")
    protected = tuple(protected)
    path = guard_output(path, protected)
    if path.exists() or path.is_symlink():
        raise FileExistsError("请选择尚不存在的源码文件名，不覆盖已有文件")
    fd, temporary = tempfile.mkstemp(prefix=".mxsource-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(text.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        guard_output(path, protected)
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
