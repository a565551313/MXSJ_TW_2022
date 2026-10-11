# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\netserver.py
import interface, net, C_sys

def ModuleReset():
    global g_AutoProxy
    global g_ConnectMgr
    global g_ErrorAnsMsg
    global g_KFServerID
    global g_LastProxy
    global g_LoginServePort
    global g_LoginServer
    global g_LoginServerID
    global g_LoginServerIP
    global g_NewBieServer
    global g_PriorServer
    global g_PriorServerInfo
    global g_Proxy
    global g_ProxyName
    global g_RefreshServerListCount
    global g_SelectServerOver
    global g_ServerRoleInfo
    global g_UnEnableServerList
    global g_iPlayerId
    g_ServerRoleInfo = {}
    g_NewBieServer = {}
    g_PriorServer = None
    g_PriorServerInfo = None
    g_LoginServer = None
    g_LoginServerID = None
    g_KFServerID = None
    g_LoginServerIP = None
    g_LoginServePort = None
    g_ConnectMgr = None
    g_Proxy = None
    g_LastProxy = None
    g_ProxyName = ''
    g_AutoProxy = False
    g_SelectServerOver = False
    g_RefreshServerListCount = 0
    g_UnEnableServerList = []
    g_ErrorAnsMsg = None
    g_iPlayerId = 0
    return


ModuleReset()

def SetPlayerID(iPlayerID):
    global g_iPlayerId
    g_iPlayerId = iPlayerID
    return


def GetPlayerID():
    return g_iPlayerId


def RefreshServerInfo():
    import permission, cfg, net, misc
    if not permission.GetSpecialVersion() and not permission.GetOverdoVersion():
        try:
            tm = float(cfg.GetData('mx.ini', 'Game', 'refreshserver'))
        except:
            tm = None
        else:
            now = misc.Time()
            if tm is None or tm > now or now - tm > 1200:
                import selectserver
                selectserver.Refresh(None)

    def getMsg(data, flag):
        global g_ErrorAnsMsg
        if flag and len(data) > 0:
            try:
                (head, body) = data.split('\r\n\r\n')
                dErrorInfo = {}
                lstErrorInfo = body.split('\r\n')
                for sInfo in lstErrorInfo:
                    (sServerID, sErrorInfo) = sInfo.split(':', 1)
                    dErrorInfo[sServerID] = sErrorInfo

                g_ErrorAnsMsg = dErrorInfo
            except ValueError:
                pass

        return

    web = cfg.GetData('update.ini', 'Setting', 'BulletinURL')
    net.CHttpObject(web, 'get', getMsg)
    return


def GetErrorAnsMsg():
    return g_ErrorAnsMsg


def SetUnEnterServerList(unEnableServerList):
    global g_UnEnableServerList
    g_UnEnableServerList = unEnableServerList
    return


def GetUnEnterServerList():
    return g_UnEnableServerList


def ClearUnEnterServerList():
    global g_UnEnableServerList
    g_UnEnableServerList = []
    return


def IsSelectServerOver():
    return g_SelectServerOver


def SetSelectServerOver(isOver):
    global g_SelectServerOver
    g_SelectServerOver = isOver
    return


def SetConnectedProxy(proxy):
    global g_LastProxy
    g_LastProxy = proxy
    return


def GetConnectedProxy():
    return g_LastProxy


def GetProxy():
    if g_Proxy == 'auto':
        return g_LastProxy
    return g_Proxy


def SetProxy(proxy):
    global g_Proxy
    import cfg
    g_Proxy = proxy
    try:
        cfg.SaveData('mx.ini', 'Game', 'proxy', proxy)
    except:
        pass

    return


def GetProxyName():
    return g_ProxyName


def SetProxyName(proxyName):
    global g_ProxyName
    g_ProxyName = proxyName
    return


def GetProxyNameByProxy(ipPort):
    import selectserver
    (_, _, proxyLst) = selectserver.GetServerInfo()
    proxyname = ''
    for proxydata in proxyLst:
        if proxydata['ipPort'] == ipPort:
            if proxydata['type'] == 1:
                proxyname = '電信'
            elif proxydata['type'] == 2:
                proxyname = '網通'
            elif proxydata['type'] == 3:
                proxyname = '教育網'
            proxyname = proxyname + proxydata.get('note', '')
            return proxyname

    return proxyname


def SetServerRoleInfo(infos):
    global g_ServerRoleInfo
    import loginin, selectserver
    g_ServerRoleInfo = infos
    if hasattr(net.g_Net, 'm_ServerInfo'):
        (field, name, ip, port, serverid) = net.g_Net.m_ServerInfo
        if serverid not in GetUnEnterServerList() or serverid in g_ServerRoleInfo:
            TransferServer(field, name, ip, port, serverid, autoenterselrole=True)
            return
    loginin.OnLogin()
    loginin.Show(False)
    return


def GetServerRoleInfo():
    return g_ServerRoleInfo


def SetLoginServerIPPort(ip, port):
    global g_LoginServePort
    global g_LoginServerIP
    g_LoginServerIP = ip
    g_LoginServePort = port
    return


def GetLoginServeIPPort():
    return (
     g_LoginServerIP, g_LoginServePort)


def GetLoginServer():
    return g_LoginServer


def TransferServer(fieldname, servername, server_ip, port, serverid, autoenterselrole=False):
    global g_LoginServer
    global g_LoginServerID
    print 'Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d' % (fieldname, servername, server_ip, port, serverid)
    g_LoginServer = (
     fieldname, servername)
    g_LoginServerID = serverid
    SetLoginServerIPPort(server_ip, port)
    import restartsave
    restartsave.SetLoginServer(fieldname, servername)
    SetSelectServerOver(True)
    C2STransferServer(serverid)
    ShowConnectingDlg()
    return


def ShowConnectingDlg():
    import net, selectserver, loginin

    def showlogin(dlg):
        global g_AutoProxy
        global g_ConnectMgr
        g_ConnectMgr = None
        g_AutoProxy = False
        if net.g_Net:
            net.g_Net.Disconnect()
            net.g_Net = net.CFakeNet()
        selectserver.Show(False)
        loginin.Show(True)
        return

    import commondialog, netlogin
    msgbox = commondialog.ShowMessageBox('正在連接服務器中....', '返回', showlogin)
    return


def S2CServerRoleInfo(netobj):
    cnt = netobj.UnpackInt(1)
    roleinfo = {}
    for i in xrange(cnt):
        serverid = netobj.UnpackInt(4)
        rolenum = netobj.UnpackInt(1)
        roleinfo[serverid] = rolenum

    SetServerRoleInfo(roleinfo)
    return


def C2STransferServer(serverid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid, 2)
    netobj.PacketSend()
    return


class CMXNet(net.CNet):

    def __init__(self, ip, port, iType=0):
        net.CNet.__init__(self, ip, port)
        self.m_NetType = iType
        return

    def PacketPrepare(self, icmd):
        net.CNet.PacketPrepare(self, icmd)
        self.m_iCmd = icmd
        return

    def OnServerCmd(self, icmd):
        if hasattr(self, 'm_Hello'):
            net.CNet.OnServerCmd(self, icmd)
        return

    def OnConnectFail(self):
        self.m_IsFail = True
        if g_ConnectMgr:
            g_ConnectMgr.OnSocketConnectFail(self)
        else:
            net.CNet.OnConnectFail(self)
        return

    def OnError(self, msg=None):
        self.m_IsFail = True
        if g_ConnectMgr:
            g_ConnectMgr.OnSocketError(self)
        else:
            net.CNet.OnError(self, msg)
        return


class CConnectMgr(interface.CBaseObject):

    def __init__(self):
        interface.CBaseObject.__init__(self, None)
        self.m_Nets = []
        import selectserver
        (self.m_ServerInfo, _, self.m_ProxyInfo) = selectserver.GetServerInfo()
        return

    def Connect(self):
        return

    def ConnectTestFail(self):
        global g_RefreshServerListCount
        import commondialog, loginin, selectserver
        if self.IsConnectTestFail():
            sServerName = loginin.GetSelectServer()
            if g_ErrorAnsMsg:
                if sServerName in g_ErrorAnsMsg:
                    msgtxt = g_ErrorAnsMsg[sServerName]
                else:
                    msgtxt = g_ErrorAnsMsg['default']
            else:
                msgtxt = '連接服務器失敗'
            if g_RefreshServerListCount < 3:
                commondialog.ShowNewMessageBox(msgtxt, '確定', selectserver.Refresh)
                g_RefreshServerListCount += 1
            else:
                commondialog.ShowNewMessageBox(msgtxt, '確定')
            loginin.CheckShowRefreshServer()
        return

    def OnSocketConnectFail(self, netobj):
        self.ConnectTestFail()
        return

    def OnSocketError(self, netobj):
        self.ConnectTestFail()
        return

    def IsConnectTestFail(self):
        for netobj in self.m_Nets:
            if netobj.m_IsFail == False:
                return False

        return True


class CRandomConnectMgr(CConnectMgr):
    PROXY_CONNECT_TIMEOUT = 15

    def __init__(self):
        CConnectMgr.__init__(self)
        self.m_Time = 0
        self.m_AllTry = False
        return

    def GetServerInfo(self, district, name):
        import selectserver
        if self.m_ServerInfo.get(district):
            for serverdata in self.m_ServerInfo[district]:
                if serverdata['name'] == name:
                    return serverdata

        return

    def GetTestProxyList(self):
        global g_AutoProxy
        import random
        if not self.m_ProxyInfo:
            return []
        ipPort = GetProxy()
        name = GetProxyName()
        extlist = [{'note': '', 'ipPort': '', 'type': 0}]
        if name != '自動選擇':
            extlist = [{'note': name, 'ipPort': ipPort, 'type': 0}] + extlist
        else:
            g_AutoProxy = True
        proxylist = extlist + self.m_ProxyInfo
        for t in xrange(self.m_Time):
            proxylist.pop(0)

        return proxylist

    def GetTestServerList(self):
        import random
        if not self.m_ServerInfo:
            return
        IPs = []
        if g_PriorServer:
            try:
                (district, name) = g_PriorServer
            except:
                return
            else:
                sinfo = self.GetServerInfo(district, name)
                if sinfo:
                    IPs.append(sinfo)
        else:
            dianXinList, WangTongList = [], []
            for (district, districtData) in self.m_ServerInfo.iteritems():
                if district.find('電信') >= 0:
                    dianXinList += districtData
                elif district.find('網通') >= 0:
                    WangTongList += districtData

            random.shuffle(dianXinList)
            random.shuffle(WangTongList)
            IPs += dianXinList[:5]
            IPs += WangTongList[:2]
        return IPs

    def Connect(self):
        import selectserver, loginhello
        serverlist = self.GetTestServerList()
        proxylist = self.GetTestProxyList()
        if not serverlist:
            selectserver.Refresh(None)
            return
        if not proxylist:
            return
        proxydata = proxylist[0]
        proxy, note = proxydata['ipPort'], proxydata.get('note')
        for d in serverlist:
            (name, ip, port, serverid, district) = (
             d['name'], d['ip'], d['port'], d['serverid'], d['district'])
            LOG('嘗試連接!!!', name, serverid, bool(proxy))
            netobj = CMXNet(ip, port, iType=loginhello.TEST_HELLO)
            netobj.m_Hello = False
            netobj.m_IsFail = False
            netobj.m_ProxyName = ''
            netobj.m_SvrName = name
            netobj.m_ServerInfo = (district, name, ip, port, serverid)
            self.m_Nets.append(netobj)
            if proxy:
                LOG_DEBUG('連接代理!!!!!', proxy, note)
                p = proxy.find(':')
                netobj.m_Proxy = proxy
                netobj.Connect(proxy[:p], int(proxy[p + 1:]))
                iplst = ip.split('.')
                for i in xrange(4):
                    netobj.NakedSend(chr(int(iplst[i])))

                netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
            else:
                netobj.Connect(ip, port)

        ShowConnectingDlg()
        self.m_Time += 1
        self.SetTimeOutCmd()
        if self.m_Time - 1 != 0 or g_AutoProxy:
            self.Connect()
        return

    def SetTimeOutCmd(self):

        def nexttest(obj):
            obj.Connect()
            return

        if getattr(self, 'm_TimeoutCmd', None):
            self.m_TimeoutCmd.Release()
        self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)
        return

    def ConnectTestFail(self):
        if self.IsConnectTestFail() and self.m_AllTry == False:
            self.m_Time = 0
            self.m_AllTry = True
            self.Connect()
        else:
            CConnectMgr.ConnectTestFail(self)
        return


class CReselectConnectMgr(CConnectMgr):

    def __init__(self, serverID, idx, pwd):
        CConnectMgr.__init__(self)
        self.m_ServerID = serverID
        self.m_Idx = idx
        self.m_Pwd = pwd
        return

    def Connect(self):
        lst = []
        import selectserver, loginhello
        (serverData, _, _) = selectserver.GetServerInfo()
        for d in serverData.values():
            for slist in d:
                if slist['district'] == '推荐區':
                    continue
                if slist['serverid'] == self.m_ServerID:
                    lst.append(slist)

        self.m_Nets = []
        for d in lst:
            (name, ip, port, serverid, district) = (
             d['name'], d['ip'], d['port'], d['serverid'], d['district'])
            print '嘗試轉服連接!!!', name, ip, port, serverid, district
            netobj = CMXNet(ip, port, iType=loginhello.RESELECT_HELLO)
            netobj.m_Hello = False
            netobj.m_IsFail = False
            netobj.m_ProxyName = ''
            netobj.m_SvrName = name
            netobj.m_ServerInfo = (district, name, ip, port, serverid)
            netobj.m_PassPort = (self.m_Idx, self.m_Pwd)
            if isinstance(district, str):
                netobj.m_EntryName = district
            proxy = GetProxy()
            if proxy:
                print '連接代理!!!!!', proxy
                p = proxy.find(':')
                proxyName = GetProxyName()
                if isinstance(proxyName, str):
                    netobj.m_ProxyName = proxyName
                netobj.Connect(proxy[:p], int(proxy[p + 1:]))
                iplst = ip.split('.')
                for i in xrange(4):
                    netobj.NakedSend(chr(int(iplst[i])))

                netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
            else:
                netobj.Connect(ip, port)
            self.m_Nets.append(netobj)

        return


def RandomConnect():
    global g_ConnectMgr
    g_ConnectMgr = CRandomConnectMgr()
    g_ConnectMgr.Connect()
    return


def ReselectServerConnect(serverID, idx, pwd):
    import main
    if main.g_IsDgwConnect:
        DgwReselectServerConnect(serverID, idx, pwd)
    else:
        NormalReselectServerConnect(serverID, idx, pwd)
    return


def DgwReselectServerConnect(serverID, idx, pwd):
    import dgwconnecttest
    dgwconnecttest.g_DGWRsLoginInfo = (serverID, idx, pwd)
    dgwconnecttest.ConnectTest(dgwconnecttest.DGW_RESELECTCONNECT, (serverID, idx, pwd))
    return


def NormalReselectServerConnect(serverID, idx, pwd):
    global g_ConnectMgr
    g_ConnectMgr = CReselectConnectMgr(serverID, idx, pwd)
    g_ConnectMgr.Connect()
    return


def ProcessServerCmd():
    if g_ConnectMgr:
        for netobj in g_ConnectMgr.m_Nets:
            if netobj.m_IsFail == False:
                netobj.ProcessServerCmd()
                if hasattr(netobj, 'm_Hello') and netobj.m_Hello:
                    break

    return


return
