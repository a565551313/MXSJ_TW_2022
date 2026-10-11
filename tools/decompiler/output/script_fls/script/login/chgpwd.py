# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\chgpwd.py
import C_object, interface, wrapinterface, combdialog

class CPwdEdit(interface.CEdit):

    def AddChar(self, c):
        if c.isalnum():
            interface.CEdit.AddChar(self, c)
        else:
            import usermacro
            usermacro.PROMPT_MSG('#Y密碼只能為數字或字母')
        return


class CChgPwd(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/chgpwd.dlg')
        import combmacro
        self.m_OldPwd = combmacro.CEDIT(CPwdEdit, 'old', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_OldPwd.aWF~[mit(16)
        self.m_OldPwd.m_IsPassword = True
        self.m_OldPwd.Active(True)
        self.m_NewPwd = combmacro.CEDIT(CPwdEdit, 'new', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_NewPwd.aWF~[mit(16)
        self.m_NewPwd.m_IsPassword = True
        self.m_NewPwdRepeat = combmacro.CEDIT(CPwdEdit, 'new2', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_NewPwdRepeat.aWF~[mit(16)
        self.m_NewPwdRepeat.m_IsPassword = True
        self.m_OldPwd.SetNextEdit(self.m_NewPwd)
        self.m_NewPwd.SetNextEdit(self.m_NewPwdRepeat)
        self.m_NewPwdRepeat.SetNextEdit(self.m_OldPwd)
        import combmacro
        txt = '特別提示：#r  如果有需要可以通過短信方式取回密碼，詳情請到登錄界面-各種密碼相關問題-取回密碼處查看'
        self.m_Text = combmacro.CRICHTEXT(C_object.CRichTextObject, 'txt', self, txt, interface.FONT_EDIT, interface.COLOR_EDIT)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import commondialog, sound
            sound.Play('action/button.wav')
            oldpwd = self.m_OldPwd.GetText()
            if len(oldpwd) < 6:
                self.m_OldPwd.SetText('')
                commondialog.ShowMessageBox('請輸入正確的舊密碼', '確定')
                return
            newpwd1 = self.m_NewPwd.GetText()
            newpwd2 = self.m_NewPwdRepeat.GetText()
            if len(newpwd1) < 6 or len(newpwd2) < 6:
                self.m_NewPwd.SetText('')
                self.m_NewPwdRepeat.SetText('')
                commondialog.ShowMessageBox('請輸入正確格式的新密碼', '確定')
                return
            if newpwd1 != newpwd2:
                commondialog.ShowMessageBox('兩次輸入的新密碼不一致', '確定')
                return
            if oldpwd == newpwd1:
                commondialog.ShowMessageBox('新舊密碼相同', '確定')
                return
            self.m_OldPwd.SetText('')
            self.m_NewPwd.SetText('')
            self.m_NewPwdRepeat.SetText('')
            import netlogin
            netlogin.C2SChgPwd(oldpwd, newpwd1)
        elif msgid == 2:
            Show(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        return


def Show(flag):
    global g_ChgPwd
    if flag:
        g_ChgPwd = CChgPwd(interface.DialogPanel)
    else:
        g_ChgPwd = None
    return


return
