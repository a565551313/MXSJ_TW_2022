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
    def test_authored_module_under_native_python_version(self):
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
            run = subprocess.run(
                [PYTHON25, str(HERE / "harness.py2"), str(pyc)],
                capture_output=True,
                text=True,
                check=False,
                cwd=cwd,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("ALL HARNESS CHECKS PASSED", run.stdout)
            self.assertIn(
                "five candidate names + shared credentials + honest stub OK", run.stdout
            )
            self.assertIn("future full-success popup guard", run.stdout)
            self.assertIn(
                "faithful archive: real terms + confirm fallback", run.stdout
            )
            self.assertIn("no credentials in diagnostic log OK", run.stdout)


@unittest.skipUnless(PYTHON25, "set MXSJ_PYTHON25 to the CPython 2.5.6 interpreter")
class RegistrationBrokenClientWorldTest(unittest.TestCase):
    """真客戶端可能比桩件世界殘酷：缺常量、版式沒導入都不能「點了沒反應」。

    這組測試要用真 py2.5 編譯並跑 `harness.py2`，所以跟上面那組一樣：沒設
    `MXSJ_PYTHON25` 就明確 skip（以前是直接 TypeError，看起來像代碼壞了）。
    """

    @staticmethod
    def _run(pyc: Path, cwd: Path, mode: str) -> str:
        env = dict(os.environ, MXSJ_HARNESS_MODE=mode)
        run = subprocess.run(
            [PYTHON25, str(HERE / "harness.py2"), str(pyc)],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
            env=env,
        )
        assert run.returncode == 0, run.stdout + run.stderr
        return run.stdout

    def test_missing_constants_and_missing_layout_fail_loudly(self):
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
            for mode, line in (
                ("no_font_edit", "falls back and still opens OK"),
                ("missing_layout", "logged, popup shown, recovered home OK"),
            ):
                with self.subTest(mode=mode):
                    out = self._run(pyc, cwd, mode)
                    self.assertIn(line, out)
                    self.assertIn("ALL HARNESS CHECKS PASSED", out)


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
