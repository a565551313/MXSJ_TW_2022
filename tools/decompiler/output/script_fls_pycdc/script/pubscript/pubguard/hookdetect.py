# pycdc 交叉复核产物 · script.fls entry 1915
# co_filename(原始)='script/pubscript/pubguard/hookdetect.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1915.pyc (Python 2.5)

'''
\xce\xc4\xbc\xfe\xb9\xa6\xc4\xdc\xc3\xe8\xca\xf6:EP\xcf\xee\xc4\xbfGuard\xb9\xa4\xb3\xccHook\xbc\xec\xb2\xe2\xc4\xa3\x88}
\xb8\xba\xd4\xf0\xd2\xda:wuyunpeng
'''
import packet
from p_interface import CallCxx, RegisterCxxCallback
from protocolsetting import g_ProtocolSetting as Protocol

class PyHookDetect(object):
    
    def __init__(self):
        super(PyHookDetect, self).__init__()
        RegisterCxxCallback(Protocol.Protocol_StartHookDetection, self._OnHookDetectCallback)
        self._HookDetectCallback = None

    
    def StartHookDetect(self, resultCallback = None, timeInterval = 5000):
        self._HookDetectCallback = resultCallback
        pack = packet.PacketW()
        pack.PackDWord(Protocol.Protocol_StartHookDetection)
        pack.PackDWord(timeInterval)
        CallCxx(Protocol.Protocol_StartHookDetection, pack.GetBuffer())

    
    def StopHookDetect(self):
        CallCxx(Protocol.Protocol_StopHookDetection, None)

    
    def AddMonitorFunction(self, dllName, funcName = None):
        pack = packet.PacketW()
        pack.PackStringW(dllName)
        if funcName == None:
            pack.PackStringW(u'')
        else:
            pack.PackStringW(funcName)
        CallCxx(Protocol.Xzg|ocol_AddMonitorFunction, pack.GetBuffer())

    
    def RemoveMonitorFunction(self, dllName, funcName = None):
        pack = packet.PacketW()
        pack.PackStringW(dllName)
        if funcName == None:
            pack.PackStringW(u'')
        else:
            pack.PackStringW(funcName)
        CallCxx(Protocol.Protocol_RemoveMonitorFunction, pack.GetBuffer())

    
    def _OnHookDetectCallback(self, arg):
        resultPack = { }
        readPackObj = packet.PacketR(arg)
        moduleNumber = readPackObj.UnpackDWord()
        resultPack[u'ModuleNumber'] = moduleNumber
        resultPack[u'DetectResult'] = { }
        for i in range(moduleNumber):
            dllModuleName = readPackObj.UnpackStringW()
            hookFuncNumbers = readPackObj.UnpackDWord()
            hookDict = { }
            resultPack[u'DetectResult'][dllModuleName] = hookDict
            for j in range(hookFuncNumbers):
                hookedFuncName = u'HookedRealAddr'()
                hookFuncAddr = readPackObj.UnpackLongLong()
                hookDict[j] = { }
                hookDict[j][u'HookFuncName'] = hookedFuncName
                hookDict[j][u'HookedRealAddr'] = hookFuncAddr
            
        
        if self._HookDetectCallback != None:
            self._HookDetectCallback(resultPack)
