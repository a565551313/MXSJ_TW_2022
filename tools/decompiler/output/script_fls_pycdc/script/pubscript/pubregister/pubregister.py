# pycdc 交叉复核产物 · script.fls entry 2867
# co_filename(原始)='script/pubscript/pubregister/pubregister.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2867.pyc (Python 2.5)

import pubregisterbase
import pubmisc

class CMgr(pubregisterbase.CMgrBase):
    
    def GetSucCallFunc(self, op_type):
        raise NotImplementedError('\xbe\xde\xa7@\xa6\xa8\xa5\\\xa6^\xbd\xd5\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def GetFailCallFunc(self, op_type):
        raise NotImplementedError('\xbe\xde\xa7@\xa5\xa2\xb1\xd1\xa6^\xbd\xd5\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def OnConnectFail(self, op_type, *args):
        raise NotImplementedError('\xb5\xf9\xa5U\xb3s\xb1\xb5\xa5\xa2\xb1\xd1\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def OnReceiveNoData(self, op_type, *args):
        raise NotImplementedError('\xb5\xf9\xa5U\xb3s\xb1\xb5\xa5\xa2\xb1\xd1\xa1A\xa8S\xa6\xb3\xbc\xc6\xbe\xda\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def OnParseFail(self, op_type, data, *args):
        raise NotImplementedError('\xb8\xd1\xaaR\xbc\xc6\xbe\xda\xa5X\xbf\xf9\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def GetUrl(self, path, **dct):
        import pubtoolkit
        import pubgameurl
        if pubtoolkit.IsInner():
            urlarea = 'if2017\xa4\xba\xba\xf4'
        elif pubmisc.IsTest():
            urlarea = 'if2017\xa5~\xb4\xfa'
        else:
            urlarea = 'if2017'
        urlbase = pubgameurl.GetIf2017Url(urlarea, path, **dct)
        raise NotImplementedError('\xb5\xf9\xa5U\xc3\xec\xb1\xb5\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def GetGateSrc(self):
        raise NotImplementedError('\xc3\xec\xb1\xb5\xb8\xcc\xaa\xbagatesrc\xb0\xd1\xbc\xc6\xa1A\xbd\xd0\xbbP\xba\xf4\xaf\xb8\xa6P\xa8\xc6\xae\xd6\xb9\xea\xab\xe1\xb6\xf1\xbcg\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def GetUrlVerifyMaskCode(self):
        raise NotImplementedError('\xb5\xf9\xa5U\xc3\xec\xb1\xb5\xb8\xcc\xae\xd5\xc5\xe7\xbdX\xaa\xba\xb1\xbb\xbdX\xa1A\xbd\xd0\xbbP\xba\xf4\xaf\xb8\xa6P\xa8\xc6\xae\xd6\xb9\xea\xab\xe1\xb6\xf1\xbcg\xa1A\xa6U\xb6\xb5\xa5\xd8\xb2\xd5\xa6\xdb\xa6\xe6\xb9\xea\xb2{')

    
    def DoRegister(self, pwd, email, mac, adsid, tgid, vregval, check_code, idcard, name, phone, *args):
        gatesrc = self.GetGateSrc()
        self.Send(self.OP_REGISTER, gatesrc, pwd, email, mac, adsid, tgid, vregval, check_code, idcard, name, phone, *args)

    
    def GetCheckCode(self, *args):
        self.Send(self.OP_CHECKCODE, self.GetGateSrc(), *args)

    
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

    OP_REGISTER = 1
    OP_CHECKCODE = 2
    
    def GetHttpCls(self, op_type):
        if op_type == self.OP_REGISTER:
            return CRegisterHttp
        elif op_type == self.OP_CHECKCODE:
            return CCheckCodeHttp
        

    
    def GetActiveEditNote(self, edit_name):
        return self.EDIT2NOTE.get(edit_name, '')

    
    def ShouldShowMailEdit2(self, mail):
        mail = mail.lower()
        if not mail.endswith('.com'):
            pass
        return '@' in mail

    EDIT2NOTE = {
        'pwd': '\xb5n\xbf\xfd\xb1K\xbdX\xb6\xc8\xa5i\xa5\xd1\xa6r\xa5\xc0\xa9\xce\xaa\xcc\xbc\xc6\xa6r\xb2\xd5\xa6\xa8\xa1A\xaa\xf8\xab\xd7\xac\xb06~16\xa6\xec\xa1C',
        'pwd2': '\xbd\xd0\xa6A\xa6\xb8\xbf\xe9\xa4J\xb1z\xaa\xba\xb5n\xbf\xfd\xb1K\xbdX\xa1C',
        'email': '\xbd\xd0\xbf\xe9\xa4J\xb1z\xaa\xba\xc1p\xc3\xb4\xb6l\xbdc\xa1]#Y\xb8\xd3\xb6l\xbdc\xb1N\xa7@\xac\xb0\xb1z\xb5n\xbf\xfd\xb9C\xc0\xb8\xae\xc9\xa9\xd2\xa5\xce\xaa\xba\xb1b\xb8\xb9#n\xa1^\xa1A\xa5\xb2\xadn\xae\xc9\xa7\xda\xad\xcc\xa5i\xaf\xe0\xb3q\xb9L\xb6l\xa5\xf3\xc1p\xc3\xb4\xb1z\xa1C#r#r\xbd\xd0\xbdT\xbb{\xb6\xf1\xbcg\xa6\xb3\xae\xc4\xaa\xba\xb9q\xa4l\xb6l\xbdc\xa1C\xb1b\xb8\xb9\xb5\xf9\xa5U\xa7\xb9\xa6\xa8\xab\xe1\xa1A\xbb\xdd\xadn48\xa4p\xae\xc9\xa4\xba\xa8\xec\xb8\xd3\xb6l\xbdc\xa4\xa4\xa6\xac\xa8\xfa\xbfE\xac\xa1\xb1b\xb8\xb9\xaa\xba\xb6l\xa5\xf3\xa1F\xb1b\xb8\xb9\xbfE\xac\xa1\xab\xe1\xa4~\xaf\xe0\xb5n\xbf\xfd\xb9C\xc0\xb8',
        'email2': '\xbd\xd0\xa6A\xa6\xb8\xbf\xe9\xa4J\xb1z\xaa\xba\xb6l\xbdc',
        'code': '\xbd\xd0\xb6\xf1\xbcg\xb9\xcf\xa4\xf9\xa4\xa4\xaa\xba\xa6r\xb2\xc5\xa1A\xa4\xa3\xb0\xcf\xa4\xc0\xa4j\xa4p\xbcg' }


class CRegisterHttp(pubregisterbase.CHttpBase):
    ERR_MSG = {
        10101: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~',
        10102: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xa4w\xb9L\xb4\xc1',
        10103: '\xbb\xdd\xadn\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX',
        10131: '\xb5u\xabH\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~',
        10132: '\xb5u\xabH\xc5\xe7\xb5\xfd\xbdX\xa4w\xa5\xa2\xae\xc4',
        10301: '\xb1b\xb8\xb9\xa4w\xa6s\xa6b\xa6\xfd\xa5\xbc\xbfE\xac\xa1',
        10302: '\xb1b\xb8\xb9\xae\xe6\xa6\xa1\xbf\xf9\xbb~',
        10303: '\xb1b\xb8\xb9\xa4w\xa6s\xa6b',
        10305: '\xb1K\xbdX\xae\xe6\xa6\xa1\xbf\xf9\xbb~',
        10306: '\xb5\xf9\xa5U\xa5\xa2\xb1\xd1',
        10320: '\xb5\xf9\xa5U\xc0W\xc1c',
        10355: '\xb8\xd3\xc3\xfe\xb6l\xbdc\xa4\xa3\xa4\xe4\xab\xf9\xb5\xf9\xa5U,\xbd\xd0\xbf\xef\xa5\xce\xa8\xe4\xa5L\xb6l\xbdc',
        10363: '\xb8\xd3\xa4\xe2\xbe\xf7\xa4w\xb8j\xa9w\xa4T\xad\xd3\xa4\xe2\xbe\xf7\xb8\xb9',
        10371: '\xb8\xd3\xa4\xe2\xbe\xf7\xa4w\xb8j\xa9w2980\xb1b\xb8\xb9',
        10711: '\xa8\xad\xa5\xf7\xb5\xfd\xb8\xb9\xae\xe6\xa6\xa1\xbf\xf9\xbb~',
        10712: '\xa8\xad\xa5\xf7\xb5\xfd\xb8\xb9\xa6~\xc4\xd6\xa5\xbc\xba\xa118\xb7\xb3' }
    
    def __init__(self, mgr, op_type, gatesrc, pwd, email, mac, adsid, tgid, vkey, check_code, idcard, name, phone, areacode, country, *args):
        dct = {
            'acct': email,
            'pass': pubregisterbase.EncryptPwd(pwd),
            'gate': gatesrc,
            'smallsize': '1',
            'phone': phone }
        if adsid:
            dct['adsid'] = adsid
        
        if tgid:
            dct['tgaccount'] = tgid
        
        if vkey == 1:
            dct['smscode'] = check_code
        elif vkey:
            dct['vcode'] = check_code
            dct['vkey'] = vkey
        
        if idcard:
            dct['idcard'] = idcard
        
        if name:
            dct['tname'] = pubmisc.ConventToUtf8String(name)
        
        continue
        areacode
        dct['areacode'] = areacode

    
    def GetErrMsg(self, err, dct):
        ecode = int(dct.get('code', 0))
        if err == 0:
            return None
        
        errmsg = self.ERR_MSG.get(ecode, '')
        if not errmsg:
            errmsg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~(%d)' % ecode
        
        return errmsg



class CCheckCodeHttp(pubregisterbase.CHttpBase):
    
    def __init__(self, mgr, op_type, gatesrc, *args):
        dct = {
            'smallsize': '1' }
        self.m_Path = '/urs/get_imgcode'
        dct['sign'] = pubmisc.GetSignKey(self.m_Path, dct)
        pubregisterbase.CHttpBase.__init__(self, mgr, dct, op_type, *args)

    
    def GetErrMsg(self, err, dct):
        if err == 0:
            return None
        
        ERR_MSG = {
            10103: '\xbb\xdd\xadn\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX',
            10102: '\xbd\xd0\xad\xab\xb7s\xc0\xf2\xa8\xfa\xc5\xe7\xb5\xfd\xbdX',
            10101: '\xb9\xcf\xa7\xce\xc5\xe7\xb5\xfd\xbdX\xbf\xf9\xbb~' }
        msg = str(dct.get('msg', ''))
        if not msg:
            msg = ERR_MSG.get(err)
        
        if not msg:
            msg = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'
        
        return '%s(%d)' % (msg, err)



class CValid(pubregisterbase.CValid):
    
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
    
    def IsValidCheckCode(cls, check_code):
        return len(check_code) == 4

    IsValidCheckCode = classmethod(IsValidCheckCode)
    
    def IsValidNameChar(cls, char):
        if char == '@':
            return False
        
        if not cls.IsValidMailChar(char):
            return False
        
        if char.isalpha():
            return True
        
        if len(char) == 2 and ord(char[0]) >= 128:
            return True
        
        return False

    IsValidNameChar = classmethod(IsValidNameChar)
