# pycdc 交叉复核产物 · script.fls entry 1592
# co_filename(原始)='script/mxgame/group/model/mdgroupcreate.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1592.pyc (Python 2.5)

'''
Author huyuhong01
Create Time 2018/12/20
\xb0\xef\xc5\xc9\xb4\xb4\xbd\xa8\xbd\xe7\xc3\xe6\xb5\xc4\xca\xfd\xbe\xdd\xb4\xe6\xb7\xc5
'''
g_oGroupCreateModel = None

def ModuleReset():
    global g_oGroupCreateModel
    g_oGroupCreateModel = None


def GetModel():
    global g_oGroupCreateModel
    if not g_oGroupCreateModel:
        g_oGroupCreateModel = CGroupCreateModel()
    
    return g_oGroupCreateModel


def Clear():
    global g_oGroupCreateModel
    g_oGroupCreateModel = None


class CGroupCreateModel(object):
    
    def __init__(self):
        self.m_iDeputeNeed = 0
        self.m_iCoinNeed = 0
        self.m_bShowNotice = False

    
    def SetDeputeNeed(self, iDeputeNeed):
        self.m_iDeputeNeed = iDeputeNeed

    
    def SetCoinNeed(self, iCoinNeed):
        self.m_iCoinNeed = iCoinNeed

    
    def GetDeputeNeed(self):
        return self.m_iDeputeNeed

    
    def GetCoinNeed(self):
        return self.m_iCoinNeed

    
    def SetNotice(self, \xd6\xe7\xdc\xdb\xc3):
        self.m_bShowNotice = \xd6\xe7\xdc\xdb\xc3

    
    def GetShowNotice(self):
        return self.m_bShowNotice
