# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\delrolever2.py
import pubdelrole
g_DelRole = None

def ModuleReset():
    global g_DelRole
    g_DelRole = None
    return


def S2CProcessVersion2(netobj):
    oDelrole = GetDelRoleMgr()
    oDelrole.S2CProcess(netobj)
    return


def GetDelRoleMgr():
    global g_DelRole
    if not g_DelRole:
        g_DelRole = CDelRole()
    return g_DelRole


class CDelRole(pubdelrole.CDelRole, pubdelrole.CNet):

    def GetTimeText(self, delTime):
        import misc
        curTime = misc.GetServerCurrentTime()
        leftTime = delTime - curTime
        return misc.Int2TimeStr(leftTime, True)

    def ShowPrompt(self, msg):
        import usermacro
        usermacro.g_PromptTips[:] = []
        return usermacro.PROMPT_MSG(msg)

    def ShowInputBox(self, msg, func):
        import commondialog
        return commondialog.ShowInputDialog(msg, func)

    def ShowMessageBox(self, msg, name, func=None):
        import commondialog
        return commondialog.ShowMessageBox(msg, name, func)

    def SetDeleteStateVersion(self, dct):
        import selectrole
        selectrole.SetDeleteStateVersion2(dct)
        self.m_DelStateDct = dct
        return

    def RefreshDelState(self):
        if not hasattr(self, 'm_DelStateDct') or not self.m_DelStateDct:
            return
        if getattr(self, 'm_DelVersion', None) == 2:
            import selectrole
            selectrole.SetDeleteStateVersion2(self.m_DelStateDct)
        return

    def IsInDelState(self, pid):
        if hasattr(self, 'm_DelStateDct') and self.m_DelStateDct.get(pid, False):
            return True
        return False

    def GetRolesInfos(self):
        import netlogin
        return netlogin.g_LoginRoleInfo

    def OnInnerDelRole(self, idx):
        lst = self.GetRolesInfos()
        if idx >= len(lst):
            return
        dct = lst[idx]
        self.C2SDelPid(dct['ID'])
        return

    def PushCall(self, func, *args):
        import mainmenu
        mainmenu.PushCall(func, *args)
        return

    def AddGMMail(self, msg):
        import dlgsysmail, misc
        dlgsysmail.AddMailAndNotify(misc.Time()[:6], msg)
        return

    def SetDelVersion(self, version):
        import selectrole
        selectrole.SetDelVersion(version)
        return

    def OnS2CCancelDelSuccess(self, pid):
        print '%d角色取消刪除成功' % pid
        return

    def DelRole(self, iPid):
        import selectrole
        selectrole.DelRole(iPid)
        return

    def GetDelResultReason(self, num):
        dct = {0: '當前操作進行的條件判斷合格', 
           1: '你的帳號下已經有一個角色在申請刪除，請耐心等待！', 
           2: '無法刪除等級最高的角色', 
           3: '取消刪號，但沒有執行過請求', 
           4: '刪號，但不符合遊戲自定義條件', 
           5: '刪號，輸入的ID不正確', 
           6: '刪號，但數據中心返回失敗', 
           7: '30天內已經刪除過', 
           8: '該角色剩餘金幣＞10，請使用後再進行刪除操作', 
           31: '申請刪號成功', 
           32: b'\x81\x8f\x82{\x8f\xfa\xae\xf8\xa5\xd3\xbd\xd0', 
           33: '成功刪除角色', 
           51: '未登錄過的遊戲ID', 
           52: '該角色已經登錄遊戲，無法執行刪除操作', 
           53: '擁有房屋的情況下不能申請刪除角色', 
           54: '擁有工廠的情況下不能申請刪除角色', 
           55: '該角色存在尚未解除的婚姻關係，暫時不能申請刪除', 
           56: '該角色在幫派中，暫時不能申請刪除', 
           57: '異常登錄狀態下，無法執行刪除操作', 
           58: '查詢數據庫失敗', 
           59: '此服務器不允許刪號', 
           60: '該角色存在尚未解除的結拜關係，暫時不能申請刪除', 
           61: '角色找回30天內不能刪除', 
           62: '請勿頻繁刪除角色', 
           63: '由於該角色還在塞班島/無味書齋，不能進行刪除', 
           64: '由於該角色負債沒有還清，不能進行刪除', 
           65: '已有師徒關係無法刪除角色，請解除關係後重試'}
        return dct.get(num, '')

    def S2CDelResultReason(self, netobj):
        num = pubdelrole.CNet.S2CDelResultReason(self, netobj)
        msg = self.GetDelResultReason(num)
        self.ShowPrompt(msg)
        return

    def S2CDelrole(self, netobj):
        pid = pubdelrole.CNet.S2CDelrole(self, netobj)
        self.DelRole(pid)
        return

    def S2CWaitInfos(self, netobj):
        (scene, dct) = pubdelrole.CNet.S2CWaitInfos(self, netobj)
        if scene == 1:
            self.SetDeleteStateVersion(dct)
        elif scene == 2:
            self.OnS2CWaitInfos(dct)
        return

    def S2CCancelDelSuccess(self, netobj):
        pid = pubdelrole.CNet.S2CCancelDelSuccess(self, netobj)
        self.OnS2CCancelDelSuccess(pid)
        return

    def S2CDelRoleVersion(self, netobj):
        iOpen = pubdelrole.CNet.S2CDelRoleVersion(self, netobj)
        num = 1 if iOpen == 0 else 2
        self.m_DelVersion = num
        self.SetDelVersion(num)
        return

    def GetHeader(self, icmd):
        import netpublic
        netobj = netpublic.PacketPrepare(netpublic.C2GS_SUB_SUICIDE2)
        netobj.PacketAddI(icmd, 1)
        return netobj


return
