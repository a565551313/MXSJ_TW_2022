#!/usr/bin/env python3
"""生成任务A最终报告"""
import json, os

output_dir = 'work/dream-world-connect-login-map/notes/co_code_analysis'

# 关键函数伪代码（基于解码结果手工编写）
key_funcs = {
    'ModuleReset': '''def ModuleReset():
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
    g_iPlayerId = None''',

    'GetPlayerID': '''def GetPlayerID():
    """获取玩家ID"""
    return g_iPlayerId''',

    'SetPlayerID': '''def SetPlayerID(iPlayerID):
    """设置玩家ID"""
    global g_iPlayerId
    g_iPlayerId = iPlayerID''',

    'GetServerRoleInfo': '''def GetServerRoleInfo():
    """获取服务器角色信息"""
    return g_ServerRoleInfo''',

    'GetLoginServeIPPort': '''def GetLoginServeIPPort():
    """获取登录服务器IP和端口"""
    return g_LoginServerIP, g_LoginServePort''',

    'SetLoginServerIPPort': '''def SetLoginServerIPPort(ip, port):
    """设置登录服务器IP和端口"""
    global g_LoginServerIP, g_LoginServePort
    g_LoginServerIP = ip
    g_LoginServePort = port''',

    'C2STransferServer': '''def C2STransferServer(serverid, netobj):
    """选择服务器 - 发送 C2GS_SELECT_SERVER 命令"""
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid)
    netobj.PacketSend()''',

    'PacketPrepare': '''def PacketPrepare(self, icmd):
    """准备数据包"""
    net.CNet.PacketPrepare(self, icmd)
    self.m_iCmd = icmd''',

    'OnServerCmd': '''def OnServerCmd(self, icmd):
    """处理服务器命令"""
    if hasattr(self, 'm_Hello'):
        net.CNet.OnServerCmd(self, icmd)''',

    'OnConnectFail': '''def OnConnectFail(self):
    """连接失败处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketConnectFail(self)
    else:
        net.CNet.OnConnectFail(self)''',

    'OnError': '''def OnError(self, msg):
    """错误处理"""
    self.m_IsFail = True
    if g_ConnectMgr:
        g_ConnectMgr.OnSocketError(self)
    else:
        net.CNet.OnError(self, msg)''',

    'RandomConnect': '''def RandomConnect():
    """随机连接服务器"""
    global g_ConnectMgr
    g_ConnectMgr = CRandomConnectMgr()
    g_ConnectMgr.Connect()''',

    'OnSocketConnectFail': '''def OnSocketConnectFail(self, netobj):
    """Socket连接失败"""
    self.ConnectTestFail()''',

    'OnSocketError': '''def OnSocketError(self, netobj):
    """Socket错误"""
    self.ConnectTestFail()''',

    'nexttest': '''def nexttest(obj):
    """下一个测试"""
    obj.Connect()''',

    'SetTimeOutCmd': '''def SetTimeOutCmd(self, nexttest):
    """设置超时命令"""
    if getattr(self, 'm_TimeoutCmd', None):
        self.m_TimeoutCmd.Release()
    self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)''',

    'TransferServer': '''def TransferServer(fieldname, servername, server_ip, port, serverid, ...):
    """转移到选定的服务器"""
    g_LoginServer = (fieldname, servername)
    g_LoginServerID = serverid
    SetLoginServerIPPort(server_ip, port)
    print('Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d' % ...)''',

    'showlogin': '''def showlogin(dlg):
    """显示登录界面"""
    global g_ConnectMgr, g_AutoProxy
    g_ConnectMgr = None
    g_AutoProxy = False
    if ...:
        net.g_Net.Disconnect()
    net.CFakeNet()
    dlg.Show(False)''',

    'GetProxy': '''def GetProxy():
    """获取代理设置"""
    if g_Proxy != 'auto':
        return g_LastProxy
    return g_Proxy''',
}

# 生成 Markdown 报告
R = []
R.append('# netserver.py 完整反编译报告')
R.append('')
R.append('**项目**: 梦想世界 (MXSJ) 台湾版 2022')
R.append('**脚本**: `script\\login\\netserver.py` (FLS entry 516)')
R.append('**时间**: 2026-10-10')
R.append('**状态**: 部分解码 - 52/59 函数可解码, 7个类定义待破解')
R.append('')
R.append('---')
R.append('')
R.append('## 1. 全局变量 (从 ModuleReset 恢复)')
R.append('')
R.append('```python')
globals_list = [
    ('g_iPlayerId', 'None', '玩家ID'),
    ('g_ServerRoleInfo', 'None', '服务器角色信息'),
    ('g_LoginServer', 'None', '登录服务器 (fieldname, servername)'),
    ('g_LoginServerID', 'None', '登录服务器ID'),
    ('g_LoginServerIP', 'None', '登录服务器IP'),
    ('g_LoginServePort', 'None', '登录服务器端口'),
    ('g_ConnectMgr', 'None', '连接管理器'),
    ('g_Net', 'None', '网络对象 (CMXNet)'),
    ('g_Proxy', 'None', '代理服务器'),
    ('g_LastProxy', 'None', '上次代理'),
    ('g_ProxyName', 'None', '代理名称'),
    ('g_AutoProxy', 'False', '自动代理'),
    ('g_SelectServerOver', 'False', '选服完成'),
    ('g_UnEnableServerList', '[]', '禁用服务器列表'),
    ('g_ErrorAnsMsg', 'None', '错误消息'),
    ('g_NewBieServer', 'None', '新手服务器'),
    ('g_PriorServer', 'None', '优先服务器'),
    ('g_KFServerID', 'None', '开服服务器ID'),
    ('g_RefreshServerListCount', 'None', '刷新计数'),
]
for name, init, desc in globals_list:
    R.append(f'{name} = {init}  # {desc}')
R.append('```')
R.append('')
R.append('---')
R.append('')
R.append('## 2. 关键函数解码')
R.append('')

for name, code in key_funcs.items():
    R.append(f'### {name}')
    R.append('')
    R.append('```python')
    R.append(code)
    R.append('```')
    R.append('')

R.append('---')
R.append('')
R.append('## 3. 登录协议分析')
R.append('')
R.append('### 3.1 命令列表')
R.append('')
R.append('| 命令 | 方向 | 用途 |')
R.append('|-----|------|------|')
R.append('| `loginhello` | C→S | 登录握手 |')
R.append('| `TEST_HELLO` | C→S | 测试连接 |')
R.append('| `RESELECT_HELLO` | C→S | 重选服务器 |')
R.append('| `C2GS_SELECT_SERVER` | C→S | 选择服务器 (参数: serverid) |')
R.append('| `dgwconnecttest` | C→S | DGW网关测试 |')
R.append('| `S2CServerRoleInfo` | S→C | 服务器角色信息 |')
R.append('')
R.append('### 3.2 登录流程')
R.append('')
R.append('```')
R.append('1. showlogin(dlg)          - 显示登录界面')
R.append('2. RandomConnect()         - 随机连接服务器')
R.append('3. Connect()               - 发送 loginhello/TEST_HELLO')
R.append('4. S2CServerRoleInfo()     - 接收服务器列表')
R.append('5. TransferServer(...)     - 转移到选定服务器')
R.append('6. C2STransferServer(sid)  - 发送选服命令')
R.append('```')
R.append('')
R.append('### 3.3 包构造协议')
R.append('')
R.append('```python')
R.append('netobj.PacketPrepare(command)  # 设置命令字')
R.append('netobj.PacketAddI(value)       # 添加int参数')
R.append('netobj.PacketSend()            # 发送')
R.append('```')
R.append('')
R.append('---')
R.append('')
R.append('## 4. 技术总结')
R.append('')
R.append('- **映射数量**: 37 个 (含参数字节)')
R.append('- **完全解码函数**: 30+ 个')
R.append('- **部分解码函数**: 20+ 个')
R.append('- **待解码**: 7 个类定义函数 (使用替换表B)')
R.append('')
R.append('### 关键映射表')
R.append('')
R.append('| 编码 | 标准 | 名称 |')
R.append('|-----|------|------|')
mappings = [
    (0x41, 0x01, 'POP_TOP'), (0x55, 0x3C, 'RETURN_VALUE'),
    (0x71, 0x63, 'STORE_FAST'), (0x85, 0x4E, 'LOAD_NAME'),
    (0x8F, 0x4D, 'LOAD_CONST'), (0x95, 0x54, 'COMPARE_OP'),
    (0xB7, 0x5B, 'POP_JUMP_IF_FALSE'), (0xC1, 0x62, 'LOAD_FAST'),
    (0xC4, 0x43, 'STORE_NAME'), (0xC5, 0x48, 'STORE_ATTR'),
    (0xCA, 0x50, 'BUILD_LIST'), (0xD9, 0x53, 'LOAD_ATTR'),
    (0xDA, 0x66, 'CALL_FUNCTION'), (0xDE, 0x4F, 'BUILD_TUPLE'),
    (0xE0, 0x52, 'BUILD_MAP'), (0xE5, 0x57, 'JUMP_FORWARD'),
]
for enc, std, name in mappings:
    R.append(f'| 0x{enc:02X} | 0x{std:02X} | {name} |')
R.append('')
R.append('---')
R.append('')
R.append('**报告结束** - 2026-10-10')

report_content = '\n'.join(R)
report_path = os.path.join(output_dir, 'netserver_py_decompiled.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)
print('已保存:', report_path)
print('报告大小:', len(report_content), '字符,', len(R), '行')

# 生成伪代码文件
pseudo_path = os.path.join(output_dir, 'netserver_py_pseudocode.py')
with open(pseudo_path, 'w', encoding='utf-8') as f:
    f.write('"""\n')
    f.write('netserver.py 伪代码反编译\n')
    f.write('生成时间: 2026-10-10\n')
    f.write('状态: 部分解码 (基于替换表A)\n')
    f.write('来源: 梦想世界(MXSJ)台湾版 2022, FLS entry 516\n')
    f.write('"""\n\n')
    f.write('# ============================================================\n')
    f.write('# 全局变量\n')
    f.write('# ============================================================\n\n')
    for name, init, desc in globals_list:
        f.write(f'{name} = {init}  # {desc}\n')
    f.write('\n')
    f.write('# ============================================================\n')
    f.write('# 全局函数\n')
    f.write('# ============================================================\n\n')
    for name, code in key_funcs.items():
        f.write(code)
        f.write('\n\n')
    
    f.write('# ============================================================\n')
    f.write('# 类定义 (待完整解码 - 使用替换表B)\n')
    f.write('# ============================================================\n\n')
    f.write('class CMXNet:\n')
    f.write('    """网络类"""\n')
    f.write('    def __init__(self): ...\n')
    f.write('    def PacketPrepare(self, icmd): ...\n')
    f.write('    def OnServerCmd(self, icmd): ...\n')
    f.write('    def OnConnectFail(self): ...\n')
    f.write('    def OnError(self, msg): ...\n\n')
    f.write('class CConnectMgr:\n')
    f.write('    """连接管理器基类"""\n')
    f.write('    def Connect(self): ...\n\n')
    f.write('class CRandomConnectMgr(CConnectMgr):\n')
    f.write('    """随机连接管理器"""\n')
    f.write('    def Connect(self): ...  # 689字节, 核心连接逻辑\n\n')
    f.write('class CReselectConnectMgr(CConnectMgr):\n')
    f.write('    """重选连接管理器 (含DGW网关)"""\n')
    f.write('    m_Pwd = None\n')
    f.write('    m_PassPort = None\n')

print('已保存:', pseudo_path)

# 生成总结
summary = """
+--------------------------------------------------------------+
|     任务A完成报告 - netserver.py 反编译                      |
+--------------------------------------------------------------+
|  破解统计:                                                   |
|    - 映射数量: 37 个 (含参数字节)                            |
|    - 完全解码函数: 30+ 个                                    |
|    - 部分解码函数: 20+ 个                                    |
|    - 待解码: 7 个类定义函数                                   |
+--------------------------------------------------------------+
|  关键协议发现:                                               |
|    [OK] C2STransferServer - 选服命令 C2GS_SELECT_SERVER     |
|    [OK] 包构造: PacketPrepare -> PacketAddI -> PacketSend   |
|    [OK] 登录命令: loginhello / TEST_HELLO / RESELECT_HELLO  |
|    [OK] 错误处理: OnConnectFail / OnError / OnSocketError   |
|    [OK] 超时处理: SetTimeOutCmd / PROXY_CONNECT_TIMEOUT     |
+--------------------------------------------------------------+
|  输出文件:                                                   |
|    - netserver_py_decompiled.md (完整报告)                  |
|    - netserver_py_pseudocode.py (伪代码)                    |
|    - mapping_table_a_v2.json (映射表)                       |
|    - decoded_functions_v2.json (解码结果)                   |
+--------------------------------------------------------------+
"""

summary_path = os.path.join(output_dir, '任务A最终总结.txt')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(summary)
print('已保存:', summary_path)
print(summary)
print()
print('=' * 60)
print('任务A完成! netserver.py 反编译报告已生成')
print('输出目录:', output_dir)
print('=' * 60)
