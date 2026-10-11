# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\selfaccount.py
import C_object, C_sys, interface, wrapinterface, combdialog, net
g_SelfAccount = None

def Show(flag):
    global g_SelfAccount
    if flag:
        g_SelfAccount = CSelfAccount(interface.DialogPanel)
    else:
        g_SelfAccount = None
    return


def Success(itype, ret, point):
    if g_SelfAccount == None:
        return
    g_SelfAccount.ShowSuccess(itype, ret, point)
    return


ACCOUNT_CHAR = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 
 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
INVALID_CHAR = [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 31, 32, 27, 26, 25, 33, 30, 
 6, 17, 18, 20, 19]

class CSelfAccountEdit(interface.CEdit):

    def AddChar(self, c):
        if c not in ACCOUNT_CHAR:
            interface.CEdit.AddChar(self, c)
        return


class _EMailEdit(interface.CEdit):

    def AddChar(self, c):
        if c not in INVALID_CHAR:
            interface.CEdit.AddChar(self, c)
        return


class CSelfAccount(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/selfaccount.dlg')
        import combmacro
        self.m_SelfAccountEdit = combmacro.CEDIT(CSelfAccountEdit, 'name', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_SelfAccountEdit.SetLimit(16)
        self.m_SelfAccountEdit.Enable(False)
        self.m_EmailEdit = combmacro.CEDIT(_EMailEdit, 'email', self, 0, interface.FONT_EDIT, linecolor=0)
        self.m_EmailEdit.SetLimit(48)
        self.m_EmailEdit.Enable(False)
        obj = self.GetObject('check_self')
        (w, h) = obj.GetSize()
        (x, y) = obj.GetPos()
        self.m_PointNormalAccount = interface.CCheckBox(self, w, h, alpha=0, msgid=2)
        self.m_PointNormalAccount.SetPos(x, y)
        self.m_PointEmail = interface.CCheckBox(self, w, h, alpha=0, msgid=3)
        (x, y) = self.GetObject('check_email').GetPos()
        self.m_PointEmail.SetPos(x, y)
        self.m_PointImg = C_object.CImagesObject(self, 'login/selected.igs', interface.UIPath)
        self.m_PointImg.SetShow(False)
        self.OnMessage(2)
        return

    def ShowSuccess(self, itype, ret, point):
        import commondialog
        note = ''
        if itype == 6:
            if ret == 0:
                note = '綁定成功'
            else:
                note = '綁定失敗'
        elif itype == 7:
            if ret == 0:
                note = '解綁成功，您的帳戶還剩下%d點' % point
            else:
                note = '解綁失敗'
        else:
            return
        import dc_error_code
        try:
            msg = '，' + dc_error_code.ERROR_MSG[ret]
        except IndexError:
            msg = ''

        commondialog.ShowMessageBox(note + msg, '確定')
        return

    def OnMessage(self, msgid):
        if msgid == 5:
            import netlogin
            if self.m_PointNormalAccount.IsSelected():
                name = self.m_SelfAccountEdit.GetText()
                errmsg = None
                if len(name) <= 5:
                    errmsg = '自定義帳號長度不能小於3個漢字(6個英文字符)'
                elif name[0].isdigit():
                    errmsg = '自定義帳號的第一個字符不能為數字'
                elif name.isdigit():
                    errmsg = b'\xbb\xc6\xb4j\xa5l\xac\x7f\xa5\xa4\xb9\xbe\xb2\xfd\xb1\xad\xb2\xdf\xa1\xdb\xa6r'
                elif (name[0] == 'A' or name[0] == 'a') and name[1:].isdigit():
                    errmsg = '自定義帳號不能為 A(a)+數字 的形式'
                elif name[0].isalpha() and name[1].isalpha() and name[2:].isdigit():
                    errmsg = '自定義帳號不能為「字母+字母+數字」的形式'
                if errmsg != None:
                    import commondialog
                    commondialog.ShowMessageBox(errmsg, '確定')
                    return
            elif self.m_PointEmail.IsSelected():
                name = self.m_EmailEdit.GetText()
                if len(name) < 1:
                    return
            else:
                return
            netlogin.C2SBindAccount(name)
        elif msgid == 6:
            import netlogin
            if self.m_PointNormalAccount.IsSelected():
                name = self.m_SelfAccountEdit.GetText()
                if len(name) < 1:
                    return
            elif self.m_PointEmail.IsSelected():
                name = self.m_EmailEdit.GetText()
                if len(name) < 1:
                    return
            else:
                return
            netlogin.C2SReleaseBind(name)
        elif msgid == 7:
            Show(False)
            import selectrole
            selectrole.Show(True)
        elif msgid == 2:
            if self.m_PointNormalAccount.IsSelected():
                return
            self.m_SelfAccountEdit.Enable(True)
            self.m_SelfAccountEdit.Active(True)
            self.m_EmailEdit.SetText('')
            self.m_EmailEdit.Enable(False)
            (x, y) = self.GetObject('check_self').GetPos()
            self.m_PointImg.SetPos(x, y)
            self.m_PointImg.SetShow(True)
            self.m_PointNormalAccount.Select(True)
            self.m_PointEmail.Select(False)
        elif msgid == 3:
            if self.m_PointEmail.IsSelected():
                return
            self.m_SelfAccountEdit.SetText('')
            self.m_SelfAccountEdit.Enable(False)
            self.m_EmailEdit.Enable(True)
            self.m_EmailEdit.Active(True)
            (x, y) = self.GetObject('check_email').GetPos()
            self.m_PointImg.SetPos(x, y)
            self.m_PointImg.SetShow(True)
            self.m_PointNormalAccount.Select(False)
            self.m_PointEmail.Select(True)
        return


return
