# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\debug\newlog\loginterface.py
import logcontext

def GetLogContext():
    return logcontext.GetLogContext()


def Loop():
    return


def GetStartTime():
    oLogContext = GetLogContext()
    return oLogContext.GetStartTime()


def LogPrint(sMsg):
    LOG(sMsg)
    return


def LogEvent(iType, dData):
    oLogEventMgr = GetLogContext().GeLLogEventMgr()
    oLogEventMgr.LogEvent(iType, dData)
    return


return
