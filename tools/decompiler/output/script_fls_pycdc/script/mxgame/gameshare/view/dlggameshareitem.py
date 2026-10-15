# pycdc 交叉复核产物 · script.fls entry 2321
# co_filename(原始)='script/mxgame/gameshare/view/dlggameshareitem.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2321.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/4/10 19:59
\xd7\xf7\xd5\xdf: hzq
\xce\xc4\xbc\xfe: dlggameshareitem
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import C_sys
import combdialog
import combmacro
import dlgitem
import gamesharedefine
import hero
import interface
import item
import itemdefine
import itemmgr
import key
import misc
import slot
import pagedlgbase
import walker

class CGameShareItemDialog(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_SwitchBag = 'OnSwitch(iBagType)'
    MSG2BAGTYPE = {
        1: gamesharedefine.BAGTYPE_PUTON,
        2: gamesharedefine.BAGTYPE_BEIBAO,
        3: gamesharedefine.BAGTYPE_XINGNANG }
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/friend/share_item.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.m_oBagPart = CBagItemPart(self)
        self.m_oEquipPart = CEquipItemPart(self)
        self.m_DelegateList = []
        self.InitDelegate()
        self.GetObject('btn_equip').LeftUp()

    
    def SetBagType(self, iBagType):
        if iBagType == gamesharedefine.BAGTYPE_PUTON:
            self.m_oBagPart.SetShow(False)
            self.m_oEquipPart.SetShow(True)
        else:
            self.m_oBagPart.SetShow(True)
            self.m_oEquipPart.SetShow(False)
            self.m_oBagPart.SetBagType(iBagType)

    
    def InitDelegate(self):
        self.m_DelegateList = []
        import dgtgameshareitem
        self.m_DelegateList.append(dgtgameshareitem.CGameShareItemDelegate(self))

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)

    
    def VClose(self):
        self.SetShow(False)

    
    def OnEidtMessage(self, iMsgID):
        pass

    
    def OnMessage(self, iMsgID):
        self.OnEidtMessage(iMsgID)
        if iMsgID in self.MSG2BAGTYPE:
            self.ssEmit(self.SS_SwitchBag, self.MSG2BAGTYPE[iMsgID])
        



class CBagItemPart(combdialog.CCombSubWnd, itemmgr.CItemListBase):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/friend/share_item_bag.dlg')
        self.m_iBagType = None
        itemmgr.CItemListBase.__init__(self, 'list', 'img_itembg')

    
    def SetBagType(self, iBagType):
        self.m_iBagType = iBagType
        self.RefreshItemList()

    
    def GetMaxLine(self, iItemLine):
        return max(iItemLine, 6)

    
    def GetItems(self):
        if self.m_iBagType is None:
            return []
        
        if self.m_iBagType == gamesharedefine.BAGTYPE_PUTON:
            dTotalItems = item.GetItems()
            dItems = { }
            for iPos, oItem in dTotalItems.iteritems():
                if iPos <= iPos:
                    pass
                elif iPos <= itemdefine.EQUIP_ENDPOS:
                    dItems[iPos] = oItem
                    continue
            
        elif self.m_iBagType == gamesharedefine.BAGTYPE_XINGNANG:
            dTotalItems = item.GetItems()
            dItems = { }
            for iPos, oItem in dTotalItems.iteritems():
                if iPos <= iPos:
                    pass
                elif iPos < item.ITEM_SCOPE + 40:
                    dItems[iPos] = oItem
                    continue
            
        else:
            dTotalItems = item.GetItems()
            dItems = { }
            for iPos, oItem in dTotalItems.iteritems():
                if iPos <= iPos:
                    pass
                elif not iPos < item.ITEM_SCOPE:
                    if iPos <= iPos:
                        pass
                    elif iPos < item.ITEM_FIGHT_SCOPE:
                        dItems[iPos] = oItem
                        continue
            
        tItemList = dItems.items()
        tItemList.sort(key = (lambda tItem: tItem[0]))
        return tItemList

    
    def GetInterfaceItemClass(self):
        return CShareInterfaceItem



class CEquipItemPart(combdialog.CCombSubWnd):
    EQUIP_LOC = (('loc_cap', '\xb4U\xa4l'), ('loc_weapon', '\xaaZ\xbe\xb9'), ('loc_cloth', '\xf1Z\xa5\xd2'), ('loc_sash', '\xb8y\xb1a'), ('loc_cuff', '\xc5@\xb5\xc3'), ('loc_special', '\xaak\xc4_'), ('loc_necklace', '\xb6\xb5\xc3\xec'), ('loc_ring', '\xa7\xd9\xab\xfc'), ('loc_shoe', '\xbec\xa4l'))
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/friend/share_item_equip.dlg')
        self.m_InterfaceItems = [
            { },
            { }]
        self.m_oPlayerAni = None
        item.AddInterfaceCallback(self.m_InterfaceItems[0], 0, oRefObj = self)
        self.InitEquip()
        self.CreatePlayerAni()
        hero.AddRefreshCallback('CEquipItemPart', (('m_Desc', 0, 0), ('m_Shape', 0, 0)), self.CreatePlayerAni)

    
    def InitEquip(self):
        for i, v in enumerate(self.EQUIP_LOC):
            (sObjname, sTip) = v
            (iX, iY, iW, iH) = self.GetLocData(sObjname)
            iit = CEquipInterfaceItem(self, iX, iY, i + 1 + 100, self.m_InterfaceItems[0])
            iit.Refresh(i + 1)
            iit.SetTips(sTip, sTip + '#r\xa1\xd870\xaf\xc5\xaa\xba\xb8\xcb\xb3\xc6\xa1G \xa5i\xb3q\xb9L\xa7\xde\xaf\xe0-\xb8\xcb\xb3\xc6\xc1\xeb\xb3y\xac\xc9\xad\xb1\xbbs\xb3y\xa9\xce\xa6b\xb0\xd3\xb7|\xc1\xca\xb6R#r\xa1\xd670\xaf\xc5\xaa\xba\xb8\xcb\xb3\xc6\xa1G \xa5i\xa6b\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf\xc1\xca\xb6R\xb8\xcb\xb3\xc6\xb6i\xa6\xe6\xbbs\xb3y')
            combmacro.BindObject(sObjname, self, iit)
        

    
    def CreatePlayerAni(self):
        (x, y, w, h) = self.GetLocData('ani_Player')
        desc = self.GetPlayerDesc()
        import oldwalkerprocess
        if self.m_oPlayerAni:
            self.m_oPlayerAni.Release()
            self.m_oPlayerAni = None
        
        \xb8\x82\xb9\xb0pe = oldwalkerprocess.SpecialShape(hero.GetHeroID(), hero.GetProp('m_Shape', 111), desc)
        self.m_oPlayerAni = walker.CFakeRole(self, -1, \xb8\x82\xb9\xb0pe, desc)
        self.m_oPlayerAni.SetPos(x + w / 2, y + h - 30)
        self.m_oPlayerAni.SetDirection(3)
        self.m_oPlayerAni.SetZ(1000)
        self.m_oPlayerAni.SetButtonMessage(None)
        self.m_oPlayerAni.SetMouseMessage(None)

    
    def GetPlayerDesc(self):
        dCharDesc = misc.DeepCopy(hero.GetProp('m_Desc'))
        if 'horse' in dCharDesc:
            del dCharDesc['horse']
        
        if 'track' in dCharDesc:
            del dCharDesc['track']
        
        if 'fairy' in dCharDesc:
            dCharDesc['fairy'] = [
                dCharDesc['fairy'][0],
                [
                    0,
                    0]]
        
        if 'aura' in dCharDesc:
            del dCharDesc['aura']
        
        return dCharDesc

    
    def OnShapeChange(self):
        self.CreatePlayerAni()

    
    def __del__(self):
        item.ReleaseInterfaceCallback(self.m_InterfaceItems[0])



class CShareInterfaceItem(item.CInterfaceItem):
    
    def __init__(self, parent, x, y, msgid, interfaceitems = None):
        item.CInterfaceItem.__init__(self, parent, x, y, msgid, interfaceitems)
        self.m_oLeftCallObj = interface.CDoubleClickObject()
        self.m_oLeftCallObj.SetDoubleClickCB(self.OnDoubleClickCallBack)
        self.m_oLeftCallObj.SetSingleClickCB(self.OnClickedCallBack)

    
    def LeftUp(self):
        if C_sys.IsKeyDown(key.VK_SHIFT):
            self.Share()
        
        self.m_oLeftCallObj.LeftUp()

    
    def LeftDown(self):
        self.m_oLeftCallObj.LeftDown()

    
    def OnDoubleClickCallBack(self):
        self.Share()

    
    def OnClickedCallBack(self):
        pass

    
    def Share(self):
        oCurItem = self.GetItem()
        if oCurItem:
            dlgitem.OnCopyItemInfo(oCurItem)
        



class CEquipInterfaceItem(dlgitem.CEquipInterface):
    
    def __init__(self, parent, x, y, msgid, interfaceitems = None):
        dlgitem.CEquipInterface.__init__(self, parent, x, y, msgid, interfaceitems)
        self.m_oLeftCallObj = interface.CDoubleClickObject()
        self.m_oLeftCallObj.SetDoubleClickCB(self.OnDoubleClickCallBack)
        self.m_oLeftCallObj.SetSingleClickCB(self.OnClickedCallBack)

    
    def LeftUp(self):
        if C_sys.IsKeyDown(key.VK_SHIFT):
            self.Share()
        
        self.m_oLeftCallObj.LeftUp()

    
    def LeftDown(self):
        self.m_oLeftCallObj.LeftDown()

    
    def OnDoubleClickCallBack(self):
        self.Share()

    
    def OnClickedCallBack(self):
        pass

    
    def Share(self):
        oCurItem = self.GetItem()
        if oCurItem:
            dlgitem.OnCopyItemInfo(oCurItem)
