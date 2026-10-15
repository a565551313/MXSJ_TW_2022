# pycdc 交叉复核产物 · script.fls entry 877
# co_filename(原始)='script/mxgame/auction/dlgauctionpreview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_877.pyc (Python 2.5)

import time
import auctiondata
import auctiondefines
import avatarfrmdata
import charpath
import combdialog
import combmacro
import dlggetinfo
import dlgpay
import dlgshiwu
import hero
import interface
import item
import itemdata
import itemdefine
import misc
import petdata
import tipsclosemgr
import usermacro
import walker
import wrapinterface
g_lHasTips = None
g_iUseLvList = None

def ModuleReset():
    global g_lHasTips, g_iUseLvList
    g_lHasTips = None
    g_iUseLvList = None


class CAuctionPreviewPart(combdialog.CCombSubWnd):
    UIPOSMAP = {
        'txt_sg': 'txt_myprice',
        'img_sg': 'img_sg2',
        'img_sgbg': 'img_myprice',
        'txt_mysg': 'txt_myprice_value' }
    UI_BUYNEED = ('btn_bid', 'btn_auto', 'txt_myprice', 'img_sg2', 'img_myprice', 'txt_myprice_value')
    UI_SGICON = ('img_sg1', 'img_sg2', 'img_sg')
    
    def __init__(self, oParent, iPageType):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_view.dlg')
        self.m_oPhotoPart = None
        self.m_bIsCash = False
        self.m_bCanBuy = None
        self.m_bIsExtensionTime = False
        self.m_bIsBook = False
        self.m_iPointSave = 0
        self.m_iPageType = iPageType
        self.m_bEnghouMoney = 0
        self.m_bLastAuto = False
        self.m_dItemData = { }
        self.m_bCanEditCanCB = True
        self.m_iUseLvList = None
        hero.AddRefreshCallbackNotFirstCB(id(self), ('m_Cash', 'm_Gold'), self.OnCashChange)
        self.InitEdit()
        if self.GetObject('text_addprice1') and self.GetObject('text_addprice2'):
            self.GetObject('text_addprice1').ReplaceText({
                '$price1': '' })
            self.GetObject('text_addprice2').ReplaceText({
                '$price2': '' })
        
        self.SetShowObject('btn_normalrule', iPageType == auctiondefines.PAGE_NORMAL)
        self.SetShowObject('btn_titlerule', iPageType == auctiondefines.PAGE_NUMBER)
        self.SetShowObject('text_tips_cash', False)
        self.SetShowObject('text_tips_sg', False)
        self.SetShowObject('btn_cashtips', False)
        self.SetShowObject('btn_book', False)
        self.SetShowObject('btn_booktips', False)
        self.SetRuleShow(False)
        LoadLocalData()

    
    def SetData(self, dItemData, iPointSave):
        iShape = dItemData['shape']
        iType = dItemData['iType']
        iPayType = dItemData['buyType']
        iCurPrice = dItemData.get('curPrice', 0)
        iBasePrice = dItemData.get('basePrice', 0)
        iAmount = dItemData.get('amount', 1)
        sName = dItemData.get('name', '')
        bCanBuy = dItemData.get('bCanBuy', 0)
        self.m_dItemData = dItemData
        self.m_bIsExtensionTime = dItemData.get('bIsOuttime', False)
        self.m_bIsBook = dItemData.get('bIsBook', False)
        self.m_iPointSave = iPointSave
        self.SetIcon(iType, dItemData)
        self.SetName(iType, iShape, iAmount, sName)
        self.SetBuyType(iPayType == auctiondefines.PAYTYPE_CASH)
        self.SetPrice(iCurPrice, iBasePrice)
        self.SetCanBuy(bCanBuy)
        self.RefreshPointSave()
        self.OnEditChange(None, False)

    
    def InitEdit(self):
        if self.GetObject('loc_edit'):
            sName = 'loc_edit'
        else:
            sName = 'txt_myprice_value'
        self.m_oEdtNum = combmacro.CEDIT(wrapinterface.CNumberEditEx, sName, self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oEdtNum.SetLimit(10)
        self.m_oEdtNum.Active(True)
        self.m_oEdtNum.SetShow(False)

    
    def SetCanBuy(self, bCanBuy):
        if bCanBuy != self.m_bCanBuy:
            self.m_bCanBuy = bCanBuy
            for sName in self.UI_BUYNEED:
                self.SetShowObject(sName, bCanBuy)
            
            oBookBtn = self.GetObject('btn_book')
            if oBookBtn:
                if bCanBuy:
                    oBookBtn.SetShow(False)
                else:
                    oBookBtn.SetShow(True)
            
            self.SetShowObject('btn_booktips', not bCanBuy)
            for sName in self.UIPOSMAP:
                oWidget = self.GetObject(sName)
                oWidgetSwitch = self.GetObject(self.UIPOSMAP[sName])
                (iX1, iY1) = oWidget.GetPos()
                (iX2, iY2) = oWidgetSwitch.GetPos()
                if bCanBuy:
                    oWidget.SetPos(iX1, max(iY1, iY2))
                    oWidgetSwitch.SetPos(iX2, min(iY1, iY2))
                    continue
                oWidget.SetPos(iX1, min(iY1, iY2))
                oWidgetSwitch.SetPos(iX2, max(iY1, iY2))
            
            if bCanBuy:
                self.GetObject('txt_price').SetText('\xb7\xed\xabe\xa5X\xbb\xf9')
            else:
                self.GetObject('txt_price').SetText('\xaa\xec\xa9l\xbb\xf9\xae\xe6')
        
        oBookBtn = self.GetObject('btn_book')
        if oBookBtn:
            if self.m_bIsBook:
                oBookBtn.SetText('\xa8\xfa\xae\xf8\xb9w\xac\xf9')
            else:
                oBookBtn.SetText('\xb9w\xac\xf9\xa9\xe7\xbd\xe6')
        
        self.m_oEdtNum.Active(self.m_bCanBuy)
        self.m_oEdtNum.SetShow(self.m_bCanBuy)

    
    def SetName(self, iType, iShape, iAmount, sName):
        if iType == auctiondefines.VIEWTYPE_NUMBER:
            sName = '\xe8\xb0\xb8\xb9\xc2\xa7\xb2\xb0'
        elif iType == auctiondefines.VIEWTYPE_AVATARFRM:
            sName = itemdata.GetData(iShape)[0]
        
        if not sName:
            if iType == auctiondefines.VIEWTYPE_SUMMON:
                sName = petdata.GetData(iShape)['name']
            else:
                sName = itemdata.GetData(iShape)[0]
        
        if iAmount > 1:
            sName = '%s\xa1\xd1%d' % (sName, iAmount)
        
        self.GetObject('txt_itemname').SetText(sName)

    
    def SetRuleShow(self, bShow):
        self.SetShowObject('text_rule', bShow)
        for sName in ('text_addprice1', 'text_addprice2'):
            self.SetShowObject(sName, not bShow)
        
        self.RefreshTipsBtnShow(bForceNotShow = bShow)
        if bShow:
            self.GetObject('txt_itemname').SetText('\xe8\xb0\xb8\xb9\xa9\xe7\xbd\xe6\xb3W\xabh')
        elif self.GetObject('txt_itemname').GetText() == '\xe8\xb0\xb8\xb9\xa9\xe7\xbd\xe6\xb3W\xabh':
            self.GetObject('txt_itemname').SetText('')
        

    
    def SetIcon(self, iType, dItemData):
        if iType == auctiondefines.VIEWTYPE_SUMMON:
            oPart = CAuctionPreviewSummon(self)
        elif iType == auctiondefines.VIEWTYPE_HERO:
            oPart = CAuctionPreviewHeroFairy(self)
        elif iType == auctiondefines.VIEWTYPE_NUMBER:
            oPart = CAuctionPreviewHeroNumber(self)
        elif iType == auctiondefines.VIEWTYPE_AVATARFRM:
            oPart = CAuctionPreviewAvatarFrm(self)
        elif iType == auctiondefines.VIEWTYPE_HORSESKIN:
            oPart = CAuctionPreviewHorseSkin(self)
        else:
            oPart = CAuctionPreviewItem(self)
        oPart.SetData(dItemData)
        (iX, iY) = self.GetObject('loc_photo').GetPos()
        oPart.SetPos(iX, iY)
        self.m_oPhotoPart = oPart

    
    def SetBuyType(self, bIsCash):
        if self.m_bIsCash != bIsCash:
            self.SetShowObject('text_tips', bIsCash)
            for sName in self.UI_SGICON:
                oIcon = self.GetObject(sName)
                (iX, iY) = oIcon.GetPos()
                if bIsCash:
                    oIcon.SetPath('combdialog3/\xd4\xd3\xcd\xbc/\xcf\xd6\xbd\xf0/xianjin.png')
                    oIcon.SetPos(iX - 3, iY - 3)
                    continue
                oIcon.SetPath('combdialog3/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xb9\xb1\xcf\xd7\xcd\xbc\xb1\xea/gongxian.png')
                oIcon.SetPos(iX + 3, iY + 3)
            
            if bIsCash:
                self.GetObject('txt_sg').SetText('\xb7\xed\xabe\xb2{\xaa\xf7')
            else:
                self.GetObject('txt_sg').SetText('\xa5@\xac\xc9\xb0^\xc4m')
            self.m_bIsCash = bIsCash
        
        self.SetShowObject('text_tips_cash', bIsCash)
        self.SetShowObject('text_tips_sg', not bIsCash)
        self.OnCashChange(False)
        if self.GetObject('text_addprice1') and self.GetObject('text_addprice2'):
            if self.m_bIsCash:
                self.GetObject('text_addprice1').ReplaceText({
                    '$price1': '25,0000' })
                self.GetObject('text_addprice2').ReplaceText({
                    '$price2': '75,0000' })
            else:
                self.GetObject('text_addprice1').ReplaceText({
                    '$price1': '100' })
                self.GetObject('text_addprice2').ReplaceText({
                    '$price2': '300' })
            if self.m_bIsExtensionTime:
                self.GetObject('text_addprice1').SetColor(11842740)
                self.GetObject('text_addprice2').SetColor(16711680)
            else:
                self.GetObject('text_addprice1').SetColor(4210829)
                self.GetObject('text_addprice2').SetColor(11842740)
            self.RefreshTipsBtnShow()
        elif self.GetObject('text_pricetips'):
            if self.m_bIsCash:
                iBase = 10000
            else:
                iBase = 100
            if self.m_bIsExtensionTime:
                sTimename = '\xb6\xb6\xa9\xb5\xb4\xc1'
                sColor = '#R'
            else:
                sTimename = ''
                sColor = interface.ReplaceYellow('#Y')
            self.GetObject('text_pricetips').SetText('\xb5\xf9\xa1G%s\xa5X\xbb\xf9\xae\xc9\xa1A\xa5[\xbb\xf9\xb4T\xab\xd7\xbb\xdd\xadn\xa6b%s%s#n\xa5H\xa4W\xa1A\xa8\xc3\xa5B\xac\xb0%s\xaa\xba\xbe\xe3\xbc\xc6\xad\xbf' % (sTimename, sColor, self.GetMoneyStr(self.GetAddPrice()), self.GetMoneyStr(iBase)))
        

    
    def SetPrice(self, iCurPrice, iBasePrice):
        if iCurPrice:
            iAddPrice = self.GetAddPrice()
            self.m_oEdtNum.SetText('%d' % (iCurPrice + iAddPrice))
            self.GetObject('txt_curprice').SetText(str(iCurPrice))
        else:
            self.m_oEdtNum.SetText('%d' % iBasePrice)
            self.GetObject('txt_curprice').SetText(str(iBasePrice))

    
    def RefreshTipsBtnShow(self, bForceNotShow = False):
        if bForceNotShow:
            self.SetShowObject('btn_addcashtips', False)
            self.SetShowObject('btn_addsgtips', False)
        else:
            self.SetShowObject('btn_addcashtips', self.m_bIsCash)
            self.SetShowObject('btn_addsgtips', not (self.m_bIsCash))

    
    def GetAddPrice(self):
        iAdd = self.GetSingleAddPrice()
        if self.m_bIsExtensionTime:
            return iAdd
        else:
            return iAdd

    
    def GetSingleAddPrice(self):
        if 'iMinAddPrice' in self.m_dItemData:
            return self.m_dItemData['iMinAddPrice']
        
        if self.m_bIsCash:
            return 250000
        else:
            return 100

    
    def RefreshPointSave(self):
        oWidget = self.GetObject('btn_cashtips')
        if not oWidget:
            return None
        
        if self.m_bIsCash and self.m_bCanBuy:
            oWidget.SetShow(True)
            oWidget.ReplaceTips({
                '$pointsave': self.GetMoneyStr(self.m_iPointSave) })
        else:
            oWidget.SetShow(False)

    
    def OnCashChange(self, bCheck = True):
        if self.m_bIsCash:
            iValue = hero.GetProp('m_Cash')
        else:
            iValue = hero.GetProp('m_Gold')
        self.GetObject('txt_mysg').SetText(str(iValue))
        if self.m_dItemData and bCheck:
            iNowNum = self.m_oEdtNum.GetNumber()
            iCurPrice = self.m_dItemData.get('curPrice', 0)
            iBasePrice = self.m_dItemData.get('basePrice', 0)
            iMyPrice = self.m_dItemData.get('myPrice', 0)
            if self.m_bIsCash:
                iAllMoney = iValue + self.m_iPointSave + iMyPrice
            else:
                iAllMoney = iValue + iMyPrice
            if iCurPrice:
                iCost = iCurPrice + self.GetAddPrice()
            else:
                iCost = iBasePrice
            if iCost < iCost:
                pass
            elif iCost <= iAllMoney:
                self.SetPrice(iCurPrice, iBasePrice)
                self.OnEditChange(None, False)
            
        

    
    def OnEditChange(self, oEdit, bTips = True):
        if not self.m_dItemData:
            return None
        
        if not self.m_bCanEditCanCB:
            return None
        
        iMyPrice = self.m_dItemData.get('myPrice', 0)
        iCurPrice = self.m_dItemData.get('curPrice', 0)
        iPrice = self.m_oEdtNum.GetNumber()
        (iMaxValue, iBase) = (0, 1)
        if iPrice > iCurPrice * 10 and iCurPrice != 0:
            if bTips:
                usermacro.PROMPT_MSG('\xa8C\xa6\xb8\xbb\xf9\xae\xe6\xa4\xa3\xaf\xe0\xb6W\xb9L\xb7\xed\xabe\xbb\xf9\xae\xe6\xaa\xba10\xad\xbf')
            
            iMaxValue = iCurPrice * 10
        
        if self.m_bIsCash:
            iHeroCash = hero.GetProp('m_Cash', 0)
            if iMaxValue == 0 or iMaxValue > iHeroCash + self.m_iPointSave + iMyPrice:
                iMaxValue = iHeroCash + self.m_iPointSave + iMyPrice
            
            iBase = 10000
        else:
            iHeroGold = hero.GetProp('m_Gold', 0)
            if iMaxValue == 0 or iMaxValue > iHeroGold + iMyPrice:
                iMaxValue = iHeroGold + iMyPrice
            
            iBase = 100
        if iPrice > iMaxValue:
            self.m_bCanEditCanCB = False
            self.m_oEdtNum.SetText('%d' % (iMaxValue / iBase) * iBase)
            self.m_bCanEditCanCB = True
        

    
    def CheckPrice(self, iPrice, iBasePrice, iCurPrice, iMyPrice, iMostPrice):
        if iMostPrice:
            usermacro.PROMPT_MSG('\xb1z\xb7\xed\xabe\xa9e\xb0U\xa4F\xa6\xdb\xb0\xca\xc4v\xa9\xe7\xa1A\xa4\xa3\xaf\xe0\xa5X\xbb\xf9')
            return None
        
        if not iCurPrice:
            iCurPrice = iBasePrice
            bCheckAdd = False
        else:
            bCheckAdd = True
        iAddPrice = self.GetAddPrice()
        if self.m_bIsCash:
            if iPrice > iMyPrice + hero.GetProp('m_Cash') + self.m_iPointSave:
                usermacro.PROMPT_MSG('\xb1z\xaa\xba\xaa\xf7\xbf\xfa\xa4\xa3\xa8\xac')
                return False
            
            if iPrice > 2100000000:
                usermacro.PROMPT_MSG('\xb1z\xbf\xe9\xa4J\xaa\xba\xaa\xf7\xbf\xfa\xb6W\xb9L\xa5i\xc4\xe2\xb1a\xaa\xba\xa4W\xad\xad')
                return False
            
            if (iPrice % 10000 or bCheckAdd) and iPrice - iCurPrice < iAddPrice:
                usermacro.PROMPT_MSG('\xa5[\xbb\xf9\xb4T\xab\xd7\xbb\xdd\xadn\xa6b%s\xb2{\xaa\xf7\xa5H\xa4W\xa1A\xa8\xc3\xa5B\xac\xb01,0000\xaa\xba\xbe\xe3\xbc\xc6\xad\xbf' % self.GetMoneyStr(iAddPrice))
                return False
            
            if iCurPrice >= iMyPrice + hero.GetProp('m_Cash') + self.m_iPointSave:
                usermacro.PROMPT_MSG('\xb7\xed\xabe\xb2{\xaa\xf7\xa4\xa3\xa8\xac')
                return False
            
        elif iPrice > iMyPrice + hero.GetProp('m_Gold'):
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa4\xa3\xa8\xac')
            return False
        
        if (iPrice % 100 or bCheckAdd) and iPrice - iCurPrice < iAddPrice:
            usermacro.PROMPT_MSG('\xa5[\xbb\xf9\xb4T\xab\xd7\xbb\xdd\xadn\xa6b%s\xa5@\xac\xc9\xb0^\xc4m\xa5H\xa4W\xa1A\xa8\xc3\xa5B\xac\xb0100\xaa\xba\xbe\xe3\xbc\xc6\xad\xbf' % self.GetMoneyStr(iAddPrice))
            return False
        
        if iCurPrice >= iMyPrice + hero.GetProp('m_Gold'):
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa4\xa3\xa8\xac')
            dlgpay.ShowForSelf()
            return False
        
        if iPrice < iCurPrice:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xaa\xba\xbb\xf9\xae\xe6')
            return False
        
        return True

    
    def GetTodayUseLvData(self):
        global g_iUseLvList
        if g_iUseLvList is None:
            g_iUseLvList = []
            oTime = time.localtime()
            sTime = '%s-%s-%s' % (oTime.tm_year, oTime.tm_mon, oTime.tm_mday)
            sHasTips = hero.GetPrivateData('Game', 'auctionlvtip')
            if sHasTips and '|' in sHasTips:
                (sRecordTime, sShapes) = sHasTips.split('|', 1)
                if sRecordTime == sTime:
                    for sShape in sShapes.split(','):
                        if sShape.isdigit():
                            g_iUseLvList.append(int(sShape))
                            continue
                    
                
            
        
        return g_iUseLvList

    
    def SaveTodayUseLvData(self):
        if g_iUseLvList is not None:
            oTime = time.localtime()
            sTime = '%s-%s-%s' % (oTime.tm_year, oTime.tm_mon, oTime.tm_mday)
            hero.SavePrivateData('Game', 'auctionlvtip', '%s|%s' % (sTime, ','.join(map(str, g_iUseLvList))))
        

    
    def CheckUseLv(self, oCB):
        import dlgnpc
        iShape = self.m_dItemData['shape']
        dItemData = auctiondata.GetSaleItemData(iShape)
        if dItemData:
            if hero.GetProp('m_Grade', 0) < dItemData['iLv']:
                if iShape not in self.GetTodayUseLvData():
                    dlgnpc.ShowClientDlg('\xa8\xcf\xa5\xce#Y%s#n\xbb\xdd\xadn\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xa1\xd9#Y%s\xaf\xc5#n\xa1A\xacO\xa7_\xa4\xb4\xadn\xa9\xe7\xbd\xe6\xa1H\nQ\xbdT\xbb{\xa5B\xa4\xa3\xa6A\xb4\xa3\xa5\xdc\nQ\xa8\xfa\xae\xf8' % (self.GetObject('txt_itemname').GetText(), dItemData['iLv']), '', misc.Functor(self.OnUseLvCB, oCB))
                    return False
                
            
        
        return True

    
    def OnUseLvCB(self, oCB, iMsgID):
        if iMsgID == 1 and self.m_dItemData:
            self.GetTodayUseLvData().append(self.m_dItemData['shape'])
            self.SaveTodayUseLvData()
            oCB()
        

    
    def GetMoneyStr(self, iPrice):
        if iPrice <= iPrice:
            pass
        elif iPrice < 100000000:
            return '%d,%04d' % (iPrice / 10000, iPrice % 10000)
        elif iPrice <= iPrice:
            pass
        elif iPrice < 0xE8D4A51000L:
            return '%d,%04d,%04d' % (iPrice / 100000000, iPrice / 10000 % 10000, iPrice % 10000)
        else:
            return '%d' % iPrice

    
    def DoBuy(self):
        import dlgnpc
        if not self.m_dItemData:
            return None
        
        iPrice = self.m_oEdtNum.GetNumber()
        if iPrice <= 0:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xbb\xf9\xae\xe6')
            return None
        
        if not self.CheckUseLv(misc.Functor(self.DoBuy)):
            return None
        
        data = self.m_dItemData
        iItemID = data['itemID']
        iItemShape = data['shape']
        iBasePrice = data['basePrice']
        iCurPrice = data['curPrice']
        iMyPrice = data['myPrice']
        iMostPrice = data['mostPrice']
        sItemName = data.get('name', '')
        if not self.CheckPrice(iPrice, iBasePrice, iCurPrice, iMyPrice, iMostPrice):
            return None
        
        if g_lHasTips is not None and (iItemID, sItemName) not in g_lHasTips and self.m_bIsExtensionTime:
            dlgnpc.ShowClientDlg('\xa6\xb9\xa9\xe7\xbd\xe6\xa4w\xb6i\xa4J#Y\xb6\xb6\xa9\xb5\xb4\xc1#n\xa1A\xb1N\xb4\xa3\xa4\xc9#R\xb3\xcc\xa7C\xa5[\xbb\xf9\xb4T\xab\xd7\xa8\xec%s#n\xa1A\xacO\xa7_\xc4~\xc4\xf2\xa5X\xbb\xf9\xa1H\nQ\xbdT\xbb{\nQ\xa8\xfa\xae\xf8' % self.GetMoneyStr(self.GetAddPrice()), '', misc.Functor(self.OnSureOuttime))
            return None
        
        if self.m_bIsCash:
            sCash = '\xb2{\xaa\xf7'
            sTips = '\xa1]\xc0u\xa5\xfd\xa8\xcf\xa5\xce\xb1H\xb0\xe2\xa5d\xa6\xac\xa4J\xa1^'
        else:
            sCash = '\xa5@\xac\xc9\xb0^\xc4m\xab\xd7'
            sTips = ''
        if self.m_dItemData['iType'] == auctiondefines.VIEWTYPE_NUMBER:
            iDay = 30
        else:
            iDay = 10
        if iCurPrice == 0 and iPrice >= iBasePrice * 1.3:
            sTxt = '\xa6\xb9\xa6\xb8\xa5X\xbb\xf9\xb0\xaa\xa5X\xaa\xec\xa9l\xbb\xf9\xae\xe6\xaa\xba#R130%%#n\xa1A\xbdT\xbb{\xa5H#R%s%s#n\xaa\xba\xbb\xf9\xae\xe6\xa5X\xbb\xf9\xb6\xdc\xa1H%s#r#Y\xaa`\xb7N\xa1G\xa9\xe7\xbd\xe6\xa6\xa8\xa5\\\xab\xe1\xa1A\xb9D\xa8\xe3\xb5o\xb0e\xa8\xec\xb6l\xbdc\xa5u\xa6\xb3%s\xa4\xd1\xa6\xb3\xae\xc4\xb4\xc1\xa1A\xbd\xd0\xa4\xce\xae\xc9\xbb\xe2\xa8\xfa#n\nQ\xbdT\xbb{\nQ\xa8\xfa\xae\xf8' % (self.GetMoneyStr(iPrice), sCash, sTips, iDay)
        else:
            sTxt = '\xbdT\xbb{\xa5H#R%s%s#n\xaa\xba\xbb\xf9\xae\xe6\xa5X\xbb\xf9\xb6\xdc\xa1H%s#r#Y\xaa`\xb7N\xa1G\xa9\xe7\xbd\xe6\xa6\xa8\xa5\\\xab\xe1\xa1A\xb9D\xa8\xe3\xb5o\xb0e\xa8\xec\xb6l\xbdc\xa5u\xa6\xb3%s\xa4\xd1\xa6\xb3\xae\xc4\xb4\xc1\xa1A\xbd\xd0\xa4\xce\xae\xc9\xbb\xe2\xa8\xfa#n\nQ\xbdT\xbb{\nQ\xa8\xfa\xae\xf8' % (self.GetMoneyStr(iPrice), sCash, sTips, iDay)
        if iCurPrice == 0:
            iCurPrice = iBasePrice
        
        if iPrice >= iCurPrice * 3 / 2:
            if not (self.m_bIsCash) or iPrice > 3000000:
                sHighTxt = '#R%s%s#n\xbb\xb7\xb0\xaa\xa9\xf3\xb7\xed\xabe\xa5X\xbb\xf9#Y%s%s#n\xa1A\xbdT\xbb{\xc4~\xc4\xf2\xa5X\xbb\xf9\xb6\xdc\xa1H\nQ\xbdT\xbb{\nQ\xa8\xfa\xae\xf8' % (self.GetMoneyStr(iPrice), sCash, self.GetMoneyStr(iCurPrice), sCash)
            else:
                sHighTxt = None
        if iItemShape in auctiondata.SALEITEM:
            if sHighTxt:
                dlgnpc.ShowClientDlg(sTxt, '', misc.Functor(self.OnSure, misc.Functor(dlgnpc.ShowClientDlg, sHighTxt, '', misc.Functor(self.OnCommit1, iItemID, iPrice))))
            else:
                dlgnpc.ShowClientDlg(sTxt, '', misc.Functor(self.OnCommit1, iItemID, iPrice))
        elif sHighTxt:
            dlgnpc.ShowClientDlg(sTxt, '', misc.Functor(self.OnSure, misc.Functor(dlgnpc.ShowClientDlg, sHighTxt, '', misc.Functor(self.OnCommit2, iItemID, iPrice))))
        else:
            dlgnpc.ShowClientDlg(sTxt, '', misc.Functor(self.OnCommit2, iItemID, iPrice))

    
    def OnSureOuttime(self, iMsgID):
        if iMsgID == 1:
            g_lHasTips.append((self.m_dItemData['itemID'], self.m_dItemData.get('name', '')))
            SaveLocalData()
            self.DoBuy()
        

    
    def OnSure(self, oFunc, iMsgID):
        if iMsgID == 1:
            oFunc()
        

    
    def OnCommit1(self, itemID, iPrice, iMsgID):
        import dlgauctionnew
        if iMsgID == 1:
            dlgauctionnew.C2SDoBidding(itemID, iPrice)
        

    
    def OnCommit2(self, itemID, iPrice, iMsgID):
        import nethdauction
        import nethdidauction
        if iMsgID == 1:
            if self.m_iPageType == auctiondefines.PAGE_NORMAL:
                nethdauction.C2SDoAuctionBuy(itemID, iPrice)
            else:
                nethdidauction.C2GSBid(itemID, iPrice)
        

    
    def DoBook(self):
        import nethdauction
        import nethdidauction
        if self.m_bIsBook:
            iIsBook = 0
        else:
            iIsBook = 1
        if self.m_iPageType == auctiondefines.PAGE_NORMAL:
            nethdauction.C2SSetRemind(self.m_dItemData['iIdx'], iIsBook)
        else:
            nethdidauction.C2GSSetRemind(int(self.m_dItemData['name']), iIsBook)

    
    def DoAutoAdd(self):
        import dlgauctionhf
        if self.m_dItemData:
            if self.m_iPageType == auctiondefines.PAGE_NORMAL:
                if not self.CheckUseLv(misc.Functor(self.DoAutoAdd)):
                    return None
                
            
            dlgauctionhf.ShowAutoAddDlg(self.m_dItemData, self.m_iPointSave, self.m_iPageType, self.GetMoneyStr(self.GetAddPrice()))
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.DoAutoAdd()
        elif iMsgID == 4:
            self.DoBook()
        elif iMsgID == 5:
            self.DoBuy()
        



class CAuctionPreviewHeroFairy(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_hero.dlg')
        self.m_iDir = 1

    
    def SetData(self, dItemData):
        iShape = dItemData['shape']
        (iHeroShape, dDesc) = charpath.GetHeroShow()
        if 'horse' in dDesc:
            del dDesc['horse']
        
        if 'track' in dDesc:
            del dDesc['track']
        
        if 'aura' in dDesc:
            del dDesc['aura']
        
        self.m_oPetAni = walker.CFakeRole(self, -1, iHeroShape, dDesc)
        self.m_oPetAni.SetZ(10)
        if iShape == 26609:
            iShape = 26608
        
        iFairyShape = itemdefine.FAIRY_ITEM_SHAPE_TO_CHAR_ID.get(iShape, iShape - 26600)
        self.m_oPetAni.SetFairy(iFairyShape)
        (x, y, w, h) = self.GetLocData('loc_hero')
        self.m_oPetAni.SetPos(x, y)
        self.m_oPetAni.SetDirection(self.m_iDir)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.m_iDir = (self.m_iDir + 4) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        elif iMsgID == 4:
            self.m_iDir = (self.m_iDir - 4) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        



class CAuctionPreviewHeroNumber(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_hero.dlg')
        self.m_iDir = 1

    
    def SetData(self, dItemData):
        (iHeroShape, dDesc) = charpath.GetHeroShow()
        if 'horse' in dDesc:
            del dDesc['horse']
        
        if 'track' in dDesc:
            del dDesc['track']
        
        if 'aura' in dDesc:
            del dDesc['aura']
        
        self.m_oPetAni = walker.CFakeRole(self, -1, iHeroShape, dDesc)
        self.m_oPetAni.SetZ(10)
        if hero.GetProp('m_FlyFlag') & 128:
            iColor = interface.COLOR_53
            iFont = interface.FontLT16E_1
        elif hero.GetProp('m_NameColor') == 1:
            iColor = interface.COLOR_42
            iFont = interface.FontLT16_1
        else:
            iColor = interface.COLOR_41
            iFont = interface.FontLT16_1
        if hero.GetProp('m_FakeName'):
            sName = hero.GetProp('m_FakeName')
        else:
            sName = hero.GetProp('m_Name')
        dExtend = {
            'm_iPrettyID': int(dItemData['name']),
            'iFakeID': 1000 }
        self.m_oPetAni.SetName(sName, hero.GetHeroID(), hero.GetProp('m_Country'), iColor, font = iFont, iSiblingType = hero.GetProp('m_iSiblingType', 0), dExtend = dExtend)
        sTitle = hero.GetProp('m_Title')
        if sTitle:
            self.m_oPetAni.SetTitle2()
        else:
            self.m_oPetAni.SetTitle2('\xbd\xd0\xb8\xcb\xb3\xc6\xba\xd9\xbf\xd7')
        (x, y, w, h) = self.GetLocData('loc_hero')
        self.m_oPetAni.SetPos(x, y)
        self.m_oPetAni.SetDirection(self.m_iDir)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 3:
            self.m_iDir = (self.m_iDir + 4) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        elif iMsgID == 4:
            self.m_iDir = (self.m_iDir - 4) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        



class CAuctionPreviewSummon(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_summon.dlg')
        self.m_iDir = 1
        self.m_iShape = 0

    
    def SetData(self, dItemData):
        iShape = dItemData['shape']
        self.m_iShape = iShape
        self.m_oPetAni = walker.CFakeRole(self, -1, iShape, 0)
        self.m_oPetAni.SetZ(10)
        (x, y, w, h) = self.GetLocData('loc_summon')
        self.m_oPetAni.SetPos(x, y)
        self.m_oPetAni.SetDirection(self.m_iDir)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            tPetInfo = auctiondata.GetPetDataByShape(self.m_iShape)
            if tPetInfo:
                sName = petdata.GetData(self.m_iShape)['name']
                oInfoDlg = dlggetinfo.ShowFakeSummonInfo(interface.DialogPanel, 0, 0, self.m_iShape, sName, tPetInfo[0], tPetInfo[1], showtips = True)
                interface.Center(oInfoDlg)
            
        elif iMsgID == 3:
            self.m_iDir = (self.m_iDir + 8) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        elif iMsgID == 4:
            self.m_iDir = (self.m_iDir - 8) % 32
            self.m_oPetAni.SetDirection(self.m_iDir)
        



class CAuctionPreviewAvatarFrm(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_avatar.dlg')
        self.m_oAvatar = None
        self.m_oMiniAvatar = None

    
    def SetData(self, dItemData):
        import avatar
        iFrmID = avatarfrmdata.GetFrmByShape(dItemData['shape'], 0)
        (iX, iY) = self.GetObject('loc_avatar').GetPos()
        (iP1, iP2, iP3, iP4) = avatar.PhotoArr2Int(avatar.GetHeroPhoto())
        self.m_oAvatar = avatar.GetSmallImgBy4Int(self, iP1, iP2, iP3, iP4, hero.GetProp('m_Sex', 1), iPlayerID = hero.GetHeroID())
        avatar.CreateAvatarFrm(self.m_oAvatar, iFrmID)
        self.m_oAvatar.SetPos(iX, iY)
        if self.GetObject('loc_avatar_s'):
            (iX, iY) = self.GetObject('loc_avatar_s').GetPos()
            self.m_oMiniAvatar = avatar.GetSmallImgBy4Int(self, iP1, iP2, iP3, iP4, hero.GetProp('m_Sex', 1), 0.5)
            avatar.CreateMiniAvatarFrm(self.m_oMiniAvatar, iFrmID)
            self.m_oMiniAvatar.SetPos(iX, iY)
        



class CAuctionPreviewItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_item.dlg')
        self.m_oImg = None
        self.m_dItemData = None
        self.GetObject('hloc_func').SetEnterCB(misc.Functor(self.OnEnter))
        self.GetObject('hloc_func').SetLeaveCB(misc.Functor(self.OnLeave))

    
    def SetData(self, dItemData):
        iShape = dItemData['shape']
        self.m_dItemData = dItemData
        self.m_oImg = item.CreateItem120Image(self, iShape)
        self.m_oImg.SetZ(10)
        (x, y, w, h) = self.GetLocData('loc_item')
        self.m_oImg.SetPos(x, y)
        self.SetShowObject('txt_func', iShape in auctiondata.SHIWUID2PETINFO)

    
    def OpenShiwu(self):
        if self.m_dItemData['shape'] in auctiondata.SHIWUID2PETINFO:
            dlgshiwu.Show(auctiondata.SHIWUID2PETINFO[self.m_dItemData['shape']])
        

    
    def OnEnter(self):
        dItemData = self.m_dItemData
        iShape = dItemData['shape']
        sDesc = dItemData.get('desc', '')
        sName = dItemData.get('name', '')
        if iShape not in (itemdefine.SHAPE_MSYJ, itemdefine.ID_NUMBER_BAG):
            sName = ''
        
        tipsclosemgr.Regist(dlggetinfo.NewItemInfo(-1, iShape, sDesc, None, 101, sName = sName))

    
    def OnLeave(self):
        tipsclosemgr.CheckClose()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.OpenShiwu()
        



class CAuctionPreviewHorseSkin(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/auction/auction_horseskin.dlg')
        self.m_iDir = 1
        self.m_iHeroShape = 0
        self.m_dDesc = { }
        self.m_oBaseAni = None
        self.m_oHorseAni = None

    
    def SetData(self, dItemData):
        import descinterface
        import horseskindata
        dSkinData = horseskindata.GetDataByItemShape(dItemData['shape'])
        if dSkinData:
            (self.m_iHeroShape, dDesc) = charpath.GetHeroShow()
            dDesc = descinterface.ClearTrack(dDesc)
            dDesc = descinterface.ClearAura(dDesc)
            dDesc = descinterface.ClearFairy(dDesc, 0)
            dDesc = descinterface.ClearFairy(dDesc, 1)
            dDesc = descinterface.SetHorseInfo(dDesc, dSkinData['iHorse'], True, True, dSkinData['iColor'], dSkinData['iFirstColor'], dSkinData['iSecondColor'])
            self.m_dDesc = dDesc
            self.m_oBaseAni = interface.CBaseObject(self)
            oHorse = walker.CFakeRole(self.m_oBaseAni, -1, self.m_iHeroShape, dDesc)
            oHorse.ClearRider()
            oHorse.SetShadow(False)
            oHorse.Enable(False)
            oHorse.SetZ(10)
            oHorse.SetDirection(self.m_iDir)
            self.m_oHorseAni = oHorse
            (iX, iY, iW, iH) = self.GetLocData('loc_hero')
            iZ = self.GetObject('loc_hero').GetZ()
            self.m_oBaseAni.SetPos(iX, iY)
            self.m_oBaseAni.SetZ(iZ)
        

    
    def OpenPreviewDlg(self):
        import appearanceridepv
        appearanceridepv.OpenAutoSelectRidePreviewExDlg(self.m_iHeroShape, self.m_dDesc)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OpenPreviewDlg()
        elif iMsgID == 3:
            self.m_iDir = (self.m_iDir + 4) % 32
            if self.m_oHorseAni:
                pass
            self.m_oHorseAni.SetDirection(self.m_iDir)
        elif iMsgID == 4:
            self.m_iDir = (self.m_iDir - 4) % 32
            if self.m_oHorseAni:
                pass
            self.m_oHorseAni.SetDirection(self.m_iDir)
        



def LoadLocalData():
    global g_lHasTips
    if g_lHasTips is None:
        g_lHasTips = []
        sStr = hero.GetPrivateData('Game', 'auctionlist')
        if sStr:
            for sEach in sStr.split('|'):
                lTmp = sEach.split(',')
                lRet = []
                if lTmp[0].isdigit():
                    lRet.append(int(lTmp[0]))
                    lRet.extend(lTmp[1:])
                    continue
            
            g_lHasTips.append(tuple(lRet))
        
    


def SaveLocalData():
    if g_lHasTips is not None:
        if len(g_lHasTips) > 10:
            lHasTips = g_lHasTips[len(g_lHasTips) - 10:]
        else:
            lHasTips = g_lHasTips
        sMsg = ''
        for tEach in lHasTips:
            lTmp = []
            for sEach in tEach:
                lTmp.append(str(sEach))
            
            sMsg += ','.join(lTmp)
        
        hero.SavePrivateData('Game', 'auctionlist', sMsg)
