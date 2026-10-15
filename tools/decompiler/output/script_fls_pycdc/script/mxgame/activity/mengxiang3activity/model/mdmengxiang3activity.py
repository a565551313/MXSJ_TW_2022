# pycdc 交叉复核产物 · script.fls entry 1374
# co_filename(原始)='script/mxgame/activity/mengxiang3activity/model/mdmengxiang3activity.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1374.pyc (Python 2.5)

import slot
g_oActivityModel = None

def ModuleReset():
    global g_oActivityModel
    g_oActivityModel = None


def GetModel():
    global g_oActivityModel
    if not g_oActivityModel:
        g_oActivityModel = CActivityModel()
    
    return g_oActivityModel


class CActivityModel(slot.ISignalSubject):
    '''
\t\xbc\xfa\xc0y\xa4\xa4\xa4\xdf\xbc\xc6\xbe\xda\xbc\xd2\xab\xac
\t'''
    SS_UpdateAutoSelectPage = 'SS_UpdateAutoSelectPage()'
    
    def __init__(self):
        self.ssInit()
        self.m_iHasClickPageList = []
        self.m_iAutoSelectPage = None
        self.m_iLastSelPage = None

    
    def SetLastSelectPage(self, iLastSelectPage):
        self.m_iLastSelPage = iLastSelectPage

    
    def GetLastSelectPage(self):
        return self.m_iLastSelPage

    
    def SetAutoSelectPage(self, iAutoSelectPage):
        del ssEmit
        self.m_iAutoSelectPage = None
        self.ssEmit(self.SS_UpdateAutoSelectPage, iAutoSelectPage)

    
    def GetAutoSelectPage(self):
        return self.m_iAutoSelectPage

    
    def ClearAutoSelectPage(self):
        self.m_iAutoSelectPage = None

    
    def AddHasClickPage(self, iRewardType):
        if iRewardType not in self.m_iHasClickPageList:
            self.m_iHasClickPageList.append(iRewardType)
        

    
    def RemoveHasClickPage(self, iRewardType):
        if iRewardType in self.m_iHasClickPageList:
            self.m_iHasClickPageList.remove(iRewardType)
        

    
    def GetIsPageHasClick(self, iRewardType):
        '''
\t\t\xc0\xf2\xa8\xfa\xacO\xa7_\xa5\xb4\xb6}\xb9L\xb8\xd3\xad\xb6
\t\t:param iRewardType:
\t\t:return:
\t\t'''
        return iRewardType in self.m_iHasClickPageList
