# pycdc 交叉复核产物 · script.fls entry 1335
# co_filename(原始)='script/mxgame/makeequip/model/mdbuild/mdbuildequipment.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1335.pyc (Python 2.5)

import limitserver
import slot
import buildequipmentlistdata
import misc
import hero
import math
import permission
g_mgr = { }
g_iPreShowLv = None
g_BuildMaterialMgr = None
g_TradeBuildMaterialMgr = None

def ModuleReset():
    global g_mgr, g_BuildMaterialMgr, g_TradeBuildMaterialMgr, g_iPreShowLv
    g_mgr = { }
    g_BuildMaterialMgr = None
    g_TradeBuildMaterialMgr = None
    g_iPreShowLv = None


def GetMgr(sViewClass):
    oMgr = g_mgr.get(sViewClass, None)
    if not oMgr:
        oMgr = CEquipmentPageMgr()
        g_mgr[sViewClass] = oMgr
    
    return oMgr


def GetBuildMaterialMgr():
    global g_BuildMaterialMgr
    if not g_BuildMaterialMgr:
        g_BuildMaterialMgr = CEquipmentBuildMaterialMgr()
    
    return g_BuildMaterialMgr


def GetTradeBuildMaterialMgr():
    global g_TradeBuildMaterialMgr
    if not g_TradeBuildMaterialMgr:
        g_TradeBuildMaterialMgr = CEquipmentBuildMaterialMgr()
    
    return g_TradeBuildMaterialMgr


class CEquipmentPageMgr(slot.ISignalSubject):
    SS_PageDataChange = 'SS_PageDataChange(iLv)'
    
    def __init__(self):
        self.ssInit()
        self.m_iCurLv = 0
        self.m_lstLv = [ i * 10 for i in xrange(3, 15) ]
        self.m_lstLiuPaiSkillId = [
            1001,
            1002,
            1003,
            1004,
            1005,
            1011]
        self.m_iCurSelectedType = 0
        self.m_bShowByPlayerLv = False

    
    def InitShowByPlayerLv(self, b):
        '''
\t\t\xacO\xa7_\xae\xda\xbe\xda\xaa\xb1\xaea\xb5\xa5\xaf\xc5\xc5\xe3\xa5\xdc\xb8\xcb\xb3\xc6\xa5\xb4\xb3y\xa4W\xad\xad
\t\t'''
        self.m_bShowByPlayerLv = b

    
    def SetEquipmentListSelectType(self, iEquipmentType):
        self.m_iCurSelectedType = iEquipmentType

    
    def GetEquipmentListSelectedType(self):
        return self.m_iCurSelectedType

    
    def GetLiuPaiSkillList(self):
        return self.m_lstLiuPaiSkillId

    
    def GetEquipmentListByLv(self, iLv):
        return buildequipmentlistdata.GetEquipmentList(iLv)

    
    def GetMaxShowLv(self):
        iMaxLv = 140
        if self.m_bShowByPlayerLv:
            iLv = hero.GetProp('m_Grade')
        else:
            iLv = iMaxLv
        iServerLv = misc.GetServerLv()
        iCurLv = min(math.floor(max(iLv + 15, iServerLv)), iMaxLv)
        iResult = 0
        for iShowLv in self.m_lstLv:
            if iCurLv >= iShowLv:
                iResult = iShowLv
                continue
        
        return iResult

    
    def GetShowLvList(self):
        iMaxLv = self.GetMaxShowLv()
        iResultList = []
        for iShowLv in self.m_lstLv:
            if iShowLv <= iMaxLv:
                iResultList.append(iShowLv)
                continue
        
        return iResultList

    
    def SetCurShowLv(self, iLv, bAutoSelect = \xa3\x85ue):
        global g_iPreShowLv
        iMaxLv = self.GetMaxShowLv()
        if iMaxLv < iLv:
            iLv = iMaxLv
        
        if iLv < 30:
            iLv = 30
        
        self.m_iCurLv = iLv
        g_iPreShowLv = iLv
        self.ssEmit(self.SS_PageDataChange, iLv, bAutoSelect)

    
    def GetCurShowLv(self):
        return self.m_iCurLv

    
    def GetPreShowLv(self):
        return g_iPreShowLv

    
    def GetShowLvByGrade(self, iGrade):
        iCurIdx = 0
        for idx, iLv in enumerate(self.m_lstLv):
            if iLv <= iGrade:
                iCurIdx = idx
                continue
        
        return self.m_lstLv[iCurIdx]



class CEquipmentBuildMaterialMgr(slot.ISignalSubject):
    SS_SetBuildEquipment = 'SS_SetBuildEquipment(iType, iLv, iID, iJingHuaID, iTuZhiID)'
    SS_PutDownItem = 'SS_PutDownItem(iItemID)'
    
    def __init__(self):
        self.ssInit()
        self.m_iCurItemID = 0
        self.m_iCurEquipLv = 0
        self.m_iCurEquipType = 0
        self.m_iJingHuaID = 0
        self.m_iTuZhiID = 0
        self.m_bHasMakeMoney = False
        self.m_iMakeMoneyType = 0
        self.m_bMakeSymbol = False

    
    def SetBuildEquipment(self, iType, iLv, iShapeID, iID = None, iJingHuaID = None, iTuZhiID = None):
        self.m_iCurEquipLv = iLv
        self.m_iCurEquipType = iType
        self.m_iCurItemID = iID
        self.m_iCurShapeID = iShapeID
        self.m_iJingHuaID = iJingHuaID
        self.m_iTuZhiID = iTuZhiID
        self.ssEmit(self.SS_SetBuildEquipment, iType, iLv, iID, iJingHuaID, iTuZhiID, iShapeID)

    
    def SetHasMakeMoney(self, bHas, iMoneyType = 0):
        self.m_bHasMakeMoney = bHas
        self.m_iMakeMoneyType = iMoneyType

    
    def GetHasMakeMoney(self):
        return (self.m_bHasMakeMoney, self.m_iMakeMoneyType)

    
    def SetMakeSymbol(self, b):
        self.m_bMakeSymbol = b

    
    def GetMakeSymbol(self):
        return self.m_bMakeSymbol

    
    def SetPutDownItem(self, iItemID):
        self.ssEmit(self.SS_PutDownItem, iItemID)

    
    def GetBuildEquipmentInfo(self):
        return (self.m_iCurEquipType, self.m_iCurEquipLv, self.m_iCurShapeID, self.m_iCurItemID, self.m_iJingHuaID, self.m_iTuZhiID)
