# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgnewgetbackaccount.py
r"""
================================================================================
ʱ\xbc\xe4: 2020/10/28 16:01
\xd7\xf7\xd5\xdf: lzj
\xceļ\xfe: dlgnewgetbackaccount
\xbd\xe9\xc9ܣ\xba
================================================================================
"""
import C_sys, combdialog, gameurl, interface, misc, permission, pubtoolkit

def GetBackAccountUrl():
    mac = pubtoolkit.GetMAC()
    if permission.IsInNet():
        sUrl = gameurl.URL_FINDACCOUNT['測試找回賬號'] + str(mac)
    else:
        sUrl = gameurl.URL_FINDACCOUNT['正式找回賬號'] + str(mac)
    return sUrl


class CNewGetBackAccountDlg(combdialog.CCombDialog):
    sUIName = 'dialog4/register/main_bg.dlg'

    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel)
        interface.Center(self)
        self.Capture(1, 0)
        self.m_oCefWidget = None
        self.InitDlg()
        return

    def Hold(self):
        return

    def InitDlg(self):
        self.GetObject('text_title').SetShow(False)
        self.GetObject('rtxt_webopen').SetShow(False)
        oBg = self.GetObject('loc_item')
        (x, y) = oBg.GetScreenPos()
        (w, h) = oBg.GetSize()
        self.m_oCefWidget = interface.CCefObject(x, y, w, h, GetBackAccountUrl(), None, None, '', 1)
        if hasattr(self.m_oCefWidget, 'SetPopupCB'):
            self.m_oCefWidget.SetPopupCB(misc.Functor(self.WebOpen))
        return

    def WebUrlForward(self):
        self.m_oCefWidget.RunJSCode('window.history.forward()')
        return

    def WebUrlBack(self):
        self.m_oCefWidget.RunJSCode('window.history.back()')
        return

    def WebOpen(self, sUrlList):
        for sUrl in sUrlList:
            C_sys.OpenUrl(sUrl)

        return

    def ColseWindow(self):
        self.CloseUI()
        return

    def OpenWeb(self):
        mac = pubtoolkit.GetMAC()
        C_sys.OpenUrl(gameurl.URL_FINDACCOUNT['正式找回賬號'] + str(mac))
        return

    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.ColseWindow()
        elif iMsgID == 2:
            self.OpenWeb()
        elif iMsgID == 3:
            self.WebUrlBack()
        elif iMsgID == 4:
            self.WebUrlForward()
        return

    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)
        return


return
