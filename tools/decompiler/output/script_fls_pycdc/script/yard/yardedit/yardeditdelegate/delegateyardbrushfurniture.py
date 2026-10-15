# pycdc 交叉复核产物 · script.fls entry 3351
# co_filename(原始)='script/yard/yardedit/yardeditdelegate/delegateyardbrushfurniture.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3351.pyc (Python 2.5)

'''
import delegateyardbrushfurniture.py
\xd4\xa4\xc0\xc0\xb9\xa6\xc4\xdc\xa3\xba
1. \xb5\xe3\xbb\xf7 \xc6\xcc\xbc\xd2\xbe\xdf \xc8\xe7\xb9\xfb\xb2\xbb\xb4\xe6\xd4\xda\xd4\xf2\xb5\xaf\xb3\xf6 \xb9\xba\xc2\xf2\xb5\xaf\xbf\xf2
\ta.\xc8\xe7\xb9\xfb\xb5\xe3\xbb\xf7\xb9\xba\xc2\xf2\xd4\xf2\xc4\xac\xc8\xcf\xb0\xda\xb7\xc5
\tb.\xb7\xf1\xd4\xf2\xb2\xbb\xb0\xda\xb7\xc5
\t\xbd\xe1\xca\xf8\xba\xf3\xa3\xba
\t\t\xbc\xcc\xd0\xf8\xb0\xda\xb7\xc5


'''
import misc
import yardeditviewbase
import yardeditblockview
import newfurnituredata
import yardblockdata
import timer
import cursor
import yarddefines
import key
import yardothers
import time
import yardfur2cursoffposdata
E_VOFF = (0, 0)
E_ATTACH = (20, 20)

class CDelegateYardBrushFurniture(yardeditviewbase.CEditViewBase):
    
    def __init__(self, oContext, pEditViewMgr, oBrushView):
        yardeditviewbase.CEditViewBase.__init__(self, oContext, pEditViewMgr)
        self.m_wrBrush = misc.WeakRef(oBrushView)
        self.m_oBlockView = None
        self.m_pTimer = None
        self.m_oCheckBuyDeadLineTimer = None
        self.m_vMapCell = None
        self.m_vMapPos = None
        self.m_vOffPos = (0, 0)
        self.m_vBasePos = (0, 0)
        self.m_bNew = False
        self.m_bContinuePlaceFur = False
        self.m_bBuyMode = False
        self.m_lPlaceBlock = None
        self.m_lBlock = None
        self.m_nShapeID = None
        self.m_nDirect = 0
        self.m_nUnitType = yarddefines.E_BLOCK_TYPE_FUR
        self.m_nRotateNum = 1
        self.m_bUseBag = True
        self.m_tWait2BrushData = None
        self.m_oClearWaitEventTimer = None
        self.InitSignal()

    
    def OnSetData(self, nShapeID, dExtend):
        if dExtend:
            vPos = dExtend['vpos']
            nID = dExtend['shapeID']
            direct = dExtend['direct']
            nDirect = direct
            dFurniture = {
                'shapeID': nID,
                'direct': direct }
            oYardDataMgr = self.GetContext().GetYardDataMgr()
            oYardDataMgr.SetAttrByKeyValue_Edit('moveshape', nID)
            oYardDataMgr.DelFurniture(vPos, dFurniture)
            vScreenPos = dExtend.get('screenpos')
            self.m_nDirect = nDirect
            self.m_nShapeID = nShapeID
            self.SetUseBag(False)
            self.RefreshOffPos(vScreenPos)
            self.m_bNew = False
            self.m_bContinuePlaceFur = False
        else:
            oBrush = self.GetBrush()
            oBrush.GetFurNumText().SetShow(True)
            self.m_bNew = True
            self.m_bContinuePlaceFur = newfurnituredata.GetData(nShapeID).get('lianxuplace')
            nDirect = 0
            if dExtend:
                nDirect = dExtend['direct']
            
            self.m_nDirect = nDirect
            self.m_nShapeID = nShapeID
            self.RefreshOffPosByTable()
        self.RefreshBlock(nShapeID, nDirect)
        self.StartMoveWithCurser()
        self.OnRefreshFurNum()

    
    def InitSignal(self):
        import yardsignal
        key.RegisterHotKey((key.VK_SPACE,), misc.Functor(self.Rotate))
        yardsignal.Connect(yardsignal.SS_YARD_BAG_ITEMATTR_CHANGED, self.OnYardBagItemAttrChanged_Signal)
        yardsignal.Connect(yardsignal.SS_YARD_BAG_FURITEMS_REFRESH, self.OnYardBagRefresh_Signal)

    
    def OnYardBagItemAttrChanged_Signal(self, pItem, sKey, oldData, curData):
        if sKey not in ('useNum', 'num'):
            return None
        
        if pItem.GetShapeID() != self.m_nShapeID:
            return None
        
        self.OnRefreshFurNum()

    
    def OnYardBagRefresh_Signal(self, pBag, lKey, iReason):
        if self.GetContext().GetYardBagDataMgr() != pBag:
            return None
        
        if self.m_nShapeID not in lKey:
            return None
        
        if self.m_tWait2BrushData:
            dFurInfo = self.m_tWait2BrushData[0]
            bUseBag = self.m_tWait2BrushData[1]
            self.Wait2BrushFurniture(dFurInfo, bUseBag)
        
        self.OnRefreshFurNum()

    
    def OnRefreshFurNum(self):
        oBagDataMgr = self.GetContext().GetYardBagDataMgr()
        nLeftNum = oBagDataMgr.CalNumByShapeID(self.m_nShapeID)
        oBrush = self.GetBrush()
        oBrush.SetFurLeftNum('#c000000%s' % nLeftNum)

    
    def Rotate(self):
        import usermacro
        if self.m_bBuyMode:
            return None
        
        import interface
        if not self.m_nRotateNum > 1:
            usermacro.PROMPT_MSG('\xb8\xd3\xb3\xc3\xa8\xe3\xa5u\xa6\xb3\xa4@\xad\xd3\xa4\xe8\xa6V')
            return None
        
        nCurDirect = (self.m_nDirect + 1) % self.m_nRotateNum
        if not yardothers.CheckEditFurnitureHasDirect(self.m_nShapeID, nCurDirect):
            usermacro.PROMPT_MSG('\xa4\xa3\xa6s\xa6b\xa4\xe8\xa6V\xb8\xea\xb7\xbd\xb5L\xaak\xb1\xdb\xc2\xe0:%s : %s' % (self.m_nShapeID, nCurDirect))
            return None
        
        self.m_nDirect = (self.m_nDirect + 1) % self.m_nRotateNum
        self.RefreshOffPosByTable()
        import yardbrushshape_funiture
        oShapeView = yardbrushshape_funiture.CreateFurniture(self.GetBrush(), self.m_nShapeID, self.m_nDirect)
        self.GetBrush().SetShape(oShapeView)
        self.RefreshBlock(self.m_nShapeID, self.m_nDirect)
        self._MoveWithCurser()

    
    def CloseBrush(self):
        pView = self.GetBrush()
        pView.CloseBrush()

    
    def OnYardBgMoved_Signal(self, pMgr, sKey, pValue, pOldValue):
        if sKey != 'vPos' or pValue == pOldValue:
            return None
        
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        if oDataMgr != pMgr:
            return None
        
        if not self.m_vMapPos:
            return None
        
        self.RefreshPos(self.m_vMapPos)

    
    def SetUseBag(self, bUseBag):
        self.m_bUseBag = bUseBag

    
    def RefreshOffPos(self, vScreenPos):
        vCursorPos = cursor.GetCursorPos()
        self.RefreshBasePos()
        self.m_vOffPos = ((vScreenPos[0] - vCursorPos[0]) + E_VOFF[0], (vScreenPos[1] - vCursorPos[1]) + E_VOFF[1])

    
    def RefreshOffPosByTable(self):
        self.RefreshBasePos()
        if not self.m_bNew:
            return None
        
        self.m_vOffPos = (0, 0)

    
    def RefreshBasePos(self):
        if not self.m_nShapeID:
            return None
        
        sPath = yardblockdata.GetFurnitureBlockKeyByID(self.m_nShapeID, self.m_nDirect)
        (x, y) = yardfur2cursoffposdata.GetFur2CursorOffPos(sPath)
        self.m_vBasePos = (x, y)
        if self.m_oBlockView:
            self.m_oBlockView.SetPos(*self.m_vBasePos)
        

    
    def GetBrush(self):
        return self.m_wrBrush()

    
    def IsInZoom(self, x, y):
        import yardgridconvertlogic
        import C_sys
        if not self.m_bNew:
            iRealX = x + self.m_vOffPos[0]
            iRealY = y + self.m_vOffPos[1]
        else:
            iRealX = x + self.m_vOffPos[0] - self.m_vBasePos[0]
            iRealY = y + self.m_vOffPos[1] - self.m_vBasePos[1]
        lObj = C_sys.GetObjects(iRealX, iRealY)
        continue
        lObj1 = None(C_sys.GetObjects, y)
        if self.GetBrush() in lObj or self.GetBrush() in lObj1:
            return True
        
        oBrushView = self.GetBrush()
        vPos = oBrushView.GetPos()
        fDistance = yardgridconvertlogic.Distance((iRealX, iRealY), vPos)
        if fDistance > yarddefines.E_CHECK_BRUSH_DISTANCE:
            return False
        else:
            return True

    
    def RefreshBlock(self, nShapeID, nDirect = 0, bUseBag = True):
        self.m_nShapeID = nShapeID
        if not self.m_oBlockView:
            self.m_oBlockView = yardeditblockview.CYardMapItemBlock(self.GetBrush())
            self.m_oBlockView.SetZ(100)
        
        self.m_oBlockView.SetPos(*self.m_vBasePos)
        dFurData = newfurnituredata.GetData(nShapeID)
        nSubType = dFurData.get('subtype', 0)
        if nSubType in (newfurnituredata.FUR_TYPE_WATER,):
            self.m_nUnitType = yarddefines.E_UNIT_FURNITURE_WATER
        elif nSubType in (newfurnituredata.FUR_TYPE_BRICK,):
            self.m_nUnitType = yarddefines.E_UNIT_FUNITURE_BRICK
        else:
            self.m_nUnitType = yarddefines.E_UNIT_FURNITURE_NORMAL
        if 'direct' in dFurData:
            self.m_nRotateNum = dFurData['direct']
        
        if not self.m_nRotateNum:
            sPath = newfurnituredata.GetFurniturePath(nShapeID, 1)
            self.m_nRotateNum = misc.FileExist(sPath, 'mapobject')
        
        self.m_nDirect = nDirect
        self.RefreshOffPosByTable()
        sPath = yardblockdata.GetFurnitureBlockKeyByID(nShapeID, nDirect)
        lBlock = yardblockdata.GetResBlockData(sPath)
        self.m_lBlock = list(lBlock)
        self.m_oBlockView.SetData(lBlock)

    
    def StartMoveWithCurser(self):
        if not self.m_pTimer:
            self.m_pTimer = timer.Timer(0.03, self._MoveWithCurser, -1, oRelayObj = self)
            self.m_vMapCell = None
            self._MoveWithCurser()
        

    
    def AttachPosNew(self, vWorldPos):
        oGridConvertLogic = self.GetGridConvertLogic()
        vMapCell = oGridConvertLogic.WorldPos2ServerMapPos(vWorldPos)
        vWorldPos = oGridConvertLogic.ServerMapPos2WorldPos(vMapCell)
        x = int(vWorldPos[0])
        y = int(vWorldPos[1])
        (iAttachX, iAttachY) = E_ATTACH
        vRealPos = (((x + iAttachX / 2) / iAttachX) * iAttachX, ((y + iAttachY / 2) / iAttachY) * iAttachY)
        vRealPos = (vRealPos[0] - self.m_vBasePos[0], vRealPos[1] - self.m_vBasePos[1])
        vMapCell = oGridConvertLogic.FurnitureClientPos2ServerPos(vRealPos, self.m_nShapeID, self.m_nDirect)
        vRealPos = oGridConvertLogic.FurnitureServerPos2WorldPos(vMapCell, self.m_nShapeID, self.m_nDirect)
        return (vMapCell, vRealPos)

    
    def AttachNormalPos(self, vWorldPos):
        vWorldPos = (vWorldPos[0] + self.m_vBasePos[0], vWorldPos[1] + self.m_vBasePos[1])
        (vMapCell, vRealPos) = self.AttachPosNew(vWorldPos)
        return (vMapCell, vRealPos)

    
    def _MoveWithCurser(self):
        if self.m_bBuyMode:
            return None
        
        (x, y) = cursor.GetCursorPos()
        oContext = self.GetContext()
        oDataMgr = oContext.GetYardDataMgr()
        vOffGrid = oDataMgr.GetAttrByKey('vPos')
        oGridConvertLogic = self.GetGridConvertLogic()
        x = x + self.m_vOffPos[0]
        y = y + self.m_vOffPos[1]
        vWorldPos = oGridConvertLogic.CalMapPosByWindowPos(vOffGrid, (x, y))
        if self.m_bNew:
            (vMapCell, vRealPos) = self.AttachPosNew(vWorldPos)
        else:
            (vMapCell, vRealPos) = self.AttachNormalPos(vWorldPos)
        if self.m_vMapCell == vMapCell:
            return None
        
        self.m_vMapCell = vMapCell
        self.RefreshPos(vRealPos)

    
    def RefreshPos(self, vRealPos):
        self.m_vMapPos = vRealPos
        oView = self.GetBrush()
        oDataMgr = self.GetContext().GetYardDataMgr()
        oGridConvertLogic = self.GetGridConvertLogic()
        vOffGrid = oDataMgr.GetAttrByKey('vPos')
        vOffPos = oGridConvertLogic.Server2ClientPos(vOffGrid)
        vPos = (int(vRealPos[0] + vOffPos[0]), int(vRealPos[1] + vOffPos[1]))
        oView.SetPos(*vPos)
        if not self.m_lBlock:
            return None
        
        pBlockLogic = self.GetBlockLogic()
        self.m_lPlaceBlock = pBlockLogic.CalBlock(self.m_lBlock, self.m_vMapCell, self.m_nUnitType)
        for vBlock in self.m_lBlock:
            bRed = vBlock in self.m_lPlaceBlock
            self.m_oBlockView.SetBlockRed(vBlock, bRed)
        

    
    def LeftDown(self):
        if self.m_bBuyMode:
            return None
        
        if not self.m_pTimer:
            return None
        else:
            self.Check2Brush()

    
    def LeftUp(self):
        if self.m_bBuyMode:
            return None
        
        if not self.m_pTimer:
            self.StartMoveWithCurser()
        
        self.m_vMapCell = None

    
    def Check2Brush(self, *argv):
        if not self.m_vMapCell:
            LOG('PLACE error pos')
            return None
        
        import usermacro
        if self.m_lPlaceBlock:
            if self.m_nUnitType == yarddefines.E_UNIT_FURNITURE_WATER:
                sMsg = yarddefines.E_TIPS.get('furnwcannotplacetips', '\xa4\xa3\xaf\xe0\xc2\\\xa9\xf1\xb3\xc3\xa8\xe3')
            else:
                sMsg = yarddefines.E_TIPS.get('furncannotplacetips', '\xa4\xa3\xaf\xe0\xc2\\\xa9\xf1\xb3\xc3\xa8\xe3')
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        oYardDataMgr = self.GetContext().GetYardDataMgr()
        oFurTable = newfurnituredata.GetData(self.m_nShapeID)
        nType = oFurTable['pagename']
        if self.m_bUseBag and oYardDataMgr.IsOutMaxFurniture(nType):
            sMsg = yarddefines.E_TIPS['outmaxfurnumtips']
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        oBrushView = self.GetBrush()
        nShapeID = self.m_nShapeID
        oBrushViewLogic = self.GetContext().GetYardBrushLogic()
        dFurInfo = {
            'usebag': self.m_bUseBag,
            'vpos': self.m_vMapCell,
            'direct': self.m_nDirect,
            'shapeID': nShapeID,
            'dExtend': oBrushView.GetExtend() }
        if oBrushViewLogic.IsSameFur(dFurInfo):
            sMsg = yarddefines.E_TIPS['furcannotsameplace']
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        import sound
        sound.PlaySound(sound.SND_BUTTON)
        bEnablePlace = True
        if self.m_bUseBag:
            oBagDataMgr = self.GetContext().GetYardBagDataMgr()
            nLeftNum = oBagDataMgr.CalNumByShapeID(self.m_nShapeID)
            bEnablePlace = nLeftNum > 0
        
        if not bEnablePlace:
            self.GotoBuyFur()
        else:
            oBrushViewLogic.BrushFurniture(dFurInfo, self.m_bUseBag)
            if not (self.m_bUseBag) or not (self.m_bContinuePlaceFur):
                oBrushView.SetExtend(None)
                oBrushView.CloseBrush()
                oYardDataMgr.SetAttrByKeyValue_Edit('moveshape', None)
            

    
    def GotoBuyFur(self):
        pYardDataMgr = self.GetContext().GetYardDataMgr()
        pYardDataMgr.SetAttrByKeyValue_Edit('goldbuy', self.m_nShapeID)
        self.ReleaseByCheckTimer()
        self.m_oCheckBuyDeadLineTimer = timer.Timer(0.1, misc.Functor(self.CheckBuyDeadLineLoop, time.time()), -1, oRelayObj = self)
        timer.Timer(0, self.OpenGetAccessDlg)
        self.SetBuyFurState(True)

    
    def ReleaseByCheckTimer(self):
        if self.m_oCheckBuyDeadLineTimer:
            self.m_oCheckBuyDeadLineTimer.Release()
            self.m_oCheckBuyDeadLineTimer = None
        

    
    def OpenGetAccessDlg(self):
        import netopenui
        import newfurnituredata
        funitureData = newfurnituredata.GetData(self.m_nShapeID)
        (iShape, iLv, iType, sName, iAmount) = (self.m_nShapeID, 0, 0, funitureData['name'], 1)
        netopenui.C2SOpenItemAccessDlg(iShape, iLv, iType, sName, iAmount, 1)

    
    def CheckBuyDeadLineLoop(self, iStartTime):
        import mdconvenientpurchase
        import popupmgr
        import popupdefine
        if not self.m_bBuyMode:
            self.ReleaseByCheckTimer()
            return None
        
        oGetAccessDlg = popupmgr.GetPopupMgr().GetUI(popupdefine.CGetAccessDlg)
        iShapeID = mdconvenientpurchase.GetConvenientPurchaseMgr().GetItemShape()[0]
        iCurTime = time.time()
        if iCurTime - iStartTime > 2:
            if not oGetAccessDlg:
                self.SetBuyFurState(False)
                return None
            
        
        if oGetAccessDlg and not hasattr(oGetAccessDlg, 'm_bLinkYardBrush') and iShapeID == self.m_nShapeID:
            oGetAccessDlg.m_bLinkYardBrush = True
            oGetAccessDlg.ssConnect(oGetAccessDlg.SS_ClickAItem, self.OnClickAItemByAccessDlg)
        

    
    def OnClickAItemByAccessDlg(self, sKey):
        import mdconvenientpurchase
        import builddefine
        import hero
        self.ReleaseByCheckTimer()
        self.ClearWaiteBrushDataEvent()
        if sKey in ('SG',):
            iHeroGold = hero.GetProp('m_Gold')
            dData = mdconvenientpurchase.GetConvenientPurchaseMgr().GetNowNeedItem()
            iGold = dData.get(builddefine.KEY_NEED_GOLD)
            if iHeroGold >= iGold:
                oBrushView = self.GetBrush()
                nShapeID = self.m_nShapeID
                dExtend = oBrushView.GetExtend()
                if dExtend:
                    dExtend = misc.DeepCopy(oBrushView.GetExtend())
                
                dFurInfo = {
                    'usebag': self.m_bUseBag,
                    'vpos': self.m_vMapCell,
                    'direct': self.m_nDirect,
                    'shapeID': nShapeID,
                    'dExtend': dExtend }
                self.m_tWait2BrushData = (dFurInfo, self.m_bUseBag)
                self.m_oClearWaitEventTimer = timer.Timer(1, self.ClearWaiteBrushDataEvent, oRelayObj = self)
                self.SetBuyFurState(False)
            else:
                self.SetBuyFurState(False)
                self._MoveWithCurser()
        else:
            self.SetBuyFurState(False)
            self._MoveWithCurser()

    
    def ReleaseClearWaiteTimer(self):
        if self.m_oClearWaitEventTimer:
            self.m_oClearWaitEventTimer.Release()
            self.m_oClearWaitEventTimer = None
        

    
    def ClearWaiteBrushDataEvent(self):
        self.ReleaseClearWaiteTimer()
        self.m_tWait2BrushData = None

    
    def Wait2BrushFurniture(self, dFurInfo, bUseBag):
        oBrushViewLogic = self.GetContext().GetYardBrushLogic()
        oBrushViewLogic.BrushFurniture(dFurInfo, bUseBag)

    
    def SetBuyFurState(self, bBuy):
        if not bBuy:
            self.ReleaseByCheckTimer()
        
        self.m_bBuyMode = bBuy

    
    def Clear(self):
        key.RegisterHotKey((key.VK_SPACE,))
