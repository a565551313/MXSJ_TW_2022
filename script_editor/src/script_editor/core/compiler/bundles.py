"""Fail-closed inventory for external, persistent standard Windows runtimes.

The local manifest is a trusted release input, not a signature or a sandbox.
Hashes detect changes; provenance records are declarations, not reproducible-build
proof. No download, executable launch or archive extraction happens here.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from .profiles import PROFILES

MAX_MANIFEST = 4 * 1024 * 1024
MAX_FILES = 10000


class BundleError(ValueError):
    pass


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise BundleError("runtime SHA256无效")
    return value


def _relative(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise BundleError("runtime路径必须是非空POSIX相对路径")
    parts = value.split("/")
    forbidden = {"CON", "PRN", "AUX", "NUL"} | {
        f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10)
    }
    for part in parts:
        if (
            part in ("", ".", "..")
            or part[-1:] in (" ", ".")
            or any(ord(c) < 32 or c in '<>:"|?*' for c in part)
            or part.split(".")[0].upper() in forbidden
        ):
            raise BundleError("runtime路径越界/不是合法Windows路径")
    if PurePosixPath(value).is_absolute():
        raise BundleError("runtime路径不能是绝对路径")
    return value


def _plain_directory(root: Path):
    if root.is_symlink() or not root.is_dir():
        raise BundleError("runtime目录缺失或为符号链接")
    # Windows junctions/reparse points can redirect without is_symlink().
    if getattr(root.lstat(), "st_file_attributes", 0) & 0x400:
        raise BundleError("runtime不允许重解析点")


def _inventory(root: Path):
    _plain_directory(root)
    files = {}
    names = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        _relative(relative)
        folded = relative.casefold()
        if folded in names:
            raise BundleError("runtime路径大小写冲突")
        names.add(folded)
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            raise BundleError("runtime文件不允许符号链接/重解析点")
        if path.is_dir():
            continue
        if not path.is_file():
            raise BundleError("runtime不是普通文件")
        files[relative] = path
        if len(files) > MAX_FILES:
            raise BundleError("runtime文件数超限")
    return files


def check_pe32(path: Path, *, dll=False):
    """Read only PE headers; reject malformed/non-x86 binaries before launch."""
    with path.open("rb") as stream:
        dos = stream.read(64)
        if len(dos) != 64 or dos[:2] != b"MZ":
            raise BundleError("runtime不是PE可执行文件")
        offset = struct.unpack_from("<I", dos, 60)[0]
        if not 64 <= offset <= min(path.stat().st_size - 26, 16 * 1024 * 1024):
            raise BundleError("runtime PE头偏移无效")
        stream.seek(offset)
        header = stream.read(26)
    if (
        len(header) != 26
        or header[:4] != b"PE\0\0"
        or struct.unpack_from("<H", header, 4)[0] != 0x14C
        or struct.unpack_from("<H", header, 24)[0] != 0x10B
        or bool(struct.unpack_from("<H", header, 22)[0] & 0x2000) != dll
    ):
        raise BundleError("runtime必须为Windows x86 PE32（EXE/DLL类型须匹配）")


def _read_manifest(path):
    if not path.is_file():
        raise BundleError("runtime清单必须是普通文件")
    if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
        raise BundleError("runtime清单不允许符号链接/重解析点")
    with path.open("rb") as stream:
        raw = stream.read(MAX_MANIFEST + 1)
    if len(raw) > MAX_MANIFEST:
        raise BundleError("runtime清单超过4MiB")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BundleError("runtime JSON重复字段")
            result[key] = value
        return result

    doc = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique)
    if not isinstance(doc, dict) or not isinstance(doc.get("compilers"), list):
        raise BundleError("runtime清单格式错误")
    # Preserve the explicit unavailable state of older empty manifests.
    if doc.get("schema") == 1 and doc["compilers"] == []:
        raise BundleError("尚未安装内置编译器；编译禁用")
    if doc.get("schema") != 2:
        raise BundleError("必须使用整套文件审计的runtime schema2；编译禁用")
    return doc, hashlib.sha256(raw).hexdigest()


def _validate_item(item):
    if not isinstance(item, dict) or item.get("vm") not in PROFILES:
        raise BundleError("runtime VM无效")
    vm = item["vm"]
    profile = PROFILES[vm]
    prefix = f"{vm}/win-x86"
    if (
        item.get("platform") != "win32"
        or item.get("version") != profile.version
        or type(item.get("bits")) is not int
        or item["bits"] != 32
        or item.get("magic") != profile.magic.hex()
        or item.get("root") != prefix
        or item.get("executable") != prefix + "/python.exe"
    ):
        raise BundleError("runtime版本/魔数/位数/目录布局不符")
    files = item.get("files")
    if not isinstance(files, dict) or not 1 <= len(files) <= MAX_FILES:
        raise BundleError("runtime缺少完整文件清单")
    folded = set()
    for name, sha in files.items():
        _relative(name)
        _sha(sha)
        if name.casefold() in folded:
            raise BundleError("runtime清单路径大小写冲突")
        folded.add(name.casefold())
    suffix = "25" if vm == "py25" else "27"
    required = {"python.exe", f"python{suffix}.dll", f"python{suffix}.zip"}
    if not required <= files.keys():
        raise BundleError("runtime缺少EXE、标准DLL或只读标准库ZIP")
    source = item.get("source")
    if not isinstance(source, dict):
        raise BundleError("runtime缺少来源记录")
    url = urlparse(source.get("url", ""))
    if (
        url.scheme != "https"
        or url.hostname
        not in ("github.com", "codeload.github.com", "www.python.org", "python.org")
        or url.username
        or url.password
        or not url.path
    ):
        raise BundleError("runtime来源必须是官方CPython HTTPS来源")
    if url.hostname in (
        "github.com",
        "codeload.github.com",
    ) and not url.path.startswith("/python/cpython/"):
        raise BundleError("runtime来源不是python/cpython")
    if not isinstance(source.get("revision"), str) or not re.fullmatch(
        r"[0-9a-f]{40}", source["revision"]
    ):
        raise BundleError("runtime来源必须记录精确源码commit")
    _sha(source.get("archive_sha256"))
    licenses = item.get("licenses")
    if not isinstance(licenses, list) or not licenses:
        raise BundleError("runtime缺少许可记录")
    components = set()
    for license in licenses:
        if not isinstance(license, dict):
            raise BundleError("runtime许可记录无效")
        name = _relative(license.get("path"))
        component = license.get("component")
        if name not in files or not isinstance(component, str) or not component.strip():
            raise BundleError("runtime许可文件未纳入哈希清单")
        components.add(component)
    if "CPython" not in components:
        raise BundleError("runtime缺少CPython许可")
    if (
        any(
            Path(name).name.lower().startswith(("msvcr", "msvcp", "vcruntime"))
            for name in files
        )
        and "Microsoft CRT" not in components
    ):
        raise BundleError("runtime缺少随包CRT许可记录")
    return vm


@dataclass(frozen=True)
class BundlePin:
    manifest: Path
    manifest_sha256: str
    vm: str
    root: Path
    files: tuple[tuple[str, str], ...]

    @property
    def executable(self):
        return self.root / "python.exe"

    @property
    def protected(self):
        return (self.manifest, *(self.root / name for name, _ in self.files))

    def verify(self):
        doc, sha = _read_manifest(self.manifest)
        if sha != self.manifest_sha256:
            raise BundleError("runtime清单在检查后发生变化")
        # Validate all records, including duplicate VM entries, without launching.
        items = {}
        for item in doc["compilers"]:
            vm = _validate_item(item)
            if vm in items:
                raise BundleError("runtime VM重复")
            items[vm] = item
        if (
            self.vm not in items
            or tuple(sorted(items[self.vm]["files"].items())) != self.files
        ):
            raise BundleError("runtime文件关联已过期")
        _plain_directory(self.manifest.parent)
        _plain_directory(self.manifest.parent / self.vm)
        expected_root = self.manifest.parent / items[self.vm]["root"]
        if expected_root != self.root:
            raise BundleError("runtime根目录已变化")
        actual = _inventory(self.root)
        if actual.keys() != dict(self.files).keys():
            raise BundleError("runtime文件缺失或存在未记录的额外文件")
        for name, expected in self.files:
            path = actual[name]
            if digest_file(path) != expected:
                raise BundleError(f"runtime文件SHA256不匹配：{name}")
            if path.suffix.lower() in (".exe", ".dll", ".pyd"):
                check_pe32(path, dll=path.suffix.lower() != ".exe")
        for license in items[self.vm]["licenses"]:
            if actual[license["path"]].stat().st_size == 0:
                raise BundleError("runtime许可文件为空")


def load_bundle(vm: str, application_root: Path) -> BundlePin:
    try:
        base = application_root.absolute() / "runtimes"
        _plain_directory(base)
        path = base / "manifest.json"
        doc, sha = _read_manifest(path)
        matches = []
        seen = set()
        for item in doc["compilers"]:
            key = _validate_item(item)
            if key in seen:
                raise BundleError("runtime VM重复")
            seen.add(key)
            if key == vm:
                matches.append(item)
        if len(matches) != 1:
            raise BundleError("未安装此VM的内置编译器；编译禁用")
        item = matches[0]
        pin = BundlePin(
            path, sha, vm, base / item["root"], tuple(sorted(item["files"].items()))
        )
        pin.verify()
        return pin
    except (OSError, ValueError, TypeError, KeyError) as exc:
        if isinstance(exc, BundleError):
            raise
        raise BundleError("runtime清单或文件缺失/损坏；编译禁用") from exc
