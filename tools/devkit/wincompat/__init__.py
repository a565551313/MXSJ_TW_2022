"""Windows 兼容性静态检查（纯标准库，Python 3.10+）。

供 ``tools/devkit/check_windows_compat.py`` 调用，也可以在测试里直接 import。
规则列表见 :mod:`wincompat.model`，各类检查分别在：

* :mod:`wincompat.filenames` —— 文件名 / 路径（非法字符、保留名、大小写冲突…）
* :mod:`wincompat.batch` —— ``.bat`` / ``.cmd``（行尾、BOM、代码页）
* :mod:`wincompat.pysource` —— Python 源码（编码、POSIX 专用 API、硬编码路径…）
* :mod:`wincompat.runner` —— 文件收集、调度与汇总
"""

from __future__ import annotations

from wincompat.model import RULES, Finding, Severity
from wincompat.runner import CheckOptions, run_checks

__all__ = ["RULES", "CheckOptions", "Finding", "Severity", "run_checks"]
__version__ = "0.1.0"
