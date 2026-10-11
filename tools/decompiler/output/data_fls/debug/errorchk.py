# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\debug\errorchk.py


def GetTraceInfo(traceobj):
    traceinfo = ''
    lasttrace = None
    while traceobj:
        lasttrace = traceobj
        plineno = traceobj.tb_lineno
        pframe = traceobj.tb_frame
        pcode = pframe.f_code
        pfile = pcode.co_filename
        pfunc = pcode.co_name
        traceinfo += "File '%s', line %d ,in '%s'\n" % (str(pfile), plineno, str(pfunc))
        traceobj = traceobj.tb_next

    if lasttrace:
        plocals = lasttrace.tb_frame.f_locals
    else:
        plocals = None
    return (
     traceinfo, plocals)


def ChangeLocalvalueStr(dDict):
    import types
    sMsgList = []
    for sKey, sValue in dDict.iteritems():
        if isinstance(sValue, types.ModuleType):
            continue
        try:
            sValueMsg = GetStr(sValue)
        except:
            sValueMsg = str(sValue)

        sMsgList.append('%s: %s' % (sKey, sValueMsg))

    return ('\n').join(sMsgList)


def GetStr(obj, bHold=False):
    if isinstance(obj, dict):
        sMag = '{'
        for sKey, sVal in obj.iteritems():
            sMag += '%s: %s, ' % (GetStr(sKey, True), GetStr(sVal, True))

        sMag += '}'
        return sMag
    if isinstance(obj, list):
        sMag = '['
        for sKey in obj:
            sMag += '%s, ' % GetStr(sKey, True)

        sMag += ']'
        return sMag
    if isinstance(obj, tuple):
        sMag = '('
        for sKey in obj:
            sMag += '%s, ' % GetStr(sKey, True)

        sMag += ')'
        return sMag
    if isinstance(obj, set):
        sMag = '{'
        for sKey in obj:
            sMag += '%s, ' % GetStr(sKey, True)

        sMag += '}'
        return sMag
    if isinstance(obj, str):
        if bHold:
            return '"%s"' % str(obj)
        return '%s' % str(obj)
    sValueMsg = str(obj)
    iFind = sValueMsg.find('object at')
    if iFind != -1:
        sValueMsg = sValueMsg[1:iFind - 1]
    return sValueMsg


def ErrorInput(sErrorInfo, dLocalvalue=None):
    if dLocalvalue and isinstance(dLocalvalue, dict):
        sLocalInfo = '\n--Engine Locals--\n'
        sLocalInfo += ChangeLocalvalueStr(dLocalvalue)[:1024]
    else:
        sLocalInfo = ''
    sLog = '%s%s' % (sErrorInfo, sLocalInfo)
    import netrender
    netrender.R2CErrUpload(sLog)
