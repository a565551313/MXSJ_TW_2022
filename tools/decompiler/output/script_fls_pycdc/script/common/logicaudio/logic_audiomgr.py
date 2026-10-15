# pycdc 交叉复核产物 · script.fls entry 1155
# co_filename(原始)='script/common/logicaudio/logic_audiomgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1155.pyc (Python 2.5)

import logic_playaudio
import logic_recordaudio
import logic_uploadaudio
g_oAudioMgr = None

def ModuleReset():
    global g_oAudioMgr
    g_oAudioMgr = None


def GetAudioMgr():
    global g_oAudioMgr
    if not g_oAudioMgr:
        g_oAudioMgr = CLogicAudioMgr()
    
    return g_oAudioMgr


def SetTeampStopOtherSound(bStop):
    import musicplaymgr
    import normalaudiomgr
    oMgr = None(None, None, **musicplaymgr)()
    oMgr.SetIsTeampStop(bStop)
    normalaudiomgr.GetSoundPlayMgr().SetIsTeampStop(bStop)


def IsTest():
    return False


class CLogicAudioMgr(object):
    
    def __init__(self):
        self.m_oLogicPlay = None
        self.m_oLogicRecord = None
        self.m_oLogicUpload = None
        self.m_iHandle = 0

    
    def CreateHandle(self):
        iHandle = self.m_iHandle + 1
        if iHandle > 1000000:
            iHandle = 1
        
        self.m_iHandle = iHandle
        return self.m_iHandle

    
    def GetPlayLogic(self):
        ''':rtype:logic_playaudio.CPlayAudioLogic'''
        if not self.m_oLogicPlay:
            self.m_oLogicPlay = logic_playaudio.CPlayAudioLogic()
        
        return self.m_oLogicPlay

    
    def GetRecordLogic(self):
        ''':rtype:logic_recordaudio.CRecordAudioLogic'''
        if not self.m_oLogicRecord:
            self.m_oLogicRecord = logic_recordaudio.CRecordAudioLogic()
        
        return self.m_oLogicRecord

    
    def GetUploadLogic(self):
        ''':rtype:logic_uploadaudio.CUploadAudioLogic'''
        if not self.m_oLogicUpload:
            self.m_oLogicUpload = logic_uploadaudio.CUploadAudioLogic()
        
        return self.m_oLogicUpload
