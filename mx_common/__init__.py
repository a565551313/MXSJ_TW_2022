"""MXSJ 编辑器共享核心：**唯一真源**（不要在这个包里 import 任何编辑器）。

编辑器交付形态是「一个目录双击就能用」（`bootstrap.py` 不 `pip install`
本包，见 `docs/PYTHON_TOOL_CONVENTIONS.md` §3），所以运行代码不是
`import mx_common`，而是**复制**：`tools/devkit/vendor_core.py` 把本目录
每个模块复制到各编辑器的 `core/` 下，每份副本带一行生成横幅、禁止手改。

改法（三步）：

1. 只改 `mx_common/<模块>.py`；
2. `python3 tools/devkit/vendor_core.py --write` 重新分发；
3. `python3 tools/devkit/vendor_core.py --check` 应为 0 报告——`tools/devkit/
   tests/test_vendor_core.py` 会把这件事钉成测试，漂移就红。

包内约束：只依赖标准库（`sprite_format.py` 连 Pillow 都不依赖），
不 import PySide6，不做 IO——这样三份副本可以在任何环境里被比对。
"""
