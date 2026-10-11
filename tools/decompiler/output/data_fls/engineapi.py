# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\engineapi.py
import C_sys

def LoopStart():
    C_sys.DrawScene()


def PerformBeforeUpdate():
    C_sys.PerformBeforeUpdate()


def BeforeVisit():
    C_sys.BeforeVisit()


def RenderChatwindow():
    C_sys.RenderChatwindow()


def Render():
    C_sys.Render()


def SchedulerUpdate(dt):
    C_sys.SchedulerUpdate(dt)


def ObjectMgrUpdate(ptr, skip):
    C_sys.ObjectMgrUpdate(ptr, skip)


def UpdateWalkerObjXsFrame():
    C_sys.UpdateWalkerObjXsFrame()


def GlfwPollEvents():
    C_sys.GlfwPollEvents()
