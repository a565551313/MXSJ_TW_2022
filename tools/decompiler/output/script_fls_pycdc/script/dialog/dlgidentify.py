# pycdc 交叉复核产物 · script.fls entry 1243
# co_filename(原始)='script/dialog/dlgidentify.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1243.pyc (Python 2.5)

import time
import interface
import combdialog
import misc
import usermacro
g_oIdentifyMgr = None

def AskOpenUI():
    import identitycert
    identitycert.C2SGetIdentity()


def OpenFailDlg():
    CRenzhengFailDlg.OpenUI()


def OpenRenzhengDlg():
    CRenzhengDlg.OpenUI()


def OpenDlgByState(iState):
    import identitycert
    if iState == identitycert.IDENTITY_VERIFIED:
        OpenRenzhengDlg()
    elif iState == identitycert.IDENTITY_VERIFICATION_FAIL:
        OpenFailDlg()
    


def CloseAllRenzhengDlg():
    CRenzhengFailDlg.CloseUI()
    CRenzhengDlg.CloseUI()


def GetIdentifyMgr():
    global g_oIdentifyMgr
    if not g_oIdentifyMgr:
        g_oIdentifyMgr = CIdentifyMgr()
    
    return g_oIdentifyMgr


def OpenRenzhengTips(sName, sID, iOverTime):
    CRenzhengTips.OpenUI(sName, sID, iOverTime)


def Show(bShow):
    if bShow:
        import netserver
        if len(netserver.g_LoginServer) == 2 and netserver.g_LoginServer[1] == '\xa5~\xba\xf4\xb4\xfa\xb8\xd5\xaaA':
            import identitycert
            identitycert.AutoCommitData('name=\xa7\xf5\xa7\xbb\xa4\xa6||idcard=220101197505181463')
        else:
            CIdentifyDlg.OpenUI()
            oDlg = CIdentifyDlg.GetUI()
            oDlg.Topmost()
            import commondialog
            commondialog.HideMessageBox()
    else:
        CIdentifyDlg.CloseUI()


class CIDEdit(interface.CEdit):
    
    def AddChar(self, char):
        if not char.isdigit() and char not in ('x', 'X'):
            usermacro.PROMPT_MSG('\xa8\xad\xa5\xf7\xb5\xfd\xa5u\xa4\xb9\xb3\\\xbf\xe9\xa4J\xbc\xc6\xa6r\xa1Bx\xbbPX\xa1A\xbd\xd0\xab\xf6\xadn\xa8D\xbf\xe9\xa4J')
            return None
        
        interface.CEdit.AddChar(self, char)



class CIdentifyDlg(combdialog.CCombDialog):
    sUIName = 'dialog/realname.dlg'
    dOpenUIConfig = {
        'KEY_PARENT': 'CapturePanel' }
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.SafeCapture(True)
        interface.Center(self)
        self.m_oTimer = None
        self.InitObject()
        self.RefreshCD()

    
    def CanClose(self):
        import hero
        return not bool(hero.GetHeroID())

    
    def InitObject(self):
        import combmacro
        self.m_IDEdit = combmacro.CEDIT(CIDEdit, 'edit_id', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_IDEdit.Active(True)
        self.m_IDEdit.SetLimit(18)
        self.m_NameEdit = combmacro.CEDIT(interface.CEdit, 'edit_name', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_NameEdit.SetLimit(12)

    
    def SendMessage(self):
        sID = self.m_IDEdit.GetText()
        sName = self.m_NameEdit.GetText()
        import identitycert
        identitycert.CommitData(sName, sID)

    
    def RefreshCD(self):
        import timer
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        
        self.m_oTimer = timer.Timer(1, self.RefreshConfirmText, -1, self)
        self.RefreshConfirmText()

    
    def RefreshConfirmText(self):
        iCD = GetIdentifyMgr().GetCDTimeStamp()
        if iCD > 0:
            sText = '\xbdT\xbb{(%d\xac\xed)' % iCD
        else:
            sText = '\xbdT \xbb{'
            if self.m_oTimer:
                self.m_oTimer.Release()
                self.m_oTimer = None
            
        self.GetObject('btn_confirm').SetText(sText)

    
    def CloseWindow(self):
        if self.CanClose():
            self.CloseUI()
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.SendMessage()
        elif msgid == 2:
            self.CloseWindow()
        



class CRenzhengFailDlg(combdialog.CCombDialog):
    sUIName = 'dialog/shiming/renzheng.dlg'
    dOpenUIConfig = {
        'KEY_PARENT': 'CapturePanel' }
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.SafeCapture(True)
        self.Topmost()
        if not self.CanClose():
            self.SetShowObject('m_CloseBtn', False)
        
        self.m_oNameEdit = None
        self.m_oIDEdit = None
        self.m_oTimer = None
        self.InitEdit()
        self.RefreshCD()

    
    def CanClose(self):
        return False

    
    def InitEdit(self):
        import combmacro
        self.m_oIDEdit = combmacro.CEDIT(CIDEdit, 'loc_id', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_oIDEdit.SetLimit(18)
        self.m_oNameEdit = combmacro.CEDIT(interface.CEdit, 'loc_name', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_oNameEdit.SetLimit(12)
        self.m_oNameEdit.Active(True)

    
    def SendMessage(self):
        import identitycert
        sID = self.m_oIDEdit.GetText()
        sName = self.m_oNameEdit.GetText()
        identitycert.CommitData(sName, sID)

    
    def RefreshCD(self):
        import timer
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        
        self.m_oTimer = timer.Timer(1, self.RefreshConfirmText, -1, self)
        self.RefreshConfirmText()

    
    def RefreshConfirmText(self):
        iCD = GetIdentifyMgr().GetCDTimeStamp()
        if iCD > 0:
            sText = '\xbdT\xbb{(%d\xac\xed)' % iCD
        else:
            sText = '\xbdT\xbb{'
            if self.m_oTimer:
                self.m_oTimer.Release()
                self.m_oTimer = None
            
        self.GetObject('btn_confirm').SetText(sText)

    
    def OpenService(self):
        import dlgservice
        dlgservice.OpenServiceWithCapture()

    
    def CloseWindow(self):
        if self.CanClose():
            self.CloseUI()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.CloseWindow()
        elif iMsgID == 3:
            self.SendMessage()
        elif iMsgID == 4:
            self.OpenService()
        



class CRenzhengDlg(combdialog.CCombDialog):
    sUIName = 'dialog/shiming/renzheng2.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.m_oNameEdit = None
        self.m_oIDEdit = None
        self.m_oTimer = None
        self.InitEdit()
        RefreshCD = self
        None()

    
    def InitEdit(self):
        import combmacro
        self.m_oIDEdit = combmacro.CEDIT(CIDEdit, 'loc_id', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_oIDEdit.SetLimit(18)
        self.m_oNameEdit = combmacro.CEDIT(interface.CEdit, 'loc_name', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_oNameEdit.SetLimit(12)
        self.m_oNameEdit.Active(True)

    
    def SendMessage(self):
        import identitycert
        sID = self.m_oIDEdit.GetText()
        sName = self.m_oNameEdit.GetText()
        identitycert.CommitData(sName, sID)

    
    def RefreshCD(self):
        import timer
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        
        self.m_oTimer = timer.Timer(1, self.RefreshConfirmText, -1, self)
        self.RefreshConfirmText()

    
    def RefreshConfirmText(self):
        iCD = GetIdentifyMgr().GetCDTimeStamp()
        if iCD > 0:
            sText = '\xbdT\xbb{(%d\xac\xed)' % iCD
        else:
            sText = '\xbdT\xbb{'
            if self.m_oTimer:
                self.m_oTimer.Release()
                self.m_oTimer = None
            
        self.GetObject('btn_confirm').SetText(sText)

    
    def OpenService(self):
        import dlgservice
        dlgservice.ShowSwitch()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.CloseUI()
        elif iMsgID == 3:
            self.SendMessage()
        elif iMsgID == 4:
            self.OpenService()
        



class CRenzhengTips(combdialog.CCombDialog):
    sUIName = 'dialog/shiming/tishi.dlg'
    
    def __init__(self, oParent, sName, sID, iOverTime):
        combdialog.CCombDialog.__init__(self, oParent)
        self.InitIdentifyData(sName, sID, iOverTime)

    
    def InitIdentifyData(self, sName, sID, iOverTime):
        import time
        import netlogin
        sAccount = netlogin.GetCurrAccount()
        if sAccount.isdigit():
            sAccount = '%s*****%s' % (sAccount[:3], sAccount[-3:])
        else:
            iAt = sAccount.rfind('@')
            sFront = sAccount[:1]
            if iAt == -1:
                sEnd = sAccount[-1:]
            elif iAt <= 1:
                sFront = ''
                sEnd = sAccount[iAt:]
            elif iAt == 2:
                sEnd = sAccount[iAt:]
            else:
                sEnd = sAccount[iAt - 1:]
            sAccount = '%s*%s' % (sFront, sEnd)
        self.GetObject('text_tishi1').ReplaceText({
            '$account': sAccount })
        self.GetObject('text_name1').SetText(sName)
        self.GetObject('text_shenfenzheng1').SetText(sID)
        sTime = time.strftime('%Y-%m-%d %H:%M:%S', misc.LocalTime(iOverTime))
        self.GetObject('text_tishi2').ReplaceText({
            '$time': sTime })

    
    def OnMessage(self, iMsgID):
        if iMsgID in (2, 3):
            self.CloseUI()
        elif iMsgID == 4:
            self.CloseUI()
            OpenRenzhengDlg()
        



class CIdentifyMgr(object):
    INTERVAL_TIME = 60
    INTERVAL_NUM = 2
    
    def __init__(self):
        self.m_iSendCount = 0
        self.m_iTimeStamp = 0

    
    def CanSendMessage(self):
        if self.m_iTimeStamp == 0:
            self.AddCount()
            return True
        else:
            iInterval = int(time.time()) - self.m_iTimeStamp
            if iInterval < self.INTERVAL_TIME:
                usermacro.PROMPT_MSG('\xbd\xd0%d\xac\xed\xab\xe1\xad\xab\xb8\xd5' % (self.INTERVAL_TIME - iInterval))
                return False
            else:
                self.AddCount()
                return True

    
    def AddCount(self):
        self.m_iSendCount += 1
        if self.m_iSendCount == self.INTERVAL_NUM:
            self.m_iSendCount = 0
            self.m_iTimeStamp = int(time.time())
            self.RefreshCD()
        else:
            self.m_iTimeStamp = 0

    
    def RefreshCD(self):
        oDlg = CIdentifyDlg.GetUI()
        if oDlg:
            oDlg.RefreshCD()
        
        oDlg = CRenzhengDlg.GetUI()
        if oDlg:
            oDlg.RefreshCD()
        
        oDlg = CRenzhengFailDlg.GetUI()
        if oDlg:
            oDlg.RefreshCD()
        

    
    def GetCDTimeStamp(self):
        iInterval = int(time.time()) - self.m_iTimeStamp
        if iInterval < self.INTERVAL_TIME:
            return self.INTERVAL_TIME - iInterval
        
        return -1
