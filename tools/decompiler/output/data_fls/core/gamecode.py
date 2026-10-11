# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\core\gamecode.py
import C_sys
__all__ = [
 'GameCodeToGBK',
 'GBKToGameCode',
 'GameCodeToUTF8',
 'UTF8ToGameCode']
CODE_GBK = 'gbk'
CODE_UTF8 = 'utf8'
CODE_BIG5 = 'big5'
CODE_UNICODE = 'unicode'
GAMECODE = CODE_UTF8
SYSCODE = CODE_GBK

def GameCodeToGBK(text):
    if not text or GAMECODE == CODE_GBK:
        return text
    return CRplCode(toGBK=True).Get(text)


def GameCodeToUTF8(text):
    if not text or GAMECODE == CODE_UTF8:
        return text
    return CRplCode(toGBK=False).Get(text)


def GameCodeToUnicode(text):
    if not text or GAMECODE == CODE_UNICODE:
        return text
    return text.decode(GAMECODE)


def GBKToGameCode(text):
    if not text or GAMECODE == CODE_GBK:
        return text
    return CRplCode(toGBK=False).Get(text)


def UTF8ToGameCode(text):
    if not text or GAMECODE == CODE_UTF8:
        return text
    return CRplCode(toGBK=True).Get(text)


def UnicodeToGameCode(text):
    if not text or GAMECODE == CODE_UNICODE:
        return text
    return text.encode(GAMECODE)


def GameCodeToSysCode(text):
    if not text or GAMECODE == SYSCODE:
        return text
    if GAMECODE == CODE_UTF8:
        return CRplCode(toGBK=True).Get(text)
    else:
        return CRplCode(toGBK=False).Get(text)


def SysCodeToGameCode(text):
    if not text or GAMECODE == SYSCODE:
        return text
    if GAMECODE == CODE_UTF8:
        return CRplCode(toGBK=False).Get(text)
    else:
        return CRplCode(toGBK=True).Get(text)


class CRplCode(object):

    def __init__(self, toGBK):
        self.m_IsToGbk = toGBK

    def Get(self, obj):
        itype = type(obj)
        if itype == str:
            return self.GetString(obj)
        if itype == dict:
            return self.GetDict(obj)
        if itype == tuple:
            return tuple(self.GetList(obj))
        if itype == list:
            return self.GetList(obj)
        return obj

    def GetString(self, s):
        if self.m_IsToGbk:
            return C_sys.UTF8_to_GBK(s)
        else:
            return C_sys.GBK_to_UTF8(s)

    def GetDict(self, d):
        dic = {}
        for k, v in d.items():
            k = self.Get(k)
            v = self.Get(v)
            dic[k] = v

        return dic

    def GetList(self, l):
        lst = []
        for v in l:
            lst.append(self.Get(v))

        return lst
