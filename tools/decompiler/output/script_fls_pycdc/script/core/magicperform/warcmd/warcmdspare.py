# pycdc 交叉复核产物 · script.fls entry 2397
# co_filename(原始)='script/core/magicperform/warcmd/warcmdspare.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2397.pyc (Python 2.5)

import warcmdbase
import e_comskilldefine
import e_warinterface

class CWarCmdSpare(warcmdbase.CStageCmd):
    
    def __init__(self, warmgr, data, attackInfo):
        warcmdbase.CStageCmd.__init__(self, warmgr, data, attackInfo)
        self.m_TargetType = data[e_comskilldefine.SKILL_DATA_POS_TARGET]
        self.m_TargetOffsetPos = data.get(e_comskilldefine.SKILL_DATA_OFFSET_POS, (0, 0))
        self.m_AlphaStart = data.get(e_comskilldefine.SKILL_DATA_REMNANT_ALPHA_START, 255)
        self.m_Interval = max(data.get(e_comskilldefine.SKILL_DATA_REMNANT_INTERVAL, 0), 1)
        self.m_Alpha = data.get(e_comskilldefine.SKILL_DATA_REMNANT_ALPHA, 0)
        self.m_Weapon = data.get(e_comskilldefine.SKILL_DATA_SPARE_WEAPON, 0)
        self.m_WeaponLevel = data.get(e_comskilldefine.SKILL_DATA_SPARE_WEAPONLEVEL, 1)
        self.m_ComponentData = data.get(e_comskilldefine.SKILL_DATA_COMPONENT, { })
        self.m_ComponentCmd = []
        self.m_bEnd = False

    
    def OnStart(self, warmgr):
        warcmdbase.CStageCmd.OnStart(self, warmgr)
        iSourceID = self.GetSourceID()
        self.m_SpareID = e_warinterface.CreateSpare(self.m_SkillID, iSourceID)
        tTargetPos = self.CalPosByTarget(self.m_TargetType, self.m_TargetOffsetPos)
        e_warinterface.SetPos(self.m_SkillID, self.m_SpareID, *tTargetPos)
        e_warinterface.SetAlpha(self.m_SkillID, self.m_SpareID, self.m_AlphaStart)
        if self.m_Weapon > 0:
            dDesc = e_warinterface.GetCharDesc(self.m_SkillID, self.m_SpareID)
            dDesc['weapon'][0] = self.m_Weapon
            dDesc['weapon'][1] = self.m_WeaponLevel
            e_warinterface.SetDesc(self.m_SkillID, self.m_SpareID, dDesc)
        
        dAttackInfo = { }
        dAttackInfo.update(self.m_AttackInfo)
        dAttackInfo[e_comskilldefine.ATTACK_INFO_SOURCE_ID] = self.m_SpareID
        for key, comp in self.m_ComponentData.items():
            dCmdInfo = { }
            if key.startswith(e_comskilldefine.SKILL_DATA_COMPONENT_ACTION):
                sCmdType = e_comskilldefine.SKILL_TYPE_ACTION
            elif key.startswith(e_comskilldefine.SKILL_DATA_COMPONENT_MOVE):
                sCmdType = e_comskilldefine.SKILL_TYPE_MOVE
            elif key.startswith(e_comskilldefine.SKILL_DATA_COMPONENT_GHOST):
                sCmdType = e_comskilldefine.SKILL_TYPE_GHOST
            elif key.startswith(e_comskilldefine.SKILL_DATA_COMPONENT_ROLEPALETTE):
                sCmdType = e_comskilldefine.SKILL_DATA_COMPONENT_ROLEPALETTE
            
            dCmdInfo[e_comskilldefine.SKILL_DATA_TYPE] = sCmdType
            dCmdInfo.update(comp)
            oCmd = e_warinterface.CreateCmdObject(self.m_SkillID, dCmdInfo, dAttackInfo)
            oCmd.OnStart(warmgr)
            self.m_ComponentCmd.append(oCmd)
        

    
    def OnLoop(self, warmgr):
        framgCnt = (self.m_FrameCnt - self.m_StartFrame) + 1
        alpha = self.m_AlphaStart - (framgCnt / self.m_Interval) * self.m_Alpha
        alpha = max(alpha, 0)
        alpha = min(alpha, 255)
        alpha = int(alpha)
        e_warinterface.SetAlpha(self.m_SkillID, self.m_SpareID, alpha)
        for oCmd in self.m_ComponentCmd:
            oCmd.OnLoop(warmgr)
        

    
    def OnEnd(self, warmgr):
        if self.m_bEnd:
            return None
        
        for oCmd in self.m_ComponentCmd:
            oCmd.OnEnd(warmgr)
        
        e_warinterface.RemoveSpare(self.m_SkillID, self.m_SpareID)
        self.m_bEnd = True

    
    def Release(self, warmgr):
        self.OnEnd(warmgr)
