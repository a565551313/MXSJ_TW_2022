# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\pubdelrole.py


class CNet(object):

    def S2CProcess(self, netobj):
        iSub = netobj.UnpackInt(1)
        func = self.GetFunc(iSub)
        print '新版角色刪除協議iSub-----', iSub
        if func:
            func(netobj)
        else:
            print '沒有正在監聽的協議號', iSub
        return

    def GetFunc(self, iSub):
        dFuncs = {1: (self.S2CDelResultReason), 2: (self.S2CDelResultReason), 
           3: (self.S2CDelrole), 
           4: (self.S2CWaitInfos), 
           5: (self.S2CCancelDelSuccess), 
           6: (self.S2CDelRoleVersion)}
        return dFuncs.get(iSub, None)

    def S2CDelResultReason(self, netobj):
        num = netobj.UnpackInt(1)
        return num

    def S2CDelrole(self, netobj):
        pid = netobj.UnpackInt(4)
        return pid

    def S2CWaitInfos(self, netobj):
        scene = netobj.UnpackInt(1)
        icount = netobj.UnpackInt(1)
        dct = {}
        for _ in range(icount):
            pid = netobj.UnpackInt(4)
            ileft = netobj.UnpackInt(4)
            dct[pid] = ileft

        return (
         scene, dct)

    def S2CCancelDelSuccess(self, netobj):
        pid = netobj.UnpackInt(4)
        return pid

    def S2CDelRoleVersion(self, netobj):
        iOpen = netobj.UnpackInt(1)
        return iOpen

    def GetHeader(self, icmd):
        raise '發送C2S協議頭,各項目組自行實現'
        return

    def C2SDelPid(self, pid):
        netobj = self.GetHeader(2)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()
        return

    def C2SCancelDel(self, pid):
        netobj = self.GetHeader(3)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()
        return


class CDelRole(object):

    def GetTimeText(self, left_time):
        raise '各項目自定義'
        return

    def ShowPrompt(self, msg):
        raise '漂浮消息提示,各項目組自行實現'
        return

    def ShowInputBox(self, msg, func):
        raise '顯示輸入條,各項目組自行實現'
        return

    def ShowMessageBox(self, msg, name, func=None):
        raise '顯示消息提示框,各項目組自行實現'
        return

    def SetDeleteStateVersion(self, dct):
        raise '設置刪除狀態版本,各項目組自行實現'
        return

    def GetRolesInfos(self):
        raise '得到自己的角色信息列表，各項目組自行實現'
        return

    def PushCall(self, func, *args):
        raise '把func函數保存起來裡，*args為func的參數等登錄後,才執行顯示,各項目自行實現'
        return

    def AddGMMail(self, msg):
        raise '添加郵件，各項目自行實現'
        return

    def SetDelVersion(self, version):
        raise '設置刪除版本，各項目自行實現'
        return

    def DelRole(self, pid):
        raise '刪除角色，各項目自行實現'
        return

    def OnRequestDelRole(self, pid, grade, gradelst, fastgrade, C2SDelPid):
        if not gradelst:
            return
        if max(gradelst) == grade:
            msg = '無法刪除等級最高的角色'
            self.ShowPrompt(msg)
            return

        def FastDel(dlg, text):
            if text.isdigit() and int(text) == dlg.m_ID:
                C2SDelPid(dlg.m_ID)
            else:
                self.ShowPrompt('請輸入正確的角色ID')
            return

        def SlowDel(dlg):
            C2SDelPid(dlg.m_ID)
            return

        if grade < fastgrade:
            dlg = self.ShowInputBox('請輸入你要刪除的角色ID，角色刪除後可能會無法恢復，請謹慎操作。', FastDel)
            dlg.m_ID = pid
        else:
            dlg = self.ShowMessageBox('#Y成功申請刪除角色7天後，該角色將會自動刪除。#n#r你確定要申請刪除該角色嗎？角色刪除後可能會無法恢復，請謹慎操作。', ('確定',
                                                                                                                                                                                                                                                                                                                                                                                                                       '取消'), (SlowDel, None))
            dlg.m_ID = pid
        return

    def OnCancelDelRole(self, pid, tm, C2SCancelDel):

        def CancelDel(dlg):
            C2SCancelDel(dlg.m_ID)
            return

        txt = b'\xf8\x82j\xa1\x7f\xac~\x08f\x0b|\x89kxc\x08s\x7f}9z\x9ai\xa0}\xb9h\x99r(\xf8\x89}\x00k\x11|\x89kxn~p\x06o\x1a\xf8\xb5z\x86\xf8\x89\x1a\x02h\ne\xb7\xfe\xa8\xf8\xb5z\x85z\x9an\xa5\xab\xdd\xb4\xc1\xa4\xba\xa5i\xc0H\xae\xc9\xa8\xfa\xae\xf8\xa5\xd3\xbd\xd0\xa1C\xb9O\xb4\xc1\xa5\xbc\xbdT\xbb{\xabh\xa6\xdb\xb0\xca\xa7R\xb0\xa3\xa8\xa4\xa6\xe2\xa1C#n' % self.GetTimeText(tm)
        dlg = self.ShowMessageBox(txt, ('取消申請', '繼續等待'), (CancelDel, None))
        dlg.m_ID = pid
        return

    def OnS2CWaitInfos(self, dct):
        txt_lst = []
        for info in self.GetRolesInfos():
            pid = info['ID']
            if pid not in dct:
                continue
            left_time = dct[pid]
            if left_time:
                txt_lst.append('本帳號下的角色#c00FFFF%s#n（ID%d）已經申請了角色刪除，現在處於#R自動刪除等待期（還剩餘%s）#n，' % (
                 info['Name'], pid, self.GetTimeText(left_time)))

        if txt_lst:
            self.PushCall(self.AddGMMail, ('#r').join(txt_lst))
        return


return
