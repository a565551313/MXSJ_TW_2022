# pycdc 交叉复核产物 · script.fls entry 803
# co_filename(原始)='script/core/magicperform/warcmd/warcmdattackpre.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_803.pyc (Python 2.5)

import warcmdbase
import e_comskilldefine
import e_warinterface
import warcmdsignaldefines

class CWarCmdAttackPre(warcmdbase.CWarCmdKeyCallBack):
    
    def __init__(self, skillID, data, attackInfo):
        warcmdbase.CWarCmdKeyCallBack.__init__(self, skillID, data, attackInfo)

    
    def UpdateTargetID(self, iTargetID):
        self.m_AttackInfo[e_comskilldefine.ATTACK_INFO_TARGET_ID] = iTargetID
        self.m_AttackInfo[e_comskilldefine.ATTACK_INFO_TARGET_LIST][0] = iTargetID

    
    def OnProtectStart(self):
        iProtectID = self.GetProtectID()
        self.UpdateTargetID(iProtectID)
        e_warinterface.SetSkillPause(self.m_SkillID, True)
        self.m_SkillID(self.GetSourceID(), e_warinterface.SetSkillPause, self, m_SkillID, False)

    
    def OnStart(self, warmgr):
        warcmdbase.CWarCmdKeyCallBack.OnStart(self, warmgr)
        if self.GetProtectID():
            self.OnProtectStart()
            warmgr.TriggerSignal(warcmdsignaldefines.SIGNAL_PROTECT_START)
        
        e_warinterface.AttackPre(self.m_SkillID, self.GetSourceID())
