# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\mainpage.py
import C_object, C_sys, interface, wrapinterface, key, net, ui, combdialog, combmacro
g_RefreshTim = 0
g_News = None
g_PwdProtect = True

class _CBulletinButton(interface.CTextButton):

    def __init__(self, parent, filename, x, y, txt, msgid=0):
        interface.CTextButton.__init__(self, parent, filename, x, y, txt, [16777147, 65538, 13107174], interface.FontLT14EG_1, msgid)
        self.m_Selected = False
        self.SetFrame(1)
        return

    def LeftDown(self):
        if not self.m_Selected:
            self.SetFrame(1)
        return

    def LeftUp(self):
        if not self.m_Selected:
            interface.CButton.LeftUp(self)
            self.SetFrame(2)
            self.m_Selected = True
        return

    def Enter(self):
        if not self.m_Selected:
            self.SetFrame(0)
        return

    def Leave(self):
        if not self.m_Selected:
            self.SetFrame(1)
        return

    def SetSelect(self, flag):
        self.m_Selected = False
        if flag:
            self.SetFrame(2)
        else:
            self.SetFrame(1)
        return


class CMainPage(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/mainpage.dlg')
        import misc
        if misc.IsTWServer():
            self.GetObject('noname15').SetShow(False)
            import main
            if main.g_LangVersion == 0:
                it = self.GetObject('noname2')
                it.SetShow(False)
                self.m_Logo = ui.CImage(self, 'combdialog4/陔腎翻賜醱/載陔んLOGO.png', interface.UIPath)
                self.m_Logo.SetPos(-10, 430)
        else:
            self.GetObject('noname10').SetShow(False)
        (x, y) = self.GetObject('refresh').GetPos()
        hotarea = self.GetObject('url')
        (x, y) = hotarea.GetPos()
        (w, h) = hotarea.GetSize()
        self.m_HotArea = wrapinterface.LoginURL(self, w, h, msgid=20)
        self.m_HotArea.SetPos(x, y)
        self.GetObject('btn_news').LeftUp()
        import cfg
        ver = cfg.GetData('update.ini', 'Setting', 'Version')
        self.m_txtVersion = combmacro.CTEXT(C_object.CTextObject, 'loc_version', self, '版本: %s' % ver, interface.FontLT14EG_1, interface.COLOR_11)
        try:
            f = open('tg.id', 'rb')
            data = f.read()
            import register
            line = data.split()
            register.g_TGID = line[0]
            self.m_TGID = interface.CTextObject(self, register.g_TGID, interface.FontLT14E_1, 0, 0)
            self.m_TGID.SetPos(5, 16)
        except IOError:
            pass

        return

    def OnButtonEnter(self, btn):
        if btn.m_MsgID == 50:
            btn.m_tips = wrapinterface.CTextTips(self, 220, '#cfff650溫馨提醒：如果玩家在啟用該功能後無法正常輸入帳號和密碼，證明有其他程序正在監視玩家的鍵盤輸入。為保障您帳號密碼安全，請務必保持密碼保護被勾選。', interface.FontLT14E_1, direct=1)
            btn.m_tips.SetOwner(btn)
        return

    def OnButtonLeave(self, btn):
        if btn.m_MsgID == 50:
            btn.m_tips = None
        return

    def _WriteTxtBox(self, arr):
        obj = self.GetObject('output')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        import chatoutput
        self.m_PublicTxtBox = chatoutput.COutput(self, w, h, 0, 0, arr, txt_font=interface.FontLT14, txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.SetChatCursor(len(arr))
        self.m_PublicTxtBox.ResetFromCursor()
        self.m_PublicTxtBox.ScrollTo(0)
        return

    def OnMessage(self, msgid):
        global g_News
        global g_RefreshTim
        if msgid == 1:
            Show(False)
            import selectserver, sound
            selectserver.Show(True)
            sound.Play('action/button.wav')
        elif msgid == 2:
            import misc
            if misc.IsTWServer():
                import main, gameurl
                if getattr(main, 'g_LangVersion', 0) == 0:
                    url = gameurl.REGISTER_URL_IN_TAIWANG
                else:
                    url = gameurl.REGISTER_URL_IN_HK
                net.OpenUrl(url)
            else:
                import register
                Show(False)
                register.Show(True)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 3:
            import main
            main.CloseGame()
        elif msgid == 4:
            import main, os
            main.CloseGame()
            os.execlp('./mxLauncher.exe', 'mxLauncher.exe')
        elif msgid in (10, 11, 12):
            _id2btn = {10: 'btn_news', 12: 'btn_service'}
            for bname in _id2btn.values():
                self.GetObject(bname).Enable(True)

            self.GetObject(_id2btn[msgid]).Enable(False)
            self.m_PublicTxtBox = None
            if msgid == 10:
                if g_News:
                    f = g_News
                else:
                    try:
                        f = open('news.txt', 'r')
                    except:
                        f = []

                result = []
                for line in f:
                    chat = line.replace('\r\n', '#r')
                    chat = chat.replace('\n', '#r')
                    result.append(chat)

                self._WriteTxtBox(result)
            elif msgid == 11:
                try:
                    f = open('history.txt', 'r')
                except:
                    f = []
                else:
                    result = []
                    for line in f:
                        chat = line.replace('\r\n', '#r')
                        chat = chat.replace('\n', '#r')
                        result.append(chat)

                    self._WriteTxtBox(result)
            elif msgid == 12:
                try:
                    f = open('service.txt', 'r')
                except:
                    f = []
                else:
                    result = []
                    import gameurl
                    linktext = '#s(10,%s,[%s])' % (gameurl.BBS_URL, gameurl.BBS_URL)
                    for line in f:
                        chat = line.replace('\r\n', '#r')
                        chat = chat.replace('\n', '#r')
                        chat = chat.replace(gameurl.BBS_URL, linktext)
                        result.append(chat)

                    self._WriteTxtBox(result)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 20:
            import gameurl, misc
            if misc.IsTWServer():
                import main
                if getattr(main, 'g_LangVersion', 0) == 0:
                    url = gameurl.LOGO_URL_IN_TAIWANG
                else:
                    url = gameurl.LOGO_URL_IN_HK
            else:
                url = gameurl.LOGO_URL
            net.OpenUrl(url)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 21:
            import gameurl, misc
            if misc.IsTWServer():
                import main
                if getattr(main, 'g_LangVersion', 0) == 0:
                    url = gameurl.BBS_URI_IN_TAIWANG
                else:
                    url = gameurl.BBS_URL_IN_HK
            else:
                url = gameurl.BBS_URL
            net.OpenUrl(url)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 22:
            import os
            os.spawnl(os.P_NOWAIT, './gameplayer.exe', './gameplayer.exe')
            import sound
            sound.Play('action/button.wav')
        elif msgid == 30:
            import misc, commondialog
            t = misc.Time()
            f = C_sys.Record(t - g_RefreshTim < 180)
            if f:
                import usermacro
                usermacro.PROMPT_MSG('請稍後再刷新')
                return
            g_RefreshTim = t
            import cfg, main
            if main.g_LangVersion == 0:
                web = cfg.GetData('update.ini', 'Setting', 'News')
                service_web = cfg.GetData('update.ini', 'Setting', 'Service')
            else:
                web = cfg.GetData('update.ini', 'HK', 'News')
                service_web = cfg.GetData('update.ini', 'HK', 'Service')
            httpobj = net.CHttpObject(web, 'get', refreshbulletin)
            service_httpobj = net.CHttpObject(service_web, 'get', refreshService)

            def _docancel(dlg):
                try:
                    net.g_HttpObjectList.remove(dlg.m_Handle)
                    net.g_HttpObjectList.remove(dlg.m_ServiceHandle)
                except:
                    pass

                return

            dlg = commondialog.ShowMessageBox('獲取公告中。。。', '取消', (_docancel,))
            dlg.m_Handle = httpobj
            dlg.m_ServiceHandle = service_httpobj
        return


def refreshbulletin(data, succeed):
    global g_News
    import commondialog
    if not succeed:
        commondialog.ShowMessageBox('刷新公告失敗', '確定')
        return
    idx = data.find('\r\n\r\n')
    if idx == -1:
        commondialog.ShowMessageBox('刷新公告失敗', '確定')
        return
    body = data[idx + 4:]
    commondialog.HideMessageBox()
    try:
        f = open('news.txt', 'wb')
        f.write(body)
        f.close()
    except:
        g_News = body.split('\r\n')

    import cfg, misc
    cfg.SaveData('mx.ini', 'Game', 'refreshnews', '%f' % misc.Time())
    if g_MainPage:
        g_MainPage.OnMessage(10)
    return


def refreshService(data, succeed):
    import commondialog
    if not succeed:
        return
    idx = data.find('\r\n\r\n')
    if idx == -1:
        return
    body = data[idx + 4:]
    commondialog.HideMessageBox()
    try:
        f = open('service.txt', 'wb')
        f.write(body)
        f.close()
    except:
        pass

    return


def Show(s, autoupdate=True):
    global g_MainPage
    if s:
        import cfg, misc, defines
        try:
            tm = float(cfg.GetData('mx.ini', 'Game', 'refreshnews'))
        except:
            tm = 0.0
        else:
            g_MainPage = CMainPage(interface.DialogPanel)
            interface.SetDefaultButton(g_MainPage.GetObject('btn_enter'))
            misc.SetSysCaption(defines.TITLE_NAME_MX)

            def _autoupdate(obj, dummy):
                if g_MainPage:
                    g_MainPage.OnMessage(30)
                return

            f = C_sys.Record(tm + 1800 < misc.Time())
            if autoupdate and f:
                bobj = C_object.CBaseObject(None)
                bobj.CreatePyCommand(60, _autoupdate, bobj)
    else:
        g_MainPage = None
    return


return
