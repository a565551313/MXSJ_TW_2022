# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\twautologin.py
import timer, loginin
g_AutoLogin = None

def GetAutoLogin():
    global g_AutoLogin
    if not g_AutoLogin:
        g_AutoLogin = CAutoLogin()
    return g_AutoLogin


def AutoLogin(sAccount, sPwd, sServer):
    GetAutoLogin().Start(sAccount, sPwd, sServer)
    return


class CAutoLogin(object):

    def __init__(self):
        self.m_oTimer = None
        self.m_sAccount = ''
        self.m_sPwd = ''
        self.m_sServer = ''
        self.m_bSelectServer = False
        self.m_bLogin = False
        self.m_bSelectRole = False
        return

    def Start(self, sAccount, sPwd, sServer):
        self.InitInfo(sAccount, sPwd, sServer)
        self.ReleaseTimer()
        self.m_oTimer = timer.Timer(0.1, self.CheckStep, iRepeat=-1)
        return

    def End(self):
        self.m_sAccount = ''
        self.m_sPwd = ''
        self.m_sServer = ''
        self.m_bSelectServer = False
        self.m_bLogin = False
        self.m_bSelectRole = False
        self.ReleaseTimer()
        return

    def CheckStep(self):
        self.CheckMainPage()
        self.CheckSelectServer()
        self.CheckLoginin()
        self.CheckSelectRole()
        return

    def CheckMainPage(self):
        import mainpage
        if mainpage.g_MainPage and mainpage.g_MainPage.GetShow():
            mainpage.g_MainPage.OnMessage(1)
        return

    def CheckSelectServer(self):
        import selectserver
        if selectserver.SelectServer and selectserver.SelectServer.GetShow() and not self.m_bSelectServer:
            for oBtn in selectserver.SelectServer.GetServerBtn():
                LOG(oBtn, oBtn.GetServerName(), self.m_sServer)
                if oBtn and oBtn.GetServerName() == self.m_sServer:
                    oBtn.LeftUp()
                    self.m_bSelectServer = True
                    break

        return

    def CheckLoginin(self):
        import loginin
        if loginin.LoginIn and loginin.LoginIn.GetShow() and not self.m_bLogin:
            loginin.LoginIn.m_UserEdit.SetText(self.m_sAccount)
            loginin.LoginIn.m_PasswordEdit.SetText(self.m_sPwd)
            loginin.LoginIn.OnMessage(1)
            self.m_bLogin = True
        return

    def CheckSelectRole(self):
        import selectrole
        if selectrole.SelectRole and selectrole.GetShow() and not self.m_bSelectRole:
            selectrole.SelectRole.OnMessage(1)
            self.m_bSelectRole = True
            self.End()
        return

    def InitInfo(self, sAccount, sPwd, sServer):
        self.m_sAccount = sAccount
        self.m_sPwd = sPwd
        self.m_sServer = sServer
        return

    def ReleaseTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        return


return
