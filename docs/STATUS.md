# 项目当前状态（STATUS）

> **快照日期：2026-10-14**（Asia/Shanghai）。本文是唯一的“当前状态”文件：每轮工作结束时更新本文，不要再新建交接文档。
> 长期规则见 [`AGENTS.md`](../AGENTS.md)；项目总览见 [`README.md`](../README.md)；历史快照在 [`archive/`](archive/README.md)。
> 表中“实测”均为本次在 Linux 沙箱（Python 3.11.2、Node 22、无 `libGL.so.1`）实际运行的结果，不是转抄。

## 1. 分支与集成

| 项 | 值 |
|---|---|
| 工作分支 | `arena/945a583b-mxsj-tw-2022`（本会话） |
| 基线 | `24d22dc`（`arena/23e52686-mxsj-tw-2022` 合入 PR #28 后的顶端；该分支领先 `master` 23 个提交：资源编辑器 0.1→0.3.3、UI 编辑器 0.1→0.5.2、0SLF 路径哈希/`.dlg` 逆向、decoder 分段参数修复、10-14 文档整理） |
| `master` | `b04f999`（PR #27 合并，2026-10-12）。两个编辑器、10-13 逆向成果与 10-14 文档整理**尚未合入 master** |
| 最近 PR | #29（工具约定 + devkit）、#28（文档整理）已合入 `arena/23e52686`；本轮（三个编辑器补齐约定 ①②）待开 PR；#1–#27 全部关闭/合并 |
| 合并授权 | 无。合入 master / 发布生产需要用户当轮明确授权 |

## 2. 组件状态与实测

| 组件 | 版本/阶段 | 状态 | 本次实测 |
|---|---|---|---|
| 逆向研究（`notes/`, `work/`） | 结案：双 VM opcode 表、0SLF 目录/路径哈希、`.dlg` 2,706/2,901、协议号表 412 条、帧续读 2 字节 | 稳定；未决项见 AGENTS §7 | 锁定输入 SHA 匹配 |
| 注册 UI 补丁（`tools/client_patches/`） | v3.3 控件修正候选 | **等待用户 Windows 原生验收**（自 10-12 起无反馈） | 90/90 通过 |
| 只读复核链（catalog / API / web） | H/I/J 已收尾 | 可运行，只读 | catalog 34/34；review_api 27/27；验收套件 68 通过 + 2 跳过（需 uvicorn 在 PATH 上）；网页未装 node_modules 未跑 |
| 地图编辑器 | 一期 + PR #27 修复 + 10-14 补齐约定（`bootstrap.py`、`启动地图编辑器.bat`、`build_exe.bat`、ruff 0） | GIRB 300/429 扇区仍解不出（明确失败）；Windows EXE 未实机构建/冒烟 | **88/88** 通过（含 6 条 bootstrap 测试；GUI 冒烟在沙箱用 Qt offscreen + 桩 libGL 跑过）；ruff 0；wincompat 0/0 |
| 资源编辑器 | 0.3.3 + 10-14 补 `build_exe.bat` / spec / `run.py` / requirements | 写回目录不变量 P0 已修；Windows 实机与 EXE 未验 | **37/37** 通过（10-14 起沙箱以 Qt offscreen + 桩 libGL 跑齐 GUI 组）；spec 干跑 onedir/onefile 通过 |
| UI 编辑器 | 0.5.3 + 10-14 补 `build_exe.bat` / spec / `run.py` / requirements | M3.3 九宫格未做；EXE 未验（0.5.3 已由用户在真实 Windows 实机跑通加图存包主流程） | **94 通过 + 1 跳过**（含 0.5.3 两条原生回归：缩放回调已删标签不崩、挂账图无引用须明示未写入）；ruff 0；wincompat 0/0 |
| 游戏服务端（`mxsj_server`） | 契约 v0.1 + 设计文档 | **无运行代码**；账号/网关/数据库/地图/战斗均未开始 | 架构测试 150 跑，**1 FAIL + 1 ERROR**（见 §3.1） |
| `mock_server.py` | 历史 Mock，协议号已按客户端修正 | 从未与真机联调；PR #25 顺带改的帧长度 3→2 未单独评审 | 未运行 |
| 文档 | 10-14 整理：AGENTS.md / STATUS.md / 归档目录；README 已刷新；新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（工具开发约定） | — | 仓库内相对链接全部可解析（脚本校验） |
| 开发工具箱（`tools/devkit/`） | 0.1.0：`check_windows_compat.py` | 新增；全仓库扫描 1.3 s | **29/29** 通过；`ruff check tools/devkit` 0 报告；工具箱通过自己的规则 |

## 3. 红灯与已知问题

### 3.1 架构测试红：Agent E 证据的输入指纹过期（当前分支，真实回归）
- 现象：`server/tests/architecture` 中 `test_agent_e_map_npc.InputPinningTests.test_evidence_file_matches_regeneration` FAIL、`test_review_csv_export.RealBatchTests` setUpClass ERROR；`python3 server/tools/export_review_csv.py --check` 报 `E evidence changed; review required`。
- 根因：提交 `45d5590`（10-13，“修复 script.fls 残余条目的分段参数”）修改了 `tools/decompiler/batch_decompile.py`（+492/−10），而 `server/docs/csv_checks/agent_e_reproduction.json` 的 `inputs.shared_decoder.sha256` 钉的是旧值 `7490dbab…`，现值 `242543f8…`。
- 已核实：重新生成后与已提交证据**逐字段比对只有这一个哈希不同**，地图/NPC 分析结果零差异。
- 处置：**本轮未修**（用户选择单独处理）。修法：`python3 server/tools/map_npc_reproduction.py --out server/docs/csv_checks/agent_e_reproduction.json`，提交信息写明“仅 decoder 指纹变化，分析零 diff”，并附 diff 证据。

### 3.2 逆向结论内部矛盾：目录查找是线性还是有序
- `notes/fls_path_hash_and_dlg.md` §2 写明引擎对 0SLF 目录**线性扫描**（`0x48ECF0`）；资源/UI 编辑器 0.3.3/0.5.2 的 P0 修复依据是“引擎按有序目录寻址（含二分模拟），新条目追加到尾且 `r1=0` 会查不到”。
- 两者不能同时成立。修复同时改了排序与 `r1≠0`，真正起作用的可能只是 `r1≠0`（0 疑为哨兵）。需用反汇编回头判定，再统一文档与 docstring。

### 3.3 环境限制（不是缺陷）
- 沙箱无 `libGL.so.1` / `libEGL` / `libxkbcommon` / `libdbus-1`，也不能 `apt`。10-14 起的变通：用 gcc 生成只导出空符号的桩库放到 `LD_LIBRARY_PATH`（`libdbus-1.so.3` 需版本节点 `LIBDBUS_1_3`，`libxkbcommon.so.0` 需 `V_0.5.0`），再加 `QT_QPA_PLATFORM=offscreen`，PySide6 6.12 即可离屏开窗，三个编辑器的 GUI 测试组都能跑。桩库只在沙箱，**不入库**；它能证明「代码不会在导入/建窗时崩」，不能替代 Windows 实机。
- 沙箱 Python 没有 `libpython3.11.so`（Debian 未装 `libpython3.11`），PyInstaller 分析会直接退出；同样用一个空桩 `libpython3.11.so.1.0` 绕过即可完成 spec 干跑（产物不可运行，只验证 hiddenimports/datas）。GitHub release 资产域不可达，装不了 python-build-standalone。
- 复核验收套件原样执行文档中的 `python3 …` 启动命令，依赖必须装在该 `python3` 可见的位置。

### 3.4 仓库体积与许可
- 526 MB 跟踪文件中约 400 MB 是客户端二进制、CEF 运行时（根目录与 `exe/` 各一份）、OGG 音频、商业字体、游戏日志；`.git` 332 MB。
- 根目录没有 LICENSE；客户端材料的再分发权利不明。
- **用户决定本轮不动二进制**（本地 checkout 可能就是游戏目录，`git rm` 后 pull 会删文件）。后续若清理：先确认本地已备份，再只移除工具不依赖的部分（`music*/`、CEF、安装/更新器、未被证据引用的日志），保留 `mx.exe`/`mxmain.dll`/`exe/python27*.dll`/`data/*.fls`/`map/*.map`/`Fonts/`。

### 3.5 Python 工具约定（2026-10-14）与现状的差距
约定全文：[`PYTHON_TOOL_CONVENTIONS.md`](PYTHON_TOOL_CONVENTIONS.md)。下表为本次实测：ruff 0.17（各目录自己的 `pyproject.toml`，没有的用根 `ruff.toml`）；wincompat = `python3 tools/devkit/check_windows_compat.py <目录>`（E = ERROR，W = WARNING）。

| 工具 | ruff 报告 | GUI | 自检启动脚本 | 一键 EXE | wincompat | Windows 实机 |
|---|---|---|---|---|---|---|
| `resource_editor/` 0.3.3 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ✅ `build_exe.bat` + `resource_editor.spec` + `run.py`（10-14；Linux 干跑通过） | 0 | 未验（bat / EXE 都没在 Windows 跑过） |
| `ui_editor/` 0.5.2 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ✅ `build_exe.bat` + `ui_editor.spec` + `run.py`（10-14；Linux 干跑通过） | 0（沙箱语料库兜底路径加 `# win-ok`，缺目录只会 skipTest） | 未验（bat / EXE 都没在 Windows 跑过） |
| `map_editor/` 0.1.0 | **0**（10-14 清掉 74 条；只做定点修改，未整体 `ruff format`） | PySide6（可选） | ✅ `bootstrap.py` + `启动地图编辑器.bat`（10-14；强制 `--gui`，其余参数转发） | ✅ `build_exe.bat`（原 `build.bat`，改名并重写为纯 ASCII）+ spec（10-14 修 onedir 缺 `exclude_binaries` 的硬错误；Linux 干跑通过） | 0 | 未验（PR #25 遗留；bat / EXE 都没在 Windows 跑过） |
| `tools/client_patches/` | 328（E501 268） | CLI | — | — | 7 W + 2 INFO（Py 2.5 片段按设计不可解析） | v3.3 待验收 |
| `tools/data_browser/desktop_app.py` | 37 | **tkinter** | ❌ | ❌ | 3 E（CONV001） | — |
| `work/.../tools/map_gui.py` | （目录合计 585） | **tkinter** | ❌ | ❌ | 2 E（CONV001）+ 3 W | 历史工具 |
| `tools/data-parser/`、`tools/dis_v43/`、`tools/decompiler/*.py` | 82 / 28 / 239 | CLI | — | — | 0 / 0 / 3 W | — |
| `server/`（src / tools / tests / apps） | 124 / 1423 / 291 / 54 | — | — | — | 10 E（验收脚本 `os.killpg`/`SIGKILL`，Linux 侧按设计）+ 93 W | 不交付 Windows |
| `mock_server.py` | 228 | — | — | — | 1 W | — |

本轮已修的「Windows 必坏」项：`work/.../co_code_analysis/bytecode_58_<module>.bin` 改名为 `bytecode_58_module.bin`（`<` `>` 是 Windows 非法文件名字符，Windows 上 checkout 该文件会报 `invalid path`；`crack_table_b.py` 的引用同步改）；新增 `.gitattributes` 强制 `*.bat`/`*.cmd` CRLF 并重归一化 5 个 bat；`map_editor/build.bat` 补 `chcp 65001`。
补齐顺序：① `map_editor` 加 `bootstrap.py` + 启动 bat，修 ruff 74 条 —— **10-14 已做**；② `resource_editor` / `ui_editor` 各加 `build_exe.bat` + spec —— **10-14 已做**（三个 `build_exe.bat` 同一模板：`py -3`/`python` 探测 → `.venv` → `requirements-dev.txt` → `unittest`（`PYTHONPATH=src`、`QT_QPA_PLATFORM=offscreen`）→ `python -m PyInstaller --noconfirm --clean <tool>.spec`）；③ 三个编辑器在 Windows 实机按 CONVENTIONS §5.3 冒烟并回填 §2 —— **待用户**：双击 3 个启动 bat、3 个 `build_exe.bat`、3 个 EXE，任一失败把 `启动日志.txt` / 控制台输出贴回来；④ 两个 tkinter 工具只保留不改，有需求时用 PySide6 重写。

## 4. 等待外部输入

| 事项 | 等谁 | 阻塞什么 |
|---|---|---|
| 注册 UI v3.3 原生复测（5 项控件问题 + 光标闪烁） | 用户在 Windows 测试副本上验证，清单见 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md` §7 | 客户端里程碑收口；之后才开始服务端第一条真实链路 |
| 两个编辑器在真实 Windows + 真实 `interface.fls` 上的实机验证（新图写包后进游戏能否显示） | 用户 | 编辑器“可用”声明 |
| 是否合入 master、是否清理二进制 | 用户授权 | — |

## 5. 下一步（优先级）

1. 修 §3.1（单独一个小提交），让架构套件与 `--check` 回绿。
2. 收到 v3.3 反馈后：先按原档接口复现，再补测试，再出下一候选；不盲发。
3. 判定 §3.2，统一 `notes/` 与编辑器文档。
4. 三个编辑器在 Windows 实机跑 CONVENTIONS §5.3 冒烟（启动 bat → `build_exe.bat` → 双击 EXE），把结果回填 §2 / §3.5；沙箱侧 10-14 已把完整测试（含 GUI 组）跑绿，不再需要「有桌面的机器跑测试」这一步。
5. 二进制清理（需授权）与 LICENSE/权利说明。
6. 服务端第一条真实链路（网关 + 账号 + 区服 + PostgreSQL），按 `server/docs/GATEWAY.md`、`INTERFACES.md` 开工；在此之前不要再堆设计文档。

## 6. 最近变更

| 日期 | 变更 |
|---|---|
| 2026-10-14 | 三个编辑器补齐工具约定 ①②：`map_editor` 新增 `bootstrap.py` + `启动地图编辑器.bat`、`tests/test_bootstrap.py`，ruff 74→0（定点改：E501 换行、`itertools.pairwise`、`zip(strict=True)`、`Iterator` 真实导入、`assertRaises(FlsError)` 等），`build.bat` 改名 `build_exe.bat` 并重写为纯 ASCII，spec 补 `exclude_binaries`，修 `test_cli_and_isolation` 读到开发者真实配置的隔离漏洞；`resource_editor` / `ui_editor` 各加 `build_exe.bat`、`<tool>.spec`、`run.py`、`requirements*.txt`、`.gitignore`（`build/` `dist/` `启动日志.txt`）。沙箱用桩库跑通 Qt offscreen：三套测试 88 / 37 / 92+1 跳过全绿；三份 spec onedir + onefile 干跑通过。**Windows 实机未验**（§3.5 ③）。 |
| 2026-10-14 | UI 编辑器 0.5.3（用户 0.5.0 原生反馈两缺陷）：① 关闭窗口中画布补发缩放信号时 `_on_zoom_changed` 只判 `hasattr`，标签 C++ 对象已删仍 `setText` 抛 `RuntimeError: libshiboken ... already deleted`——改用 `shiboken6.isValid` 把关；② 「图片保存成功却没存进去」：挂账新图仅当被当前布局引用才随包写（设计如此），旧成功弹窗不报实际写入数，未引用被静默漏过、且保存默认生成 `原名_patched.fls` 新包，用户重开原包自然还是原条数——弹窗改明示新包路径、条目总数、实际写入/替换数，有未引用挂账图时点名警告（报告新增 `staged_unreferenced`/`entries_after`）。补两条回归测试，94+1 跳过全绿。用户侧用 0.5.0 时另请注意：务必升级到含 P0 写回修复的版本再对真实包加图。 |
| 2026-10-14 | 工具开发约定：新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（PEP 8 + 模块化、GUI 一律 PySide6、必须有 `bootstrap.py` 自检启动与 `build_exe.bat`、Linux→Windows 交付检查）与 AGENTS §5 摘要；新增 `tools/devkit/check_windows_compat.py`（Windows 兼容静态检查，29 测试）、根 `ruff.toml`、`.editorconfig`、`.gitattributes`（`*.bat` CRLF）；`map_editor/pyproject.toml` 补 ruff 配置，两个编辑器的 ruff 规则加 `W`；修 Windows 必坏项（`bytecode_58_<module>.bin` 改名、bat CRLF、`build.bat` 加 `chcp 65001`）。差距清单见 §3.5。 |
| 2026-10-14 | 文档整理：新增 `AGENTS.md`、`docs/STATUS.md`、`docs/archive/`（归档 14 个过期快照：根目录 `AGENT_HANDOFF.md`、`work/` 下 10-09/10-10 交接与分派文档、地图编辑器交接报告、`CLIENT_DATA_AGENT_HANDOFF.md`、4 份 route-scope 残留）；v3.3 事实表抽成 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md`；刷新 `README.md`（补两个编辑器、修正测试计数、状态移到本文）、`server/README.md`、`tools/client_patches/README.md`、`work/.../INDEX.md`。未改任何代码、测试、数据与二进制。 |
| 2026-10-13 | 资源编辑器 0.3.3 / UI 编辑器 0.5.2：写回目录不变量 P0 修复；decoder 分段参数修复（引发 §3.1）。 |
| 2026-10-12 | PR #26/#27 合入 master：复核链、注册 UI v3.3、网关设计、地图编辑器及其修复。 |

## 7. 如何更新本文

每轮结束：改快照日期 → 更新 §1 分支/基线 → 用**实际跑过**的结果更新 §2（没跑就写“未执行”）→ 增删 §3/§4 → 调整 §5 → 在 §6 追加一行。不要删历史行；超过一屏时把旧行搬到 `archive/`。
