# pycdc 交叉复核产物 · script.fls entry 3553
# co_filename(原始)='script/mxgame/group/dlgchangeintro.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3553.pyc (Python 2.5)

import combdialog
import interface
import combmacro
import usermacro
g_GroupChangeIntroDlg = None

def ModuleReset():
    global g_GroupChangeIntroDlg
    g_GroupChangeIntroDlg = None


def SetShow(bShow, iGroupId = None):
    global g_GroupChangeIntroDlg, g_GroupChangeIntroDlg
    if bShow:
        if not g_GroupChangeIntroDlg:
            g_GroupChangeIntroDlg = CInputMsgBox(iGroupId)
        
        g_GroupChangeIntroDlg.SetShow(True)
    else:
        g_GroupChangeIntroDlg = None


class CInputMsgBox(combdialog.CCombDialog):
    
    def __init__(self, iGroupId):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group/newgroup/inputmsgbox.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_Edit = None
        self.m_GroupID = iGroupId
        self.CreateEdit()
        self.AfterOpenDialog()

    
    def CreateEdit(self):
        self.m_Edit = combmacro.CMLEDIT(interface.CMultilineEdit, 'edt_input', self, interface.COLOR_4, interface.FontLT14_3, 0, interface.COLOR_4)
        self.m_Edit.SetLimit(100)
        self.m_Edit.SetLineLimit(4)
        self.m_Edit.Active(True)

    
    def CloseWindow(self):
        SetShow(False)

    
    def OnSendIntro(self):
        import banword
        import netgroup
        sMsg = self.m_Edit.GetText().replace(',', '\xa1A')
        if banword.IsValidOnIntrodruce(sMsg):
            None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, netgroup.C2SChangeGroupNotice, self.m_GroupID, sMsg)
            self.CloseWindow()
        else:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xbf\xe9\xa4J\xa4\xa4\xa5]\xa7t\xb1\xd3\xb7P\xa6r\xb2\xc5')

    
    def OnMessage(self, iMsgid):
        if iMsgid == 1:
            self.OnSendIntro()
        elif iMsgid == 2:
            self.CloseWindow()
