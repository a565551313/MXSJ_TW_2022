# pycdc 交叉复核产物 · script.fls entry 1171
# co_filename(原始)='script/mxgame/newgroup/model/groupcashview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1171.pyc (Python 2.5)

import slot
import groupcashviewdata
g_mgr = None

def ModuleReset():
    global g_mgr
    g_mgr = None


def GetMgr():
    global g_mgr
    if not g_mgr:
        g_mgr = CGroupCashViewMgr()
    
    return g_mgr


class CGroupCashViewMgr(slot.ISignalSubject):
    SS_GroupCashViewChange = 'SS_GroupCashViewChange'
    
    def __init__(self):
        self.ssInit()
        self.m_lstGroupCashData = []
        self.m_dGroupCashData = { }
        self.SetGroupCashData(0, { }, False)
        self.SetGroupCashData(1, { }, False)

    
    def SetGroupCashData(self, iState, dServData, \xa3\x92\xa4nd = True):
        import copy
        lstLocalData = groupcashviewdata.GetGroupCashDatas()
        lstCashData = []
        for idx, dItemLocalData in enumerate(lstLocalData):
            oData = copy.deepcopy(dItemLocalData)
            sKey = oData.get('getWayID')
            dServValueData = dServData.get(sKey, { })
            oData['cashRate'] = dServValueData.get('cashRate', 0)
            oData['compareRatio'] = dServValueData.get('compareRatio', 0)
            oData['iScore'] = dServValueData.get('iScore', '')
            lstCashData.append(oData)
        
        self.m_dGroupCashData[iState] = lstCashData
        if \xa3\x92\xa4nd:
            self.ssEmit(self.SS_GroupCashViewChange, iState)
        

    
    def GetGroupCashData(self, iState):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xc0\xb0\xac\xa3\xb8\xea\xaa\xf7\xa6C\xaa\xed
\t\t:param iState: 0 \xa5\xbb\xa9P\xbc\xc6\xbe\xda  1\xa4W\xa9P\xbc\xc6\xbe\xda
\t\t:return:
\t\t'''
        return self.m_dGroupCashData.get(iState, [])
