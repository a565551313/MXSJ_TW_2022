# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\localpwd.py
import C_object, interface, wrapinterface, combdialog

class CPwdEdit(interface.CEdit):

    def AddChar(self, c):
        if c.isalnum():
            interface.CEdit.AddChar(self, c)
        return


class CLocalPwd(combdialog.CCombDialog):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/localpwd.dlg')
        self.m_OldPwd = CPwdEdit(self, 0, interface.FontLT14E_1, 362, 255, 222, 14)
        self.m_OldPwd.SetLimit(16)
        self.m_OldPwd.m_IsPassword = True
        self.m_OldPwd.Active(True)
        self.m_NewPwd = CPwdEdit(self, 0, interface.FontLT14E_1, 362, 302, 222, 14)
        self.m_NewPwd.SetLimit(16)
        self.m_NewPwd.m_IsPassword = True
        self.m_NewPwdRepeat = CPwdEdit(self, 0, interface.FontLT14E_1, 362, 330, 222, 14)
        self.m_NewPwdRepeat.SetLimit(16)
        self.m_NewPwdRepeat.m_IsPassword = True
        self.m_OldPwd.SetNextEdit(self.m_NewPwd)
        self.m_NewPwd.SetNextEdit(self.m_NewPwdRepeat)
        self.m_NewPwdRepeat.SetNextEdit(self.m_OldPwd)
        self.m_FileSize = 0
        return

    def LeftDown(self):
        return

    def LeftUp(self):
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import commondialog, sound
            sound.Play('action/button.wav')
            oldpwd = self.m_OldPwd.GetText()
            if len(oldpwd) < 6:
                self.m_OldPwd.SetText('')
                commondialog.ShowMessageBox('請輸入正確的設置本地密碼的驗証碼', '確定')
                return
            newpwd1 = self.m_NewPwd.GetText()
            newpwd2 = self.m_NewPwdRepeat.GetText()
            if len(newpwd1) < 6 or len(newpwd2) < 6:
                self.m_NewPwd.SetText('')
                self.m_NewPwdRepeat.SetText('')
                commondialog.ShowMessageBox('請輸入正確格式的本地密碼', '確定')
                return
            if newpwd1 != newpwd2:
                commondialog.ShowMessageBox('兩次輸入的本地密碼不一致', '確定')
                return
            if self.m_FileSize == 0:
                commondialog.ShowMessageBox('請選擇安全強度', '確定')
                return
            self.m_OldPwd.SetText('')
            self.m_NewPwd.SetText('')
            self.m_NewPwdRepeat.SetText('')
            import netlogin
            netlogin.C2SSetLocalPwd(self.m_FileSize, oldpwd, newpwd1)
        elif msgid == 2:
            Show(False)
            import selectrole, sound
            sound.Play('action/button.wav')
            selectrole.Show(True)
        elif msgid in (11, 12, 13, 14):
            import sound
            sound.Play('action/button.wav')
            _n2s = {11: ('chk_small', 100), 12: ('chk_middle', 200), 13: ('chk_strong', 460), 14: ('chk_super', 960)}
            for (n, v) in _n2s.values():
                self.GetObject(n).Enable(True)

            self.GetObject(_n2s[msgid][0]).Enable(False)
            self.m_FileSize = _n2s[msgid][1]
        return


def CreateLocalPwdFile(netobj):
    global g_CreateTime
    size = netobj.UnpackInt(4)
    pos = []
    for i in xrange(1024):
        pos.append(netobj.UnpackInt(4) % size)

    flag = []
    for i in xrange(1024):
        flag.append(netobj.UnpackInt(1))

    ss = (size + 999) / 1000
    table = map((lambda x: []), xrange(1000))
    for (i, p) in enumerate(pos):
        tp = p / ss
        table[tp].append((p, flag[i]))

    import loginin, random, C_sys
    f = open('%s.lpd' % loginin.g_User, 'wb')
    C_object.CBaseObject(None)

    def Timer(obj, i):
        global g_CreateTime
        buf = C_sys.RandBuf(ss)
        for t in table[i]:
            bp = t[0] - i * ss
            buf = buf[:bp] + chr(t[1]) + buf[bp + 1:]

        f.write(buf)
        i += 1
        if f.tell() != ss * i:
            g_CreateTime = None
            commondialog.ShowMessageBox('磁盤空間不足，本地密碼創建失敗！', '確定')
            return
        g_CreateTime.SetMessage('正在創本地密碼,請稍等(%d%%)' % (i / 10))
        if i >= 1000:
            f.close()
            nf = open('%s.lpd' % loginin.g_User, 'rb')
            for i in xrange(1024):
                nf.seek(pos[i])
                if flag[i] != ord(nf.read(1)):
                    g_CreateTime = None
                    commondialog.ShowMessageBox('匹配錯誤，本地密碼創建失敗！', '確定')
                    return

            import netlogin
            netlogin.C2SLocalPwdSuccess()
            return
        return (
         i,)

    import commondialog
    g_CreateTime = commondialog.CModeMessageBox(None)
    g_CreateTime.SetMessage('正在創本地密碼,請稍等(0%)')
    g_CreateTime.CreatePyCommand(1, Timer, 0)
    g_CreateTime.Capture(1, 1)
    g_CreateTime.m_IsCapture = True
    g_CreateTime.SetZ(998)
    return


def CreateFail(netobj):
    global g_CreateTime
    g_CreateTime = None
    return


def CreateSuccess(netobj):
    global g_CreateTime
    import commondialog
    g_CreateTime = None
    commondialog.ShowMessageBox('本地密碼創建成功！', '確定')
    return


def FileCheck(netobj):
    filesize = netobj.UnpackInt(4)
    s = (netobj.GetCmdLen() - 4) / 4
    import loginin
    try:
        nf = open('%s.lpd' % loginin.g_User, 'rb')
    except:
        import commondialog
        commondialog.ShowMessageBox('打開本地密碼文件(%s.lpd)錯誤！' % loginin.g_User, '確定')
        return

    result = ''
    for i in xrange(s):
        p = netobj.UnpackInt(4) % filesize
        try:
            nf.seek(p)
            r = nf.read(1)
        except:
            r = '0'

        result += r

    import netlogin
    netlogin.C2SLoginLocalPW(result)
    return


def Show(flag):
    global g_LocalPwd
    if flag:
        g_LocalPwd = CLocalPwd(interface.DialogPanel)
    else:
        g_LocalPwd = None
    return


return
