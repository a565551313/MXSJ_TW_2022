# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\selectrole.py
import C_object, interface, combdialog, net, netlogin
SelectRole = None
g_SelectRoleIdx = None
g_AccountFlag = 0
g_Flag = False

def SelectRoleErr(err_id, err_msg):
    import commondialog
    if err_msg != None:
        commondialog.ShowMessageBox(err_msg, '確定')
    netlogin.g_LoginErrorCallback = None
    return


class CAccountDialog(combdialog.CCombDialog):

    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'login_new/account_manage.dlg')
        interface.Center(self)
        self.AfterOpenDialog()
        return

    def CloseWindow(self):
        par = self.GetParent()
        if par:
            par.CloseAccountDialog()
        return

    def OnMessage(self, msgid):
        global g_AccountFlag
        global g_Flag
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 21:
            import misc
            if misc.IsTWServer():
                return
            import aboutpwd, sound
            sound.Play('action/button.wav')
            g_Flag = True
            if g_AccountFlag == 1:
                import gameurl
                net.OpenUrl(gameurl.DYT_RESET_GAME_URL)
            else:
                aboutpwd.Show(True)
        elif msgid == 23:
            import commondialog, sound
            sound.Play('action/button.wav')
            commondialog.ShowMessageBox('正在獲取購卡記錄...', '確定')
            netlogin.C2SGetBuyCardRecord(1)
        elif msgid == 24:
            import commondialog, sound
            sound.Play('action/button.wav')
            commondialog.ShowMessageBox('正在獲取帳戶消費記錄...', '確定')
            netlogin.C2SGetConsumeRecord(1)
        return


class CClickRole(interface.CClickObject, interface.CBoxObject):

    def __init__(self, parent, x, y, w, h, info, msgid):
        interface.CBoxObject.__init__(self, parent, w, h, 16711680, 0)
        interface.CClickObject.__init__(self, msgid)
        self.m_Idx = msgid - 100
        self.SetPos(x, y)
        self.m_Info = info
        import hero, walker, loginin
        try:
            desc = hero.LoadDesc(info['ID'], loginin.GetLoginEmail())
            if 'fairy' in desc:
                del desc['fairy']
            if 'aura' in desc:
                del desc['aura']
            if 'track' in desc:
                del desc['track']
            if 'summon' in desc:
                del desc['summon']
            if 'summontype' in desc:
                del desc['summontype']
        except:
            desc = {}
            LOG('初始化角色造型獲取數據報錯', info.get('Shape', 0), self.m_Info.get('ID', 0))

        if not desc:
            desc = info.get('Desc', {})
            LOG('本地沒數據，使用服務器的')
        if type(desc) == dict:
            bIsNewChar = desc.get('isNewchar', True)
            if bIsNewChar:
                desc['bForceShape'] = True
        else:
            bIsNewChar = True
        self.m_RoleImg = walker.CFakeRole(self, -1, info['Shape'], desc, iIsUseNewRes=bIsNewChar)
        self.IgnoreSonMessage(1)
        self.m_RoleImg.SetPos(40, 150)
        self.m_RoleImg.SetDirection(6)
        self.m_Name = interface.CTextObject(self, '', interface.FontLT16_2, 16711680)
        return

    def GetID(self):
        return self.m_Info['ID']

    def LeftUp(self):
        interface.CClickObject.LeftUp(self)
        return

    def OnMessage(self, msgid):
        self.GetParent().OnMessage(msgid)
        return


class CSelectRole(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login_new/selectrole_800.dlg')
        netlogin.C2SAccount()
        self.m_RoleInfo = []
        self.m_AccountDialog = None
        self.ShowName()
        self.SelectDefaultRole()
        return

    def GetRect(self, idx):
        obj = self.GetObject('box_role%d' % idx)
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        return (x, y, w, h)

    def HideCreateBtn(self, iRoleNum):
        for i in xrange(1, 5):
            self.GetObject('btn_create%s' % i).SetShow(False)
            self.GetObject('spr_btnstar%s' % i).SetShow(False)

        if iRoleNum < 4:
            self.GetObject('btn_create4').SetShow(True)
            self.GetObject('spr_btnstar4').SetShow(True)
        return

    def SelectDefaultRole(self):
        global g_SelectRoleIdx
        import cfg
        rolenum = len(netlogin.g_LoginRoleInfo)
        if rolenum == 0:
            return
        if g_SelectRoleIdx and 0 <= g_SelectRoleIdx < rolenum:
            old = g_SelectRoleIdx
            self.m_RoleInfo[old].LeftUp()
            return
        if rolenum > 4:
            rolenum = 4
        for i in xrange(rolenum):
            (x, y, w, h) = self.GetRect(i)
            oRole = CClickRole(self, x, y, w, h, netlogin.g_LoginRoleInfo[i], i + 100)
            self.m_RoleInfo.append(oRole)

        self.HideCreateBtn(rolenum)
        if len(netlogin.g_CurrAccount) <= 1:
            self.m_RoleInfo[0].LeftUp()
            return
        import createrole
        if createrole.GetNewCreateFlag():
            self.m_RoleInfo[-1].LeftUp()
            EnterGame()
            return
        account = netlogin.GetCurrAccount()
        s = cfg.GetData('users/role.ini', net.g_Net.GetServerName() + account, 'LastID')
        try:
            lastid = int(s)
        except:
            s = cfg.GetData('mx.ini', account, 'LastID')
            try:
                lastid = int(s)
            except:
                lastid = -1

        for (i, info) in enumerate(netlogin.g_LoginRoleInfo):
            if info['ID'] == lastid:
                self.m_RoleInfo[i].LeftUp()
                return

        self.m_RoleInfo[0].LeftUp()
        return

    def ShowAccountDialog(self):
        self.m_AccountDialog = CAccountDialog(self)
        return

    def GetSize(self):
        import world
        return (world.WINDOW_WIDTH, world.WINDOW_HEIGHT)

    def CloseAccountDialog(self):
        self.m_AccountDialog = None
        return

    def SetSelectAura(self, idx):
        for i in range(0, 4):
            self.GetObject('img_choose%s' % i).SetShow(False)

        if idx < 4:
            self.GetObject('img_choose%s' % idx).SetShow(True)
        return

    def ShowName(self):
        shape2job = {1: '戰士', 2: '法師', 3: '術士'}
        for idx in range(4):
            self.GetObject('name%s' % (idx + 1)).SetText('')
            self.GetObject('level%s' % (idx + 1)).SetText('')

        for (idx, info) in enumerate(netlogin.g_LoginRoleInfo):
            if idx >= 4:
                return
            try:
                jobName = shape2job[int(str(info['Shape'])[1])]
            except:
                jobName = '戰士'

            self.GetObject('name%s' % (idx + 1)).SetText(info['Name'])
            self.GetObject('level%s' % (idx + 1)).SetText(str(info['Level']) + '級' + jobName)

        return

    def OnMessage(self, msgid):
        global g_SelectRoleIdx
        if msgid == 1:
            import sound
            sound.Play('action/button.wav')
            if g_SelectRoleIdx == None:
                if self.m_RoleInfo[0].m_MsgID == 0:
                    import commondialog
                    commondialog.ShowMessageBox('請先創建角色', '確定')
                    return
                else:
                    self.OnMessage(self.m_RoleInfo[0].m_MsgID)
            EnterGame()
        elif msgid == 2:
            self.ShowAccountDialog()
        elif msgid == 5:
            Show(False)
            import selectserver, sound
            sound.Play('action/button.wav')
            selectserver.Show(True)
            net.g_Net.Disconnect()
        elif msgid in (10, 11, 12, 13):
            Show(False)
            import createrole, sound
            sound.Play('action/button.wav')
            createrole.Show(True)
        elif msgid == 22:
            Show(False)
            import selfaccount, sound
            sound.Play('action/button.wav')
            selfaccount.Show(True)
        elif msgid == 26:
            import certmgr
            if not certmgr.IsCertUser() or certmgr.IsCertUser() and certmgr.g_IsCertRight:
                import commondialog, sound
                sound.Play('action/button.wav')
                if g_SelectRoleIdx == None:
                    commondialog.ShowMessageBox('請選擇角色...', '確定')
                    return

                def _ok(dlg, txt):
                    if not txt.isdigit() or len(txt) > 10:
                        commondialog.ShowMessageBox('請輸入正確的角色ID', '確定')
                        return
                    if netlogin.g_LoginRoleInfo[g_SelectRoleIdx]['ID'] != int(txt):
                        commondialog.ShowMessageBox('請輸入正確的角色ID', '確定')
                        return
                    if netlogin.g_LoginRoleInfo[g_SelectRoleIdx]['Level'] > 10:
                        commondialog.ShowMessageBox('10級以上的角色需要進入遊戲，找輪迴使者進行刪除操作', '確定')
                        return
                    netlogin.C2SDelRole(int(txt))
                    return

                dlg = commondialog.ShowInputDialog('#Y注意：角色刪除後將無法恢復，該角色下的世界貢獻度也將消失，請您慎重考慮!#r#r確認刪除請輸入角色ID驗証：', _ok)
            else:
                certmgr.ShowNeedCert(certmgr.g_CertLeft)
        elif 100 <= msgid < interface.RIGHT_BUTTON_MESSAGE:
            import sound, C_sys
            sound.Play('action/button.wav')
            t = C_sys.GetTime()
            if g_SelectRoleIdx != msgid - 100:
                g_SelectRoleIdx = msgid - 100
                self.SetSelectAura(g_SelectRoleIdx)
            elif t - self.m_LeftUpTim <= 5000:
                EnterGame()
            self.m_LeftUpTim = t
        return


def EnterGame():
    import commondialog
    if g_SelectRoleIdx == None:
        commondialog.ShowMessageBox('請選擇角色...', '確定')
        return
    netlogin.C2SLoginPlayerEnter(netlogin.g_LoginRoleInfo[g_SelectRoleIdx]['ID'])
    netlogin.g_LoginErrorCallback = SelectRoleErr
    commondialog.ShowMessageBox('登錄中...', '取消')
    interface.SetDefaultButton(None)
    return


def EnterRoleAdmin():
    import commondialog
    netlogin.C2SGetAccountBalance()
    commondialog.ShowMessageBox('獲取帳號數據中.....', '取消')
    return


def Show(s):
    global SelectRole
    global g_SelectRoleIdx
    if s:
        g_SelectRoleIdx = None
        SelectRole = CSelectRole(interface.DialogPanel)
        interface.SetDefaultButton(SelectRole.GetObject('btn_enter'))
        import register
        if register.g_ConfirmDlg:
            interface.SetDefaultButton(None)
            register.g_ConfirmDlg.Topmost()
    else:
        SelectRole = None
    return


def GetShow():
    return isinstance(SelectRole, CSelectRole)


def RefreshCertUser():
    return


return
