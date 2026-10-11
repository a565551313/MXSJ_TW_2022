# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\struct.py
__version__ = '0.1'
from _struct import Struct, error
_MAXCACHE = 100
_cache = {}

def _compile(fmt):
    if len(_cache) >= _MAXCACHE:
        _cache.clear()
    s = Struct(fmt)
    _cache[fmt] = s
    return s


def calcsize(fmt):
    try:
        o = _cache[fmt]
    except KeyError:
        o = _compile(fmt)

    return o.size


def pack(fmt, *args):
    try:
        o = _cache[fmt]
    except KeyError:
        o = _compile(fmt)

    return o.pack(*args)


def pack_into(fmt, buf, offset, *args):
    try:
        o = _cache[fmt]
    except KeyError:
        o = _compile(fmt)

    return o.pack_into(buf, offset, *args)


def unpack(fmt, s):
    try:
        o = _cache[fmt]
    except KeyError:
        o = _compile(fmt)

    return o.unpack(s)


def unpack_from(fmt, buf, offset=0):
    try:
        o = _cache[fmt]
    except KeyError:
        o = _compile(fmt)

    return o.unpack_from(buf, offset)
