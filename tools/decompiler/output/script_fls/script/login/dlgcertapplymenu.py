# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dlgcertapplymenu.py
import combdialog, interface
g_CertApplyMenuDlg = None

def ModuleReset():
    global g_CertApplyMenuDlg
    g_CertApplyMenuDlg = None
    return


class CCertApplyDialog(combdialog.CCombDialog):

    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'login/cert/certapply.dlg')
        self.m_DlgHelpID = 5040
        interface.Center(self)
        return

    def CloseWindow(self):
        global g_CertApplyMenuDlg
        g_CertApplyMenuDlg = None
        return

    def BindNewPhone(self):
        import loginin
        if loginin.g_User and loginin.g_User.endswith('@2980.com'):

            def Func(msgid):
                if msgid == 1:
                    import net, gameurl
                    net.OpenUrl(gameurl.MAIN2980_URL)
                return

            msg = b'5>?7\xa2\xc9\xa3\xe6\xa2n\xa2O\xb2i\xb8\xfa\xb1k\xbad\xc4\xf1\xc6w\xb0t\xa3\xe5\xb9\xf0\xa6Z\xb2i\xb8\xfa\xb1k\xbad\xac\xe6\xa1e\xa6r\xb4Z\xbfj\xa6\xf0\xb6e\xa3\xe6\xa6\xf0\xc4\xf1\xc6w\xa3\xe5\xb9\xf0\xa6q\xb2\xe1\xb4\xe1\xa3\xa3\xb9\xd9\xa0@\xa1^\nQ\xb5n\xbf\xfd2980\xb6l\xbdc\nQ\xbc\xc8\xa4\xa3\xb3B\xb2z\n'
            import dlgnpc
            dlgnpc.ShowClientDlg(msg, '', Func)
        else:
            import netlogin
            netlogin.C2SBindNewPhone()
        return

    def OnMessage(self, msgid):
        if msgid == 2:
            self.CloseWindow()
        elif msgid == 5:
            import netcert
            netcert.C2SApplyCert()
            self.CloseWindow()
        elif msgid == 6:
            msg = b'\xbd\xf5\xa6\xd9\xadT\xa7\xe8\xb3X\xbb_\xa3`+z9&\xae\xa0\xadT\xad\xdb\xb5\xd8\xbd\xf5\xa6\xd9\xa7\xe8\xae\xbb\xa6\xcc\xaei\xa3G\xbd\xf5\xb9j\xb0\xb1\xae\x7f\xad\xf6\xa9K\xb9j\xb0\xb1\xaej\xa0[\xae\xb3\xac\xdb\xc0\xb3\xb5\xfd\xae\xd1\xaa\xba\xb9q\xb8\xa3\xa4W\xb5L\xaak\xb5n\xbf\xfd\xa1C#r2.\xa8C\xad\xd3\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xa5i\xa5H\xa6b\xa4\xa3\xa6P\xaa\xba\xb9q\xb8\xa3\xa4W\xa5\xd3\xbd\xd0\xb3\xcc\xa6h30\xad\xd3\xb5\xfd\xae\xd1\xa1C#r3.\xb5\xfd\xae\xd1\xa5\xd3\xbd\xd0\xa6\xa8\xa5\\\xa4\xa7\xab\xe1\xa1A\xa5\xbb\xa5x\xb9q\xb8\xa3\xb1N\xa5\xc3\xa4[\xabO\xa6s\xb5\xfd\xae\xd1\xa1C\xb5\xfd\xae\xd1\xb5L\xaak\xb3q\xb9L\xb2\xbe\xb0\xca\xb3]\xb3\xc6\xab\xfe\xa8\xa9\xa1C\xa6p\xbb\xdd\xa6b\xa8\xe4\xa5L\xb9q\xb8\xa3\xa4W\xb5n\xa4J\xb9C\xc0\xb8\xabh\xbb\xdd\xadn\xad\xab\xb7s\xc5\xe7\xb5\xfd\xa5\xd3\xbd\xd0\xa1C#r4.\xa6\xa8\xa5\\\xa5\xd3\xbd\xd0\xb5\xfd\xae\xd1\xab\xe1\xa5i\xa5H\xb3q\xb9L\xa1u\xba\xde\xb2z\xb5\xfd\xae\xd1\xa1v\xa8\xd3\xb1\xb1\xa8\xee\xb5\xfd\xae\xd1\xa8\xcf\xa5\xce\xbdd\xb3\xf2\xa5H\xa4\xce\xb5\xfd\xae\xd1\xbc\xc6\xb6q\xa1C'
            import commondialog
            commondialog.ShowNewMessageBox(msg, ('確定', ), (None, ))
            commondialog.g_MessageBox.m_Font = interface.FontHT12
            commondialog.g_MessageBox.SetMessage(msg)
            self.CloseWindow()
        elif msgid == 7:
            self.BindNewPhone()
        elif msgid == 8:
            self.CloseWindow()
        return


def Show(isShow=True):
    global g_CertApplyMenuDlg
    if not g_CertApplyMenuDlg:
        g_CertApplyMenuDlg = CCertApplyDialog()
    return


return
