# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlggetpass.py
import interface, combdialog, dlgregister, pubdlggetpass, pubactfunction
g_CodeTimer = None
g_FireCode = True
g_MainDlg = None

def ModuleReset():
    global g_CodeTimer
    global g_FireCode
    global g_MainDlg
    g_CodeTimer = None
    g_FireCode = True
    g_MainDlg = None
    return


def ShowConfimeDlg():
    global g_MainDlg
    if g_MainDlg:
        g_MainDlg.ShowConfirmDlg()
    else:
        g_MainDlg = CGetPassMainDlg()
    return


def GetPhoneDlg():
    if g_MainDlg and isinstance(g_MainDlg.m_SubDlg, CPhoneDlg):
        return g_MainDlg.m_SubDlg
    else:
        return
    return


def CloseMainDlg():
    if g_MainDlg:
        g_MainDlg.CloseWindows()
    return


class CGetPassMainDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'login/register/get_0_dikuang.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_SubDlg = None
        self.m_SubDlgInfo = None
        self.ShowTurnBackBtn(False)
        self.ShowConfirmDlg()
        return

    def GetSize(self):
        bg = self.GetObject('bg')
        if bg:
            return bg.GetSize()
        return (0, 0)

    def CloseSubDlg(self):
        if self.m_SubDlg and hasattr(self.m_SubDlg, 'CloseWindows'):
            self.m_SubDlg.CloseWindows()
        self.m_SubDlg = None
        return

    def ShowConfirmDlg(self):
        self.CloseSubDlg()
        self.m_SubDlg = CConfirmDlg(self)
        return

    def ShowNDYTGetPassDlg(self):
        self.CloseSubDlg()
        self.m_SubDlg = CNDYTGetPassDlg(self)
        return

    def ShowSelectDlg(self, email, phone, qq):
        self.CloseSubDlg()
        self.m_SubDlgInfo = [email, phone, qq]
        self.m_SubDlg = CSelectDlg(self, email, phone, qq)
        return

    def ShowPhoneGetPassDlg(self, email, phone, qq):
        self.CloseSubDlg()
        self.m_SubDlgInfo = [email, phone, qq]
        self.m_SubDlg = CPhoneDlg(self, email)
        return

    def ShowEmailGetPassDlg(self, fbemail, bindeamil, phone, qq):
        self.CloseSubDlg()
        self.m_SubDlgInfo = [fbemail, bindeamil, phone, qq]
        self.m_SubDlg = CEmailDlg(self, fbemail, bindeamil, phone, qq)
        return

    def ShowNDYTEmailDlg(self, email):
        self.CloseSubDlg()
        self.m_SubDlg = CNDYTEmailDlg(self, email)
        return

    def ShowTurnBackBtn(self, bshow):
        obj = self.GetObject('m_rtBtn')
        obj and obj.SetShow(bshow)
        return

    def TrunBack(self):
        if self.m_SubDlg:
            if isinstance(self.m_SubDlg, CSelectDlg):
                self.ShowConfirmDlg()
            elif isinstance(self.m_SubDlg, CNDYTGetPassDlg):
                self.ShowConfirmDlg()
            elif isinstance(self.m_SubDlg, CNDYTEmailDlg):
                self.ShowConfirmDlg()
            elif isinstance(self.m_SubDlg, CPhoneDlg):
                (email, phone, qq) = self.m_SubDlgInfo
                if email.isdigit() or email.endswith('@2980.com'):
                    if qq:
                        self.ShowSelectDlg(email, phone, qq)
                    else:
                        self.ShowConfirmDlg()
                elif phone:
                    self.ShowSelectDlg(email, phone, qq)
                else:
                    self.ShowConfirmDlg()
            elif isinstance(self.m_SubDlg, CEmailDlg):
                (fbemail, bindeamil, phone, qq) = self.m_SubDlgInfo
                if phone:
                    self.ShowSelectDlg(fbemail, phone, qq)
                else:
                    self.ShowConfirmDlg()
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


class CAccountMgr(pubdlggetpass.CAccountMgr):

    def GetGameGate(self):
        return 'mx'


class C2980Mgr(pubdlggetpass.C2980Mgr):

    def GetUrlVerifyMaskCode(self):
        return '882f035bc58e4cada985030ab512a3ec'

    def GetPortKey(self):
        return '0066b3f7-4183-4834-9adf-9695c220ea48'

    def GetGameName(self):
        return 'mx'

    def GetGameGate(self):
        return 'mxgame'


class CConfirmDlg(combdialog.CCombDialog, pubdlggetpass.CConfirmDlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_1.dlg')
        pubdlggetpass.CConfirmDlgBase.__init__(self, CAccountMgr)
        parent.ShowTurnBackBtn(False)
        self.CreateNDYTLink()
        return

    def InitEdit(self):
        import combmacro
        self.m_AccountEdit = combmacro.CEDIT(dlgregister.CCommMailEdit, 'edit_act', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_AccountEdit.m_TipsName = self.ACT_TIPS
        self.m_AccountEdit.SetTxtTip('請輸入您要找回的帳號')
        self.m_AccountEdit.SetLimit(50)
        self.m_CodeEidt = combmacro.CEDIT(dlgregister.CCommCodeEdit, 'edit_code', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_CodeEidt.m_TipsName = self.CODE_TIPS
        self.m_CodeEidt.SetTxtTip('請輸入驗証碼')
        self.m_CodeEidt.SetLimit(4)
        self.m_AccountEdit.SetNextEdit(self.m_CodeEidt)
        self.m_CodeEidt.SetMsgID(1)
        self.m_AccountEdit.Active(True)
        self.m_TipsObjs = {}
        return

    def CreateNDYTLink(self):
        import wraptextobj
        (x, y) = self.GetObject('btn_feiduoyitong').GetPos()
        self.m_UnDYTPwd = wraptextobj.CUnderLineClickText(self, x, y, '找回非戰盟密碼', 3176608, 3176608, interface.FontLT14_3, msgid=4)
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def ShowTips(self, objname, tips, sType='WARN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
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
         self.m_AccountEdit, self.m_CodeEidt]
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_AccountEdit, self.m_CodeEidt]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def ShowCheckCodeImg(self, fname, path):
        if not getattr(self, 'm_CheckCode', None):
            self.m_CheckCode = dlgregister.CCheckCodeBox(self)
            (x, y) = self.GetObject('code_pic').GetPos()
            self.m_CheckCode.SetPos(x, y)
        self.m_CheckCode.ShowCodeImg(fname, path)
        return

    def ShowSelectDlg(self, email, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowSelectDlg(email, mobile, qq)
        return

    def ShowPhoneGetPassDlg(self, email, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowPhoneGetPassDlg(email, mobile, qq)
        return

    def ShowEmailGetPassDlg(self, fbemail, bindeamil, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowEmailGetPassDlg(fbemail, bindeamil, mobile, qq)
        return

    def ShowNDYTGetPassDlg(self):
        import usermacro
        usermacro.PROMPT_MSG('非戰盟帳號請至官網客服專區找回密碼')
        return
        parent = self.GetParent()
        if parent:
            parent.ShowNDYTGetPassDlg()
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.GetInfo()
        elif msgid == 3:
            self.GetPhotoCode()
        elif msgid == 4:
            self.ShowNDYTGetPassDlg()
        return


import dlgaboutpwd

class CSearchServerListBox(dlgaboutpwd.CSearchServerListBox):

    def __init__(self, parent, color, font, x, y, w, h, fname=b'combdialog\\\xd2\xe6\xcd\xf8\xc8\xa6\\\xb0\xb4\xc5\xa5\\\xcf\xc2\xc0\xad.igs'):
        interface.CListBox.__init__(self, parent, color, font, x, y, w, h, fname)
        self.AliasServerName()
        return


class CNDYTGetPassDlg(combdialog.CCombDialog, pubdlggetpass.CNDYTGetPassDlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_6.dlg')
        pubdlggetpass.CNDYTGetPassDlgBase.__init__(self, CAccountMgr)
        parent.ShowTurnBackBtn(True)
        self.CreateServerEdit()
        return

    def InitEdit(self):
        import combmacro
        self.m_EmailEdit = combmacro.CEDIT(dlgregister.CCommMailEdit, 'edit_act', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_EmailEdit.m_TipsName = self.ACT_TIPS
        self.m_EmailEdit.SetTxtTip('請輸入您註冊時填寫的聯繫郵箱')
        self.m_EmailEdit.SetLimit(50)
        self.m_AccountEidt = combmacro.CEDIT(dlgregister.CAccountEdit, 'edit_id', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_AccountEidt.m_TipsName = self.CODE_TIPS
        self.m_AccountEidt.SetTxtTip('請輸入角色ID')
        self.m_AccountEidt.SetLimit(10)
        self.m_EmailEdit.SetNextEdit(self.m_AccountEidt)
        self.m_AccountEidt.SetMsgID(1)
        self.m_EmailEdit.Active(True)
        self.m_TipsObjs = {}
        return

    def CreateServerEdit(self):
        import combmacro
        self.m_ServerSearchEdit = combmacro.CLISTBOX(CSearchServerListBox, 'edit_server', self, [0, 0], interface.FontLT12_1)
        self.m_ServerSearchEdit.SetItemProp(2, 16, 72)
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def GetServerID(self):
        serName = self.m_ServerSearchEdit.GetText()
        if serName:
            serverid = self.m_ServerSearchEdit.m_ServerRecord[serName]
            return serverid
        return

    def ShowTips(self, objname, tips, sType='WARN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
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
         self.m_EmailEdit, self.m_AccountEidt]
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_EmailEdit, self.m_AccountEidt]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def ShowNDYTEmailDlg(self, email):
        parent = self.GetParent()
        if parent:
            parent.ShowNDYTEmailDlg(email)
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.OnComfirm()
        return


class CSelectDlg(combdialog.CCombDialog, pubdlggetpass.CSelectDlgBase):

    def __init__(self, parent, fbemail, phone, qq):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_5choose.dlg')
        pubdlggetpass.CSelectDlgBase.__init__(self, fbemail, phone, qq, CAccountMgr, C2980Mgr)
        parent.ShowTurnBackBtn(True)
        return

    def RefreshTitleTips(self):
        obj = self.GetObject('txt_title')
        if obj:
            title = '正在找回%s的密碼，請選擇找回方式' % pubdlggetpass.GetShowEmail(self.m_FbEmail)
            obj.SetText(title)
        return

    def RefreshItemTips(self):
        obj = self.GetObject('txt_email')
        if obj:
            title = '（%s）' % pubdlggetpass.GetShowEmail(self.m_BindEmail)
            obj.SetText(title)
        return

    def ShowPhoneTips(self, bShow):
        obj = self.GetObject('txt_phone')
        obj and obj.SetShow(bShow)
        return

    def ShowPhoneGetPassDlg(self, email, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowPhoneGetPassDlg(email, mobile, qq)
        return

    def ShowEmailGetPassDlg(self, fbemail, bindeamil, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowEmailGetPassDlg(fbemail, bindeamil, mobile, qq)
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.ShowPhoneGetPassDlg(self.m_FbEmail, self.m_Phone, self.m_QQ)
        elif msgid == 2:
            self.DoFindBack()
        return


class CEmailDlg(combdialog.CCombDialog, pubdlggetpass.CEmailDlgBase):

    def __init__(self, parent, fbemail, bindemail, phone, qq):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_2mail.dlg')
        pubdlggetpass.CEmailDlgBase.__init__(self, fbemail, bindemail, phone, qq, CAccountMgr, C2980Mgr)
        parent.ShowTurnBackBtn(True)
        self.m_Time = 0
        self.m_Timer = None
        self.ShowCountdown()
        return

    def RefreshTitleTips(self):
        obj = self.GetObject('txt_title')
        if obj:
            title = '正在找回%s的密碼' % pubdlggetpass.GetShowEmail(self.m_FbEmail)
            obj.SetText(title)
        return

    def RefreshContent(self):
        obj = self.GetObject('txt_content')
        if obj:
            title = '我們已向您的郵箱%s發送了\n一封密碼找回郵件' % pubdlggetpass.GetShowEmail(self.m_BindEmail)
            obj.SetText(title)
        return

    def RefreshMobileTips(self):
        bshow = False
        if self.m_HasBindPhone:
            bshow = True
        obj = self.GetObject('phone_tips1')
        obj and obj.SetShow(bshow)
        obj = self.GetObject('phone_tips2')
        obj and obj.SetShow(bshow)
        return

    def ShowPhoneGetPassDlg(self, email, mobile, qq):
        parent = self.GetParent()
        if parent:
            parent.ShowPhoneGetPassDlg(email, mobile, qq)
        return

    def ShowCountdown(self):

        def countdown(obj, t):
            obj.m_Time = t
            if t > 0:
                return (
                 t - 1,)
            return

        self.m_Time = self.COUNTDOWN
        self.m_Timer = self.CreatePyCommand(30, countdown, self.COUNTDOWN - 1)
        return

    def GetCountdownTime(self):
        return self.m_Time

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.DoConfirm()
        elif msgid == 2:
            self.ReSend()
        elif msgid == 3:
            self.ShowPhoneGetPassDlg(self.m_FbEmail, self.m_Phone, self.m_QQ)
        return


class CNDYTEmailDlg(combdialog.CCombDialog, pubdlggetpass.CNDYTEmailDlgBase):

    def __init__(self, parent, email):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_7.dlg')
        pubdlggetpass.CNDYTEmailDlgBase.__init__(self, email, CAccountMgr)
        parent.ShowTurnBackBtn(True)
        self.m_Time = 0
        self.m_Timer = None
        self.ShowCountdown()
        return

    def RefreshContent(self):
        obj = self.GetObject('txt_content')
        if obj:
            title = '我們已向您的郵箱%s發送了\n一封密碼找回郵件' % pubdlggetpass.GetShowEmail(self.m_Mail)
            obj.SetText(title)
        return

    def ShowCountdown(self):

        def countdown(obj, t):
            obj.m_Time = t
            if t > 0:
                return (
                 t - 1,)
            return

        self.m_Time = self.COUNTDOWN
        self.m_Timer = self.CreatePyCommand(30, countdown, self.COUNTDOWN - 1)
        return

    def GetCountdownTime(self):
        return self.m_Time

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.GoConfirm()
        return


class CPhoneDlg(combdialog.CCombDialog, pubdlggetpass.CPhoneDlgBase):

    def __init__(self, parent, email):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/getpassword_3telephone.dlg')
        pubdlggetpass.CPhoneDlgBase.__init__(self, email, CAccountMgr, C2980Mgr)
        parent.ShowTurnBackBtn(True)
        self.AfterInit()
        self.GetObject('btn_msg').SetShow(False)
        self.RefreshCountdown()
        return

    def RefreshTitleTips(self):
        obj = self.GetObject('txt_title')
        if obj:
            if self.m_Email.isdigit():
                showtxt = pubdlggetpass.GetShowPhone(self.m_Email)
            else:
                showtxt = pubdlggetpass.GetShowEmail(self.m_Email)
            title = '正在找回%s的密碼' % showtxt
            obj.SetText(title)
        return

    def InitEdit(self):
        import dlgregister, combmacro
        if self.m_Email.isdigit():
            showtxt = pubdlggetpass.GetShowPhone(self.m_Email)
        else:
            showtxt = pubdlggetpass.GetShowEmail(self.m_Email)
        self.m_AccountTxt = combmacro.CTEXT(interface.CTextObject, 'edit_account', self, showtxt, interface.FontLT14_3, interface.COLOR_55)
        self.m_PhoneEdit = combmacro.CEDIT(dlgregister.CPhoneEdit, 'edit_phone', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_PhoneEdit.m_TipsName = self.PHONE_TIPS
        self.m_PhoneEdit.m_ActiveIdx = self.PHONE_TIPS
        self.m_PhoneEdit.m_EditChange = True
        self.m_PhoneEdit.SetTxtTip('請輸入手機號碼')
        self.m_PhoneEdit.SetLimit(11)
        self.m_CodeEdit = combmacro.CEDIT(dlgregister.C2980CodeEdit, 'edit_code', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_CodeEdit.m_TipsName = self.CODE_TIPS
        self.m_CodeEdit.SetTxtTip('請輸入手機收到的驗証碼')
        self.m_CodeEdit.SetMsgID(2)
        self.m_CodeEdit.SetLimit(9)
        self.m_Pwd1Edit = combmacro.CEDIT(dlgregister.CPwdEdit, 'edit_pwd1', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_Pwd1Edit.m_TipsName = self.PWD1_TIPS
        self.m_Pwd1Edit.SetLimit(16)
        self.m_Pwd1Edit.SetTxtTip('請設置您的新密碼')
        self.m_Pwd1Edit.m_IsPassword = True
        self.m_Pwd1Edit.m_EditChange = True
        self.m_Pwd2Edit = combmacro.CEDIT(dlgregister.CPwdEdit, 'edit_pwd2', self, interface.COLOR_55, interface.FontLT14_3, linecolor=0)
        self.m_Pwd2Edit.m_TipsName = self.PWD2_TIPS
        self.m_Pwd2Edit.SetLimit(16)
        self.m_Pwd2Edit.SetTxtTip('請再次輸入新密碼')
        self.m_Pwd2Edit.m_IsPassword = True
        self.m_PhoneEdit.Active(True)
        self.m_PhoneEdit.SetNextEdit(self.m_CodeEdit)
        self.m_CodeEdit.SetNextEdit(self.m_Pwd1Edit)
        self.m_Pwd1Edit.SetNextEdit(self.m_Pwd2Edit)
        self.m_Pwd2Edit.SetMsgID(3)
        self.m_TipsObjs = {}
        return

    def AfterInit(self):
        if self.m_IsPhone:
            phone = pubdlggetpass.GetPhone(self.m_Email)
            self.m_PhoneEdit.SetText(phone)
            self.m_PhoneEdit.Enable(False)
            self.m_AreaCode.Enable(False)
            self.m_CodeEdit.Active(True)
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def InitAreaCodeBox(self):
        import areaphonecodedata, combmacro, dlggetbackaccount
        hotareadata = areaphonecodedata.HOTINFOLST
        allareadata = areaphonecodedata.INFOLST
        defaultcountry = {'info': '+86', 'phoneCode': 86, 'sCountry': 'CN'}
        (x, y, w, h) = self.GetLocData('loc_areacode')
        self.m_AreaCode = dlggetbackaccount.CAreaCodeListBox(self, interface.COLOR_55, interface.FontLT14_3, x, y + 3, w, h - 3, hotareadata, allareadata)
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
         self.m_PhoneEdit, self.m_CodeEdit, self.m_Pwd1Edit, self.m_Pwd2Edit]
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_PhoneEdit, self.m_CodeEdit, self.m_Pwd1Edit, self.m_Pwd2Edit]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def ShowVoiceVerify(self):
        self.GetObject('btn_msg').SetShow(True)
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

    def ShowCountdown(self):
        global g_CodeTimer
        if not g_FireCode:
            self.ShowVoiceVerify()
        if hasattr(g_CodeTimer, 'm_Time') and g_CodeTimer.m_Time > 0:
            self.SetCountdown(g_CodeTimer.m_Time)
            return

        def countdown(obj, t):
            global g_FireCode
            obj.m_Time = t
            dlg = GetPhoneDlg()
            if dlg:
                dlg.SetCountdown(t)
            if t > 0:
                return (
                 t - 1,)
            else:
                g_FireCode = False
            return

        if hasattr(g_CodeTimer, 'm_CodeTimer') and g_CodeTimer.m_CodeTimer:
            g_CodeTimer.m_CodeTimer.Release()
        g_CodeTimer = interface.CBaseObject(None)
        g_CodeTimer.m_CodeTimer = g_CodeTimer.CreatePyCommand(30, countdown, self.MSG_COUNTDOWN)
        self.SetCountdown(self.MSG_COUNTDOWN)
        return

    def RefreshCountdown(self):
        if not g_FireCode:
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

    def OnEditChange(self, ctrl):
        if getattr(ctrl, 'm_ActiveIdx', None) == self.PHONE_TIPS:
            self.HideTips(self.PHONE_TIPS)
            phone = self.m_PhoneEdit.GetText().strip()
            if not phone:
                self.ShowTips(self.PHONE_TIPS, '區號默認為+86', 'NORMAL')
        elif getattr(ctrl, 'm_ActiveIdx', None) == self.PWD1_TIPS:
            self.HideTips(self.PWD2_TIPS)
        return

    def Hold(self):
        return

    def OnCommChangePwd(self, err_code, dct, *args):
        pubdlggetpass.CPhoneDlgBase.OnCommChangePwd(self, err_code, dct, *args)
        CloseMainDlg()
        return

    def On2980ChangePwd(self, err_code, dct, *args):
        pubdlggetpass.CPhoneDlgBase.On2980ChangePwd(self, err_code, dct, *args)
        CloseMainDlg()
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.GetPhoneVoice()
        elif msgid == 3:
            self.ChangePwd()
        elif msgid == 4:
            self.GetCode()
        return


return
