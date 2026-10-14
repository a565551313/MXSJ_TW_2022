"""在真 CPython 2.5.6 中编译/执行自写注册模块的离线回归。"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PYTHON25 = os.environ.get("MXSJ_PYTHON25")


@unittest.skipUnless(PYTHON25, "set MXSJ_PYTHON25 to the CPython 2.5.6 interpreter")
class RegistrationRuntimeTest(unittest.TestCase):
    def compile_and_run(self, *arguments):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            pyc = cwd / "register.pyc"
            compiled = subprocess.run(
                [
                    PYTHON25,
                    str(HERE / "compile_with_py25.py"),
                    str(HERE / "register.py"),
                    str(pyc),
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=cwd,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            return subprocess.run(
                [PYTHON25, str(HERE / "harness.py2"), str(pyc), *arguments],
                capture_output=True,
                text=True,
                check=False,
                cwd=cwd,
            )

    def test_authored_module_under_native_python_version(self):
        run = self.compile_and_run()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("ALL HARNESS CHECKS PASSED", run.stdout)
        self.assertIn(
            "five candidate names + shared credentials + honest stub OK", run.stdout
        )
        self.assertIn("future full-success popup guard", run.stdout)
        self.assertIn("no credentials in diagnostic log OK", run.stdout)
        self.assertIn(
            "entry stage markers + native boundary ordering OK", run.stdout
        )
        self.assertIn(
            "entry failures + geometry guard + atomic publication"
            " + private logging OK",
            run.stdout,
        )

    def test_initial_layout_exception_recovers_home(self):
        run = self.compile_and_run("--entry-failure-probe")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("initial layout exception recovery OK", run.stdout)


class RegistrationOutputGuardTest(unittest.TestCase):
    def test_inputs_and_their_hardlink_aliases_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            inputs = [cwd / "base.fls", cwd / "keys.json", cwd / "register.py"]
            for path in inputs:
                path.write_bytes(b"synthetic input; must not be overwritten")
            command = [
                sys.executable,
                str(HERE / "build_native_registration.py"),
                "--python25",
                sys.executable,
                "--archive",
                str(inputs[0]),
                "--keys",
                str(inputs[1]),
                "--source",
                str(inputs[2]),
            ]
            for index, source in enumerate(inputs):
                alias = cwd / f"alias_{index}.fls"
                os.link(source, alias)
                for output in (source, alias):
                    with self.subTest(output=output.name):
                        result = subprocess.run(
                            command + ["--output", str(output)],
                            cwd=cwd,
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn(
                            "refusing to overwrite an input file", result.stderr
                        )
                        self.assertEqual(
                            source.read_bytes(),
                            b"synthetic input; must not be overwritten",
                        )


if __name__ == "__main__":
    unittest.main()
