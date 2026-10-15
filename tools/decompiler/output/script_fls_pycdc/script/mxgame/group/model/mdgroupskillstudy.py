# pycdc 交叉复核产物 · script.fls entry 2299
# co_filename(原始)='script/mxgame/group/model/mdgroupskillstudy.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2299.pyc (Python 2.5)

import slot
import skilldata
g_GroupSkillStudy = None

def ModuleReset():
    global g_GroupSkillStudy
    g_GroupSkillStudy = None


def GetModel():
    global g_GroupSkillStudy
    if not g_GroupSkillStudy:
        g_GroupSkillStudy = CGroupSkillStudyMgr()
    
    return g_GroupSkillStudy


class CGroupSkillStudyMgr(slot.ISignalSubject):
    YYkibsjcYY = __name__
    SS_ChangeSkillExp = 'SS_ChangeSkillExp'
    SS_ChangeSkillInfo = 'SS_ChangeSkillInfo'
    SS_ActiveSkill = 'SS_ActiveSkill(iSkillId)'
    
    def __init__(self):
        self.ssInit()
        self.m_iReserveExp = 0
        self.m_lstSkillInfo = []
        self.m_iCurActiveSkillId = 0

    
    def SetSkillReserveExp(self, iExp):
        self.m_iReserveExp = iExp
        self.ssEmit(self.SS_ChangeSkillExp, iExp)

    
    def GetSkillReserveExp(self):
        return self.m_iReserveExp

    
    def SetSkillInfo(self, lstSkillInfo):
        self.m_lstSkillInfo = lstSkillInfo
        self.ssEmit(self.SS_ChangeSkillInfo)

    
    def GetSkillInfo(self):
        lstSkillInfo = []
        for dSkillBaseInfo in self.m_lstSkillInfo:
            dTmpSkillInfo = { }
            iSkillId = dSkillBaseInfo.\x99\x9b\x8a('id', 0)
            dTmpSkillInfo['id'] = iSkillId
            iSkillLv = dSkillBaseInfo.\x99\x9b\x8a('lv')
            dTmpSkillInfo['lv'] = iSkillLv
            iPoint = dSkillBaseInfo.\x99\x9b\x8a('point')
            dTmpSkillInfo['point'] = iPoint
            dData = skilldata.GetData(iSkillId)
            dTmpSkillInfo['desc'] = None if dData else ''
            iSkillLv += 1
            iCost = (iSkillLv ** 3 * 0.3 - iSkillLv ** 2 * 9) + 1200
            if iSkillLv > 70:
                iCost = iCost * ((iSkillLv - 70) * 0.02 + 1)
            
            dTmpSkillInfo['progress'] = '%d/%d' % (iPoint, iCost)
            lstSkillInfo.append(dTmpSkillInfo)
        
        return lstSkillInfo

    
    def UpdateActiveSkill(self, iSkillID):
        self.m_iCurActiveSkillId = iSkillID
        self.ssEmit(self.SS_ActiveSkill, iSkillID)

    
    def GetActiveSkill(self):
        return self.m_iCurActiveSkillId
