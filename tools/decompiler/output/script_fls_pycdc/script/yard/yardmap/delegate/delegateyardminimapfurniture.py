# pycdc 交叉复核产物 · script.fls entry 899
# co_filename(原始)='script/yard/yardmap/delegate/delegateyardminimapfurniture.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_899.pyc (Python 2.5)

'''
delegateyardmap.py
create by hfl 2019/8/16 16:26

1.\xbc\xd3\xd4\xd8\xb5\xd8\xbf\xe9
2.\xbc\xd3\xd4\xd8furniture

\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import delegateyardminimapbase
import interface
import yardmapdefines
import timer
import yardmaptable
import yardmapz
import newfurnituredata
E_SPECIAL_SHAPE = (29303, 29314)

class CDelegateYardMiniMapFurniture(delegateyardminimapbase.CDelegateYardMiniMapBase):
    
    def __init__(self, pView, pContext):
        delegateyardminimapbase.CDelegateYardMiniMapBase.__init__(self, pView, pContext)
        self.m_nCurRenderIndex = 0
        self.m_dFurniture = { }
        self.m_oRenderGridTimer = None
        self.m_lQueue = []
        self.m_iRenderFurNumOnce = yardmapdefines.E_DRAW_FURNITRUE_ONCE_MINIMAP
        self.InitMapSizeInfo()
        self.InitSignal()

    
    def InitMapSizeInfo(self):
        nMapID = self.GetContext().GetMapID()
        (self.m_Width, self.m_Height) = yardmaptable.GetMapData(nMapID)['mapsize']
        self.m_Width = self.m_Width
        self.m_Height = self.m_Height
        self.m_nBaseZ = self.m_Height + self.m_Width

    
    def InitSignal(self):
        import yardsignal
        yardsignal.Connect(yardsignal.SS_YARD_FURNITURE_UPDATE, self.UpdateYardFurniture)
        yardsignal.Connect(yardsignal.SS_YARD_FURNITURE_ADD, self.OnYardFurnitureAdd_Signal)
        yardsignal.Connect(yardsignal.SS_YARD_FURNITURE_DEL, self.OnYardFurnitureDel_Signal)
        yardsignal.Connect(yardsignal.SS_YARD_FURNITURE_PLANT_UPDATE, self.UpdateYardFurniturePlant)

    
    def OnYardFurnitureAdd_Signal(self, oDataMgr, tFurnitureInfo):
        if oDataMgr != self.GetYardDataMgr():
            return None
        
        (vPos, \xca\xe7\xc0fo) = tFurnitureInfo
        self.RenderOneFurniture(vPos, \xca\xe7\xc0fo)

    
    def OnYardFurnitureDel_Signal(self, oDataMgr, tFurnitureInfo):
        if oDataMgr != self.GetYardDataMgr():
            return None
        
        (vPos, furnitureInfo) = tFurnitureInfo
        shapeID = furnitureInfo['shapeID']
        nDirect = furnitureInfo['direct']
        self.DelFurniture(vPos, shapeID, nDirect)

    
    def UpdateYardFurniturePlant(self, lKey):
        oYardDataMgr = self.GetYardDataMgr()
        oMiniMapConvertLogic = self.GetMiniGridConvertLogic()
        for tKey in lKey:
            lPlant = oYardDataMgr.GetPlantInFurniture(tKey)
            oFurniture = self.GetFurniture(*tKey)
            if oFurniture:
                oFurniture.InitPlant(lPlant, oMiniMapConvertLogic)
                continue
        

    
    def UpdateYardFurniture(self, pContext):
        if pContext != self.GetYardDataMgr():
            return None
        
        self.Clear()
        self.RenderMiniMapFur()

    
    def Clear(self):
        self.ReleaseRenderTimer()
        self.m_lQueue = []
        self.m_dFurniture = { }
        self.m_nCurRenderIndex = 0

    
    def RenderMiniMapFur(self):
        self.InitMapSizeInfo()
        self.m_lQueue = []
        oYardDataMgr = self.GetYardDataMgr()
        if not oYardDataMgr.GetAllFurniture():
            self.UpdateRenderStateToFinish()
            return None
        
        dAllFurniture = oYardDataMgr.GetAllFurniture()
        self.m_lQueue = dAllFurniture.keys()
        iSumFur = len(self.m_lQueue)
        self.m_iRenderFurNumOnce = max(iSumFur / 60, yardmapdefines.E_DRAW_FURNITRUE_ONCE_MINIMAP)
        self.m_nCurRenderIndex = 0
        if self.m_lQueue:
            if not self.m_oRenderGridTimer:
                self.m_oRenderGridTimer = timer.Timer(0.04, self.RendeFurnitureLoop, -1, oRelayObj = self)
            
        else:
            self.ReleaseRenderTimer()

    
    def ReleaseRenderTimer(self):
        if self.m_oRenderGridTimer:
            self.m_oRenderGridTimer.Release()
            self.m_oRenderGridTimer = None
        

    
    def RendeFurnitureLoop(self):
        if self.m_nCurRenderIndex >= len(self.m_lQueue):
            self.ReleaseRenderTimer()
            self.UpdateRenderStateToFinish()
            return None
        
        nStart = self.m_nCurRenderIndex
        nEnd = min(self.m_nCurRenderIndex + self.m_iRenderFurNumOnce, len(self.m_lQueue))
        if nEnd > len(self.m_lQueue):
            return None
        
        self.m_nCurRenderIndex = nEnd
        oDataMgr = self.GetYardDataMgr()
        for i in range(nStart, nEnd):
            vPos = self.m_lQueue[i]
            lFurInfo = oDataMgr.GetFurnitureByPos(vPos)
            for dFurInfo in lFurInfo:
                self.RenderOneFurniture(vPos, dFurInfo)
            
        

    
    def AddUnit(self, vPos, shapeID, nDirect, oUnit):
        if vPos not in self.m_dFurniture:
            self.m_dFurniture[vPos] = { }
        
        dUnit = self.m_dFurniture[vPos]
        dUnit[(shapeID, nDirect)] = oUnit

    
    def DelFurniture(self, vPos, shapeID, nDirect):
        if vPos not in self.m_dFurniture:
            return None
        
        dFur = self.m_dFurniture[vPos]
        tID = (shapeID, nDirect)
        if tID not in dFur:
            return None
        
        del dFur[tID]

    
    def GetFurniture(self, vPos, shapeID, nDirect):
        if vPos not in self.m_dFurniture:
            return None
        
        dFur = self.m_dFurniture[vPos]
        tID = (shapeID, nDirect)
        if tID in dFur:
            return dFur.get(tID)
        else:
            return None

    
    def RenderOneFurniture(self, vServerPos, dFurInfo):
        nShapeID = dFurInfo['shapeID']
        nDirect = dFurInfo['direct']
        oParent = self.GetView().GetFurParent()
        oMiniMapConvertLogic = self.GetMiniGridConvertLogic()
        oGridConvertLogic = self.GetGridConvertLogic()
        oYardDataMgr = self.GetYardDataMgr()
        vPos = oGridConvertLogic.FurnitureServerPos2WorldPos(vServerPos, nShapeID, nDirect)
        (x, y) = oMiniMapConvertLogic.ClientPos2MiniMap(vPos)
        (fScale, _) = oMiniMapConvertLogic.GetScale()
        fScale = 1 / fScale
        oUnit = CYardFurnitureScale(oParent, nShapeID, nDirect)
        oUnit.SetScale(fScale)
        oUnit.SetPos(x, y)
        tID = (vServerPos, nShapeID, nDirect)
        dPlantInfo = oYardDataMgr.GetPlantInFurniture(tID)
        oUnit.InitPlant(dPlantInfo, oMiniMapConvertLogic)
        iRate = newfurnituredata.GetFurZOffY(nShapeID)
        vOffPos = oGridConvertLogic.GetFurOffPos(nShapeID, nDirect)
        vPos = (vPos[0] + vOffPos[0], vPos[1] + vOffPos[1])
        if iRate:
            (_, iSizeH) = oUnit.GetSize()
            vPos = (vPos[0], vPos[1] - int(iSizeH / iRate))
        
        z = yardmapz.GetFurnitureZByType(0, vPos[0], vPos[1], nShapeID)
        oUnit.SetZ(int(z))
        self.AddUnit(vServerPos, nShapeID, nDirect, oUnit)

    
    def UpdateRenderStateToFinish(self):
        if hasattr(self.GetView(), 'UpdateRenderState'):
            self.GetView().UpdateRenderState({
                'bFurnitureRender': True })
        



class CYardFurnitureScale(interface.CStretchImagesObject):
    Z_BORDER = -1
    
    def __init__(self, oParent, iShapeID, iDirect):
        import newfurnituredata
        (sPackage, sFileName) = newfurnituredata.GetFurStablePath(iShapeID, iDirect)
        if iShapeID in E_SPECIAL_SHAPE:
            sFileName = sFileName.replace('.igs', '_min.igs')
        
        self.m_fScale = 1
        self.m_nDirect = iDirect
        interface.CStretchImagesObject.__init__(self, oParent, sFileName, sPackage)
        self.m_oSubPartList = []
        sFileType = newfurnituredata.GetFurnitureType(iShapeID)
        if sFileType == '\xaa\xe1\xaeE':
            oBorder = interface.CStretchImagesObject(self, sFileName.replace('.igs', '1.igs'), sPackage)
            oBorder.SetZ(self.Z_BORDER)
            self.m_oSubPartList.append(oBorder)
        
        self.m_dPlant = { }
        self.m_bScale = True

    
    def IsScale(self):
        return self.m_bScale

    
    def SetScale(self, fScale):
        self.m_fScale = fScale
        interface.CStretchImagesObject.SetScale(self, fScale)
        for oSubPart in self.m_oSubPartList:
            oSubPart.SetScale(fScale)
        

    
    def InitPlant(self, dPlantInfoList, oMiniConvertLogic):
        self.m_dPlant = { }
        for dPlantInfo in dPlantInfoList:
            self.PlacePlant(dPlantInfo['iType'], dPlantInfo['iPos'], dPlantInfo['iPic'], dPlantInfo['iColor'], oMiniConvertLogic)
        

    
    def ClearPlant(self):
        self.m_dPlant = { }

    
    def PlacePlant(self, iType, iPos, iPic, iPal, oMiniConvertLogic):
        import yarditemminimapfarm
        import garth
        iState = iPic & 1
        iPhase = iPic >> 1
        if iType not in garth.PLANT_INFO_DATA:
            return None
        
        tInfo = garth.PLANT_INFO_DATA[iType]
        iIndex = min(len(tInfo) - 1, 1 + iState * 3 + iPhase)
        iSpecialType = tInfo[iIndex]
        if iSpecialType == 0:
            sFilename = 'furniture\\plant\\%.2d%d%d%d.igs' % (iType, self.m_nDirect, iPhase + 1, iState)
        else:
            sFilename = 'furniture\\plant\\%d%d%d%d.igs' % (iSpecialType, self.m_nDirect, iPhase + 1, iState)
        if tInfo[0] == 1:
            (iOffsetX, iOffsetY) = garth.PLANT_POS_DATA[self.m_nDirect * 2 + iPos]
        else:
            (iOffsetX, iOffsetY) = garth.PLANT_POS_DATA[0]
        
        try:
            oPlant = yarditemminimapfarm.CPlantIcon(self, sFilename, iPal)
            vPos = oMiniConvertLogic.ClientPos2MiniMap((iOffsetX, iOffsetY))
            oPlant.SetPos(*vPos)
            oPlant.SetZ(0)
            oPlant.SetScale(self.m_fScale)
            self.m_dPlant[iPos] = oPlant
        except:
            return None
