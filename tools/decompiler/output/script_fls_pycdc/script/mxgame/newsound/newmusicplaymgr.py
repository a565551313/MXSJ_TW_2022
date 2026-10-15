# pycdc 交叉复核产物 · script.fls entry 4327
# co_filename(原始)='script/mxgame/newsound/newmusicplaymgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4327.pyc (Python 2.5)

'''
\xd2\xf4\xc0\xd6\xb9\xdc\xc0\xed\xc6\xf7
'''
import C_wwise
import permission
import timer
import newaudioobj
import audio
import sounddefine
BASE_VOL = 37
PREUP_TIME = 0
PREDOWN_TIME = 0
DOWN_TIME = 1500
UP_TIME = 1500
g_oMusicPlayMgr = None

def ModuleReset():
    if g_oMusicPlayMgr:
        g_oMusicPlayMgr.SetIsTeampStop(False)
    


def GetMusicPlayMgr():
    global g_oMusicPlayMgr
    if not g_oMusicPlayMgr:
        g_oMusicPlayMgr = CMusicPlayMgr()
    
    return g_oMusicPlayMgr


def Clear():
    global g_oMusicPlayMgr
    if g_oMusicPlayMgr:
        g_oMusicPlayMgr.StopAllMusic()
    
    g_oMusicPlayMgr = None


class CMusicPlayMgr(object):
    
    def __init__(self):
        self.m_oLastPlayMusic = None
        self.m_oCurPlayMusic = None
        self.m_fSwitchPercent = 0
        self.m_bWindowActive = True
        self.m_iSwitchCount = 0
        self.m_bStopMusic = False
        self.m_iLastVolume = 0
        self.m_iGlobalVolume = 0
        self.m_oSwitchTimer = None

    
    def PlayMusic(self, sEventName, bReplay = True):
        '''
\t\t\xbc\xbd\xa9\xf1\xad\xb5\xbc\xd6
\t\t:param str sEventName: \xa8\xc6\xa5\xf3\xa6W
\t\t:param bool bReplay: \xacO\xa7_\xad\xab\xbc\xbd
\t\t'''
        import delayloading
        import hero
        if self.m_oCurPlayMusic:
            if not bReplay and self.m_oCurPlayMusic.IsSame(sEventName):
                return None
            
            if self.m_oLastPlayMusic:
                self.m_oLastPlayMusic.Stop()
            
            self.m_oLastPlayMusic = self.m_oCurPlayMusic
        
        if self.m_oSwitchTimer:
            self.m_oSwitchTimer.Release()
        
        self.m_fSwitchPercent = 0
        self.m_iSwitchCount = 0
        self.m_oCurPlayMusic = CMusicObject(sEventName, sounddefine.GAME_ID)
        if not self.m_bWindowActive:
            self.SwitchMusicDirectly()
        else:
            self.SwitchMusicDirectly()
            self.m_oCurPlayMusic.Play()
        if audio.GetAudioQueue():
            self.m_oCurPlayMusic.Pause()
        

    
    def GetRealVolume(self):
        return self.m_iGlobalVolume

    
    def SetIsTeampStop(self, bStop):
        if self.m_bStopMusic == bStop:
            return None
        
        self.m_bStopMusic = bStop
        if not bStop:
            if self.m_oCurPlayMusic:
                self.m_oCurPlayMusic.Resume()
            
        elif self.m_oCurPlayMusic:
            self.m_oCurPlayMusic.Pause()
        

    
    def SetGlobalVolume(self, iVolume):
        '''
\t\t\xb3]\xb8m\xb9\xea\xae\xc9\xc1n\xad\xb5
\t\t:param int iVolume: \xc1n\xad\xb5\xaa\xba\xad\xb5\xb6q 0 - 100
\t\t:return:
\t\t'''
        self.m_iLastVolume = iVolume
        if not self.m_bStopMusic:
            self.m_iGlobalVolume = iVolume
            if self.m_oCurPlayMusic:
                pass
            self.m_oCurPlayMusic.SetVolume(self.m_iGlobalVolume)
        
        self.m_bStopMusic

    
    def StopAllMusic(self):
        if self.m_oCurPlayMusic:
            self.m_oCurPlayMusic.Stop()
            self.m_oCurPlayMusic = None
        
        if self.m_oLastPlayMusic:
            self.m_oLastPlayMusic.Stop()
            self.m_oLastPlayMusic = None
        
        if self.m_oSwitchTimer:
            self.m_oSwitchTimer.Release()
            self.m_oSwitchTimer = None
        

    
    def OnMusicSwitch(self):
        if self.m_oLastPlayMusic:
            fPercent = 1 - 100 * (self.m_iSwitchCount - PREDOWN_TIME / 100) / DOWN_TIME
            fPercent = min(1, max(0, fPercent))
            if fPercent == 0:
                self.m_oLastPlayMusic.Stop()
                self.m_oLastPlayMusic = None
            else:
                self.m_oLastPlayMusic.SetVolume(self.m_iGlobalVolume * fPercent)
        
        fPercent = 100 * (self.m_iSwitchCount - PREUP_TIME / 100) / UP_TIME
        fPercent = min(1, max(0, fPercent))
        if self.m_oCurPlayMusic:
            self.m_oCurPlayMusic.SetVolume(self.m_iGlobalVolume * fPercent)
        
        self.m_iSwitchCount += 1

    
    def SwitchMusicDirectly(self):
        if self.m_oLastPlayMusic:
            self.m_oLastPlayMusic.Stop()
            self.m_oLastPlayMusic = None
        
        if self.m_oCurPlayMusic:
            self.m_oCurPlayMusic.SetVolume(self.m_iGlobalVolume)
        

    
    def OnWindowActive(self, bActive):
        self.m_bWindowActive = bActive
        if self.m_oCurPlayMusic:
            if bActive and not audio.GetAudioQueue():
                if self.m_oCurPlayMusic.IsStartPlay():
                    self.m_oCurPlayMusic.Resume()
                else:
                    self.m_oCurPlayMusic.Play()
            else:
                self.m_oCurPlayMusic.Pause()
        



class CMusicObject(newaudioobj.CAudioObject):
    
    def __init__(self, sFileName, iObjID):
        newaudioobj.CAudioObject.__init__(self, sFileName, 100, iObjID)

    
    def Play(self):
        iEventID = C_wwise.SoundEngine_GetIDFromString('play_music')
        self.SetState(self.m_sEventName)
        iPlayingID = C_wwise.SoundEngine_PostEvent(iEventID, self.m_iSoundID, self.m_pFinishCallBack)
        LOG_DEBUG('iPlayingID = ', iPlayingID)
        self.m_iPlayingID = iPlayingID
        if iPlayingID != -1:
            self.m_bIsStartPlay = True
            iVolumeID = C_wwise.SoundEngine_GetIDFromString(sounddefine.VOLUME_MUSIC)
            C_wwise.SoundEngine_SetRTPCValue(iVolumeID, self.m_iVolume, sounddefine.LISTENER_ID)
        
        return iPlayingID

    
    def SetState(self, sState):
        iGoup = C_wwise.SoundEngine_GetIDFromString('map')
        iState = C_wwise.SoundEngine_GetIDFromString(sState)
        C_wwise.SoundEngine_SetState(iGoup, iState)

    
    def SetVolume(self, iVolume):
        if iVolume != self.m_iVolume:
            self.m_iVolume = iVolume
            if self.m_bIsStartPlay:
                iVolumeID = C_wwise.SoundEngine_GetIDFromString(sounddefine.VOLUME_MUSIC)
                C_wwise.SoundEngine_SetRTPCValue(iVolumeID, iVolume, sounddefine.LISTENER_ID)
                LOG_DEBUG('SetRTPCByPlaingID = ', self.m_iPlayingID, 'iVolume= ', iVolume)
