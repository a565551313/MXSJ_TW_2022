# Python 工具与编辑器开发约定

> **2026-10-14 与用户约定。** 适用于仓库内所有**新写或大改**的 Python 工具、编辑器、脚本（`tools/`、`*_editor/`、`server/tools/`、`work/**/tools/` 等）。
> 摘要在 [`AGENTS.md`](../AGENTS.md) §5；现有工具与本约定的差距、补齐顺序记录在 [`STATUS_HISTORY §3.5`](archive/STATUS_HISTORY.md#s3-3-5)。
> 约定只有一个目的：**用户在 Windows 上双击就能用，不来回折腾。**

## 0. 一句话版本

PEP 8 + 模块化；GUI 只用 PySide6；每个工具自带「自检并启动」脚本和「一键打 EXE」脚本；在 Linux 上开发的东西，交付前必须过 Windows 检查，并如实写明哪些在 Windows 实机验过、哪些没有。

## 1. 代码规范：PEP 8 + 模块化

1. **风格 = PEP 8，用 ruff 检查。** 配置统一是（仓库根 [`ruff.toml`](../ruff.toml) 已给出默认值，各工具的 `pyproject.toml` 照抄一份）：
   ```toml
   [tool.ruff]
   line-length = 88
   target-version = "py310"

   [tool.ruff.lint]
   select = ["E", "W", "F", "I", "UP", "B"]
   ```
   命令：`pip install ruff && ruff check <工具目录>`，提交前必须 **0 报告**；`ruff format <工具目录>` 统一排版。不要用整文件 `# noqa` 或 `per-file-ignores` 把问题藏起来；个别行确有理由时写 `# noqa: <code>  # 原因`。
2. **Python ≥ 3.10**（与现有编辑器一致），每个文件以 `from __future__ import annotations` 开头；类型标注写 `X | None`，不写 `Optional[X]`。
3. **目录布局**（新工具照抄，现有编辑器 `resource_editor/`、`ui_editor/` 就是这个样子）：
   ```
   <tool>/
     pyproject.toml          # 名称、版本、依赖、ruff 配置、[project.gui-scripts] 入口
     README.md               # 用途 / 用法 / 测试 / 构建；版本号与 pyproject 一致
     bootstrap.py            # 自检并启动（§3）
     启动<工具名>.bat         # Windows 双击入口（§3）
     build_exe.bat           # 一键构建 EXE（§4）
     <tool>.spec             # PyInstaller 配置（§4）
     requirements.txt        # 运行依赖；requirements-dev.txt 另含 pyinstaller / ruff
     src/<package>/
       __init__.py           # __version__
       __main__.py           # python -m <package>
       app.py                # 组装 QApplication，提供 main(argv) -> int
       core/                 # 纯逻辑：格式解析、编解码、模型、服务。禁止 import PySide6
       gui/                  # 窗口、控件、绘制；只调用 core 的公开接口
     tests/                  # unittest；core 测试不依赖 Qt
   ```
4. **拆分原则**：一个模块一个职责；单文件超过约 600 行、单个函数超过约 80 行就拆；GUI 回调里不写解析 / IO 逻辑，交给 `core` 的服务函数；魔数（偏移、密钥、结构常量）集中到 `core/constants.py` 并注明来源（反汇编地址或 `notes/` 文件）。
5. **可测试**：`core` 函数接受 `Path` / `bytes` 参数，不隐式读全局路径或环境变量；`main(argv)` 返回 `int`，模块 import 时不产生副作用；每个 bug 修复都带一个能复现旧 bug 的测试（见 AGENTS §6「工作方式」）。
6. **路径一律 `pathlib.Path`**，不手拼 `/`；文本文件读写**必须**显式 `encoding="utf-8"`（读用户可能用记事本改过的文件用 `utf-8-sig`）；CSV 写入加 `newline=""`。
7. **多个工具共用的核心代码放 `mx_common/`，用生成式副本分发**（2026-10-16 加，UI 编辑器分析 P1-2 的落地）：同一份格式代码在两个编辑器里各存一份、靠人记得同步，已经导致 `sprite.py` 与资源编辑器实现分叉。现在真源在仓库根 `mx_common/`，`tools/devkit/vendor_core.py` 把它复制到各工具的 `core/` 下（副本 = 生成横幅 + 真源全文，行尾归一化后比对，**勿手改**）：

   ```bash
   python3 tools/devkit/vendor_core.py --check   # 0 报告；tests/test_vendor_core.py 会跑
   python3 tools/devkit/vendor_core.py --write   # 改完真源后分发
   ```

   为什么是复制而不是依赖：工具要能在一个只有 Python + PySide6 的目录里双击运行（§3，不 `pip install` 本仓库任何包）。**行为一致性**不能只靠「同源」——落点不同的实现（如 UI 无 Pillow 的 RGBA 解码 vs 资源编辑器 Pillow 落点）要有交叉测试（`tools/devkit/tests/test_sprite_parity.py` 就是例子）。

## 2. GUI：一律 PySide6

- 新 GUI **只用 PySide6**（`PySide6>=6.4`，与现有编辑器一致）。禁止 tkinter、PyQt5/6、wxPython、GTK；CLI 工具要加界面也用 PySide6，不要用 tkinter「凑合」。
- Qt 只出现在 `gui/` 和 `app.py`；`core/` 不得 import PySide6——因为 core 测试要在没有显示器、没有 `libGL` 的沙箱里跑。
- 长任务放 `QThread` / `QThreadPool`，主线程不阻塞；文件选择用 `QFileDialog`（返回的 Windows 路径带反斜杠，立刻包成 `Path`）。
- 界面文字中文；字体不写死（Qt 自动回退到微软雅黑 / Noto），布局用 layout 而不是绝对坐标，1.25×/1.5× DPI 下不能截断。
- GUI 测试用 `QT_QPA_PLATFORM=offscreen`；沙箱缺 `libGL.so.1` 跑不了时写「未执行」，**不算通过**。

## 3. 自检并启动脚本：`bootstrap.py` + `启动<工具名>.bat`

目标：用户拿到目录后**双击一个文件**就能开界面；缺什么自动装；出错不闪退、留日志。

> 2026-11-03 用户加码：**涉及开发、测试、工具配合的环节一律不许要求用户使用命令行**，也不许让用户
> 解压到“独立目录”、手写配置、生成令牌或去仓库外找产物；交付物全部留在仓库内。文档写给用户看的部分
> 只能是“双击哪个文件、等什么提示、失败发什么日志”。参考 `tools/client_mcp/bootstrap.py`。

`bootstrap.py` 必须做到：

1. 检查 Python ≥ 3.10；不满足时打印下载地址，并提醒安装时勾选 “Add python.exe to PATH”。
2. 按 `(导入名, pip 名)` 列表检查依赖；缺失则用 `sys.executable -m pip install` 自动安装，官方源失败后依次尝试清华、阿里云镜像；装完复检。
3. 支持 `--check-only`：只自检不开界面，退出码 0 / 2。Linux 沙箱、CI 都用它。
4. 把 `src/` 加进 `sys.path` 再 import 应用，不要求用户 `pip install` 本包。
5. 任何异常写入同目录 `启动日志.txt`（带时间、Python 版本、完整 traceback），终端里停住等回车；用户只需把日志发回来。
6. 透传命令行参数（如要打开的文件）给应用的 `main(argv)`。

`启动<工具名>.bat` 固定骨架：`@echo off` → `chcp 65001 >nul` → `cd /d "%~dp0"` → 优先 `py -3`、其次 `python`、都没有时提示安装并 `pause` → `bootstrap.py %*` → 失败时 `pause`。文件保存为 **CRLF**（仓库 `.gitattributes` 已对 `*.bat` 强制），内容**只含 ASCII**——中文提示放在 `bootstrap.py` 里打印，因为 cmd 按控制台代码页解析 bat 文件本身，不可靠。

**参考实现**：[`resource_editor/bootstrap.py`](../resource_editor/bootstrap.py) + [`resource_editor/启动编辑器.bat`](../resource_editor/启动编辑器.bat)。新工具复制过去改名字、依赖表和入口即可。

## 4. 一键构建 EXE：`build_exe.bat` + `<tool>.spec`

- **PyInstaller 不能跨平台**：EXE 只能在 Windows 上构建。Linux 侧负责把 spec 和脚本写对并做干跑（§5.1），Windows 侧（用户或 Windows 机器上的 Agent）负责双击 `build_exe.bat` 并把结果写回 STATUS。
- `build_exe.bat`（CRLF、ASCII）步骤固定：检查 Python → 创建 / 复用 `.venv` → `pip install -r requirements-dev.txt` → 跑 `unittest`（失败即停）→ `pyinstaller --noconfirm --clean <tool>.spec` → 打印 `dist\<Name>\<Name>.exe` 路径 → `pause`。用环境变量（如 `set <TOOL>_ONEFILE=1`）切换单文件版。
- spec 要求：入口是**不做 pip 安装**的轻量脚本（`run.py` 或 `src/<package>/__main__.py`，不是 `bootstrap.py`）；GUI 程序 `console=False`，但无参数双击必须直接开窗（map_editor PR #25 的教训）；`datas` 带上程序需要的数据文件；`hiddenimports` 用 `collect_submodules("<package>")`；`excludes` 去掉 tkinter / matplotlib / numpy / pytest 等没用到的大包；用了 `multiprocessing` 必须 `freeze_support()`；onedir 模式 `EXE(...)` 必须 `exclude_binaries=True`（写成 `exclude_binaries=not ONEFILE` 让一份 spec 两用），否则 `COLLECT` 必报 `Resource ... is not a valid file`——map_editor 的旧 spec 就漏了这一项，直到 10-14 干跑才暴露。
- 冻结态资源定位：`Path(getattr(sys, "_MEIPASS", Path(__file__).parent))`；用户配置写到 `%APPDATA%\<Tool>\`（`Path(os.environ.get("APPDATA", Path.home()))`），不写进安装目录或源码目录。
- 版本：「关于」对话框或 `--version` 显示 `__version__`，与 `pyproject.toml` 一致；`dist/`、`build/`、`.venv/` 不入库。
- **参考实现**：[`map_editor/build_exe.bat`](../map_editor/build_exe.bat) + [`map_editor/map_editor.spec`](../map_editor/map_editor.spec)；`resource_editor/`、`ui_editor/` 的同名文件由同一模板生成，只差工具名 / spec 名 / `<TOOL>_ONEFILE` 变量名。注意三者至今**没有在 Windows 上实机构建过**（[STATUS_HISTORY §3.5](archive/STATUS_HISTORY.md#s3-3-5)），谁先在 Windows 上跑通谁把结果写回去。

## 5. Linux 开发 → Windows 交付检查

### 5.1 机械检查（必须跑，结果贴进 PR 描述和 STATUS）

| 步骤 | 命令 | 通过标准 |
|---|---|---|
| 风格 | `ruff check <tool>` | 0 报告 |
| 单元测试 | `(cd <tool> && PYTHONPATH=src QT_QPA_PLATFORM=offscreen python3 -m unittest discover -s tests)` | 全过；缺 libGL 时 GUI 测试记「未执行」 |
| 自检脚本 | `python3 <tool>/bootstrap.py --check-only` | 退出码 0 |
| Windows 兼容静态检查 | `python3 tools/devkit/check_windows_compat.py <tool>`（新工具或大改时加 `--strict`） | 无 ERROR；每条 WARNING 要么修掉，要么在 PR 里逐条说明为什么可以留 |
| spec 干跑（可选，需能 import PySide6） | `(cd <tool> && pyinstaller --noconfirm --clean --distpath /tmp/wc-dist --workpath /tmp/wc-build <tool>.spec)`，再带 `<TOOL>_ONEFILE=1` 跑一次 | 两种模式都构建成功，且数据文件出现在 `dist/<Name>/_internal/<package>/data/`；沙箱缺 libGL / libpython 时的桩库办法见 [STATUS_HISTORY §3.3](archive/STATUS_HISTORY.md#s3-3-3) |

[`tools/devkit/check_windows_compat.py`](../tools/devkit/README.md) 检查：文件名（非法字符、保留名、大小写冲突、长度、符号链接）、`.bat`（CRLF、BOM、`chcp 65001`）、Python 源码（`open`/`read_text` 缺 `encoding`、POSIX 专用 API、硬编码 `/tmp`、字面量 `python3` 启动子进程、非 PySide6 GUI）。规则表：`--list-rules`；行内豁免：行尾加 `# win-ok: 原因`。

### 5.2 人工清单（静态检查覆盖不到的）

- **路径**：`Path` 拼接；不假设大小写敏感（`Interface.fls` 与 `interface.fls` 在 Windows 是同一个文件，在 Linux 不是——读取客户端文件要做大小写无关的查找或明确报错）；路径里有中文和空格（`D:\Lager\夢想世界\`）必须正常；避免相对仓库根超过 200 字符的路径。
- **编码**：所有文本 IO 显式 `encoding`；控制台输出可能被重定向到 GBK 文件，`print` 大量中文时 `sys.stdout.reconfigure(errors="replace")` 或在 bat 里 `set PYTHONUTF8=1`。
- **进程**：子进程用 `[sys.executable, ...]`，不用 `python3`；不用 `os.killpg`/`SIGKILL`/`setsid`，用 `Popen.terminate()`；`subprocess` 不依赖 `shell=True` 的 POSIX 语法。
- **文件锁**：Windows 上打开着的文件不能删除 / 改名——写前关闭句柄；临时文件用 `tempfile.NamedTemporaryFile(delete=False)` 再手动删；原子写用「写临时文件 → `os.replace()`」且目标未被占用。
- **多进程 / 线程**：`multiprocessing` 在 Windows 是 spawn，入口必须有 `if __name__ == "__main__":`，传给子进程的对象要可 pickle。
- **外部程序**：不依赖 `ImageMagick`、`pycdc`、`sh` 等外部可执行文件（map_editor 用 Pillow 替代 ImageMagick 就是为此）；确需依赖时在 `bootstrap.py` 里检测并给出下载提示。
- **bat**：CRLF、ASCII、`%~dp0`、失败 `pause`；不用 `python3` 命令名；用 `where` 探测而不是假设路径。
- **数据位置**：配置写 `%APPDATA%`，缓存写 `%LOCALAPPDATA%`，不往 `~/.config` 或源码目录写。
- **Qt**：原生文件对话框返回的路径先 `Path()`；高 DPI 下界面不截断；关闭主窗口后不残留后台线程导致进程不退出。

### 5.3 Windows 实机冒烟（用户或 Windows 机器上的 Agent 执行）

1. 解压 / 拉取到含中文、含空格的路径下；
2. 双击 `启动<工具名>.bat`：首次会自动装依赖并出现窗口；关闭后任务管理器里不残留进程；
3. 打开一个真实文件（`data/*.fls`、`map/*.map`、`.dlg`），做一次保存 / 导出到桌面，再把导出结果重新打开；
4. 双击 `build_exe.bat`：构建成功；双击 `dist\<Name>\<Name>.exe` 重复第 3 步；
5. 把 Windows 版本、Python 版本、步骤结果与截图 / `启动日志.txt` 记到 `docs/STATUS.md` §2。

### 5.4 如实表述

PR 描述与 STATUS 里分三栏写：**Linux 已做 / Windows 待验 / 已知差异**。没有在 Windows 实机跑过就写「未在 Windows 实机验证」，不要写「可用」「已交付」；测试替身通过不等于原生通过（项目红线，见 AGENTS §0）。

## 6. PR 自检清单（复制到 PR 描述里逐项打勾）

```
- [ ] ruff check <tool>：0 报告
- [ ] 单元测试：core 全过；GUI 测试（offscreen）通过 / 因缺 libGL 未执行
- [ ] python3 <tool>/bootstrap.py --check-only：退出码 0
- [ ] python3 tools/devkit/check_windows_compat.py <tool>：0 ERROR；WARNING 已逐条处理或说明
- [ ] 启动*.bat / build_exe.bat：CRLF、ASCII，流程与 §3/§4 一致
- [ ] <tool>.spec 干跑成功 / 本次未做（原因）
- [ ] README 与 pyproject 版本一致；STATUS §2 已更新本次实测
- [ ] Windows 实机：已验（环境 + 结果）/ 待用户验（已列出 §5.3 清单）
```

## 7. 现有工具怎么办

不要求一次性把老工具全部改造；差距清单与补齐顺序维护在 [`STATUS_HISTORY §3.5`](archive/STATUS_HISTORY.md#s3-3-5)。原则：

- **碰到就补齐**：改某个工具时，顺手让它满足本约定（至少：ruff 0 报告 + `bootstrap.py` + Windows 静态检查无 ERROR）。
- **新代码零例外**：新工具、新模块一律按本约定；在老文件里加新函数也按 PEP 8。
- **tkinter 工具不再维护**：`tools/data_browser/desktop_app.py`、`work/.../tools/map_gui.py` 保留为历史工具，有需求时用 PySide6 重写而不是修补。
