# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgcertlook.py
import cert, certmgr, netcert, combdialog, interface
g_CertLookDlg = None

def ModuleReset():
    global g_CertLookDlg
    g_CertLookDlg = None
    return


def Show():
    global g_CertLookDlg
    if not g_CertLookDlg:
        g_CertLookDlg = CCertLookDlg()
    return


def RefreshData(data, page, hasNext):
    if g_CertLookDlg:
        g_CertLookDlg.RefreshData(data, page, hasNext)
    return


class CTextButton(interface.CTextButton):

    def LeftUp(self):
        g_CertLookDlg.OnButtonLeftUp(self)
        return


class CCertLookDlg(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/certlook.dlg')
        interface.Center(self)
        self.m_Page = 1
        self.GetObject('btn_Prev').Enable(False)
        return

    def RefreshData(self, data, page, hasNext):
        self.m_Page = page
        pcinfo = cert.GetPCInfo()
        for i in range(len(data)):
            if data[i]['Mac'] == pcinfo:
                temp = data.pop(i)
                temp['Address'] += '(本機使用中)'
                data.insert(0, temp)
                break

        self.m_Data = data
        self.RefreshList()
        self.GetObject('txt_Num').SetText('%d/3' % self.m_Page)
        self.GetObject('btn_Next').Enable(hasNext)
        return

    def RefreshList(self):
        obj = self.GetObject('list1')
        lastp = obj.m_VScrollBar.GetPos()
        head = obj.m_Head
        obj.Clear()
        import time
        for (idx, data) in enumerate(self.m_Data):
            color = 16777110
            hot = {True: (-1), False: None}['(本機使用中)' in data['Address']]
            itemobj = obj.AddTextItem((data['Address'], data['Time'], ''), color, hot)
            itemobj.m_CloseBtn = interface.CTextButton(itemobj, 'combdialog2/偌聽/偌臟媼趼.igs', 425, -1, '刪除', 0, interface.FontLT14_3, 50 + idx)
            itemobj.m_CloseBtn.SetZ(10)
            itemobj.m_PcInfo = data['Mac']
            itemobj.m_CertID = data['CertID']

        obj.ResetScrollBar()
        obj.ResetItems(head)
        obj.m_VScrollBar.SetBarPos(lastp)
        return

    def OnHotEnter(self, itemobj):
        import wrapinterface
        self.m_Tips = wrapinterface.CTextTips(None, -1, '本機正在使用的証書', interface.FontLT12_1, direct=1)
        return

    def OnHotLeave(self, itemobj):
        if hasattr(self, 'm_Tips'):
            self.m_Tips = None
        return

    def GoPage(self, page):
        obj = self.GetObject('list1')
        obj.Clear()
        if page == 1:
            self.GetObject('btn_Prev').Enable(False)
        else:
            self.GetObject('btn_Prev').Enable(True)
        self.m_Page = page
        netcert.C2SChangePage(page)
        return

    def CloseWindow(self):
        global g_CertLookDlg
        g_CertLookDlg = None
        return

    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 3:
            self.CloseWindow()
        elif msgid == 4:
            self.GoPage(self.m_Page - 1)
        elif msgid == 5:
            self.GoPage(self.m_Page + 1)
        elif 150 <= msgid <= 200:
            tab = self.GetObject('list1')
            it = tab.m_Items[msgid - 50 - 100]

            def realDel(dlg):
                netcert.C2SDelCert(dlg.m_Page, dlg.m_Pcinfo, dlg.m_CertID)
                return

            import commondialog
            dlg = commondialog.ShowMessageBox('刪除對應地點的安全証書，將不能在該地點再次登錄，是否確定將本條証書刪除？', ('確定',
                                                                                                                                                                                                                                                                                           '取消'), (realDel, None))
            dlg.m_Page = self.m_Page
            dlg.m_Pcinfo = it.m_PcInfo
            dlg.m_CertID = it.m_CertID
        return


return
