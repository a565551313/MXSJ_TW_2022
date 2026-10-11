# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\misc.py
import time, pprint, sys, os.path, traceback, pubdelegate, pubvars, pubcore.pubfunc as pubfunc, pubcore, timer, function, pubnet, publog, pubcipher
from math import cos as Cos, sin as Sin, sqrt as Sqrt
import C_sys, C_object, re
try:
    from C_sys import UTF8_to_Unicode, Unicode_to_UTF8
except ImportError:
    UTF8_to_Unicode = lambda x: x
    Unicode_to_UTF8 = lambda x: x

RECENT_LOGIN_CC_EFFECT_TIME = 259200
g_Logger = publog.GetPubLogger(__name__)

def GetLan(_sText):
    return pubdelegate.GetLan(_sText)


def Time():
    t = C_sys.GetTimeIntervalSince1970()
    return t


CORRECT_ONCE = 4294967296L
SPILL_TEMPTIME = 604800000
g_ElapsedTimeCorrect = 0
g_LastElapsedTime = C_sys.GetSysElapsedRealTime()

def SysElapsedRealTime():
    global g_ElapsedTimeCorrect
    global g_LastElapsedTime
    if hasattr(C_sys, 'GetSysElapsedRealTime'):
        iCurElapedTime = C_sys.GetSysElapsedRealTime()
        if iCurElapedTime < g_LastElapsedTime and g_LastElapsedTime - iCurElapedTime > SPILL_TEMPTIME:
            g_ElapsedTimeCorrect += CORRECT_ONCE
            g_Logger.warn('时间溢出：%s, %s, %s', iCurElapedTime, g_LastElapsedTime, g_ElapsedTimeCorrect)
        iRealElapedTime = iCurElapedTime + g_ElapsedTimeCorrect
        g_LastElapsedTime = iCurElapedTime
        return iRealElapedTime / 1000.0
    return Time()


g_FirstCmp = Time() - SysElapsedRealTime()
g_Correct = 0.0

def GetRealTime():
    global g_Correct
    global g_FirstCmp
    fCurTime = g_Correct + Time()
    iCurBootTime = SysElapsedRealTime()
    fCur = fCurTime - iCurBootTime
    fCheck = g_FirstCmp - fCur
    if fCheck > 1 or fCheck < -1:
        g_Logger.debug('时间快/慢了%s,%s' % (g_Correct, fCheck))
        g_Correct += fCheck
        fCurTime = g_Correct + Time()
    return fCurTime


def _Str2Color(s):
    c = int(s)
    if c < 0:
        c = 0
    if c > 255:
        c = 255
    return c


def Str2Color(color):
    if type(color) == str:
        color = color.split()
    r = _Str2Color(color[0])
    g = _Str2Color(color[1])
    b = _Str2Color(color[2])
    if len(color) <= 3:
        return r * 65536 + g * 256 + b
    ret = [r * 65536 + g * 256 + b]
    if len(color) >= 6:
        r = _Str2Color(color[3])
        g = _Str2Color(color[4])
        b = _Str2Color(color[5])
        ret.append(r * 65536 + g * 256 + b)
    if len(color) >= 9:
        r = _Str2Color(color[6])
        g = _Str2Color(color[7])
        b = _Str2Color(color[8])
        ret.append(r * 65536 + g * 256 + b)
    return ret


def SB2DB(s):
    uStr = Decode(s)
    uDst = ''
    for uCh in uStr:
        iCode = ord(uCh)
        if iCode == 32:
            iCode = 12288
        elif 33 <= iCode <= 126:
            iCode += 65248
        uDst += unichr(iCode)

    return Encode(uDst)


D2SDICT = {12288: 32, 
   65287: 65287, 
   65288: 65288, 
   65289: 65289}

def DB2SB(s):
    uStr = Decode(s)
    uDst = ''
    for uCh in uStr:
        iCode = ord(uCh)
        if iCode in D2SDICT:
            iCode = D2SDICT[iCode]
        elif 65281 <= iCode <= 65374:
            iCode -= 65248
        uDst += unichr(iCode)

    return Encode(uDst)


def HasSpecialChar(name):
    SPECIAL = [
     ' ', '\u3000']
    Length = len(name)
    i = 0
    while i < Length:
        ch = name[i]
        ascii = ord(ch)
        if ascii > 128:
            i += 1
            ch = ch + name[i]
            ascii2 = ord(name[i])
            if ascii2 < 160:
                return True
            if ascii > 247 or ascii < 161 or 169 < ascii < 176:
                return True
        if ch in SPECIAL:
            return True
        i += 1

    return False


def IsAllSymbol(name):
    Length = len(name)
    i = 0
    while i < Length:
        ascii = ord(name[i])
        if ascii <= 128:
            if name[i].isalnum():
                return False
        else:
            i += 1
            ascii2 = ord(name[i])
            if 176 <= ascii <= 247 and ascii2 >= 160:
                return False
            if not ascii == 163 and 193 <= ascii2 <= 218 or 225 <= ascii2 <= 250:
                if 176 <= ascii2 <= 185:
                    return False
        i += 1

    return True


def GetCharList_GBK(strText):
    li = list(strText)
    theLen = len(strText)
    retList = []
    x = 0
    while x < theLen:
        if ord(li[x]) > 128:
            retList.append(strText[x:x + 2])
            x += 2
        else:
            retList.append(strText[x])
            x += 1

    return retList


def GetCharList_UTF8(strText):
    li = list(strText)
    theLen = len(strText)
    retList = []
    x = 0
    while x < theLen:
        os = 1
        if 192 <= ord(li[x]) <= 223:
            os = 2
        elif 224 <= ord(li[x]) <= 239:
            os = 3
        retList.append(strText[x:x + os])
        x += os

    return retList


def BitDataToList(_bitData, _nKeep=0, _bReverse=False):
    dataList = []
    i = 0
    while 1:
        if i >= _nKeep and 2 ** i > _bitData:
            break
        dataList.insert(0, _bitData & 1 << i != 0 and 1 or 0)
        i += 1

    if _bReverse:
        dataList.reverse()
    return dataList


def String2List(str):
    strLength = len(str)
    if strLength > 1 and 'default' not in str:
        tempStr = str
        listInfo = [int(i) for i in tempStr[1:strLength - 1].split(',')]
        return listInfo
    else:
        return


def String2TupleList(str):
    strLength = len(str)
    tupleList = []
    if strLength > 1 and 'default' not in str:
        tempStr = str
        for strTuple in tempStr[1:strLength - 2].split('),'):
            tempTuple = tuple([int(i) for i in strTuple[1:len(strTuple)].split(',')])
            tupleList.append(tempTuple)

    return tupleList


def String2QuadInfo(str):
    strLength = len(str)
    quadList = []
    if strLength > 1 and 'default' not in str:
        tempStr = str
        for quadStr in tempStr.split(';'):
            quadList.append(String2TupleList(quadStr))

    return quadList


def StringFormat2Html(sNeedFormatString):
    sFormatString = '<head>\n<meta charset = "UTF-8">\n</head><pre>'
    tNeedTransChar = (
     ('&', '&amp;'),
     ('"', '&quot;'),
     ('<', '&lt;'),
     ('>', '&gt;'),
     (' ', '&nbsp;'))
    for tTransChar in tNeedTransChar:
        sNeedFormatString = sNeedFormatString.replace(tTransChar[0], tTransChar[1])

    return sFormatString + sNeedFormatString


def CC_RADIANS_TO_DEGREES(angle):
    return angle * 57.29577951


def Ceil(value):
    result = int(value)
    if result == value:
        return result
    else:
        return result + 1


def Floor(value):
    result = int(value)
    return result


def Clamp(value, min, max):
    if max < value:
        return max
    else:
        if min > value:
            return min
        return value


def PCMP(_va, _vb, _e=0.01):
    dv = _va - _vb
    absdv = abs(dv)
    if absdv <= _e:
        return 0
    if dv > 0:
        return 1
    return -1


def Rand_int(a, b):
    if a == b:
        return a
    else:
        if a > b:
            return b + Rand(a - b + 1)
        return a + Rand(b - a + 1)


def Rand_List(ls):
    if ls and len(ls) > 0:
        return ls[Rand(len(ls))]
    else:
        return


def Rand(n):
    return int(C_sys.CCRANDOM_0_1() * n - 1e-10)


g_SysL2GameL = {'zh-Hans': 'zh_cn', 
   'zh-Hant': 'zh_tw', 
   'zh-HK': 'zh_tw', 
   'zh-TW': 'zh_tw', 
   'en': 'en_us', 
   'ja': 'ja_jp', 
   'ko': 'ko_kr', 
   'fi': 'fi_fi', 
   'da': 'da_dk', 
   'he': 'he_il', 
   'nl': 'nl_nl', 
   'pt': 'pt_pt', 
   'fr': 'fr_fr', 
   'es': 'es_es', 
   'de': 'de_de', 
   'ru': 'ru_ru', 
   'it': 'it_it', 
   'el': 'el_gr', 
   'no': 'no_no', 
   'cs': 'cs_cz', 
   'tr': 'tr_tr', 
   'hu': 'hu_hu', 
   'sl': 'sl_sl', 
   'pl': 'pl_pl', 
   'sv': 'sv_se', 
   'vi': 'vi_vn'}

def GetGameLanguage():
    sysLanguage = C_sys.GetSysLanguage()
    if sysLanguage.startswith('zh-Hans'):
        return 'zh_cn'
    else:
        if sysLanguage.startswith('zh-Hant'):
            return 'zh_tw'
        return g_SysL2GameL.get(sysLanguage, 'zh_cn')


UCS_BITS = 4

def Decode(s, sFormat='utf8'):
    if sFormat == 'utf8':
        sUni = UTF8_to_Unicode(s)
        idx = len(sUni) - 1
        sChList = []
        iCh = 0
        while idx >= 0:
            iCh <<= 8
            iCh |= ord(sUni[idx])
            if idx % UCS_BITS == 0:
                sChList.insert(0, Unichr(iCh))
                iCh = 0
            idx -= 1

        return ('').join(sChList)
    else:
        return s


def Encode(uni_s, sFormat='utf8'):
    if sFormat == 'utf8':
        sUniList = []
        for iCh in UnicodeGen(uni_s):
            idx = UCS_BITS
            while idx > 0:
                sUniList.append(chr(iCh & 255))
                iCh >>= 8
                idx -= 1

        s = Unicode_to_UTF8(('').join(sUniList))
        return s
    else:
        return uni_s


def Unichr(i):
    try:
        return unichr(i)
    except ValueError:
        return unichr(55296 + (i - 65536) // 1024) + unichr(56320 + (i - 65536) % 1024)


def UnicodeGen(us):
    i, n = 0, len(us)
    while i < n:
        cur = ord(us[i])
        if cur < 55296 or cur > 57343:
            yield cur
            i += 1
        else:
            yield (cur - 55296 << 10) + ord(us[i + 1]) - 56320 + 65536
            i += 2


def UCS4LittleEndianChr(i):
    t1, t2, t3, t4 = (
     i >> 24, (i & 16711680) >> 16,
     (i & 65280) >> 8, i & 255)
    return ('').join([chr(t1), chr(t2), chr(t3), chr(t4)])


def UCS2_to_UCS4(sRawUnicode):
    sNewUnicode = ''
    for i, c in enumerate(sRawUnicode):
        t = ord(c)
        iUnicode = ((t & 65280) >> 8 | (t & 255) << 8) << 16
        sNewUnicode += UCS4LittleEndianChr(iUnicode)

    return sNewUnicode


g_nPrintLevel = 0

def Get_NewPrint_Fmt(_info):
    return pprint.pformat(_info, indent=2)


def NewPrint(_info, _nLevel=0):
    global g_nPrintLevel
    if _nLevel < g_nPrintLevel:
        return
    print '********************' + '\n' + Get_NewPrint_Fmt(_info)
    print '********************'


def NewPrintLevelSetting(_nLv):
    global g_nPrintLevel
    g_nPrintLevel = _nLv


def PrintRunningStack():
    g_Logger.debug('=' * 40)
    g_Logger.debug('\tPrintRunningStack')
    g_Logger.debug('=' * 40)
    count = 1
    for sTrace in traceback.format_stack()[:-1]:
        ls = sTrace.split()
        sPath = './' + ('/').join(ls[1].strip()[1:-2].replace('\\', '/').split('/')[-3:]) + ' '
        sFmt = '>' * count + '> ' + sPath + (' ').join(ls[2:6])
        sFmt += '\n' + ' ' * (count + 0) + (' ').join(ls[6:])
        g_Logger.debug(sFmt + '\n')
        count += 1

    g_Logger.debug('=' * 40)
    g_Logger.debug('=' * 40)


def PrintExcLocals():
    tb = sys.exc_traceback
    while tb.tb_next is not None:
        tb = tb.tb_next

    try:
        ret = Get_NewPrint_Fmt(tb.tb_frame.f_locals)
        g_Logger.debug('=' * 40)
        g_Logger.debug('Local values:')
        g_Logger.debug(ret)
        g_Logger.debug('=' * 40)
    except:
        pass

    return


def IF_TRUE_A_B(_bJudge, _value_A, _value_B):
    if _bJudge:
        return _value_A
    return _value_B


def AllChildrenCall(_pParent, _pCall):
    for obj in _pParent.GetChildren():
        _pCall(obj)
        AllChildrenCall(obj, _pCall)


def GetAttribute(_sStr, _default=None):
    if not _sStr:
        return _default
    else:
        try:
            subMods = _sStr.split('.')
            nIdx = len(subMods)
            obj = None
            sModStr = _sStr
            while nIdx > 0:
                nIdx -= 1
                try:
                    obj = __import__(sModStr, fromlist=['*'])
                except ImportError:
                    sModStr = ('.').join(subMods[:nIdx])
                    continue
                else:
                    if nIdx != len(subMods) - 1:
                        for attr in subMods[nIdx + 1:]:
                            obj = getattr(obj, attr)

                    break

        except:
            traceback.print_exc()
            return _default

        return obj


def MD5(s, iLen=0):
    import hashlib
    md5pwd = hashlib.md5(s)
    if iLen:
        return md5pwd.hexdigest()[:iLen]
    else:
        return md5pwd.hexdigest()


def FileMD5(sFileName):
    import os.path, hashlib
    if not os.path.isfile(sFileName):
        return ''
    f = open(sFileName, 'rb')
    s = f.read()
    f.close()
    return hashlib.md5(s).hexdigest()


def GetIP():
    s = C_sys.GetLocalIP()
    try:
        lst = s.split('.')
        if len(lst) != 4:
            lst = (0, 0, 0, 0)
        else:
            lst = [int(x) for x in lst]
    except:
        lst = (0, 0, 0, 0)

    return lst


def GetEngineVersion():
    sVer = C_sys.GetEngineVersion()
    lst = sVer.split('.')
    try:
        default = [
         0, 0, 0]
        lst = [int(v) for v in lst]
        cnt = min(3, len(lst))
        for i in xrange(cnt):
            default[i] = lst[i]

        return tuple(default)
    except:
        return (0, 0, 0)


def GetAppVersion():
    if pubfunc.IsPC():
        sver = '100.0.0'
    else:
        sver = C_sys.GetAppVersion()
    lst = sver.split('.')
    try:
        default = [
         0, 0, 0]
        lst = [int(v) for v in lst]
        cnt = min(3, len(lst))
        for i in range(cnt):
            default[i] = lst[i]

        return tuple(default)
    except:
        return (0, 0, 0)


g_Plateform = None

def GetWindowsSYSVersion():
    global g_Plateform
    if g_Plateform == None:
        VER2SYS = {'10.0': '10', '6.3': '8.1', 
           '6.2': '8', 
           '6.1': '7', 
           '6.0': 'Vista', 
           '5.1': 'XP', 
           '5.0': '2000'}
        import os, re
        try:
            ver = os.popen('ver').read()
        except:
            g_Plateform = ''
            return g_Plateform

        patt = re.compile('[0-9]+.[0-9]+')
        verall = patt.findall(ver)
        for verstr in verall:
            if verstr:
                g_Plateform = VER2SYS.get(verstr.strip(), '')
                return g_Plateform

        g_Plateform = ''
        return g_Plateform
    else:
        return g_Plateform
        return


def GetPlatform():
    nType = C_sys.GetPlatformNum()
    return {0: 'UNKOWN', 1: 'IOS', 2: 'ANDROID', 3: 'PC'}.get(nType, 'Other')


def GetNetWorkType():
    nType = pubfunc.GetNetworkType()
    return {0: 'NO NETWORK', 1: 'WIFI', 2: '2G', 3: '3G', 4: '4G'}.get(nType, '')


GET_APK_SIGNATURES_ASYN_INTERVAL = 180
g_LastCallTime = 0
g_Infos = ''

def GetAPKSignaturesAsyn(pCallFunc):
    global g_Infos
    global g_LastCallTime
    if not pubfunc.IsAndroid():
        pFunctor = function.CFunctor(pCallFunc, '')
        timer.Timer(0, pFunctor)
    nCurTime = C_sys.GetTimeIntervalSince1970()
    if nCurTime - g_LastCallTime >= GET_APK_SIGNATURES_ASYN_INTERVAL:
        g_LastCallTime = nCurTime

        def cbFunc(sRet):
            global g_Infos
            g_Infos = sRet
            pCallFunc(sRet)

        C_sys.GetAPKSignaturesAsyn(cbFunc)
    else:
        pFunctor = function.CFunctor(pCallFunc, g_Infos)
        timer.Timer(0, pFunctor)


GET_APPLICATION_INTERVAL = 180
g_CurApplication = ['', 0]

def GetApplicationAppInfo():
    global g_CurApplication
    import os
    curTime = Time()
    if curTime - g_CurApplication[1] > GET_APPLICATION_INTERVAL:
        try:
            apl = os.listdir('Applications')
        except:
            apl = []

        if not apl:
            try:
                apl = os.listdir('./')
            except:
                apl = [
                 'nodata']

        apl.sort()
        sInfo = (',').join(apl)
        g_CurApplication = [sInfo, curTime]
    else:
        sInfo = g_CurApplication[0]
    return sInfo


def GetIniDirectory():
    path = C_sys.GetAppWorkPath()
    if pubfunc.IsPC():
        path = os.path.join(path, '../ini')
    else:
        path = os.path.join(path, 'ini/')
    return path


g_Tgid = '0'

def GetChannel(default='0'):
    global g_Tgid
    if g_Tgid == '0':
        sPath = os.path.join(GetIniDirectory(), 'tg.id')
        g_Tgid = C_sys.LoadFile(sPath)
        if g_Tgid:
            return g_Tgid
        return default
    if not g_Tgid:
        return default
    return g_Tgid


def GetDeviceID():
    if pubfunc.IsAndroid():
        return C_sys.GetAndroidId()
    else:
        return ''


def GetImei():
    imei = ''
    try:
        imei = C_sys.GetDeviceId()
    finally:
        return imei.upper()


def GetIDFA():
    if pubfunc.IsIOS():
        ver = C_sys.GetSysVersion()
        if ver:
            verlist = ver.split('.')
            if verlist and verlist[0].isdigit():
                if int(verlist[0]) < 6:
                    return ''
    if hasattr(C_sys, 'GetIDFA'):
        return C_sys.GetIDFA()
    return ''


def RemoveSelf(_Obj, _bAni=True):
    if _Obj and hasattr(_Obj, 'GetParent'):
        parent = _Obj.GetParent()
        if parent:
            parent.RemoveChild(_Obj, _bAni)


def DELAY_CALL(fDelayTime, pObj, sMethodName, *args, **kwargs):
    if fDelayTime < 0.001:
        getattr(pObj, sMethodName)(*args, **kwargs)
        return
    timer.Timer(fDelayTime, function.CFunctorByName(pObj, sMethodName, *args, **kwargs))


def GetServerTime():
    return pubvars.g_fServerTime + pubvars.g_fRunningTime


def GetSerLocalTime(t):
    temp2 = t + time.timezone - -28800
    temp3 = time.localtime(temp2)
    if int(temp3[-1]) == 1:
        temp2 -= 3600
        temp4 = time.localtime(temp2)
        if int(temp4[-1]) != 1:
            temp5 = list(temp3)
            temp5[3] -= 1
            return time.struct_time(temp5)
        return temp4
    else:
        return temp3


g_WorkingPath = os.path.normpath(C_sys.GetAppWorkPath())

def GetServerInfo(sServerIniPath=''):
    if not sServerIniPath:
        sServerIniPath = os.path.join(g_WorkingPath, 'ini/server.ini')
    try:
        data = pubcipher.LoadFile(sServerIniPath)
        rIp = re.compile('\\d{1,3}[.]\\d{1,3}[.]\\d{1,3}[.]\\d{1,3}')
        rPort = re.compile(' \\d+ ')
        rExp = re.compile('&| \\(.+\\)')
        rKey = re.compile('.+')
        qu_list = []
        key = None
        svr_list = []
        first_in = 1
        for line in data.split('\n'):
            if line.strip() == '':
                continue
            if line.strip().replace('=', '') == '':
                break
            l = line.split(' ')
            if rIp.search(line):
                kt = l[0]
                ip = port = exp = ''
                proxyip = proxyport = '0'
                for idx, mo in enumerate(rIp.finditer(line)):
                    if idx == 0:
                        ip = mo.group().strip()
                    elif idx == 1:
                        proxyip = mo.group().strip()

                for idx, mo in enumerate(rPort.finditer(line)):
                    if idx == 0:
                        port = mo.group().strip()
                    elif idx == 1:
                        proxyport = mo.group().strip()

                try:
                    exp = rExp.search(line).group()
                    exp = exp.strip()
                    if exp.find('(') == 0 and exp.find(')', -1) == len(exp) - 1:
                        exp = exp[1:-1]
                except:
                    exp = ''

                tmp = [
                 kt, ip, port, proxyip, proxyport, 
                 exp]
                svr_list.append(tmp)
            elif first_in == 1:
                first_in = 2
                key = rKey.search(line).group()
                continue
            qu_list.append({'name': key, 'svrlist': svr_list})
            key = rKey.search(line).group()
            svr_list = []

        qu_list.append({'name': key, 'svrlist': svr_list})
        return qu_list
    except Exception as e:
        return []

    return


def GetPushToken():
    if not hasattr(pubfunc.GetDirector(), 'getPushToken'):
        return 'FFFFFFFFFFFFFFFF'
    sToken = pubfunc.GetDirector().getPushToken()
    sToken = ('').join(sToken.replace('<', '').replace('>', '').split())
    return sToken


def GetEncryptPushToken():
    sToken = GetPushToken()
    skey = '1bec508e'
    sSecret = ''
    g_Logger.debug('====================')
    g_Logger.debug('获得Token...')
    if sToken:
        sSecret = C_sys.StrDesEncrypt(skey, sToken)
        g_Logger.debug('Token:%s' % sToken)
        g_Logger.debug('SecretToken:%s' % sSecret)
    else:
        g_Logger.debug('失败!')
    g_Logger.debug('====================')
    return sSecret


PI = 3.141592653589793

def Radians(_fDegrees):
    return PI * _fDegrees / 180.0


def Degrees(_fRadians):
    return int(_fRadians * 180.0 / PI + 0.5) % 360


def Rotate(_fAngle, _vPos):
    fRadian = Radians(_fAngle)
    _x = _vPos[0]
    _y = _vPos[1]
    x = _x * Cos(fRadian) - _y * Sin(fRadian)
    y = _x * Sin(fRadian) + _y * Cos(fRadian)
    return (int(x > 0 and x + 0.5 or x - 0.5), int(y > 0 and y + 0.5 or y - 0.5))


def RotateByOriPoint(_fAngle, _vBeginPos, _vOriPoint):
    vDelta = [_vBeginPos[i] - _vOriPoint[i] for i in range(2)]
    vPos = Rotate(_fAngle, vDelta)
    x, y = [vPos[i] + _vOriPoint[i] for i in range(2)]
    return (int(x > 0 and x + 0.5 or x - 0.5), int(y > 0 and y + 0.5 or y - 0.5))


def RotateByCosCyta(_cosCyta, _vPos, _nDir=1):
    _x = _vPos[0]
    _y = _vPos[1]
    sinCyta = Sqrt(1 - _cosCyta ** 2) * _nDir
    x = _x * _cosCyta - _y * sinCyta
    y = _x * sinCyta + _y * _cosCyta
    return (x, y)


def AngleIn360(_fAngle):
    if _fAngle >= 360:
        _fAngle -= 360
    elif _fAngle < 0:
        _fAngle += 360
    return _fAngle


def DistanceForAngle(_fAngle1, _fAngle2):
    _fAngle1 = AngleIn360(_fAngle1)
    _fAngle2 = AngleIn360(_fAngle2)
    dist = _fAngle1 - _fAngle2
    dist = abs(dist)
    if dist > 180:
        dist = 360 - dist
    return dist


def Dir(_ox, _oy, _nx, _ny):
    oDist = Sqrt(_ox ** 2 + _oy ** 2)
    oxNor = _ox / oDist
    oyNor = _oy / oDist
    nDist = Sqrt(_nx ** 2 + _ny ** 2)
    nxNor = _nx / nDist
    nyNor = _ny / nDist
    nDir = oxNor * nyNor - oyNor * nxNor
    if nDir >= 0:
        return True
    else:
        return False


def ConvertCoordinateFromOther(_vOriPoint, _vDirA, _vDirB):
    return Vector2(_vOriPoint.x * _vDirA.x + _vOriPoint.y * _vDirB.x, _vOriPoint.x * _vDirA.y + _vOriPoint.y * _vDirB.y)


def ConvertCoordinateFromNormal(_vOriPoint, _vDirA, _vDirB):
    return Vector2((_vDirB.y * _vOriPoint.x - _vDirB.x * _vOriPoint.y) / (_vDirA.x * _vDirB.y - _vDirA.y * _vDirB.x), (-_vDirA.y * _vOriPoint.x + _vDirA.x * _vOriPoint.y) / (_vDirA.x * _vDirB.y - _vDirA.y * _vDirB.x))


class Vector2(object):

    def __init__(self, _fX=0.0, _fY=0.0):
        self.x = _fX
        self.y = _fY

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        raise TypeError("unsupported operand type(s) for *: 'Vector2' and '%s'" % other)

    def Dot(self, other):
        return self.x * other.x + self.y * other.y

    def Cross(self, other):
        return self.x * other.y - other.x * self.y

    def Mod(self):
        return Sqrt(self.x * self.x + self.y * self.y)

    def Normalize(self):
        fMod = self.Mod()
        self.x /= fMod
        self.y /= fMod

    def __cmp__(self, other):
        return cmp((self.x, self.y), (other.x, other.y))


class Vector3(object):

    def __init__(self, _fX=0.0, _fY=0.0, _fZ=0.0):
        self.x = _fX
        self.y = _fY
        self.z = _fZ

    def __repr__(self):
        return '(%s, %s, %s)' % (self.x, self.y, self.z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        raise TypeError("unsupported operand type(s) for *: 'Vector3' and '%s'" % other)

    def Cross(self, other):
        a1, b1, c1 = self.x, self.y, self.z
        a2, b2, c2 = other.x, other.y, other.z
        return Vector3(b1 * c2 - b2 * c1, c1 * a2 - a1 * c2, a1 * b2 - a2 * b1)

    def __cmp__(self, other):
        return cmp((self.x, self.y, self.z), (other.x, other.y, other.z))


class CSection(object):
    sName = ''
    pServerList = []

    def SetData(self, **kwargs):
        self.sName = kwargs.get('name')
        self.pServerList = kwargs.get('svrlist')

    def GetData(self):
        return {'name': (self.sName), 'svrlist': (self.pServerList)}

    def __repr__(self):
        return '%s\n%s' % (self.sName, self.pServerList)


class CServer(object):
    sName = ''
    sIP = ''
    nPort = 0
    sProxyIP = ''
    nProxyPort = 0
    sExtraInfo = ''

    def SetData(self, tServerInfo):
        self.sName, self.sIP, nPort, self.sProxyIP, nProxyPort, self.sExtraInfo = tServerInfo
        self.nPort = int(nPort) if nPort.isdigit() else 0
        self.nProxyPort = int(nProxyPort) if nProxyPort.isdigit() else 0
        self.ParseExtraInfo()

    def ParseExtraInfo(self):
        return

    def GetData(self):
        return (
         self.sName, self.sIP, self.nPort, self.sProxyIP, self.nProxyPort, self.sExtraInfo)

    def __repr__(self):
        return (', ').join([str(i) for i in (self.sName, self.sIP, self.nPort, self.sProxyIP, self.nProxyPort, self.sExtraInfo)])


def MakeCompanyIP():
    IPDATA = [
     [
      121, 8, 235, 144, 29],
     [
      183, 6, 180, 224, 28],
     [
      58, 248, 14, 96, 27],
     [
      121, 201, 17, 8, 31],
     [
      121, 201, 17, 154, 31],
     [
      121, 201, 17, 156, 32],
     [
      113, 107, 234, 121, 32],
     [
      112, 73, 6, 217, 32],
     [
      182, 138, 101, 240, 31]]
    result = {}
    for iplist in IPDATA:
        if len(iplist) == 5:
            i1, i2, i3, i4, iMask = iplist
            if iMask > 24:
                iMask = 255 - (2 ** (8 - (iMask - 24)) - 1)
            else:
                continue
            ip = ((i1 * 256 + i2) * 256 + i3) * 256 + i4
            ip_mask = 4294967040L + iMask
            for j in range(1, 255):
                t = ((i1 * 256 + i2) * 256 + i3) * 256 + j
                if t & ip_mask == ip & ip_mask:
                    result['%s.%s.%s.%s' % (i1, i2, i3, j)] = 1

        else:
            i1, i2, i3, i4 = iplist
            result['%s.%s.%s.%s' % (i1, i2, i3, i4)] = 1

    return result


g_CompanyIP = MakeCompanyIP()

def IP2String(ip):
    sRet = ''
    for _ in xrange(4):
        if len(sRet):
            sRet += '.'
        sRet += '%d' % (ip % 256)
        ip /= 256

    return sRet


def String2IP(sIP):
    ip = 0
    info = sIP.split(',')
    if not len(info) == 4:
        return ip
    i1, i2, i3, i4 = [int(i) for i in info]
    ip = ((i1 * 256 + i2) * 256 + i3) * 256 + i4
    return ip


g_StartTime = 0

def RecordStartTime():
    global g_StartTime
    g_StartTime = SysElapsedRealTime()


def GetUseTime():
    curTime = SysElapsedRealTime()
    useTime = curTime - g_StartTime
    return useTime


g_QuoteMap = {}
_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict((a + b, chr(int(a + b, 16))) for a in _hexdig for b in _hexdig)

def Quote(s):
    global g_QuoteMap
    if not g_QuoteMap:
        STR_SAFE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-'
        for i in xrange(256):
            c = chr(i)
            g_QuoteMap[c] = c in STR_SAFE and c or '%%%02X' % i

    res = [g_QuoteMap[i] for i in s]
    return ('').join(res)


def UnQuote(s):
    res = s.split('%')
    if len(res) == 1:
        return s
    s = res[0]
    for item in res[1:]:
        try:
            s += _hextochr[item[:2]] + item[2:]
        except KeyError:
            s += '%' + item
        except UnicodeDecodeError:
            s += unichr(int(item[:2], 16)) + item[2:]

    return s


g_fLastPubLoopStartTime = GetRealTime()
g_fLastFrameUsedTime = 0
if GetEngineVersion() >= (3, 10, 185):
    g_bCanGetLastFrameDeltaTime = True
    g_fLastFrameDeltaTime = C_object.CDisplayLinkDirector.GetInstance().GetFrameDeltaTime()
else:
    g_bCanGetLastFrameDeltaTime = False
    g_fLastFrameDeltaTime = g_fLastPubLoopStartTime

def Loop():
    global g_fLastFrameDeltaTime
    global g_fLastFrameUsedTime
    global g_fLastPubLoopStartTime
    fCurTime = GetRealTime()
    g_fLastFrameUsedTime = fCurTime - g_fLastPubLoopStartTime
    g_fLastPubLoopStartTime = fCurTime
    if g_bCanGetLastFrameDeltaTime:
        g_fLastFrameDeltaTime = C_object.CDisplayLinkDirector.GetInstance().GetFrameDeltaTime()
    else:
        g_fLastFrameDeltaTime = g_fLastPubLoopStartTime


def GetLastFrameUsedTime():
    return g_fLastFrameUsedTime


def GetLastFrameDeltaTime():
    return g_fLastFrameDeltaTime


def GetLastPubLoopStartTime():
    return g_fLastPubLoopStartTime


def RegisterKeyboardListener():
    pEventListener = C_object.CEventListener(3, RegisterKeyboardListenerCB)
    pubfunc.GetDirector().AddEventListenerWithFixPriority(pEventListener, -1)


def RegisterKeyboardListenerCB(event, isPress, keyCode):
    global g_fLastPubLoopStartTime
    if keyCode == 202:
        g_fLastPubLoopStartTime = GetRealTime()


g_NetWorkSegment = None
g_CCName = ''
g_CCAccount = ''

def OnReceiveInfo(bSuccess, responseData, *arg):
    global g_NetWorkSegment
    try:
        s = pubcore.loads(responseData)
        g_NetWorkSegment = s['view']
    except Exception as e:
        g_Logger.error('OnReceiveInfo Exception%s' % e)
        g_NetWorkSegment = '公网'


def CheckNetWorkSegment():
    url = 'http://wd.2980.com/'
    timeout = 5
    callback = function.CreateFunctor(OnReceiveInfo)
    pubnet.Get(url, {}, timeout, callback)


def GetNetWorkSegment():
    return g_NetWorkSegment


def GetCCAccount():
    global g_CCAccount
    if not pubcore.IsPC():
        g_CCAccount = C_sys.LoadUserData('check_duoyi_account')
    return g_CCAccount


def ReadFile(filename, mode):
    f = open(filename, mode)
    fileContent = f.read()
    f.close()
    return fileContent


def GetCCName():
    global g_CCName
    return g_CCName


def CCCallBack(bSuccess, result, *arg):
    global g_CCAccount
    global g_CCName
    import pubjson
    try:
        if bSuccess:
            result = pubcore.loads(result)
            if 'data' in result.keys():
                if result['data']:
                    if pubjson.g_JsonLib:
                        g_CCName = UnQuote(result['data'][0]['nick'])
                        g_CCAccount = result['data'][0]['mail']
                    else:
                        sUCS4Unicode = UCS2_to_UCS4(result['data'][0]['nick'])
                        g_CCName = UnQuote(C_sys.Unicode_to_UTF8(sUCS4Unicode))
                        g_CCAccount = result['data'][0]['mail']
                else:
                    g_CCName = ''
                    g_CCAccount = ''
            else:
                g_CCName = ''
                g_CCAccount = ''
        else:
            g_CCName = ''
            g_CCAccount = ''
    except Exception as e:
        traceback.print_exc()
        pubcore.EmitErrorPush()
        g_CCName = ''
        g_CCAccount = ''


def InitCCName():
    url = 'http://localhost:38700/GetOnLineList'
    timeout = 5
    callback = function.CreateFunctor(CCCallBack)
    pubnet.Get(url, {}, timeout, callback)


def IsLoginCCRecent(cbOnGetRecentLoginCC, iEffectTime=RECENT_LOGIN_CC_EFFECT_TIME):
    if pubcore.IsPC() or pubcore.IsMac():

        def OnGetOnlineList(bSuccess, sData, *args):
            g_Logger.debug('OnGetOnlineList:%s, data=%s, %s', bSuccess, sData, args)
            if bSuccess:
                d = pubcore.loads(sData)
                if d:
                    l = d.get('data', [])
                    if l and l[0].get('mail'):
                        cbOnGetRecentLoginCC(True, l[0].get('mail'))
                        return
            cbOnGetRecentLoginCC(False, '')

        sUrl = 'http://localhost:38700/GetOnLineList'
        pubnet.Get(sUrl, {}, 5, OnGetOnlineList)
    elif pubcore.IsIOS():
        bInstllCC = C_sys.CanOpenUrl('calltoimccQYB://')
        cbOnGetRecentLoginCC(bool(bInstllCC), '')
    else:
        sCCAccount = C_sys.LoadUserData('check_duoyi_account', coreData=False)
        sLastLoginTime = C_sys.LoadUserData('check_duoyi_login_time', coreData=False)
        iCurTime = pubdelegate.GetServerTime()
        g_Logger.debug('GetCCAccount:%s, %s, %s', sCCAccount, sLastLoginTime, iCurTime)
        if not sCCAccount or not sLastLoginTime:
            cbOnGetRecentLoginCC(False, '')
            return
        iLastTime = int(sLastLoginTime)
        if iCurTime - iLastTime > iEffectTime:
            cbOnGetRecentLoginCC(False, '')
            return

        def OnCheckAccountCB(bSuccess, sData, *args):
            g_Logger.debug('OnCheckAccountCB:%s, data=%s, %s', bSuccess, sData, args)
            if bSuccess:
                if '-1' not in sData and '-2' not in sData and '-32' not in sData:
                    cbOnGetRecentLoginCC(True, sCCAccount)
                    return
            cbOnGetRecentLoginCC(False, '')

        sUrl = 'https://im.2980.com:10011/game_check_account?name=%s' % sCCAccount
        pubnet.Get(sUrl, {}, 5, OnCheckAccountCB)


def InitPubDataPath():
    pubvars.g_PubDataDirPath = 'pubdata'
    sRoot = os.path.join(C_sys.GetAppWorkPath(), pubvars.g_PubDataDirPath)
    if not os.path.exists(sRoot):
        try:
            os.makedirs(sRoot)
        except OSError as e:
            print 'ERROR：', e
            return

    pubvars.g_PubIniDirPath = os.path.join(pubvars.g_PubDataDirPath, 'ini')
    iniRoot = os.path.join(sRoot, 'ini')
    if not os.path.exists(iniRoot):
        os.makedirs(iniRoot)
    pubvars.g_PubIniPath = os.path.join(pubvars.g_PubIniDirPath, 'pub.ini')
    sPubIniFilePath = os.path.join(iniRoot, 'pub.ini')
    if not os.path.exists(sPubIniFilePath):
        f = open(sPubIniFilePath, 'w')
        f.close()


def IsGtEngineVersion(version):
    sVersion = C_sys.GetEngineVersion()
    strList = sVersion.split('.')
    sVersion = ''
    for item in strList:
        sVersion += item

    return int(sVersion) > version


MAXLINESIZE = 76
MAXBINSIZE = MAXLINESIZE // 4 * 3

def Base64EncodeString(s):
    import binascii
    pieces = []
    for i in range(0, len(s), MAXBINSIZE):
        chunk = s[i:i + MAXBINSIZE]
        pieces.append(binascii.b2a_base64(chunk))

    return ('').join(pieces).replace('\r', '').replace('\n', '')


def Base64DecodeString(s):
    import binascii
    return binascii.a2b_base64(s)


def IsGameRegionTW():
    if pubdelegate.GetGameRegion() == 'tw':
        return True
    return False


def IsGameRegionHK():
    if pubdelegate.GetGameRegion() == 'hk':
        return True
    return False


def IsGameRegionMO():
    if pubdelegate.GetGameRegion() == 'mo':
        return True
    return False
