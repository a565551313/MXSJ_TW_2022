# pycdc 交叉复核产物 · script.fls entry 1841
# co_filename(原始)='script/mxgame/makeequip/view/viewbuild/buildequipmentlist.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1841.pyc (Python 2.5)

import combdialog
import interface
import item
import itemdata
import itemdefine
import makeequipitemface
import mdmakegem_new
import misc
import tableview

class CItemBgBox(interface.CImageCheckBox):
    CLASS2TIPS = {
        0: ('\xbe\xd4\xa4h', '\xa7\xf0\xc0\xbb', '\xaaZ\xbe\xb9', '\xc5@\xb5\xc3', '\xf1Z\xa5\xd2', '\xa7\xd9\xab\xfc'),
        1: ('\xaak\xaev', '\xc6F\xa4O', '\xb6\xb5\xc3\xec', '\xa7\xd9\xab\xfc', '\xf1Z\xa5\xd2', '\xc5@\xb5\xc3'),
        2: ('\xb3N\xa4h', '\xa8\xbe\xbfm', '\xc5@\xb5\xc3', '\xf1Z\xa5\xd2', '\xa7\xd9\xab\xfc', '\xbec\xa4l') }
    
    def __init__(self, parent, filename, x, y, msgid = 0, width = 0, height = 0):
        interface.CImageCheckBox.__init__(self, parent, filename, x, y, msgid = msgid, width = width, height = height)
        self.tmpEnable = True
        self.m_oTuijianTips = None

    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if getattr(par, 'MouseWheelDown', None):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if getattr(self, 'MouseWheelUp', None):
            par.MouseWheelUp(p)
        

    
    def FakeEnable(self, enable, disable_tips = None):
        self.Enable(enable)
        if enable:
            self.m_oFakeBox = None
            self.m_sDisableTips = None
        else:
            self.m_oFakeBox = CFakeClickBox(self, self.m_Width, self.m_Height, 0, 32, 1)
            self.m_sDisableTips = disable_tips

    
    def Enter(self):
        import hero
        import wrapinterface
        interface.CImageCheckBox.Enter(self)
        oParent = self.GetParent()
        if getattr(oParent, 'm_bTuijian', None):
            sTips = '%s\xa5H#Y%s#n\xc4\xdd\xa9\xca\xac\xb0\xa5D#r\xb1\xc0\xaf\xf2\xc0u\xa5\xfd\xa5\xb4\xb3y#Y%s\xa1B%s\xa1B%s\xa1B%s#n' % self.CLASS2TIPS[hero.GetProp('m_Class', 0)]
            self.m_oTuijianTips = wrapinterface.CTextTips(None, 240, sTips, interface.FontLT14_3, direct = 2)
            self.m_oTuijianTips.SetOwner(self)
        

    
    def Leave(self):
        interface.CImageCheckBox.Leave(self)
        self.m_oTuijianTips = None

    
    def OnMessage(self, msgid):
        import usermacro
        if msgid == 1 and self.m_sDisableTips:
            usermacro.PROMPT_MSG(self.m_sDisableTips)
        



class CFakeClickBox(interface.CClickBox):
    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if getattr(par, 'MouseWheelDown', None):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if getattr(self, 'MouseWheelUp', None):
            par.MouseWheelUp(p)
        



class CEquipmentCellItem(combdialog.CCombSubWnd):
    
    def __init__(self, parent, dEquipmenData, oClickFunc, iIdx):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog/equip/equipmentItem.dlg')
        self.m_oClickFunc = oClickFunc
        self.m_oIdx = iIdx
        self.m_selected = False
        self.m_IsIgnoreEsc = True
        self.m_bAble = True
        self.m_sUnableTips = ''
        self.m_bTuijian = False
        self.SetData(dEquipmenData)
        self.InitView()

    
    def SetData(self, dEquipmenData):
        self.m_dData = dEquipmenData

    
    def SetIdx(self, iIdx):
        self.m_oIdx = iIdx

    
    def ResetView(self, dEquipmenData, bSelected):
        self.SetData(dEquipmenData)
        self.InitView()
        self.SetSelect(bSelected)

    
    def InitView(self):
        import mdmakeequip
        if self.m_dData:
            iShapeId = self.m_dData.get('iShapeId', 0)
            (sItemName, _) = itemdata.GetData(iShapeId)
            iLv = self.m_dData.get('iLv', 0)
            bAble = self.m_dData.get('bAble', True)
            sUnableTips = self.m_dData.get('sEnableTips', '')
        else:
            iShapeId = 0
            iLv = 0
            sItemName = ''
            bAble = True
            sUnableTips = ''
        self.m_bAble = bAble
        self.m_sUnableTips = sUnableTips
        self.m_oImg = item.CreateItem44Image(self, iShapeId)
        interface.AlignObjects(self.m_oImg, self.GetObject('loc_item'), interface.ALIGN_LEFT_TOP)
        self.m_oImg.SetZ(-1)
        self.m_oTextName = self.GetObject('text_itemName')
        self.m_oTextName.SetText(sItemName)
        self.m_oTextName.SetZ(1)
        self.m_oTextLv = self.GetObject('text_ItemLv')
        sType = itemdata.GetType(iShapeId)
        sEquipName = itemdata.GetTypeName(sType)
        self.m_oTextLv.SetText('%d\xaf\xc5%s' % (iLv, sEquipName))
        self.m_oBg = self.GetObject('img_bg')
        (iX, iY, iW, iH) = self.GetLocData('img_bg')
        self.GetObject('img_bg').SetShow(False)
        sFileName = self.GetObject('img_bg').m_FileName
        self.m_oImgBg = CItemBgBox(self, sFileName, iX, iY, 0, iW, iH)
        self.m_oImgBg.FakeEnable(self.m_bAble, self.m_sUnableTips)
        self.m_oImgBg.SetZ(-2)
        oMgr = mdmakeequip.GetMakeEquipMgr()
        if oMgr.IsTuijianEquip(self.m_dData):
            bShow = True
        else:
            bShow = False
        self.m_bTuijian = bShow
        self.SetShowObject('img_tuijian', bShow)

    
    def SetSelect(self, bSelect):
        self.m_selected = bSelect
        self.m_oImgBg.SetCheck(bSelect)

    
    def GetSelect(self):
        return self.m_selected

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        self.m_selected = not iShapeId()
        if callable(self.m_oClickFunc):
            iShapeId = self.m_dData.get('iShapeId', 0)
            iLv = self.m_dData.get('iLv', 0)
            self.m_oClickFunc(self.m_oIdx, iShapeId, iLv)
        

    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if getattr(par, 'MouseWheelDown', None):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if getattr(self, 'MouseWheelUp', None):
            par.MouseWheelUp(p)
        



class CEquipmentList(object):
    SS_TurnPage = 'SS_TurnPage(iAdd)'
    SS_EquipListBoxChg = 'SS_EquipListBoxChg'
    
    def __init__(self):
        self.m_iListWidth = 0
        self.m_iListHight = 0
        self.m_iListStartX = 0
        self.m_iListStartY = 0
        self.m_iListSelectIdx = -1
        self.m_oEquipmentList = None
        self.m_oEquipListBox = None
        self.m_lstEquipmentDatas = []

    
    def CreateEquipList(self, iEquipListX, iEquipListY, iEquipListW, iEquipListH, iListBoxX, iListBoxY, iListBoxW, iListBoxH):
        self.m_iListWidth = iEquipListW
        self.m_iListHight = iEquipListH
        self.m_iListStartX = iEquipListX
        self.m_iListStartY = iEquipListY
        self.m_iListSelectIdx = -1
        self.m_oEquipmentList = tableview.CTableView(self, self.m_iListWidth, self.m_iListHight)
        self.m_oEquipmentList.SetDelegateNumberOfCells(self.DelegateNumberOfCells)
        self.m_oEquipmentList.SetDelegateSizeOfIndex(self.DelegateSizeOfIndex)
        self.m_oEquipmentList.SetDelegateNewCellOfIndex(self.DelegateNewCellOfIndex)
        self.m_oEquipmentList.SetDelegateUpdateCellOfIndex(self.DelegateUpdateCellOfIndex)
        self.m_oEquipmentList.SetDefaultCellAlign(interface.ALIGN_LEFT)
        self.m_oEquipmentList.SetPos(self.m_iListStartX, self.m_iListStartY)
        self.m_oEquipmentList.SetShowBgLine(False)
        self.m_oEquipmentList.SetZ(1)
        self.m_oEquipListBox = interface.CListBox(self, interface.COLOR_5, interface.FontLT14_3, iListBoxX, iListBoxY, iListBoxW, iListBoxH)
        self.m_oEquipListBox.SetTextAlign(interface.ALIGN_CENTER_MIDDLE)
        self.m_oEquipListBox.SetDownButtonPosWithAlign(interface.ALIGN_RIGHT_MIDDLE)
        self.m_oEquipListBox.SetItemProp(4, 16, 160)
        self.m_oEquipListBox.SetListBoxChangeCB(misc.Functor(self.OnEquipListBoxChg))
        self.m_oEquipListBox.SetReadOnly(True)
        self.m_oEquipListBox.SetZ(2)

    
    def OnEquipListBoxChg(self):
        self.ssEmit(self.SS_EquipListBoxChg)

    
    def TurnPage(self, iAdd):
        self.ssEmit(self.SS_TurnPage, iAdd)

    
    def GetEquipmentList(self):
        return self.m_oEquipmentList

    
    def GetEquipListBox(self):
        '''
\t\t:rtype interface.CListBox
\t\t'''
        return self.m_oEquipListBox

    
    def SetClickEquipmentListCB(self, oClickFunc):
        self.m_oClickEquipmentListFunc = oClickFunc

    
    def OnClickItem(self, iIdx, iShape, iLv):
        tUpdateIdxs = (self.m_iListSelectIdx, iIdx)
        self.m_iListSelectIdx = iIdx
        self.m_oEquipmentList.Reload(-1, tUpdateIdxs)
        if callable(self.m_oClickEquipmentListFunc):
            self.m_oClickEquipmentListFunc(iShape, iLv)
        

    
    def OnClickItemNoDoCB(self, iIdx, iShap, iLv):
        tUpdateIdxs = (self.m_iListSelectIdx, iIdx)
        self.m_iListSelectIdx = iIdx
        self.m_oEquipmentList.Reload(-1, tUpdateIdxs)

    
    def GetCellWidget(self):
        return CEquipmentCellItem

    
    def DelegateNumberOfCells(self):
        return len(self.m_lstEquipmentDatas)

    
    def DelegateSizeOfIndex(self, iIdx):
        return CEquipmentCellItem(None, { }, None, 0).GetSize()[1]

    
    def DelegateNewCellOfIndex(self, oContainer, iIdx):
        if iIdx > len(self.m_lstEquipmentDatas):
            return None
        
        oCellWidgetCls = self.GetCellWidget()
        if oCellWidgetCls == interface.CTextObject:
            oCellWidget = interface.CTextObject(oContainer, self.m_lstEquipmentDatas[iIdx], interface.FontST20, interface.COLOR_29)
        else:
            oCellWidget = oCellWidgetCls(oContainer, self.m_lstEquipmentDatas[iIdx], misc.Functor(self.OnClickItem), iIdx)
        return oCellWidget

    
    def DelegateUpdateCellOfIndex(self, oCell, iIdx, bReused):
        if hasattr(oCell, 'ResetView'):
            oCell.SetIdx(iIdx)
            oCell.ResetView(self.m_lstEquipmentDatas[iIdx], self.m_iListSelectIdx == iIdx)
        elif isinstance(oCell, interface.CTextObject):
            oCell.SetText(self.m_lstEquipmentDatas[iIdx])
        

    
    def UpdateEquipmentListDatas(self, lstDatas, bClearSelect = True):
        if bClearSelect:
            self.m_iListSelectIdx = -1
        
        if len(lstDatas) != len(self.m_lstEquipmentDatas):
            self.m_oEquipmentList.Clear()
        
        self.m_lstEquipmentDatas = lstDatas
        self.m_oEquipmentList.Reload()

    
    def SetSelectItemByType(self, iType, bDoCB):
        if not iType:
            self.m_iListSelectIdx = -1
            self.m_oEquipmentList.Reload()
            return None
        
        import iteminterface
        for idx, oEquipmentData in enumerate(self.m_lstEquipmentDatas):
            iShapeId = oEquipmentData.get('iShapeId')
            iTempType = iteminterface.GetEquipTypeByShape(iShapeId)
            iLv = oEquipmentData.get('iLv')
            if iType == iTempType:
                bAble = oEquipmentData.get('bAble', True)
                if not bAble:
                    pass
                elif bDoCB:
                    self.OnClickItem(idx, iShapeId, iLv)
                else:
                    self.OnClickItemNoDoCB(idx, iShapeId, iLv)
                break
                continue
        

    
    def SetSelectItemByIdx(self, iIdx, bDoCB):
        if not (self.m_lstEquipmentDatas) or len(self.m_lstEquipmentDatas) <= iIdx:
            return None
        
        oEquipmentData = self.m_lstEquipmentDatas[iIdx]
        iShapeId = oEquipmentData.get('iShapeId')
        iLv = oEquipmentData.get('iLv')
        if bDoCB:
            self.OnClickItem(iIdx, iShapeId, iLv)
        else:
            self.OnClickItemNoDoCB(iIdx, iShapeId, iLv)



class CEquipItem(makeequipitemface.CInterfaceItemWithLevel):
    
    def LeftUp(self):
        makeequipitemface.CInterfaceItemWithLevel.LeftUp(self)
        self.GetParent().LeftUp()



class CEquipForGemCellItem(combdialog.CCombSubWnd):
    CLASS2TIPS = {
        0: ('\xbe\xd4\xa4h', '\xa7\xf0\xc0\xbb', '\xf1Z\xa5\xd2', '\xc5@\xb5\xc3', '\xa7\xd9\xab\xfc'),
        1: ('\xaak\xaev', '\xc6F\xa4O', '\xf1Z\xa5\xd2', '\xc5@\xb5\xc3', '\xb6\xb5\xc3\xec'),
        2: ('\xb3N\xa4h', '\xa8\xbe\xbfm/\xb3t\xab\xd7', '\xf1Z\xa5\xd2', '\xc5@\xb5\xc3', '\xa7\xd9\xab\xfc') }
    
    def __init__(self, parent, dEquipData, oClickFunc, idx):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog/equip/baoshiequipmentItem.dlg')
        self.m_oClickFunc = oClickFunc
        self.m_iIdx = idx
        self.m_bSelected = False
        self.m_dData = None
        self.m_oEquip = None
        self.m_oGemLst = []
        self.m_bEnabled = True
        self.m_bGrey = False
        self.m_oEquipName = None
        self.m_oImgBg = None
        self.m_oTuijianTips = None
        self.GetObject('text_itemName_grey').SetShow(False)
        self.SetData(dEquipData)
        self.InitView()
        self.UpdataMosaicInEquipGem()

    
    def SetData(self, dEquipData):
        self.m_dData = dEquipData

    
    def GetData(self):
        return self.m_dData

    
    def GetIdx(self):
        return self.m_iIdx

    
    def SetIdx(self, idx):
        self.m_iIdx = idx

    
    def ResetView(self, dEquipmenData, bSelected, bEnabled):
        self.m_dData = None
        self.SetData(dEquipmenData)
        self.InitView()
        self.UpdataMosaicInEquipGem()
        self.SetSelect(bSelected)
        self.SetEnabled(bEnabled)

    
    def SetSelect(self, bSelect):
        if self.m_oImgBg and self.m_dData:
            self.m_oImgBg.SetCheck(bSelect)
            self.m_selected = bSelect
        

    
    def GetSelect(self):
        return self.m_selected

    
    def SetEnabled(self, bEnable):
        if self.m_dData is None:
            return None
        
        self.m_oImgBg.Enable(bEnable)
        if hasattr(self.m_oEquip, 'Enable'):
            pass
        self.m_oEquip.Enable(bEnable)
        self.m_bEnabled = bEnable
        oImgBg = self.m_oImgBg.m_BGImg
        if hasattr(oImgBg, 'Enable'):
            oImgBg.Enable(bEnable)
        
        if bEnable:
            self.m_bGrey = False
            for oGem in self.m_oGemLst:
                if hasattr(oGem, 'SetLight'):
                    pass
                oGem.SetLight(8)
            
            if hasattr(oImgBg, 'SetLight'):
                pass
            oImgBg.SetLight(8)
            if hasattr(self.m_oEquip, 'ShowShadow'):
                pass
            self.m_oEquip.ShowShadow(False)
            self.m_oEquipName.SetShow(True)
            if self.GetObject('text_itemName_grey'):
                pass
            self.GetObject('text_itemName_grey').SetShow(False)
            if self.GetSelect():
                oImgBg.SetFrame(1)
            else:
                oImgBg.SetFrame(0)
        else:
            for oGem in self.m_oGemLst:
                if hasattr(oGem, 'SetGrey'):
                    pass
                oGem.SetGrey()
            
            self.m_bGrey = True
            oImgBg.SetFrame(0)
            if hasattr(oImgBg, 'SetGrey'):
                pass
            oImgBg.SetGrey()
            if hasattr(self.m_oEquipName, 'SetGrey'):
                pass
            self.m_oEquipName.SetGrey()
            if hasattr(self.m_oEquip, 'ShowShadow'):
                pass
            self.m_oEquip.ShowShadow(True)
            self.m_oEquipName.SetShow(False)
            if self.GetObject('text_itemName_grey'):
                pass
            self.GetObject('text_itemName_grey').SetShow(True)

    
    def InitView(self):
        self.InitTuijian()
        if self.m_dData is None:
            self.GetObject('text_itemName').SetShow(False)
            self.GetObject('text_itemName_grey').SetShow(False)
            self.GetObject('img_bg').SetShow(True)
            self.m_oEquip = None
            return None
        
        sItemName = ''
        if self.m_dData:
            iShapeId = self.m_dData.m_Shape
            (sItemName, _) = itemdata.GetData(iShapeId)
        
        (iX, iY, iW, iH) = self.GetLocData('loc_item')
        item = CEquipItem(self, iX, iY, self.m_iIdx)
        item.SetItem(self.m_dData)
        self.m_oEquip = item
        (iX, iY, iW, iH) = self.GetLocData('img_bg')
        self.GetObject('img_bg').SetShow(False)
        sFileName = self.GetObject('img_bg').m_FileName
        self.m_oImgBg = CItemBgBox(self, sFileName, iX, iY, 0, iW, iH)
        self.m_oImgBg.SetZ(-10)
        self.m_oEquipName = self.GetObject('text_itemName')
        self.m_oEquipName.SetText(sItemName)
        if self.GetObject('text_itemName_grey'):
            pass
        self.GetObject('text_itemName_grey').SetText(sItemName)
        self.InitGuide()

    
    def InitGuide(self):
        import guidectrl
        import guidedefine
        import mdguide
        if 'iGemEquipID' in mdguide.g_dGuideCacheData and self.m_dData:
            if self.m_dData.GetID() == mdguide.g_dGuideCacheData['iGemEquipID']:
                guidectrl.GetGuideCtrl().AddWefOrdObj(self.GetParent().GetParent().GetParent(), guidedefine.GUIDE_MAKE_GEM_MOSAIC_EQUIPITEM, 'm_oEquip', self.m_oEquip)
            
        

    
    def InitTuijian(self):
        if self.IsTuijianEquip():
            bShow = True
        else:
            bShow = False
        self.SetShowObject('img_tuijian', bShow)
        self.SetShowObject('hbox_tuijian', bShow)
        oHotBox = self.GetObject('hbox_tuijian')
        if oHotBox:
            oHotBox.SetEnterCB(misc.Functor(self.OnEnterHotBox))
            oHotBox.SetLeaveCB(misc.Functor(self.OnLeaveHotBox))
        

    
    def IsTuijianEquip(self):
        import hero
        import iteminterface
        if not self.m_dData:
            return False
        
        if hero.GetProp('m_Grade', 0) <= hero.GetProp('m_Grade', 0):
            pass
        elif hero.GetProp('m_Grade', 0) < 45:
            iShape = self.m_dData.GetShape()
            if itemdata.IsType(iShape, 'equip'):
                iType = iteminterface.GetEquipTypeByShape(iShape)
            else:
                iType = 0
            iClass = hero.GetProp('m_Class', 0)
            if iClass == 0:
                return iType in (6, 11, 12)
            elif iClass == 1:
                return iType in (6, 11, 8)
            elif iClass == 2:
                return iType in (6, 11, 12)
            
        
        return False

    
    def OnEnterHotBox(self):
        import wrapinterface
        import hero
        sTips = '%s\xa5H#Y%s#n\xac\xb0\xa5D\xa1A\xb1\xc0\xaf\xf2\xc0u\xa5\xfd\xc6^\xb4O#Y%s\xa1B%s\xa1B%s#n' % self.CLASS2TIPS[hero.GetProp('m_Class', 0)]
        self.m_oTuijianTips = wrapinterface.CTextTips(None, 220, sTips, interface.FontLT14_3, direct = 2)
        self.m_oTuijianTips.SetOwner(self.GetObject('hbox_tuijian'))

    
    def OnLeaveHotBox(self):
        self.m_oTuijianTips = None

    
    def UpdataMosaicInEquipGem(self):
        
        def Sort(t1, t2):
            (_, iLv1) = t1
            (_, iLv2) = t2
            return iLv2 - iLv1

        import ui
        self.m_oGemLst = []
        self.m_oLvlLst = []
        if self.m_dData is None:
            for idx in xrange(1, 4):
                sLocName = 'loc_gem_%d' % idx
                self.GetObject(sLocName).SetShow(False)
            
            return None
        
        dGemLst = self.m_dData.GetGemList()
        dGemLst = list(dGemLst)
        dGemLst.sort(Sort)
        for idx in xrange(1, 4):
            sLocName = 'loc_gem_%d' % idx
            if len(dGemLst) < idx:
                self.GetObject(sLocName).SetShow(False)
                continue
            self.GetObject(sLocName).SetShow(True)
            (iGemId, iLv) = dGemLst[idx - 1]
            oGem = ui.CImage(self.GetObject(sLocName), 'item20/%d.igs' % iGemId, 'item')
            sLv = None if iLv != 0 else ''
            oLvl = interface.CTextObject(self.GetObject(sLocName), sLv, interface.FontLT12E_1, 16777215)
            oLvl.SetZ(1)
            interface.Center(oGem)
            interface.TopRight(oLvl)
            self.m_oGemLst.append(oGem)
            self.m_oLvlLst.append(oLvl)
        

    
    def LeftUp(self):
        if not (self.m_bEnabled) or self.m_dData is None:
            return None
        
        combdialog.CCombSubWnd.LeftUp(self)
        self.m_selected = not self.m_oImgBg.GetSelect()
        if callable(self.m_oClickFunc):
            if self.m_dData:
                iItemID = self.m_dData.GetID()
                self.m_oClickFunc(self.m_iIdx, iItemID)
            
        

    
    def LeftDown(self):
        pass

    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if getattr(par, 'MouseWheelDown', None):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if getattr(self, 'MouseWheelUp', None):
            par.MouseWheelUp(p)
        



class CEquipForGemList(object):
    
    def __init__(self):
        self.m_iListWidth = 0
        self.m_iListHight = 0
        self.m_iListStartX = 0
        self.m_iListStartY = 0
        self.m_iListSelectIdx = -1
        self.m_oEquipmentList = None
        self.m_oEquipListBox = None
        self.m_iSelectID = 0
        self.m_lstEquipmentDatas = []
        self.m_bCellEnabled = True
        self.m_iSelShape = 0
        self.m_iSelLevel = 0
        self.m_iListType = 1

    
    def CreateEquipList(self, oParent, ilocWidgetList):
        self.m_iListSelectIdx = -1
        (self.m_iListStartX, self.m_iListStartY, self.m_iListWidth, self.m_iListHight) = ilocWidgetList
        self.m_oEquipmentList = tableview.CTableView(oParent, self.m_iListWidth, self.m_iListHight)
        self.m_oEquipmentList.SetDelegateNumberOfCells(self.TbDelegateNumberOfCells)
        self.m_oEquipmentList.SetDelegateSizeOfIndex(self.TbDelegateSizeOfIndex)
        self.m_oEquipmentList.SetDelegateNewCellOfIndex(self.TbDelegateNewCellOfIndex)
        self.m_oEquipmentList.SetDelegateUpdateCellOfIndex(self.TbDelegateUpdateCellOfIndex)
        self.m_oEquipmentList.SetDefaultCellAlign(interface.ALIGN_LEFT)
        self.m_oEquipmentList.SetPos(self.m_iListStartX, self.m_iListStartY)
        self.m_oEquipmentList.SetShowBgLine(False)
        self.m_oEquipmentList.SetZ(1)

    
    def SetListType(self, iType):
        self.m_iListType = iType

    
    def SetSelectIdx(self, idx):
        self.m_iSelectID = idx

    
    def SetSelLevel(self, iLevel):
        self.m_iSelLevel = iLevel

    
    def SetSelShape(self, iShape):
        self.m_iSelShape = iShape
        self.m_oEquipmentList.Reload(-1)

    
    def GetCellWidget(self):
        return CEquipForGemCellItem

    
    def GetAllCell(self):
        return self.m_oEquipmentList.GetAllCell()

    
    def GetCellDataList(self):
        return self.m_lstEquipmentDatas

    
    def TbDelegateNumberOfCells(self):
        return len(self.m_lstEquipmentDatas)

    
    def TbDelegateSizeOfIndex(self, iIdx):
        return 55

    
    def TbDelegateNewCellOfIndex(self, oContainer, iIdx):
        if iIdx > len(self.m_lstEquipmentDatas):
            return None
        
        oCellWidgetType = self.GetCellWidget()
        oCellWidget = oCellWidgetType(oContainer, self.m_lstEquipmentDatas[iIdx], misc.Functor(self.OnClickItem), iIdx)
        return oCellWidget

    
    def TbDelegateUpdateCellOfIndex(self, oCell, iIdx, bReused):
        import itemdefine
        import mdmakeequip
        import dlgmakenew
        if hasattr(oCell, 'ResetView'):
            oCell.SetIdx(iIdx)
            oItem = self.m_lstEquipmentDatas[iIdx]
            bEnable = True
            if oItem is None:
                oCell.ResetView(oItem, False, True)
                return None
            
            if self.m_iListType == 1:
                oCell.ResetView(oItem, self.m_iSelectID == getattr(oItem, 'm_ID', 0), bEnable)
            elif self.m_iListType == 2:
                oLeftEquip = mdmakegem_new.GetTransformMgr().GetLeftEquip()
                oRightEquip = mdmakegem_new.GetTransformMgr().GetRightEquip()
                iLeftID = getattr(oLeftEquip, 'm_ID', 0)
                iRightID = getattr(oRightEquip, 'm_ID', 0)
                if self.m_iSelShape and getattr(oItem, 'm_Shape', 0):
                    (lv, sType) = mdmakeequip.GetItemLvAndType(oItem)
                    iPos = itemdefine.EQUIP_TYPE_DATA[itemdefine.WEAPON_CLIENT_TO_SERVER[sType]][itemdefine.KEY_EQUIP_POS]
                    sSeltype = itemdata.GetType(self.m_iSelShape)
                    if sSeltype == 'all':
                        bEnable = True
                    else:
                        iSelPos = itemdefine.EQUIP_TYPE_DATA[itemdefine.WEAPON_CLIENT_TO_SERVER[sSeltype]][itemdefine.KEY_EQUIP_POS]
                        if iSelPos == iPos:
                            bEnable = True
                        else:
                            bEnable = False
                else:
                    bEnable = True
                if not (self.m_bCellEnabled) and self.m_iSelectID != getattr(oItem, 'm_ID', 0):
                    bEnable = False
                
                if iLeftID == getattr(oItem, 'm_ID', 0) or iRightID == getattr(oItem, 'm_ID', 0):
                    bSelect = True
                    bEnable = True
                else:
                    bSelect = False
                oCell.ResetView(oItem, bSelect, bEnable)
            elif self.m_iListType == 3:
                oLeftGem = mdmakegem_new.GetComposeMgr().GetLeftItem()
                oRightGem = mdmakegem_new.GetComposeMgr().GetRightItem()
                iLeftID = getattr(oLeftGem, 'm_ID', 0)
                iRightID = getattr(oRightGem, 'm_ID', 0)
                if not (self.m_iSelShape) or self.m_iSelShape == getattr(oItem, 'm_Shape', 0):
                    iLevel = oItem.GetExtInfo('MKBookLv', 0)
                    if not (self.m_iSelLevel) or iLevel == self.m_iSelLevel:
                        bEnable = True
                    else:
                        bEnable = False
                else:
                    bEnable = False
                if self.m_iSelShape and dlgmakenew.GetType(self.m_iSelShape) == 14:
                    iLv1 = mdmakegem_new.GetGemLvByShape(self.m_iSelShape)
                    iLv2 = mdmakegem_new.GetGemLvByShape(getattr(oItem, 'm_Shape', 0))
                    if iLv2 == iLv1:
                        bEnable = True
                    else:
                        bEnable = False
                
                if not (self.m_bCellEnabled) and self.m_iSelectID != getattr(oItem, 'm_ID', 0):
                    bEnable = False
                
                if iLeftID == getattr(oItem, 'm_ID', 0) or iRightID == getattr(oItem, 'm_ID', 0):
                    bSelect = True
                    bEnable = True
                else:
                    bSelect = False
                oCell.ResetView(oItem, bSelect, bEnable)
            
        elif isinstance(oCell, interface.CTextObject):
            oCell.SetText(self.m_lstEquipmentDatas[iIdx])
        

    
    def SetClickEquipmentItemCB(self, oClickFunc):
        self.m_oClickEquipmentItemFunc = oClickFunc

    
    def UpdateEquipmentListDatas(self, lstDatas, bClearSelect = True, bIsInit = False):
        if bClearSelect:
            self.m_iListSelectIdx = -1
        
        if len(lstDatas) != len(self.m_lstEquipmentDatas):
            self.m_oEquipmentList.Clear()
        
        self.m_lstEquipmentDatas = lstDatas
        if len(self.m_lstEquipmentDatas) < 7:
            for idx in xrange(len(self.m_lstEquipmentDatas), 7):
                self.m_lstEquipmentDatas.append(None)
            
            self.m_oEquipmentList.SetScorllBarShow(False)
        else:
            self.m_oEquipmentList.SetScorllBarShow(True)
        iStartRow = -1
        if bIsInit:
            import mdguide
            if len(self.m_lstEquipmentDatas) > 8:
                iGemEquipID = mdguide.g_dGuideCacheData.get('iGemEquipID', None)
                if iGemEquipID:
                    for idx, oItem in enumerate(self.m_lstEquipmentDatas):
                        if oItem.GetID() == iGemEquipID:
                            if idx > 7:
                                iStartRow = idx
                            
                            break
                            continue
                    
                
            
        
        self.m_oEquipmentList.Reload(iStartRow = iStartRow)

    
    def OnClickItem(self, idx, iItemID):
        self.m_iSelectID = iItemID
        if callable(self.m_oClickEquipmentItemFunc):
            self.m_oClickEquipmentItemFunc(idx, iItemID)
        

    
    def SetEnableForAllCell(self, bEnable):
        self.m_bCellEnabled = bEnable
        self.m_oEquipmentList.Reload(-1)

    
    def SetEnableOfCellByIndex(self, oCell, bEnable):
        oCell.SetEnabled(bEnable)

    
    def SetSelectItemByGemShape(self, iGemShape):
        import gem2equipposdata
        for idx, oItem in enumerate(self.m_lstEquipmentDatas):
            iShapeId = getattr(oItem, 'm_Shape', 0)
            if gem2equipposdata.IsGemWeapon(iGemShape, iShapeId):
                if self.m_iSelectID != getattr(oItem, 'm_ID', 0):
                    self.OnClickItem(idx, getattr(oItem, 'm_ID', 0))
                
                break
                continue
        



class CEquipTbViewPart(object):
    '''
\t\xb9D\xa8\xe3\xc5\xe3\xa5\xdc\xb3q\xa5\xce\xb2\xd5\xa5\xf3
\t'''
    
    def __init__(self, oTbview, oCreateItemFunc, oClickCB):
        self.m_oTbview = oTbview
        self.m_oClickCB = oClickCB
        self.m_oCreateItemFunc = oCreateItemFunc
        self.InitTableView()

    
    def GetTbAllView(self):
        return self.m_oTbview

    
    def InitTableView(self):
        self.GetTbAllView().SetDelegateNewCellOfData(misc.Functor(self.OnDelegateNewCellOfData))
        self.GetTbAllView().SetDelegateUpdateCellOfData(misc.Functor(self.OnDelegateUpdateCellOfData))
        self.GetTbAllView().SetDelegateAlignOfData(misc.Functor(self.OnDelegateAlignOfData))

    
    def OnDelegateNewCellOfData(self, oParent, dData):
        oCell = self.m_oCreateItemFunc(oParent)
        oCell.SetData(dData)
        oCell.SetSelectCB(self.m_oClickCB)
        return oCell

    
    def OnDelegateUpdateCellOfData(self, oCell, dData, bReUes):
        if bReUes:
            oCell.SetData(dData)
        

    
    def OnDelegateAlignOfData(self, dData):
        return interface.ALIGN_LEFT_MIDDLE



class CEquipForGasCellItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/equip/bagua_equipitem.dlg')
        self.m_iItemID = None
        self.m_oClickFunc = None
        self.m_oEquip = None
        self.m_oImgBg = None
        self.SetPassScrollingMessagesUp(True)

    
    def SetData(self, dEquipData):
        self.m_dData = dEquipData
        self.ResetView(dEquipData)

    
    def GetData(self):
        return self.m_dData

    
    def SetSelectCB(self, oCB):
        self.m_oClickFunc = oCB

    
    def ResetView(self, dEquipmenData):
        bSelected = dEquipmenData.get('bSelected', False)
        bEnable = dEquipmenData.get('bEnable', True)
        self.m_iItemID = dEquipmenData.get('iItemID', False)
        self.CreateItemIcon(self.m_iItemID)
        if bSelected:
            pass
        elif bEnable:
            pass
        
        iFrame = 0
        self.GetObject('img_bg').GetImageWithCount(0).SetFrame(iFrame)
        self.GetObject('text_itemName').SetText(dEquipmenData.get('sName', ''))
        self.GetObject('text_ItemLv').SetText(dEquipmenData.get('sDesc', ''))
        self.GetObject('img_tuijian').SetShow(dEquipmenData.get('bIsUse', False))
        self.m_bSelect = bSelected
        self.m_bEnable = bEnable
        None(self.GetObject('img_bg').GetImageWithCount(0).SetLight if bEnable else 6)

    
    def CreateItemIcon(self, iItemID):
        import makeitemicon
        self.m_oEquip = makeitemicon.CBackItem(self.GetObject('loc_item'))
        self.m_oEquip.CreateRealItemIcon(iItemID, 0)

    
    def LeftUp(self):
        if callable(self.m_oClickFunc) and self.m_bEnable:
            self.m_oClickFunc(self.m_iItemID)
        

    
    def LeftDown(self):
        pass

    
    def Enter(self):
        if not (self.m_bSelect) and self.m_bEnable:
            self.GetObject('img_bg').GetImageWithCount(0).SetFrame(2)
        

    
    def Leave(self):
        if not (self.m_bSelect) and self.m_bEnable:
            self.GetObject('img_bg').GetImageWithCount(0).SetFrame(0)
