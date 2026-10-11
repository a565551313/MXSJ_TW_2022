# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\pwdcard.py
import C_object, interface, wrapinterface, combdialog, combmacro

class CPwdCard(combdialog.CCombPanel):

    def __init__(self, parent, n1, n2, n3):
        combdialog.CCombPanel.__init__(self, parent, 'login/pwdcard.dlg')
        self.btn_name = []
        self.btn_pos = []
        for i in xrange(10):
            name = 'btn_%d' % i
            self.btn_name.append(name)
            self.btn_pos.append(self.GetObject(name).GetPos())

        self.m_txtPos = []
        self.m_txtPos.append(combmacro.CTEXT(C_object.CTextObject, 'loc_1', self, '%s%d' % (chr(ord('A') + n1[0]), n1[1]), interface.FontLT14E_1, interface.COLOR_1, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
        self.m_txtPos.append(combmacro.CTEXT(C_object.CTextObject, 'loc_2', self, '%s%d' % (
         chr(ord('A') + n2[0]), n2[1]), interface.FontLT14E_1, interface.COLOR_1, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
        self.m_txtPos.append(combmacro.CTEXT(C_object.CTextObject, 'loc_3', self, '%s%d' % (chr(ord('A') + n3[0]), n3[1]), interface.FontLT14E_1, interface.COLOR_1, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
        import random
        (w, h) = self.GetObject('noname12').GetSize()
        self.SetPos(random.randint(0, 800 - w), random.randint(0, 600 - h))
        self.RandomButton()
        self.Capture(1, 0)
        self.m_pwd = ''
        return

    def RandomButton(self):
        import copy, random
        btn_name = copy.deepcopy(self.btn_name)
        for (x, y) in self.btn_pos:
            name = btn_name[random.randint(0, len(btn_name) - 1)]
            btn_name.remove(name)
            self.GetObject(name).SetPos(x, y)

        return

    def ShowPwd(self):
        _tname = ('txt_pwd1', 'txt_pwd2', 'txt_pwd3')
        self.m_txtPwd = []
        for i in xrange(0, len(self.m_pwd), 2):
            self.m_txtPwd.append(combmacro.CTEXT(C_object.CTextObject, _tname[i / 2], self, self.m_pwd[i:i + 2], interface.FontLT14E_1, interface.COLOR_1, align=interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))

        return

    def OnMessage(self, msgid):
        if msgid in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
            if len(self.m_pwd) < 6:
                self.m_pwd += str(msgid % 10)
                self.ShowPwd()
                self.RandomButton()
        elif msgid == 11:
            self.m_pwd = self.m_pwd[:-1]
            self.ShowPwd()
            self.RandomButton()
        elif msgid == 12:
            n1 = int(self.m_pwd[0:2])
            n2 = int(self.m_pwd[2:4])
            n3 = int(self.m_pwd[4:6])
            import netlogin
            netlogin.C2SPwdCard(n1, n2, n3)
            Hide()
        return


def Show(n1, n2, n3):
    global g_PwdCard
    g_PwdCard = CPwdCard(interface.MxvPanel, (n1 / 10 - 1, n1 % 10), (n2 / 10 - 1, n2 % 10), (n3 / 10 - 1, n3 % 10))
    return


def Hide():
    global g_PwdCard
    g_PwdCard = None
    return


return
