# pycdc 交叉复核产物 · script.fls entry 1045
# co_filename(原始)='script/mxgame/makeequip/delegate/delegateeightdiagrams/dgtremovegas.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1045.pyc (Python 2.5)

import builddefine
import delegatebase
import item
import itemdata
import itemdefine
import mdeightdiagrams
import netbuild
import nethero
import permission
import usermacro
import dlgremovegas

class CNewGasRemoveDelegate(delegatebase.CDelegateBase):
    
    def GetModel(self):
        return mdeightdiagrams.GetGasRemoveModel()

    
    def Init(self):
        netbuild.C2SGetGasRemoveList()
        oView = self.GetView()
        oView.ssConnect(oView.SS_RemoveGas, self.OnGasRemove)
        oView.ssConnect(oView.SS_PutItem, self.OnChangeItem)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdateSelectItem, self.OnUpdateSelectItem)
        self.OnUpdateSelectItem()

    
    def OnChangeItem(self, iItemID):
        netbuild.C2SGasRemovePutItem(iItemID)

    
    def OnGasRemove(self, iType = 6):
        oView = self.GetView()
        iItemID = self.GetModel().GetSelectItem()
        bRequest = None if permission.IsOpenGossipAlter() else bool(oView.GetInputItems())
        if bRequest:
            nethero.C2SBaguaMake(iType, [
                iItemID])
        else:
            usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xb7Q\xadn\xbe\xde\xa7@\xaa\xba\xb8\xcb\xb3\xc6')

    
    def OnUpdateSelectItem(self, iItemID = None):
        import opengasinterface
        if permission.IsOpenGossipAlter():
            self.OnUpdateSelectItemNew()
            return None
        
        oView = self.GetView()
        iItemID = self.GetModel().GetSelectItem()
        oItem = item.GetItem(iItemID)
        if not iItemID or not oItem:
            oView.ClearInputItem()
        else:
            dInfo = self.GetModel().GetSelectItemInfo()
            iSum = 0
            iSum += opengasinterface.GetGradeReady(dInfo['iSelItemID'])
            if dInfo['ShapeList'] and not iSum:
                for sName in dInfo['gasInfoList']:
                    iSum += opengasinterface.GetSumByName(sName)
                
            
            iSum = int(iSum * 0.25)
            dInfo['ShapeList'] = [
                itemdefine.ID_GAS_BAGUA]
            dInfo['gasInfoList'] = [
                '\xad\xe9\xc2\xf7\xaa\xf0\xc1\xd9:%d' % iSum]
            oView.RefershEquipInfo(dInfo, oItem.\xa5\x87\x96\xb2os(), True)

    
    def OnUpdateSelectItemNew(self):
        oView = self.GetView()
        iItemID = self.GetModel().GetSelectItem()
        oItem = item.GetItem(iItemID)
        if not iItemID or not oItem:
            oView.ClearInputItem()
        else:
            dInfo = self.GetModel().GetSelectItemInfo()
            dInfo['ShapeList'] = [
                itemdefine.ID_GAS_BAGUA,
                itemdefine.ID_BIND_CASH_ICON,
                itemdefine.ID_ITEM_XTJC_NEW]
            oView.RefershEquipInfo(dInfo)
            oItem = item.GetItem(iItemID)
            oView.CreateEquipShowPanel(oItem)



class CGasEquipDgt(delegatebase.CDelegateBase):
    
    def Init(self):
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdateSelectItem, self.OnUpdateSelectItem)
        oModel.ssConnect(oModel.SS_UpdateAllEquipInfo, self.OnUpdateAllEquipInfo)
        oModel.ssConnect(oModel.SS_OperateFinish, self.OnOperateFinish)
        self.UpdateTableView()

    
    def GetModel(self):
        return mdeightdiagrams.GetGasRemoveModel()

    
    def GetShowDataList(self):
        '''
\t\t\xb3\xd0\xab\xd8\xa9\xd2\xa6\xb3\xb8\xcb\xb3\xc6
\t\t:return:
\t\t'''
        dInfo = []
        for iItemID, dItemInfo in self.GetModel().GetAllEquipInfo().iteritems():
            oItem = item.GetItem(iItemID)
            if not oItem:
                continue
            
            iBaoGuaType = dItemInfo.get('iBaoGuaType', 0)
            dInfo.append({
                'bSelected': self.GetModel().GetSelectItem() == iItemID,
                'iItemID': iItemID,
                'sName': itemdata.GetData(oItem.GetShape())[0],
                'sDesc': builddefine.ID2Bagua.get(iBaoGuaType, ''),
                'bIsUse': oItem.\xa5\x87\x96\xb2os() <= item.MAX_EQUIP_POS })
        
        return dInfo

    
    def UpdateTableView(self):
        oTableView = self.GetView().GetTbAllView()
        oTableView.ReloadWithDiffSourceDict(self.GetShowDataList())

    
    def OnOperateFinish(self, iItemID):
        self.GetModel().SetSelectItem(0, { })
        netbuild.C2SGetGasRemoveList()

    
    def OnUpdateSelectItem(self, iItemID):
        self.UpdateTableView()

    
    def OnUpdateAllEquipInfo(self, dAllEquipInfo):
        self.UpdateTableView()
