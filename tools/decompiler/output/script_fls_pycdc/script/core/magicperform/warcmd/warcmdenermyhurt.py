# pycdc 交叉复核产物 · script.fls entry 2691
# co_filename(原始)='script/core/magicperform/warcmd/warcmdenermyhurt.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2691.pyc (Python 2.5)

import e_comskilldefine
import e_warinterface
import warcmdbase
import warcmdsignaldefines

class CWarCmdEnermyHurt(warcmdbase.CWarCmdKeyCallBack):
    
    def __init__(self, skillID, data, attackInfo):
        warcmdbase.CWarCmdKeyCallBack.__init__(self, skillID, data, attackInfo)
        self.m_Target = data.get(e_comskilldefine.SKILL_DATA_TARGET, e_comskilldefine.TARGET_TYPE_TAR)
        self.m_EnemyList = self.GetTargetList()[:]
        iProctectID = self.GetProtectID()
        if iProctectID and iProctectID not in self.m_EnemyList:
            self.m_EnemyList.append(iProctectID)
        
        self.m_lNeedGoBack = []
        self.CalNeedGoBackEnemy()

    
    def OnSourceHurt(self):
        iSkillID = self.m_SkillID
        iSourceID = self.GetSourceID()
        e_warinterface.BeginHit(iSkillID, iSourceID, 0)
        e_warinterface.EndHit(iSkillID, iSourceID)
        e_warinterface.HurtFrame(iSkillID, iSourceID)
        e_warinterface.HitEff(iSkillID, iSourceID, 0)

    
    def OnDamagebackTriggerStart(self, warmgr):
        self.m_EndFrame += 20
        warmgr.TriggerSignal(warcmdsignaldefines.SIGNAL_DAMAGEBACK_START)

    
    def OnDamagebackEnd(self, warmgr):
        if not e_warinterface.IsDied(self.m_SkillID, self.GetSourceID()):
            e_warinterface.GoBack(self.m_SkillID, self.GetSourceID(), 0)
        
        warmgr.TriggerSignal(warcmdsignaldefines.SIGNAL_DAMAGEBACK_END)

    
    def OnStart(self, warmgr):
        warcmdbase.CWarCmdKeyCallBack.OnStart(self, warmgr)
        isAtt = self.m_Target == e_comskilldefine.TARGET_TYPE_ATT
        isEnemy = self.m_Target == e_comskilldefine.TARGET_TYPE_TAR
        isBoth = self.m_Target == e_comskilldefine.TARGET_TYPE_BOTH
        if isEnemy or isBoth:
            targetList = self.m_EnemyList
            for targetID in targetList:
                if isBoth or targetID != self.GetSourceID():
                    e_warinterface.HurtFrame(self.m_SkillID, targetID)
                    continue
            
        
        if isBoth or isAtt:
            if self.GetDamageBackType() != 0:
                self.OnSourceHurt()
            
            if self.GetDamageBackType() > 0:
                self.OnDamagebackTriggerStart(warmgr)
            
        
        self.NewSkillFuhuoGoBackIfNeeded()

    
    def OnEnd(self, warmgr):
        if self.GetDamageBackType() > 0:
            pass
        self.OnDamagebackEnd(warmgr)

    
    def CalNeedGoBackEnemy(self):
        '''\xadp\xba\xe2\xb4_\xac\xa1\xa1A \xc2k\xa6\xec\xabO\xa9\xb3\xaa\xba\xc5\xde\xbf\xe8
\t\t'''
        import world
        if self.m_SkillID not in (2107, 2119, 1711, 1716):
            return None
        
        for iTargetID in self.m_EnemyList:
            
            try:
                oObj = world.GetObj(iTargetID)
                if not oObj:
                    continue
                
                if oObj.IsSuperPosition(oObj.m_OrigX, oObj.m_OrigY):
                    continue
                
                if oObj.m_HPChg < 0 and oObj.m_State == 'die':
                    self.m_lNeedGoBack.append(iTargetID)
            continue
            continue

        

    
    def NewSkillFuhuoGoBackIfNeeded(self):
        if not self.m_lNeedGoBack:
            return None
        
        for iTargetID in self.m_lNeedGoBack:
            e_warinterface.GoBack(self.m_SkillID, iTargetID, 15, True)
