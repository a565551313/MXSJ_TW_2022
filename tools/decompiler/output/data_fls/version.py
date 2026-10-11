# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\version.py
import C_sys
g_ScriptVersion = [
 0, 0, 1]

def GetSysVersion():
    n1, n2, n3 = C_sys.GetVersion()
    return (n1, n2, n3)


def GetScriptVersion():
    global g_ScriptVersion
    return g_ScriptVersion


def GetSysVersionStr():
    return '%s.%s.%s' % tuple(GetSysVersion())


def GetScriptVersionStr():
    return '%s.%s.%s' % tuple(GetScriptVersion())
