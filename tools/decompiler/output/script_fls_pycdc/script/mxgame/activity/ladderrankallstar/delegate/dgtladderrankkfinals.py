# pycdc 交叉复核产物 · script.fls entry 2084
# co_filename(原始)='script/mxgame/activity/ladderrankallstar/delegate/dgtladderrankkfinals.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2084.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/1/26 19:38
\xd7\xf7\xd5\xdf: \xd0\xa1\xbb\xd2\xbb\xd2
\xce\xc4\xbc\xfe: dgtladderrankknockoutmatch
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mdladderrankallstar
import ladderrankallstardefine
import misc

class CLadderRankFinalsDgt(delegatebase.CDelegateBase):
    
    def GetView(self):
        '''
\t\t:rtype: dlgladderrankfinals.CLadderRankFinalsDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return mdladderrankallstar.GetLadderRankAllStarModel()

    
    def Init(self):
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_RefreshAllRankInfo, self.RefreshMatchInfo)
        self.RefreshMatchInfo()

    
    def RefreshMatchInfo(self):
        dAllRankInfo = misc.DeepCopy(self.GetModel().GetAllRankInfo())
        if not dAllRankInfo:
            return None
        
        dData = self.CalFinalsMatchInfo(dAllRankInfo)
        dLineInfoList = self.CalLineInfo(dData, dAllRankInfo)
        self.GetView().RefreshRankFinalsView(dData)
        self.GetView().OnRefreshLine(dLineInfoList)

    
    def CalFinalsMatchInfo(self, dAllRankInfo):
        dData = { }
        for iMatchType in ladderrankallstardefine.TYPE_EIGHT_MATCH_LIST:
            dRankInfo = dAllRankInfo.get(iMatchType, { })
            if dRankInfo:
                dData[iMatchType] = dRankInfo
                continue
        
        for iMatchType in ladderrankallstardefine.FINALS_RELEVANCE_LIST:
            tType = ladderrankallstardefine.FINALS_RELEVANCE_DICT[iMatchType]
            dRankInfoTemp = { }
            dRankInfoTemp['iState'] = 0
            dRankInfoTemp['iWinTeamID'] = 0
            dRankInfoTemp['dAllRankInfo'] = { }
            for iPos, iMatch in enumerate(tType):
                dRankInfo = dData.get(iMatch, { })
                if not dRankInfo:
                    continue
                
                iState = dRankInfo['iState']
                iWinTeamID = dRankInfo['iWinTeamID']
                if iState == 2:
                    for iIndex, dInfo in dRankInfo['dAllRankInfo'].iteritems():
                        if iMatchType == ladderrankallstardefine.MATCH_TYPE_FOURTH:
                            if iWinTeamID != dInfo['iTeamId']:
                                dRankInfoTemp['dAllRankInfo'][iPos + 1] = dInfo
                            elif iWinTeamID == dInfo['iTeamId']:
                                if iWinTeamID == 999:
                                    dRankInfoTemp['dAllRankInfo'][iPos + 1] = dInfo
                                
                            
                        iWinTeamID != dInfo['iTeamId']
                        (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, iWinTeamID == dInfo['iTeamId'])
                        dRankInfoTemp['dAllRankInfo'][iPos + 1] = dInfo
                    
            
            if iMatchType in dAllRankInfo:
                dRankInfo = dAllRankInfo[iMatchType]
                dRankInfoTemp['iState'] = dRankInfo['iState']
                dRankInfoTemp['iWinTeamID'] = dRankInfo['iWinTeamID']
            
            if iMatchType == ladderrankallstardefine.MATCH_TYPE_FIFTH_1:
                dData[ladderrankallstardefine.MATCH_TYPE_FIFTH_0] = dRankInfoTemp
                continue
            dData[iMatchType] = dRankInfoTemp
        
        dData = self.CalChampionData(dData, dAllRankInfo)
        return dData

    
    def CalChampionData(self, dData, dRankFinalsInfo):
        dRankTypeInfo = dData[ladderrankallstardefine.MATCH_TYPE_FOURTH]
        dAllRankInfo = dRankTypeInfo['dAllRankInfo']
        iWinTeamID = dRankTypeInfo['iWinTeamID']
        for iIndex, dRankInfo in dAllRankInfo.iteritems():
            if iWinTeamID == dRankInfo['iTeamId']:
                dData[ladderrankallstardefine.TYPE_LOSEWIN_MATCH] = dRankInfo
                continue
        
        dWinDataTemp = self.GetBo3MatchData(dRankFinalsInfo)
        for iWinTeamID, iWinNum in dWinDataTemp.iteritems():
            if iWinNum == 2:
                dAllRankInfoTemp = dData[ladderrankallstardefine.MATCH_TYPE_FIFTH_0]['dAllRankInfo']
                for dRankTypeInfoTemp in dAllRankInfoTemp.itervalues():
                    iTeamID = dRankTypeInfoTemp['iTeamId']
                    if iWinTeamID == iTeamID:
                        dData[ladderrankallstardefine.TYPE_WWIN_MATCH] = dRankTypeInfoTemp
                        continue
                
                [
                    iWinTeamID][ladderrankallstardefine.MATCH_TYPE_FIFTH_0]['iWinTeamID'] = None
                dData[ladderrankallstardefine.MATCH_TYPE_FIFTH_0]['bHaveWin'] = True
                continue
        
        return dData

    
    def GetBo3MatchData(self, dRankFinalsInfo):
        dWinDataTemp = { }
        for iMatchType in ladderrankallstardefine.FINALS_BO3_TEAM_LIST:
            if iMatchType in dRankFinalsInfo:
                dRankTypeInfo = dRankFinalsInfo[iMatchType]
                iWinTeamID = dRankTypeInfo['iWinTeamID']
                iState = dRankTypeInfo['iState']
                if iState != ladderrankallstardefine.MATCH_TYPE_END:
                    continue
                
                if iWinTeamID in dWinDataTemp:
                    dWinDataTemp[iWinTeamID] = dWinDataTemp[iWinTeamID] + 1
                else:
                    dWinDataTemp[iWinTeamID] = 1
            iWinTeamID in dWinDataTemp
        
        return dWinDataTemp

    
    def CalLineInfo(self, dRankFinalsInfo, dAllRankInfo):
        dLineInfo = { }
        bBo3Over = False
        dWinDataTemp = self.GetBo3MatchData(dAllRankInfo)
        for iWinTeamID, iWinNum in dWinDataTemp.iteritems():
            if iWinNum == 2:
                bBo3Over = True
                continue
        
        for iMatchType, dRankInfo in dRankFinalsInfo.iteritems():
            if iMatchType in ladderrankallstardefine.LOC_RANK_LINE_NAME:
                if iMatchType == ladderrankallstardefine.MATCH_TYPE_FIFTH_0:
                    if not bBo3Over:
                        continue
                    
                
                dGroupWinInfo = { }
                iState = dRankInfo['iState']
                dGroupWinInfo['iState'] = iState
                dAllRankInfo = dRankInfo['dAllRankInfo']
                iWinTeamID = dRankInfo['iWinTeamID']
                for iIndex, dRankInfo in dAllRankInfo.iteritems():
                    if iWinTeamID == dRankInfo['iTeamId']:
                        dGroupWinInfo['iWinTeam'] = iIndex - 1
                        continue
                
                dLineInfo[iMatchType] = dGroupWinInfo
                continue
        
        return dLineInfo
