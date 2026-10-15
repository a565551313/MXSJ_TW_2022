# pycdc 交叉复核产物 · script.fls entry 1297
# co_filename(原始)='script/mxgame/item/model/mditemguide.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1297.pyc (Python 2.5)

import slot
import netcommon
g_ItemGuideMgr = None

def ModuleReset():
    GetItemGuideMgr().Clear()


def GetItemGuideMgr():
    ''':rtype: CItemGuideMgr'''
    global g_ItemGuideMgr
    if not g_ItemGuideMgr:
        g_ItemGuideMgr = CItemGuideMgr()
    
    return g_ItemGuideMgr


class CItemGuideMgr(slot.ISignalSubject):
    SS_UpdateIsOpenWarehouse = 'UpdateIsOpenWarehouse(bIsOpenWarehouse)'
    
    def __init__(self):
        self.ssInit()
        self.m_bIsOpenWarehouse = False
        self.m_bIsAskMark = False
        self.m_bIsReceiveMark = False

    
    def AskIsOpenWarehouse(self):
        if self.m_bIsReceiveMark or self.m_bIsAskMark:
            return None
        else:
            self.m_bIsAskMark = True
            netcommon.C2SAskIsOpenWarehouse()

    
    def SetIsOpenWarehouse(self, bIsOpenWarehouse):
        self.m_bIsReceiveMark = True
        if self.m_bIsOpenWarehouse == bIsOpenWarehouse:
            return None
        
        self.m_bIsOpenWarehouse = bIsOpenWarehouse
        self.EmitIsOpenWarehouse(bIsOpenWarehouse)

    
    def GetIsOpenWarehouse(self):
        if self.m_bIsReceiveMark:
            return self.m_bIsOpenWarehouse
        else:
            self.AskIsOpenWarehouse()
            return True

    
    def Clear(self):
        self.m_bIsOpenWarehouse = False
        self.m_bIsAskMark = False
        self.m_bIsReceiveMark = False

    
    def EmitIsOpenWarehouse(self, bIsOpenWarehouse):
        self.ssEmit(self.SS_UpdateIsOpenWarehouse, bIsOpenWarehouse)


print 
# WARNING: Decompyle incomplete
