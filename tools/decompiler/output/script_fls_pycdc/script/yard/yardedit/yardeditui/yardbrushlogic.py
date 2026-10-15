# pycdc 交叉复核产物 · script.fls entry 2148
# co_filename(原始)='script/yard/yardedit/yardeditui/yardbrushlogic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2148.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: hufenlin
\xc3\xe8\xca\xf6: \xc1\xc4\xcc\xec\xc6\xf8\xc5\xdd\xcf\xd4\xca\xbe\xca\xfd\xc1\xbf\xbf\xd8\xd6\xc6
yardbrushlogic:
\t\xcb\xa2\xd7\xd3\xa3\xba\xcb\xa2\xb5\xd8\xc2\xdf\xbc\xad

================================================================================
'''
import yarddefines
import yardalltable
import yardbackpreoplogic
import yardbrushtable
import misc
import yardothers

class CBrushLogic(object):
    
    def __init__(self, pEditContext):
        self.m_wrContext = misc.WeakRef(pEditContext)
        self.m_oBackPreLogic = yardbackpreoplogic.CYardBackPreLogic(pEditContext)

    
    def GetContext(self):
        ''':rtype: yardeditcontext.CYardEditContext'''
        return self.m_wrContext()

    
    def GetBackPreLogic(self):
        return self.m_oBackPreLogic

    
    def ID2ClientID(self, sID):
        return '%s_new' % sID

    
    def FiltLandGrass(self, lID):
        lTID = []
        if not lID:
            return lTID
        
        for nShapeID in lID:
            (nType, _) = yardalltable.ParserLandShapeID2TypeAndBrushID(nShapeID)
            if nType == yarddefines.E_UNIT_LAND_GRASS:
                continue
            
            lTID.append(nShapeID)
        
        return lTID

    
    def CalLandCost(self, lNew, lOld):
        '''
\t\t:param lNew:
\t\t:param lOld:
\t\t:return:
\t\t'''
        dNewType = { }
        dOldType = { }
        for nID in lNew:
            nType = yardalltable.GetTypeByShapeID(nID)
            dNewType[nType] = dNewType.get(nType, 0) + 1
        
        for nID in lOld:
            nType = yardalltable.GetTypeByShapeID(nID)
            dOldType[nType] = dOldType.get(nType, 0) + 1
        
        dCost = { }
        for nType in (yarddefines.E_UNIT_LAND_WATER, yarddefines.E_UNIT_LAND_SAND):
            nNew = dNewType.get(nType, 0)
            nOld = dOldType.get(nType, 0)
            nCost = nNew - nOld
            dCost[nType] = nCost
        
        return dCost

    
    def Brush(self, dResult, dOldResult, bEvent = True):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        if not dResult:
            return None
        
        dEvent = {
            'land': { } }
        dLand = dEvent['land']
        lNew = []
        for vGrid, lID in dResult.iteritems():
            lID = self.FiltLandGrass(lID)
            lNew.extend(lID)
            dLand[vGrid] = {
                'new': lID }
        
        lOld = []
        for vGrid, lID in dOldResult.iteritems():
            if vGrid not in dLand:
                dLand[vGrid] = { }
            
            lID = self.FiltLandGrass(lID)
            lOld.extend(lID)
            dLand[vGrid]['old'] = list(lID)
        
        for vGrid, lShape in dResult.iteritems():
            lShape = self.FiltLandGrass(lShape)
            oDataMgr.SetLand(vGrid, lShape)
        
        pBagDataMgr = oContext.GetYardBagDataMgr()
        dCost = self.CalLandCost(lNew, lOld)
        for nType, nNum in dCost.iteritems():
            nBaseID = yardalltable.GetShapeBaseIDByType(nType)
            pItem = pBagDataMgr.GetLandItem(nBaseID)
            pItem.UseItem(nNum)
        
        dEvent['useland'] = dCost
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def CalPreviewBrushResult(self, dConfig):
        dBrushInfo = dConfig['brushinfo']
        vOffGrid = dConfig['voffgrid']
        bPreview = dConfig.get('bPreview', False)
        shape = dConfig['shape']
        nNewType = yardalltable.GetTypeByShapeID(shape)
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        dResult = { }
        dOldResult = { }
        lNewList = []
        lOldList = []
        for vGrid in dBrushInfo.keys():
            nNewBrushID = dBrushInfo[vGrid]
            vRealGrid = (vGrid[0] + vOffGrid[0], vGrid[1] + vOffGrid[1])
            lID = oDataMgr.GetLand(vRealGrid, [])
            lID = list(lID)
            lNewID = []
            nSaveID = yardalltable.PackTypeAndBrushID2LandShapeID(nNewType, nNewBrushID)
            for nID in lID:
                (nType, nBaseBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nID)
                if nType == nNewType:
                    nNewBrushID = yardbrushtable.CalLinkBrushID(nNewBrushID, nBaseBrushID)
                    nSaveID = yardalltable.PackTypeAndBrushID2LandShapeID(nNewType, nNewBrushID)
                    continue
            
            for nID in lID:
                (nType, nBaseBrushID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nID)
                if nType == nNewType:
                    continue
                    continue
                nTemRealBrush = yardbrushtable.CalLinkBrushDel(nNewBrushID, nBaseBrushID)
                if nTemRealBrush:
                    nTID = yardalltable.PackTypeAndBrushID2LandShapeID(nType, nTemRealBrush)
                    lNewID.append(nTID)
                    continue
            
            lNewID.append(nSaveID)
            if lNewID == lID:
                continue
            
            if bPreview:
                dResult[vGrid] = lNewID
            else:
                dResult[vRealGrid] = lNewID
            lNewList.extend(lNewID)
            lOldList.extend(lID)
            dOldResult[vRealGrid] = lID
        
        dCost = self.CalLandCost(lNewList, lOldList)
        return (dResult, dOldResult, dCost)

    
    def BrushDel(self, vScreenPos, nShapeID, bEvent = True):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vOffGrid = oDataMgr.GetAttrByKey('vPos')
        pGridConvertLogic = oContext.GetGridConvertLogic()
        vGrid = pGridConvertLogic.CalWindowPos2Grid(vOffGrid, vScreenPos, False)
        dTableData = yardalltable.GetDataByShapeID(nShapeID)
        nType = dTableData['type']
        if not vGrid:
            return None
        
        lID = oDataMgr.GetLand(vGrid)
        if not lID:
            return None
        
        lCopyID = list(lID)
        bChange = False
        for nID in lCopyID:
            (nTempType, nShapeID) = yardalltable.ParserLandShapeID2TypeAndBrushID(nID)
            if nType == nTempType:
                lCopyID.remove(nID)
                bChange = True
                break
                continue
        
        if not bChange:
            return None
        
        oDataMgr.SetLand(vGrid, list(lCopyID))
        dEvent = { }
        dEvent['land'] = {
            vGrid: {
                'old': list(lID),
                'new': lCopyID } }
        yardothers.ShowEditDelFurTips(nShapeID)
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def DelFurntirue(self, dFur, bEvent = True):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vPos = dFur['vpos']
        nShapeID = dFur['shapeID']
        yardothers.ShowEditSuitBeautyTipsIfNeeded(nShapeID, False)
        oDataMgr.DelFurniture(vPos, dFur)
        pBagDataMgr = oContext.GetYardBagDataMgr()
        pFurItem = pBagDataMgr.GetFurItem(nShapeID)
        pFurItem.RecicleItem()
        dEvent = {
            'furnituredel': dict(dFur),
            'recicleitem': {
                'shapeID': nShapeID } }
        yardothers.ShowEditDelFurTips(nShapeID)
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def ReplaceFurniture(self, dDelFur, dAddFur, bEvent = True):
        '''\xa5\xd8\xabe\xa5u\xb9\xea\xb2{\xb4\xc0\xb4\xab\xac\xdb\xa6P\xa4\xe8\xa6V\xaa\xba\xb3\xc3\xa8\xe3
\t\t:param dDelFur:
\t\t:param dAddFur:
\t\t:return:
\t\t'''
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vPos = dDelFur['vpos']
        oDataMgr.DelFurniture(vPos, dDelFur)
        vPos = dAddFur['vpos']
        oDataMgr.AddFurniture(vPos, dAddFur)
        dEvent = {
            'furnitureadd': dict(dAddFur),
            'furnituredel': dict(dDelFur) }
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def IsSameFur(self, dResult):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vPos = dResult['vpos']
        nShapeID = dResult['shapeID']
        direct = dResult.get('direct', 0)
        lFur = oDataMgr.GetFurnitureByPos(vPos)
        if not lFur:
            return False
        
        for dFur in lFur:
            nTShapeID = dFur['shapeID']
            nTDirect = dFur['direct']
            if nTShapeID == nShapeID and nTDirect == direct:
                return True
                continue
        
        return False

    
    def BrushFurniture(self, dResult, bBrushByBag = False, bEvent = True):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        pBagDataMgr = oContext.GetYardBagDataMgr()
        vPos = dResult['vpos']
        nShapeID = dResult['shapeID']
        dAdd = {
            'shapeID': nShapeID,
            'direct': dResult.get('direct', 0),
            'vpos': vPos }
        yardothers.ShowEditSuitBeautyTipsIfNeeded(nShapeID, True)
        oDataMgr.AddFurniture(vPos, dAdd)
        dEvent = { }
        if bBrushByBag:
            dUseItem = {
                'shapeID': nShapeID }
            pFurItem = pBagDataMgr.GetFurItem(nShapeID)
            pFurItem.UseItem()
            dEvent['useitem'] = dUseItem
        
        dCopyAdd = dict(dAdd)
        dCopyAdd['vpos'] = vPos
        dEvent['furnitureadd'] = dCopyAdd
        dExtend = dResult.get('dExtend')
        if dExtend:
            vPos = dExtend['vpos']
            dEvent['furnituredel'] = {
                'shapeID': dExtend['shapeID'],
                'direct': dExtend.get('direct', 0),
                'vpos': vPos }
        
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def BrushFarm(self, vPos, bEvent = True):
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        pFarmObj = oDataMgr.GetFarm()
        vOldPos = pFarmObj.GetPos()
        pFarmObj.SetPos(vPos)
        dEvent = { }
        dEvent['oldfarmpos'] = vOldPos
        dEvent['newfarmpos'] = vPos
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def BrushHouse(self, dResult, bEvent = True):
        vPos = dResult['vpos']
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vOldPos = oDataMgr.GetHouseInfoValueByKey('vpos')
        oDataMgr.SetHouseInfoByKey('vpos', vPos)
        dEvent = { }
        dEvent['oldhousepos'] = vOldPos
        dEvent['newhousepos'] = vPos
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def BrushNpc(self, dNpc, bEvent = True):
        vPos = dNpc['vpos']
        npcID = dNpc['npcID']
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vOldPos = oDataMgr.GetStableNpcByNpcID(npcID)['vpos']
        oDataMgr.SetStableNpcPosByNpcID(npcID, vPos)
        dEvent = {
            'oldnpcpos': {
                'npcID': npcID,
                'vpos': vOldPos },
            'newnpcpos': {
                'npcID': npcID,
                'vpos': vPos } }
        if bEvent:
            self.m_oBackPreLogic.AddEvent2Stack(dEvent)
        else:
            return dEvent

    
    def BrushAnimal(self, dAnimal, bEvent = True):
        vPos = dAnimal['vpos']
        iAnimalID = dAnimal['animalID']
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vOldPos = (dAnimal['x'], dAnimal['y'])
        oDataMgr.SetAnimalPos(iAnimalID, vPos)
        dEvent = {
            'oldanimalpos': {
                'animalID': iAnimalID,
                'vpos': vOldPos },
            'newanimalpos': {
                'animalID': iAnimalID,
                'vpos': vPos } }

    
    def BrushResume(self, dChangeData):
        '''"changedLand": "addFur": "delFur", farmpos, housepos, npcpos'''
        lEvent = []
        vFarmPos = dChangeData.get('farmpos')
        if vFarmPos:
            dEvent = self.BrushFarm(vFarmPos, bEvent = False)
            lEvent.append(dEvent)
        
        vHousePos = dChangeData.get('housepos')
        if vHousePos:
            dEvent = self.BrushHouse({
                'vpos': vHousePos }, bEvent = False)
            lEvent.append(dEvent)
        
        dNpcPos = dChangeData.get('npcpos')
        if dNpcPos:
            for nID, vPos in dNpcPos.iteritems():
                dNpc = {
                    'vpos': vPos,
                    'npcID': nID }
                dEvent = self.BrushNpc(dNpc, bEvent = False)
                lEvent.append(dEvent)
            
        
        lDelFur = dChangeData.get('delFur')
        if lDelFur:
            for dFur in lDelFur:
                dEvent = self.DelFurntirue(dFur, bEvent = False)
                lEvent.append(dEvent)
            
        
        lAddFur = dChangeData.get('addFur')
        if lAddFur:
            for dFur in lAddFur:
                dEvent = self.BrushFurniture(dFur, True, bEvent = False)
                lEvent.append(dEvent)
            
        
        changedLand = dChangeData.get('changedLand')
        if changedLand:
            oYardDataMgr = self.GetContext().GetYardDataMgr()
            dOldLand = { }
            for vGrid, lLand in changedLand.iteritems():
                lOldLand = oYardDataMgr.GetLand(vGrid)
                if lOldLand:
                    dOldLand[vGrid] = lOldLand
                    continue
            
            dEvent = self.Brush(changedLand, dOldLand, bEvent = False)
            lEvent.append(dEvent)
