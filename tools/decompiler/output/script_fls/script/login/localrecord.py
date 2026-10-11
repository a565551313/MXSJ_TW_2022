# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\localrecord.py
import os, md5, C_sys, permission
TEA = 0
TEA2 = 1
TEA3 = 2
GAMETAG = 'MXSJ'
CHECKTAG = (TEA, TEA2)
g_LocVer = -1
g_CurVer = TEA3
g_bOpenCache = False
g_iModifyTime = 0
g_lstData = []

def InitOpenCache():
    global g_bOpenCache
    g_bOpenCache = permission.GetSpecialVersion()
    return


InitOpenCache()

class AchieveType(object):
    Default = 0
    UsingSmart = 1
    UsingSCSI = 2
    WithZeroRightsAndFlip = 3
    WithZeroRights = 4
    WithAdminRight = 5


def ModuleReset():
    global g_CurVer
    global g_LocVer
    g_LocVer = -1
    g_CurVer = TEA3
    return


def GetCurVer():
    return g_CurVer


def SetLocalPwd(pwd, user):
    oEnfunc = GetEncryptFunc()
    if not oEnfunc:
        ClearLPD()
        sLog = '加密函數號Error!!! %s' % g_CurVer
        LOG(sLog)
        return
    lst = GetFileData()
    lst = lst[-19:]
    for (idx, (_user, _pwd)) in enumerate(lst):
        if _user == user:
            lst.pop(idx)
            lst.append((user, pwd))
            break
    else:
        lst.append((user, pwd))

    data = GetEncryptData(lst)
    WriteLPD(data)
    return


def GetLocalPwd(user):
    pwd = ''
    for ret in GetFileData():
        if user == ret[0]:
            pwd = ret[1]
            break

    return pwd


def GetAllAcount():
    accountLst = set()
    for ret in GetFileData():
        accountLst.add(ret[0])

    return list(accountLst)


def ClearLPD():
    if os.path.isfile('lpd'):
        try:
            os.remove('lpd')
        except:
            pass

    if os.path.isdir('lpd'):
        try:
            os.rmdir('lpd')
        except:
            pass

    import gamedebug, sys
    s = gamedebug.GetSystrace()
    linenum = sys._getframe().f_back.f_lineno
    sLog = 'DecryptError:%s,line:%s' % (s, linenum)
    LOG(sLog)
    return


def MD5Zip(pwd):
    ret = ''
    for i in range(0, len(pwd), 2):
        ret += chr(int(pwd[i + 1] + pwd[i], 16))

    return ret


def Byte4ToNum(s):
    return (ord(s[0]) << 24) + (ord(s[1]) << 16) + (ord(s[2]) << 8) + ord(s[3])


def NumToByte4(n):
    return chr(n >> 24 & 255) + chr(n >> 16 & 255) + chr(n >> 8 & 255) + chr(n & 255)


def TEAEncrypt(plain, key):
    left = Byte4ToNum(plain)
    right = Byte4ToNum(plain[4:])
    a = Byte4ToNum(key)
    b = Byte4ToNum(key[4:])
    c = Byte4ToNum(key[8:])
    d = Byte4ToNum(key[12:])
    delta = 2654435769L
    sum = 0
    for i in xrange(16):
        sum += delta
        left += (right << 4) + a ^ right + sum ^ (right >> 5) + b
        left &= 4294967295L
        right += (left << 4) + c ^ left + sum ^ (left >> 5) + d
        right &= 4294967295L

    left = NumToByte4(left)
    right = NumToByte4(right)
    return left + right


def TEADecrypt(plain, key):
    left = Byte4ToNum(plain)
    right = Byte4ToNum(plain[4:])
    a = Byte4ToNum(key)
    b = Byte4ToNum(key[4:])
    c = Byte4ToNum(key[8:])
    d = Byte4ToNum(key[12:])
    delta = 2654435769L
    sum = delta << 4 & 4294967295L
    for i in xrange(16):
        right -= (left << 4) + c ^ left + sum ^ (left >> 5) + d
        right &= 4294967295L
        left -= (right << 4) + a ^ right + sum ^ (right >> 5) + b
        left &= 4294967295L
        sum -= delta
        sum &= 4294967295L

    left = NumToByte4(left)
    right = NumToByte4(right)
    return left + right


def TEAEncryptStr(plain, key):
    temp = ''
    plain = AddFill(plain)
    while plain:
        temp += TEAEncrypt(plain[:8], key)
        plain = plain[8:]

    return temp


def TEADecryptStr(plain, key):
    temp = ''
    while len(plain):
        temp += TEADecrypt(plain[:8], key)
        plain = plain[8:]

    temp = DelFill(temp)
    return temp


def GetDecryptKeys():
    achieve_lst = [
     AchieveType.WithZeroRights,
     AchieveType.UsingSmart,
     AchieveType.UsingSCSI,
     AchieveType.WithZeroRightsAndFlip,
     AchieveType.WithAdminRight]
    for achieve_type in achieve_lst:
        yield DriveIDKey(achieve_type)

    return


def TEA3EncryptStrWithRights(plain):
    key = DriveIDKey(AchieveType.WithZeroRights)
    tag = TEAEncryptStr(GAMETAG, key)
    import md5
    hashcode = md5.md5(plain).hexdigest()
    data = TEAEncryptStr('%s%s' % (hashcode, plain), key)
    result = '%c%s%s' % (len(tag), tag, data)
    return result


def TEA3DecryptStrWithRights(plain):
    iLen = ord(plain[0])
    plain = plain[iLen + 1:]
    for key in GetDecryptKeys():
        data = TEADecryptStr(plain, key)
        hashcode = data[:32]
        data = data[32:]
        if hashcode == md5.md5(data).hexdigest():
            return (
             data, key)

    return ('', '')


def AddFill(plain):
    fillnum = 8 - len(plain) % 8
    plain = chr(fillnum) + plain + ':' * (fillnum - 1)
    return plain


def DelFill(plain):
    fillnum = ord(plain[0])
    if fillnum == 1:
        fillnum = None
    else:
        fillnum = -fillnum + 1
    plain = plain[1:fillnum]
    return plain


def DriveIDKey(achieve_type):
    s = str(C_sys.GetDriveID(achieve_type)) + GAMETAG
    s = s[:16]
    s += '0' * (16 - len(s))
    return s


def GetFileData():
    global g_bOpenCache
    global g_iModifyTime
    global g_lstData
    lst = []
    if not os.path.isfile('lpd'):
        return lst
    try:
        iModifyTime = os.path.getmtime('lpd')
    except:
        g_bOpenCache = False
        iModifyTime = -1

    if g_bOpenCache and g_lstData and iModifyTime == g_iModifyTime:
        return g_lstData
    try:
        f = open('lpd', 'rb')
    except:
        LOG('lpd open file failed!!!')
        return lst

    data = f.read()
    f.close()
    try:
        lst = GetDecryptData(data)
    except Exception:
        ClearLPD()
        lst = []

    g_iModifyTime = iModifyTime
    g_lstData = lst
    return lst


def GetDecryptData(data):
    ver = ord(data[0])
    defunc = GetDecryptFunc(ver)
    if not defunc:
        return []
    import pyDes
    lst = []
    (data, key) = defunc(data[1:])
    key = key[:8]
    while data:
        (user, size, data) = data.split(':', 2)
        size = ord(size)
        pwd = data[:size]
        data = data[size:]
        pwd = pyDes.Decrypt(pwd, key)
        lst.append([user, pwd])

    return lst


def GetEncryptData(lst):
    import pyDes
    key = DriveIDKey(AchieveType.WithZeroRights)
    key = key[:8]
    result_lst = []
    for (user, pwd) in lst:
        pwd = pyDes.Encrypt(pwd, key)
        size = len(pwd)
        line = '%s:%c:%s' % (user, size, pwd)
        result_lst.append(line)

    data = ('').join(result_lst)
    efunc = GetEncryptFunc()
    data = efunc(data)
    return '%c%s' % (g_CurVer, data)


def WriteLPD(tempstr):
    try:
        os.popen('attrib -h lpd')
    except:
        pass

    try:
        lpd = open('lpd', 'wb')
        lpd.write(tempstr)
        lpd.close()
    except Exception, e:
        LOG('WriteLPD err ', e)
        ClearLPD()
        LOG('寫入密碼時失敗!!!')

    try:
        os.popen('attrib +h lpd')
    except:
        pass

    return


EncryptFunc = {TEA: TEAEncryptStr, 
   TEA3: TEA3EncryptStrWithRights}
DecryptFunc = {TEA: TEADecryptStr, 
   TEA3: TEA3DecryptStrWithRights}

def GetEncryptFunc():
    global EncryptFunc
    return EncryptFunc.get(g_CurVer)


def GetDecryptFunc(ver):
    global DecryptFunc
    return DecryptFunc.get(ver)


return
