# pycdc 交叉复核产物 · script.fls entry 3128
# co_filename(原始)='script/mxgame/returncollectcards/mdreturncollectcards.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3128.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/5/18 15:23
\xd7\xf7\xd5\xdf: 
\xce\xc4\xbc\xfe: mdreturncollectcards
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import slot
import returncollectcardsdefines
import returncollectcarddata
import minigame101
g_oReturnCollectCardsModel = None

def ModuleReset():
    global g_oReturnCollectCardsModel
    g_oReturnCollectCardsModel = None


def GetReturnCollectCardsModel():
    ''':rtype: CReturnCollectCardsModel'''
    global g_oReturnCollectCardsModel
    if not g_oReturnCollectCardsModel:
        g_oReturnCollectCardsModel = CReturnCollectCardsModel()
    
    return g_oReturnCollectCardsModel


class CReturnCollectCardsModel(slot.ISignalSubject):
    SS_UpdateAllCardInfo = 'SS_UpdateAllCardInfo()'
    SS_UpdateDlgShowInfo = 'SS_UpdateDlgShowInfo()'
    SS_DataReachSign = 'SS_DataReachSign()'
    SS_DrawReward = 'SS_DrawReward'
    SS_RefreshCloseAniBtnSelect = 'SS_RefreshCloseAniBtnSelect()'
    SS_RefreshRedPoint = 'SS_RefreshRedPoint'
    
    def __init__(self):
        self.ssInit()
        self.m_dAllCardInfoList = []
        self.m_lAllCardState = []
        self.m_lTaskCardState = []
        self.m_lRewardCardState = []
        self.m_dDlgShowInfo = { }
        self.m_bClosePlayRewardAni = False
        self.m_bRedDot = 0
        self.InitAllCardData()

    
    def InitAllCardData(self):
        for iPos in xrange(0, returncollectcardsdefines.All_BOX_NUM):
            dCardData = returncollectcarddata.GetDataByPos(iPos)
            dAllCardInfo = {
                'iMap': dCardData['iMap'],
                'iShape': dCardData['iShape'],
                'sCardName': dCardData['sCardName'],
                'iNum': dCardData['iNum'],
                'iRewardID': dCardData['iRewardID'],
                'iState': returncollectcardsdefines.CARD_TYPE_BACK,
                'iType': returncollectcardsdefines.CARD_TYPE_BACK }
            self.m_dAllCardInfoList.append(dAllCardInfo)
        

    
    def UpdateCardInfoByCardState(self, iCardStateList):
        self.ssEmit(self.SS_DataReachSign)
        if len(iCardStateList) != returncollectcardsdefines.All_BOX_NUM or self.m_lAllCardState == iCardStateList:
            return None
        
        self.m_lAllCardState = iCardStateList
        lCardState = []
        lRewardCardState = [
            None]
        for iIndex, dData in enumerate(self.m_dAllCardInfoList):
            iState = iCardStateList[dData['iMap']]
            self.m_dAllCardInfoList[iIndex]['iState'] = iState
            if dData['iMap'] < returncollectcardsdefines.BOX_NUM:
                self.m_dAllCardInfoList[iIndex]['iType'] = iState
                lCardState.append(iState)
                continue
            self.m_dAllCardInfoList[iIndex]['iType'] = returncollectcardsdefines.CARD_TYPE_REWARD
            lRewardCardState.append(iState)
        
        self.m_lTaskCardState = lCardState
        self.m_lRewardCardState = lRewardCardState
        self.SetJKRedDot(returncollectcardsdefines.CARD_STATE_CANRECEIVE in self.m_lRewardCardState)
        self.ssEmit(self.SS_UpdateAllCardInfo)

    
    def GetAllCardInfo(self):
        return self.m_dAllCardInfoList

    
    def UpdateDlgShowInfo(self, dDlgShowInfo):
        if dDlgShowInfo == self.m_dDlgShowInfo:
            return None
        
        self.m_dDlgShowInfo = dDlgShowInfo
        self.ssEmit(self.SS_UpdateDlgShowInfo)

    
    def GetDlgShowInfo(self):
        return self.m_dDlgShowInfo

    
    def SetDrawResult(self, dData):
        if not dData['iResult']:
            return None
        
        iResult = dData['iResult']
        iActivityID = dData['iActivityID']
        if iActivityID == minigame101.G101_FLAG_RETURNJK1:
            bGuarantee = False
        else:
            bGuarantee = True
        self.ssEmit(self.SS_DrawReward, iResult, bGuarantee)

    
    def SetClosePlayRewardAni(self, bClosePlayRewardAni):
        self.m_bClosePlayRewardAni = bClosePlayRewardAni
        self.ssEmit(self.SS_RefreshCloseAniBtnSelect)

    
    def GetClosePlayRewardAni(self):
        return self.m_bClosePlayRewardAni

    
    def GetCardStateList(self):
        return self.m_lTaskCardState

    
    def GetRewardCardStateList(self):
        return self.m_lRewardCardState

    
    def SetJKRedDot(self, bRedDot):
        if self.m_bRedDot == bRedDot:
            return None
        
        self.m_bRedDot = bRedDot
        self.ssEmit(self.SS_RefreshRedPoint)

    
    def GetIsShowJKRedPoint(self):
        if self.m_bRedDot or returncollectcardsdefines.CARD_STATE_CANRECEIVE in self.m_lRewardCardState:
            return True
        else:
            return False
