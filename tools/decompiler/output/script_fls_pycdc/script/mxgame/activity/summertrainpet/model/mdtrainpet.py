# pycdc 交叉复核产物 · script.fls entry 3888
# co_filename(原始)='script/mxgame/activity/summertrainpet/model/mdtrainpet.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3888.pyc (Python 2.5)

import slot
import trainpetdefines
g_oTrainPetModel = None

def ModuleReset():
    global g_oTrainPetModel
    g_oTrainPetModel = None


def GetModel():
    ''':rtype: CTrainPetModel'''
    global g_oTrainPetModel
    if not g_oTrainPetModel:
        g_oTrainPetModel = CTrainPetModel()
    
    return g_oTrainPetModel


class CTrainPetModel(slot.ISignalSubject):
    SS_OnAddAttrSuccess = 'OnAddAttrSuccess'
    SS_OnFeiShengSuccess = 'OnFeiShengSuccess'
    SS_OnShengLingSuccess = 'OnOnShengLingSuccess'
    
    def __init__(self):
        self.ssInit()
        self.m_dTrainPetInfo = {
            'iAddZiZhiNum': 0,
            'iShengLingNum': 0,
            'iPresentYuLingNum': 0,
            'dMaxAttr': { },
            'iResetPoint': 0 }
        self.m_dSelectPreviewSummonInfo = {
            trainpetdefines.PHYSIC_ATTACK_PET: { },
            trainpetdefines.MAGIC_ATTACK_PET: { } }

    
    def UpdateTrainPetInfo(self, dInfo):
        self.m_dTrainPetInfo.update(dInfo)

    
    def GetTrainInfoByKey(self, sKey, default = None):
        return self.m_dTrainPetInfo.get(sKey, default)

    
    def OnAddAttrSuccess(self, iAddZiZhiNum, iResetPoint):
        self.m_dTrainPetInfo['iAddZiZhiNum'] = iAddZiZhiNum
        self.m_dTrainPetInfo['iResetPoint'] = iResetPoint
        self.ssEmit(self.SS_OnAddAttrSuccess)

    
    def UpdateShengLingNum(self, iShengLingNum, iAddSkill):
        self.m_dTrainPetInfo['iShengLingNum'] = iShengLingNum
        continue
        iAddSkill

    
    def RefreshSelectPreviewSummonInfo(self, dPhysicPetInfo, dMagicPetInfo):
        self.m_dSelectPreviewSummonInfo[trainpetdefines.PHYSIC_ATTACK_PET] = dPhysicPetInfo
        self.m_dSelectPreviewSummonInfo[trainpetdefines.MAGIC_ATTACK_PET] = dMagicPetInfo

    
    def GetSelectPreviewSummonInfo(self):
        return self.m_dSelectPreviewSummonInfo
