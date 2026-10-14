"""Fail-closed native build API (not yet wired to the GUI).

All replacements are explicit identities + freshly authored standard pycs. New
file only, bounded decode, independent inverse, full CPython marshal read, then
no-clobber atomic hard-link publication. Never executes original/authored code.
"""

from __future__ import annotations

import os
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path

from ..archives.document import ArchiveDocument
from ..archives.verify import envelope, equal_region
from ..archives.writer import write_data, write_script
from ..compiler.runner import Compiler, audit_standard
from ..vm.compression import inflate
from ..vm.py25 import codec as py25
from ..vm.py25.keys import KeyProfile
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


def _native(archive, replacement, profile):
    expected = replacement.standard_pyc
    stored = archive.read_stored(replacement.index)
    if archive.vm == "py25":
        if profile is None:
            raise ValueError("script replacement requires digest-bound XOR profile")
        profile.validate(archive, replacement.index)
        # Original must be recognizable without repairs, not just a zlib header.
        py25.decode(profile.crypt(inflate(stored)), padding=True)
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
) -> BuildReport:
    profiles = dict(profiles or {})
    destination = guard_new_package(destination, (source_path, *protected))
    if not replacements:
        raise ValueError("empty replacement set")
    changed, selected = {}, {}
    with ArchiveDocument(source_path) as source:
        fingerprint = source.fingerprint()
        if fingerprint != source_sha256 or compiler.vm != source.vm:
            raise ValueError("source digest/VM mismatch")
        for replacement in replacements:
            i = replacement.index
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
            changed[i] = _native(source, replacement, profiles.get(i))
        fd, temporary = tempfile.mkstemp(
            prefix=".mxscript-build-", dir=destination.parent
        )
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
            guard_new_package(destination, (source_path, *protected))
            # Atomic no-clobber: a racing file cannot be silently overwritten.
            # Unsupported hard-link filesystems fail safely, without fallback.
            os.link(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return BuildReport(
        fingerprint,
        output_hash,
        tuple(sorted(selected)),
        len(source.entries) - len(selected),
        destination,
    )
