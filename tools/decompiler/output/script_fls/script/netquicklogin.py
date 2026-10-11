# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\netquicklogin.py
import C_object, net
QUICKLOGIN_SECOND = 10
g_LoginKey = None
g_DoRestart = True
g_oStartQucikTimer = None
g_bCanDoQuickLogin = False
g_Timer = None
g_ConnectObj = None
g_MaintainFlag = False
g_bHasClickQuickLogin = False
g_bHasQuickLoginFail = False

def ModuleReset():
    global g_ConnectObj
    global g_DoRestart
    global g_LoginKey
    global g_MaintainFlag
    global g_Timer
    global g_bCanDoQuickLogin
    global g_oStartQucikTimer
    g_LoginKey = None
    g_DoRestart = True
    g_oStartQucikTimer = None
    g_bCanDoQuickLogin = False
    g_Timer = None
    g_ConnectObj = None
    g_MaintainFlag = False
    g_bHasClickQuickLogin = False
    return


def SetHasClickQuickLogin(bClick):
    global g_bHasClickQuickLogin
    g_bHasClickQuickLogin = bClick
    return


def SetQuickLoginFail(bFail):
    global g_bHasQuickLoginFail
    g_bHasQuickLoginFail = bFail
    return


def RefreshErrorMsg():
    global g_bHasQuickLoginFail
    import usermacro
    if g_bHasQuickLoginFail:
        g_bHasQuickLoginFail = False
        usermacro.PROMPT_MSG('重新連接失敗，請重新登錄')
    return


def S2CLoginKey(netobj):
    global g_LoginKey
    key = netobj.UnpackInt(4)
    itype = netobj.UnpackInt(1)
    g_LoginKey = key
    print '瞬連key瞬連key', key
    return


def S2CForceLoginOut(netobj):
    global g_LoginKey
    itype = netobj.UnpackInt(1)
    g_LoginKey = None
    import juben
    if juben.IsPlayJuben():
        juben.StopJuBen(True)
    return


def S2CQuickLoginFail(netobj):
    import ratio, main
    ratio.Set800x600()
    SetQuickLoginFail(True)
    main.Restart()
    print '瞬連失敗!!'
    return


def S2CDelLoginKey(netobj):
    global g_LoginKey
    g_LoginKey = None
    import juben
    if juben.IsPlayJuben():
        juben.StopJuBen(True)
    return


FUNC_DICT = {1: S2CLoginKey, 2: S2CForceLoginOut, 
   3: S2CQuickLoginFail, 
   4: S2CDelLoginKey}

def S2CQuickLogin(netobj):
    global FUNC_DICT
    isub = netobj.UnpackInt(1)
    if FUNC_DICT.has_key(isub):
        func = FUNC_DICT[isub]
        print 'S2CQuickLogin   ', func.__name__
        func(netobj)
    else:
        print 'S2CQuickLogin!!!    找不到函數'
    return


def C2SSendLoginKey(key):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_QUICKLOGIN)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(key, 4)
    netobj.PacketSend()
    return


def C2SRequestQuickLogin(key, pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_QUICKLOGIN)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(key, 4)
    if not pid:
        import netserver
        pid = netserver.GetPlayerID()
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()
    return


class CQuickNet(net.CNet):

    def __init__(self, proxy, ip, port):
        if not port:
            port = ''
        net.CNet.__init__(self, ip, port)
        self.m_Hello = False
        self.m_Proxy = proxy
        self.m_NetFunction[1] = S2CHello
        return

    def OnConnectFail(self):
        global g_ConnectObj
        print '連接失敗：', self.GetInfo()
        g_ConnectObj = None
        return

    def OnError(self, msg=None):
        global g_ConnectObj
        print '連接錯誤：', self.GetInfo(), msg
        g_ConnectObj = None
        return

    def ConnectServer(self):
        if self.m_Proxy:
            print '連接代理!!!!!', self.m_Proxy
            (ip, port) = self.m_Proxy.split(':')
            self.Connect(ip, int(port))
            iplst = self.m_IP.split('.')
            port = self.m_Port
            for i in xrange(4):
                self.NakedSend(chr(int(iplst[i])))

            self.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
        else:
            print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            print g_LoginKey
            self.Connect(self.m_IP, self.m_Port)
        return


def S2CHello(netobj):
    global g_ConnectObj
    import traceback
    traceback.print_stack()
    print '成功連接服務器：', netobj.GetInfo()
    g_ConnectObj = None
    ClearConnectTimer()
    import hero, main
    main.RestartQuickLogin(g_LoginKey, hero.g_ID)
    return


def NormalLogout():
    global g_LoginKey
    if g_LoginKey and net.g_Net:
        C2SSendLoginKey(g_LoginKey)
        g_LoginKey = None
    return


def SetMaintainFlag(bMaintain):
    global g_MaintainFlag
    g_MaintainFlag = bMaintain
    return


def Connect(showdlg=True, sReason=''):
    import selectserver
    proxy = selectserver.g_Proxy
    ip = selectserver.g_LastVisit[2]
    port = selectserver.g_LastVisit[3]

    def cancel(dlg):
        dlg.Release()
        ClearConnectTimer()
        net.ShowError(None)
        return

    def done(dlg, i):
        dlg.SetMessage('網絡異常斷開，嘗試重新連接中' + '.' * (i % 9))
        return (i + 1,)

    import commondialog
    if showdlg:
        dlg = commondialog.ShowMessageBox('網絡異常斷開，嘗試重新連接中', '取消', cancel)
        dlg.CreatePyCommand(15, done, 0)
    StartConnectTimer(proxy, ip, port)
    return


def ClearConnectTimer():
    global g_Timer
    if g_Timer:
        g_Timer.Release()
    g_Timer = None
    return


def IsQuickConnect():
    return g_Timer


def CanQuickConnect():
    import hero
    return g_LoginKey and hero.g_ID


def StartConnectTimer(proxy, ip, port):
    global g_Timer
    ClearConnectTimer()

    def done(obj, i):
        global g_ConnectObj
        if i > 60:
            net.ShowError(None)
            return
        if i % 2 == 0 and g_ConnectObj == None:
            g_ConnectObj = CQuickNet(proxy, ip, port)
            g_ConnectObj.ConnectServer()
        return (i + 1,)

    g_Timer = C_object.CBaseObject(None)
    g_Timer.CreatePyCommand(30, done, 0)
    return


def ProcessServerCmd():
    if g_ConnectObj:
        g_ConnectObj.ProcessServerCmd()
    return


def StartQuickTimer():
    r"""
        \xa6b\xb8\xf3\xaaA\xa9M\xa6^\xad\xec\xaaA\xb6\xa5\xacq\xa6p\xaaG\xb3s\xa4W\xa4F\xaaA\xb0Ⱦ\xb9\xa1A\xa6\xfd\xacO\xaa\xf8\xaeɶ\xa1\xa5d\xb5ۦ\xac\xa4\xa3\xa8\xec\xaaA\xb0Ⱥݪ\xba\xa4H\xaa\xab\xc4ݩ\xcaS2CPropInit\xa8\xf3ĳ\xa7Y\xbb{\xac\xb0\xb6i\xa4J\xb9C\xc0\xb8\xb6\xa5\xacq\xa5d\xa6\xed\xa1A
        \xa6\xb9\xaeɩM\xaaA\xb0Ⱦ\xb9\xaa\xba\xba\xf4\xb5\xb8\xb3s\xb1\xb5\xc1٦b\xa1A\xa6\xfd\xacO\xabȤ\xe1\xbaݤw\xb8g\xa5d\xa6\xed\xa1A\xa5D\xb0ʱҰ\xca\xc0\xfe\xb3s\xa1C
        \xa6b\xa6\xac\xa8\xec\xa4H\xaa\xab\xc4ݩ\xcaS2CPropInit\xa8\xf3ĳ\xbbݭn\xb2M\xb0\xa3\xb3o\xadӱҰ\xca\xc0\xfe\xb3s\xaa\xba\xa9w\xaeɾ\xb9\xa1C
        """
    global g_oStartQucikTimer
    if g_oStartQucikTimer:
        LOG('開啟瞬連定時器！！！！！！！')
        import timer
        g_oStartQucikTimer = timer.Timer(QUICKLOGIN_SECOND, DoQuickLoginConnect, 1)
    return


def DoQuickLoginConnect():
    global g_bCanDoQuickLogin
    if g_bCanDoQuickLogin:
        g_bCanDoQuickLogin = False
        Connect(False)
        import dlgladderrank
        dlgladderrank.ShowLoadingDlg(2)
    return


def ClearQuickTimer():
    global g_bCanDoQuickLogin
    global g_oStartQucikTimer
    LOG('清除瞬連定時器！！！！！！！')
    g_bCanDoQuickLogin = False
    if g_oStartQucikTimer:
        g_oStartQucikTimer.Release()
        g_oStartQucikTimer = None
    return


def SetCanQuickLogin(bCanDoQuickLogin):
    global g_bCanDoQuickLogin
    g_bCanDoQuickLogin = bCanDoQuickLogin
    return


return
