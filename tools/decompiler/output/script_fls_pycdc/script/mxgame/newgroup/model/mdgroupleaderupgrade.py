# pycdc 交叉复核产物 · script.fls entry 1349
# co_filename(原始)='script/mxgame/newgroup/model/mdgroupleaderupgrade.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1349.pyc (Python 2.5)

import slot
g_MdLeaderUpGrade = None

def ModuleReset():
    global g_MdLeaderUpGrade
    g_MdLeaderUpGrade = None


def GetMd\x91\xb8\xbc\xb9\xb8\xaf\x88\xad\x9a\xaf\xbc\xb9\xb8():
    global g_MdLeaderUpGrade
    if g_MdLeaderUpGrade is None:
        g_MdLeaderUpGrade = CMdGroupLeaderUpGrade()
    
    return g_MdLeaderUpGrade


class CMdGroupLeaderUpGrade(slot.ISignalSubject):
    SS_OnStateChange = 'OnStateChange()'
    
    def __init__(self):
        self.ssInit()
        self.m_dTaskList = []
        self.m_iState = 0

    
    def SetTaskList(self, dList):
        self.m_dTaskList = dList

    
    def GetTaskList(self):
        return self.m_dTaskList

    
    def SetState(self, iState):
        self.m_iState = iState
        self.ssEmit(self.SS_OnStateChange)

    
    def GetState(self):
        return self.m_iState
