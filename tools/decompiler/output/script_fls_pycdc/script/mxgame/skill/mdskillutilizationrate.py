# pycdc 交叉复核产物 · script.fls entry 314
# co_filename(原始)='script/mxgame/skill/mdskillutilizationrate.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_314.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/8/27 16:47
\xd7\xf7\xd5\xdf: gesaferoc
\xce\xc4\xbc\xfe: mdskillutilizationrate
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import slot
g_oSkillUtilizationRate = None

def ModuleReset():
    global g_oSkillUtilizationRate
    g_oSkillUtilizationRate = None


def GetSkillUtilizationRate():
    ''':rtype: CSkillUtilizationRate'''
    global g_oSkillUtilizationRate
    if not g_oSkillUtilizationRate:
        g_oSkillUtilizationRate = CSkillUtilizationRate()
    
    return g_oSkillUtilizationRate


class CSkillUtilizationRate(slot.ISignalSubject):
    SS_UpdateSkillUtilizationRate = 'OnUpdateSkillUtilizationRate(dSkillUtilizationRate)'
    
    def __init__(self):
        self.\xf0\xf0\xca\xed\xea\xf7()
        self.m_dSkillUtilizationRate = 0

    
    def SetSkillUtilizationRate(self, dSkillUtilizationRate):
        self.m_dSkillUtilizationRate = dSkillUtilizationRate
        self.ssEmit(self.SS_UpdateSkillUtilizationRate, dSkillUtilizationRate)

    
    def GetSkillUtilizationRate(self):
        return self.m_dSkillUtilizationRate

    
    def AskSkillUtilizationRate(self):
        import netblock
        netblock.C2SRequestSkillRate()
