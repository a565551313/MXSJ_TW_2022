# pycdc 交叉复核产物 · script.fls entry 449
# co_filename(原始)='QAPKRV~OZECOG~CAVKTKty/countrycontest/arena/delegate/dgtctrycontest3v3matchhall.py'
# uncompyle6 状态=absent  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_449.pyc (Python 2.5)

import defines
import C_sys
import delegatebase
import netctrycontest
import mdctrycontest3v3arena
import time
import misc
import crtycontestdefine

class CCtryContest3v3MatchDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.m_iLastLookTime = 0
        self.m_tLookTeamID = None
        self.m_dFilterDict = {
            'iClass': 0,
            'sFind': '' }
        self.m_tRetList = []
        self.UpdateZuDuiBtnState()
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickFindMate, self.OnClickFindTeammate)
        oView.ssConnect(oView.SS_ClickSingleMatch, self.OnClickSingleMatch)
        oView.ssConnect(oView.SS_ClickTeamMatch, self.OnClickTeamMatch)
        oView.ssConnect(oView.SS_ClickSearch, self.OnClickSetFilter)
        oView.ssConnect(oView.SS_ClickNext, self.OnClickNextTeams)
        oView.ssConnect(oView.SS_ClickApply, self.OnClickApply)
        oView.ssConnect(oView.SS_LookTeam, self.OnLookTeam)
        oView.ssConnect(oView.SS_ClickZuDui, self.OnClickZuDui)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_InitTeamList, self.OnInitTeam)
        oModel.ssConnect(oModel.SS_UpdateMyTeam, self.OnUpdateMyTeam)
        oModel.ssConnect(oModel.SS_UpdateOneTeam, self.OnUpdateOneTeam)
        oModel.ssConnect(oModel.SS_UpdateTeamNum, self.OnUpdateTeamNum)
        oModel.ssConnect(oModel.SS_DelTeam, self.OnTeamDel)
        oModel.ssConnect(oModel.SS_TeamDetail, self.OnTeamDetail)
        oModel.ssConnect(oModel.SS_SetFindTeamState, self.OnSetFindTeam)
        self.OnInitTeam()
        self.OnInitPlayer()

    
    def GetModel(self):
        '''
\t\t:rtype: mdctrycontest3v3arena.CCtryContest3v3ArenaModel
\t\t'''
        return mdctrycontest3v3arena.GetArenaModel()

    
    def GetView(self):
        '''
\t\t:rtype: dlgctrycontest3v3matchhall.C3v3MatchHallDialog
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def OnUpdateMyTeam(self, dTeam):
        self.OnInitTeam()

    
    def OnUpdateOneTeam(self, tTeamID, dTeam):
        self.OnInitTeam()

    
    def UpdateZuDuiBtnState(self):
        iTime = misc.GetServerCurrentTime()
        tTime = time.localtime(iTime)
        iMonth = tTime[1]
        iDay = tTime[2]
        bShow = False
        if iMonth == crtycontestdefine.MOHTH_3v3_GL and iDay >= crtycontestdefine.DAY_3v3_GLMIN and iDay <= crtycontestdefine.DAY_3v3_GLMAX:
            bShow = True
        
        oView = self.GetView()
        oView.UpdateZuduiBtn(bShow)
        oModel = self.GetModel()
        iFindTeam = oModel.GetFindTeamState()
        oView.RefreshFindTeamBtn(iFindTeam)

    
    def OnTeamDel(self):
        netctrycontest.C2SAskOneTeam(self.GetModel().GetSeqID(), self.m_dFilterDict)
        self.OnInitTeam()

    
    def OnUpdateTeamNum(self, iTeamIdx):
        self.RefreshRetList()
        self.GetView().SetTeamList(self.m_tRetList, (iTeamIdx,))

    
    def OnTeamDetail(self, tTeamID, dDetailList):
        if tTeamID == self.m_tLookTeamID and dDetailList:
            sTips = '\xb6\xa4\xaa\xf8\xa1G%s %s' % self.TransInfo(dDetailList[0])
            for idx in range(1, len(dDetailList)):
                sTips += '#r\xb6\xa4\xad\xfb\xa1G%s %s' % self.TransInfo(dDetailList[idx])
            
            self.GetView().SetTipsStr(sTips)
        

    
    def OnInitTeam(self):
        self.RefreshRetList()
        self.GetView().SetTeamList(self.m_tRetList)

    
    def OnInitPlayer(self):
        dPlayerList = self.GetModel().GetPlayerList()
        self.GetView().SetPlayerList(dPlayerList)

    
    def OnLookTeam(self, tTeamID):
        if self.m_tLookTeamID == tTeamID:
            if C_sys.GetTime() - self.m_iLastLookTime < 3000:
                return None
            
        
        self.m_iLastLookTime = C_sys.GetTime()
        self.m_tLookTeamID = tTeamID
        netctrycontest.C2STeamDetail(tTeamID)

    
    def OnClickZuDui(self):
        netctrycontest.C2SOpen3V3TeamFight()

    
    def OnClickFindTeammate(self):
        oModel = self.GetModel()
        iFindTeamState = oModel.GetFindTeamState()
        iFindTeamState = None if iFindTeamState == 1 else 1
        netctrycontest.C2S3v3FindTeammate(iFindTeamState)

    
    def OnSetFindTeam(self):
        oModel = self.GetModel()
        iFindTeamState = oModel.GetFindTeamState()
        oView = self.GetView()
        oView.RefreshFindTeamBtn(iFindTeamState)

    
    def OnClickSingleMatch(self):
        netctrycontest.C2SSingleMatch()

    
    def OnClickTeamMatch(self):
        import dlgctrycontest1v1randommatch
        dlgctrycontest1v1randommatch.TopmostDlg()
        netctrycontest.C2STeamMatch()

    
    def OnClickSetFilter(self, bSelList, sFindStr):
        iNeedClass = 0
        for iIndex, bSel in enumerate(bSelList):
            if bSel:
                iNeedClass |= 1 << iIndex
                continue
        
        self.m_dFilterDict = {
            'iClass': iNeedClass,
            'sFind': sFindStr }
        netctrycontest.C2SFilterTeam(self.m_dFilterDict)

    
    def OnClickNextTeams(self):
        netctrycontest.C2SAskNextTeams(self.GetModel().GetSeqID(), self.m_dFilterDict)

    
    def OnClickApply(self, tTeamID):
        (None, None, None, None, None, netctrycontest)(tTeamID)

    
    def RefreshRetList(self):
        self.m_tRetList = []
        iNum = 1
        oModel = self.GetModel()
        dMyTeam = oModel.GetMyTeam()
        dTeamList = oModel.GetTeamList()
        if dMyTeam:
            self.m_tRetList.append((iNum, (dMyTeam['sName'], dMyTeam['tTeamID']), dMyTeam['iNum'], dMyTeam['tTeamID'], dMyTeam['iLeadClass']))
            iNum += 1
        
        for dTeam in dTeamList:
            self.m_tRetList.append((iNum, (dTeam['sName'], dTeam['tTeamID']), dTeam['iNum'], dTeam['tTeamID'], dTeam['iLeadClass']))
            iNum += 1
        

    
    def TransInfo(self, dInfo):
        return (dInfo['sName'], defines.CAREER_ID2NAME[dInfo['iClass']])
