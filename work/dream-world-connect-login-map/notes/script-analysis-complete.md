# Entry 516 Python 脚本完整分析报告
## `script\login\netserver.py` - 登录网络服务器模块

**分析日期**: 2026-10-10
**脚本路径**: `script\login\netserver.py` (在 `data/script.fls` entry 516 中)
**解码状态**: ✅ 完整解码（5层XOR + zlib + Python 2.7 marshal）
**代码对象数**: 59 个

---

## 1. 模块概述

这是一个 **Python 2.7 脚本**，是梦想世界客户端的**登录阶段网络处理模块**。负责：
- 服务器列表管理和选择
- 登录服务器连接
- 服务器命令处理（`OnServerCmd`）
- 代理/网关（DGW）连接管理
- 角色信息和玩家ID管理

---

## 2. 全局变量

| 变量名 | 用途 |
|--------|------|
| `g_ServerRoleInfo` | 服务器角色信息 |
| `g_NewBieServer` | 新手服务器标志 |
| `g_PriorServer` / `g_PriorServerInfo` | 优先/推荐服务器 |
| `g_LoginServer` | 当前登录服务器对象 |
| `g_LoginServerID` | 登录服务器ID |
| `g_KFServerID` | 跨服服务器ID |
| `g_LoginServerIP` | 登录服务器IP |
| `g_LoginServePort` | 登录服务器端口 |
| `g_ConnectMgr` | 连接管理器实例 |
| `g_Proxy` / `g_LastProxy` | 代理服务器信息 |
| `g_ProxyName` | 代理名称 |
| `g_AutoProxy` | 自动选择代理标志 |
| `g_SelectServerOver` | 服务器选择完成标志 |
| `g_RefreshServerListCount` | 刷新服务器列表计数 |
| `g_UnEnableServerList` | 不可进入服务器列表 |
| `g_ErrorAnsMsg` | 错误应答消息 |
| `g_iPlayerId` | 玩家ID |
| `g_IsDgwConnect` | 是否DGW连接 |
| `g_DGWRsLoginInfo` | DGW重选登录信息 |

---

## 3. 核心类和函数

### 3.1 CMXNet 类（主网络类）

```python
class CMXNet:
    def __init__(self):          # 初始化网络模块
        ...
    def PacketPrepare(self):     # 准备数据包
        ...
    def OnServerCmd(self, cmd):  # 服务器命令回调（由原生层触发）
        ...
    def OnConnectFail(self):    # 连接失败回调
        ...
    def OnError(self):          # 错误回调
        ...
```

**关键**: `OnServerCmd(int)` 是原生层事件 `0x2714` 触发的回调，接收一个 16位 命令字。

### 3.2 连接管理器类

| 类名 | 用途 |
|------|------|
| `CConnectMgr` | 基础连接管理器 |
| `CRandomConnectMgr` | 随机连接管理器（测试代理/服务器） |
| `CReselectConnectMgr` | 重选连接管理器 |

### 3.3 关键函数

| 函数名 | 功能 |
|--------|------|
| `ModuleReset()` | 重置模块状态 |
| `SetPlayerID(id)` / `GetPlayerID()` | 设置/获取玩家ID |
| `getMsg(...)` | 获取消息文本 |
| `RefreshServerInfo()` | 刷新服务器信息（HTTP请求 `update.ini` 中的 `BulletinURL`） |
| `GetErrorAnsMsg(...)` | 获取错误应答消息 |
| `SetUnEnterServerList(list)` / `GetUnEnterServerList()` / `ClearUnEnterServerList()` | 管理不可进入服务器列表 |
| `IsSelectServerOver()` / `SetSelectServerOver(flag)` | 查询/设置服务器选择完成状态 |
| `SetConnectedProxy(proxy)` / `GetConnectedProxy()` | 设置/获取已连接代理 |
| `GetProxy()` / `SetProxy(proxy)` | 获取/设置代理 |
| `GetProxyName()` / `SetProxyName(name)` / `GetProxyNameByProxy(proxy)` | 代理名称管理 |
| `SetServerRoleInfo(info)` / `GetServerRoleInfo()` | 设置/获取服务器角色信息 |
| `SetLoginServerIPPort(ip, port)` / `GetLoginServeIPPort()` / `GetLoginServer()` | 登录服务器IP/端口管理 |
| `TransferServer(...)` | 转移服务器 |
| `showlogin()` | 显示登录界面 |
| `ShowConnectingDlg()` | 显示"正在连接"对话框 |
| `S2CServerRoleInfo(...)` | 处理服务器下发的角色信息 |
| `C2STransferServer(...)` | 发送转移服务器请求 |
| `ProcessServerCmd(cmd)` | **处理服务器命令（核心分发函数）** |

---

## 4. 关键命令字发现

从脚本字符串中提取的关键命令/协议字符串：

| 字符串 | 含义 | 可能用途 |
|--------|------|----------|
| `loginhello` | 登录握手 | **登录阶段第一个命令**，客户端→服务器 |
| `TEST_HELLO` | 测试握手 | 连接测试（代理/服务器探测） |
| `RESELECT_HELLO` | 重选握手 | 重新选择服务器时的握手 |
| `Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d` | 转服命令格式 | 跨服转移时的数据格式 |
| `PROXY_CONNECT_TIMEOUT` | 代理连接超时 | 代理连接超时设置 |
| `dgwconnecttest` | DGW连接测试 | 多益网关连接测试 |
| `DGW_RESELECTCONNECT` | DGW重选连接 | 通过DGW重选服务器 |
| `CreatePyCommand` | 创建Python命令 | 动态创建命令对象 |
| `NakedSend` | 裸发送 | 不经过Packet封装的直接发送 |
| `SetTimeOutCmd` | 设置超时命令 | 设置命令超时处理 |

### 4.1 推测的登录流程

```
1. 客户端选择服务器
   └── 显示 "正在连接" 对话框 (ShowConnectingDlg)
   
2. 建立 TCP 连接 (IMP_ConnectNsServer)
   └── 连接成功 → OnConnected 事件 (0x2711)
   
3. 发送登录握手包
   └── 命令: "loginhello" (可能是 C2S 的第一个命令)
   └── 使用 PacketPrepare + PacketAdd* 系列函数构造
   └── 使用 IMP_SendBuffer2NS 发送
   
4. 等待服务器响应
   └── 服务器返回命令 → 事件 0x2714 → OnServerCmd(cmd)
   └── ProcessServerCmd(cmd) 分发处理
   
5. 处理服务器命令
   ├── S2CServerRoleInfo → 设置角色信息 → 显示登录界面 (showlogin)
   ├── C2STransferServer → 转移服务器
   └── 其他命令...
```

---

## 5. 连接管理器详解

### 5.1 CConnectMgr（基础连接管理器）

```python
class CConnectMgr:
    def __init__(self):
        self.m_ServerInfo = None    # 服务器信息
        self.m_TimeoutCmd = None    # 超时命令
        ...
    
    def GetServerInfo(self):        # 获取服务器信息
        ...
    def GetTestProxyList(self):     # 获取测试代理列表
        ...
    def GetTestServerList(self):    # 获取测试服务器列表
        ...
    def Connect(self):              # 连接
        ...
    def nexttest(self):             # 测试下一个
        ...
    def SetTimeOutCmd(self, cmd):   # 设置超时命令
        ...
    def ConnectTestFail(self):      # 连接测试失败
        ...
```

### 5.2 CRandomConnectMgr（随机连接管理器）

```python
class CRandomConnectMgr:
    def __init__(self):
        self.m_Time = 0             # 时间戳
        self.m_AllTry = 0           # 总尝试次数
        ...
    
    def Connect(self):              # 随机连接
        ...
    def RandomConnect(self):        # 随机选择并连接
        ...
```

**用途**: 测试多个代理/服务器，选择最快的连接。

### 5.3 CReselectConnectMgr（重选连接管理器）

```python
class CReselectConnectMgr:
    def __init__(self):
        self.m_ServerID = 0         # 服务器ID
        self.m_Idx = 0              # 索引
        self.m_Pwd = ""             # 密码/口令
        self.m_PassPort = 0         # 通行端口
        self.m_EntryName = ""       # 入口名称
        ...
    
    def ReselectServerConnect(self):    # 重选服务器连接
        ...
    def DgwReselectServerConnect(self): # DGW重选连接
        ...
    def NormalReselectServerConnect(self): # 普通重选连接
        ...
```

**关键字段**: `m_Pwd`（密码）、`m_PassPort`（通行端口）- 这些是**登录凭证**！

---

## 6. DGW（Duoyi Gateway）系统

脚本中包含 **DGW（多益网关）** 相关功能，这是一个代理/加速器系统：

| 字符串 | 含义 |
|--------|------|
| `dgwconnecttest` | DGW连接测试 |
| `g_DGWRsLoginInfo` | DGW重选登录信息 |
| `DGW_RESELECTCONNECT` | DGW重选连接命令 |
| `g_IsDgwConnect` | 是否通过DGW连接 |
| `dgw.dll` | DGW动态库（HTTP辅助） |

**DGW 功能**:
- 代理/加速器连接
- 服务器列表获取（`GetTargetServers`）
- 连接测试和选择
- 重选服务器时的网关切换

---

## 7. 数据包构造

从脚本和 mx.exe 字符串中，数据包构造流程：

```python
# 典型的发包流程（推测）
def send_login_hello(self):
    # 1. 准备数据包
    self.PacketPrepare()           # 调用原生 PacketPrepare
    
    # 2. 添加字段
    IMP_WriteUInt16(cmd_id)        # 命令字
    IMP_WriteStr("loginhello")     # 握手字符串
    IMP_WriteUInt32(player_id)     # 玩家ID
    # ... 更多字段
    
    # 3. 发送
    IMP_SendBuffer2NS()            # 发送到服务器
```

原生层提供的包构造函数（从 mx.exe 字符串）：
- `PacketPrepare` - 开始构造包
- `PacketAddI` / `PacketAddUI` - 添加整数
- `PacketAddL` - 添加长整数
- `PacketAddS` - 添加字符串
- `PacketAddBinaryS` - 添加二进制数据
- `PacketSend` - 发送包
- `NakedSend` - 裸发送（不封装）

---

## 8. 与原生层的交互

### 8.1 原生 → Python 回调

| 事件ID | 原生触发 | Python回调 | 参数 |
|--------|----------|------------|------|
| 0x2711 | TCP连接成功 | `OnConnected` | 无 |
| 0x2712 | 错误 | `OnError` | 错误码 |
| 0x2714 | 收到服务器命令 | `OnServerCmd` | uint16 命令字 |

### 8.2 Python → 原生 调用

| Python 调用 | 原生函数 | 功能 |
|-------------|----------|------|
| `PacketPrepare()` | `IMP_NewIMBuffWriter` | 创建包写入器 |
| `IMP_WriteUInt16(val)` | `IMP_WriteUInt16` | 写入uint16 |
| `IMP_WriteStr(str)` | `IMP_WriteStr` | 写入字符串 |
| `IMP_SendBuffer2NS()` | `IMP_SendBuffer2NS` | 发送包 |
| `Connect(ip, port)` | `IMP_ConnectNsServer` | 连接服务器 |
| `RefreshCryptKey(key)` | `IMP_RefreshCryptKey` | 刷新密钥 |

---

## 9. 未解决的问题

1. **命令字具体数值**: `loginhello`、`TEST_HELLO` 等字符串对应的具体命令ID（uint16）
2. **数据包格式**: 每个命令的完整字段布局
3. **服务器响应格式**: 服务器返回的数据包结构
4. **加密时机**: 哪些包加密、哪些不加密
5. **密钥交换**: `IMP_RefreshCryptKey` 的密钥来源和交换时机
6. **co_code 自定义编码**: 脚本字节码的第二层编码转换

---

## 10. 下一步行动建议

### 10.1 立即行动
1. **动态捕获密钥**: 在 `IMP_RefreshCryptKey` 处下断点，捕获实际密钥字符串
2. **抓包分析**: 捕获真实登录数据包，用破解的加密算法解密
3. **命令字映射**: 确定 `loginhello` 等字符串对应的具体命令ID

### 10.2 深入分析
4. **完整反编译脚本**: 破解 `co_code` 的自定义编码，完整反编译 Python 脚本
5. **协议文档**: 编写完整的协议命令字和数据格式文档
6. **模拟服务器**: 实现一个能完成登录流程的模拟服务器

### 10.3 终极目标
7. **离线登录**: 实现无需官方服务器的本地登录
8. **进入空地图**: 完成登录 → 角色选择 → 进入空地图的完整流程

---

## 11. 关键文件

| 文件 | 说明 |
|------|------|
| `data/script.fls` (entry 516) | 本脚本的源文件 |
| `work/.../entry516-five-xor-marshal.bin` | 解码后的 marshal 数据 |
| `work/.../decode_entry516.py` | 解码器脚本 |
| `work/.../entry516-result.json` | 解码结果 JSON |
| `IMProtocol.dll` | 网络协议库 |
| `mx.exe` / `mxmain.dll` | 主程序（含原生回调桥接） |
