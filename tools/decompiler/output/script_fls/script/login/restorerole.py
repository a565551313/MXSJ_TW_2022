# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\restorerole.py
import interface, combdialog, pubrestorerole
g_RestoreDlg = None
g_Mgr = None

def ModuleReset():
    global g_Mgr
    global g_RestoreDlg
    g_RestoreDlg = None
    g_Mgr = None
    return


def RequestOpenDlg():
    global g_Mgr
    if not g_Mgr:
        g_Mgr = CMgr()
    g_Mgr.C2SGetRolesInfo()
    return


def Close():
    global g_Mgr
    Show(False)
    if g_Mgr:
        g_Mgr.OnClear()
        g_Mgr = None
    return


def Show(bShow, data=None):
    global g_RestoreDlg
    if data is None:
        data = {}
    if bShow:
        if not g_RestoreDlg:
            g_RestoreDlg = CRestoreRoleDlg()
        g_RestoreDlg.Refresh(data)
    elif g_RestoreDlg:
        g_RestoreDlg.CloseWindow()
        g_RestoreDlg = None
    return


def OnRoleAdd(pid):
    if g_Mgr:
        g_Mgr.OnRoleAdd(pid)
    return


def S2CProcess(netobj):
    global g_Mgr
    if not g_Mgr:
        g_Mgr = CMgr()
    g_Mgr.S2CProcess(netobj)
    return


class CMgr(pubrestorerole.CNet, pubrestorerole.CMgr):
    RESTORING_LST = []
    DEBUG = True

    def GetHeader(cls, iSub):
        import netpublic
        if cls.DEBUG:
            print 'C2GS_RESTORE_ROLE', iSub
        netobj = netpublic.PacketPrepare(netpublic.C2GS_RESTORE_ROLE)
        netobj.PacketAddI(iSub, 1)
        return netobj

    def S2CRestoreVersion(self, netobj):
        import misc
        version = pubrestorerole.CNet.S2CRestoreVersion(self, netobj)
        print 'S2CRestoreVersion', version
        if not misc.IsTWServer():
            import selectrole
            selectrole.SetRestoreVersion(version)
        return

    def S2CRolesInfo(self, netobj):
        pub_data_dct = pubrestorerole.CNet.S2CRolesInfo(self, netobj)
        if self.DEBUG:
            print pub_data_dct
        local_data_dct = self.ProcessRolesData(pub_data_dct)
        self.ShowRolesInfo(local_data_dct)
        return

    def S2CCanPayRoles(self, netobj):
        if not hasattr(self, 'm_RestoreID'):
            return
        data = pubrestorerole.CNet.S2CCanPayRoles(self, netobj)
        if self.DEBUG:
            print data
        dct = {}
        iNeed = self.m_RestoreDct[self.m_RestoreID]['Cost']
        for (pid, gold) in data.items():
            if gold >= iNeed:
                dct[pid] = gold

        if dct:
            self.ShowCanPayRoles(dct)
        else:
            self.ShowBuyGoldNpcDlg()
        return

    def S2CBuyGoldUrl(self, netobj):
        url = pubrestorerole.CNet.S2CBuyGoldUrl(self, netobj)
        if self.DEBUG:
            print url
        self.OpenBuyGoldUrl(url)
        return

    def S2CRestoreResult(self, netobj):
        result_num = pubrestorerole.CNet.S2CRestoreResult(self, netobj)
        result_msg = self.GetResultReason(result_num)
        self.ShowPrompt(result_msg)
        return

    def GetResultReason(self, result_num):
        dct = {1: '該賬號在最近的30天內成功恢復過角色，暫時無法使用該功能', 
           2: '該賬號在本服的角色過多，暫時無法使用該功能', 
           3: '該賬號在本服沒有角色，需要在本服務器創建一個角色後才能使用角色找回功能', 
           4: '該賬號已經有角色在恢復中了，正在處理恢復請求，請稍候', 
           5: '恢復角色，世貢餘額不足，恢復失敗。', 
           6: '恢復角色，數據中心返回失敗。', 
           7: '網絡異常', 
           8: '該賬號在本服沒有角色可以找回', 
           30: '恢復成功'}
        return dct.get(result_num, '未知錯誤')

    def ShowPrompt(self, result_msg):
        import usermacro
        usermacro.g_PromptTips[:] = []
        return usermacro.PROMPT_MSG(result_msg)

    def ShowRolesInfo(self, data):
        self.m_RestoreDct = data
        Show(True, data)
        return

    def ShowCanPayRoles(self, data):
        if not hasattr(self, 'm_RestoreID'):
            return
        import dlgnpc
        quest_lst = []
        self.m_CanPayLst = pid_lst = data.keys()
        pid_lst.sort()
        for pid in pid_lst:
            gold = data[pid]
            name = self.GetExistRoleName(pid)
            quest_lst.append('Q%s' % name)

        quest_text = ('\n').join(quest_lst)
        text = '請選擇要支付的角色。\n%s' % quest_text
        dlgnpc.ShowClientDlg(text, '', self.ConfirmPayRole)
        return

    def ConfirmPayRole(self, msgid):
        if not (hasattr(self, 'm_CanPayLst') and hasattr(self, 'm_RestoreID')):
            return
        if msgid > len(self.m_CanPayLst):
            return
        pay_id = self.m_CanPayLst[msgid - 1]
        self.C2SRestoreRole(self.m_RestoreID, pay_id)
        if self.m_RestoreID not in self.RESTORING_LST:
            self.RESTORING_LST.append(self.m_RestoreID)
        del self.m_CanPayLst
        del self.m_RestoreID
        return

    def GetExistRoleName(self, pid):
        import netlogin
        for dct in netlogin.g_LoginRoleInfo:
            if dct['ID'] == pid:
                return dct['Name']

        return '%d' % pid

    def ShowBuyGoldNpcDlg(self):
        import dlgnpc

        def func(msgid):
            if msgid == 1:
                self.C2SOpenBuyGoldUrl()
            return

        text = '沒有可供支付的角色，是否需要充值以支付本次角色恢復的費用？#r#Y提示：世貢會充值到本服最高等級的角色中#n'
        text = '%s\nQ我要充值\nQ取消恢復' % text
        dlgnpc.ShowClientDlg(text, '', func)
        del self.m_RestoreID
        return

    def OpenBuyGoldUrl(self, url):
        import net
        net.OpenUrl(url)
        return

    def ProcessRolesData(self, pub_data_dct):
        local_data_dct = {}
        for (pid, pub_data) in pub_data_dct.items():
            if type(pid) is not int:
                continue
            local_data_dct[pid] = local_data = {}
            for (pub_key, local_key, default_value) in [('Name', 'Name', ''), ('Class', 'Class', 0),
             ('Grade', 'Grade', 0), ('Cost', 'Cost', 0)]:
                if pub_key not in pub_data:
                    local_data[local_key] = default_value
                else:
                    local_data[local_key] = pub_data[pub_key]

        return local_data_dct

    def RequestRestoreRole(self, pid):
        self.m_RestoreID = pid
        self.C2SGetCanPayRoles(pid)
        return

    def OnRoleAdd(self, pid):
        if pid not in self.RESTORING_LST:
            return
        self.RESTORING_LST.remove(pid)
        self.ShowSuccess(pid)
        return

    def ShowSuccess(self, pid):
        import commondialog
        name = self.GetExistRoleName(pid)
        commondialog.ShowNewMessageBox('您的角色#G%s#n已經成功恢復！' % name, '確定')
        return

    def OnClear(self):
        self.RESTORING_LST = []
        return


class CRestoreRoleDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/restorerole.dlg')
        interface.Center(self)
        self.m_SelectID = self.m_SelectCost = 0
        return

    def CloseWindow(self):
        import dlgnpc
        dlgnpc.CloseClientNpc()
        return

    def Refresh(self, data):
        oTable = self.GetObject('table_Roles')
        oTable.InitStyle('TABLE_STYLE_4')
        oTable.Clear()
        pid_lst = data.keys()
        pid_lst.sort(key=(lambda pid: data[pid]['Grade']), reverse=True)
        pos = 0
        for (idx, pid) in enumerate(pid_lst):
            dct = data[pid]
            texts = self.GetItemTexts(pid, dct)
            itemobj = oTable.AddTextItem(texts)
            itemobj.m_Pid = pid
            itemobj.m_Cost = dct['Cost']
            if pid == self.m_SelectID:
                pos = idx
                itemobj.LeftUp()

        pos = min(pos, len(pid_lst) - oTable.m_Row)
        oTable.ResetItems(pos)
        oTable.ResetScrollBar()
        if hasattr(oTable, 'm_VScrollBar'):
            oTable.m_VScrollBar.SetBarPos(pos)
        if self.m_SelectID in data:
            self.m_SelectCost = data[self.m_SelectID]['Cost']
        else:
            self.m_SelectID = self.m_SelectCost = 0
        return

    def GetItemTexts(self, pid, dct):
        import hero, createrole
        iClass = dct['Class']
        sClass = '未知'
        if iClass < 3:
            sClass = ('戰士', '法師', '術士')[iClass]
        sGrade = '%d級' % dct['Grade']
        return ['%d' % pid, dct['Name'], sClass, sGrade, '%d世貢' % dct['Cost']]

    def RequestRestoreRole(self, msgid):
        if msgid != 1:
            return
        if not self.m_SelectID:
            return
        if g_Mgr:
            g_Mgr.RequestRestoreRole(self.m_SelectID)
        Show(False)
        return

    def OnMessage(self, msgid):
        if msgid in (2, 3):
            Close()
        elif msgid == 1:
            import dlgnpc
            text = '找回該角色需要花費%d世貢\nQ從角色擁有的世貢中扣除\nQ取消恢復' % self.m_SelectCost
            dlgnpc.ShowClientDlg(text, '', self.RequestRestoreRole)
        elif 100 <= msgid < 200:
            table = self.GetObject('table_Roles')
            idx = msgid - 101
            itemobj = table.m_Items[idx]
            self.m_SelectID = itemobj.m_Pid
            self.m_SelectCost = itemobj.m_Cost
        return


def GetTestData():
    return {1111111: {'Name': 'name111', 'Grade': 30, 'Class': 2, 'Cost': 200}, 111222: {'Name': 'name222', 'Grade': 40, 'Class': 3, 'Cost': 300}, 111333: {'Name': 'name3', 'Grade': 42, 'Class': 6, 'Cost': 400}, 111444: {'Name': 'name4', 'Grade': 22, 'Class': 4, 'Cost': 500}, 111555: {'Name': 'name5', 'Grade': 23, 'Class': 4, 'Cost': 500}, 111666: {'Name': 'name6', 'Grade': 27, 'Class': 4, 'Cost': 500}, 111777: {'Name': 'name7', 'Grade': 11, 'Class': 4, 'Cost': 500}, 111888: {'Name': 'name8', 'Grade': 90, 'Class': 4, 'Cost': 500}, 111999: {'Name': 'name9', 'Grade': 199, 'Class': 4, 'Cost': 500}, 1122: {'Name': 'name12', 'Grade': 199, 'Class': 4, 'Cost': 500}, 1133: {'Name': 'nam13', 'Grade': 199, 'Class': 4, 'Cost': 500}, 1155: {'Name': 'name14', 'Grade': 199, 'Class': 4, 'Cost': 500}, 1166: {'Name': 'name14', 'Grade': 199, 'Class': 4, 'Cost': 500}}


def Test():
    global g_Mgr
    if not g_Mgr:
        g_Mgr = CMgr()
    data = GetTestData()
    data = g_Mgr.ProcessRolesData(data)
    g_Mgr.ShowRolesInfo(data)
    return


return
