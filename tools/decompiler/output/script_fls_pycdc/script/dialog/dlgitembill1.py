# pycdc 交叉复核产物 · script.fls entry 3279
# co_filename(原始)='script/dialog/dlgitembill1.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3279.pyc (Python 2.5)

import copy
import datetime
import commondialog
import dlggetinfo
import itemdata
import mdredpoint
import cfg
import combdialog
import combmacro
import dlgdialbox
import interface
import itemdefine
import misc
import net
import netreddot
import permission
import ui
import usermacro
import wrapinterface
import dlgitembill1_item
import itembilldefines
import mdreddot
import dlgreddot
g_ItemBill = None
g_tips = None
g_CardPay = None
g_CardCharge = None
g_DytPointDlg = None
g_SecretRedpoint = False
g_FestivelRedpoint = False
g_TreasureRedpoint = False
g_NewServerRedpoint = False
g_DiscountRedPoint = False
g_LastSelectData = { }
g_PageData = { }
g_dAccumulation = { }
g_dPageExtData = { }

def ModuleReset():
    global g_ItemBill, g_tips, g_CardPay, g_CardCharge, g_DytPointDlg, g_SecretRedpoint, g_FestivelRedpoint, g_TreasureRedpoint, g_NewServerRedpoint, g_DiscountRedPoint, g_LastSelectData, g_PageData, g_dAccumulation, g_dPageExtData
    g_ItemBill = None
    g_tips = None
    g_CardPay = None
    g_CardCharge = None
    g_DytPointDlg = None
    g_SecretRedpoint = False
    g_FestivelRedpoint = False
    g_TreasureRedpoint = False
    g_NewServerRedpoint = False
    g_DiscountRedPoint = False
    g_LastSelectData = { }
    g_PageData = { }
    g_dAccumulation = { }
    g_dPageExtData = { }


def SetPageExtData(iPage, sDataKey, anyDataValue):
    if iPage not in g_dPageExtData:
        g_dPageExtData[iPage] = { }
    
    g_dPageExtData[iPage][sDataKey] = anyDataValue


def GetPageExtData(iPage, sDataKey, anyValue = None):
    return g_dPageExtData.get(iPage, { }).get(sDataKey, anyValue)


def RefershBuyLst(iPage, buylist):
    if g_ItemBill:
        buylistOld = g_PageData.get(iPage, None)
        curPage = g_PageData.get('curRefreshUIPage')
        if buylistOld == buylist and curPage == iPage:
            oGoods = g_ItemBill.m_oDlgGoods
            if oGoods and oGoods.GetShow():
                oGoods.OnCloseMiniBuyPanel()
                return None
            
        
        g_PageData['curRefreshUIPage'] = iPage
        g_PageData[iPage] = copy.deepcopy(buylist)
        g_ItemBill.SetBuyList(buylist, iRealPage = iPage)
        cfg.SaveData('mx.ini', 'Game', 'GoodsPage', str(iPage))
        if iPage == 1:
            cfg.SaveData('mx.ini', 'Game', 'ShowGoodsTime', '%s:%s:%s' % datetime.date.isocalendar(datetime.date.today()))
        
    


def CloseWindow():
    global g_LastSelectData, g_ItemBill
    g_LastSelectData = { }
    if g_ItemBill:
        g_ItemBill.Clear()
    
    g_ItemBill = None


def QuickPay():
    import mdpay
    if mdpay.IsNewPay():
        import dlgpay
        import hero
        mdpay.GetModel().SetTargetID(hero.GetHeroID())
        dlgpay.Show()
    else:
        import quickpay
        quickpay.Show()


def QuickPay_TW():
    import dlgnpc
    import main
    if main.g_LangVersion == 0:
        sDesc = '\xbd\xd0\xbf\xef\xbe\xdc\xa5R\xad\xc8\xa4\xe8\xa6\xa1\nL\xb3q\xa5\xce\xa5d\xc2\xe0\xb1H\xb0\xe2\xa5d\nL\xb3q\xa5\xce\xa5d\xc2\xe0\xb9C\xc0\xb8\xc2I\xbc\xc6\nLATM\xc1\xca\xb6R\xb9C\xc0\xb8\xc2I\xbc\xc6'
    else:
        sDesc = '\xbd\xd0\xbf\xef\xbe\xdc\xa5R\xad\xc8\xa4\xe8\xa6\xa1\nL\xb3q\xa5\xce\xa5d\xc2\xe0\xb1H\xb0\xe2\xa5d\nL\xb3q\xa5\xce\xa5d\xc2\xe0\xb9C\xc0\xb8\xc2I\xbc\xc6'
    dlgnpc.ShowClientDlg(sDesc, '', misc.Functor(OnQuickPayCallBack))


def OnQuickPayCallBack(iMsgID):
    import dlgitembill
    import gameurl
    import security
    if iMsgID == 1:
        dlgitembill.CSGSAskOpenBuildCard()
    elif iMsgID == 2:
        dlgitembill.CSGSAskBuyPointShop()
    elif iMsgID == 3:
        web = gameurl.BUYCARD_USEATM_URL
        token_key = security.CreateOneEncodeGuid()
        web += '&tokenkey=%s' % token_key
        net.OpenUrl(web)
    


def DoubleElevenBlinkDiscount(iFlag):
    if g_ItemBill and g_ItemBill.GetShow():
        g_ItemBill.BlinkDoubleEleven(iFlag)
    


def GetDefoultPage(iShowBtnList):
    iDefaultPage = itembilldefines.DEFAULT_PAGE
    sCurPage = cfg.GetData('mx.ini', 'Game', 'GoodsPage')
    if sCurPage and sCurPage.isdigit():
        iDefaultPage = int(sCurPage)
    
    sTime = cfg.GetData('mx.ini', 'Game', 'ShowGoodsTime')
    if sTime:
        sTimeList = sTime.split(':')
        if len(sTimeList) >= 2 and sTimeList[0].isdigit() and sTimeList[1].isdigit():
            (iYear, iWeek, _) = datetime.date.isocalendar(datetime.date.today())
            if iYear != int(sTimeList[0]) or iWeek != int(sTimeList[1]):
                iDefaultPage = itembilldefines.DEFAULT_PAGE
            
        
    
    if iDefaultPage not in iShowBtnList:
        iBtnList = [
            9,
            8,
            5,
            7,
            3,
            4,
            2,
            6,
            1]
        for iPage in iBtnList:
            if iPage in iShowBtnList:
                iDefaultPage = iPage
                break
                continue
        
    
    return iDefaultPage


def Show(oParent, iShowBtnList, iDefaultPage, iDefaultItemID):
    '''
\t:param oParent: \xa4\xf7\xbf\xcb
\t:param iShowBtnList: \xc5\xe3\xa5\xdc\xab\xf6\xb6s\xa6C\xaa\xed
\t:param iDefaultPage: \xc0q\xbb{\xbf\xef\xa4\xa4\xa4\xc0\xad\xb6
\t:param iDefaultItemID: \xc0q\xbb{\xbf\xef\xa4\xa4\xaa\xab\xab~ID
\t:return:
\t'''
    global g_ItemBill
    if iDefaultPage == 0:
        iDefaultPage = GetDefoultPage(iShowBtnList)
    
    LOG_DEBUG('\xa5\xb4\xb6}\xb0\xd3\xab\xb0', iShowBtnList, iDefaultPage)
    g_ItemBill = CItemBillMain(oParent, iShowBtnList, iDefaultPage, iDefaultItemID)
    g_ItemBill.SetZ(3)
    if iDefaultPage in g_PageData:
        buyList = g_PageData[iDefaultPage]
        buyList = copy.deepcopy(buyList)
        g_ItemBill.SetBuyList(buyList, iRealPage = iDefaultPage)
    
    g_PageData['curRefreshUIPage'] = iDefaultPage
    cfg.SaveData('mx.ini', 'Game', 'GoodsPage', str(iDefaultPage))
    if iDefaultPage == 1:
        cfg.SaveData('mx.ini', 'Game', 'ShowGoodsTime', '%s:%s:%s' % datetime.date.isocalendar(datetime.date.today()))
    


def IsOpen():
    return g_ItemBill is not None


def ShowCardPay(parent):
    global g_CardPay
    g_CardPay = CCardPay(parent)


def ShowState467Tips(isShow):
    if g_ItemBill:
        g_ItemBill.ShowState467Tips(isShow)
    


def CreateRedpointObj(oParent):
    obj = ui.CImage(oParent, 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe\xd0\xa1\xba\xec\xb5\xe3.igs', 'interface')
    obj.SetPos(70, 2)
    obj.SetZ(30)
    return obj


def SetGoldShopRedPoint():
    import model_mapinfobar
    if not g_SecretRedpoint and g_FestivelRedpoint and g_NewServerRedpoint:
        pass
    model_mapinfobar.GetModel().SetGoldShopRedPoint(g_DiscountRedPoint)


def ResetSecretRedpoint(bShow):
    global g_SecretRedpoint
    g_SecretRedpoint = bShow
    if g_ItemBill:
        g_ItemBill.SetSecretRedpoint(g_SecretRedpoint)
    
    SetGoldShopRedPoint()


def ResetFestivalRedpoint(bShow):
    global g_FestivelRedpoint
    g_FestivelRedpoint = bShow
    if g_ItemBill:
        g_ItemBill.SetFestivalRedpoint(g_FestivelRedpoint)
    
    SetGoldShopRedPoint()


def ResetTreasureRedpoint(bShow):
    global g_TreasureRedpoint
    g_TreasureRedpoint = bShow
    if g_ItemBill:
        g_ItemBill.SetTreasureRedpoint(g_TreasureRedpoint)
    
    SetGoldShopRedPoint()


def ResetNewServerRedpoint(bShow):
    global g_NewServerRedpoint
    g_NewServerRedpoint = bShow
    if g_ItemBill:
        g_ItemBill.SetNewServerRedPoint(g_NewServerRedpoint)
    
    SetGoldShopRedPoint()


def ResetDiscountShopRedpoint(bShow):
    global g_DiscountRedPoint
    g_DiscountRedPoint = bShow
    if g_ItemBill:
        g_ItemBill.SetDiscountShopRedpoint(g_DiscountRedPoint)
    
    SetGoldShopRedPoint()


def SetAccumulationShapeData(iShopType, iShapeList):
    g_dAccumulation[iShopType] = iShapeList


def SetDingYueShape(dShape, dCanShape):
    CReadyDingYueDlg.OpenUI(dShape, dCanShape)


def GetDiscountNum(iDiscount, bGrey = False):
    if iDiscount <= iDiscount:
        pass
    elif iDiscount < 100:
        if iDiscount % 10 == 0:
            iDiscount /= 10
        
        sPath = TW_NOCHANGE('%d\xd5\xdb') % iDiscount
    elif iDiscount == 0:
        sPath = TW_NOCHANGE('\xcf\xde\xb9\xba')
    else:
        return ''
    if bGrey:
        sPath = sPath + TW_NOCHANGE('-\xbb\xd2')
    
    sPath = TW_NOCHANGE('combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xd5\xdb\xbf\xdb\xbd\xc7\xb1\xea/%s.png') % sPath
    if misc.FileExist(sPath, interface.UIPath):
        return sPath
    else:
        return ''


class CCardPay(combdialog.CCombDialog):
    
    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/itembill/cardpay.dlg')
        interface.Center(self)

    
    def CloseWindow(self):
        global g_CardPay
        g_CardPay = None

    
    def OnMessage(self, msgid):
        msgid2log = {
            2: '\xc2I\xa5d\xa5R\xad\xc8-\xa5R\xac\xb0\xc2I\xbc\xc6',
            3: '\xc2I\xa5d\xa5R\xad\xc8-\xa5R\xac\xb0\xb1H\xb0\xe2\xa5d',
            4: '\xc2I\xa5d\xa5R\xad\xc8-\xc2I\xbc\xc6\xc2\xe0\xa5@\xb0^' }
        if msgid in msgid2log:
            import clickcounter
            clickcounter.Log(msgid2log[msgid])
        
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            import usermacro
            par = self.GetParent()
            code = par.m_CodeEdit.GetText()
            pwd = par.m_PwdEdit.GetText()
            par.m_CodeEdit.Clear()
            par.m_PwdEdit.Clear()
            par.m_CodeEdit.Active(True)
            if len(code) != 12:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xa5d\xb8\xb9')
                return None
            
            if len(pwd) != 8:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xb1K\xbdX')
                return None
            
            import netplayer
            netplayer.C2SNpcCharge(code, pwd)
        elif msgid == 3:
            import usermacro
            par = self.GetParent()
            code = par.m_CodeEdit.GetText()
            pwd = par.m_PwdEdit.GetText()
            par.m_CodeEdit.Clear()
            par.m_PwdEdit.Clear()
            par.m_CodeEdit.Active(True)
            if len(code) != 12:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xa5d\xb8\xb9')
                return None
            
            if len(pwd) != 8:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xb1K\xbdX')
                return None
            
            import netplayer
            netplayer.C2SDiankaMake(code, pwd)
        elif msgid == 4:
            CSGSPointChangeWorldContributeShop()
        



def ShowCardCharge(chargedata):
    global g_CardCharge
    import hero
    import dlgshenmoisland
    import usermacro
    if hero.IsShenHe():
        return None
    
    if dlgshenmoisland.IsShenmoHuodong():
        usermacro.PROMPT_MSG('\xbc\xc8\xae\xc9\xb5L\xaak\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0\xa1A\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xa6A\xa8\xcf\xa5\xce')
        return None
    
    if not g_CardCharge:
        g_CardCharge = CCardCharge()
    
    g_CardCharge.InitData(chargedata)
    g_CardCharge.Topmost()


def ShowCardMoney(iSeq, iMode, iCash):
    import popupmgr
    if g_CardCharge:
        g_CardCharge.OpenCardMoney(iSeq, iMode, iCash)
    else:
        popupmgr.GetPopupMgr().OpenUI(CCardMoneyDlg, interface.DialogPanel, [
            iMode,
            iCash,
            iSeq])


def RefreshData(data):
    if g_CardCharge:
        g_CardCharge.RefreshData(data)
    


class CCardCharge(combdialog.CCombDialog):
    
    class CBuyAmount(interface.CEdit):
        
        def AddChar(self, char):
            if char.isdigit():
                if char == char:
                    pass
                elif char == '0':
                    return None
                
                interface.CEdit.AddChar(self, char)
            
            amount = self.GetNumber()
            if amount > 5:
                self.SetText('5')
            

        
        def MakeCT(self):
            txt = self.GetText()
            
            try:
                amount = int(txt)
            except ValueError:
                amount = None

            self.GetParent().SetBuyAmount(amount)

        
        def CharInput(self, c):
            interface.CEdit.CharInput(self, c)
            self.MakeCT()

        
        def MsgDelete(self):
            interface.CEdit.MsgDelete(self)
            self.MakeCT()

        
        def MsgBack(self):
            interface.CEdit.MsgBack(self)
            self.MakeCT()


    
    class CBuyPrice(wrapinterface.CNumberEdit):
        
        def CharInput(self, c):
            interface.CEdit.CharInput(self, c)
            txt = self.GetText()
            
            try:
                price = int(txt)
            except ValueError:
                price = None

            self.GetParent().SetTotalPrice(price)


    
    class CSellAmount(wrapinterface.CNumberEdit):
        
        def AddChar(self, c):
            wrapinterface.CNumberEdit.AddChar(self, c)
            self.GetParent().OnSellAmountChg()

        
        def MsgDelete(self):
            wrapinterface.CNumberEdit.MsgDelete(self)
            self.GetParent().OnSellAmountChg()

        
        def MsgBack(self):
            wrapinterface.CNumberEdit.MsgBack(self)
            self.GetParent().OnSellAmountChg()


    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/itembill/cardcharge.dlg')
        interface.Center(self)
        self.m_ChargeType = 0
        self.m_iMaxPrice = 0
        self.m_iMinPrice = 0
        self.SetBtnType()
        self.InitSignals()

    
    def InitSignals(self):
        import netreddot
        oModel = mdredpoint.GetCRedPointModel()
        oModel.ssConnect(oModel.SS_UpdateRedPoint, self.CheckCardMoneyRedPoint)
        dRedPoint = oModel.GetRedPointState(netreddot.CARDGETMONEY)
        self.CheckCardMoneyRedPoint(netreddot.CARDGETMONEY, dRedPoint.get('bRed'), dRedPoint.get('iNum'))

    
    def CheckCardMoneyRedPoint(self, iType, bRed, iNum):
        import netreddot
        if iType == netreddot.CARDGETMONEY:
            self.EnableBtnGetMoneyRedDot(bRed)
        

    
    def SetBtnType(self):
        for objname in ('btn_info', 'btn_jsk'):
            self.GetObject(objname).m_ParentNotify = True
        

    
    def OnButtonEnter(self, btn):
        txt = {
            2: '\xacd\xb8\xdf\xa5\xe6\xa9\xf6\xb0O\xbf\xfd\xa9M\xb1\xbe\xb3\xe6\xb0O\xbf\xfd',
            9: '\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa7\xd6\xb3t\xa5R\xad\xc8\xb1H\xb0\xe2\xa5d' }[btn.m_MsgID]
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def EnableBtnGetMoneyRedDot(self, bEnable):
        oBtnGetMoney = self.GetObject('btn_getmoney')
        if bEnable:
            oBtnGetMoney.SetBigRedDot(11, iOffsetX = 7, iOffsetY = -7)
        else:
            oBtnGetMoney.SetBigRedDot(0)

    
    def InitData(self, chargedata):
        self.m_Remain = chargedata.get('remain', -1)
        self.m_Currency = chargedata.get('currency', 0)
        self.m_ChargeType = chargedata.get('chargetype', 0)
        self.m_iMaxPrice = chargedata.get('iMaxPrice', 0)
        self.m_iMinPrice = chargedata.get('iMinPrice', 0)
        if self.m_Currency == 0:
            sTips = '\xb1H\xb0\xe2\xb3\xe6\xbb\xf9\xa5\xb2\xb6\xb7\xacO10000\xaa\xba\xbe\xe3\xbc\xc6\xad\xbf'
        else:
            sTips = '\xb1H\xb0\xe2\xb3\xe6\xbb\xf9\xa5\xb2\xb6\xb7\xacO100\xaa\xba\xbe\xe3\xbc\xc6\xad\xbf'
        self.GetObject('tips_help_1').SetTips(sTips)
        self.RefershCtrl()

    
    def RefershCtrl(self):
        color = interface.COLOR_5
        if self.m_ChargeType == 0:
            self.m_BuyAmountEdit = combmacro.CEDIT(CCardCharge.CBuyAmount, 'amount', self, color, interface.FontLT14_3)
            self.m_BuyAmountEdit.SetLimit(4)
            self.m_BuyAmount = None
            self.m_PriceEdit = combmacro.CEDIT(CCardCharge.CBuyPrice, 'price', self, color, interface.FontLT14_3)
            self.m_PriceEdit.SetLimit(9)
            self.m_PriceEdit.m_IsMoney = True
            self.m_SinglePrice = None
            import hero
            if self.m_Currency == 0:
                hero.CreateCombDlgCash('cash', 'dlgcardcharge', (('m_Cash', 0, 0),), self)
                sText = '\xb7\xed\xabe\xb2{\xaa\xf7'
            else:
                hero.CreateCombDlgCash('cash', 'dlgcardcharge', (('m_ShenWuBi', 0, 0),), self)
                sText = '  \xb9\xda\xb7Q\xb9\xf4'
            it = self.GetObject('noname14')
            it.ReplaceText({
                '\xb7\xed\xabe\xb2{\xaa\xf7': sText })
            self.GetObject('btn_BuyTab').SetSelect(True)
            self.SetShowObject('tips_help_1', False)
            self.m_NoticeTxt = None
        else:
            self.m_RemainTxt = combmacro.CTEXT(interface.CTextObject, 'remain', self, '%d' % self.m_Remain, interface.FontLT14_3, color)
            self.m_SellAmountEdit = combmacro.CEDIT(CCardCharge.CSellAmount, 'amount1', self, color, interface.FontLT14_3)
            self.m_SellAmountEdit.SetLimit(5)
            self.m_SellAmountEdit.Active(True)
            self.m_PriceEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'price1', self, color, interface.FontLT14_3)
            self.m_PriceEdit.SetTipsInfo('\xbb\xf9\xae\xe6\xbdd\xb3\xf2\xa1G%s-%s' % (self.m_iMinPrice, self.m_iMaxPrice), 0, 1)
            self.m_PriceEdit.m_IsMoney = True
            self.m_PriceEdit.SetLimit(8)
            self.m_PriceEdit.SetCharChangeCB(misc.Functor(self.OnPriceEditContentChange))
            txt = ''.join([
                '\xaa`\xb7N\xa1G\xb1H\xb0\xe2\xa5d\xa5i\xb3q\xa5\xce\xa9\xf3\xbd\xe3\xb8\xb9\xa4U\xa9\xd2\xa6\xb3\xaaA\xb0\xc8\xbe\xb9\xaa\xba\xa9\xd2\xa6\xb3\xa8\xa4\xa6\xe2\xa1C',
                '\xb1H\xb0\xe2\xc0\xf2\xb1o\xa6\xac\xa4J\xa5i\xc2I\xc0\xbb\xa4U\xa4\xe8\xab\xf6\xb6s\xa9\xce\xabe\xa9\xb9\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3\xb3B\xbb\xe2\xa8\xfa\xa1C'])
            oLocTxtTip = self.GetObject('txt_Tip')
            it = interface.CRichTextObject(oLocTxtTip, oLocTxtTip.GetSize()[0], interface.FontLT12_1, txt, interface.COLOR_30)
            self.m_NoticeTxt = it
            self.GetObject('btn_SaleTab').SetSelect(True)
            self.SetShowObject('tips_help_1', True)

    
    def OnPriceEditContentChange(self, *vArgs):
        import usermacro
        sText = self.m_PriceEdit.GetText()
        if sText.isdigit():
            iValue = int(sText)
            if iValue > self.m_iMaxPrice:
                usermacro.PROMPT_MSG('\xb1z\xb3]\xb8m\xaa\xba\xb3\xe6\xbb\xf9\xb9F\xa8\xec\xb7\xed\xabe\xa5i\xb3]\xb8m\xaa\xba\xa4W\xad\xad')
                self.m_PriceEdit.SetText(str(self.m_iMaxPrice))
            
        

    
    def ChangeMoney(self, price):
        return misc.ChangeMoney(str(price))

    
    def RefreshData(self, data):
        markettbl = self.GetObject('markettbl')
        markettbl.Clear()
        for i in xrange(4, 0, -1):
            for num, amount, price in data:
                if i == num:
                    it = markettbl.AddTextItem(('\xa5\xbf\xa6b\xa5X\xb0\xe2', self.ChangeMoney(price), str(amount)), color = interface.COLOR_195)
                    if self.m_ChargeType == 0:
                        it.m_BuyType = 1
                    else:
                        it.m_SellType = 1
                    it.m_Price = price
                    break
                    continue
            else:
                it = markettbl.AddTextItem(('--', '--', '--'))
                it.m_SellType = 0
                it.m_BuyType = 0
        
        for i in xrange(11, 15):
            for num, amount, price in data:
                if i == num:
                    it = markettbl.AddTextItem(('\xa5\xbf\xa6b\xa6\xac\xc1\xca', self.ChangeMoney(price), str(amount)), color = interface.COLOR_175)
                    if self.m_ChargeType == 0:
                        it.m_BuyType = 2
                    else:
                        it.m_SellType = 2
                    it.m_Price = price
                    break
                    continue
            else:
                it = markettbl.AddTextItem(('--', '--', '--'))
                it.m_BuyType = 0
                it.m_SellType = 0
        
        markettbl.ResetItems()

    
    def OnSellAmountChg(self):
        
        try:
            amount = int(self.m_SellAmountEdit.GetText())
        except ValueError:
            self.m_Yajin = None
            return None

        color = interface.COLOR_5
        self.m_Yajin = combmacro.CTEXT(interface.CTextObject, 'yajin1', self, '%d' % amount * 10000, interface.FontLT14_3, color)

    
    def SetBuyAmount(self, amount):
        self.m_BuyAmount = amount
        if amount is not None:
            color = interface.COLOR_5
            self.m_Yajin = combmacro.CTEXT(interface.CTextObject, 'yajin', self, misc.ChangeMoney('%d' % amount * 10000), interface.FontLT14_3, color)
        
        self.SetTotalPrice(self.m_SinglePrice)

    
    def SetTotalPrice(self, price):
        if self.m_BuyAmount is None or price is None:
            self.m_TotalPriceTxt = None
            return None
        
        self.m_SinglePrice = price
        color = interface.COLOR_5
        self.m_TotalPriceTxt = combmacro.CTEXT(interface.CTextObject, 'totalprice', self, misc.ChangeMoney('%d' % self.m_BuyAmount * price), interface.FontLT14_3, color)

    
    def CloseWindow(self):
        global g_CardCharge
        import popupmgr
        import netplayer
        g_CardCharge = None
        popupmgr.GetPopupMgr().CloseUI(CCardMoneyDlg)
        netplayer.C2SDytCloseWindow()

    
    def DoBuy(self, msgid):
        tbl = self.GetObject('markettbl')
        if msgid - 101 >= len(tbl.m_Items):
            return None
        
        it = tbl.m_Items[msgid - 101]
        if msgid == 104 and hasattr(it, 'm_BuyType') and it.m_BuyType == 1:
            self.m_BuyAmountEdit.SetText('1')
            self.m_BuyAmountEdit.Active(True)
            self.m_BuyAmountEdit.SetSelect(0, 999)
            self.m_PriceEdit.SetText(str(it.m_Price))
        else:
            it.m_SelectColor = -1

    
    def DoSell(self, msgid):
        tbl = self.GetObject('markettbl')
        if msgid - 101 >= len(tbl.m_Items):
            return None
        
        it = tbl.m_Items[msgid - 101]
        if not hasattr(it, 'm_SellType'):
            return None
        
        if msgid == 105 and it.m_SellType == 2:
            self.m_SellAmountEdit.SetText('1')
            self.m_PriceEdit.SetText(str(it.m_Price))
        else:
            it.m_SelectColor = -1

    
    def OpenCardMoney(self, iSeq, iMode, iCash):
        import popupmgr
        popupmgr.GetPopupMgr().OpenUI(CCardMoneyDlg, self, [
            iMode,
            int(iCash),
            iSeq])

    
    def OnMessage(self, msgid):
        msgid2log = {
            6: '\xb1H\xb0\xe2\xa5d\xa5\xe6\xa9\xf6-\xb1\xbe\xb3\xe6\xb0O\xbf\xfd',
            7: '\xb1H\xb0\xe2\xa5d\xa5\xe6\xa9\xf6-\xbaM\xb3\xe6',
            3: '\xb1H\xb0\xe2\xa5d\xa5\xe6\xa9\xf6-\xbdT\xbb{\xbb{\xc1\xca',
            8: '\xb1H\xb0\xe2\xa5d\xa5\xe6\xa9\xf6-\xbdT\xbb{\xb1H\xb0\xe2' }
        if msgid in msgid2log:
            import clickcounter
            clickcounter.Log(msgid2log[msgid])
        
        if msgid == 1:
            self.CloseWindow()
        elif msgid in (2, 10):
            CSGSAskOpenLookBuyPosition()
        elif msgid == 3:
            import usermacro
            if self.m_BuyAmount is None:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xba\xa6\xac\xc1\xca\xbc\xc6\xb6q')
                return None
            
            if self.m_SinglePrice is None:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xba\xa6\xac\xc1\xca\xbb\xf9\xae\xe6')
                return None
            
            import netplayer
            netplayer.C2SDiankaBuy(self.m_BuyAmount, self.m_SinglePrice, self.m_Currency)
            self.m_BuyAmountEdit.SetText('')
            self.m_BuyAmount = None
            self.m_PriceEdit.SetText('')
            self.m_SinglePrice = None
            self.m_Yajin = None
            self.m_TotalPriceTxt = None
        elif msgid == 4:
            CSGSAskBuyTimeCardShop(self.m_Currency)
        elif msgid == 5:
            CSGSAskOpenSellCard(self.m_Currency)
        elif msgid == 6:
            import netcommon
            netcommon.C2SOnCashClick(2)
            self.EnableBtnGetMoneyRedDot(False)
        elif msgid in (7, 11):
            CSGSAskOpenStripping(self.m_Currency)
        elif msgid == 8:
            import usermacro
            amount = self.m_SellAmountEdit.GetText()
            
            try:
                amount = int(amount)
            except ValueError:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xbc\xc6\xb6q')
                return None

            if amount <= 0:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xbc\xc6\xb6q')
                return None
            
            if amount > self.m_Remain:
                usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xb3o\xbb\xf2\xa6h\xb1H\xb0\xe2\xa5d')
                return None
            
            price = self.m_PriceEdit.GetText()
            
            try:
                price = int(price)
            except ValueError:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xbb\xf9\xae\xe6')
                return None

            if price < 1000:
                usermacro.PROMPT_MSG('\xbb\xf9\xae\xe6\xa4\xa3\xaf\xe0\xa7C\xa9\xf31000')
                return None
            
            
            def _OK(dlg):
                import netplayer
                netplayer.C2SDiankaSell(dlg.m_Amount, dlg.m_Price, dlg.m_Currency)

            import commondialog
            unit = 100
            if self.m_Currency == 0:
                unit = 10000
            
            price = (price / unit) * unit
            txt = '\xb7\xc7\xb3\xc6\xb1H\xb0\xe2#Y %d #n\xb1i\xb1H\xb0\xe2\xa5d\xa1A#r\xa8C\xb1i #Y%d#n \xa8\xe2\xa1A#r\xbdT\xa9w\xb6\xdc\xa1H' % (amount, price)
            dlg = commondialog.ShowMessageBox(txt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (_OK, None))
            dlg.m_Amount = amount
            dlg.m_Price = price
            dlg.m_iMinPrice = self.m_iMinPrice
            dlg.m_iMaxPrice = self.m_iMaxPrice
            dlg.m_Price = price
            dlg.m_Currency = self.m_Currency
        elif msgid in (9, 12, 13):
            import dlgitembill
            dlgitembill.CSGSAskOpenBuildCard()
        elif msgid <= msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            if self.m_ChargeType == 0:
                self.DoBuy(msgid)
            else:
                self.DoSell(msgid)
        



class CNumberEdit(interface.CEdit):
    
    def __init__(self, oParent, iColor, iFont, x, y, w, h, linecolor = 0, overstriking = False):
        interface.CEdit.__init__(self, oParent, iColor, iFont, x, y, w, h, linecolor, overstriking)
        self.m_IsMoney = True
        self.m_iMin = 0
        self.m_iMax = 20000000

    
    def AddChar(self, char):
        if char.isdigit():
            if char == char:
                pass
            elif char == '0':
                return None
            
            interface.CEdit.AddChar(self, char)
        
        if hasattr(self, 'm_iMin') and hasattr(self, 'm_iMax'):
            iNum = self.GetNumber()
            iNum = max(self.m_iMin, iNum)
            iNum = min(self.m_iMax, iNum)
            self.SetText(str(iNum))
        

    
    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        if hasattr(self, 'm_iMin') and hasattr(self, 'm_iMax'):
            iNum = self.GetNumber()
            iNum = max(self.m_iMin, iNum)
            iNum = min(self.m_iMax, iNum)
            self.SetText(str(iNum))
        

    
    def SetText(self, txt):
        self.Clear()
        if hasattr(self, 'm_iMin') and hasattr(self, 'm_iMax'):
            txt = int(txt)
            txt = max(self.m_iMin, txt)
            txt = min(self.m_iMax, txt)
        
        txt = str(txt)
        for char in txt:
            interface.CEdit.AddChar(self, char)
        
        if hasattr(self, 'm_IsMoney') and self.m_IsMoney:
            import misc
            
            try:
                color = misc.GetCashColor(int(self.GetText()), False)
                for ob, _ in self.m_Data:
                    ob.SetColor(color)

        

    
    def SetRange(self, iMin = 0, iMax = 20000000):
        if iMax == iMax:
            pass
        elif iMax == 0:
            return None
        else:
            self.m_iMin = iMin
            self.m_iMax = iMax



class CCardMoneyDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent, iMode, iEarning, iRespondId):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/itembill/cardmoney.dlg')
        self.m_iMode = iMode
        self.m_iEarning = iEarning
        self.m_iRespondId = iRespondId
        self.m_oMoneyEdit = None
        self.InitWidgets()
        self.InitDlg()

    
    def InitWidgets(self):
        import misc
        import combmacro
        sEarnging = misc.GetCashString(self.m_iEarning)
        self.GetObject('txt_total').SetText(sEarnging)
        self.GetObject('txt_total').SetColor(16777215)
        self.m_oMoneyEdit = combmacro.CEDIT(CNumberEdit, 'txt_getmoney', self, 16777215, interface.FontLT14_1)
        self.m_oMoneyEdit.m_IsMoney = False
        self.m_oMoneyEdit.SetRange(0, self.m_iEarning)
        self.m_oMoneyEdit.SetTextAlign(interface.ALIGN_MIDDLE)
        self.m_oMoneyEdit.Active(True)

    
    def InitDlg(self):
        import netreddot
        netreddot.C2SRemoveRedDot(netreddot.CARDGETMONEY)
        oModel = mdredpoint.GetCRedPointModel()
        oModel.SetRedPointState(netreddot.CARDGETMONEY, False, 0)

    
    def Close(self, bAutoRelease = True):
        import popupmgr
        combdialog.CCombDialog.Close(self, bAutoRelease)
        popupmgr.GetPopupMgr().CloseUI(CCardMoneyDlg, bAutoRelease)

    
    def OnClickOK(self):
        import nethandleui
        iCurMoney = self.GetCurMoney()
        nethandleui.C2SDrawMoney(self.m_iMode, str(iCurMoney), self.m_iRespondId)
        self.OnClickClose()

    
    def SetRespondId(self, iRespondId):
        self.m_iRespondId = iRespondId

    
    def OnClickClose(self):
        self.Close()

    
    def OnMinusLeftUp(self):
        iCurMoney = self.GetCurMoney()
        self.SetCurMoney(iCurMoney - 1000000)

    
    def OnPlusLeftUp(self):
        iCurMoney = self.GetCurMoney()
        self.SetCurMoney(iCurMoney + 1000000)

    
    def OnClickCancel(self):
        self.OnClickClose()

    
    def GetCurMoney(self):
        return self.m_oMoneyEdit.GetNumber()

    
    def SetCurMoney(self, iMoney):
        self.m_oMoneyEdit.SetText(str(iMoney))

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnClickClose()
        elif iMsgID == 2:
            self.OnClickOK()
        elif iMsgID == 3:
            self.OnMinusLeftUp()
        elif iMsgID == 4:
            self.OnPlusLeftUp()
        elif iMsgID == 5:
            import netplayer
            netplayer.C2SOpenRecord(99)
        



def ShowDytPointDlg(remain, phone):
    global g_DytPointDlg
    g_DytPointDlg = CDytPointDlg(remain, phone)


class CDytPointDlg(combdialog.CCombDialog):
    
    class CExgPoint(wrapinterface.CNumberEdit):
        
        def AddChar(self, c):
            wrapinterface.CNumberEdit.AddChar(self, c)
            
            try:
                if int(self.GetText()) > self.m_Max:
                    self.SetText(str(self.m_Max))
            except:
                pass

            self.OnChange()

        
        def DeleteChar(self):
            wrapinterface.CNumberEdit.DeleteChar(self)
            self.OnChange()

        
        def OnChange(self):
            
            try:
                point = int(self.GetText())
                if point % 1000 == 0 and point != 0:
                    self.GetParent().GetObject('btn_Sure').Enable(True)
                else:
                    self.GetParent().GetObject('btn_Sure').Enable(False)
            except:
                pass



    
    class CMobileEdit(interface.CEdit):
        
        def LeftDown(self):
            interface.CEdit.LeftDown(self)
            self.GetParent().GetObject('txt_MobileTip').SetShow(False)


    
    def __init__(self, remain, phoneNumber):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/itembill/dytpoint.dlg')
        interface.Center(self)
        self.m_Remain = remain
        self.m_RemainTxt = combmacro.CTEXT(interface.CTextObject, 'remain', self, str(remain), interface.FontLT14_3, interface.COLOR_12)
        self.m_ExgPoint = combmacro.CEDIT(CDytPointDlg.CExgPoint, 'edt_ChargePoint', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_ExgPoint.m_Max = remain
        self.m_ExgPoint.SetLimit(8)
        self.m_PhoneNum = phoneNumber[:3] + '******' + phoneNumber[9:]
        color = interface.COLOR_105
        show_point = 1000
        if remain < 1000:
            show_point = 0
        
        self.GetObject('btn_Sure').Enable(False)
        self.SetBtnType()
        self.m_Timer = None
        self.SetBtnShow()

    
    def SetBtnShow(self):
        if self.m_Remain < itembilldefines.MIN_POINT_LIMIT:
            pass
        bShowAll = self.m_Remain > 0
        oBtnAll = self.GetObject('btn_all')
        oBtnSure = self.GetObject('btn_Sure')
        oBtnAll.SetShow(bShowAll)
        oBtnSure.SetShow(not bShowAll)
        if bShowAll:
            self.m_ExgPoint.SetText(str(self.m_Remain))
            self.m_ExgPoint.Enable(False)
        

    
    def SetBtnType(self):
        for objname in ('btn_Pay', 'btn_Sure', 'btn_Recode'):
            self.GetObject(objname).m_ParentNotify = True
        

    
    def OnButtonEnter(self, btn):
        txt = {
            1: '\xa5R\xad\xc8\xc2I\xbc\xc6\xa8\xec\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xa4W',
            2: '\xacd\xb8\xdf\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xaa\xba\xc2I\xbc\xc6\xa5R\xad\xc8\xa9M\xa7I\xb4\xab\xb0O\xbf\xfd',
            3: '\xc0\xf2\xa8\xfa\xa7I\xb4\xab\xc2I\xbc\xc6\xae\xc9\xbb\xdd\xadn\xb6\xf1\xbcg\xaa\xba\xc5\xe7\xb5\xfd\xbdX',
            4: '\xbdT\xa9w\xb1N\xc2I\xbc\xc6\xb1q\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xa4W\xa7I\xb4\xab\xa6\xa8\xa5\xbb\xa8\xa4\xa6\xe2\xa4W\xaa\xba\xa5@\xac\xc9\xb0^\xc4m\xab\xd7' }[btn.m_MsgID]
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def CloseWindow(self):
        global g_DytPointDlg
        g_DytPointDlg = None

    
    def OnGetAllPoint(self):
        import netplayer
        netplayer.C2SDytExg2SG(self.m_Remain)
        self.m_ExgPoint.Enable(True)

    
    def OnMessage(self, msgid):
        msgid2log = {
            1: '\xbe\xd4\xb7\xf9\xc2I\xbc\xc6\xac\xdb\xc3\xf6-\xa5R\xad\xc8',
            2: '\xbe\xd4\xb7\xf9\xc2I\xbc\xc6\xac\xdb\xc3\xf6-\xacd\xb8\xdf',
            4: '\xbe\xd4\xb7\xf9\xc2I\xbc\xc6\xac\xdb\xc3\xf6-\xbdT\xa9w\xa7I\xb4\xab' }
        if msgid in msgid2log:
            import clickcounter
            clickcounter.Log(msgid2log[msgid])
        
        if msgid == 5:
            self.CloseWindow()
        elif msgid == 1:
            import gameurl
            import netlogin
            import hero
            account = netlogin.GetCurrAccount()
            web = gameurl.BUY_DYTPOINT_URL % (misc.g_ServerID, hero.g_ID, account)
            net.OpenUrl(web)
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa6b\xbcu\xa5X\xaa\xba\xba\xf4\xad\xb6\xa4W\xb6i\xa6\xe6\xbe\xde\xa7@\xa1C\xa5R\xad\xc8\xa6\xa8\xa5\\\xab\xe1\xa5i\xc0\xf2\xb1o\xac\xdb\xc0\xb3\xaa\xba\xbe\xd4\xb7\xf9\xc2I\xbc\xc6\xa1C')
        elif msgid == 2:
            import netplayer
            netplayer.C2SDytGetConsume()
        elif msgid == 3:
            pass
        elif msgid == 4:
            
            try:
                point = int(self.m_ExgPoint.GetText())
            except ValueError:
                return None

            if point < 1000:
                import usermacro
                usermacro.PROMPT_MSG('\xa8C\xa6\xb8\xa7I\xb4\xab\xb3\xcc\xa4p\xad\xc8\xac\xb01000\xc2I')
                return None
            
            import netplayer
            netplayer.C2SDytExg2SG(point)
        elif msgid == 6:
            self.OnGetAllPoint()
        elif msgid == 7:
            pass
        



class CItemBox(interface.CBoxObject, interface.CBase):
    UNBOUND_SHAPE_LIST = [
        itemdefine.ID_LUCKY_SUMMON_BOOK_REWARD,
        itemdefine.ID_LUCKY_SUMMON_BOOK_ITEM,
        itemdefine.ID_FINAL_SUMMON_BOOK_REWARD,
        itemdefine.ID_FINAL_OR_LUCKY_BOOK_ITEM,
        itemdefine.ID_RANDOM_SUMMON_BOOK_REWARD]
    SHAPE2MASK = {
        9114: ('combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xcb\xab\xbc\xbc\xc4\xdc.igs', 0, 0),
        itemdefine.ID_LUCKY_SUMMON_BOOK_REWARD: ('combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xcc\xd8\xca\xe2.png', -4, -4),
        itemdefine.ID_LUCKY_SUMMON_BOOK_ITEM: ('combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xcc\xd8\xca\xe2.png', -4, -4),
        itemdefine.ID_FINAL_OR_LUCKY_BOOK_ITEM: ('combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xbc\xb8\xc2\xca\xcb\xab\xb7\xdd.png', 0, 30),
        itemdefine.ID_RANDOM_SUMMON_BOOK_REWARD: ('combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xbc\xb8\xc2\xca\xcb\xab\xb7\xdd.png', 0, 30) }
    
    def __init__(self, parent, shape, num):
        interface.CBoxObject.__init__(self, parent, 44, 44, 0, 0)
        self.MessageProcess()
        self.SetQuantity(num)
        self.m_ImgShape = shape
        self.m_Image = dlgdialbox.CreateBoxItem(self, shape)
        self.m_ExtDesc = None
        self.InitMask(shape)

    
    def InitMask(self, iShape):
        if iShape in self.SHAPE2MASK:
            (sPath, iX, iY) = self.SHAPE2MASK[iShape]
            self.m_oMaskImg = combmacro.CIMAGE(self, sPath)
            self.m_oMaskImg.SetPos(iX, iY)
            self.m_oMaskImg.SetZ(10)
        

    
    def SetExtDesc(self, sExt = None):
        self.m_ExtDesc = sExt

    
    def SetQuantity(self, q):
        self.m_Quantity = q
        if q > 1:
            self.m_QuantityText = interface.CTextObject(self, '%3d' % q, interface.FontLT14E_1, 16777215, 0)
            interface.BottomRight(self.m_QuantityText, offsetx = -2)
            self.m_QuantityText.SetZ(10)
        else:
            self.m_QuantityText = None

    
    def Enter(self):
        import dlggetinfo
        import item
        if self.m_ImgShape in self.UNBOUND_SHAPE_LIST:
            iItemKey = None
        else:
            iItemKey = item.MARK_BOUND
        self.m_ItemTips = dlggetinfo.NewItemInfo(self.m_ImgShape, self.m_ImgShape, self.m_ExtDesc, None, iKey = iItemKey)

    
    def Leave(self):
        if getattr(self, 'm_ItemTips', None):
            self.m_ItemTips = None
        

    
    def LeftUp(self):
        import dlgshopsummonview
        if self.m_ImgShape in (itemdefine.ID_LUCKY_SUMMON_BOOK_REWARD, itemdefine.ID_LUCKY_SUMMON_BOOK_ITEM):
            dlgshopsummonview.Show()
        



class CNewItemCheckBox(wrapinterface.CItemCheckBox1):
    
    def __init__(self, parent, shape, amount, text, ext, color, font, x, y, msgid = 0, iconmsgid = 0, bg = 'combdialog/\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb7\xd6\xc0\xe0\xb8\xf16\xd7\xd6.igs', width = 0, height = 0, select_color = None, iBuyID = None):
        wrapinterface.CItemCheckBox1.__init__(self, parent, shape, amount, text, ext, color, font, x, y, msgid, iconmsgid, bg, width, height, select_color)
        self.m_iCanBuyNum = -1
        self.m_oMaskImg = None
        self.m_iBuyID = iBuyID
        self.m_oIconExImg = None
        self.m_iItemType = -1
        self.m_sTips = ''
        self.m_oTips = None
        self.m_oPreviewTips = None
        if shape in itembilldefines.GIFT_PREVIEW_LIST:
            self.CreatePreviewImg(shape)
        
        self.InitMask(shape)

    
    def GetSelectShape(self):
        return self.m_Shape

    
    def InitMask(self, iShape):
        if iShape in itembilldefines.SHAPE2MASK:
            (sPath, iX, iY) = itembilldefines.SHAPE2MASK[iShape]
            self.m_oMaskImg = combmacro.CIMAGE(self, sPath)
            self.m_oMaskImg.SetPos(iX, iY)
            self.m_oMaskImg.SetZ(10)
        

    
    def InitRollAni(self):
        if self.m_Shape in itembilldefines.ROLL_ANI_SHAPE and self.m_iCanBuyNum > 0:
            self.CreateRollAni()
        

    
    def CreateTips(self):
        import style
        if self.m_Shape in itembilldefines.SHOWTIS_ITEMS:
            self.m_oTips = wrapinterface.CImageWithTips(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), itembilldefines.SHOWTIS_ITEMS[self.m_Shape], tipsWide = 320, font = interface.FontLT14_3, alpha = 16777215)
            interface.Center(self.m_oTips, self.GetSize()[0] / 3)
        

    
    def CreatePreviewImg(self, iShape):
        if iShape == itembilldefines.SHENSHOU_GIFT:
            self.m_oPreviewImg = interface.CButton(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd4\xa4\xc0\xc0.igs', 0, 0, 1)
        elif iShape == itembilldefines.XUANJI_GIFT:
            self.m_oPreviewImg = interface.CButton(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd4\xa4\xc0\xc0.igs', 0, 0, 2)
        elif iShape == itembilldefines.SPECIAL_SHOUJUE:
            self.m_oPreviewImg = interface.CButton(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd4\xa4\xc0\xc0.igs', 0, 0, 3)
        
        self.m_oPreviewImg.SetPos(2, 3)
        self.m_oPreviewImg.SetZ(10)
        self.m_oPreviewImg.SetEnterCB(misc.Functor(self.OnEnterCB, iShape))
        self.m_oPreviewImg.SetLeaveCB(misc.Functor(self.OnLeaveCB))

    
    def OnEnterCB(self, iShape):
        if iShape == itembilldefines.SPECIAL_SHOUJUE:
            sText = '\xc2I\xc0\xbb\xa5i\xacd\xac\xdd\xc3~\xb3Z\xa6\xc0'
        elif iShape == itembilldefines.XUANJI_GIFT:
            sText = '\xc2I\xc0\xbb\xa5i\xacd\xac\xdd\xa5\xc8\xbe\xf7\xc2\xa7\xa5]'
        else:
            return None
        self.m_oPreviewTips = wrapinterface.CTextTips(None, -1, sText, interface.FontLT14_3, direct = 1)
        self.m_oPreviewTips.SetOwner(self.m_oPreviewImg)

    
    def OnLeaveCB(self):
        self.m_oPreviewTips = None

    
    def ClosePreviewPart(self):
        self.m_oPreviewPart = None

    
    def SetText(self, text):
        tl = text.split('#r')
        self.m_TextObjects = []
        (txtw, txth) = (0, 0)
        for t in tl:
            tobj = interface.CTextObject(self, t, self.m_Font, self.m_Color, 0)
            (tw, th) = tobj.GetSize()
            txth = txth + th
            self.m_TextObjects.append(tobj)
        
        (sw, sh) = self.GetSize()
        offsetY = None if len(self.m_TextObjects) == 3 else 6
        y = (sh - txth) / 2 - 2
        for tobj in self.m_TextObjects:
            tobj.SetPos(54, y)
            (tw, th) = tobj.GetSize()
            y += th + offsetY
        

    
    def SetStateTxt(self, state_text, color):
        if getattr(self, 'm_TextObjects', []):
            (bx, by) = self.m_TextObjects[0].GetPos()
            (offx, _) = self.m_TextObjects[0].GetSize()
            x = bx + offx
            y = by
        else:
            (sw, sh) = self.GetSize()
            x = 54
            y = sh / 2 - 2
        self.m_StateTxt = interface.CTextObject(self, state_text, self.m_Font, color, 0)
        self.m_StateTxt.SetPos(x, y)

    
    def SetNumLimit(self, numlimit, iDiscount = -1, bShowLimitImg = True):
        if iDiscount == 100:
            return None
        
        self.m_iCanBuyNum = numlimit
        bGrey = False
        if numlimit == 0:
            bGrey = True
            self.m_ImgObject.m_Image.SetGrey()
        
        if numlimit != itembilldefines.UNLIMITED_PURCHASE_NUM:
            self.SetTxt(numlimit)
        
        if bShowLimitImg:
            self.CreateLimitImg(bGrey, iDiscount)
        
        self.InitRollAni()

    
    def CreateIconExImg(self, iNumLimit, iType):
        self.m_oIconExImg = None
        if iType == 0:
            return None
        
        sPath = ''
        if iType == 1:
            sPath = '\xad\xad\xc1\xca'
        
        if not sPath:
            return None
        
        bGray = None if iNumLimit == 0 else False
        if bGray:
            sPath = sPath + '-\xa6\xc7'
        
        sPath = 'combdialog3\\\xd4\xd3\xcd\xbc\\\xcf\xde\xb9\xba\xcd\xbc\xb1\xea\\%s.png' % sPath
        self.m_oIconExImg = combmacro.CIMAGE(self, sPath)
        self.m_oIconExImg.SetZ(20)
        oIconImg = self.m_ImgObject.m_Image
        (iPosX, iPosY) = oIconImg.GetPos()
        self.m_oIconExImg.SetPos(iPosX, iPosY)

    
    def SetTxt(self, txt):
        self.m_LimitNumTxt = interface.CTextObject(self, str(txt), interface.FontLT14E_1, 16777215)
        (w, h) = self.m_LimitNumTxt.GetSize()
        import style
        (iPosx, iPosy) = style.GetIntTuple('dlgitembill1.CNewItemCheckBox', 'm_LimitNumText')
        self.m_LimitNumTxt.SetPos(iPosx - w, iPosy)
        self.m_LimitNumTxt.SetZ(20)

    
    def CreateLimitImg(self, bGrey, iDiscount):
        import combmacro
        import style
        sPath = GetDiscountNum(iDiscount, bGrey)
        if not sPath:
            return None
        
        self.m_LimitImg = combmacro.CIMAGE(self, sPath)
        self.m_LimitImg.SetZ(20)
        (iPosX, iPosY) = style.GetIntTuple('dlgitembill1.CNewItemCheckBox', 'm_LimitImg')
        self.m_LimitImg.SetPos(iPosX, iPosY)

    
    def CreateRollAni(self):
        import style
        oRollAni = interface.CSpriteObject(self, 'item44/select.spr', 'item')
        oRollAni.CreateCommand(1, 'animation')
        (imgx, imgy) = style.GetIntTuple('wrapinterface.CItemCheckBox1', 'data_img_pos')
        oRollAni.SetPos(imgx + 21, imgy + 20)
        self.m_RollAni = oRollAni

    
    def CheckCanBuy(self):
        if self.m_iCanBuyNum == 0:
            iShopType = self.GetParent().GetShopType()
            if iShopType in (7, itembilldefines.SHOPTYPE_NEW_SERVER, itembilldefines.SHOWTYPE_FESTIVALGIFT):
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xad\xad\xc1\xca\xbc\xc6\xb6q'
            elif iShopType == 1 and self.m_Shape in itemdefine.ITEM_SHENGONGFU:
                sText = '\xa4w\xb9F\xa8\xec\xa5\xbb\xa4\xeb\xc1\xca\xb6R\xbc\xc6\xb6q\xa4W\xad\xad'
            elif iShopType == 10:
                sText = '\xa7A\xa4w\xc1\xca\xb6R\xa4F\xa6\xb9\xb9D\xa8\xe3'
            elif iShopType == 1 and self.m_Shape == itembilldefines.YOUHUI_CHANLLENGE:
                sText = '2020\xa6~9\xa4\xeb3\xa4\xe9-9\xa4\xeb17\xa4\xe9\xba\xfb\xc5@\xabe\xa5u\xaf\xe0\xc1\xca\xb6R\xa4@\xa6\xb8'
            else:
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xa5\xbb\xa9P\xad\xad\xc1\xca\xbc\xc6\xb6q'
            import usermacro
            usermacro.PROMPT_MSG(sText)
            return False
        
        return True

    
    def LeftUp(self):
        if not self.CheckCanBuy():
            return None
        
        wrapinterface.CItemCheckBox1.LeftUp(self)

    
    def RightUp(self):
        if not self.CheckCanBuy():
            return None
        
        wrapinterface.CItemCheckBox1.RightUp(self)
        if self.GetSelect():
            self.SetTextColor(self.m_SelectedColor)
        else:
            self.SetTextColor(self.m_Color)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.m_oPreviewPart = CSummonGiftDialog(self.m_iBuyID, self.ClosePreviewPart)
            self.m_oPreviewPart.SetCanBuy(self.m_iCanBuyNum > 0)
        elif iMsgID == 2:
            import dlg2019shoplibao
            dlg2019shoplibao.ShowDlg(0, itembilldefines.XUANJI_GIFT, 0, bPreview = True)
        elif iMsgID == 3:
            import dlgshopsummonview
            dlgshopsummonview.Show()
        



class CItemBillGoods(combdialog.CCombSubWnd):
    MONEY_TYPE = itembilldefines.PAYTYPE_SG
    PAYPARTUI = ('txt_gold', 'txt_total', 'text_total', 'txt_buynum', 'text_buynum', 'hfrm_1', 'hfrm_2', 'hfrm_3', 'noname12', 'noname15', 'noname16')
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/itembill_new/itembill_goods.dlg')
        self.SetZ(1)
        self.m_oMiniBuyPanel = None
        self.initData()
        self.InitTableView()
        self.CreateBuyAmountEdit()
        self.OnBuy(None)
        self.ShowItemType(self.MONEY_TYPE)
        (iX, iY, iW, iH) = self.GetItemBoxLocData()
        self.m_oMark = interface.CClickBox(self, iW, iH, 16711680, 0)
        self.m_oMark.SetPos(iX, iY)
        self.m_oMark.SetShow(False)
        self.m_DelayCreatCommand = None
        self.m_oFlashAni = None
        self.InitSignalCombineCompensation()
        self.m_DingYueList = []
        self.m_DingYueDict = { }
        self.m_DoneDingYueList = []
        self.m_oItemsDict = { }
        self.m_tShowVIPShopType = ()
        self.InitShowVIPShopType()

    
    def InitShowVIPShopType(self):
        if permission.IsOpenGoldShopSimplify():
            self.m_tShowVIPShopType = (itembilldefines.SHOPTYPE_DISCOUNT,)
        else:
            self.m_tShowVIPShopType = (itembilldefines.SHOPTYPE_DISCOUNT, itembilldefines.SHOPTYPE_ROLE)

    
    def InitSignalCombineCompensation(self):
        import mdcombinecompensation
        import combinecompensationdefine
        oModel = mdcombinecompensation.GetCCombineCompensationModel()
        oModel.ssConnect(oModel.SS_DiscountTimeOut, self.StopCombineCompensationTips)
        oModel.ssConnect(oModel.SS_DiscountActivited, self.CreateDiscountShopTips)
        oModel.RequestCurStateDetail(combinecompensationdefine.PREDEFINE_DISCOUNT_SHOP)

    
    def StopCombineCompensationTips(self):
        if self.m_oDiscountShopTimer and not self.m_oDiscountShopTimer.IsReleased():
            self.m_oDiscountShopTimer.Release()
        
        self.m_oDiscountShopTimer = None
        self.SetShowObject('text_tips_combine', False)
        self.SetShowObject('tips_combine', False)

    
    def GetIdx(self):
        return self.m_SelectedItem + self.m_CurrentPage

    
    def GetItemBoxLocData(self):
        return self.GetLocData('box_goods')

    
    def GetTableView(self):
        return self.GetObject('box_goods')

    
    def InitTableView(self):
        oTable = self.GetTableView()
        oTable.SetDelegateNumberOfCells(self.TbDelegateNumberOfCells)
        oTable.SetDelegateNewCellOfIndex(misc.Functor(self.TbDelegateNewCellOfIndex))
        oTable.SetDelegateUpdateCellOfIndex(misc.Functor(self.TbDelegateUpdateCellOfIndex))
        oTable.SetShowRowLine(False)

    
    def TbDelegateNumberOfCells(self):
        return len(self.m_oSourceList)

    
    def TbDelegateNewCellOfIndex(self, oContainer, iIdx):
        import misc
        oItem = dlgitembill1_item.CBillItemDlg(oContainer, interface.COLOR_354, misc.WeakRef(self))
        oItem.SetEnterCB(self.OnItemEnter, oItem)
        oItem.SetLeaveCB(self.OnItemLeave, oItem)
        return oItem

    
    def TbDelegateUpdateCellOfIndex(self, oCell, iIdx, bReused):
        (oItemData, iCount) = self.m_oSourceList[iIdx]
        oCell.Reset()
        if not oItemData:
            oCell.Enable(False)
            oCell.SetTextShow(False)
            return None
        
        (iShape, iPayType, sTxt, iAmount, iBuyTuple) = oItemData
        oCell.SetItem(iShape, sTxt, iBuyTuple, iPayType, iIdx, iCount)
        if self.m_SelectedItem is not None and self.m_SelectedItem == oCell.GetIndex():
            oCell.SetCheck(True)
        else:
            oCell.SetCheck(False)
        self.SetDingYueData(iShape, sTxt, iBuyTuple, iIdx)
        self.m_oItemsDict[iIdx] = oCell

    
    def initData(self):
        self.m_oDiscountShopTimer = None
        self.m_SelectedItem = None
        self.m_CurrentPage = None
        self.m_ShopType = 0
        self.m_SelectedShape = 0
        self.m_DefaultItemID = 0

    
    def SetShopType(self, iShopType):
        self.m_ShopType = iShopType
        oTipTmp = None().GetObject('text_dft_002')
        self.SetShowObject('btn_refresh', False)
        if oTipTmp:
            oTipTmp.SetShow(iShopType == 7)
            (iX, iY) = self.GetObject('loc_norebtn').GetPos()
            self.GetObject('btn_buy').SetPos(iX, iY)
        
        self.CheckShowDiscountShopTips()
        self.RefreshEndTime(iShopType)
        self.SetShowObject('tips_num', False)

    
    def RefreshEndTime(self, iShopType):
        import time
        oEndTimeObj = self.GetObject('text_xinfu_time')
        if oEndTimeObj:
            if iShopType in (itembilldefines.SHOPTYPE_NEW_SERVER, itembilldefines.SHOWTYPE_FESTIVALGIFT, itembilldefines.SHOWTYPE_SECRET):
                iEndTime = GetPageExtData(iShopType, 'iEndTime', None)
                if iEndTime:
                    oTime = time.localtime(iEndTime)
                    iYear = oTime.tm_year
                    iMon = oTime.tm_mon
                    iDay = oTime.tm_mday
                    iHour = oTime.tm_hour
                    if iHour == 0:
                        iEndTime -= 86400
                        oTime = time.localtime(iEndTime)
                        iYear = oTime.tm_year
                        iMon = oTime.tm_mon
                        iDay = oTime.tm_mday
                        iHour = 24
                    
                    oEndTimeObj.ReplaceText({
                        '$y': str(iYear),
                        '$m': str(iMon),
                        '$d': str(iDay),
                        '$h': str(iHour) })
                    oEndTimeObj.SetShow(True)
                else:
                    oEndTimeObj.SetShow(False)
            else:
                oEndTimeObj.SetShow(False)
        

    
    def CheckShowDiscountShopTips(self):
        import netstate
        import netstatedefine
        import mdcombinecompensation
        if self.GetShopType() == itembilldefines.SHOPTYPE_DISCOUNT and netstate.GetState(netstatedefine.ID_COMBINE_COMPENSATION_STATE):
            if not mdcombinecompensation.GetCCombineCompensationModel().IsDiscountTimeOut():
                self.SetShowObject('tips_combine', True)
                self.SetShowObject('text_tips_combine', True)
            
        else:
            self.SetShowObject('tips_combine', False)
            self.SetShowObject('text_tips_combine', False)

    
    def CreateDiscountShopTips(self):
        if self.GetShopType() == itembilldefines.SHOPTYPE_DISCOUNT:
            self.InitDiscountTimer()
            self.SetShowObject('tips_combine', True)
            self.SetShowObject('text_tips_combine', True)
        

    
    def InitDiscountTimer(self):
        import timer
        import misc
        if self.m_oDiscountShopTimer and not self.m_oDiscountShopTimer.IsReleased():
            self.m_oDiscountShopTimer.Release()
        
        self.SetDiscountTips()
        self.m_oDiscountShopTimer = timer.Timer(60, misc.Functor(self.SetDiscountTips), -1, self)

    
    def SetDiscountTips(self):
        import netstate
        import netstatedefine
        oTips = self.GetObject('tips_combine')
        oState = netstate.GetState(netstatedefine.ID_COMBINE_COMPENSATION_STATE)
        bStop = False
        if oState:
            iTime = oState.GetDiscountShopRemainTime()
            if iTime >= 0:
                oTips.SetTips('\xa6X\xaaA\xc0u\xb4f\xb3\xd1\xbel\xae\xc9\xb6\xa1\xa1G%s' % misc.Int2TimeStr(iTime))
            else:
                bStop = True
        else:
            bStop = True
        if bStop:
            self.StopCombineCompensationTips()
        

    
    def SetDefaultItemId(self, iDefaultItemId):
        self.m_DefaultItemID = iDefaultItemId

    
    def GetShopType(self):
        return self.m_ShopType

    
    def OnGoldCallback(self):
        if self.m_CurrentPage is None or self.m_SelectedItem is None:
            return None
        
        idx = self.GetItemByPos(self.GetIdx()).GetServerIndex()
        iMoney = self.GetOwnerMoney(idx)
        iPrice = self.GetTotalPrice(idx)
        iSinglePrice = self.m_BuyList[idx][2]
        if iMoney < iPrice:
            self.m_BuyAmountEdit.SetText(str(max(1, iMoney / iSinglePrice)))
        
        self.DrawTotalPrice(idx)

    
    def CreateBuyAmountEdit(self):
        import wrapedit
        color = interface.COLOR_5
        self.m_BuyAmountEdit = combmacro.CEDIT(wrapedit.CLimitNumberEdit, 'loc_num', self, color, interface.FontLT14_3, interface.COLOR_5)
        self.m_BuyAmountEdit.SetLimit(5)
        self.m_BuyAmountEdit.Active(True)

    
    def OnLimitEditChange(self, editObj):
        if self.m_SelectedItem is None:
            self.m_BuyTotalPrice = None
            return None
        
        idx = self.GetItemByPos(self.GetIdx()).GetServerIndex()
        largeBuyNum = self.GetLargeBuyNum(idx)
        if hasattr(self.m_BuyAmountEdit, 'm_MaxNum') and self.m_BuyAmountEdit.m_MaxNum is not None:
            maxLimit = min(self.m_BuyAmountEdit.m_MaxNum, largeBuyNum)
        else:
            maxLimit = largeBuyNum
        if maxLimit <= 0:
            maxLimit = 1
        
        
        try:
            self.m_BuyAmount = int(self.m_BuyAmountEdit.GetText())
            if self.m_BuyAmount > maxLimit:
                self.m_BuyAmountEdit.SetText(str(maxLimit))
        except:
            self.m_BuyAmount = 0

        self.DrawTotalPrice(idx)

    
    def SetBuyList(self, buylist, page = 0, iRealPage = 0):
        if self.m_ShopType != iRealPage:
            return None
        
        self.ShowItemType(self.MONEY_TYPE)
        if self.m_ShopType in self.m_tShowVIPShopType:
            buylist.insert(0, (31215, 1, 150, 0, ''))
        
        import dlggetinfo
        dlggetinfo.ClearItemInfo(4)
        self.m_BuyList = buylist
        self.m_CurrentPage = 0
        self.m_SelectedItem = None
        self.m_oSourceList = []
        self.m_TotalPage = len(buylist)
        self.SetActivePage(page)
        self.SelectDefaultItem()
        self.OnCloseMiniBuyPanel()

    
    def SelectDefaultItem(self):
        if not self.m_DefaultItemID:
            self.AutoSelectLastItem()
            return None
        
        if not self.SelectDefaultItemInCurPage():
            self.OnMouseWheelDown(100, False)
            if not self.SelectDefaultItemInCurPage():
                LOG('\xb0\xd3\xab\xb0\xa7\xe4\xa4\xa3\xa8\xec\xbb\xdd\xa8D\xaa\xab', self.m_DefaultItemID)
            
        

    
    def SelectDefaultItemInCurPage(self):
        for iIdx, oItem in self.m_oItemsDict.iteritems():
            if oItem.GetShape() == self.m_DefaultItemID:
                self.SelectItem(iIdx, oItem.GetIndex())
                return True
                continue
        
        return False

    
    def AutoSelectLastItem(self):
        dLastSelectData = GetLastSelectData()
        iServerIdx = dLastSelectData.get('iPos', -1)
        iAmount = dLastSelectData.get('iAmount', -1)
        iPage = dLastSelectData.get('iPage', -1)
        iShape = dLastSelectData.get('iShape', -1)
        iPos = self.GetItemPosByServerIdx(iServerIdx)
        if iPos == -1:
            return None
        
        iPos = iPos - iPage
        self.OnMouseWheelDown(-1, bAutoShowMark = False)
        if iPos not in self.m_oItemsDict:
            return None
        
        (oItemData, iCount) = self.m_oSourceList[iPos]
        if oItemData and iShape != oItemData[0]:
            return None
        
        self.SelectItem(iPos)
        iCanBuyAmount = self.GetItemCanBuyAmount(iPos)
        if iCanBuyAmount > 0:
            self.m_BuyAmountEdit.SetText(str(iAmount))
        else:
            self.m_BuyAmountEdit.SetText('0')
        self.m_BuyAmountEdit.SetSelect(0, 999)

    
    def OnMouseWheelDown(self, p, bAutoShowMark = True):
        oTable = self.GetTableView()
        oTable.Reload(p)
        self.SetDelayShow(bAutoShowMark)

    
    def OnMouseWheelUp(self, p, bAutoShowMark = True):
        oTable = self.GetTableView()
        oTable.Reload(p)
        self.SetDelayShow(bAutoShowMark)

    
    def SetDelayShow(self, bAutoShowMark = True):
        '''\xa9\xb5\xae\xc920\xb4V\xc5\xe3\xa5\xdctips'''
        global g_tips
        
        def ShowTip(obj):
            obj.m_oMark.SetShow(False)

        if bAutoShowMark:
            self.m_oMark.SetShow(True)
        
        g_tips = None
        if self.m_DelayCreatCommand:
            self.m_DelayCreatCommand.Release()
            self.m_DelayCreatCommand = None
        
        self.m_DelayCreatCommand = self.CreatePyCommand(20, ShowTip)

    
    def BarChange(self, p):
        self.SetActivePage(p * 2)

    
    def SetActivePage(self, page):
        if page >= self.m_TotalPage or page < 0:
            return None
        
        self.m_DingYueList = []
        self.m_DingYueDict = { }
        self.OnBuy(None)
        self.m_CurrentPage = page
        self.SetDataSource(self.m_BuyList)

    
    def SetDataSource(self, oBuyList):
        tSourceList = []
        self.m_oItemsDict = { }
        if permission.IsOpenGoldShopSimplify() and self.m_ShopType == itembilldefines.SHOPTYPE_DISCOUNT:
            tSoldOutList = []
            iCount = 0
            for iBuyTuple in oBuyList:
                tSource = [
                    self.GetItemData(iBuyTuple),
                    iCount]
                if tSource[0][4][1] != 0:
                    tSourceList.append(tSource)
                else:
                    tSoldOutList.append(tSource)
                iCount += 1
            
            tSourceList.extend(tSoldOutList)
        else:
            iCount = 0
            for iBuyTuple in oBuyList:
                tSourceList.append([
                    self.GetItemData(iBuyTuple),
                    iCount])
                iCount += 1
            
        oTable = self.GetTableView()
        self.m_oSourceList = tSourceList
        oTable.Reload()

    
    def SetDingYueData(self, iShape, sTxt, iBuyTuple, iCount):
        idx = iCount + self.m_CurrentPage
        if self.m_ShopType == 6:
            if iShape not in self.m_DingYueList:
                self.m_DingYueList.append(iShape)
                self.m_DingYueDict[iShape] = [
                    sTxt,
                    iBuyTuple[4],
                    idx]
            
        

    
    def GetItemByPos(self, iPos):
        return self.m_oItemsDict.get(iPos, None)

    
    def GetItemPosByServerIdx(self, iServerIdx):
        for oItem in self.m_oItemsDict.itervalues():
            if iServerIdx == oItem.GetServerIndex():
                return oItem.GetIndex()
                continue
        
        return -1

    
    def GetItemByServerIdx(self, iServerIdx):
        for oItem in self.m_oItemsDict.itervalues():
            if iServerIdx == oItem.GetServerIndex():
                return oItem
                continue
        

    
    def GetItemData(self, iBuyTuple):
        '''
\t\t:return:(\xaa\xab\xab~shape, \xb3f\xb9\xf4\xc3\xfe\xab\xac, \xa6W\xa6r+\xbb\xf9\xae\xe6\xa6r\xb2\xc5\xa6\xea, \xad\xd3\xbc\xc6)
\t\t'''
        import itemdata
        iShape = iBuyTuple[0]
        (sName, explain) = itemdata.GetData(iShape)
        if iShape in itembilldefines.RMB_ITEM_DICT:
            iPayType = itembilldefines.PAYTYPE_RMB
        elif self.m_ShopType == itembilldefines.SHOPTYPE_TREASURE:
            iPayType = itembilldefines.PAYTYPE_CASH
        else:
            iPayType = itembilldefines.PAYTYPE_SG
        if self.m_ShopType == 7 and iBuyTuple[6]:
            iPayType = iBuyTuple[6]
        
        if iPayType == itembilldefines.PAYTYPE_RMB:
            sTxt = sName + '#r%s\xa4\xb8' % iBuyTuple[2]
        elif iPayType == itembilldefines.PAYTYPE_CASH:
            sTxt = sName + '#r\xb2{\xaa\xf7\xa1G%s' % misc.GetCashString(iBuyTuple[2])
        elif iPayType == itembilldefines.PAYTYPE_MXB:
            sTxt = sName + '#r\xb9\xda\xb7Q\xb9\xf4\xa1G%d' % iBuyTuple[2]
        else:
            sTxt = sName + '#r\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa1G%d' % iBuyTuple[2]
        sNumber = self.GetCanBuyText(self.m_ShopType, iShape, iBuyTuple[1])
        sTxt += sNumber
        return (iShape, iPayType, sTxt, iBuyTuple[2], iBuyTuple)

    
    def GetCanBuyText(self, iType, shape, iNum):
        if shape in (31215, 31220):
            return ''
        
        if iType in ():
            if iNum != 65535:
                return '#r\xa5\xbb\xa6\xb8\xa5i\xb6R\xbc\xc6\xb6q:%d' % iNum
            elif iNum == 0:
                return '#r\xa4w\xb0\xe2\xa5\xfa'
            
        
        return ''

    
    def OnBuy(self, idx, inc = 1):
        if idx is None:
            self.m_BuyTarget = None
            self.m_BuyAmount = 0
            self.m_SelectedItem = None
            self.m_iSelectedServerIdx = None
            self.OnCloseMiniBuyPanel()
        elif idx != self.m_BuyTarget:
            self.m_BuyTarget = idx
            self.m_BuyAmount = 1
        elif idx == 0 and self.m_ShopType in self.m_tShowVIPShopType:
            inc = 0
        
        self.m_BuyAmount += inc
        if self.m_BuyAmount < 1:
            self.m_BuyAmount = 1
        
        if self.m_BuyList[idx][3] != 100 and self.m_BuyAmount > self.m_BuyList[idx][1]:
            self.m_BuyAmount = self.m_BuyList[idx][1]
        
        self.m_BuyAmountEdit.Clear()
        self.m_BuyAmountEdit.SetText(str(self.m_BuyAmount))
        self.SetBuyAmountEditSelect()

    
    def SetBuyAmountEditSelect(self):
        if not self.m_oMiniBuyPanel:
            self.m_BuyAmountEdit.Active(True)
            self.m_BuyAmountEdit.SetSelect(0, 999)
        else:
            self.OnMiniBuyEditSelect()

    
    def OnItemEnter(self, icb):
        global g_tips
        import dlggetinfo
        iIdx = icb.GetIndex()
        iKey = self.GetItemKeyByShape(icb.m_Shape)
        g_tips = dlggetinfo.NewItemInfo(iIdx, icb.m_Shape, icb.m_sTips, None, iKey)

    
    def OnItemLeave(self, icb):
        global g_tips
        g_tips = None

    
    def GetOwnerMoney(self, iIndex):
        import hero
        oItem = self.GetItemByServerIdx(iIndex)
        if oItem:
            iPayType = oItem.GetPayType()
            if iPayType == itembilldefines.PAYTYPE_RMB:
                return 9999
            
            return [
                hero.g_Prop.m_Cash,
                hero.g_Prop.m_FightCash,
                hero.g_Prop.m_Gold,
                hero.g_Prop.m_ShenWuBi][iPayType - 1]
        
        return 0

    
    def GetLargeBuyNum(self, idx):
        price = self.m_BuyList[idx][2]
        ownermoney = self.GetOwnerMoney(idx)
        return ownermoney / price

    
    def GetTotalPrice(self, idx):
        if idx is not None:
            total = self.m_BuyList[idx][2] * self.m_BuyAmount
        else:
            total = 0
        return total

    
    def GetItemKeyByShape(self, iShape):
        import item
        if iShape in (itemdefine.ID_ITEM_VIP, itemdefine.ID_RANDOM_SUMMON_BOOK_REWARD, itemdefine.ID_RANDOM_BAZHENTU):
            return 0
        elif iShape in (itemdefine.ID_JINGPING_SUMMON_BOOK_ITEM,):
            return item.MARK_JINGPIN
        else:
            return item.MARK_BOUND

    
    def DrawTotalPrice(self, idx):
        self.m_BuyTotalPrice = None
        oItem = self.GetItemByServerIdx(idx)
        if oItem:
            iPayType = oItem.GetPayType()
            if iPayType == itembilldefines.PAYTYPE_RMB:
                return None
            
        
        iColor = interface.COLOR_5
        iOwnerMoney = self.GetOwnerMoney(idx)
        iTotalPrice = self.GetTotalPrice(idx)
        if iOwnerMoney < iTotalPrice:
            iColor = interface.COLOR_218
        
        sTotalPriceText = misc.GetCashString(iTotalPrice)
        self.m_BuyTotalPrice = combmacro.CTEXT(interface.CShadowText, 'loc_total', self, sTotalPriceText, interface.FontLT14_3, iColor)
        if self.m_oMiniBuyPanel:
            self.m_oMiniBuyPanel.SetTotalPrice(sTotalPriceText)
            self.m_oMiniBuyPanel.SetChangeFlag(True)
            self.m_oMiniBuyPanel.SetTotalNum(self.m_BuyAmount)
            self.m_oMiniBuyPanel.SetChangeFlag(False)
        

    
    def OnOneRmbSure(self):
        import hero
        import mdpayrmbpurchase
        import dlgpayrmbpurchase
        mdpayrmbpurchase.GetModel().SetBaseInfo(hero.GetHeroID(), itembilldefines.RMB_ITEM_DICT[self.m_SelectedShape], 1)
        dlgpayrmbpurchase.Show()

    
    def DoBuy(self):
        import usermacro
        import hero
        import dlgnpc
        if self.m_BuyTarget is None:
            return None
        
        
        try:
            amount = int(self.m_BuyAmountEdit.GetText())
        except:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xba\xa7I\xb4\xab\xbc\xc6\xb6q')
            return None

        if amount <= 0:
            usermacro.PROMPT_MSG('\xc1\xca\xb6R\xbc\xc6\xb6q\xa6\xdc\xa4\xd6\xac\xb01')
            return None
        
        bBuyRMBItem = self.m_SelectedShape in itembilldefines.RMB_ITEM_DICT
        if bBuyRMBItem:
            self.OnOneRmbSure()
        
        iLimitAmount = self.m_BuyAmountEdit.GetMaxNum()
        if amount > iLimitAmount or iLimitAmount == 0:
            if self.m_ShopType == 7:
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xad\xad\xc1\xca\xbc\xc6\xb6q'
            elif self.m_ShopType == 1 and self.m_SelectedShape in itemdefine.ITEM_SHENGONGFU:
                sText = '\xa4w\xb9F\xa8\xec\xa5\xbb\xa4\xeb\xc1\xca\xb6R\xbc\xc6\xb6q\xa4W\xad\xad'
            else:
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xa5\xbb\xa9P\xad\xad\xc1\xca\xbc\xc6\xb6q'
            usermacro.PROMPT_MSG(sText)
            return None
        
        SetLastSelectData(self.m_BuyTarget, amount, self.m_CurrentPage, self.m_SelectedShape)
        if self.m_BuyTarget == 0 and self.m_ShopType in self.m_tShowVIPShopType:
            self.GetParent().BuyVip(self.m_ShopType)
            return None
        
        if self.m_ShopType in self.m_tShowVIPShopType:
            buytarget = self.m_BuyTarget - 1
        else:
            buytarget = self.m_BuyTarget
        if not bBuyRMBItem and self.IsBuyItem(self.m_SelectedShape, buytarget, amount):
            C2SBuyCommonIB(buytarget, amount)
        

    
    def IsBuyItem(self, iShape, iBuyTarget, iAmount):
        import item
        import itemdefine
        import dlgnpc
        import dialoguecommondata
        if iAmount <= 0:
            return True
        
        if iShape == itemdefine.ID_TIAOZHAN_YUEKA:
            if item.GetItemNum(itemdefine.ID_TIAOZHAN_YUEKA):
                
                def OnCB(oCB, iMsgId):
                    if iMsgId == 1:
                        if oCB:
                            pass
                        oCB()
                    

                sMsg = dialoguecommondata.GetDialogue('shop', 1001)
                dlgnpc.ShowClientDlg(sMsg, '', misc.Functor(OnCB, misc.Functor(C2SBuyCommonIB, iBuyTarget, iAmount)))
                return False
            
        
        return True

    
    def GetItemSelectData(self, iPos):
        (tItemData, iServerIndex) = self.m_oSourceList[iPos]
        dItemData = { }
        if tItemData:
            (iShape, iPayType, sTxt, iAmount, iBuyTuple) = tItemData
            dItemData = {
                'iServerIndex': iServerIndex,
                'iIndex': iPos,
                'iShape': iShape,
                'iPayType': iPayType,
                'sTxt': sTxt,
                'iAmount': iAmount,
                'iBuyTuple': iBuyTuple }
        
        return dItemData

    
    def GetItemCanBuyAmount(self, iPos):
        (tItemData, _) = self.m_oSourceList[iPos]
        if tItemData:
            (iShape, iPayType, sTxt, iAmount, tBuyTuple) = tItemData
            return tBuyTuple[1]
        
        return 0

    
    def SelectItem(self, pos, bRightUp = False):
        oItem = dlgitembill1_item.CBillItemSelectData()
        dItemData = self.GetItemSelectData(pos)
        iBuyTuple = dItemData.get('iBuyTuple')
        if iBuyTuple:
            oItem.SetItem(dItemData, iBuyTuple)
        
        self.OnItemLeave(pos)
        if oItem and oItem.GetCanBuy():
            if bRightUp and oItem.GetPayType() == itembilldefines.PAYTYPE_RMB:
                return None
            
            if bRightUp:
                if not self.m_oMiniBuyPanel:
                    bResetPos = True
                    self.m_oMiniBuyPanel = CMiniBuyDialog(self)
                else:
                    bResetPos = False
                self.m_oMiniBuyPanel.RefreshItemInfo(dItemData, bResetPos)
                iChange = 0
            elif self.m_SelectedItem != pos:
                self.OnCloseMiniBuyPanel()
            
            iChange = 1
            iCurIdx = self.m_SelectedItem
            tUpdate = (iCurIdx, pos)
            self.m_SelectedItem = pos
            self.m_iSelectedServerIdx = oItem.GetServerIndex()
            self.GetTableView().Reload(-1, tUpdate)
            if oItem.GetPayType() == itembilldefines.PAYTYPE_RMB:
                self.ShowItemType(oItem.GetPayType(), sBtnText = '%d\xa4\xb8' % self.m_BuyList[self.m_iSelectedServerIdx][2], iShape = oItem.GetShape())
            else:
                self.ShowItemType(oItem.GetPayType())
            if self.m_ShopType == itembilldefines.SHOWTYPE_SECRET:
                pass
            bNotLimitBuy = oItem.GetMaxNum() == itembilldefines.UNLIMITED_PURCHASE_NUM
            if bNotLimitBuy:
                self.m_BuyAmountEdit.SetMaxNum(itembilldefines.DEFAULT_MAX_NUM)
            else:
                self.m_BuyAmountEdit.SetMaxNum(oItem.GetMaxNum())
            self.OnBuy(oItem.GetServerIndex(), inc = iChange)
            self.m_SelectedShape = oItem.GetShape()
            if bRightUp:
                if self.m_ShopType == 1 or self.m_ShopType == 7:
                    self.OnMiniBuyMax(bNotLimitBuy)
                    if self.m_oMiniBuyPanel:
                        self.m_oMiniBuyPanel.SetBuyAmountEditSelect()
                    
                
            self.SetAccumulationTips()
        

    
    def ShowItemType(self, itype, sBtnText = '\xc1\xca \xb6R', iShape = 0):
        import hero
        self.m_ShowObjects = []
        hero.ReleaseDlgItem('ItemBillDlg', (('m_Cash',), ('m_FightCash',), ('m_Gold',), ('m_ShenWuBi',)))
        if itype == itembilldefines.PAYTYPE_RMB:
            for sUIName in self.PAYPARTUI:
                self.SetShowObject(sUIName, False)
            
            self.SetShowObject('rtxt_xinfu_tips', True)
            oTipsText = self.GetObject('rtxt_xinfu_tips')
            if oTipsText:
                oTipsText.SetShow(True)
                oTipsText.ReplaceText({
                    '$rmb': sBtnText })
                if iShape == 73642:
                    oTipsText.ReplaceText({
                        '$Quota': '#r\xa5\xbb\xc2\xa7\xa5]' })
                else:
                    oTipsText.ReplaceText({
                        '$Quota': '\xa1A\xad\xad\xc1\xca1\xa6\xb8#r\xa5\xbb\xc2\xa7\xa5]' })
            
            self.m_BuyAmountEdit.SetShow(False)
            self.GetObject('btn_buy').SetText(sBtnText + '\xc1\xca\xb6R')
        else:
            for sUIName in self.PAYPARTUI:
                self.SetShowObject(sUIName, True)
            
            self.SetShowObject('rtxt_xinfu_tips', False)
            self.GetObject('btn_buy').SetText('\xc1\xca \xb6R')
            self.m_BuyAmountEdit.SetShow(True)
            self.SetImage(itype)
            color = interface.COLOR_5
            name = [
                'm_Cash',
                'm_FightCash',
                'm_Gold',
                'm_ShenWuBi'][itype - 1]
            if name in ('m_Cash', 'm_ShenWuBi'):
                cls = CCashShadowText
            else:
                cls = interface.CShadowText
            hero.CreateCombDlgItem('loc_gold', 'ItemBillDlg', ((name, 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, cls, interface.FontLT14_3, color),), self)
            hero.AddRefreshCallback('dlgitembill1_gold', (('m_Gold',),), self.OnGoldCallback)

    
    def SetImage(self, itype):
        import style
        import combmacro
        sMengXiangBiImg = 'combdialog3/\xd4\xd3\xcd\xbc/\xc3\xce\xcf\xeb\xb1\xd2/mengxiangbixiao.png'
        if interface.IsStyle1() or interface.IsStyle2():
            sMengXiangBiImg = 'combdialog/\xd4\xd3\xcd\xbc/\xbd\xf0\xc7\xae\xcd\xbc\xb1\xea.igs'
        
        path = [
            'combdialog/\xd4\xd3\xcd\xbc/\xcf\xd6\xbd\xf0\xcd\xbc\xb1\xea.igs',
            'combdialog/\xd4\xd3\xcd\xbc/\xb5\xd6\xd3\xc3\xbd\xf0\xcd\xbc\xb1\xea.igs',
            'combdialog/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xb9\xb1\xcf\xd7\xb6\xc8\xcd\xbc\xb1\xea.igs',
            sMengXiangBiImg][itype - 1]
        sName = 'imgitype%d' % (itype - 1)
        (offsetx, offsety) = style.GetIntTuple('dialog/itembill/itembill.dlg', sName)
        for i in xrange(2):
            (x, y) = self.GetObject('showimg%d' % i).GetPos()
            img = combmacro.CIMAGE(self.GetObject('showimg%d' % i), style.GetPath(path))
            img.SetPos(offsetx, offsety)
            self.m_ShowObjects.append(img)
        
        sText = [
            '\xb7\xed\xabe\xb2{\xaa\xf7',
            '\xa9\xe8\xa5\xce\xaa\xf7',
            '\xa5@\xac\xc9\xb0^\xc4m',
            '\xb9\xda\xb7Q\xb9\xf4'][itype - 1]
        self.GetObject('txt_gold').SetText(sText)
        if self.m_oMiniBuyPanel:
            pass
        self.m_oMiniBuyPanel.SetBuyType(offsetx, offsety, path)

    
    def SetAccumulationTips(self):
        if self.m_ShopType in (1, 6):
            bShow = self.m_SelectedShape in g_dAccumulation.get(self.m_ShopType, [])
        else:
            bShow = False
        self.GetObject('tips_num').SetShow(bShow)
        if self.m_oMiniBuyPanel:
            self.m_oMiniBuyPanel.SetAccumulationTipsShow(bShow)
        

    
    def OnCloseMiniBuyPanel(self):
        self.m_oMiniBuyPanel = None

    
    def OnMiniBuyChange(self, iChange):
        if self.m_BuyTarget is not None:
            self.OnBuy(self.m_BuyTarget, inc = iChange)
        

    
    def OnMiniBuyNum(self, sNum):
        self.m_BuyAmountEdit.SetText(sNum)

    
    def OnMiniBuyMax(self, bNotLimitBuy = False):
        iSelectIndex = self.GetItemByPos(self.GetIdx()).GetServerIndex()
        iMyMax = max(self.GetLargeBuyNum(iSelectIndex), 1)
        if bNotLimitBuy:
            iMax = 1
        elif hasattr(self.m_BuyAmountEdit, 'm_MaxNum') and self.m_BuyAmountEdit.m_MaxNum is not None:
            iMax = min(self.m_BuyAmountEdit.m_MaxNum, iMyMax)
        else:
            iMax = iMyMax
        self.m_BuyAmountEdit.SetText(str(iMax))

    
    def OnMiniBuyEditSelect(self):
        if self.m_oMiniBuyPanel:
            self.m_oMiniBuyPanel.SetBuyAmountEditSelect()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID in (6, 7):
            iPage = None if iMsgID == 7 else self.m_CurrentPage - 1
            self.SetActivePage(iPage)
        elif iMsgID == 9:
            self.DoBuy()
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 150:
            self.SelectItem(iMsgID - 100)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < interface.RIGHT_BUTTON_MESSAGE + 500:
            self.SelectItem(iMsgID - interface.RIGHT_BUTTON_MESSAGE - 100, bRightUp = True)
        



class CMiniBuyDialog(combdialog.CCombDialog):
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/itembill/itembill_new/itembill_minibuy.dlg')
        self.m_oItemCheckBox = None
        self.m_oMoneyImage = None
        self.m_oBuyEdit = None
        self.m_ChangeFlag = False
        self.m_dItemData = { }
        self.SetAccumulationTipsShow(False)
        self.CreateBuyAmountEdit()

    
    def CreateBuyAmountEdit(self):
        import wrapedit
        self.m_oBuyEdit = combmacro.CEDIT(wrapedit.CLimitNumberEdit, 'loc_num', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oBuyEdit.SetLimit(5)
        self.m_oBuyEdit.Active(True)

    
    def SetBuyAmountEditSelect(self):
        self.m_oBuyEdit.SetSelect(0, 999)

    
    def SetTotalPrice(self, sTotalPrice):
        self.GetObject('txt_price').SetText(sTotalPrice)

    
    def SetTotalNum(self, iTotalNum):
        self.m_oBuyEdit.SetText(str(iTotalNum))

    
    def SetChangeFlag(self, bFlag):
        self.m_ChangeFlag = bFlag

    
    def SetBuyType(self, x, y, path):
        import style
        self.m_oMoneyImage = combmacro.CIMAGE(self.GetObject('loc_MoneyImg'), style.GetPath(path))
        self.m_oMoneyImage.SetPos(x, y)

    
    def SetAccumulationTipsShow(self, bShow):
        self.SetShowObject('tips_num', bShow)

    
    def RefreshItemInfo(self, dItemData, bResetPos):
        self.m_dItemData = dItemData
        iShape = dItemData.get('iShape', 0)
        iNum = dItemData.get('iBuyTuple', (0, 0))[1]
        sText = dItemData.get('sTxt', '')
        oBG = self.GetObject('box_item')
        oBG.SetShow(False)
        sBGFile = oBG.m_FileName
        (x, y) = oBG.GetPos()
        (w, h) = oBG.GetSize()
        if iNum == itembilldefines.UNLIMITED_PURCHASE_NUM:
            iNum = -1
        
        self.m_oItemCheckBox = CMiniBuyItemCheckBox(self, iShape, iNum, sText, None, interface.COLOR_1, interface.FontLT14_3, x, y, bg = sBGFile, width = w, height = h)
        if bResetPos:
            self.ResetPos()
        

    
    def ResetPos(self):
        '''
\t\t\xb8\xd3\xac\xc9\xad\xb1\xbcu\xa5X\xae\xc9\xac\xc9\xad\xb1btn_buy\xa5\xbf\xa6n\xb8m\xa9\xf3\xb9\xab\xbc\xd0\xa4\xa7\xa4W
\t\t:param self:
\t\t:return:
\t\t'''
        import cursor
        oBtnBuy = self.GetObject('btn_buy')
        (iBtnPosX, iBtnPosY) = oBtnBuy.GetScreenPos()
        (iMousePosX, iMousePosY) = cursor.GetCursorPos()
        iDisX = iMousePosX - iBtnPosX
        iDisY = iMousePosY - iBtnPosY
        (iCurPosX, iCurPosY) = self.GetPos()
        iEndPosX = iCurPosX + iDisX
        iEndPosY = iCurPosY + iDisY
        (iBtnSizeW, iBtnSizeH) = oBtnBuy.GetSize()
        self.SetPos(iEndPosX - iBtnSizeW / 2, iEndPosY - iBtnSizeH / 2)

    
    def CloseWindow(self):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.OnCloseMiniBuyPanel()

    
    def OnLimitEditChange(self, oEdit):
        oParent = self.GetParent()
        if oParent:
            if self.m_ChangeFlag:
                return None
            
            sText = oEdit.GetText()
            if sText is not None:
                oParent.OnMiniBuyNum(sText)
            
        

    
    def OnItemEnter(self, oItemCheckBox):
        global g_tips
        iShape = self.m_dItemData.get('iShape', 0)
        iKey = self.GetItemKeyByShape(iShape)
        g_tips = dlggetinfo.NewItemInfo(self.m_dItemData.get('iIndex', 0), iShape, self.m_dItemData.get('sTips', ''), None, iKey)

    
    def GetItemKeyByShape(self, iShape):
        import item
        if iShape in (itemdefine.ID_ITEM_VIP, itemdefine.ID_RANDOM_SUMMON_BOOK_REWARD, itemdefine.ID_RANDOM_BAZHENTU):
            return 0
        elif iShape in (itemdefine.ID_JINGPING_SUMMON_BOOK_ITEM,):
            return item.MARK_JINGPIN
        else:
            return item.MARK_BOUND

    
    def OnItemLeave(self, oItemCheckBox):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.OnItemLeave(None)

    
    def DoBuy(self):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.DoBuy()

    
    def OnChangeNum(self, iMsgID):
        oParent = self.GetParent()
        if oParent:
            if iMsgID == 3:
                oParent.OnMiniBuyChange(-1)
            elif iMsgID == 4:
                oParent.OnMiniBuyChange(1)
            
        

    
    def OnRightChangeNum(self, iMsgID):
        oParent = self.GetParent()
        if oParent:
            if iMsgID == interface.RIGHT_BUTTON_MESSAGE + 3:
                oParent.OnMiniBuyNum('1')
            elif iMsgID == interface.RIGHT_BUTTON_MESSAGE + 4:
                oParent.OnMiniBuyMax()
            
        

    
    def SetPos(self, x, y):
        import ratio
        oParent = self.GetParent()
        if oParent:
            iMaxX = ratio.WINDOW_WIDTH
            iMaxY = ratio.WINDOW_HEIGHT
            (iParentX, iParentY) = oParent.GetScreenPos()
            iX = iParentX + x
            iY = iParentY + y
            (iW, iH) = self.GetSize()
            if iX < 0:
                x = x - iX
            elif iX + iW > iMaxX:
                x = iMaxX - iW - iParentX
            
            if iY < 0:
                y = y - iY
            elif iY + iH > iMaxY:
                y = iMaxY - iH - iParentY
            
            combdialog.CCombDialog.SetPos(self, x, y)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.DoBuy()
        elif iMsgID in (3, 4):
            self.OnChangeNum(iMsgID)
        elif iMsgID in (interface.RIGHT_BUTTON_MESSAGE + 3, interface.RIGHT_BUTTON_MESSAGE + 4):
            self.OnRightChangeNum(iMsgID)
        



class CMiniBuyItemCheckBox(wrapinterface.CItemCheckBox1):
    
    def SetText(self, sText):
        sTestList = sText.split('#r')
        self.m_TextObjects = []
        iTextHeight = 0
        for sTextStr in sTestList:
            oText = interface.CTextObject(self, sTextStr, self.m_Font, self.m_Color, 0)
            (_, iObjH) = oText.GetSize()
            iTextHeight = iTextHeight + iObjH
            self.m_TextObjects.append(oText)
        
        (_, iSelfH) = self.GetSize()
        offsetY = None if len(self.m_TextObjects) == 3 else 6
        iTextY = (iSelfH - iTextHeight) / 2 - 2
        for oText in self.m_TextObjects:
            oText.SetPos(54, iTextY)
            (_, iObjH) = oText.GetSize()
            iTextY += iObjH + offsetY
        



class CCashShadowText(interface.CShadowText):
    
    def __init__(self, parent, txt, fontid, color, space = 0):
        if txt.isdigit():
            txt = misc.GetCashString(int(txt))
        
        interface.CShadowText.__init__(self, parent, txt, fontid, color, color, space)



class CItemBillDoubleEleven(CItemBillGoods):
    REFRESHTIME = 10
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/double11.dlg')
        self.HintText = self.GetObject('text_tishi')
        self.NextRefrehTimeText = self.GetObject('text_time')
        self.m_BtnDiscountBuy = self.GetObject('txtbtn_quan')
        self.m_oTips = self.GetObject('text_tips')
        self.m_oTimer = None
        self.m_oAni = None
        self.SetZ(1)
        self.m_oMiniBuyPanel = None
        self.initData()
        self.CreateBuyAmountEdit()
        self.OnBuy(None)
        self.ShowItemType(self.MONEY_TYPE)
        (iX, iY, iW, iH) = self.GetItemBoxLocData()
        self.m_oMark = interface.CClickBox(self, iW, iH, 16711680, 0)
        self.m_oMark.SetPos(iX, iY)
        self.m_oMark.SetShow(False)
        self.m_DelayCreatCommand = None
        self.CheckDiscount()
        self.InitTimer()
        self.InitSignals()

    
    def InitSignals(self):
        import mdpropitem
        oModel = mdpropitem.GetModel()
        oModel.ssConnect(oModel.SS_UpdateBagChange, self.CheckDiscount)

    
    def InitTextTime(self):
        import misc
        iCurTime = misc.GetServerCurrentTime()
        (bLastDay, iHourRemain, iMinuteRemain) = self.CalcRemainTime(iCurTime)
        if bLastDay:
            self.NextRefrehTimeText.SetText('\xb6Z\xac\xa1\xb0\xca\xb5\xb2\xa7\xf4\xa1G%.2d\xa4p\xae\xc9%.2d\xa4\xc0' % (iHourRemain, iMinuteRemain))
        else:
            (iHourTill, iMinuteTill) = self.CalcTimeToRefreshTime(iCurTime)
            self.NextRefrehTimeText.SetText('\xb6Z\xa4U\xa6\xb8\xb9D\xa8\xe3\xa8\xea\xb7s\xa1G%.2d\xa4p\xae\xc9%.2d\xa4\xc0' % (iHourTill, iMinuteTill))

    
    def InitTimer(self):
        import timer
        import misc
        timer.Timer(0, misc.Functor(self.InitTextTime), 0, self)
        if not (self.m_oTimer) or self.m_oTimer.IsReleased():
            self.m_oTimer = timer.Timer(60, misc.Functor(self.InitTextTime), -1, self)
        

    
    def ShowBtnDiscountBlink(self, iFlag):
        if iFlag:
            self.m_oAni = ui.CImage(self.m_BtnDiscountBuy, 'common/hint.igs', interface.UIPath)
            (xSize, ySize) = self.m_BtnDiscountBuy.GetSize()
            self.m_oAni.SetPos(xSize / 2, ySize / 2)
            self.m_oAni.SetZ(1)
            self.m_oAni.CreateCommand(2, 'animation')
            self.ReleaseBlinkCommand()
        

    
    def ReleaseBlinkEffect(self):
        if self.m_oAni:
            self.m_oAni.ReleaseCommand()
            self.m_oAni = None
        

    
    def ReleaseBlinkCommand(self, iSec = 3):
        import timer
        timer.Timer(iSec, misc.Functor(self.ReleaseBlinkEffect), 0, self)

    
    def CalcRemainTime(self, iCurTime):
        import time
        structTime = time.localtime(iCurTime)
        iYear = structTime[0]
        iMonth = structTime[1]
        iDay = structTime[2]
        iHour = structTime[3]
        bLastDay = False
        iHourRemain = 23
        iMinuteRemain = 59
        if iYear == 2019 and iMonth == 11 and iDay == 11 and iHour >= 10:
            iMinute = structTime[4]
            bLastDay = True
            iHourRemain -= iHour
            if iMinute > 0:
                iMinuteRemain -= iMinute
            
        
        return (bLastDay, iHourRemain, iMinuteRemain)

    
    def CalcTimeToRefreshTime(self, iCurTime):
        import time
        structTime = time.localtime(iCurTime)
        iHour = structTime[3]
        iMinute = structTime[4]
        iHourTill = 0
        iMinuteTill = 0
        if iHour < 10:
            iHourTill = 10 - iHour
        else:
            iHourTill = 34 - iHour
        if iMinute > 0:
            iMinuteTill = 60 - iMinute
            iHourTill -= 1
        
        return (iHourTill, iMinuteTill)

    
    def GetItemBoxLocData(self):
        return self.GetLocData('itbox_goods')

    
    def GetItemBoxObject(self):
        return self.GetObject('itbox_goods')

    
    def SetImage(self, itype):
        pass

    
    def CheckDiscount(self):
        self.EnableBtnDiscount(self.GetValidDiscountTicketsQuantity())

    
    def GetValidDiscountTicketsQuantity(self):
        import item
        import itemdefine
        import misc
        iCurSvrTime = misc.GetServerCurrentTime()
        oItemDict = item.GetItemsByShape(itemdefine.ID_DOUBLE_ELEVEN_TICKET)
        iQuantity = 0
        for oItem in oItemDict.values():
            iTime = int(oItem.GetExtInfo('Time', 0))
            if iTime > iCurSvrTime:
                iQuantity += 1
                continue
        
        return iQuantity

    
    def EnableBtnDiscount(self, iQuantity):
        if iQuantity:
            self.m_BtnDiscountBuy.SetBigRedDot(iQuantity, iOffsetX = 7, iOffsetY = -7)
            self.m_BtnDiscountBuy.Enable(True)
            self.m_oTips.Enable(False)
        else:
            self.m_BtnDiscountBuy.SetBigRedDot(0)
            self.m_BtnDiscountBuy.Enable(False)
            self.m_oTips.Enable(True)

    
    def EnableParentKeyObjects(self, bEnable):
        oView = self.GetParent()
        oView.SetShowObject('noname9', bEnable)
        oView.SetShowObject('noname7', bEnable)
        oView.SetShowObject('btn_CardCharge', bEnable)
        oView.SetShowObject('btn_QuickPay', bEnable)
        oView.SetShowObject('loc_Tips1', bEnable)
        oView.SetShowObject('loc_Tips2', bEnable)
        oView.SetClickObjectShow(bEnable)
        if not bEnable:
            oView.SetShowObject('text_dft_001', bEnable)
        

    
    def EnableBuyList(self, bEnable):
        self.SetShowObject('itbox_goods', bEnable)
        self.SetShowObject('btn_Bar', bEnable)
        self.SetShowObject('text_tishi', not bEnable)

    
    def SetShow(self, iShow):
        self.EnableParentKeyObjects(not iShow)
        CItemBillGoods.SetShow(self, iShow)

    
    def SetBuyList(self, buylist, page = 0, iRealPage = 0):
        CItemBillGoods.SetBuyList(self, buylist, page, iRealPage)
        self.EnableBuyList(len(buylist) > 0)
        if not len(buylist):
            self.m_oItemsDict = { }
            self.EnableBtnDiscount(0)
        else:
            self.CheckDiscount()

    
    def initData(self):
        self.m_SelectedItem = None
        self.m_iSelectedServerIdx = None
        self.m_CurrentPage = None
        self.m_ShopType = 0
        self.m_Prepage = self.GetObject('itbox_goods').GetTotal()
        self.m_SelectedShape = 0
        self.m_DefaultItemID = 0

    
    def UseDiscountTicket(self):
        import dlgnpc
        iQuantity = self.GetValidDiscountTicketsQuantity()
        sMsg = '\xbdT\xa9w\xae\xf8\xaf\xd3\xa4@\xad\xd3\xa7\xe9\xa6\xa9\xa8\xe9\xac\xb0\xb7\xed\xabe\xa5X\xb0\xe2\xaa\xba\xb9D\xa8\xe3\xad\xb0\xa7C\xa7\xe9\xa6\xa9\xb6\xdc\xa1H\xb7\xed\xabe\xbe\xd6\xa6\xb3\xa7\xe9\xa6\xa9\xa8\xe9%d\xb1i\nQ\xbdT\xa9w\nQ\xa8\xfa\xae\xf8' % iQuantity
        dlgnpc.ShowClientDlg(sMsg, '', misc.Functor(self.OnDiscountMessage))

    
    def OnDiscountMessage(self, iMsgId):
        import usermacro
        import csdoubleeleven
        if iMsgId == 1:
            LOG_DEBUG('\xb5o\xb0e\xa7\xe9\xa6\xa9\xa8\xe9\xa8\xf3\xc4\xb3')
            iNum = self.GetValidDiscountTicketsQuantity()
            if iNum <= 0:
                usermacro.PROMPT_MSG('\xa7A\xa8S\xa6\xb3\xa7\xe9\xa6\xa9\xa8\xe9')
                return None
            
            csdoubleeleven.C2GSUseDiscountTicket()
        

    
    def DoBuy(self):
        import usermacro
        if self.m_BuyTarget is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xa4\xa4\xa7A\xadn\xc1\xca\xb6R\xaa\xba\xb9D\xa8\xe3')
            return None
        
        
        try:
            amount = int(self.m_BuyAmountEdit.GetText())
        except:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xba\xa7I\xb4\xab\xbc\xc6\xb6q')
            return None

        if amount <= 0:
            usermacro.PROMPT_MSG('\xc1\xca\xb6R\xbc\xc6\xb6q\xa6\xdc\xa4\xd6\xac\xb01')
            return None
        
        iLimitAmount = self.m_BuyAmountEdit.GetMaxNum()
        if amount > iLimitAmount or iLimitAmount == 0:
            if self.m_ShopType == 7:
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xad\xad\xc1\xca\xbc\xc6\xb6q'
            elif self.m_ShopType == 1 and self.m_SelectedShape in itemdefine.ITEM_SHENGONGFU:
                sText = '\xa4w\xb9F\xa8\xec\xa5\xbb\xa4\xeb\xc1\xca\xb6R\xbc\xc6\xb6q\xa4W\xad\xad'
            else:
                sText = '\xc1\xca\xb6R\xbc\xc6\xb6q\xa4\xa3\xaf\xe0\xb6W\xa5X\xa5\xbb\xa9P\xad\xad\xc1\xca\xbc\xc6\xb6q'
            usermacro.PROMPT_MSG(sText)
            return None
        
        SetLastSelectData(self.m_BuyTarget, amount, self.m_CurrentPage, self.m_SelectedShape)
        if self.m_BuyTarget == 0 and self.m_ShopType in (1, 2):
            self.GetParent().BuyVip(self.m_ShopType)
            return None
        
        if self.m_ShopType in (1, 2):
            buytarget = self.m_BuyTarget - 1
        else:
            buytarget = self.m_BuyTarget
        C2SBuyCommonIB(buytarget, amount)

    
    def OnMessage(self, iMsgID):
        CItemBillGoods.OnMessage(self, iMsgID)
        if iMsgID == 25:
            self.UseDiscountTicket()
        elif iMsgID == 8:
            QuickPay()
        



class CItemBillMain(combdialog.CCombSubWnd):
    BTN_SORT = ('btn_Goods1', 'btn_Goods6', 'btn_Goods2', 'btn_Goods4', 'btn_Goods3', 'btn_Goods7', 'btn_Goods9', 'btn_Goods8', 'btn_Goods5', 'btn_Goods10', 'btn_Goods12', 'btn_Goods13')
    TAB2NAME = {
        netreddot.DOUBLEELEVEN: 'btn_Goods10',
        netreddot.AVATARFRAMESHOP: 'btn_Goods12',
        netreddot.SHOP_WEEKGIFT: 'btn_Goods6' }
    
    def __init__(self, oParent, showbtnlst, iDefaultPage, iDefaultItemID):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/itembill_new/itembill_shop.dlg')
        self.m_oDlgGoods = None
        self.m_oDlgDoubleEleven = None
        self.m_oDlgAvatarFrame = None
        self.m_DefaultItemID = iDefaultItemID
        self.m_oChargeRedDot = None
        self.m_oDiscountTimer = None
        self.m_oGuideSubscribe = None
        self.m_ShopType = None
        self.InitBtnPos()
        self.SetBtnType()
        self.SetBtnShow(showbtnlst)
        self.GetObject('btn_Goods%d' % iDefaultPage).SetSelect(True)
        if self.GetObject('img_huobao'):
            self.GetObject('img_huobao').SetZ(1)
        
        self.CreateClickText()
        self.SetState467Tips()
        self.OnChangeType(iDefaultPage)
        self.InitSignals()
        self.CreateDiscountTimer()
        self.InitRichTextSubscribe()
        self.InitRedDot()

    
    def InitRichTextSubscribe(self):
        oRichSub = self.GetObject('rtxt_book')
        oRichSub.SetEnterCB(misc.Functor(self.OnRichTextSubscribeEnter))
        oRichSub.SetLeaveCB(misc.Functor(self.OnRichTextSubscribeLeave))

    
    def InitRedDot(self):
        oRedMgr = mdreddot.GetMgr()
        oNode = oRedMgr.GetNode('\xb0\xd3\xab\xb0\xa1A\xa8C\xb6g\xc2\xa7\xa5]\xa1A\xadq\xbe\\')
        (iW, _) = self.GetObject('rtxt_book').GetSize()
        iPosX = iW / 2
        self.m_oSubScribeRedDot = CSubScribeRedDot(oNode, oParent = self.GetObject('rtxt_book'))
        self.m_oSubScribeRedDot.UpdateRenderParam(iPosX)
        self.m_oWeeklyPurchaseRedDot = dlgreddot.CSimpleRedDotWidget(self.GetObject('btn_Goods1'), oNode, iOffsetX = -2, iOffsetY = 2)

    
    def CreateSubscribeGuide(self):
        (iSizeW, iSizeH) = self.GetObject('rtxt_book').GetSize()
        self.m_oRedGuide = wrapinterface.CCombTipsBox(self.GetObject('rtxt_book'), '\xadq\xbe\\\xaaA\xb0\xc8\xb1\xf8\xb4\xda\xa6\xb3\xa7\xf3\xb7s\xa1A\xbd\xd0\xc2I\xc0\xbb\xacd\xac\xdd', 6, iSizeW / 2, 0, 130, 60, -20, 0)

    
    def DestroySubscribeGuide(self):
        self.m_oRedGuide = None

    
    def Clear(self):
        if self.m_oDlgGoods:
            self.m_oDlgGoods.m_BuyList = None
        

    
    def SetShowDlgs(self, listDlg, bShow):
        for oDlg in listDlg:
            if oDlg:
                oDlg.SetShow(bShow)
                continue
        

    
    def InitSignals(self):
        import netreddot
        oModel = mdredpoint.GetCRedPointModel()
        oModel.ssConnect(oModel.SS_UpdateRedPoint, self.OnUpdateRedDot)
        for iType in [
            netreddot.DOUBLEELEVEN,
            netreddot.AVATARFRAMESHOP,
            netreddot.CHARGE_REWARD,
            netreddot.SHOP_WEEKGIFT]:
            dRedPoint = oModel.GetRedPointState(iType)
            self.OnUpdateRedDot(iType, dRedPoint.get('bRed'), dRedPoint.get('iNum'))
        

    
    def CreateDiscountTimer(self):
        import timer
        if misc.GetServerCurrentTime() < itembilldefines.DISCOUNT_TIME_STAMP:
            self.ReleaseDiscountTimer()
            self.m_oDiscountTimer = timer.Timer(1, self.OnRefreshDiscount, -1, self)
        

    
    def ReleaseDiscountTimer(self):
        if self.m_oDiscountTimer:
            self.m_oDiscountTimer.Release()
        
        self.m_oDiscountTimer = None

    
    def OnRefreshDiscount(self):
        if misc.GetServerCurrentTime() >= itembilldefines.DISCOUNT_TIME_STAMP:
            self.ReleaseDiscountTimer()
            C2SAskOpenItemBill(1)
        

    
    def OnUpdateRedDot(self, iType, bRed, iNum):
        import netreddot
        if iType in self.TAB2NAME:
            self.GetObject(self.TAB2NAME[iType]).SetRedDot(bRed, interface.ALIGN_LEFT_TOP, 70, 2)
        elif iType == netreddot.CHARGE_REWARD:
            if bRed:
                oRichText = self.GetObject('txt_GetReward')
                if oRichText:
                    self.m_oChargeRedDot = CreateRedpointObj(oRichText)
                    interface.TopRight(self.m_oChargeRedDot)
                
            else:
                self.m_oChargeRedDot = None
        

    
    def BlinkDoubleEleven(self, iFlag):
        if self.m_oDlgDoubleEleven and self.m_oDlgDoubleEleven.GetShow():
            self.m_oDlgDoubleEleven.ShowBtnDiscountBlink(iFlag)
        

    
    def SetBuyList(self, buylist, page = 0, iRealPage = 0):
        if iRealPage == 10:
            if self.m_oDlgDoubleEleven is None:
                self.m_oDlgDoubleEleven = CItemBillDoubleEleven(self)
            
            self.m_oDlgDoubleEleven.SetShow(True)
            self.SetShowDlgs([
                self.m_oDlgGoods,
                self.m_oDlgAvatarFrame], False)
            self.m_oDlgDoubleEleven.SetShopType(self.m_ShopType)
            self.m_oDlgDoubleEleven.SetDefaultItemId(self.m_DefaultItemID)
            self.m_DefaultItemID = 0
            self.m_oDlgDoubleEleven.SetBuyList(buylist, page, iRealPage)
            self.SetShowRechargePanel(True)
        elif iRealPage == itembilldefines.SHOPTYPE_AVATAR_FRAME:
            import dlgavatarframeshop
            if self.m_oDlgAvatarFrame is None:
                self.m_oDlgAvatarFrame = dlgavatarframeshop.CAvatarFrameShopDlg(self)
            
            self.SetShowRechargePanel(False)
            self.m_oDlgAvatarFrame.SetShow(True)
            self.SetShowDlgs([
                self.m_oDlgGoods,
                self.m_oDlgDoubleEleven], False)
            self.m_oDlgAvatarFrame.SetBuyList(buylist, page, iRealPage)
        elif self.m_oDlgGoods is None:
            self.m_oDlgGoods = CItemBillGoods(self)
        elif not self.m_oDlgGoods.GetShow():
            self.m_oDlgGoods.SetShow(True)
        
        if self.m_oDlgDoubleEleven:
            self.m_oDlgDoubleEleven.SetShow(False)
        
        if self.m_oDlgAvatarFrame:
            self.m_oDlgAvatarFrame.SetShow(False)
        
        self.m_oDlgGoods.SetShopType(self.m_ShopType)
        self.m_oDlgGoods.SetDefaultItemId(self.m_DefaultItemID)
        self.m_DefaultItemID = 0
        self.m_oDlgGoods.SetBuyList(buylist, page, iRealPage)
        self.SetShowRechargePanel(True)

    
    def SetShowRechargePanel(self, bShow):
        for sName in [
            'btn_QuickPay',
            'btn_CardCharg5',
            'btn_CardCharge',
            'noname7',
            'loc_Tips1',
            'loc_Tips2',
            'noname9',
            'noname3',
            'img_cashflow']:
            self.SetShowObject(sName, bShow)
        
        if self.m_FreeVipTips:
            self.m_FreeVipTips.SetShow(bShow)
        
        self.SetClickObjectShow(bShow)
        self.SetShowObject('text_dft_001', self.m_ShopType == itembilldefines.SHOPTYPE_TREASURE)

    
    def SetSecretRedpoint(self, bShow):
        pageObj = self.GetObject('btn_Goods7')
        if bShow:
            pageObj.m_SecretRedTips = CreateRedpointObj(pageObj)
        else:
            pageObj.m_SecretRedTips = None

    
    def SetFestivalRedpoint(self, bShow):
        pageObj = self.GetObject('btn_Goods8')
        if bShow:
            pageObj.m_FestivalRedTips = CreateRedpointObj(pageObj)
        else:
            pageObj.m_FestivalRedTips = None

    
    def SetTreasureRedpoint(self, bShow):
        pageObj = self.GetObject('btn_Goods9')
        if bShow:
            pageObj.m_TreasureRedTips = CreateRedpointObj(pageObj)
        else:
            pageObj.m_TreasureRedTips = None

    
    def SetNewServerRedPoint(self, bShow):
        pageObj = self.GetObject('btn_Goods13')
        if bShow:
            pageObj.m_TreasureRedTips = CreateRedpointObj(pageObj)
        else:
            pageObj.m_TreasureRedTips = None

    
    def SetDiscountShopRedpoint(self, bShow):
        pageObj = self.GetObject('btn_Goods1')
        if bShow:
            pageObj.m_DiscountShopRedTips = CreateRedpointObj(pageObj)
        else:
            pageObj.m_DiscountShopRedTips = None

    
    def SetState467Tips(self):
        import netstate
        self.ShowState467Tips(netstate.GetState(467))

    
    def ShowState467Tips(self, isShow):
        if isShow:
            obj = self.GetObject('loc_Tips1')
            if not obj:
                return None
            
            (x, y) = obj.GetPos()
            self.m_FreeVipTips = interface.CTextObject(self, '\xad\xba\xa5R\xb0eVIP', interface.FontLT12_1, interface.COLOR_25)
            self.m_FreeVipTips.SetPos(x, y)
        else:
            self.m_FreeVipTips = None

    
    def IsHideShenHeBtn(self, sName):
        import hero
        if hero.IsShenHe():
            if sName == 'txt_Dyt':
                return True
            
        else:
            return False

    
    def CreateClickText(self):
        self.m_ClickTextList = []
        iClickRichTextDict = {
            'txt_GetReward': 30,
            'txt_Dyt': 31 }
        for name, msgID in iClickRichTextDict.items():
            oClickText = self.GetObject(name)
            if self.IsHideShenHeBtn(name):
                if oClickText:
                    pass
                oClickText.SetShow(False)
                continue
            
            oClickText.SetEnterCB(misc.Functor(self.OnClickTextEnter, oClickText, msgID))
            oClickText.SetLeaveCB(misc.Functor(self.OnClickTextLeave, oClickText, msgID))
            self.m_ClickTextList.append(oClickText)
        

    
    def SetClickObjectShow(self, bShow):
        for obj in self.m_ClickTextList:
            obj.SetShow(bShow)
        

    
    def InitBtnPos(self):
        self.m_BtnPosList = []
        for objname in self.BTN_SORT:
            (x, y) = self.GetObject(objname).GetPos()
            self.m_BtnPosList.append((x, y))
        
        self.SetSecretRedpoint(g_SecretRedpoint)
        self.SetFestivalRedpoint(g_FestivelRedpoint)
        self.SetTreasureRedpoint(g_TreasureRedpoint)
        self.SetNewServerRedPoint(g_NewServerRedpoint)
        self.SetDiscountShopRedpoint(g_DiscountRedPoint)

    
    def SetBtnShow(self, showbtnlst):
        for objname in self.BTN_SORT:
            self.GetObject(objname).SetShow(False)
        
        for btnidx in showbtnlst:
            self.GetObject('btn_Goods%d' % btnidx).SetShow(True)
        
        if 7 not in showbtnlst and g_SecretRedpoint:
            netreddot.C2SRemoveRedDot(netreddot.SECRET)
        
        if 8 not in showbtnlst and g_FestivelRedpoint:
            netreddot.C2SRemoveRedDot(netreddot.FESTIVALGIFT)
        
        if itembilldefines.SHOPTYPE_TREASURE not in showbtnlst and g_TreasureRedpoint:
            netreddot.C2SRemoveRedDot(netreddot.TREASURESHOP)
        
        if itembilldefines.SHOPTYPE_NEW_SERVER not in showbtnlst and g_NewServerRedpoint:
            netreddot.C2SRemoveRedDot(netreddot.NEWSERVERSHOP)
        
        if itembilldefines.SHOPTYPE_DISCOUNT not in showbtnlst and g_DiscountRedPoint:
            netreddot.C2SRemoveRedDot(netreddot.DISCOUNTSHOP)
        
        self.RefreshBtnPos()

    
    def RefreshBtnPos(self):
        iPosIdx = 0
        for objname in self.BTN_SORT:
            obj = self.GetObject(objname)
            if obj.GetShow():
                (x, y) = self.m_BtnPosList[iPosIdx]
                obj.SetPos(x, y)
                iPosIdx += 1
                continue
        

    
    def SetBtnType(self):
        for objname in ('btn_CardCharge', 'btn_QuickPay'):
            self.GetObject(objname).m_ParentNotify = True
        

    
    def OnClickTextEnter(self, oText, iMsgID):
        sTips = {
            16: '\xb6i\xa6\xe6\xb9C\xc0\xb8\xc2I\xbc\xc6\xbc\xb7\xc2I',
            17: '\xa5R\xad\xc8\xa7Y\xa5i\xc0\xf2\xb1o\xb9C\xc0\xb8\xb9\xf4\xaa\xba\xbc\xfa\xc0y' }.get(iMsgID)
        if sTips:
            self.m_Tips = wrapinterface.CTextTips(None, -1, sTips, interface.FontLT14_3, direct = 1)
            self.m_Tips.SetOwner(oText)
        

    
    def OnClickTextLeave(self, oText, iMsgID):
        if iMsgID in (16, 17):
            self.m_Tips = None
        

    
    def OnButtonEnter(self, btn):
        txt = {
            8: '\xb3q\xb9L\xb3q\xa5\xce\xa5d\xa9\xce\xaa\xccATM\xc1\xca\xb6R\xb9C\xc0\xb8\xc2I\xbc\xc6\xa9\xce\xb1H\xb0\xe2\xa5d',
            14: '\xa5i\xc1\xca\xb6R\xa9M\xa5X\xb0\xe2\xb1H\xb0\xe2\xa5d',
            4: '\xa8C\xa4\xd110:00\xc0H\xbe\xf7\xa8\xea\xb7s\xba\xd8\xc3\xfe\xa4\xce\xbb\xf9\xae\xe6' }[btn.m_MsgID]
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def BuyVip(self, iShopType):
        import hero
        if hero.g_Prop.m_Gold >= 150:
            CSGSAskContributeVipShop(itembilldefines.SHOP2BUY.get(iShopType, 0))
            return None
        
        import quickpay
        quickpay.ShowQuickPay()

    
    def MobileCheck(self, msgid):
        if msgid == 1:
            import hero
            if hero.g_Prop.m_Grade < 30:
                import usermacro
                usermacro.PROMPT_MSG('\xb5\xa5\xaf\xc5\xb9F\xa8\xec30\xaf\xc5\xa4~\xaf\xe0\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
                return None
            
            import dlgsysopt
            dlgsysopt.MobileCheck(True)
        

    
    def IsInKuaFuServer(self):
        if misc.IsInKuafuServer():
            import usermacro
            usermacro.PROMPT_MSG('\xb8\xf3\xaaA\xb5L\xaak\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return True
        

    
    def OnCardPay(self):
        if self.IsInKuaFuServer():
            return None
        
        import dlgpointcardcharge
        dlgpointcardcharge.ShowDlg()

    
    def DoOpenVendue(self):
        import dlgitembill
        self.m_oVendueDlg = dlgitembill.CVendue()

    
    def DoPoint2SG_TW(self):
        CSGSPointChangeWorldContributeShop()

    
    def BuyTimeCard(self):
        if self.IsInKuaFuServer():
            return None
        
        import dlgnpc
        dlgnpc.ShowClientDlg('Q\xa7\xda\xadn\xa5\xce\xb2{\xaa\xf7\xa5\xe6\xa9\xf6\xb1H\xb0\xe2\xa5d\nQ\xa7\xda\xadn\xa5\xce\xb9\xda\xb7Q\xb9\xf4\xa5\xe6\xa9\xf6\xb1H\xb0\xe2\xa5d', '', misc.Functor(self.OnBuyTimeCardCallback))

    
    def OnBuyTimeCardCallback(self, iMsgID):
        if iMsgID in (1, 2):
            CSGSAskBuyTimeCardShop(iMsgID - 1)
        

    
    def DytPoint2SG(self):
        if self.IsInKuaFuServer():
            return None
        
        import hero
        if hero.g_Prop.m_IsDYT:
            import dlgitembill
            if not dlgitembill.GetHasBindPhone():
                import dlgnpc
                dlgnpc.ShowClientDlg('\xb1z\xaa\xba\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xa5\xbc\xb8j\xa9w\xa4\xe2\xbe\xf7\xa1A\xbd\xd0\xb6i\xa6\xe6\xa4\xe2\xbe\xf7\xb8j\xa9w\nQ\xa7\xda\xadn\xb8j\xa9w\xa4\xe2\xbe\xf7', '', self.MobileCheck)
            else:
                import netplayer
                netplayer.C2SDytPoint2SG()
        else:
            import usermacro
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xb1b\xb8\xb9\xa5\xd8\xabe\xac\xb0\xabD\xbe\xd4\xb7\xf9\xb1b\xb8\xb9\xa1A\xbd\xd0\xa5\xfd\xb1N\xb1b\xb8\xb9\xa4\xc9\xaf\xc5\xac\xb0\xbe\xd4\xb7\xf9\xb1b\xb8\xb9')

    
    def GetPayReward(self):
        if self.IsInKuaFuServer():
            return None
        
        CSGSDrawEncouragementShop()
        netreddot.C2SRemoveRedDot(netreddot.CHARGE_REWARD)

    
    def StartDingYue(self):
        import hero
        if hero.GetProp('m_Grade', 0) < 30:
            usermacro.PROMPT_MSG('\xa4H\xaa\xab\xb9F\xa8\xec30\xaf\xc5\xab\xe1\xa4~\xa5i\xb6i\xa6\xe6\xadq\xbe\\')
            return None
        
        if self.CheckRedPointState(netreddot.SHOP_WEEKGIFT):
            netreddot.C2SRemoveRedDot(netreddot.SHOP_WEEKGIFT)
            self.DestroySubscribeGuide()
        
        C2SRequestDingYueShape()

    
    def OnChangeType(self, iType):
        '''
\t\t\xa4\xc1\xb4\xab\xa4\xc0\xad\xb6\xa1A\xbd\xd0\xa8D\xaaA\xb0\xc8\xbe\xb9\xb5o\xbc\xc6\xbe\xda\xa8\xc3\xae\xf8\xb0\xa3\xac\xf5\xc2I
\t\t:param iT) 5jY\xef\xbf\xee\x8c\xfa\xea\xa4\xc0\xad\xb6
\t\t'''
        SetLastSelectData(-1, -1, -1, -1)
        self.m_ShopType = iType
        C2SAskOpenShopPage(iType)
        if iType in [
            itembilldefines.SHOPTYPE_WEEKGIFT,
            itembilldefines.SHOPTYPE_DISCOUNT]:
            self.SetShowObject('rtxt_book', True)
            if self.CheckRedPointState(netreddot.SHOP_WEEKGIFT):
                pass
            self.CreateSubscribeGuide()
        else:
            self.SetShowObject('rtxt_book', False)
        dPage2Dot = {
            itembilldefines.SHOPTYPE_DISCOUNT: (netreddot.DISCOUNTSHOP, g_DiscountRedPoint),
            itembilldefines.SHOWTYPE_SECRET: (netreddot.SECRET, g_SecretRedpoint),
            itembilldefines.SHOWTYPE_FESTIVALGIFT: (netreddot.FESTIVALGIFT, g_FestivelRedpoint),
            itembilldefines.SHOPTYPE_TREASURE: (netreddot.TREASURESHOP, g_TreasureRedpoint),
            itembilldefines.SHOWTYPE_DOUBLEELEVEN: (netreddot.DOUBLEELEVEN, True),
            itembilldefines.SHOPTYPE_AVATAR_FRAME: (netreddot.AVATARFRAMESHOP, True),
            itembilldefines.SHOPTYPE_NEW_SERVER: (netreddot.NEWSERVERSHOP, g_NewServerRedpoint) }
        if iType in dPage2Dot:
            (iRedDotID, bSend) = dPage2Dot[iType]
            if bSend:
                netreddot.C2SRemoveRedDot(iRedDotID)
            
        

    
    def OnRichTextSubscribeEnter(self):
        self.m_oSubTips = wrapinterface.CTextTips(self.GetObject('rtxt_book'), -1, '\xacd\xac\xdd\xa9M\xb6i\xa6\xe6\xa8C\xb6g\xadq\xbe\\', interface.FontLT14_3, direct = 1)
        self.m_oSubTips.SetOwner(self.GetObject('rtxt_book'))

    
    def OnRichTextSubscribeLeave(self):
        self.m_oSubTips = None

    
    def CheckRedPointState(self, iType):
        dInfo = mdredpoint.GetCRedPointModel().GetRedPointState(iType)
        return None if dInfo else False

    
    def OnMessage(self, msgid):
        msgid2log = {
            8: '\xb9\xda\xb7Q\xa5@\xac\xc9\xb0\xd3\xab\xb0-\xa7\xd6\xb1\xb6\xa5R\xad\xc8',
            14: '\xb9\xda\xb7Q\xa5@\xac\xc9\xb0\xd3\xab\xb0-\xb1H\xb0\xe2\xa5d\xa5\xe6\xa9\xf6',
            10: '\xb9\xda\xb7Q\xa5@\xac\xc9\xb0\xd3\xab\xb0-\xc2I\xa5d\xa5R\xad\xc8',
            31: '\xb9\xda\xb7Q\xa5@\xac\xc9\xb0\xd3\xab\xb0-\xbe\xd4\xb7\xf9\xc2I\xbc\xc6\xac\xdb\xc3\xf6',
            30: '\xb9\xda\xb7Q\xa5@\xac\xc9\xb0\xd3\xab\xb0-\xbb\xe2\xa8\xfa\xa5R\xad\xc8\xbc\xfa\xc0y' }
        if msgid in msgid2log:
            import clickcounter
            clickcounter.Log(msgid2log[msgid])
        
        if msgid in (1, 5, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28):
            msgid2shoptype = {
                1: 1,
                19: 2,
                21: 3,
                20: 4,
                5: 5,
                22: 6,
                23: 7,
                24: 8,
                25: itembilldefines.SHOPTYPE_TREASURE,
                26: 10,
                27: itembilldefines.SHOPTYPE_AVATAR_FRAME,
                28: itembilldefines.SHOPTYPE_NEW_SERVER }
            self.m_Items = []
            self.m_DogSpecialItem = []
            self.OnChangeType(msgid2shoptype[msgid])
        elif msgid == 8:
            if misc.IsTWServer():
                QuickPay_TW()
            else:
                QuickPay()
        elif msgid == 14:
            self.BuyTimeCard()
        elif msgid == 18:
            self.DoOpenVendue()
        elif msgid == 31:
            if misc.IsTWServer():
                self.DoPoint2SG_TW()
            else:
                self.DytPoint2SG()
        elif msgid == 30:
            self.GetPayReward()
        elif msgid == 29:
            self.StartDingYue()
        



class CReadyDingYueDlg(combdialog.CCombDialog):
    sUIName = 'dialog/itembill/itembill_new/itembill_book.dlg'
    dOpenUIConfig = {
        'KEY_PARENT': 'CapturePanel',
        'KEY_IS_IGNORE_ESC': True }
    
    def __init__(self, oParent, dShape, dCanShape):
        combdialog.CCombDialog.__init__(self, oParent)
        self.Capture(1, 0)
        self.m_oTableView = CReadyDingYueTbViewPart(self.GetTableView(), misc.Functor(self.OnClickItem))
        self.m_bSelect = False
        self.m_dShape = dShape
        self.m_dNowShape = misc.DeepCopy(dShape)
        self.m_dCanShape = dCanShape
        self.m_iCurSelectNum = 0
        self.m_iTotalCost = 0
        self.InitTips()

    
    def InitTips(self):
        self.m_iCurSelectNum = 0
        self.m_iTotalCost = 0
        for iShape in self.m_dShape:
            self.m_iCurSelectNum += 1
            self.m_iTotalCost += self.m_dShape[iShape].get('iNum') * self.m_dCanShape[iShape].get('iPrice')
        
        self.UpdateTips()

    
    def RefreashWindow(self, dShape, dCanShape):
        self.m_dShape = dShape
        self.m_dNowShape = misc.DeepCopy(dShape)
        self.m_dCanShape = dCanShape
        self.UpdateDingYueItem()

    
    def GetTableView(self):
        return self.GetObject('tbview_book')

    
    def SortItem(self, dData):
        if permission.IsOpenGoldShopSimplify():
            iSortList = [
                72818,
                73798,
                73801,
                73799,
                73800,
                70662,
                72264,
                25431,
                72262,
                72827,
                25707]
        else:
            iSortList = [
                72857,
                72858,
                72859,
                72860,
                72861,
                72862,
                72863,
                72864,
                72818,
                70662,
                72264,
                25431,
                72262,
                72827,
                25707]
        return iSortList.index(dData['iShape'])

    
    def UpdateDingYueItem(self):
        oTableView = self.GetTableView()
        dItemList = []
        for iShape, dInfo in self.m_dCanShape.iteritems():
            dItem = { }
            dOwnItem = self.m_dShape.get(iShape, { })
            dItem['iShape'] = iShape
            dItem['sName'] = itemdata.GetData(iShape)[0]
            dItem['iPrice'] = str(dInfo['iPrice'])
            dItem['sTips'] = dInfo.get('sDesc', '')
            dItem['bSelect'] = bool(dOwnItem)
            dItem['iNowCount'] = dOwnItem.get('iNum', '')
            dItem['iDiscount'] = dInfo.get('iDiscount', 0)
            dItem['iPos'] = dInfo.get('iPos', 0)
            dItemList.append(dItem)
        
        dItemList.sort(key = misc.Functor(self.SortItem))
        oTableView.ReloadWithDiffSourceDict(dItemList)

    
    def DoDingYue(self):
        import usermacro
        if self.m_bSelect:
            C2SSendDingYueShape(self.m_dShape)
            if len(self.m_dShape) > 0:
                usermacro.PROMPT_MSG('\xa4w\xa6\xa8\xa5\\\xadq\xbe\\')
                self.CloseUI()
            else:
                usermacro.PROMPT_MSG('\xa4w\xa6\xa8\xa5\\\xa8\xfa\xae\xf8\xadq\xbe\\')
                C2SRequestDingYueShape()
        else:
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xc4\xbf\xef\xa6P\xb7N\xaaA\xb0\xc8\xb1\xf8\xb4\xda')

    
    def SetItmeCount(self, iShape, iCount):
        iPrice = self.m_dCanShape[iShape].get('iPrice', 0)
        if iShape in self.m_dShape:
            if iCount:
                self.m_iTotalCost += (iCount - self.m_dShape[iShape]['iNum']) * iPrice
                self.m_dShape[iShape]['iNum'] = iCount
            else:
                self.m_iCurSelectNum -= 1
                self.m_iTotalCost -= iPrice * self.m_dShape[iShape].get('iNum', 0)
                del self.m_dShape[iShape]
        elif iCount:
            self.m_dShape[iShape] = {
                'iNum': iCount,
                'iShape': iShape,
                'iType': self.m_dCanShape[iShape]['iType'] }
            self.m_iCurSelectNum += 1
            self.m_iTotalCost += iPrice * iCount
        
        self.UpdateDingYueItem()
        self.UpdateTips()

    
    def UpdateTips(self):
        self.GetObject('text_tips_5').ReplaceText({
            '$num': str(self.m_iCurSelectNum),
            '$money': str(self.m_iTotalCost) })

    
    def OnClickItem(self, iItemShape, iType = 0):
        dOwnItem = self.m_dShape.get(iItemShape, { })
        dCanItem = self.m_dCanShape[iItemShape]
        iMaxCount = dCanItem.get('iNum', 1)
        iNowCount = dOwnItem.get('iNum', 0)
        if iMaxCount == 1:
            if iNowCount:
                if iType in (0, 2):
                    self.SetItmeCount(iItemShape, 0)
                else:
                    usermacro.PROMPT_MSG('\xb8\xd3\xa4\xba\xaee\xb3\xcc\xa6h\xa5u\xaf\xe0\xadq\xbe\\1\xad\xd3\xa1A\xb5L\xaak\xad\xd7\xa7\xef\xbc\xc6\xb6q')
            elif iType in (0, 2):
                self.SetItmeCount(iItemShape, 1)
            
        elif iNowCount:
            if iType in (0, 2):
                self.SetItmeCount(iItemShape, 0)
                return None
            
        elif iType in (0, 2):
            pass
        else:
            self.SetItmeCount(iItemShape, 0)
            return None
        if iNowCount == 0:
            iNowCount = iMaxCount
        
        dItem = { }
        dItem['iShape'] = iItemShape
        dItem['sName'] = itemdata.GetData(iItemShape)[0]
        dItem['sTips'] = dCanItem.get('sDesc', '')
        dItem['bSelect'] = None
        dItem['iMaxCount'] = iMaxCount
        dItem['iNowCount'] = iNowCount
        dItem['iNowCount'] = iNowCount
        dItem['iDiscount'] = dCanItem.get('iDiscount', 0)
        dItem['iPrice'] = dCanItem.get('iPrice', 0)
        CReadyDingYueForSetNumDlg.OpenUI(dItem, misc.Functor(self.OnSetNumCB))

    
    def CloseWindow(self):
        if self.m_dShape != self.m_dNowShape:
            commondialog.ShowMessageBox('\xb7\xed\xabe\xa6\xb3\xadq\xbe\\\xa4\xba\xaee\xad\xd7\xa7\xef\xa5\xbc\xbdT\xa9w\xa1A\xacO\xa7_\xc3\xf6\xb3\xac\xac\xc9\xad\xb1\xa9\xf1\xb1\xf3\xad\xd7\xa7\xef\xa1H', ('\xa9\xf1\xb1\xf3\xad\xd7\xa7\xef', '\xa7\xda\xa6A\xb7Q\xb7Q'), misc.Functor(self.CloseUI), None)
        else:
            self.CloseUI()

    
    def OnSetNumCB(self, iShape, iCount):
        self.SetItmeCount(iShape, iCount)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.m_bSelect = not (self.m_bSelect)
            self.GetObject('btn_choose').SetSelect(self.m_bSelect)
        elif iMsgID == 3:
            self.DoDingYue()
        



class CReadyDingYueTbViewPart(object):
    
    def __init__(self, oTbview, oClickCB):
        self.m_oTbview = oTbview
        self.m_oClickCB = oClickCB
        self.InitTableView()

    
    def GetTbAllView(self):
        return self.m_oTbview

    
    def InitTableView(self):
        self.GetTbAllView().SetDelegateNewCellOfData(misc.Functor(self.OnDelegateNewCellOfData))
        self.GetTbAllView().SetDelegateUpdateCellOfData(misc.Functor(self.OnDelegateUpdateCellOfData))
        self.GetTbAllView().SetDelegateAlignOfData(misc.Functor(self.OnDelegateAlignOfData))

    
    def OnDelegateNewCellOfData(self, oParent, dData):
        oCell = CDingYueItem(oParent)
        oCell.SetItemInfo(dData)
        oCell.SetSelectCallBack(self.m_oClickCB)
        return oCell

    
    def OnDelegateUpdateCellOfData(self, oCell, dData, bReUes):
        if bReUes:
            oCell.SetItemInfo(dData)
        

    
    def OnDelegateAlignOfData(self, dData):
        return interface.ALIGN_CENTER_MIDDLE



class CDingYueItem(combdialog.CCombSubWnd):
    sUIName = 'dialog/itembill/itembill_new/itembill_bookitem.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_oParent = oParent
        self.m_bSelect = False
        self.m_iShape = None
        self.m_sTips = None
        self.m_oBg = None
        self.m_oSelectCallBack = None
        self.m_oBg = self.GetObject('lst_goods')
        self.SetPassScrollingMessagesUp(True)
        self.SetIgnoreEsc(True)

    
    def SetItemInfo(self, dInfo):
        import item
        iShape = dInfo['iShape']
        sName = dInfo['sName']
        iPrice = dInfo['iPrice']
        sTips = dInfo['sTips']
        bSelect = dInfo['bSelect']
        iDiscount = dInfo['iDiscount']
        self.m_iShape = iShape
        self.m_sTips = sTips
        self.m_oIconList = []
        oIcon = item.CreateItem44StretchImage(self.GetObject('loc_item'), iShape)
        self.m_oIconList.append(oIcon)
        self.GetObject('text_itemname').SetText(sName)
        self.GetObject('text_sg').ReplaceText({
            '$num': str(iPrice) })
        self.GetObject('text_num').SetText(str(dInfo.get('iNowCount', '')))
        sPaht = GetDiscountNum(iDiscount)
        if iDiscount and sPaht:
            self.GetObject('img_discount').SetPath(sPaht, interface.UIPath)
            self.SetShowObject('img_discoun', True)
        else:
            self.SetShowObject('img_discoun', False)
        self.SetSelect(bSelect)

    
    def SetSelectCallBack(self, func):
        self.m_oSelectCallBack = func

    
    def CreateTips(self):
        iKey = self.GetItemKeyByShape()
        (sName, sInfo) = itemdata.GetData(self.m_iShape)
        self.m_oTips = wrapinterface.CItemTips(self.m_iShape, '', sName, sInfo, self.m_sTips, key = iKey, charcount = 33)
        self.m_oTips.SetOwner(self)

    
    def GetItemKeyByShape(self):
        import item
        if self.m_iShape in (itemdefine.ID_ITEM_VIP,):
            return 0
        elif self.m_iShape in (itemdefine.ID_JINGPING_SUMMON_BOOK_ITEM,):
            return item.MARK_JINGPIN
        else:
            return item.MARK_BOUND

    
    def SetSelect(self, bSelect):
        if bSelect is None:
            self.SetShowObject('btn_select', False)
        else:
            self.SetShowObject('btn_select', True)
            self.GetObject('btn_select').SetSelect(bSelect)

    
    def GetShape(self):
        return self.m_iShape

    
    def LeftUp(self):
        combdialog.CCombSubWnd.LeftUp(self)
        self.m_oTips = None
        if self.m_oSelectCallBack:
            pass
        self.m_oSelectCallBack(self.m_iShape, 0)

    
    def RightUp(self):
        combdialog.CCombSubWnd.RightUp(self)
        if self.m_oSelectCallBack:
            pass
        self.m_oSelectCallBack(self.m_iShape, 1)

    
    def Enter(self):
        oImage = self.m_oBg.GetImage(0, 0)
        oImage.SetFrame(2)
        self.CreateTips()

    
    def Leave(self):
        oImage = self.m_oBg.GetImage(0, 0)
        oImage.SetFrame(0)
        self.m_oTips = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            if self.m_oSelectCallBack:
                pass
            self.m_oSelectCallBack(self.m_iShape, 2)
        



class CSummonGiftDialog(combdialog.CCombDialog):
    ITEM_LIST = [
        73500,
        73497,
        72224,
        73511]
    ITEM_REDBAG = 73433
    
    def __init__(self, iBuyID, oCloseFunc):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog4/itembill/itembill_new/itembill_summongift.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_oCloseFunc = misc.Functor(oCloseFunc)
        self.m_oIconList = []
        self.m_iBuyID = iBuyID
        for iIndex in xrange(5):
            oHloc = self.GetObject('hloc_item%s' % (iIndex + 1))
            if oHloc:
                oHloc.SetEnterCB(misc.Functor(self.OnEnterCB, iIndex))
                oHloc.SetLeaveCB(misc.Functor(self.OnLeaveCB))
                continue
        

    
    def SetCanBuy(self, bCanBuy):
        oBuyBtn = self.GetObject('btn_upgrade')
        if bCanBuy:
            oBuyBtn.FakeEnable(True)
            oBuyBtn.SetText('\xc1\xca\xb6R')
        else:
            oBuyBtn.FakeEnable(False, '\xb1z\xa4w\xc1\xca\xb6R\xaf\xab\xc3~\xc2\xa7\xa5]\xa1A\xb5L\xaak\xc4~\xc4\xf2\xc1\xca\xb6R')
            oBuyBtn.SetText('\xa4w\xc1\xca\xb6R')

    
    def OnEnterCB(self, iCBKey):
        import itemdata
        import tipsclosemgr
        if iCBKey == 4:
            iShape = self.ITEM_REDBAG
        else:
            iShape = self.ITEM_LIST[iCBKey]
        (sName, sDesc) = itemdata.GetData(iShape)
        tipsclosemgr.Regist(wrapinterface.CItemTips(iShape, None, sName, sDesc, key = 64, parent = self, charcount = 33))

    
    def OnLeaveCB(self):
        import tipsclosemgr
        tipsclosemgr.CheckClose()

    
    def InitDlg(self):
        import item
        self.m_oIconList = []
        for iIndex, iShape in enumerate(self.ITEM_LIST):
            oLoc = self.GetObject('loc_reward%d' % (iIndex + 1))
            (iX, iY) = oLoc.GetPos()
            iZ = oLoc.GetZ()
            oIcon = item.CreateItem44StretchImage(self, iShape)
            oIcon.SetScale(1.5)
            oIcon.SetPos(iX, iY)
            oIcon.SetZ(iZ)
            self.m_oIconList.append(oIcon)
        

    
    def CloseWindow(self):
        self.m_oCloseFunc()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            C2SBuyCommonIB(self.m_iBuyID, 1)
            self.CloseWindow()
        



class CReadyDingYueForSetNumDlg(combdialog.CCombDialog):
    sUIName = 'dialog/itembill/itembill_new/itembill_minibook.dlg'
    dOpenUIConfig = {
        'KEY_PARENT': 'CapturePanel',
        'KEY_ALIGN': -1 }
    
    def __init__(self, oParent, dShowInfo, oCloseFunc):
        combdialog.CCombDialog.__init__(self, oParent)
        self.Capture(1, 0)
        self.m_dShowInfo = dShowInfo
        self.m_oCloseFunc = misc.Functor(oCloseFunc)
        self.m_oCell = None
        self.m_oBookAmountEdit = None
        self.m_iShape = dShowInfo['iShape']
        self.m_iCount = dShowInfo['iNowCount']
        self.m_iMaxCount = dShowInfo['iMaxCount']
        self.m_iPrice = dShowInfo['iPrice']
        self.InitDingYueItem()
        self.CreateBookAmountEdit()
        self.ResetPos()

    
    def ResetPos(self):
        '''
\t\t\xb8\xd3\xac\xc9\xad\xb1\xbcu\xa5X\xae\xc9\xac\xc9\xad\xb1btn_buy\xa5\xbf\xa6n\xb8m\xa9\xf3\xb9\xab\xbc\xd0\xa4\xa7\xa4W
\t\t:param self:
\t\t:return:
\t\t'''
        import cursor
        oBtnBuy = self.GetObject('btn_buy')
        (iBtnPosX, iBtnPosY) = oBtnBuy.GetScreenPos()
        (iMousePosX, iMousePosY) = cursor.GetCursorPos()
        iDisX = iMousePosX - iBtnPosX
        iDisY = iMousePosY - iBtnPosY
        (iCurPosX, iCurPosY) = self.GetPos()
        iEndPosX = iCurPosX + iDisX
        iEndPosY = iCurPosY + iDisY
        (iBtnSizeW, iBtnSizeH) = oBtnBuy.GetSize()
        self.SetPos(iEndPosX - iBtnSizeW / 2, iEndPosY - iBtnSizeH / 2)

    
    def InitDingYueItem(self):
        self.m_oCell = CDingYueItem(self.GetObject('box_item'))
        dShowInfo = misc.DeepCopy(self.m_dShowInfo)
        dShowInfo['iNowCount'] = dShowInfo['iMaxCount']
        self.m_oCell.SetItemInfo(dShowInfo)

    
    def CreateBookAmountEdit(self):
        import wrapedit
        oTxtNum = self.GetObject('txt_num')
        self.m_oBookAmountEdit = combmacro.CEDIT(wrapedit.CLimitNumberEdit, 'txt_num', self, oTxtNum.GetColor(), oTxtNum.GetFont())
        self.m_oBookAmountEdit.SetTextAlign(oTxtNum.GetAlign())
        self.m_oBookAmountEdit.SetMaxNum(self.m_iMaxCount)
        self.m_oBookAmountEdit.Active(True)
        self.m_oBookAmountEdit.SetText(str(self.m_iCount))
        self.m_oBookAmountEdit.SetSelect(0, 999)

    
    def OnLimitEditChange(self, oEdit):
        sCount = oEdit.GetText()
        if sCount:
            self.m_iCount = int(sCount)
        else:
            self.m_iCount = 0
        self.GetObject('txt_price').SetText(str(self.m_iCount * self.m_iPrice))

    
    def OnAddCount(self, iCount):
        self.m_iCount += iCount
        self.m_iCount = max(0, min(self.m_iMaxCount, self.m_iCount))
        self.m_oBookAmountEdit.SetText(str(self.m_iCount))
        self.GetObject('txt_price').SetText(str(self.m_iCount * self.m_iPrice))

    
    def OnConfirm(self):
        if self.m_iCount:
            if self.m_oCloseFunc:
                pass
            self.m_oCloseFunc(self.m_iShape, self.m_iCount)
            self.CloseUI()
        else:
            usermacro.PROMPT_MSG('\xadq\xbe\\\xbc\xc6\xb6q\xa6\xdc\xa4\xd6\xac\xb01')

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseUI()
        elif iMsgID == 2:
            self.OnConfirm()
        elif iMsgID == 3:
            self.OnAddCount(-1)
        elif iMsgID == 4:
            self.OnAddCount(1)
        
        iMsgID -= interface.RIGHT_BUTTON_MESSAGE
        if iMsgID == 3:
            self.OnAddCount(-100)
        elif iMsgID == 4:
            self.OnAddCount(100)
        



class CSubScribeRedDot(dlgreddot.CRedDotWidget):
    
    def __init__(self, oNode, oParent = None):
        dlgreddot.CRedDotWidget.__init__(self, oParent, oNode)
        self.m_oTips = None

    
    def UpdateRenderParam(self, iPosX):
        self.m_iPosX = iPosX
        self.RenderImg()

    
    def RenderImg(self):
        if not self.m_iStatus:
            self.m_oTips = None
        else:
            self.m_oTips = wrapinterface.CCombTipsBox(self.m_oParent(), '\xadq\xbe\\\xa4\xba\xaee\xa6\xb3\xa7\xf3\xb7s\xa1A\xbd\xd0\xc2I\xc0\xbb\xacd\xac\xdd', 6, self.m_iPosX, 0, 130, 60, -20, 0)
            self.m_oTips.SetZ(dlgreddot.RED_POINT_Z)



def C2SAskOpenShopPage(iPage):
    netobj = net.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(iPage, 1)
    netobj.PacketSend()


def C2SAskOpenConcessShop():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(0, 1)
    net.g_Net.PacketSend()


def CSGSAskOpenServerShop():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(1, 1)
    net.g_Net.PacketSend()


def C2SAskSpringShop():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(32, 1)
    net.g_Net.PacketSend()


def C2SBuyCommonIB(ipos, amount):
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(3, 1)
    net.g_Net.PacketAddI(ipos, 1)
    net.g_Net.PacketAddI(amount, 2)
    net.g_Net.PacketSend()


def CSGSAskBuyTimeCardShop(iCurrency):
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(5, 1)
    net.g_Net.PacketAddI(iCurrency, 1)
    net.g_Net.PacketSend()


def CSGSDrawEncouragementShop():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(7, 1)
    net.g_Net.PacketSend()


def CSGSPointChangeWorldContributeShop():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(8, 1)
    net.g_Net.PacketSend()


def CSGSAskContributeVipShop(iSub):
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(9, 1)
    net.g_Net.PacketAddI(iSub, 1)
    net.g_Net.PacketSend()


def CSGSAskOpenSellCard(iCurrency):
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(12, 1)
    net.g_Net.PacketAddI(iCurrency, 1)
    net.g_Net.PacketSend()


def CSGSAskOpenLookBuyPosition():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(13, 1)
    net.g_Net.PacketSend()


def CSGSAskOpenStripping(iCurrency):
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(14, 1)
    net.g_Net.PacketAddI(iCurrency, 1)
    net.g_Net.PacketSend()


def C2SClickBuy():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(28, 1)
    net.g_Net.PacketSend()


def C2SClickMobile():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(29, 1)
    net.g_Net.PacketSend()


def C2SClickPhone():
    net.g_Net.PacketPrepare(net.C2GS_PLAYER_IB)
    net.g_Net.PacketAddI(30, 1)
    net.g_Net.PacketSend()


def C2SAskOpenItemBill(iFrom):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(iFrom, 1)
    netobj.PacketSend()


def C2SAskOpenItemBillByShape(iShape):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(iShape, 4)
    netobj.PacketSend()


def C2SRequestDingYueShape():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(33, 1)
    netobj.PacketSend()


def C2SSendDingYueShape(dShape):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(34, 1)
    netobj.PacketAddI(len(dShape), 1)
    for iShape, dItem in dShape.iteritems():
        netobj.PacketAddI(iShape, 4)
        netobj.PacketAddI(dItem['iNum'], 2)
        netobj.PacketAddI(dItem['iType'], 1)
    
    netobj.PacketSend()


def C2SRefreshDiscount():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_PLAYER_IB)
    netobj.PacketAddI(35, 1)
    netobj.PacketSend()


def SetLastSelectData(iPos, iAmount, iPage, iShape):
    global g_LastSelectData
    g_LastSelectData = {
        'iPos': iPos,
        'iAmount': iAmount,
        'iPage': iPage,
        'iShape': iShape }


def UpdateLastSelectData(sKey, iData):
    g_LastSelectData[sKey] = iData


def GetLastSelectData():
    return g_LastSelectData
