# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\common\clientright.py
import os, cfg
g_GmVersionMgr = None

def GetMgr():
    global g_GmVersionMgr
    if not g_GmVersionMgr:
        g_GmVersionMgr = CGMVersionMgr()
    return g_GmVersionMgr


def IsSpecialVersion():
    return GetMgr().IsSpecialVersion()


def IsLocalNet():
    return GetMgr().IsLocalNet()


def HasPower(sPowerKey):
    return GetMgr().HasPower(sPowerKey)


def IsInNet():
    return GetNetName() in ('广州内网', '成都内网')


def IsMidNet():
    return GetNetName() in ('广州中网', '成都中网')


def GetNetName():
    import pubcore.misc
    return pubcore.misc.GetNetWorkSegment()


class CGMVersionMgr(object):

    def __init__(self):
        self.m_IsSpecialVersion = os.path.exists('nocheck')
        self.m_Powers = {}
        self.InitPowers()

    def InitPowers(self):
        self.m_Powers = {}
        dAllInfo = cfg.GetSysDict('nocheck')
        if not dAllInfo:
            return
        dGameInfo = dAllInfo.get('game', {})
        for sKey, sValue in dGameInfo.iteritems():
            self.m_Powers[sKey] = sValue == '1'

        if self.m_Powers.get('ignore_nocheck'):
            self.m_IsSpecialVersion = False

    def IsSpecialVersion(self):
        return self.m_IsSpecialVersion

    def HasPower(self, sKey):
        return bool(self.m_Powers.get(sKey.lower()))

    def IsLocalNet(self):
        return self.HasPower('LocalNet')
