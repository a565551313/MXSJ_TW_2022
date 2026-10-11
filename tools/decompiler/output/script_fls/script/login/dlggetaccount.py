# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlggetaccount.py
import interface, wrapinterface, combdialog
g_GetAccount = None

def ModuleReset():
    global g_GetAccount
    g_GetAccount = None
    return


from gameurl import ACTIVATION_URL, GET_ACCOUNT_URL

class CGetAccount(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/getaccount.dlg')
        import wraptextobj
        self.GetObject('btn_num').LeftUp()
        (x, y) = self.GetObject('txt_GetAccount').GetPos()
        self.m_Account = wraptextobj.CUnderLineClickText(self, x, y, '通過手機找回賬號', 65535, 16711680, interface.FontLT14_3, msgid=12)
        self.m_GetAccountTime = 0
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import misc, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            import C_sys
            t = misc.Time()
            f = C_sys.Record(t - self.m_GetAccountTime < 120)
            if f:
                import usermacro
                usermacro.PROMPT_MSG('操作過於頻繁，請稍後再嘗試')
                self.m_GetAccountTime = t
                return

            def _getacct(data, succeed):
                import commondialog
                if not succeed:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    (head, body) = data.split('\r\n\r\n')
                except ValueError:
                    return

                result = body.split()
                if result[0][:2] != '0,':
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    acct_count = int(result[0][2:].strip())
                except ValueError:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return

                if acct_count <= 0:
                    commondialog.ShowMessageBox('沒有得到有效的帳號信息', '確定')
                    return
                acct_count = min(acct_count, len(result) - 1)
                txt = '您的帳號如下：#Y'
                for i in xrange(acct_count):
                    if i % 5 == 0:
                        txt += '#r%-12s' % result[i + 1]
                    else:
                        txt += '%-12s' % result[i + 1]

                import combmacro
                commondialog.HideMessageBox()
                self.m_Result = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_Result', self, txt, interface.FontLT14_3, 16776960)
                return

            def _getemail(data, succeed):
                import commondialog
                if not succeed:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                    return
                try:
                    (head, body) = data.split('\r\n\r\n')
                except ValueError:
                    return

                if body[:2] == '91':
                    commondialog.ShowMessageBox('郵箱和角色ID不匹配', '確定')
                elif body[:3] == '0,0':
                    commondialog.ShowMessageBox('找回成功，帳號信息已發送至您的郵箱', '確定')
                elif body[:3] == '0,1':
                    commondialog.ShowMessageBox('郵件發送失敗，請確認您填寫的是正確郵箱', '確定')
                else:
                    commondialog.ShowMessageBox('獲取失敗', '確定')
                return

            import C_sys, net, commondialog, misc, device
            try:
                mac = device.GetMAC()
            except:
                commondialog.ShowMessageBox('無法獲取帳號信息', '確定')
                return
            else:
                import gameurl
                if self.m_SelectFlag == 10:
                    web = gameurl.GETPWD_CURRENTPC_URL % mac
                    import security
                    token_key = security.CreateOneEncodeGuid()
                    web += '&tokenkey=%s' % token_key
                    net.CHttpObject(web, 'get', _getacct)
                elif self.m_SelectFlag == 11:
                    idx = self.m_SelectFlag - 11
                    import net, usermacro
                    net.OpenUrl(ACTIVATION_URL)
                    usermacro.PROMPT_MSG('#Y請在彈出的網頁上進行相關操作#n')
                    return
                commondialog.ShowMessageBox('獲取帳號信息中...', '確定')
        elif msgid == 2:
            Show(False)
            import loginin, sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            loginin.Show(True)
        elif msgid == 10:
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            self.m_SelectFlag = 10
        elif msgid == 11:
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            self.m_SelectFlag = 11
        elif msgid == 12:
            import sound, sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            import net, usermacro
            net.OpenUrl(GET_ACCOUNT_URL)
            usermacro.PROMPT_MSG('#Y請在彈出的網頁上進行相關操作#n')
        return


def Show(flag):
    global g_GetAccount
    if flag:
        g_GetAccount = CGetAccount(interface.DialogPanel)
    else:
        g_GetAccount = None
    return


return
