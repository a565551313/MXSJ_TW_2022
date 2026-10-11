# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\processlib.py


def ModuleReset(mode=0):
    global g_LastGetProcessTime
    global g_ModuleList
    global g_ProcessDct
    global g_ProcessPathList
    g_ProcessDct = {}
    g_LastGetProcessTime = 0
    g_ProcessPathList = []
    g_ModuleList = []


ModuleReset()
import C_sys, os

def GetProcessDict():
    global g_LastGetProcessTime
    global g_ProcessDct
    current = C_sys.GetTickCount()
    if not g_ProcessDct or current - g_LastGetProcessTime >= 100:
        g_LastGetProcessTime = current
        result, g_ProcessDct = C_sys.GetProcessDict()
        if result:
            ErrorLog('C_sys.GetProcessDict() error=%s' % result)
    return g_ProcessDct


def GetProcessPathList(bReset=False):
    global g_ProcessPathList
    if not g_ProcessPathList or bReset:
        g_ProcessPathList = []
        for path in C_sys.GetModuleFileName():
            if not path:
                continue
            if path == '<unknown>':
                continue
            g_ProcessPathList.append(path)

    return g_ProcessPathList


def GetModuleList(bReset=False):
    global g_ModuleList
    if not g_ModuleList or bReset:
        result, g_ModuleList = C_sys.GetModuleList()
        if result:
            ErrorLog('C_sys.GetModuleList() error=%s' % result)
    return g_ModuleList


def GetSelfName():
    lst = GetModuleList()
    if lst:
        return os.path.basename(lst[0])
    return 'mxmain.dll'
