# pycdc 交叉复核产物 · script.fls entry 3883
# co_filename(原始)='script/mxgame/return2020/md2020return.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3883.pyc (Python 2.5)

import slot
import datapresentcenter_2020returnward
g_oReturnModel = None

def ModuleReset():
    global g_oReturnModel
    g_oReturnModel = None


def GetModel():
    '''
\t:rtype: C2020ReturnModel
\t'''
    global g_oReturnModel
    if not g_oReturnModel:
        g_oReturnModel = C2020ReturnModel()
    
    return g_oReturnModel


class C2020ReturnModel(slot.ISignalSubject):
    SS_SwitchPage = 'SS_SwitchPage(iPage)'
    SS_RefreshBindNum = 'SS_RefreshBindNum()'
    SS_RefreshProgress = 'SS_RefreshProgress()'
    SS_RefreshTaskList = 'SS_RefreshTaskList()'
    SS_RefreshHuoyueReward = 'SS_RefreshHuoyueReward()'
    SS_RefreshPlayer = 'SS_RefreshPlayer()'
    SS_RefreshRecruitNum = 'SS_RefreshRecruitNum()'
    SS_RefreshFriendList = 'SS_RefreshFriendList()'
    SS_RefreshRedPoint = 'SS_RefreshRedPoint()'
    SS_RefreshShowHelpDlg = 'SS_RefreshShowHelpDlg()'
    SS_RefreshPresentRedPoint = 'SS_RefreshPresentRedPoint()'
    PAGE_REWARD_MSG = 2
    PAGE_FRIEND_MSG = 3
    PAGE_HELP_MSG = 4
    RedPoint_Reward = 0
    RedPoint_Wish = 1
    RedPoint_Help = 2
    RedPoint_Mission = 3
    
    def __init__(self):
        self.ssInit()
        self.m_iBindNum = 0
        self.m_iProgress = 0
        self.m_dTaskList = self.GetDefaultTaskList()
        self.m_dHuoyueData = self.GetDefaultHuoyueData()
        self.m_iPlayerID = 0
        self.m_iRecruitNum = 0
        self.m_dFriendList = []
        self.m_iSelectID = 0
        self.m_iRedPointRewardIDList = []
        self.m_dBackRedPoint = { }
        self.m_dPresentCenterPoint = { }
        self.m_iRecruitRedPoint = 0
        self.m_dRecruit = { }
        self.m_lBack = []
        self.m_iLeftTime = 0
        self.m_bShowHelpDlg = False
        self.m_iShowOpenPage = self.PAGE_REWARD_MSG

    
    def IsShowHelpDlg(self):
        return self.m_bShowHelpDlg

    
    def RefreshShowHelpDlg(self, bShow):
        self.m_bShowHelpDlg = bShow
        self.ssEmit(self.SS_RefreshShowHelpDlg)

    
    def SwitchFriendPage(self):
        self.ssEmit(self.SS_SwitchPage, self.PAGE_FRIEND_MSG)

    
    def SetDefaultShowHelpPage(self):
        self.m_iShowOpenPage = self.PAGE_HELP_MSG

    
    def ResetDefaultOpenPage(self):
        self.m_iShowOpenPage = self.PAGE_REWARD_MSG

    
    def GetDefaultOpenPage(self):
        return self.m_iShowOpenPage

    
    def SetBindNum(self, iNum):
        self.m_iBindNum = iNum
        self.ssEmit(self.SS_RefreshBindNum)

    
    def GetBindNum(self):
        return self.m_iBindNum

    
    def SetProgress(self, iProgress):
        self.m_iProgress = iProgress
        self.ssEmit(self.SS_RefreshProgress)

    
    def GetProgress(self):
        return self.m_iProgress

    
    def SetTaskList(self, dTaskList):
        self.m_dTaskList = dTaskList
        self.ssEmit(self.SS_RefreshTaskList)

    
    def GetDefaultTaskList(self):
        iKeyList = datapresentcenter_2020returnward.GetAllTaskData().keys()
        iKeyList.sort()
        dTaskInfoList = []
        for iTaskID in iKeyList:
            if iTaskID < iTaskID:
                pass
            elif iTaskID < 5000:
                dTaskInfo = { }
                dTaskInfo['iTaskID'] = iTaskID
                dTaskInfo['iProgress'] = 0
                dTaskInfo['iComplete'] = 0
                dTaskInfo['iGot'] = 0
                dTaskInfo['iPlayerID'] = 0
                dTaskInfoList.append(dTaskInfo)
                continue
        
        return dTaskInfoList

    
    def GetTaskList(self):
        return self.m_dTaskList

    
    def SetHuoyueData(self, dHuoyueData):
        self.m_dHuoyueData = dHuoyueData
        self.ssEmit(self.SS_RefreshHuoyueReward)

    
    def HasGotHuoyue(self, iRewardId):
        return self.m_dHuoyueData.get(iRewardId, 0)

    
    def SetLeftTime(self, iLeftTime):
        self.m_iLeftTime = iLeftTime

    
    def GetLeftTime(self):
        return self.m_iLeftTime

    
    def GetHuoyueNeedProgress(self, iRewardId):
        return datapresentcenter_2020returnward.GetHuoyueByID(iRewardId, { }).get('iHuoyue', 0)

    
    def GetDefaultHuoyueData(self):
        iKeyList = datapresentcenter_2020returnward.GetHuoyueData().keys()
        iKeyList.sort()
        dHuoyueData = { }
        for iHuoyueID in iKeyList:
            dHuoyueData[iHuoyueID] = 0
        
        return dHuoyueData

    
    def GetHuoyueData(self):
        return self.m_dHuoyueData

    
    def SetPlayerInfo(self, iPlayerID):
        self.m_iPlayerID = iPlayerID
        self.ssEmit(self.SS_RefreshPlayer)

    
    def GetPlayerInfo(self):
        return self.m_iPlayerID

    
    def SetRecruitNum(self, iRecruitNum):
        self.m_iRecruitNum = iRecruitNum
        self.ssEmit(self.SS_RefreshRecruitNum)

    
    def GetRecruitNum(self):
        return self.m_iRecruitNum

    
    def SetFriendData(self, dFriendList):
        self.m_dFriendList = dFriendList
        iSelectID = self.GetSelectID()
        bFind = False
        for dData in dFriendList:
            if iSelectID == dData['iID']:
                bFind = True
                break
                continue
        
        if not bFind:
            self.SetSelectID(0)
        
        self.ssEmit(self.SS_RefreshFriendList)

    
    def GetFriendData(self):
        return self.m_dFriendList

    
    def SetSelectID(self, iID):
        self.m_iSelectID = iID

    
    def GetSelectID(self):
        return self.m_iSelectID

    
    def GetSelectName(self):
        if not self.m_iSelectID:
            return ''
        
        import friend
        return friend.GetFriendName(self.m_iSelectID)

    
    def SetRedPointRewardData(self, dRecruit, lBack):
        '''
\t\t1000~1999 - \xa6^\xc2k\xaa\xcc\xac\xa1\xc5D\xbc\xfa\xc0yID
\t\t2000~2999 - \xa9\xdb\xb6\xd2\xaa\xcc\xac\xa1\xc5D\xbc\xfa\xc0yID
\t\t3000~3999 - \xa6^\xc2k\xa5\xf4\xb0\xc8\xbc\xfa\xc0yID
\t\t4000~4999 - \xa9\xdb\xb6\xd2\xa5\xf4\xb0\xc8\xbc\xfa\xc0yID
\t\t'''
        import mdpresentcenter
        self.m_iRecruitRedPoint = 0
        for iPlayerID in dRecruit:
            if dRecruit[iPlayerID]:
                self.m_iRecruitRedPoint = 1
                break
                continue
        
        self.m_dRecruit = dRecruit
        self.m_lBack = lBack
        self.SetPresentCenterRedPoint(self.PAGE_REWARD_MSG, self.m_iRecruitRedPoint)

    
    def SetPresentCenterRedPoint(self, iType, iPoint):
        if self.m_dPresentCenterPoint.get(iType) != iPoint:
            self.m_dPresentCenterPoint[iType] = iPoint
            self.ssEmit(self.SS_RefreshPresentRedPoint)
        

    
    def GetPresentCenterRedPoint(self, iType = None):
        if iType == None:
            return self.m_dPresentCenterPoint
        
        return self.m_dPresentCenterPoint.get(iType)

    
    def SetBackRedPoint(self, iType, iPoint):
        pass

    
    def GetBackRedPoint(self, iType = None):
        if iType == None:
            return self.m_dBackRedPoint
        
        return self.m_dBackRedPoint.get(iType)

    
    def GetBackIconRedPoint(self):
        if self.m_dBackRedPoint:
            for iShow in self.m_dBackRedPoint.values():
                if iShow:
                    return True
                    continue
            
        
        return False

    
    def GetBackReward(self):
        return self.m_lBack

    
    def GetRecruitRedPoint(self):
        return self.m_iRecruitRedPoint

    
    def GetRecruitReward(self):
        return self.m_dRecruit
