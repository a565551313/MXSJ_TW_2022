# pycdc 交叉复核产物 · script.fls entry 935
# co_filename(原始)='script/mxgame/activity/countrycontest/arena/view/ctrycontestwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_935.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import misc
import titletableview
import defines
import ui

class CMatchHallApplyButton(interface.CTextButton):
    
    def __init__(self, oParent, oLeftUpCB):
        interface.CTextButton.__init__(self, oParent, 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xd2\xbb\xbc\xb6\xb0\xb4\xc5\xa5/', 0, 0, '\xa5\xd3\xbd\xd0', 9191197, interface.FontLT12, 0, 54)
        self.m_LeftUpCB = oLeftUpCB

    
    def LeftUp(self):
        self.m_LeftUpCB()



class C1v1MatchHallCell(titletableview.CTitleTableCell):
    
    def __init__(self, *args):
        titletableview.CTitleTableCell.__init__(self, *args)
        self.m_oCallBack = None
        self.m_oCellPart = C1v1MatchHallItem(self)
        self.m_oCellPart.SetCallBack(self.OnCallBack)
        interface.Center(self.m_oCellPart)

    
    def OnCallBack(self, iArenaID):
        self.m_oCallBack(iArenaID)

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def SetData(self, tData):
        self.m_oCellPart.SetData(tData)

    
    def SetItemPos(self, oItem, iX, iW, iAlign):
        (iTxtW, iTxtH) = oItem.GetSize()
        (_, iCellH) = self.GetSize()
        (iXTmp, iYTmp) = interface.GetAlignXY(iTxtW, iTxtH, iW, iCellH, iAlign)
        oItem.SetPos(iX + iXTmp, iYTmp)

    
    def SetBg(self, iColor):
        self.SetAlpha(0)



class C1v1MatchHallItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/nationfight/newnationfight/zbs_1vs1matchhall_item.dlg')
        self.m_tData = ()

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def SetData(self, tData):
        self.m_tData = tData
        self.RefreshInfo()

    
    def RefreshInfo(self):
        oTextMaster = self.GetObject('text_master')
        oTextMaster.SetText(self.m_tData[0][0])
        (w, h) = oTextMaster.GetSize()
        oTextMaster.m_HotBox = ui.CHotBox(oTextMaster, w, h, 0, '\xa6u\xbe\xdd\xa6\xa8\xa5\\\xa1G%d\xa6\xb8' % self.m_tData[0][1])
        oTextClass = self.GetObject('text_class')
        oTextClass.SetText(self.m_tData[1])
        if self.m_tData[2]:
            self.GetObject('btn_lock').SetShow(True)
            self.GetObject('btn_unlock').SetShow(False)
        else:
            self.GetObject('btn_lock').SetShow(False)
            self.GetObject('btn_unlock').SetShow(True)
        self.GetObject('text_playernum').SetText(self.m_tData[3])
        (bHasClick, iArenaID) = self.m_tData[4]
        oTextBtn = self.GetObject('btn_apply')
        if bHasClick:
            oTextBtn.Enable(False)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.m_oCallBack(self.m_tData[4][1])
        

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)

    
    def LeftUp(self):
        self.GetParent().LeftUp()

    
    def LeftDown(self):
        self.GetParent().LeftDown()



class C3v3MatchHallCell(titletableview.CTitleTableCell):
    
    def __init__(self, *args):
        titletableview.CTitleTableCell.__init__(self, *args)
        self.m_oCallBack = None
        self.m_oCellPart = C3v3MatchHallItem(self)
        self.m_oCellPart.SetCallBack(self.OnCallBack)
        self.m_oCellPart.SetEnterCB(self.OnEnterCB)
        self.m_oCellPart.SetLeaveCB(self.OnLeaveCB)
        interface.Center(self.m_oCellPart)

    
    def OnEnterCB(self, tData):
        self.m_oEnterCB(tData, self)

    
    def OnLeaveCB(self):
        self.m_oLeaveCB()

    
    def SetEnterLeaveCB(self, oEnterCB, oLeaveCB):
        self.m_oEnterCB = misc.Functor(oEnterCB)
        self.m_oLeaveCB = misc.Functor(oLeaveCB)

    
    def OnCallBack(self, iArenaID):
        self.m_oCallBack(iArenaID)

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def SetData(self, tData):
        self.m_oCellPart.SetData(tData)

    
    def SetItemPos(self, oItem, iX, iW, iAlign):
        (iTxtW, iTxtH) = oItem.GetSize()
        (_, iCellH) = self.GetSize()
        (iXTmp, iYTmp) = interface.GetAlignXY(iTxtW, iTxtH, iW, iCellH, iAlign)
        oItem.SetPos(iX + iXTmp, iYTmp)

    
    def SetBg(self, iColor):
        self.SetAlpha(0)



class C3v3MatchHallItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/nationfight/newnationfight/zbs_3vs3matchhall1_item.dlg')
        self.m_tData = ()

    
    def SetCallBack(self, oCallBack):
        self.m_oCallBack = misc.Functor(oCallBack)

    
    def SetEnterCB(self, oCallBack):
        self.m_oEnterCB = misc.Functor(oCallBack)

    
    def SetLeaveCB(self, oCallBack):
        self.m_oLeaveCB = misc.Functor(oCallBack)

    
    def SetData(self, tData):
        self.m_tData = tData
        self.RefreshInfo()

    
    def RefreshInfo(self):
        oTextMaster = self.GetObject('text_master')
        oTextMaster.SetText(self.m_tData[1][0])
        self.GetObject('text_zhiye').SetText(defines.CAREER_ID2NAME[self.m_tData[4]])
        self.GetObject('text_playernum').SetText(str(self.m_tData[2]))

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.m_oCallBack(self.m_tData[3])
        

    
    def Enter(self):
        self.m_oEnterCB(self.m_tData[1][1])

    
    def Leave(self):
        self.m_oLeaveCB()

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.GetParent().MouseWheelUp, p)

    
    def LeftUp(self):
        self.GetParent().LeftUp()

    
    def LeftDown(self):
        self.GetParent().LeftDown()



class CMatchHallPasswordDialog(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, oFunc):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/nationfight/newnationfight/3vs3roompassword.dlg')
        interface.Center(self)
        self.m_IsIgnoreEsc = True
        self.m_oCBFunc = oFunc
        self.m_PasswordEdit = combmacro.CEDIT(ui.CNumberEdit, 'lineup', self, interface.COLOR_3, interface.FontLT14_3)
        self.m_PasswordEdit.Active(True)
        self.m_PasswordEdit.SetLimit(4)

    
    def CloseWindow(self):
        self.GetParent().ClosePasswordDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 8:
            sText = self.m_PasswordEdit.GetText()
            self.m_oCBFunc(sText)
