# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\pubscript\pubdylogin.py


def GetHeader(header_type):
    import imnet
    shareobj = imnet.g_Net
    if shareobj:
        shareobj.PacketPrepare(header_type)
    return shareobj
    raise '遊戲向益網發送協議的協議頭，各項目各自實現'


def C2SLoginCallbackValue(login_callback_value):
    import imshare
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.LOGINCALLBACK)
    netobj.PacketAddUniS(login_callback_value)
    SendNetObj(netobj)
    LOG_DEBUG('通知戰盟登錄')
    return


def C2SLocalPwd(account, pwd):
    import imshare
    hex_pwd = Str2Hex(pwd)
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.GAME_START_YW)
    netobj.PacketAddUniS(account)
    netobj.PacketAddUniS(hex_pwd)
    SendNetObj(netobj)
    return


def SendLocalPwd(account, pwd):
    if not CanUseNewVersion():
        return
    if not CanGameStartYW():
        return
    C2SLocalPwd(account, pwd)
    return


def C2SStartResPatch():
    import imshare
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.STARTRESPACTH)
    MXTAG = 1
    netobj.PacketAddI(MXTAG)
    SendNetObj(netobj)
    return


def C2IMMultiDownload(sVersion, dDownloadList):
    """
        :param list dDownloadList: [{ "url":xxx, "dir":xxx, "md5"::xxx, "ver":xxx}, ]
        """
    import imshare
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.MULTIDOWNLOAD)
    dParams = {'gameid': 23, 
       'ver': sVersion, 
       'task': dDownloadList}
    print dParams
    netobj.PackAddJsonS(dParams)
    SendNetObj(netobj)
    LOG('請求下載', sVersion)
    return


def C2IMCanrt}\d}tiDownload():
    import imshare
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.CANCELMULTIDOWNLOAD)
    netobj.PacketAddI(23)
    SendNetObj(netobj)
    LOG('請求取消下載')
    return


def SendNetObj(netobj):
    netobj.PacketSend()
    return


def S2CAccountPwd(netobj):
    account = netobj.UnpackUniString()
    pwd = netobj.UnpackUniString()
    is_lpd = netobj.UnpackUInt()
    OnReceiveAccountPwd(account, pwd, is_lpd)
    return


def OnReceiveAccountPwd(account, pwd, is_lpd):
    import loginin
    if is_lpd:
        hex_pwd = pwd
        pwd = Hex2Str(hex_pwd)
    CYWLoginInfoMgr.SetOneOff(account, pwd)
    CYWLoginInfoMgr.SetIsLocalPwd(is_lpd)
    if loginin.IsShowAutoLogin():
        loginin.DYAutoLogin2(account, pwd, is_lpd)
    else:
        import selectserver
        loginin.Show(False)
        selectserver.Refresh(None)
        selectserver.SetOneOffLogin(True)
    return
    raise '收到益網發送的帳號和加密後的密碼，各項目各自實現'


def C2SSendAccounts(sAccounts):
    import imshare
    netobj = GetHeader(imshare.GAME2IMAUDIOROOM.SETACCOUNTS)
    if not netobj:
        return
    netobj.PacketAddUniS(sAccounts)
    SendNetObj(netobj)
    print '發送帳號列表給戰盟', sAccounts
    return


def OnSendSaveAccounts():
    if not CanSendAccounts():
        return
    sAccount = GetSendAccounts()
    if not sAccount:
        print '沒有保存密碼的帳號'
        return
    C2SSendAccounts(sAccount)
    return


def GetSendAccounts():
    import loginin, cfg, re, re
    patt = re.compile('^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$')
    sAccounts = ''
    for user in loginin.GetAccountList():
        if not patt.match(user) and not (user.isdigit() and len(user) == 11):
            continue
        if cfg.GetData('mx.ini', user, 'savepwd') == '1':
            sAccounts += user + ';'

    return sAccounts[:-1]
    raise "獲取保存密碼的帳號列表,以';'分隔，如'1111@qq.com;2222@qq.com'"


def CanSendAccounts():
    import pubimtools
    if pubimtools.GetVersion() < (0, 5, 56):
        print '校驗戰盟版本不符', pubimtools.GetVersion()
        return False
    if not pubimtools.IsImRunning() or not pubimtools.IsOnLine():
        print '戰盟不在線'
        return False
    return True
    raise '是否發送帳號列表'


def CanUseNewVersion():
    import imnet
    return imnet.CanUseNewVersion()


def CanGameStartYW():
    return True
    raise '是否啟用 遊戲登錄時若益網離線則啟動益網 功能'


def Str2Hex(text):
    import binascii
    int_text = binascii.b2a_hex(text)
    return int_text


def Hex2Str(hex_text):
    import binascii
    str_text = binascii.a2b_hex(hex_text)
    return str_text


def CmdParam(p):
    dct = ParseCmdParam(p)
    if dct.has_key('戰盟推廣ID'):
        import clientinterface
        ywtgid = dct['戰盟推廣ID']
        clientinterface.CheckTGIDFromYW(ywtgid)
        print '解析ywtgid：', ywtgid
    if dct.has_key('戰盟版本'):
        print '解析ywversion：', dct['戰盟版本']
    if dct.has_key('戰盟新版登錄') and dct['戰盟新版登錄']:
        CYWLoginInfoMgr.SetDYLoginKey(dct['戰盟登錄校驗值'])
    if dct.has_key('選擇服務器ID'):
        CYWLoginInfoMgr.SetServerID(dct['選擇服務器ID'])
    account, pwd = dct.get('戰盟登錄帳號'), dct.get('戰盟登錄密碼')
    if not (account and pwd):
        print '密碼解析錯誤，自動登錄失敗'
        return
    CYWLoginInfoMgr.SetOneoffName(account)
    CYWLoginInfoMgr.SetOneoffPwd(pwd)
    return


def ParseCmdParam(p):
    dct = {}
    if not p.startswith('@'):
        return dct
    import base64
    p = base64.b64decode(p[1:])
    yw_info = ParseYWInfo(p)
    if yw_info:
        (dct['戰盟推廣ID'], dct['戰盟版本']) = yw_info
    (account, pwd) = ParseAccountAndPwd(p)
    if account and pwd:
        dct['戰盟登錄帳號'] = account
        dct['戰盟登錄密碼'] = pwd
        SaveAccout(account)
    serverid = ParseServerID(p)
    if serverid:
        dct['選擇服務器ID'] = serverid
    login_callback_value = ParseLoginCallbackValue(p)
    if login_callback_value:
        dct['戰盟登錄校驗值'] = login_callback_value
        dct['戰盟新版登錄'] = True
    return dct


def SaveAccout(sAccount):
    import toolkit
    toolkit.SaveAccount(sAccount)
    return


def ParseYWInfo(p):
    import re
    patt_yw = re.compile('.*tgid=(?P<ywtgid>[0-9]+)&version=(?P<ywversion>[0-9\\.]+)')
    mobj_yw = patt_yw.match(p)
    if mobj_yw:
        return (
         mobj_yw.group('ywtgid'), mobj_yw.group('ywversion'))
    return


def ParseAccountAndPwd(p):
    import re
    patt_dy = re.compile('.*token=(?P<oneoffname>[\\w\\W\\@\\_\\.\\-]+)&code=(?P<oneoffpwd>[a-zA-Z0-9]+)')
    mobj = patt_dy.match(p)
    if mobj:
        account, pwd = mobj.group('oneoffname'), mobj.group('oneoffpwd')
        pwd = DecryptString(pwd)
        return (account, pwd)
    return (None, None)


def ParseLoginCallbackValue(p):
    import re
    patt = re.compile('.*logincallback=(?P<value>[^&]+)')
    mobj = patt.match(p)
    if mobj:
        return mobj.group('value')
    return


def ParseServerID(p):
    import re
    patt = re.compile('.*gameserverid=(?P<iServerID>[0-9]+)')
    mobj = patt.match(p)
    if mobj:
        return mobj.group('iServerID')
    return


def DecryptString(inputstr):
    import misc, time
    t = int(time.time() / 30)
    mac = misc.GetMAC().lower()
    key = 'YIWANGMAGIC'
    for tm in (t, t - 1):
        result = _DecryptString(inputstr, mac, tm)
        if result and result.startswith(key):
            return result[len(key):]

    return


def _DecryptString(to_dec, mac_key, time_key):
    dec_len = len(to_dec)
    mac_len = len(mac_key)
    arr = []
    j = 0
    i = 0
    while i < dec_len - 1:
        low = int(to_dec[i], 16)
        i = i + 1
        high = int(to_dec[i], 16)
        i = i + 1
        ch = low * 16 + high
        mc = mac_key[j % mac_len]
        cr = ch ^ ord(mc)
        cr = cr ^ time_key & 255
        cr = cr ^ time_key >> 8 & 255
        j = j + 1
        arr.append(chr(cr))

    return ('').join(arr)


class CYWLoginInfoMgr(object):
    m_Oneoff_Name = None

    @classmethod
    def SetOneoffName(cls, name):
        cls.m_Oneoff_Name = name
        return

    @classmethod
    def IsOneoff(cls):
        return cls.m_Oneoff_Name != None

    m_Oneoff_Pwd = None

    @classmethod
    def SetOneoffPwd(cls, pwd):
        cls.m_Oneoff_Pwd = pwd
        return

    m_IslocalPwd = False

    @classmethod
    def SetIsLocalPwd(cls, islocal):
        cls.m_IslocalPwd = islocal
        return

    @classmethod
    def GetIslocalPwd(cls):
        return cls.m_IslocalPwd

    @classmethod
    def SetOneOff(cls, name, pwd):
        cls.m_Oneoff_Name = name
        cls.m_Oneoff_Pwd = pwd
        return

    @classmethod
    def GetOneoff(cls):
        return (cls.m_Oneoff_Name, cls.m_Oneoff_Pwd)

    m_DYLoginKey = None

    @classmethod
    def SetDYLoginKey(cls, dyLoginKey):
        cls.m_DYLoginKey = dyLoginKey
        return

    @classmethod
    def GetDYLoginKey(cls):
        return cls.m_DYLoginKey

    m_ServerID = 0

    @classmethod
    def SetServerID(cls, sServerID):
        if sServerID:
            cls.m_ServerID = int(sServerID)
        return

    @classmethod
    def GetServerID(cls):
        return cls.m_ServerID

    @classmethod
    def ClearCmdParam(cls):
        cls.m_DYLoginKey = None
        cls.m_Oneoff_Name = None
        cls.m_Oneoff_Pwd = None
        cls.m_IslocalPwd = False
        return


return
