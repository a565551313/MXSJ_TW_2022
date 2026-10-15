# pycdc 交叉复核产物 · script.fls entry 1958
# co_filename(原始)='script/dialog/mubanhao/model/mgrmubanhao.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1958.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/12 16:16
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: mgrmubanhao
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import slot
import newappearancebtndata
import mubanhaodata
g_oMubanhaoMgr = None

def ModuleReset():
    global g_oMubanhaoMgr
    g_oMubanhaoMgr = None


def GetMubanhaoMgr():
    ''':rtype: CMubanhaoMgr'''
    global g_oMubanhaoMgr
    if not g_oMubanhaoMgr:
        g_oMubanhaoMgr = CMubanhaoMgr()
    
    return g_oMubanhaoMgr


class CMubanhaoMgr(slot.ISignalSubject):
    
    def __init__(self):
        self.ssInit()
        self.m_sSelectMainBtnName = mubanhaodata.GetNameData()[0]
        self.m_iSelPage = mubanhaodata.GetFirstBtnMsg(self.m_sSelectMainBtnName)
        self.m_iLastPage = 1

    
    def GetMainBtnName(self):
        return self.m_sSelectMainBtnName

    
    def SetMainBtnName(self, sName):
        self.m_sSelectMainBtnName = sName

    
    def GetSelPage(self):
        return self.m_iSelPage

    
    def SetSelPage(self, iPage):
        continue
        iPage.m_iSelPage = None

    
    def SetLastPage(self, iPage):
        self.m_iLastPage = iPage

    
    def GetLastPage(self):
        return self.m_iLastPage
