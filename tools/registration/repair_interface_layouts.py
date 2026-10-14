#!/usr/bin/env python3
"""Repair only the native storage of the two registration layouts, to a NEW pack.

Standalone standard-library CLI; Python >= 3.10, no Qt/client execution.
Evidence: notes/native_dlg_path_cipher.md (C_sys.LoadFile actual method binding).
Preserve the user's current layout plaintext byte for byte; do not use templates.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import struct
import tempfile
from pathlib import Path
from typing import BinaryIO

MASK = 0xFFFFFFFF
TARGETS = (b"login/regterms.dlg", b"login/regform.dlg")
HEADER = b"# -*- coding: gbk -*-"
RECORD = struct.Struct("<IIII")
CHUNK = 1024 * 1024


def native_path_hash(path: bytes) -> int:
    """0x60E080 normalization + 0x454860 arithmetic, restricted to our ASCII paths.

    This is a literal arithmetic reconstruction, NOT execution of game code.
    Empty/NUL/long/non-ASCII paths are intentionally unsupported by this helper.
    """
    if not path or len(path) >= 256 or b"\0" in path or not path.isascii():
        raise ValueError("this repair helper requires a short ASCII path")
    normalized = path.replace(b"\\", b"/").upper()
    padded = normalized + b"\0" * (-len(normalized) % 4)
    words = list(struct.unpack(f"<{len(padded) // 4}I", padded))
    words.extend((0x9BE74448, 0x66F42C48))
    rotation, x, y = 0xF4FA8928, 0x37A8470E, 0x7758B42B
    for word in words:
        rotation = ((rotation << 1) | (rotation >> 31)) & MASK
        mix = rotation ^ 0x267B0B11
        x ^= word
        y ^= word
        multiplier = ((mix + y) | 0x02040801) & 0xBFEF7FDF
        product = x * multiplier
        # MUL sets CF when the high word is nonzero; ADC eax,edx; ADC eax,0.
        lo, hi = product & MASK, product >> 32
        total = lo + hi + int(hi != 0)
        next_x = ((total & MASK) + (total >> 32)) & MASK
        multiplier = ((mix + x) | 0x00804021) & 0x7DFEFBFF
        product = y * multiplier
        lo, hi = product & MASK, product >> 32
        # ADD edx,edx; ADC eax,edx; on carry ADD eax,2.
        total = lo + ((hi << 1) & MASK) + (hi >> 31)
        y = ((total & MASK) + (2 if total >> 32 else 0)) & MASK
        x = next_x
    return x ^ y


def native_layout_key(path: bytes) -> bytes:
    """0x60E153: key = (path_hash + 0x9234AB) XOR 0x937F4912, little endian."""
    value = ((native_path_hash(path) + 0x9234AB) & MASK) ^ 0x937F4912
    return struct.pack("<I", value)


def xor4(data: bytes, key: bytes) -> bytes:
    if len(key) != 4:
        raise ValueError("XOR key must have four bytes")
    repeated = (key * ((len(data) + 3) // 4))[: len(data)]
    return bytes(a ^ b for a, b in zip(data, repeated, strict=True))


def validate_layout(plain: bytes) -> None:
    """Parse literal layout syntax only. Never eval/exec it or rewrite its bytes.

    GB18030/surrogate handling follows the existing editor's mixed-byte parser.
    This is not a native CPython 2.5 parser or a native-widget validation claim.
    """
    if not plain.startswith(HEADER):
        raise ValueError("layout does not have the expected GBK coding header")
    text = plain.decode("gb18030", "surrogateescape")
    text = "".join(
        f"\\u{ord(char):04x}" if 0xDC80 <= ord(char) <= 0xDCFF else char
        for char in text
    )
    tree = ast.parse(text)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign):
        raise ValueError("layout must contain only UI_INFO literal assignment")
    assignment = tree.body[0]
    if (
        len(assignment.targets) != 1
        or not isinstance(assignment.targets[0], ast.Name)
        or assignment.targets[0].id != "UI_INFO"
        or not isinstance(assignment.value, ast.List)
        or not assignment.value.elts
        or not all(isinstance(item, ast.Dict) for item in assignment.value.elts)
    ):
        raise ValueError("UI_INFO must be a nonempty list of widget dictionaries")
    allowed = (
        ast.List,
        ast.Dict,
        ast.Tuple,
        ast.Constant,
        ast.UnaryOp,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )
    for node in ast.walk(assignment.value):
        if not isinstance(node, allowed):
            raise ValueError("nonliteral layout syntax is not accepted")


def decode_current(stored: bytes, path: bytes) -> tuple[bytes, str]:
    """Distinguish native-correct, plaintext, and legacy header-derived ciphertext."""
    native_plain = xor4(stored, native_layout_key(path))
    if native_plain.startswith(HEADER):
        validate_layout(native_plain)
        return native_plain, "already_native"
    if stored.startswith(HEADER):
        validate_layout(stored)
        return stored, "plaintext_needs_native_xor"
    if len(stored) < 4:
        raise ValueError("layout payload too short")
    old_key = bytes(a ^ b for a, b in zip(stored[:4], b"# -*", strict=True))
    plain = xor4(stored, old_key)
    validate_layout(plain)  # No frequency guesses or template fallback.
    return plain, "different_key_needs_native_xor"


def read_index(fh: BinaryIO, size: int) -> list[tuple[int, int, int]]:
    header = fh.read(12)
    if len(header) != 12 or header[:4] != b"0SLF":
        raise ValueError("input must be a 0SLF interface pack")
    count, directory = struct.unpack_from("<II", header, 4)
    if not 0 < count <= 1_000_000 or directory < 12:
        raise ValueError("invalid directory header")
    if directory + count * RECORD.size > size:
        raise ValueError("directory is outside input file")
    fh.seek(directory)
    data = fh.read(count * RECORD.size)
    if len(data) != count * RECORD.size:
        raise ValueError("short directory read")
    rows = []
    previous = -1
    spans = []
    for index, (entry_id, r1, r2, r3) in enumerate(RECORD.iter_unpack(data)):
        if entry_id <= previous:
            raise ValueError("directory must have unique, ascending entry IDs")
        previous = entry_id
        length = ((r1 * entry_id + 0x0DF25E) & MASK) ^ r2
        offset = ((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ r3
        if length and (offset < 12 or offset + length > directory):
            raise ValueError("payload outside the pre-directory data area")
        if length:
            spans.append((offset, offset + length))
        rows.append((entry_id, offset, length))
    spans.sort()
    if any(
        end > following
        for (_, end), (following, _) in zip(spans, spans[1:], strict=False)
    ):
        raise ValueError("overlapping stored payloads are not accepted")
    return rows


def same_source(fh: BinaryIO, before: os.stat_result) -> None:
    after = os.fstat(fh.fileno())
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in fields):
        raise ValueError("input changed during repair; no output published")


def verify_copy(
    source: BinaryIO, candidate: BinaryIO, size: int, writes: list[tuple[int, bytes]]
) -> str:
    """Compare EVERY byte to the input plus exactly the approved replacements."""
    source.seek(0)
    candidate.seek(0)
    digest = hashlib.sha256()
    at = 0
    while at < size:
        expected = bytearray(source.read(min(CHUNK, size - at)))
        if not expected:
            raise ValueError("short input read during verification")
        end = at + len(expected)
        for offset, payload in writes:
            first, last = max(at, offset), min(end, offset + len(payload))
            if first < last:
                expected[first - at : last - at] = payload[
                    first - offset : last - offset
                ]
        actual = candidate.read(len(expected))
        if actual != expected:
            raise ValueError("output differs outside the exact approved payloads")
        digest.update(actual)
        at = end
    if candidate.read(1):
        raise ValueError("output length changed")
    return digest.hexdigest()


def repair_pack(source: Path, output: Path) -> dict:
    source, output = Path(source), Path(output)
    if output.resolve() == source.resolve() or output.exists() or output.is_symlink():
        raise ValueError(
            "output must be a NEW path; inputs/aliases cannot be overwritten"
        )
    if not output.parent.is_dir():
        raise ValueError("output directory does not exist")
    report = {
        "version": "registration-layout-storage-1",
        "layouts": [],
        "native_game_acceptance": "not_tested",
        "output_created": False,
    }
    temporary = None
    with source.open("rb") as original:
        before = os.fstat(original.fileno())
        rows = {
            entry: (offset, length)
            for entry, offset, length in read_index(original, before.st_size)
        }
        writes = []
        for path in TARGETS:
            entry_id = native_path_hash(path)
            if entry_id not in rows:
                raise ValueError(f"missing required layout: {path.decode('ascii')}")
            offset, length = rows[entry_id]
            if not 0 < length <= 4 * CHUNK:
                raise ValueError("registration layout length outside safe limits")
            original.seek(offset)
            stored = original.read(length)
            if len(stored) != length:
                raise ValueError("short layout read")
            plain, status = decode_current(stored, path)
            replacement = xor4(plain, native_layout_key(path))
            assert len(replacement) == length
            assert xor4(replacement, native_layout_key(path)) == plain
            report["layouts"].append(
                {
                    "path": path.decode("ascii"),
                    "entry_id": f"0x{entry_id:08X}",
                    "storage_before": status,
                    "bytes": length,
                    "plaintext_sha256": hashlib.sha256(plain).hexdigest(),
                }
            )
            if replacement != stored:
                writes.append((offset, replacement))
        same_source(original, before)
        if not writes:
            report["result"] = (
                "both layouts already native-encrypted; investigate elsewhere"
            )
            return report
        fd, name = tempfile.mkstemp(prefix=".reg-native-", dir=output.parent)
        temporary = Path(name)
        try:
            with os.fdopen(fd, "w+b") as candidate:
                original.seek(0)
                shutil.copyfileobj(original, candidate, CHUNK)
                same_source(original, before)
                for offset, replacement in writes:
                    candidate.seek(offset)
                    candidate.write(replacement)
                candidate.flush()
                os.fsync(candidate.fileno())
                report["output_sha256"] = verify_copy(
                    original, candidate, before.st_size, writes
                )
                same_source(original, before)
            # Exclusive, atomic publication: never overwrite a racing output/alias.
            # Needs hard-link support (e.g. NTFS); fail closed when unsupported.
            os.link(temporary, output)
            report.update(
                output_created=True,
                output_bytes=before.st_size,
                changed_layout_count=len(writes),
            )
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="current interface.fls, read-only")
    parser.add_argument("--output", type=Path, help="new output path (must not exist)")
    args = parser.parse_args()
    output = args.output or args.source.with_name(
        args.source.stem + "_native_fixed.fls"
    )
    try:
        report = repair_pack(args.source, output)
    except (OSError, ValueError, SyntaxError, RecursionError) as exc:
        print(f"FAILED ({type(exc).__name__}): {exc}")
        print("Do not replace the game's pack. The input was not written.")
        return 1
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if report["output_created"]:
        print(f"NEW OUTPUT: {output}")
        print("Only layout STORAGE was repaired. Native game test is still needed.")
    else:
        print("NO OUTPUT: no storage repair is needed; do not overwrite any pack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
