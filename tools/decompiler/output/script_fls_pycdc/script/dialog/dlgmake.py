# pycdc 交叉复核产物 · script.fls entry 4907
# co_filename(原始)='script/dialog/dlgmake.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4907.pyc (Python 2.5)

import combdialog
import combmacro
import interface
import item
import style
import ui
MAKESKILL = 1111
g_MakeDialog = None
g_tips = None

def ModuleReset():
    global g_MakeDialog, g_tips
    g_MakeDialog = None
    g_tips = None


class CMakeDialog(combdialog.CCombDialog):
    TYPE2NUM = [
        1,
        2,
        2,
        3,
        5,
        5,
        6,
        7,
        7,
        9,
        9,
        2,
        2]
    REPAIR = ((), ('equip',), ('all',), ('all',), ('all',), ('all',), ('all',), ('all',), ('all',), ('all',), ('all',), (), ('all',), ())
    MAKE = [
        (),
        ((25077, 25078), (26001, 26001), (26002, 26002), (26003, 26003), (26004, 26004), (26005, 26005), (26006, 26006), (26007, 26007), (26008, 26008), (26009, 26009), (26010, 26010), (26011, 26011), (26012, 26012), (26013, 26013), (26014, 26014), (26015, 26015), (30381, 'equip'), (30382, 'equip'), (30383, 'equip'), (30384, 'equip'), (30385, 'equip'), (30386, 'equip'), (30387, 'equip'), (30388, 'equip'), (26861, 'equip'), (26862, 'equip'), (26863, 'equip'), (26864, 'equip'), (26865, 'equip'), (26866, 'equip'), (26867, 'equip'), (30381, 30381), (30382, 30382), (30383, 30383), (30384, 30384), (30385, 30385), (30386, 30386), (30387, 30387), (30388, 30388), (26861, 26861), (26862, 26862), (26863, 26863), (26864, 26864), (26865, 26865), (26866, 26866), (26867, 26867), (70651, 'equip'), (70652, 'equip'), (70653, 'equip'), (70654, 'equip'), (70655, 'equip'), (26015, 26015), ('gem', 'equip'), ('reloaditem', 'equip'), (25678, 25678), (25679, 25679), (25678, 'equip'), (25679, 'equip'), (70601, 70601), (70602, 70602), (70603, 70603), (70604, 70604), (70605, 70605), (70611, 70611), (70612, 70612), (70613, 70613), (70614, 70614), (70615, 70615), (30401, 30401), (30402, 30402), (30403, 30403), (30411, 30411), (30412, 30412), (30413, 30413), (26865, 26866), (30385, 30386), (30414, 30415), (70616, 70617), (30414, 70617), (70616, 30415)),
        (),
        (),
        (),
        (),
        (),
        (),
        (),
        (),
        (),
        (('makebook', 'equip'),),
        ()]
    
    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/make.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        import hero
        hero.CreateCombDlgCash('txt_info', 'MakeDlg', (('m_Cash', 0, 3),), self)
        self.m_Boxs = [
            (self.GetObject('area_items'), self.GetObject('fight_item_box'), self.GetObject('noname11')),
            (self.GetObject('itembox2'),)]
        self.m_Boxs_Name = [
            ('area_items', 'fight_item_box'),
            ('itembox2',)]
        self.m_Boxs_Data = [
            ([
                item.ITEM_START,
                30], [
                item.ITEM_FIGHT_START,
                10]),
            ([
                item.ITEM_SCOPE,
                40],)]
        self.box_Tpye = 0
        self.m_TiliTxt = None
        self.m_MoneyTxt = None
        self.m_SLVTxt = None

    
    def UpdateBag(self, num = None):
        import hero
        if num is None:
            num = hero.g_Prop.m_BagMax
        
        for i in xrange(num, 40):
            pos = i + item.ITEM_SCOPE
            iit = self.m_InterfaceItems.get(pos)
            if iit:
                iit.Enable(False)
                continue
        

    
    def Switch(self, itype):
        print 'Switch  ', itype
        self.box_Tpye = itype
        for i in xrange(2):
            for box in self.m_Boxs[i]:
                box.SetShow(False)
                if hasattr(box, 'm_Real'):
                    for real in box.m_Real:
                        ob = real.Get()
                        if ob:
                            ob.SetShow(False)
                            continue
                    
            
        
        for box in self.m_Boxs[itype]:
            box.SetShow(True)
            if hasattr(box, 'm_Real'):
                for real in box.m_Real:
                    ob = real.Get()
                    if ob:
                        ob.SetShow(True)
                        continue
                
        
        for a in xrange(len(self.m_Boxs_Data)):
            for b in self.m_Boxs_Data[a]:
                for i in xrange(b[1]):
                    pos = i + b[0]
                    if a == self.box_Tpye:
                        self.m_InterfaceItems[pos].SetShow(True)
                        continue
                    self.m_InterfaceItems[pos].SetShow(False)
                
            
        
        self.CheckValid()
        self.UpdateBag()

    
    def UpdateCost(self, iTili, iMoney, sklv):
        self.m_TiliTxt = combmacro.CIFTEXT(interface.CTextObject, 'txt_info', self, 0, 1, str(iTili), interface.FontLT14_3, interface.COLOR_1)
        continue
        self.m_MoneyTxt = interface.CTextObject('txt_info', self, 0, 2, str, iMoney, interface.FontLT14_3, interface.COLOR_1)
        self.m_SLVTxt = combmacro.CIFTEXT(interface.CTextObject, 'txt_info', self, 0, 0, str(sklv), interface.FontLT14_3, interface.COLOR_1)

    
    def Refresh(self, itype):
        self.m_Type = itype
        itype_special = -1
        if itype in (4, 12):
            if type == 4:
                itype = 2
                self.m_Type = 2
            
            itype_special = 4
        
        self.m_Disabled = []
        for idx in xrange(self.TYPE2NUM[itype], 9):
            bd = ui.CImage(self, style.GetPath('common/itembox_disabled.igs'), interface.UIPath)
            (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', idx / 3, idx % 3)
            bd.SetPos(x, y)
            self.m_Disabled.append(bd)
        
        if itype == 11:
            tips_txt = '#R\xbd\xd0\xb1N\xbb\xdd\xadn\xad\xab\xb8m\xc4\xdd\xa9\xca\xaa\xba\xb8\xcb\xb3\xc6\xa1A\xa5\xb4\xb3y\xb2\xc5\xa9\xce\xb1j\xa4\xc6\xa5\xb4\xb3y\xb2\xc5\xa1A\xa5H\xa4\xce\xa8\xe4\xa5L\xa5\xb4\xb3y\xa5\xce\xa7\xf7\xae\xc6\xa1]\xa8\xe2\xbb\xf6\xa5\xdb\\\xa4\xd1\xb4\xb9\xa5\xdb\xa1A\xa4\xad\xbcw\xba\xeb\xba\xe9\xa1A\xa4\xb8\xae\xf0\xb5\xb2\xb4\xb9\xa1^\xa6P\xae\xc9\xa9\xf1\xa4J\xa5\xb4\xb3y\xae\xe6\xa4\xba\xa1A\xa7\xda\xb1N\xae\xda\xbe\xda\xb1z\xa9\xd2\xa9\xf1\xa4J\xaa\xba\xa7\xf7\xae\xc6\xac\xb0\xb1z\xaa\xba\xb8\xcb\xb3\xc6\xb6i\xa6\xe6\xac\xdb\xc0\xb3\xaa\xba\xc4\xdd\xa9\xca\xad\xab\xb8m\xa1C'
            if self.m_TiliTxt:
                self.m_TiliTxt.SetShow(False)
            
            if self.m_MoneyTxt:
                self.m_MoneyTxt.SetShow(False)
            
            if self.m_SLVTxt:
                self.m_SLVTxt.SetShow(False)
            
            for n in [
                'noname9',
                'noname10',
                'noname6',
                'noname7',
                'txt_info',
                'noname8',
                'btn_repair']:
                self.GetObject(n).SetShow(False)
            
            self.GetObject('txt_info').m_Cash.SetShow(False)
            (x, y) = self.GetObject('desc').GetPos()
            self.GetObject('desc').SetPos(x, y - 6)
        elif itype_special == 4:
            tips_txt = ''
        else:
            tips_txt = '#R\xbbs\xb3y\xa1G\xa5i\xa5H\xbbs\xb3y\xb8\xcb\xb3\xc6\xa9\xce\xaa\xcc\xa6X\xa6\xa8\xaa\xab\xab~\xa1C\xad\xec\xa7\xf7\xae\xc6\xb5\xa5\xaf\xc5\xa4\xa3\xaf\xe0\xb6W\xb9L\xbbs\xb3y\xa7\xde\xaf\xe0\xb5\xa5\xaf\xc5\xa1C#r\xad\xd7\xb2z\xa1G\xa4\xe4\xa5I\xa4@\xa9w\xaa\xba\xb6O\xa5\xce\xb4N\xa5i\xa5H\xa8\xcf\xb8\xcb\xb3\xc6\xb7\xd8\xb5M\xa4@\xb7s\xa1C\xa1]\xad@\xa4[\xab\xd7\xb8\xc9\xba\xa1\xa1^'
        self.m_TipsTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, tips_txt, interface.FontLT14_3, 13775360)
        self.m_TiliTxt = None
        self.m_MoneyTxt = None
        self.m_Produce = None
        self.m_ID2Pos = { }
        self.m_InterfaceItems = { }
        self.m_SelectedItems = []
        for i in xrange(9):
            self.m_SelectedItems.append(None)
        
        for a in xrange(len(self.m_Boxs_Data)):
            index = 0
            for b in self.m_Boxs_Data[a]:
                box_Name = self.m_Boxs_Name[a][index]
                index += 1
                for i in xrange(b[1]):
                    pos = i + b[0]
                    (x, y, w, h) = combmacro.GetIFObjectData(self, box_Name, i / 5, i % 5)
                    iit = item.CInterfaceItem(self, x, y, pos + 100)
                    iit.Refresh(pos)
                    self.m_InterfaceItems[pos] = iit
                
            
        
        self.Switch(self.box_Tpye)
        if self.box_Tpye == 0:
            self.GetObject('noname19').LeftUp()
        else:
            self.GetObject('noname20').LeftUp()
        self.GetObject('btn_make').Enable(False)
        self.GetObject('btn_repair').Enable(False)

    
    def _findtype(self, shape, lst):
        import itemdata
        for v in lst:
            if type(v) == str and itemdata.IsType(shape, v):
                return v
                continue
        

    
    def CheckValid(self):
        ids = self.GetItemsID()
        ss = [ self.GetSelectedItemShape(id) for id in ids ]
        enabled = []
        for m in self.MAKE[self.m_Type]:
            r = list(m)
            for s in ss:
                
                try:
                    r.remove(s)
                continue
                except ValueError:
                    None if (len(ids) == 0 or len(self.MAKE[self.m_Type]) == 0) and len(ids) < self.TYPE2NUM[self.m_Type] else []
                    None if (len(ids) == 0 or len(self.MAKE[self.m_Type]) == 0) and len(ids) < self.TYPE2NUM[self.m_Type] else []
                    
                    try:
                        r.remove(self._findtype(s, r))
                    except ValueError:
                        r = []
                        break
                    except:
                        None<EXCEPTION MATCH>ValueError
                    


                None if (len(ids) == 0 or len(self.MAKE[self.m_Type]) == 0) and len(ids) < self.TYPE2NUM[self.m_Type] else []<EXCEPTION MATCH>ValueError
            
            enabled.extend(r)
        
        import itemdata
        if self.m_Type == 1:
            if len(ss) >= 2:
                if not 25077 in ss or 25078 in ss:
                    if (itemdata.IsType(ss[0], 'equip') or itemdata.IsType(ss[1], 'reloaditem') or itemdata.IsType(ss[1], 'equip')) and itemdata.IsType(ss[0], 'reloaditem'):
                        for s in ss[2:]:
                            if itemdata.IsType(s, 'makegem'):
                                break
                                continue
                            None if self.m_Type == 11 else None if (len(ids) == 0 or len(self.MAKE[self.m_Type]) == 0) and len(ids) < self.TYPE2NUM[self.m_Type] else []
                        
                        for s in ss[2:]:
                            if itemdata.IsType(s, 'supermake'):
                                break
                                continue
                        
                        for s in ss[2:]:
                            if itemdata.IsType(s, 'makedir'):
                                break
                                continue
                        
                        self.m_Disabled[0].SetShow(False)
                        self.m_Disabled[1].SetShow(False)
                        self.m_Disabled[2].SetShow(False)
                    else:
                        self.m_Disabled[0].SetShow(True)
                        self.m_Disabled[1].SetShow(True)
                        self.m_Disabled[2].SetShow(True)
                
        for iif in self.m_InterfaceItems.values():
            if iif.m_Item is None and iif.m_Item.m_ID in ids and iif.m_Item.m_Shape in enabled or self._findtype(iif.m_Item.m_Shape, enabled):
                iif.Enable(True)
                continue
            iif.Enable(False)
        

    
    def OnSelectItem(self, pos):
        
        def getempty():
            mtype = self.m_Type
            if not self.m_Disabled[0].GetShow() and mtype in (1, 11):
                mtype = 4
            
            for idx in xrange(self.TYPE2NUM[mtype]):
                if self.m_SelectedItems[idx] is None:
                    return idx
                    continue
            

        self.m_Produce = None
        itf = self.m_InterfaceItems[pos]
        ids = self.GetItemsID()
        if itf.m_Item.m_ID in ids:
            itf.Select(False)
            self.m_SelectedItems[itf.m_Idx] = None
            iidx = itf.m_Idx
            del itf.m_Idx
            if not self.m_Disabled[0].GetShow() and self.m_Type in (1, 11) and iidx < 2:
                
                try:
                    del self.m_InterfaceItems[self.m_SelectedItems[2].m_Pos].m_Idx
                    self.m_InterfaceItems[self.m_SelectedItems[2].m_Pos].Select(False)
                except:
                    (None,)

                
                try:
                    del self.m_InterfaceItems[self.m_SelectedItems[3].m_Pos].m_Idx
                    self.m_InterfaceItems[self.m_SelectedItems[3].m_Pos].Select(False)
                except:
                    (None,)

                self.m_SelectedItems[2] = None
                self.m_SelectedItems[3] = None
            
        else:
            idx = getempty()
            if idx is not None:
                itf.Select(True)
                (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', idx / 3, idx % 3)
                it = item.CInterfaceItem(self, x, y, 100 + pos)
                it.Refresh(pos)
                self.m_SelectedItems[idx] = it
                itf.m_Idx = idx
            
        itype = None
        ids = self.GetItemsID()
        self.m_TiliTxt = None
        self.m_MoneyTxt = None
        if len(ids) == 0:
            self.GetObject('btn_repair').Enable(False)
            self.GetObject('btn_make').Enable(False)
        else:
            import itemdata
            ss = [ self.GetSelectedItemShape(id) for id in ids ]
            if len(ids) == 1:
                if self.m_Type == 0 or self.m_Type == 1:
                    for r in self.REPAIR[self.m_Type]:
                        if type(r) == str or itemdata.IsType(ss[0], r) or ss[0] == r:
                            itype = 0
                            break
                            continue
                        []
                    
                elif self.m_Type == 1:
                    for m in self.MAKE[self.m_Type]:
                        r = list(m)
                        for s in ss:
                            
                            try:
                                r.remove(s)
                            continue
                            except ValueError:
                                
                                try:
                                    r.remove(self._findtype(s, r))
                                except ValueError:
                                    break
                                except:
                                    None<EXCEPTION MATCH>ValueError
                                


                            None<EXCEPTION MATCH>ValueError
                        
                        if len(r) == 0:
                            itype = self.m_Type
                            break
                            continue
                    
                else:
                    itype = self.m_Type
        self.CheckValid()
        if itype is None:
            return None
        elif itype == 0:
            self.GetObject('btn_repair').Enable(True)
            self.GetObject('btn_make').Enable(True)
        else:
            self.GetObject('btn_repair').Enable(False)
            self.GetObject('btn_make').Enable(True)
        import netnpc
        print 'itype', itype
        ids0 = self.GetItemsShape()
        j = 0
        for i, v in enumerate(ids0):
            if v in xrange(70651, 70656):
                del ids[i + j]
                j += 1
                continue
        
        netnpc.C2SGetMakeCost(itype, ids)

    
    def GetItemsID(self):
        ids = []
        for it in self.m_SelectedItems:
            if it is not None:
                ids.append(it.m_Item.m_ID)
                continue
        
        return ids

    
    def GetItemsShape(self):
        ids = []
        for it in self.m_SelectedItems:
            if it is not None:
                ids.append(it.m_Item.m_Shape)
                continue
        
        return ids

    
    def GetSelectedItemShape(self, id):
        for it in self.m_SelectedItems:
            if it is not None and it.m_Item.m_ID == id:
                return it.m_Item.m_Shape
                continue
        

    
    def MakeOver(self, shape, amount, desc):
        self.Refresh(self.m_Type)
        if amount > 0:
            import usermacro
            import itemdata
            d = itemdata.GetData(shape)
            usermacro.MOVE_MSG(0, shape, '\xbbs\xb3y\xa4F%d\xad\xd3%s' % (amount, d[0]))
            import wrapinterface
            self.m_Produce = wrapinterface.CItemIcon(self, shape, amount, 10)
            self.m_Produce.SetInfoExt(desc)
            (x, y, w, h) = self.GetLocData('box_result')
            self.m_Produce.SetPos(x, y)
        

    
    def OnIconEnter(self, obj):
        obj.ShowTips()

    
    def OnIconLeave(self, obj):
        obj.HideTips()

    
    def OnMessage(self, msgid):
        print 'msgid, self.m_Type', msgid, self.m_Type
        if msgid == 1:
            self.SetShow(False)
        elif msgid == 3:
            import netnpc
            import sound
            import sounddefine
            sound.Play(sounddefine.PATH_MAKEEQUIP_SOUND)
            ids = self.GetItemsID()
            if self.m_Type == 3:
                netnpc.C2SMake3(self.GetItemsID())
            elif self.m_Type == 11:
                iShapes = self.GetItemsShape()
                extend = 0
                for id in iShapes:
                    if id in xrange(70651, 70656):
                        extend = 16
                        break
                        continue
                
                len_ids = len(ids)
                if extend:
                    len_ids -= 1
                
                if len_ids == 2:
                    netnpc.C2SMake11(1, self.GetItemsID(), extend)
                elif len_ids == 3:
                    netnpc.C2SMake11(2, self.GetItemsID(), extend)
                elif len_ids == 4:
                    netnpc.C2SMake11(3, self.GetItemsID(), extend)
                
            else:
                iShapes = self.GetItemsShape()
                extend = 0
                for id in iShapes:
                    if id in xrange(70651, 70656):
                        extend = 16
                        break
                        continue
                
                len_ids = len(ids)
                if extend:
                    len_ids -= 1
                
                if not self.m_Disabled[0].GetShow() and self.m_Type == 1 and len_ids >= 3:
                    if len_ids == 3:
                        netnpc.C2SMakeGem(ids, extend)
                    elif len_ids == 4:
                        netnpc.C2SSuperMake(ids, extend)
                    
                elif len_ids == 1:
                    netnpc.C2SMake(7, ids, extend)
                else:
                    ss = [ self.GetSelectedItemShape(id) for id in ids ]
                    
                    def OK(obj):
                        netnpc.C2SMake(self.m_Type, self.GetItemsID(), extend)

                    if 25077 in ss and 25078 in ss:
                        book_info = 0
                        iron_info = 0
                        import item
                        for id in ids:
                            it = item.GetItem(id)
                            if it.m_Shape == 25077:
                                if hasattr(it, 'm_InfoExt') and it.m_InfoExt:
                                    txt = it.m_InfoExt.split('#r')[0]
                                    book_info = int(txt.split(' ')[2])
                                else:
                                    self.SetShow(False)
                                    return None
                            it.m_InfoExt
                            if it.m_Shape == 25078:
                                if hasattr(it, 'm_InfoExt') and it.m_InfoExt:
                                    txt = it.m_InfoExt.split('#r')[0]
                                    iron_info = int(txt.split(' ')[1])
                                else:
                                    self.SetShow(False)
                                    return None
                            it.m_InfoExt
                        
                        if book_info and iron_info and book_info < iron_info:
                            import commondialog
                            commondialog.ShowMessageBox('\xa7A\xa9\xd2\xa8\xcf\xa5\xce\xaa\xba\xa6\xca\xb7\xd2\xba\xeb\xc5K\xaa\xba\xb5\xa5\xaf\xc5\xb0\xaa\xa9\xf3\xbbs\xb3y\xab\xfc\xabn\xae\xd1\xa1A\xbbs\xb3y\xaa\xba\xb8\xcb\xb3\xc6\xb5\xa5\xaf\xc5\xb1N\xb7|\xb5\xa5\xa6P\xa9\xf3\xbbs\xb3y\xab\xfc\xabn\xae\xd1\xaa\xba\xb5\xa5\xaf\xc5\xa1A\xbd\xd0\xb0\xdd\xa7A\xacO\xadn\xab\xf6\xb7\xd3\xa6\xb9\xa4\xe8\xae\xd7\xbbs\xa7@\xb8\xcb\xb3\xc6\xbb\xf2', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OK, None))
                        else:
                            OK(None)
                    else:
                        OK(None)
        elif msgid == 4:
            import netnpc
            import sound
            netnpc.C2SMake(0, self.GetItemsID())
            import sounddefine
            sound.Play(sounddefine.PATH_MAKEEQUIP_SOUND)
        elif msgid in (6, 7):
            self.Switch(msgid - 6)
        elif msgid == 10:
            self.m_Produce = None
        elif msgid >= interface.RIGHT_BUTTON_MESSAGE:
            pos = msgid - interface.RIGHT_BUTTON_MESSAGE - 100
            if self.m_InterfaceItems[pos].m_Item is None:
                self.OnMessage(1)
            
        elif msgid >= 100:
            pos = msgid - 100
            if self.m_InterfaceItems[pos].m_Item:
                self.OnSelectItem(pos)
            
        



def ShowMakeDialog(itype):
    global g_MakeDialog
    g_MakeDialog = CMakeDialog(interface.DialogPanel)
    import netnpc
    netnpc.SetMakeCallback(MakeOver)
    g_MakeDialog.Refresh(itype)


def ShowReMakeDialog():
    global g_MakeDialog
    g_MakeDialog = CMakeDialog(interface.DialogPanel)
    import netnpc
    netnpc.SetMakeCallback(MakeOver)
    g_MakeDialog.Refresh(11)


def UpdateCost(iTili, iMoney, sklv):
    
    try:
        g_MakeDialog.UpdateCost(iTili, iMoney, sklv)
    except:
        pass



def MakeOver(itype, amount, desc):
    if g_MakeDialog:
        g_MakeDialog.MakeOver(itype, amount, desc)
