# pycdc 交叉复核产物 · script.fls entry 3505
# co_filename(原始)='script/co\x00\x00on/logicaudio/logic_uploadaudio.py'
# uncompyle6 状态=recovered  转译阶段=baseline
# 生成时间=2026-10-14T23:56:18Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3505.pyc (Python 2.5)

import usermacro
import audio
import slot
import hero
import misc
import timer
UPLOAD_SERVER_TEST = ('http://et.oa.com:6061/ls/ulVoice.jsp',)
UPLOAD_SERVER = ('http://voice2.duoyi.com:83/gv/ulGV.jsp', 'http://voice3.duoyi.com:83/gv/ulGV.jsp')

class CUploadAudioLogic(slot.ISignalSubject):
    SS_StartUpload = 'SS_StartUpLoad(sUrl, sAudioPath)'
    SS_UpLoadResult = 'SS_UpdateResult(bSuc, sPath, sUrl)'
    
    def __init__(self):
        self.ssInit()
        self.m_sAudioPath = ''
        self.m_sAudioUrl = ''
        self.m_bAudioUploadSucceed = False
        self.m_bIsAudioUploadIng = False
        self.m_oEndTimer = None

    
    def ReleaseEndTimer(self):
        if self.m_oEndTimer:
            self.m_oEndTimer.Release()
            self.m_oEndTimer = None
        

    
    def UploadAudio(self, sAudioPath, iHandle, bFailed = False):
        '''\xa4W\xb6\xc7\xbby\xad\xb5\xa8\xec\xbby\xad\xb5\xaaA'''
        LOG_DEBUG('------\xb6}\xa9l\xa4W\xb6\xc7\xad\xb5\xc0W\xb5\xb9\xbby\xad\xb5\xaaA------')
        if not sAudioPath:
            return None
        
        self.m_sAudioPath = sAudioPath
        self.ssEmit(self.SS_StartUpload, sAudioPath, iHandle)
        self.ReleaseEndTimer()
        self.m_oEndTimer = timer.Timer(5, misc.Functor(self.OnUpLoadDeadTime, iHandle), oRelayObj = self)
        self.m_bIsAudioUploadIng = True
        audio.UpLoadChatAudio(hero.\x86\xbe\xa8D, self.m_sAudioPath, callbackdata = (misc.Functor(self.OnUploadAudioCB, iHandle), True), bFailed = bFailed)

    
    def OnUpLoadDeadTime(self, iHandle, *args):
        self.ReleaseEndTimer()
        self.ssEmit(self.SS_UpLoadResult, False, self.m_sAudioPath, self.m_sAudioUrl, iHandle)
        self.Clear()

    
    def IsUpLoading(self):
        return self.m_bIsAudioUploadIng

    
    def Clear(self):
        self.m_sAudioPath = ''
        self.m_sAudioUrl = ''
        self.m_bAudioUploadSucceed = False
        self.m_bIsAudioUploadIng = False

    
    def GetAudioTime(self):
        if self.m_sAudioPath:
            return audio.GetChatAudioPlayTime(self.m_sAudioPath) / 1000
        else:
            return 0

    
    def OnUploadAudioCB(self, iHandle, bSuc, sUrl, iAudioTime):
        self.ReleaseEndTimer()
        self.DoUploadAudioCB(bSuc, sUrl, iAudioTime)
        self.ssEmit(self.SS_UpLoadResult, self.m_bAudioUploadSucceed, self.m_sAudioPath, self.m_sAudioUrl, iHandle)

    
    def DoUploadAudioCB(self, bSucceed, sUrl, iAudioTime):
        LOG_DEBUG('\xa4W\xb6\xc7\xbby\xad\xb5\xa6^\xbd\xd5', bSucceed)
        self.m_bIsAudioUploadIng = False
        if not bSucceed:
            usermacro.PROMPT_MSG('\xa4W\xb6\xc7\xbby\xad\xb5\xa5\xa2\xb1\xd1')
            self.m_bAudioUploadSucceed = False
            return None
        
        if not sUrl:
            usermacro.PROMPT_MSG('\xa4W\xb6\xc7\xbby\xad\xb5\xa5\xa2\xb1\xd1')
            return None
        
        self.m_sAudioUrl = sUrl
        self.m_bAudioUploadSucceed = True
