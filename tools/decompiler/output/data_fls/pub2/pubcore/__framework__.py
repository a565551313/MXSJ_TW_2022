# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\__framework__.py
import misc, timer, timernofix, pubdelegate, pubvars

def OnStarted():
    misc.RecordStartTime()
    misc.InitPubDataPath()
    misc.RegisterKeyboardListener()
    if pubdelegate.IsCheckNetWorkSegment():
        misc.CheckNetWorkSegment()
    if pubdelegate.IsCheckCCName():
        misc.InitCCName()
    pubvars.init()


def OnUpdated(fCurTime):
    misc.Loop()
    timer.Loop(fCurTime)
    timernofix.Loop()
