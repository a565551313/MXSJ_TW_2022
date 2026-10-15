# pycdc 交叉复核产物 · script.fls entry 3709
# co_filename(原始)='script/mxgame/activityreward/model/mdseasonchallenge.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3709.pyc (Python 2.5)

'''
\xc8\xfc\xbc\xbe\xcc\xf4\xd5\xbd
'''
import activityrewarddefine
import slot
import battlepassdata
g_SeasonChallengeModel = None

def GetSeasonChallengeModel():
    global g_SeasonChallengeModel
    if g_SeasonChallengeModel is None:
        g_SeasonChallengeModel = CSeasonChallengeModel()
    
    return g_SeasonChallengeModel


class CSeasonChallengeModel(slot.ISignalSubject):
    SS_OnRefreshTaskList = 'OnRefreshTaskList(oList)'
    SS_OnShowRewardIconTips = 'OnShowRewardIconTips(iTaskId, iStep, sDesc)'
    SS_OnRefreshSeasonRedDot = 'OnRefreshSeasonRedDot(bShow)'
    
    def __init__(self):
        self.ssInit()
        self.m_oTaskList = []
        self.m_bRewardFlag = False
        self.m_iRewardNum = 0

    
    def GetTaskList(self):
        return self.m_oTaskList

    
    def SetTaskList(self, dList):
        for dVal in dList:
            oData = battlepassdata.GetSJTZInfo(dVal['taskId'], dVal['iStep'])
            dVal['type'] = oData['iTaskType']
            dVal['desc'] = oData['sTaskDesc']
            dVal['iNeed'] = oData['iMaxCount']
            dVal['taskName'] = oData['sTaskName']
            dVal['iHaveChildTask'] = oData['iHaveChildTask']
            dVal['iTaskShape1'] = battlepassdata.GetSJTZTaskShape(dVal['taskId'], 1)
            dVal['iTaskShape2'] = battlepassdata.GetSJTZTaskShape(dVal['taskId'], 2)
            dVal['iTaskShape3'] = battlepassdata.GetSJTZTaskShape(dVal['taskId'], 3)
            dVal['iMaxCount1'] = battlepassdata.GetSJTZTaskMaxCount(dVal['taskId'], 1)
            dVal['iMaxCount2'] = battlepassdata.GetSJTZTaskMaxCount(dVal['taskId'], 2)
            dVal['iMaxCount3'] = battlepassdata.GetSJTZTaskMaxCount(dVal['taskId'], 3)
        
        for i, dVal in enumerate(dList):
            bExist = False
            for j, data in enumerate(self.m_oTaskList):
                if data['taskId'] == dVal['taskId']:
                    bExist = True
                    self.m_oTaskList[j] = dList[i]
                    continue
            
            if not bExist:
                self.m_oTaskList.append(dVal)
            
            bExist = False
        
        bCanGetReward = False
        self.m_iRewardNum = 0
        for i, data in enumerate(self.m_oTaskList):
            for iRewardState in data['state']:
                if iRewardState == activityrewarddefine.TYPE_REWARD_RECEIVE_ING:
                    self.m_iRewardNum += 1
                    continue
                self
            
        
        if self.m_iRewardNum > 0:
            bCanGetReward = True
        
        self.SetRewardFlag(bCanGetReward)
        self.ssEmit(self.SS_OnRefreshTaskList, self.m_oTaskList)

    
    def GetTaskData(self, iTaskId):
        for val in self.m_oTaskList:
            if val['taskId'] == iTaskId:
                return val
                continue
        

    
    def SetRewardFlag(self, bFlag):
        import mdactivityreward
        self.m_bRewardFlag = bFlag
        self.ssEmit(self.SS_OnRefreshSeasonRedDot, bFlag)
        mdactivityreward.CalBPRedPoint()

    
    def GetRewardFlag(self):
        return self.m_bRewardFlag

    
    def GetRewardNum(self):
        return self.m_iRewardNum

    
    def OnShowRewardIconTips(self, iTaskId, iStep, \xb2\x85\xa4\xb2\xa2):
        self.ssEmit(self.SS_OnShowRewardIconTips, iTaskId, iStep, \xb2\x85\xa4\xb2\xa2)
