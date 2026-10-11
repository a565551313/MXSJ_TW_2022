# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\getaccount.py
import C_object, interface, wrapinterface, combdialog
g_GetAccount = None

class CGetAccount(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/getaccount.dlg')
        import combmacro
        btn = self.GetObject('btn_num')
        (w, h) = btn.GetSize()
        (x, y) = btn.GetPos()
        self.m_NumBtn = interface.CCheckBox(self, w, h, alpha=0, msgid=5)
        self.m_NumBtn.SetPos(x, y)
        (x, y) = self.GetObject('account').GetPos()
        self.m_GreyInput1 = interface.CImagesObject(self, 'login/grey_input.igs', interface.UIPath)
        self.m_GreyInput1.SetPos(x, y)
        btn = self.GetObject('btn_name')
        (w, h) = btn.GetSize()
        (x, y) = btn.GetPos()
        self.m_NameBtn = interface.CCheckBox(self, w, h, alpha=0, msgid=6)
        self.m_NameBtn.SetPos(x, y)
        (x, y) = self.GetObject('name').GetPos()
        self.m_GreyInput2 = interface.CImagesObject(self, 'login/grey_input.igs', interface.UIPath)
        self.m_GreyInput2.SetPos(x, y)
        self.m_SelfAccountEdit = None
        self.m_NameEdit = None
        btn = self.GetObject('btn_email')
        (w, h) = btn.GetSize()
        (x, y) = btn.GetPos()
        self.m_EmailBtn = interface.CCheckBox(self, w, h, alpha=0, msgid=7)
        self.m_EmailBtn.SetPos(x, y)
        (x, y) = self.GetObject('email').GetPos()
        self.m_GreyInput3 = interface.CImagesObject(self, 'login/grey_input.igs', interface.UIPath)
        self.m_GreyInput3.SetPos(x, y)
        (x, y) = self.GetObject('id').GetPos()
        self.m_GreyInput4 = interface.CImagesObject(self, 'login/grey_input.igs', interface.UIPath)
        self.m_GreyInput4.SetPos(x, y)
        self.m_EmailEdit = None
        self.m_IDEdit = None
        (x, y) = self.GetObject('btn_num').GetPos()
        self.m_PointImg = C_object.CImagesObject(self, 'login/selected.igs', interface.UIPath)
        self.m_PointImg.SetPos(x, y)
        self.m_SelectFlag = 0
        self.m_GetAccountTime = 0
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import misc, sound
            sound.Play('action/button.wav')
            import C_sys
            t = misc.Time()
            f = C_sys.Record(t - self.m_GetAccountTime < 120)
            if f:
                import usermacro
                usermacro.PROMPT_MSG('操作過於頻繁，請稍後再嘗試')
                return
            self.m_GetAccountTime = t

            def _getacct(data, succeed):
                import commondialog
                if not succeed:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    (head, body) = data.split('\r\n\r\n')
                except ValueError:
                    return

                result = body.split()
                if result[0][:2] != '0,':
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    acct_count = int(result[0][2:].strip())
                except ValueError:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return

                if acct_count <= 0:
                    commondialog.ShowMessageBox('沒有得到有效的帳號信息', '確定')
                    return
                acct_count = min(acct_count, len(result) - 1)
                txt = '您的帳號如下：#Y'
                for i in xrange(acct_count):
                    if i % 5 == 0:
                        txt += '#r%-12s' % result[i + 1]
                    else:
                        txt += '%-12s' % result[i + 1]

                import combmacro
                commondialog.HideMessageBox()
                self.m_Result = combmacro.CRICHTEXT(C_object.CRichTextObject, 'result', self, txt, interface.FontLT14E_1, 16776960)
                return

            def _getemail(data, succeed):
                import commondialog
                if not succeed:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    (head, body) = data.split('\r\n\r\n')
                except ValueError:
                    return

                if body[:2] == '91':
                    commondialog.ShowMessageBox('郵箱和角色ID不匹配', '確定')
                elif body[:3] == '0,0':
                    commondialog.ShowMessageBox('找回成功，帳號信息已發送至您的郵箱', '確定')
                elif body[:3] == '0,1':
                    commondialog.ShowMessageBox('郵件發送失敗，請確認您填寫的是正確郵箱', '確定')
                else:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                return

            import C_sys, net, commondialog, misc
            try:
                mac = misc.GetMAC()
            except:
                commondialog.ShowMessageBox('無法獲取帳號信息', '確定')
                return
            else:
                import gameurl
                if self.m_SelectFlag == 0:
                    web = gameurl.GETPWD_CURRENTPC_URL % mac
                    import security
                    token_key = security.CreateOneEncodeGuid()
                    web += '&tokenkey=%s' % token_key
                    net.CHttpObject(web, 'get', _getacct)
                elif self.m_SelectFlag == 1:
                    if self.m_SelfAccountEdit == None or self.m_NameEdit == None:
                        return
                    account = self.m_SelfAccountEdit.GetText()
                    name = self.m_NameEdit.GetText()
                    if len(account) < 1:
                        commondialog.ShowMessageBox('請填寫正確的自定義帳號名', '確定')
                        return
                    if len(name) < 2:
                        commondialog.ShowMessageBox('請填寫正確的身份証姓名', '確定')
                        return
                    web = gameurl.GETPWD_ACCOUNT_NAME_URL % mac
                    web += '&account=%s&name=%s' % (account, name)
                    import security
                    token_key = security.CreateOneEncodeGuid()
                    web += '&tokenkey=%s' % token_key
                    net.CHttpObject(web, 'get', _getacct)
                elif self.m_SelectFlag == 2:
                    if self.m_EmailEdit == None or self.m_IDEdit == None:
                        return
                    import selectserver
                    if selectserver.g_LoginServer == None or len(selectserver.g_LoginServer) < 2:
                        return
                    pos = selectserver.g_LoginServer[1].find('(')
                    if pos < 0:
                        pos = selectserver.g_LoginServer[1].find('（')
                    if pos < 0:
                        servername = selectserver.g_LoginServer[1]
                    else:
                        servername = selectserver.g_LoginServer[1][:pos]
                    email = self.m_EmailEdit.GetText()
                    userid = self.m_IDEdit.GetText()
                    web = gameurl.GETPWD_EMAIL_ROLE_URL % (servername, userid, email)
                    import security
                    token_key = security.CreateOneEncodeGuid()
                    web += '&tokenkey=%s' % token_key
                    net.CHttpObject(web, 'get', _getemail)
                else:
                    return
                commondialog.ShowMessageBox('獲取帳號信息中...', '確定')
        elif msgid == 2:
            Show(False)
            import loginin, sound
            sound.Play('action/button.wav')
            loginin.Show(True)
        elif msgid == 5:
            import sound
            sound.Play('action/button.wav')
            if self.m_SelectFlag == 0:
                return
            self.m_SelectFlag = 0
            self.m_GreyInput1.SetShow(True)
            self.m_GreyInput2.SetShow(True)
            self.m_GreyInput3.SetShow(True)
            self.m_GreyInput4.SetShow(True)
            (x, y) = self.GetObject('btn_num').GetPos()
            self.m_PointImg.SetPos(x, y)
            if self.m_SelfAccountEdit:
                self.m_SelfAccountEdit.Active(False)
            if self.m_NameEdit:
                self.m_NameEdit.Active(False)
            for obj in (self.m_SelfAccountEdit, self.m_NameEdit, self.m_EmailEdit, self.m_IDEdit):
                if obj:
                    obj.Active(False)

            self.m_SelfAccountEdit = None
            self.m_NameEdit = None
            self.m_EmailEdit = None
            self.m_IDEdit = None
        elif msgid == 6:
            import sound
            sound.Play('action/button.wav')
            if self.m_SelectFlag == 1:
                return
            self.m_SelectFlag = 1
            self.m_GreyInput1.SetShow(False)
            self.m_GreyInput2.SetShow(False)
            self.m_GreyInput3.SetShow(True)
            self.m_GreyInput4.SetShow(True)
            (x, y) = self.GetObject('btn_name').GetPos()
            self.m_PointImg.SetPos(x, y)
            import combmacro
            self.m_SelfAccountEdit = combmacro.CEDIT(interface.CEdit, 'account_base', self, 0, interface.FontLT14E_1, linecolor=0)
            self.m_SelfAccountEdit.Active(True)
            self.m_NameEdit = combmacro.CEDIT(interface.CEdit, 'name_base', self, 0, interface.FontLT14E_1, linecolor=0)
            self.m_SelfAccountEdit.SetNextEdit(self.m_NameEdit)
            self.m_NameEdit.SetNextEdit(self.m_SelfAccountEdit)
            self.m_EmailEdit = None
            self.m_IDEdit = None
        elif msgid == 7:
            import sound
            sound.Play('action/button.wav')
            if self.m_SelectFlag == 2:
                return
            self.m_SelectFlag = 2
            self.m_GreyInput1.SetShow(True)
            self.m_GreyInput2.SetShow(True)
            self.m_GreyInput3.SetShow(False)
            self.m_GreyInput4.SetShow(False)
            (x, y) = self.GetObject('btn_email').GetPos()
            self.m_PointImg.SetPos(x, y)
            import combmacro
            self.m_EmailEdit = combmacro.CEDIT(interface.CEdit, 'email_base', self, 0, interface.FontLT14E_1, linecolor=0)
            self.m_EmailEdit.Active(True)
            self.m_EmailEdit.SetLimit(32)
            self.m_IDEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'id_base', self, 0, interface.FontLT14E_1, linecolor=0)
            self.m_IDEdit.SetLimit(9)
            self.m_EmailEdit.SetNextEdit(self.m_IDEdit)
            self.m_IDEdit.SetNextEdit(self.m_EmailEdit)
            self.m_SelfAccountEdit = None
            self.m_NameEdit = None
        return


def Show(flag):
    global g_GetAccount
    if flag:
        g_GetAccount = CGetAccount(interface.DialogPanel)
    else:
        g_GetAccount = None
    return


return
