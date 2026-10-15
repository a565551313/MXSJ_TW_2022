# pycdc 交叉复核产物 · script.fls entry 168
# co_filename(原始)='script/yard/yardedit/yardeditui/yardbrushshape.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_168.pyc (Python 2.5)

'''
cmp_yardshape:
\t\xcd\xa5\xd4\xba\xb5\xd8\xcd\xbc \xcb\xa2\xd7\xd3\xd4\xec\xd0\xcd\xa3\xba
'''
import yardalltable
import yardbrushtable
import yardviewsignal
import cmp_yardviewbase
import copy
import weakref
import yardshape
import random
import misc

class CYardBrushShapeCmp(cmp_yardviewbase.CYardCmpBase):
    
    def __init__(self, pContext, pViewMgr):
        super(CYardBrushShapeCmp, self).__init__(pContext, pViewMgr)
        self.m_iShape = None
        self.m_nCurType = None
        self.m_iSize = None
        self.m_pBlockView = None
        self.m_oBrushData = None
        self.m_oBrush2ShapeSID = None
        self.m_wrParent = None
        self.m_dGridUI = None
        self.m_vOffGrid = (0, 0)
        self.m_lRedBlock = None
        self.m_dPreviewData = None
        self.m_dOldData = None

    
    def InitBrush(self, iShape, iSize, pParent):
        self.m_iShape = iShape
        self.m_nCurType = yardalltable.GetTypeByShapeID(iShape)
        self.m_iSize = iSize
        self.m_dGridUI = { }
        self.m_wrParent = misc.WeakRef(pParent)
        oBrushData = yardalltable.GetBrushBySize(iSize)
        self.m_oBrushData = oBrushData

    
    def layoutGrid(self):
        iCenter = self.m_iSize / 2
        pS2CLogic = self.GetGridConvertLogic()
        vPos00 = pS2CLogic.Grid2Pos((iCenter, iCenter))
        (gridW, gridH) = pS2CLogic.GetUnitSize()
        for vGrid, pGridUI in self.m_dGridUI.items():
            vPosXY = pS2CLogic.Grid2Pos(vGrid)
            vPosXY = (vPosXY[0] - vPos00[0], vPosXY[1] - vPos00[1])
            (w, h) = pGridUI.GetSize()
            vPos1 = (-(w - gridW) / 2, -(h - gridH) / 2)
            vPos = (vPosXY[0] + vPos1[0], vPosXY[1] + vPos1[1])
            pGridUI.SetPos(*vPos)
        

    
    def DrawBrush(self, dPrieviewData, vOffGrid, dOldData = None):
        if not dOldData:
            dOldData = { }
        
        pParent = self.m_wrParent()
        dGridUI = self.m_dGridUI
        self.m_dGridUI = { }
        self.m_vOffGrid = vOffGrid
        sPackage = 'map'
        self.m_dPreviewData = dPrieviewData
        self.m_dOldData = dOldData
        for vGrid, lShape in dPrieviewData.iteritems():
            for nIndex, nShape in enumerate(lShape):
                (nType, nBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nShape)
                if nType != self.m_nCurType:
                    continue
                
                pOldGrid = dGridUI.get(vGrid)
                if pOldGrid and pOldGrid.m_nShapeID == nShape:
                    pGrid = pOldGrid
                else:
                    dData = yardalltable.GetDataByShapeID(nShape)
                    sPath = dData['path']
                    pGrid = yardshape.CreateShape(pParent, sPath, sPackage)
                    pGrid.m_nShapeID = nShape
                    pGrid.m_pBlockView = None
                pGrid.SetZ(1)
                self.m_dGridUI[vGrid] = pGrid
                lShape.remove(nShape)
            
        
        self.layoutGrid()
        yardviewsignal.Emit(yardviewsignal.SS_BrushModifyGrid, dPrieviewData, vOffGrid)

    
    def GetBrushInfo(self):
        return dict(self.m_oBrushData)

    
    def RefreshBlock(self):
        import yarddefines
        if not self.m_dPreviewData:
            return None
        
        if self.m_nCurType != yarddefines.E_UNIT_LAND_WATER:
            self.RefreshBrushLandBlock()
        else:
            self.RefreshBrushWaterBlock()

    
    def RefreshBrushLandBlock(self):
        import yarddefines
        import yardeditblockview
        pBlockLogic = self.GetBlockLogic()
        pGridConvertLogic = self.GetGridConvertLogic()
        self.m_pBlockView = None
        self.m_lRedBlock = []
        lNewBlock = []
        for vGrid, lID in self.m_dPreviewData.iteritems():
            for nIndex, nShapeID in enumerate(lID):
                (nType, nBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nShapeID)
                if nType != yarddefines.E_UNIT_LAND_WATER:
                    continue
                
                lTBlock = pBlockLogic.GetWaterBlockByShapeID(nShapeID)
                if not lTBlock:
                    return None
                
                vMapGrid = (self.m_vOffGrid[0] + vGrid[0], self.m_vOffGrid[1] + vGrid[1])
                vMapPos = pGridConvertLogic.Server2ClientPos(vMapGrid)
                vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vMapPos)
                for vBlock in lTBlock:
                    vBlockNew = (vMapCell[0] + vBlock[0], vMapCell[1] + vBlock[1])
                    if vBlockNew not in lNewBlock:
                        lNewBlock.append(vBlockNew)
                        continue
                
            
        
        lOldBlock = []
        for vGrid, lID in self.m_dOldData.iteritems():
            for nShapeID in lID:
                (nType, nBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nShapeID)
                if nType != yarddefines.E_UNIT_LAND_WATER:
                    continue
                
                lTBlock = pBlockLogic.GetWaterBlockByShapeID(nShapeID)
                if not lTBlock:
                    return None
                
                vMapPos = pGridConvertLogic.Server2ClientPos(vGrid)
                vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vMapPos)
                for vBlock in lTBlock:
                    vBlockNew = (vMapCell[0] + vBlock[0], vMapCell[1] + vBlock[1])
                    if vBlockNew not in lOldBlock:
                        lOldBlock.append(vBlockNew)
                        continue
                
            
        
        lDelBlock = []
        for vBlock in lOldBlock:
            if vBlock not in lNewBlock:
                lDelBlock.append(vBlock)
                continue
        
        if not lDelBlock:
            return None
        
        vMapPos = pGridConvertLogic.Server2ClientPos(self.m_vOffGrid)
        vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vMapPos)
        lRealAllBlock = []
        for vBlock in lDelBlock:
            lRealAllBlock.append((vBlock[0] - vMapCell[0], vBlock[1] - vMapCell[1]))
        
        dConfig = {
            'out': (yarddefines.E_BLOCK_TYPE_FUR_W,) }
        lRedAllBlock = pBlockLogic.CalBlockByConfig(lRealAllBlock, vMapCell, dConfig)
        self.m_lRedBlock = lRedAllBlock
        if not lRealAllBlock:
            return None
        
        pParent = self.m_wrParent()
        self.m_pBlockView = yardeditblockview.CYardMapItemBlock(pParent)
        self.m_pBlockView.SetData(lRedAllBlock)
        self.m_pBlockView.SetZ(2)
        for vBlock in lRedAllBlock:
            None.None = None
            None.m_pBlockView.SetBlockRed(vBlock, True)
        
        self.m_pBlockView.SetPos(-80, 0)

    
    def RefreshBrushWaterBlock(self):
        import yarddefines
        import yardeditblockview
        self.m_pBlockView = None
        self.m_lRedBlock = []
        pBlockLogic = self.GetBlockLogic()
        pGridConvertLogic = self.GetGridConvertLogic()
        lAllBlock = []
        for vGrid, pGrid in self.m_dGridUI.iteritems():
            nShapeID = pGrid.m_nShapeID
            (nType, nBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nShapeID)
            if nType != yarddefines.E_UNIT_LAND_WATER:
                continue
            
            lTBlock = pBlockLogic.GetWaterBlockByShapeID(nShapeID)
            if not lTBlock:
                return None
            
            vMapGrid = (self.m_vOffGrid[0] + vGrid[0], self.m_vOffGrid[1] + vGrid[1])
            vMapPos = pGridConvertLogic.Server2ClientPos(vMapGrid)
            vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vMapPos)
            for vBlock in lTBlock:
                vBlockNew = (vMapCell[0] + vBlock[0], vMapCell[1] + vBlock[1])
                if vBlockNew not in lAllBlock:
                    lAllBlock.append(vBlockNew)
                    continue
            
        
        vMapPos = pGridConvertLogic.Server2ClientPos(self.m_vOffGrid)
        vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vMapPos)
        lRealAllBlock = []
        for vBlock in lAllBlock:
            lRealAllBlock.append((vBlock[0] - vMapCell[0], vBlock[1] - vMapCell[1]))
        
        lRedAllBlock = pBlockLogic.CalBlock(lRealAllBlock, vMapCell, yarddefines.E_UNIT_LAND_WATER)
        pParent = self.m_wrParent()
        self.m_pBlockView = yardeditblockview.CYardMapItemBlock(pParent)
        self.m_pBlockView.SetData(lRealAllBlock)
        self.m_pBlockView.SetZ(2)
        for vBlock in lRealAllBlock:
            bRed = vBlock in lRedAllBlock
            self.m_pBlockView.SetBlockRed(vBlock, bRed)
        
        self.m_lRedBlock = lRedAllBlock
        self.m_pBlockView.SetPos(-80, 0)

    
    def GetPlaceBlock(self):
        return self.m_lRedBlock
