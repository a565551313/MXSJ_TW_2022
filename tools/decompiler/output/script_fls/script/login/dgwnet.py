# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dgwnet.py
import dgw, netserver, cfg, misc, interface
ERRTYPE_TOKEN_ERR = 1
ERRTYPE_TOKEN_TIMEOUT = 2
ERRTYPE_FAILE = 3
ERRTYPE_DROPPED = 5
ERRTYPE_QUICKLOGIN = 6
ERRTYPE_GET_DGW_ERR = 7
DES_KEY = 'dgw17y4m'
MXPROID = 3
NETTYPE = 5
ECHOTIME = 22
CACHETIME = 10800
TIMEOUT = 3000
g_SaveInfo = {'base': None, 'server': None, 'token': None}
g_EchoTimer = None
g_LastTime = 0
g_LastType = 0
g_Debug = True

def ModuleReset():
    global g_Debug
    global g_EchoTimer
    global g_LastTime
    global g_LastType
    global g_SaveInfo
    g_SaveInfo = {'base': None, 'server': None, 'token': None}
    g_EchoTimer = None
    g_LastTime = 0
    g_LastType = 0
    g_Debug = True
    return


def OldConnectTest(itype):
    import dgwconnecttest
    ModuleReset()
    dgwconnecttest.SetDgwFlag(False)
    if itype == dgwconnecttest.DGW_LOGINCONNECT:
        netserver.g_PriorServer = dgwconnecttest.g_DGWLoginInfo[:2]
        netserver.RandomConnect()
    elif itype == dgwconnecttest.DGW_SHUNLIANCONNECT:
        import netquicklogin
        netquicklogin.ConnectServer()
    elif itype == dgwconnecttest.DGW_KUAFUREALCONNECT:
        import connect
        (idx, pwd, proxy_port_ip_list, serverid) = dgwconnecttest.g_DGWKuaFuInfo
        connect.TryNewKuaFuConnect(idx, pwd, proxy_port_ip_list, serverid)
    elif itype == dgwconnecttest.DGW_RESELECTCONNECT:
        (serverid, idx, pwd) = dgwconnecttest.g_DGWRsLoginInfo
        netserver.NormalReselectServerConnect(serverid, idx, pwd)
    Print('dgw失敗，舊方式連接，類型為%d' % itype)
    StopWorking()
    return


def IsBanDgwServer(serverid):
    import permission
    if serverid in (30153, 1111, 30321, 30322):
        return True
    elif permission.GetSpecialVersion():
        sDGWTest = cfg.GetData('mx.ini', 'Game', 'dgwtest')
        if sDGWTest and sDGWTest.isdigit():
            return not int(sDGWTest)
        else:
            return True
    else:
        return False
    return


def IsDGWNet(netobj):
    return getattr(netobj, 'm_IsDGW', False)


def StartWorking(ip, iport, serverid, itype, callback):
    global g_SaveInfo
    g_SaveInfo = {}
    g_SaveInfo['base'] = (
     ip, iport, serverid, itype)
    json_config = '{"proid" : %d, "bsid" : %d, "port" : %d, "conf" : "dgw.ini", "net" : %d, "cid" : "%s", "good_ip" : [%s], "platform" : 3, "timeout" : %d}' % (
     MXPROID, serverid, iport, NETTYPE, misc.GetMAC(), GetGoodIP(ip), TIMEOUT)
    LOG('開始連接DGW')
    if not IsBanDgwServer(serverid):
        LOG_DEBUG(json_config)
        dgw.StartRequest(json_config, callback)
    else:
        LOG_DEBUG('禁止服務器編號')
        OldConnectTest(itype)
    return


def GetGoodIP(ip):
    import json
    (isok, dgwlst) = GetCacheTcpData(ip)
    goodip = ''
    if not isok:
        return goodip
    try:
        sinfo = json.read(dgwlst[0])
        normal = sinfo.get('normal', [])
        echo = sinfo.get('echo', [])
    except:
        normal = []
        echo = []

    if normal and echo:
        try:
            (normalip, normaludp, normaltcp) = normal
            (echoip, echoudp) = echo
            goodip = '{"s":["%s:%d:%d","%s:%d"]}' % (normalip, normaludp, normaltcp, echoip, echoudp)
        except:
            pass

    return goodip


def StartEcho():
    global g_EchoTimer

    def StopAndSave(obj):
        StopWorking()
        return

    if g_EchoTimer:
        g_EchoTimer.Release()
        g_EchoTimer = None
    dgw.StartEcho()
    g_EchoTimer = interface.CBaseObject(None)
    g_EchoTimer.CreatePyCommand(ECHOTIME * 30, StopAndSave)
    return


def StopWorking():
    SaveDGWInfo()
    dgw.StopRequest()
    return


def SaveDGWInfo():
    serverlist = dgw.GetServerList()
    result = []
    for serverinfo in serverlist:
        (smid, sip, iudpport, iport, isreal) = serverinfo
        iresult = dgw.GetTenDelay(str(sip), iudpport, iport)
        if iresult >= 3000:
            continue
        result.append((iresult, sip, iudpport, iport, isreal))

    result.sort((lambda i, j: cmp(i[0], j[0])))
    saveresult = []
    for ipinfo in result:
        (_, normalip, normaludp, normaltcp, __) = ipinfo
        echo = dgw.GetEchoWithNormal('%s:%d:%d' % (normalip, normaludp, normaltcp))
        try:
            (echoip, echoudp) = echo.split(':')
        except:
            (echoip, echoudp) = ('', 0)

        data = '{"normal":["%s",%d,%d],"echo":["%s",%d]}' % (normalip, normaludp, normaltcp, echoip, int(echoudp))
        saveresult.append(data)

    baseinfo = g_SaveInfo.get('base', None)
    if baseinfo and saveresult:
        baseip = baseinfo[0]
        SaveCacheTcpData(baseip, saveresult)
        DoLogEvent(result)
    return


def DoLogEvent(result):
    dInfoxx = {'dgw_line': '10.17.65.68:50018,', 
       'dgw_use_line': '10.17.65.68:50018', 
       'dgw_test_result': '16, 50, 8', 
       'dgw_status': '3', 
       'custom': 'type: 5'}
    str_line = []
    str_result = []
    for (iresult, sip, iudpport, iport, isreal) in result:
        str_line.extend([sip, ':', str(iport), ','])
        str_result.extend([str(iresult), ','])

    if str_line:
        str_line.pop()
        str_result.pop()
    dInfoxx['dgw_line'] = ('').join(str_line)
    dInfoxx['dgw_test_result'] = ('').join(str_result)
    import net
    dgwinfo = getattr(net.g_Net, 'm_DGWInfo', None)
    if dgwinfo:
        dInfoxx['dgw_use_line'] = '%s:%d' % (dgwinfo[0], dgwinfo[2])
        dInfoxx['dgw_status'] = str(dgwinfo[3])
    import pubdyflyer, pubbigdatadefines
    pubdyflyer.C2BLogEvent(pubbigdatadefines.DGW_EVENT, dInfoxx)
    return


def IsCanSendDgwLog(iType):
    global g_LastTime
    global g_LastType
    import misc
    if g_LastTime is 0:
        g_LastTime = misc.Time()
    elif iType == g_LastType and misc.Time() - g_LastTime < 3:
        return False
    else:
        g_LastTime = misc.Time()
        g_LastType = iType
    return True


def ServerDGWLog(iType):
    if not IsCanSendDgwLog(iType):
        return
    Print(str(iType) + ' 發送給im服務器')
    import hero
    baseinfo = g_SaveInfo.get('base', None)
    serverinfo = g_SaveInfo.get('server', None)
    tokeninfo = g_SaveInfo.get('token', None)
    if not baseinfo:
        return
    (ip, iport, serverid, itype) = baseinfo
    if serverinfo:
        (sip, siport, siudpport, sisreal) = serverinfo
    else:
        (sip, siport, siudpport, sisreal) = ('None', 0, 0, 0)
    if tokeninfo:
        stoken = tokeninfo
    else:
        stoken = 'None'
    iHeroID = hero.GetHeroID()
    json_config = '{\n\t\t"error_type" : %s,\n\t\t"proid" : %s,\n\t\t"bsid" : %s,\n\t\t"uid" : "%s",\n\t\t"port" : %s,\n\t\t"token" : "%s",\n\t\t"cid" : "%s",\n\t\t"net" : %s,\n\t\t"server" : [{"info":["%s", %s, %s, %s]}]\n\t\t}' % (iType, MXPROID, serverid, iHeroID, iport, stoken, misc.GetMAC(), NETTYPE, sip, siport, siudpport, sisreal)
    if serverinfo and tokeninfo:
        dgw.SetFail(json_config.decode('gbk').encode('utf-8'))
    return


def ServerDGWError(errtype):
    LOG('[dgw err]', errtype)
    ServerDGWLog(errtype)
    import dgwconnecttest
    dgwconnecttest.SetDgwFlag(False)
    baseinfo = g_SaveInfo.get('base', None)
    if not baseinfo:
        return
    (ip, iport, serverid, itype) = baseinfo
    OldConnectTest(itype)
    return


class CDGWNet(netserver.CMXNet):

    def __init__(self, ip, port, Itype=0):
        netserver.CMXNet.__init__(self, ip, port, Itype)
        self.m_IsDGW = True
        self.m_DGWInfo = None
        self.m_ProxyName = ''
        self.m_Proxy = ''
        self.m_DGWData = {}
        self.m_DGWToken = '0'
        self.m_DGWBaseInfo = None
        self.m_TryPrivate = True
        self.m_ServerList = []
        return

    def ConnectServer(self, lTcp):
        (sIp, iTcpPort, iUdpPort, iReal) = lTcp
        g_SaveInfo['server'] = (sIp, iTcpPort, iUdpPort, iReal)
        if iReal == 1:
            self.m_ProxyName = 'DGW直連'
        else:
            self.m_ProxyName = 'DGW代理'
            self.m_Proxy = '%s:%s' % (sIp, iTcpPort)
        self.m_DGWInfo = (
         sIp, iUdpPort, iTcpPort, iReal)
        self.Connect(sIp, iTcpPort)
        Print('使用dgw返回列表登錄(%s) IP：%s，端口：%s' % (self.m_ProxyName, sIp, iTcpPort))
        if self.IsNeedEcho():
            StartEcho()
        return

    def IsNeedEcho(self):
        import json
        baseinfo = g_SaveInfo.get('base', None)
        tcpinfo = g_SaveInfo.get('server', None)
        if not (baseinfo and tcpinfo):
            return True
        (sip, iport, serverid, itype) = baseinfo
        (isok, dgwlst) = GetCacheTcpData(sip)
        if isok:
            try:
                sinfo = json.read(dgwlst[0])
                normal = sinfo.get('normal', [])
                echo = sinfo.get('echo', [])
            except:
                return True
            else:
                if normal and echo:
                    try:
                        (normalip, normaludp, normaltcp) = normal
                        (lastip, lasttcp, lastudp, _) = tcpinfo
                        (echoip, echoudp) = echo
                    except:
                        return True
                    else:
                        if (
                         lastip, lasttcp, lastudp) == (normalip, normaltcp, normaludp):
                            return False
        return True


def GetCacheTcpData(ip):
    ipsdata = Encrypt(ip)
    try:
        dgwips = cfg.GetData('cachelink.ini', 'TCPDATA', ipsdata)
    except:
        LOG_DEBUG('GetCacheTcpData ERROR', ip, ipsdata)
        dgwips = None

    if dgwips:
        try:
            dgwips = Decrypt(dgwips)
        except:
            return (False, [])
        else:
            try:
                (dgwtime, dgwips) = dgwips.split('#')
                dgwtime = int(dgwtime)
                dgwlst = dgwips.split('|')
            except:
                return (False, [])
            else:
                nowtime = misc.Time()
                dt = nowtime - dgwtime
                if dt >= CACHETIME or dt < 0:
                    return (False, [])
                elif len(dgwlst) == 0:
                    return (False, [])
                else:
                    LOG_DEBUG('獲得緩存數據', ip, dgwlst)
                    return (True, dgwlst)
    else:
        return (False, [])
    return


def SaveCacheTcpData(ip, dgwlst):
    dgws = ('|').join(dgwlst)
    nowtime = misc.Time()
    msg = '%s#%s' % (str(int(nowtime)), dgws)
    LOG_DEBUG('緩存數據', msg)
    try:
        ipsdata, msgdata = Encrypt(ip), Encrypt(msg)
    except:
        return

    try:
        cfg.SaveData('cachelink.ini', 'TCPDATA', ipsdata, msgdata)
    except:
        LOG_DEBUG('SaveCacheTcpData ERROR', msg)

    return


def SendDGWStatus(netobj):
    if not (hasattr(netobj, 'm_IsDGW') and netobj.m_IsDGW):
        return
    if hasattr(netobj, 'm_DGWInfo') and netobj.m_DGWInfo:
        (ip, udpPort, tcpPort, real) = netobj.m_DGWInfo
        dgw.SetSuccessServer(ip, udpPort, tcpPort)
        if real == 1:
            msg = '直連'
        else:
            msg = '代理'
    return


def UpLoadLog(log):
    import logupload
    LOG_DEBUG(log)
    logupload.Upload(1, log)
    return


def Encrypt(data):
    import C_sys
    try:
        data = C_sys.StrDesEncrypt(DES_KEY, data)
    except:
        data = ''

    return data


def Decrypt(data):
    import C_sys
    try:
        data = C_sys.StrDesDecrypt(DES_KEY, data)
    except:
        data = ''

    return data


def Print(msg):
    if g_Debug:
        print msg
    return


return
