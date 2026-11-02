import importlib.util
import json
import os
import struct
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "script_fls_compare.py"
spec = importlib.util.spec_from_file_location("script_fls_compare", MODULE)
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


def test_changes_and_report(tmp_path):
    base, current, report = (tmp_path / name for name in ("base", "now", "report"))
    make_archive(base, [(1, b"one"), (2, b"two"), (4, b"four")])
    make_archive(current, [(2, b"changed"), (3, b"three"), (4, b"four")])
    assert mod.main(["--current", str(current), "--baseline", str(base),
                     "--report", str(report)]) == 0
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["summary"] == {"added": 1, "removed": 1, "index_changed": 1,
                                  "payload_changed": 1}
    assert [x["id"] for x in result["changes"]] == [1, 2, 3]
    assert result["changes"][1]["changes"] == ["index_changed", "payload_changed"]


def test_duplicate_and_bounds(tmp_path):
    path = tmp_path / "bad"
    make_archive(path, [(1, b"a"), (1, b"b")])
    with pytest.raises(ValueError, match="duplicate"):
        mod.inventory(path)
    path.write_bytes(b"0SLF" + struct.pack("<II", 1, 999))
    with pytest.raises(ValueError, match="directory"):
        mod.inventory(path)
    make_archive(path, [(1, b"a")])
    data = bytearray(path.read_bytes())
    struct.pack_into("<I", data, 13 + 12, 0)
    path.write_bytes(data)
    with pytest.raises(ValueError, match="payload"):
        mod.inventory(path)


def test_report_never_overwrites_inputs_or_existing_file(tmp_path):
    path = tmp_path / "input"
    make_archive(path, [(1, b"a")])
    original = path.read_bytes()
    alias = tmp_path / "hardlink"
    os.link(path, alias)
    for target in (path, alias):
        with pytest.raises(SystemExit):
            mod.main(["--current", str(path), "--baseline", str(path),
                      "--report", str(target)])
        assert path.read_bytes() == original
    report = tmp_path / "report"
    report.write_text("keep", encoding="utf-8")
    with pytest.raises(SystemExit):
        mod.main(["--current", str(path), "--baseline", str(path),
                  "--report", str(report)])
    assert report.read_text(encoding="utf-8") == "keep"
