# pycdc 交叉复核产物 · script.fls entry 525
# co_filename(原始)='script/mxgame/pay/view/dlgpayalipay.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_525.pyc (Python 2.5)

import interface
import combdialog
import misc

class CNewAlipayPayDialog(combdialog.CCombSubWnd):
    '''
\t\t\xa4\xe4\xa5I\xc4_\xa4\xe4\xa5I\xae\xc9\xaa\xba\xa4\xe4\xa5I\xac\xc9\xad\xb1
\t\t'''
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_zf_zfb_new.dlg')

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetTaxtipsShow(self, \x8c\xbd\x86\x81\x99):
        if self.GetObject('txt_golddes1'):
            pass
        self.GetObject('txt_golddes1').SetShow(\x8c\xbd\x86\x81\x99)
        if self.GetObject('txt_golddes2'):
            pass
        self.GetObject('txt_golddes2').SetShow(\x8c\xbd\x86\x81\x99)

    
    def SetQRCode(self, sQRCode):
        pass

    
    def SetSuccess(self, bSuccess, sMsg):
        import usermacro
        if not bSuccess and sMsg:
            usermacro.PROMPT_MSG(sMsg)
        

    
    def SetCommitCB(self, oFunc):
        self.m_CommitCB = misc.Functor(oFunc)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 11:
            if self.m_CommitCB:
                self.m_CommitCB()
            
        



class CAlipayPayDialog(combdialog.CCombSubWnd):
    '''
\t\xa4\xe4\xa5I\xc4_\xa4\xe4\xa5I\xae\xc9\xaa\xba\xa4\xe4\xa5I\xac\xc9\xad\xb1
\t'''
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_zf_zfb.dlg')
        self.InitDialog()

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetQRCode(self, sQRCode):
        if sQRCode:
            self.m_QRCode = interface.CB%8mapObject(self, sQRCode)
            (x, y, w, h) = self.GetLocData('loc_qrcode')
            self.m_QRCode.SetPos(x, y)
            self.m_QRCode.SetZ(100)
        else:
            self.m_QRCode = None

    
    def SetSuccess(self, bSuccess):
        self.GetObject('txt_paid').SetShow(bSuccess)
        self.GetObject('txt_paying').SetShow(not bSuccess)

    
    def InitDialog(self):
        self.m_WaitAnimal = interface.CSpriteObject(self, 'combdialog/\xd2\xe6\xcd\xf8\xc8\xa6/loading\xb6\xaf\xbb\xad/loading.spr', interface.UIPath)
        self.m_WaitAnimal.CreateCommand(1, 'animation')
        (x, y) = self.GetObject('loc_waitani').GetPos()
        self.m_WaitAnimal.SetPos(x, y)

    
    def OnMessage(self, iMsgID):
        pass
