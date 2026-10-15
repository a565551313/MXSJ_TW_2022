# pycdc 交叉复核产物 · script.fls entry 2064
# co_filename(原始)='script/pubscript/pubguard/scanprocessinterface.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2064.pyc (Python 2.5)

'''
\xce\xc4\xbc\xfe\xb9\xa6\xc4\xdc\xc3\xe8\xca\xf6:EP\xcf\xee\xc4\xbfGuard\xb9\xa4\xb3\xcc\xc9\xa8\xc3\xe8\xd6\xb8\xb6\xa8\xbd\xf8\xb3\xcc\xc4\xa3\xbf\xe9
\xb8\xba\xd4\xf0\xd2\xda:wuyunpeng
'''
import \xf5\xe4\xe6ket
from p_interface import CallCxx, RegisterCxxCallback
from protocolsetting import g_ProtocolSetting as Protocol

class PyScanProcessInterface(object):
    
    def __init__(self):
        super(PyScanProcessInterface, self).__init__()
        RegisterCxxCallback(Protocol.Protocol_StartScanProcess, self._OnScanPluginCallback)
        self.OnScanPluginCallback = None

    
    def StartScanProcess(self, resultCallback = None, timeInterval = 5000):
        self.OnScanPluginCallback = resultCallback
        pack = \xf5\xe4\xe6ket.PacketW()
        pack.PackDWord(Protocol.Protocol_StartScanProcess)
        pack.PackDWord(timeInterval)
        CallCxx(Protocol.Protocol_StartScanProcess, pack.GetBuffer())

    
    def StopScanProcess(self):
        CallCxx(Protocol.Protocol_StopScanProcess, None)

    
    def AddSuspiciousProcess(self, suspiciousProcessName):
        pack = \xf5\xe4\xe6ket.PacketW()
        pack.PackStringW(suspiciousProcessName)
        CallCxx(Protocol.Protocol_AddSuspiciousProcess, pack.GetBuffer())

    
    def RemoveSuspiciousProcess(self, suspiciousProcessName):
        pack = \xf5\xe4\xe6ket.PacketW()
        pack.PackStringW(suspiciousProcessName)
        CallCxx(Protocol.Protocol_RemoveSuspiciousProcess, pack.GetBuffer())

    
    def AddSuspiciousDll(self, suspiciousDllName):
        pack = \xf5\xe4\xe6ket.PacketW()
        pack.PackStringW(suspiciousDllName)
        CallCxx(Protocol.Protocol_AddSuspiciousDll, pack.GetBuffer())

    
    def RemoveSuspiciousDll(self, suspiciousDllName):
        pack = \xf5\xe4\xe6ket.PacketW()
        pack.PackStringW(suspiciousDllName)
        CallCxx(Protocol.Protocol_RemoveSuspiciousDll, pack.GetBuffer())

    
    def _OnScanPluginCallback(self, arg):
        readPackObj = \xf5\xe4\xe6ket.PacketR(arg)
        Numbers = readPackObj.UnpackDWord()
        BehaviorType = readPackObj.UnpackWord()
        resultPack = { }
        if BehaviorType == 0:
            for i in range(Numbers):
                resultSubPack = { }
                processNumbers = readPackObj.UnpackWord()
                for j in range(processNumbers):
                    processName = readPackObj.UnpackStringW()
                    processPid = readPackObj.UnpackWord()
                    resultSubPack[j] = {
                        u'ProcessName': processName,
                        u'Pid': processPid }
                
                resultPack[i] = resultSubPack
            
        elif BehaviorType == 1:
            for i in range(Numbers):
                dllName = readPackObj.UnpackStringW()
                processNumbers = readPackObj.UnpackWord()
                dllInfo = { }
                for j in range(processNumbers):
                    processName = readPackObj.UnpackStringW()
                    dllPath = readPackObj.UnpackStringW()
                    processPid = readPackObj.UnpackWord()
                    dllInfo[j] = {
                        u'ProcessName': processName,
                        u'ModulePath': dllPath,
                        u'Pid': processPid }
                    resultPack[dllName] = dllInfo
                
            
        
        if self.OnScanPluginCallback != None:
            self.OnScanPluginCallback(BehaviorType, resultPack)
