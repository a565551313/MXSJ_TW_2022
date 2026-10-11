# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\pubclass.py
__version__ = '0.0.1'

class CSingleTon(object):
    pMgrObj = None

    def __init__(self):
        return

    @classmethod
    def Get(cls):
        if cls.pMgrObj is None or not isinstance(cls.pMgrObj, cls):
            cls.pMgrObj = cls()
        return cls.pMgrObj

    sharedManager = Get

    @classmethod
    def Release(cls):
        cls.pMgrObj = None
        return

    releaseManager = Release
