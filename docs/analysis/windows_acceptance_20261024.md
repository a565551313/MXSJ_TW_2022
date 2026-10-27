# Windows 验收报告（2026-10-24）

> 范围：在本机 Windows 宿主上执行项目 ROADMAP **阶段 B「原生交付验证」** 的工程层验收
> （静态门禁、各组件 Windows 原生测试、bootstrap 自检、EXE 打包与冒烟）。
> **产品层未验**：真实桌面 GUI 观感、游戏客户端联调、独立原生依据校验、公网部署（见 §7）。
> 判定口径：**跳过不算通过**；所有数字均为本轮实跑，不与历史记录混算。

## 0. 结论摘要

- **可交付面基本健康**：9 个编辑器/工具目录 wincompat 0/0/0；catalog 34、review_api 27、
  web_server 63、native_channel 18 全绿；前端 `tsc` 0 退出、vitest 112 过 / 9 跳（与 STATUS 记录一致）；
  三个编辑器 `bootstrap.py --check-only` 全部 exit 0；PyInstaller 3/3 构建成功，
  MapEditor.exe `--scan` exit 0，两个 GUI EXE offscreen 下事件循环正常启动（exit 124 = 10s 超时后仍在运行）。
- **新发现 3 类真问题**（按严重度）：
  1. **`vendor_core` 行尾敏感比对在 Windows autocrlf 检出下自毁**（§5.1）——原始树上
     `--check` 必报 9 份副本漂移；devkit 测试首跑必红 11 项并**把工作树写脏**；
     Windows 上「git 干净」与「vendor 一致」不可兼得。影响每一位 Windows 开发者。
  2. **CRLF 字节钉伪影族**（§5.2）——`script_editor/licenses/recovery/GPL-3.0.txt` 与
     `server/docs/catalog/script_entries.jsonl` 被 autocrlf 转换后打破代码内 SHA256 钉，
     直接挂掉 script_editor 3 个测试与 script_manual 校验。项目已为 `runtimes/**` 修过同一根因一轮，
     本轮是漏网实例。
  3. **平台无关的真实漂移**（§5.3）——script_editor 包哈希钉、ruff 1 error。
     （architecture 证据钉的初判已**推翻**：逐字节复测证明其同为 CRLF 伪影族成员，
     修正记录见 §10.2；ruff 1 error 同日已修。）
- **Windows 特化适配问题**（§6）：WinError 32 句柄锁（local_server 2 / ui_editor 12 / resource_editor 9）、
  map_editor 路径分隔符、devkit WIN102 夹具、TransportTests 进程语义、review_browser_acceptance 的
  `python3`/`killpg`、mock_server 硬编码 `/tmp`。
- **修复进展（同日追加，详见 §10）**：P0-1 / P0-2 两项根因已修复并复验——架构套件 **161 全绿**、
  script_manual validate 通过（5135/5135）、catalog / review_api 全绿、script_editor 的 3 个 GPL
  许可错误消除；`vendor_core --check` 在 CRLF 检出态通过且不再写脏工作树。
- **工作树现状（验收时快照，修复后已变）**：验收运行（devkit 套件）曾把 9 个 vendored 副本改写为
  混合行尾，`git status` 显示 modified 但 `git diff` 为空（逻辑内容与 HEAD 一致，见 §5.1.6）。
  修复后口径：`git diff` 仅 10 个文件有真实内容差异，其余 M 项为 stat 缓存伪影（§10.4）。

## 1. 环境

| 项 | 值 |
|---|---|
| 宿主 | Windows（WorkBuddy 沙箱宿主，**非用户日常机器**；`python3` 解析差异见 §6.5） |
| Python | 3.13.14（仓库外 venv `C:\Users\Admin\.workbuddy\binaries\python\envs\mxsj`） |
| PySide6 / Pillow | 6.10.3 / 已装（阿里云 PyPI 镜像；pypi.org 被沙箱代理 502 拦截） |
| Node / npm | 22.22.2 / 163 包（npmmirror 镜像；默认 registry 停滞 25 分钟后换镜像，8m20s 装完） |
| git | `core.autocrlf=true`（Windows 版 Git 默认）——本轮多数差异的根因背景 |

环境本身的两个插曲（PyPI 502、npm registry 停滞）是沙箱网络问题，非项目缺陷，仅记录备查。

## 2. 静态门禁

| 门禁 | 结果 | 对照基线 | 判定 |
|---|---|---|---|
| wincompat（map_editor/resource_editor/ui_editor/script_editor/local_server/web_server/tools/devkit/mx_common） | ERROR 0 / WARNING 0 / INFO 0（文件名 685 项、源码 571 个） | 0/0/0 | ✅ |
| wincompat（server/script_manual/tools/native_channel） | ERROR 10 / WARNING 93 / INFO 0（910 项文件名 + 254 个源码） | [STATUS_HISTORY §3.5](../archive/STATUS_HISTORY.md#s3-3-5) 记录「10 E（验收脚本 os.killpg/SIGKILL，Linux 侧按设计）+ 93 W」逐项一致 | ✅ 复现基线 |
| ruff（11 个目录） | **1 error**：`tools/native_channel/bootstrap.py:21` E501（89>88） | STATUS 记录为 0 | ❌ 新发现 |
| py_compile（全仓 893 个 .py） | 1 失败：`tools/decompiler/output` 历史伪代码（CPython 2 语料，按设计不编译） | 已知边界 | ✅ |

wincompat 的 W 类为 WIN302（`read_text` 未指定 encoding，Windows 默认 GBK）与 WIN304
（POSIX 专有 signal API），全部位于 server 侧验收/探针脚本，与既定基线一致。

## 3. 测试套件（Windows 原生 Python 实跑）

| 套件 | 计数 | 结果 | 根因分类 |
|---|---|---|---|
| server/tests/catalog | 34 | ✅ OK | — |
| server/tests/review_api | 27 | ✅ OK | — |
| web_server | 63 | ✅ OK | — |
| tools/native_channel | 18 | ✅ OK（与 STATUS「18 项 stdlib 通过」一致） | — |
| local_server | 68 | 2 错误 | WinError 32：`StoreAndCLITests`（`test_foreign_database_is_not_replaced` 等）setUp 建 `SQLiteStore` 不关连接，tearDown rmtree 删临时目录被句柄锁挡住（§6.1） |
| map_editor | 107 | 1 失败 + 2 跳过 | `test_roundtrip_and_recent_ordering`：配置回读把 `/games/mxsj` 规范化成 `\games\mxsj`（§6.2） |
| ui_editor | 782 | 12 错误 + 1 跳过 | 全部 WinError 32 句柄锁（如 `test_write_pack_copy_verified` tearDown rmtree）（§6.1） |
| resource_editor | 126 | 9 错误 | 同上（如 `test_concurrent_reads_without_pread`）（§6.1） |
| script_editor | 376 | 4 失败 + 3 错误 + 61 跳过 | 4 失败：包哈希钉 + TransportTests ×3（§5.3、§6.4）；3 错误：pycdc GPL 许可 CRLF 伪影（§5.2）；61 跳过：GUI 用例（§6.6） |
| tools/devkit | 44 | 首跑 12 失败 → 复跑 1 失败 | 11 项 vendor_core 行尾自毁（§5.1）+ 1 项 WIN102 夹具（§6.3） |
| server/tests/architecture | 150 | 1 失败 + 1 错误 | 证据钉漂移，平台无关（§5.3） |
| server/tests/review_browser_acceptance | 68 | 1 失败 + 1 错误 | 探针 `python3` 解析到宿主 runtime 缺 uvicorn + `tearDownClass` `os.killpg`（§6.5） |
| script_manual validate | — | 失败：「证据来源摘要变化：server/docs/catalog/script_entries.jsonl」 | CRLF 字节钉伪影（§5.2） |
| tools/client_patches | 58 | 2 错误 | 作废 overlay 的陈旧守卫，按设计失败（既定边界） |
| 前端 review_web | — | `tsc --noEmit` exit 0；vitest **112 过 / 9 跳**（17 文件） | ✅ 与 STATUS 记录一致 |
| mock_server_v2 --self-test | — | 失败：`FileNotFoundError: '\tmp\test_mock_nocheck'` | 硬编码 POSIX `/tmp`（§6.7） |

> 调用口径备注（非项目缺陷）：script_editor 按 AGENTS.md 记载的「仓库根 + `PYTHONPATH=script_editor/src`」
> 跑会多出 4 个 `RuntimeCheckoutTest` 错误（`repair_runtimes` 在组件根、不在 src，不可导入）；
> 改从 `script_editor/` 组件目录跑，该 4 项全部通过。上表为组件目录口径。建议 AGENTS.md 补明。

## 4. bootstrap 自检 + EXE 打包冒烟

| 项 | 结果 |
|---|---|
| map_editor / resource_editor / ui_editor `bootstrap.py --check-only` | 3/3 **EXIT=0**（PySide6/Pillow 就绪） |
| PyInstaller onedir 构建（3 个编辑器 spec） | **3/3 成功**（MapEditor / ResourceEditor / UIEditor） |
| `MapEditor.exe --scan <repo>/map` | **exit 0**：扫描 8 文件 / 8 地图，正常载入内置 `scenes_tw_v2_27_2.json` |
| `ResourceEditor.exe` / `UIEditor.exe`（QT_QPA_PLATFORM=offscreen） | 均 **exit 124**（10s 超时后仍在运行 = Qt 事件循环正常启动，无窗口冒烟上限） |

## 5. 三个专节深挖

### 5.1 `vendor_core` 行尾敏感比对：Windows autocrlf 检出下的自毁（本轮最深发现）

**机制**（`tools/devkit/vendor_core.py`）：

- `load_text()` 用 `newline=""` 按字节读（注释原话「CRLF 副本会被判为漂移」）；
  `store_text()` 恒写 LF；`rendered()` = LF 横幅 + 真源全文。
- Windows 版 Git `core.autocrlf=true` 检出后，**真源与 9 份副本都是纯 CRLF**。
- 于是 `rendered()` = 「LF 横幅 + CRLF 正文」的**混合行尾**，与纯 CRLF 副本逐字节比对 → 全部判漂移。

**实测复现**（本轮做过完整实验，非推断）：

1.  pristine 检出（9 副本纯 CRLF、`git status` 干净）上跑 `vendor_core.py --check`
   → **9 份副本全部报「副本与真源不一致」**，退出码 1。
2.  `python -m unittest discover -s tools/devkit/tests` 首跑 → **12 失败**：
   9 个 `test_banner_and_body_are_verbatim` subTest + `test_repo_copies_match_mx_common`
   + `test_write_is_idempotent` + 1 个 walk_mode（§6.3）。
3.  原因在于 `test_vendor_core.py::test_write_is_idempotent` 对**真实仓库文件**调用
   `vendor_core.write()`（`expected_files()` 用真实 `REPO_ROOT`）：pristine 树上 9 份副本全部
   「不一致」→ 被改写为混合行尾 → mtime 刷新、git 标记 modified（`git diff` 为空，逻辑内容未变）。
4.  改写后复跑 devkit 套件只剩 1 失败（walk_mode）——**首跑 12 → 复跑 1 不是 flaky，是状态跃迁**。
   （验收过程中 12:25:55 的 9 文件被改写事件，即此测试所为；已用 mtime 实验与逐字节比对证实。）
5.  改写后的树：`vendor_core --check` 通过，但 9 个文件在 `git status` 显示 ` M`
   （autocrlf 行尾往返；`git diff` 空，提交它们是 no-op）。

**结论**：Windows autocrlf 检出上，工作树**无法同时满足「git 干净」与「vendor_core 一致」**；
每位 Windows 开发者首次跑 devkit 套件都会必红 11 项并弄脏工作树。Linux 上无此问题（全员 LF）。

**修复建议（一行主修复）**：`load_text()` 改用 universal newlines（`newline=None`），
比对即行尾不敏感；`--write` 随之恒产纯 LF（与提交 blob 一致），git 与 vendor_core 同时干净，
Linux 行为不变。备选：`.gitattributes` 对 `mx_common/**` 与 9 个副本路径声明 `eol=lf`
（影响所有平台检出，需一次性 renormalize，慎重）。
**附带测试设计问题**：`test_write_is_idempotent` 不应对真实文件调用 `write()`
（同文件的 `test_check_detects_and_write_repairs_drift` 已示范了 mock `REPO_ROOT` 的临时目录做法）；
在修好主问题前，它至少应该在 drifted 时跳过写入而不是默默改树。

### 5.2 CRLF 字节钉伪影族（项目已修过一轮，本轮是漏网实例）

`.gitattributes` 现有注释自述：runtimes 的 `BUILD.json` 曾被 autocrlf 打破 SHA256 钉，
故对 `script_editor/runtimes/**` 声明 `-text`。本轮发现同根因的两个新实例：

| 文件 | 磁盘（Windows 检出） | 提交 blob | 钉值 | 后果 |
|---|---|---|---|---|
| `script_editor/licenses/recovery/GPL-3.0.txt` | CRLF，sha `0b383d5a…` | LF，sha `8ceb4b9e…` | `pycdc_engine.py:23` `LICENSE_SHA256 = 8ceb4b9e…` | `EngineIntegrityTests` 3 个错误：「pycdc GPL许可证缺失或摘要不匹配」 |
| `server/docs/catalog/script_entries.jsonl` | CRLF，sha `811bc855…` | LF，sha `d42694bf…` | script_manual 证据摘要 | `mxsj_manual validate --verify-evidence` 失败：「证据来源摘要变化」 |

已验证：磁盘内容归一化为 LF 后哈希与钉值逐位一致（`0b383d5a` → 规范化 → `8ceb4b9e`），
即**内容没错，错在行尾**。修复建议：`.gitattributes` 增加
`script_editor/licenses/** -text` 与 `server/docs/catalog/*.jsonl -text`
（证据/许可类文本一律按字节处理），并顺带排查其他被代码钉 SHA256 的文本文件
（`server/docs/csv_checks/*.json` 等 evidence 文件建议同保护）。

### 5.3 平台无关的真实漂移（Linux 侧同样会红，需人工复核后重生/更新）

> **⚠️ 后续修正（2026-10-24 深挖后，详见 §10.2）**：本条 1（architecture 证据钉）的初判**错误**。
> 逐字节复测证明：`agent_e_reproduction.json` 的单行 sha256 差异与 `RealBatchTests` 红灯
> **全部是 CRLF 伪影**——`tools/decompiler/batch_decompile.py`、manifest 的 9 个 `source_files`
> 与 `server/docs/csv_checks/staging/provenance.json` 被 autocrlf 改写；LF 归一化后与钉值逐位一致，
> 重生工具输出与提交版**逐字节一致**。真实待复核项仅剩本条 2（包哈希钉）与 3（ruff，已修）。

1. **architecture 证据钉**（150 项中 1 失败 + 1 错误）：
   - `test_agent_e_map_npc.InputPinningTests.test_evidence_file_matches_regeneration`：
     重生 `agent_e_reproduction.json` 与提交版差 **1 行**——某条目 sha256
     `a7474223…`（提交）vs `ce482297…`（重生）。
   - `test_review_csv_export.RealBatchTests.setUpClass`：`export_review_csv.py:254`
     `require(map_evidence == …)` → 「E evidence changed; review required」。
   - 根因：`26b7a08`（2026-10-15，「fix(decompiler): 把三处静默失效改成硬失败/明示产物」）
     改了 decoder 行为但未重生证据。重生工具在 Windows 上跑通（entry 4897/1870 均 PASS），
     差异是确定性的单行 sha256，**不是 CRLF 伪影**。
   - 修复：人工复核该条目变化合理后，跑
     `server/tools/map_npc_reproduction.py --out server/docs/csv_checks/agent_e_reproduction.json`
     （及 export_review_csv 对应证据）重生并提交。
2. **script_editor 包哈希钉**：`test_committed_script_package_decodes_with_builtin_catalog`
   期望 `a45e0e49ed33`，现行 `8b6e9266`——包内容已变、钉未更新。需人工确认包变化后更新钉。
3. **ruff 1 error**：`tools/native_channel/bootstrap.py:21` E501（89>88），STATUS 记录为 0，
   属新增欠账（一行拆断即可）。

## 6. Windows 特化适配问题（产品/测试需按 Windows 语义适配）

1. **WinError 32 句柄锁**（local_server 2 + ui_editor 12 + resource_editor 9）：
   测试 tearDown `rmtree` 临时目录时，SQLite 连接 / 打开中的文件句柄未关，
   Windows 下删除被拒（Linux 无此限制）。修法：setUp 建的对象在 `addCleanup`/tearDown 里显式 close。
2. **路径分隔符**（map_editor 1）：`test_roundtrip_and_recent_ordering` 期望 recent_roots 保留
   POSIX 分隔符，实际被 `Path()` 规范成 `\games\mxsj`。需明确产品语义（存原始字符串还是规范化路径）再修测试或产品。
3. **WIN102 夹具**（devkit 1）：`test_walk_mode_scopes_paths_and_counts` 的 `_make_tree` 写
   `other/nul.txt`——Windows 保留设备名，写操作落入 nul 设备、文件并不存在，期望的 WIN102 不出现。
   夹具需按平台调整（如改用 `CON`/`aux.txt` 之外的可行保留名场景，或 Windows 上断言跳过并注明）。
4. **TransportTests ×3**（script_editor 失败主力）：`test_binary_streams_are_not_decoded`、
   `test_cancel_running_process_keeps_partial_output`、`test_timeout_preserves_prefix_and_reaps_process`——
   stdout 前缀在 Windows 进程/管道语义下丢失（`b'prefix' not found in b''`）。需按 Windows 进程模型调整探针或断言。
5. **review_browser_acceptance**（1 失败 + 1 错误）：
   - `test_live_api_conformance`：探针按文档 spawn `python3 review_api_launch.py`；
     `shutil.which('python3')` 能解析到 venv 里的 `python3.exe`，但 `subprocess` 实际落到
     宿主 `versions\3.13.12\python3.exe`（缺 uvicorn）→ 「probe produced no report」。
     **部分属宿主 PATH 伪影**，但探针对 `python3` 的隐式依赖在真实 Windows 上同样脆弱（用户机器未必有 `python3` 这名）。
   - `tearDownClass`：`os.killpg` 在 Windows AttributeError（wincompat 基线里已记录的 Linux 侧设计）。
6. **script_editor 61 跳过**：缺 Qt 运行库的 GUI 用例，offscreen 只能跑非 GUI 部分（既定边界）。
7. **mock_server_v2 --self-test**：硬编码 `/tmp`（Windows 上变 `\tmp\test_mock_nocheck` 相对路径）。
   应改用 `tempfile`。

## 7. 未验项（ROADMAP 阶段 B 产品层，本环境无法覆盖）

1. **真实桌面 GUI 观感**：offscreen 只证明事件循环能起，不等于界面可看可用。
2. **游戏客户端联调**（阶段 B.1/B.2）：打开→导入/修改→保存新包→重开→再次编辑、
   真实客户端加载/交互、候选人工核验→VM 编译→原生转换→独立读回。
3. **独立原生依据校验**（阶段 B.3）：只用同源编码/解码器不算，需第三方依据。
4. **保存失败/取消/错误来源不损坏原包**（阶段 B.4）的真机路径。
5. **用户原位包确认**（阶段 B.5）：原位包 ≠ 完整重编译新包，需用户当面确认。
6. 公网部署、真实机械盘写包耗时。

以上需在用户自己的 Windows 机器（有游戏客户端副本）上按 §5 的「注明版本、输入 SHA、场景、实际结果」逐条执行。

## 8. 待办清单（按优先级）

> 状态图例：✅ 已修复并复验（同日，见 §10）｜⬜ 待办。

**P0（影响所有 Windows 开发者，建议最先修）**
1. ✅ `vendor_core.load_text` 行尾归一化（§5.1 一行修复）；`test_write_is_idempotent` 改为临时树夹具，另增 CRLF 检出回归测试（§10.1）。
2. ✅ `.gitattributes` 补 `-text`：除 `script_editor/licenses/**`、`server/docs/catalog/*.jsonl` 外，实测补齐全族另 6 处（decompiler 输出、`batch_decompile.py`、work `protocol_opcodes.json`、tools 源码、csv_checks staging 与 `*.json`），并重新签出全部受影响文件（§10.1）。

**P1（红灯/欠账）**
3. ⬜ **§6 人工复核项**：`server/tools/map_npc_reproduction.py` 修复后，batch_001 manifest 的该工具哈希行已按 §6 重生（`cc5e9349`→`7fe0d302`，单行 diff 见 §10.3）——提交前需人工复核。architecture 证据本体经复测无需重生（§10.2）。
4. ⬜ script_editor 包哈希钉更新（§5.3-2）：`a45e0e49` vs `8b6e9266`，真实注册不符，与 CRLF 无关，需人工确认包变化后更新。
5. ⬜ WinError 32：local_server / ui_editor / resource_editor 测试补关句柄（§6.1）。
6. ✅ ruff E501 修复（§5.3-3）：`tools/native_channel/bootstrap.py:21` 一行拆断。
7. ✅ AGENTS.md 补 script_editor 测试命令的组件目录口径（§3 备注）。

**P2（Windows 适配）**
8. ⬜ map_editor 配置回读路径分隔符语义（§6.2）。
9. ⬜ TransportTests Windows 进程语义（§6.4）。
10. ⬜ review_browser_acceptance：探针去掉对 `python3` 名字的隐式依赖 + tearDown 的 killpg 适配（§6.5）。
11. ⬜ devkit WIN102 夹具平台化（§6.3）。
12. ⬜ mock_server_v2 `/tmp` → `tempfile`（§6.7）。

**工作树处置**：~~修完 P0-1 后 `git restore` 9 个 vendored 副本~~ 已随 P0-1 完成（归一化后 `--check` 通过、复跑不再写脏）。当前 `git status` 的 706 个 ` M` 中仅 10 个为真实内容差异（§10.4），其余为 stat 缓存伪影（字节与索引一致，提交 no-op）；3 个 untracked（`.workbuddy/`、两份 analysis 文档）待用户决定是否入库。

## 9. 复现命令（备查）

```bash
# 静态门禁
python tools/devkit/check_windows_compat.py map_editor resource_editor ui_editor script_editor \
  local_server web_server tools/devkit mx_common          # 期望 0/0/0
python tools/devkit/vendor_core.py --check                # 修复前 pristine 树上必报 9 漂移（§5.1）；修复后 CRLF 检出态通过

# 测试（均 Windows 原生 Python；ui_editor/resource_editor 需 QT_QPA_PLATFORM=offscreen）
cd local_server   && python -m unittest discover -s tests -t .
cd ui_editor      && PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
cd resource_editor && PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
cd script_editor  && PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
cd map_editor     && QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
python -m unittest discover -s tools/devkit/tests         # 修复前首跑 12 失败（§5.1）；修复后恒 1 失败（WIN102 P2，§6.3）
python -m unittest discover -s server/tests/architecture  # 修复前 1 失败 + 1 错误（§5.3，已修正为 CRLF 伪影）；修复后 161 全绿
PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --repository . --require-full-inventory

# 打包冒烟
cd map_editor && python -m PyInstaller --noconfirm --clean map_editor.spec …
./MapEditor.exe --scan <client-root>                      # 期望 exit 0
QT_QPA_PLATFORM=offscreen timeout 10 ./UIEditor.exe       # 期望 124（事件循环存活）
```

## 10. P0 根因修复与复验（2026-10-24 追加）

### 10.1 修复清单

| # | 修复 | 文件 | 要点 |
|---|---|---|---|
| P0-1a | `load_text` 行尾归一化 | `tools/devkit/vendor_core.py` | `newline=""` 字节读 → universal newlines；`--check` 成功消息刻意保持原文（stdout 被 `documentation_refresh_20261018.json` 钉住） |
| P0-1b | 测试夹具临时树化 + 回归 | `tools/devkit/tests/test_vendor_core.py` | `test_write_is_idempotent` 改临时目录 + mock `REPO_ROOT`，不再写真实仓库；新增 `test_crlf_checkout_is_not_drift` |
| P0-2a | `.gitattributes` 全族 `-text` | `.gitattributes`、`server/docs/csv_checks/.gitattributes` | 新增 `script_editor/licenses/**`、`server/docs/catalog/*.jsonl`、`tools/decompiler/batch_decompile.py`、`tools/decompiler/output/**`、work `protocol_opcodes.json`、`server/tools/*.py`、`tools/*.py`、csv_checks `staging/**` 与 `*.json`（`runtimes/**`、`batch_001/**` 为既有先例） |
| P0-2b | 重新签出受影响文件 | 686 个目标文件 | 单遍脚本：全索引 `git ls-files -s -z` + 进程内 hashlib 复算 blob；CRLF→LF 且逐文件验证归一化后 `sha1` == 索引 blob 哈希才落盘（385 转换 / 301 已是 LF；8 个 `i/crlf` staging CSV 经安全校验正确跳过） |
| 附带 1 | 生成器平台依赖修复 | `server/tools/map_npc_reproduction.py` | `write_staging_csvs` 的 `provenance.json` 改 `write_bytes` 显式 LF（Windows 文本模式把 `\n`→`\r\n`，与提交版 LF 不符） |
| 附带 2 | 文档口径 | `tools/devkit/README.md`、`docs/PYTHON_TOOL_CONVENTIONS.md`、`AGENTS.md`、`tools/native_channel/bootstrap.py` | 「字节比对」→「行尾归一化后比对」；local_server / script_editor 测试命令口径；E501 拆行 |

### 10.2 §5.3-1 初判修正（实测推翻）

初判依据是「重生证据与提交版差 1 行 sha256」且「工具近期被 `26b7a08` 改过」，
形似「改了工具没重生证据」。逐字节复测结论：

| 对象 | 磁盘（autocrlf 后） | LF 归一化后 | 钉值 | 判定 |
|---|---|---|---|---|
| `tools/decompiler/batch_decompile.py` | CRLF | `a7474223…` | `a7474223…`（agent_e_reproduction.json） | CRLF 伪影 |
| manifest 的 9 个 `source_files` | CRLF | 与 manifest 记录逐位一致 | 同上 | CRLF 伪影 |
| `server/docs/csv_checks/staging/provenance.json` | CRLF（810B，`bc58931c`） | LF（759B，`0aa3538c`） | `0aa3538c`（manifest maps_npcs 条目） | CRLF 伪影 |

且重生工具输出与提交版证据**逐字节一致**。即 architecture 证据链**没有任何平台无关的真实漂移**，
初判的「未重生证据」不成立。教训：字节钉报差时，先做行尾归一化复算再下「内容漂移」结论。

### 10.3 manifest 重生（§6 人工复核项）

`server/tools/map_npc_reproduction.py` 被 batch_001 manifest 的 `source_files` 钉住；
修复生成器后按 §6 重生 manifest，逐字段 diff **仅一行**：

```diff
-    "server/tools/map_npc_reproduction.py": "cc5e9349bfb60ca4b2c432505c1f2476939e4c57d829c75cd6cf252a2edd25ca",
+    "server/tools/map_npc_reproduction.py": "7fe0d30260e41af13cd0ba30f30e58d3c196606bdec1dde346878eed5ecbb119",
```

独立佐证：全新导出（`export_review_csv.py --out <tmp>`，22 个文件）与提交版 `diff -r`
亦仅此一行，其余字节级一致（含 8 个 E staging CRLF CSV 与 LF 版 provenance.json）。
**提交信息须说明此行变化**（§6）。

### 10.4 修复后复跑（Windows 原生 Python 实跑）

| 套件 | 结果 | 修复前 |
|---|---|---|
| `server/tests/architecture` | **161 OK** | 1 失败 + 1 错误（RealBatchTests 整类曾因 E evidence setUpClass 错误未能运行） |
| `script_manual validate --verify-evidence --require-full-inventory` | **通过**（5135/5135） | 失败：「证据来源摘要变化」 |
| `server/tests/catalog` | 34 OK | OK（-text 无反向风险） |
| `server/tests/review_api` | 27 OK | OK（同上） |
| `export_review_csv.py --check` | 全过（含 `map_npc_evidence_and_staging_match`） | 失败 |
| `tools/devkit` | 45 测 1 失败 = 既有 P2（WIN102 夹具） | 首跑 12 失败（44 测，+1 为新增回归） |
| `script_editor` | 376 测 4 失败 = 既有（3×TransportTests P2 + 1×包哈希钉 P1）；原 3 个 GPL 许可**错误**已消除 | 4 失败 + 3 错误 |
| `git ls-files --eol` | `i/lf w/crlf` 残留 **0** | 全族受害 |

工作树口径：`git status` 的 706 个 ` M` 中，`git diff` 实测仅 **10 个**文件有真实内容差异
（即 §10.1 所列源码/文档/manifest 编辑）；其余为 stat 缓存伪影——抽验
`server/docs/csv_checks/agent_e_reproduction.json` 的 raw 哈希 `7aaeef89…` 与索引 blob 逐位相同。
本沙箱文件系统 stat 不稳定（§5.1 记载过 9 副本的同类现象），`git update-index --really-refresh`
亦无法确认；提交时以 `git diff` 为准，伪影不会进入提交。

### 10.5 遗留（不在本轮批准范围）

- **P1-4** script_editor 包哈希钉（`a45e0e49` vs `8b6e9266`）：真实注册不符，需人工确认包变化后更新钉。
- **P1-5 / P2**：WinError 32 ×23（local_server 2 / ui_editor 12 / resource_editor 9）、map_editor 路径分隔符、TransportTests ×3、review_browser_acceptance 的 `python3`/`killpg`、devkit WIN102 夹具、mock_server_v2 `/tmp`。
- **提交决策**：10 个真实修改 + 3 个 untracked（`.workbuddy/`、`docs/analysis/` 两份文档）待用户复核后提交；§10.3 的单行 manifest diff 须在提交信息中说明（§6）。

---

*报告生成：2026-10-24，WorkBuddy Agent。所有失败均附根因分类；未执行项在 §7 明确列出，不计入通过。*
