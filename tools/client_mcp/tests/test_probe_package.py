import hashlib
import importlib.util
import os
import struct
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "client_probe" / "build_probe_package.py"
spec = importlib.util.spec_from_file_location("build_probe_package", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def make_archive(path, entries):
    body = bytearray(b"0SLF" + struct.pack("<II", len(entries), 0))
    records = []
    for index, (entry_id, payload) in enumerate(entries):
        offset = len(body)
        body.extend(payload)
        r1 = 1
        r2 = ((r1 * entry_id + 0x0DF25E) & mod.MASK) ^ len(payload)
        r3 = ((r2 * index * 0x00F718FE + 0x0D59D16C) & mod.MASK) ^ offset
        records.append(struct.pack("<IIII", entry_id, r1, r2, r3))
    struct.pack_into("<I", body, 8, len(body))
    body.extend(b"".join(records))
    path.write_bytes(body)


def test_builds_copy_manifest_and_optional_probe(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"one"), (2, b"two")])
    output = tmp_path / "package"
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    result = mod.build_package(
        source, output, expected_sha256=expected, include_probe_source=True
    )
    assert (output / "script.fls").read_bytes() == source.read_bytes()
    assert (output / "mxsj_probe.py").is_file()
    assert (output / "ipc.py").is_file()
    assert (output / "serve.py").is_file()
    assert result["source"]["sha256"] == expected
    assert result["fls"]["entry_count"] == 2


def test_hash_and_directory_validation_happen_before_output(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"x")])
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="SHA-256"):
        mod.build_package(source, output, expected_sha256="0" * 64)
    assert not output.exists()
    source.write_bytes(b"not fls")
    with pytest.raises(ValueError, match="0SLF"):
        mod.build_package(
            source,
            output,
            expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        )
    assert not output.exists()


def test_rejects_aliases_existing_targets_and_repository_paths(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"x")])
    alias_dir = tmp_path / "alias"
    alias_dir.mkdir()
    alias = alias_dir / "script.fls"
    os.link(source, alias)
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="script.fls"):
        mod.build_package(alias, tmp_path / "out1", expected_sha256=expected)
    alias.unlink()
    source.unlink()
    make_archive(source, [(1, b"x")])
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        mod.build_package(source, existing, expected_sha256=expected)
    with pytest.raises(ValueError, match="outside the repository"):
        mod.build_package(
            source,
            Path(__file__).resolve().parents[3] / "new-package",
            expected_sha256=expected,
        )


def test_rejects_unsorted_directory_and_invalid_probe(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(2, b"two"), (1, b"one")])
    with pytest.raises(ValueError, match="sorted"):
        mod.build_package(
            source,
            tmp_path / "out",
            expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        )
    make_archive(source, [(1, b"one")])
    bad_probe = tmp_path / "bad.py"
    bad_probe.write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        mod.build_package(
            source,
            tmp_path / "out",
            expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            probe_source=bad_probe,
        )
