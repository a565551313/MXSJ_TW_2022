# pycdc 交叉复核产物 · script.fls entry 4118
# co_filename(原始)='script/mxgame/prettynum/prettynumrefreshlogic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4118.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2019/12/24 15:18
\xd7\xf7\xd5\xdf: hfl
\xce\xc4\xbc\xfe: \xf6\xa6\xba\xc5\xb9\xdc\xc0\xed\xc6\xf7
\t1.\xd3\xc3\xd3\xda\xf6\xa6\xba\xc5\xb5\xc4\xcb\xa2\xd0\xc2 \xd4\xdd\xca\xb1\xd6\xbb\xcb\xa2hero\xd7\xd4\xbc\xba
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import misc
import timer
g_oPretyNumRefreshLogic = None

def ModuleReset():
    global g_oPretyNumRefreshLogic
    g_oPretyNumRefreshLogic = None


def GetPrettyRefreshLogic():
    global g_oPretyNumRefreshLogic
    if not g_oPretyNumRefreshLogic:
        g_oPretyNumRefreshLogic = CPrettyNumRefreshLogic()
    
    return g_oPretyNumRefreshLogic


class CPrettyNumRefreshLogic(object):
    
    def __init__(self):
        self.m_dPlayer2NumView = { }
        self.m_dPlayer2NumTitleView = { }
        self.m_oDelayRefreshTimer = None
        self.m_lQueue = []
        self.InitSignal()

    
    def InitSignal(self):
        import hero
        oPropPrettyItem = hero.GetName2PropItem('m_iPrettyID')
        oPropPrettyItem.AddRefreshCallbackWithID('prettynummgr', self.OnHeroPrettyIDChanged_Signal)
        oPropPrettyItem = hero.GetName2PropItem('m_iFakeID')
        oPropPrettyItem.AddRefreshCallbackWithID('prettynummgr', self.OnHeroFakeIDChanged_Signal)

    
    def OnHeroPrettyIDChanged_Signal(self, *args):
        import hero
        iPlayerID = hero.GetHeroObject()
        if iPlayerID in self.m_lQueue:
            return None
        
        self.Add2RenderQueue(iPlayerID)

    
    def OnHeroFakeIDChanged_Signal(self, *args):
        import hero
        iPlayerID = hero.GetHeroObject()
        if iPlayerID in self.m_lQueue:
            return None
        
        self.Add2RenderQueue(iPlayerID)

    
    def ReleaseRefreshTimer(self):
        if not self.m_oDelayRefreshTimer:
            self.m_oDelayRefreshTimer.Release()
            self.m_oDelayRefreshTimer = None
        

    
    def Add2RenderQueue(self, iPlayerID):
        if iPlayerID in self.m_lQueue:
            return None
        
        
        try:
            None.m_lQueue.append(iPlayerID)
            if not self.m_oDelayRefreshTimer:
                self.m_oDelayRefreshTimer = timer.Timer(0.1, self.RenderLoop, -1, oRelayObj = self)
            
            return None


    
    def RenderLoop(self):
        if not self.m_lQueue:
            self.ReleaseRefreshTimer()
            return None
        
        iPlayerID = self.m_lQueue.pop(0)
        (iPrettyID, iFakeID, sTittle) = self.GetPlayerPrettyInfo(iPlayerID)
        lwrNumView = self.m_dPlayer2NumView.get(iPlayerID)
        if lwrNumView:
            lDel = []
            for wrNumView in lwrNumView:
                oNumView = wrNumView()
                if not oNumView:
                    lDel.append(wrNumView)
                    continue
                
                oNumView.SetData(iPlayerID, iPrettyID, iFakeID)
            
            for wrNumView in lDel:
                if wrNumView in lwrNumView:
                    lwrNumView.remove(wrNumView)
                    continue
            
        
        lwrNumTittleView = self.m_dPlayer2NumTitleView.get(iPlayerID)
        if lwrNumTittleView:
            lDel = []
            for wrNumTittleViewView in lwrNumTittleView:
                oNumTittleView = wrNumTittleViewView()
                if not oNumTittleView:
                    lDel.append(wrNumTittleViewView)
                    continue
                
                oNumTittleView.SetData(iPlayerID, iPrettyID, sTittle)
            
            for wrNumTittleView in lDel:
                if wrNumTittleView in lwrNumTittleView:
                    lwrNumTittleView.remove(wrNumTittleView)
                    continue
            
        

    
    def GetPlayerPrettyInfo(self, iPlayerID):
        import hero
        import friend
        iPrettyID = 0
        iFakeID = 0
        sTittle = ''
        if iPlayerID == hero.GetHeroID():
            iPrettyID = hero.GetProp('m_iPrettyID', 0)
            iFakeID = hero.GetProp('m_iFakeID', 0)
            sTittle = hero.GetProp('m_Title', '')
        else:
            oMgr = friend.GetControl()
            oPlayer = oMgr.GetUpdatePlayer(iPlayerID)
            iPrettyID = getattr(oPlayer, 'm_iPrettyID', 0)
            iFakeID = getattr(oPlayer, 'm_iFakeID', 0)
            sTittle = getattr(oPlayer, 'm_Title', '')
        return (iPrettyID, iFakeID, sTittle)

    
    def Add2RefreshLogic(self, iPlayerID, oView):
        import prettynumview
        import prettynumtitleview
        if isinstance(oView, prettynumview.CPrettyNumView):
            self.AddNumView2RefreshLogic(iPlayerID, oView)
        elif isinstance(oView, prettynumtitleview.CPrettyNumTitleView):
            self.AddNumTittleView2RefreshLogic(iPlayerID, oView)
        

    
    def AddNumView2RefreshLogic(self, iPlayerID, oNumView):
        import prettynumview
        if not isinstance(oNumView, prettynumview.CPrettyNumView):
            return None
        
        if iPlayerID not in self.m_dPlayer2NumView:
            self.m_dPlayer2NumView[iPlayerID] = []
        
        lNumObj = self.m_dPlayer2NumView[iPlayerID]
        wrObj = misc.WeakRef(oNumView)
        lNumObj.append(wrObj)
        nLen = len(lNumObj)
        for iIndex in 1;('.,(nLen):
            iRealIndex = nLen - iIndex - 1
            wrObj = lNumObj[iRealIndex]
            if not wrObj():
                lNumObj.remove(wrObj)
                continue
        

    
    def AddNumTittleView2RefreshLogic(self, iPlayerID, oNumTittleView):
        import prettynumtitleview
        if not isinstance(oNumTittleView, prettynumtitleview.CPrettyNumTitleView):
            return None
        
        if iPlayerID not in self.m_dPlayer2NumTitleView:
            self.m_dPlayer2NumTitleView[iPlayerID] = []
        
        lNumTittleObj = self.m_dPlayer2NumTitleView[iPlayerID]
        wrObj = misc.WeakRef(oNumTittleView)
        lNumTittleObj.append(wrObj)
        nLen = len(lNumTittleObj)
        for iIndex in 1;('.,(nLen):
            iRealIndex = nLen - iIndex - 1
            wrObj = lNumTittleObj[iRealIndex]
            if not wrObj():
                lNumTittleObj.remove(wrObj)
                continue
