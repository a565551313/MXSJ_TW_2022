# pycdc 交叉复核产物 · script.fls entry 3210
# co_filename(原始)='script/dialog/dlgjingdongcard.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3210.pyc (Python 2.5)

import combdialog
import interface
import combmacro
import usermacro
import wrapinterface
import commondialog
import misc

def Show(iItemID):
    if not CJingDongCardDialog.GetUI():
        CJingDongCardDialog.OpenUI(iItemID)
    else:
        CJingDongCardDialog.GetUI().SetShow(True)


class CJingDongCardDialog(combdialog.CCombDialog):
    sUIName = 'dialog/nationfight/newnationfight/playerinfo.dlg'
    
    def __init__(self, oParent, iID):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel)
        interface.Center(self)
        self.m_oNameEdit = None
        self.m_oPhoneEdit = None
        self.m_iItemID = iID
        self.InitDlg()

    
    def InitDlg(self):
        self.m_oNameEdit = combmacro.CEDIT(interface.CEdit, 'frame_bg1', self, interface.COLOR_3, interface.FontLT14_3, interface.COLOR_1)
        self.m_oNameEdit.SetDefaultTips('\xa6\xac\xa5\xf3\xa4H\xa6W\xa6r', interface.FontLT14_3, interface.COLOR_3)
        self.m_oNameEdit.SetAutoClearDefaultTips(True)
        self.m_oPhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'frame_bg2', self, interface.COLOR_3, interface.FontLT14_3, interface.COLOR_1)
        self.m_oPhoneEdit.SetDefaultTips('\xa5\xbb\xa4H\xa4\xe2\xbe\xf7\xb8\xb9', interface.FontLT14_3, interface.COLOR_3)
        self.m_oPhoneEdit.SetAutoClearDefaultTips(True)
        self.m_oMailEdit = combmacro.CMLEDIT(interface.CMultilineEdit, 'frame_bg3', self, interface.COLOR_1, interface.FontLT14_3, 0, interface.COLOR_3)
        self.m_oMailEdit.SetDefaultTips('\xa6\xac\xa5\xf3\xa4H\xb6l\xbdc', interface.FontLT14_3, interface.COLOR_1)
        self.m_oMailEdit.SetAutoClearDefaultTips(True)
        self.m_oNameEdit.SetNextEdit(self.m_oPhoneEdit)
        self.m_oPhoneEdit.SetNextEdit(self.m_oMailEdit)
        self.m_oMailEdit.SetNextEdit(self.m_oNameEdit)

    
    def Publish(self):
        sName = self.m_oNameEdit.GetText()
        sPhone = self.m_oPhoneEdit.GetText()
        sMail = self.m_oMailEdit.GetText()
        if not sName:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa6W\xba\xd9')
            return None
        
        if not sPhone:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa4\xe2\xbe\xf7\xb8\xb9\xbdX')
            return None
        
        if len(sPhone) != 11:
            usermacro.PROMPT_MSG('\xb1z\xbf\xe9\xa4J\xaa\xba\xa4\xe2\xbe\xf7\xb8\xb9\xbdX\xa6\xb3\xbb~\xa1A\xbd\xd0\xad\xab\xb7s\xbf\xe9\xa4J')
            return None
        
        if not sMail:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xb6l\xbdc\xabH\xae\xa7')
            return None
        
        if not self.CheckEmail(sMail):
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb6l\xbdc')
            return None
        
        commondialog.ShowMessageBox('\xabH\xae\xa7\xb6\xf1\xbcg\xb6\xc8\xa6\xb3\xa4@\xa6\xb8\xbe\xf7\xb7|\xa1A\xbd\xd0\xbdT\xbb{\xacO\xa7_\xb2\xc5\xa6X\xa1H ', ('\xacO', '\xa7_'), misc.Functor(self.OnConfirmPublisth, sName, sPhone, sMail))

    
    def OnConfirmPublisth(self, sName, sPhone, sMail, oObj):
        import netctrycontest
        LOG_DEBUG('\xb4\xa3\xa5\xe6', sName, sPhone)
        netctrycontest.C2SJingDongInfoDetail(self.m_iItemID, sName, sPhone, sMail)
        self.CloseWindow()

    
    def CloseWindow(self):
        if self.m_oNameEdit:
            pass
        self.m_oNameEdit.Active(False)
        if self.m_oPhoneEdit:
            pass
        self.m_oPhoneEdit.Active(False)
        if self.m_oMailEdit:
            pass
        self.m_oMailEdit.Active(False)
        self.CloseUI()

    
    def CheckEmail(self, sEmail):
        import re
        if len(sEmail) < 5 or len(sEmail) > 50:
            return False
        
        sPattStr = '^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$'
        oPatt = re.compile(sPattStr)
        oMat = oPatt.match(sEmail)
        if oMat is None:
            return False
        
        return True

    
    def OnMessage(self, \xa9\x8dsgID):
        if \xa9\x8dsgID == 1:
            self.CloseWindow()
        elif \xa9\x8dsgID == 6:
            self.Publish()
