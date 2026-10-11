# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\pubvars.py
g_bIsInDevice = False
g_WorkingPath = ''
g_DocumentsPath = ''
g_LibraryPath = ''
g_UpdateResPath = ''
g_IniDirPath = ''
g_ConfigIniFilePath = ''
g_UpdateIniFilePath = ''
g_PubDataDirPath = ''
g_PubIniDirPath = ''
g_PubIniPath = ''
g_EGLView = None
g_ccDirector = None
g_SpriteFrameCache = None
g_TextureCache = None
g_sDeviceUniqueID = ''
g_fCurrentTime = 0.0
g_fLastTotalTime = 0.0
g_fServerTime = 0.0
g_fRunningTime = 0.0
g_bIsPlayBgMusic = True
g_bIsPlayEffect = True
g_bIsIpadScene = False
g_bIsIp5Scene = False
g_bIsExitGame = False
g_Platform = None
g_PlatformNum = None
g_PlatformName = {1: 'IOS', 
   2: 'Android', 
   3: 'PC'}
g_AccPlatform = None
g_IsInDevice = None
g_IsIpad = None

def init():
    global g_EGLView
    global g_IniDirPath
    global g_SpriteFrameCache
    global g_TextureCache
    global g_bIsIp5Scene
    global g_bIsIpadScene
    global g_ccDirector
    import os, C_sys, C_object, pubfunc
    g_EGLView = C_object.CDisplayLinkDirector.GetInstance().GetOpenGLView()
    g_ccDirector = C_object.CDisplayLinkDirector.GetInstance()
    g_SpriteFrameCache = C_object.CSpriteFrameCache.GetInstance()
    g_TextureCache = C_object.CTextureCache.GetInstance()
    g_bIsIpadScene = C_sys.GetIsIpad()
    g_bIsIp5Scene = C_sys.GetIsIphone5()
    g_IniDirPath = os.path.join(C_sys.GetAppWorkPath(), '..', 'ini') if pubfunc.IsPC() else os.path.join(C_sys.GetAppWorkPath(), 'ini')


def SetDeviceGlobalVars():
    global g_AccPlatform
    global g_IsInDevice
    global g_IsIpad
    global g_Platform
    global g_PlatformNum
    import C_sys
    g_Platform = C_sys.GetPlatform()
    g_PlatformNum = C_sys.GetPlatformNum()
    g_AccPlatform = g_PlatformNum
    if g_Platform in ('x86_64', 'i386', 'Windows PC'):
        g_IsInDevice = False
    else:
        g_IsInDevice = True
    g_IsIpad = C_sys.GetIsIpad()
