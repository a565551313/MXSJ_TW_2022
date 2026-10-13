"""bootstrap 启动脚本的依赖检查与参数处理测试（不开窗口、不联网）。"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

BOOTSTRAP = Path(__file__).resolve().parents[1] / "bootstrap.py"


def _load_bootstrap():
    spec = importlib.util.spec_from_file_location("map_editor_bootstrap", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBootstrap(unittest.TestCase):
    def test_missing_module_detected(self):
        bootstrap = _load_bootstrap()
        missing = bootstrap.find_missing(
            [("definitely_not_a_real_module_xyz", "SomePackage")])
        self.assertEqual(
            missing, [("definitely_not_a_real_module_xyz", "SomePackage")])

    def test_requirements_match_requirements_txt(self):
        """bootstrap 的依赖表必须和 requirements.txt 一个来源，不能各改各的。"""
        bootstrap = _load_bootstrap()
        req = (BOOTSTRAP.parent / "requirements.txt").read_text(encoding="utf-8")
        pinned = {
            line.strip() for line in req.splitlines()
            if line.strip() and not line.startswith("#")
        }
        self.assertEqual({spec for _, spec in bootstrap.REQUIREMENTS}, pinned)

    @unittest.skipUnless(
        importlib.util.find_spec("PySide6") is not None
        and importlib.util.find_spec("PIL") is not None,
        "当前环境未装齐依赖",
    )
    def test_current_env_complete(self):
        bootstrap = _load_bootstrap()
        self.assertEqual(bootstrap.find_missing(), [])

    def test_check_only_does_not_import_gui(self):
        """``--check-only`` 只做自检：依赖齐全时退出码 0，且不会去 import Qt 界面。"""
        bootstrap = _load_bootstrap()
        with mock.patch.object(bootstrap, "ensure_dependencies", return_value=True), \
                mock.patch.dict("sys.modules", {"map_editor.cli": None}):
            self.assertEqual(bootstrap.main(["--check-only"]), 0)

    def test_dependency_failure_stops_before_gui(self):
        bootstrap = _load_bootstrap()
        with mock.patch.object(bootstrap, "ensure_dependencies", return_value=False):
            self.assertEqual(bootstrap.main([]), 2)

    def test_gui_flag_is_forced_and_other_args_forwarded(self):
        bootstrap = _load_bootstrap()
        fake_cli = mock.Mock()
        fake_cli.main.return_value = 0
        with mock.patch.object(bootstrap, "ensure_dependencies", return_value=True), \
                mock.patch.dict("sys.modules", {"map_editor.cli": fake_cli}):
            self.assertEqual(bootstrap.main(["--client-root", "X:/mxsj"]), 0)
        fake_cli.main.assert_called_once_with(["--gui", "--client-root", "X:/mxsj"])


if __name__ == "__main__":
    unittest.main()
