# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\register.py
import C_sys, combdialog, combmacro, gameurl, interface, net, ui, usermacro, wrapinterface
g_AccountInfo = {}
g_CDKey = '1234567890123456'
g_ConfirmDlg = None
g_RegisterPanel = None

def ModuleReset():
    global g_AccountInfo
    global g_CDKey
    global g_ConfirmDlg
    global g_RegisterPanel
    g_AccountInfo = {}
    g_CDKey = '1234567890123456'
    g_ConfirmDlg = None
    g_RegisterPanel = None
    return


class CRegEdit(interface.CEdit):

    def AddChar(self, c):
        if c.isalnum():
            interface.CEdit.AddChar(self, c)
        else:
            import usermacro
            usermacro.PROMPT_MSG('只能使用數字或字母')
        return

    def Active(self, flag):
        interface.CEdit.Active(self, flag)
        if hasattr(self, 'm_ActiveIdx'):
            self.GetParent().OnActive(self.m_ActiveIdx, flag)
        return


class PhoneEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit():
            interface.CEdit.AddChar(self, c)
        return


class _IdentityEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit() or c == 'x' or c == 'X':
            interface.CEdit.AddChar(self, c)
        return

    def MsgEnter(self):
        self.GetParent().OnMessage(2)
        return


class CAdvPwdEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit():
            CRegEdit.AddChar(self, c)
        else:
            import usermacro
            usermacro.PROMPT_MSG('高級密碼只能使用數字')
        return


class CMyEdit(CRegEdit):

    def AddChar(self, char):
        if IsValid(char) and char != '@':
            interface.CEdit.AddChar(self, char)
        return


class CMailEdit(CRegEdit):

    def DeleteChar(self):
        CRegEdit.DeleteChar(self)
        if hasattr(self, 'm_EditChange'):
            self.GetParent().OnEditChange(self)
        return

    def AddChar(self, c):
        if IsValid(c):
            interface.CEdit.AddChar(self, c)
        if hasattr(self, 'm_EditChange'):
            self.GetParent().OnEditChange(self)
        return


class C2980MailEdit(CRegEdit):

    def AddChar(self, char):
        if char.isalnum():
            interface.CEdit.AddChar(self, char)
        return


def IsValid(txt):
    _invalid = ('"', "'", '/', '\\', '=', '+', '|', ';', ':', '[', ']', '{', '}', '?',
                '*', ',', '(', ')', '&', '^', '%', '$', '#', '!', '~', '`')
    for c in _invalid:
        if c in txt:
            return False

    return True


def ShowError(err, ecode=0, errmsg=''):
    import commondialog, dc_error_code
    if err not in dc_error_code.ERROR_MSG:
        if errmsg:
            msg = errmsg + '-%d' % err
        else:
            msg = '未知錯誤(%d)' % err
    else:
        msg = dc_error_code.ERROR_MSG[err]
    commondialog.ShowNewMessageBox(msg, '確定')
    return


def ShowConfirmDlg(flag):
    global g_ConfirmDlg
    if flag == 1:
        g_ConfirmDlg = None
    else:
        g_ConfirmDlg = CConfirm(interface.DialogPanel)
    return


class CConfirm(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/confirm.dlg')
        self.Topmost()
        import chatoutput, servicedata
        result = [_[1] for s in servicedata.CONFIRM_MSG.split('\n')]
        output = self.GetObject('output')
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(self, w, h, 0, 0, result, txt_font=interface.FontLT14_3, txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.SetChatCursor(0)
        self.m_PublicTxtBox.ResetFromCursor()
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import netlogin, selectrole, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            netlogin.C2SConfirmRegInfo()
            if selectrole.g_SelectRoleDlg:
                interface.SetDefaultButton(selectrole.g_SelectRoleDlg.GetObject('btn_Login'))
            ShowConfirmDlg(1)
        elif msgid == 2:
            import main, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            main.CloseGame()
        return


class CRegPanel1(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg1.dlg')
        import chatoutput, servicedata
        result = [_[1] for s in servicedata.SERVICE_MSG.split('\n')]
        output = self.GetObject('output')
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(self, w, h, 0, 0, result, txt_font=interface.FontLT12_1, txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.Refresh()
        self.m_PublicTxtBox.ScrollTo(0)
        self.m_ImgStep = ui.CImage(self, 'combdialog/娸芞/肮砩沭遴.igs', 'interface')
        (x, y) = self.GetObject('reginfo1').GetPos()
        self.m_ImgStep.SetPos(x, y)
        self.m_ImgStep.SetFrame(1)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            Step(1)
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            import clickcounter
            clickcounter.LoginLog('註冊帳號服務條款頁-我同意')
        elif msgid == 2:
            import main, sound
            main.CloseGame()
            import sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
        elif msgid == 3:
            Show(False)
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            import clickcounter
            clickcounter.LoginLog('註冊帳號服務條款頁-我拒絕')
            try:
                import mainpage
                mainpage.Show(True)
            except:
                import main
                main.doreturn(interface.CBaseObject(None))

        return


class CCheckCodeBox(interface.CBoxObject):

    class CClickObject(interface.CClickObject):

        def Enter(self):
            self.m_Tips = wrapinterface.CTextTips(self.GetParent(), -1, '點擊刷新驗証碼', interface.FontLT14_3, direct=1)
            return

        def Leave(self):
            self.m_Tips.SetShow(False)
            return

    class CClickImages(interface.CImagesObject, CClickObject):

        def __init__(self, parent, filename, path, msgid):
            interface.CImagesObject.__init__(self, parent, filename, path)
            interface.CClickObject.__init__(self, msgid)
            return

    class CClickBitmap(interface.CBitmapObject, CClickObject):

        def __init__(self, parent, filename, path, msgid):
            interface.CBitmapObject.__init__(self, parent, filename, path)
            interface.CClickObject.__init__(self, msgid)
            return

    def __init__(self, parent):
        interface.CBoxObject.__init__(self, parent, 0, 0, 0, 0)
        return

    def ShowCodeImg(self, b64str):
        if getattr(self, 'm_DelayTime', None):
            self.m_DelayTime.Release()
            self.m_DelayTime = None
        self.m_InRequest = False
        import os, misc
        path = 'photo'
        try:
            os.makedirs(path)
        except:
            pass

        try:
            os.makedirs(path + '\\register')
        except:
            pass

        timetxt = '%d%02d%02d-%02d%02d%02d' % misc.LocalTime()[:6]
        try:
            r = misc.RandInt(0, 9)
            fname = 'register\\' + str(r) + timetxt + '.jpg'
            import base64
            sDecoded = base64.b64decode(b64str)
            f = file(path + '\\' + fname, 'wb')
            f.write(sDecoded)
            f.close()
            self.m_CodeImg = CCheckCodeBox.CClickBitmap(self, fname, path, 1)
        except Exception, e:
            print 'Load CodeImg Err:', e
            self.m_CodeImg = CCheckCodeBox.CClickImages(self, 'combdialog/娸芞/openerror.igs', interface.UIPath, 1)
            self.m_CodeImg.SetPos(7, 0)
            return False

        return True

    def ShowFailCodeImg(self):
        self.m_InRequest = False
        return

    def RequestNewCode(self):
        self.m_InRequest = True
        webargs = 'acct_reg.aspx?act=flushcode&gatesrc=mx'
        web = gameurl.REGISTER_URL + webargs
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_REGCODE)
        if getattr(self, 'm_DelayTime', None):
            self.m_DelayTime.Release()

        def delay(obj):
            obj.m_InRequest = False
            return

        self.m_DelayTime = self.CreatePyCommand(150, delay)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            if getattr(self, 'm_InRequest', None):
                usermacro.PROMPT_MSG('正在請求中')
                return
            self.RequestNewCode()
        return


class CRegPanel2(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg2.dlg')
        self.CreateEdits()
        (x, y) = self.GetObject('youxiang').GetPos()
        import wraptextobj
        self.m_YouXiang = wraptextobj.CUnderLineClickText(self, x, y, '點擊註冊2980郵箱', 65535, 16711680, interface.FontLT14_3, msgid=3)
        self.m_ImgStep = ui.CImage(self, 'combdialog/娸芞/沓迡訧蹋.igs', 'interface')
        (x, y) = self.GetObject('reginfo2').GetPos()
        self.m_ImgStep.SetPos(x, y)
        self.m_ImgStep.SetFrame(1)
        return

    def CreateEdits(self):
        self.m_PwdEdit = combmacro.CEDIT(CRegEdit, 'pwd', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_PwdEdit.m_ActiveIdx = 'pwd'
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = combmacro.CEDIT(CRegEdit, 'pwd2', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_PwdEdit2.m_ActiveIdx = 'pwd2'
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.m_IsPassword = True
        self.m_EmailEdit = combmacro.CEDIT(CMailEdit, 'email', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_EmailEdit.m_ActiveIdx = 'email'
        self.m_EmailEdit.SetLimit(32)
        self.m_EmailEdit.Active(True)
        self.m_EmailEdit2 = combmacro.CEDIT(CMailEdit, 'email2', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_EmailEdit.m_EditChange = True
        self.m_EmailEdit2.m_ActiveIdx = 'email2'
        self.m_EmailEdit2.SetLimit(32)
        self.m_EmailEdit2.SetShow(False)
        self.GetObject('txt_Mail2').SetShow(False)
        self.GetObject('img_Mail2Bg').SetShow(False)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_EmailEdit)
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        self.m_EmailEdit2.SetNextEdit(self.m_PwdEdit)
        self.m_CodeEdit = combmacro.CEDIT(CRegEdit, 'edt_Code', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_CodeEdit.m_ActiveIdx = 'code'
        self.m_CodeEdit.SetLimit(4)
        self.m_CodeEdit.SetShow(False)
        self.GetObject('txt_Code').SetShow(False)
        self.GetObject('txt_CodeBg').SetShow(False)
        import wraptextobj
        self.m_RefershCode = combmacro.CCLICKTEXT(wraptextobj.CUnderLineClickText, 'txt_RefershCode', self, '換張圖片', 65535, 16711680, interface.FontLT14_3, 4)
        self.m_RefershCode.SetShow(False)
        return

    def OnButtonEnter(self, btn):
        if btn.m_MsgID == 99:
            btn.m_tips = wrapinterface.CTextTips(self, 220, '#cfff650選中此項會自動將您註冊的帳號綁定到填寫的郵箱地址上，綁定後將允許您使用郵箱作為帳號登錄遊戲', interface.FontLT14_3, direct=1)
            btn.m_tips.SetOwner(btn)
        return

    def OnButtonLeave(self, btn):
        if btn.m_MsgID == 99:
            btn.m_tips = None
        return

    def IdentityCheck(self, identity):
        if len(identity) != 18:
            return True
        s = 0
        A = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 3, 4, 5, 6, 7, 8, 9]
        for (i, c) in enumerate(identity[:17]):
            if not c.isdigit():
                return False
            s += int(c) * A[i]

        s = s % 11
        code = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25][s]
        if identity[17].lower() != code:
            return False
        else:
            return True
        return

    def DoCheck(self):
        pwd = self.m_PwdEdit.GetText()
        self.m_PwdEdit.Active(True)
        if len(pwd) < 6:
            self.m_PwdEdit.Active(True)
            return '請輸入正確格式的密碼'
        if pwd != self.m_PwdEdit2.GetText():
            self.m_PwdEdit2.Active(True)
            return '兩次輸入的密碼不匹配'
        email = self.m_EmailEdit.GetText().strip()
        if self.CheckEmail(email) == False:
            self.m_EmailEdit.Active(True)
            return '請輸入正確格式的郵箱'
        if self.m_EmailEdit2.GetShow():
            email2 = self.m_EmailEdit2.GetText().strip()
            if email != email2:
                usermacro.PROMPT_MSG('兩次輸入的郵箱不一致，請核對正確後再提交')
                self.m_EmailEdit2.Active(True)
                return ''
        if self.m_CodeEdit.GetShow():
            code = self.m_CodeEdit.GetText().strip()
            if len(code) < 4:
                usermacro.PROMPT_MSG('請輸入正確的驗証碼')
                return ''
        return

    def CheckEmail(self, email):
        if len(email) < 5 or len(email) > 50:
            return False
        import re
        pattStr = '^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$'
        patt = re.compile(pattStr)
        mat = patt.match(email)
        if mat is None:
            return False
        return True

    def Save(self):
        g_AccountInfo['Password'] = self.m_PwdEdit.GetText()
        g_AccountInfo['Password2'] = self.m_PwdEdit2.GetText()
        g_AccountInfo['Email'] = self.m_EmailEdit.GetText().strip()
        return

    def OnActive(self, activeIdx, flag):
        if flag == False:
            return
        note = {'pwd': '登錄密碼僅可由字母或者數字組成,長度為6~16位。', 
           'pwd2': '請再次輸入您的登錄密碼', 
           'email': '請輸入您的聯繫郵箱（#Y該郵箱將作為您登錄遊戲時所用的帳號#n）', 
           'email2': '請再次輸入您的郵箱', 
           'code': '請填寫圖片中的字符，不區分大小寫'}
        if activeIdx in note:
            self.m_Note = combmacro.CRICHTEXT(interface.CRichTextObject, 'note' + str(activeIdx), self, note[activeIdx], interface.FontLT14_3, interface.COLOR_1)
        else:
            self.m_Note = None
        return

    def OnEditChange(self, ctrl):
        if getattr(ctrl, 'm_ActiveIdx', None) == 'email':
            email = ctrl.GetText()
            email = email.strip()
            email = email.lower()
            flag = email.endswith('@qq.com') or email.endswith('@vip.qq.com')
            self.GetObject('txt_Mail2').SetShow(flag)
            self.GetObject('img_Mail2Bg').SetShow(flag)
            self.m_EmailEdit2.SetShow(flag)
            if flag:
                self.m_EmailEdit.SetNextEdit(self.m_EmailEdit2)
            else:
                self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        return

    def DoNext(self):
        msg = self.DoCheck()
        import sound, sounddefine
        sound.Play(sounddefine.PATH_BTN_SOUND)
        if msg is not None:
            if msg:
                import commondialog
                commondialog.ShowNewMessageBox(msg, '確定')
            return
        import clientinterface
        if clientinterface.CheckRegisterTime():
            import commondialog
            commondialog.ShowNewMessageBox('註冊過於頻繁，請稍後再試', '確定')
            return
        self.Save()
        pwd = g_AccountInfo['Password']
        email = g_AccountInfo['Email']
        import device
        try:
            mac = device.GetMAC()
        except:
            mac = '0'

        import md5
        pwd = md5.new(pwd).hexdigest()
        args = 'gatesrc=mx&encrypt=true&password=%s' % pwd
        args += '&email=%s' % email
        args += '&mac=%s' % mac
        import commondialog, misc
        commondialog.ShowNewMessageBox('正在註冊，請等待...', '取消')
        if getattr(self, 'm_Vregval', None):
            vcode = self.m_CodeEdit.GetText()
            vcode = vcode.strip()
            vcode = vcode.lower()
            args += '&vcode=%s' % vcode
            args += '&vregval=%s' % self.m_Vregval
        try:
            s = '&tgaccount=%s' % misc.GetTGID()
            args += s
        except:
            pass

        import main
        if main.g_Adsid:
            args += '&adsid=%s' % main.g_Adsid
        webargs = 'acct_reg.aspx?' + args
        print webargs
        webargs = clientinterface.GetCheckCode(webargs, {})
        print '加驗証後：', webargs
        import net
        web = gameurl.REGISTER_URL + webargs
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_REGISTERGAME, args)
        return

    def ShowCheckCode(self, imgbytes, vregval):
        if not getattr(self, 'm_CheckCode', None):
            self.m_CheckCode = CCheckCodeBox(self)
            (x, y) = self.GetObject('img_Code').GetPos()
            self.m_CheckCode.SetPos(x, y)
        self.m_CheckCode.ShowCodeImg(imgbytes)
        self.m_Vregval = vregval
        self.m_CodeEdit.SetShow(True)
        self.GetObject('txt_Code').SetShow(True)
        self.GetObject('txt_CodeBg').SetShow(True)
        self.m_RefershCode.SetShow(True)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.Save()
            Step(0)
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
        elif msgid == 2:
            self.DoNext()
        elif msgid == 3:
            Register2980(0)
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            import clickcounter
            clickcounter.LoginLog('註冊帳號填寫資料頁-註冊2980郵箱')
        elif msgid == 4:
            if hasattr(self, 'm_CheckCode'):
                self.m_CheckCode.OnMessage(1)
        return


def Register2980(step):
    global g_RegisterPanel
    _panels = [
     CRegPanel2_2980, CRegPanel3_2980]
    g_RegisterPanel = _panels[step](interface.DialogPanel)
    return


OP_CHECKEMAIL = 1
OP_CHECKPHONE = 2
OP_REGISTER = 3
OP_PHONECODE = 4
OP_PHONEVOICE = 5
OP_REGISTERGAME = 6
OP_REGCODE = 7
PORTKEY = '0066b3f7-4183-4834-9adf-9695c220ea48'

class CRegPanel2_2980(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg4.dlg')
        self.m_CheckPhoneNum = {}
        self.m_CheckEmail = {}
        self.m_PhonecodeResult = {}
        self.GetObject('chk_agree').SetSelect(True)
        self.m_PwdEdit = combmacro.CEDIT(CRegEdit, 'pwd', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_PwdEdit.m_ActiveIdx = 'pwd'
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = combmacro.CEDIT(CRegEdit, 'pwd2', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_PwdEdit2.m_ActiveIdx = 'pwd2'
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.m_IsPassword = True
        self.m_PhoneEdit = combmacro.CEDIT(PhoneEdit, 'phone', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_PhoneEdit.m_ActiveIdx = 'phone'
        self.m_PhoneEdit.SetLimit(11)
        self.m_CodeEdit = combmacro.CEDIT(PhoneEdit, 'yanzhengma', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_CodeEdit.m_ActiveIdx = 'yanzhengma'
        self.m_CodeEdit.SetLimit(6)
        self.m_EmailEdit = combmacro.CEDIT(C2980MailEdit, 'email', self, 16777215, interface.FontLT14_3, linecolor=16777215)
        self.m_EmailEdit.m_ActiveIdx = 'email'
        self.m_EmailEdit.SetLimit(16)
        self.m_EmailEdit.Active(True)
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_PhoneEdit)
        self.m_PhoneEdit.SetNextEdit(self.m_CodeEdit)
        import wraptextobj
        (x, y) = self.GetObject('check').GetPos()
        self.m_Check = wraptextobj.CUnderLineClickText(self, x, y, '檢測', 65535, 16711680, interface.FontLT14_3, msgid=5)
        (x, y) = self.GetObject('click').GetPos()
        self.m_Click = wraptextobj.CUnderLineClickText(self, x, y, '點擊這裡', 65535, 16711680, interface.FontLT14_3, msgid=10)
        (x, y) = self.GetObject('service').GetPos()
        self.m_Service = wraptextobj.CUnderLineClickText(self, x, y, '《2980服務條款》', 65535, 16711680, interface.FontLT14_3, msgid=11)
        self.m_Timer = None
        return

    def OnButtonEnter(self, btn):
        if btn.m_MsgID == 99:
            btn.m_tips = wrapinterface.CTextTips(self, 220, '#cfff650選中此項會自動將您註冊的帳號綁定到填寫的郵箱地址上，綁定後將允許您使用郵箱作為帳號登錄遊戲', interface.FontLT14_3, direct=1)
            btn.m_tips.SetOwner(btn)
        return

    def OnButtonLeave(self, btn):
        if btn.m_MsgID == 99:
            btn.m_tips = None
        return

    def IdentityCheck(self, identity):
        if len(identity) != 18:
            return True
        s = 0
        A = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 3, 4, 5, 6, 7, 8, 9]
        for (i, c) in enumerate(identity[:17]):
            if not c.isdigit():
                return False
            s += int(c) * A[i]

        s = s % 11
        code = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25][s]
        if identity[17].lower() != code:
            return False
        else:
            return True
        return

    def DoCheck(self):
        email = self.m_EmailEdit.GetText()
        email = email.strip()
        email = email.lower()
        if len(email) < 5:
            self.m_EmailEdit.Active(True)
            return '郵箱不符合要求，請檢查'
        if email.isdigit():
            self.m_EmailEdit.Active(True)
            return '郵箱地址必須包含字母'
        pwd = self.m_PwdEdit.GetText()
        if len(pwd) < 6:
            self.m_PwdEdit.Active(True)
            return '密碼不符合要求，請檢查'
        if pwd != self.m_PwdEdit2.GetText():
            self.m_PwdEdit.Active(True)
            return '兩次輸入的密碼不一致'
        phone = self.m_PhoneEdit.GetText()
        if len(phone) != 11:
            self.m_PhoneEdit.Active(True)
            return '手機號碼長度不符合要求, 請檢查'
        phonecode = self.m_CodeEdit.GetText()
        if len(phonecode) != 6:
            self.m_CodeEdit.Active(True)
            return '驗証碼要求長度六位, 請檢查'
        result = self.m_CheckEmail.get(email)
        if result is None:
            self.RequestEmailValid(email, self.DoRegist, None)
            return '正在檢查帳號, 請稍候'
        elif result[0] != 250:
            self.m_EmailEdit.Active(True)
            return result[1]
        result = self.m_CheckPhoneNum.get(phone)
        if result is None:
            self.RequestPhoneValid(phone, self.DoRegist, None)
            return
        elif result[0] != 250:
            self.m_PhoneEdit.Active(True)
            return result[1]
        return

    def CheckEmail(self, email):
        msg = '請輸入正確格式的郵箱'
        import re
        pattStr = '^([a-z0-9A-Z]+[_-|\\.]?)+[a-z0-9A-Z]@([a-z0-9A-Z]+(-[a-z0-9A-Z]+)?\\.)+[a-zA-Z]{2,}$'
        patt = re.compile(pattStr)
        mat = patt.match(email)
        if mat is None:
            return msg
        return

    def Save(self):
        g_AccountInfo['Password'] = self.m_PwdEdit.GetText()
        g_AccountInfo['Password2'] = self.m_PwdEdit2.GetText()
        g_AccountInfo['Email'] = self.m_EmailEdit.GetText().strip()
        return

    def GetMailUrl(self):
        if 'ResultEmail' not in g_AccountInfo:
            return
        email = g_AccountInfo['ResultEmail']
        return gameurl.GetMailUrl(email)

    def OnActive(self, activeIdx, flag):
        if flag == False:
            return
        note = {'pwd': '登錄密碼僅可由字母或者數字組成，長度為6~16位。', 
           'pwd2': '請再次輸入您的登錄密碼', 
           'email': '請輸入5至16個字符（字母或數字），必須包含字母。字母不區分大小寫', 
           'phone': '手機號必須是11位數字。一個手機號碼只允許綁定一個2980郵箱', 
           'yanzhengma': '請輸入手機收到的短信驗証碼'}
        if activeIdx in note:
            self.m_Note = combmacro.CRICHTEXT(interface.CRichTextObject, 'note', self, note[activeIdx], interface.FontLT14_3, interface.COLOR_1)
        else:
            self.m_Note = None
        return

    def UpdateCheckPhoneNum(self, phone, result, msg):
        self.m_CheckPhoneNum[phone] = (
         result, msg)
        return

    def RequestPhoneValid(self, phone, callback, *args):
        webargs = '/funswregister.aspx?'
        webargs += 'act=dy_2980auth'
        webargs += '&portkey=%s' % PORTKEY
        webargs += '&checktype=phone'
        webargs += '&phoneUserName=%s' % phone
        web = gameurl.REGISTER_2980_URL + webargs
        print 'RequestPhoneValid', web
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_CHECKPHONE, phone, callback, *args)
        return

    def UpdatePhoneCodeResult(self, phone, result):
        if result == 250:
            self.m_PhonecodeResult[phone] = C_sys.GetTime()
        self.m_PhonecodeResult['LastClick'] = C_sys.GetTime()
        return

    def RequestPhoneCode(self, phone):
        webargs = '/funswregister.aspx?'
        webargs += 'act=dy_2980code'
        webargs += '&portkey=%s' % PORTKEY
        webargs += '&phone=%s' % phone
        web = gameurl.REGISTER_2980_URL + webargs
        print 'RequestPhoneCode', web
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_PHONECODE, phone)
        self.RefreshGetValKey()
        return

    def RequestPhoneVoiceCode(self, phone):
        webargs = '/funswregister.aspx?'
        webargs += 'act=dy_2980code'
        webargs += '&codeType=1'
        webargs += '&portkey=%s' % PORTKEY
        webargs += '&phone=%s' % phone
        web = gameurl.REGISTER_2980_URL + webargs
        print 'RequestVoiceCode', web
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_PHONEVOICE, phone)
        return

    def UpdateCheckEmail(self, email, result, msg):
        self.m_CheckEmail[email] = (result, msg)
        return

    def RequestEmailValid(self, email, callback, *args):
        webargs = '/funswregister.aspx?'
        webargs += 'act=dy_2980auth'
        webargs += '&portkey=%s' % PORTKEY
        webargs += '&checktype=name'
        webargs += '&phoneUserName=%s' % email
        web = gameurl.REGISTER_2980_URL + webargs
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_CHECKEMAIL, email, callback, *args)
        return

    def EncryptPwd(self, pwd):
        import md5
        md5pwd = md5.md5(pwd)
        return md5pwd.hexdigest()

    def DoRegist(self):
        msg = self.DoCheck()
        if msg:
            import commondialog
            commondialog.ShowNewMessageBox(msg, '確定')
            return
        self.Save()
        pwd = g_AccountInfo['Password']
        email = g_AccountInfo['Email']
        phone = self.m_PhoneEdit.GetText()
        phonecode = self.m_CodeEdit.GetText()
        ery_pwd = self.EncryptPwd(pwd)
        import device
        mac = device.GetMAC()
        webargs = '/funswregister.aspx?'
        webargs += 'act=dy_2980adduser'
        webargs += '&password=%s' % ery_pwd
        webargs += '&accort=%s' % email
        webargs += '&phone=%s' % phone
        webargs += '&phonecode=%s' % phonecode
        webargs += '&portkey=%s' % PORTKEY
        webargs += '&name=&idnumber=&gate=mxgame'
        webargs += '&mac=%s' % mac
        import commondialog
        commondialog.ShowNewMessageBox('正在註冊中，請耐心等待...', '取消')
        web = gameurl.REGISTER_2980_URL + webargs
        net.CHttpObject(web, 'get', OnReceiveProcess, OP_REGISTER, email)
        return

    def RefreshGetValKey(self, cdTime=60):

        def downCount(obj, nowCount):
            nowCount -= 1
            obj.m_CountTime = nowCount
            if nowCount <= 0:
                obj.GetObject('btn_Getval').SetText('獲取驗証碼')
                obj.GetObject('btn_Getval').Enable(True)
                obj.ShowVoiceVerify()
                if obj.m_Timer:
                    obj.m_Timer.Release()
                    obj.m_Timer = None
                return
            else:
                obj.GetObject('btn_Getval').SetText('獲取驗証碼 %d' % nowCount)
                obj.GetObject('btn_Getval').Enable(False)
                return (nowCount,)
            return

        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        showText = '獲取驗証碼%s' % cdTime
        self.GetObject('btn_Getval').SetText(showText)
        self.GetObject('btn_Getval').Enable(False)
        self.m_Timer = self.CreatePyCommand(30, downCount, cdTime)
        return

    def ShowVoiceVerify(self):
        txt = '#u手機收不到短信，點擊這裡接收語音驗証碼#r(您將收到一個語音自動播放驗証碼的來電)#n'
        (x, y, w, h) = self.GetLocData('txt_Yuyin')
        self.m_VoiceVerify = interface.CClickRichText(self, x, y, w, txt, interface.COLOR_274, 65280, interface.FontLT12_1, 9)
        return

    def GetCheckCode(self):
        phone = self.m_PhoneEdit.GetText()
        import commondialog
        if len(phone) != 11:
            commondialog.ShowNewMessageBox('手機號碼不符合要求, 請檢查', '確定')
            return
        tm = C_sys.GetTime()
        lasttm = self.m_PhonecodeResult.get('LastClick')
        if lasttm:
            slot = (tm - lasttm) / 10000
            if slot < 60:
                usermacro.PROMPT_MSG('還需等待%d秒才能再次請求驗証碼' % (60 - slot))
                return
        lastsucesstm = self.m_PhonecodeResult.get(phone)
        if lastsucesstm:
            slot = (tm - lastsucesstm) / 10000
            if slot < 300:
                commondialog.ShowNewMessageBox('短信發送成功', '確定')
                self.m_PhonecodeResult['LastClick'] = tm
                return
        result = self.m_CheckPhoneNum.get(phone)
        if result is None:
            self.RequestPhoneValid(phone, self.RequestPhoneCode, phone)
        elif result[0] != 250:
            commondialog.ShowNewMessageBox(result[1], '確定')
            return
        else:
            self.RequestPhoneCode(phone)
        return

    def GetVoiceCode(self):
        if hasattr(self, 'm_CountTime') and self.m_CountTime > 0:
            import usermacro
            usermacro.PROMPT_MSG('%d秒後可重試' % self.m_CountTime)
            return
        import commondialog
        phone = self.m_PhoneEdit.GetText()
        if len(phone) != 11:
            commondialog.ShowNewMessageBox('手機號碼不符合要求, 請檢查', '確定')
            return
        result = self.m_CheckPhoneNum.get(phone)
        if result is None:
            self.RequestPhoneValid(phone, self.RequestPhoneVoiceCode, phone)
        elif result[0] != 250:
            commondialog.ShowNewMessageBox(result[1], '確定')
        else:
            self.RequestPhoneVoiceCode(phone)
        return

    def OnMessage(self, msgid):
        if msgid == 2:
            self.Save()
            Step(1)
            import clickcounter
            clickcounter.LoginLog('註冊2980郵箱頁-返回')
        elif msgid == 9:
            self.GetVoiceCode()
        elif msgid == 11:
            web = gameurl.MAIN2980_URL + '/server.htm'
            net.OpenUrl(web)
        elif msgid == 10:
            phone = self.m_PhoneEdit.GetText()
            if len(phone) != 11:
                import commondialog
                commondialog.ShowNewMessageBox('手機號碼不符合要求, 請檢查', '確定')
                return
            web = gameurl.MAIN2980_URL + '/phonecode.aspx?phone=%s' % phone
            net.OpenUrl(web)
            import clickcounter
            clickcounter.LoginLog('註冊2980郵箱頁-點擊這裡')
        elif msgid == 4:
            self.GetCheckCode()
        elif msgid == 5:
            import commondialog
            email = self.m_EmailEdit.GetText()
            email = email.strip()
            email = email.lower()
            if len(email) < 5:
                commondialog.ShowNewMessageBox('郵箱不符合要求，請檢查', '確定')
                return
            if email.isdigit():
                commondialog.ShowNewMessageBox('郵箱地址必須包含字母', '確定')
                return
            msg = self.m_CheckEmail.get(email)
            if msg is None:
                self.RequestEmailValid(email, None, None)
            import clickcounter
            clickcounter.LoginLog('註冊2980郵箱頁-檢測')
        elif msgid == 1:
            if not self.GetObject('chk_agree').IsSelected():
                usermacro.PROMPT_MSG('請勾選「我同意《2980服務條款》」（條款內容可以點擊鏈接進行查看）')
                return
            self.DoRegist()
            import clickcounter
            clickcounter.LoginLog('註冊2980郵箱頁-註冊帳號')
        return


def OnCheckEmail(data, *args):
    ERR_MSG = {609: '帳號格式輸入錯誤', 
       250: '該帳號可以使用', 
       625: '帳號已存在', 
       611: '檢測超出規定次數', 
       500: '服務器出錯', 
       614: '你不具備訪問權限', 
       583: '無任何執行動作'}
    Code = data.get('Code')
    (email, callback, arg) = args
    msg = ERR_MSG.get(Code)
    if not msg:
        try:
            msg = UTF82GBK(data.get('Message'))
        except:
            msg = '未知錯誤, 返回碼(%d)' % Code

    if not callback:
        import commondialog
        commondialog.ShowNewMessageBox(msg, '確定')
    elif isinstance(g_RegisterPanel, CRegPanel2_2980):
        g_RegisterPanel.UpdateCheckEmail(email, Code, msg)
    if arg:
        if not isinstance(arg, tuple):
            arg = (
             arg,)
        callback(*arg)
    else:
        callback()
    return


def OnCheckPhone(data, *args):
    ERR_MSG = {609: '手機號碼格式輸入錯誤', 
       250: '請輸入正確格式的手機號碼', 
       625: '手機號已存在', 
       611: '檢測超出規定次數', 
       500: '服務器出錯', 
       614: '你不具備訪問權限', 
       583: '無任何執行動作'}
    (phone, callback, arg) = args
    Code = data.get('Code')
    msg = ERR_MSG.get(Code)
    if not msg:
        try:
            msg = UTF82GBK(data.get('Message'))
        except:
            msg = '未知錯誤, 返回碼(%d)' % Code

    if isinstance(g_RegisterPanel, CRegPanel2_2980):
        g_RegisterPanel.UpdateCheckPhoneNum(phone, Code, msg)
    if Code == 250:
        if arg:
            if not isinstance(arg, tuple):
                arg = (
                 arg,)
            callback(*arg)
        else:
            callback()
    else:
        import commondialog
        commondialog.ShowNewMessageBox(msg, '確定')
    return


def OnRegister(data, *args):
    ERR_MSG = {608: '手機號或帳號不存在', 
       609: b"\xb0\xd15O-*&i%9#L(\xd4'o/(-*0f(^", 
       614: '你不具備訪問權限', 
       624: '請按要求填寫帳號', 
       625: '手機號或帳號存在', 
       626: '對像為空,用戶註冊失敗', 
       627: '註冊失敗', 
       631: '賬號出錯', 
       632: '服務器連接超時,註冊失敗', 
       633: '該賬號已被註冊為戰盟帳號', 
       634: '手機號已綁定戰盟帳號', 
       635: '身份証號格式不對', 
       636: '密碼長度不對', 
       638: '提供的用戶名和密碼與戰盟用戶名和遊戲密碼不一致', 
       500: '服務器出錯', 
       583: '無任何執行動作', 
       400: '短信驗証碼已超時', 
       401: '手機短信驗証碼輸入錯誤,請重新輸入', 
       402: '請先獲取短信驗証碼', 
       250: '註冊成功', 
       700: ' 正在維護中'}
    import commondialog
    Code = data.get('Code')
    if Code == 250:
        email = args[0] + '@2980.com'
        import loginin
        loginin.SaveAccount(email)
        commondialog.HideMessageBox()
        Register2980(1)
        return
    else:
        msg = ERR_MSG.get(Code)
        if not msg:
            try:
                msg = UTF82GBK(data.get('Message'))
            except:
                msg = '未知錯誤, 返回碼(%d)' % Code

        commondialog.ShowNewMessageBox(msg, '確定')
        return
    return


def OnPhoneCode(data, *args):
    ERR_MSG = {609: '參數不能為空（格式不對）', 
       250: '短信發送成功', 
       500: '短信發送失敗', 
       501: '短信服務暫停', 
       614: '你不具備訪問權限', 
       583: '無任何執行動作'}
    import commondialog
    Code = data.get('Code')
    msg = ERR_MSG.get(Code)
    if not msg:
        try:
            msg = UTF82GBK(data.get('Message'))
        except:
            msg = '未知錯誤, 返回碼(%d)' % Code

    commondialog.ShowNewMessageBox(msg, '確定')
    phone = args[0]
    if isinstance(g_RegisterPanel, CRegPanel2_2980):
        g_RegisterPanel.UpdatePhoneCodeResult(phone, Code)
    return


def OnPhoneVoice(data, *args):
    ERR_MSG = {250: '語音發送成功', 
       500: '語音發送失敗', 
       609: '手機號填寫有誤，請檢查確認'}
    import commondialog
    Code = data.get('Code')
    msg = ERR_MSG.get(Code)
    if not msg:
        try:
            msg = UTF82GBK(data.get('Message'))
        except:
            msg = '未知錯誤, 返回碼(%d)' % Code

    commondialog.ShowNewMessageBox(msg, '確定')
    return


def OnRegisterGame(data, *args):
    global g_AccountInfo
    import commondialog
    resultlist = data.split('|')
    try:
        err = int(resultlist[0])
    except:
        commondialog.ShowNewMessageBox('參數(%s)#r異常錯誤:%s' % (args, data), '確定')
        return

    dn = {}
    try:
        result = resultlist[1].split('&')
    except:
        result = []

    for ss in result:
        arr = ss.split('=', 1)
        dn[arr[0]] = arr[1]

    ecode = int(dn.get('code2', 0))
    errmsg = str(dn.get('msg', ''))
    ERR_MSG = {21: '註冊錯誤', 
       52: '普通錯誤', 
       100: '帳號被鎖', 
       110: '簽名驗証失敗', 
       120: '需要驗証碼'}
    if err == 120:
        imgbytes = str(dn.get('imgbytes', ''))
        vregval = str(dn.get('vregval', ''))
        ShowRegisterCheckCode(imgbytes, vregval)
        commondialog.HideMessageBox()
        return
    if err != 0:
        ShowError(err, ecode, errmsg)
        return
    import clientinterface
    clientinterface.SaveRegisterTime()
    g_AccountInfo = {}
    g_AccountInfo['ResultID'] = dn.get('number', '')
    email = dn.get('email', '')
    g_AccountInfo['ResultAccount'] = email
    g_AccountInfo['Email'] = email
    if email:
        import loginin
        loginin.SaveAccount(email)
        g_AccountInfo['ResultEmail'] = email
    commondialog.HideMessageBox()
    Step(2)
    return


def OnRegCode(data, *args):
    resultlist = data.split('|')
    try:
        err = int(resultlist[0])
    except:
        import commondialog
        commondialog.ShowNewMessageBox('參數(%s)#r異常錯誤:%s' % (args, data), '確定')
        ShowRegisterCodeFail()
        return

    dn = {}
    try:
        result = resultlist[1].split('&')
    except:
        result = []

    for ss in result:
        arr = ss.split('=', 1)
        dn[arr[0]] = arr[1]

    msg = str(dn.get('msg', ''))
    imgbytes = str(dn.get('imgbytes', ''))
    vregval = str(dn.get('vregval', ''))
    ERR_MSG = {102: '請求過於頻繁'}
    if err != 0:
        if not msg:
            msg = ERR_MSG.get(err)
        if not msg:
            msg = '未知錯誤'
        import commondialog
        commondialog.ShowNewMessageBox(msg + '(%d)' % err, '確定')
        ShowRegisterCodeFail()
        return
    ShowRegisterCheckCode(imgbytes, vregval)
    return


g_Func = {OP_CHECKEMAIL: OnCheckEmail, 
   OP_CHECKPHONE: OnCheckPhone, 
   OP_REGISTER: OnRegister, 
   OP_PHONECODE: OnPhoneCode, 
   OP_PHONEVOICE: OnPhoneVoice, 
   OP_REGISTERGAME: OnRegisterGame, 
   OP_REGCODE: OnRegCode}

def UTF82GBK(msg):
    return msg.decode('utf-8').encode('gbk')


def OnReceiveProcess(data, succeed, optype, *args):
    global g_Func
    import commondialog
    if not (succeed and data):
        commondialog.ShowNewMessageBox('註冊連接失敗', '確定')
        if optype == OP_REGCODE:
            ShowRegisterCodeFail()
        return
    (head, body) = data.split('\r\n\r\n', 1)
    if not body:
        commondialog.ShowNewMessageBox('註冊連接失敗, 沒有數據', '確定')
        return
    import playerphoto
    analyser = playerphoto.CAnalyser(body)
    d = analyser.GetData()
    if not d:
        if optype in (OP_REGISTERGAME, OP_REGCODE):
            d = body
        else:
            print '解析數據出錯', optype
            return
    func = g_Func.get(optype)
    if func:
        func(d, *args)
    return


class CRegPanel3_2980(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg5.dlg')
        email = g_AccountInfo['Email'] + '@2980.com'
        self.m_EmailTxt = combmacro.CTEXT(interface.CTextObject, 'email', self, email, interface.FontST36D, interface.COLOR_5, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            Show(False)
            import selectserver
            selectserver.Show(True)
        elif msgid == 2:
            Show(False)
            import mainpage
            mainpage.Show(True)
        return


class CRegPanel4(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg3.dlg')
        if 'ResultEmail' in g_AccountInfo:
            self.m_EmailTxt = combmacro.CTEXT(interface.CTextObject, 'email', self, '%s' % g_AccountInfo['ResultEmail'], interface.FontST36D, 16768635, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
        self.OnMessage(3)
        self.m_ImgStep = ui.CImage(self, 'combdialog/娸芞/俇傖.igs', 'interface')
        (x, y) = self.GetObject('reginfo3').GetPos()
        self.m_ImgStep.SetPos(x, y)
        self.m_ImgStep.SetFrame(1)
        return

    def OnMessage(self, msgid):
        if msgid == 2:
            Show(False)
            import mainpage, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            mainpage.Show(True)
        elif msgid == 3:
            url = gameurl.GetMailUrl(g_AccountInfo['ResultEmail'])
            if url:
                import net
                net.OpenUrl(url)
        return


def Step(n):
    global g_RegisterPanel
    _panels = [CRegPanel1, CRegPanel2, CRegPanel4]
    g_RegisterPanel = _panels[n](interface.DialogPanel)
    return


def Show(s):
    global g_RegisterPanel
    if s:
        C_sys.InputSecrecy(1)
        Step(0)
    else:
        g_RegisterPanel = None
        C_sys.InputSecrecy(0)
    return


def ShowRegisterCheckCode(imgbytes, vregval):
    if type(g_RegisterPanel) == CRegPanel2:
        g_RegisterPanel.ShowCheckCode(imgbytes, vregval)
    return


def ShowRegisterCodeFail():
    if type(g_RegisterPanel) == CRegPanel2 and getattr(g_RegisterPanel, 'm_CheckCode', None):
        g_RegisterPanel.m_CheckCode.ShowFailCodeImg()
    return


def ClearRegCode():
    try:
        import os
        path = 'photo\\register'
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)
    except Exception, e:
        print 'ClearRegCode Err:', e

    return


def SetCheckCode(checkcode):
    if g_RegisterPanel and isinstance(g_RegisterPanel, CRegPanel2_2980) and g_RegisterPanel.GetShow():
        g_RegisterPanel.m_CodeEdit.SetText(checkcode)
        return True
    return False


return
