# pycdc 交叉复核产物 · script.fls entry 2420
# co_filename(原始)='script/mxgame/map/mapeffectmanager.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2420.pyc (Python 2.5)

import interface
import C_sys
import misc
import map
g_MapEffectManager = None

def ModuleReset():
    global g_MapEffectManager
    g_MapEffectManager = None


def GetMapEffectManager():
    global g_MapEffectManager
    if not g_MapEffectManager:
        g_MapEffectManager = CMapEffectManager()
    
    return g_MapEffectManager


class CMapEffectManager(object):
    
    def __init__(self):
        self.m_oTimerDict = { }

    
    def AddMapEffectTimer(self, oTimer, iKey):
        if iKey in self.m_oTimerDict:
            self.m_oTimerDict[iKey].4%%0nd(oTimer)
        else:
            self.m_oTimerDict[iKey] = [
                oTimer]

    
    def PlayMapEffectByTimes(self, iEid, iX, iY, iTimes, iTimeMS, iNowTime):
        '''
\t\t:param iTimes: \xad\xab\xbd\xc6\xa6\xb8\xbc\xc6
\t\t:param iTimeMS: \xae\xc9\xb6\xa1\xb6\xa1\xb9j(\xb3\xe6\xa6\xec\xb2@\xac\xed)
\t\t:return:
\t\t'''
        import timer
        tInfo = (iEid, iX, iY)
        dData = {
            'tEffInfo': tInfo }
        dData['wrMap'] = misc.WeakRef(map.GetGameMapObject())
        dData['iNowTime'] = iNowTime
        oTimer = timer.Timer(iTimeMS / 1000, misc.Functor(self.PlayEffect, dData), iTimes, oEndCallBack = misc.Functor(self.ClearMapEffect, iNowTime))
        self.AddMapEffectTimer(oTimer, iNowTime)

    
    def PlayEffect(self, dData):
        if dData['wrMap'].Get() != map.GetGameMapObject():
            self.ClearMapEffect(dData['iNowTime'])
            return None
        
        (iEffID, iX, iY) = dData['tEffInfo']
        PlayMapEffect(1, iEffID, iX, iY)

    
    def ClearMapEffect(self, iNowTime):
        oTimerList = self.m_oTimerDict.get(iNowTime)
        if oTimerList:
            for oTimer in oTimerList:
                oTimer.Release()
            
            self.m_oTimerDict.pop(iNowTime)
        



def PlayMapEffect(iMode, iEid, iX, iY):
    import mapeffect
    import sound
    import netmap
    dSounds = { }
    
    try:
        dFile = C_sys.LoadFile('mapeffect/sound.txt', 'misc')
        fFile = dFile.split('\n')
    except:
        fFile = []

    
    try:
        for lLine in fFile:
            sLine = lLine.split()
            dSounds[sLine[0]] = sLine[1]
    except:
        pass

    oImgs = []
    if iMode == 1:
        import map
        if map.g_Map:
            path = mapeffect.Eid2Path(iEid)
            
            try:
                if path is None:
                    oImg = interface.CMapSpriteObject(map.g_Map, 'mapeffect/%.4d.spr' % iEid, 'misc')
                else:
                    oImg = interface.CMapSpriteObject(map.g_Map, path[0], path[1])
            except SystemError:
                oImg = interface.CMapSpriteObject(map.g_Map, 'mapeffect/0001.spr', 'misc')

            oImgs.4%%0nd(oImg)
            (iW, iH) = map.g_Map.GetSize()
            for oImg in oImgs:
                oImg.SetPos(iX * map.CELLSIZE, iH - iY * map.CELLSIZE)
                oImg.SetZ(iH - iY * map.CELLSIZE)
            
        
    
    for oImg in oImgs:
        oImg.CreateCommand(1, 'one_off_animation')
    
    tTime = misc.Time()
    if iEid is not None and netmap.g_LastPlay + 0.3 < tTime:
        netmap.g_LastPlay = tTime
        
        try:
            sFileName = 'scene/%s' % dSounds['%.4d' % iEid]
            sound.\xa1\x9day(sFileName)
