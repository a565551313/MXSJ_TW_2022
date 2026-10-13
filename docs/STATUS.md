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
| 最近 PR | #28（文档整理）已合入 `arena/23e52686`；#1–#27 全部关闭/合并 |
| 合并授权 | 无。合入 master / 发布生产需要用户当轮明确授权 |

## 2. 组件状态与实测

| 组件 | 版本/阶段 | 状态 | 本次实测 |
|---|---|---|---|
| 逆向研究（`notes/`, `work/`） | 结案：双 VM opcode 表、0SLF 目录/路径哈希、`.dlg` 2,706/2,901、协议号表 412 条、帧续读 2 字节 | 稳定；未决项见 AGENTS §7 | 锁定输入 SHA 匹配 |
| 注册 UI 补丁（`tools/client_patches/`） | v3.3 控件修正候选 | **等待用户 Windows 原生验收**（自 10-12 起无反馈） | 90/90 通过 |
| 只读复核链（catalog / API / web） | H/I/J 已收尾 | 可运行，只读 | catalog 34/34；review_api 27/27；验收套件 68 通过 + 2 跳过（需 uvicorn 在 PATH 上）；网页未装 node_modules 未跑 |
| 地图编辑器 | 一期 + PR #27 修复 | GIRB 300/429 扇区仍解不出（明确失败）；Windows EXE 未实机冒烟 | **82/82** 通过（README 旧计数 68 已过期） |
| 资源编辑器 | 0.3.3 | 可用；写回目录不变量 P0 已修 | 核心 29 通过 + 2 跳过；`test_batch_ops`/`test_gui_smoke` 需 libGL，未执行 |
| UI 编辑器 | 0.5.2（三期 M3.2） | 可用；M3.3 九宫格未做 | 核心 37 通过 + 1 跳过（语料库不在沙箱）；`test_gui`/`test_painters`/`test_pack_build`/`test_assets` 需 libGL，未执行 |
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
- 沙箱无 `libGL.so.1`，所有 Qt GUI 测试无法执行；需要在有桌面的机器上跑一次完整 `unittest discover`。
- 复核验收套件原样执行文档中的 `python3 …` 启动命令，依赖必须装在该 `python3` 可见的位置。

### 3.4 仓库体积与许可
- 526 MB 跟踪文件中约 400 MB 是客户端二进制、CEF 运行时（根目录与 `exe/` 各一份）、OGG 音频、商业字体、游戏日志；`.git` 332 MB。
- 根目录没有 LICENSE；客户端材料的再分发权利不明。
- **用户决定本轮不动二进制**（本地 checkout 可能就是游戏目录，`git rm` 后 pull 会删文件）。后续若清理：先确认本地已备份，再只移除工具不依赖的部分（`music*/`、CEF、安装/更新器、未被证据引用的日志），保留 `mx.exe`/`mxmain.dll`/`exe/python27*.dll`/`data/*.fls`/`map/*.map`/`Fonts/`。

### 3.5 Python 工具约定（2026-10-14）与现状的差距
约定全文：[`PYTHON_TOOL_CONVENTIONS.md`](PYTHON_TOOL_CONVENTIONS.md)。下表为本次实测：ruff 0.17（各目录自己的 `pyproject.toml`，没有的用根 `ruff.toml`）；wincompat = `python3 tools/devkit/check_windows_compat.py <目录>`（E = ERROR，W = WARNING）。

| 工具 | ruff 报告 | GUI | 自检启动脚本 | 一键 EXE | wincompat | Windows 实机 |
|---|---|---|---|---|---|---|
| `resource_editor/` 0.3.3 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ❌ 无 | 0 | 未验 |
| `ui_editor/` 0.5.2 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ❌ 无 | 1 W（`tests/test_codec.py` 硬编码 `/home/user/interface_dlg_decoded`） | 未验 |
| `map_editor/` | 74（E501 43、I001 11、UP037 7、F401 4、B905 3、E741 2、F821 1[字符串标注]、B017 1） | PySide6（可选） | ❌ 无：`runGUI.py` 缺 Qt 直接 ImportError，也没有 bat | ⚠️ `build.bat` + spec 有，但**从未在 Windows 构建** | 2 W（测试 `write_text` 无 encoding） | 未验（PR #25 遗留） |
| `tools/client_patches/` | 328（E501 268） | CLI | — | — | 7 W + 2 INFO（Py 2.5 片段按设计不可解析） | v3.3 待验收 |
| `tools/data_browser/desktop_app.py` | 37 | **tkinter** | ❌ | ❌ | 3 E（CONV001） | — |
| `work/.../tools/map_gui.py` | （目录合计 585） | **tkinter** | ❌ | ❌ | 2 E（CONV001）+ 3 W | 历史工具 |
| `tools/data-parser/`、`tools/dis_v43/`、`tools/decompiler/*.py` | 82 / 28 / 239 | CLI | — | — | 0 / 0 / 3 W | — |
| `server/`（src / tools / tests / apps） | 124 / 1423 / 291 / 54 | — | — | — | 10 E（验收脚本 `os.killpg`/`SIGKILL`，Linux 侧按设计）+ 93 W | 不交付 Windows |
| `mock_server.py` | 228 | — | — | — | 1 W | — |

本轮已修的「Windows 必坏」项：`work/.../co_code_analysis/bytecode_58_<module>.bin` 改名为 `bytecode_58_module.bin`（`<` `>` 是 Windows 非法文件名字符，Windows 上 checkout 该文件会报 `invalid path`；`crack_table_b.py` 的引用同步改）；新增 `.gitattributes` 强制 `*.bat`/`*.cmd` CRLF 并重归一化 5 个 bat；`map_editor/build.bat` 补 `chcp 65001`。
补齐顺序建议：① `map_editor` 加 `bootstrap.py` + 启动 bat，修 ruff 74 条；② `resource_editor` / `ui_editor` 各加 `build_exe.bat` + spec；③ 三个编辑器在 Windows 实机按 CONVENTIONS §5.3 冒烟并回填 §2；④ 两个 tkinter 工具只保留不改，有需求时用 PySide6 重写。

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
4. 在有桌面的机器上跑一遍三个编辑器的完整测试并把结果记到本文。
4a. 按 §3.5 的顺序把三个编辑器补齐到工具约定（`map_editor` bootstrap + ruff；两个编辑器的 `build_exe.bat` + spec），然后在 Windows 实机跑 CONVENTIONS §5.3 冒烟。
5. 二进制清理（需授权）与 LICENSE/权利说明。
6. 服务端第一条真实链路（网关 + 账号 + 区服 + PostgreSQL），按 `server/docs/GATEWAY.md`、`INTERFACES.md` 开工；在此之前不要再堆设计文档。

## 6. 最近变更

| 日期 | 变更 |
|---|---|
| 2026-10-14 | 工具开发约定：新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（PEP 8 + 模块化、GUI 一律 PySide6、必须有 `bootstrap.py` 自检启动与 `build_exe.bat`、Linux→Windows 交付检查）与 AGENTS §5 摘要；新增 `tools/devkit/check_windows_compat.py`（Windows 兼容静态检查，29 测试）、根 `ruff.toml`、`.editorconfig`、`.gitattributes`（`*.bat` CRLF）；`map_editor/pyproject.toml` 补 ruff 配置，两个编辑器的 ruff 规则加 `W`；修 Windows 必坏项（`bytecode_58_<module>.bin` 改名、bat CRLF、`build.bat` 加 `chcp 65001`）。差距清单见 §3.5。 |
| 2026-10-14 | 文档整理：新增 `AGENTS.md`、`docs/STATUS.md`、`docs/archive/`（归档 14 个过期快照：根目录 `AGENT_HANDOFF.md`、`work/` 下 10-09/10-10 交接与分派文档、地图编辑器交接报告、`CLIENT_DATA_AGENT_HANDOFF.md`、4 份 route-scope 残留）；v3.3 事实表抽成 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md`；刷新 `README.md`（补两个编辑器、修正测试计数、状态移到本文）、`server/README.md`、`tools/client_patches/README.md`、`work/.../INDEX.md`。未改任何代码、测试、数据与二进制。 |
| 2026-10-13 | 资源编辑器 0.3.3 / UI 编辑器 0.5.2：写回目录不变量 P0 修复；decoder 分段参数修复（引发 §3.1）。 |
| 2026-10-12 | PR #26/#27 合入 master：复核链、注册 UI v3.3、网关设计、地图编辑器及其修复。 |

## 7. 如何更新本文

每轮结束：改快照日期 → 更新 §1 分支/基线 → 用**实际跑过**的结果更新 §2（没跑就写“未执行”）→ 增删 §3/§4 → 调整 §5 → 在 §6 追加一行。不要删历史行；超过一屏时把旧行搬到 `archive/`。
