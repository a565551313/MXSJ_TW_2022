# pycdc 交叉复核产物 · script.fls entry 3102
# co_filename(原始)='script/mxgame/map/mapani.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3102.pyc (Python 2.5)

'''
\xb5\xd8\xcd\xbc\xb5\xc4\xcc\xd8\xd0\xa7\xb6\xaf\xbb\xad
'''
import C_sys
import interface
import map
import mapanilayerdata
import newnormalaudiomgr
import newsoundinterface
import timer
import misc
from collections import deque
import juben
import mapaninotdelayloaddata
import asynctaskdefine
import asynctaskqueue
import permission
g_MapAniLoader = None
g_ResList = None
g_SceneEffect = True
g_MapID = None
g_MapAniObjects = []
g_LoadedResIDSet = set()
g_bLoadAniEnabled = True
SHENMO_HIDE_ANI = (({
    1157: [
        (434, 2311)] }, True), ({
    1177: [
        (2977, 2348),
        (275, 220)] }, True), ({
    1176: [
        (505, 237)] }, True), ({
    1052: [
        (3893, 2156),
        (79, 1958)] }, True), ({
    1313: [
        (2882, 189)] }, True))
HUODONG_HIDE_ANI = {
    9039: ({
        1039: [
            (49, 364),
            (49, 1141)] }, True),
    9040: ({
        1040: [
            (44, 330),
            (1531, 951)] }, True),
    9041: ({
        1041: [
            (56, 1694),
            (2119, 127)] }, True),
    9042: ({
        1042: [
            (51, 191),
            (475, 1725)] }, True),
    9043: ({
        1159: [
            (2823, 73)] }, True),
    9047: ({
        1047: [
            (2325, 1741)] }, True) }

def GetMapAniLoader():
    global g_MapAniLoader
    if not g_MapAniLoader:
        g_MapAniLoader = CMapAniLoaderNew()
    
    return g_MapAniLoader


def DestroyMapAniLoader():
    global g_MapAniLoader
    if g_MapAniLoader:
        g_MapAniLoader.Destroy()
        g_MapAniLoader = None
    


def SetLoadAniEnabled(bFlag):
    global g_bLoadAniEnabled
    g_bLoadAniEnabled = bFlag


def DelayLoadMapAni():
    SetLoadAniEnabled(True)
    Load()


def ModuleReset():
    global g_ResList, g_SceneEffect, g_MapID, g_MapAniObjects, g_LoadedResIDSet, g_MapAniLoader
    g_ResList = None
    g_SceneEffect = True
    g_MapID = None
    g_MapAniObjects = []
    g_LoadedResIDSet = set()
    if g_MapAniLoader:
        g_MapAniLoader.Destroy()
        g_MapAniLoader = None
    
    DestroyMapAniLoader()


def Init():
    global g_ResList
    if g_ResList:
        return None
    
    data = C_sys.LoadFile('ani.lst', 'map')
    g_ResList = data.split()


def InitIfNeeed():
    if g_ResList:
        return None
    
    Init()


class CRes(object):
    
    def __init__(self, data):
        self.m_Type = -1
        self.m_FileName = ''
        
        try:
            self.m_Type = int(data.pop())
        except:
            return None

        if self.m_Type in (0, 1, 2, 3, 4):
            self.m_FileName = 'ani\\' + data.pop()
        



def GetResByIdx(idx):
    return g_ResList[idx]


def LoadRes(idx):
    name = g_ResList[idx]
    data = C_sys.LoadFile('ani\\' + name, 'map')
    if data is None:
        print 'miss ani\\' + name
        return None
    
    data = data.split()
    data.reverse()
    res = CRes(data)
    g_ResList[idx] = res
    return res


class CAni(interface.CSpriteObject):
    
    def __init__(self, res, x, y):
        oParent = None if map.g_Map else None
        if not oParent:
            return None
        
        if not res.m_FileName:
            return None
        
        interface.CSpriteObject.__init__(self, oParent, res.m_FileName, 'map')
        self.m_sFileName = res.m_FileName
        self.SetPos(x, y)
        self.SetZ(y)
        n = misc.RandInt(0, self.FrameAmount() - 1)
        self.SetFrame(n)
        self.CreateCommand(0, 'animation')
        self.SetAniShow(res.m_FileName, x, y)
        self.ChangeZ(res.m_FileName)

    
    def ChangeZ(self, filename):
        iZ = mapanilayerdata.GetMapAniZValue(filename, g_MapID, map.GetCurrentSceneID())
        if iZ is not None:
            self.SetZ(iZ)
        

    
    def IsSpecialScene(self, iMapID, sceneID):
        
        try:
            if g_MapID == iMapID:
                pass
            return map.g_Map.m_Scene[0] == sceneID
        except:
            pass

        return False

    
    def IsHuodongScene(self, iMinimapID):
        
        try:
            return map.GetCurrentMiniMapID() == iMinimapID
        except:
            return False


    
    def GetFileName(self):
        return self.m_sFileName

    
    def SetAniShow(self, filename, x, y):
        import deltiaozhuaniddata
        if filename == 'ani\\\xb4\xab\xcb\xcd\xb5\xe3.spr':
            import dlgshenmoisland
            filterLst = []
            for idx in xrange(1, 11):
                filterLst.append('\xbe\xc7\xae{%d\xb8\xb9\xc6U' % idx)
            
            filterLst.extend(('\xbe\xc7\xae{\xa5\xf4\xb0\xc8A\xc6U', '\xbe\xc7\xae{\xa5\xf4\xb0\xc8B\xc6U', '\xbe\xc7\xae{\xa5\xf4\xb0\xc8C\xc6U', '\xbe\xc7\xae{\xb7\xc7\xb3\xc6\xc6U'))
            if map.g_Map.m_SceneName in filterLst:
                self.SetShow(False)
            
            lst = [
                (deltiaozhuaniddata.DATA, misc.IsInKuafuServer())]
            if self.IsSpecialScene(1041, 1041):
                lst.append(({
                    1041: [
                        (56, 1694)] }, True))
            
            for iMinimapID in HUODONG_HIDE_ANI:
                if self.IsHuodongScene(iMinimapID):
                    lst.append(HUODONG_HIDE_ANI[iMinimapID])
                    continue
            
            if dlgshenmoisland.IsShenmoHuodong():
                for t in SHENMO_HIDE_ANI:
                    lst.append(t)
                
            
            for delDct, bValid in lst:
                if not bValid or g_MapID not in delDct:
                    continue
                
                for posX, posY in delDct[g_MapID]:
                    if x == int(posX) and y == int(posY):
                        self.SetShow(False)
                        return None
                        continue
                
            
        



class CMapAni(interface.CMapSpriteObject):
    
    def __init__(self, res, x, y):
        oParent = None if map.g_Map else None
        if not oParent:
            return None
        
        if not res.m_FileName:
            return None
        
        interface.CMapSpriteObject.__init__(self, oParent, res.m_FileName, 'map')
        self.SetPos(x, y)
        self.SetZ(y)
        n = misc.RandInt(0, self.FrameAmount() - 1)
        self.SetFrame(n)
        self.CreateCommand(0, 'animation')


Type2Class = {
    0: CAni,
    1: CMapAni }

def Create(idx, iResID, *arg):
    oEvent = CLoadEvent(iResID, *arg)
    GetMapAniLoader().Push(oEvent)
    g_MapAniObjects[idx] = oEvent
    if permission.IsOpenNewSoundBnk():
        iRes = oEvent.GetResID()
        name = g_ResList[iRes].m_FileName
        if '\xc0s\xc0Y' in name:
            newsoundinterface.Play('%s, %d, %d' % (name, arg[0], arg[1]), False, True)
        
    


def GetFileName(idx):
    global g_MapID
    import racingspeedgame
    g_MapID = idx
    mapReplaceList = map.GetMapReplaceDict()
    if idx in mapReplaceList:
        sFileName = mapReplaceList[idx] + '.ani'
    elif racingspeedgame.CheckGameStart():
        sFixID = ''
        iFixID = racingspeedgame.GetRacingSpeedMgr().GetSceneFixId(idx)
        if iFixID:
            sFixID = '_%d' % iFixID
        
        sFileName = '%d%s.ani' % (idx, sFixID)
    else:
        sFileName = '%.4d.ani' % idx
    return sFileName


def GetNeedHideAniLst(mapID, hasRainbow, rainbowLst):
    import rainbowdata
    allRainbowAni = set(rainbowdata.GetAllRainbowAni(mapID))
    if not hasRainbow or not rainbowLst:
        return allRainbowAni
    
    tempAniLst = []
    for rainbowID in rainbowLst:
        tempAniLst.extend(rainbowdata.GetRainbowAni(mapID, rainbowID))
    
    return allRainbowAni - set(tempAniLst)


def Load(oMapObject = None, iAniID = None, hasRainbow = False, rainbowLst = None):
    global g_MapAniObjects, g_MapAniData, g_NeedHideAniInfo
    import map
    if permission.IsOpenNewSoundBnk():
        import newnormalaudiomgr
        newnormalaudiomgr.GetSoundPlayMgr().StopAllSound()
    
    if not g_bLoadAniEnabled:
        return None
    
    if not oMapObject:
        oMapObject = map.GetGameMapO-%*,t()
    
    if not oMapObject:
        return None
    
    iMapID = oMapObject.GetID()
    if not iAniID:
        iAniID = iMapID
    
    GetMapAniLoader().Clear()
    specialAniLst = [
        0,
        259,
        260,
        261,
        262,
        263,
        264,
        265,
        542]
    
    try:
        if hasattr(oMapObject, 'm_SceneAniTimer') and oMapObject.m_SceneAniTimer:
            oMapObject.m_SceneAniTimer.Release()
            oMapObject.m_SceneAniTimer = None
        
        Init()
        filename = GetFileName(iAniID)
        
        try:
            data = C_sys.LoadFile(filename, 'map')
            if data is None:
                return None
        except IOError:
            return None

        data = data.split()
        data.reverse()
        iCount = len(data) - 1
        total = int(data[iCount])
        g_MapAniObjects = [
            None] * total
        iCount -= 1
        sn = int(data[iCount])
        iCount -= 1
        g_MapAniData = [ (int(data[iCount - i * 3]), int(data[iCount - i * 3 - 1]), int(data[iCount - i * 3 - 2])) for i in xrange(sn) ]
        iCount -= sn * 3 - 1
        iCount -= 1
        total *= 2
        iCount -= 1
        px = [ (int(data[iCount - i * 2]), int(data[iCount - i * 2 - 1])) for i in xrange(total) ]
        iCount -= total * 2 - 1
        iCount -= 1
        iCount -= total * 2 - 1
        g_NeedHideAniInfo = set()
        g_NeedHideAniInfo.update(GetNeedHideAniLst(iAniID, hasRainbow, rainbowLst))
        
        def _Refresh(obj, x, y, iLPos, iRPos, tPos, bPos):
            dEnterMap = { }
            dLeaveMap = { }
            lEnterSort = []
            (iMapX, iMapY) = obj.GetPos()
            iMapX = -iMapX
            iMapY = -iMapY
            import ratio
            iMapRightX = iMapX + ratio.WINDOW_WIDTH
            iMapRightY = iMapY + ratio.WINDOW_HEIGHT
            iCenterX = (iMapRightX + iMapX) / 2
            iCenterY = (iMapY + iMapRightY) / 2
            if x < iMapX:
                while iLPos < total - 1:
                    ppx = px[iLPos + 1]
                    if iMapX < ppx[0]:
                        break
                    
                    if ppx[1] > 0:
                        dLeaveMap[ppx[1]] = True
                    
                    iLPos += 1
                while iRPos < total - 1:
                    ppx = px[iRPos + 1]
                    if iMapRightX < ppx[0]:
                        break
                    
                    if ppx[1] < 0:
                        iDistance = (iCenterX - ppx[0]) ** 2 + (iCenterY - g_MapAniData[-ppx[1] - 1][2]) ** 2
                        lEnterSort.append((iDistance, -ppx[1]))
                    
                    iRPos += 1
            elif x > iMapX:
                while iLPos > -1:
                    ppx = px[iLPos]
                    if iMapX >= ppx[0]:
                        break
                    
                    if ppx[1] > 0:
                        iDistance = (iCenterX - ppx[0]) ** 2 + (iCenterY - g_MapAniData[ppx[1] - 1][2]) ** 2
                        lEnterSort.append((iDistance, ppx[1]))
                    
                    iLPos -= 1
                while iRPos > -1:
                    ppx = px[iRPos]
                    if iMapRightX >= ppx[0]:
                        break
                    
                    if ppx[1] < 0:
                        dLeaveMap[-ppx[1]] = True
                    
                    iRPos -= 1
            
            lEnterSort.sort(key = (lambda x: x[0]))
            for tSort in lEnterSort:
                idx = tSort[1]
                if idx not in dLeaveMap:
                    idx -= 1
                    if (g_SceneEffect or not hasattr(obj, 'm_FakeMap') or g_MapAniData[idx][0] in specialAniLst) and g_MapAniData[idx] not in g_NeedHideAniInfo:
                        Create(idx, *g_MapAniData[idx])
                    
                g_MapAniData[idx] not in g_NeedHideAniInfo
            
            oLoader = GetMapAniLoader()
            for idx in dLeaveMap.iterkeys():
                oEvent = g_MapAniObjects[idx - 1]
                g_MapAniObjects[idx - 1] = None
                if oEvent:
                    if permission.IsOpenNewSoundBnk():
                        iRes = oEvent.GetResID()
                        (x, y) = oEvent.GetResPos()
                        name = g_ResList[iRes].m_FileName
                        if '\xc0s\xc0Y' in name:
                            newnormalaudiomgr.GetSoundPlayMgr().StopSoundByName('%s, %d, %d' % (name, x, y))
                        
                    
                    oEvent.SetIsDelete()
                    oLoader.Pop(oEvent.m_iID)
                    continue
            
            return (iMapX, iMapY, iLPos, iRPos, tPos, bPos)

        oMapObject.m_SceneAniTimer = oMapObject.CreatePyCommand(1, _Refresh, -100000, -100000, -1, -1, -1, -1)
    except:
        pass



def LoadEffect(parent, filename, path, iBaseX = 0, iBaseY = 0, iBaseZ = 0):
    data = C_sys.LoadFile(filename, interface.UIPath)
    data = data.splitlines()
    res = []
    for line in data:
        if len(line) == 0 or line[0] == '#':
            continue
        
        (sFileName, x, y) = line.split('\t')
        
        try:
            spr = interface.CSpriteObject(parent, '%s/%s.spr' % (path, sFileName), interface.UIPath)
        except:
            print '\xc3\xbb\xd3\xd0\xd5\xd2\xb5\xbd\xb8\xc4\xd7\xca\xd4\xb4\xce\xc4\xbc\xfe\xa3\xba%s/%s.spr' % (path, sFileName)
            continue

        spr.SetPos(iBaseX + int(x), iBaseY + int(y))
        spr.SetZ(iBaseZ)
        spr.CreateCommand(1, 'animation')
        res.append(spr)
    
    return res


class CLoadEvent(object):
    NEXT_ID = 0
    
    def __init__(self, iResId, *args):
        super(CLoadEvent, self).__init__()
        CLoadEvent.NEXT_ID += 1
        self.m_iID = CLoadEvent.NEXT_ID
        self.m_iResId = iResId
        self.m_oArgs = args
        self.m_oRealObj = None
        self.m_bDelete = False

    
    def GetResID(self):
        return self.m_iResId

    
    def GetResPos(self):
        return self.m_oArgs

    
    def SetIsDelete(self):
        self.m_bDelete = True

    
    def IsDelete(self):
        return self.m_bDelete

    
    def GetPathInfo(self):
        
        try:
            oRes = g_ResList[self.m_iResId]
            if type(oRes) == str:
                oRes = LoadRes(self.m_iResId)
            
            if not oRes:
                LOG_DEBUG('\xb8\xea\xb7\xbd\xa5[\xb8\xfc\xbf\xf9\xbb~>>>>>>>>>', self.m_iResId)
                return None
            
            return (oRes.m_FileName, 'map')
        except:
            return None


    
    def Load(self):
        
        try:
            oRes = g_ResList[self.m_iResId]
            if type(oRes) == str:
                oRes = LoadRes(self.m_iResId)
            
            if oRes:
                oClass = Type2Class.get(oRes.m_Type)
                if oClass:
                    self.m_oRealObj = oClass(oRes, *self.m_oArgs)
                    if self.m_iResId not in g_LoadedResIDSet:
                        g_LoadedResIDSet.add(self.m_iResId)
                    
                
        except:
            pass




class CMapAniLoaderNew(object):
    
    def __init__(self):
        super(CMapAniLoaderNew, self).__init__()
        self.m_dId2WaitEvent = { }
        self.m_bAsyncEnabled = True
        self.m_dEventID2AsyncTaskID = { }
        self.m_setAsyncTaskID = set()
        self.m_oQueue = deque()
        self.m_oTimer = None

    
    def Push(self, oEvent):
        iMapID = map.GetMapID()
        if not iMapID:
            if self.m_dId2WaitEvent or self.m_oQueue:
                self.Clear()
            
            return None
        
        if oEvent.m_iResId == 0 or juben.IsPlayJuben():
            oEvent.Load()
            return None
        
        if mapaninotdelayloaddata.IsNotDelayLoad(iMapID, oEvent.m_iResId):
            oEvent.Load()
            return None
        
        if not (self.m_bAsyncEnabled) or oEvent.m_iResId in g_LoadedResIDSet:
            self.m_oQueue.append(oEvent)
            if not self.m_oTimer:
                self.CreateTimer()
            
            return None
        
        iEventID = oEvent.m_iID
        param = oEvent.GetPathInfo()

    
    def Pop(self, iId):
        iTaskID = self.m_dEventID2AsyncTaskID.get(iId, None)
        if iTaskID:
            if iTaskID in self.m_setAsyncTaskID:
                asynctaskqueue.GetAsyncTaskQueue().RemoveAsyncLoadTaskById(asynctaskdefine.TASK_TYPE_MAP_ANI, iTaskID)
                self.m_setAsyncTaskID.remove(iTaskID)
            
            del self.m_dEventID2AsyncTaskID[iId]
        
        if iId in self.m_dId2WaitEvent:
            oEvent = self.m_dId2WaitEvent.pop(iId)
            return oEvent
        

    
    def OnAsyncTaskFinish(self, *vArgs):
        '''
\t\t\xb2\xa7\xa8B\xbdu\xb5{\xa5[\xb8\xfc\xa7\xb9\xb8\xea\xb7\xbd\xa4\xa7\xab\xe1\xa6^\xbd\xd5\xa1A\xa6\xb9\xae\xc9\xa5i\xa5H\xa5[\xb8\xfc\xa6a\xb9\xcf\xafS\xae\xc4
\t\t:param vArgs: \xb2K\xa5[\xb2\xa7\xa8B\xa5\xf4\xb0\xc8\xaa\xba\xae\xc9\xad\xd4\xb6\xc7\xa4J\xaa\xba\xa6^\xbd\xd5\xb0\xd1\xbc\xc6
\t\t:return: None
\t\t'''
        (iId, oSprite) = vArgs
        oEvent = self.Pop(iId)
        if oEvent and map.GetMapID():
            oEvent.Load()
        

    
    def SetAsyncEnabled(self, bFlag):
        self.m_bAsyncEnabled = bFlag

    
    def CreateTimer(self):
        self.ReleaseTimer()
        self.m_oTimer = timer.Timer(0.033, self.Loop, -1, self)

    
    def Loop(self):
        '''
\t\t\xa5\xce\xa9\xf3\xa8C\xb4V\xa5[\xb8\xfc\xa4w\xb8g\xa5[\xb8\xfc\xb9L\xaa\xba\xa6a\xb9\xcf\xafS\xae\xc4\xb8\xea\xb7\xbd
\t\t:return: None
\t\t'''
        iMapID = map.GetMapID()
        if not iMapID:
            self.Clear()
            return None
        
        if self.m_oQueue:
            oEvent = self.m_oQueue.popleft()
            oEvent.Load()
        
        if not self.m_oQueue:
            self.ReleaseTimer()
        

    
    def ReleaseTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        

    
    def Clear(self):
        self.ReleaseTimer()
        self.m_dId2WaitEvent = { }
        oQueue = asynctaskqueue.GetAsyncTaskQueue()
        for iTaskID in self.m_setAsyncTaskID:
            oQueue.RemoveAsyncLoadTaskById(asynctaskdefine.TASK_TYPE_MAP_ANI, iTaskID)
        
        self.m_setAsyncTaskID.clear()
        self.m_dEventID2AsyncTaskID = { }
        self.m_oQueue.clear()

    
    def Destroy(self):
        self.ReleaseTimer()
        oQueue = asynctaskqueue.GetAsyncTaskQueue()
        for iTaskID in self.m_setAsyncTaskID:
            oQueue.RemoveAsyncLoadTaskById(asynctaskdefine.TASK_TYPE_MAP_ANI, iTaskID)
