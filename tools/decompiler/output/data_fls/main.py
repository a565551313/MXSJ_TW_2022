# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\main.py
import pubmain
Quit = False

def MainLoop(f, mousex, mousey):
    global Quit
    if Quit:
        return 1
    pubmain.Loop(f)


def GameLoop(*args):
    f, x, y = args
    r = MainLoop(f, x, y)
    return r


def MainLoopQuit(flag):
    global Quit
    Quit = flag


Loop = GameLoop

def RenderStart():
    import pubmain
    pubmain.Start()
    import logsys
    logsys.InitSystem()
    import renderagent
    renderagent.Start()


Start = RenderStart
import engineapi

def DrawScene():
    engineapi.LoopStart()


def PerformBeforeUpdate():
    engineapi.PerformBeforeUpdate()


def BeforeVisit():
    engineapi.BeforeVisit()


def RenderChatwindow():
    engineapi.RenderChatwindow()


def Render():
    engineapi.Render()


def SchedulerUpdate(dt):
    engineapi.SchedulerUpdate(dt)


def ObjectMgrUpdate(ptr, skip):
    engineapi.ObjectMgrUpdate(ptr, skip)


def UpdateWalkerObjXsFrame():
    engineapi.UpdateWalkerObjXsFrame()


def GlfwPollEvents():
    engineapi.GlfwPollEvents()


def OnSizeRestored(*args):
    return
