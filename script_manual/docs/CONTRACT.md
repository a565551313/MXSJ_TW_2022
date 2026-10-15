# 手册数据契约 v1

## 1. 版本与身份

`coordination/baseline.json` 钉死分析用仓库提交、两包 SHA256、条目数、双VM、参数表摘要和语料引用；工具版本在 `pyproject.toml` / `mxsj_manual.__version__`。包名、展示路径不能代替指纹；换包必须新建分析基线，不能沿用旧说明假装已验证。

原始 script.fls `8b6e9266…` 的1288只登记 `excluded_by_policy`，`path=null`、`functions=[]`；禁止读payload、恢复内容、分任务或写正文。本工具额外拒绝解除这个固定包的排除声明。data.fls 的目录条目只登记，不能当脚本写说明。

PR34 `full/manifest.audited.jsonl` 是可用的外部语料入口，**不是本项目已经下载并钉摘要的输入**；当前状态 `external_reference_not_loaded`。B对接时须给出实际manifest/候选/引擎版本指纹，A审核后更新基线。旧catalog、旧恢复稿、PR34语料、编辑器dev6恢复引擎不是同一来源，严禁混称。

## 2. 目录：`inventory/modules.jsonl`（B独占）

UTF8 JSONL，一行一条，不能重复主键。每条必须且仅包含：

| 字段 | 含义 |
|---|---|
| archive_sha256 / entry_index | 固定包SHA / 从0开始的原始entry号，禁止重新编号 |
| path | 包内展示路径；不可确认时null；不能拿entry ID伪装真实路径 |
| vm | py25或py27，必须与基线一致 |
| path_status | structurally_read / historical / unreadable / directory / excluded_by_policy |
| functions | 自动元数据数组：name、signature（未知用null）、kind（function/method/class）。空数组表示尚未整理或不可读，不代表无函数 |

结构性路径可从原始marshal的co_filename读取；不能仅因旧catalog有名字就标 `structurally_read`。恢复失败/片段/语法通过的区别留在B提取回执，不以错误函数名补齐统计。存在同路径不同entry时保留所有身份，不合并。

B把完整目录替换这个单文件，保留20个初始身份（路径若确需纠错先报A）；不另外放一份重复的seed让加载器“最后覆盖”。另附 `inventory/B_extraction_receipt.json` 和必要说明，记录全部输入/工具/manifest SHA、提取命令、缺失/目录/失败/排除计数及抽样核对；回执不是可加载模块，不受record schema控制，A必须人工审阅后才能宣称全量集成。

## 3. 领域说明：`annotations/<domain>/*.json`（C–G独占）

权威格式是 `schema/contract.schema.json` 的 `$defs.annotation`，未知字段拒绝，不接受散落Markdown作为第二套底稿。示例 `examples/annotation.json`；文件名任意但必须唯一主键且放在正确领域目录。

2026-10-16 G停工后，其固定四篇由A代写：任务包owner仍G，author明确实际作者A，不伪称G提交；独立复核尚未完成，A不得用自己的代审身份自批这四篇。此例外不接管C–F正文返修。

必填：schema_version=1、身份、与目录完全一致的path、owner、domain、author、source_status、purpose、keywords、functions、resources、relationships、related_modules、modification_guides、limitations、sources、evidence。没有资料的列表可为空，**不要编造**。

- `purpose` / 函数summary / 分支effect / 资源summary / 修改问答answer均为 **Claim**：`text`、`confidence`、`evidence`。
- Claim.confidence：`extracted`=直接自动观察的事实；`inferred`=推测待核实；`static_reviewed`=作者已读证据并核对的解释；`runtime_verified`=作者有实机记录。**不是逐级自动升级**。非推测必须引用证据；实机结论还必须引用 `kind=runtime_report` 的证据。报告应含平台、输入SHA、操作、预期/实际、日志，机器只检查引用，真实性/充分性由H审阅。
- `sources`：id / 仓库内规范相对path / sha256 / kind(metadata、recovered_source、runtime_report) / note（来源、引擎、缺失等）。相对路径不得逃逸、带盘符、反斜杠或符号链接。源码从仓库外语料读取时，不把大语料搬进Git；先与A约定可分发的小证据摘录/审阅报告及其路径，注明原候选SHA和行范围，不能伪装成完整源码。未经允许不摘录1288或敏感内容。
- `evidence`：id、source_id、start_line、end_line，**从1开始，闭区间**，绑定原始UTF8文本字节摘要，不是重排后的代码位置；不可把AST解析/语法通过当行为证据。
- `source_status` 独立标来源：metadata_only、historical_unverified_origin、recovered_partial、recovered_complete_not_original、native_origin_checked_not_semantics。原生来源已核不等于反编译语义正确。
- `functions`：name用限定名（如CMainPage.OnMessage）去重；signature为参数文本，未知null；kind；summary；calls（静态引用字符串线索，未解动态调用不要写死）；branches（condition/effect，大OnMessage要拆消息条件）。空calls不表示无调用。未覆盖全部函数要写limitations。
- `resources`：kind(module/layout/file/config/image/sound/protocol)、target、summary。target只展示，不用来执行、请求网络或构造输出文件。
- `relationships`：direction(upstream/downstream)、kind(imports/calls/message/data_flow)、module（已知身份或null）、symbol（符号或null）、summary(Claim)。方向表示相对当前模块的上游/下游；动态目标未解用null并解释，不能仅凭相似名字建立确定调用。
- `related_modules`：只存身份，由查看器解析路径；这是“相关线索”，不自动认定caller/callee。
- `modification_guides`：question、answer。必须说清“改正文/URL/布局/调用入口分别在哪里”，标出待实机验证风险。
- `limitations`：至少写清来源缺失、未解释函数/消息分支、未证实动态关系和版本边界。不能把“未发现”写成“不存在”。

## 4. 任务归属与H审核

`coordination/tasks.json` 由A唯一维护，主负责人/domain固定映射：C/login、D/ui_chat、E/network、F/battle、G/gameplay。跨域只有一个owner，其他人通过协审报告向owner/A反馈，不重复建档。

正文作者不能把自己设成审核通过。常规独立复核由H提交，用户明确授权时由A以A_delegate代审，在 `reviews/*.json` 单独提交 `$defs.review`：schema_version、身份、annotation_sha256（**实际JSON文件原字节SHA**）、reviewer="H"（或用户明确授权的 `A_delegate`）、decision(accepted/changes_requested)、note。`reviews/example.json.template` 仅示意，不加载。

手册目录自带LF属性规则，bat例外为CRLF，防止Windows Git换行转换令正文审核失效。手动改写换行仍算字节变化。旧候选若在目录外被Git转换换行，摘要不匹配就应拒绝；须恢复来源原字节或提交新SHA并重审，不能放宽字节校验。

审核不是密码学签名；协作权限由工作流保障。A检查H身份/证据范围后集成。正文改动一个字节则审核变 `stale_review`，不再计入审核通过，须实际审核者重审。通过不代表游戏实机通过，也不替代源码来源状态。H可接受一份明确标缺失的有限说明，但不能据此把整个模块/全体函数说成已解释。

### 4.1 用户授权A代审（2026-10-16）

用户原话“**H宕机了你审吧**”授权A接手审核；不是独立H会话，也不是作者自批。
`reviewer="A_delegate"` 必须另填非空 `delegation`，写明授权来源和非独立身份。
该字段是工作流记录，不是认证凭据。H记录继续兼容；领域作者C–G仍不得作为reviewer。
查看器、离线页和导出数据必须显示实际身份、授权、审核意见和绑定SHA；总数称“审核通过”，不得把A记录标成H通过。
A不能为缺少正文的正式目录放孤立审核；本轮8份记录先存 `coordination/delegated_reviews_20261016/*.json.template`，不参与正式统计。
待领域正文经授权集成后，**逐个核对原字节SHA** 再激活至 `reviews/*.json`；不是自动merge授权。
不再要求等20篇齐备才能审核已有提交；保留有限范围和原生/运行期未知，不冒充全模块验收。

## 5. 集成闸门与只读边界

- 包指纹/条目范围/VM、重复身份、任务归属、路径漂移、正文跨目录、未知字段、悬空证据、反向或越界行号、过期审核分别处理；重复/硬错误退出2，过期审核显式警告并降为未通过。
- 常规加载不读取原游戏包；`--verify-evidence --repository` 只只读核对引用文本的SHA/行号，不import/eval/exec，不请求公告URL。
- 外部schema引用、JSON重复键/NaN、符号链接、路径穿越拒绝。单正文≤2MiB、全部说明/审核≤32MiB、目录≤16MiB、HTML≤64MiB，超限分批而非静默截断。
- 索引不完整允许预览，但要公开登记/说明/审核通过三种数。只有`--require-full-inventory`通过才说明“全部条目建档”，仍不代表全体函数解释完。
- 离线页面只用textContent；原生富文本转义所有数据；不以游戏路径生成文件；不远程加载内容。输出只创建仓库外的新目录，绝不覆盖输入或旧输出。
