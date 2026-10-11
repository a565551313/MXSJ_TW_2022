# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\util.py
__version__ = '0.0.1'
g_Override = {}

def Register(func):

    def _Wrapper(*args, **kw):
        global g_Override
        override = g_Override.get((func.__module__, func.__name__), func)
        return override(*args, **kw)

    return _Wrapper


def Override(modulename):

    def _Decorator(func):
        g_Override[(modulename, func.__name__)] = func
        return func

    return _Decorator
