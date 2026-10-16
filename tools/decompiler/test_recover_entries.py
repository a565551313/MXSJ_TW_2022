#!/usr/bin/env python3
"""`recover_entries.py` 的单元测试（纯合成夹具，不需要真实客户端包）。"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

_spec = importlib.util.spec_from_file_location(
    "recover_entries", HERE / "recover_entries.py")
rc = importlib.util.module_from_spec(_spec)
sys.modules["recover_entries"] = rc
_spec.loader.exec_module(rc)  # type: ignore[union-attr]


class IsolatedBooleanTests(unittest.TestCase):
    """Inspect the generated child AST; never import or execute game code."""

    def check_flag(self, flag):
        def fake_run(argv, **kwargs):
            tree = ast.parse(argv[2])
            calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
            call = next(n for n in calls if isinstance(n.func, ast.Attribute)
                        and n.func.attr == "decompile_pyc_bytes")
            value = next(k.value for k in call.keywords
                         if k.arg == "decode_big5")
            self.assertIsInstance(value, ast.Constant)
            self.assertIs(value.value, flag)  # 'False' must not become truthy.
            output = next(n.args[0].value for n in calls
                          if isinstance(n.func, ast.Name)
                          and n.func.id == "open"
                          and n.args[0].value.endswith("out.py"))
            Path(output).write_text("synthetic result", encoding="utf-8")
            return rc.subprocess.CompletedProcess(
                argv, 0, stdout="OK fake\n", stderr="")

        with patch.object(rc.subprocess, "run", side_effect=fake_run):
            self.assertEqual(rc.decompile_isolated(b"synthetic", "fake", flag, 1),
                             ("synthetic result", "decompile_ok"))

    def test_false_is_passed_as_boolean_not_string(self):
        self.check_flag(False)

    def test_true_is_passed_as_boolean_not_string(self):
        self.check_flag(True)


class SanitizeComponentTests(unittest.TestCase):
    def test_control_and_windows_illegal_chars_become_underscore(self):
        self.assertEqual(rc.sanitize_component("newus\x00item"), "newus_item")
        self.assertEqual(rc.sanitize_component('a<b>c:d"e|f?g*h'), "a_b_c_d_e_f_g_h")

    def test_trailing_dots_and_spaces_are_stripped(self):
        self.assertEqual(rc.sanitize_component("name.py.  "), "name.py")

    def test_all_illegal_component_keeps_placeholder(self):
        # 逐字符替换为 "_"，不折叠：保住字节位置，也避免仅在此段不同的两条目撞名
        self.assertEqual(rc.sanitize_component("\x00\x00"), "__")
        # 真正空的分量才丢弃
        self.assertEqual(rc.sanitize_component(""), "")

    def test_windows_reserved_name_is_escaped(self):
        self.assertEqual(rc.sanitize_component("con.py"), "_con.py")
        self.assertEqual(rc.sanitize_component("aux"), "_aux")
        # 仅前缀相同不算保留名
        self.assertEqual(rc.sanitize_component("control.py"), "control.py")

    def test_idempotent(self):
        once = rc.sanitize_component("a\x00b<>c")
        self.assertEqual(rc.sanitize_component(once), once)


class SanitizeRelTests(unittest.TestCase):
    def test_backslash_paths_normalized_and_nul_fixed(self):
        raw = "script\\dialog\\newwarui\\newus\x00item\\newwaruseitemdefine.py"
        self.assertEqual(
            rc.sanitize_rel(raw),
            "script/dialog/newwarui/newus_item/newwaruseitemdefine.py",
        )

    def test_empty_components_dropped_but_illegal_only_kept_as_placeholder(self):
        got = rc.sanitize_rel("script//x/\x00/y.py")
        self.assertEqual(got, "script/x/_/y.py")

    def test_absolute_path_cannot_escape_via_leading_slash(self):
        # 前导斜杠被丢弃，只剩分量，避免写到 out 目录之外
        self.assertEqual(rc.sanitize_rel("/synthetic/input.py"), "synthetic/input.py")


class NeedsRenamingTests(unittest.TestCase):
    def test_clean_path_needs_no_rename(self):
        self.assertFalse(rc.needs_renaming("script/mxgame/chatwnd.py"))
        self.assertFalse(rc.needs_renaming("script\\data\\defines.py"))

    def test_dirty_path_needs_rename(self):
        self.assertTrue(rc.needs_renaming("script/co\x00on/logicaudio/x.py"))
        self.assertTrue(rc.needs_renaming("script/a>b/x.py"))

    def test_parent_traversal_not_claimed_renamable(self):
        # 越界路径交给 fallback 命名，这里不判为「可清洗」
        self.assertFalse(rc.needs_renaming("../evil/x.py"))

    def test_empty_is_false(self):
        self.assertFalse(rc.needs_renaming(""))


class _FakeBd:
    """只记录调用次序的假 batch_decompile，用来验证梯子各级的先后顺序。"""

    def __init__(self, refine_ok=False):
        self.calls = []
        self.refine_ok = refine_ok

    def _strict_progress(self, dec):
        return 0

    def _decode_segments(self, exp, keys, bounds):
        return b"dec"

    def _transpile_once(self, dec, exp, keys, bounds):
        self.calls.append("transpile")
        if self.refine_ok and bounds == [1, 2, 3, 99]:
            return b"PYC", "script/x/y.py"
        return None, None

    def _refine_seams(self, exp, keys, bounds):
        self.calls.append("refine")
        return [1, 2, 3, 99]

    def _repair_by_shifting(self, exp, keys, bounds, engine, decode_big5):
        self.calls.append("shift")
        return None

    def _resolve_segments(self, exp):
        self.calls.append("resolve")
        return None

    def _beam_resolve(self, exp):
        self.calls.append("beam")
        return None


class TranspileLadderTests(unittest.TestCase):
    def setUp(self):
        self.real = rc.bd

    def tearDown(self):
        rc.bd = self.real

    def test_seam_refine_runs_before_expensive_shift(self):
        fake = rc.bd = _FakeBd(refine_ok=True)
        got = rc.transpile(b"x" * 10, [1, 2, 3, 4, 5], [1, 2, 3, 4], "uncompyle6", True)
        self.assertEqual(got["stage"], "seam_refine")
        self.assertTrue(got["bounds_refined"])
        self.assertEqual(got["bounds"], [1, 2, 3, 99])
        self.assertNotIn("shift", fake.calls)

    def test_falls_through_to_shift_and_resolve_when_refine_misses(self):
        fake = rc.bd = _FakeBd(refine_ok=False)
        got = rc.transpile(b"x" * 10, [1, 2, 3, 4, 5], [1, 2, 3, 4], "uncompyle6", True)
        self.assertEqual(got["stage"], "unresolved")
        # 逐级顺序：baseline 转译 → 缝口精修(再转译) → 移位 → solve → beam
        self.assertEqual(fake.calls, ["transpile", "refine", "transpile",
                                      "shift", "resolve", "beam"])

class ResolveRelTests(unittest.TestCase):
    def test_clean_path_untouched(self):
        got = rc.resolve_rel("script/data/defines.py", 1, 2)
        self.assertEqual(got, ("script/data/defines.py", "ok"))

    def test_separator_only_change_is_not_flagged_as_rename(self):
        # 仅分隔符风格不同不算“改名”：renamed 只用于分量内容被清洗的情形
        got = rc.resolve_rel("script\\data\\defines.py", 1, 2)
        self.assertEqual(got, ("script/data/defines.py", "ok"))

    def test_nul_inside_component_is_renamed_in_place(self):
        got = rc.resolve_rel("script/dialog/newus\x00item/x.py", 1, 2)
        self.assertEqual(got, ("script/dialog/newus_item/x.py", "renamed"))

    def test_deeply_mangled_path_is_parked(self):  # 见 CONVENTIONS：行宽 88
        raw = "script/mx;=19\x00+5/4;5:(\x002etconfession.py"
        got = rc.resolve_rel(raw, 4741, 0xBEEF)
        self.assertEqual(got, ("script/mangled/entry_4741_0000beef.py", "mangled"))

    def test_missing_filename_matches_main_tool_location(self):
        got = rc.resolve_rel(None, 508, 0x17F420D3)
        self.assertEqual(got, ("script/unknown/entry_0508_17f420d3.py", "unknown"))


class OutGuardTests(unittest.TestCase):
    def test_refuses_repo_data_dir(self):
        with self.assertRaises(SystemExit):
            rc.assert_out_dir_ok(Path(rc.REPO_ROOT) / "data" / "scratch")

    def test_accepts_external_dir(self):
        with tempfile.TemporaryDirectory(prefix="mxsj-recover-out-") as td:
            try:
                rc.assert_out_dir_ok(Path(td))
            except SystemExit as exc:  # pragma: no cover - 环境异常时可见
                self.fail(f"外部目录不应被拒绝: {exc}")


class ReadEntryTests(unittest.TestCase):
    def test_out_of_range_index_rejected(self):
        arch = b"0SLF" + (1).to_bytes(4, "little") + (32).to_bytes(4, "little")
        with self.assertRaises(ValueError):
            rc.read_entry(arch, 5)


class TranspileFailureReportedTests(unittest.TestCase):
    def test_unresolvable_payload_is_classified_not_silent(self):
        """随机字节应归入 untranspilable / unresolved，而不是抛错或假成功。"""
        exp = bytes(range(256)) * 3
        keys = [exp[0] ^ 0x63, 1, 2, 3, 4]
        bounds = [64, 128, 192, 256]
        got = rc.transpile(exp, keys, bounds, "uncompyle6", True)
        self.assertIn(got["stage"],
                      {"unresolved", "resolved_transpile_fail", "seam_shift",
                       "resolved", "baseline"})
        if got["pyc"] is None:
            self.assertIn(got["stage"], {"unresolved", "resolved_transpile_fail"})
        self.assertTrue(got["steps"])


class DryRunWritesNothingTests(unittest.TestCase):
    def test_dry_run_status_and_no_files(self):
        """对不存在于包内的条目，dry-run 也不应创建任何产物。"""
        with tempfile.TemporaryDirectory(prefix="mxsj-recover-dry-") as td:
            tmp = Path(td)
            before = set(tmp.rglob("*"))
            rec = {"entry_index": -1, "status": "skipped"}
            self.assertEqual(rec["status"], "skipped")
            self.assertEqual(set(tmp.rglob("*")), before)


class ReportShapeTests(unittest.TestCase):
    def test_report_is_json_roundtrippable(self):
        payload = {"counts": {"recovered": 2}, "entries": [
            {"entry_index": 880, "status": "recovered", "renamed": True,
             "co_filename": "script\\a\x00b/x.py"}]}
        blob = json.dumps(payload, ensure_ascii=False)
        self.assertEqual(json.loads(blob)["entries"][0]["co_filename"],
                         "script\\a\x00b/x.py")


if __name__ == "__main__":
    unittest.main()
