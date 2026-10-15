# pycdc 交叉复核产物 · script.fls entry 1681
# co_filename(原始)='script/mxgame/myqnew/view/dlgmyqfilter.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1681.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: ${DATE} ${TIME}
\xd7\xf7\xd5\xdf: ${AuthorName}
\xce\xc4\xbc\xfe: ${NAME}
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import interface
import myqdefine
import myqinterface
import myqsignal
import usermacro

class CChangeFilterDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, iType, iStyle = None):
        if iStyle and iStyle == 4:
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/mengyouquan_new/myq_filter.dlg')
        else:
            combdialog.CCombDialog.__init__(self, oParent, 'dialog/mengyouquan_new/myq_filter.dlg')
        interface.Center(self)
        self.m_bSelFriend = False
        self.m_bSelGroup = False
        if iType == myqdefine.FILTER_FRIANDMEM:
            self.m_bSelFriend = True
            self.m_bSelGroup = True
        None(None, None, None)
        if iType == myqdefine.FILTER_FRIEND:
            self.m_bSelFriend = True
        elif iType == myqdefine.FILTER_MEMBER:
            self.m_bSelGroup = True
        
        self.RefreshBtnState()

    
    def ClickBtn(self, iMsgID):
        if iMsgID == 2:
            self.m_bSelFriend = not (self.m_bSelFriend)
        else:
            self.m_bSelGroup = not (self.m_bSelGroup)
        if not (self.m_bSelFriend) and not (self.m_bSelGroup):
            usermacro.PROMPT_MSG('\xa6\xdc\xa4\xd6\xbf\xef\xbe\xdc\xa4@\xad\xd3\xc5\xe3\xa5\xdc\xc3\xfe\xab\xac')
            if iMsgID == 2:
                self.m_bSelFriend = not (self.m_bSelFriend)
            else:
                self.m_bSelGroup = not (self.m_bSelGroup)
            self.RefreshBtnState()
            return None
        
        self.RefreshBtnState()
        self.DoChange()

    
    def RefreshBtnState(self):
        self.GetObject('btn_friend').SetSelect(self.m_bSelFriend)
        self.GetObject('btn_member').SetSelect(self.m_bSelGroup)

    
    def DoChange(self):
        iTarType = myqdefine.FILTER_FRIEND
        if self.m_bSelFriend and self.m_bSelGroup:
            iTarType = myqdefine.FILTER_FRIANDMEM
        elif self.m_bSelFriend and not (self.m_bSelGroup):
            iTarType = myqdefine.FILTER_FRIEND
        elif not (self.m_bSelFriend) and self.m_bSelGroup:
            iTarType = myqdefine.FILTER_MEMBER
        
        myqinterface.GetMYQContext().SetCurShowType(iTarType)
        myqsignal.Emit(myqsignal.SS_OnChangeFilter, iTarType)

    
    def CloseWindow(self):
        myqsignal.Emit(myqsignal.SS_OnCloseFilter)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID in (2, 3):
            self.ClickBtn(iMsgID)
