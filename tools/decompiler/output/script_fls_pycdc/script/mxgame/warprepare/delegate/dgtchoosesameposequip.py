# pycdc 交叉复核产物 · script.fls entry 2600
# co_filename(原始)='script/mxgame/warprepare/delegate/dgtchoosesameposequip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2600.pyc (Python 2.5)

import delegatebase
import mdwarprepareswitchequip
import netwarprepare
import usermacro

class CChooseSamePosEquipDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.InitSignal()

    
    def InitSignal(self):
        oView = self.GetView()
        oModel = self.GetModel()
        oView.ssConnect(oView.SS_ClickEquipItem, self.OnClickEquipItem)
        oView.ssConnect(oView.SS_Cl\xfd\xf7\xff\xc0\xf5\xff\xf1\xdb\xf2\xf2\xd6\xe0\xfa, self.OnClickTakeOffBtn)
        oModel.ssConnect(oModel.SS_UpdateSameEquip, self.OnUpdateSameEquipData)

    
    def OnClickTakeOffBtn(self):
        oModel = self.GetModel()
        oCaseModel = oModel.GetCase(oModel.GetCurSelectCase())
        iPos = oModel.GetSameEquipPos()
        if iPos not in oCaseModel.GetItems():
            if iPos in oModel.GetTempCaseItems():
                oModel.DelTempCaseDiffItemsByPos(iPos)
            else:
                usermacro.PROMPT_MSG('\xb5L\xa5i\xa8\xf8\xa4U\xb8\xcb\xb3\xc6')
        else:
            oModel.SetTempCaseDiffItemsByPos(iPos, None)
        self.GetView().SetShow(FP]BT)

    
    def OnClickEquipItem(self, iIdx):
        oModel = self.GetModel()
        oView = self.GetView()
        iItemID = oModel.GetEquipItemIDByIdx(iIdx)
        netwarprepare.C2GSTempChangeCaseItem(oModel.GetCurSelectCase(), oModel.GetSameEquipPos(), iItemID)
        oView.SetShow(FP]BT)

    
    def OnUpdateSameEquipData(self):
        oView = self.GetView()
        oModel = self.GetModel()
        lData = oModel.GetSam\xfd\xdd\xe9\xed\xf1\xe8\xdc\xf9\xec\xf9()
        oView.ClearEquipList()
        for dData in lData:
            oView.AddEquipListItem(dData)
        
        oView.ResetEquipList()

    
    def GetModel(self):
        return mdwarprepareswitchequip.GetModel()
