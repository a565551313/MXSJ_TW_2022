# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlggetbackaccount.py
import interface, ui, combdialog, pubdlggetaccount, dlgsysopt
g_MainDlg = None
g_CodeTimer = None
g_FirstCode = True
g_LocalTimer = None

def ModuleReset():
    global g_CodeTimer
    global g_FirstCode
    global g_LocalTimer
    global g_MainDlg
    g_MainDlg = None
    g_CodeTimer = None
    g_FirstCode = True
    g_LocalTimer = None
    return


def ShowGetAccountDlg():
    global g_MainDlg
    g_MainDlg = CGetAccountMainDlg()
    return


def GetCheckPhoneDlg():
    if g_MainDlg and g_MainDlg.m_SubDlg and isinstance(g_MainDlg.m_SubDlg, CCheckPhoneDlg) and g_MainDlg.m_SubDlg.GetShow():
        return g_MainDlg.m_SubDlg
    return


class CVScrollBar(combdialog.CVScrollBar):

    class CBar(combdialog.CVScrollBar.CBar):

        def GetPos(self):
            (x, y) = interface.CContainerObject.GetPos(self)
            return (x - 2, y - self.m_Y)

        def SetPos(self, x, y):
            interface.CContainerObject.SetPos(self, x + 2, y + self.m_Y)
            return

    def __init__(self, parent, h, n_max=1, n_page=1, unit=1):
        if type(h) == list:
            h = int(h[0])
        interface.CContainerObject.__init__(self, parent)
        self.m_Unit = unit
        self.m_Height = h
        self.m_UpButton = interface.CButton(self, self.GetVScrollBarPath() + 'up.igs', 0, 0, 1)
        self.m_UpButton.SetZ(1)
        self.m_DownButton = interface.CButton(self, self.GetVScrollBarPath() + 'down.igs', 0, 0, 2)
        self.m_DownButton.SetZ(1)
        self.m_Imagess = ui.CVFrame(self, self.m_Height, self.GetVScrollBarPath())
        (_, iDownBtnH) = self.m_DownButton.GetSize()
        h -= iDownBtnH
        self.m_DownButton.SetPos(0, h)
        (_, iUpBtnH) = self.m_UpButton.GetSize()
        h -= iUpBtnH
        if n_max <= n_page:
            self.m_UpButton.Enable(False)
            self.m_DownButton.Enable(False)
        self.m_Bar = self.CBar(self, iUpBtnH, n_max, n_page, h)
        self.MessageProcess()
        return

    def GetVScrollBarPath(self):
        return b'combdialog\\\xd2\xe6\xcd\xf8\xc8\xa6\\\xca\xfa\xb9\xf6\xb6\xaf\xcc\xf5\\'


class CAreaCodeListBox(dlgsysopt.CAreaCodeListBox):

    class CMyList(interface.CList):
        VSCROLLBAR_CLASS = CVScrollBar

        def __init__(self, parent, x, y, w, h, color=16777215, alpha=256, hspace=0):
            interface.CList.__init__(self, parent, x, y, w, h, color, alpha, hspace)
            return

        def OnMessage(self, msgid):
            if msgid < interface.RIGHT_BUTTON_MESSAGE:
                self.GetParent().OnSelect(msgid)
            else:
                self.GetParent().OnListClose()
            return

        def LeftUp(self):
            self.GetParent().OnListClose()
            return

        def RightUp(self):
            self.GetParent().OnListClose()
            return

    def __init__(self, parent, color, font, x, y, w, h, hotareadata, allareadata):
        interface.CListBox.__init__(self, parent, color, font, x, y, w, h, b'combdialog/\xd2\xe6\xcd\xf8\xc8\xa6/\xb0\xb4\xc5\xa5/\xcf\xc2\xc0\xad.igs')
        self.SetDownButtonPos(w, 3)
        self.m_HotAreaData = hotareadata[:]
        self.m_AllAreaData = allareadata[:]
        self.m_ShowData = hotareadata[:]
        self.m_IsShowHotArea = False
        self.m_SeletCountry = ''
        self.CreateClickBox(True, w, h)
        return

    def CreateClickBox(self, txtevent=True, w=0, h=0):
        if not txtevent:
            self.m_TxtClickBox = None
            return
        self.m_TxtClickBox = interface.CClickBox(self, w + 8, h, alpha=0, msgid=1)
        self.m_TxtClickBox.SetPos(-8, 0)
        return


class CGetAccountMainDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/register/get_0_dikuang.dlg')
        self.m_SubDlg = None
        self.ShowTurnBackBtn(False)
        self.ShowGetAccountSelDlg()
        interface.Center(self)
        return

    def GetSize(self):
        bg = self.GetObject('bg')
        if bg:
            return bg.GetSize()
        return (0, 0)

    def ShowGetAccountSelDlg(self):
        self.CloseSubDlg()
        self.m_SubDlg = CGetAccountSelDlg(self)
        return

    def ShowLocalAccountDlg(self, accounts):
        self.CloseSubDlg()
        self.m_SubDlg = CLocalAccountDlg(self, accounts)
        return

    def ShowCheckPhoneDlg(self):
        self.CloseSubDlg()
        self.m_SubDlg = CCheckPhoneDlg(self)
        return

    def ShowPhoneAccountDlg(self, phone, accounts):
        self.CloseSubDlg()
        self.m_SubDlg = CPhoneAccountDlg(self, phone, accounts)
        return

    def ShowTurnBackBtn(self, bshow):
        obj = self.GetObject('m_rtBtn')
        obj and obj.SetShow(bshow)
        return

    def TrunBack(self):
        if self.m_SubDlg:
            if isinstance(self.m_SubDlg, CLocalAccountDlg) or isinstance(self.m_SubDlg, CCheckPhoneDlg):
                self.ShowGetAccountSelDlg()
            elif isinstance(self.m_SubDlg, CPhoneAccountDlg):
                self.ShowCheckPhoneDlg()
        return

    def CloseSubDlg(self):
        if self.m_SubDlg and hasattr(self.m_SubDlg, 'CloseWindows'):
            self.m_SubDlg.CloseWindows()
            self.m_SubDlg = None
        return

    def CloseWindows(self):
        global g_MainDlg
        self.CloseSubDlg()
        g_MainDlg = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindows()
        elif msgid == 2:
            self.TrunBack()
        return


class CGetAccountSelDlg(combdialog.CCombDialog, pubdlggetaccount.CGetAccountSelDlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getaccount1.dlg')
        parent.ShowTurnBackBtn(False)
        self.m_Httpobj = None
        return

    def GetGate(self):
        return 'mx'

    def ShowLocalAccountDlg(self, accountdata):
        if accountdata.get('code') != 0:
            self.m_Httpobj = None
            msg = accountdata.get('message', '系統繁忙，獲取失敗')
            import usermacro
            usermacro.PROMPT_MSG(msg)
        else:
            self.ShowCountdown()
            accounts = accountdata.get('account_list', [])
            parent = self.GetParent()
            if parent:
                parent.ShowLocalAccountDlg(accounts)
        return

    def ShowCountdown(self):
        global g_LocalTimer

        def countdown(obj, t):
            obj.m_Time = t
            if t > 0:
                return (
                 t - 1,)
            return

        if hasattr(g_LocalTimer, 'm_CodeTimer') and g_LocalTimer.m_CodeTimer:
            g_LocalTimer.m_CodeTimer.Release()
        g_LocalTimer = interface.CBaseObject(None)
        g_LocalTimer.m_CodeTimer = g_LocalTimer.CreatePyCommand(30, countdown, self.COUNTDOWN - 1)
        g_LocalTimer.m_Time = self.COUNTDOWN
        return

    def GetCountdownTime(self):
        if hasattr(g_LocalTimer, 'm_Time') and g_LocalTimer.m_Time:
            return g_LocalTimer.m_Time
        else:
            return 0
        return

    def ShowCheckPhoneDlg(self):
        parent = self.GetParent()
        if parent:
            parent.ShowCheckPhoneDlg()
        return

    def Hold(self):
        return

    def CloseWindows(self):
        if self.m_Httpobj:
            self.m_Httpobj.Release()
            self.m_Httpobj = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            if not self.m_Httpobj:
                self.m_Httpobj = self.GetLocalAccount()
        elif msgid == 2:
            self.ShowCheckPhoneDlg()
        return


class CLocalAccountDlg(combdialog.CCombDialog, pubdlggetaccount.CLocalAccountDlgBase):

    def __init__(self, parent, accounts):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getaccount2.dlg')
        pubdlggetaccount.CLocalAccountDlgBase.__init__(self, accounts)
        parent.ShowTurnBackBtn(True)
        return

    def ShowNoActTips(self):
        import combmacro
        (x, y, w, h) = self.GetLocData('lst_account')
        self.m_Tips = interface.CTextObject(self, '您的電腦未註冊過帳號', interface.FontLT14_3, 9803157, 0)
        (tw, th) = self.m_Tips.GetSize()
        self.m_Tips.SetPos(x + (w - tw) / 2, y + (h - th) / 2)
        return

    def RefreshAccountList(self):
        import combmacro
        (x, y, w, h) = self.GetLocData('lst_account')
        self.m_List = interface.CList(self, x, y, w, h, alpha=0)
        for aid in self.m_Accounts:
            self.m_List.AddTextItem(aid, 0, interface.FontLT16_2, 20)

        self.m_List.Refresh()
        self.m_List.ResetScrollBar(False)
        return

    def Hold(self):
        return


class CGetAccountMgr(pubdlggetaccount.CGetAccountMgr):

    def GetGameGate(self):
        return 'mx'


class CCheckPhoneDlg(combdialog.CCombDialog, pubdlggetaccount.CCheckPhoneDlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getaccount3.dlg')
        pubdlggetaccount.CCheckPhoneDlgBase.__init__(self, CGetAccountMgr)
        parent.ShowTurnBackBtn(True)
        self.ShowTips(self.PHONE_TIPS, '區號默認為+86', 'NORMAL')
        self.GetObject('btn_msg').SetShow(False)
        self.RefreshCountdown()
        return

    def InitEdit(self):
        import dlgregister, combmacro
        self.m_PhoneEdit = combmacro.CEDIT(dlgregister.CPhoneEdit, 'edit_phone', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_PhoneEdit.m_TipsName = self.PHONE_TIPS
        self.m_PhoneEdit.m_ActiveIdx = self.PHONE_TIPS
        self.m_PhoneEdit.m_EditChange = True
        self.m_PhoneEdit.\j{[w{[ip('請輸入帳號關聯的手機號碼')
        self.m_PhoneEdit.SetLimit(11)
        self.m_CodeEdit = combmacro.CEDIT(dlgregister.C2980CodeEdit, 'edit_code', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_CodeEdit.m_TipsName = self.CODE_TIPS
        self.m_CodeEdit.\j{[w{[ip('請輸入手機收到的驗証碼')
        self.m_CodeEdit.SetMsgID(2)
        self.m_CodeEdit.SetLimit(8)
        self.m_PhoneEdit.SetNextEdit(self.m_CodeEdit)
        self.m_PhoneEdit.Active(True)
        self.m_TipsObjs = {}
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def InitAreaCodeBox(self):
        import areaphonecodedata, combmacro
        hotareadata = areaphonecodedata.HOTINFOLST
        allareadata = areaphonecodedata.INFOLST
        defaultcountry = {'info': '+86', 'phoneCode': 86, 'sCountry': 'CN'}
        (x, y, w, h) = self.GetLocData('loc_areacode')
        self.m_AreaCode = CAreaCodeListBox(self, interface.COLOR_55, interface.FontLT14_3, x, y + 3, w, h - 3, hotareadata, allareadata)
        self.m_AreaCode.SetItemProp(1, 16, 16 * (len(hotareadata) + 2))
        self.m_AreaCode.SetReadOnly(True)
        self.m_AreaCode.SetDefaultCountry(defaultcountry)
        obj = self.GetObject('btn_xiala')
        obj and obj.SetShow(False)
        return

    def GetAreaCodeData(self):
        (areacode, sCountry) = self.m_AreaCode.GetSelectData()
        areacode = '%04d' % areacode
        return (areacode, sCountry)

    def ShowTips(self, objname, tips, sType='WARN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
        import dlgregister
        color = dlgregister.GetColorByType(sType)
        if self.m_TipsObjs.get(objname):
            self.m_TipsObjs[objname].SetText(tips)
            self.m_TipsObjs[objname].SetColor(color)
        else:
            self.m_TipsObjs[objname] = interface.CTextObject(self, tips, interface.FontLT12_1, color, 0)
            (x, y) = obj.GetPos()
            self.m_TipsObjs[objname].SetPos(x, y)
        edit = self.GetEidtByTipsName(objname)
        edit and edit.ResetTipsFlag()
        return

    def HideTips(self, objname):
        if self.m_TipsObjs.get(objname):
            del self.m_TipsObjs[objname]
        return

    def HideSpecialTips(self, edit):
        editlst = [
         self.m_PhoneEdit, self.m_CodeEdit]
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_PhoneEdit, self.m_CodeEdit]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def SetCountdown(self, t):
        btn = self.GetObject('btn_code')
        txt = self.GetObject('chg_code')
        if t > 0:
            txt.SetText(str(t) + '秒後重試')
            btn.Enable(False)
        else:
            txt.SetText('獲取驗証碼')
            btn.Enable(True)
            self.ShowVoiceVerify()
        return

    def ShowVoiceVerify(self):
        self.GetObject('btn_msg').SetShow(True)
        return

    def ShowCountdown(self):
        global g_CodeTimer
        if not g_FirstCode:
            self.ShowVoiceVerify()
        if hasattr(g_CodeTimer, 'm_Time') and g_CodeTimer.m_Time > 0:
            self.SetCountdown(g_CodeTimer.m_Time)
            return

        def countdown(obj, t):
            global g_FirstCode
            obj.m_Time = t
            dlg = GetCheckPhoneDlg()
            if dlg:
                dlg.SetCountdown(t)
            if t > 0:
                return (
                 t - 1,)
            else:
                g_FirstCode = False
            return

        if hasattr(g_CodeTimer, 'm_CodeTimer') and g_CodeTimer.m_CodeTimer:
            g_CodeTimer.m_CodeTimer.Release()
        g_CodeTimer = interface.CBaseObject(None)
        g_CodeTimer.m_CodeTimer = g_CodeTimer.CreatePyCommand(30, countdown, self.MSG_COUNTDOWN)
        self.SetCountdown(self.MSG_COUNTDOWN)
        return

    def RefreshCountdown(self):
        if not g_FirstCode:
            self.ShowVoiceVerify()
        if hasattr(g_CodeTimer, 'm_Time') and g_CodeTimer.m_Time > 0:
            self.SetCountdown(g_CodeTimer.m_Time)
            return
        return

    def GetCountdownTime(self):
        if hasattr(g_CodeTimer, 'm_Time') and g_CodeTimer.m_Time:
            return g_CodeTimer.m_Time
        else:
            return 0
        return

    def ShowTipsDialog(self, sCode, phone, sSmsCenter):

        def Func(msgid):
            if msgid == 1:
                self.m_CodeEdit.SetText(sCode)
            return

        txt = '您的驗証碼是#Y%s#n，請使用手機號（%s）編輯短信#Y%s#n發送到#Y%s#n上，發送短信後請等待30秒，然後點擊下面的「短信已發送」選項。\nQ短信已發送' % (sCode, phone, sCode, sSmsCenter)
        import dlgnpc
        dlgnpc.ShowClientDlg(txt, '')
        return

    def ShowPhoneAccountDlg(self, phone, accounts):
        parent = self.GetParent()
        if parent:
            parent.ShowPhoneAccountDlg(phone, accounts)
        return

    def OnEditChange(self, ctrl):
        if getattr(ctrl, 'm_ActiveIdx', None) == self.PHONE_TIPS:
            self.HideTips(self.PHONE_TIPS)
            phone = self.m_PhoneEdit.GetText().strip()
            if not phone:
                self.ShowTips(self.PHONE_TIPS, '區號默認為+86', 'NORMAL')
        return

    def ShowVoiceTips(self):

        def doget(obj):
            dlg = obj.m_obj.Get()
            if dlg:
                dlg.DoGetPhoneVoice()
            return

        import commondialog
        mbox = commondialog.ShowNewMessageBox('點擊【確定】接收語言驗証碼，您將收到一個語音自動播放驗証碼的來電', ('確認',
                                                                                                                                                                                                                                                                          '取消'), (doget, None))
        mbox.m_obj = interface.CShadowObject(self)
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.GetPhoneVoice()
        elif msgid == 2:
            self.FindBack()
        elif msgid == 3:
            self.GetCode()
        return


class CPhoneAccountDlg(combdialog.CCombDialog, pubdlggetaccount.CPhoneAccountDlgBase):

    def __init__(self, parent, phone, accounts):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getaccount4.dlg')
        pubdlggetaccount.CPhoneAccountDlgBase.__init__(self, phone, accounts)
        parent.ShowTurnBackBtn(True)
        return

    def RefreshAccountList(self):
        import combmacro
        (x, y, w, h) = self.GetLocData('lst_account')
        self.m_List = interface.CList(self, x, y, w, h, alpha=0)
        for aid in self.m_Accounts:
            self.m_List.AddTextItem(aid, 0, interface.FontLT16_2, 20)

        self.m_List.Refresh()
        self.m_List.ResetScrollBar(False)
        return

    def ShowPhoneTips(self):
        txtobj = self.GetObject('txt_phone')
        if txtobj:
            size = len(self.m_Phone) - 6
            phone = self.m_Phone[:3] + '*' * size + self.m_Phone[-3:]
            txt = '手機號碼%s關聯/綁定的帳號如下：' % phone
            txtobj.SetText(txt)
        return

    def ShowNoActTips(self):
        import combmacro
        (x, y, w, h) = self.GetLocData('lst_account')
        self.m_Tips = interface.CTextObject(self, '您的手機號暫未綁定或關聯戰盟帳號', interface.FontLT14_3, 9803157, 0)
        (tw, th) = self.m_Tips.GetSize()
        self.m_Tips.SetPos(x + (w - tw) / 2, y + (h - th) / 2)
        return

    def Hold(self):
        return


return
