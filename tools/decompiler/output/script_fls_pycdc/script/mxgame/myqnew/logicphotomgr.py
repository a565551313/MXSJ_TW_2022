# pycdc 交叉复核产物 · script.fls entry 250
# co_filename(原始)='script/mxgame/myqnew/logicphotomgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_250.pyc (Python 2.5)

import slot
import misc
g_oLoadPhotoMgr = None

def ModuleReset():
    global g_oLoadPhotoMgr
    g_oLoadPhotoMgr = None


def GetPhotoLoader():
    global g_oLoadPhotoMgr
    if not g_oLoadPhotoMgr:
        g_oLoadPhotoMgr = CLogicLoadPhotoMgr()
    
    return g_oLoadPhotoMgr


class CLogicLoadPhotoMgr(slot.ISignalSubject):
    SS_LoadPhotoSuccess = 'LoadPhotoSuccess'
    
    def __init__(self):
        self.ssInit()
        self.m_dPhotoUrl = { }
        self.m_oTimer = None

    StartDownLoadPhoto = None(**        import newmyqbase
        tKey = (sUrl, iType)
        if tKey not in self.m_dPhotoUrl:
            oPhotoUrlObj = newmyqbase.CPhotoBase()
            oPhotoUrlObj.SetPhotoUrl(sUrl)
            oPhotoUrlObj.SetFinishCallBack(misc.Functor(self.OnDownLoadUrlFinishded, tKey))
            oPhotoUrlObj.RefreshPhoto(iType)
            self.m_dPhotoUrl[tKey] = oPhotoUrlObj
        else:
            oPhotoUrlObj = self.m_dPhotoUrl[tKey]
            oPhotoUrlObj.RefreshPhoto(iType)
)
    
    def RemovePhotoUrl(self, sUrl, iType):
        tKey = (sUrl, iType)
        if tKey in self.m_dPhotoUrl:
            del self.m_dPhotoUrl[tKey]
        

    
    def Clear(self):
        self.m_dPhotoUrl = { }

    
    def OnDownLoadUrlFinishded(self, tKey, sKey, tPath, bSuc, iType):
        self.ssEmit(self.SS_LoadPhotoSuccess, tKey, sKey, tPath, bSuc, iType)
