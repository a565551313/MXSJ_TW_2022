# 项目当前状态（STATUS）

> **2026-10-18 更正：正式服恢复，本地服独立化。** `server/` 保持 PR #52 合并前的 `cb2409aa` 状态。本轮在 `local_server/` 内建立独立 `src/mxsj_local_server`、配置、测试与打包结构，从历史实现迁入 SQLite／账号／会话／角色基础及日志，不再依赖正式服包。68 项本地测试通过；其他玩法只有契约边界，协议接入和 GUI 待实现，不宣称完整正式服等价。下文旧“共享实现”描述仅为历史。

> 快照：**2026-10-18，Asia/Shanghai**。§1–§2 是唯一当前概览；下方 §3 及后续编号记录是按日期保留的历史证据，不因其中写有“本轮／最新”就覆盖本表。
> 规则见 [AGENTS](../AGENTS.md)，能力入口见 [README](../README.md)，建议阶段见 [ROADMAP](ROADMAP.md)。
> 旧顶部摘要与组件表已[完整归档](archive/2026-10-18-status-prefix.md)；原 §3.1–§3.73 等章节不搬迁，保留既有引用。

## 1. 分支与集成

| 项 | 当前核实值 |
|---|---|
| 会话分支 | `arena/e0fb7c91-mxsj-tw-2022`（active，固定名称） |
| 本轮起点 | `7259dd11`（当前检出基线，已含 PR #52/#53 合并） |
| 集成边界 | ui_editor 目录型基路径诊断归类在当前分支，尚未合并 master |
| 本轮授权 | 用户确认「先修吧」：先做诊断归类（①）；画布拼帧预览（②）与 `.spr` 解码待后续 |
| 本轮证据 | `tests.test_diagnostics` 21/21（含 3 项新回归）、无 Qt 核心套件通过、ruff 0 报告、`check_windows_compat` 0 ERROR；Qt/GUI 模块沙箱缺 `libGL.so.1` 未执行，详见本轮记录 |

## 2. 组件状态与实测

版本按当前源码元数据核对；测试计数仅属于下列范围，不用于计算项目完成率。

> 本轮 local_server **68 项测试通过**（原基础与日志回归 64 项，独立工程检查 4 项）；其他项目测试结果仅保留历史，不算本轮重跑。Windows／GUI／客户端接入未验收。

| 组件 | 当前能力／版本 | 本轮检查与边界 |
|---|---|---|
| 独立 SQLite 本地服 | `local_server/src/mxsj_local_server` 自有实现：账号／会话／角色基础、事务与日志；独立 CLI 和构建入口 | **68/68**；单独复制目录后运行通过。无游戏 TCP／进图／完整玩法／GUI／Windows EXE 验收。正式服目录保持恢复状态 |
| 独立客户端 Web 服务 | [web_server](../web_server/README.md) **0.3.0**：PySide6 GUI、浏览器后台、独立监听启停／暂停、文本发布与回退、访问控制及诊断／审计候选实现 | 本轮 **60 项通过、3 项 GUI 跳过**；Qt 原生 libGL 缺失，GUI／Windows／浏览器视觉交互未验。HTTP 管理与权限边界使用真实回环测试；未知原生更新格式仍未实现 |
| 本地服诊断日志 | 位于本地服 core/observability；JSONL、轮替、脱敏与操作追踪 | 已包含在本轮 68 项回归中；非事务资产审计，Windows 锁／ACL 尚未实机验收；[说明](../local_server/README.md) |
| 静态复核链 | Catalog → FastAPI → React，只读候选数据，不是游戏网关 | Catalog **34**、API **27** 通过；网页类型检查／构建通过，测试 **112 通过、9 跳过**；本轮未做实时后端／真实浏览器验收 |
| 脚本编辑器 | **0.6.0.dev7**，双 VM、双恢复引擎、原生分段修复、新包构建 | 选定核心 **38 通过、3 跳过**（41 项）；未跑全套 GUI、旧 VM 完整环境或 Windows／游戏验收；历史 dev6 全量结果不能替代本轮 |
| 资源编辑器 | **0.4.3**，后台识别、撤销、原生布局导入／替换、新包保护 | 本轮未跑完整套件；共享核心检查通过。用户曾确认特定大包打开提速，不外推所有资源兼容 |
| UI 编辑器 | **0.8.5**，目录型基路径归类（`RESOURCE_DIR_BASE`，不再误报缺图）；0.8.4 编码/刷新/布局导出仍在 | 本轮 `tests.test_diagnostics` 21/21；画布拼帧预览（②）与 `.spr` 解码未做；九宫格近似与完整语料限制仍在，历史实现见 §3.60–§3.61 |
| 地图编辑器 | 一期只读解析／预览／导出 | **87 通过、1 跳过**（88 项）；有未关闭文件 ResourceWarning；1034/1035 固定样本的 GIRB **300/429** 扇区仍未解，不是全游戏统计 |
| 脚本手册 | **0.1.0.dev4**，只读目录、说明、专题与审核链 | 严格来源／完整登记校验通过：**5135 登记／20 说明／16 有限通过／1 排除**；四份战斗说明待非作者独审，专题不继承模块审核 |
| 共享核心／开发工具箱 | `mx_common` 唯一真源，生成副本独立交付 | **4 模块／9 副本一致**；devkit **44 通过**（含 Pillow 精灵交叉测试） |
| 逆向输入与来源 | 原包、key DB、材料映射 | 两份锁定 SHA 匹配；文件名来源映射 **96/96**，不是玩法或全量源码恢复证明 |
| 原生注册 | `tools/registration`；采用 PR #32 的用户确认版本 | 确认仅限当时版本／交互；没有真实注册服务。本轮未重跑；旧 overlay v3/v3.2/v3.3 已作废，禁止分发 |
| 本地 Mock | 登录、创角、进图及部分交互、JSON 存储 | 同会话上一轮 `--self-test` 回环通过，本轮文档检查不重复运行；不是正式认证／事务保证，也不是 Windows 客户端验收 |

### 当前阻塞项与风险

- **原生验收**：编辑器自洽回读不等于游戏正确；Windows／EXE／真实客户端和完整外部语料没有本轮验收。
- **Mock 误用**：默认准备客户端时可能改包及写开发模式；`--no-patch` 不是完全只读。已有账号未验证密码摘要，快速重登未验证请求 key，不可用于公网账号服务。见 [Mock 边界](MOCK_SERVER.md)。
- **依赖**：本轮 `npm audit` 非零，报告 1 moderate／2 critical，涉及 Vitest 开发依赖链；不等同于生产静态页面漏洞，需核实条件后升级，禁止盲目 `--force`。API 浮动依赖也需后续锁定。
- **自动化**：当前检出无 `.github/workflows`；CI 是建议待办，不是本轮实现。
- **许可／材料**：商业客户端与字体的再分发权利未确认，根目录无 LICENSE；恢复引擎另有许可要求，不把整包当开源工具发行。

### 下一步与未执行范围

1. 后续按授权建立 CI、依赖升级与可重复环境；本轮只记录缺口。
2. 固定编辑器真实样本、Windows／原生验收与回退记录。
3. 本地基础已实现账号／会话／角色元数据持久化；用户于 2026-10-18 同意暂缓原生加密接入，先保留分层边界，后续优先通过 CLI／自动化测试推进共享业务。legacy 凭据／有界 TCP、原生客户端选角／单地图另行接入，不再作为立即迁移 Mock 的任务；详下方决策记录及 [本地入口](../local_server/README.md)。PostgreSQL 同规则适配与专项并发验收仍待实现。
4. 本轮未执行完整编辑器 GUI、Windows EXE、游戏、独立 review-browser 验收套件、真实浏览器或公网服务；不把历史 Qt 桩库结果移植成本轮结论。

### 决策记录：暂缓原生 TCP 加密接入（2026-10-18）

用户在讨论原生协议后续接入成本后确认“行吧。先记录一下”，随后决定交由另一个 Agent 并行攻克原生信道。本会话仅记录并提交决策，不启动实现、客户端改包或联调。

- **现状**：新共享服务尚无 TCP 监听；原生 `C_net / SetSeed` 游戏信道加解密仍未恢复并验证。已有 Hello／部分报文字段证据不能当作完整原生接入；`IMProtocol.dll` 的算法不能替代游戏信道算法。
- **推进顺序**：本会话暂缓原生加密接入，先通过现有操作员 CLI 和自动化测试推进共享业务；原生研究由独立 Agent 并行推进，不要求共享业务等待研究完成；本地 SQLite 与未来正式适配器遵守同一业务规则，不做本地放宽版。
- **保留边界**：TCP 连接 → 可替换的协议适配层（握手、加解密、拆包、字段编解码）→ 认证／会话入口（验证后产生可信 RequestContext）→ 共享业务 → 持久化适配器。不得让业务层依赖 socket、原始包或加密状态。
- **返工预期**：未来主要补协议适配层和联调，原则上不因传输加密重写账号／角色规则、SQLite 事务与幂等；但原生包头、长度、收发状态和握手顺序可能关联，不能承诺只替换一个加密函数。凭据和会话语义仍可能需要局部调整。
- **凭据边界**：旧客户端 MD5 摘要不能冒充当前 `operator-utf8-v1` 的原始密码输入；legacy 认证须单独适配和验收。当前只用假测试账号，不提前引入真实账号迁移负担。
- **测试入口**：若后续确需网络测试，再单独实现显式隔离、默认仅本机的测试入口，不冒充原生协议。本次没有授权立即建立明文 TCP 或新增绕过补丁；原生兼容目标不变。
- **禁止迁入**：旧 Mock 的免密码认证、固定／未验证重登 key、自动客户端改包与加密绕过，不得作为共享服务默认逻辑。共享日志不记录凭据或原始敏感报文。
- **恢复原生接入的验收门槛**：独立算法／报文证据与测试向量、连续多包及双向状态／分段／重连验证，再进行不绕过加密的 Windows 原生客户端联调；未完成前不宣称原生已接通。

**后续明确授权：独立 Agent 可修改 `data/script.fls`，以加快原生任务。**
先备份原包并记录 SHA-256，在隔离测试副本中只修改必要 entry，记录用途与回退方法，并核验未涉及 entry 内容不变；大包和敏感采集数据不提交 Git。此授权不自动扩大到 EXE、DLL、key 文件或共享业务接口。
允许必要的脚本观察／测试／兼容适配；关闭 SetSeed、明文或替代算法仅能算标记清楚的对照实验，不能作为原生加密完成证据。优先交付原生握手→正确解读登录加密包→客户端正确接受响应的最小闭环，并验证双向连续包、分段与重连。最终须分别说明修改客户端与未修改客户端的实测状态、保留补丁及其语义影响。
独立 Agent 负责协议研究／适配，不迁入 Mock 的认证捷径，不改共享账号／角色规则、schema 或事务；接口调整先协调。完整任务说明已在对话提供，当前授权只代表允许开展，不代表任何原生实现已完成。

本轮只更新文档，未重跑代码测试；上方测试数保留的是上一轮日志模块验收结果。
保存时核到本地 HEAD 为 `cb2409aa883814018c8479c5d359a8a845b24d8a`、远端会话分支仍为 `af7d6e5072346bb0e23ec1130eea2f62d3bf4cf5`，工作文件仍含后续实现；本轮不重置或覆盖文件，不把既有差异重新提交。提交前已取回远端提交并核对全部 2793 个受跟踪文件：无缺失，仅本次 docs/STATUS.md 决策记录不同；随后只恢复当前分支指针与索引到远端基线，未覆盖工作文件，未重复提交既有实现。

### 独立 Web 项目决策与基础实现（2026-10-18）

用户明确指定项目名 `web_server`，使用 Python，公告／区服列表／更新分发可独立部署，不依赖游戏服务或原生 TCP 攻克。
本轮建立 `web_server/` 可独立复制运行的标准库 WSGI 基础、开发 runner、显式资源配置和测试。默认仅托管无业务含义的 example.txt，不猜测原生更新清单，不修改 update.ini、server.ini 或原始客户端资源。
支持原始字节 GET／HEAD、ETag／304、缓存控制和仅反映 Web 存活的 healthz；无目录浏览／匿名写入口，资源显式白名单、路径和链接校验、文件与快照大小限制。
运行目录需由可信发布者管理，采用启动快照；多副本切换不是原子发布。开发 runner 不用于公网生产，生产 WSGI／代理、TLS、更新信任链、Range 下载、完整日志及发布管理仍待实现或选型。
验证：`python -m unittest discover -s web_server/tests -v` 14 项；配置 check-only、ruff 和 Windows 静态检查通过。仅本子项目验收，不重跑或继承全仓库运行验收；未进行真实客户端／Windows EXE／生产部署测试。

### Web 已知文本格式落地（2026-10-18）

按用户要求，将已知公告／客服公告／基础区服列表写入 web_server：新增 UTF-8 操作员内容输入、严格 Big5／CRLF 生成器、假数据示例及三个只读 HTTP 路径。生成只写全新 release 目录，不改客户端配置或资源；未知更新接口继续 404。
[LEGACY_FORMATS](../web_server/LEGACY_FORMATS.md) 记录候选代码依据，以及 reserve/type、可选 serverid、列表附加段、HTTP 特性、更新清单与包格式等未核验事项。基础五字段列表不等于完整原生选服兼容；没有伪造更新成功或客户端验收。
本轮 22 项 Web 测试通过，含字节输出、Big5 严格编码、CRLF、字段拒绝、不覆写发布和未知接口 404；lint、配置自检与 Windows 静态检查通过。未运行 Windows 客户端、未探测官方 URL、未重跑游戏服务端测试。

### Web Python 工程规范整改（2026-10-18）

用户指出 web_server 未按 `PYTHON_TOOL_CONVENTIONS.md` 完整交付并要求整改。本轮重排为 `src/mxsj_web_server/{core,gui,data}`，GUI 仅预留边界说明，**不擅自实现仍在讨论的桌面窗口／远程后台**。
新增 pyproject／统一版本 **0.2.1**、包入口、requirements／开发依赖、自检 bootstrap、ASCII／CRLF 双击 BAT、两模式 PyInstaller spec 与构建 BAT；保留 run.py/content.py 为薄 CLI 入口。示例资源迁入包内只读 data；默认可写配置在 APPDATA/MXSJWebServer（无 APPDATA 时为用户主目录），不写安装包；显式发布目录仍由操作员选择。

- **Linux 已做**：35 项 unittest（原功能回归、独立中文空格路径、无副作用自检、版本一致性、依赖镜像流程替身、profile 不覆盖、源程序 HTTP 回环与关闭、spec 两模式结构测试），ruff 零报告，自检及 Windows 静态检查通过；构建 wheel 并在独立 venv、仓库外目录通过入口版本／配置检查。
- **构建阻塞**：onedir／onefile 均实际尝试 PyInstaller 干跑，但缺少 `libpython3.11.so.1.0` 而失败。结构替身测试不是打包成功，本轮无 EXE 产物。
- **Windows 待验**：BAT、自装依赖、两模式 EXE、中文路径、实际 APPDATA 权限、关闭后进程清理、原生客户端读取；Python 3.10 仅语法边界检查，实测解释器为 3.11.2。
- **已知功能边界**：当前是 CLI，注册 console-scripts、EXE console=True；尚无 QApplication、GUI、远程后台、后台开关或 Qt 验收。以后真实 GUI 按 PySide6／gui-scripts／console=False 交付，不能把预留目录称作完成。公网部署、未知更新格式及发布管理仍未实现。

证据：[Web 工程规范检查](analysis/evidence/web_server_standards_20261018.json)。原客户端资源、配置和游戏服务端代码未改。

### Web 管理器与双入口第一版（2026-10-18）

用户确认八模块设计并明确“开始编写”。本轮在独立 web_server 内实现 0.3.0 候选：
- PySide6 本地管理器：菜单、用户指定顺序的工具栏、七个管理页面、独立后台开关、托盘菜单与最小化恢复、关闭二次确认；耗时操作经 Worker，不在 GUI 线程执行。
- 现代浏览器后台：单管理员登录／会话、公告与区服编辑、预览／保存、生成版本／切换回退、设置／ACL、日志导出、公开服务控制。后台监听控制及密码重置仅本地。
- 共用 Manager：SQLite 独立状态与不可变文本版本、全局 revision 冲突保护、发布指针与内容审计同事务；失败不替换已发布内存快照。两项监听默认关闭，用户需保存→生成→发布。
- 安全：随机盐 scrypt、短期内存会话、CSRF／Origin／Host、HTTPS 后台可信代理来源限制、两套 CIDR 名单与有效期、可信转发链、登录／请求限流。单目录单进程锁，绑定失败不自动换端口。
- 公开暂停为503、后台暂停只读、停止释放端口并撤销后台会话；有界线程／请求体／socket 超时。日志轮替、敏感字段排除、写失败告警；监听生命周期诊断不宣称事务审计。

**Linux 已做**：63 项测试中 60 通过、3 GUI 因缺 libGL.so.1 跳过；真实 HTTP 权限／生命周期／发布失败／回退测试，ruff、Windows 静态与 JavaScript 语法检查通过；wheel 独立安装核心和后台资源检查通过。
**未验／阻塞**：完整 bootstrap 自检返回2（Qt原生库缺失），core-only 自检通过；PyInstaller 缺 libpython3.11.so.1.0。没有 Windows EXE、托盘／DPI／窗口截图或真实浏览器交互验收，不将静态／HTTP测试算 GUI 通过。
**功能限制**：单管理员、无 MFA／多人 RBAC／Windows Service 安装；桌面编辑菜单作用于文本控件，表格无全局撤销栈，布局持久化／最近配置未实现。后台设置暂为 JSON 编辑器。原生更新包与清单仍未恢复，禁止假报更新成功；服务不是直接面向公网的抗 DDoS／TLS 产品，须按部署说明加反向代理和网络限制。
证据见 [Web 管理器检查](analysis/evidence/web_server_management_20261018.json)，使用方式见 [README](../web_server/README.md) 与 [管理设计](../web_server/docs/MANAGEMENT.md)。游戏服务、旧 Mock 和原始客户端资源不变。

### 历史导航

- 旧顶部概览：[归档](archive/2026-10-18-status-prefix.md)。
- §3.1–§3.2：架构证据修复、目录寻址结案。
- §3.51–§3.53：手册审核与专题；§3.60–§3.61：UI 0.8.4。
- §3.63–§3.71：脚本原生加载问题及分段修复；§3.72：Mock；§3.73：PR #51 冲突处理。
- 以下旧 §4–§7 也是历史管理记录；当前等待项／下一步以本节为准。

## 3. 红灯与已知问题

> 以下逐节保留历史原文。状态可能已被后续章节修订；本轮判断以 §2 为准。

### 3.1 ~~架构测试红：Agent E 证据的输入指纹过期~~ ✅ 已修（2026-10-15）
- 现象：`server/tests/architecture` 中 `test_agent_e_map_npc.InputPinningTests.test_evidence_file_matches_regeneration` FAIL、`test_review_csv_export.RealBatchTests` setUpClass ERROR；`python3 server/tools/export_review_csv.py --check` 报 `E evidence changed; review required`。
- 根因：提交 `45d5590`（10-13，“修复 script.fls 残余条目的分段参数”）修改了 `tools/decompiler/batch_decompile.py`（+492/−10），而 `server/docs/csv_checks/agent_e_reproduction.json` 的 `inputs.shared_decoder.sha256` 钉的是旧值 `7490dbab…`，现值 `242543f8…`。
- 已核实：重新生成后与已提交证据**逐字段比对只有这一个哈希不同**，地图/NPC 分析结果零差异。
- 处置 ✅：按上述命令重生成证据后，**还差第二步**——`batch_001/manifest.json` 的 `tool_and_evidence_sha256` 把证据与 `batch_decompile.py` 都按文件哈希钉了一遍，因此必须跟着刷新，否则 `test_review_csv_export.RealBatchTests` 会从 setUpClass ERROR 变成 2 条真 FAIL（该 ERROR 原本把这两条掩盖掉了）。而 `export_review_csv.py` 拒绝写非空目录，所以刷新方式是：`--out /tmp/b001` 干跑 → `cmp` 确认**只有 `manifest.json` 不同**（全部 CSV 逐字节一致）→ 拷贝落位。结果：`server/tests/architecture` **161/161 OK**、`--check` 通过；总 diff = 2 个派生 JSON 共 3 行哈希，`tools/decompiler/batch_decompile.py` 本体未改（只是把它的记录指纹对齐现值）。`server/tests` 里 `review_api.*` 的 3 个 ImportError 是沙箱缺 FastAPI，基线同样红，与本项无关。

### 3.2 ~~逆向结论内部矛盾：目录查找是线性还是有序~~ ✅ 已判定（2026-10-16，反汇编）
- 判定：`.dlg` 走的真实 LoadFile 链 `0x45D580 → 0x609760 → 0x6097F0 → 0x60DD00` 在 `0x60DD00` 用**二分**定位——`0x60DD35` 调 `0x60E690`，该函数是标准 `std::lower_bound`（`sub %esi,%ecx` + `sar $0x4` 求条数、`sar %edx` 取中点、`cmp %edi,(%esi,%eax,8)` 半区推进），返回后 `0x60DD3D` 判「到 end」、`0x60DD41` 判「entry_id 不等」。**因此目录必须按 entry_id 升序**，新增/插入后其后记录下标全变、`r3` 必须重算——资源/UI 编辑器 0.3.3/0.5.2 的修复方向正确。
- 反例实测：同一份新条目改成「追加到目录尾」，用精确复刻的 lower_bound 查询 → **查不到**（插值点落在无关 entry_id 上），与 0.5.2 记录的「新图不显示/重开条目变少/卡屏」症状一致；而按编辑器 `patch_pack_copy` 写出的包（真实 `data/passive.fls`，新增 1 布局 + 3 个乱序资源），新条目与全部原条目都能被该复刻定位，未改条目 0 条变化、`r1=0` 0 条。
- 文档已同步：`notes/fls_path_hash_and_dlg.md` §2 加更正横幅（「线性扫描」那句属 `0x48ECF0` = `ReadFls`，不能用来推断 LoadFile 寻址）；`notes/native_dlg_path_cipher.md` 新增 §2.1（含指令级证据与三条写包推论）；AGENTS §7 该条改写为已判定。
- 仍有效/未确定：`0x48F170` 的**解目录公式**不受影响（三个闭式常量在 `.text` 各出现 1 次，已逐条比对）；`r1` 解码出的 f1 在查询路径 `+4` 上**未被读取**，故 `r1≠0` 仍是保守防守、不是已证实的引擎要求；本轮**无任何真机包验证**，结论来自副本上的离线判定与算法复刻。

### 3.3 环境限制（不是缺陷）
- **本轮脚本编辑器dev6环境已补齐**：真实Qt6.10.3离屏测试，使用固定GitHub来源真实Linux系统ELF库而非空符号桩；双标准VM与Linux pycdc实际构建/运行。以下10-14旧环境描述仅历史，不能代替本轮证据；这些Linux测试材料不进入Windows源码交付包。
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
| `tools/client_patches/` | 328（E501 268） | CLI | — | — | 7 W + 2 INFO（Py 2.5 片段按设计不可解析） | v3.3 已作废（2026-10-14），待还原+原生重做 |
| `tools/data_browser/desktop_app.py` | 37 | **tkinter** | ❌ | ❌ | 3 E（CONV001） | — |
| `work/.../tools/map_gui.py` | （目录合计 585） | **tkinter** | ❌ | ❌ | 2 E（CONV001）+ 3 W | 历史工具 |
| `tools/data-parser/`、`tools/dis_v43/`、`tools/decompiler/*.py` | 82 / 28 / 239 | CLI | — | — | 0 / 0 / 3 W | — |
| `server/`（src / tools / tests / apps） | 124 / 1423 / 291 / 54 | — | — | — | 10 E（验收脚本 `os.killpg`/`SIGKILL`，Linux 侧按设计）+ 93 W | 不交付 Windows |
| `mock_server.py` | 228 | — | — | — | 1 W | — |

本轮已修的「Windows 必坏」项：`work/.../co_code_analysis/bytecode_58_<module>.bin` 改名为 `bytecode_58_module.bin`（`<` `>` 是 Windows 非法文件名字符，Windows 上 checkout 该文件会报 `invalid path`；`crack_table_b.py` 的引用同步改）；新增 `.gitattributes` 强制 `*.bat`/`*.cmd` CRLF 并重归一化 5 个 bat；`map_editor/build.bat` 补 `chcp 65001`。
补齐顺序：① `map_editor` 加 `bootstrap.py` + 启动 bat，修 ruff 74 条 —— **10-14 已做**；② `resource_editor` / `ui_editor` 各加 `build_exe.bat` + spec —— **10-14 已做**（三个 `build_exe.bat` 同一模板：`py -3`/`python` 探测 → `.venv` → `requirements-dev.txt` → `unittest`（`PYTHONPATH=src`、`QT_QPA_PLATFORM=offscreen`）→ `python -m PyInstaller --noconfirm --clean <tool>.spec`）；③ 三个编辑器在 Windows 实机按 CONVENTIONS §5.3 冒烟并回填 §2 —— **待用户**：双击 3 个启动 bat、3 个 `build_exe.bat`、3 个 EXE，任一失败把 `启动日志.txt` / 控制台输出贴回来；④ 两个 tkinter 工具只保留不改，有需求时用 PySide6 重写。

### 3.6 两个编辑器定向审查（2026-10-14，当前检出 fa13871）

首次审查仅复现，以下缺陷现已在 0.7.1 / 0.3.8 修复。所有破坏性复现使用仓库外临时合成包，未改真实资源。

**修复复核**：UI 写包拒绝源包/别名及挂载资源目录其他包，独占临时副本经布局、新图及未改条目逐字节校验后原子发布；任一步失败清理临时文件、源包与旧输出不动。资源保存同样仅输出新包；导出保护当前/历史源包、工作区其他包、硬/软链接，并约束目录边界、多帧目标预检。资源真名缓存保存后重建，导入路径按 entry_id 保留于会话，网格类型/缩略图/选择也在排序后按条目身份重建；发布前失败恢复写前顺序，旧下标与用户编辑不受排序影响。Qt 缺失时批量测试正常收集。额外定位原有 UI 剪贴板测试在解释器退出时 SIGSEGV（基线也复现）：仅在测试 tearDown 清理该组创建的 QMimeData 后，完整测试正常退出；产品不清空用户剪贴板。

- **高优先级：UI 写包输出硬链接可截空源包。** `ui_editor/src/ui_editor/core/pack_build.py:470–497` 只用 `resolve()` 判断同文件，不能识别硬链接；不同路径硬链接进入 `open(out, "wb")`，先截断同一个 inode。复现：185 B 合成源包经硬链接输出后变 0 B，随后报魔数错误。GUI 覆盖提示也只比 `Path`，不能兜住别名。另有显式原位覆盖分支，先改包后校验且无自动备份/回滚，与原包保护规则冲突。应拒绝源资源及其别名，先临时文件校验，再发布新包。
- **高优先级：资源批量导出未保护源包/别名。** `resource_editor/src/resource_editor/core/services/exporter.py:137–172` 仅做路径分段清洗与本批次重名去重，没有目标与源资源的 samefile 检查。复现：条目真名与源包名重合，选源包所在目录导出，42 B 合成源包被覆盖为 10 B 条目负载，仍返回 `entries=1, files=1, failed=[]`。同类缺口还需覆盖已有符号链接/硬链接与导出目录逃逸保护。
- **数据关联缺陷：资源保存后真名缓存错位。** `resource_editor/src/resource_editor/core/model/document.py:363–371` 重建槽位时没有清掉/重建 `_names`，并丢弃新增槽位的 `path_name`；新增一个排序靠前的条目后保存，旧真名缓存仍按旧下标使用。合成三条目复现：新条目 NEW 标成旧 B 的名，B 标成 A 的名，A 丢名；负载仍正确，但真名搜索/导出可能误标。应按 entry_id 保留导入路径并重建名称映射，补「命名→新增低哈希→保存→再次导出」回归。
- 实测：两目录 ruff 均 0；Windows 静态检查均 0 ERROR/0 WARNING。UI 不依赖 Qt 的选定 8 个测试文件共 46 项，45 通过、1 因缺少完整 dlg 语料库跳过；完整发现运行 50 项但有 23 ERROR（包含 setUpClass 错误），均受缺 `libGL.so.1` 阻塞，不能算完整通过。资源完整发现运行 41 项：36 通过、4 跳过、1 ERROR；错误为 `test_batch_ops.py` Qt 导入失败后返回类型注解引用未定义的 `EntryGridPanel`，导致整文件不能收集，包含其中非 GUI 测试。未造系统库桩件，未运行 Windows/真实 interface.fls/游戏原生验收。

### 3.7 编辑器首期增强（2026-10-14，用户「好，开工」授权）

**已实现并离线回归**：资源 0.4.0、UI 0.8.0；代码 `f224f16` + 类型缓存修复 `bf2bfc3` 已推送当前固定分支。此前 0.3.8 / 0.7.1 的源保护、独占临时构建、发布前校验、原子新包发布契约不变。

- 资源：每包独立全局增量时间线，替换/还原/增删/帧图导入可撤销重做，多选/按路径批量导入的成功项算一步；空操作不记步，新编辑截断重做。稳定槽位与相邻对象定位不依赖旧下标，构建排序/保存失败之后仍可撤销。50 步/64 MiB 增量预算、超大单步保留一条（不是总进程内存上限）。成功保存清历史并建立新基线，取消/失败不提前清历史；旧 `undo(index)` 参数只兼容签名，现在按文档最近一步撤销。
- 资源 GUI：Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z、只读时间线、当前选择按条目身份恢复、增删计数与缓存重建；编辑框保留文字撤销，只读预览不拦文档撤销。阻塞保存禁编辑/切包；后台预览完成不能误解锁保存。GUI 预览与 core 类型缓存均带代际，编辑/撤销后旧结果不回灌；类型嗅探旧结果回灌先由新回归复现失败，再修复为带代际缓存。
- UI：改名在属性写入之前查静态引用、列模块/entry/类/方法/位置锚点/代码皮肤并默认取消；添加属性覆盖也走同一入口，核心名字字段不能移除。重复/非字符串的新名字拒绝；删除枚举全部后代并继续尊重子树锁定。确认只改布局，不改脚本/索引、不自动接线。
- UI 诊断：零 Qt 只读核心，资源存在性注入；重复名、尺寸/坐标类型、负/零尺寸、父矩形越界、挂载来源缺资源、待入包资源、目标字段编码、静态索引缺控件。按树路径定位，过期结果暂停定位；警告可本次标有意设计，但不写 `.dlg`、不隐藏保存检查、不能隐藏编码错误。零尺寸可能是自动尺寸，越界可能是滚动/重叠，缺资源可能是未挂载/热更新，静态未命中不代表无动态引用。
- 保存清单：资源列真实新增/修改/删除、身份/缓存真名/存储大小，不为认名读取未改负载；UI 列相对最近成功保存基线的树位置字段差异、旧/新值、控件增删、图片新增/替换/未引用跳过与全部诊断。散装不嵌入图；失败/取消保关联/基线/挂账，成功才重设基线。UI 保留撤销历史，撤销/重做至保存基线可恢复干净；`1`/`True` 这类 Python 等值但序列化不同的未知字段也正确列差异和标脏。Big5/GBK 编码错误在 GUI 清单与程序化窗口写回前拒绝，不自动简繁转换，不把兼容回退当引擎支持。

**实测证据**：新增 67 条回归（UI 33、资源 34）。使用 `git archive 9ee68e3` 的仓库外只读基线，资源新增撤销、引用改名取消两条同一探针旧版均 FAIL，本版均 PASS；另补类型缓存旧嗅探回灌与等值类型脏标记的先失败后修复回归。完整进程结果：UI 170 项（169 通过、1 缺全量 dlg 语料库跳过）、资源 97/97，均退出 0；Python 3.11.2 / PySide6 6.8.3 / Pillow 12.3，GUI 仅沙箱 offscreen + 系统库桩件，桩件不入库不交付。无桩件资源 97 项（74 通过、23 GUI 跳过）；UI 无 Qt 12 模块 92 项（91 通过、1 语料库跳过），额外确认测试过程没有 import PySide6。两目录 ruff、Windows 静态检查均 0；bootstrap `--check-only` 均通过；`git diff --check` 通过，锁定 script.fls/key DB SHA 与 AGENTS 完全一致。

**未验/不扩范围**：Windows EXE/桌面快捷键手感、真实完整 `interface.fls`、游戏加载/点击与动态脚本均未验；没有实现自动接线、消息号规划、脚本源码编辑/编译写回或包外项目文件；九宫格只有 `CPngNineFrame` 的**固定三分近似**（切割线不可配、未与游戏切法比对，M3.3 仍未做）。0.8.1 已补成功保存新包后的解析器优先重挂/缓存失效与树挂载，合成布局重开验证通过；真实新图显示仍待实机。诊断只说当前挂载来源未找到，不将其当新包缺失。合成 data.fls（含目录条目）保存后槽位数量、元数据与历史重基线已补专项回归，不外推真实大包/Windows 线程交互验收。未动真实客户端资源、架构证据红灯或注册/服务端代码；未构建 EXE/上传测试包/合并/发布。

### 3.8 两项导入交互（本轮：资源 0.4.1 / UI 0.8.1）

- **授权范围**：资源按路径导入改可搜索/可手填下拉；UI 资源树包根右键
  导入本地 `.dlg` 到完整包内路径。只生成新包，不自动带图片或接脚本。
- **资源**：普通/多选 0SLF 路径导入与帧图转精灵共用 editable QComboBox /
  contains、忽略大小写 QCompleter。候选只取当前槽位真名，剔除目录/无名/
  已删条目；新增/撤销后重新选择即更新。已有地址默认 No；严格相对 GBK
  路径校验，不把本地硬盘地址当游戏地址。FLSDATA 文件名导入行为不变。
- **UI**：无已识别布局的 0SLF 包也入树；导入经过受限解析、Big5 显示文本/
  GBK 资源字段检查，目标是非布局资源则拒绝。取消/错误不切文档；替换和
  丢弃未保存文档都确认。导入后是单文档「待入新包」叶子，可预览/编辑，
  切换/放弃清叶子，保存失败保留内容/历史/待入标记，非多文档队列。
- **核心写包**：`allow_create=True` 显式启用缺失布局新增；默认仍拒绝缺条目。
  新增明文（零 XOR 密钥，与资源编辑器一致），已有布局沿原密钥替换。
  有序目录/非零种子、病态回退重组、独立负载比对与布局读回后才原子发布。
  GUI 校验总数和编号集合计入新增布局；不覆盖原包/别名或其它挂载源包。
- **状态迁移**：成功才清待入标记、优先挂载新包及登记本会话自定义路径；
  树读取严格锁定用户点中的包，不按同名跨包顺序冒取。0SLF 不存全名，
  重启无法自动恢复所有未知路径。连续导入先保存，再在生成的新包节点导入下一份。
- **本轮实测**：新增 30 条回归（资源 7 / UI 23）。完整离屏资源 104/104、
  UI 193 项（192 通过/1 缺完整语料库跳过），退出 0；Python 3.11.2 /
  PySide6 6.8.3 / Pillow 12.3，GL/EGL/xkb/dbus 桩仅在仓库外用于 offscreen。
  无桩件资源 77 通过/27 GUI 跳过；选列 12 个 UI 核心模块 100 通过/1 跳过，
  断言未 import PySide6。两工具 ruff、Windows 静态检查 0/0/0、bootstrap
  `--check-only` 绿；锁定 script.fls/key DB SHA-256 均不变。
- **仍未验**：新增明文布局的客户端原生加载、完整布局语料、Windows 桌面
  快捷键/EXE 与真实大包。工具读回通过不等于游戏验收。已按用户本轮授权上传两个工具源码启动包（见下方交付记录）；未构建 EXE、
  上传客户端测试包、开 PR、合并或发布；未改架构证据、注册/服务端代码及原始客户端包。

### 3.9 工具源码包交付（本轮用户授权 Google Drive 上传）

- 源码提交 **`fe2e057a3783bf595db5bce0320660b279d6d472`**；两个 ZIP 均只含
  对应工具的已跟踪文件、启动/EXE 构建脚本、数据字典/静态索引、测试、文档、
  `交付说明.txt` 和逐文件 SHA-256 清单。不是 Windows EXE，不附客户端包、
  Python/依赖安装包、缓存或沙箱系统库桩；需 Python 3.10+ 和联网安装依赖。
- 打包前工具副本逐文件字节比对通过；ZIP CRC 与全文件读回比对通过。
  在无客户端数据的交付副本复跑：资源 **97 通过 + 7 数据缺失跳过**（104 项），
  UI **191 通过 + 2 数据/语料缺失跳过**（193 项）；均退出 0，Qt offscreen +
  仓库外系统库桩。交付副本 ruff 与 bootstrap 自检通过；不外推 Windows/游戏验收。
- 已上传用户 My Drive 根目录；上传返回和再次读取的**文件大小/MD5 均与本地一致**，
  两个最终文件未在垃圾桶，未更改分享权限。UI 交付说明补准“启动仅自动安装 PySide6，
  转精灵另需 Pillow”，更正前本轮刚上传的 UI 副本已移垃圾桶（非永久删除）；工具代码未改。

| 工具 / 文件 | Google Drive | 大小 / MD5 / SHA-256 |
|---|---|---|
| 资源 0.4.1 · `resource_editor_0.4.1_source_20261014_fe2e057.zip` | [下载](https://drive.google.com/file/d/1D-zDVh5rfpfxcTw5J1AGqDaJdlA-S2zi/view) | 159,089 B；MD5 `622b700479431736d62202ae2bbe555c`；SHA-256 `fcf7f84a68d5ff2a21c20df2c75e778cd301aa1c2b9aea47b9414bc02b8e90b1` |
| UI 0.8.1 · `ui_editor_0.8.1_source_20261014_fe2e057.zip` | [下载](https://drive.google.com/file/d/13Os-8wj-R86AHnvXWNubkrDFhG47NBV7/view) | 383,390 B；MD5 `69a9539af9cefeb090afe0d4a3d7c23a`；SHA-256 `d708608f204b25383579119aa473f1fe0410543a45c75d8eff6a05917352fa27` |

### 3.10 用户反馈修复：重开找不到布局 / 大包打开变慢

- **用户实测更新**：用户确认当时填写 `login/regform.dlg`；约 600 MB 包在双击
  文件名的打开读条阶段很慢。更新后用户本轮明确反馈“速度很快，新布局也找到了”。
  两项交互问题按该测试环境通过；未拿到实际包字节，不外推所有写回/游戏加载或 EXE 验收。
- **已确认的代码缺口**：0.8.1 只存本会话路径，重启未知地址不参与扫描；
  资源打开阻塞任务会先嗅探全条目、读布局引用，然后才显示网格。
- **UI 0.8.2**：保存/精确回读成功才把合法 .dlg 地址存入 QSettings；新实例
  按每个包实际编号相交显示，不改包格式、不增加包外项目文件。包根“按包内
  路径打开布局…”只读检查旧新包，成功才入树/记忆；失败/取消不挂幽灵节点。
  已知 `login/regform.dlg` / `login/regterms.dlg` 同步两工具字典。basename
  与完整地址不等同，不会猜路径/自动重命名。新回归有另一个进程读设置证明。
- **资源 0.4.2**：阻塞阶段只建索引/快速匹配字典；完整类型和布局引用后台补。
  “待识别”不假报二进制；每包最多一任务，发布检查文档/代际/归档，过期拒绝
  并重排；保留页码/多选。label/搜索只匹配目录，不隐式读全部布局；显式目录
  导出仍补全引用真名。读/关闭互斥，防旧后台工作读取被复用的文件描述符。
- **本轮回归**：资源 110/110、UI 197 项（196 通过/1 缺完整语料跳过），
  Linux / Python 3.11.2 / PySide6 6.8.3 / Qt offscreen + 仓库外系统库桩，
  进程退出 0；ruff/wincompat 0/0/0，bootstrap 自检通过，锁定原包/key SHA
  均不变。未在 Windows/用户的 interface.fls 量耗时，不能宣称实际卡顿已消失。
- **交付完成**：修复代码 `f6e6e2a` 已推送，两个源码启动 ZIP（非 EXE）已上传
  My Drive 根目录。交付副本资源 103 通过/7 数据跳过、UI 195 通过/2 数据或
  语料跳过，退出 0；ruff/ZIP CRC/逐文件字节与清单校验通过。上传返回大小/
  MD5 与本地一致，不附资源/缓存/系统库桩，不改分享权限、不删除旧版。
  旧 0.4.1/0.8.1 包不是此次修复版。
  - [资源 0.4.2 下载](https://drive.google.com/file/d/16OCdL0m6ajPxPTbk6eWy3qUqyX2RU7Ny/view)：
    `resource_editor_0.4.2_source_20261014_f6e6e2a.zip`，162,019 B，
    MD5 `0248ce26fc493fce58f10b9c6e5f57a1`，
    SHA-256 `9f26b885fbae1f665925c89763de7172adcb4318c259d7edb078b9f5690c6cef`。
  - [UI 0.8.2 下载](https://drive.google.com/file/d/12iJrtHBbr9MqZYRwmn2XP4cKVP7j1VNg/view)：
    `ui_editor_0.8.2_source_20261014_f6e6e2a.zip`，386,673 B，
    MD5 `c77378c806978420f3f4bb09d5a3f9c6`，
    SHA-256 `3ce6d781d3bd9e965905440892022c6783d12abe537b2fcd46fa0505fbc8893d`。

### 3.11 注册第二期点击“申请会员”卡屏（用户新反馈，待定位）

- 用户已确认编辑器打开速度/新布局查找修复有效；进一步确认：游戏使用网盘
  registration_phase2.zip 的 script，两张新布局在同一个 fls 都能找到；卡屏是
  **整个窗口冻住、无响应**，不是仅“首页隐藏/空屏”。这些前提不再重复询问。
  未取得该用户包字节/原生阶段日志，能找到路径仍不等于加载成功。
- 已找到自写源码 `tools/registration/register.py`（entry 4007），入口打包器
  `build_native_registration.py`（entry 337 的 9 字节条件补丁），已发第二期
  script SHA-256 `17a94c77e4cda673023f0e17221edb73f789183a0af0d4fcd5c6a1d3b651e0b2`。
- 实际流程：`Show(True)` → `Step(0)` → `CRegTermsPanel` 先加载
  **login/regterms.dlg** / 取 loc_msg / 创建原生 COutput；同意后才加载
  login/regform.dlg / 四编辑框和五账号勾选。只确认 regform 可查不够，必须
  同一个实际安装的 interface.fls 同时含两张；在原包上分别保存的两个副本不算。
- 只读解密/解析原始 entry 337 的 code object 并正规化反汇编确认：
  CMainPage.OnMessage 的 pc 215/218/221 为 Show(False)，225/228/231/234
  才调用 register.Show(True)。已有补丁仅改 pc 102..110，不改变这个先后。
  原第二期自写 Show/Step 未捕获构造异常；因此“先隐藏首页、布局构造失败后看似卡屏”
  是有代码依据的**候选解释**，不是已证实的本次根因，更不能排除原生加载阻塞。
- 现有 register_diag.txt 主要覆盖表单消息/提交，没有覆盖入口和条款构造。
  若日志不存在或未新增，不能拿它证明注册模块没执行。
- **本轮新增 phase2-diag1**：自写 register.py 在首次模块/依赖导入、InputSecrecy、
  Step、条款布局、loc_msg/尺寸、COutput 构造/定位/游标/排版/滚动及表单阶段
  各写 begin/ready，每条关文件；photo 不可写时尝试工作目录 register_diag.txt。
  仅阶段/尺寸/异常类型，无账号/密码/邮箱/异常文本。初次构造抛 Python 异常
  时尝试解除输入保密并恢复首页；切页失败保留旧全局引用。没有中断原生同步
  调用的能力，**没有复现/证实修复用户的整窗卡死**；原生函数不返回时 except 无效。
- 只读反汇编原 code object：579/CCombPanel.__init__ 和 4832/COutput.__init__
  均含 MessageProcess，所以“layout begin”或“output create begin”不只定位到
  文件读取/文本构造，也含消息处理。COutput 将行宽设为 w-20；防御性拒绝非正
  行宽/高度，但没有证据表明用户实际控件尺寸异常。不改引擎/布局/目录 f1/XOR。
- 重建真 CPython **2.5.6**，14/14 离线回归通过（无 skip），ruff、Windows 静态
  检查均 0。新增同一故障探针：旧自写源码在模拟 regterms 构造异常时抛出、
  新版回退；另测阶段顺序/文本初始化异常/旧引用保留/日志写失败与备用路径。
  这只证实自写错误处理，不是假装复现真实引擎无响应；未执行任何原游戏代码。
- 已构建仓库外新包 `/home/user/registration-phase2-diag1-build/script.fls`，
  24,263,562 B，SHA-256 `7cf8d5c4b2cfbf6b8e241f0088df5542c5c000ef438244d590a487db0d52d274`。
  原包仅337/4007变；337仍原9字节补丁。用旧自写源码重建出的全包 SHA 与已发
  第二期 `17a94c...` 完全相同，再逐条比较：**相对用户第二期仅4007变，其余
  5001条压缩负载相等**。新包 marshal 精确读回及真2.5.6桩冒烟通过。
- 测试/说明 `tools/registration/DIAGNOSTIC_TESTING.md`。用户只须在测试副本
  备份并替换 script，不重导或覆盖 interface；若再冻住只取新日志最后30行。
  下一步必须取实际最后阶段，再决定检查资源字节/原生排版/消息处理；不能直接
  宣称卡屏已解决。诊断包随后按用户本轮“你传网盘”授权上传；未改权限，原包/key DB SHA 均未改变。
- 诊断包源码提交 `e3c288e631211f59631e89d68b6e09440d077dfe`，本地交付
  `/home/user/registration-phase2-diag1-delivery/registration_phase2_diag1.zip`，
  **24,190,013 B**，ZIP SHA-256
  `ac8b9db8c17f7e39025fd81994c6e76c9e1111427442642829caed1b7356cd6d`，
  MD5 `c82f585455b720a991c237a3e7877a97`。仅 data/script.fls、诊断测试说明、
  源码/构建证据 manifest、SHA256SUMS 四文件，无 interface/编译器/key DB/桩件。
  CRC、逐文件解包相等、包内 script SHA 核验通过；先以会话附件呈现，随后按用户明确授权上传 Drive。
  不重新分发旧二期包，不把此次诊断交付记成原生卡屏已解决。
- **网盘交付已完成**：[registration_phase2_diag1.zip](https://drive.google.com/file/d/1YxoYNmpTejl7qk86K9ELg_b1bvYJcGk8/view)，My Drive 根目录。上传返回大小 24,190,013 B、MD5 `c82f585455b720a991c237a3e7877a97` 与本地一致；未再次下载核验，未改分享权限/删除旧包。

### 3.12 diag1 实机返回条款构造异常；原生路径 XOR 与存储修复助手

> 本节为此前助手阶段记录，用户随后拒绝其作为最终解决方案；已由 §3.13 通用编辑器修复接续，勿再催助手交付。

- 用户本轮提供完整入口日志：模块导入、InputSecrecy 都 ready；
  `step=0 begin` → `terms layout begin` → `step=0 EXC type=Exception` →
  recovery secrecy/home ready。用户明确“不再卡屏，现在点了没反应、不跳协议页”。
  **diag1 回退按此测试环境奏效，注册协议/表单未通过**。已确认这次异常在
  CCombPanel 构造期间、条款文本/loc_msg 初始化之前，不能凭类型确认具体内部行。
- 深追真实 C_sys.LoadFile PyMethodDef：字符串0x6B4038、方法表0x7DB2F0、函数
  **0x45D580**；旧笔记0x461340实际为 **ReadFls**，不能当同一加载器。
  静态追到0x60E080/0x454860路径哈希、0x60E153的
  `key=((hash+0x9234AB)&0xffffffff)^0x937F4912`，0x609C80读包后逐DWORD XOR。
  regterms key字节 `a9bd00b5`、regform `f94b3e60`。不是明文头自解密、也不是
  目录f1密钥。证据 notes/native_dlg_path_cipher.md；原PE哈希/调用位移/指令签名
  新回归钉住，只读字节/反汇编，不执行/模拟执行原游戏代码。
- **确定的旧写入缺陷**：注册说明让资源工具原样导入明文，UI 缺地址新增也为
  明文/零密钥；编辑器回读能解析但原生路径XOR后不再是布局。这与日志吻合；
  尚未取到用户实际存储字节，故实际两条状态/这是否唯一故障仍待助手报告。
  不再把“明文新增实机待验”说成已知可兼容原生；旧笔记明确加更正横幅。
- 新 `tools/registration/repair_interface_layouts.py` 是**标准库一次性CLI助手**，
  非新GUI/EXE、不改游戏脚本、不启动游戏。拖测试副本当前interface到同目录
  `修复注册布局存储.bat`，需要已有Python3.10+，无需PySide等第三方依赖。
  检查两条当前存储：原生密文则不动；明文/已知头反推可解则保留用户全部明文字节
  按路径密钥重加密。只出新包、不取仓库模板、不改目录/其余负载、逐字全文件比对
  后原子独占发布，输入/别名/已存在输出拒绝；缺地址/非法字面量/重叠/无序则拒绝。
  两条均正确则NO OUTPUT，应另查失败点；不盲目补布局/不要求上传600MB。
- 新包通常为 `interface_native_fixed.fls`；diag1 script保持不变。操作说明
  `tools/registration/NATIVE_STORAGE_REPAIR.md`。Windows BAT/NTFS发布/用户实际
  新包和原生跳转尚未验；FAT等不支持硬链接会安全拒绝，不降级覆盖。
- 新回归9项，本轮总 **23/23**（含真2.5.6自写脚本回归，无skip），ruff 0。
  原策略合成探针：明文按真实路径key解密无法还原头，本版密文精确回读原字节。
  覆盖用户编辑保留、跨1MiB块整包等值、旧错误密钥/混合状态、已正确无输出、
  输入/硬软链接/既有输出保护、非法数据、验证失败与发布竞争安全清理。
  这是确定存储缺陷的离线复现/修正，**不是用户条款已实机出现**。
- 没有直接改两编辑器执行管线/发新编辑器版；只在UI pack_build文档标记旧
  明文/零密钥新增不兼容。通用新路径加密与按原生key验证是后续必要修正；
  已正确加密的现有路径再由UI沿原密钥写仍可保留该形式，但游戏仍需回读验证。
  原包/key DB/两张模板均不改，不改337/4007，不写真实注册接口。
- 修复助手源码提交 `ec6511d912d3ddb9c2d588588ab5371f61ca301e` 已推送。
  仓库外 ZIP `/home/user/registration-layout-storage-fix-delivery/registration_layout_storage_fix.zip`
  12,855 B，MD5 `a93a452ffd09504d5c965935bb253875`，SHA-256
  `37b1efee63edd9337f799fc7cc0c4db2ac2b84d08c88a21af7f918faeb7591fa`。
  六文件仅助手/BAT/说明/静态依据/manifest/校验和，无FLS/模板/key DB/编译器。
  CRC/源码字节/解包读回/交付副本ruff、合成包独立CLI执行及既有输出拒绝通过；
  Windows静态检查0/0。此时本地打包完成、未上传，须按现有发布约束获本轮上传授权。


### 3.13 用户拒绝一次性助手：两个编辑器通用原生写入/持续编辑

**需求纠正**：用户布局还在调整，不接受只修regterms/regform存储的助手作为最终方案。
本轮修两个编辑器正常新增/导入→保存新包→重开→再编辑→再次保存流程，不导模板覆盖用户改动。

- 原生密钥为 `((entry_id + 0x009234AB) & 0xffffffff) ^ 0x937F4912` 的小端重复XOR。
  新增/替换目标都用路径编号派生；历史头反推只作输入兼容，不再用于发布正确性判断。
- 两包各自包含相同零Qt `core/native_layout.py`；严格GBK相对路径、字面量AST、不执行源码、
  保留明文混合字节。opaque只看前缀，正常非布局文本/图片不自动编码。
- UI0.8.3：普通/新条目/重组回退都原生编码；发布前严格原生回读、未改负载逐字比对。
  已原生输入不双重加密；附加图片接口拒绝.dlg绕过。没改字段也可保存当前布局迁移。
- 资源0.4.3：按路径新增/替换统一编码；内容替换识别新/旧布局。高级raw保持原字节契约，
  但改动已识别布局保存必须原生回读；原路径记录或源布局提示不会被损坏新头降级绕过。
  原包保护、原子输出、撤销/重做、原未改负载保持；旧头提示仅读4KB，不拖回打开全扫描。
- 先复现旧工具新增：独立公式探针 RESOURCE OLD FAIL/UI OLD FAIL；修后同探针两PASS。
  不是只把3个旧明文/沿任意key期望改掉：另加两个工具连续流程、任意future路径、
  中文GBK/大小写/斜杠、旧明文/错误key、native输入、opaque、失败源/既有输出不动等回归。
- 实跑资源118/118，UI204（203通过+1缺语料库跳过），注册23/23含真2.5.6；
  ruff 0、wincompat0E/0W/0I、自检通过。Qt用仓库外桩+Linux offscreen，非Windows实机。
- 当前操作见 [正常编辑流程](../tools/registration/EDITORS_NATIVE_LAYOUT_WORKFLOW.md)。
  原生注册协议→同意→表单仍待用户测最新输出，不能宣称唯一根因或游戏已全修好。
- 源码ZIP已在仓库外完成CRC/源码manifest核验和解包复跑：资源118项（缺原包7跳过）、UI204项（缺原包/语料库2跳过），无失败。包不含原FLS、Qt桩、编译器或模板；代码提交 `e46e94b` 已推送固定分支，不开PR/合并。
- 本轮询问后用户明确选择“上传两个新版包”，已上传My Drive根目录，未改权限：
  [资源0.4.3源码ZIP](https://drive.google.com/file/d/1GdGFrRPA_e-QvnKsq5w55zahPdSbahxW/view)，
  169,742B，MD5 `76003d580acc6c2b67da04c5c35d9d45`，SHA256 `350f5175fa32bd1d95ce90cf76f7889be734f42d5200680d4debb9e8e2cdf99c`；
  [UI0.8.3源码ZIP](https://drive.google.com/file/d/1S9_89VFYdUWosXrZhAQK419yu9IfGDRu/view)，
  396,808B，MD5 `ff9d71b2d0acd2087bfe7960fa7291e8`，SHA256 `21a6784eda15170bd638caac255aae472da50c094a4e246119400f73dfd777b7`。
  上传返回大小/MD5均与本地一致；未再次下载、未删除旧包，不冒充已构建EXE或实机验收。

### 3.14 2026-10-15 协议已显示，同意进入账号框构造后AttributeError

- 新实机事实：协议可进入；`terms msgid=1`→`step=1 begin`→`form layout ready`
  →`form import C_object ready`→`form account begin`→`AttributeError`。
  用户确认目标控件是account/CBox，不能继续让用户重命名正确控件/重导布局。
- 不能只凭异常类型认定缺哪项；原日志把CEDIT属性、FONT_EDIT属性、原生工厂内部与
  SetLimit并在一段。新增phase2-diag2只分割这条调用链，保留原生接口/参数/协议回退。
  严格代码元数据日志最多12帧；缺失属性名仅在静态co_names中且是ASCII标识符才输出，
  不打印异常值/repr/局部变量/账号资料。字段布局不改，不加字体/控件替代fallback。
- 原始code object只读核对entry3564 CreateEdit别名/7形参/9参数子类构造、entry3854
  CEdit.SetLimit确实存在。测试桩由假cls(name)改为9参数边界；没有执行恢复游戏代码。
- 真2.5.6回归26/26（含6种定位/隐私/旧协议引用保留探针）、ruff0、wincompat0/0/0。
  原diag1源对新的精确定位探针先失败。新包marshal逐字回读及读回模块桩冒烟通过，
  相比按旧源码重建的diag1仅4007压缩负载改变，另外5001条全等。
- 仓库外 `/home/user/registration-phase2-diag2-delivery/data/script.fls`，
  SHA256 `4022b90e3568248317a8c6799c4fc8e61f641a538668616d7b7d51f345f39f09`。
  是诊断版，实际缺失属性及表单显示尚未解决/验收；代码 `839c0c4` 已推送。
  用户本轮明确选择上传，已上传 [registration_phase2_diag2.zip](https://drive.google.com/file/d/1ELUEuF4mGD_4AE4EiYMF5K6wgYDDIYDc/view) 到My Drive根目录；
  返回大小/MD5与本地一致，未改权限/删除旧包，未再次下载核验。
  ZIP `registration_phase2_diag2.zip`，24,201,007B，MD5 `611eab945260ee28628703aa6caf0c29`，
  SHA256 `4ee6b9c8aa2e840527bc3075ae94e3cef56aa19de2df0fd0dd592cd02ae88b78`；
  ZIP CRC/逐文件回读通过，未含模板或interface.fls。

### 3.15 2026-10-15 FONT_EDIT实机确认缺失，按原生注册字体修复

- 用户diag2输出：account anchor/factory ready，font resolve begin后AttributeError，
  `missing_attribute=FONT_EDIT`。实际缺陷为脚本依赖本客户端不存在的旧别名，不是布局。
- 原entry4007 `CRegPanel2/CreateEdits` pc18/21的LOAD_GLOBAL interface/LOAD_ATTR FontLT14_3
  已只读核对；协议正文也实机使用该字体成功。四框/提示区统一明确选该原生字体，
  提示区使用黑色0与当前四框一致，不依赖COLOR_EDIT，不注入别名或fallback。
- 默认离线桩移除以前假设存在的FONT_EDIT/COLOR_EDIT。旧diag2对“缺旧别名仍进表单”
  同探针先失败，新代码通过，测试同时检查四框与提示字体/颜色、旧别名即使存在也不用。
- 真2.5.6 32/32；ruff/wincompat通过。保留diag2元数据保护、分段标记，新增font1版本标记。
  新包与实际已发diag2的精确重建（SHA匹配）只4007变，其余5001条压缩负载全等。
- 本轮构建曾被完整marshal比对拦下：旧修复转译器在边界附近把新代码有效LOAD_FAST猜成
  STORE_NAME（新源解密原生字节实际精确匹配输入）。没有放宽断言/改key DB；新增零执行
  authored_marshal用于已知自写载荷：严格源混淆字节+zero padding比对，拒绝修tag/长度/边界，
  逐co_code确定逆映射后完整标准marshal逐字匹配，再运行新包读回模块桩冒烟。原条目转译仍原逻辑，
  未改batch_decompile证据指纹。新增4项严格校验拒绝损坏回归。
- 输出 `/home/user/registration-phase2-font1-delivery/data/script.fls`，SHA256
  `77b3eac611f52cf8ac750fe1adf57d672e3f3e85f51fa5f9c81980e1d6564466`。
  不动用户interface.fls/布局/协议，不绕过流程，不接注册接口。Windows/表单交互待实机。
  源码包已完成CRC/逐文件回读，ZIP `registration_phase2_font1.zip`，24,199,085B，
  MD5 `766b458916c391b872972a371038badf`，SHA256 `438994935eb3fa6af77c2ac4ee06d5d5f0b1602d2f050ee73f9e189b03ce9a7a`。
  源码 `254e934` 已推送。用户本轮明确选择上传，已上传
  [registration_phase2_font1.zip](https://drive.google.com/file/d/1YtpqnvZFYxDJeK9biN3rLyFcr8WYurf9/view)
  到My Drive根目录；返回大小/MD5与本地一致，未改权限/删除旧包，未再次下载核验。
  不能拿此字体修正冒充全部原生验收。

### 3.16 独立脚本编辑器开工授权（2026-10-15）

用户确认font1后“确实好了”，协议→表单这一步已实机通过，不外推全部控件/服务器验收。
用户要求独立工具、可内置编译器、script.fls与data.fls均支持，先看结构后明确“先提交推送然后开工”。
当前工作区干净，既有字体修复已提交至41f1e49；先提交本设计检查点并推送当前会话分支，随后开始M1。
设计见script_editor/DESIGN.md；M1基础不冒充原生写包/Windows双编译器已交付。

### 3.17 独立脚本编辑器M1基础实现（2026-10-15）

**顺序与范围**：先完成设计提交`2f5f7e4`并push固定分支，再写代码。新增独立`script_editor/`，
不跨目录import旧工具，容器只读模块从资源编辑器有来源地整理并去除写包函数。
版本`0.1.0.dev1`；这是基础代码，不是完整工具交付，也不称Windows可用。

- 核心：0SLF/FLS\0惰性只读索引/稳定条目身份/候选VM；FLS目录名、范围、本地头与尾标记严格校验，
  不用GBK替换丢字；不解压/执行恢复模块。打开后的原包修改/路径替换拒绝旧索引；指纹按需计算缓存。
  源码严格UTF8/可读BOM、原子保存、已知输入/硬软链接保护、明确Big5/GBK选中文字面量。
- 项目：相对路径/包SHA/VM/下标与身份、用户关联而非原生语义证明；原包变化拒绝恢复关联，不复制大包。
- 编译：精确2.5.6/2.7.13及magic检查、exe哈希变化拒绝、Windows x86要求、-E -S独立子进程/30秒超时，
  只compile+marshal、不import/exec目标。仅发布标准pyc；原生输出后端不存在、GUI按钮禁用。
  真2.5最小开发编译器缺binascii/_struct，探针/助手不额外依赖它们；中文co_filename显式用UTF8字节，
  不让2.5将unicode路径隐式转ASCII。助手保留2.5语法，仅一处UP031局部豁免有理由。
- GUI代码：双包树/筛选、来源确认、参考稿只读禁编译、源码多标签/行号/基础单行高亮/查找替换/撤销，
  源码与项目脏状态提醒，索引/指纹/编译后台任务。**这些交互测试未能在本环境执行**。
  自检/中文名ASCII CRLF启动BAT、onedir构建BAT/spec和版本入口已写，未构建/冻结/实机。

**实际验证**：`PYTHONPATH=script_editor/src MXSJ_PY25=<外部2.5.6> MXSJ_PY27=<外部2.7.13>
QT_QPA_PLATFORM=offscreen .../python -m unittest discover -s script_editor/tests`：41项，35通过、6 GUI跳过。
两真实编译测试分别核对版本/头魔数、中文文件名、独立完整marshal读取EOF、编译重现全等、故意含文件写入/
raise的源码**未执行**、语法失败旧输出不变、跨VM拒绝。另覆盖包损坏/失效索引、项目迁移/指纹不符、
输出别名/原子发布失败；仓库外独立副本以`-I`导入全部core，无Qt/兄弟目录依赖。
原始`script.fls`与`data.fls`只读实测各5002/133条，未改内容；锁定script/key DB SHA与AGENTS一致。
ruff 0；wincompat --strict 0 ERROR/0 WARNING；bootstrap --check-only因libGL.so.1缺失准确返回2并日志，
不当作环境通过。PySide6 6.12.0装于仓库外venv，未造Qt系统库桩件，GUI没有算通过。

**尚未完成**：M1 GUI实际运行验收；M2双VM变换/原生独立回读/新包输出；M3真实源码链与差异/关联布局；
M4 Windows两套完整运行时、全文件清单/许可证/哈希、EXE/路径/DPI实机。
`runtimes/manifest.json`明确为空，目前仅exe摘要校验框架，不称完整依赖供应链审计。
Linux2.7.13从CPython官方GitHub tag v2.7.13构建，编译器和产物都留仓库外，不混入Git/发行包。
没有上传脚本编辑器测试包、没有开PR/合并/发布；现有两编辑器/注册运行源码未改。

### 3.18 M2双VM原生新包核心（2026-10-15，用户“继续下一阶段”）

**已实现（支持子集）**：`script_editor/`升0.2.0.dev1，核心/API与实验`native_cli`自包含，
不导入旧打包器/猜测修复器。VM2.5递归等宽opcode映射、来源绑定五段XOR、固定原扩展长度/仅根后零padding；
超长拒绝，绝不缩lnotab/伸缩边界。外部catalog需显式包SHA和catalog SHA，profile还绑下标/身份/存储SHA。
VM2.7递归co_extra、split-stream、跳转双坐标与行号转换；完整有界marshal树读取/引用检查、
单条解压64MiB上限、未知/截断/拼接流拒绝；EXTENDED_ARG与uint16寻址溢出等暂不支持。

写包核心只改明确条目，不添加模块/不猜导入hash。0SLF实际物理顺序不同于ID目录，按原物理顺序写，
目录/r1不变，头未知字段/空隙/尾部保留；data未改本地记录连填充全等，改项重算CRC/长度，保留目录原名原字节。
临时包重开后，全量逐条/容器封套比较；改项从实际新包独立逆变换，标准marshal全字节等于本次自写pyc，
再用精确标准CPython完整marshal读取CodeType至EOF；不执行目标模块。原包变化则拒绝。
发布以同目录临时文件硬链接到**不存在的新目标**，含发布竞态也不覆盖任何已有文件；不支持硬链接则安全失败。
此阶段比允许覆盖旧输出更严格，反复编辑须新名字；已补“重开上轮新包/重绑profile/再改再出新包”回归。

**真正复现后修复**：真实2.7编译的分号语句产生连续`6,0`行号事件，初版将零行差当填充全合并，
完整字节回读断言失败；新增失败样例后改为只聚合`255,0`溢出段，保留合法零行差事件，真编译复跑通过。
没有通过裁行号或放宽相等断言来凑绿。跳转参数流第二坐标被篡改也明确拒绝，不再像旧转译器忽略它。

**独立证据/旧研究差异**：当前`exe/python27.dll` SHA256 `66f90925…`，实际EvalFrameEx位于
`0x1E12A3A0`，分发表RVA `0x12D8EC/0x12DA94`，不是旧笔记中的地址。
只读PE/反汇编抽样钉`tests/evidence/py27_dispatch.json`，标准2.7语义与当前DLL核对：
BUILD_SET104→183、BUILD_MAP105→137、LOAD_ATTR106→230、COMPARE_OP107→124、IMPORT_NAME108→135、
IMPORT_FROM109→155；旧注释名称误标，不能当golden。旧表把原生66映为STORE_SLICE+2，当前DLL实际走unknown，
本工具排除该条并拒绝，不改旧研究工具/架构钉指纹。

**本轮实际跑过**：79项，73通过、6 GUI因libGL.so.1缺失未执行；含两真实标准编译器M1/M2完整管线、
嵌套/闭包/long/complex/集合/字典/导入/属性/比较、行号溢出与分号、目标源码含写文件/raise但未执行，
新包重开再编、多项显式替换、损坏/错身份/错键/超长/回读不符/运行时marshal后置失败/发布失败/输出竞态等。
真实材料测试显式`MXSJ_M2_REPO`，不在独立发行工具内暗找仓库路径；独立core副本无Qt/兄弟依赖检查通过。
- 原始script包4007替换当前自写register源码：其余5001条存储负载全等，完整marshal回读通过。
- 原始data包75替换离线探针：其余132条本地记录全等；另实际命令行端到端通过。
  **data探针有意替换核心库，不能用于客户端**；全部验证产物在仓库外/临时目录，没有上传或交付。
- 原始337严格读取遇未知opcode150而拒绝，已有真实材料负向测试，不能称所有脚本都可编辑。
- 锁定script/key DB和原始data/DLL哈希未变；ruff 0、wincompat --strict 0/0；bootstrap --check-only
  仍因缺libGL正确退出2，不算GUI/环境通过。spec补带独立audit助手，未做冻结干跑/Windows构建。

**下一步/未做（M2时点；M3后续见§3.19）**：M3接GUI写包清单、项目承接新包与关联布局/诊断；未知条目继续只读。
M4 Windows标准x86双编译器随包/全文件哈希与许可证、EXE/DPI/原生实机仍未交付；当前manifest为空。
没有修改两旧编辑器/注册源码/原包，没有新增DLL、pyc、FLS、ZIP到Git，也没有合并/发布。

### 3.19 M3可信源码清单与新包续编接线（2026-10-15，功能代码已实施，GUI未验收）

**Linux已做**：`script_editor/`升`0.3.0.dev1`，新增无Qt的`services/workflow.py`，
快照当前编辑区→保留原co_filename原始bytes→真实标准编译与完整marshal审计→
native全pyc往返→不可变预编译清单→沿用M2严格新包发布→纯元数据重基。
明确仅改当前绑定一条，不自动接线/新增模块；无负载变化不出包。
标准pyc单独导出仍用源码路径UTF8，native才用原文件名bytes，不猜字符集。
marshal树现在保留`s/t/R`标量值供文件名读取，发射原raw不变，M2全部回归通过。

GUI拆为window/project_actions/build_actions/preview；匹配选中条目、源码、VM与已验证编译器才启用原生动作。
预编译后清单显示双包来源/身份/摘要/负载变化/源码diff/带行号的静态布局与API线索，默认取消；
陈旧清单不能发布。成功承接确切新包，迁移同包其它绑定/会话基线，其它包不动；
源码文字/dirty/撤销不自动保存或清除。已发布但UI采用失败单独报告新包路径/SHA，保留旧关联。
后台期间全部动作/快捷键禁用，回调显式queued；大包解析/指纹/编译在worker。
项目后台预读全部UTF8/包，采用前拒绝同源跨VM/已开reference冲突；失败回滚新增树/标签。
这些GUI行为已写测试，但当前真实Qt不可运行，**不宣称事务/线程/交互已实测通过**。

schema2兼容schema1读，保存原文件名HEX/上次成功入包源码SHA/显式XOR目录路径、摘要和包来源；
不保存compiler路径、不复制源码/大包/keys。相对路径同盘可迁移，跨Windows盘保存绝对路径。
项目保存不代替源码保存；dirty时明确确认。diff只有会话可信文本基线；重开仅有SHA时明示不能逐行比，
不拿磁盘现文本/反编译稿伪造基线。目录读取限制16MiB，防增长竞态；生成器元数据同样保留输入别名保护。
布局/GetObject/GetChild/FONT_EDIT只是静态提示，不eval/执行、不猜非ASCII字节编码；
**未挂载interface验证控件，不做自动布局接线或资源/脚本联合保存**。

**本轮实测**：105项，91通过、14 GUI明确skip（旧6＋新8）；
含真实2.5.6/2.7.13双VM快照→预编译→发布→项目保存/重开→再编、原文件名非UTF8 bytes真实编译/回读，
schema1/2/相对路径迁移、原包/catalog变化、重复关联、错误SHA/参考稿/VM/语法/基线拒绝、
已有目标/发布失败/其它已知输入保护、未改条目与未选绑定SHA保持；core独立副本无Qt/兄弟目录依赖回归通过。
- 注册当前自写源码经4007两轮离线构建，每轮其它5001条负载不变；不修改注册源码/用户布局/account/CBox。
- 原data条目75经两轮M3工作流，每轮其它132条记录保持；**故意替换核心库的离线探针，禁止客户端/上传/交付**。
- 所有FLS只在仓库外TemporaryDirectory，测试结束删除；没有新增客户端包或编译器二进制到Git。
- ruff check/format通过；wincompat `--strict --no-git` ERROR0/WARNING0/INFO0；compileall/版本CLI通过。
  bootstrap `--check-only`因QtWidgets缺libGL正确退出2；还缺libEGL/libxkbcommon/libdbus，未造桩假验收。
- 原script/data/keys复算SHA分别仍为8b6e9266…/5f96bdb2…/43bb090d…；仅改新工具和文档。
  完整本轮日志位于沙箱仓库外`/home/user/script-editor-m3-verification/`，不作为发行物。

**Windows待验/下一步**：先补真实Qt GUI交互验收（新8项＋原6项），M3仍未完整验收；
然后M4 Windows双x86标准编译器来源/许可/全部文件哈希、随包运行、EXE与中文/空格/跨盘路径、DPI、
文件锁/硬链接、客户端加载和注册业务实机。manifest仍空；没有以Linux编译代替Windows交付。
详细使用与范围见[`script_editor/M3_WORKFLOW.md`](../script_editor/M3_WORKFLOW.md)。

### 3.20 M4准备：整套运行时审计与发行检查（2026-10-15，未交付Windows产物）

**实际实施**：`script_editor/`升`0.3.1.dev1`。确认原`bundled_compiler`仅查EXE SHA，
不能检测DLL/标准库变化；新增core/compiler/bundles.py、distribution.py及runtime_cli/release_checks。
运行时schema2记录精确版本/魔数/32bit、官方源码来源URL/commit/源码包SHA、许可路径和**所有文件SHA**。
有界JSON/重复字段/VM、非法Windows路径/越界/大小写冲突、链接/重解析点、漏件/额外文件、
PE32/x86与EXE/DLL类型、许可缺失均拒绝；CRT须有许可记录。
注册Compiler携带不可变BundlePin，每次编译/完整marshal审计前后复验整套文件及清单；
源码/标准pyc的输出保护包括全部运行时输入，显式开发编译器在GUI说明不是随包审计。
保留schema1空清单不可用兼容，但拒绝schema1非空EXE-only清单，不降级。

runtime_cli支持明确`--static`（不执行，报告static-only），默认真实Windows双VM版本/编译/完整marshal验收；
合成目标含写文件/raise但只编译不执行。stage只往不存在的runtimes子目录复制清单列出的文件，
复验源清单竞态/目标字节，失败只删除本次新建目录，不删除旧EXE/输入。
build_exe.bat在装依赖前即要求双运行时Windows实测，空manifest立即失败；
release_checks要求发现指定GUI/双编译器/native端到端测试，防止空套件假绿；
绑定随包编译器跑全测试，GUI/真实编译器skip致失败，仅6个确切外部游戏/DLL材料测试可缺失；
测试后再核验运行时，PyInstaller后精确复制/复验并记录runtime-audit.json。
没有执行Windows bat/spec，也没有把该流程写成已构建成功。

**本轮Linux实测**：129项收集，115通过、14 GUI仍因libGL/libEGL/libxkbcommon/libdbus缺失未执行。
其中新增24项明确使用合成PE头/测试文件/mock probe，只验证整套SHA护栏/复制清理/竞态/CLI/skip策略；
**这些不是可执行Windows标准编译器，没有启动这些合成PE，不能计为Windows验收**。
既有真实Linux2.5.6/2.7.13、真实双包M3两轮构建及core隔离继续通过；
ruff/format、Windows静态`--strict --no-git`零报告，compileall/版本CLI通过。
bootstrap仍正确退出2；空manifest的runtime_cli审计与release_checks均明确失败，不产出发行物。
本轮日志在仓库外`/home/user/script-editor-m4-verification/`。

**来源事实**：只读GitHub官方refs确认2.5.6 commit `11a859d70dffc8da51d346dabd1fe6a635825ae5`，
2.7.13 commit `9c1426de7521299f70eb5483e7e25d1c2a73dbbd`；核验已有codeload源码包SHA，
见[`M4_RUNTIME_DISTRIBUTION.md`](../script_editor/M4_RUNTIME_DISTRIBUTION.md)。
这是源码来源，不是Windows二进制哈希；未伪造运行时清单条目。旧vcproj/vcxproj工具链不能假定当前runner直接可编译。

**未解决/下一步**：没有Windows/Wine执行环境，没有真正标准x86双运行时或CRT再发行许可/逐文件实际哈希；
manifest仍为空（schema2）。需真实Windows旧工具链构建/合法来源审查、子进程DLL搜索路径/中文ANSI argv/跨盘、
NTFS硬链接/文件锁、14项GUI/EXE双击/DPI/退出及客户端业务验收。
整套本地哈希不等于数字签名、可重现构建证明或法律许可审核；不称M4完成/免安装交付。
本轮仅改新脚本工具与文档，不修改游戏/keys/DLL/注册源码/用户布局，不上传游戏探针，不合master。

### 3.21 脚本编辑器源码GUI测试包已授权上传（2026-10-15，历史缺件包）

> 已被§3.22的含双编译器源码ZIP取代；以下保留历史记录，不是当前交付状态。

用户明确授权“打包传到网盘我去测试”。上传前已说明这是源码测试包，不是EXE/内置双编译器发行。
新增`script_editor/先读测试说明.txt`（启动与测试边界/最小脱敏反馈），修README中遗留的“只复制空清单”旧构建说明。
独立工具全部从提交`7f3414e8242d1ed2e6f418d0d9cc89a89eb4e692`取材，打包bat恢复ASCII/CRLF。
新增包内PACKAGE_MANIFEST.json记录来源提交与逐文件SHA；无游戏/FLS/DLL/EXE/keys/探针/本地日志或缓存。

- 文件：`MXSJ_ScriptEditor_0.3.1.dev1_source_test.zip`，86文件，135692字节。
- SHA256：`45638bb94756f2e43a39883e536b2c0df58a1018ffe5d711f86686e9756b3b05`。
- MD5：`e6cda49d6a1f186ebdeb16a54af4fac5`；Drive返回MD5/size与本地一致。
- 网盘：https://drive.google.com/file/d/135Wg6izLhOVzQ4H9e5-L3273_6DiUrhi/view 。未修改分享权限。
- 解压到仓库外独立目录复测：129项，115通过，14 GUI因真实Qt系统库缺失未执行；
  ruff 0、版本CLI0.3.1.dev1、包内逐文件SHA全匹配，ZIP CRC全过。
  真实双编译器与游戏材料测试仅通过显式环境变量启用，不是运行时自动寻找仓库。
- 产物和日志仅在仓库外`/home/user/script-editor-0.3.1-delivery/`，没有把ZIP/编译器加Git。

用户解压先读说明，双击启动bat；需已有Python3.10+，自检尝试安装PySide6。
这轮可测双包索引、源码编辑/撤销/查找替换/关闭与只读保护；缺已验证开发编译器时原生写包不可用。
script关联还需用户显式提供匹配包的研究目录，不猜key，不拿游戏DLL或反编译稿替代。
当前空runtime清单使build_exe.bat明确拒绝发行构建；不要把源码GUI测试当Windows免安装交付。
M4真实Windows运行时/许可/EXE与M3 GUI实测仍待完成，不重传旧font1/diag2或游戏验证探针。

### 3.22 补齐双Windows编译器并重新打包上传（2026-10-15）

用户明确要与UI/资源编辑器一样的**独立源码包**，由包内脚本自行构建编辑器EXE；
这次修补的是缺失的两套编译器，不再给空manifest的替代GUI包。
先推送维护者构建脚本检查点`188b16d`，再推送产品代码`efeddeafcadf5ddf999567dfbfe59f15e2241a02`。

**补齐的真实构建物与产品变化**：
- 从固定官方源码交叉构建标准CPython2.5.6/2.7.13，Zig0.13.0、x86-windows-gnu；
  分别156/178个官方core编译单元，0失败。4个EXE/DLL均为真实PE32/i386，非合成测试PE或游戏DLL。
- 两套各9个文件：EXE、DLL、ZIP_STORED纯Python标准库、BUILD.json及5份原许可；
  schema2清单现非空，全部18个文件实际SHA/官方归档URL/commit/归档SHA齐。
  2.7.13归档SHA已按本次实下纠正为`ae1dc735e2990bf8de8e73c3f77b35d4f69502570957c743a7e8618a652fe08a`。
- 只改MinGW平台适配（posix分支、私有strcasecmp名、Windows.h大小写），每文件前后SHA写BUILD；
  compiler/opcode/marshal未改。原许可含CPython、Zig、MinGW、LLVM、zlib。
- 目标Windows10/11系统UCRT，不再分发微软CRT，不支持XP/Win7；这是compiler-only运行时，
  非含全部外部扩展的通用Python2发行。维护者可用`build_runtimes.py`重建，普通用户不需要Zig。
- GUI开窗后后台自动探测两套精确版本/魔数/x86/整套SHA，无需先打开源码选EXE；
  失败显示诊断、禁用对应编译，不阻止源码阅读编辑。新增无Qt依赖的`检查内置编译器.bat`；
  bootstrap的check-only也做真正双编译/marshal验证。build_exe仍严格拒绝GUI/编译器skip和缺件。
- 二进制保持gitignored，只随交付ZIP；不改原游戏/keys/注册源码、布局/account/CBox或旧编辑器。

**实测与未验范围**：
- 重新构建真实Linux2.5.6/2.7.13作为回归编译器；134项118通过、16 GUI因libGL缺失未执行（3.353s）。
  显式启用只读游戏/DLL材料；全套包括两VM原生包/注册项目续编回读，原包/keys SHA保持锁定值。
- ZIP解压到仓库外含中文/空格的独立目录：134项112通过、22 skip（16 GUI＋6 opt-in材料，1.687s）；
  不携带游戏材料，只通过显式环境变量使用回归编译器，不依赖仓库兄弟目录。
- 18文件整套静态审计通过；ZIP CRC及全部109个交付文件SHA清单一致；
  解压副本wincompat walk 109文件/72源码脚本，ERROR/WARNING/INFO均0；ruff0且77文件format通过。
  bootstrap正确退出2/写日志（Qt系统libGL缺失），不把未执行当通过。
- Windows CI尝试run38662087057在分配job前startup_failure；试验工作流已移除。
  Wine源码构建实验也未得到可执行环境；均没有Windows运行证据。
  **真实Windows启动/编译/marshal、GUI、EXE自构建/双击、中文跨盘/文件锁及客户端仍待验证**。

**已上传的新交付**（只上传这一份工具ZIP，不重传旧包/探针、不改分享权限）：
- `MXSJ_ScriptEditor_0.3.2.dev1_source_with_compilers.zip`，109文件，**7114401字节**。
- 源码提交：`efeddeafcadf5ddf999567dfbfe59f15e2241a02`。
- SHA256：`17194fd1f1df20e656f0919fff07ef47b8663e05175837eba1c3557efcaaf8cf`。
- MD5：`19ee695bfc4b94f3fbeac21b3fea0876`；上传后重新读取Drive元数据，MD5与size均和本地一致。
- 网盘：https://drive.google.com/file/d/1yb1JsQbnWgremYR5u1-aQlwFjOWPSFO_/view 。
- 包内附`先读测试说明.txt`、`SOURCE_DELIVERY.json`、`PACKAGE_SHA256.json`与明确static-only的审计记录。
  源ZIP/构建工作区在仓库外缓存；源码与构建方法已Git保存，ZIP/编译器没有加入Git。

用户完整解压到新目录，先双击检查内置编译器bat，再启动GUI；需EXE时自行运行build_exe.bat。
不需要另装Python2；源码启动/自构建仍需Python3.10+及PySide6。源码交付形式本身符合要求，
剩余问题是Windows实测，不再把“必须由助手给成品EXE”当作验收条件。

### 3.23 脚本编辑器工作区重整（2026-10-15，代码初版/仅预览）

用户明确指出0.3.2“这么简陋”，原菜单＋三栏文本框不能当成完整编辑器交付。
先提交/推送检查点`0d18214`，再实现0.4.0.dev1；未重新打包上传，不把旧网盘链接当新版。

本轮实际改动：
- 工具栏与菜单复用同一QAction，打开包/源码/项目、保存、撤销重做、查找、关联、生成新包、
  编译器检查可直达；按来源/关联/VM/任务状态启用，不新增空按钮。
- 可停靠包导航、来源属性、大纲、底部检查台；视图菜单隐藏/恢复默认；正式入口QSettings只保存
  窗口/面板布局，测试注入独立设置，不污染用户偏好或自动重开游戏文件。
- 包选择器明确切换script/data，原包只读；显示0基下标与真实记录身份，不猜模块名；
  已关联者标注来源文件，双击打开对应源码，切包不自动改源码VM或关联。
- 源码标签带路径/来源/VM，等宽字体、当前行、四空格Tab/选区缩进、自动缩进、三引号状态高亮。
  UTF-16位置处理兼容非BMP字符；选区缩进、全部替换仍一次撤销，参考稿各入口只读。
- Ctrl+F区分大小写/整词/双向循环查找、当前/全部替换；类/函数分层大纲和布局/控件引用可定位行。
  只做词法线索，兼容Py2 print语句，不AST执行/恢复代码，不声称挂载/语法已通过。
- 差异明确比较打开时文本与编辑缓冲区，保存不伪造原包文本基线；分析延迟合并，
  大型源码停止自动扫描；超长差异明确标注截断，不改变实际编译文本。
- 工作区拆分成独立装配/菜单/行为/源码标签模块；后台任务同时禁用停靠区交互并恢复原状态。
  原包只读、可信源码、双VM隔离、严格预编译/新名发布/回读护栏和编译器文件完全未放宽。

**真实GUI环境与现场发现**：
- 原沙箱缺GL/EGL/xkbcommon/dbus，现用真实GLVND1.7.0、D-Bus1.12.24及OpenCV wheel里的真实
  libxkbcommon补齐进程本地依赖；不是桩库、不修改系统PATH，不随产品分发Linux库。
  私有测试依赖与日志保留`/home/user/script-editor-test-environment/`，PySide6安装仍在外部venv。
- PySide6 6.12.0/Python3.11.2的最小QTreeWidgetItem循环复现None计数每条减2并崩溃；
  不是原包损坏。已固定6.10.3并实测6000节点，bootstrap识别/修复不匹配版本，
  直接GUI入口也拒绝其它版本；源码Python支持范围明确为3.10—3.14。
- 6.10.3下枚举临时menuAction会释放C++菜单/分隔符；已显式持有菜单、menuAction和dock action引用。
  原有菜单/禁构建测试真实复现失败后修复，不是改测试绕过。

**本轮实测**：149/149全执行通过，含26项GUI及真实Linux2.5.6/2.7.13编译、只读原材料与
两轮原生新包/项目回归（最终3.754s）；无GUI skip。新增15项：工作区/来源/导航、缩进/高亮、
引用/差异、搜索撤销、6000节点、Qt版本拒绝以及纯核心词法大纲。
ruff0、84文件format通过；wincompat95文件/79源码脚本，ERROR/WARNING/INFO均0。
18文件双Windows运行时静态审计仍过，原script/data/keys SHA保持锁定值。
bootstrap现在真实加载Qt后正确退出2：非Windows禁止执行Windows运行时，不再是缺Qt库。

真实预览：`/home/user/MXSJ_ScriptEditor_0.4.0_workspace.png`，由实际Qt程序抓图，
打开只读script/data与已有作者源码；编译器为显式选入并验证的Linux开发版，不冒充Windows执行。
**0.4未重新打包/上传；Windows双编译器、GUI、EXE/客户端验收仍待。**
当前先提供界面方向预览，不再把测试数量当作界面完整性或成品交付的替代。

### 3.24 工作区重整源码＋双编译器正式上传回执（2026-10-15）

用户明确授权“提交推送上传”。功能提交`4655c77`，交付说明提交并推送
`0216b58f80c327f0373455e39633143f602f7cd4`，按此提交的script_editor完整tracked文件
打包，额外仅加入manifest指定的18个真实Windows运行时文件、静态审计和来源/SHA清单。
所有bat规范化CRLF。§3.23的“仅预览/未上传”为历史检查点，现由本回执取代。

- 新文件：`MXSJ_ScriptEditor_0.4.0.dev1_source_with_compilers.zip`。
- Drive：[下载0.4.0源码＋双编译器](https://drive.google.com/file/d/1QNXpgwiGECqh377UN2npCNNTh32AGAvn/view)
  （ID `1QNXpgwiGECqh377UN2npCNNTh32AGAvn`，与旧包同一My Drive根目录，旧包保留，不改权限）。
- 116文件，**7,130,558字节**；上传后另调get_file，大小和MD5与本地相同；未再次下载。
- SHA256：`d4f417c142657aafa29ede993d5fcb807161b002e30e782a0d31a71dd4f3f9ed`。
- MD5：`1c5338c7427e709aa3793cfb550afea7`。
- 本地交付：`/home/user/deliveries/script-editor-0.4.0/`，含ZIP及receipt.json；不进Git。

交付前复跑仓库**149/149全通过**（4.879s，26 GUI，无skip）。ZIP完整解压到仓库外
含中文/空格的新目录，清除MXSJ_M2_REPO、只用自身src再测：149项中**143通过、6项外部游戏
材料测试按设计跳过**（2.083s），26 GUI全部执行，真实Linux双编译器及核心原生新包回读通过。
独立源码ruff通过；Windows兼容严格扫描121条目/79源码脚本，0 ERROR/WARNING/INFO。
本地ZIP CRC、精确文件集合、每个文件SHA、18运行时文件已在上传前/后核对；
解压后静态SHA/PE/来源审计也通过，未混入缓存、启动日志、游戏材料或Linux测试依赖。

交付是**独立源码测试包＋内置CPython2.5.6/2.7.13 Windows x86编译器**，不是编辑器EXE。
Windows端先完整解压到新目录，运行“检查内置编译器.bat”，再运行“启动脚本编辑器.bat”；
需要EXE时用户运行build_exe.bat，实际双VM/严格GUI检查不通过仍禁止构建。
Windows双编译器执行、桌面、EXE/客户端验收仍待；不把Linux结果或静态审计冒充通过。

### 3.25 Windows刚打开即误报源包变化修复（2026-10-15，0.4.1.dev1）

用户在0.4.0实机看到“源包打开后发生变化或被替换”，进一步确认**刚打开就报**。
不能据此认定用户改包。排查并对照官方CPython3.13/3.14源码：
`Modules/posixmodule.c`的win32_xstat把ctime重映射成birthtime；
`Python/fileutils.c`的_Py_fstat_noraise经FileBasicInfo保留实际ChangeTime。
因此ArchiveDocument将path.stat()与reader的fstat五元组直接比较会误报；
用户Python精确版本尚未知，但代码问题与触发症状一致，不需要先让用户反复重新打开。
源码依据：[CPython3.13 posixmodule](https://github.com/python/cpython/blob/v3.13.0/Modules/posixmodule.c)、
[fileutils](https://github.com/python/cpython/blob/v3.13.0/Python/fileutils.c)。

修复：
- FileReader的大小/初始修订同次fstat捕获，ArchiveDocument不在初始化中重新把变化当新基线。
- 新增path_revision：重新只读/二进制打开当前路径，同一fstat接口核对身份、大小、mtime/ctime，
  临时描述符在finally关闭；原句柄前后复核仍在，不能只看旧句柄或去掉inode/时间检查。
- revision与close共用锁，初始化快照失败也释放原描述符；不改源包、不改编译器或GUI工作流。
- 版本0.4.1.dev1；新的Windows差异回归列入build_exe严格必跑集合。

新增5项：模拟路径/句柄ctime/身份命名差异的不变文件、相同元数据下路径身份改变、
句柄变而路径快照伪装未变、FileReader打开后初始化前变动、临时快照失败释放句柄。
先跑旧码，ctime/身份差异两子用例复现同一ContainerError，且打开后重设基线用例未拒绝；
修后5/5通过。其它新API相关旧码失败不冒充已有行为缺陷证据。
完整Linux154/154（26 GUI、真实双Linux compiler/只读材料）全执行通过，4.238s。
模拟Windows差异不是Windows实机执行；不重新给0.4.0链接当修复版。

**0.4.1交付回执**：
- 修复与随包源码：`661efe3e858565bf29aaba428a78e2594c2ce523`，已推送固定分支。
- [下载0.4.1修复源码＋双编译器](https://drive.google.com/file/d/1xnMZls3kZmylUHZi8sRrcvlvnt4bU9fQ/view)。
- 文件`MXSJ_ScriptEditor_0.4.1.dev1_source_with_compilers.zip`，117文件，7,132,907字节。
- SHA256：`ef5f7a4a308b52d9bfeb5af7dfecec1720ae3859a7fe07fcd77d23551d26c5b3`。
- MD5：`61eac4d24c136a2eb0522961acb67df2`；上传后另调用get_file核对大小/MD5一致，未再次下载。
- 与旧包同一My Drive根目录；旧包保留、分享权限未改。仍为源码＋两套18文件Windows x86
  compiler/标准库/许可/清单＋自构建EXE脚本；不含游戏、keys、离线探针或Linux测试依赖。
- ZIP CRC、精确文件集合、逐文件SHA通过；双运行时静态审计复过，编译器本身未改。
  独立解压到仓库外中文/空格目录，仅自身src、取消真实材料环境：154项148通过，
  6项材料测试按设计跳过，26 GUI全执行，2.222s；ruff/严格兼容122条目80源码，均0。
- 本地`/home/user/deliveries/script-editor-0.4.1/receipt.json`保存交付核对；不进Git。
- 提醒用户完整解压到新目录，确认版本0.4.1.dev1再打开自己的原包；不要改原包元数据、
  删除保护、换游戏DLL或覆盖旧工具目录。Windows修复效果仍待实机确认。


### 3.26 补真正包内脚本读取与恢复编辑（2026-10-15，0.5.0.dev1开发中）

用户发现所有未关联条目都提示先提供自己的源码，并进一步质疑“残次品，不能编辑源码有什么用”。
已承认0.4只是有源回编器，不满足用户从包内打开现有脚本编辑的目标，不再拿信任限制或UI重整代替功能。
本轮先push既有检查点，再补包内工作流；**未上传0.5候选、未提供旧链接冒充新版或宣称功能全面**。

已实现：
- 未绑定条目双击后台严格解码成标准pyc，调用独立30秒限时进程恢复；三页中央工作区为
  可编辑恢复草稿/反汇编/来源诊断。失败显示具体缺参数/未知映射/坏格式与存储预览，不造pass源码。
- 草稿可撤销/查找/显式字节转换/另存新UTF-8.py；新文件原子拒覆盖及竞态，原参考页仍只读。
  草稿可编辑但不自动绑定，不准直接原生发布。重新打开带草稿/VM标记的文件也仍未核验。
- 检查并采用：VM/条目/来源指纹核对→真实标准编译→原生往返全字节回读→人工确认业务逻辑，
  才标记recovered-reviewed并建立关联；未修改的部分恢复输出直接拒绝采用。
- 关联新增source_kind/recovery_sha256，schema2兼容缺省authored，拒绝未核验草稿/未知来源入关联；
  项目重开保留恢复来源，清单显示原标准字节码SHA，不把恢复稿称作原始源码。
- 已读嵌入文件名可在树标签显示/筛选，原始文件名字节仍无损保留，不用于猜模块身份或写磁盘路径。
- 继续原有F6不可变清单、每轮新名/只读原包、未改条目保留、完整回读及项目承接，原生codec未改。

恢复引擎：uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser1.9.0 / six1.17.0 / click8.5.0固定依赖，
bootstrap只查分发元数据不在GUI导入引擎；主进程只以标准pyc/JSON文件调用独立GPL worker。
GPL worker单独spec/EXE，主GUI明确排除其引擎；build_exe新增独立程序、完整上游对应源码/许可归档，
最后实际双VM恢复EXE smoke，任何失败阻断；**本轮没有Windows构建或执行，不能称这些已实机验收**。
新增源文件许可及上游全文在licenses/recovery，原主编辑器权利不自动改成GPL。
输入先核心限量marshal验证；超64MiB存储不加载全条目，仅预览；worker输出限长/协议验证/无stdout污染。

现场修复真实输出问题（不改VM指令/编译器/原加密边界）：
- uncompyle6在Python3宿主给2.5字符串输出b前缀，合法2.5不能编译：仅按token移除b，保留字节内容。
- 部分模块尾隐式LOAD_NAME None被输出为非法顶层return：只处理最后的顶层bare return/return None，
  不碰函数return/表达式返回值。
- xdis6.1.8的UnicodeForPython3.__repr__丢前两字并错误输出u'\u'；在独立worker中修正常量显示，
  Unicode以正确u+ascii转义，不改常量值，兼容future_unicode_literals，不修改安装的库文件。
  新增中文/引号/反斜杠/非BMP/字节常量的真实双VM编译并解析marshal核对值，不只是断言能编译。

真实回归：新增13项，合计**167/167全执行通过，30 GUI，无skip**，8.438s。
- 合成合法模块由真实双compiler编译，包内恢复/编辑/两轮读取和来源项目重开；带副作用sentinel但绝不执行。
- Qt真实worker从未关联条目进入可编辑草稿，取消另存/拒绝采用/明确采用/F6发布及项目重开，双VM均过。
- 真实原包script下标4007和data75直接恢复（不取作者.py），编辑后回编/新包回读通过；未改5001/132逐条全等。
- script4007原样恢复稿回编**超过原固定展开长度10字节**，没有放宽护栏；隔离回归明确缩短常量后
  验证在原边界内可写。**这不是任意模块任意改动都能写回的证据，更不能隐藏固定长度限制**。
- 失败/缺catalog/资源条目、VM/marshal拒绝、timeout、发布竞态及未核验关联拒绝均有回归。
ruff0、92文件格式通过；严格兼容109条目/86源码脚本，ERROR/WARNING/INFO均0。
实际调用发行入口`python -m script_editor.release_checks --root script_editor`，返回2并明确
`Release blocked: Windows运行时执行验收只能在真实Windows进行`；未伪装平台/替换发行编译器绕过，
因此167项是Linux开发环境测试通过，不是Windows发行检查通过。
真实Qt恢复视图已抓图并查看：`/home/user/script-editor-recovery-workspace.png`，实际双包、原4007恢复草稿可编辑、
无源码关联、无目标执行/写包；编译器为显式Linux开发版，不是Windows实测证据。

**未解决/待授权**：
- 工具目前仍不附匹配script.fls的XOR参数表。为了用户开包即可读取，需要明确授权将既有固定原包
  对应的逐模块解码参数与工具交付；不擅自把“只传工具不传keys”的旧边界改掉。
  未授权前不复制/上传参数、不猜key；data恢复本身不需要该目录。下一步只询问这个交付决定，不让用户重新决定核心功能。
- 未知映射/分段失败/反编失败只诊断，不保证全部恢复；script超过固定长度仍拒绝，未做lnotab裁剪或猜边界。
- 尚无全包模块名扫描/恢复覆盖率批处理；Windows恢复EXE/GUI新流程/客户端语义仍待验。
- 当前0.5为已提交开发进展，不是已完成“功能全面”的新发行包；旧0.4.1只有开包误报修复。

### 3.27 已授权附带固定原包参数，0.5独立源码测试包已上传（2026-10-15）

§3.26核心及回归已在8d6ee2d/09414c6提交推送。之后询问唯一阻断交付的参数授权，
用户明确选择**“允许附带匹配的解码参数”**，不是要求其提供源码，也没有授权上传游戏包。
据此把原有已知SHA的参数原样复制到工具自身decoding/script-original.json，独立运行不读仓库tools。
自动使用条件为整个原包SHA和参数文件SHA同时精确匹配；data不需要；其他包不按名字/目录猜测。
派生包使用已验证项目关系，或显式确认来源选取JSON后逐模块严格校验；保留固定边界/未知拒绝。
打开包的SHA计算在后台，不冻结UI；缺/坏参数不隐藏包索引，诊断明确且不套错误参数。

新增参数audit/stage CLI及Windows构建复制复查，缺件/摘要错/目标已存在阻断；参数不进入运行时清单，
两套compiler仍按原18文件独立清单。新增3项参数匹配/篡改/拒覆盖回归，1项实际Qt开包自动匹配后
无外部源码恢复编辑回归；发行检查强制此GUI用例和内置参数摘要。真实4007/data75回归已改用工具
自身参数自动匹配，不再读取tools目录。

当前全套**171/171，无skip，8.781s，31 GUI**；ruff0/96文件格式全过，严格兼容114条目/89源码脚本
ERROR/WARNING/INFO均0；原包script/data和原参数SHA未变。真实Windows发行检查仍因非Windows返回2，
没有降低门槛。已从提交快照打独立源码＋完整双Windows编译器＋参数ZIP，中文路径隔离解压回归、
静态审计与逐文件清单复核通过，上传原网盘父目录，不改分享权限。

**新交付（不是旧0.4.1）**：
- 源码提交`f899babe598710a8ea18cf8900dfc4698337ed3f`，0.5.0.dev1，135文件，7,294,512B。
- 文件`MXSJ_ScriptEditor_0.5.0.dev1_source_with_compilers.zip`；SHA256
  `919f4c48d90c88b08f3f09a81050b7fe12c5515c2e92f9bf9a42b28e14598aaa`；
  MD5 `a21c334f61bf4c0fb74ba8b27284efb4`。
- Drive ID `1-1PNBSZb_5Kt5ziy9WTn-P2wfZa_8ESc`，父`0AM2SnEVIISYdUk9PVA`；
  https://drive.google.com/file/d/1-1PNBSZb_5Kt5ziy9WTn-P2wfZa_8ESc/view
- 上传后独立get_file重查名字/父/大小/MD5，均与本地一致；没有修改权限、覆盖旧网盘文件或上传游戏包。
- 源目录/ZIP/本地回执：`/home/user/deliveries/script-editor-0.5/`；逐文件清单与SOURCE_DELIVERY.json在包内。
- 中文路径隔离解压：171发现，**164通过、7项明确外部材料skip**，31 GUI全过；skip集合精确等于
  release_checks许可的7项，未将skip算通过。所有134清单项再核SHA；完整双compiler18项静态审计不变。
- 额外用解压后的实际Qt（确认导入路径不指向仓库src）打开原script4007和data75，
  使用工具自身参数自动匹配，不打开作者.py，不手动关联参数，二者均进入可编辑未核验草稿；
  无bindings、无目标执行、无写原包。恢复worker也来自独立解压目录，不依赖tools。
- 日志`/home/user/script-editor-test-environment/module-browser-isolated-tests.log`；
  验证`release-0.5-isolated-verification.json`；完整开发171通过日志仍`module-browser-all-tests.log`。
- Windows compiler执行/独立worker EXE构建/新GUI客户端语义仍待用户Windows测试；
  本包是源码自构建交付，不声称已提供/验证EXE或全部模块都能编辑回包。

### 3.28 修复0.5.0把Python3.14挡在启动前（2026-10-15）

用户提供真实Windows/Python3.14.7日志，pip明确xdis6.1.8 Requires-Python>=3.6,<3.13，
bootstrap却支持3.10—3.14且把全部恢复依赖当GUI强制前提。错误是本工具的宿主依赖配置，
不是网络/用户操作；不建议继续换源、重复必失败命令或--ignore-requires-python强装。
开工先核对远端：本地快照HEAD回退到fa13871但所有文件逐字节等于远端a98222f；
fetch确认后仅mixed reset恢复同分支索引/HEAD，没有hard reset/删文件；push up-to-date后开工。

修复：
- uncompyle6 3.9.3还限制xdis<6.2，不能只升级xdis。使用上游已适配xdis>=6.3/列出Python3.14
  的固定提交`91298ba80e322cfb8736ab8a697509527297a7a9`（2026-10-05，版本3.9.4.dev0），
  不冒充PyPI正式发布版或修改上游依赖声明。配xdis6.3.0，spark/six/click原固定版本不变。
- 上游完整未改源码随third_party，1,294,429B，SHA256
  `9e60958d4b0386e3976331ba6236ef2a1a986b2a162f3ddb9a8db424ae2e4d87`；
  bootstrap核摘要再以本地file URI+#sha256正常pip安装，安装后校验版本/PEP610来源摘要，
  不让其他同版本dev提交混入。Windows构建/GPL对应源码归档也取同一份，不再下载失配的3.9.3。
- GUI依赖/恢复依赖分开；Qt失败仍阻开窗，但引擎安装失败允许打开已有编辑器并说明恢复暂不可用。
  --check-only/发行仍失败，不能假报引擎就绪。安装错误不再统一误导为网络故障。
- worker适配xdis6.3的PythonImplementation枚举接口；其新compat_str errors=ignore会丢非UTF8字节，
  在独立进程内恢复严格UTF8、失败保留原bytes的读取行为，不改安装文件或原常量值。
  原Unicode输出保护继续存在；新增集合值及全部256字节的恢复回编核对。

真实对照暴露旧引擎**严重来源正确性问题**：0.5.0的3.9.3将4007身份证校验列表实际值
误渲染为常量下标，例如A=[3,4,5,...]、code=[15,16,...]，编译/原生回读都不能发现这种业务错误。
新版上游恢复为原列表值/字符串，独立回归断言此内容；不为了满足固定容量回退到错误恢复结果。
正确恢复4007原样回编44411>44362（+49），即使缩短旧占位仍超容量，必须拒绝。
真实回包证据改用业务数据script4001：明确缩短展示文字常量（不是任意增长），与data75均回编/新包
且5001/132未改；4007单列正确恢复/容量拒绝。旧0.5.0的“回包通过”不能当恢复语义正确证据。
UI打开旧3.9.3恢复稿显示警示，保留原文/可编辑/项目状态，不自动覆盖用户修改或降级其已确认身份；
建议保留已有.py/项目副本，新版重读原包后对比合并并重新核验。

本轮在真实标准Linux CPython3.14.7（与用户相同宿主版本）新建venv：正常pip完整解析/构建安装
上游源码＋xdis6.3等，pip check通过；又实际卸载引擎后运行bootstrap自动补装及--version，
再次启动不重复安装，均成功；不以mock/换版本代替安装证据。
3.14.7 **184/184、32 GUI、0skip、10.790s**；3.11 **184/184、32 GUI、0skip、7.408s**。
真实双VM标准compiler也从固定官方源码构建，目标仅编译/反汇编/回读，从不执行游戏代码。
Qt使用真实本地系统库与官方wheel，测试依赖仅沙箱使用，不进工具包。
新增bootstrap8测试、集合256字节1测试、真实容量拒绝1测试、旧稿保留GUI1测试；旧测试未删。
引擎失败允许开窗不表示旧引擎仍可恢复：worker先核对版本/来源再读目标，缺件/旧版本拒绝；
父进程校验协议标签防止旧EXE混用，冻结spec显式复制版本/来源元数据，构建安装后重核来源。
新增错版本/旧协议/严格install-only三项回归，正常UI降级不会偷偷调用不兼容引擎。
wincompat误把Distribution.read_text当Path默认GBK，按其明确UTF8 API作精确豁免，保留Path规则并增反例；
devkit30/30通过，ruff0，98文件格式通过，严格117条目/90源码脚本ERROR/WARNING/INFO均0。
发行入口实际返回2：Windows运行时执行验收只能在真实Windows进行；未伪装平台绕过。
日志均在`/home/user/script-editor-test-environment/`，all-py314.log/all-py311.log、
python314-pip-install.log/bootstrap-py314-auto-install.log/recovery-core-py314.log。

两套Windows交付编译器本地缓存缺失，本轮用原build_runtimes/官方源码/Zig0.13重建，compiler/opcode/marshal
未改；18项许可/标准库等仍齐全，4个EXE/DLL摘要改变，manifest已如实更新，静态SHA/PE32来源审计通过。
仍不是Windows启动证据。已从提交快照打独立源码＋双compiler＋既有授权参数新ZIP，中文路径隔离复核后
传原Drive父目录，不覆盖旧文件、不改权限、不传游戏包，回执如下。

**0.5.1实际交付回执（新的修复包，不是旧0.5.0）**：
- 源码`130269aa15234fc152bf0e6a83d964a9ecd8da5b`；文件
  `MXSJ_ScriptEditor_0.5.1.dev1_source_with_compilers.zip`；138文件、8,291,306B。
- SHA256 `ad513b083412cf955ee546312413badbcc0603802e3947fcda954617acaa7ba6`；
  MD5 `c781c88d5c49b4a3d1e76211f65df0b6`。
- 新Drive ID `18gthjpPO5oxp6IGYX5G3tqp8nrQOlMTN`，父`0AM2SnEVIISYdUk9PVA`；
  https://drive.google.com/file/d/18gthjpPO5oxp6IGYX5G3tqp8nrQOlMTN/view
- 上传后独立get_file复查文件名/父/大小/MD5一致；未改分享权限或覆盖旧文件。
- `/home/user/deliveries/script-editor-0.5.1/`保存新包/源目录/回执；中文路径隔离副本
  `isolated 中文 工具 test/MXSJ_ScriptEditor_0.5.1.dev1`；从副本导入工具src，不依赖仓库兄弟目录。
- 隔离真实3.14.7发现184，**176通过+8明确外部材料skip，32 GUI全过**，5.541s；skip集合逐项
  精确等于release白名单，不把skip算通过。137项清单再核SHA，双compiler18文件静态审计/授权参数/上游源码SHA均过。
- 又实际卸载引擎并从中文路径副本运行bootstrap，自动安装本地URI+#sha源码成功；第二次启动直接就绪，
  输出0.5.1.dev1且不重复安装；pip check通过，未采用--ignore-requires-python或--no-deps绕过正常解析。
- 独立日志`isolated-py314.log`及`isolated-bootstrap-install.log`在上述测试环境目录。
  用户应完整解压新目录，运行原名启动bat；保留已有.py/项目，旧恢复稿先对比合并核验，勿覆盖修改。
- Windowscompiler执行/EXE构建/客户端语义仍未验；源码包内保留真实严格构建/协议/容量拒绝，不宣称全面完成。


### 3.29 用户授权合并两条工作线（2026-10-15）

- PR #32 已先行合入 `master`（`c025e0822b4c679731c8cd02a76675f445e19e76`）。用户随后明确授权本会话分支也合入主线。
- 冲突取舍：启动器相关工具及注册 `register.py` / `harness.py2` / `tests/test_runtime.py` 保持 PR #32 版本；`script_editor/` 整棵源码树与已交付修复版分支 `b271095` 完全一致。注册构建器保留本分支的确定性 authored-marshal 回读，避免对自写源码使用启发式边界修复。
- 5 个冲突文件均已处理；注册文档并列保存新交付记录与历史警告，状态记录保留双方事实。未覆盖用户布局、原始游戏包或 `mxLauncher.exe` 本地原件，未重新打包/上传网盘。

**本次集成实测（Linux Python 3.11.2，不冒充 Windows）**：

| 套件 | 发现 | 通过 | 跳过 |
|---|---:|---:|---:|
| script_editor（含 32 项真实 Qt offscreen GUI） | 184 | 184 | 0 |
| resource_editor | 118 | 118 | 0 |
| ui_editor | 204 | 203 | 1（未提供完整 `.dlg` 语料库） |
| registration（真 CPython 2.5.6） | 42 | 42 | 0 |
| decompiler | 66 | 66 | 0 |
| data-parser | 24 | 24 | 0 |
| devkit | 30 | 30 | 0 |
| server architecture | 161 | 161 | 0 |
| **合计** | **829** | **828** | **1** |

- 真实标准编译器为从官方 GitHub tag 在仓库外重建的 CPython 2.5.6 / 2.7.13（`-O0 -fno-strict-aliasing`）；双 VM 恢复/编辑/编译/原生新包回读回归均通过。Qt 系统依赖在仓库外补齐后重新完整运行，之前因缺库的跳过/导入失败不作为最终通过依据；测试环境 Linux 库未加入产品。
- 注册完整构建成功：源码 SHA-256 `c2682b109d6850d9d8623401193d380400c8f15a7797254c4b2c95bee4f6810a`；生成 `script.fls` 为 24,264,817 B，SHA-256 **`f0253c9536d95e0a82642eb1a109d16bbdd07eeaf7aae2504e747d25cdf0e1f6`**，与对方最终版本记录一致。构建器验证只改 337/4007、337 仅 9 字节差异、完整 compiled marshal 回读与自写模块 2.5 冒烟通过，其他 5,000 条压缩负载全等。产物仅在仓库外验证，不入 Git/不替换原包。
- `ruff check script_editor tools/devkit/wincompat/pysource.py tools/devkit/tests/test_wincompat.py`、98 文件格式检查、Windows 静态检查（117 文件名 / 90 源码，0 ERROR/WARNING/INFO）、来源映射与 CSV `--check` 均通过。`bootstrap.py --version` 验证 Qt/恢复引擎依赖就绪并输出 0.5.1.dev1。
- **预期阻断**：Git 仓库不含被忽略的 Windows 编译器二进制，本次 `bootstrap.py --check-only` 返回 2 并指出 runtime 缺失；不绕过检查、不把仓库克隆冒充完整源码交付 ZIP。已上传的 0.5.1 ZIP 仍以 §3.28 回执为准，无需重传。
- 原输入 SHA 复核不变：script `8b6e9266…`，data `5f96bdb2…`，匹配参数 `43bb090d…`，启动器原件 `3eeba17e…`。本次不执行游戏或恢复出的目标代码。
- **未修/待验边界**：PR #32 生成工具的 report 路径覆盖、签名剥除误删额外 overlay、PNG 填充失败前写盘问题仍存在；本次遵用户决定保留其版本，不宣称已修。脚本编辑器 Windows EXE / 客户端验证仍待，用户对注册版本的实测确认不等于整个编辑器已验收。



### 3.30 双引擎恢复集成第一段（2026-10-15，本分支开发中）

- 本轮固定分支 `arena/61deb9e5-mxsj-tw-2022`，起点 `8212b26`；先提交推送检查点 `a2492a3` 后开始实现。研究方继续跑语料，本方不重跑全量、不修改 decompiler 被钉的工具或原包；不改已实测注册/启动器，不自行合并或上传新包。
- 网盘主样 446,379 B / SHA `a778c5fd6d3624e91ed0786382c17f9f8e156c9529f3d19fb43bc19dee1689dc`，失败补样 58,020 B / SHA `4920b41cb962241e0d4bf1b98123666de78ecd96094102b5a24ecde6cef0b797` 均独立下载复核。只使用 manifest 的 archive SHA + entry 编号和标准 pyc 的 artifact SHA，不按文件名猜身份，不执行其驱动或恢复源码，1288 排除记录不生成内容。材料留仓库外 `.cache`，不入 Git/发行包。
- 新开发版本 0.6.0.dev1：后台保留独立 uncompyle6 / pycdc 候选；主引擎失败/超时不丢第二引擎；部分、双失败、只有头注释等明确分类。候选可另开编辑标签，重复打开/取消均保留已有编辑。新增逐流输出限额、可取消的进程传输、POSIX 进程组回收；Windows 路径未实测。现有标准编译、来源核验、原子新包、容量与完整回读护栏不变。
- pycdc 经上游 LICENSE/README 实核为 **GPL version 3（不是 MIT）**，独立进程、不与 GUI 链接。完整官方源码归档 commit `b4289760970dbc399684f1e155ec6d1ea1cc787e`，373,111 B / SHA `d7d8c53d37a1a586097145b532fca02535db2f2f0999b3b1e910133c9941bf31` 已附源码树。两次真实 Linux CMake 构建二进制 SHA 均为 `84573109081562e70ace38b6850f581276dcc33401be6d23e55e0486c8d4eeb4`，与研究方记录一致。加载核二进制/完整源码/GPL许可摘要，不用 PATH 或游戏 DLL。真实 staged 副本校验及恢复通过；Windows EXE stage 新增第二引擎与完整对应源码复制、实际双 VM smoke 门禁，未执行 Windows 构建。
- 不回退编辑器的引擎依赖：继续固定 u6 3.9.4.dev0＋xdis6.3，旧样例 u6 3.9.3/xdis6.1.8 只是研究证据，不安装进产品。

**本轮最终实测**（Linux Python 3.11.2，真实 Qt 6.10.3 offscreen）：
- 编辑器 **220/220，通过且零 skip**，其中 36 GUI；新增 36 项覆盖候选、原始字节、错误分类、超时/取消/输出上限、完整源码/许可、候选另开与脏稿保护、真实标准2.5.6/2.7.13双VM编译、6项外部研究样例/原包用例。完整测试日志：仓库外 `/home/user/script-editor-dual-recovery/all-tests.log`。
- 真实原包 2371：严格解码后主引擎 0.5s 超时，第二引擎产出候选；3505：主引擎失败头不算源码、pycdc 部分候选可阅读/编辑；小样124为部分且可编译仍不标完整，3505/4861原始非UTF8字节保留，82双失败没有假源码。4305标准pyc小样两引擎返回文本，但直接原包严格参数校验仍拒绝；不混同两种链路。
- 124/4861 原包仍分别遇未知 opcode 213/215，4305 遇 marshal count 失败；下一段需按原包/entry/pyc精确关联、验证实际修复参数后才能接通，不能直接拿外部pyc绕过。无全面覆盖率/语义正确率声明。
- `bootstrap.py --check-only` 已执行，当前 Git 开发目录缺本机 pycdc bundle，先于 runtime 检查退出2；Git也未包含发行用 Windows x86 双 compiler runtime，不能计为完整自检通过；原生编译回归用的是仓库外实际源码编出的2.5.6/2.7.13，不是游戏 DLL。
- Ruff 全编辑器 0 报告、105 个 Python 文件格式检查通过；Windows 静态检查 0 ERROR / 0 WARNING。人工复核了新进程 argv/临时目录/UTF8/Windows文件关闭与平台分支；Windows 原生/EXE 未验，0.6尚未打包上传。已交付0.5.1网盘包不变，不冒充其中已有双引擎。

**下一段**：读取研究方 entry 清单与候选来源，严格复核修复参数；项目续编保存未采用草稿及候选元数据；补结构差异与覆盖验收。固定容量研究仍独立，不用删lnotab或猜key凑回包。



### 3.31 研究方全量语料交付只读复核（2026-10-15）

用户说“他已经完成了你看看”。本轮只读审查，不代替另一 agent 重建/运行全量，不运行下载的驱动或目标模块，不改编辑器产品代码、原包/keys/启动器/注册脚本、旧证据或网盘权限，不合并他方分支。研究方 `arena/4803041b-mxsj-tw-2022@8816f23` 只新增状态交接，本侧仅通过 GitHub API 读取，不 cherry-pick。

**交付入口与独立核验**：
- [完整交付索引](https://drive.google.com/file/d/1nIUskEGc1pkECGZIi3ZqUB8exmv8Zgrm/view)、[10卷SHA清单](https://drive.google.com/file/d/1FLksxEL5ZbXzH0LTz2U63wfjk0Keuve6/view)、[上传回执](https://drive.google.com/file/d/1lMhOi7wCgtOYC45XTVO0QvgzZKqdwEyF/view)。这是固定8212b26的新全量重建，**不是早先2364954字节补包，也不宣称逐字节复现旧79MB**。
- 实际下载10个独立ZIP，总计152769019字节；逐卷实算SHA256/MD5与交付索引及Drive元数据相符。直接流式读ZIP，不解压/运行代码：185048个受SHA256SUMS覆盖的文件逐一SHA/CRC通过，checksum文件本身也经CRC和整卷SHA保护；无重名、越界路径或symlink成员。
- 主键 `(archive_sha256, entry_index)` 恰5002个，0..5001无重漏；全部5001个非排除条目的容器entry_id和原参数与本地锁定原包/原表一致；193676次artifact引用的SHA/大小及其所属entry目录均核对一致。1288在full/sample/sample_v2中均仅record，未读取其payload。
- `full/manifest.audited.jsonl` 为74417377字节，SHA `e06efa990600ec1ca3f4f57c475596c10203c40d36a989ce43fe1192fa890535`；最大单行16246字节。后续需逐行有界导入，不把74MB清单塞进现有16MiB参数表入口。
- 独立从audited清单重算：4973条有源码形状候选，4780条双引擎均有候选；4916完整输出标记/57部分/28失败/1政策排除。4997份标准pyc，1954/3066/4166/4691缺pyc；单引擎超时4条，聚合超时0。原样语法记录通过2.5.6/2.7.18为3756/3757，处理候选为3806/4062。这里是核对归档的编译记录，**本轮未重跑这些编译器，数量不是语义正确率或编辑器回包覆盖率**。

**编辑器对接实测（仅21条只读核心codec，不调用反编译器/编译器）**：
- 研究修复报告15个非baseline条目：8条（63/1013/1528/1854/1931/2643/2984/4305）用记录中的修复参数通过编辑器现有严格codec，所得标准pyc与交付逐字节相同；原参数均拒绝。可作为下一段严格导入的正向验收，尤其4305/1931不再缺修复证据。
- 另3条有交付pyc但仍被严格opcode拒绝：64（80@3217）、4133（92@595）、4928（203@30721）；4条是报告中明确没有pyc的失败项。baseline的124/4861也仍被213@2506、215@381拒绝。**不把这种拒绝当成“不能阅读编辑候选”的理由，但不能因此放宽发布校验。**
- 2371原参数可严格解码，却与归档pyc不完全相同：一个嵌套65字节co_code内，offset42..44由本侧 `[19,3,9]` 变为归档 `[124,6,0]`；其余marshal树相同。两版语义均未验证。归档stage=baseline/repaired=false仅代表全局参数未换，不能理解成没有局部转译修补。
- 读取（不导入执行）固定研究转译器确认：它有未知opcode→NOP、元组tag强制修正、header修补、co_code局部seam求解。因此“marshal可读/重复pyc相同/native加载通过”并不证明严格可逆或控制流/业务语义正确。不能仅匹配entry和全局keys就将外部pyc冒充编辑器原生解码结果。
- 统计小口径：`compiler-and-byte-summary.json` 的u6 raw_pass=52包含50条已被audited降为diagnostic-only的条目；按有源码形状过滤只剩2。最终总表3756/3757已经正确过滤，可以复算。编辑器按audited主体/状态处理，不直接用子表52作为可用源码数。
- 研究侧u6/xdis=3.9.3/6.1.8、编译器2.7.18；编辑器继续固定修过3.14兼容的3.9.4.dev0/6.3及产品2.7.13，不覆盖版本，不沿用其编译通过章。该5002条语料针对script.fls，不能外推data.fls覆盖。

**审查结论**：以“全量研究语料交付”范围可以接收，无需让研究方重跑；不等于全模块安全回编或编辑器完成。下一步本侧实现：流式audited清单/路径/指纹导入，严格校验可复现的修复profile；将外部候选与原生已验证来源分层保留，支持候选/编辑稿项目续编。源码可读/编辑和安全回包继续分离。

机器可核对结果（不含源码正文、原始keys或1288 payload）：[`docs/evidence/corpus_8212b26_editor_review_20261015.json`](evidence/corpus_8212b26_editor_review_20261015.json)。下载归档与审查输出在仓库外 `/home/user/corpus-review/.cache/material`（缓存不保证续轮保留）；本侧审查辅助脚本在 `/home/user/corpus-review-tools/`。原包script/data、参数、被钉工具及启动器SHA复核未变。本轮没有重跑GUI/220项产品套件，也未构建、打包上传或进行Windows/游戏验收。

### 3.32 编辑器第二段：语料对接与草稿续编（2026-10-15）

按用户“那进行下一步”实施；先提交推送 `5998c1b` 再编码，未合他方分支/主线。
源码升 `0.6.0.dev2`，独立目录，不改游戏原包、原keys表、启动器或已验注册方案。

**实际实现**：
- `corpus_manifest` 逐行有界导入74MB audited清单，保存offset/长度/行SHA；严格关联整包SHA、
  VM、entry index/id、整清单SHA与产物SHA。只按选中entry读取、拒绝跨namespace/路径别名/symlink，
  不把74MB清单交给16MiB keys入口。1288在读取产物前排除。
- `verified_parameters`逐项整数比对原参数、本侧严格解码且与交付pyc逐字节相等才写**全新JSON**；
  真实通过63/1013/1528/1854/1931/2643/2984/4305，7条拒绝。未覆盖原表，不移植NOP或局部修补。
  GUI显式另存后关联该目录，保存项目引用路径/SHA；不是静默替换内置表。
- 外部候选保留原stdout/stderr、转义稿/变换和历史语法证据，可编辑但不自动可发布。
  历史2.5.6通过仅影响展示排序；124/2371/4861实际可读且origin_verified=false。
  采用时重新核对实际原包standard SHA，不能依靠序列化bool或complete放行。
- schema3保存全部打开缓冲区、未采用稿、候选/原字节/诊断、VM/来源/采用状态和语料引用；
  兼容1/2，原子保存，不强制先存.py。重开保留已有编辑/undo、不覆盖当前候选，改名另存后重复打开也保留。
  语料缺失或已嵌入源码文件缺失仍能恢复文本，原包和catalog仍需可验证。
- 语料目录只读，单离线产物8MiB/单快照文本与raw约8MiB、最多128编辑区、项目≤64MiB；
  保存前48MiB近似预算，超限不改旧项目、不丢缓冲。1182真实stdout 4239260B可读；
  本机子进程每流2MiB边界不放宽。缺语料普通打开回退本机双引擎并提示，显式另开失败不碰旧稿。

**本轮实际验证**：
- 完整套件264/264，**零跳过**，其中48 Qt offscreen GUI；相对220新增44项。
  Linux/Python3.11.2、PySide6/Qt6.10.3，标准CPython2.5.6/2.7.13实际构建启用，
  固定pycdc实际构建并跑双VM冒烟，真实原包与外部小样/选中full产物均启用。
  首轮全量曾因测试venv的恢复源码安装摘要不符失败；通过启动器同等的带SHA本地源码安装重钉后，
  最终全量无失败。没有放宽源码来源检查来过测试。
- 真实4305用已核验profile与**测试专用小源码（非整份恢复游戏逻辑）**，真实编译→新包→完整标准读回，
  内嵌文件名保留，其余5001条存储负载全等；哨兵证明编译目标未执行。
  未改严格原生链的VM/文件名、容量拒绝、完整回读与原包只读要求。
- ruff全过，Windows静态检查104文件零发现，git diff --check通过。
  发行门新增关键GUI/schema3/严格目录测试，5条真实full语料测试明确为外部材料可选项。
- 机器记录：[第二段验证摘要](evidence/script_editor_0.6_stage2_20261015.json)。
  仓库外完整日志`/home/user/script-editor-next/final-tests.log`，构建器及Linux测试环境不入源码交付。
  原包script/data、原表、mxLauncher SHA记录在摘要且复核未改；未执行游戏模块/DLL/研究驱动，未重跑全量反编译。

**未完成/下一步**：更广结构差异与安全回包覆盖验收；Windows构建/运行、EXE依赖闭包与客户端实机。
本轮未新打包上传网盘，不把Linux测试当Windows验收；下一次交付仍须独立源码、双Windows编译器与GPL第二引擎闭包。

### 3.33 data.fls全量可打开补齐（2026-10-15）

用户明确“data.fls也要啊”；不能用“支持2.7编译”代替包内源码打开覆盖。
本轮从已推送`e72aac9`继续，版本0.6.0.dev3，不改原包/原表/启动器/注册，不重跑script研究全量。

- 实际检查固定data SHA `5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c`：
  133条=12目录+121脚本，121全部严格CRC/长度/native解码成功。
- 新`core/services/data_corpus.py`只处理data，调用既有独立双引擎生成全量候选缓存；
  CLI`script_editor.data_corpus`、GUI“恢复语料→生成data全量候选清单…”接线。
  新目录不可覆盖，原包只读；构建中断/取消留INCOMPLETE、不发布可用清单；可选标准2.7.13逐候选编译检查。
- VM2.7清单显式archive_vm、entry index、路径身份和目录标记；复用有界SHA/路径约束，
  不错套script entry_id/五段参数/2.5 magic或语法记录。导入/候选页/项目快照与离线续编均已接通。
- 首轮120/121可读，data82 `lib\uuid.pyo`被xdis6.3的unsigned long位数读取和pycdc失败阻断。
  修复仅位于独立GPL worker：按signed32读取位数、校验15bit digits与边界，保留每个整数的值/符号。
  不修改原始pyc、opcode、原codec或安装的第三方文件；主GUI仍不导入GPL解析库。
  真实2.5.6和2.7.13编译→恢复→再编译，正负大long的原始marshal常量对照通过。
- 复测**121/121均有可编辑候选，121/121至少一候选通过标准2.7.13语法检查**。
  主引擎121完整启发式；pycdc84完整/37失败，有原诊断，不说双引擎全部成功。
  共220份有主体候选中198语法通过/22不通过；不以此替代业务语义验证。
- 实际逐一在Qt offscreen GUI打开121个data脚本，全部可编辑、VM=py27、严格原包来源匹配。
  原字节/compat渲染性质/trace/诊断保留；项目保存与重开保留data修改、VM及语料引用，不自动采用。
  uuid也实际通过不依赖缓存的普通read_module直接打开。
- 真实data75用**测试专用小源码**编译→新包→完整standard读回，原嵌入文件名保留，另132条存储负载全等，
  目标未执行。不是121条全恢复源码回包或客户端业务验收。
- 本轮新增24项，完整**288/288，零跳过，54 GUI**；真实双compiler/pycdc、script材料与全data缓存启用。
  ruff通过，Windows静态检查108源码/脚本，0 error/warning/info；git diff --check通过。
  发行门新增data关键GUI/生成/负long双VM测试，5条真实data材料测试为明确外部可选项。
  新生成清单1067个artifact引用均用产品读取器重核SHA/长度；输入script/data/keys/launcher SHA全部未改。

证据：[data覆盖与回归摘要](evidence/script_editor_data_corpus_20261015.json)。
仓库外缓存`/home/user/script-editor-next/.cache/data-corpus-v2`，日志`data-corpus-v2-build.log`、`data-full-tests.log`；
候选源码/原字节与Linux工具不入Git。源码工具支持自行生成，不依赖另一个agent交语料。

**未完成**：Windows构建/运行、EXE依赖闭包、客户端语义与全条目安全回包。未新打包/上传，旧网盘0.5.1不含本轮修复；
不自行合master。下一次交付仍须完整独立源码、双Windows编译器与GPL第二引擎闭包。

### 3.34 0.6.0.dev3完整源码交付收尾（2026-10-15）

用户授权“那你提交推送上传”；data功能提交`a00df3d`已推送，先补真实交付文件再上传。
- 已从固定CPython官方源码交叉重建Windows x86 2.5.6/2.7.13，更新实际交付manifest，
  两套EXE/DLL/标准库/许可的静态PE及逐文件SHA核验通过；不是Linux文件改名。
- 从固定pycdc源码真实交叉生成Windows x86程序，只导入Windows 10/11系统UCRT/kernel32；
  GPL完整源归档、许可、静态CRT/LLVM许可及完整构建配方随包。13条Zig libunwind属性警告，构建退出0。
  新增构建声明摘要校验/EXE暂存保留及对应回归，不允许暂存时丢弃运行时声明。
- 完整回归**289/289、54 GUI、零跳过**；ruff、Windows静态109源码/脚本0发现、diff检查通过。
  主恢复引擎固定源码及xdis/spark-parser/six/click对应源码、双CPython官方源码也附交付，
  一键启动/EXE构建脚本和固定原包匹配参数保留；首次Qt/安装构建依赖仍需联网，不是离线安装器。
- 证据：[交付构建静态核验](evidence/script_editor_0.6_dev3_delivery_build_20261015.json)。
  [网盘下载](https://drive.google.com/file/d/1ux8i20f7chx4vlHIiWPnxTw7YTJmqCpB/view)：
  `MXSJ_ScriptEditor_0.6.0.dev3_source_with_compilers.zip`，39,314,505 B，174文件，
  源码`6ba927665a8ba40c821623c4bca3c073c76a4dbd`；SHA256
  `fe4db94db3bcb10982ae6b14dbc448d5554abb9e6e6ea1ae77e1eaa93dffd011`，
  MD5 `a3baf00914f39fa4da7bbbfad319f71a`。ZIP CRC/逐文件SHA与长度全通过，
  解压的独立交付副本再跑289/289、54 GUI、零跳过（23.380s）。
  上传后单独get_file重读远端大小/MD5均同本地，未改分享权限，旧包保留。
  [机器回执](evidence/script_editor_0.6_dev3_delivery_receipt_20261015.json)记录源提交/摘要/远端ID。
- Windows启动、双compiler实际运行、Windows EXE构建及游戏语义仍待用户实测；
  不附游戏包或研究语料，不改mxLauncher/注册，不开PR/合master或更改网盘分享权限。

### 3.35 用户反馈script打开即条目0负载越界（2026-10-15，待定位）

用户实际反馈：data.fls可正常打开，抽看部分源码正常；script打开即报“条目0负载越界”。
**尚未拿到报错文件的元数据，不能宣称已复现/修复，也不能仅据此认定用户文件损坏。**

- 本次重新只读核仓库原包：SHA `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`，
  24,454,082 B，5002条，目录偏移24,374,050；全部负载边界通过。
  第一条偏移7,489,695、长度214，普通读取和模拟Windows无pread的seek/read分支均可打开。
  这不是用户文件或Windows实机验收；不拿原包通过代替用户报错。
- 新增独立标准库只读诊断`diagnose_archive.py`及BAT：记录文件大小/SHA、头与有限目录原始记录、
  解码边界及稳定性；不附源码/负载/密钥、不执行游戏模块、不写回输入、不需要Qt。
  诊断包用于收集**用户刚才报错的那份script**的JSON，不是编辑器修复版。
- 容器错误增加具体偏移/长度/目录偏移/文件大小，不放松原边界校验，不影响data读取。
- 本次核心/只读诊断/文件身份回归35/35通过，新增诊断6项；ruff与4个改动文件Windows静态0发现。
  未重跑此前289完整GUI/真实双VM测试；不复用旧环境结果冒充本次完整回归。
- 下一步：拿到用户JSON后与固定原包/当前派生包的目录字段比对，再做有证据的兼容修复。
  本次未上传新网盘发行包，未改启动器/注册/游戏包，未合master。

### 3.36 用户诊断定位：script目录后负载被误拒（2026-10-15）

已从Drive读取`script-open-diagnostic-1792062154408995100.json`（ID `12960oayaA6CKHg1i58B94_6VYLlDS8k6`）。
用户Windows3.14.7，script SHA `c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1`，
48,449,597 B、5002条；目录`[24,184,785,24,264,817)`，首负载从24,264,817开始、长214。
这是**目录后的负载**，首条不超EOF；旧读取器误把“必须在目录前”当硬规则。
旧诊断的5002 invalid也是同一规则，不能据此认定5002条都真正损坏；尚未取得用户完整目录和负载。

- 用用户提供的8条原始目录记录重放，旧0.6.0.dev3解析器确切复现“条目0负载越界”；
  新读取器通过这8条重放。允许目录两侧，但仍拒绝头部/目录重叠及真正EOF越界。
- 同时修流式writer：将目录本身视为保留区域，写完两侧负载后回填，不重复拷贝目录后负载。
  独立envelope按区域物理顺序核无引用旧字节/间隙/尾部；不把目录强搬到末尾，不改data逻辑。
- 新增8个布局回归含4种目录位置×4种变更组合、目录后续编及native API完整codec读回，
  后者显式mock标准编译器审计，不冒充真实Windows编译验收。相关核心回归**56/56零跳过**。
  ruff全目录通过，Windows静态113源码/脚本0发现。未重跑完整GUI/双VM289基线。
- 另在仓库原包5002条及由它构造的48,647,407 B“全负载目录后”模型上做完整只读/无改动重写：
  两者全部边界通过、重写逐字节相等。模型不是用户的完整c727包，不替代其恢复或游戏验证。
- 诊断v2保留旧pre-directory指标，新增实际文件边界和目录重叠指标，不再把post-directory误报损坏。
- [机器证据](evidence/script_editor_post_directory_20261015.json)。不自动扩展原包XOR表的SHA白名单。
  用户现有修改/项目、原游戏包不动；Windows/用户全包/客户端仍待测；**源码修复尚未更新网盘整包**。

### 3.37 0.6.0.dev4完整源码修复包已交付（2026-10-15）

用户明确要求上传到网盘`script_editor`目录（Drive ID `1Oknzs5ftrOHpf_jy0vQasYRtJCPoBQmO`），
不传My Drive根目录，不交缺编译器的纯Git源码或需要覆盖旧目录的零散补丁。
修复源码`77dc861`已推送；版本升0.6.0.dev4，GUI标题可明确区分旧0.6.0.dev3。

- 双Windows x86标准CPython2.5.6/2.7.13及Windows pycdc均从固定官方源码真实交叉重建。
  compiler manifest更新为实际产物摘要，PE/系统DLL导入/许可和对应源码静态核验通过。
- 本次80/80零跳过（56核心＋24runtime bundle），ruff及Windows静态113源码/脚本0发现。
  本环境未重跑此前完整GUI/真实双VM289历史基线，不把它当0.6.0.dev4当前验收。
- 新说明明确目录后负载修复、保留项目续编、派生c727包不自动套原包XOR表；
  首次Qt/Python构建依赖仍需联网；不含编辑器预构建EXE或游戏包。
- [构建核验](evidence/script_editor_0.6_dev4_delivery_build_20261015.json)。
  [网盘文件](https://drive.google.com/file/d/1Si8vmiddOC43jAAyNO1zZjlPvpgPSL_3/view)位于指定
  [script_editor目录](https://drive.google.com/drive/folders/1Oknzs5ftrOHpf_jy0vQasYRtJCPoBQmO)，
  `MXSJ_ScriptEditor_0.6.0.dev4_source_with_compilers.zip`，39,326,132 B、179文件，
  源码提交`3f708a098fb67d67a867d9090b49f5a159c9a549`，修复`77dc861`。
  SHA256 `974c0bdcd7f454517aba2932eab4df0335aa26c81330ff03131a58a0a59369ac`，
  MD5 `876b1df8d3b57f0d10964c4a75d64374`。ZIP CRC/逐文件SHA与长度全通过，
  真正解压ZIP后的独立副本再跑80/80、零跳过（0.308s）。上传后独立get_file重读
  文件名、父目录ID、大小及MD5均匹配本地，未改权限/移动旧文件/替换旧ZIP。
  [机器回执](evidence/script_editor_0.6_dev4_delivery_receipt_20261015.json)。
- Windows实际加载、EXE构建、完整用户c727包恢复及客户端语义仍未验；不改分享权限，不合master。

### 3.38 0.6.0.dev5补齐已知测试包XOR自动关联（2026-10-15）

用户0.6.0.dev4截图：包已打开，但所有条目停在“请先选择并确认XOR目录”。
根因是§3.36只修容器布局而未登记当前c727包的参数关联，这是交付缺口，不能再要求用户手找目录。

- 精确登记诊断中的完整SHA `c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1`，
  关联同一份已授权`script-original.json`，仍核对参数SHA。只允许逐条严格恢复尝试，
  不是已验证全部payload/边界，更不是恢复源码可信/可发布证明；不猜key、不扩展到未知版本。
- 原包与此测试包共用一份参数，EXE暂存去重但双包完整指纹仍分别复核；篡改参数仍拒绝。
  项目缺关联时补已核验内置关联，不覆盖显式项目目录；旧未恢复标签可重试，
  已有可编辑稿/修改/撤销历史不被替换。1288、严格native/marshal与人工采用门保持。
- 新增7项（5核心＋2真实Qt工作流）：Qt→自动绑定→严格native读取→真实主恢复worker→可编辑，
  以及旧项目缺参数→自动补齐→重试→再点击不覆盖修改。SHA/参数路线用受控样本模拟，
  标准CPython2.5真实编译与worker不mock；不把它冒充实际用户完整c727文件验收。
- 全套310项：**294通过、16明确外部语料/缓存跳过，55 GUI实际通过**；真实双VM与Linux双引擎启用。
  非许可跳过0，所有required IDs在场；ruff/Windows静态113源码/脚本0发现，diff检查通过。
- 用户截图同entry 7/13/2359/2368在仓库原包上用真实双引擎均获得候选（1465/51710/4239/4019字符）。
  这仅证明原包这些条目非全不可恢复，不声称已读到用户派生包相同负载。
- 版本0.6.0.dev5；完整源码交付复用dev4已核验Windows双编译器/pycdc及对应源码/许可，
  不用Linux测试产物冒充Windows文件，不附游戏包。仍上传指定script_editor目录，不改权限/旧包。
- [本轮证据](evidence/script_editor_registered_catalog_20261015.json)。已交付
  [0.6.0.dev5完整源码ZIP](https://drive.google.com/file/d/115EwvX3Cr6r3RR4nCeVf5uMnFYyS9iu5/view)，
  放指定script_editor文件夹（ID `1Oknzs5ftrOHpf_jy0vQasYRtJCPoBQmO`），
  `MXSJ_ScriptEditor_0.6.0.dev5_source_with_compilers.zip`，39,343,950 B、182文件，
  代码`820fc89c95795949c09a9552ed7b50f13b77f9b3`，MD5 `8fac8969745e28ca05e806b40525adfa`，
  SHA256 `624397280d67a4c0261fdd232402a55263e834ba0b0bacdf21438440adcb33fc`。
  ZIP CRC/逐文件摘要通过，真正解压后的副本复测310项中294通过、16明确外部跳过、55 GUI通过（10.376s）；
  上传后独立get_file重读文件名、父目录、大小及MD5均匹配，旧包/权限不变，无游戏包上传。
  [交付回执](evidence/script_editor_0.6_dev5_delivery_receipt_20261015.json)。
  Windows加载/EXE构建、完整用户c727恢复和客户端语义仍待验。

### 3.39 0.6.0.dev6源码：script模块路径优先（2026-10-15）

用户截图要求像data一样显示模块路径，而非数字ID。旧0SLF容器目录仅有ID，
旧GUI直到双击恢复后才追加`repr(bytes)`，既没有批量路径索引，也仍以ID为主标题。

- 新增只读路径扫描：已确认整包/参数SHA，参数表一次读取并在结束再次复核；
  每条仍检查存储摘要/固定XOR边界、有界native marshal。独立于opcode翻译和反编译器，
  不运行游戏代码，不产生源码绑定、编辑稿或发布资格。原包/参数变化拒绝整批索引。
- 列表直接显示`script/login/register.py`等内嵌路径，统一斜杠；原`.py`/`.pyo`后缀保留，
  不把源码文件名猜成`.pyo`。控制字符拒绝，非UTF8可见转义，不猜码页；不可读项明确标记。
  ID/序号保留在详情和搜索，搜索支持两种斜杠、大小写无关；data仍使用其容器目录路径。
- 打开包、旧项目、确认外部参数、发布后切换新包均接入后台路径索引；拒绝参数确认不显示
  未采用参数所得路径。项目回滚恢复原导航状态，已有源码/撤销保留；新包切换清理旧导航缓存。
- 新增15项全部通过，含5项真实Qt（自动路径/搜索/精确entry映射、旧项目保留编辑、
  data保留pyo、手动参数重索引、拒绝确认不泄漏路径）；核心含摘要篡改/中途变化/坏压缩隔离。
  在修改前源码上，同一GUI用例先复现FAIL（实际`#0 · ID 00000064`，预期模块路径）。
- 仓库原包5002条真实Qt后台打开：4951条路径，51条明确不可读；约7.95秒、Qt事件循环
  393次响应；搜索`login/register.py`仅4007，0源码标签/0绑定，不执行模块。
  用户完整c727负载仍不可用，不能冒充用户全包或Windows验收。
- 全套325项运行结束0失败，但有55次测试/子测试跳过（本轮重置缺双标准VM/构建件及外部语料），
  **不符合完整发布验收条件**，不沿用历史dev5的294通过/55 GUI数字。ruff/diff检查通过。
- [机器证据](evidence/script_editor_module_paths_20261015.json)。代码已推送固定分支；
  未合master、未改游戏原包/分享权限。本轮取回dev5完整源码ZIP时，连接器download_file返回
  `Could not retrieve the file from the connector`；不重复失败调用、不交缺编译器替代ZIP。
  此为上轮源码修复时状态。本轮用户要求提交推送上传，未重复失败调用；按固定配方重建双Windows
  编译器（156/178官方core单元）与Windows pycdc，标准库及许可与旧件一致、PE32/摘要核验通过，
  更新运行时清单；二进制仍不入Git，不混入Linux测试程序。
- 本轮已重建实际Linux双标准VM与pycdc并使用固定来源uncompyle6重新跑全套：
  **325项中309通过、16许可外部语料/缓存跳过，60 GUI通过**（12.653s），41 required全执行。
  不沿用上轮缺VM时的55次跳过或dev5的历史数字；Windows执行/EXE及游戏仍待用户测试。
  [本轮构建核验](evidence/script_editor_dev6_delivery_build_20261015.json)。
  完整独立源码ZIP已交付：
  [MXSJ_ScriptEditor_0.6.0.dev6_source_with_compilers.zip](https://drive.google.com/file/d/1BS9py9F5-z_MWr4zfZp214HUBW3Fo-8q/view)，
  指定script_editor文件夹 `1Oknzs5ftrOHpf_jy0vQasYRtJCPoBQmO`，39,409,837 B、187文件，
  源提交`3791d0cc83e3d3178d7652cdd744fc516932aac3`，
  SHA256 `6ac9e6bf51dd4b7613418320fcd054c5c9b2e4e073489602130295130837c38e`，
  MD5 `a1af71f85fe056d3dc8e2d6d7d9ef6e0`。
  ZIP CRC/逐文件长度摘要、双Windows运行时及pycdc/参数暂存核验通过；真正解压后完整回归
  同样325项中309通过、16许可跳过、60 GUI通过、41 required在场并执行（12.484s）。
  测试后186个payload文件仍匹配原包清单；上传后独立get_file核对名称/父目录/大小/MD5一致。
  旧包和权限未动、未上传游戏；[最终回执](evidence/script_editor_0.6_dev6_delivery_receipt_20261015.json)。

### 3.40 A总控与客户端脚本手册底座（2026-10-15）

- **授权与范围**：用户指定本会话为A并要求先开始；开工先检查工作树并推送固定分支（起点`1a0b233`，当时无待提交，Everything up-to-date）。本轮只新增独立`script_manual/`、本节与测试证据；不改脚本编辑器、游戏脚本、原包、启动器或Drive权限，不重建/上传游戏包，不合工作分支到master。
- **协议与任务**：`coordination/baseline.json`固定两包SHA、VM、条目数、参数摘要、来源提交；`schema/contract.schema.json`为严格格式。主键为包SHA+原始entry号，禁止按路径/文件名静默覆盖；1288排除元记录不得写路径/函数/正文，data目录不能当源码。`tasks.json`分配C–G各4个样板，main.py归C、E/F协审；B全量目录、H独立复核，A不伪称已启动其他会话。
- **内容边界**：20条种子明确标`historical`，来自已钉SHA的旧catalog，不是本轮逐条原包提取。只提供337公告模块格式样板（6个重点函数、2个消息分支、1条下游线索）；全部解释保留`inferred`，来源`historical_unverified_origin`，交C/H复核。其余19模块未编写说明。PR34语料只引用外部`full/manifest.audited.jsonl`，本轮没有下载全语料或钉其manifest摘要；不得以本底座冒充B完成。
- **工具能力**：PySide6路径主列表，中文功能/路径/函数名和多词检索、领域/审核筛选、职责/函数及消息分支/上下游与修改入口/证据四页、内部模块跳转、后台加载/复验/导出、失败保留当前手册、关闭等待任务结束。core不依赖Qt，不导入执行游戏脚本。单HTML内嵌所有数据/CSS/JS，无网络依赖，SHA白名单CSP与文本转义；仓库外全新目录导出，不覆盖旧输出，失败保留INCOMPLETE标记；BUILD记录输入/HTML摘要与覆盖数。
- **审核闸门**：包/entry/VM、重复主键、唯一owner、路径漂移、未知字段、证据悬空、越界行号、目录/排除政策、大小和符号链接等校验；禁止远程schema、重复JSON键/NaN与路径穿越。`--verify-evidence --repository`实算文本SHA/行范围，不代表语义正确；`--require-full-inventory`在当前20/5135上明确拒绝（完整登记仍不等于全函数解释）。H单独review绑定说明原字节SHA，改动即过期，不能由作者自填审核通过；此工作流不是密码学签名。
- **Linux实测**：75/75，零跳过，其中11 Qt offscreen，Qt实际库`/home/user/path-navigation/.cache/qt-libs`；ruff（显式含spec）0；bootstrap `--check-only`退出0；Windows静态检查ERROR/WARNING/INFO均0。真实Chromium153.0.8010.0以断网context及`file://`验证14项（检索、分支、来源/证据、关联/深链、筛选、空状态、390px无横向溢出、无外网请求/JS/CSP错误）。测试本机临时注册已有中文字体，不把字体嵌入/再分发。生成站点/截图/日志/浏览器/构建目录均仓库外。
- **Windows与打包待验**：附ASCII/CRLF双击启动bat、自动依赖自检、源码、build_exe.bat及onedir/onefile spec，入口不跑pip；EXE异常日志写APPDATA。Linux spec已尝试，但宿主缺`libpython3.11.so.1.0`，在Analysis阶段停止，**不是打包成功**。未Windows双击、EXE、用户包或游戏运行验收；不把Linux通过写成Windows可用/已交付EXE。
- **下一阶段**：按`script_manual/docs/AGENT_TASKS.md`向B–H分派固定版本底座；B提交目录和提取回执，C–G先完成20个样板、H逐份复核，A统一集成再扩域/串功能链。其他Agent只改自有目录，不改schema/总任务/导航/根STATUS。
- **持久证据**：`docs/evidence/script_manual_0.1.0_dev1_validation_20261015.json`含工具源文件摘要、75项统计、真实浏览器记录、导出回执、原包/参数前后匹配及未验边界；不是网盘上传回执。
- **补记此前PR34授权已履行**：纯文档38行人工审查后已合，merge `8afb53a14fe9c939d61ea3ab71ed64f0bf682af1`，2026-10-15T13:09:05Z，评论 https://github.com/a565551313/MXSJ_TW_2022/pull/34#issuecomment-6192827624 。核对10卷远程metadata/回执与固定工具SHA，无CI配置；本会话未下载150 MB重验185048文件。该授权不扩展至本编辑器/手册工作线。

### 3.41 C登录域559386b的A预审：需修改，未集成（2026-10-15）

- 用户转交C分支`arena/160274ce-mxsj-tw-2022`及提交`559386b3a44015d4bf7a4b4f0651b09d3257b87b`。A只fetch对象并在仓库外覆盖副本审查，没有切分支、cherry-pick、merge、改正式annotations或现行预览；查询没有该head的打开PR。4份说明有155条类/函数记录、30消息分支，不代表全部已核对。
- 通过范围：只改login域5文件；隔离证据镜像下validate（含SHA/行范围）退出0，20目录/4说明/0 H通过。机器格式校验不等于事实正确。
- 阻塞：mainpage的selectserver.Show错误绑定4806(loginin，selectserver旧catalog为4844)；LoginOk被误写为保存账号（候选实际246–265提交C2SLoginIn，OnLogin 657–661才SaveAccount）；LoginOk/ShowLogin及跨模块问答等多处引用范围不支持结论；main.py的Python2证据以.py入工具目录使ruff报38项；与A保字节转义稿比较出现字符丢失形态，需原始输出/解码后处理证据澄清。旧候选来源状态升级也须补来源关联。
- A责任：初稿也误串mainpage→loginin，C虽改文字仍未改身份，A承认种子错误；测试夹具直接读生产内容，A后续拆分固定夹具与内容冒烟。catalog子集20项完成，8个失败报告含subTest；全套GUI复验因夹具缺新增证据出现模态窗口，超时后A终止自有测试进程，**没有完整回归结论**。不将所有测试问题推给C，不通过改数字凑绿。
- 持久预审：`docs/evidence/script_manual_C_559386b_A_review_20261015.md`。这是A集成预审，不是H独立审核记录。当前正式底座仍20历史种子/1说明样板/0 H通过，C修订后再交A/H/E/F；未开/合PR、未上传、未改游戏或编辑器。

### 3.42 E网络ec97941预审与A测试夹具隔离dev2（2026-10-15）

- E分支`arena/14596f40-mxsj-tw-2022`提交`ec97941f386c7e199e2f7fb39f49f0cf71b2959a`仅network域6文件，157类/函数记录、42分支。只fetch，在仓库外构建覆盖副本；没有切分支/合入/改E正文，也未发现该head打开PR。validate含证据SHA/行号通过，20目录/5说明/0 H通过，3970未编入为唯一关联警告；ruff与隔离wincompat通过，真实Qt与离线Chromium另做E内容冒烟。
- A独立venv使用Python3.11.2/u6 3.9.3/xdis6.1.8，定点只读恢复3176/2170/871/516/4293，全部baseline/source；871/516去掉6行恢复头后与仓库旧稿**原字节相同**，其余恢复行数与E报告一致并抽查关键片段。未执行游戏脚本，未处理1288，未裁决原生帧/服务端行为；原包/keys SHA不变。
- 待E修：报告把OnError隐藏窗口前提写反（实际not IsQuickConnect且not CanQuickConnect），JSON瞬连分支应补未在瞬连中的守卫；SetServerRoleInfo实际OnLogin后Show(False)隐藏登录面板，不是回登录界面；DoConnect成功回调未引用的限制需贯彻到摘要和main协审；生成时间位于恢复头，H重跑不能直接匹配整文件SHA，应补工具/依赖与归一化正文/pyc摘要；计时单位表述保持一致。报告修改后须同步所有JSON的SHA/行号。
- A自修0.1.0.dev2：开工前先推送检查点；tests/fixtures冻结schema v1样本，单元夹具不再复制生产annotations/inventory/reviews，新增缺生产数据仍可单测、生产数量无假设结构冒烟、非法生产数据仍拒绝3项回归。未改schema/归属/任务表或C/E正文，也不是把断言1改成4/5。
- 回归：A当前数据、仓库外E覆盖、仓库外C+E同时覆盖，均78/78、零跳过、11真实Qt offscreen。旧夹具E副本复现75项：58通过/3失败/3错误/11GUI跳过，不能说75实过；旧失败/错误主要为夹具/数量耦合。新单元绿灯不消除C的.py ruff问题或C/E事实问题。A ruff显式含spec 0、wincompat 0/0/0（58文件/26源码脚本）、bootstrap自检0、当前来源复验0。Windows/EXE/游戏未验；此前Linux打包缺宿主libpython的边界不变。
- 持久证据：`docs/evidence/script_manual_E_ec97941_A_review_20261015.md`与`script_manual_0.1.0_dev2_validation_20261015.json`。E需小修再交A/H，C仍按§3.41修订；二者均未并入正式数据，现行预览也不冒充已集成。


<!-- 以下保留master并行工作记录；章节编号为各工作线原有历史编号。 -->

### 3.30 固定版本全量语料重建与网盘归档（2026-10-15）

本轮仅语料和证据；分支 `arena/4803041b-mxsj-tw-2022`，输入基线固定
`8212b26e359a693db5513e1bf0d0c6a5139336ba`，不跟随浮动 master。
原包 `8b6e9266…`、原参数表 `43bb090d…` 前后未变；工具完整 SHA 为
`a74742231e04c018c3f63452cfc859c20c6404fd73891eae9076bfcf8185b4e8`。
与文档/旧 manifest 的 `242543f8…` 差异实算定位到 `45d5590` → `26b7a087`
（引擎护栏、路径解析、失败标记及清点）；用户确认采用当前固定版本新重建，
**不宣称逐字节复现旧 79 MB，不修改旧 manifest**。

- 5002 条全部登记，1288 在读 payload 前排除，只有 `excluded_by_policy` 记录；
  实际范围 5001，标准 pyc 4997。原包只读，无目标 import/exec。
- 先交 10 条代表样例，再补 entry 82 真双引擎失败，随后每批 50 条、2 worker；
  转译 120 秒、双引擎各 30 秒独立进程组隔离，stdout/stderr 原字节完整留存。
- 最终 audited 清单：有源码形状候选的独立 entry **4973**，双引擎重复候选 entry
  **4780**；完整标记 **4916** / 部分 **57** / 失败 **28** / 排除 **1**。
  entry 聚合超时 0，但 uncompyle6 单引擎超时 4（另一引擎产出）；不隐去超时记录。
- uncompyle6：4445 完整标记 / 347 部分 / 201 失败 / 4 超时；
  pycdc：4834 / 127 / 36 / 0。真实 CPython 2.5.6 / 2.7.18 原样语法通过的独立
  entry 为 3756 / 3757，处理候选为 3806 / 4062；**都不是语义正确率**。
  raw 未做历史 Big5 字面量后处理，不与旧编译计数直接比较。
- Python 3.11.2、uncompyle6 3.9.3、xdis 6.1.8、pycdc 固定提交
  `b4289760970dbc399684f1e155ec6d1ea1cc787e`，实际依赖/编译器/源码 SHA 均归档。
  仓库外驱动与修复参数、验证、版本差异、命令均留档；原工具、编辑器、启动器、注册脚本未改。
- 测试：原工具 66/66、隔离驱动 7/7、诊断-only 清点复核 4/4。
  最终用 `full/manifest.audited.jsonl`，主键 `(archive_sha256, entry_index)`；
  原始 runner 清单保留。仅 parser/opcode 诊断不计源码；候选形状仍是启发式，非语义验收。
- 归档前核验 179531 个引用产物指纹；归档后从 ZIP 读取 185048 文件逐个 SHA 校验，
  10 卷 CRC 均通过；上传回执大小与 MD5 全部匹配。10 个独立 ZIP 共 152769019 B，
  全部解压同一空目录，不需拼接；不含原始游戏包/原参数表，**分享权限未改**。

持久交付入口（10 卷下载、完整 SHA、统计、样例和编辑器对接契约）：
[网盘交付索引](https://drive.google.com/file/d/1nIUskEGc1pkECGZIi3ZqUB8exmv8Zgrm/view)；
[归档 SHA256 清单](https://drive.google.com/file/d/1FLksxEL5ZbXzH0LTz2U63wfjk0Keuve6/view)；
[上传核对回执](https://drive.google.com/file/d/1lMhOi7wCgtOYC45XTVO0QvgzZKqdwEyF/view)。
沙箱当前根目录 `/home/user/mxsj-corpus-20261015`；生成物未进 Git，不依赖沙箱存活。
编辑器集成和语义/原生验收仍属于另一工作线，本轮没有开展。

## 4. 等待外部输入

> 以下保留历史内容及原章节锚点；不是本轮任务或授权。当前等待项、下一步与文档维护职责以 §1–§2 和 ROADMAP 为准。

| 事项 | 等谁 | 阻塞什么 |
|---|---|---|
| 脚本编辑器0.6.0.dev5完整源码修复包已上传指定script_editor目录（§3.38） | 用户Windows启动、双VM检查/EXE/客户端测试 | 不重复询问参数授权；script固定容量/未知映射继续严格拒绝，不把Linux或静态检查冒充Windows |
| 资源大包打开/新布局查找用户已确认通过；其余 Windows 快捷键/EXE、新图游戏加载仍待验 | 用户 | 不把两项交互通过外推完整编辑器/原生加载验收 |
| font1用户确认“确实好了”；account/CBox保留 | 后续功能按需验收，不再等font1重传/复测 | 不外推全部表单/真实服务器成功，不重导/改用户布局，不索取真实资料 |
| 真实注册接口与五账号整批成功回覆 | 后续服务端工作线（未开工） | 已定单条批量＋重名顺延（最多 `_99` 且最终 16 位，整批五个/同批重试不重复创建）；真实接口/固定成功回调调整/服务器验收未做，本阶段继续留桩，不能假报成功 |
| 是否合入 master、是否清理二进制 | 用户授权 | — |

## 5. 下一步（优先级）

> 以下保留历史内容及原章节锚点；不是本轮任务或授权。当前等待项、下一步与文档维护职责以 §1–§2 和 ROADMAP 为准。

当前用户请求已执行：0.6.0.dev6完整独立源码修复包已提交、推送、上传指定script_editor目录并重读核验（§3.39），等Windows/客户端测试反馈；
包内恢复编辑仍是主目标，不回退为要求用户自有.py的工具。
0.5开发工作流已实测，匹配参数的交付授权已获得；独立源码新包已上传并复查，不宣称全面完成，继续补覆盖率/固定长度/Windows验证，
不把阶段版或旧0.4.1网盘包当满足用户目标的成品。
M3功能已接线且核心离线回归通过（§3.19），
M4双Windows编译器/标准库/许可及完整SHA已补齐并随源码ZIP上传（§3.22），
Linux原先缺库的GUI现已全量实际通过；Windows仍须双编译器自检、真实桌面及EXE/客户端验收；
布局当前仅静态线索，不将挂载验证/自动接线算作已完成。
font1用户已确认好了，不再沿用旧账号框排查为当前任务；保留用户布局与account/CBox。
下面其余历史工作不混入本轮脚本编辑器实现。

1. ✅（2026-10-15，单独提交已完成）§3.1 修好，架构套件 161/161 与 `--check` 回绿；顺带记下第二步 `manifest.json` 也必须刷新的坑。下一个红灯候选是 §3.2（线性 vs 有序）判定，它决定资源/UI 编辑器两处文档口径。
2. **UI 编辑器 × script.fls 联动 + 注册界面原生重做**（用户 2026-10-14 定的方向，合并为一条线）：① ✅（0.7.0）离线索引生成器 `tools/script_link/build_script_index.py`：不跑反编译、直接转译+解析 Py2.5 marshal/字节码挖掘，4,987/5,002 个模块挖成（15 条基线转译失败未做边界修复），关联 2,920 个布局、13,162 个被取用名、19 个高置信代码皮肤锚点；随包 `script_index.json`（1.3 MB，查询层 `core/script_index.py`）。② ✅（0.7.0）代码现造的按钮（如 login 的占位锚点）按真皮肤渲染，不再显示默认占位（`painters._paint_code_skin`；皮肤覆盖仅限高置信工厂模式，其余代码控件仍占位）；左栏「脚本」页显示引用模块/被取用控件/锚点与皮肤详情，点名字回画布选中；打开布局状态栏报关联计数；③ ✅（0.8.0）改名/删除子树引用护栏、静态布局诊断与保存前清单（详 §3.7）；加控件自动接线（GetObject 认领 + OnMessage 骨架 + 空闲消息号）仍未实现；④ 脚本可在编辑器内查看/编辑，保存时布局与脚本一起出新包（写回管线 `tools/decompiler/pack_and_encrypt.py` 已验证往返逐字节一致；编辑后源码编译依赖 CPython 2.5.6——**2026-10-14 已在沙箱从 GitHub 源码自建成功**，自写源码经编译→混淆→5 段 XOR 加密→重打包→解密→转译往返全通（代码对象/繁体 unicode 常量/控制流一字不差），「仓库侧打包」路线打通，不必依赖 Windows）；⑤ 第一个实战：注册界面按原生重做（原生 `.dlg` + 原生脚本套路，参照 `chgpwd` 类原生表单；提交先留桩并明示未接通；用户已定字段/条款页/桩文案，见 §6）。硬边界：546 个 stub + 12 个转译失败的脚本无源码、不可联动编辑，须明确标记；写脚本前先拿无害小改动做真机验证。

PR #32 逆向补充：转译失败条目降至 4 条，救回条目需重建脚本索引；反编译语料仍为参考，不自动视作可信可回编源码。
3. 判定 §3.2，统一 `notes/` 与编辑器文档。
4. 两编辑器新功能先在客户端副本上复核（新增路径下拉、包树右键导入/替换、连续新包导入和新增原生编码布局加载）：撤销/重做混合批量、引用取消/确认、诊断定位/刷新、保存清单取消与新包读回，特别检查保存后新图解析器来源迁移；严禁覆盖原包。三个编辑器在 Windows 实机跑 CONVENTIONS §5.3 冒烟（启动 bat → `build_exe.bat` → 双击 EXE），把结果回填 §2 / §3.5；沙箱侧 10-14 已把完整测试（含 GUI 组）跑绿，不再需要「有桌面的机器跑测试」这一步。
5. 二进制清理（需授权）与 LICENSE/权利说明。
6. 服务端第一条真实链路（网关 + 账号 + 区服 + PostgreSQL），按 `server/docs/GATEWAY.md`、`INTERFACES.md` 开工；在此之前不要再堆设计文档。

## 6. 最近变更

> 以下保留历史内容及原章节锚点；不是本轮任务或授权。当前等待项、下一步与文档维护职责以 §1–§2 和 ROADMAP 为准。

| 日期 | 变更 |
|---|---|
| 2026-10-15 | 0.5.1修3.14启动完整源码＋双compiler＋授权参数新ZIP已上传18gthjpPO5oxp6IGYX5G3tqp8nrQOlMTN，138文件8,291,306B，源130269a；隔离3.14.7为176通过+8材料skip/32 GUI，中文路径真实bootstrap补装/二次不重装/pip check均过，137项清单及运行时静态/远端MD5复核一致。184全套双宿主通过；Windows/EXE/客户端未验，保留用户稿及固定容量护栏，详§3.28。 |
| 2026-10-15 | 用户真实3.14.7日志证实0.5.0固定xdis6.1.8不兼容，非网络。0.5.1改已适配3.14的固定上游完整源码＋xdis6.3并核SHA/PEP610，恢复失败不再挡GUI；真实3.14.7安装/启动器补装复检及3.14/3.11各184/184（32 GUI）通过。修字节保真/枚举接口，旧集合常量错误明确警告且保留用户稿；4007正确恢复+49超容量仍拒绝，4001/data75容量内真实回包。正打新包，详§3.28。 |
| 2026-10-15 | 0.5.0.dev1包内恢复编辑源码＋双compiler＋已授权固定原包解码参数已上传新Drive文件1-1PNBSZb_5Kt5ziy9WTn-P2wfZa_8ESc，135文件7,294,512B；隔离164通过+7指定材料skip，额外真实Qt自动参数读取script4007/data75可编辑，清单/静态运行时/远端MD5复查全通过。源码f899bab；未上传游戏包/改权限，Windows及固定长度等限制保留，详§3.27。 |
| 2026-10-15 | 用户明确允许随工具源码网盘包附带固定原包匹配解码参数；已实现后台完整SHA自动匹配、参数摘要核对、独立audit/stage及新GUI无手动参数恢复回归。171/171（31 GUI）通过，正打独立源码＋双compiler＋授权参数包；仍不含游戏包，不宣称全面完成，详§3.27。 |
| 2026-10-15 | 用户拒绝只能关联自有源码的残缺功能：0.5开发接入包内严格解码/独立恢复进程、可编辑草稿/反汇编、检查人工采用、来源持久化及双VM回包续编。167/167（30 GUI）通过，真实4007/data75恢复编辑回包且5001/132未改；修恢复引擎Unicode/Py2.5字面量渲染。未上传候选，不宣称全面完成；XOR参数随包授权待定，script固定长度/未知模块/Windows仍待，详§3.26。 |
| 2026-10-15 | 用户0.4.0刚开包报源包变化：定位Windows stat/fstat ctime语义差异，统一原/新句柄fstat并固定初始快照，保留修改/替换保护。修复661efe3已push，0.4.1含双编译器源码ZIP上传Drive `1xnMZls3kZmylUHZi8sRrcvlvnt4bU9fQ`，7132907B/117文件，重读大小MD5一致。154/154（26 GUI），解压148过＋6材料跳过，Win差异模拟先失败后通过，实机待确认；不改游戏材料/权限，详§3.25。 |
| 2026-10-15 | 按用户“提交推送上传”：0.4.0.dev1工作区源码＋双Windows编译器新ZIP已传Drive `1QNXpgwiGECqh377UN2npCNNTh32AGAvn`，7130558字节/116文件，重读大小MD5一致；源码0216b58，仓库149/149（26 GUI），独立解压143过＋6材料跳过，ZIP逐文件SHA与双运行时静态审计过。不含游戏/keys/探针，不改权限；Windows/EXE/客户端未验，详§3.24。 |
| 2026-10-15 | 用户批评脚本编辑器简陋：先push检查点0d18214，重整0.4.0.dev1工具栏/可停靠工作区、包切换、大纲/引用定位、编辑差异、查找和缩进。补真实Qt依赖，149/149（26 GUI）全执行通过；隔离Qt6.12/Python3.11大树崩溃，固定6.10.3并修菜单生命周期。提供真实Linux Qt截图，仅预览未重打包上传；Windows未验，详§3.23。 |
| 2026-10-15 | 按用户“补齐重新打包上传”：0.3.2.dev1独立源码＋真实Windows x86双编译器ZIP已传Drive `1yb1JsQbnWgremYR5u1-aQlwFjOWPSFO_`，7114401字节，重读MD5一致；18运行时文件SHA/标准库/5许可与自动双VM检查齐。134项118过16 GUI未执行，独立解压112过22跳过；源码提交efeddea，不含游戏/keys/探针，不改分享权限。真实Windows/GUI/EXE/客户端未验，详§3.22。 |
| 2026-10-15 | 用户授权打包上传测试：脚本编辑器0.3.1.dev1源码GUI ZIP已传Drive `135Wg6izLhOVzQ4H9e5-L3273_6DiUrhi`，135692字节、MD5与本地一致；解压副本129项115通过14 GUI未执行，先读说明/启动bat随包。明确无EXE/Windows双编译器、不含游戏包/keys/探针，不改权限；等用户真实GUI测试，详§3.21。 |
| 2026-10-15 | 用户继续：脚本编辑器0.3.1.dev1补M4整套运行时文件SHA/PE32/来源许可/注册后复验及严格发行检查；129项115通过14 GUI缺系统库未执行，新增24项为合成PE/mock护栏测试。manifest仍空，Windows真实双运行时/EXE与M3 GUI均未验收，缺件不再构建假完整发行；原包/注册源码/旧工具未改、无上传，详§3.20。 |
| 2026-10-15 | 用户继续M3：脚本编辑器0.3.0.dev1接可信源码预编译/清单/GUI单条新包与项目续编、原始co_filename字节/schema2/静态引用提示；105项91通过14 GUI缺真实系统库未执行。注册4007及data75均两轮离线回归、其余5001/132保持；M3 GUI未完整验收，M4随包编译器/EXE仍未交付。原包/keys/注册源码/两旧编辑器未改，无上传/合并/发布；详§3.19。 |
| 2026-10-15 | 用户继续下一阶段：独立脚本编辑器0.2.0.dev1实现M2支持子集原生后端/实验CLI，79项73通过6 GUI未执行；真编译/真实双包回读全等及5001/132未改条目校验通过。修真实分号lnotab零差事件丢失，静态核对当前DLL分发表和2.7语义、排除错误opcode66。只生成仓库外验证新包，旧原包/研究工具未改；GUI写包/M4随包编译器未完成，详§3.18。 |
| 2026-10-15 | 按用户“先提交推送然后开工”，先push设计检查点`2f5f7e4`，再实现独立脚本编辑器0.1.0.dev1基础，双包只读/手工源码与参考模式/项目/双标准编译核心。41项35通过6 GUI缺libGL未执行；ruff、wincompat 0；bootstrap正确返回2。原生写包/Windows随包编译器禁用或未实现，详情§3.17；未改原包/旧工具，不当作完整交付。 |
| 2026-10-15 | diag2实机报missing_attribute=FONT_EDIT。按原entry4007的FontLT14_3原生调用修四框/提示区，去除旧FONT_EDIT/COLOR_EDIT依赖与假测试桩；旧源无别名探针失败→新源通过，真2.5.6 32/32。新源构建校验发现旧边界猜测误改LOAD_FAST，新增严格自写marshal确定逆变换而非放宽断言，原转译器/key DB不改。新包与精确diag2重建仅4007变化，保留全部用户布局；实机待验，交付状态见§3.15。 |
| 2026-10-15 | 用户已进入协议，同意消息1到达、表单layout ready，但账号框初始化AttributeError；用户确认account/CBox。新增diag2拆解原生输入框调用、受限缺失属性/代码位置日志；只读原生工厂签名核对并纠正桩的cls(name)错误边界。真2.5.6 26/26、旧源定位探针先失败、新包marshal回读/桩冒烟/5001条与diag1等值、ruff与wincompat通过。不动用户布局，不声称已修好；本轮用户明确授权后上传Drive，大小/MD5与本地一致，详§3.14。 |
| 2026-10-14 | 用户否决一次性两路径助手作为终局，资源0.4.3/UI0.8.3修正常新增/修改/连续保存：统一原生路径XOR，旧明文/错key目标显式保存迁移，严格原生发布验证，不覆模板，不碰script；独立旧行为两FAIL→两PASS，资源118/118、UI203通过+1跳过、注册23/23，ruff/wincompat/启动自检通过。Windows与协议→表单仍待验，源码包已获当轮授权上传Drive，大小/MD5一致，交付链接见 §3.13。 |
| 2026-10-14 | 用户日志确认diag1已不再冻窗，但条款CCombPanel构造抛Exception、回首页，未跳转。静态追真实LoadFile方法表/机器码发现路径XOR公式；旧0x461340实际ReadFls，明文头自解是编辑器技巧而非原生。新增标准库两布局存储修复助手（保留用户明文字节，原包只读、整包逐字校验、新包独占发布、不改script），23/23回归含真2.5.6/静态PE/存储安全探针、ruff通过。只修确定存储缺陷，实际用户两条状态/Windows/条款跳转仍待验；编辑器通用新增未修，详 §3.12。 |
| 2026-10-14 | 用户明确“你传网盘”，上传现有已校验 registration_phase2_diag1.zip 到 My Drive 根目录（ID `1YxoYNmpTejl7qk86K9ELg_b1bvYJcGk8`）。上传返回大小/MD5 与本地相等；未改权限/删除旧包，未再次下载核验。只换 script，不重导 interface，仍是卡屏诊断版、原生根因待最后阶段日志。详 §3.11。 |
| 2026-10-14 | 用户确认原第二期网盘脚本、同包两布局、卡屏为整窗无响应。新增 phase2-diag1：模块导入至原生布局/条款文本/表单逐段日志、会返回的 Python 异常回退及原子切页引用发布；原生阻塞仍未定位/不能靠 except 恢复。真2.5.6重建，14/14回归+ruff+Windows静态检查通过；旧版同一布局异常探针先失败，新版通过。新 script 对已发第二期仅4007负载改变，337/其余5000条全等，未改接口/布局/原包。详 §3.11 和注册目录诊断说明。未上传 Drive/改权限。 |
| 2026-10-14 | 用户确认编辑器“速度很快，新布局也找到了”，大包打开/新布局查找两项按该环境通过。新增反馈：第二期脚本点击申请会员卡屏。已定位 tools/registration 源码/337入口/4007注册模块，确认先条款 regterms 再表单 regform；原始 337 正规化字节码证实先隐藏主页再构造注册页，构造异常是候选原因而非本次已证实根因。需确认同一实际新包包含两张布局、脚本版本/卡屏形态及最小诊断。只读复核，注册回归12通过+1真2.5.6缺失跳过，原包/key SHA不变；本轮未改脚本/出包/上传。详 §3.11。 |
| 2026-10-14 | 用户反馈布局导入保存后重开找不到、资源编辑器打开大包变慢。确认 0.8.1 自定义路径仅本会话及打开前全量扫描两处缺口，修为 UI 0.8.2 QSettings 地址记忆/包根精确路径只读恢复、资源 0.4.2 索引先显示/全量识别后台化、过期回调/多选/读关闭互斥护栏；注册两完整地址同步字典。新增 10 条回归：资源 110/110、UI 196 通过+1 语料跳过，ruff/wincompat/bootstrap 绿、原包/key SHA 不变。未取得用户确切地址/文件，不按大小断言数据正确；真实 Windows 打开速度/游戏仍待验。修复 `f6e6e2a` 已推送；源码修复 ZIP 已上传 My Drive 根目录且大小/MD5 与本地一致（资源 162,019 B、UI 386,673 B）；详情/链接见 §3.10，旧包保留，分享权限未改。 |
| 2026-10-14 | 按用户要求打包上传两工具到 My Drive 根目录：资源 0.4.1 / UI 0.8.1 源码启动 ZIP（非 EXE），代码钉 `fe2e057`。ZIP CRC/逐文件字节/清单 SHA 验证通过；交付副本资源 97 通过+7 数据跳过、UI 191 通过+2 数据/语料跳过，ruff/bootstrap 绿；Google Drive 文件大小/MD5 二次核验与本地一致。包内说明含 Python/启动步骤和新增明文布局/Windows/游戏待验边界；未改分享权限、未附客户端资源或桩件、未构建 EXE/开 PR/合并。最终下载链接/完整哈希见 §3.9。 |
| 2026-10-14 | 两项新交互按授权实现：资源 0.4.1 可搜索/手填包内地址（实际存在/已识别路径，不造未知名）；UI 0.8.1 包根右键导入明文 .dlg、单文档待入包预览编辑、明确新增/替换清单和显式新增写包通道。保存成功优先重挂新包/登记会话地址，树重开按指定包取布局。新增明文存储/替换沿原 XOR 密钥，原包不动、不自动导图/接脚本。新增 30 条回归；资源 104/104、UI 192 通过 + 1 语料库跳过；ruff/wincompat/bootstrap 绿，锁定输入 SHA 不变。系统库桩仅用于沙箱离屏；Windows/游戏/新增原生编码布局加载未验。固定分支提交记录见顶端，未开 PR/合并/发布/上传测试包；详 §3.8。 |
| 2026-10-14 | 用户授权首期三项已实现：资源 0.4.0 全局增量撤销/重做（增删替换/还原与批量一步）、UI 0.8.0 修改前静态引用护栏/删除子树检查/零 Qt 布局诊断、双工具保存前改动清单。功能 `f224f16`、类型缓存代际修复 `bf2bfc3` 已推送固定分支；新增 67 条回归，UI 170 项（169 通过、1 缺语料库跳过）、资源 97/97，沙箱 offscreen 进程均退出 0；无桩件 UI 92 项（91 通过、1 跳过）、资源 97 项（74 通过、23 GUI 跳过）；ruff/wincompat 0、bootstrap 自检绿、原包/key DB 哈希不变。版本基线探针旧版两 FAIL、本版两 PASS；详情/已知边界见 §3.7。只生成新包，不改编译脚本、不自动接线；未验 Windows/游戏，未构建 EXE/开 PR/合并/上传测试包。 |
| 2026-10-14 | 用户授权修复两个编辑器：UI 0.7.1、资源 0.3.8，代码提交 `eeff8c4` 已推送固定分支 `arena/51e31d38-mxsj-tw-2022`，未开 PR/合并/发布。新增 30 条输出安全/原子失败/真名连续性/GUI 状态回归（UI 16、资源 14）；最初 12 条核心回归在旧实现上复现失败后再修复。行为变化：Ctrl+S/另存包都生成新包，拒绝源资源及别名，不再原位覆盖源包；UI 的未改条目发布前分块逐字节检查，不能以 span 相同替代。资源导出追加目录边界与全帧预检；保存后真名和网格按 entry_id 重建。完整离屏实测 UI 137 项（136 通过、1 缺完整语料库跳过）、资源 63/63，进程均退出 0；环境 Python 3.11.2 / PySide6 6.8.3 / Pillow 12.3，系统库桩件只用于沙箱 offscreen，不入库、不代替 Windows/游戏验收。无桩件 UI 核心 74 项（73 通过、1 跳过）、资源 63 项（53 通过、10 GUI 跳过）；两目录 ruff 0、wincompat 0/0/0、bootstrap 自检通过。锁定原包/key DB 哈希未变。更新 README/DESIGN，未修架构证据红灯、未构建 Windows EXE、未合并/发布或上传测试包。 |
| 2026-10-14 | 项目分析复核（`arena/51e31d38-mxsj-tw-2022`，基线 `fa13871`）：只读检查主要目录、实现与文档，未改业务代码、原包或证据。锁定 script.fls/key DB 的 SHA-256 均匹配；catalog 34/34、devkit 29/29；注册测试 13 项中 12 通过、1 因未设置 CPython 2.5.6 而跳过。架构 150 项仍为 1 FAIL + 1 ERROR；来源文件名核验 96/96（非玩法验证）；CSV `--check` 仍报 `E evidence changed; review required`。将地图/NPC 证据重生成至仓库外后递归逐字段比对，仅 `/inputs/shared_decoder/sha256` 变化（`7490dbab…` → `242543f8…`），未修复已提交证据。API/网页/编辑器 GUI/Windows/客户端联调本轮未执行；未启动 Mock、未提交/推送/发布。本轮仅更新本文，标明旧会话状态与当前检出事实的区别。 |
| 2026-10-15 | 注册线 A 案做完：**`CONFIRM_MSG` 判定 + 兜底 + 重建测试包**。判定用硬证据 —— `servicedata` 的 pyc（28,177 B）名字表只有 `SERVICE_MSG`/`SERVICE_MSG2`；两归档 4,941 个可读模块中无任何 `CONFIRM_MSG` 定义者，唯一引用是 `script/login/register.py:142` 且无 try ⇒ **旧客户端 `CConfirm` 构造即 AttributeError**；上一期「`CConfirm` 原样引用、既有流程不改」保留的正是这条死路。条款侧结论相反：模块确实在包内，真机一直在走正式文本（`script/data` 在 import 路径上，与 14 个 `import defines` 同构）。　改动：`register.py` 新增 `CONFIRM_FALLBACK`（Big5 字节常量，逐字节核对过：8/0/22/0/84）与 `_LoadConfirmLines()`（与 `_LoadTermsLines` 同构的 guard，包内补上常量即自动改用原文），`CConfirm` 不再裸取属性；文件头第 3 点按实测更正。　测试保真度根因：`harness.py2` 原先给 `servicedata` 桩件塞了 `CONFIRM_MSG`，所以历次「CConfirm 流程走通」测的是桩件世界 —— 现加 9a（忠实本版：有 `SERVICE_MSG`、无 `CONFIRM_MSG` → 真文本条款 + 兜底确认框 + 构造不抛，字节级断言，不依赖沙箱没编的 big5 codec）与 9b 对照组，`test_runtime.py` 断言 9a 输出行。　构建与验证：重建 `out/script.fls`（sha256 `ed0f4126c0b5d3533b157cd1b8002b9d570f3c1e152c61f7c60dcd48de5a5a5f`，24,262,648 B；构建器自动校验 337 只差 9 字节、4007 marshal 往返一致、无网络名残留），本目录 13 项回归（11 布局 + 2 运行时）**全通过**，`ruff --config tools/registration/ruff.toml` 0 错。沙箱侧自建 CPython 2.5.6 配方（`tools/registration/build_python25.sh` → `/home/user/py25`）复用有效，注意它是最小构建：没有 `big5` codec 与 `_json`/`select` 等扩展，桩件断言要按字节比。　README/TESTING 已同步更正（含「占位条款」旧说法与真机预期）。**未上传网盘**：出货包待另轮授权。 |
| 2026-10-15 | 「全都要」三件都落了。**(b) 入库**：新增子树 `tools/decompiler/output/script_fls_pycdc/`（499 个 pycdc 产物 + `manifest.json` + `README.md`，13.7 MB / 386,116 行；uncompyle6 侧已有完整源码的 18 个重复项不重复入库），并把 recover_entries 救回的 9 个产物并入 `output/script_fls/`；manifest 逐档记 `entry`/`status`/`lines`/`escaped_bytes`/`py25` 与 uncompyle6 成色，并钉住 script.fls（`8b6e9266…`）、keys（`43bb090d…`）、`batch_decompile.py`（`242543f8…`）三个输入哈希。`build_material_inventory.py` 会数 `script_fls/` 的 .py 个数，因此 `server/docs/SOURCE_EVIDENCE.md` 那句「只有 52 个 .py」加了勘误行（现 61 个）。**(a) 网盘**：`MXSJ_script_fls_pycdc_recovered_20261015.zip`（2,364,954 B，MD5 `c566766dc3a2ea96415711ac19851bd0`，Drive `1B588Ib1AlxycyzEXU9W4jZxiVe5xNFbd`，命名沿用 MXSJ_ 根目录惯例）含 pycdc 全树 517 个、recovered 9 条（含 `preload_mov.pyc`）、10 份逐条证据 JSON 与包内 README（覆盖率口径、三条限制、重跑配方）。**(c)** 工具与报告原地保留。覆盖率现状：可读源码 4,941/5,002 = 98.78%，仍零源码 61 条。 |
| 2026-10-15 | 第二引擎 `pycdc` 接上并做完交叉复核（新增 `tools/decompiler/crosscheck_pycdc.py` + `test_crosscheck_pycdc.py`，45 项测试、ruff 0 错；`--write` 只写语料下 `pycdc/` 独立树、绝不覆盖 uncompyle6 产物）。构建配方在沙箱验证可用（`pip install cmake` + 纯 C++，**不需要 flex/bison**，约 2 分钟）。**双引擎矩阵**：547 个 52 字节占位里 pycdc 完整解出 465 条、部分 23 条、自己崩 56 条；pycdc 净补 **546 条**可读源码（含 5 条需开 `--ladder`，正是 10-13 记为“救回”的 63/64/1013/1528/1854）；反向 75 条只有 uncompyle6 能出 → 单引擎结论不可信。定论残余：**两引擎+修复梯全开后仍零源码 61 条**（含 `1954`/`3066`/`4166`/`4691` 这 4 条连转译都过不去），覆盖率 4,941/5,002 = **98.78%**，清单 `residual_no_source.json`。用自建 CPython 2.5.6 实测可编译率，抓到系统性伪影：模块顶层那句 `return` 让 3,220 个产物编译不过（剥掉后 uncompyle6 75.4%、pycdc 48.4%），**回编译管线必须先剥再 `compile()` 校验**；另有 35 个产物含 NUL 字节、27 个编码声明与实际字节不符。语料与报告仍在 `/home/user/mxsj-dec/`（不入库）；`data/script.fls`、`script_fls_keys.json`、`batch_decompile.py` 三者未改。 |
| 2026-10-15 | **§5.1 红灯回绿**（§3.1 结案）：`agent_e_reproduction.json` 的 `inputs.shared_decoder.sha256` 按 `45d5590` 现值重钉（`7490dbab…`→`242543f8…`），并同步 `batch_001/manifest.json` 的 `tool_and_evidence_sha256`（证据 + `batch_decompile.py` 两项）。**关键补充**：§3.1 原修法只写了重生成证据一步，漏了 manifest——不改它会让你从 1 个 setUpClass ERROR 变成 2 个真 FAIL。全部 CSV 逐字节一致，`server/tests/architecture` 161/161 OK、`export_review_csv.py --check` 通过；`batch_decompile.py` 本体一行未动，`data/script.fls`（`8b6e9266…`）与 `script_fls_keys.json`（`43bb090d…`）与 manifest 内记录互相印证未变。本轮同时补上：`recover_entries.py` 的定点恢复（26 条 → 13 账目误差 / 9 救回 / 4 无解）与 `servicedata` 翻案，见 §6 上一条与逆向笔记 §4.5。 |
| 2026-10-15 | 「修 26 条」完成。新增 `tools/decompiler/recover_entries.py`（`test_recover_entries.py` 25 项测试、ruff 0 错）：以 import 方式复用 SHA 被 `agent_e_reproduction.json` 锁定的 `batch_decompile`，只改三处——不再用 `_decompile_ok` 否决整条、逐路径分量清洗 `co_filename`、反编译放进子进程带 `--decompile-timeout`；另加一级「catalog 密钥先缝口精修」。**26 条的真相**：13 条早有产物（9 条在 `script/unknown/`、4 条在真实模块路径，属上一轮按索引名清点的误差）、9 条本轮救回（6 条完整源码、2 条部分源码+marshal 结构摘要、1 条仅摘要并留 `.pyc` 供换引擎重试）、4 条确实解不开（`1954`/`3066`/`4166`/`4691`；`4166` 严格步进只差 76 字节，是下一个最有价值的目标）。语料现为 5,000 个 `.py` / 66 MB（生成物不入库）。**顺带翻案**：`servicedata` 其实一直在这版 `script.fls` 里——entry 1931 解出 `script\data\servicedata.py`（86 KB，`SERVICE_MSG` 11,602 B 真条款全文 + `SERVICE_MSG2`「線上遊戲定型化契約範本」，按 `main.g_LangVersion` 分两套），旧记「不在本版 script.fls 内」是因为该条在 catalog 里没有名字、按名检索不到；而 `script/login/register.py:171`、`loginin.py:696` 本来就 `import servicedata`。注册测试包把占位条款换成正式文本需重建 `out/script.fls` 并跑 13 项回归，**另轮授权**。`data/script.fls`、`tools/decompiler/script_fls_keys.json` 全程只读，SHA-256 复核未变（`8b6e9266…`/`43bb090d…`）；详见 `notes/opcode_mapping_and_decompilation.md` §4.5。 |
| 2026-10-15 | 真机「窗口标题 + 聊天乱码」定位**结案**（`notes/title_and_chat_encoding.md`）：客户端只有 `SetWindowTextA`（`SetWindowTextW` 计数 0），`misc.SetSysCaption → C_sys.SetCaption` 零转换，`TITLE_NAME_MX` 实为 **Big5 字节**，登录后标题再由「游戏名 + `server.ini` 服务器名 + 服务端下发角色名」三段拼接；`imwin7.dll` 全程按 ACP（`GetACP`/`MultiByteToWideChar`/`CharNextA`）处理输入与剪贴板 → 判定为**系统 ANSI 码页问题，非资源损坏**，首选用 Locale Emulator 以 cp950 单进程启动验证。为查证而把 `data/script.fls` **全量补反编译**：5002 条目 → 完整 4401 / 部分 28 / 明确失败 547（对应已知 546 stub 一类）/ 无产物 26，产出 62 MB 4987 文件；因 uncompyle6 在 `preload_mov`(2371)、`wingtypeposdata`(2679) 上指数级爆炸会堵死 worker 池，改用「一条一子进程＋超时」驱动（脚本在仓库外，未改被证据钉死的 `batch_decompile.py`）。**生成物按约定不入库**。顺带查实 `GetGameRegion()` 两处定义（`pubdelegate_v2.py:216` 与被 `@Override` 覆盖的 `delegate.py:227`）**均返回 `'cn'`**，即台服构建启用简中屏蔽词子集；已排除「cn/tw 表是码位表因而致乱码」的假设——`DATA` 实测为 0..3863 连续序号表，其影响是命中变 `*`/被拦，不是乱码。本轮只读解析、未执行任何游戏模块，未改客户端原包与三编辑器代码。 |
| 2026-10-14 | 注册第二期授权执行**已完成**：源码/原生布局/真实母版/回归测试/批量顺延方案/记账以提交 `22a3fab` 推送到固定分支 `arena/23e52686-mxsj-tw-2022`（未合入 master）；`registration_phase2.zip` 已上传 Google Drive，文件 ID `1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7`，[下载](https://drive.google.com/file/d/1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7/view)，24,189,000 B，ZIP MD5 `56c583afa4fa58b7fa8f47efb5a802c3`、SHA-256 `0541062f45a74bfbda99b62022d30c3929feb0e0979069d36b06d513d3cec97b`。上传返回的文件大小/MD5 与本地逐字节校验包一致，未改分享权限。只发第二期界面测试包，真实注册/查重/顺延/事务仍未实现；Windows 仍待用户按包内说明导入 `login/regterms.dlg` / `login/regform.dlg` 至 interface.fls 新包并实机验证。 |
| 2026-10-14 | 用户明确授权「提交推送上传」，注册第二期出货执行中。交付前重新跑 13/13 回归、ruff 0、wincompat 0 ERROR/0 WARNING；重建两张布局与 script.fls（SHA-256 `17a94c77…`），新包读回完整 marshal 比对及真 2.5.6 冒烟全绿，原 5000 条压缩负载全等。按工作区重新打包 `registration_phase2.zip`（24,189,000 B，MD5 `56c583afa4fa58b7fa8f47efb5a802c3`），逐文件解包字节比对和 ZIP CRC 通过；测试说明补充已定的「单条批量＋重名顺延」仍属待服务端实现规则。只交付原生注册 UI/校验/候选名单，不创建真实账号、不假报成功；Windows 新布局/勾选皮肤仍待用户实机。准备提交推送当前固定分支并上传网盘，完成后补编号。 |
| 2026-10-14 | 用户通过选项选定后续注册规则：**一条批量请求＋服务器跳过重名顺延**。请求带基础账号、数量 1/5、共用密码/邮箱及批次编号；五账号模式按原名、`_1`、`_2`…查找，最多 `_99` 且最终最长 16 位（14 位基础仅到 `_9`）。凑满五个才整批创建，凑不满就整批不创建；服务端唯一性/事务及同批重试返回原结果防止重复建五个；成功弹窗/登录预填使用服务器实际名单。单账号重名不擅自改名。**这是已定业务规则，不是已实现接口**：现运行源码仍不发送/查重/顺延，当前固定 pending 名单回调须在接口接通前调整，需补重名/耗尽/并发/重试验收。仅更新 README/STATUS，未改运行源码、未提交/推送/上传；选择方案不等于发布授权。本轮既有客户端离线回归复跑 13/13、ruff 0、wincompat 0/0（不作为顺延/事务/幂等服务端验收证据）。 |
| 2026-10-14 | 用户询问五账号的发送方式（连续五次/一次带标记）与重名顺延。核对现状：注册模块只在内存生成固定五份，不发数据、不查数据库、不顺延。已解释推荐的后续方案：单条批量业务请求（基础账号、数量 1/5、共用密码/邮箱、批次编号）由服务器统一查重和整批创建，回传实际名单，避免重试多建一组。发送方式/重名策略待用户选定；顺延必须守最终 16 位，14 位基础只到 `_9`、`_10` 超长，建议最多 `_99` 同时守长度上限，凑不齐则整批不创建。若定顺延，当前固定名单成功回调及登录预填须在接口接通前调整为服务器实际结果。**本轮未改运行源码、未实现接口、未提交/推送/上传**；上轮发布授权询问被跳过，不能视为授权。 |
| 2026-10-14 | 注册第二期增加用户点单的原生「註冊五個帳號」勾选（默认关闭）。用户通过选项确定基础账号上限 14 位，单账号仍 16 位；候选依次为原账号、`_1`~`_4`，共用密码/邮箱；下划线只作为自动后缀，切换不截断已有输入。已取回服务条款 `service.dlg`（Drive `1KaFXbFxU-VOJ5OJ0UIS7rINmn9uhJagS`，2984 B，SHA-256 `820f09a8…`）逐字拷为 regterms；五份真实模板重新取回并钉 SHA 防乱码、布局写入保留 Big5 文案/GBK 皮肤原字节。checkbox 采用原生 `CIMGCHECKBOX(interface.CImageCheckBox, 锚点, parent, 皮肤, True, 4)`，反汇编实证 LeftUp 先发消息再自动翻转，所以 manual=True 只翻一次；皮肤源于原 ui_res_style1 的登入注册勾选框。完成回调仅在已发送真请求且完整名单确认后列出五个账号（部分/重复/过期/旧表单回覆不能报全成功）；**本包无服务端接口，仅列待注册候选并明示尚未注册**。13/13 回归、ruff 0、wincompat 0/0；打包器增加禁止覆盖输入/硬链接别名、完整 marshal 往返相等断言与新包读回模块冒烟，原 5000 条压缩负载全等；script.fls SHA-256 `17a94c77e4cda673023f0e17221edb73f789183a0af0d4fcd5c6a1d3b651e0b2`、regform SHA-256 `8eeb7568…`。候选 zip 已本地打好并逐文件解包比对（MD5 `9220555bb808346eac38170c17c2c3dd`），未提交/推送/上传，等待授权与 Windows 实机。 |
| 2026-10-14 | 注册第一期 1.1 实机复测**全通**（用户确认）。第二期推进：用户回传 `reg.zip`（chgpwd/reg1/reg2/confirm 四张布局，已存 `tools/registration/templates/`）并拍板：注册协议直接拷贝服务条款 dlg、旧注册页风格与现行严重不符必须改；帐号规则与密码同口径（6~16 字母数字）、表单三按钮（上一步/确认注册/返回首页）。已完成：`build_regform_dlg.py` 从 chgpwd.dlg 派生 `regform.dlg`（登陆套件、四输入行、三按钮，经 UI 编辑器 codec 解析校验）；脚本 v2 改协议页照 `loginin.CServiceMessageDialog` 范式（regterms/loc_msg）、表单四框 + CPwdEdit 式输入限制 + 提示区，新 script.fls SHA-256 `5bfe2d797c4e5ce722f55152125fb91935c09afa957ffffb96e06e3056378829`、2.5.6 冒烟全绿。只差用户导出 `login/service.dlg`（见 §4）生成 regterms.dlg 后打包上传。 |
| 2026-10-14 | 注册第一期实机首测回報：条款页可打开、能进表单页、拒绝/上一步可返回；点「下一步」无反应。定位：原版脚本所有 UI 文案是 Big5 字节串，1.0 传 unicode 给 `ShowNewMessageBox`，其内部字节拼接解码失败、异常被客户端吞掉。1.1 修复：源码全部 UI 文案改 Big5 字节字面量（`MSG_*` 常量与原版逐字一致）、提交路径加 try/except 兜底弹框、表单消息与提交阶段写诊断 `photo\register_diag.txt`；构建器断言桩文案为 Big5 字节且不以 unicode 残留，2.5.6 冒烟全绿（含诊断文件断言）。新产物 `out/script.fls` SHA-256 `a90f0b62ceede2d6ebf35784eb52bf7992d6f75ff6c608016bbd88811cf9ef65`；1.1 包已上传网盘（Drive `1Hhnp_75jfCHlIZm5_qKYjWoUQ4GmT4DE`，zip MD5 `8abb9230886018f0cbd24199a15b58f4`，含测试说明），待用户实机复测。 |
| 2026-10-14 | 注册原生重做**第一期测试包建成**（`tools/registration/`，产物 `out/script.fls` SHA-256 `f062b8e9c1819d63fd4e4662bb3d974b5d0349a612c80b2c724b205cf0efe5fe`，git 忽略不入库）：新源码 `register.py`（条款页 `CRegTermsPanel`/表单页 `CRegFormPanel`/`CConfirm` 原样保留/对旧运营商网络名零残留断言）经自建 CPython 2.5.6 编译后整模块替换条目 4007，首页条目 337 打与 v1 已实机验证逐字节相同的 9 字节谓词补丁（其余 5000 条负载逐字节不变，构建器自动校验）；另用真 2.5.6 解释器加桩件把「开条款（servicedata 缺失走占位条款）→同意→表单（验证码/2980 占位已隐藏）→四种校验提示→桩提示→回条款/回首页→CConfirm 确认流程」全走通（`harness.py2`）。已知差异（README 记账）：本期表单沿用旧 reg2 版式=邮箱即帐号，独立帐号框待第二期改 layout；条款为占位文本（原 `servicedata` 模块不在本版 script.fls 内）。已上传网盘（Drive `1JS4-sYtKyZv6ANbJkk4m7TPebX3fivtY`，zip MD5 `273de8b9013ccc13d30b2460486c20d2`，含测试说明），待用户在已还原的测试副本实机验证；第二期等模板导出后给表单加帐号框并定版条款。 |
| 2026-10-14 | 注册原生重做开工前置全部就绪：① 用户确认测试副本已还原原包，并拍板表单字段=账号/密码/确认密码/邮箱、先过会员条款页、点确认注册后的桩文案=「伺服器尚未開放註冊，請稍後再試」；② 沙箱自建 CPython 2.5.6 成功（GitHub 源码 `-std=gnu89` 编译），玩具模块实证「自写 Py2.5 源码→编译→`pack_and_encrypt.py pack-script`→解密转译」往返无损，脚本重打包不再依赖 Windows；③ 加载链确认：台服走 `innerversionfun.LoadUIFileData`（原生 `C_sys.LoadFile` 解密后脚本层 `exec` 布局文本），新 `.dlg` 的 XOR 密钥由原生侧按明文头自解（与每条目随机密钥的实测一致），第一期先复用旧 `login/reg1.dlg`/`login/reg2.dlg`（只换脚本、不动 interface.fls），布局定版待用户导出模板（见 §4）。下一步：重写 `login/register.py`（条目 4007）+ 沿用 v1 已实证首页入口补丁，出第一期测试包。 |
| 2026-10-14 | UI 编辑器 0.7.0（脚本联动第一期 + 控件树锁定图标；Drive `18Tzk1T5KbDA4VhosnaRHrbwydwOSTwqJ`）：控件树改为两列、每行第二列小锁（默认开锁图标，点切换、与画布锁定双向同步；顺带修好控件树点击选中的反查失效）。新增索引生成器 `tools/script_link/`（基线转译+marshal/字节码挖掘 4,987/5,002 模块、2,920 布局、生成用时约 10 秒、5 条合成测试）；编辑器侧 `core/script_index.py` 查询层 + 随包 `data/script_index.json`；打开布局自动关联脚本（状态栏报数、左栏新增「脚本」页、点控件名回画布选中），代码现造按钮按真皮肤渲染（`_paint_code_skin`，取不到图回落占位）。119 通过 + 1 跳过、ruff 0、wincompat 0/0、从 zip 复跑绿；真包皮肤效果待用户用真实 `interface.fls` 验证（仓库无此包）。联动后续：脚本源码查看/编辑、加控件自动接线、脚本写回（§5 第 2 项），注册界面原生重做为第一个实战。 |
| 2026-10-14 | 用户决定暂缓：条目 1163/52226 的定点补解码先放一放（工具侧已万事俱备：0.3.7 导出解码失败条目必落原始 `.bin`，只差用户重导回传），优先转攻**注册界面原生重做**（§5 第 2 项 ⑤）。恢复 1163 线时第一步仍是导出 `interface_1163.bin`/`interface_52226.bin` 回传。 |
| 2026-10-14 | 资源编辑器 0.3.7（Drive `1ytgJ6Li81kdC0tA5VCrGJDwSvEfafnLE`）+ 用户回传 `1163b.zip` 复核：1162 导出的 PNG 是正常精灵帧（卷轴图局部）；52226 点击预览报 totalLines 不符、1163 报头解析越界，但两条**仍未随包回传**——点击只是预览报错，导出是独立动作，0.3.6 起导出解码失败条目必落原始 `.bin`（已用同形态样本在导出器实测），已请用户对 1163/52226 用右键「导出该条/导出选中」重导；用户另问 sound.fls 不能在编辑器播放——属实为缺功能（旧版只给 Hex 预览），0.3.7 新增音频识别与预览播放：`core/codecs/wav.py` 解析 RIFF 头（PCM 按字节数、GSM 每 65B 块 320 样本、IMA 每 1024B 块 2041 样本，fact 只兜底，与 libsndfile 实测一致），预览页可播放/停止/拖进度，解码走系统多媒体后端（沙箱无后端时降级为只看信息、已实测不崩；Windows 的 FFmpeg 后端对 PCM/IMA/GSM 一般可解，GSM 仍以实机为准）；49/49 绿、ruff 0、wincompat 0/0、zip 包内复跑通过。 |
| 2026-10-14 | 资源编辑器 0.3.6（Drive `19CbOVerFBV8qvT4ahQG6h7P7wEfRZ4k0`）：用户回传 `1163.zip` 分析定版——① 条目 1163 本体仍未拿到：旧导出遇精灵解码失败整条丢弃（`export_entries` 只记 failed 不落文件），0.3.6 改为回退原始字节 `.bin`，并让无真名的 XOR `.dlg` 按内容识别导出解密明文；② `item.fls` 四条样本（225/236/625/639）是新精灵变体 **T4/T5**：与 I0 同头同 token 文法、无调色板、像素为 3 字节 RGB（T4 用 u8 行长、T5 用 u16），四条均 `data_end==len` 且渲染为武器/翅膀/图鉴图逐张核对，资源与 UI 两边解码器已同步支持；③ `interface.fls` 的 `0x1C` 头条目（0016/0042/0047/52227）是 **Spine 骨骼二进制**（版本 3.4.02/3.6.52、BE 浮点、`./images/`、root 骨骼、附件名 `tx_*`/`Btxx_*`），不是坏精灵；用户导出的 interface_52227 与 0.3.4 校验报告的同号精灵对不上，疑保存新增条目排序插入造成校验下标整体偏移，待 0.3.6 发布后重导 1163 及相邻条目定点补解码；④ 其余样本定性：8 条 interface 无名条目是路径字典未收录的 XOR `.dlg`（已全部解密核对）、sound 大条目是 RIFF WAV（PCM/GSM610/IMA-ADPCM）、小条目是 GBK 重定向文本、`dialog/heroreplace.dlg` 正常。sound 条目导出自动落 `.wav`。44/44 绿、ruff 0、wincompat 0/0、zip 包内复跑通过。 |
| 2026-10-14 | 三个编辑器补齐工具约定 ①②：`map_editor` 新增 `bootstrap.py` + `启动地图编辑器.bat`、`tests/test_bootstrap.py`，ruff 74→0（定点改：E501 换行、`itertools.pairwise`、`zip(strict=True)`、`Iterator` 真实导入、`assertRaises(FlsError)` 等），`build.bat` 改名 `build_exe.bat` 并重写为纯 ASCII，spec 补 `exclude_binaries`，修 `test_cli_and_isolation` 读到开发者真实配置的隔离漏洞；`resource_editor` / `ui_editor` 各加 `build_exe.bat`、`<tool>.spec`、`run.py`、`requirements*.txt`、`.gitignore`（`build/` `dist/` `启动日志.txt`）。沙箱用桩库跑通 Qt offscreen：三套测试 88 / 37 / 92+1 跳过全绿；三份 spec onedir + onefile 干跑通过。**Windows 实机未验**（§3.5 ③）。 |
| 2026-10-14 | 用户实机确认：UI 编辑器 0.5.3 在真实 `interface.fls` 上加图存包成功、使用无报错——P0 写回修复 + 0.5.3 保存明示两轮闭环（§4 该行 UI 侧销项；资源编辑器同路径与 EXE 路径仍待验）。 |
| 2026-10-14 | 用户立「原生优先」规矩并写入 `AGENTS.md` §4（第 12、13 条）：原生能实现的必须按原生规范做；原生做不到、只能用替代方式的，必须反复向用户确认并获明确同意才能做。同时用户判定注册预览 v3.3 不规范（代码 overlay 拼控件、整图烤字按钮、包外散图）并作废——待其在 Windows 测试副本还原原包（`script.fls.before-registration-preview` 改回，SHA-256 `8b6e9266…`）并移除 `photo/registration_preview_v3`，勿再分发 v3/v3.2/v3.3。重做方向已定（§5 第 2 项）：注册界面按原生重做（原生 `.dlg` + 原生脚本套路，提交先留桩），与 UI 编辑器 × script.fls「一步到位」联动合并为一条线，注册界面为第一个实战。本轮发布：UI 编辑器 0.6.0（右键/复制粘贴/等比/锁定，Drive `1PHmkw04IIwRCdFT9Q58qfgxRS9WLrKUN`，MD5 `dd661dc6e60222c33a5ab4e0b6d0fd05`）与资源编辑器 0.3.5（工具栏，Drive `1ylUzM_i82-lzfaEp3WVx37gsNtNie4bo`，MD5 `ef29abe85fd1b7d7f1e0e00620f7eb31`）已提交推送并上传网盘。 |
| 2026-10-14 | 两编辑器补常用功能（用户点单）：资源编辑器 0.3.5 新增顶部图标工具栏（目录/打开/刷新/保存/另存/导出/导入/精灵/删除；图标在上+两字短名、与菜单共用同一动作、置灰同步，规格对齐 UI 编辑器；现画图标 `gui/icons.py`），40/40 绿。UI 编辑器 0.6.0 画布控件右键菜单 + 复制/粘贴/删除（Ctrl+C/Ctrl+V/Delete 走系统剪贴板 MIME，多选整组、粘贴偏移 16px 不重叠、整组一步撤销、删除改进为多选并汇总子控件数确认；焦点在文本框时三键回落文本编辑不误伤；model 新增 `insert_widget`）；追加「等比」工具栏开关（canvas `aspect_resize`：角把手按相对变化大的一轴定比例、边把手以中心为锚、最小 8px 保比例、Shift 临时等比）与「锁定」控件开关（工具栏/右键菜单/Ctrl+L：锁后拖不动/缩不了/删不掉、对齐分布绕开、父锁不挡子；`Widget.locked` 仅内存态不写 .dlg、不标脏不进撤销，撤销重建后按序号路径恢复锁定），112 通过 + 1 跳过绿。两边 ruff 0、wincompat 0/0；Windows 手感待用户确认。 |
| 2026-10-14 | 资源编辑器 0.3.4（用户实机反馈）：真实 interface.fls（53,555 条）仅新增一条无关条目，保存却被写后校验的逐条试解码拦下——条目 1163（头解析越界读）、52227（totalLines 与帧高和不符）是原包自带精灵，本机解码器未覆盖其变体，字节并未经手改动。改判责任：字节逐字比对仍是硬闸门，试解码只对本次改动/新增（`PackDocument.changed_indexes()`）的条目拦截，未改动者记 `sprite_undecodable` 在保存日志提示。补两条回归（未动不拦、改了必拦），39/39 绿。解码器缺口待样本：请用户从原包导出条目 1163/52227 的原始字节后再定点补。 |
| 2026-10-14 | UI 编辑器 0.5.3（用户 0.5.0 原生反馈两缺陷）：① 关闭窗口中画布补发缩放信号时 `_on_zoom_changed` 只判 `hasattr`，标签 C++ 对象已删仍 `setText` 抛 `RuntimeError: libshiboken ... already deleted`——改用 `shiboken6.isValid` 把关；② 「图片保存成功却没存进去」：挂账新图仅当被当前布局引用才随包写（设计如此），旧成功弹窗不报实际写入数，未引用被静默漏过、且保存默认生成 `原名_patched.fls` 新包，用户重开原包自然还是原条数——弹窗改明示新包路径、条目总数、实际写入/替换数，有未引用挂账图时点名警告（报告新增 `staged_unreferenced`/`entries_after`）。补两条回归测试，94+1 跳过全绿。用户侧用 0.5.0 时另请注意：务必升级到含 P0 写回修复的版本再对真实包加图。 |
| 2026-10-14 | 工具开发约定：新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（PEP 8 + 模块化、GUI 一律 PySide6、必须有 `bootstrap.py` 自检启动与 `build_exe.bat`、Linux→Windows 交付检查）与 AGENTS §5 摘要；新增 `tools/devkit/check_windows_compat.py`（Windows 兼容静态检查，29 测试）、根 `ruff.toml`、`.editorconfig`、`.gitattributes`（`*.bat` CRLF）；`map_editor/pyproject.toml` 补 ruff 配置，两个编辑器的 ruff 规则加 `W`；修 Windows 必坏项（`bytecode_58_<module>.bin` 改名、bat CRLF、`build.bat` 加 `chcp 65001`）。差距清单见 §3.5。 |
| 2026-10-14 | 文档整理：新增 `AGENTS.md`、`docs/STATUS.md`、`docs/archive/`（归档 14 个过期快照：根目录 `AGENT_HANDOFF.md`、`work/` 下 10-09/10-10 交接与分派文档、地图编辑器交接报告、`CLIENT_DATA_AGENT_HANDOFF.md`、4 份 route-scope 残留）；v3.3 事实表抽成 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md`；刷新 `README.md`（补两个编辑器、修正测试计数、状态移到本文）、`server/README.md`、`tools/client_patches/README.md`、`work/.../INDEX.md`。未改任何代码、测试、数据与二进制。 |
| 2026-10-13 | 资源编辑器 0.3.3 / UI 编辑器 0.5.2：写回目录不变量 P0 修复；decoder 分段参数修复（引发 §3.1）。 |
| 2026-10-12 | PR #26/#27 合入 master：复核链、注册 UI v3.3、网关设计、地图编辑器及其修复。 |
| 2026-10-15 | **沙箱重置 → 重建并出货注册测试包**：`/home/user` 下的 CPython 2.5.6、uncompyle6 venv、79 MB 反编译语料与 `tools/registration/out/` 全部消失；本地 `.git` 退回 `fa13871`。按 §1-2「先对比远程」处置：`git fetch` + 确认工作区与远端 tip `421ab91` 之间**只有 515 个缺失、零内容差异**，故 `git reset --hard` 无损对齐；再用 `build_python25.sh`（走 codeload，允许名单内）重建 2.5.6、重跑构建器 → `out/script.fls` SHA-256 与重置前**逐字节一致**（`ed0f4126…`），13/13 回归与 ruff 仍全绿。**出货记录**：包 `registration_phase2b_terms_confirm.zip`（24,190,980 B，MD5 `e5177426…`，SHA-256 `c30a6387…`）已传网盘根目录 `0AM2SnEVIISYdUk9PVA`，id `1k5dE9pt9NQL-ywhh27U_lM6JfcAEQD7b`，未改分享权限；含 `data/script.fls` + 两张 `.dlg` + `TESTING.md`。教训：生成物只在 `out/` 会随沙箱重置消失，要留档就得上传 |
| 2026-10-15 | 新增 **`docs/DECOMPILE_CORPUS.md`**（全量反编译语料的重建配方与使用规则），并从根 `README.md` 速查表、`AGENTS.md` §2 目录地图 + §6 工作方式、`output/script_fls_pycdc/README.md` 四处指过去。写之前把每条命令实测了一遍，捞到三个会在沙箱重置后坑死下一个人的事实：① `batch_decompile.py` 用 `import uncompyle6`，**解释器选错就把 5,002 条全写成 52 字节占位且退出码 0**（同一条 entry 0：`python3` → 0/1、52 B；venv → 1/1、316 B，已复现）；② `--engine auto` 的 pycdc 回退只认硬编码 `/usr/local/bin/pycdc`，不建软链就静默不用第二引擎；③ `--entry 1931` 在 batch 里是静默零产出（需修复梯，走 `recover_entries.py --entries` 实测 2.3 s 得 86,917 B 的 `script/data/servicedata.py`，里面 `CONFIRM_MSG` 计数 0、`SERVICE_MSG` 计数 3 ⇒ 上一轮那条判定现在有了可复现的两行命令），且 `--entry <文本>` 走 `script-catalog.csv` 的 filename 列、对 12+ 条无名条目必漏。另记：`accounting.json` 无生成器（一次性脚本产物），文档里写清了自己怎么补 或用 `--entries` 绕开。**副作用**：未改三个工具的任何一行行为，只加文档；`data/script.fls` 等锁定输入 SHA 复核未变 |
| 2026-10-15 | 把反编译语料的**三个静默失效**工程化（用户「好」授权）：`batch_decompile.py` 新增 `preflight()`（缺 uncompyle6 直接拒绝开跑，旧行为要显式 `--allow-missing-engine`）、`resolve_pycdc_bin()`（`--pycdc`/`$MXSJ_PYCDC`/旧硬编码路径/`PATH`，`--engine pycdc` 而无 pycdc 时拒绝）、`script/failed/` 的 `TRANSMAP FAILED` 明示标记 + `--report` 清点表（键名 `failed`/`missing` 直接喂 crosscheck/recover，一次性脚本缺口关闭）。新增 `test_batch_decompile.py` 21 项（其中一条把自己的实现缺陷抓出来了：标记正文原本含 `Decompilation failed` 原文，会被 `uncompyle6_state()` 误判成占位 → 已改措辞并加断言）。P4 单条超时隔离仍是待办。**连带义务**：全部做完——`agent_e_reproduction.json` 重钉后 899 个字段里**只有 `inputs.shared_decoder.sha256` 变化**（`242543f8…`→`a7474223…`），地图/NPC 结果零差异；`batch_001/manifest.json` 按 §3.1 干跑对比后只拷 manifest，差异恰好 2 个哈希字段，CSV 与 maps_npcs 逐字节全同；`export_review_csv.py --check` = pass；架构 161 项 + decompiler 66 项全绿；`batch_decompile.py` ruff 从 40 → 39（未新增，E501 全是既有的）；`server/tests` 那 3 个 review_api 报错经 `git stash` 对照确认为沙箱缺 fastapi，与本次无关。`docs/DECOMPILE_CORPUS.md` §3–§4/§7 与 notes §4.6 同步（含「新版会数出 5,002 个 .py」的对账口径）|
| 2026-10-15 | **用用户网盘 `script1015.fls` 当基线重做注册包并出货**（用户「从网盘下载…基于这个重新改」，选定「就用这份重做」而非保留调试脚手架）。取回：`download_file` 落盘 24,264,943 B，MD5 `f85917c2b57cad92f486004f02c43378`、SHA-256 `77b3eac611f52cf8…6564466`（与 Drive 元数据一致）。逐条比对 5,002 条 ⇒ **只有 337、4007 与仓库基线不同**，其余 5,000 条压缩负载逐字节全同；337 已含同一个 9 字节补丁（逐字节相同），4007 是 A 案**之前**的旧 `register`（`CConfirm` 仍裸取 `servicedata.CONFIRM_MSG` 那条死路，另多 `_DiagFailure`/`_ImportRuntime`/`_RecoverEntry`/`_CreateFormEdit` 调试脚手架；uncompyle6 到 1,202 行 parse error，比我们的 451 行版本胖）。⇒ 该归档**不含任何我们无法复现的内容**，重建产物 SHA-256 仍是 `ed0f4126…`（与已出货那颗逐字节相同）。　工具侧：`build_native_registration.py` 加 `--base-sha256`（不符即退出并回显实测 SHA + 可复制参数）、`--report`（验证全通过才落 JSON 构建记录：基线/密钥表/源码/产物 SHA + 337 处理方式 + 实际改动条目），并把 337 判定抽成纯函数 `tw_predicate_window`（clean/patched/拒绝三态）——外来基线若是已补形态就明示「原樣保留」而不是重复写入，认不得就报错；新增 `tests/test_build_base.py` 7 项，本目录 20/20 绿，两条分支各实测一次。　**出货**：`registration_phase2b_on_script1015base.zip`（24,190,255 B，MD5 `f3bdaf9a…`，SHA-256 `437fd798…`）→ 网盘根目录 `0AM2SnEVIISYdUk9PVA`，id `1KDEq1eiF_RJMM4l7pDvorScuMAIo_Ojo`，Drive 侧 MD5 已核对一致，未改分享权限；比上一包多 `build_report.json`。　另记（沙箱第二次重置）：py2.5.6 用 `tools/registration/build_python25.sh` 重建约 1 分钟；uncompyle6 venv `python3 -m venv` + `pip install uncompyle6`（3.9.3）可用；`data/script.fls` 与 `script_fls_keys.json` SHA 未变 |
| 2026-10-15 | **实机回归：装 `ed0f4126…` 后协议页点「我同意」进不去表单页（点了没反应）→ 已修并出货 `f0253c95…`**。把用户网盘里能进表单页的那版 4007 解出来逐函数比字节，找到两条根因：(1) 表单四框字体我用了 `interface.FONT_EDIT`（照 `chgpwd.py`），旧版实机用的是 `interface.FontLT14_3`——而 `harness.py2` 桩件恰好定义了 `FONT_EDIT=1`/`COLOR_EDIT=6`，**桩件世界永远测不出缺常量**（又一次「桩件 ≠ 归档真值」）；(2) 我上一轮「清理调试脚手架」把 `Show`/`Step` 的 try/except + `_DiagFailure` + `_RecoverEntry` 一起删了 ⇒ 客户端吞异常 = 静默无反应、日志也空。修法不是回退：新增 `_EditFont()`/`_HintColor()`（优先原版常量，缺则退回实机验证过的 `FontLT14_3`/`0` 并把选中哪个写进日志）、`_CreateFormEdit()`（先 `GetObject` 验锚点，缺则 `anchor missing` 再抛；已核对 `regform.dlg` 确有 account/pwd/pwd2/email/txt/chk_five）、`Step`/`Show` 全兜底（`_DiagFailure` 只记类型名不记值 + `_RecoverEntry` 解除 InputSecrecy 回首页 + 弹 `MSG_UNKNOWN_ERR`），规则：**绝不允许「点了什么都没发生」**。防复发：构建器把 `_CreateFormEdit`/`_DiagFailure`/`_RecoverEntry` 三个名字列入必存在清单（删掉就拒绝出货）；`harness.py2` 加 `MXSJ_HARNESS_MODE=no_font_edit\|missing_layout` 两个残酷世界，`test_runtime.py` 各断言一轮 ⇒ 本目录 21/21 绿、ruff 0、wincompat 0/0。产物 24,264,817 B，SHA-256 `f0253c9536d95e0a82642eb1a109d16bbdd07eeaf7aae2504e747d25cdf0e1f6`（4007 负载仍 44,362 B 定长、编译 pyc 20,748 B）；基线仍是用户网盘 `script1015.fls`（`77b3eac6…`，337 保留）。TESTING 增加日志行对照表。另补上出货打包工具 `tools/registration/make_release.py`（固定「排除自身 + 名称排序 + 时间戳钉死」，产出可复现并 `--check` 自检）——起因是手工 `find\|xargs sha256sum > SHA256SUMS.txt` 会先把目标建成空文件再收进清单，**清单里那行自指哈希永远校验不过**，本轮之前打的包都有这毛病（只影响校验、不影响包内容）。新增 5 项打包回归后本目录 26/26 绿、ruff 0、wincompat 0/0。**出货**：`registration_phase2c_formpage_fix.zip`（24,194,889 B，MD5 `d8ec2994…`，SHA-256 `9be556bb…`）→ 网盘根目录 `0AM2SnEVIISYdUk9PVA`，id `1_IV9mmXetexJ_UnaGaeuyuRFAXd27goX`，Drive 侧 MD5 已核对一致，未改分享权限 |
| 2026-10-15 | 用户问「mxLauncher.exe / mx.exe / mxmain.dll 能不能反编译出源码」⇒ 新增 **`notes/client_binary_reversibility.md`**，全部实测：`mx.exe` 与 `mxmain.dll` **MD5 相同（同一颗）**，其导出表自报 `ClientLoader.exe` 且只导出 2 个具名函数（`JSON_DecodeObject`/`JSON_EncodeObject`，MSVC 修饰名已手工还原签名）；`objdump -h` + 逐节香农熵显示 `.text` 6.64（没被壳盖住，可反汇编）而 `_dyprot0/_dyprot1` 7.85/7.72 —— **5.2 MB ≈ 全镜像 54% 是多益保护壳的加密段**；无符号表无 PDB；依赖 37 个 DLL 且**不含任何 python2x.dll**（内嵌定制解释器）；明文可得的结构信息只有 331 个 RTTI 类名（`CGameWnd`/`CMainWnd`/`CChatWnd`…）。**关键负面结果**：全仓二进制明文里 `CCombPanel`/`FONT_EDIT`/`PyArg_ParseTuple` 命中均为 0 ⇒ `interface`/`combdialog` 的注册名不在明文里，**上一轮想用 strings 证「本版没有 FONT_EDIT」是不成立的（两个方向都测不出）**，该问题只能靠运行期日志回答（新包的 `font FONT_EDIT` / `font fallback FontLT14_3` 行会自己说）。`mxLauncher.exe` 无壳、MFC(VS2003) 静态链接、`.rsrc` 1.13 MB + 115 个 RTTI 类名（`CBackWin`/`CMxBitmapButton`/`CMxLink`/`CMxProgressCtrl`）⇒ 可出伪 C 与近乎原样的资源清单，但仍是"看得懂流程"，不是可重编源码。成本表写在文档 §4：定点问题走运行期探针（分钟级）＞ 启动器资源清单（半天）＞ 全量反编译引擎（人年级，且当前无待办需要它）；沙箱无 java/IDA，只够 capstone 定点反汇编 |
| 2026-10-15 | 用户问「mxLauncher.exe 能拿到资源包？」⇒ 落成 **`tools/data-parser/pe_resource_dump.py`**（只用标准库的 PE `.rsrc` 抽取器：BITMAP 补 BMP 头、GROUP_ICON/GROUP_CURSOR 组装成 `.ico`/`.cur`、DLGTEMPLATE 与 DLGTEMPLATEEX 两种版式都解、RT_STRING、VS_VERSIONINFO、具名型別 PNG；解不动的一律留原字节并在 manifest 记 `note`，**不猜**），配 12 项回归测试（自建最小 PE 验结构 + 真档核对）。实测 `mxLauncher.exe` **86 条资源全部落地**：30 张 BMP 切片、**一张 982×553 / 545,162 B 的整套启动器皮肤 PNG**（内嵌 Photoshop CC 2015 XMP ⇒ 皮肤 2015 年重画，版式版权字串还是 `Copyright (C) 2008`）、15 个 `.cur`、1 个 `.ico`、82 条字串（id 117 =「关于 mxstartup(&A)...」）、**5 个对话框版式全解**（`100`「梦想世界更新程序」235×55；`102` 415×307，id 1000 是 **WebBrowser ActiveX** ⇒ 新闻/广告走 IE 控件而非自绘），`file_version=128.0.1.0` 与 `update.ini` 的 `2.27.2` 不一致 ⇒ **VERSION 资源不能当版本号**。**「资源包」的主体不在这颗 exe 里**：游戏资源是 `data/*.fls` 7 个（走既有 `tools/decompiler` / `repack_fls.py`）；启动器皮肤另可读 `resource\updaterbk.res` 与 `bk%d.png`（本仓库 `resource/` 只剩空的 `history.his` ⇒ 实机用的就是内嵌那张 PNG）；更新链路是 `update.ini` 的 `UpdateURL`/`FileInfoURL`（服务器侧 MD5 清单）+ `[Download] DLServerUrl`，下载器在 `ResLib.dll`（libcurl，**无导出表**，`exe/ResLib.dll` 是另一颗）；`patch/mx.bin` 与 `mxLauncher.exe` **MD5 相同** ⇒ 就是「新版启动器自己」；`AddFontResourceA` + `Fonts\FZLanTingYuan-DB-GBK.ttf` 说明 `Fonts/` 那 4 个 ttf 由启动器注册（**GBK 版**，与繁中显示那条线相关）。本目录 12/12 绿、ruff 0；导出产物留在 `scratch/launcher_out/`（87 档 / 1.2 MB，按红线不入库）；结论写进 `notes/client_binary_reversibility.md` §6–§7，README 与 AGENTS 索引已加 |
| 2026-10-15 | 接问「原先那颗 exe 的文本乱码能解决吗」⇒ 能，且已定位：`mxLauncher.exe` **是 ANSI 建的档**（USER32 只导入 `CreateWindowExA`/`SetWindowTextA`/`GetWindowTextA`/`DrawTextA`/`MessageBoxA`/`DefWindowProcA`，全表 **A 系 113 / W 系 10**），并导入 `GetACP`+`MultiByteToWideChar`+`WideCharToMultiByte`，串里**没有** `big5`/`cp936`/`CP_UTF8` ⇒ 它不自己挑码页，**所有文字都过一次系统 ANSI 码页**；而 `.rsrc` 版式里的字是 UTF-16 简体（「梦想世界更新程序」「确定」），CP_ACP=936 无损、CP950 丢字或变成另一个字、CP1252 变 `?`。字体是另一层：版式用 `MS Shell Dlg`，繁中系统映射到 PMingLiU（**无简体字形，码页对了也照样方块**），启动器只给自绘控件 `AddFontResourceA` 注册 `Fonts\FZLanTingYuan-DB-GBK.ttf`。⇒ 三条解法（前两条不动 exe）：系统「非 Unicode 程序的语言」改简中 / 按程序模拟区域工具只给它换码页 / 把字从文字改成图（改 DIALOG 字串 + 皮肤 PNG 重画简体）。写成 `notes/client_binary_reversibility.md` §8。**与游戏内文本（引擎内嵌 Big5 + 标题走 SetWindowTextA）是两套原因，别一起治** |
| 2026-10-15 | 使用者選了「把啟動器圖上的繁字換成簡體」並要先看效果 ⇒ 新工具 **`tools/data-parser/skin_label_patch.py`**（逐行中位色／兩端插值擦掉皮膚圖上的舊字，再用客戶端自帶 `Fonts/FZLanTingYuan-DB-GBK.ttf` 重畫簡體，`--pad-to` 靠 IEND 前插 `tEXt` 塊把 PNG 湊成**原字節數**）與 **`pe_resource_patch.py`**（`.rsrc` 原位寫回：長度不符直接拒、寫完自己反讀校驗、`--strip-signature` 清目錄並砍檔尾證書）。實測：`mxLauncher.exe` 的 `PNG_1`（offset 516,416 / 545,162 B / lang 2052）換掉 8 個標籤後**逐位元組等長**，反讀 86 條資源、型別統計、5 個版式全不變；產物 `scratch/mxLauncher_simplified.exe`（1,646,592 B，簽名已剝）**未入庫、原檔未動**。掃過全部資源文字：除皮膚圖外沒有繁體（版式與 STRING 表本來就是簡體，它們花屏是码页問題）⇒ 圖改完繁體就到頭；logo「新夢想世界」是手繪圖形未動。新增 12 項測試（含「原載荷寫回 ⇒ 整檔 sha256 不變」不变量），`tools/data-parser` 36/36 綠、ruff 0；方法与邊界寫進 `notes/client_binary_reversibility.md` §9 |

## 7. 如何更新本文

> 以下保留历史内容及原章节锚点；不是本轮任务或授权。当前等待项、下一步与文档维护职责以 §1–§2 和 ROADMAP 为准。

每轮结束：改快照日期 → 更新 §1 分支/基线 → 用**实际跑过**的结果更新 §2（没跑就写“未执行”）→ 增删 §3/§4 → 调整 §5 → 在 §6 追加一行。不要删历史行；超过一屏时把旧行搬到 `archive/`。


## 3.43 C login第二轮预审（2026-10-16）

- 固定PR #35 head `242fd8c941997f22a47f06069554cebba20d79a3`；隔离覆盖A远端e49cb00审查，未合入。
- 已确认改正selectserver误链、函数级LoginOk摘要、ShowLogin行段；main候选仅改.py.txt，原字节SHA不变，不能视为字符保真问题已修。
- 阻塞：LoginOk旧问答未同步；ShowLogin与协议检查条件失真；问答/分支多处证据不覆盖断言；关系方向/kind需复核；恢复来源/有损字串处理需说明。
- 本轮严格validate20/4/H0、ruff含spec、wincompat67路径/26脚本均通过；unittest 78项=67通过+11 GUI因无Qt跳过，0失败。游戏/Windows/EXE未验。
- 报告：`docs/evidence/script_manual_C_242fd8c_A_review_20261016.md`；PR评论：https://github.com/a565551313/MXSJ_TW_2022/pull/35#issuecomment-6203416829 。H仍后置，正式数据仍20历史种子/1样板/H0。
- 安全边界：初期本地HEAD8212b26与远端A e49cb00不一致；临时索引核查证实工作文件与远端完全一致，仅新增本报告与STATUS补充。备份索引后只对齐同一分支HEAD/index，无工作文件覆盖，无reset/切分支/stash/强推。收据`docs/evidence/git_metadata_alignment_20261016.json`；本报告随后提交推送，PR评论已发布。


## 3.44 E network第二轮闭环与H输入准备（2026-10-16）

- 固定PR #36 `60c573956f12a739712e4b24ddf1fb852f71bff0`，仅network六文件；相对首轮五项修订经A独立核对闭环，可入H待审队列。没有合并，没有代写H accepted。
- 用Python3.11.2/u6 3.9.3/xdis6.1.8/spark-parser1.9.0/click8.5.0只读定点恢复3176/2170/871/516/4293：五条稳定恢复头与固定keys/bounds核对，精确去六头正文SHA 5/5匹配；871/516与仓库旧候选正文原字节一致。原包/参数表/工具SHA均未变，未执行游戏模块、未定点恢复1288。
- OnError条件及守卫、OnLogin后隐藏面板、未引用Success成功链口径、可复现正文摘要和计时单位已同步；帧长2/3字节、队列/成功回调/瞬连定时异常继续待核，不预判真实行为。
- E覆盖来源验证20/5/H0、C+E草稿覆盖20/8/H0通过，均仅3970未编入种子警告。C退修结论不变。三组各78项=67通过+11 GUI跳过/0失败；已装PySide6但缺系统libGL.so.1。ruff含spec通过，E静态69路径/26脚本全0，两组离线HTML构建通过；本轮浏览器、Windows/EXE、原生/实机/服务端未验。
- 报告：`docs/evidence/script_manual_E_60c5739_A_review_20261016.md`；机器收据：`docs/evidence/script_manual_E_60c5739_A_validation_20261016.json`；H固定字节输入：`script_manual/coordination/H_QUEUE_E_60c5739.json`。交接单不是H审核，也未从此会话启动/联系其他独立会话。
- 协调表仅更新C=blocked、E=submitted；其余assigned不等于已经开工。截至查询只有C/E两个开放手册PR；B目录及D/F/G十二篇样板与C返修仍是下一卡口，H按既定20样板齐备后独审。正式数据仍20历史种子/1样板/H0。
- 上轮本地Git元数据回退已安全核实并只对齐同分支HEAD/index，未覆盖任何工作文件。检查点94e6d33已推送，工作区随后只新增本轮A报告/协调资料；继续仅在固定A分支提交推送。


## 3.45 B/D/F首轮集成预审（2026-10-16）

- 固定B `e516b63499615af7892ece0a217bd36c35894032`、D `1f6fdd323475e3940ea95b19e62c452e58dbd259`、F `12ce0c63ab50db00050365de5a6891fd4fa37ce6`，范围各自inventory/ui_chat/battle，无越域。截至查询三者只有分支提交、没有PR，须owner各自在固定分支开PR到A；未替owner切分支或创建PR。
- B用A真实20种子独立sample→full，两次script提取和data提取后5135行/128382函数记录与提交逐字节一致，SHA35203710d79acd08b080e9d08fa1357ea9f8c29464a64eeb1a34aa27e36a9efd。原包/参数/13工具指纹一致，1288的read_stored请求为0。发现70个kwargs-only签名多加裸*、48个内部.n形参须置未知或安全重建；四条拒绝旧路径的原线索未实际保留在回执。B待修，不改A测试。
- D独立重现12个白名单pyc与候选摘要，3142行摘录逐条匹配；菜单信号实际锻造委托、聊天左右键层次、CClickBox签名与快捷键守卫抽查吻合。83函数/75分支为有限样板，可入H待审；损坏标识符、动态/原生/实机边界继续保留。交接单`script_manual/coordination/H_QUEUE_D_1f6fdd3.json`。
- F独立定点探针697/1612/8均u6 3.9.3 decompile_ok/source（2640/45/176行），1406仍decompile_fail/13行partial+digest，不冒称可用完整源。F需将三份名称底稿补为有限说明，并修netwar三处globals假引用、入场动画pass条件、跨模块入队/循环切换证据和来源说明。main仍C唯一owner。
- 外部B+D+E+F覆盖：5135登记/13说明/1排除/H0；再叠C草稿：5135/16/1/H0；严格来源和full闸门均通过，无关联警告。两组dev2各78项=67通过+11 GUI跳过/0失败；旧75项种子耦合失败不再存在，不等于B/F内容正确。ruff含B脚本/spec通过，静态89路径/27脚本全0，13说明全目录离线HTML25816929字节构建成功；浏览器本轮未验，真实Qt缺libGL，Windows/EXE/游戏/原生/服务端未验。
- 报告`docs/evidence/script_manual_BDF_A_review_20261016.md`；机器收据`docs/evidence/script_manual_BDF_A_validation_20261016.json`含固定SHA、全部坏签名、D来源复现、F探针及回归日志摘要。仅提交A报告/协调资料，不提交候选/生成站/全量覆盖产物。
- 协调表D=submitted、F=blocked，保持C=blocked/E=submitted/G=assigned；B状态记报告。D/E共8篇仅A有限预审待H，不是H accepted；B/C/F待修，G未交，H按20篇齐备后独审。正式数据仍20历史种子/1样板/H0，所有领域/目录提交均未合入。


## 3.46 H宕机后用户授权A代审（2026-10-16）

- 用户明确授权“H宕机了你审吧”。A以实际身份`A_delegate`承担审核，非独立H，不再等20篇齐备；旧H_QUEUE保持固定历史输入，其等待gate由本轮覆盖。
- 固定D `1f6fdd323475e3940ea95b19e62c452e58dbd259`、E `60c573956f12a739712e4b24ddf1fb852f71bff0`。逐项核八篇240类/函数、118已列关键分支及职责/资源/上下游/修改指南/局限；240定义/非空签名字面匹配仅自动辅助，不等于语义验收。
- **三篇有限通过**：interface22/24、key19/13、chatoutput25/21，共66函数/58分支。已标注的损坏标识符/焦点/滚动异常、动态调用/原生事件/编码/资源/实机未知继续保留，不声称全模块解释完或候选可回编。
- **五篇退修、11项P2**：mainmenu.PushCall无条件排队被写成立即回调，Recall推导式异常未交代；net的组包顺序/帧率缩放与查名/队列异常摘要；netquicklogin.ModuleReset全局作用域与未重置标志、问答错引状态段；netserver把属性存在当握手、组包顺序、未来时间戳刷新分支、递归完整谓词；connect无代理摘要写成两路而实际二选一。均要求修文档/证据，不修游戏候选后冒充原文。
- 八份真实审核记录在`script_manual/coordination/delegated_reviews_20261016/*.json.template`，绑定原JSON原字节SHA，暂不加载以免正式目录引用未合正文。机器收据含逐函数/分支检查与全部SHA。**未获领域合并授权，本轮未合B–G；正式20种子/1说明/0通过**。任务表三篇仍submitted，mainmenu及E四篇blocked；B/C/F既有退修、G待交不放宽。
- 工具升0.1.0.dev3：schema兼容H/A_delegate，代审必须填授权；表格、原生详情、离线页显示实际身份/意见/授权/审核绑定SHA，总数改称审核通过。C等作者不可自批，H旧记录兼容，孤立/重复拒绝和原字节stale继续有效。
- 正式与外置DE覆盖来源校验通过；外置只用A20种子，20/9/3且7条未建档关联警告保留，未借B问题目录消警告或声称full。3份实际通过JSON逐个加1字节均降stale、通过数3→2，恢复原字节后3。
- 根/覆盖两组各82项=71通过+11 Qt因libGL.so.1缺失跳过/0失败；ruff含spec、Windows静态全0、JS语法通过。外置HTML构建与jsdom26.1.0执行页面脚本通过，核3通过/5退修与身份意见展示；不是实际浏览器、Qt、Windows/EXE、游戏/原生/实服测试。
- B PR38/F PR37发现base误指master，gh pr edit经典Projects GraphQL错误后改用REST PATCH，响应确认均为A固定分支、head未变；未代开D PR或合任何领域PR。
- 报告：`docs/evidence/script_manual_DE_A_delegated_review_20261016.md`；收据：`docs/evidence/script_manual_DE_A_delegated_validation_20261016.json`。仅A工具/协议、协调、审核与状态，不搬入完整候选、生成HTML、npm依赖或游戏包，无网盘上传。


## 3.47 G停工后由A补四篇有限说明（2026-10-16）

- 用户报告G停工，A承接G固定四篇，开工前A69ca61f已推且干净。只补G，不接管C–F返修；owner=G保留任务包身份，author明确A代写，**不为自己四篇创建A_delegate accepted**。task状态四篇submitted表示有限稿待复核，不代表独立审核完成。
- hero3038/dlgitem717/task1129/npc949两轮定点恢复均baseline/decompile_ok/source；固定script/keys摘要未变，去六头正文4/4逐字节相等。完整输出形状不等于原始源码/语义正确。原候选、pyc、两轮产物留仓库外。
- 新增四份gameplay JSON：13/12、13/19、13/14、12/17函数/分支，合计**51/62**，每篇职责、资源/上下游、3项修改问答与有限范围/实机局限。四份小摘录951行逐行与候选相等，含候选全文/正文SHA和原行号。不是全函数解释。
- 明确保留task.RefreshNecessary拆错变量、TaskSatisfy/UnSatisfy异常推导式，角色ID类型/显示OR及私有配置假值回落，物品布局双入口/隐藏亦构造/装饰器未知，普通与任务NPC点击门禁/距离/重叠/任务分流。没有修游戏候选凑解释，不把发送当服务器成功。
- 正式schema/来源SHA/行号校验过，现**20种子/5说明/0通过**，未使用B问题全量目录或声称full通过；其他领域PR仍未合，D/E三份有限通过仍在固定模板等待授权集成与原字节核对。
- unittest82项=71通过+11 Qt缺libGL.so.1跳过/0失败；ruff含spec、Windows静态全0；外置HTML构建和jsdom26.1.0执行真实页面脚本通过，四中文词命中正确模块且均显示A作者/待审。非真实浏览器、Qt、Windows/EXE、游戏、原生或服务端验收。
- 报告`docs/evidence/script_manual_G_A_draft_20261016.md`；机器收据`docs/evidence/script_manual_G_A_draft_validation_20261016.json`，含stored/pyc/candidate/正文/JSON摘要、两轮复现与测试产物指纹。未改原包/参数/编辑器/启动器，未上传或合任何领域PR。


## 3.48 用户授权先合并再重新分配给全新agent（2026-10-16）

- 用户明确要求先合现有成果，再按合并后实际进展分给全新agent，不是原会话。A开工前9880457已推且干净；仅在固定A分支操作，不合master。
- `gh pr merge 38/35/36/37 --merge`分别执行成功并读回merged；对应合并7a0a05a/82d42b3/ccf602c/dbf3406。D无PR，按授权以固定1f6fdd3非快进merge为7d32e5340b0ab4168f725d238d767ad6232f715d并推A；G四篇已在9880457，无重复合入。
- 激活八份此前真实A_delegate审核前，逐个比较合入正文原JSON SHA全部相同；三有限通过interface/key/chatoutput，mainmenu和四网络五退修。旧templates不改、只载canonical `reviews/8b6e9266_<entry>.json`，没有给G自批或新造H记录。
- 当前**5135登记/20说明/3通过/5退修review/12pending/1排除**；无关联警告。C155/30、D83/75、E157/43、F259/10、G51/62，共705函数记录/220分支；F173条多为名称底稿，不能说全部解释完。inventory128382只是结构记录，B的70/48签名和4条fallback仍需修，full/schema通过不闭合语义。
- 全新任务：N1目录，N2登录/main，N3主菜单D1及保护已过三篇，N4四网络10项，N5战斗补解释/证据，N6接管A代写gameplay，N7全新独立H角色按批复核。七份自包含卡在`script_manual/coordination/new_agents_20261016/N1.md`至N7.md，入口`NEW_AGENTS_START_20261016.md`，机器分派`reassignment_20261016.json`。全部awaiting_new_agent_start，不冒称已启动/联系；原逻辑owner仅兼容目录归属，新作者/审核note记实际新会话。
- 新人各用系统给的固定分支先合A基线，不能切旧B–H分支，不能再更新已合PR35–38，只开新PR到A。领域只改自己路径，N7只审不代写，main仅N2；N3避免改共用来源让三份有效审核失效。A保留工具/schema/总表/状态。
- 此轮并行先修当前20篇及目录，不再等20篇齐备，也不扩5000模块/下载全量79MB语料。N7可先审G四篇，随新PR就绪独立核定原字节SHA；未合正文的review暂存template以免孤立记录。
- 合并态严格来源/full验证通过；82项=71通过+11 Qt缺libGL.so.1跳过/0失败；ruff含spec、Windows静态全0；完整20说明单HTML与jsdom脚本验证通过。无真实浏览器/Qt、Windows/EXE、游戏/原生/实服验收；生成站点/依赖留仓库外。
- 报告`docs/evidence/script_manual_integration_reassignment_20261016.md`；同名JSON收据含合并ID、激活SHA、分域/审核统计、任务卡指纹和本轮验证。原包/参数/分析基线未变，仅baseline注释说明现目录来源与待修边界。


## 3.49 全新N1–N7七PR已收到并按固定head复核（2026-10-16）

- 用户要求继续查看全新agent的成果。开工先push A（up-to-date），本轮只审核/评论/维护协调文档，**未merge PR39–45、未正式激活新review、未合master**。正式数据仍9b0dea7的5135/20/3/1，5退修review/12pending。
- 沙箱重建已实查：旧临时分析环境消失，本地HEAD回到8212b26但最新文件保留。比对215路径，212原blob相同、3bat只换行差异且Git过滤hash相同；仅恢复当前分支指针/索引到远端9b0dea7，工作字节未动，未重复提交/clean。新环境重新安装、复跑，不引用旧日志冒充本轮。
- 新PR固定输入：N1 #43 f953eb9；N2 #39 c714236；N3 #41 77b64be；N4 #40 44230b9；N5 #44 e2fb1aa；N6 #42 23b60f9；N7 #45 db872c5。七PR全部base A、变更在各卡范围，均已评论；机器表reassignment更新为已交PR，卡保留历史开工边界，不再表示尚待启动。
- N1真20种子→sample/full，A新跑一棵隔离树，三产物逐字节等于PR43；32项独立元数据回归全过（首次快照缺BDF收据跳1，补齐后重跑32无跳过）。5135身份/128382结构函数未丢；70kwargs、48内部槽、186非标识符及4fallback逐条留痕。A明确认可186保守null策略，不认可“全目录语义已验收”；这32不属于标准82，后续集成入口需单列。
- N3/N4/N6是有限集成候选：新N7九份模板绑定新JSON原字节SHA均匹配，三份UI旧已过字节不变。G原作者是A，接管作者N6，非作者审核是新N7，A不自批。
- N2五组修复重点复核有实质进展；A独立核stored/pyc/raw u6/严格cp950→候选4/4，17段main摘录975行完全匹配。新N7仅基线退修+新稿部分核对，尚未审完新head的逐Claim/方向/保真链，不能把基线退修或A结构通过当成已有H新字节accepted。
- N5确已补三篇重点说明（共267函数/63分支，war仍42名称底稿），但发现3项P2：①697/8的来源头entry_id错写（实际0x206d634b/0x005d26b3，四处要改并更新sources SHA）；②CPlayCtrl.Release先调用下游后置None，不能声称“可重入安全”；③Timer(0.033,...,-1,...)未引callee/单位语义却说约30fps/无限重复，须补证或降断言。已评论PR44，N5同PR修后报新head，N7再审，A不代写正文。
- N7是有效部分审核交付，不是全部验收完成：原基线16review中3有限过/13退修；九新模板可用，但login新稿未审完、battle未审。“N5无PR”是旧快照，当前44已交且需返修，已评论要求追加新状态、补N2和N5修后head的独立尾审。
- A白名单独立恢复17条，16source形状+1406仍partial（不是17完整源）；N6 980、N4 302、N3 59、N5三候选2208条摘录行和N2 main975行均匹配。本轮七快照/组合schema/来源/full全过，过期审核未屏蔽。
- **仅仓库外模拟**：叠七PR内容为3accepted/13stale/4pending，精确激活九具名N7模板后12accepted/4login stale/4battle pending；example模板不激活。此12不是正式A状态；新内容未获merge前不放正式孤立/提前生效审核。
- 模拟组合新跑82项=71过+11缺PySide6跳过/0失败；ruff含spec、Windows静态walk166路径/29源全0；HTML构建及jsdom实际脚本通过（4中文/函数搜索、3过滤、3路径identity导航、20篇×4页80次tab、hero→npc按钮跳转、N6/H身份）。非真实Qt/浏览器/CSP/Windows/EXE/游戏/原生/实服验收，无1288定点恢复或业务请求。
- A澄清CONTRACT：evidence行号指sources.path自身物理行，L/R候选原行是另一套编号，避免改已审字节。恢复工具False双repr传字符串问题已确认，N2真实False直接API绕过且raw链吻合；本轮仅登记，不静默改冻结工具SHA。
- 报告docs/evidence/script_manual_new_cohort_A_review_20261016.md；同名JSON含固定head/各PR评论、复现/检查/DOM指纹、N1回放及3项P2。下一步新N5修三项，新N7补尾审，A在授权/对应门槛满足后再集成并重跑，不改历史报告为当前结果。


## 3.50 N5二轮6fd5061复核：原三P2闭合，余一处指南范围（2026-10-16）

- 用户通知N5二轮已交，实查是原PR44快进更新到6fd5061dded82bbbcfc96694a5c20ef1a7a3e41e，父为e2fb1aa。A开工前de60052已推且干净，先push确认；仅仓库外审查，未merge/改正文/正式review/原包/工具。
- B-N5-01/02/03本轮均闭合：原包目录四ID及新回执/摘录/重新恢复结果一致，sources SHA和provenance行号同步；Release撤保证并明先调下游后清引用，Timer单位/重复/实际帧率未知同步到各处。267函数记录/67分支，42名称底稿仍明确。
- 新发现B-N5-04 / P2：war.json修改指南仍要求所有回调最终NextCmd或SetProcess(Wait)，虽写“推断”但把End等终止回调也涵盖。候选End去六头L1900–1974，录像L1909 CloseGame返回、普通L1927 SetMainLoop收尾，无NextCmd/SetProcess(Wait)，不是漏推进卡队列。只需限定继续消费队列的非终止回调，明确结束/关闭/切主循环例外，给新增Process/Wait断言补现有w_process/w_wait证据并标清推测；无须重做原三项或改候选。
- A本轮重恢复四条，3source形状+1406仍partial；2208摘录行逐行一致，四去头正文SHA匹配。PR快照与外置组合schema/来源/full通过；82=71过+11缺PySide6跳过/0失败，ruff含spec和Windows静态walk133路径/27源全0。未另跑HTML/jsdom或真实浏览器/Qt/Windows/EXE/游戏/原生/实服。
- 已评论PR44并同步PR45的新N7，原三项不再列未修。N5在同一PR小修指南后报新head，N7按新字节末审；N2尾审仍待。正式仍5135/20/3/1、5changes/12pending，外置组合12accepted/4login stale/4battle pending不是正式值。
- 报告docs/evidence/script_manual_N5_6fd5061_A_review_20261016.md及同名JSON含四ID/四新JSON SHA/反例范围/验证指纹；机器分派表N5固定head与最新待办已更新，首轮报告保留历史判断不改写。


## 3.51 A按授权接手收尾：七PR已合A，16份有限通过，四battle待非A独审（2026-10-16）

- 用户“你帮他们收尾吧”授权后，A先确认8638aad已推且干净，逐条`gh pr merge <明确PR号> --merge`成功并读回MERGED：43 f953eb9、39 c714236、41 77b64be、40 44230b9、42 23b60f9、44 6fd5061、45 db872c5，base均固定A；本地ff至e60fcb588ff7a50249504ff603f1a64af50f5c8b。未合master、未上传或改游戏/编辑器/启动器/原包/参数。
- 正式5135登记/20说明/**16有限accepted（12 H+4 A_delegate）/4pending/0stale/0changes/1排除**。九份N7模板逐个原字节SHA匹配激活；登录四份不改正文，由A在既有授权下有限代审五组阻塞、六题与原包→raw/正文链，不把N7旧基线退修换SHA冒充新审。gameplay用N6新稿/N7独审，不复活A自批。
- A接手war的B-N5-04并发现netwar同句重复，均限定非终止/仍消费队列回调，End关闭/切主循环为例外；netwar另撤回C2S/S2C字段必须对称的误导。e_warctrl指南纠正主动Release与自动移除不同、TriggerSignal是发出非订阅、ModuleReset只置None不保证timer/资源释放。warcmd把候选L12误称第12项改为字面映射第6项，元描述与sources SHA同步、L前缀候选原文不改。四篇均明示A共同作者、保持pending，**A不自批凑20**；原三P2仍closed，N5_RESPONSE追加真实A补记/新SHA。
- 修复恢复子进程False双repr问题，传真实布尔；先加AST合成回归在旧代码复现2失败，改一行后工具27项全过。四条N2重新经隔离子进程分别False/True，stored/pyc/raw/body SHA与严格cp950链4/4吻合；不执行/import恢复游戏模块。历史冻结工具SHA保留旧报告，新SHA钉本次报告，非静默替换分析基线。
- 新`python script_manual/check_manual.py`统一六闸门，`--require-gui`可禁跳Qt；不恢复原包/生成站点。标准86=原82+runner4，75通过11缺PySide6跳过0失败；N1独立32/32、恢复工具27/27另列。严格来源/full无警告、ruff含spec、Windows static walk168路径/31源全0；修改工具2路径/2源全0。工具既有临时路径测试改用跨平台TemporaryDirectory，安全路径用合成夹具。
- 新跑N1**两棵真实隔离树**，各冻结20种子→sample/full，四次成功；三产物跨树且与交付逐字节一致，128382结构函数记录未丢。1288定点读取四次均0，整包SHA仍会覆盖该字节范围，不说完全没读其字节。不是沿用上轮单树退化结果。
- 新合并态严格HTML构建与jsdom通过：16accepted/4pending、4中文/函数搜索、2过滤、3路径identity导航、80tab、hero→npc跳转、N2/A_delegate授权与四battle/A作者pending身份，0脚本错误。不是实浏览器/CSP/Qt/Windows/EXE/游戏/原生/实服验收；42名称底稿/5000未扩语义保留。
- 详细MD/JSON报告`docs/evidence/script_manual_A_finalize_20261016.{md,json}`含七合并ID、16绑定SHA、四篇待审新SHA、工具修复与测试摘要。README/CONTRACT/分派入口/机器表刷新为现状，旧卡与§3.49/3.50保留历史。不要求用户转交返修或重新开七人；四篇只欠非A对A修订新字节末审，尚无结果，不伪造独立通过。

- A收尾内容已推570a6a1与作者说明/字节收据对齐0b04cc1；独审请求已实际留言PR45#issuecomment-6206831156，N5收尾通知PR44#issuecomment-6206831398。仅表示请求已发布，未声称N7已开工或有新结果；45已合，若续审须新PR到A、只改reviews，四篇待审SHA见收尾报告。


## 3.52 Windows源码测试交付准备与Arena沙盒恢复规则（2026-10-16）

- 用户授权把独立脚本手册工具打包上传Google Drive供Windows实测，并要求把Arena Agent Mode沙盒状态丢失的预防/恢复写给后续agent。开工先push3dd4df6，up-to-date且工作区干净；不合master、不改游戏/编辑器/启动器，不上传原游戏包。
- 新增长期文档`docs/ARENA_SANDBOX_RECOVERY.md`，在AGENTS.md开工60秒入口醒目链接，并加`docs/templates/AGENT_CHECKPOINT.md`。记录本仓库已观测的临时环境失效、HEAD/index旧但新版工作字节保留，不推断平台根因或承诺本地持久。预防为阶段提交/推送/核远端OID与版本、持久的小回执和授权交付；恢复先保护差异，再fetch/逐路径核Git blob及CRLF，按真实缺失/元数据错位分别处理。高级update-ref/read-tree只在全部路径核准和备份后手工操作，禁止reset hard/clean、删.git或替换仓库根，不把dirty误判为前人没提交。
- 新增`script_manual/测试手册.bat`（ASCII/CRLF）：独立venv、依赖镜像回退、bootstrap预检、六闸门强制GUI、每次新日志、失败停住；`WINDOWS_TEST.md`列解压/启动/来源校验根目录/目视搜索导航/构建EXE/脱敏日志回报。不会自动上传日志或运行游戏。
- 新增`make_source_package.py`：只从干净已提交checkout的Git白名单与27个实际来源依赖收集源码/证据，不装游戏或整份语料；含N1共享解析器core、BDF小收据及六闸门所需合成测试/静态工具。拒绝越界/符号链接、缺证/错SHA、原游戏/编译器二进制、仓库内输出和覆盖旧ZIP；逐文件manifest钉提交及SHA，ZIP CRC/成员摘要自验。用户运行/自检/构建不需要Git。新增4项纯合成打包回归，标准90=79通过+11缺PySide6跳过；N1独立32/32、恢复工具27/27、严格来源/full、ruff含spec、Windows static walk172路径/34源全0。Windows/Qt实机仍待用户，不算通过。
- Drive已检查历史script_editor文件夹及其父目录；同级新建script_manual文件夹`1mxu6gDe2qLywlGR17NgtSuCShgQZom85`，没有更改分享权限。源码包需先提交推送，再构建并在无原包/.git的中文空格目录实际解压复跑；上传/远端校验成功后另追加真实回执，不提前宣称已上传。
- 内容仍5135登记/20说明/16有限accepted/4battle pending/1排除，无stale；四篇A共同作者未自批。此次不扩语义或替代非A末审。

- **实际交付完成补记**：源码已提交推送84e0b9c后构建ZIP，264项/3,140,276字节；263个载荷manifest SHA/大小及CRC全过。原ZIP解压到仓库外中文空格路径，在无.git/原包、清除继承PYTHONPATH/PYTHONHOME后六闸门全过（90=79pass+11缺Qt skip、N1独立32、恢复27），再strict HTML导出通过。不是隐式依赖原checkout才可用。
- 已上传Google Drive文件`14s0nmb61CfMDFMerb23JpJkQioZHc6J6`，新script_manual文件夹`1mxu6gDe2qLywlGR17NgtSuCShgQZom85`；单独get读回父目录、size3140276、MD5 94ab1107d8c4eacaee96111b5ab35d3a一致，未改分享权限。SHA256 261237f7212628b4574523466cd9805b329dfb2a57488d0226c97c0a5b8db0bc为本地ZIP值，不假称远端重算。交付MD/JSON：docs/evidence/script_manual_windows_source_test1_delivery_20261016.{md,json}。源码ZIP不是EXE，用户Windows/Qt/目视验收仍待；四battle独审仍pending。已授权上传取代此前各历史轮“不上传”的阶段边界，不是上传游戏包/改变权限授权。

## 3.53 手册按修改任务进入：dev4首批6篇/26步骤（2026-10-16）

- 用户明确拒绝目录+函数名作为完整手册，授权按原目标继续；开工先核4d423c8干净并push up-to-date。本轮实写6专题/26步骤/46引用，涉及6已有模块，默认GUI/HTML任务入口、步骤导航、检索、函数/证据深链、已核原文预览；新增schema/严格加载与正文变更失效保护、缓存SHA冲突防护，打包数据补guides。没有修改已审/待审annotation和review字节。
- 原模块5135登记/20说明/16accepted/4battle pending/1排除不变。六专题A编排且全部draft_unreviewed，引用模块通过不能转移。完整目标、五领域后续具体任务和实质验收写入script_manual/docs/CONTENT_PLAN.md，不把6专题或20篇当终点，不再要求用户重提需求/重派七人。
- 本轮最终六闸门：106=93pass+13Qt skip，N1独立32、恢复27通过；strict/full/evidence、ruff/spec、Windows静态184路径/38源、0错/警告。新增合成加载/失效/坏引用/转义/预览/缓存冲突/打包字节保全测试；两项新Qt交互仅写未执行。实际安装PySide6-Essentials6.10.3尝试offscreen，缺libGL.so.1，未使用桩库，不把跳过算通过。
- 真实Chromium153断网file://且CSP开，生产6篇/26步骤/检索空态、12函数证据定位与刷新、专题深链、来源预览、battle待审、hero→npc、390px宽度通过，0脚本/页/CSP错、仅本地文件请求；旧20种子隔离夹具14组浏览器断言也实际通过。不是Qt/Windows/EXE/游戏/专题独审。
- dev4版本同步源码/pyproject/源包root；本轮未重打ZIP或上传，Drive test1仍是dev3样板旧包。详细MD/JSON：docs/evidence/script_manual_task_guides_dev4_20261016.*；真实导出/浏览器产物在仓库外/home/user/manual-guides-20261016/final-site与final-browser。源码阶段推送，不以测试或新首页冒称全量内容交付。


## 3.54 目录寻址判定结案 + 版本/文档漂移修复（2026-10-16，会话分支 `arena/6256d39f-mxsj-tw-2022`）

- 用户「先做1、2」：① 给逆向笔记加更正横幅、把判定写进 `native_dlg_path_cipher.md`；② 修文档漂移（九宫格口径、`pyproject` 版本对齐 + 一致性测试）。开工核 `git status` 干净；本轮**未动任何客户端原包/参数表、未改编辑器运行逻辑**（只改 docstring/文档/打包元数据 + 新增只读测试），未合 master、未开 PR。
- **① 判定**（详见 §3.2 与 `notes/native_dlg_path_cipher.md` §2.1）：`.dlg` 的 LoadFile 链在 `0x60DD00` 调 `0x60E690`——标准 `std::lower_bound`（16 字节步长、比 entry_id），返回后 `0x60DD3D`/`0x60DD41` 判未命中 ⇒ **目录必须按 entry_id 升序**，插入后其后记录 `r3` 必须重算。`notes/fls_path_hash_and_dlg.md` §2 的「线性扫描」加了两处更正（文首横幅 + §2 内联），指明那句属 `0x48ECF0` = `ReadFls`；`0x48F170` 解目录公式仍有效（三个闭式常量在 `.text` 各出现 1 次，已逐条比对反汇编）。AGENTS §7 同一坑改写为已判定并指向新证据。
- **② 文档漂移**：`painters.py` docstring、`ui_editor/README.md`「格式与保真约定」、`ui_editor/DESIGN.md`、根 `README.md` §2 表、本文件上文、`notes/ui_editor_phase2_design.md` 六处统一为准确口径——**九宫格只有 `CPngNineFrame` 的固定三分近似**（边角不拉伸、切割线不可配、未与游戏切法比对），**M3.3 仍未完成**（切割线编辑 + 2.2 数据摸底未做）。
- **② 版本对齐**：`ui_editor/pyproject.toml` 0.8.2 → **0.8.3**、`resource_editor/pyproject.toml` 0.4.2 → **0.4.3**（两包 README/`__init__` 早已是前者，属打包元数据落后一版）。新增 `tests/test_packaging.py`（各 2 项，零 Qt、Py3.10 无 `tomllib` 时有正则回退）：钉 `pyproject` 版本 = 包内 `__version__` = README 口径。**先复现**：把版本改回 0.8.2 → 1 FAIL；改回 0.8.3 → OK。
- 本轮实测（沙箱 PySide6 6.12.0 + gcc 空符号桩库离屏，桩库不入库，做法见 §3.3）：UI 编辑器 **206 = 205 通过 + 1 语料库跳过**；资源编辑器 **120/120（零跳过）**；两者 `ruff check` 0、`check_windows_compat.py` 0/0/0、bootstrap `--check-only` exit 0。另复跑端到端写包（真实 `data/passive.fls` +1 布局）：`mode=added`、条目 41→42、目录升序、原条目全部可被 lower_bound 复刻定位。**无 Windows/EXE/真机/完整语料验收**；判定仍属离线证据，未经游戏回读验证。

## 3.55 共享核心 mx_common + 多实现同源回归 + 语料门槛与路径编码（2026-10-16，会话分支 `arena/6256d39f-mxsj-tw-2022`）

用户「开工」执行分析报告建议 ③（抽共享 core）、⑤（语料门槛）、⑧（统一路径编码）。**本轮只改编辑器源码与测试，未动客户端原包/参数表、未改协议与导出行为、未合 master、未开 PR。**

- **③ 共享核心**：新建仓库根 `mx_common/`（唯一真源）：`mxhash.py`（原逐指令复刻 + 新增严格 `path_hash()`）、`native_layout.py`、`output_paths.py`、`sprite_format.py`（**新**：魔数表/头与帧结构/行长上限/alpha 折算）。新建 `tools/devkit/vendor_core.py`：把这 4 个模块复制到两个编辑器 `core/` 下（副本 = 4 行生成横幅 + 真源全文，**按字节**比对，恒 LF），支持 `--check/--diff/--write/--list`；首次 `--write` 重写 8 份副本后 `--check` 0 报告。`tools/devkit/tests/test_vendor_core.py`（5 例）把「副本必须与真源一致」变成测试，并用临时目录**复现**「改一个字符 → check 报错 → write 修回」。
- **③ 多实现同源**：`sprite.py`（UI，无 Pillow，输出 RGBA）与 `core/codecs/sprite.py`（资源，Pillow 落点）仍是两种落点，但**格式常量与 alpha 折算收归共享模块**（编辑器内旧私有名保留为别名，`codecs/detect.py` 的 `SPRITE_MAGICS` 不变）；新增 `tools/devkit/tests/test_sprite_parity.py`（9 例）：真实精灵（`data/skill.fls` 里 **唯一一份** I0，3,627 B）两解码器逐帧 RGBA 一致、两边编码器输出互解一致且与源图一致、I1 宽行回退一致、手工构造 T4 真彩两解码器一致、alpha 折算对旧公式 0–255/0–31 逐点等值。**仓库内只有这一份真实精灵样本**，覆盖窄，如实记录。
- **⑤ 语料门槛**：`ui_editor/tests/test_codec.py` 去掉硬编码沙箱路径 `/home/user/interface_dlg_decoded`，拆成两层——**仓库内最小语料恒跑**（`tools/registration/` 7 个真实布局 + 本包夹具，缺文件即失败，不再因「外面没有语料」整组跳过）；**外部语料**只在 `MXSJ_DLG_CORPUS`（支持 `:` 多目录）给出时跑，**按实际数量上报**（低于 2,000 篇打印提示、不再一刀切 FAIL）。旧行为「指向 8 篇语料 → `8 not greater than 2000` 直接失败、连这 8 篇都不跑」已复现并修掉。
- **⑧ 路径编码**：全仓清除 `mx_hash(x.encode("gbk","replace"))`（13 处）。查询侧（`FlsPack.contains/read_named`、`known_layout_hashes`、资源编辑器 `known_path_hashes`/扒取命名）把「GBK 不可编码」当作**引擎也寻址不到**：返回未命中/跳过并留痕（`catalog.unencodable_layout_paths()`、`names.unencodable_known_paths()`，**尚未接进 GUI 诊断面板**，列为后续）；写入侧（`pack_build` 附加资源与变更清单、`main_window` 写后校验、资源编辑器 `index_by_path/add_entry_for_path/replace_for_path`）统一走严格 `path_hash()`，不可编码即在写之前抛错。新增 `ui_editor/tests/test_path_encoding.py`（8 例，含「不可编码附加资源 → `PackError` 且不留输出文件」端到端）与 `resource_editor/tests/test_path_encoding.py`（6 例）。
- **文档**：`AGENTS.md` §2 目录地图加 `mx_common/` 行；`docs/PYTHON_TOOL_CONVENTIONS.md` §1 新增第 7 条「多工具共用核心放 `mx_common/`，生成式副本分发」；两个编辑器 README/DESIGN 说明副本勿手改与语料新口径；`tools/devkit/README.md` 补 vendor_core 用法与用例数。
- **本轮实测**（沙箱 PySide6 6.12.0 + gcc 空符号桩库离屏）：UI 编辑器 **215 = 214 通过 + 1 语料库跳过**（上一轮 206）；资源编辑器 **126/126**（上一轮 120）；devkit **44**（上一轮 30）；架构 161、catalog 34、review_api 27、map_editor 88 全 OK；手册六闸门 OK（106=93 通过+13 Qt 跳过，N1 32，恢复 27）；`ruff` 0（mx_common/devkit/ui/resource/map）；`check_windows_compat.py`（mx_common+devkit+ui+resource）ERROR 0 / WARNING 0；两个编辑器 `bootstrap.py --check-only` 退出码 0；端到端写包复跑（真实 `data/passive.fls`，+1 布局）：`mode=added`、41→42、目录升序、原条目全部可被 lower_bound 复刻定位。
- **未验/未做**：Windows/EXE/真机、真实完整 `interface.fls`、游戏内加载与显示；`script_editor` 本轮**未纳入验证**（其 325 项里有 2 个 `xdis` 缺失错误 + 1 个 PySide6 版本钉 `6.10.3`≠沙箱 `6.12.0`，均为环境性、与本轮无关）；`tools/data-parser/extract_dlg.py` 与 `tools/data-parser/mx_path_hash.py` 仍各自独立（未并入 `mx_common/`）；`core/assets.py`、`core/painters.py` import Qt 与「core 零 Qt」约定的差异未处理（分析报告 P2-5）；`main_window.py` 拆分（建议④）未做。

## 3.56 拆 main_window 第一段：写回校验抽到 core/publish.py（2026-10-16，会话分支 `arena/6256d39f-mxsj-tw-2022`）

用户「④」执行分析报告建议④的第一段（报告原文：先给 `write_pack_copy` 抽 `core/publish.py`）。**只重构不扩功能**：写包行为、错误文案、报告字段与抽取前逐条一致；未动客户端原包/参数表，未合 master，未开 PR。

- **抽出内容**（`ui_editor/src/ui_editor/core/publish.py`，241 行，零 Qt）：
  - `engine_finds()` / `directory_is_sorted()`——模拟引擎二分寻址（`0x60E690` lower_bound + 相等判定）；
  - `verify_structure()`——条目数 = 原数 + 新增图片 +（新增布局?1:0）、目录无逆序、条目集合一致、布局与每张新图二分命中、除 `changed_ids` 外条目字节未被改（逐条 `read_id` 比对）；
  - `verify_readback()` / `verify_written_pack()`——回读钩子 :data:`ReadBack` 由调用方注入（GUI 注入全新 AssetResolver，测试注入只读 FlsPack + 原生密钥解码），所以本模块既不 import Qt 也不 import `core.assets`；
  - 保存前检查：`save_encoding_issues()` / `require_save_encoding()`（编码闸门）、`save_review_plan()` + `SavePlan`（图片行「新增/替换/未引用」、待入包提示、编码问题合并）——原先混在窗口方法里。
- **窗口侧**：`write_pack_copy` 只保留编排（取 extras、编码闸门、`patch_pack_copy`、报告元数据、状态迁移），校验改调 `publish.verify_written_pack`；`_confirm_save_review` 变成「算数据→弹窗」两段，数据来自 `save_review_plan`；新增 `_fresh_pack_readback` 静态方法作为注入钩子。`ui/main_window.py` 1,713 → 1,633 行（本段共减 80 行；报告④的其余部分——资源树/脚本面板/诊断——早已是独立模块，剩下的主要是菜单/信号/编辑命令的编排，未在本轮动）。
- **新增测试**：`ui_editor/tests/test_publish.py` **20 例、零 Qt**（此前这段逻辑只能被 GUI 测试间接覆盖）：二分寻址单元；结构检查**逐条反例**（条目数不符、目录乱序、条目集合被换、未列条目被改字节、`layout_added` 计入总数）；回读反例（布局内容不符 / 回读缺失 / 新图不一致 / 回读抛异常被记成报告而非抛出）；真实 `data/passive.fls` 端到端（写出新包 → 零 Qt 回读钩子 → `ok=True`、条目 +2、`changed_entries=0`）；保存前检查（编码闸门拒绝不可 GBK 编码的图片名与布局字段、图片行标签、待入包提示新增/替换、散装保存不嵌入）。
- **本轮实测**：UI 编辑器 **235 = 234 通过 + 1 外部语料跳过**（上一轮 215）；devkit 44；`ruff` 0；`check_windows_compat.py ui_editor` ERROR 0 / WARNING 0；端到端写包复跑（真实 `data/passive.fls`，+1 布局）：`mode=added`、41→42、目录升序、原条目全部可被 lower_bound 复刻定位。资源编辑器/其它组件本轮未改。
- **未做/未验**：报告④的其余拆分（资源树面板、脚本面板、诊断面板的进一步解耦；编辑命令与剪贴板逻辑）未动；Windows/EXE/真机与完整语料仍未验。

## 3.57 目标条目重写口径（建议⑦）+ 绘制对照清单（建议⑥）（2026-10-16，会话分支 `arena/6256d39f-mxsj-tw-2022`）

用户「开工」（你选的 ⑥+⑦；两份分析报告按你的选择随本轮提交入库）。**只加事实说明与核对材料，不改写包行为、不改绘制实现**；未动客户端原包/参数表，未合 master，未开 PR。

- **⑦ 目标条目会被怎么写（P2-1）**：`core/publish.py` 新增 `TargetWrite` / `classify_target_write()` / `classify_target_path()`：把「存储层」与「版式层」分开说清楚——`storage` = absent（新增）/ native / legacy（旧密钥）/ plaintext / unreadable（写回会拒绝替换）；`layout_rewritten` = 原明文与编辑器新明文不同（**用户没改任何属性也会真**，序列化会归一化字段顺序与写法）；`migrated` = 旧存储本次改为原生路径密钥；`byte_identical` 只在「原生存储且明文相同」时有意义（XOR 同密钥同明文 ⇒ 存储字节不变）。保存清单首行（`SavePlan.target_write` → `layout_notice`）与保存成功弹窗都带这句；`save_review.py` 的静态口径从「未改布局不动」改成准确版：**目标条目会按编辑器版式重写**，除目标条目、本次写入的图片与明确迁移的旧存储外，其它条目逐字节不动。README「格式与保真约定」同步补证据（8 个真实 `.dlg` 只有 1 个逐字节往返一致）。
- **⑦ 实测补充（本轮新事实）**：仓库内 7 个真实包（`script.fls`/`data.fls`/`effect.fls`/`skill.fls`/`skill2.fls`/`magicres5.fls`/`passive.fls`）里**一条 `.dlg` 条目都没有**（界面布局在未入库的 `interface.fls`），所以「目标条目分类」的真实验证只能用合成路径：先由编辑器写出原生条目，再对它分类。测试覆盖 absent / native 同明文（字节不变）/ native 异明文（版式重写）/ plaintext / legacy / unreadable 六种，另有真实包端到端：写出新包 → 分类 = absent → 对写出的条目再分类 = native+字节不变 → **无改动再保存一次，目标条目字节逐字节不变** → 改一个字段后明确报「版式重写」。
- **⑥ 绘制对照清单（P2-4）**：新增 `ui/paint_samples.py`（渲染 + 清单数据）与两个 CLI：`tools/render_paint_samples.py`（38 类样例 PNG + `contact_sheet.png` + `manifest.json`（尺寸/SHA256/绘制函数/是否命中真实资源）；支持 `--pack`/`--assets-dir`/`--image`/`--scale`）、`tools/paint_compare.py`（样例 vs 真机截图 → 并排图 + 差异图 + `*_report.json`：尺寸是否一致、差异像素数与比例、差异包围盒、平均绝对差；**只给统计不给结论**）。新增 `docs/PAINT_CHECKLIST.md`：38 行 × 类型/绘制函数/编辑器画什么/依赖/游戏侧期望/真机截图/差异/结论，**游戏侧各列一律留空**等真机核对。
- **⑥ 目视核对到的差异（本轮）**：`defaults_data.DEFAULT_PROPS` 38 类 vs `painters._PAINTERS` 37 类 → **`CDataWidget` 没有专用绘制**，走兜底占位框（清单里可见，样例第 10 张就是这个占位框）；20 类模板带图片字段（`CProgress` 用 `sBgFileName`/`sBarFileName`），`--image` 指向真实资源时有且仅有这 20 类渲染不同（机器验证）。
- **⑥ 机检（`tests/test_paint_samples.py`，12 例）**：38 类全渲染非空且尺寸 = `effective_size`；联络表覆盖全部样例；`manifest.json` 的 SHA256 与实际文件一致；**清单类型集合 == 模板类型集合**、清单绘制函数 == 分发表（以后新增控件类型漏进清单会红）；**「游戏侧各列必须留空」这条规矩被机检**；清单重新生成与仓库那份逐字一致；真实精灵（`data/skill.fls` 唯一一份 I0）作为资源时命中且只影响图片类。
- **本轮实测**（桩库离屏）：UI 编辑器 **257 = 256 通过 + 1 外部语料跳过**；devkit 44；`ruff` 0；`check_windows_compat ui_editor` 0/0/0；样例渲染冒烟：占位版 38 类 + 联络表 40 文件、真实资源版（散装目录放真实 I0 精灵）20 类渲染改变；`paint_compare.py` 用「样例 + 人为色块」造的真机截图跑通（差异 60 像素 / 3.12% / 包围盒 (2,2,12,8)）；端到端写包复跑 `mode=added`、41→42、升序、原条目全可定位。
- **未做/未验**：任何「与游戏一致」的结论（必须真机截图人工填表）；`CDataWidget` 虽缺专用绘制但**未改**（属功能决策，先记录）；`interface.fls` 未入库 ⇒ 仓库内无法渲染真实界面图；Windows/EXE/真机仍全部未验。


## 3.58 主窗口继续拆分：控件编辑命令（2026-10-17）

用户授权「那你先拆」。行为保持型重构，不新增功能、不修改原包。

- `ui/main_window.py` 的 23 个编辑方法搬到 `ui/commands.py` 的
  `EditingCommandsMixin`：添加/提升、选择集合、文本焦点分流、复制粘贴、
  删除与静态引用护栏、锁定/撤销后恢复、右键菜单、控件重排。
  窗口继承 mixin，保留所有原有方法名和信号连接；mixin 不初始化 QObject，
  不保存文件。结构刷新与选择回调仍在主窗口。
- 主窗口 1,638 → 1,296 行；新模块 367 行。④仍未全部完成，主窗口仍超过
  600 行约定；后续可按文件/资源工作流、动作/菜单组装继续拆分。
- 实测：AST 对比搬出的 23 个方法与本轮修改前实现全部一致；UI 全套
  257 项（256 通过、1 外部语料跳过），覆盖复制粘贴/删除/锁定与撤销；
  devkit 44 通过；ruff 0；wincompat ERROR/WARNING/INFO 均 0；
  `bootstrap.py --check-only` 退出 0（沙箱 Qt 环境）。
- 验收边界更正：用户已明确反馈，之前在 Windows 添加控件后游戏里能显示，
  此项记为用户实测通过，不再描述为完全未验证。本轮重构仅有上述沙箱回归，
  不将之前的功能验收外推成本轮 Windows/EXE 验收，也不要求重复整套验收。


## 3.59 主窗口职责拆分收口至 600 行以内（2026-10-17）

用户授权「继续」。继 §3.58 的编辑命令拆分，本轮仅迁移界面层方法与依赖，
不改写包行为、不改功能、不碰客户端原包。

- 新增 `ui/workflows.py`（545 行）：27 个方法，包含散装布局/目录/包的
  打开与导入、保存清单、生成新包、导出 PNG、资源样式加载。
- 新增 `ui/window_setup.py`（303 行）：5 个方法，包含面板、菜单、工具栏、
  动作工厂与信号连接。静态方法装饰器一并保留。
- `MainWindow` 组合三个职责 mixin，继续持有窗口/文档状态、选择与历史回调、
  诊断/脚本关联和几何编辑编排。主窗口 1,296 → **491 行**；连同前一轮
  `commands.py`（367 行），这四个窗口模块均不超过 600 行。
  mixin 不定义初始化方法，不接管 QObject 生命周期。
- GUI 测试的 mock 查找位置跟随依赖迁移：保存/导入对话框与文件选择框改在
  `ui.workflows` 打桩；主包缺失路径测试同样在新模块替换目录函数。
  不保留仅供旧测试使用的无效导入，不降低测试断言。
- 新增 `tests/test_window_structure.py` 3 项纯 AST 护栏：四个模块行数上限、
  方法不跨组重复遮蔽、mixin 无 QObject 初始化且窗口继承顺序明确。
- 实测：本轮搬出的 32 个方法 AST 与修改前完全一致；UI **260 项**
  （259 通过、1 外部语料跳过）；devkit 44 通过；ruff 0；wincompat
  ERROR/WARNING/INFO 均 0；`bootstrap.py --check-only` 退出 0。
  以上为 Linux 沙箱离屏结果，不冒充本轮 Windows/EXE 验收。
- 当前主窗口拆分的行数目标已达到；不扩展为整个编辑器全部模块均符合
  行数约定（既存 `pack_build.py`、`painters.py` 的超长问题不在本轮改动内）。
  用户此前 Windows 添加控件并在游戏中显示的验收结论继续保留。

## 3.60 UI 编辑器 0.8.4：文本编码、来源刷新、布局导出（2026-10-17）

用户明确授权实现这三项；不改变编辑器界面语言、不做简繁转换，不改原包。

- 工具栏增加 Big5（默认）/GBK/UTF-8 文本编码下拉；切换从当前布局原始
  解密字节重新解析，立即更新画布，不拿乱码文字反向转码、不自动保存。
  `sText/sTitle/sTitles/sTips` 支持选定编码（包括嵌套容器），资源路径保持
  GBK，路径哈希和 FLS 加解密规则不变。文档记录编码与原始字节；保存成功
  更新字节快照，避免切换时恢复成保存前的内容。
- 保存/存包、导入预检、编码诊断和全新 resolver 回读使用文档编码。
  保留既有原生 GBK 文件头（按字段混合编码）；UTF-8 可读写不等于目标游戏
  已支持 UTF-8 字体渲染。不是“全部官服版本已兼容”的结论。
- 工具栏刷新（F5）：新建 resolver 重开包索引、重扫来源目录（含新增包）、
  重读当前布局、图片与 ui.lst；成功才替换窗口状态并关闭旧包。保留包顺序、
  已记路径和待入包图片；取消/读取失败保留当前文档。目录树反映散装布局
  新增/删除并恢复当前定位。未保存新建布局无来源，刷新不凭空丢掉它。
- 左侧已有布局右键导出：锁定所点包/文件，散装原字节复制，包内先解密后
  原字节输出 .dlg，不重排、不改 MD5、不转码；不含当前未保存编辑。
  灰色缺失节点禁用导出；待入包节点仍用另存为。保护源包、散装源资源及
  软/硬链接别名，不能通过导出覆盖源文件。
- 新增 `ui/source_actions.py` 组织这三项；主窗口仍少于 600 行，结构护栏
  加入新 mixin，不删除旧有的行数/重复方法/QObject 初始化检查。
- 新增 28 项测试（编码 6、来源 GUI 22），涵盖三编码嵌套往返、GBK 原文、
  UTF-8 BOM、切换/取消/失败、保存后切换、待入包标记、GBK/UTF-8 写包回读、
  图片/未命中缓存/样式刷新、包索引更新、新包发现、刷新失败回滚、同名包
  精确导出、导出未保存编辑隔离、源文件/图片硬链接保护与菜单信号。
- 本轮实际验证：UI **288 项（287 通过，1 外部语料跳过）**；devkit **44 通过**；ruff 0；
  Windows 兼容静态扫描 ERROR/WARNING/INFO 均 0；vendor_core --check 通过；
  bootstrap --check-only 成功。环境为 Python 3.11 + PySide6 的 Linux
  offscreen，系统缺少图形库，用仓库外空符号桩库支持离屏测试，不入交付。
  本轮没有新的 Windows/EXE/官服实包验收，没有生成或上传新版 ZIP。
  用户既有 Windows 添加控件并在游戏中显示的验收继续保留。
- `data/script.fls` 与密钥库 SHA256 均保持锁定值，资源编辑器本轮未改。

## 3.61 左侧过滤 0 布局 FLS（2026-10-17）

用户要求左侧隐藏 0 布局的包。统一在 `_add_pack_to_tree` 过滤无已识别布局的
FLS，单包打开、资源目录打开、刷新均生效；resolver 仍挂载它们，图片/其它资源
读取不受影响。不将“未识别到布局”说成包物理内容必然没有布局。
更新零布局提示和目录状态统计，移除“空包可在左侧右键导入”的过时提示。
程序化导入仍可展示待入包节点；丢弃后清除没有其它布局的空包根，不留 0 布局节点。
调整既有回归，覆盖单包/目录过滤、隐藏包保持挂载、刷新后仍过滤、待入包清理、
未命中路径不挂空根。UI 288 项（287 通过、1 外部语料跳过），ruff、diff 检查通过；
Windows 静态检查 ERROR/WARNING/INFO 均 0。本轮没有新增 Windows/EXE 实机验收。

## 3.62 两编辑器独立源码 ZIP 上传云盘（2026-10-17）

用户明确授权分别打包上传 Google Drive。源码快照 `840799ccb7c890bd0571efc402bbf0c0b0a2f9ed`，
只打包各工具的受版本控制文件；不含游戏 FLS、密钥、venv、空符号桩库、缓存或编译 EXE。
ZIP 顶层有交付说明，进入 `ui_editor` / `resource_editor` 子目录启动；各自包含
中文启动 BAT、bootstrap、build_exe.bat 和 spec。UI 包额外含原有 7 份注册布局
最小测试样本，保持测试的仓库相对路径，不降低缺语料断言；仅作测试，不是部署补丁。

独立解压复测：UI 287 项（280 通过、7 缺外部资源/语料跳过），资源 126 项
（119 通过、7 缺真实客户端资源跳过）；两包 bootstrap --check-only 通过。
Linux Qt offscreen + 仓库外桩库，不冒充 Windows EXE/官服实包验收。
打包前 ruff、Windows 兼容静态检查和共享核心副本检查均通过。

上传到 My Drive 根目录，保留旧包、未更改共享权限。上传后另行 get_file 核对
文件名、大小、MD5 与本地 ZIP 一致：

| 包 | 字节数 | MD5 | Drive 链接 |
|---|---:|---|---|
| ui_editor_0.8.4_source_20261017.zip | 456498 | d9bc58757812db183c1ebb606842faf8 | https://drive.google.com/file/d/1ppId3BylFSIpDE8ccTKiDJY29_IFlTeO/view |
| resource_editor_0.4.3_source_20261017.zip | 176389 | 2a30149401d6d42b5f8c2f44e7d75ebd | https://drive.google.com/file/d/1r6ZxYDegD2O9hVY60Yg2QqT1PRBayL3O/view |

UI ZIP SHA256：`15c7c0ed785fb34a1b2536bc9f630a15a3eb0e9620f0a88504fc607f60933c87`；
资源 ZIP SHA256：`4d988aeff1d0d02ab2137a970dc33c3f8195d714e9041260f4e38f724268d6aa`。


### 3.63 内置打开列表：原生导入链静态定位（2026-10-17）

本轮按用户“你查”继续，不要求重复搜索、找日志或盲放文件。
已确定编辑器先显示窗口、再强制读 file_interface.FILE_INFO、再扫描本地interface；
前置依赖失败能留下空窗口。仓库原包目录缺少正确键 file_interface.s（0x3caabef5）。
原生 C_sys.PkgImport VA 0x45D1D0 存在普通 Python 导入回退，不是仅支持包内模块。
查明正确脚本资源键为模块名加 .s，4,951个候选匹配，纠正notes §3/§6旧判断（见新§7）。
报告：docs/analysis/native_open_list_failure_20261017.md；证据同级evidence目录。
边界：未取得真实客户端 sys.path，不能指定散装.py准确放置位置；未实机复现异常；
不把 .py 重命名 .s，未运行恢复模块，未修改script.fls或密钥。下一步为核启动路径设置，
或在授权范围内设计独立可回滚修复，不能宣称已修好。
本轮HEAD观测为5ef8aa2，工作文件含前轮大量已交付内容；未重置或批量暂存这些内容，
未基于旧HEAD盲目补交/推送，保留工作树待按恢复规程核对远端。


### 3.64 用户要求完整源码放 Diff：已生成单模块替换候选（2026-10-17）

路径 `tools/client_patches/native_uieditor_open_list/dgtuieditor.py`，643行，
只改变 entry 918 的 CUIEditorDgt.GetFileInfo；同目录有小范围diff、README及audit.json。
本轮从锁定原包单条恢复（uncompyle6 3.9.3），保留原始字节字符串为ASCII转义，
移除反编译器b前缀/非法模块return，并还原4个文档字符串。
仓库外构建CPython2.5.6并仅compile，不执行模块；60个代码对象与原code递归比对，
除GetFileInfo外59个的指令、参数、名字、局部变量、标志、堆栈、自由变量、闭包、
字面量常量均一致（排除源位置元数据）。源码SHA256见audit.json。
原包/密钥未修改，没有分发FLS；用户自行用脚本编辑器备份、替换、编译，原生验收待做。
已有自定义修改的模块不可整份覆盖。该目录为Diff交付，不将恢复语料冒充原作者源码。
HEAD/索引旧版问题沿用3.63：保留现有工作树，未盲目批量提交推送。

### 3.65 完整 dgtuieditor 修复源码云盘交付（2026-10-17）

按用户要求打包并上传 `dgtuieditor_open_list_fix_20261017.zip`，7191字节，
内含完整643行dgtuieditor.py、README.md、GetFileInfo.diff、audit.json。
打包前源文件SHA256与审计一致，ZIP CRC及解压源码逐字节核对通过。
上传后独立get_file复核大小、MD5一致：`fe980a7bc93716eafc17ae9027099e8e`。
ZIP SHA256：`0bdd83cc82638605f4ebc5d6d210f1fddba7c84150d663e022ac1d507fb61822`。
Drive：https://drive.google.com/file/d/1kCUs9Q_AbGekYUZJ9Z-Mqv2q5tJ7YelI/view
My Drive根目录，未改共享权限、未覆盖旧文件；仅源码候选，不含游戏包/密钥。

### 3.66 修正源码交付遗漏：固定XOR长度超限（2026-10-17）

用户反馈 authored marshal exceeds fixed XOR length; no shrink/rescale。
原因：3.64/3.65仅做compile和原code比对，漏掉native_build.py固定expanded_size限制。
不放宽边界，不缩放参数。新版完整源码628行，GetFileInfo只返回本地GetTmpFileInfo，
**功能收窄：不合并包内开发清单；interface不存在/扫描错误仍沿用原生空数据行为。**
实际经编辑器compile_standard→build_package→独立readback及标准marshal审计通过：
22398字节 <= 22441，补零43；只改918，其余5001条存储内容核验不变。
仓库外compact_verified_test.fls仅验证未分发；原包/密钥未改；没有执行恢复模块。
同目录源码/diff/README/audit已更新；59个非目标代码对象仍与原code一致。
v2 ZIP6457字节，MD5 337160fda83677cc654271925565dda8，上传后get_file匹配：
https://drive.google.com/file/d/11DX11YNL_2BaTBRVovHV6LTHXOTKMZiC/view
旧版不再建议使用；保留旧云盘文件、不改共享权限；Windows/游戏端待验证。


### 3.67 用户反馈内置编辑器无法打开：暂停部署（2026-10-17）

用户截图：mx.exe，Version=(0,8,147)，Code=0xC0000005，Address=0x004EE054。
建议立即退出游戏并恢复本次修改前备份script.fls；v1/v2均不再建议部署。
README、audit追加暂停标记，不删除源码、不擅自改用户云盘文件。
本地mxmain.dll同地址指令为 mov esi,[esi+0x30]，位于代码模块装入函数，
调用链前段从代码对象取得filename；原生import路径调用此前定位的0x4EDFE0。
只能说明本地二进制映射下加载路径可能访问无效code对象；截图无寄存器/调用栈，
不能据此断言哪个模块解密失败，也不能确认用户二进制与仓库完全一致。
本轮追加核查：锁定原包918 decode→encode逐字节等于原解密marshal（22441字节）；
此自洽结果与前轮离线写包回读均不能替代原生引擎验收，暂不再发猜测补丁。
下一步需要用户实际生成的出错script.fls（仓库外只读接收）核对实际修改条目、
头部/目录、负载、固定段参数和原生加载链；不要求用户重复搜索或自行找日志。

### 3.68 已核用户1017script.zip并交付精确回退（2026-10-17）

Drive下载文件1hEAYFKKA5lIeot2Www0tR6J0VVAUYWuB，MD5已核；用户FLS SHA为
0ee42496e9c69abc4bbcad3aa35ebb232866acfaaa1555dcbacc9575f25aad20。
918解压加密载荷与我方v2测试构建逐字节相同，非用户贴错代码。
仅恢复918后整个包SHA精确回到此前c7276deb…已登记用户包（48449597字节），
保留其余5001条和此前337/4007/4082修改。回退ZIP已CRC/整包SHA核验、上传、独立get_file复核：
https://drive.google.com/file/d/1G14eDPJMbGMtPYPnN8cs0MJ2iJ5t4gxq/view
文件48294282字节，MD5 5791e84f8b92b6982e4e1c7623f74545，未改共享权限。
所有FLS/ZIP/pyc仍仓库外/home/user/crash_1017，下载时落库内google_drive的ZIP已移出。
报告docs/analysis/native_open_crash_20261017.md，证据同级evidence。
仍未确诊原生加载崩溃根因，不把离线同源回读当引擎兼容；不再发猜测性修复候选。
原始输入和密钥未改，未执行恢复模块，无Windows/游戏验收。HEAD旧版与工作树差异仍待恢复核对，
未批量暂存/覆盖已有工作，未盲推。

### 3.69 用户回退成功；授权直接构建字节码对照测试包（2026-10-17）

用户明确“替换回去就能打开了”，回退恢复内置编辑器启动已实机确认，空列表未验收。
随后用户要求“你直接改好一个我试试，是不是脚本编辑器的问题”，本轮按此授权构建新候选。
外部临时文件恢复后缺失，已从Drive取回先前回退ZIP并核MD5及解压c727整包SHA。
不重新编译/序列化模块、不调用FLS writer：在原生GetFileInfo的49字节窗口改成
LOAD_FAST self / LOAD_ATTR GetTmpFileInfo / CALL_FUNCTION 0 / RETURN_VALUE，余39字节NOP。
实际仅29字节变动；marshal总长22441不变，所有元数据/原始常量/行号表序列化布局不变；
其余59个代码对象不变。新zlib流8436字节＋10字节零尾占满旧8446槽，解压逐字节回读一致。
整个包长度48449597、头/目录/偏移/长度均不变；目标槽之外所有文件字节完全一致，5001条不变。
输出FLS SHA256 4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678。
16项native codec单测本轮通过，未执行恢复模块、无游戏实机结果；这是用户授权的对照候选，
不是宣称已确诊或已修好脚本编辑器。若正常可缩小到重编译/序列化/写包链，不能单独定位某算法。
源码/旧v1/v2仍暂停；本次只列本地interface文件，不合并包内开发清单。
ZIP script_uieditor_direct_bytecode_test_20261017.zip 48295807字节，MD5
1d5b430cf97b2e3b59eb211278b7f626；上传后独立get_file核对一致：
https://drive.google.com/file/d/1q3OCueg5pt1gSNTfG2pOJOcNAXf0UI1U/view
未改云盘权限。输入/输出FLS、ZIP、构建探针均在/home/user/uieditor_direct_test_20261017。
repo仅小审计docs/analysis/evidence/native_open_crash_20261017/direct_bytecode_test_audit.json，
未存原包/密钥/完整游戏包。HEAD旧版保留现有工作树，未盲目批量提交推送。


### 3.70 用户实机确认原位补丁：有列表、加载成功（2026-10-17）

用户原话“你的可以，有列表了，加载成功”。对应3.69直接字节码包
1q3OCueg5pt1gSNTfG2pOJOcNAXf0UI1U，FLS SHA256
4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678。
内置编辑器可打开、显示本地列表、布局加载成功得到用户实测支持。
同等本地扫描逻辑的全模块重编译版崩溃，而保留原marshal布局/函数长度/包结构的
原位版成功，将排查主线收窄到重编译/序列化/写包转换链，而非再改用户文件目录。
尚未单独定位具体错误算法；不把它写成所有脚本编辑器功能或任意扩容写包已通过。
保留本地文件限定：本版不合并包内开发清单。旧v1/v2源码仍暂停使用，不建议
将当前可用测试包通过编辑器再次编译覆盖；独立审计已追加用户验收范围。
下一步独立对比失败重编译版与成功原位版，按复现补测试再改编辑器，
不得只放宽固定长度保护或以同源codec回读代替原生兼容性验证。


### 3.71 脚本编辑器dev7原生cipher修复并交付覆盖更新（2026-10-17）

用户在确认原位包“有列表了，加载成功”后要求修编辑器。本轮已完成代码修复，
不是继续让用户排查目录，也不再仅靠原位改字节绕过完整重编译。

- 真因：旧catalog研究边界并非客户端真值。918正确4511/9012/13542/18070，
  旧表第一/第四边界各提前3字节。旧读写共用错误参数，同源往返误报成功。
  错位分别损伤嵌入路径和`m_dOrgWidgetInfo`，后者被旧v2恢复成`JxCOrgWidgetInfo`。
- 实现native seed/递推边界，统一接入load_profile、路径索引、语料参数核验与写包。
  539行不完整/非唯一键通过name-seed及目录hash双核对；两对五键碰撞不任选。
  共享mxhash新增script_editor分发目标；原包/catalog及SHA未改。
- 已验收原位包4bf116...自动关联。仅该完整SHA的entry918去掉确定的10零槽尾后
  严格解压，其他未知尾部/拼接流/截断规则不放宽。实际从此包完成预编译/发布，
  新输出ceeb3ddf...、48449552字节，仅918替换，其余5001不变。
- 原包5002项全部严格解码及独立模块名侧客户端算法解密对照通过；真实2.5.6
  编译628行v3验证源码，60个code中仅GetFileInfo语义不同，59个保持。
  v3完整源码+diff另存native_uieditor_open_list_v3，旧v1/v2仍暂停，不自动改用户旧稿。
- 本轮335测试：247通过、88明确跳过、0失败。GUI缺libGL、2.7未配置及外部语料
  跳过不算通过；未宣称完整发行门禁通过。ruff/Windows兼容0错误0警告/vendor校验通过。
- 云盘读取旧dev6完整ZIP失败，未重复相同请求。交付dev6覆盖式源码更新，保留已有
  Windows编译器/引擎；不是完整重装包或EXE。旧EXE不会自动更新，应从原bat启动。
  实际ZIP覆盖到HEAD旧源码后，隔离安装副本38项通过、零跳过，已验证所需新模块齐全。

[下载dev7源码更新](https://drive.google.com/file/d/1_Ae-5qkZeWtCtGa_94mkIT5PV7KJxPVf/view)
文件MXSJ_ScriptEditor_0.6.0.dev7_update_20261017.zip，88157字节，
MD5 `2ca0feb66321a9a2e12547ea6f48bd7f`；上传后get_file重读匹配，位于既定
script_editor目录，未修改分享权限/旧包。完整修改文件、diff、说明、核验摘要及
未游戏验收v3参考源码随包；不含FLS/EXE/DLL，不要求替换当前已能运行的游戏包。

报告：[native cipher修复](analysis/native_cipher_fix_20261017.md)；
[测试/输入核验](analysis/evidence/native_cipher_fix_20261017/verification.json)、
[交付回执](analysis/evidence/native_cipher_fix_20261017/delivery_receipt.json)、
[从用户已验收包完整重编译审计](analysis/evidence/native_cipher_fix_20261017/accepted_workflow_audit.json)。

**当前状态：编辑器核心修复、覆盖更新交付完成；修正版完整重编译输出仍未Windows/游戏验收。**
用户验收过的仍是此前原位包，不能把那次成功写成本轮新包已通过。下一步接受dev7反馈；
不要求重复证明旧原位包，不再发旧v1/v2，不替换用户个人修改或可用包。

## 3.72 `mock_server.py` 修復「網絡錯誤(007)」、日曆/日程時間偏移與系統設置分辨率保存卡死（2026-10-17）

- **「網絡錯誤(007)」根因與修復**：反組譯 `mxmain.dll`（`C_sys.GetTime` @ `0x4545b0`）確認其返回值為 `(timeGetTime() - start_ms) * 10`（單位 **0.1ms = 10,000 ticks/sec**），`mxgw.SecondGetResult`（entry `2296`）中 `cdt = (G2 - G1) / 100` 為**厘秒（100 ticks/sec）**，看門狗週期 `CreatePyCommand(750 / 1200 / 5400)` 為 **25s / 40s / 180s**（30 FPS 幀數）。舊版 `GS2C_TIME = 31` 下發 Unix 秒（1 tick/sec）導致 40s 週期內 `cdt ≈ 4000 > sdt ≈ 590` 必敗並斷線報 `007`。現改為單調遞增 100Hz 厘秒計數器（`monotonic_centiseconds()`，僅在收到 `C2GS_REQUEST_TIME = 61` 時回覆）。
- **日曆与日程表時間偏移根因與修復**：`script/misc.py`（entry `3183`）啟動時 `g_RecordTime = 0`，若伺服器未下發觸發 `misc.SetServerTime(tm)` 的封包，`GetServerCurrentTime()` 會將 Windows 開機運行秒數（`C_sys.GetTickCount() / 1000`）疊加到 `time.time()` 上；且 `dlgcalendar.S2CTime`（entry `1425`）監聽 `GS2C_TIME_SECOND = 192`。現於進圖、瞬連及收到 `C2GS_OPEN_UI = 88 (isub=241)` / `C2GS_SCHEDULE = 82` 時同步下發 `GS2C_OPEN_UI = 89 (isub=241)`、`GS2C_PROP_SWITCH = 21 (isub=6)` 與 `GS2C_TIME_SECOND = 192`，並完整回應 `C2GS_SCHEDULE = 82 (isub=1, 2)`。
- **系統設置/分辨率保存卡死根因與修復**：`dgtbaseopt.Save()`（entry `2373`）在跨 `ratio` 切換分辨率（`視野擴大` $\leftrightarrow$ `800*600`/`1024*768`/`1280*960`）或切換界面風格時會觸發 `netquicklogin.Connect` $\rightarrow$ `main.RestartQuickLogin` $\rightarrow$ `Restart(2, False)`（清空熱鍵、場景與 UI 並建立新連線發送 `C2GS_QUICKLOGIN = 13, sub=2`）。舊版未下發 `GS2C_QUICKLOGIN = 12 (isub=1)` 導致 `g_LoginKey = None` 拋出 `TypeError` 且未處理 `opcode 13 / 21 / 90`。現於登入時下發 `GS2C_OTHER_ASSISTANT = 11 (isub=42)`（`S2CSetRate`）、`GS2C_PROP_SWITCH = 21 (isub=1)` 與 `GS2C_QUICKLOGIN = 12 (isub=1)`，並完整實作 `C2GS_PLAYER_SYSSWITCH = 21`（含 `C2GS_GAME_PUBLIC = 209, sub=5` 分片重組）、`C2GS_HUODONG = 90 ('newchar' sub=11)` 與 `C2GS_QUICKLOGIN = 13 (sub=1, 2)` 瞬連重登。
- `mock_server.py` 與 `mock_server (1).py` 均已同步並通過 `--self-test` 全鏈路 6 階段回環測試。


### 3.73 PR #51 同步master并解决状态记录冲突（2026-10-18）

- 用户报告PR合并冲突；实际仅`docs/STATUS.md`末尾双方追加内容冲突，运行代码无冲突。
- 保留本分支§3.54–3.71全部记录，以及master的Mock时钟/日历/瞬连修复记录；
  后者改编号§3.72，对应概览链接同步更新，不覆盖任何一方进度。
- master的`mock_server.py`、`mock_server (1).py`及quest.story设计文档逐字节保留；
  script/UI/资源编辑器和共享核心相对dev7提交不变。
- 本轮重新执行：Mock `--self-test`六阶段回环通过，脚本编辑器38项核心回归通过
  （零跳过），vendor_core 4模块/9副本一致；无未解决冲突，新增合并差异格式检查通过。
  没有重新执行335项全量回归，也没有新增Windows/游戏验收。
- 本轮只将master同步进固定工作分支并推送PR #51，不执行PR合入master。
- 小审计：`docs/analysis/evidence/pr51_conflict_resolution_20261018.json`。


### 3.74 文档事实纠偏与验收路线整理（2026-10-18）

- 固定会话分支 `arena/a101be51-mxsj-tw-2022`，代码基线 `cb2409a`；用户授权本轮文档整理。
- 当前概览统一为资源 0.4.3、UI 0.8.4、脚本编辑器 dev7、手册 dev4；正式服务端、只读复核链与 Mock 分开描述。
- 旧 STATUS 顶部与 README 作废注册安装章节归档；原编号历史章节保留并加适用范围提示，不删除证据或更写旧审计结果。
- 新增 ROADMAP 与 Mock 副作用说明。CI、依赖升级、认证／事务和新游戏逻辑仍是规划，未实现；没有改变任何协议号、帧长度或客户端写入行为。
- 本轮重新运行的命令、环境、退出码与结果见 [检查 JSON](analysis/evidence/documentation_refresh_20261018.json)，当前汇总在 §2；Mock 回环沿用同会话上一轮分析，不伪称本轮复跑。
- 不改源码、原包、key DB 或交付 ZIP；只提交文档和小型检查记录到当前分支，不合并／发布／上传。原始输入摘要保持一致。


### 3.75 tools 第一阶段：状态导航与依赖清单（2026-10-18）

- 用户授权第一阶段：总索引、子目录说明、替代入口与依赖盘点；不移动／删除文件，不改算法，不重建语料、索引或补丁。
- 会话恢复时本地 HEAD 为 cb2409a、工作文件保留上一轮成果；核对远端 886915c2611e661d7c51b057a7a5a8b6cc4038c0 的 26 路径逐字节相同并备份后，仅对齐当前分支指针／索引，未覆盖文件或重复提交。
- 新增 [tools 导航](../tools/README.md)、[依赖清单](../tools/DEPENDENCIES.md) 及四个子目录 README；更新 script_link、dis_v43、client_patches 和根入口。
- 修正 client_patches 整体判废的概括：注册 overlay 停用；内置 UI 旧源码暂停；v3 完整源码仅离线参考，尚未原生验收。
- 已核实原生注册构建动态依赖旧 batch／pack／decoder；batch 的 data 包分支调用 universal_fls_tool；UI 索引、来源核验、手册打包、旧 SQLite 与源码摘要各有保留理由。
- 本轮架构测试 **161/161** 通过；未运行旧工具批量恢复／重包、GUI、真实客户端或前端。依赖清单是代表性静态核对，不是完整动态调用图；历史 work、外部脚本等尚未穷尽。
- 文件范围、相对链接和锁定输入检查见 [本轮检查](analysis/evidence/tools_lifecycle_20261018.json)。全部 2342 个原有非 Markdown 跟踪文件按 Git 属性归一化后的 blob 与基线一致；第二阶段迁移／第三阶段清理均未实施。


### 3.76 共享服务端 SQLite 本地模式第一阶段（2026-10-18）

- 用户明确确认“所有规则按正式服开发的本地测试版”，授权实现。采用 `local_server/` 作为启动／配置目录，业务唯一真源位于 `server/src/mxsj_server/`，不复制第二套规则。
- 第一阶段：标准库 SQLite schema v1、显式初始化／校验、scrypt 随机盐凭据、随机会话票据摘要、持久化区服 epoch、接管／过期／撤销与事务内 fencing、角色元数据创建／归属查询／名称及策略约束、幂等回执同事务。
- 操作员控制台支持 init-db/check/provision/console；不开放端口、不给明文密码命令行参数、不自动建号／导入旧 JSON、不改客户端、不调用旧 Mock。旧两份 Mock 文件完全不变。
- SQLite 使用每事务连接、BEGIN IMMEDIATE、外键、synchronous=FULL 和有界锁等待；异常回滚，未知 schema／损坏库拒绝，不静默重置。未来 PostgreSQL 通过 Store 端口替换，必须实现同等锁／事务保证，当前尚无适配器，不能只改连接串宣称可部署。
- 38 项新增回归通过：错误密码、会话替换与到期、越权、同键异参、并发重复／同名、角色限制、真实 SQLite COMMIT 锁失败、回执写入失败回滚、未知／损坏库拒绝、独立 Python 进程恢复、CLI／分层边界。架构 161/161；新增代码 ruff、启动自检、local_server Windows 静态检查通过；不是 Windows BAT／EXE 或游戏验收。
- 角色策略是显式有限测试配置，不冒称已恢复官方完整创角规则；完整属性／背包／技能／资产初始化未做。enter_world 校验归属后明确 NOT_IMPLEMENTED，不能据此进图。
- 本轮未迁入旧客户端 TCP／legacy 认证、地图／战斗／任务奖励，未构建 Windows EXE；已提供构建入口但待实机。下一阶段先固定客户端凭据／报文证据并迁入协议层，不搬旧 Mock 的免认证、固定 key 或自动补丁逻辑。
- 详细使用与限制见 [local_server](../local_server/README.md)，检查见 [本轮证据](analysis/evidence/local_runtime_phase1_20261018.json)。原包与 key DB 摘要未变，无数据库／凭据生成物入库。

### ui_editor 目录型基路径诊断归类（2026-10-19）

用户在官服客户端副本上实测：`login_new/newlogin_800.dlg` 中以 `\` 结尾的
`sFileName`（如 `combdialog4\新登陆界面\三态按钮\声音按钮\关闭\`）被诊断误报
「已挂载资源中未找到」，但游戏正常加载。结案依据：`notes/fls_path_hash_and_dlg.md`
探针 v7 的 706 条目录型伪引用（运行时拼子图、包内无此条目、永不命中）；
反编译 `script/login/loginin.py::SetMusicBtn` 证实 `SetPath(基路径)+SetFrame(n)`
切换 `打开\`/`关闭\` 目录；用户手动输入 `基路径+0.png/1.png/2.png` 在编辑器中
可见（`3.png` 不存在，帧集为三帧）。另实测 `输入底框\`、`上文字底\`、
`勾选框底\` 等基路径同样只显示占位框，子图拼名族不同（按钮序号帧 vs
边框 left/middle/right 等，见 combdialog.py 字面量）。

- 本轮实现（① 诊断归类）：`core/diagnostics.py` 对资源字段以 `\`/`/` 结尾的
  引用改报 `RESOURCE_DIR_BASE`（提示），不再报 `RESOURCE_MISSING`；探测
  `基路径+0.png` 作线索，命中/缺席均不判缺（缺席可能是其它拼名族）；
  未挂载来源时也归类。不改 `.dlg` 字段值、不改任何客户端资源。
- 实测：`tests.test_diagnostics` 21/21（新增 3 项回归，含误报复现）；无 Qt
  核心套件通过（158 项 ok/36 跳过）；ruff 0 报告；`check_windows_compat`
  0 ERROR/0 WARNING。Qt/GUI 模块（test_gui*/test_assets/test_painters 等）
  因沙箱缺 `libGL.so.1` 导入失败，未执行不算通过；Windows/官服实包未验收。
- 未做（待授权）：② 画布按控件族拼帧预览（按钮→`0.png`…、横框→
  `left1.png`/`middle.png`/`right2.png`、九宫格→分片）；`.spr`（CSpriteFrame）
  解码——用户实测画布占位，SPR 格式无样本无结论，需官服 `interface.fls`
  条目字节（预期哈希 `0x1310B991`）才能定案「未找到 vs 未解码」。
- 下一步：用户验证 `勾选框底\0.png` 等子图候选；或提供 interface.fls 后
  批量枚举各基路径子图、推进 ② 与 SPR 悬案。
