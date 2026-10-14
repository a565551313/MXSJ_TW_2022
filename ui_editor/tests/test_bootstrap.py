"""启动自检脚本测试（不实际装包）。"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_bootstrap():
    spec = importlib.util.spec_from_file_location(
        "ui_bootstrap", ROOT / "bootstrap.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBootstrap(unittest.TestCase):
    def test_find_missing_all_present(self):
        bootstrap = _load_bootstrap()
        self.assertEqual(bootstrap.find_missing([("json", "json")]), [])

    def test_find_missing_detects_absent(self):
        bootstrap = _load_bootstrap()
        missing = bootstrap.find_missing(
            [("definitely_missing_mod_xyz", "xyz>=1")])
        self.assertEqual(len(missing), 1)


if __name__ == "__main__":
    unittest.main()
