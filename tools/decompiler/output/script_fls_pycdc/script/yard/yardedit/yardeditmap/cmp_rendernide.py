# pycdc 交叉复核产物 · script.fls entry 1009
# co_filename(原始)='script/yard/yardedit/yardeditmap/cmp_rendernide.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1009.pyc (Python 2.5)

'''
\xd0\xa1\xce\xd1\xce\xc4\xbc\xfe
'''
import cmp_yardviewbase
import yarddefines
import timer
import yarditemnide
import yardothers
E_DRAW_ONCE = 2

class CYardCmpDrawNide(cmp_yardviewbase.CYardCmpBase):
    
    def __init__(self, pContext, pViewMgr):
        cmp_yardviewbase.CYardCmpBase.__init__(self, pContext, pViewMgr)
        self.m_pTimer = None
        self.m_dNideUI = { }
        self.m_lNideConfig = []
        self.m_nStartIndex = 0
        self.InitSignal()

    
    def InitSignal(self):
        import yardsignal
        yardsignal.Connect(yardsignal.SS_YARD_EDITEX_ATTRCHANGED, self.OnHideNideIfNeeded_Signal)
        yardsignal.Connect(yardsignal.SS_YARD_ANIMAL_ATTR_CHANGED, self.OnYardNideAttrRefresh_Signal)

    
    def OnHideNideIfNeeded_Signal(self, oYardDataMgr, sKey, pValue, pOldValue):
        if self.GetYardDataMgr() != oYardDataMgr:
            return None
        
        if sKey != 'nSelectShape':
            return None
        
        if pValue in self.m_dNideUI:
            oAni = self.m_dNideUI[pValue]
            oAni.SetShow(False)
        elif pOldValue in self.m_dNideUI:
            oAni = self.m_dNideUI[pOldValue]
            oAni.SetShow(True)
        

    
    def OnYardNideAttrRefresh_Signal(self, oYardDataMgr, nideID, sKey, *args):
        if self.GetYardDataMgr() != oYardDataMgr:
            return None
        
        if sKey not in ('vpos',):
            return None
        
        if nideID in self.m_dNideUI:
            del self.m_dNideUI[nideID]
        
        oParent = self.GetViewMgr().GetLayerByType(yarddefines.E_UNIT_FUNITURE)
        self.RenderOneNide(nideID, oParent)

    
    def AddNide(self, nideID, oAni):
        self.m_dNideUI[nideID] = oAni

    
    def ReleaseTimer(self):
        if self.m_pTimer:
            self.m_pTimer.Release()
            self.m_pTimer = None
        

    
    def RenderNide(self):
        self.ReleaseTimer()
        pDataMgr = self.GetYardDataMgr()
        dAllAnimal = pDataMgr.GetAllAnimal()
        self.m_lNideConfig = []
        for iID, dInfo in dAllAnimal.iteritems():
            if yardothers.IsAniNideType(dInfo['iType']):
                self.m_lNideConfig.append(iID)
                continue
        
        if not self.m_lNideConfig:
            return None
        
        self.m_nStartIndex = 0
        self.m_pTimer = timer.Timer(0.033, self.RendeNideLoop, -1, oRelayObj = self)

    
    def RendeNideLoop(self):
        nLen = len(self.m_lNideConfig)
        if nLen <= self.m_nStartIndex:
            self.ReleaseTimer()
            return None
        
        nStart = self.m_nStartIndex
        nEnd = min(nLen, nStart + E_DRAW_ONCE)
        self.m_nStartIndex = nEnd
        lData = self.m_lNideConfig[nStart:nEnd]
        oParent = self.GetViewMgr().GetLayerByType(yarddefines.E_UNIT_FUNITURE)
        for iNideID in lData:
            self.RenderOneNide(iNideID, oParent)
        

    
    def RenderOneNide(self, nideID, oParent):
        import yardothers
        oYardDataMgr = self.GetYardDataMgr()
        dNideInfo = oYardDataMgr.GetAnimalByIdx(nideID)
        if not dNideInfo:
            raise None, None, None
            None('\xa4\xa3\xa6s\xa6b\xaa\xbaNide')
            return None
        
        oConvertLogic = self.GetGridConvertLogic()
        vWorldPos = (dNideInfo['x'], dNideInfo['y'])
        vServerPos = oConvertLogic.WorldPos2ServerMapPos(vWorldPos)
        iShapeID = yardothers.GetAniNideShapeID(dNideInfo['iType'])
        tID = (vServerPos, nideID, 0)
        oNide = yarditemnide.CNideObj(oParent, dNideInfo['x'], dNideInfo['y'], dNideInfo['iIdx'], iShapeID, 0)
        oNide.SetIsOpTargetFlag(True)
        oNide.SetSeverPos(vServerPos)
        oNide.MessageProcess()
        oNide.SetID(tID)
        oNide.SetPos(*vWorldPos)
        iZ = oConvertLogic.GetFurZByServerPos(vServerPos, 0)
        oNide.SetZ(iZ)
        self.AddNide(nideID, oNide)
        pBlock = self.DrawBlock(vServerPos, iShapeID)
        oNide.m_pBlock = pBlock

    
    def DrawBlock(self, vWorldPos, iType):
        import yardeditblockview
        pBlockLogic = self.GetBlockLogic()
        lBlock = pBlockLogic.GetFurnitureBlock(iType, 0, vWorldPos, pBlockLogic.GetFurnitureBlockTypesByShapeID(iType)[0])
        if not lBlock:
            return None
        
        pViewMgr = self.GetViewMgr()
        oParent = pViewMgr.GetLayerByType(yarddefines.E_UNIT_BLOCK)
        pBlockView = yardeditblockview.CYardMapItemBlock(oParent, 64)
        pBlockView.SetData(lBlock)
        pBlockView.SetBlockMode(0)
        pBlockView.SetPos(*vWorldPos)
        return pBlockView
