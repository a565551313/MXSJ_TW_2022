# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\core\C_log.py


def FileLog(sLogText):
    import C_debug, C_sys
    C_debug.PrintToFile(C_sys.UTF8_to_GBK(sLogText))


def FlushEngineLog():
    return


def FlushPyLog():
    return


def GetEngineLogPath():
    import gamecode, os, C_sys
    path = gamecode.GBKToGameCode(C_sys.GetAppWorkPath())
    return os.path.join(path, 'EngineLog.txt')


def GetPyLogPath():
    import init
    return init.LOGNAME


def SetDmpSuffix(sDmpSuffix):
    return
