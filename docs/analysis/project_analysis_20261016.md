# 《夢想世界》MXSJ_TW_2022 项目分析报告

> 分析日期：2026-10-16（Asia/Shanghai）｜分析分支：`arena/6256d39f-mxsj-tw-2022`（基线 `5ef8aa2`）
> 方法：**只读**。未修改任何业务代码、原包或证据；所有结论先读源码/文档，再在沙箱实跑对应套件核对。
> 本文是独立分析，不替代 `docs/STATUS.md`（当前状态）与 `AGENTS.md`（长期规则）。凡本项目自述与我实测不一致处，均已单独标注。

---

## 0. 结论速览

| 维度 | 判断 |
|---|---|
| **它是什么** | 围绕《夢想世界》台服 **v2.27.2**（多益網絡）客户端的**逆向研究 + 工具链 + Python 私服重建**工程；仓库根目录本身就是一份游戏安装目录 |
| **最强的地方** | 逆向**实证质量**与**工程诚实度**：双定制 VM opcode 表、0SLF 容器/路径哈希、5 段 XOR、编码乱码根因都钉到了字节与反汇编地址；文档/证据相互约束（SHA 钉输入），"不能验证就写不能验证" |
| **最弱的地方** | 与目标（可长期运行的私服）之间的距离：`mxsj_server` **只有 652 行契约骨架、零运行时**；协议结论**全部来自静态分析、无一次真实抓包** |
| **最容易被低估的资产** | 一套**已在真机验证过的客户端改造能力**：自建 CPython 2.5.6 编译 → 混淆 → 5 段 XOR → 重打包 → 用户实机确认可用的注册界面（原生 `.dlg` + 原生脚本套路） |
| **最容易被高估的资产** | 测试数量与文档体量。测试多为往返/摘要/schema 自证；文档已膨胀为 394 个 `.md`，`STATUS.md` 单文件 240 KB 且是 append-only 日志 |
| **本次实测结论** | 文档记录**没有虚报**：我按 README 命令复跑，架构 161/161、catalog 34/34、review_api 27/27、地图 88、资源 118、手册六闸门全绿（GUI 项按缺依赖如实跳过） |
| **最该先做的三件事** | ① 砍到最小范围打通"注册→选区→登录→进图"第一条真实链路；② 解决 `mx.exe:0x48ECF0` "线性扫描 vs 有序寻址"的矛盾（它决定编辑器写包是否正确）；③ 抽取共享 `core` 库，终结同一逻辑的多份分叉实现 |

---

## 1. 项目身份与真实边界

第 0 层事实（README/AGENTS 自述，我核对属实）：

- 对象是 **TW v2.27.2** 客户端；`mx.exe` / `mxmain.dll` 与 `data/script.fls`、`data/data.fls` 等是锁定逆向输入。
- 目标终局：**Python + asyncio + PostgreSQL** 的可长期维护回合制服务端；本地测试与将来公网同一套业务架构。
- **明确不是**：可直接部署的游戏服务端，也不是已验收的客户端发行版。所有"完成"都要带范围、版本、可追溯证据。
- 核心工作方法：**能展示 ≠ 能运行，能运行 ≠ 正确，测试通过 ≠ 原生验收完成**；事实 / 推断 / 设计三分。

这个自我定位在私有服务器项目里罕见地克制，也是本项目最值得保留的资产。

---

## 2. 项目实际构成：六条工作线

| # | 工作线 | 主要路径 | 规模（我实测） | 成熟度 |
|---|---|---|---|---|
| 1 | **逆向研究** | `notes/`、`work/dream-world-connect-login-map/`、`tools/decompiler/`、`tools/data-parser/` | `tools/decompiler` 主工具 `batch_decompile.py` 约 70 KB；`work/` 98 篇 md；反编译覆盖 4,941/5,002 = 98.78% | **结案级**（有未决项） |
| 2 | **只读数据复核链** | `server/src/mxsj_catalog` + `server/apps/review_api` + `server/apps/review_web` | catalog 983 行；batch_001 = 17 CSV + manifest + validation + JSONL（2.8 MB）；前端 React 19 + Vite 7 | **可运行**（最接近"产品"） |
| 3 | **客户端编辑器四件套** | `map_editor/` `resource_editor/` `ui_editor/` `script_editor/` | src 行数：2,767 / 6,128 / 8,273 / 8,580；均为 PySide6 + `core`（无 Qt）/GUI 分层 + bootstrap + build_exe | **0.4–0.8 版**，功能可用，Windows 实机未验 |
| 4 | **客户端改造** | `tools/registration/`（原生注册 UI 重做）、`tools/client_patches/`（已作废的 v3.3）、启动器皮肤 `.rsrc` 原位写回 | registration 2,981 行 + 自建 CPython 2.5.6 工具链 | **真机验证过**（唯一闭环到用户实机的线） |
| 5 | **脚本开发手册** | `script_manual/` | 5,371 行 + 14 MB 数据；登记 5,135 条、128,382 条函数/类元数据；**说明仅 20 篇** | dev4，内容建设中（0.39% 覆盖） |
| 6 | **游戏服务端** | `server/src/mxsj_server/` + `server/docs/` | **652 行**（21 个模块目录只有 `contracts.py` + 空 `__init__.py`）；设计文档 1,951 行 | **纯设计，无运行代码** |
| — | 历史 Mock | `mock_server.py` | 3,000 行、手写 ~40 个封包构造器 | 从未与真机联调 |

仓库卫生数据（本次实测）：

- 跟踪文件 **2,680 个 / 538.8 MiB**；工作区 898 MB。体积大头：`.dll` 193.5 MiB、`.ogg` 113.9 MiB、`.fls` 49.1 MiB、`.ttf` 31.8 MiB、`.dat` 19.5 MiB、`.exe` 18.9 MiB、`.map` 16.7 MiB。
- 跟踪 `.py` 1,261 个 / 16.8 MiB；**其中 82% 的行数（427,442 行 / 681 文件 / 15 MB）是 `tools/decompiler/output/` 的反编译产物**——即项目自己反复声明"不准确、不可执行、只作线索"的生成物。
- 文档：394 `.md`、345 `.json`、10 `.jsonl`。`docs/STATUS.md` = **240 KB / 1,513 行**，含 **43 个 `### 3.x` 追加式小节**；`server/docs` 单独就有 187 个 md / 9.6 MB。

---

## 3. 硬核技术成果盘点（值得单独说清的部分）

这部分是本项目真正的护城河，全部有字节级/反汇编级证据：

1. **双定制 Python VM 体系**（`notes/opcode_mapping_and_decompilation.md`）
   - VM#1：`script.fls` = 定制 **Py2.5**，`HAVE_ARGUMENT` 从标准 `0x5A` 改成 **`0x5F`**，`PyEval_EvalFrameEx@0x004E7460`，跳转表 `0x004EA308`（98 项）+ 索引表 `0x004EA490`；
   - VM#2：`data.fls` = 定制 **Py2.7**，`co_code` 是**指令/参数双流分离结构**，`PyCodeObject` 头多 4 字节 `co_extra`，`co_lnotab` 语义也改了。
   - 这解释了"以前反汇编器在 `0x5A..0x5E` 失步"的根因，直接推翻旧的"S-Box/参数二次混淆"假设。这类结论属于可以写进论文的发现。
2. **0SLF 容器格式全解**（`notes/fls_path_hash_and_dlg.md`）
   - 16 字节目录记录的闭式变换（`len = ((r1*entry_id + 0x0DF25E) ^ r2)` 等）；包查找 `0x48ECF0`、目录读取 `0x48F170`。
   - **路径哈希寻址**复刻：`entry_id == mx_hash(规范化路径)`；`.dlg` 2,706/2,901 定位解码；原生 XOR 密钥 `((hash + 0x9234AB) & 0xffffffff) ^ 0x937F4912`（`notes/native_dlg_path_cipher.md`，对照真实 `C_sys.LoadFile@0x45D580` 静态链）。
3. **5 段式 XOR + zlib 载荷加密**与重打包流水线（`tools/decompiler/pack_and_encrypt.py`），并用**自建 CPython 2.5.6** 实测"自写源码 → 编译 → 混淆 → 加密 → 重打包 → 解密 → 转译"往返无损。
4. **协议号表** 409 条 opcode（`work/.../artifacts/protocol_table/protocol_opcodes.csv`），含方向、`co_offset`、`load_const_enc`/`store_enc`。
5. **编码乱码根因结案**（`notes/title_and_chat_encoding.md`）：客户端只有 ANSI 版窗口 API（`SetWindowTextW` 计数 0），标题/IM 文字由**系统 ACP** 解释，脚本层零转换，`TITLE_NAME_MX` 本身是 Big5 字节 → 结论是"用 Locale Emulator/cp950 启动"，**不是资源损坏**。这类"用户看到的现象 → 根因 → 处置"闭环正是本项目最擅长的事。
6. **真机验证过的客户端改造**：注册界面按原生规范重做（只改 entry 337/4007，其余 5,000 条逐字节不变），用户实机确认测试无问题；`mxLauncher.exe` 皮肤繁体→简体 `.rsrc` 原位写回。

---

## 4. 本次独立验证：我实际跑了什么

环境：沙箱 Python 3.11.2，自建 venv 安装 `jsonschema/ruff/fastapi/uvicorn/Pillow/httpx`；**缺 PySide6 + libGL**（GUI 组按项目约定记为未执行，不计通过）。

| 套件 | 命令 | 实测结果 | 与项目记录对照 |
|---|---|---|---|
| 服务端架构 | `python3 -m unittest discover -s server/tests/architecture` | **161 OK**（28.6 s） | 与 §3.1 一致（曾红，已修） |
| 复核目录 / API | `… -s server/tests/catalog`、`… -s server/tests/review_api` | **34 / 27 OK** | 一致 |
| 地图编辑器 | `(cd map_editor && python3 -m unittest discover -s tests)` | **88 OK（1 跳过）** | 与"88/88"一致 |
| 资源编辑器 | `(cd resource_editor && PYTHONPATH=src …)` | **118 OK（33 跳过）** | 与"118/118"一致；跳过=无 Qt |
| UI 编辑器 | `(cd ui_editor && PYTHONPATH=src …)` | 147 项中 **22 ERROR + 34 跳过**，全部 `ModuleNotFoundError: PySide6` | 环境缺失，**非缺陷** |
| 手册六闸门 | `python3 script_manual/check_manual.py` | **严格证据+全量目录通过；手册 106 OK(13 跳过)；N1 32 OK；恢复 27 OK；ruff 0；wincompat 0/0/0** | 与 dev4 记录一致 |
| 复核网页 | `npm ci` + `typecheck` + `vitest run` | **typecheck 通过；17 文件 / 112 通过 / 9 跳过** | 一致 |
| 锁定输入 | `sha256sum data/script.fls tools/decompiler/script_fls_keys.json` | `8b6e9266…` / `43bb090d…` | **与 AGENTS §1 完全一致** |

**判断：项目的自述是可复现的，没有夸大。** 这在同类项目里相当少见。缺 GUI 依赖导致的部分跳过，项目也坚持"跳过不算通过"，态度正确。

---

## 5. 工程质量：做对了什么

1. **证据指纹机制**：证据 JSON 把工具源码 SHA 钉死（如 `batch_decompile.py`），改工具就必须重生成证据并逐字段 diff，否则架构测试变红——实测有效（§3.1 的两步修复就很典型：只重生成证据还不够，`manifest.json` 也得刷）。
2. **拒绝假成功**：GIRB 碰撞 300/429 扇区解不出时明确报失败；反编译器缺引擎时**直接拒绝运行**并打印正确配方（我在沙箱里实测触发到了这个行为，退出码与提示都正确）。
3. **边界与安全**：写包永不覆盖原包、生成物写仓库外、不执行/`eval` 恢复出来的游戏模块、不索取真实账号凭据、留了 `docs/ARENA_SANDBOX_RECOVERY.md` 处理"沙箱重置 + HEAD 回退但工作文件还在"的坑。
4. **工具化约定**：`core` 不 import Qt（无桌面可测）、bootstrap 自检启动脚本、一键 EXE、交付前 `check_windows_compat.py`——三个编辑器同构，新人上手成本低。
5. **PR 过程留痕**：47 个 PR 记录 + 每轮报告 MD/JSON 成对，能追溯"谁在什么范围内、凭什么说通过了"。

---

## 6. 问题与风险（按严重度排序）

### P0-1 目标与产出的落差仍是最大风险：服务端零运行时
`server/src/mxsj_server/` 21 个模块目录全部只有 `contracts.py`（共 **652 行**）。账号、网关、数据库、地图、战斗**一行运行代码都没有**。
同时 `mock_server.py`（3,000 行手写封包）"从未与真机联调"，README 也把它排除在正式服务端之外。
→ 现状是"研究/工具很多，游戏不能玩"。这是项目自身早已声明的，但**从时间投入看，六条线里最该收口的那条线进度最慢**。

### P0-2 协议结论缺真实抓包，属系统性不确定
`AGENTS.md §7` 自己写着"仓库里**没有任何真实客户端抓包字节**"。已知具体隐患：
- `GS2C_PROP_CHANGE` 与 `GS2C_NPC_CHAT_EXT` 在客户端表里**同为 152**（客户端自身冲突）；
- 链路帧 `0xFF` 续读长度被从 3 改成 2（PR #25 顺带改），"未单独评审"；
- 所有封包长度/字段都是静态推出来的。
→ 只要没做一次真机抓包对照，任何"协议已还原"的声明都只是概率性的。**这是拿下"第一条真实链路"之前必须解决的输入缺口。**

### P0-3 一个未决矛盾会直接决定编辑器产出是否原生可读
`notes/fls_path_hash_and_dlg.md` 说引擎对 0SLF 目录**线性扫描**（`0x48ECF0`）；而资源/UI 编辑器的 P0 修复依据是"引擎按**有序目录**寻址（含二分模拟），新条目 `r1=0` 查不到"。
两者不能同时成立——而我实测的资源/UI 编辑器**所有写包能力都建立在这个假设上**。判定成本很低（回到 `mx.exe:0x48ECF0` 反汇编即可），收益却极高（决定"新包进游戏能不能被读到"）。

### P1-1 同一逻辑多份分叉实现（技术债的主要来源）
- `mxhash.py` 与 `native_layout.py` 在 `resource_editor` 与 `ui_editor` 中**逐字节相同**（`6c4b2475…` / `e63722d9…`）——两份拷贝；
- `.fls` 容器实现三份互不相同：`resource_editor/.../fls0slf.py`(184 行)、`script_editor/.../archives/fls0slf.py`(124 行)、`ui_editor/core/pack.py`；
- 加上 `tools/data-parser/universal_fls_tool.py`、`tools/decompiler`、`script_manual` 的解析路径，同类解析器至少 **5–6 份**。
→ 修一处不会自动修全部，P0-3 那种"文档口径不一致"正是它的症状。建议抽 `<pkg>_core` 共享库（现在所有工具都是 `src/<pkg>/{core,gui}`，抽公共 core 的成本并不高）。

### P1-2 测试多为"自证"，原生行为仍依赖用户反馈
架构 161 项、catalog 34 项、手册 106 项大部分是往返一致、schema 校验、目录/契约静态检查、证据 SHA 比对——它们**证明的是内部一致性与证据链完整**，不是"进游戏能看见"。
真正的端到端断言（新地图/新布局在客户端可见、注册 UI 在真机可用）目前靠用户实机回报。GUI 组在无桌面环境大量跳过（本次 UI 编辑器 22 ERROR/34 跳过），**跳过计数的绿不等于覆盖率**。

### P1-3 过程成本开始超过产出：文档已成 append-only 日志
`docs/STATUS.md` = 240 KB / 1,513 行 / 43 个 `### 3.x` 小节，每轮追加一节，内容混合"当前状态"与"历史工作日志"；`server/docs` 187 md、全仓 394 md。
项目自己的约定是"当前状态只写在 STATUS，长期规则写 AGENTS"，但 STATUS 已经退化成 changelog。**新 Agent 每轮读 240 KB 才能得到 20 行有用信息。**
配套还有七代理（N1–N7）任务卡、审核角色（A/H/N7）、`review` 模板/激活/SHA 绑定等相当重的协作流程——而它的产出目前是 **20 篇说明 / 5,135 条登记（0.39%）**、16 篇有限通过。流程与产出比例失衡。

### P2-1 生成物入库，与自家红线冲突
`tools/decompiler/output/` 的 681 个反编译 `.py`（427k 行）被跟踪入库，而 `AGENTS.md`/`docs/DECOMPILE_CORPUS.md` 明确写"反编译产物只作线索""全量语料按红线只写在仓库外，沙箱重置就没""不要入库"。
部分语料入库既污染代码行数统计（占跟踪 Python 行数 82%），也让"哪些是我们写的代码"变得难以辨认。

### P2-2 仓库重量与许可
538.8 MiB 跟踪二进制（DLL 193.5 + 音乐 113.9 + FLS 49.1 + 字体 31.8 + …）。克隆、快照、diff 成本都很高；且分发客户端 DLL/音乐/字体存在权利风险（README 自己也把 LICENSE/权利说明列为待办）。
仓库约定是"新增大二进制先问"，但存量没清理，也**缺一个"从零把锁定输入放回原位"的 bootstrap 脚本**——目前新人克隆后哪些文件必须自备、校验值是什么，散落在文档各处。

### P2-3 版本与可追溯性
本地 `master` 顶端是 2026-10-16 11:53 的 **`5ef8aa2 "Add files via upload"`**，浅克隆里只有 1 个提交；47 个 PR 的历史都在 `arena/*` 分支上。也就是说 `master` **无法 bisect/blame**，而正式交付物有多个历史 ZIP 落在 Google Drive，缺一份统一的"版本 → 提交 → 包 SHA → 用途"索引。（我当前会话分支也尚未推到远端。）

### P2-4 范围过宽
六条线各自 60–70%：编辑器要补"控件自动接线/脚本联动"，手册要从 20 篇扩到五个领域，服务端要开工，逆向还有 4 条零源码、2 个 GIRB 扇区、`servicedata` 条款入库等尾巴。**没有一条线有"完成定义（Definition of Done）"**，因此"下一步"永远在增长。

---

## 7. 建议的下一步（按性价比排序）

1. **把"第一条真实链路"当成唯一主线**（最小范围）：网关 + 账号 + 区服/角色 + 进图，先不做战斗/交易/公会。以 `server/docs/INTERFACES.md`、`GATEWAY.md` 为规格，把 `mock_server.py` 降级为"封包字典参考"而不是运行基础。
2. **想办法拿到一次真实抓包**（哪怕只是"连接 → 选区 → 登录"的最小脱敏样本）。这是唯一能把协议从"推测"变成"事实"的输入，优先级高于任何新工具。没有它，链路越做越深，返工风险越大。
3. **判定 P0-3 的矛盾**（`mx.exe:0x48ECF0`），然后统一 `notes/` 与两个编辑器的文档口径。这件事成本低、影响大。
4. **抽共享 core 库**：`fls` 容器、`mxhash`、`native_layout`、`dlg_codec` 各做一份，编辑器以依赖方式引用；加"多实现一致性"回归，防止再次分叉。
5. **文档治理（不动内容，只改结构）**：STATUS.md 只保留"当前状态/红灯/待办"；把 §3.x 历史整块 `git mv` 到 `docs/archive/STATUS_HISTORY.md`（项目已有归档规范）；给每个组件加 5–10 行的 **DoD**（什么条件下可以写"通过"）。
6. **仓库瘦身（需用户授权，涉及既有约定）**：`tools/decompiler/output/` 出库（保留清单+哈希收据即可）；大二进制/音乐/字体改为"本地放置 + `bootstrap_inputs.py` 校验清单"，或明确迁到独立数据仓库。收益：克隆从 538 MiB 量级降到几十 MB，且降低分发风险。
7. **给手册定完成边界**：例如"五大领域各 4 篇、共 20 篇为 dev4 验收目标"，而不是"5,135 条全讲"。当前 0.39% 的覆盖面若不作边界声明，会持续吸收全部生产力。
8. **顺手补掉的确定性尾巴**：`servicedata` 正式条款入库（需重建 `out/script.fls` + 13 项回归，另轮授权）、`release`/`Timer` 类断言收窄、`1288` 排除策略的书面固化。

---

## 8. 总体评价

这是一个**逆向质量远超平均、工程纪律远超平均、但产品化进度明显滞后**的项目。

- 逆向侧：双 VM、0SLF、路径哈希、XOR、编码链路，都做到了"地址级 + 字节级 + 可复算"，并且有一例真正落到用户实机的客户端改造（原生注册界面）。这部分可以直接作为方法论范本。
- 工程侧：证据指纹、失败即失败、跳过不算通过、原包只读、核心层不依赖 Qt——这些规矩执行得相当彻底，本次独立复跑**未发现任何虚报**。
- 风险侧：把大量精力投入到"记录工作过程"（240 KB 的 STATUS、394 篇 md、七代理流程）与"边缘能力打磨"（六套工具、5,135 条目录），而**目标闭环（能玩的私服）与关键输入（真实抓包）都还没开始**。这是典型的"研究型项目的成功陷阱"：证据越来越硬，产品越来越远。

如果只允许改一件事：**把"第一条真实链路 + 一次真实抓包"设为唯一 KPI，其余线一律让路**。项目的技术底盘已经足够支撑它，缺的是收口。

---

### 附：本文使用的复跑命令

```bash
python3 -m unittest discover -s server/tests/architecture      # 161 OK
python3 -m unittest discover -s server/tests/catalog           # 34 OK
python3 -m unittest discover -s server/tests/review_api        # 27 OK
(cd map_editor && python3 -m unittest discover -s tests)       # 88 OK (1 skip)
(cd resource_editor && PYTHONPATH=src python3 -m unittest discover -s tests)  # 118 OK (33 skip)
python3 script_manual/check_manual.py                          # 六闸门
npm ci --prefix server/apps/review_web && npm --prefix server/apps/review_web run typecheck
npm --prefix server/apps/review_web test                       # 112 passed / 9 skipped
sha256sum data/script.fls tools/decompiler/script_fls_keys.json
```
