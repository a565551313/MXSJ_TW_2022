# pycdc 交叉复核产物 · script.fls entry 4954
# co_filename(原始)='script/mxgame/activityreward/model/mdactivityreward.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4954.pyc (Python 2.5)

'''
\xbb\xee\xd4\xbe\xb6\xc8\xbd\xb1\xc0\xf8\xca\xfd\xbe\xdd
'''
import C_sys
import battlepassdata
import misc
import slot
import activityrewarddefine as define
import itemdefine
import hero
g_ActivityRewardMgr = None
g_BfWeekRewardMgr = None
g_BfTreasureChestMgr = None
g_ExchangeData = [
    {
        'shape': 73339,
        'rate': 0,
        'sid': 73336,
        'name': '\xa7\xa4\xc3M\xa1P\xa4\xd1\xabC\xbe\xa5\xa8\xf7',
        'getState': define.TYPE_REWARD_RECEIVE_NOT,
        'imsgid': 0 },
    {
        'shape': 26618,
        'rate': 15000,
        'sid': 73063,
        'name': '\xabC\xc0s\xb9F\xb0^',
        'getState': define.TYPE_REWARD_RECEIVE_NOT,
        'imsgid': 1 },
    {
        'shape': 73340,
        'rate': 0,
        'sid': 73337,
        'name': '\xaf\xcd\xbbH\xa1P\xaa\xe1\xbb\xb4\xa6p\xb9\xda',
        'getState': define.TYPE_REWARD_RECEIVE_NOT,
        'imsgid': 2 },
    {
        'shape': 73341,
        'rate': 0,
        'sid': 73338,
        'name': '\xaa\xe1\xbd\xba\xa4\xa7\xb4\xb9',
        'getState': define.TYPE_REWARD_RECEIVE_NOT,
        'imsgid': 3 }]

def ModuleReset():
    global g_ActivityRewardMgr, g_BfWeekRewardMgr, g_BfTreasureChestMgr, g_ExchangeData
    g_ActivityRewardMgr = None
    g_BfWeekRewardMgr = None
    g_BfTreasureChestMgr = None
    g_ExchangeData = []


def IsOpenActivityRewardMgr():
    import functionmgr
    return functionmgr.GetFuncMgr().CheckFuncIsOpenByStr('treasures')


def GetActivityRewardMgr():
    ''':rtype: CActivityRewardMgr'''
    global g_ActivityRewardMgr
    if not g_ActivityRewardMgr:
        g_ActivityRewardMgr = CActivityRewardMgr()
    
    return g_ActivityRewardMgr


def GetBfWeekRewardMgr():
    ''':rtype: CBfWeekRewardMgr'''
    global g_BfWeekRewardMgr
    if not g_BfWeekRewardMgr:
        g_BfWeekRewardMgr = CBfWeekRewardMgr()
    
    return g_BfWeekRewardMgr


def GetBfTreasureChestMgr():
    ''':rtype: CBfTreasureChestMgr'''
    global g_BfTreasureChestMgr
    if not g_BfTreasureChestMgr:
        g_BfTreasureChestMgr = CBfTreasureChestMgr()
    
    return g_BfTreasureChestMgr


def CalBPRedPoint():
    import mdpresentcenter
    iBPRedPoint = GetActivityRewardMgr().GetCanGetReward()
    if not GetActivityRewardMgr().SpecialCheckCenterShowRed():
        iBPRedPoint = 0
    
    iBPRedPoint += GetBfWeekRewardMgr().GetCanGetReward()
    if CheckTreasureCollectRedShow():
        iBPRedPoint += 1
    
    if GetMBLRecord().GetData() is None:
        iBPRedPoint += 1
    
    if GetBfTreasureChestMgr().GetShowSeasonEndRedDot():
        iBPRedPoint += 1
    
    if GetActivityRewardMgr().IsAlreadyShowRedDotToday():
        iBPRedPoint = 0
    
    if IsOpenActivityRewardMgr() and not GetActivityRewardMgr().IsInSeasonCD():
        mdpresentcenter.GetRedPointModel().SetPresentBattlePassShow(iBPRedPoint)
    


def CheckTreasureCollectRedShow():
    bShowRed = False
    oBfTreasureChestMgr = GetBfTreasureChestMgr()
    dBXData = oBfTreasureChestMgr.GetItem(itemdefine.ID_ITEM_BATTLE_BIG_TREASURE_CHEST)
    iBXNum = 0
    if dBXData:
        iBXNum = dBXData.GetCount()
    
    if iBXNum > 0:
        bShowRed = True
    
    return bShowRed


def GetItemType(iShape):
    if iShape in (itemdefine.ID_ITEM_BATTLE_SMALL_TREASURE_CHEST, itemdefine.ID_ITEM_BATTLE_BIG_TREASURE_CHEST, itemdefine.ID_ITEM_BATTLE_OPEN_TREASURE_CHEST):
        return define.TYPE_TREASURE_CHEST_TREASURE_CHEST
    elif iShape in (itemdefine.ID_ITEM_BATTLE_KEY_FRAGMENTATION, itemdefine.ID_ITEM_BATTLE_KEY):
        return define.TYPE_TREASURE_CHEST_MATERIAL
    elif iShape in (itemdefine.ID_ITEM_BATTLE_BADGE, itemdefine.ID_ITEM_BATTLE_ESSENCE):
        return define.TYPE_TREASURE_CHEST_FRAGMENTATION
    
    return define.TYPE_TREASURE_CHEST_FRAGMENTATION


def GetExChangeData():
    return g_ExchangeData


def GetExChangeRateByShape(iShape):
    for dData in g_ExchangeData:
        if dData['shape'] == iShape:
            return dData['rate']
            continue
    


def GetSidByShape(iShape):
    for dData in g_ExchangeData:
        if dData['shape'] == iShape:
            return dData['sid']
            continue
    


def SetRateByShape(sid, iRate):
    for dDate in g_ExchangeData:
        if dDate is None:
            continue
        
        if dDate['sid'] == sid:
            dDate['rate'] = iRate
            continue
    


def SetStateByShape(sid, iState):
    for dDate in g_ExchangeData:
        if dDate is None:
            continue
        
        if dDate['sid'] == sid:
            if dDate['islimit']:
                dDate['getState'] = iState
            else:
                dDate['extime'] = iState
        dDate['islimit']
    


def GetStateByShape(iShape):
    for dData in g_ExchangeData:
        if dData is None:
            continue
        
        if dData['shape'] == iShape:
            return dData['getState']
            continue
    
    return define.TYPE_REWARD_RECEIVE_NOT


def SetExchangeData(lExchangeData):
    global g_ExchangeData
    g_ExchangeData = lExchangeData


def GetAllMiBaoRewardListByGrade(iMaxGrade):
    tSpecList = []
    dSpecial = { }
    iSpeSortList = []
    iHighSortList = []
    tHighSortList = []
    for iGrade in xrange(1, iMaxGrade + 1):
        iSurShape = battlepassdata.GetSurShape(iGrade)
        iSurShape2 = battlepassdata.GetSurShape2(iGrade)
        if iSurShape:
            iSurCount = battlepassdata.GetSurCount(iGrade)
            if iSurShape not in dSpecial:
                dSpecial[iSurShape] = 0
                iSGPrice = battlepassdata.GetItemPrice(iSurShape)
                if iSGPrice > 0:
                    tHighSortList.append((iSurShape, iSGPrice))
                else:
                    iSpeSortList.append(iSurShape)
            
            dSpecial[iSurShape] += iSurCount
        
        if iSurShape2:
            iSurCount2 = battlepassdata.GetSurCount2(iGrade)
            if iSurShape2 not in dSpecial:
                dSpecial[iSurShape2] = 0
                iSGPrice = battlepassdata.GetItemPrice(iSurShape2)
                if iSGPrice > 0:
                    tHighSortList.append((iSurShape2, iSGPrice))
                else:
                    iSpeSortList.append(iSurShape2)
            
            dSpecial[iSurShape2] += iSurCount2
            continue
    
    tHighSortList.sort(key = (lambda x: x[1]), reverse = True)
    for tData in tHighSortList:
        iHighSortList.append(tData[0])
    
    for iShape in iHighSortList + iSpeSortList:
        iCount = dSpecial[iShape]
        tSpecList.append((iShape, iCount, battlepassdata.GetItemKey(iShape)))
    
    return tSpecList


class CActivityRewardMgr(slot.ISignalSubject):
    SS_UpdateActivityIntegral = 'UpdateActivityIntegral(iNowActivityIntegral)'
    SS_UpdateActivityGrade = 'UpdateActivityGrade(iActivityGrade, iAllActivityIntegral)'
    SS_UpdateAllReward = 'UpdateAllReward(dRewardData)'
    SS_UpdateOneReward = 'UpdateOneReward(iGradeList, dRewardData)'
    SS_UpdateQualification = 'UpdateQualification(iBuyOrdCount, iBuySurCount)'
    SS_UpdateLastTime = 'UpdateLastTime(iLastTime)'
    SS_UpdateLastEmptyTime = 'UpdateLastEmptyTime(iLastTime)'
    SS_UpdateLastKeyNum = 'UpdateLastKeyNum(iLastKeyNum)'
    SS_UpdateRedPoint = 'UpdateLastKeyNum(iLastKeyNum)'
    SS_UpdateEndTimeRedPoint = 'UpdateEndTimeRedPoint()'
    SS_UpdateOpenChildDlg = 'UpdateOpenChildDlg(sType)'
    SS_MiBaoLuGradeHint = 'SetMiBaoLuGradeHint(iType,iFlag)'
    SS_SessionFinish = 'OnSessionFinish()'
    SS_UpdateTodayExp = 'OnUpdateTodayExp()'
    
    def __init__(self):
        self.ssInit()
        self.m_iNowActivityIntegral = 0
        self.m_iNowAllActivityIntegral = 0
        self.m_iActivityGrade = 0
        self.m_iAllActivityIntegral = 0
        self.m_iLastKeyNum = 0
        self.m_iLastTime = misc.GetServerCurrentTime()
        self.m_iEmptyLastTime = misc.GetServerCurrentTime()
        self.m_dRewardData = { }
        self.m_iBuyOrdCount = 0
        self.m_iBuySurCount = 0
        self.m_iTodayExp = 0
        self.m_iMaxExp = 0
        self.m_sOpenClildDlg = None
        self.m_bIsInSeasonCD = False

    
    def IsInWaitSeasonCD(self):
        iLeftTime = self.m_iLastTime - misc.GetServerCurrentTime()
        iEmptyLeftTime = self.m_iEmptyLastTime - misc.GetServerCurrentTime()
        if iLeftTime < 0 and iEmptyLeftTime < 0:
            return True
        else:
            return False

    
    def IsEmptySeason(self):
        iLeftTime = self.m_iLastTime - misc.GetServerCurrentTime()
        iEmptyLeftTime = self.m_iEmptyLastTime - misc.GetServerCurrentTime()
        if iLeftTime < 0 and iEmptyLeftTime > 0:
            return True
        else:
            return False

    
    def CheckSessionState(self):
        if self.IsInSeasonCD():
            self.ssEmit(self.SS_SessionFinish)
        

    
    def UpdateEndTimeRedPoint(self):
        self.ssEmit(self.SS_UpdateEndTimeRedPoint)

    
    def SetActivityIntegral(self, iNowActivityIntegral):
        '''
\t\t\xb3]\xb8m\xb7\xed\xabe\xbfn\xa4\xc0\xabH\xae\xa7
\t\t:param int iNowActivityIntegral: \xbfn\xa4\xc0\xabH\xae\xa7
\t\t'''
        if iNowActivityIntegral == self.m_iNowActivityIntegral:
            return None
        
        self.m_iNowActivityIntegral = iNowActivityIntegral
        self.ssEmit(self.SS_UpdateActivityIntegral, iNowActivityIntegral)

    
    def GetActivityIntegral(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xbfn\xa4\xc0\xabH\xae\xa7
\t\t:rtype: int
\t\t'''
        return self.m_iNowActivityIntegral

    
    def SetTodayExp(self, iExp, iMaxExp):
        '''
\t\t\xb3]\xb8m\xb7\xed\xa4\xd1\xc0\xf2\xb1o\xaa\xba\xaf\xb5\xc4_\xb8g\xc5\xe7
\t\t:param iExp: int
\t\t:return:
\t\t'''
        self.m_iTodayExp = iExp
        self.m_iMaxExp = iMaxExp
        self.ssEmit(self.SS_UpdateTodayExp)

    
    def GetTodayExp(self):
        return self.m_iTodayExp

    
    def GetMaxExp(self):
        return self.m_iMaxExp

    
    def SetActivityGrade(self, iActivityGrade, iAllActivityIntegral):
        '''
\t\t\xb3]\xb8m\xb7\xed\xabe\xaa\xba\xbfn\xa4\xc0\xb5\xa5\xaf\xc5\xabH\xae\xa7
\t\t:param int iActivityGrade: \xb7\xed\xabe\xac\xa1\xc5D\xb5\xa5\xaf\xc5
\t\t:param int iAllActivityIntegral: \xb7\xed\xabe\xac\xa1\xc5D\xc1`\xbfn\xa4\xc0
\t\t'''
        if iActivityGrade == self.m_iActivityGrade and iAllActivityIntegral == self.m_iAllActivityIntegral:
            return None
        
        self.m_iActivityGrade = iActivityGrade
        self.m_iAllActivityIntegral = iAllActivityIntegral
        self.ssEmit(self.SS_UpdateActivityGrade, iActivityGrade, self.m_iAllActivityIntegral)

    
    def SetMiBaoLuGradeHint(self, iType, iFlag):
        self.ssEmit(self.SS_MiBaoLuGradeHint, iType, iFlag)

    
    def GetActivityGrade(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xbfn\xa4\xc0\xb5\xa5\xaf\xc5
\t\t:rtype: int
\t\t'''
        return self.m_iActivityGrade

    
    def GetAllActivityIntegral(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xc1`\xbfn\xa4\xc0
\t\t:rtype: int
\t\t'''
        return self.m_iAllActivityIntegral

    
    def GetNeedActivityIntegral(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xa4\xc9\xaf\xc5\xa9\xd2\xbb\xdd\xadn\xaa\xba\xbfn\xa4\xc0\xabH\xae\xa7
\t\t:rtype: int
\t\t'''
        iActivityGrade = self.GetActivityGrade()
        if iActivityGrade > 100:
            iActivityGrade = 101
        
        return battlepassdata.GetNextExp(iActivityGrade)

    
    def SetAllRewardData(self, dRewardData):
        '''
\t\t\xb3]\xb8m\xbc\xfa\xc0y\xaa\xba\xbb\xe2\xa8\xfa\xabH\xae\xa7
\t\t:param dRewardData: \xbc\xfa\xc0y\xa6r\xa8\xe5
\t\t'''
        self.m_dRewardData = dRewardData
        self.ssEmit(self.SS_UpdateAllReward, dRewardData)

    
    def GetAllRewardData(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa9\xd2\xa6\xb3\xaa\xba\xbc\xfa\xc0y\xabH\xae\xa7
\t\t:rtype: dict
\t\t'''
        return self.m_dRewardData

    
    def SetGradeRewardData(self, iGradeList, dRewardData):
        '''
\t\t\xb3]\xb8m\xb3\xa1\xa4\xc0\xbc\xfa\xc0y\xabH\xae\xa7
\t\t:param list[int] iGradeList: \xa9\xd2\xad\xd7\xa7\xef\xaa\xba\xbc\xfa\xc0y\xb5\xa5\xaf\xc5\xa6C\xaa\xed
\t\t:param dict dRewardData: \xa9\xd2\xad\xd7\xa7\xef\xaa\xba\xabH\xae\xa7
\t\t'''
        self.m_dRewardData.update(dRewardData)
        CalBPRedPoint()
        self.ssEmit(self.SS_UpdateOneReward, iGradeList, dRewardData)

    
    def GetGradeRewardData(self, iGrade):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xb5\xa5\xaf\xc5\xa4U\xbc\xfa\xc0y\xbb\xe2\xa8\xfa\xabH\xae\xa7
\t\t:param int iGrade: \xbfn\xa4\xc0\xb5\xa5\xaf\xc5
\t\t:rtype: dict
\t\t'''
        return self.m_dRewardData.get(iGrade, { })

    
    def GetCanGetReward(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa5i\xa5H\xbb\xe2\xa8\xfa\xaa\xba\xbc\xfa\xc0y\xbc\xc6\xa5\xd8
\t\t:rtype: in\twtt\xd9\xa3\xd8\xb3\xdc:wtt\xbd\xc5\xd6\x18\xc7\xa0P\xc4\xa7\xca,P\xd07\xd7\x9f\xd71UIOLET]OMLDPHPE]L6:50:38
\t\t\xa5\xfd\xbdT\xbb{\xa4U\xa1G 101\xaf\xc5\xaa\xba\xbc\xfa\xc0y\xacO\xa7_\xa5u\xa6\xb3\xc6_\xb0\xcd\xa1H \xa6p\xaaG\xacO\xab\xc8\xa4\xe1\xba\xdd\xafS\xae\xed\xb3B\xb2z \xa5h\xb1\xbc101 \xaf\xc5\xaa\xba\xadp\xbc\xc6 \xa7Y\xa5i\xb8\xd1\xa8M\xb0\xdd\xc3D@\xacx\xa5\xfa\xbaa;@\xa7\xf5\xae\xda;
\t\t\xb9C\xc0\xb8\xab\xe1\xba\xdd-\xb9\xda\xb7Q-\xacx\xa5\xfa\xbaa(8807) 2019-5-8 16:51:02
\t\t101\xaf\xc5\xa5u\xb7|\xbb\xe2\xa8\xfa\xc6_\xb0\xcd
\t\t1.\xadp\xbc\xc6\xa1G \xb5\xa5\xaf\xc5\xaa\xac\xbaA+ \xc6_\xb0\xcd\xbc\xfa\xc0y
\t\t101\xaf\xc5 \xaa\xba\xbc\xfa\xc0y \xa5u\xb7|\xa6\xb3\xc6_\xb0\xcd \xac\xb0\xa4F\xc1\xd7\xa7K\xad\xab\xbd\xc6\xadp\xbc\xc6101 \xaf\xc5\xb8\xf5\xb9L\xaa\xac\xbaA\xadp\xbc\xc6
\t\t'''
        iCanGetReward = 0
        dAllRewardData = self.GetAllRewardData()
        for nGrade, dInfo in dAllRewardData.iteritems():
            if nGrade == 101:
                continue
            
            for iType in (define.TYPE_REWARD_ORD, define.TYPE_REWARD_SUR):
                if dInfo.get(iType, { }).get(define.KEY_REWARD_TYPE, None) == define.TYPE_REWARD_RECEIVE_ING:
                    if iType == define.TYPE_REWARD_ORD:
                        if battlepassdata.GetOrdShape(nGrade):
                            iCanGetReward += 1
                        
                    elif battlepassdata.GetSurShape(nGrade):
                        iCanGetReward += 1
                    
                    if battlepassdata.GetSurShape2(nGrade):
                        iCanGetReward += 1
                    
                battlepassdata.GetSurShape2(nGrade)
            
        
        if self.m_iBuyOrdCount and self.GetLastKeyNum():
            iCanGetReward += 1
        
        return iCanGetReward

    
    def IsAlreadyShowRedDotToday(self):
        '''
\t\t\xaa\xf0\xa6^\xa4\xb5\xa4\xe9\xaf\xb5\xc4_\xbf\xfd\xac\xf5\xc2I\xacO\xa7_\xa4w\xb8g\xc5\xe3\xa5\xdc\xb9L\xa4F
\t\t:return:
\t\t'''
        import time
        import mdpresentcenter
        iLastTime = mdpresentcenter.GetRedPointModel().GetLastPresentBattlePassRemoveTime()
        if not iLastTime:
            return False
        
        tLastDay = time.localtime(iLastTime)
        tToday = time.localtime(misc.GetServerCurrentTime())
        if tToday[0] == tLastDay[0] and tToday[1] == tLastDay[1]:
            pass
        return tToday[2] == tLastDay[2]

    
    def SpecialCheckCenterShowRed(self):
        '''
\t\t\xbc\xfa\xc0y\xa4\xa4\xa4\xdf\xac\xf5\xc2I\xbcW\xa5[\xa7P\xc2_
\t\t:rtype: bool\tTrue:\xbc\xfa\xc0y\xa4\xa4\xa4\xdf\xc5\xe3\xa5\xdc\xac\xf5\xc2I\xa1AFalse:\xa4\xa3\xc5\xe3
\t\t'''
        if self.m_iActivityGrade > 100:
            return False
        elif self.m_iActivityGrade % 5 == 0:
            return True
        elif self.GetBuyQualification() and self.GetCanGetReward() >= 10:
            return True
        elif not self.GetBuyQualification() and self.GetCanGetReward() >= 5:
            return True
        
        return False

    
    def SetQualification(self, iBuyOrdCount, iBuySurCount):
        '''
\t\t\xb3]\xb8m\xa4w\xb8g\xc1\xca\xb6R\xb8\xea\xae\xe6\xaa\xba\xbc\xc6\xa5\xd8
\t\t:param int iBuyOrdCount: \xb4\xb6\xb3q\xb8\xea\xae\xe6\xbc\xc6\xa5\xd8
\t\t:param int iBuySurCount: \xb6W\xaf\xc5\xb8\xea\xae\xe6\xbc\xc6\xa5\xd8
\t\t'''
        if iBuyOrdCount == self.m_iBuyOrdCount and iBuySurCount == self.m_iBuySurCount:
            return None
        
        self.m_iBuyOrdCount = iBuyOrdCount
        self.m_iBuySurCount = iBuySurCount
        self.ssEmit(self.SS_UpdateQualification, iBuyOrdCount, iBuySurCount)

    
    def GetBuyOrdQualification(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb4\xb6\xb3q\xb8\xea\xae\xe6\xbc\xc6\xa5\xd8
\t\t:rtype: int
\t\t'''
        return self.m_iBuyOrdCount

    
    def GetBuySurQualification(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb6W\xaf\xc5\xb8\xea\xae\xe6\xbc\xc6\xa5\xd8
\t\t:rtype: int
\t\t'''
        return self.m_iBuySurCount

    
    def GetBuyQualification(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb8\xea\xae\xe6\xbc\xc6\xa5\xd8
\t\t:rtype: int
\t\t'''
        return self.m_iBuyOrdCount

    
    def SetEmptyLastTime(self, iTime):
        if self.m_iEmptyLastTime == iTime:
            return None
        
        self.m_iEmptyLastTime = iTime
        self.ssEmit(self.SS_UpdateLastEmptyTime, iTime)

    
    def SetLastTime(self, iTime):
        '''
\t\t\xb3]\xb8m\xb3\xd1\xbel\xae\xc9\xb6\xa1\xc2W
\t\t:param int iTime: \xae\xc9\xb6\xa1\xc2W \xaaA\xb0\xc8\xbe\xb9\xae\xc9\xb6\xa1
\t\t'''
        if self.m_iLastTime == iTime:
            return None
        
        self.m_iLastTime = iTime
        self.ssEmit(self.SS_UpdateLastTime, iTime)

    
    def GetLastTime(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb3\xd1\xbel\xae\xc9\xb6\xa1
\t\t:rtype: int
\t\t'''
        return self.m_iLastTime - misc.GetServerCurrentTime()

    
    def IsOpenBattlePass(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xac\xa1\xb0\xca\xacO\xa7_\xb6}\xb1\xd2
\t\t:rtype: bool
\t\t'''
        return self.GetLastTime() > 0

    
    def SetLastKeyNum(self, iLastKeyNum):
        '''
\t\t\xb3]\xb8m\xb3\xd1\xbel\xa5i\xbb\xe2\xa8\xfa\xaa\xba\xc6_\xb0\xcd\xc1`\xbc\xc6
\t\t:param int iLastKeyNum: \xb3\xd1\xbel\xa5i\xbb\xe2\xa8\xfa\xaa\xba\xc6_\xb0\xcd\xc1`\xbc\xc6
\t\t'''
        self.m_iLastKeyNum = iLastKeyNum
        CalBPRedPoint()
        self.ssEmit(self.SS_UpdateLastKeyNum, iLastKeyNum)

    
    def GetOwnKeyNum(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa4w\xb8g\xbb\xe2\xa8\xfa\xaa\xba\xc6_\xb0\xcd\xc1`\xbc\xc6
\t\t'''
        return self.m_iLastKeyNum

    
    def GetLastKeyNum(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xb3\xd1\xbel\xa5i\xbb\xe2\xa8\xfa\xaa\xba\xc6_\xb0\xcd\xc1`\xbc\xc6
\t\t:rtype: int
\t\t'''
        return max(self.GetActivityGrade() - 100 - self.m_iLastKeyNum, 0)

    
    def SetClildDlgType(self, sType):
        '''
\t\t\xb3]\xb8m\xa5\xb4\xb6}\xaa\xba\xa4l\xac\xc9\xad\xb1\xabH\xae\xa7
\t\t\xa4\xa3\xa5\xce\xa6s\xbc\xc6\xbe\xda\xc2\xe0\xb5o\xb4N\xa6\xe6
\t\t'''
        self.m_sOpenClildDlg = sType
        self.ssEmit(self.SS_UpdateOpenChildDlg, sType)

    
    def ClearClildDlgType(self):
        '''
\t\t\xb2M\xb2z\xa4\xa3\xb5o\xabH\xb8\xb9
\t\t'''
        self.m_sOpenClildDlg = None

    
    def GetClildDlgType(self):
        return self.m_sOpenClildDlg

    
    def GetAttLevelNeedIntegral(self, iNeedLv):
        iNeedIntegral = 0
        for iLv, dInfo in battlepassdata.GRADE_DATA.iteritems():
            if iLv >= iNeedLv:
                break
            
            iNeedIntegral += dInfo['iNextExp']
        
        return iNeedIntegral - self.GetAllActivityIntegral()



class CBfWeekRewardMgr(slot.ISignalSubject):
    SS_UpdateHaveTaskNum = 'UpdateHaveTaskNum(iHaveTaskNum)'
    SS_UpdateMainRewardGetType = 'UpdateMainRewardGetType(iMainRewardGetType)'
    SS_UpdateWeekRewardData = 'UpdateWeekRewardData(iTaskList, dRewardData)'
    SS_UpdateMiBaoExp = 'UpdateMiBaoExp(iExp)'
    SS_UpdateWeekRewardItem = "UpdateWeekRewardItem(iShape, iAmount)'"
    
    def __init__(self):
        self.ssInit()
        self.m_iHaveTaskNum = 0
        self.m_iMainRewardGetType = define.TYPE_REWARD_RECEIVE_NOT
        self.m_dWeekRewardData = { }
        self.m_iWaitForCollectionMBExp = 0
        self.m_iShape = 0
        self.m_iAmount = 0

    
    def SetHaveTaskNum(self, iHaveTaskNum):
        '''
\t\t\xb3]\xb8m\xb7\xed\xabe\xa7\xb9\xa6\xa8\xa5\xf4\xb0\xc8\xaa\xba\xc1`\xbc\xc6
\t\t:param int iHaveTaskNum: \xa5\xf4\xb0\xc8\xaa\xba\xc1`\xbc\xc6
\t\t'''
        if iHaveTaskNum == self.m_iHaveTaskNum:
            return None
        
        self.m_iHaveTaskNum = iHaveTaskNum
        self.ssEmit(self.SS_UpdateHaveTaskNum, iHaveTaskNum)

    
    def GetHaveTaskNum(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa7\xb9\xa6\xa8\xa5\xf4\xb0\xc8\xaa\xba\xc1`\xbc\xc6
\t\t:rtype: int
\t\t'''
        return self.m_iHaveTaskNum

    
    def SetMainRewardGetType(self, iMainRewardGetType):
        '''
\t\t\xb3]\xb8m\xb7\xed\xabe\xaa\xba\xbfn\xa4\xc0\xb5\xa5\xaf\xc5\xabH\xae\xa7
\t\t:param int iMainRewardGetType: \xb7\xed\xabe\xac\xa1\xc5D\xb5\xa5\xaf\xc5
\t\t'''
        if iMainRewardGetType == self.m_iMainRewardGetType:
            return None
        
        self.m_iMainRewardGetType = iMainRewardGetType
        CalBPRedPoint()
        self.ssEmit(self.SS_UpdateMainRewardGetType, iMainRewardGetType)

    
    def GetMainRewardGetType(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xbfn\xa4\xc0\xb5\xa5\xaf\xc5
\t\t:rtype: int
\t\t'''
        return self.m_iMainRewardGetType

    
    def SetWeekRewardItemInfo(self, iShape, iAmount):
        self.m_iShape = iShape
        self.m_iAmount = iAmount
        self.ssEmit(self.SS_UpdateWeekRewardItem, iShape, iAmount)

    
    def GetWeekRewardItemInfo(self):
        return (self.m_iShape, self.m_iAmount)

    
    def SetTaskRewardData(self, iTaskList, dRewardData):
        '''
\t\t\xb3]\xb8m\xb3\xa1\xa4\xc0\xbc\xfa\xc0y\xabH\xae\xa7
\t\t:param list[int] iTaskList: \xa9\xd2\xad\xd7\xa7\xef\xaa\xba\xbc\xfa\xc0y\xa5\xf4\xb0\xc8\xa6C\xaa\xed
\t\t:param dict dRewardData: \xa9\xd2\xad\xd7\xa7\xef\xaa\xba\xabH\xae\xa7
\t\t'''
        self.m_dWeekRewardData.update(dRewardData)
        CalBPRedPoint()
        self.ssEmit(self.SS_UpdateWeekRewardData, iTaskList, dRewardData)

    
    def ClearTaskRewardData(self):
        '''
\t\t\xb2M\xaa\xc5\xa5\xfe\xb3\xa1\xa5\xf4\xb0\xc8\xabH\xae\xa7
\t\t'''
        self.m_dWeekRewardData = { }

    
    def GetTaskRewardData(self, iTaskID):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xb5\xa5\xaf\xc5\xa4U\xbc\xfa\xc0y\xbb\xe2\xa8\xfa\xabH\xae\xa7
\t\t:param int iTaskID: \xbfn\xa4\xc0\xb5\xa5\xaf\xc5
\t\t:rtype: dict or None
\t\t'''
        return self.m_dWeekRewardData.get(iTaskID, None)

    
    def GetAllTaskIDList(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa5\xf4\xb0\xc8\xaa\xba\xa6C\xaa\xed
\t\t:rtype: list[int]
\t\t'''
        return self.m_dWeekRewardData.keys()

    
    def GetAllTaskData(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xa9\xd2\xa6\xb3\xaa\xba\xa5\xf4\xb0\xc8\xabH\xae\xa7
\t\t:rtype: dict
\t\t'''
        return self.m_dWeekRewardData

    
    def GetCanGetReward(self):
        iCanGetReward = 0
        if hero.GetProp('m_Grade') < 30:
            return iCanGetReward
        
        dAllTaskData = self.GetAllTaskData()
        for _, dInfo in dAllTaskData.iteritems():
            if dInfo.get(define.KEY_REWARD_TYPE) == define.TYPE_REWARD_RECEIVE_ING:
                iCanGetReward += 1
                continue
        
        if self.GetMainRewardGetType() == define.TYPE_REWARD_RECEIVE_ING:
            iCanGetReward += 1
        
        import mdseasonchallenge
        oChallengeModel = mdseasonchallenge.GetSeasonChallengeModel()
        if oChallengeModel.GetRewardFlag():
            iCanGetReward += oChallengeModel.GetRewardNum()
        
        return iCanGetReward

    
    def SetMiBaoExp(self, iExp):
        self.m_iWaitForCollectionMBExp = iExp
        self.ssEmit(self.SS_UpdateMiBaoExp, iExp)

    
    def GetMiBaoExp(self):
        return self.m_iWaitForCollectionMBExp



class CBfTreasureChestMgr(slot.ISignalSubject):
    SS_UpdateAddItem = 'UpdateMateria(iType, iItemID, iCount)'
    SS_UpdateChangeItem = 'UpdateChangeItem(iItemID, iCount)'
    SS_UpdateAddItemRedDot = 'UpdateAddItemRedDot(iItemID, iCount, iLastCount)'
    SS_UpdateGetItemDict = 'UpdateGetItemDict(iItemList)'
    SS_UpdateSelectItemID = 'UpdateSelectItemID(iItemID)'
    SS_UpdateRewardData = 'UpdateRewardData()'
    SS_UpdateRewardState = 'UpdateRewardState()'
    SS_SeasonEndRedDotChg = 'SeasonEndRedDotChg(bShow)'
    SS_UpdateAllRewardData = 'UpdateAllRewardData()'
    
    def __init__(self):
        self.ssInit()
        self.m_dMaterialDict = set([])
        self.m_dTreasureChestDict = set()
        self.m_dFragmentationDict = set([])
        self.m_dItemData = { }
        self.m_iSelectItemID = 0
        self.m_bIsHaveRedDot = False
        self.m_bShowSeasonEndRedDot = False
        self.CreateVirItem()

    
    def GetShowSeasonEndRedDot(self):
        return self.m_bShowSeasonEndRedDot

    
    def SetShowSessionEndRedDot(self, bShowSeasonEndRedDot):
        self.m_bShowSeasonEndRedDot = bShowSeasonEndRedDot
        self.ssEmit(self.SS_SeasonEndRedDotChg, bShowSeasonEndRedDot)

    
    def SetHaveRedDot(self, bIsHaveRedDot):
        self.m_bIsHaveRedDot = bIsHaveRedDot
        CalBPRedPoint()

    
    def GetHaveRedDot(self):
        return self.m_bIsHaveRedDot

    
    def CreateVirItem(self):
        for iShape in battlepassdata.GetAllGoodsShapeData().iterkeys():
            self.AddAItem(iShape, 0, True)
        

    
    def GetCanGetReward(self):
        if self.GetHaveRedDot():
            return 1
        else:
            return 0

    
    def AddAItem(self, iItemID, iCount, bIsLoading):
        '''
\t\t\xb2K\xa5[\xa4@\xad\xd3\xb9D\xa8\xe3
\t\t:param int iItemID: \xaa\xab\xab~ID
\t\t:param int iCount: \xaa\xab\xab~\xbc\xc6\xb6q
\t\t'''
        iItemType = GetItemType(iItemID)
        if iItemType is None:
            return None
        
        oItem = CTreasureChestItem(iItemType, iItemID)
        oItem.SetCount(iCount)
        self.m_dItemData[iItemID] = oItem
        if iItemType == define.TYPE_TREASURE_CHEST_MATERIAL:
            self.m_dMaterialDict.add(iItemID)
        elif iItemType == define.TYPE_TREASURE_CHEST_TREASURE_CHEST:
            self.m_dTreasureChestDict.add(iItemID)
        elif iItemType == define.TYPE_TREASURE_CHEST_FRAGMENTATION:
            self.m_dFragmentationDict.add(iItemID)
        
        if not bIsLoading:
            oItem.SetOldCount(0)
        
        self.ssEmit(self.SS_UpdateAddItem, iItemType, iItemID, iCount)
        if iCount and not bIsLoading:
            self.SetHaveRedDot(True)
            self.ssEmit(self.SS_UpdateAddItemRedDot, iItemID, iCount, 0)
        

    
    def ChangeItem(self, iItemID, iCount, bIsLoading):
        '''
\t\t\xa7\xef\xc5\xdc\xa4@\xad\xd3\xb9D\xa8\xe3\xaa\xba\xbc\xc6\xb6q
\t\t:param int iItemID: \xaa\xab\xab~ID
\t\t:param int iCount: \xaa\xab\xab~\xbc\xc6\xb6q
\t\t:param bool bIsLoading: \xacO\xa7_\xacO\xb5n\xbf\xfd\xaa\xac\xbaA\xb5o\xaa\xba
\t\t'''
        oItem = self.GetItem(iItemID)
        CalBPRedPoint()
        if not oItem:
            self.AddAItem(iItemID, iCount, bIsLoading)
            return None
        
        iLastCount = oItem.GetCount()
        if not bIsLoading:
            oItem.SetOldCount(iLastCount)
        
        oItem.SetCount(iCount)
        self.ssEmit(self.SS_UpdateChangeItem, iItemID, iCount)
        if iCount > iLastCount and not bIsLoading:
            self.SetHaveRedDot(True)
            self.ssEmit(self.SS_UpdateAddItemRedDot, iItemID, iCount, iLastCount)
        

    
    def GetItem(self, iItemID):
        '''
\t\t\xc0\xf2\xa8\xfa\xaa\xab\xab~
\t\t:param int iItemID: \xaa\xab\xab~ID
\t\t:rtype: CTreasureChestItem
\t\t'''
        return self.m_dItemData.get(iItemID, None)

    
    def GetMaterial(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xa7\xf7\xae\xc6\xabH\xae\xa7
\t\t'''
        return self.m_dMaterialDict

    
    def GetTreasureChest(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xc4_\xbdc\xabH\xae\xa7
\t\t'''
        return self.m_dTreasureChestDict

    
    def GetFragmentation(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xaa\xba\xb8H\xa4\xf9\xabH\xae\xa7
\t\t'''
        return self.m_dFragmentationDict

    
    def SetSelectItem(self, iItemID):
        '''
\t\t\xbf\xef\xbe\xdc\xa4@\xad\xd3\xb9D\xa8\xe3
\t\t:param int iItemID: \xb9D\xa8\xe3ID
\t\t'''
        self.m_iSelectItemID = iItemID
        self.ssEmit(self.SS_UpdateSelectItemID, iItemID)

    
    def GetSelectItem(self):
        return self.m_iSelectItemID

    
    def SetGetItemDict(self, iItemList):
        self.ssEmit(self.SS_UpdateGetItemDict, iItemList)

    
    def RefreshRewardItemData(self, iShape, sDesc):
        self.ssEmit(self.SS_UpdateRewardData, iShape, sDesc)

    
    def RefreshRewardIconState(self):
        self.ssEmit(self.SS_UpdateRewardState)

    
    def RefreshAllReward(self):
        self.ssEmit(self.SS_UpdateAllRewardData)



class CTreasureChestItem(object):
    '''
\t\xb9D\xa8\xe3\xc3\xfe\xa1A\xa4\xe8\xabK\xa5H\xab\xe1\xc2X\xaei
\t'''
    
    def __init__(self, iType, iItemID):
        self.m_iType = iType
        self.m_iItemShape = iItemID
        self.m_iCount = 1
        self.m_iOldCount = None

    
    def GetType(self):
        return self.m_iType

    
    def SetCount(self, iCount):
        self.m_iCount = iCount

    
    def SetOldCount(self, iCount):
        self.m_iOldCount = iCount

    
    def GetCount(self):
        return self.m_iCount

    
    def GetOldCount(self):
        return self.m_iOldCount


g_RecordMgr = None

def GetMBLRecord():
    ''':rtype: CServerBattleRankMgr'''
    global g_RecordMgr
    if not g_RecordMgr:
        g_RecordMgr = CMBLRecord()
    
    return g_RecordMgr


class CMBLRecord(object):
    S_DICKEY = 'mx-mblhd-%d'
    
    def __init__(self):
        self.m_dicRecord = None

    
    def GetData(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xac\xf5\xc2I\xaa\xba\xc2I\xc0\xbb\xaa\xac\xbaA
\t\t:return:
\t\t'''
        import cfg
        strKey = self.S_DICKEY % self.GetPlayerRealId()
        state = cfg.GetData('users/%d.ini' % self.GetPlayerRealId(), 'Game', strKey)
        if self.CheckDateIsEnd():
            return 1
        
        return state

    
    def SaveData(self):
        import cfg
        strKey = self.S_DICKEY % self.GetPlayerRealId()
        cfg.SaveData('users/%d.ini' % self.GetPlayerRealId(), 'Game', strKey, 1)

    
    def GetPlayerRealId(self):
        import hero
        iRealId = hero.GetRealID()
        if iRealId is None:
            iRealId = 0
        
        return iRealId

    
    def CheckDateIsEnd(self):
        '''
\t\t\xaf\xb5\xc4_\xbf\xfd\xc1\xc9\xa9u\xb5\xb2\xa7\xf4\xa4\xa7\xab\xe1\xb5L\xbb\xdd\xac\xf5\xc2I\xb4\xa3\xbf\xf4
\t\t:return:
\t\t'''
        import time
        import misc
        start = (2019, 10, 10, 8, 30, 0, 0, 0, 0)
        return time.mktime(start) < misc.GetServerCurrentTime()
