# pycdc 交叉复核产物 · script.fls entry 1529
# co_filename(原始)='script/mxgame/activity/timewheel/view/dlgtimewheelmain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1529.pyc (Python 2.5)

import combdialog
import slot
import pagedlgbase
import delegatetimewheelmain
import timewheelinterface
import permission

class CTimeWheelMainDlg(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.CPageDlgBase):
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/shiguangzhilun/main_new.dlg')
        pagedlgbase.CPageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = []
        self.GetObject('btn_zhuihui').m_ParentNotify = True
        self.InitDelegate()
        self.InitDlg()

    
    def InitDlg(self):
        continue
        if 'img_discount':
            self.GetObject('img_discount').SetZ(1000)
        

    
    def InitDelegate(self):
        sList = [
            'btn_speed',
            'btn_delegate',
            'btn_weekcard',
            'btn_zhuihui',
            'btn_preferential']
        self.m_DelegateList = [
            delegatetimewheelmain.CTimeWheelMainDgt(self, sList)]

    
    def ShowDelegateRedPoint(self, bRed):
        self.GetObject('btn_delegate').SetRedDot(bRed)

    
    def OnButtonEnter(self, oObj):
        import wrapinterface
        import interface
        if self.GetObject('btn_zhuihui') == oObj:
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, oObj.m_TipsStr, interface.FontLT14_3, direct = oObj.m_TipsDirect - 1)
            self.m_TipsObj.SetOwner(oObj)
        

    
    def OnButtonLeave(self, oObj):
        if self.GetObject('btn_zhuihui') == oObj:
            self.m_TipsObj = None
        

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.CloseWindow()

    
    def CloseWindow(self):
        timewheelinterface.CloseTimeWheelDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID in (2, 3, 4, 5, 6):
            self.ssEmit(self.SS_ClickBtn, iMsgID)
            self.m_TipsObj = None
