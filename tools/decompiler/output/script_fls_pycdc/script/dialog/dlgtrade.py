# pycdc 交叉复核产物 · script.fls entry 4762
# co_filename(原始)='script/dialog/dlgtrade.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4762.pyc (Python 2.5)

import combdialog
import combmacro
import interface
import permission
import style
import tipsclosemgr
import ui
import wrapinterface
import itemdefine
import dlgtattoo
SHAPE2BUYNUMBER = {
    25007: 10,
    72008: 1 }
g_TradeDialog = None
g_BoughtTaskItem = []
g_iDefaultChoiceShape = None
g_bFlagClosePracticeDlg = False

def ModuleReset():
    global g_TradeDialog, g_iDefaultChoiceShape, g_bFlagClosePracticeDlg, g_BoughtTaskItem
    g_TradeDialog = None
    g_iDefaultChoiceShape = 0
    g_bFlagClosePracticeDlg = False
    g_BoughtTaskItem = []
    CChushenDlg.ResetClear()


def IsBoughtTaskItem(shape):
    if shape in g_BoughtTaskItem:
        return True
    
    return False


def ConvertToPos(par, child):
    (parX, parY) = par.GetPos()
    (childX, childY) = child.GetPos()
    x = parX + childX
    y = parY + childY
    return (x, y)


def SetPraticeDlgCloseFlag(bClose = False):
    global g_bFlagClosePracticeDlg
    g_bFlagClosePracticeDlg = bClose


def GetPracticeDlgCloseFlag():
    return g_bFlagClosePracticeDlg


def SetRideDownGradeDefaultNum(iNum):
    import itemdefine
    SHAPE2BUYNUMBER[itemdefine.ID_HORSE_REVERSE_CRYSTAL] = iNum


def GetRideDownGradeDefaultNum():
    import itemdefine
    SHAPE2BUYNUMBER[itemdefine.ID_HORSE_REVERSE_CRYSTAL] = 0


class CGoodsBox(interface.CClickBox):
    
    def __init__(self, parent, x, y, igsidx, mid):
        interface.CClickBox.__init__(self, parent, 146, 52, alpha = 0, msgid = mid)
        self.SetPos(x, y)
        self.m_IgsIdx = igsidx
        row = igsidx / 4
        col = igsidx % 4
        self.m_Idx = col * 6 + row
        self.m_Selected = False
        self.m_Data = None
        self.m_ExtText = None
        self.m_GoodBoxBG = None
        self.m_sInfo = ''
        self.m_iDetailID = 0

    
    def SetIconPos(self, iFixedPosX, iFixedPosY):
        (x, y) = self.GetPos()
        self.m_IconPosX = iFixedPosX - x
        self.m_IconPosY = iFixedPosY - y

    
    def SetDetailID(self, iDetailID):
        self.m_iDetailID = iDetailID

    
    def SetGoodBoxBG(self, shadowbg):
        self.m_GoodBoxBG = shadowbg
        if shadowbg and shadowbg.Get():
            shadowbg.Get().SetFrame(0)
        

    
    def HasData(self):
        return self.m_Data is not None

    
    def SetItemIdx(self, idx):
        self.m_ItemInfoIdx = idx

    
    def SetGoodInfo(self, shape, num, price, desc, exttext = None):
        self.m_Data = (shape, num, price)
        self.m_ExtText = exttext
        self.CreateIcon(shape)
        self.CreateNameObj(desc)

    
    def SetEmpty(self):
        self.m_Data = None
        self.m_ExtText = None
        self.m_Icon = None
        self.m_NameObj = None
        self.m_sInfo = ''

    
    def CreateIcon(self, shape):
        import item
        self.m_Icon = item.CreateItem44Image(self, shape)
        self.m_Icon.SetPos(self.m_IconPosX, self.m_IconPosY)
        if self.m_ExtText:
            wrapinterface.ShowExt(self.m_Icon, self.m_ExtText, 32, 8, interface.FontLT12E_1)
        

    
    def CreateNameObj(self, desc):
        self.m_sInfo = desc
        color = interface.COLOR_1
        if self.m_Selected:
            color = interface.COLOR_385
        
        self.m_NameObj = interface.CRichTextObject(self, 100, interface.FontLT12_1, desc, color)
        (_, h) = self.GetSize()
        (_, nameh) = self.m_NameObj.GetSize()
        (offx, offy) = style.GetIntTuple('dlgtrade.CGoodsBox', 'namepos')
        self.m_NameObj.SetPos(offx, (h - nameh) / 2 + 2 + offy)

    
    def GetPrice(self):
        if self.m_Data:
            return self.m_Data[2]
        else:
            return 0

    
    def GetShape(self):
        if self.m_Data:
            return self.m_Data[0]
        else:
            return 0

    
    def Enter(self):
        if tipsclosemgr.IsHandle():
            return None
        
        if self.m_Data is None:
            return None
        
        if hasattr(self, 'm_ItemInfoIdx'):
            import dlggetinfo
            self.m_Tips = dlggetinfo.ShowTradeItemInfo(self.m_Data[0], self.m_ItemInfoIdx, iDetailID = self.m_iDetailID)
            tipsclosemgr.Regist(self.m_Tips)
            if self.m_ExtText:
                wrapinterface.ShowExt(self.m_Tips, self.m_ExtText, 90, 18, interface.FontST36D)
            
        
        if self.m_Selected:
            return None
        
        if self.m_GoodBoxBG.Get():
            self.m_GoodBoxBG.Get().SetFrame(2)
        

    
    def Leave(self):
        tipsclosemgr.CheckClose()
        self.m_Tips = None
        if self.m_Selected:
            return None
        
        if self.m_GoodBoxBG.Get():
            self.m_GoodBoxBG.Get().SetFrame(0)
        

    
    def SetCheck(self, flag):
        self.m_Selected = flag
        igs = self.m_GoodBoxBG.Get()
        if igs is None:
            return None
        
        if flag:
            igs.SetFrame(1)
        else:
            igs.SetFrame(0)
        self.CreateNameObj(self.m_sInfo)

    
    def SetFlash(self, bFlash):
        if bFlash and self.m_Icon:
            (x, y) = self.m_Icon.GetPos()
            z = self.m_Icon.GetZ()
            flashObj = interface.CSpriteObject(self, 'item44/select.spr', 'item')
            (offx, offy) = style.GetIntTuple('dlgtrade.CGoodsBox', 'flashpos')
            flashObj.SetPos(x + offx, y + offy)
            flashObj.SetZ(z + 1)
            flashObj.CreateCommand(1, 'animation')
        else:
            flashObj = None
        self.m_FlashObj = flashObj

    
    def SetHint(self, bHint):
        sPath = style.GetPath('combdialog/\xd4\xd3\xcd\xbc/\xd0\xc2\xca\xd6\xbc\xfd\xcd\xb7\xd7\xf3.igs')
        iTime = style.GetInt('dlgtrade.CGoodsBox', 'hinttime')
        if bHint and self.m_Icon:
            (x, y) = self.m_Icon.GetPos()
            (w, h) = self.m_Icon.GetSize()
            z = self.m_Icon.GetZ()
            if interface.IsNewStyle():
                hintObj = wrapinterface.CreateZhiYinMini(self, '\xa5\xaa', x + w + 100, y + h / 2 + 8)
            else:
                hintObj = ui.CImage(self, sPath, interface.UIPath)
                hintObj.CreateCommand(iTime, 'animation')
                hintObj.SetPos(x + w + 100, y + h / 2 + 8)
            hintObj.SetZ(z + 1)
        else:
            hintObj = None
        self.m_HintObj = hintObj



class CTradeBase(combdialog.CCombDialog):
    
    class CAutoEdit(wrapinterface.CNumberEdit):
        
        def SetMaxNum(self, num):
            self.m_MaxNum = num

        
        def AddChar(self, char):
            wrapinterface.CNumberEdit.AddChar(self, char)
            if not hasattr(self, 'm_Ignore') and self.m_Ignore:
                self._OnChange()
            

        
        def DeleteChar(self):
            wrapinterface.CNumberEdit.DeleteChar(self)
            self._OnChange()

        
        def _OnChange(self):
            
            try:
                amount = int(self.GetText())
            except ValueError:
                amount = 0

            if hasattr(self, 'm_MaxNum') and amount > self.m_MaxNum:
                amount = self.m_MaxNum
                self.m_Ignore = True
                self.SetText(str(self.m_MaxNum))
                self.m_Ignore = False
            
            if self.GetParent() and hasattr(self.GetParent(), 'OnEditChange'):
                self.GetParent().OnEditChange(self)
            


    DIALOG_PATH = 'dialog/trade.dlg'
    
    def __init__(self, ticketid, itype = 0, responseID = 0, iDetailID = 0):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, self.DIALOG_PATH)
        interface.Center(self)
        self.m_SelectBox = -1
        self.m_CurrPage = 0
        self.m_iLastSelType = 0
        self.m_iDetaildID = iDetailID
        self.GetObject('pageup').Enable(False)
        self.GetObject('pagedown').Enable(False)
        self.UpdateBaseInfo(ticketid, itype, responseID)
        self.CreateNumberEdit()
        self.CreateDialogDesc()
        self.CreatePyCommand(9000, CloseDlg)
        self.InitSingle()

    
    def InitSingle(self):
        import commoncb
        commoncb.RegistCB(commoncb.USE_FLYITEM, self, 'CloseWindow')

    
    def InitBuyList(self):
        buyLst = self.GetObject('buylist')
        self.m_BuyList = []
        oIconLst = self.GetObject('loc_icon_pos')
        goodBoxCls = self.GetBoxClass()
        for idx in xrange(24):
            (x, y) = ConvertToPos(buyLst, buyLst.m_Imagess[idx])
            (icon_x, icon_y) = oIconLst.GetArryPosByIdx(idx)
            box = goodBoxCls(self, x, y, idx, idx + 10)
            box.SetIconPos(icon_x, icon_y)
            box.m_ItemInfoIdx = (idx % 4) * 6 + idx / 4
            box.SetGoodBoxBG(interface.CShadowObject(buyLst.m_Imagess[idx]))
            self.m_BuyList.append(box)
        

    
    def CreateDialogDesc(self):
        pass

    
    def CreateNumberEdit(self):
        self.m_BuyAmountEdit = combmacro.CEDIT(CTradeBase.CAutoEdit, 'amount_edit', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_BuyAmountEdit.Active(True)
        self.m_BuyAmountEdit.Enable(not (self.m_Type))
        self.SetEditMaxNum()

    
    def SetEditMaxNum(self):
        self.m_BuyAmountEdit.SetMaxNum(300)

    
    def CreateCashTxt(self, ticketid):
        if ticketid is None:
            cashDesc = '\xb7\xed\xabe\xb2{\xaa\xf7'
            cashStr = 'm_Cash'
            if interface.IsStyle4():
                self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xb2{\xaa\xf7')
            else:
                font = interface.FontLT16_9
                color = interface.COLOR_10
                self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, cashDesc, font, color)
            import hero
            hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', ((cashStr, 0, 0),), self)
        elif interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xbb\xc8\xb2\xbc\xaa\xf7\xc3B')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xbb\xc8\xb2\xbc\xaa\xf7\xc3B', interface.FontLT16_2, interface.COLOR_10)
        import item
        import re
        it = item.GetItem(ticketid)
        if not hasattr(it, 'm_InfoExt') or it.m_InfoExt is None:
            import netitem
            netitem.C2SItemString(ticketid, 0)
            return None
        
        patt = re.compile('\xad\xb1\xad\xc8[ ]*[0-9]+')
        mo = patt.search(it.m_InfoExt)
        if mo is not None:
            
            try:
                ticket_price = int(it.m_InfoExt[mo.start() + 4:mo.end()].strip())
            except ValueError:
                return None

            self.SetTicketPrice(ticket_price)
        

    
    def SetTicketPrice(self, ticket_price):
        self.m_TicketCashObj = combmacro.CTEXT(interface.CTextObject, 'curr_cash', self, str(ticket_price), interface.FontLT14_3, 16777215)
        self.m_TicketCash = ticket_price

    
    def SetTotalPrice(self, amount, price):
        if self.m_SelectBox < 0:
            self.m_TotalPriceObj = combmacro.CTEXT(interface.COverstrikingTextObject, 'total_price', self, '', interface.FontLT14_3, interface.COLOR_9)
            return None
        
        totalprice = CTEXT
        color = self.GetTotalPriceInfo(amount, price)
        if totalprice > 0:
            import misc
            self.m_TotalPriceObj = combmacro.CTEXT(interface.CTextObject, 'total_price', self, misc.ChangeMoney(str(totalprice)), interface.FontLT14_3, color)
        else:
            self.m_TotalPriceObj = None

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        allPoint = None if getattr(self, 'm_TicketCash', None) else hero.g_Prop.m_Cash
        color = None if totalprice > allPoint else interface.COLOR_5
        return (totalprice, color)

    
    def OnEditChange(self, edit):
        amount = 0
        
        try:
            amount = int(self.m_BuyAmountEdit.GetText())
        except ValueError:
            pass

        price = self.m_BuyList[self.m_SelectBox].GetPrice()
        self.SetTotalPrice(amount, price)
        if not price:
            return None
        
        self.SetCanBuyAmount(amount, price)

    
    def SetCanBuyAmount(self, amount, price):
        pass

    
    def GetBoxClass(self):
        return CGoodsBox

    
    def SetBuyList(self, buylist):
        import dlggetinfo
        dlggetinfo.ClearItemInfo(4)
        oIconLst = self.GetObject('loc_icon_pos')
        goodBoxCls = self.GetBoxClass()
        buyLstCtrl = self.GetObject('buylist')
        if len(buylist) > 24:
            for page in xrange(len(buylist) / 24):
                for idx in xrange(24):
                    (x, y) = ConvertToPos(buyLstCtrl, buyLstCtrl.m_Imagess[idx])
                    (icon_x, icon_y) = oIconLst.GetArryPosByIdx(idx)
                    box = goodBoxCls(self, x, y, idx, (page + 1) * 24 + idx + 10)
                    box.SetIconPos(icon_x, icon_y)
                    box.SetDetailID(self.m_iDetaildID)
                    box.m_ItemInfoIdx = (page + 1) * 24 + (idx % 4) * 6 + idx / 4
                    box.SetGoodBoxBG(interface.CShadowObject(buyLstCtrl.m_Imagess[idx]))
                    box.SetShow(False)
                    self.m_BuyList.append(box)
                
            
            self.GetObject('pagedown').Enable(True)
        
        for idx, data in enumerate(buylist):
            page = idx / 24
            count = idx - page * 24
            row = count % 6
            col = count / 6
            box = self.m_BuyList[row * 4 + col + page * 24]
            goodInfo = self.GetGoodInfo(data[0], data[1], data[2])
            box.SetGoodInfo(*goodInfo)
            box.SetDetailID(self.m_iDetaildID)
        

    
    def UpdateBaseInfo(self, iTicketid, iType = 0, iResponseID = 0):
        self.m_Type = iType
        self.m_ResponseID = iResponseID
        self.CreateCashTxt(iTicketid)
        self.InitBuyList()

    
    def GetGoodBoxByShape(self, iShape):
        for box in self.m_BuyList:
            if not box.HasData():
                continue
            
            tData = box.m_Data
            if tData[0] == iShape:
                return box
                continue
        

    
    def SelectDefault(self, iShape):
        pBox = self.GetGoodBoxByShape(iShape)
        if not pBox:
            return None
        
        pBox.LeftUp()

    
    def GetGoodInfo(self, shape, num, price):
        name = GetNameWithPeiFang(shape)
        tempPrice = price
        desc = name
        if num > 1 and num != 65535:
            desc = '%s (%d)' % (name, num)
        
        if tempPrice > 10000:
            tempstr = str(price)
            tempPrice = ''.join([
                tempstr[:-4],
                ',',
                tempstr[-4:None]])
        
        desc += '#r\xbb\xf9\xae\xe6: %s' % tempPrice
        return (shape, num, price, desc)

    
    def DoBuy(self, sel, amount):
        if sel < 0 or amount <= 0:
            return None
        
        count = sel - self.m_CurrPage * 24
        row = count / 4
        col = count % 4
        index = col * 6 + row
        
        try:
            box = self.m_BuyList[sel]
        except IndexError:
            return None

        if not box.HasData():
            return None
        
        import netnpc
        import netcommon
        netnpc.C2SNpcBuy(index + self.m_CurrPage * 24, amount, self.m_ResponseID)

    
    def RefreshFlashItem(self, itemID):
        import task
        import item
        if item.PackIsFull():
            return None
        
        taskItems = task.GetAllItems(True)
        if self.m_CurrPage >= 0:
            for i in xrange(24):
                box = self.m_BuyList[24 * self.m_CurrPage + i]
                if box.GetShape() == itemID and itemID in taskItems:
                    box.SetFlash(False)
                    g_BoughtTaskItem.append(itemID)
                    continue
            
        

    
    def ShowPage(self, page):
        import task
        import item
        self.HideUpPageItems()
        for oBuyObj in self.m_BuyList:
            oBuyObj.SetShow(False)
        
        selBoxObj = None
        itemDct = task.GetAllItems()
        for i in range(0, 24):
            box = self.m_BuyList[24 * page + i]
            box.SetShow(True)
            if box.m_Data:
                (shape, num, price) = box.m_Data
                if shape in itemDct:
                    pass
                box.SetHint(12601 in itemDct[shape])
                if shape in itemDct:
                    pass
                bTaskItem = not IsBoughtTaskItem(shape)
                box.SetFlash(bTaskItem)
                if bTaskItem and selBoxObj is None and not item.HasTaskItem(shape):
                    selBoxObj = box
                    selBoxObj.LeftUp()
                
            not item.HasTaskItem(shape)
        
        self.m_CurrPage = page
        self.EnablePageBtns(page)

    
    def HideUpPageItems(self):
        if self.m_CurrPage >= 0:
            nLen = len(self.m_BuyList)
            for i in xrange(nLen):
                iCurIndex = 24 * self.m_CurrPage + i
                if iCurIndex >= nLen:
                    continue
                
                box = self.m_BuyList[24 * self.m_CurrPage + i]
                box.SetShow(False)
                if box.m_Selected == True:
                    box.SetCheck(False)
                    self.m_SelectBox = -1
                    continue
            
        

    
    def EnablePageBtns(self, page):
        self.GetObject('pageup').Enable(True)
        self.GetObject('pagedown').Enable(True)
        import math
        lastpage = int(math.ceil(len(self.m_BuyList) / 24) - 1)
        if page <= 0:
            self.GetObject('pageup').Enable(False)
        
        if page >= lastpage:
            self.GetObject('pagedown').Enable(False)
        
        if page <= 0:
            pass
        isShield = page >= lastpage
        self.SwitchPageBtns(isShield)

    
    def SwitchPageBtns(self, isShield):
        if isShield:
            self.GetObject('pageup').SetShow(False)
            self.GetObject('pagedown').SetShow(False)
        else:
            self.GetObject('pageup').SetShow(True)
            self.GetObject('pagedown').SetShow(True)

    
    def SetHint(self, objname):
        obj = self.GetObject(objname)
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        z = obj.GetZ()
        if interface.STYLE == 1:
            hintObj = interface.CSpriteObject(self, 'combdialog2/\xd4\xd3\xcd\xbc/\xd0\xc2\xca\xd6\xbc\xfd\xcd\xb7\xd3\xd2.spr', interface.UIPath)
            hintObj.CreateCommand(2, 'animation')
            hintObj.SetPos(x, y + h / 2 + 2)
        elif interface.IsNewStyle():
            hintObj = wrapinterface.CreateZhiYinMini(self, '\xa5k', x, y + h / 2 + 2)
        else:
            hintObj = ui.CImage(self, 'combdialog/\xd4\xd3\xcd\xbc/\xd0\xc2\xca\xd6\xbc\xfd\xcd\xb7\xd3\xd2.igs', interface.UIPath)
            hintObj.CreateCommand(5, 'animation')
            hintObj.SetPos(x, y + h / 2 + 2)
        hintObj.SetZ(z + 10)
        self.m_HintObj = hintObj

    
    def GetDefaultBuyNumber(self, idx, isright):
        shape = self.m_BuyList[idx].m_Data[0]
        if isright and shape in SHAPE2BUYNUMBER.keys():
            return self.m_BuyList[idx].m_Data[1]
        else:
            iNum = SHAPE2BUYNUMBER.get(shape, 1)
            if shape == itemdefine.ID_HORSE_REVERSE_CRYSTAL:
                SetRideDownGradeDefaultNum(1)
            
            return iNum

    
    def CloseWindow(self):
        CloseDlg()

    
    def GetCount(self, idx, isright):
        if self.m_SelectBox == idx:
            
            try:
                count = int(self.m_BuyAmountEdit.GetText())
            except ValueError:
                count = 0

            shape = self.m_BuyList[idx].m_Data[0]
            count += (1, -1)[isright]
            if not (self.m_iLastSelType) and isright:
                count = self.GetDefaultBuyNumber(idx, isright)
            
        else:
            count = self.GetDefaultBuyNumber(idx, isright)
        return count

    
    def OnClickGood(self, idx, isright):
        if idx >= len(self.m_BuyList) or not self.m_BuyList[idx].HasData():
            if isright:
                self.RightUp()
            
            return None
        
        self.m_BuyList[self.m_SelectBox].SetCheck(False)
        self.m_BuyList[idx].SetCheck(True)
        count = self.GetCount(idx, isright)
        self.m_iLastSelType = isright
        self.m_SelectBox = idx
        count = self.GetLimitAmount(idx, count)
        self.m_BuyAmountEdit.SetText('%d' % count)
        self.m_BuyAmountEdit.SetSelect(0, 999)
        self.SetTickctDlgLimit()
        if hasattr(self.m_BuyList[idx], 'm_HintObj') and self.m_BuyList[idx].m_HintObj:
            self.m_BuyList[idx].SetHint(False)
            self.SetHint('btn_Buy')
            self.m_bShowCloseHint = True
        

    
    def GetLimitAmount(self, idx, count):
        if count < 1:
            count = 1
        
        if self.m_Type == 1:
            if self.m_BuyList[idx].m_Data[1] != 0 and count > self.m_BuyList[idx].m_Data[1]:
                count = self.m_BuyList[idx].m_Data[1]
            
        elif self.m_BuyList[idx].m_Data[1] != 1 and count > self.m_BuyList[idx].m_Data[1]:
            count = self.m_BuyList[idx].m_Data[1]
        
        return count

    
    def GetCanBuyAmount(self):
        pass

    
    def GetSelInfo(self):
        selbox = self.m_SelectBox
        page = self.m_CurrPage
        
        try:
            cnt = int(self.m_BuyAmountEdit.GetText())
        except:
            cnt = 1

        return (selbox, page, cnt)

    
    def SetSelInfo(self, selbox, page, cnt):
        self.m_SelectBox = selbox
        self.m_BuyAmountEdit.SetText('%d' % cnt)
        self.ShowPage(page)
        if self.m_BuyList[selbox].HasData():
            self.m_BuyList[selbox].SetCheck(True)
        
        self.SetTickctDlgLimit()

    
    def SetTickctDlgLimit(self):
        if getattr(self, 'm_TicketCash', None):
            cash = self.m_TicketCash
            price = self.m_BuyList[self.m_SelectBox].GetPrice()
            self.m_BuyAmountEdit.SetMaxNum(cash / price)
        

    
    def OnMessage(self, msgid):
        if msgid in (1, 5):
            self.CloseWindow()
        elif msgid == 4:
            
            try:
                amount = int(self.m_BuyAmountEdit.GetText())
            except ValueError:
                return None

            self.DoBuy(self.m_SelectBox, amount)
            self.RefreshFlashItem(self.m_BuyList[self.m_SelectBox].GetShape())
            if hasattr(self, 'm_bShowCloseHint') and self.m_bShowCloseHint:
                self.SetHint('m_CloseBtn')
                self.m_bShowCloseHint = False
            
        elif msgid == 6:
            if self.m_CurrPage <= 0:
                return None
            
            self.ShowPage(self.m_CurrPage - 1)
        elif msgid == 7:
            if self.m_CurrPage >= len(self.m_BuyList) / 24:
                return None
            
            self.ShowPage(self.m_CurrPage + 1)
        elif msgid % interface.RIGHT_BUTTON_MESSAGE - 10 < len(self.m_BuyList):
            idx = msgid % interface.RIGHT_BUTTON_MESSAGE - 10
            self.OnClickGood(idx, msgid > interface.RIGHT_BUTTON_MESSAGE)
        



class CTradeDlg(CTradeBase):
    pass


class CGroceryTradeDlg(CTradeBase):
    
    def DoBuy(self, sel, amount):
        import hero
        import dlgitem
        import usermacro
        import dlgshenmoisland
        if sel < 0 or amount <= 0:
            return None
        
        
        try:
            box = self.m_BuyList[sel]
        except IndexError:
            return None

        if not box.HasData():
            return None
        
        if box.GetPrice() * amount > hero.GetProp('m_Cash', 0):
            if dlgshenmoisland.IsShenmoHuodong():
                usermacro.PROMPT_MSG('\xac\xa1\xb0\xca\xb2{\xaa\xf7\xa4\xa3\xa8\xac')
            else:
                dlgitem.OpenGetMoneyDlg()
            return None
        
        CTradeBase.DoBuy(self, sel, amount)

    
    def SetEditMaxNum(self):
        pass

    
    def GetGoodInfo(self, shape, num, price):
        if shape == 25100:
            self.m_BuyAmountEdit.SetMaxNum(200)
        
        name = GetNameWithPeiFang(shape)
        tempPrice = price
        desc = name
        if tempPrice > 10000:
            tempstr = str(price)
            tempPrice = ''.join([
                tempstr[:-4],
                ',',
                tempstr[-4:None]])
        
        desc += '#r\xbb\xf9\xae\xe6: %s' % tempPrice
        return (shape, num, price, desc)

    
    def GetLimitAmount(self, idx, count):
        if count < 1:
            count = 1
        
        if self.m_BuyList[idx].m_Data[1] != 1 and count > self.m_BuyList[idx].m_Data[1]:
            count = self.m_BuyList[idx].m_Data[1]
        
        return count

    
    def GetCanBuyAmount(self):
        price = self.m_BuyList[self.m_SelectBox].GetPrice()
        shape = self.m_BuyList[self.m_SelectBox].GetShape()
        if shape == 72375:
            import item
            dct = item.GetItemsByShape(72375)
            num = len(dct)
            maxAmount = None if num < 10 else 1
        else:
            import hero
            maxAmount = hero.g_Prop.m_Cash / price
        maxAmount = None if maxAmount > 0 else 1
        if self.m_BuyList[self.m_SelectBox].m_Data[1] != 1:
            maxAmount = min(self.m_BuyList[self.m_SelectBox].m_Data[1], maxAmount)
        
        return maxAmount

    
    def SetCanBuyAmount(self, amount, price):
        maxAmount = self.GetCanBuyAmount()
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        



class CHerbsTradeDlg(CGroceryTradeDlg):
    
    def GetCount(self, idx, isright):
        
        try:
            count = int(self.m_BuyAmountEdit.GetText())
        except ValueError:
            count = 0

        count += ((0, 0), (1, -1))[self.m_SelectBox == idx][isright]
        return count



class CPSTradeDlg(CTradeBase):
    
    def StartPSTimer(self, iTime):
        self.EndPSTimer()
        
        def tick(obj, iTime):
            obj.CreateTimeText(iTime)
            if iTime <= 0:
                obj.EndPSTimer()
                obj.OnPSTimerOut()
                return None
            
            return (iTime - 1,)

        self.CreateTimeText(iTime)
        self.m_PSTimer = self.CreatePyCommand(30, tick, iTime)

    
    def EndPSTimer(self):
        if hasattr(self, 'm_PSTimer') and self.m_PSTimer:
            self.m_PSTimer.Release()
            self.m_PSTimer = None
        

    
    def CreateTimeText(self, iTime):
        txt = '\xa4U\xa6\xb8\xa8\xea\xb7s\xae\xc9\xb6\xa1: %2d:%2d' % (iTime / 60, iTime % 60)
        self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, txt, interface.FontLT12_1, interface.COLOR_86, align = interface.ALIGN_LEFT | interface.ALIGN_BOTTOM)

    
    def OnPSTimerOut(self):
        import netnpc
        netnpc.C2SNpcBuy(0, 0)



class CPointTradeDlg(CTradeBase):
    
    def SetEditMaxNum(self):
        pass

    
    def CreateCashTxt(self, ipoint):
        import hero
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if ipoint is None:
            if interface.IsStyle4():
                self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xb2{\xaa\xf7')
            else:
                self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xb2{\xaa\xf7', font, color)
            hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_Cash', 0, 0),), self)
        elif interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xbfn\xa4\xc0')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xbfn\xa4\xc0', font, color)
        hero.g_Prop.m_CookPoint = ipoint
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_CookPoint', 0, 0),), self)

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        color = None if totalprice > hero.g_Prop.m_CookPoint else interface.COLOR_5
        return (totalprice, color)

    
    def SetCanBuyAmount(self, amount, price):
        import hero
        maxAmount = hero.g_Prop.m_CookPoint / price
        maxAmount = None if maxAmount > 0 else 1
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        

    
    def GetGoodInfo(self, shape, num, price):
        name = GetNameWithPeiFang(shape)
        tempPrice = price
        desc = name
        if num > 1 and num != 65535:
            desc = '%s (%d)' % (name, num)
        
        if tempPrice > 10000:
            tempstr = str(price)
            tempPrice = ''.join([
                tempstr[:-4],
                ',',
                tempstr[-4:None]])
        
        desc += '#r\xbb\xf9\xae\xe6: %s' % tempPrice
        desc = self.DealWithFood(desc, shape)
        return (shape, num, price, desc)

    
    def DealWithFood(self, desc, shape):
        import hero
        import itemdata
        shape = itemdata.Shape2Image(shape)
        if shape in hero.g_Skills[hero.ST_ABILITY].keys() and shape not in (21434, 25433):
            iLevel = hero.g_Skills[hero.ST_ABILITY][shape].m_Level
            sColor = style.GetStr(self.GetDlgPath(), 'foodcolor')
            desc += '#r%s\xb7\xed\xabe\xab~\xbd\xe8: %d' % (sColor, iLevel)
        
        return desc



class CPracticeDlg(CTradeBase):
    DIALOG_PATH = 'dialog/foodtrade.dlg'
    
    def __init__(self, ticketid, itype = 0, responseID = 0, iDetailID = 0):
        CTradeBase.__init__(self, ticketid, itype, responseID, iDetailID)
        dlgtattoo.CTattooDialog.SetTattooShopOpen(True)

    
    def SetEditMaxNum(self):
        pass

    
    def CreateCashTxt(self, ipoint):
        import hero
        font = interface.FontLT14_9
        color = interface.COLOR_10
        self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xa9\xe8\xa5\xce\xaa\xf7', font, color)
        self.m_CashNote2 = combmacro.CTEXT(interface.CTextObject, 'fightcashtxt', self, '\xb7\xed\xabe\xb2{\xaa\xf7', font, color)
        color1 = interface.COLOR_97
        tc = None if interface.IsNewStyle() else interface.CShadowText
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_FightCash', 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, tc, interface.FontLT14_3, color1),), self)
        hero.CreateCombDlgCash('cur_fightcash', 'dlgnewtrade', (('m_Cash', 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, tc, interface.FontLT14_3, color1),), self)

    
    def SetCanBuyAmount(self, amount, price):
        import hero
        maxAmount = (hero.g_Prop.m_FightCash + hero.g_Prop.m_Cash) / price
        maxAmount = None if maxAmount > 0 else 1
        if self.m_BuyList[self.m_SelectBox].m_Data[1] != 0 and amount > self.m_BuyList[self.m_SelectBox].m_Data[1]:
            maxAmount = min(self.m_BuyList[self.m_SelectBox].m_Data[1], maxAmount)
        
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        color1 = interface.COLOR_5
        if hero.g_Prop.m_FightCash >= totalprice or hero.g_Prop.m_Cash + hero.g_Prop.m_FightCash >= totalprice:
            color = color1
        else:
            color = interface.COLOR_32
        return (totalprice, color)

    
    def GetLimitAmount(self, idx, count):
        if count < 1:
            count = 1
        
        if self.m_BuyList[idx].m_Data[1] != 0 and count > self.m_BuyList[idx].m_Data[1]:
            count = self.m_BuyList[idx].m_Data[1]
        
        return count



class CFoodTradeDlg(CTradeBase):
    DIALOG_PATH = 'dialog/foodtrade.dlg'
    
    def SetEditMaxNum(self):
        pass

    
    def CreateCashTxt(self, ipoint):
        import hero
        font = interface.FontLT14_9
        color = interface.COLOR_10
        color1 = interface.COLOR_97
        self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xa9\xe8\xa5\xce', font, color)
        self.m_CashNote2 = combmacro.CTEXT(interface.CTextObject, 'fightcashtxt', self, '\xb7\xed\xabe\xb2{\xaa\xf7', font, color)
        tc = None if interface.IsNewStyle() else interface.CShadowText
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_FightCash', 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, tc, interface.FontLT14_3, color1),), self)
        hero.CreateCombDlgCash('cur_fightcash', 'dlgnewtrade', (('m_Cash', 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, tc, interface.FontLT14_3, color1),), self)

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        color1 = interface.COLOR_5
        color = None if totalprice > hero.g_Prop.m_Cash + hero.g_Prop.m_FightCash else color1
        return (totalprice, color)

    
    def SetCanBuyAmount(self, amount, price):
        import hero
        curCash = None if hero.g_Prop.m_FightCash else hero.g_Prop.m_Cash
        maxAmount = curCash / price
        maxAmount = None if maxAmount > 0 else 1
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        



class CZPUseCashDlg(CTradeBase):
    
    def CreateDialogDesc(self):
        self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, '#R\xbe\xc7\xb2\xdf\xbc@\xb1\xa1\xa7\xde\xaf\xe0-\xa5j\xb8\xb3\xb5\xfb\xa6\xf4\xab\xe1\xa5i\xa5H\xc0\xf2\xb1o\xa7\xe9\xa6\xa9\xc0u\xb4f\xa1A\xa7\xde\xaf\xe0\xb5\xa5\xaf\xc5\xb6V\xb0\xaa\xa1A\xa7\xe9\xa6\xa9\xc0u\xb4f\xb6V\xa6h\xa1C#n', interface.FontLT12_1)

    
    def CloseWindow(self):
        
        def OK(dlg):
            CloseDlg()

        import commondialog
        dlg = commondialog.ShowMessageBox('\xbdT\xa9w\xadn\xc3\xf6\xb3\xac\xb0\xd3\xab~\xa6C\xaa\xed\xb6\xdc\xa1H\xc3\xf6\xb3\xac\xab\xe1\xbb\xdd\xadn#R60\xa4\xc0\xc4\xc1#n\xa4~\xaf\xe0\xa6A\xa6\xb8\xacd\xac\xdd', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OK, None))

    
    def GetLimitAmount(self, idx, count):
        return 1

    
    def GetGoodInfo(self, shape, level, price):
        import itemdata
        iPrice = int(((100 - level * 5) / 100) * price)
        name = itemdata.GetData(shape)[0]
        if level:
            desc = '%s#r\xad\xec\xbb\xf9\xa1G%d#r\xa7\xe9\xab\xe1\xa1G%d' % (name, price, int(((100 - level * 5) / 100) * price))
        else:
            desc = '%s#r\xad\xec\xbb\xf9\xa1G%d' % (name, price)
        return (shape, level, iPrice, desc)



class CZPUseFightCashDlg(CTradeBase):
    
    def CreateDialogDesc(self):
        self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, '#R\xbe\xc7\xb2\xdf\xbc@\xb1\xa1\xa7\xde\xaf\xe0-\xa5j\xb8\xb3\xb5\xfb\xa6\xf4\xab\xe1\xa5i\xa5H\xc0\xf2\xb1o\xa7\xe9\xa6\xa9\xc0u\xb4f\xa1A\xa7\xde\xaf\xe0\xb5\xa5\xaf\xc5\xb6V\xb0\xaa\xa1A\xa7\xe9\xa6\xa9\xc0u\xb4f\xb6V\xa6h\xa1C#n', interface.FontLT12_1)

    
    def CreateCashTxt(self, iPoint):
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xa9\xe8\xa5\xce\xaa\xf7')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xa9\xe8\xa5\xce\xaa\xf7', font, color)
        import hero
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_FightCash', 0, 0),), self)

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        color = None if totalprice > hero.g_Prop.m_FightCash else interface.COLOR_5
        return (totalprice, color)

    
    def CloseWindow(self):
        
        def OK(dlg):
            CloseDlg()

        import commondialog
        dlg = commondialog.ShowMessageBox('\xbdT\xa9w\xadn\xc3\xf6\xb3\xac\xb0\xd3\xab~\xa6C\xaa\xed\xb6\xdc\xa1H\xc3\xf6\xb3\xac\xab\xe1\xbb\xdd\xadn#R60\xa4\xc0\xc4\xc1#n\xa4~\xaf\xe0\xa6A\xa6\xb8\xacd\xac\xdd', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OK, None))

    
    def GetLimitAmount(self, idx, count):
        return 1

    
    def GetGoodInfo(self, shape, level, price):
        import itemdata
        iPrice = int(((100 - level * 5) / 100) * price)
        name = itemdata.GetData(shape)[0]
        if level:
            desc = '%s#r\xad\xec\xbb\xf9\xa1G%d#r\xa7\xe9\xab\xe1\xa1G%d' % (name, price, int(((100 - level * 5) / 100) * price))
        else:
            desc = '%s#r\xad\xec\xbb\xf9\xa1G%d' % (name, price)
        return (shape, level, iPrice, desc)



class CLimitGoodsBox(CGoodsBox):
    
    def SetGoodInfo(self, iShape, iNum, iPrice, iLimit, sDesc):
        self.m_Data = (iShape, iNum, iPrice)
        self.CreateIcon(iShape)
        self.CreateNameObj(sDesc)
        self.ShowLimitInfo(iLimit, iNum)

    
    def ShowLimitInfo(self, iLimit, iNum):
        if iLimit == 1:
            self.m_iNumber = iNum
            self.m_bIsLimit = True
            (iX, iY) = self.m_Icon.GetPos()
            self.m_Title = interface.CTextObject(self, '%d' % iNum, interface.FontLT12E_1, 16777215)
            self.m_Title.SetPos(iX + 35, iY + 35)
            self.m_Img = ui.CImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xcf\xde\xb9\xba\xcd\xbc\xb1\xea/\xcf\xde\xb9\xba.png', interface.UIPath)
            self.m_Img.SetZ(500)
            if iNum <= 0:
                self.m_Icon.SetGrey()
                self.m_Img.SetGrey()
            
        else:
            self.m_bIsLimit = False

    
    def GetNumber(self):
        if hasattr(self, 'm_iNumber') and hasattr(self, 'm_bIsLimit'):
            if self.m_bIsLimit:
                return self.m_iNumber
            
        
        return 1



class CShiTuPointTradeDlg(CTradeBase):
    
    def CreateCashTxt(self, iPoint):
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xbfn\xa4\xc0')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xbfn\xa4\xc0', font, color)
        self.m_CurCash = combmacro.CTEXT(interface.CTextObject, 'curr_cash', self, str(iPoint), font, color)

    
    def InitBuyList(self):
        buyLst = self.GetObject('buylist')
        self.m_BuyList = []
        oIconLst = self.GetObject('loc_icon_pos')
        for idx in xrange(24):
            (x, y) = ConvertToPos(buyLst, buyLst.m_Imagess[idx])
            box = CLimitGoodsBox(self, x, y, idx, idx + 10)
            box.SetIconPos(oIconLst.GetArryPosByIdx(idx))
            box.m_ItemInfoIdx = (idx % 4) * 6 + idx / 4
            box.SetGoodBoxBG(interface.CShadowObject(buyLst.m_Imagess[idx]))
            self.m_BuyList.append(box)
        

    
    def GetGoodInfo(self, iShape, iNum, iPrice, iLimit):
        sName = GetNameWithPeiFang(iShape)
        tempPrice = iPrice
        sDesc = sName
        if iNum > 1 and iNum != 65535:
            sDesc = '%s (%d)' % (sName, iNum)
        
        if tempPrice > 10000:
            tempstr = str(iPrice)
            tempPrice = ''.join([
                tempstr[:-4],
                ',',
                tempstr[-4:None]])
        
        sDesc += '#r\xbb\xf9\xae\xe6: %s' % tempPrice
        return (iShape, iNum, iPrice, iLimit, sDesc)

    
    def SetBuyList(self, buyList):
        import dlggetinfo
        dlggetinfo.ClearItemInfo(4)
        buyLstCtrl = self.GetObject('buylist')
        oIconLst = self.GetObject('loc_icon_pos')
        if len(buyList) > 24:
            for page in xrange(len(buyList) / 24):
                for idx in xrange(24):
                    (x, y) = ConvertToPos(buyLstCtrl, buyLstCtrl.m_Imagess[idx])
                    box = CLimitGoodsBox(self, x, y, idx, (page + 1) * 24 + idx + 10)
                    box.SetIconPos(oIconLst.GetArryPosByIdx(idx))
                    box.SetDetailID(self.m_iDetaildID)
                    box.m_ItemInfoIdx = (page + 1) * 24 + (idx % 4) * 6 + idx / 4
                    box.SetGoodBoxBG(interface.CShadowObject(buyLstCtrl.m_Imagess[idx]))
                    box.SetShow(False)
                    self.m_BuyList.append(box)
                
            
            self.GetObject('pagedown').Enable(True)
        
        for idx, data in enumerate(buyList):
            page = idx / 24
            count = idx - page * 24
            row = count % 6
            col = count / 6
            box = self.m_BuyList[row * 4 + col + page * 24]
            goodInfo = self.GetGoodInfo(*data)
            box.SetGoodInfo(*goodInfo)
            box.SetDetailID(self.m_iDetaildID)
        

    
    def OnClickGood(self, idx, isright):
        
        try:
            iCount = self.m_BuyList[idx].GetNumber()
            if iCount <= 0:
                import usermacro
                usermacro.PROMPT_MSG('\xa5\xbb\xa9P\xa7I\xb4\xab\xa4w\xb9F\xa4W\xad\xad\xa1A\xbd\xd0\xa6b\xa8C\xb6g\xa4@0\xa1G00\xa8\xea\xb7s\xab\xe1\xa6A\xa7I\xb4\xab')
                return None
        except:
            return None

        if idx >= len(self.m_BuyList) or not self.m_BuyList[idx].HasData():
            if isright:
                self.RightUp()
            
            return None
        
        self.m_BuyList[self.m_SelectBox].SetCheck(False)
        self.m_BuyList[idx].SetCheck(True)
        count = self.GetCount(idx, isright)
        self.m_iLastSelType = isright
        self.m_SelectBox = idx
        count = self.GetLimitAmount(idx, count)
        self.m_BuyAmountEdit.SetText('%d' % count)
        self.m_BuyAmountEdit.SetSelect(0, 999)
        self.SetTickctDlgLimit()
        if hasattr(self.m_BuyList[idx], 'm_HintObj') and self.m_BuyList[idx].m_HintObj:
            self.m_BuyList[idx].SetHint(False)
            self.SetHint('btn_Buy')
            self.m_bShowCloseHint = True
        



class CGroceryDlg(CTradeBase):
    
    def SetEditMaxNum(self):
        pass

    
    def CreateDialogDesc(self):
        self.m_Desc = combmacro.CTEXT(interface.CTextObject, 'box_amount', self, '\xa5k\xc1\xe4\xc2I\xc0\xbb\xc5\xdc\xac\xb0\xb3\xcc\xa4j\xc1\xca\xb6R\xbc\xc6\xb6q', interface.FontLT14_2, interface.COLOR_10)

    
    def GetLimitAmount(self, idx, count):
        if count < 1:
            count = 0
        
        if self.m_BuyList[idx].GetShape() not in (22300, 22301) and count > self.m_BuyList[idx].m_Data[1]:
            count = self.m_BuyList[idx].m_Data[1]
        
        return count

    
    def GetCanBuyAmount(self):
        price = self.m_BuyList[self.m_SelectBox].GetPrice()
        shape = self.m_BuyList[self.m_SelectBox].GetShape()
        if shape == 72375:
            import item
            dct = item.GetItemsByShape(72375)
            num = len(dct)
            maxAmount = None if num < 10 else 1
        else:
            import hero
            maxAmount = hero.g_Prop.m_Cash / price
        maxAmount = None if maxAmount > 0 else 1
        if self.m_BuyList[self.m_SelectBox].GetShape() not in (22300, 22301):
            maxAmount = min(self.m_BuyList[self.m_SelectBox].m_Data[1], maxAmount)
        
        return maxAmount

    
    def GetCount(self, idx, isright):
        import item
        if self.m_SelectBox == idx:
            
            try:
                count = int(self.m_BuyAmountEdit.GetText())
            except ValueError:
                count = 0

            if isright:
                count = min(self.GetCanBuyAmount(), 40 - item.GetGoodsNum())
            else:
                count += 1
        else:
            count = self.GetDefaultBuyNumber(idx, isright)
        return count

    
    def SetCanBuyAmount(self, amount, price):
        maxAmount = self.GetCanBuyAmount()
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        



class CGoldTradeDlg(CTradeBase):
    
    def SetEditMaxNum(self):
        self.m_BuyAmountEdit.SetMaxNum(200)

    
    def GetLimitAmount(self, idx, count):
        if self.m_BuyList[idx].m_Data[1] < 200:
            count = self.m_BuyList[idx].m_Data[1]
        else:
            count = 200
        if count < 1:
            count = 1
        
        return count



class CReputeTradeDlg(CTradeBase):
    
    def CreateCashTxt(self, ipoint):
        import hero
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if ipoint is None:
            if interface.IsStyle4():
                self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xb2{\xaa\xf7')
            else:
                self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xb2{\xaa\xf7', font, color)
            hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_Cash', 0, 0),), self)
            self.m_IsCash = True
        elif interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xb7\xed\xabe\xc1n\xb1\xe6')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xc1n\xb1\xe6', font, color)
        hero.g_Prop.m_CookPoint = ipoint
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_CookPoint', 0, 0),), self)

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        allPoint = None if getattr(self, 'm_IsCash', None) else hero.g_Prop.m_CookPoint
        color = None if totalprice > allPoint else interface.COLOR_5
        return (totalprice, color)

    
    def SetCanBuyAmount(self, amount, price):
        import hero
        maxAmount = hero.g_Prop.m_CookPoint / price
        maxAmount = None if maxAmount > 0 else 1
        if self.m_BuyList[self.m_SelectBox].m_Data[1] != 0 and amount > self.m_BuyList[self.m_SelectBox].m_Data[1]:
            maxAmount = min(self.m_BuyList[self.m_SelectBox].m_Data[1], maxAmount)
        
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        

    
    def GetLimitAmount(self, idx, count):
        if count < 1:
            count = 1
        
        if self.m_BuyList[idx].m_Data[1] != 0 and count > self.m_BuyList[idx].m_Data[1]:
            count = self.m_BuyList[idx].m_Data[1]
        
        return count

    
    def SetTradeKey(self, sKey):
        key2CashText = {
            'JingJiPoint6': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'XianziPoint': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'AnimalWarPoint': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'FXPoint2': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'ShenwuPoint': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'RongLianPoint': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'YardPoint': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'Maze': '\xb0g\xaec\xbfn\xa4\xc0',
            'ChristmasShift': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'zhidao': '\xb7\xed\xabe\xbfn\xa4\xc0',
            'DengmiPoint': '\xb7\xed\xabe\xbfn\xa4\xc0' }
        key2Title = {
            'Maze': '\xb0g\xaec\xb0\xd3\xab\xb0' }
        if sKey in key2CashText:
            if interface.IsStyle4():
                self.GetObject('cashtxt').SetText(key2CashText[sKey])
            else:
                font = interface.FontLT16_9
                self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, key2CashText[sKey], font, interface.COLOR_10)
        
        if sKey in key2Title:
            self.GetObject('noname0').ChgCaptionTxt(key2Title[sKey])
        

    
    def ShowTips(self, sKey):
        self.m_Skey = sKey
        objname = self.GetObject('img_Tips')
        (w, h) = objname.GetSize()
        (x, y) = objname.GetPos()
        self.m_BtnTips = interface.CButton(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), x, y, 168)
        self.m_BtnTips.m_ParentNotify = True

    
    def OnButtonEnter(self, btn):
        if self.m_Skey == 'GoodHeart':
            txt = '\xbe\xe1\xa5\xf4\xb6\xa4\xaa\xf8\xa1A\xb1a\xb7s\xa4H\xa1]\xa4\xf1\xa6\xdb\xa8\xad\xb5\xa5\xaf\xc5\xa7C10\xaf\xc5\xa5H\xa4W\xa1^\xa5\xb4\xb3\xa5\xa9\xc7\xa9\xce\xbex\xa8\xc6\xaa\xba\xa7\xaf\xa9\xc7\xa1A\xb4N\xa5i\xa5H\xc0\xf2\xb1o\xb5\xbd\xb4c\xad\xc8\xa1C\xa8C\xa6\xec\xb7s\xa4H\xb4\xa3\xa8\xd11\xc2I\xb5\xbd\xb4c\xad\xc8\xa1A\xb1a2\xa6\xec\xa5H\xa4W\xaa\xba\xb7s\xa4H\xa5i\xa5H\xc0\xf2\xb1o2\xc2I\xb5\xbd\xb4c\xad\xc8'
        elif self.m_Skey == 'FXPoint2':
            txt = '\xb6\xa4\xa5\xee\xa4\xa4\xa6p\xaaG\xa6\xb3\xa1u\xba\xd6\xbdt\xc0H\xa8\xad\xa1v\xba\xd9\xbf\xd7\xaa\xba\xaa\xb1\xaea\xa1]\xb6\xa4\xa5\xee\xac\xc9\xad\xb1\xa6W\xa6r\xac\xb0\xafS\xae\xed\xc3C\xa6\xe2\xa1^\xa1A\xb6\xa4\xaa\xf8\xa6b\xa5H\xa4U\xaa\xb1\xaak\xa5i\xa5H\xc0\xf2\xb1o\xa5\\\xbcw\xad\xc8\xa1G\xb0\xa3\xc5]\xa5\xf4\xb0\xc8\xa1B\xbe\xc7\xae{\xa5\xf4\xb0\xc8\xa1B\xb3\xa1\xa4\xc0\xb6g\xa5\xbd\xac\xa1\xb0\xca'
        
        self.m_Tips = wrapinterface.CTextTips(self, 200, txt, interface.FontLT14_3, direct = 0, owner = btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None



class CChushenBox(CGoodsBox):
    
    def CreateNameObj(self, desc):
        self.m_sInfo = desc
        txtLst = desc.split('#r')
        self.m_TextObjects = []
        (_, txtH) = (0, 0)
        for txt in txtLst:
            color = interface.COLOR_1
            if txt.startswith('#B'):
                txt = txt[2:]
                color = 255
            
            if txt.startswith('#Y'):
                txt = txt[2:]
                color = interface.COLOR_86
            
            txtObj = interface.CTextObject(self, txt, interface.FontLT12_1, color)
            (_, th) = txtObj.GetSize()
            txtH = txtH + th
            self.m_TextObjects.append(txtObj)
        
        (_, h) = self.GetSize()
        y = (h - txtH) / 2
        for txtObj in self.m_TextObjects:
            txtObj.SetPos(54, y)
            (_, th) = txtObj.GetSize()
            y += th
        

    
    def SetTextColor(self, color):
        if not getattr(self, 'm_TextObjects', None):
            return None
        
        for txtObj in self.m_TextObjects:
            txtObj.SetColor(color)
        

    
    def Enter(self):
        CGoodsBox.Enter(self)
        if hasattr(self, 'm_LearnLevel'):
            ext = '\xbb\xdd\xadn\xaa\xba\xb2i\xb6\xb9\xa7\xde\xaf\xe0\xb5\xa5\xaf\xc5\xa1G%d' % self.m_LearnLevel
            self.m_Tips.Refresh(ext)
        



class CChushenDlg(CTradeBase):
    s_CurTab = 0
    DIALOG_PATH = 'dialog/chushen/shipu.dlg'
    CHUSHEN_TIPS = [
        '\xb2\xa2\xa8\xfd\xb2i\xb6\xb9\xa1A\xaak\xa4O\xab\xec\xb4_\xae\xc4\xaaG\xb8\xfb\xb1j',
        '\xbb\xb6\xa8\xfd\xb2i\xb6\xb9\xa1A\xa4O\xb9D\xab\xec\xb4_\xae\xc4\xaaG\xb8\xfb\xb1j',
        '\xad\xbb\xa8\xfd\xb2i\xb6\xb9\xa1A\xa6U\xc4\xdd\xa9\xca\xab\xec\xb4_\xae\xc4\xaaG\xa5\xad\xa7\xa1']
    
    def ResetClear(cls):
        cls.s_CurTab = 0

    ResetClear = classmethod(ResetClear)
    
    def GetSkillLvl(self):
        import hero
        skillObj = hero.g_Skills[0].get(1114)
        if not skillObj:
            return 0
        
        return skillObj.m_Level

    
    def SetBuyList(self, dList):
        self.m_BuyDict = dList
        self.SetActiveTab(CChushenDlg.s_CurTab)

    
    def InitBuyList(self):
        pass

    
    def SetActiveTab(self, iTab):
        CChushenDlg.s_CurTab = iTab
        iType = iTab + 1
        buylist = self.m_BuyDict[iType]
        import dlggetinfo
        dlggetinfo.ClearItemInfo(4)
        color = interface.COLOR_110
        self.m_Text = combmacro.CRICHTEXT(interface.CRichTextObject, 'tips', self, CChushenDlg.CHUSHEN_TIPS[iTab], interface.FontLT12_1, color)
        obj = self.GetObject('btn_Item%d' % iType)
        if obj:
            obj.SetSelect(True)
        
        buyLst = self.GetObject('buylist')
        oIconLst = self.GetObject('loc_icon_pos')
        (baseX, baseY) = buyLst.GetPos()
        (offsetX, offsetY) = style.GetIntTuple(self.GetDlgPath(), 'food')
        self.m_BuyList = []
        for idx in xrange(24):
            x = baseX + (idx % 4) * 148 + offsetX
            y = baseY + (idx / 4) * 54 + offsetY
            (icon_x, icon_y) = oIconLst.GetArryPosByIdx(idx)
            box = CChushenBox(self, x, y, idx, idx + 10)
            box.SetIconPos(icon_x, icon_y)
            box.m_ItemInfoIdx = (idx % 4) * 6 + idx / 4
            box.SetGoodBoxBG(interface.CShadowObject(buyLst.m_Imagess[idx]))
            self.m_BuyList.append(box)
        
        skillLvl = self.GetSkillLvl()
        for idx, data in enumerate(buylist):
            page = idx / 24
            count = idx - page * 24
            row = count % 6
            col = count / 6
            box = self.m_BuyList[row * 4 + col + page * 24]
            (learnLvl, goodInfo) = self.GetGoodInfo(*data)
            box.m_LearnLevel = learnLvl
            box.SetGoodInfo(*goodInfo)
        

    
    def DoBuy(self, sel, amount):
        if sel < 0 or amount <= 0:
            return None
        
        count = sel - self.m_CurrPage * 24
        row = count / 4
        col = count % 4
        index = col * 6 + row
        
        try:
            box = self.m_BuyList[sel]
        except IndexError:
            return None

        if not box.HasData():
            return None
        
        idx = self.GetRealIdx(index + self.m_CurrPage * 24)
        import netcommon
        netcommon.C2SCookMasterBuy(idx, amount)

    
    def GetRealIdx(self, idx):
        lst = self.m_BuyDict[CChushenDlg.s_CurTab + 1]
        return lst[idx][-1]

    
    def SetEditMaxNum(self):
        pass

    
    def CreateCashTxt(self, ipoint):
        import hero
        font = interface.FontLT14_10
        color = interface.COLOR_10
        self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb7\xed\xabe\xbfn\xa4\xc0', font, color)
        hero.g_Prop.m_CookPoint = ipoint
        hero.CreateCombDlgCash('curr_cash', 'dlgnewtrade', (('m_CookPoint', 0, 0),), self)

    
    def GetTotalPriceInfo(self, amount, price):
        import hero
        totalprice = amount * price
        color = None if totalprice > hero.g_Prop.m_CookPoint else interface.COLOR_5
        return (totalprice, color)

    
    def SetCanBuyAmount(self, amount, price):
        import hero
        maxAmount = hero.g_Prop.m_CookPoint / price
        maxAmount = None if maxAmount > 0 else 1
        if maxAmount < amount:
            self.m_BuyAmountEdit.SetText('%d' % maxAmount)
        

    
    def GetGoodInfo(self, shape, num, price, realIdx):
        import cookdata
        import itemdata
        realShape = itemdata.Shape2Image(shape)
        data = cookdata.GetData(shape)
        name = data['name']
        learnLvl = data['learn_lv']
        tempPrice = price
        desc = name
        if num > 1 and num != 65535:
            desc = '%s (%d)' % (name, num)
        
        if tempPrice > 10000:
            tempstr = str(price)
            tempPrice = ''.join([
                tempstr[:-4],
                ',',
                tempstr[-4:None]])
        
        desc += '#r\xbb\xf9\xae\xe6: %s' % tempPrice
        desc = self.DealWithFood(desc, shape)
        return (learnLvl, (shape, num, price, desc))

    
    def DealWithFood(self, desc, shape):
        import hero
        import itemdata
        shape = itemdata.Shape2Image(shape)
        if shape in hero.g_Skills[hero.ST_ABILITY].keys() and shape not in (21434, 25433):
            iLevel = hero.g_Skills[hero.ST_ABILITY][shape].m_Level
            sColor = style.GetStr(self.GetDlgPath(), 'food')
            desc += '#r%s\xb7\xed\xabe\xab~\xbd\xe8: %d' % (sColor, iLevel)
        
        return desc

    
    def SetTradeKey(self, sKey):
        pass

    
    def SetDefaultValue(self):
        if getattr(self, 'm_BuyAmountEdit', None):
            amount_obj = self.m_BuyAmountEdit
            if amount_obj.GetText():
                amount_obj.SetText('')
            
            self.m_TotalPriceObj = None
        

    
    def CloseWindow(self):
        CTradeBase.CloseWindow(self)
        import hero
        hero.RemoveRefreshCallback('dlgnewtrade', (('m_CookPoint',),))

    
    def OnMessage(self, msgid):
        if msgid <= msgid:
            pass
        elif msgid <= 103:
            self.SetActiveTab(msgid - 100)
            self.SetDefaultValue()
        else:
            CTradeBase.OnMessage(self, msgid)



class CCarnivalTradeDlg(CTradeBase):
    
    def __init__(self, ticketid, itype = 0, responseID = 0, iDetailID = 0):
        CTradeBase.__init__(self, ticketid, itype, responseID, iDetailID)
        self.m_iCurPoint = ticketid

    
    def CreateCashTxt(self, iPoint):
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xb6g\xa6~\xbfn\xa4\xc0')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xb6g\xa6~\xbfn\xa4\xc0', font, color)
        self.m_CurCash = combmacro.CTEXT(interface.CTextObject, 'curr_cash', self, str(iPoint), interface.FontLT14_3, 16777215)

    
    def SetEditMaxNum(self):
        pass

    
    def GetCanBuyAmount(self):
        iPrice = self.m_BuyList[self.m_SelectBox].GetPrice()
        return max(self.m_iCurPoint / iPrice, 1)

    
    def SetCanBuyAmount(self, amount, price):
        iMaxAmount = self.GetCanBuyAmount()
        if amount > iMaxAmount:
            self.m_BuyAmountEdit.SetText('%d' % iMaxAmount)
        

    
    def GetTotalPriceInfo(self, amount, price):
        iTotalPrice = amount * price
        color = None if iTotalPrice > self.m_iCurPoint else interface.COLOR_5
        return (iTotalPrice, color)



class CGuessTradeDlg(CTradeBase):
    
    def __init__(self, ticketid, itype = 0, responseID = 0, iDetailID = 0):
        CTradeBase.__init__(self, ticketid, itype, responseID, iDetailID)
        self.m_iCurGuessPoint = ticketid

    
    def CreateCashTxt(self, iPoint):
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xc4v\xb2q\xbfn\xa4\xc0')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xc4v\xb2q\xbfn\xa4\xc0', font, color)
        self.m_CurCash = combmacro.CTEXT(interface.CTextObject, 'curr_cash', self, str(iPoint), interface.FontLT14_3, 16777215)

    
    def SetEditMaxNum(self):
        pass

    
    def GetCanBuyAmount(self):
        iPrice = self.m_BuyList[self.m_SelectBox].GetPrice()
        return max(self.m_iCurGuessPoint / iPrice, 1)

    
    def SetCanBuyAmount(self, amount, price):
        iMaxAmount = self.GetCanBuyAmount()
        if amount > iMaxAmount:
            self.m_BuyAmountEdit.SetText('%d' % iMaxAmount)
        

    
    def GetTotalPriceInfo(self, amount, price):
        iTotalPrice = amount * price
        color = None if iTotalPrice > self.m_iCurGuessPoint else interface.COLOR_5
        return (iTotalPrice, color)



class CSnowmanTableTradeDlg(CGroceryTradeDlg):
    
    def ShowTips(self, bShow):
        '''
\t\t\xacO\xa7_\xc5\xe3\xa5\xdc\xb4\xa3\xa5\xdc
\t\t'''
        sTips = '\xaaA\xb0\xc8\xbe\xb9\xc2I\xa5d\xbb\xf9\xae\xe6\xb8\xfb\xa7C\xae\xc9\xa1A\xb3\xb7\xa4H\xb0\xf2\xaey\xb1N\xa8\xc9\xa6\xb3\xa4@\xa9w\xa7\xe9\xa6\xa9'
        self.m_oTips = interface.CTextObject(self.GetObject('box_amount'), sTips, interface.FontLT14_3, interface.COLOR_9)
        interface.CenterLeft(self.m_oTips)
        self.m_oTips.SetShow(bShow)



class C2018WorldCupShop(CTradeBase):
    BUYLIST = [
        (70662, 30, 12),
        (25707, 30, 100),
        (25732, 30, 200),
        (72224, 1, 1250)]
    HUFU_POS = 12
    
    def __init__(self, ticketid, itype = 0, responseID = 0, iHufuAmount = 1):
        CTradeBase.__init__(self, ticketid, itype, responseID)
        self.SetBuyList(self.BUYLIST)
        self.m_CurPoint = ticketid
        self.m_HufuAmount = iHufuAmount
        self.SetHufuInfo(iHufuAmount)
        self.SetHufuEnable(iHufuAmount > 0)
        self.SetTradeTips()

    
    def SetEditMaxNum(self):
        pass

    
    def SetTradeTips(self):
        (x, y) = self.GetObject('total_price').GetPos()
        self.m_TradeTipsObj = interface.CTextObject(self, '\xb6\xc8\xa5i\xa8\xcf\xa5\xce\xc3\xe0\xc1\xf9\xa7U\xab\xc2\xbfn\xa4\xc0\xc1\xca\xb6R\xaa\xab\xab~', interface.FontLT14_3, interface.COLOR_81)
        self.m_TradeTipsObj.SetPos(x + 105, y)

    
    def SetHufuInfo(self, iHufuAmount):
        import ui
        oHufuBox = self.m_BuyList[self.HUFU_POS]
        path = 'combdialog3\\\xd4\xd3\xcd\xbc\\\xcf\xde\xb9\xba\xcd\xbc\xb1\xea\\\xcf\xde\xb9\xba.png'
        oHufuBox.m_oImage = ui.CImage(oHufuBox, path, interface.UIPath)
        z = oHufuBox.m_Icon.GetZ()
        oHufuBox.m_oImage.SetZ(z + 1)
        oHufuBox.m_LimitNumTxt = interface.CTextObject(oHufuBox, str(iHufuAmount), interface.FontLT14E_1, 16777215)
        (w, h) = oHufuBox.m_LimitNumTxt.GetSize()
        oHufuBox.m_LimitNumTxt.SetPos(45 - w, 35)
        oHufuBox.m_LimitNumTxt.SetZ(z + 1)

    
    def SetHufuEnable(self, bAble):
        oHufuBox = self.m_BuyList[self.HUFU_POS]
        if not bAble:
            oHufuBox.m_Icon.SetGrey()
            oHufuBox.m_oImage.SetGrey()
            oHufuBox.Enable(False)
        

    
    def GetGoodInfo(self, shape, num, price):
        name = GetNameWithPeiFang(shape)
        desc = name
        desc += '#r\xbb\xf9\xae\xe6: %s' % price
        return (shape, num, price, desc)

    
    def GetCanBuyAmount(self):
        iPrice = self.m_BuyList[self.m_SelectBox].GetPrice()
        iShape = self.m_BuyList[self.m_SelectBox].GetShape()
        if iShape == 72224:
            return self.m_HufuAmount
        else:
            return max(self.m_CurPoint / iPrice, 1)

    
    def SetCanBuyAmount(self, amount, price):
        iMaxAmount = self.GetCanBuyAmount()
        if amount > iMaxAmount:
            self.m_BuyAmountEdit.SetText('%d' % iMaxAmount)
        

    
    def CreateCashTxt(self, iPoint):
        font = interface.FontLT16_9
        color = interface.COLOR_10
        if interface.IsStyle4():
            self.GetObject('cashtxt').SetText('\xa7U\xab\xc2\xbfn\xa4\xc0')
        else:
            self.m_CashNote = combmacro.CTEXT(interface.CTextObject, 'cashtxt', self, '\xa7U\xab\xc2\xbfn\xa4\xc0', font, color)
        self.m_CurCash = combmacro.CTEXT(interface.CTextObject, 'curr_cash', self, str(iPoint), font, color)

    
    def GetTotalPriceInfo(self, amount, price):
        iTotalPrice = amount * price
        color = None if iTotalPrice > self.m_CurCash else interface.COLOR_5
        return (iTotalPrice, color)

    
    def DoBuy(self, sel, amount):
        
        try:
            box = self.m_BuyList[sel]
        except IndexError:
            return None

        if not box.HasData():
            return None
        
        for idx, tInfo in enumerate(self.BUYLIST):
            (iShape, _, _) = tInfo
            if iShape == box.GetShape():
                break
                continue
        else:
            return None
        import networldcup
        networldcup.C2SBuyItem(idx + 1, amount)


g_Mode2Class = {
    0: CGroceryTradeDlg,
    1: CPSTradeDlg,
    2: CPointTradeDlg,
    3: CPointTradeDlg,
    6: CPracticeDlg,
    7: CFoodTradeDlg,
    9: CHerbsTradeDlg,
    12: CZPUseCashDlg,
    13: CZPUseFightCashDlg,
    19: CShiTuPointTradeDlg,
    22: CGroceryDlg,
    41: CGoldTradeDlg,
    101: CReputeTradeDlg,
    106: CGuessTradeDlg,
    107: CSnowmanTableTradeDlg }

def Show(buylist, ticketid, mode, itype = 0, responseID = 0, sKey = '', iChoiceShape = 0, iDetailID = 0):
    global g_TradeDialog
    import permission
    import newtradeinterface
    import mdnewtrade
    import dlggroup
    if permission.IsOpenNewTrade():
        if iChoiceShape:
            SetDefaultChoiceShape(iChoiceShape)
        
        dNewBuyList = []
        iSelectIdx = -1
        for iIdx, tValue in enumerate(buylist):
            dInfo = {
                'iShape': tValue[0],
                'iNum': tValue[1],
                'iPrice': tValue[2],
                'bSelect': tValue[0],
                'iItemIndex': iIdx }
            if g_iDefaultChoiceShape and tValue[0] == g_iDefaultChoiceShape:
                iSelectIdx = iIdx
            
            dNewBuyList.append(dInfo)
        
        SetDefaultChoiceShape(0)
        newtradeinterface.ShowNewTrade(mode, sKey)
        mdnewtrade.GetModel().SetTradeInfo(responseID, itype, mode, ticketid, iSelectIdx, sKey)
        mdnewtrade.GetModel().SetAllGoodsInfo(dNewBuyList, iSelectIdx, iDetailID = iDetailID)
        return None
    
    if g_TradeDialog:
        (selbox, page, cnt) = g_TradeDialog.GetSelInfo()
        if isinstance(g_TradeDialog, CPracticeDlg):
            dlgtattoo.CTattooDialog.SetTattooShopOpen(False)
        
    else:
        selbox = -1
        cnt = 0
        page = GetPageWithTaskNeed(buylist)
    cls = g_Mode2Class.get(mode, CTradeDlg)
    g_TradeDialog = cls(ticketid, itype, responseID, iDetailID)
    g_TradeDialog.SetBuyList(buylist)
    dlggroup.CloseGroupBuyDlg()
    SetTips(sKey)
    maxPage = (len(buylist) - 1) / 24
    if page > maxPage:
        page = maxPage
    
    if selbox >= 0:
        g_TradeDialog.SetSelInfo(selbox, page, cnt)
    else:
        g_TradeDialog.ShowPage(page)
        dlggroup.CloseGroupBuyDlg()
    if iChoiceShape:
        g_TradeDialog.SelectDefault(iChoiceShape)
    
    if g_iDefaultChoiceShape:
        g_TradeDialog.SelectDefault(g_iDefaultChoiceShape)
        SetDefaultChoiceShape(None)
    
    return g_TradeDialog


def SetDefaultChoiceShape(iShape):
    global g_iDefaultChoiceShape
    g_iDefaultChoiceShape = iShape


def SetTips(sKey):
    if sKey in ('GoodHeart', 'FXPoint2'):
        g_TradeDialog.ShowTips(sKey)
    


def GetPageWithTaskNeed(buyList):
    import task
    import item
    itemDct = task.GetAllItems()
    page = 0
    for idx, data in enumerate(buyList):
        shape = data[0]
        if shape in itemDct and not item.HasTaskItem(shape):
            page = idx / 24
            break
            continue
    
    return page


def RefreshTicket(info):
    if not isinstance(g_TradeDialog, CTradeBase):
        return None
    
    import re
    patt = re.compile('\xad\xb1\xad\xc8[ ]*[0-9]+')
    mo = patt.search(info)
    if mo is not None:
        
        try:
            ticket_price = int(info[mo.start() + 4:mo.end()].strip())
        except ValueError:
            return None

        g_TradeDialog.SetTicketPrice(ticket_price)
    


def CloseDlg(flag = None):
    global g_TradeDialog, g_BoughtTaskItem
    if isinstance(g_TradeDialog, CPracticeDlg):
        dlgtattoo.CTattooDialog.SetTattooShopOpen(False)
    
    g_TradeDialog = None
    g_BoughtTaskItem = []


def ShowJingJiTradeDlg(buylst, point, mode, responseID = 0):
    global g_TradeDialog
    cls = g_Mode2Class.get(mode, CPointTradeDlg)
    g_TradeDialog = cls(point, 0, responseID)
    g_TradeDialog.GetObject('noname0').ChgCaptionTxt('\xa7I\xb4\xab\xbc\xfa\xc0y')
    g_TradeDialog.SetBuyList(buylst)


def StartPSTimer(iTime):
    if g_TradeDialog and isinstance(g_TradeDialog, CPSTradeDlg):
        g_TradeDialog.StartPSTimer(iTime)
    


def ShowChushen(dBuy, ticketid, mode, itype = 0, responseID = 0, iDetailID = 0):
    global g_TradeDialog
    g_TradeDialog = CChushenDlg(ticketid, itype, responseID, iDetailID = iDetailID)
    g_TradeDialog.SetBuyList(dBuy)
    return g_TradeDialog


def ShowWorldCupShop(iPoint, iHufuAmount):
    global g_TradeDialog
    g_TradeDialog = C2018WorldCupShop(iPoint, iHufuAmount = iHufuAmount)
    LOG_DEBUG('\xa5\xb4\xb6}\xa5@\xac\xc9\xac\xd7\xbfn\xa4\xc0\xa7I\xb4\xab\xac\xc9\xad\xb1', iPoint, iHufuAmount)
    return g_TradeDialog


def ShowCarnivalShop(iPoint, iType, iResponseID, lstBuy):
    global g_TradeDialog
    g_TradeDialog = CCarnivalTradeDlg(iPoint, iType, iResponseID)
    g_TradeDialog.SetBuyList(lstBuy)
    return g_TradeDialog


def GetNameWithPeiFang(shape):
    import hero
    import itemdata
    materialLs = []
    for _, _, info in hero.g_Designs.values():
        for id, _ in info:
            materialLs.append(id)
        
    
    name = itemdata.GetData(shape)[0]
    if shape in materialLs:
        name = name + '(\xb0t\xa4\xe8)'
    
    return name
