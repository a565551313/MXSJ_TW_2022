"""Bootstrap installation and stdio contract tests."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock

PATH = Path(__file__).resolve().parents[1] / "bootstrap.py"
spec = importlib.util.spec_from_file_location("client_mcp_bootstrap", PATH)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(TestCase):
    def test_check_only_never_installs(self):
        with mock.patch.object(bootstrap, "find_missing", return_value=["mcp"]):
            with mock.patch.object(bootstrap, "install_packages") as install:
                self.assertEqual(bootstrap.main(["--check-only"]), 2)
                install.assert_not_called()

    def test_install_fallback_and_recheck(self):
        results = [SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]
        with mock.patch.object(bootstrap.subprocess, "run", side_effect=results) as run:
            with mock.patch.object(bootstrap, "find_missing", return_value=[]):
                self.assertTrue(bootstrap.install_packages(["mcp>=1.2.0,<2"]))
        self.assertEqual(run.call_count, 2)
        self.assertIn(bootstrap.MIRRORS[1], run.call_args.args[0])
        self.assertIs(run.call_args.kwargs["stdout"], bootstrap.sys.stderr)

    def test_successful_pip_requires_import_recheck(self):
        with mock.patch.object(
            bootstrap.subprocess, "run", return_value=SimpleNamespace(returncode=0)
        ):
            with mock.patch.object(bootstrap, "find_missing", return_value=["mcp"]):
                self.assertFalse(bootstrap.install_packages(["mcp"]))
