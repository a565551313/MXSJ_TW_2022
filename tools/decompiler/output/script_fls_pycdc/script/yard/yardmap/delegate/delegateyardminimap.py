# pycdc 交叉复核产物 · script.fls entry 4950
# co_filename(原始)='script/yard/yardmap/delegate/delegateyardminimap.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4950.pyc (Python 2.5)

'''
delegateyardmap.py
create by hfl 2019/6/27 16:26
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import delegateyardbase
import yardmapdefines
import timer
import yardalltable
import yardshape
import yards2ctools

class CDelegateYardMiniMap(delegateyardbase.CDelegateYardBase):
    
    def __init__(self, pView, pContext):
        delegateyardbase.CDelegateYardBase.__init__(self, pView, pContext)
        self.m_nMaxGridID = 0
        self.m_nCurLoadGridID = 0
        self.m_dUnit = { }
        self.m_pRenderGridTimer = None
        self.m_pCheckPosTimer = None
        self.InitSignal()

    
    def InitSignal(self):
        import yardsignal
        yardsignal.Connect(yardsignal.SS_YARD_LAND_UPDATE, self.UpdateYardLand)
        yardsignal.Connect(yardsignal.SS_YARD_LANDGRID_CHANGED, self.OnYardLandChanged_Signal)
        import yardviewsignal
        yardviewsignal.Connect(yardviewsignal.SS_UpdateHeroPosition, self.OnUpdateHeroPosition)

    
    def OnYardLandChanged_Signal(self, pDataMgr, vGrid, lLandID, lOldID):
        if pDataMgr != self.GetYardDataMgr():
            return None
        
        if lOldID:
            dUnit = self.m_dUnit.get(vGrid, { })
            for nShapeID in lOldID:
                if nShapeID in dUnit:
                    del dUnit[nShapeID]
                    continue
            
        
        for nIndex, nID in enumerate(lLandID):
            self.RenderGridUnit(vGrid, nID, nIndex)
        

    
    def OnUpdateHeroPosition(self):
        pMiniMap = self.GetView()
        pMiniMap.UpdateHeroPosition()

    
    def UpdateYardLand(self, pContext):
        if pContext != self.GetYardDataMgr():
            return None
        
        self.Clear()
        self.RenderMiniMapUnits()

    
    def Clear(self):
        self.ReleaseRenderTimer()
        self.m_dUnit = { }
        self.m_nMaxGridID = 0
        self.m_nCurLoadGridID = 0

    
    def RenderMiniMap(self):
        self.RenderMiniMapUnits()

    
    def RenderMiniMapUnits(self):
        pYardDataMgr = self.GetYardDataMgr()
        if not pYardDataMgr.GetAllLandData():
            self.UpdateRenderStateToFinish()
            return None
        
        pGridConvertLogic = self.GetGridConvertLogic()
        vMaxSize = pGridConvertLogic.GetMaxGrid()
        tRange = (-vMaxSize[0], vMaxSize[0], -vMaxSize[0], vMaxSize[1])
        if tRange:
            self.m_nMaxGridID = tRange
            if self.m_nMaxGridID:
                if not self.m_pRenderGridTimer:
                    self.m_pRenderGridTimer = timer.Timer(0.04, self.RenderGridLoop, -1, oRelayObj = self)
                
            else:
                self.ReleaseRenderTimer()

    
    def ReleaseRenderTimer(self):
        if self.m_pRenderGridTimer:
            self.UpdateRenderStateToFinish()
            self.m_pRenderGridTimer.Release()
            self.m_pRenderGridTimer = None
        

    
    def RenderGridLoop(self):
        if self.m_nCurLoadGridID >= self.m_nMaxGridID:
            self.ReleaseRenderTimer()
            return None
        
        lGrid = self.CalRenderRange()
        for vGrid in lGrid:
            self.RenderGridUnits(vGrid)
        

    
    def CalRenderRange(self):
        lGrid = []
        nEnd = self.m_nCurLoadGridID
        pDataMgr = self.GetYardDataMgr()
        while len(lGrid) < yardmapdefines.E_DRAW_ONCE_MINIMAP and nEnd < self.m_nMaxGridID:
            vGrid = yards2ctools.ID2Pos(nEnd)
            if pDataMgr.GetLand(vGrid):
                lGrid.append(vGrid)
            
            nEnd += 1
        self.m_nCurLoadGridID = nEnd
        return lGrid

    
    def AddUnit(self, vPos, shapeID, pUnit):
        if vPos not in self.m_dUnit:
            self.m_dUnit[vPos] = { }
        
        dUnit = self.m_dUnit[vPos]
        dUnit[shapeID] = pUnit

    
    def RenderGridUnits(self, vGrid):
        pDataMgr = self.GetYardDataMgr()
        lID = pDataMgr.GetLand(vGrid)
        if not lID:
            return None
        
        for nIndex, nID in enumerate(lID):
            self.RenderGridUnit(vGrid, nID, nIndex)
        

    
    def RenderGridUnit(self, vServerPos, nShape, nIndex):
        pParent = self.GetView().GetLandParent()
        pGridConvertLogic = self.GetGridConvertLogic()
        pMiniMapConverLogic = self.GetMiniGridConvertLogic()
        vPos = pGridConvertLogic.Server2ClientPos(vServerPos)
        (x, y) = pMiniMapConverLogic.ClientPos2MiniMap(vPos)
        (sPath, sPackage) = yardalltable.GetResVPathByShape(nShape)
        (sPath, sPackage) = pMiniMapConverLogic.Convert2MiniMapResPath(sPath, sPackage)
        pObj = yardshape.CreateShape(pParent, sPath, sPackage)
        pObj.SetZ((1000 + x - y) + nIndex)
        pObj.SetPos(int(x), int(y))
        self.AddUnit(vServerPos, nShape, pObj)

    
    def GetNpcPoint(self):
        pDataMgr = self.GetYardDataMgr()
        lStableNpc = pDataMgr.GetAllStableNpc(bAll = True)
        lst = []
        for dNpc in lStableNpc.itervalues():
            v = (dNpc['name'], None, 0, 1, dNpc['vpos'], 0, None, 255, 'l', dNpc['shapeID'])
            lst.append(v)
        
        return lst

    
    def UpdateRenderStateToFinish(self):
        if hasattr(self.GetView(), 'UpdateRenderState'):
            self.GetView().UpdateRenderState({
                'bLandRender': True })
