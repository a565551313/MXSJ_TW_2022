# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\render\rendertask.py
from renderprotocol import *
import C_object, C_sys, wrapobject, renderagent
g_Type2Task = {}
g_TaskID2Type = {}
g_TaskIDSeed = 1

def GetTask(iType):
    global g_Type2Task
    return g_Type2Task.get(iType, g_Type2Task[0])


class CRenderTask(object):

    def __init__(self, iType):
        self.m_Type = iType
        g_Type2Task[iType] = self

    def GetType(self):
        return self.m_Type

    def ProcessR2CAdd(self, sClientID, sTaskID, *args):
        return self.GetRenderData(sClientID, sTaskID, *args)

    def GetRenderData(self, sClientID, sTaskID, *args):
        raise NotImplementedError('渲染端-执行解包和生成渲染对象、宽高、扩展信息并予以返回，若出错则返回None')

    def OnC2RDel(self, sClientID, sTaskID):
        import renderagent
        renderagent.DelRenderObj(sClientID, sTaskID)


class CAvatarTask(CRenderTask):

    def GetRenderData(self, sClientID, sTaskID, iWidth, iHeight, sPack, *sPathList):
        dTaskInfo = renderagent.GetRenderTaskInfo(sTaskID)
        if dTaskInfo:
            oNode = dTaskInfo['obj']
            if oNode and isinstance(oNode, wrapobject.CAvatar):
                oNode.Refresh(sPathList, sPack, iWidth, iHeight)
            else:
                oNode = wrapobject.CAvatar(None, sPathList, sPack, iWidth, iHeight)
        else:
            oNode = wrapobject.CAvatar(None, sPathList, sPack, iWidth, iHeight)
        n = oNode.GetCocosNode()
        n.SetCameraMask(2, bitwise=True, recursive=True)
        return (
         oNode, iWidth, iHeight, [])


class CImageTask(CRenderTask):

    def GetRenderData(self, sClientID, sTaskID, sFileName, sPackage):
        import os
        extends = []
        try:
            sFileName = C_sys.GBK_to_UTF8(sFileName)
            sPackage = C_sys.GBK_to_UTF8(sPackage)
            if sFileName.endswith('.igs'):
                obj = C_object.CImagesObject(None, sFileName, sPackage)
                width, height = obj.GetResSize()
            elif sFileName.endswith('.spr'):
                obj = C_object.CSpriteObject(None, sFileName, sPackage)
                obj.CreateCommand(1, 'animation')
                width, height = obj.GetResSize()
            elif sFileName.endswith('.png') or sFileName.endswith('.jpg'):
                obj = C_object.CBitmapObject(None, sFileName, sPackage)
                width, height = obj.GetSize()
            elif sFileName.endswith('.plist'):
                sRealPath = os.path.join(sPackage, sFileName).replace('\\', '/')
                obj = wrapobject.CSpine(None, sRealPath[:-6], -1, -1)
                width, height = obj.GetSize()
            elif sFileName.endswith('.avatar'):
                sRealPath = os.path.join(sPackage, sFileName).replace('\\', '/')
                obj = wrapobject.CSpine(None, sRealPath[:-7], 140, 200)
                width, height = obj.GetSize()
            else:
                raise NotImplementedError('未知的文件后缀名称')
        except Exception as e:
            NormalLog('%s Error:(%s, %s) %s' % (self.__class__.__name__, sFileName, sPackage, e))
            return

        node = obj.GetCocosNode()
        node.SetCameraMask(2, bitwise=True, recursive=True)
        return (
         obj, width, height, extends)


_ = CRenderTask(0)
_ = CAvatarTask(TYPE_AVATAR)
_ = CImageTask(TYPE_IMAGE)

def ProcessC2RAdd(sClientID, iType, sTaskID, *args):
    rtobj = GetTask(iType)
    result_lst = rtobj.ProcessR2CAdd(sClientID, sTaskID, *args)
    import renderagent
    if result_lst:
        renderagent.AddRenderObj(sClientID, sTaskID, *result_lst)
    else:
        import netrender
        agent = renderagent.GetRenderAgent()
        netrender.R2CDoneRenderTask(agent, sClientID, 0, sTaskID, 0, '', 0, 0, [])
