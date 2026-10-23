"""Source/project/output IO with alias protection and atomic publication."""

from __future__ import annotations

import hashlib
import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceRevision:
    """Raw disk digest, distinct from editor text and published module baselines."""

    sha256: str | None

    @classmethod
    def capture(cls, path: Path):
        digest = hashlib.sha256()
        try:
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except FileNotFoundError:
            return cls(None)
        return cls(digest.hexdigest())

    def verify(self, path: Path):
        if self != self.capture(path):
            raise ValueError(
                "源码已被外部修改、删除或新建；编辑内容保留，请先对比或另存，未覆盖磁盘文件"
            )


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


def atomic_write(
    path: Path,
    data: bytes,
    protected: Iterable[Path] = (),
    *,
    expected: SourceRevision | None = None,
) -> None:
    protected = tuple(protected)
    path = guard_output(path, protected)
    if expected is not None:
        expected.verify(path)
    fd, temporary = tempfile.mkstemp(prefix=".mxscript-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        guard_output(path, protected)
        if expected is not None:
            expected.verify(path)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_source(path: Path) -> str:
    # Strict UTF-8 only. Never silently decode Big5/GBK and rewrite the file.
    return read_source_snapshot(path)[0]


def read_source_snapshot(path: Path) -> tuple[str, SourceRevision]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return text, SourceRevision(hashlib.sha256(raw).hexdigest())


def save_source(
    path: Path,
    text: str,
    protected: Iterable[Path] = (),
    *,
    expected: SourceRevision | None = None,
) -> None:
    if path.suffix.lower() != ".py":
        raise ValueError("源码必须保存为.py；源码与包输出分离")
    atomic_write(path, text.encode("utf-8"), protected, expected=expected)


def save_new_source(path: Path, text: str, protected: Iterable[Path] = ()) -> None:
    """Publish a new .py without overwriting any existing path, including races."""
    if path.suffix.lower() != ".py":
        raise ValueError("源码必须保存为.py")
    publish_new(path, text.encode("utf-8"), protected)


def publish_new(path: Path, data: bytes, protected: Iterable[Path] = ()) -> None:
    """Atomic no-clobber publication of a new document; never an input alias."""
    protected = tuple(protected)
    path = guard_output(path, protected)
    if path.exists() or path.is_symlink():
        raise FileExistsError("请选择尚不存在的文件名，不覆盖已有文件")
    fd, temporary = tempfile.mkstemp(prefix=".mxsource-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        guard_output(path, protected)
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
