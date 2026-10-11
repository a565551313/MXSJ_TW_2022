# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\pubfunc.py
import C_sys, C_object, pubvars, pubdefines, pubdelegate

def GetCurScene():
    return pubdelegate.GetGameScene()


def GetSceneSize():
    pDirector = C_object.CDisplayLinkDirector.GetInstance()
    pScene = pDirector.GetRunningScene()
    if pScene:
        return pScene.GetContentSize()
    else:
        return pDirector.GetWinSize()


def GetWinSize():
    pDirector = GetDirector()
    return pDirector.GetWinSize()


def GetDirector():
    return C_object.CDisplayLinkDirector.GetInstance()


def IsRealDevice():
    return C_sys.GetPlatformNum() != pubdefines.CC_PLATFORM_WIN32


def IsPC():
    return C_sys.GetPlatformNum() == pubdefines.CC_PLATFORM_WIN32


def IsSimulator():
    return C_sys.GetPlatform() in ('x86_64', 'i386')


def IsAndroid():
    return C_sys.GetPlatformNum() == pubdefines.CC_PLATFORM_ANDROID


def IsTV():
    if not IsAndroid():
        return False
    if not C_sys.AndroidCheckHasFeature('android.hardware.touchscreen') or C_sys.AndroidCheckHasFeature('android.software.leanback'):
        return True
    return False


def IsIOS():
    return C_sys.GetPlatformNum() == pubdefines.CC_PLATFORM_IOS


def IsMac():
    return C_sys.GetPlatformNum() == pubdefines.CC_PLATFORM_MAC


def GetOpenGLView():
    return pubvars.g_EGLView


def ExitGame():
    pubvars.g_bIsExitGame = True


def FrameExist(sFameName):
    if C_object.CSpriteFrameCache.GetInstance().GetSpriteFrameByName(sFameName):
        return True
    return False


def ResExist(sName):
    return FrameExist(sName) or C_sys.FileExist(sName)


def ResExistEx(sName):
    return FrameExist(sName) or FileExistEx(sName)


def WinEnginePathConfig(bUseUTF8Path=False):
    if not IsPC():
        return
    if [
     3, 6, 3] > [int(i) for i in C_sys.GetEngineVersion().split('.')]:
        if bUseUTF8Path:
            GetPyHome = lambda : C_sys.GBK_to_UTF8(C_sys.GetPyHome())
            GetHomeDirectory = C_sys.GetHomeDirectory
            GetAppWorkPath = C_sys.GetAppWorkPath
            FileExist = C_sys.FileExist
            AddWorkPath = C_sys.AddWorkPath
        else:
            GetPyHome = C_sys.GetPyHome
            GetHomeDirectory = lambda : C_sys.UTF8_to_GBK(C_sys.GetHomeDirectory())
            GetAppWorkPath = lambda : C_sys.UTF8_to_GBK(C_sys.GetAppWorkPath())
            FileExist = lambda path: C_sys.FileExist(C_sys.GBK_to_UTF8(path))
            AddWorkPath = lambda path: C_sys.AddWorkPath(C_sys.GBK_to_UTF8(path))
    elif bUseUTF8Path:
        GetPyHome = lambda : C_sys.GBK_to_UTF8(C_sys.GetPyHome())
        GetHomeDirectory = lambda : C_sys.GBK_to_UTF8(C_sys.GetHomeDirectory())
        GetAppWorkPath = lambda : C_sys.GBK_to_UTF8(C_sys.GetAppWorkPath())
        FileExist = lambda path: C_sys.FileExist(C_sys.UTF8_to_GBK(path))
        AddWorkPath = lambda path: C_sys.AddWorkPath(C_sys.UTF8_to_GBK(path))
    else:
        GetPyHome = C_sys.GetPyHome
        GetHomeDirectory = C_sys.GetHomeDirectory
        GetAppWorkPath = C_sys.GetAppWorkPath
        FileExist = C_sys.FileExist
        AddWorkPath = C_sys.AddWorkPath
    globals()['GetPyHome'] = GetPyHome
    globals()['GetHomeDirectory'] = GetHomeDirectory
    globals()['GetAppWorkPath'] = GetAppWorkPath
    globals()['FileExist'] = FileExist
    globals()['AddWorkPath'] = AddWorkPath


def IsEngineVersionGreaterEqual(sVer):
    tEngineVer = tuple(int(i) for i in C_sys.GetEngineVersion().split('.'))
    tVer = tuple(int(i) for i in sVer.split('.'))
    return tEngineVer >= tVer


def GetMainSysVer():
    if IsPC():
        return 0
    ver = C_sys.GetSysVersion()
    if ver:
        verlist = ver.split('.')
        if verlist and verlist[0].isdigit():
            return int(verlist[0])
    return 0


g_nNetworkType = None
g_fNetworkTypeLastCallTime = 0

def GetNetworkType():
    global g_fNetworkTypeLastCallTime
    global g_nNetworkType
    nCurTime = C_sys.GetTimeIntervalSince1970()
    if nCurTime - g_fNetworkTypeLastCallTime >= 30:
        g_fNetworkTypeLastCallTime = nCurTime
    if g_nNetworkType is None or nCurTime - g_fNetworkTypeLastCallTime >= 30:
        g_nNetworkType = C_sys.GetNetworkType()
    return g_nNetworkType


g_sProcessNames = None
g_fProcessNamesLastTime = 0
g_CurAPKSignatures = ['', 0]

def GetProcessNames():
    global g_fProcessNamesLastTime
    global g_sProcessNames
    nCurTime = C_sys.GetTimeIntervalSince1970()
    if nCurTime - g_fProcessNamesLastTime >= 180:
        g_fProcessNamesLastTime = nCurTime
    if g_sProcessNames is None or nCurTime - g_fProcessNamesLastTime >= 180:
        if IsIOS() and GetMainSysVer() > 8:
            g_sProcessNames = ''
        else:
            g_sProcessNames = C_sys.GetProcessNames()
    return g_sProcessNames


def GetAPKSignatures():
    global g_CurAPKSignatures
    curTime = C_sys.GetTimeIntervalSince1970()
    if curTime - g_CurAPKSignatures[1] > 180:
        signatures = C_sys.GetAPKSignatures()
        g_CurAPKSignatures = [signatures, curTime]
    else:
        signatures = g_CurAPKSignatures[0]
    return signatures


g_FileExistCache = {}

def FileExistEx(filepath):
    global g_FileExistCache
    b = g_FileExistCache.get(filepath, None)
    if b is None:
        b = C_sys.FileExist(filepath)
        g_FileExistCache[filepath] = b
    return b


def GetScreenBrightness():
    return C_sys.GetScreenBrightness()


def GetExecutablePath():
    return C_sys.GetExecutablePath()


def GetAppWorkPath():
    return C_sys.GetAppWorkPath()
