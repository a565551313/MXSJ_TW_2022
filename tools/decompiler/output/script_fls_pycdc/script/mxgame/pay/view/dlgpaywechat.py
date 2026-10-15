# pycdc 交叉复核产物 · script.fls entry 2247
# co_filename(原始)='script/mxgame/pay/view/dlgpaywechat.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2247.pyc (Python 2.5)

import interface
import combdialog
import paydefines

class CWechatPayDialog(combdialog.CCombSubWnd):
    '''
\t\xb7L\xabH\xa4\xe4\xa5I\xae\xc9\xaa\xba\xa4\xe4\xa5I\xac\xc9\xad\xb1
\t'''
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/pay/pay_zf_wx.dlg')
        self.InitDialog()

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetPayMoney(self, iNum):
        iNum = self.GetObject
        None(None).ReplaceText({
            '$total': str(iNum * 1) })

    
    def SetTaxtipsShow(self, bShow):
        if self.GetObject('txt_golddes1'):
            pass
        self.GetObject('txt_golddes1').SetShow(bShow)
        if self.GetObject('txt_golddes2'):
            pass
        self.GetObject('txt_golddes2').SetShow(bShow)

    
    def SetQRCode(self, sQRCode):
        import mdpay
        if sQRCode:
            if mdpay.IsNewQRCode():
                self.m_QRCode = interface.CQRCodeObject(self, sQRCode, paydefines.QRCODE_SIZE)
                (x, y, w, h) = self.GetLocData('loc_qrcode')
                self.m_QRCode.SetPos(x, y)
                self.m_QRCode.SetZ(100)
            else:
                self.m_QRCode = interface.CBitmapObject(self, sQRCode)
                (x, y, w, h) = self.GetLocData('loc_qrcode')
                self.m_QRCode.SetPos(x, y)
                self.m_QRCode.SetZ(100)
        else:
            self.m_QRCode = None

    
    def SetSuccess(self, bSuccess, sMsg):
        import usermacro
        self.GetObject('txt_fail').SetShow(False)
        self.GetObject('hloc_fail').SetShow(False)
        if bSuccess:
            self.m_WaitAnimal.SetShow(False)
            self.m_QRCode = None
        elif sMsg:
            self.GetObject('txt_fail').SetShow(True)
            self.GetObject('hloc_fail').SetShow(True)
            usermacro.PROMPT_MSG(sMsg)
            self.m_WaitAnimal.SetShow(False)
        else:
            self.m_WaitAnimal.SetShow(True)
        self.GetObject('img_success').SetShow(bSuccess)
        self.GetObject('txt_success').SetShow(bSuccess)

    
    def InitDialog(self):
        self.m_WaitAnimal = interface.CSpriteObject(self, 'combdialog/\xd2\xe6\xcd\xf8\xc8\xa6/loading\xb6\xaf\xbb\xad/loading.spr', interface.UIPath)
        self.m_WaitAnimal.CreateCommand(1, 'animation')
        (x, y) = self.GetObject('loc_waitani').GetPos()
        self.m_WaitAnimal.SetPos(x, y)

    
    def OnMessage(self, iMsgID):
        self.GetParent().ssEmit(self.GetParent().SS_ClickAlipayCommit)
