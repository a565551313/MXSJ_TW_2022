# pycdc 交叉复核产物 · script.fls entry 2693
# co_filename(原始)='script/dialog/dlgshiwu.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2693.pyc (Python 2.5)

import interface
import wrapinterface
import combdialog
g_PetShiWuDialog = None
g_PetShiwu = None

def ModuleReset():
    global g_PetShiWuDialog, g_PetShiwu
    g_PetShiWuDialog = None
    g_PetShiwu = None


class CPetAni(wrapinterface.CPetAni):
    
    def __init__(self, parent, shape, desc, key = None, fps = 150):
        self.m_StateIndex = 0
        wrapinterface.CPetAni.__init__(self, parent, shape, desc, key, fps)
        self.m_Photo.ATTACK_RATE = -1

    
    def RandomAction(self):
        self.m_Photo.SetState(self.m_State)
        if self.m_Photo.m_Action:
            state_list = self.RANDOM_STATE_FOR_SHAPE.get(self.m_AniShape, self.RANDOM_STATE)
        else:
            state_list = self.RANDOM_STATE
        self.m_StateIndex = (self.m_StateIndex + 1) % len(state_list)
        self.m_State = state_list[self.m_StateIndex]
        return ()



class CPetShiWuDialog(combdialog.CCombDialog):
    
    def __init__(self, shape2shiwumax, shapelst = None):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/summon/sumshiwu.dlg')
        interface.Center(self)
        self.m_Shape2ShiwuMax = shape2shiwumax
        self.m_CurPetItem = None
        self.m_CurDirect = 0
        self.m_ID2Desc = { }
        import pet
        self.GetObject('sumlst').m_VScrollBar.SetShow(len(pet.g_Pets) > 10)
        if shapelst:
            self.RefershByShapelst(shapelst)
        else:
            self.RefershPetLst()
        self.Capture(1, 0)

    
    def RefershPetLst(self):
        import pet
        import combmacro
        import copy
        petlist = self.GetObject('sumlst')
        for petobj in pet.g_Pets:
            it = petlist.AddTextItem(petobj.m_Prop.m_Name)
            it.m_ID = petobj.m_ID
            it.m_Shape = getattr(petobj.m_Prop, 'm_Shape')
            it.m_Desc = getattr(petobj.m_Prop, 'm_Desc')
            it.m_CurShiwu = 1
            if 'weapon2' in it.m_Desc and it.m_Desc['weapon2'][1] == 2:
                it.m_CurShiwu = 2
            
            if 'weapon3' in it.m_Desc and it.m_Desc['weapon3'][1] == 3:
                it.m_CurShiwu = 3
            
            self.m_ID2Desc[it.m_ID] = copy.deepcopy(it.m_Desc)
            sel = combmacro.GetSelectedItemFromList(petlist)
            if sel is None:
                it.LeftUp()
            
            if pet.GetActivatePet() and pet.GetActivatePet().m_ID == it.m_ID:
                it.LeftUp()
                continue
        
        if len(pet.g_Pets) == 0:
            self.GetObject('btn_pre').SetShow(False)
            self.GetObject('btn_bck').SetShow(False)
            self.GetObject('btn_left').Enable(False)
            self.GetObject('btn_right').Enable(False)
        
        petlist.ResetItems()
        petlist.ResetScrollBar()

    
    def RefershByShapelst(self, shapelst):
        import combmacro
        import copy
        petlist = self.GetObject('sumlst')
        petlist.Clear()
        for idx, shape in enumerate(shapelst):
            it = petlist.AddTextItem(self.GetItemName(shape))
            it.m_ID = idx
            it.m_Shape = shape
            if self.m_Shape2ShiwuMax[shape] == 2:
                it.m_Desc = {
                    'color': [
                        0,
                        0,
                        0],
                    'weapon': [
                        0,
                        1,
                        0],
                    'weapon2': [
                        0,
                        2],
                    'wing': [
                        0],
                    'titleFlash': 0,
                    'fairy': [
                        [
                            0,
                            0],
                        [
                            0,
                            0]] }
            elif self.m_Shape2ShiwuMax[shape] == 3:
                it.m_Desc = {
                    'color': [
                        0,
                        0,
                        0],
                    'weapon': [
                        0,
                        1,
                        0],
                    'weapon2': [
                        0,
                        2],
                    'weapon3': [
                        0,
                        3],
                    'wing': [
                        0],
                    'titleFlash': 0,
                    'fairy': [
                        [
                            0,
                            0],
                        [
                            0,
                            0]] }
            elif self.m_Shape2ShiwuMax[shape] == 1:
                enumerate = 1
                None['wing'] = [
                    0]
                None['titleFlash'] = 0
                None['fairy'] = [
                    [
                        0,
                        0],
                    [
                        0,
                        0]]
                it.m_Desc = None
            else:
                it.m_Desc = {
                    'color': [
                        0,
                        0,
                        0],
                    'weapon': [
                        0,
                        0,
                        0],
                    'wing': [
                        0],
                    'titleFlash': 0,
                    'fairy': [
                        [
                            0,
                            0],
                        [
                            0,
                            0]] }
            it.m_CurShiwu = self.m_Shape2ShiwuMax[shape]
            self.m_ID2Desc[it.m_ID] = copy.deepcopy(it.m_Desc)
            sel = combmacro.GetSelectedItemFromList(petlist)
            if sel is None:
                it.LeftUp()
                continue
        
        petlist.ResetItems()
        petlist.ResetScrollBar()

    
    def GetItemName(self, shape):
        import petdata
        return petdata.GetData(shape)['name']

    
    def DrawPetPhoto1(self, shape, desc):
        import copy
        if hasattr(self, 'm_PetAni1') and self.m_PetAni1:
            self.m_PetAni1.ReleaseAll()
        
        petdesc = copy.deepcopy(desc)
        petdesc['weapon'][1] = 0
        if 'weapon2' in petdesc:
            petdesc['weapon2'][1] = 0
        
        if 'weapon3' in petdesc:
            petdesc['weapon3'][1] = 0
        
        self.m_PetAni1 = CPetAni(self, shape, petdesc, fps = 150)
        photo = self.GetObject('box_1')
        (x, y) = photo.GetPos()
        self.m_PetAni1.SetPos(x + 7, y + 5)

    
    def DrawPetPhoto2(self, shape, desc):
        if hasattr(self, 'm_PetAni2') and self.m_PetAni2:
            self.m_PetAni2.ReleaseAll()
        
        self.DrawPetPhoto1(shape, self.m_CurPetItem.m_Desc)
        self.m_PetAni2 = CPetAni(self, shape, desc, fps = 150)
        photo = self.GetObject('box_2')
        (x, y) = photo.GetPos()
        self.m_PetAni2.SetPos(x + 7, y + 5)

    
    def RefershBtn(self):
        import style
        if self.m_Shape2ShiwuMax[self.m_CurPetItem.m_Shape] == 1:
            self.GetObject('shiwu0').SetText('\xa8\xd8\xc0\xb9\xb9\xa2\xaa\xab')
            (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_shiwu1')
            self.GetObject('shiwu0').SetPos(x, y)
            self.GetObject('btn_pre').SetShow(False)
            self.GetObject('btn_bck').SetShow(False)
        else:
            self.GetObject('shiwu0').SetText('\xa8\xd8\xc0\xb9%d\xaeM\xb9\xa2\xaa\xab' % self.m_CurPetItem.m_CurShiwu)
            (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_shiwu2')
            self.GetObject('shiwu0').SetPos(x, y)
            self.GetObject('btn_pre').SetShow(True)
            self.GetObject('btn_bck').SetShow(True)
            self.GetObject('btn_pre').Enable(self.m_CurPetItem.m_CurShiwu > 1)
            self.GetObject('btn_bck').Enable(self.m_CurPetItem.m_CurShiwu < self.m_Shape2ShiwuMax[self.m_CurPetItem.m_Shape])

    
    def RefershShiwu(self):
        import copy
        PetItem = self.m_CurPetItem
        if PetItem:
            InfoDct = copy.deepcopy(self.m_ID2Desc)
            if PetItem.m_CurShiwu == 1:
                InfoDct[PetItem.m_ID]['weapon'][1] = 1
                self.m_ID2Desc[PetItem.m_ID]['weapon'][1] = 1
                if 'weapon2' in InfoDct[PetItem.m_ID]:
                    del InfoDct[PetItem.m_ID]['weapon2']
                
                if 'weapon3' in InfoDct[PetItem.m_ID]:
                    del InfoDct[PetItem.m_ID]['weapon3']
                
            elif PetItem.m_CurShiwu == 2:
                if not InfoDct[PetItem.m_ID].get('weapon2', None):
                    InfoDct[PetItem.m_ID].update({
                        'weapon2': [
                            0,
                            2] })
                    self.m_ID2Desc[PetItem.m_ID].update({
                        'weapon2': [
                            0,
                            2] })
                
                if 'weapon3' in InfoDct[PetItem.m_ID]:
                    del InfoDct[PetItem.m_ID]['weapon3']
                
            elif PetItem.m_CurShiwu == 3 and not InfoDct[PetItem.m_ID].get('weapon3', None):
                InfoDct[PetItem.m_ID].update({
                    'weapon3': [
                        0,
                        3] })
                self.m_ID2Desc[PetItem.m_ID].update({
                    'weapon3': [
                        0,
                        3] })
            
            self.DrawPetPhoto2(PetItem.m_Shape, InfoDct[PetItem.m_ID])
            self.m_PetAni2.SetDir(self.m_CurDirect * 8)
            self.m_PetAni1.SetDir(self.m_CurDirect * 8)
        

    
    def CloseWindow(self):
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.m_CurPetItem.m_CurShiwu -= 1
            self.RefershBtn()
            self.RefershShiwu()
        elif msgid == 2:
            self.m_CurPetItem.m_CurShiwu += 1
            self.RefershBtn()
            self.RefershShiwu()
        elif msgid == 3:
            self.CloseWindow()
        elif msgid == 4:
            self.m_CurDirect -= 1
            self.m_CurDirect = (self.m_CurDirect + 4) % 4
            self.m_PetAni1.SetDir(self.m_CurDirect * 8)
            self.m_PetAni2.SetDir(self.m_CurDirect * 8)
        elif msgid == 5:
            self.m_CurDirect += 1
            self.m_CurDirect %= 4
            self.m_PetAni1.SetDir(self.m_CurDirect * 8)
            self.m_PetAni2.SetDir(self.m_CurDirect * 8)
        elif msgid <= msgid:
            pass
        elif msgid < 120:
            petlist = self.GetObject('sumlst')
            idx = msgid - 101
            if idx >= len(petlist.m_Items):
                return None
            
            self.m_CurDirect = 0
            it = petlist.m_Items[idx]
            self.m_CurPetItem = it
            self.DrawPetPhoto2(it.m_Shape, it.m_Desc)
            self.RefershBtn()
            self.RefershShiwu()
        



def ShowSwitch(shape2shiwumax = None):
    global g_PetShiWuDialog, g_PetShiWuDialog
    g_PetShiWuDialog = None
    g_PetShiWuDialog = CPetShiWuDialog(shape2shiwumax)


def Show(shapeinfo):
    global g_PetShiwu, g_PetShiwu
    (shapelst, shiwumax) = shapeinfo
    shape2shiwumax = { }
    for shape in shapelst:
        shape2shiwumax[shape] = shiwumax
    
    g_PetShiwu = None
    g_PetShiwu = CPetShiWuDialog(shape2shiwumax, shapelst)
