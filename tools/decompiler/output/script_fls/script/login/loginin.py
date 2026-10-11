# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\loginin.py
import C_object, C_sys, interface, wrapinterface, combdialog, misc, net
LoginIn = None
g_LoginEmail = None
g_Char = None
g_AllChar = range(48, 58) + range(65, 91) + range(96, 106)
g_InputFrame = 0
g_KeyUpList = []
g_Protect = 0
g_DefaultAccount = None
g_Flag = False
_key_map = {41: 48, 
   33: 49, 
   64: 50, 
   35: 51, 
   36: 52, 
   37: 53, 
   94: 54, 
   38: 55, 
   42: 56, 
   40: 57, 
   96: 48, 
   97: 49, 
   98: 50, 
   99: 51, 
   100: 52, 
   101: 53, 
   102: 54, 
   103: 55, 
   104: 56, 
   105: 57}
idx = 0

def KeyDisturb(c):
    global g_Char
    global idx
    idx += 1
    if c >= 65 and c <= 91:
        c += 32
    elif _key_map.has_key(c):
        c = _key_map[c]
    r = False
    if c == g_Char:
        g_Char = None
        r = True
    gc = _key_map.get(g_Char)
    if gc == c:
        g_Char = None
        r = True
    r = C_sys.Record(r)
    return r


def ClearChar():
    global g_Char
    g_Char = None
    return


def KeyDisturbTimer(obj):
    global LoginIn
    global g_Char
    global g_InputFrame
    global g_KeyUpList
    global g_Protect
    if interface.g_ActiveEdit == None or interface.g_ActiveEdit.Get() != LoginIn.m_PasswordEdit or not g_Protect:
        for (c, t) in g_KeyUpList:
            C_sys.KeydbEvent(c, 0, 2)

        ClearChar()
        g_KeyUpList = []
        C_sys.SetKeyboardProtect(0)
        return ()
    g_InputFrame += 1
    if g_InputFrame % 4 == 0:
        C_sys.SetKeyboardProtect(g_Protect)
    while len(g_KeyUpList):
        (c, t) = g_KeyUpList[0]
        t -= g_InputFrame
        if t > 7 or misc.RandInt(0, 2) == 0:
            C_sys.KeydbEvent(c, 0, 2)
        else:
            break
        del g_KeyUpList[0]

    if g_InputFrame % 2 == 0:
        return ()
    c = g_AllChar[misc.RandInt(0, len(g_AllChar) - 1)]
    f = C_sys.Record(C_sys.KeydbEvent(c, 0, 0))
    if f:
        g_KeyUpList.append((c, g_InputFrame))
        if c >= 65 and c <= 91:
            c += 32
        g_Char = c
    else:
        g_Char = None
    return ()


def GetLoginEmail():
    global g_LoginEmail
    return g_LoginEmail


g_HideLpdBtn = False

def CheckHide():
    global g_HideLpdBtn
    import os
    if os.path.isfile('hlpd'):
        g_HideLpdBtn = True
    return


CheckHide()
g_LocalPwdFlag = [
 False, False]
g_HasLoginBefore = True
g_DYAutoLoginDlg = None
g_HasSelServer = False

def SetHasSelServer(flag):
    global g_HasSelServer
    g_HasSelServer = flag
    return


def StartDYAutoLogin():
    global g_DYAutoLoginDlg
    import main
    (email, pwd) = main.GetOneoff()
    import mainpage
    mainpage.Show(True, False)
    mainpage.Show(False)
    ShowLogin()
    g_LoginInDlg.SetShow(False)
    if IsShowAutoLogin():
        g_DYAutoLoginDlg = CDYAutoLoginDlg()
        g_LoginInDlg.OneoffLogin(email, pwd)
    else:
        import selectserver
        selectserver.Show(True)
        selectserver.SetOneOffLogin(True)
    return


def IsShowAutoLogin():
    global g_HasLoginBefore
    return g_HasLoginBefore or g_HasSelServer


def StartDYAutoLogin2():
    global g_DYAutoLoginDlg
    import mainpage
    mainpage.Show(True, False)
    mainpage.Show(False)
    ShowLogin()
    g_LoginInDlg.SetShow(False)
    if IsShowAutoLogin():
        g_DYAutoLoginDlg = CDYAutoLoginDlg()
    else:
        import selectserver
        selectserver.Show(True)
        selectserver.SetOneOffLogin(True)
    return


def ShowDYAutoLogin2():
    global g_DYAutoLoginDlg
    ShowLogin()
    g_LoginInDlg.SetShow(False)
    g_DYAutoLoginDlg = CDYAutoLoginDlg()
    import main
    (email, pwd) = main.GetOneoff()
    if email and pwd:
        import pubdylogin
        is_lpd = pubdylogin.CYWLoginInfoMgr.GetIslocalPwd()
        g_LoginInDlg.OneoffLogin2(email, pwd, is_lpd)
    return


def DYAutoLogin2(account, pwd, is_lpd):
    if g_LoginInDlg:
        g_LoginInDlg.OneoffLogin2(account, pwd, is_lpd)
    return


def DYAutoLoginOK():
    HideDYAutoLogin()
    return


def HideDYAutoLogin():
    global g_DYAutoLoginDlg
    if g_DYAutoLoginDlg:
        g_DYAutoLoginDlg.Capture(0)
        g_DYAutoLoginDlg = None
    return


class CDYAutoLoginDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/dyautologin.dlg')
        self.Capture(1, 1)
        self.Topmost()
        return

    def CloseGame(self):
        import main
        main.doexit()
        return

    def RestartGame(self):
        import main
        main.Restart()
        return

    def CloseDlg(self):
        HideDYAutoLogin()
        return

    def CloseWindow(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.RestartGame()
        elif msgid == 2:
            self.CloseGame()
        return


def DYAutoLoginFail():
    HideDYAutoLogin()
    Show(True)
    if g_LoginInDlg:
        g_LoginInDlg.AutoFillPwd()
    return


def LoginOk():
    global g_LoginEmail
    global g_User
    import netlogin, commondialog, re
    user = LoginIn.m_UserEdit.GetText()
    password = LoginIn.m_PasswordEdit.GetText()
    g_User = user
    if not (user and password):
        return
    if len(password) < 6:
        commondialog.ShowMessageBox('請輸入正確密碼', '確定')
        return
    patt = re.compile('^[0-9]+$')
    if patt.match(user):
        commondialog.ShowMessageBox('請輸入正確的帳號...', '確定')
        return
    g_LoginEmail = user
    netlogin.C2SLoginIn(user, password)
    netlogin.g_LoginErrorCallback = LoginInErr
    return


def LoginInErr(err_id, err_msg):
    import commondialog
    if err_id == 9:

        def dopatch(dlg):
            import main, os
            main.CloseGame()
            gameExe = 'mxLauncher.exe'
            try:
                restartFile = os.getcwd() + '\\' + gameExe
                if os.path.exists(restartFile):
                    os.system(restartFile)
            except:
                pass

            return

        def quit(dlg):
            import main
            main.CloseGame()
            return

        if isinstance(LoginIn, CLoginIn):
            LoginIn.m_UserEdit.Active(False)
            LoginIn.m_PasswordEdit.Active(False)
        commondialog.ShowMessageBox('當前客戶端版本較低, 請更新後進入!', ('退出遊戲',
                                                                                                                                                      '現在更新'), (quit, dopatch))
        return
    if err_msg != None:
        if isinstance(LoginIn, CLoginIn):
            LoginIn.m_PasswordEdit.SetText('')
        mbox = commondialog.ShowMessageBox(err_msg, '確定')
        mbox.SetPos(216, 396)
    else:
        commondialog.ShowMessageBox('讀取帳號信息...', '確定')
    import netlogin
    netlogin.g_LoginErrorCallback = LoginInErr
    return


class CUserEdit(interface.CListBox):

    def __init__(self, parent, color, font, x, y, w, h):
        interface.CListBox.__init__(self, parent, color, font, x, y, w, h, b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xcf\xc2\xc0\xad')
        self.SetDownButtonPos(w - 2, 3)
        return

    def MsgEnter(self):
        if self.GetText() == '':
            import commondialog
            commondialog.ShowMessageBox('請輸入帳號...', '確定')
            return
        LoginIn.m_PasswordEdit.Active(True)
        return

    def MsgDown(self):
        c = self.GetItemCount()
        sel = self.GetSelected() + 1
        if sel > c:
            sel = 1
        self.OnSelect(sel)
        return

    def MsgUp(self):
        c = self.GetItemCount()
        sel = self.GetSelected() - 1
        if sel < 1:
            sel = c
        self.OnSelect(sel)
        return

    def AddText(self, txt):
        index = 0
        while index < len(txt):
            if ord(txt[index]) < 128:
                interface.CEdit.AddChar(self, txt[index])
            else:
                interface.CEdit.AddChar(self, txt[index:index + 2])
                index += 1
            index += 1

        return

    def AddChar(self, c):
        try:
            if KeyDisturb(ord(c)):
                return
        except:
            pass

        interface.CListBox.AddChar(self, c)
        return


def SetProtect(protect):
    global g_Protect
    g_Protect = protect
    C_sys.SetKeyboardProtect(g_Protect)
    return


class CPasswordEdit(interface.CEdit):

    def MsgEnter(self):
        if isinstance(LoginIn, CLoginIn):
            LoginIn.OnMessage(2)
        else:
            LoginOk()
        return

    def AddChar(self, c):
        try:
            if KeyDisturb(ord(c)):
                return
        except:
            pass

        interface.CEdit.AddChar(self, c)
        if not c.isalnum():
            import usermacro
            usermacro.PROMPT_MSG('請仔細輸入，密碼只可能是數字或字母')
        return


class CRichClickText(interface.CClickText):

    def __init__(self, parent, x, y, text, normal_color, active_color, font, msgid=0):
        interface.CClickText.__init__(self, parent, x, y, text, normal_color, active_color, font, msgid)
        (w, h) = self.GetSize()
        self.m_Text = text
        self.m_Font = font
        self.m_UnderLine = C_object.CRichTextObject(self, w + 10, self.m_Font, '#u' + self.m_Text, normal_color)
        self.m_UnderLine.SetZ(-1)
        return

    def Enter(self):
        self.SetColor(self.m_ActiveColor)
        (w, h) = self.GetSize()
        self.m_UnderLine = C_object.CRichTextObject(self, w + 10, self.m_Font, '#u' + self.m_Text, self.m_ActiveColor)
        self.m_UnderLine.SetZ(-1)
        return

    def Leave(self):
        if self.m_MoveFlag:
            (x, y) = self.GetPos()
            self.SetPos(x - 1, y - 1)
            self.m_MoveFlag = False
        self.SetColor(self.m_NormalColor)
        (w, h) = self.GetSize()
        self.m_UnderLine = C_object.CRichTextObject(self, w + 10, self.m_Font, '#u' + self.m_Text, self.m_NormalColor)
        self.m_UnderLine.SetZ(-1)
        return


class CLoginIn(combdialog.CCombPanel):

    def __init__(self, parent):
        global g_DefaultAccount
        combdialog.CCombPanel.__init__(self, parent, 'login_new/newlogin_800.dlg')
        for idx in xrange(1, 16):
            btn = self.GetObject('ani%.2d' % idx)
            if btn:
                btn.SetFrame(misc.RandInt(0, btn.FrameAmount() - 1))
                btn.m_BGImg.CreateCommand(3, 'animation')

        if misc.IsTWServer():
            SetProtect(True)
        else:
            import mainpage
            self.GetObject('chk_protect').SetSelect(mainpage.g_PwdProtect)
            self.GetObject('chk_protect').m_ParentNotify = True
            SetProtect(mainpage.g_PwdProtect)
            self.GetObject('chk_agree').SetSelect(True)
            self.GetObject('chk_agree').m_ParentNotify = True
        obj = self.GetObject('box_URL')
        if obj:
            (w, h) = obj.GetSize()
            (x, y) = obj.GetPos()
            self.m_URLArea = wrapinterface.LoginURL(self, w, h, msgid=10)
            self.m_URLArea.SetPos(x, y)
        self.m_AccountList = GetAccountList()
        import combmacro
        obj = self.GetObject('edt_Name')
        (w, h) = obj.GetSize()
        (x, y) = obj.GetPos()
        self.m_UserEdit = CUserEdit(self, 16777215, interface.FontLT14_3, x, y, w, h)
        self.m_UserEdit.SetLimit(32)
        self.m_UserEdit.SetItemProp(2, 14, 64)
        self.m_UserEdit.Active(True)
        self.m_PasswordEdit = combmacro.CEDIT(CPasswordEdit, 'edt_Pwd', self, 16777215, interface.FontLT14_3, linecolor=0)
        self.m_PasswordEdit.SetLimit(16)
        self.m_PasswordEdit.m_IsPassword = True
        import os
        if os.path.exists('nocheck'):
            pw = '11111111'
            self.m_PasswordEdit.SetText(pw)
            self.m_PasswordEdit.Active(True)
            self.m_PasswordEdit.SetSelect(0, len(pw))
        self.m_UserEdit.SetNextEdit(self.m_PasswordEdit)
        self.m_PasswordEdit.SetNextEdit(self.m_UserEdit)
        self.SetMusicBtn()
        self.m_GetAccountTime = 0
        self.m_UserEdit.Topmost()
        self.RefreshAccountList()
        import register
        if register.g_AccountInfo.has_key('ResultEmail'):
            self.m_UserEdit.SetText(register.g_AccountInfo['ResultEmail'])
            del register.g_AccountInfo['ResultEmail']
        elif g_DefaultAccount:
            self.m_UserEdit.SetText(g_DefaultAccount)
            g_DefaultAccount = None
        elif len(self.m_UserEdit.m_TextList) > 0:
            self.m_UserEdit.OnSelect(1)
            self.m_PasswordEdit.Active(True)
        self.CreatePyCommand(1, KeyDisturbTimer)
        return

    def OnButtonEnter(self, btn):
        if btn.m_MsgID == 50:
            btn.m_tips = wrapinterface.CTextTips(self, 220, '#cfff650溫馨提醒：如果玩家在啟用該功能後無法正常輸入帳號和密碼，證明有其他程序正在監視玩家的鍵盤輸入。為保障您帳號密碼安全，請務必保持密碼保護被勾選。', interface.FontLT14_3, direct=1)
            btn.m_tips.SetOwner(btn)
        return

    def OnButtonLeave(self, btn):
        if btn.m_MsgID == 50:
            btn.m_tips = None
        return

    def RefreshAccountList(self):
        self.m_UserEdit.Reset()
        for acc in self.m_AccountList:
            self.m_UserEdit.AddTextItem(acc)

        return

    def SaveAccount(self):
        if C_sys.IsReplaying():
            return
        acc = self.m_UserEdit.GetText()
        if (acc[0] == 'a' or acc[0] == 'A') and acc[1:].isdigit():
            acc = 'A' + acc[1:]
        if acc and SaveAccount(acc):
            self.m_AccountList = GetAccountList()
        return

    def OneoffLogin(self, user, password, is_lpd=False):
        global g_LocalPwdFlag
        global g_LoginEmail
        global g_User
        g_LocalPwdFlag = [
         False, False]
        self.m_UserEdit.SetText(user)
        self.m_PasswordEdit.SetText('')
        self.m_BtnLocalPwd.SetSelect(False)
        g_User = user
        if not is_lpd:
            import localrecord
            password = localrecord.MD5Zip(password)
        self.m_PassWord = password
        g_LoginEmail = user
        import netserver, netlogin
        netserver.RandomConnect()
        netlogin.g_LoginErrorCallback = LoginInErr
        import commondialog
        commondialog.HideMessageBox()
        return

    def OneoffLogin2(self, user, password, is_lpd=False):
        global g_LocalPwdFlag
        global g_LoginEmail
        global g_User
        if not is_lpd:
            g_LocalPwdFlag = [
             False, False]
        else:
            g_LocalPwdFlag = [
             False, True]
        self.m_UserEdit.SetText(user)
        self.m_PasswordEdit.SetText('')
        self.m_BtnLocalPwd.SetSelect(False)
        g_User = user
        if not is_lpd:
            import localrecord
            password = localrecord.MD5Zip(password)
        self.m_PassWord = password
        g_LoginEmail = user
        import netserver, netlogin
        netserver.RandomConnect()
        netlogin.g_LoginErrorCallback = LoginInErr
        import commondialog
        commondialog.HideMessageBox()
        return

    def SetMusicBtn(self):
        import gamectrl
        if gamectrl.GetMusicVolume() > 0:
            self.GetObject('btn_Music').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xc9\xf9\xd2\xf4\xb0\xb4\xc5\xa5/\xb4\xf2\xbf\xaa/')
            self.GetObject('btn_Music').SetLight(8)
            self.GetObject('btn_Music').SetFrame(3)
            self.GetObject('btn_Music').m_Selected = True
        else:
            self.GetObject('btn_Music').SetPath(b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xc9\xf9\xd2\xf4\xb0\xb4\xc5\xa5/\xb9\xd8\xb1\xd5/')
            self.GetObject('btn_Music').SetFrame(1)
            self.GetObject('btn_Music').m_Selected = False
        return

    def OnMessage(self, msgid):
        global g_Flag
        if msgid == 2:
            if not misc.IsTWServer():
                obj = self.GetObject('chk_agree')
                if obj and not obj.IsSelected():
                    import commondialog
                    commondialog.ShowMessageBox('請勾選「我同意多益通用戶協議」#r（協議內容可以點擊鏈接進行查看）', ('確定', ), (None, ))
                    return
            LoginOk()
            import sound
            sound.Play('action/button.wav')
        elif msgid == 1:
            Show(False)
            import selectserver
            selectserver.Show(True)
            net.g_Net.Disconnect()
            import sound
            sound.Play('action/button.wav')
        elif msgid == 3:
            import main
            main.CloseGame()
        elif msgid == 10:
            import gameurl, main
            if misc.IsTWServer():
                if getattr(main, 'g_LangVersion', 0) == 0:
                    url = gameurl.LOGO_URL_IN_TAIWANG
                else:
                    url = gameurl.LOGO_URL_IN_HK
            else:
                url = gameurl.LOGO_URL
            net.OpenUrl(url)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 22:
            Show(False)
            import getaccount, sound
            sound.Play('action/button.wav')
            getaccount.Show(True)
        elif msgid == 23:
            if misc.IsTWServer():
                return
            Show(False)
            g_Flag = True
            import aboutpwd, sound
            sound.Play('action/button.wav')
            aboutpwd.Show(True)
        elif msgid == 24:
            import gameurl
            net.OpenUrl(gameurl.DYT_XIEYI_URL)
        elif msgid == 50:
            import mainpage, sound
            sound.Play('action/button.wav')
            mainpage.g_PwdProtect = not self.GetObject('btn_Protect').IsSelected()
            SetProtect(mainpage.g_PwdProtect)
        elif msgid == 71:
            import cfg, sound, gamectrl
            iMusicVolume = gamectrl.GetMusicVolume()
            if iMusicVolume == 0:
                iMusicVolume = -70
            iMusicVolume = -iMusicVolume
            sound.SaveNewMusic(iMusicVolume)
            gamectrl.SetSoundVolume(iMusic=iMusicVolume)
            sound.PlayLoginMusic()
            self.SetMusicBtn()
        return


def Show(s):
    global LoginIn
    if s:
        LoginIn = CLoginIn(interface.DialogPanel)
        interface.SetDefaultButton(LoginIn.GetObject('btn_login'))
        C_sys.InputSecrecy(1)
    else:
        LoginIn = None
        C_sys.InputSecrecy(0)
        C_sys.SetKeyboardProtect(0)
    import selectserver
    loginserver = selectserver.g_LoginServer
    return


def OnLogin():
    if not LoginIn:
        return
    LoginIn.SaveAccount()
    return


class CServiceMessageDialog(combdialog.CCombPanel):

    def __init__(self, parent, msg, nextfunc):
        combdialog.CCombPanel.__init__(self, parent, 'login/service.dlg')
        self.m_NextFunc = nextfunc
        import chatoutput
        result = [_[1] for s in msg.split('\n')]
        output = self.GetObject('loc_msg')
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(self, w, h, 0, 0, result, txt_font=interface.FontLT14_3, txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.SetChatCursor(0)
        self.m_PublicTxtBox.ResetFromCursor()
        self.m_PublicTxtBox.ScrollTo(0)
        return

    def OnMessage(self, msgid):
        global g_Panel
        if msgid == 1:
            g_Panel = None
            self.m_NextFunc(True)
        elif msgid == 2:
            g_Panel = None
            import selectserver
            selectserver.Show(True)
            net.g_Net.Disconnect()
        return


def ShowService(bFlag):
    global g_Panel
    import servicedata
    g_Panel = CServiceMessageDialog(interface.DialogPanel, servicedata.SERVICE_MSG, Show)
    return


def ShowLogin():
    global g_Panel
    import main
    if main.g_LangVersion == 0:
        import servicedata
        g_Panel = CServiceMessageDialog(interface.DialogPanel, servicedata.SERVICE_MSG2, ShowService)
    else:
        ShowService(True)
    return


class CClickRichText(interface.CClickBox):

    def __init__(self, parent, x, y, w, text, normal_color, active_color, font, msgid=0, Enable_color=8421504):
        temptxt = text
        if w == 0:
            w = len(text) * (interface.g_FontSize[font] + 1) / 2
            h = interface.g_FontSize[font]
        elif len(text) * (interface.g_FontSize[font] + 1) / 2 < w:
            w = len(text) * (interface.g_FontSize[font] + 1) / 2
            h = interface.g_FontSize[font]
        else:
            i = len(text) * (interface.g_FontSize[font] + 1) / 2 / w
            h = (i + 1) * interface.g_FontSize[font] + 1
        interface.CClickBox.__init__(self, parent, w, h, 0, 0, msgid)
        self.SetPos(x, y)
        self.m_TextObj = C_object.CRichTextObject(self, w, font, text, normal_color)
        self.m_TextObj1 = C_object.CRichTextObject(self, w, font, text, active_color)
        self.m_TextObj2 = C_object.CRichTextObject(self, w, font, text, Enable_color)
        self.m_TextObj.SetPos(0, 0)
        self.m_TextObj1.SetPos(0, 0)
        self.m_TextObj2.SetPos(0, 0)
        self.m_TextObj1.SetShow(False)
        self.m_TextObj2.SetShow(False)
        self.m_NormalColor = normal_color
        self.m_ActiveColor = active_color
        self.m_EnableColor = Enable_color
        self.m_MoveFlag = False
        self.m_text = text
        (self.m_w, self.m_h) = self.m_TextObj.GetSize()
        self.m_font = font
        self.SetSize(w, self.m_h)
        return

    def LeftDown(self):
        (x, y) = self.m_TextObj.GetPos()
        self.m_TextObj.SetPos(x + 1, y + 1)
        (x, y) = self.m_TextObj1.GetPos()
        self.m_TextObj1.SetPos(x + 1, y + 1)
        self.m_MoveFlag = True
        return

    def LeftUp(self):
        if self.m_MoveFlag:
            (x, y) = self.m_TextObj.GetPos()
            self.m_TextObj.SetPos(x - 1, y - 1)
            (x, y) = self.m_TextObj1.GetPos()
            self.m_TextObj1.SetPos(x - 1, y - 1)
            self.m_MoveFlag = False
        interface.CClickObject.LeftUp(self)
        return

    def Enter(self):
        self.m_TextObj1.SetShow(True)
        self.m_TextObj.SetShow(False)
        par = self.GetParent()
        if hasattr(par, 'OnEnter'):
            par.OnEnter(self)
        return

    def Leave(self):
        if self.m_MoveFlag:
            (x, y) = self.m_TextObj.GetPos()
            self.m_TextObj.SetPos(x - 1, y - 1)
            (x, y) = self.m_TextObj1.GetPos()
            self.m_TextObj1.SetPos(x - 1, y - 1)
            self.m_MoveFlag = False
        self.m_TextObj1.SetShow(False)
        self.m_TextObj.SetShow(True)
        try:
            par = self.GetParent()
        except:
            return

        if hasattr(par, 'OnLeave'):
            par.OnLeave(self)
        return

    def Enable(self, flag):
        interface.CClickObject.Enable(self, flag)
        if flag:
            self.m_TextObj.SetShow(True)
            self.m_TextObj1.SetShow(False)
            self.m_TextObj2.SetShow(False)
        else:
            self.m_TextObj.SetShow(False)
            self.m_TextObj1.SetShow(False)
            self.m_TextObj2.SetShow(True)
        return


g_LastCheckTime = 0

class CEmailCodeDlg(combdialog.CCombDialog):

    def __init__(self, email):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/upgrade_email.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import combmacro
        self.m_EmailCodeText = combmacro.CEDIT(interface.CEdit, 'emailcode', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_6)
        self.m_EmailCodeText.SetLimit(10)
        self.m_EmailCodeText.Active(True)
        obj = self.GetObject('tip')
        (x, y) = obj.GetPos()
        self.m_FinallyPath = CClickRichText(self, x, y, 400, '#u※點此將其他郵箱升級為多益通帳號#n', (255,
                                                                                                                                                                            5172479)[interface.STYLE], 65280, interface.FontLT12E_1, 99)
        self.m_Email = combmacro.CTEXT(C_object.CTextObject, 'account', self, email, interface.FontLT14_3, (255,
                                                                                                            5172479)[interface.STYLE])
        return

    def RightUp(self):
        return

    def CloseWindow(self):
        return

    def CloseDlg(self):
        global g_UpgradeDlg
        g_UpgradeDlg = None
        return

    def OnMessage(self, msgid):
        global g_LastCheckTime
        if msgid == 1:
            emailCodeText = self.m_EmailCodeText.GetText()
            if emailCodeText and emailCodeText.isdigit() and 6 <= len(emailCodeText) <= 10:
                import netlogin
                netlogin.C2SReqDYTUseEmailCode(emailCodeText)
                self.m_EmailCodeText.Clear()
            else:
                import usermacro
                usermacro.PROMPT_MSG('請輸入正確的驗証碼')
        elif msgid == 2:
            import main
            main.doreturn(C_object.CBaseObject(None))
        elif msgid == 4:
            import misc
            t = misc.Time()
            if t - g_LastCheckTime >= 900:
                import netlogin
                netlogin.C2SCheckEmail()
                g_LastCheckTime = t
            else:
                import usermacro
                usermacro.PROMPT_MSG('驗証碼已發送，請不要重複點擊')
        elif msgid == 99:
            self.CloseDlg()
            ShowFinallyPathDlg(1)
        return


g_UpgradeDlg = None
g_TempMailPwd = None
g_TargetEmail = None

def ShowEmailCodeDlg(email=''):
    global g_TargetEmail
    global g_UpgradeDlg
    import main
    main.HideWindow()
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    if email:
        start = min(2, len(email))
        pos = email.rfind('@')
        if pos < 0:
            pos = max(1, len(email))
        end = pos - 1
        try:
            g_TargetEmail = '%s%s%s' % (email[:start], '*' * (end - start), email[end:])
        except:
            g_TargetEmail = email

    g_UpgradeDlg = CEmailCodeDlg(g_TargetEmail)
    return


class CFinallyPathDlg(combdialog.CCombDialog):

    def __init__(self, predlg=0):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/upgrade_other.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import register, combmacro
        self.m_EmailText = combmacro.CEDIT(register.CMailEdit, 'email', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_6)
        self.m_PasswordText = combmacro.CEDIT(interface.CEdit, 'password', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_6)
        self.m_PasswordText.m_IsPassword = True
        self.m_EmailText.SetLimit(32)
        self.m_EmailText.Active(True)
        self.m_EmailText.SetNextEdit(self.m_PasswordText)
        self.m_PasswordText.SetNextEdit(self.m_EmailText)
        self.m_PreDlg = predlg
        if self.m_PreDlg == 0:
            self.GetObject('noname5').SetShow(False)
        (x, y) = self.GetObject('noname15').GetPos()
        self.m_NoUpdate = CClickRichText(self, x, y, 400, '#u暫不升級#n', 65535, 65280, interface.FontLT12E_1, 2)
        obj = self.GetObject('loc_text')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        msg = '#c00FFFF[註冊一個多益通帳號]#c()'
        self.m_ClickText = CClickRichText(self, x, y, w, msg, interface.COLOR_5, interface.COLOR_5, interface.FontLT14_3, 3)
        return

    def OnEnter(self, obj):
        if obj == self.m_ClickText:
            self.m_Tips = wrapinterface.CTextTips(self, -1, '點擊可直接註冊多益通帳號', interface.FontLT14_3, direct=1)
        return

    def OnLeave(self, obj):
        self.m_Tips = None
        return

    def RightUp(self):
        return

    def CloseWindow(self):
        return

    def CloseDlg(self):
        global g_UpgradeDlg
        g_UpgradeDlg = None
        return

    def IsEMail(self, email):
        if hasattr(self, 'm_Pattern'):
            patt = self.m_Pattern
        else:
            import re
            patt = re.compile('^[-.\\w]{1,64}@[-.\\w]{1,64}\\.[\\w]{2,4}$')
            self.m_Pattern = patt
        return None != patt.match(email)

    def Confirm(self):
        global g_TempMailPwd
        emailText = self.m_EmailText.GetText()
        passwordText = self.m_PasswordText.GetText()
        import usermacro
        if len(emailText) == 0:
            usermacro.PROMPT_MSG('請輸入要升級到的多益通帳號')
        elif len(passwordText) == 0:
            usermacro.PROMPT_MSG('請輸入正確的密碼')
        elif not self.IsEMail(emailText):
            usermacro.PROMPT_MSG('請輸入合法的郵箱地址')
        else:
            import netlogin
            netlogin.C2SReqDYTUseEMail(emailText, passwordText)
            s = ''
            for c in passwordText:
                c = ord(c) ^ 255
                s += chr(c)

            g_TempMailPwd = '%s,%s' % (emailText, s)
            self.m_EmailText.Clear()
            self.m_PasswordText.Clear()
            SaveAccount(emailText)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.Confirm()
        elif msgid == 2:
            import main
            main.doreturn(C_object.CBaseObject(None))
        elif msgid == 3:
            self.CloseDlg()
            Show(False)
            import register, selectrole
            selectrole.Show(False)
            register.Show(True)
            net.g_Net.Disconnect()
        elif msgid == 4:
            self.CloseDlg()
            if self.m_PreDlg == 1:
                ShowEmailCodeDlg()
            elif self.m_PreDlg == 2:
                ShowUsePasswordDlg()
        return


def ShowFinallyPathDlg(predlg):
    global g_UpgradeDlg
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    g_UpgradeDlg = CFinallyPathDlg(predlg)
    return


class CUsePasswordDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/upgrade_pwd.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import combmacro
        self.m_PasswordText = combmacro.CEDIT(interface.CEdit, 'password', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_6)
        self.m_PasswordText.Active(True)
        self.m_PasswordText.m_IsPassword = True
        obj = self.GetObject('tip')
        (x, y) = obj.GetPos()
        self.m_FinallyPath = CClickRichText(self, x, y, 400, '#u※點擊此處將其他郵箱升級為多益通帳號#n', (255,
                                                                                                                                                                                         5172479)[interface.STYLE], 65280, interface.FontLT12E_1, 99)
        return

    def RightUp(self):
        return

    def CloseWindow(self):
        return

    def CloseDlg(self):
        global g_UpgradeDlg
        g_UpgradeDlg = None
        return

    def Confirm(self):
        passwordText = self.m_PasswordText.GetText()
        if len(passwordText) == 0:
            import usermacro
            usermacro.PROMPT_MSG('請輸入正確的密碼')
        else:
            import netlogin
            netlogin.C2SReqDYTUsePassword(passwordText)
            self.m_PasswordText.Clear()
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.Confirm()
        elif msgid == 2:
            import main
            main.doreturn(C_object.CBaseObject(None))
        elif msgid == 99:
            self.CloseDlg()
            ShowFinallyPathDlg(2)
        return


def ShowUsePasswordDlg():
    global g_UpgradeDlg
    import main
    main.HideWindow()
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    g_UpgradeDlg = CUsePasswordDlg()
    return


class CConfirmDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/upgrade_confirm.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import combmacro
        self.m_PasswordText = combmacro.CEDIT(interface.CEdit, 'password', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_6)
        txt = g_LoginEmail
        self.m_UserText = combmacro.CTEXT(interface.CTextObject, 'user', self, txt, interface.FontLT14_3, 255, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
        txt = g_LoginEmail + '@mx'
        self.m_User2Text = combmacro.CTEXT(interface.CTextObject, 'user2', self, txt, interface.FontLT14_3, 255, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
        return

    def RightUp(self):
        return

    def CloseWindow(self):
        return

    def CloseDlg(self):
        global g_UpgradeDlg
        g_UpgradeDlg = None
        return

    def Confirm(self):
        passwordText = self.m_PasswordText.GetText()
        if passwordText != '確認新用':
            import usermacro
            usermacro.PROMPT_MSG('輸入的文字不正確，請檢查')
        else:
            self.CloseDlg()
            import netlogin
            netlogin.C2SAffirmUseDYT()
        return

    def OnMessage(self, msgid):
        if msgid == 2:
            self.CloseDlg()
            import netlogin
            netlogin.C2SDYTCloseDlg()
        elif msgid == 1:
            self.Confirm()
        return


def ShowConfirmDlg():
    global g_UpgradeDlg
    import main
    main.HideWindow()
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    g_UpgradeDlg = CConfirmDlg()
    return


class CSetPwd(combdialog.CCombDialog):

    def __init__(self, email):

        class CRegEdit(interface.CEdit):

            def AddChar(self, c):
                if c.isalnum():
                    interface.CEdit.AddChar(self, c)
                else:
                    import usermacro
                    usermacro.PROMPT_MSG('密碼僅可由6至16位字母或數字組成')
                return

        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/dyt_pwd.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import combmacro
        self.m_PwdEdit = combmacro.CreateEdit(CRegEdit, 'pwd', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_PwdEdit.m_ActiveIdx = 'pwd'
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = combmacro.CreateEdit(CRegEdit, 'pwd2', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_PwdEdit2.m_ActiveIdx = 'pwd2'
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.m_IsPassword = True
        import misc
        self.m_EmailText = combmacro.CTEXT(C_object.CTextObject, 'email', self, email, interface.FontLT14_3, 255, align=interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.Active(True)
        return

    def RightUp(self):
        return

    def CloseWindow(self):
        return

    def CloseDlg(self):
        global g_UpgradeDlg
        g_UpgradeDlg = None
        return

    def DoCheck(self):
        pwd = self.m_PwdEdit.GetText()
        self.m_PwdEdit.Active(True)
        if len(pwd) < 6:
            return '請輸入正確格式的密碼（密碼僅可由6至16位字母或數字組成）'
        if pwd != self.m_PwdEdit2.GetText():
            return '遊戲密碼和確認密碼不符，請檢查確認'
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseDlg()
            import netlogin
            netlogin.C2SDYTCloseDlg()
        elif msgid == 2:
            msg = self.DoCheck()
            if msg:
                import commondialog
                commondialog.ShowMessageBox(msg, '確定')
            else:
                pwd = self.m_PwdEdit.GetText()
                self.m_PwdEdit.Clear()
                self.m_PwdEdit2.Clear()
                import netlogin
                netlogin.C2SSetActive(pwd)
        return


def ShowSetDYT(email):
    global g_UpgradeDlg
    import main
    main.HideWindow()
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    g_UpgradeDlg = CSetPwd(email)
    return


def CloseUpgrade():
    global g_UpgradeDlg
    if g_UpgradeDlg:
        g_UpgradeDlg.CloseDlg()
    g_UpgradeDlg = None
    return


def ShowPrivate(info):
    global g_UpgradeDlg
    if info:
        g_UpgradeDlg = CPrivateDlg(info)
        import nettask
        if nettask.g_TaskInfo.has_key(11635):
            obj = wrapinterface.CCombTipsBox(g_UpgradeDlg, '填寫所有帶*號的內容，只要年滿#B18週歲#n即可解除防沉迷限制', 6, 284, 166, 150, 80)
            obj.Topmost()
            g_UpgradeDlg.m_CombTips = obj
    else:
        g_UpgradeDlg = None
    return


class CPrivateDlg(combdialog.CCombDialog):

    def __init__(self, info):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/private_info.dlg')
        interface.Center(self)
        import combmacro, wrapinterface

        class CEdit(interface.CEdit):

            def SetNotifyID(self, nid):
                self.m_NotifyID = nid
                return

            def AddChar(self, char):
                interface.CEdit.AddChar(self, char)
                if hasattr(self, 'm_NotifyID') and self.m_NotifyID:
                    self.GetParent().OnMessage(self.m_NotifyID)
                return

            def DeleteChar(self):
                interface.CEdit.DeleteChar(self)
                if hasattr(self, 'm_NotifyID') and self.m_NotifyID:
                    self.GetParent().OnMessage(self.m_NotifyID)
                return

        self.m_IDEdit = combmacro.CEDIT(CEdit, 'id', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_IDEdit.SetNotifyID(3)
        self.m_IDEdit.Active(True)
        self.m_NameEdit = combmacro.CEDIT(interface.CEdit, 'name', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_PhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'phone', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_QQEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'qq', self, interface.COLOR_5, interface.FontLT12E_1)
        self.m_NameEdit.SetLimit(20)
        already_set = False
        key_edit_list = (('idcard', self.m_IDEdit), ('name', self.m_NameEdit), ('mobile', self.m_PhoneEdit), ('qq', self.m_QQEdit))
        edit_list = []
        for (key, edit) in key_edit_list:
            edit.Enable(True)
            if info.has_key(key):
                if info[key]:
                    edit.Enable(False)
                    edit.m_ResultTxt = C_object.CTextObject(edit, '已設置', interface.FontLT14_3, interface.COLOR_5)
                else:
                    edit_list.append(edit)
            else:
                edit_list.append(edit)

        Len = len(edit_list)
        for i in range(0, Len):
            edit_list[i].SetNextEdit(edit_list[(i + 1) % Len])

        if Len:
            edit_list[0].Active(True)
        return

    def IdentityCheck(self, identity):
        if len(identity) != 18:
            return False
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
        if self.m_IDEdit.m_EnableFlag:
            identity = self.m_IDEdit.GetText()
            import idcarddata
            if idcarddata.ValidDateFormat(identity):
                if not idcarddata.ValidDate(identity):
                    return '未滿18歲'
            else:
                return '身份証號碼日期格式錯誤'
            if idcarddata.ValidCDCard(identity) == False:
                return '無效的身份証號碼'
            if not identity.isalnum():
                return '身份証只允許輸入數字或字母，請檢查輸入信息'
        if self.m_NameEdit.m_EnableFlag:
            name = self.m_NameEdit.GetText()
            lenname = len(name)
            if lenname < 4 or lenname > 20:
                return '請輸入您的真實姓名'
            if not misc.IsGB2312(name, 0):
                return '姓名只能輸入簡體中文'
        if self.m_PhoneEdit.m_EnableFlag:
            phone = self.m_PhoneEdit.GetText()
            if phone and (phone[0] != '1' or len(phone) != 11):
                return '請輸入正確的手機號碼(可以不填)'
        if self.m_QQEdit.m_EnableFlag:
            qq = self.m_QQEdit.GetText()
            if qq and not qq.isdigit():
                return '請填寫正確的QQ號(可以不填)'
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import usermacro
            msg = self.DoCheck()
            if msg:
                usermacro.PROMPT_MSG(msg)
                return
            s = ''
            identity = self.m_IDEdit.GetText()
            name = self.m_NameEdit.GetText()
            phone = self.m_PhoneEdit.GetText()
            qq = self.m_QQEdit.GetText()
            key_value_list = (('idcard', identity), ('qq', qq), ('mobile', phone), ('name', name))
            for (key, value) in key_value_list:
                if value:
                    s += '%s=%s||' % (key, value)

            if s:
                if (identity or self.m_IDEdit.m_EnableFlag == False) and (name or self.m_NameEdit.m_EnableFlag == False):
                    import netlogin
                    netlogin.C2SPrivateInfo(s[:-2])
                    ShowPrivate(None)
                else:
                    usermacro.PROMPT_MSG('請將：#R身份証、真實姓名#n全部填寫完後，再點擊確認保存')
        elif msgid == 2:
            ShowPrivate(None)
        elif msgid == 3:
            identity = self.m_IDEdit.GetText()
            if not identity.isalnum() and identity:
                import usermacro
                usermacro.PROMPT_MSG('身份証只允許輸入數字或字母，請檢查輸入信息')
                return
        else:
            print 'CPrivateDlg::OnMessage', msgid
        return


def HintExistSameEmail():
    global g_TempMailPwd
    if not g_TempMailPwd:
        return
    (email, pwd) = g_TempMailPwd.split(',')
    if email.endswith('@mx'):
        email = email[:-3]
    g_TempMailPwd = None
    s = ''
    for c in pwd:
        c = ord(c) ^ 255
        s += chr(c)

    def confirm(dlg):
        print dlg.m_Email, dlg.m_Pwd
        import netlogin
        netlogin.C2SAffirmUseSameEmail(dlg.m_Email, dlg.m_Pwd)
        return

    import commondialog
    msg = '目標多益通在本遊戲中存在同名帳號，您確定要將#Y%s#n升級到#Y%s#n多益通帳號嗎？' % (g_LoginEmail, email)
    mbox = commondialog.ShowMessageBox(msg, ('確定', '取消'), (confirm, None))
    mbox.m_Email = email
    mbox.m_Pwd = s
    return


def GetAccountList():
    import cfg
    acc_lst = cfg.GetData('mx.ini', 'Login', 'AccountList')
    if acc_lst == None:
        acc_lst = ''
    try:
        f = open('users/usr.lst', 'r')
    except:
        return []

    usr_lst = f.read()
    try:
        f.close()
    except:
        pass

    if len(acc_lst) >= len(usr_lst):
        s = acc_lst
    else:
        s = usr_lst
    if s:
        return s.split(',')
    return []


def SaveAccount(account):
    import cfg, os
    lst = GetAccountList()
    if account in lst:
        lst.remove(account)
    lst.insert(0, account)
    s = (',').join(lst)
    ret = cfg.SaveData('mx.ini', 'Login', 'AccountList', s)
    if not os.path.lexists('users'):
        os.mkdir('users')
    fname = 'users/usr.lst'
    try:
        f = open(fname, 'w')
    except IOError, ioerror:
        print '讀文件錯誤：', fname, ioerror
        return ret

    f.write(s)
    try:
        f.close()
    except IOError, ioerror:
        print '關閉文件出現異常：', fname, ioerror

    return ret


return
