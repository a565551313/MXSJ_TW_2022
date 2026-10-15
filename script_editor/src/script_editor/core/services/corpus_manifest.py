"""Bounded, read-only corpus index. Filenames never establish module identity."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MAX_MANIFEST = 128 * 1024 * 1024
MAX_ROW = 64 * 1024


def digest(value):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise ValueError("语料SHA256非法")
    return value


def bounded_read(path, limit):
    if path.is_symlink() or not path.is_file():
        raise ValueError("语料文件缺失、非普通文件或为符号链接")
    with path.open("rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("语料文件不是普通文件")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("语料文件超过大小限制")
    return raw


def artifact_path(root, name, *, check=True):
    if not isinstance(name, str) or len(name) > 512:
        raise ValueError("语料路径非法")
    parts = PurePosixPath(name).parts
    if (
        not parts
        or name != "/".join(parts)
        or name.startswith("/")
        or any(
            p in {".", ".."}
            or ":" in p
            or "\\" in p
            or p.endswith((".", " "))
            or any(ord(c) < 32 for c in p)
            for p in parts
        )
    ):
        raise ValueError("语料路径越界或包含平台歧义")
    path = root
    for part in parts:
        path = path / part
        if check and path.is_symlink():
            raise ValueError("语料路径不能经过符号链接")
    if check and not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("语料路径逃逸")
    return path


def references(value):
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys():
            yield value
        for item in value.values():
            yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


@dataclass(frozen=True)
class CorpusRef:
    archive: Path
    fingerprint: str
    path: Path
    sha256: str


@dataclass(frozen=True)
class CorpusIndex:
    ref: CorpusRef
    offsets: tuple[tuple[int, int, str], ...]
    repair_indices: tuple[int, ...] = ()

    @property
    def root(self):
        return self.ref.path.parent.parent

    def row(self, archive, index):
        if (
            archive.path != self.ref.archive
            or archive.vm != "py25"
            or archive.fingerprint() != self.ref.fingerprint
        ):
            raise ValueError("语料与原包指纹/VM不符")
        if type(index) is not int or not 0 <= index < len(self.offsets):
            raise ValueError("非法语料条目")
        if index == 1288:
            raise ValueError("excluded_by_policy：不读取1288产物")
        # Verify the complete manifest, not just mtime/size or a displayed name.
        check = hashlib.sha256()
        total = 0
        path = artifact_path(self.root, "full/manifest.audited.jsonl")
        if not path.is_file():
            raise ValueError("语料清单不可用")
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                total += len(chunk)
                if total > MAX_MANIFEST:
                    raise ValueError("语料清单超过限制")
                check.update(chunk)
        if check.hexdigest() != self.ref.sha256:
            raise ValueError("语料清单已变化，须重新明确导入")
        offset, size, checksum = self.offsets[index]
        with self.ref.path.open("rb") as stream:
            stream.seek(offset)
            raw = stream.read(size)
        if hashlib.sha256(raw).hexdigest() != checksum:
            raise ValueError("读取期间语料清单变化")
        return json.loads(raw)

    def artifact(self, row, ref, limit=8 * 1024 * 1024):
        prefix = f"full/entries/{row['entry_index']:04d}/"
        if row["entry_index"] == 1288 or not ref["path"].startswith(prefix):
            raise ValueError("语料产物不属于此entry")
        digest(ref["sha256"])
        if type(ref["bytes"]) is not int or not 0 <= ref["bytes"] <= limit:
            raise ValueError("语料产物超过限制")
        raw = bounded_read(artifact_path(self.root, ref["path"]), limit)
        if len(raw) != ref["bytes"] or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise ValueError("语料产物SHA256/大小不符")
        return raw


def load_corpus(archive, path, *, expected_sha=None, cancel=None):
    path = Path(path).absolute()
    if (
        archive.vm != "py25"
        or path.name != "manifest.audited.jsonl"
        or path.parent.name != "full"
    ):
        raise ValueError("请选择script.fls对应的full/manifest.audited.jsonl")
    root = path.parent.parent.resolve(strict=True)
    path = artifact_path(root, "full/manifest.audited.jsonl")
    if path.is_symlink() or not path.is_file():
        raise ValueError("语料清单缺失或为符号链接")
    fingerprint = archive.fingerprint()
    checksum, offsets, total = hashlib.sha256(), [], 0
    repairs = []
    with path.open("rb") as stream:
        while True:
            if cancel is not None and cancel.is_set():
                from .recovery_process import RecoveryCancelled

                raise RecoveryCancelled("语料导入已取消")
            raw = stream.readline(MAX_ROW + 1)
            if not raw:
                break
            if len(raw) > MAX_ROW or total + len(raw) > MAX_MANIFEST:
                raise ValueError("语料清单/行超过限制")
            try:
                row = json.loads(raw)
                index = row["entry_index"]
                if (
                    type(index) is not int
                    or index != len(offsets)
                    or index >= len(archive.entries)
                    or row["archive_sha256"] != fingerprint
                    or row["schema_version"] != 1
                    or row["index_base"] != 0
                ):
                    raise ValueError("语料条目顺序/身份/格式不符")
                if (
                    type(row.get("schema_version")) is not int
                    or type(row.get("index_base")) is not int
                    or not isinstance(row.get("engines"), dict)
                    or set(row["engines"]) - {"uncompyle6", "pycdc"}
                    or not isinstance(row.get("artifacts"), list)
                    or row.get("status")
                    not in {
                        "complete",
                        "partial",
                        "failed",
                        "timeout",
                        "excluded_by_policy",
                    }
                ):
                    raise ValueError("语料状态/引擎/产物结构非法")
                if index == 1288:
                    if (
                        row["status"] != "excluded_by_policy"
                        or row["engines"]
                        or row["artifacts"]
                    ):
                        raise ValueError("1288只能有政策排除记录")
                elif (
                    row.get("transpile", {}).get("entry_id")
                    != archive.index.metas[index].entry_id
                ):
                    raise ValueError("语料容器entry_id不符")
                for ref in references(row):
                    if not ref["path"].startswith(f"full/entries/{index:04d}/"):
                        raise ValueError("跨entry产物引用")
                    digest(ref["sha256"])
                    if (
                        type(ref["bytes"]) is not int
                        or not 0 <= ref["bytes"] <= 64 * 1024 * 1024
                    ):
                        raise ValueError("非法语料产物长度")
                    artifact_path(root, ref["path"], check=False)
            except (KeyError, TypeError, RecursionError, AttributeError) as exc:
                raise ValueError("语料记录结构非法") from exc
            if index != 1288 and row.get("transpile", {}).get("stage") not in (
                None,
                "baseline",
            ):
                repairs.append(index)
            offsets.append((total, len(raw), hashlib.sha256(raw).hexdigest()))
            total += len(raw)
            checksum.update(raw)
    if len(offsets) != len(archive.entries):
        raise ValueError("语料清单缺条目")
    if expected_sha is not None and digest(expected_sha) != checksum.hexdigest():
        raise ValueError("语料清单已变化，须重新明确导入")
    archive._assert_unchanged()
    return CorpusIndex(
        CorpusRef(archive.path, fingerprint, path, checksum.hexdigest()),
        tuple(offsets),
        tuple(repairs),
    )
