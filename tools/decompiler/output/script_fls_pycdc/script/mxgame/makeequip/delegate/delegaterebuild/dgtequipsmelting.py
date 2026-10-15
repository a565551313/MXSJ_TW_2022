# pycdc 交叉复核产物 · script.fls entry 3521
# co_filename(原始)='script/mxgame/makeequip/delegate/delegaterebuild/dgtequipsmelting.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3521.pyc (Python 2.5)

import builddefine
import delegatebase
import itemdata
import mdmakeequip
import mdequipsmelting
import mdequipspecialeff
import mdpropitem

class CEquipSmeltingDelegate(delegatebase.CDelegateBase):
    '''
\t\xad\xab\xb3y\xac\xc9\xad\xb1\xabH\xae\xa7\xa8\xea\xb7s\xbc\xc6\xbe\xda
\t'''
    
    def __init__(self, oView):
        self.m_iEquipID = 0
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetView(self):
        ''':rtype: dlgequipsmelting.CEquipSmeltingDlg'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickAItem, self.OnClickAItem)
        oView.ssConnect(oView.SS_ClickDelAItem, self.OnClickDelAItem)
        oView.ssConnect(oView.SS_ApplySmelting, self.OnApplySmelting)
        oView.ssConnect(oView.SS_CancelSmelting, self.OnCancelSmelting)
        oView.ssConnect(oView.SS_MakeSureSmelting, self.OnMakeSureSmelting)
        oView.ssConnect(oView.SS_ClickSelectBtn, self.OnClickSelectBtn)
        oEquipSmeltingMgr = mdequipsmelting.GetEquipSmeltingMgr()
        oEquipSmeltingMgr.ssConnect(oEquipSmeltingMgr.SS_UpdateBeSmeltedEquipData, self.OnUpdateBeSmeltedEquip)
        oEquipSmeltingMgr.ssConnect(oEquipSmeltingMgr.SS_UpdateSmeltingInfo, self.OnUpdateSmeltingInfo)
        oEquipSmeltingMgr.ssConnect(oEquipSmeltingMgr.SS_ClearEquipInfo, self.OnClearEquipInfo)
        oEquipSpecialEffMgr = mdequipspecialeff.GetEquipSpecialEffMgr()
        oEquipSpecialEffMgr.ssConnect(oEquipSpecialEffMgr.SS_UpdateSpecialEffData, self.OnUpdateSpecialEffData)
        oPropItem = mdpropitem.GetModel()
        oPropItem.ssConnect(oPropItem.SS_UpdateBagInfoChange, self.OnUpdateBagInfoChange)
        self.InitDlg()

    
    def InitDlg(self):
        oView = self.GetView()
        self.ClearInfo()
        self.RefreshSpecialEff(mdequipspecialeff.GetEquipSpecialEffMgr().GetSpecialEffData())
        self.RefreshItemPoint(mdequipsmelting.GetEquipSmeltingMgr().GetBeSmeltedEquip())
        oView.SetSmeltingTips(builddefine.TYPE_SMELTING_NONE)

    
    def ClearInfo(self):
        oView = self.GetView()
        oView.SetSmeltingFraction('')
        oView.SetLastTime('')
        oView.SetEquipName('')
        self.ClearItemSelect()

    
    def SetSmeltingInfo(self, \xee\xce\xeb\xfe\xeb):
        oView = self.GetView()
        iType = \xee\xce\xeb\xfe\xeb.get(builddefine.KEY_SMELTING_MODE, builddefine.TYPE_SMELTING_NONE)
        iFraction = \xee\xce\xeb\xfe\xeb.get(builddefine.KEY_SMELTING_FRACTION, 0)
        iNeedTime = \xee\xce\xeb\xfe\xeb.get(builddefine.KEY_SMELTING_NEED_TIME, 0)
        iLastTime = \xee\xce\xeb\xfe\xeb.get(builddefine.KEY_SMELTING_LAST_TIME, 0)
        iItemID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
        if not iItemID:
            oView.DelEquipIcon()
            oView.SetEquipName('')
            self.ClearItemSelect()
        
        if iType in [
            builddefine.TYPE_SMELTING_APPLY,
            builddefine.TYPE_SMELTING_NONE]:
            oView.SetSmeltingFraction(iFraction)
            if iNeedTime:
                oView.SetNeedTime(iNeedTime)
            else:
                oView.SetNeedTime('\xa5\xdf\xa7Y')
            oView.SetLastTime('')
            oView.SelApplyBtn()
        elif iType == builddefine.TYPE_SMELTING_MAKE_SURE:
            oView.SetSmeltingFraction(iFraction)
            oView.SetNeedTime('')
            oView.SetLastTime('\xa5i\xa5H\xb6i\xa6\xe6\xa4\xc0\xb8\xd1')
            oView.SelSureBtn()
        elif iType == builddefine.TYPE_SMELTING_CANCEL:
            oView.SetSmeltingFraction(iFraction)
            oView.SetNeedTime('')
            oView.SetLastTime('%d\xae\xc9%d\xa4\xc0' % (iLastTime / 60 / 60, iLastTime / 60 % 60))
            oView.ResetBtnSel()
        

    
    def SelectItem(self, iItemPos):
        oView = self.GetView()
        dInterfaceItem = oView.GetInterfaceItem()
        if iItemPos not in dInterfaceItem:
            return None
        
        it = dInterfaceItem[iItemPos].m_Item
        if not it:
            return None
        
        iItemType = mdmakeequip.GetType(it.m_Shape)
        if iItemType == builddefine.TYPE_ITEM_EQUIP:
            iSelSmeltEquipID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
            for oItem in dInterfaceItem.values():
                if oItem.GetItem() and oItem.GetItem().GetID() == iSelSmeltEquipID:
                    oItem.Select(False)
                    continue
            
            oView.CreateEquipIcon(iItemPos)
            dInterfaceItem[iItemPos].Select(True)
            oView.SetEquipName(itemdata.GetData(it.m_Shape)[0])
            mdequipsmelting.GetEquipSmeltingMgr().SetSelSmeltEquip(it.m_ID)
        else:
            dInterfaceItem[iItemPos].Select(False)
            return None

    
    def ClearItemSelect(self):
        oView = self.GetView()
        dInterfaceItem = oView.GetInterfaceItem()
        for oItem in dInterfaceItem.values():
            oItem.Select(False)
        

    
    def RefreshSpecialEff(self, dSpecialEffData):
        oView = self.GetView()
        for it in oView.GetInterfaceItem().values():
            if it.GetItemId() in dSpecialEffData:
                it.ShowSpecialEff(*dSpecialEffData[it.GetItemId()])
                continue
        

    
    def RefreshItemPoint(self, dSpecialEffData):
        oView = self.GetView()
        for it in oView.GetInterfaceItem().values():
            if it.GetItemId() in dSpecialEffData:
                it.ShowItemPoint(dSpecialEffData[it.GetItemId()])
                continue
        

    
    def OnClickAItem(self, iItemPos):
        self.SelectItem(iItemPos)

    
    def OnClickDelAItem(self, iItemPos):
        oView = self.GetView()
        if iItemPos == builddefine.TYPE_ITEM_EQUIP:
            oView.DelEquipIcon()
            oView.SetEquipName('')
            mdequipsmelting.GetEquipSmeltingMgr().SetSelSmeltEquip(0)
        
        self.ClearInfo()

    
    def OnApplySmelting(self):
        iItemID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
        if not iItemID:
            return None
        
        LOG_DEBUG('\xa5\xd3\xbd\xd0\xba\xb2\xb7\xd2', iItemID)
        import netcommon
        netcommon.C2SSmeltEquip(builddefine.TYPE_SMELTING_APPLY, iItemID)

    
    def OnCancelSmelting(self):
        iItemID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
        if not iItemID:
            return None
        
        LOG_DEBUG('\xa8\xfa\xae\xf8\xba\xb2\xb7\xd2', iItemID)
        import netcommon
        netcommon.C2SSmeltEquip(builddefine.TYPE_SMELTING_CANCEL, iItemID)

    
    def OnMakeSureSmelting(self):
        iItemID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
        if not iItemID:
            return None
        
        LOG_DEBUG('\xbdT\xbb{\xba\xb2\xb7\xd2', iItemID)
        import netcommon
        netcommon.C2SSmeltEquip(builddefine.TYPE_SMELTING_MAKE_SURE, iItemID)

    
    def OnClickSelectBtn(self, iType):
        oView = self.GetView()
        oView.SetSmeltingTips(iType - 1)

    
    def OnUpdateBagInfoChange(self, iType, iItemID, iItemKey, sExt):
        oView = self.GetView()
        iSelSmeltItemID = mdequipsmelting.GetEquipSmeltingMgr().GetSelSmeltEquip()
        if iItemID == iSelSmeltItemID:
            oView.DelEquipIcon()
            mdequipsmelting.GetEquipSmeltingMgr().SetSelSmeltEquip(0)
        

    
    def OnUpdateBeSmeltedEquip(self, dBeSmeltedEquip):
        self.RefreshItemPoint(dBeSmeltedEquip)

    
    def OnUpdateSmeltingInfo(self, dSmeltingInfo):
        self.SetSmeltingInfo(dSmeltingInfo)

    
    def OnUpdateSpecialEffData(self, dSpecialEffData):
        self.RefreshSpecialEff(dSpecialEffData)

    
    def OnClearEquipInfo(self):
        oView = self.GetView()
        mdequipsmelting.GetEquipSmeltingMgr().SetSelSmeltEquip(0)
        oView.ClearInfo()
        self.ClearInfo()
