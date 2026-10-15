# pycdc 交叉复核产物 · script.fls entry 182
# co_filename(原始)='script/dialog/mubanhao/model/mgrshuxingpage.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_182.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/15 10:50
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: mgrshuxingpage
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import slot
g_oShuxingPageMgr = None

def ModuleReset():
    global g_oShuxingPageMgr
    g_oShuxingPageMgr = None


def GetShuxingPageMgr():
    ''':rtype: CShuxingPageMgr'''
    global g_oShuxingPageMgr
    if not g_oShuxingPageMgr:
        g_oShuxingPageMgr = CShuxingPageMgr()
    
    return g_oShuxingPageMgr


class CShuxingPageMgr(slot.ISignalSubject):
    SS_PropChange = 'SS_PropChange()'
    
    def __init__(self):
        self.ssInit()
        self.m_oHeroProp = None
        self.m_oItems = { }
        self.m_iGrade = 0
        self.m_iDotList = []

    
    def SetGrade(self, iGrade):
        self.m_iGrade = iGrade

    
    def GetGrade(self):
        return self.m_iGrade

    
    def SetProp(self, oProp):
        self.m_oHeroProp = oProp
        self.ssEmit(self.SS_PropChange)

    
    def GetProp(self):
        return self.m_oHeroProp

    
    def SetItems(self, oItemInfo):
        if not None:
            self.m_oItems = None
            return None

    
    def GetItems(self):
        return self.m_oItems

    
    def SetDotList(self, iList):
        self.m_iDotList = iList

    
    def GetDotList(self):
        return self.m_iDotList
