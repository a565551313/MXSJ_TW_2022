#!/usr/bin/env python3
"""``crosscheck_pycdc.py`` 的回归测试（不需要真的装 pycdc）。

覆盖点：判定四态、现有产物成色识别、目标清单解析、以及「绝不覆盖已有产物」
这条护栏；引擎子进程用假脚本代替，因此本套测试在任何机器上都能跑。
"""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "decompiler"))

import crosscheck_pycdc as cc  # noqa: E402

FAKE_OK = ("#!/bin/sh\n"
           "printf '%s\\n' "
           "'# Source Generated with Decompyle++' 'print 1' 'print 2'\n")
FAKE_INCOMPLETE = ("#!/bin/sh\n"
                   "printf '%s\\n' "
                   "'# Source Generated with Decompyle++' "
                   "'# WARNING: Decompyle incomplete' 'x = 1'\n")
FAKE_REJECT = "#!/bin/sh\necho \"Unsupported file format\" >&2\nexit 1\n"
FAKE_HANG = "#!/bin/sh\nsleep 5\n"


def _fake_engine(dirpath: Path, body: str) -> Path:
    p = dirpath / "eng"
    p.write_text(body, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


class ClassifyTests(unittest.TestCase):
    def test_clean_output_is_ok(self):
        self.assertEqual(cc.classify_pycdc("# Source Generated\nprint 1\n", 0),
                         "pycdc_ok")

    def test_incomplete_marker_downgrades_to_partial(self):
        text = "# Source Generated\n# WARNING: Decompyle incomplete\n"
        self.assertEqual(cc.classify_pycdc(text, 0), "pycdc_incomplete")

    def test_reject_is_not_reported_as_error(self):
        out = "Unsupported file format\n"
        self.assertEqual(cc.classify_pycdc(out, 1), "pycdc_reject")

    def test_empty_success_is_error_not_ok(self):
        # 引擎 0 退出但没吐东西：不能记成成功
        self.assertEqual(cc.classify_pycdc("\n\n", 0), "pycdc_error")


class RunEngineTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.dir = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_ok_engine_reports_line_count_and_keeps_text(self):
        eng = _fake_engine(self.dir, FAKE_OK)
        state, lines, err, secs, text, esc = cc.run_engine(eng, b"PYC", 1, 20)
        self.assertFalse(esc)
        self.assertEqual(state, "pycdc_ok")
        self.assertEqual(lines, 3)
        self.assertGreaterEqual(secs, 0.0)
        self.assertIn("print 2", text)
        self.assertEqual(err, [])

    def test_incomplete_engine_is_partial_not_full(self):
        eng = _fake_engine(self.dir, FAKE_INCOMPLETE)
        got = cc.run_engine(eng, b"PYC", 1, 20)
        self.assertEqual(got[0], "pycdc_incomplete")
        self.assertEqual(got[1], 3)

    def test_reject_engine(self):
        eng = _fake_engine(self.dir, FAKE_REJECT)
        state, lines, err, _s, _t, _e = cc.run_engine(eng, b"PYC", 1, 20)
        self.assertEqual(state, "pycdc_reject")
        self.assertEqual(lines, 0)
        self.assertEqual(err, ["Unsupported file format"])

    def test_hanging_engine_times_out_instead_of_stalling_batch(self):
        eng = _fake_engine(self.dir, FAKE_HANG)
        state, lines, _err, secs, _t, _e = cc.run_engine(eng, b"PYC", 1, 1)
        self.assertEqual(state, "pycdc_timeout")
        self.assertEqual(lines, 0)
        self.assertLess(secs, 4.0)


class DecodeEngineOutputTests(unittest.TestCase):
    def test_valid_utf8_passes_through_untouched(self):
        text, esc = cc.decode_engine_output("打印 ok\n".encode())
        self.assertEqual((text, esc), ("打印 ok\n", False))

    def test_raw_gbk_bytes_get_escaped_and_flagged(self):
        raw = "打印".encode("gbk") + b" tail"
        text, esc = cc.decode_engine_output(raw)
        self.assertTrue(esc)
        self.assertIn("\\xb4", text)          # 转义后仍可读出原字节
        text.encode("utf-8")                    # 落盘必须还是合法 UTF-8

    def test_empty_output(self):
        self.assertEqual(cc.decode_engine_output(b""), ("", False))


class Uncompyle6StateTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.dir = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def _w(self, name: str, text: str) -> Path:
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_states(self):
        self.assertEqual(cc.uncompyle6_state(self.dir / "nope.py"), "absent")
        stub = self._w("a.py", "# uncompyle6\n# Decompilation failed\n")
        self.assertEqual(cc.uncompyle6_state(stub), "stub")
        full = self._w("b.py", "# uncompyle6 version 3.9.3\nimport x\n")
        self.assertEqual(cc.uncompyle6_state(full), "full")
        rec = self._w("c.py", "# MXSJ 恢复产物\n# 结构摘要\n")
        self.assertEqual(cc.uncompyle6_state(rec), "recovered")
        self.assertEqual(cc.uncompyle6_state(self._w("d.py", "x = 1\n")),
                         "unknown")


class TargetEntriesTests(unittest.TestCase):
    def test_sorted_and_deduplicated(self):
        got = cc.target_entries({"failed": [5, 3, 5, 11]}, "failed")
        self.assertEqual(got, [3, 5, 11])

    def test_missing_class_says_what_is_available(self):
        with self.assertRaises(SystemExit) as cm:
            cc.target_entries({"failed": [1], "full": [2]}, "missing")
        self.assertIn("failed", str(cm.exception))


class PlanWriteTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.dir = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_writes_into_isolated_pycdc_tree(self):
        dest, ok = cc.plan_write(self.dir, "script/x/y.py")
        self.assertTrue(ok)
        self.assertEqual(dest.relative_to(self.dir), Path("pycdc/script/x/y.py"))

    def test_existing_artifact_is_never_overwritten(self):
        dest, _ = cc.plan_write(self.dir, "script/x/y.py")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("旧的", encoding="utf-8")
        dest2, ok = cc.plan_write(self.dir, "script/x/y.py")
        self.assertFalse(ok)
        self.assertEqual(dest2.read_text(encoding="utf-8"), "旧的")


class ResolvePycdcTests(unittest.TestCase):
    def test_explicit_missing_path_fails_loudly(self):
        with self.assertRaises(SystemExit):
            cc.resolve_pycdc("/definitely/not/here/pycdc")

    def test_fallback_candidate_is_honoured(self):
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "pycdc"
            cand.write_text("#!/bin/sh\n", encoding="utf-8")
            saved = os.environ.get("PATH", "")
            os.environ["PATH"] = ""  # 屏蔽 PATH，专测候选清单这一级
            try:
                self.assertEqual(cc.resolve_pycdc(None, candidates=(cand,)), cand)
            finally:
                os.environ["PATH"] = saved

    def test_hint_mentions_build_recipe(self):
        saved = os.environ.get("PATH", "")
        os.environ["PATH"] = ""  # 让 which 找不到，走报错分支
        try:
            with self.assertRaises(SystemExit) as cm:
                cc.resolve_pycdc(None, candidates=())
            self.assertIn("cmake", str(cm.exception))
        finally:
            os.environ["PATH"] = saved


class ReportShapeTests(unittest.TestCase):
    def test_fake_engine_output_is_json_serialisable(self):
        # 报告要能落盘；把一条典型记录 round-trip 一遍
        rec = {"entry_index": 2371, "status": "pycdc_ok", "lines": 120,
               "secs": 0.005, "uncompyle6": "stub", "stderr_head": []}
        self.assertEqual(json.loads(json.dumps(rec)), rec)


if __name__ == "__main__":
    unittest.main()
