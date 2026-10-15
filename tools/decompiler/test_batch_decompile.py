#!/usr/bin/env python3
"""``batch_decompile.py`` 开跑前校验与失败可见性的回归测试。

覆盖 2026-10-15 补上的三件事：pycdc 路径解析优先级、解释器缺引擎时不得静默跑完、
转译失败必须落盘成可数的标记（外加 ``--report`` 清点表与下游键名约定）。
只用合成夹具；唯一碰真实归档的那条在归档缺席时自动跳过。
"""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "decompiler"))

import batch_decompile as bd  # noqa: E402

ARCHIVE = REPO_ROOT / "data" / "script.fls"


def make_fake_pycdc(root: Path, name: str = "pycdc") -> Path:
    """造一个可执行的假 pycdc，只为验证「能不能被找到」。"""
    exe = root / name
    exe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return exe


class ResolvePycdcBinTests(unittest.TestCase):
    def test_explicit_argument_wins(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            chosen = make_fake_pycdc(root, "chosen")
            decoy = make_fake_pycdc(root, "pycdc")
            env = {bd.PYCDC_ENV: str(decoy), "PATH": str(root)}
            with mock.patch.dict(os.environ, env, clear=False):
                self.assertEqual(bd.resolve_pycdc_bin(chosen), chosen)

    def test_env_var_beats_legacy_and_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            from_env = make_fake_pycdc(root, "from_env")
            legacy = make_fake_pycdc(root, "legacy")
            make_fake_pycdc(root, "pycdc")  # PATH 上也有，但优先级最低
            env = {bd.PYCDC_ENV: str(from_env), "PATH": str(root)}
            with mock.patch.dict(os.environ, env, clear=False), \
                    mock.patch.object(bd, "PYCDC_LEGACY_DEFAULT", legacy):
                self.assertEqual(bd.resolve_pycdc_bin(None), from_env)

    def test_legacy_default_used_when_nothing_else_set(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            legacy = make_fake_pycdc(root, "legacy")
            with mock.patch.dict(os.environ, {bd.PYCDC_ENV: "", "PATH": str(root)},
                                 clear=False), \
                    mock.patch.object(bd, "PYCDC_LEGACY_DEFAULT", legacy):
                self.assertEqual(bd.resolve_pycdc_bin(None), legacy)

    def test_none_when_nothing_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with mock.patch.dict(os.environ, {bd.PYCDC_ENV: "", "PATH": str(root)},
                                 clear=False), \
                    mock.patch.object(bd, "PYCDC_LEGACY_DEFAULT", root / "missing"):
                self.assertIsNone(bd.resolve_pycdc_bin(None))

    def test_unexecutable_file_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            plain = Path(td) / "pycdc"
            plain.write_text("not executable\n", encoding="utf-8")
            plain.chmod(0o644)
            with mock.patch.dict(os.environ, {bd.PYCDC_ENV: "", "PATH": str(td)},
                                 clear=False), \
                    mock.patch.object(bd, "PYCDC_LEGACY_DEFAULT", Path(td) / "nope"):
                self.assertIsNone(bd.resolve_pycdc_bin(plain))


class ProbeEnginesTests(unittest.TestCase):
    def test_uncompyle6_is_only_used_for_auto_and_uncompyle6(self):
        with mock.patch.object(bd, "resolve_pycdc_bin", lambda explicit=None: None), \
                mock.patch("importlib.util.find_spec", lambda name: object()):
            self.assertTrue(bd.probe_engines("auto")["uncompyle6_used"])
            self.assertTrue(bd.probe_engines("uncompyle6")["uncompyle6_used"])
            self.assertFalse(bd.probe_engines("pycdc")["uncompyle6_used"])

    def test_probe_records_the_running_interpreter(self):
        # 历史坑的根因就是「解释器选错」，所以这个字段必须进探针输出与报告。
        with mock.patch.object(bd, "resolve_pycdc_bin", lambda explicit=None: None), \
                mock.patch("importlib.util.find_spec", lambda name: None):
            got = bd.probe_engines("auto")
        self.assertEqual(got["interpreter"], sys.executable)
        self.assertFalse(got["uncompyle6_installed"])
        self.assertIsNone(got["pycdc"])


class PreflightTests(unittest.TestCase):
    def test_refuses_writing_into_data_dir(self):
        with self.assertRaises(SystemExit) as ctx:
            bd.preflight("pycdc", REPO_ROOT / "data" / "out", ARCHIVE)
        self.assertIn("原包目录", str(ctx.exception))

    def test_refuses_writing_into_repo_root(self):
        with self.assertRaises(SystemExit) as ctx:
            bd.preflight("pycdc", REPO_ROOT, ARCHIVE)
        self.assertIn("仓库根目录", str(ctx.exception))

    def test_missing_pycdc_file_is_refused_before_the_run(self):
        with tempfile.TemporaryDirectory() as td, self.assertRaises(SystemExit) as ctx:
            bd.preflight("auto", Path(td) / "out", ARCHIVE, Path(td) / "nope")
        self.assertIn("--pycdc", str(ctx.exception))

    def test_pycdc_path_is_published_to_the_env_for_child_workers(self):
        with tempfile.TemporaryDirectory() as td:
            exe = make_fake_pycdc(Path(td))
            with mock.patch.dict(os.environ, {bd.PYCDC_ENV: ""}, clear=False):
                bd.preflight("auto", Path(td) / "out", ARCHIVE, exe)
                self.assertEqual(os.environ[bd.PYCDC_ENV], str(exe.resolve()))

    def _no_u6(self):
        return mock.patch.object(bd, "probe_engines",
                                 lambda engine: {"requested": engine,
                                                 "uncompyle6_installed": False,
                                                 "uncompyle6_used": False,
                                                 "pycdc": None, "interpreter": "x"})

    def test_missing_uncompyle6_hard_fails_for_auto(self):
        with tempfile.TemporaryDirectory() as td, self._no_u6():
            with self.assertRaises(SystemExit) as ctx:
                bd.preflight("auto", Path(td) / "out", ARCHIVE)
        msg = str(ctx.exception)
        self.assertIn("52 字节", msg)
        self.assertIn("--allow-missing-engine", msg)

    def test_allow_missing_engine_downgrades_to_warning(self):
        with tempfile.TemporaryDirectory() as td, self._no_u6():
            with mock.patch("builtins.print") as fake:
                bd.preflight("auto", Path(td) / "out", ARCHIVE,
                             allow_missing_engine=True)
            fake.assert_not_called()  # 显式放行时不再唠叨

    def test_pycdc_engine_without_pycdc_is_refused(self):
        # 选了 --engine pycdc 却没有它：跑完同样只是失败占位，属于同一类静默失效。
        with tempfile.TemporaryDirectory() as td, self._no_u6():
            with self.assertRaises(SystemExit) as ctx:
                bd.preflight("pycdc", Path(td) / "out", ARCHIVE)
        self.assertIn("找不到可用的 pycdc", str(ctx.exception))

    def test_pycdc_engine_without_uncompyle6_is_allowed(self):
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(bd, "probe_engines",
                                  lambda engine: {"requested": engine,
                                                  "uncompyle6_installed": False,
                                                  "uncompyle6_used": False,
                                                  "pycdc": "/bin/sh",
                                                  "interpreter": "x"}):
            eng = bd.preflight("pycdc", Path(td) / "out", ARCHIVE)
        self.assertEqual(eng["requested"], "pycdc")


class TranspileFailureMarkerTests(unittest.TestCase):
    def test_marker_text_distinguishes_transpile_from_decompile_failure(self):
        txt = bd._transpile_failure_marker(1954, 0x1234ABCD, ValueError("bad marshal"))
        self.assertIn("TRANSMAP FAILED entry=1954", txt)
        self.assertIn("id=1234abcd", txt)
        self.assertIn("ValueError: bad marshal", txt)
        self.assertIn("--entries 1954", txt)
        # 不能被下游成色判定误认成反编译占位（crosscheck 靠正文串分类）
        self.assertNotIn(bd.DECOMPILE_FAIL_MARK, txt)
        import crosscheck_pycdc as cc
        with tempfile.TemporaryDirectory() as tmp:
            marker_file = Path(tmp) / "m.py"
            marker_file.write_text(txt, encoding="utf-8")
            state = cc.uncompyle6_state(marker_file)
            # 必须是 unknown：认成 stub 会被 --class failed 再复核一遍，
            # 认成 full/recovered 更糟——会被当成可用源码。
            self.assertEqual(
                state, "unknown",
                f"标记文件的成色判定漂了：{state}")

    def test_worker_writes_marker_instead_of_dropping_the_entry(self):
        with tempfile.TemporaryDirectory() as td:
            task = (1954, 0x1234ABCD, b"\x00\x01not-a-pyc-payload", [1, 2, 3, 4, 5],
                    [0, 1, 2, 3], td, None, "uncompyle6", True)
            res = bd._worker_script_fls(task)
            self.assertFalse(res["ok"])
            self.assertTrue(res["transpile_fail"])
            written = Path(td) / res["rel"]
            self.assertTrue(written.is_file(), "转译失败的条目必须留下文件")
            self.assertIn("TRANSMAP FAILED", written.read_text(encoding="utf-8"))
            self.assertIn("failed", written.parts)  # script/failed/ 下

    def test_marker_is_never_written_over_a_real_module_path(self):
        with tempfile.TemporaryDirectory() as td:
            real = Path(td) / "script" / "data" / "servicedata.py"
            real.parent.mkdir(parents=True)
            real.write_text("# 真产物\n", encoding="utf-8")
            task = (1931, 0x0, b"\x00garbage", [0] * 5, [0] * 5, td, None,
                    "uncompyle6", True)
            res = bd._worker_script_fls(task)
            self.assertTrue(res["transpile_fail"])
            self.assertEqual(real.read_text(encoding="utf-8"), "# 真产物\n")


@unittest.skipUnless(ARCHIVE.is_file(), "需要仓库内的 data/script.fls")
class CensusAndReportTests(unittest.TestCase):
    def _run(self, out: Path, report: Path):
        return bd.process_script_fls(
            ARCHIVE, out, None, "auto", True, None, 2, 1, report=report)

    def test_report_contains_both_classes_and_pins_the_archive(self):
        with tempfile.TemporaryDirectory() as td:
            out, report = Path(td) / "out", Path(td) / "acc.json"
            res = self._run(out, report)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["kind"], "script_fls_accounting")
            self.assertEqual(payload["total"], res["total"])
            c = payload["counts"]
            self.assertEqual(c["ok"] + c["failed"] + c["missing"], payload["total"])
            self.assertEqual(len(payload["inputs"]["sha256"]), 64)
            # 与批处理内的条目数一致性（每条要么成功、要么两类失败之一）
            self.assertEqual(
                sorted(payload["failed"] + payload["missing"] +
                       [r["idx"] for r in res["results"] if r["ok"]]),
                sorted(r["idx"] for r in res["results"]))

    def test_report_keys_feed_the_two_downstream_tools(self):
        import crosscheck_pycdc as cc
        with tempfile.TemporaryDirectory() as td:
            out, report = Path(td) / "out", Path(td) / "acc.json"
            self._run(out, report)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertIsInstance(payload["failed"], list)
            self.assertIsInstance(cc.target_entries(payload, "failed"), list)
            self.assertIsInstance(payload["missing"], list)  # recover_entries 读这个键

    def test_no_entry_is_silently_absent_from_the_output_tree(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            res = self._run(out, Path(td) / "acc.json")
            written = {p.relative_to(out).as_posix() for p in out.rglob("*.py")}
            for r in res["results"]:
                self.assertIn(Path(r["rel"]).as_posix(), written,
                              "每条被处理的条目都要留下文件（真源码、失败占位或明示标记）")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
