# pycdc 交叉复核产物 · script.fls entry 3443
# co_filename(原始)='script/core/warweather.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3443.pyc (Python 2.5)

import ui
import war
import random
import misc
import warrior
import timer
g_WeatherMgr = None
g_XYList = None

def ModuleReset():
    global g_WeatherMgr, g_XYList
    g_WeatherMgr = None
    g_XYList = None


def GetWeatherMgr():
    global g_WeatherMgr
    if not g_WeatherMgr:
        g_WeatherMgr = CWeatherMgr()
    
    return g_WeatherMgr


class CWeatherMgr(object):
    
    def __init__(self):
        self.m_CurWeahter = None
        self.m_iTimeInc = 0
        self.m_oWeatherTimer = timer.Timer(0, self.OnWeatherUpdate, -1, self)

    
    def CreateByID(self, iID):
        if iID == 6:
            oWeather = CRainWeather()
        elif iID == 1:
            oWeather = CFireWeather()
        elif iID == 2:
            oWeather = CForestWeather()
        else:
            return None
        war.g_Background.m_Weather = oWeather
        self.m_CurWeahter = misc.WeakRef(oWeather)

    
    def OnWeatherUpdate(self):
        self.m_iTimeInc += 1
        if self.m_iTimeInc % 1000 >= warrior.g_WaitingTimeInc:
            return None
        
        if self.m_CurWeahter and self.m_CurWeahter():
            self.m_CurWeahter().OnWeatherAniUpdate()
        

    
    def Release(self):
        if self.m_oWeatherTimer:
            self.m_oWeatherTimer.Release()
        
        self.m_CurWeahter = None



class CWeatherBase(object):
    
    def __init__(self):
        self.m_WeahterAniList = []
        self.m_iCurFrame = 0

    
    def CreateWeatherAni(self, sPath, sPlayState, tPos):
        oAni = ui.CEffAniObject(war.g_Background, sPath)
        oAni.SetPlayState(sPlayState)
        oAni.SetEndCB(misc.Functor(self.OnWeatherAniEnd))
        oAni.SetPos(*tPos)
        oAni.SetZ(99)
        self.m_WeahterAniList.append(oAni)

    
    def OnWeatherAniUpdate(self):
        self.m_iCurFrame += 1
        for oAni in self.m_WeahterAniList:
            oAni.OnPlay(None)
        

    
    def OnWeatherAniEnd(self, oAni):
        if oAni in self.m_WeahterAniList:
            self.m_WeahterAniList.remove(oAni)
        



class CRainWeather(CWeatherBase):
    
    def __init__(self):
        CWeatherBase.__init__(self)

    
    def OnWeatherAniUpdate(self):
        if self.m_iCurFrame % 15 == 0:
            self.CreateRain()
        
        CWeatherBase.OnWeatherAniUpdate(self)

    
    def CreateRain(self):
        import ratio
        if ratio.Is1280x960():
            (iXSize, iYSize) = (1280, 960)
            iRainFall = 8
        else:
            (iXSize, iYSize) = (800, 600)
            iRainFall = 5
        for idx in range(iRainFall):
            self.CreateWeatherAni('magicres/eff/weather/rain.eff', 0, (random.randint(0, iXSize), random.randint(0, iYSize)))
        



class CFireWeather(CWeatherBase):
    
    def __init__(self):
        CWeatherBase.__init__(self)
        self.m_CreatePosList = RandomScreenPos(6)

    
    def OnWeatherAniUpdate(self):
        if self.m_iCurFrame % 10 == 0:
            if self.m_CreatePosList:
                for idx in xrange(2):
                    tPos = self.m_CreatePosList.pop(random.randint(0, len(self.m_CreatePosList) - 1))
                    self.CreateWeatherAni('magicres/eff/weather/fire.eff', 1, tPos)
                
            
        
        CWeatherBase.OnWeatherAniUpdate(self)



class CForestWeather(CWeatherBase):
    
    def __init__(self):
        CWeatherBase.__init__(self)
        self.m_CreatePosList = RandomScreenPos(6)

    
    def OnWeatherAniUpdate(self):
        if self.m_iCurFrame % 10 == 0:
            if self.m_CreatePosList:
                for idx in xrange(2):
                    tPos = self.m_CreatePosList.pop(random.randint(0, len(self.m_CreatePosList) - 1))
                    self.CreateWeatherAni('magicres/eff/weather/forest.eff', 1, tPos)
                
            
        
        CWeatherBase.OnWeatherAniUpdate(self)



def GetBlockPosList():
    global g_XYList
    import ratio
    if g_XYList:
        return g_XYList
    
    iMinX = 0
    iMinY = 0
    iMaxX = ratio.WINDOW_WIDTH
    iMaxY = ratio.WINDOW_HEIGHT
    iBlockX = (iMaxX - iMinX) / 6
    iBlockY = (iMaxY - iMinY) / 3
    g_XYList = []
    iXList = []
    iYList = []
    for idx in range(3):
        iYList.append(iMinY + (iMaxY - iMinY) * idx / 3 + iBlockY / 2)
    
    print iYList
    for idx in range(6):
        iXList.append(iMinX + (iMaxX - iMinX) * idx / 6 + iBlockX / 2)
    
    for iY in iYList:
        for iX in None:
            g_XYList.append((iX, iY))
        
    
    return g_XYList


def RandomScreenPos(iPosCount):
    lRowList = []
    for idx in range(0, 18, 3):
        lRowList.append(range(idx, idx + 3))
    
    tPosList = GetBlockPosList()
    iArgCount = iPosCount / 6
    tRetList = []
    for idx in xrange(iArgCount):
        for lst in lRowList:
            tRetList.append(tPosList[lst.pop(random.randint(0, len(lst) - 1))])
        
    
    return tRetList
