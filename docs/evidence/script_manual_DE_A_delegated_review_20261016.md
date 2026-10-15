# D/E 八篇正式代审（A代审，2026-10-16）

> 用户明确授权：“H宕机了你审吧”。实际审核者 **A_delegate**，不是独立H。审核不再等待20篇齐备。仅对已提交的冻结恢复候选进行有限静态解释审核；不是原始源码、原生、实机或服务端验收。

## 1. 固定输入与结论

- A工具起点：`542597c262483b0b2f49d6e54b640888ba8c1726`。
- D：`1f6fdd323475e3940ea95b19e62c452e58dbd259`；E PR36：`60c573956f12a739712e4b24ddf1fb852f71bff0`。未改作者正文。
- 前轮仅来源复现/关键链预审；本轮逐项比较八篇职责、240条已列类/函数、118个关键分支、资源/上下游/修改指南与局限。签名自动定位240/240吻合仅是辅助检查，不是自动语义验收。
- D十二份候选/pyc摘要与3142行摘录、E五份去六头摘要沿用已独立复现的固定快照，本轮重新阅读比对，不冒充重新下载/恢复全包。两份前序收据见机器收据。

| 作者 | 模块 | 已列类/函数 / 分支 | 本轮决定 | JSON原字节SHA256 |
|---|---|---:|---|---|
| E | `connect.json` | 24 / 7 | 退修：C1 | `3c32bc2397114566c1fe35dcb32036ff695f33e9da4b0f734f0145f198e323e9` |
| E | `net.json` | 52 / 23 | 退修：N1,N2,N3 | `e00bd3e82ff47faf1d93b4f29a4916a54c484ce252c84a023850619ba9039a1d` |
| E | `netquicklogin.json` | 29 / 6 | 退修：Q1,Q2 | `9c2a8cd021148264f1069469fdb366e1857d4ebc3c80004f3cbb2c3ea52ce678` |
| E | `netserver.json` | 52 / 7 | 退修：S1,S2,S3,S4 | `0eca5474ea815ad5269c4659db590344ec504399aa2778ef3db2eca41d961621` |
| D | `chatoutput.json` | 25 / 21 | 有限通过 | `bb4b492a400adfcb7812b255e76c51a0c655e24e34c0f49121448959068bf799` |
| D | `interface.json` | 22 / 24 | 有限通过 | `a8c3ddf43ef74a6a0fe4319dc6922233ae9e44583523fe26d72830a3d9258318` |
| D | `key.json` | 19 / 13 | 有限通过 | `745bd2579c85ab7e1faf9deb78fd37cedb23bb0a5e322b398064a2c8ed4f4b0f` |
| D | `mainmenu.json` | 17 / 17 | 退修：D1 | `a88bd387abcc8e0edcb3f6a1dd0258a922ef149332c3f16f66e63238f8cee48d` |

**3篇有限通过：interface、key、chatoutput，共66条类/函数、58个已列分支；5篇退修，共11项P2。** 有限通过只覆盖已整理子集，绝不推导全模块已解释/候选可回编/游戏正确。

## 2. 逐项退修（全部是文档修订要求，不要求修游戏候选）

### D1 · P2 · entry 219 / `PushCall`

- 作者原文件：[固定提交 L427](https://github.com/a565551313/MXSJ_TW_2022/blob/1f6fdd323475e3940ea95b19e62c452e58dbd259/script_manual/annotations/ui_chat/mainmenu.json#L427)；字段 `functions/PushCall/summary; functions/PushCall/calls`。
- 已绑定候选行：377–385; Recall 1277–1285（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：PushCall被写成主界面存在时立即func，否则排队；冻结候选本函数仅无条件_g_Callback.append((func,args))，没有主界面判断或直接调用。Recall还出现cl = [_[1] for x in _g_Callback]的变量不对应形态，不能直接保证逐个回调成功。
- 要求：把PushCall改为候选字面的无条件排队，移除不存在的func直接调用；Recall只说明声明的回调/清队列代码并登记推导式异常及执行成败待核。不要修写候选或按历史实现补逻辑。

### N1 · P2 · entry 3176 / `CNet.PacketPrepare`

- 作者原文件：[固定提交 L594](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/net.json#L594)；字段 `functions/CNet.PacketPrepare/summary`。
- 已绑定候选行：901–904（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：说明把记录m_NetHead放在原生PacketPrepare之前；候选顺序是先CNetClient.PacketPrepare(self,a)，再self.m_NetHead=a。
- 要求：按候选纠正调用顺序；不要据此承诺原生发送/回调行为。

### N2 · P2 · entry 3176 / `LowestUnpackParams`

- 作者原文件：[固定提交 L49](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/net.json#L49)；字段 `functions/LowestUnpackParams/summary`。
- 已绑定候选行：55–69（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：“每轮2包”漏掉帧率缩放。候选先写一次原生2，但随后UNPACK_PACKET_NUM_PER_PROCESS=2/iRate并再次回写；例如iRate=2时末次设值是1。
- 要求：区分初次写2和最后按帧率缩放回写，不把最终预算恒定写成2；原生是否采纳未验。

### N3 · P2 · entry 3176 / `CNet.GetServerName`

- 作者原文件：[固定提交 L281](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/net.json#L281)；字段 `functions/CNet.GetServerName/summary; functions/CNetServerCommandQueue.Loop/summary; limitations`。
- 已绑定候选行：696–708; 1323–1341（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：GetServerName候选含serverinfo = [_[1] for x in s.splitlines() if x.strip() != '']，表达式不随循环变量x取行，不能无条件解释为正常读取各服务器记录后匹配。另类级已注明低优先队列赋值异常，但Loop函数摘要仍写“否则低”，容易把已知未结控制流当作可用路径。
- 要求：明确GetServerName候选推导式异常、正常查名行为待核；Loop函数摘要同步限定“声明的高/低选择意图”，不把低优先路径写成已确认能消费。可保留两段候选字面，不要求修复游戏。

### Q1 · P2 · entry 871 / `ModuleReset`

- 作者原文件：[固定提交 L28](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netquicklogin.json#L28)；字段 `functions/ModuleReset/summary`。
- 已绑定候选行：14–39（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：摘要声称重置点击/失败标志。候选ModuleReset没有g_bHasQuickLoginFail赋值；g_bHasClickQuickLogin=False虽出现却未列global，按文本是局部赋值。模块顶层初值不等于再次调用ModuleReset会重置这两全局。
- 要求：仅列已声明global且赋值的重置状态；区分模块初值、局部同名变量与未重置全局，标注候选作用域异常待核，不声称实机bug。

### Q2 · P2 · entry 871 / `CanQuickConnect`

- 作者原文件：[固定提交 L570](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netquicklogin.json#L570)；字段 `modification_guides/断线后不弹瞬连框/answer/evidence`。
- 已绑定候选行：CanQuickConnect 242–244; net.OnError 856–872; main相应触发段（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：该静态问答谈CanQuickConnect、net.OnError退出/重登门禁和main窗口触发，却只引用q_src_state（仓库旧稿18–62行）；这段不覆盖这些函数和调用方。
- 要求：把证据拆到实际CanQuickConnect/清Key、net.OnError和main调用行；若不提供某跨模块来源则降为待核/缩小回答，不能借状态初值证明整条诊断链。

### S1 · P2 · entry 516 / `CMXNet`

- 作者原文件：[固定提交 L415](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netserver.json#L415)；字段 `functions/CMXNet/summary; modification_guides/同名CMXNet`。
- 已绑定候选行：292–295; 441–443; 514–516（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：类级摘要仍写“未握手前不走主通道分发”，但OnServerCmd只检查hasattr(self,'m_Hello')，并非真值；创建测连对象时已设m_Hello=False，仍满足属性存在条件。方法分支已经正确提示不要写成已握手，但未贯彻到类说明。
- 要求：统一类摘要、同名类对照问答和方法说明为属性存在门闸；不能把False过滤或握手完成当作此函数保证。

### S2 · P2 · entry 516 / `CMXNet.PacketPrepare`

- 作者原文件：[固定提交 L443](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netserver.json#L443)；字段 `functions/CMXNet.PacketPrepare/summary`。
- 已绑定候选行：287–290（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：说明称记录m_iCmd后调基类；实际候选先net.CNet.PacketPrepare(self,icmd)，再self.m_iCmd=icmd。
- 要求：纠正先后顺序，与net.CNet.PacketPrepare各自层次分开。

### S3 · P2 · entry 516 / `RefreshServerInfo`

- 作者原文件：[固定提交 L71](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netserver.json#L71)；字段 `functions/RefreshServerInfo/branches/0`。
- 已绑定候选行：68–99（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：“时间戳差<=1200即跳过刷新”遗漏tm>now分支。例如tm=101、now=100，差为-1却命中tm>now并刷新。候选float解析失败又落except而不进else，不能将tm=None的理想兜底补成已确认流程。
- 要求：照候选写全permission门禁及else里的(tm is None or tm>now or now-tm>1200)；跳过条件需排除未来时间戳，区分解析异常路径。HTTP拉文案仍在外层执行，保持来源说明。

### S4 · P2 · entry 516 / `CRandomConnectMgr.Connect`

- 作者原文件：[固定提交 L661](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/netserver.json#L661)；字段 `functions/CRandomConnectMgr.Connect/summary; branches/1`。
- 已绑定候选行：426–476（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：分支只整理“首轮自动代理再扩一轮”，但候选递归条件是(self.m_Time-1 != 0) or g_AutoProxy；递增后m_Time=2且非自动代理同样再次Connect，不能让修改指南读成仅首轮自动扩一轮。
- 要求：给出完整递归谓词和m_Time先自增的顺序，登记后续轮数也可立即递归的字面行为/疑点。不要按意图改成AND或把候选修好后冒称原文。

### C1 · P2 · entry 2170 / `DoConnect`

- 作者原文件：[固定提交 L290](https://github.com/a565551313/MXSJ_TW_2022/blob/60c573956f12a739712e4b24ddf1fb852f71bff0/script_manual/annotations/network/connect.json#L290)；字段 `functions/DoConnect/summary`。
- 已绑定候选行：184–196（含恢复头的R行，非原始源码行；候选摘要见机器收据）。
- 问题：总摘要称无代理“按电信/网通各发一次”，但else依据IsDianXin二选一target_idx=0或1，只有一次ConnectAttempt。其分支描述已经写对，摘要仍与之矛盾。
- 要求：将无代理摘要改为二选一发一次，保留有代理前两条各一次以及三处Fail双回调/Success未引用的缺失说明。

## 3. 有限通过理由与保留边界

- **interface（22/24）**：逐项核样式动态导出、鼠标回调登记与左右键分派、Capture拖动、OpenUI/布局尺寸、点击msgid与回调优先级、CClickBox实际签名、CharInput/IME、CEdit输入/复制粘贴与路径选择。特别核对左右键在无OnMessage时不同的回退行为；Active(False)控制流异常已明确保留，不认定为可用实现或实机bug。
- **key（19/13）**：核空允许表放行、四例外、CFunctor保存/删除与空格标志、匹配/编辑模式提前return、RegisterHotKey与Ex差异、IsHotKey仅查询、GetCallFunc、鼠标直接注册、F11与系统热键查询。没有把损坏登记helper恢复成合法函数，也未推定原生事件顺序、线程和物理默认键位。
- **chatoutput（25/21）**：核AddChat缓存先于无窗口返回、延迟替换、频道映射/筛选、可见索引/对象重建、左右键显示与接收位分离、场景穿透/动态链接、Show与内外置配置、翻页、漂字及内存过滤。基础滚动异常、新气泡链接衔接、布局/字体/外窗及服务端采纳继续未知；没把发送调用写成网络成功。
- 菜单4号信号→Skill命名不等于技能页、实际锻造委托及animation多订阅；主模块快捷键/输入框并行入口和布局路径只按静态调用/字符串核对，仍没有读取/验证资源实际存在或运行引擎。
- E先前五项修订仍有效：OnError布尔条件、OnLogin后隐藏、未引用Success、稳定摘要、计时单位；本轮新发现的其他函数/分支失真不能由前轮预审抵消。已标注的帧长2/3冲突、回调异常、计时器异常/DGW缺链不得为消除退修而删掉。

## 4. 可机验记录与激活边界

- 八份 `$defs.review` 记录在 `script_manual/coordination/delegated_reviews_20261016/A_delegate_<entry>.json.template`；包含实际审核者、用户授权、accepted/changes_requested、说明原字节SHA、范围和逐项意见。不是占位模板结论；后缀仅为避免正式目录出现孤立review。
- 正式正文尚未合入，本轮不擅自merge领域提交/批准B目录。正式仍 **20种子 / 1说明 / 0审核通过**。仓库外A20种子+D/E覆盖有9说明、3通过、5退修、1未审；7条关联未建档警告明确保留，不借B已知错误目录消警告。
- 用户授权集成后才能将对应记录激活到reviews；激活前重算实际正文原字节SHA，改变一个字节就必须重新审核。本轮对3份实际通过JSON各加1字节，均降为stale且通过数3→2，复原后回到3。
- dev3 schema允许H/A_delegate，A_delegate必须填delegation；C等领域作者仍被拒绝。查看器表格/详情和单HTML显示实际审核者、授权、意见与绑定SHA，汇总改称“审核通过”而非“H通过”。保留H兼容、拒绝孤立/重复审核、字节过期、安全转义。
- 旧 `H_QUEUE_D_1f6fdd3.json` / `H_QUEUE_E_60c5739.json` 保留为固定历史输入快照，其“等20篇”gate由本报告及CONTRACT§4.1覆盖，不再执行。

## 5. 本轮实际验证

- 正式、仓库外D/E覆盖：schema/来源摘要/行号验证通过；正式20/1/0，覆盖20/9/3。未运行full闸门，20种子不能宣称全量5135。
- 根与覆盖两组各 **82项：71通过、11 Qt因libGL.so.1缺失跳过、0失败**。4项新增行为回归覆盖代审授权必填、身份/意见显示、原字节过期、H兼容和恶意文本转义。
- ruff含spec通过；Windows静态检查68路径/26源码，0错误/0警告/0信息；JS `node --check`通过。
- 仓库外离线HTML构建通过；jsdom26.1.0执行真实页面脚本，核3个A代审通过、5个退修、意见/绑定SHA展示与过滤。**jsdom不是浏览器或真实Qt**，本轮未运行真实浏览器/Windows/EXE/游戏/原生/实服。
- 机器收据：`docs/evidence/script_manual_DE_A_delegated_validation_20261016.json`，含逐函数定位/签名辅助结果、118分支记录、11发现、全部正文/审核原字节SHA和外置验证产物摘要。未将候选源码、生成站点或npm依赖搬入Git。

## 6. 协调

- B PR38、F PR37原误指master，已用REST PATCH并核响应改为固定A分支；未修改head、未合并、未代owner创建PR。前次gh pr edit的GraphQL classic Projects错误不等于改base成功。
- D三份有限通过/一份退修；D仍需owner在固定分支交PR到A。E四份按本轮意见退修，优先修摘要/分支与证据，不重做全量恢复。B/C/F既有退修不因此放宽，G仍待交。
