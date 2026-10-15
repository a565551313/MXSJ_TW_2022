# pycdc 交叉复核产物 · script.fls entry 2728
# co_filename(原始)='script/mxgame/makeequip/view/widget/ownequiplistwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2728.pyc (Python 2.5)

import builddefine
import comtree
import hero
import interface
import itemmgr
import misc
import style
import ui
import builddefine as define

class CItemListWidget(object):
    
    def __init__(self, sListObject, sBoxObject, msgid = 100):
        self.m_ItemMsgID = msgid
        self.m_ItemList = sListObject
        self.m_ItemBox = sBoxObject
        self.m_ItemData = None
        self.InitItemsCtrl()
        self.RefreshItemList()

    
    def InitItemsCtrl(self):
        self.m_ItemBox.SetShow(False)
        for \xcb\xce\xc9\xc2 in self.m_ItemList.m_Lines:
            \xcb\xce\xc9\xc2.SetShow(False)
        

    
    def ShowItemsCtrl(self, isshow):
        self.m_ItemList.SetShow(isshow)

    
    def GetInterfaceItemClass(self):
        import item
        return item.CInterfaceItem
        raise '\xc4~\xa9\xd3CItemListBase\xaa\xbaDlg\xa1A\xbb\xdd\xadn\xad\xab\xbcgCInterfaceItem\xaa\xba\xae\xf8\xae\xa7\xc5T\xc0\xb3\xa8\xe7\xbc\xc6\xa1A\xa6]\xac\xb0CInterfaceItem\xaa\xba\xa4\xf7\xc3\xfe\xacOCBGBox\xa1A\xa6\xd3\xa4\xa3\xacODlg'

    
    def GetItems(self):
        raise '\xc0\xf2\xa8\xfa\xc5\xe3\xa5\xdc\xa6b\xa6C\xaa\xed\xb8\xcc\xad\xb1\xaa\xbaItem\xabH\xae\xa7\xa1A\xbb\xdd\xadn\xa6UDlg\xa6\xdb\xa4v\xa9w\xb8q'

    
    def GetInterfaceItem(self):
        if getattr(self, 'm_InterfaceItem', None):
            return self.m_InterfaceItem
        
        self.m_InterfaceItem = { }
        return self.m_InterfaceItem

    
    def RefreshItemList(self):
        self.m_ItemData = self.GetItems()
        itemline = len(self.m_ItemData) / 5
        itemline = None if len(self.m_ItemData) % 5 else itemline
        itemline = max(itemline, 8)
        self.GetInterfaceItem()
        self.m_ItemList.Clear()
        for idx in xrange(itemline):
            self.AddItems(idx)
        

    
    def AddItems(self, idx):
        import ui
        path = self.m_ItemBox.m_FileName
        bg = itemmgr.CBGBox(self.m_ItemList, self.m_ItemList.m_ItemWidth, self.m_ItemList.m_ItemHeight, 0, 0)
        bg.m_ItemBG = []
        for i in xrange(5):
            img = ui.CImage(bg, path, interface.UIPath)
            (x, y) = self.m_ItemBox.m_Imagess[i].GetPos()
            img.SetPos(x, y)
            img.SetZ(1)
            bg.m_ItemBG.append(img)
        
        i = 0
        for pos, itemdata in self.m_ItemData[idx * 5:idx * 5 + 5]:
            (x, y) = bg.m_ItemBG[i].GetPos()
            i += 1
            iit = self.GetInterfaceItemClass()(bg, x, y, self.m_ItemMsgID + pos)
            iit.SetItem(itemdata)
            iit.SetZ(2)
            self.GetInterfaceItem()[pos] = iit
        
        self.m_ItemList.AddItem(bg)
        self.m_ItemList.ResetItems()
        self.m_ItemList.ResetScrollBar()
