# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\respondcheck.py
import version, gamepath, C_misc, C_sys
PID = gamepath.getpid()
MAPNAME = 'respond_%s' % str(PID)
CHECK_EXE = 'exe\\checkrespond\\sw3communicate.exe'
PROCDUMP = 'exe\\checkrespond\\procdump.exe'
CHECK_TIME = 2
CHECK_FILE = 'config/respond.ini'
CHECK_SECTION = 'Setting'
CHECK_KEY = 'check_time'
g_IsStartCheck = False

def OnEnterGame():
    if not version.IsCocosClient():
        return
    if not gamepath.exists(CHECK_EXE):
        return
    StartCheck()


def OnCloseGame():
    StopCheck()


def StartCheck():
    global g_IsStartCheck
    try:
        C_misc.CreateShareMemory(MAPNAME, '123')
    except:
        print 'CreateShareMem Fail!'
        return

    import main
    main.CModuleLoop.AddLoop(__name__, 'Loop')
    ClearLocalFile()
    sver = str(C_sys.GetVersion())
    sver = sver.replace(' ', '')
    info = '%s_withlog' % sver if C_sys.IsLogDebug() else '%s' % sver
    check_time = GetCheckTime()
    cmd = 'start %s %s "%s" %d %s %d' % (CHECK_EXE, MAPNAME, PROCDUMP, check_time, info, PID)
    gamepath.system(cmd)
    g_IsStartCheck = True


def StopCheck():
    if not g_IsStartCheck:
        return
    try:
        C_misc.DestoryShareMemory(MAPNAME)
    except:
        pass

    import main
    main.CModuleLoop.DelLoop(__name__)
    open('respondtxt_%d.txt' % PID, 'w').write('')


def ClearLocalFile():
    for name in gamepath.listdir(gamepath.getcwd()):
        if name.startswith('respond'):
            gamepath.remove(name)


def GetCheckTime():
    try:
        import cfg
        tm = float(cfg.GetData(CHECK_FILE, CHECK_SECTION, CHECK_KEY))
    except:
        tm = CHECK_TIME

    return tm


def Loop():
    if not g_IsStartCheck:
        return
    else:
        import time
        try:
            C_misc.WriteShareMemory(MAPNAME, str(time.time()))
        except:
            print '[respondcheck]WriteShareMemory error'

        has_dump = False
        has_log = False
        for name in gamepath.listdir(gamepath.getcwd()):
            if name.startswith('respond_') and name.endswith('.dmp'):
                has_dump = True
            if name == 'respond_pylog.txt':
                has_log = True

        if has_dump:
            if not has_log:
                import C_log
                logFile = C_sys.UTF8_to_GBK(C_log.GetPyLogPath())
                if gamepath.exists(logFile):
                    import shutil
                    shutil.copy(logFile, 'respond_pylog.txt')
            import commondialog
            tips = '#R【程序未响应】#r请把游戏目录以下文件发给客户端程序，然后删掉（不然会一直弹这个框哦）#r#Rrespond_xxx.dmp#n#r#Rresspond_pylog.txt'
            commondialog.ShowMessageBox(tips, ('哦，好的', ), None)
        return
