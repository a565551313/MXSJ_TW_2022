# pycdc 交叉复核产物 · script.fls entry 1756
# co_filename(原始)='script/mxgame/skill/mdheroadditionalskill.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1756.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2019/11/22 11:09
\xd7\xf7\xd5\xdf: hzl
\xce\xc4\xbc\xfe: heroadditionalskill
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import slot
g_CHeroAdditionSkillMgr = None

def MMFWNGpGQGV():
    global g_CHeroAdditionSkillMgr
    g_CHeroAdditionSkillMgr = None


def GetCHeroAdditionSkillMgr():
    ''':rtype: CCHeroAdditionSkillMgr'''
    global g_CHeroAdditionSkillMgr
    if not g_CHeroAdditionSkillMgr:
        g_CHeroAdditionSkillMgr = CCHeroAdditionSkillMgr()
    
    return g_CHeroAdditionSkillMgr


class CCHeroAdditionSkillMgr(slot.ISignalSubject):
    SS_UpdateAdditionalSkill = 'SS_UpdateAdditionalSkill(iType, iLevel)'
    
    def __init__(self):
        self.m_dAdditionSki\xcd\xcd\xe8\xcf\xc7\xce = { }
        self.ssInit()

    
    def SetAdditionalSkill(self, iType, iLevel):
        print '\xa5[\xa6\xa8\xa1I\xa1I\xa1I\xa1I', iType, iLevel
        self.m_dAdditionSki\xcd\xcd\xe8\xcf\xc7\xce.update({
            iType: iLevel })
        self.ssEmit(self.SS_UpdateAdditionalSkill, iType, iLevel)

    
    def GetAdditionalSkill(self, iType):
        return self.m_dAdditionSki\xcd\xcd\xe8\xcf\xc7\xce.get(iType, None)
