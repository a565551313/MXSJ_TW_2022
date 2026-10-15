# pycdc 交叉复核产物 · script.fls entry 635
# co_filename(原始)='script/dialog/dlgitembillminibuy2.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_635.pyc (Python 2.5)

import interface
import combdialog
import hero
import misc
import wrapinterface
import combmacro
import ui
import usermacro
import action
import itemdata
MIN_AMOUNT = 1
MAX_AMOUNT = 200
MODE_BUY_AND_USE = 1
MODE_JUST_BUY = 2
SPECIAL_ITEM_NOTCLOSE = (25707,)
g_oMiniBuy2Dialog = None
g_tDialogLastPos = None
g_dShowAmountInJustBuyMode = { }

def ModuleReset():
    global g_oMiniBuy2Dialog, g_tDialogLastPos
    g_oMiniBuy2Dialog = None
    g_tDialogLastPos = None


def ModuleRestart():
    global g_dShowAmountInJustBuyMode
    g_dShowAmountInJustBuyMode = { }


def OpenDialog(iItemId, iAmount, iPrice, iMode, iMaxNum = 200, sExtraTips = ''):
    global g_oMiniBuy2Dialog
    if iMode not in (MODE_BUY_AND_USE, MODE_JUST_BUY):
        return None
    
    import dlgsummontalentresult
    oParent = interface.DialogPanel
    if dlgsummontalentresult.g_oResultDlg:
        oParent = dlgsummontalentresult.g_oResultDlg
    
    g_oMiniBuy2Dialog = CMiniBuy2Dialog(oParent, iItemId, iAmount, iPrice, iMode, iMaxNum)
    g_oMiniBuy2Dialog.SetExtraTips(sExtraTips)


def CloseDlg():
    global g_oMiniBuy2Dialog
    g_oMiniBuy2Dialog = None


class CMiniBuy2Dialog(combdialog.CCombDialog):
    
    def __init__(self, oParent, iShape, iAmount, iPrice, iMode, iMaxNum):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/itembill/itembill_new/itembill_minibuy2.dlg')
        if iMode == MODE_JUST_BUY:
            iAmount = g_dShowAmountInJustBuyMode.get(iShape, iAmount)
            iAmount = min(iAmount, iMaxNum)
        
        tData = itemdata.GetData(iShape)
        sName = None if not tData else tData[0]
        sTxt = '\xa8\xad\xa4W%s\xa4\xa3\xa8\xac\xa1A\xa5i\xa5H\xa7\xd6\xb1\xb6\xc1\xca\xb6R' % sName
        if iMode == MODE_JUST_BUY:
            sTxt = '\xa5i\xa5H\xa7\xd6\xb1\xb6\xc1\xca\xb6R%s' % sName
        
        self.GetObject('text_tips').SetText(sTxt)
        if not None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None):
            iMaxNum = MAX_AMOUNT
        
        self.m_iMaxNum = iMaxNum
        self.m_oEdit = combmacro.CEDIT(ui.CNumberEdit, 'txt_num', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oEdit.SetMaxNum(iMaxNum)
        self.m_iShape = iShape
        self.m_iPrice = iPrice
        self.m_iAmount = iAmount
        self.m_iMode = iMode
        self.m_oLongClickAction = None
        self.m_sExtraTips = ''
        self.m_oTips = None
        self.RefreshItemCheckBox()
        hero.AddPropCallBack('CMiniBuy2Dialog_gold', 'm_Gold', misc.Functor(self.OnGoldChanged))
        self.m_oEdit.SetCharChangeCB(misc.Functor(self.OnAmountNumberChange))
        self.RefreshAmountText(iAmount, True)
        if g_tDialogLastPos:
            self.SetPos(g_tDialogLastPos[0], g_tDialogLastPos[1])
        else:
            interface.Center(self)
        self.m_oEdit.Active(True)
        self.m_oEdit.SetSelect(0, 999)
        self.GetObject('btn_minus').SetButtonType(1)
        self.GetObject('btn_plus').SetButtonType(1)
        self.RefreshMode()

    
    def SetExtraTips(self, sTips):
        self.m_sExtraTips = sTips

    
    def RefreshMode(self):
        if self.m_iMode == MODE_BUY_AND_USE:
            self.GetObject('btn_buy').SetText('\xc1\xca\xb6R\xa8\xc3\xa8\xcf\xa5\xce')
        elif self.m_iMode == MODE_JUST_BUY:
            self.GetObject('btn_buy').SetText('\xc1\xca  \xb6R')
        

    
    def RefreshItemCheckBox(self):
        import itemdata
        (name, explain) = itemdata.GetData(self.m_iShape)
        oBoxItem = self.GetObject('box_item')
        (iX, iY) = oBoxItem.GetPos()
        (iW, iH) = oBoxItem.GetSize()
        self.m_oItemCheckBox = wrapinterface.CItemCheckBox1(self, self.m_iShape, 1, name + '#r\xa5@\xac\xc9\xb0^\xc4m\xab\xd7: ' + str(self.m_iPrice), None, interface.COLOR_1, interface.FontLT14_3, iX, iY, msgid = 1000, bg = oBoxItem.m_FileName, width = iW, height = iH)

    
    def RefreshAmountText(self, iAmount, bSetNumberText):
        self.m_iAmount = self.GetVaildNumber(iAmount)
        if bSetNumberText:
            self.m_oEdit.SetText(str(iAmount))
        
        self.GetObject('txt_price').SetText(str(self.m_iAmount * self.m_iPrice))

    
    def GetVaildNumber(self, iAmount):
        if iAmount < MIN_AMOUNT:
            return MIN_AMOUNT
        
        if iAmount > self.m_iMaxNum:
            return self.m_iMaxNum
        
        return iAmount

    
    def CloseWindow(self):
        global g_tDialogLastPos, g_oMiniBuy2Dialog
        g_tDialogLastPos = self.GetPos()
        g_oMiniBuy2Dialog = None

    
    def OnAmountNumberChange(self):
        self.m_iAmount = self.m_oEdit.GetNumber()
        iVaild = self.GetVaildNumber(self.m_iAmount)
        if iVaild != self.m_iAmount:
            self.m_oEdit.SetText(str(iVaild))
            return None
        
        self.RefreshAmountText(iVaild, False)

    
    def OnGoldChanged(self):
        iGold = hero.GetProp('m_Gold')
        self.GetObject('txt_sg').SetText(str(iGold))

    
    def BnLeave(self, iMsgId):
        self.StopAutoAdd()

    
    def BnLeftUp(self, iMsgId):
        self.StopAutoAdd()

    
    def BnLeftDown(self, iMsgId):
        if self.m_oLongClickAction:
            if self.m_oLongClickAction.GetMsgId() == iMsgId:
                return None
            else:
                self.StopAutoAdd()
        
        self.m_oLongClickAction = action.CLongClickAction(iMsgId)
        action.AddAction(self, self.m_oLongClickAction)

    
    def StopAutoAdd(self):
        if self.m_oLongClickAction:
            self.m_oLongClickAction.Stop()
            self.m_oLongClickAction = None
        

    
    def OnLongClickAction(self, iMsgId):
        if iMsgId == 3:
            if self.m_iAmount > MIN_AMOUNT:
                self.RefreshAmountText(self.m_iAmount - 1, True)
            
        elif iMsgId == 4:
            if self.m_iAmount < self.m_iMaxNum:
                self.RefreshAmountText(self.m_iAmount + 1, True)
            
        

    
    def OnItemEnter(self, oItem):
        import dlggetinfo
        self.m_oTips = dlggetinfo.NewItemInfo(-1, self.m_iShape, self.m_sExtraTips, None)
        self.m_oTips.Topmost()

    
    def OnItemLeave(self, oItem):
        self.m_oTips = None

    
    def OnMessage(self, iMsgID):
        import netopenui
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            if self.m_iAmount <= 0:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xc1\xca\xb6R\xbc\xc6\xb6q')
            elif self.m_iMode == MODE_BUY_AND_USE:
                netopenui.C2SQuickBuyHTDan(1, self.m_iShape, self.m_iAmount)
                if self.m_iShape == 25707:
                    self.CloseWindow()
                
            elif self.m_iMode == MODE_JUST_BUY:
                g_dShowAmountInJustBuyMode[self.m_iShape] = self.m_iAmount
                netopenui.C2SQuickBuyHTDan(3, self.m_iShape, self.m_iAmount)
            
            if self.m_iShape not in SPECIAL_ITEM_NOTCLOSE:
                self.CloseWindow()
            
        elif iMsgID == 3:
            if self.m_iAmount > MIN_AMOUNT:
                self.RefreshAmountText(self.m_iAmount - 1, True)
            
        elif iMsgID == 4:
            if self.m_iAmount < self.m_iMaxNum:
                self.RefreshAmountText(self.m_iAmount + 1, True)
            
        elif iMsgID == 5:
            if self.m_iAmount <= 0:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xc1\xca\xb6R\xbc\xc6\xb6q')
            else:
                netopenui.C2SQuickBuyHTDan(2, self.m_iShape, self.m_iAmount)
                self.CloseWindow()
        elif iMsgID == interface.RIGHT_BUTTON_MESSAGE + 3:
            self.RefreshAmountText(MIN_AMOUNT, True)
        elif iMsgID == interface.RIGHT_BUTTON_MESSAGE + 4:
            self.RefreshAmountText(self.m_iMaxNum, True)
