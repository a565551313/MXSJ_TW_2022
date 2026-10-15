# pycdc 交叉复核产物 · script.fls entry 796
# co_filename(原始)='script/render/render/rendertask.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_796.pyc (Python 2.5)

from renderprotocol import *
from netrender import TaskAdd, TaskUnpack
from clientagent import GetClientAgent
g_Type2Task = { }
g_TaskID2Type = { }
g_TaskIDSeed = 1
g_TempRequestDict = { }

def Add(iType, sTaskID, *args):
    if AddRenderTask(iType, sTaskID, *args):
        g_TaskID2Type[sTaskID] = iType
        return True
    
    return False


def AddSimple(iType, *args):
    global g_TaskIDSeed
    import os
    sTaskID = '%d-%d' % (os.getpid(), g_TaskIDSeed)
    if Add(iType, sTaskID, *args):
        g_TaskIDSeed += 1
        return sTaskID
    


def Del(sTaskID):
    if sTaskID in g_TaskID2Type:
        iType = g_TaskID2Type.pop(sTaskID)
        return DelRenderTask(iType, sTaskID)
    
    return False


def GetTask(iType):
    return g_Type2Task.get(iType, g_Type2Task[0])


def OnR2CDone(sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
    if sTaskID in g_TaskID2Type:
        iType = g_TaskID2Type[sTaskID]
        rtobj = GetTask(iType)
        rtobj.OnR2CDone(sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends)
    


class CRenderTask(object):
    
    def __init__(self, iType):
        self.m_Type = iType
        g_Type2Task[iType] = self

    
    def GetType(self):
        return self.m_Type

    
    def \xb6ǧ\xb4\x91\x91(self, clientAgent, *args):
        TaskAdd(clientAgent, *args)

    
    def OnR2CDone(self, sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
        raise NotImplementedError('\xc5\xde\xbf\xe8\xba\xdd-\xb0\xf5\xa6\xe6\xb4\xe8\xacV\xa5\xf4\xb0\xc8\xa7\xb9\xa6\xa8\xaa\xba\xb1\xb5\xa6\xac\xb3B\xb2z')



class CAvatarTask(CRenderTask):
    
    def OnR2CDone(self, sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
        import renderavatar
        renderavatar.OnRenderDone(sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends)



class CImageTask(CRenderTask):
    
    def OnR2CDone(self, sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
        import renderbitmap
        renderbitmap.OnRenderDone(sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends)


_ = CRenderTask(0)
_ = CAvatarTask(TYPE_AVATAR)
_ = CImageTask(TYPE_IMAGE)

def AddRenderTask(iType, sTaskID, *args):
    clientAgent = GetClientAgent()
    if clientAgent:
        if clientAgent.IsReady():
            clientAgent.TaskPrepare(PR_C2R_ADD_RENDER_TASK)
            TaskAdd(clientAgent, iType, sTaskID)
            GetTask(iType).\xb6ǧ\xb4\x91\x91(clientAgent, *args)
            return clientAgent.TaskSend(SHAREUTIL_3D_RENDERER_NAME)
        else:
            PushRequest(sTaskID, iType, *args)
            return True
    
    return False


def DelRenderTask(iType, sTaskID):
    clientAgent = GetClientAgent()
    if clientAgent:
        if clientAgent.IsReady():
            clientAgent.TaskPrepare(PR_C2R_DEL_RENDER_TASK)
            TaskAdd(clientAgent, iType, sTaskID)
            return clientAgent.TaskSend(SHAREUTIL_3D_RENDERER_NAME)
        else:
            PopRequest(sTaskID)
            return True
    
    return False


def PushRequest(sTaskID, iType, *args):
    g_TempRequestDict[sTaskID] = (iType, args)


def PopRequest(sTaskID):
    if sTaskID in g_TempRequestDict:
        g_TempRequestDict.pop(sTaskID)
    


def ProcessTempRequest():
    global g_TempRequestDict
    dct = g_TempRequestDict
    g_TempRequestDict = { }
    for iType, args in dct.items():
        Add(iType, sTaskID, *args)
