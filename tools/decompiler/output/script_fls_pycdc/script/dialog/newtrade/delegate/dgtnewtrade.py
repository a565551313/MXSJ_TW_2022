# pycdc 交叉复核产物 · script.fls entry 2621
# co_filename(原始)='script/dialog/newtrade/delegate/dgtnewtrade.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2621.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/9/21 20:56
\xd7\xf7\xd5\xdf:
\xce\xc4\xbc\xfe:
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import hero
import interface
import item
import mdmvpnormal
import netitem
import netnpc
import newtradedefine
import newtradeinterface
import re
import mdnewtrade
import timer
import misc
import itemdefine

class CNewTradeDelegate(delegatebase.CDelegateBase):
    
    def GetView(self):
        ''':rtype: dlgtradenew.CNewTradeDlg'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return mdnewtrade.GetModel()

    
    def Init(self):
        self.m_iSelectIdx = -1
        self.m_iAmount = 0
        self.InitSigal()
        self.m_iTime = 0
        self.m_oPSTimer = None
        self.m_oTimer = None
        self.GetView().InitUI()
        self.InitAutoCloseUI()

    
    def InitSigal(self):
        import commoncb
        commoncb.RegistCB(commoncb.USE_FLYITEM, self, 'OnCloseView')
        oView = self.GetView()
        oView.ssConnect(oView.SS_CloseWindow, self.OnCloseView)
        oView.ssConnect(oView.SS_OnBuyClick, self.OnBtnBuyClick)
        oView.ssConnect(oView.SS_OnItemRightUp, self.OnItemRightUp)
        oView.ssConnect(oView.SS_OnItemLeftUp, self.OnItemLeftUp)
        oView.ssConnect(oView.SS_OnAmountEditChange, self.OnAmountEditChange)
        oModel1 = mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEWTRADE)
        oModel1.ssConnect('m_iTicketID', self.RefreshTicket)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_InitOtherPart, self.UpdateTradeData)

    
    def OnAmountEditChange(self, sAmount):
        if sAmount and sAmount.isdigit():
            self.m_iAmount = min(int(sAmount), self.GetMaxAmount())
        else:
            self.m_iAmount = min(1, self.GetMaxAmount())
        self.SetViewTotalPriceColor()
        self.SetViewTotalPrice()

    
    def StartPSTimer(self):
        self.EndPSTimer()
        self.CreateTimeText(self.m_iTime)
        self.m_oPSTimer = timer.Timer(1, misc.Functor(self.OnTick), -1, self)

    
    def OnTick(self):
        self.m_iTime -= 1
        if self.m_iTime <= 0:
            self.EndPSTimer()
            self.OnPSTimerOut()
            return None
        
        self.CreateTimeText(self.m_iTime)

    
    def EndPSTimer(self):
        if hasattr(self, 'm_oPSTimer') and self.m_oPSTimer:
            self.m_oPSTimer.Release()
            self.m_oPSTimer = None
        

    
    def CreateTimeText(self, iTime):
        txt = '\xa4U\xa6\xb8\xa8\xea\xb7s\xae\xc9\xb6\xa1: %2d:%2d' % (iTime / 60, iTime % 60)
        self.GetView().SetTradeTips(txt)

    
    def OnPSTimerOut(self):
        import netnpc
        netnpc.C2SNpcBuy(0, 0)

    
    def UpdateTradeData(self):
        '''
\t\t\xb3o\xa8\xc7\xa8\xe7\xbc\xc6\xa6b\xa6\xac\xa8\xec\xb0\xd3\xab\xb0\xbc\xc6\xbe\xda\xae\xc9\xb0\xf5\xa6\xe6
\t\t:return:
\t\t'''
        iSelect = self.GetModel().GetSelectItemIdx()
        if iSelect != self.m_iSelectIdx:
            self.m_iAmount = 1
            self.m_iSelectIdx = iSelect
        
        self.UpdateBuyEdit()
        self.UpdateOwnCash()
        self.BindCashFreshCB()
        self.SetViewDescShort()
        if self.GetModel().GetTradeMode() == newtradedefine.TRADE_PS:
            self.m_iTime = self.GetModel().GetEndTime()
            self.StartPSTimer()
        

    
    def SetViewDescShort(self):
        self.GetView().SetTradeTips(newtradeinterface.GetTipsByTrade(self.GetModel().GetTradeMode()))

    
    def OnItemLeftUp(self, iIndex):
        self.GetModel().SetSelectItemId(iIndex)
        if self.m_iSelectIdx != iIndex:
            self.m_iSelectIdx = iIndex
            self.m_iAmount = self.GetDefaultSum()
            self.UpdateBuyEdit()
        elif self.GetMaxAmount() > self.m_iAmount:
            self.m_iAmount += 1
            self.UpdateBuyEdit()
        

    
    def OnItemRightUp(self, iIndex):
        self.GetModel().SetSelectItemId(iIndex)
        if self.m_iSelectIdx != iIndex:
            self.m_iSelectIdx = iIndex
            self.m_iAmount = self.GetDefaultSum()
        else:
            self.OnSameItemRightUp()
        self.UpdateBuyEdit()

    
    def OnSameItemRightUp(self):
        iSelectShape = self.GetModel().GetSelectItemShape()
        
        try:
            iTradeMode = self.GetModel()()
            if iTradeMode == newtradedefine.TRADE_GROCERY or iSelectShape in itemdefine.ITEM_BIXIE or iSelectShape == itemdefine.ID_DINGSHEN:
                self.m_iAmount = self.GetMaxAmount()
            elif iTradeMode == newtradedefine.TRADE_FARM:
                self.m_iAmount = min(self.GetMaxAmount(), 40 - item.GetGoodsNum())
            else:
                self.m_iAmount = max(1, self.m_iAmount - 1)
            return None


    
    def GetDefaultSum(self):
        '''
\t\t\xad\xba\xa6\xb8\xc2I\xc0\xbb\xb8\xd3\xaa\xab\xab~\xc0q\xbb{\xb3]\xb8m\xaa\xba\xbc\xc6\xb6q
\t\t:return:
\t\t'''
        iSum = 1
        iTradeMode = self.GetModel().GetTradeMode()
        iSelectShape = self.GetModel().GetSelectItemShape()
        if iTradeMode in (newtradedefine.TRADE_GROCERY,):
            if iSelectShape in itemdefine.ITEM_BIXIE:
                iSum = 10
            
        elif iTradeMode == newtradedefine.TRADE_MDEICINAL:
            iSum = None if self.m_iAmount > 0 else 1
        
        return iSum

    
    def UpdateOwnCash(self):
        tShowCashType = newtradeinterface.GetShowCashByType(self.GetModel().GetTradeMode())
        for iIndex, iCashType in enumerate(tShowCashType):
            self.SetViewOwnCash(iIndex, iCashType)
        
        self.SetViewTotalPriceColor()

    
    def BindCashFreshCB(self):
        tShowCashType = newtradeinterface.GetShowCashByType(self.GetModel().GetTradeMode())
        for iCashType in tShowCashType:
            sProp = newtradeinterface.GetPropByType(iCashType)
            if sProp:
                hero.AddRefreshCallbackNotFirstCB('CNewGiveItemCashDgt', (sProp,), self.UpdateOwnCash)
                continue
        

    
    def SetViewOwnCash(self, iIndex, iCashType):
        '''
\t\t:param iIndex:
\t\t:param iCashType:
\t\t:return:
\t\t'''
        iOwnCash = self.GetOwnCashByType(iCashType)
        sCashName = newtradeinterface.GetCashNameByType(iCashType)
        if iIndex == 0:
            self.GetView().SetCashName(sCashName)
            self.GetView().SetCashAmount(iOwnCash)
        elif iIndex == 1:
            self.GetView().SetFightCashName(sCashName)
            self.GetView().SetFightCashSum(iOwnCash)
        

    
    def GetOwnCashByType(self, iCashType):
        '''
\t\t\xc0\xf2\xa8\xfa\xbe\xd6\xa6\xb3\xaa\xba\xb3f\xb9\xf4
\t\t:param iCashType:
\t\t:return:
\t\t'''
        if iCashType == newtradedefine.TYPE_OTHER or iCashType == newtradedefine.TYPE_COOK_POINT:
            return self.GetModel().GetTicketID()
        elif iCashType == newtradedefine.TYPE_TICKET:
            iTicketID = self.GetModel().GetTicketID()
            oItem = item.GetItem(iTicketID)
            if not hasattr(oItem, 'm_InfoExt') or oItem.GetExtInfoDict() is None:
                netitem.C2SItemString(iTicketID, 0)
                return 0
            
            patt = re.{ompile('\xad\xb1\xad\xc8[ ]*[0-9]+')
            mo = patt.search(oItem.m_InfoExt)
            if mo is not None:
                
                try:
                    return int(oItem.m_InfoExt[mo.start() + 4:mo.end()].strip())
                except ValueError:
                    return 0
                except:
                    None<EXCEPTION MATCH>ValueError
                

            None<EXCEPTION MATCH>ValueError
            return 0
        else:
            sProp = newtradeinterface.GetPropByType(iCashType)
            if sProp:
                return hero.GetProp(sProp, 0)
            
        return 0

    
    def RefreshTicket(self, *args):
        self.UpdateOwnCash()

    
    def SetFightCashInfo(self):
        self.GetView()

    
    def SetViewBuyEditAmount(self):
        self.GetView().SetBuyEditAmount(self.m_iAmount)

    
    def SetViewBuyEditMax(self):
        iMaxAmount = self.GetMaxAmount()
        self.GetView().SetBuyEditMax(iMaxAmount)

    
    def SetViewBuyEditSelect(self):
        iAmount = 999
        self.GetView().SetBuyEditSelect(iAmount)

    
    def SetViewBuyEditEnable(self):
        bEnable = not self.GetModel().GetTradeType()
        self.GetView().SetBuyEditEnable(bEnable)

    
    def UpdateBuyEdit(self):
        '''
\t\t\xc1\xca\xb6R\xbc\xc6\xb6q\xa7\xef\xc5\xdc\xae\xc9\xbd\xd5\xa5\xce\xa4@\xa6\xb8
\t\t:return:
\t\t'''
        self.SetViewBuyEditMax()
        self.SetViewBuyEditAmount()
        self.SetViewBuyEditSelect()
        self.SetViewTotalPriceColor()
        self.SetViewTotalPrice()
        self.SetViewBuyEditEnable()

    
    def GetTotalPrice(self):
        return self.m_iAmount * self.GetModel().GetSelectItemPrice()

    
    def SetViewTotalPrice(self):
        iTotalPrice = self.GetTotalPrice()
        self.GetView().SetTotalPrice(str(iTotalPrice))

    
    def SetViewTotalPriceColor(self):
        iColor = self.GetPriceColor()
        self.GetView().SetTotalPriceColor(iColor)

    
    def GetOwnCash(self):
        tShowCashType = newtradeinterface.GetShowCashByType(self.GetModel().GetTradeMode())
        iSum = 0
        for iCashType in tShowCashType:
            iSum += self.GetOwnCashByType(iCashType)
        
        return iSum

    
    def GetMaxAmount(self):
        iSum = self.GetOwnCash()
        iUnitPrice = self.GetModel().GetSelectItemPrice()
        if not iUnitPrice:
            if self.GetModel().GetSelectItemShape() == itemdefine.ID_DINGSHEN:
                return 200
            
            return 1
        
        iAmount = iSum / iUnitPrice
        iAmount = None if iAmount == 0 else iAmount
        if self.GetModel().GetTradeMode() == newtradedefine.TRADE_COOK and self.GetModel().GetTradeKey() == 'zhidao':
            return iAmount
        elif self.GetModel().GetTradeMode() == newtradedefine.TRADE_GROCERY and self.GetModel().GetSelectItemLimitNum() == 1:
            return 200
        elif self.GetModel().GetTradeMode() == newtradedefine.TRADE_FARM and self.GetModel().GetSelectItemShape() in (22300, 22301):
            return max(min(iAmount, 40 - item.GetGoodsNum()), 1)
        else:
            return min(iAmount, self.GetModel().GetSelectItemLimitNum())

    
    def GetPriceColor(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xc1`\xbb\xf9\xc3C\xa6\xe2
\t\t:return:
\t\t'''
        iOwnCash = self.GetOwnCash()
        iNeedCash = self.GetTotalPrice()
        iColor = None if iNeedCash > iOwnCash else interface.COLOR_5
        return iColor

    
    def OnBtnBuyClick(self):
        if self.m_iSelectIdx < 0 or self.m_iAmount <= 0:
            return None
        
        self.m_iRespondID = self.GetModel().GetRespondID()
        netnpc.C2SNpcBuy(self.m_iSelectIdx, self.m_iAmount, self.m_iRespondID)
        LOG_DEBUG('\xb0\xd3\xab\xb0\xc1\xca\xb6R\xa4U\xbc\xd0:%d, \xbc\xc6\xb6q:%d, Respond:%d' % (self.m_iSelectIdx, self.m_iAmount, self.m_iRespondID))

    
    def InitAutoCloseUI(self):
        self.m_oTimer = timer.Timer(9000, self.OnCloseView, oRelayObj = self)

    
    def OnCloseView(self):
        self.GetModel().ClearModel()
        self.GetView().CloseUI()
