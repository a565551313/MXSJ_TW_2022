# pycdc 交叉复核产物 · script.fls entry 4324
# co_filename(原始)='script/dialog/dlgbank.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4324.pyc (Python 2.5)

'''
#===============================================
# 2015.1.15\xc8\xd5\xce\xac\xbb\xa4\xba\xf3\xa3\xac\xc8\xa1\xcf\xfb\xc7\xae\xd7\xaf\xb5\xc4\xb4\xe6\xc8\xeb\xb9\xa6\xc4\xdc
# 2015.1.22\xc8\xd5\xce\xac\xbb\xa4\xba\xf3\xa3\xac\xcd\xea\xc8\xab\xc8\xa1\xcf\xfb\xc7\xae\xd7\xaf\xb4\xe6\xc8\xa1\xc7\xae\xb9\xa6\xc4\xdc
'''
import combdialog
import combmacro
import interface
import ui
import wrapinterface
g_SliderMutle = False
g_ChangeMode = True
g_DlgBank = None
g_SetwardBankDlg = None
g_DlgCashFlow = None

def ModuleReset():
    global g_SliderMutle, g_ChangeMode, g_DlgBank, g_SetwardBankDlg, g_DlgCashFlow
    g_SliderMutle = False
    g_ChangeMode = True
    g_DlgBank = None
    g_SetwardBankDlg = None
    g_DlgCashFlow = None


def CreateMutle():
    global g_SliderMutle
    g_SliderMutle = True


def ReleaseMutle():
    global g_SliderMutle
    g_SliderMutle = False


def GetMutle():
    return g_SliderMutle


class CHSlider(interface.CHSlider):
    
    class CBar(interface.CBoxObject, interface.CHoldObject):
        
        def __init__(self, parent, n_max, fname, path):
            (w, h) = parent.GetSize()
            barw = 6
            barh = h + 10
            interface.CBoxObject.__init__(self, parent, barw, barh, 4489440, 0)
            self.m_Image = ui.CImage(self, fname, path)
            (barw, barh) = self.m_Image.GetSize()
            self.SetSize(barw, barh)
            self.m_nMax = n_max
            self.m_MoveArea = w - barw
            self.m_CurPos = 0
            self.SetPos(0, -(barh - h) / 2)
            self.MessageProcess()

        
        def Hold(self):
            import cursor
            (mx, my) = cursor.GetPos()
            (_, objy) = self.GetPos()
            x = mx - interface.HoldX
            if x < 0:
                x = 0
            elif x > self.m_MoveArea:
                x = self.m_MoveArea
            
            pos = self.m_nMax * x / self.m_MoveArea
            if pos != self.m_CurPos:
                self.m_CurPos = x * self.m_nMax / self.m_MoveArea
                self.GetParent().PosChange(pos)
            
            self.SetPos(x, objy)
            self.CreateTips()

        
        def SetBarPos(self, pos):
            if pos < 0:
                pos = 0
            elif pos > self.m_nMax:
                pos = self.m_nMax
            
            x = pos * self.m_MoveArea / self.m_nMax
            (_, objy) = self.GetPos()
            self.SetPos(x, objy)
            if pos == self.m_CurPos:
                return None
            
            self.m_CurPos = pos
            self.GetParent().PosChange(pos)
            self.CreateTips()

        
        def LeftDown(self):
            self.Capture(1, 1)
            interface.CHoldObject.LeftDown(self)
            CreateMutle()

        
        def LeftUp(self):
            self.Capture(0)
            interface.CHoldObject.LeftUp(self)
            
            try:
                par = self.GetParent().GetParent()
                if hasattr(par, 'OnSliderLeftUp'):
                    par.OnSliderLeftUp(self.m_CurPos)
                    ReleaseMutle()
            except:
                ReleaseMutle()
                return None


        
        def CreateTips(self):
            (x, y) = self.GetPos()
            (_, h) = self.GetSize()
            self.m_TextObj = interface.CRichTextObject(self, 100, interface.FontLT12_1, '%d%%' % self.m_CurPos, interface.COLOR_56)
            self.m_TextObj.SetPos(int(x - self.m_CurPos * 1.1), (y - h) + 8)


    
    def LeftUp(self):
        import cursor
        (sx, _) = self.GetScreenPos()
        (mx, _) = cursor.GetPos()
        p = (mx - sx) * self.m_nMax / self.m_Bar.m_MoveArea
        self.SetBarPos(p)
        self.m_Bar.LeftUp()



class CNumberEdit(wrapinterface.CNumberEdit):
    
    def SetMaxNum(self, maxnum):
        self.m_MaxNum = maxnum

    
    def AddChar(self, char):
        wrapinterface.CNumberEdit.AddChar(self, char)
        self.OnChange()

    
    def DeleteChar(self):
        wrapinterface.CNumberEdit.DeleteChar(self)
        self.OnChange()

    
    def OnChange(self):
        
        try:
            cash = int(self.GetText())
        except ValueError:
            cash = 0

        import usermacro
        if cash > self.m_MaxNum:
            usermacro.PROMPT_MSG('\xb1z\xbf\xe9\xa4J\xaa\xba\xbc\xc6\xa6r\xb9F\xa8\xec\xaa\xf7\xbf\xfa\xa4W\xad\xad')
            self.SetText(str(self.m_MaxNum))
        
        if not GetMutle():
            if hasattr(self.GetParent(), 'OnChange'):
                self.GetParent().OnChange()
            
        



class CBankBase(combdialog.CCombDialog):
    
    def __init__(self, parent = -1):
        if parent == -1:
            parent = interface.DialogPanel
        
        combdialog.CCombDialog.__init__(self, parent, 'dialog/bank.dlg')
        interface.Center(self)
        self.m_CanSaveCash = 2000000
        self.InitDialog()

    
    def InitDialog(self):
        self.InitParentNontify()
        self.CreateInputCtrls()
        self.CreateCashInfo()
        self.CreateSavingInfo()
        self.SetMaxLimit()

    
    def InitParentNontify(self):
        for btnName in ('btn_increase', 'btn_decrease'):
            self.GetObject(btnName).m_ParentNotify = True
        

    
    def CreateInputCtrls(self):
        self.m_InputEdit = combmacro.CEDIT(CNumberEdit, 'input_Edit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_InputEdit.m_IsMoney = True
        self.m_InputEdit.SetLimit(11)
        self.m_InputEdit.Active(True)

    
    def CreateCashInfo(self):
        import hero
        propitem = hero.g_Name2PropItem['m_Cash']
        propitem.AddRefreshCallbackWithID('CBank', self.RefreshCashText)

    
    def CreateSavingInfo(self):
        pass

    
    def RefreshCashText(self):
        import hero
        import misc
        cash = hero.g_Prop.m_Cash
        self.m_Cash = cash
        color = misc.GetCashColor(cash, False)
        cash = misc.ChangeMoney(str(cash))
        self.m_CashTxt = combmacro.CTEXT(interface.CTextObject, 'txt_Cash', self, cash, interface.FontLT14_3, color)
        self.SetMaxLimit()

    
    def RefreshSaveText(self):
        pass

    
    def ReleaseCallBacks(self):
        import hero
        propitem = hero.g_Name2PropItem['m_Cash']
        propitem.RemoveRefreshCallbackWithID('CBank')

    
    def GetInputMoney(self, msgtxt):
        import usermacro
        
        try:
            cash = int(self.m_InputEdit.GetText())
        except ValueError:
            usermacro.PROMPT_MSG(msgtxt)
            return None

        if cash <= 0:
            self.CloseWindow()
            return None
        
        return cash

    
    def SetMaxLimit(self):
        maxCash = self.m_Cash
        DepositLimit = self.m_CanSaveCash - self.m_SaveMoney
        if hasattr(self, 'm_SaveMoney'):
            maxCash = max(self.m_SaveMoney, min(self.m_Cash, DepositLimit))
        
        self.m_InputEdit.SetMaxNum(maxCash)

    
    def CloseWindow(self):
        pass

    
    def OnIncreaseMoney(self):
        curInputMoney = self.m_InputEdit.GetText()
        
        try:
            iMoney = int(curInputMoney)
        except:
            iMoney = 0

        iMoney += 1000000
        self.m_InputEdit.SetText('%d' % iMoney)

    
    def OnDecreaseMoney(self):
        curInputMoney = self.m_InputEdit.GetText()
        
        try:
            iMoney = int(curInputMoney)
        except:
            iMoney = 0

        iMoney -= 1000000
        if iMoney < 0:
            iMoney = 0
        
        self.m_InputEdit.SetText('%d' % iMoney)

    
    def OnSaveMoney(self):
        import netnpc
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa6s\xa4J\xaa\xf7\xc3B')
        if cash:
            if cash > self.m_Cash:
                cash = self.m_Cash
            
            netnpc.C2SNpcInput(None, '%d|%d' % (1, cash))
            self.CloseWindow()
        

    
    def OnDrawMoney(self):
        import netnpc
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa8\xfa\xa5X\xaa\xf7\xc3B')
        if cash:
            if cash > self.m_SaveMoney:
                cash = self.m_SaveMoney
            
            netnpc.C2SNpcInput(None, '%d|%d' % (2, cash))
            self.CloseWindow()
        

    
    def OnButtonEnter(self, btn):
        wrapinterface[2] = '\xc2I\xc0\xbb1\xa6\xb8\xb4\xee\xa4\xd6100\xb8U\xa1A\xa4\xa3\xa8\xac\xabh\xb4\xee\xa4\xd6\xac\xb00'
        wrapinterface[3] = '\xc2I\xc0\xbb1\xa6\xb8\xbcW\xa5[100\xb8U\xa1A\xa4\xa3\xa8\xac\xabh\xa5\xfe\xb3\xa1\xbcW\xa5['
        wrapinterface[8] = '\xc2I\xc0\xbb\xb4\xee\xa4\xd61%'
        wrapinterface[9] = '\xc2I\xc0\xbb\xbcW\xa5[1%'
        tipsTxt = wrapinterface
        self.m_Tips = wrapinterface.CTextTips(self, -1, tipsTxt[btn.m_MsgID], interface.FontLT14_3, direct = 1)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.OnDecreaseMoney()
        elif msgid == 3:
            self.OnIncreaseMoney()
        elif msgid == 4:
            self.OnSaveMoney()
        elif msgid == 5:
            self.OnDrawMoney()
        



def ShowBankDlg():
    global g_DlgBank
    if not g_DlgBank:
        g_DlgBank = CBankDlg()
    


class CBankDlg(CBankBase):
    
    def CreateSavingInfo(self):
        import hero
        propitem = hero.g_Name2PropItem['m_Saving']
        propitem.AddRefreshCallbackWithID('CBank', self.RefreshSaveText)

    
    def RefreshSaveText(self):
        import hero
        import misc
        save = hero.g_Prop.m_Saving
        self.m_SaveMoney = save
        color = misc.GetCashColor(save, False)
        save = misc.ChangeMoney(str(save))
        self.m_SaveTxt = combmacro.CTEXT(interface.CTextObject, 'txt_Save', self, save, interface.FontLT14_3, color)
        self.SetMaxLimit()
        if g_ChangeMode:
            self.ChangeMode()
        

    
    def SetMaxLimit(self):
        self.m_InputEdit.SetMaxNum(self.m_SaveMoney)

    
    def ChangeMode(self):
        self.GetObject('btn_Saving').SetShow(False)
        (x, y) = self.GetObject('btn_DrawMoney').GetPos()
        self.GetObject('btn_DrawMoney').SetPos(x - 40, y)

    
    def ReleaseCallBacks(self):
        import hero
        propitem = hero.g_Name2PropItem['m_Saving']
        propitem.RemoveRefreshCallbackWithID('CBank')
        CBankBase.ReleaseCallBacks(self)

    
    def CloseWindow(self):
        global g_DlgBank
        self.ReleaseCallBacks()
        g_DlgBank = None



def ShowStewardBankDlg(icash):
    global g_SetwardBankDlg
    if not g_SetwardBankDlg:
        g_SetwardBankDlg = CStewardBankDlg(icash)
    


class CStewardBankDlg(CBankBase):
    
    def __init__(self, imoney):
        self.m_SaveMoney = imoney
        CBankBase.__init__(self)

    
    def CreateSavingInfo(self):
        import misc
        color = misc.GetCashColor(self.m_SaveMoney, False)
        self.m_txtCash = combmacro.CTEXT(interface.CTextObject, 'txt_Save', self, misc.ChangeMoney(str(self.m_SaveMoney)), interface.FontLT14_3, color)

    
    def CloseWindow(self):
        global g_SetwardBankDlg
        self.ReleaseCallBacks()
        g_SetwardBankDlg = None



class CShopBankDlg(CBankBase):
    
    def __init__(self, parent, imoney):
        self.m_SaveMoney = imoney
        CBankBase.__init__(self, parent)

    
    def CreateSavingInfo(self):
        import misc
        color = misc.GetCashColor(self.m_SaveMoney, False)
        self.m_txtCash = combmacro.CTEXT(interface.CTextObject, 'txt_Save', self, misc.ChangeMoney(str(self.m_SaveMoney)), interface.FontLT14_3, color)

    
    def OnSaveMoney(self):
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa6s\xa4J\xaa\xf7\xc3B')
        if cash and cash > self.m_Cash:
            cash = max(0, self.m_Cash)
        
        if cash:
            self.GetParent().OnSaving(cash)
            self.CloseWindow()
        

    
    def OnDrawMoney(self):
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa6s\xa4J\xaa\xf7\xc3B')
        if cash and cash > self.m_SaveMoney:
            cash = max(0, self.m_SaveMoney)
        
        if cash:
            self.GetParent().OnDraw(cash)
            self.CloseWindow()
        

    
    def CloseWindow(self):
        self.ReleaseCallBacks()
        self.m_InputEdit.Active(False)
        self.GetParent().m_SubDlg = None
        self.Capture(0)



class CFactoryBankDlg(CBankBase):
    
    def __init__(self, parent, imoney):
        if imoney > 100000:
            self.m_SaveMoney = imoney - 100000
        else:
            self.m_SaveMoney = 0
        CBankBase.__init__(self, parent)

    
    def CreateSavingInfo(self):
        import misc
        color = misc.GetCashColor(self.m_SaveMoney, False)
        self.m_txtCash = combmacro.CTEXT(interface.CTextObject, 'txt_Save', self, misc.ChangeMoney(str(self.m_SaveMoney)), interface.FontLT14_3, color)

    
    def OnSaveMoney(self):
        import netliving
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa6s\xa4J\xaa\xf7\xc3B')
        if cash:
            if cash > self.m_Cash:
                cash = self.m_Cash
            
            netliving.C2SPutInCash(cash)
            self.CloseWindow()
        

    
    def OnDrawMoney(self):
        import netliving
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa6s\xa4J\xaa\xf7\xc3B')
        if cash:
            if cash > self.m_SaveMoney:
                cash = self.m_SaveMoney
            
            netliving.C2STakeOutCash(cash)
            self.CloseWindow()
        

    
    def CloseWindow(self):
        self.ReleaseCallBacks()
        self.m_InputEdit.Active(False)
        self.GetParent().m_ManageDlg = None
        self.Capture(0)



def ShowCashFlowDlg(imode = 0, icash = 0, exmsg = '', responsID = -1):
    global g_DlgCashFlow
    if g_DlgCashFlow:
        g_DlgCashFlow.CloseWindow()
    
    g_DlgCashFlow = CCashFlowDlg(imode, icash, exmsg)
    g_DlgCashFlow.SetResponID(responsID)


class CCashFlowDlg(combdialog.CCombDialog):
    
    def __init__(self, imode, icash, exmsg):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/cashflow.dlg')
        interface.Center(self)
        self.InitDialog(imode, icash, exmsg)
        self.Capture(1, 0)

    
    def InitDialog(self, imode, icash, exmsg):
        self.InitParentNontify()
        self.CreateInputCtrls()
        self.RefreshCurCash(icash, imode)
        self.CreateDesc(imode, exmsg)
        self.HideCtrls(imode)

    
    def SetResponID(self, responid):
        self.m_ResponID = responid

    
    def InitParentNontify(self):
        for btnName in ('btn_increase', 'btn_decrease', 'btn_add', 'btn_minus'):
            self.GetObject(btnName).m_ParentNotify = True
        

    
    def CreateInputCtrls(self):
        self.m_InputEdit = combmacro.CEDIT(CNumberEdit, 'input_Edit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_InputEdit.m_IsMoney = True
        self.m_InputEdit.SetLimit(11)
        self.m_InputEdit.Active(True)
        self.m_MoneySlider = combmacro.CHSLIDER(CHSlider, 'slider', self, 100)

    
    def CreateDesc(self, imode, exmsg):
        self.m_IMode = imode
        if imode == 0:
            desc = exmsg
        else:
            desc = self.GetDesc(imode, exmsg)
        if desc:
            if interface.IsNewStyle():
                desc = interface.ReplaceYellow(desc)
                desc = desc.replace('#cFFFFFF', '#c84473B')
            
            descObj = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_desc', self, desc, interface.FontLT14_3, interface.COLOR_4)
            (_, Height) = descObj.GetSize()
            (x, y, w, h) = self.GetLocData('txt_desc')
            if Height > h:
                descObj = interface.CScrollRichText(self, x + 5, y + 5, w - 12, h - 10)
                descObj.AddTxt(desc, interface.FontLT14_3, interface.COLOR_4)
                descObj.ResetScrollBar(False)
            
            self.m_Desc = descObj
        else:
            descObj = None
            self.m_Desc = descObj

    
    def RefreshCurCash(self, icash, imode):
        self.m_Cash = icash
        self.m_CanUseCash = icash
        if imode == 2:
            if icash < 1000000:
                self.m_CanUseCash = 0
            else:
                self.m_CanUseCash = icash - 1000000
        
        self.m_InputEdit.SetMaxNum(self.m_CanUseCash)

    
    def HideCtrls(self, imode):
        if imode == 0:
            for ctrlname in ('percent0', 'percent100', 'slider', 'btn_increase', 'btn_decrease', 'btn_add', 'btn_minus'):
                self.GetObject(ctrlname).SetShow(False)
            
            self.m_MoneySlider.m_Bar.SetShow(False)
            (_, y) = self.GetObject('percent0').GetPos()
            (x, _) = self.GetObject('txt_inputcash').GetPos()
            self.GetObject('txt_inputcash').SetPos(x, y)
            (w, _) = self.GetObject('btn_decrease').GetSize()
            (ix, iy) = self.m_InputEdit.GetPos()
            self.m_InputEdit.SetPos(ix - w, iy)
        

    
    def GetDesc(self, imode, exmsg):
        import misc
        if interface.IsStyle2():
            sColorType = 'iColor'
        else:
            sColorType = 'iLowColor'
        color = misc.NewGetCashColor(self.m_Cash, sColorType = sColorType)
        DESC_TXT = ('\xb1z\xa5\xd8\xabe\xabO\xa6s\xa6b\xa7\xda\xb3B\xaa\xba\xc2I\xa5d\xb1H\xb0\xe2\xa6\xac\xa4J\xa6\xb3\xa1G#r#c%.6X%d#n\xa8\xe2\xbb\xc8\xa4l#r\xb1z\xadn\xa8\xfa\xa5X\xa6h\xa4\xd6\xa1H', '\xb1z\xa5i\xa5H\xb1N\xa9~\xa5\xc1\xa4p\xb0\xcf\xaa\xba\xb8\xea\xaa\xf7\xb4\xa3\xa5X\xa4@\xb3\xa1\xa4\xc0\xa5\xce\xa9\xf3\xa4\xe4\xb4\xa9\xc0\xb0\xac\xa3\xab\xd8\xb3]\xa1C\xa6\xfd\xacO\xa4p\xb0\xcf\xb3\xd1\xbel\xb8\xea\xaa\xf7\xb3\xcc\xa7C\xa4\xa3\xb1o\xa4\xd6\xa9\xf3100\xb8U\xa1C\xa5\xd8\xabe\xa4p\xb0\xcf\xa6\xb3\xb8\xea\xaa\xf7#c%.6X%d#n\xa1A\xb1z\xadn\xb4\xa3\xa8\xfa\xa6h\xa4\xd6\xa1H', '\xb1z\xa5\xd8\xabe\xa5i\xa5H\xbb\xe2\xa8\xfa\xaa\xba\xa5R\xad\xc8\xbc\xfa\xc0y\xa6\xb3\xa1G#r#c%.6X%d#n\xb2{\xaa\xf7#r\xb1z\xadn\xa8\xfa\xa5X\xa6h\xa4\xd6\xb2{\xaa\xf7\xa1H')
        if imode - 1 < len(DESC_TXT):
            return DESC_TXT[imode - 1] % (color, self.m_Cash) + exmsg
        

    
    def GetInputMoney(self, msgtxt):
        import usermacro
        
        try:
            cash = int(self.m_InputEdit.GetText())
        except ValueError:
            usermacro.PROMPT_MSG(msgtxt)
            return None

        if cash <= 0:
            self.CloseWindow()
            return None
        
        return cash

    
    def AddOnePercent(self):
        curpos = self.m_MoneySlider.GetBarPos()
        curpos += 1
        if curpos > 100:
            curpos = 100
        
        self.m_MoneySlider.SetBarPos(curpos)
        self.m_MoneySlider.m_Bar.LeftDown()
        self.m_MoneySlider.m_Bar.LeftUp()

    
    def MinusOnePercent(self):
        curpos = self.m_MoneySlider.GetBarPos()
        curpos -= 1
        if curpos < 0:
            curpos = 0
        
        self.m_MoneySlider.SetBarPos(curpos)
        self.m_MoneySlider.m_Bar.LeftDown()
        self.m_MoneySlider.m_Bar.LeftUp()

    
    def CloseWindow(self):
        global g_DlgCashFlow
        g_DlgCashFlow = None

    
    def OnIncreaseMoney(self):
        curInputMoney = self.m_InputEdit.GetText()
        
        try:
            iMoney = int(curInputMoney)
        except:
            iMoney = 0

        iMoney += 1000000
        self.m_InputEdit.SetText('%d' % iMoney)

    
    def OnDecreaseMoney(self):
        curInputMoney = self.m_InputEdit.GetText()
        
        try:
            iMoney = int(curInputMoney)
        except:
            iMoney = 0

        iMoney -= 1000000
        if iMoney < 0:
            iMoney = 0
        
        self.m_InputEdit.SetText('%d' % iMoney)

    
    def OnContrlMenoy(self):
        cash = self.GetInputMoney('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xf7\xc3B')
        if not cash:
            cash = 0
        
        if self.m_IMode == 0:
            import netitemshop
            netitemshop.C2SSetAdFee(cash)
        else:
            import nethandleui
            nethandleui.C2SDrawMoney(self.m_IMode, '%d' % cash, self.m_ResponID)
        self.CloseWindow()

    
    def OnChange(self):
        curInputMoney = self.m_InputEdit.GetText()
        
        try:
            iMoney = float(curInputMoney)
            ratio = int(iMoney * 100 / self.m_CanUseCash)
            self.m_MoneySlider.SetBarPos(ratio)
        except:
            return None


    
    def OnSliderLeftUp(self, pos):
        curText = '%d' % self.m_CanUseCash * pos / 100
        self.m_InputEdit.SetText(curText)

    
    def OnButtonEnter(self, btn):
        tipsTxt = {
            2: '\xc2I\xc0\xbb1\xa6\xb8\xb4\xee\xa4\xd6100\xb8U\xa1A\xa4\xa3\xa8\xac\xabh\xb4\xee\xa4\xd6\xac\xb00',
            3: '\xc2I\xc0\xbb1\xa6\xb8\xbcW\xa5[100\xb8U\xa1A\xa4\xa3\xa8\xac\xabh\xa5\xfe\xb3\xa1\xbcW\xa5[',
            8: '\xc2I\xc0\xbb\xb4\xee\xa4\xd61%',
            9: '\xc2I\xc0\xbb\xbcW\xa5[1%' }
        self.m_Tips = wrapinterface.CTextTips(self, -1, tipsTxt[btn.m_MsgID], interface.FontLT14_3, direct = 1)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def OnMessage(self, msgid):
        if msgid in (1, 5):
            self.CloseWindow()
        elif msgid == 2:
            self.OnDecreaseMoney()
        elif msgid == 3:
            self.OnIncreaseMoney()
        elif msgid == 4:
            self.OnContrlMenoy()
        elif msgid == 8:
            self.MinusOnePercent()
        elif msgid == 9:
            self.AddOnePercent()
