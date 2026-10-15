# pycdc 交叉复核产物 · script.fls entry 183
# co_filename(原始)='script/mxgame/activity/ladderrankallstar/delegate/dgtseparategroup.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_183.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/2/6 16:51
\xd7\xf7\xd5\xdf: 
\xce\xc4\xbc\xfe: dgtseparategroup
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mdladderrankallstar
import ladderrankallstardefine
import misc

class CSeparateGroupDgt(delegatebase.CDelegateBase):
    
    def GetView(self):
        '''
\t\t:rtype: dlgseparategroup.CSeparateGroupDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return mdladderrankallstar.GetLadderRankAllStarModel()

    
    def Init(self):
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_RefreshAllRankInfo, self.RefreshSeparateGroupItem)
        self.RefreshSeparateGroupItem()

    
    def RefreshSeparateGroupItem(self):
        dAllRankInfo = misc.DeepCopy(self.GetModel().GetAllRankInfo())
        if not dAllRankInfo:
            return None
        
        
        try:
            dData = self(dAllRankInfo)
            self.GetView().RefreshSeparateGroupView(dData)
            return None


    
    def CalSeparateGroupMatchInfo(self, dAllRankInfo):
        dData = { }
        for iTenPos in xrange(1, 5):
            lSingleGroupInfo = []
            lWinTeamID = []
            for iEndPos in xrange(1, 6):
                iMatch = 100 + iTenPos * 10 + iEndPos
                dRankTypeInfo = dAllRankInfo.get(iMatch, { })
                if not dRankTypeInfo:
                    continue
                
                dAllRankInfoTemp = dRankTypeInfo['dAllRankInfo']
                iWinTeamID = dRankTypeInfo['iWinTeamID']
                iState = dRankTypeInfo['iState']
                if iEndPos in (1, 2):
                    for iIndex, dRankInfo in dAllRankInfoTemp.iteritems():
                        lSingleGroupInfo.append(dRankInfo)
                    
                
                if iEndPos in (3, 5) and iState == 2:
                    lWinTeamID.append(iWinTeamID)
                    continue
            
            for dSingleGroupInfo in lSingleGroupInfo:
                if dSingleGroupInfo['iTeamId'] in lWinTeamID:
                    dSingleGroupInfo['iWin'] = 1
                    continue
                dSingleGroupInfo['iWin'] = 0
            
            dData[iTenPos] = lSingleGroupInfo
        
        return dData
