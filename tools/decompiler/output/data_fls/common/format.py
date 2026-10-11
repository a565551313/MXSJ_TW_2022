# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\common\format.py
__all__ = [
 'Print',
 'Format']

class CHandle(object):

    def __init__(self):
        self.m_Msg = []

    def write(self, sMsg):
        self.m_Msg.append(sMsg)

    def Print(self):
        print ('').join(self.m_Msg)

    def GetMsg(self):
        return ('').join(self.m_Msg)


def Print(*args, **kwargs):
    handle = kwargs.get('handle', None)
    sSpace = kwargs.get('sSpace', '    ')
    if handle is None:
        handle = CHandle()
    for obj in args:
        FormatPrint(handle, obj, sSpace)
        handle.write('\n\n')

    handle.Print()
    return


def Format(obj, sSpace='    '):
    handle = CHandle()
    FormatPrint(handle, obj, sSpace)
    return handle.GetMsg()


def FormatPrintList(handle, obj, sSpace, offset):
    handle.write('[\n')
    for it in obj:
        handle.write(sSpace * (offset + 1))
        FormatPrint(handle, it, sSpace, offset + 1)
        handle.write(',\n')

    handle.write(sSpace * offset)
    handle.write(']')


def FormatPrintTuple(handle, obj, sSpace, offset):
    handle.write('(\n')
    for it in obj:
        handle.write(sSpace * (offset + 1))
        FormatPrint(handle, it, sSpace, offset + 1)
        handle.write(',\n')

    handle.write(sSpace * offset)
    handle.write(')')


def FormatPrintDict(handle, obj, sSpace, offset):
    handle.write('{\n')
    for k, v in obj.iteritems():
        handle.write(sSpace * (offset + 1))
        FormatPrint(handle, k, sSpace, offset + 1)
        handle.write(': ')
        FormatPrint(handle, v, sSpace, offset + 1)
        handle.write(',\n')

    handle.write(sSpace * offset)
    handle.write('}')


def FormatPrintString(handle, obj, sSpace, offset):
    handle.write('"')
    obj = obj.replace('\\', '\\\\')
    obj = obj.replace('"', '\\"')
    obj = obj.replace("'", "\\'")
    obj = obj.replace('', '\\b')
    obj = obj.replace('', '\\f')
    obj = obj.replace('\n', '\\n')
    obj = obj.replace('\r', '\\r')
    obj = obj.replace('\t', '\\t')
    handle.write(obj)
    handle.write('"')


def FormatPrint(handle, obj, sSpace, offset=0):
    import types
    ty = type(obj)
    if ty is types.ListType:
        FormatPrintList(handle, obj, sSpace, offset)
    elif ty is types.TupleType:
        FormatPrintTuple(handle, obj, sSpace, offset)
    elif ty is types.DictType:
        FormatPrintDict(handle, obj, sSpace, offset)
    elif isinstance(obj, (types.StringType, types.UnicodeType)):
        FormatPrintString(handle, obj, sSpace, offset)
    elif ty is types.IntType or ty is types.LongType or ty is types.BooleanType or ty is types.NoneType:
        handle.write(str(obj))
    elif ty is types.FloatType:
        handle.write(str(obj))
    elif hasattr(obj, '__dict__'):
        FormatPrintDict(handle, obj.__dict__, sSpace, offset)
    else:
        handle.write(str(obj))
