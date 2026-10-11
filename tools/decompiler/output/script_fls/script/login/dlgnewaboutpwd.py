# -*- coding: utf-8 -*-
# Source Generated with Decompyle++
# File: tmp5fnonb0g.pyc (Python 2.5)

'''\n================================================================================\n奀潔: 2020/9/14 20:22\n釬氪: wz\n恅璃: dlgnewaboutpwd\n賡庄ㄩ\n================================================================================\n'''
import C_sys
import combdialog
import interface
import misc
import permission
import slot
import gameurl

def GetPassWordUrl():
    if permission.IsInNet():
        sUrl = gameurl.URL_FINDPASSWORD['測試找回密碼']
    else:
        sUrl = gameurl.URL_FINDPASSWORD['正式找回密碼']
    return sUrl


class CNewAboutPwdDlg(combdialog.CCombDialog, slot.ISignalSubject):
    sUIName = 'dialog4/register/main_bg.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel)
        self.ssInit()
        interface.Center(self)
        self.Capture(1, 0)
        self.InitDlg()
        self.m_DelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        self.m_DelegateList = []

    
    def Hold(self):
        pass

    
    def InitDlg(self):
        self.GetObject('rtxt_webopen').ReplaceText({
            '$website': gameurl.URL_FINDPASSWORD['官網找回密碼'] })
        oBg = self.GetObject('loc_item')
        while None:
            (x, y) = oBg()
            (w, h) = oBg.GetSize()
            self.m_oCefWidget = interface.CCefObject(x, y, w, h, GetPassWordUrl(), None, None, '', 1)
            if hasattr(self.m_oCefWidget, 'SetPopupCB'):
                self.m_oCefWidget.SetPopupCB(misc.Functor(self.WebOpen))
            

    
    def WebUrlForward(self):
        self.m_oCefWidget.RunJSCode('window.history.forward()')

    
    def WebUrlBack(self):
        self.m_oCefWidget.RunJSCode('window.history.back()')

    
    def WebOpen(self, sUrlList):
        for sUrl in sUrlList:
            C_sys.OpenUrl(sUrl)
        

    
    def OpenWeb(self):
        C_sys.OpenUrl(gameurl.URL_FINDPASSWORD['官網找回密碼'])

    
    def CloseWindow(self):
        self.CloseUI()

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseUI()
        elif iMsgID == 2:
            self.OpenWeb()
        elif iMsgID == 3:
            self.WebUrlBack()
        elif iMsgID == 4:
            self.WebUrlForward()
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)


