# pycdc 交叉复核产物 · script.fls entry 1017
# co_filename(原始)='script/login/dlgnewaboutpwd.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1017.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/9/14 20:22
\xd7\xf7\xd5\xdf: wz
\xce\xc4\xbc\xfe: dlgnewaboutpwd
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import C_sys
import combdialog
import interface
import misc
import permission
import slot
import gameurl

def GetPassWordUrl():
    if permission.IsInNet():
        sUrl = gameurl.URL_FINDPASSWORD['\xb4\xfa\xb8\xd5\xa7\xe4\xa6^\xb1K\xbdX']
    else:
        sUrl = gameurl.URL_FINDPASSWORD['\xa5\xbf\xa6\xa1\xa7\xe4\xa6^\xb1K\xbdX']
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
            '$website': gameurl.URL_FINDPASSWORD['\xa9x\xba\xf4\xa7\xe4\xa6^\xb1K\xbdX'] })
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
        C_sys.OpenUrl(gameurl.URL_FINDPASSWORD['\xa9x\xba\xf4\xa7\xe4\xa6^\xb1K\xbdX'])

    
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
