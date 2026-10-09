# 文档与证据审计

- case: `dream-world-connect-login-map`
- 审计时间: 2026-10-09 Asia/Shanghai
- 审计范围: `report/analysis.md`、`report/handoff-20261009.md`、`timeline.md`、`workitems.md`、`evidence/E-REA-*`、相关 notes、`scope.md`
- 审计模式: 只读审阅；本文件是唯一写入物，未修改主报告、时间线或工作项
- 自动审查: `C:\Users\Admin\.codex\skills\reverse-skill\case-review\scripts\review_case.py ... --format markdown`
- 自动审查结果: `FAIL`，47 errors，0 warnings，16 evidence，9 workitems，10 timeline events，13 findings，1 path

## 结论摘要

当前材料的分析方向基本一致：已确认本地服务器配置、客户端连接相关静态接口、`0x2714 -> OnServerCmd(int)` 边界、FLS 全量 zlib 解压；仍未确认登录 opcode、服务端响应、账号页切换、角色/世界状态或地图进入。主要问题在于文档状态没有完全收敛，历史证据与当前结论并列时缺少统一的“截至时间/是否取代”标记，证据索引存在断链，E-REA-008 的关键结果尚未具备独立复现材料。

## 高优先级问题

### A-001：证据图存在明确断链

- `workitems.md:10` 引用了 `E-IDA-001..E-IDA-007`，当前 `evidence/` 只有 `E-IDA-007.md`；前六项实际写在 `notes/ida-protocol-interface.md`，没有独立 Evidence 文件。
- `workitems.md:11` 的 `E-001..E-008` 中，`E-006`、`E-007`、`E-008` 没有对应的顶层证据文件；现有相关内容实际是 `E-REA-006..008`。
- `timeline.md:23` 同样引用了不存在的 `E-IDA-001..006`。
- 建议：二选一并保持全案一致：
  1. 为接口笔记中的 E-IDA-001..006 生成独立 `evidence/E-IDA-00x.md`，并保留 `notes/ida-protocol-interface.md` 作为汇总；
  2. 将所有引用改为现有证据编号或 `notes/ida-protocol-interface.md`，不要把 notes 中的局部小节误当成顶层 Evidence。
- 推荐方案：补建 E-IDA-001..006，因为这些条目已经在 notes 中有明确标题、地址、函数和结论，补建后可保留既有时间线语义。

### A-002：E-REA-008 的核心结论只有交接摘要，缺少独立复现链

- E-REA-008 的 `source_type` 是 `user_provided_investigation_handoff`，明确写明本轮未重新运行。
- 其最重要的结论是“entry 516 经五层 XOR 得到完整 Python 2.7 marshal 树、59 个代码对象”，但没有命令、脚本、输出摘要、解码产物 hash 或 REA Evidence ID。
- `notes/entry516-expanded.bin` 存在，但 E-REA-008 没有引用它，也没有说明它是原始 zlib 展开数据、五层变换中间产物还是最终数据。
- 建议：
  - 添加只读复现脚本或命令记录，保存五层变换参数、输入/输出 hash、marshal 解析统计；
  - 对“59 个代码对象”“`CMXNet.OnServerCmd`”“`ProcessServerCmd`”“`C2STransferServer`”分别给出可定位输出；
  - 若暂时不能复现，将 E-REA-008 的状态降为 `reported`/`handoff_only`，在 F-011 中把该结论明确标成“待独立验证”，不要使用“已恢复”式标题作为无条件事实。

### A-003：历史缺失 `script.fls` 与当前已存在 `script.fls` 的覆盖关系需要统一

- E-REA-005 记录 14:46 时工作副本缺少 `data/script.fls`，E-REA-006 记录后续仓库同步已出现该文件；这一点本身不矛盾。
- 但 `report/analysis.md` 的 F-010 标题仍是“当前工作副本缺少”，虽然正文已写“当前状态由 F-011 更新”；读者容易把 F-010 当作当前状态。
- `report/handoff-20261009.md` 没有明确说明 `script.fls` 已通过 E-REA-006 补入当前工作区，只保留了较早的“缺少文件”背景。
- 建议：将 F-010 标题改为“历史状态：14:46 工作副本缺少 `data/script.fls`”，并在正文顶部加入“被 E-REA-006/F-011 取代，不代表当前文件状态”；handoff 增加当前文件 hash/大小和 E-REA-006 链接。

### A-004：暂停边界与当前用户重新要求不一致

- `timeline.md` 18:52 事件写入“按用户明确要求暂停，不继续分析”。
- `workitems.md` 中 WI-006、WI-008、WI-009 均为 `paused`，handoff 末尾也写“Resume only after a new explicit user request”。
- 当前任务已经是新的明确请求，故这些内容应被视为历史停点，而不是永久状态。
- 建议：不删除历史记录；在新一条时间线事件中记录“暂停已解除/进入多 agent 审计与继续分析阶段”，并将工作项状态迁移到审查器支持的状态（例如 `in_progress` 或项目约定的 `blocked`/`done`），同时在 notes 中保留原暂停原因。
- 本审计不修改 `timeline.md`/`workitems.md`，只提出修订建议。

## 中优先级问题

### B-001：状态枚举不符合 case-review 契约

自动审查报告出错：

- work item 状态：`paused` 不受支持（WI-006、WI-008、WI-009）。
- evidence 状态：`observed_static`、`observed_static_partial_decode`、`reported_static_analysis`、`observed_user_report` 不受支持。
- finding 状态：F-005 至 F-013 的状态不受支持。

建议统一到 `case-review/scripts/review_case.py` 实际接受的枚举，而不是自行扩展状态名。迁移映射应由主控者确认后一次性执行，例如：

| 当前值 | 建议语义 | 修订原则 |
|---|---|---|
| `observed_static` | `observed` | 观察到的静态证据在 notes/字段中保留 `static/read-only` |
| `observed_static_partial_decode` | `partial` 或 `observed` | 必须在解释中写明“部分解码” |
| `reported_static_analysis` | `reported` 或 `candidate` | 未独立重跑的 E-REA-008 不应标成已验证 |
| `observed_user_report` | `reported` | 来源为用户观察，不等同于工具观测 |
| `paused` | `in_progress`、`blocked` 或项目支持的停点状态 | 以实际是否等待外部材料/新任务为准 |

不要仅为了通过脚本而把“用户交接”改成“已观察”。

### B-002：多个 E-REA 条目缺少 `repro_command` 或明确离线限制

自动审查报告指出 E-REA-002 至 E-REA-008、E-USER-001、E-LOOPBACK-001 等证据缺少可复现命令或明确的 offline limitation。当前条目通常有 `provider`、`source_ref`、`effects`、`limitations`，但审查器不把这些字段自动视为复现说明。

建议每条证据至少补充以下之一：

```yaml
repro_command: |
  在 case 根目录执行的只读命令；路径使用当前 Windows 工作区
```

或：

```yaml
repro_command: n/a
notes: |
  该条目是用户观察/历史交接，当前无原始运行环境；未独立复现。
```

E-REA-008 应使用第二种形式，不能伪造复现命令。

### B-003：哈希字段命名与位置不符合自动审查器预期

自动审查报告对 E-IDA-007、E-LOOPBACK-001、E-REA-001..008、E-USER-001 报告 `content_hash` 无效。主要原因是条目使用了 `sample_sha256`、`bundle_sha256` 或没有 64 位 `content_hash`；样本 hash 并不等于证据 Markdown 文件 hash。

建议：

- 对证据条目自身增加 `content_hash: sha256:<64 hex>`，或者按照项目约定记录证据文件固定 hash；
- 样本 hash 继续保留为 `sample_sha256`，不要覆盖或混淆；
- 对用户报告/历史诊断没有可固定原始 artifact 的情况，明确 `content_hash: n/a` 并在 `notes` 中说明原因，或让审查器支持非文件型证据；
- 若采用 `artifact_path`，必须是 case 根目录内的真实相对路径，避免引用 `/workspace/...`。

### B-004：历史路径与当前工作区路径混用

- E-REA-001..006 多处使用 `/workspace/MXSJ_TW_2022/...`，当前 case 的真实输入在 `D:\Lager\夢想世界\...`。
- `report/analysis.md` 已部分改用当前 Windows 路径/相对 case 路径，但 evidence 原文仍保留历史路径。
- 建议所有证据同时保留：
  - `historical_source_ref`: 原始分析环境路径；
  - `artifact_path`: 当前 case 内的相对路径（若已复制并 hash 一致）；
  - `sample_sha256`: 样本 hash。
- 若当前 case 没有对应 artifact，不要把历史 `/workspace/...` 路径写成当前可复现路径；改成“历史环境路径，仅用于来源追踪”。

### B-005：E-REA-003 与 E-REA-004 的结论边界应在主报告中更显眼

- E-REA-003 只确认静态事件分派：`0x2711`、`0x2712`、`0x2714`。
- E-REA-004 进一步确认 `0x2714` 路径通过 `IMP_ReadUInt16` 向 Python bridge 调用 `OnServerCmd(int)`，但仍没有运行时调用、具体命令值或脚本绑定。
- 主报告 F-007/F-008 目前总体写得谨慎，但 F-008 标题“服务端事件”容易被误读为已观测到服务端事件，而证据只是静态事件码分支。
- 建议标题改为“静态事件码 `0x2714` 的服务端命令候选路径”或在标题前加“静态：”；在 impact 第一行加入“未证明该事件在本次运行中发生”。

### B-006：`E-REA-002` 对导入 ordinal 的表述应继续标注为映射结果

E-REA-002 使用“ordinal 11/101/103”并结合接口笔记映射为 `htons`、`connect`、异步 API。证据条目已经写了限制，但后续摘要容易把 ordinal 身份当成原始符号确认。

建议在所有摘要中采用：

> “按当前导入槽/接口笔记映射为 `htons`/`connect`；ordinal 的完整符号身份和异步完成处理尚未全部独立闭合。”

不要简化成“ordinal 11 就是 `htons`”。

## 低优先级问题与整理建议

### C-001：F-011 存在重复 `supersedes` 字段

F-011 在连续位置出现两个 `supersedes` 字段：一个描述 E-REA-007/F-012 的旧解码状态，另一个描述 F-010 的文件缺失状态。语义都有效，但结构化解析器可能只保留最后一个。

建议合并为列表：

```yaml
supersedes:
  - E-REA-007 / F-012 的旧解码状态
  - F-010 关于当前工作副本缺少 script.fls 的历史状态
```

### C-002：F-013 的证据等级应与 F-011 一致

F-013 完全依赖 E-REA-008 的用户交接摘要，当前标注为 `reported_static_analysis`，这比“已观察静态分析”更谨慎，但需明确它是“二手分析报告”，不是当前任务独立证据。建议在标题或 `confidence` 中加入 `handoff_only`，并链接到待补充的解码复现材料。

### C-003：notes 中的旧状态机段落需要分层标注

`notes/state-machine-draft.md` 同时包含：

- 初始候选状态机；
- Ghidra 更新；
- 当前 E-USER-001/E-REA-008 停点。

内容没有实质冲突，但读者可能把早期“历史 next offline checks”当作当前计划。建议把旧段落标题改成 `Historical next checks`，把最新部分置于文档顶部或增加“current status”表。

### C-004：handoff 缺少当前证据索引和未决问题矩阵

`report/handoff-20261009.md` 主要总结了 E-REA-002 和 loopback 工具，没有完整列出：

- E-REA-003/004 的事件桥；
- E-REA-006/007/008 的脚本资源进展；
- F-010 被 F-011 取代；
- 关键未决项与对应证据。

建议新增一张简表：`问题 | 当前结论 | 证据 | 置信度 | 下一步`，尤其列出“登录首帧/响应、命令值、脚本绑定、S2->S3、地图 ID、空地图判定”。

### C-005：`workitems.md` 的 Coverage 与当前材料不完全匹配

- `Validated findings have Evidence` 已勾选，但 F-011/F-013 的关键部分来自未独立复现的 E-REA-008，应改为“关键 finding 均有 evidence 引用；部分为 reported/handoff-only”。
- `Path documented` 已勾选，但 P-001 仍是候选 callflow，且不是完整的协议/状态路径；建议把勾选旁注改为“候选路径已记录，验证路径未完成”。
- `field-journal anonymized` 未勾选，当前确实没有看到完成标记；若交接要求 field journal，应补齐或明确不适用。
- `roles assigned` 在 `scope.md` 未勾选，且 specialist_roles 为空；如果当前已采用多 agent，应补写角色和输出文件映射。

## 当前证据链的推荐分层

### 已直接支持

- E-001/E-002：服务器配置与最近服务器名称到 endpoint 的静态映射。
- E-003/E-004/E-005：登录/选服日志、字符串线索、地图资源格式线索。
- E-IDA-007：`mx.exe` 对 `IMProtocol.dll` 的静态导入关系。
- E-REA-002：`IMProtocol.dll` 内到 Winsock connect 的静态链路。
- E-REA-003/E-REA-004：静态事件分派与 `OnServerCmd(int)` 桥边界。
- E-REA-006/E-REA-007：`script.fls` 存在、FLS 全量解压验证、`PY_CODERESOURCE=8` 的 `imp` 常量解释。
- E-USER-001：用户观察到选服/下一步打开“连接服务器”对话框；这是报告型证据，不是工具运行观测。

### 报告型/待独立复核

- E-REA-008：entry 516 五层 XOR 后的 59-code-object marshal 树、方法名集合、非标准 `co_code` 层。
- F-011/F-013：依赖 E-REA-008 的脚本控制流和 loader 结论。

### 尚未形成证据

- 登录请求首帧及服务端响应；
- 具体 opcode/命令值；
- `ProcessServerCmd` 与原生 `OnServerCmd(int)` 的绑定；
- 账号登录页的确切切换条件；
- 认证成功、角色列表、世界入口；
- 地图 ID、初始坐标、空地图的可重复判定；
- 3134 端口是否属于主登录通道而非辅助/NsServer 通道。

## 推荐修订顺序

1. 先修复证据编号断链：E-IDA-001..006、E-008 的缺失或错误引用。
2. 统一 status 枚举，并给 E-REA-008 标出 `reported/handoff-only`。
3. 给 E-REA 条目补 `repro_command` 或规范的 `n/a + offline limitation`。
4. 分离历史路径与当前路径，补齐当前 case 内 artifact/hash 关联。
5. 将 F-010、F-011、F-012、F-013 的 supersedes 关系改成结构化列表，并在 handoff 加 current-status 表。
6. 记录新的“暂停已解除/多 agent 审计开始”时间线事件，再迁移 WI-006/WI-008/WI-009 状态。
7. 重新运行 case review；只有 errors 清零后再声称证据包可交接。

## 审计结论

分析结论本身没有发现“已确认登录/进图”这类过度升级；主要风险是证据包的可审计性和接手者对当前状态的误读。最关键的内容修订是：把 E-REA-008 降级为可追踪但未独立复现的 handoff 证据，把 E-REA-005 明确标为历史缺失状态，把未创建的 E-IDA/E-008 引用补齐，并让时间线/工作项反映当前暂停已解除这一事实。
