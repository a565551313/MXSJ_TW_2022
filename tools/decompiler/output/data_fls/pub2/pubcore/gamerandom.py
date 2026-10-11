# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\gamerandom.py
__version__ = '1.0.1'
__author__ = ''
__description__ = ''
__require__ = []

def int32(n):
    return n & 4294967295L


def int64(n):
    return n & 18446744073709551615L


class CRandom:

    def __init__(self, iSeed=None):
        if iSeed is not None:
            self.seed(iSeed)
        return

    def seed(self, iSeed):
        x = [
         0, 0, 0, 0, 0]
        s = iSeed
        for i in xrange(5):
            s = int32(s * 29943829) - 1
            x[i] = s

        self.m_Buf = x
        for i in xrange(19):
            self.BRandom()

    def BRandom(self):
        x = self.m_Buf
        sum = 2111111111 * x[3]
        sum += 1492 * x[2]
        sum += 1776 * x[1]
        sum += 5115 * x[0]
        sum += x[4]
        x[3] = x[2]
        x[2] = x[1]
        x[1] = x[0]
        x[4] = int32(sum >> 32)
        x[0] = int32(sum)
        return x[0]

    def random(self):
        r = self.BRandom()
        r *= 1.0 / 4294967296.0
        return r

    def randint(self, iMin, iMax):
        if iMax == iMin:
            return iMin
        if iMax < iMin:
            return 2147483648L
        interval = int32(iMax - iMin + 1)
        longran = int64(self.BRandom() * interval)
        iran = int32(longran >> 32)
        return iMin + iran
