# 从「账号登录页」到「进游戏」——协议梳理与当前阻塞点

日期：2026-10-11　分支：`arena/aaa3c7bf-mxsj-tw-2022`　基线：`fef1e12`
前置：`notes/hello-path-20261011.md`（选区 → 登录页，已由用户在 Windows 上验证通过）

本文只描述**已经证实**的部分；推测处一律标注 `[推测]`。

---

## 0. 结论速览

| 环节 | 状态 | 说明 |
|---|---|---|
| 选区 → 登录页 | ✅ 已通 | `tools/hello_server.py` |
| 登录包 `C2GS_ACCOUNT_ENTER` 字段 | ✅ 已解出 | 见 §3 |
| 回包 `LOGIN_ACCOUNT_INFO` / `LOGIN_PLAYER_INFO` 字段 | ✅ 已解出 | 见 §4 |
| 角色选择 / 进地图的脚本状态机 | ✅ 已解出 | 见 §5 |
| **游戏信道加解密** | ❌ **阻塞** | 算法本体在运行时解密段里，见 §2 |

**唯一阻塞项是 §2 的加解密。** 只要拿到它，登录 → 角色列表 → 选人 → 进地图
三步都只是照着 §3–§5 发包。

---

## 1. 环境说明（本次重建，避免下次重来）

`/tmp` 不会持久化。本轮工具链已改放到**会持久化的目录**：

- `/home/user/env` —— `pefile` / `capstone` / `unicorn`（`pip install --target`，不进 git）
- `/home/user/rev/lib.py` —— mx.exe 反汇编小工具（`dis(va, n)`、`sections()`、`imports()`）
- `/home/user/rev/xdis.py` —— `python3 xdis.py <hexva>[:count]`
- `/home/user/rev/rawcode.py` —— dump 脚本 code object 的**原始（S-box 混淆后）字节码**
- `/home/user/rev/all/entry<N>.marshal.bin` —— `fls_batch_decoder.py --index N` 的产物
- `/home/user/rev/d/*.dis` —— `pymarshal_dis.py <bin> --consts` 的产物

注意：脚本字节码的 opcode 经过 S-box 混淆，映射表只解出约 43 个
（`work/dream-world-connect-login-map/notes/co_code_analysis/mapping_table_v4.json`）。
反汇编结果里出现 `<U:xx>` 的地方是未解出的 opcode，读的时候要结合常量表推断。
已确认的两个：

- `0x05` = **STORE_SUBSCR**（依据：`LOAD v; LOAD x; LOAD k; 05` 出现在 `x[k] = v` 位置）
- `0x3F` / `0x09` / `0x15` / `0x23` = 1 字节的 BINARY 运算（v4 报告已列，其中 `0x23`=SUBTRACT）

---

## 2. 阻塞点：游戏信道加解密在运行时解密段里

### 2.1 加解密的入口（在明文 `.text` 中，位置确定）

`netlogin.S2CHello` 里 `net.g_Net.SetSeed(seed)` 之后，加密标志打开。相关地址
（全部在 `.text`，未混淆）：

| 用途 | 地址 |
|---|---|
| SetSeed（Python 包装） | `0x468250` |
| SetSeed 实现体 | `0x4ab360` |
| 密钥派生（纯算术，无调用，可移植） | `0x4abb20` |
| 密码器 init（thiscall，1 参数） | `0x4c54f0` |
| 密码器 process（thiscall，buf, len） | `0x4c5590` |
| 接收帧解析 | `0x4ab540`（读 1 字节长度 L；`0xFF` 时按 MaxLenBytes 续读；再读 L 字节体） |
| 接收解密 helper | `0x4ab460` |
| 发送 | `0x4ab3f0` |
| NakedSend | `0x4680a0` |
| PacketPrepare → 实现 | `0x467c70` → `0x4ac470` |

C_net 方法名字符串表在文件偏移 `0x2b3770` 附近（`PacketAddS / PacketSend /
NakedSend / GetPacketData / SetMaxLenBytes / SetSeed / SetSeed2 / UnpackInt / …`）。

### 2.2 为什么静态/离线模拟都拿不到

`0x4c54f0` 与 `0x4c5590` 都只是 thunk，函数体 `jmp` 进保护区：

```
004c54f0  push  0x6bc0b4
004c54f5  lea   ecx,[ebp-0x104]
004c54fb  push  ecx
004c54fc  call  0x5c47d4        ; sprintf 型调试输出
004c5501  add   esp,8
004c5504  lea   eax,[ebp-0x104]
004c550a  jmp   0xa3e460        ; ← 进入 _dyprot0
```

段熵（Shannon，按文件原始字节算）：

| 段 | 文件偏移 | 大小 | 熵 |
|---|---|---|---|
| `.text` | `0x001000` | `0x2aea00` | **6.636** ← 正常代码 |
| `.rdata` | `0x2b0000` | `0x12b000` | 5.990 |
| `.data` | `0x3db000` | `0x04ec00` | 5.101 |
| `_dyprot0` | `0x547000` | `0x316800` | **7.847** ← 密文/压缩 |
| `_dyprot1` | `0x85e000` | `0x1e3e00` | **7.716** ← 密文/压缩 |

`_dyprot0` 头部是纯随机字节（`e5 4f c4 d3 3a d6 1c 51 …`）；
`_dyprot1` 头部混着 `e9 9d 97 02 00` / `81 f2 c9 6a b2 34` 这类 x86 碎片，
是典型的「打包 + 运行时还原」特征。

**结论：保护区的内容只存在于运行起来的进程里。**
unicorn 离线模拟也无法进行——喂给它的是磁盘上的密文字节。

### 2.3 顺带排除的几条路

- **IMProtocol.dll 的密码不是同一套。** 已把 IMProtocol 的 ENC/DEC S-box
  （`0x10026C48` / `0x10027448`，各 2048 字节）和 8 张密钥派生 S-box
  （`0x10026448` 起 2048 字节）拿到 mx.exe 里逐字节搜，**全部未命中**。
  IMProtocol 只负责 NS/IM 信道，与游戏信道无关。
- **`mxmain_spare.dll` 不是脱壳副本。** 它 6.6 MB（主程序 9.7 MB），
  且 `.text/.rdata/.data/_dyprot0` 在文件里都没有原始数据，只有 `_dyprot1` 和
  `.rsrc` 有。不可用作替身。
- **`patch/mx.bin` 是更新器**，不是主程序（`.text` 只有 `0x5c74a`）。

### 2.4 三条可行的解法

**A. 转储运行时解密后的段（推荐）**
`tools/dump_dyprot.py`：纯标准库 + ctypes，只读 attach 到运行中的 `mx.exe`
（`PROCESS_VM_READ | PROCESS_QUERY_INFORMATION`），读出 `_dyprot0` + `_dyprot1`
（约 5.2 MB）落地为 `dyprot0.bin` / `dyprot1.bin` / `dyprot.json`。
不写目标进程、不改任何游戏文件、不联网。
拿到之后可以用 unicorn 直接调用 `0x4c54f0` / `0x4c5590` 生成任意长度密钥流，
再移植成纯 Python（或干脆把固定 seed 的密钥流固化成表）。

**B. 已知明文收割（无需 Windows 工具，已实现并离线验证通过）**
seed 由服务端指定、固定不变 ⇒ 密钥流 `K[i]` 是确定的。把客户端当密码本用：

1. `netlogin.C2SLoginIn` 把账号写成**定长 32**、密码写成**定长 20**，
   位于包体偏移 5..56（见 `notes/login-packets-20261011.md` §1），
   是我们自己敲的 ⇒ **52 字节连续已知明文，位置固定**。
   一次登录就拿到 52 字节，不用再靠 9 秒 1 字节的 PING 慢慢攒。
2. 收发两条密码流由同一 seed、同一密钥材料初始化 ⇒
   `K_send[i] == K_recv[i]`，且起始位置相同。
3. 因此**不需要知道初始 skip `n` 是多少**：先发一段垃圾包把收端偏移推进
   已知区间的起点即可（垃圾包解出来 cmd 不匹配任何表项，`net.py` 会忽略）。

`tools/login_server.py` 就是这么做的，并用 `tools/fake_client_test.py`
做了端到端离线回归（自造一条密钥流，验证「收割 52 字节 → 对齐 → 加密回包」
全链路，假客户端能正确解出 `cmd=15` / `cmd=3` / `Name='Tester'`，
收割出的 52 字节与真值 0 处不符）。

代价：**依赖 3 个假设**，第一次跑需要实测确认 ——
① 收发密码流同源同起点；② `NakedSend` 会消耗 25 字节密码流
（若不消耗，用 `--known-start 0x5`）；③ 垃圾包不会让客户端断线。
另外进地图阶段的大包（PROP_INIT / MAP_*）会超出这 52 字节，
需要多次登录累积或改用方案 A。

**C. 不解密，只做协议观测**
放弃登录进游戏，只交付「抓包 + 解帧 + 按 cmd 打标签」的观测服务器。
可以验证 §3–§5 的字段划分是否正确，但进不了游戏。

---

## 3. 客户端发出的登录包

`C2SLoginIn(name, pwd)`（`script\login\netlogin.py:29`，脚本条目 4082）：

```
commondialog.ShowMessageBox('正在登錄中....', '取消')
g_CurrAccount = name
netobj = net.g_Net
netobj.PacketPrepare(net.C2GS_LOGIN_ACCOUNT_ENTER)     # cmd = 1

iScriptV1 = CLIENT_VERSION[0]
if main.g_MiniVersion == 1:
    netobj.PacketAddI(<iScriptV1 相关表达式>, 2)        # 2 字节

netobj.PacketAddS(name, 32)                            # 账号，定长 32
netobj.PacketAddS(pwd,  20)                            # 密码，定长 20

n1, n2, n3 = C_sys.GetVersion()
netobj.PacketAddI(n1, 1)
netobj.PacketAddI(n2, 1)
netobj.PacketAddI(n3, 2)

ver = cfg.GetData('update.ini', 'Setting', 'Version')
s1, s2, s3 = ver.split('.')
netobj.PacketAddI(int(s1), ?)
netobj.PacketAddI(int(s2), ?)
netobj.PacketAddI(int(s3), ?)
# … 后续还有一段（含 192 / 168 / 254 / 4 / 4294967295 / 'g_TGID' / 'isCache' / '0'
#    等常量），尚未逐条定死宽度
```

最后 `netobj.PacketSend()`。

`PacketAddI(v, n)` 的 `n` 是**字节宽度**（1/2/4）；`PacketAddS(s, n)` 的 `n` 是
定长字节数（不足补零）。`UnpackInt(n)` 是无符号小端，`UnpackSigned(n)` 带符号。

---

## 4. 服务端回包

### 4.1 `GS2C_LOGIN_ACCOUNT_INFO` = **15**

```
g_LoginRoleInfo = []
g_LoginAccountInfo['Count']     = UnpackInt(1)   # 角色个数
g_CurrentTime                   = UnpackInt(4)
vid                             = UnpackInt(1)
selectserver.g_ServerVersion    = _vid2ver[vid]  # _vid2ver = {0:3, 1:2, 2:1}
g_LoginAccountInfo['CurCount']  = 0              # 脚本自己置 0
if g_LoginAccountInfo['Count'] == 0:
    EnterSelectRole()
```

### 4.2 `GS2C_LOGIN_PLAYER_INFO` = **3** —— 逐个角色

每个角色一条，字段顺序固定：

| 字段 | 解包 |
|---|---|
| `ID` | `UnpackInt(4)` |
| `time` | `UnpackInt(4)` |
| `Icon` | `UnpackInt(1)` |
| `Shape` | `UnpackInt(2)` |
| `Desc` | `UnpackInt(2)` |
| `Level` | `UnpackInt(1)` |
| `School` | `UnpackInt(1)` |
| `Race` | `UnpackInt(1)`（不在 0..4 则脚本强制置 0） |
| `iPrepareLoad` | `UnpackInt(1)` |
| `Point` | `UnpackSigned(4)` |
| `Name` | `UnpackString(16)` |

收满 `Count` 个 → `EnterSelectRole()`。

### 4.3 `GS2C_PLAYER_ENTER` = **4**

`netlogin.S2CLoginRoleEnter`（`netlogin.py:766`）是**空函数**，真正的处理在别的
模块（尚未定位）。`[推测]` 进地图由它驱动。

---

## 5. 脚本状态机（登录 → 角色选择 → 进地图）

`EnterSelectRole()`（`netlogin.py:651`）是通往角色界面的枢纽：

```
if dlgnationfight.g_NationFightRegister:
    commondialog.HideMessageBox(); return
loginin.OnLogin()
loginin.Show(False)
commondialog.HideMessageBox()
point2month.Show(False)
selectrole.Show(True)          # ← 角色选择界面弹出
banword.UpdateBanWord()
```

`_EnterSelectRole()`：`createrole.Show(False)` → `HideMessageBox()` →
`selectrole.Show(True)`。

`_EnterAdminRole()`：`selectrole.Show(False)` → `point2month.Show(True, g_SelectRoleIdx)`。

即**最小可用链路**：

```
[server] GS2C_HELLO (明文, cmd=1)
[client] C2GS_ANSWERHELLO (cmd=62, 加密)
[client] C2GS_ACCOUNT_ENTER (cmd=1, 加密)
[server] LOGIN_ACCOUNT_INFO (15, Count=1, 加密)
[server] LOGIN_PLAYER_INFO  (15→3, 一条角色, 加密)
   ⇒ 脚本自动 EnterSelectRole() ⇒ selectrole.Show(True)
[client] C2GS_PLAYER_ENTER (cmd=2, 选人)
[server] PLAYER_ENTER (4) / PROP_INIT (16) / MAP_*  ⇒ 进地图
```

---

## 6. 帧格式（需要再确认的部分）

接收（`0x4ab540`）：

1. 读 1 字节 `L`；若 `L == 0xFF`，再按 `MaxLenBytes`（默认 2，可用
   `SetMaxLenBytes` 改）读小端长度；
2. 读 `L` 字节体；加密开启时用 `+0xf8` 的密码器解密；
3. 加密开启时再跑解压器（vtable `[+0x2118]+4）；
4. `body[0]` 为 cmd。

发送（`0x4ab3f0`）：加密 `+0x1108`（若开启），再从 `+0x14` 的 socket 发出。

`[待确认]` 发送侧的长度前缀是否同样不加密、以及 `NakedSend` 是否绕过加密
（`0x4680a0` 走的是全局 `0x82a370`，看起来绕过了 `0x4ab3f0`，且只 push 了 4 字节
长度的参数 —— 很可能「裸发」不加密）。这一点一旦确认，B 方案的收割会好做很多。

---

## 7. 下一步

已完成的：

- `tools/login_server.py` —— 已知明文收割 + 发加密回包，离线回归通过
- `tools/fake_client_test.py` —— 上面那条的端到端离线回归
- `tools/pydis26.py` —— CPython 2.6 脚本反汇编器
- `notes/login-packets-20261011.md` —— 逐字节报文格式

待做的：

1. **在真机上跑一次** `login_server.py`，验证 §2.4 的 3 个假设：
   ```
   python login_server.py --account <你要敲的账号> --password <密码> --send-login
   ```
   看服务端日志里 `HARVEST` 有没有出 52 字节、客户端有没有弹角色界面。
   若没弹，先加 `--probe` 单独验证垃圾包会不会把客户端搞断线。
2. 若假设 ①（收发同源）不成立，就只能走方案 A（转储 `_dyprot`）。
3. 确认 §6 的两个待确认项（`NakedSend` 是否加密、`UnpackString(16)` 语义）。
4. 进地图阶段的包超出 52 字节密钥流，需要多次登录累积，或改用方案 A：
   拿到解密后的段之后用 unicorn 调 `0x4c54f0` / `0x4c5590` 直接生成任意长度
   密钥流，再与脚本侧的 `0x4abb20` 密钥派生交叉验证。
