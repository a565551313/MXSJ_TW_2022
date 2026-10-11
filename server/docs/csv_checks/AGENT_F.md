# Agent F — 称谓 / 坐骑提示 / 家具数据 抽取正确性核查

**范围**：`data/script.fls` 中三个零基 FLS 条目索引 **2566 / titledata.py**、**1919 / ridedata.py**、**244 / newfurnituredata.py**。
**性质**：只读证据收集。本报告不改写公共解码器、历史密钥库或 `server/game_data/`；不执行任何恢复出来的客户端脚本；不剪坏字节、不猜文案、不做繁简转换。

## 0. 输入与复现

| 项 | 值 |
|---|---|
| 档案 | `data/script.fls` |
| 档案 SHA-256 | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| 载荷解压 | `size=((a*entry_id+0xDF25E)&0xFFFFFFFF)^b`，`pos=((b*index*0xF718FE+0xD59D16C)&0xFFFFFFFF)^c`，`<IIII` 位于 `index_offset+16*index`，`index_offset = <I` 位于文件偏移 8 |
| XOR 方案 | 5 段单字节 XOR；`XTABS`（256 项）见 `tools/decompiler/batch_decompile.py:300`；`encrypt_5seg_xor` 见 `tools/decompiler/pack_and_encrypt.py:1127`（`pts=[0]+bounds+[n]`，恒为 5 段） |
| 载入配方 | `Py25MarshalTranspiler(dec, exp, keys, bounds)` → `MarshalReader(bytes(tr.out)[8:]).read()`，要求 `r.pos == len(r.data)` |

复现命令（本报告全部数字均可用下列命令与自带脚本重跑）：

```bash
cd /home/user/MXSJ_TW_2022
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/probe67_recap_2566_1919.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/probe65_final.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/probe66_cocode_stats.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/survey_csv_readiness.py          # 回归，通过
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -v   # 31 项通过
```

脚本与原始输出在 `server/tools/csv_checks_agent_f/`（`probe*.py` + `probe*.out`）。

---

## 1. 条目 2566 / `titledata.py`

| 项 | 值 |
|---|---|
| 条目索引 | 2566 |
| 实际文件名 | `script\data\titledata.py`（marshal `co_filename`） |
| 表 / 字段 | `DATA[336][0]`、`DATA[877][0]`（称谓说明文本） |
| 模块形状 | `names == (GetData, DATA)`，`DATA` = 812 行，marshal 恰好吃满 150106 字节 |
| 载荷长度 / SHA-256 | 150106 / `252688822a12fe814555a9800401746155b581a55d1c47007884fc0780fac026` |
| 已存 bounds / keys | `[30130, 60297, 90430, 120649]` / `[196, 147, 166, 249, 248]` |
| 候选 bounds / keys | `[30130, 60263, 90409, 120551]` / keys 不变 |

### 1.1 异常字节与 XOR 边界的关系

对已存分段做全模块字符串审计（`probe67`）：2356 个字符串中 5 个不过严格 CP950，其中 3 个是真实文本，且**每一个都正好终止在一条已存 bounds 上**：

| 解码载荷偏移 | 长度 | 结束于 | 已存 bound | 已存 keys 下首个坏字节 |
|---|---|---|---|---|
| 60209 | 88 | 60297 | B1 = 60297 | 串内偏移 54 |
| 90361 | 69 | 90430 | B2 = 90430 | 串内偏移 48 |
| 120524 | 125 | 120649 | B3 = 120649 | 串内偏移 52 |

即：三条已存 bounds 分别把自己的字符串从中间劈开，后半段用了下一段的 XOR key，于是后半段整体错码。另 2 个失败（偏移 7566 长 6、偏移 148480 长 1626）是 `co_lnotab` 之类的控制字节表，不是文本。

目标记录定位：

- `DATA[336][0]` → 解码载荷偏移 **21401**，长 69，落在段 0（key 196）。
- `DATA[877][0]` → 解码载荷偏移 **48566**，长 125，落在段 1（key 147）。
- `consts[1236]`（即 `DATA[877][0]` 的源常量）→ 载荷 `[60209, 60297)`，被已存 B1 = 60297 恰好截断。

### 1.2 当前值与候选

**当前值（已存 bounds）**：严格 CP950 解码失败（`UnicodeDecodeError`），读取器无法产出可用文本。

**候选（bounds `[30130, 60263, 90409, 120551]`）**：

- `DATA[336][0]` → `夢想真人秀活動的專屬稱謂，有一雙會說話的大眼睛美女。#r【有效期】2個月`
- `DATA[877][0]` → `熟知各地商會，精於商業貿易，奔跑各地為幫派賺取豐厚商業利潤的人所能獲得的稱號。#r#r獲取條件：#r完成幫派商業投資任務次數≧800。`
  - 备选：B3 = 120552 时末句为 `商業貿易　奔跑`（全角空格）而非 `商業貿易，奔跑`；**120551 为语义完整值，120552 仅作记录，不采用**。

富文本标记 `#r` 在两处均原样保留。

### 1.3 依据与测试

- **独立证据（同行行）**：859 / 876 / 877 三行共用同一 125 字节说明，仅 `≧250` / `≧500` / `≧800` 不同；336 行的说明在形式上与 335 / 337 一致。跨模块扫描（全部 5002 条目 × 5 个 CP950 针串）确认这些文本只出现在 2566，故同行一致性是唯一可用的独立证据。
- **全模块字符串审计**：候选 bounds 下 2356 个字符串只剩 2 个 `lnotab` 类控制字节表失败，**真实文本 0 失败**。
- **反例（可解码但值错）**：B2 = 90403 / 90407 / 90408 同样 0 个 CP950 失败，但分别损坏一个字符或产生 key 漂移乱码。因此"零解码失败"不是充分条件，必须逐字读全文。
- **未排除解释**：无原生算法/原生读取器对照；候选值仍属"读取器修复后的重解码结果"，不是客户端原生行为的直接证明。

### 1.4 状态

`confirmed_extraction_bug` —— 已存 bounds 截断字符串常量，客户端源数据本身未证明异常。

---

## 2. 条目 1919 / `ridedata.py`

| 项 | 值 |
|---|---|
| 条目索引 | 1919 |
| 实际文件名 | `script\data\ridedata.py` |
| 表 / 字段 | `CHANGESHAPE_PREVIEWDATA[24]`、`[34]`（坐骑造型切换提示）；`PREVIEWDATA[24]`/`[34]` 与二者共用同一说明常量 |
| 模块形状 | 13 个 name、114 个 const；`DATA`(33)、`PREVIEWDATA`(28)、`CHANGESHAPE_PREVIEWDATA`(28) |
| 载荷长度 / SHA-256 | 9066 / `5091db2c8f410c7652a89abdd284ab9efddde05c85afa499d71e35e95452a61a` |
| 已存 bounds / keys | `[1907, 3840, 5925, 7698]` / `[89, 39, 126, 150, 135]` |
| 候选 bounds / keys | `[1907, 3840, 5756, 7613]` / keys 不变 |

### 2.1 异常字节与 XOR 边界的关系

| 记录 | 解码载荷偏移 | 长度 | 结束于 | 已存 bound | 已存 keys 下首个坏字节 |
|---|---|---|---|---|---|
| `CHANGESHAPE_PREVIEWDATA[24]` | 5745 | 180 | 5925 | B2 = 5925 | 串内偏移 11 |
| `CHANGESHAPE_PREVIEWDATA[34]` | 7567 | 131 | 7698 | B3 = 7698 | 串内偏移 92 |

同样模式：两条已存 bounds 把自己的字符串截断。旧坏值即 `consts[102]`（长 180，位于 `[5745, 5925)`）与 `consts[108]`（长 131，位于 `[7567, 7698)`）。

### 2.2 当前值与候选

**当前值（已存 bounds）**：严格 CP950 失败。

**候选（bounds `[1907, 3840, 5756, 7613]`）**：

- `CHANGESHAPE_PREVIEWDATA[24]` → `購買條件：#r1、人物等級≧90級#r2、擁有高級/特殊高級坐騎#r3、消耗#Y25000#n世界貢獻度#r#r特別說明：#r1、首次成功兌換雙人坐騎後可以額外獲得5點人物屬性潛力點#r2、雙人坐騎暫無小精靈模式`
- `CHANGESHAPE_PREVIEWDATA[34]` → `購買新坐騎：#r   消耗#Y3000#n世界貢獻度#r特別說明：#r1、幸運豬無法通過隨機兌換以及切換造型獲得#r2、幸運豬無法切換為其他初級坐騎造型`

`#Y` / `#n` / `#r` 富文本标记原样保留。

### 2.3 依据与测试

- **全模块字符串审计**：已存 bounds 下 115 个字符串 13 个失败（11 个 `lnotab`/控制字节表 + 2 个真实文本）；候选 bounds 下 11 个失败，**全部**是 `lnotab`/控制字节表，真实文本 0 失败。
- **反例（可解码但值错）**：边界 3 在 7567–7659 区间内多个取值同样 0 个 CP950 失败，但会损坏一个字符或造成 key 漂移；5745 / 5747 / 5748 / 5749 / 5751 / 5753 / 5754 / 5755 亦全部通过严格 CP950 却各有字符损坏。仅 5756 与 7613 在全窗口扫描下唯一给出语义完整文本。
- **未排除解释**：无原生读取器对照；`PREVIEWDATA` 与 `CHANGESHAPE_PREVIEWDATA` 复用同一说明常量这一事实来自 marshal 常量去重行为，属于结构观察而非独立数据源。

### 2.4 状态

`confirmed_extraction_bug` —— 已存 bounds 截断字符串常量。

---

## 3. 条目 244 / `newfurnituredata.py`（重点）

| 项 | 值 |
|---|---|
| 条目索引 | 244 |
| 实际文件名 | `script\data\newfurnituredata.py` |
| 目标表 | 模块级 `DATA`（家具主数据） |
| 载荷长度 | 91087（marshal 恰好吃满） |
| 已存 bounds / keys | `[18282, 34193, 54797, 73070]` / `[233, 132, 132, 105, 246]` |
| 旧候选 bounds / keys | `[18282, 36511, 54797, 73114]` / `[233, 11, 132, 105, 246]` |
| 当前 no-solver 局部候选 | B0=`18289` **或** `18290`，其余 bounds / keys 同旧候选；两者都通过当前结构与 DATA 检查，但互不等价 |

**结论先行**：`TYPE2NAME` / `ORDER` 等辅助字面量可读，**不代表**家具主表已原生确认。no-solver 复核在 `[22,47423)` 结构推导的模块 `co_code` 内统计，旧 B0=18282 仍有 2 个未映射 opcode，不能沿用 solver 参与的旧 DATA 输出。窄范围扫描留下 B0=18289 / 18290 两个候选；二者各自仅能由局部 allowlist 完整提取 233 条目标 DATA 赋值（非公共 whole-module strict 读取），但 `DATA[29251].pre` 分别为 CP950 文本和整数 `153`。没有证据选择其一，**数据边界仍未解决**。

### 3.1 主数据实际变量、赋值位置与初始化方式

用 no-solver 原始解密结果经 `SpanTrackingMarshalReader` 从 TYPE_CODE/字符串对象结构推导，模块根 `co_code` 位于载荷 `[22, 47423)`、长度 47401；不是硬编码扫描窗。全 marshal 共 25 个 code object，其余 code object 均在 `[47957, 54415)` 且不跨过根 `co_code` 范围。模块级共 64 个 `STORE_NAME`，其中数据表类赋值位置（根 `co_code` 字节偏移）：

| 变量 | `co_code` 偏移 | 形状 |
|---|---|---|
| `SITE` | 2001 | dict，6 条 |
| `LAYER` | 2115 | dict，4 条 |
| `ORDER` | 2820 | list，233 条 |
| **`DATA`** | **46863** | **dict，233 条（家具主表）** |
| `SPE_HORSE_DATA` | 47394 | dict，35 条 |

其余 34 个早期 `STORE_NAME`（偏移 3–201）是 `FUR_TYPE_*` / `FUR_SHOWTYPE_*` / `SIT_*` 常量，684–876 是 26 个函数定义。`TYPE2NAME`(459)、`DIDRANGE`(675) 为辅助字典。

**初始化方式**（`DATA` 的赋值指令序列，起始于 `co_code` 2823）：

```
BUILD_MAP 0                 # DATA = {}
  DUP_TOP
  BUILD_MAP 0               # 内层记录 dict
  DUP_TOP
  ... 20 组 (值; ROT_TWO; 键; STORE_SUBSCR) ...
  ROT_TWO; LOAD_CONST <家具id>; STORE_SUBSCR     # DATA[<id>] = 记录
  DUP_TOP; BUILD_MAP 0; DUP_TOP ...              # 下一条记录
```

每条记录 20 个字段：`ani, base_cost, beauty, beauty_limit, bg_type, cost, desc, direct, grade, layer, lianxuplace, lv, name, pagename, pre, special, stablepath, subtype, type, zoff`。233 条记录，id 从 25798 到 29999（`ORDER` 亦为 233 条，与之对应）。

### 3.2 解码边界与 opcode 统计（均限结构推导的 `co_code`）

**(a) saved 与旧候选的 code-only 统计**

`probe65_final.py` / `probe66_cocode_stats.py` 对每组原始 key/bound 解密后，先用 marshal 结构解析根 code object，再仅扫描其 `co_code` `[22,47423)`。saved 参数为 **22743 条 Duoyi 指令、2361 个未映射 opcode**。旧候选 B0=18282、B1=36511、B2=54797、B3=73114 / keys `[233,11,132,105,246]` 为 25961 条、**2 个未映射**（payload 绝对偏移 18282、18288）。这些数不含常量池，不是数据损坏结论。

**(b) no-solver 的窄范围 B0 复核**

固定候选 B1/B2/B3 和 keys，只在 `[18280,18298)` 小窗逐一改变 B0；对每个设置重做 raw decrypt、marshal 结构解析、code-only opcode 统计、no-solver 转译，并尝试局部 allowlist 读取 DATA 赋值片段。B0=18289 与 18290 都有 25963 条指令、0 个未映射 opcode，且目标片段完整提取 233 条 DATA 成功；B0=18291 虽也有 0 个未映射 opcode，但在常量索引 `18266` 处失败，故不能入选。旧 B0=18282 有 2 个未映射 opcode，当前探针在 DATA 解析前即拒绝；旧整模块读取器遇到 NOP 回退的失步说明仅作历史限制记录。

这两个保留候选都不是原生确认：边界分别落在同一条三字节指令的参数字节 1/2，且 DATA 结果不同——`DATA[29251].pre` 在 B0=18289 为 46 字节 CP950 文本，在 B0=18290 为整数 `153`。当前证据不足以选择，不能把任一读法升格为唯一结果。

**(c) 目标 DATA 赋值的局部安全读取范围**

完整公共读取器在家具模块的其他位置遇到 `LOAD_NAME b'None'` 与带默认值的 `MAKE_FUNCTION`；本次没有扩大公共读取器的语法或改动 `script_literal_reader.py`。该文件哈希被 `batch_001/manifest.json` 记录，修改它会使现有批次检查失效；本收口遵守不改 batch_001 的范围。新的 probe65 只从前一个模块级 name-store 之后，到 `STORE_NAME DATA` 为止，读取目标赋值片段；局部 allowlist 仅接受字面量构造指令及精确名称 `LOAD_NAME b'None'`，不执行恢复代码，任何其他指令/名称都会拒绝。`MAKE_FUNCTION` 位于目标赋值片段之外，不作解释。B0=18289/18290 目标 DATA 赋值均完整提取为 233 行、233 次外层写入；目标字典及其嵌套字典均无重复键写入；`assignment_complete=true`、`module_verified=false`。这是有明确边界的赋值片段证据，不是整模块严格验证，更不是 native-loader 验证。

**(d) NOP 回退不缩短缓冲区，但可能令指令遍历失步**

`transpile_py25_code()` 以 `bytearray(co)` 原位替换未知 Duoyi opcode 为标准 NOP(9)，所以输出 `co_code` 长度不变；它仍按 Duoyi 3 字节跨距前进，残留的两个操作数字节不会删除。标准遍历器把 NOP 当 1 字节后，可能把残留操作数误当指令，出现失步或伪 `EXTENDED_ARG`。旧 B0=18282 no-solver 变体正有此风险；不得把旧工具的遍历症状或 5249/7598 等越界计数当作 `co_code` 长度缩短或文件损坏证据。

**(e) B3 候选：`DATA[29760].desc`（非原生确认）**

`DATA[29760]`（`關山白`）的说明串位于解码载荷 `[73070, 73189)`，长 119。saved B3=73070 下 CP950 失败；B3=73114 的候选读法为「白葉黃花，朦朦朧朧之間透漏著難得一見的淡雅清新意蘊…」，与同行家具说明结构一致。73000–73300 扫描记录在 `probe64_b3_scan.out`，但可读性/同行一致性不是原生加载器证明，仍按候选处理。

### 3.3 重新生成的 no-solver DATA 與常量池结果（`probe65_final.out`）

`probe65_final.py` 对每个候选显式调用 `Archive.transpile(..., use_solver=False)`；raw opcode 统计直接来自同一参数集的 `Archive.decode()` 输出。B0=18289 与 B0=18290 均从前一个 name-store 之后到 `STORE_NAME DATA` 为止，使用局部 allowlist 完整读取目标赋值片段：233 条记录、233 次外层写入，目标及嵌套字典均无重复键写入。整模块 public reader 没有参与，也没有被修改；因此 `assignment_complete=true` 只表示该片段完整，不表示全模块或原生加载行为已验证。

| 范围 | 复核结果 |
|---|---|
| `DATA` 结构 | 233 条；每条恰为预期 20 个字段 |
| `DATA` 所有 bytes 字段值 | B0=18289：543 个（`name` 233、`desc` 164、`layer` 140、`pre` 1、`stablepath` 5）；B0=18290：542 个（除 `pre` 的 bytes 值外其余相同） |
| `DATA` CP950 / 控制字符检查 | 两个候选均为 0 失败、0 控制字符 |
| 所有 code object 的 `co_consts` bytes（独立审计） | 25 个 code object、539 个 bytes 常量出现次数；按字节值多重集与 DATA 对照，403 次可匹配 DATA 字段值，另 136 次为额外常量值；两类均 0 CP950/控制字符问题 |

“匹配/额外常量”仅按 bytes 值多重集区分，不宣称常量来源归属；`co_code` 与 `co_lnotab` 均不属于 `co_consts`，更不算作 DATA 文本。报告特意把目标 DATA 文本审计和其他常量池值审计分开，不能把后者失败（若有）记成家具 DATA 损坏。

两个候选唯一可见的 DATA 差异：

```
DATA[29251].pre: B0=18289 -> bytes / CP950 text
                  B0=18290 -> integer 153
```

这项歧义尚无独立边界证据裁决；不得自动挑选其中一个作为唯一数据结果。旧版 solver-enabled `probe65_final.out` 的整表结果已被本版取代。


### 3.4 反例与证据边界

| 设置 / 指标 | 表面结果 | 限制或相反证据 |
|---|---|---|
| B0=18289 与 B0=18290 | 都是 0 个未映射 opcode、都能完整提取 233 条目标 DATA 赋值 | `DATA[29251].pre` 不同；不能仅按 opcode 计数择一；这不是整模块严格验证 |
| B0=18291 | 也是 0 个未映射 opcode | 局部 DATA 赋值读取在常量索引 `18266` 失败；再次说明 0 未映射不是充分条件 |
| 旧 B0=18282 | marshal 结构仍可解析，计数为 2 个未映射 | transpiler NOP 回退导致读取器拒绝；solver 参与的旧输出不可冒充 no-solver 结果 |
| B3=73113 / 73115 / 73116 | 可严格 CP950 解码 | 分别出现错字、ASCII 杂质或乱码；CP950 成功不是值正确证明 |
| saved 配置 | marshal 完整消费，部分辅助常量可读 | 根 `co_code` 在推导范围内仍有 2361 个未映射 opcode，不能据辅助表可读证明 DATA 正确 |

旧探针中 `key1=73/198` 等 `0x42` 孪生键样例保留作排除案例；它们说明单看未映射 opcode 计数不够。新的 B0 结果采用“结构解析范围 + code-only 统计 + no-solver 局部 DATA 字面量赋值解析 + DATA 字段审计”交叉呈现；未扫描为全模块 strict，也不等同于原生加载器验证。

### 3.5 状态

| 子项 | 状态 |
|---|---|
| 主表变量/赋值位置/初始化方式 | 在两个 no-solver 候选结构下均可严格重建 233 条 DATA；属于 marshal/literal 证据 |
| saved / 旧 B0=18282 的遍历症状 | 未映射 opcode 被 NOP 回退后可能失步；不表示 co_code 被缩短，也不是 native data 损坏证明 |
| #17 DATA 读取范围 | probe65 仅对目标赋值片段使用 allowlist（含精确 `LOAD_NAME b'None'`）；共享公共读取器与其 whole-module strict 契约保持不变 |
| `DATA[29760].desc` | B3=73114 是可读候选（CP950 与邻行一致），未获 native-loader 确认 |
| 家具主表整体 | 两个 no-solver B0 候选在 `DATA[29251].pre` 上冲突；保留歧义，未取得原生算法/独立读取器对照 |

---

## 4. 三项共用的排除过程（如何排除"源数据本身异常"）

对每一处异常字节都做了同一组排除，之后才判定为提取缺陷：

1. **不是编码解释问题**：所有候选读法一律用严格 CP950（`bytes.decode('cp950')`）判定；对 244 的 `DATA[29760].desc` 另外试过 `big5`、`gbk`、`gb18030`、`utf-8`、`utf-16-le/be`、`shift_jis`、`euc_jp`、`euc_kr`、`latin-1`，无一给出可读中文（`probe56_encodings.out`）。
2. **不是单键猜错**：对 244 的异常串穷举 256 个单字节 key；对 2566 / 1919 的异常串做 ±120 / ±200 边界全扫描并打印全文逐字比对。
3. **不是段内换键**：对 244 的异常串穷举"段内split × 双键"组合（`probe58`），只有 B3 = 73114 一种解释与 5 段模型自洽。
4. **结构验证有明确范围**：2566/1919 的候选 marshal walk 消费完整载荷；244 使用 raw no-solver payload、结构推导根 `co_code` 范围及局部 allowlist 读取 DATA 赋值片段（不是 whole-module strict reader）。三者检查范围不同，不能把一种统计外推到另一种。
5. **旁证不等于唯一性**：2566/1919 有同行/邻行结构相似；244 的相邻家具说明可作文本旁证，但 B0=18289/18290 仍在 `DATA[29251].pre` 分歧，且没有 native-loader/独立读取器对照。

---

## 5. 能否进入待审 CSV / 必须隔离什么

### 5.1 可进入待审 CSV（附条件）

| 条目 | 记录 | 条件 |
|---|---|---|
| 2566 | `DATA[336][0]`、`DATA[877][0]` | 以 `bounds=[30130, 60263, 90409, 120551]` 重解码后入待审；`#r` 标记必须保留；`DATA[877][0]` 采用 120551 版本（`商業貿易，奔跑`），120552 版本（全角空格）不入库 |
| 1919 | `CHANGESHAPE_PREVIEWDATA[24]`、`[34]`（及共用同常量的 `PREVIEWDATA[24]`、`[34]`） | 以 `bounds=[1907, 3840, 5756, 7613]` 重解码后入待审；`#Y`/`#n`/`#r` 原样保留 |
| 244 | `DATA` 全部 233 条的名称/说明 | B0=18289 与 18290 两个 no-solver 候选的名称/说明字节一致，可作为**带双候选标记**的审阅材料；不得据此批准 `pre` 等其他字段或称为原生确认 |

### 5.2 必须隔离、不得进入正式 `server/game_data/`

1. **244 的非名称/说明字段**：不得转换为服务器权威规则或制作公式。特别是 `DATA[29251].pre` 在两个通过 no-solver 检查的候选下分别是 CP950 文本与整数 `153`，必须维持歧义；不得只因中文可读就认定它是字段语义。其他价格、等级、层级和材料等值也只能作为客户端候选信息审阅。
2. **244 的 `desc` 中出现的 `#Y…#n` 数值片段**（如 `消耗#Y25000#n世界貢獻度`，见 1919 条目；244 的说明中亦有同类结构）：同上，只能作为富文本原样保留。
3. **未取得原生算法/独立读取器对照**：三个条目的候选值全部来自"修正分段后的重解码"，没有任何一条经过客户端原生 `PyMarshal_ReadObjectFromString` 或第二个独立实现交叉验证。因此上述三项都只能进**待审**，不能直接进正式数据。
4. **不宣称"全部修复"**：本报告只覆盖分配到的三个条目与其中的 `DATA[336]`/`DATA[877]`、`CHANGESHAPE_PREVIEWDATA[24]`/`[34]`、244 的 `DATA` 主表。`server/docs/catalog/csv_readiness_survey.json` 中 2566 的旧十六进制样本与当前读取器输出不一致（survey 长 88/156，读取器长 69/125，偏移亦不同），引用 survey 前必须重新派生。
5. **不跨表统一名称差异**：2566 的称谓行、1919 的坐骑提示、244 的家具名之间不做任何名称归一。

---

## 6. 提交给 Agent A 的字节/边界证据（公共解码器与密钥库由 Agent A 负责，本报告只提交证据）

| 条目 | 已存 | 候选 | 判据 |
|---|---|---|---|
| 2566 | bounds `[30130, 60297, 90430, 120649]` | bounds `[30130, 60263, 90409, 120551]`，keys 不变 | 三条文本串分别终止于 60297 / 90430 / 120649；候选下真实文本 CP950 失败数 5 → 0 |
| 1919 | bounds `[1907, 3840, 5925, 7698]` | bounds `[1907, 3840, 5756, 7613]`，keys 不变 | 两条文本串分别终止于 5925 / 7698；候选下真实文本 CP950 失败数 2 → 0 |
| 244 | saved bounds/keys 如表 3；旧候选 B0=18282、B1=36511、B2=54797、B3=73114 / keys `[233, 11, 132, 105, 246]` | no-solver 局部候选 B0=18289 **或** 18290，其余不变；B3=73114 仅为可读候选 | 结构解析推导根 `co_code` `[22,47423)`；saved=2361 未映射、旧 B0=18282=2、两个保留 B0 候选=0；两者局部 DATA 赋值读取为 233 条但 `DATA[29251].pre` 冲突。native 未确认 |

probe65 的 DATA 局部读取器只在目标赋值片段内允许精确 `LOAD_NAME b'None'`；其它名称加载拒绝。完整公共 strict literal reader 的 `LOAD_NAME` / `MAKE_FUNCTION` 语法范围未更改。`transpile_py25_code` 的 NOP fallback 另需注意：它保留输出长度但会留下操作数字节，可能导致标准走查失步；该实现没有在本次改写。

---

## 7. 遗留问题

1. 三个条目均无原生算法/独立读取器对照；候选边界与候选键不是"已证唯一解"。2566 / 1919 的若干近邻边界均能严格 CP950 解码；244 的 no-solver B0=18289/18290 均通过当前结构检查却在 `DATA[29251].pre` 不同，须保留未决状态。
2. 244 的 `DATA` 记录字段中 `ani` / `stablepath` / `pagename` / `special` 等大量为 `None` 或短整数，其业务含义未核对（只作文本留档）。
3. 244 的模块级函数（`GetFurniturePath`、`GetSiteTable` 等 26 个）未做语义核查；它们可能包含对 `DATA` 的运行时加工，因此"字面量层面的 `DATA`"与"客户端运行时实际看到的 `DATA`"可能存在差异——这是把结果限定在"待审"而非"已确认"的主要原因。
4. 2566 的 `consts[1236]` / `DATA[877][0]` 与 859 / 876 行的 `≧250` / `≧500` 差异只在本模块内自洽，无跨模块独立来源。
