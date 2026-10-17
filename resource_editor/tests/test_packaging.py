"""打包元数据一致性：`pyproject.toml`、包内 `__version__` 与 README 口径。

0.4.3 时曾出现 `pyproject.toml` 仍写 0.4.2 的漂移（README 已开 0.4.3 小节），
本测试把它钉住：三处版本必须一致，改版本时不会漏掉任何一处。
只读文本，不导入 Qt，无桌面环境也能跑。
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import resource_editor

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = PACKAGE_ROOT / "pyproject.toml"
README = PACKAGE_ROOT / "README.md"

_VERSION_RE = re.compile(r'(?m)^version\s*=\s*"([^"]+)"')
_STATED_RE = re.compile(r"当前版本：\*\*([0-9][0-9.]*)\*\*")
_HEADING_RE = re.compile(r"(?m)^##\s+([0-9]+\.[0-9]+\.[0-9]+)\b")


def pyproject_version(text: str) -> str:
    """读 [project] version；Python 3.10 没有 tomllib 时退回正则。"""
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - 仅 Python 3.10
        match = _VERSION_RE.search(text)
        if match is None:
            raise AssertionError(
                "pyproject.toml 里找不到 version") from None
        return match.group(1)
    return tomllib.loads(text)["project"]["version"]


def readme_version(text: str) -> str | None:
    """README 自称的当前版本：显式口径优先，否则取第一个版本小节标题。"""
    match = _STATED_RE.search(text)
    if match is not None:
        return match.group(1)
    match = _HEADING_RE.search(text)
    return match.group(1) if match is not None else None


class PackagingMetadataTests(unittest.TestCase):
    def test_pyproject_version_matches_package(self):
        text = PYPROJECT.read_text(encoding="utf-8")
        self.assertEqual(pyproject_version(text), resource_editor.__version__)

    def test_readme_states_the_same_version(self):
        stated = readme_version(README.read_text(encoding="utf-8"))
        if stated is None:
            self.skipTest("README 未使用可识别的版本口径")
        self.assertEqual(stated, resource_editor.__version__)


if __name__ == "__main__":
    unittest.main()
