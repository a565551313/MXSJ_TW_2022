# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\point2month.py
import C_object, interface, wrapinterface, combdialog
DAYS = [
 2, 3, 4, 5, 6, 7, 8, 9, 10]
POINTS = [11, 12, 13, 14, 15, 16, 17, 18, 19]
g_RoleIdx = -1

def Show(flag, idx=-1):
    global g_Point2Month
    global g_RoleIdx
    if idx >= 0:
        g_RoleIdx = idx
    if flag:
        import selectserver
        if selectserver.g_ServerVersion != 2:
            g_Point2Month = CPoint2Month(interface.DialogPanel)
        else:
            g_Point2Month = CPoint2Point(interface.DialogPanel)
    else:
        g_Point2Month = None
    return


class _ListBox(interface.CListBox):

    def AddChar(self, char):
        interface.CListBox.AddChar(self, char)
        txt = self.GetText()
        if txt in DAYS:
            self.GetParent().SetNeedPoint(int(txt[:2]))
        else:
            self.GetParent().SetNeedPoint(0)
        return

    def DeleteChar(self):
        interface.CListBox.DeleteChar(self)
        txt = self.GetText()
        if txt in DAYS:
            self.GetParent().SetNeedPoint(int(txt[:2]))
        else:
            self.GetParent().SetNeedPoint(0)
        return

    def Active(self, flag):
        interface.CListBox.Active(self, False)
        return


class CPoint2Month(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/point2month.dlg')
        import netlogin
        try:
            roleinfo = netlogin.g_LoginRoleInfo[g_RoleIdx]
        except KeyError:
            return

        import combmacro
        self.m_ID = roleinfo['ID']
        self.m_NameTxtObj = combmacro.CTEXT(C_object.CTextObject, 'name', self, '%s (%d)' % (roleinfo['Name'], self.m_ID), interface.FONT_DEFAULT, 0)
        if roleinfo['time'] == 0:
            maxdays = 90
        elif roleinfo['time'] == 1:
            maxdays = 0
        else:
            remain_time = roleinfo['time'] - netlogin.g_CurrentTime
            day_seconds = 86400
            if remain_time % day_seconds == 0:
                maxdays = 90 - remain_time / day_seconds
            else:
                maxdays = 89 - remain_time / day_seconds
        obj = self.GetObject('time')
        (w, h) = obj.GetSize()
        (x, y) = obj.GetPos()
        self.m_DaysEdit = _ListBox(self, 0, interface.FontLT14E_1, x, y, w, h, 'login/down_arrow.igs')
        self.m_DaysEdit.SetDownButtonPos(208, 1)
        self.m_DaysEdit.SetItemProp(2, 14, 64)
        for txt in DAYS:
            if int(txt[:2]) <= maxdays:
                self.m_DaysEdit.AddTextItem(txt)

        self.m_DaysEdit.SetText('10天')
        self.SetNeedPoint(10)
        balance = netlogin.g_Balance
        self.m_Balance = combmacro.CTEXT(C_object.CTextObject, 'remain', self, '%d' % balance, interface.FONT_DEFAULT, 0)
        if roleinfo['time'] in (0, 1):
            self.m_RemainTim = None
        else:
            import time
            if netlogin.g_CurrentTime == None or roleinfo['time'] < 1100000000:
                self.m_RemainTim = combmacro.CTEXT(C_object.CTextObject, 'remain_time', self, '已過期', interface.FONT_DEFAULT, 0)
            else:
                txt = '%d年%d月%d日 %02d:%02d:%02d' % time.localtime(roleinfo['time'])[:6]
                self.m_RemainTim = combmacro.CTEXT(C_object.CTextObject, 'remain_time', self, txt, interface.FONT_DEFAULT, 0)
        (x, y) = self.GetObject('confirm').GetPos()
        self.m_OK = wrapinterface.CLoginButton(self, 'login/btn_normal.igs', x, y, '確認轉換', 1)
        (x, y) = self.GetObject('back').GetPos()
        self.m_Return = wrapinterface.CLoginButton(self, 'login/btn_normal.igs', x, y, '返 回', 2)
        return

    def SetNeedPoint(self, day):
        import combmacro
        if day == 0:
            self.m_NeedPoint = None
        else:
            self.m_NeedPoint = combmacro.CTEXT(C_object.CTextObject, 'need', self, '%d' % (day * 15), interface.FONT_DEFAULT, 0)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import netlogin
            daytxt = self.m_DaysEdit.GetText()
            if daytxt not in DAYS:
                return
            self.m_OK.Enable(False)
            import commondialog
            commondialog.ShowMessageBox('正在轉換中', '確定')
            netlogin.C2SExchgGameTime(self.m_ID, int(daytxt[:2]))
        elif msgid == 2:
            Show(False)
            import selectrole
            selectrole.Show(True)
        return


class CPoint2Point(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/point2point.dlg')
        import netlogin
        try:
            roleinfo = netlogin.g_LoginRoleInfo[g_RoleIdx]
        except KeyError:
            return

        import combmacro
        self.m_ID = roleinfo['ID']
        self.m_NameTxtObj = combmacro.CTEXT(C_object.CTextObject, 'name', self, '%s (%d)' % (roleinfo['Name'], self.m_ID), interface.FONT_DEFAULT, 0)
        if roleinfo['time'] == 1:
            maxpoints = 0
        else:
            maxpoints = (1350 - roleinfo['Point']) / 150 * 150
        obj = self.GetObject('point')
        (w, h) = obj.GetSize()
        (x, y) = obj.GetPos()
        self.m_PointsEdit = interface.CListBox(self, 0, interface.FontLT14E_1, x, y, w, h, 'combdialog/偌聽/腎翻狟硌渀.igs')
        self.m_PointsEdit.SetReadOnly(True)
        self.m_PointsEdit.SetDownButtonPos(w, -2)
        self.m_PointsEdit.SetItemProp(2, 14, 64)
        for v in POINTS:
            if v <= maxpoints:
                self.m_PointsEdit.AddTextItem(str(v))
                if len(self.m_PointsEdit.GetText()) == 0:
                    self.m_PointsEdit.SetText(str(v))

        balance = netlogin.g_Balance
        self.m_Balance = combmacro.CTEXT(C_object.CTextObject, 'remain', self, '%d' % balance, interface.FONT_DEFAULT, 0)
        if roleinfo['time'] == 1:
            self.m_RemainPoint = combmacro.CTEXT(C_object.CTextObject, 'remain_point', self, '免費', interface.FONT_DEFAULT, 0)
        else:
            self.m_RemainPoint = combmacro.CTEXT(C_object.CTextObject, 'remain_point', self, str(roleinfo['Point']), interface.FONT_DEFAULT, 0)
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            import netlogin
            try:
                point = int(self.m_PointsEdit.GetText())
            except:
                point = 0
            else:
                if point not in POINTS:
                    return
                self.GetObject('btn_confirm').Enable(False)
                import commondialog
                commondialog.ShowMessageBox('正在轉換中', '確定')
                netlogin.C2SExchgGamePoint(self.m_ID, point)
        elif msgid == 2:
            Show(False)
            import selectrole
            selectrole.Show(True)
        return


return
