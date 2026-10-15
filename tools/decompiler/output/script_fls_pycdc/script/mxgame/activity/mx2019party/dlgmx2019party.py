# pycdc 交叉复核产物 · script.fls entry 3212
# co_filename(原始)='script/mxgame/activity/mx2019party/dlgmx2019party.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3212.pyc (Python 2.5)

import interface
import wrapinterface
import combdialog
import commondialog
import combmacro
import misc
import usermacro
import mxitemdata
import item
g_SignUpDlg = None

def ModuleReset():
    global g_SignUpDlg
    g_SignUpDlg = None


def ShowSignUpDlg():
    global g_SignUpDlg
    g_SignUpDlg = CSignUpDlg()
    return g_SignUpDlg


class CSignUpDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/carnival/informationfill.dlg')
        interface.Center(self)
        self.m_oNameEdit = None
        self.m_oIDEdit = None
        self.m_oPhoneEdit = None
        self.m_oAddressEdit = None
        self.m_iItemID = 0
        self.InitDlg()

    
    def InitDlg(self):
        self.m_oNameEdit = combmacro.CEDIT(interface.CEdit, 'loc_name', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oNameEdit.Active(True)
        self.m_oIDEdit = combmacro.CEDIT(CIDEdit, 'loc_id', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oPhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'loc_phone', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oAddressEdit = combmacro.CEDIT(interface.CEdit, 'loc_dress', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oNameEdit.SetNextEdit(self.m_oIDEdit)
        self.m_oIDEdit.SetNextEdit(self.m_oPhoneEdit)
        self.m_oPhoneEdit.SetNextEdit(self.m_oAddressEdit)
        self.m_oAddressEdit.SetNextEdit(self.m_oNameEdit)

    
    def SetItemNameByShape(self, iItemID):
        self.m_iItemID = iItemID
        if iItemID:
            self.GetObject('text_reward').LzkText(mxitemdata.DATA.get(item.GetItem(iItemID).GetShape()))
        

    
    def Publish(self):
        sName = self.m_oNameEdit.GetText()
        sID = self.m_oIDEdit.GetText()
        sPhone = self.m_oPhoneEdit.GetText()
        sAddress = self.m_oAddressEdit.GetText()
        if not sName:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa6W\xba\xd9')
            return None
        
        if not sID:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa8\xad\xa5\xf7\xb5\xfd')
            return None
        
        if not sPhone:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa4\xe2\xbe\xf7\xb8\xb9\xbdX')
            return None
        
        if not sAddress:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa6a\xa7}\xabH\xae\xa7')
            return None
        
        commondialog.ShowMessageBox('\xabH\xae\xa7\xb6\xf1\xbcg\xb6\xc8\xa6\xb3\xa4@\xa6\xb8\xbe\xf7\xb7|\xa1A\xbd\xd0\xbdT\xbb{\xacO\xa7_\xb2\xc5\xa6X\xa1H ', ('\xacO', '\xa7_'), (misc.Functor(self.OnConfirmPublisth, sName, sID, sPhone, sAddress), None))

    
    def OnConfirmPublisth(self, sName, sID, sPhone, sAddress, obj):
        LOG_DEBUG('\xb4\xa3\xa5\xe6', sName, sID, sPhone, sAddress)
        import netmx2019party
        netmx2019party.C2SPublishMsg(sName, sID, sPhone, self.m_iItemID, sAddress)
        self.CloseWindow()

    
    def CloseWindow(self):
        global g_SignUpDlg
        if self.m_oNameEdit:
            pass
        self.m_oNameEdit.Active(False)
        if self.m_oIDEdit:
            pass
        self.m_oIDEdit.Active(False)
        if self.m_oPhoneEdit:
            pass
        self.m_oPhoneEdit.Active(False)
        g_SignUpDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.Publish()
        



class CIDEdit(interface.CEdit):
    
    def AddChar(self, char):
        if not char.isdigit() and char not in ('x', 'X'):
            usermacro.PROMPT_MSG('\xa8\xad\xa5\xf7\xb5\xfd\xa5u\xa4\xb9\xb3\\\xbf\xe9\xa4J\xbc\xc6\xa6r\xa1Bx\xbbPX\xa1A\xbd\xd0\xab\xf6\xadn\xa8D\xbf\xe9\xa4J')
            return None
        
        interface.CEdit.AddChar(self, char)
