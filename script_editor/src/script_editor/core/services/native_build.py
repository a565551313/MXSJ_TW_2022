"""Fail-closed native build API.

All replacements are explicit identities + freshly authored standard pycs. New
file by default, bounded decode, independent inverse, full CPython marshal read,
then no-clobber atomic hard-link publication. Never executes original/authored
code.

``in_place=True`` is the opt-in loose mode: the caller names the *source*
archive as the destination, and publication becomes "re-hash the original,
optionally keep one rolling ``.bak``, then atomically replace it". Every check
above still runs first — loose mode changes where the bytes go, never what is
verified, and it can never silently overwrite a third protected file.

``encode_replacement`` is the public single-entry encoder used by the M3
workflow preview (``core/services/workflow.py``) and by the GUI's F6 action;
``build_package`` is the only publication path.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..archives.verify import envelope, equal_region
from ..archives.writer import write_data, write_script
from ..compiler.runner import Compiler, audit_standard
from ..policy import require_module_allowed
from ..vm.compression import inflate
from ..vm.py25 import codec as py25
from ..vm.py25.keys import KeyProfile, inflate_script
from ..vm.py27 import codec as py27


@dataclass(frozen=True)
class Replacement:
    index: int
    identity: str
    standard_pyc: bytes


@dataclass(frozen=True)
class BuildReport:
    source_sha256: str
    output_sha256: str
    modified_indexes: tuple[int, ...]
    unchanged_entries: int
    output: Path


#: Rolling backup written next to a package that loose mode overwrites. Fixed
#: name on purpose: repeated saves replace it, so disk use stays bounded.
BACKUP_SUFFIX = ".bak"


def guard_new_package(path: Path, protected: tuple[Path, ...]) -> Path:
    path = path.absolute()
    if path.suffix.lower() != ".fls":
        raise ValueError("native output must have .fls suffix")
    if path.exists() or path.is_symlink():
        raise ValueError("output must be a NEW file; no existing file is overwritten")
    if any(path.resolve() == p.resolve() for p in protected):
        raise ValueError("output cannot be an input/alias")
    if not path.parent.is_dir():
        raise ValueError("choose an existing output directory")
    return path


def guard_in_place(
    path: Path, source_path: Path, protected: tuple[Path, ...]
) -> Path:
    """Allow overwriting exactly the source archive, and nothing else.

    ``protected`` normally contains every open input, including the source.
    Loose mode removes only that one entry, so an alias of any *other* input
    (a catalog, a bound source file, another open package) still fails closed.
    """
    path = path.absolute()
    if path.suffix.lower() != ".fls":
        raise ValueError("原包必须是 .fls")
    if not path.exists() or path.is_symlink():
        raise ValueError("原包已不存在或不是普通文件，拒绝就地覆盖")
    if not path.is_file():
        raise ValueError("目标不是普通文件，拒绝就地覆盖")
    if not path.parent.is_dir():
        raise ValueError("原包所在目录不可用")
    if path.resolve() != source_path.resolve():
        raise ValueError("就地覆盖只能指向本次构建的原包本身")
    others = {p.resolve() for p in protected} - {source_path.resolve()}
    if path.resolve() in others:
        raise ValueError("目标同时是另一个受保护的输入，拒绝就地覆盖")
    return path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_backup(path: Path) -> Path:
    """Copy the file about to be replaced to ``<name>.fls.bak`` atomically."""
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists() and backup.is_dir():
        raise ValueError("备份路径被占用为目录，拒绝覆盖原包")
    fd, temporary = tempfile.mkstemp(prefix=".mxscript-bak-", dir=path.parent)
    os.close(fd)
    try:
        shutil.copy2(path, temporary)
        os.replace(temporary, backup)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return backup


def _replace_in_place(
    path: Path,
    temporary: Path,
    *,
    expected_sha256: str,
    output_sha256: str,
    backup: bool,
) -> Path | None:
    """Replace ``path`` with an already verified temporary package.

    The original is re-hashed after its reader was closed, so a package that
    changed during the build is never overwritten. Returning ``None`` means no
    backup was requested.
    """
    if _sha256_file(path) != expected_sha256:
        raise ValueError("原包在保存期间被改动，已放弃覆盖；请重新打开后再保存")
    backup_path = _write_backup(path) if backup else None
    try:
        os.replace(temporary, path)
    except OSError as exc:
        # Windows keeps an open handle locked: the game or another viewer holds it.
        raise ValueError(
            f"写回原包失败（{exc}）：原包可能仍被游戏或其它程序打开，"
            "请关闭后重试；原包未被改动"
        ) from exc
    if _sha256_file(path) != output_sha256:
        raise ValueError(
            "写回后原包摘要与新包不一致；"
            + (f"旧文件已备份在 {backup_path}" if backup_path else "且未留备份")
        )
    return backup_path


def encode_replacement(archive, replacement, profile):
    require_module_allowed(archive.vm, replacement.index)
    expected = replacement.standard_pyc
    stored = archive.read_stored(replacement.index)
    if archive.vm == "py25":
        if profile is None:
            raise ValueError("script replacement requires digest-bound XOR profile")
        profile.validate(archive, replacement.index)
        # Original must be recognizable without repairs, not just a zlib header.
        py25.decode(
            profile.crypt(inflate_script(archive, replacement.index)), padding=True
        )
        native = py25.encode(expected)
        if len(native) > profile.expanded_size:
            raise ValueError(
                "authored marshal exceeds fixed XOR length; no shrink/rescale"
            )
        padded = native + bytes(profile.expanded_size - len(native))
        return zlib.compress(profile.crypt(padded), 9)
    span = archive.index.spans[replacement.index]
    if archive.index.metas[replacement.index].w1 != 8:
        raise ValueError("unknown data compression method")
    original = inflate(stored, raw=True)
    if len(original) != span.usize or zlib.crc32(original) & 0xFFFFFFFF != span.crc:
        raise ValueError("original data payload CRC/size mismatch")
    py27.decode(original)  # Non-scripts/unknown formats stay read-only.
    return py27.encode(expected)


#: Historical private name; kept so existing callers and evidence tests that
#: import ``_native`` keep working. New code uses ``encode_replacement``.
_native = encode_replacement


def verify_output(source, result, replacements, profiles, compiler):
    envelope(source, result, replacements)
    for i in range(len(source.entries)):
        if source.index.metas[i] != result.index.metas[i]:
            raise ValueError("entry metadata changed")
        if i not in replacements:
            old, new = source.index.spans[i], result.index.spans[i]
            if source.kind == "flsdata":
                if old.local_len != new.local_len:
                    raise ValueError("unchanged local record length differs")
                equal_region(
                    source, old.local_offset, result, new.local_offset, old.local_len
                )
            else:
                if old.length != new.length:
                    raise ValueError("unchanged stored entry length differs")
                equal_region(source, old.offset, result, new.offset, old.length)
            continue
        expected = replacements[i].standard_pyc
        stored = result.read_stored(i)
        if source.vm == "py25":
            restored = py25.decode(
                profiles[i].crypt(inflate(stored)), header=expected[:8], padding=True
            )
        else:
            native = inflate(stored, raw=True)
            span = result.index.spans[i]
            if len(native) != span.usize or zlib.crc32(native) & 0xFFFFFFFF != span.crc:
                raise ValueError("written data CRC/size mismatch")
            restored = py27.decode(native)
        if restored != expected:
            raise ValueError(
                "independent native readback differs from full authored pyc"
            )
        audit_standard(compiler, restored)


def build_package(
    source_path: Path,
    destination: Path,
    *,
    source_sha256: str,
    replacements: tuple[Replacement, ...],
    compiler: Compiler,
    profiles: dict[int, KeyProfile] | None = None,
    protected: tuple[Path, ...] = (),
    in_place: bool = False,
    backup: bool = True,
) -> BuildReport:
    """Write one new package, or (``in_place``) overwrite the source archive.

    ``in_place`` is loose mode. It still refuses a changed source, still writes
    and verifies a temporary package first, and still leaves a rolling
    ``<name>.fls.bak``. Only the final ``os.replace`` differs from the strict
    path, which links a brand-new file instead.
    """
    profiles = dict(profiles or {})
    destination = (
        guard_in_place(destination, source_path, protected)
        if in_place
        else guard_new_package(destination, (source_path, *protected))
    )
    if not replacements:
        raise ValueError("empty replacement set")
    changed, selected = {}, {}
    with ArchiveDocument(source_path) as source:
        fingerprint = source.fingerprint()
        if fingerprint != source_sha256 or compiler.vm != source.vm:
            raise ValueError("source digest/VM mismatch")
        for replacement in replacements:
            i = replacement.index
            require_module_allowed(source.vm, i)
            if (
                type(i) is not int
                or not 0 <= i < len(source.entries)
                or i in selected
                or replacement.identity != source.entries[i].identity
                or source.entries[i].directory
            ):
                raise ValueError("duplicate/invalid replacement identity")
            selected[i] = replacement
            audit_standard(compiler, replacement.standard_pyc)
            changed[i] = encode_replacement(source, replacement, profiles.get(i))
        fd, temporary = tempfile.mkstemp(
            prefix=".mxscript-build-", dir=destination.parent
        )
        # In loose mode the temporary file becomes the replacement, so it may
        # only be unlinked once the swap ran (or the build failed before it).
        keep_temporary = False
        try:
            with os.fdopen(fd, "w+b") as out:
                if source.vm == "py25":
                    write_script(source, changed, out)
                else:
                    write_data(source, changed, out)
                out.flush()
                os.fsync(out.fileno())
            with ArchiveDocument(temporary) as result:
                verify_output(source, result, selected, profiles, compiler)
                output_hash = result.fingerprint()
            source._assert_unchanged()
            keep_temporary = in_place
            if not in_place:
                guard_new_package(destination, (source_path, *protected))
                # Atomic no-clobber: a racing file cannot be silently
                # overwritten. Unsupported hard-link filesystems fail safely.
                os.link(temporary, destination)
        finally:
            if not keep_temporary:
                Path(temporary).unlink(missing_ok=True)
    if in_place:
        try:
            # The reader above is closed by now: Windows refuses to replace a
            # file that still has an open handle, and the game may hold one too.
            _replace_in_place(
                destination,
                temporary,
                expected_sha256=fingerprint,
                output_sha256=output_hash,
                backup=backup,
            )
        finally:
            Path(temporary).unlink(missing_ok=True)
    return BuildReport(
        fingerprint,
        output_hash,
        tuple(sorted(selected)),
        len(source.entries) - len(selected),
        destination,
    )
