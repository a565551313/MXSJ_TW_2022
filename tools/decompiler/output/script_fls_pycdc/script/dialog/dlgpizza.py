# pycdc 交叉复核产物 · script.fls entry 4759
# co_filename(原始)='script/dialog/dlgpizza.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4759.pyc (Python 2.5)

import re
import combdialog
import combmacro
import commoncb
import dlglabyrinthtreasuremain
import interface
import item
import itemdefine
import misc
import pagedlgbase
import permission
import pizza
import style
import timer
import ui
import usermacro
import wrapinterface
import itemdata
import warui
import mainmenu
g_Tips = None
g_PizzaBag = { }
g_dWarPizzaBag = { }
g_oTaskBag = None
g_PizzaBagFlag = True
g_PizzaBuff = { }
g_Sel2Explore = { }
g_GetDialog = None
g_BagWarMode = { }

def ModuleReset():
    global g_Tips, g_PizzaBag, g_PizzaBagFlag, g_PizzaBuff, g_Sel2Explore, g_GetDialog, g_ItemsID, g_BagWarMode, g_dWarPizzaBag, g_oTaskBag
    g_Tips = None
    g_PizzaBag = { }
    g_PizzaBagFlag = True
    g_PizzaBuff = { }
    g_Sel2Explore = { }
    g_GetDialog = None
    g_ItemsID = None
    g_BagWarMode = { }
    g_dWarPizzaBag = { }
    CMapManage.ResetClear()
    g_oTaskBag = None

g_Color = {
    1: 'combdialog/\xd4\xd3\xcd\xbc/\xbb\xd2'[-2:],
    2: 'combdialog/\xd4\xd3\xcd\xbc/\xb0\xd7'[-2:],
    3: 'combdialog/\xd4\xd3\xcd\xbc/\xc2\xcc'[-2:],
    4: 'combdialog/\xd4\xd3\xcd\xbc/\xc0\xb6'[-2:],
    5: 'combdialog/\xd4\xd3\xcd\xbc/\xb3\xc8'[-2:],
    6: 'combdialog/\xd4\xd3\xcd\xbc/\xb7\xdb\xba\xec'[-4:],
    7: 'combdialog/\xd4\xd3\xcd\xbc/\xd7\xcf'[-2:],
    8: 'combdialog/\xd4\xd3\xcd\xbc/\xbb\xc6'[-2:] }
TAO_ZHUANG = [
    71123,
    71124,
    71125,
    71126,
    71127,
    71372,
    71373,
    71374,
    71375,
    71376,
    71626,
    71634,
    71642,
    71643,
    71646,
    71137,
    71138,
    71139,
    71140,
    71141,
    71142,
    71388,
    71389,
    71390,
    71391,
    71392,
    71633,
    71625,
    71630,
    71647,
    71648,
    71143,
    71144,
    71145,
    71146,
    71147,
    71393,
    71394,
    71395,
    71396,
    71631,
    71635,
    71636,
    71644,
    72427,
    72428,
    72429,
    72430,
    72431,
    72432]

class CPizzaItem(interface.CBoxObject, interface.CClickObject):
    PATH1 = {
        26: TW_NOCHANGE('\xc3\xd4\xb9\xac\xb5\xc0\xbe\xdf\xbf\xf2'),
        53: TW_NOCHANGE('\xc3\xd4\xb9\xac\xb4\xf3\xb5\xc0\xbe\xdf\xbf\xf2') }
    PATH2 = {
        1: TW_NOCHANGE('\xbb\xd2'),
        2: TW_NOCHANGE('\xb0\xd7'),
        3: TW_NOCHANGE('\xc2\xcc'),
        4: TW_NOCHANGE('\xc0\xb6'),
        5: TW_NOCHANGE('\xb3\xc8'),
        6: TW_NOCHANGE('\xba\xec'),
        7: TW_NOCHANGE('\xd7\xcf'),
        8: TW_NOCHANGE('\xbb\xc6') }
    
    def __init__(self, parent, sizes, idx, mtype, desc):
        interface.CBoxObject.__init__(self, parent, sizes, sizes, 16711680, 0)
        interface.CClickObject.__init__(self, 0)
        self.m_Size = sizes
        self.m_Idx = idx
        self.m_Type = mtype
        self.CreateBg()
        self.m_Tips = None
        self.m_Desc = desc
        self.m_Grade = 0
        self.SetState(False)
        self.CreateTaoZhuangImg()

    
    def CreateBg(self):
        import itemdata
        realShape = itemdata.Shape2Image(self.m_Idx)
        if interface.IsNewStyle():
            if interface.IsStyle4():
                sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/1.png'
            elif interface.IsStyle5():
                sPath = 'combdialog5/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/1.png'
            else:
                sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/1.png'
            self.m_Mask = ui.CImage(self, sPath % (CPizzaItem.PATH1[self.m_Size], CPizzaItem.PATH2[self.m_Type]), interface.UIPath)
            if self.m_Size == 53:
                self.m_Mask.SetPos(-4, -4)
            elif self.m_Size == 26:
                self.m_Mask.SetPos(-1, -1)
            
        else:
            self.m_Mask = ui.CImage(self, 'combdialog/\xd4\xd3\xcd\xbc/%d\xce\xca\xba\xc5.igs' % self.m_Size, interface.UIPath)
            self.m_Mask.SetAlpha(80)
        self.m_Mask.SetShow(False)
        
        try:
            self.m_Bg = ui.CImage(self, 'item%d/%.5d.igs' % (self.m_Size, realShape), 'item')
        except:
            default = 71013
            if self.m_Size >= 53:
                default = 71131
            
            self.m_Bg = ui.CImage(self, 'item%d/%.5d.igs' % (self.m_Size, default), 'item')

        if interface.IsNewStyle() and self.m_Size == 26:
            self.m_Bg.SetPos(4, 4)
        

    
    def CreateNewFlash(self):
        if self.m_Bg:
            import dlgitem
            (w, h) = self.GetSize()
            z = self.m_Bg.GetZ()
            flashObj = dlgitem.CFlashBox(self.m_Bg, w, h)
            flashObj.SetZ(z - 1)
            newTextObj = dlgitem.CNewTextBox(self.m_Bg)
            newTextObj.SetPos(2, 2)
            newTextObj.SetZ(z + 2)
        else:
            flashObj = None
            newTextObj = None
        self.m_FlashObj = flashObj
        self.m_NewTextObj = newTextObj

    
    def ClearFlash(self):
        if hasattr(self, 'm_FlashObj') and self.m_FlashObj:
            self.m_FlashObj.Release()
            self.m_FlashObj = None
        
        if hasattr(self, 'm_NewTextObj') and self.m_NewTextObj:
            self.m_NewTextObj.Release()
            self.m_NewTextObj = None
        

    
    def GetParentDlg(self):
        return self.GetParent().GetParent()

    
    def CreateTaoZhuangImg(self):
        if self.m_Idx in TAO_ZHUANG:
            if interface.IsNewStyle():
                if interface.IsStyle4():
                    sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/\xcc\xd7\xd7\xb0\xd0\xc7\xd0\xc7/xingxing.png'
                elif interface.IsStyle5():
                    sPath = 'combdialog5/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/\xcc\xd7\xd7\xb0\xd0\xc7\xd0\xc7/xingxing.png'
                else:
                    sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/\xcc\xd7\xd7\xb0\xd0\xc7\xd0\xc7/xingxing.png'
                self.m_TaoZhuangImg = ui.CImage(self, sPath, interface.UIPath)
            else:
                self.m_TaoZhuangImg = ui.CImage(self, '\xd4\xd3\xcd\xbc/\xd0\xc7\xd0\xc7.igs', interface.UIPath)
            (w, _) = self.GetSize()
            (imgW, _) = self.m_TaoZhuangImg.GetSize()
            x = w - imgW
            if interface.IsNewStyle() and self.m_Size == 26:
                x = x + 6
            
            self.m_TaoZhuangImg.SetPos(x, 0)
            self.m_TaoZhuangImg.SetZ(50)
        

    
    def CheckGrade(self):
        parent = self.GetParentDlg()
        if self.m_State and parent and parent.IsOwner() and self.m_Grade != pizza.GetData(self.m_Idx)[5]:
            return True
        
        return False

    
    def SetState(self, state):
        if state:
            self.m_State = True
            self.SetGrade(self.m_Grade)
        else:
            self.m_State = False
        if interface.IsNewStyle() and self.CheckGrade():
            self.m_Mask.SetShow(self.m_State)
            self.m_Bg.SetShow(self.m_State)
            self.m_Bg.SetZ(self.m_Mask.GetZ() + 1)
        else:
            self.m_Mask.SetShow(not (self.m_State))
            self.m_Bg.SetShow(self.m_State)
        if hasattr(self, 'm_TaoZhuangImg'):
            self.m_TaoZhuangImg.SetShow(self.m_State)
        

    
    def SetGrade(self, grade):
        self.m_Grade = grade
        if self.m_State and grade != pizza.GetData(self.m_Idx)[5]:
            self.GetParentDlg().m_Backgrounds[self.m_Idx].SetShow(False)
        

    
    def Enter(self):
        global g_Tips
        import dlggetinfo
        parent = self.GetParentDlg()
        if self.m_State:
            g_Tips = dlggetinfo.NewItemInfo(self.m_Idx, self.m_Idx, '', None, None)
            g_Tips.Topmost()
            if parent and parent.IsOwner() and self.m_Grade != pizza.GetData(self.m_Idx)[5]:
                self.ShowLimitTips()
            
        
        if parent and hasattr(parent, 'm_ChooseBox'):
            if interface.IsNewStyle():
                sizetype = {
                    26: TW_NOCHANGE('\xd0\xa1\xd1\xa1\xd6\xd0\xbf\xf2'),
                    53: TW_NOCHANGE('\xb4\xf3\xd1\xa1\xd6\xd0\xbf\xf2') }
                if interface.IsStyle4():
                    sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s.png'
                elif interface.IsStyle5():
                    sPath = 'combdialog5/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s.png'
                else:
                    sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s.png'
                parent.m_ChooseBox = ui.CImage(self, sPath % sizetype[self.m_Size], interface.UIPath)
                if self.m_Size == 26:
                    parent.m_ChooseBox.SetPos(-1, -1)
                
            else:
                parent.m_ChooseBox = ui.CImage(self, 'combdialog/\xd4\xd3\xcd\xbc/%d\xb8\xdf\xc1\xc1.igs' % self.m_Size, interface.UIPath)
            parent.m_ChooseBox.SetZ(20)
            if self.m_Size == 53:
                (x, y) = style.GetIntTuple('dlgpizza.CPizzaItem', 'data_selbox_pos')
                parent.m_ChooseBox.SetPos(x, y)
            
        
        self.ClearFlash()

    
    def ShowLimitTips(self):
        import ratio
        if ratio.Is1024x768():
            (x, y) = (420, 180)
        elif ratio.Is1366x768():
            (x, y) = (548, 180)
        elif ratio.Is1366x708():
            (x, y) = (548, 150)
        elif ratio.Is1280x960():
            (x, y) = (510, 276)
        else:
            (x, y) = (300, 130)
        txt = '\xa5\xd1\xa9\xf3\xb1z\xaa\xba\xb1\xb4\xaf\xc1\xab\xd7\xb9F\xa8\xec\xa4F#Y\xb5\xa5\xaf\xc5\xa4W\xad\xad#n\xa1A\xb4\xa3\xa4\xc9\xb5\xa5\xaf\xc5\xab\xe1#Y\xa6A\xa6\xb8\xa4W\xa5\xe6#n\xb8\xd3\xc4_\xaa\xab\xa5i\xbcW\xa5[\xb8\xd3\xc4_\xaa\xab\xaa\xba\xb3\xd1\xbel\xb1\xb4\xaf\xc1\xab\xd7'
        self.m_LimitTips = wrapinterface.CTextTips(None, 200, txt, interface.FontLT14_3, direct = 1)
        self.m_LimitTips.SetPos(x, y)

    
    def Leave(self):
        global g_Tips
        self.m_LimitTips = None
        g_Tips = None
        
        try:
            parent = self.GetParent()
        except SystemError:
            return None

        if parent and hasattr(parent, 'm_ChooseBox'):
            parent.m_ChooseBox = None
        



class CNeedIconBtn(interface.CButton):
    
    def __init__(self, oParent, oOwner, iMsgID):
        sFileName = style.GetPath('combdialog/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xbc\xbc\xc4\xdc\xbf\xf2\xbc\xd3\xba\xc5')
        interface.CButton.__init__(self, oParent, sFileName, 0, 0, iMsgID)
        self.m_oWrOwner = misc.WeakRef(oOwner)

    
    def LeftUp(self):
        interface.CButton.LeftUp(self)
        self.m_oWrOwner().LeftUp()

    
    def LeftDown(self):
        interface.CButton.LeftDown(self)
        self.m_oWrOwner().LeftDown()

    
    def Enter(self):
        self.m_oTipsObj = wrapinterface.CTextTips(self, -1, '\xa7\xd6\xb3t\xc1\xca\xb6R\xafS\xae\xc4\xc3\xc4', interface.FontLT14_3)
        self.m_oTipsObj.SetZ(10)
        self.m_oWrOwner().Enter()

    
    def Leave(self):
        self.m_oTipsObj = None
        self.m_oWrOwner().Leave()

    
    def OnHand(self, hand):
        self.m_oWrOwner().OnHand(hand)


g_dBagPos = { }

def CancelSelect(iItem):
    if g_oTaskBag:
        g_oTaskBag.OnCancelSelect(iItem)
    


class CPizzaBag(combdialog.CCombDialog):
    OPENTYPE_NORMAL = 0
    OPENTYPE_WAR = 1
    OPENTYPE_TASK = 2
    
    def __init__(self, bagid, type, parent, bInWar, iTaskID = 0):
        if type == itemdefine.BAGTYPE_DRUG:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/item/item_yaobao.dlg')
        elif type == 0:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/pizza/bag.dlg')
        elif type == 1:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/bag.dlg')
        elif type == 2:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/pizza/bag.dlg')
            self.GetObject('noname0').ChgCaptionTxt('\xbe\xd4\xb3\xf5\xb1M\xa5\xce\xadI\xa5]')
        elif type == 3:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/fish/yulou.dlg')
        elif type == itemdefine.BAG_TYPE_GEM:
            combdialog.CCombDialog.__init__(self, parent, 'dialog/equip/baoshibag.dlg')
        
        self.m_iTaskID = iTaskID
        self.m_BagID = bagid
        self.m_iBagType = type
        self.m_bInWar = bInWar
        self.m_InterfaceItems = { }
        self.m_oExtWidgets = []
        commoncb.RegistCB(commoncb.BAG_ITEM_CHANGE, self, 'OnBagItemUpdate')
        item.AddInterfaceCallback(self.m_InterfaceItems, item.ITEM_BAGS, oRefObj = self)
        self.SetZ(99999)
        self.ShowItems(0)
        self.m_oOwnerWr = None
        self.m_oOwnerTimer = None

    
    def CheckOwnerIsExist(self):
        if self.m_oOwnerWr:
            if self.m_oOwnerWr():
                pass
            if not self.m_oOwnerWr().GetShow():
                self.SetShow(False)
                if self.m_oOwnerTimer:
                    self.m_oOwnerTimer.Release()
                    self.m_oOwnerTimer = None
                
            

    
    def SetOwner(self, oOwner):
        self.m_oOwnerWr = misc.WeakRef(oOwner)
        if not self.m_oOwnerTimer:
            self.m_oOwnerTimer = timer.Timer(0.033, self.CheckOwnerIsExist, -1, self)
        

    
    def GetBagType(self):
        return self.m_iBagType

    
    def ReleaseInterfaceCallback(self):
        item.ReleaseInterfaceCallback(self.m_InterfaceItems, item.ITEM_BAGS)

    
    def ShowItems(self, page):
        import task
        import main
        obj = self.GetObject('btn%d' % (page + 1))
        if obj:
            obj.SetSelect(True)
        
        msgid = 100
        obj = self.GetObject('area_item')
        if hasattr(obj, 'm_Real') and obj.m_Real:
            for iit in obj.m_Real:
                real_obj = iit.Get()
                if real_obj:
                    real_obj.Clear()
                    continue
            
        
        obj.m_Real = []
        (ox, oy) = obj.GetPos()
        total = obj.GetTotal()
        begin = 1 + total * page
        lstNeed = []
        if self.m_bInWar == self.OPENTYPE_TASK:
            lstNeed = task.GetTaskNeedDrug(self.m_iTaskID)
        
        for i in xrange(total):
            pos = i + begin
            (x, y) = obj.m_Imagess[i].GetPos()
            iit = item.CInterfaceBagsItem(self, ox + x, oy + y, pos + msgid, self.m_InterfaceItems)
            iit.m_BagID = self.m_BagID
            iit.Refresh(pos)
            obj.m_Real.append(interface.CShadowObject(iit))
            if iit.GetItem():
                if self.m_bInWar:
                    iit.SetUsedRedMark(item.IsCacheUsedDrugItem(iit.GetItemId()))
                
                if self.m_iBagType == itemdefine.BAGTYPE_DRUG:
                    iit.ShowQualityInfo()
                    if permission.IsOpenFightOptimize() and main.InWar() and hasattr(iit, 'CheckDrugItem'):
                        iit.CheckDrugItem()
                    
                    if self.m_bInWar == self.OPENTYPE_TASK:
                        iit.ShowShadow(iit.GetShape() not in lstNeed)
                    
                
            
            iit.SetShow(obj.GetShow())
        
        self.CheckCreateExtwidget()

    
    def SetEffecDrugGrey(self):
        '''
\t\t\xb8m\xa6\xc7\xafS\xae\xc4\xc3\xc4
\t\t:return:
\t\t'''
        for oItem in self.m_InterfaceItems.values():
            if oItem and oItem.GetItem():
                oDrugObj = oItem.GetItem()
                iShape = oDrugObj.GetShape()
                if itemdata.IsType(iShape, 'effectdrug'):
                    oItem.SetGrey()
                
            itemdata.IsType(iShape, 'effectdrug')
        

    
    def OnBagItemUpdate(self, dChangeData):
        iBagID = dChangeData.get('iBagID', 0)
        if self.m_BagID == iBagID:
            self.CheckCreateExtwidget()
            self.ShowGemLevel()
            self.ShowItems(0)
        
        iCanUseDrugsCount = warui.GetDrugUseTimes()
        if iCanUseDrugsCount <= 0 and mainmenu.IsWar():
            self.SetEffecDrugGrey()
        

    
    def OnCancelSelect(self, iItemID):
        for iPos, oItem in self.m_InterfaceItems.iteritems():
            if oItem and oItem.m_Item and iItemID == oItem.m_Item.GetID():
                oItem.Select(False)
                break
                continue
        

    
    def ShowGemLevel(self):
        if self.m_iBagType != itemdefine.BAG_TYPE_GEM:
            return None
        
        for oItemInterface in self.m_InterfaceItems.itervalues():
            if oItemInterface and oItemInterface.GetItem():
                oItem = oItemInterface.GetItem()
                sDesc = oItem.m_Desc
                oSerch = re.search('\\d+', sDesc)
                if oSerch:
                    iLevel = int(oSerch.group())
                else:
                    iLevel = 0
                oItem.m_Level = iLevel
                oItemInterface.ShowItemLevel()
                continue
        

    
    def CheckCreateExtwidget(self):
        self.m_oExtWidgets = []
        oAreaItem = self.GetObject('area_item')
        if self.m_iBagType == itemdefine.BAGTYPE_DRUG:
            for iIndex in xrange(oAreaItem.GetTotal()):
                oItemInterface = self.m_InterfaceItems[iIndex + 1]
                oItem = oItemInterface.GetItem()
                if not oItem:
                    (iW, iH) = oAreaItem.GetImageList()[iIndex].GetSize()
                    (iOX, iOY) = oAreaItem.GetImageList()[iIndex].GetPos()
                    (iX, iY) = oAreaItem.GetPos()
                    oNeedIcon = CNeedIconBtn(self, oItemInterface, 4)
                    (iBW, iBH) = oNeedIcon.GetSize()
                    oNeedIcon.SetPos(iX + iOX + (iW - iBW) / 2, iY + iOY + (iH - iBH) / 2)
                    oNeedIcon.SetZ(1)
                    self.m_oExtWidgets.append(oNeedIcon)
                    return None
                    continue
            
        

    
    def SetDefaultPos(self, offx = 0, offy = 0):
        import ratio
        iMaxW = ratio.WINDOW_WIDTH
        (w, _) = self.GetParent().GetSize()
        (x, _) = self.GetParent().GetPos()
        (ow, _) = self.GetSize()
        if x + w + offx + ow / 2 <= iMaxW:
            self.SetPos(w + offx, offy)
        else:
            self.SetPos(-w + offx, offy)

    
    def Hold(self):
        if self.m_bInWar:
            self.m_oOwnerWr().Hold()
        else:
            combdialog.CCombDialog.Hold(self)

    
    def LeftDown(self):
        if self.m_bInWar:
            self.m_oOwnerWr().LeftDown()
        else:
            combdialog.CCombDialog.LeftDown(self)

    
    def LeftUp(self):
        if self.m_bInWar:
            self.m_oOwnerWr().LeftUp()
        else:
            combdialog.CCombDialog.LeftUp(self)

    
    def RightUp(self):
        if self.m_bInWar:
            self.m_oOwnerWr().RightUp()
        else:
            combdialog.CCombDialog.RightUp(self)

    
    def OnCopyItemInfo(self, curItem):
        import itemdata
        import chatinput
        if curItem:
            itemID = curItem.m_ID
            shape = curItem.m_Shape
            amount = curItem.m_Quantity
            name = itemdata.GetItemServerName(curItem)
            if name is None:
                name = itemdata.GetData(shape)[0]
            
            if shape in chatinput.g_SpecialItem:
                (func, _) = chatinput.g_SpecialItem[shape]
                if callable(func):
                    name = func(curItem)
                
            
            import copylinkobj
            import kuafulink
            copylinkobj.CreateCopyLink(kuafulink.CLinkItem.CLIENT_TYPE, itemID, shape, name, amount, self.m_BagID)
        

    
    def OnNeedIconClick(self):
        import consignmalldefines
        import dlgconsignmall
        import mdconsignmallbuy
        if self.m_iBagType == itemdefine.BAGTYPE_DRUG:
            oModel = mdconsignmallbuy.GetBuyModel()
            oModel.ClearSelectData()
            oModel.SetSelectShelfID(consignmalldefines.DRUG_SHELF_IDS[0])
            oModel.SetBuyMode(consignmalldefines.BUYMODE_QUICK)
            dlgconsignmall.Show(consignmalldefines.PAGE_BUY)
            if dlgconsignmall.g_ConsignMall:
                dlgconsignmall.g_ConsignMall.SetZ(self.GetZ() + 1)
            
        

    
    def RealCloseWindow(self):
        if self.m_BagID in g_PizzaBag:
            if g_PizzaBag[self.m_BagID] == self:
                g_dBagPos[self.m_BagID] = self.GetPos()
                del g_PizzaBag[self.m_BagID]
            
        
        if self.m_BagID in g_dWarPizzaBag:
            if g_dWarPizzaBag[self.m_BagID] == self:
                del g_dWarPizzaBag[self.m_BagID]
            
        
        CloseTaskBag()
        self.ReleaseInterfaceCallback()

    
    def OnClickItem(self, iMsgId):
        '''
\t\t\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xc3\xc4\xab~
\t\t:param iMsgId:
\t\t:return:
\t\t'''
        import mainmenu
        import C_sys
        import key
        iPos = iMsgId - 100
        oItem = self.m_InterfaceItems[iPos]
        oDrugObj = oItem.GetItem()
        if oDrugObj:
            iShape = oDrugObj.GetShape()
            iCanUseDrugsCount = warui.GetDrugUseTimes()
            if iCanUseDrugsCount <= 0 and itemdata.IsType(iShape, 'effectdrug') and mainmenu.IsWar():
                usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xa6A\xa8\xcf\xa5\xce\xa6\xb9\xc3\xfe\xc3\xc4\xaa\xab\xa4F')
                return None
            
        
        if mainmenu.IsWar():
            if self.m_bInWar == self.OPENTYPE_WAR and oItem and oItem.GetItem():
                if hasattr(self.m_oOwnerWr(), 'OnBagUseItemInWar'):
                    self.m_oOwnerWr().OnBagUseItemInWar(self.m_iBagType, oItem.GetItem())
                
            
            return None
        
        if self.m_bInWar == self.OPENTYPE_TASK:
            self.m_oOwnerWr()._AddItemQuantity(oItem, 1)
            return None
        
        if C_sys.IsKeyDown(key.VK_SHIFT):
            self.OnCopyItemInfo(oItem.GetItem())
        else:
            oItem.Take()

    
    def OnMessage(self, iMsgId):
        import nethero
        import netopenui
        if iMsgId == 1:
            self.RealCloseWindow()
        elif self.m_iBagType == itemdefine.BAGTYPE_DRUG and iMsgId in (2, 3):
            if iMsgId == 2:
                netopenui.C2SOneKeyPutInDrag(self.m_BagID)
            elif iMsgId == 3:
                nethero.C2SZhenliBag(self.m_BagID)
            
        elif iMsgId in (2, 3):
            self.ShowItems(iMsgId - 2)
        elif iMsgId == 4:
            self.OnNeedIconClick()
        elif iMsgId < iMsgId:
            pass
        elif iMsgId <= 130:
            self.OnClickItem(iMsgId)
        elif iMsgId - interface.RIGHT_BUTTON_MESSAGE < iMsgId - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif iMsgId - interface.RIGHT_BUTTON_MESSAGE <= 130:
            iPos = iMsgId - interface.RIGHT_BUTTON_MESSAGE - 100
            oItem = self.m_InterfaceItems[iPos]
            oDrugObj = oItem.GetItem()
            if oDrugObj:
                import nethero
                nethero.C2SBagItemUse(self.m_BagID, oDrugObj.m_ID)
            
        



def ShowBag(bagid, type):
    global g_PizzaBagFlag
    import warui
    import dlgitem
    import ratio
    import mainmenu
    if g_BagWarMode.get(type, False):
        pass
    bInWarMode = mainmenu.IsRealWar()
    if not bInWarMode:
        if dlgitem.g_ItemDialog and dlgitem.g_ItemDialog.GetShow():
            pass
        else:
            dlgitem.ShowSwitch()
        if bagid in g_PizzaBag and g_PizzaBag[bagid] and hasattr(g_PizzaBag[bagid], 'ReleaseInterfaceCallback'):
            g_PizzaBag[bagid].ReleaseInterfaceCallback()
        
    elif not warui.g_ItemDialog:
        return None
    
    if bagid in g_dWarPizzaBag and g_dWarPizzaBag[bagid] and hasattr(g_dWarPizzaBag[bagid], 'ReleaseInterfaceCallback'):
        g_dWarPizzaBag[bagid].ReleaseInterfaceCallback()
    
    if not bInWarMode:
        oBag = CPizzaBag(bagid, type, interface.DialogPanel, bInWarMode)
        g_PizzaBag[bagid] = oBag
        (t, p) = (8, 12)
        if type != itemdefine.BAGTYPE_DRUG:
            if g_PizzaBagFlag:
                dlgitem.g_ItemDialog.SetPos(t, p)
                g_PizzaBagFlag = False
            
        
        (w, h) = dlgitem.g_ItemDialog.GetSize()
        i = 0
        hh = 0
        for t1 in g_PizzaBag:
            dlg = g_PizzaBag[t1]
            (ww1, hh1) = dlg.GetSize()
            if t1 in g_dBagPos:
                g_PizzaBag[t1].SetPos(*g_dBagPos[t1])
            elif interface.IsNewStyle() and t + w + 4 + ww1 + 20 > ratio.WINDOW_WIDTH:
                dlg.SetPos(ratio.WINDOW_WIDTH - ww1 - 20, p + hh + 3 * i)
            else:
                dlg.SetPos(t + w + 4, p + hh + 3 * i)
            hh += hh1
            i += 1
        
    else:
        oDlg = warui.g_ItemDialog
        oBag = CPizzaBag(bagid, type, oDlg, bInWarMode)
        (iX, iY) = oDlg.GetPos()
        (iW, iH) = oDlg.GetSize()
        oBag.SetOwner(oDlg)
        g_dWarPizzaBag[bagid] = oBag
        g_dWarPizzaBag[bagid].SetPos(iW, 0)
        oDlg.SetPos((ratio.WINDOW_WIDTH - oBag.GetSize()[0] - oDlg.GetSize()[0]) / 2, iY)


def ShowBagWithParent(iBagId, oParent, taskid):
    global g_oTaskBag
    import ratio
    if g_oTaskBag and hasattr(g_oTaskBag, 'ReleaseInterfaceCallback'):
        g_oTaskBag.ReleaseInterfaceCallback()
    
    oDlg = oParent
    oBag = CPizzaBag(iBagId, itemdefine.BAGTYPE_DRUG, oDlg, CPizzaBag.OPENTYPE_TASK, taskid)
    (iX, iY) = oDlg.GetPos()
    (iW, iH) = oDlg.GetSize()
    oBag.SetOwner(oDlg)
    g_oTaskBag = oBag
    g_oTaskBag.SetPos(iW, 0)
    oDlg.SetPos((ratio.WINDOW_WIDTH - oBag.GetSize()[0] - oDlg.GetSize()[0]) / 2, iY)


def CloseTaskBag():
    global g_oTaskBag
    if g_oTaskBag and hasattr(g_oTaskBag, 'ReleaseInterfaceCallback'):
        g_oTaskBag.ReleaseInterfaceCallback()
    
    g_oTaskBag = None


def SetBagTypeInWar(iBagType, bInWar):
    g_BagWarMode[iBagType] = bInWar


def IsBagTypeShow(iBagType, bInWar):
    if not bInWar:
        for oBag in g_PizzaBag.itervalues():
            if oBag.GetBagType() == iBagType:
                return True
                continue
        
    else:
        for oBag in g_dWarPizzaBag.itervalues():
            if oBag.GetBagType() == iBagType:
                return True
                continue
        
    return False


def CloseBagByType(iBagType, bInWar):
    if not bInWar:
        for iBagID in g_PizzaBag.keys():
            oBag = g_PizzaBag[iBagID]
            if oBag.GetBagType() == iBagType:
                oBag.RealCloseWindow()
                continue
        
    else:
        for iBagID in g_dWarPizzaBag.keys():
            oBag = g_dWarPizzaBag[iBagID]
            if oBag.GetBagType() == iBagType:
                oBag.RealCloseWindow()
                continue
        


def CloseAllBag(bInWar):
    if not bInWar:
        for iBagID in g_PizzaBag.keys():
            oBag = g_PizzaBag[iBagID]
            oBag.RealCloseWindow()
        
    else:
        for iBagID in g_dWarPizzaBag.keys():
            oBag = g_dWarPizzaBag[iBagID]
            oBag.RealCloseWindow()
        


class CItem44(interface.CClickBox):
    
    def __init__(self, parent, shape, name, extStr, msgid = 0):
        interface.CClickBox.__init__(self, parent, 209, 55, 0, 0, msgid)
        self.m_ItemImg = item.CreateItem44Image(self, shape)
        self.m_ItemImg.SetPos(5, 5)
        self.m_Title = interface.CTextObject(self, name, interface.FontLT14_3, interface.COLOR_1, 0)
        self.m_Title.SetPos(55, 10)
        color_define = style.GetStr('dlgpizza.CItem44', 'data_define_color')
        if shape in TAO_ZHUANG:
            extStr = '%s\xa1]\xaeM\xb8\xcb\xa1^#n  ' % color_define + extStr
        
        self.m_TaoZhangTxt = interface.CRichTextObject(self, 1000, interface.FontLT14_3, extStr, interface.COLOR_1)
        self.m_TaoZhangTxt.SetPos(55, 30)



class CGetDialog(combdialog.CCombDialog):
    
    def __init__(self, shape, btnTxt):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/pizza/info.dlg')
        interface.Center(self)
        self.Capture(1, 1)
        self.m_sTipsText = ''
        if btnTxt:
            lst = btnTxt.split(',')
            self.CreateBtns(lst)
        
        self.CreatePizzaInfo(shape)

    
    def Refresh(self, shape, btnTxt):
        self.m_BtnList = []
        if btnTxt:
            txtList = btnTxt.split(',')
            self.CreateBtns(txtList)
        
        self.CreatePizzaInfo(shape)

    
    def CreatePizzaInfo(self, shape):
        import pizza1
        name1 = ''
        grade = 0
        desc1 = ''
        if pizza1.DATA.get(shape):
            (name1, desc1) = pizza1.GetData(shape)
            grade = 0
        
        for oid, name, id, mtype, desc, _ in pizza.DATA:
            if id == shape:
                name1 = name
                desc1 = desc
                grade = mtype
                continue
        
        if shape <= shape:
            pass
        elif shape <= 71710:
            grade = 0
        
        self.m_ImgShape = shape
        self.m_ImgName = name1
        self.m_Grade = grade
        self.m_ImgShape = shape
        if name1:
            obj = self.GetObject('noname1')
            (x, y) = obj.GetPos()
            self.m_Img = CItem44(self, shape, name1, '\xab~\xac\xdb%d\xaf\xc5' % grade, 2)
            self.m_Img.SetPos(x, y)
            self.m_Desc = combmacro.CreateRichText(interface.CRichTextObject, 'desc', self, desc1, interface.FontLT14_3, interface.COLOR_4)
        

    
    def GetTextButtonData(self, btnName):
        if interface.IsNewStyle():
            sPath = style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xb0\xb4\xc5\xa6\xb6\xfe\xd7\xd6.igs')
            sBtnStyle = style.GetStr(self.GetDlgPath(), 'data_btn_style')
            return [
                sBtnStyle,
                sPath,
                btnName,
                10 * len(btnName),
                3,
                0,
                0,
                0]
        elif len(btnName) == 10:
            return [
                style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xb0\xb4\xc5\xa6\xc1\xf9\xd7\xd6.igs'),
                btnName,
                3,
                0]
        
        return [
            style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xb0\xb4\xc5\xa6\xcb\xc4\xd7\xd6.igs'),
            btnName,
            3,
            0]

    
    def CreateBtns(self, txtList):
        self.m_BtnList = []
        btnName = txtList[0]
        if len(btnName) == 10:
            x1 = 19
            x2 = 127
            x = 205
        else:
            x1 = 28
            x2 = 112
            x = 196
        data = self.GetTextButtonData(btnName)
        data.reverse()
        btn = combdialog.CTextButton(self, data)
        if interface.IsNewStyle():
            x1 = 28
            x2 = 135
            x = 246
        
        h = style.GetInt(self.GetDlgPath(), 'data_btn_y')
        btn.SetPos(x1, h)
        btn.m_BtnName = btnName
        self.m_BtnList.append(btn)
        if len(txtList) > 1:
            btnName = txtList[1]
            sPath = style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xb0\xb4\xc5\xa6\xb6\xfe\xd7\xd6.igs')
            if interface.IsNewStyle():
                sBtnStyle = style.GetStr(self.GetDlgPath(), 'data_btn_style')
                data = [
                    sBtnStyle,
                    sPath,
                    btnName,
                    10 * len(btnName),
                    4,
                    0,
                    0,
                    0]
            else:
                data = [
                    style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xb0\xb4\xc5\xa6\xcb\xc4\xd7\xd6.igs'),
                    btnName,
                    4,
                    0]
            data.reverse()
            btn = combdialog.CTextButton(self, data)
            btn.SetPos(x2, h)
            btn.m_BtnName = btnName
            self.m_BtnList.append(btn)
        
        self.GetObject('btn_Close').SetPos(x, h)
        btnName2Tips = {
            '\xacB\xa8\xfa\xc4_\xaa\xab': '\xacB\xa8\xfa\xc4_\xaa\xab\xa5i\xa5H\xb1N\xc4_\xaa\xab\xb5n\xb0O\xa6b\xa6\xdb\xa4v\xaa\xba\xa6\xac\xc2\xc3\xa5U\xa4W',
            '\xb0O\xbf\xfd\xabH\xae\xa7': '\xb0O\xbf\xfd\xc4_\xaa\xab\xabH\xae\xa7\xa5i\xa5H\xc0\xf2\xb1o\xa6\xe6\xb7|\xc1n\xb1\xe6\xa4\xce\xa8\xe4\xa5L\xbc\xfa\xc0y' }
        for btn in self.m_BtnList:
            if btn.m_BtnName in btnName2Tips:
                txt = btnName2Tips[btn.m_BtnName]
                btn.m_TipsStr = txt
                btn.m_TipsDirect = 1
                continue
        

    
    def RefreshTips(self, sTipsText):
        import usermacro
        if self.m_sTipsText:
            usermacro.RemoveTipsByText(self.m_sTipsText)
        
        if sTipsText:
            usermacro.PROMPT_MSG(sTipsText)
        
        self.m_sTipsText = sTipsText

    
    def CloseWindow(self):
        global g_GetDialog
        import usermacro
        if self.m_sTipsText:
            usermacro.RemoveTipsByText(self.m_sTipsText)
        
        g_GetDialog = None

    
    def OnMessage(self, msgid):
        if msgid in (1, 5):
            self.CloseWindow()
        elif msgid == 2:
            import copylinkobj
            import hero
            import C_sys
            import key
            if C_sys.IsKeyDown(key.VK_SHIFT):
                copylinkobj.CreateCopyLink(28, hero.g_ID, self.m_ImgShape, self.m_ImgName)
            
        elif msgid == 3:
            import \x8f\x84\x95npc
            \x8f\x84\x95npc.C2SNpcAnswer(1)
            self.CloseWindow()
        elif msgid == 4:
            import \x8f\x84\x95npc
            \x8f\x84\x95npc.C2SNpcAnswer(2)
            self.CloseWindow()
        



class CMyListBox(interface.CListBox):
    
    def OnSelect(self, sel):
        if sel < 0 or sel > len(self.m_TextList):
            return None
        
        self.Clear()
        self.AddText(self.m_TextList[sel - 1])
        self.m_List = None
        self.m_Selected = sel
        if hasattr(self, 'm_SelectNotify') and self.m_SelectNotify:
            self.GetParent().OnChooseEdit(sel)
        



class CClickNotifyBox(interface.CClickBox):
    
    def GetPar(self):
        
        try:
            par = self.GetParent()
        except SystemError:
            par = None

        return par

    
    def Enter(self):
        par = self.GetPar()
        if par:
            par.OnEnter(self.m_MsgID)
        

    
    def Leave(self):
        par = self.GetPar()
        if par:
            par.OnLeave(self.m_MsgID)
        

    
    def LeftDown(self):
        pass



class CSubMapList(combdialog.CCombSubWnd, pagedlgbase.COnePageDlgBase):
    sUIName = 'dialog/pizza/maze_topbottom.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.m_LastFlush = misc.Time()

    
    def VClose(self):
        self.SetShow(False)

    
    def VOpenPage(self, dExtend = None):
        if dExtend:
            userId = dExtend.get('userId')
            mapID = dExtend.get('mapID')
            userName = dExtend.get('userName')
            dMapData = dExtend.get('dMapData')
            tExploerData = dExtend.get('tExploerData')
            lastItems = dExtend.get('lastItems')
            self.RefreshData(userId, mapID, userName, dMapData, tExploerData, lastItems)
        
        self.SetShow(True)

    
    def CreateListBox(self):
        mapNameLst = ('\xaa\xf7\xa6r\xb6\xf0', '\xaf\xb3\xac\xd3\xb3\xae', '\xa7l\xa6\xe5\xa5j\xb3\xf9')
        self.m_ListBox = combmacro.CLISTBOX(CMyListBox, 'box_choose', self, interface.COLOR_5, interface.FontLT14_3)
        for mapName in mapNameLst:
            self.m_ListBox.AddTextItem(mapName)
        
        self.m_ListBox.SetReadOnly(True)
        self.m_ListBox.SetItemProp(0, 16, 48)
        self.m_ListBox.OnSelect(self.m_MapID)
        self.m_ListBox.m_SelectNotify = True
        self.m_ListBox.SetShow(False)
        obj = self.GetObject('box_choose')
        self.m_MapInfo = interface.CRichTextObject(obj, 500, interface.FontLT14_3, self.m_MapName, 16777215)
        self.m_MapInfo.SetPos(0, 0)
        self.m_MapInfo.SetZ(1)
        interface.Center(self.m_MapInfo, offsety = self.GetMapInfoOffSetY() / 2)

    
    def GetMapInfoOffSetY(self):
        return style.GetInt(self.GetDlgPath(), 'data_mapinfo_offset_y')

    
    def OnChooseEdit(self, sel):
        import hero
        if hasattr(self, 'm_OwnerID') and self.m_OwnerID == hero.g_ID:
            CMapManage.SaveMazeMapID(sel)
        
        if self.m_OwnerID in g_PizzaBuff and sel in g_PizzaBuff[self.m_OwnerID] and self.m_OwnerID in g_Sel2Explore and sel in g_Sel2Explore[self.m_OwnerID]:
            self.RefreshData(self.m_OwnerID, sel, self.m_OwnerName, g_PizzaBuff[self.m_OwnerID][sel], g_Sel2Explore[self.m_OwnerID][sel])
        else:
            import nethero
            nethero.C2SChiocePizza(self.m_OwnerID, sel)

    
    def CreateImgClickBox(self):
        imgObj = self.GetObject('img_Tips')
        (nx, ny) = imgObj.GetPos()
        (nw, nh) = imgObj.GetSize()
        self.m_Notify = CClickNotifyBox(self, nw, nh, 0, 0, 5)
        self.m_Notify.SetPos(nx, ny)

    
    def RefreshData(self, userid, mapid, name, data, tExploerData, lastItems = None):
        if lastItems is None:
            lastItems = []
        
        (self.m_PersonExplore, self.m_ServerExplore, self.m_MaxPeroneExp) = tExploerData
        self.m_MapID = mapid
        self.m_OwnerID = userid
        self.m_OwnerName = name
        self.SetMapInfos()
        self.m_Data = self.ChgData(data, self.m_MapName)
        self.m_Cts = [
            0] * 8
        self.m_ChooseBox = None
        self.m_Edges = []
        self.m_Backgrounds = { }
        self.m_Maps = { }
        self.m_TxtLst = []
        self.m_NewItems = lastItems
        self.DrawItems()
        self.ShowPageBtn()
        self.RefreshChoose()
        self.MakeCt(self.m_PersonExplore)
        self.CreateListBox()
        self.CreateImgClickBox()
        self.ShowBtnLink()

    
    def SetMapInfos(self):
        mapNameDct = {
            1: '\xaa\xf7\xa6r\xb6\xf0',
            2: '\xaf\xb3\xac\xd3\xb3\xae',
            3: '\xa7l\xa6\xe5\xa5j\xb3\xf9' }
        dataRangeDct = {
            1: range(152) + range(507, 554),
            2: range(152, 303),
            3: range(303, 454) }
        dataStartDct = {
            1: (0, 355),
            2: 151,
            3: 302 }
        self.m_MapName = mapNameDct.get(self.m_MapID, mapNameDct[1])
        self.m_DataRange = dataRangeDct.get(self.m_MapID, dataRangeDct[1])
        self.m_DataStart = dataStartDct.get(self.m_MapID, dataStartDct[1])

    
    def RefreshChoose(self):
        listBox = getattr(self, 'm_ListBox', None)
        if listBox:
            listBox.SetText(self.m_MapName)
        
        mapInfo = getattr(self, 'm_MapInfo', None)
        if mapInfo:
            mapInfo.SetText(self.m_MapName)
            interface.Center(mapInfo, offsety = self.GetMapInfoOffSetY() / 2)
        
        self.GetObject('btn_Page1').LeftUp()

    
    def GetAreaType(self, oid, mtype):
        if oid < 507:
            if mtype <= mtype:
                pass
            elif mtype <= 5:
                return 0
            
            if mtype <= mtype:
                pass
            elif mtype <= 8:
                return 1
            
        elif mtype <= mtype:
            pass
        elif mtype <= 5:
            return 2
        
        if mtype <= mtype:
            pass
        elif mtype <= 8:
            return 3
        

    
    def FigureObjPos(self, areaName, areaType, mtype, pos, figureType = 0):
        if interface.IsStyle4() or interface.IsStyle5():
            iStyleOffset = (4, 4)
        else:
            iStyleOffset = (interface.STYLE * 2, interface.STYLE * 2)
        areaObj = self.GetObject(areaName)
        (sx, sy) = (4, 4)
        (addx, addy) = None if areaType == 0 else iStyleOffset
        (rows, cols) = areaObj.m_Size
        px = pos / cols
        py = pos % cols
        (x, y) = areaObj.GetImage(px, py).GetPos()
        x += addx
        y += addy
        if figureType == 0:
            return (x - sx, y - sy, x, y)
        elif figureType == 1:
            return (x, y)
        

    
    def CreateBackground(self, idx, mtype, oid, sizes):
        pathDct = {
            'edge1': 'combdialog/\xd4\xd3\xcd\xbc/26X26%s.igs' % g_Color[mtype],
            'bg1': 'item26/26X26%s.igs' % g_Color[mtype],
            'edge2': 'combdialog/\xd4\xd3\xcd\xbc/53X53%s.igs' % g_Color[mtype],
            'bg2': 'item53/53X53%s.igs' % g_Color[mtype] }
        areaInfo = {
            0: ('area_item1', pathDct['bg1'], pathDct['edge1']),
            1: ('area_item2', pathDct['bg2'], pathDct['edge2']),
            2: ('area_item3', pathDct['bg2'], pathDct['edge2']),
            3: ('area_item4', pathDct['bg2'], pathDct['edge2']) }
        pngpath1 = {
            26: TW_NOCHANGE('\xc3\xd4\xb9\xac\xb5\xc0\xbe\xdf\xbf\xf2'),
            53: TW_NOCHANGE('\xc3\xd4\xb9\xac\xb4\xf3\xb5\xc0\xbe\xdf\xbf\xf2') }
        pngpath2 = {
            1: TW_NOCHANGE('\xbb\xd2'),
            2: TW_NOCHANGE('\xb0\xd7'),
            3: TW_NOCHANGE('\xc2\xcc'),
            4: TW_NOCHANGE('\xc0\xb6'),
            5: TW_NOCHANGE('\xb3\xc8'),
            6: TW_NOCHANGE('\xba\xec'),
            7: TW_NOCHANGE('\xd7\xcf'),
            8: TW_NOCHANGE('\xbb\xc6') }
        areaType = self.GetAreaType(oid, mtype)
        (areaName, bgPath, edgePath) = areaInfo[areaType]
        infoLst = self.m_ItemNum['area%d' % (areaType + 1)]
        pos = infoLst[0]
        infoLst[0] += 1
        areaObj = self.GetObject(areaName)
        (x1, y1, x2, y2) = self.FigureObjPos(areaName, areaType, mtype, pos, 0)
        if interface.IsNewStyle():
            if interface.IsStyle4():
                sPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/0.png'
            elif interface.IsStyle5():
                sPath = 'combdialog5/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/0.png'
            else:
                sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xc3\xd4\xb9\xac/%s%s/0.png'
            imgObj = ui.CImage(areaObj, sPath % (pngpath1[sizes], pngpath2[mtype]), interface.UIPath)
            (x, y) = None if sizes == 53 else (x2 - 1, y2 - 1)
            imgObj.SetPos(x, y)
        else:
            edgeObj = ui.CImage(areaObj, edgePath, interface.UIPath)
            imgObj = ui.CImage(areaObj, bgPath, 'item')
            edgeObj.SetPos(x1, y1)
            imgObj.SetPos(x2, y2)
            self.m_Edges.append(edgeObj)
        self.m_Backgrounds[idx] = imgObj
        return (areaName, pos)

    
    def CreateItemImg(self, areaName, sizes, pos, oid, id, mtype, desc):
        areaObj = self.GetObject(areaName)
        areaType = self.GetAreaType(oid, mtype)
        imgObj = CPizzaItem(areaObj, sizes, id, mtype, desc)
        imgObj.Topmost()
        imgObj.m_ID = oid
        imgObj.m_Shape = id
        OH = 0
        (x, y) = self.FigureObjPos(areaName, areaType, mtype, pos, 1)
        if type(self.m_DataStart) != int:
            posKey = None if oid < 507 else oid - 1 - self.m_DataStart[1]
        else:
            posKey = oid - 1 - self.m_DataStart
        if posKey in self.m_Data:
            (OH, gd) = self.m_Data[posKey]
            imgObj.SetGrade(gd)
        
        if not posKey in self.m_Data and self.m_Data[posKey][0] != 0 and self.m_Data[posKey][1] != 0:
            self.m_Backgrounds[id].SetShow(False)
        
        imgObj.SetState(OH)
        if posKey in self.m_NewItems:
            imgObj.CreateNewFlash()
        
        if mtype in range(1, 9) and imgObj.m_State:
            self.m_Cts[mtype - 1] += 1
            areaTxt = 'area%d' % (areaType + 1)
            self.m_ItemNum[areaTxt][1] += 1
        
        imgObj.SetPos(x, y)
        self.m_Maps[oid] = imgObj

    
    def DrawItems(self):
        self.m_ItemNum = {
            'area1': [
                0,
                0],
            'area2': [
                0,
                0],
            'area3': [
                0,
                0],
            'area4': [
                0,
                0] }
        for oid, name, id, mtype, desc, _ in pizza.DATA:
            if oid not in self.m_DataRange:
                continue
            
            areaType = self.GetAreaType(oid, mtype)
            sizes = None if areaType == 0 else 53
            (areaName, pos) = self.CreateBackground(id, mtype, oid, sizes)
            self.CreateItemImg(areaName, sizes, pos, oid, id, mtype, desc)
        
        self.ShowOwner()
        self.ShowItemNumByPage(1)

    
    def ShowOwner(self):
        color = interface.COLOR_5
        self.m_TxtLst.append(combmacro.CTEXT(interface.CTextObject, 'txt_owner', self, self.m_OwnerName, interface.FontLT14_3, color, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))

    
    def ShowItemNumByPage(self, page):
        if page == 1:
            areaNormal = 'area1'
            areaSpecial = 'area2'
        else:
            areaNormal = 'area3'
            areaSpecial = 'area4'
        (numNormalAll, numNormalOwn) = self.m_ItemNum[areaNormal]
        (numSecialAll, numSepcialOwn) = self.m_ItemNum[areaSpecial]
        txtNumNormal = '%d/%d' % (numNormalOwn, numNormalAll)
        txtNumSpecial = '%d/%d' % (numSepcialOwn, numSecialAll)
        txtClass = interface.CTextObject
        self.m_NumTxt = []
        self.m_NumTxt.append(combmacro.CTEXT(txtClass, 'box_num', self, txtNumNormal, interface.FontLT14_3, interface.COLOR_4))
        self.m_NumTxt.append(combmacro.CTEXT(txtClass, 'box_numspecial', self, txtNumSpecial, interface.FontLT14_3, interface.COLOR_4))

    
    def ShowBtnLink(self):
        btn = self.GetObject('btn_Link')
        if btn:
            import hero
            import misc
            if self.IsOwner():
                pass
            bShow = not misc.IsInKuafuServer()
            btn.SetShow(bShow)
        

    
    def ShowPageBtn(self):
        mapid = getattr(self, 'm_MapID', None)
        showFlag = mapid == 1
        self.GetObject('btn_Page1').SetShow(showFlag)
        self.GetObject('btn_Page1').m_ParentNotify = showFlag
        self.GetObject('btn_Page2').SetShow(showFlag)
        self.GetObject('btn_Page2').m_ParentNotify = showFlag

    
    def IsOwner(self):
        import hero
        ownerID = getattr(self, 'm_OwnerID', None)
        return ownerID == hero.g_ID

    
    def OnButtonEnter(self, btnObj):
        self.OnEnter(btnObj.m_MsgID)

    
    def OnButtonLeave(self, btnObj):
        self.OnLeave(btnObj.m_MsgID)

    
    def OnEnter(self, msgid):
        txtDct = {
            5: '\xb1\xb4\xaf\xc1\xab\xd7\xb6V\xb0\xaa\xa1A\xa5X\xb2{\xb0\xaa\xaf\xc5\xc4_\xaa\xab\xaa\xba\xb7\xa7\xb2v\xb6V\xb0\xaa#r\xb7\xed\xabe\xaaA\xb0\xc8\xbe\xb9\xb1\xb4\xaf\xc1\xab\xd7\xac\xb0#Y%d#n#r\xb7\xed\xabe\xa8\xa4\xa6\xe2\xb5\xa5\xaf\xc5\xaa\xba\xb1\xb4\xaf\xc1\xab\xd7\xa4W\xad\xad\xac\xb0#R%d#n' % (self.m_ServerExplore, self.m_MaxPeroneExp),
            7: '%s\xc4_\xaa\xab' % self.m_MapName,
            8: '%s\xbf\xf2\xa5\xa2\xc4_\xaa\xab' % self.m_MapName }
        txt = txtDct.get(msgid)
        if txt:
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def ChgData(self, data, mapname):
        import copy
        mapname2chgpos = {
            '\xa7l\xa6\xe5\xa5j\xb3\xf9': {
                125: 124,
                137: 132,
                143: 142 } }
        data1 = copy.deepcopy(data)
        if mapname in mapname2chgpos:
            for bpos in data1:
                if bpos in mapname2chgpos[mapname]:
                    tmppos = bpos
                    tmpdata = data1[bpos]
                    bpos = mapname2chgpos[mapname][bpos]
                    data1[tmppos] = data1[bpos]
                    data1[bpos] = tmpdata
                    continue
            
        
        return data1

    
    def MakeCt(self, personExplore):
        color = interface.COLOR_5
        self.m_TxtLst.append(combmacro.CTEXT(interface.CTextObject, 'noname2', self, str(personExplore), interface.FontLT14_3, color, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))

    
    def AskRefresh(self):
        import misc
        t = misc.Time()
        if t - self.m_LastFlush > 3:
            self.m_LastFlush = t
            import nethero
            nethero.C2SChiocePizza(self.m_OwnerID, self.m_MapID)
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            CMapManage.Hide()
        elif msgid == 2:
            self.AskRefresh()
        elif msgid == 3:
            import nethero
            nethero.C2SOpenMazePassInfo(self.m_MapID, self.m_OwnerID)
        elif msgid in [
            4,
            5,
            interface.RIGHT_BUTTON_MESSAGE + 5]:
            import dlgtool_lycos_new
            dlgtool_lycos_new.ShowHelper('\xb0g\xaec\xb1\xb4\xaf\xc1\xb6i\xab\xd7')
        elif msgid == 6:
            import copylinkobj
            import hero
            import kuafulink
            if not hero.g_ID:
                return None
            
            copylinkobj.CreateCopyLink(kuafulink.CLinkPizzaDlg.CLIENT_TYPE)
        elif msgid in (7, 8):
            page = msgid - 6
            self.ShowItemNumByPage(page)
        elif msgid in (9, 10):
            dx = None if msgid == 9 else -1
            mapID = (self.m_MapID + dx + 2) % 3 + 1
            self.OnChooseEdit(mapID)
        



class CMapManage(object):
    s_Dialog = None
    s_LastSelectMapid = None
    s_OwnerID = None
    
    def IsOpenNew(cls):
        return True

    IsOpenNew = classmethod(IsOpenNew)
    
    def ResetClear(cls):
        cls.s_Dialog = None
        cls.s_LastSelectMapid = None
        cls.s_OwnerID = None

    ResetClear = classmethod(ResetClear)
    
    def IsOpen(cls):
        return dlglabyrinthtreasuremain.CLabyrinthTreasureDlg.IsOpen()

    IsOpen = classmethod(IsOpen)
    
    def ShowMapCollection(cls, userId, mapID, userName, dMapData, tExploerData, lastItems):
        import hero
        cls.IsDifferentMapDlg(userId)
        cls.SetMapData(userId, mapID, dMapData, tExploerData)
        bIsSelf = userId == hero.GetHeroID()
        if bIsSelf:
            tData = cls.GetMapData(userId)
            if not tData:
                return None
            
            (mapID, dMapData, tExploerData) = tData
        
        oDlg = dlglabyrinthtreasuremain.CLabyrinthTreasureDlg.OpenUI()
        oDlg.VOpenPage({
            'iSub': 1,
            'dExtend': {
                'bIsSelf': bIsSelf,
                'userId': userId,
                'mapID': mapID,
                'userName': userName,
                'dMapData': dMapData,
                'tExploerData': tExploerData,
                'lastItems': lastItems } })
        cls.s_OwnerID = userId

    ShowMapCollection = classmethod(ShowMapCollection)
    
    def GetMapData(cls, userId):
        mapID = cls.GetMazeMapID()
        if userId in g_PizzaBuff and mapID in g_PizzaBuff[userId] and userId in g_Sel2Explore and mapID in g_Sel2Explore[userId]:
            return (mapID, g_PizzaBuff[userId][mapID], g_Sel2Explore[userId][mapID])
        else:
            import nethero
            nethero.C2SChiocePizza(userId, mapID)
            return None

    GetMapData = classmethod(GetMapData)
    
    def Hide(cls):
        global g_PizzaBuff, g_Sel2Explore
        import dlglabyrinthtreasuremain
        dlglabyrinthtreasuremain.CLabyrinthTreasureDlg.CloseUI()
        cls.s_OwnerID = None
        g_PizzaBuff = { }
        g_Sel2Explore = { }

    Hide = classmethod(Hide)
    
    def GetMazeMapID(cls):
        import hero
        if not cls.s_LastSelectMapid:
            
            try:
                cls.s_LastSelectMapid = int(hero.GetPrivateData('MazeMapID', 'mapID'))
            cls.s_LastSelectMapid = 1

        
        return cls.s_LastSelectMapid

    GetMazeMapID = classmethod(GetMazeMapID)
    
    def SaveMazeMapID(cls, mapID):
        if mapID:
            import hero
            cls.s_LastSelectMapid = mapID
            hero.SavePrivateData('MazeMapID', 'mapID', str(mapID))
        

    SaveMazeMapID = classmethod(SaveMazeMapID)
    
    def IsDifferentMapDlg(cls, userId):
        if cls.IsOpen():
            if userId != cls.s_OwnerID:
                cls.Hide()
            
        elif cls.s_Dialog and userId != cls.s_Dialog.m_OwnerID:
            cls.Hide()
        

    IsDifferentMapDlg = classmethod(IsDifferentMapDlg)
    
    def SetMapData(cls, userId, mapID, dMapData, tExploerData):
        if userId in g_PizzaBuff:
            g_PizzaBuff[userId][mapID] = dMapData
        else:
            g_PizzaBuff[userId] = {
                mapID: dMapData }
        if userId in g_Sel2Explore:
            g_Sel2Explore[userId][mapID] = tExploerData
        else:
            g_Sel2Explore[userId] = {
                mapID: tExploerData }

    SetMapData = classmethod(SetMapData)


def ShowGet(iShape, sBtnText, sTipsText):
    global g_GetDialog
    if not g_GetDialog:
        g_GetDialog = CGetDialog(iShape, sBtnText)
    else:
        g_GetDialog.Refresh(iShape, sBtnText)
    g_GetDialog.RefreshTips(sTipsText)
