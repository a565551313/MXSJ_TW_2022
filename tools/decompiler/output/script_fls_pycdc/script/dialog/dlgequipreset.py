# pycdc 交叉复核产物 · script.fls entry 423
# co_filename(原始)='script/dialog/dlgequipreset.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_423.pyc (Python 2.5)

import interface
import wrapinterface
import combdialog
g_EquipResetDlg = None

def ModuleReset():
    global g_EquipResetDlg
    g_EquipResetDlg = None


class CEquipResetDlg(combdialog.CCombDialog):
    
    def __init__(self, npcid):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/nationfight/equipreset.dlg')
        interface.Center(self)
        import netnpc
        netnpc.SetMakeCallback(self.OnCompose)
        self.m_InterfaceItem = { }
        import combmacro
        import item
        item.AddInterfaceCallback(self.m_InterfaceItem, oRefObj = self)
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_items1', self, item.ITEM_START, self.m_InterfaceItem, 100)
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_fight', self, item.ITEM_FIGHT_START, self.m_InterfaceItem, 100)
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_items2', self, item.ITEM_SCOPE, self.m_InterfaceItem, 100)
        self.GetObject('item').LeftUp()
        self.m_SelectItems = [
            None,
            None]
        self.m_NpcID = npcid

    
    def OnCompose(self, shape, amount, desc):
        import combmacro
        import item
        obj = self.GetObject('box_result')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        for <tf in self.m_SelectItems:
            if <tf:
                self.m_InterfaceItem[<tf.m_Pos].Select(False)
                (ix, iy) = <tf.GetPos()
                (iw, ih) = <tf.GetSize()
                xstep = (x + (w - iw) / 2 - ix) / 30
                ystep = (y + (h - ih) / 2 - iy) / 30
                <tf.m_PosList = [ (ix + xstep * i, iy + ystep * i) for i in range(29, 0, -1) ]
                <tf.m_ItemImg.SetAlpha(207)
                self.ShowMoveObj(<tf)
                continue
            []
        
        self.m_SelectItems = [
            None,
            None]
        self.ShowComp((shape, amount, desc))

    
    def ShowMoveObj(self, obj):
        if obj and obj.m_PosList:
            
            try:
                self.m_MoveObjList.append(obj)
            except:
                self.m_MoveObjList = [
                    obj]

            self.StartMove()
        

    
    def StartMove(self):
        if not self.m_MoveObjList:
            return None
        
        if hasattr(self, 'm_MoveCmd') and self.m_MoveCmd:
            return None
        
        
        def MoveCalls(obj):
            remove_list = []
            for fobj in obj.m_MoveObjList:
                if fobj.m_PosList:
                    (x, y) = fobj.m_PosList.pop()
                    fobj.SetPos(int(x), int(y))
                    continue
                remove_list.append(fobj)
            
            for fobj in remove_list:
                obj.m_MoveObjList.remove(fobj)
            
            if obj.m_MoveObjList:
                return ()
            
            obj.m_MoveCmd.Release()
            obj.m_MoveCmd = None

        self.m_MoveCmd = self.CreatePyCommand(1, MoveCalls)

    
    def ShowComp(self, data):
        if data:
            (shape, amount, desc) = data
            import wrapinterface
            msgid = 10
            self.m_OuputItem = wrapinterface.CItemIcon(self, shape, amount, msgid)
            self.m_OuputItem.m_InfoExt = desc
            obj = self.GetObject('box_result')
            (x, y) = obj.GetPos()
            (w, h) = obj.GetSize()
            (iw, ih) = self.m_OuputItem.GetSize()
            self.m_OuputItem.SetPos(x + (w - iw) / 2, y + (h - ih) / 2)
        else:
            self.m_OuputItem = None

    
    def OnIconEnter(self, obj):
        obj.ShowTips()

    
    def OnIconLeave(self, obj):
        obj.HideTips()

    
    def AddEquip(self, pos):
        import combmacro
        self.ShowComp(None)
        seliit = self.m_InterfaceItem[pos]
        if seliit and seliit.GetItem():
            selectItemsIds = self.GetSelectItemsIds()
            if seliit.GetItem().m_ID in selectItemsIds:
                return None
            
            for idx in xrange(len(self.m_SelectItems)):
                if not self.m_SelectItems[idx]:
                    (x, y, _, _) = combmacro.GetIFObjectData(self, 'box_make', 0, idx)
                    import item
                    iit = item.CInterfaceItem(self, x, y, 500 + idx)
                    iit.Refresh(pos)
                    iit.SetPos(x, y)
                    self.m_SelectItems[idx] = iit
                    self.m_InterfaceItem[pos].Select(True)
                    break
                    continue
            
        

    
    def DeleteEquip(self, idx):
        iit = self.m_SelectItems[idx]
        self.m_SelectItems[idx] = None
        self.m_InterfaceItem[iit.m_Pos].Select(False)

    
    def RefreshShadow(self):
        if hasattr(self, 'CheckValid'):
            self.CheckValid()
        

    
    def GetSelectItemsIds(self):
        selectItemsIds = []
        for seliit in self.m_SelectItems:
            if seliit:
                selectItemsIds.append(seliit.GetItem().m_ID)
                continue
        
        return selectItemsIds

    
    def GetSelectItemsShapes(self):
        selectItemsShapes = []
        for seliit in self.m_SelectItems:
            if seliit:
                selectItemsShapes.append(seliit.GetItem().m_Shape)
                continue
        
        return selectItemsShapes

    
    def CloseWindow(self):
        global g_EquipResetDlg
        import netnpc
        import item
        g_EquipResetDlg = None
        netnpc.SetMakeCallback(None)
        item.ReleaseInterfaceCallback(self.m_InterfaceItem)
        item.ReleaseShadowCallback('DlgEquipReset')

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid <= msgid:
            pass
        elif msgid <= 300:
            self.AddEquip(msgid - 100)
        elif msgid in (500, 501):
            self.DeleteEquip(msgid - 500)
        elif msgid == 2:
            itemids = []
            for iit in self.m_SelectItems:
                if not iit or not iit.GetItem():
                    return None
                
                itemids.append(iit.GetItem().m_ID)
            
            if len(itemids) != 2:
                return None
            
            import netpet
            { }
        



class CPetEquipResetDlg(CEquipResetDlg):
    VALIDSHAPES = [
        25501,
        25502,
        25503,
        25504,
        25505,
        25506,
        25507,
        25508,
        25509,
        25510,
        25511,
        25512,
        72222,
        72223,
        72224]
    
    def __init__(self, npcid):
        CEquipResetDlg.__init__(self, npcid)
        self.CheckValid()

    
    def GetValid(self, oItem):
        if oItem:
            iShape = oItem.m_Shape
            selectItemsShapes = self.GetSelectItemsShapes()
            if not selectItemsShapes:
                return iShape in CPetEquipResetDlg.VALIDSHAPES
            else:
                return iShape == selectItemsShapes[0]
        
        return False

    
    def OnCompose(self, shape, amount, desc):
        CEquipResetDlg.OnCompose(self, shape, amount, desc)
        self.CheckValid()

    
    def AddEquip(self, pos):
        import item
        import combmacro
        self.ShowComp(None)
        if pos in self.m_InterfaceItem:
            seliit = self.m_InterfaceItem[pos]
            if seliit.IsSelected():
                if self.m_SelectItems[0] and self.m_SelectItems[0].m_Pos == pos:
                    seliit.Select(False)
                    self.m_SelectItems[0] = None
                elif self.m_SelectItems[1] and self.m_SelectItems[1].m_Pos == pos:
                    seliit.Select(False)
                    self.m_SelectItems[1] = None
                
                self.CheckValid()
                return seliit
            
            for idx in xrange(len(self.m_SelectItems)):
                if not self.m_SelectItems[idx]:
                    (x, y, _, _) = combmacro.GetIFObjectData(self, 'box_make', 0, idx)
                    iit = item.CInterfaceItem(self, x, y, 500 + idx)
                    iit.Refresh(pos)
                    iit.SetPos(x, y)
                    self.m_SelectItems[idx] = iit
                    self.m_InterfaceItem[pos].Select(True)
                    break
                    continue
            
            self.CheckValid()
            return seliit
        

    
    def DeleteEquip(self, idx):
        CEquipResetDlg.DeleteEquip(self, idx)
        self.CheckValid()

    
    def CheckValid(self):
        for pos in self.m_InterfaceItem:
            <tf = self.m_InterfaceItem[pos]
            curItem = <tf.GetItem()
            if self.GetValid(curItem):
                <tf.Enable(True)
                <tf.ShowShadow(False)
                continue
            
            <tf.Enable(False)
            <tf.ShowShadow(True)
        



def GetFunc(npcid):
    import world
    pobj = world.GetObj(npcid)
    name = getattr(pobj, 'm_PropName', '')
    title = getattr(pobj, 'm_PropTitle', '')
    if name == '\xa5P\xacy\xb9D\xa4H' or title == '\xa5l\xb3\xea\xc3~\xb7\xd2\xa7\xaf' or name == '\xa5l\xb3\xea\xc3~\xb3]\xb8m\xa4H':
        cls = CPetEquipResetDlg
    else:
        cls = CEquipResetDlg
    return cls


def Show(npcid):
    global g_EquipResetDlg
    cls = GetFunc(npcid)
    if cls == CPetEquipResetDlg:
        import dlgpetcenter
        if dlgpetcenter.IsTest():
            import dlgequipresetnew
            dlgequipresetnew.ShowPetEquipReset()
            return None
        
    
    g_EquipResetDlg = cls(npcid)
    import item
    item.AddShadowCallback('DlgEquipReset', interface.CShadowObject(g_EquipResetDlg), 'RefreshShadow')
