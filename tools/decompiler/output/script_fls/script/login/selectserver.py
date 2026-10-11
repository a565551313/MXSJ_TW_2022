# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\selectserver.py
import C_object, C_sys, interface, wrapinterface, combdialog, net, cfg, misc, commondialog, ui
g_LoginServer = None
g_RefreshTim = 0
g_ServerList = None
SelectServer = None
g_ServerVersion = 0
g_LastVisit = None
g_ServerReMsg = None
g_NeedShowReMsg = False
COLOR_TEXT = [
 14089945, 13092]
FONT_TEXT = interface.FontLT14E_1
import os
if os.path.exists('interdaili'):
    g_Proxy = '10.17.64.100:3138'
elif os.path.exists('outerdaili'):
    g_Proxy = '10.17.177.135:3134'
else:
    g_Proxy = None
SERVERINI = 'server.ini'

def ShowReMsg():
    global g_NeedShowReMsg
    global g_ServerReMsg
    import commondialog

    def _f(data, flag):
        global g_ServerReMsg
        if flag and len(data) > 0:
            try:
                (head, body) = data.split('\r\n\r\n')
                g_ServerReMsg = body
                import commondialog
                commondialog.ShowMessageBox(g_ServerReMsg, '確定')
            except ValueError:
                pass

        return

    g_NeedShowReMsg = False
    if g_ServerReMsg == None:
        web = cfg.GetData('update.ini', 'Setting', 'BulletinURL')
        net.CHttpObject(web, 'get', _f)
    else:
        commondialog.ShowMessageBox(g_ServerReMsg, '確定')
    return


class CMXNet(net.CNet):

    def OnConnectFail(self):
        global g_NeedShowReMsg
        g_NeedShowReMsg = True
        net.CNet.OnConnectFail(self)
        import commondialog
        commondialog.ShowMessageBox('連接服務器失敗', '確定', Refresh)
        return

    def OnError(self, msg=None):
        if hasattr(self, 'm_IsRelogin') and self.m_IsRelogin:
            return
        if hasattr(self, 'm_IsExit') and self.m_IsExit:
            return
        net.CNet.OnError(self, msg)
        return


def ServerInfo():
    global SERVERINI
    f = misc.OpenFile(SERVERINI, 'rt')
    s = f.read()
    s = C_sys.RecordString(s)
    serverinfo = [_[1] for x in s.splitlines() if x.strip() != '']
    n = 0
    for l in serverinfo:
        if l.replace('=', '') == '':
            n += 1

    if len(serverinfo) > 0:
        serverinfo.append('======================')
        serverinfo.append('======================')
    return serverinfo


def GetServerInfo():
    global g_ServerList
    import serverdata
    if g_ServerList:
        import copy
        serverinfo = copy.deepcopy(g_ServerList)
    else:
        try:
            serverinfo = ServerInfo()
        except:
            Refresh(None)
            serverinfo = []

    n = 0
    lst1, lst2, lst3 = [], [], []
    for line in serverinfo:
        if line.replace('=', '') == '':
            n += 1
        elif n == 0:
            lst1.append(line)
        elif n == 2:
            lst2.append(line)
        elif n == 3:
            lst3.append(line)

    dServerInfo = {}
    for l in lst1:
        try:
            lstr = l.split()
            if len(lstr) == 1:
                sArea = lstr[0]
                dServerInfo[sArea] = []
            else:
                dInfo = {}
                dInfo['name'] = lstr[0]
                dInfo['ip'] = lstr[1]
                dInfo['port'] = int(lstr[2])
                dInfo['reserve'] = lstr[3]
                dInfo['type'] = lstr[4]
                dInfo['district'] = sArea
                if len(lstr) == 6:
                    iServerID = int(lstr[5])
                    dInfo['serverid'] = iServerID
                    misc.SetServerIDLst(iServerID)
                else:
                    dInfo['serverid'] = None
                dServerInfo[sArea].append(dInfo)
                iSerID = dInfo['serverid']
                if iSerID and not serverdata.IsInServerInfoDict(iSerID):
                    serverdata.SetServerInfoDict(iSerID, dInfo)
        except:
            LOG_EXC('server.ini錯誤行(code 1)', l)

    sAliasList = []
    for l in lst2:
        lstr = l.split()
        sAliasList.append(lstr)

    dProxyList = []
    for l in lst3:
        try:
            lstr = l.split()
            iCnt = len(lstr)
            if iCnt and lstr[0].find('ip') >= 0:
                dProxyInfo = {'ipPort': (lstr[1]), 'type': (int(lstr[2]))}
                if iCnt == 4:
                    dProxyInfo['note'] = lstr[3]
                dProxyList.append(dProxyInfo)
        except:
            LOG_EXC('server.ini錯誤行(code 2)', l)

    return (
     dServerInfo, sAliasList, dProxyList)


def Show(s):
    global SERVERINI
    global SelectServer
    global g_LastVisit
    global g_NeedShowReMsg
    if s:
        import cfg, time
        SERVERINI = cfg.GetData('mx.ini', 'Game', 'serverini')
        if SERVERINI == None:
            SERVERINI = 'server.ini'
        import misc
        if misc.IsTWServer():
            SelectServer = CSelectServer2(interface.DialogPanel)
        else:
            SelectServer = CSelectServer1(interface.DialogPanel)
        interface.SetDefaultButton(SelectServer.m_EnterButton)
        if g_NeedShowReMsg:
            try:
                _newinfo = SelectServer.m_RecordServer[g_LastVisit[1]]
                if g_LastVisit[2] == _newinfo[1] and str(g_LastVisit[3]) == _newinfo[2]:
                    ShowReMsg()
            except:
                pass

        import C_sys, defines
        C_sys.SetCaption(defines.TITLE_NAME_MX)
        try:
            tm = float(cfg.GetData('mx.ini', 'Game', 'refreshserver'))
        except:
            tm = 0.0
        else:

            def _refreshserver(obj, dummy):
                if SelectServer:
                    SelectServer.OnMessage(22)
                return

            now = misc.Time()
            nst = time.localtime(now)
            ost = time.localtime(tm)
            import permission
            f = C_sys.Record(not permission.GetSpecialVersion() and now > tm and nst[:3] != ost[:3])
            if f:
                bobj = C_object.CBaseObject(None)
                bobj.CreatePyCommand(1, _refreshserver, bobj)
            f = C_sys.Record(tm + 1800 < misc.Time())
            if f:
                bobj = C_object.CBaseObject(None)
                bobj.CreatePyCommand(1, _refreshserver, bobj)
    else:
        SelectServer = None
    g_NeedShowReMsg = False
    return


def Connect(fieldname, servername, ip, port, proxy=None):
    global g_LastVisit
    global g_LoginServer
    print 'fieldname=%s servername=%s ip=%s port=%d proxy=%s' % (fieldname, servername, ip, port, proxy)
    g_LastVisit = (
     fieldname, servername, ip, port)
    g_LoginServer = (fieldname, servername)
    net.g_Net = None
    netobj = CMXNet(ip, port)
    netobj.m_Hello = False
    if proxy:
        p = proxy.find(':')
        proxyip, proxyport = proxy[:p], int(proxy[p + 1:])
        netobj.Connect(proxyip, proxyport)
        iplst = ip.replace('.', ' ').split()
        for i in xrange(4):
            netobj.NakedSend(chr(int(iplst[i])))

        netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
    else:
        netobj.Connect()
    net.g_Net = netobj
    import commondialog
    commondialog.ShowMessageBox('正在連接服務器中....', '取消')
    return


def Refresh(dlg):
    import net, cfg, os, commondialog
    if os.path.exists('nocheck'):
        print '檢測到nocheck文件,不刷新服務器列表'
        return

    def refreshServerList(data, succeed):
        global g_ServerList
        if not succeed:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))
            return
        try:
            (head, body) = data.split('\r\n\r\n')
        except ValueError:
            try:
                f = misc.OpenFile('__server.tmp', 'w')
                f.write(data)
                f.close()
                SelectServer.m_ServerSearchEdit.AliasServerName()
            except IOError:
                pass
            else:
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))
                return

        commondialog.HideMessageBox()
        try:
            f = misc.OpenFile('server.ini', 'wb')
            f.write(body)
            f.close()
        except IOError:
            g_ServerList = [_[1] for x in body.split('\r\n') if x.strip() != '']
            import usermacro
            usermacro.PROMPT_MSG('無法修改文件#r請關閉打開的server.ini文件')

        import cfg
        cfg.SaveData('mx.ini', 'Game', 'refreshserver', '%f' % misc.Time())
        if SelectServer:
            Show(True)
        return

    cfg.SaveData('mx.ini', 'Game', 'refreshserver', '%f' % misc.Time())
    import main
    if main.g_LangVersion == 0:
        web = cfg.GetData('update.ini', 'Setting', 'ServerList')
    else:
        web = cfg.GetData('update.ini', 'HK', 'ServerList')
    net.CHttpObject(web, 'get', refreshServerList)
    commondialog.ShowMessageBox('獲取服務器列表中。。。', '取消')
    return


class CSearchServerListBox(interface.CListBox):

    def __init__(self, parent, color, font, x, y, w, h):
        interface.CListBox.__init__(self, parent, color, font, x, y, w, h)
        self.m_DownButton.SetShow(False)
        self.AliasServerName()
        return

    def AliasServerName(self):
        import copy
        self.m_ServerRecord = copy.deepcopy(self.GetParent().m_RecordServer)
        self.m_AilasName = {}
        if g_ServerList:
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                serverinfo = []

        n = 0
        for l in serverinfo:
            if l.replace('=', '') == '':
                n += 1

        if n == 0:
            serverinfo.insert(0, '=====')
        else:
            serverinfo = serverinfo[:-1]
        n = 0
        for l in serverinfo:
            if l.replace('=', '') == '':
                n += 1
            elif n == 2:
                lstr = l.split()
                if len(lstr) > 4:
                    aliasName = lstr[4][1:-1]
                    if self.m_ServerRecord.has_key(aliasName):
                        self.m_ServerRecord[lstr[0]] = copy.deepcopy(self.m_ServerRecord[aliasName])
                        self.m_AilasName[lstr[0]] = aliasName

        return

    def AddChar(self, char):
        interface.CEdit.AddChar(self, char)
        self.OnChange()
        return

    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        self.OnChange()
        return

    def DeleteSelected(self):
        interface.CEdit.DeleteSelected(self)
        self.OnChange()
        return

    def OnChange(self):
        self.m_TextList = []
        txt = self.GetText()
        txt = txt.strip()
        if txt == '':
            self.RefreshItem()
            return
        serverList = [_[1] for serverName in self.m_ServerRecord.keys()]
        serverList.sort(reverse=True)
        preServer = ''
        for serverName in serverList:
            if serverName not in preServer and txt in serverName:
                self.m_TextList.append(serverName)
            preServer = serverName

        self.RefreshItem()
        return

    def OnSelect(self, sel):
        interface.CListBox.OnSelect(self, sel)
        self.OnChangeParentState()
        return

    def OnChangeParentState(self):
        parent = self.GetParent()
        self.m_List = None
        txt = self.GetText()
        txt = txt.strip()
        if not self.m_ServerRecord.has_key(txt):
            return
        serverInfo = self.m_ServerRecord[txt]
        areaName = serverInfo[0]
        serverName = txt
        if self.m_AilasName.has_key(txt):
            serverName = self.m_AilasName[txt]
        match = ''
        if '(網通)' in txt:
            match = '(網通)'
        if '(電信)' in txt:
            match = '(電信)'
        if len(match) > 0:
            for key in parent.m_ServerListRecord.keys():
                tmpAreaInfo = parent.m_ServerListRecord[key]
                for tmpServerInfo in tmpAreaInfo:
                    if serverName == tmpServerInfo[1] and match[1:-1] in tmpServerInfo[0]:
                        areaName = tmpServerInfo[0]
                        print 'areaName:', areaName
                        break

        print 'areaName, serverName', areaName, serverName
        parent.DefaultServerChange(areaName, serverName)
        return

    def RefreshItem(self):
        tl = self.m_TextList
        if len(tl):
            (pw, ph) = self.GetSize()
            self.m_List = self.CMyList(self, 0, -self.m_ItemHeightAmount, pw, self.m_ItemHeightAmount, hspace=self.m_ItemSpace)
            self.m_List.Capture(1, 1)
            for i in xrange(len(self.m_TextList)):
                self.m_List.AddTextItem(self.m_TextList[i], 0, self.m_FontID, self.m_ItemHeight, -1, 10395294, -1, i + 1)

            self.m_List.ResetScrollBar(False)
            self.m_List.Refresh(0)
            if len(tl) == 1 and tl[0] == self.GetText():
                self.OnChangeParentState()
        else:
            self.OnListClose()
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            tl = self.m_TextList
            if len(tl):
                (pw, ph) = self.GetSize()
                self.m_List = self.CMyList(self, 0, -self.m_ItemHeightAmount, pw, self.m_ItemHeightAmount, hspace=self.m_ItemSpace)
                self.m_List.Capture(1, 1)
                for i in xrange(len(self.m_TextList)):
                    self.m_List.AddTextItem(self.m_TextList[i], 0, self.m_FontID, self.m_ItemHeight, -1, 10395294, -1, i + 1)

                self.m_List.ResetScrollBar(False)
                self.m_List.Refresh(0)
        return


class CSelectServer1(combdialog.CCombPanel):

    class _DefaultServerBtn(C_object.CBoxObject, interface.CClickObject):

        def __init__(self, parent, txt, w, h, msgid, ignoreImgWidth=False):
            C_object.CBoxObject.__init__(self, parent, w, h, 0, 0)
            interface.CClickObject.__init__(self, msgid)
            self.m_Info = txt
            self.m_Info = txt
            self.w = w
            self.h = h
            self.SetTextImg(txt, 0, ignoreImgWidth)
            return

        def Enter(self):
            self.m_Txt.SetColor(16711680)
            return

        def Leave(self):
            self.m_Txt.SetColor(0)
            return

        def SetText1(self, input_txt):
            self.m_Info = input_txt
            C_object.CTextObject(self, input_txt, interface.FontLT14_3, 0)
            (tw, th) = self.m_Txt.GetSize()
            self.m_Txt.SetPos((self.w - tw + 1) / 2, (self.h - th + 1) / 2)
            return

        def SetTextImg(self, txt, color, ignoreImgWidth=False):

            class MyRichText:

                def __init__(self, parent, txt, color, ignoreImgWidth=False):
                    img = [1, 2, 3, 4, 5]
                    img_txt = [6, 7, 8, 9, 10]
                    self.m_IgnoreImgWidth = ignoreImgWidth
                    self.m_Text = txt
                    self.m_TxtArr = []
                    last_index = 0
                    index = 0
                    (x, y) = (0, 0)
                    (w, h) = (0, 0)
                    self.m_TextWidth = 0
                    while index < len(txt):
                        for (i, v) in enumerate(img_txt):
                            if v == txt[index:index + len(v)]:
                                if last_index < index:
                                    tmp_str = txt[last_index:index]
                                    it = C_object.CTextObject(parent, tmp_str, interface.FontLT14_3, color)
                                    self.m_TxtArr.append(it)
                                    (_w, _h) = it.GetSize()
                                    x += _w
                                    if _h > h:
                                        h = _h
                                    w += _w
                                    self.m_TextWidth += _w
                                it = C_object.CImagesObject(parent, 'login/servericon/%s.igs' % img[i], interface.UIPath)
                                it.m_IsImg = True
                                (_w, _h) = it.GetSize()
                                self.m_TxtArr.append(it)
                                x += _w
                                if _h > h:
                                    h = _h
                                w += _w
                                index += len(v) - 1
                                last_index = index + 1
                                break

                        index += 1

                    if last_index < index:
                        tmp_str = txt[last_index:index]
                        it = C_object.CTextObject(parent, tmp_str, interface.FontLT14_3, color)
                        self.m_TxtArr.append(it)
                        (_w, _h) = it.GetSize()
                        x += _w
                        if _h > h:
                            h = _h
                        w += _w
                        self.m_TextWidth += _w
                    self.w = w
                    self.h = h
                    self.x = 0
                    self.y = 0
                    return

                def SetPos(self, x, y):
                    self.x = x
                    self.y = y
                    firstImg = True
                    txtLen = self.m_Text.find('·')
                    for it in self.m_TxtArr:
                        (tw, th) = it.GetSize()
                        if hasattr(it, 'm_IsImg'):
                            if it.m_IsImg and firstImg:
                                if txtLen <= 16:
                                    x += 10
                                else:
                                    x += 5
                                firstImg = False
                            else:
                                x += 2
                        it.SetPos(x, y + self.h - th)
                        x += tw

                    return

                def SetColor(self, color):
                    for it in self.m_TxtArr:
                        if hasattr(it, 'SetColor'):
                            it.SetColor(color)

                    return

                def GetPos(self):
                    return (
                     self.x, self.y)

                def GetSize(self):
                    if self.m_IgnoreImgWidth:
                        return (
                         self.m_TextWidth, self.h)
                    else:
                        return (
                         self.w, self.h)
                    return

            if txt.find('·'):
                self.m_Txt = MyRichText(self, txt, color, ignoreImgWidth)
                (tw, th) = self.m_Txt.GetSize()
                self.m_Txt.SetPos((self.w - tw + 1) / 2, (self.h - th + 1) / 2)
            else:
                self.m_Txt = C_object.CTextObject(self, txt, interface.FontLT14_3, 0)
                (tw, th) = self.m_Txt.GetSize()
                self.m_Txt.SetPos((self.w - tw + 1) / 2, (self.h - th + 1) / 2)
            return

    class CMyListBox(interface.CListBox):

        def OnSelect(self, sel):
            interface.CListBox.OnSelect(self, sel)
            self.GetParent().OnMessage(300 + sel)
            return

        def Enter(self):
            interface.CListBox.Enter(self)
            txt = '    使用「多益代理」登錄遊戲可降低電信、網#r通網絡間互聯時延遲過久的問題。使用時，請根#r據自己的網絡類型選擇連接。若連接方為相同網#r絡時，使用代理可能反而增加網絡延時，因此在#r網絡正常時不推荐使用代理登錄。'
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT12E_1)
            return

        def Leave(self):
            interface.CListBox.Leave(self)
            if hasattr(self, 'm_Tips'):
                self.m_Tips = None
            return

        def SetBtnTip(self, txt):
            if txt == '':
                return
            self.m_DownButton.m_ParentNotify = True
            self.m_BtnTip = txt
            return

        def OnButtonEnter(self, obj):
            if hasattr(self, 'm_BtnTip') and len(self.m_BtnTip) > 0:
                self.m_Tips = wrapinterface.CTextTips(self, 280, self.m_BtnTip, interface.FontLT12E_1)
                (w, h) = self.m_Tips.GetSize()
                (x, y) = self.m_Tips.GetPos()
                self.m_Tips.SetPos(-w / 2 - 2, y)
            return

        def OnButtonLeave(self, obj):
            if hasattr(self, 'm_Tips'):
                self.m_Tips = None
            return

        def OnMessage(self, msgid):
            if msgid == 1:
                tl = self.m_TextList
                if len(tl):
                    (pw, ph) = self.GetSize()
                    self.m_List = self.CMyList(self, 0, -self.m_ItemHeightAmount, pw, self.m_ItemHeightAmount, hspace=self.m_ItemSpace)
                    self.m_List.Capture(1, 1)
                    for i in xrange(len(self.m_TextList)):
                        self.m_List.AddTextItem(self.m_TextList[i], 0, self.m_FontID, self.m_ItemHeight, -1, 10395294, -1, i + 1)

                    self.m_List.ResetScrollBar(False)
                    self.m_List.Refresh(0)
            return

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/selectserver.dlg')
        self.m_ServerListRecord = {}
        self.m_RecordServer = {}
        self.m_Area = []
        self.m_Server = {}
        self.m_ServerInfomation = {}
        self.m_ServerMessageRecord = {}
        self.m_SuggestServer = []
        self.m_ServerChoose = None
        import combmacro
        self.m_Proxy = combmacro.CLISTBOX(self.CMyListBox, 'sel_proxy', self, interface.COLOR_1, interface.FontLT14_3)
        self.m_Proxy.SetItemProp(2, 16, 72)
        self.m_Proxy.SetReadOnly(True)
        self.m_Proxy.SetBtnTip('#Y請選擇您的網絡提供商#n#r註：使用「多益代理」登錄遊戲可降低電信、網通網絡間互聯時延遲過久的問題。使用時，請根據自己的網絡類型選擇連接。若連接方為相同網絡時，使用代理可能反而增加網絡延時，因此在網絡正常時不推荐使用代理登錄。')
        self.InitProxy()
        self.m_Sel_IPPort = None
        self.m_EnterButton = self.GetObject('noname16')
        self.GetObject('noname25').m_Button_Type = 1
        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))
                serverinfo = []

        interrupt = False
        try:
            try:
                self.ShowArea()
                self.ShowSuggestArea()
            except:
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))
                interrupt = True

        finally:
            self.m_ServerSearchEdit = combmacro.CLISTBOX(CSearchServerListBox, 'searchedit', self, interface.COLOR_1, interface.FontLT14_3)
            self.m_ServerSearchEdit.SetItemProp(2, 16, 72)
            if interrupt:
                return

        n = 0
        try:
            s = cfg.GetData('mx.ini', 'Login', 'LastServer')
            if s != None and len(s) > 0:
                lastsrv = (
                 s.split()[0], s.split()[1])
            else:
                self.GetObject('area1').LeftUp()
                self.GetObject('area4').LeftUp()
            s1 = cfg.GetData('mx.ini', 'Login', 'LastArea')
        except:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))

        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))
                serverinfo = []

        import main
        record_name = ''
        if main.g_RelogServerName != None and main.g_RelogServerName != lastsrv[1]:
            try:
                for l1 in serverinfo:
                    if l1.replace('=', '') == '':
                        continue
                    if l1.find(main.g_RelogServerName) == 0:
                        lastsrv = (
                         record_name[:], main.g_RelogServerName[:])
                        break
                    temp = l1.split()
                    if len(temp) == 1:
                        record_name = temp[0]

                main.g_RelogServerName = None
                import usermacro
                usermacro.PROMPT_MSG(main.g_RelogTips[:])
                main.g_RelogTips = ''
            except:
                main.g_RelogServerName = None
                main.g_RelogTips = ''

        record_name = ''
        try:
            for l1 in serverinfo:
                if l1.replace('=', '') == '':
                    n += 1
                if n == int(s1):
                    if l1.find(lastsrv[1]) == 0 and lastsrv[0] == record_name:
                        obj = self.GetObject('list')
                        (x, y) = obj.GetPos()
                        (w, h) = obj.GetSize()
                        self.m_ShowList = CSelectServer1._DefaultServerBtn(self, lastsrv[0], w, h, 197)
                        self.m_ShowList.SetPos(x, y)
                        obj = self.GetObject('server')
                        (x, y) = obj.GetPos()
                        (w, h) = obj.GetSize()
                        self.m_ShowServer = CSelectServer1._DefaultServerBtn(self, lastsrv[1], w, h, 198)
                        self.m_ShowServer.SetPos(x, y)
                        self.m_DefaultServer = []
                        temp = l1.split()
                        self.m_DefaultServer.append(record_name)
                        self.m_DefaultServer.append(temp[0])
                        self.m_DefaultServer.append(temp[1])
                        self.m_DefaultServer.append(temp[2])
                        i = 1
                        telecomIndex = 0
                        netcomIndex = 3
                        for ss in self.m_Area:
                            if '電信' in ss:
                                telecomIndex += 1
                                i = telecomIndex
                            elif '網通' in ss:
                                netcomIndex += 1
                                i = netcomIndex
                            if ss == lastsrv[0]:
                                if i > 3:
                                    self.GetObject('area1').LeftUp()
                                else:
                                    self.GetObject('area4').LeftUp()
                                self.GetObject('area%d' % i).LeftUp()
                                return

                        return
                    temp = l1.split()
                    if len(temp) == 1:
                        record_name = temp[0]

            self.GetObject('area1').LeftUp()
            self.GetObject('area4').LeftUp()
        except:
            self.GetObject('area1').LeftUp()
            self.GetObject('area4').LeftUp()

        return

    def InitProxy(self):
        try:
            serverinfo = ServerInfo()
        except:
            serverinfo = []

        self.m_IPPort = []
        ip = []
        n = 0
        for line in serverinfo:
            if line.replace('=', '') == '':
                n += 1
                continue
            lst = line.split()
            iCnt = len(lst)
            if iCnt > 0 and lst[0] == 'ip' and n > 0:
                if iCnt == 3:
                    ip.append((lst[1], lst[2]))
                elif iCnt == 4:
                    ip.append((lst[1], lst[2], lst[3]))

        s = '不使用多益代理'
        self.m_Proxy.SetText(s)
        self.m_IPPort.append({'name': s, 'ip_port': '', 'note': ''})
        txt = ''
        for (idx, val) in enumerate(ip):
            ip_port = val[0]
            number = val[1]
            note = ''
            if len(val) >= 3:
                note = val[2]
            if number == '1':
                txt = '電信'
            elif number == '2':
                txt = '網通'
            elif number == '3':
                txt = '教育網'
            else:
                continue
            self.m_IPPort.append({'name': txt, 'ip_port': ip_port, 'note': note})

        self.m_IPPort.reverse()
        for data in self.m_IPPort:
            self.m_Proxy.AddTextItem(data['name'] + data['note'])

        self.m_Proxy.SetItemProp(2, 16, len(self.m_Proxy.m_TextList) * 18)
        return

    def DefaultServerChange(self, area, server):
        serverInfo = self.m_RecordServer[server]
        self.m_DefaultServer = []
        self.m_DefaultServer.append(area)
        self.m_DefaultServer.append(server)
        self.m_DefaultServer.append(serverInfo[1])
        self.m_DefaultServer.append(serverInfo[2])
        self.m_ServerChoose = None
        obj = self.GetObject('list')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        self.m_ShowList = CSelectServer1._DefaultServerBtn(self, area, w, h, 197)
        self.m_ShowList.SetPos(x, y)
        obj = self.GetObject('server')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        self.m_ShowServer = CSelectServer1._DefaultServerBtn(self, server, w, h, 198)
        self.m_ShowServer.SetPos(x, y)
        i = 1
        telecomIndex = 0
        netcomIndex = 3
        for ss in self.m_Area:
            if '電信' in ss:
                telecomIndex += 1
                i = telecomIndex
            elif '網通' in ss:
                netcomIndex += 1
                i = netcomIndex
            if ss == area:
                it = self.GetObject('area%d' % i)
                if it.m_EnableFlag:
                    it.LeftUp()
                else:
                    self.OnMessage(28 + i - 1)
                return

        return

    def ShowSuggestArea(self):
        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))
                serverinfo = []

        n = 0
        for l in serverinfo:
            if l.replace('=', '') == '':
                n += 1

        if n == 0:
            serverinfo.insert(0, '=====')
        else:
            serverinfo = serverinfo[:-1]
        n = 0
        n1 = 0
        n2 = 0
        n3 = 0
        record_type = 0
        data_type = 0
        record_area_name = ''
        record_server_name = ''
        for k in range(1, 11):
            tempstr = 'freesuggust%s' % k
            self.GetObject(tempstr).SetShow(False)

        for l in serverinfo:
            lstr = l.split()
            if record_type == 1:
                if data_type == 0:
                    if len(lstr) > 1:
                        if len(lstr) != 5:
                            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                                          '取消'), (Refresh, None))
                        self.m_ServerMessageRecord[90 + n1] = lstr[1]
                        n += 1
                        tempstr = 'freesuggust%s' % (n1 + 1)
                        self.GetObject(tempstr).SetShow(True)
                        obj = self.GetObject(tempstr)
                        (x, y) = obj.GetPos()
                        (w, h) = obj.GetSize()
                        if lstr[4] != '&':
                            record_server_name = lstr[0]
                            record_server_name += lstr[4]
                        else:
                            record_server_name = lstr[0]
                        tmptxt = record_server_name
                        serverName = ''
                        dot = tmptxt.find('·')
                        if dot >= 0:
                            serverName = tmptxt[:dot]
                            tmptxt = tmptxt[dot + 1:]
                            if tmptxt.find('·'):
                                space = ((8 - len(serverName)) / 2 + 1) * ' '
                                serverName = space + serverName + space
                            serverName += record_server_name[dot:]
                        self.m_SuggestServer.append(self._DefaultServerBtn(self, serverName, w, h, 90 + n1))
                        self.m_SuggestServer[n - 1].SetPos(x, y)
                        n1 += 1
                    else:
                        record_type = 0
                if data_type == 1:
                    record_type = 0
                if data_type == 2:
                    if len(lstr) > 1:
                        if len(lstr) != 5:
                            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                                          '取消'), (Refresh, None))
                        n += 1
                        n3 += 1
                    else:
                        record_type = 0
            elif l == '推荐區':
                record_type = 1
            elif '=' in l:
                data_type += 1
            elif len(lstr) == 1 and '=' not in l:
                record_area_name = l
            elif len(lstr) > 4 and record_type == 0:
                self.m_ServerInfomation[lstr[1]] = (
                 record_area_name, lstr[0], lstr[2])

        return

    def ShowArea(self):
        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                serverinfo = []

        n = 0
        for l in serverinfo:
            if l.replace('=', '') == '':
                n += 1

        if n == 0:
            serverinfo.insert(0, '=====')
        else:
            serverinfo = serverinfo[:-1]
        n = 0
        tinfo = []
        for l in serverinfo:
            if l.replace('=', '') == '':
                n += 1
            elif n == 0:
                tinfo.append(l)

        if len(tinfo) <= 0:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))
            return
        i = 0
        telecomIndex = 0
        netcomIndex = 3
        record_area_data_type = 0
        m_record_name = '推荐區'
        for line in tinfo:
            lstr = line.split()
            if len(lstr) == 1 and lstr[0] != '推荐區' and record_area_data_type == 0:
                if '電信' in lstr[0]:
                    telecomIndex += 1
                    i = telecomIndex
                elif '網通' in lstr[0]:
                    netcomIndex += 1
                    i = netcomIndex
                record_area_data_type = 1
                m_record_name = lstr[0]
                self.m_Area.append(m_record_name)
                self.m_ServerListRecord[28 + i - 1] = []
            elif m_record_name != '推荐區' and len(lstr) > 4:
                record_area_data_type = 0
                self.m_RecordServer[lstr[0]] = [m_record_name, lstr[1], lstr[2], lstr[4]]
                self.m_ServerListRecord[28 + i - 1].append((m_record_name, lstr[0], lstr[1], lstr[2], lstr[4]))
            elif m_record_name != '推荐區':
                commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                              '取消'), (Refresh, None))

        for k in xrange(telecomIndex + 1, 4):
            self.GetObject('area%d' % k).SetShow(False)
            self.GetObject('areaname%d' % k).SetShow(False)

        for k in xrange(netcomIndex + 1, 7):
            self.GetObject('area%d' % k).SetShow(False)
            self.GetObject('areaname%d' % k).SetShow(False)

        return

    def RefreshAreaFollow(self, areatype):
        if len(self.m_ServerListRecord) <= 0:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))
            return
        id2ctrl = {28: 'telecom', 29: 'telecom', 30: 'telecom', 31: 'netcom', 
           32: 'netcom', 33: 'netcom'}
        id2msg = {28: 134, 29: 134, 30: 134, 31: 146, 32: 146, 33: 146}
        msgStart = id2msg[areatype]
        tempstr = id2ctrl[areatype]
        self.m_Server[tempstr] = []
        n = 1
        try:
            if self.m_ServerChoose and self.m_ServerChoose.m_LastCom == tempstr:
                self.m_ServerChoose = None
            for i in self.m_ServerListRecord[areatype]:
                tempstr1 = tempstr
                tempstr1 += '%s' % n
                if n > 12:
                    break
                obj = self.GetObject(tempstr1)
                (x, y) = obj.GetPos()
                (w, h) = obj.GetSize()
                if i[4] != '&':
                    record_server_name = i[1]
                    record_server_name += i[4]
                else:
                    record_server_name = i[1]
                self.m_Server[tempstr].append(self._DefaultServerBtn(self, record_server_name, w, h, msgStart + n, True))
                self.m_Server[tempstr][n - 1].m_Area = areatype
                self.m_Server[tempstr][n - 1].SetPos(x, y)
                self.m_Server[tempstr][n - 1].SetZ(700 + n)
                try:
                    if i[1] in self.m_DefaultServer[1]:
                        self.m_ServerChoose = C_object.CImagesObject(self, 'button/block_server.igs', 'interface')
                        self.m_ServerChoose.m_LastCom = tempstr
                        self.m_ServerChoose.SetPos(x, y)
                except:
                    pass

                n += 1

            record_server_name = ''
            for i in range(1, 13):
                record_server_name = tempstr
                record_server_name += '%s' % i
                self.GetObject(record_server_name).SetShow(True)

            for i in range(n, 13):
                record_server_name = tempstr
                record_server_name += '%s' % i
                self.GetObject(record_server_name).SetShow(False)

        except:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))
            return

        return

    def BnEnter(self, msgid):
        if msgid == 1:
            txt = '請輸入要查找的服務器名'
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct=1)
        return

    def BnLeave(self, msgid):
        if msgid == 1:
            if hasattr(self, 'm_Tips'):
                self.m_Tips = None
        return

    def OnMessage(self, msgid):
        global g_Proxy
        global g_RefreshTim
        print 'msgid', msgid
        if 300 <= msgid <= 350:
            idx = msgid - 300 - 1
            g_Proxy = self.m_IPPort[idx]['ip_port']
        elif 400 <= msgid <= 500:
            pass
        elif 90 <= msgid <= 105:
            if self.m_ServerMessageRecord.has_key(msgid):
                ip = self.m_ServerMessageRecord[msgid]
                serverInfo = self.m_ServerInfomation[ip]
                Connect(serverInfo[0], serverInfo[1], ip, int(serverInfo[2]), g_Proxy)
                cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (serverInfo[0], serverInfo[1]))
                self.m_RecordLastArea = serverInfo[0]
                self.m_RecordLastServer = serverInfo[1]
            cfg.SaveData('mx.ini', 'Login', 'LastArea', '0')
            import sound
            sound.Play('action/button.wav')
        elif 135 <= msgid <= 146:
            areaType = self.m_Server['telecom'][msgid - 135].m_Area
            server = self.m_ServerListRecord[areaType][msgid - 135]
            Connect(server[0], server[1], server[2], int(server[3]), g_Proxy)
            cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (server[0], server[1]))
            self.m_RecordLastArea = server[0]
            self.m_RecordLastServer = server[1]
            self.DefaultServerChange(server[0], server[1])
            cfg.SaveData('mx.ini', 'Login', 'LastArea', '0')
            import sound
            sound.Play('action/button.wav')
        elif 147 <= msgid <= 158:
            areaType = self.m_Server['netcom'][msgid - 147].m_Area
            server = self.m_ServerListRecord[areaType][msgid - 147]
            Connect(server[0], server[1], server[2], int(server[3]), g_Proxy)
            cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (server[0], server[1]))
            self.m_RecordLastArea = server[0]
            self.m_RecordLastServer = server[1]
            self.DefaultServerChange(server[0], server[1])
            cfg.SaveData('mx.ini', 'Login', 'LastArea', '0')
            import sound
            sound.Play('action/button.wav')
        elif msgid == 198:
            self.OnMessage(20)
        elif msgid >= 28 and msgid < 62:
            if 28 <= msgid <= 30:
                _id2btn = {28: 'area1', 29: 'area2', 30: 'area3'}
                for bname in _id2btn.values():
                    self.GetObject(bname).Enable(True)

                self.GetObject(_id2btn[msgid]).Enable(False)
            if 31 <= msgid <= 33:
                _id2btn = {31: 'area4', 32: 'area5', 33: 'area6'}
                for bname in _id2btn.values():
                    self.GetObject(bname).Enable(True)

                self.GetObject(_id2btn[msgid]).Enable(False)
            self.RefreshAreaFollow(msgid)
            import sound
            sound.Play('action/button.wav')
        elif msgid == 20:
            if len(self.m_DefaultServer) > 0:
                Connect(self.m_DefaultServer[0], self.m_DefaultServer[1], self.m_DefaultServer[2], int(self.m_DefaultServer[3]), g_Proxy)
                cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (self.m_DefaultServer[0], self.m_DefaultServer[1]))
                self.m_RecordLastArea = self.m_DefaultServer[0]
                self.m_RecordLastServer = self.m_DefaultServer[1]
            else:
                area = self.m_RecordServer[self.m_DefaultServer[1]][0]
                serverInfo = self.m_LastServer[self.m_DefaultServer]
                Connect(area, serverInfo[1], serverInfo[2], int(serverInfo[3]), g_Proxy)
                cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (area, serverInfo[1]))
                self.m_RecordLastArea = area
                self.m_RecordLastServer = serverInfo[1]
            import sound
            sound.Play('action/button.wav')
        elif msgid == 21:
            self.m_TimeType = None
            Show(False)
            import mainpage, sound
            sound.Play('action/button.wav')
            mainpage.Show(True)
        elif msgid == 22:
            import misc, commondialog, sound
            t = misc.Time()
            if t - g_RefreshTim < 60:
                import usermacro
                usermacro.PROMPT_MSG('請稍後再刷新')
                return
            g_RefreshTim = t
            Refresh(None)
            sound.Play('action/button.wav')
        return


class CSelectServer2(combdialog.CCombPanel):

    class _DefaultServerBtn(C_object.CBoxObject, interface.CClickObject):

        def __init__(self, parent, txt, w, h, msgid):
            C_object.CBoxObject.__init__(self, parent, w, h, 0, 0)
            interface.CClickObject.__init__(self, msgid)
            self.m_Txt = interface.CTextObject(self, txt, interface.FontLT14_1, 3355522)
            self.m_TxtStr = txt
            (tw, th) = self.m_Txt.GetSize()
            self.m_Txt.SetPos((w - tw + 1) / 2, (h - th + 1) / 2)
            self.w = w
            self.h = h
            return

        def Enter(self):
            self.m_Txt.SetColor(9182732)
            return

        def Leave(self):
            self.m_Txt.SetColor(3355522)
            return

        def SetText1(self, input_txt):
            self.m_Txt = interface.CTextObject(self, input_txt, interface.FontLT14_1, 3355522)
            (tw, th) = self.m_Txt.GetSize()
            self.m_Txt.SetPos((self.w - tw + 1) / 2, (self.h - th + 1) / 2)
            return

        def GetServerName(self):
            return self.m_TxtStr

    def __init__(self, parent):
        global g_ServerVersion
        global g_reocrd_block_time
        self.select_area = 0
        g_ServerVersion = 0
        self.m_ServerMessageRecord = {}
        self.m_SuggestServer = []
        self.m_Server = []
        self.m_ServerInfomation = {}
        self.record_server = {}
        self.last_server = None
        self.m_ServerListName = {}
        self.default_server = []
        import key
        combdialog.CCombPanel.__init__(self, parent, 'login/multi_selserver5.dlg')
        import main
        if main.g_LangVersion == 0:
            it = self.GetObject('noname1')
            it.SetShow(False)
            self.m_Logo = ui.CImage(self, 'combdialog4/陔腎翻賜醱/載陔んLOGO.png', interface.UIPath)
            self.m_Logo.SetPos(554, 10)
        self.m_EnterButton = combdialog.CreateTextButton(self, ['42', 20, '下一步', b'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xb6\xfe\xbc\xb6\xb0\xb4\xc5\xa5/'], 90)
        (x, y) = self.GetObject('enter_btn').GetPos()
        self.m_EnterButton.SetPos(x, y)
        self.m_ReturnButton = combdialog.CreateTextButton(self, ['42', 21, '返 回', b'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xb6\xfe\xbc\xb6\xb0\xb4\xc5\xa5/'], 90)
        (x, y) = self.GetObject('back_btn').GetPos()
        self.m_ReturnButton.SetPos(x, y)
        self.m_RefreshServerList = combdialog.CreateTextButton(self, ['42', 22, '刷新列表', b'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xb6\xfe\xbc\xb6\xb0\xb4\xc5\xa5/'], 90)
        (x, y) = self.GetObject('refresh_btn').GetPos()
        self.m_RefreshServerList.SetPos(x, y)
        _photos = ('堁拸陑_800.png', '錘疏桏_800.png',
                   'ロ酵評_800.png', '毞莽赽_800.png',
                   '筏ь⑦_800.png', '僶盻赽_800.png',
                   b'\xd1\xd7\xc8\xe7\xb7\xe7_800.png', '迶蹕价_800.png',
                   b'\xd7\xcf\xe6\xcc\xc8\xbb_800.png', '槱猀狨_800.png',
                   '羈魒鳶_800.png', '瑞鍊嫁_800.png')
        (x, y) = self.GetObject('loc_photo').GetPos()
        self.m_Photo = ui.CImage(self, b'combdialog4/\xd0\xc2\xb5\xc7\xc2\xbd\xbd\xe7\xc3\xe6/\xd0\xc2\xc8\xcb\xce\xef\xd4\xec\xd0\xcd/%s' % _photos[misc.RandInt(0, len(_photos) - 1)], 'interface')
        self.m_Photo.SetPos(x, y)
        self.m_Photo.SetZ(-1)
        g_reocrd_block_time = 0
        n = 0
        try:
            self.ShowArea()
        except:
            commondialog.ShowMessageBox('vvvvvvvvvvvvvvv', ('確定', '取消'), (Refresh, None))
            return

        try:
            s = cfg.GetData('mx.ini', 'Login', 'LastServer')
            if s != None and len(s) > 1:
                try:
                    self.default_server = (
                     s.split()[0], s.split()[1])
                    obj = self.GetObject('default_server')
                    (x, y) = obj.GetPos()
                    (w, h) = obj.GetSize()
                    self.last_server = CSelectServer2._DefaultServerBtn(self, s.split()[1], w, h, 38)
                    self.last_server.SetPos(x, y)
                    if len(self.m_ServerListName) > 0 and len(self.default_server) > 0:
                        self.record_server[38] = self.m_ServerListName[self.default_server[1]]
                except:
                    cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % ('免費區', self.record_server[50][0]))

            else:
                try:
                    serverinfo = ServerInfo()
                    server_record = 0
                    for l in serverinfo:
                        if '=' in l:
                            server_record = 1
                        elif server_record == 1:
                            temp_record = l.split()
                            self.default_server = ('免費區', temp_record)
                            obj = self.GetObject('default_server')
                            (x, y) = obj.GetPos()
                            (w, h) = obj.GetSize()
                            self.last_server = CSelectServer2._DefaultServerBtn(self, self.default_server[1], w, h, 38)
                            self.last_server.SetPos(x, y)
                            if len(self.m_ServerListName) > 0 and len(self.default_server) > 0:
                                self.record_server[38] = self.m_ServerListName[self.default_server[1]]
                            break

                except:
                    serverinfo = []
                    self.default_server = (
                     '免費區', self.record_server[50][0])
                    obj = self.GetObject('default_server')
                    (x, y) = obj.GetPos()
                    (w, h) = obj.GetSize()
                    self.last_server = CSelectServer2._DefaultServerBtn(self, self.record_server[50][0], w, h, 38)
                    self.last_server.SetPos(x, y)
                    if len(self.m_ServerListName) > 0 and len(self.default_server) > 0:
                        self.record_server[38] = self.m_ServerListName[self.record_server[50][0]]

        except:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))

        return

    def GetServerNameDict(self):
        return self.m_ServerListName

    def GetServerBtn(self):
        return self.m_Server

    def ShowArea(self):
        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                serverinfo = []

        free_server = []
        n1 = 1
        server_type = 0
        for l in serverinfo:
            if '免費區' in l:
                server_type = 1
            elif '=' in l:
                break
            elif server_type == 1 and len(l) > 4:
                free_server.append(l)

        if len(free_server) == 0:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))
            return
        for i in range(1, 27):
            temp_area = 'temp%d' % i
            self.GetObject(temp_area).SetShow(False)

        for line in free_server:
            lstr = line.split()
            temp_area = 'server%d' % n1
            temp_area1 = 'temp%d' % n1
            obj = self.GetObject(temp_area)
            self.GetObject(temp_area1).SetShow(True)
            (x, y) = obj.GetPos()
            (w, h) = obj.GetSize()
            self.m_Server.append(CSelectServer2._DefaultServerBtn(self, lstr[0], w, h, 49 + n1))
            self.m_Server[n1 - 1].SetPos(x, y)
            self.m_ServerListName[lstr[0]] = lstr
            self.record_server[49 + n1] = lstr
            n1 += 1

        return

    def ShowSuggestArea(self):
        if g_ServerList:
            import copy
            serverinfo = copy.deepcopy(g_ServerList)
        else:
            try:
                serverinfo = ServerInfo()
            except:
                serverinfo = []

        free_server = []
        n = 0
        for l in serverinfo:
            if '免費區' in l:
                break
            if '推荐區' not in l:
                free_server.append(l)

        n1 = 1
        self.m_SuggestServer = []
        for i in range(1, 10):
            temp_area = 'tempsuggest%d' % i
            self.GetObject(temp_area).SetShow(False)

        try:
            for l in free_server:
                lstr = l.split()
                temp_area = 'suggestserver%d' % n1
                temp_area1 = 'tempsuggest%d' % n1
                obj = self.GetObject(temp_area)
                self.GetObject(temp_area1).SetShow(True)
                (x, y) = obj.GetPos()
                (w, h) = obj.GetSize()
                self.m_SuggestServer.append(CSelectServer2._DefaultServerBtn(self, lstr[0], w, h, 89 + n1))
                self.m_SuggestServer[n1 - 1].SetPos(x, y)
                self.record_server[89 + n1] = lstr
                n1 += 1

        except:
            commondialog.ShowMessageBox('服務器列表需要刷新', ('確定',
                                                                                                          '取消'), (Refresh, None))

        return

    def OnMessage(self, msgid):
        global g_RefreshTim
        if msgid >= 50 and msgid < 100:
            Connect('免費區', self.record_server[msgid][0], self.record_server[msgid][1], int(self.record_server[msgid][2]), g_Proxy)
            cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % ('免費區', self.record_server[msgid][0]))
        if msgid == 38 or msgid == 20:
            self.times_type = None
            if len(self.default_server) > 0:
                Connect('免費區', self.record_server[38][0], self.record_server[38][1], int(self.record_server[38][2]), g_Proxy)
                cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (self.default_server[0], self.default_server[1]))
            else:
                Connect('免費區', self.record_server[38][0], self.record_server[38][1], int(self.record_server[38][2]), g_Proxy)
                cfg.SaveData('mx.ini', 'Login', 'LastServer', '%s %s' % (self.default_server[0], self.default_server[1]))
        if msgid == 21:
            self.times_type = None
            Show(False)
            import mainpage
            mainpage.Show(True)
        if msgid == 22:
            import misc, commondialog
            t = misc.Time()
            if t - g_RefreshTim < 60:
                import usermacro
                usermacro.PROMPT_MSG('請稍後再刷新')
                return
            g_RefreshTim = t
            Refresh(None)
        return


return
