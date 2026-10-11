# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\init.py
import C_debug, C_sys, sys, version, cStringIO

class CStdout(object):

    def __init__(self):
        self.m_Buffer = cStringIO.StringIO()

    def flush(self):
        self.m_Buffer.flush()

    def write(self, s):
        self.m_Buffer.write(s)
        if s.endswith('\n'):
            C_debug.Print(C_sys.UTF8_to_GBK(self.m_Buffer.getvalue()[:-1]))
            self.m_Buffer.seek(0)
            self.m_Buffer.truncate()

    def writelines(self, l):
        map(self.write, l)

    def close(self):
        self.m_Buffer.close()


class CStderr(CStdout):
    pass


sys.stdout = CStdout()
sys.stderr = CStderr()

def ErrorCallback(*args):
    if len(args[0]) <= 1:
        return
    else:
        if args[0].startswith('[WindowsMessage]WM_NCLBUTTONDOWN'):
            import looptime
            looptime.SetIsMoveWindow()
            return
        lst = args[0].split('\n')
        import glcheck
        if glcheck.OnGLError(lst[0]):
            return
        if len(lst) < 3:
            return
        if not lst[1]:
            return
        import errorchk
        if len(args) >= 3 and args[2]:
            traceinfo, localvalue = errorchk.GetTraceInfo(args[2])
        else:
            traceinfo, localvalue = args[0], None
        try:
            errorchk.ErrorInput(str(args[0]), localvalue)
        except Exception as e:
            print 'game.OnPythonError::ErrorInput错误!!', e

        return


C_debug.SetErrorCallback(ErrorCallback)
import gc
gc.disable()

def GetScriptPath():
    scriptPath = C_sys.GetPyHome()
    flspath = scriptPath + '/data.fls'
    if C_sys.FileExist(flspath):
        scriptPath = flspath
    return scriptPath


def DefaultSysPath():
    scriptPath = GetScriptPath()
    sys.path.append(scriptPath + '/check')
    sys.path.append(scriptPath + '/common')
    sys.path.append(scriptPath + '/core')
    sys.path.append(scriptPath + '/debug')
    sys.path.append(scriptPath + '/lib')
    sys.path.append(scriptPath + '/pub2')
    sys.path.append(scriptPath + '/render')
    sys.path.append(scriptPath + '/ui')


DefaultSysPath()
import os, datetime
app_work_path = C_sys.GetAppWorkPath()
if not os.path.isdir(app_work_path):
    app_work_path = C_sys.GBK_to_UTF8(app_work_path)
try:
    logpath = app_work_path + 'log/render'
    os.makedirs(logpath)
except:
    pass

sCmdLine = C_sys.GetCmdLine()
if 'proc_render' in sCmdLine:
    logname = datetime.datetime.today().strftime('r_pylog_%Y-%m-%d %H-%M-%S.txt')
else:
    logname = datetime.datetime.today().strftime('c_pylog_%Y-%m-%d %H-%M-%S.txt')
LOGNAME = app_work_path + 'log/render/' + logname
C_debug.SetStdOut(LOGNAME)
os.chdir(app_work_path)
import logsys
logsys.SetLogName(LOGNAME)
import C_misc
if hasattr(C_misc, 'SetDumpFileNamePrefix'):
    dmpname = logname + '&' + version.GetSysVersionStr() + '&' + version.GetScriptVersionStr() + '&'
    C_misc.SetDumpFileNamePrefix(dmpname)
DistributeDict = {}

def Distribute(script_id, *args):
    global DistributeDict
    if script_id not in DistributeDict:
        raise SystemError('unknow script_id:%d' % script_id)
    mod_name, func_name = DistributeDict[script_id]
    func = getattr(__import__(mod_name), func_name, None)
    if callable(func):
        return func(*args)
    else:
        NormalLog('Init.Distribute ', mod_name, func_name)
        return


import pubmain
pubmain.Initialize()
import delegate
C_debug.ColorPrint('red', '======init======\n')
