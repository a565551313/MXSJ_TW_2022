# pycdc 交叉复核产物 · script.fls entry 4960
# co_filename(原始)='script/pubscript/pubregister/pubactfunction.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4960.pyc (Python 2.5)

import net
import interface
import pubmisc
import pubtoolkit
import pubregisterbase
g_Cookie = ''

def GetCookie():
    return g_Cookie


class CHttpObject(net.CHttpObject):
    
    def __init__(self, url, method, cookie, callback, *arg):
        self.m_Callback = callback
        self.m_Arg = arg
        import whitewebsite
        if not whitewebsite.CheckUrlIsInWhite(url):
            return None
        
        (server, port, file) = net.GetUrlInfo(url)
        net.CNetClient.__init__(self)
        self.Connect(server, port)
        header = self.GetHeader(file, server, cookie)
        self.NakedSend(header)
        self.m_Data = ''
        
        def NetProcess(obj):
            data = self.Process()
            if data:
                self.m_Data += data
            
            return ()

        self.m_Timer = interface.CBaseObject(None)
        self.m_Timer.CreatePyCommand(0, NetProcess)
        net.g_HttpObjectList.append(self)

    
    def GetHeader(self, filename, hoststr, cookie):
        if cookie and isinstance(cookie, str):
            cookie = 'Cookie: %s\r\n' % cookie
        else:
            cookie = ''
        header = 'GET %s HTTP/1.1\r\n' % filename + 'Host: %s\r\n' % hoststr + cookie + 'Connection: Close\r\n' + '\r\n'
        return header



class CMgr(pubregisterbase.CMgrBase):
    
    def GetSucCallFunc(self, op_type):
        raise '\xbe\xde\xa7@\xa6\xa8\xa5\\\xa6^\xbd\xd5\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def GetFailCallFunc(self, op_type):
        raise '\xbe\xde\xa7@\xa5\xa2\xb1\xd1\xa6^\xbd\xd5\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def OnConnectFail(self, op_type, *args):
        raise '\xb5\xf9\xa5U\xb3s\xb1\xb5\xa5\xa2\xb1\xd1\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def OnReceiveNoData(self, op_type, *args):
        raise '\xb5\xf9\xa5U\xb3s\xb1\xb5\xa5\xa2\xb1\xd1\xa1A\xa8S\xa6\xb3\xbc\xc6\xbe\xda\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def OnParseFail(self, op_type, data, *args):
        raise '\xb8\xd1\xaaR\xbc\xc6\xbe\xda\xa5X\xbf\xf9\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def GetGameGate(self):
        raise 'CRegisterHttp\xb5\xf9\xa5U\xae\xc9\xa5\xce\xa8\xec\xaa\xbagate\xad\xc8\xa1A\xbd\xd0\xbbP\xba\xf4\xaf\xb8\xa6P\xa8\xc6\xae\xd6\xb9\xea\xab\xe1\xb6\xf1\xbcg\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def GetUrl(self, path, **dct):
        import pubgameurl
        import pubtoolkit
        if pubtoolkit.~D~YYer():
            urlarea = 'if2017\xa4\xba\xba\xf4'
        elif pubmisc.IsTest():
            urlarea = 'if2017\xa5~\xb4\xfa'
        else:
            urlarea = 'if2017'
        urlbase = pubgameurl.GetIf2017Url(urlarea, path, **dct)
        raise '\xc3\xec\xb1\xb5\xba\xf4\xa7}\xabe\xba\xf3\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{'

    
    def GetPhoneCode(self, phone, country, account, *args):
        self.Send(self.OP_PHONE_CODE, self.GetGameGate(), phone, country, account, self.OP_PHONE_CODE, *args)

    
    def ShowPhoneCode(self, phone, country, account, *args):
        self.Send(self.OP_CHECK_CODE, self.GetGameGate(), phone, country, account, self.OP_CHECK_CODE, *args)

    
    def GetPhoneVoice(self, phone, country, account, *args):
        self.Send(self.OP_PHONE_VOICE, self.GetGameGate(), phone, country, account, self.OP_PHONE_VOICE, *args)

    
    def DoGetPassByMail(self, email, *args):
        self.Send(self.OP_PWD_EMAIL, self.GetGameGate(), email, *args)

    
    def DoGetPassByPhone(self, account, Phone, country, smscode, newpass, *args):
        self.Send(self.OP_PWD_PHONE, account, Phone, country, smscode, newpass, *args)

    
    def DoGetImgCode(self, *args):
        self.Send(self.OP_IMG_CODE, *args)

    
    def DoGetBindInfo(self, account, smscode, vkey, *args):
        self.Send(self.OP_BIND_INFO, account, self.GetGameGate(), smscode, vkey, *args)

    
    def DoGetActByPhone(self, phone, country, smscode, *args):
        self.Send(self.OP_GET_ACCOUNT, phone, country, smscode, *args)

    
    def DoReSend(self, email, *args):
        self.Send(self.OP_RESEND_EMAIL, email, *args)

    OP_PHONE_CODE = 1
    OP_SHOW_CODE = 2
    OP_PHONE_VOICE = 3
    OP_PWD_EMAIL = 4
    OP_PWD_PHONE = 5
    OP_IMG_CODE = 6
    OP_BIND_INFO = 7
    OP_GET_ACCOUNT = 8
    OP_RESEND_EMAIL = 9
    
    def GetHttpCls(self, op_type):
        dct = {
            self.OP_PHONE_CODE: CPhoneCodeHttp,
            self.OP_SHOW_CODE: CShowCodeHttp,
            self.OP_PHONE_VOICE: CPhoneVoiceHttp,
            self.OP_PWD_EMAIL: CPwdEmailHttp,
            self.OP_PWD_PHONE: CPwdPhoneHttp,
            self.OP_IMG_CODE: CGetImgHttp,
            self.OP_BIND_INFO: CGetBindInfoHttp,
            self.OP_GET_ACCOUNT: CGetActByPhoneHttp,
            self.OP_RESEND_EMAIL: CReSendHttp }
        return dct[op_type]

    
    def ProcessCheckCodeData(self, imgbytes, path):
        import os
        import time
        import random
        
        try:
            os.makedirs(path)
        except BaseException:
            pass

        timetxt = '%d%02d%02d-%02d%02d%02d' % time.localtime()[:6]
        r = random.randint(0, 9)
        fname = '%s%s.jpg' % (str(r), timetxt)
        
        try:
            import base64
            sDecoded = base64.b64decode(imgbytes)
            f = open(path + '\\' + fname, 'wb')
            f.write(sDecoded)
            f.close()
        except Exception:
            e = None
            print 'Load CodeImg Err:', e
            fname = None

        return fname



class CCodeHttpBase(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, gate, mobile, country, account, mode, *args):
        dct = {
            'gate': gate,
            'phone': mobile,
            'type': mode,
            'scene': 4 }
        self.m_Path = '/common/send_smscode'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            -1000: '\xb2\xa7\xb1`\xa1A\xb5o\xb0e\xa5\xa2\xb1\xd1',
            10132: '\xbd\xd0\xad\xab\xb7s\xc0\xf2\xa8\xfa\xb5u\xabH\xc5\xe7\xb5\xfd\xbdX',
            10201: '\xb5u\xabH\xc3\xfe\xab\xac\xbf\xf9\xbb~',
            10205: '\xa4\xe2\xbe\xf7\xb8\xb9\xae\xe6\xa6\xa1\xbf\xf9\xbb~',
            10233: '\xa4\xe2\xbe\xf7\xb8\xb9\xb6W\xae\xc9\xb7\xed\xa4\xe9\xb5o\xb0e\xad\xad\xa8\xee' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CPhoneCodeHttp(CCodeHttpBase):
    pass


class CPhoneVoiceHttp(CCodeHttpBase):
    pass


class CShowCodeHttp(CCodeHttpBase):
    pass


class CPwdEmailHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, gate, email, *args):
        dct = {
            'acct': email,
            'gate': gate }
        self.m_Path = '/urs/get_pwd_by_mail'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            10300: '\xb1b\xb8\xb9\xa4\xa3\xa6s\xa6b',
            10323: '\xa7\xe4\xa6^\xb1K\xbdX\xa4\xd3\xb9L\xc0W\xc1c',
            10324: '\xc0\xf2\xa8\xfa\xb1b\xb8\xb9\xabH\xae\xa7\xa5\xa2\xb1\xd1',
            10520: '\xb6l\xa5\xf3\xa5\xbc\xb8j\xa9wqq',
            10522: '\xb6l\xbdc\xa5\xbc\xb3]\xb8m\xb8j\xa9w\xb6l\xbdc' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CPwdPhoneHttp(pubregisterbase.CHttpBase):
    ERR_MSG = {
        10300: '\xb1b\xb8\xb9\xa4\xa3\xa6s\xa6b',
        10302: '\xb1b\xb8\xb9\xae\xe6\xa6\xa1\xbf\xf9\xbb~',
        10324: '\xc0\xf2\xa8\xfa\xb1b\xb8\xb9\xabH\xae\xa7\xa5\xa2\xb1\xd1',
        10327: '\xa4\xa3\xaf\xe0\xad\xd7\xa7\xef\xac\xb0\xad\xec\xa6\xb3\xb1K\xbdX',
        10351: '\xa4\xe2\xbe\xf7\xb8\xb9\xbbP\xb3q\xa6\xe6\xb5\xfd\xa4w\xc3\xf6\xc1p\xa6\xfd\xa5\xbc\xa5\xcd\xae\xc4',
        10350: '2980\xb1b\xb8\xb9\xbd\xd0\xa8\xec2980\xb6l\xbdc\xbe\xde\xa7@',
        10356: '\xb8\xd3\xbd\xe3\xb8\xb9\xa5\xbc\xb8j\xa9w\xa4\xe2\xbe\xf7',
        10357: '\xb1b\xb8\xb9\xbbP\xa4\xe2\xbe\xf7\xb8\xb9\xa4\xa3\xa4\xc7\xb0t',
        10131: '\xb5u\xabH\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~',
        10132: '\xbd\xd0\xad\xab\xb7s\xc0\xf2\xa8\xfa\xb5u\xabH\xc5\xe7\xb5\xfd\xbdX' }
    
    def __init__(self, mgr, op_type, account, mobile, country, smscode, newpass, *args):
        dct = {
            'acct': account,
            'phone': mobile,
            'pass': pubregisterbase.EncryptPwd(newpass),
            'smscode': smscode }
        if country:
            dct['country'] = country
        
        self.m_Path = '/urs/modify_password_by_mobile'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = self.ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CGetImgHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, *args):
        dct = {
            'smallsize': '1' }
        self.m_Path = '/urs/get_imgcode'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def Send(self):
        if self.DEBUG:
            print self.m_Url, 'Do Send', self.__class__.__name__
        
        self.m_HttpObj = CHttpObject(self.m_Url, 'get', GetCookie(), self.m_Mgr.OnReceive, self.m_Type)

    
    def ProcessHeader(self, header):
        global g_Cookie
        for line in header.split('\r\n'):
            if line.startswith('Set-Cookie: '):
                idx = len('Set-Cookie: ')
                g_Cookie = line[idx:]
                continue
        

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            10103: '\xb0\xd1\xbc\xc6\xaf\xca\xa5\xa2\xa1A\xbb\xdd\xadn\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX',
            10102: '\xbd\xd0\xad\xab\xb7s\xc0\xf2\xa8\xfa\xc5\xe7\xb5\xfd\xbdX\xa1]\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xb9L\xb4\xc1\xa9\xce\xa8\xe4\xa5L\xb0\xdd\xc3D\xbe\xc9\xadP\xa1^',
            10101: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CGetBindInfoHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, account, gate, smscode, vkey, *args):
        dct = {
            'acct': account,
            'gate': gate,
            'vcode': smscode,
            'vkey': vkey,
            'smallsize': '1' }
        self.m_Path = '/game/urs/get_pass_method'
        dct['sign'] = pubmisc.GetAccountSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def Send(self):
        if self.DEBUG:
            print self.m_Url, 'Do Send', self.__class__.__name__
        
        self.m_HttpObj = CHttpObject(self.m_Url, 'get', GetCookie(), self.m_Mgr.OnReceive, self.m_Type)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            -91: '\xa5\xbc\xaa\xbe\xa8t\xb2\xce\xbf\xf9\xbb~(-91)',
            -93: '\xc3\xb1\xa6W\xc5\xe7\xb5\xfd\xa5\xa2\xb1\xd1',
            10000: '\xaf\xca\xa4\xd6\xa5\xb2\xb6\xb7\xb0\xd1\xbc\xc6',
            10001: '\xb0\xd1\xbc\xc6\xa4\xba\xaee\xa4\xa3\xa6X\xaak',
            10101: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~',
            10102: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xa4w\xb9L\xb4\xc1',
            10103: '\xbb\xdd\xadn\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX',
            10300: '\xb1b\xb8\xb9\xa4\xa3\xa6s\xa6b',
            10324: '\xc0\xf2\xa8\xfa\xb1b\xb8\xb9\xabH\xae\xa7\xa5\xa2\xb1\xd1',
            10360: '\xbd\xd0\xa8\xcf\xa5\xce\xa6r\xa5\xc0\xb1b\xb8\xb9\xa7\xe4\xa6^\xb1K\xbdX',
            10365: '\xa5\xbc\xb3]\xb8m\xb8j\xa9w\xb6l\xbdc\xa9M\xa4\xe2\xbe\xf7\xb8\xb9\xbdX' }
        msg = ERR_MSG.get(err)
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CGetActByPhoneHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, mobile, country, smscode, *args):
        dct = {
            'phone': mobile,
            'smscode': smscode }
        self.m_Path = '/urs/get_acct_by_mobile'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        10000
        ERR_MSG = {
            10131: '\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~',
            10132: '\xc5\xe7\xb5\xfd\xbdX\xb9L\xb4\xc1',
            10205: '\xa4\xe2\xbe\xf7\xb8\xb9\xae\xe6\xa6\xa1\xbf\xf9\xbb~' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CReSendHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, email, *args):
        dct = {
            'acct': email }
        self.m_Path = '/urs/resend_active_mail'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            10001: '\xb0\xd1\xbc\xc6\xbf\xf9\xbb~',
            10353: '\xb8\xd3\xb1b\xb8\xb9\xa5\xbc\xb5\xf9\xa5U',
            10354: '\xb8\xd3\xb1b\xb8\xb9\xb6W48\xa4p\xae\xc9\xa5\xbc\xbfE\xac\xa1\xa1A\xa4\xa3\xaf\xe0\xad\xab\xb5o' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CValid(pubregisterbase.CValid):
    
    def IsValidPhoneNum(cls, phone):
        if len(phone) < len(phone):
            pass
        elif len(phone) <= 11:
            return True
        
        return False

    IsValidPhoneNum = classmethod(IsValidPhoneNum)
    
    def IsValidAccount(cls, account):
        if len(account) < 5 or len(account) > 50:
            return False
        
        isEmailAct = True
        isPhontAct = True
        import re
        pattStr = '^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$'
        patt = re.compile(pattStr)
        mat = patt.match(account)
        if mat is None:
            isEmailAct = False
        
        if not account.isdigit():
            isPhontAct = False
        
        if not isEmailAct:
            pass
        return isPhontAct

    IsValidAccount = classmethod(IsValidAccount)
    
    def IsValidMail(cls, email):
        if len(email) < 5 or len(email) > 50:
            return False
        
        import re
        pattStr = '^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$'
        patt = re.compile(pattStr)
        mat = patt.match(email)
        if mat is None:
            return False
        
        return True

    IsValidMail = classmethod(IsValidMail)
    
    def IsValidPhoneCode(cls, phone_check_code):
        return len(phone_check_code) in (6, 8)

    IsValidPhoneCode = classmethod(IsValidPhoneCode)
    
    def IsValidImgCode(cls, check_code):
        return len(check_code) == 4

    IsValidImgCode = classmethod(IsValidImgCode)
