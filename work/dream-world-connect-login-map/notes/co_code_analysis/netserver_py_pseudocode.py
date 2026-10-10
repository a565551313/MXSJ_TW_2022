"""
netserver.py 伪代码反编译
生成时间: 2026-10-10
状态: 部分解码 (基于替换表A)
来源: 梦想世界(MXSJ)台湾版 2022, FLS entry 516
"""

# ============================================================
# 全局变量
# ============================================================

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

# ============================================================
# 全局函数
# ============================================================

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

def GetPlayerID():
    """获取玩家ID"""
    return g_iPlayerId

def SetPlayerID(iPlayerID):
    """设置玩家ID"""
    global g_iPlayerId
    g_iPlayerId = iPlayerID

def GetServerRoleInfo():
    """获取服务器角色信息"""
    return g_ServerRoleInfo

def GetLoginServeIPPort():
    """获取登录服务器IP和端口"""
    return g_LoginServerIP, g_LoginServePort

def SetLoginServerIPPort(ip, port):
    """设置登录服务器IP和端口"""
    global g_LoginServerIP, g_LoginServePort
    g_LoginServerIP = ip
    g_LoginServePort = port

def C2STransferServer(serverid, netobj):
    """选择服务器 - 发送 C2GS_SELECT_SERVER 命令"""
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid)
    netobj.PacketSend()

def PacketPrepare(self, icmd):
    """准备数据包"""
    net.CNet.PacketPrepare(self, icmd)
    self.m_iCmd = icmd

def OnServerCmd(self, icmd):
    """处理服务器命令"""
    if hasattr(self, 'm_Hello'):
        net.CNet.OnServerCmd(self, icmd)

def OnConnectFail(self):
    """连接失败处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketConnectFail(self)
    else:
        net.CNet.OnConnectFail(self)

def OnError(self, msg):
    """错误处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketError(self)
    else:
        net.CNet.OnError(self, msg)

def RandomConnect():
    """随机连接服务器"""
    global g_ConnectMgr
    g_ConnectMgr = CRandomConnectMgr()
    g_ConnectMgr.Connect()

def OnSocketConnectFail(self, netobj):
    """Socket连接失败"""
    self.ConnectTestFail()

def OnSocketError(self, netobj):
    """Socket错误"""
    self.ConnectTestFail()

def nexttest(obj):
    """下一个测试"""
    obj.Connect()

def SetTimeOutCmd(self, nexttest):
    """设置超时命令"""
    if getattr(self, 'm_TimeoutCmd', None):
        self.m_TimeoutCmd.Release()
    self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)

def TransferServer(fieldname, servername, server_ip, port, serverid, ...):
    """转移到选定的服务器"""
    g_LoginServer = (fieldname, servername)
    g_LoginServerID = serverid
    SetLoginServerIPPort(server_ip, port)
    print('Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d' % ...)

def showlogin(dlg):
    """显示登录界面"""
    global g_ConnectMgr, g_AutoProxy
    g_ConnectMgr = None
    g_AutoProxy = False
    if ...:
        net.g_Net.Disconnect()
    net.CFakeNet()
    dlg.Show(False)

def GetProxy():
    """获取代理设置"""
    if g_Proxy != 'auto':
        return g_LastProxy
    return g_Proxy

# ============================================================
# 类定义 (待完整解码 - 使用替换表B)
# ============================================================

class CMXNet:
    """网络类"""
    def __init__(self): ...
    def PacketPrepare(self, icmd): ...
    def OnServerCmd(self, icmd): ...
    def OnConnectFail(self): ...
    def OnError(self, msg): ...

class CConnectMgr:
    """连接管理器基类"""
    def Connect(self): ...

class CRandomConnectMgr(CConnectMgr):
    """随机连接管理器"""
    def Connect(self): ...  # 689字节, 核心连接逻辑

class CReselectConnectMgr(CConnectMgr):
    """重选连接管理器 (含DGW网关)"""
    m_Pwd = None
    m_PassPort = None
