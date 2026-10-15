# pycdc 交叉复核产物 · script.fls entry 2588
# co_filename(原始)='script/mxgame/group/dlggroupsetprice.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2588.pyc (Python 2.5)

import combdialog
import interface
import types
import misc
g_SetPriceDlg = None

def ShowSetPiceDlg(sTips, oSetPriceCB, iPrice = None):
    global g_SetPriceDlg
    g_SetPriceDlg = CSetPrice(sTips, oSetPriceCB, iPrice)


class CSetPrice(combdialog.CCombDialog):
    
    def __init__(self, sTips, oSetPriceCB, iPrice = None):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group/newgroup/setprice.dlg')
        self.Capture(1, 0)
        interface.Center(self)
        if isinstance(oSetPriceCB, types.MethodType):
            oCB = misc.Functor(oSetPriceCB)
        else:
            oCB = oSetPriceCB
        self.m_oSetPriceCB = oCB
        for None in iPrice:
            None.m_iPrice = None
            self.m_oPriceEidt = None
            self.SetTips(sTips)
            self.AfterOpenDialog()
            return None

    
    def InitEdit(self):
        import combmacro
        import wrapinterface
        self.m_oPriceEidt = combmacro.CEDIT(wrapinterface.CNumberEdit, 'loc_edt', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        if self.m_iPrice:
            self.m_oPriceEidt.SetText(str(self.m_iPrice))
            self.m_oPriceEidt.SetSelect(0, len(str(self.m_iPrice)))
        
        self.m_oPriceEidt.SetLimit(5)
        self.m_oPriceEidt.Active(True)

    
    def SetTips(self, sTips):
        self.GetObject('rtxt_tips').SetText(sTips)

    
    def SetPrice(self):
        iPrice = self.m_oPriceEidt.GetNumber()
        if self.m_oSetPriceCB and callable(self.m_oSetPriceCB):
            self.m_oSetPriceCB(iPrice)
        
        self.m_oPriceEidt.Active(False)
        self.CloseWindow()

    
    def CloseWindow(self):
        global g_SetPriceDlg
        g_SetPriceDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.SetPrice()
