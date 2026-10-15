# pycdc 交叉复核产物 · script.fls entry 3260
# co_filename(原始)='script/mxgame/gongji/mdgongji.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3260.pyc (Python 2.5)

import math
import hero
import item
import itemdefine
import misc
import slot
import officeradvantagedata
g_oGongJiModel = None

def ModuleReset():
    global g_oGongJiModel
    g_oGongJiModel = None


def GetModel():
    global g_oGongJiModel
    if not g_oGongJiModel:
        g_oGongJiModel = CModelGongji()
    
    return g_oGongJiModel


class CModelGongji(slot.ISignalSubject):
    SS_ServerDataChg = 'SS_ServerDataChg()'
    SS_SelectItemChg = 'SS_SelectItemChg()'
    SS_ChangePage = 'SS_ChangePage()'
    
    def __init__(self):
        '''
\t\t\xbb\xaa\xa6\xfc\xa5u\xbb\xdd\xadn\xaa\xbe\xb9D\xb7\xed\xabe\xb5\xa5\xaf\xc5\xa9M\xb7\xed\xabe\xc2I\xbc\xc6\xa7Y\xa5i\xa1A\xc2I\xbc\xc6\xa9M\xb5\xa5\xaf\xc5\xb1q\xaa\xb1\xaea\xc4\xdd\xa9\xca\xae\xb3\xa1A\xa8\xea\xb7s\xae\xc9\xa6P\xae\xc9\xa8\xea\xb7s\xb3o\xb8\xcc
\t\t'''
        self.m_dAllDataList = []
        self.m_dServerDict = {
            'iToday': 0,
            'iTodayMax': 50,
            'iWeek': 0,
            'iWeekMax': 1000,
            'iRookie': 0,
            'iWeekResume': 0 }
        self.m_dSelectItemInfo = { }
        self.m_iItemListNum = 8
        self.m_iCurrIdx = 0
        self.m_dSelectGonggiInfo = { }
        self.m_iEveryPageMaxSize = 0
        self.ssInit()

    
    def GetMy#ata(self):
        return officeradvantagedata.GetMyGuanZhiInfo()

    
    def ResetAllData(self):
        lData = misc.DeepCopy(officeradvantagedata.GetAllDataList())
        lData.remove(officeradvantagedata.GetGuanZhiDataByIndex(0))
        self.SetAllData(lData)

    
    def SetEveryPageMaxSize(self, iNum):
        self.m_iEveryPageMaxSize = iNum

    
    def SetAllData(self, dList):
        self.m_dAllDataList = dList

    
    def GetAllData(self):
        return self.m_dAllDataList

    
    def GetCurrPageData(self):
        if not self.m_dAllDataList:
            return []
        
        iEnd = self.m_iCurrIdx + self.m_iEveryPageMaxSize
        iLen = len(self.m_dAllDataList)
        if iEnd > iLen:
            iEnd = iLen
        
        iStart = iEnd - self.m_iEveryPageMaxSize
        lCurrPageData = self.m_dAllDataList[iStart:iEnd]
        return lCurrPageData

    
    def ChangePage(self, iNum):
        iOld = self.m_iCurrIdx
        self.m_iCurrIdx += iNum * self.m_iEveryPageMaxSize
        self.m_iCurrIdx = max(self.m_iCurrIdx, 0)
        self.m_iCurrIdx = min(self.m_iCurrIdx, len(self.m_dAllDataList) - self.m_iEveryPageMaxSize)
        if iOld != self.m_iCurrIdx:
            self.ssEmit(self.SS_ChangePage)
        

    
    def SetCurrIdx(self, iIdx):
        self.m_iCurrIdx = iIdx

    
    def SetSelectGonggiInfo(self, \x86\xa6ata):
        self.m_dSelectGonggiInfo = \x86\xa6ata

    
    def GetSelectGonggiInfo(self):
        return self.m_dSelectGonggiInfo

    
    def SetServerData(self, \x86\xa6ata):
        self.m_dServerDict = \x86\xa6ata
        self.ssEmit(self.SS_ServerDataChg)

    
    def GetServerData(self):
        return self.m_dServerDict

    
    def SetSelectItemData(self, \x86\xa6ata):
        self.m_dSelectItemInfo = \x86\xa6ata
        self.ssEmit(self.SS_SelectItemChg)

    
    def GetSelectItemData(self):
        return self.m_dSelectItemInfo

    
    def GetItemListNum(self):
        return self.m_iItemListNum

    
    def SetItemListNum(self, iNum):
        self.m_iItemListNum = iNum

    
    def GetGuanZhiTips(self):
        iScore = hero.GetProp('m_iSorce', 0)
        iGrade = hero.GetProp('m_Grade', 0)
        sTips = officeradvantagedata.GetGuanZhiCostTips(iScore, iGrade)
        \x86\xa6ata = officeradvantagedata.GetGuanZhiInfoByScore(iScore)
        sTips += '#r\xba\xfb\xab\xf9\xa9x\xc2\xbe\xa9\xd2\xbb\xdd\xa5\\\xc1Z\xad\xc8\xa1G%s' % \x86\xa6ata['iMin']
        return sTips

    
    def GetLastValue(self):
        return (self.m_dServerDict['iTodayMax'] - self.m_dServerDict['iToday'], self.m_dServerDict['iWeekMax'] - self.m_dServerDict['iWeek'])

    
    def GetItemList(self):
        dItemList = []
        iItemIDList = []
        for iPos, oItemObj in item.GetItems(item.ITEM_NORMAL).iteritems():
            if iPos < item.ITEM_START:
                continue
            
            if not oItemObj:
                continue
            
            if self.IsValidItem(oItemObj):
                iItemID = oItemObj.GetID()
                if iItemID in self.m_dSelectItemInfo:
                    iCount = self.m_dSelectItemInfo[iItemID]
                    bSelect = True
                    iGongji = self.GetOneItemValue(iItemID, iCount)
                else:
                    iCount = oItemObj.GetQuantity()
                    bSelect = False
                    iGongji = 0
                dInfo = {
                    'iCount': iCount,
                    'iPos': iPos,
                    'iItemID': iItemID,
                    'bSelect': bSelect,
                    'iGongji': iGongji }
                dItemList.append(dInfo)
                iItemIDList.append(iItemID)
                continue
        
        for iItemID in self.m_dSelectItemInfo.keys():
            if iItemID not in iItemIDList:
                del self.m_dSelectItemInfo[iItemID]
                continue
        
        dItemList.sort(key = (lambda dDict: dDict['iPos']))
        iLen = len(dItemList)
        if iLen < self.GetItemListNum():
            dEmptyItem = {
                'iItemID': 0 }
            for _ in xrange(self.GetItemListNum() - iLen):
                dItemList.append(dEmptyItem)
            
        
        return dItemList

    
    def GetSelectValue(self):
        iValue = 0
        for iItemID in self.m_dSelectItemInfo:
            iValue += self.GetOneItemValue(iItemID, self.m_dSelectItemInfo[iItemID])
        
        return iValue

    
    def GetOneItemValue(self, iItemID, iNum):
        if not iNum:
            return 0
        
        oItemObj = item.GetItem(iItemID)
        iShape = oItemObj.GetShape()
        if iShape == itemdefine.SHAPE_MSYJ:
            sExtName = oItemObj.GetExtName()
            if '\xb0\xaa\xaf\xc5' in sExtName:
                return 20 * iNum
            elif '\xb2\xd7\xaf\xc5' in sExtName:
                return 40 * iNum
            
        elif iShape in itemdefine.ID_GEM_LIST:
            return 2 * iNum
        
        return 0

    
    def GetMaxNumByItem(self, iItemID):
        import math
        oModel = self
        (iTodayTarget, iWeekTarget) = oModel.GetLastValue()
        oModel.GetSelectValue()
        iNowSelectValue = oModel.GetOneItemValue(iItemID, 1)
        iTarget = min(iTodayTarget, iWeekTarget) - oModel.GetSelectValue()
        return int(math.ceil(iTarget / iNowSelectValue))

    
    def IsValidItem(self, oItemObj):
        if oItemObj:
            iShape = oItemObj.GetShape()
            if iShape in itemdefine.ID_GEM_LIST:
                return True
            elif iShape == itemdefine.SHAPE_MSYJ:
                sExtName = oItemObj.GetExtName()
                if not sExtName and '\xb0\xaa\xaf\xc5' in sExtName:
                    pass
                return '\xb2\xd7\xaf\xc5' in sExtName
            
        
        return False
