from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

MAX_FILE = 2 * 1024 * 1024
MAX_INVENTORY = 16 * 1024 * 1024


class ManualError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path, limit=MAX_FILE) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ManualError(f"文件缺失或不允许符号链接：{path.name}")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ManualError(f"文件超过安全上限：{path.name}")
    return data


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManualError(f"JSON重复字段：{key}")
        result[key] = value
    return result


def parse_json(data: bytes):
    try:
        return json.loads(
            data.decode("utf-8-sig"),
            object_pairs_hook=_unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ManualError(f"非法JSON常量：{value}")
            ),
        )
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ManualError(f"JSON不可读取：{exc}") from exc


def read_json(path: Path, limit=MAX_FILE):
    return parse_json(read_bytes(path, limit))


def source_path(root: Path, name: str) -> Path:
    parts = PurePosixPath(name).parts
    if (
        not parts
        or name.startswith("/")
        or "\\" in name
        or ":" in name
        or any(p in {"..", "."} for p in name.split("/"))
        or any(ord(c) < 32 for c in name)
        or re.match(r"^[A-Za-z]:", name)
    ):
        raise ManualError("证据必须使用仓库内规范相对路径")
    root = root.resolve(strict=True)
    target = root.joinpath(*parts)
    for parent in (target, *target.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ManualError("证据路径禁止符号链接")
    if not target.resolve(strict=True).is_relative_to(root):
        raise ManualError("证据路径越出仓库")
    return target


def module_id(record):
    return f"{record['archive_sha256']}:{record['entry_index']}"
