# pycdc 交叉复核产物 · script.fls entry 477
# co_filename(原始)='script/dialog/dlgsmeltequip.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_477.pyc (Python 2.5)

import interface
import combdialog
import item
import itemmgr
g_SmeltDlg = None

def ModuleReset():
    global g_SmeltDlg
    g_SmeltDlg = None
    CSmeltDialog.ResetClear()


class CInterfaceItem(item.CInterfaceItem):
    
    def LeftUp(self):
        if self.m_MsgID:
            par = self.GetDlgParent()
            if not hasattr(par, 'OnMessage'):
                return None
            
            par.OnMessage(self.m_MsgID)
            self.CheckHoldObject()
        

    
    def RightUp(self):
        if self.m_MsgID:
            self.GetDlgParent().OnMessage(self.m_MsgID + interface.RIGHT_BUTTON_MESSAGE)
        else:
            par = self.GetParent()
            if hasattr(par, 'RightUp'):
                par.RightUp()
            

    
    def MouseWheelDown(self, p):
        parent = self.GetParent()
        if getattr(parent, 'MouseWheelDown', None):
            parent.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        parent = self.GetParent()
        if getattr(parent, 'MouseWheelUp', None):
            parent.MouseWheelUp(p)
        

    
    def GetDlgParent(self):
        p = self.GetParent()
        while p:
            if isinstance(p, interface.CDialogBase):
                return p
            
            p = p.GetParent()

    
    def Leave(self):
        item.CInterfaceItem.Leave(self)
        if getattr(self, 'm_IsSel', None):
            self.m_PosBox.SetShow(self.m_IsSel)
        

    
    def ShowItemLevel(self):
        itemID = getattr(self.m_Item, '\x8d_ID')
        if itemID and itemID in CSmeltDialog.s_ID2Point:
            itemLevel = CSmeltDialog.s_ID2Point[itemID]
            print itemLevel, itemID
            dItemLevel2Tips = {
                3: '\xa4w\xa5\xd3\xbd\xd0',
                2: '\xa5i\xba\xb2\xb7\xd2' }
            if itemLevel in dItemLevel2Tips:
                self.m_EquipPoint = interface.CTextObject(self.m_ItemImg, dItemLevel2Tips[itemLevel], interface.FontLT12E_1, 16711680, 0)
                (txtw, txth) = self.m_EquipPoint.GetSize()
                self.m_EquipPoint.SetPos(42 - txtw, 44 - txth)
                self.m_EquipPoint.SetZ(1)
            else:
                self.m_EquipPoint = None
        else:
            self.m_EquipPoint = None

    
    def ShowTeXiao(self):
        import style
        itemID = getattr(self.m_Item, '\x8d_ID')
        if itemID and itemID in CSmeltDialog.s_TieXiaoItemdct:
            (texiao, teji) = CSmeltDialog.s_TieXiaoItemdct[itemID]
            if texiao and teji:
                self.m_EquipDesc = interface.CRichTextObject(self.m_ItemImg, 200, interface.FontLT12E_1, '\xafS\xae\xc4#r\xafS\xa7\xde', 65280)
            elif texiao and not teji:
                self.m_EquipDesc = interface.CTextObject(self.m_ItemImg, '\xafS\xae\xc4', interface.FontLT12E_1, 65280, 0)
            else:
                self.m_EquipDesc = interface.CTextObject(self.m_ItemImg, '\xafS\xa7\xde', interface.FontLT12E_1, 65280, 0)
            (txtw, txth) = self.m_EquipDesc.GetSize()
            (offsetx, offsety) = style.GetIntTuple('dlgsmeltequip.CInterfaceItem', 'data_equipdesc')
            self.m_EquipDesc.SetPos((45 - txtw) + offsetx, 2 + offsety)
            self.m_EquipDesc.SetZ(1)
        else:
            self.m_EquipDesc = None



def ShowDlg():
    global g_SmeltDlg
    g_SmeltDlg = CSmeltDialog()


def RefreshSelMode(mode, point):
    if not g_SmeltDlg:
        return None
    
    if mode < mode:
        pass
    elif mode < 4:
        g_SmeltDlg.SelBtn(mode)
    
    g_SmeltDlg.RefreshSmeltPoint(mode, point)


def RefreshTeXiao(data):
    if g_SmeltDlg:
        g_SmeltDlg.RefreshTeXiao(data)
    


def PutDownItem():
    if g_SmeltDlg:
        g_SmeltDlg.OnPutDownItem()
    


class CSmeltDialog(combdialog.CCombDialog, itemmgr.CItemListBase):
    s_ID2Point = { }
    s_TieXiaoItemdct = { }
    
    def ResetClear(cls):
        cls.s_ID2Point = { }
        cls.s_TieXiaoItemdct = { }

    ResetClear = classmethod(ResetClear)
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/melting.dlg')
        itemmgr.CItemListBase.__init__(self, 'list', 'area_items1')
        interface.Center(self)
        self.m_SelIt = None
        self.m_LastSel = None
        self.CheckValid()
        self.RefreshItemPoints()

    
    def GetInterfaceItemClass(self):
        return CInterfaceItem

    
    def SelBtn(self, iMode):
        if iMode == 3:
            for i in range(3):
                obj = self.GetObject('btn_%d' % (i + 1))
                if obj.IsSelected():
                    obj.SetSelect(False)
                    continue
            
            return None
        
        self.GetObject('btn_%d' % iMode).LeftUp()

    
    def GetItems(self):
        import itemdata
        itemLst = []
        for pos, itemobj in item.g_Items[item.ITEM_NORMAL].items():
            if pos < 20:
                continue
            
            shape = itemobj.m_Shape
            level = getattr(itemobj, 'm_Level', 0)
            if itemdata.IsType(shape, 'equip') or level >= 80 or shape in range(68501, 68514):
                itemLst.append((pos, itemobj))
                continue
        
        return itemLst

    
    def CheckValid(self):
        import itemdata
        for iif in self.m_InterfaceItem.itervalues():
            if iif.GetItem():
                shape = iif.GetItem().m_Shape
                if itemdata.IsType(shape, 'equip'):
                    enable = True
                else:
                    enable = False
                iif.Enable(enable)
                iif.ShowShadow(not enable)
                continue
        

    
    def RefreshTeXiao(self, data):
        CSmeltDialog.s_TieXiaoItemdct = data
        for it in self.m_InterfaceItem.values():
            it.ShowTeXiao()
        

    
    def RefreshSmeltPoint(self, iMode, iPoint):
        if not self.m_SelIt:
            return None
        
        if iPoint > 0:
            import combmacro
            self.m_SmeltPoint = combmacro.CTEXT(interface.CTextObject, 'txt_point', self, '%d' % iPoint, interface.FontLT14_3, interface.COLOR_1)
            CSmeltDialog.s_ID2Point[self.m_SelIt.m_Item.\x8d_ID] = iMode
        else:
            itemID = self.m_SelIt.m_Item.\x8d_ID
            if itemID in CSmeltDialog.s_ID2Point:
                del CSmeltDialog.s_ID2Point[itemID]
            
            self.m_SmeltPoint = None
        self.RefreshItemPoints()

    
    def CreateDesc(self, idx):
        Idx2Desc = {
            1: '\xb8\xcb\xb3\xc6\xa5\xd3\xbd\xd0\xba\xb2\xb7\xd2\xa1G#r\xc7\xe9\xaf\xab\xbe\xb9\xa4\xce#Y\xb5\xa5\xaf\xc5\xa1\xd980#n\xaa\xba\xb8\xcb\xb3\xc6\xa5i\xa5H\xa5\xd3\xbd\xd0\xba\xb2\xb7\xd2#r\xc7\xea\xb7\xed\xba\xb2\xb7\xd2\xbfn\xa4\xc0\xb8\xfb\xb0\xaa\xae\xc9\xa1A\xbb\xdd\xadn#Y\xa4@\xa4\xd1#n\xb5\xa5\xab\xdd\xbdT\xbb{\xaa\xba\xae\xc9\xb6\xa1\xa1A\xba\xb2\xb7\xd2\xab\xe1\xa5i\xa5H\xa6b\xad\xdc\xaew\xba\xde\xb2z\xad\xfb\xb3B\xa7\xe4\xa6^#r\xc7\xeb\xba\xb2\xb7\xd2\xb8\xcb\xb3\xc6\xbb\xdd\xadn\xa5\xfd\xa9\xee\xb0\xa3\xb8\xcb\xb3\xc6\xaa\xba\xc4_\xa5\xdb\xa9M\xa4K\xa8\xf6',
            2: '\xbdT\xbb{\xba\xb2\xb7\xd2\xa1G#r\xc7\xe9\xba\xb2\xb7\xd2\xc0\xf2\xb1o\xaa\xba\xbfn\xa4\xc0\xa5i\xa5H\xa7I\xb4\xab\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8#r\xc7\xea\xba\xb2\xb7\xd2\xbfn\xa4\xc0\xb8\xfb\xb0\xaa\xaa\xba\xb8\xcb\xb3\xc6\xa1A\xa5i\xa5H\xa6b\xad\xdc\xaew\xba\xde\xb2z\xad\xfb\xb3B\xa7\xe4\xa6^\xa1F\xba\xb2\xb7\xd2\xbfn\xa4\xc0\xb8\xfb\xa7C\xaa\xba\xb8\xcb\xb3\xc6\xb5L\xaak\xa7\xe4\xa6^#r\xc7\xeb\xa5[\xc2\xea\xaa\xba\xb8\xcb\xb3\xc6\xb5L\xaak\xb6i\xa6\xe6\xba\xb2\xb7\xd2',
            3: '\xa8\xfa\xae\xf8\xba\xb2\xb7\xd2\xa5\xd3\xbd\xd0\xa1G#r\xa5i\xa5H\xb1N\xa4w\xb8g\xa5\xd3\xbd\xd0\xba\xb2\xb7\xd2\xaa\xba\xb8\xcb\xb3\xc6\xa6^\xb4_\xa8\xec\xa5\xbf\xb1`\xaa\xac\xbaA' }
        desc = Idx2Desc.get(idx, '')
        if desc:
            import combmacro
            if interface.IsNewStyle():
                desc = desc.replace('#Y', '#cED8900')
            
            self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'info', self, desc, interface.FontLT14_3, interface.COLOR_4)
        else:
            self.m_Desc = None

    
    def CreateSmeltItem(self, shape, pos):
        import itemdata
        (x, y) = self.GetObject('img_Item1').GetPos()
        z = self.GetObject('img_Item1').GetZ()
        self.m_ItemObj = item.CInterfaceItem(self, x + 4, y + 4, pos + 100)
        self.m_ItemObj.Refresh(pos)
        self.m_ItemObj.SetZ(z + 100)
        name = itemdata.GetData(shape)[0]
        self.m_TxtObject = interface.CTextObject(self, name, interface.FontLT14_3, interface.COLOR_1)
        self.m_TxtObject.SetPos(x + 68, y + 20)

    
    def RefreshItemPoints(self):
        for it in self.m_InterfaceItem.values():
            if it:
                it.ShowItemLevel()
                continue
        

    
    def OnClickItem(self, pos):
        it = self.m_InterfaceItem[pos]
        if self.m_SelIt == it:
            it.m_IsSel = False
            it.m_PosBox.SetShow(False)
            self.m_SelIt = None
            self.OnPutDownItem()
            return None
        
        self.m_SelIt = it
        if it and it.m_Item:
            if self.m_LastSel:
                self.m_LastSel.m_IsSel = False
                self.m_LastSel.m_PosBox.SetShow(False)
            
            it.m_IsSel = True
            it.m_PosBox.SetShow(True)
            self.m_LastSel = it
            import netcommon
            netcommon.C2SSelSmeltEquip(it.m_Item.\x8d_ID)
            self.CreateSmeltItem(it.m_Item.m_Shape, pos)
        

    
    def OnPutDownItem(self):
        self.m_ItemObj = None
        self.m_TxtObject = None
        self.m_SmeltPoint = None
        self.m_Desc = None

    
    def OnConfirm(self):
        if not getattr(self, 'm_SelIt', None):
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xb8\xcb\xb3\xc6')
            return None
        elif not getattr(self, 'm_SelMode', None):
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xc4\xbf\xef\xadn\xb6i\xa6\xe6\xaa\xba\xbe\xde\xa7@')
            return None
        
        itemID = self.m_SelIt.m_Item.\x8d_ID
        import netcommon
        netcommon.C2SSmeltEquip(self.m_SelMode, itemID)
        if itemID in CSmeltDialog.s_ID2Point:
            del CSmeltDialog.s_ID2Point[itemID]
        

    
    def CloseWindow(self):
        global g_SmeltDlg
        g_SmeltDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 4:
            self.OnConfirm()
        elif msgid in (8, 9, 10):
            self.m_SelMode = msgid - 7
            self.CreateDesc(self.m_SelMode)
        elif msgid == 11:
            import netcommon
            netcommon.C2SShowTradeDlg()
        elif msgid < msgid:
            pass
        elif msgid < 300:
            pos = msgid - 100
            self.OnClickItem(pos)
