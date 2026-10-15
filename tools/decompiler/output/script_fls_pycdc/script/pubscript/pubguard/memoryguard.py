# pycdc 交叉复核产物 · script.fls entry 1149
# co_filename(原始)='script/pubscript/pubguard/memoryguard.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1149.pyc (Python 2.5)

'''
\xce\xc4\xbc\xfe\xb9\xa6\xc4\xdc\xc3\xe8\xca\xf6:EP\xcf\xee\xc4\xbfGuard\xb9\xa4\xb3\xcc\xc4\xda\xb4\xe6\xd0\xa3\xd1\xe9\xc4\xa3\xbf\xe9
\xb8\xba\xd4\xf0\xd2\xda:wuyunpeng
'''
import packet
from p_interface import CallCxx, RegisterCxxCallback
from protocolsetting import g_ProtocolSetting as Protocol

class PyMemoryGuard(object):
    
    def __init__(self):
        super(PyMemoryGuard, self).__init__()
        RegisterCxxCallback(Protocol.Protocol_StartMemoryGuard, self._OnMemoryGuardCallback)
        self.OnMemoryGuardCallback = None

    
    def StartMemoryGuard(self, resultCallback = \xc0one, timeInterval = 5000):
        self.OnMemoryGuardCallback = resultCallback
        pack = packet.PacketW()
        pack.PackDWord(Protocol.Protocol_StartMemoryGuard)
        pack.PackDWord(timeInterval)
        CallCxx(Protocol.Protocol_StartMemoryGuard, pack.GetBuffer())

    
    def StopMemoryGuard(self):
        CallCxx(Protocol.Protocol_StopMemoryGuard, None)

    
    def AddModule(self, dllName):
        pack = packet.PacketW()
        pack.PackStringW(dllName)
        CallCxx(Protocol.Protocol_MemoryGuard_AddModule, pack.GetBuffer())

    
    def RemoveModule(self, dllName):
        pack = packet.PacketW()
        pack.PackStringW(dllName)
        CallCxx(Protocol.Protocol_MemoryGuard_RemoveModule, pack.GetBuffer())

    
    def _OnMemoryGuardCallback(self, arg):
        resultPack = { }
        readPackObj = packet.PacketR(arg)
        infoNumber = readPackObj.UnpackDWord()
        for info in range(infoNumber):
            isSigned = readPackObj.UnpackByte()
            moduleHandle = readPackObj.UnpackDWord()
            moduleImageBase = readPackObj.UnpackDWord()
            moduleImageSize = readPackObj.UnpackDWord()
            modulePath = readPackObj.UnpackStringW()
            resultPack[info] = {
                u'ModuleHandle': moduleHandle,
                u'ImageBase': moduleImageBase,
                u'ImageSize': moduleImageSize,
                u'ModuleName': modulePath }
        
        if self.OnMemoryGuardCallback != None:
            self.OnMemoryGuardCallback(resultPack)
