# 登录阶段报文格式（逐字节）

日期：2026-10-11　分支：`arena/aaa3c7bf-mxsj-tw-2022`
来源：script.fls 条目 **4082**（`script\login\netlogin.py`），CPython 2.6 字节码
工具：`tools/pydis26.py`（本次新增，手工校验过的 opcode 反汇编器）

本文的字段顺序和宽度是**从解出来的字节码逐条读出来的**，`C2SLoginIn` 与
`S2CLoginAccountInfo` 两个函数已 100% 解完（0 个未知 opcode）。

---

## 0. 通用约定

- `PacketAddI(v, n)`：`n` = **字节宽度**（1 / 2 / 4），小端，无符号。
- `PacketAddS(s, n)`：`n` = 定长字节数，不足补零，**不写长度前缀**。
- `UnpackInt(n)`：小端无符号，读 `n` 字节。
- `UnpackSigned(n)`：小端有符号。
- `PacketPrepare(cmd)` 会把 cmd 写进包体首字节，所以**包体 = cmd + 下列字段**。
- 链路帧：`[1 字节长度 L]` + `[L 字节包体]`；`L == 0xFF` 时按 `MaxLenBytes`
  （默认 2）续读一个小端长度。长度字节本身**不加密**，包体加密（见
  `notes/login-path-20261011.md` §2/§6）。

---

## 1. `C2GS_ACCOUNT_ENTER` = 1（客户端 → 服务端）

`C2SLoginIn(name, pwd)`。条件：`certmgr.GetIsCertLogin()` 为假时走简洁分支
（我们把 HELLO 的 cert 字节发 0 即可，这也是 `hello_server.py --cert` 的默认值）。

| 偏移（包体内，含 cmd=1） | 宽 | 字段 | 说明 |
|---:|---:|---|---|
| 0 | 1 | cmd | `1` |
| 1 | 1 | `iScriptV1` | `CLIENT_VERSION[0]`；若 `main.g_MiniVersion == 1` 则 `\| 128` |
| 2 | 1 | — | `CLIENT_VERSION[1]` |
| 3 | 2 | — | `CLIENT_VERSION[2]` |
| **5** | **32** | **`name`（账号）** | 定长 32，用户输入 |
| **37** | **20** | **`pwd`（密码）** | 定长 20，用户输入 |
| 57 | 1 | `n1` | `C_sys.GetVersion()` 返回三元组 |
| 58 | 1 | `n2` | 同上 |
| 59 | 2 | `n3` | 同上 |
| 61 | 1 | `v1` | `update.ini` `[Setting] Version` 按 `.` 拆三段后 `int()` |
| 62 | 1 | `v2` | 同上 |
| 63 | 2 | `v3` | 同上 |
| 65 | 1×4 | `localip[0..3]` | `C_sys.GetLocalIP()`；失败为 `[0,0,0,0]` |
| 69 | 4 | `adsid >> 32` | `long(main.g_Adsid)`；异常时 `adsid = 0` |
| 73 | 4 | `adsid & 0xFFFFFFFF` | 同上 |
| 77 | 1 | `len(tgId)` | `register.g_TGID`，缺省 `''` |
| 78 | *t* | `tgId` | *t* = 上一字段 |
| 78+*t* | 4 | `driveid` | `C_sys.GetDriveID()` |
| 82+*t* | *m* | `mac` | `misc.GetMAC()`，**无长度前缀**，*m* = 其长度 |

固定部分合计 **81 字节**（cmd 计入则为 82），另加 `len(tgId)` 与 `len(mac)`。

> **对已知明文收割很关键**：`name` 在包体偏移 5..36，`pwd` 在 37..56，
> 合起来是**连续 52 字节的已知明文，位置固定**。这是我们不用碰受保护代码
> 也能拿到密钥流的主要抓手。

收尾：`isCertLogin` 为假时直接 `netobj.PacketSend()`；为真时走
`netpublic.SplitPacketSend(netobj, net.C2GS_LOGIN_ACCOUNT_ENTER)`。

---

## 2. `GS2C_LOGIN_ACCOUNT_INFO` = 15（服务端 → 客户端）

| 宽 | 字段 | 说明 |
|---:|---|---|
| 1 | `Count` | → `g_LoginAccountInfo['Count']`，角色个数 |
| 4 | `g_CurrentTime` | 服务器时间 |
| 1 | `vid` | → `selectserver.g_ServerVersion = _vid2ver[vid]` |

`_vid2ver = {1: 2, 2: 1, 3: 0}`（`vid` 取别的值会 `KeyError`，所以**只能发 1/2/3**）。

脚本随后：
```
g_LoginAccountInfo['CurCount'] = 0
try:    print 'game version = %d' % selectserver.g_ServerVersion
except: print 'game version error'
if g_LoginAccountInfo['Count'] == 0:
    EnterSelectRole()
```

---

## 3. `GS2C_LOGIN_PLAYER_INFO` = 3（服务端 → 客户端，每个角色一条）

| 宽 | 字段 | 解包 |
|---:|---|---|
| 4 | `ID` | `UnpackInt(4)` |
| 4 | `time` | `UnpackInt(4)` |
| 1 | `Icon` | `UnpackInt(1)` |
| 2 | `Shape` | `UnpackInt(2)` |
| 2 | `Desc` | `UnpackInt(2)` |
| 1 | `Level` | `UnpackInt(1)` |
| 1 | `School` | `UnpackInt(1)` |
| 1 | `Race` | `UnpackInt(1)`；不在 `(0,1,2,3,4)` 内会被脚本强制改成 0 |
| 1 | `iPrepareLoad` | `UnpackInt(1)` |
| 4 | `Point` | `UnpackSigned(4)` |
| 16 | `Name` | `UnpackString(16)` |

每条 **37 字节**（含 cmd 则 38）。

脚本随后：
```
g_LoginRoleInfo.append(info)
g_LoginAccountInfo['CurCount'] += 1
if g_LoginAccountInfo['CurCount'] == g_LoginAccountInfo['Count']:
    EnterSelectRole()
```
另有两处客户端自算显示字段，与协议无关：
`info['Photo'] = ((info['Icon'] - 1) % 12) + 1`；
若 `ID` 已存在于 `g_LoginRoleInfo` 则覆盖而不是追加。

`[待确认]` `UnpackString(16)` 到底是「读 16 字节定长」还是「先读 1 字节长度、
再读至多 16 字节」。写模拟服务器时两种都要试。

---

## 4. `C2GS_ANSWERHELLO` = 62（`NakedSend`，客户端 → 服务端）

`S2CHello` 里：

```python
print 'seed1:%x' % seed
seed = (4294967296 - seed) % 3227993 + 2562088
seed = seed OP 6636321                      # OP 见下
netobj.NakedSend(
      chr(seed % 256)
    + chr((seed / 256  ) % 256)
    + chr((seed / 65536) % 256)
    + '\x00' + '\x00' * 21 )
```

**定长 25 字节**：3 字节由 seed 派生 + `'\x00'` + 21 个 `'\x00'`。

- `0x3D` = `BINARY_DIVIDE` 已由 `seed/256%256`、`seed/65536%256` 确证。
- `0x27`（`seed OP 6636321`）在 XOR / AND / OR 之间还定不下来；
  `6636321 = 0x653F21`。
- `0x3F` 判为 `BINARY_SUBTRACT`（`4294967296 - seed`），与
  `CurCount += 1` 里 `0x43 = BINARY_ADD` 不冲突。

`[待确认]` `NakedSend` 是否绕过加密。`0x4680a0` 走的是全局 `0x82a370`，
看起来绕过了 `0x4ab3f0`（正常发送路径）。若确实不加密，这 25 字节就是明文。

---

## 5. 最小链路

```
[server] GS2C_HELLO (cmd=1, 明文)  08 01 <seed:u32LE> <servernum:u16LE> <cert:u8>
[client] C2GS_ANSWERHELLO (cmd=62) 25 字节
[client] C2GS_ACCOUNT_ENTER (cmd=1) 82+ 字节
[server] LOGIN_ACCOUNT_INFO (cmd=15, Count=1, vid=1..3)
[server] LOGIN_PLAYER_INFO  (cmd=3,  一条 37 字节角色)
   ⇒ CurCount==Count ⇒ EnterSelectRole() ⇒ selectrole.Show(True)
[client] C2GS_PLAYER_ENTER (cmd=2, 选人)
[server] PLAYER_ENTER (4) / PROP_INIT (16) / MAP_*  ⇒ 进地图
```

---

## 6. 附：本次校验出来的 opcode（供 `tools/pydis26.py` 复用）

在 v4 统计表之外，靠具体语义新确认/修正的：

| 混淆字节 | 标准(2.6) | 指令 | 判据 |
|---|---|---|---|
| `0x3D` | 21 | BINARY_DIVIDE | `seed/256%256`、`seed/65536%256` |
| `0x43` | 23 | BINARY_ADD | `CurCount += 1` |
| `0x3F` | 24 | BINARY_SUBTRACT | `4294967296 - seed` |
| `0x37` | 22 | BINARY_MODULO | `'seed1:%x' % seed`、`% 12` |
| `0x09` | 20 | BINARY_MULTIPLY | `'\x00' * 21`、`pcinfo = '0' * 32` |
| `0x46` | 63 | BINARY_RSHIFT | `adsid >> 32` |
| `0x3E` | 64 | BINARY_AND | `adsid & 0xFFFFFFFF` |
| `0x5B` | 66 | BINARY_OR | `iScriptV1 \| 128` |
| `0x05` | 60 | STORE_SUBSCR | `info['ID'] = UnpackInt(4)` |
| `0x06` / `0x5A` | 3 / 2 | ROT_THREE / ROT_TWO | `a,b,c = x,y,z` 窥孔优化 |
| `0x40` | 87 | POP_BLOCK | try 体结束 |
| `0x10` | 88 | END_FINALLY | except 分支后被跳过的 1 字节 |
| `0xCF` | 127 | SET_LINENO | **证明是 2.6**（2.7 已移除） |
| `0xBC` | 99 | DUP_TOPX | `CurCount += 1` |
| `0x0B` / `0x1F` | 70 / 71 | PRINT_ITEM / PRINT_NEWLINE | `try: print ... except: print` |
| `0x30` | 104 | BUILD_MAP（1 字节） | 字典字面量头 |
| `0x6C` | 92 | UNPACK_SEQUENCE | `n1,n2,n3 = ...` |

仍未定：`0x27`（XOR/AND/OR 之一）、`0x47`（`S2CLoginRoleInfo` 覆盖分支里的
`BREAK_LOOP` 之类）。
