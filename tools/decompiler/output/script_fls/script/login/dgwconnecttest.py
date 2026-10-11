# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dgwconnecttest.py
import interface, netserver, dgwnet, selectserver, misc
DGW_TIMEOUT = 5
MAXTRY = 1
DGW_LOGINCONNECT = 1
DGW_RESELECTCONNECT = 2
DGW_KUAFUREALCONNECT = 4
DGW_SHUNLIANCONNECT = 5
CONNSTATE_SUCC = 0
CONNSTATE_TEST = 1
CONNSTATE_FAIL = 2
g_DgwMgr = None
g_DGWLoginInfo = None
g_DGWKuaFuInfo = None
g_DGWRsLoginInfo = None
g_ConnectState = CONNSTATE_SUCC
g_IsUseDgw = True
g_DgwResetFlag = True

def ModuleReset():
    global g_DGWKuaFuInfo
    global g_DGWLoginInfo
    global g_DGWRsLoginInfo
    global g_DgwMgr
    g_DgwMgr = None
    g_DGWLoginInfo = None
    g_DGWKuaFuInfo = None
    g_DGWRsLoginInfo = None
    return


def SendConnectTimeOutLog():
    dgwnet.ServerDGWError(dgwnet.ERRTYPE_FAILE)
    dgwnet.StartEcho()
    return


def SetConnectState(iState):
    global g_ConnectState
    g_ConnectState = iState
    return


def IsConnectSucc():
    return g_ConnectState == CONNSTATE_SUCC


def IsConnectFail():
    return g_ConnectState == CONNSTATE_FAIL


def IsConnectTest():
    return g_ConnectState == CONNSTATE_TEST


class CDGWConnectTestBase(interface.CBaseObject):

    def __init__(self):
        interface.CBaseObject.__init__(self, interface.MainPanel)
        (self.m_ServerInfo, _, _) = selectserver.GetServerInfo()
        self.m_Nets = []
        self.m_TryPrivateIP = True
        self.m_RequestDgwTime = 0
        self.m_TimeOutCmd = None
        self.m_SelServerAttr = None
        self.m_BaseInfo = None
        self.m_DGWToken = '0'
        self.m_DGWData = {}
        self.m_RetryNum = MAXTRY
        return

    def GetTestServerList(self):
        return

    def Connect(self):
        args = self.GetTestServerList()
        if not args:
            return
        self.m_SelServerAttr = args
        self.m_BaseInfo = args['dgwinfo']
        self.m_RequestDgwTime = misc.Time()
        self.TryDGWRequest()
        return

    def TryDGWRequest(self):
        (sIp, iPort, iServerID, iType) = self.m_BaseInfo
        dgwnet.StartWorking(sIp, iPort, iServerID, iType, self.OnDGWRequestData)
        return

    def OnDGWRequestData(self, data):
        import json, dgw
        iNowTime = int(round(misc.Time() - self.m_RequestDgwTime, 3) * 1000)
        sLog = '獲取DGW鏈接耗時：%s' % iNowTime
        LOG(sLog)
        dgwnet.UpLoadLog(sLog)
        try:
            self.m_DGWData = json.read(data)
        except:
            self.m_DGWData = {}

        self.ReleaseTimer()
        self.m_DGWToken = self.m_DGWData.get('token', '0')
        if self.m_DGWToken is None:
            self.m_DGWToken = '0'
        dgwnet.g_SaveInfo['token'] = self.m_DGWToken
        if self.m_DGWToken == '0':
            result = self.m_DGWData.get('result', 0)
            desc = self.m_DGWData.get('desc', '')
            if desc:
                LOG(desc)
            if self.m_RetryNum > 0 and result != dgw.DGW_HTTP_SERVERS_READ_FAILED:
                self.m_RetryNum -= 1
                self.TryDGWRequest()
            else:
                self.m_RetryNum = MAXTRY
                dgwnet.ServerDGWError(dgwnet.ERRTYPE_GET_DGW_ERR)
        else:
            self.m_RetryNum = MAXTRY
            GetDgwMgr().UpdateDGWData(self.m_DGWData['servers'])
            self.DGWTCPConnect()
        return

    def DGWTCPConnect(self):
        if self.m_DGWToken == '0':
            return
        self.TryToConnect()
        return

    def TryToConnect(self):
        (sIp, iPort, iServerID, iType) = self.m_BaseInfo
        lTcpList = GetDgwMgr().GetNextConnectData()
        if lTcpList:
            for lTcp in lTcpList:
                netobj = self.CreateTestNet()
                netobj.ConnectServer(lTcp)
                self.m_Nets.append(netobj)

            self.SetTimeOutCmd(DGW_TIMEOUT, self.OnConnectTimeOut)
            self.UpdateConnectState()
        else:
            self.ReleaseTimer()
            self.UpdateConnectState()
            dgwnet.OldConnectTest(iType)
            dgwnet.UpLoadLog('dgw接入服無返回鏈路')
        return

    def UpdateConnectState(self):
        if self.m_Nets:
            LOG('更新狀態 test')
            SetConnectState(CONNSTATE_TEST)
        else:
            LOG('更新狀態 fail')
            SetConnectState(CONNSTATE_FAIL)
        return

    def CreateTestNet(self):
        import hero
        (sIp, iPort, iServerID, iType) = self.m_BaseInfo
        netobj = dgwnet.CDGWNet(sIp, iPort, Itype=iType)
        netobj.m_Hello = False
        netobj.m_IsFail = False
        netobj.m_ProxyName = ''
        netobj.m_HeroID = hero.g_ID
        netobj.m_DGWToken = self.m_DGWToken
        for (name, value) in self.m_SelServerAttr.iteritems():
            setattr(netobj, name, value)

        return netobj

    def TryDGWPrivateIP(self):
        if not self.m_TryPrivateIP:
            return False
        self.m_TryPrivateIP = False
        isTry = False
        for netobj in self.m_Nets:
            if netobj.DGWConnectByPrivateIP():
                isTry = True

        return isTry

    def SetTimeOutCmd(self, iTime=DGW_TIMEOUT, callback=SendConnectTimeOutLog):
        import timer
        self.ReleaseTimer()
        self.m_TimeOutCmd = timer.Timer(iTime, callback, 1)
        return

    def ReleaseTimer(self):
        if self.m_TimeOutCmd:
            self.m_TimeOutCmd.Release()
            self.m_TimeOutCmd = None
        return

    def OnConnectTimeOut(self):
        if not GetDgwMgr().HasNextConnectData():
            LOG('連接超時:OnConnectTimeOut')
            SendConnectTimeOutLog()
            dgwnet.OldConnectTest(self.m_BaseInfo[3])
        else:
            LOG('嘗試下一步代理連接:OnConnectTimeOut')
            self.DGWTCPConnect()
        return

    def OnSocketConnectFail(self, netobj):
        if self.IsConnectTestFail():
            LOG('連接失敗:dgw.OnSocketConnectFail')
            netobj.m_IsFail = True
            dgwnet.ServerDGWError(dgwnet.ERRTYPE_FAILE)
        elif self.IsNetConnectFail():
            LOG('嘗試下一步代理連接:OnSocketConnectFail')
            self.DGWTCPConnect()
        return

    def OnSocketError(self, netobj):
        if self.IsConnectTestFail():
            LOG('連接失敗:dgw.OnSocketError')
            netobj.m_IsFail = True
            dgwnet.ServerDGWError(dgwnet.ERRTYPE_FAILE)
        elif self.IsNetConnectFail():
            LOG('嘗試下一步代理連接:OnSocketError')
            self.DGWTCPConnect()
        return

    def IsConnectTestFail(self):
        return self.IsNetConnectFail() and not GetDgwMgr().HasNextConnectData()

    def IsNetConnectFail(self):
        for netobj in self.m_Nets:
            if netobj.m_IsFail == False:
                return False

        return True


class CDGWConnectTest(CDGWConnectTestBase):

    def GetServerInfo(self, district, name):
        if self.m_ServerInfo.get(district):
            for serverdata in self.m_ServerInfo[district]:
                if serverdata['name'] == name:
                    return serverdata

        return

    def GetRandomServer(self):
        import random
        serverinfo = []
        for (district, district_data) in self.m_ServerInfo.iteritems():
            for sinfo in district_data:
                serverid = int(sinfo['serverid'])
                servername = sinfo['name']
                ip = sinfo['ip']
                port = sinfo['port']
                serverinfo.append((district, servername, ip, int(port), serverid))

        return random.choice(serverinfo)

    def GetTestServerList(self):
        if not self.m_ServerInfo:
            return
        IPs = None
        if netserver.g_PriorServer:
            try:
                (district, name) = netserver.g_PriorServer
                sinfo = self.GetServerInfo(district, name)
                if sinfo:
                    serverid = int(sinfo['serverid'])
                    servername = sinfo['name']
                    ip = sinfo['ip']
                    port = sinfo['port']
                    ipdata = (district, servername, ip, int(port), serverid)
                    IPs = ipdata
            except:
                IPs = None

        if not IPs:
            netserver.g_PriorServer = None
            IPs = self.GetRandomServer()
        return self.AnalyseIPs(IPs)

    def AnalyseIPs(self, IPs):
        global g_DGWLoginInfo
        (district, servername, ip, port, serverid) = IPs
        g_DGWLoginInfo = (
         district, servername, ip)
        IPs = {'dgwinfo': (
                     ip, int(port), serverid, DGW_LOGINCONNECT), 
           'm_ServerInfo': (
                          district, servername, ip, int(port), serverid), 
           'm_SvrName': servername, 
           'm_EntryName': (district[:4] + '入口'), 
           'm_IsLogin': True}
        return IPs

    def Connect(self):
        CDGWConnectTestBase.Connect(self)
        return


class CDGWKuaFuRealConnectTest(CDGWConnectTestBase):

    def __init__(self, args):
        CDGWConnectTestBase.__init__(self)
        (ip, port, serverid, proxy, idx, pwd) = args
        self.m_Proxy = proxy
        self.m_Idx = idx
        self.m_Pwd = pwd
        self.m_ServerList = (ip, port, serverid)
        return

    def GetTestServerList(self):
        if not self.m_ServerList:
            return
        (ip, port, serverid) = self.m_ServerList
        IPs = {'dgwinfo': (
                     ip, int(port), serverid, DGW_KUAFUREALCONNECT), 
           'm_PassPort': (
                        self.m_Idx, self.m_Pwd), 
           'm_EntryName': '代理'}
        import misc
        if misc.IsKuafuServerID(serverid):
            IPs['m_DstIPPort'] = (
             ip, port)
        return IPs

    def Connect(self):
        LOG('[ZQDB]KF time=2')
        if not self.m_ServerList:
            return
        CDGWConnectTestBase.Connect(self)
        return

    def CreateTestNet(self):
        (sIp, iPort, iServerID, iType) = self.m_BaseInfo
        netobj = dgwnet.CDGWNet(sIp, iPort, Itype=iType)
        netobj.m_Hello = False
        netobj.m_IsFail = False
        netobj.m_Idx = self.m_Idx
        netobj.m_Pwd = self.m_Pwd
        netobj.m_ReConnect = True
        netobj.m_Proxy = self.m_Proxy
        netobj.m_ProxyName = ''
        netobj.m_DGWToken = self.m_DGWToken
        for (name, value) in self.m_SelServerAttr.iteritems():
            setattr(netobj, name, value)

        return netobj


class CDGWReselectConnectTest(CDGWConnectTest):

    def __init__(self, args):
        CDGWConnectTestBase.__init__(self)
        (serverid, idx, pwd) = args
        self.m_ServerID = serverid
        self.m_Idx = idx
        self.m_Pwd = pwd
        return

    def GetTestServerList(self):
        IPs = None
        for (district, districtData) in self.m_ServerInfo.iteritems():
            for serverdata in districtData:
                if int(serverdata['serverid']) == self.m_ServerID:
                    IPs = (
                     district, serverdata['name'], serverdata['ip'], int(serverdata['port']), self.m_ServerID)
                    break

        print IPs
        return self.AnalyseIPs(IPs)

    def AnalyseIPs(self, IPs):
        global g_DGWLoginInfo
        (district, servername, ip, port, serverid) = IPs
        g_DGWLoginInfo = (
         district, servername, ip)
        IPs = {'dgwinfo': (
                     ip, int(port), serverid, DGW_RESELECTCONNECT), 
           'm_ServerInfo': (
                          district, servername, ip, int(port), serverid), 
           'm_SvrName': servername, 
           'm_EntryName': (district[:4] + '入口'), 
           'm_PassPort': (
                        self.m_Idx, self.m_Pwd), 
           'm_IsLogin': True}
        return IPs


class CDGWShunLianConnectTest(CDGWConnectTestBase):
    m_ResultLog = ''
    DELAY_LOGIN_SEC = 10

    def __init__(self):
        CDGWConnectTestBase.__init__(self)
        self.m_bStartRestart = False
        self.m_oDelayLoginTimer = None
        return

    def GetTestServerList(self):
        oldnetobj = netserver.g_OldNetObj
        if hasattr(oldnetobj, 'm_ServerInfo'):
            (field, name, ip, port, serverid) = oldnetobj.m_ServerInfo
            IPs = {'dgwinfo': (
                         ip, int(port), serverid, DGW_SHUNLIANCONNECT), 
               'm_ServerInfo': (
                              field, name, ip, port, serverid), 
               'm_SvrName': name, 
               'm_EntryName': (field[:4] + '入口')}
            LOG_DEBUG('test', 'dgw普通connect ip:%s:%s' % (ip, port))
            return IPs
        elif hasattr(oldnetobj, 'm_DstIPPort'):
            (ip, port) = oldnetobj.m_DstIPPort
            serverid = netserver.g_KFServerID
            if not serverid:
                serverid = oldnetobj.m_ServerID
            IPs = {'dgwinfo': (ip, int(port), serverid, DGW_SHUNLIANCONNECT), 'm_PassPort': (oldnetobj.m_PassPort), 
               'm_EntryName': (getattr(oldnetobj, 'm_EntryName', '')), 
               'm_DstIPPort': (
                             ip, port)}
            LOG_DEBUG('test', 'dgw跨服connect ip:%s:%s' % (ip, port))
            return IPs
        else:
            data = self.GetServerInfo()
            if not data:
                return
            (ip, port, serverid, field, name) = (
             data['ip'], data['port'], data['serverid'], data['district'], data['name'])
            IPs = {'dgwinfo': (
                         ip, int(port), serverid, DGW_SHUNLIANCONNECT), 
               'm_ServerInfo': (
                              field, name, ip, port, serverid), 
               'm_SvrName': name, 
               'm_EntryName': (field[:4] + '入口')}
            LOG_DEBUG('test', 'dgw瞬連connect ip:%s:%s' % (ip, port))
            return IPs
        return

    def GetServerInfo(self):
        import selectserver, netserver
        (field, name) = netserver.GetLoginServer()
        (serverInfo, _, _) = selectserver.GetServerInfo()
        if serverInfo.get(field):
            for serverdata in self.m_ServerInfo[field]:
                if serverdata['name'] == name:
                    return serverdata

        return

    def Connect(self):
        CDGWConnectTestBase.Connect(self)
        return

    def GetNetInfo(self, netobj):
        ip = port = ''
        if hasattr(netobj, 'm_ServerInfo'):
            (ip, port) = netobj.m_ServerInfo[2:4]
        elif hasattr(netobj, 'm_DstIPPort'):
            (ip, port) = netobj.m_DstIPPort
        return (
         ip, port)

    def OnSocketConnectFail(self, netobj):
        if self.IsConnectTestFail():
            LOG('連接失敗:dgw.OnSocketConnectFail')
            netobj.m_IsFail = True
            dgwnet.ServerDGWLog(dgwnet.ERRTYPE_DROPPED)
            self.TryAutoLogin()
        elif self.IsNetConnectFail():
            LOG('嘗試下一步代理連接:OnSocketConnectFail')
            self.DGWTCPConnect()
        return

    def OnSocketError(self, netobj):
        if self.IsConnectTestFail():
            LOG('連接失敗:dgw.OnSocketError')
            netobj.m_IsFail = True
            dgwnet.ServerDGWLog(dgwnet.ERRTYPE_DROPPED)
            self.TryAutoLogin()
        elif self.IsNetConnectFail():
            LOG('嘗試下一步代理連接:OnSocketError')
            self.DGWTCPConnect()
        return

    def OnSocketSuccess(self):
        return

    def TryAutoLogin(self):
        import loginin, netquicklogin, timer
        if loginin.CanAutoLogin() and not self.m_bStartRestart and not netquicklogin.IsQuickConnect():
            self.ReleaseLoginTimer()
            self.m_bStartRestart = True
            self.m_oDelayLoginTimer = timer.Timer(self.DELAY_LOGIN_SEC, misc.Functor(self.DoAutoLogin))
        return

    def DoAutoLogin(self):
        import loginin
        self.ReleaseLoginTimer()
        loginin.DoConnectFailAutoLogin()
        self.m_bStartRestart = False
        return

    def ReleaseLoginTimer(self):
        if self.m_oDelayLoginTimer:
            self.m_oDelayLoginTimer.Release()
            self.m_oDelayLoginTimer = None
        return


class CDGWDataMgr(object):
    ENUM = 3

    def __init__(self):
        self.m_Idx = 0
        self.m_TcpList = []
        return

    def ClearData(self):
        r"""\xb2M\xb2z\xbcƾ\xda"""
        self.m_Idx = 0
        self.m_TcpList = []
        return

    def UpdateDGWData(self, dServerInfoList):
        r"""\xa6s\xc0xdgw\xbcƾ\xda"""
        self.ClearData()
        for dServerInfo in dServerInfoList:
            dInfoList = dServerInfo['s']
            for dInfo in dInfoList:
                if 'normal' not in dInfo:
                    continue
                self.m_TcpList.append(dInfo['normal'])

        return

    def GetDGWData(self):
        r"""\xc0\xf2\xa8\xfadgw\xbcƾ\xda"""
        return self.m_TcpList

    def GetNextConnectData(self):
        r"""\xa8C\xa6\xb8\xc0\xf2\xa8\xfaENUM\xadӥN\xb2z\xbcƾ\xda"""
        lTcp = self.m_TcpList[self.m_Idx:self.m_Idx + self.ENUM]
        self.m_Idx += self.ENUM
        return lTcp

    def HasNextConnectData(self):
        r"""\xacO\xa7_\xc1٦\xb3\xa4U\xa4@\xbd\xfc\xbcƾ\xda"""
        return self.m_Idx < len(self.m_TcpList)


def GetDgwMgr():
    global g_DgwMgr
    if not g_DgwMgr:
        g_DgwMgr = CDGWDataMgr()
    return g_DgwMgr


def TryDGWQuickLogin():
    import main, net, netquicklogin
    netquicklogin.g_InQuickLogin = True
    netserver.g_OldNetObj = net.g_Net
    main.SaveClientData()
    ConnectTest(DGW_SHUNLIANCONNECT)
    return


def ConnectTest(itype, args=None):
    Type2Cls = {DGW_LOGINCONNECT: CDGWConnectTest, 
       DGW_RESELECTCONNECT: CDGWReselectConnectTest, 
       DGW_SHUNLIANCONNECT: CDGWShunLianConnectTest, 
       DGW_KUAFUREALCONNECT: CDGWKuaFuRealConnectTest}
    cls = Type2Cls.get(itype)
    if not cls:
        return
    if args:
        netserver.g_ConnectMgr = cls(args)
    else:
        netserver.g_ConnectMgr = cls()
    netserver.g_ConnectMgr.Connect()
    return netserver.g_ConnectMgr


def IsUseDgw():
    global g_IsUseDgw
    return g_IsUseDgw


def SetDgwFlag(bSet):
    global g_IsUseDgw
    g_IsUseDgw = bSet
    return


return
