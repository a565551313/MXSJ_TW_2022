# pycdc 交叉复核产物 · script.fls entry 687
# co_filename(原始)='script/mxgame/activity/ladderrankallstar/model/mdallgameguess.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_687.pyc (Python 2.5)

import slot
g_oGuessMatchModel = None
g_oMyGuessRecordModel = None
g_oGuessChampionModel = None
g_oCGuessShopModel = None

def ModuleReset():
    global g_oGuessMatchModel, g_oMyGuessRecordModel, g_oGuessChampionModel, g_oCGuessShopModel
    g_oGuessMatchModel = None
    g_oMyGuessRecordModel = None
    g_oGuessChampionModel = None
    g_oCGuessShopModel = None


def GetGuessMatchModel():
    global g_oGuessMatchModel
    if not g_oGuessMatchModel:
        g_oGuessMatchModel = CGuessMatchModel()
    
    return g_oGuessMatchModel


def GetMyGuessRecordModel():
    global g_oMyGuessRecordModel
    if not g_oMyGuessRecordModel:
        g_oMyGuessRecordModel = CMyGuessRecordModel()
    
    return g_oMyGuessRecordModel


def GetGuessChampionModel():
    global g_oGuessChampionModel
    if not g_oGuessChampionModel:
        g_oGuessChampionModel = CGuessChampionModel()
    
    return g_oGuessChampionModel


def GetGuessShopModel():
    global g_oCGuessShopModel
    if not g_oCGuessShopModel:
        g_oCGuessShopModel = CGuessShopModel()
    
    return g_oCGuessShopModel


class CGuessMatchModel(slot.ISignalSubject):
    SS_UpdateGuessMatchDlg = 'UpdateGuessMatchDlg()'
    SS_UpdateGuessGroup = 'UpdateGuessGroup()'
    SS_UpdateGuessMoney = 'UpdateGuessMoney()'
    SS_UpdateGuessTeam = 'UpdateGuessTeam()'
    
    def __init__(self):
        del self
        None.ssInit()
        self.m_dictMatchData = { }
        self.m_iCoin = 0
        self.m_iTeamType = 0
        self.m_iSelectGroup = 1
        self.m_iClickBattleId = 0
        self.m_bOpen = False

    
    def UpdateGuessMatchDlg(self, iTeamType, dictData):
        self.m_iTeamType = iTeamType
        self.m_dictMatchData = dictData
        self.SetOpen(True)
        self.ssEmit(self.SS_UpdateGuessMatchDlg)
        self.ssEmit(self.SS_UpdateGuessTeam)

    
    def GetBattleInfoByID(self, iBattleID):
        for idx, dicInfo in self.m_dictMatchData.items():
            if dicInfo['iBattleID'] == iBattleID:
                self.m_iClickBattleId = iBattleID
                return dicInfo
                continue
        

    
    def UpdateCoin(self, iCoin):
        self.m_iCoin = iCoin
        self.ssEmit(self.SS_UpdateGuessMoney)

    
    def SetSelectGroup(self, iGroup):
        self.m_iSelectGroup = iGroup
        self.ssEmit(self.SS_UpdateGuessGroup)

    
    def SetOpen(self, bOpen):
        self.m_bOpen = bOpen

    
    def GetSelectGroup(self):
        return self.m_iSelectGroup

    
    def GetMatchDic(self):
        return self.m_dictMatchData

    
    def GetCurTeamType(self):
        return self.m_iTeamType

    
    def GetMyGuessScore(self):
        return self.m_iCoin

    
    def GetBattleId(self):
        return self.m_iClickBattleId

    
    def GetOpen(self):
        return self.m_bOpen



class CMyGuessRecordModel(slot.ISignalSubject):
    SS_UpdateMyGuessRecordDlg = 'UpdateMyGuessRecordDlg()'
    
    def __init__(self):
        self.ssInit()
        self.m_lstData = []

    
    def UpdateMyGuessRocordDlg(self, lstData):
        self.m_lstData = lstData
        self.ssEmit(self.SS_UpdateMyGuessRecordDlg)

    
    def GetMatchData(self):
        return self.m_lstData



class CGuessChampionModel(slot.ISignalSubject):
    SS_OpenGuessChampion = 'OpenGuessChampion()'
    
    def __init__(self):
        self.ssInit()
        self.m_dictMatchData = { }
        self.m_iSelectGroupId = None

    
    def SetSelectGroupID(self, iGroupId):
        self.m_iSelectGroupId = iGroupId

    
    def OpenGuessChampion(self, dictPlayerData):
        self.m_dictMatchData = dictPlayerData
        self.ssEmit(self.SS_OpenGuessChampion)

    
    def GetMatchDic(self):
        return self.m_dictMatchData

    
    def GetSelectGroupId(self):
        return self.m_iSelectGroupId



class CGuessShopModel(slot.ISignalSubject):
    SS_ShopItemData = 'OnShopItemData(iShopList)'
    SS_UpdateTicket = 'OnUpdateTicket()'
    
    def __init__(self):
        self.ssInit()
        self.m_iShopLst = []
        self.m_iTicket = 0

    
    def SetShopItemData(self, iShopList):
        self.m_iShopLst = iShopList
        self.ssEmit(self.SS_ShopItemData, iShopList)

    
    def SetTicket(self, iTicket):
        self.m_iTicket = iTicket
        self.ssEmit(self.SS_UpdateTicket, iTicket)

    
    def GetTicket(self):
        return self.m_iTicket
