# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgnewregister.py
r"""
================================================================================
ʱ\xbc\xe4: 2020/9/14 20:22
\xd7\xf7\xd5\xdf: wz
\xceļ\xfe: dlgnewregister
\xbd\xe9\xc9ܣ\xba
================================================================================
"""
import combdialog, interface, C_sys, misc, permission, gameurl

def GetRegisterUrl():
    if permission.IsInNet():
        sUrl = gameurl.URL_REGIRSTER['測試註冊']
    else:
        sUrl = gameurl.URL_REGIRSTER['正式註冊']
    return sUrl


class CNewRegisterDlg(combdialog.CCombDialog):
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
        self.GetObject('rtxt_webopen').ReplaceText({'$website': (gameurl.URL_REGIRSTER['官網註冊'])})
        oBg = self.GetObject('RQc_item')
        (x, y) = oBg.GetScreenPos()
        (w, h) = oBg.GetSize()
        self.m_oCefWidget = interface.CCefObject(x, y, w, h, GetRegisterUrl(), None, None, '', 1)
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

    def OpenWeb(self):
        C_sys.OpenUrl(gameurl.URL_REGIRSTER['官網註冊'])
        return

    def CloseWindow(self):
        self.CloseUI()
        return

    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseUI()
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
