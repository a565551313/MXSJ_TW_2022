# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgregister.py
import interface, combdialog, combmacro, gamefont, style, pubregister, pub2980register, pubdlgreg, ui
g_RegMainDlg = None
g_ReSendDlg = None
g_RegCommonMgr = None
g_Reg2980Mgr = None
g_Reg2980CodeTimer = None
g_FirstReg2980Code = True
g_RegPhoneCodeTimer = None
g_FirstRegPhoneCode = True
g_ReSendTimer = None
g_LastRegDlg = 1

def ModuleReset():
    global g_FirstReg2980Code
    global g_FirstRegPhoneCode
    global g_LastRegDlg
    global g_ReSendDlg
    global g_ReSendTimer
    global g_Reg2980CodeTimer
    global g_Reg2980Mgr
    global g_RegCommonMgr
    global g_RegMainDlg
    global g_RegPhoneCodeTimer
    g_RegMainDlg = None
    g_ReSendDlg = None
    g_RegCommonMgr = None
    g_Reg2980Mgr = None
    g_Reg2980CodeTimer = None
    g_FirstReg2980Code = True
    g_RegPhoneCodeTimer = None
    g_FirstRegPhoneCode = True
    g_ReSendTimer = None
    g_LastRegDlg = 1
    return


FontID18 = gamefont.CreateFont(gamefont.TYPE_SIMHEI, 18)

def ShowRegisterDlg():
    global g_RegMainDlg
    g_RegMainDlg = CRegMainDlg()
    return


def GetRegCommonDlg():
    if g_RegMainDlg:
        if g_RegMainDlg.m_CommDlg and g_RegMainDlg.m_CommDlg.GetShow():
            return g_RegMainDlg.m_CommDlg
    return


def GetReg2980Dlg():
    if g_RegMainDlg:
        if g_RegMainDlg.m_2980Dlg and g_RegMainDlg.m_2980Dlg.GetShow():
            return g_RegMainDlg.m_2980Dlg
    return


def GetReSendDlg():
    if g_ReSendDlg and g_ReSendDlg.GetShow():
        return g_ReSendDlg
    return


def CloseRegDlg():
    if g_RegMainDlg:
        g_RegMainDlg.CloseWindows()
    return


def SetLastRegDlg(flag):
    global g_LastRegDlg
    g_LastRegDlg = flag
    return


def GetColorByType(sType):
    type2color = {'WARN': 16711680, 
       'NORMAL': 0, 
       'FRIEND': 3176608}
    return type2color.get(sType, 16711680)


class CRegEdit(interface.CEdit):

    def GetLineColor(self, linecolor):
        return linecolor

    def Clear(self):
        interface.CEdit.Clear(self)
        self.ShowTxtTip()
        return

    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        if len(self.m_Data) == 0:
            self.ShowTxtTip()
        self.HideEditTips()
        if hasattr(self, 'm_EditChange'):
            self.GetParent().OnEditChange(self)
        return

    def DeleteSelected(self):
        interface.CEdit.DeleteSelected(self)
        if len(self.m_Data) == 0:
            self.ShowTxtTip()
        self.HideEditTips()
        if hasattr(self, 'm_EditChange'):
            self.GetParent().OnEditChange(self)
        return

    def AddChar(self, c):
        interface.CEdit.AddChar(self, c)
        self.m_EditTip = None
        if hasattr(self, 'm_EditChange'):
            self.GetParent().OnEditChange(self)
        return

    def ShowEditTips(self, sMsg):
        if hasattr(self, 'm_TipsName'):
            self.GetParent().ShowTips(self.m_TipsName, sMsg)
            self.m_HideTipsFlag = True
        return

    def HideEditTips(self):
        if hasattr(self, 'm_TipsName'):
            self.GetParent().HideTips(self.m_TipsName)
            self.m_HideTipsFlag = False
        return

    def IsTooLong(self, char):
        if self.m_Limit:
            selectedcount = self.GetSelectedCount()
            l = 0
            for ch in self.m_Data:
                l += len(ch[1])

            if l - selectedcount + len(char) > self.m_Limit:
                return True
        return False

    def Active(self, is_active):
        interface.CEdit.Active(self, is_active)
        parent = self.GetParent()
        if parent and hasattr(parent, 'HideSpecialTips'):
            parent.HideSpecialTips(self)
        return

    def HideSpecialTips(self):
        if hasattr(self, 'm_HideTipsFlag') and self.m_HideTipsFlag:
            self.HideEditTips()
        return

    def ResetTipsFlag(self):
        if hasattr(self, 'm_HideTipsFlag'):
            self.m_HideTipsFlag = False
        return

    def SetTxtTip(self, txt, color=8947848):
        self.m_TipTxt = txt
        self.m_TipColor = color
        self.ShowTxtTip()
        return

    def ShowTxtTip(self):
        self.m_EditTip = None
        if hasattr(self, 'm_TipTxt') and self.m_TipTxt != '':
            self.m_EditTip = interface.CTextObject(self, self.m_TipTxt, interface.FontST12, self.m_TipColor)
        return

    def SetMsgID(self, msgid):
        self.m_MsgID = msgid
        return


class CAccountEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit():
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個字符' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        return


class CCommMailEdit(CRegEdit):

    def AddChar(self, c):
        try:
            import loginin
            if loginin.KeyDisturb(ord(c)):
                return
        except:
            pass

        if pubregister.CValid.IsValidMailChar(c):
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個字符' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        return


class CPhoneAreaListBox(interface.CListBox):

    def AddText(self, txt):
        sArea = txt
        if '(+' in txt:
            ileft = txt.find('(+')
            iRight = txt.find(')')
            sArea = txt[ileft + len('('):iRight]
        interface.CListBox.AddText(self, sArea)
        return

    def SetListW(self, iW):
        self.m_iListWidth = iW
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            tl = self.m_TextList
            if len(tl):
                (_, ph) = self.GetSize()
                self.m_List = self.CMyList(self, 0, ph, self.m_iListWidth, self.m_ItemHeightAmount, hspace=self.m_ItemSpace)
                self.m_List.Capture(1, 1)
                for i in xrange(len(self.m_TextList)):
                    self.m_List.AddTextItem(self.m_TextList[i], interface.COLOR_54, self.m_FontID, self.m_ItemHeight, -1, 8424071, -1, i + 1)

                self.m_List.ResetScrollBar(False)
                self.m_List.Refresh(0)
        return


class C2980MailEdit(CRegEdit):

    def AddChar(self, c):
        try:
            import loginin
            if loginin.KeyDisturb(ord(c)):
                return
        except:
            pass

        if pub2980register.CValid.IsValidMailChar(c):
            if self.IsTooLong(c):
                self.ShowEditTips('只能輸入%d個字母或數字' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('只能輸入字母或數字')
        return


class CPwdEdit(CRegEdit):

    def AddChar(self, c):
        if c.isalnum():
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個數字和字母' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('只能輸入數字或字母')
        return


class CCommCodeEdit(CRegEdit):

    def AddChar(self, c):
        if c.isalnum():
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個數字和字母' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('只能輸入數字或字母')
        return


class CIDCodeEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit() or c in 'xX':
            if self.IsTooLong(c):
                self.ShowEditTips('請輸入年滿18歲的有效身份証號碼')
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('請輸入年滿18歲的有效身份証號碼')
        return


class CNameEdit(CRegEdit):

    def AddChar(self, c):
        if self.IsChinese(c):
            if self.IsTooLong(c):
                self.ShowEditTips('請輸入你的真實姓名')
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('請輸入簡體中文姓名')
        return

    def IsChinese(self, s):
        if interface.GCODE == interface.BIG5:
            return True
        import misc
        return misc.IsChinese(s)


class C2980CodeEdit(CRegEdit):

    def AddChar(self, c):
        if c.isalnum():
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個數字和字母' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('只能輸入數字或字母')
        return


class CPhoneEdit(CRegEdit):

    def AddChar(self, c):
        if c.isdigit():
            if self.IsTooLong(c):
                self.ShowEditTips('最多輸入%d個數字' % self.m_Limit)
                return
            CRegEdit.AddChar(self, c)
        else:
            self.ShowEditTips('只能輸入數字')
        return


class CCheckCodeBox(interface.CBoxObject):

    def __init__(self, parent):
        interface.CBoxObject.__init__(self, parent, 0, 0, 0, 0)
        return

    def ShowCodeImg(self, fname, path):
        if fname:
            try:
                self.m_CodeImg = ui.CImage(self, fname, path)
                return
            except Exception, e:
                print 'Load CodeImg Err:', e

        self.m_CodeImg = ui.CImage(self, 'combdialog/娸芞/openerror.igs', interface.UIPath)
        self.m_CodeImg.SetPos(7, 0)
        return


class CRegMainDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'login/register/reg_0_dikuang.dlg')
        self.m_CommDlg = None
        self.m_2980Dlg = None
        self.m_SuccDlg = None
        interface.Center(self)
        self.Capture(1, 0)
        if g_LastRegDlg == 1:
            self.GetObject('btn_comm').LeftUp()
            self.GetObject('btn_comm').Leave()
        else:
            self.GetObject('btn_2980').LeftUp()
            self.GetObject('btn_2980').Leave()
        self.ShowTurnBackBtn(False)
        return

    def ShowSwitchCommonDlg(self, bShow):
        if bShow:
            SetLastRegDlg(1)
            self.ShowSwitch2980Dlg(False)
            if not self.m_CommDlg:
                self.m_CommDlg = CRegCommonDlg(self)
            else:
                self.m_CommDlg.SetShow(True)
        elif self.m_CommDlg:
            self.m_CommDlg.CloseWindows()
        self.m_CommDlg = None
        return

    def ShowSwitch2980Dlg(self, bShow):
        if bShow:
            SetLastRegDlg(2)
            self.ShowSwitchCommonDlg(False)
            if not self.m_2980Dlg:
                self.m_2980Dlg = CReg2980Dlg(self)
            else:
                self.m_2980Dlg.SetShow(True)
        elif self.m_2980Dlg:
            self.m_2980Dlg.CloseWindows()
        self.m_2980Dlg = None
        return

    def ShowReSendDlg(self):
        global g_ReSendDlg
        self.CloseWindows()
        g_ReSendDlg = CReSendDlg()
        return

    def ShowCommSuccDlg(self, mail):
        self.ShowDikuang(False)
        self.m_SuccDlg = CCommonSuccDlg(self, mail)
        return

    def Show2980SuccDlg(self, mail):
        self.ShowDikuang(False)
        self.m_SuccDlg = C2980SuccDlg(self, mail)
        return

    def ShowPhoneSuccDlg(self, phone):
        self.ShowDikuang(False)
        self.m_SuccDlg = CPhoneSuccDlg(self, phone)
        return

    def ShowDikuang(self, bshow):
        names = [1, 2, 3, 4, 5]
        for s in names:
            obj = self.GetObject(s)
            obj and obj.SetShow(bshow)

        if bshow:
            if g_LastRegDlg == 1:
                self.ShowSwitchCommonDlg(True)
            else:
                self.ShowSwitch2980Dlg(True)
        else:
            self.ShowSwitchCommonDlg(False)
            self.ShowSwitch2980Dlg(False)
        return

    def GetSize(self):
        bg = self.GetObject('bg')
        if bg:
            return bg.GetSize()
        return (0, 0)

    def ShowTurnBackBtn(self, bshow):
        obj = self.GetObject('m_rtBtn')
        obj and obj.SetShow(bshow)
        return

    def TurnBack(self):
        if self.m_SuccDlg and self.m_SuccDlg.GetShow():
            self.CloseSuccDlg()
            self.ShowDikuang(True)
            self.ShowTurnBackBtn(False)
        return

    def CloseSuccDlg(self):
        if self.m_SuccDlg and hasattr(self.m_SuccDlg, 'CloseWindows'):
            self.m_SuccDlg.CloseWindows()
        self.m_SuccDlg = None
        return

    def CloseWindows(self):
        global g_RegMainDlg
        self.ShowSwitchCommonDlg(False)
        self.ShowSwitch2980Dlg(False)
        self.CloseSuccDlg()
        g_RegMainDlg = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.TurnBack()
        elif msgid == 2:
            self.ShowSwitch2980Dlg(True)
        elif msgid == 3:
            self.ShowSwitchCommonDlg(True)
        elif msgid == 4:
            self.CloseWindows()
        elif msgid == 5:
            self.ShowReSendDlg()
        return


class CRegCommonMgr(pubdlgreg.CRegCommonMgr):

    def GetGateSrc(self):
        return 'mx'

    def GetUrlVerifyMaskCode(self):
        return '882f035bc58e4cada985030ab512a3ec'


class CReg2980Mgr(pubdlgreg.CReg2980Mgr):

    def GetUrlVerifyMaskCode(self):
        return '882f035bc58e4cada985030ab512a3ec'

    def GetPortKey(self):
        return '0066b3f7-4183-4834-9adf-9695c220ea48'

    def GetGameName(self):
        return 'mx'

    def GetGameGate(self):
        return 'mxgame'


class CRegCommonDlg(combdialog.CCombDialog, pubdlgreg.CRegCommonDlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/reg_3_common_email.dlg')
        pubdlgreg.CRegCommonDlgBase.__init__(self, CRegCommonMgr, CReg2980Mgr)
        self.RefreshCountDown()
        self.GetObject('btn_pvcode').SetShow(False)
        self.GetObject('btn_agree').SetSelect(False)
        return

    def InitEdit(self):
        self.m_PwdEdit = combmacro.CEDIT(CPwdEdit, 'edit_pwd', self, 0, interface.FontST12, linecolor=0)
        self.m_PwdEdit.m_ActiveIdx = 'pwd'
        self.m_PwdEdit.m_TipsName = self.PWD_TIPS
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit.m_EditChange = True
        self.m_PwdEdit.SetTxtTip('6-16個字母或數字，區分大小寫')
        self.m_PwdEdit2 = combmacro.CEDIT(CPwdEdit, 'edit_pwd2', self, 0, interface.FontST12, linecolor=0)
        self.m_PwdEdit2.m_ActiveIdx = 'pwd2'
        self.m_PwdEdit2.m_TipsName = self.PWD2_TIPS
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.SetMsgID(2)
        self.m_PwdEdit2.m_IsPassword = True
        self.m_PwdEdit2.SetTxtTip('請再次輸入登錄密碼')
        self.m_EmailEdit = combmacro.CEDIT(CCommMailEdit, 'edit_email', self, 0, interface.FontST12, linecolor=0)
        self.m_EmailEdit.m_ActiveIdx = 'email'
        self.m_EmailEdit.m_TipsName = self.EMAIL_TIPS
        self.m_EmailEdit.SetLimit(32)
        self.m_EmailEdit.m_EditChange = True
        self.m_EmailEdit.SetTxtTip('請輸入手機號或常用郵箱')
        self.m_PhoneAreaNumEdit = combmacro.CLISTBOX(CPhoneAreaListBox, 'edit_phonecode', self, 0, interface.FontST12)
        self.m_PhoneAreaNumEdit.m_SelectNotify = True
        self.m_PhoneAreaNumEdit.SetReadOnly(True)
        self.m_PhoneAreaNumEdit.SetItemProp(3, 16, 57)
        self.m_PhoneAreaNumEdit.SetListW(165)
        self.m_PhoneAreaNumEdit.SetDownButtonShow(False)
        import pubphoneareanum
        areaNumList = pubphoneareanum.GetAreaNumList()
        for tInfo in areaNumList:
            (sArea, _, _) = tInfo
            self.m_PhoneAreaNumEdit.AddTextItem(sArea)

        self.m_PhoneEdit = combmacro.CEDIT(CPhoneEdit, 'edit_phone', self, 0, interface.FontST12, linecolor=0)
        self.m_PhoneEdit.m_ActiveIdx = 'phone'
        self.m_PhoneEdit.m_EditChange = True
        self.m_PhoneEdit.m_TipsName = self.PHONE_TIPS
        self.m_PhoneEdit.SetLimit(11)
        self.m_PhoneEdit.SetTxtTip('請輸入手機號')
        self.m_PhoneCodeEdit = combmacro.CEDIT(C2980CodeEdit, 'edit_pcode', self, 0, interface.FontST12, linecolor=0)
        self.m_PhoneCodeEdit.m_ActiveIdx = 'pcode'
        self.m_PhoneCodeEdit.m_TipsName = self.EMAIL2_TIPS
        self.m_PhoneCodeEdit.SetLimit(9)
        self.m_PhoneCodeEdit.SetTxtTip('請輸入手機收到的驗証碼')
        self.m_IDCodeEdit = combmacro.CEDIT(CIDCodeEdit, 'edit_idcode', self, 0, interface.FontST12, linecolor=0)
        self.m_IDCodeEdit.m_ActiveIdx = 'idcode'
        self.m_IDCodeEdit.m_TipsName = 'tips_idcode'
        self.m_IDCodeEdit.SetLimit(18)
        self.m_IDCodeEdit.SetTxtTip('請輸入有效身份証號碼')
        self.m_NameEdit = combmacro.CEDIT(CNameEdit, 'edit_name', self, 0, interface.FontST12, linecolor=0)
        self.m_NameEdit.m_ActiveIdx = 'name'
        self.m_NameEdit.m_TipsName = 'tips_name'
        self.m_NameEdit.SetLimit(12)
        self.m_NameEdit.SetTxtTip('請輸入你的真實姓名')
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PhoneCodeEdit.SetNextEdit(self.m_IDCodeEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_PhoneEdit)
        self.m_IDCodeEdit.SetNextEdit(self.m_NameEdit)
        self.m_NameEdit.SetNextEdit(self.m_EmailEdit)
        self.m_PhoneEdit.SetNextEdit(self.m_PhoneCodeEdit)
        self.m_EmailEdit.Active(True)
        self.CreateServiceBtn()
        self.m_TipsObjs = {}
        return

    def OnSelect(self, iIdx):
        self.m_iAreaNo = iIdx
        return

    def CreateServiceBtn(self):
        obj = self.GetObject('btn_treaty')
        (x, y) = obj.GetPos()
        obj.SetShow(False)
        iOffsetY = style.GetInt(self.GetDlgPath(), 'data_pos_offset_y')
        y += iOffsetY
        self.m_ServiceBtn = interface.CClickRichText(self, x, y, 160, '#u多益戰盟帳號服務條款 ', 2645120, 2645120, interface.FontST12, msgid=1)
        return

    def ClickAgreeBtn(self):
        self.GetObject('btn_agree').LeftUp()
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def ShowTips(self, objname, tips, sType='WARN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
        color = GetColorByType(sType)
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
         self.m_PwdEdit, self.m_PwdEdit2, self.m_EmailEdit, self.m_PhoneCodeEdit, self.m_IDCodeEdit, self.m_NameEdit]
        if hasattr(self.m_EmailEdit, 'm_HideTipsFlag') and self.m_EmailEdit.m_HideTipsFlag:
            self.ShowTips(self.EMAIL_TIPS, '請確保郵箱真實有效，用於註冊後的驗証', 'FRIEND')
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_PwdEdit, self.m_PwdEdit2, self.m_EmailEdit, self.m_PhoneCodeEdit]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def IsAgreeTreaty(self):
        return self.GetObject('btn_agree').IsSelected()

    def ShowCheckCodeImg(self, fname, path):
        return

    def ShowSwitchCodeImg(self, bShow):
        return

    def ShowVoiceVerify(self):
        self.GetObject('btn_pvcode').SetShow(True)
        return

    def SetCountdown(self, t):
        btn = self.GetObject('btn_pcode')
        txt = self.GetObject('chg_pcode')
        if t > 0:
            txt.SetText('重試(%d)' % t)
            btn.Enable(False)
        else:
            txt.SetText('獲取驗証碼')
            btn.Enable(True)
            self.ShowVoiceVerify()
        return

    def ShowCountdown(self):
        global g_RegPhoneCodeTimer
        if not g_FirstRegPhoneCode:
            self.ShowVoiceVerify()
        if hasattr(g_RegPhoneCodeTimer, 'm_Time') and g_RegPhoneCodeTimer.m_Time > 0:
            self.SetCountdown(g_RegPhoneCodeTimer.m_Time)
            return

        def countdown(obj, t):
            global g_FirstRegPhoneCode
            obj.m_Time = t
            dlg = GetRegCommonDlg()
            if dlg:
                dlg.SetCountdown(t)
            if t > 0:
                return (
                 t - 1,)
            else:
                g_FirstRegPhoneCode = False
            return

        if hasattr(g_RegPhoneCodeTimer, 'm_CodeTimer') and g_RegPhoneCodeTimer.m_CodeTimer:
            g_RegPhoneCodeTimer.m_CodeTimer.Release()
        g_RegPhoneCodeTimer = interface.CBaseObject(None)
        g_RegPhoneCodeTimer.m_CodeTimer = g_RegPhoneCodeTimer.CreatePyCommand(30, countdown, self.MSG_COUNTDOWN)
        self.SetCountdown(self.MSG_COUNTDOWN)
        return

    def RefreshCountDown(self):
        if not g_FirstRegPhoneCode:
            self.ShowVoiceVerify()
        if hasattr(g_RegPhoneCodeTimer, 'm_Time') and g_RegPhoneCodeTimer.m_Time > 0:
            self.SetCountdown(g_RegPhoneCodeTimer.m_Time)
            return
        return

    def GetCountdownTime(self):
        if hasattr(g_RegPhoneCodeTimer, 'm_Time') and g_RegPhoneCodeTimer.m_Time:
            return g_RegPhoneCodeTimer.m_Time
        else:
            return 0
        return

    def ShowCommSuccDlg(self, mail):
        parent = self.GetParent()
        if parent:
            parent.ShowCommSuccDlg(mail)
        return

    def ShowPhoneSuccDlg(self, phone):
        parent = self.GetParent()
        if parent:
            parent.ShowPhoneSuccDlg(phone)
        return

    def SwitchRegMode(self, mode):
        self.m_RegMode = mode
        return

    def OnEditChange(self, ctrl):
        self.HideTips(self.PHONE_TIPS)
        attr = getattr(ctrl, 'm_ActiveIdx', None)
        if attr == 'email':
            self.HideTips(self.EMAIL_TIPS)
            mail = self.m_EmailEdit.GetText().strip()
            if mail:
                isShowPCode = self.ShouldShowPhoneCodeEidt(mail)
                isShowMail2 = self.ShouldShowMailEdit2(mail)
                self.ChangePhoneMode(isShowPCode)
                if isShowMail2:
                    self.m_PhoneAreaNumEdit.Enable(True)
                    self.m_PhoneAreaNumEdit.SetDownButtonShow(True)
                    self.m_PhoneAreaNumEdit.OnSelect(1)
                    self.m_PhoneEdit.Enable(True)
                    self.m_PwdEdit2.SetNextEdit(self.m_PhoneEdit)
                elif isShowPCode:
                    self.m_PhoneEdit.SetText(mail)
                    self.m_PhoneEdit.Enable(False)
                    self.m_PwdEdit2.SetNextEdit(self.m_PhoneCodeEdit)
                    self.m_PhoneAreaNumEdit.SetText('+86')
                    self.m_PhoneAreaNumEdit.SetDownButtonShow(False)
                    self.m_PhoneAreaNumEdit.Enable(False)
                elif not self.m_PhoneEdit.IsEnable():
                    self.m_PhoneEdit.SetText('')
                    self.m_PhoneEdit.Enable(True)
                    self.m_PhoneAreaNumEdit.SetText('')
                    self.m_PhoneAreaNumEdit.SetDownButtonShow(True)
                    self.m_PwdEdit2.SetNextEdit(self.m_PhoneEdit)
                if self.m_RegMode == self.PHONE_MODE:
                    return
                tipobj = self.m_TipsObjs.get(self.EMAIL_TIPS)
                if not tipobj:
                    self.ShowTips(self.EMAIL_TIPS, '請確保郵箱真實有效，用於註冊後的驗証', 'FRIEND')
            else:
                self.ShowTips(self.EMAIL_TIPS, '請確保郵箱真實有效，用於註冊後的驗証', 'FRIEND')
        elif attr == 'pwd':
            self.HideTips(self.PWD2_TIPS)
        elif attr == 'phone':
            mail = self.m_EmailEdit.GetText().strip()
            isShowMail2 = self.ShouldShowMailEdit2(mail)
            isShowPCode = self.ShouldShowPhoneCodeEidt(mail)
            if not isShowMail2 and not isShowPCode:
                self.ShowTips(self.PHONE_TIPS, '請先輸入正確格式的帳號')
                self.m_PhoneEdit.SetText('')
        return

    def ChangePhoneMode(self, bChange):
        if bChange:
            self.SwitchRegMode(self.PHONE_MODE)
        else:
            self.SwitchRegMode(self.COMMON_MODE)
        return

    def Hold(self):
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

    def CheckSpecialEmail(self):
        import checkemaildata
        email = self.GetEditContent(self.m_EmailEdit).strip()
        findFlag = False
        for emailUrl in checkemaildata.DATA:
            if emailUrl in email:
                findFlag = True
                break

        if findFlag and not getattr(self, 'm_PhraseFlag', False):
            self.m_PhraseFlag = True
            return True
        return False

    def EnQis`reCheck(self):
        import mxv
        mxv.ShowClientPhraseCheck(0)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.ReadTreaty()
        elif msgid == 2:
            if self.CheckSpecialEmail():
                self.EnQis`reCheck()
                return
            self.DoRegister()
        elif msgid == 5:
            self.GetPhoneCode()
        elif msgid == 6:
            self.GetPhoneVoice()
        return


class CCommonSuccDlg(combdialog.CCombDialog, pubdlgreg.CCommonSuccDlgBase):

    def __init__(self, parent, mail):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/reg_success_common.dlg')
        pubdlgreg.CCommonSuccDlgBase.__init__(self, mail, CReSendMgr)
        parent.ShowTurnBackBtn(True)
        self.m_Time = 0
        self.m_Timer = None
        self.ShowCountdown()
        return

    def ShowIDTips(self):
        import combmacro
        text = '%s 註冊成功！' % self.m_Mail
        self.m_IDTips = combmacro.CTEXT(interface.CTextObject, 'txt_ID', self, text, FontID18, 0)
        return

    def ShowDyTips(self, bShow):
        for i in range(1, 6):
            obj = self.GetObject('tips_dingyue%d' % i)
            if obj:
                obj.SetShow(bShow)

        return

    def ShowQtTips(self, bShow):
        for i in range(1, 6):
            obj = self.GetObject('tips_qita%d' % i)
            if obj:
                obj.SetShow(bShow)

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
        elif msgid == 2:
            self.ReSend()
        return


class CPhoneSuccDlg(combdialog.CCombDialog, pubdlgreg.CPhoneSuccDlgBase):

    def __init__(self, parent, phone):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/reg_success_2980.dlg')
        pubdlgreg.CPhoneSuccDlgBase.__init__(self, phone)
        parent.ShowTurnBackBtn(True)
        return

    def ShowIDTips(self):
        import combmacro
        text = '%s 註冊成功！' % self.m_Phone
        self.m_IDTips = combmacro.CTEXT(interface.CTextObject, 'txt_ID', self, text, FontID18, 0)
        return

    def ShowMail(self):
        import combmacro
        text = self.m_Phone + '@2980.com'
        self.m_EmailTips = combmacro.CTEXT(interface.CTextObject, 'txt_mail', self, text, FontID18, 0)
        return

    def Longin(self):
        CloseRegDlg()
        import loginin
        loginin.Show(True)
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.Longin()
        return


class CReg2980Dlg(combdialog.CCombDialog, pubdlgreg.CReg2980DlgBase):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/reg_2_2980email.dlg')
        pubdlgreg.CReg2980DlgBase.__init__(self, CReg2980Mgr)
        self.GetObject('btn_msg').SetShow(False)
        self.GetObject('btn_agree').SetSelect(False)
        self.RefreshCountDown()
        return

    def InitEdit(self):
        self.m_PwdEdit = combmacro.CEDIT(CPwdEdit, 'edit_pwd', self, 0, interface.FontST12, linecolor=0)
        self.m_PwdEdit.m_ActiveIdx = 'pwd'
        self.m_PwdEdit.m_TipsName = self.PWD_TIPS
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.SetTxtTip('6-16個字母或數字，區分大小寫')
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit.m_EditChange = True
        self.m_PwdEdit2 = combmacro.CEDIT(CPwdEdit, 'edit_pwd2', self, 0, interface.FontST12, linecolor=0)
        self.m_PwdEdit2.m_ActiveIdx = 'pwd2'
        self.m_PwdEdit2.m_TipsName = self.PWD2_TIPS
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.SetTxtTip('請再次輸入登錄密碼')
        self.m_PwdEdit2.m_IsPassword = True
        self.m_EmailEdit = combmacro.CEDIT(C2980MailEdit, 'edit_email', self, 0, interface.FontST12, linecolor=0)
        self.m_EmailEdit.m_ActiveIdx = 'email'
        self.m_EmailEdit.m_TipsName = self.EMAIL_TIPS
        self.m_EmailEdit.SetLimit(16)
        self.m_EmailEdit.SetTxtTip('6-16個字母或數字，必須含字母')
        self.m_PhoneEdit = combmacro.CEDIT(CPhoneEdit, 'edit_phone', self, 0, interface.FontST12, linecolor=0)
        self.m_PhoneEdit.m_ActiveIdx = 'phone'
        self.m_PhoneEdit.m_TipsName = self.PHONE_TIPS
        self.m_PhoneEdit.SetLimit(11)
        self.m_PhoneEdit.SetTxtTip('請輸入手機號')
        self.m_CodeEdit = combmacro.CEDIT(C2980CodeEdit, 'edit_code', self, 0, interface.FontST12, linecolor=0)
        self.m_CodeEdit.m_ActiveIdx = 'code'
        self.m_CodeEdit.m_TipsName = self.CODE_TIPS
        self.m_CodeEdit.SetMsgID(2)
        self.m_CodeEdit.SetLimit(9)
        self.m_CodeEdit.SetTxtTip('請輸入手機收到的驗証碼')
        self.m_IDCodeEdit = combmacro.CEDIT(CIDCodeEdit, 'edit_idcode', self, 0, interface.FontST12, linecolor=0)
        self.m_IDCodeEdit.m_ActiveIdx = 'idcode'
        self.m_IDCodeEdit.m_TipsName = 'tips_idcode'
        self.m_IDCodeEdit.SetLimit(18)
        self.m_IDCodeEdit.SetTxtTip('請輸入有效身份証號碼')
        self.m_NameEdit = combmacro.CEDIT(CNameEdit, 'edit_name', self, 0, interface.FontST12, linecolor=0)
        self.m_NameEdit.m_ActiveIdx = 'name'
        self.m_NameEdit.m_TipsName = 'tips_name'
        self.m_NameEdit.SetLimit(12)
        self.m_NameEdit.SetTxtTip('請輸入你的真實姓名')
        self.m_EmailEdit.Active(True)
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_PhoneEdit)
        self.m_PhoneEdit.SetNextEdit(self.m_CodeEdit)
        self.m_CodeEdit.SetNextEdit(self.m_IDCodeEdit)
        self.m_IDCodeEdit.SetNextEdit(self.m_NameEdit)
        self.CreateServiceBtn()
        self.m_TipsObjs = {}
        return

    def CreateServiceBtn(self):
        obj = self.GetObject('btn_treaty')
        (x, y) = obj.GetPos()
        obj.SetShow(False)
        iOffsetY = style.GetInt(self.GetDlgPath(), 'data_pos_offset_y')
        y += iOffsetY
        self.m_ServiceBtn = interface.CClickRichText(self, x, y, 150, '#u2980郵箱服務使用協議 ', 2645120, 2645120, interface.FontST12, msgid=1)
        return

    def ClickAgreeBtn(self):
        self.GetObject('btn_agree').LeftUp()
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def ShowTips(self, objname, tips, sType='WARN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
        color = GetColorByType(sType)
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
         self.m_PwdEdit, self.m_PwdEdit2, self.m_EmailEdit, self.m_PhoneEdit, self.m_CodeEdit]
        for chkedit in editlst:
            if edit != chkedit:
                chkedit.HideSpecialTips()

        return

    def GetEidtByTipsName(self, name):
        editlst = [
         self.m_PwdEdit, self.m_PwdEdit2, self.m_EmailEdit, self.m_PhoneEdit, self.m_CodeEdit]
        for edit in editlst:
            if hasattr(edit, 'm_TipsName') and edit.m_TipsName == name:
                return edit

        return

    def IsAgreeTreaty(self):
        return self.GetObject('btn_agree').IsSelected()

    def SetCountdown(self, t):
        btn = self.GetObject('btn_code')
        txt = self.GetObject('chg_code')
        if t > 0:
            txt.SetText('重試(%d)' % t)
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
        global g_Reg2980CodeTimer
        if not g_FirstReg2980Code:
            self.ShowVoiceVerify()
        if hasattr(g_Reg2980CodeTimer, 'm_Time') and g_Reg2980CodeTimer.m_Time > 0:
            self.SetCountdown(g_Reg2980CodeTimer.m_Time)
            return

        def countdown(obj, t):
            global g_FirstReg2980Code
            obj.m_Time = t
            dlg = GetReg2980Dlg()
            if dlg:
                dlg.SetCountdown(t)
            if t > 0:
                return (
                 t - 1,)
            else:
                g_FirstReg2980Code = False
            return

        if hasattr(g_Reg2980CodeTimer, 'm_CodeTimer') and g_Reg2980CodeTimer.m_CodeTimer:
            g_Reg2980CodeTimer.m_CodeTimer.Release()
        g_Reg2980CodeTimer = interface.CBaseObject(None)
        g_Reg2980CodeTimer.m_CodeTimer = g_Reg2980CodeTimer.CreatePyCommand(30, countdown, self.MSG_COUNTDOWN)
        self.SetCountdown(self.MSG_COUNTDOWN)
        return

    def RefreshCountDown(self):
        if not g_FirstReg2980Code:
            self.ShowVoiceVerify()
        if hasattr(g_Reg2980CodeTimer, 'm_Time') and g_Reg2980CodeTimer.m_Time > 0:
            self.SetCountdown(g_Reg2980CodeTimer.m_Time)
            return
        return

    def GetCountdownTime(self):
        if hasattr(g_Reg2980CodeTimer, 'm_Time') and g_Reg2980CodeTimer.m_Time:
            return g_Reg2980CodeTimer.m_Time
        else:
            return 0
        return

    def ShowSuccDlg(self, mail):
        parent = self.GetParent()
        if parent:
            parent.Show2980SuccDlg(mail)
        return

    def Hold(self):
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

    def OnEditChange(self, ctrl):
        if getattr(ctrl, 'm_ActiveIdx', None) == 'pwd':
            self.HideTips(self.PWD2_TIPS)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.ReadTreaty()
        elif msgid == 2:
            self.DoRegister()
        elif msgid == 3:
            self.GetPhoneVoice()
        elif msgid == 6:
            self.GetCode()
        elif msgid == 8:
            self.ClickCheckMail()
        return


class C2980SuccDlg(combdialog.CCombDialog, pubdlgreg.C2980SuccDlgBase):

    def __init__(self, parent, mail):
        combdialog.CCombDialog.__init__(self, parent, 'login/register/reg_success_2980.dlg')
        pubdlgreg.C2980SuccDlgBase.__init__(self, mail)
        parent.ShowTurnBackBtn(True)
        return

    def ShowIDTips(self):
        import combmacro
        text = '%s 註冊成功！' % self.m_Mail
        self.m_IDTips = combmacro.CTEXT(interface.CTextObject, 'txt_ID', self, text, FontID18, 0)
        return

    def Longin(self):
        CloseRegDlg()
        import loginin
        loginin.Show(True)
        return

    def Hold(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.Longin()
        return


class CReSendMgr(pubdlgreg.CReSendMgr):

    def GetGameGate(self):
        return 'mx'


class CReSendDlg(combdialog.CCombDialog, pubdlgreg.CReSendDlgBase):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'login/register/reg_4_repostmail.dlg')
        pubdlgreg.CReSendDlgBase.__init__(self, CReSendMgr)
        self.RefreshCountDown()
        interface.Center(self)
        self.Capture(1, 0)
        return

    def InitEdit(self):
        self.m_EmailEdit = combmacro.CEDIT(CCommMailEdit, 'edit_email', self, 0, interface.FontST12, linecolor=0)
        self.m_EmailEdit.m_TipsName = self.EMAIL_TIPS
        self.m_EmailEdit.SetLimit(32)
        self.m_EmailEdit.SetMsgID(1)
        self.m_EmailEdit.Active(True)
        self.m_TipsObjs = {}
        return

    def ShowTips(self, objname, tips, sType='WARIN'):
        obj = self.GetObject(objname)
        if not (obj and obj.GetShow()):
            return
        color = GetColorByType(sType)
        if self.m_TipsObjs.get(objname):
            self.m_TipsObjs[objname].SetText(tips)
            self.m_TipsObjs[objname].SetColor(color)
        else:
            self.m_TipsObjs[objname] = interface.CTextObject(self, tips, interface.FontLT12_1, color, 0)
            (x, y) = obj.GetPos()
            self.m_TipsObjs[objname].SetPos(x, y)
        return

    def HideTips(self, objname):
        if self.m_TipsObjs.get(objname):
            del self.m_TipsObjs[objname]
        return

    def GetEditContent(self, edit):
        if edit and edit.GetShow():
            return edit.GetText()
        return

    def SetCountdown(self, t):
        btn = self.GetObject('btn_send')
        txt = self.GetObject('chg_send')
        if t > 0:
            txt.SetText(str(t) + '秒後重試')
            btn.Enable(False)
        else:
            txt.SetText('發送')
            btn.Enable(True)
        (tx, ty) = txt.GetPos()
        (tw, _) = txt.GetSize()
        (bx, by) = btn.GetPos()
        (bw, _) = btn.GetSize()
        txt.SetPos(int(bx + (bw - tw) / 2), ty)
        return

    def ShowCountdown(self):
        global g_ReSendTimer
        if hasattr(g_ReSendTimer, 'm_Time') and g_ReSendTimer.m_Time > 0:
            self.SetCountdown(g_ReSendTimer.m_Time)
            return

        def countdown(obj, t):
            obj.m_Time = t
            dlg = GetReSendDlg()
            if dlg:
                dlg.SetCountdown(t)
            if t > 0:
                return (
                 t - 1,)
            return

        if hasattr(g_ReSendTimer, 'm_CodeTimer') and g_ReSendTimer.m_CodeTimer:
            g_ReSendTimer.m_CodeTimer.Release()
        g_ReSendTimer = interface.CBaseObject(None)
        g_ReSendTimer.m_CodeTimer = g_ReSendTimer.CreatePyCommand(30, countdown, self.COUNTDOWN)
        self.SetCountdown(self.COUNTDOWN)
        return

    def RefreshCountDown(self):
        if hasattr(g_ReSendTimer, 'm_Time') and g_ReSendTimer.m_Time > 0:
            self.SetCountdown(g_ReSendTimer.m_Time)
            return
        return

    def GetSize(self):
        bg = self.GetObject('bg')
        if bg:
            return bg.GetSize()
        return (0, 0)

    def TrunBack(self):
        self.CloseWindows()
        ShowRegisterDlg()
        return

    def CloseWindows(self):
        global g_ReSendDlg
        pubdlgreg.CReSendDlgBase.CloseWindows(self)
        g_ReSendDlg = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.ReSend()
        elif msgid == 2:
            self.TrunBack()
        elif msgid == 4:
            self.CloseWindows()
        return


class CQuickRegDlg(CRegCommonDlg):

    def __init__(self, parent, iSeq):
        CRegCommonDlg.__init__(self, parent)
        self.m_iSeq = iSeq
        if hasattr(self, 'm_EmailEdit'):
            self.m_EmailEdit.SetTxtTip('請輸入常用郵箱')
        return

    def RefreshCountDown(self):
        return

    def ShouldShowPhoneCodeEidt(self, mail):
        return False

    def DoRegister(self):
        import nethero, usermacro, C_sys, md5, localrecord
        tm = C_sys.GetTime()
        if hasattr(self, 'm_RegLastClick') and 0 <= tm - self.m_RegLastClick < 1:
            usermacro.PromptMsg('操作過於頻繁，請稍後再嘗試')
            return
        self.m_RegLastClick = tm
        result = self.DoCheck()
        if not result:
            return
        password = self.GetEditContent(self.m_PwdEdit)
        email = self.GetEditContent(self.m_EmailEdit).strip()
        password = md5.md5(password).hexdigest()
        password = localrecord.MD5Zip(password)
        nethero.C2SQuickRegister(self.m_iSeq, email, password)
        self.GetParent().CloseWindow()
        return

    def Hold(self):
        return


return
