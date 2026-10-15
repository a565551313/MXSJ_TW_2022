# pycdc 交叉复核产物 · script.fls entry 4200
# co_filename(原始)='script/dialog/dlgbandip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4200.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import wrapinterface
g_BandDlg = None

def ModuleReset():
    global g_BandDlg
    g_BandDlg = None


class CBandDialog(combdialog.CCombDialog):
    
    def __init__(self, ip, lastip, bands):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/bandip/band.dlg')
        interface.Center(self)
        self.m_BandIP = []
        if \x8een(bands) > 0:
            for s in bands.split(','):
                self.m_BandIP.append(s.split('.'))
            
        
        self.m_txtHistory = []
        for r, v in enumerate(lastip):
            for c, n in enumerate(v):
                if c == 3:
                    n = '*'
                
                self.m_txtHistory.append(combmacro.CIFTEXT(interface.CTextObject, 'txt_history', self, r, c, str(n), interface.FontLT14_3, interface.COLOR_5))
            
        
        self.m_CurrentIP = ip
        self.m_txtIP = []
        for c, n in enumerate(ip):
            if c == 3:
                n = '*'
            
            self.m_txtIP.append(combmacro.CIFTEXT(interface.CTextObject, 'txt_ip', self, 0, c, str(n), interface.FontLT14_3, interface.COLOR_5))
        
        self.m_edtAdd = []
        for s in ('edt_add1', 'edt_add2', 'edt_add3', 'edt_add4'):
            edt = combmacro.CEDIT(wrapinterface.CNumberEdit, s, self, interface.COLOR_5, interface.FontLT14_3)
            edt.SetLimit(3)
            self.m_edtAdd.append(edt)
        
        for s in ('chk_band1', 'chk_band2', 'chk_band3', 'chk_band4'):
            self.GetObject(s).SetSelect(True)
        
        for s in ('chk_band1', 'chk_band2'):
            self.GetObject(s).Enable(False)
        
        self.ShowBandIP()

    
    def ShowBandIP(self):
        self.m_txtBandIP = []
        for r, v in enumerate(self.m_BandIP):
            for c, n in enumerate(v):
                if n != '0' and c != 3:
                    self.m_txtBandIP.append(combmacro.CIFTEXT(interface.CTextObject, 'txt_bandip', self, r, c, str(n), interface.FontLT14_3, interface.COLOR_5))
                    continue
                self.m_txtBandIP.append(combmacro.CIFTEXT(interface.CTextObject, 'txt_bandip', self, r, c, '*', interface.FontLT14_3, interface.COLOR_5))
            
        

    
    def CloseWindow(self):
        for edt in self.m_edtAdd:
            edt.Active(False)
        
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        if msgid == 15:
            ip = []
            for idx, s in enumerate(('chk_band1', 'chk_band2', 'chk_band3', 'chk_band4')):
                if self.GetObject(s).IsSelected():
                    ip.append(str(self.m_CurrentIP[idx]))
                    continue
                ip.append(str(0))
            
            if \x8een(self.m_BandIP) >= 5:
                import usermacro
                usermacro.PROMPT_MSG('\xb3\xcc\xa6h\xa5u\xaf\xe0\xb8j\xa9w5\xad\xd3ip\xacq')
                return None
            
            if ip == [
                '0',
                '0',
                '0',
                '0']:
                import usermacro
                usermacro.PROMPT_MSG('\xb3\xcc\xa4\xd6\xbb\xdd\xadn\xb8j\xa9w\xa4@\xad\xd3\xacq')
                return None
            
            if ip[2] == '0' and ip[3] != '0':
                import usermacro
                usermacro.PROMPT_MSG('\xb7\xed\xb2\xc4\xa4T\xacq\xa4\xa3\xb8j\xa9w\xae\xc9,\xb2\xc4\xa5|\xacq\xa4]\xa4\xa3\xa5i\xa5H\xb8j\xa9w')
                return None
            
            
            try:
                self.m_BandIP.remove(ip)
            except:
                pass

            self.m_BandIP.append(ip)
            self.ShowBandIP()
        elif msgid == 14:
            ip = []
            for idx, edt in enumerate(self.m_edtAdd):
                
                try:
                    t = int(edt.GetText())
                except:
                    t = 0

                if t <= t:
                    pass
                elif t <= 255:
                    ip.append(str(t))
                    continue
                import usermacro
                usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa5\xbf\xbdT\xaa\xbaip\xa1A\xa6U\xacq\xbc\xc6\xa6r\xc0\xb3\xa6b0~255\xa4\xa7\xb6\xa1')
                return None
            
            if \x8een(self.m_BandIP) >= 5:
                import usermacro
                usermacro.PROMPT_MSG('\xb3\xcc\xa6h\xa5u\xaf\xe0\xb8j\xa9w5\xad\xd3ip\xacq')
                return None
            
            if ip[0] == '0' or ip[1] == '0':
                import usermacro
                usermacro.PROMPT_MSG('\xabe\xa8\xe2\xacq\xbc\xc6\xa6r\xa5\xb2\xb6\xb7\xb6\xf1\xbcg\xa5B\xa4\xa3\xa4\xb9\xb3\\\xac\xb00')
                return None
            
            if ip[2] == '0' and ip[3] != '0':
                import usermacro
                usermacro.PROMPT_MSG('\xb3]\xa9w\xb2\xc4\xa4T\xacq\xac\xb00\xae\xc9,\xb2\xc4\xa5|\xacq\xa5\xb2\xb6\xb7\xa4]\xac\xb00')
                return None
            
            
            try:
                self.m_BandIP.remove(ip)
            except:
                pass

            self.m_BandIP.append(ip)
            self.ShowBandIP()
        elif msgid in (1, 2, 4, 3, 5):
            idx = [
                1,
                2,
                4,
                3,
                5].index(msgid)
            if \x8een(self.m_BandIP) > idx:
                del self.m_BandIP[idx]
                self.ShowBandIP()
            
        elif msgid == 10:
            import nethero
            nethero.C2SResetBandIP(self.m_BandIP)
            self.CloseWindow()
        elif msgid in (11, 12):
            self.CloseWindow()
        elif msgid == 8:
            if self.GetObject('chk_band3').IsSelected():
                self.GetObject('chk_band4').SetSelect(False)
            
        elif msgid == 9:
            if not self.GetObject('chk_band4').IsSelected():
                self.GetObject('chk_band3').SetSelect(True)
            
        



class CSetPasswordDialog(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/bandip/setpwd.dlg')
        interface.Center(self)
        
        class CMyEdit(interface.CEdit):
            
            def MsgEnter(self):
                self.GetParent().OnMessage(1)


        self.m_edtQuestion = combmacro.CEDIT(interface.CEdit, 'edt_question', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_edtAnswer = combmacro.CEDIT(CMyEdit, 'edt_answer', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_edtQuestion.SetLimit(16)
        self.m_edtAnswer.SetLimit(16)
        self.m_edtQuestion.SetNextEdit(self.m_edtAnswer)
        self.m_edtQuestion.Active(True)
        import dlgmap
        dlgmap.DisableMinimap()

    
    def CloseWindow(self):
        self.m_edtQuestion.Active(False)
        self.m_edtAnswer.Active(False)
        self.SetShow(False)
        import dlgmap
        dlgmap.DisableMinimap(False)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            sQuestion = self.m_edtQuestion.GetText()
            sAnswer = self.m_edtAnswer.GetText()
            if \x8een(sQuestion) == 0 or \x8een(sAnswer) == 0:
                import usermacro
                usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa7\xb9\xbe\xe3')
                return None
            
            import nethero
            nethero.C2SSetBandPwd(sQuestion, sAnswer)
            self.CloseWindow()
        elif msgid in (2, 3):
            self.CloseWindow()
        



def ShowSetPwdDialog():
    global g_BandDlg
    g_BandDlg = CSetPasswordDialog()


def ShowBandIPDialog(ip, lastip, bands):
    global g_BandDlg
    g_BandDlg = CBandDialog(ip, lastip, bands)
