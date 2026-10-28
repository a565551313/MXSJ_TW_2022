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

#: Backup name used by 生成新包 when the user saves over the original name.
#: Fixed name on purpose: writing it again replaces the previous copy.
BACKUP_RENAME_SUFFIX = "_bak"


def install_over_source(source: Path, output: Path, *, expected_sha256=None) -> Path:
    """Put an already verified ``output`` at ``source``, keeping the old bytes.

    The old package becomes ``<name>_bak`` (one rolling copy). Nothing is
    guessed: callers pass the digest they verified, so a package that changed
    while the build ran is never silently replaced.
    """
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError("输出不能就是原包本身")
    if expected_sha256 is not None and _sha256_file(source) != expected_sha256:
        raise ValueError("原包在保存期间被改动，已放弃覆盖；请重新打开后再保存")
    backup = source.with_name(source.name + BACKUP_RENAME_SUFFIX)
    os.replace(source, backup)
    # Rename is atomic, but a writer can still have changed the bytes between
    # the digest check above and this rename. Verify the copy we are about to
    # keep - the same rule loose mode already applies to ``<name>.fls.bak``.
    if expected_sha256 is not None:
        try:
            changed = _sha256_file(backup) != expected_sha256
        except OSError:
            # An unreadable backup (antivirus/indexer lock on Windows) must not
            # leave the package name empty: put it back before giving up.
            os.replace(backup, source)
            raise
        if changed:
            os.replace(backup, source)  # still exactly one package at the old name
            raise ValueError("原包在备份期间被改动，已放弃覆盖；请重新打开后再保存")
    try:
        os.replace(output, source)
    except OSError:
        os.replace(backup, source)  # put the original back; nothing is lost
        raise
    return backup


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
    if backup_path is not None and _sha256_file(backup_path) != expected_sha256:
        # A writer slipped in between the hash above and the copy, so the copy
        # holds bytes we never verified. Keeping it as ``.bak`` would tell the
        # user "this is what was there" about content we did not check.
        try:
            backup_path.unlink()
        except OSError:
            pass
        raise ValueError("原包在备份期间被改动，已放弃覆盖；请重新打开后再保存")
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


def _original_native_size(archive, index, profile):
    """Marshaled length the entry shipped with, or ``None`` if unreadable.

    Only used to explain a refusal, so any failure here must not replace the
    real error: the caller falls back to the plain message.
    """
    try:
        standard = py25.decode(
            profile.crypt(inflate_script(archive, index)), padding=True
        )
        return len(py25.encode(standard))
    except (OSError, ValueError, zlib.error):
        return None


class CapacityError(ValueError):
    """The build is bigger than this entry's fixed XOR slot.

    Carries the numbers so a caller can offer a way out (see the experimental
    resize switch) instead of only printing prose.
    """

    def __init__(self, message, *, native_size, slot_size, original_size=None):
        super().__init__(message)
        self.native_size = native_size
        self.slot_size = slot_size
        self.original_size = original_size

    @property
    def shortfall(self):
        """How many bytes the build is over the slot."""
        return self.native_size - self.slot_size


def _capacity_message(archive, index, profile, new_size):
    """Explain a fixed-length refusal with the numbers the user needs.

    The capacity is not a policy knob: the client derives the four XOR segment
    boundaries from the five keys *and the payload length*, so changing the
    length would change the cipher arithmetic. Growing a module can therefore
    only be refused, while shrinking is fine (zero-padded back to the same
    length).
    """
    over = new_size - profile.expanded_size
    original = _original_native_size(archive, index, profile)
    detail = (
        ""
        if original is None
        else f"；原模块是 {original} 字节，本来还有 "
        f"{profile.expanded_size - original} 字节余量"
    )
    return (
        "authored marshal exceeds fixed XOR length; no shrink/rescale"
        f"（这次编译出的原生负载 {new_size} 字节，超过该条目固定长度 "
        f"{profile.expanded_size} 字节，超出 {over} 字节{detail}。"
        "固定长度由客户端取参公式决定，默认不缩放参数；"
        "可以把模块改小后写回。自动校验与写包这条路径会直接按新长度"
        "重算分段（实验：本机可自校验，客户端加载行为未实机验收），"
        "只有显式不扩容的调用才会因长度不足被拒绝）"
    )


@dataclass(frozen=True)
class EncodedReplacement:
    """Stored bytes plus the native (pre-XOR) facts the preview needs."""

    stored: bytes
    native_size: int
    resized: bool


def encode_replacement(archive, replacement, profile, *, allow_resize=False):
    return encode_replacement_detailed(
        archive, replacement, profile, allow_resize=allow_resize
    ).stored


def encode_replacement_detailed(archive, replacement, profile, *, allow_resize=False):
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
            if not allow_resize:
                raise CapacityError(
                    _capacity_message(
                        archive, replacement.index, profile, len(native)
                    ),
                    native_size=len(native),
                    slot_size=profile.expanded_size,
                    original_size=_original_native_size(
                        archive, replacement.index, profile
                    ),
                )
            # Opt-in: the client derives the four boundaries from the five keys
            # and the inflated length, so encrypting at the new length stays
            # self-consistent. Refuse early if this length admits no valid
            # five-segment split instead of writing something unreadable.
            try:
                return EncodedReplacement(
                    zlib.compress(profile.crypt_variable(native), 9), len(native), True
                )
            except ValueError as exc:
                raise ValueError(
                    "这个长度无法按客户端取参公式分成五段"
                    f"（{len(native)} 字节）：{exc}；把模块再改小/改大一些后重试"
                ) from exc
        padded = native + bytes(profile.expanded_size - len(native))
        return EncodedReplacement(
            zlib.compress(profile.crypt(padded), 9), len(native), False
        )
    span = archive.index.spans[replacement.index]
    if archive.index.metas[replacement.index].w1 != 8:
        raise ValueError("unknown data compression method")
    original = inflate(stored, raw=True)
    if len(original) != span.usize or zlib.crc32(original) & 0xFFFFFFFF != span.crc:
        raise ValueError("original data payload CRC/size mismatch")
    py27.decode(original)  # Non-scripts/unknown formats stay read-only.
    encoded = py27.encode(expected)
    # Data records carry their own size, so a different length is not a resize
    # of a fixed slot; the flag stays False for py27.
    return EncodedReplacement(encoded, len(encoded), False)


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
            # ``crypt_variable`` equals ``crypt`` for the original length and is
            # the only correct readback when the entry was resized.
            restored = py25.decode(
                profiles[i].crypt_variable(inflate(stored)),
                header=expected[:8],
                padding=True,
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
    allow_resize: bool = False,
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
            changed[i] = encode_replacement(
                source, replacement, profiles.get(i), allow_resize=allow_resize
            )
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
