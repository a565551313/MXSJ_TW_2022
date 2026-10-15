# pycdc 交叉复核产物 · script.fls entry 2742
# co_filename(原始)='script/audio/audiomgr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2742.pyc (Python 2.5)

import hero
import interface
import re
import misc
import audio
import permission
import wrapinterface
g_RecMode = 0
g_RecordMsgBar = None
g_RecordTimer = None
g_SequenceTimer = None
g_VoiceRecognise = None
g_Hash2Audio1Info = { }
g_Hash2Audio2Info = { }
g_Url2Hash = { }
g_Url2CanVR = { }
g_VRWork = True
g_AutoVRWork = True
g_AccountWork = True
g_HotKeyTimer = None
g_AudioReadHistory = []
g_AudioFriend = 1
g_MaxAudioDuration = 1800
g_AudioSpeakObject = None
g_AudioSpeakTimer = None
g_FriendAudioSpeakTimer = None
g_HasAudioChannel = [
    1,
    3,
    11]
g_AudioChannel = [
    1,
    3]
g_LoginAudioPlayList = []
g_AudioPlayList = []
g_FriendAudioPlayList = []
g_AudioUrl2PlayerID = { }

def ModuleReset():
    global g_RecMode, g_RecordMsgBar, g_RecordTimer, g_SequenceTimer, g_VoiceRecognise, g_Hash2Audio1Info, g_Hash2Audio2Info, g_Url2Hash, g_Url2CanVR, g_VRWork, g_AutoVRWork, g_AccountWork, g_HotKeyTimer, g_AudioReadHistory, g_AudioFriend, g_MaxAudioDuration, g_AudioSpeakObject, g_AudioSpeakTimer, g_FriendAudioSpeakTimer, g_HasAudioChannel, g_AudioChannel, g_LoginAudioPlayList, g_AudioPlayList, g_FriendAudioPlayList, g_AudioUrl2PlayerID
    g_RecMode = 0
    g_RecordMsgBar = None
    g_RecordTimer = None
    g_SequenceTimer = None
    g_VoiceRecognise = None
    g_Hash2Audio1Info = { }
    g_Hash2Audio2Info = { }
    g_Url2Hash = { }
    g_Url2CanVR = { }
    g_VRWork = True
    g_AutoVRWork = True
    g_AccountWork = True
    g_HotKeyTimer = None
    g_AudioReadHistory = []
    g_AudioFriend = 1
    g_MaxAudioDuration = 1800
    g_AudioSpeakObject = None
    g_AudioSpeakTimer = None
    g_FriendAudioSpeakTimer = None
    g_HasAudioChannel = [
        1,
        3,
        11]
    g_AudioChannel = [
        1,
        3]
    g_LoginAudioPlayList = []
    g_AudioPlayList = []
    g_FriendAudioPlayList = []
    g_AudioUrl2PlayerID = { }

AUDIOLINK = 32
AUDIOVRLINK = 65
AUDIOACLINK1 = 81
AUDIOACLINK2 = 82
AudioPat = re.compile('#s\\(32,(?P<url>.+?),(?P<sec>[0-9]+),(?P<context>[\\s\\S]+?)\\)')
AudioVRPat = re.compile('#s\\(63,(?P<context>[\\s\\S]+?)\\)')
AudioAccountPat1 = re.compile('#s\\(81,(?P<context>[\\s\\S]+?)\\)')
AudioAccountPat2 = re.compile('#s\\(82,(?P<context>[\\s\\S]+?)\\)')
REC_NONE = 0
REC_CHANNEL = 1
REC_FRIEND = 17
REC_ACCOUNTFRIEND = 32
REC_ACCOUNTGROUP = 33
REC_MSG = {
    REC_CHANNEL: '\xbf\xfd\xad\xb5\xa4\xa4\xa1K\xc3P\xb6}\xbf\xfd\xa8\xee\xab\xf6\xb6s(Alt+~)\xa9\xce%s\xac\xed\xab\xe1\xa7\xb9\xa6\xa8\xa8\xc3\xb5o\xb0e\xa1A \xb9\xab\xbc\xd0\xa5k\xc1\xe4\xb0\xb1\xa4\xee\xbf\xfd\xad\xb5\xa8\xc3\xa8\xfa\xae\xf8\xb5o\xb0e',
    REC_FRIEND: '\xbf\xfd\xad\xb5\xa4\xa4\xa1K\xc3P\xb6}\xbf\xfd\xa8\xee\xab\xf6\xb6s(Alt+~)\xa9\xce%s\xac\xed\xab\xe1\xa7\xb9\xa6\xa8\xa8\xc3\xb5o\xb0e\xa1A \xb9\xab\xbc\xd0\xa5k\xc1\xe4\xb0\xb1\xa4\xee\xbf\xfd\xad\xb5\xa8\xc3\xa8\xfa\xae\xf8\xb5o\xb0e',
    REC_ACCOUNTFRIEND: '\xbf\xfd\xad\xb5\xa4\xa4\xa1K\xc3P\xb6}\xbf\xfd\xa8\xee\xab\xf6\xb6s(Alt+~)\xa9\xce%s\xac\xed\xab\xe1\xa7\xb9\xa6\xa8\xa8\xc3\xb5o\xb0e\xa1A \xb9\xab\xbc\xd0\xa5k\xc1\xe4\xb0\xb1\xa4\xee\xbf\xfd\xad\xb5\xa8\xc3\xa8\xfa\xae\xf8\xb5o\xb0e',
    REC_ACCOUNTGROUP: '\xbf\xfd\xad\xb5\xa4\xa4\xa1K\xa6A\xab\xf6\xbf\xfd\xbbs\xab\xf6\xb6s(Alt+~)\xa9\xce%s\xac\xed\xab\xe1\xa7\xb9\xa6\xa8\xa8\xc3\xb5o\xb0e\xa1A \xb9\xab\xbc\xd0\xa5k\xc1\xe4\xb0\xb1\xa4\xee\xbf\xfd\xad\xb5\xa8\xc3\xa8\xfa\xae\xf8\xb5o\xb0e' }

def Release():
    global g_AudioSpeakObject
    if g_AudioSpeakObject:
        g_AudioSpeakObject.Release()
        g_AudioSpeakObject = None
    
    ShowRecordMsg(None)


def ShowRecordMsg(msg):
    global g_RecordMsgBar, g_RecordMsgBar
    if not msg:
        g_RecordMsgBar = None
        return None
    
    g_RecordMsgBar = interface.CTextObject(interface.MainPanel, msg, interface.FontLT14E_1, [
        15990528,
        0], 0)
    g_RecordMsgBar.SetZ(getattr(interface.MainPanel, 'm_MaxZ', 10000) + 1)
    (w, h) = g_RecordMsgBar.GetSize()
    if g_RecMode == REC_FRIEND:
        bw = w
        bh = h
        (bx, by) = (0, 0)
        y = 310
        x = 124
    elif g_RecMode == REC_ACCOUNTFRIEND:
        bw = w
        bh = h
        (bx, by) = (0, 0)
        y = 375
        x = 199
    else:
        x = 8
        bw = w + 10
        bh = 34
        bx = -x
        by = (h - bh) / 2
        y = 554 - h - by
    g_RecordMsgBar.m_BG = interface.CBoxObject(g_RecordMsgBar, bw, bh, 0, 143)
    g_RecordMsgBar.m_BG.SetPos(bx, by)
    g_RecordMsgBar.m_BG.SetZ(-1)
    g_RecordMsgBar.SetPos(x, y)


def GetRecMode():
    edt = interface.GetActiveEdit()
    if edt:
        ui = edt.GetParent()
        import friend
        import dlgtalk
        import chatinput
        import dlgaccountfriend
        import dlgaccountfriendgroup
        if isinstance(ui, dlgtalk.CMultiTalkDialog) and friend.IsFriend(ui.m_PID):
            if getattr(ui, 'FLAG_IS_AUDIO_UI', False) == True:
                if hasattr(ui, 'IsAccountTalkDlg') and ui.IsAccountTalkDlg():
                    return (REC_ACCOUNTFRIEND, ui)
                
                return (REC_FRIEND, ui)
            else:
                return (REC_NONE, None)
        elif isinstance(edt, chatinput.CChatInput) and IsValidAudioChannel() and g_AutoVRWork:
            return (REC_CHANNEL, None)
        elif isinstance(ui, dlgaccountfriend.CAccountTalkDlg):
            return (REC_ACCOUNTFRIEND, ui)
        
    
    return (REC_NONE, None)


def OnStartWithHotkey():
    global g_HotKeyTimer
    import key
    import C_sys
    
    def checkKeyUp(obj):
        if C_sys.IsKeyDown(key.VK_ALT) and C_sys.IsKeyDown(key.VK_WAVE):
            return ()
        
        OnStop()

    OnStart()
    g_HotKeyTimer = interface.CBaseObject(None)
    g_HotKeyTimer.CreatePyCommand(1, checkKeyUp)


def OnStart():
    global g_RecMode, g_RecordTimer
    if g_RecordTimer:
        return None
    
    
    def RecordProcess(obj, frm):
        ui = None
        if obj.m_AudioUI:
            ui = obj.m_AudioUI.Get()
            if ui is None:
                StopRecord(ui)
                g_RecordTimer = None
                return None
            
        
        frm += 1
        if frm % 30 == 0:
            msg = REC_MSG[g_RecMode] % (g_MaxAudioDuration - frm) / 30
            ShowRecordMsg(msg)
        
        if frm >= g_MaxAudioDuration:
            StopRecord(ui)
            g_RecordTimer = None
            return None
        
        return (frm,)

    import usermacro
    (g_RecMode, ui) = GetRecMode()
    if g_RecMode == REC_NONE:
        return None
    
    if g_RecMode == REC_CHANNEL and not IsValidAudioChannel():
        usermacro.PROMPT_MSG('\xbc\xc8\xae\xc9\xa5u\xa4\xe4\xab\xf9\xa6b\xb6\xa4\xa5\xee\xa1B\xc0\xb0\xac\xa3\xa1B\xa5@\xac\xc9\xc0W\xb9D\xb5o\xb0e\xbby\xad\xb5\xabH\xae\xa7')
        return None
    
    if StartRecord():
        import clickcounter
        if g_RecMode == REC_FRIEND:
            clickcounter.Log('\xa6n\xa4\xcd\xbby\xad\xb5')
        
        g_RecordTimer = interface.CBaseObject(None)
        g_RecordTimer.CreatePyCommand(1, RecordProcess, 0)
        if ui:
            ui = interface.CShadowObject(ui)
        
        g_RecordTimer.m_AudioUI = ui
        import key
        key.RegisterRightButtonHotKey(StopAllRecordWithSend)
    


def OnStop():
    global g_RecordTimer
    if not g_RecordTimer:
        return None
    
    ui = None
    if g_RecordTimer.m_AudioUI:
        ui = g_RecordTimer.m_AudioUI.Get()
    
    g_RecordTimer.Release()
    g_RecordTimer = None
    StopRecord(ui)


def StartRecord():
    if audio.IsChatAudioRecording():
        print '\xb7\xed\xabe\xa5\xbf\xa6b\xbf\xfd\xad\xb5\xa4\xa4'
        return False
    
    if audio.RecordChatAudio() != 0:
        return False
    
    msg = REC_MSG[g_RecMode] % g_MaxAudioDuration / 30
    ShowRecordMsg(msg)
    return True


def StopRecord(ui):
    audiofile = audio.StopRecordChatAudio()
    ShowRecordMsg('')
    if not audiofile:
        return None
    
    if g_RecMode & 16 != 0:
        import friend
        if not ui and hasattr(ui, 'm_PID'):
            print 'StopRecord Error !!!'
        elif friend.IsBan(ui.m_PID):
            import usermacro
            usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xb5\xb9\xa1u\xab\xcc\xbd\xaa\xa6W\xb3\xe6\xa1v\xa4\xa4\xaa\xba\xa4H\xb5o\xae\xf8\xae\xa7')
        else:
            PrepareSendFriendChatAudio(audiofile, callback = interface.CShadowObject(ui))
    elif g_RecMode == REC_CHANNEL:
        PrepareSendChannelChatAudio(audiofile)
    elif g_RecMode == REC_ACCOUNTFRIEND:
        PrepareSendAcFriendChatAudio(audiofile, ui.GetActive(), callback = interface.CShadowObject(ui))
    elif g_RecMode == REC_ACCOUNTGROUP:
        if not hasattr(ui, 'm_GroupID'):
            print 'StopRecord Error !!!'
        else:
            PrepareSendAcFriendChatAudio(audiofile, ui.GetActive(), callback = interface.CShadowObject(ui))
    else:
        import channel
        PrepareSendChatAudio(channel.g_Channel, audiofile)


def CompareVRText(sVRText):
    import voicehongbao
    import nethuodong
    import nethdhongbao
    import dlghongbao
    sOrigDict = dlghongbao.GetYuYingMsg()
    for sMsg, dInfo in sOrigDict.items():
        for sChar in [
            '\xa1A',
            ',',
            '?',
            '!',
            '\xa1H',
            '\xa1I']:
            if sChar in sVRText:
                sVRText = sVRText.replace(sChar, '')
            
            if sChar in sMsg:
                sMsg = sMsg.replace(sChar, '')
                continue
        
        iEndTime = dInfo['iEndTime']
        iCurTime = misc.GetServerTime()
        if iEndTime < iCurTime:
            continue
        
        if voicehongbao.CompareVR(sMsg, sVRText):
            idx = dInfo['idx']
            ipid = dInfo['pid']
            iType = dInfo['iType']
            nethdhongbao.C2SOpenHB(idx, ipid, iType)
            continue
    


def StopAllRecordWithSend():
    global g_RecordTimer
    audio.StopRecordChatAudio()
    ShowRecordMsg('')
    if g_RecordTimer:
        g_RecordTimer.Release()
        g_RecordTimer = None
    


def GetPlayAudioVolume():
    sVolume = hero.GetPrivateData('Audio', 'volumplay')
    
    try:
        volume = int(sVolume)
    except:
        volume = 50

    return volume


def GetRecordAudioVolume():
    sVolume = hero.GetPrivateData('Audio', 'volumrecord')
    
    try:
        volume = int(sVolume)
    except:
        volume = 100

    return volume


def SetPlayAudioVolume(sVolume):
    hero.SavePrivateData('Audio', 'volumplay', str(sVolume))
    import dlgsysopt
    dlgsysopt.UpdateAudioSetting()


def SetRecordAudioVolume(sVolume):
    hero.SavePrivateData('Audio', 'volumrecord', str(sVolume))
    import dlgsysopt
    dlgsysopt.UpdateAudioSetting()


def GetMaxDuration():
    return g_MaxAudioDuration


def CleanAudioInfo():
    audio.CleanAudio()


def IsAudioChatMsg(word):
    mo = AudioPat.search(word)
    if mo:
        return True
    else:
        return False


def IsValidAudioChannel():
    import channel
    ch = channel.g_Channel
    if ch in g_HasAudioChannel:
        return True
    
    return False


def IsChCanPlay(ch):
    if ch in g_AudioChannel:
        return True
    
    return False


def AddLoginAudioPlayList(ch, word):
    g_LoginAudioPlayList.append((ch, word))


def CallLoginAudioPlayList():
    global g_LoginAudioPlayList
    for al in g_LoginAudioPlayList:
        g_AudioPlayList.append(al)
    
    g_LoginAudioPlayList = []
    AudioSpeak()


def AddAudioPlayList(ch, word):
    if IsChCanPlay(ch):
        g_AudioPlayList.append((ch, word))
        AudioSpeak()
    


def AudioSpeak():
    global g_AudioSpeakObject, g_AudioSpeakTimer
    if len(g_AudioPlayList) > 0:
        if not g_AudioSpeakObject:
            g_AudioSpeakObject = interface.CBaseObject(None)
        
        if not g_AudioSpeakTimer:
            if not hasattr(hero, 'g_ID'):
                return None
            
            g_AudioSpeakTimer = g_AudioSpeakObject.CreatePyCommand(2, SpeakProcess, hero.g_ID)
        
    


def SpeakProcess(obj, id):
    global g_AudioSpeakTimer
    if len(g_AudioPlayList) > 0:
        data = g_AudioPlayList.pop(0)
        (ch, remain) = data
        if not IsChCanPlay(ch):
            return (id,)
        
        patt = re.compile('^#\\([0-9]+,[^)]+\\)#')
        mo = patt.search(remain)
        if mo is not None:
            comma = remain.find(',')
            end = remain.find(')#')
            uid = int(remain[2:comma])
            name = remain[comma + 1:end]
            student = 0
            comma = name.find(',')
            if comma != -1:
                student = name[comma + 1:]
                name = name[:comma]
            
            remain = remain[mo.end():]
            if id != uid:
                mat = AudioPat.search(remain)
                if mat:
                    url = mat.group('url')
                    sec = mat.group('sec')
                    PreparePlayChatAudio(url)
                
            
        
        return (id,)
    else:
        g_AudioSpeakTimer = None
        return None


def IsValidChat(sVrText):
    import banword
    if not banword.BadWholeWord(sVrText):
        pass
    return banword.IsValidChat(sVrText)[0]


def PrepareSendChatAudio(ch, audiofilename):
    if not hasattr(hero, 'g_ID'):
        return None
    
    if ch not in g_HasAudioChannel:
        return None
    
    audio.UpLoadChatAudio(hero.g_ID, audiofilename, callbackdata = (PreSendChatAudio, ch))


def PreSendChatAudio(ch, url, audiotime):
    StartVR(url, CheckSendChatAudioVR, ch, audiotime)


def CheckSendChatAudioVR(bSucces, url, vrtxt, ch, audiotime):
    if not bSucces:
        return None
    
    if not IsValidChat(vrtxt):
        import usermacro
        usermacro.PROMPT_MSG('\xa4\xba\xaee\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
        return None
    
    SendChatAudio(ch, url, audiotime)


def SendChatAudio(ch, url, audiotime):
    name = getattr(hero.g_Prop, 'm_Name')
    transtext = '#s(%d,%s,%d,%s)' % (AUDIOVRLINK, url, audiotime, name)
    print '\xb5o\xb0e\xbby\xad\xb5\xae\xf8\xae\xa7', ch, transtext
    import netchat
    import stackcheck
    stackcheck.SetBeforeCall(stackcheck.KEY_CHATINPUT)
    netchat.C2SPlayerChat(ch, transtext)


def PreparePlayChatAudio(url):
    destfile = audio.CheckDownLoadFileMap(url)
    if destfile:
        audio.PlayChatAudio(destfile)
    else:
        audio.DownLoadChatAudio(hero.g_ID, url, callbackdata = audio.PlayChatAudio)


def LinkPlayChatAudio(url, bVR = False):
    if bVR == True:
        print '  >> \xa4U\xb8\xfc\xa8\xc3\xb6i\xa6\xe6\xbby\xad\xb5\xc3\xd1\xa7O\xa1G', url
    
    destfile = audio.CheckDownLoadFileMap(url)
    if destfile:
        if not audio.IsChatAudioPlay(destfile):
            audio.StopAllChatAudio()
        
        PlayAudioAndVR(destfile, url, bVR)
    else:
        audio.DownLoadChatAudio(hero.g_ID, url, callbackdata = (PlayAudioAndVR, url, bVR))
    StopSequence()


def AutoVR(url):
    print '  >> \xa4U\xb8\xfc\xa8\xc3\xa6\xdb\xb0\xca\xb6i\xa6\xe6\xbby\xad\xb5\xc3\xd1\xa7O\xa1G', url
    destfile = audio.CheckDownLoadFileMap(url)
    if destfile:
        OnlyAudioVR(destfile, url)
    else:
        audio.DownLoadChatAudio(hero.g_ID, url, callbackdata = (OnlyAudioVR, url))


def OnlyAudioVR(destfile, url):
    StartVR(url)


def PlayAudioAndVR(destfile, url, bVR):
    audio.PlayChatAudio(destfile)
    if bVR:
        StartVR(url)
    


def SavePlayChatAudio(url, username):
    print '\xabO\xa6s\xbby\xad\xb5', url, username
    import os
    chatlogforder = 'ChatLog\\Audio\\'
    if not os.path.exists(chatlogforder):
        os.makedirs(chatlogforder)
    
    filedir = misc.getLan('%s\xbby\xad\xb5-%s-' % (chatlogforder, username))
    if not hasattr(hero, 'g_ID'):
        return None
    
    
    def SaveAudioFile(srcfile, destfrd):
        import shutil
        import usermacro
        import cstr
        filename = cstr.GetFileName(srcfile)
        destfile = destfrd + filename
        shutil.copy(srcfile, destfile)
        usermacro.ROLLINFO2(misc.getLan('%s\xa6s\xa9\xf1\xa6bChatLog\\Audio\\\xa5\xd8\xbf\xfd') % filename)

    downfile = audio.CheckDownLoadFileMap(url)
    if downfile:
        SaveAudioFile(downfile, filedir)
    else:
        audio.DownLoadChatAudio(hero.g_ID, url, callbackdata = (SaveAudioFile, filedir))


def PrepareSendFriendChatAudio(audiofilename, callback = None):
    if not hasattr(hero, 'g_ID'):
        return None
    
    audio.UpLoadChatAudio(hero.g_ID, audiofilename, callbackdata = (PreSendFriendChatAudio, callback))


def PreSendFriendChatAudio(param, url, audiotime):
    StartVR(url, CheckSendAudioVR, param, audiotime)


def CheckSendAudioVR(bSucces, url, vrtxt, param, audiotime):
    if not bSucces:
        return None
    
    if not param:
        return None
    
    if not IsValidChat(vrtxt):
        import usermacro
        usermacro.PROMPT_MSG('\xa4\xba\xaee\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
        return None
    
    SendFriendChatAudio(param, url, audiotime)


def SendFriendChatAudio(param, url, audiotime):
    name = getattr(hero.g_Prop, 'm_Name')
    transtext = '#s(%d,%s,%d,%s)' % (AUDIOLINK, url, audiotime, name)
    print '\xb5o\xb0e\xa6n\xa4\xcd\xb9\xef\xb8\xdc\xbby\xad\xb5', transtext
    if param:
        ui = param.Get()
        if ui and hasattr(ui, 'DoSendMsg'):
            ui.DoSendMsg(transtext)
            StartVR(url, SendAudioVR, param)
        
    


def PrepareSendAcFriendChatAudio(audiofilename, accountID, callback = None):
    if not accountID:
        return None
    
    audio.UpLoadChatAudio(accountID, audiofilename, callbackdata = (PreSendAcFriendChatAudio, callback))


def PreSendAcFriendChatAudio(param, url, filename):
    StartVR(url, CheckSendAcFriendAudioVR, param, filename)


def CheckSendAcFriendAudioVR(bSucces, url, vrtxt, param, filename):
    if not bSucces:
        return None
    
    if not param:
        return None
    
    if not IsValidChat(vrtxt):
        import usermacro
        usermacro.PROMPT_MSG('\xa4\xba\xaee\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
        return None
    
    SendAcFriendChatAudio(param, url, filename)


def SendAcFriendChatAudio(param, url, filename):
    import audio
    (name, audioSec, audioSize, hashStr) = audio.GetAudioInfo(filename)
    newhash = audio.GetUrlHash(url)
    if newhash:
        hashStr = newhash
    
    txt1 = '#s(%d,%s,%s,%d)' % (AUDIOACLINK1, name, hashStr, audioSec)
    txt2 = '#s(%d,%s,%d,%s)' % (AUDIOACLINK2, hashStr, audioSize, url)
    print '\xb5o\xb0e\xbe\xd4\xb7\xf9\xbby\xad\xb5\xc3\xec\xb1\xb51', txt1
    print '\xb5o\xb0e\xbe\xd4\xb7\xf9\xbby\xad\xb5\xc3\xec\xb1\xb52', txt2
    if param:
        ui = param.Get()
        if ui and hasattr(ui, 'DoSendMsg'):
            ui.DoSendMsg(txt1)
            ui.DoSendMsg(txt2)
            SetUrl2Hash(url, hashStr)
            SetAccountAudioCanVR(url)
            StartVR(url, SendAudioVR, param)
        
    


def SendAudioVR(bSucces, url, vrtxt, param):
    if not bSucces:
        return None
    
    if not param:
        return None
    
    ui = param.Get()
    if ui and hasattr(ui, 'DoSendAudioVR'):
        ui.DoSendAudioVR(url, vrtxt)
    


def PrepareSendChannelChatAudio(audiofilename, callback = None):
    if not hasattr(hero, 'g_ID') or not (hero.g_ID):
        return None
    
    import audio
    audio.UpLoadChatAudio(hero.g_ID, audiofilename, utype = 'gp', callbackdata = (PreSendChannelChatAudio, callback))


def PreSendChannelChatAudio(param, url, audiotime):
    StartVR(url, CheckSendChannelAudioVR, param, audiotime)


def CheckSendChannelAudioVR(bSucces, url, vrtxt, param, audiotime):
    if not bSucces:
        return None
    
    if not IsValidAudioChannel():
        return None
    
    if not IsValidChat(vrtxt):
        import usermacro
        usermacro.PROMPT_MSG('\xa4\xba\xaee\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
        return None
    
    SendChannelChatAudio(param, url, audiotime)


def SendChannelChatAudio(param, url, audiotime):
    import mainmenu
    import channel
    name = getattr(hero.g_Prop, 'm_Name')
    transtext = '#s(%d,%s,%d,%s)' % (AUDIOLINK, url, audiotime, name)
    ch = channel.g_Channel
    if IsValidAudioChannel():
        oChatInput = mainmenu.GetChatInputObj()
        if oChatInput is not None:
            oChatInput.Chat(ch, transtext)
        
        StartVR(url, SendChannelAudioVR, ch)
    


def SendChannelAudioVR(bSucces, url, vrtxt, ch):
    import channel
    if not bSucces:
        return None
    
    if not IsValidAudioChannel():
        return None
    
    DoSendChannelAudioVR(ch, url, vrtxt)
    if ch == channel.CH_ORG:
        CompareVRText(vrtxt)
    


def DoSendChannelAudioVR(ch, url, vrtxt):
    import mainmenu
    import channel
    if len(vrtxt) > 225:
        cuttxt = GetCutTxt(vrtxt, 215)
        vrtxt = cuttxt + '\xa1K\xa1K'
    
    transtext = '#s(%d,%s,%s)' % (63, url, vrtxt)
    ch = channel.g_Channel
    if IsValidAudioChannel():
        oChatInput = mainmenu.GetChatInputObj()
        if oChatInput is not None:
            oChatInput.Chat(ch, transtext)
        
    


def GetCutTxt(txt, cutlen):
    board = []
    i = 0
    while i < len(txt):
        board.append(i)
        if ord(txt[i]) < 128:
            i += 1
            continue
        i += 2
    if cutlen not in board:
        cutlen += 1
    
    return txt[:cutlen]


def AddFriendAudioPlayList(sid, word):
    if g_AudioFriend:
        g_FriendAudioPlayList.append((sid, word))
        FriendAudioSpeak()
    


def FriendAudioSpeak():
    global g_AudioSpeakObject, g_FriendAudioSpeakTimer
    if len(g_FriendAudioPlayList) > 0:
        if not g_AudioSpeakObject:
            g_AudioSpeakObject = interface.CBaseObject(None)
        
        if not g_FriendAudioSpeakTimer:
            if not hasattr(hero, 'g_ID'):
                return None
            
            g_FriendAudioSpeakTimer = g_AudioSpeakObject.CreatePyCommand(2, FriendSpeakProcess, hero.g_ID)
        
    


def FriendSpeakProcess(obj, id):
    global g_FriendAudioSpeakTimer
    if len(g_FriendAudioPlayList) > 0:
        data = g_FriendAudioPlayList.pop(0)
        (sid, remain) = data
        if sid == id:
            return (id,)
        
        import friend
        if not friend.IsFriend(sid):
            return (id,)
        
        mat = AudioPat.search(remain)
        if mat:
            url = mat.group('url')
            sec = mat.group('sec')
            PreparePlayChatAudio(url)
        
        return (id,)
    else:
        g_FriendAudioSpeakTimer = None


def SequencePlay(url):
    destfile = audio.CheckDownLoadFileMap(url)
    if destfile:
        AddSequence(destfile)
    else:
        audio.DownLoadChatAudio(hero.g_ID, url, callbackdata = AddSequence)


def AddSequence(destfile):
    global g_SequenceTimer
    if g_SequenceTimer:
        g_SequenceTimer.m_List.append(destfile)
    else:
        g_SequenceTimer = interface.CBaseObject(None)
        g_SequenceTimer.m_List = [
            destfile]
        g_SequenceTimer.m_Command = None
        g_SequenceTimer.m_Current = None
    if g_SequenceTimer.m_Command is None:
        g_SequenceTimer.m_Command = g_SequenceTimer.CreatePyCommand(2, AudioCheck)
    


def StopSequence():
    global g_SequenceTimer
    if g_SequenceTimer and g_SequenceTimer.m_Command:
        g_SequenceTimer.m_Command.Release()
    
    g_SequenceTimer = None


def AudioCheck(obj):
    if not obj.m_List:
        obj.m_Current = None
        obj.m_Command = None
        return None
    
    destfile = obj.m_List[0]
    if not destfile:
        del obj.m_List[0]
        return ()
    
    if obj.m_Current == destfile:
        if not audio.IsChatAudioPlay(destfile):
            obj.m_Current = None
            del obj.m_List[0]
        
        return ()
    
    audio.StopAllChatAudio()
    audio.PlayChatAudio(destfile)
    obj.m_Current = destfile
    return ()


def InSequenceWaiting(url):
    destfile = audio.CheckDownLoadFileMap(url)
    if destfile and g_SequenceTimer:
        pass
    return destfile in g_SequenceTimer.m_List


def GetVR():
    global g_VoiceRecognise
    if not g_VoiceRecognise:
        g_VoiceRecognise = CVoiceRecognise()
    
    return g_VoiceRecognise


def StartVR(url, callback = None, *args):
    VR = GetVR()
    VR.StartVR(url, callback, *args)


def OnEndVR(bSecceed, url, vrtxt, callbackdata = None):
    VR = GetVR()
    VR.OnVREnd(bSecceed, url, vrtxt, callbackdata)


def SetUrl2Hash(url, hashStr):
    g_Url2Hash[url] = hashStr


def Url2Hash(url):
    return g_Url2Hash.get(url)


def IsAccountAudioCanVR(url):
    return url in g_Url2CanVR


def SetAccountAudioCanVR(url):
    g_Url2CanVR[url] = True


def IsAudioRead(accountID, hashStr):
    return hashStr in GetAudioReadHistory(accountID)


def CheckRepealAudio(checkMsg, hashStr):
    checkMat = AudioPat.search(checkMsg)
    if not checkMat:
        return False
    
    context = checkMat.group('context')
    
    try:
        (_, linkHash) = context.split(',')
    except:
        linkHash = None

    return linkHash == hashStr


def IsAudioVRMsg(msg):
    mo = AudioVRPat.search(msg)
    if mo:
        return True
    
    return False

HeroIdPat = re.compile('#s\\([0-9]+\\)#s\\([0-9]+,(?P<heroid>[0-9]+),(?P<name>[^#\\)\\(]+),[0-9]+\\)')

def GetHeroId(word):
    mat = HeroIdPat.search(word)
    if mat:
        heroid = mat.group('heroid')
        if heroid.isdigit():
            return int(heroid)
        
    
    return hero.g_ID

AudioPat1 = re.compile('#s\\(65,(?P<url>.+?),(?P<sec>[0-9]+),(?P<name>[\\s\\S]+?)\\)')

def GetAudioUrl(word):
    mat = AudioPat1.search(word)
    if mat:
        return mat.group('url')
    
    return ''


def RecordUrl2PlayerID(word):
    url = GetAudioUrl(word)
    if url:
        g_AudioUrl2PlayerID[url] = GetHeroId(word)
    


def GetPlayerIDByUrl(url):
    return g_AudioUrl2PlayerID.get(url, 0)


def DealAudioVRInfo(msg):
    import wrapui
    mat = AudioVRPat.search(msg)
    if mat:
        context = mat.group('context')
        lst = wrapui.Split(context)
        if len(lst) == 2:
            (url, vrText) = lst
            OnEndVR(True, url, vrText)
        
    


def DealAcountAudioVRInfo(accountID, msg, bHero):
    import wrapui
    mat = AudioVRPat.search(msg)
    if mat:
        context = mat.group('context')
        lst = wrapui.Split(context)
        if len(lst) == 3:
            (url, vrText, hashStr) = lst
            if bHero:
                SetAccountAudioCanVR(url)
            
            OnEndVR(True, url, vrText)
        
    


def AddAudioReadHistory(ID, sHash):
    if sHash not in g_AudioReadHistory:
        g_AudioReadHistory.append(sHash)
    


def GetAudioReadHistory(ID):
    return g_AudioReadHistory


def IsAccountAudio1(msg):
    mat = AudioAccountPat1.search(msg)
    return mat is not None


def IsAccountAudio2(msg):
    mat = AudioAccountPat2.search(msg)
    return mat is not None


def MergeAudio(iAudioType, bHero, msg):
    if not g_AccountWork:
        return None
    
    if iAudioType == 1:
        mat = AudioAccountPat1.search(msg)
        if mat:
            context = mat.group('context')
            lst = context.split(',')
            filename = lst[0]
            hashStr = lst[1]
            sec = int(lst[2])
            if hashStr in g_Hash2Audio2Info:
                (_, url) = g_Hash2Audio2Info[hashStr]
                del g_Hash2Audio2Info[hashStr]
                return '#s(%d,%s,%d,%d,%s)' % (AUDIOLINK, url, sec, bHero, hashStr)
            else:
                g_Hash2Audio1Info[hashStr] = (filename, sec)
        
    elif iAudioType == 2:
        mat = AudioAccountPat2.search(msg)
        if mat:
            context = mat.group('context')
            lst = context.split(',')
            (hashStr, audioSize, url) = lst
            if hashStr in g_Hash2Audio1Info:
                (filename, sec) = g_Hash2Audio1Info[hashStr]
                del g_Hash2Audio1Info[hashStr]
                return '#s(%d,%s,%d,%d,%s)' % (AUDIOLINK, url, sec, bHero, hashStr)
            else:
                g_Hash2Audio2Info[hashStr] = (audioSize, url)
        
    


class CVoiceRecognise(object):
    
    def __init__(self):
        self.m_Url2Txt = { }
        self.m_FailUrlLst = []
        self.m_AudioObjs = { }

    
    def GetVRText(self, url):
        return self.m_Url2Txt.get(url, '')

    
    def IsFailUrl(self, url):
        return url in self.m_FailUrlLst

    
    def IsVRWork(self):
        return g_VRWork

    
    def GetAmrPath(self, dyaPath):
        import C_audio
        import os
        import md5
        if not audio.g_CheckCode:
            print '  >> \xbby\xad\xb5\xa5\xbc\xaa\xec\xa9l\xa4\xc6\xa9\xce\xaa\xec\xa9l\xa4\xc6\xa5\xa2\xb1\xd1'
            return None
        
        (dirname, ext) = os.path.splitext(dyaPath)
        amrPath = dirname + '.amr'
        validStr = md5.md5('%s[%u]' % (dyaPath, audio.g_CheckCode)).hexdigest()
        state = C_audio.ConvertDyaToAmr(dyaPath, amrPath, validStr)
        if state == 0:
            if os.path.isfile(amrPath):
                return amrPath
            
        

    
    def Url2AmrPath(self, url):
        if permission.IsDebugVoice():
            return 'server.ini'
        
        import os
        dyaPath = audio.CheckDownLoadFileMap(url)
        if not dyaPath:
            return None
        
        if not os.path.isfile(dyaPath):
            return None
        
        amrPath = self.GetAmrPath(dyaPath)
        return amrPath

    
    def RegistObject(self, url, obj):
        if not self.IsVRWork():
            return None
        
        self.RemoveObject(url, obj)
        if url not in self.m_AudioObjs:
            self.m_AudioObjs[url] = []
        
        self.m_AudioObjs[url].append({
            'oObj': misc.WeakRef(obj),
            'iObjID': id(obj) })

    
    def RemoveObject(self, url, obj):
        objlst = self.m_AudioObjs.get(url)
        if not objlst:
            return None
        
        lst = []
        for realobj in objlst:
            if realobj['iObjID'] and realobj['iObjID'] != id(obj):
                lst.append(realobj)
                continue
        
        self.m_AudioObjs[url] = lst

    
    def StartVR(self, url, callback = None, *args):
        print '  >> StartVR :', url
        import voicerecognise
        if not self.IsVRWork():
            return None
        
        if url in self.m_Url2Txt:
            self.OnVREnd(True, url, self.m_Url2Txt[url], callbackdata = (callback, args))
            return None
        
        amrPath = self.Url2AmrPath(url)
        if not amrPath:
            print '  >> \xbby\xad\xb5\xa4\xe5\xa5\xf3\xa5\xbc\xa4U\xb8\xfc\xa1G', url
            return None
        
        voicerecognise.StartVR(amrPath, url, OnEndVR, (callback, args))
        oObjList = self.m_AudioObjs.get(url)
        if oObjList:
            for iPos in range(len(oObjList) - 1, -1, -1):
                dRealDict = oObjList[iPos]
                if dRealDict['oObj']:
                    oRealObj = dRealDict['oObj']()
                    if oRealObj:
                        if hasattr(oRealObj, 'OnAudioVRStart'):
                            oRealObj.OnAudioVRStart()
                        
                    else:
                        del oObjList[iPos]
                oRealObj
                del oObjList[iPos]
            
        
        if oObjList:
            self.m_AudioObjs[url] = oObjList
        

    
    def OnVREnd(self, bSucceed, url, vrtxt, callbackdata = None):
        if permission.IsDebugVoice():
            bSucceed = True
            vrtxt = '\xa4\xba\xb3\xa1\xb4\xfa\xb8\xd5\xa4\xe5\xa5\xbb'
        
        print '  >> OnVREnd: ', bSucceed, url, vrtxt
        if not self.IsVRWork():
            return None
        
        if bSucceed:
            self.m_Url2Txt[url] = vrtxt
            if url in self.m_FailUrlLst:
                self.m_FailUrlLst.remove(url)
            
        else:
            self.m_FailUrlLst.append(url)
        oObjList = self.m_AudioObjs.get(url)
        if oObjList:
            for iPos in range(len(oObjList) - 1, -1, -1):
                dRealDict = oObjList[iPos]
                if dRealDict['oObj']:
                    oRealObj = dRealDict['oObj']()
                    if oRealObj:
                        if hasattr(oRealObj, 'OnAudioVREnd'):
                            if bSucceed:
                                oRealObj.OnAudioVREnd(vrtxt)
                            else:
                                oRealObj.OnAudioVRFail()
                        
                    else:
                        del oObjList[iPos]
                oRealObj
                del oObjList[iPos]
            
        
        if oObjList:
            self.m_AudioObjs[url] = oObjList
        
        if callbackdata:
            func = callbackdata[0]
            args = callbackdata[1]
            if func:
                func(bSucceed, url, vrtxt, *args)
            
        



class CAudioBtn(wrapinterface.CButtonWithTips):
    
    def LeftDown(self):
        import key
        import nethdhongbao
        import gamemoduledefines
        import stopgamemoduleinterface
        if stopgamemoduleinterface.CheckStop(gamemoduledefines.GAMEMODULE_CHATAUDIO):
            return None
        
        
        def leftUp():
            import key
            key.RegisterRightButtonHotKey()
            key.RegisterLeftButtonHotKey(None)
            OnStop()
            if hasattr(self, 'm_IsEnter') and self.m_IsEnter:
                self.SetFrame(2)
            else:
                self.SetFrame(0)

        OnStart()
        nethdhongbao.C2SRequestYuYingMsg()
        key.RegisterLeftButtonHotKey(leftUp)
        self.SetFrame(1)
        parent = self.GetParent()
        if parent and hasattr(parent, 'ActiveInputWithAudio'):
            parent.ActiveInputWithAudio()
        

    
    def LeftUp(self):
        pass

    
    def Enter(self):
        wrapinterface.CButtonWithTips.Enter(self)
        self.m_IsEnter = True

    
    def Leave(self):
        wrapinterface.CButtonWithTips.Leave(self)
        self.m_IsEnter = False
