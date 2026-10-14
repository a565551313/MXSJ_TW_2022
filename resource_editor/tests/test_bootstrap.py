"""bootstrap 启动脚本的依赖检查逻辑测试。"""
import importlib.util
import unittest
from pathlib import Path

BOOTSTRAP = Path(__file__).resolve().parents[1] / "bootstrap.py"


def _load_bootstrap():
    spec = importlib.util.spec_from_file_location("bootstrap", BOOTSTRAP)
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

    @unittest.skipUnless(
        importlib.util.find_spec("PySide6") is not None
        and importlib.util.find_spec("PIL") is not None,
        "当前环境未装齐依赖",
    )
    def test_current_env_complete(self):
        bootstrap = _load_bootstrap()
        self.assertEqual(bootstrap.find_missing(), [])


if __name__ == "__main__":
    unittest.main()
