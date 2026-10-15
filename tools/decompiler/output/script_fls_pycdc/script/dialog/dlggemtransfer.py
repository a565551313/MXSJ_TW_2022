# pycdc 交叉复核产物 · script.fls entry 4492
# co_filename(原始)='script/dialog/dlggemtransfer.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4492.pyc (Python 2.5)

import interface
import combdialog
import itemmgr
g_GemTransferDlg = None

def ModuleReset():
    global g_GemTransferDlg
    g_GemTransferDlg = None


class CGemTransferDlg(combdialog.CCombDialog, itemmgr.CItemListBase):
    
    def __init__(self, makerID):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/gemtransfer.dlg')
        itemmgr.CItemListBase.__init__(self, 'list', 'area_items1')
        self.m_MakerID = makerID
        self.m_SelectItems = [
            None,
            None]
        interface.Center(self)
        self.InitTips()
        import netnpc
        netnpc.SetMakeCallback(self.TransferOver)

    
    def InitTips(self):
        import makeequipinterface
        obj = self.GetObject('img_servertips')
        iGemgrade = makeequipinterface.GetGemTransGrade()
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        self.m_LevelTips = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 10)
        self.m_LevelTips.SetPos(x, y)
        self.m_LevelTips.m_Info = '\xb7\xed\xabe\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa4U\xa1A\xc1\xeb\xb7\xd2\xb5\xa5\xaf\xc5\xa1\xd8%d\xaa\xba\xb8\xcb\xb3\xc6\xb6i\xa6\xe6\xc2\xe0\xb2\xbe\xab\xe1\xa1A\xb5\xa5\xaf\xc5\xa4\xa3\xb7|\xad\xb0\xa7C' % iGemgrade

    
    def OnEnter(self, msgid):
        if hasattr(self, 'm_LevelTips') and msgid == 10:
            import wrapinterface
            self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_LevelTips.m_Info, interface.FontLT14_3)
        

    
    def OnLeave(self, msgid):
        if hasattr(self, 'm_Tips') and msgid == 10:
            self.m_Tips = None
        

    
    def GetInterfaceItemClass(self):
        import dlgrepair
        return dlgrepair.CInterfaceItem

    
    def GetItems(self):
        import itemdata
        import item
        itemLst = []
        for pos, itemobj in item.g_Items[item.ITEM_NORMAL].items():
            if pos < 20:
                continue
            
            shape = itemobj.m_Shape
            if itemdata.IsType(shape, 'equip'):
                itemLst.append((pos, itemobj))
                continue
        
        return itemLst

    
    def CalCost(self):
        iCost = 0
        if self.m_SelectItems[0]:
            it1 = self.m_SelectItems[0].GetItem()
            it2 = self.m_SelectItems[1].GetItem()
            iLevel1 = int(self.GetEquipLv(it1))
            iLevel2 = int(self.GetEquipLv(it2))
            iLevel = None if iLevel1 == iLevel2 else 0
            level2Cost = {
                0: 0,
                10: 250,
                20: 500,
                30: 750,
                40: 1000,
                50: 1250,
                60: 1500,
                70: 1750,
                80: 2000,
                90: 2250,
                100: 2500,
                110: 2750,
                120: 3000,
                130: 3250 }
            iCost = level2Cost.get(iLevel, 3250)
        
        return iCost

    
    def UpdateCost(self, cost):
        import style
        if len(self.GetSelectItemsIDs()) == 2:
            import combmacro
            import hero
            self.m_TxtCost = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_Money', self, '%s' % cost, interface.FontLT14_3, interface.COLOR_5)
            (w, _) = self.m_TxtCost.GetSize()
            (cx, cy) = self.m_TxtCost.GetPos()
            self.m_TxtTotalMoney = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_Money', self, '/%d' % hero.g_Prop.m_ShenWuBi, interface.FontLT14_3, interface.COLOR_5)
            (mx, my) = self.m_TxtTotalMoney.GetPos()
            (_, offy) = style.GetIntTuple('dialog/gemtransfer.dlg', 'data_cost_offset')
            my -= offy
            self.m_TxtCost.SetPos(cx, cy - offy)
            self.m_TxtTotalMoney.SetPos(mx + w, my)
        else:
            self.m_TxtCost = None
            self.m_TxtTotalMoney = None

    
    def OnSelectItem(self):
        selectItemsIDs = self.GetSelectItemsIDs()
        if len(selectItemsIDs) != 2:
            return None
        
        cost = self.CalCost()
        self.UpdateCost(cost)

    
    def TransferOver(self, itype, amount, desc):
        self.m_SelectItems = [
            None,
            None]
        self.UpdateCost(None)
        self.CheckValid()

    
    def StartTransfer(self):
        selectItemsIDs = self.GetSelectItemsIDs()
        if len(selectItemsIDs) != 2:
            return None
        
        dctinfo = { }
        dctinfo['Num'] = 2
        dctinfo['Type'] = 1
        self.m_MakerID[dctinfo] = None
        dctinfo['i1'] = selectItemsIDs[0]
        dctinfo['i7'] = selectItemsIDs[1]
        dctinfo['Power'] = 0
        sub = 2
        import netcommon
        netcommon.C2SItemInfo(sub, dctinfo)

    
    def CreateBg(self, it):
        import style
        import combmacro
        it.m_Background = None
        igs = combmacro.CIMAGE(it, style.GetPath('combdialog/\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb8\xf1.igs'), interface.UIPath)
        igs.SetPos(1, 1)
        igs.SetAlpha(144)
        igs.SetZ(1000)
        it.m_Background = igs

    
    def DelBg(self, it):
        if hasattr(it, 'm_Background'):
            it.m_Background = None
        

    
    def GetEquipLv(self, it):
        if it and hasattr(it, 'm_Level'):
            return it.m_Level
        
        if not hasattr(it, 'm_InfoExt') or not hasattr(it, 'm_Shape'):
            return None
        
        import re
        patt = re.compile('\\|\xb5\xa5\xaf\xc5\\$(?P<lv>\\d+)')
        result = patt.search(it.m_InfoExt)
        equipLv = 0
        if result:
            equipLv = result.group('lv')
        else:
            import itemdata
            desc = itemdata.GetData(it.m_Shape)[1]
            patt = re.compile('#r\xa1i\xb5\xa5\xaf\xc5\xa1j(?P<lv>\\d+)')
            result2 = patt.search(desc)
            if result2:
                equipLv = result2.group('lv')
            
        return equipLv

    
    def GetEquipType(self, it):
        if not hasattr(it, 'm_Shape'):
            return None
        
        type2shape = {
            '\xaaZ\xbe\xb9': ((50000, 59999), (68001, 68041), (68501, 68505), 68513, 68361),
            '\xb4U\xa4l': ((60000, 60999),),
            '\xf1Z\xa5\xd2': ((61000, 61999),),
            '\xbec\xa4l': ((62000, 62999),),
            '\xc5@\xb5\xc3': ((63000, 63999),),
            '\xb6\xb5\xc3\xec': ((64000, 64999),),
            '\xa7\xd9\xab\xfc': ((65000, 65999),),
            '\xb8y\xb1a': ((66000, 66999),),
            '\xaak\xc4_': ((67000, 67999),) }
        findType = None
        equipShape = it.m_Shape
        for type, scopes in type2shape.iteritems():
            if equipShape in scopes:
                findType = type
                break
            
            for scope in scopes:
                
                try:
                    (start, end) = scope
                except:
                    continue

                if equipShape in xrange(start, end):
                    findType = type
                    break
                    continue
            
        
        if not findType:
            import re
            import itemdata
            desc = itemdata.GetData(it.m_Shape)[1]
            patt = re.compile('#r\xa1i\xc3\xfe\xab\xac\xa1j(?P<type>.{4})')
            result = patt.search(desc)
            if result:
                findType = result.group('type')
            
        
        return findType

    
    def GetEquipInfo(self, it):
        equipLv = self.GetEquipLv(it)
        equipType = self.GetEquipType(it)
        infoDct = { }
        infoDct['lv'] = equipLv
        infoDct['type'] = equipType
        return infoDct

    
    def IsEquipIdentify(self, it):
        import item
        return it.m_Key & item.MARK_JIANDING

    
    def CheckEquipInfoEqual(self, infoDct1, infoDct2):
        if infoDct1['type'] == infoDct2['type']:
            return True
        else:
            return False

    
    def CheckValid(self):
        selectItemsIDs = self.GetSelectItemsIDs()
        if len(selectItemsIDs) == 2:
            for iit in self.m_InterfaceItem.itervalues():
                iit.Enable(False)
                self.CreateBg(iit)
            
        elif len(selectItemsIDs) == 1:
            for seliit in self.m_SelectItems:
                if seliit:
                    it = seliit.GetItem()
                    continue
            
            selEquipInfo = self.GetEquipInfo(it)
            isNeedCompare = True
        elif len(selectItemsIDs) == 0:
            isNeedCompare = False
        
        for iit in self.m_InterfaceItem.itervalues():
            iit.Select(False)
            it = iit.GetItem()
            if it:
                if it.m_Shape in range(50000, 69999):
                    if it.m_ID in selectItemsIDs:
                        iit.Select(True)
                        index = selectItemsIDs.index(it.m_ID)
                        if self.m_SelectItems[index] and getattr(iit, 'm_Pos', None):
                            self.m_SelectItems[index].Refresh(iit.m_Pos)
                        
                    
                    if self.IsEquipIdentify(it):
                        if isNeedCompare:
                            tmpEquipInfo = self.GetEquipInfo(it)
                            if self.CheckEquipInfoEqual(tmpEquipInfo, selEquipInfo):
                                iit.Enable(True)
                                self.DelBg(iit)
                                continue
                            
                        else:
                            iit.Enable(True)
                            self.DelBg(iit)
                    
                
            
            iit.Enable(False)
            self.CreateBg(iit)
        

    
    def AddEquip(self, pos):
        import combmacro
        seliit = self.m_InterfaceItem[pos]
        if seliit and seliit.GetItem():
            selectItemsIDs = self.GetSelectItemsIDs()
            if seliit.GetItem().m_ID in selectItemsIDs:
                return None
            
            for idx in xrange(len(self.m_SelectItems)):
                if not self.m_SelectItems[idx]:
                    (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', 0, idx)
                    import item
                    iit = item.CInterfaceItem(self, x, y, 500 + idx)
                    iit.Refresh(pos)
                    (iw, ih) = iit.GetSize()
                    iit.SetPos(x + (w - iw) / 2, y + (h - ih) / 2)
                    self.m_SelectItems[idx] = iit
                    self.m_InterfaceItem[pos].Select(True)
                    break
                    continue
            
        

    
    def DeleteEquip(self, idx):
        iit = self.m_SelectItems[idx]
        self.m_SelectItems[idx] = None
        self.m_InterfaceItem[iit.m_Pos].Select(False)

    
    def GetSelectItemsIDs(self):
        selectItemsIDs = []
        for seliit in self.m_SelectItems:
            if seliit:
                selectItemsIDs.append(seliit.GetItem().m_ID)
                continue
        
        return selectItemsIDs

    
    def CloseWindow(self):
        global g_GemTransferDlg
        g_GemTransferDlg = None
        import item
        import netnpc
        item.ReleaseShadowCallback('DlgGemTransfer')
        netnpc.SetMakeCallback(None)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid <= msgid:
            pass
        elif msgid <= 300:
            self.AddEquip(msgid - 100)
            self.CheckValid()
            self.OnSelectItem()
        elif msgid in (500, 501):
            self.DeleteEquip(msgid - 500)
            self.UpdateCost(None)
            self.CheckValid()
        elif msgid == 3:
            self.StartTransfer()
        



def Show(isShow, makerID):
    global g_GemTransferDlg
    if g_GemTransferDlg:
        g_GemTransferDlg.CloseWindow()
    
    if isShow:
        g_GemTransferDlg = CGemTransferDlg(makerID)
        import item
        item.AddShadowCallback('DlgGemTransfer', interface.CShadowObject(g_GemTransferDlg), 'CheckValid')
