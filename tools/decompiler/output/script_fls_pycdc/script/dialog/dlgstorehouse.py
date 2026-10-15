# pycdc 交叉复核产物 · script.fls entry 4362
# co_filename(原始)='script/dialog/dlgstorehouse.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4362.pyc (Python 2.5)

import combdialog
import gamemoduledefines
import interface
import item
import stopgamemoduleinterface
import style
import ui
import wrapinterface
g_StoreHouse = None
g_SHHandle = None
g_LastTime = 0
g_Data = []
g_ShowOnceFlag = True
g_PrevShape = None
g_PrevIdx = 0
STORE_START = 300
STORE_SCOPE = 380

def ModuleReset():
    global g_StoreHouse, g_SHHandle, g_LastTime, g_Data, g_ShowOnceFlag, g_PrevShape, g_PrevIdx
    g_StoreHouse = None
    g_SHHandle = None
    g_LastTime = 0
    g_Data = []
    g_ShowOnceFlag = True
    g_PrevShape = None
    g_PrevIdx = 0
    CNameMgr.SetDefaultName()
    CStoreHouseDialog.ResetClear()


def ShowOnceTips():
    global g_ShowOnceFlag
    import usermacro
    if g_ShowOnceFlag:
        usermacro.PROMPT_MSG('\xab\xf6Shift+\xa5k\xc1\xe4\xa5i\xaa\xbd\xb1\xb5\xa6s\xa9\xf1\xa1A\xb5L\xbb\xdd\xbdT\xbb{')
        g_ShowOnceFlag = False
    


def ShowRentDlg(mode, isbig, price, cash = 0, fight_cash = 0):
    global g_StoreHouse
    if mode not in (0, 1):
        return None
    
    if g_StoreHouse and hasattr(g_StoreHouse, 'RemoveCallBacks'):
        g_StoreHouse.RemoveCallBacks()
    
    g_StoreHouse = CRentSHDialog(mode, isbig, price, cash, fight_cash)


def ShowEnterSH():
    global g_StoreHouse
    if g_StoreHouse and hasattr(g_StoreHouse, 'RemoveCallBacks'):
        g_StoreHouse.RemoveCallBacks()
    
    g_StoreHouse = CEnterSH()


def ShowSetPwd():
    global g_SHHandle
    g_SHHandle = CSHSetPwd()


def ShowPay(mode, price, cash, fight_cash, limittime):
    global g_SHHandle
    g_SHHandle = CSHPay(mode, price, cash, fight_cash, limittime)


def ShowRenameDlg():
    if g_StoreHouse:
        g_StoreHouse.ShowRenameDlg()
    


def Show(mode, isbig, time, price, cash, fight_cash, data = None, name = None, isfasten = 0):
    global g_Data, g_StoreHouse
    if data is None:
        data = []
    
    g_Data = []
    for pos, shape, amount, key, iLevel, sExtName in data:
        itObj = SHItem((pos - 1) + STORE_START, shape, amount, key, iLevel)
        itObj.SetExtName(sExtName)
        g_Data.append(itObj)
    
    if g_StoreHouse and hasattr(g_StoreHouse, 'RemoveCallBacks'):
        g_StoreHouse.RemoveCallBacks()
    
    g_StoreHouse = CStoreHouseDialog(mode, isbig, price, cash, fight_cash, time, name, isfasten)
    CNameMgr.SetOpenStoreName(name)
    import warui
    warui.ShowMagicShortKey()


def IsStoreHouseShow():
    if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
        return g_StoreHouse.GetShow()
    
    return False

Item_Weapon = [
    50130,
    50140,
    50150,
    51130,
    51140,
    51150,
    52130,
    52140,
    52150,
    53130,
    53140,
    53150,
    54130,
    54140,
    54150,
    61080,
    60080,
    62080,
    63080,
    64080,
    65080,
    66080,
    67080]

def OpenUnlockSH():
    global g_SHHandle
    g_SHHandle = CUnlockSH()


def CloseWindow():
    global g_SHHandle, g_StoreHouse
    g_SHHandle = None
    if hasattr(g_StoreHouse, 'ClearAllItemExt'):
        g_StoreHouse.ClearAllItemExt()
    
    g_StoreHouse = None
    import dlgmap
    import warui
    dlgmap.DisableMinimap(False)
    warui.ShowMagicShortKey()


def ShowPetEggName(iPos):
    if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
        g_StoreHouse.ShowItemExtName(iPos)
    


def _InItemBox(pos):
    if pos <= pos:
        pass
    elif not pos < item.ITEM_FIGHT_START:
        if pos <= pos:
            pass
        elif pos < item.ITEM_FIGHT_SCOPE:
            return True
        
    return False


def _InSHBox(pos):
    if pos <= pos:
        pass
    elif pos < STORE_SCOPE:
        return True
    
    return False


def InEquipBox(pos):
    if pos <= pos:
        pass
    elif pos <= item.MAX_EQUIP_POS:
        return True
    
    return False


class SHItem(object):
    
    def __init__(self, pos, shape, quantity, key = 0, iLevel = 0, sExt = None):
        self.m_ID = pos
        self.m_Pos = pos
        self.m_Shape = shape
        self.m_Quantity = quantity
        self.m_Key = key
        self.m_Level = iLevel
        self.m_Type = item.ITEM_STOREHOUSE
        self.m_InfoExt = sExt
        self.m_sExtName = None

    
    def SetExtName(self, sExtName):
        self.m_sExtName = sExtName

    
    def GetExtName(self):
        return self.m_sExtName

    
    def GetShape(self):
        return self.m_Shape

    
    def GetKey(self):
        return self.m_Key

    
    def IsMarkSoulBind(self):
        '''\xacO\xa7_\xacO\xb1M\xa6\xb3\xaa\xba'''
        return self.m_Key & item.MARK_SOUL_BINDED



class CInterfaceItem(item.CInterfaceItem):
    
    def ShowItemInfo(self, it, flag = 0, isEquipComp = False):
        import dlggetinfo
        id = it.m_ID
        shape = it.m_Shape
        ext = dlggetinfo.GetItemExt(it, flag)
        if shape in dlggetinfo.SPECIAL_SHAPE:
            iif = dlggetinfo.ShowRealShapeItemInfo(shape, id, it.m_Key, ext)
        else:
            iif = dlggetinfo.NewItemInfo(id, shape, ext, None, it.m_Key, isEquipComp, sName = it.GetExtName())
        dlggetinfo.g_ItemInfoTips[0][0] = interface.CShadowObject(iif)
        return iif

    
    def IsEquipItem(self):
        import itemdata
        if self.m_Item and getattr(self.m_Item, 'm_Shape', None) and itemdata.IsType(self.m_Item.m_Shape, 'equip'):
            return True
        
        return False



class StoreIIF(CInterfaceItem):
    
    def Take(self):
        if self.m_ItemImg is None or not self.m_ItemImg.GetShow():
            return None
        
        self.SetItemShow(False)
        import handobj
        if _InItemBox(self.m_Pos):
            handobj.HandItem(self.m_Item.m_ID, self.m_InterfaceItems, self.AcceptPut, self.Put)
        else:
            handobj.HandSHItem(self.m_Item.m_ID, self.m_Item.m_Shape, self.m_InterfaceItems, self.AcceptPut, self.Put)

    
    def Put(self):
        self.SetItemShow(True)

    
    def AcceptPut(self):
        
        def _DelayShow(obj):
            self.SetItemShow(True)

        self.CreatePyCommand(30, _DelayShow)

    
    def OnHand(self, hand):
        import handobj
        if hand.m_Type == handobj.TYPE_ITEM or hand.m_Type == handobj.TYPE_SH:
            if self.m_Item and hand.m_ID == self.m_Item.m_ID:
                handobj.Clear()
                return None
            
            if hand.m_Type == handobj.TYPE_ITEM:
                it = item.GetItem(hand.m_ID)
            else:
                it = GetSHItem(hand.m_ID)
                if it is None:
                    return None
                
            if _InItemBox(it.m_Pos) and _InItemBox(self.m_Pos):
                item.CInterfaceItem.OnHand(self, hand)
                return None
            elif _InItemBox(it.m_Pos) and _InSHBox(self.m_Pos):
                self.StoreConsumableItems(it.m_Pos, self.m_Pos)
            elif _InSHBox(it.m_Pos) and _InItemBox(self.m_Pos):
                import netstorehouse
                netstorehouse.C2SPopSH((it.m_Pos - STORE_START) + 1, 0, self.m_Pos)
            elif _InSHBox(it.m_Pos) and _InSHBox(self.m_Pos):
                import netstorehouse
                netstorehouse.C2SSHMove((it.m_Pos - STORE_START) + 1, (self.m_Pos - STORE_START) + 1, False)
            elif InEquipBox(it.m_Pos) and _InSHBox(self.m_Pos):
                import usermacro
                usermacro.PROMPT_MSG('\xa8\xd8\xc0\xb9\xa4\xa4\xaa\xba\xb8\xcb\xb3\xc6\xb5L\xaak\xaa\xbd\xb1\xb5\xa6s\xa4J\xad\xdc\xaew')
                handobj.Clear()
                return None
            
            
            def _DelayShow(obj, pos):
                if obj.IsEnter():
                    obj.Enter()
                

            self.CreatePyCommand(5, _DelayShow, it.m_Pos)
            handobj.Accept()
        

    
    def StoreConsumableItems(self, fromPos, destPos):
        par = self.GetParent()
        if par:
            par.StoreConsumableItems(fromPos, (destPos - STORE_START) + 1)
        

    
    def SetItemByPos(self, pos):
        if _InItemBox(pos):
            item.CInterfaceItem.SetItemByPos(self, pos)
            return None
        elif _InSHBox(pos):
            for it in g_Data:
                if pos == it.m_Pos:
                    self.SetSHItem(it)
                    break
                    continue
            
        

    
    def SetItemShow(self, flag):
        if self.m_ItemImg:
            self.m_ItemImg.SetShow(flag)
        
        if hasattr(self, 'm_FlashObj') and self.m_FlashObj:
            self.m_FlashObj.SetShow(flag)
        

    
    def SetSHItem(self, it = None):
        import task
        import itemdata
        self.m_Item = it
        if it is None:
            self.m_ItemImg = None
            self.m_QuantityText = None
        else:
            self.m_ItemImg = item.CreateItem44Image(self, it.m_Shape)
            self.SetQuantity()
            shape = getattr(self.m_Item, 'm_Shape', None)
            if shape and itemdata.IsType(self.m_Item.m_Shape, 'gem'):
                self.ShowGemLevelTxt()
            elif shape == 72307 and self.m_Item and self.m_Item.m_InfoExt:
                lst = self.m_Item.m_InfoExt.split('\xa1G')
                self.ShowItemExtName(lst[0])
            
            self.ShowSHEquipTypeTxt()
        self.SetFlash(False)
        if it is None:
            return None
        
        dTaskItems = task.GetAllItems(True)
        iShape = it.GetShape()
        if iShape:
            iRealShape = task.NormalShape2Special(iShape)
            if iRealShape in dTaskItems and not it.IsMarkSoulBind():
                self.SetFlash(True)
            
        

    
    def ShowSHEquipTypeTxt(self):
        if self.m_Item and self.m_Item.GetKey() & item.MARK_MODUL != 0:
            self.m_EquipTypeTxt = interface.CTextObject(self.m_ItemImg, '\xbc\xd2\xa8\xe3', interface.FontST12E, [
                3357517,
                16777215], 0)
            (iTxtW, iTxtH) = self.m_EquipTypeTxt.GetSize()
            tSpace = (2, 2)
            self.m_EquipTypeTxt.SetPos(44 - iTxtW - tSpace[0], tSpace[1])
        else:
            self.m_EquipTypeTxt = None

    
    def RefreshSHItem(self, pos):
        if self.m_InterfaceItems is not None:
            self.m_InterfaceItems[pos] = self
        
        self.m_Pos = pos
        self.SetItemByPos(pos)

    
    def SetFlash(self, bFlash):
        if bFlash:
            (w, h) = self.GetSize()
            z = self.m_ItemImg.GetZ()
            flashObj = interface.CSpriteObject(self, 'item44/select.spr', 'item')
            flashObj.SetPos(w / 2, h / 2)
            flashObj.SetZ(z + 1)
            flashObj.CreateCommand(1, 'animation')
        else:
            flashObj = None
        self.m_FlashObj = flashObj



class _CEditWithEnable(interface.CEdit):
    
    def Enable(self, flag):
        interface.CEdit.Enable(self, flag)
        (w, h) = self.GetSize()
        self.m_EnableBox = interface.CBoxObject(self, w + 2, h + 2, 5263440, 256)
        self.m_EnableBox.SetPos(-1, -1)
        if flag:
            self.m_EnableBox.SetShow(False)
        else:
            self.m_EnableBox.SetShow(True)



class CRentSHDialog(combdialog.CCombDialog):
    
    def __init__(self, itype, isbig, price, cash, fight_cash):
        import combmacro
        if itype == 0:
            if isbig == 2:
                combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/sh_rent_normal_big.dlg')
            else:
                combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/sh_rent_normal.dlg')
        elif isbig == 2:
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/sh_rent_special_big.dlg')
        else:
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/sh_rent_special.dlg')
        if isbig == 11:
            self.GetObject('noname0').ChgCaptionTxt('\xa4\xc9\xaf\xc5\xa6\xa8\xa4j\xad\xdc\xaew')
            self.GetObject('noname3').SetShow(False)
            self.GetObject('noname5').SetShow(False)
            tip_str = '\xa4\xc9\xaf\xc5\xab\xe1\xad\xdc\xaew\xaa\xba\xae\xe6\xa4l\xbc\xc6\xb1N\xa5\xd140\xad\xd3\xc5\xdc\xa6\xa880\xad\xd3\xa1C#r\xaa`\xb7N\xa1G\xa4\xc9\xaf\xc5\xab\xe1\xaa\xba\xad\xdc\xaew\xa6\xb3\xae\xc4\xb4\xc1\xbbP\xad\xec\xad\xdc\xaew\xa6\xb3\xae\xc4\xb4\xc1\xa4@\xadP\xa1C'
            self.m_TipsTxt = interface.CRichTextObject(self, 310, interface.FontLT14_3, tip_str, interface.COLOR_4)
            self.m_TipsTxt.SetPos(35, 50)
        
        self.m_Mode = itype
        self.m_IsBig = isbig
        self.SetPos(170, 90)
        color = interface.COLOR_56
        self.m_PriceTxt1 = combmacro.CTEXT(interface.CTextObject, 'price1', self, '%d\xa5@\xac\xc9\xb0^\xc4m\xab\xd7' % price, interface.FontLT14_3, color)
        self.m_PriceTxt2 = combmacro.CTEXT(interface.CTextObject, 'price2', self, '%d\xb2{\xaa\xf7+%d\xa9\xe8\xa5\xce\xaa\xf7' % (cash, fight_cash), interface.FontLT14_3, color)
        self.m_SHNameEdit = combmacro.CEDIT(CEnterEdit, 'SHNameEdit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_SHNameEdit.m_IsGB2312 = True
        self.m_SHNameEdit.SetLimit(20)
        self.m_SHNameEdit.Active(True)
        self.m_SHPwdEdit = combmacro.CEDIT(interface.CEdit, 'SHPwdEdit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_SHPwdEdit.m_IsPassword = True
        self.m_SHPwdEdit2 = combmacro.CEDIT(interface.CEdit, 'SHPwdEdit2', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_SHPwdEdit2.m_IsPassword = True
        if isbig == 11:
            self.m_SHNameEdit.Enable(False)
            self.m_SHPwdEdit.Enable(False)
            self.m_SHPwdEdit2.Enable(False)
            color = interface.COLOR_263
            self.m_InvalidTxt1 = combmacro.CRICHTEXT(interface.CRichTextObject, 'SHNameEdit', self, '\xa4\xa3\xa5\xce\xbf\xe9\xa4J', interface.FontLT14_3, color)
            self.m_InvalidTxt2 = combmacro.CRICHTEXT(interface.CRichTextObject, 'SHPwdEdit', self, '\xa4\xa3\xa5\xce\xbf\xe9\xa4J', interface.FontLT14_3, color)
            self.m_InvalidTxt3 = combmacro.CRICHTEXT(interface.CRichTextObject, 'SHPwdEdit2', self, '\xa4\xa3\xa5\xce\xbf\xe9\xa4J', interface.FontLT14_3, color)
        
        self.m_SHNameEdit.SetNextEdit(self.m_SHPwdEdit)
        self.m_SHPwdEdit.SetNextEdit(self.m_SHPwdEdit2)
        self.m_SHPwdEdit2.SetNextEdit(self.m_SHNameEdit)
        import dlgmap
        dlgmap.DisableMinimap()

    
    def ConfirmUse(self):
        import banword
        import usermacro
        name = self.m_SHNameEdit.GetText()
        pwd = self.m_SHPwdEdit.GetText()
        pwd2 = self.m_SHPwdEdit2.GetText()
        if len(name) < 1 and self.m_IsBig != 11:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xad\xdc\xaew\xa6W')
            return None
        
        if not banword.IsValidOnIntrodruce(name):
            usermacro.PROMPT_MSG('\xa4\xba\xaee\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1A\xbd\xd0\xc0\xcb\xacd\xad\xd7\xa7\xef')
            return None
        
        if pwd != pwd2:
            usermacro.PROMPT_MSG('\xa8\xe2\xa6\xb8\xb1K\xbdX\xbf\xe9\xa4J\xa4\xa3\xa4@\xadP\xa1A\xbd\xd0\xbdT\xbb{\xab\xe1\xad\xab\xb7s\xb6\xf1\xbcg\xa1C')
            self.m_SHPwdEdit.SetSelect(0, len(pwd))
            self.m_SHPwdEdit.Active(True)
            self.m_SHPwdEdit2.SetText('')
            return None
        
        import netstorehouse
        pay_mode = 1
        if not self.GetObject('chk_sg').IsSelected() and not self.GetObject('chk_cash').IsSelected():
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xa5I\xb6O\xa4\xe8\xa6\xa1')
            return None
        
        if self.GetObject('chk_cash').IsSelected():
            pay_mode = 2
        
        netstorehouse.C2SRentSH(self.m_Mode, self.m_IsBig, pay_mode, name, pwd)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            CloseWindow()
        elif msgid == 5:
            self.ConfirmUse()
        



class CEditTextObject(interface.CEditTextObject):
    
    def __init__(self, parent, char, font, color):
        interface.CEditTextObject.__init__(self, parent, char, font, color)
        if char.isdigit():
            self.m_Sub = interface.CRichTextObject(self, interface.g_FontSize[font], font, '#u%s#n' % char, color)
        



class CEnterEdit(interface.CEdit):
    
    def __init__(self, parent, color, font, x, y, w, h, linecolor = 0, overstriking = False):
        interface.CEdit.__init__(self, parent, color, font, x, y, w, h, linecolor, overstriking)
        self.m_TextClass = CEditTextObject
        self.m_IsGB2312 = False

    
    def AddChar(self, s):
        import misc
        import pubmisc
        if getattr(self, 'm_IsGB2312'):
            if misc.IsTWServer():
                if misc.IsBIG5(s, 1) or s.isdigit():
                    interface.CEdit.AddChar(self, s)
                else:
                    import usermacro
                    usermacro.PROMPT_MSG('\xad\xdc\xaew\xa6W\xba\xd9\xa5u\xa4\xb9\xb3\\\xbf\xe9\xa4J\xbc\xc6\xa6r\xa1B\xa6r\xa5\xc0\xa9M\xba~\xa6r')
            elif pubmisc.IsGB2312(s, 1) or s.isdigit():
                interface.CEdit.AddChar(self, s)
            else:
                import usermacro
                usermacro.PROMPT_MSG('\xad\xdc\xaew\xa6W\xba\xd9\xa5u\xa4\xb9\xb3\\\xbf\xe9\xa4J\xbc\xc6\xa6r\xa1B\xa6r\xa5\xc0\xa9M\xba~\xa6r')
        else:
            interface.CEdit.AddChar(self, s)

    
    def MsgEnter(self):
        par = self.GetParent()
        if hasattr(par, 'MsgEnter'):
            par.MsgEnter()
        



class CEnterSH(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/sh_enter.dlg')
        import ratio
        if ratio.Is800x600():
            self.SetPos(190, 120)
        else:
            interface.Center(self)
        self.CreateNameEdit()
        self.CreateLinks()

    
    def CreateNameEdit(self):
        import combmacro
        self.m_SHNameEdit = combmacro.CEDIT(CEnterEdit, 'SHNameEdit', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_SHNameEdit.SetLimit(20)
        self.m_SHNameEdit.Active(True)

    
    def CreateLinks(self):
        if interface.IsNewStyle():
            color = '#c0A83F5'
        else:
            color = '#G'
        linkInfo = [
            (2, 'txt_fasten', '#u%s\xb9\xef\xad\xdc\xaew\xb6i\xa6\xe6\xa9T\xa9w#n' % color),
            (3, 'txt_Link', '#u%s\xa7\xd1\xb0O\xad\xdc\xaew\xa6W#n' % color)]
        self.m_LinkTexts = []
        for msgID, ctrlname, linkTxt in linkInfo:
            (x, y, w, h) = self.GetLocData(ctrlname)
            txtobj = interface.CClickRichText(self, x, y, w, linkTxt, 65280, 65280, interface.FontLT14_3, msgid = msgID)
            self.m_LinkTexts.append(txtobj)
        

    
    def ShowLinkDlg(self, msgid):
        import dlgnpc
        txtInfo = {
            2: '1.\xa7A\xa5i\xa5H\xa6b\xad\xdc\xaew\xac\xc9\xad\xb1\xa1A\xa5k\xc1\xe4\xc2I\xc0\xbb\xad\xdc\xaew\xbc\xd0\xc5\xd2\xad\xb6\xa1A\xb9\xef\xad\xdc\xaew\xb6i\xa6\xe6\xa9T\xa9w/\xb8\xd1\xb0\xa3\xa9T\xa9w\xbe\xde\xa7@\xa1C#r' + '2.\xa9T\xa9w\xab\xe1\xaa\xba\xad\xdc\xaew\xa1A\xa5i\xa5H\xa6b\xad\xab\xb5n\xab\xe1\xabO\xab\xf9\xa5\xb4\xb6}\xaa\xba\xaa\xac\xbaA\xa1A\xa4]\xa4\xa3\xb7|\xb3Q\xb7s\xa5\xb4\xb6}\xaa\xba\xad\xdc\xaew\xb3\xbb\xb4\xc0\xb1\xbc\xa1C#r' + '3.\xa4@\xa6\xfd\xb6i\xa4J\xb2\xa7\xb1`\xb5n\xbf\xfd\xc5\xe7\xb5\xfd\xaa\xac\xbaA\xa1A\xb1N\xa6\xdb\xb0\xca\xa8\xfa\xae\xf8\xa9T\xa9w\xa1C',
            3: '\xc7\xe9\xa6p\xaaG\xa7\xd1\xb0O\xa4F\xad\xdc\xaew\xa6W\xa6r\xa1A\xa5i\xa5H\xbf\xef\xbe\xdc\xa1i\xacd\xb8\xdf\xa7\xda\xaa\xba\xa9\xd2\xa6\xb3\xad\xdc\xaew\xa1j#r' + '\xc7\xea\xacd\xb8\xdf\xad\xdc\xaew\xbb\xdd\xadn\xb5\xa5\xab\xdd3\xa4\xd1\xae\xc9\xb6\xa1\xa4~\xaf\xe0\xa6\xac\xa8\xec\xb5\xb2\xaaG',
            4: '\xc7\xe9\xa6p\xaaG\xa7\xd1\xb0O\xa4F\xad\xdc\xaew\xa6W\xa6r\xa1A\xa5i\xa5H\xbf\xef\xbe\xdc#s(111,\xacd\xb8\xdf\xa7\xda\xaa\xba\xa9\xd2\xa6\xb3\xad\xdc\xaew)#r' + '\xc7\xea\xacd\xb8\xdf\xad\xdc\xaew\xbb\xdd\xadn\xb5\xa5\xab\xdd3\xa4\xd1\xae\xc9\xb6\xa1\xa4~\xaf\xe0\xa6\xac\xa8\xec\xb5\xb2\xaaG' }
        dlgnpc.ShowClientDlg(txtInfo.get(msgid, ''), '', None)

    
    def MsgEnter(self):
        self.OnMessage(5)

    
    def OnMessage(self, msgid):
        import netstorehouse
        if msgid == 1:
            CloseWindow()
        elif msgid in (2, 3):
            if msgid == 3:
                netstorehouse.C2SSHForgetName()
                return None
            
            self.ShowLinkDlg(msgid)
        elif msgid == 5:
            name = self.m_SHNameEdit.GetText()
            if len(name) < 1:
                import usermacro
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xad\xdc\xaew\xa6W')
                return None
            
            netstorehouse.C2SEnterSH(name)
        



class CUnlockSH(combdialog.CCombDialog):
    LINKID = 50
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/sh_unlock.dlg')
        self.SetPos(190, 120)
        self.Capture(1, 0)
        import combmacro
        self.m_PwdEdit = combmacro.CEDIT(CEnterEdit, 'pwd', self, interface.COLOR_1, interface.FontLT14_3)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit.SetLimit(20)
        self.m_PwdEdit.Active(True)
        color = None if interface.IsNewStyle() else '#G'
        linkText = '#c(%d)#u%s%s#n#c()' % (CUnlockSH.LINKID, color, '\xa7\xd1\xb0O\xb1K\xbdX')
        self.m_LinkText = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_Link', self, linkText, interface.FontLT14_3)

    
    def ShowLinkDlg(self):
        import dlgnpc
        txt = '\xc7\xe9\xa6p\xaaG\xa7\xd1\xb0O\xad\xdc\xaew\xb1K\xbdX\xa1A\xa5i\xa5H\xc2I\xc0\xbb\xa5\xaa\xa4U\xa8\xa4\xaa\xba\xa1i\xb3]\xb8m\xb1K\xbdX\xa1j\xa1A\xbf\xef\xbe\xdc\xa1i\xb1j\xa6\xe6\xb2M\xaa\xc5\xb1K\xbdX\xa1j\xa7Y\xa5i#r' + '\xc7\xea\xb1j\xa8\xee\xb2M\xaa\xc5\xb1K\xbdX\xbb\xdd\xadn\xa4\xe4\xa5I50\xb8U\xa8\xe2\xb2{\xaa\xf7\xa8\xc3\xb5\xa5\xab\xdd5\xa4\xd1\xa1A5\xa4\xd1\xab\xe1\xb2M\xaa\xc5\xb1K\xbdX\xa8\xc3\xaa\xf0\xc1\xd950\xb8U\xa9\xe8\xa5\xce\xaa\xf7'
        dlgnpc.ShowClientDlg(txt, '', None)

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        import cursor
        (cx, cy) = cursor.GetPos()
        if hasattr(self, 'm_LinkText') and self.m_LinkText:
            (x, y) = self.m_LinkText.GetScreenPos()
            id = self.m_LinkText.ClickID(cx - x, cy - y)
            if id == CUnlockSH.LINKID:
                self.ShowLinkDlg()
            
        

    
    def MsgEnter(self):
        self.OnMessage(5)

    
    def CloseWindow(self):
        global g_SHHandle
        g_SHHandle = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 5:
            pwd = self.m_PwdEdit.GetText()
            if len(pwd) < 1:
                import usermacro
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xad\xdc\xaew\xb1K\xbdX')
                return None
            
            import netstorehouse
            netstorehouse.C2SUnlock(pwd)
            self.CloseWindow()
        



class CSHSetPwd(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/sh_setpwd.dlg')
        self.SetPos(250, 100)
        self.Capture(1, 0)
        import combmacro
        self.m_OldPwd = combmacro.CEDIT(interface.CEdit, 'oldpwd', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_OldPwd.m_IsPassword = True
        self.m_OldPwd.Active(True)
        self.m_Pwd1 = combmacro.CEDIT(interface.CEdit, 'pwd1', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_Pwd1.m_IsPassword = True
        self.m_Pwd2 = combmacro.CEDIT(interface.CEdit, 'pwd2', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_Pwd2.m_IsPassword = True
        self.m_OldPwd.SetNextEdit(self.m_Pwd1)
        self.m_Pwd1.SetNextEdit(self.m_Pwd2)
        self.m_Pwd2.SetNextEdit(self.m_OldPwd)
        import dlgmap
        dlgmap.DisableMinimap()

    
    def _Close(self):
        global g_SHHandle
        import dlgmap
        dlgmap.DisableMinimap(False)
        g_SHHandle = None

    
    def OnMessage(self, msgid):
        if msgid in (1, 11):
            self._Close()
        elif msgid == 5:
            oldpwd = self.m_OldPwd.GetText()
            pwd1 = self.m_Pwd1.GetText()
            pwd2 = self.m_Pwd2.GetText()
            if pwd1 != pwd2:
                self.m_Pwd2.Active(True)
                import usermacro
                usermacro.PROMPT_MSG('\xb1K\xbdX\xa4\xa3\xa4@\xadP\xa1I')
                return None
            
            if oldpwd == pwd1:
                self.m_OldPwd.Active(True)
                import usermacro
                usermacro.PROMPT_MSG('\xb7s\xc2\xc2\xb1K\xbdX\xa6n\xb9\xb3\xa7\xb9\xa5\xfe\xa4@\xbc\xcb\xb0\xda...')
                return None
            
            import netstorehouse
            netstorehouse.C2SSHSetPwd(oldpwd, pwd1)
            self._Close()
        elif msgid == 6:
            import commondialog
            
            def _ok(dlg):
                import netstorehouse
                netstorehouse.C2SSHClearPwd()

            txt = interface.Replace('\xb1j\xa8\xee\xb2M\xaa\xc5\xad\xdc\xaew\xb1K\xbdX\xbb\xdd\xadn\xa4\xe4\xa5I50\xb8U\xa8\xe2\xb2{\xaa\xf7\xa8\xc3\xb5\xa5\xab\xdd5\xa4\xd1\xa1A5\xa4\xd1\xab\xe1\xb2M\xaa\xc5\xb1K\xbdX\xa8\xc3\xaa\xf0\xc1\xd950\xb8U\xa9\xe8\xa5\xce\xaa\xf7\xa1C\xbdT\xbb{\xadn\xb2M\xaa\xc5\xb1K\xbdX\xb6\xdc?#B(\xadY\xaa\xbe\xb9D\xc2\xc2\xb1K\xbdX\xa1A\xa5i\xaa\xbd\xb1\xb5\xb3]\xb8m\xad\xdc\xaew\xb1K\xbdX\xac\xb0\xaa\xc5\xa7Y\xa5i\xb2M\xaa\xc5)#n')
            dlg = commondialog.ShowMessageBox(txt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (_ok, None))
        



class CSHPay(combdialog.CCombDialog):
    
    def __init__(self, mode, price, cash, fight_cash, limittime):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/sh_pay.dlg')
        import combmacro
        self.SetPos(170, 100)
        self.Capture(1, 0)
        self.CreateTimeText()
        self.m_Mode = mode
        self.GetObject('price').SetShow(False)
        color = interface.COLOR_56
        self.m_PriceTxt1 = combmacro.CTEXT(interface.CTextObject, 'cash', self, '%d\xa5@\xac\xc9\xb0^\xc4m\xab\xd7' % price, interface.FontLT14_3, color)
        self.m_PriceTxt2 = combmacro.CTEXT(interface.CTextObject, 'fight_cash', self, '%d\xb2{\xaa\xf7+%d\xa9\xe8\xa5\xce\xaa\xf7' % (cash, fight_cash), interface.FontLT14_3, color)

    
    def CreateTimeText(self):
        import misc
        import time
        import combmacro
        limitTime = misc.GetServerCurrentTime() + 7776000
        timeTxt = '%d-%.2d-%.2d' % time.localtime(limitTime)[:3]
        color = interface.COLOR_229
        self.m_FeeTime = combmacro.CTEXT(interface.CTextObject, 'time', self, timeTxt, interface.FontLT14_3, color)

    
    def OnMessage(self, msgid):
        global g_SHHandle, g_SHHandle
        if msgid in (1, 4):
            g_SHHandle = None
        elif msgid == 3:
            import netstorehouse
            pay_mode = 1
            if not self.GetObject('chk_sg').IsSelected() and not self.GetObject('chk_cash').IsSelected():
                import usermacro
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xa5I\xb6O\xa4\xe8\xa6\xa1')
                return None
            
            if self.GetObject('chk_cash').IsSelected():
                pay_mode = 2
            
            netstorehouse.C2SSHPay(pay_mode)
            g_SHHandle = None
        



class CSHReName(combdialog.CCombDialog):
    
    def __init__(self, parent, name):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/sh_rename.dlg')
        self.SetPos(100, 100)
        self.Capture(1, 0)
        self.m_name = name
        import combmacro
        if name:
            color = interface.COLOR_56
            self.m_oldname = combmacro.CTEXT(interface.CTextObject, 'oldname', self, name, interface.FontLT14_3, color)
        
        self.m_Name1 = combmacro.CEDIT(CEnterEdit, 'name1', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_Name1.m_IsGB2312 = True
        self.m_Name2 = combmacro.CEDIT(CEnterEdit, 'name2', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_Name2.m_IsGB2312 = True
        self.m_Name1.Active(True)
        self.m_Name1.SetNextEdit(self.m_Name2)
        self.m_Name2.SetNextEdit(self.m_Name1)
        self.m_Name1.SetLimit(20)
        self.m_Name2.SetLimit(20)
        import dlgmap
        dlgmap.DisableMinimap()

    
    def MsgEnter(self):
        pass

    
    def OnMessage(self, msgid):
        if msgid in (1, 11):
            self.SetShow(False)
        elif msgid == 5:
            import usermacro
            name1 = self.m_Name1.GetText()
            name2 = self.m_Name2.GetText()
            if name1.strip() == '':
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xb7s\xaa\xba\xad\xdc\xaew\xa6W\xba\xd9')
                return None
            
            if name1 != name2:
                usermacro.PROMPT_MSG('\xa8\xe2\xa6\xb8\xbf\xe9\xa4J\xaa\xba\xb7s\xaa\xba\xa6W\xba\xd9\xa4\xa3\xa6P')
                return None
            
            import netstorehouse
            netstorehouse.C2SReNameSH(name1)
            self.SetShow(False)
        



class CListBox(interface.CListBox):
    
    def OnSelect(self, sel):
        if sel < 0 or sel > len(self.m_TextList):
            return None
        
        txt = self.m_TextList[sel - 1]
        self.m_List = None
        if txt == self.GetText():
            return None
        
        
        def _Refresh():
            store_name = self.GetParent().m_Name
            if store_name in ('1', '2'):
                netstorehouse.C2SOpenStoreHouse(int(store_name))
            else:
                netstorehouse.C2SEnterSH(store_name)

        import netstorehouse
        if txt == '\xb4\xb6\xb3q':
            netstorehouse.C2SInsureToNormal()
        elif txt == '\xabO\xc0I':
            
            def _OK(a):
                netstorehouse.C2SNormalToInsure()
                _Refresh()

            import commondialog
            commondialog.ShowMessageBox('\xc2\xe0\xb4\xab\xac\xb0\xabO\xc0I\xbc\xd2\xa6\xa1\xab\xe1\xa1A\xa6p\xaaG\xa5X\xb2{\xb2\xa7\xb1`\xb5n\xbf\xfd\xa5B\xa4f\xa5O\xc5\xe7\xb5\xfd\xa5\xa2\xb1\xd1\xa1A\xabh72\xa4p\xae\xc9\xa4\xba\xb1N\xb5L\xaak\xb6i\xa6\xe6\xa6s\xa4J\xa9M\xa8\xfa\xa5X\xbe\xde\xa7@(\xb8\xd1\xb0\xa3\xb2\xa7\xb1`\xb5n\xbf\xfd\xaa\xac\xbaA\xab\xe1\xa5i\xa5H\xb8\xd1\xb0\xa3\xb8\xd3\xaa\xac\xbaA)', ('\xbdT\xa9w', '\xa9\xf1\xb1\xf3'), (_OK, None))
            return None
        
        _Refresh()



class CHPageButton(combdialog.CHPageButton):
    
    def LeftUp(self):
        combdialog.CHPageButton.LeftUp(self)
        import netstorehouse
        if self.m_Name in ('1', '2'):
            netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
        elif self.m_Name == '3':
            netstorehouse.C2SEnterSH(self.m_TipName)
        else:
            netstorehouse.C2SEnterSH(self.m_Name)

    
    def RightUp(self):
        (x, y) = self.GetPos()
        if self.m_Name not in ('1,', '2', '3'):
            import popmenu
            self.m_PopMenu = popmenu.PopSetFastenStoreMenu(self.GetParent(), x, y + 20, (self.m_Name, (1, 0)[self.m_IsFasten]))
        

    
    def Enter(self):
        combdialog.CHPageButton.Enter(self)
        if self.m_Name in ('1,', '2'):
            return None
        
        if self.m_IsFasten:
            txt = None if len(self.m_Name) > 6 else '\xa5k\xc1\xe4\xa5i\xb8\xd1\xb0\xa3\xa9T\xa9w'
        elif len(self.m_Name) > 6:
            pass
        
        txt = '\xa5k\xc1\xe4\xa5i\xa9T\xa9w\xad\xdc\xaew'
        if self.m_Name == '3':
            txt = ''
        
        if not txt:
            return None
        
        import wrapinterface
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT12_1, direct = 1)
        self.m_Tips.SetOwner(self)

    
    def Leave(self):
        combdialog.CHPageButton.Leave(self)
        self.m_Tips = None

    
    def OnHand(self, hand):
        import handobj
        import netstorehouse
        par = self.GetParent()
        if hand.m_Type == handobj.TYPE_ITEM:
            import item
            page = par.m_Page
            if self.m_Name in ('1', '2'):
                netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
            elif self.m_Name == '3':
                netstorehouse.C2SEnterSH(self.m_TipName)
            else:
                netstorehouse.C2SEnterSH(self.m_Name)
            it = item.GetItem(hand.m_ID)
            if it:
                par.StoreConsumableItems(it.m_Pos)
            
        elif hand.m_Type == handobj.TYPE_SH:
            page = par.m_Page - 1
            name = None if self.m_Name != '3' else self.m_TipName
            it = GetSHItem(hand.m_ID)
            if it and name != par.m_Name:
                netstorehouse.C2SSHToSH(name, (it.m_Pos - STORE_START) + 1, it.m_Quantity, page)
            
        
        handobj.Clear()
        handobj.Accept()



class CHPagePngButton(combdialog.CHPagePngButton):
    
    def LeftUp(self):
        combdialog.CHPagePngButton.LeftUp(self)
        import netstorehouse
        if self.m_Name in ('1', '2'):
            netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
        elif self.m_Name == '3':
            netstorehouse.C2SEnterSH(self.m_TipName)
        else:
            netstorehouse.C2SEnterSH(self.m_Name)

    
    def RightUp(self):
        (x, y) = self.GetPos()
        if self.m_Name not in ('1,', '2', '3'):
            import popmenu
            self.m_PopMenu = popmenu.PopSetFastenStoreMenu(self.GetParent(), x, y + 5, (self.m_Name, (1, 0)[self.m_IsFasten]))
        

    
    def Enter(self):
        combdialog.CHPagePngButton.Enter(self)
        if self.m_Name in ('1,', '2'):
            return None
        
        if self.m_IsFasten:
            txt = None if len(self.m_Name) > 6 else '\xa5k\xc1\xe4\xa5i\xb8\xd1\xb0\xa3\xa9T\xa9w'
        elif len(self.m_Name) > 6:
            pass
        
        txt = '\xa5k\xc1\xe4\xa5i\xa9T\xa9w\xad\xdc\xaew'
        if self.m_Name == '3':
            txt = ''
        
        if not txt:
            return None
        
        import wrapinterface
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT12_1, direct = 1)
        self.m_Tips.SetOwner(self)

    
    def Leave(self):
        combdialog.CHPagePngButton.Leave(self)
        self.m_Tips = None

    
    def OnHand(self, hand):
        import handobj
        import netstorehouse
        par = self.GetParent()
        if hand.m_Type == handobj.TYPE_ITEM:
            import item
            page = par.m_Page
            if self.m_Name in ('1', '2'):
                netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
            elif self.m_Name == '3':
                netstorehouse.C2SEnterSH(self.m_TipName)
            else:
                netstorehouse.C2SEnterSH(self.m_Name)
            it = item.GetItem(hand.m_ID)
            if it:
                par.StoreConsumableItems(it.m_Pos)
            
        elif hand.m_Type == handobj.TYPE_SH:
            page = par.m_Page - 1
            name = None if self.m_Name != '3' else self.m_TipName
            it = GetSHItem(hand.m_ID)
            if it and name != par.m_Name:
                netstorehouse.C2SSHToSH(name, (it.m_Pos - STORE_START) + 1, it.m_Quantity, page)
            
        
        handobj.Clear()
        handobj.Accept()



class CNameMgr:
    s_ShowName = {
        '1': 0,
        '2': 0 }
    s_NameSort = [
        '1',
        '2']
    s_OpenStoreName = None
    
    def AddStoreName(cls, name, isfasten, needRefresh = True):
        cls.s_ShowName[name] = isfasten
        if name not in cls.s_NameSort:
            cls.s_NameSort.append(name)
        
        if needRefresh and cls.s_OpenStoreName:
            if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
                g_StoreHouse.CreatePageButton(cls.s_OpenStoreName, cls.s_ShowName.get(cls.s_OpenStoreName, 0))
            
        

    AddStoreName = classmethod(AddStoreName)
    
    def RandomDelStoreName(cls, retainName = None):
        for name in cls.s_NameSort:
            if name not in ('1', '2', retainName) and not cls.s_ShowName.get(name):
                break
                continue
        else:
            return None
        cls.s_NameSort.remove(name)
        del cls.s_ShowName[name]

    RandomDelStoreName = classmethod(RandomDelStoreName)
    
    def DelStoreName(cls, name, isfasten, needRefresh = True):
        if name in cls.s_ShowName:
            del cls.s_ShowName[name]
        
        if name in cls.s_NameSort:
            cls.s_NameSort.remove(name)
        
        if needRefresh and cls.s_OpenStoreName:
            if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
                cls.CleanStoreFasten()
                lst = cls.GetSortShowLstKey()
                for sortkey in lst:
                    if cls.s_ShowName.get(sortkey, None) is not None:
                        cls.AddStoreName(sortkey, cls.s_ShowName[sortkey])
                        continue
                
            
        

    DelStoreName = classmethod(DelStoreName)
    
    def SetDefaultName(cls):
        cls.s_ShowName = {
            '1': 0,
            '2': 0 }
        cls.s_NameSort = [
            '1',
            '2']
        if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
            g_StoreHouse.CleanStoreNameFasten()
        

    SetDefaultName = classmethod(SetDefaultName)
    
    def CleanStoreFasten(cls):
        for name in cls.s_ShowName.keys():
            cls.s_ShowName[name] = 0
        
        if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
            g_StoreHouse.CleanStoreNameFasten()
        

    CleanStoreFasten = classmethod(CleanStoreFasten)
    
    def SetOpenStoreName(cls, name):
        cls.s_OpenStoreName = name

    SetOpenStoreName = classmethod(SetOpenStoreName)
    
    def GetSortShowLstKey(cls):
        keyLst = cls.s_ShowName.keys()
        
        def cmpFunc(x, y):
            if '1' in (x, y):
                return None if x == '1' else -1
            
            if '2' in (x, y):
                return None if x == '2' else -1
            
            if cls.s_ShowName.get(x) != cls.s_ShowName.get(y):
                return None if cls.s_ShowName.get(x) == 1 else -1
            
            if x in cls.s_NameSort and y in cls.s_NameSort:
                return cls.s_NameSort.index(y) - cls.s_NameSort.index(x)
            
            return x < y

        keyLst.sort(cmp = cmpFunc, reverse = True)
        return keyLst

    GetSortShowLstKey = classmethod(GetSortShowLstKey)
    
    def GetSortShowLstKey2(cls):
        keyLst = [
            '3']
        for name, isFasten in cls.s_ShowName.iteritems():
            if not isFasten:
                keyLst.append(name)
                continue
        
        
        def cmpFunc(x, y):
            if '1' in (x, y):
                return None if x == '1' else -1
            
            if '2' in (x, y):
                return None if x == '2' else -1
            
            if '3' in (x, y):
                return None if x == '3' else -1
            
            if cls.s_ShowName.get(x) != cls.s_ShowName.get(y):
                return None if cls.s_ShowName.get(x) == 1 else -1
            
            if x in cls.s_NameSort and y in cls.s_NameSort:
                return cls.s_NameSort.index(y) - cls.s_NameSort.index(x)
            
            return x < y

        keyLst.sort(cmp = cmpFunc, reverse = True)
        return keyLst

    GetSortShowLstKey2 = classmethod(GetSortShowLstKey2)
    
    def GetFastenNameLst(cls):
        lst = []
        for name, isFasten in cls.s_ShowName.iteritems():
            if isFasten:
                lst.append(name)
                continue
        
        return lst

    GetFastenNameLst = classmethod(GetFastenNameLst)
    
    def GetFastenLen(cls):
        return len(cls.GetFastenNameLst())

    GetFastenLen = classmethod(GetFastenLen)
    
    def GetShowLen(cls):
        return len(cls.s_ShowName)

    GetShowLen = classmethod(GetShowLen)
    
    def GetNotfastenNum(cls):
        return cls.GetShowLen() - cls.GetFastenLen()

    GetNotfastenNum = classmethod(GetNotfastenNum)


class CStoreHouseDialog(combdialog.CCombDialog):
    s_MyBagPage = 0
    s_LastAdjustTime = { }
    s_LastPasten = None
    s_STORE_SHOW_MAX = 7
    s_STORE_SHOW_MIN = 4
    s_STORE_NAME_MAX = 15
    s_ShapeDct = {
        'equip': (50010, 67090),
        'antique': (21501, 21515),
        'drug': (21100, 21118) }
    
    def ResetClear(cls):
        cls.s_MyBagPage = 0
        cls.s_LastAdjustTime = { }
        cls.s_LastPasten = None

    ResetClear = classmethod(ResetClear)
    
    def __init__(self, mode, isbig, price, cash, fight_cash, limittime, name, isfasten):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/storehouse.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_DlgHelpID = 5090
        self.m_IsBig = isbig
        self.m_Page = 1
        self.m_SHMode = mode
        self.m_FeePrice = price
        self.m_FeeCash = cash
        self.m_FeeFightCash = fight_cash
        self.m_Name = name
        self.InitCB()
        self.SetCurTime()
        self.CreatePageButton(name, isfasten)
        self.SetMode()
        self.CreateInterfaceItems()
        self.CheckStoreType(limittime)
        self.EnableRenewBtn()
        self.SetSafeType()
        self.CreateCashText()
        self.UpdateBag()
        self.InitBtns()

    
    def InitCB(self):
        import commoncb
        commoncb.RegistCB(commoncb.TASK_SATISFY, self, 'RefreshItemsFlash')

    
    def InitBtns(self):
        self.GetObject('btn_adjust').m_ParentNotify = True
        self.GetObject('btn_expend').m_ParentNotify = True
        self.GetObject('btn_Bag%d' % self.s_MyBagPage).LeftUp()
        self.GetObject('btn_Bag%d' % self.s_MyBagPage).Leave()

    
    def OnCaptureCover(self, oItem = None):
        self.DoTopmost()

    
    def CreatePageButton(self, name, isfasten):
        CNameMgr.AddStoreName(name, isfasten, False)
        self.m_FastenBtn = None
        self.m_FastenBox = None
        if CNameMgr.GetFastenLen() >= self.s_STORE_SHOW_MIN:
            self.ShowFastenBox(name)
        else:
            self.ShowFastenNornaml(name)
            CStoreHouseDialog.s_LastPasten = None

    
    def ShowFastenBox(self, name):
        while CNameMgr.GetNotfastenNum() > self.s_STORE_SHOW_MAX - 2:
            CNameMgr.RandomDelStoreName(name)
        keyLst = CNameMgr.GetSortShowLstKey2()
        if name not in keyLst:
            self.ShowPageBtns(keyLst, '3', name)
            CStoreHouseDialog.s_LastPasten = name
        elif getattr(CStoreHouseDialog, 's_LastPasten', None) and CNameMgr.s_ShowName.get(CStoreHouseDialog.s_LastPasten):
            self.ShowPageBtns(keyLst, name, CStoreHouseDialog.s_LastPasten)
        else:
            keyLst.remove('3')
            CStoreHouseDialog.s_LastPasten = None
            self.ShowPageBtns(keyLst, name)
        self.CreateFastenBtn()

    
    def ShowItemExtName(self, iPos):
        oItem = self.m_InterfaceItems[1][iPos]
        if oItem:
            if oItem.m_Item.m_Shape == 72307:
                sExt = oItem.m_Item.m_InfoExt
                sInfoList = sExt.split('\xa1G')
                oItem.ShowItemExtName(sInfoList[0])
            
        

    
    def ShowFastenNornaml(self, name):
        while CNameMgr.GetShowLen() > self.s_STORE_SHOW_MAX:
            CNameMgr.RandomDelStoreName(name)
        keyLst = CNameMgr.GetSortShowLstKey()
        self.ShowPageBtns(keyLst, name)

    
    def ShowPageBtns(self, nameLst, name, tipName = None):
        self.m_StoreName = []
        btnPath = style.GetStr(self.GetDlgPath(), 'data_pagebtn_path')
        (iOffsetX, iOffsetY) = style.GetIntTuple(self.GetDlgPath(), 'data_pagebtn_offset')
        (ix, iy) = style.GetIntTuple(self.GetDlgPath(), 'data_pagebtn_pos')
        btn_width = style.GetInt(self.GetDlgPath(), 'data_pagebtn_width')
        iFontStyle = style.GetInt(self.GetDlgPath(), 'data_pagebtn_fontidx')
        for i, sName in enumerate(nameLst):
            trueName = sName
            if sName in ('1', '2', '3'):
                trueName = [
                    '\xb4\xb6\xb3q',
                    '\xb4\xb6\xb3q',
                    '\xabO\xc0I',
                    tipName][int(sName)]
            
            if interface.IsNewStyle():
                if len(trueName) > 5:
                    trueName = trueName[:4] + '..'
                
                data = [
                    iFontStyle,
                    btnPath,
                    trueName,
                    50,
                    0,
                    2,
                    0,
                    0]
                classType = CHPagePngButton
            elif len(trueName) > 6:
                trueName = trueName[:4] + '..'
            
            data = [
                iFontStyle,
                btnPath,
                trueName,
                0,
                2,
                0,
                0]
            classType = CHPageButton
            data.reverse()
            it = classType(self, data)
            it.m_Name = sName
            it.m_IsFasten = CNameMgr.s_ShowName.get(sName, 0)
            x = iOffsetX + btn_width * i
            y = iOffsetY
            it.SetPos(x + ix, y + iy)
            self.m_StoreName.append(it)
            if name == sName:
                it.SetSelect(True)
            
            if sName == '3':
                it.m_TipName = tipName
                continue
        

    
    class CMyButton(interface.CButton):
        
        def Enter(self):
            interface.CButton.Enter(self)
            par = self.GetParent()
            par.CreateFastenBox()


    
    def CreateFastenBtn(self):
        import style
        path = style.GetPath('combdialog/\xd4\xd3\xcd\xbc/down.igs')
        num = 0
        iOffX = style.GetInt(self.GetDlgPath(), 'data_storebtn')
        for idx, storeBtn in enumerate(self.m_StoreName):
            if storeBtn.m_Name in ('1', '2', '3'):
                num += 1
                continue
            
            if idx >= num:
                (x, y) = storeBtn.GetPos()
                storeBtn.SetPos(x + iOffX, y)
                continue
        
        (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_storebtn')
        x += (80 - iOffX) * num
        self.m_FastenBtn = self.CMyButton(self, path, x, y)

    
    class CMyBox(interface.CClickBox):
        
        def RightUp(self):
            par = self.GetParent()
            par.m_FastenBox = None

        
        def Leave(self):
            import cursor
            import C_sys
            (x, y) = cursor.GetPos()
            objects = C_sys.GetObjects(x, y)
            for obj in objects:
                if isinstance(obj, (CStoreHouseDialog.CMyNameButton, CStoreHouseDialog.CMyNamePngButton)):
                    return None
                    continue
            
            par = self.GetParent()
            if par:
                par.m_FastenBox = None
            


    
    class CMyNameButton(interface.CTextButton):
        
        def Enter(self):
            interface.CTextButton.Enter(self)
            import wrapinterface
            self.m_OwnTips = wrapinterface.CTextTips(None, -1, '\xa5k\xc1\xe4\xa5i\xb8\xd1\xb0\xa3\xa9T\xa9w', interface.FontLT14_3, direct = 1)

        
        def Leave(self):
            interface.CTextButton.Leave(self)
            self.m_OwnTips = None

        
        def LeftUp(self):
            interface.CTextButton.LeftUp(self)
            import netstorehouse
            netstorehouse.C2SEnterSH(self.m_Name)

        
        def RightUp(self):
            (x, y) = self.GetPos()
            import popmenu
            self.m_PopMenu = popmenu.PopSetFastenStoreMenu(self.GetParent(), x, y + 15, (self.m_Name, 0))

        
        def OnHand(self, hand):
            import handobj
            import netstorehouse
            par = self.GetParent().GetParent()
            if hand.m_Type == handobj.TYPE_ITEM:
                import item
                page = par.m_Page
                if self.m_Name in ('1', '2'):
                    netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
                else:
                    netstorehouse.C2SEnterSH(self.m_Name)
                it = item.GetItem(hand.m_ID)
                if it:
                    par.StoreConsumableItems(it.m_Pos)
                
            elif hand.m_Type == handobj.TYPE_SH:
                page = par.m_Page - 1
                name = self.m_Name
                it = GetSHItem(hand.m_ID)
                if it and name != par.m_Name:
                    netstorehouse.C2SSHToSH(name, (it.m_Pos - STORE_START) + 1, it.m_Quantity, page)
                
            
            handobj.Clear()
            handobj.Accept()


    
    class CMyNamePngButton(interface.CTextButton):
        
        def Enter(self):
            interface.CTextButton.Enter(self)
            import wrapinterface
            self.m_OwnTips = wrapinterface.CTextTips(None, -1, '\xa5k\xc1\xe4\xa5i\xb8\xd1\xb0\xa3\xa9T\xa9w', interface.FontLT14_3, direct = 1)

        
        def Leave(self):
            interface.CTextButton.Leave(self)
            self.m_OwnTips = None

        
        def LeftUp(self):
            interface.CTextButton.LeftUp(self)
            import netstorehouse
            netstorehouse.C2SEnterSH(self.m_Name)

        
        def RightUp(self):
            (x, y) = self.GetPos()
            import popmenu
            self.m_PopMenu = popmenu.PopSetFastenStoreMenu(self.GetParent(), x, y + 5, (self.m_Name, 0))

        
        def OnHand(self, hand):
            import handobj
            import netstorehouse
            par = self.GetParent().GetParent()
            if hand.m_Type == handobj.TYPE_ITEM:
                import item
                page = par.m_Page
                if self.m_Name in ('1', '2'):
                    netstorehouse.C2SOpenStoreHouse(int(self.m_Name))
                else:
                    netstorehouse.C2SEnterSH(self.m_Name)
                it = item.GetItem(hand.m_ID)
                if it:
                    par.StoreConsumableItems(it.m_Pos)
                
            elif hand.m_Type == handobj.TYPE_SH:
                page = par.m_Page - 1
                name = self.m_Name
                it = GetSHItem(hand.m_ID)
                if it and name != par.m_Name:
                    netstorehouse.C2SSHToSH(name, (it.m_Pos - STORE_START) + 1, it.m_Quantity, page)
                
            
            handobj.Clear()
            handobj.Accept()


    
    def CreateFastenBox(self):
        bgPath = style.GetStr(self.GetDlgPath(), 'data_bg')
        btnPath = style.GetStr(self.GetDlgPath(), 'data_btn')
        num = CNameMgr.GetFastenLen()
        if interface.IsNewStyle():
            (w1, h1) = (50, 25)
        else:
            obj = ui.CImage(self, btnPath, interface.UIPath)
            (w1, h1) = obj.GetSize()
        import math
        w = 3 * w1 + 50
        h = int((math.ceil(num / 3) * 1.5 + 0.5) * h1)
        (x, y) = self.m_FastenBtn.GetPos()
        self.m_FastenBox = self.CMyBox(self, w, h, alpha = 0)
        self.m_FastenBox.SetPos(x, y + 20)
        self.m_FastenBox.SetZ(200)
        self.m_FastenBox.m_BGLst = ui.CFrame(self.m_FastenBox, w, h, bgPath)
        lst = CNameMgr.GetFastenNameLst()
        btnLst = []
        for idx, name in enumerate(lst):
            x = int((idx % 3) * (w1 + 10) + 15)
            y = int((0.5 + (idx / 3) * 1.5) * h1)
            if interface.IsNewStyle():
                if len(name) > 5:
                    tname = name[:4] + '..'
                else:
                    tname = name
                it = self.CMyNamePngButton(self.m_FastenBox, btnPath, x, y, tname, interface.COLOR_1, interface.FontLT14_3, 0, 50)
                (iOffsetX, iOffsetY) = style.GetIntTuple(self.GetDlgPath(), 'CMyNamePngButton_offset')
                it.SetOffset(iOffsetX, iOffsetY)
                it.SetTextPos(0, 1)
            else:
                it = self.CMyNameButton(self.m_FastenBox, btnPath, x, y, name, 16777141, interface.FontLT14_3)
            it.m_Name = name
            it.SetZ(100)
            btnLst.append(it)
        
        self.m_FastenBox.m_BtnLst = btnLst

    
    def SetMode(self):
        key2name = {
            0: '\xb4\xb6\xb3q\xad\xdc\xaew',
            1: '\xaf\xd3\xa7\xf7\xad\xdc\xaew' }
        mode = self.m_SHMode & 1
        if mode in key2name:
            titleObj = self.GetObject('noname0')
            titleObj.ChgCaptionTxt(key2name[mode])
        
        if mode == 1:
            self.GetObject('txt_Tips').SetShow(False)
        
        self.GetObject('btn_adjust').SetShow(mode == 1)
        self.GetObject('btn_adjust1').SetShow(mode != 1)
        self.GetObject('noname6').SetShow(False)
        self.GetObject('btn_storemgr').SetShow(self.m_SHMode & 2)

    
    def CreateInterfaceItems(self):
        import combmacro
        import itemdata
        import task
        self.m_InterfaceItems = [
            { },
            { }]
        combmacro.CITEMAREA(StoreIIF, 'self_item_box', self, item.ITEM_START, self.m_InterfaceItems[0], 100)
        combmacro.CITEMAREA(StoreIIF, 'self_fight_item_box', self, item.ITEM_FIGHT_START, self.m_InterfaceItems[0], 100)
        combmacro.CITEMAREA(StoreIIF, 'self_item_box2', self, item.ITEM_SCOPE, self.m_InterfaceItems[0], 100)
        ipagesize = 40
        itembox = self.GetObject('sh_item_box')
        (x, y) = itembox.GetPos()
        (w, h) = itembox.GetSize()
        for i in xrange(ipagesize):
            pos = i + STORE_START
            (ix, iy) = itembox.GetImage(i / 5, i % 5).GetPos()
            iit = StoreIIF(self, x + ix, y + iy, pos, self.m_InterfaceItems[1])
            iit.RefreshSHItem(pos)
            iit.SetItemByPos(pos)
            oItem = iit.GetItem()
            if not oItem:
                continue
            
            iShape = oItem.GetShape()
            dTaskItems = task.GetAllItems(True)
            if iShape:
                if itemdata.IsType(iit.m_Item.m_Shape, 'gem'):
                    iit.ShowGemLevelTxt()
                
                iRealShape = task.NormalShape2Special(iShape)
                if iRealShape in dTaskItems and not oItem.IsMarkSoulBind():
                    iit.SetFlash(True)
                
            not oItem.IsMarkSoulBind()
        
        item.AddInterfaceCallback(self.m_InterfaceItems[0], 0, oRefObj = self)
        import BlankFrame
        BlankFrame.CreateBlank(self, x, y, w, h, -1, BlankFrame.BLANK_RIGHT)
        if self.m_IsBig == 2:
            for i in xrange(ipagesize):
                pos = i + STORE_START + ipagesize
                (ix, iy) = itembox.GetImage(i / 5, i % 5).GetPos()
                iit = StoreIIF(self, x + ix, y + iy, pos, self.m_InterfaceItems[1])
                iit.RefreshSHItem(pos)
            
            item.AddInterfaceCallback(self.m_InterfaceItems[1], 0, oRefObj = self)
        else:
            self.GetObject('btn_Page1').SetShow(False)
            self.GetObject('btn_Page2').SetShow(False)

    
    def RefreshItemsFlash(self, iTaskList = None):
        import task
        dTaskItems = task.GetAllItems(True)
        for oIt in self.m_InterfaceItems[1].itervalues():
            oItem = oIt.GetItem()
            if not oItem:
                oIt.SetFlash(False)
                continue
            
            iShape = task.NormalShape2Special(oItem.GetShape())
            iRealShape = task.NormalShape2Special(iShape)
            if iRealShape in dTaskItems and not oItem.IsMarkSoulBind():
                oIt.SetFlash(True)
                continue
            oIt.SetFlash(False)
        

    
    def ClearAllItemExt(self):
        for dInterfaceItem in self.m_InterfaceItems:
            for interfaceitemObj in dInterfaceItem.values():
                if interfaceitemObj and interfaceitemObj.GetItem() and hasattr(interfaceitemObj.GetItem(), 'm_InfoExt'):
                    del interfaceitemObj.GetItem().m_InfoExt
                    continue
            
        

    
    def EnableRenewBtn(self):
        if self.m_SHMode & 4 != 0:
            self.GetObject('btn_add').SetShow(True)
            self.GetObject('btn_adjust').Enable(False)
        else:
            self.GetObject('btn_add').SetShow(False)
            self.GetObject('btn_adjust').Enable(True)

    
    def CheckStoreType(self, limittime):
        if self.m_SHMode & 2 == 0:
            self.GetObject('btn_add').SetShow(False)
            self.GetObject('btn_up').SetShow(False)
        else:
            self.GetObject('SetPwdBtn').SetShow(True)
            self.GetObject('btn_add').SetShow(True)
            import time
            import combmacro
            self.m_LimitTime = limittime
            tm = time.time()
            if limittime - tm <= 259200:
                color = interface.COLOR_30
            else:
                color = interface.COLOR_4
            timetxt = '%d-%.2d-%.2d' % time.localtime(limittime)[:3]
            if interface.IsNewStyle():
                txt = '\xa8\xec\xb4\xc1\xae\xc9\xb6\xa1\xa1G#r%s' % timetxt
            else:
                txt = '\xa8\xec\xb4\xc1\xae\xc9\xb6\xa1\xa1G%s' % timetxt
            self.m_LimitTimeTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'time', self, txt, interface.FontLT12_1, color)
            if self.m_IsBig == 2:
                self.GetObject('btn_up').SetShow(False)
            

    
    def AskDeleteStore(self):
        import netstorehouse
        netstorehouse.C2SAskDelStore()

    
    def SetSafeType(self):
        import combmacro
        color = interface.COLOR_5
        if self.m_Name == '2':
            color = interface.COLOR_37
            self.UpdateStore(40)
        
        listToSelect = [
            '\xb4\xb6\xb3q',
            '\xabO\xc0I']
        self.m_SafeType = combmacro.CLISTBOX(CListBox, 'draw_down', self, color, interface.FontLT14_3)
        for v in listToSelect:
            self.m_SafeType.AddTextItem(v)
        
        if self.m_SHMode & 8 == 0:
            txt = listToSelect[0]
        else:
            txt = listToSelect[1]
        self.m_SafeType.SetText(txt)
        self.m_SafeType.SetItemProp(2, 16, len(self.m_SafeType.m_TextList) * 18)
        self.m_SafeType.SetReadOnly(True)
        if color == interface.COLOR_37:
            obj = self.m_SafeType.m_DownButton
            obj.Enable(False)
            if hasattr(obj, 'm_NotifyBox'):
                obj.m_NotifyBox.Enable(False)
            
        

    
    def CreateCashText(self):
        import hero
        hero.CreateCombDlgCash('cash', 'dlgstorehouse', (('m_Cash', 0, 0),), self)

    
    def CleanStoreNameFasten(self):
        for ctrl in self.m_StoreName:
            ctrl.m_IsFasten = 0
        

    
    def SetCurTime(self):
        import misc
        self.m_CurTime = misc.GetServerCurrentTime()

    
    def CheckIdle(self):
        import misc
        tempTime = misc.GetServerCurrentTime()
        if tempTime - self.m_CurTime >= 300:
            return True
        
        return False

    
    def CloseWindowByIdle(self):
        if self.CheckIdle():
            import usermacro
            usermacro.PROMPT_MSG('\xa5\xd1\xa9\xf35\xa4\xc0\xc4\xc1\xa4\xba\xa8S\xa6\xb3\xbe\xde\xa7@\xad\xdc\xaew\xa1A\xbb\xdd\xadn\xad\xab\xb7s\xa5\xb4\xb6}\xa4~\xaf\xe0\xa8\xcf\xa5\xce')
            self.CloseWindow()
            return True
        
        self.SetCurTime()
        return False

    
    def OnButtonEnter(self, btn):
        if btn == self.GetObject('btn_adjust'):
            txt = '\xa6\xdb\xb0\xca\xbe\xe3\xb2z\xad\xdc\xaew\xa4\xa4\xaa\xba\xaa\xab\xab~'
        elif btn.m_MsgID == 14:
            txt = '\xaf\xb2\xa5\xce\xb7s\xb1K\xbdX\xad\xdc\xaew'
        
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT12_1, direct = 1)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def CheckLimit(self, shape):
        for k in self.s_ShapeDct:
            if shape <= shape:
                pass
            elif shape <= self.s_ShapeDct[k][1]:
                return True
                continue
        
        return False

    
    def SetShadow(self, flag):
        for pos in self.m_InterfaceItems[0]:
            iit = self.m_InterfaceItems[0][pos]
            it = iit.GetItem()
            if it:
                if not self.CheckLimit(it.m_Shape):
                    iit.Enable(not flag)
                    iit.ShowShadow(flag)
                
            self.CheckLimit(it.m_Shape)
        

    
    def UpdateBag(self, num = None):
        import hero
        if num is None:
            num = hero.g_Prop.m_BagMax
        
        for i in xrange(num):
            pos = i + item.ITEM_SCOPE
            iit = self.m_InterfaceItems[0].get(pos)
            if iit:
                iit.Enable(True)
                continue
        
        for i in xrange(num, 40):
            pos = i + item.ITEM_SCOPE
            iit = self.m_InterfaceItems[0].get(pos)
            if iit:
                iit.Enable(False)
                continue
        
        if self.m_SHMode in (3, 11):
            self.SetShadow(True)
        else:
            self.SetShadow(False)

    
    def UpdateStore(self, num = 0):
        for i in xrange(num):
            pos = i + STORE_START
            iit = self.m_InterfaceItems[1].get(pos)
            if iit:
                iit.Enable(True)
                continue
        
        for i in xrange(num, 40):
            pos = i + STORE_START
            iit = self.m_InterfaceItems[1].get(pos)
            if iit:
                iit.Enable(False)
                continue
        

    
    def RefreshSH(self, pos):
        for p in self.m_InterfaceItems[1].keys():
            if p == pos:
                self.m_InterfaceItems[1][p].RefreshSHItem(p)
                break
                continue
        

    
    def RefreshAdjustBtn(self):
        btnAdjust = self.GetObject('btn_adjust')
        btnAdjust1 = self.GetObject('btn_adjust1')
        if btnAdjust.GetShow():
            btnAdjust.Enable(True)
        
        if btnAdjust1.GetShow():
            btnAdjust1.Enable(True)
        

    
    def RefreshTime(self, limittime):
        if self.m_LimitTime == 0:
            return None
        
        import time
        import combmacro
        self.m_LimitTime = limittime
        timetxt = '%d-%.2d-%.2d' % time.localtime(limittime)[:3]
        tm = time.time()
        if limittime - tm <= 259200:
            color = interface.COLOR_80
        else:
            color = interface.COLOR_4
        if interface.IsNewStyle():
            txt = '\xa8\xec\xb4\xc1\xae\xc9\xb6\xa1\xa1G#r%s' % timetxt
        else:
            txt = '\xa8\xec\xb4\xc1\xae\xc9\xb6\xa1\xa1G%s' % timetxt
        self.m_LimitTimeTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'time', self, txt, interface.FontLT12_1, color)
        self.RefreshAdjustBtn()

    
    def Adjust(self, itemData, startGap = 1):
        itemList = []
        operatorList = []
        for iif in itemData:
            it = iif.GetItem()
            if it:
                itemList.append((it.m_Shape, it.m_Quantity))
                continue
            itemList.append(None)
        
        itemNum = len(itemList)
        
        def merge():
            for i in range(itemNum):
                if itemList[i] is None:
                    continue
                
                (shape1, quantity1) = itemList[i]
                if quantity1 >= 5:
                    continue
                
                for j in range(i + 1, itemNum):
                    if itemList[j] is None:
                        continue
                    
                    (shape2, quantity2) = itemList[j]
                    if quantity2 >= 5:
                        continue
                    
                    if shape1 == shape2:
                        operatorList.append((j, i))
                        total = quantity2 + quantity1
                        if total > 5:
                            itemList[i] = (shape1, 5)
                            itemList[j] = (shape1, total - 5)
                        else:
                            itemList[i] = (shape1, total)
                            itemList[j] = None
                        return True
                        continue
                
            
            return False

        while merge():
            continue
            (None, None, None)
        for i in range(itemNum):
            minItem = itemList[i]
            moveIdx = i
            for j in range(i + 1, itemNum):
                if self.MaterialSortRule(minItem, itemList[j]):
                    moveIdx = j
                    minItem = itemList[j]
                    continue
            
            if moveIdx != i:
                operatorList.append((moveIdx, i))
                itemList[i] = itemList[moveIdx]
                itemList[moveIdx] = itemList[i]
                continue
        
        for j, i in operatorList:
            import netstorehouse
            netstorehouse.C2SSHMove(j + startGap, i + startGap, True)
        

    
    def MaterialSortRule(self, it1, it2):
        if it2 is None:
            return False
        
        if it1 is None:
            return True
        
        (shape1, quantity1) = it1
        (shape2, quantity2) = it2
        import itemdata
        if itemdata.IsType(shape1, 'equip') and itemdata.IsType(shape2, 'equip'):
            grade1 = itemdata.GetEquipLv(shape1)
            grade2 = itemdata.GetEquipLv(shape2)
            if grade2 < grade1:
                return True
            elif grade2 == grade1 and shape1 < shape2:
                return True
            elif shape1 == shape2 and quantity1 < quantity2:
                return True
            
        elif shape1 > shape2:
            return True
        elif shape1 == shape2:
            return quantity1 < quantity2
        else:
            return False

    
    def Adjust1(self, itemData, startGap = 1):
        interfaceItems = []
        empty = []
        for idx, iif in enumerate(itemData):
            it = iif.GetItem()
            if it:
                tmpit = interface.CBaseObject(None)
                tmpit.m_ID = it.m_ID
                tmpit.m_Shape = it.m_Shape
                tmpit.m_Pos = idx
                tmpit.m_Quantity = it.m_Quantity
                tmpit.m_Key = it.m_Key
                tmpit.m_InfoExt = it.m_InfoExt
                interfaceItems.append(tmpit)
            
            empty.append(idx)
        
        import itemprioritydata
        prioList = itemprioritydata.GetPrioList()
        prioData = itemprioritydata.GetPrioData()
        specialPrioList = itemprioritydata.GetSpePrioList()
        specialPrioData = itemprioritydata.GetSpePrioData()
        
        def keyFunc(it):
            shape = it.m_Shape
            if shape in prioList:
                prio = prioData[shape]
                return (0, prio)
            
            for func in specialPrioList:
                if func(shape):
                    prio = specialPrioData[func]
                    equipPriority = itemprioritydata.GetEquipPriority(shape)
                    return (0, prio + equipPriority)
                    continue
            
            return (1, shape)

        
        def keyfunc2(it):
            global g_PrevShape, g_PrevIdx, g_PrevShape
            if not g_PrevShape:
                g_PrevShape = it.m_Shape
            
            if it.m_Shape == g_PrevShape:
                if it.m_Key & 64 != 0:
                    return (g_PrevIdx, 0)
                else:
                    return (g_PrevIdx, it.m_Quantity)
            else:
                g_PrevIdx += 1
                g_PrevShape = it.m_Shape
                if it.m_Key & 64 != 0:
                    return (g_PrevIdx, 0)
                else:
                    return (g_PrevIdx, it.m_Quantity)

        
        def keyfunc3(it):
            if it.m_Shape == 72307:
                import petskill
                sName = it.m_InfoExt.split('\xa1G')[0]
                iId = petskill.GetSkillID(sName)
                return iId
            else:
                return None

        interfaceItems.sort(key = keyFunc)
        interfaceItems.sort(key = keyfunc2)
        interfaceItems.sort(key = keyfunc3)
        len_items = len(interfaceItems)
        empty.sort(cmp)
        action = []
        m1 = { }
        m2 = { }
        for i, v in enumerate(empty):
            if i < len_items:
                it = interfaceItems[i]
                if v != it.m_Pos:
                    action.append((it.m_Pos, v))
                    m1[v] = it.m_Pos
                    m2[it.m_Pos] = v
                
            v != it.m_Pos
        
        operation = []
        for v in action:
            if m1[v[1]] != v[1]:
                operation.append((m1[v[1]], v[1]))
                if v[1] in m2:
                    m1[m2[v[1]]] = m1[v[1]]
                    m2[m1[v[1]]] = m2[v[1]]
                
            v[1] in m2
        
        for j, i in operation:
            import netstorehouse
            netstorehouse.C2SSHMove(j + startGap, i + startGap, True)
        

    
    def ShowRenameDlg(self):
        if stopgamemoduleinterface.CheckStop(gamemoduledefines.GAMEMODULE_STORENAME):
            return None
        
        self.m_ReNameDlg = CSHReName(self, self.m_Name)

    
    def CommintSort(self):
        mode = self.m_SHMode & 1
        if mode == 1:
            sortFunc = self.Adjust
        else:
            sortFunc = self.Adjust1
        if self.m_Page == 1:
            itemLst = _[2]
            sortFunc(itemLst)
        elif self.m_Page == 2:
            itemLst = _[4]
            sortFunc(itemLst, 41)
        

    
    def ChoosePage(self, page):
        if self.m_IsBig == 2:
            ispage1 = page == 1
            ispage2 = page == 2
            self.m_Page = page
            for i in range(40):
                self.m_InterfaceItems[1][i + STORE_START].SetShow(ispage1)
                self.m_InterfaceItems[1][i + STORE_START + 40].SetShow(ispage2)
            
            self.GetObject('btn_Page1').Enable(ispage2)
            self.GetObject('btn_Page2').Enable(ispage1)
        

    
    def RemoveCallBacks(self):
        import hero
        hero.ReleaseDlgItem('dlgstorehouse', (('m_Cash', 0, 0),))
        import item
        item.ReleaseInterfaceCallback(self.m_InterfaceItems[0], 0)
        if self.m_IsBig == 2:
            item.ReleaseInterfaceCallback(self.m_InterfaceItems[1], 0)
        

    
    def CloseWindow(self):
        global g_StoreHouse
        import dlgmap
        import warui
        self.RemoveCallBacks()
        dlgmap.DisableMinimap(False)
        if hasattr(g_StoreHouse, 'ClearAllItemExt'):
            g_StoreHouse.ClearAllItemExt()
        
        g_StoreHouse = None
        warui.ShowMagicShortKey()

    
    def CheckBangDing(self, ikey):
        if ikey & 64 != 0:
            import usermacro
            usermacro.PROMPT_MSG('\xb8j\xa9w\xaa\xba\xb9D\xa8\xe3\xa4\xa3\xaf\xe0\xa9\xf1\xa4J\xaf\xd3\xa7\xf7\xad\xdc\xaew')
            return True
        

    
    def StoreConsumableItems(self, pos, destPos = 0):
        import netstorehouse
        if pos in self.m_InterfaceItems[0]:
            iif = self.m_InterfaceItems[0][pos]
            if iif.GetItem():
                it = iif.GetItem()
                netstorehouse.C2SPushSH(it.m_ID, iif.GetItem().m_Quantity, destPos, self.m_Page - 1, 0)
            
        

    
    def OnMessage(self, msgid):
        if self.CloseWindowByIdle():
            return None
        
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 8:
            self.ChoosePage(1)
        elif msgid == 9:
            self.ChoosePage(2)
        elif msgid == 3:
            import hero
            import usermacro
            if hero.g_Prop.m_IsGuestLogin == 0:
                ShowSetPwd()
            else:
                usermacro.PROMPT_MSG('\xb1z\xb7\xed\xabe\xb3B\xa9\xf3\xb9C\xab\xc8\xb5n\xbf\xfd\xaa\xac\xbaA\xa1A\xb5L\xaak\xb6i\xa6\xe6\xa6\xb9\xbe\xde\xa7@')
        elif msgid == 4:
            if self.m_LimitTime > 0:
                ShowPay(self.m_SHMode, self.m_FeePrice, self.m_FeeCash, self.m_FeeFightCash, self.m_LimitTime)
            
        elif msgid == 5:
            CStoreHouseDialog.s_MyBagPage = 0
        elif msgid == 6:
            CStoreHouseDialog.s_MyBagPage = 1
        elif msgid == 7:
            import hero
            import usermacro
            import netstorehouse
            if hero.g_Prop.m_IsGuestLogin == 0:
                netstorehouse.C2SOpenReNameDlg()
            else:
                usermacro.PROMPT_MSG('\xb1z\xb7\xed\xabe\xb3B\xa9\xf3\xb9C\xab\xc8\xb5n\xbf\xfd\xaa\xac\xbaA\xa1A\xb5L\xaak\xb6i\xa6\xe6\xa6\xb9\xbe\xde\xa7@')
        elif msgid == 14:
            import netstorehouse
            netstorehouse.C2SExpendSort()
        elif msgid == 10:
            import C_sys
            import netstorehouse
            t = C_sys.GetTime()
            if self.m_Name not in self.s_LastAdjustTime:
                self.s_LastAdjustTime[self.m_Name] = {
                    1: None,
                    2: None }
            
            lasttime = self.s_LastAdjustTime[self.m_Name][self.m_Page]
            if lasttime and lasttime < t and lasttime + 100000 > t:
                wtime = 10 - (t - lasttime) / 10000
                import usermacro
                usermacro.PROMPT_MSG('\xbe\xe3\xb2z\xa4@\xa6\xb8\xab\xe1\xa1A\xbd\xd0\xb5\xa5\xab\xdd%d\xac\xed\xa4~\xaf\xe0\xa6A\xa6\xb8\xbe\xe3\xb2z' % wtime)
                return None
            
            netstorehouse.C2SAskSortItem()
        elif msgid == 31:
            import C_sys
            import netstorehouse
            t = C_sys.GetTime()
            if self.m_Name not in self.s_LastAdjustTime:
                self.s_LastAdjustTime[self.m_Name] = {
                    1: None,
                    2: None }
            
            lasttime = self.s_LastAdjustTime[self.m_Name][self.m_Page]
            if lasttime and lasttime < t and lasttime + 100000 > t:
                wtime = 10 - (t - lasttime) / 10000
                import usermacro
                usermacro.PROMPT_MSG('\xbe\xe3\xb2z\xa4@\xa6\xb8\xab\xe1\xa1A\xbd\xd0\xb5\xa5\xab\xdd%d\xac\xed\xa4~\xaf\xe0\xa6A\xa6\xb8\xbe\xe3\xb2z' % wtime)
                return None
            
            self.s_LastAdjustTime[self.m_Name][self.m_Page] = t
            netstorehouse.C2SAskSortItem()
        elif msgid == 11:
            ShowEnterSH()
        elif msgid == 12:
            import netstorehouse
            netstorehouse.C2SUpGradeStoreHouse()
        elif msgid == 13:
            import nethero
            nethero.C2SPackItem(0)
            item.SetArrangeEnd(False)
        elif msgid == 15:
            import popmenu
            (x, y) = self.GetObject('btn_storemgr').GetPos()
            self.m_MgrMenu = popmenu.PopStoreMenu(self, x, y)
        elif _InItemBox(msgid - 100):
            if msgid - 100 in self.m_InterfaceItems[0]:
                iif = self.m_InterfaceItems[0][msgid - 100]
                if iif.GetItem():
                    iif.Take()
                
            
        elif _InSHBox(msgid):
            if msgid in self.m_InterfaceItems[1]:
                iif = self.m_InterfaceItems[1][msgid]
                if iif.GetItem():
                    iif.Take()
                
            
        elif _InItemBox(msgid - 100 - interface.RIGHT_BUTTON_MESSAGE):
            import C_sys
            import key
            if C_sys.IsKeyDown(key.VK_SHIFT):
                pos = msgid - 100 - interface.RIGHT_BUTTON_MESSAGE
                if pos in self.m_InterfaceItems[0]:
                    iif = self.m_InterfaceItems[0][pos]
                    if iif.m_Item and iif.m_Item.m_Shape in Item_Weapon:
                        if self.m_SHMode & 1 == 1:
                            import usermacro
                            usermacro.PROMPT_MSG('\xb8j\xa9w\xaa\xba\xb9D\xa8\xe3\xa4\xa3\xaf\xe0\xa9\xf1\xa4J\xaf\xd3\xa7\xf7\xad\xdc\xaew')
                        
                        return None
                    
                    if iif.GetItem():
                        import netstorehouse
                        import C_sys
                        netstorehouse.C2SPushSH(iif.GetItem().m_ID, 1, 0, self.m_Page - 1, 1)
                    
                
                return None
            
            pos = msgid - 100 - interface.RIGHT_BUTTON_MESSAGE
            self.StoreConsumableItems(pos)
        elif _InSHBox(msgid - interface.RIGHT_BUTTON_MESSAGE):
            import C_sys
            import key
            if C_sys.IsKeyDown(key.VK_SHIFT):
                pos = msgid - interface.RIGHT_BUTTON_MESSAGE
                if pos in self.m_InterfaceItems[1]:
                    iif = self.m_InterfaceItems[1][pos]
                    if iif.GetItem():
                        import netstorehouse
                        netstorehouse.C2SPopSH((iif.m_Pos - STORE_START) + 1, 1, 0)
                    
                
                return None
            
            pos = msgid - interface.RIGHT_BUTTON_MESSAGE
            if pos in self.m_InterfaceItems[1]:
                iif = self.m_InterfaceItems[1][pos]
                if iif.GetItem():
                    import netstorehouse
                    netstorehouse.C2SPopSH((iif.m_Pos - STORE_START) + 1, iif.GetItem().m_Quantity, 0)
                
            
        



def RefreshSHData(iPos, iShape, iAmount, sName, key = 0, iLevel = 0, sExt = None):
    if not isinstance(g_StoreHouse, CStoreHouseDialog):
        return None
    
    sh_pos = (iPos - 1) + STORE_START
    if not _InSHBox(sh_pos):
        return None
    
    for i, it in enumerate(g_Data):
        if it.m_Pos == sh_pos:
            if iShape == 0:
                del g_Data[i]
            else:
                itObj = SHItem(sh_pos, iShape, iAmount, key, iLevel, sExt)
                itObj.SetExtName(sName)
                g_Data[i] = itObj
            break
            continue
    elif iShape != 0:
        itObj = SHItem(sh_pos, iShape, iAmount, key, iLevel, sExt)
        itObj.SetExtName(sName)
        g_Data.append(itObj)
    
    g_StoreHouse.RefreshSH(sh_pos)


def RefreshSHTime(limittime):
    if not isinstance(g_StoreHouse, CStoreHouseDialog):
        return None
    
    g_StoreHouse.RefreshTime(limittime)


def ChoosePage(page):
    if not isinstance(g_StoreHouse, CStoreHouseDialog):
        return None
    
    g_StoreHouse.ChoosePage(page)


def SHItemSort():
    if g_StoreHouse and isinstance(g_StoreHouse, CStoreHouseDialog):
        g_StoreHouse.CommintSort()
    


def GetSHItem(pos):
    for i, it in enumerate(g_Data):
        if it.m_Pos == pos:
            return it
            continue
    


def ShowItem(pos):
    if g_StoreHouse is None:
        return None
    
    if _InItemBox(pos):
        iif = g_StoreHouse.m_InterfaceItems[0][pos]
    elif _InSHBox(pos):
        iif = g_StoreHouse.m_InterfaceItems[1][pos]
    else:
        return None
    if iif.GetItem():
        iif.SetItemShow(True)
    


def ArrangeItem():
    import netstorehouse
    interfaceItems = []
    empty = []
    for i, iif in enumerate(g_Data):
        it = interface.CBaseObject(None)
        it.m_ID = iif.m_ID
        it.m_Shape = iif.m_Shape
        it.m_Pos = iif.m_Pos
        interfaceItems.append(it)
        empty.append(i)
    
    
    def mycmp(a, b):
        pro_list = [
            25007,
            25008,
            25100,
            25010,
            25011,
            30031,
            30036,
            30034,
            40034]
        grade = 100000
        x = a.m_Shape
        y = b.m_Shape
        if x in pro_list:
            x -= grade
        
        if y in pro_list:
            y -= grade
        
        return cmp(x, y)

    interfaceItems.sort(mycmp)
    len_items = len(interfaceItems)
    empty.sort(cmp)
    action = []
    for i, v in enumerate(empty):
        if i < len_items:
            it = interfaceItems[i]
            if v != it.m_Pos - STORE_START:
                action.append(((it.m_Pos - STORE_START) + 1, v + 1))
            
        v != it.m_Pos - STORE_START
    
    m1 = { }
    m2 = { }
    for v in action:
        m1[v[1]] = v[0]
        m2[v[0]] = v[1]
    
    operation = []
    for v in action:
        if m1[v[1]] != v[1]:
            operation.append((m1[v[1]], v[1]))
            if v[1] in m2:
                m1[m2[v[1]]] = m1[v[1]]
                m2[m1[v[1]]] = m2[v[1]]
            
        v[1] in m2
    
    netstorehouse.C2SArrange(operation)
