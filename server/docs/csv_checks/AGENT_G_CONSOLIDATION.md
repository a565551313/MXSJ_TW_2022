# Agent G — PR #13 / #14 / #15 / #17 统一收口交接

- **日期：** 2026-10-11（UTC）
- **工作分支：** `arena/0df6c016-mxsj-tw-2022`
- **PR base：** `arena/b53b33e6-mxsj-tw-2022`
**目的：** 统一修正文档、探查输出与回归测试；不合并、不关闭原 PR，不改写正式游戏数据。

> 本文把观测事实、候选解码和未经证实的解释分开。strict marshal/literal 读取、CP950 成功、代码可走查、文字通顺、未知 opcode 数为零，都不能单独证明客户端原生加载结果。

## 1. 各原 PR 的处理清单

| 原 PR | 接收并保留 | 本收口所做修改 | 暂缓／未确认 |
|---|---|---|---|
| **#13 — Agent B 道具/装备/工艺探查** | 保留已核实表格证据、边界候选与原始字节定位；保留 72548 的完整非法 CP950 字节串与隔离状态。 | `AGENT_B.md` 更正基线说明：GitHub 上 `2d403c2` 是真实提交（完整 SHA `2d403c2362feb2481d394c6dc6dead39876832ab`），GitHub compare 还确认它是协调基线 `ff6555d6ad56fc804a9f2cad251b0fb396081e22` 的祖先（基线领先 10 个提交）；本次实际集成基线仍记为协调分支 tip。探查工具增加显式候选 bounds；机器 JSON 记录 1945/41052 的 `778764→778759`、候选「時空石」、1182/4924 同字节证据和 `native_loader_confirmed=false`。 | `778759→時空石` 仍是有交叉证据的候选，不是原生加载器确认；72548 的末字节 `0x84` 不得裁剪或猜名。其它候选仍待独立/原生验证。未据此改正式数据。 |
| **#14 — Agent D 技能/BUFF 读取** | 保留 `3205` 的真实 `DATA` 证据：590 次写入、581 个唯一 ID、9 次覆盖及全部旧/新值；保留其他关注表的 strict-reader 实测与覆盖信息。 | `AGENT_D.md` 改为使用 `Archive.transpile(..., use_solver=False)` 和现有公共 `extract_table_report`，默认 strict；3205 断言落在真正 `DATA` 而不是常量池或旁表。纠正 NOP 说明：转译器原位写入等长缓冲区，不会缩短；残留操作数字节可能令标准遍历失步。 | 719、4406 等仍隔离；显式 partial 结果仍标为未验证；不把解析成功、CP950 或模板相似当作客户端行为证明。候选密钥/边界未写入历史密钥库。 |
| **#15 — Agent C 宠物/怪物/资质表** | 保留 saved `2954/DATA[2800]` 的 `法力資質=2130`、最大值 `1989`，保留原始字节与边界差异证据；保留所有名字匹配、表间关系及来源字节。 | `AGENT_C.md` 将 2130/1989 明确列为 saved-parameter 事实；`7979` 得到 1700 仅为候选，`1700*117//100==1989` 只是算术旁证，不证明公式。将 3010/4021/4022 标为资质表缺项、原因未证实，禁止补零。`AGENT_D.md` 同步取消按名称自动取首个技能 ID。 | `2954/DATA[2800]` 整行继续隔离，不改成 1700、不交换、不补零；宠物同名技能保留 `高級命中: 229/255`、`終級命中: 329/355`，`match_count=2, ambiguous=true`，不得自动选 ID。 |
| **#17 — Agent F 家具/称谓/坐骑提示表** | 保留家具 DATA 20 字段架构、233 条记录、`DATA[29760].desc` 候选及旧探针作为探索历史。 | 重写 `probe65_final.py` / `probe66_cocode_stats.py`：从原始解密 marshal 结构推导根 `co_code` 区间，统计不扫描常量池；所有转译显式 `use_solver=False`。probe65 仅用局部 allowlist 读取前一 name-store 到 `STORE_NAME DATA` 的目标赋值片段（其中仅接受精确 `LOAD_NAME b'None'`）；公共 whole-module reader 未修改，避免改变 batch_001 中记录的工具哈希。新输出将 DATA 字段文本与非 DATA `co_consts` 分开审计。 | B0=18289 与 18290 都通过当前 no-solver 结构检查，但 `DATA[29251].pre` 分别为 CP950 文本与整数 153；不自动择一。无 native-loader 或独立读取器对照，家具结果仍为候选。旧 5249/7598 等越界计数不再作代码损坏证据。 |

原 PR #13、#14、#15、#17 均保持原状；协调收口不替代协调者后续对这些 PR 的处理。

## 2. 关键可复现结果

### #13：1945 / 41052 与 72548

- `server/docs/csv_checks/agent_b_probe.json` 现记录：保存边界 `778764` 下名称为「晉怖肋」；候选边界 `778759` 下为「時空石」，只改变键 41052；候选状态为 `cross_corroborated_candidate_not_native_verified`。
- 候选字节 `aec9aac5a5db` 在 entry 1182 payload `863430` 和 entry 4924 payload `125988` 有独立载荷命中；4924 候选表也有「時空石」。这些只提高候选可信度，不证明原生加载器输出。
- 1945 `DATA[72548][0]` 保留 decoded bytes `c2f9a448a7a4c34dc5e9c5e784`；严格 CP950 在末字节 `0x84` 失败。报告与机器输出均保留原始 payload bytes、偏移及隔离状态。
- Agent B 原报告保守行数 `6852−4=6848` 与 batch_001 候选参数下的 6851 行是不同审阅范围；本收口未改 batch_001、profile 或导出器。

### #14：3205 DATA 与 strict/partial 契约

- 当前公共读取器回归测试确认：`DATA` = 581 个最终键、590 次写入、9 次覆盖；覆盖 ID 为 `{4236,4573,4574,4575,4576,4577,4578,4579,4581}`，首个覆盖的旧/新名称分别为「天魔返生術」/「地魔返生術」。
- 报告中的复现代码对 `3205`、`454`、`3075`、`2242`、`333` 使用公共读取器 strict 默认值；违规必须拒绝，只有显式 `allow_partial=True` 才能得到且必须标为 `verified=False, partial=True` 的部分结果。
- `transpile_py25_code()` 对未知 opcode 用 NOP 覆写同长度缓冲区；剩余参数字节可能造成遍历失步，但不代表字节缓冲区缩短。

### #15：候选/事实/猜测

- `2954/DATA[2800]` saved 值 2130 / 1989 不变；`bounds[1]=7979` 得到 1700 是待审候选；没有批准写入第一批数据。
- 3010、4021、4022 在资质表缺行，保留 NULL/缺失，不合成零值。
- `pet_skill_name_matches.csv` 保留四个 ID 候选：高級命中 229、255；終級命中 329、355。名字与技能书/ICON 映射只可作为分类线索，不足以静默丢弃一个 ID。

### #17：code-only 与 DATA/常量池分离

- `probe65_final.py` 对 saved 参数及候选参数均从 raw decrypted marshal 结构推导根家具模块 `co_code=[22,47423)`、长度 47401；`co_consts` 和 `co_lnotab` 不参与 opcode 统计。saved 参数在该范围内为 2361 个未映射 opcode；旧 B0=18282 的候选为 2 个（18282、18288）。这不是文件损坏结论。
- B0 扫描范围明确为 `[18280,18298)`，不是全局穷举。B0=18289/18290 均为 25963 条指令、0 未映射 opcode；目标赋值片段读取完整（233 行、233 次外层写入，目标及嵌套字典无重复键），但 `module_verified=false`；两者只在 `DATA[29251].pre` 分歧。B0=18291 虽 0 未映射，局部 DATA 读取仍因常量索引失败，说明 opcode 数不是充分判据。
- 对 B0=18289：233 行各 20 字段；DATA 所有 bytes 字段 543 个，按字段为 `name=233, desc=164, layer=140, pre=1, stablepath=5`，CP950 失败 0、控制字符 0。
- 全部 25 个 code object 的 `co_consts` 独立审计：539 次 bytes 常量出现；按 bytes 值多重集 403 次可与 DATA 字段值匹配、136 次为额外池值，池审计问题 0。匹配仅按值，不是常量来源证明。B0=18290 对应 DATA bytes 字段 542 个（无 `pre` bytes 值）。
- 这些均为静态结构/候选证据，未执行恢复脚本，不表示原生客户端行为。

## 3. 文件与数据边界

本收口仅修改 server 侧报告、探针、架构测试和本交接文档。以下均不得修改且本轮不应出现 diff：

- `data/script.fls`、`tools/decompiler/script_fls_keys.json`、客户端文件；
- `server/game_data/` 正式数据；
- `server/docs/csv_checks/batch_001/`、`batch_001_profiles.json`、`server/tools/export_review_csv.py`。

未运行恢复客户端脚本；不使用 `eval`/`exec`；没有做简繁转换。

## 4. 验证、提交与统一 PR

最终验证（2026-10-11 UTC）：

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q`：**161 tests OK**。
- `PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check`：**通过**，22 个输出文件逐字节一致；1945/2027/2954/3205 分别为 6851/135/131/579 条 review 行，隔离 1/0/1/2 条；技能 DATA 为 590 次写入、581 唯一 ID、9 次覆盖；missing aptitude 仍为 3。
- `PYTHONDONTWRITEBYTECODE=1 python3 server/tools/agent_b_item_probe.py --out server/docs/csv_checks/agent_b_probe.json`：退出码 0；重复运行与提交 JSON **逐字节一致**。JSON 记录 1945/41052 保存边界 778764、候选边界 778759、「時空石」、1182/4924 字节交叉证据与 `native_loader_confirmed=false`；72548 保留完整非法 CP950 原字节。新测试 `test_agent_b_item_probe.py`：**3 tests OK**。
- `PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/probe65_final.py`：退出码 0；`probe65_final.out` 重生成。B0=18289/18290 均为 code-only 0 unmapped，目标赋值局部审计为 233 行/233 次外层写入/0 字典重复写入，`module_verified=false`；`DATA[29251].pre` 保留文本/153 差异。
- `PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/probe66_cocode_stats.py`：退出码 0；`probe66_cocode_stats.out` 重生成，opcode 统计范围只含结构推导的根 `co_code`。
- 新测试 `test_agent_f_furniture_probe.py`：**6 tests OK**；覆盖边界不越界、常量池伪 opcode 隔离、DATA/全常量池分开报告、局部赋值 allowlist 与候选差异保留。
- `git diff --check`：通过；`batch_001/`、profile、exporter、正式数据、原始 FLS/密钥库均无改动。

- **提交号：** 待提交。
- **统一 PR：** 待推送/创建，base 必须为 `arena/b53b33e6-mxsj-tw-2022`；原 PR #13/#14/#15/#17 不合并、不关闭。
- **尚未解决：** native-loader 对照、41052 候选原生确认、72548 客户端显示/加载行为、2954 的 2130/1700 取舍、同名宠物技能候选 ID 的原生关联、家具 B0=18289/18290 与 `DATA[29251].pre` 差异。所有未决字段继续隔离或保留候选标记。
