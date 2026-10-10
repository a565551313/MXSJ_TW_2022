# netserver.py 完整反编译报告

**项目**: 梦想世界 (MXSJ) 台湾版 2022
**脚本**: `script\login\netserver.py` (FLS entry 516)
**时间**: 2026-10-10
**状态**: 部分解码 - 52/59 函数可解码, 7个类定义待破解

---

## 1. 全局变量 (从 ModuleReset 恢复)

```python
g_iPlayerId = None  # 玩家ID
g_ServerRoleInfo = None  # 服务器角色信息
g_LoginServer = None  # 登录服务器 (fieldname, servername)
g_LoginServerID = None  # 登录服务器ID
g_LoginServerIP = None  # 登录服务器IP
g_LoginServePort = None  # 登录服务器端口
g_ConnectMgr = None  # 连接管理器
g_Net = None  # 网络对象 (CMXNet)
g_Proxy = None  # 代理服务器
g_LastProxy = None  # 上次代理
g_ProxyName = None  # 代理名称
g_AutoProxy = False  # 自动代理
g_SelectServerOver = False  # 选服完成
g_UnEnableServerList = []  # 禁用服务器列表
g_ErrorAnsMsg = None  # 错误消息
g_NewBieServer = None  # 新手服务器
g_PriorServer = None  # 优先服务器
g_KFServerID = None  # 开服服务器ID
g_RefreshServerListCount = None  # 刷新计数
```

---

## 2. 关键函数解码

### ModuleReset

```python
def ModuleReset():
    """重置所有全局变量"""
    global g_ServerRoleInfo, g_NewBieServer, g_PriorServer
    global g_LoginServer, g_LoginServerID, g_LoginServerIP, g_LoginServePort
    global g_ConnectMgr, g_Proxy, g_LastProxy, g_ProxyName
    global g_AutoProxy, g_SelectServerOver, g_UnEnableServerList
    global g_ErrorAnsMsg, g_iPlayerId
    g_ServerRoleInfo = None
    g_NewBieServer = None
    g_PriorServer = None
    g_LoginServer = None
    g_LoginServerID = None
    g_LoginServerIP = None
    g_LoginServePort = None
    g_ConnectMgr = None
    g_Proxy = None
    g_LastProxy = None
    g_ProxyName = None
    g_AutoProxy = False
    g_SelectServerOver = False
    g_UnEnableServerList = []
    g_ErrorAnsMsg = None
    g_iPlayerId = None
```

### GetPlayerID

```python
def GetPlayerID():
    """获取玩家ID"""
    return g_iPlayerId
```

### SetPlayerID

```python
def SetPlayerID(iPlayerID):
    """设置玩家ID"""
    global g_iPlayerId
    g_iPlayerId = iPlayerID
```

### GetServerRoleInfo

```python
def GetServerRoleInfo():
    """获取服务器角色信息"""
    return g_ServerRoleInfo
```

### GetLoginServeIPPort

```python
def GetLoginServeIPPort():
    """获取登录服务器IP和端口"""
    return g_LoginServerIP, g_LoginServePort
```

### SetLoginServerIPPort

```python
def SetLoginServerIPPort(ip, port):
    """设置登录服务器IP和端口"""
    global g_LoginServerIP, g_LoginServePort
    g_LoginServerIP = ip
    g_LoginServePort = port
```

### C2STransferServer

```python
def C2STransferServer(serverid, netobj):
    """选择服务器 - 发送 C2GS_SELECT_SERVER 命令"""
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid)
    netobj.PacketSend()
```

### PacketPrepare

```python
def PacketPrepare(self, icmd):
    """准备数据包"""
    net.CNet.PacketPrepare(self, icmd)
    self.m_iCmd = icmd
```

### OnServerCmd

```python
def OnServerCmd(self, icmd):
    """处理服务器命令"""
    if hasattr(self, 'm_Hello'):
        net.CNet.OnServerCmd(self, icmd)
```

### OnConnectFail

```python
def OnConnectFail(self):
    """连接失败处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketConnectFail(self)
    else:
        net.CNet.OnConnectFail(self)
```

### OnError

```python
def OnError(self, msg):
    """错误处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketError(self)
    else:
        net.CNet.OnError(self, msg)
```

### RandomConnect

```python
def RandomConnect():
    """随机连接服务器"""
    global g_ConnectMgr
    g_ConnectMgr = CRandomConnectMgr()
    g_ConnectMgr.Connect()
```

### OnSocketConnectFail

```python
def OnSocketConnectFail(self, netobj):
    """Socket连接失败"""
    self.ConnectTestFail()
```

### OnSocketError

```python
def OnSocketError(self, netobj):
    """Socket错误"""
    self.ConnectTestFail()
```

### nexttest

```python
def nexttest(obj):
    """下一个测试"""
    obj.Connect()
```

### SetTimeOutCmd

```python
def SetTimeOutCmd(self, nexttest):
    """设置超时命令"""
    if getattr(self, 'm_TimeoutCmd', None):
        self.m_TimeoutCmd.Release()
    self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)
```

### TransferServer

```python
def TransferServer(fieldname, servername, server_ip, port, serverid, ...):
    """转移到选定的服务器"""
    g_LoginServer = (fieldname, servername)
    g_LoginServerID = serverid
    SetLoginServerIPPort(server_ip, port)
    print('Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d' % ...)
```

### showlogin

```python
def showlogin(dlg):
    """显示登录界面"""
    global g_ConnectMgr, g_AutoProxy
    g_ConnectMgr = None
    g_AutoProxy = False
    if ...:
        net.g_Net.Disconnect()
    net.CFakeNet()
    dlg.Show(False)
```

### GetProxy

```python
def GetProxy():
    """获取代理设置"""
    if g_Proxy != 'auto':
        return g_LastProxy
    return g_Proxy
```

---

## 3. 登录协议分析

### 3.1 命令列表

| 命令 | 方向 | 用途 |
|-----|------|------|
| `loginhello` | C→S | 登录握手 |
| `TEST_HELLO` | C→S | 测试连接 |
| `RESELECT_HELLO` | C→S | 重选服务器 |
| `C2GS_SELECT_SERVER` | C→S | 选择服务器 (参数: serverid) |
| `dgwconnecttest` | C→S | DGW网关测试 |
| `S2CServerRoleInfo` | S→C | 服务器角色信息 |

### 3.2 登录流程

```
1. showlogin(dlg)          - 显示登录界面
2. RandomConnect()         - 随机连接服务器
3. Connect()               - 发送 loginhello/TEST_HELLO
4. S2CServerRoleInfo()     - 接收服务器列表
5. TransferServer(...)     - 转移到选定服务器
6. C2STransferServer(sid)  - 发送选服命令
```

### 3.3 包构造协议

```python
netobj.PacketPrepare(command)  # 设置命令字
netobj.PacketAddI(value)       # 添加int参数
netobj.PacketSend()            # 发送
```

---

## 4. 技术总结

- **映射数量**: 37 个 (含参数字节)
- **完全解码函数**: 30+ 个
- **部分解码函数**: 20+ 个
- **待解码**: 7 个类定义函数 (使用替换表B)

### 关键映射表

| 编码 | 标准 | 名称 |
|-----|------|------|
| 0x41 | 0x01 | POP_TOP |
| 0x55 | 0x3C | RETURN_VALUE |
| 0x71 | 0x63 | STORE_FAST |
| 0x85 | 0x4E | LOAD_NAME |
| 0x8F | 0x4D | LOAD_CONST |
| 0x95 | 0x54 | COMPARE_OP |
| 0xB7 | 0x5B | POP_JUMP_IF_FALSE |
| 0xC1 | 0x62 | LOAD_FAST |
| 0xC4 | 0x43 | STORE_NAME |
| 0xC5 | 0x48 | STORE_ATTR |
| 0xCA | 0x50 | BUILD_LIST |
| 0xD9 | 0x53 | LOAD_ATTR |
| 0xDA | 0x66 | CALL_FUNCTION |
| 0xDE | 0x4F | BUILD_TUPLE |
| 0xE0 | 0x52 | BUILD_MAP |
| 0xE5 | 0x57 | JUMP_FORWARD |

---

**报告结束** - 2026-10-10