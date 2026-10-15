# pycdc 交叉复核产物 · script.fls entry 406
# co_filename(原始)='script/dialog/dlgcombfire.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_406.pyc (Python 2.5)

import C_sys
import combdialog
import combmacro
import cursor
import handobj
import interface
import style
import ui
import world
import wrapinterface
COMB_COLOR = 14540253
BASE_WIDTH = 26
BASE_HEIGHT = 26
SPR_WAIT = 30
FRAME_LENS = 30
SPR_COLOREXT = {
    70420: 1,
    70433: 1,
    70432: 1,
    70428: 1,
    70426: 1,
    70423: 1,
    70422: 1 }
cursor.AddNotLoadCursor('dlgcombfire', 'g_CursorFireBlockList')
g_FireDlg = None
g_CursorFireBlockList = None
g_CursorFireBlockData = None
g_CursorFireBlockItemID = None
g_CheckCanPlayTimer = None

def ModuleReset():
    global g_FireDlg, g_CursorFireBlockList, g_CursorFireBlockData, g_CursorFireBlockItemID, g_CheckCanPlayTimer
    g_FireDlg = None
    g_CursorFireBlockList = None
    g_CursorFireBlockData = None
    g_CursorFireBlockItemID = None
    g_CheckCanPlayTimer = None


class CCursorCombFireBlock(interface.CMapImagesObject, interface.CBase):
    
    def __init__(self, parent, ipos, itype):
        import sprdata
        import firedata
        (uipath, filename) = sprdata.GetData(firedata.GetItemId(itype))
        interface.CMapImagesObject.__init__(self, parent, filename, uipath)
        self.m_Pos = ipos



def ReleaseCheckCanPlayTimer():
    global g_CheckCanPlayTimer
    if g_CheckCanPlayTimer:
        g_CheckCanPlayTimer.Release()
        g_CheckCanPlayTimer = None
    


def StartCheckCanPlayTimer():
    global g_CheckCanPlayTimer
    ReleaseCheckCanPlayTimer()
    import map
    import cursor
    
    def done(obj):
        (mx, my) = map.g_Map.GetPos()
        (cx, cy) = cursor.GetCursorPos()
        x = cx - mx
        y = cy - my
        if _CanPlace(x, y, g_CursorFireBlockData):
            alpha = 256
        else:
            alpha = 64
        if g_CursorFireBlockList:
            for obj in g_CursorFireBlockList:
                obj.SetAlpha(alpha)
            
            return ()
        

    g_CheckCanPlayTimer = interface.CBaseObject(None)
    g_CheckCanPlayTimer.CreatePyCommand(1, done)


def CreateCursorFireBlock(itemID, data):
    global g_CursorFireBlockList, g_CursorFireBlockData, g_CursorFireBlockItemID
    g_CursorFireBlockList = []
    g_CursorFireBlockData = data
    g_CursorFireBlockItemID = itemID
    import cursor
    for ipos, itype in data:
        rows = ipos % 13
        cols = ipos / 13
        (x1, y1) = TransPos(ipos)
        x1 = int(x1 + 0)
        y1 = int(y1 + 0)
        if itype != 0:
            obj = CCursorCombFireBlock(cursor.Cursor, ipos, itype)
            obj.SetPos(x1, y1)
            obj.SetZ(-1)
            g_CursorFireBlockList.append(obj)
            continue
    
    StartCheckCanPlayTimer()


def CanDoSelect():
    import map
    import cursor
    (mx, my) = map.g_Map.GetPos()
    (cx, cy) = cursor.GetCursorPos()
    x = cx - mx
    y = cy - my
    return _CanPlace(x, y, g_CursorFireBlockData)


def DoSelect():
    import map
    import cursor
    import nethero
    (mx, my) = map.g_Map.GetPos()
    (cx, cy) = cursor.GetCursorPos()
    x = cx - mx
    y = cy - my
    (x, y) = map.g_Map.ClientPos2ServerPos(x, y)
    nethero.C2SCombFirePlace(g_CursorFireBlockItemID, x, y)
    DoCancel()


def DoCancel():
    global g_CursorFireBlockList, g_CursorFireBlockData, g_CursorFireBlockItemID
    import key
    ReleaseCheckCanPlayTimer()
    key.RegisterRightButtonHotKey()
    key.RegisterLeftButtonHotKey()
    g_CursorFireBlockList = None
    g_CursorFireBlockData = None
    g_CursorFireBlockItemID = None


def GetSprColorExt(shape):
    data = SPR_COLOREXT.get(shape)
    if data == 1:
        return range(1, 6)
    elif data:
        return data
    else:
        return None


class _boxitem(ui.CCheckBox):
    s_AbleDraw = False
    
    def __init__(self, parent, combboxs, w, h, normal_color = -1, enter_color = -1, select_color = -1, msgid = 0, alpha = 256):
        ui.CCheckBox.__init__(self, parent, w, h, normal_color, enter_color, select_color, alpha, msgid)
        self.m_CombBoxs = combboxs
        combboxs.append(self)
        self.m_Index = -1
        self.m_SprItem = None
        self.m_Item = None
        self.m_ID = None
        self.m_SprID = None
        self.m_Type = -1
        self.m_SprType = -1
        self.m_CurColor = None
        self.m_SprColor = 0

    
    def ResetClear(cls):
        cls.s_AbleDraw = False

    ResetClear = classmethod(ResetClear)
    
    def IsAbleDraw(cls):
        return cls.s_AbleDraw

    IsAbleDraw = classmethod(IsAbleDraw)
    
    def SetAbleDraw(cls, itype):
        if not handobj.IsHand():
            return None
        
        cls.s_AbleDraw = itype

    SetAbleDraw = classmethod(SetAbleDraw)
    
    def Enter(self):
        if self.IsSelected1():
            return None
        
        if self.IsAbleDraw():
            if handobj.IsHand():
                self.OnHand(handobj.g_HandObj)
            
        
        ui.CCheckBox.Enter(self)
        oParent = self.GetParent()
        if hasattr(oParent, 'OnItemEnter'):
            oParent.OnItemEnter(self)
        

    
    def Leave(self):
        if self.IsSelected1():
            return None
        
        ui.CCheckBox.Leave(self)
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'OnItemLeave'):
            oParent.OnItemLeave(self)
        

    
    def LeftUp(self):
        ui.CCheckBox.LeftUp(self)
        import key
        if C_sys.IsKeyDown(key.VK_CTRL):
            return None
        
        if self.m_SelectColor == -1:
            return None
        
        if not self.m_Selected:
            for cb in self.m_CombBoxs:
                cb.Select(False)
            
            self.SetBg(self.m_SelectColor)
            self.m_Selected = True
        

    
    def HasItem(self):
        if not self.m_Item:
            pass
        return self.m_SprItem

    
    def SetItem(self, id, itemid):
        self.Select(True)
        
        try:
            self.m_Item = ui.CImage(self, 'item26\\%d.igs' % itemid, 'item')
            self.m_Item.SetZ(20)
            self.m_ID = id
        except:
            self.m_Item = None
            self.m_ID = None


    
    def SetColor(self, color):
        self.m_CurColor = color
        if self.m_IsPng and color == COMB_COLOR:
            color = self.m_EnterColor
        
        self.SetBg(color)

    
    def IsSelected1(self):
        return self.m_CurColor == COMB_COLOR

    
    def SetActive(self):
        parent = self.GetParent()
        if parent:
            if self.m_Item or self.m_SprItem:
                parent.m_Start.Active(True)
                parent.m_Start.SetText(str(self.m_Index))
                parent.m_Start.SetSelect(0, 999)
            else:
                parent.m_Start.Active(False)
                parent.m_Start.SetText('')
        

    
    def SetIndex(self):
        flag = False
        cts = self.GetParent().m_Start.GetText()
        
        try:
            idx = int(cts)
        except:
            idx = -1

        if idx in range(0, 170):
            self.m_Index = idx
            flag = True
        
        return flag

    
    def SetSprItem(self, id, color):
        self.Select(True)
        
        try:
            self.m_SprItem = ui.CImage(self, style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xd1\xcc\xbb\xa8\xd0\xa1\xcd\xbc\xb1\xea.igs'), 'interface')
            self.m_SprItem.SetZ(20)
            self.m_SprItem.SetPos(18, 16)
            self.m_SprID = id
            self.m_SprColor = color
        except:
            self.m_SprItem = None
            self.m_SprID = None
            self.m_SprColor = 0


    
    def Clear(self):
        self.GetParent().ClearBg(self.m_SprID, self.m_Pos)
        self.m_SprItem = None
        self.m_Item = None
        self.m_ID = None
        self.m_SprID = None
        self.m_Index = -1
        self.m_Type = -1
        self.m_SprType = -1
        self.m_SprColor = 0
        self.GetParent().MakeCts()

    
    def OnHand(self, hand):
        import handobj
        if getattr(hand, 'm_Type', None) == handobj.TYPE_DLGIMG:
            import firedata
            if not self.GetParent().CheckSpr(hand.m_ID, self.m_Pos):
                import usermacro
                usermacro.PROMPT_MSG('\xafS\xae\xc4\xa4\xa3\xaf\xe0\xb6\xa1\xb9j\xa4\xd3\xaa\xf1.')
                return None
            
            self.GetParent().ClearSelect(self.m_MsgID)
            arr = firedata.DATA.get(hand.m_ID)
            if arr:
                if not self.SetIndex():
                    import usermacro
                    usermacro.PROMPT_MSG('\xb0{\xc3{\xaa\xba\xad\xc8\xa5u\xaf\xe0\xa6b0-169\xaa\xba\xbdd\xb3\xf2\xa4\xba.')
                    return None
                
                if arr[1] in (0, 1):
                    self.SetItem(hand.m_ID, arr[2])
                    self.m_Type = arr[1]
                elif arr[1] == 2:
                    self.SetSprItem(hand.m_ID, hand.m_Color)
                    self.m_SprType = arr[1]
                
                self.GetParent().SetBg(hand.m_ID, self.m_Pos)
                self.GetParent().MakeCts()
            
        



class CLineupListBox(interface.CListBox):
    
    def OnSelect(self, sel):
        interface.CListBox.OnSelect(self, sel)
        self.GetParent().OnLineupChange(self.m_DataList[sel - 1][0])

    
    def Reset(self):
        self.SetText('')
        self.m_TextList = []
        self.m_DataList = []
        self.m_Selected = 0

    
    def AddTextItem(self, idx, name):
        self.m_TextList.append(name)
        if not hasattr(self, 'm_DataList'):
            self.m_DataList = []
        
        self.m_DataList.append((idx, ''))

    
    def OnMessage(self, msgid):
        if msgid == 1:
            tl = self.m_TextList
            if len(tl):
                (pw, ph) = self.GetSize()
                self.m_List = self.CMyList(self, 0, ph, pw, self.m_ItemHeightAmount, hspace = self.m_ItemSpace)
                self.m_List.Capture(1, 1)
                for i in xrange(len(self.m_TextList)):
                    (pw, ph) = self.m_List.GetSize()
                    item = interface.CTextCheckButton(self.m_List, self.m_TextList[i], 0, self.m_FontID, pw, self.m_ItemHeight, -1, 8424071, -1, msgid = i + 1)
                    self.m_List.AddItem(item)
                
                self.m_List.ResetScrollBar(False)
                self.m_List.Refresh(0)
            
        



class _startnumedit(wrapinterface.CNumberEdit):
    
    def MsgEnter(self):
        import handobj
        if handobj.g_HandObj is None:
            parent = self.GetParent()
            arr = parent.GetSelectList()
            if len(arr) > 0:
                for it in arr:
                    if not it.SetIndex():
                        import usermacro
                        usermacro.PROMPT_MSG('\xb0{\xc3{\xaa\xba\xad\xc8\xa5u\xaf\xe0\xa6b0-169\xaa\xba\xbdd\xb3\xf2\xa4\xba.')
                        return None
                        continue
                
                import usermacro
                usermacro.PROMPT_MSG('\xaa\xb1\xaea\xb3]\xb8m\xb8\xd3\xa7\xc7\xa6C\xac\xb0%d.' % it.m_Index)
            else:
                for it in parent.m_Items:
                    if it.IsSelected():
                        if it.m_Item is None and it.m_SprItem is None:
                            return None
                        
                        if not it.SetIndex():
                            import usermacro
                            usermacro.PROMPT_MSG('\xb0{\xc3{\xaa\xba\xad\xc8\xa5u\xaf\xe0\xa6b0-169\xaa\xba\xbdd\xb3\xf2\xa4\xba.')
                        else:
                            import usermacro
                            usermacro.PROMPT_MSG('\xaa\xb1\xaea\xb3]\xb8m\xb8\xd3\xa7\xc7\xa6C\xac\xb0%d.' % it.m_Index)
                        return None
                        continue
                
        

    
    def Enter(self):
        import wrapinterface
        txt = '\xa6b#G\xb0{\xc3{\xa7\xc7\xa6C\xae\xd8#n\xa4\xa4\xbf\xe9\xa4J\xbc\xc6\xa6r\xa8\xc3\xa6^\xa8\xae\xab\xe1\xa7Y\xa5i\xb3]\xb8m\xb9\xef\xc0\xb3\xbf\xef\xae\xd8\xa4\xa4\xaa\xba\xafS\xae\xc4#r\xb0{\xc3{\xb6\xb6\xa7\xc7\xa1A\xa7Y\xb7\xcf\xaa\xe1\xa7\xf7\xae\xc6\xaa\xba\xb0{\xc3{\xa9\xce\xbfU\xa9\xf1\xb6\xb6\xa7\xc7\xa1C\xa4]\xa5i\xa5H\xab\xf6Ctrl\xc1\xe4\xc2I#r\xbf\xef\xa7\xe5\xb6q\xb3]\xb8m\xa7\xc7\xa6C\xa1A\xb3]\xb8m\xb0{\xc3{\xa7\xc7\xa6C\xab\xe1\xa1A\xb3o\xa4@\xad\xec\xae\xc6\xa9\xce\xb3o\xa4@\xa7\xe5\xb6q\xad\xec\xae\xc6#r\xa6b\xba\xf4\xae\xe6\xa4\xa4\xb3]\xb8m\xac\xb0\xb8\xd3\xa7\xc7\xa6C\xa1A\xc2I\xc0\xbb\xa5k\xc1\xe4\xb0h\xa5X\xa7\xc7\xa6C\xb3]\xb8m\xa1C'
        self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
        self.m_Tips.SetOwner(self)
        self.Topmost()
        self.m_Tips.Topmost()

    
    def Leave(self):
        self.m_Tips = None



class CSpriteTips(wrapinterface.CTips):
    
    def __init__(self, parent, key, tcolor = 0, font = None, color = 2105376, alpha = 192, edge = 5, direct = 0, owner = None):
        if font == None:
            font = interface.FontLT14_3
        
        dn = {
            70420: (12, 40, 127),
            70422: (12, 63, 142),
            70423: (8, 42, 152),
            70426: (13, 52, 157),
            70428: (13, 37, 117),
            70432: (8, 25, 108),
            70433: (8, 66, 90) }
        import firedata
        shape = firedata.GetItemId(key, False)
        
        try:
            (frame, x, y) = dn[shape]
        except:
            shape = 70433
            (frame, x, y) = (8, 66, 90)

        wrapinterface.CTips.__init__(self, parent, edge * 2, 20, color, alpha, owner, direct)
        self.m_Icon = ui.CImage(self, 'fire/%d.igs' % shape, 'mapobject')
        self.m_Icon.SetFrame(frame)
        self.m_Icon.SetPos(x, y)
        (w, h) = self.m_Icon.GetSize()
        w = w + 4 + edge * 2
        h = h + edge * 2
        self.SetSize(w, h)
        self.m_Icon.SetShow(False)
        self.m_Spr = CCombFireSpr(self, 1, 0, key, tcolor)
        self.m_Spr.SetPos(x, y)
        self.m_Spr.SetFrame(12)
        self._drawedge(interface.COLOR_49)



class CMyTextCheckButton(interface.CTextCheckButton):
    
    def Enter(self):
        interface.CTextCheckButton.Enter(self)
        self.m_Tips = CSpriteTips(None, self.m_Key, self.m_Idx)
        (ox, oy) = self.GetScreenPos()
        (w, h) = self.m_Tips.GetSize()
        self.m_Tips.SetPos(ox - w, oy)
        self.m_Tips.Topmost()

    
    def Leave(self):
        interface.CTextCheckButton.Leave(self)
        self.m_Tips = None



class CSprListItem(interface.CClickBox, interface.CListBox):
    
    def __init__(self, parent, key, data1, msgid):
        interface.CClickBox.__init__(self, parent, 32, 32, color = 16711680, alpha = 0, msgid = msgid)
        self.m_Key = key
        self.m_ImageObj = ui.CImage(self, style.GetPath('combdialog\\\xb0\xb4\xc5\xa5\\\xc9\xab\xc5\xcc\xb0\xb4\xc5\xa5.igs'), interface.UIPath)
        self.m_ImageObj.SetPos(0, 0)
        self.m_ItemHeightAmount = 120
        self.m_FontID = interface.FontLT14_3
        self.m_ItemHeight = 20
        self.m_TextList = [
            '\xb5L']
        self.m_iTextAlign = None
        self.m_oListBoxChangeCB = None
        for i in data1:
            self.m_TextList += [
                str(i)]
        
        self.m_ItemSpace = 0
        self.m_ReadOnly = False
        self.m_Line = interface.CBoxObject(self, 2, interface.g_FontSize[interface.FontLT16_2], 0)
        self.m_Line.SetShow(False)
        self.m_Bg = interface.CBoxObject(self, 24, 24, 10066329, 128)
        self.m_Bg.SetPos(6, 6)
        self.m_Bg.SetShow(False)

    
    def Enter(self):
        return None
        self.m_Bg.SetShow(True)

    
    def Leave(self):
        self.m_Bg.SetShow(False)

    
    def Reset(self):
        pass

    
    def OnSelect(self, sel):
        interface.CListBox.OnSelect(self, sel)
        if sel > 10000:
            return None
        
        txt = self.m_Txt
        txt += [
            '',
            '\xa4@',
            '\xa4G',
            '\xa4T',
            '\xa5|',
            '\xa4\xad'][int(sel - 1)]
        self.GetParent().m_Color = sel - 1
        self.GetParent().SetText(txt)

    
    def OnListClose(self):
        self.m_List = None

    
    def AddText(self, txt):
        pass

    
    def RightUp(self):
        self.OnListClose()

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        (pw, ph) = self.GetSize()
        self.m_List = self.CMyList(self, 0, ph, pw, self.m_ItemHeightAmount, hspace = self.m_ItemSpace)
        self.m_List.Capture(1, 1)
        for i in xrange(len(self.m_TextList)):
            (pw, ph) = self.m_List.GetSize()
            item = CMyTextCheckButton(self.m_List, self.m_TextList[i], 0, self.m_FontID, pw, self.m_ItemHeight, -1, 255, -1, msgid = i + 1)
            item.m_Idx = i
            item.m_Key = self.m_Key
            self.m_List.AddItem(item)
        
        self.m_List.ResetScrollBar(False)
        self.m_List.Refresh(0)
        self.GetParent().Topmost()
        self.m_List.SetZ(20)

    
    def OnMessage(self, msgid):
        pass



class CCombFireDlg(combdialog.CCombDialog):
    
    class CDelClickText(interface.CClickText):
        
        def __init__(self, parent, x, y, ID):
            interface.CClickText.__init__(self, parent, x, y, '\xa7R\xb0\xa3', 4671303, interface.COLOR_30, interface.FontLT12_1, 0)
            self.m_ID = ID

        
        def LeftUp(self):
            interface.CClickText.LeftUp(self)
            
            def f1(dlg):
                import nethero
                nethero.C2SCombFireDelDIY(dlg.m_ID)

            import commondialog
            dlg = commondialog.ShowMessageBox('\xa7A\xbdT\xa9w\xa7R\xb0\xa3\xb8\xd3\xbc\xd2\xaaO\xbb\xf2\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (f1, None))
            dlg.m_ID = self.m_ID


    DEFAULT_TEMPLATE = [
        (1, '\xc2\xf9\xb3\xdf\xc1{\xaa\xf9'),
        (2, '\xac\xaf\xad\xb8\xbd\xc4\xa4\xd1'),
        (3, '\xb8`\xbcy\xa6N\xb2\xbb'),
        (4, '\xb7R\xb1\xa1\xa5\xc3\xbb\xb7')]
    
    def __init__(self, data):
        import combmacro
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/fire.dlg')
        interface.Center(self)
        self.m_ListTips = None
        self.m_DIYDict = { }
        
        def CreateListBox(dataList, objName, visibleCount, IsReadOnly):
            listObj = combmacro.CLISTBOX(interface.CListBox, objName, self, interface.COLOR_5, interface.FontLT14_3)
            listObj.SetItemProp(1, 16, 17 * visibleCount)
            listObj.SetReadOnly(IsReadOnly)
            for str in dataList:
                listObj.AddTextItem(str)
            
            return listObj

        self.m_Txt1 = [
            '\xa4@',
            '\xb7\xcf',
            '\xb9\xda',
            '\xa5\xcd',
            '\xc4@',
            '\xb7R',
            '\xa4\xdf',
            '\xa4\xcd',
            '\xa5P',
            '\xb7t',
            '\xb7\xb8',
            '\xb8`',
            '\xac\xaf',
            '\xc2\xf9']
        self.m_Txt2 = [
            '\xa4G',
            '\xaa\xe1',
            '\xb7Q',
            '\xa8\xb0',
            '\xa7A',
            '\xb1\xa1',
            '\xabQ',
            '\xbd\xcb',
            '\xabB',
            '\xa9]',
            '\xb1m',
            '\xbcy',
            '\xad\xb8',
            '\xb3\xdf']
        self.m_Txt3 = [
            '\xa4T',
            '\xc0\xe9',
            '\xa6\xa8',
            '\xa7\xd6',
            '\xa6n',
            '\xa5\xc3',
            '\xaa\xf8',
            '\xac\xdb',
            '\xa9_',
            '\xacy',
            '\xba\xd6',
            '\xa6N',
            '\xbd\xc4',
            '\xc1{']
        self.m_Txt4 = [
            '\xa5|',
            '\xc4\xea',
            '\xafu',
            '\xbc\xd6',
            '\xb9B',
            '\xbb\xb7',
            '\xc0H',
            '\xa6\xf1',
            '\xbdt',
            '\xacP',
            '\xa5\xfa',
            '\xb2\xbb',
            '\xa4\xd1',
            '\xaa\xf9']
        self.m_Name1 = CreateListBox(self.m_Txt1, 'm_name1', len(self.m_Txt1), True)
        self.m_Name1.OnSelect(1)
        self.m_Name2 = CreateListBox(self.m_Txt2, 'm_name2', len(self.m_Txt2), True)
        self.m_Name2.OnSelect(1)
        self.m_Name3 = CreateListBox(self.m_Txt3, 'm_name3', len(self.m_Txt3), True)
        self.m_Name3.OnSelect(1)
        self.m_Name4 = CreateListBox(self.m_Txt4, 'm_name4', len(self.m_Txt4), True)
        self.m_Name4.OnSelect(1)
        self.CreateCtrl()
        self.m_Bg = { }
        self.m_lbLineup.AddTextItem(0, '1')
        self.m_lbLineup.AddTextItem(1, '2')
        self.m_lbLineup.AddTextItem(2, '3')
        self.m_lbLineup.AddTextItem(3, '4')
        self.m_lbLineup.AddTextItem(4, '5')
        self.m_lbLineup.SetText('1')
        self.SetData(data)
        self.Draw()
        self.ShowList(11)
        self.m_Lines = []
        import hero
        hero.g_Name2PropItem['m_Cash'].AddRefreshCallbackWithID('combfirecash', self.MakeCts)
        hero.g_Name2PropItem['m_Gold'].AddRefreshCallbackWithID('combfiregold', self.MakeCts)
        self.m_TipsInfo = interface.CNotifyBox(self, 147, 20, alpha = 0, msgid = 30001)
        self.m_TipsInfo.SetPos(37, 475)
        self.m_TipsInfo.m_Info = '\xb6O\xa5\xce\xacO\xbbs\xa7@\xb2\xd5\xa6X\xb7\xcf\xaa\xe1\xa9\xd2\xae\xf8\xaf\xd3\xaa\xba\xb2{\xaa\xf7'

    
    def CreateCtrl(self):
        color = interface.COLOR_5
        self.m_Start = combmacro.CEDIT(_startnumedit, 'start', self, color, interface.FontLT14_3, color)
        self.m_Start.SetLimit(7)
        self.m_Start.SetText('')
        self.m_lbLineup = combmacro.CLISTBOX(CLineupListBox, 'cts', self, color, interface.FontLT14_3)
        self.m_lbLineup.SetItemProp(2, 16, 90)
        self.m_lbLineup.SetReadOnly(True)

    
    def CheckChange(self):
        defaultNameLst = ('\xa4@', '\xa4G', '\xa4T', '\xa5|')
        objNameLst = ('m_Name1', 'm_Name2', 'm_Name3', 'm_Name4')
        for idx, objName in enumerate(objNameLst):
            obj = getattr(self, objName)
            if defaultNameLst[idx] != obj.GetText():
                return True
                continue
        
        data = self.GetItemData()
        if len(data):
            return True
        
        return False

    
    def UpdateDIYTemplateList(self, \xacct):
        for idx, it in self.m_DIYDict.items():
            if idx in \xacct:
                \xacct[idx] = self.m_DIYDict[idx]
                continue
        
        self.m_DIYDict = \xacct
        if self.GetObject('b4').m_EnableFlag == False:
            self.ShowList(3)
        

    
    def UpdateDIYTemplateLen(self, ID, amount):
        import nethero
        if 'amount' not in self.m_DIYDict[ID]:
            self.m_DIYDict[ID]['amount'] = amount
            self.m_DIYDict[ID]['data'] = []
            s = 0
            while s < amount and s < 169:
                start = s
                end = min(s + 30, amount)
                nethero.C2SCombFireRequestDIYData(ID, start, end)
                s += 30
        

    
    def UpdateDIYTemplateData(self, ID, data):
        tplate = self.m_DIYDict[ID]['data']
        tplate.extend(data)
        if len(tplate) == self.m_DIYDict[ID]['amount']:
            self.m_DIYDict[ID]['template'] = self.m_DIYDict[ID]['data']
            self.ShowDIYTemplate(ID)
        

    
    def ShowDIYTemplate(self, ID):
        it = self.m_DIYDict[ID]
        name = it['name']
        self.m_Name1.SetText(name[0:2])
        self.m_Name2.SetText(name[2:4])
        self.m_Name3.SetText(name[4:6])
        self.m_Name4.SetText(name[6:8])
        tplate = self.m_DIYDict[ID].get('template')
        if not tplate:
            return None
        
        import firedata
        for it in self.m_Items:
            it.Clear()
        
        for t in tplate:
            (ipos, index, id1, id, color) = t
            it = self.m_Items[ipos]
            if id1:
                arr = firedata.DATA.get(id1)
                if arr:
                    it.SetItem(id1, arr[2])
                
                it.m_Type = arr[1]
            
            if id:
                arr = firedata.DATA.get(id)
                it.SetSprItem(id, color)
                it.m_SprType = arr[1]
                self.SetBg(id, ipos)
            
            it.m_Index = index
            it.Select(False)
        
        self.MakeCts()

    
    def SaveDIYTemplate(self):
        for idx in range(1, 6):
            if idx not in self.m_DIYDict:
                ID = idx
                break
                continue
        else:
            return None
        title = self.GetTitle()
        if title is None:
            return None
        
        import usermacro
        data = self.GetItemData()
        if not data:
            usermacro.PROMPT_MSG('\xabO\xa6s\xbc\xd2\xaaO\xa4\xa3\xaf\xe0\xac\xb0\xaa\xc5')
            return None
        
        if hasattr(self, 'm_LastFreshTime1') and self.m_LastFreshTime1 + 200000 > C_sys.GetTime():
            usermacro.PROMPT_MSG('\xabO\xa6s\xbc\xd2\xaaO20\xac\xed\xab\xe1\xa4~\xaf\xe0\xa6A\xabO\xa6s')
            return None
        
        self.m_LastFreshTime1 = C_sys.GetTime()
        import nethero
        nethero.C2SCombFireSaveDIY(ID, title, data)

    
    def OnEnter(self, msgid):
        import wrapinterface
        self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_TipsInfo.m_Info, interface.FontLT14_3, direct = 0)

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def MakeCts(self):
        cts = 0
        sg = 0
        for it in self.m_Items:
            if it.m_Type in range(2):
                cts += self.m_Price[it.m_Type]
            
            if it.m_SprType == 2:
                cts += self.m_Price[2]
                if it.m_SprColor > 0:
                    sg += 1
                
            
            if hasattr(it, 'm_SprColor') and it.m_SprColor > 0:
                cts += 16000
                continue
        
        num = self.m_lbLineup.GetText()
        num = int(num)
        money = cts * num + 20000
        sg = sg * num
        import hero
        self.m_NeedCash = money
        if money > hero.g_Prop.m_Cash:
            color = 16711680
        else:
            color = interface.COLOR_5
        import misc
        money = misc.ChangeMoney(str(money))
        self.m_CtsTxt = combmacro.CTEXT(interface.CTextObject, 'prices', self, money, interface.FontLT14_3, color)

    
    def CheckSpr(self, id, pos):
        import firedata
        arr = firedata.DATA.get(id)
        if arr and arr[1] == 2:
            bg = arr[6]
            br = pos / 13
            bc = pos % 13
            for i in range(bg * bg):
                rows = i / bg
                cols = i % bg
                if br + rows >= 13:
                    continue
                
                if bc + cols >= 13:
                    continue
                
                if self.m_Bg.get((br + rows) * 13 + bc + cols):
                    break
                    continue
            else:
                return True
        elif arr and arr[1] in (1, 0):
            return True
        
        return False

    
    def ClearBg(self, id, pos):
        import firedata
        arr = firedata.DATA.get(id)
        if arr and arr[1] == 2:
            bg = arr[6]
            br = pos / 13
            bc = pos % 13
            for i in range(bg * bg):
                rows = i / bg
                cols = i % bg
                if br + rows >= 13:
                    continue
                
                if bc + cols >= 13:
                    continue
                
                newpos = (br + rows) * 13 + bc + cols
                if len(self.m_Items) > newpos:
                    
                    try:
                        del self.m_Bg[newpos]

                    continue
            
        

    
    def SetBg(self, id, pos):
        import firedata
        arr = firedata.DATA.get(id)
        if arr and arr[1] == 2:
            bg = arr[6]
            br = pos / 13
            bc = pos % 13
            for i in range(bg * bg):
                rows = i / bg
                cols = i % bg
                if br + rows >= 13:
                    continue
                
                if bc + cols >= 13:
                    continue
                
                newpos = (br + rows) * 13 + bc + cols
                if len(self.m_Items) > newpos:
                    (x, y) = self.m_Items[newpos].GetPos()
                    obj = interface.CBoxObject(self, 26, 26, 7687495, 256)
                    obj.SetPos(x, y)
                    self.m_Bg[newpos] = obj
                    continue
            
        

    
    def OnLineupChange(self, idx):
        self.MakeCts()

    
    def SetData(self, data):
        self.m_Price = [
            0,
            0,
            0]
        self.m_Data = [
            [],
            [],
            []]
        for itype, price, arr in data:
            self.m_Price[itype] = price
            for i in arr:
                self.m_Data[itype].append(i)
            
        

    
    def Draw(self):
        import listdata
        self.m_Items = []
        (x, y) = self.GetObject('box').GetPos()
        if interface.IsStyle4():
            xx = yy = 5
        else:
            xx = yy = 4
        w = h = 26
        dInfo = listdata.GetListInfo(listdata.DEFAULT_TYPE)
        sItNormalPath = dInfo['sItNormalPath']
        sItEnterPath = dInfo['sItEnterPath']
        sItSelectPath = dInfo['sItSelectPath']
        for i in range(169):
            it = _boxitem(self, self.m_Items, w, h, sItNormalPath, sItEnterPath, sItSelectPath, msgid = i + 1000)
            cols = i % 13
            rows = i / 13
            it.m_Pos = i
            it.SetPos(x + cols * (w + 1) + xx, y + rows * (w + 1) + yy)
        

    
    def OnItemEnter(self, it):
        msgid = it.m_MsgID
        import firedata
        if msgid <= msgid:
            pass
        elif msgid < 2000:
            txt = ''
            arr = firedata.DATA.get(it.m_ID)
            if arr:
                txt += '%-24s#r' % arr[0]
            
            arr = firedata.DATA.get(it.m_SprID)
            if arr:
                txt += '\xafS\xae\xc4:%s' % arr[0]
                txt += [
                    '',
                    '\xa4@',
                    '\xa4G',
                    '\xa4T',
                    '\xa5|',
                    '\xa4\xad'][int(it.m_SprColor)]
                txt += '#r'
            
            if txt:
                txt += '\xa7\xc7\xa6C:%d' % it.m_Index
                it.Topmost()
                self.m_ListTips = wrapinterface.CTextTips(it, -1, txt, interface.FontLT14_3, direct = 1)
                self.m_ListTips.Topmost()
                self.m_ListTips.SetOwner(it)
                if it.m_ID:
                    self.m_ListTips.m_Img = ui.CImage(self.m_ListTips, 'item26\\%d.igs' % firedata.GetItemId(it.m_ID), 'item')
                    self.m_ListTips.m_Img.SetZ(20)
                    self.m_ListTips.m_Img.SetPos(140, 4)
                
            
        elif msgid <= msgid:
            pass
        elif msgid < 100:
            listobj = self.GetObject('list')
            if len(listobj.m_Items) >= msgid - 1:
                it = listobj.m_Items[msgid - 1]
                if it and it.m_Type == 3:
                    self.m_ListTips = wrapinterface.CTextTips(self, -1, '#G\xc2\xf9\xc0\xbb#n\xb8\xd3\xbc\xd2\xaaO\xa6W\xba\xd9\xa1A\xb1N\xb7|\xa6b\xba\xf4\xae\xe6\xa4\xa4\xc5\xe3\xa5\xdc\xbc\xd2\xaaO\xa4\xba\xaee\xa1A#r\xa8\xc3\xb7|#G\xc2\xd0\xbb\\#n\xb7\xed\xabe\xba\xf4\xae\xe6\xa9\xd2\xa6\xb3\xaa\xab\xab~\xa1A\xa8\xcf\xa5\xce\xbc\xd2\xaaO\xab\xe1\xa1A\xa5i#r\xa5H\xa6b\xbc\xd2\xaaO\xb0\xf2\xc2\xa6\xa4W\xc4~\xc4\xf2\xbds\xbf\xe8\xa9M\xbbs\xa7@\xb2\xd5\xa6X\xb7\xcf\xaa\xe1', interface.FontLT14_3, direct = 1)
                    self.m_ListTips.SetOwner(it)
                elif it and it.m_Color > 0:
                    self.m_ListTips = wrapinterface.CTextTips(self, -1, '\xc1\xca\xb6R\xa6\xb9\xafS\xae\xc4\xbb\xdd\xaa\xe1\xb6O#R20000#n', interface.FontLT14_3, direct = 1)
                    self.m_ListTips.SetOwner(it)
                
            
        

    
    def OnItemLeave(self, it):
        self.m_ListTips = None

    
    def ShowList(self, msgid):
        if msgid not in (11, 12, 13, 3):
            return None
        
        self.GetObject('b1').Enable(msgid != 11)
        self.GetObject('b2').Enable(msgid != 12)
        self.GetObject('b3').Enable(msgid != 13)
        self.GetObject('b4').Enable(msgid != 3)
        listobj = self.GetObject('list')
        listobj.Clear()
        import firedata
        import sprdata
        if msgid == 3:
            for idx, iname in self.DEFAULT_TEMPLATE:
                item = listobj.AddTextItem(iname)
                item.m_ID = idx
                item.m_Name = iname
                item.m_Type = 3
                item.m_DIY = False
            
            lst = self.m_DIYDict.values()
            lst.sort(key = (lambda x: x['time']))
            (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_lsit_pos')
            for it in lst:
                item = listobj.AddTextItem(it['name'])
                item.m_ID = it['ID']
                item.m_DelBtn = self.CDelClickText(item, x, y, it['ID'])
                item.m_Name = it['name']
                item.m_Type = 3
                item.m_DIY = True
            
        else:
            for key in self.m_Data[msgid - 11]:
                (name, mtype, itemid, hx, hy, frames, bg) = firedata.GetData(key)
                item = listobj.AddTextItem(name)
                arr = GetSprColorExt(itemid)
                if arr:
                    item.m_Bn = CSprListItem(item, key, arr, 3000 + key)
                    item.m_Bn.SetPos(100, 1)
                    item.m_Bn.m_Txt = name
                
                item.SetZ(20)
                item.m_Color = 0
                item.m_Type = mtype
                item.m_UiPath = sprdata.GetData(itemid)[0]
                item.m_IPath = sprdata.GetData(itemid)[1]
                item.m_ID = key
                item.m_Bg = bg
                item.m_ItemID = itemid
            
        listobj.ResetItems()
        listobj.ResetScrollBar()

    
    def SelItem(self, msgid):
        if msgid <= msgid:
            pass
        elif msgid < 2000:
            it = self.m_Items[msgid - 1000]
            if it:
                selID = it.m_ID
                if selID in (-1, None):
                    return None
                
                self.m_Start.Active(True)
                self.m_Start.SetSelect(0, 999)
                for itemObj in self.m_Items:
                    if itemObj.m_ID == selID:
                        itemObj.SetColor(COMB_COLOR)
                        continue
                
            
        

    
    def ClearSelect(self, msgid):
        for it1 in self.m_Items:
            if it1.m_MsgID != msgid:
                it1.SetColor(it1.m_NormalColor)
                continue
        

    
    def Put(self):
        for cb in self.m_Items:
            cb.Select(False)
        

    
    def MakeIndex(self):
        import misc
        n = misc.RandInt(0, 5)
        if n == 0:
            idx = 1
            for it in self.m_Items:
                if it.HasItem():
                    it.m_Index = idx
                    idx += 1
                    continue
            
        elif n == 1:
            for it in self.m_Items:
                if it.HasItem():
                    it.m_Index = misc.RandInt(1, 4)
                    continue
            
        elif n == 2:
            arr = []
            for it in self.m_Items:
                if it.HasItem():
                    arr.append(it)
                    continue
            
            arr1 = range(1, len(arr) + 1)
            for it in arr:
                idx = misc.RandInt(0, len(arr1) - 1)
                it.m_Index = arr1[idx]
                arr1.pop(idx)
            
        elif n == 3:
            arr = []
            for it in self.m_Items:
                if it.HasItem():
                    rows = it.m_Pos / 13
                    cols = it.m_Pos % 13
                    it.m_Index = rows + 1
                    continue
            
        elif n == 4:
            arr = []
            for it in self.m_Items:
                if it.HasItem():
                    rows = it.m_Pos / 13
                    cols = it.m_Pos % 13
                    it.m_Index = cols + 1
                    continue
            
        elif n == 5:
            arr = []
            for it in self.m_Items:
                if it.HasItem():
                    rows = it.m_Pos / 13
                    cols = it.m_Pos % 13
                    it.m_Index = max(rows - 6, 6 - rows, cols - 6, 6 - cols) + 1
                    continue
            
        
        import usermacro
        usermacro.PROMPT_MSG('\xa7A\xaa\xba\xb2\xd5\xa6X\xb7\xcf\xaa\xe1\xbfU\xa9\xf1\xa7\xc7\xa6C\xa4w\xc0H\xbe\xf7\xa5\xcd\xa6\xa8.')

    
    def GetSelectList(self):
        arr = []
        for it in self.m_Items:
            if it.IsSelected1():
                arr.append(it)
                continue
        
        return arr

    
    def GetTitle(self):
        import usermacro
        import banword
        title = self.m_Name1.GetText() + self.m_Name2.GetText() + self.m_Name3.GetText() + self.m_Name4.GetText()
        title = title.replace(' ', '')
        if len(title) == 0:
            usermacro.PROMPT_MSG('\xde\xa6\xc3\x88\xc0;\xcf>\xcd\xca\xc6\xe0\xac\xb0\xaa\xc5\xa1I')
            return None
        
        if len(title) > 8:
            usermacro.PROMPT_MSG('\xb2\xd5\xa6X\xb7\xcf\xaa\xe1\xa6W\xa4\xa3\xaf\xe0\xa4j\xa9\xf34\xad\xd3\xa6r\xa9\xce8\xad\xd3\xad^\xa4\xe5\xa6r\xb2\xc5\xa1I')
            return None
        
        if not banword.IsValidChat(title)[0]:
            usermacro.PROMPT_MSG('\xb7\xcf\xaa\xe1\xa9R\xa6W\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby\xa1I')
            return None
        
        return title

    
    def GetItemData(self):
        data = []
        for it in self.m_Items:
            id1 = 0
            id = 0
            color = 0
            if it.m_SprType == 2:
                
                try:
                    id = int(it.m_SprID)
                    color = int(it.m_SprColor)

            
            if it.m_Type in range(2):
                
                try:
                    id1 = int(it.m_ID)

            
            if id > 0 or id1 > 0:
                data.append([
                    it.m_Pos,
                    it.m_Index,
                    id1,
                    id,
                    color])
                continue
        
        return data

    
    def DoubleClick(self, msgid):
        flag = False
        t = C_sys.GetTime()
        if hasattr(self, 'm_LeftUpTime') and hasattr(self, 'm_LeftUpMsgID'):
            if t - self.m_LeftUpTime < 5000 and self.m_LeftUpMsgID == msgid:
                flag = True
            
        
        self.m_LeftUpTime = t
        self.m_LeftUpMsgID = msgid
        return flag

    
    def SelTemplate(self, msgid):
        it = self.GetObject('list').m_Items[msgid - 101]
        if it:
            import handobj
            selID = it.m_ID
            if it.m_Type == 3:
                if it.m_DIY == True:
                    it = self.m_DIYDict[selID]
                    self.ShowDIYTemplate(selID)
                    import nethero
                    if it.get('request') is None:
                        nethero.C2SCombFireRequestDIYDataLen(selID)
                        it['request'] = True
                    
                else:
                    InPut(selID)
                    defTemplate = self.DEFAULT_TEMPLATE
                    self.m_Name1.SetText(defTemplate[selID - 1][1][0:2])
                    self.m_Name2.SetText(defTemplate[selID - 1][1][2:4])
                    self.m_Name3.SetText(defTemplate[selID - 1][1][4:6])
                    self.m_Name4.SetText(defTemplate[selID - 1][1][6:8])
            
        

    
    def DoBuy(self):
        title = self.GetTitle()
        if title is None:
            return None
        
        import usermacro
        num = self.m_lbLineup.GetText()
        num = int(num)
        data = self.GetItemData()
        money = self.m_NeedCash
        if len(data) == 0:
            usermacro.PROMPT_MSG('\xa7A\xa8S\xa9\xf1\xa5\xf4\xa6\xf3\xaaF\xa6\xe8\xa1I')
            return False
        
        import hero
        if money > hero.g_Prop.m_Cash:
            usermacro.PROMPT_MSG('\xa7A\xaa\xba\xaa\xf7\xbf\xfa\xa4\xa3\xa8\xac\xa5H\xc1\xca\xb6R\xb2\xd5\xa6X\xb7\xcf\xaa\xe1')
            return False
        
        
        def DoMake(dlg):
            import nethero
            nethero.C2SCombFireBuy(dlg.title, dlg.num, dlg.data)
            dlg.m_Start.Active(False)
            CCombFireDlg.CloseWindow()

        import commondialog
        dlg = commondialog.ShowMessageBox('\xa7A\xbdT\xa9w\xaa\xe1\xb6O#R%s#n\xb2{\xaa\xf7\xc1\xca\xb6R\xb7\xed\xabe\xaa\xba\xb2\xd5\xa6X\xb7\xcf\xaa\xe1\xb6\xdc\xa1H' % money, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (DoMake, None))
        dlg.title = title
        dlg.num = num
        dlg.data = data
        dlg.m_Start = self.m_Start

    
    def CloseWindow(cls):
        global g_FireDlg
        import hero
        hero.g_Name2PropItem['m_Gold'].RemoveRefreshCallbackWithID('combfiregold')
        hero.g_Name2PropItem['m_Cash'].RemoveRefreshCallbackWithID('combfirecash')
        g_FireDlg = None

    CloseWindow = classmethod(CloseWindow)
    
    def DoClose(self):
        
        def RealClose(dlg):
            if dlg:
                dlg.m_Start.Active(False)
            
            CCombFireDlg.CloseWindow()

        if self.CheckChange():
            import commondialog
            dlg = commondialog.ShowMessageBox('\xa7A\xbdT\xa9w\xb0h\xa5X\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (RealClose, None))
            dlg.m_Start = self.m_Start
        else:
            RealClose(None)
            self.m_Start.Active(False)

    
    def RegisterMouseBtn(self):
        import key
        
        def onleftup():
            _boxitem.SetAbleDraw(False)
            (x, y) = cursor.GetCursorPos()
            objlist = C_sys.GetObjects(x, y)
            if objlist and isinstance(objlist[0], _boxitem):
                objlist[0].OnHand(handobj.g_HandObj)
            

        
        def onleftdown():
            objlist = []
            (x, y) = cursor.GetCursorPos()
            objlist = C_sys.GetObjects(x, y)
            if objlist and isinstance(objlist[0], _boxitem):
                _boxitem.SetAbleDraw(True)
                objlist[0].OnHand(handobj.g_HandObj)
            

        
        def onrightdown():
            handobj.Clear()
            key.RegisterLeftButtonHotKey()

        C_sys.RegisterHotKey(key.LEFT_BUTTON_DOWN, onleftdown)
        C_sys.RegisterHotKey(key.LEFT_BUTTON_UP, onleftup)
        C_sys.RegisterHotKey(key.RIGHT_BUTTON_DOWN, onrightdown)

    
    def DoClear(self):
        
        def _clearAll(dlg):
            obj = dlg.m_Obj.Get()
            if not obj:
                return None
            
            for it in obj.m_Items:
                it.Clear()
            
            self.MakeCts()

        
        def _clearSelected(dlg):
            obj = dlg.m_Obj.Get()
            if not obj:
                return None
            
            for it in obj.m_Items:
                if it.IsSelected1():
                    it.Clear()
                    continue
            
            self.MakeCts()

        selectedItems = self.GetSelectList()
        if len(selectedItems) > 0:
            msg = '\xbdT\xa9w\xb2M\xb0\xa3\xbf\xef\xa4\xa4\xaa\xba\xaa\xab\xab~\xb6\xdc\xa1H'
            func = _clearSelected
        else:
            msg = '\xbdT\xa9w\xb2M\xb0\xa3\xa9\xd2\xa6\xb3\xaa\xba\xaa\xab\xab~\xb6\xdc\xa1H'
            func = _clearAll
        import commondialog
        dlg = commondialog.ShowMessageBox(msg, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (func, None))
        dlg.m_Obj = interface.CShadowObject(self)

    
    def DoSave(self):
        import usermacro
        import commondialog
        if len(self.m_DIYDict) >= 5:
            usermacro.PROMPT_MSG('\xb3\xcc\xa6h\xa5u\xaf\xe0\xc3B\xa5~\xabO\xa6s5\xad\xd3\xbc\xd2\xaaO')
            return None
        
        title = self.GetTitle()
        if title is None:
            return None
        
        
        def done(dlg):
            obj = dlg.m_Dlg.Get()
            if obj is None:
                return None
            
            obj.SaveDIYTemplate()

        dlg = commondialog.ShowMessageBox('\xa7A\xbdT\xa9w\xadn\xabO\xa6s\xb8\xd3\xbc\xd2\xaaO\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (done, None))
        dlg.m_Dlg = interface.CShadowObject(self)

    
    def SetOnHand(self, it):
        if it.m_Type == 3:
            return None
        
        if it.m_Type == 2:
            handobj.HandDlgImg(it.m_ID, 'interface', style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xb1\xde\xc5\xda26.igs'), self.Put)
            handobj.g_HandObj.m_Color = it.m_Color
        else:
            handobj.HandDlgImg(it.m_ID, 'item', 'item26\\%d.igs' % it.m_ItemID, self.Put)
        self.RegisterMouseBtn()
        self.m_Start.Active(True)
        self.m_Start.SetText('0')

    
    def SetColor(self, msgid):
        for it in self.m_Items:
            if it.m_Selected:
                it.Select(False)
                it.SetColor(COMB_COLOR)
            
            if it.IsSelected1():
                if not it.m_ID:
                    pass
                if not (it.m_SprID):
                    it.SetColor(it.m_NormalColor)
                    continue
        
        it = it = self.m_Items[msgid - 1000]
        if it.m_ID or it.m_SprID:
            arr = self.GetSelectList()
            if it.IsSelected1():
                it.SetColor(it.m_NormalColor)
            else:
                it.SetColor(COMB_COLOR)
        
        self.m_Start.Active(True)
        self.m_Start.SetSelect(0, 999)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.DoClose()
        elif msgid == 6:
            self.DoClear()
        elif msgid == 7:
            self.DoBuy()
        elif msgid == 8:
            self.MakeIndex()
        elif msgid in (11, 12, 13, 3):
            if not hasattr(self, 'm_RequestDIYList'):
                self.m_RequestDIYList = True
                import nethero
                nethero.C2SCombFireRequestDIYList()
            
            self.ShowList(msgid)
        elif msgid == 21:
            self.DoSave()
        elif msgid <= msgid:
            pass
        elif msgid < 2000 + interface.RIGHT_BUTTON_MESSAGE:
            self.ClearSelect(msgid - interface.RIGHT_BUTTON_MESSAGE)
            it = self.m_Items[msgid - 1000 - interface.RIGHT_BUTTON_MESSAGE]
            if it:
                it.Clear()
            
        elif msgid <= msgid:
            pass
        elif msgid < 2000:
            if self.DoubleClick(msgid):
                self.SelItem(msgid)
                return None
            
            import key
            if C_sys.IsKeyDown(key.VK_CTRL):
                self.SetColor(msgid)
                return None
            
            self.ClearSelect(msgid)
            it = self.m_Items[msgid - 1000]
            if it:
                it.SetActive()
            
        elif msgid <= msgid:
            pass
        elif msgid < 1000:
            if self.DoubleClick(msgid):
                self.SelTemplate(msgid)
                return None
            
            listobj = self.GetObject('list')
            it = listobj.m_Items[msgid - 101]
            if it:
                self.SetOnHand(it)
            
        



class CCombFire(interface.CMapImagesObject, world.CObject):
    
    def __init__(self, parent, tid, fname, x, y):
        interface.CMapImagesObject.__init__(self, parent, 'furniture/space.igs', 'mapobject')
        world.CObject.__init__(self, tid)
        self.SetPos(x, y)
        self.SetMouseMessage(None)
        self.SetButtonMessage(None)
        self.m_Data = None
        self.m_Start = 0
        self.m_Brother = []
        self.m_Sprs = []
        self.m_Lights = { }
        self.m_Sprs = []
        self.m_CurTime = None
        self.m_Parent = interface.CShadowObject(parent)

    
    def SetName(self, name, color, top = False):
        self.m_NameText = name

    
    def Play(self, start, stop = True):
        self.m_CurTime = start
        
        def _Play(par, start, stop):
            for obj in par.m_Brother:
                obj.SetLight(8)
                obj.SetAlpha(256)
            
            keys = par.m_Lights.keys()
            cts = len(keys)
            if cts == 0:
                return None
            
            cur = par.m_Lights.keys()[start % cts]
            for obj in par.m_Lights[cur]:
                obj.SetLight(16)
                obj.SetAlpha(256)
            
            if start <= start:
                pass
            elif start <= 180 or not stop:
                return (start + 1, stop)
            
            Clear(par.m_ID)

        self.CreatePyCommand(FRAME_LENS, _Play, start, stop)
        
        def _Play1(par, start, stop):
            if start / FRAME_LENS >= 181 and stop:
                for obj in par.m_Sprs:
                    obj.SetShow(False)
                
                return None
            
            for obj in par.m_Sprs:
                curframe = (start + obj.m_CurFrame * FRAME_LENS) % (obj.m_Cts + SPR_WAIT)
                if curframe < obj.m_Cts:
                    obj.SetShow(True)
                    for frame, ct in obj.m_Data:
                        if curframe > ct:
                            curframe -= ct
                            continue
                        
                        obj.SetFrame(frame)
                    
                obj.SetShow(False)
            
            return (start + 1, stop)

        self.CreatePyCommand(1, _Play1, start * FRAME_LENS, stop)

    
    def DrawByData(self, shape):
        if shape in (2015, 2016, 2017, 2018):
            data = ReadData(shape)
            self.Draw(data, 2)
        else:
            return None

    
    def Draw(self, data, flag = 1):
        self.m_Data = data
        self.m_Brother = []
        self.m_Sprs = []
        parent = self.m_Parent.Get()
        if parent is None:
            return None
        
        (x, y) = self.GetPos()
        t = 45
        dn1 = { }
        for ipos, frame, itype, itype1, icolor in data:
            dn1[frame] = 1
            rows = ipos % 13
            cols = ipos / 13
            (x1, y1) = TransPos(ipos, flag)
            x1 = int(x1 + x)
            y1 = int(y1 + y)
            if itype != 0:
                
                try:
                    obj = CCombFireBlock(parent, ipos, itype)
                    obj.SetParent(self)
                    obj.SetPos(x1, y1)
                    obj.SetZ(ipos)
                    self.m_Brother.append(obj)
                    if frame > 0:
                        self.m_Lights.setdefault(frame, [])
                        self.m_Lights[frame].append(obj)
                (ipos, itype)

            
            if itype1 != 0:
                
                try:
                    obj1 = CCombFireSpr(parent, ipos, frame, itype1, icolor)
                    obj1.SetPos(x1, y1)
                    (w, h) = parent.GetSize()
                    obj1.SetZ(h - y)
                    self.m_Sprs.append(obj1)
                (ipos, itype)

                continue
        
        dn = { }
        arr = dn1.keys()
        idx = 0
        arr.sort()
        for i in arr:
            dn[i] = idx
            idx += 1
        
        for obj in self.m_Sprs:
            
            try:
                obj.m_CurFrame = dn[obj.m_KeyFrame1]
            continue
            continue

        

    
    def Enter(self):
        pass

    
    def Leave(self):
        pass



class CCombFireSpr(interface.CWalkerObject):
    
    def __init__(self, parent, ipos, frame, itype, color = 0):
        import sprdata
        import firedata
        (uipath, filename) = sprdata.GetData1(firedata.GetItemId(itype, False))
        interface.CWalkerObject.__init__(self, parent)
        self.LoadPalProject('fire\\%d.pro' % firedata.GetItemId(itype, False), 'mapobject')
        self.Load(filename, uipath)
        self.m_Cts = GetMovLen(filename, uipath)
        self.m_Data = GetMovData(filename, uipath)
        self.m_Pos = ipos
        self.m_KeyFrame1 = frame
        self.m_CurFrame = 0
        self.SetColor(color)

    
    def CSetDirection(self, d):
        pass

    
    def SetColor(self, idx):
        self.SetPalProject(idx)



class CCombFireBlock(interface.CMapImagesObject, interface.CBase):
    
    def __init__(self, parent, ipos, itype):
        import sprdata
        import firedata
        (uipath, filename) = sprdata.GetData(firedata.GetItemId(itype))
        interface.CMapImagesObject.__init__(self, parent, filename, uipath)
        self.m_Pos = ipos
        self.MessageProcess()

    
    def SetParent(self, parent):
        self.m_Parent = interface.CShadowObject(parent)

    
    def Enter(self):
        parent = self.m_Parent.Get()
        self.m_Tips = wrapinterface.CTextTips(None, -1, parent.m_NameText, interface.FontLT14_3, direct = 0, owner = self)

    
    def Leave(self):
        self.m_Tips = None

    
    def LeftDown(self):
        import cursor
        import walker
        import goods
        import district
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, walker.CWalkerBase):
                obj.LeftDown()
                break
            
            if isinstance(obj, goods.CCrop) and isinstance(obj, goods.CGoods) or isinstance(obj, district.CDoorplate):
                obj.LeftDown()
                break
                continue
        else:
            import map
            if hasattr(map, 'g_Map') and map.g_Map is not None:
                map.g_Map.LeftDown()
            

    
    def RightDown(self):
        import cursor
        import walker
        import goods
        import district
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, walker.CWalkerBase):
                obj.RightDown()
                break
            
            if isinstance(obj, goods.CCrop) and isinstance(obj, goods.CGoods) or isinstance(obj, district.CDoorplate):
                obj.RightDown()
                break
                continue
        else:
            import map
            if hasattr(map, 'g_Map') and map.g_Map is not None:
                map.g_Map.RightDown()
            

    
    def LeftUp(self):
        import cursor
        import walker
        import goods
        import district
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, walker.CWalkerBase):
                obj.LeftUp()
                break
            
            if isinstance(obj, goods.CCrop) and isinstance(obj, goods.CGoods) or isinstance(obj, district.CDoorplate):
                obj.LeftUp()
                break
                continue
        else:
            import map
            if hasattr(map, 'g_Map') and map.g_Map is not None:
                map.g_Map.LeftUp()
            

    
    def RightUp(self):
        import cursor
        import walker
        import goods
        import district
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, walker.CWalkerBase):
                obj.RightUp()
                break
            
            if isinstance(obj, goods.CCrop) and isinstance(obj, goods.CGoods) or isinstance(obj, district.CDoorplate):
                obj.RightUp()
                break
                continue
        else:
            import map
            if hasattr(map, 'g_Map') and map.g_Map is not None:
                map.g_Map.RightUp()
            



def GetMovLen(spr, path):
    import C_sys
    data = C_sys.LoadFile(spr, path).split('\n')[1:]
    ct = 0
    
    try:
        for i in data:
            arr = i.split(' ')
            ct += int(arr[1])
    except:
        pass

    return ct


def GetMovData(spr, path):
    import C_sys
    data = C_sys.LoadFile(spr, path).split('\n')[1:]
    arr1 = []
    
    try:
        for i in data:
            arr = i.split(' ')
            arr1.append((int(arr[0]), int(arr[1])))
    except:
        pass

    return arr1


def Show(data):
    global g_FireDlg
    g_FireDlg = CCombFireDlg(data)


def UpdateDIYTemplateList(\xacct):
    if g_FireDlg:
        g_FireDlg.UpdateDIYTemplateList(\xacct)
    


def UpdateDIYTemplateLen(ID, amount):
    if g_FireDlg:
        g_FireDlg.UpdateDIYTemplateLen(ID, amount)
    


def UpdateDIYTemplateData(ID, Data):
    if g_FireDlg:
        g_FireDlg.UpdateDIYTemplateData(ID, Data)
    


def Hide():
    global g_FireDlg
    g_FireDlg = None


def CanPlace(data):
    import hero
    (x, y) = hero.g_Hero.GetPos()
    return _CanPlace(x, y, data)


def TransPos(ipos, flag = 1):
    import math
    rows = ipos % 13
    cols = ipos / 13
    t = 45
    if flag == 1:
        x1 = -int(cols * BASE_WIDTH * math.cos((math.pi / 180) * t) - rows * BASE_WIDTH * math.sin((math.pi / 180) * t))
        y1 = int(cols * BASE_WIDTH * math.cos((math.pi / 180) * t) + rows * BASE_WIDTH * math.sin((math.pi / 180) * t)) * 0.6
    else:
        y1 = cols * BASE_WIDTH * 0.7
        x1 = BASE_WIDTH * (rows - 7) * 0.9
    return (x1, y1)


def _CanPlace(x, y, data, flag = 1):
    import map
    xx = 2
    for ipos, itype in data:
        rows = ipos % 13
        cols = ipos / 13
        if cols in range(xx - 1, 12 - xx) and rows in range(xx - 1, 12 - xx):
            t = 45
            (x1, y1) = TransPos(ipos, flag)
            x1 = int(x1 + x)
            y1 = int(y1 + y)
            if map.g_Map.GetEventPoint(int(x1 / 20), int(y1 / 20)) in (1, 2):
                return False
            
        map.g_Map.GetEventPoint(int(x1 / 20), int(y1 / 20)) in (1, 2)
    
    return True


def Clear(id):
    import world
    print '\xa7R\xb0\xa3----', id
    
    try:
        world.g_Objects[id].m_Brother = []
        world.g_Objects[id].m_Sprs = []
        world.g_Objects[id].m_Lights = { }
        world.g_Objects[id].m_Sprs = []
        world.DelObject(id)
    except:
        pass



def OutPut(filename):
    if g_FireDlg:
        data = [
            '@@ver1']
        for it in g_FireDlg.m_Items:
            id1 = 0
            id = 0
            color = 0
            
            try:
                id = int(it.m_SprID)
                color = int(it.m_SprColor)
            except:
                pass

            
            try:
                id1 = int(it.m_ID)
            except:
                pass

            if id > 0 or id1 > 0:
                data.append('%d\t%d\t%d\t%d\t%d' % (it.m_Pos, it.m_Index, id1, id, color))
                continue
        
        
        try:
            f = open('mapobject\\fire\\%s.txt' % filename, 'w')
            f.write('\r\n'.join(data))
            f.close()
        except IOError:
            return None
        except:
            None<EXCEPTION MATCH>IOError
        

    None<EXCEPTION MATCH>IOError
    import usermacro
    usermacro.PROMPT_MSG('\xa5\xb4\xb6}\xbc\xd2\xaaO\xa4~\xaf\xe0\xb6i\xa6\xe6\xac\xdb\xc0\xb3\xbe\xde\xa7@.')


def ReadData(filename):
    
    try:
        import C_sys
        d = C_sys.LoadFile('fire\\%s.txt' % filename, 'mapobject')
        f = d.split('\n')[1:]
    except:
        f = []

    data = []
    for t in f:
        arr = t.split('\t')
        
        try:
            ipos = int(arr[0])
        except:
            ipos = 0

        
        try:
            iSeries = int(arr[1])
        except:
            iSeries = 0

        
        try:
            id1 = int(arr[2])
        except:
            id1 = 0

        
        try:
            id = int(arr[3])
        except:
            id = 0

        
        try:
            color = int(arr[4])
        except:
            color = 0

        data.append((ipos, iSeries, id1, id, color))
    
    return data


def InPut(filename):
    if g_FireDlg:
        for it in g_FireDlg.m_Items:
            it.Clear()
        
        
        try:
            import C_sys
            d = C_sys.LoadFile('fire\\%s.txt' % filename, 'mapobject')
            f = d.split('\n')[1:]
        except:
            f = []

        cts = 0
        for t in f:
            arr = t.split('\t')
            
            try:
                ipos = int(arr[0])
            except:
                ipos = 0

            
            try:
                index = int(arr[1])
            except:
                index = 0

            
            try:
                id1 = int(arr[2])
            except:
                id1 = 0

            
            try:
                id = int(arr[3])
            except:
                id = 0

            
            try:
                color = int(arr[4])
            except:
                color = 0

            it = g_FireDlg.m_Items[ipos]
            if id1:
                import firedata
                arr = firedata.DATA.get(id1)
                if arr:
                    it.SetItem(id1, arr[2])
                
                it.m_Type = arr[1]
            
            if id:
                import firedata
                arr = firedata.DATA.get(id)
                it.SetSprItem(id, color)
                it.m_SprType = arr[1]
                g_FireDlg.SetBg(id, ipos)
            
            if id or id1:
                cts += 1
            
            it.m_Index = index
            it.Select(False)
        
        g_FireDlg.MakeCts()
