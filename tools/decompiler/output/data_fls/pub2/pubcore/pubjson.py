# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\pubjson.py
import C_sys, json
g_JsonLib = 0
g_IsUnicode = 1
pyJson25 = getattr(json, 'read', None)
if pyJson25:
    g_JsonLib = 1

def dumps(*args, **kw):
    if g_JsonLib:
        return json.write(*args, **kw)
    else:
        return json.dumps(*args, **kw)


def jsonDumps(*args, **kw):
    if g_JsonLib:
        return json.write(*args, **kw)
    else:
        return json.dumps(*args, **kw)


def loads(*args, **kw):
    if g_JsonLib:
        data = json.read(args[0])
    else:
        data = json.loads(*args, **kw)
    return _ToUtf8(data)


def jsonLoads(*args, **kw):
    if g_JsonLib:
        data = json.read(args[0])
    else:
        data = json.loads(*args, **kw)
    return _ToUtf8(data)


def load(*args, **kw):
    if g_JsonLib:
        raise NotImplementedError('python 2.5 json not support load')
    data = json.load(*args, **kw)
    return _ToUtf8(data)


def dump(*args, **kw):
    if g_JsonLib:
        raise NotImplementedError('python 2.5 json not support dump')
    return json.dump(*args, **kw)


def _Byteify(input, encoding='utf-8'):
    import misc
    if isinstance(input, dict):
        returnDict = {}
        for key, value in input.iteritems():
            returnDict[_Byteify(key)] = _Byteify(value)

        return returnDict
    if isinstance(input, list):
        returnList = []
        for item in input:
            returnList.append(_Byteify(item))

        return returnList
    if isinstance(input, unicode):
        return C_sys.Unicode_to_UTF8(misc.UCS2_to_UCS4(input))
    else:
        return input


def _ToUtf8(data):
    if g_IsUnicode:
        return _Byteify(data)
    return data
