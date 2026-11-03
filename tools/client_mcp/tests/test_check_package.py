"""Tests for the double-click package checker (stdlib only)."""

import hashlib
import importlib.util
import struct
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "check_package.py"
spec = importlib.util.spec_from_file_location("check_package", MODULE)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def make_archive(path, entries, *, broken_length=False):
    body = bytearray(b"0SLF" + struct.pack("<II", len(entries), 0))
    records = []
    for index, (entry_id, payload) in enumerate(entries):
        offset = len(body)
        body.extend(payload)
        r1 = 1
        length = len(payload) if not broken_length else len(payload) + 999_999
        r2 = ((r1 * entry_id + 0x0DF25E) & check.MASK) ^ length
        r3 = ((r2 * index * 0x00F718FE + 0x0D59D16C) & check.MASK) ^ offset
        records.append(struct.pack("<IIII", entry_id, r1, r2, r3))
    struct.pack_into("<I", body, 8, len(body))
    body.extend(b"".join(records))
    path.write_bytes(body)


def test_known_package_is_recognised(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"one"), (2, b"two")])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    check.KNOWN_PACKAGES[digest] = ("测试包", "能启动", "不会写报告")
    try:
        info = check.inspect(source)
    finally:
        del check.KNOWN_PACKAGES[digest]
    assert info["known"] is True
    assert info["entry_count"] == 2
    assert info["problems"] == []
    assert "测试包" in check.render(info)


def test_unknown_package_is_flagged(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"one")])
    info = check.inspect(source)
    assert info["known"] is False
    text = check.render(info)
    assert "未知包" in text
    assert "截图" in text


def test_broken_lengths_and_order_are_reported(tmp_path):
    source = tmp_path / "script.fls"
    make_archive(source, [(1, b"one")], broken_length=True)
    info = check.inspect(source)
    assert any("越界" in item for item in info["problems"])
    assert check.main([str(source)]) == 1

    unsorted = tmp_path / "unsorted.fls"
    make_archive(unsorted, [(2, b"two"), (1, b"one")])
    assert any("升序" in item for item in check.inspect(unsorted)["problems"])


def test_missing_file_renders_helpful_message(tmp_path):
    info = check.inspect(tmp_path / "nope.fls")
    assert info["exists"] is False
    assert "没有找到" in check.render(info)
    assert check.main([str(tmp_path / "nope.fls")]) == 2
