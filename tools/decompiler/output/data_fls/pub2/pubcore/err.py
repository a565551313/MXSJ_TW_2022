# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\err.py
__version__ = '0.0.1'

class CPubErr(Exception):

    def __init__(self, msg):
        super(CPubErr, self).__init__()
        self.m_Msg = msg

    @property
    def Msg(self):
        return '%s: %s' % (self.__class__.__name__, self.m_Msg)

    def __str__(self):
        return self.m_Msg
