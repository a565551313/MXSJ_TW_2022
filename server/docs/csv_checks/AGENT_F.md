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
| 候选 bounds / keys | `[18282, 36511, 54797, 73114]` / `[233, 11, 132, 105, 246]` |

**结论先行**：`TYPE2NAME` / `ORDER` 等辅助字面量可部分恢复，**不代表**家具主表已恢复。本次在主表 `DATA` 上定位到三处独立缺陷（1 个 key 错 + 2 个 bound 错），修正后 `DATA` 以 233 条记录完整重建，397 个名称/说明字符串全部通过严格 CP950。

### 3.1 主数据实际变量、赋值位置与初始化方式

模块 `co_code` 位于解码载荷 `[22, 47423)`（25 个 code object，其余 code object 全在 `[47957, 54415)` 内且不跨界）。模块级共 64 个 `STORE_NAME`，其中数据表类赋值位置（`co_code` 字节偏移）：

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

### 3.2 读取失败的确切原因（三层，互相独立）

**(a) 已存 key 1 错：132 → 11（`confirmed_extraction_bug`）**

段 1 = `[18282, 34193)`。用已存 key 132 解这段 Duoyi 字节码，6029 条指令里 **2027 条 opcode 不在 `PY25_MAP`**；改用 key 11 后同样区间 8837 条指令只有 2 条不在表内。

**(b) 已存 bound 1 错：34193 → 36511（`confirmed_extraction_bug`）**

即令把 key 1 换成 11，段 2 = `[34193, 47423)` 用已存 key 132 仍有 334 / 6892 条 opcode 不在表内；把 B1 推到 36511 后 `[36511, 47423)` 在 key 132 下 **0 / 6014** 条不在表内。合计：模块 `co_code` `[22, 47423)` 的未映射 Duoyi opcode 从已存配置的 **2361** 降到 **2**（残留 2 条位于 dec 18282 / 18288，紧邻段 0/段 1 交界）。

**(c) 读取器本身的局限（`reader_limitation`，与上面两点独立）**

`review_client_data_boundaries.evaluate_literals` 的白名单只含 `LOAD_CONST(100)`、`BUILD_TUPLE/LIST(102/103)`、`BUILD_MAP(104)`、`DUP_TOP(4)`、`ROT_TWO(2)`、`STORE_SUBSCR(60)`、`STORE_NAME(90)`。而本模块对 `None` 发出的是 **`LOAD_NAME 58`（opcode 101，`names[58] == b'None'`）**，不是 `LOAD_CONST`。因此即使字节流完全正确，评估器仍会在 `DATA` 构建段（`co_code` 2831）抛 `unsupported opcode 101`。这是评估器能力缺口，不是数据损坏。

**(d) 观测到的 `EXTENDED_ARG` 是怎么造出来的（次级机制）**

`transpile_py25_code` 对 Duoyi opcode `>= 0x5F` 保留 3 字节跨距，但未映射的 Duoyi opcode 会写成标准 NOP(9)（1 字节）。于是任何基于标准字节跨距的走查器都会失同步，并自行"制造"出一个 `EXTENDED_ARG before argument-free instruction`。已存配置下错误报在模块字节码 18307（dec 18322），前面三条指令是 `(18300, 138, 2495)`、`(18303, 9 NOP)`、`(18304, 143 EXTENDED_ARG, 2517)` —— 正是 (a) 的错误 key 触发了这条路径。修正 key/bound 后 `instructions()` 走完 25963 条指令无任何错误。

**(e) 已存 bound 3 错：73070 → 73114（`confirmed_extraction_bug`，修正 (a)(b) 后才暴露）**

`DATA[29760]`（`關山白`）的说明串位于解码载荷 `[73070, 73189)`，长 119。已存 B3 = 73070 把整条串划进段 4（key 246），结果前 44 字节乱码、严格 CP950 在串内偏移 11 失败。全模块字符串审计显示：这是整个条目**唯一**一例真实文本失败（其余失败均为 `lnotab` 控制字节表）。

对 B3 做 73000–73300 全扫描（`probe64`），**只有 73114** 给出语义完整读法：

```
73113 → ...難得一見的淡雅絀新意蘊...     （絀 为坏字）
73114 → ...難得一見的淡雅清新意蘊...     ✓ 唯一
73115 → ...淡雅清(s意蘊...               （ASCII 杂质）
73116 → ...淡雅清(鼒N蘊...               （乱码）
73070 → 严格 CP950 失败
```

### 3.3 修正后的完整结果（`probe65_final.out`）

```
candidate bounds=[18282, 36511, 54797, 73114] keys=[233, 11, 132, 105, 246]
    instructions(): 25963 instructions, no error
    DATA            -> dict len=233
    ORDER           -> list len=233
    TYPE2NAME       -> dict len=28
    SITE            -> dict len=6      （已存配置下 evaluate_literals 直接失败）
    LAYER           -> dict len=4
    DIDRANGE        -> dict len=14
    SPE_HORSE_DATA  -> dict len=35
    DATA name/desc strings: good=397 bad=0
```

`DATA[29760].desc` 完整读法：

```
白葉黃花，朦朦朧朧之間透漏著難得一見的淡雅清新意蘊#r【類型】庭院裝飾：景觀植物#r【物品等級】1#r【製作需求】70級巧匠之術
```

其邻居 29758（`珊瑚草`）、29759（`燈籠花`）、29761 的说明在句式、【類型】/【物品等級】/【製作需求】结构上完全同构，可作同行一致性旁证。

### 3.4 反例（"可解码/可走查但值错"）

| 配置 | 表面现象 | 实际结果 |
|---|---|---|
| key1 = **73**（11 的 `0x42` 孪生键，`11^73 = 0x42`） | `[18282, 36511)` 同样接近 0 条未映射 opcode | `instructions()` 在 18260 抛 `unsupported opcode 9`（NOP）→ **73 是错的，11 是对的** |
| key1 = 198（132 的 `0x42` 孪生键） | 段 2 局部窗口 0 条未映射 | marshal 走查在 47423 直接失败（tag 'j'） |
| B3 = 73113 / 73115 / 73116 | 严格 CP950 通过 | 分别坏一个字 / 混入 ASCII / 乱码 |
| B1 = 36508 | `DATA` 也能重建出 233 条 | `[36508, 47423)` 有 1 条未映射 opcode，非最优；36511 唯一给出 0 |
| 已存配置整体 | marshal 走查成功、`TYPE2NAME`/`ORDER` 可读、文件名正确 | 主表 `DATA` 完全不可用（`EXTENDED_ARG`）——**辅助表可读绝不等于主表已恢复** |

`0x42` 孪生键现象是系统性的：`PY25_MAP` 的 111 个 Duoyi opcode 中有 52 个的 `k^0x42` 也在表内，因此"未映射 opcode 计数"单独不足以定键，必须叠加 marshal 走查、常量串 CP950 合法性与语义可读性三重判据。

### 3.5 状态

| 子项 | 状态 |
|---|---|
| 主表变量/赋值位置/初始化方式 | 已确认（`DATA`，`co_code` 46863，`BUILD_MAP`+逐字段 `STORE_SUBSCR`） |
| `EXTENDED_ARG` 根因 | `confirmed_extraction_bug`（key1 132→11、B1 34193→36511）＋ `reader_limitation`（`LOAD_NAME` 不在白名单） |
| `DATA[29760].desc` | `confirmed_extraction_bug`（B3 73070→73114） |
| 家具主表整体 | 已重建，但**未取得原生算法或独立读取器对照**，因此不宣称"完整家具配置已恢复" |

---

## 4. 三项共用的排除过程（如何排除"源数据本身异常"）

对每一处异常字节都做了同一组排除，之后才判定为提取缺陷：

1. **不是编码解释问题**：所有候选读法一律用严格 CP950（`bytes.decode('cp950')`）判定；对 244 的 `DATA[29760].desc` 另外试过 `big5`、`gbk`、`gb18030`、`utf-8`、`utf-16-le/be`、`shift_jis`、`euc_jp`、`euc_kr`、`latin-1`，无一给出可读中文（`probe56_encodings.out`）。
2. **不是单键猜错**：对 244 的异常串穷举 256 个单字节 key；对 2566 / 1919 的异常串做 ±120 / ±200 边界全扫描并打印全文逐字比对。
3. **不是段内换键**：对 244 的异常串穷举"段内split × 双键"组合（`probe58`），只有 B3 = 73114 一种解释与 5 段模型自洽。
4. **不是 marshal 结构错位**：三个条目在候选配置下 marshal 走查都恰好吃满载荷（2566: 150106；1919: 9066；244: 91087），`co_filename` 正确，常量/名称数量稳定。
5. **不是孤证**：每一处修正都使该条目全模块字符串审计的真实文本失败数降为 0，且同行/邻行记录在句式与结构上同构。

---

## 5. 能否进入待审 CSV / 必须隔离什么

### 5.1 可进入待审 CSV（附条件）

| 条目 | 记录 | 条件 |
|---|---|---|
| 2566 | `DATA[336][0]`、`DATA[877][0]` | 以 `bounds=[30130, 60263, 90409, 120551]` 重解码后入待审；`#r` 标记必须保留；`DATA[877][0]` 采用 120551 版本（`商業貿易，奔跑`），120552 版本（全角空格）不入库 |
| 1919 | `CHANGESHAPE_PREVIEWDATA[24]`、`[34]`（及共用同常量的 `PREVIEWDATA[24]`、`[34]`） | 以 `bounds=[1907, 3840, 5756, 7613]` 重解码后入待审；`#Y`/`#n`/`#r` 原样保留 |
| 244 | `DATA` 全部 233 条的名称/说明 | 以 `bounds=[18282, 36511, 54797, 73114]`、`keys=[233, 11, 132, 105, 246]` 重解码后入待审；**名称/说明字段 only** |

### 5.2 必须隔离、不得进入正式 `server/game_data/`

1. **244 的 `cost` / `base_cost` / `lv` / `beauty` / `grade` / `type` / `subtype` / `layer` / `pre` 等数值字段**：这些是客户端展示与定价用的显示值。任务约束要求"价格/材料/条件只能作为客户端描述文本保存，不得转换为服务器权威规则"。因此它们只能随说明文本一起作为**客户端描述文本**留档，不得派生为服务器端的售价公式、制作条件或摆放规则。
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
| 244 | bounds `[18282, 34193, 54797, 73070]`，keys `[233, 132, 132, 105, 246]` | bounds `[18282, 36511, 54797, 73114]`，keys `[233, 11, 132, 105, 246]` | key1 132→11（2027→2 条未映射 opcode）；B1 34193→36511（334→0）；B3 73070→73114（唯一给出 `淡雅清新意蘊`）；`instructions()` 由报错变为走完 25963 条 |

同时建议 Agent A 关注两处读取器能力缺口（非本报告修改范围）：

1. `evaluate_literals` 白名单缺 `LOAD_NAME(101)`；244 这类模块用 `LOAD_NAME 'None'` 表示 `None`，导致主表即使字节正确也评估不出。
2. `transpile_py25_code` 把未映射 Duoyi opcode 写成 1 字节标准 NOP(9)，与保留的 3 字节 Duoyi 跨距不一致，会使标准走查器失同步并制造伪 `EXTENDED_ARG`；建议对未映射 opcode 保留原跨距或显式报错，而不是静默替换。

---

## 7. 遗留问题

1. 三个条目均无原生算法/独立读取器对照；候选边界与候选键是"最自洽解"，不是"已证唯一解"。2566 / 1919 的边界在全扫描中各有若干同样通过严格 CP950 的近邻值，仅靠逐字语义比对定值。
2. 244 的 `DATA` 记录字段中 `ani` / `stablepath` / `pagename` / `special` 等大量为 `None` 或短整数，其业务含义未核对（只作文本留档）。
3. 244 的模块级函数（`GetFurniturePath`、`GetSiteTable` 等 26 个）未做语义核查；它们可能包含对 `DATA` 的运行时加工，因此"字面量层面的 `DATA`"与"客户端运行时实际看到的 `DATA`"可能存在差异——这是把结果限定在"待审"而非"已确认"的主要原因。
4. 2566 的 `consts[1236]` / `DATA[877][0]` 与 859 / 876 行的 `≧250` / `≧500` 差异只在本模块内自洽，无跨模块独立来源。
