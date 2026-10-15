# pycdc 交叉复核产物 · script.fls entry 2177
# co_filename(原始)='script/mxgame/makeequip/view/viewrebuild/dlgequipidentify.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2177.pyc (Python 2.5)

'''
\xb4\xf2\xd4\xec\xbc\xf8\xb6\xa8\xd7\xd3\xbd\xe7\xc3\xe6
'''
import builddefine
import combdialog
import dgtequipIdentify
import interface
import item
import itemdata
import itemdefine
import itemmgr
import makeequipitemface
import makeitemicon
import mdmakeequip
import needadditembtn
import slot

class CEquipIdentifyDlg(combdialog.CCombSubWnd, slot.ISignalSubject, itemmgr.CItemListBase):
    SS_ClickUseMoney = 'ClickUseMoney()'
    SS_ClickUseSG = 'ClickUseSG()'
    SS_MakeSureIdentify = 'MakeSureIdentify()'
    SS_ClickAItem = 'ClickAItem(iItemPos)'
    SS_ClickDelAItem = 'ClickDelAItem(iItemPos)'
    SS_ClickAddItem = 'ClickAddItem(sKey)'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/equip/chongzao2.dlg')
        itemmgr.CItemListBase.__init__(self, 'list', 'area_items1', bUseUIPos = True)
        self.ssInit()
        self.m_DelegateList = []
        self.m_oFirstItem = None
        self.m_oSecondItem = None
        self.m_oNeedSecondItemIcon = None
        self.m_oAfterIdentifyItem = None
        self.m_dMoneyTextDict = {
            '$cost': '0',
            '$own': '0' }
        self.InitDelegate()

    
    def GetInterfaceItemClass(self):
        return makeequipitemface.CInterfaceItemWithLevel

    
    def GetItems(self):
        tItemList = []
        for pos, oItemObj in item.g_Items[item.ITEM_NORMAL].items():
            shape = oItemObj.m_Shape
            iType = mdmakeequip.GetType(shape)
            if iType == builddefine.TYPE_ITEM_EQUIP or oItemObj.m_Key & item.MARK_JIANDING == 0 or itemdata.IsType(shape, 'jianding'):
                tItemList.append((pos, oItemObj))
                continue
        
        return tItemList

    
    def GetMaxLine(self, iItemLine):
        return max(iItemLine, 2)

    
    def SetEquipName(self, sEquipName):
        self.GetObject('txt_equip_name').SetText(sEquipName)

    
    def SetIdentifyName(self, sIdentifyName):
        self.GetObject('txt_jd_name').SetText(sIdentifyName)

    
    def SetEquipLv(self, iEquipLv):
        self.GetObject('txt_equip_lv').SetText(str(iEquipLv))

    
    def SetIdentifyLv(self, iIdentifyLv):
        self.GetObject('txt_jd_lv').SetText(str(iIdentifyLv))

    
    def SetMakeGoldText(self, iCostMoney):
        self.m_dMoneyTextDict['$cost'] = str(iCostMoney)
        if iCostMoney > int(self.m_dMoneyTextDict['$own']):
            self.m_dMoneyTextDict['$cost'] = '%s%s#n' % (builddefine.COLOR_NEED, iCostMoney)
        
        self.GetObject('txt_cash').ReplaceText(self.m_dMoneyTextDict)

    
    def SetOwnMoneyText(self, iOwnMoney):
        self.m_dMoneyTextDict['$own'] = str(iOwnMoney)
        self.GetObject('txt_cash').ReplaceText(self.m_dMoneyTextDict)

    
    def GetUseMoneyBtnType(self):
        return self.GetObject('btn_ues_money').IsSelected()

    
    def SetUseMoneyBtnType(self, bType):
        self.GetObject('btn_ues_money').SetSelect(bType)
        self.ShowEnableIcon(bType)
        if self.m_oSecondItem:
            self.m_oSecondItem.SetShow(not bType)
        

    
    def GetUseSGBtnType(self):
        return self.GetObject('btn_ues_sgjd').IsSelected()

    
    def SetUseSGBtnType(self, bType):
        self.GetObject('btn_ues_sgjd').SetSelect(bType)
        self.ShowEnableIcon(bType)
        if self.m_oSecondItem:
            self.m_oSecondItem.SetShow(not bType)
        

    
    def CreateEquipIcon(self, iItemPos):
        (x, y, _, _) = self.GetLocData('img_Item1')
        self.m_oFirstItem = self.CreateUesItemIcon(x, y, 500 + builddefine.TYPE_ITEM_EQUIP, iItemPos)
        self.GetObject('txt_equiptips').SetShow(False)

    
    def DelEquipIcon(self):
        self.m_oFirstItem = None
        self.GetObject('txt_equiptips').SetShow(True)

    
    def CreateIdentifyIcon(self, iItemPos):
        (x, y, _, _) = self.GetLocData('img_Item2')
        it = self.CreateUesItemIcon(x, y, 500 + builddefine.TYPE_ITEM_IDENTIFY, iItemPos)
        it.DelQuantityText()
        it.ChangeQuantityToNeed(1)
        self.m_oSecondItem = it
        self.GetObject('txt_equiptip1').SetShow(False)

    
    def DelIdentifyIcon(self):
        self.m_oSecondItem = None
        self.m_oNeedSecondItemIcon = None
        self.GetObject('txt_equiptip1').SetShow(True)

    
    def CreateAfterIdentifyIcon(self, iItemPos):
        (x, y, _, _) = self.GetLocData('img_end')
        self.m_oAfterIdentifyItem = iItemPos.m_oAfterIdentifyItem

    
    def DelAfterIdentifyIcon(self):
        self.m_oAfterIdentifyItem = None

    
    def CreateNeedItemIcon(self, iType, iLv, iClassType):
        if iType == builddefine.TYPE_ITEM_IDENTIFY:
            oAlignObject = self.GetObject('img_Item2')
            self.m_oSecondItem = needadditembtn.CNeedAddItemBtn(oAlignObject)
            self.m_oSecondItem.SetAddCB(self.OnClickAddItem, (iType, iLv, iClassType))
            interface.Center(self.m_oSecondItem)
            iShape = itemdefine.LV_TO_IDENTIFY.get(iLv, itemdefine.ID_ITEM_30_IDENTIFY)
            self.m_oNeedSecondItemIcon = makeitemicon.CNeedItemIcon(oAlignObject, iShape, 999)
            interface.Center(self.m_oNeedSecondItemIcon)
            self.m_oNeedSecondItemIcon.SetFreeze(True)
            self.m_oNeedSecondItemIcon.DelNeedTxt()
            self.GetObject('txt_equiptip1').SetShow(False)
        

    
    def CheckSelect(self, iType, iItemID):
        for iif in self.GetInterfaceItem().itervalues():
            oItem = iif.GetItem()
            if not oItem:
                continue
            
            if iType == builddefine.TYPE_ITEM_IDENTIFY:
                if iif.GetItem().GetID() == iItemID:
                    iif.Select(False)
                
            iif.GetItem().GetID() == iItemID
            iif.Select(False)
        

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtequipIdentify.CEquipIdentifyDelegate(self)]

    
    def CreateUesItemIcon(self, iPosX, iPosY, iMsgID, iItemPos):
        it = makeequipitemface.CInterfaceItemWithLevel(self, iPosX, iPosY, iMsgID)
        it.SetZ(1)
        it.SetStyle(1 | 2)
        it.Refresh(iItemPos)
        return it

    
    def ShowEnableIcon(self, bShow):
        import ui
        import style
        if bShow:
            oAlignObject = self.GetObject('img_Item2')
            self.m_oEnableIcon = ui.CImage(oAlignObject, style.GetPath('common/itembox_disabled.igs'), interface.UIPath)
            self.m_oEnableIcon.SetZ(100)
        else:
            self.m_oEnableIcon = False

    
    def OnClickAddItem(self, dKey):
        self.ssEmit(self.SS_ClickAddItem, dKey)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.ssEmit(self.SS_ClickUseMoney)
        elif iMsgID == 3:
            self.ssEmit(self.SS_MakeSureIdentify)
        elif iMsgID == 4:
            self.ssEmit(self.SS_ClickUseSG)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 500:
            iItemPos = iMsgID - 100
            if iItemPos in self.m_InterfaceItem:
                self.ssEmit(self.SS_ClickAItem, iItemPos)
            
        elif iMsgID < iMsgID:
            pass
        elif iMsgID < 506:
            self.ssEmit(self.SS_ClickDelAItem, iMsgID - 500)
