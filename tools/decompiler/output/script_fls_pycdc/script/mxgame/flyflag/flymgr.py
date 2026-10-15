# pycdc 交叉复核产物 · script.fls entry 3718
# co_filename(原始)='script/mxgame/flyflag/flymgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3718.pyc (Python 2.5)

import autocm_new
import slot
import netfly
import usermacro
g_FlyMgr = None
DEFAULT_POS_DATA = {
    1025: {
        'tPos': (93, 85),
        'sDesc': '\xb2M\xad\xb7\xa7\xf8' },
    1054: {
        'tPos': (157, 117),
        'sDesc': '\xa9\xfa\xa4\xeb\xab\xb0' },
    1008: {
        'tPos': (128, 51),
        'sDesc': '\xaa\xda\xaf\xf3\xc2\xed' },
    1014: {
        'tPos': (57, 46),
        'sDesc': '\xb6\xb3\xb3\xb6\xa8\xa6' },
    1001: {
        'tPos': (72, 37),
        'sDesc': '\xa5\xc3\xbfA\xab\xb0' },
    1007: {
        'tPos': (56, 44),
        'sDesc': '\xad\xbb\xb8\xad\xab\xb0' },
    1013: {
        'tPos': (72, 50),
        'sDesc': '\xa4\xd1\xbba\xab\xb0' },
    1019: {
        'tPos': (60, 38),
        'sDesc': '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5' },
    1026: {
        'tPos': (27, 33),
        'sDesc': '\xbe\xa4\xa9\xfa\xc2\xed' },
    1027: {
        'tPos': (49, 27),
        'sDesc': '\xa9]\xb9\xf5\xc2\xed' } }
SAME_DISTANCE_SCENE_NAME = [
    '\xa5\xc3\xbfA\xab\xb0',
    '\xad\xbb\xb8\xad\xab\xb0',
    '\xa4\xd1\xbba\xab\xb0',
    '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5']
AUTOCM_BAN_TIPS = '\xa6\xdb\xb0\xca\xb0\xa3\xc5]\xa4\xa4\xb8T\xa4\xee\xad\xb8\xa6\xe6'
countryId2Pos = {
    1: 1001,
    2: 1007,
    3: 1013,
    4: 1019 }
Country2King = {
    1: ('\xabn\xbb\xbb\xb0\xea\xa4\xfd', 1, '\xa5\xc3\xbfA\xab\xb0', 113, 63, 0),
    2: ('\xa4\xd1\xb9\xe7\xb0\xea\xa4\xfd', 1, '\xad\xbb\xb8\xad\xab\xb0', 102, 63, 0),
    3: ('\xb2M\xb4P\xb0\xea\xa4\xfd', 1, '\xa4\xd1\xbba\xab\xb0', 110, 75, 0),
    4: ('\xa5[\xac\xa5\xb0\xea\xa4\xfd', 1, '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5', 114, 70, 0) }
COUNTRY_POS_DATA = {
    1001: {
        'tPos': (56, 82),
        'sDesc': '\xa5\xc3\xbfA\xab\xb0' },
    1007: {
        'tPos': (55, 81),
        'sDesc': '\xad\xbb\xb8\xad\xab\xb0' },
    1013: {
        'tPos': (62, 77),
        'sDesc': '\xa4\xd1\xbba\xab\xb0' },
    1019: {
        'tPos': (65, 71),
        'sDesc': '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5' } }
DEFAULT_FLY_POS = {
    1025: [
        (93, 85),
        (172, 18),
        (180, 140)],
    1054: [
        (10, 22),
        (96, 95),
        (228, 63),
        (223, 161),
        (297, 108),
        (157, 117),
        (341, 226),
        (160, 185)],
    1008: [
        (128, 51),
        (41, 106),
        (139, 6)],
    1014: [
        (57, 46),
        (13, 108)],
    1001: [
        (72, 37)],
    1007: [
        (56, 44)],
    1013: [
        (72, 50)],
    1019: [
        (60, 38)],
    1026: [
        (27, 33)],
    1027: [
        (49, 27)] }
GROUP_FLY_POS = (63, 44)
GROUP_SCENE_ID = 0
DEFAULT_SWITCH_POS = {
    1025: [
        (186, 114),
        (179, 7)],
    1054: [
        (10, 22),
        (342, 224),
        (212, 29)],
    1008: [
        (35, 112),
        (144, 3)],
    1014: [
        (9, 114)],
    1001: [
        (8, 5),
        (127, 15)],
    1007: [
        (10, 8),
        (129, 24)],
    1013: [
        (5, 14),
        (128, 16)],
    1019: [
        (18, 18),
        (126, 15)],
    1026: [
        (6, 5),
        (8, 84),
        (27, 33)],
    1027: [
        (110, 4),
        (117, 86),
        (49, 27)] }
KUAFU2NORMAL = {
    1181: 1014,
    1182: 1004,
    1183: 1008,
    1184: 1022,
    1185: 1005,
    1186: 1018,
    1126: 1025,
    1154: 1054,
    1196: 1023,
    1197: 1012,
    1198: 1029,
    1199: 1030,
    1200: 1032,
    1201: 1033,
    1202: 1034,
    1203: 1035,
    1204: 1158,
    1205: 1159,
    1206: 1176,
    1207: 1177,
    1208: 1194,
    1209: 1026,
    1222: 1027,
    1223: 1157,
    1411: 1005,
    1412: 1054,
    1413: 1018,
    1414: 1023,
    1415: 1012,
    1416: 1029,
    1417: 1027,
    1421: 1005,
    1422: 1054,
    1423: 1018,
    1424: 1023,
    1425: 1012,
    1426: 1029,
    1427: 1027,
    1431: 1005,
    1432: 1054,
    1433: 1018,
    1434: 1023,
    1435: 1012,
    1436: 1029,
    1437: 1027,
    1441: 1005,
    1442: 1054,
    1443: 1018,
    1444: 1023,
    1445: 1012,
    1446: 1029,
    1447: 1027,
    1451: 1005,
    1452: 1054,
    1453: 1018,
    1454: 1023,
    1455: 1012,
    1456: 1029,
    1457: 1027 }
KUAFU2NAME = {
    1411: '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec1',
    1412: '\xa9\xfa\xa4\xeb\xab\xb01',
    1413: '\xa4\xd3\xae\xa7\xaaL\xa6a1',
    1414: '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa41',
    1415: '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL1',
    1416: '\xafe\xad\xb7\xa8\xa61',
    1417: '\xa9]\xb9\xf5\xc2\xed1',
    1421: '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec2',
    1422: '\xa9\xfa\xa4\xeb\xab\xb02',
    1423: '\xa4\xd3\xae\xa7\xaaL\xa6a2',
    1424: '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa42',
    1425: '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL2',
    1426: '\xafe\xad\xb7\xa8\xa62',
    1427: '\xa9]\xb9\xf5\xc2\xed2',
    1431: '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec3',
    1432: '\xa9\xfa\xa4\xeb\xab\xb03',
    1433: '\xa4\xd3\xae\xa7\xaaL\xa6a3',
    1434: '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa43',
    1435: '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL3',
    1436: '\xafe\xad\xb7\xa8\xa63',
    1437: '\xa9]\xb9\xf5\xc2\xed3',
    1441: '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec4',
    1442: '\xa9\xfa\xa4\xeb\xab\xb04',
    1443: '\xa4\xd3\xae\xa7\xaaL\xa6a4',
    1444: '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa44',
    1445: '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL4',
    1446: '\xafe\xad\xb7\xa8\xa64',
    1447: '\xa9]\xb9\xf5\xc2\xed4',
    1451: '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec5',
    1452: '\xa9\xfa\xa4\xeb\xab\xb05',
    1453: '\xa4\xd3\xae\xa7\xaaL\xa6a5',
    1454: '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa45',
    1455: '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL5',
    1456: '\xafe\xad\xb7\xa8\xa65',
    1457: '\xa9]\xb9\xf5\xc2\xed5' }
Zhi_Yie_Npc = {
    4: {
        1: '\xae\xfc\xa4\xdf',
        2: '\xacx\xae\xf6',
        0: '\xa5\xf1\xaai' },
    1: {
        1: '\xa5\xf4\xb2z',
        2: '\xb8\xca\xb8q',
        0: '\xb1L\xb4\xbc\xabH' },
    3: {
        1: '\xabn\xaa\xf8\xb6\xb3',
        2: '\xc3\xfa\xc5r',
        0: '\xa4\xda\xaf\xba\xa4\xd1' },
    2: {
        1: '\xa4\xec\xbcv',
        2: '\xa4\xec\xc6L',
        0: '\xaaQ\xc0\xdc' } }
ADD_DURABLE = 40
FULL_DURABLE = 500
FULL_FYL_POINT = 60
MAX_RECORD_NUM = 12
MAX_SCENE_NUM = 10
INI_SHOWNPC = 'FlyDlgShowNpc'

def ModuleReset():
    global g_FlyMgr
    g_FlyMgr = None


def GetMgr():
    global g_FlyMgr
    if not g_FlyMgr:
        g_FlyMgr = CFlyPosMgr()
    
    return g_FlyMgr


def GetKingConfig():
    import hero
    iCountry = hero.GetProp('m_Country')
    return Country2King.get(iCountry, None)


def GetZhiYeNpcName():
    import hero
    iCountry = hero.GetProp('m_Country')
    iClass = hero.GetProp('m_Class')
    return Zhi_Yie_Npc.get(iCountry, { }).get(iClass, None)


def GetAirportPosByID(iSceneID):
    if iSceneID in DEFAULT_POS_DATA:
        return DEFAULT_POS_DATA[iSceneID]['tPos']
    
    return (0, 0)


def GetAirportPosByName(sSceneName):
    for tInfo in DEFAULT_POS_DATA.values():
        if tInfo['sDesc'] == sSceneName:
            return tInfo['tPos']
            continue
    
    return (0, 0)


def GetDefaultFlyPosListByID(iSceneID):
    if iSceneID in DEFAULT_FLY_POS:
        return DEFAULT_FLY_POS[iSceneID]
    
    return []


def GetReturnTeamFLyPosListByID(iSceenID):
    if iSceenID in DEFAULT_SWITCH_POS:
        return DEFAULT_SWITCH_POS[iSceenID]
    
    return []


def IsCanFlyMapByID(iSceenID):
    if iSceenID in DEFAULT_POS_DATA.keys():
        return True
    
    return False


def IsCanFlyMapByName(sSceenName):
    for k, dInfo in DEFAULT_POS_DATA.items():
        if sSceenName == dInfo['sDesc']:
            return True
            continue
    
    return False


class CFlyPosMgr(slot.ISignalSubject):
    ss_ItemFlyPointChg = 'ss_ItemFlyPointChg(iItemID, iPos, sPointName, iSceneID, x, y)'
    ss_FlyItemDel = 'ss_FlyItemDel(iItemID)'
    ss_MapFlyPointChg = 'ss_MapFlyPointChg(iSceneID, x, y, sDesc)'
    ss_MapFlyPointInit = 'ss_MapFlyPointInit()'
    ss_DurableChange = 'ss_DurableChange(iDurable)'
    
    def __init__(self):
        self.ssInit()
        self.ssCreate(self.ss_ItemFlyPointChg)
        self.ssCreate(self.ss_MapFlyPointChg)
        self.ssCreate(self.ss_DurableChange)
        self.m_ItemFlyPoint = { }
        self.m_MapFlyPoint = { }
        self.m_TopBtnPos = None
        self.m_Durable = None
        self.m_IsNpcShow = None

    
    def GetCountrySceneData(self, iCountryId):
        '''\xb3q\xb9L\xb0\xea\xaeaID\xc0\xf2\xb1o\xaa\xf9\xac\xa3\xa6^\xaa\xf9\xb2\xc5\xb6\xc7\xb0e\xc2I'''
        if iCountryId == 0:
            return None
        
        iSenceId = countryId2Pos[iCountryId]
        return COUNTRY_POS_DATA[iSenceId]

    
    def CheckUseHuiMenFu(self):
        '''\xacO\xa7_\xa6\xb3\xa5i\xa5\xce\xaa\xba\xa6^\xaa\xf9\xb2\xc5'''
        import item
        dItem = item.GetItemsByShape(30044)
        if dItem:
            for oItem in dItem.values():
                if oItem.IsInDeadline():
                    return oItem
                    continue
            
        

    
    def GetScenePointList(self, iSceneID):
        iSceneID = KUAFU2NORMAL.get(iSceneID, iSceneID)
        tDefaultFlyPos = DEFAULT_POS_DATA.get(iSceneID)
        tSceneFlyPosList = self.GetMapFlyPoointList(iSceneID)
        tTmpList = []
        if tDefaultFlyPos:
            tTmpList.extend([
                tDefaultFlyPos])
        
        if tSceneFlyPosList:
            tTmpList.extend(tSceneFlyPosList)
        
        return (tTmpList, bool(tDefaultFlyPos))

    
    def SwitchMode(self, iItemID):
        netfly.C2SChangeFlyOpenType(iItemID)

    
    def AddDurable(self, iItemID):
        import item
        oFlyBagItem = item.FindItemWithPrior('\xad\xb8\xa6\xe6\xbaX\xb8\xc9\xa5R\xa5]')
        sTips = '\xad@\xa4[\xa4w\xa8\xac\xb0\xf7\xa1]%d/%d\xa1^\xa1A\xb5L\xaak\xc4~\xc4\xf2\xb8\xc9\xa5R' % (self.m_Durable, FULL_DURABLE)
        if FULL_DURABLE - self.m_Durable < ADD_DURABLE:
            usermacro.PROMPT_MSG(sTips)
            return None
        
        if oFlyBagItem is None:
            self.AddDurableBySG()
        else:
            self.AddDurableByItem(iItemID, oFlyBagItem.m_ID)

    
    def RecordTextFlyPoint(self, iItemID, iPos, sDesc):
        netfly.C2STextFlyRecord(iItemID, iPos + 1, sDesc)

    
    def FlyToScene(self, iItemID, iPos):
        if autocm_new.IsCM():
            usermacro.PROMPT_MSG(AUTOCM_BAN_TIPS)
            return None
        
        netfly.C2SFlyGotoTrans(iItemID, iPos)

    
    def FlyToRecord(self, iItemID, iPos):
        if autocm_new.IsCM():
            usermacro.PROMPT_MSG(AUTOCM_BAN_TIPS)
            return None
        
        netfly.C2SFlyGotoRecord(iItemID, iPos)

    
    def FlyToSceneByFu(self, iItemID, iSceneID):
        netfly.C2SSFlyGotoTrans(iItemID, iSceneID)

    
    def SetFlyAlias(self, iItemID, sAlias):
        netfly.C2SSetItemAlias(iItemID, sAlias)

    
    def MapFlyToRecord(self, iSceneID, x, y, mode = 0):
        if autocm_new.IsCM():
            usermacro.PROMPT_MSG(AUTOCM_BAN_TIPS)
            return None
        
        iSceneID = KUAFU2NORMAL.get(iSceneID, iSceneID)
        netfly.C2SMapGotoRecord(iSceneID, x, y, mode)

    
    def RecordMapFlyPoint(self, iSceneID, x, y, sDesc):
        iSceneID = KUAFU2NORMAL.get(iSceneID, iSceneID)
        netfly.C2SRecoreFlyPoint(iSceneID, x, y, sDesc)

    
    def DelMapFlyPoint(self, iSceneID, x, y):
        iSceneID = KUAFU2NORMAL.get(iSceneID, iSceneID)
        netfly.C2SDelMapFlyPoint(iSceneID, x, y)

    
    def TopSceneBtn(self, iItemID, iPos):
        netfly.C2STopSceneBtn(iItemID, iPos)

    
    def IsNpcIconShow(self):
        if self.m_IsNpcShow is not None:
            return self.m_IsNpcShow
        
        import cfg
        import hero
        b = cfg.GetData('mx.ini', str(hero.g_ID), INI_SHOWNPC)
        if b in ('True', None):
            self.m_IsNpcShow = True
        else:
            self.m_IsNpcShow = False
        return self.m_IsNpcShow

    
    def SaveNpcIconShow(self, bShow):
        import cfg
        import hero
        self.m_IsNpcShow = bShow
        cfg.SaveData('mx.ini', str(hero.g_ID), INI_SHOWNPC, str(bShow))

    
    def GetMapFlyPoointList(self, iSceneID):
        return self.m_MapFlyPoint.get(iSceneID, [])

    
    def GetAllFlyPointNum(self):
        iSum = len(DEFAULT_POS_DATA)
        for tPointList in self.m_MapFlyPoint.values():
            iSum += len(tPointList)
        
        return iSum

    
    def GetDurable(self):
        if self.m_Durable:
            return self.m_Durable
        
        return 0

    
    def DoShowTextFly(self, iItemID, iDurable, sRecordDict, sSceneDict):
        import dlgflyflag
        dlgflyflag.ShowTextFlyDlg(iItemID, iDurable, sRecordDict, sSceneDict)

    
    def DoShowMapFly(self, iItemID, iBurable, iTopBtnPos):
        import dlgflyflag
        dlgflyflag.ShowMapFlyDlg(iItemID, iBurable, iTopBtnPos)

    
    def AddDurableBySG(self):
        netfly.C2SAddFlyBySG()

    
    def AddDurableByItem(self, iItemID, iFlyBagID):
        netfly.C2SAddFlyByItem(iItemID, iFlyBagID)

    
    def OnUpdateItemFlyPointInfo(self, iItemID, iPos, iSceneID, x, y, sPointName):
        if iItemID not in self.m_ItemFlyPoint:
            self.m_ItemFlyPoint[iItemID] = { }
        
        self.m_ItemFlyPoint[iItemID][iPos] = dTmp = { }
        dTmp['iSceneID'] = iSceneID
        dTmp['tPos'] = (x, y)
        dTmp['sPointName'] = sPointName
        self.ssEmit(self.ss_ItemFlyPointChg, iItemID, iPos, sPointName, iSceneID, x, y)

    
    def OnDelItemFlyPointInfo(self, iItemID, iPos):
        if iPos not in self.m_ItemFlyPoint[iItemID]:
            return None
        
        del self.m_ItemFlyPoint[iItemID][iPos]
        self.ssEmit(self.ss_ItemFlyPointChg, iItemID, iPos, '', -1, -1, -1)

    
    def OnDelFlyItem(self, iItemID):
        if iItemID not in self.m_ItemFlyPoint:
            return None
        
        del self.m_ItemFlyPoint[iItemID]
        self.ssEmit(self.ss_FlyItemDel, iItemID)

    
    def OnRefreshDurable(self, iDurable):
        self.m_Durable = iDurable
        self.ssEmit(self.ss_DurableChange, iDurable)

    
    def OnShowTextFlyDlg(self, iItemID, iDurable, sSceneList, sRecordList):
        self.m_Durable = iDurable
        iKeyList = range(0, MAX_RECORD_NUM)
        sTmpRecordDict = dict(zip(iKeyList, sRecordList))
        iKeyList = range(0, MAX_SCENE_NUM)
        sTmpSceneDict = dict(zip(iKeyList, sSceneList))
        self.DoShowTextFly(iItemID, iDurable, sTmpRecordDict, sTmpSceneDict)

    
    def OnShowMapFlyDlg(self, iItemID, iDurable, iTopBtnPos):
        self.m_Durable = iDurable
        self.m_TopBtnPos = iTopBtnPos
        self.DoShowMapFly(iItemID, iDurable, iTopBtnPos)

    
    def OnInitMapFlyPointInfo(self, dInfo):
        import banword
        self.m_MapFlyPoint = dInfo
        self.ssEmit(self.ss_MapFlyPointInit)
        sDescList = []
        for iSceneID in dInfo:
            for dPoint in dInfo[iSceneID]:
                sDesc = dPoint.get('sDesc', '')
                (iX, iY) = dPoint.get('tPos', (0, 0))
                if sDesc:
                    sDescList.append((sDesc, '%d_%d_%d' % (iSceneID, iX, iY)))
                    continue
            
        
        if sDescList:
            banword.AddCheckWordTask(sDescList, 'flyposname')
        

    
    def OnAddMapFlyPointInfo(self, iSceneID, x, y, sDesc):
        import banword
        if iSceneID not in self.m_MapFlyPoint:
            self.m_MapFlyPoint[iSceneID] = []
        
        dInfo = { }
        dInfo['tPos'] = (x, y)
        dInfo['sDesc'] = sDesc
        self.m_MapFlyPoint[iSceneID].append(dInfo)
        self.ssEmit(self.ss_MapFlyPointChg, iSceneID, x, y, sDesc)
        if sDesc:
            banword.AddCheckWordTask([
                (sDesc, '%d_%d_%d' % (iSceneID, x, y))], 'flyposname')
        

    
    def OnDelMapFlyPointInfo(self, iSceneID, x, y):
        if iSceneID not in self.m_MapFlyPoint:
            return None
        
        tTmpList = []
        for dInfo in self.m_MapFlyPoint[iSceneID]:
            if dInfo['tPos'] == (x, y):
                tTmpList.append(dInfo)
                continue
        
        for dInfo in tTmpList:
            self.m_MapFlyPoint[iSceneID].remove(dInfo)
        
        self.ssEmit(self.ss_MapFlyPointChg, iSceneID, -1, -1, '')

    
    def OnTriggerCommonCB(self, idx):
        import commoncb
        cbkeyDict = {
            1: commoncb.FLY_GET,
            2: commoncb.FLY_USE,
            3: commoncb.FLY_ADD }
        if idx in cbkeyDict:
            commoncb.TriggerCB(cbkeyDict[idx], 1)
