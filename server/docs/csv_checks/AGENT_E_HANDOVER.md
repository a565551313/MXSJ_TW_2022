# AGENT E HANDOVER — 地图/NPC 检查的长期复现材料（接手 PR #16 之后）

**角色。** 本文件是原 Agent E（PR #16，合并提交 `db58fe1`，报告 `AGENT_E.md`）的接手
交付。目的不是重新调查全部客户端，也不是把 AGENT_E.md 当作权威结论转抄，而是把
原来保存在临时目录（`/tmp/mx`，已丢失）中的关键探针，变成仓库内可长期运行的
只读工具、回归测试和机器可读证据，并对报告逐条标注复现状态：**已独立复现** /
**仍是候选** / **尚未复现**。发现报告错误之处以勘误形式记录（见 §6）。

**约束遵守。** 全程只读于 `data/script.fls` 与 `tools/decompiler/*`；未执行任何恢复的游
戏脚本（无 `exec`/`eval`/`marshal.loads`——使用带绝对偏移的自写 marshal 遍历器）；未启动
`mock_server.py`；未修改公共密钥库与公共转译器（仅只读导入 `PY25_MAP`/`XTABS` 两张静态
表，并在证据中记录该文件 SHA-256）；未猜任何地图 ID/名称；`npcid == 0` 与重复记录全部
保留；不做繁简转换；未写 `server/game_data/`；不合并或回退任何 PR。LOAD_NAME 仅支持
字面量占位名 `None` 这一个特例，不放开任意名称查找。

---

## 1. 交付清单与运行方式

| 交付物 | 路径 |
|--------|------|
| 只读复现工具 | `server/tools/map_npc_reproduction.py` |
| 回归测试（39 项） | `server/tests/architecture/test_agent_e_map_npc.py` |
| 机器可读证据（测试钉死） | `server/docs/csv_checks/agent_e_reproduction.json` |
| 待审候选 CSV（暂存，非批准数据） | `server/docs/csv_checks/staging/`（9 个文件 + README） |

```
# 全套核查（含全档案消费者名称扫描），任一候选参数集失败则以非零码退出
python3 server/tools/map_npc_reproduction.py --check

# 重新生成证据 JSON 与暂存 CSV（确定性输出，测试会逐字节比对）
python3 server/tools/map_npc_reproduction.py --out server/docs/csv_checks/agent_e_reproduction.json
python3 server/tools/map_npc_reproduction.py --csv-dir server/docs/csv_checks/staging

# 回归测试
python3 -m unittest server.tests.architecture.test_agent_e_map_npc -v
```

输入完整性在每次运行时核对（证据与测试都断言）：

| 输入 | SHA-256 | 状态 |
|------|---------|------|
| `data/script.fls` | `8b6e9266…f27febaf6c0d72` | 与 PR #16 报告记录一致 |
| `tools/decompiler/script_fls_keys.json` | `43bb090d…7d09aac3d97daceb` | 与报告记录一致 |
| `tools/decompiler/batch_decompile.py` | 记录于证据 `inputs.shared_decoder` | 只读引用其 `PY25_MAP`/`XTABS` |

工具方法（独立于转译器的启发式修复）：payload → 按显式 (keys, bounds) 做 5 段 XOR →
自写 Python 2.5 marshal 遍历器（解析 interned-string 引用表、保留绝对偏移）→ 自定义
操作码流严格校验（criterion 1：操作码必须命中 `PY25_MAP`，参数必须在代码对象自身的
`n_consts`/`n_names`/代码长度之内）→ 字面量求值（criterion 3：仅允许
LOAD_CONST / `LOAD_NAME 'None'` / BUILD_TUPLE / BUILD_LIST / BUILD_MAP / DUP_TOP /
ROT_TWO / STORE_SUBSCR，终止于 STORE_NAME 或 STORE_GLOBAL；重复字典键报错）→ 跨表
见证（criterion 4）。**工具不含边界求解器**——候选与备选边界均以显式参数注入，使“通过
检查”与“被搜索出来”严格分离。

---

## 2. 五个主条目：可重复核查的判定矩阵（全部通过）

候选参数集在每个条目上都通过了四项判据；保存参数与投放参数都在预期位置失败。
直接来自 `agent_e_reproduction.json` 的 `verifications` 节：

| 条目 | 参数集 | 结果 | 失败环节（若有） |
|------|--------|------|------------------|
| 400 | saved `[961,2001,3063,4125]` | **PASS** | ——（原框架即正确，佐证 400 本身无缺陷） |
| 1301 | saved DB `[1612,3237,4884,6553]` | FAIL | 字节码（code 1591 遇 0x7c）＋字面量＋见证 |
| 1301 | **候选 `[1616,3239,4884,6553]`** | **PASS** | —— |
| 1301 | 投放 solver `(1615,3239,4884,6553)` | FAIL | **仅见证**：机械判据全过，文本键 兔坦卡門陵墓 |
| 1799 | saved `[528,1096,1655,2207]` | FAIL | cp950 两个常量＋见证（co_name 亦坏） |
| 1799 | **候选 `[528,1093,1652,2202]`** | **PASS** | —— |
| 2601 | saved `[18821,37733,56546,75375]` | FAIL | 字节码（code 18799 遇 0xf7）＋字面量＋见证 |
| 2601 | **候选 `[18827,37735,56546,75376]`** | **PASS** | —— |
| 2601 | 仅槽3用保存值 `[18827,37735,56546,75375]` | FAIL | **仅见证**：const[179]=4810，谷雨鎮商人 （1003,4810) 无佐证 |
| 2804 | saved `[26695,53365,79988,106627]` | FAIL | **仅见证**（机械判据全过） |
| 2804 | **候选 `[26695,53365,79989,106619]`** | **PASS** | —— |
| 2804 | 仅槽2用保存值 79988 | FAIL | **仅见证**：WENZI[1022][(28,108)] npcID=324≠2008 |
| 2804 | 仅槽3用保存值 106627 | FAIL | **仅见证**：const[544]=蓮７導姒（合法 cp950） |
| 4897 | saved `[26677,53319,79959,106579]` | FAIL | DATA_WENZI 字面量（79937 处 BINARY_RSHIFT）＋见证 |
| 4897 | **候选槽2 `[26677,53319,79961,106579]`** | **PASS** | ——（槽0 维持保存值，仍未确定） |
| 1870 | saved（不修） | PASS（判据1–3） | 但 co_names 含损坏名；**保持 unresolved** |

这张表同时是“**错误参数不能仅凭中文合法通过**”的回归证据：1301-solver、
2601-slot3、2804-保存、2804-槽2、2804-槽3 五个错框在字节码/结构/cp950 判据上全部
通过，全部被跨表见证否决（`verdict['witness_failures']` 非空）。测试
`WrongParameterRejectionTests` 逐条钉死。

**保存参数 vs 候选参数的字段与引用变化**（证据 `parameter_comparisons` 节，测试
`ParameterComparisonTests` 钉死）：1301 投放态与候选态的整表差异恰为“键 1071 加入 /
文本键 兔坦卡門陵墓 移除”（记录体不变、零行变化）；1799 保存态与候选态恰为两行换名
＋ co_name 复原（const[31]：损坏 hex→元靈遊仙；const[74]：损坏 hex→天選使者）；2601
槽3 恰为场景 1003 一条记录（const[179]：4810→4764）；2804 保存态恰为 DATA_POS 场景
1020 一条记录（const[544]：蓮７導姒→打漁老張）与 DATA_WENZI 场景 1022 一条
（npcID 324→2008）；4897 保存态仅失去 DATA_WENZI 一表。2601/1301 的全保存边界因解
码或字面量评估失败，差异如实记为“only under candidate parameters”。

---

## 3. 已独立复现（仓库内重跑、测试钉死）

以下报告结论在本仓工具下逐条重现；这些是**静态复现**，不等于原生客户端运行时验证
（见 §4）。

**1301 mapdata.py**：候选边界下 `DATA` 恰为 104 个整数键，每行 `{name, w, h}` 三字段齐
全、无重复键、无无效文本；`DATA[1071] = {name: 加洛法師師道殿, w: 1588, h: 1220}`；
`MAP_ASCRIPTION` 6 行 `{1039:1039, 1040:1039, 1041:1039, 1073:1073, 1074:1073,
1075:1073}`。投放边界下重现交付态异常：104 键 = 103 int + 1 bytes，bytes 键恰为
`兔坦卡門陵墓`（该记录 name 恰为 加洛法師師道殿），整数常量 1071 在常量池中孤立
（const[115]，本工具口径：模块代码中未被任何 LOAD_CONST 引用）；保存的 DB 边界在
code 1591 处字节码失效。杂散键的文本恰是 `DATA[1053]` 的场景名（解释了它为何看似
合理）。

**400 sceneid2name.py**：57 行全为 4 元组常量（上报的保存边界本身干净：字节码有效、
遍历恰好消费 4790/4790、0 无效文本）。与修复后的 1301 对账：57/57 键是其子集、
1071 其中、57 个场景名全部一致（0 失配）。交付态的 `not_in_map_catalog` 标记因此确认
为 **1301 侧的提取瑕疵**，400 数据本身为源值。

**1799 npcname2realnamedata.py**：保存边界下精确重现两个编码失败常量
（`a4b8c646b9dc3acf`、`a4d1bfefa8197c1a`，与调查单逐字节一致）及损坏 co_name
`b'<modu\xda\xd3\x88'`。候选边界下 55 行全部 cp950 干净、co_name 复原 `<module>`，
两行修复值为 `個人心法教師 → 元靈遊仙`、`天選使者 → 明威`。与 NPC 表交叉佐证复现：
2601 侧 175 条记录使用 36 个 alias；字段 11 非空且 alias 命中者 71 条中 70 条一致、唯
一失配为 `藥店`（map 1054, npcid 1078：1799 作 藥店老闆，记录作 裝備店老闆）；2804 侧
178 条/37 alias/74 命中/73 一致/同一失配。

**2601 npcposdata.py**：候选边界下 `DATA` 顶层恰 430 个键（场景数，非 NPC 数）、1335
条记录、每条恰 14 字段、632 条 `npcid == 0`、703 条非零记录映射到 665 个
`(scene, npcid)` 对、多重性直方图 `{1:653, 2:3, 4:5, 6:4}`（12 个多记录对的全部记录以
list 保留，无静默折叠）、field7 恒 255、378 种 shape（2601；2804 为 381 种）。保存边界在 code 18799 处字节码
失效（报告“payload 18821”的另一表述，见勘误 E4）；槽3 改回 75375 时结构全好但
`const[179]` 变 4810、谷雨鎮商人 落在 `(1003,4810)`——该对在任何表都无佐证，候选的
4764 则同时被本表与 2804 佐证。

**2804 minimapnpcpos.py**：确认模块内**不存在** `DATA`（调用 `table(b'DATA')` 抛
KeyError；NPEG 调查的“no supported literal assignment for DATA”确认为调查目标名错
误 = `confirmed_extraction_bug`）。`DATA_POS` 顶层 434 键、1344 记录、631 条零 ID、
嵌套 `{scene -> {scene 显示名 -> [records]}}`；`DATA_WENZI` 165 键/287 条，字段即源键
名 `{name, desc, jumpPos, npcID, npcName, servergrade}`。`const[544] = 打漁老張`，且其
字面表（(1020, 4229)）与 2601 同时佐证。槽2 由见证定值：备选 79988 使
`WENZI[1022][(28,108)].npcID = 324`，候选 79989 使其 = 2008，并与 4897@79961 的
165/165 场景全同相洽。

**2601 ∩ 2804 联合核对**：664 个共同 `(scene, npcid)` 对；8 对内容差异（与报告 §9.3
item 3 逐字段一致，双方记录完整保留于证据 `content_difference_detail`）；2601 独有
`(1179,5020)`；2804 独有 12 对（清单与报告一致）。**另有 9 对内容全同但记录顺序不
同**——报告未区分此情形，见勘误 E1。

**4897 minimapnpcpos_test.py（见证位）**：槽2=79961 下 `DATA_WENZI` 165 场景与
2804@79989 **165/165 全同**；`DATA_POS` 433 场景，与 2804 的共同对 674/674 记录列表
全同（2804 另有 9908 与 `(1327,5030)`）；保存值 79959 使 `DATA_WENZI` 字面量在 79937
处被拒（BINARY_RSHIFT）。

**1870 taiwan/npcpos_fix.py（标本位）**：保存边界下可完整遍历，模块与 `Fix` 的
co_names 中损坏名 `D~ChhiIha^ehcEeNpc`（`DelShenHeNpc` 的错位形态）与正确
`npcposdata / minimapnpcpos / DelShenHeNpc / Fix` 同现——与报告描述一致。按原判
保持 unresolved（见 §5），绑定语义不引用。

**消费者方向性佐证（字节级存在扫描，全 5002 条）**：`sceneid2name` 仅命中 400 自身；
`npcposdata` 仅命中 {1870, 2601}；`minimapnpcpos` 命中 15 条，报告 §7(a) 所列全部消费
者（159/450/518/539/949/1693/1697/1870/2120/2341/2965/4010/4676）都在其中；
`InitTestData` 命中 {1693, 2054, 2601, 2804, 4897}；`DelShenHeNpc`/`IsNeedDelShenHeNpc`
仅命中 {1870 或三表}。方法声明：字节子串匹配（含字面字符串命中，如 `*mapdata.py`
家族），弱于报告的 co_names 递归扫描；方向一致但未逐条重做 §7 精确清单。

**运行时变异的静态证据**：从 2804 候选框架提取嵌套代码对象 co_names/常量重
现——`InitTestData`（names 含 `DATA_POS, values, enumerate, insert`；常量含
`1054, 戰隊使者, 無雙, 5025, 33, [30,200]`）；`GetData`/`GetMapNpcNames`（names 含
`misc, IsFreshManServer, DATA_POS, has_key, values / …, GetRealName,
npcname2realnamedata`；常量 `-1, 1054, 1055, 0`）；`DelShenHeNpc`（`hero, IsShenHe,
IsNeedDelShenHeNpc, append`）。结论与报告一致：**字面表本身无版本分支、无运行时
初始化依赖；变异全部发生在消费者侧**（插入 戰隊使者、freshman 服 1054→1055 改写、
神合过滤、台版重绑定）。

---

## 4. 仍是候选（静态复现，未获原生加载器确认）

不因 PR #16 已合并而升级。以下保持 `candidate` 标签，证据 JSON / CSV / provenance 均
携带同一句声明：

- 全部修复边界：1301 `[1616,3239,4884,6553]`、1799 `[528,1093,1652,2202]`、2601
  `[18827,37735,56546,75376]`、2804 `[26695,53365,79989,106619]`、4897 槽2 `79961`。
- 2601 与 2804 的数据内容（430+434 场景、1335+1344 记录）及其字段语义（仅
  f0/f2/f4/f8/f11 有跨表或代码佐证；f3 取值域 {0,1,2} 但含义未定）。
- 4897 与 2804 的互证环路（2804 槽2 由 4897 定、4897 自身槽0 `26677/26678` 未定）。
- 400 虽以保存边界通过全部判据，其“57 行均为源值”的分级仍沿用报告的
  `confirmed_source_value`；消费者路径未证实（见 §5）。

---

## 5. 尚未复现 / 保持 unresolved

| # | 事项 | 本轮状态 |
|---|------|----------|
| 1 | **400 第二列（`related_id`）含义** | 数字复现（17 行 related≠key：`1061…1072→2302`、`1073→1041`、`1074→1042`、`1075→1047`、`1301→2121`、`1303→2122`；43 行为目录内 id，其中 40 行名称一致），**含义未建立**；暂存 CSV 将其标为 `related_id_unresolved`，禁止作连接键 |
| 2 | **400 vs 1301 尺寸语义** | 复现 0 全同 / 38 轴互换 / 19 不同值（清单一致）；两套尺寸分栏携带，不选赢家 |
| 3 | **坐标系** | 1301 `(w,h)`、400 `(size_a,size_b)`、NPC `[x,y]`、WENZI `jumpPos` 为四套框架；比例探针 median `w/max_x ≈ 25.8`、p10≈22（50 个可比场景，口径见勘误 E5）——无单一换算因子，不做任何缩放/截断 |
| 4 | **零 ID / 重复 / 跨场景同 ID** | 复现并保留：`npcid==0` 632（2601）/631（2804）；多重对 12/11 以 list 保留；跨场景同 npcid 是常态（2601：336 个 npcid 中 106 个出现于多场景；2804：343/107）→ **npcid 单独不是全局键**，`(scene, npcid)` 才是 |
| 5 | **运行时数据变更** | `GetData`（1054→1055）、`GetMapNpcNames`（同上）、`InitTestData`（索引 33 处插入 5025 戰隊使者）、`DelShenHeNpc`（条件过滤）、1870 `Fix()`（运行时重绑定）**都会改变消费者所见数据**；静态 names/consts 证据已复现；暂存 CSV 是**变异前**状态，变换只作消费者行为文档，不烘焙 |
| 6 | **1870 Fix() 绑定语义** | 框架未修（槽0 两解均干净），`X.DelShenHeNpc = Y` 不得引用为事实 |
| 7 | **400 模块消费者路径** | 字节级扫描未见任何条目引用 `sceneid2name`（仅 400 自身）；不能断言死/活，维持 unresolved |
| 8 | **`藥店` 单点失配与 1799 非穷尽** | 复现：19 个 alias 在 NPC 表中无 field0 使用（2804 侧 18）、22 条记录 field11 非空但 alias 不在 1799；按原判携带不“修” |
| 9 | **报告 §7 精确消费者清单 / §8.3 全库 447/398 统计** | 未逐条重做（方向性佐证见 §3）；全库严格校验属解码器所有者范围。另记录：按仓内 payload 公式，45 个条目解压/取钥失败（与“walk 失败 13 个”口径不同，仅作线索） |
| 10 | **原生客户端运行时验证** | 约束之外，未做也不应在本工具链内补做 |

不把几张表拼成“完整地图-NPC 配置”；`npc_2601_vs_2804_agreement.csv` 以“关系表”
方式存在（每对一行、双侧重数、三态 agreement），不产生合并视图。

---

## 6. 勘误（对 AGENT_E.md 的修正；原报告其余结论见 §3/§4/§5）

**E1 — 记录序比较语义（影响 §4、§8、§9.1 item 2、§9.2、§9.3 item 3）。**
报告称 “2601 ∩ 2804 = 664 pairs with **656 identical record-lists**” 并据此建议
“a join must compare *lists*”。复现显示 656 是**顺序无关（multiset）**比较的结果；做
**顺序敏感**比较时只有 **647** 对完全一致，多出 **9 对内容全同但记录顺序不同**：
`(1084,4840)`、`(1085,4840)`、`(1086,4840)`、`(1087,4840)`（均为 6 条 接引人 记录的重
排）与 `(2202,4425)`、`(9050,4425)`、`(9052,4425)`、`(9199,4425)`、`(9444,4425)`
（4 条 集結人 记录的重排）。报告未报告这 9 对，也未声明“identical”的比较语义。
修正：证据与暂存 CSV 用三态区分 `identical_sequence`（647）/
`identical_multiset_different_order`（9）/`content_difference`（8）；连接建议改为“按
multiset 比较、并把顺序差异单列携带”。顺序差异的业务含义未确定，保持 unresolved。

**E2 — 1799 佐证计数口径（§3、§7(d)）。**
报告 “of the **71 records whose field 11 is set**, 70 agree” 中，71 是“字段 11 非空
**且** field0 命中 1799 alias”的记录数，不是字段 11 非空总数——2601 实为 **93** 条非
空（2804：**96**），其中 22 条 alias 不在 1799 表内（与 §9.3 item 5 的 22 自洽）。数字
本身全部复现一致，但表述易误读，特此固定口径（证据
`alias_table_vs_npcposdata.records_with_real_name_set` = 93）。

**E3 — 1301 “stranded consts” 统计口径（§1 表格）。**
报告列 `[0,1,2,3,4,115,253]`（solver）与 `[0,1,2,3,4,253]`（候选），把嵌套代码对象与
`None` 常量也计入。本工具口径为“模块代码中从未被任何 LOAD_CONST 引用”：候选下
**0 个**、solver 投放下恰 **1 个**（`const[115] = 1071`）。核心事实一致（投放使 1071
脱离字面量流），口径以本工具为准并在证据 `stranded_consts` 中给出。

**E4 — 2601 保存边界失败位置的两种数字（§4）。**
报告同段给出 “fails criterion 1 at payload **18821**” 与 “saved 18821 fails at **18799**”。
本工具 criterion-1 的失败点为 code offset **18799**（`unmapped custom opcode 0xf7`）。
同一现象的不同坐标（payload 绝对偏移 vs 指令解码进程），记录以免后人按“两处失
败”误读。

**E5 — 坐标比例的小数（§7(c)）。**
报告 `median h/max(y) ≈ 27.3`、`max coordinate 332 for a 10000-wide scene`。本工具按
“记录有合法 [x,y] 且场景在 1301 目录内”的口径得到 `median w/max(x) = 25.8` ✓、
p10 = 22.0 ✓，但 h 向中位数为 29.0（50 个可比场景）；另有 69 条 2601 记录不含
[x,y]，全表最大坐标出现在不在目录内的场景 9500（(441,193)）。方向性结论（无单一
比例）复现一致；精确小数按本工具口径为准并保留为 lead 级。**不因此修正报告原
文**，仅在证据 `semantics_recheck.coordinate_scale_probe` 固化本工具口径。

**E6 — 全库解压（§8.3 相关的补充观察）。**
按仓内 payload 公式+XOR（保存边界）扫描全部 5002 条：45 条解压失败（清单在证据
`consumer_name_reference_scan.decode_failures`）。该集合与报告 “13 条 marshal walk 失
败 / 4989 可遍历” 口径不同（解压 vs 遍历），合并解读前应逐条核对，暂列线索。

未发现其它与已复现证据冲突的报告结论；§6 各条均以本仓证据 JSON 为准。

---

## 7. 可进入待审 CSV 的字段（白名单）与禁项

暂存 CSV 已按此白名单落地（`staging/`，编码 UTF-8，文本为客户端自有 cp950 内容渲
染，无繁简转换；每表行序按键排序，重生成可逐字节复现）：

| CSV | 可入列 | 依据 |
|-----|--------|------|
| `mapdata_scene_dictionary.csv` | `scene_id, name, w, h` | 104 整键、三字段齐；字段名有 `GetSceneName/GetSceneSize` 代码佐证 |
| `mapdata_parent_scene.csv` | `scene_id, parent_scene_id` | 有 `GetParentMap`/`MAP_ASCRIPTION` 代码佐证 |
| `sceneid2name_minimap_scenes.csv` | `scene_id, name, related_id_unresolved, size_a, size_b` | 键名中性化；后三列语义未立，分栏携带 |
| `npcname2realnamedata_alias_to_realname.csv` | `alias, real_name` | 55 行，NPC 表 field0/field11 70/71、73/74 佐证 |
| `npcposdata_records.csv` | `scene_id, record_index` + 14 字段 | 仅 `display_name(f0)`, `npcid(f2)`, `x,y(f4)`, `shape(f8)`, `real_name(f11)` 有佐证；`f5/f6/f9/f10/f12/f13` 中性列名；`field7_const255`；零 ID 与重复记录保留 |
| `minimapnpcpos_pos_records.csv` | 同上 + `scene_display_name` | 嵌套内层键为场景显示名，注意与 1301/400 名字有 8 处不同，**禁止按名字 join** |
| `minimapnpcpos_wenzi_entries.csv` | `scene_id, x, y, name, desc, jump_x, jump_y, npcID, npcName, servergrade` | 列名即源数据自带键名；4532 对 `servergrade` 键名的佐证为报告结论，本轮未重复其修复 |
| `npc_2601_vs_2804_agreement.csv` | `scene_id, npcid, records_2601, records_2804, agreement` | 关系表非合并表；三态 agreement |

禁项（与原报告一致并重申）：不入 4897/1870/4532/4516；不入任何 `GetData`/
`InitTestData`/`DelShenHeNpc`/`Fix` 作用后的视图；不入合并“完整地图-NPC 表”；`藥店`
失配、8 对内容差异、9 对顺序差异保持可见不“修”；不把 `related_id_unresolved` 重命
名为 scene id；不在任一坐标框架间换算。

---

## 8. 协作边界与移交事项

- **公共解码器/密钥库**：未改动。按原报告 §9.3 item 10 的解码器修复（公共读取器实
  现 `LOAD_NAME 'None'`、将修复边界写回 key DB、停用 span-solver 对 1301 的覆盖、复
  跑 400 的 cross-check、447/398 线索核查）属于 Agent A 的工作面；本工具中的最小
  证据为：`WrongParameterRejectionTests` 五项错框否决用例 + 证据 `verifications` 矩
  阵。修复写回与否由协调者决定，本工具保持参数外部注入、不依赖 key DB 被改。
- **4897 槽0 / 1870 槽0** 的未鉴别放置仍然开放；若 A 侧工具能区分，可仅以新参数集
  注入本工具复跑，无需改工具。
- **新 PR 目标分支**由协调者确认；本交付全部位于 `server/` 内，未触碰原客户端或
  FLS 文件。

---

## 9. 本轮验证的运行记录

```
python3 server/tools/map_npc_reproduction.py --check
  -> archive/keydb sha256 均匹配；16 个参数集中 6 个候选/已验证集 PASS，
     其余错框在各自预期环节 FAIL；CHECK OK
python3 -m unittest discover -s server/tests/architecture
  -> Ran 70 tests（31 原有 + 39 新增），OK
```
