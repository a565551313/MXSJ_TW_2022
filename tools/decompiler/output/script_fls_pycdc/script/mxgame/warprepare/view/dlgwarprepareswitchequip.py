# pycdc 交叉复核产物 · script.fls entry 828
# co_filename(原始)='script/mxgame/warprepare/view/dlgwarprepareswitchequip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_828.pyc (Python 2.5)

'''
import dlgwarprepareswitchequip as d
d.Show()

'''
import C_sys
import commondialog
import cursor
import dlggetinfo
import gamemoduledefines
import handobj
import interface
import combdialog
import item
import itemdata
import itemdefine
import itemmgr
import misc
import slot
import dgtwarprepareswitchequip
import stopgamemoduleinterface
import style
import tipsclosemgr
import ui
import wrapinterface
g_oDialog = None

def ModuleReset():
    global g_oDialog
    g_oDialog = None


def Show():
    global g_oDialog
    if not g_oDialog:
        g_oDialog = CWarPrepareSwitchDialog(interface.DialogPanel)
    else:
        g_oDialog.Topmost()


class CWarPrepareSwitchDialog(combdialog.CCombDialog, itemmgr.CItemListBase, slot.ISignalSubject):
    SS_ClickCase = 'OnCaseClick(idx)'
    SS_ClickCaseRename = 'OnCaseRename(idx)'
    SS_ClickCaseUse = 'OnCaseUse(idx)'
    SS_RightUpCaseItem = 'OnCaseRightUp(idx, dItem)'
    SS_HoldHandCaseItem = 'OnHoldHandCaseItem(idx, iPos, iID)'
    SS_RightUpBagItem = 'OnBagRightUp(iItemID)'
    SS_LeftUpCaseItem = 'OnLeftUpCaseItem(idx, iPos)'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/warprepare/equip_project.dlg')
        itemmgr.CItemListBase.__init__(self, 'lst_item', 'img_item')
        interface.Center(self)
        self.ssInit()
        self.m_dCase = { }
        self.InitDlg()
        self.InitDelegate()

    
    def SetCaseEquipBoxSelect(self, iCaseIndex, iEquipPos, bSelect):
        self.m_dCase[iCaseIndex].SetEquipBoxSelect(iEquipPos, bSelect)

    
    def SetCaseItem(self, iCaseIndex, iEquipPos, dItem):
        self.m_dCase[iCaseIndex].SetItem(iEquipPos, dItem)

    
    def SetCaseName(self, iCaseIndex, sCaseName):
        self.m_dCase[iCaseIndex].SetName(sCaseName)

    
    def SetCaseFight(self, iCaseIndex, iFight):
        self.m_dCase[iCaseIndex].SetFight(iFight)

    
    def SetCaseSelect(self, iCaseIndex):
        for iEachIndex, oItem in self.m_dCase.iteritems():
            if iEachIndex == iCaseIndex:
                oItem.SetSelectShow(True)
                continue
            oItem.SetSelectShow(False)
        

    
    def SetCaseUsing(self, iCaseIndex):
        for iEachIndex, oItem in self.m_dCase.iteritems():
            if iEachIndex == iCaseIndex:
                oItem.SetUsing(True)
                continue
            oItem.SetUsing(False)
        

    
    def ShowCaseRenameDialog(self, sName, oReNameCB):
        commondialog.ShowInputDialog('"%s"\xa7\xef\xa6W\xa4\xe8\xae\xd7' % sName, oReNameCB, ishidedlg = False, limit = 6, checktxt = '\xb3\xcc\xa6h\xbf\xe9\xa4J3\xad\xd3\xa6r')

    
    def CloseCaseRenameDialog(self):
        commondialog.HideInputDialog()

    
    def InitDelegate(self):
        self.m_Delegates = [
            dgtwarprepareswitchequip.CWarPrepareSwitchEquipDelegate(self)]

    
    def InitDlg(self):
        for iIndex in (1, 2):
            self.m_dCase[iIndex] = CWarPrepareEquipProjectItem(self, iIndex)
            (iX, iY) = self.GetObject('loc_project%d' % iIndex).GetPos()
            self.m_dCase[iIndex].SetPos(iX, iY)
        

    
    def GetMaxLine(self, iItemLine):
        return max(iItemLine, 6)

    
    def GetItems(self):
        dItems = { }
        dTotalItems = item.GetItems()
        for iPos, oItem in dTotalItems.iteritems():
            if itemdata.IsType(oItem.GetShape(), 'equip'):
                dItems[iPos] = oItem
                continue
        
        tItemList = dItems.items()
        tItemList.sort(key = (lambda tItem: tItem[0]))
        return tItemList

    
    def GetInterfaceItemClass(self):
        return CBagInterfaceItem

    
    def ChangeItem(self, oIt, dItemData):
        oIt.SetRightUpCB(misc.Functor(self.OnItemRightUp))

    
    def OnProjectSelect(self, iIndex):
        self.ssEmit(self.SS_ClickCase, iIndex)

    
    def OnProjectRename(self, iIndex):
        self.ssEmit(self.SS_ClickCaseRename, iIndex)

    
    def OnProjectUse(self, iIndex):
        self.ssEmit(self.SS_ClickCaseUse, iIndex)

    
    def OnProjectRightUpItem(self, iIndex, dItem):
        self.ssEmit(self.SS_RightUpCaseItem, iIndex, dItem)

    
    def OnProjectHoldHandItem(self, iIndex, iEquipPos, iItemID):
        self.ssEmit(self.SS_HoldHandCaseItem, iIndex, iEquipPos, iItemID)

    
    def OnProjectLeftUpItem(self, iIndex, iEquipPos):
        self.ssEmit(self.SS_LeftUpCaseItem, iIndex, iEquipPos)

    
    def OnItemRightUp(self, oIt):
        oItem = oIt.GetItem()
        if oItem:
            self.ssEmit(self.SS_RightUpBagItem, oItem.GetID())
        

    
    def CloseWindow(self):
        global g_oDialog
        g_oDialog = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.CloseWindow()
        



class CWarPrepareEquipProjectItem(combdialog.CCombSubWnd):
    EQUIP_LOC = {
        itemdefine.EQUIPPOS_CAP: ('loc_cap', '\xb4U\xa4l'),
        itemdefine.EQUIPPOS_WEAPON: ('loc_weapon', '\xaaZ\xbe\xb9'),
        itemdefine.EQUIPPOS_CLOTH: ('loc_cloth', '\xf1Z\xa5\xd2'),
        itemdefine.EQUIPPOS_SASH: ('loc_sash', '\xb8y\xb1a'),
        itemdefine.EQUIPPOS_CUFF: ('loc_cuff', '\xc5@\xb5\xc3'),
        itemdefine.EQUIPPOS_MAGIC: ('loc_special', '\xaak\xc4_'),
        itemdefine.EQUIPPOS_NECKLACE: ('loc_necklace', '\xb6\xb5\xc3\xec'),
        itemdefine.EQUIPPOS_RING: ('loc_ring', '\xa7\xd9\xab\xfc'),
        itemdefine.EQUIPPOS_SHOSE: ('loc_shoe', '\xbec\xa4l'),
        itemdefine.EQUIPPOS_SECONDWEAPON: ('loc_viceweapon', '\xb0\xc6\xaaZ\xbe\xb9') }
    
    def __init__(self, oParent, iIndex):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/warprepare/project_item.dlg')
        self.m_iIndex = iIndex
        self.m_dEquips = { }
        self.InitDlg()
        self.SetSelectShow(False)

    
    def SetSelectShow(self, bSelect):
        self.GetObject('frame_select').SetShow(bSelect)

    
    def SetEquipBoxSelect(self, iEquipPos, bSelect):
        self.m_dEquips[iEquipPos].SetSelectBoxShow(bSelect)

    
    def SetName(self, sName):
        self.GetObject('text_name').SetText(sName)

    
    def SetUsing(self, bUsing):
        self.SetShowObject('text_useing', bUsing)
        self.SetShowObject('btn_use', not bUsing)

    
    def SetItem(self, iPos, dItem):
        self.m_dEquips[iPos].SetItemInfo(dItem)

    
    def SetFight(self, iFight):
        self.GetObject('txt_total').SetText(str(iFight))

    
    def InitDlg(self):
        for sLocName, sTips in self.EQUIP_LOC.iteritems():
            (iX, iY) = self.GetObject(sLocName).GetPos()
            self.m_dEquips[iPos] = CEquipItemIcon(self, iPos, sTips, misc.Functor(self.OnEquipRightUp), misc.Functor(self.OnEquipHoldHand), misc.Functor(self.OnEquipLeftUp))
            self.m_dEquips[iPos].SetPos(iX, iY)
        

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        self.OnSelect()

    
    def OnSelect(self):
        self.GetParent().OnProjectSelect(self.m_iIndex)

    
    def OnEquipLeftUp(self, iPos):
        self.OnSelect()
        self.GetParent().OnProjectLeftUpItem(self.m_iIndex, iPos)

    
    def OnEquipRightUp(self, dInfo):
        self.GetParent().OnProjectRightUpItem(self.m_iIndex, dInfo)

    
    def OnEquipHoldHand(self, iPos, iItemID):
        self.GetParent().OnProjectHoldHandItem(self.m_iIndex, iPos, iItemID)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.OnSelect()
            if stopgamemoduleinterface.CheckStop(gamemoduledefines.GAMEMODULE_ZHANBEINAME):
                return None
            
            self.GetParent().OnProjectRename(self.m_iIndex)
        elif iMsgID == 2:
            self.OnSelect()
            self.GetParent().OnProjectUse(self.m_iIndex)
        



class CBagInterfaceItem(item.CInterfaceItem):
    
    def __init__(self, parent, x, y, msgid, ebxi~jmoiitems = None):
        item.CInterfaceItem.__init__(self, parent, x, y, msgid, ebxi~jmoiitems)
        self.m_oRightUpCB = None

    
    def SetItem(self, oItem):
        item.CInterfaceItem.SetItem(self, oItem)
        if oItem and oItem.m_Pos < item.ITEM_START:
            self.m_oEquipMark = interface.CEffectObject(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/equip.png', interface.UIPath)
            self.m_oEquipMark.SetPos(-6, -5)
            self.m_oEquipMark.SetZ(1001)
        else:
            self.m_oEquipMark = None

    
    def SetRightUpCB(self, oRightUpCB):
        self.m_oRightUpCB = oRightUpCB

    
    def RightUp(self):
        if self.m_oRightUpCB:
            self.m_oRightUpCB(self)
        

    
    def LeftUp(self):
        self.ReleaseHoldHand()
        item.CInterfaceItem.LeftUp(self)

    
    def LeftDown(self):
        item.CInterfaceItem.LeftDown(self)
        if self.m_Item:
            self.DelayHoldHand()
        

    
    def DelayHoldHand(self):
        self.ReleaseHoldHand()
        
        def hand(obj):
            import handobj
            if hasattr(obj, 'm_DelayHand') and obj.m_DelayHand and obj.m_Item and not handobj.IsHand():
                handobj.HandHoldItem(self.m_Item.m_ID, self.m_InterfaceItems, None, None)
            

        self.m_HoldHandAni = self.CreatePyCommand(6, hand)
        self.m_DelayHand = True

    
    def ReleaseHoldHand(self):
        self.m_DelayHand = False
        if hasattr(self, 'm_HoldHandAni') and self.m_HoldHandAni:
            self.m_HoldHandAni.Release()
            self.m_HoldHandAni = None
            import handobj
            handobj.Clear()
        



class CEquipItemIcon(interface.CClickBox):
    
    def __init__(self, oParent, iPos, sTxt, oRightUpCB, oHoldHandCB, oLeftUpCB):
        interface.CClickBox.__init__(self, oParent, 44, 44, alpha = 0)
        self.m_dItem = None
        self.m_oImage = None
        self.m_sTxt = sTxt
        self.m_oRightUpCB = oRightUpCB
        self.m_oHoldHandCB = oHoldHandCB
        self.m_oLeftUpCB = oLeftUpCB
        self.m_iPos = iPos
        self.m_oTips = None
        if interface.IsNewStyle():
            self.m_oPosBox = ui.CImage(self, style.GetStr('item.CInterfaceBase', 'item_select_img'), interface.UIPath)
            (iSelectImgOffsetX, iSelectImgOffsetY) = style.GetIntTuple('item.CInterfaceBase', 'item_select_img_offset')
            self.m_oPosBox.SetPos(-1 + iSelectImgOffsetX, -2 + iSelectImgOffsetY)
            self.m_oSelBox = ui.CImage(self, 'combdialog3/\xb5\xc0\xbe\xdf\xbf\xf2/\xd1\xa1\xd6\xd0\xbf\xf2/xuanzhongkuang3.png', interface.UIPath)
            self.m_oSelBox.SetPos(-1, -2)
        else:
            self.m_oPosBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
            self.m_oPosBox.SetPos(-1, -1)
            self.m_oSelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
            self.m_oSelBox.SetFrame(2)
            self.m_oSelBox.SetPos(-1, -1)
        self.m_oPosBox.SetZ(1)
        self.m_oSelBox.SetZ(2)
        self.m_oPosBox.SetShow(False)
        self.m_oSelBox.SetShow(False)

    
    def SetSelectBoxShow(self, bShow):
        self.m_oSelBox.SetShow(bShow)

    
    def LeftUp(self):
        self.m_oLeftUpCB(self.m_iPos)
        self.ReleaseHoldHand()

    
    def LeftDown(self):
        if self.m_dItem:
            self.DelayHoldHand()
        

    
    def DelayHoldHand(self):
        ()()
        
        def hand(obj):
            if hasattr(obj, 'm_DelayHand') and obj.m_DelayHand and obj.m_oImage and not handobj.IsHand():
                handobj.HandWarPrepareItem(self.m_dItem['tItemID'], self.m_dItem['iShape'], misc.Functor(obj.OnHoldEnd))
                obj.m_oImage.SetShow(False)
            

        self.m_HoldHandAni = self.CreatePyCommand(6, hand)
        self.m_DelayHand = True

    
    def OnHoldEnd(self):
        (iX, iY) = cursor.GetCursorPos()
        print C_sys.GetObjects(iX, iY)
        if self in C_sys.GetObjects(iX, iY):
            if self.m_oImage:
                self.m_oImage.SetShow(True)
            
        else:
            self.RightUp()

    
    def ReleaseHoldHand(self):
        self.m_DelayHand = False
        if hasattr(self, 'm_HoldHandAni') and self.m_HoldHandAni:
            self.m_HoldHandAni.Release()
            self.m_HoldHandAni = None
            handobj.Clear()
        

    
    def OnHoldHand(self, oHandItem):
        if oHandItem.m_Type == handobj.TYPE_HOLDITEM:
            self.m_oHoldHandCB(self.m_iPos, oHandItem.m_ID)
        

    
    def SetItemInfo(self, dItem):
        if not dItem:
            self.m_oImage = None
        else:
            self.m_oImage = item.CreateItem44Image(self, dItem['iShape'], dItem['iKey'])
        self.m_dItem = dItem

    
    def RightUp(self):
        self.m_oRightUpCB(self.m_dItem)

    
    def Enter(self):
        if not self.m_dItem:
            oTips = wrapinterface.CTextTips(self.GetParent(), -1, self.m_sTxt, interface.FontLT14_3, direct = 1)
            oTips.SetOwner(self)
            self.m_oTips = oTips
        else:
            oTips = dlggetinfo.ShowWarprepareItemInfo(self.m_dItem['iShape'], self.m_dItem['tItemID'][0], self.m_dItem['tItemID'][1])
            oTips.SetOwner(self)
            tipsclosemgr.Regist(oTips)
        self.m_oPosBox.SetShow(True)

    
    def Leave(self):
        self.m_oPosBox.SetShow(False)
        self.m_oTips = None
        tipsclosemgr.CheckClose()



def Test():
    '''
\timport dlgwarprepareswitchequip
\tdlgwarprepareswitchequip.Test()
\t:return:
\t'''
    import mdwarprepareswitchequip
    oModel = mdwarprepareswitchequip.GetModel()
    dItems = {
        itemdefine.EQUIPPOS_CAP: 60010,
        itemdefine.EQUIPPOS_WEAPON: 50020,
        itemdefine.EQUIPPOS_SASH: 66010,
        itemdefine.EQUIPPOS_CUFF: 63010 }
    for iPos, iShape in dItems.items():
        dItems[iPos] = {
            'iShape': iShape,
            'iKey': 0,
            'iPos': iPos,
            'tItemID': (1, iPos) }
        oModel.SetCaseItems(1, iPos, dItems[iPos])
    
    Show()
