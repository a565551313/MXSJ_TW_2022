# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\signal.py
__version__ = '0.0.1'
import pubclass, slot

def ModuleReset():
    OnRestartClear()


def OnRestartClear():
    CErrorPush.Release()


def EmitErrorPush():
    CErrorPush.Get().ssEmit(CErrorPush.c_ErrorPush)


def ConnectErrorPush(func):
    CErrorPush.Get().ssConnect(CErrorPush.c_ErrorPush, func)


class CSignalBase(pubclass.CSingleTon, slot.ISignalSubject):

    def __init__(self):
        super(CSignalBase, self).__init__()
        slot.ISignalSubject.ssInit(self)


class CErrorPush(CSignalBase):
    c_ErrorPush = 'ErrorPush'
