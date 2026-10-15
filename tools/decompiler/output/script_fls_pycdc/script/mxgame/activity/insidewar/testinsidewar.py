# pycdc 交叉复核产物 · script.fls entry 693
# co_filename(原始)='script/mxgame/activity/insidewar/testinsidewar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_693.pyc (Python 2.5)

import mdinsidewarmain
import dlginsidewarmain
import mdinsidejob
import dlginsidewarrank
import mdinsidewarrank
g_CInsideWarTest = None

def GetServerBattleTest():
    global g_CInsideWarTest
    if not g_CInsideWarTest:
        g_CInsideWarTest = CServerBattleTest()
    
    return g_CInsideWarTest


class CServerBattleTest(object):
    
    def FirstFunc(self):
        pass

    
    def OpenWarMian(self):
        '''
\t\t\xa5\xb4\xb6}\xb3]\xb8m\xa5D\xad\xb1\xaaO
import testinsidewar as t
t.GetServerBattleTest().OpenWarMian()
\t\t:return:
\t\t'''
        dlginsidewarmain.Show('FWU}\xa4F\xb3]\xb8m\xa5D\xad\xb1\xaaO')

    
    def TestWarMain(self, bState):
        '''
\t\t\xb3]\xb8m\xa4F\xc2\xbe\xb7~\xabH\xae\xa7
import testinsidewar as t
t.GetServerBattleTest().TestWarMain(True)

import testinsidewar as t
t.GetServerBattleTest().TestWarMain(False)
\t\t:return:
\t\t'''
        mdinsidewarmain.GetMainSetModel().SetIsSetClass(bState)

    
    def ShowJobSetting(self):
        '''
\t\t\xa5\xb4\xb6}\xc2\xbe\xb7~\xabH\xae\xa7\xad\xb1\xaaO
import testinsidewar as t
t.GetServerBattleTest().ShowJobSetting()
\t\t'''
        import dlginsidewarjob
        dlginsidewarjob.ShowSettingBGDlg()
        self.SetJobSetting()
        self.TestWarMain(True)

    
    def SetJobSetting(self):
        '''
\t\t\xb3]\xb8m\xa4F\xc2\xbe\xb7~\xabH\xae\xa7
import testinsidewar as t
t.GetServerBattleTest().SetJobSetting()
\t\t:return:
\t\t'''
        iFirst = 0
        dictRoleProp = { }
        iReset = 0
        if iFirst == 1:
            pass
        
        mdinsidejob.GetCountryPlayerSettingModel().OpenRolePropSettingDlg(dictRoleProp, iFirst, iReset)

    
    def S2CTeamRank(self):
        '''
\t\t\xb1\xc6\xa6\xe6\xba]\xb0O\xbf\xfd
import testinsidewar as t
t.GetServerBattleTest().S2CTeamRank()
\t\t:return:
\t\t'''
        iRecordLen = 100
        iType = 1
        dicRecords = { }
        for idx in range(iRecordLen):
            dicRecord = { }
            iTeamID = idx
            dicRecord['iTeamID'] = iTeamID
            iRank = idx
            dicRecord['iRank'] = None
            sTeamName = 'xxx%s' % idx
            dicRecord['sTeamName'] = sTeamName
            sServerName = 'NB'
            dicRecord['sServerName'] = sServerName
            sCaptainName = 'Me%s' % idx
            dicRecord['sCaptainName'] = sCaptainName
            iScore = idx * 100
            dicRecord['iScore'] = iScore
            iPowerScore = idx + 100
            dicRecord['iPowerScore'] = iPowerScore
            iTeamMatesLen = 6
            lstName = []
            for iTeamMate in range(iTeamMatesLen):
                sTeamMateName = '\xbd\xde\xb6\xa4\xa4\xcd'
                lstName.append(sTeamMateName)
            
            dicRecord['lstMate'] = lstName
            dicRecords[idx] = dicRecord
        
        dlginsidewarrank.ShowServerRank()
        mdinsidewarrank.GetServerBattleModel().UpdateRankInfo(dicRecords)
