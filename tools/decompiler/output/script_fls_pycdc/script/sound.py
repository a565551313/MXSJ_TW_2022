# pycdc 交叉复核产物 · script.fls entry 4652
# co_filename(原始)='script/sound.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4652.pyc (Python 2.5)

import C_sound
import C_sys
import charpath
import interface
import limitserver
import musicdata
import cfg
import newsoundinterface
import normalaudiomgr
import permission
import broadcastingdata
import sounddefine
g_9416Music = None
g_Music = None
g_Timer = interface.CBaseObject(None)
g_LastTime = None
g_LoopSample = { }
g_bPlayMusic = True
g_bPlaySample = True
g_bInitPlayMusic = True
g_bInitPlaySample = True
g_bTrrigerGroupDownload = False

def SetPlayMusic(bPlayMusic):
    global g_bPlayMusic
    g_bPlayMusic = bPlayMusic


def SetPlaySample(bPlaySample):
    global g_bPlaySample
    g_bPlaySample = bPlaySample


def ModuleReset():
    global g_Music, g_Timer, g_LastTime, g_LoopSample, g_bPlayMusic, g_bPlaySample, g_9416Music, g_bInitPlayMusic, g_bInitPlaySample
    g_Music = None
    g_Timer = interface.CBaseObject(None)
    g_LastTime = None
    g_LoopSample = { }
    g_bPlayMusic = True
    g_bPlaySample = True
    g_9416Music = None
    g_bInitPlayMusic = True
    g_bInitPlaySample = True
    CDownLoadMusic.ResetClear()


def PlayOggMusic(fileName, path):
    import recordvideo
    sPath = '%s/%s' % (path, fileName)
    if path.find('sound') != -1:
        PlayOggNormalSound(sPath)
        return None
    
    recordvideo.CRecordVideo.RecordMusic(fileName, path)
    if not g_bPlayMusic or not g_bInitPlayMusic:
        C_sound.StopMusic()
    else:
        SwitchOggMusicByAudio(fileName, path)


def PlayOggNormalSound(fileName):
    if fileName.find('sound/') == -1:
        return False
    
    import normalaudiomgr
    return normalaudiomgr.GetSoundPlayMgr().PlaySound(fileName)


def SwitchOggMusicByAudio(fileName, path, bReplay = False):
    import musicplaymgr
    if permission.IsOpenNewMusic():
        musicplaymgr.GetMusicPlayMgr().PlayMusic(path + '/' + fileName, bReplay)
    elif bReplay:
        C_sound.StopMusic()
        SetBGMusic(None)
    
    C_sound.PlayMusic(fileName, path)


def SetMusicVolume(iVolume, iType = -1, bChange = True):
    global g_bInitPlayMusic, g_bInitPlayMusic
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.SetMusicVolume(iVolume, iType, bChange)
        return None
    
    SetBgMusicVolume(iVolume)
    SetLoginMusicVolume(iVolume, iType)
    if iVolume == 0 and bChange:
        g_bInitPlayMusic = False
    else:
        g_bInitPlayMusic = True


def SetBgMusicVolume(iVolume):
    import musicplaymgr
    sMusic = GetMusicVolume()
    oMusicPlayMgr = musicplaymgr.GetMusicPlayMgr()
    oMusicPlayMgr.SetGlobalVolume(iVolume)
    iRealVolume = oMusicPlayMgr.GetRealVolume()
    if sMusic:
        if (int(sMusic) == -1 or int(sMusic) == 0) and iRealVolume != 0:
            LOG('\xc1n\xad\xb5\xad\xb5\xb6q:%d %d' % (int(sMusic), iRealVolume))
            LOG_STACK()
        


def SetLoginMusicVolume(iVolume, iType):
    if iType == -1:
        C_sound.SetMusicVolume(iVolume)
    else:
        C_sound.SetMusicVolume(iVolume, iType)


def SetSampleVolume(iVolume, iSampleID = -1):
    global g_bInitPlaySample, g_bInitPlaySample
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.SetSampleVolume(iVolume, iSampleID)
        return None
    
    sMusic = GetVoiceVolume()
    if sMusic:
        if (int(sMusic) == -1 or int(sMusic) == 0) and iVolume != 0:
            LOG('\xad\xb5\xae\xc4\xad\xb5\xb6q:%d %d' % (int(sMusic), iVolume))
            LOG_STACK()
        
    if iSampleID == -1:
        oMgr = normalaudiomgr.GetSoundPlayMgr()
        oMgr.SetVolume(iVolume)
        iVolume = oMgr.GetRealVolume()
        C_sound.SetSampleVolume(iVolume)
    else:
        C_sound.SetSampleVolume(iVolume, iSampleID)
    if iVolume == 0:
        g_bInitPlaySample = False
    else:
        g_bInitPlaySample = True


def SaveNewMusic(iMusic):
    cfg.SaveData('users/local.ini', 'Game', 'music', '%d' % iMusic)


def SaveNewVoice(iVoice):
    cfg.SaveData('users/local.ini', 'Game', 'voice', '%d' % iVoice)


def GetMusicVolume():
    sMusic = cfg.GetData('users/local.ini', 'Game', 'music')
    if not sMusic:
        sMusic = cfg.GetData('mx.ini', 'Game', 'music')
        if sMusic:
            SaveNewMusic(int(sMusic))
        
    
    return sMusic


def GetVoiceVolume():
    sVoice = cfg.GetData('users/local.ini', 'Game', 'voice')
    if not sVoice:
        sVoice = cfg.GetData('mx.ini', 'Game', 'voice')
        if sVoice:
            SaveNewVoice(int(sVoice))
        
    
    return sVoice


def PlaySample(fileName, path):
    import recordvideo
    recordvideo.CRecordVideo.RecordMusic(fileName, path)
    if fileName.endswith('.ogg'):
        fileName = fileName.replace('.ogg', '')
    
    sampleID = C_sound.PlaySample(fileName, path)
    LOG_DEBUG('>>>PlaySample>>>', fileName)
    if not g_bPlaySample or not g_bInitPlaySample:
        C_sound.StopSample(sampleID)
    
    return sampleID


def PlayWithoutCheck(fname):
    return Play(fname, False)


def Play(fname, isCheck = True):
    global g_LastTime
    import soundmgr
    if None(None, None, **permission)():
        return None
    
    if limitserver.IsTestGameServer('wavusenew'):
        return PlayNew(fname, isCheck)
    
    oMgr = soundmgr.GetSoundMgr()
    if not oMgr.GetPathState(fname):
        return None
    
    t = C_sys.GetTime()
    if g_LastTime:
        if t - g_LastTime <= 1000 and isCheck:
            LOG_DEBUG('>>>\xbc\xbd\xa9\xf1\xb3Q\xc4d\xbaI>>>', fname)
            return False
        
    
    if type(fname) == int:
        tPath = musicdata.GetData(fname)
        if tPath:
            (packet, path) = tPath
            if path.endswith('.ogg'):
                PlayOggMusic(path, packet)
            else:
                PlaySample(path, packet)
            bPlaySuccess = True
        else:
            import sounddata
            tPath = sounddata.GetSoundPathByID(fname)
            if tPath:
                (packet, path) = tPath
                if path[-4:] == '.ogg':
                    bPlaySuccess = PlayOggNormalSound('%s/%s' % (packet, path))
                else:
                    PlaySample(path, packet)
                    bPlaySuccess = True
            else:
                bPlaySuccess = False
    elif fname[-4:] == '.ogg':
        bPlaySuccess = PlayOggNormalSound('newsound/%s' % fname)
    elif fname[-4:] == '.snd':
        data = C_sys.LoadFile(fname, 'sound')
        if data:
            lines = data.splitlines()
            for line in lines:
                data = line.split()
                if len(data) == 2:
                    time = int(data[0])
                    
                    def Play(obj, soundname):
                        if soundname.endswith('.ogg'):
                            PlayOggMusic(soundname, 'sound')
                        else:
                            PlaySample(soundname, 'sound')

                    g_Timer.CreatePyCommand(int(data[0]), Play, data[1])
                    continue
            
            bPlaySuccess = True
        else:
            bPlaySuccess = False
    else:
        PlaySample(fname, 'sound')
        bPlaySuccess = True
    if bPlaySuccess:
        g_LastTime = t
    
    return bPlaySuccess


def PlayFBMusic(musicname):
    music = CFBMusic(musicname)
    PlayBGMusic(music)


def PlayNew(fname, isCheck = True):
    global g_LastTime
    import soundmgr
    oMgr = soundmgr.GetSoundMgr()
    if not oMgr.GetPathState(fname):
        return None
    
    t = C_sys.GetTime()
    if g_LastTime:
        if t - g_LastTime <= 1000 and isCheck:
            LOG_DEBUG('>>>\xbc\xbd\xa9\xf1\xb3Q\xc4d\xbaI>>>', fname)
            return False
        
    
    if type(fname) == int:
        tPath = musicdata.GetData(fname)
        if tPath:
            (packet, path) = tPath
            if charpath.IsUseNewRes():
                PlayOggMusic(packet, path)
            else:
                PlaySample(path, packet)
            bPlaySuccess = True
        else:
            import sounddata
            tPath = sounddata.GetSoundPathByID(fname)
            if tPath:
                (packet, path) = tPath
                if charpath.IsUseNewRes():
                    bPlaySuccess = PlayOggNormalSound('%s/%s' % (packet, path))
                else:
                    PlaySample(path, packet)
                    bPlaySuccess = True
            else:
                bPlaySuccess = False
    elif fname[-4:] == '.ogg':
        bPlaySuccess = PlayOggNormalSound('newsound/%s' % fname)
    elif fname[-4:] == '.snd':
        data = C_sys.LoadFile(fname, 'sound')
        if data:
            lines = data.splitlines()
            for line in lines:
                data = line.split()
                if len(data) == 2:
                    time = int(data[0])
                    
                    def Play(obj, soundname):
                        if charpath.IsUseNewRes():
                            PlayOggNormalSound('sound/%s' % soundname)
                        else:
                            PlaySample(soundname, 'sound')

                    g_Timer.CreatePyCommand(int(data[0]), Play, data[1])
                    continue
            
            bPlaySuccess = True
        else:
            bPlaySuccess = False
    else:
        PlaySample(fname, 'sound')
        bPlaySuccess = True
    if bPlaySuccess:
        g_LastTime = t
    
    return bPlaySuccess


def PlayLoginMusic():
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.Play('login', iType = sounddefine.MUSIC_TYPE)
        return None
    
    music = CMusic('new_login')
    PlayBGMusic(music)


def SendMusicLog():
    import cfg
    import netcommon
    music = GetMusicVolume()
    voice = GetVoiceVolume()
    if not music:
        iMusic = 1
    elif int(music) < 0:
        iMusic = 0
    else:
        iMusic = 1
    if not voice:
        iVoice = 1
    elif int(voice) < 0:
        iVoice = 0
    else:
        iVoice = 1
    netcommon.C2SSaveMusicLog(iMusic, iVoice)


class CMusic:
    
    def __init__(self, fname):
        self.m_FileName = fname

    
    def GetFileName(self):
        return self.m_FileName

    
    def Play(self):
        dData = broadcastingdata.GetSpeicalMusicData()
        if self.m_FileName in dData:
            (sFile, sDir) = dData[self.m_FileName]
            PlayOggMusic('%s' % sFile, sDir)
            return None
        
        PlayOggMusic('%s.ogg' % self.m_FileName, 'music')



class CLoadMusic(object):
    
    def __init__(self, fname, path):
        self.m_FileName = fname
        self.m_Path = path

    
    def GetFileName(self):
        return self.m_FileName

    
    def Play(self):
        LOG_DEBUG('CLoadMusic.Play', self.m_FileName, self.m_Path)
        PlayOggMusic(self.m_FileName, self.m_Path)



class CFBMusic(CMusic):
    
    def __init__(self, musicname):
        import random
        if not musicname or len(musicname) <= 0:
            fname = 'm014'
        else:
            fname = musicname
        
        try:
            f = open('music/%s.ogg' % fname)
            f.close()
        except:
            fname = 'm014'

        CMusic.__init__(self, fname)



class CSceneMusic(CMusic):
    
    def __init__(self, sceneid):
        import bgdata
        import random
        d = bgdata.GetSceneData(sceneid)
        if len(d) <= 0:
            fname = 'm014'
        else:
            fname = d[random.randint(0, len(d) - 1)]
        
        try:
            f = open('music/%s.ogg' % fname)
            f.close()
        except:
            fname = 'm014'

        CMusic.__init__(self, fname)



class CFightMusic(CMusic):
    
    def __init__(self, itype):
        import bgdata
        import random
        import hero
        if hero.GetProp('m_Grade', 0) == 0:
            fname = 'm025'
        elif hero.GetProp('m_Grade', 0) <= 30:
            if itype == bgdata.WARTYPE_TASK or itype == bgdata.WARTYPE_ANLEI:
                fname = 'm038'
            else:
                d = bgdata.GetFightData(itype)
                if len(d) <= 0:
                    fname = 'm020'
                else:
                    fname = d[random.randint(0, len(d) - 1)]
        
        try:
            f = open('music/%s.ogg' % fname)
            f.close()
        except:
            fname = 'm020'

        CMusic.__init__(self, fname)



class C9416SceneMusic(CSceneMusic, interface.CBaseObject):
    STEP = 0.333
    LOW_TIME = 1
    
    def __init__(self, sceneid):
        interface.CBaseObject.__init__(self, None)
        CMusic.__init__(self, self.Get9416Music())
        self.m_IsPlay = None
        self.m_IsChangeMusic = None

    
    def Set9416Music(cls, sMusic):
        global g_9416Music
        import hero
        if g_9416Music != sMusic:
            g_9416Music = sMusic
            hero.SavePrivateData('Game', 'musicin9416', sMusic)
            PlayMusic(9416)
        

    Set9416Music = classmethod(Set9416Music)
    
    def Get9416Music(self):
        global g_9416Music, g_9416Music
        import hero
        if g_9416Music is None:
            g_9416Music = hero.GetPrivateData('Game', 'musicin9416')
            if g_9416Music is None:
                g_9416Music = 'newtheme'
            
        
        return g_9416Music

    
    def Play(self):
        self.m_IsPlay = False
        
        def done(obj, v):
            v += obj.STEP
            origv = obj.GetOrigVolume()
            if v > origv:
                obj.m_CurVolume = max(0, int(origv))
                SetMusicVolume(obj.m_CurVolume, bChange = False)
                obj.ReStoreVolume()
                if obj.m_IsPlay == False:
                    obj.m_IsPlay = True
                    CSceneMusic.Play(obj)
                
                return None
            elif C_sys.GetTime() - obj.m_StartTime < obj.LOW_TIME * 10000:
                obj.m_CurVolume = 0
            elif obj.m_IsPlay == False:
                obj.m_IsPlay = True
                CSceneMusic.Play(obj)
            
            obj.m_CurVolume = max(0, int(v))
            SetMusicVolume(obj.m_CurVolume, bChange = False)
            return (v,)

        if hasattr(self, 'm_Timer') and self.m_Timer:
            self.m_Timer.Release()
        
        self.m_StartTime = C_sys.GetTime()
        SetMusicVolume(0, bChange = False)
        self.m_Timer = self.CreatePyCommand(1, done, 0)

    
    def PlayNextMusic(self):
        global g_Music
        self.m_IsChangeMusic = True
        self.ReStoreVolume()
        if g_Music and g_Music.GetFileName() == self.m_NextMusic.GetFileName():
            return None
        
        g_Music = self.m_NextMusic
        g_Music.Play()

    
    def HasChangeMusic(self):
        return self.m_IsChangeMusic is not None

    
    def ChangeMusic(self, nextMusic):
        LOG_DEBUG('\xa7\xf3\xa7\xefmusic')
        self.m_Timer.Release()
        self.m_IsChangeMusic = False
        self.m_NextMusic = nextMusic
        if self.m_IsPlay == False:
            self.PlayNextMusic()
            return None
        
        
        def done(obj):
            if C_sys.GetTime() - obj.m_StartChangeTime > obj.m_ChangeTime * 10000:
                obj.PlayNextMusic()
                return None
            
            return ()

        if hasattr(self, 'm_CMTimer') and self.m_CMTimer:
            self.m_CMTimer.Release()
            self.m_CMTimer = None
        
        self.m_StartChangeTime = C_sys.GetTime()
        self.m_ChangeTime = max((self.m_CurVolume / 100) * 3, 1.2)
        C_sound.SetMusicVolume(0)
        self.m_CMTimer = self.CreatePyCommand(1, done)

    
    def GetOrigVolume(self):
        import cfg
        music = GetMusicVolume()
        if music is None:
            music = 70
        else:
            music = int(music)
        return music

    
    def ReStoreVolume(self):
        v = max(0, self.GetOrigVolume())
        SetMusicVolume(v)

    
    def Release(self):
        if hasattr(self, 'm_Timer') and self.m_Timer:
            self.m_Timer.Release()
        
        if hasattr(self, 'm_CMTimer') and self.m_CMTimer:
            self.m_CMTimer.Release()
        
        interface.CBaseObject.Release(self)
        if self.m_IsChangeMusic == False:
            self.PlayNextMusic()
        elif self.m_IsPlay == False:
            CSceneMusic.Play(self)
        
        self.ReStoreVolume()



def SetBGMusic(music):
    global g_Music
    g_Music = music


def PlayBGMusic(music):
    global g_Music, g_Music
    if g_Music is None:
        g_Music = music
        g_Music.Play()
        return None
    
    if g_Music and isinstance(g_Music, C9416SceneMusic):
        if g_Music.HasChangeMusic():
            g_Music.Release()
        else:
            g_Music.ChangeMusic(music)
            return None
    
    if g_Music and g_Music.GetFileName() == music.GetFileName():
        return None
    
    g_Music = music
    g_Music.Play()


def PlayMusic(sceneid):
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.Play(sceneid, iType = sounddefine.MUSIC_TYPE)
        return None
    
    if sceneid == 9416:
        sceneMusic = C9416SceneMusic(sceneid)
    else:
        sceneMusic = CSceneMusic(sceneid)
    PlayBGMusic(sceneMusic)


def PlayFightMusic(itype):
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.Play('battle_normal', iType = sounddefine.MUSIC_TYPE)
        return None
    
    music = CFightMusic(itype)
    PlayBGMusic(music)


def PlayVirtualSceneMusic(sceneID, sceneName):
    import scenename2sounddata
    if sceneName in scenename2sounddata.DATA:
        filename = scenename2sounddata.DATA[sceneName]
        music = CMusic(filename)
        PlayBGMusic(music)
    else:
        PlayMusic(sceneID)


def PlayDownLoadMusic(fileName, path):
    music = CLoadMusic(fileName, path)
    PlayBGMusic(music)


class CSample(interface.CBaseObject):
    
    def __init__(self, filename, path = 'sound'):
        interface.CBaseObject.__init__(self, None)
        self.m_Filename = filename
        self.m_Path = path
        self.m_PlayID = None

    
    def Play(self):
        pass

    
    def Stop(self):
        if self.m_PlayID is not None:
            C_sound.StopSample(self.m_PlayID)
            self.m_PlayID = None
        

    
    def Playback(self, sec):
        if self.m_PlayID is not None:
            C_sound.SetPlaybackTime(self.m_PlayID, sec)
        

    
    def SetVolume(self, v):
        if self.m_PlayID is not None:
            SetSampleVolume(v, self.m_PlayID)
        



class COnceSample(CSample):
    
    def Play(self):
        self.m_PlayID = PlaySample(self.m_Filename, self.m_Path)



def StopAllLoopSample():
    if permission.IsOpenNewSoundBnk():
        newsoundinterface.StopAllLoopSample()
    else:
        for sid in g_LoopSample.iterkeys():
            C_sound.StopSample(sid)
        


class CLoopSample(CSample):
    
    def Play(self):
        self.Stop()
        self.m_PlayID = PlaySample(self.m_Filename, self.m_Path)
        g_LoopSample[self.m_PlayID] = interface.CShadowObject(self)

    
    def IsPlaying(self):
        return self.m_PlayID is not None

    
    def Stop(self):
        if self.m_PlayID is not None:
            if self.m_PlayID in g_LoopSample:
                del g_LoopSample[self.m_PlayID]
                C_sound.StopSample(self.m_PlayID)
                self.m_PlayID = None
            
        


SND_GETTASK = 1
SND_COMPLETETASK = 2
SND_SHOWDLG = 3
SND_LEVELUP = 4
SND_GETEXP = 5
SND_PLAYEFFECT = 6
SND_CLOSEDLG = 7
SND_BUTTON = 8
SND_PAGEBTN = 9
SND_PROMPT = 10
SOUNDTYPE = {
    SND_GETTASK: 'action/task1.wav',
    SND_COMPLETETASK: 'action/task0.wav',
    SND_SHOWDLG: 'action/opengui.wav',
    SND_LEVELUP: 'action/skillup.wav',
    SND_GETEXP: 'action/exp.wav',
    SND_CLOSEDLG: 'action/closegui.wav',
    SND_BUTTON: 'action/button.wav',
    SND_PAGEBTN: 'action/pageturn.wav',
    SND_PROMPT: 'action/prompt.wav' }

def PlaySound(itype, soundpath = None):
    if soundpath:
        path = soundpath
    else:
        path = SOUNDTYPE.get(itype, 'action/button.wav')
    Play(path)


class CDownLoadMusic(object):
    DOWNLOADDIR = 'musicdownload'
    SPECIALDOWNLOADLIST = [
        'music/theme.ogg',
        'music/newtheme.ogg']
    DOWNLOADGROUP = [
        'broadcast/broadcast001.ogg',
        'broadcast/broadcast002.ogg',
        'broadcast/broadcast003.ogg',
        'broadcast/broadcast004.ogg',
        'broadcast/broadcast005.ogg',
        'broadcast/broadcast006.ogg',
        'broadcast/broadcast007.ogg',
        'broadcast/broadcast008.ogg',
        'broadcast/broadcast009.ogg',
        'broadcast/broadcast010.ogg',
        'broadcast/broadcast011.ogg',
        'broadcast/broadcast012.ogg',
        'broadcast/broadcast013.ogg',
        'broadcast/broadcast014.ogg',
        'broadcast/broadcast015.ogg',
        'broadcast/broadcast016.ogg',
        'broadcast/broadcast017.ogg',
        'broadcast/broadcast018.ogg',
        'broadcast/broadcast019.ogg',
        'broadcast/broadcast020.ogg',
        'broadcast/broadcast021.ogg']
    SENDLOGMAX = 3
    TRYMAX = 3
    s_TryCount = { }
    s_tDownloadTask = []
    s_dDownloadLock = { }
    s_dPlayWhenFinish = { }
    s_SendLogCount = 0
    
    def ResetClear(cls):
        cls.s_TryCount = { }
        cls.s_SendLogCount = 0
        cls.s_dPlayWhenFinish = { }
        cls.s_dDownloadLock = { }
        cls.s_tDownloadTask = []

    ResetClear = classmethod(ResetClear)
    
    def SendLog(cls, log):
        cls.s_SendLogCount += 1
        if cls.s_SendLogCount > cls.SENDLOGMAX:
            return None
        
        
        def DelaySend(obj, dummy, result):
            import hero
            import net
            if net.GetNet() and hero.g_ID:
                import netcommon
                netcommon.C2SSendMusicLog(result)
                return None
            
            return (dummy, result)

        import random
        sec = random.randint(60, 300)
        bobj = interface.CBaseObject(None)
        bobj.CreatePyCommand(sec * 30, DelaySend, bobj, log)

    SendLog = classmethod(SendLog)
    
    def TryAgain(cls, fileName):
        if fileName not in cls.s_TryCount:
            cls.s_TryCount[fileName] = 0
        else:
            cls.s_TryCount[fileName] += 1
        if cls.s_tDownloadTask > cls.TRYMAX:
            cls.bReplay('\xb9F\xa8\xec\xb3\xcc\xa4j\xa4U\xb8\xfc\xa6\xb8\xbc\xc6')
        
        cls.TryDownLoadMusic(fileName)

    TryAgain = classmethod(TryAgain)
    
    def GetDownLoadUrl(cls, fileName):
        import cfg
        import versions
        tVersion = versions.GetClientVersion()
        if fileName in cls.SPECIALDOWNLOADLIST:
            url = cfg.GetData('update.ini', 'Download', 'DLServerUrl')
            if url:
                url = url + '%d.%d.%d/' % tVersion + fileName
            
        else:
            url = cfg.GetData('update.ini', 'Setting', 'DownFile')
            if url:
                url = url + '%d.%d.%d/musicdownload/' % tVersion + fileName
            
        if not url:
            result = 'DLServerUrl\xa4\xa3\xa6s\xa6b'
            cls.SendLog(result)
            print result
            return ''
        
        return url

    GetDownLoadUrl = classmethod(GetDownLoadUrl)
    
    def CheckHashCode(cls, filePath):
        import md5
        import misc
        
        try:
            fObj = misc.OpenFile(filePath, 'rb')
            data = fObj.read()
            code = md5.md5(data).hexdigest()
            hashCode = broadcastingdata.GetHashCode(filePath)
            return code == hashCode
        except IOError:
            ioe = None
            result = '%s:%s' % (ioe.__class__.__name__, ioe.message)
            cls.SendLog(result)
            return False


    CheckHashCode = classmethod(CheckHashCode)
    
    def DownLoadMusic(cls, fileName, bPlayWhenFinish = True):
        import C_sys
        fileName = fileName.replace('music/broadcast', 'broadcast/broadcast')
        filePath = '%s/%s' % (cls.DOWNLOADDIR, fileName)
        if filePath not in broadcastingdata.GetName2HashCodeData():
            return None
        
        if bPlayWhenFinish is not None:
            cls.s_dPlayWhenFinish[fileName] = bPlayWhenFinish
        
        iCurTime = C_sys.GetTime()
        if fileName in cls.s_dDownloadLock:
            if iCurTime - cls.s_dDownloadLock[fileName] < 200000:
                LOG_DEBUG('\xad\xab\xbd\xc6\xa4U\xb8\xfc', fileName)
                return None
            
        
        cls.CheckTrrigerGroupDownload(fileName)
        cls.s_dDownloadLock[fileName] = iCurTime
        cls.TryAgain(fileName)

    DownLoadMusic = classmethod(DownLoadMusic)
    
    def CheckTrrigerGroupDownload(cls, fileName):
        global g_bTrrigerGroupDownload
        import os
        import usermacro
        if not g_bTrrigerGroupDownload:
            if fileName in broadcastingdata.GetDownloadGroupData():
                g_bTrrigerGroupDownload = True
                if not os.path.exists(cls.DOWNLOADDIR + '/' + fileName):
                    usermacro.PROMPT_MSG('\xb9q\xa5x\xa4U\xb8\xfc\xa4\xa4\xa1A\xbd\xd0\xb5y\xb5\xa5\xa1]\xb9w\xadp30\xac\xed\xab\xe1\xa4U\xb8\xfc\xa7\xb9\xa6\xa8\xa6\xdb\xb0\xca\xbc\xbd\xa9\xf1\xa1^')
                
                for sGroupFileName in broadcastingdata.GetDownloadGroupData():
                    if sGroupFileName != fileName and not os.path.exists('%s/%s' % (cls.DOWNLOADDIR, sGroupFileName)):
                        tDownloadTask = (sGroupFileName, None)
                        if tDownloadTask not in cls.s_tDownloadTask:
                            cls.s_tDownloadTask.append(tDownloadTask)
                        
                    tDownloadTask not in cls.s_tDownloadTask
                
            
        

    CheckTrrigerGroupDownload = classmethod(CheckTrrigerGroupDownload)
    
    def TryDownLoadMusic(cls, fileName):
        import os
        filePath = '%s/%s' % (cls.DOWNLOADDIR, fileName)
        bExist = os.path.exists(filePath)
        LOG_DEBUG('\xc0\xcb\xacd\xa5\xbb\xa6a\xad\xb5\xbc\xd6', filePath, bExist)
        if bExist:
            if cls.CheckHashCode(filePath):
                cls.OnDownloadFinish(fileName)
                return True
            
        
        url = cls.GetDownLoadUrl(fileName)
        LOG_DEBUG('\xa4U\xb8\xfc\xad\xb5\xbc\xd6', url, filePath)
        if cls.s_TryCount.get(fileName, 0) == 0:
            import C_net
            C_net.DownloadFile(url, filePath, DownloadCallback)
        else:
            import http
            http.CDownload(url, filePath, HttpDownloadCallback, filePath)

    TryDownLoadMusic = classmethod(TryDownLoadMusic)
    
    def OnDownloadFinish(cls, fileName):
        if cls.s_dPlayWhenFinish.get(fileName, False):
            PlayDownLoadMusic(fileName, cls.DOWNLOADDIR)
        
        if cls.s_tDownloadTask:
            (sFileName, bPlayMusic) = cls.s_tDownloadTask.pop()
            cls.DownLoadMusic(sFileName, bPlayMusic)
        

    OnDownloadFinish = classmethod(OnDownloadFinish)


def DownloadCallback(nResult, sURL, sSaveFilePath):
    LOG_DEBUG('\xa4U\xb8\xfc\xad\xb5\xbc\xd6\xa6^\xbd\xd5', nResult, sURL, sSaveFilePath)
    idx = sSaveFilePath.find('/')
    path = sSaveFilePath[:idx]
    fileName = sSaveFilePath[idx + 1:]
    if nResult != 0:
        result = '\xa4U\xb8\xfc\xad\xb5\xbc\xd6\xa5\xa2\xb1\xd1%s\xa1]%s\xa1^' % (nResult, sURL)
        
        try:
            CDownLoadMusic.SendLog(result)
            CDownLoadMusic.TryAgain(fileName)
        except AttributeError:
            pass

        return None
    
    if CDownLoadMusic.CheckHashCode(sSaveFilePath):
        CDownLoadMusic.OnDownloadFinish(fileName)
    else:
        CDownLoadMusic.SendLog('\xa4U\xb8\xfc\xaa\xba\xa4\xe5\xa5\xf3hash\xa5X\xbf\xf9')
        CDownLoadMusic.TryAgain(fileName)


def HttpDownloadCallback(succeed, sSaveFilePath):
    idx = sSaveFilePath.find('/')
    path = sSaveFilePath[:idx]
    fileName = sSaveFilePath[idx + 1:]
    LOG_DEBUG('Http\xa4U\xb8\xfc\xad\xb5\xbc\xd6\xa6^\xbd\xd5', succeed, sSaveFilePath)
    if not succeed:
        CDownLoadMusic.SendLog('Http\xa4U\xb8\xfc\xa4\xe5\xa5\xf3\xa5\xa2\xb1\xd1')
        CDownLoadMusic.TryAgain(fileName)
        return None
    
    if CDownLoadMusic.CheckHashCode(sSaveFilePath):
        CDownLoadMusic.OnDownloadFinish(fileName)
    else:
        CDownLoadMusic.SendLog('\xa4U\xb8\xfc\xaa\xba\xa4\xe5\xa5\xf3hash\xa5X\xbf\xf9')
        CDownLoadMusic.TryAgain(fileName)
