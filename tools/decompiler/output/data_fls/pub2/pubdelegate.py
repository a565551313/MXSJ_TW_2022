# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubdelegate.py
__version__ = '0.0.7'
from pubcore.util import Register

@Register
def GetGameScene():
    import C_object
    pDirector = C_object.CDisplayLinkDirector.GetInstance()
    pScene = pDirector.GetRunningScene()
    return pScene


@Register
def GetServerTime():
    raise NotImplementedError('获取服务器时间')


@Register
def GetGameGate():
    raise NotImplementedError('获取游戏产品代号')


@Register
def IsCheckNetWorkSegment():
    return False


@Register
def IsCheckCCName():
    return False


@Register
def GetLan(str):
    return str


@Register
def GetGameRegion():
    raise NotImplementedError('获取游戏上线地区')
