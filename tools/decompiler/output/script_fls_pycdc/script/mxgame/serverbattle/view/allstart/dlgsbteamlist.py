# pycdc 交叉复核产物 · script.fls entry 2789
# co_filename(原始)='script/mxgame/serverbattle/view/allstart/dlgsbteamlist.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2789.pyc (Python 2.5)

'''
\xcc\xec\xd1\xa1\xc8\xab\xc3\xf7\xd0\xc7\xa3\xac\xb6\xd3\xce\xe9\xd0\xc5\xcf\xa2\xc1\xd0\xb1\xed
'''
import interface
import combdialog
g_TeamListDlg = None

def ModuleReset():
    global g_TeamListDlg
    g_TeamListDlg = None


def ShowTeamListDlg(dTeamInfoList):
    global g_TeamListDlg
    g_TeamListDlg = CTeamListDlg()
    g_TeamListDlg.RefreshTeamList(dTeamInfoList)


class CTeamListDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/serverbattle/allstar/team_list.dlg')
        interface.Center(self)

    
    def RefreshTeamList(self, dTeamInfoList):
        import serverdata
        oTable = self.GetObject('tab_team')
        oTable.Clear()
        for dTeamInfo in self.SortTeamList(dTeamInfoList):
            if dTeamInfo.get('bIsMyTeam'):
                iInsertIdx = 0
            else:
                iInsertIdx = None
            iRank = dTeamInfo.get('iRank', -1)
            if iRank == -1 or iRank > 30:
                sRank = '-'
            else:
                sRank = str(iRank)
            sTeamName = dTeamInfo.get('sTeamName', '\xa5\xbc\xaa\xbe\xb6\xa4\xa5\xee')
            iServerID = dTeamInfo.get('iServerID', 0)
            sServerName = serverdata.GetServerNameByID(iServerID)
            iZBSAverageScore = dTeamInfo.get('iZBSAverageScore', 0)
            iTeamAverageScore = dTeamInfo.get('iTeamAverageScore', 0)
            oItem = oTable.AddTextItem([
                sRank,
                sTeamName,
                sServerName,
                str(iZBSAverageScore),
                str(iTeamAverageScore)], hot = 1, iInsertIdx = iInsertIdx)
            oItem.m_iTeamID = dTeamInfo.get('iTeamID', 0)
            oItem.m_iServerID = iServerID
        
        oTable.ResetItems()
        oTable.ResetScrollBar()

    
    def OnHotEnter(self, oIt):
        LOG_DEBUG('\xbd\xd0\xa8D\xb6\xa4\xa5\xeeTips', oIt.m_iTeamID, oIt.m_iServerID)
        if not oIt.m_iServerID and oIt.m_iTeamID:
            return None
        
        import dlgsbasroll
        import netserverbattleteam
        dlgsbasroll.SetShowTeamTipsInfo(oIt.m_iTeamID, oIt.m_iServerID)
        netserverbattleteam.C2SGetBattleTeamTips(oIt.m_iTeamID, oIt.m_iServerID)

    
    def OnHotLeave(self, oIt):
        LOG_DEBUG('\xc1\xf4\xc2\xc3\xb6\xa4\xa5\xeeTips')
        import dlgsbasroll
        dlgsbasroll.HideTeamInfoTips()

    
    def OnHotLeftUp(self, oIt):
        LOG_DEBUG('\xbd\xd0\xa8D\xb6\xa4\xa5\xee\xabH\xae\xa7', oIt.m_iTeamID, oIt.m_iServerID)
        if not oIt.m_iServerID and oIt.m_iTeamID:
            return None
        
        import netserverbattleteam
        netserverbattleteam.C2SRequestTeamInfo(oIt.m_iTeamID, oIt.m_iServerID)

    
    def SortTeamList(self, dTeamInfoList):
        dTeamInfoList.sort(key = (lambda d: d['iRank']))
        return dTeamInfoList

    
    def CloseWindow(self):
        global g_TeamListDlg
        g_TeamListDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.CloseWindow)
