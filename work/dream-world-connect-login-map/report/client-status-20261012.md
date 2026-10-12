# 客户端现状权威报告（2026-10-12）

**角色**：客户端总指挥
**方法**：不采信任何既有文档结论。本文每一条都来自本轮实际执行的命令、反汇编或字节码。
**范围**：客户端逆向与客户端侧测试工具。服务端（`server/`）由另一条线负责，本文只在涉及协议真值时提及。
**取代**：`INDEX.md` / `QUICK_START.md` / `HANDOVER-20261010.md` 中与本文冲突的部分一律以本文为准。

---

## 0. 一分钟结论

1. **协议号表已经拿到权威版本**，不再需要引用任何手抄数值。来源是客户端自己：`data/script.fls` 条目 **3970** = `script\protocol.py`，412 条赋值、409 个整型常量（C2GS=176，GS2C=233），**2476 字节 `co_code` 上 0 个未映射 opcode**。产物：`artifacts/protocol_table/protocol_opcodes.{csv,json}`。
2. **链路帧的 `MaxLenBytes` 是 2，不是 3**。全二进制扫描对 `CNetClient+0x6990` 只有一次写入，在 `mx.exe:0x4AB23F`，`imm32 = 2`。
3. **`mock_server.py` 有 5 处被客户端证据证伪的实现**，本轮已全部修正，修正后自测仍全绿。其中最严重的是 0xFF 转义写成 3 字节长度——它只影响包体 ≥ 0xFF 的报文，而 `GS2C_PROP_INIT`（包体 404 字节）正好是唯一命中者，也就是**进图后的第一个包**。
4. **`mock_server.py --self-test` 过去验证的是 `data/data.fls` 的机器人分支，不是 v2.27.2 真实客户端报文**。已改为发送真实布局，现在日志显示 `script.fls v=0.2.27`。"verified 100%" 这句话此前的含金量需要打折。
5. **仓库里至今没有一个真实客户端字节**。`notes/protocol-artifacts/stream-0001..0022.bin` 与 `tools/captures/capture-*.bin` 全部 0 字节（本轮 `stat` 确认）。所有协议结论仍是静态证据。
6. **一批客户端工具已经过期**，它们建立在被推翻的 `IMProtocol.dll` 帧模型上（详见 §5）。

---

## 1. 协议号表：权威来源与复现

```bash
cd work/dream-world-connect-login-map
python3 tools/extract_protocol_table.py --cross-check-mock ../../mock_server.py
```

本轮实测输出：

```
client file      : script\protocol.py
module docstring : GBK '协议号'
co_names=413 co_consts=241 co_code=2476B
assignments      : 412  (int=409, non-int=3)
unmapped opcodes : 0
direction split  : C2GS=176  GS2C=233
  GS2C_HELLO = 1          C2GS_ANSWERHELLO = 62
  C2GS_LOGIN_ACCOUNT_ENTER = 1   GS2C_LOGIN_ACCOUNT_INFO = 15
  GS2C_LOGIN_PLAYER_INFO = 3     C2GS_HEART_BEAT = 63
  GS2C_HEART_BEAT = 63           C2GS_SELECT_SERVER = 41
  GS2C_SELSERVER = 47            GS2C_PROP_INIT = 16
  GS2C_MAP_SCENE_M = 96
```

原理：该模块是纯常量模块，`co_code` 2476 字节 = 412 ×（`LOAD_CONST` 3B + `STORE_NAME` 3B），因此可以线性遍历指令流、按 `HAVE_ARGUMENT = 0x5F` 切分，把 `LOAD_CONST n` 与紧随的 `STORE_NAME x` 配对。**不执行任何还原出的游戏代码**，只解 marshal 与字节码。

### 1.1 表的结构性事实（本轮新得，之前无人记录）

| 事实 | 数值 | 影响 |
|---|---|---|
| 取值范围 | 1 .. 242 | 命令字是**单字节**，不可能超过 255；`GS2C_*` 与 `C2GS_*` 是两个独立命名空间，同号不冲突 |
| 未使用的值 | **17, 28, 46, 197** | 发这些号的包客户端根本没有处理函数 |
| C2GS 内部重号 | 152 = `C2GS_PLAYER_UPGRADE` + `C2GS_CHECKWG` | 客户端 `m_NetFunction` 是字典，后注册者覆盖前者 → 两者之一不可达 |
| GS2C 内部重号 | 9 = `GS2C_LOGIN_LOCALPW` + `GS2C_LOGIN_CARDPW`；**152 = `GS2C_PROP_CHANGE` + `GS2C_NPC_CHAT_EXT`** | 同上。152 这组直接影响我们：mock 用 `GS2C_NPC_CHAT_EXT=152` 做 NPC 对话 |
| 被禁用的命令 | `C2GS_PLAYER_EXTRA_INFO = None`、`GS2C_PLAYER_EXTRA_INFO = None` | 这两个在 v2.27.2 里是空值，不是数字，别指望能发 |

`GS2C_PROP_CHANGE` 与 `GS2C_NPC_CHAT_EXT` 同为 152 是**客户端自身的冲突**，不是我们的错误。但必须真机确认客户端最终注册的是哪一个，否则 NPC 对话或属性变更会静默失效。

### 1.2 `mock_server.py` 与客户端表的差异（本轮交叉检查结果）

65 个常量中 49 个一致，16 个不一致。已修 2 个硬错误，其余 14 个 `*_LEGACY` 是本项目自造的兼容名，保留但已标注：

| 常量 | 原值 | 客户端真值 | 处置 |
|---|---|---|---|
| `GS2C_MAP_DEL` | 100 | **85**（100 是 `GS2C_MAP_ADD_GOODS`） | 已改 |
| `GS2C_PROP_CHANGE` | 17 | **152**（17 在客户端不存在） | 已改，并标注与 NPC_CHAT_EXT 重号 |
| `GS2C_LOGIN_PLAYER_INFO_END` | 14 | 14 是 `GS2C_BLACKLIST`，该命令不存在 | 已标注（未使用） |
| `C2GS_LOGIN_QUIT=4`、`C2GS_LOGIN_PLAYER_DEL=7`、`C2GS_PROP_NEWPOINT=17` | — | 客户端表中不存在 | 已标注 |
| 12 个 `*_LEGACY` | — | 客户端表中不存在 | 保留兼容，已标注 |

注意 `C2GS_LOGIN_PLAYER_DEL = 7` 是虚构的：客户端只有 **S2C** 方向的 `GS2C_LOGIN_PLAYER_DEL = 10`。删角请求走的是别的路径（`C2GS_ACCOUNT_MANAGE = 5` 是候选，**未验证**）。

---

## 2. 链路帧格式：`MaxLenBytes = 2`（已判定，终结长期分歧）

三份笔记写"默认 2"，`mock_server.py` 却按 3 字节写。本轮用 objdump 直接判定。

`CNetClient::RecvPacket`（`mx.exe:0x4AB540`）的状态机，实测反汇编：

```asm
4ab56a: cmpl  $0x0,0x698c(%ebx)      ; state == 0 ?
4ab580: push  $0x1                   ;   ReadBytes(&+0x6988, 1)   <- 读 1 字节长度
4ab58f: movl  $0x1,0x698c(%ebx)      ;   state = 1
4ab599: cmpl  $0x1,0x698c(%ebx)
4ab5a2: cmpl  $0xff,0x6988(%ebx)     ; L == 0xFF ?
4ab5b5: push  0x6990(%ebx)           ;   ReadBytes(&+0x6988, MaxLenBytes)
4ab5bd: call  0x4ab460
4ab5ca: movl  $0x2,0x698c(%ebx)      ;   state = 2
4ab5d4: mov   0x6988(%ebx),%eax      ; length
```

`+0x6990` 就是 `MaxLenBytes`。全二进制扫描对它的写入**只有一处**：

```
file 0x0AA63F  VA 0x4AB23F  c7 87 90 69 00 00 02 00 00 00   mov dword ptr [edi+0x6990], 2
```

**结论：续读长度是 2 字节小端。** 写 3 字节会多出一个 `0x00`，客户端把它当作包体首字节 → `cmd = 0x00` → 流错位。

实测影响面（用 `mock_server` 自己的构造函数量的）：

| 包 | 包体 | 成帧方式 |
|---|---:|---|
| GS2C_HELLO | 8 | 1 字节长度 |
| GS2C_LOGIN_ACCOUNT_INFO | 7 | 1 字节长度 |
| GS2C_LOGIN_PLAYER_INFO | 38 | 1 字节长度 |
| **GS2C_PROP_INIT** | **404** | **0xFF 转义 ← 唯一命中者** |
| GS2C_MAP_SCENE_M | 20 | 1 字节长度 |
| GS2C_MAP_ADD_NPC | 50 | 1 字节长度 |

因为长度值 < 65536，多写的第 3 个字节总是 `0x00`，2 字节读出来的长度值仍然正确——所以问题不是长度算错，而是**包体整体前移一字节**。这类 bug 在自测里完全看不出来（自测过去也按 3 字节读）。

---

## 3. 登录报文：从字节码直接读出的字段宽度

`data/script.fls` 条目 **4082** = `script\login\netlogin.py`，71 个代码对象。`C2SLoginIn` 实测反汇编：

```
167  LOAD_FAST   3 (netobj)
170  LOAD_ATTR  11 (PacketAddS)
173  LOAD_FAST   0 (name)
176  LOAD_CONST  8 (32)        <- 账号定长 32
179  CALL_FUNCTION 2
183  LOAD_FAST   3 (netobj)
186  LOAD_ATTR  11 (PacketAddS)
189  LOAD_FAST   1 (pwd)
192  LOAD_CONST  9 (20)        <- 密码定长 20
195  CALL_FUNCTION 2
```

`GS2C_LOGIN_ACCOUNT_INFO` 的 `_vid2ver` 实测：

```
 76  BUILD_MAP / 77 LOAD_CONST 2 / 81 LOAD_CONST 1 / 84 STORE_SUBSCR   -> {1: 2}
 85  BUILD_MAP / 86 LOAD_CONST 1 / 90 LOAD_CONST 2 / 93 STORE_SUBSCR   -> {2: 1}
 94  BUILD_MAP / 95 LOAD_CONST 0 / 99 LOAD_CONST 3 /102 STORE_SUBSCR   -> {3: 0}
112  LOAD_FAST 2 (vid) / 115 BINARY_SUBSCR      <- 在 try 之外
134  POP_BLOCK / 135 JUMP_FORWARD -> 150        <- try 只包住那句 print
```

因此：

- **`vid` 只能是 1/2/3**。查表在 `try` 之外，发 4/5/99 会抛 `KeyError` 冒出函数，**不会**走到 `except` 打印 `game version error`。
- `mock_server` 里"1..5 valid；99 触发『數據已經轉移』"这句话**不成立**：`數據已經轉移` 的 CP950 与 GBK 字节串在条目 4082 里都不存在（本轮实测）。这是凭空写的。
- 账号在包体内偏移 5..36、密码 37..56，**连续 52 字节固定位置明文**——这仍然是拿密钥流最现实的抓手。

---

## 4. 本轮对 `mock_server.py` 的修改（全部有证据，自测复验通过）

| # | 位置 | 改动 | 证据 |
|---|---|---|---|
| 1 | `frame_gs2c()` | 0xFF 转义 3 字节 → **2 字节**；新增 `MAX_LEN_BYTES`、超长时抛错而不是静默截断 | `mx.exe:0x4AB23F` / `0x4AB540` |
| 2 | `recv_gs2c()`（自测内） | 同步改为读 2 字节 | 同上 |
| 3 | 自测 login 包 | 40B 账号 + 32B 密码 → **32B + 20B** 真实布局（87 字节 fields），并加断言锁定分支 | 条目 4082 `co_code` 176/192 |
| 4 | `GS2C_MAP_DEL` | 100 → **85** | 条目 3970 |
| 5 | `GS2C_PROP_CHANGE` | 17 → **152**，附重号警告 | 条目 3970 |
| 6 | 文件头 docstring | 删掉"Authentic opcodes"、"97 个 ITEM_SERVERINIT"等不实说法；改为写清权威来源与复现命令；`*_LEGACY` 标注为非客户端事实 | §1、§5 |
| 7 | 常量区注释 | 标注 3 个虚构常量 | §1.2 |

验证（本轮实际执行）：

```
$ python3 mock_server.py --self-test
[LOGIN] C2GS_LOGIN_ACCOUNT_ENTER (op=1, script.fls v=0.2.27): account='testuser01', pwd='e10adc3949ba59abbe56'
[PASS] All stages (...) verified 100%
EXIT=0
```

改动前后对比：改动前日志是 `sub=0`（legacy 分支），改动后是 `script.fls v=0.2.27`（真实分支）。**这是本轮最重要的一处测试有效性修复**——之前"100% 通过"覆盖的不是目标客户端。

`GS2C_PROP_INIT` 断言同步更新为 `0xFF + 2B len(404) + op(16)`，总长 407；并新增成帧回归断言，检查转义后紧跟的字节必须是命令字而不是 `0x00`。

---

## 5. 过期/失效清单（客户端侧）

### 5.1 建立在被推翻模型上的工具 —— 不要再用它们分析真实报文

游戏通道走 `mx.exe` 原生 `C_net`（`CNetClient`/`CServerCommand`），**不经过 `IMProtocol.dll`**（这解释了 Frida observer 的 0 次 IMP 命中）。以下工具仍按 `IMProtocol` 模型写：

| 文件 | 问题 |
|---|---|
| `notes/protocol-artifacts/im_crypto.py` | `build_frame`/`parse_frame` 用 `>H`（大端 2 字节总长 + 2 字节命令字）。加解密往返自检**通过**，但帧模型是错的 |
| `tools/packet_analyzer.py` | `extract_frames` 用 `struct.unpack("!H", buffer[:2])` 切帧 → 与真实 `[1B len][body]` 完全不符 |
| `tools/enhanced_capture_server.py` | 依赖上面两者做"自动解密" |

保留作历史，但**任何新抓包分析都不要从这里起步**。

### 5.2 被取代的文件

- `tools/mock_server.py`（552 行，md5 `6e20d333…`）已被**仓库根目录**的 `mock_server.py`（2081 行，md5 `daca1591…`）取代。`QUICK_START.md` 仍指向旧路径，**已过期**。

### 5.3 文档中不成立的客户端结论

| 说法 | 出处 | 实际 |
|---|---|---|
| `vid` 1..5 有效，99 触发"數據已經轉移" | `mock_server.py` docstring | `vid` 只能 1/2/3；该字符串不存在于条目 4082 |
| "all 97 `ITEM_SERVERINIT` hero attributes" | `mock_server.py` 头部 | 与同文件另一处"112"自相矛盾。实测 `hero.py`（条目 3038）模块级 `ITEM_ALL` 与 `ITEM_SERVERINIT` 都是 `BUILD_TUPLE 0`——**空元组，运行时由 `InitItem` 填充**。两个数字都不是客户端静态字面量 |
| C2GS 命令字 0x0001/0x0002/0x0003/0x0010/0x00FF | `notes/protocol-commands-values.md`、`QUICK_START.md` | 命令字是单字节（1..242），不存在 0x0010/0x00FF 这种值。WI-013 应以本文 §1 结项 |
| 帧格式 `uint16_be 总长 + uint16_be 命令字` | 多处 | 已被 `[1B len][body]` 取代 |
| `loginhello` 明文包 34 字节 | `HANDOVER`、`protocol-commands-values.md` | 文件不存在，数值无来源 |
| `script\protocol.py` 有 412 条 | `hello-path-20261011.md` | ✅ 本轮独立复现确认 |
| `MaxLenBytes` 默认 2 | `hello-path`、`login-path` | ✅ 本轮以二进制证据确认 |

### 5.4 工具行为提醒（本轮实测）

| 工具 | 状态 |
|---|---|
| `tools/fls_batch_decoder.py` | ✅ 可用。参数是 `--archive/--index/--output`（不是旧文档的 `--entry/--input/--output-dir`）。耗时：3970 → 2.6s，4082 → 9.0s，3038 → 28.0s |
| `tools/pydis26.py` | ✅ 可用。用法 `pydis26.py <marshal.bin> <func-name>`，**不支持 `--help`**（会被当文件名报错） |
| `tools/extract_protocol_table.py` | ✅ 本轮新增 |
| `hello_server.py` / `login_server.py` / `packet_analyzer.py` / `enhanced_capture_server.py` / `map_parser.py` | ✅ `--help` 均正常 |
| `pydis26.s()` 解码顺序 | ⚠️ 先试 `big5hkscs`，会把 GBK 串显示成乱码（`协议号` → `衪祜瘍`）。条目 3970 的字符串是 **GBK**，而道具/宠物表是 CP950——**同一归档内编码混用**，读字符串时必须两条都试 |
| `objdump` | ✅ 可直接反汇编 `mx.exe`（`pei-i386`，ImageBase 0x400000）。节：`.text` 0x401000、`_dyprot0` 0x947000、`_dyprot1` 0xC5E000。加壳节里的代码静态读不到 |

---

## 6. 客户端侧任务分派

### P0 — 打通 HELLO（唯一的关键路径）

静态证据链已闭合，缺的只是 Windows 上一次真实运行。**没有这一步，后面所有协议工作都停在纸面。**

- 工具：`tools/hello_server.py`（仅绑 127.0.0.1）
- 期望：客户端选区 → 收到 `GS2C_HELLO`（`08 01 <seed:u32LE> <srvnum:u16LE> <cert:u8>`）→ 回 25 字节 `C2GS_ANSWERHELLO`(cmd=62) → 跳账号页
- 必须记录：`Get-NetTCPConnection` 状态、`hello_server` 完整日志、客户端 `log/game/`+`log/pylog`、截图、操作顺序
- 对照组：`--no-hello` 只收不发，用于确认"服务端先发"这一假设

### P1 — 拿密钥流（走已知明文，不要碰加壳代码）

`C2SLoginIn` 的账号+密码是包体偏移 5..56 的**连续 52 字节固定位置明文**。用我们自己控制的账号密码，对 `C2GS_ANSWERHELLO` 之后的首个密文包做已知明文攻击，比 hook `IMP_RefreshCryptKey` 现实得多——而且 `IMP_RefreshCryptKey` 根本不是游戏通道的密钥来源（见 §5.1）。

### P2 — 判定 GS2C 152 重号的胜者

真机上分别只发 `GS2C_PROP_CHANGE=152` 和 `GS2C_NPC_CHAT_EXT=152`，看客户端响应哪一个。这个结论服务端也要用，属于跨线共享事实。

### P3 — 补齐 `NakedSend` 的 seed 派生

`0x27` opcode 仍未定（XOR/AND/OR 三选一）。判据：`seed = ((4294967296 - seed) % 3227993 + 2562088) OP 6636321`，`6636321 = 0x653F21`。P0 拿到真实 25 字节回复后即可反解。

### P4 — 清理客户端侧过期资产

- `packet_analyzer.py` / `enhanced_capture_server.py` / `im_crypto.py` 顶部加"帧模型已过期"横幅，或移到 `tools/legacy/`
- `tools/mock_server.py`（552 行旧版）标注被取代
- `QUICK_START.md` / `INDEX.md` 的路径与命令字表更新为本文

### 明确不做

- 不猜值、不补齐缺失字段、不删除任何原始客户端文件
- 不在拿到真机证据前，新增任何"已确认"级别的协议结论
- 不执行还原出来的游戏脚本（`eval`/`exec` 一律禁止）

---

## 7. 本轮产物

| 路径 | 说明 |
|---|---|
| `tools/extract_protocol_table.py` | 新增。从条目 3970 提取权威协议号表，可交叉核对任意 Python 文件里的硬编码常量 |
| `artifacts/protocol_table/protocol_opcodes.csv` | 409 条：name, value, direction, code_offset, load_const_enc, store_enc |
| `artifacts/protocol_table/protocol_opcodes.json` | 含来源 SHA、方法说明、非整型赋值、重号表 |
| `report/client-status-20261012.md` | 本文 |
| `../../mock_server.py` | 7 处修正（见 §4） |
