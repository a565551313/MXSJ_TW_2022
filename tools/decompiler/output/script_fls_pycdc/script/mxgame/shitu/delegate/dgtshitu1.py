# pycdc 交叉复核产物 · script.fls entry 4475
# co_filename(原始)='script/mxgame/shitu/delegate/dgtshitu1.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4475.pyc (Python 2.5)

import delegatebase
import mdshitu1
import netshitu1
import shitudefine
import permission

class CFindMasterDelegate(delegatebase.CDelegateBase):
    EACH_PAGE_NUM = 10
    ACTIVE_2_TXT = {
        0: '\xa5\xfe\xa4\xd1',
        1: '\xa5\xd5\xa4\xd1',
        2: '\xb1\xdf\xa4W' }
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_iCurPage = 0
        self.m_dMasterInfoList = []
        self.m_dMasterExDict = { }

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_SetFindMasterCondition, self.OnSetFindMasterCondition)
        oView.ssConnect(oView.SS_AutoFindMaster, self.OnAutoFindMaster)
        oView.ssConnect(oView.SS_NextPage, self.OnNextPage)
        oView.ssConnect(oView.SS_PerPage, self.OnPerPage)
        oView.ssConnect(oView.SS_BaiShi, self.OnBaiShi)
        oView.ssConnect(oView.SS_LookPlayer, self.OnLookPlayer)
        oModel = mdshitu1.GetFindMasterModel()
        oModel.ssConnect(oModel.SS_MastetInfoListChange, self.OnMasterInfoListChange)
        oModel.ssConnect(oModel.SS_MasterNumChange, self.OnMasterNumChange)
        oModel.ssConnect(oModel.SS_SetMasterHasRequest, self.OnSetMasterHasRequest)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnMasterExInfoDictChange)

    
    def OnSetFindMasterCondition(self):
        LOG_DEBUG('\xb3]\xb8m\xb4M\xaev\xb7N\xa6V')
        netshitu1.C2SOpenFindMasterSetting()

    
    def OnAutoFindMaster(self):
        LOG_DEBUG('\xa4@\xc1\xe4\xb4M\xaev')
        netshitu1.C2SAutoSetMaster()

    
    def OnNextPage(self):
        LOG_DEBUG('\xa4U\xa4@\xad\xb6')
        import usermacro
        iStart = (self.m_iCurPage + 1) * self.EACH_PAGE_NUM
        iEnd = (self.m_iCurPage + 2) * self.EACH_PAGE_NUM
        if self.m_dMasterInfoList[iStart:iEnd]:
            self.m_iCurPage += 1
            self.GetView().RefreshList(self.m_dMasterInfoList[iStart:iEnd])
            self.GetView().RefreshListExInfo(self.m_dMasterExDict)
        else:
            usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xa4U\xa4@\xad\xb6\xa4F')

    
    def OnPerPage(self):
        LOG_DEBUG('\xa4W\xa4@\xad\xb6')
        import usermacro
        if self.m_iCurPage > 0:
            iStart = (self.m_iCurPage - 1) * self.EACH_PAGE_NUM
            iEnd = self.m_iCurPage * self.EACH_PAGE_NUM
            self.m_iCurPage -= 1
            self.GetView().RefreshList(self.m_dMasterInfoList[iStart:iEnd])
            self.GetView().RefreshListExInfo(self.m_dMasterExDict)
        else:
            usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xa4W\xa4@\xad\xb6\xa4F')

    
    def OnBaiShi(self, iPlayerID):
        LOG_DEBUG('\xab\xf4\xaev', iPlayerID)
        import usermacro
        for dMasterInfo in self.m_dMasterInfoList:
            if dMasterInfo[shitudefine.KEY_PLAYER_ID] == iPlayerID and dMasterInfo[shitudefine.KEY_HAS_REQUEST]:
                usermacro.PROMPT_MSG('\xa7A\xa4w\xb8g\xa5\xd3\xbd\xd0\xb9L\xa4F')
                return None
                continue
        
        netshitu1.C2SSetMaster(iPlayerID)

    
    def OnLookPlayer(self, iPlayerID):
        import dlgfriend
        dlgfriend.FindPlayerWithID(iPlayerID, 1)

    
    def OnMasterInfoListChange(self, dMasterInfoList):
        oView = self.GetView()
        if not oView:
            return None
        
        self.m_iCurPage = 0
        self.m_dMasterInfoList = self.ProcressMasterInfo(dMasterInfoList)
        oView.SetShowPageBtn(len(dMasterInfoList) > self.EACH_PAGE_NUM)
        oView.RefreshList(self.m_dMasterInfoList[:self.EACH_PAGE_NUM])

    
    def OnMasterExInfoDictChange(self, dMasterExInfoDict):
        oView = self.GetView()
        self.m_dMasterExDict = dMasterExInfoDict
        oView.RefreshListExInfo(dMasterExInfoDict)

    
    def OnMasterNumChange(self, iRelateTchNum, iNormalTchNum, iRelateTchMax, iTotalTchMax):
        oView = self.GetView()
        if not oView:
            return None
        
        oView.SetNearTxt('%d/%d' % (iRelateTchNum, iRelateTchMax))
        oView.SetNormalTxt('%d/%d' % (iNormalTchNum, iTotalTchMax - iRelateTchNum))

    
    def OnSetMasterHasRequest(self, iMasterID):
        for dMasterInfo in self.m_dMasterInfoList:
            if dMasterInfo[shitudefine.KEY_PLAYER_ID] == iMasterID:
                dMasterInfo[shitudefine.KEY_HAS_REQUEST] = True
                continue
        
        self.GetView().RefreshHasRequest(iMasterID)

    
    def ProcressMasterInfo(self, dMasterInfoList):
        dResultList = []
        for dMasterInfo in dMasterInfoList:
            dInfo = { }
            dInfo[shitudefine.KEY_DESC] = '%s\xa5X\xaev/%s\xa4\xc0' % (dMasterInfo[shitudefine.KEY_CHUSHI_NUM], float(dMasterInfo[shitudefine.KEY_MASTER_SCORE]) / 10)
            dInfo[shitudefine.KEY_ACTIVE_TYPE] = self.ACTIVE_2_TXT[dMasterInfo[shitudefine.KEY_ACTIVE_TYPE]]
            dInfo[shitudefine.KEY_SAME_GROUP] = dMasterInfo[shitudefine.KEY_SAME_GROUP]
            dInfo[shitudefine.KEY_PLAYER_ID] = dMasterInfo[shitudefine.KEY_PLAYER_ID]
            dInfo[shitudefine.KEY_HAS_REQUEST] = dMasterInfo[shitudefine.KEY_HAS_REQUEST]
            dInfo[shitudefine.KEY_SORT_SCARE] = dMasterInfo[shitudefine.KEY_SORT_SCARE]
            dInfo[shitudefine.KEY_PLAYER_ONLINE] = dMasterInfo[shitudefine.KEY_PLAYER_ONLINE]
            dResultList.append(dInfo)
        
        dResultList.sort(key = self.GetSortKey, reverse = True)
        dResultList2 = []
        iOffline = 0
        for dInfo in dResultList:
            if not dInfo[shitudefine.KEY_PLAYER_ONLINE]:
                iOffline += 1
                if iOffline > 50:
                    continue
                
            
            dResultList2.append(dInfo)
        
        return dResultList2

    
    def GetSortKey(self, dInfo):
        return (dInfo[shitudefine.KEY_SORT_SCARE], dInfo[shitudefine.KEY_PLAYER_ONLINE], dInfo[shitudefine.KEY_SAME_GROUP])



class CFindMasterIntentionDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_SetIntention, self.OnSetIntention)
        oModel = mdshitu1.GetFindMasterSettingModel()
        oModel.ssConnect(oModel.SS_ConfigChange, self.OnConfigChange)

    
    def OnConfigChange(self, iOnlineType, iSchoolType, iSexType):
        self.GetView().RefreshIntention(iOnlineType, iSchoolType, iSexType)

    
    def OnSetIntention(self, dInfo):
        LOG_DEBUG('\xb3]\xb8m\xb4M\xaev\xb7N\xa6V', dInfo)
        netshitu1.C2SFindMasterSetting(dInfo[shitudefine.KEY_ACTIVE_TYPE], dInfo[shitudefine.KEY_PLAYER_CLASS], dInfo[shitudefine.KEY_PLAYER_SEX])
        oView = self.GetView()
        oView.CloseWindow()



class CRequestFileDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_iPlayerID = None

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_Agree, self.OnAgree)
        oView.ssConnect(oView.SS_Object, self.OnObject)
        oView.ssConnect(oView.SS_TempChat, self.OnTempChat)
        oModel = mdshitu1.GetRequestFileModel()
        oModel.ssConnect(oModel.SS_PlayerInfoChange, self.OnPlayerInfoChange)

    
    def OnPlayerInfoChange(self, iPlayerID, sGroup, iHuoyue, iGold, iVip):
        oView = self.GetView()
        if not oView:
            return None
        
        self.m_iPlayerID = iPlayerID
        oModel = mdshitu1.GetPlayerExInfoModel()
        dExInfo = oModel.GetPlayerExInfo(iPlayerID)
        if not dExInfo:
            return None
        
        oView.SetName(dExInfo[shitudefine.KEY_PLAYER_NAME])
        oView.SetGroup(sGroup)
        oView.SetLv(dExInfo[shitudefine.KEY_PLAYER_LV])
        oView.SetImpress(iHuoyue, iGold, iVip)
        oView.ShowIcon(dExInfo[shitudefine.KEY_PLAYER_AVATAR], self.m_iPlayerID)

    
    def OnAgree(self):
        LOG_DEBUG('\xa6P\xb7N')
        if not self.m_iPlayerID:
            return None
        
        netshitu1.C2SAgreeRecruit(self.m_iPlayerID, 1)
        mdshitu1.RemoveHasReadRequest(self.m_iPlayerID)
        self.GetView().CloseWindow()

    
    def OnObject(self):
        LOG_DEBUG('\xa9\xda\xb5\xb4')
        if not self.m_iPlayerID:
            return None
        
        netshitu1.C2SAgreeRecruit(self.m_iPlayerID, 0)
        mdshitu1.RemoveHasReadRequest(self.m_iPlayerID)
        self.GetView().CloseWindow()

    
    def OnTempChat(self):
        LOG_DEBUG('\xc1{\xae\xc9\xb7|\xb8\xdc', self.m_iPlayerID)
        import friend
        import dlgtalk
        import netfriend
        if friend.IsFriend(self.m_iPlayerID):
            dlgtalk.ShowTalkDialog(self.m_iPlayerID, friend.GetShowName(self.m_iPlayerID), 0)
        else:
            netfriend.C2SAddTemp(self.m_iPlayerID)
            friend.GetControl().AddOpenTalkDlgPlayerID(self.m_iPlayerID)
        self.GetView().CloseWindow()



class CMasterAssessDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_iPoint = 0
        self.m_iPlayerID = 0
        self.m_oTimer = None
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_Assess, self.OnAssess)
        oView.ssConnect(oView.SS_SelectPoint, self.OnSelectPoint)
        oView.ssConnect(oView.SS_CloseWindow, self.OnCloseWindow)
        oModel = mdshitu1.GetMasterAssessModel()
        oModel.ssConnect(oModel.SS_PlayerInfoChange, self.OnPlayerInfoChange)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnPlayerExInfoDictChange)
        self.InitTimer()

    
    def InitTimer(self):
        import timer
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = timer.Timer(120, self.DoCloseWindow)

    
    def OnAssess(self):
        LOG_DEBUG('\xb5\xfb\xbb\xf9', self.m_iPlayerID, self.m_iPoint * 2)
        self.Assess(self.m_iPoint * 2)
        self.GetView().DoCloseWindow()

    
    def OnSelectPoint(self, iPoint):
        LOG_DEBUG('\xb5\xfb\xc2I', iPoint)
        iPoint2Assess = {
            2: '2\xa4\xc0\xa1A\xaev\xb3\xc5\xabD\xb1`\xaet',
            4: '4\xa4\xc0\xa1A\xaev\xb3\xc5\xa4\xf1\xb8\xfb\xaet',
            6: '6\xa4\xc0\xa1A\xaev\xb3\xc5\xa4@\xaf\xeb',
            8: '8\xa4\xc0\xa1A\xaev\xb3\xc5\xabD\xb1`\xa6n',
            10: '10\xa4\xc0\xa1A\xaev\xb3\xc5\xb9\xef\xa7\xda\xc0\xb0\xa7U\xab\xdc\xa4j' }
        self.m_iPoint = iPoint
        oView = self.GetView()
        oView.SetStart(iPoint)
        oView.SetAssess(iPoint2Assess[iPoint * 2])

    
    def OnCloseWindow(self):
        self.Assess(8)

    
    def OnPlayerInfoChange(self, iPlayerID):
        self.m_iPlayerID = iPlayerID

    
    def OnPlayerExInfoDictChange(self, dExInfo):
        oView = self.GetView()
        dPlayerInfo = mdshitu1.GetPlayerExInfoModel().GetPlayerExInfo(self.m_iPlayerID)
        oView.SetName(dPlayerInfo[shitudefine.KEY_PLAYER_NAME])
        oView.SetIcon(dPlayerInfo[shitudefine.KEY_PLAYER_AVATAR], self.m_iPlayerID)

    
    def Assess(self, iPoint):
        LOG_DEBUG('\xaev\xa4\xf7\xb5\xfb\xbb\xf9', iPoint)
        netshitu1.C2SSetMasterAssess(self.m_iPlayerID, iPoint)

    
    def DoCloseWindow(self):
        self.GetView().CloseWindow()



class CApplyTudiDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_dBuffer = { }
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oModel = mdshitu1.GetShoutuModel()
        oModel.ssConnect(oModel.SS_TudiIDListChange, self.OnTudiIDListChange)
        oModel.ssConnect(oModel.SS_ExInfoChange, self.OnExInfoChange)
        oModel.ssConnect(oModel.SS_ImproveEnd, self.OnImproveEnd)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnTudiExInfoChange)
        oModel = mdshitu1.GetFriendListModel()
        oModel.ssConnect(oModel.SS_RequestTuDiNumChange, self.OnRequestTuDiNumChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_LookPlayerInfo, self.LookPlayerInfo)
        oView.ssConnect(oView.SS_ImproveRank, self.OnImproveRank)
        oView.ssConnect(oView.SS_ShowShoutuStatusDlg, self.OnShowShoutuStatusDlg)
        oView.ssConnect(oView.SS_ShowChushiInfo, self.OnShowChushiInfo)

    
    def OnTudiIDListChange(self, iPlayerIDList):
        self.RefreshList()

    
    def OnExInfoChange(self, iAcceptFlag, iStuNum, iStuMax, iRewardNum, iImproveLeftTime):
        oView = self.GetView()
        oView.SetShoutuStatus(iAcceptFlag)
        oView.SetShoutuNum(iStuNum, iStuMax)
        oView.ShowChushiGiftNumImg(iRewardNum)
        self.RefreshTips()

    
    def OnImproveEnd(self):
        self.RefreshTips()

    
    def OnTudiExInfoChange(self, dPlayerInfoDict):
        self.RefreshList()

    
    def OnRequestTuDiNumChange(self, iNum):
        if iNum > 0:
            import netshitu1
            netshitu1.C2SOpenFindTudiDlg()
        

    
    def LookPlayerInfo(self, iPlayerID):
        LOG_DEBUG('\xacd\xac\xdd\xaa\xb1\xaea\xa5\xd3\xbd\xd0\xc0\xc9\xae\xd7', iPlayerID)
        netshitu1.C2SOpenRequestFileDlg(iPlayerID)

    
    def OnImproveRank(self):
        LOG_DEBUG('\xb4\xa3\xa4\xc9\xb1\xc6\xa6W')
        import usermacro
        import pubtimeformat
        iLeftTime = mdshitu1.GetShoutuModel().GetImproveLeftTime()
        if iLeftTime > 0:
            sTime = pubtimeformat.PubLeftTimeDayMin(iLeftTime)
            usermacro.PROMPT_MSG('\xa7A\xb2{\xa6b\xa4w\xb8g\xb3B\xa9\xf3\xb4\xa3\xabe\xb1\xc6\xa6W\xaa\xba\xaa\xac\xbaA\xa1A\xab\xf9\xc4\xf2\xae\xc9\xb6\xa1\xc1\xd9\xa6\xb3#Y%s' % sTime)
            return None
        
        netshitu1.C2SImproveRank()

    
    def OnShowShoutuStatusDlg(self):
        LOG_DEBUG('\xa5\xb4\xb6}\xa6\xac\xae{\xb3]\xb8m\xac\xc9\xad\xb1')
        netshitu1.C2SOpenRecruitSetting()

    
    def OnShowChushiInfo(self):
        LOG_DEBUG('\xa5\xb4\xb6}\xa5X\xaev\xae{\xa7\xcc\xabH\xae\xa7\xac\xc9\xad\xb1')
        netshitu1.C2SOpenChushiTudiListDlg()

    
    def ProcessPlayerInfoList(self):
        dResult = []
        import hero
        for iPlayerID in mdshitu1.GetShoutuModel().GetTudiIDList():
            dPlayerInfo = mdshitu1.GetPlayerExInfoModel().GetPlayerExInfo(iPlayerID)
            if not dPlayerInfo:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_PLAYER_ID] = iPlayerID
            dInfo[shitudefine.KEY_PLAYER_NAME] = dPlayerInfo[shitudefine.KEY_PLAYER_NAME]
            dInfo[shitudefine.KEY_PLAYER_LV] = dPlayerInfo[shitudefine.KEY_PLAYER_LV]
            dInfo[shitudefine.KEY_PLAYER_CLASS] = hero.id2class(dPlayerInfo[shitudefine.KEY_PLAYER_CLASS])
            dInfo[shitudefine.KEY_PLAYER_AVATAR] = dPlayerInfo[shitudefine.KEY_PLAYER_AVATAR]
            dInfo[shitudefine.KEY_PLAYER_ONLINE] = dPlayerInfo[shitudefine.KEY_PLAYER_ONLINE]
            dResult.append(dInfo)
        
        dResult.sort(key = SortPlayerList)
        return dResult

    
    def RefreshList(self):
        import copy
        dInfoList = self.ProcessPlayerInfoList()
        if self.m_dBuffer == dInfoList:
            return None
        
        self.GetView().SetApplyList(dInfoList)
        self.m_dBuffer = copy.deepcopy(dInfoList)
        self.RefreshTips()

    
    def RefreshTips(self):
        oView = self.GetView()
        oModel = mdshitu1.GetShoutuModel()
        bHasRequest = bool(len(oModel.GetTudiIDList()))
        iImproveLeftTime = oModel.GetImproveLeftTime()
        bAccept = oModel.IsAccept()
        LOG_DEBUG('\xacO\xa7_\xa6\xb3\xa5\xd3\xbd\xd0\xa6C\xaa\xed', bHasRequest, oModel.GetTudiIDList(), bAccept, iImproveLeftTime)
        if bHasRequest:
            oView.HideEmptyAndSetTips()
            if iImproveLeftTime > 0:
                oView.ShowImproveTips()
            elif bAccept:
                oView.ShowFindTips()
            else:
                oView.HideFindAndImproveTips()
        elif iImproveLeftTime > 0:
            if bAccept:
                oView.ShowImproveMTips()
                oView.HideFindAndImproveTips()
            else:
                oView.ShowSetTips()
                oView.ShowImproveTips()
        elif bAccept:
            oView.ShowEmptyTips()
            oView.ShowFindTips()
        else:
            oView.ShowSetTips()
            oView.HideFindAndImproveTips()



class CShoutuSettingDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_iCurTudiNum = 0
        self.m_iRecruitTudi30 = 0
        self.m_iHuoye7 = 0
        self.m_bHasGroup = False
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oModel = mdshitu1.GetShoutuSettingModel()
        oModel.ssConnect(oModel.SS_ConfigChange, self.OnConfigChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_SetShoutuStatus, self.SetShoutuStatus)

    
    def OnConfigChange(self, iAcceptFlag, iCurTudiNum, iRecruitTudi30, iHuoYe7, iStatus, iActive):
        oView = self.GetView()
        bAcceptFlag = bool(iAcceptFlag)
        oView.SetAgreeBtnSelect(bAcceptFlag)
        oView.SetActiveBtnSelect(iActive)
        bShoutuMonthEnable = IsShoutuMonthEnable(iStatus)
        bHuoyueEnable = IsHuoyueEnable(iStatus)
        bGroupEnable = IsHasGroup(iStatus)
        bShoutuNumEnable = IsShoutuNum(iStatus)
        self.m_iCurTudiNum = iCurTudiNum
        self.m_iRecruitTudi30 = iRecruitTudi30
        self.m_iHuoye7 = iHuoYe7
        self.m_bHasGroup = bGroupEnable
        if bAcceptFlag:
            sStatus = '\xa9\xdb\xa6\xac\xa4\xa4'
        else:
            sStatus = '\xb0\xb1\xa4\xee\xa4\xa4'
        oView.SetStatusTxt(sStatus)
        oView.SetCurStatusTips(iCurTudiNum, iRecruitTudi30, iHuoYe7)
        oView.SetStatusImg(bShoutuNumEnable, bShoutuMonthEnable, bHuoyueEnable, bGroupEnable)

    
    def SetShoutuStatus(self, iAgree, iActive):
        LOG_DEBUG('\xb3]\xb8m\xacO\xa7_\xc4@\xb7N\xa6\xac\xae{', iAgree, iActive)
        import usermacro
        (bCan, sTips) = self.CheckIsCanShoutu()
        if bCan:
            netshitu1.C2SRecruitSetting(iAgree, iActive)
            self.GetView().CloseWindow()
        else:
            usermacro.PROMPT_MSG(sTips)

    
    def CheckIsCanShoutu(self):
        sTxtList = []
        bCurTudiNumFlag = bRecruitTudi30Flag = bHuoye7Flag = bGroupFlag = True
        if self.m_iCurTudiNum >= 5:
            sTxtList.append('\xa4\xa3\xba\xa1\xa8\xac\xb7\xed\xabe\xa5X\xaev\xae{\xa7\xcc\xbc\xc6\xb6q<5')
            bCurTudiNumFlag = False
        
        if self.m_iRecruitTudi30 >= 5:
            sTxtList.append('\xa4\xa3\xba\xa1\xa8\xac\xb3\xcc\xaa\xf1\xa4@\xad\xd3\xa4\xeb\xa4\xba\xa9\xdb\xa6\xac\xaa\xba\xae{\xa7\xcc\xbc\xc6\xa5\xd8<5')
            bRecruitTudi30Flag = False
        
        if self.m_iHuoye7 < 1000:
            sTxtList.append('\xa4\xa3\xba\xa1\xa8\xac\xb3\xcc\xaa\xf17\xa4\xd1\xa4\xba\xb2\xd6\xadp\xac\xa1\xc5D\xab\xd7\xa1\xd91000')
            bHuoye7Flag = False
        
        if not self.m_bHasGroup:
            sTxtList.append('\xbb\xdd\xadn\xa5[\xa4J\xc0\xb0\xac\xa3\xa4~\xaf\xe0\xa9\xdb\xa6\xac\xae{\xa7\xcc')
            bGroupFlag = False
        
        if bCurTudiNumFlag and bRecruitTudi30Flag and bHuoye7Flag:
            pass
        return (bGroupFlag, '#r'.join(sTxtList))



class CRelationshipDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_dMemberInfoList = []

    
    def Init(self):
        oModel = mdshitu1.GetRelationshipModel()
        oModel.ssConnect(oModel.SS_MemberListChange, self.OnMemberListChange)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnPlayerExInfoDictChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_Dismiss, self.OnDismiss)
        oView.ssConnect(oView.SS_SetNear, self.OnSetNear)
        oView.ssConnect(oView.SS_LookPlayerInfo, self.OnLookPlayerInfo)

    
    def OnMemberListChange(self, dTudiInfoList, dMasterInfoList):
        import copy
        dList1 = copy.deepcopy(dTudiInfoList)
        dList2 = copy.deepcopy(dMasterInfoList)
        self.m_dMemberInfoList = dList1 + dList2
        self.RefreshList()

    
    def OnPlayerExInfoDictChange(self, dExInfoDict):
        self.RefreshList()

    
    def OnSetNear(self, iPlayerID):
        LOG_DEBUG('\xb3]\xac\xb0\xbf\xcb\xb6\xc7', iPlayerID)
        netshitu1.C2SSetNear(iPlayerID)

    
    def OnDismiss(self, iPlayerID):
        LOG_DEBUG('\xc2_\xb5\xb4\xc3\xf6\xabY', iPlayerID)
        netshitu1.C2SSetRelieve(iPlayerID)

    
    def OnLookPlayerInfo(self, iPlayerID):
        import dlgfriend
        dlgfriend.FindPlayerWithID(iPlayerID, 1)

    
    def RefreshList(self):
        dResultList = []
        for dInfo in self.m_dMemberInfoList:
            dExInfo = mdshitu1.GetPlayerExInfoModel().GetPlayerExInfo(dInfo[shitudefine.KEY_PLAYER_ID])
            if not dExInfo:
                continue
            
            dTmp = { }
            dTmp[shitudefine.KEY_PLAYER_ID] = dInfo[shitudefine.KEY_PLAYER_ID]
            dTmp[shitudefine.KEY_NEAR_POINT] = dInfo[shitudefine.KEY_NEAR_POINT]
            if dInfo[shitudefine.KEY_IS_NEAR]:
                if dInfo[shitudefine.KEY_IS_MASTER]:
                    dTmp[shitudefine.KEY_RELATIONSHIP] = '\xbf\xcb\xb6\xc7\xaev\xa4\xf7'
                else:
                    dTmp[shitudefine.KEY_RELATIONSHIP] = '\xbf\xcb\xb6\xc7\xae{\xa7\xcc'
            elif dInfo[shitudefine.KEY_IS_MASTER]:
                dTmp[shitudefine.KEY_RELATIONSHIP] = '\xb4\xb6\xb3q\xaev\xa4\xf7'
            else:
                dTmp[shitudefine.KEY_RELATIONSHIP] = '\xb4\xb6\xb3q\xae{\xa7\xcc'
            dTmp[shitudefine.KEY_PLAYER_LV] = dExInfo[shitudefine.KEY_PLAYER_LV]
            dTmp[shitudefine.KEY_PLAYER_NAME] = dExInfo[shitudefine.KEY_PLAYER_NAME]
            dTmp[shitudefine.KEY_PLAYER_ONLINE] = dExInfo[shitudefine.KEY_PLAYER_ONLINE]
            dResultList.append(dTmp)
        
        self.GetView().RefreshMemberList(dResultList)



class CShifuShouyeDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_SelectID = None
        self.m_bShowTipsFlag = False
        self.m_dTaskInfoDict = { }
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oModel = mdshitu1.GetMasterShouyeModel()
        oModel.ssConnect(oModel.SS_TudiShouyeInfoChange, self.OnTudiShouyeInfoChange)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnPlayerInfoChange)
        oModel.ssConnect(oModel.SS_DegreeExInfoChange, self.OnDegreeExInfoChange)
        oModel = mdshitu1.GetFriendListModel()
        oModel.ssConnect(oModel.SS_TongMenInfoChange, self.OnTongMenInfoChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_PublishTask, self.OnPublishTask)
        oView.ssConnect(oView.SS_ShowExpProcessInfo, self.ShowExpProcessInfo)
        oView.ssConnect(oView.SS_ClearExpProcessInfo, self.ClearExpProcessInfo)
        oView.ssConnect(oView.SS_RequestTaskInfo, self.OnRequestTaskInfo)
        oView.ssConnect(oView.SS_LookPlayerInfo, self.LookPlayerInfo)
        self.InitDlg()

    
    def InitDlg(self):
        iTudiIDList = mdshitu1.GetFriendListModel().GetTudiIDList()
        dPlayerInfo = self.ProcessPlayerInfo(iTudiIDList)
        self.GetView().SetPlayerList(dPlayerInfo)
        import netshitu1
        for iPlayerID in iTudiIDList:
            netshitu1.C2SRequestTudiShouyeInfo(iPlayerID)
        

    
    def OnTudiShouyeInfoChange(self, iPlayerID, iDegree, iDegreeMax, iStatus, dTaskInfoDict):
        self.RefreshMemberItStatus(iPlayerID, iStatus)
        if self.m_SelectID != iPlayerID:
            return None
        
        if self.CheckSameData(iPlayerID, iDegree, iDegreeMax, iStatus, dTaskInfoDict):
            return None
        
        self.RefreshDlg(iPlayerID)

    
    def OnPlayerInfoChange(self, dPlayerExInfo):
        iTudiIDList = mdshitu1.GetFriendListModel().GetTudiIDList()
        dPlayerInfo = self.ProcessPlayerInfo(iTudiIDList)
        self.GetView().SetPlayerList(dPlayerInfo)

    
    def OnRequestTaskInfo(self, iPlayerID):
        LOG_DEBUG('\xbd\xd0\xa8D\xc0\xf2\xa8\xfa\xae{\xa7\xcc\xa5\xf4\xb0\xc8\xbc\xc6\xbe\xda', iPlayerID)
        if iPlayerID == self.m_SelectID:
            LOG_DEBUG('ID\xac\xdb\xa6P\xa9\xbf\xb2\xa4')
            return None
        
        self.m_SelectID = iPlayerID
        netshitu1.C2SRequestTudiShouyeInfo(iPlayerID)
        self.RefreshDlg(iPlayerID)

    
    def LookPlayerInfo(self, iPlayerID):
        LOG_DEBUG('\xacd\xac\xdd\xaa\xb1\xaea\xabH\xae\xa7', iPlayerID)
        import dlgfriend
        dlgfriend.FindPlayerWithID(iPlayerID, 1)

    
    def OnPublishTask(self):
        LOG_DEBUG('\xb5o\xa7G\xa5\xf4\xb0\xc8', self.m_SelectID)
        if not self.m_SelectID:
            LOG_DEBUG('\xa8S\xbf\xef\xa8\xa4\xa6\xe2', self.m_SelectID)
            return None
        
        iStatus = mdshitu1.GetMasterShouyeModel().GetStatus(self.m_SelectID)
        if iStatus == shitudefine.TASK_STATUS_UNSTART:
            netshitu1.C2SPublishTask(self.m_SelectID)
        

    
    def ShowExpProcessInfo(self):
        LOG_DEBUG('\xc5\xe3\xa5\xdc\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7', self.m_SelectID)
        netshitu1.C2SGetDegressExInfo(self.m_SelectID)
        self.m_bShowTipsFlag = True

    
    def OnDegreeExInfoChange(self, iPlayerID, iCurXLExp, iXLExpMax, iActive, iChushiLv, iNear):
        dPlayerInfo = mdshitu1.GetPlayerExInfoModel().GetPlayerExInfo(self.m_SelectID)
        if not dPlayerInfo and iPlayerID != self.m_SelectID or not (self.m_bShowTipsFlag):
            self.ClearExpProcessInfo()
            return None
        
        iLv = dPlayerInfo[shitudefine.KEY_PLAYER_LV]
        sColorLst = [
            '#Y',
            '#G']
        txt0 = '\xb4\xa3\xa4\xc9\xb5\xa5\xaf\xc5\xa1B\xad\xd7\xb7\xd2\xb5\xa5\xaf\xc5\xa5H\xa4\xce\xc0\xf2\xb1o\xac\xa1\xc5D\xab\xd7\xa1A\xa5i\xb4\xa3\xb0\xaa\xa5X\xaev\xb6i\xab\xd7#r'
        txt1 = '\xb7\xed\xabe\xb5\xa5\xaf\xc5:%s%d/%d#n#r' % (sColorLst[iLv >= 60], iLv, iChushiLv)
        txt2 = '\xad\xd7\xb7\xd2\xb8g\xc5\xe7:%s%d/%d#n#r' % (sColorLst[iCurXLExp >= iXLExpMax], iCurXLExp, iXLExpMax)
        txt3 = '\xac\xa1\xc5D\xab\xd7:%s%d/3000#n#r' % (sColorLst[iActive >= 3000], iActive)
        txt4 = '\xb7\xed\xabe\xbf\xcb\xb1K\xab\xd7\xac\xb0%d\xa1A\xbbP\xaev\xa4\xf7\xaa\xba\xbf\xcb\xb1K\xab\xd7\xb6V\xb0\xaa\xa5X\xaev\xbc\xfa\xc0y\xb6V\xb0\xaa' % iNear
        sTips = '%s%s%s%s%s' % (txt0, txt1, txt2, txt3, txt4)
        self.GetView().ShowExpTips(sTips)

    
    def OnTongMenInfoChange(self, dInfoList):
        iTudiIDList = mdshitu1.GetFriendListModel().GetTudiIDList()
        dPlayerInfo = self.ProcessPlayerInfo(iTudiIDList)
        self.GetView().SetPlayerList(dPlayerInfo)

    
    def ClearExpProcessInfo(self):
        LOG_DEBUG('\xb2M\xb2z\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7')
        self.m_bShowTipsFlag = False
        oView = self.GetView()
        if not oView:
            return None
        
        oView.ClearExpTips()

    
    def RefreshStatus(self, iStatus):
        oView = self.GetView()
        if iStatus == shitudefine.TASK_STATUS_DONE:
            oView.SetPublishBtnDone()
        elif iStatus == shitudefine.TASK_STATUS_ING:
            oView.SetPublishBtnStart()
        else:
            oView.SetPublishBtnUnstart()

    
    def RefreshMemberItStatus(self, iPlayerID, iStatus):
        oView = self.GetView()
        if iStatus == shitudefine.TASK_STATUS_DONE:
            oView.RefreshMemberStatus(iPlayerID, shitudefine.TASK_STATUS_DONE)
        elif iStatus == shitudefine.TASK_STATUS_ING:
            oView.RefreshMemberStatus(iPlayerID, shitudefine.TASK_STATUS_ING)
        else:
            oView.RefreshMemberStatus(iPlayerID, shitudefine.TASK_STATUS_UNSTART)

    
    def GetTudiIDList(self):
        oModel = mdshitu1.GetFriendListModel()
        iTudiList = []
        for dMemberInfo in oModel.GetTongMenList():
            if dMemberInfo[shitudefine.KEY_IS_CHUSHI] == 0 and dMemberInfo[shitudefine.KEY_RELATIONSHIP] in (shitudefine.RELATION_TUDI_NEAR, shitudefine.RELATION_TUDI):
                iTudiList.append(dMemberInfo[shitudefine.KEY_PLAYER_ID])
                continue
        
        return iTudiList

    
    def ProcessTaskList(self, dTaskInfoDict):
        import shitutaskdata
        dResultList = []
        for iTaskID in sorted(dTaskInfoDict.keys()):
            dTaskInfo = dTaskInfoDict[iTaskID]
            dTmp = shitutaskdata.GetTaskInfo(iTaskID)
            if not dTmp:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_TASK_TITLE] = dTmp['sTitle']
            dInfo[shitudefine.KEY_TASK_STATUS] = dTaskInfo[shitudefine.KEY_TASK_STATUS]
            if dInfo[shitudefine.KEY_TASK_STATUS] == shitudefine.TASK_STATUS_DONE:
                dInfo[shitudefine.KEY_DESC] = '\xa4w\xa7\xb9\xa6\xa8'
            else:
                dInfo[shitudefine.KEY_DESC] = '%d/%d' % (dTaskInfo[shitudefine.KEY_TASK_CUR], dTaskInfo[shitudefine.KEY_TASK_SUM])
            dInfo[shitudefine.KEY_TASK_ICON_PATH] = dTmp['sIconPath']
            dInfo[shitudefine.KEY_TASK_ICON_PACK] = dTmp['sIconPack']
            dResultList.append(dInfo)
        
        LOG_DEBUG('\xa5\xf4\xb0\xc8\xabH\xae\xa7', dResultList)
        return dResultList

    
    def ProcessPlayerInfo(self, iTudiIDList):
        import hero
        oModel = mdshitu1.GetPlayerExInfoModel()
        dResult = { }
        for iPlayerID in iTudiIDList:
            dPlayerInfo = oModel.GetPlayerExInfo(iPlayerID)
            if not dPlayerInfo:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_PLAYER_NAME] = dPlayerInfo[shitudefine.KEY_PLAYER_NAME]
            dInfo[shitudefine.KEY_PLAYER_CLASS] = hero.id2class(dPlayerInfo[shitudefine.KEY_PLAYER_CLASS])
            dInfo[shitudefine.KEY_PLAYER_LV] = dPlayerInfo[shitudefine.KEY_PLAYER_LV]
            dInfo[shitudefine.KEY_PLAYER_AVATAR] = dPlayerInfo[shitudefine.KEY_PLAYER_AVATAR]
            dInfo[shitudefine.KEY_TASK_STATUS] = shitudefine.TASK_STATUS_UNSTART
            dInfo[shitudefine.KEY_PLAYER_ONLINE] = dPlayerInfo[shitudefine.KEY_PLAYER_ONLINE]
            dInfo[shitudefine.KEY_PLAYER_ID] = iPlayerID
            dResult[iPlayerID] = dInfo
        
        return dResult

    
    def CheckSameData(self, iPlayerID, iDegree, iDegreeMax, iStatus, dTaskInfoDict):
        if iPlayerID not in self.m_dTaskInfoDict:
            return False
        
        dBufferInfoDict = self.m_dTaskInfoDict[iPlayerID]
        if dBufferInfoDict[shitudefine.KEY_TASK_DEGREE][0] == iDegree and dBufferInfoDict[shitudefine.KEY_TASK_DEGREE][1] == iDegreeMax and dBufferInfoDict[shitudefine.KEY_TASK_INFO] == dTaskInfoDict and dBufferInfoDict[shitudefine.KEY_TASK_STATUS] == iStatus:
            return True
        else:
            return False

    
    def SaveBuffer(self, iPlayerID, iDegree, iDegreeMax, iStatus, dTaskInfoDict):
        import copy
        self.m_dTaskInfoDict[iPlayerID] = dInfo = { }
        dInfo[shitudefine.KEY_TASK_DEGREE] = (iDegree, iDegreeMax)
        dInfo[shitudefine.KEY_TASK_STATUS] = iStatus
        dInfo[shitudefine.KEY_TASK_INFO] = copy.deepcopy(dTaskInfoDict)

    
    def RefreshDlg(self, iPlayerID):
        oModel = mdshitu1.GetMasterShouyeModel()
        dInfo = oModel.GetTaskInfo(iPlayerID)
        if not dInfo:
            return None
        
        (iDegree, iDegreeMax) = dInfo[shitudefine.KEY_TASK_DEGREE]
        iStatus = dInfo[shitudefine.KEY_TASK_STATUS]
        dTaskInfoDict = dInfo[shitudefine.KEY_TASK_INFO]
        self.GetView().SetExp(iDegree, iDegreeMax)
        dTaskList = self.ProcessTaskList(dTaskInfoDict)
        self.GetView().SetTaskInfo(dTaskList)
        self.RefreshStatus(iStatus)
        self.RefreshMemberItStatus(iPlayerID, iStatus)
        self.SaveBuffer(iPlayerID, iDegree, iDegreeMax, iStatus, dTaskInfoDict)



class CShouyeTipsDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        oModel = mdshitu1.GetMasterShouyeModel()
        oModel.ssConnect(oModel.SS_TudiShouyeInfoChange, self.OnTudiShouyeInfoChange)
        self.InitView()

    
    def InitView(self):
        oModel = mdshitu1.GetMasterShouyeModel()
        oView = self.GetView()
        iPlayerID = oView.GetPlayerID()
        dTaskInfoDict = oModel.GetTaskInfo(iPlayerID)
        if not dTaskInfoDict:
            return None
        
        dTaskInfo = dTaskInfoDict[shitudefine.KEY_TASK_INFO]
        tProgress = dTaskInfoDict[shitudefine.KEY_TASK_DEGREE]
        dTaskList = self.ProcessTaskList(dTaskInfo)
        oView.SetTaskInfo(iPlayerID, dTaskList)
        (iCurRate, iSumRate) = tProgress
        oView.SetExp(iPlayerID, iCurRate, iSumRate)

    
    def OnTudiShouyeInfoChange(self, iPlayerID, iDegree, iDegreeMax, iIsAllot, dTaskInfoDict):
        self.GetView().SetExp(iPlayerID, iDegree, iDegreeMax)
        dTaskList = self.ProcessTaskList(dTaskInfoDict)
        self.GetView().SetTaskInfo(iPlayerID, dTaskList)

    
    def ProcessTaskList(self, dTaskInfoDict):
        import shitutaskdata
        dResultList = []
        for iTaskID in sorted(dTaskInfoDict.keys()):
            dTaskInfo = dTaskInfoDict[iTaskID]
            dTmp = shitutaskdata.GetTaskInfo(iTaskID)
            if not dTmp:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_TASK_TITLE] = dTmp['sTitle']
            dInfo[shitudefine.KEY_TASK_STATUS] = dTaskInfo[shitudefine.KEY_TASK_STATUS]
            if dInfo[shitudefine.KEY_TASK_STATUS] == shitudefine.TASK_STATUS_DONE:
                dInfo[shitudefine.KEY_DESC] = '\xa4w\xa7\xb9\xa6\xa8'
            else:
                dInfo[shitudefine.KEY_DESC] = '%d/%d' % (dTaskInfo[shitudefine.KEY_TASK_CUR], dTaskInfo[shitudefine.KEY_TASK_SUM])
            dInfo[shitudefine.KEY_TASK_ICON_PATH] = dTmp['sIconPath']
            dInfo[shitudefine.KEY_TASK_ICON_PACK] = dTmp['sIconPack']
            dResultList.append(dInfo)
        
        LOG_DEBUG('\xa5\xf4\xb0\xc8\xabH\xae\xa7', dResultList)
        return dResultList



class CTudiShouyeTaskListDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_bShowTipsFlag = False

    
    def Init(self):
        oModel = mdshitu1.GetTudiShouyeModel()
        oModel.ssConnect(oModel.SS_TudiShouyeInfoChange, self.OnTudiShouyeInfoChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_JoinTask, self.OnJoinTask)

    
    def OnTudiShouyeInfoChange(self, iDegree, iDegreeMax, dTaskInfoList):
        oView = self.GetView()
        oView.SetExp(iDegree, iDegreeMax)
        dTaskList = self.ProcessTaskList(dTaskInfoList)
        oView.ShowTaskList(dTaskList)

    
    def OnJoinTask(self, iTaskID):
        import shitutaskdata
        import wrapui
        import autofindpath
        import tasktypedata
        dTaskInfo = shitutaskdata.GetTaskInfo(iTaskID)
        if dTaskInfo is None:
            return None
        
        if dTaskInfo['sSponsor'] == '\xaev\xa4\xf7':
            (_, sLink, _) = tasktypedata.GetData(3)
        else:
            sLink = dTaskInfo['sSponsor']
        dLinkInfo = wrapui.GetLinkDct(sLink)
        tData = None(None, None, None, None, None, None, None, wrapui)(dLinkInfo.get('context', ''))
        if len(tData) != 6:
            return None
        
        (sNpcName, _, sMapName, x, y, _) = tData
        x = int(x)
        y = int(y)
        autofindpath.AutoFind(sMapName, (x, y), sNpcName = sNpcName)

    
    def ShowExpProcessInfo(self):
        LOG_DEBUG('\xc5\xe3\xa5\xdc\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7')
        import hero
        netshitu1.C2SGetDegressExInfo(hero.GetRealID())
        self.m_bShowTipsFlag = True

    
    def OnDegreeExInfoChange(self, iPlayerID, iCurXLExp, iXLExpMax, iActive):
        import hero
        if hero.GetRealID() != iPlayerID:
            self.ClearExpProcessInfo()
            return None
        
        iLv = hero.GetProp('m_Grade', 0)
        sColorLst = [
            '#Y',
            '#G']
        txt1 = '\xb7\xed\xabe\xb5\xa5\xaf\xc5:%s%d/60#n#r' % (sColorLst[iLv >= 60], iLv)
        txt2 = '\xad\xd7\xb7\xd2\xb8g\xc5\xe7:%s%d/%d#n#r' % (sColorLst[iCurXLExp >= iXLExpMax], iCurXLExp, iXLExpMax)
        txt3 = '\xac\xa1\xc5D\xab\xd7:%s%d/3000#n#r' % (sColorLst[iActive >= 3000], iActive)
        sTips = '%s%s%s' % (txt1, txt2, txt3)
        self.GetView().ShowExpTips(sTips)

    
    def ClearExpProcessInfo(self):
        LOG_DEBUG('\xb2M\xb2z\xb6i\xab\xd7\xc3B\xa5~\xabH\xae\xa7')
        self.m_bShowTipsFlag = False
        oView = self.GetView()
        if not oView:
            return None
        
        oView.ClearExpTips()

    
    def ProcessTaskList(self, dTaskInfoList):
        import shitutaskdata
        dResultList = []
        for dTaskInfo in dTaskInfoList:
            iTaskID = dTaskInfo[shitudefine.KEY_TASK_ID]
            dTmp = shitutaskdata.GetTaskInfo(iTaskID)
            if not dTmp:
                continue
            
            if dTaskInfo[shitudefine.KEY_TASK_CUR] >= dTaskInfo[shitudefine.KEY_TASK_SUM]:
                continue
            
            dInfo = { }
            dInfo[shitudefine.KEY_PLAYER_NAME] = dTaskInfo[shitudefine.KEY_PLAYER_NAME]
            dInfo[shitudefine.KEY_TASK_ID] = iTaskID
            dInfo[shitudefine.KEY_TASK_CUR] = dTaskInfo[shitudefine.KEY_TASK_CUR]
            dInfo[shitudefine.KEY_TASK_SUM] = dTaskInfo[shitudefine.KEY_TASK_SUM]
            dInfo[shitudefine.KEY_TASK_TITLE] = dTmp['sTitle']
            dInfo[shitudefine.KEY_DESC] = dTmp['sDesc']
            dInfo[shitudefine.KEY_TASK_REWARD] = dTmp['sReward']
            dInfo[shitudefine.KEY_TASK_TARGET] = dTmp['sTarget']
            dResultList.append(dInfo)
        
        return dResultList



class CChushiListDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_dTudiInfoList = []

    
    def Init(self):
        oModel = mdshitu1.GetChushiListModel()
        oModel.ssConnect(oModel.SS_ChushiListChange, self.OnChushiListChange)
        oModel = mdshitu1.GetPlayerExInfoModel()
        oModel.ssConnect(oModel.SS_PlayerExInfoDictChange, self.OnPlayerExInfoDictChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_RequestGift, self.OnRequestGift)
        oView.ssConnect(oView.SS_LookPlayerInfo, self.OnLookPlayerInfo)

    
    def OnChushiListChange(self, dInfoList):
        self.m_dTudiInfoList = dInfoList
        self.RefreshList()

    
    def OnPlayerExInfoDictChange(self, dPlayerInfoDict):
        self.RefreshList()

    
    def OnRequestGift(self, iPlayerID):
        netshitu1.C2SGetChushiReward(iPlayerID)

    
    def OnLookPlayerInfo(self, iPlayerID):
        import dlginfo
        dlginfo.ShowInfoDialog(iPlayerID)

    
    def RefreshList(self):
        import avatar
        dResultList = []
        for dInfo in self.m_dTudiInfoList:
            dTmp = { }
            iPlayerID = dInfo[shitudefine.KEY_PLAYER_ID]
            dPlayerExInfo = mdshitu1.GetPlayerExInfoModel().GetPlayerExInfo(iPlayerID)
            if not dPlayerExInfo:
                continue
            
            dTmp[shitudefine.KEY_PLAYER_ID] = iPlayerID
            dTmp[shitudefine.KEY_PLAYER_NAME] = dPlayerExInfo[shitudefine.KEY_PLAYER_NAME]
            dTmp[shitudefine.KEY_PLAYER_AVATAR] = avatar.Int2PhotoArr(*dPlayerExInfo[shitudefine.KEY_PLAYER_AVATAR])
            dTmp[shitudefine.KEY_ASSESS_DESC] = shitudefine.ASSESS_GRADE_2_DESC.get(dInfo[shitudefine.KEY_ASSESS_GRADE], '\xb5L')
            dTmp[shitudefine.KEY_REWARD_NUM] = dInfo[shitudefine.KEY_REWARD_NUM]
            dTmp[shitudefine.KEY_ASSESS_DEGREE] = dInfo[shitudefine.KEY_ASSESS_DEGREE]
            if dInfo[shitudefine.KEY_ASSESS_GRADE] == shitudefine.ASSESS_GRADE_BEST:
                dTmp[shitudefine.KEY_DESC] = '\xa4U\xa4@\xaf\xc5\xb5\xfb\xbb\xf9\xbc\xc8\xa5\xbc\xb6}\xa9\xf1\xa1A\xb7q\xbd\xd0\xb4\xc1\xab\xdd\xa1I'
            else:
                dTmp[shitudefine.KEY_DESC] = '\xa8\xec\xa4U\xa4@\xad\xd3\xb5\xfb\xbb\xf9\xaa\xba\xb6i\xab\xd7\xa1G%d%%' % dInfo[shitudefine.KEY_ASSESS_DEGREE]
            dResultList.append(dTmp)
        
        self.GetView().RefreshList(dResultList)



class CFriendListDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        import mdshitu1
        import mdredpoint
        oRedPointMgr = mdredpoint.GetCRedPointModel()
        oModel = mdshitu1.GetFriendListModel()
        oModel.ssConnect(oModel.SS_RequestTuDiNumChange, self.OnRequestTuDiNumChange)
        oRedPointMgr.ssConnect(oRedPointMgr.SS_UpdateRedPoint, self.UpdateRedPoint)

    
    def OnRequestTuDiNumChange(self, iNum):
        pass

    
    def UpdateRedPoint(self, *args):
        import mdredpoint
        import netreddot
        dData = mdredpoint.GetCRedPointModel().GetRedPointState(netreddot.MYQ_MSGLIST)
        bRed = dData.get('bRed', False)
        dExtend = dData.get('dExtend', { })
        iNum = 0
        if dExtend:
            iNum = dExtend.get('Sum', 0)
        
        self.SetShowNewShituRedPoint(bRed, iNum)

    
    def SetShowShituRedPoint(self, bShow):
        self.GetView().RefreshShituPageRedPoint(bShow)

    
    def SetShowNewShituRedPoint(self, bShow, iSum):
        self.GetView().RefreshNewShituPageRedPoint(bShow, iSum)



class CMainmenuBtnDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        import mdshitu1
        oModel = mdshitu1.GetFriendListModel()
        oModel.ssConnect(oModel.SS_RequestTuDiNumChange, self.OnRequestTuDiNumChange)
        iNum = oModel.GetNotReadRequestNum()
        if iNum > 0:
            self.GetView().NotifyFriendRedDot(str(id(self)), True)
        

    
    def OnRequestTuDiNumChange(self, iNum):
        import mdshitu1
        iNotRead = mdshitu1.GetFriendListModel().GetNotReadRequestNum()
        self.SetShowShituRedPoint(iNotRead > 0)

    
    def SetShowShituRedPoint(self, bShow):
        self.GetView().NotifyFriendRedDot(str(id(self)), bShow)



def SortPlayerList(dInfo):
    if dInfo[shitudefine.KEY_PLAYER_ONLINE] == 0:
        iOnline = 1
    else:
        iOnline = 0
    return (iOnline, dInfo[shitudefine.KEY_PLAYER_NAME])


def IsShoutuNum(iFlag):
    return iFlag & 1 == 0


def IsShoutuMonthEnable(iFlag):
    return iFlag & 2 == 0


def IsHasGroup(iFlag):
    return iFlag & 4 == 0


def IsHuoyueEnable(iFlag):
    return iFlag & 8 == 0
