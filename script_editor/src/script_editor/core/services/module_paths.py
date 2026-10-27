"""Read embedded script filenames, not source, without executing/translating code.

0SLF directory IDs are not filenames. Read the pinned catalog once per scan,
then validate each fixed-boundary payload and bounded native marshal tree.
Names are navigation metadata only: never a binding or proof of source trust.
"""

from __future__ import annotations

import hashlib
import zlib

from ..policy import module_allowed, require_module_allowed
from ..vm.marshal_tree import parse
from ..vm.py25.keys import KeyProfile, catalog_snapshot, inflate_script

_PROGRESS_STEP = 256

# Bytes that may never appear in an embedded module path (C0 controls + DEL).
_PATH_FORBIDDEN = bytes(range(32)) + b"\x7f"


def display_module_path(raw: bytes) -> str:
    if (
        not isinstance(raw, bytes)
        or not raw
        or len(raw) > 8192
        or len(raw.translate(None, _PATH_FORBIDDEN)) != len(raw)
    ):
        raise ValueError("内嵌路径为空、过长或含控制字符")
    # Normalize actual separators BEFORE escaping undecodable bytes. Never
    # reinterpret escaped \\xNN as a separator, guess GBK, or change .py to .pyo.
    raw = raw.replace(b"\\", b"/")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("ascii", errors="backslashreplace")


def scan_script_paths(archive, catalog, *, limit=None, progress=None):
    """Return (index -> display path, index -> failure reason), independently.

    Run in the opening/project worker, never the Qt thread. Corrupt entries do
    not hide good ones. Archive/catalog mutation invalidates the ENTIRE result.
    No decompiler, legacy interpreter, export, or game code is invoked.

    ``limit`` stops after that many policy-allowed entries and is only used for
    a *probe* that may reject parameters early; accepting parameters still
    requires the complete pass. ``progress(done, total)`` is optional and is
    called every :data:`_PROGRESS_STEP` entries so a long scan can show signs of
    life without touching Qt from this thread.
    """
    if archive.kind != "0slf":
        return {}, {}
    if catalog is None:
        return {}, {e.index: "未关联已确认的XOR参数" for e in archive.entries}
    catalog.verify(archive)
    # Parsed once per catalog file per session, never per entry; the digest is
    # still recomputed from the cached bytes and compared to the pin.
    rows, digest = catalog_snapshot(catalog.path)
    if digest != catalog.sha256:
        raise ValueError("路径索引的XOR参数摘要不符")
    fingerprint = archive.fingerprint()
    paths, errors = {}, {}
    allowed = sum(1 for e in archive.entries if module_allowed(archive.vm, e.index))
    total = allowed if limit is None else min(allowed, limit)
    scanned = 0
    for entry in archive.entries:
        if module_allowed(archive.vm, entry.index):
            if scanned >= total:
                break
            scanned += 1
            if progress is not None and (
                scanned % _PROGRESS_STEP == 0 or scanned == total
            ):
                progress(scanned, total)
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
