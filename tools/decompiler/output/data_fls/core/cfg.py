# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\core\cfg.py
import os
g_mxini = {}
g_File2Data = {}
g_File2ModifyTime = {}
g_OpenCache = True

def ModuleReset():
    global g_File2Data
    global g_File2ModifyTime
    global g_OpenCache
    global g_mxini
    g_mxini = {}
    g_File2Data = {}
    g_File2ModifyTime = {}
    g_OpenCache = True


def readanalyser(lines):
    d = {}
    sec = None
    lines = lines.splitlines()
    size = len(lines)
    for i in xrange(size):
        try:
            s = lines[i].strip()
        except IndexError:
            s = ''

        if s == '':
            continue
        if s[0] == '[' and s[-1] == ']':
            d[s[1:-1]] = {}
            sec = d[s[1:-1]]
        elif s.find('=') and sec is not None:
            l = s.split('=')
            if len(l) == 2:
                sec[l[0].strip().lower()] = l[1].strip()

    return d


def _read(fname):
    bMustRead = False
    if not os.path.exists(fname):
        try:
            os.rename(fname + '_', fname)
            bMustRead = True
        except:
            return

    if g_OpenCache and not bMustRead:
        if fname in g_File2ModifyTime:
            try:
                if os.path.getmtime(fname) <= g_File2ModifyTime[fname]:
                    if fname in g_File2Data:
                        return g_File2Data[fname]
            except:
                if fname in g_File2ModifyTime:
                    del g_File2ModifyTime[fname]
                if fname in g_File2Data:
                    del g_File2Data[fname]

    d = {}
    sec = None
    try:
        f = open(fname, 'rt')
    except IOError as ioerror:
        print '读文件错误：', fname, ioerror
        return

    try:
        for line in f:
            s = line.strip()
            if s == '':
                continue
            if s[0] == '[' and s[-1] == ']':
                d[s[1:-1]] = {}
                sec = d[s[1:-1]]
            elif s.find('=') != -1 and sec is not None:
                l = s.split('=', 1)
                sec[l[0].strip().lower()] = l[1].strip()

    except Exception as ex:
        print '解析文件错误：', fname, ex
        d = None

    try:
        f.close()
    except IOError as ioerror:
        print '关闭文件出现异常：', fname, ioerror

    if g_OpenCache:
        try:
            g_File2Data[fname] = d
            g_File2ModifyTime[fname] = os.path.getmtime(fname)
        except:
            if fname in g_File2ModifyTime:
                del g_File2ModifyTime[fname]
            if fname in g_File2Data:
                del g_File2Data[fname]

    return d


def _write(fname, d):
    l = []
    for s, sv in d.iteritems():
        l.append('[%s]\n' % s)
        for k, v in sv.iteritems():
            l.append('%s=%s\n' % (k, v))

    temp = fname + '_'
    try:
        f = open(temp, 'wt')
        f.writelines(l)
        f.close()
        if os.path.exists(fname):
            os.remove(fname)
        os.rename(temp, fname)
    except BaseException:
        return False

    if g_OpenCache:
        try:
            g_File2Data[fname] = d
            g_File2ModifyTime[fname] = os.path.getmtime(fname)
        except:
            if fname in g_File2ModifyTime:
                del g_File2ModifyTime[fname]
            if fname in g_File2Data:
                del g_File2Data[fname]

    return True


def SaveData(fname, section, key, value, dDic=None):
    if value is not None:
        value = str(value)
    if dDic is None:
        d = _read(fname)
    else:
        d = dDic
    if fname == 'mx.ini' and d is None:
        d = _read('mxbak.ini')
    if d is None:
        d = {}
    s = d.get(section)
    if s is None:
        s = {}
        d[section] = s
    key = key.lower()
    s[key] = value
    if fname == 'mx.ini':
        if section not in g_mxini:
            g_mxini[section] = {}
        g_mxini[section][key] = value
    return _write(fname, d)


def GetData(sFName, sSection, sKey):
    global g_mxini
    s = None
    d = _read(sFName)
    if d is not None:
        s = d.get(sSection)
    sKey = sKey.lower()
    if sFName == 'mx.ini' and (d is None or s is None or s.get(sKey) is None):
        d = _read('mxbak.ini')
        if d is not None:
            s = d.get(sSection)
    if d is None or s is None:
        return
    if sFName == 'mx.ini' and d is not None:
        g_mxini = d
    sKey = sKey.lower()
    return s.get(sKey)


def WriteMXIniBackUp():
    fname = 'mxbak.ini'
    if not os.path.exists(fname):
        try:
            f = open(fname, 'wt')
            f.close()
        except:
            return

    return _write(fname, g_mxini)


def GetSysDict(fname):
    global g_mxini
    d = _read(fname)
    if fname == 'mx.ini' and d is not None:
        g_mxini = d
    return d
