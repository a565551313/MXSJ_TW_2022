"""Optional standalone GPL-3.0 pycdc; fixed source and audited per-build binary.

No PATH lookup, environment override, game DLL or arbitrary executable discovery.
The manifest is a delivery integrity record, not a publisher signature.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .recovery_process import run_bounded

SOURCE_COMMIT = "b4289760970dbc399684f1e155ec6d1ea1cc787e"
SOURCE_SHA256 = "d7d8c53d37a1a586097145b532fca02535db2f2f0999b3b1e910133c9941bf31"
MAX_BINARY = 32 * 1024 * 1024
LICENSE_SHA256 = "8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903"


def engine_root():
    base = (
        Path(sys.executable).resolve().parent
        if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parents[4]
    )
    return base / "recovery_engines" / "pycdc"


def checked_file(path, limit):
    if path.is_symlink() or not path.is_file():
        raise ValueError("恢复引擎文件缺失或为符号链接")
    with path.open("rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("恢复引擎不是普通文件")
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise ValueError("恢复引擎文件超过限制")
    return content


@dataclass(frozen=True)
class PycdcEngine:
    path: Path
    binary_sha256: str
    source_commit: str = SOURCE_COMMIT
    source_sha256: str = SOURCE_SHA256

    def verified_bytes(self):
        if (self.source_commit, self.source_sha256) != (SOURCE_COMMIT, SOURCE_SHA256):
            raise ValueError("pycdc 源码版本/摘要不匹配")
        content = checked_file(self.path, MAX_BINARY)
        if hashlib.sha256(content).hexdigest() != self.binary_sha256:
            raise ValueError("pycdc 二进制摘要不匹配")
        return content

    def run(self, pyc, *, timeout=30, cancel=None):
        content = self.verified_bytes()
        with tempfile.TemporaryDirectory(prefix="mx-pycdc-") as temporary:
            root = Path(temporary)
            executable = root / ("pycdc.exe" if os.name == "nt" else "pycdc")
            # Execute exactly the bytes verified above, not a replaceable source path.
            executable.write_bytes(content)
            executable.chmod(0o700)
            source = root / "standard.pyc"
            source.write_bytes(pyc)
            return run_bounded(
                [str(executable), str(source)], timeout=timeout, cancel=cancel, cwd=root
            )


def discover_pycdc(root=None):
    root = Path(root) if root is not None else engine_root()
    manifest = root / "manifest.json"
    if not manifest.exists():
        return None
    if root.is_symlink():
        raise ValueError("pycdc 目录不能是符号链接")
    try:
        info = json.loads(checked_file(manifest, 16384))
    except RecursionError as exc:
        raise ValueError("pycdc清单嵌套过深") from exc
    if not isinstance(info, dict):
        raise ValueError("pycdc清单必须为对象")
    name = "pycdc.exe" if os.name == "nt" else "pycdc"
    if (
        type(info.get("schema_version")) is not int
        or info.get("schema_version") != 1
        or info.get("executable") != name
        or info.get("platform") != sys.platform
    ):
        raise ValueError("pycdc 清单格式/平台不匹配")
    engine = PycdcEngine(
        root / name,
        info.get("binary_sha256", ""),
        info.get("source_commit", ""),
        info.get("source_sha256", ""),
    )
    engine.verified_bytes()
    license_bytes = checked_file(root / "LICENSE.txt", 128 * 1024)
    source = checked_file(
        root / "corresponding-source" / f"pycdc-{SOURCE_COMMIT}.tar.gz", 1024 * 1024
    )
    if hashlib.sha256(license_bytes).hexdigest() != LICENSE_SHA256:
        raise ValueError("pycdc GPL许可证缺失或摘要不匹配")
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("pycdc完整对应源码缺失或摘要不匹配")
    return engine


def stage_pycdc(source_root, destination):
    """Stage exact verified program, license and full GPL corresponding source."""
    root = Path(source_root) / "recovery_engines" / "pycdc"
    engine = discover_pycdc(root)
    if engine is None:
        raise ValueError("缺少第二恢复引擎；不能构建双引擎发行包")
    target = Path(destination).resolve(strict=True) / "recovery_engines" / "pycdc"
    archive = f"pycdc-{SOURCE_COMMIT}.tar.gz"
    files = {
        engine.path.name: engine.verified_bytes(),
        "LICENSE.txt": checked_file(root / "LICENSE.txt", 128 * 1024),
        "corresponding-source/" + archive: checked_file(
            root / "corresponding-source" / archive, 1024 * 1024
        ),
        "manifest.json": checked_file(root / "manifest.json", 16384),
    }
    target.mkdir(parents=True, exist_ok=False)
    (target / "corresponding-source").mkdir()
    for name, content in files.items():
        with (target / name).open("xb") as stream:
            stream.write(content)
    return discover_pycdc(target)
