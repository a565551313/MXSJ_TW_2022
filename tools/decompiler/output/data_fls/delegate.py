# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\delegate.py
__version__ = '0.0.7'
from pubcore.util import Override

@Override('pubdelegate')
def GetGameScene():
    import C_object
    pDirector = C_object.CDisplayLinkDirector.GetInstance()
    pScene = pDirector.GetRunningScene()
    return pScene


@Override('pubdelegate')
def GetServerTime():
    return 0


@Override('pubdelegate')
def GetGameGate():
    return 'mx'


@Override('pubdelegate')
def IsCheckNetWorkSegment():
    return True


@Override('pubdelegate')
def IsCheckCCName():
    return True


@Override('pubdelegate')
def GetLan(str):
    return str


@Override('pubdelegate')
def GetGameRegion():
    return 'cn'
