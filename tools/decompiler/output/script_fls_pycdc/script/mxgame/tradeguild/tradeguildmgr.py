# pycdc 交叉复核产物 · script.fls entry 4276
# co_filename(原始)='script/mxgame/tradeguild/tradeguildmgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4276.pyc (Python 2.5)

import itemdata
import itemdefine
import limitserver
import permission
from tradeguilddefines import *
import slot
import nettradeguild
g_TradeGuildMgr = None

def ModuleReset():
    global g_TradeGuildMgr
    g_TradeGuildMgr = None


def GetTradeGuildMgr():
    global g_TradeGuildMgr
    if not g_TradeGuildMgr:
        g_TradeGuildMgr = CTradeGuildMgr()
    
    return g_TradeGuildMgr


class CTradeGuildMgr(slot.ISignalSubject):
    SS_EquipListChange = 'EquipListChange(iType, dEquipInfoList)'
    SS_PetListChange = 'EquipPetChange(iType, dPetInfoList)'
    SS_PageChange = 'PageChange(iCurPage, iSumPage)'
    SS_SaleEquipListChange = 'SaleEquipListChange(dEquipInfoList)'
    SS_SalePetListChange = 'SalePetListChange(dPetInfoList)'
    SS_SaleRecordChange = 'SaleRecordChange(sRecordList)'
    SS_SelectItem = 'SelectItem(iType, dItem)'
    
    def __init__(self):
        self.m_CurEquipPage = 1
        self.m_CurPetPage = 1
        self.m_iMaxEquipPage = 1
        self.m_iMaxPetPage = 1
        self.m_CurEquipType = None
        self.m_CurPetType = None
        self.m_EquipInfoList = []
        self.m_PetInfoList = []
        self.m_EquipReceiveTime = { }
        self.m_PetReceiveTime = { }
        self.m_SaleRocord = []
        self.m_dSaleDict = { }
        self.m_EquipData = None
        self.m_PetData = None
        self.m_EquipSearchBuffer = { }
        self.m_PetSearchBuffer = { }
        self.m_RemainTimer = None
        self.InitSignal()
        self.InitSearchData()

    
    def RequestEquipList(self, iType, iPage = 1, sSearchTxt = '', iMiniLv = LV_MIN, iMaxLv = LV_MAX, iSortType = SORT_TYPE_LV_UP):
        '''
\t\t\xbd\xd0\xa8D\xb8\xcb\xb3\xc6\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac\xa1A\xa4Mor\xbcCor...\xa1A\xb9\xef\xc0\xb3 EQUIP_TYPE_SWORD
\t\t:param iPage: \xb2\xc4\xb4X\xad\xb6\xbc\xc6\xbe\xda
\t\t:param sSearchTxt: \xbfz\xbf\xef\xaa\xba\xa4\xe5\xa5\xbb
\t\t:param iMiniLv: \xb3\xcc\xa4p\xb5\xa5\xaf\xc5
\t\t:param iMaxLv: \xb3\xcc\xa4j\xb5\xa5\xaf\xc5
\t\t:param iSortType: \xb1\xc6\xa7\xc7\xbc\xd2\xb6\xf4
\t\t'''
        LOG_DEBUG('\xbd\xd0\xa8D\xb8\xcb\xb3\xc6\xa6C\xaa\xed', iType, iPage, sSearchTxt, iMiniLv, iMaxLv, iSortType)
        self.m_CurEquipType = iType
        self.m_CurEquipPage = iPage
        if iType == EQUIP_TYPE_CARE:
            nettradeguild.C2SRequestCareList(0, iType, iPage)
        else:
            iSortModel = SORT_TYPE_2_MODEL[iSortType]
            iEquipPos = 0
            if iType in EQUIP_TYPE_2_SEARCH:
                if EQUIP_TYPE_2_SEARCH[iType] in itemdata.EQUIP2POS:
                    iEquipPos = itemdata.EQUIP2POS[EQUIP_TYPE_2_SEARCH[iType]]
                
            
            nettradeguild.C2SNewRequestItemList(0, iType, iPage, iSortModel, iEquipPos)

    
    def RequestPetList(self, iType, iPage = 1, sSearchTxt = '', iMiniLv = LV_MIN, iMaxLv = LV_MAX, iSortType = SORT_TYPE_LV_UP):
        '''
\t\t\xbd\xd0\xa8D\xc3d\xaa\xab\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac\xa1A0-10\xaf\xc5or15-25\xaf\xc5or...
\t\t:param iPage: \xb2\xc4\xb4X\xad\xb6\xbc\xc6\xbe\xda
\t\t:param sSearchTxt: \xbfz\xbf\xef\xaa\xba\xa4\xe5\xa5\xbb
\t\t:param iMiniLv: \xb3\xcc\xa4p\xb5\xa5\xaf\xc5
\t\t:param iMaxLv: \xb3\xcc\xa4j\xb5\xa5\xaf\xc5
\t\t:param iSortType: \xb1\xc6\xa7\xc7\xbc\xd2\xb6\xf4
\t\t'''
        LOG_DEBUG('\xbd\xd0\xa8D\xc3d\xaa\xab\xa6C\xaa\xed', iType, iPage, sSearchTxt, iMiniLv, iMaxLv, iSortType)
        self.m_CurPetType = iType
        self.m_CurPetPage = iPage
        if iType == PET_TYPE_CARE:
            nettradeguild.C2SRequestCareList(1, iType, iPage)
        else:
            iSortModel = SORT_TYPE_2_MODEL[iSortType]
            iPetGrade = 0
            if iType in PET_TYPE_2_SEARCH:
                iPetGrade = PET_TYPE_2_SEARCH[iType][1]
            
            nettradeguild.C2SNewRequestItemList(1, iType, iPage, iSortModel, iPetGrade)

    
    def BuyItem(self, iItemID, iItemType, iCurPage = None):
        '''
\t\t\xc1\xca\xb6R\xb0\xd3\xab~
\t\t:param iItemID: \xb0\xd3\xab~id
\t\t:param iItemType: \xb0\xd3\xab~\xc3\xfe\xab\xac(0-\xb8\xcb\xb3\xc6,1-\xc3d\xaa\xab)
\t\t:param iCurPage: \xb7\xed\xabe\xad\xb6
\t\t'''
        if iCurPage is None:
            if iItemType == 0:
                iCurPage = self.m_CurEquipPage
            else:
                iCurPage = self.m_CurPetPage
        
        LOG_DEBUG('\xc1\xca\xb6R\xb0\xd3\xab~', iItemID, iItemType, iCurPage)
        nettradeguild.C2SBuyItem(iItemType, iItemID, iCurPage)

    
    def SetItemCare(self, iType, iItemID, iCare):
        '''
\t\t\xc3\xf6\xaa`\xb0\xd3\xab~
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iItemID: \xb9\xea\xa8\xd2ID
\t\t:param iCare: 1-\xc3\xf6\xaa`\xa1A0-\xa8\xfa\xae\xf8\xc3\xf6\xaa`
\t\t'''
        nettradeguild.C2SItemCare(iType, iItemID, iCare)

    
    def GetItemRemainTime(self, iType, iItemID):
        '''
\t\t\xc0\xf2\xa8\xfa\xb0\xd3\xab~\xa4\xbd\xa5\xdc\xb4\xc1\xb3\xd1\xbel\xae\xc9\xb6\xa1
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iItemID: \xb9\xea\xa8\xd2ID
\t\t:return: iTime
\t\t'''
        import C_sys
        if iType == 0:
            dReceiveTime = self.m_EquipReceiveTime
        else:
            dReceiveTime = self.m_PetReceiveTime
        if iItemID not in dReceiveTime:
            return 0
        else:
            return dReceiveTime[iItemID]

    
    def RequestSaleList(self, iType):
        '''
\t\t\xbd\xd0\xa8D\xa5X\xb0\xe2\xb0\xd3\xab~\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t'''
        LOG_DEBUG('\xbd\xd0\xa8D\xa5X\xb0\xe2\xb0\xd3\xab~\xa6C\xaa\xed', iType)
        nettradeguild.C2SRequestSaleList(iType)

    
    def RequestSaleRecord(self):
        '''
\t\t\xbd\xd0\xa8D\xa5X\xb0\xe2\xb0O\xbf\xfd
\t\t'''
        LOG_DEBUG('\xbd\xd0\xa8D\xa5X\xb0\xe2\xb0O\xbf\xfd')
        nettradeguild.C2SRequestSaleRecord()

    
    def PushItem(self, iType, iItemID, iCashType, iPrice):
        '''
\t\t\xa4W\xac[\xb0\xd3\xab~
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iItemID: \xb9\xea\xa8\xd2ID
\t\t:param iCashType: 0-\xb2{\xaa\xf7 1-\xa5d
\t\t:param iPrice: \xbb\xf9\xae\xe6
\t\t'''
        LOG_DEBUG('\xa4W\xac[\xb0\xd3\xab~', iType, iItemID, iCashType, iPrice)
        nettradeguild.C2SPushItem(iType, iItemID, iCashType, iPrice)

    
    def ResetPrice(self, iType, iItemID, iCashType, iPrice):
        '''
\t\t\xad\xab\xb7s\xa9w\xbb\xf9\xb0\xd3\xab~
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iItemID: \xb9\xea\xa8\xd2ID
\t\t:param iCashType: 0-\xb2{\xaa\xf7 1-\xa5d
\t\t:param iPrice: \xbb\xf9\xae\xe6
\t\t'''
        LOG_DEBUG('\xad\xab\xb7s\xa9w\xbb\xf9\xb0\xd3\xab~', iType, iItemID, iCashType, iPrice)
        nettradeguild.C2SResetPrice(iType, iItemID, iCashType, iPrice)

    
    def PullItem(self, iType, iItemID):
        '''
\t\t\xa4U\xac[\xb0\xd3\xab~
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iItemID: \xb9\xea\xa8\xd2ID
\t\t'''
        LOG_DEBUG('\xa4U\xac[\xb0\xd3\xab~', iType, iItemID)
        nettradeguild.C2SPullItem(iType, iItemID)

    
    def GetEquipMaxPage(self):
        return self.m_iMaxEquipPage

    
    def GetPetMaxPage(self):
        return self.m_iMaxPetPage

    
    def UpdateEquipList(self, iType, iSumPage, dInfoList):
        '''
\t\t\xa7\xf3\xb7s\xb8\xcb\xb3\xc6\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac
\t\t:param iSumPage: \xc1`\xad\xb6\xbc\xc6
\t\t:param dInfoList: \xb8\xcb\xb3\xc6\xabH\xae\xa7\xa6C\xaa\xed
\t\t\t[
\t\t\t\t{"iItID":\xb8\xcb\xb3\xc6id,
\t\t\t\t"iShapeID":"\xb3y\xab\xacid",
\t\t\t\t"bCare":"\xacO\xa7_\xc3\xf6\xaa`",
\t\t\t\t"iRemainTime":\xb3\xd1\xbel\xae\xc9\xb6\xa1,
\t\t\t\t"iCashType":\xb3f\xb9\xf4\xc3\xfe\xab\xac(0-\xb2{\xaa\xf7,1-\xb1H\xb0\xe2\xa5d),
\t\t\t\t"iPrice":\xbb\xf9\xae\xe6}\xa1A
\t\t\t]
\t\t:return: None
\t\t'''
        LOG_DEBUG('\xa7\xf3\xb7s\xb8\xcb\xb3\xc6\xa6C\xaa\xed', iType, iSumPage)
        if iType != self.m_CurEquipType:
            LOG_DEBUG('\xaa\xf0\xa6^\xb8\xcb\xb3\xc6\xc3\xfe\xab\xac\xa9M\xbd\xd0\xa8D\xaa\xba\xa4\xa3\xa4@\xbc\xcb\xa1A\xa5\xe1\xb1\xf3\xbc\xc6\xbe\xda')
            return None
        
        self.m_EquipReceiveTime = { }
        for dInfo in dInfoList:
            iEquipID = dInfo['iItID']
            iRemainTime = dInfo['iRemainTime']
            self.m_EquipReceiveTime[iEquipID] = iRemainTime
        
        if self.m_EquipReceiveTime:
            self.CreateRemainTimer()
        else:
            self.DelRemainTimer()
        if self.m_CurEquipPage > iSumPage:
            self.m_CurEquipPage = iSumPage
        
        self.m_iMaxEquipPage = iSumPage
        self.m_EquipInfoList = dInfoList
        self.ssEmit(self.SS_EquipListChange, iType, dInfoList)
        self.ssEmit(self.SS_PageChange, self.m_CurEquipPage, iSumPage)

    
    def UpdatePetList(self, iType, iSumPage, dInfoList):
        '''
\t\t\xa7\xf3\xb7s\xc3d\xaa\xab\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac
\t\t:param iSumPage: \xc1`\xad\xb6\xbc\xc6
\t\t:param dInfoList: \xc3d\xaa\xab\xabH\xae\xa7\xa6C\xaa\xed
\t\t\t[
\t\t\t\t{"iItID":\xc3d\xaa\xabid,
\t\t\t\t"iShapeID":"\xb3y\xab\xacid",
\t\t\t\t"bCare":"\xacO\xa7_\xc3\xf6\xaa`",
\t\t\t\t"iRemainTime":\xb3\xd1\xbel\xae\xc9\xb6\xa1,
\t\t\t\t"iCashType":\xb3f\xb9\xf4\xc3\xfe\xab\xac(0-\xb2{\xaa\xf7,1-\xb1H\xb0\xe2\xa5d),
\t\t\t\t"iPrice":\xbb\xf9\xae\xe6,
\t\t\t\t"iPetType":\xc3d\xaa\xab\xc3\xfe\xab\xac(0-\xb4\xb6\xb3q,1-\xc5\xdc\xb2\xa7,2-\xb3\xa5\xa5\xcd)}\xa1A
\t\t\t]
\t\t'''
        LOG_DEBUG('\xa7\xf3\xb7s\xc3d\xaa\xab\xa6C\xaa\xed', iType, iSumPage)
        if iType != self.m_CurPetType:
            LOG_DEBUG('\xaa\xf0\xa6^\xc3d\xaa\xab\xc3\xfe\xab\xac\xa9M\xbd\xd0\xa8D\xaa\xba\xa4\xa3\xa4@\xbc\xcb\xa1A\xa5\xe1\xb1\xf3\xbc\xc6\xbe\xda')
            return None
        
        self.m_PetReceiveTime = { }
        for dInfo in dInfoList:
            iPetID = dInfo['iItID']
            iRemainTime = dInfo['iRemainTime']
            self.m_PetReceiveTime[iPetID] = iRemainTime
        
        if self.m_PetReceiveTime:
            self.CreateRemainTimer()
        else:
            self.DelRemainTimer()
        if self.m_CurPetPage > iSumPage:
            self.m_CurPetPage = iSumPage
        
        self.m_iMaxPetPage = iSumPage
        self.m_PetInfoList = dInfoList
        self.ssEmit(self.SS_PetListChange, iType, dInfoList)
        self.ssEmit(self.SS_PageChange, self.m_CurPetPage, iSumPage)

    
    def UpdateSaleItemList(self, iType, dInfoList):
        '''
\t\t\xa7\xf3\xb7s\xa5X\xb0\xe2\xb0\xd3\xab~\xa6C\xaa\xed
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param dInfoList: \xb0\xd3\xab~\xa6C\xaa\xed
\t\t\t[
\t\t\t\t{"iItID":\xc3d\xaa\xabid,
\t\t\t\t"iShapeID":\xb3y\xab\xacid,
\t\t\t\t"iCashType":\xb3f\xb9\xf4\xc3\xfe\xab\xac(0-\xb2{\xaa\xf7,1-\xb1H\xb0\xe2\xa5d),
\t\t\t\t"iPrice":\xbb\xf9\xae\xe6,
\t\t\t\t"iPetType":\xc3d\xaa\xab\xc3\xfe\xab\xac(0-\xb4\xb6\xb3q,1-\xc5\xdc\xb2\xa7,2-\xb3\xa5\xa5\xcd)}
\t\t\t]
\t\t'''
        LOG_DEBUG('\xa7\xf3\xb7s\xa5X\xb0\xe2\xa6C\xaa\xed', iType)
        self.m_dSaleDict[iType] = dInfoList
        if iType == 0:
            self.ssEmit(self.SS_SaleEquipListChange, dInfoList)
        else:
            self.ssEmit(self.SS_SalePetListChange, dInfoList)

    
    def GetSaleItemList(self, iType):
        return self.m_dSaleDict.get(iType, [])

    
    def GetMySaleSummon(self, iSummonID):
        for dPetInfo in self.m_dSaleDict.get(1, []):
            if dPetInfo.get('iItID', None) == iSummonID:
                return dPetInfo
                continue
        

    
    def UpdateSaleRecord(self, lRecord):
        '''
\t\t\xa7\xf3\xb7s\xbeP\xb0\xe2\xb0O\xbf\xfd
\t\t:param sRecord: \xbeP\xb0\xe2\xb0O\xbf\xfd\xad\xec\xa9l\xabH\xae\xa7
\t\t'''
        LOG_DEBUG('\xa7\xf3\xb7s\xbeP\xb0\xe2\xb0O\xbf\xfd')
        self.m_SaleRocord = lRecord
        self.ssEmit(self.SS_SaleRecordChange, self.m_SaleRocord)

    
    def SelectItem(self, iType, dInfo):
        self.ssEmit(self.SS_SelectItem, iType, dInfo)

    
    def CreateRemainTimer(self):
        import timer
        self.DelRemainTimer()
        self.m_RemainTimer = timer.Timer(1, self.RefreshRemainTime, -1, self)

    
    def DelRemainTimer(self):
        if self.m_RemainTimer:
            self.m_RemainTimer.Release()
            self.m_RemainTimer = None
        

    
    def RefreshRemainTime(self):
        bHasEquipChange = False
        if self.m_EquipReceiveTime:
            for iItemId, iRemainTime in self.m_EquipReceiveTime.items():
                if iRemainTime > 0:
                    iRemainTime -= 1
                    self.m_EquipReceiveTime[iItemId] = iRemainTime
                    for index, dEquipData in enumerate(self.m_EquipInfoList):
                        if dEquipData['iItID'] == iItemId:
                            self.m_EquipInfoList[index]['iRemainTime'] = iRemainTime
                            continue
                    
                    if iRemainTime <= 0:
                        bHasEquipChange = True
                    
                iRemainTime <= 0
            
        
        bHasPetChange = False
        if self.m_PetReceiveTime:
            for iItemId, iRemainTime in self.m_PetReceiveTime.items():
                if iRemainTime > 0:
                    iRemainTime -= 1
                    self.m_PetReceiveTime[iItemId] = iRemainTime
                    for index, dPetData in enumerate(self.m_PetInfoList):
                        if dPetData['iItID'] == iItemId:
                            self.m_PetInfoList[index]['iRemainTime'] = iRemainTime
                            continue
                    
                    if iRemainTime <= 0:
                        bHasPetChange = True
                    
                iRemainTime <= 0
            
        
        if bHasEquipChange:
            self.ssEmit(self.SS_EquipListChange, 0, self.m_EquipInfoList)
        
        if bHasPetChange:
            self.ssEmit(self.SS_PetListChange, 1, self.m_PetInfoList)
        

    
    def InitSignal(self):
        '''
\t\t\xaa\xec\xa9l\xa4\xc6\xabH\xb8\xb9
\t\t'''
        self.ssInit()
        self.ssCreate(self.SS_EquipListChange)
        self.ssCreate(self.SS_PetListChange)
        self.ssCreate(self.SS_PageChange)
        self.ssCreate(self.SS_SaleEquipListChange)
        self.ssCreate(self.SS_SalePetListChange)
        self.ssCreate(self.SS_SaleRecordChange)

    
    def GetSearchEquip(self, iType, sSearchTxt, iMinLv, iMaxLv):
        '''
\t\t\xc0\xf2\xb1o\xbfz\xbf\xef\xaa\xba\xb8\xcb\xb3\xc6
\t\t:param iType: \xc3\xfe\xab\xac
\t\t:param sSearchTxt: \xbfz\xbf\xef\xa4\xe5\xa5\xbb
\t\t:param iMinLv: \xb5\xa5\xaf\xc5\xa4U\xad\xad
\t\t:param iMaxLv: \xb5\xa5\xaf\xc5\xa4W\xad\xad
\t\t:return: [iShapeID,]
\t\t'''
        import itemdata
        tSearchKey = (iType, sSearchTxt, iMinLv, iMaxLv)
        if tSearchKey in self.m_EquipSearchBuffer:
            return self.m_EquipSearchBuffer[tSearchKey]
        
        if iType not in EQUIP_TYPE_2_SEARCH:
            return []
        
        sType = EQUIP_TYPE_2_SEARCH[iType]
        iResultList = []
        for iShape, dEquipInfo in self.m_EquipData.iteritems():
            if not itemdata.IsType(iShape, sType):
                continue
            
            sName = dEquipInfo['sName']
            iLv = dEquipInfo['iLv']
            if sSearchTxt not in sName:
                continue
            
            if iLv < iMinLv or iLv > iMaxLv:
                continue
            
            iResultList.append(iShape)
        
        iResultList.sort()
        self.m_EquipSearchBuffer[tSearchKey] = iResultList
        return iResultList

    
    def GetSearchPet(self, iType, sSearchTxt, iMinLv, iMaxLv):
        '''
\t\t\xc0\xf2\xb1o\xbfz\xbf\xef\xaa\xba\xc3d\xaa\xab
\t\t:param iType: \xc3\xfe\xab\xac
\t\t:param sSearchTxt: \xbfz\xbf\xef\xa4\xe5\xa5\xbb
\t\t:param iMinLv: \xb5\xa5\xaf\xc5\xa4U\xad\xad
\t\t:param iMaxLv: \xb5\xa5\xaf\xc5\xa4W\xad\xad
\t\t:return: [iShapeID,]
\t\t'''
        tSearchKey = (iType, sSearchTxt, iMinLv, iMaxLv)
        if tSearchKey in self.m_PetSearchBuffer:
            return self.m_PetSearchBuffer[tSearchKey]
        
        if iType not in PET_TYPE_2_SEARCH:
            return []
        
        tRange = PET_TYPE_2_SEARCH[iType]
        iResultList = []
        for iShape, dPetInfo in self.m_PetData.iteritems():
            (iTypeMin, iTypeMax) = tRange
            iMin = max(iMinLv, iTypeMin)
            iMax = min(iMaxLv, iTypeMax)
            sName = dPetInfo['sName']
            iLv = dPetInfo['iLv']
            if sSearchTxt not in sName:
                continue
            
            if iLv < iMin or iLv > iMax:
                continue
            
            iResultList.append(iShape)
        
        iResultList.sort()
        self.m_PetSearchBuffer[tSearchKey] = iResultList
        return iResultList

    
    def InitSearchData(self):
        '''
\t\t\xaa\xec\xa9l\xa4\xc6\xb7j\xaf\xc1\xa6C\xaa\xed
\t\t'''
        import itemdata
        import petdata
        self.m_EquipData = { }
        for iShape in itemdata.DATA.iterkeys():
            if not itemdata.IsType(iShape, 'equip'):
                continue
            
            iLv = itemdata.GetEquipLv(iShape)
            if not iLv < LV_MIN:
                if iLv > LV_MAX:
                    continue
                
            self.m_EquipData[iShape] = data = { }
            data['sName'] = itemdata.DATA[iShape][0]
            data['iLv'] = iLv
        
        self.m_PetData = { }
        for iShape in petdata.DATA.iterkeys():
            if petdata.IsShenShou(iShape) and petdata.IsXianShou(iShape) or petdata.IsXiYouShou(iShape):
                continue
            
            iLv = petdata.DATA[iShape]['carry_grade']
            if iLv < LV_MIN or iLv > LV_MAX:
                continue
            
            self.m_PetData[iShape] = data = { }
            data['sName'] = petdata.DATA[iShape]['name']
            data['iLv'] = iLv
        

    
    def SortRequestItemListByGrade(self, iType, iRequestList, bDown):
        '''
\t\t\xb9\xef\xbd\xd0\xa8D\xaa\xab\xab~\xa6C\xaa\xed\xab\xf6\xb5\xa5\xaf\xc5\xb1\xc6\xa7\xc7
\t\t:param iType: \xc3\xfe\xab\xac 0-\xb8\xcb\xb3\xc6 1-\xc3d\xaa\xab
\t\t:param iRequestList: \xbd\xd0\xa8D\xa6C\xaa\xed
\t\t:param bDown: \xacO\xa7_\xad\xb0\xa7\xc7
\t\t:return: \xb1\xc6\xa7\xc7\xab\xe1\xa6C\xaa\xed
\t\t'''
        if iType == 0:
            iRequestList.sort(cmp = self.EquipSort, reverse = bDown)
        else:
            iRequestList.sort(cmp = self.PetSort, reverse = bDown)
        return iRequestList

    
    def EquipSort(self, iShape1, iShpae2):
        if self.m_EquipData[iShape1]['iLv'] > self.m_EquipData[iShpae2]['iLv']:
            return 1
        elif self.m_EquipData[iShape1]['iLv'] < self.m_EquipData[iShpae2]['iLv']:
            return -1
        else:
            return 0

    
    def PetSort(self, iShape1, iShpae2):
        if self.m_PetData[iShape1]['iLv'] > self.m_PetData[iShpae2]['iLv']:
            return 1
        elif self.m_PetData[iShape1]['iLv'] < self.m_PetData[iShpae2]['iLv']:
            return -1
        else:
            return 0



def TestRequestEquip(iType = EQUIP_TYPE_SWORD, sSearchTxt = '', iMiniLv = LV_MIN, iMaxLv = LV_MAX, iSortType = SORT_TYPE_LV_UP):
    GetTradeGuildMgr().RequestEquipList(iType, 1, sSearchTxt = sSearchTxt, iMiniLv = iMiniLv, iMaxLv = iMaxLv, iSortType = iSortType)


def TestRequestPet(iType = PET_TYPE_0_10, sSearchTxt = '', iMiniLv = LV_MIN, iMaxLv = LV_MAX, iSortType = SORT_TYPE_LV_UP):
    GetTradeGuildMgr().RequestPetList(iType, 1, sSearchTxt = sSearchTxt, iMiniLv = iMiniLv, iMaxLv = iMaxLv, iSortType = iSortType)
