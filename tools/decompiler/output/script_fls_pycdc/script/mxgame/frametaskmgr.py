# pycdc 交叉复核产物 · script.fls entry 247
# co_filename(原始)='script/mxgame/frametaskmgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_247.pyc (Python 2.5)

'''
frametaskmgr.py
create by xian90 2019/12/11 11:29
\xc4\xa3\xbf\xe9\xb9\xa6\xc4\xdc\xcb\xb5\xc3\xf7:
'''
import time
from collections import deque
import types
import timer
import misc
g_oFrameTaskMgr = None

def ModuleReset():
    if g_oFrameTaskMgr:
        g_oFrameTaskMgr.Destroy()
    


def GetFrameTaskMgr():
    global g_oFrameTaskMgr
    if not g_oFrameTaskMgr:
        g_oFrameTaskMgr = CFrameTaskMgr()
    
    return g_oFrameTaskMgr


class CFrameTaskMgr(object):
    IMPORT_MODULE_NUM_PER_FRAME = 1
    
    def __init__(self):
        super(CFrameTaskMgr, self).__init__()
        self.m_bLoading = False
        self.m_oFrameTimer = None
        self.m_oDelayTimer = None
        self.m_oAfterLoadingTimer = None
        self.m_oDelayTaskList = []
        self.m_oAfterLoadingTaskList = []
        self.m_oPreImportModuleList = deque()

    
    def SetIsLoading(self, bFlag):
        self.m_bLoading = bFlag

    
    def AddImportModuleTask(self, oModoleNameList):
        self.m_oPreImportModuleList.extend(oModoleNameList)
        self.StartFrameTimer()

    
    def StartFrameTimer(self):
        if not self.m_oFrameTimer:
            self.m_oFrameTimer = timer.Timer(0.033, self.FrameLoop, -1, self)
        

    
    def FrameLoop(self):
        if self.m_oPreImportModuleList:
            for i in range(self.IMPORT_MODULE_NUM_PER_FRAME):
                if self.m_oPreImportModuleList:
                    sModuleName = self.m_oPreImportModuleList.popleft()
                    
                    try:
                        __import__(sModuleName)
                    print 'import module failed:', sModuleName

                    continue
            
        else:
            self.ReleaseFrameTimer()

    
    def ReleaseFrameTimer(self):
        if self.m_oFrameTimer:
            self.m_oFrameTimer.Release()
            self.m_oFrameTimer = None
        

    
    def AddDelayTask(self, fDelayTime, oFunc):
        if type(oFunc) is types.MethodType:
            oFunc = misc.Functor(oFunc)
        
        fExecTime = fDelayTime + time.time()
        self.m_oDelayTaskList.append([
            fExecTime,
            oFunc])
        self.m_oDelayTaskList.sort(key = (lambda oData: oData[0]))
        self.StartDelayTimer()

    
    def StartDelayTimer(self):
        if not self.m_oDelayTimer:
            self.m_oDelayTimer = timer.Timer(0.033, self.DoDelayTaskCheck, -1, self)
        

    
    def DoDelayTaskCheck(self):
        if self.m_oDelayTaskList:
            fCurTime = time.time()
            iCount = 0
            for fExecTime, oFunc in self.m_oDelayTaskList:
                if fExecTime > fCurTime:
                    break
                
                iCount += 1
                if oFunc and callable(oFunc):
                    
                    try:
                        oFunc()
                    if isinstance(oFunc, misc.Functor):
                        LOG_EXC('\xb0\xf5\xa6\xe6\xa8\xe7\xbc\xc6------------------------------', oFunc.m_Func)
                    else:
                        LOG_EXC('\xb0\xf5\xa6\xe6\xa8\xe7\xbc\xc6------------------------------', oFunc)

                    continue
                isinstance(oFunc, misc.Functor)
            
            if iCount > 0:
                for i in range(iCount):
                    self.m_oDelayTaskList.pop(0)
                
            
        else:
            self.ReleaseDelayTimer()

    
    def ReleaseDelayTimer(self):
        if self.m_oDelayTimer:
            self.m_oDelayTimer.Release()
            self = None
            None.m_oDelayTimer = None
        

    
    def OnLoadingFinish(self):
        if self.m_oAfterLoadingTaskList:
            self.m_oAfterLoadingTaskList.sort(key = (lambda oData: oData[0]))
        
        self.StartAfterLoadingTimer()

    
    def AddAfterLoadingTask(self, fAfterLoadingTime, oFunc):
        if not self.m_bLoading:
            oFunc()
            return None
        
        if type(oFunc) is types.MethodType:
            oFunc = misc.Functor(oFunc)
        
        self.m_oAfterLoadingTaskList.append([
            fAfterLoadingTime,
            oFunc])

    
    def StartAfterLoadingTimer(self):
        if not self.m_oAfterLoadingTimer:
            if self.m_oAfterLoadingTaskList:
                fAfterLoadingTime = self.m_oAfterLoadingTaskList[0][0]
                self.m_oAfterLoadingTimer = timer.Timer(fAfterLoadingTime, self.DoAfterLoadingTask)
                for oTaskData in self.m_oAfterLoadingTaskList:
                    oTaskData[0] -= fAfterLoadingTime
                
            
        

    
    def DoAfterLoadingTask(self):
        if self.m_oAfterLoadingTaskList:
            fCurTime = time.time()
            iCount = 0
            for fExecTime, oFunc in self.m_oAfterLoadingTaskList:
                if fExecTime > fCurTime:
                    break
                
                if oFunc and callable(oFunc):
                    
                    try:
                        oFunc()
                    if isinstance(oFunc, misc.Functor):
                        LOG_EXC('\xb0\xf5\xa6\xe6\xa8\xe7\xbc\xc6------------------------------', oFunc.m_Func)
                    else:
                        LOG_EXC('\xb0\xf5\xa6\xe6\xa8\xe7\xbc\xc6------------------------------', oFunc)

                    continue
                isinstance(oFunc, misc.Functor)
            
            if iCount > 0:
                for i in range(iCount):
                    self.m_oAfterLoadingTaskList.pop(0)
                
            
        else:
            self.ReleaseAfterLoadingTimer()

    
    def ReleaseAfterLoadingTimer(self):
        if self.m_oAfterLoadingTimer:
            self.m_oAfterLoadingTimer.Release()
            self.m_oAfterLoadingTimer = None
        

    
    def Destroy(self):
        self.ReleaseFrameTimer()
        self.ReleaseDelayTimer()
        self.ReleaseAfterLoadingTimer()
