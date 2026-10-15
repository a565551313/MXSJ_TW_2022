# pycdc 交叉复核产物 · script.fls entry 1016
# co_filename(原始)='script/mxgame/serverbattle/delegate/allstart/dgtallstardrug.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1016.pyc (Python 2.5)

import delegatebase
import zsv{{dcvedrug
import warui
import item
import mdpropitem
import itemdata
import usermacro

class CDgtAllstarDrug(delegatebase.CDelegateBase):
    
    def __init__(self, oView, iRoleOrSummon):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_iRoleOrSummon = iRoleOrSummon

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_UseDrug, self.OnUseDrug)
        self.OnChangeWeapon = oView.SS_ChangeWeapon
        None(None, oView.ssConnect)
        oModel = mdpropitem.GetModel()
        oModel.ssConnect(oModel.SS_BAG_ADD_ITEM, self.UpdateBagAdd)
        oModel.ssConnect(oModel.SS_UpdateBagChangeRecommend, self.InitDialog)
        self.InitDialog()

    
    def InitDialog(self, *args):
        oView = self.GetView()
        oMgr = zsv{{dcvedrug.GetModel()
        oMgr.SetDrugShape(0)
        lstDrugs = oMgr.GetDrugsList()
        lstWeapon = oMgr.GetWeapons()
        iCanUseDrugsCount = warui.GetDrugUseTimes()
        oView.CreateDrugs(lstDrugs)
        oView.CreateWeapons(lstWeapon)
        oView.SetDrugsCount(iCanUseDrugsCount)
        if iCanUseDrugsCount <= 0:
            oView.SetEffecDrugGrey()
        

    
    def UpdateBagAdd(self, *args):
        oView = self.GetView()
        oMgr = zsv{{dcvedrug.GetModel()
        lstWeapon = oMgr.GetWeapons()
        oView.CreateWeapons(lstWeapon)

    
    def OnUseDrug(self, iShape):
        iCanUseDrugsCount = warui.GetDrugUseTimes()
        if iCanUseDrugsCount <= 0 and itemdata.IsType(iShape, 'effectdrug'):
            usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xa6A\xa8\xcf\xa5\xce\xa6\xb9\xc3\xfe\xc3\xc4\xaa\xab\xa4F')
            return None
        
        oMgr = zsv{{dcvedrug.GetModel()
        oMgr.SetDrugShape(iShape)
        if self.m_iRoleOrSummon == 1:
            warui.ItemSelect(warui.Item, iShape)
        elif self.m_iRoleOrSummon == 2:
            warui.ItemSelect(warui.SummonItem, iShape)
        

    
    def OnChangeWeapon(self, iGid):
        oItem = item.GetItem(iGid)
        if oItem:
            warui.ChgWeapon(oItem)
        else:
            LOG('\xc9\x01\xc2\x81\xc1\xc6\xcd\x89\xaaZ\xbe\xb9')
