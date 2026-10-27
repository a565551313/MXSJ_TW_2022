"""Export one package's entries as a corpus directory.

Two flavours, same container, different question:

* **decrypted** — what the client actually loads. For a script entry that is
  the standard ``.pyc`` (opcode-converted back from the native bytes); when an
  entry decrypts but does not decode as a module, the decrypted native payload
  is written instead and the manifest says so.
* **encrypted** — the stored bytes exactly as they sit in the package.

Nothing here executes a module, and nothing is ever written back into a
package: the destination must be a directory that does not exist yet, and the
manifest records the package digest so a corpus can be traced to its source.
"""

from __future__ import annotations

import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from pathlib import Path

from ..inspection.native import inspect_module
from ..vm.compression import inflate
from ..vm.py25.keys import inflate_script

#: Characters that survive into a file name; everything else becomes ``_``.
_UNSAFE = re.compile(r"[^0-9A-Za-z._-]+")

DECRYPTED = "decrypted"
ENCRYPTED = "encrypted"


@dataclass(frozen=True)
class ExportedEntry:
    index: int
    name: str
    status: str
    size: int
    sha256: str


def _safe_stem(filename: bytes, index: int, identity: str) -> str:
    """A readable, collision-free stem derived from the embedded file name."""
    text = filename.decode("latin-1") if isinstance(filename, bytes) else ""
    stem = Path(text.replace("\\", "/")).name
    stem = _UNSAFE.sub("_", stem).strip("._") or f"entry-{identity}"
    return f"{index:05d}_{stem[:80]}"


def _write(destination: Path, name: str, data: bytes) -> ExportedEntry:
    path = (destination / name).resolve()
    # Defence in depth: a name must never resolve outside the chosen directory,
    # whatever an archive says its entries are called.
    if destination.resolve() not in path.parents:
        raise ValueError(f"导出文件名越界：{name}")
    path.write_bytes(data)
    return ExportedEntry(0, name, "", len(data), hashlib.sha256(data).hexdigest())


def export_corpus(
    archive,
    destination,
    *,
    mode: str = DECRYPTED,
    catalog=None,
    progress=None,
    cancel=None,
):
    """Write every entry of ``archive`` under ``destination``.

    Returns the manifest dictionary that is also written as ``manifest.json``.
    A per-entry failure is recorded, never raised: one undecodable module must
    not cost the other 5,000 entries their export.
    """
    if mode not in {DECRYPTED, ENCRYPTED}:
        raise ValueError("导出模式只能是 decrypted 或 encrypted")
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("请选择一个尚不存在的导出目录，不覆盖已有文件")
    destination.mkdir(parents=True)

    entries = []
    failures = []
    total = len(archive.entries)
    cancelled = False
    for index in range(total):
        if cancel is not None and cancel.is_set():
            cancelled = True
            break
        if progress is not None:
            progress(index, total, "导出语料")
        entry = archive.entries[index]
        if entry.directory:
            continue
        try:
            # Reading and writing belong inside the boundary too: one unreadable
            # entry or one full disk must not cost the rest of the corpus.
            stored = archive.read_stored(index)
            if mode == ENCRYPTED:
                name = f"{index:05d}.bin"
                data = stored
                status = "stored"
            else:
                data, name, status = _decrypted(archive, index, catalog, stored)
            written = _write(destination, name, data)
        except Exception as exc:  # noqa: BLE001 - recorded per entry
            failures.append({"index": index, "identity": entry.identity,
                             "error": str(exc)})
            continue
        entries.append(
            ExportedEntry(
                index, written.name, status, written.size, written.sha256
            )
        )

    manifest = {
        "schema": 1,
        "mode": mode,
        "archive": str(Path(archive.path).resolve()),
        "archive_sha256": archive.fingerprint(),
        "vm": archive.vm,
        "entries_total": total,
        "entries_written": len(entries),
        "cancelled": cancelled,
        "failures": failures,
        "entries": [
            {
                "index": item.index,
                "file": item.name,
                "status": item.status,
                "size": item.size,
                "sha256": item.sha256,
            }
            for item in entries
        ],
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if progress is not None:
        progress(total, total, "导出语料")
    return manifest


def _decrypted(archive, index, catalog, stored):
    """``(bytes, file name, status)`` for one decrypted entry."""
    try:
        standard, filename, _ = inspect_module(archive, index, catalog)
        identity = archive.entries[index].identity
        return (
            standard,
            _safe_stem(filename, index, identity) + ".pyc",
            "standard-pyc",
        )
    except Exception:
        # Not a decodable module: keep whatever the cipher yields so the corpus
        # is still complete, and label it plainly.
        native = _native_payload(archive, index, catalog, stored)
        identity = archive.entries[index].identity
        # The identity is archive-controlled: sanitise it like any other name.
        safe = _safe_stem(identity.encode("latin-1", "replace"), index, str(index))
        return native, safe + ".native", "native-payload"


def _native_payload(archive, index, catalog, stored):
    if archive.vm == "py25":
        if catalog is None:
            raise ValueError("script 包缺少解码参数，只能导出加密语料")
        from ..vm.py25.keys import load_profile

        catalog.verify(archive)
        profile = load_profile(
            archive,
            index,
            catalog.path,
            archive_sha256=archive.fingerprint(),
            catalog_sha256=catalog.sha256,
        )
        return profile.crypt(inflate_script(archive, index))
    # Same contract as inspect_module: the inflated bytes must match the entry's
    # recorded length and CRC, or this is not the payload the client would load.
    if archive.index.metas[index].w1 != 8:
        raise ValueError("不支持的data压缩方法")
    native = inflate(stored, raw=True)
    span = archive.index.spans[index]
    if len(native) != span.usize or zlib.crc32(native) & 0xFFFFFFFF != span.crc:
        raise ValueError("原条目CRC/长度不符")
    return native
