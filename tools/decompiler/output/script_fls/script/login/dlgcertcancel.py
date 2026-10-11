# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgcertcancel.py
import interface, combdialog, cert, certmgr, netcert
g_CertCancel = None
g_ChangePhone = None
g_ChangeBindTime = 0
g_MailCode = None

def ModuleReset():
    global g_CertCancel
    global g_ChangeBindTime
    global g_ChangePhone
    global g_MailCode
    g_CertCancel = None
    g_ChangePhone = None
    g_ChangeBindTime = 0
    g_MailCode = None
    return


def Show():
    global g_CertCancel
    if not g_CertCancel:
        g_CertCancel = CCertCancel()
    return


def RefreshPhoneNumber():
    if g_CertCancel:
        g_CertCancel.RefreshPhoneNumber()
    return


class CCertCancel(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/cancelcert.dlg')
        interface.Center(self)
        self.RefreshPhoneNumber()
        return

    def RefreshPhoneNumber(self):
        phoneNumber = certmgr.GetBindPhone()
        if not phoneNumber:
            phoneNumber = '??????????'
        phoneNumber = phoneNumber[:3] + '****' + phoneNumber[7:]
        import combmacro
        self.m_PhoneNumber = combmacro.CTEXT(interface.CTextObject, 'txt_PhoneNumber', self, str(phoneNumber), interface.FontLT14_3, interface.COLOR_9)
        return

    def ChangePhone(self):
        import loginin
        if loginin.g_User and loginin.g_User.endswith('@2980.com'):

            def Func(msgid):
                if msgid == 1:
                    import net, gameurl
                    net.OpenUrl(gameurl.MAIN2980_URL)
                return

            msg = '2980用戶可以登錄郵箱關聯新手機（登錄郵箱後在「設置→帳戶→關聯手機」菜單中操作）\nQ登錄2980郵箱\nQ暫不處理\n'
            import dlgnpc
            dlgnpc.ShowClientDlg(msg, '', Func)
        else:
            import netlogin
            netlogin.C2SBindNewPhone()
        return

    def CloseWindow(self):
        global g_CertCancel
        g_CertCancel = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 3:
            ShowMailCode()
        elif msgid == 4:
            self.ChangePhone()
        elif msgid == 5:
            self.CloseWindow()
        return


def SetChangeBindTime(iTime):
    global g_ChangeBindTime
    print '換綁確認期結束時間', iTime
    g_ChangeBindTime = iTime
    return


class CChangePhone(combdialog.CCombDialog):

    def __init__(self, phoneNum):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/changephone.dlg')
        interface.Center(self)
        import combmacro, wrapinterface
        self.m_PhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'edit_Phone', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_PhoneEdit.SetLimit(11)
        self.m_PhoneCodeEdit = combmacro.CEDIT(interface.CEdit, 'edit_PhoneCode', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_MailCodeEdit = combmacro.CEDIT(interface.CEdit, 'edit_MailCode', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_PhoneCodeEdit.SetLimit(10)
        self.m_MailCodeEdit.SetLimit(8)
        self.m_Timer = None
        if not phoneNum:
            phoneNum = '??????????'
        phoneNumber = phoneNum[:3] + '****' + phoneNum[7:]
        self.m_TxtPhoneNumber = combmacro.CTEXT(interface.CTextObject, 'txt_phonenumber', self, phoneNumber, interface.FontLT14_3, 16777215, spacing=0, align=interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        return

    def RefreshChangePhone(self, cdTime=60):

        def downCount(obj, nowCount):
            nowCount -= 1
            if nowCount <= 0:
                showText = '獲取驗証碼'
                obj.GetObject('btn_ChangePhone').SetText(showText)
                obj.GetObject('btn_ChangePhone').Enable(True)
                if obj.m_Timer:
                    obj.m_Timer.Release()
                    obj.m_Timer = None
                return
            else:
                showText = '獲取驗証碼 %d' % nowCount
                obj.GetObject('btn_ChangePhone').SetText(showText)
                obj.GetObject('btn_ChangePhone').Enable(False)
                return (nowCount,)
            return

        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        showText = '獲取驗証碼 %d' % cdTime
        self.GetObject('btn_ChangePhone').SetText(showText)
        self.GetObject('btn_ChangePhone').Enable(False)
        self.m_Timer = self.CreatePyCommand(30, downCount, cdTime)
        return

    def SentPhoneNumber(self, phoneNumber):
        import dlgnpc
        mode = certmgr.GetSendMsgMode()
        if mode == 1:
            netcert.C2SMsgMode(1, 3)
            netcert.C2SApplyChangePhone(phoneNumber)
        elif mode == 2:
            netcert.C2SMsgMode(2, 3)
            netcert.C2SApplyChangePhone(phoneNumber)
        elif mode == 3:

            def callback(msgid):
                if msgid == 1:
                    netcert.C2SMsgMode(1, 3)
                    netcert.C2SApplyChangePhone(phoneNumber)
                elif msgid == 2:
                    netcert.C2SMsgMode(2, 3)
                    netcert.C2SApplyChangePhone(phoneNumber)
                return

            txt = '請選擇驗証方式：\nQ直接手機獲取驗証碼（推荐）\nQ備用方式（在推荐方式無效的情況下使用）'
            dlgnpc.ShowClientDlg(txt, '', callback)
        return

    def GetChangePhone(self, phoneNumber):
        if self.m_Timer:
            return False
        self.SentPhoneNumber(phoneNumber)
        return True

    def CloseWindow(self):
        global g_ChangePhone
        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        g_ChangePhone = None
        return

    def Comfirm(self):
        phoneNumber = self.m_PhoneEdit.GetText()
        if not phoneNumber:
            import usermacro
            usermacro.PROMPT_MSG('請輸入新手機號碼')
            return
        if len(phoneNumber) != 11:
            import usermacro
            usermacro.PROMPT_MSG('您輸入的手機號碼有誤，請重新輸入')
            return
        hasSent = self.GetChangePhone(phoneNumber)
        if hasSent:
            self.RefreshChangePhone()
        return

    def OnMessage(self, msgid):
        if msgid in (1, 4):
            self.CloseWindow()
        elif msgid == 2:
            self.Comfirm()
        elif msgid == 3:
            phoneCode = self.m_PhoneCodeEdit.GetText()
            mailCode = self.m_MailCodeEdit.GetText()
            if not phoneCode:
                import usermacro
                usermacro.PROMPT_MSG('請輸入手機驗証碼')
                return
            if not mailCode:
                import usermacro
                usermacro.PROMPT_MSG('請輸入郵箱授權碼')
                return
            if len(mailCode) != 8:
                import usermacro
                usermacro.PROMPT_MSG('請輸入正確的郵箱授權碼')
                return
            netcert.C2SChangePhone(phoneCode, mailCode)
        return


def ShowChangePhone():
    import misc
    servertime = misc.GetServerTime()
    print '換綁確認期時間 和 當前時間：', g_ChangeBindTime, servertime
    if g_ChangeBindTime and servertime < g_ChangeBindTime:
        day = (g_ChangeBindTime - servertime) / 86400
        day = max(day, 1)
        ShowChangingPhoneTips(day)
    else:
        ShowChangePhoneDlg()
    return


def ShowChangingPhoneTips(iDay):
    import dlgnpc

    def Func(msgid):
        if msgid == 1:
            netcert.C2SStopChangePhone()
        return

    txt = '您已經申請了修改綁定的手機號碼，目前正處於確認期（離正式生效的時間還有%d天）。確認期內可隨時取消申請。\nQ我要取消申請\nQ繼續等待' % iDay
    dlgnpc.ShowClientDlg(txt, '', Func)
    return


def ShowChangePhoneDlg():
    global g_ChangePhone
    phone = certmgr.GetBindPhone()
    g_ChangePhone = CChangePhone(phone)
    return


def CloseChangePhone():
    if g_ChangePhone:
        g_ChangePhone.CloseWindow()
    return


def SetCheckCode(checkcode):
    if g_ChangePhone and g_ChangePhone.GetShow():
        g_ChangePhone.m_PhoneCodeEdit.SetText(checkcode)
        return True
    return False


class CMailCheckCode(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/mailcode.dlg')
        interface.Center(self)
        import combmacro
        self.m_MailCodeEdit = combmacro.CEDIT(interface.CEdit, 'edit_MailCode', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_MailCodeEdit.SetLimit(8)
        self.m_Timer = None
        return

    def GetMailCode(self):
        if self.m_Timer:
            return False
        netcert.C2SWantStopCert()
        return True

    def SendMailCode(self, mailCode):
        if not mailCode:
            import usermacro
            usermacro.PROMPT_MSG('請輸入郵箱授權碼')
            return False
        if len(mailCode) != 8:
            import usermacro
            usermacro.PROMPT_MSG(b'O"M\x1bV\xb8WMO\xa6XHD\x9eO\x91C07\x84\xbdX')
            return False
        netcert.C2SConfirmStopCert(mailCode)
        return True

    def RefreshGetMailCode(self, cdTime=60):

        def downCount(obj, nowCount):
            nowCount -= 1
            if nowCount <= 0:
                showText = '獲取授權碼'
                obj.GetObject('btn_GetCheckCode').SetText(showText)
                obj.GetObject('btn_GetCheckCode').Enable(True)
                if obj.m_Timer:
                    obj.m_Timer.Release()
                    obj.m_Timer = None
                return
            else:
                showText = '獲取授權碼 %d' % nowCount
                obj.GetObject('btn_GetCheckCode').SetText(showText)
                obj.GetObject('btn_GetCheckCode').Enable(False)
                return (nowCount,)
            return

        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        showText = '獲取授權碼%s' % cdTime
        self.GetObject('btn_GetCheckCode').SetText(showText)
        self.GetObject('btn_GetCheckCode').Enable(False)
        self.m_Timer = self.CreatePyCommand(30, downCount, cdTime)
        return

    def CloseWindow(self):
        global g_MailCode
        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        g_MailCode = None
        return

    def OnMessage(self, msgid):
        if msgid in (1, 4):
            self.CloseWindow()
        elif msgid == 2:
            hasSent = self.GetMailCode()
            if hasSent:
                self.RefreshGetMailCode()
        elif msgid == 3:
            mailCode = self.m_MailCodeEdit.GetText()
            self.SendMailCode(mailCode)
        return


def ShowMailCode(show=True):
    global g_MailCode
    if show:
        if not g_MailCode:
            g_MailCode = CMailCheckCode()
    elif g_MailCode:
        g_MailCode.CloseWindow()
    return


return
