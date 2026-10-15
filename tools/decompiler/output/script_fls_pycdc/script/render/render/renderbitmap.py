# pycdc 交叉复核产物 · script.fls entry 3889
# co_filename(原始)='script/render/render/renderbitmap.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3889.pyc (Python 2.5)

import interface
import ui
import misc
import rendertask
import cctexture2d
g_ObjectDict = { }

def Start():
    import main
    main.CModuleLoop.AddLoop(__name__, 'Loop')


def Loop():
    for shadow in g_ObjectDict.values():
        obj = shadow()
        if obj:
            obj.OnTimeoutCheck()
            continue
    


def OnRenderDone(sTaskID, iSuccess, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
    shadow = g_ObjectDict.get(sTaskID)
    if shadow:
        obj = shadow()
        if obj:
            if iSuccess:
                obj.SetPixels(iBytePerPixel, sPixelData, iWidth, iHeight, extends)
                return None
            
            obj.OnRenderFail()
        else:
            del g_ObjectDict[sTaskID]
    
    rendertask.Del(sTaskID)


def OnRenderReconnect():
    lst = []
    del_lst = []
    for sTaskID, shadow in g_ObjectDict.iteritems():
        obj = shadow()
        if obj:
            lst.append(obj)
            continue
        del_lst.append(sTaskID)
    
    for sTaskID in del_lst:
        del g_ObjectDict[sTaskID]
    
    if lst:
        for obj in lst:
            obj.OnRenderReconnect()
        
    


def OnRenderResult(obj, bSuccess, sFileName, sPackage, oResizeCB):
    if not bSuccess:
        obj.OnRenderFail()
        obj.LoadLocalImage(sFileName, sPackage, 0, 0)
    
    if oResizeCB:
        oResizeCB(bSuccess)
    


def OnDefaultImage(obj, sFileName, sPackage):
    if not obj.IsReady():
        obj.LoadLocalImage(sFileName, sPackage, 0, 0)
    


def CreateRenderBitmap(oParent, sFileName, sPackage, sDefFileName, sDefPackage, oResizeCB = None):
    img = CRenderBitmapObject(oParent)
    if img.Load(sFileName, sPackage):
        if callable(oResizeCB):
            oResizeCB = misc.Functor(oResizeCB)
        
        img.SetStateCallback(300, OnRenderResult, sDefFileName, sDefPackage, oResizeCB)
        img.CreatePyCommand(6, OnDefaultImage, sDefFileName, sDefPackage)
    else:
        img.LoadLocalImage(sDefFileName, sDefPackage, 0, 0)
    return img


class CRenderBitmapObject(interface.CContainerObject):
    
    def __init__(self, parent):
        interface.CContainerObject.__init__(self, parent)
        self.m_Bitmap = None
        self.m_IsLocalImage = False
        (self.m_Width, self.m_Height) = (0, 0)
        self.m_FixSize = None
        self.m_TaskID = None
        self.m_Filename = None
        self.m_Package = None
        self.m_Timeout = 0
        self.m_TimeoutStep = 0
        self.m_StateCallback = None
        self.m_IsAnim3 = False
        self.m_KeyPos = (0, 0)

    
    def Load(self, sFileName, sPackage):
        self.m_IsLocalImage = False
        self.m_Bitmap = None
        self.DelTask()
        self.CreateTask(sFileName, sPackage)
        self.m_IsAnim3 = sFileName.endswith('.ani3')
        return self.m_TaskID

    
    def LoadLocalImage(self, filename, package, x, y):
        self.m_IsLocalImage = True
        self.m_Bitmap = ui.CImage(self, filename, package)
        self.m_Bitmap.SetPos(x, y)
        (self.m_Width, self.m_Height) = self.m_Bitmap.GetSize()

    
    def SetStateCallback(self, timeout, callback, *args, **kwargs):
        self.m_Timeout = timeout
        self.m_TimeoutStep = 0
        self.m_StateCallback = misc.Functor(callback, *args, **kwargs)
        self.m_StateCallback.SetIsPrioriyCallArg(True)

    
    def GetSize(self):
        return (self.m_Width, self.m_Height)

    
    def SetFixSize(self, w, h):
        self.m_FixSize = (w, h)

    
    def GetFixSize(self):
        if self.m_FixSize:
            return self.m_FixSize
        else:
            return self.GetSize()

    
    def IsReady(self):
        return self.m_Bitmap is not None

    
    def IsAnim3(self):
        return self.m_IsAnim3

    
    def SetKeyPos(self, kx, ky):
        self.m_KeyPos = (kx, ky)
        for None in None:
            return None

    
    def GetKeyPos(self):
        return self.m_KeyPos

    
    def DoStateCallback(self, bSuccess):
        if self.m_StateCallback:
            callback = self.m_StateCallback
            self.m_StateCallback = None
            callback(self, bSuccess)
        
        self.m_Timeout = 0
        self.m_TimeoutStep = 0

    
    def OnRenderFail(self):
        self.m_Bitmap = None
        (self.m_Width, self.m_Height) = (0, 0)
        self.m_Filename = None
        self.m_Package = None
        self.DelTask()
        self.DoStateCallback(False)

    
    def OnRenderReconnect(self):
        if self.m_Filename and self.m_Package:
            self.DelTask()
            self.CreateTask(self.m_Filename, self.m_Package)
        

    
    def OnTimeoutCheck(self):
        if self.m_Timeout > 0:
            if self.m_TimeoutStep < self.m_Timeout:
                self.m_TimeoutStep += 1
            else:
                self.m_Timeout = 0
                self.m_TimeoutStep = 0
                self.DoStateCallback(False)
        

    
    def __del__(self):
        self.DelTask()

    
    def DelTask(self):
        if self.m_TaskID:
            sTaskID = self.m_TaskID
            self.m_TaskID = None
            if sTaskID in g_ObjectDict:
                del g_ObjectDict[sTaskID]
            
            rendertask.Del(sTaskID)
        

    
    def CreateTask(self, sFileName, sPackage):
        self.m_TaskID = rendertask.AddSimple(rendertask.TYPE_IMAGE, sFileName, sPackage)
        if self.m_TaskID:
            self.m_Filename = sFileName
            self.m_Package = sPackage
            g_ObjectDict[self.m_TaskID] = misc.WeakRef(self)
        

    
    def SetPixels(self, iBytePerPixel, sPixelData, iWidth, iHeight, extends):
        self.m_TimeoutStep = 0
        if self.m_IsLocalImage:
            self.m_IsLocalImage = False
            self.m_Bitmap = None
            (self.m_Width, self.m_Height) = (0, 0)
        
        
        try:
            if self.m_Bitmap:
                self.m_Bitmap.SetPixels(iWidth, iHeight, sPixelData, cctexture2d.RGBA8888)
            else:
                self.m_Bitmap = interface.CBitmapObject.CreateFromPixels(self, iWidth, iHeight, sPixelData, cctexture2d.RGBA8888)
        except ValueError:
            e = None
            LOG_DEBUG(e)
            self.OnRenderFail()
            return None

        (kx, ky) = self.m_KeyPos
        self.m_Width = iWidth
        self.m_Height = iHeight
        if self.IsAnim3() and extends:
            (x, y) = extends
            kx -= x
            ky -= y
        
        self.m_Bitmap.SetPos(kx, ky)
        self.DoStateCallback(True)
