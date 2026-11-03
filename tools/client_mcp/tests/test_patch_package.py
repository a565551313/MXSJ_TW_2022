"""Tests for the in-place guarded-hook patcher (synthetic 0SLF packages)."""

import importlib.util
import struct
import zlib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
MODULE = Path(__file__).resolve().parents[1] / "client_probe" / "patch_package.py"
spec = importlib.util.spec_from_file_location("patch_package", MODULE)
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)

MASK = 0xFFFFFFFF
PROBE_ID = 2537560296


@pytest.fixture(scope="module")
def vm():
    mx_hash, marshal_tree, cipher, codec, _ = patcher._require_script_editor(REPO)
    return mx_hash, marshal_tree, cipher, codec


def _string_atom(marshal_tree, payload):
    return marshal_tree.Atom(
        b"s", b"s" + struct.pack("<I", len(payload)) + payload, payload
    )


def _empty_tuple(marshal_tree):
    return marshal_tree.Group(b"(", ())


def _module_marshal(marshal_tree, codec):
    """A minimal VM25 module: ``LOAD_CONST None; RETURN_VALUE``."""
    consts = marshal_tree.Group(
        b"(",
        (
            marshal_tree.Atom(b"i", b"i" + struct.pack("<i", -1), None),
            marshal_tree.Atom(b"N", b"N", None),
        ),
    )
    fields = (
        consts,
        _empty_tuple(marshal_tree),
        _empty_tuple(marshal_tree),
        _empty_tuple(marshal_tree),
        _empty_tuple(marshal_tree),
        _string_atom(marshal_tree, b"mainpage.py"),
        _string_atom(marshal_tree, b"mainpage"),
    )
    root = marshal_tree.Code(
        struct.pack("<iiii", 0, 0, 3, 64),
        bytes([patcher.OP_LOAD_CONST, 1, 0, patcher.OP_RETURN_VALUE]),
        fields,
        struct.pack("<i", 1),
        b"",
    )
    standard = marshal_tree.emit(root, lambda code, lines, extra: (code, lines, extra))
    return codec.encode(codec.MAGIC + bytes(4) + standard)


def _build_package(path, vm):
    _, marshal_tree, cipher, codec = vm
    native = _module_marshal(marshal_tree, codec)
    stored = zlib.compress(
        cipher.xor_segments(
            native, *cipher.parameters_for_name(b"mainpage", len(native))
        ),
        9,
    )
    probe = zlib.compress(b"probe payload", 9)
    payloads = [(patcher.MAINPAGE_ID, stored), (PROBE_ID, probe)]
    body = bytearray()
    records = bytearray()
    for index, (entry_id, chunk) in enumerate(payloads):
        offset = len(body) + 12
        body.extend(chunk)
        r1 = 1
        r2 = (((r1 * entry_id + 0x0DF25E) & MASK) ^ len(chunk)) & MASK
        r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ offset) & MASK
        records.extend(struct.pack("<IIII", entry_id, r1, r2, r3))
    header = b"0SLF" + struct.pack("<II", len(payloads), len(body) + 12)
    path.write_bytes(header + bytes(body) + bytes(records))
    return path


def _module_code(path, vm):
    _, marshal_tree, cipher, codec = vm
    data = path.read_bytes()
    entry = next(
        e for e in patcher.read_directory(data) if e["id"] == patcher.MAINPAGE_ID
    )
    plain, _, _ = patcher.decrypt(
        patcher._payload(data, entry), b"mainpage", patcher.MAINPAGE_ID, cipher, vm[0]
    )
    root = marshal_tree.parse(codec.decode(plain)[8:])
    names = [patcher._atom_value(atom) for atom in root.fields[1].items]
    return root, names


def test_hook_layout_jumps_are_consistent():
    code = patcher.hook_bytes(names_start=0)
    patcher.verify_hook_layout(code, 0)
    assert code[-4] == patcher.OP_LOAD_CONST
    assert code[-1] == patcher.OP_RETURN_VALUE


def test_patch_adds_guarded_hook_and_keeps_other_entries(tmp_path, vm):
    package = _build_package(tmp_path / "script.fls", vm)
    before = package.read_bytes()
    before_probe = next(
        patcher._payload(before, e)
        for e in patcher.read_directory(before)
        if e["id"] == PROBE_ID
    )
    report = patcher.patch(package, write=True, repo_root=REPO)
    assert report["entry_count"] == 2
    assert report["probe_entry_present"] is True

    after = package.read_bytes()
    entries = patcher.read_directory(after)
    probe = next(patcher._payload(after, e) for e in entries if e["id"] == PROBE_ID)
    assert probe == before_probe

    root, names = _module_code(package, vm)
    assert b"mxsj_probe" in names and b"write_report" in names
    # The synthetic module is only the trailing pair, so the hook starts at 0.
    assert root.code[0] == patcher.OP_SETUP_EXCEPT
    patcher.verify_hook_layout(root.code, 0)


def test_patch_refuses_a_second_run(tmp_path, vm):
    package = _build_package(tmp_path / "script.fls", vm)
    patcher.patch(package, write=True, repo_root=REPO)
    with pytest.raises(FileExistsError):
        patcher.patch(package, write=True, repo_root=REPO)


def test_check_mode_does_not_write(tmp_path, vm):
    package = _build_package(tmp_path / "script.fls", vm)
    before = package.read_bytes()
    patcher.patch(package, write=False, repo_root=REPO)
    assert package.read_bytes() == before


def test_rejects_non_0slf(tmp_path, vm):
    bogus = tmp_path / "script.fls"
    bogus.write_bytes(b"not a package")
    with pytest.raises(ValueError):
        patcher.patch(bogus, write=False, repo_root=REPO)
