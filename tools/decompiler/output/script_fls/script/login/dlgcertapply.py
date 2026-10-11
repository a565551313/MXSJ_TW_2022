# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgcertapply.py
import combdialog, interface, combmacro
g_CertApplyDlg = None

class CCertApplyDialog(combdialog.CCombDialog):
    SELECTTEXT = ('辦公室', '家裡', '學校宿舍',
                  '自習室', '筆記本', '台式機',
                  '咖啡廳', '網吧')

    class CListBox(interface.CListBox):

        def __init__(self, parent, color, font, x, y, w, h, fname=b'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xb9\xa6\xc4\xdc\xd5\xb9\xbf\xaa/'):
            interface.CListBox.__init__(self, parent, color, font, x, y, w, h, fname)
            return

        def Enter(self):
            return

        def Leave(self):
            return

    class CEdit(interface.CEdit):

        def AddChar(self, ch):
            if ch.isdigit() or ch.isalpha():
                interface.CEdit.AddChar(self, ch)
            return

    def __init__(self, phoneNumber):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/certapply2.dlg')
        interface.Center(self)
        self.m_Timer = None
        item_height = 16
        item_hspace = 2
        self.m_Environment = combmacro.CLISTBOX(self.CListBox, 'box_environment', self, interface.COLOR_5, interface.FontLT14E_1)
        self.m_Environment.SetItemProp(item_hspace, item_height, len(self.SELECTTEXT) * (item_height + item_hspace))
        self.m_Environment.SetReadOnly(True)
        for txt in self.SELECTTEXT:
            self.m_Environment.AddTextItem(txt)

        self.m_Environment.SetText(self.SELECTTEXT[1])
        self.m_InputEdit = combmacro.CEDIT(self.CEdit, 'box_input', self, 16777215, interface.FontLT14E_1, linecolor=None, overstriking=False)
        phoneNumber = phoneNumber[:3] + '****' + phoneNumber[7:]
        self.m_TxtPhoneNumber = combmacro.CTEXT(interface.CTextObject, 'box_phonenumber', self, phoneNumber, interface.FontLT14_3, 4210829, spacing=0, align=interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
        return

    def Apply(self):
        import usermacro, netcert, certmgr
        valKey = self.m_InputEdit.GetText()
        if not valKey:
            usermacro.PROMPT_MSG('請輸入驗証碼')
            return
        if len(valKey) != 6:
            usermacro.PROMPT_MSG('您輸入的驗証碼有誤，請重新輸入')
            return
        import C_sys
        t = C_sys.GetTime()
        if hasattr(self, 'm_LastFreshTime1') and self.m_LastFreshTime1 + 20000 > t:
            usermacro.PROMPT_MSG('正在驗証中……')
            return
        self.m_LastFreshTime1 = t
        netcert.C2SSend6ValKey(valKey)
        adress = self.m_Environment.GetText()
        certmgr.SetBindAddress(adress)
        return

    def RefreshGetValKey(self, cdTime=60):

        def downCount(obj, nowCount):
            nowCount -= 1
            if nowCount <= 0:
                obj.GetObject('btn_Getval').SetText('獲取驗証碼')
                obj.GetObject('btn_Getval').Enable(True)
                if obj.m_Timer:
                    obj.m_Timer.Release()
                    obj.m_Timer = None
                return
            else:
                obj.GetObject('btn_Getval').SetText('獲取驗証碼 %d' % nowCount)
                obj.GetObject('btn_Getval').Enable(False)
                return (nowCount,)
            return

        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        showText = '獲取驗証碼 %s' % cdTime
        self.GetObject('btn_Getval').SetText(showText)
        self.GetObject('btn_Getval').Enable(False)
        self.m_Timer = self.CreatePyCommand(60, downCount, cdTime)
        return

    def GetValidateKey(self):
        if self.m_Timer:
            return False
        import netcert
        netcert.C2SGetValiKey(1)
        return True

    def CloseWindow(self):
        global g_CertApplyDlg
        g_CertApplyDlg = None
        return

    def OnMessage(self, msgid):
        if msgid == 2:
            self.CloseWindow()
        elif msgid == 4:
            import certmgr, dlgnpc, netcert
            mode = certmgr.GetSendMsgMode()
            if mode == 1:
                netcert.C2SMsgMode(1, 1)
                self.ClickGetKey()
            elif mode == 2:
                netcert.C2SMsgMode(2, 1)
                self.ClickGetKey()
            elif mode == 3:

                def callback(msgid):
                    if msgid == 1:
                        netcert.C2SMsgMode(1, 1)
                        self.ClickGetKey()
                    elif msgid == 2:
                        netcert.C2SMsgMode(2, 1)
                        self.ClickGetKey()
                    return

                sContent = '請選擇驗証方式：'
                sQuestionList = ['直接手機獲取驗証碼（推荐）', '備用方式（在推荐方式無效的情況下使用）']
                dlgnpc.ShowNewClientDlg(sContent, sQuestionList, callback)
        elif msgid == 1:
            self.Apply()
        elif msgid == 3:
            import netcert
            netcert.C2SCancle()
            self.CloseWindow()
        return


def Show(phoneNumber):
    global g_CertApplyDlg
    if not g_CertApplyDlg:
        g_CertApplyDlg = CCertApplyDialog(phoneNumber)
    return


return
