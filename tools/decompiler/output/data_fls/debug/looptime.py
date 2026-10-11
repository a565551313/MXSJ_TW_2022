# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\debug\looptime.py
__all__ = [
 'LoopBegin', 
 'LoopEnd', 
 'GetLastLastLoopTime', 
 'GetLastLoopTime', 
 'GetTimeStamp', 
 'GetAverageLoopTime', 
 'GetOverLoopTime', 
 'SetIsMoveWindow', 
 'IsMoveWindowThisLoop', 
 'IsMoveWindowLastLoop', 
 'IsMoveWindowLastLastLoop']

def LoopBegin():
    SetLoopTime()


def LoopEnd():
    return


g_LastLoopTime = 0
g_LastLastLoopTime = 0
g_TimeStamp = 0
g_LoopFrame = 0
g_AverageLoopTime = [
 0, 0, 0, 0, 0, 0]

def SetLoopTime():
    global g_AverageLoopTime
    global g_LastLastLoopTime
    global g_LastLoopTime
    global g_LoopFrame
    global g_TimeStamp
    import misc
    g_LoopFrame += 1
    curTime = misc.Time()
    if g_TimeStamp == 0:
        g_TimeStamp = curTime
        return
    lastTime = g_TimeStamp
    g_TimeStamp = curTime
    g_LastLastLoopTime = g_LastLoopTime
    g_LastLoopTime = curTime - lastTime
    g_AverageLoopTime[0] += 1
    g_AverageLoopTime[1] += g_LastLoopTime
    if g_LastLoopTime > 0.04:
        g_AverageLoopTime[2] += 1
    if g_LastLoopTime > 0.1:
        g_AverageLoopTime[3] += 1
    if g_LastLoopTime > 0.5:
        g_AverageLoopTime[4] += 1
    if g_LastLoopTime > 1:
        g_AverageLoopTime[5] += 1


def GetLastLoopTime():
    return g_LastLoopTime


def GetLastLastLoopTime():
    return g_LastLastLoopTime


def GetTimeStamp():
    return g_TimeStamp


def GetAverageLoopTime():
    if g_AverageLoopTime[0] > 0:
        return g_AverageLoopTime[1] / g_AverageLoopTime[0]
    return 0


def GetOverLoopTime():
    if g_AverageLoopTime[0] > 0:
        return '%s %s %s %s %s' % (g_AverageLoopTime[0],
         float(g_AverageLoopTime[2]) / g_AverageLoopTime[0],
         float(g_AverageLoopTime[3]) / g_AverageLoopTime[0],
         float(g_AverageLoopTime[4]) / g_AverageLoopTime[0],
         float(g_AverageLoopTime[5]) / g_AverageLoopTime[0])
    return '0 0.0 0.0 0.0 0.0'


g_MoveWindowFrames = []

def SetIsMoveWindow():
    global g_MoveWindowFrames
    g_MoveWindowFrames.append(g_LoopFrame)
    if len(g_MoveWindowFrames) > 10:
        g_MoveWindowFrames.pop(0)


def IsMoveWindowThisLoop():
    return g_LoopFrame in g_MoveWindowFrames


def IsMoveWindowLastLoop():
    loopFrame = g_LoopFrame - 1
    return loopFrame in g_MoveWindowFrames


def IsMoveWindowLastLastLoop():
    loopFrame = g_LoopFrame - 2
    return loopFrame in g_MoveWindowFrames
