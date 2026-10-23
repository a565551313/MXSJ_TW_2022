"""Read embedded script filenames, not source, without executing/translating code.

0SLF directory IDs are not filenames. Read the pinned catalog once per scan,
then validate each fixed-boundary payload and bounded native marshal tree.
Names are navigation metadata only: never a binding or proof of source trust.
"""

from __future__ import annotations

import hashlib
import json
import zlib

from ..policy import require_module_allowed
from ..vm.marshal_tree import parse
from ..vm.py25.keys import KeyProfile, inflate_script, read_catalog


def display_module_path(raw: bytes) -> str:
    if (
        not isinstance(raw, bytes)
        or not raw
        or len(raw) > 8192
        or any(n < 32 or n == 127 for n in raw)
    ):
        raise ValueError("内嵌路径为空、过长或含控制字符")
    # Normalize actual separators BEFORE escaping undecodable bytes. Never
    # reinterpret escaped \\xNN as a separator, guess GBK, or change .py to .pyo.
    raw = raw.replace(b"\\", b"/")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("ascii", errors="backslashreplace")


def scan_script_paths(archive, catalog):
    """Return (index -> display path, index -> failure reason), independently.

    Run in the opening/project worker, never the Qt thread. Corrupt entries do
    not hide good ones. Archive/catalog mutation invalidates the ENTIRE result.
    No decompiler, legacy interpreter, export, or game code is invoked.
    """
    if archive.kind != "0slf":
        return {}, {}
    if catalog is None:
        return {}, {e.index: "未关联已确认的XOR参数" for e in archive.entries}
    catalog.verify(archive)
    raw = read_catalog(catalog.path)
    if hashlib.sha256(raw).hexdigest() != catalog.sha256:
        raise ValueError("路径索引的XOR参数摘要不符")
    rows = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(rows, dict):
        raise ValueError("路径索引的XOR目录不是对象")
    fingerprint = archive.fingerprint()
    paths, errors = {}, {}
    for entry in archive.entries:
        try:
            require_module_allowed(archive.vm, entry.index)
            info = rows[str(entry.index)]
            stored = archive.read_stored(entry.index)
            expanded = inflate_script(archive, entry.index)
            profile = KeyProfile(
                fingerprint,
                entry.index,
                entry.identity,
                hashlib.sha256(stored).hexdigest(),
                catalog.sha256,
                tuple(info["keys"]),
                tuple(info["bounds"]),
                len(expanded),
            )
            profile = profile.calibrated(archive)
            profile.validate(archive, entry.index)
            # Native syntax/metadata validation is independent of whether the
            # opcode converter or a decompiler can recover this module's source.
            tree = parse(profile.crypt(expanded), zero_padding=True)
            paths[entry.index] = display_module_path(tree.fields[5].value)
        except (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            IndexError,
            zlib.error,
        ) as exc:
            errors[entry.index] = "路径读取失败：" + str(exc)
    catalog.verify(archive)
    archive._assert_unchanged()
    return paths, errors


def index_script_paths(archive, catalog):
    """Attach optional navigation metadata, keeping unavailable packages usable."""
    try:
        archive.module_paths, archive.module_path_errors = scan_script_paths(
            archive, catalog
        )
    except (OSError, ValueError) as exc:
        archive.module_paths = {}
        archive.module_path_errors = {
            e.index: "路径索引不可用：" + str(exc) for e in archive.entries
        }
