# pycdc 交叉复核产物 · script.fls entry 3995
# co_filename(原始)='script/mxgame/serverbattle/view/dlgteaminvitefrd.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3995.pyc (Python 2.5)

import interface
import combdialog
import usermacro
import netserverbattleteam
g_TeamInvite = None

def ModuleReset():
    global g_TeamInvite
    g_TeamInvite = None


def Show(FrdLst):
    global g_TeamInvite
    g_TeamInvite = CTeamInviteDlg()
    FrdLst.sort(key = (lambda v: v['iState']), reverse = True)
    g_TeamInvite.RefreshList(FrdLst)


def CloseWindows():
    if g_TeamInvite and g_TeamInvite.GetShow():
        g_TeamInvite.CloseWindow()
    


class CTeamInviteDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/serverbattle/team/invitefriend.dlg')
        interface.Center(self)
        self.iCurSelectedIdx = -1

    
    def RefreshList(self, lstFrd):
        self.m_ItemList = []
        self.m_FrdTable = self.GetObject('tab_friends')
        self.m_FrdTable.Clear()
        for playerData in lstFrd:
            iLv = playerData['iLv']
            iState = playerData['iState']
            sState = playerData['sName'] if iState == 1 else '\xc2\xf7\xbdu'
            iColor = None if iState == 1 else 8421504
            it = self.m_FrdTable.AddTextItem((sName, str(iLv), sState), iColor)
            it.m_Data = playerData
            self.m_ItemList.append(it)
        
        self.m_FrdTable.m_SelectNotify = True
        self.m_FrdTable.ResetItems()
        self.m_FrdTable.ResetScrollBar()

    
    def CloseWindow(self):
        global g_TeamInvite
        g_TeamInvite = None

    
    def OnCommitClick(self):
        if self.iCurSelectedIdx == -1:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xb1z\xb7Q\xc1\xdc\xbd\xd0\xaa\xba\xaa\xb1\xaea')
            return None
        
        oList = self.GetObject('tab_friends')
        oItem = oList.m_Items[self.iCurSelectedIdx]
        oData = oItem.m_Data
        netserverbattleteam.C2SInviteFrd(oData['iID'])
        CloseWindows()

    
    def OnMessage(self, msgid):
        if msgid in (2, 4):
            self.CloseWindow()
        elif msgid == 3:
            self.OnCommitClick()
        elif msgid in range(25, 500):
            idx = msgid - 25
            self.iCurSelectedIdx = idx
