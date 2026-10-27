# tools/devkit — 开发自检工具箱

> 当前测试范围与结果统一见 [STATUS](../../docs/STATUS.md)。静态检查和副本分发脚本使用标准库，**完整测试还需 Pillow**（精灵跨实现回归），不能再按纯标准库套件理解。
>
> 仓库外虚拟环境安装 `python -m pip install Pillow` 后，从仓库根运行 `python -m unittest discover -s tools/devkit/tests` 和 `python tools/devkit/vendor_core.py --check`。不要手改生成副本。

给在 Linux 沙箱里写代码、最终交付到 Windows 的 Agent 用。约定全文见 [`docs/PYTHON_TOOL_CONVENTIONS.md`](../../docs/PYTHON_TOOL_CONVENTIONS.md)。静态检查脚本使用标准库，Python 3.10+；完整测试的依赖与平台边界见上方说明。

## check_windows_compat.py — Windows 兼容性静态检查

```bash
python3 tools/devkit/check_windows_compat.py                     # 整个仓库
python3 tools/devkit/check_windows_compat.py resource_editor     # 只看某个工具目录
python3 tools/devkit/check_windows_compat.py --since origin/master --strict   # 只看改动文件，WARNING 也算失败
python3 tools/devkit/check_windows_compat.py --json /tmp/wincompat.json
python3 tools/devkit/check_windows_compat.py --list-rules
```

- 文件列表来自 `git ls-files`（已跟踪 + 未忽略的新文件），所以被 `.gitignore` 忽略的客户端二进制、`.venv` 不会被扫；不在 git 仓库里时退回目录遍历（`--no-git` 强制）。
- 默认排除 `tools/decompiler/output/`（机器生成的反编译线索）等目录；`--exclude PATTERN` 追加。
- 文件名检查永远看全量（大小写冲突需要完整目录视图），源码 / 脚本扫描只看给定路径或 `--since` 的改动文件。
- 退出码：0 无需处理；1 有 ERROR（`--strict` 时 WARNING 也算）；2 参数错误。
- 行内豁免：在该行加 `# win-ok: 原因`。

| 代码 | 级别 | 检查什么 |
|---|---|---|
| WIN101–106 | ERROR / WARNING | 文件名非法字符、保留设备名、结尾空格 / 句点、大小写冲突、路径过长、符号链接 |
| WIN201–203 | WARNING / ERROR | `.bat`/`.cmd` 的 LF 行尾、非 ASCII 前没有 `chcp 65001`、UTF-8 BOM |
| WIN301–302 | WARNING | `open()` / `read_text()` / `write_text()` 没写 `encoding` |
| WIN303–304 | ERROR | 导入 / 调用仅 POSIX 可用的模块与 API（`fcntl`、`os.killpg`、`signal.SIGKILL`…）；在 `try/except` 或平台判断里降级为 WARNING |
| WIN305 | WARNING | 硬编码 `/tmp`、`/home` 等绝对路径 |
| WIN306 | WARNING | 用字面量 `python` / `python3` 启动子进程（应 `sys.executable`） |
| WIN307 | INFO | 文件无法解析（如 Python 2 语法）或不是 UTF-8，已跳过 |
| CONV001 | ERROR | GUI 框架不是 PySide6（项目约定） |

启发式说明：`read_text`/`write_text` 只按方法名匹配，同名的自定义方法会误报，用 `# win-ok` 豁免；POSIX API 的检测只认 `import os` / `import signal` 及其别名。

## check_doc_versions.py — 文档版本号一致性检查

```bash
python3 tools/devkit/check_doc_versions.py                    # 检查 README / AGENTS / STATUS
python3 tools/devkit/check_doc_versions.py --doc docs/ROADMAP.md
python3 tools/devkit/check_doc_versions.py --json /tmp/docver.json
python3 tools/devkit/check_doc_versions.py --no-exclude-history   # 连历史叙述一起严格比对
```

**为什么有这个工具**：顶层文档（README / AGENTS / STATUS）历史上长期**手工维护**各组件的
版本号，导致 `ui_editor` 从 0.8.4 涨到 0.21.0 而 README 一次都没跟上，读者据此会得出
错误结论（「UI 编辑器只支持字段编码和布局导出」）。本工具把「文档里写的版本」与
「源码里真实的版本」机械比对，让漂移在提交前就红。

- 真实版本从各组件 `pyproject.toml` 的 `[project].version` 读取。
- 只在**版本上下文**里比对——组件名紧邻版本号才算声明；单纯提到组件名的叙述不受影响。
- **历史叙述默认跳过**：`docs/STATUS.md` 按设计保留大量历史轮次记录，那里的
  「UI 编辑器 0.19.0」是当时那一版的标题，属于正确事实。工具按行内标记
  （日期前缀、`### 3.xx` 编号章节、「以下保留历史内容」横幅段）识别并跳过。
  加 `--no-exclude-history` 可连历史叙述一起严格比对（届时大量 ERROR 属预期）。
- 退出码：0 一致；1 有 ERROR（版本声明不一致）；2 参数错误。

**边界**：这是**静态字符串比对**，只验证「文档写的版本 == 源码声明的版本」，
不验证功能、测试数或 Windows 实机行为，也不判断某段版本叙述是否**过时**——
过时与否仍要人工判断。

## vendor_core.py — 共享核心分发器

```bash
python3 tools/devkit/vendor_core.py --list     # 列出 mx_common/ 模块与分发目标
python3 tools/devkit/vendor_core.py --check    # 0 报告 = 编辑器副本与真源逐字节一致
python3 tools/devkit/vendor_core.py --diff     # 漂移处打印 unified diff
python3 tools/devkit/vendor_core.py --write    # 按真源重写副本
```

`mx_common/` 是路径哈希 / `.dlg` 原生存储 / 输出路径保护 / 精灵格式常量的
**唯一真源**；编辑器要「一个目录双击就能用」，所以运行时是复制而不是依赖。
副本 = 4 行生成横幅 + 真源全文，行尾归一化后比对（CRLF/CR 按 LF 语义，签出行尾不算漂移）；
`tools/devkit/tests/test_vendor_core.py` 在单元测试里跑 `--check`。

## 测试

```bash
python3 -m unittest discover -s tools/devkit/tests -v     # wincompat 自检 + 分发一致性 + 精灵多实现同源 + 文档版本一致性
ruff check tools/devkit                                   # 使用仓库根 ruff.toml
```

## 目录

```
tools/devkit/
  check_windows_compat.py   # CLI 入口
  check_doc_versions.py     # CLI 入口：文档版本号 vs pyproject.toml
  wincompat/
    model.py                # Severity / RULES / Finding
    filenames.py            # WIN1xx
    batch.py                # WIN2xx
    pysource.py             # WIN3xx + CONV001（ast）
    runner.py               # 文件收集（git / walk）、调度、汇总
  tests/test_wincompat.py
  tests/test_vendor_core.py
  tests/test_sprite_parity.py
  tests/test_doc_versions.py
```
