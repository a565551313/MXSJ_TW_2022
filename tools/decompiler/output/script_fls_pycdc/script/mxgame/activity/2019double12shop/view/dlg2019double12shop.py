# pycdc 交叉复核产物 · script.fls entry 491
# co_filename(原始)='script/mxgame/activity/2019double12shop/view/dlg2019double12shop.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_491.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2019/12/9 11:42
\xd7\xf7\xd5\xdf: rxz
\xce\xc4\xbc\xfe: dlg2019double12shop
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import helper2019double12
import item
import slot
import pagedlgbase
import double122019define
import ui
import interface
import itemdefine
import misc
import walkerpart
import makeitemicon
g_GoodsTips = None

def ModuleReset():
    global g_GoodsTips
    g_GoodsTips = None


class C2019Double12ShopItem(combdialog.CCombSubWnd):
    PREVIEW_MSGID = 10
    
    def __init__(self, oParent, oClickCartCB, oSelectItemCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/double12/double12_goods.dlg')
        self.InitDialog()
        self.m_oItemImg = None
        self.m_oLimitBuyImg = None
        self.m_oLimitBuyText = None
        self.m_dData = None
        self.m_oPreviewImg = None
        self.m_oPreviewTips = None
        self.m_oPreviewBox = None
        self.m_bSelected = False
        self.m_iCanBuy = 0
        self.m_iLastNum = 0
        self.m_iLimitCount = 0
        self.m_bEditCB = False
        self.m_oClickCartCB = oClickCartCB
        self.m_oSelectItemCB = oSelectItemCB

    
    def InitDialog(self):
        oHotBox = self.GetObject('hloc_item')
        if oHotBox:
            oHotBox.SetEnterCB(misc.Functor(self.OnItemEnter))
            oHotBox.SetLeaveCB(misc.Functor(self.OnItemLeave))
            oHotBox.SetMouseWheelEnable(True)
        
        self.GetObject('img_discount').SetZ(5)
        self.GetObject('edit_number').SetText('0')
        self.GetObject('edit_number').SetCharChangeCB(misc.Functor(self.OnCharChange))

    
    def LockStyle(self):
        import defines
        oItem = self.GetObject('img_goods')
        if oItem:
            pass
        oItem.ResetImageByStyle(defines.STYLE4_KEY)

    
    def SetData(self, dData):
        import item
        import itemdata
        import helper2019double12
        if dData == self.m_dData:
            return None
        
        self.m_dData = misc.DeepCopy(dData)
        bIsLimitBuy = dData[double122019define.ITEM_IS_LIMIT_BUY]
        iCanBuy = helper2019double12.CalItemLimitBuyCount(dData[double122019define.ITEM_ID])
        self.m_iCanBuy = iCanBuy
        iShowLock = dData[double122019define.ITEM_LOCK_TYPE]
        iShape = helper2019double12.GetShapeChange(dData[double122019define.ITEM_SHAPE])
        iSgPrice = dData['sg_price']
        self.SetShowObject('img_lock', iShowLock == double122019define.ITEM_LOCK)
        self.GetObject('img_lock').SetZ(1)
        self.GetObject('text_itemname').SetText(itemdata.GetData(iShape)[0])
        if iSgPrice > 0:
            self.GetObject('txt_prize').SetText(str(dData[double122019define.ITEM_SG_PRICE]))
            self.GetObject('text_sg').SetText('')
            self.SetShowObject('loc_sg', True)
        else:
            self.SetShowObject('loc_sg', False)
            self.GetObject('text_sg').SetText('\xa7K\xb6O\xc1\xca\xb6R')
        if not self.m_oLimitBuyImg:
            self.m_oLimitBuyImg = ui.CImageBox(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xcf\xde\xb9\xba\xcd\xbc\xb1\xea/\xcf\xde\xb9\xba.igs', interface.UIPath, 0)
            self.m_oLimitBuyImg.SetZ(1)
        
        self.m_oLimitBuyImg.SetShow(False)
        self.GetObject('text_limit').SetText(str(iCanBuy))
        self.GetObject('text_limit').SetZ(1)
        self.m_oItemImg = item.CreateItem44Image(self, iShape)
        self.m_oItemImg.SetPos(3, 3)
        iLimitCount = dData[double122019define.ITEM_LIMIT_BUY_COUNT]
        self.UpdateLimitCount(iLimitCount)
        if iCanBuy > 0:
            if iSgPrice <= 0:
                self.CreateTips(self.m_oItemImg)
            
            self.m_oItemImg.SetLight(8)
        else:
            self.m_oItemImg.SetGrey()
        if bIsLimitBuy:
            if iCanBuy > 0:
                self.m_oLimitBuyImg.SetLight(8)
            else:
                self.m_oLimitBuyImg.SetGrey()
        
        self.SetSelectedItem(dData.get(double122019define.ITEM_SELECT_TYPE, False))
        self.ShowOtherUI()

    
    def UpdateLimitCount(self, iLimitCount):
        self.m_iLimitCount = iLimitCount
        iNumber = iLimitCount - self.m_iCanBuy
        self.SetEditShow(bool(iNumber))
        self.SetEditNumber(iNumber)
        self.m_iLastNum = iNumber
        if not (self.m_iLimitCount) and not (self.m_iCanBuy):
            self.SetShowObject('loc_number', False)
            self.SetShowObject('btn_shoppingcar', False)
        

    
    def CreateTips(self, oParent):
        oAni = interface.CSpriteObject(oParent, 'item44/select.spr', interface.ITEM_PATH)
        oAni.SetZ(10)
        oAni.CreateCommand(1, 'animation')
        (iW, iH) = oParent.GetSize()
        oAni.SetPos(iW / 2, iH / 2)
        oParent.m_oLimitBuyAni = oAni

    
    def ShowOtherUI(self):
        import clickimage
        iShape = self.m_dData.get(double122019define.ITEM_SHAPE, 0)
        self.SetShowObject('img_discount', False)
        self.SetShowObject('img_discount_right', False)
        if iShape in (itemdefine.ID_LUCKY_SUMMON_BOOK_REWARD, itemdefine.ID_LUCKY_SUMMON_BOOK_ITEM):
            self.m_oPreviewImg = clickimage.CClickImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd4\xa4\xc0\xc0.igs', self.PREVIEW_MSGID, 0, 0)
            self.m_oPreviewImg.SetZ(5)
            self.m_oPreviewImg.SetPos(1, 3)
            (iW, iH) = self.m_oItemImg.GetSize()
            self.m_oPreviewBox = interface.CClickBox(self, iW * 4 / 5, iH * 4 / 5, alpha = 0, msgid = self.PREVIEW_MSGID)
            self.m_oPreviewBox.SetZ(4)
            self.m_oPreviewBox.SetEnterCB(misc.Functor(self.OnClickBoxEnter))
            self.m_oPreviewBox.SetLeaveCB(misc.Functor(self.OnClickBoxLeave))
            self.m_oPreviewBox.SetPos(1, 3)
        elif iShape == itemdefine.ID_DOUBLE_SKILL_HF:
            self.SetShowObject('img_discount', True)
        else:
            self.m_oPreviewImg = None
            self.m_oPreviewBox = None

    
    def GetEditNumber(self):
        return self.GetObject('edit_number').GetNumber()

    
    def SetEditNumber(self, iNum):
        self.GetObject('edit_number').SetNotCBChangeCharLock(True)
        self.GetObject('edit_number').SetText(str(iNum))
        self.GetObject('edit_number').SetNotCBChangeCharLock(False)

    
    def SetChangeNumber(self, bAdd):
        iNumber = self.GetEditNumber()
        if bAdd:
            iNumber += 1
        else:
            iNumber -= 1
        self.m_bEditCB = False
        self.OnClickCartCB(iNumber)

    
    def SetEditShow(self, bShow):
        self.SetShowObject('loc_number', bShow)
        self.SetShowObject('btn_shoppingcar', not bShow)

    
    def OnCharChange(self):
        iNumber = self.GetEditNumber()
        self.m_bEditCB = True
        if iNumber > self.m_iLimitCount:
            self.SetEditNumber(self.m_iLimitCount)
            self.OnClickCartCB(self.m_iLimitCount)
        elif iNumber <= 0:
            self.SetEditNumber(1)
            self.OnClickCartCB(1)
        elif iNumber != self.m_iLastNum:
            self.OnClickCartCB(iNumber)
        

    
    def SetMaxOrMinNumber(self, bMax):
        if bMax:
            iNumber = self.m_iLimitCount
        else:
            iNumber = 1
        self.m_bEditCB = False
        self.OnClickCartCB(iNumber)

    
    def GetSelect(self):
        return self.m_bSelected

    
    def GetBGImage(self):
        return self.GetObject('img_goods').GetImageList()[0]

    
    def GetId(self):
        return self.m_dData.get(double122019define.ITEM_ID, 0)

    
    def SetSelectedItem(self, bSelected):
        self.m_bSelected = bSelected
        if self.GetSelect():
            self.GetBGImage().SetFrame(1)
            if not self.m_bEditCB:
                self.SetEditSelect()
            
        else:
            self.GetBGImage().SetFrame(0)

    
    def SetEditSelect(self):
        self.GetObject('edit_number').Active(True)
        self.GetObject('edit_number').SetSelect(0, 999)
        self.m_bEditCB = False

    
    def OnSelectItemCB(self):
        iNumber = self.GetEditNumber()
        if self.m_oSelectItemCB:
            pass
        self.m_oSelectItemCB(self.m_dData, iNumber + 1)

    
    def OnEnter(self, iMsgID):
        if iMsgID == self.PREVIEW_MSGID:
            self.OnClickBoxEnter(iFlag = 1)
        

    
    def OnLeave(self, iMsgID):
        self.OnClickBoxLeave()

    
    def OnClickBoxEnter(self, iFlag = 0):
        import wrapinterface
        self.m_oPreviewTips = wrapinterface.CTextTips(None, -1, '\xc2I\xc0\xbb\xa5i\xacd\xac\xdd\xc3~\xb3Z\xa6\xc0', interface.FontLT14_3, direct = 1)
        if iFlag == 0:
            oOwner = self.m_oPreviewBox
        else:
            oOwner = self.m_oPreviewImg
        self.m_oPreviewTips.SetOwner(oOwner)

    
    def OnClickBoxLeave(self):
        self.m_oPreviewTips = None

    
    def OnItemEnter(self):
        global g_GoodsTips
        import item
        if not self.m_dData:
            return None
        
        import dlggetinfo
        iKey = None
        iBindType = self.m_dData.get(double122019define.ITEM_BIND_TYPE, 0)
        if iBindType == 1:
            iKey = item.MARK_BOUND
        elif iBindType == 2:
            iKey = item.MARK_JINGPIN
        
        g_GoodsTips = dlggetinfo.NewItemInfo(0, helper2019double12.GetShapeChange(self.m_dData[double122019define.ITEM_SHAPE]), self.m_dData[double122019define.ITEM_DESC], None, iKey)

    
    def OnItemLeave(self):
        global g_GoodsTips
        g_GoodsTips = None

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.MouseWheelUp(p)

    
    def LeftUp(self):
        combdialog.CCombSubWnd.LeftUp(self)
        self.OnSelectItemCB()

    
    def OnOpenSummmonView(self):
        import dlgshopsummonview
        dlgshopsummonview.Show()

    
    def OnClickCartCB(self, iNum):
        self.m_oClickCartCB(self.m_dData, iNum)

    
    def OnMessage(self, iMsgID):
        if iMsgID in (1, 4):
            self.SetChangeNumber(True)
        elif iMsgID == 2:
            self.OnSelectItemCB()
        elif iMsgID == self.PREVIEW_MSGID:
            self.OnOpenSummmonView()
        elif iMsgID == 5:
            self.SetChangeNumber(False)
        
        iMsgID -= interface.RIGHT_BUTTON_MESSAGE
        if iMsgID == 4:
            self.SetMaxOrMinNumber(True)
        elif iMsgID == 5:
            self.SetMaxOrMinNumber(False)
        



class C2019Double12DiscountTypeDialog(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/double12/double12_card.dlg')
        self.SetShowObject('loc_hide', False)

    
    def SetDiscountType(self, iType):
        for iIndex in xrange(len(double122019define.DISCOUNT_PRICE)):
            iId = iIndex + 1
            oText = self.GetObject('text_card%d' % iId)
            if not oText:
                continue
            
            bSpecial = iId == iType
            sText = None if bSpecial else 'text_nor_1'
            iColor = self.GetObject(sText).GetColor()
            oText.SetColor(iColor)
            sText = None if bSpecial else 'text_nor_2'
            iColor = self.GetObject(sText).GetColor()
            self.GetObject('txt_discount%d' % iId).SetColor(iColor)
            oImage = self.GetObject('img_card%d' % iId)
            if not oImage:
                continue
            
            sImg = None if bSpecial else 'img_card_nor'
            (sPath, sPack) = self.GetObject(sImg).GetPathInfo()
            oImage.SetImagePath(sPath, sPack)
        



class C2019Double12DiscountUsedDialog(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/double12/double12_used.dlg')

    
    def SetUsedDiscountType(self, iType):
        if iType < 0 or iType >= len(double122019define.DISCOUNT_PRICE):
            return None
        
        iTotal = double122019define.DISCOUNT_PRICE[iType][0]
        iDiscount = double122019define.DISCOUNT_PRICE[iType][1]
        self.GetObject('text_card').SetText('\xba\xa1%d\xb4\xee' % iTotal)
        self.GetObject('text_discount').SetText('%d' % iDiscount)



class C2019Double12ShopDialog(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_OnPageOpen = 'SS_OnPageOpen()'
    SS_OnCartButtonClick = 'SS_OnCartButtonClick()'
    SS_OnItemCartButtonClick = 'SS_OnItemCartButtonClick(iItemId)'
    SS_OnMiniBuyConfirm = 'SS_OnMiniBuyConfirm(iItemId, iCount)'
    SS_OnOpenMiniBuyDlg = 'SS_OnOpenMiniBuyDlg(iItemId)'
    SS_OnSelectItem = 'SS_SelectItem()'
    SS_OnClickChangeShop = 'SS_OnClickChangeShop()'
    SS_OnClickBuyItem = 'SS_OnClickBuyItem(iItemID)'
    SS_ClickQuickAddShoppingCart = 'SS_ClickQuickAddShoppingCart()'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/itembill/double12/double12_shop.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.InitView()
        self.m_oSpecialItemAni = None
        self.m_oPlayerPart = None
        self.m_DelegateList = []
        self.InitDelegate()

    
    def InitView(self):
        self.m_oMinibuyDialog = None
        self.m_oDiscountTypeListDialog = None
        self.m_oDiscountUsedDialog = None
        self.m_oCartDialog = None
        self.m_oFlashAni = None
        self.m_oSpeItemList = []
        self.SetShowObject('img_goods', False)
        self.m_oShopItemListView = self.GetObject('tbview_goods')
        self.m_oShopItemListView.SetShowBgLine(False)
        self.m_oShopItemListView.SetDelegateNewCellOfData(self.TbDelegateNewCellOfData)
        self.m_oShopItemListView.SetDelegateUpdateCellOfData(self.TbDelegateUpdateCellOfData)
        self.SetShowObject('btn_CardCharg6', False)
        for i in range(2):
            i += 1
            self.GetObject('img_lock%d' % i).SetShow(False)
            self.GetObject('text_unlocktips%d' % i).SetShow(False)
            self.GetObject('btn_buyspeitem%d' % i).SetShow(False)
        

    
    def InitDelegate(self):
        import dgt2019double12shop
        self.m_DelegateList = [
            dgt2019double12shop.C2019Double12ShopDelegate(self)]

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)
        self.ssEmit(self.SS_OnPageOpen)

    
    def VClose(self):
        self.SetShow(False)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_OnCartButtonClick)
        elif iMsgID in (3, 4):
            self.ssEmit(self.SS_OnClickBuyItem, self.m_oSpeItemList[iMsgID - 3].GetItemID())
        elif iMsgID == 5:
            self.ssEmit(self.SS_OnClickChangeShop)
        elif iMsgID == 9:
            self.ssEmit(self.SS_ClickQuickAddShoppingCart)
        

    
    def TbDelegateNewCellOfData(self, oContainer, oData):
        oCell = C2019Double12ShopItem(oContainer, misc.Functor(self.OnCartButtonClick), misc.Functor(self.OnSelectItem))
        oCell.SetData(oData)
        return oCell

    
    def TbDelegateUpdateCellOfData(self, oCell, oData, bReused):
        if bReused:
            oCell.SetData(oData)
        

    
    def OnCartButtonClick(self, dItemData, iNum):
        self.ssEmit(self.SS_OnItemCartButtonClick, dItemData[double122019define.ITEM_ID], iNum)

    
    def OnMiniBuyConfirm(self, iItemId, iAmount):
        self.ssEmit(self.SS_OnMiniBuyConfirm, iItemId, iAmount)

    
    def OnOpenMiniBuyDlg(self, dItemData):
        self.ssEmit(self.SS_OnOpenMiniBuyDlg, dItemData[double122019define.ITEM_ID])

    
    def OnSelectItem(self, dItemData, iEditNum):
        if dItemData[double122019define.ITEM_SELECT_TYPE]:
            self.OnCartButtonClick(dItemData, iEditNum)
        else:
            self.ssEmit(self.SS_OnSelectItem, dItemData)

    
    def OpenSpecialItemTips(self):
        oLoc = self.GetObject('loc_item2')
        oAni = interface.CSpriteObject(oLoc, 'common/hint_twice.spr', interface.UIPath)
        oAni.CreateCommand(2, 'animation')
        self.m_oPlayerPart = walkerpart.CPlayerOncePart(oAni, self.ClearSpecialItemAni)
        self.m_oPlayerPart.SetCBFrame(oAni.FrameAmount(1) * 4 - 2)
        self.m_oPlayerPart.PlayOnce()
        oAni.SetZ(10)
        (iW, iH) = oLoc.GetSize()
        oAni.SetPos(iW / 2, iH / 2)
        self.m_oSpecialItemAni = oAni

    
    def ClearSpecialItemAni(self):
        self.m_oSpecialItemAni = None

    
    def RefreshLeftTimeTips(self, sTips):
        self.GetObject('txt_tips').SetText(sTips)

    
    def ShowDelLines(self, iTextLen, bShow):
        if not bShow:
            self.m_oDelLine = None
            return None
        
        obj = self.GetObject('txt_oldprize')
        if not obj:
            return None
        
        self.m_oDelLine = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xbc\xdb\xb8\xf1\xbb\xae\xcf\xdf.png', interface.UIPath)
        interface.AlignObjects(self.m_oDelLine, obj, interface.ALIGN_LEFT_MIDDLE)
        (iX, iY) = self.m_oDelLine.GetPos()
        iX -= 4
        iY -= 2
        self.m_oDelLine.SetPos(iX, iY)

    
    def SetQuickAddShoppingCartBtn(self, bShowQuickAdd):
        oBtnLoc = self.GetObject('loc_btn')
        oShoppingCarLoc = self.GetObject('loc_shoppingcar')
        oQuickBuy = self.GetObject('btn_quickbuy')
        oQuickBuy.SetShow(bShowQuickAdd)
        if bShowQuickAdd:
            interface.AlignObjects(oQuickBuy, oBtnLoc, interface.ALIGN_LEFT_MIDDLE)
            interface.AlignObjects(oShoppingCarLoc, oBtnLoc, interface.ALIGN_RIGHT_MIDDLE)
        else:
            interface.AlignObjects(oShoppingCarLoc, oBtnLoc, interface.ALIGN_MIDDLE)

    
    def SetDiscountTips(self, sTips):
        self.GetObject('text_tips2').SetText(sTips)

    
    def SetRefreshBtnState(self, bShow, tBtnText):
        oBtn = self.GetObject('btn_CardCharg6')
        if oBtn:
            bPreShow = oBtn.GetShow()
            oBtn.SetShow(bShow)
            (sBtnText, sTips) = tBtnText
            oBtn.SetText(sBtnText)
            oBtn.SetTips(sTips)
            if not bPreShow and bShow:
                oAni = interface.CSpriteObject(oBtn, 'common/hint_twice.spr', interface.UIPath)
                oAni.CreateCommand(2, 'one_off_animation')
                oAni.SetZ(10)
                (iW, iH) = oBtn.GetSize()
                oAni.SetPos(iW / 2, iH / 2)
                self.m_oFlashAni = oAni
            
        
        self.SetShowObject('text_tips2', not bShow)

    
    def IsCartDialogShowing(self):
        return self.m_oCartDialog

    
    def OpenMiniBuyDialog(self, dCartItem):
        import dlg2019double12minibuy
        import cursor
        if not self.m_oMinibuyDialog:
            self.m_oMinibuyDialog = dlg2019double12minibuy.C2019Double12ShopMiniDialog(self, dCartItem, misc.Functor(self.OnMiniBuyConfirm))
        else:
            self.m_oMinibuyDialog.Refresh(dCartItem, misc.Functor(self.OnMiniBuyConfirm))
        (iParentX, iParentY) = self.GetScreenPos()
        (iCursorX, iCursorY) = cursor.GetCursorPos()
        self.m_oMinibuyDialog.SetPos(iCursorX - iParentX - 120, iCursorY - iParentY - 160)

    
    def OpenCartDialog(self):
        import dlg2019double12cart
        self.m_oCartDialog = dlg2019double12cart.C2019Double12CartDialog(self)

    
    def CloseCartDialog(self):
        self.m_oCartDialog = None

    
    def CloseMiniBuy(self):
        self.m_oMinibuyDialog = None

    
    def SetMySG(self, iSG):
        pass

    
    def SetShopItem(self, dShopItem):
        dDataList = []
        dSpeInfoList = []
        for iId, dData in dShopItem.items():
            if dData[double122019define.ITEM_SPE_TYPE]:
                dSpeInfoList.append(dData)
                continue
            dDataList.append(dData)
        
        (misc.DeepCopy(dDataList),)
        self.SetSpeItem(dSpeInfoList)

    
    def SetSpeItem(self, dShopItem):
        if not dShopItem:
            return None
        
        self.m_oSpeItemList = []
        for i in range(2):
            oItem = dShopItem[i]
            i += 1
            bLock = oItem[double122019define.ITEM_LOCK_TYPE] == double122019define.ITEM_LOCK
            iNum = oItem[double122019define.ITEM_LIMIT_BUY_COUNT]
            self.GetObject('img_lock%d' % i).SetShow(bLock)
            self.GetObject('text_unlocktips%d' % i).SetShow(bLock)
            self.GetObject('btn_buyspeitem%d' % i).SetShow(not bLock)
            self.GetObject('hloc_spe_item%d' % i).SetEnterCB(misc.Functor(self.OnHotBoxEnter, i))
            self.GetObject('hloc_spe_item%d' % i).SetLeaveCB(misc.Functor(self.OnHotBoxLeave, i))
            if oItem['shape'] == itemdefine.ID_MOONLIGHT_CASE:
                self.GetObject('txt_prize%d' % i).SetText(str(oItem['sg_price']))
            
            oImg = CBackItemIcon(self.GetObject('loc_item%d' % i))
            oImg.SetItemID(oItem[double122019define.ITEM_ID])
            oImg.SetZ(1)
            oImg.CreateBackNeedItemIcon(oItem[double122019define.ITEM_SHAPE], iNum, 0, False)
            oImg.SetExtMsg(oItem[double122019define.ITEM_DESC])
            if iNum == 0:
                self.GetObject('btn_buyspeitem%d' % i).SetText('\xa4w\xc1\xca\xb6R')
                self.GetObject('btn_buyspeitem%d' % i).Enable(False)
                oImg.SetItemIconGrey()
            else:
                self.GetObject('btn_buyspeitem%d' % i).SetText('\xc1\xca \xb6R')
                self.GetObject('btn_buyspeitem%d' % i).Enable(True)
            if oItem[double122019define.ITEM_BIND_TYPE] == 1:
                iKey = item.MARK_BOUND
            elif oItem[double122019define.ITEM_BIND_TYPE] == 2:
                iKey = item.MARK_JINGPIN
            else:
                iKey = None
            oImg.GetBackNeedItemIcon().SetKey(iKey)
            if not bLock and iNum != 0:
                oAni = interface.CSpriteObject(oImg, 'item44/select.spr', interface.ITEM_PATH)
                oAni.SetZ(10)
                oAni.CreateCommand(1, 'animation')
                oAni.SetPos(21, 21)
                oImg.m_oLimitBuyAni = oAni
            
            self.m_oSpeItemList.append(oImg)
        

    
    def SetPriceText(self, iOldPrice, iNewPrice):
        self.ShowDelLines(len(str(iOldPrice)), iOldPrice > iNewPrice)
        self.GetObject('txt_oldprize').SetText(str(iOldPrice))
        self.GetObject('txt_newprize').SetText(str(iNewPrice))

    
    def GetDiscountUsedDlgShow(self):
        if self.m_oDiscountUsedDialog:
            return self.m_oDiscountUsedDialog.GetShow()
        
        return False

    
    def SetDiscountUsed(self, iUsedDiscountType):
        import helper2019double12
        if iUsedDiscountType <= 0:
            if not self.m_oDiscountTypeListDialog:
                self.m_oDiscountTypeListDialog = C2019Double12DiscountTypeDialog(self)
                interface.AlignObjects(self.m_oDiscountTypeListDialog, self.GetObject('loc_card'), interface.ALIGN_CENTER_MIDDLE)
            
            if self.m_oDiscountUsedDialog:
                self.m_oDiscountUsedDialog.SetShow(False)
            
            self.m_oDiscountTypeListDialog.SetShow(True)
            (iOldPrice, iDiscountType) = helper2019double12.CalDiscountInfo()
            self.m_oDiscountTypeListDialog.SetDiscountType(iDiscountType)
        elif self.m_oDiscountTypeListDialog:
            self.m_oDiscountTypeListDialog.SetShow(False)
        
        if not self.m_oDiscountUsedDialog:
            self.m_oDiscountUsedDialog = C2019Double12DiscountUsedDialog(self)
            interface.AlignObjects(self.m_oDiscountUsedDialog, self.GetObject('loc_card'), interface.ALIGN_CENTER_MIDDLE)
        
        self.m_oDiscountUsedDialog.SetShow(True)
        self.m_oDiscountUsedDialog.SetUsedDiscountType(iUsedDiscountType)

    
    def OnHotBoxEnter(self, iPos):
        iPos -= 1
        self.m_oSpeItemList[iPos].GetBackNeedItemIcon().Enter()

    
    def OnHotBoxLeave(self, iPos):
        iPos -= 1
        self.m_oSpeItemList[iPos].GetBackNeedItemIcon().Leave()

    
    def SetCartRedDot(self, iCount):
        if iCount > 999:
            iCount = 999
        
        if iCount <= 0:
            self.GetObject('img_red').SetShow(False)
            self.GetObject('text_num').SetShow(False)
        else:
            self.GetObject('img_red').SetShow(True)
            self.GetObject('text_num').SetShow(True)
            self.GetObject('text_num').SetText(str(iCount))

    
    def GetCartRedShow(self):
        return self.GetObject('img_red').GetShow()



class CBackItemIcon(makeitemicon.CBackItem):
    
    def __init__(self, oParent):
        makeitemicon.CBackItem.__init__(self, oParent)
        self.m_iItemID = 0

    
    def SetItemID(self, iItemID):
        self.m_iItemID = iItemID

    
    def GetItemID(self):
        return self.m_iItemID
