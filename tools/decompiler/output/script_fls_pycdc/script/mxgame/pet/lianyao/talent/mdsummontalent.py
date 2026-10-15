# pycdc 交叉复核产物 · script.fls entry 3347
# co_filename(原始)='script/mxgame/pet/lianyao/talent/mdsummontalent.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3347.pyc (Python 2.5)

import slot
g_oModel = None

def GetModel():
    global g_oModel
    if not g_oModel:
        g_oModel = CSummonTalentModel()
    
    return g_oModel


class CSummonTalentModel(slot.ISignalSubject):
    SS_UpdateNewTalent = 'OnUpdateTalent(iPetID)'
    SS_UpdateTargetTalents = 'OnUpdateTarget(iPetID)'
    
    def __init__(self):
        self.ssInit()
        self.m_dPetTalents = { }
        self.m_dPetNewTalentFlash = { }
        self.m_dPetTargets = { }

    
    def SetPetNewTalentFlash(self, iPetID, bFlash):
        self.m_dPetNewTalentFlash[iPetID] = bFlash

    
    def SetPetNewTalent(self, iPetID, lTalent):
        self.m_dPetTalents[iPetID] = lTalent
        self.ssEmit(self.SS_UpdateNewTalent, iPetID)

    
    def GetPetNewTalent(self, iPetID):
        return self.m_dPetTalents.get(iPetID, None)

    
    def GetPetNewTalentNeedFlash(self, iPetID):
        return self.m_dPetNewTalentFlash.get(iPetID, False)

    
    def SetPetTargetCase(self, iPetID, iTargetList):
        self.m_dPetTargets[iPetID] = {
            'iTargetList': iTargetList }
        None(self.ssEmit(self), iPetID)

    
    def GetPetTargetCase(self, iPetID):
        return self.m_dPetTargets.get(iPetID, None)
