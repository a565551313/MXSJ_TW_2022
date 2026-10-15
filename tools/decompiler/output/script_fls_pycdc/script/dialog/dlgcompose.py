# pycdc 交叉复核产物 · script.fls entry 2962
# co_filename(原始)='script/dialog/dlgcompose.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2962.pyc (Python 2.5)

import interface
import combdialog
import item
import style
import mdpropitem
import itemdefine
g_Dialog = None

def ModuleReset():
    global g_Dialog
    g_Dialog = None


def Show(mode, itemID = 0, bPlaySound = True):
    global g_Dialog, g_Dialog, g_Dialog
    import netnpc
    import hero
    if mode:
        mode2class = {
            1: CGemCompDlg,
            2: CGemCompDlg,
            3: CGemCompDlg,
            4: CRemakeDlg,
            5: CBaguaDlg,
            6: CTJCDlg,
            7: CTJCDlg,
            8: CEyeCompDlg,
            9: CCrystalDlg,
            10: CIceBallDlg,
            11: CTattooUpdateDlg,
            12: CTattooStrengthenDlg,
            13: CTattooFuseDlg }
        if g_Dialog and hasattr(g_Dialog, 'DelInterfaceItem'):
            g_Dialog.DelInterfaceItem()
        
        if mode in (1, 2, 3):
            g_Dialog = mode2class[mode](mode, bPlaySound)
        else:
            g_Dialog = mode2class[mode](mode)
        if itemID != 0 and hasattr(g_Dialog, 'SetResultItem'):
            g_Dialog.SetResultItem(itemID)
        
        netnpc.SetMakeCallback(g_Dialog.OnCompose)
        netnpc.SetMakeIDCallback(SetResultItem)
        hero.g_Name2PropItem['m_Cash'].AddRefreshCallbackWithID('CComposeDlg', g_Dialog.OnCashChg)
        hero.g_Name2PropItem['m_Huoli'].AddRefreshCallbackWithID('CComposeDlg', g_Dialog.OnHuoliChg)
    elif g_Dialog:
        item.ReleaseInterfaceCallback(g_Dialog.m_InterfaceItem)
        netnpc.SetMakeCallback(None)
        hero.g_Name2PropItem['m_Cash'].RemoveRefreshCallbackWithID('CComposeDlg')
        hero.g_Name2PropItem['m_Huoli'].RemoveRefreshCallbackWithID('CComposeDlg')
    
    g_Dialog = None


def UpdateCost(ihuoli, iMoney, sklv):
    if g_Dialog:
        g_Dialog.OnCostChg(ihuoli, iMoney, sklv)
    


class CInterfaceItem(item.CInterfaceItem):
    s_ShowExtItem = []
    s_ExtColor = 65280
    
    def InitExtItem(self, itemLst):
        CInterfaceItem.s_ShowExtItem = itemLst

    InitExtItem = classmethod(InitExtItem)
    
    def SetItem(self, it):
        item.CInterfaceItem.SetItem(self, it)
        extName = None
        if it and it.m_Shape in self.s_ShowExtItem:
            extName = it.GetExtName()
        
        self.CreateExtName(extName)

    
    def SetExtNameColor(self, icolor = 65280):
        CInterfaceItem.s_ExtColor = icolor

    SetExtNameColor = classmethod(SetExtNameColor)
    
    def CreateExtName(self, name):
        self.m_ExtNameTextLst = []
        if name:
            txtLst = []
            if len(name) < 8:
                txtLst = [
                    name]
            
            if len(name) == 8:
                txtLst = [
                    name[:4],
                    name[4:]]
            elif len(name) == 10:
                txtLst = [
                    name[:4].ljust(6),
                    name[4:]]
            elif len(name) >= 12:
                txtLst = [
                    name[:6],
                    name[6:]]
            
            hSpace = 28
            for txt in reversed(txtLst):
                obj = interface.CTextObject(self.m_ItemImg, txt, interface.FontLT12E_1, CInterfaceItem.s_ExtColor)
                (w, h) = obj.GetSize()
                x = None if interface.IsNewStyle() else (44 - w) + 2
                obj.SetPos(x, hSpace)
                obj.SetZ(1000)
                hSpace -= h
                self.m_ExtNameTextLst.append(obj)
            
        



class CComposeDlg(combdialog.CCombDialog):
    DIALOG_PATH = 'dialog/compose.dlg'
    s_ShowExtItem = []
    s_ExtColor = 65280
    
    def __init__(self, mode, bPlaySound = True):
        self.m_bPlaySound = bPlaySound
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, self.DIALOG_PATH)
        interface.Center(self)
        self.m_Mode = mode
        self.m_InputItems = {
            0: None,
            1: None }
        self.m_OuputItem = None
        self.m_LastCommit = 0
        self.CreateInterfaceItem()
        self.InitSound()
        self.GetObject('item').LeftUp()
        self.SwitchBtn(0)

    
    def InitSound(self):
        import soundmgr
        oMgr = soundmgr.GetSoundMgr()
        oMgr.SetPathState('action/diamondtake.wav', False)

    
    def CreateInterfaceItem(self):
        import hero
        import combmacro
        self.m_InterfaceItem = { }
        CInterfaceItem.InitExtItem(self.s_ShowExtItem)
        CInterfaceItem.SetExtNameColor(self.s_ExtColor)
        self.m_ItemStyle = CInterfaceItem
        item.AddInterfaceCallback(self.m_InterfaceItem, oRefObj = self)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_items1', self, item.ITEM_START, self.m_InterfaceItem, 100)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_fight', self, item.ITEM_FIGHT_START, self.m_InterfaceItem, 100)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_items2', self, item.ITEM_SCOPE, self.m_InterfaceItem, 100)
        limit = item.ITEM_SCOPE + hero.g_Prop.m_BagMax
        for i in range(item.ITEM_SCOPE, item.ITEM_SCOPE + 40):
            it = self.m_InterfaceItem[i]
            it.Enable(i < limit)
            func = {
                True: self.DelBg,
                False: self.CreateBg }[i < limit]
            func(it)
        

    
    def DelInterfaceItem(self):
        item.ReleaseInterfaceCallback(self.m_InterfaceItem)

    
    def CreateBg(self, iit):
        import combmacro
        iit.m_Background = None
        igs = combmacro.CIMAGE(iit, style.GetPath('combdialog/\xd4\xd3\xcd\xbc/\xce\xef\xc6\xb7\xb8\xf1.igs'), interface.UIPath)
        igs.SetPos(0, 0)
        igs.SetAlpha(144)
        igs.SetZ(1000)
        iit.m_Background = igs

    
    def DelBg(self, iit):
        if hasattr(iit, 'm_Background'):
            iit.m_Background = None
        

    
    def SwitchBtn(self, switch):
        obj = self.GetObject('loc_btns')
        if not obj:
            return None
        
        btn1 = self.GetObject('btn_NormalComp')
        btn2 = self.GetObject('btn_QuickComp')
        if switch == 1:
            lst = ((btn1, True, True), (btn2, False, False))
        elif switch == 2:
            lst = ((btn1, True, True), (btn2, True, True))
        else:
            lst = ((btn1, True, False), (btn2, False, False))
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        tmp_lst = _[1]
        base = []([ btn.GetSize()[0] for btn in tmp_lst ])
        base = (w - base) / (len(tmp_lst) + 1)
        x += base
        for btn, bShow, bEnable in lst:
            btn.SetShow(bShow)
            btn.Enable(bEnable)
            btn.SetPos(x, y)
            (w, h) = btn.GetSize()
            x += w + base
        

    
    def ShowDesc(self, desc):
        if desc:
            import combmacro
            self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, interface.Replace(desc), interface.FontLT14_3, interface.COLOR_4)
        else:
            self.m_Desc = None

    
    def ShowComp(self, data):
        if data:
            (shape, amount, desc) = data
            import wrapinterface
            self.m_OuputItem = wrapinterface.CItemIcon(self, shape, amount, 0)
            obj = self.GetObject('box_result')
            (x, y) = obj.GetPos()
            (w, h) = obj.GetSize()
            (iw, ih) = self.m_OuputItem.GetSize()
            self.m_OuputItem.SetPos(x + (w - iw) / 2, y + (h - ih) / 2)
        else:
            self.m_OuputItem = None

    
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

    
    def IsQuickComp(self, dct):
        import dlgmakenew
        TYPE2OBJECT = dlgmakenew.TYPE2OBJECT
        for key in (0, 1):
            itf = dct[key]
            if not itf:
                continue
            
            iit = itf.GetItem()
            if not iit:
                continue
            
            tp = dlgmakenew.GetType(iit.m_Shape)
            if TYPE2OBJECT.get(tp, '') in ('\xc4_\xa5\xdb\xa5]', '\xc4_\xa5\xdb', '\xb4H\xb0\xb2\xb3\xb7\xb2y', '\xa4K\xa8\xf6\xafu\xae\xf0', '\xc5]\xaak\xa4\xf4\xb4\xb9', '\xad\xab\xb3y\xba\xeb\xb5\xd8', '\xafu\xae\xf0\xa4f\xb3U', '\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL'):
                return True
                continue
        
        tjCount = 0
        tjShape = []
        for key in (0, 1):
            itf = dct[key]
            if not itf:
                continue
            
            iit = itf.GetItem()
            if not iit:
                continue
            
            tp = dlgmakenew.GetType(iit.m_Shape)
            if TYPE2OBJECT.get(tp, '') == '\xa4\xd1\xb4\xb9\xa5\xdb':
                tjCount += 1
                tjShape.append(iit.m_Shape)
                continue
        
        if tjCount == 1:
            return True
        elif tjCount == 2:
            if tjShape[0] != tjShape[1]:
                return False
            
            return True
        
        return False

    
    def OnItemClick(self, pos):
        import combmacro
        self.m_LastClick = pos
        if pos in self.m_InterfaceItem:
            sel_itf = self.m_InterfaceItem[pos]
            if sel_itf.IsSelected():
                if self.m_InputItems[0] and self.m_InputItems[0].m_Pos == pos:
                    sel_itf.Select(False)
                    self.m_InputItems[0] = None
                elif self.m_InputItems[1] and self.m_InputItems[1].m_Pos == pos:
                    sel_itf.Select(False)
                    self.m_InputItems[1] = None
                
                if self.m_InputItems[0] or self.m_InputItems[1]:
                    if self.IsQuickComp(self.m_InputItems):
                        self.SwitchBtn(2)
                    else:
                        self.SwitchBtn(1)
                else:
                    self.SwitchBtn(0)
                return sel_itf
            
            if sel_itf.GetItem() is None:
                return None
            
            if self.m_InputItems[0] is None:
                input_index = 0
            elif self.m_InputItems[1] is None:
                input_index = 1
            else:
                return None
            sel_itf.Select(True)
            (x, y, _, _) = combmacro.GetIFObjectData(self, 'box_make', 0, input_index)
            new_itf = self.m_ItemStyle(self, x, y, 100 + pos)
            new_itf.Refresh(pos)
            new_itf.SetPos(x, y)
            self.m_InputItems[input_index] = new_itf
            self.ShowComp(None)
            if self.IsQuickComp(self.m_InputItems):
                self.SwitchBtn(2)
            else:
                self.SwitchBtn(1)
            return sel_itf
        

    
    def OnCompose(self, shape, amount, desc):
        import combmacro
        obj = self.GetObject('box_result')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        for itf in (self.m_InputItems[0], self.m_InputItems[1]):
            if itf:
                self.m_InterfaceItem[itf.m_Pos].Select(False)
                (ix, iy) = itf.GetPos()
                (iw, ih) = itf.GetSize()
                xstep = (x + (w - iw) / 2 - ix) / 30
                ystep = (y + (h - ih) / 2 - iy) / 30
                itf.m_PosList = [ (ix + xstep * i, iy + ystep * i) for i in range(29, 0, -1) ]
                itf.m_ItemImg.SetAlpha(207)
                itf.Enable(False)
                itf.ShowDisabledBackground(False)
                self.ShowMoveObj(itf)
                continue
            []
        
        self.m_InputItems = {
            0: None,
            1: None }
        self.SwitchBtn(0)
        its = self.m_InterfaceItem[self.m_LastClick].GetItem()
        if its and its.m_Quantity >= 2:
            self.OnItemClick(self.m_LastClick)
        
        self.ShowComp((shape, amount, desc))
        self.CheckValid()

    
    def CheckValid(self):
        pass

    
    def OnCashChg(self):
        if not self.GetObject('money'):
            return None
        
        import hero
        import misc
        cash = hero.g_Prop.m_Cash
        cashStr = misc.ChangeMoney(str(cash))
        if hasattr(self, 'm_CostData') and self.m_CostData:
            (_, cost, _) = self.m_CostData
            txt = '%d/%s' % (cost, cashStr)
        else:
            cost = -1
            txt = '%s' % cashStr
        if cost <= cash:
            color = interface.COLOR_5
        else:
            color = 16711680
        import combmacro
        self.m_Money = combmacro.CTEXT(interface.CTextObject, 'money', self, txt, interface.FontLT14_3, color, 0, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)

    
    def OnHuoliChg(self):
        if not self.GetObject('huoli'):
            return None
        
        import hero
        huoli = hero.g_Prop.m_Huoli
        self.m_Huoli = None
        if not hasattr(self, 'm_CostData') or not (self.m_CostData):
            return None
        
        (cost, _, _) = self.m_CostData
        txt = '%d/%d' % (cost, huoli)
        if cost <= huoli:
            color = interface.COLOR_5
        else:
            color = 16711680
        import combmacro
        self.m_Huoli = combmacro.CTEXT(interface.CTextObject, 'huoli', self, txt, interface.FontLT14_3, color, 0, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)

    
    def OnCostChg(self, ihuoli, iMoney, sklv):
        if not self.GetObject('money') and self.GetObject('huoli'):
            return None
        
        self.m_CostData = (ihuoli, iMoney, sklv)
        self.OnCashChg()
        self.OnHuoliChg()

    
    def DoComposeCommit(self, func):
        import misc
        t = misc.Time()
        if t - self.m_LastCommit < 0.05:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xa3\xadn\xbe\xde\xa7@\xa4\xd3\xa7\xd6')
            return None
        
        self.m_LastCommit = t
        lst = []
        if self.m_InputItems[0] and self.m_InputItems[0].GetItem():
            lst.append(self.m_InputItems[0].GetItem().m_ID)
        
        if self.m_InputItems[1] and self.m_InputItems[1].GetItem():
            lst.append(self.m_InputItems[1].GetItem().m_ID)
        
        if lst:
            lst.append(0)
            import sounddefine
            import sound
            sound.Play(sounddefine.PATH_MAKEEQUIP_SOUND)
            func(self.m_Mode, lst[0], lst[1])
        

    
    def DoCompose(self):
        import nethero
        self.DoComposeCommit(nethero.C2SCompose)

    
    def DoQuickCompose(self):
        import nethero
        self.DoComposeCommit(nethero.C2SQuickCompose)

    
    def OnCloseWindow(self):
        import soundmgr
        oMgr = soundmgr.GetSoundMgr()
        oMgr.SetPathState('action/diamondtake.wav', True)
        self.DelInterfaceItem()
        Show(0)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.OnCloseWindow()
        elif msgid == 2:
            self.DoCompose()
        elif msgid == 3:
            self.DoQuickCompose()
        elif msgid % interface.RIGHT_BUTTON_MESSAGE - 100 in self.m_InterfaceItem:
            self.OnItemClick(msgid % interface.RIGHT_BUTTON_MESSAGE - 100)
        else:
            print 'CComposeDlg::OnMessage', msgid



class CGemCompDlg(CComposeDlg):
    ITEM2TIPS = {
        '\xc4_\xa5\xdb': '\xa6X\xa6\xa8\xa1G\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xc4_\xa5\xdb\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xb9\xef\xc0\xb3\xc3\xfe\xab\xac\xaa\xba\xc4_\xa5\xdb#r\xa4@\xc1\xe4\xa6X\xa6\xa8\xa1G\xb1N\xa9\xf1\xa4J\xaa\xba\xa9\xd2\xa6\xb3\xc4_\xa5\xdb\xa5\xfe\xb3\xa1\xa6X\xa6\xa8\xac\xb0\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xb9\xef\xc0\xb3\xc3\xfe\xab\xac\xaa\xba\xc4_\xa5\xdb',
        '\xa4\xd1\xb4\xb9\xa5\xdb': '\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xa4\xd1\xb4\xb9\xa5\xdb\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xa4\xd1\xb4\xb9\xa5\xdb\xa1A#B\xb5\xf9\xa1G\xa4@\xc1\xfb\xa4\xd1\xb4\xb9\xa5\xdb\xa1P\xa2\xbe\xc1\xd9\xa5i\xbbP\xa4@\xc1\xfb\xa4\xd1\xb4\xb9\xa5\xdb\xa1P\xa2\xbd\xa6X\xa6\xa8\xac\xb0\xa4@\xc1\xfb\xa4\xd1\xb4\xb9\xa5\xdb\xa1P\xa2\xbf#n',
        '\xa8\xe2\xbb\xf6\xa5\xdb': '\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xa8\xe2\xbb\xf6\xa5\xdb\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xa8\xe2\xbb\xf6\xa5\xdb\xa1A#B\xb5\xf9\xa1G\xa4@\xc1\xfb\xa8\xe2\xbb\xf6\xa5\xdb\xa1P\xa2\xbe\xc1\xd9\xa5i\xbbP\xa4@\xc1\xfb\xa8\xe2\xbb\xf6\xa5\xdb\xa1P\xa2\xbd\xa6X\xa6\xa8\xac\xb0\xa4@\xc1\xfb\xa8\xe2\xbb\xf6\xa5\xdb\xa1P\xa2\xbf#n',
        '\xa4K\xa8\xf6\xafu\xae\xf0': '4\xa5\xf7\xab~\xbd\xe8\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xa4K\xa8\xf6\xafu\xae\xf0\xa5i\xa5H\xbf\xc4\xa6X\xb4\xa3\xaf\xc2\xa6\xa81\xa5\xf7\xa7\xf3\xb0\xaa\xab~\xbd\xe8\xaa\xba\xb9\xef\xc0\xb3\xc3\xfe\xab\xac\xaa\xba\xa4K\xa8\xf6\xafu\xae\xf0\xa1A\xa9\xf1\xa4J\xa4@\xad\xd3\xa4K\xa8\xf6\xafu\xae\xf0\xab\xe1\xa5i\xa6\xdb\xb0\xca\xa4\xc7\xb0t\xa6\xe6\xc5n\xa4\xba\xa8\xe4\xa5L\xa6P\xc3\xfe\xafu\xae\xf0\xb6i\xa6\xe6\xa6X\xa6\xa8',
        '\xad\xab\xb3y\xba\xeb\xb5\xd8': '\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa1A#B\xb5\xf9\xa1G\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa1P\xa2\xbe\xc1\xd9\xa5i\xbbP\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa2\xbf\xa1P\xa6X\xa6\xa8\xac\xb0\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa1P\xa2\xc0\xa1F\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa1P\xa2\xbd\xc1\xd9\xa5i\xbbP\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa1P\xa2\xc0\xa1P\xa6X\xa6\xa8\xac\xb0\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xba\xeb\xb5\xd8\xa1P\xa2\xc1#n',
        '\xc4_\xa5\xdb\xa5]': '\xa6X\xa6\xa8\xa1G\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6p\xb7N\xc4_\xa5\xdb\xa5]\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xa6p\xb7N\xc4_\xa5\xdb\xa5]\xa1C#r\xa4@\xc1\xe4\xa6X\xa6\xa8\xa1G\xb1N\xa9\xf1\xa4J\xaa\xba\xa9\xd2\xa6\xb3\xa6p\xb7N\xc4_\xa5\xdb\xa5]\xa5\xfe\xb3\xa1\xa6X\xa6\xa8\xac\xb0\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xa6p\xb7N\xc4_\xa5\xdb\xa5]#r\xb5\xf9\xa1G\xa6p\xb7N\xc4_\xa5\xdb\xa5]\xb3\xcc\xb0\xaa\xa5u\xaf\xe0\xa6X\xa6\xa8\xa8\xec8\xaf\xc5',
        '\xad\xdf\xaf\xab\xa4Y': '3\xad\xd3\xa4p\xad\xdf\xaf\xab\xa4Y\xa5i\xa5H\xa6X\xa6\xa81\xad\xd3\xad\xdf\xaf\xab\xa4Y\xa1A\xa9\xf1\xa4J\xa4@\xad\xd3\xa4p\xad\xdf\xaf\xab\xa4Y\xab\xe1\xa5i\xa6\xdb\xb0\xca\xa4\xc7\xb0t\xa6\xe6\xc5n\xa4\xba\xa8\xe4\xa5\xa6\xa6P\xc3\xfe\xaa\xba\xa4p\xad\xdf\xaf\xab\xa4Y\xb6i\xa6\xe6\xa6X\xa6\xa8',
        '\xafu\xae\xf0\xa4f\xb3U': '\xa6X\xa6\xa8\xa1G4\xad\xd3\xab~\xbd\xe8\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa4K\xa8\xf6\xafu\xae\xf0\xa4f\xb3U\xa5i\xa5H\xa6X\xa6\xa81\xad\xd3\xa7\xf3\xb0\xaa\xab~\xbd\xe8\xaa\xba\xa4K\xa8\xf6\xafu\xae\xf0\xa4f\xb3U#r\xa4@\xc1\xe4\xa6X\xa6\xa8\xa1G\xb1N\xa9\xf1\xa4J\xaa\xba\xa9\xd2\xa6\xb3\xafu\xae\xf0\xa4f\xb3U\xa5\xfe\xb3\xa1\xa6X\xa6\xa8\xac\xb0\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xafu\xae\xf0\xa4f\xb3U',
        '\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL': '\xa8C3\xad\xd3\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL\xa5i\xa5H\xa6X\xa6\xa81\xad\xd3\xb0\xa3\xc5]\xc3\xb9\xbdL\xa1A\xa9\xf1\xa4J\xa4@\xad\xd3\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL\xab\xe1\xa5i\xa6\xdb\xb0\xca\xa4\xc7\xb0t\xa6\xe6\xc5n\xa4\xba\xa8\xe4\xa5\xa6\xa6P\xc3\xfe\xaa\xba\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL\xb6i\xa6\xe6\xa6X\xa6\xa8' }
    
    def __init__(self, mode, bPlaySound = True):
        CComposeDlg.__init__(self, mode, bPlaySound)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xaa\xab\xab~')
        self.CheckValid()

    
    def CreateInterfaceItem(self):
        import hero
        import combmacro
        import dlgmakenew1
        self.m_InterfaceItem = { }
        self.m_ItemStyle = dlgmakenew1.CInterfaceItemWithLevel
        item.AddInterfaceCallback(self.m_InterfaceItem, oRefObj = self)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_items1', self, item.ITEM_START, self.m_InterfaceItem, 100, 1)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_fight', self, item.ITEM_FIGHT_START, self.m_InterfaceItem, 100, 1)
        combmacro.CITEMAREA(self.m_ItemStyle, 'area_items2', self, item.ITEM_SCOPE, self.m_InterfaceItem, 100, 1)
        limit = item.ITEM_SCOPE + hero.g_Prop.m_BagMax
        for i in range(item.ITEM_SCOPE, item.ITEM_SCOPE + 40):
            it = self.m_InterfaceItem[i]
            it.Enable(i < limit)
            func = {
                True: self.DelBg,
                False: self.CreateBg }[i < limit]
            func(it)
        

    
    def OnSelectNew(self, new_item):
        import dlgmakenew
        import netnpc
        tp = dlgmakenew.GetType(new_item.m_Shape)
        key = dlgmakenew.TYPE2OBJECT.get(tp)
        self.ShowDesc(self.ITEM2TIPS.get(key))
        if key in ('\xc4_\xa5\xdb', '\xc4_\xa5\xdb\xa5]', '\xad\xdf\xaf\xab\xa4Y'):
            ids = []
            if self.m_InputItems[0] and self.m_InputItems[0].GetItem():
                ids.append(self.m_InputItems[0].GetItem().m_ID)
            
            if self.m_InputItems[1] and self.m_InputItems[1].GetItem():
                ids.append(self.m_InputItems[1].GetItem().m_ID)
            
            ids.append(0)
            netnpc.C2SGetMakeCost(1, ids[:2])
        
        self.m_CostData = None
        self.OnCashChg()
        self.OnHuoliChg()

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            if new_itf.IsSelected():
                new_item = new_itf.GetItem()
                if new_item:
                    self.OnSelectNew(new_item)
                
            elif self.m_InputItems[0] is None and self.m_InputItems[1] is None:
                self.m_CostData = None
                self.OnCashChg()
                self.OnHuoliChg()
                self.ShowDesc(None)
            elif self.m_InputItems[0]:
                sel_itf = self.m_InputItems[0]
            elif self.m_InputItems[1]:
                sel_itf = self.m_InputItems[1]
            
            if sel_itf.GetItem():
                self.OnSelectNew(sel_itf.GetItem())
            
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            cur_itf = self.m_InterfaceItem[self.m_InputItems[0].m_Pos]
        elif self.m_InputItems[1]:
            cur_itf = self.m_InterfaceItem[self.m_InputItems[1].m_Pos]
        else:
            cur_itf = None
        import hero
        import dlgmakenew
        if self.m_InputItems[0] and self.m_InputItems[1]:
            enable_type = ()
        elif cur_itf:
            enable_type = (dlgmakenew.GetType(cur_itf.GetItem().m_Shape),)
        else:
            dct = dlgmakenew.OBJECT2TYPE
            enable_type = [ dct.get(key, -1) for key in ('\xa4\xd1\xb4\xb9\xa5\xdb', '\xc4_\xa5\xdb', '\xa4K\xa8\xf6\xafu\xae\xf0', '\xad\xab\xb3y\xba\xeb\xb5\xd8', '\xc4_\xa5\xdb\xa5]', '\xad\xdf\xaf\xab\xa4Y', '\xafu\xae\xf0\xa4f\xb3U', '\xa4p\xb0\xa3\xc5]\xc3\xb9\xbdL') ]
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            bEnable = False
            if iit is None:
                bEnable = True
            elif itf.IsSelected():
                bEnable = True
            elif self.IsTianJingShi(iit.m_Shape):
                bEnable = False
            elif enable_type:
                tp = dlgmakenew.GetType(iit.m_Shape)
                if tp in enable_type:
                    pass
                bEnable = self.OnCheckItem(iit, cur_itf, dlgmakenew.TYPE2OBJECT.get(tp, 0))
            else:
                bEnable = False
            itf.Enable(bEnable)
            func = {
                True: self.DelBg,
                False: self.CreateBg }[bEnable]
            func(itf)
        

    
    def IsTianJingShi(self, ishape):
        if ishape <= ishape:
            pass
        elif ishape <= 30388:
            return True
        

    
    def OnCheckItem(self, itemobj, curr_itemobj, tp):
        if tp and curr_itemobj and curr_itemobj.GetItem():
            if tp in ('\xa4K\xa8\xf6\xafu\xae\xf0', '\xad\xdf\xaf\xab\xa4Y'):
                return True
            
            shape = curr_itemobj.GetItem().m_Shape
            if tp == '\xa4\xd1\xb4\xb9\xa5\xdb':
                dct = {
                    30385: (30385, 30386),
                    30386: (30385,) }
                return itemobj.m_Shape in dct.get(shape, (shape,))
            
            import misc
            if tp == '\xa8\xe2\xbb\xf6\xa5\xdb' and misc.IsTWServer():
                dct = {
                    26865: 26866,
                    26866: 26865 }
                return itemobj.m_Shape == dct.get(shape, shape)
            
            if tp == '\xad\xab\xb3y\xba\xeb\xb5\xd8':
                shape2level = {
                    70611: 1,
                    70612: 2,
                    30471: 3,
                    30411: 3,
                    70613: 3,
                    30472: 4,
                    30412: 4,
                    70614: 4,
                    30473: 5,
                    30413: 5,
                    70615: 5,
                    30414: 6,
                    70616: 6,
                    30474: 7,
                    70617: 7,
                    30415: 7,
                    30416: 8,
                    70618: 8 }
                lv = shape2level.get(shape)
                cur_lv = shape2level.get(itemobj.m_Shape)
                dct = {
                    5: (5, 8),
                    6: (6, 7),
                    7: (6,),
                    8: (5,) }
                return cur_lv in dct.get(lv, (lv,))
            
            if tp == '\xc4_\xa5\xdb':
                return itemobj.m_Shape == shape
            
            if tp == '\xc4_\xa5\xdb\xa5]':
                import itemdata
                (name, _) = itemdata.GetData(itemobj.m_Shape)
                (curr_name, _) = itemdata.GetData(shape)
                if name in ('\xa4K\xaf\xc5\xa6p\xb7N\xc4_\xa5\xdb\xa5]',):
                    return False
                
                return name == curr_name
            
            if tp == '\xafu\xae\xf0\xa4f\xb3U':
                shape2level = {
                    73540: 1,
                    73541: 1,
                    73542: 2,
                    73543: 2,
                    73544: 3,
                    73545: 3,
                    73546: 4,
                    73547: 4 }
                lv = shape2level.get(shape)
                cur_lv = shape2level.get(itemobj.m_Shape)
                dct = {
                    1: (1,),
                    2: (2,),
                    3: (3,),
                    4: (4,) }
                return cur_lv in dct.get(lv, (lv,))
            
        
        if tp == '\xc4_\xa5\xdb\xa5]':
            import itemdata
            (name, _) = itemdata.GetData(itemobj.m_Shape)
            if name in ('\xa4K\xaf\xc5\xa6p\xb7N\xc4_\xa5\xdb\xa5]',):
                return False
            
        
        return True



class CRemakeDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xad\xab\xb3y\xba\xeb\xb5\xd8')
        self.CheckValid()
        self.ShowDesc('\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa1A#B\xb5\xf9\xa1G\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa1P\xa2\xbf\xc1\xd9\xa5i\xbbP\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa1P\xa2\xbe\xa6X\xa6\xa8\xac\xb0\xa4@\xc1\xfb\xb8\xcb\xb3\xc6\xad\xab\xb3y\xba\xeb\xb5\xd8\xa1P\xa2\xc0')

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        Shape2Level = {
            70611: 1,
            70612: 2,
            30471: 3,
            30411: 3,
            70613: 3,
            30472: 4,
            30412: 4,
            70614: 4,
            30473: 5,
            30413: 5,
            70615: 5,
            30414: 6,
            70616: 6,
            30474: 7,
            70617: 7,
            30415: 7,
            30416: 8,
            70618: 8 }
        if self.m_InputItems[0] and self.m_InputItems[1]:
            enable_level = ()
        elif self.m_InputItems[0]:
            level = Shape2Level[self.m_InputItems[0].GetItem().m_Shape]
            if level in (6, 7):
                enable_level = (6, 7)
            else:
                enable_level = (level,)
        elif self.m_InputItems[1]:
            level = Shape2Level[self.m_InputItems[1].GetItem().m_Shape]
            if level in (6, 7):
                enable_level = (6, 7)
            else:
                enable_level = (level,)
        else:
            enable_level = (1, 2, 3, 4, 5, 6, 7, 8)
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if iit is None and itf.IsSelected() or Shape2Level.get(iit.m_Shape) in enable_level:
                itf.Enable(True)
                self.DelBg(itf)
                continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



class CBaguaDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xa4K\xa8\xf6\xafu\xae\xf0')
        self.m_Shape2Name = {
            70464: '\xa4K\xa8\xf6\xa1P\xa7\xa2\xae\xf0',
            70465: '\xa4K\xa8\xf6\xa1P\xa6\xe1\xae\xf0\xa1]g\xa1@n\xa1^',
            70466: '\xa4K\xa8\xf6\xa1P\xa9[\xae\xf0',
            26875: '\xa4K\xa8\xf6\xa1P\xb4S\xae\xf0\xa1]x\xa1@n\xa1^',
            26876: '\xa4K\xa8\xf6\xa1P\xa7\xa2\xae\xf0',
            26877: '\xa4K\xa8\xf6\xa1P\xa6\xe1\xae\xf0\xa1]g\xa1@n\xa1^',
            26878: '\xa4K\xa8\xf6\xa1P\xa9[\xae\xf0',
            26871: '\xa4K\xa8\xf6\xa1P\xb0\xae\xae\xf0',
            26872: '\xa4K\xa8\xf6\xa1P\xa7I\xae\xf0',
            26873: '\xa4K\xa8\xf6\xa1P\xc2\xf7\xae\xf0',
            26874: '\xa4K\xa8\xf6\xa1P\xbe_\xae\xf0',
            70459: '\xa4K\xa8\xf6\xa1P\xb0\xae\xae\xf0',
            70460: '\xa4K\xa8\xf6\xa1P\xa7I\xae\xf0',
            70461: '\xa4K\xa8\xf6\xa1P\xc2\xf7\xae\xf0',
            70462: '\xa4K\xa8\xf6\xa1P\xbe_\xae\xf0',
            70463: '\xa4K\xa8\xf6\xa1P\xb4S\xae\xf0\xa1]x\xa1@n\xa1^' }
        self.ShowDesc('4\xa5\xf7\xab~\xbd\xe8\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xa4K\xa8\xf6\xafu\xae\xf0\xa5i\xa5H\xbf\xc4\xa6X\xb4\xa3\xaf\xc2\xa6\xa81\xa5\xf7\xa7\xf3\xb0\xaa\xab~\xbd\xe8\xaa\xba\xb9\xef\xc0\xb3\xc3\xfe\xab\xac\xaa\xba\xa4K\xa8\xf6\xafu\xae\xf0\xa1A\xa9\xf1\xa4J\xa4@\xad\xd3\xa4K\xa8\xf6\xafu\xae\xf0\xab\xe1\xa5i\xa6\xdb\xb0\xca\xa4\xc7\xb0t\xa6\xe6\xc5n\xa4\xba\xa8\xe4\xa5L\xa6P\xc3\xfe\xafu\xae\xf0\xb6i\xa6\xe6\xa6X\xa6\xa8')
        self.CheckValid()

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_name = self.m_Shape2Name[self.m_InputItems[0].GetItem().m_Shape]
        elif self.m_InputItems[1]:
            sel_name = self.m_Shape2Name[self.m_InputItems[1].GetItem().m_Shape]
        else:
            sel_name = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if iit is None and itf.IsSelected() or iit.m_Shape in self.m_Shape2Name:
                if sel_name is None or sel_name == self.m_Shape2Name[iit.m_Shape]:
                    itf.Enable(True)
                    self.DelBg(itf)
                    continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



class CTJCDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        captionStr = {
            6: '\xb4\xa3\xaf\xc2\xa4\xd1\xaa\xf7\xb2f',
            7: '\xa6X\xa6\xa8\xa4\xd1\xaa\xf7\xb2f' }
        self.GetObject('noname0').ChgCaptionTxt(captionStr[mode])
        self.m_Shape2Name = {
            26904: '\xa4p\xa4\xd1\xaa\xf7\xb2f',
            26905: '\xa4\xd1\xaa\xf7\xb2f',
            26906: '\xa4j\xa4\xd1\xaa\xf7\xb2f',
            70467: '\xa4p\xa4\xd1\xaa\xf7\xb2f',
            30117: '\xa4p\xa4\xd1\xaa\xf7\xb2f',
            30118: '\xa4\xd1\xaa\xf7\xb2f',
            30119: '\xa4j\xa4\xd1\xaa\xf7\xb2f',
            30154: '\xa4\xd1\xaa\xf7\xb2f' }
        self.CheckValid()
        descStr = {
            6: '2\xa5\xf7\xac\xdb\xa6P\xa4j\xa4p\xa1B\xac\xdb\xa6P\xb5\xa5\xaf\xc5\xaa\xba\xa4\xd1\xaa\xf7\xb2f\xa5i\xa5H\xb4\xa3\xaf\xc2\xa5X1\xa5\xf7\xa4j\xa4p\xa4\xa3\xc5\xdc\xa1A\xb5\xa5\xaf\xc5\xa7\xf3\xb0\xaa\xa4@\xaf\xc5\xaa\xba\xa4\xd1\xaa\xf7\xb2f',
            7: '2\xa5\xf7\xac\xdb\xa6P\xa4j\xa4p\xa1B\xac\xdb\xa6P\xb5\xa5\xaf\xc5\xaa\xba\xa4\xd1\xaa\xf7\xb2f\xa5i\xa5H\xa6X\xa6\xa8\xa5X1\xa5\xf7\xb5\xa5\xaf\xc5\xa4\xa3\xc5\xdc\xa1A\xa4j\xa4p\xa7\xf3\xb0\xaa\xa4@\xaf\xc5\xaa\xba\xa4\xd1\xaa\xf7\xb2f' }
        self.ShowDesc(descStr[mode])

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_name = self.m_Shape2Name[self.m_InputItems[0].GetItem().m_Shape]
        elif self.m_InputItems[1]:
            sel_name = self.m_Shape2Name[self.m_InputItems[1].GetItem().m_Shape]
        else:
            sel_name = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if iit is None and itf.IsSelected() or iit.m_Shape in self.m_Shape2Name:
                if sel_name is None or sel_name == self.m_Shape2Name[iit.m_Shape]:
                    itf.Enable(True)
                    self.DelBg(itf)
                    continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



class CEyeCompDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xa4d\xa8\xbd\xb2\xb4')
        self.CheckValid()
        self.ShowDesc('\xa8\xe2\xad\xd3\xad@\xa4[\xab\xd7\xb3\xa3\xa4\xa3\xac\xb00\xaa\xba\xa4d\xa8\xbd\xb2\xb4\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xb7s\xaa\xba\xa4d\xa8\xbd\xb2\xb4\xa1A\xa6X\xa6\xa8\xa4\xa7\xab\xe1\xb7s\xaa\xba\xa4d\xa8\xbd\xb2\xb4\xad@\xa4[\xab\xd7\xac\xb0\xa6X\xa6\xa8\xa9\xd2\xa5\xce\xa8\xe2\xad\xd3\xa4d\xb8\xcc\xb2\xb4\xaa\xba\xad@\xa4[\xab\xd7\xa4\xa7\xa9M#B\xb5\xf9\xa1G\xad@\xa4[\xab\xd7\xac\xb00\xaa\xba\xa4d\xa8\xbd\xb2\xb4\xa4\xa3\xa4\xb9\xb3\\\xa6X\xa6\xa8\xa1A\xa6X\xa6\xa8\xad@\xa4[\xa4W\xad\xad\xac\xb0200#n')

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        if self.m_InputItems[0] and self.m_InputItems[1]:
            input_amount = 2
        elif self.m_InputItems[0] or self.m_InputItems[1]:
            input_amount = 1
        else:
            input_amount = 0
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if (iit is None and itf.IsSelected() or input_amount < 2) and iit.m_Shape == 25439:
                itf.Enable(True)
                self.DelBg(itf)
                continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



class CCrystalDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xc5]\xaak\xa4\xf4\xb4\xb9')
        self.m_Shape2Name = {
            25737: '\xc5]\xaak\xa4\xf4\xb4\xb9\xb8H\xa4\xf9',
            25738: '\xc5]\xaak\xa4\xf4\xb4\xb9' }
        self.CheckValid()
        self.ShowDesc('\xa8\xe2\xad\xd3\xb5\xa5\xaf\xc5\xac\xdb\xa6P\xaa\xba\xa6P\xc3\xfe\xc5]\xaak\xa4\xf4\xb4\xb9\xa5i\xa5H\xa6X\xa6\xa8\xa4@\xad\xd3\xa7\xf3\xb0\xaa\xb5\xa5\xaf\xc5\xaa\xba\xc5]\xaak\xa4\xf4\xb4\xb9')

    
    def OnItemClick(self, pos):
        if getattr(self.m_InterfaceItem[pos].GetItem(), 'm_Shape', None) not in self.m_Shape2Name:
            return None
        
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_name = self.m_Shape2Name[self.m_InputItems[0].GetItem().m_Shape]
        elif self.m_InputItems[1]:
            sel_name = self.m_Shape2Name[self.m_InputItems[1].GetItem().m_Shape]
        else:
            sel_name = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if iit is None and itf.IsSelected() or iit.m_Shape in self.m_Shape2Name:
                if sel_name is None or sel_name == self.m_Shape2Name[iit.m_Shape]:
                    itf.Enable(True)
                    self.DelBg(itf)
                    continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        

    
    def OnCompose(self, shape, amount, desc):
        CComposeDlg.OnCompose(self, shape, amount, desc)
        num = item.GetItemNum(25737)
        if shape == 25738 and num <= 1:
            for pos in self.m_InterfaceItem:
                iit = self.m_InterfaceItem[pos].GetItem()
                if iit is not None and iit.m_Shape == 25738:
                    self.m_InterfaceItem[pos].SetItemByPos(pos)
                    self.OnItemClick(pos)
                    self.CheckValid()
                    return None
                    continue
            
        



class CIceBallDlg(CComposeDlg):
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.GetObject('noname0').ChgCaptionTxt('\xa6X\xa6\xa8\xb3\xb7\xb2y')
        self.m_Shape2Name = {
            10031: '\xa4p\xb3\xb7\xb2y',
            10032: '\xa4\xa4\xb3\xb7\xb2y',
            10443: '\xa4p\xb3\xb7\xb2y',
            10444: '\xa4\xa4\xb3\xb7\xb2y' }
        self.CheckValid()
        self.ShowDesc('1 \xa8\xe2\xad\xd3\xa6P\xb5\xa5\xaf\xc5\xb3\xb7\xb2y\xa5i\xa5H\xa6X\xa6\xa8\xac\xb0\xb0\xaa\xa4@\xaf\xc5\xaa\xba\xb3\xb7\xb2y\xa1C#r2 \xb3\xb7\xb2y\xa5i\xa5H\xb3\xcc\xb0\xaa\xa6X\xa6\xa8\xa8\xec\xa4T\xaf\xc5\xa1C')

    
    def OnItemClick(self, pos):
        if getattr(self.m_InterfaceItem[pos].GetItem(), 'm_Shape', None) not in self.m_Shape2Name:
            return None
        
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        return new_itf

    
    def IsQuickComp(self, dct):
        if self.m_InputItems[0] or self.m_InputItems[1]:
            return True
        
        return False

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_name = self.m_Shape2Name[self.m_InputItems[0].GetItem().m_Shape]
        elif self.m_InputItems[1]:
            sel_name = self.m_Shape2Name[self.m_InputItems[1].GetItem().m_Shape]
        else:
            sel_name = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if iit is None and itf.IsSelected() or iit.m_Shape in self.m_Shape2Name:
                if sel_name is None or sel_name == self.m_Shape2Name[iit.m_Shape]:
                    itf.Enable(True)
                    self.DelBg(itf)
                    continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



def GetEffect(shape):
    effect = ''
    if shape in (72185, 72186, 72187):
        effect = '\xc4\xdd\xa9\xca\xaf\xab\xaf\xbe\xa1G'
    elif shape in (72188, 72189, 72190):
        effect = '\xafS\xae\xc4\xaf\xab\xaf\xbe\xa1G'
    
    return effect


class CTattooUpdateDlg(CComposeDlg):
    DIALOG_PATH = 'dialog/composeeffect.dlg'
    CAPTION = '\xa4\xc9\xaf\xc5\xaf\xab\xaf\xbe'
    DESC = '\xa1u\xaf\xab\xaf\xbe\xa2\xb9\xa1v+\xa1u\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5\xa2\xb9\xa1v=\xa6P\xc3\xfe\xab\xac\xaf\xab\xaf\xbe\xa2\xba#r\xa1u\xaf\xab\xaf\xbe\xa2\xba\xa1v+\xa1u\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5\xa2\xba\xa1v=\xa6P\xc3\xfe\xab\xac\xaf\xab\xaf\xbe\xa2\xbb#r\xb5\xa5\xaf\xc5\xb6V\xb0\xaa\xaa\xba\xaf\xab\xaf\xbe\xaa\xba\xaa\xfe\xa5[\xbc\xc6\xad\xc8\xa4W\xad\xad\xb6V\xb0\xaa#r\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xab\xe1\xa1A\xb1N\xc5\xdc\xac\xb0\xb8j\xa9w\xc4\xdd\xa9\xca'
    s_ShowExtItem = [
        72184,
        72185,
        72186,
        72187,
        72188,
        72189,
        72190]
    s_ExtColor = 5562350
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.m_ValidTattoo = [
            72185,
            72186,
            72187,
            72188,
            72189,
            72190]
        self.m_ValidItem = [
            72180,
            72181]
        self.GetObject('noname0').ChgCaptionTxt(self.CAPTION)
        self.CheckValid()
        self.ShowDesc(self.DESC)
        self.GetObject('btn_commit').SetText('\xa4\xc9\xaf\xc5')

    
    def OnItemClick(self, pos):
        newItf = CComposeDlg.OnItemClick(self, pos)
        if newItf:
            self.CheckValid()
            self.SetNeedItem(newItf)
        
        self.ShowEffect()
        return newItf

    
    def SetNeedItem(self, newItf):
        newItem = newItf.GetItem()
        if newItem.m_Shape not in (72185, 72186, 72187, 72188, 72189, 72190):
            return None
        
        if self.m_InputItems[1] or not self.m_InputItems[0]:
            return None
        
        if self.m_InputItems[0].GetItem() == newItem:
            for pos in self.m_InterfaceItem:
                itf = self.m_InterfaceItem[pos]
                iit = itf.GetItem()
                if not iit:
                    continue
                
                if self.CheckTattoo(iit.m_Shape, newItem):
                    itf.LeftUp()
                    return None
                    continue
            
        

    
    def ShowEffect(self):
        
        def _showeffect(it, shape):
            if hasattr(it, 'm_InfoExt') and it.m_InfoExt:
                effect = GetEffect(shape)
                if it.m_InfoExt.count('#r') > 1:
                    tmptxt = it.m_InfoExt.replace('#r', '#n#r', 2)
                    tmptxt = tmptxt.replace('+', '+#Y', 1)
                    effect += tmptxt
                else:
                    effect += it.m_InfoExt
                if not effect.endswith('#r'):
                    effect += '#r'
                
                import combmacro
                return combmacro.CRICHTEXT(interface.CRichTextObject, 'effect', self, effect, interface.FontLT14_3, interface.COLOR_4)
            else:
                it.AddUpdateCallback(InfoExtCallback, CTattooStrengthenDlg)
                import netitem
                netitem.C2SItemString(it.m_ID, 0)

        if self.m_InputItems[0]:
            it = self.m_InputItems[0].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                self.m_EffectTxt = _showeffect(it, shape)
                return None
            
        
        if self.m_InputItems[1]:
            it = self.m_InputItems[1].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                self.m_EffectTxt = _showeffect(it, shape)
                return None
            
        
        self.m_EffectTxt = None

    
    def SetResultItem(self, id):
        for pos in self.m_InterfaceItem:
            iit = self.m_InterfaceItem[pos].GetItem()
            if iit is not None and iit.m_ID == id:
                self.m_InterfaceItem[pos].SetItemByPos(pos)
                if getattr(iit, 'm_Level', None) in (1, 2):
                    self.OnItemClick(pos)
                    break
                
            getattr(iit, 'm_Level', None) in (1, 2)
        

    
    def CheckTattoo(self, curshape, curitem):
        if curshape is None:
            if curitem.m_Shape in self.m_ValidTattoo or getattr(curitem, 'm_Level', None) in (1, 2) or curitem.m_Shape in self.m_ValidItem:
                return True
            
        elif hasattr(curitem, 'm_Level'):
            if (curitem.m_Level == 1 or curshape == 72180 or curitem.m_Level == 2) and curshape == 72181:
                return True
            
        return False

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_shape = self.m_InputItems[0].GetItem().m_Shape
            curitem = self.m_InputItems[0].GetItem()
        elif self.m_InputItems[1]:
            sel_shape = self.m_InputItems[1].GetItem().m_Shape
            curitem = self.m_InputItems[1].GetItem()
        else:
            sel_shape = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if not iit is None and itf.IsSelected():
                if not sel_shape is None or self.CheckTattoo(sel_shape, iit):
                    if (sel_shape in self.m_ValidTattoo and iit.m_Shape in self.m_ValidItem or self.CheckTattoo(iit.m_Shape, curitem) or sel_shape in self.m_ValidItem) and iit.m_Shape in self.m_ValidTattoo and self.CheckTattoo(sel_shape, iit):
                        itf.Enable(True)
                        self.DelBg(itf)
                        continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        

    
    def OnCompose(self, shape, amount, desc):
        CComposeDlg.OnCompose(self, shape, amount, desc)
        its = self.m_InterfaceItem[self.m_LastClick].GetItem()
        if its and its.m_Shape not in self.m_ValidTattoo and its.m_Quantity >= 2:
            self.OnItemClick(self.m_LastClick)
        
        self.CheckValid()

    
    def DoCompose(self):
        
        def shapecheck(shape = 0):
            import usermacro
            if shape in (72188, 72185):
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5I')
            elif shape in (72189, 72186):
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5II')
            else:
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xa4@\xad\xd3\xaf\xab\xaf\xbe')

        if self.m_Mode == 11:
            if not self.m_InputItems[0] and self.m_InputItems[1]:
                item = self.m_InputItems[1].GetItem()
                shapecheck(item.m_Shape)
            elif not self.m_InputItems[1] and self.m_InputItems[0]:
                item = self.m_InputItems[0].GetItem()
                shapecheck(item.m_Shape)
            elif not self.m_InputItems[1] and not self.m_InputItems[0]:
                shapecheck()
            
        
        import nethero
        self.DoComposeCommit(nethero.C2SCompose)



def AddTattooStrengEffectExt(effectext, id):
    if isinstance(g_Dialog, CTattooStrengthenDlg):
        iits = g_Dialog.m_InputItems
        for iit in iits.values():
            if iit:
                git = iit.GetItem()
                if git.m_ID == id:
                    g_Dialog.AddEffectExt(effectext)
                    return None
                
            git.m_ID == id
        
    


class CTattooStrengthenDlg(CComposeDlg):
    DIALOG_PATH = 'dialog/composeeffect.dlg'
    CAPTION = '\xad\xab\xb8m\xaf\xab\xaf\xbe'
    DESC = '\xa1u\xaf\xab\xaf\xbe\xa2\xb9\xa1v+\xa1u\xbaa\xc5A\xa4\xa7\xa5\xc9X1\xa1v=\xb7s\xaa\xba\xa1u\xaf\xab\xaf\xbe\xa2\xb9\xa1v#r\xa1u\xaf\xab\xaf\xbe\xa2\xba\xa1v+\xa1u\xbaa\xc5A\xa4\xa7\xa5\xc9X2\xa1v=\xb7s\xaa\xba\xa1u\xaf\xab\xaf\xbe\xa2\xba\xa1v#r\xa1u\xaf\xab\xaf\xbe\xa2\xbb\xa1v+\xa1u\xbaa\xc5A\xa4\xa7\xa5\xc9X3\xa1v=\xb7s\xaa\xba\xa1u\xaf\xab\xaf\xbe\xa2\xbb\xa1v#r\xb7s\xaa\xba\xaf\xab\xaf\xbe\xaa\xba\xc3\xfe\xab\xac\xa4\xa3\xc5\xdc\xa1A\xaa\xfe\xa5[\xbc\xc6\xad\xc8\xc5\xdc\xa4\xc6#r\xaf\xab\xaf\xbe\xad\xab\xb8m\xab\xe1\xa1A\xb1N\xc5\xdc\xac\xb0\xb8j\xa9w\xc4\xdd\xa9\xca'
    s_ShowExtItem = [
        72184,
        72185,
        72186,
        72187,
        72188,
        72189,
        72190]
    s_ExtColor = 5562350
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.m_ValidTattoo = [
            72185,
            72186,
            72187,
            72188,
            72189,
            72190]
        self.m_ValidItem = [
            25431,
            30204,
            31204]
        self.GetObject('noname0').ChgCaptionTxt(self.CAPTION)
        self.CheckValid()
        self.m_EffectExt = ''
        self.ShowDesc(self.DESC)
        self.GetObject('btn_commit').SetText('\xad\xab\xb8m')

    
    def OnEnter(self, msgid):
        import dlggetinfo
        if msgid == 2:
            self.m_Tips = dlggetinfo.ShowFakeItem(30204)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def GetMaterialQuantity(self):
        sum = 0
        for shape in (25431, 30204, 31204):
            sum += item.GetItemNum(shape)
        
        return sum

    
    def SetNeedItem(self):
        import combmacro
        import ui
        (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', 0, 1)
        self.m_Material = item.CreateItem44Image(self, 30204, 0)
        self.m_Material.SetPos(x, y)
        self.m_NotifyBox2 = interface.CNotifyBox(self, w, h, 0, 0, 2)
        self.m_NotifyBox2.SetPos(x, y)
        self.m_SelBox2 = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
        self.m_SelBox2.SetPos(x, y)
        self.m_SelBox2.SetZ(1)
        quantity = self.GetMaterialQuantity()
        needQuantity = self.m_Level
        txt = None if needQuantity <= quantity else '#R%d/%d' % (needQuantity, quantity)
        self.m_Material.m_NumTxt = interface.CRichTextObject(self.m_Material, w, interface.FontLT12E_1, txt)
        (tw, th) = self.m_Material.m_NumTxt.GetSize()
        self.m_Material.m_NumTxt.SetPos(w - tw - 3, h - th)
        self.m_Material.m_NumTxt.SetZ(100)

    
    def ClearNeedItem(self):
        self.m_Material = None
        self.m_SelBox = None

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        self.GetEffectExt()
        self.ShowEffect()
        if self.m_InputItems[0]:
            curitem = self.m_InputItems[0].GetItem()
            self.m_Level = curitem.m_Level
            self.SetNeedItem()
        else:
            self.ClearNeedItem()
        return new_itf

    
    def AddEffectExt(self, ext):
        self.m_EffectExt = ext
        self.ShowEffect()

    
    def GetEffectExt(self):
        import nettattoo
        if self.m_InputItems[0]:
            it = self.m_InputItems[0].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                nettattoo.C2SGetEffectExt(it.m_ID, 0)
            
        
        if self.m_InputItems[1]:
            it = self.m_InputItems[1].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                nettattoo.C2SGetEffectExt(it.m_ID, 0)
            
        

    
    def ShowEffect(self):
        
        def _showeffect(it, shape, effectext):
            if hasattr(it, 'm_InfoExt') and it.m_InfoExt:
                effect = GetEffect(shape)
                if it.m_InfoExt.count('#r') > 1:
                    tmptxt = it.m_InfoExt.replace('#r', '#n#r', 2)
                    tmptxt = tmptxt.replace('+', '+#Y', 1)
                    effect += tmptxt
                else:
                    effect += it.m_InfoExt
                if effect.count('#r') >= 1:
                    effect = effect.split('#r')[0] + '#r' + effect.split('#r')[1]
                
                if not effect.endswith('#r'):
                    effect += '#r'
                
                if effectext:
                    effect += effectext
                
                import combmacro
                effect = interface.Replace(effect)
                return combmacro.CRICHTEXT(interface.CRichTextObject, 'effect', self, effect, interface.FontLT14_3, interface.COLOR_4)
            else:
                it.AddUpdateCallback(InfoExtCallback, CTattooStrengthenDlg)
                import netitem
                netitem.C2SItemString(it.m_ID, 0)

        if self.m_InputItems[0]:
            it = self.m_InputItems[0].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                self.m_EffectTxt = _showeffect(it, shape, self.m_EffectExt)
                return None
            
        
        if self.m_InputItems[1]:
            it = self.m_InputItems[1].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                self.m_EffectTxt = _showeffect(it, shape, self.m_EffectExt)
                return None
            
        
        self.m_EffectTxt = None

    
    def SetResultItem(self, id):
        for pos in self.m_InterfaceItem:
            iit = self.m_InterfaceItem[pos].GetItem()
            if iit is not None and iit.m_ID == id:
                self.m_InterfaceItem[pos].SetItemByPos(pos)
                self.OnItemClick(pos)
                break
                continue
        

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_shape = self.m_InputItems[0].GetItem().m_Shape
        elif self.m_InputItems[1]:
            sel_shape = self.m_InputItems[1].GetItem().m_Shape
        else:
            sel_shape = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if (iit is None and itf.IsSelected() or sel_shape is None) and iit.m_Shape in self.m_ValidTattoo:
                itf.Enable(True)
                self.DelBg(itf)
                continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



class CTattooFuseDlg(CComposeDlg):
    DIALOG_PATH = 'dialog/composeeffect.dlg'
    CAPTION = '\xbf\xc4\xa6X\xaf\xab\xaf\xbe'
    DESC = '\xa8\xe2\xad\xd3\xafS\xa7\xde\xaf\xab\xaf\xbe\xa5i\xa5H\xbf\xc4\xa6X\xa6\xa8\xa4@\xad\xd3\xb7s\xaa\xba\xafS\xa7\xde\xaf\xab\xaf\xbe\xa1A\xbf\xc4\xa6X\xab\xe1\xb2\xa3\xa5\xcd\xaa\xba\xafS\xa7\xde\xbbP\xbf\xc4\xa6X\xabe\xa4\xa3\xa6P#r\xb5\xf9\xa1G\xa6p\xaaG\xbf\xc4\xa6X\xaa\xba\xafS\xa7\xde\xaf\xab\xaf\xbe\xa4\xa4\xa6\xb3\xa4@\xad\xd3\xa4w\xbfE\xac\xa1\xa1A\xbf\xc4\xa6X\xab\xe1\xafS\xa7\xde\xaf\xab\xaf\xbe\xaa\xba\xa6\xb3\xae\xc4\xb4\xc1\xac\xb0\xbf\xc4\xa6X\xabe\xa8\xe2\xad\xd3\xafS\xa7\xde\xaf\xab\xaf\xbe\xa6\xb3\xae\xc4\xb4\xc1\xa4\xa7\xa9M\xaa\xba\xa5\xad\xa7\xa1\xad\xc8'
    s_ShowExtItem = [
        72184,
        72185,
        72186,
        72187,
        72188,
        72189,
        72190]
    s_ExtColor = 5562350
    
    def __init__(self, mode):
        CComposeDlg.__init__(self, mode)
        self.m_ValidTattoo = [
            72184]
        self.m_ValidItem = [
            72184]
        self.GetObject('noname0').ChgCaptionTxt(self.CAPTION)
        self.CheckValid()
        self.ShowDesc(self.DESC)
        self.GetObject('btn_commit').SetText('\xbf\xc4\xa6X')

    
    def OnItemClick(self, pos):
        new_itf = CComposeDlg.OnItemClick(self, pos)
        if new_itf:
            self.CheckValid()
        
        self.ShowEffect()
        return new_itf

    
    def ShowEffect(self):
        
        def _effect(it):
            eff = ''
            if hasattr(it, 'm_InfoExt') and it.m_InfoExt:
                eff += '\xafS\xa7\xde\xaf\xab\xaf\xbe\xa1G'
                if it.m_InfoExt.count('#r') > 1:
                    eff += it.m_InfoExt.replace('#r', '\xa1A', 1)
                else:
                    eff += it.m_InfoExt
                if not eff.endswith('#r'):
                    eff += '#r'
                
            else:
                it.AddUpdateCallback(InfoExtCallback, CTattooFuseDlg)
                import netitem
                netitem.C2SItemString(it.m_ID, 0)
            return eff

        effect = ''
        if self.m_InputItems[0]:
            it = self.m_InputItems[0].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                effect += _effect(it)
            
        
        if self.m_InputItems[1]:
            it = self.m_InputItems[1].GetItem()
            shape = it.m_Shape
            if shape in self.m_ValidTattoo:
                effect += _effect(it)
            
        
        if effect != '':
            import combmacro
            self.m_EffectTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'effect', self, effect, interface.FontLT14_3, interface.COLOR_4)
        else:
            self.m_EffectTxt = None

    
    def SetResultItem(self, itemid):
        for pos in self.m_InterfaceItem:
            iit = self.m_InterfaceItem[pos].GetItem()
            
            try:
                iit is not None
                if iit.m_ID == itemid:
                    self.m_InterfaceItem[pos].SetItemByPos(pos)
                    self.OnItemClick(pos)
                    return None
                    continue
            finally:
                return None


    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_shape = self.m_InputItems[0].GetItem().m_Shape
        elif self.m_InputItems[1]:
            sel_shape = self.m_InputItems[1].GetItem().m_Shape
        else:
            sel_shape = None
        import hero
        for pos in self.m_InterfaceItem:
            if pos <= pos:
                pass
            elif pos < item.ITEM_SCOPE + 40:
                continue
            
            itf = self.m_InterfaceItem[pos]
            iit = itf.GetItem()
            if not iit is None and itf.IsSelected():
                if not sel_shape is None or iit.m_Shape in self.m_ValidTattoo + self.m_ValidItem:
                    if (sel_shape in self.m_ValidTattoo or iit.m_Shape in self.m_ValidItem or sel_shape in self.m_ValidItem) and iit.m_Shape in self.m_ValidTattoo:
                        itf.Enable(True)
                        self.DelBg(itf)
                        continue
            item.ITEM_SCOPE + hero.g_Prop.m_BagMax
            itf.Enable(False)
            self.CreateBg(itf)
        



def InfoExtCallback(it, *args):
    (cls,) = args
    if g_Dialog and isinstance(g_Dialog, cls):
        iits = g_Dialog.m_InputItems
        for iit in iits.values():
            if iit:
                git = iit.GetItem()
                if git.m_ID == it.m_ID:
                    g_Dialog.ShowEffect()
                    return None
                
            git.m_ID == it.m_ID
        
    


def SetResultItem(id):
    if hasattr(g_Dialog, 'SetResultItem'):
        g_Dialog.SetResultItem(id)
    


def TattooComp(parent, mode, tattoo = None):
    global g_Dialog, g_Dialog
    import netnpc
    if mode:
        mode2class = {
            11: CTattooLevelUp,
            12: CTattooLevelUp,
            13: CTattooFuse }
        if mode == 13 and isinstance(g_Dialog, CTattooFuse):
            g_Dialog.SetOtherTattoo(tattoo)
            return None
        
        cls = mode2class[mode]
        g_Dialog = cls(parent)
        g_Dialog.SetTattoo(tattoo)
        netnpc.SetMakeCallback(g_Dialog.OnCompose)
        netnpc.SetMakeIDCallback(SetResultItem)
    elif g_Dialog:
        netnpc.SetMakeCallback(None)
    
    g_Dialog = None


class CCompExt(object):
    
    def CheckValid(self):
        for pos in self.m_InterfaceItem:
            itf = self.m_InterfaceItem[pos]
            itf.Enable(False)
            self.CreateBg(itf)
        

    
    def SetTattoo(self, data):
        if data:
            (tid, shape, level, desc, iconid) = data
            self.m_TattooID = tid
            self.m_Shape = shape
            self.m_TattooExt = desc
            self.m_Level = level
            self.CheckValid()
            import combmacro
            import ui
            (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', 0, 0)
            self.m_Tattoo = item.CreateItem44Image(self, shape, 0)
            self.m_Tattoo.SetPos(x, y)
            self.m_NotifyBox = interface.CNotifyBox(self, w, h, 0, 0, 1)
            self.m_NotifyBox.SetPos(x, y)
            self.m_SelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
            self.m_SelBox.SetPos(x, y)
            self.m_SelBox.SetZ(1)
            self.GetObject('btn_commit').SetText(self.CAPTION[:4])
            self.ShowEffect()
            self.SetNeedItem()
            name = desc.split('#')[0]
            self.SetTattooText(name)
        else:
            self.m_Tattoo = None
            self.m_NotifyBox = None
            self.m_SelBox = None
            self.m_Tips = None

    
    def SetTattooText(self, name):
        self.m_ExtNameTextLst = []
        if name:
            txtLst = []
            if len(name) < 8:
                txtLst = [
                    name]
            
            if len(name) == 8:
                txtLst = [
                    name[:4],
                    name[4:]]
            elif len(name) == 10:
                txtLst = [
                    name[:4].ljust(6),
                    name[4:]]
            elif len(name) >= 12:
                txtLst = [
                    name[:6],
                    name[6:]]
            
            hSpace = 28
            for txt in reversed(txtLst):
                obj = interface.CTextObject(self.m_Tattoo, txt, interface.FontLT12E_1, CInterfaceItem.s_ExtColor)
                (w, h) = obj.GetSize()
                obj.SetPos((44 - w) + 2, hSpace)
                obj.SetZ(1000)
                hSpace -= h
                self.m_ExtNameTextLst.append(obj)
            
        

    
    def SetNeedItem(self):
        pass

    
    def UpdateDesc(self, tid, desc):
        if tid == self.m_TattooID:
            self.m_TattooExt = desc
            self.ShowEffect()
            self.SetNeedItem()
        

    
    def ShowEffect(self):
        import itemdata
        desc = '%s\xa1G%s' % (itemdata.GetData(self.m_Shape)[0], self.m_TattooExt)
        if self.m_InputItems[0]:
            input_item = self.m_InputItems[0].GetItem()
            desc += '#r%s' % itemdata.GetData(input_item.m_Shape)[0]
            if input_item.m_InfoExt:
                desc += '\xa1G%s' % input_item.m_InfoExt
            
        
        if hasattr(self, 'm_EffectExt') and self.m_EffectExt:
            desc += '#r%s' % self.m_EffectExt
        
        desc = interface.Replace(desc)
        desc = desc.replace('#r', '#n#r', 2)
        desc = desc.replace('+', '+#Y', 1)
        import combmacro
        self.m_EffectTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'effect', self, desc, interface.FontLT14_3, interface.COLOR_4)

    
    def OnEnter(self, msgid):
        import dlggetinfo
        self.m_Tips = dlggetinfo.ShowFakeItem(self.m_Shape, self.m_TattooExt)

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def OnCompose(self, shape, amount, desc):
        import combmacro
        obj = self.GetObject('box_result')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        igs = self.m_Tattoo
        (ix, iy) = igs.GetPos()
        (iw, ih) = igs.GetSize()
        xstep = (x + (w - iw) / 2 - ix) / 30
        ystep = (y + (h - ih) / 2 - iy) / 30
        igs.m_PosList = [ (ix + xstep * i, iy + ystep * i) for i in range(29, 0, -1) ]
        self.ShowMoveObj(igs)
        self.m_InputItems = {
            0: None,
            1: None }
        self.ShowComp((shape, amount, desc))
        self.SetTattoo((self.m_TattooID, self.m_Shape, 0, self.m_TattooExt, 0))
        self.CheckValid()

    
    def DoCompose(self):
        import nettattoo
        import misc
        t = misc.Time()
        if t - self.m_LastCommit < 0.2:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xa3\xadn\xbe\xde\xa7@\xa4\xd3\xa7\xd6')
            return None
        
        self.m_LastCommit = t
        mode2func = {
            11: nettattoo.C2SUpdateWithID,
            12: nettattoo.C2SStrengthenWithID }
        if self.m_Mode == 11:
            if self.m_InputItems[1]:
                selItem = self.m_InputItems[1].GetItem()
                mode2func[self.m_Mode](self.m_TattooID, selItem.m_ID)
            else:
                import usermacro
                if self.m_Shape in (72188, 72185):
                    usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5I')
                elif self.m_Shape in (72189, 72186):
                    usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xaf\xab\xaf\xbe\xa4\xc9\xaf\xc5\xb2\xc5II')
                
            return None
        
        mode2func[self.m_Mode](self.m_TattooID)



class CUpdateDlg(CCompExt, CTattooUpdateDlg):
    
    def CheckTattoo(self, curshape, itemlevel):
        if (itemlevel == 1 or curshape == 72180 or itemlevel == 2) and curshape == 72181:
            return True
        else:
            return False

    
    def ClearSelect(self):
        for pos in self.m_InterfaceItem:
            itf = self.m_InterfaceItem[pos]
            if itf.IsSelected():
                itf.Select(False)
                continue
        

    
    def SetNeedItem(self):
        self.ClearSelect()
        for pos in self.m_InterfaceItem:
            itf = self.m_InterfaceItem[pos]
            curItem = itf.GetItem()
            if curItem and hasattr(curItem, 'm_Shape') and hasattr(self, 'm_Level') and self.CheckTattoo(curItem.m_Shape, self.m_Level):
                itf.LeftUp()
                return None
                continue
        

    
    def CheckValid(self):
        for pos in self.m_InterfaceItem:
            itf = self.m_InterfaceItem[pos]
            curItem = itf.GetItem()
            if curItem and hasattr(curItem, 'm_Shape') and hasattr(self, 'm_Level') and self.CheckTattoo(curItem.m_Shape, self.m_Level):
                itf.Enable(True)
                self.DelBg(itf)
                continue
            
            itf.Enable(False)
            self.CreateBg(itf)
        

    
    def OnItemClick(self, pos):
        self.m_LastClick = pos
        import combmacro
        if pos in self.m_InterfaceItem:
            sel_itf = self.m_InterfaceItem[pos]
            if sel_itf.IsSelected():
                if self.m_InputItems[1] and self.m_InputItems[1].m_Pos == pos:
                    sel_itf.Select(False)
                    self.m_InputItems[1] = None
                
                if self.m_InputItems[0] or self.m_InputItems[1]:
                    if self.IsQuickComp(self.m_InputItems):
                        self.SwitchBtn(2)
                    else:
                        self.SwitchBtn(1)
                else:
                    self.SwitchBtn(0)
                return sel_itf
            
            if sel_itf.GetItem() is None:
                return None
            
            if self.m_InputItems[1] is None:
                input_index = 1
            else:
                return None
            sel_itf.Select(True)
            (x, y, _, _) = combmacro.GetIFObjectData(self, 'box_make', 0, input_index)
            new_itf = item.CInterfaceItem(self, x, y, 100 + pos)
            new_itf.Refresh(pos)
            new_itf.SetPos(x, y)
            self.m_InputItems[input_index] = new_itf
            self.ShowComp(None)
            if self.IsQuickComp(self.m_InputItems):
                self.SwitchBtn(2)
            else:
                self.SwitchBtn(1)
            return sel_itf
        



class CStrengthenDlg(CCompExt, CTattooStrengthenDlg):
    
    def AddEffectExt(self, tid, ext):
        if tid == self.m_TattooID:
            self.m_EffectExt = ext
            self.ShowEffect()
        

    
    def OnEnter(self, msgid):
        import dlggetinfo
        if msgid == 1:
            self.m_Tips = dlggetinfo.ShowFakeItem(self.m_Shape, self.m_TattooExt)
        elif msgid == 2:
            self.m_Tips = dlggetinfo.ShowFakeItem(30204)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def GetMaterialQuantity(self):
        sum = 0
        for shape in (25431, 30204, 31204):
            sum += item.GetItemNum(shape)
        
        return sum

    
    def SetNeedItem(self):
        CTattooStrengthenDlg.SetNeedItem(self)



class CFuseDlg(CCompExt, CTattooFuseDlg):
    
    def SetTattoo(self, data):
        if data:
            (tid, shape, level, desc, iconid) = data
            self.m_TattooID = tid
            self.m_Shape = shape
            self.m_TattooExt = desc
            self.CheckValid()
            import combmacro
            import ui
            (x, y, w, h) = combmacro.GetIFObjectData(self, 'box_make', 0, 1)
            self.m_Tattoo = item.CreateItem44Image(self, shape, 0)
            self.m_Tattoo.SetPos(x, y)
            self.m_NotifyBox = interface.CNotifyBox(self, w, h, 0, 0, 1)
            self.m_NotifyBox.SetPos(x, y)
            self.m_SelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
            self.m_SelBox.SetPos(x, y)
            self.m_SelBox.SetZ(1)
            self.GetObject('btn_commit').SetText(self.CAPTION[:4])
            self.ShowEffect()
            name = desc.split('(')[0]
            self.SetTattooText(name)
        else:
            self.m_Tattoo = None
            self.m_NotifyBox = None
            self.m_SelBox = None
            self.m_Tips = None
            self.m_TattooID = None
            self.m_Shape = None
            self.m_TattooExt = None

    
    def CheckValid(self):
        if self.m_InputItems[0]:
            sel_itf = self.m_InputItems[0]
            for pos in self.m_InterfaceItem:
                itf = self.m_InterfaceItem[pos]
                iit = itf.GetItem()
                if iit and iit.m_Pos == sel_itf.m_Pos:
                    itf.Enable(True)
                    self.DelBg(itf)
                    continue
                itf.Enable(False)
                self.CreateBg(itf)
            
        else:
            for pos in self.m_InterfaceItem:
                itf = self.m_InterfaceItem[pos]
                iit = itf.GetItem()
                if iit:
                    pass
                itf.Enable(iit.m_Shape == 72184)
                func = None if iit and iit.m_Shape == 72184 else self.CreateBg
                func(itf)
            

    
    def DoCompose(self):
        import nettattoo
        import misc
        import usermacro
        if not self.m_InputItems[0]:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xad\xd3\xafS\xa7\xde\xaf\xab\xaf\xbe')
            return None
        
        t = misc.Time()
        if t - self.m_LastCommit < 0.2:
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xa3\xadn\xbe\xde\xa7@\xa4\xd3\xa7\xd6')
            return None
        
        self.m_LastCommit = t
        sel_iit = self.m_InputItems[0].GetItem()
        nettattoo.C2SFuseWithID(self.m_TattooID, sel_iit.m_ID)



def OnTattooUpdate(tattoo):
    if g_Dialog and isinstance(g_Dialog, (CTattooLevelUp, CTattooFuse)):
        g_Dialog.SetTattoo(tattoo)
        g_Dialog.m_InputItems = {
            0: None,
            1: None }
    


def OnInfoUpdate(tid, desc):
    if g_Dialog and isinstance(g_Dialog, CTattooLevelUp):
        g_Dialog.UpdateDesc(tid, desc)
    


def AddEffectExt(ext, id):
    if g_Dialog and isinstance(g_Dialog, CTattooLevelUp):
        g_Dialog.AddEffectExt(id, ext)
    


def TakeOutTattoo(tid):
    if g_Dialog and isinstance(g_Dialog, (CTattooLevelUp, CTattooFuse)):
        g_Dialog.TakeOutTattoo(tid)
    


class CTattooLevelUp(combdialog.CCombDialog):
    s_SignShape = {
        1: 72180,
        2: 72181,
        3: 0 }
    
    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/tattoolevelup.dlg')
        self.m_NeedItemLst = []
        (w, h) = parent.GetSize()
        (my, mh) = self.GetSize()
        self.SetPos(w - 5, (h - mh) / 2)
        self.m_Condition = {
            0: False,
            1: False }
        self.m_LastCommit = 0
        oModel = mdpropitem.GetModel()
        oModel.ssConnect(oModel.SS_UpdateBagChangeRecommend, self.OnItemChange)

    
    def AddEffectExt(self, tid, ext):
        if tid == self.m_TattooID:
            self.m_WaveExt = ext
            self.ShowEffect('effect_strength', True)
        

    
    def TakeOutTattoo(self, tid):
        if tid == self.m_TattooID:
            self.CloseWindow()
        

    
    def SetResultItem(self, tid):
        if self.GetParent():
            self.GetParent().OnCompose(tid)
        

    
    def OnCompose(self, shape, amount, desc):
        pass

    
    def UpdateDesc(self, tid, desc):
        if tid == self.m_TattooID:
            self.m_TattooExt = desc
            self.SetTattooDefault(self.m_TattooName)
            import nettattoo
            nettattoo.C2SGetEffectExt(tid, 1)
        

    
    def SetTattoo(self, data):
        if data:
            (tid, shape, level, desc, iconid) = data
            self.m_TattooID = tid
            self.m_Shape = shape
            self.m_TattooExt = desc
            self.m_Level = level
            self.SetTattooBox()
            self.m_TattooName = desc.split('#')[0]
            self.SetTattooDefault(self.m_TattooName)
            self.SetNeedItem()
        else:
            self.m_Tattoo = None
            self.m_NotifyBox = None
            self.m_SelBox = None
            self.m_Tips = None

    
    def SetTattooBox(self):
        self.m_BoxLst = []
        for objname in ('tattoolevel', 'tattoostrength'):
            (x, y, w, h) = self.GetLocData(objname)
            tattoo = item.CreateItem44Image(self, self.m_Shape, 0)
            tattoo.SetPos(x, y)
            notifybox = interface.CNotifyBox(self, w, h, 0, 0, 1)
            notifybox.SetPos(x, y)
            self.m_BoxLst.append((tattoo, notifybox))
        

    
    def ShowEffect(self, objname, wavemark = False):
        import itemdata
        desc = '%s\xa1G%s' % (itemdata.GetData(self.m_Shape)[0], self.m_TattooExt)
        if getattr(self, 'm_EffectExt', ''):
            desc += '#r%s' % self.m_EffectExt
        
        if wavemark and getattr(self, 'm_WaveExt', ''):
            if desc.endswith('#r'):
                desc += '%s' % self.m_WaveExt
            else:
                desc += '#r%s' % self.m_WaveExt
        
        desc = self.ReplaceColor(desc)
        import combmacro
        txt = combmacro.CRICHTEXT(interface.CRichTextObject, objname, self, desc, interface.FontLT14_3, interface.COLOR_4)
        self.m_EffectTxt[objname] = txt

    
    def ReplaceColor(self, desc):
        desc = interface.Replace(desc)
        desc = desc.replace('#r', '#n#r', 2)
        desc = desc.replace('+', '+#Y', 1)
        desc = desc.replace('-', '-#Y', 1)
        desc = interface.ReplaceYellow(desc)
        return desc

    
    def SetTattooDefault(self, name):
        self.m_EffectTxt = { }
        self.m_ExtNameTextLst = []
        for objname in ('effect_levelup', 'effect_strength'):
            self.ShowEffect(objname)
        
        for obj, _ in self.m_BoxLst:
            self.SetTattooText(name, obj)
        

    
    def SetTattooText(self, name, boxobj):
        if name:
            txtLst = []
            if len(name) < 8:
                txtLst = [
                    name]
            
            if len(name) == 8:
                txtLst = [
                    name[:4],
                    name[4:]]
            elif len(name) == 10:
                txtLst = [
                    name[:4].ljust(6),
                    name[4:]]
            elif len(name) >= 12:
                txtLst = [
                    name[:6],
                    name[6:]]
            
            hSpace = 28
            for txt in reversed(txtLst):
                obj = interface.CTextObject(boxobj, txt, interface.FontLT12E_1, CInterfaceItem.s_ExtColor)
                (w, h) = obj.GetSize()
                obj.SetPos((44 - w) + 2, hSpace)
                obj.SetZ(100)
                hSpace -= h
                self.m_ExtNameTextLst.append(obj)
            
        

    
    def OnItemChange(self, dChangeList):
        for dItemData in dChangeList:
            iShape = 0
            oItem = None
            if dItemData['sType'] == 'DelItem':
                oItem = dItemData['oItem']
            elif dItemData['sType'] in ('AddItem', 'ItemNumChange'):
                iItemID = dItemData.get('iItemID')
                oItem = item.GetItem(iItemID)
            
            if oItem:
                iShape = oItem.GetShape()
            
            if iShape and iShape in [
                itemdefine.ID_HONOR_STONE,
                itemdefine.ID_TATTOO_UP_HF_LV1,
                itemdefine.ID_TATTOO_UP_HF_LV2]:
                self.SetNeedItem()
                continue
        

    
    def SetNeedItem(self):
        import makeitemicon
        self.m_NeedItemLst = []
        oItemList = [
            ('box_sign', self.s_SignShape[self.m_Level], self.DoLevelUp),
            ('box_jade', 30204, self.DoStrength)]
        for sLocName, iShape, oCB in enumerate(oItemList):
            (x, y, w, h) = self.GetLocData(sLocName)
            oMaterialImg = makeitemicon.CBackItem(self)
            oMaterialImg.SetPos(x, y)
            oMaterialImg.AddClickAddCB(oCB)
            if iShape == 30204:
                iNeedNum = self.m_Level
            elif not iShape:
                self.SetLevelUpBtn(False)
                continue
            else:
                self.SetLevelUpBtn(True)
                iNeedNum = 1
            iItemNum = self.GetSelfItemNum(iShape)
            self.SetConditionFlag(idx, iNeedNum <= iItemNum)
            if iNeedNum > iItemNum:
                oMaterialImg.CreateNeedAddItemBtn(iShape, 0, 0)
                oMaterialImg.CreateBackNeedItemIcon(iShape, iItemNum, iNeedNum, True)
            else:
                oMaterialImg.CreateBackNeedItemIcon(iShape, iItemNum, iNeedNum, False)
            self.m_NeedItemLst.append(oMaterialImg)
        

    
    def SetLevelUpBtn(self, flag):
        self.GetObject('btn_levelup').Enable(flag)

    
    def SetConditionFlag(self, idx, flag):
        self.m_Condition[idx] = flag

    
    def GetSelfItemNum(self, shape):
        if shape == 30204:
            shapes = (25431, 30204, 31204)
        else:
            shapes = (shape,)
        num = 0
        for shape in shapes:
            num += item.GetItemNum(shape)
        
        return num

    
    def OnEnter(self, msgid):
        import dlggetinfo
        if msgid == 1:
            self.m_Tips = dlggetinfo.ShowFakeItem(self.m_Shape, self.m_TattooExt)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def Getsignitem(self, level):
        shape = {
            1: 72180,
            2: 72181,
            3: 0 }[level]
        if shape:
            dct = item.GetItemsByShape(shape)
            if dct:
                return dct.values()[0]
            
        

    
    def DoLevelUp(self, *args):
        import nettattoo
        import netopenui
        import itemdata
        if not self.CheckTimeLimit():
            return None
        
        if self.m_Condition[0]:
            itemobj = self.Getsignitem(self.m_Level)
            if itemobj:
                pass
            nettattoo.C2SUpdateWithID(self.m_TattooID, itemobj.m_ID)
        else:
            iShape = self.s_SignShape[self.m_Level]
            (sName, _) = itemdata.GetData(iShape)
            netopenui.C2SOpenItemAccessDlg(iShape, 0, 0, sName, 1, 0)
            return None

    
    def DoStrength(self, *args):
        import nettattoo
        if not self.CheckTimeLimit():
            return None
        
        nettattoo.C2SStrengthenWithID(self.m_TattooID)

    
    def CheckTimeLimit(self):
        import misc
        t = misc.Time()
        if t - self.m_LastCommit < 0.05:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xa3\xadn\xbe\xde\xa7@\xa4\xd3\xa7\xd6')
            return False
        
        self.m_LastCommit = t
        return True

    
    def CloseWindow(self):
        TattooComp(None, 0)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 3:
            self.DoLevelUp()
        elif msgid == 4:
            self.DoStrength()
        



class CTattooFuse(combdialog.CCombDialog):
    s_ValidTattoo = [
        72182,
        72183,
        72184]
    
    class CMyNotifyBox(interface.CNotifyBox):
        
        def LeftUp(self):
            par = self.GetPar()
            if par:
                par.OnLeftUp(self.m_MsgID)
            

        
        def LeftDown(self):
            par = self.GetPar()
            if par:
                par.OnLeftDown(self.m_MsgID)
            


    
    def __init__(self, parent):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/tattoofuse.dlg')
        (w, h) = parent.GetSize()
        (my, mh) = self.GetSize()
        self.SetPos(w - 5, (h - mh) / 2)
        self.m_LastCommit = 0
        self.ClearItemInfo()

    
    def ClearItemInfo(self):
        self.m_ResetBox = None
        self.m_BoxLst = {
            1: None,
            2: None }
        self.m_SelTatooInfo = {
            1: None,
            2: None }
        self.m_NotifyLst = {
            1: None,
            2: None }
        self.m_ResetBox = None
        self.m_ResetNotifyBox = None

    
    def SetResultItem(self, tid):
        self.ClearItemInfo()
        self.ShowEffect()
        self.GetParent().SetNewItem(tid)

    
    def OnCompose(self, shape, amount, desc):
        pass

    
    def SetTattoo(self, data):
        if data:
            self.m_SelTatooInfo[1] = data
            (tid, shape, level, desc, iconid) = data
            self.SetTattooBox(1, shape)
            name = desc.split('#')[0]
            self.SetTattooDefault(1, name)
            self.SetResetBox(1, shape, name)
        else:
            self.m_Tips = None

    
    def TakeOutTattoo(self, tid):
        itemid1 = None if self.m_SelTatooInfo[1] else 0
        itemid2 = None if self.m_SelTatooInfo[2] else 0
        if tid == itemid1 or tid == itemid2:
            self.CloseWindow()
        

    
    def GetEmptyPos(self):
        if self.m_BoxLst[1] and self.m_BoxLst[2]:
            return -1
        elif self.m_BoxLst[1]:
            return 2
        else:
            return 1

    
    def CheckItemVal(self, data, emptypos):
        pos = {
            1: 2,
            2: 1 }[emptypos]
        if not self.m_SelTatooInfo[pos]:
            return True
        elif data[0] == self.m_SelTatooInfo[pos][0]:
            return False
        
        return True

    
    def SetOtherTattoo(self, data):
        emptypos = self.GetEmptyPos()
        if emptypos == -1:
            import usermacro
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xa8\xfa\xa4U\xa4\xa3\xbb\xdd\xadn\xb6i\xa6\xe6\xbf\xc4\xa6X\xaa\xba\xaf\xab\xaf\xbe')
            return None
        
        if not self.CheckItemVal(data, emptypos):
            return None
        
        if data:
            self.m_SelTatooInfo[emptypos] = data
            (tid, shape, level, desc, iconid) = data
            self.SetTattooBox(emptypos, shape)
            name = desc.split('#')[0]
            self.SetTattooDefault(emptypos, name)
            self.SetResetBox(emptypos, shape, name)
        else:
            self.m_Tips = None

    
    def SetTattooBox(self, emptypos, shape):
        objname = ('tattooimg', 'tattooimg2')[emptypos - 1]
        (x, y, w, h) = self.GetLocData(objname)
        tattoo = item.CreateItem44Image(self, shape, 0)
        tattoo.SetPos(x, y)
        tattoo.m_TxtLst = []
        notifybox = self.CMyNotifyBox(self, w, h, 0, 0, emptypos)
        notifybox.SetPos(x, y)
        notifybox.SetZ(100)
        self.m_BoxLst[emptypos] = tattoo
        self.m_NotifyLst[emptypos] = notifybox

    
    def SetResetBox(self, emptypos, shape, name):
        if emptypos != 1:
            return None
        
        (x, y, w, h) = self.GetLocData('m_ResetBox')
        tattoo = item.CreateItem44Image(self, shape, 0)
        tattoo.SetPos(x, y)
        tattoo.m_TxtLst = []
        notifybox = self.CMyNotifyBox(self, w, h, 0, 0, emptypos + 10)
        notifybox.SetPos(x, y)
        notifybox.SetZ(100)
        self.m_ResetBox = tattoo
        self.m_ResetNotifyBox = notifybox
        self.SetTattooText(name, self.m_ResetBox)

    
    def ShowEffect(self):
        
        def _effect(desc):
            eff = ''
            if desc:
                eff += '\xafS\xa7\xde\xaf\xab\xaf\xbe\xa1G'
                if desc.count('#r') > 1:
                    eff += desc.replace('#r', '\xa1A', 1)
                else:
                    eff += desc
                if not eff.endswith('#r'):
                    eff += '#r'
                
            
            return eff

        effect = ''
        if self.m_SelTatooInfo[1]:
            (iid, shape, _, desc, _) = self.m_SelTatooInfo[1]
            if shape in self.s_ValidTattoo:
                effect += _effect(desc)
            
        
        if self.m_SelTatooInfo[2]:
            (iid, shape, _, desc, _) = self.m_SelTatooInfo[2]
            if shape in self.s_ValidTattoo:
                effect += _effect(desc)
            
        
        if effect != '':
            import combmacro
            self.m_EffectTxt = combmacro.CRICHTEXT(interface.CRichTextObject, 'effect', self, effect, interface.FontLT14_3, interface.COLOR_4)
        else:
            self.m_EffectTxt = None

    
    def SetTattooDefault(self, pos, name):
        self.m_EffectTxt = None
        self.ShowEffect()
        obj = self.m_BoxLst[pos]
        if obj:
            self.SetTattooText(name, obj)
        

    
    def SetTattooText(self, name, boxobj):
        if name:
            if '(' in name:
                name = name[:-3]
            
            txtLst = []
            if len(name) < 8:
                txtLst = [
                    name]
            
            if len(name) == 8:
                txtLst = [
                    name[:4],
                    name[4:]]
            elif len(name) == 10:
                txtLst = [
                    name[:4].ljust(6),
                    name[4:]]
            elif len(name) >= 12:
                txtLst = [
                    name[:6],
                    name[6:]]
            
            hSpace = 28
            lst = boxobj.m_TxtLst
            for txt in reversed(txtLst):
                obj = interface.CTextObject(boxobj, txt, interface.FontLT12E_1, CInterfaceItem.s_ExtColor)
                (w, h) = obj.GetSize()
                obj.SetPos((44 - w) + 2, hSpace)
                obj.SetZ(100)
                hSpace -= h
                lst.append(obj)
            
        

    
    def OnEnter(self, msgid):
        import dlggetinfo
        if msgid in (1, 2, 11):
            msgid %= 10
            (_, shape, _, desc, _) = self.m_SelTatooInfo[msgid]
        
        if msgid == 1:
            self.m_SelTatooInfo
            self.m_Tips = dlggetinfo.ShowFakeItem(shape, desc)
        elif msgid == 2:
            self.m_Tips = dlggetinfo.ShowFakeItem(shape, desc)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def OnLeftUp(self, msgid):
        if msgid == 11:
            msgid = 1
        
        if msgid in (1, 2):
            self.m_Tips = None
            self.m_SelTatooInfo[msgid] = []
            self.m_BoxLst[msgid] = None
            self.m_NotifyLst[msgid] = None
            self.ShowEffect()
        
        if msgid == 1:
            self.m_ResetBox = None
            self.m_ResetNotifyBox = None
        

    
    def OnLeftDown(self, msgid):
        pass

    
    def DoFuse(self):
        import misc
        import usermacro
        import nettattoo
        pos = self.GetEmptyPos()
        if pos != -1:
            usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xa8\xe2\xad\xd3\xafS\xa7\xde\xaf\xab\xaf\xbe')
            return None
        
        t = misc.Time()
        if t - self.m_LastCommit < 0.2:
            usermacro.PROMPT_MSG('\xbd\xd0\xa4\xa3\xadn\xbe\xde\xa7@\xa4\xd3\xa7\xd6')
            return None
        
        self.m_LastCommit = t
        nettattoo.C2SFuseWithID(self.m_SelTatooInfo[1][0], self.m_SelTatooInfo[2][0])

    
    def DoReset(self):
        import usermacro
        import nettattoo
        pos = self.GetEmptyPos()
        if pos == 1:
            usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xaf\xab\xaf\xbe')
            return None
        
        nettattoo.C2SResetWithID(self.m_SelTatooInfo[1][0])

    
    def CloseWindow(self):
        self.ClearItemInfo()
        TattooComp(None, 0)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 4:
            self.DoFuse()
        elif msgid == 5:
            self.DoReset()
