# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\debug\logsys.py
import os, C_sys, C_log, C_debug, C_object
LogFormatType = 6
SHOWTYPES = [
 1]
g_LogMgr = None
g_LogOn = False
g_LogPrint = False
g_BaseInfo = ''
g_LogName = ''

def GetLogMgr():
    global g_LogMgr
    if not g_LogMgr:
        g_LogMgr = CLogMgr()
    return g_LogMgr


def SetLogName(sName):
    global g_LogName
    g_LogName = sName


def GetFrameInfo(popCount):
    import inspect
    frame = inspect.currentframe()
    for i in xrange(0, popCount):
        frame = frame.f_back

    filename, lineno, funcName, lines, index = inspect.getframeinfo(frame)
    return (os.path.basename(filename), lineno, funcName, lines, index)


def GetFileNameAndLineNoPrefix(popCount=2):
    filename, lineno, _, _, _ = GetFrameInfo(1 + popCount)
    return '%s line %d ->' % (filename, lineno)


def WarLog(*args):
    flag = 'war flag->'
    NormalLog(flag, *args)


class CLogger(object):

    def __init__(self, logLv):
        self.m_LogLv = logLv

    def __call__(self, *args, **kwargs):
        self.m_Type = 0 if not kwargs.values() else kwargs.values()[0]
        LogDown(self.m_LogLv, self.m_Type, *args)


class CLogMgr(object):

    def LogDown(self, logLv, type, *args):
        global g_LogOn
        global g_LogPrint
        logText = (' ').join([str(ob).replace('%', '') for ob in args])
        color = {LV_WARING: 'red', LV_ERROR: 'green'}.get(logLv, 0)
        if g_LogOn:
            if logLv == LV_LOGIN:
                self.FileLog('[Login]' + logText)
            else:
                self.FileLog(logText)
        elif logLv == LV_LOCAL:
            self.FileLog(logText)
            return
        if logLv == LV_LOGIN:
            self.PrintLog(logText, color)
            return
        if g_LogPrint or type in SHOWTYPES:
            self.PrintLog(logText, color)

    def FileLog(self, logText):
        logText = logText.replace('{', '｛')
        logText = logText.replace('}', '｝')
        try:
            import gametime
            tmstr = '[%0d-%0d-%0d %0d:%0d:%0d]' % gametime.GetLocalUTC8Date()[:6]
        except BaseException:
            tmstr = ''

        if tmstr:
            logText = tmstr + logText
        C_log.FileLog(logText)
        C_log.FlushPyLog()

    def PrintLog(self, logText, color):
        import gamecode
        logText += '\n'
        logText = gamecode.GameCodeToGBK(logText)
        if color:
            C_debug.ColorPrint(color, logText)
        else:
            C_debug.Print(logText)


def LogDown(logLv, iPrint, *args):
    mgr = GetLogMgr()
    mgr.LogDown(logLv, iPrint, *args)


def GetBaseInfo():
    global g_BaseInfo
    return g_BaseInfo


class EmptyOutput(object):

    def __init__(self):
        return

    def flush(self):
        return

    def write(self, s):
        return

    def writelines(self, l):
        return


def InitLogPrint():
    global g_LogPrint
    import clientright
    g_LogPrint = clientright.IsLocalNet()


def InitSystem():
    global g_LogOn
    InitLogPrint()
    WriteBaseInfo()
    import clientright
    if clientright.IsSpecialVersion() and clientright.IsLocalNet():
        return
    import sys
    sys.stdout = EmptyOutput()
    sys.stderr = EmptyOutput()
    g_LogOn = True


def WriteBaseInfo():
    global LogFormatType
    global g_BaseInfo
    import version
    lst = [
     '脚本版本:%s' % version.GetScriptVersion(),
     '引擎版本:%s' % version.GetSysVersionStr(),
     '系统版本:%s' % str(C_sys.GetWindowVersion()),
     '日志版本:%d' % LogFormatType]
    instance = C_object.CDisplayLinkDirector.GetInstance()
    sGPU = instance.GetConfigInfo('gl.renderer')
    sGLVersion = instance.GetConfigInfo('gl.version')
    lst.append('GPU:%s' % sGPU)
    lst.append('GLVersion:%s' % sGLVersion)
    msg = ('; ').join(lst)
    msg = msg.replace('{', '｛')
    msg = msg.replace('}', '｝')
    g_BaseInfo = '【基础信息】%s' % msg
    C_log.FileLog(g_BaseInfo)


def FlushEngineLog():
    C_log.FlushEngineLog()


def LogStack(*args):
    try:
        import traceback
        tracebackList = traceback.format_stack()
        tracebackList.pop()
        sStack = '\n' + ('').join(tracebackList)
        if args:
            sStack += (' ').join([str(arg) for arg in args])
        NormalLog(sStack)
    except Exception as e:
        NormalLog('LOG出错:', e)


def LogPause():
    LogStack()
    os.system('pause')


def LogErr(*args):
    s = (' ').join([str(arg) for arg in args])
    ErrorLog(s)


def PushLog(sTitle, sMsg, sIM, sTM):
    return


def Print(*args):
    import format
    for arg in args:
        format.Print(arg)


LV_DEBUG = 'debug'
LV_NORMAL = 'normal'
LV_LOCAL = 'local'
LV_WARING = 'warning'
LV_ERROR = 'error'
LV_LOGIN = 'login'
import __builtin__
__builtin__.DebugLog = CLogger(LV_DEBUG)
__builtin__.NormalLog = CLogger(LV_NORMAL)
__builtin__.LocalLog = CLogger(LV_LOCAL)
__builtin__.WarningLog = CLogger(LV_WARING)
__builtin__.ErrorLog = CLogger(LV_ERROR)
__builtin__.LoginLog = CLogger(LV_LOGIN)
__builtin__.LogStack = LogStack
__builtin__.LogPause = LogPause
__builtin__.LogErr = LogErr
__builtin__.WarLog = WarLog
__builtin__.PushLog = PushLog
__builtin__.Print = Print
