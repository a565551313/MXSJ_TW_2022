# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgcertman.py
import interface, combdialog, cert, certmgr, netcert
g_CertMan = None

def ModuleReset():
    global g_CertMan
    g_CertMan = None
    return


def Show():
    global g_CertMan
    if g_CertMan:
        return
    g_CertMan = CCertMan()
    return


def SetCheckCode(checkcode):
    if g_CertMan and g_CertMan.GetShow():
        g_CertMan.m_MobileCheck.SetText(checkcode)
        return True
    return False


class CCertMan(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/managecert.dlg')
        interface.Center(self)
        import combmacro
        self.m_MobileCheck = combmacro.CEDIT(interface.CEdit, 'edt_CheckCode', self, interface.COLOR_5, interface.FontLT14_3)
        self.GetObject('btn_PhoneSel').SetSelect(True)
        self.m_Timer = None
        return

    def SetValidateKey(self, txt):
        self.m_MobileCheck.SetText(txt)
        return

    def CloseWindow(self):
        global g_CertMan
        g_CertMan = None
        return

    def GetValidateKey(self):
        if self.m_Timer:
            return False
        netcert.C2SGetValiKey(2)
        return True

    def SendValidateKey(self, valKey):
        import usermacro
        if not valKey:
            usermacro.PROMPT_MSG('請輸入驗証碼')
            return False
        netcert.C2SSend6ValKey2(valKey)
        return True

    def RefreshGetValKey(self, cdTime=60):

        def downCount(obj, nowCount):
            nowCount -= 1
            obj.m_CountTime = nowCount
            if nowCount <= 0:
                showText = '獲取驗証碼'
                obj.GetObject('btn_GetCheckCode').SetText(showText)
                obj.GetObject('btn_GetCheckCode').Enable(True)
                obj.ShowVoiceVerify()
                if obj.m_Timer:
                    obj.m_Timer.Release()
                    obj.m_Timer = None
                return
            else:
                showText = '獲取驗証碼 %d' % nowCount
                obj.GetObject('btn_GetCheckCode').SetText(showText)
                obj.GetObject('btn_GetCheckCode').Enable(False)
                return (nowCount,)
            return

        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        showText = '獲取驗証碼 %s' % cdTime
        self.GetObject('btn_GetCheckCode').SetText(showText)
        self.GetObject('btn_GetCheckCode').Enable(False)
        self.m_Timer = self.CreatePyCommand(30, downCount, cdTime)
        return

    def ShowVoiceVerify(self):
        import combmacro
        txt = '#u手機收不到短信，點擊這裡接收語音驗証碼#r(您將收到一個語音自動播放驗証碼的來電)#n'
        (x, y, w, h) = self.GetLocData('txt_Yuyin')
        self.m_VoiceVerify = interface.CClickRichText(self, x, y, w, txt, interface.COLOR_274, 65280, interface.FontLT12_1, 99)
        return

    def ClickGetKey(self):
        self.GetValidateKey()
        return

    def GetVoiceCode(self):
        if hasattr(self, 'm_CountTime') and self.m_CountTime > 0:
            import usermacro
            usermacro.PROMPT_MSG('%d秒後可重試' % self.m_CountTime)
            return
        import C_sys
        tm = C_sys.GetTime()
        if hasattr(self, 'm_LastClick') and 0 <= tm - self.m_LastClick < 20000:
            import usermacro
            usermacro.PROMPT_MSG('操作過於頻繁，請稍後再嘗試')
            return
        self.m_LastClick = tm
        netcert.C2SMsgMode(3, 2)
        self.ClickGetKey()
        return

    def OnMessage(self, msgid):
        if msgid in (2, 5):
            netcert.C2SCancle()
            self.CloseWindow()
        elif msgid == 3:
            import dlgnpc
            mode = certmgr.GetSendMsgMode()
            if mode == 1:
                netcert.C2SMsgMode(1, 2)
                self.ClickGetKey()
            elif mode == 2:
                netcert.C2SMsgMode(2, 2)
                self.ClickGetKey()
            elif mode == 3:

                def callback(msgid):
                    if msgid == 1:
                        netcert.C2SMsgMode(1, 2)
                        self.ClickGetKey()
                    elif msgid == 2:
                        netcert.C2SMsgMode(2, 2)
                        self.ClickGetKey()
                    return

                txt = '請選擇驗証方式：\nQ直接手機獲取驗証碼（推荐）\nQ備用方式（在推荐方式無效的情況下使用）'
                dlgnpc.ShowClientDlg(txt, '', callback)
        elif msgid == 4:
            checkcode = self.m_MobileCheck.GetText()
            self.SendValidateKey(checkcode)
        elif msgid == 99:
            self.GetVoiceCode()
        return


def SetCDTime(sec):
    if g_CertMan:
        g_CertMan.RefreshGetValKey(sec)
    return


return
