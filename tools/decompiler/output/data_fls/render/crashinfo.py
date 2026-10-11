# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\render\crashinfo.py


def Set(key, msg):
    import C_object
    director = C_object.CDisplayLinkDirector.GetInstance()
    director.SetCrashInfo(key, msg)


def StartInfo(msg):
    Set('Render::Start', msg)


def CommunicateInfo(msg):
    Set('Render::Communicate', msg)


def DealInfo(msg):
    Set('Render::Deal', msg)


def SpineInfo(msg):
    Set('Render::Spine', msg)


def WaveInfo(msg):
    Set('LastWave', msg)


def BaseInfo():
    import processlib
    name = processlib.GetSelfName()
    import version
    ver = version.GetSysVersionStr()
    import C_log, os
    logpath = C_log.GetPyLogPath()
    logname = os.path.basename(logpath)
    Set('BaseInfo', 'name=%s;version=%s;logname=%s' % (name, ver, logname))
    import pubcore.misc as misc
    sName = misc.GetCCName()
    Set('PlayerName', sName)


def MemoryInfo(msg):
    Set('MemoryInfo', msg)
