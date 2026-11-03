"""Tests for the resident-timer builder (synthetic 0SLF packages)."""

import importlib.util
import struct
import sys
import zlib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PROBE_DIR = Path(__file__).resolve().parents[1] / "client_probe"
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

spec = importlib.util.spec_from_file_location(
    "build_resident", PROBE_DIR / "build_resident.py"
)
resident = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resident)

patcher = resident  # patch_package symbols are re-exported by build_resident


@pytest.fixture(scope="module")
def vm():
    return resident._require_script_editor(REPO)


def _string_atom(marshal_tree, payload):
    return marshal_tree.Atom(
        b"s", b"s" + struct.pack("<I", len(payload)) + payload, payload
    )


def _empty(marshal_tree):
    return marshal_tree.Group(b"(", ())


def _probe_module(marshal_tree, codec):
    """Minimal module: ``LOAD_CONST None; RETURN_VALUE`` with one name."""
    consts = marshal_tree.Group(
        b"(",
        (
            marshal_tree.Atom(b"i", b"i" + struct.pack("<i", -1), None),
            marshal_tree.Atom(b"N", b"N", None),
        ),
    )
    fields = (
        consts,
        marshal_tree.Group(b"(", (_string_atom(marshal_tree, b"write_report"),)),
        _empty(marshal_tree),
        _empty(marshal_tree),
        _empty(marshal_tree),
        _string_atom(marshal_tree, b"script/mxsj_probe.py"),
        _string_atom(marshal_tree, b"<module>"),
    )
    root = marshal_tree.Code(
        struct.pack("<iiii", 0, 0, 4, 64),
        bytes([100, 1, 0, 83]),
        fields,
        struct.pack("<i", 1),
        b"",
    )
    native = codec.encode(
        codec.MAGIC
        + bytes(4)
        + marshal_tree.emit(root, lambda code, lines, extra: (code, lines, extra))
    )
    return native


def _build(path, vm):
    mx_hash, marshal_tree, cipher, codec, _ = vm
    native = _probe_module(marshal_tree, codec)
    stored = zlib.compress(
        cipher.xor_segments(
            native, *cipher.parameters_for_name(b"mxsj_probe", len(native))
        ),
        9,
    )
    other = zlib.compress(b"other", 9)
    payloads = [(561484, other), (resident.PROBE_ID, stored)]  # sorted by id
    body = bytearray()
    records = bytearray()
    for index, (entry_id, chunk) in enumerate(payloads):
        offset = len(body) + 12
        body.extend(chunk)
        r1 = 1
        r2 = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ len(chunk)) & 0xFFFFFFFF
        r3 = (
            ((r2 * index * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ offset
        ) & 0xFFFFFFFF
        records.extend(struct.pack("<IIII", entry_id, r1, r2, r3))
    header = b"0SLF" + struct.pack("<II", len(payloads), len(body) + 12)
    path.write_bytes(header + bytes(body) + bytes(records))
    return path


def _module(path, vm):
    mx_hash, marshal_tree, cipher, codec, _ = vm
    data = path.read_bytes()
    entry = next(
        e for e in resident.read_directory(data) if e["id"] == resident.PROBE_ID
    )
    native, _, _ = resident.decrypt(
        resident._payload(data, entry),
        b"mxsj_probe",
        resident.PROBE_ID,
        cipher,
        mx_hash,
    )
    return marshal_tree.parse(codec.decode(native)[8:])


def test_tick_callback_is_guarded_and_returns_none():
    vm = resident._require_script_editor(REPO)
    _, marshal_tree, _, _, _ = vm
    tick = resident.build_tick_code(marshal_tree, b"script/mxsj_probe.py")
    assert tick.code[0] == 121  # SETUP_EXCEPT
    assert tick.code[-1] == 83  # RETURN_VALUE
    resident.verify_hook_layout(tick.code, 0)
    assert struct.unpack("<iiii", tick.header) == (0, 0, 3, 0x41)


def test_patch_adds_timer_and_keeps_other_entries(tmp_path, vm):
    package = _build(tmp_path / "script.fls", vm)
    before = package.read_bytes()
    other_before = next(
        resident._payload(before, e)
        for e in resident.read_directory(before)
        if e["id"] != resident.PROBE_ID
    )
    report = resident.patch(package, write=True, repo_root=REPO)
    assert report["timer_seconds"] == resident.TIMER_SECONDS
    assert "tick_instructions" in report["details"]

    after = package.read_bytes()
    other_after = next(
        resident._payload(after, e)
        for e in resident.read_directory(after)
        if e["id"] != resident.PROBE_ID
    )
    assert other_after == other_before

    root = _module(package, vm)
    names = [resident._atom_value(a) for a in root.fields[1].items]
    assert b"_tick" in names and b"timer" in names and b"_TIMER" in names
    assert struct.unpack("<iiii", root.header)[2] >= 6


def test_patch_refuses_second_run(tmp_path, vm):
    package = _build(tmp_path / "script.fls", vm)
    resident.patch(package, write=True, repo_root=REPO)
    with pytest.raises(FileExistsError):
        resident.patch(package, write=True, repo_root=REPO)


def test_check_mode_does_not_write(tmp_path, vm):
    package = _build(tmp_path / "script.fls", vm)
    before = package.read_bytes()
    resident.patch(package, write=False, repo_root=REPO)
    assert package.read_bytes() == before


def test_package_without_probe_entry_is_refused(tmp_path, vm):
    _, _, _, _, _ = vm
    empty = tmp_path / "script.fls"
    other = zlib.compress(b"x", 9)
    body = bytearray()
    body.extend(other)
    r2 = ((561484 + 0x0DF25E) & 0xFFFFFFFF) ^ len(other) >> 0
    record = struct.pack("<IIII", 561484, 1, r2, 0)
    header = b"0SLF" + struct.pack("<II", 1, 12 + len(body))
    empty.write_bytes(header + bytes(body) + record)
    with pytest.raises(ValueError):
        resident.patch(empty, write=False, repo_root=REPO)
