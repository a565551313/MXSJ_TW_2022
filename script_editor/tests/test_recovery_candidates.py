"""Synthetic recovery/transport tests, plus opt-in read-only corpus evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from native_fixtures import minimal_pyc

from script_editor.core.services.module_browser import read_module, recover_standard
from script_editor.core.services.pycdc_engine import (
    SOURCE_COMMIT,
    SOURCE_SHA256,
    PycdcEngine,
    discover_pycdc,
)
from script_editor.core.services.recovery_candidates import (
    RecoveryCandidate,
    best_candidate,
    primary_candidate,
    pycdc_candidate,
)
from script_editor.core.services.recovery_process import (
    ProcessOutput,
    RecoveryCancelled,
    run_bounded,
)


def engine_output(stdout=b"x = 1\n", stderr=b"", status="finished", code=0):
    output = ProcessOutput(status, code, stdout, stderr)
    return SimpleNamespace(
        run=lambda *a, **k: output,
        source_commit=SOURCE_COMMIT,
        source_sha256=SOURCE_SHA256,
        binary_sha256="a" * 64,
    )


class CandidateTests(unittest.TestCase):
    def test_partial_but_syntactically_valid_never_becomes_complete(self):
        candidate = pycdc_candidate(
            engine_output(b"x=1\n# WARNING: Decompyle incomplete\n"), b"", "py25"
        )
        self.assertEqual(candidate.status, "partial")
        self.assertFalse(candidate.complete)
        self.assertFalse(candidate.metadata()["syntax_checked"])
        self.assertFalse(candidate.metadata()["semantics_verified"])

    def test_original_bytes_and_full_stderr_survive_display_conversion(self):
        raw = b"title='\xff'\n"
        error = b"first\nsecond\xff\n"
        candidate = pycdc_candidate(engine_output(raw, error), b"", "py25")
        self.assertEqual(candidate.stdout, raw)
        self.assertEqual(candidate.stderr, error)
        self.assertIn("\\xff", candidate.source)
        self.assertEqual(candidate.status, "partial")
        self.assertEqual(
            candidate.metadata()["stdout_sha256"], hashlib.sha256(raw).hexdigest()
        )

    def test_nul_is_not_silently_dropped(self):
        candidate = pycdc_candidate(engine_output(b"x='\x00'\n"), b"", "py25")
        self.assertFalse(candidate.complete)
        self.assertIn(b"\x00", candidate.stdout)

    def test_header_only_output_is_failure_not_editable_source(self):
        candidate = pycdc_candidate(engine_output(b"# Source Generated\n"), b"", "py25")
        self.assertFalse(candidate.source)
        self.assertEqual(candidate.status, "failed")
        primary = primary_candidate(
            {
                "source": "# decompiler header only\n",
                "complete": False,
                "diagnostics": ["parser failed"],
                "raw_source": "# decompiler header only\n",
            }
        )
        self.assertFalse(primary.source)
        self.assertEqual(primary.status, "failed")
        self.assertTrue(primary.stdout)

    def test_process_status_never_upgraded_by_source_text(self):
        for status in ("timeout", "output_limit"):
            with self.subTest(status=status):
                candidate = pycdc_candidate(engine_output(status=status), b"", "py25")
                self.assertFalse(candidate.complete)
                self.assertEqual(candidate.status, status)
        candidate = pycdc_candidate(engine_output(code=1), b"", "py25")
        self.assertEqual(candidate.status, "failed")

    def test_cancellation_does_not_fall_through_to_source_candidate(self):
        with self.assertRaises(RecoveryCancelled):
            pycdc_candidate(engine_output(status="cancelled"), b"", "py25")

    def test_complete_fallback_preferred_partial_text_remains_available(self):
        first = RecoveryCandidate("uncompyle6", "v", "partial", "x=1\n")
        second = RecoveryCandidate("pycdc", "v", "complete", "x=2\n")
        self.assertIs(best_candidate([first, second]), second)
        self.assertIs(best_candidate([first, replace(second, status="partial")]), first)

    def test_bad_magic_rejected_before_any_engine(self):
        with patch(
            "script_editor.core.services.module_browser.discover_pycdc"
        ) as probe:
            with self.assertRaisesRegex(ValueError, "magic"):
                recover_standard(b"not a pyc", "py25")
            probe.assert_not_called()

    def test_optional_engine_absence_keeps_existing_recovery(self):
        result = {
            "source": "x=1\n",
            "complete": True,
            "diagnostics": [],
            "disassembly": "listing",
        }
        with (
            patch(
                "script_editor.core.services.module_browser.discover_pycdc",
                return_value=None,
            ),
            patch(
                "script_editor.core.services.module_browser._recover_primary",
                return_value=result,
            ),
        ):
            actual = recover_standard(minimal_pyc("py25"), "py25")
        self.assertEqual(actual["source"], "x=1\n")
        self.assertEqual(len(actual["candidates"]), 1)
        self.assertIn("未安装", "".join(actual["diagnostics"]))

    def test_invalid_optional_engine_manifest_keeps_primary_available(self):
        result = {
            "source": "x=1\n",
            "complete": True,
            "diagnostics": [],
            "disassembly": "listing",
        }
        with (
            patch(
                "script_editor.core.services.module_browser.discover_pycdc",
                side_effect=ValueError("bad optional manifest"),
            ),
            patch(
                "script_editor.core.services.module_browser._recover_primary",
                return_value=result,
            ),
        ):
            actual = recover_standard(minimal_pyc("py25"), "py25")
        self.assertTrue(actual["complete"])
        self.assertIn("bad optional manifest", "".join(actual["diagnostics"]))

    def test_primary_failure_does_not_erase_secondary_candidate(self):
        with patch(
            "script_editor.core.services.module_browser._recover_primary",
            side_effect=ValueError("primary unavailable"),
        ):
            result = recover_standard(
                minimal_pyc("py25"), "py25", pycdc=engine_output()
            )
        self.assertEqual(result["selected_engine"], "pycdc")
        self.assertEqual(result["candidates"][0].status, "failed")
        self.assertTrue(result["source"])

    def test_excluded_entry_never_reads_payload_or_inspects_module(self):
        archive = SimpleNamespace(
            vm="py25",
            path=Path("source.fls"),
            fingerprint=lambda: "a" * 64,
            _assert_unchanged=lambda: None,
            entries={1288: SimpleNamespace(identity="excluded")},
        )
        with patch(
            "script_editor.core.services.module_browser.inspect_module"
        ) as inspect:
            result = read_module(archive, 1288)
        inspect.assert_not_called()
        self.assertFalse(result.source)
        self.assertFalse(result.stored_preview)
        self.assertFalse(result.standard_sha256)
        self.assertIn("excluded_by_policy", result.diagnostics[0])


class TransportTests(unittest.TestCase):
    def test_binary_streams_are_not_decoded(self):
        result = run_bounded(
            [
                sys.executable,
                "-c",
                "import sys;sys.stdout.buffer.write(b'\\xff');"
                "sys.stderr.write('one\\ntwo')",
            ]
        )
        self.assertEqual(result.status, "finished")
        self.assertEqual(result.stdout, b"\xff")
        self.assertEqual(result.stderr, b"one\ntwo")

    def test_timeout_preserves_prefix_and_reaps_process(self):
        start = time.monotonic()
        result = run_bounded(
            [
                sys.executable,
                "-c",
                "import time;print('prefix',flush=True);time.sleep(8)",
            ],
            timeout=0.15,
        )
        self.assertEqual(result.status, "timeout")
        self.assertIn(b"prefix", result.stdout)
        self.assertLess(time.monotonic() - start, 3)

    def test_output_flood_is_bounded_and_never_success(self):
        result = run_bounded(
            [sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*65536)"],
            limit=4096,
        )
        self.assertEqual(result.status, "output_limit")
        self.assertEqual(len(result.stdout), 4096)

    def test_cancel_before_start_does_not_launch_process(self):
        cancel = threading.Event()
        cancel.set()
        with patch("subprocess.Popen") as popen:
            result = run_bounded(["NEVER_EXECUTE"], cancel=cancel)
        self.assertEqual(result.status, "cancelled")
        popen.assert_not_called()

    def test_cancel_running_process_keeps_partial_output(self):
        cancel = threading.Event()
        timer = threading.Timer(0.15, cancel.set)
        timer.start()
        try:
            result = run_bounded(
                [
                    sys.executable,
                    "-c",
                    "import time;print('prefix',flush=True);time.sleep(8)",
                ],
                cancel=cancel,
            )
        finally:
            timer.cancel()
        self.assertEqual(result.status, "cancelled")
        self.assertIn(b"prefix", result.stdout)


class EngineIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        name = "pycdc.exe" if os.name == "nt" else "pycdc"
        self.binary = self.root / name
        self.binary.write_bytes(b"test-only-not-executed")
        source_root = Path(__file__).resolve().parents[1]
        shutil.copyfile(
            source_root / "licenses/recovery/GPL-3.0.txt", self.root / "LICENSE.txt"
        )
        corresponding = self.root / "corresponding-source"
        corresponding.mkdir()
        archive = f"pycdc-{SOURCE_COMMIT}.tar.gz"
        shutil.copyfile(source_root / "third_party" / archive, corresponding / archive)
        self.manifest = {
            "schema_version": 1,
            "platform": sys.platform,
            "executable": name,
            "source_commit": SOURCE_COMMIT,
            "source_sha256": SOURCE_SHA256,
            "binary_sha256": hashlib.sha256(self.binary.read_bytes()).hexdigest(),
        }

    def save_manifest(self):
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf8"
        )

    def test_absence_is_optional(self):
        self.assertIsNone(discover_pycdc(self.root))

    def test_manifest_and_exact_binary_hash_required(self):
        self.save_manifest()
        self.assertIsInstance(discover_pycdc(self.root), PycdcEngine)
        self.binary.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "摘要"):
            discover_pycdc(self.root)

    def test_wrong_platform_source_or_path_rejected(self):
        for field, value in [
            ("platform", "other"),
            ("source_commit", "a" * 40),
            ("source_sha256", "a" * 64),
            ("executable", "../pycdc"),
        ]:
            with self.subTest(field=field):
                original = self.manifest[field]
                self.manifest[field] = value
                self.save_manifest()
                with self.assertRaises(ValueError):
                    discover_pycdc(self.root)
                self.manifest[field] = original

    def test_missing_corresponding_source_or_license_blocks_loading(self):
        self.save_manifest()
        (self.root / "LICENSE.txt").unlink()
        with self.assertRaises(ValueError):
            discover_pycdc(self.root)

    def test_stage_preserves_source_and_refuses_existing_destination(self):
        from script_editor.core.services.pycdc_engine import stage_pycdc

        self.save_manifest()
        install = self.root / "source" / "recovery_engines" / "pycdc"
        install.mkdir(parents=True)
        for name in (self.binary.name, "manifest.json", "LICENSE.txt"):
            shutil.copyfile(self.root / name, install / name)
        shutil.copytree(
            self.root / "corresponding-source", install / "corresponding-source"
        )
        destination = self.root / "destination"
        destination.mkdir()
        staged = stage_pycdc(self.root / "source", destination)
        self.assertEqual(staged.binary_sha256, self.manifest["binary_sha256"])
        with self.assertRaises(FileExistsError):
            stage_pycdc(self.root / "source", destination)

    def test_nonobject_or_deep_manifest_is_rejected_cleanly(self):
        for content in ("[]", "[" * 1200 + "0" + "]" * 1200):
            with self.subTest(content=content[:30]):
                (self.root / "manifest.json").write_text(content, encoding="utf8")
                with self.assertRaises(ValueError):
                    discover_pycdc(self.root)

    def test_oversized_manifest_is_not_read_unbounded(self):
        (self.root / "manifest.json").write_bytes(b"x" * 17000)
        with self.assertRaisesRegex(ValueError, "限制"):
            discover_pycdc(self.root)


@unittest.skipUnless(
    os.environ.get("MXSJ_CORPUS_SAMPLES") and os.environ.get("MXSJ_PYCDC_BUNDLE"),
    "opt-in corpus samples/pycdc required",
)
class ActualCorpusTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(os.environ["MXSJ_CORPUS_SAMPLES"])
        self.engine = discover_pycdc(Path(os.environ["MXSJ_PYCDC_BUNDLE"]))

    def recover(self, entry, *, failure=False, timeout=2):
        directory = self.root / (
            "MXSJ_CORPUS_SAMPLE_FAILURE_82_20261015/sample_failure"
            if failure
            else "MXSJ_CORPUS_SAMPLE_8212b26_20261015/sample_v2"
        )
        record = json.loads(
            (directory / f"entries/{entry:04d}/record.json").read_text(encoding="utf-8")
        )
        self.assertEqual(record["entry_index"], entry)
        artifact = next(
            a for a in record["artifacts"] if a["path"].endswith("standard.pyc")
        )
        data = (directory.parent / artifact["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), artifact["sha256"])
        return recover_standard(data, "py25", pycdc=self.engine, timeout=timeout)

    def test_real_partial_source_is_editable_but_never_complete(self):
        result = self.recover(124)
        self.assertEqual(result["selected_engine"], "pycdc")
        self.assertIn("GetCountryData", result["source"])
        self.assertFalse(result["complete"])
        self.assertEqual(result["candidates"][1].status, "partial")

    def test_real_non_utf8_candidates_keep_exact_engine_bytes(self):
        for entry in (3505, 4861):
            with self.subTest(entry=entry):
                result = self.recover(entry)
                candidate = result["candidates"][1]
                self.assertTrue(candidate.source)
                self.assertFalse(candidate.complete)
                with self.assertRaises(UnicodeDecodeError):
                    candidate.stdout.decode("utf8")

    def test_real_pathological_primary_times_out_secondary_still_recovers(self):
        result = self.recover(2371, timeout=0.5)
        self.assertEqual(result["selected_engine"], "pycdc")
        self.assertEqual(result["candidates"][0].status, "timeout")
        self.assertTrue(result["candidates"][1].source)

    def test_real_both_fail_has_no_fake_source(self):
        result = self.recover(82, failure=True)
        self.assertFalse(result["source"])
        self.assertTrue(all(c.status == "failed" for c in result["candidates"]))
        self.assertTrue(result["candidates"][1].stderr)

    def test_real_complete_pair_keeps_two_candidates_and_origin(self):
        result = self.recover(4305)
        self.assertEqual(result["selected_engine"], "uncompyle6")
        self.assertEqual(len(result["candidates"]), 2)
        self.assertTrue(all(c.complete for c in result["candidates"]))
        self.assertEqual(
            result["candidates"][1].binary_sha256, self.engine.binary_sha256
        )

    def test_original_archive_path_uses_secondary_after_primary_timeout(self):
        from script_editor.core.archives.document import ArchiveDocument
        from script_editor.core.services.bundled_catalog import bundled_catalog

        repo = os.environ.get("MXSJ_M2_REPO")
        if not repo:
            self.skipTest("opt-in original package required")
        repo = Path(repo)
        with ArchiveDocument(repo / "data/script.fls") as archive:
            fingerprint = archive.fingerprint()
            catalog = bundled_catalog(archive, repo / "script_editor")
            report = read_module(archive, 2371, catalog, pycdc=self.engine, timeout=0.5)
            self.assertEqual(report.selected_engine, "pycdc", report.diagnostics)
            self.assertTrue(report.source)
            self.assertEqual(report.candidates[0].status, "timeout")
            self.assertEqual(archive.fingerprint(), fingerprint)
            self.assertEqual(report.metadata()["archive_sha256"], fingerprint)


@unittest.skipUnless(os.environ.get("MXSJ_PYCDC_BUNDLE"), "verified pycdc required")
class ActualEngineSmoke(unittest.TestCase):
    def test_both_real_vms_second_engine_compile_without_execution(self):
        from script_editor.core.compiler.runner import (
            compile_standard,
            inspect_compiler,
        )

        engine = discover_pycdc(Path(os.environ["MXSJ_PYCDC_BUNDLE"]))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for vm in ("py25", "py27"):
                with self.subTest(vm=vm):
                    compiler_path = os.environ.get("MXSJ_" + vm.upper())
                    if not compiler_path:
                        self.skipTest("both actual standard compilers required")
                    compiler = inspect_compiler(Path(compiler_path), vm)
                    sentinel = root / "MUST_NOT_EXECUTE"
                    source = (
                        f"engine_smoke=42\nopen({str(sentinel)!r},'w').write('NO')\n"
                    )
                    pyc = root / (vm + ".pyc")
                    compile_standard(compiler, source, b"engine-smoke.py", pyc)
                    candidate = pycdc_candidate(engine, pyc.read_bytes(), vm)
                    self.assertTrue(candidate.complete, candidate.diagnostics)
                    self.assertIn("engine_smoke", candidate.source)
                    compile_standard(
                        compiler,
                        candidate.source,
                        b"engine-smoke.py",
                        root / (vm + "-recovered.pyc"),
                    )
                    self.assertFalse(sentinel.exists())
