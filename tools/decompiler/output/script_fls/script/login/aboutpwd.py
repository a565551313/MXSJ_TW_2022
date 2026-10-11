# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\aboutpwd.py
import C_object, interface, wrapinterface, combdialog
g_AboutPwd = None
PublicTxt = {1: '\n取回密碼\n\n    《夢想世界》充分保証用戶帳號的安全性，在全國範圍內率先開通短信找回密碼服務。\n    #Y【多益通行証取回密碼】#n\n    多益通行証是多益網絡推出的統一帳號系統，每個多益通帳號都對應固定的服務號，服務號可用於使用網站取回多益通密碼\n    郵箱取回多益通帳號密碼可#s(10,http://dy.duoyi.com/func/view.aspx?act=getpassbymail&pstype=game,[點擊查看])\n    若您忘記了多益通帳號對應的服務號可#s(10,http://kf.duoyi.com/dyt/check_number.htm,[點擊取回服務號])\n    \n    #Y【非多益通行証取回密碼】#n\n    非多益通行証還可使用郵箱取回密碼\n    詳情可點擊\n', 
   2: b'\n\xa4@\xa1B\xa6h\xafq\xb3q\xb1b\xb8\xb9\xb1K\xbdX\xb3W\xabh\xa1F \n    1\xa1B\xa9\xd2\xa6\xb3\xb2\xa3\xab~\xa8\xcf\xa5\xce\xa6P\xa4@\xad\xd3\xa6h\xafq\xb3q\xb1b\xb8\xb9\xa1A\xa6\xfd\xa4@\xad\xd3\xa6h\xafq\xb3q\xb1b\xb8\xb9\xa6\xb3\xa4G\xba\xd8\xc3\xfe\xab\xac\xaa\xba\xb1K\xbdX\xa1G\n      a) \xa4@\xba\xd8\xb1K\xbdX\xa5\xce\xa9\xf3\xb5n\xbf\xfd\xb9C\xc0\xb8\xb2\xa3\xab~\xa1A\xac\xb0\xa1u\xa6h\xafq\xb3q\xb9C\xc0\xb8\xb1K\xbdX\xa1v\xa1C\n      b) \xa5t\xa4@\xba\xd8\xb1K\xbdX\xa5\xce\xa9\xf3\xb5n\xbf\xfd\xabD\xb9C\xc0\xb8\xb2\xa3\xab~\xa1A\xac\xb0\xa1u\xa6h\xafq\xb3q\xba\xf4\xaf\xb8\xb1K\xbdX\xa1v\xa1C\n    2\xa1B\xa1u\xa6h\xafq\xb3q\xb9C\xc0\xb8\xb1K\xbdX\xa1v\xa9M\xa1u\xa6h\xafq\xb3q\xba\xf4\xaf\xb8\xb1K\xbdX\xa1v\xa5\xb2\xb6\xb7\xb9\xef\xc0\xb3\xaa\xba\xb2\xa3\xab~\xb8\xcc\xb3]\xb8m\xa1G\n      a) \xa6p\xaaG\xa6b\xb9C\xc0\xb8\xb8\xcc\xb5\xf9\xa5U\xaa\xba\xa6h\xafq\xb3q\xb6i\xa6\xe6\xba\xf4\xaf\xb8\xb5n\xbf\xfd\xae\xc9\xa1A\xb7|\xb4\xa3\xa5\xdc\xb1K\xbdX\xbf\xf9\xbb~\xa1A\xa8\xc3\xadn\xa8D\xb6i\xa6\xe6\xba\xf4\xaf\xb8\xb1K\xbdX\xb3]\xb8m\xa1C\n      b) \xa6P\xbc\xcb\xa6b\xba\xf4\xaf\xb8\xb8\xcc\xb5\xf9\xa5U\xaa\xba\xa6h\xafq\xb3q\xb6i\xa6\xe6\xb9C\xc0\xb8\xb5n\xbf\xfd\xae\xc9\xa1A\xa4]\xb7|\xb4\xa3\xa5\xdc\xb1K\xbdX\xbf\xf9\xbb~\xa1A\xa8\xc3\xadn\xa8D\xb6i\xa6\xe6\xb9C\xc0\xb8\xb1K\xbdX\xb3]\xb8m\xa1C\n    3\xa1B\xa6h\xafq\xb3q\xa4\xa3\xb4\xa3\xa8\xd1\xad\xd7\xa7\xef\xb1K\xbdX\xa5\\\xaf\xe0\xa1A\xa5u\xb4\xa3\xa8\xd1\xb6l\xbdc\xa7\xe4\xa6^\xb1K\xbdX\xa1]\xad\xab\xb8m\xb1K\xbdX\xa1^\xa5\\\xaf\xe0\xa1C\n      \xa8\xcf\xa5\xce\xb6l\xbdc\xa8\xfa\xa6^\xa6h\xafq\xb3q\xb1b\xb8\xb9\xb1K\xbdX\xa5i#s(10,http://dy.duoyi.com/func/view.aspx?act=getpassbymail,[\xc2I\xc0\xbb\xacd\xac\xdd])\n\n\xa4G\xa1B\xa6h\xafq\xb3q\xb5\xf9\xa5U\xb3W\xabh\xa1F \n    1\xa1B\xa6h\xafq\xb3q\xb5\xf9\xa5U\xa4\xe8\xa6\xa1\xa1C\n      a) \xb3q\xa6\xe6\xb5\xfd\xa5\xce\xa4\xe1\xa6W\xa5\xb2\xb6\xb7\xa8\xcf\xa5\xce\xb6l\xbdc\xa6a\xa7}\xb6i\xa6\xe6\xb5\xf9\xa5U\xa1A\xb5\xf9\xa5U\xae\xc9\xa5u\xbb\xdd\xb6\xf1\xbcg\xb6l\xbdc\xa9M\xb1K\xbdX\xa7Y\xa5i\xa1A\xa8\xe4\xa5L\xabH\xae\xa7\xa6b\xb5n\xbf\xfd\xa6h\xafq\xb2\xa3\xab~\xab\xe1\xbb\xdd\xadn\xae\xc9\xa6A\xb6\xf1\xbcg\xa1C\n      b) 2980\xb6l\xbdc\xa5\xce\xa4\xe1\xa5i\xa5H\xa7K\xb5\xf9\xa5U\xaa\xbd\xb1\xb5\xb5n\xbf\xfd\xa8\xcf\xa5\xce\xa6h\xafq\xb3q\xaa\xba\xb2\xa3\xab~\xa1C\n        1. \xa6p\xaaG\xa8\xcf\xa5\xce2980\xb2\xc4\xa4@\xa6\xb8\xb5n\xbf\xfd\xaa\xba\xacO\xa6h\xafq\xabD\xb9C\xc0\xb8\xb2\xa3\xab~\xa1A\xa8\xba\xb4N\xb5\xa5\xa9\xf3\xaa\xbd\xb1\xb5\xb3]\xb8m\xa4F\xa1u\xa6h\xafq\xb3q\xba\xf4\xaf\xb8\xb1K\xbdX\xa1v\xa1A \xa6\xd3\xa1u\xa6h\xafq\xb3q\xb9C\xc0\xb8\xb1K\xbdX\xa1u\xac\xb0\xaa\xc5\xa1C\n        2. \xa6p\xaaG\xa8\xcf\xa5\xce2980\xb2\xc4\xa4@\xa6\xb8\xb5n\xbf\xfd\xaa\xba\xacO\xa6h\xafq\xb9C\xc0\xb8\xb2\xa3\xab~\xa1A\xa8\xba\xb4N\xb5\xa5\xa9\xf3\xaa\xbd\xb1\xb5\xb3]\xb8m\xa4F\xa1u\xa6h\xafq\xb3q\xb9C\xc0\xb8\xb1K\xbdX\xa1v\xa1A\xa6\xd3\xa1u\xa6h\xafq\xb3q\xba\xf4\xaf\xb8\xb1K\xbdX\xa1u\xac\xb0\xaa\xc5\xa1C\n        3. 2980\xb6l\xbdc\xaa\xba\xb1K\xbdX\xa5u\xa6b\xad\xba\xa6\xb8\xb5n\xbf\xfd\xa6h\xafq\xb3q\xae\xc9\xa5i\xa5H\xa7K\xb5\xf9\xa5U\xaa\xbd\xb1\xb5\xb5n\xbf\xfd\xa1C\xa6\xb9\xab\xe1\xa6h\xafq\xb3q\xb1K\xbdX\xa9\xce2980\xb6l\xbdc\xb1K\xbdX\xa6p<)7M=u)9>9-\xe6<\xdb6AYl[\xea;\xd9\x90\xba\xba\xba\xba\xa8;\xd8<\xf25\xeb)\xeb0 ?T>{"p4\\\x90\xba\xba\xba\xba\xba\xba\xfb\xb3\xba<\xf25\xeb)\xeb0 ?\xde7\xf41\xd24=<);\xdd,\xf6\'\xf9;\xc7=\xc3+\xf8"#;\xc4;\xd827?m/g"#\'\xc2;\xd83\xf7<\xcd;\xd8>T>\xda2]2~?\xd61\xd24=\x90\xba\xba\xba\xba\xba\xba\xf8\xb3\xba4@$@?T>{2U?T<\xf25\xeb)\xeb/\xf4%g>9<\xca0 (91\xe4;\xdb3H7\xf42\xde0 ?T>{"p4\\>\xc7.\xd4>9<\xca;\xdb>k<\xea/\xf4%g#\xd9Z\xb8\xa1\xa7\xb9\xda\xb7Q\xa5@\xac\xc9\xa1v\xa9m\xa6W\xa1A\xa9M\xa8\xad\xa5\xf7\xb5\xfd\xb4N\xacO\xa5\xb2\xb6\xf1\xb6\xb5\xa1F\xa5\xce\xa6h\xafq\xb3q\xb5n\xbf\xfd\xa1u\xbb\xe2\xb7R\xba\xf4\xa1v\xb3o\xa8\xc7\xb4N\xa4\xa3\xacO\xa5\xb2\xb6\xf1\xb6\xb5\xa1C\n    3\xa1B\xa6h\xafq\xb3q\xb1b\xb8\xb9\xac\xb0\xa5\xc3\xa4[\xa9\xca\xb5\xf9\xa5U\xa1A\xb2\xc4\xa4@\xa6\xb8\xbdT\xbb{\xb1b\xb8\xb9\xab\xe1\xa1A\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xad\xd7\xa7\xef\xa1A\xbd\xd0\xa5\xce\xa4\xe1\xa5\xbf\xbdT\xa8\xcf\xa5\xce\xa9M\xa8c\xb0O\xb1b\xb8\xb9\xa1C\n    4\xa1B\xa6h\xafq\xb3q\xa6\xe6\xb5\xfd\xb5\xf9\xa5U\xb1b\xb8\xb9\xbb\xdd\xa6b\xa6h\xafq\xb3q\xb2\xa3\xab~\xa4\xa4\xb6i\xa6\xe6\xa1]\xb9\xda\xb7Q\xa5@\xac\xc9\xa1A\xbb\xe2\xb7R\xba\xf4\xa1^\xa1C\n', 
   3: '\n本地密碼：\n#Y多益通行証暫不提供本地密碼相關服務#n\n「本地密碼是通過在本地電腦上創建安全性文件的方式來保護用戶的帳號。\n設置好本地密碼之後，該帳號僅能在擁有此安全驗証文件的電腦上登錄，而無法在其他電腦上登錄，極大提高帳號安全性；同時，如果確實需要在其他電腦上進行遊戲，可以將生成的以本人登錄帳號所命名的安全驗証文件拷貝到其他電腦的《夢想世界》遊戲目錄下， 即可在異地使用本地密碼登錄遊戲\n\n獲取本地密碼驗証碼或取消本地密碼可#s(10,http://kf.duoyi.com/dyt/local_password.htm,[點擊查看])\n\n#Y注意：設置本地密碼之後，下次登錄遊戲時，原始密碼會失效，必須使用新設置的本地密碼才可登錄\n'}

def Show(flag):
    global g_AboutPwd
    if flag:
        g_AboutPwd = CAbountPwd(interface.DialogPanel)
    else:
        g_AboutPwd = None
    return


class CAbountPwd(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/aboutgetpwd.dlg')
        if interface.GCODE == interface.GBK:
            (x1, y1) = self.GetObject('noname1').GetPos()
            (_, y2) = self.GetObject('btn_localpwd').GetPos()
            self.m_DYTBtn = interface.CButton(self, 'combdialog/偌聽/腎翻偌臟.igs', x1, y2 + y2 - y1, 4)
            self.m_DYTBtnTxt = combdialog.CTextFrame(self, [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], 3)
            self.m_DYTBtnTxt.SetPos(x1 + 40 + 8, y2 + y2 - y1 + 12)
            self.m_DYTBtnTxt.SetZ(1000)
        self.OnMessage(3)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            Show(False)
            import selectrole, sound, loginin
            if selectrole.g_Flag:
                if selectrole.g_AccountFlag == 0:
                    sound.Play('action/button.wav')
                    selectrole.Show(True)
                    selectrole.g_Flag = False
            if loginin.g_Flag:
                sound.Play('action/button.wav')
                loginin.Show(True)
                loginin.g_Flag = False
        elif msgid == 2:
            ShowMailGetpwd()
        elif msgid in (3, 4, 5):
            txt = PublicTxt[msgid - 2]
            txt = txt.replace('\n', '#r')
            import combmacro, chatoutput
            self.m_Desc = combmacro.COUTPUT(chatoutput.COutput, 'output', self, 0, 0)
            self.m_Desc.m_Chats = txt.split('#r')
            self.m_Desc.ResetFromCursor()
            if msgid == 3:
                self.m_GetpwdBtn = interface.CTextButton(self, 'combdialog/偌聽/6趼蟯偌聽.igs', 268, 239, '郵箱取回密碼', 0, interface.FONT_EDIT, 2)
                self.m_GetpwdBtn.SetZ(100)
            else:
                self.m_GetpwdBtn = None
            import sound
            sound.Play('action/button.wav')
        return


g_MailGetpwdDialog = None
g_FailCommitTime = 0

def ShowMailGetpwd():
    global g_MailGetpwdDialog
    if g_MailGetpwdDialog:
        g_MailGetpwdDialog = None
    else:
        g_MailGetpwdDialog = CGetPwdDialog()
    return


class CGetPwdDialog(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/mailboxgetpwd.dlg')
        (mw, mh) = (0, 0)
        for obj in self.m_Frames.itervalues():
            if not hasattr(obj, 'GetSize'):
                continue
            (w, h) = obj.GetSize()
            if w > mw:
                mw = w
            if h > mh:
                mh = h

        self.m_Width = mw
        self.m_Height = mh
        interface.Center(self)
        self.Topmost()
        import combmacro, wrapinterface
        self.m_MailBox = combmacro.CEDIT(interface.CEdit, 'mailbox', self, 0, interface.FONT_EDIT, 0)
        self.m_Pid = combmacro.CEDIT(wrapinterface.CNumberEdit, 'pid', self, 0, interface.FONT_EDIT, 0)
        self.m_MailBox.SetNextEdit(self.m_Pid)
        self.m_Pid.SetNextEdit(self.m_MailBox)
        self.Capture(1, 1)
        self.m_MailBox.Active(True)
        self.m_MailBox.SetLimit(32)
        return

    def SetResult(self, txt):
        import combmacro
        if type(txt) == str:
            self.m_Result = combmacro.CreateRichText(C_object.CRichTextObject, 'result', self, txt, interface.FONT_DESC, 16777215)
        else:
            self.m_Result = None
        return

    def Record(self):
        global g_FailCommitTime
        import cfg, time
        lasttime = cfg.GetData('mx.ini', 'Game', 'LastCommitForbiden')
        if lasttime:
            lasttime = int(lasttime)
            thistime = time.time()
            if thistime - lasttime < 1800:
                return False
        return g_FailCommitTime < 3

    def SuccessOnce(self):
        global g_FailCommitTime
        g_FailCommitTime = 0
        return

    def FailOnce(self):
        global g_FailCommitTime
        import cfg, time
        g_FailCommitTime += 1
        if g_FailCommitTime >= 3:
            g_FailCommitTime = 0
            cfg.SaveData('mx.ini', 'Game', 'LastCommitForbiden', '%d' % time.time())
        return

    def IsEMail(self, email):
        if hasattr(self, 'm_Pattern'):
            patt = self.m_Pattern
        else:
            import re
            patt = re.compile('^[-.\\w]{1,64}@[-.\\w]{1,64}\\.[\\w]{2,4}$')
            self.m_Pattern = patt
        return None != patt.match(email)

    def OnMessage(self, msgid):
        if msgid == 1 or msgid == 3:
            ShowMailGetpwd()
            import sound
            sound.Play('action/button.wav')
        elif msgid == 2:
            import sound
            sound.Play('action/button.wav')
            mailbox = self.m_MailBox.GetText()
            pid = self.m_Pid.GetText()
            if len(mailbox) == 0 or len(pid) == 0:
                return
            if not self.IsEMail(mailbox):
                import usermacro
                usermacro.PROMPT_MSG('請輸入合法的郵箱地址')
                return

            def _getemail(data, ret, obj):
                obj = obj.Get()
                if obj == None:
                    return
                if ret == False:
                    obj.SetResult('網絡繁忙，請稍後再試')
                    return
                data = data.split('\n')[-1]
                data = data.split(',')
                LEN = len(data)
                if LEN >= 1:
                    id = int(data[0])
                    if LEN >= 2:
                        txt = data[1]
                    if id in (20, 21, 23, 63):
                        obj.SetResult('所填信息有誤，請重新輸入')
                        obj.FailOnce()
                    elif id == 108:
                        obj.SetResult('你已經成功提交過一次，三天內不能再次提交。')
                    elif id == 109:
                        obj.SetResult('所填郵箱有誤，請重新輸入')
                        obj.FailOnce()
                    elif id == 0:
                        obj.SetResult('郵件發送完成，請注意查收系統郵件。根據鏈接修改密碼，鏈接有效期為三天。三天內禁止再次提交修改申請。')
                        obj.SuccessOnce()
                    else:
                        print '不可預知的返回結果', id
                else:
                    print '返回結果格式錯誤:', data
                return

            if self.Record() == False:
                self.SetResult('信息輸入錯誤次數太多，暫時無法提交申請，請稍後再試')
                return
            import net, netlogin, gameurl
            web = gameurl.EMAINGETPWD_URL % (netlogin.g_ServerNum, pid, mailbox)
            import security
            token_key = security.CreateOneEncodeGuid()
            web += '&tokenkey=%s' % token_key
            net.CHttpObject(web, 'get', _getemail, C_object.CShadowObject(self))
            self.SetResult('申請已提交，請勿關閉界面，耐心等待結果')
        return


return
