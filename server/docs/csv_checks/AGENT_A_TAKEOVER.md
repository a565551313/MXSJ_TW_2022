# Agent A 接替报告（第一阶段）：条目 3205 / `petskill.py` 与 PR #14 · #18 冲突核查

日期：2026-10-11。工作分支：`arena/dc130665-mxsj-tw-2022`（基线提交 `6b7f871`，来自
`arena/b53b33e6-mxsj-tw-2022`）。

本报告只做**只读复现 + 结构核查**，不修改客户端、FLS、密钥库或正式 `server/game_data/`，
不执行还原出的游戏脚本，不启动 `mock_server.py`。第一阶段的目标是先把可控的小结果钉死：
条目 3205 的参数冲突、PR #14 与 PR #18 的矛盾、以及公共读取器对“顶层赋值”和“重复字典键”的正确读法。

---

## 0. 开工前确认的 PR 状态

| PR | 责任 | 状态 | head 提交 | 基线 |
|---:|---|---|---|---|
| #13 | Agent B 道具/装备/商城 | OPEN | `1f6938f2f7b6` | `arena/b53b33e6-…` |
| #14 | Agent D 技能/Buff | OPEN | `1d8ec734baa1` | `arena/b53b33e6-…` |
| #15 | Agent C 宠物/资质/图鉴 | OPEN | `977d377f1a56` | `arena/b53b33e6-…` |
| #16 | Agent E 地图/NPC | **MERGED**（`db58fe1`） | `8b92f3ce69bd` | `master` |
| #17 | Agent F 称谓/坐骑/家具 | OPEN | `3539aeb98089` | `arena/b53b33e6-…` |
| #18 | 独立复核 | OPEN | `b75361bf5aef` | `arena/b53b33e6-…` |

本阶段没有合并、关闭或改写任何上述 PR。本分支不包含它们的文件；引用它们的内容时使用
`gh`/`git show origin/pr/N:<path>` 读取，未做 cherry-pick。

输入版本（实测）：

| 文件 | SHA-256 |
|---|---|
| `data/script.fls` | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| `tools/decompiler/script_fls_keys.json` | `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb` |

密钥库中 3205 保存值：`keys=[204,23,122,74,218]`、`bounds=[18043,36122,54130,72108]`。

---

## 1. 结论摘要

1. **条目 3205 有 `DATA` 主表**，并且它是用 `STORE_GLOBAL` 发布的（不是 `STORE_NAME`）。
   PR #18 只统计 `STORE_NAME`，因此“本条目没有模块级 `DATA` 赋值”的结论错误。
2. **PR #14 的 `keys[1]=152` 成立**，配合 `bounds=[18043,36123,54155,72143]` 可以重建
   **581 条唯一技能 ID**（590 次写入、9 次重复键覆盖）、**0 处 CP950 失败**、字段结构统一。
3. **PR #18 的 `keys[1]=218` 被否定**。它能得到“未映射操作码 = 0”的高分，但同一指标对正确
   参数也是 0，指标无区分力；用 218 解码后模块体里出现 2183 个 `BREAK_LOOP`、2009 个
   `CONTINUE_LOOP`、1284 个 `BUILD_CLASS` 等模块级字面量代码不可能出现的操作码，
   首个违规在 **18021**（正确密钥在该处是 `STORE_SUBSCR`），并且**读不出 `DATA`**。
4. **PR #14 的一处描述错误**：`transpile_py25_code()` 不会缩短字节码长度。它写入的是等长缓冲区，
   未映射操作码被就地换成 NOP、其后 2 个参数字节仍留在输出里，真正的问题是**按标准字节码遍历
   输出时会失步**，不是长度变化。
5. **PR #14 的验证脚本确实没有覆盖 581 条主表结果**（它只对 3205 的常量做了“不是字典”的断言）。
   本阶段补上真正重建 `DATA` 并检查结构与关联的回归测试。
6. 公共读取器已按“同时识别 `STORE_NAME`/`STORE_GLOBAL`、重复键必须留证据”的最小补丁修好；
   原有输出与既有测试全部保持通过（`client_data_boundary_review.json` 逐字节一致）。
7. `2242 / SKILLIDLST[16] = 416`（两个 PR 一致的候选）经独立重建确认：48 项全部能在 3205 的
   `DATA` 里命中，`DATA[416]['name'] = '水擊'`，`64605` 不存在。
   注意：PR #18 用来支持 416 的 `AUTOFIGHTLIST` 证据本身有效，但它位于第 2/3 段，
   **两种密钥下都读出同样的 37 项**，因此不能用来支持 `keys[1]=218`。

尚未取得：与原生加载器一致的证据（第 6 级）。PR #18 已核对 `PkgImport` 在 `0x457C72` 跳入
`DuoyiProtect` 运行时解密段，静态不可读；本阶段接受该阻塞事实，不再把它当作完成前置条件。

---

## 2. 复现命令与实测结果

```bash
# 1) 三方只读复现（原始参数 / PR#14 候选 / PR#18 候选）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/probe_script_entry_3205.py --write
# 2) 回归测试（含本阶段新增 13 项）
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -v
# 3) 确认公共读取器输出没有变化
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_client_data_boundaries.py > /tmp/review.json
python3 -c "import json;print(json.load(open('/tmp/review.json'))==json.load(open('server/docs/catalog/client_data_boundary_review.json')))"
```

实测：

| 命令 | 结果 |
|---|---|
| `probe_script_entry_3205.py --write` | 退出码 0，`server/docs/csv_checks/entry_3205_parameter_probe.json` 生成 |
| `unittest discover -s server/tests/architecture -v` | **44 tests OK**（原 31 项 + 本次新增 13 项），约 2.1 秒 |
| 读取器输出比对 | `True`（与 `server/docs/catalog/client_data_boundary_review.json` JSON 语义完全相同） |

---

## 3. 三种参数集为什么不同

同一份 `data/script.fls`，同一套转译器（**显式关闭** `solve_py25_co_span` 自动求解器，
避免启发式覆盖被测参数），三种参数的结果：

| 指标 | 原始保存值 | PR #14 候选 | PR #18 候选 |
|---|---|---|---|
| `keys` | `[204,23,122,74,218]` | `[204,152,122,74,218]` | `[204,218,122,74,218]` |
| `bounds` | `[18043,36122,54130,72108]` | `[18043,36123,54155,72143]` | 保存值（未动） |
| 根 `co_code` 未映射 Duoyi 操作码数 | **2433**（首个就在 18043） | **0** | **0** |
| 标准指令遍历 | **失败**：18032 `EXTENDED_ARG` 后接无参指令 | 通过，20776 条 | 通过，20776 条 |
| 模块体非法操作码数（字面量白名单） | 无法遍历 | **0** | **9843**（`BREAK_LOOP` 2183、`CONTINUE_LOOP` 2009、`LOAD_LOCALS` 2009、`BUILD_CLASS` 1284…） |
| 严格字面量/栈机首个违规 | 未执行 | 无 | **18021 `BREAK_LOOP`**（同处正确密钥为 `STORE_SUBSCR`） |
| 顶层字面量赋值 | 无 | `ICON_MAPPING`、**`DATA`**、`AUTOFIGHTLIST`、`ShieldShortCutSkills` | 仅 `ICON_MAPPING` |
| `DATA` | 读不出 | **581 条 / 590 次写入 / 9 次重复** | 读不出 |
| 文本失败 | — | 0 | — |

### 3.1 为什么 “未映射操作码 = 0” 不能作为判据

复现 PR #18 的评分函数（保存边界、第 1 段内部窗口），得到与它**完全相同**的排名：

```text
[(0, 218), (1, 152), (287, 143), (288, 130), ...]
```

但这个 `1` 是伪差异：

* 扫描窗口从 `bounds[0]+3 = 18046` 开始，而第 1 段的起点是 18043；从 18046 起遍历相当于
  **从指令中途开始**，对齐是任意的。
* 以整段 `co_code`（[22,37496)）统计，`152` 与 `218` **都是 0 个未映射操作码**。

即：该指标在这里只能说明“这段不再是乱码”，不能说明“这段是正确代码”。
`PY25_MAP` 只覆盖 111/256 个字节值，而 3205 第 1 段的真实明文主要由
`0x00`（参数高位）、`0x8F`（`LOAD_CONST`）、`0x9D`、`0x30`、`0x5A` 等少数取值组成；
换成 218 后这些字节被异或成 `0x42`、`0xCD`、`0xDF`、`0x72`、`0x18`——**恰好也都在映射表里**，
于是统计上“干净”，结构上已经全错。

### 3.2 用结构而不是文字区分

新增的严格读取器把“模块级字面量代码能出现哪些操作码”作为白名单，并对栈行为逐条校验：

* PR #14 候选：全过程 **0 违规**，栈深最大 37（来自 `BUILD_LIST 37` 的自动战斗列表），
  `LOAD_CONST`/`co_names` 下标 0 越界，模块结束时栈为空。
* PR #18 候选：**18021** 处就出现 `BREAK_LOOP (80)`——循环控制流不可能出现在模块级字面量赋值里；
  同位置在正确密钥下是 `STORE_SUBSCR (60)`。整段还有 9843 个白名单外操作码。

两个方案的判别证据都不依赖任何中文文本（文本只作旁证）。

---

## 4. 主表恢复结果与重复键证据

以 PR #14 参数重建 `petskill.py` 根代码对象：

* `co_filename = script\data\petskill.py`；`co_names` 10 项。
* 顶层赋值（按顺序）：
  `ICON_MAPPING`（**STORE_GLOBAL** @165，12 项）、`DATA`（**STORE_GLOBAL** @37341）、
  `AUTOFIGHTLIST`（STORE_NAME @37458，37 项）、`ShieldShortCutSkills`（STORE_NAME @37467，`[556]`）。
* `DATA`：**590 次字典写入 → 581 个唯一 ID**，键范围 `101..45432`，
  581 条记录的字段集合完全一致 `{name, desc, type, fpneed, mpneed, hpneed}`，
  CP950 解码失败 **0** 处。
* 关联：`AUTOFIGHTLIST ⊂ DATA`、`SKILLIDLST(48) ⊂ DATA`、`DATA[416]['name']='水擊'`、
  `64605 ∉ DATA`。

### 4.1 9 次重复键写入（位置 / 顺序 / 旧值 / 新值）

写入顺序号是 `DATA` 字典自身的写入序号（0 基），偏移是**转译后 `co_code` 的字节偏移**：

| 顺序 | 偏移 | 键 | 旧值 → 新值 |
|---:|---:|---:|---|
| 352 | 22409 | 4573 | `name='天魔返生術'` → `name='地魔返生術'`（其余字段逐字节相同） |
| 353 | 22472 | 4574 | 完全相同 |
| 354 | 22535 | 4575 | 完全相同 |
| 355 | 22598 | 4576 | 完全相同 |
| 356 | 22661 | 4577 | 完全相同 |
| 357 | 22724 | 4578 | 完全相同 |
| 358 | 22787 | 4579 | 完全相同 |
| 359 | 22850 | 4581 | 完全相同 |
| 360 | 22913 | 4236 | 完全相同 |

这 9 次覆盖是**客户端源码本身**的行为（两次连续的记录块，中间夹着 4580、4582），
运行时“后写生效”。读取器保留全部写入，最终表值取最后一次写入，因此
`DATA[4573]['name'] = '地魔返生術'`，同时 `'天魔返生術'` 的证据仍然可查。
既不能静默覆盖，也不能把重复记录删掉。

### 4.2 主表之外的附带确认

`bounds[1]=36123` 的必要性可以纯结构化地看出来：用 36122 时记录 6220（`靈通強化Ⅱ`）
的字段键变成整数 `218`、丢失 `b'name'`，破坏 581 条记录统一的字段集合；
`bounds[2]=54155` / `bounds[3]=72143` 则分别修复 `DATA[719]['desc']`、`DATA[4406]['desc']`
的字符串中段错误（这两处只有文本级证据，且 54155 存在同样可解码的邻居 54156，见候选清单）。

---

## 5. 对既有报告结论的逐条处置

| 原结论 | 处置 | 依据 |
|---|---|---|
| PR #18 §3.5：3205 **没有**模块级 `DATA` 字面量表，“上一位 Agent 试图重建 DATA 方向本身就走不通” | **推翻** | `DATA` 以 `STORE_GLOBAL` @37341 发布；改用能识别 97 的读取器即可重建 581 条 |
| PR #18 §3.5：`keys[1]` 应为 218，依据“每段未映射操作码密度” | **否定** | 该指标对 152 也是 0；218 下模块体共 9843 个非法操作码，首个 18021 `BREAK_LOOP`，读不出 `DATA` |
| PR #18 §3.5：`ICON_MAPPING` 的 `STORE_NAME` 未定位 | **修正** | `ICON_MAPPING` 同样是 `STORE_GLOBAL`（@165，12 项），已在读取器中恢复 |
| PR #18 §3.3：`SKILLIDLST[16]=416` | **确认**（与 PR #14 一致） | 重建 48 项，全集命中 3205 `DATA`，`64605` 不存在 |
| PR #18 §3.3：用 `AUTOFIGHTLIST` 含 416 支持上述结论 | **限定** | 该表位于后续段，两种密钥下读出完全相同的 37 项，不能支持 `keys[1]=218`（但对 416 的支持有效） |
| PR #18 §3.4：143 作为 `EXTENDED_ARG` 自洽 | 接受 | 与 `PY25_MAP` 一致，本阶段未改动 |
| PR #14 §3.1：`keys[1]` 真实值 152 | **确认** | 见 §3、§4 |
| PR #14 §3.1：`bounds[1..3]` 候选 | **确认**，其中 `bounds[1]` 增加结构化证据（记录 6220 字段集合） | 见 §4.2 |
| PR #14 §3.1：`transpile_py25_code()` 遇未映射操作码“只写 1 字节 NOP 却前进 3 字节，导致**输出长度缩水**” | **纠正** | 实现写入等长 `bytearray`，长度不变；真实后果是残留的 2 个参数字节被后续标准遍历当作指令，造成失步（回归测试已固定该事实） |
| PR #14 §6：附带的验证脚本覆盖了本报告结论 | **纠正/补齐** | 该脚本对 3205 只断言常量属性，从未重建 `DATA`；本次新增真正覆盖 581 条结果的测试 |
| PR #14 §3.4：`evaluate_literals()` 遇重复键抛错是“保护限制” | 保留并扩展 | 默认仍拒绝（不静默覆盖），另增可记录全部写入的路径 |
| 任务书：3205 “常量索引越界 / 异常 EXTENDED_ARG” | 澄清 | 那是保存密钥下的**工具侧后果**，不是客户端运行时报错 |

---

## 6. 公共读取器怎么改（最小补丁）

新增 `server/tools/script_literal_reader.py`（只读、只用标准库、不执行脚本）：

* **同时识别 `STORE_NAME`(90) 与 `STORE_GLOBAL`(97)** 作为顶层发布语句；
* **重复字典键记录而非丢弃**：每次写入产出 `WriteEvent(order, at, kind, key, old, new)`，
  `Assignment.overwrites` / `duplicate_keys` 给出有序证据；`duplicate_policy='error'` 保留旧的拒绝行为；
* **结构校验**：`co_consts` / `co_names` 下标边界、`STORE_SUBSCR` 目标必须是字面量字典、
  栈不下溢、模块结束栈为空、字面量操作码白名单（白名单外即报出精确偏移与操作码）；
* `scan_module()` 在**第一个**无法接受的形状处停止，之后的赋值不会被误当作可信结果。

对既有 `server/tools/review_client_data_boundaries.py` 的改动是**纯增量**：只新增
`top_level_literal_assignments()` 与 `extract_table_report()` 两个包装函数，
`evaluate_literals()` / `extract_table()` / `Review().report()` 的行为与输出完全不变
（已实测报告 JSON 与保存目录逐字节一致）。因此该补丁不会破坏 B–F 的在途工具。

---

## 7. 新增回归测试（`server/tests/architecture/test_script_entry_3205.py`，13 项）

| 测试 | 抓住什么 |
|---|---|
| `SavedParametersTest.test_saved_parameters_do_not_read_the_module` | 原始参数确实读不出（`EXTENDED_ARG`，无任何赋值） |
| `AgentDParametersTest.test_module_is_literal_and_publishes_store_global_tables` | `DATA`/`ICON_MAPPING` 是 `STORE_GLOBAL`，`AUTOFIGHTLIST`/`ShieldShortCutSkills` 是 `STORE_NAME` |
| `…test_data_table_structure` | 581 条、整型键、`101..45432`、字段集合统一、逐字段 CP950 可解 |
| `…test_duplicate_writes_are_recorded_with_position_old_new_and_order` | 590 次写入、9 个重复键、顺序号 352–360、偏移 22409…22913、4573 的名称覆盖、其余 8 条逐字节相同、最终取值 |
| `…test_cross_table_links_hold` | `AUTOFIGHTLIST(37) ⊂ DATA`、`ICON_MAPPING` 键值都在 `DATA`、`ShieldShortCutSkills=[556]` |
| `…test_entry_2242_skillidlist_links_into_the_master_table` | 2242 重建 48 项、`SKILLIDLST[16]=416`、全部命中 3205 `DATA`、`DATA[416]='水擊'` |
| `Pr18ParametersTest.test_candidate_passes_its_own_two_criteria` | **PR #18 的两条自证标准（未映射 0、标准遍历通过、20776 条）在 218 下同样成立**——指标无区分力 |
| `…test_candidate_is_rejected_structurally` | 218 下首个违规 18021 `BREAK_LOOP`、读不出 `DATA`、模块体 >1000 个非法操作码 |
| `…test_candidate_breaks_the_literal_item_that_the_correct_key_completes` | 同一段字节：152 → `…; STORE_SUBSCR`，218 → `…; BREAK_LOOP` |
| `PublicReaderSemanticsTest.test_strict_mode_still_refuses_to_silently_overwrite` | 严格模式仍拒绝重复键，记录模式保留 9 条证据 |
| `…test_transpiler_does_not_shorten_the_bytecode` | 固定“转译器不缩短长度”的事实（纠正 PR #14 的描述） |
| `InputsUnchangedTest.test_client_archive_and_key_database_unchanged` | FLS/密钥库 SHA-256 未变 |
| `…test_candidates_are_not_installed_in_the_key_database` | 候选没有写回密钥库（3205 仍是 `keys[1]=23`、原 bounds） |

测试全部读多写零：只打开 `data/script.fls`、`script_fls_keys.json`，不做任何写入。

---

## 8. 交付物

| 文件 | 说明 |
|---|---|
| `server/tools/script_literal_reader.py` | 修正后的公共读取器（STORE_GLOBAL + 重复键证据 + 结构/栈/下标校验） |
| `server/tools/probe_script_entry_3205.py` | 三方只读复现工具（`--set saved\|agent_d\|pr18\|all`，`--write`） |
| `server/docs/csv_checks/entry_3205_parameter_probe.json` | 上述工具写出的机器可读证据 |
| `server/docs/csv_checks/parameter_candidates_phase1.json` | 独立候选清单（来源 / 原值 / 候选值 / 证据 / 反证 / 置信度 / 原生一致性） |
| `server/tests/architecture/test_script_entry_3205.py` | 13 项回归测试 |
| `server/tools/review_client_data_boundaries.py` | 纯增量补丁（两个包装函数） |
| `server/docs/csv_checks/AGENT_A_TAKEOVER.md` | 本报告 |

---

## 9. 准入结论

**可以进入待审 CSV（先应用候选参数，且工具生成与人工修改分开）**

| 表 | 前提 | 备注 |
|---|---|---|
| 3205 `petskill.DATA`（581 条） | `keys[1]=152`、`bounds=[18043,36123,54155,72143]` | 字段为客户端原始字节，`type` 等尚未与任何服务端规则对齐 |
| 3205 `AUTOFIGHTLIST`(37)、`ShieldShortCutSkills`(1)、`ICON_MAPPING`(12) | 同上 | 注意：这三个表与 `keys[1]` 无关，PR #18 的 `keys[1]=218` 前提应删除 |
| 2242 `SKILLIDLST`（48 项） | `bounds[1]=264` | 仅 ID 列表，不携带名称 |

**必须隔离 / 不得直接进入正式配置**

* `DATA[4573]`：源码两次赋值的唯一语义差异记录，进 CSV 时需同时标注“源内覆盖，取后写”。
* `DATA[719]['desc']`、`DATA[4406]['desc']`：其正确性只依赖文本级证据，且 `bounds[2]` 存在
  同样可解码的邻居候选（54156），在取得独立来源前按 `candidate` 对待。
* 3205 的 `desc` 文本是客户端文案，含 `#r` 等富文本标记；不能当作服务端技能算法。

**仍需隔离/未解决**

* 与原生加载结果的一致（第 6 级）：未取得。原生 `PkgImport` 在 `0x457C72` 进入 `DuoyiProtect`
  运行时解密段，静态不可读；这仍是后续独立任务，不作为本阶段或第二阶段的完成前置。
* 密钥库其余约 4990 个条目未逐条验证；3205 的错误说明拟合误差存在，但不能推断其他条目。

---

## 10. 第二阶段（未开始，仅登记边界）

1. 汇总 B/C/D/E/F 的候选：不改原密钥库，先扩展现有独立候选清单
   （`parameter_candidates_phase1.json` 已按“来源 / 原始值 / 候选值 / 证据 / 置信度”建档，
   并区分 *存在提取错误*、*获得跨表支持*、*与原生加载一致* 三种层级）。
2. 证据不足者保留 `candidate`，不强行确认；冲突项（例如不同条目对同一记录给出不同值）
   先用跨条目逐字节比对裁决，再谈文本。
3. 原生加载器分析单列；如遇保护代码阻塞，记录阻塞点后交付已完成部分。

---

## 11. 合规声明

* 未修改 `data/script.fls`、`mx.exe`、`mxmain.dll` 或任何客户端文件（SHA-256 实测比对）。
* 未修改 `tools/decompiler/script_fls_keys.json`、`batch_decompile.py`、`fls_batch_decoder.py`；
  本次新增的读取器与工具都只读这些输入。
* 未执行任何还原出的游戏脚本，未使用 `exec`/`eval`/运行时导入；只做字节解析、反汇编与受限字面量重建。
* 未启动 `mock_server.py`；未向 `server/game_data/` 写入任何内容；未做繁简转换。
* 未删除异常记录、未剪掉坏字节、未按邻号猜技能 ID、未合并两张宠物表。
* 本报告中“确认”仅表示静态证据一致（结构自洽 + 跨条目/跨表支持），**不等于**与原生客户端逐位相同。
