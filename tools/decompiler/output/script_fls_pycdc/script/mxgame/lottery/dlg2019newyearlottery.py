# pycdc 交叉复核产物 · script.fls entry 4688
# co_filename(原始)='script/mxgame/lottery/dlg2019newyearlottery.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4688.pyc (Python 2.5)

import combdialog
import combmacro
import commondialog
import dlgdialbox
import interface
import itemdata
import misc
import ui
import usermacro
import wrapinterface
g_oSignUpDlg = None

def ModuleReset():
    global g_oSignUpDlg
    g_oSignUpDlg = None


def ShowRealItemDlg(iItemID, sName):
    global g_oSignUpDlg
    if not g_oSignUpDlg:
        g_oSignUpDlg = CRealItemDlg(iItemID, sName)
    
    return g_oSignUpDlg


class CDialBox2019KuanianLottery(dlgdialbox.CDialBox):
    SHARESHAPE = [
        73455,
        73454,
        73457,
        73456,
        73447,
        73448,
        72452,
        73450,
        72453,
        72446,
        73449,
        73451]
    s_Lucky = 0
    s_LotteryTimes = 1
    s_LoginCount = 0
    LIMIT = {
        1: 0,
        2: 100,
        3: 200,
        4: 300,
        5: 400,
        6: 600,
        7: 800 }
    LOGIN_LIMIT = {
        1: 0,
        2: 1,
        3: 1,
        4: 2,
        5: 3,
        6: 5,
        7: 7 }
    s_OpenFlag = False
    
    class CMyNotifyBox(interface.CNotifyBox):
        
        def Enter(self):
            self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_TipTxt, interface.FontLT14_3, direct = 1)

        
        def Leave(self):
            self.m_Tips = None

        
        def SetTipsTxt(self, txt):
            self.m_TipTxt = txt


    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog4/lottery/2019lottery/lottery.dlg')
        self.Capture(1, 0)
        (px, py) = self.GetParent().GetSize()
        self.SetPos((px - 670) / 2, (py - 560) / 2)
        self.m_Over = True
        self.m_Flash1 = None
        self.m_Flash2 = None
        self.m_Flash3 = None
        self.m_Delay = None
        self.m_Now = CDialBox2019KuanianLottery.s_LotteryTimes
        self.CreateGoodList(1)
        self.SwitchBtn()
        self.m_HideFlag = None if CDialBox2019KuanianLottery.s_LotteryTimes < 4 else False
        self.RefreshDlg()
        self.HideBtn(self.m_HideFlag)
        self.GetObject('lottery%d' % self.m_Now).LeftUp()
        self.ShowProcess()
        self.CreateTips()
        self.m_GrayBG = ui.CImage(interface.CapturePanel, 'combdialog2/\xbb\xb6\xc0\xd6\xb3\xe9\xbd\xb1/\xc3\xc9\xb0\xe6.igs', interface.UIPath)
        self.m_GrayBG.SetPos(0, 0)
        self.m_GrayBG.SetZ(self.GetZ() - 1)
        for iIndex, sName in enumerate(('lucky2_004', 'lucky2_006', 'lucky2_007', 'lucky2_008', 'lucky2_005', 'lucky2_010')):
            self.GetObject(sName).SetText(str(self.LIMIT[iIndex + 2]))
        
        for iIndex in range(2, 8):
            self.GetObject('lottery%s' % iIndex).SetTips('\xb2\xd6\xadp\xb5n\xbf\xfd%s\xa4\xd1\xa5B\xb2\xd6\xadp\xac\xa1\xc5D%s' % (self.LOGIN_LIMIT[iIndex], self.LIMIT[iIndex]))
        

    
    def ResetClear(cls):
        cls.s_Lucky = 0
        cls.s_LotteryTimes = 1
        cls.s_OpenFlag = False
        cls.s_LoginCount = 0

    ResetClear = classmethod(ResetClear)
    
    def SetLotteryAttr(cls, times, lucky, count):
        CDialBox2019KuanianLottery.s_LotteryTimes = times + 1
        CDialBox2019KuanianLottery.s_Lucky = lucky
        CDialBox2019KuanianLottery.s_LoginCount = count

    SetLotteryAttr = classmethod(SetLotteryAttr)
    
    def GetIdxByShape(self, iTargetShape):
        for iShape, _, _ in enumerate(self.m_GoodLst):
            if iShape == iTargetShape:
                return idx
                continue
        
        return -1

    
    def CreateTips(self):
        (x, y, w, h) = self.GetLocData('luckypoint')
        self.m_LuckyTips = CDialBox2019KuanianLottery.CMyNotifyBox(self, w, h, alpha = 0)
        self.m_LuckyTips.SetPos(x, y)
        self.m_LuckyTips.SetTipsTxt('\xb7\xed\xabe\xac\xa1\xc5D\xad\xc8\xa1G%d' % CDialBox2019KuanianLottery.s_Lucky)
        self.m_LuckyTips.SetZ(1001)

    
    def ShowProcess(self):
        import dlgstate
        (x, y, w, h) = self.GetLocData('luckypoint1')
        self.GetObject('luckypoint1').SetShow(False)
        igsname = 'combdialog2/\xbb\xb6\xc0\xd6\xb3\xe9\xbd\xb1/\xb3\xe9\xbd\xb1\xbd\xf8\xb6\xc8\xcc\xf52.igs'
        self.m_LuckyImage = dlgstate.CProgress(self, w, igsname)
        self.m_LuckyImage.SetPos(x, y)
        iTempLuck = self.s_Lucky
        iLastValue = 0
        iPer = 0
        for iKey in sorted(self.LIMIT.keys()):
            iValue = self.LIMIT[iKey]
            if iValue == 0:
                continue
            
            if iTempLuck <= iLastValue:
                break
            
            iPer += min((iTempLuck - iLastValue) * 1000 / (iValue - iLastValue), 1000)
            iLastValue = iValue
        
        iPer = min(iPer / (len(self.LIMIT.keys()) - 1), 1000)
        self.m_LuckyImage.SetRate(iPer)
        self.m_LuckyImage.SetZ(1000)
        oTxt = self.GetObject('txt_tips')
        (iX, iY) = oTxt.GetPos()
        (iW, iH) = oTxt.GetSize()
        oTxt.SetSize(iW + 200, iH)
        oTxt.SetPos(iX - 100, iY)
        oTxt.SetText('\xb7\xed\xabe\xb2\xd6\xadp\xb5n\xbf\xfd\xa1G%d\xa4\xd1   \xb7\xed\xabe\xac\xa1\xc5D\xab\xd7\xa1G%d' % (self.s_LoginCount, iTempLuck))

    
    def HideBtn(self, hide):
        if not CDialBox2019KuanianLottery.s_OpenFlag:
            CDialBox2019KuanianLottery.s_OpenFlag = True
        else:
            obj = self.GetObject('once_tips')
            if obj:
                obj.SetShow(False)
            
        for idx in range(0, 7):
            obj = self.GetObject('lottery%d' % idx)
            if idx not in (0, 7) and idx < CDialBox2019KuanianLottery.s_LotteryTimes:
                obj.Enable(False)
                obj.SetLight(5)
                obj.m_FinishImg = ui.CImage(obj, 'common\\\xbb\xc6\xc9\xab\xb9\xb4.igs', interface.UIPath)
                (x, y) = obj.GetSize()
                obj.m_FinishImg.SetPos(x - 25, y - 15)
                continue
        
        self.FlashBtn()

    
    def FlashBtn(self):
        
        def doflash(dlg, obj, frame):
            if obj.IsSelected():
                return None
            
            frame = (frame + 1) % 2
            obj.SetFrame(frame + 1)
            return (obj, frame)

        self.ReleaseTimer()
        if CDialBox2019KuanianLottery.s_LotteryTimes <= CDialBox2019KuanianLottery.s_LotteryTimes:
            pass
        elif CDialBox2019KuanianLottery.s_LotteryTimes <= 6 and CDialBox2019KuanianLottery.LIMIT[CDialBox2019KuanianLottery.s_LotteryTimes] <= CDialBox2019KuanianLottery.s_Lucky:
            obj = self.GetObject('lottery%d' % CDialBox2019KuanianLottery.s_LotteryTimes)
            self.m_Flash2 = self.CreatePyCommand(15, doflash, obj, 1)
        
        if getattr(self.m_StartBtn, 'm_EnableFlag', None):
            self.m_Flash3 = self.CreatePyCommand(15, doflash, self.m_StartBtn, 1)
        

    
    def ReleaseTimer(self):
        for i in range(3):
            TimerName = 'm_Flash%d' % (i + 1)
            obj = getattr(self, TimerName, None)
            if obj:
                obj.Release()
                continue
        

    
    def CreateGoodList(self, iType):
        self.m_Type = iType
        import specialgiftdata
        self.m_GoodLst = specialgiftdata.GetData(iType)
        box1 = self.GetObject('box_area1_1')
        box2 = self.GetObject('box_area1_2')
        box3 = self.GetObject('box_area1_3')
        if box1:
            self.m_Items = []
            for shape, num, name in enumerate(self.m_GoodLst):
                if idx < 14:
                    (ix, iy) = box1.GetImage(idx / 7, idx % 7).GetPos()
                    (x, y) = box1.GetPos()
                elif idx <= idx:
                    pass
                elif idx < 17:
                    (ix, iy) = box2.GetImage(0, idx - 14).GetPos()
                    (x, y) = box2.GetPos()
                elif idx == 17:
                    (ix, iy) = box3.GetImage(0, idx - 17).GetPos()
                    (x, y) = box3.GetPos()
                else:
                    LOG_ERR('CreateGoodList\xbf\xf9\xbb~', shape)
                    break
                obj = CNewItemBox(self, shape, num, name)
                obj.SetPos(x + ix + 3, y + iy + 3)
                self.m_Items.\xf6\xe7\xe7\xf2\xf9d(obj)
            
        

    
    def SwitchBtn(self):
        self.m_StartBtn = self.GetObject('btn_start')
        self.m_StopBtn = self.GetObject('btn_stop')
        if self.m_StopBtn:
            self.m_StopBtn.SetShow(False)
        

    
    def BanAllBtn(self):
        if getattr(self, 'm_Flash3', None):
            self.m_Flash3.Release()
        
        for i in range(1, 8):
            obj = self.GetObject('lottery%d' % i)
            if obj:
                obj.Enable(False)
                continue
        

    
    def ClickStart(self):
        import nethdlottery2020
        nethdlottery2020.C2SStartLottery2020(self.m_Now)
        self.m_Over = False
        self.BanAllBtn()
        self.Run()
        self.BeginStart()

    
    def Run(self):
        
        def Flush(obj):
            obj.m_Tick += 1
            prev = 0
            if hasattr(obj, 'm_Select'):
                prev = obj.m_Select
                obj.m_Items[prev].Select(False)
            
            obj.m_Select = (prev + 1) % len(obj.m_Items)
            obj.m_Items[obj.m_Select].Select(True)
            return ()

        self.m_Tick = 0
        self.m_Delay = self.CreatePyCommand(3, Flush)

    
    def BeginStart(self):
        if getattr(self, 'm_Roll', None):
            self.m_Roll.Release()
        
        
        def Go(obj):
            obj.m_Count += 1
            if obj.m_Count == 30:
                obj.m_StartBtn.SetShow(False)
                obj.m_StopBtn.SetShow(True)
                return None
            
            return ()

        self.m_Count = 0
        self.m_Roll = self.CreatePyCommand(1, Go)
        self.m_StartBtn.Enable(False)

    
    def ClickStop(self):
        import nethdlottery2020
        nethdlottery2020.C2SStopLottery2020(self.m_Now)
        self.m_StopBtn.Enable(False)

    
    def OnOver(self):
        self.OnDealMsg()
        
        def beginshare(ob):
            ob.m_Over = True
            oItem = ob.m_Items[ob.m_Result]
            iShape = oItem.GetItemShape()
            sName = oItem.GetItemName()
            if iShape in ob.SHARESHAPE:
                import dlgshare
                dlgshare.ShowBiyi(iShape, sName)
            
            self.CloseWindow(True)

        self.CreatePyCommand(60, beginshare)

    
    def Stop(self, idx, msg):
        if self.m_Delay:
            self.m_Delay.Release()
        
        import net
        net.CreateCmdDelay(30)
        lst = self.Initgamearg(idx, msg)
        (_, delay) = lst.pop()
        self.m_Delay = self.CreatePyCommand(1, CDialBox2019KuanianLottery.OnChoice, lst, delay)

    
    def ReleaseBtn(self):
        if getattr(self, 'm_Roll', None):
            self.m_Roll.Release()
            self.m_Roll = None
        

    
    def ShowLinkDlg(self):
        oDlg = dlgdialbox.g_LinkDlg = dlgdialbox.CNewCombDialog(interface.CapturePanel, 'dialog4/lottery/2019lottery/lotteryrule.dlg')
        oDlg.Capture(1)
        oDlg.SetPos(20, 50)
        oDlg.m_GrayBG = ui.CImage(interface.CapturePanel, 'combdialog2/\xbb\xb6\xc0\xd6\xb3\xe9\xbd\xb1/\xc3\xc9\xb0\xe6.igs', interface.UIPath)
        (px, py) = self.GetParent().GetSize()
        oDlg.SetPos((px - 660) / 2, (py - 420) / 2)
        oDlg.m_GrayBG.SetZ(self.GetZ() + 1)

    
    def CloseWindow(self, flag = False):
        if self.m_Over or flag:
            if self.m_Delay:
                self.m_Delay.Release()
                self.m_Delay = None
            
            if self.m_Flash1:
                self.m_Flash1.Release()
                self.m_Flash1 = None
            
            if self.m_Flash2:
                self.m_Flash2.Release()
                self.m_Flash2 = None
            
            self.ReleaseBtn()
            dlgdialbox.g_DialBox = None
        

    
    def RefreshDlg(self):
        import hero
        tempNum = (self.m_Now + 1) / 2
        if not tempNum:
            tempNum = 1
        elif tempNum == 4:
            tempNum = 3
        
        self.CreateGoodList(self.m_Now)
        for i in xrange(1, 4):
            showFlag = None if i == tempNum else False
            for j in xrange(1, 4):
                obj = self.GetObject('box_area%d_%d' % (i, j))
                if obj:
                    obj.SetShow(showFlag)
                    continue
            
        
        if self.s_Lucky < self.LIMIT[self.m_Now] or self.s_LoginCount < self.LOGIN_LIMIT[self.m_Now]:
            sTxt = '\xbb\xdd\xb2\xd6\xadp\xb5n\xbf\xfd\xa4\xd1\xbc\xc6\xb9F\xa8\xec%s\xa4\xd1\xa1A\xb2\xd6\xadp\xac\xa1\xc5D\xad\xc8\xb9F\xa8\xec%s\xc2I\xa5i\xa9\xe2\xbc\xfa' % (self.LOGIN_LIMIT[self.m_Now], self.LIMIT[self.m_Now])
            enable_flag = False
        elif hero.GetProp('m_Grade', 0) < 10:
            sTxt = '\xbb\xdd\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xba\xa110\xaf\xc5'
            enable_flag = False
        elif self.m_Now != self.s_LotteryTimes:
            sTxt = '\xbd\xd0\xa5\xfd\xb6i\xa6\xe6\xb2\xc4%d\xa6\xb8\xa9\xe2\xbc\xfa' % self.s_LotteryTimes
            enable_flag = False
        else:
            sTxt = ''
            enable_flag = True
        self.m_StartBtn.Enable(enable_flag)
        if not enable_flag:
            (x, y, w, h) = self.GetLocData('btn_start')
            self.m_StartTips = CDialBox2019KuanianLottery.CMyNotifyBox(self, w, h, alpha = 0)
            self.m_StartTips.SetPos(x, y)
            self.m_StartTips.SetTipsTxt(sTxt)
        else:
            self.m_StartTips = None

    
    def OnButtonEnter(self, obj):
        if getattr(obj, 'm_TipsTxt', None):
            self.m_BtnTips = wrapinterface.CTextTips(obj, -1, obj.m_TipsTxt, interface.FontLT14_3, direct = 1)
        

    
    def OnButtonLeave(self, obj):
        self.m_BtnTips = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.ClickStart()
        elif msgid == 3:
            self.CloseWindow()
        elif msgid == 4:
            self.ClickStop()
        elif msgid == 20:
            self.ShowLinkDlg()
        elif msgid == 21:
            pass
        elif msgid <= msgid:
            pass
        elif msgid <= 17:
            if not self.m_Over:
                return None
            
            self.m_Now = msgid - 10
            self.RefreshDlg()
            self.FlashBtn()
        



class CRealItemDlg(combdialog.CCombDialog):
    
    def __init__(self, iID, sName):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/lottery/2019lottery/informationfill.dlg')
        interface.Center(self)
        self.m_oNameEdit = None
        self.m_oIDEdit = None
        self.m_oPhoneEdit = None
        self.m_oAddressEdit = None
        self.m_iItemID = iID
        self.m_sName = sName
        self.InitDlg()
        self.SetItemNameByShape()

    
    def InitDlg(self):
        self.m_oNameEdit = combmacro.CEDIT(interface.CEdit, 'loc_name', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oNameEdit.Active(True)
        self.m_oIDEdit = combmacro.CEDIT(CIDEdit, 'loc_id', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oPhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'loc_phone', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oAddressEdit = combmacro.CEDIT(interface.CEdit, 'loc_dress', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oMailEdit = combmacro.CEDIT(interface.CEdit, 'loc_mail', self, interface.COLOR_1, interface.FontLT14_3, interface.COLOR_1)
        self.m_oNameEdit.SetNextEdit(self.m_oIDEdit)
        self.m_oIDEdit.SetNextEdit(self.m_oPhoneEdit)
        self.m_oPhoneEdit.SetNextEdit(self.m_oAddressEdit)
        self.m_oAddressEdit.SetNextEdit(self.m_oMailEdit)
        self.m_oMailEdit.SetNextEdit(self.m_oNameEdit)

    
    def SetItemNameByShape(self):
        if self.m_iItemID:
            self.GetObject('text_reward').SetText(self.m_sName)
        

    
    def Publish(self):
        sName = self.m_oNameEdit.GetText()
        sID = self.m_oIDEdit.GetText()
        sPhone = self.m_oPhoneEdit.GetText()
        sAddress = self.m_oAddressEdit.GetText()
        sMail = self.m_oMailEdit.GetText()
        if not sName:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa6W\xba\xd9')
            return None
        
        if not sID:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa8\xad\xa5\xf7\xb5\xfd')
            return None
        
        if not sPhone:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa4\xe2\xbe\xf7\xb8\xb9\xbdX')
            return None
        
        if not sAddress:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa6a\xa7}\xabH\xae\xa7')
            return None
        
        if not sMail:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xb6l\xbdc\xabH\xae\xa7')
            return None
        
        commondialog.ShowMessageBox('\xabH\xae\xa7\xb6\xf1\xbcg\xb6\xc8\xa6\xb3\xa4@\xa6\xb8\xbe\xf7\xb7|\xa1A\xbd\xd0\xbdT\xbb{\xacO\xa7_\xb2\xc5\xa6X\xa1H ', ('\xacO', '\xa7_'), (misc.Functor(self.OnConfirmPublisth, sName, sID, sPhone, sMail, sAddress), None))

    
    def OnConfirmPublisth(self, sName, sID, sPhone, sMail, sAddress, obj):
        LOG_DEBUG('\xb4\xa3\xa5\xe6', sName, sID, sPhone, sAddress)
        import nethdlottery2020
        nethdlottery2020.C2STrueItemInfo(self.m_iItemID, sName, sID, sPhone, sMail, sAddress)
        self.CloseWindow()

    
    def CloseWindow(self):
        global g_oSignUpDlg
        if self.m_oNameEdit:
            pass
        self.m_oNameEdit.Active(False)
        if self.m_oIDEdit:
            pass
        self.m_oIDEdit.Active(False)
        if self.m_oPhoneEdit:
            pass
        self.m_oPhoneEdit.Active(False)
        g_oSignUpDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.Publish()
        



class CIDEdit(interface.CEdit):
    
    def AddChar(self, char):
        if not char.isdigit() and char not in ('x', 'X'):
            usermacro.PROMPT_MSG('\xa8\xad\xa5\xf7\xb5\xfd\xa5u\xa4\xb9\xb3\\\xbf\xe9\xa4J\xbc\xc6\xa6r\xa1Bx\xbbPX\xa1A\xbd\xd0\xab\xf6\xadn\xa8D\xbf\xe9\xa4J')
            return None
        
        interface.CEdit.AddChar(self, char)



class CNewItemBox(dlgdialbox.CItemBoxLottery):
    
    def __init__(self, parent, shape, num, txt):
        dlgdialbox.CItemBoxLottery.__init__(self, parent, shape, num, txt)
        self.m_SelBox.SetPos(-7, -8)

    
    def SetText(self, txt):
        self.m_Text = txt

    
    def Enter(self):
        (_, sExplain) = itemdata.GetData(self.m_ItemShape)
        self.m_Tips = wrapinterface.CItemTips(self.m_ItemShape, '', self.m_Text, sExplain, '', charcount = 30)

    
    def Leave(self):
        self.m_Tips = None
