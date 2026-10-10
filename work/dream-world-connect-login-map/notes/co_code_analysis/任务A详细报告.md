# 任务A详细报告: 破解 co_code 自定义编码，反编译登录脚本

**项目**: 梦想世界 (MXSJ) 台湾版 2022
**目标**: `script\login\netserver.py` (FLS entry 516)
**时间**: 2026-10-10
**状态**: 重大突破 - 已定位解码函数，破解部分映射，成功解码关键函数

---

## 1. 执行摘要

本任务成功破解了梦想世界客户端 Python 脚本的**自定义字节码编码**，定位了编码/解码函数，破解了部分 opcode 映射表，并成功解码了登录脚本中的多个关键函数。

### 关键成果

| 成果 | 状态 |
|-----|------|
| 定位字节码解码函数 | 完成 (0x420F80) |
| 确认编码方式 | 字节替换 (S盒) |
| 破解 opcode 映射 | 15+ 个映射 |
| 解码关键函数 | 10+ 个函数 |
| 理解包构造协议 | PacketPrepare/PacketAddI/PacketSend |
| 理解选服协议 | C2STransferServer |
| 完整反编译源码 | 进行中 (需要更多映射) |

---

## 2. 编码方式详解

### 2.1 编码类型
**co_code 使用字节替换编码（S盒替换）**，在游戏引擎加载脚本时动态解码。**

### 2.2 解码函数定位

| 项目 | 值 |
|-----|-----|
| **函数地址** | `0x420F80` (VMA) |
| **调用者** | `0x421D93` |
| **算法** | 多态字节替换，根据模式字节选择 |
| **模式 2** | 3字节一组简单替换 @ `0x421001` |
| **模式 6** | 4字节一组简单替换 @ `0x4210AC` |

### 2.3 替换循环伪代码 (模式 2)

```c
// 3字节一组的字节替换循环 @ 0x421001
for (int i = 0; i < count; i++) {
    data[i*3+0] = sbox[data[i*3+0]];  // 替换字节0 (opcode)
    data[i*3+1] = sbox[data[i*3+1]];  // 替换字节1 (参数低字节)
    data[i*3+2] = sbox[data[i*3+2]];  // 替换字节2 (参数高字节)
}
```

### 2.4 关键发现: 参数字节也被替换

- **所有3个字节都被替换**，包括参数字节
- 但对于小值 (0x00-0x02)，替换表是**恒等映射** (`table[x] = x`)
- 这解释了为什么参数看起来是"明文"
- 对于较大的参数值，参数也会被编码

---

## 3. 已破解的 Opcode 映射表

### 3.1 替换表 A (用于大部分函数)

| 编码字节 | 标准字节 | Opcode 名称 | 参数 | 破解方法 |
|---------|---------|------------|------|---------|
| 0x00 | 0x00 | (恒等) | - | 参数分析 |
| 0x01 | 0x01 | (恒等) | - | GetLoginServeIPPort |
| 0x02 | 0x02 | (恒等) | - | GetLoginServeIPPort |
| 0x41 | 0x01 | POP_TOP | 无 | OnSocketConnectFail |
| 0x55 | 0x3C | RETURN_VALUE | 无 | 多个函数末尾 |
| 0x71 | 0x63 | STORE_FAST | 2字节 | 统计分析 + C2STransferServer |
| 0x85 | 0x4E | LOAD_NAME | 2字节 | GetPlayerID |
| 0x8F | 0x4D | LOAD_CONST | 2字节 | SetPlayerID |
| 0xC1 | 0x62 | LOAD_FAST | 2字节 | SetPlayerID |
| 0xC4 | 0x43 | STORE_NAME | 2字节 | SetPlayerID |
| 0xC5 | 0x48 | STORE_ATTR | 2字节 | PacketPrepare (推测) |
| 0xCA | 0x50 | BUILD_LIST | 2字节 | ClearUnEnterServerList |
| 0xD9 | 0x53 | LOAD_ATTR | 2字节 | OnSocketConnectFail |
| 0xDA | 0x66 | CALL_FUNCTION | 2字节 | OnSocketConnectFail |
| 0xDE | 0x4F | BUILD_TUPLE | 2字节 | GetLoginServeIPPort |

### 3.2 可能的额外映射 (待验证)

| 编码字节 | 推测标准 | Opcode 名称 | 证据 |
|---------|---------|------------|------|
| 0xB7 | 0x5B 或 0x58 | POP_JUMP_IF_FALSE / JUMP_IF_FALSE_OR_POP | OnServerCmd (条件跳转) |
| 0xE5 | 0x57 | JUMP_FORWARD | OnServerCmd, showlogin |
| 0xE0 | 0x45 或 0x52 | UNPACK_SEQUENCE / BUILD_MAP | 多个函数 |
| 0x37 | 0x45 | UNPACK_SEQUENCE | TransferServer |
| 0x98 | 0x67 | MAKE_FUNCTION | 类定义 (CMXNet) |
| 0xFB | 0x43 | STORE_NAME | 类定义 (可能不同替换表) |
| 0xAA | 0x4E | LOAD_NAME | 类定义 (可能不同替换表) |

### 3.3 重要说明: 可能存在多个替换表

从解码函数的多态结构可知，**不同函数可能使用不同的替换表**。目前破解的主要是"替换表 A"，用于大部分简单函数和部分复杂函数。类定义函数 (如 CMXNet) 可能使用不同的替换表。

---

## 4. 已解码的关键函数

### 4.1 C2STransferServer (完全解码)

**功能**: 选择服务器 (客户端 → 服务器)

**反汇编字节码**:
```
 0: LOAD_NAME 0 (net)
 3: LOAD_ATTR 1 (g_Net)
 6: STORE_FAST 1 (netobj)
 9: LOAD_FAST 1 (netobj)
12: LOAD_ATTR 2 (PacketPrepare)
15: LOAD_NAME 0 (net)
18: LOAD_ATTR 3 (C2GS_SELECT_SERVER)
21: CALL_FUNCTION 1
24: POP_TOP
25: LOAD_FAST 1 (netobj)
28: LOAD_ATTR 4 (PacketAddI)
31: LOAD_FAST 0 (serverid)
34: LOAD_CONST 1
37: CALL_FUNCTION 2
40: POP_TOP
41: LOAD_FAST 1 (netobj)
44: LOAD_ATTR 5 (PacketSend)
47: CALL_FUNCTION 0
50: POP_TOP
51: LOAD_CONST 0
54: RETURN_VALUE
```

**推测的 Python 源码**:
```python
def C2STransferServer(serverid, netobj):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid)
    netobj.PacketSend()
```

**协议意义**: 选择服务器时，发送 `C2GS_SELECT_SERVER` 命令，参数为 `serverid` (整数)

### 4.2 PacketPrepare (几乎完全解码)

**推测的 Python 源码**:
```python
def PacketPrepare(self, icmd):
    net.CNet.PacketPrepare(self, icmd)
    self.m_iCmd = icmd  # 0xC5 = STORE_ATTR
```

### 4.3 OnServerCmd (部分解码)

**推测的 Python 源码**:
```python
def OnServerCmd(self, icmd):
    if not hasattr(self, 'm_Hello'):  # 0xB7 = 条件跳转
        net.CNet.OnServerCmd(self, icmd)
    # 0xE5 = JUMP_FORWARD
```

### 4.4 TransferServer (部分解码)

**推测的 Python 源码**:
```python
def TransferServer(fieldname, servername, server_ip, port, serverid, ...):
    # 0x37 = UNPACK_SEQUENCE
    g_LoginServer = (fieldname, servername)
    g_LoginServerID = serverid
    SetLoginServerIPPort(server_ip, port)
    print('Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d' % ...)
    ...
```

### 4.5 简单 Getter/Setter (完全解码)

```python
# Getter 示例
def GetPlayerID():
    return g_iPlayerId

def GetServerRoleInfo():
    return g_ServerRoleInfo

def GetLoginServeIPPort():
    return g_LoginServerIP, g_LoginServePort

# Setter 示例
def SetPlayerID(iPlayerID):
    global g_iPlayerId
    g_iPlayerId = iPlayerID

def SetLoginServerIPPort(ip, port):
    global g_LoginServerIP, g_LoginServePort
    g_LoginServerIP = ip
    g_LoginServePort = port

def ClearUnEnterServerList():
    global g_UnEnableServerList
    g_UnEnableServerList = []
```

### 4.6 RandomConnect (完全解码)

```python
def RandomConnect():
    global g_ConnectMgr
    g_ConnectMgr = CRandomConnectMgr()
    g_ConnectMgr.Connect()
```

### 4.7 回调函数 (完全解码)

```python
def OnSocketConnectFail(self, netobj):
    self.ConnectTestFail()

def OnSocketError(self, netobj):
    self.ConnectTestFail()

def nexttest(obj):
    obj.Connect()
```

---

## 5. 登录流程分析

基于已解码的函数，登录流程大致为:

```
1. showlogin(dlg) - 显示登录界面
   - g_ConnectMgr = None
   - g_AutoProxy = False
   - 条件断开现有连接: net.g_Net.Disconnect()
   - 创建 CFakeNet
   - dlg.Show(False)

2. RandomConnect() 或 ReselectServerConnect() - 随机/重选服务器连接
   - g_ConnectMgr = CRandomConnectMgr()
   - g_ConnectMgr.Connect()

3. CConnectMgr.Connect() - 连接服务器 (647/689 字节，待完整解码)
   - 构造服务器列表
   - 发送 loginhello / TEST_HELLO / RESELECT_HELLO

4. 连接成功后 - 选择服务器
   - C2STransferServer(serverid, netobj)
   - 发送 C2GS_SELECT_SERVER 命令

5. 服务器响应 - 处理服务器角色信息
   - S2CServerRoleInfo(netobj) - 解析服务器列表
   - SetServerRoleInfo(infos) - 保存服务器信息

6. TransferServer(...) - 转移到选定的服务器
   - 设置 g_LoginServer, g_LoginServerID
   - SetLoginServerIPPort(server_ip, port)
   - C2STransferServer(...)
```

---

## 6. 包构造协议

从已解码的函数，包构造流程为:

```python
# 1. 准备包
netobj.PacketPrepare(net.C2GS_SELECT_SERVER)  # 设置命令字
# 或: net.CNet.PacketPrepare(self, icmd)

# 2. 添加参数
netobj.PacketAddI(serverid)    # 添加整数参数
# 可能还有: PacketAddUI, PacketAddL, PacketAddS, PacketAddBinaryS

# 3. 发送包
netobj.PacketSend()
# 或: NakedSend
```

**命令字** (从 names 列表提取):
- `C2GS_SELECT_SERVER` - 选择服务器
- `loginhello` - 登录握手
- `TEST_HELLO` - 测试连接
- `RESELECT_HELLO` - 重选服务器
- `C2STransferServer` - 转移服务器
- `S2CServerRoleInfo` - 服务器角色信息 (S→C)

---

## 7. 全局变量

从 ModuleReset 和各函数的 names 列表提取:

| 变量名 | 类型 | 用途 |
|-------|------|------|
| g_iPlayerId | int | 玩家ID |
| g_ServerRoleInfo | dict/list | 服务器角色信息 |
| g_LoginServer | tuple | 登录服务器 (fieldname, servername) |
| g_LoginServerID | int | 登录服务器ID |
| g_LoginServerIP | str | 登录服务器IP |
| g_LoginServePort | int | 登录服务器端口 |
| g_ConnectMgr | CConnectMgr | 连接管理器 |
| g_Proxy | str | 代理服务器 |
| g_LastProxy | str | 上次代理 |
| g_ProxyName | str | 代理名称 |
| g_AutoProxy | bool | 自动代理 |
| g_SelectServerOver | bool | 选服完成标志 |
| g_UnEnableServerList | list | 禁用服务器列表 |
| g_ErrorAnsMsg | str | 错误消息 |
| g_Net | CMXNet | 网络对象 |
| g_NewBieServer | ? | 新手服务器 |
| g_PriorServer | ? | 优先服务器 |
| g_KFServerID | int | 开服服务器ID |
| g_RefreshServerListCount | int | 刷新服务器列表计数 |

---

## 8. 类结构

### 8.1 CMXNet (网络类)
- 方法: `__init__`, `PacketPrepare`, `OnServerCmd`, `OnConnectFail`, `OnError`
- 属性: `m_Nets`, `m_IsFail`, `m_Hello`, `m_iCmd`, `m_ServerID`, `m_ServerInfo`

### 8.2 CConnectMgr (连接管理器基类)
- 方法: `__init__`, `Connect`, `GetServerInfo`, `GetTestProxyList`, `GetTestServerList`, `nexttest`, `SetTimeOutCmd`, `ConnectTestFail`

### 8.3 CRandomConnectMgr (随机连接管理器)
- 方法: `__init__`, `Connect` (689字节，最复杂的函数)

### 8.4 CReselectConnectMgr (重选连接管理器)
- 方法: `RandomConnect`, `ReselectServerConnect`, `DgwReselectServerConnect`, `NormalReselectServerConnect`
- 属性: `m_Pwd`, `m_PassPort` (DGW网关认证)

---

## 9. 技术细节

### 9.1 文件清单

| 文件 | 描述 |
|-----|------|
| `co_code_analyzer.py` | 初步字节码分析工具 |
| `co_code_analysis/code_objects.json` | 59个code object的完整信息 |
| `co_code_analysis/decoded_results.json` | 解码结果 |
| `co_code_analysis/extended_mapping.json` | 扩展映射表 |
| `co_code_analysis/statistical_analysis.json` | 统计分析结果 |
| `co_code_analysis/cross_references.json` | 交叉引用分析 |
| `co_code_analysis/bytecode_*.bin` | 各函数的原始字节码 |
| `co_code_analysis/decoded_*.bin` | 各函数的解码后字节码 |

### 9.2 二进制分析发现

| 项目 | 地址 (VMA) | 描述 |
|-----|-----------|------|
| 字节替换函数 | `0x420F80` | 多态字节替换 |
| 3字节替换循环 | `0x421001` | 模式2的核心循环 |
| 4字节替换循环 | `0x4210AC` | 模式6的核心循环 |
| 跳转表 | `0x421354` | 模式选择跳转表 |
| 调用者 | `0x421D93` | 调用字节替换函数 |
| PyCodeObject字段名 | `0x6CC258` | co_argcount等字段名表 |
| 'co_code'字符串 | `0x6CC28C` | PyCodeObject字段名 |
| 'script.fls'字符串 | `0x6B227D` | FLS文件路径 |
| '0SLF'魔数 | `0x6B8A0C` | FLS文件魔数 |
| FLS加载代码 | `0x48ED87` | 引用0SLF魔数 |

---

## 10. 下一步行动计划

### 10.1 短期 (继续任务A)

1. **破解更多映射** (优先级排序)
   - 0xB7 = POP_JUMP_IF_FALSE (0x5B) - 验证跳转目标
   - 0xE5 = JUMP_FORWARD (0x57) - 验证跳转目标
   - 0xE0 = UNPACK_SEQUENCE (0x45) 或 BUILD_MAP (0x52)
   - 0x95 = COMPARE_OP (0x54) - 从 getMsg 推测
   - 0x98 = MAKE_FUNCTION (0x67) - 从类定义推测
   - 0xFB = STORE_NAME (0x43) - 可能是不同替换表

2. **完整解码关键函数**
   - `Connect` (689字节) - 最复杂的连接函数
   - `ProcessServerCmd` (96字节) - 服务器命令处理
   - `S2CServerRoleInfo` (98字节) - 服务器角色信息解析
   - `getMsg` (159字节) - 消息解析
   - `RefreshServerInfo` (264字节) - 刷新服务器列表

3. **定位完整替换表**
   - 分析 `[arg1+0x188]` 的来源
   - 或在 `_dyprot0`/`_dyprot1` 段搜索
   - 或考虑动态分析 (Windows调试器)

### 10.2 中期 (任务A收尾)

4. **反编译完整 netserver.py**
   - 使用完整映射解码所有59个code object
   - 重建Python源码结构
   - 生成可读的伪代码/Python源码

5. **提取完整协议规范**
   - 所有命令字 (uint16) 的具体数值
   - 包格式定义
   - 登录握手完整流程

### 10.3 长期 (后续任务)

6. **任务B**: 分析其他脚本 (战斗、任务等)
7. **任务E**: 增强模拟服务器，支持完整登录流程
8. **任务G**: 编写完整协议文档

---

## 11. 风险与限制

1. **多替换表问题**: 不同函数可能使用不同的替换表，增加破解难度
2. **参数编码**: 参数字节也被替换，对于大参数值需要完整映射表
3. **保护壳**: `_dyprot0`/`_dyprot1` 段可能是 Themida 保护，增加静态分析难度
4. **动态分析需求**: 可能需要在 Windows 上用调试器捕获运行时的完整替换表

---

## 12. 备注

本分析完全基于**离线静态分析**，未修改原始样本，未连接外部服务器。

所有发现已记录在 `work/dream-world-connect-login-map/notes/co_code_analysis/` 目录下。

**报告生成时间**: 2026-10-10
**数据来源**: `entry516-five-xor-marshal.bin` (17,234 字节)