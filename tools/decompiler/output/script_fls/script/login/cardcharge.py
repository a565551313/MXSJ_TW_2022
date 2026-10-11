# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\cardcharge.py
import C_object, interface, wrapinterface, combdialog
g_CardCharge = None
g_ChargeMode = None

class CCardCharge(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/cardcharge.dlg')
        import combmacro
        self.m_Code = combmacro.CEDIT(interface.CEdit, 'code', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_Code.SetLimit(12)
        self.m_Code.Active(True)
        self.m_Pwd = combmacro.CEDIT(interface.CEdit, 'pwd', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_Pwd.SetLimit(8)
        self.m_Code.SetNextEdit(self.m_Pwd)
        self.m_Pwd.SetNextEdit(self.m_Code)
        import netlogin
        if netlogin.g_CurrAccount.isdigit():
            self.m_SelfAccountTxt = 'A' + netlogin.g_CurrAccount
        else:
            self.m_SelfAccountTxt = netlogin.g_CurrAccount
        btn = self.GetObject('btn_self')
        (w, h) = btn.GetSize()
        (x, y) = btn.GetPos()
        self.m_SelfAccountBtn = interface.CCheckBox(self, w, h, alpha=0, msgid=5)
        self.m_SelfAccountBtn.SetPos(x, y)
        self.m_SelfAccount = combmacro.CTEXT(C_object.CTextObject, 'self', self, self.m_SelfAccountTxt, interface.FONT_DEFAULT, 0)
        self.m_GreyInput = interface.CImagesObject(self, 'login/grey_input.igs', interface.UIPath)
        self.m_GreyInput.SetShow(False)
        (x, y) = self.GetObject('btn_self').GetPos()
        self.m_PointImg = C_object.CImagesObject(self, 'login/selected.igs', interface.UIPath)
        self.m_PointImg.SetPos(x, y)
        self.m_CurrSelect = 0
        return

    def SetCode(self, code):
        self.m_Code.SetText(code)
        self.m_Pwd.Active(True)
        return

    def SetPwd(self, pwd):
        self.m_Pwd.SetText(pwd)
        if self.m_CurrSelect == 1:
            self.m_OtherAccount.Active(True)
        else:
            self.m_Pwd.Active(False)
        return

    def OnMessage(self, msgid):
        global g_ChargeMode
        if msgid in (1, 3):
            import net, netlogin, commondialog, sound
            sound.Play('action/button.wav')
            if self.m_CurrSelect == 0:
                self.m_DestAccount = netlogin.g_CurrAccount
            else:
                self.m_DestAccount = self.m_DestAccountEdit.GetText()
                if self.m_DestAccount.isdigit():
                    commondialog.ShowMessageBox('帳號填寫錯誤，請仔細檢查。#r（是否忘記填寫帳號前的「A」？）', '確定')
                    return
            if len(self.m_DestAccount) < 3:
                commondialog.ShowMessageBox('請輸入正確的帳號', '確定')
                return
            code = self.m_Code.GetText()
            pwd = self.m_Pwd.GetText()
            if len(code) != 12 or len(pwd) != 8:
                commondialog.ShowMessageBox('請輸入正確的卡號和密碼', '確定')
                return
            import netlogin
            if msgid == 1:
                g_ChargeMode = 0
                if self.m_DestAccount.isdigit():
                    netlogin.C2SCardCharge('A' + self.m_DestAccount, code, pwd, g_ChargeMode)
                else:
                    netlogin.C2SCardCharge(self.m_DestAccount, code, pwd, g_ChargeMode)
                self.GetObject('btn_jishou').Enable(False)
                self.GetObject('btn_point').Enable(False)
                commondialog.ShowMessageBox('正在進行充點數操作，請稍後...', '確定')
            else:
                g_ChargeMode = 1
                if self.m_DestAccount.isdigit():
                    netlogin.C2SCardCharge('A' + self.m_DestAccount, code, pwd, g_ChargeMode)
                else:
                    netlogin.C2SCardCharge(self.m_DestAccount, code, pwd, g_ChargeMode)
                self.GetObject('btn_jishou').Enable(False)
                self.GetObject('btn_point').Enable(False)
                commondialog.ShowMessageBox('正在進行充寄售卡操作，請稍後...', '確定')
        elif msgid == 2:
            Show(False)
            ShowSuccess(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        elif msgid == 5:
            if self.m_CurrSelect == 0:
                return
            import combmacro, sound
            sound.Play('action/button.wav')
            self.m_CurrSelect = 0
            (x, y) = self.GetObject('btn_self').GetPos()
            self.m_PointImg.SetPos(x, y)
            self.m_SelfAccount = combmacro.CTEXT(C_object.CTextObject, 'self', self, self.m_SelfAccountTxt, interface.FONT_DEFAULT, 0)
            self.m_DestAccountEdit = None
            self.m_Pwd.SetNextEdit(self.m_Code)
        elif msgid == 6:
            return
            if self.m_CurrSelect == 1:
                return
            import combmacro, sound
            sound.Play('action/button.wav')
            self.m_CurrSelect = 1
            (x, y) = self.GetObject('btn_other').GetPos()
            self.m_PointImg.SetPos(x, y)
            self.m_SelfAccount = None
            (x, y) = self.GetObject('selfbar').GetPos()
            self.m_GreyInput.SetPos(x, y)
            self.m_DestAccountEdit = combmacro.CEDIT(interface.CEdit, 'other', self, 0, interface.FONT_EDIT, linecolor=0)
            self.m_DestAccountEdit.SetLimit(20)
            self.m_DestAccountEdit.Active(True)
            self.m_Pwd.SetNextEdit(self.m_DestAccountEdit)
            self.m_DestAccountEdit.SetNextEdit(self.m_Code)
        return


class CSuccess(combdialog.CCombPanel):

    def __init__(self, parent, account, codepoint):
        combdialog.CCombPanel.__init__(self, parent, 'login/charge_ok.dlg')
        import combmacro
        self.m_Txt1 = combmacro.CTEXT(C_object.CTextObject, 'gongxi', self, '恭喜您，充值成功！', interface.FontID36, 16768635)
        self.m_Txt1_2 = combmacro.CTEXT(C_object.CTextObject, 'gongxi', self, '恭喜您，充值成功！', interface.FontID36, 16768635)
        (x, y) = self.m_Txt1_2.GetPos()
        self.m_Txt1_2.SetPos(x + 1, y)
        if g_ChargeMode == 1:
            if account.isdigit():
                txt = '你已為#cFF8B64 A%s #n成功充值#cFF8B64 %s #n張寄售卡' % (account, codepoint)
            else:
                txt = '你已為#cFF8B64 %s #n成功充值#cFF8B64 %s #n張寄售卡' % (account, codepoint)
        elif account.isdigit():
            txt = '你已為#cFF8B64 A%s #n成功充值#cFF8B64 %s #n遊戲點' % (account, codepoint)
        else:
            txt = '你已為#cFF8B64 %s #n成功充值#cFF8B64 %s #n遊戲點' % (account, codepoint)
        self.m_Txt2 = combmacro.CRICHTEXT(C_object.CRichTextObject, 'note', self, txt, interface.FONT_DEFAULT, 16768608)
        self.m_Txt3 = combmacro.CRICHTEXT(C_object.CRichTextObject, 'note', self, txt, interface.FONT_DEFAULT, 16768608)
        (x, y) = self.m_Txt3.GetPos()
        self.m_Txt3.SetPos(x + 1, y)
        import selectserver
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            ShowSuccess(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        elif msgid == 2:
            import selectrole, netlogin, point2month, sound
            sound.Play('action/button.wav')
            if selectrole.g_SelectRoleIdx and 0 <= selectrole.g_SelectRoleIdx < len(netlogin.g_LoginRoleInfo):
                ShowSuccess(False)
                import point2month
                point2month.Show(True, selectrole.g_SelectRoleIdx)
            else:
                import commondialog
                commondialog.ShowMessageBox('請先返回至角色選擇界面並選擇想包月的角色', '確定')
                return
        elif msgid == 3:
            import sound
            sound.Play('action/button.wav')
            ShowSuccess(False)
            Show(True)
        return


def ShowSuccess(flag, account='', codepoint=''):
    global g_Success
    if flag:
        g_Success = CSuccess(interface.DialogPanel, account, codepoint)
    else:
        g_Success = None
    return


def SetCodeAndPwd(code, pwd):
    global g_CardCharge
    if g_CardCharge != None:
        g_CardCharge.SetCode(code)
        g_CardCharge.SetPwd(pwd)
    return


def ChargeSuccess(ret, point):
    import commondialog
    if not isinstance(g_CardCharge, CCardCharge):
        return
    g_CardCharge.GetObject('btn_point').Enable(True)
    g_CardCharge.GetObject('btn_jishou').Enable(True)
    if ret == 0:
        account = g_CardCharge.m_DestAccount
        Show(False)
        commondialog.HideMessageBox()
        ShowSuccess(True, account, point)
        return
    else:
        import commondialog, dc_error_code
        if dc_error_code.ERROR_MSG.has_key(ret):
            txt = dc_error_code.ERROR_MSG[ret]
            commondialog.ShowMessageBox('充值失敗，' + txt, '確定')
        else:
            commondialog.ShowMessageBox('充值失敗', '確定')
    return


def Show(flag):
    global g_CardCharge
    if flag:
        g_CardCharge = CCardCharge(interface.DialogPanel)
    else:
        g_CardCharge = None
    return


return
