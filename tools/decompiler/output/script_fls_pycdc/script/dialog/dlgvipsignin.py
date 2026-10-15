# pycdc 交叉复核产物 · script.fls entry 1462
# co_filename(原始)='script/dialog/dlgvipsignin.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1462.pyc (Python 2.5)

import C_object
import interface
import combdialog
MAPDATA = [
    (0, 0, 2),
    (1, 0, 1),
    (1, 1, 1),
    (1, 2, 1),
    (1, 3, 1),
    (1, 4, 1),
    (2, 4, 1),
    (3, 4, 1),
    (4, 4, 1),
    (5, 4, 1),
    (5, 3, 1),
    (5, 2, 1),
    (4, 2, 1),
    (3, 2, 1),
    (3, 1, 1),
    (3, 0, 1),
    (4, 0, 1),
    (5, 0, 1),
    (6, 0, 1),
    (7, 0, 1),
    (7, 1, 1),
    (7, 2, 1),
    (8, 2, 1),
    (8, 3, 1),
    (8, 4, 1),
    (9, 4, 1),
    (10, 4, 1),
    (11, 4, 1),
    (11, 3, 1),
    (11, 2, 1),
    (11, 1, 1),
    (12, 1, 1)]
WIDTH = 50
HEIGHT = 50
TYPE2FILENAME = {
    1: '\xd7\xaa\xd7\xaa\xc6\xd5\xcd\xa8\xb8\xf1\xd7\xd3.igs',
    2: '\xd7\xaa\xd7\xaa\xc6\xf0\xb5\xe3.igs' }

def GetCellFile(iType):
    return 'combdialog/\xd0\xd2\xd4\xcb\xd7\xaa\xd7\xaa\xc0\xd6/' + TYPE2FILENAME.get(iType, '\xd7\xaa\xd7\xaa\xc6\xd5\xcd\xa8\xb8\xf1\xd7\xd3.igs')

g_SignInDlg = None
g_GainExtReward = False

def Show(dataDct):
    global g_SignInDlg
    g_SignInDlg = CSignInDlg()
    g_SignInDlg.SetData(dataDct)


def Close():
    global g_SignInDlg
    g_SignInDlg = None


def SignIn(signinIdx):
    if g_SignInDlg:
        g_SignInDlg.SignIn(signinIdx)
    


def RefreshDateTxt(signinamount, maxsignin):
    if g_SignInDlg:
        g_SignInDlg.RefreshDateTxt(signinamount, maxsignin)
    


def ShowExtReward():
    global g_GainExtReward
    g_GainExtReward = True


class CCell(C_object.CBoxObject, interface.CClickObject):
    
    def __init__(self, parent, iType, idx):
        C_object.CBoxObject.__init__(self, parent, WIDTH, HEIGHT, 0, 0)
        interface.CClickObject.__init__(self, 0)
        self.CreateBackgroundImg(iType)
        self.SetPresent(False)
        self.CreateEnterImg()
        self.m_Idx = idx

    
    def CreateBackgroundImg(self, iType):
        self.m_Type = iType
        self.m_CellImage = C_object.CImagesObject(self, GetCellFile(self.m_Type), 'interface')

    
    def CreateEnterImg(self):
        self.m_EnterImg = C_object.CImagesObject(self, 'combdialog/\xd0\xd2\xd4\xcb\xd7\xaa\xd7\xaa\xc0\xd6/\xd7\xaa\xd7\xaa\xb8\xdf\xc1\xc1.igs', 'interface')
        self.m_EnterImg.SetPos(-2, -2)
        self.m_EnterImg.SetZ(10)
        self.m_EnterImg.SetShow(False)

    
    def ReplaceShape(self, shape):
        dct = {
            9003: 25405,
            9002: 23013,
            9004: 25405,
            9029: 70662,
            9065: 30208,
            9005: 25405 }
        return dct.get(shape, shape)

    
    def SetShape(self, shape, amount = 1):
        import item
        shape = self.ReplaceShape(shape)
        self.m_Shape = shape
        if shape:
            self.m_Icon = item.CreateItem44Image(self, shape)
            self.m_Icon.SetPos(2, 2)
            self.m_Icon.SetZ(1)
        else:
            self.m_Icon = None
        if self.m_Icon and amount > 1:
            self.m_AmountText = C_object.CTextObject(self.m_Icon, '%2d' % amount, interface.FontLT14E_1, 16777215, 0)
            self.m_AmountText.SetPos(26, 30)
        else:
            self.m_AmountText = None

    
    def GetShape(self):
        return self.m_Shape

    
    def SetPresent(self, bPresent):
        self.m_IsPresent = bPresent
        if bPresent:
            self.m_PresentAni = C_object.CSpriteObject(self, 'common/sign.spr', 'interface')
            interface.Center(self.m_PresentAni)
            self.m_PresentAni.CreateCommand(1, 'animation')
            self.m_PresentAni.SetZ(2)
        elif hasattr(self, 'm_PresentAni') and self.m_PresentAni:
            self.m_PresentAni.Release()
            self.m_PresentAni = None
        

    
    def SetSign(self, bSign):
        if bSign:
            self.m_SignText = C_object.CRichTextObject(self, 100, interface.FontLT14E_1, ('\xa4w\xbb\xe2\xa8\xfa', '\xa4w\xb9L\xb4\xc1')[bSign - 1], (65280, 13023744)[bSign - 1])
            self.m_SignText.SetPos(2, 15)
            self.m_SignText.SetZ(4)
        else:
            self.m_SignText = None

    
    def Enter(self):
        import dlggetinfo
        import wrapinterface
        self.m_EnterImg.SetShow(True)
        if hasattr(self, 'm_Shape') and self.m_Shape:
            shape = self.m_Shape
            if shape == 9003:
                shape = 25405
            
            self.m_Tips = dlggetinfo.NewItemInfo(self.m_Idx, shape, '', None, 64)
        

    
    def Leave(self):
        self.m_EnterImg.SetShow(False)
        self.m_Tips = None

    
    def LeftUp(self):
        pass



class CCellMap(C_object.CBaseObject):
    
    def __init__(self, parent, x, y):
        C_object.CBaseObject.__init__(self, parent)
        self.CreateCells()
        self.SetPos(x, y)
        self.SetZ(100)

    
    def CreateCells(self):
        self.m_CellObject = []
        for row, col, iType in enumerate(MAPDATA):
            cell = CCell(self, iType, idx)
            cell.SetPos(WIDTH * row, HEIGHT * col)
            cell.SetZ(row + col)
            self.m_CellObject.append(cell)
        

    
    def Clear(self):
        self.CreateCells()

    
    def SetShape(self, idx, shape, amount):
        self.m_CellObject[idx].SetShape(shape, amount)

    
    def SetSign(self, idx, bSign):
        self.m_CellObject[idx].SetSign(bSign)

    
    def SetPresent(self, idx):
        self.m_CellObject[idx].SetPresent(True)

    
    def GetCell(self, idx):
        return self.m_CellObject[idx]



class CSignInDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog2/signin/signin.dlg')
        (x, y) = self.GetObject('loc_Map').GetPos()
        self.m_CellMap = CCellMap(self, x, y)
        self.Effect()
        interface.Center(self)
        self.GetObject('btn_draw').m_ParentNotify = True

    
    def Init(self):
        self.GetObject('noname0').ChgCaptionTxt('VIP\xc3\xb1\xa8\xec')
        for name in ('noname2', 'noname6', 'noname9', 'txt_date2'):
            obj = self.GetObject(name)
            if obj:
                obj.SetShow(False)
                continue
        

    
    def SetData(self, dataDct):
        import dlggetinfo
        import misc
        self.m_CellMap.Clear()
        for idx, dct in enumerate(dataDct['itemList']):
            tm = dataDct['beginTime'] + idx * 24 * 60 * 60
            timeList = misc.LocalTime(tm)
            ext = '%d\xa4\xeb%d\xa4\xe9\xb4M\xc4_\xa5i\xbb\xe2\xa8\xfa' % timeList[1:3]
            obj = self.m_CellMap.GetCell(idx + 1)
            obj.SetShape(dct['shape'], dct['amount'])
            if idx + 1 < dataDct['signinIdx'] and dct['sign'] == 0:
                signflag = 2
            else:
                signflag = dct['sign']
            obj.SetSign(signflag)
        
        self.m_CellMap.SetPresent(dataDct['signinIdx'])

    
    def Effect(self):
        import mapani
        self.m_EffRes = mapani.LoadEffect(self, 'dialog2/signin/effect/effect2.txt', 'dialog2/signin/effect')

    
    def Idx2Pos(self, idx):
        (baseX, baseY) = self.m_CellMap.GetPos()
        cellObj = self.m_CellMap.GetCell(idx)
        (x, y) = cellObj.GetPos()
        return (baseX + x, baseY + y)

    
    def Idx2Shape(self, idx):
        cellObj = self.m_CellMap.GetCell(idx)
        return cellObj.GetShape()

    
    def SignIn(self, signinIdx):
        cellObj = self.m_CellMap.GetCell(signinIdx)
        
        def callback():
            cellObj.SetSign(True)

        self.PlaySignAni(signinIdx, callback)

    
    def PlaySignAni(self, signinIdx, callback):
        import itemdata
        import mainmenu
        shape = self.Idx2Shape(signinIdx)
        (tx, ty) = self.Idx2Pos(signinIdx)
        self.m_SignSpr = C_object.CStretchImagesObject(self, 'item120/%.5d.igs' % itemdata.Shape2Image(shape), 'item')
        self.m_SignSpr.SetPos(320, 40)
        self.m_SignSpr.SetZ(1000)
        itemBtn = mainmenu.GetItemBtn()
        if itemBtn == None:
            callback()
        
        (x, y) = self.GetPos()
        (tx, ty) = itemBtn.GetPos()
        tx = tx - x
        ty = ty - y
        (sx, sy) = self.m_SignSpr.GetPos()
        (step, xstep) = (45, 25)
        ex = sx
        ey = sy - xstep * 2
        posList = []
        for i in range(step):
            x = tx + int(i * (ex - tx) * 1 / step)
            y = ty + int(i * (ey - ty) * 1 / step)
            scale = 1 * (step + i) / (2 * step)
            posList.append((x, y, scale))
        
        []([ (ex, ey + i * 3, 1) for i in range(0, xstep) ])
        
        def run(obj, posList, callback):
            if len(posList) == 0:
                obj.m_SignAni.Release()
                obj.m_SignAni = None
                obj.m_SignSpr = None
                if g_GainExtReward:
                    obj.ShowExtReward()
                
                callback()
                return None
            
            (x, y, scale) = posList.pop()
            obj.m_SignSpr.SetScale(scale)
            obj.m_SignSpr.SetPos(x, y)
            return (posList, callback)

        self.m_SignAni = self.CreatePyCommand(1, run, posList, callback)

    
    def RefreshDateTxt(self, signinamount, maxsignin):
        import combmacro
        self.m_AmountTxt = combmacro.CRICHTEXT(C_object.CRichTextObject, 'txt_date1', self, '#Y%d' % signinamount, interface.FontLT14E_1, interface.COLOR_4)
        self.m_MaxTxt = combmacro.CRICHTEXT(C_object.CRichTextObject, 'txt_date2', self, '#Y%d' % maxsignin, interface.FontLT14E_1, interface.COLOR_4)

    
    def ShowExtReward(self):
        import itemdata
        import mainmenu
        import combmacro
        shape = 26734
        self.m_RewardSpr = C_object.CStretchImagesObject(self, 'item120/%.5d.igs' % itemdata.Shape2Image(shape), 'item')
        self.m_RewardSpr.SetPos(320, 140)
        self.m_RewardSpr.SetZ(1000)
        itemBtn = mainmenu.GetItemBtn()
        if not itemBtn:
            return None
        
        (x, y) = self.GetPos()
        (tx, ty) = itemBtn.GetPos()
        tx = tx - x
        ty = ty - y
        (sx, sy) = self.m_RewardSpr.GetPos()
        (step, xstep) = (45, 25)
        ex = sx
        ey = sy - xstep * 2
        posList = []
        for i in range(step):
            x = tx + int(i * (ex - tx) * 1 / step)
            y = ty + int(i * (ey - ty) * 1 / step)
            scale = 1 * (step + i) / (2 * step)
            posList.append((x, y, scale))
        
        []([ (ex, ey + i * 3, 1) for i in range(0, xstep) ])
        
        def run(obj, posList):
            if len(posList) == 0:
                obj.m_RewardAni.Release()
                obj.m_RewardAni = None
                obj.m_RewardSpr = None
                obj.m_Firewords = []
                g_GainExtReward = False
                return None
            
            (x, y, scale) = posList.pop()
            obj.m_RewardSpr.SetScale(scale)
            obj.m_RewardSpr.SetPos(x, y)
            obj.ShowFirewords()
            return (posList,)

        self.m_RewardAni = self.CreatePyCommand(1, run, posList)

    
    def ShowFirewords(self):
        import random
        import combmacro
        self.m_Firewords = []
        (dlgw, dlgh) = self.GetSize()
        (x, y, w, h) = combmacro.GetObjectData(self, 'btn_draw')
        for idx in xrange(2):
            effectidx = random.randint(20, 30)
            fx = random.randint(0, dlgw)
            fy = random.randint(0, dlgh)
            fireword = C_object.CSpriteObject(self, 'mapeffect/%.4d.spr' % effectidx, 'misc')
            fireword.SetPos(fx, fy)
            fireword.SetZ(1000 - effectidx)
            self.m_Firewords.append(fireword)
        
        for obj in self.m_Firewords:
            obj.CreateCommand(1, 'one_off_animation')
        

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def OnSignIn(self):
        import nethuodong
        nethuodong.CVipSignin.C2SSignin()

    
    def CloseWindow(self):
        global g_SignInDlg
        g_SignInDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 3:
            self.OnSignIn()
        


g_SigninBtn = None

def ShowSigninBtn(bShow = True, txt = 'VIP\xc3\xb1\xa8\xec', huodongType = 1, leftTime = -1):
    global g_SigninBtn, g_SigninBtn
    if bShow:
        g_SigninBtn = CSigninBtn(interface.MainPanel, 40, 100, txt, huodongType)
        g_SigninBtn.SetLeftTime(leftTime)
    else:
        g_SigninBtn = None


class CSigninBtn(C_object.CBaseObject):
    
    def __init__(self, parent, x, y, txt, huodongType):
        C_object.CBaseObject.__init__(self, parent)
        self.m_Text = txt
        self.m_HuodongType = huodongType
        self.CreateClickImg()
        self.CreateTitle()
        self.SetPos(x, y)

    
    def CreateClickImg(self):
        import clickimage
        img1 = clickimage.CClickImage(self, 'mainmenu/packet.igs', 1, 0, 0)
        img2 = clickimage.CClickImage(self, 'mainmenu/packet_timebar.igs', 2, 12, 48)
        self.m_ImageList = [
            img1,
            img2]

    
    def CreateTitle(self):
        self.m_TextObj = interface.CTextObject(self.m_ImageList[-1], self.m_Text, interface.FontST12, 255, 0)
        interface.Center(self.m_TextObj)

    
    def OnEnter(self, msgid):
        if msgid == 1:
            self.m_ImageList[0].SetFrame(2)
            import wrapinterface
            if self.m_LeftTime == 0:
                self.m_Tip = wrapinterface.CTextTips(None, -1, '\xa5i\xbb\xe2\xa8\xfa', interface.FontLT14E_1, direct = 1)
            
        

    
    def OnLeave(self, msgid):
        self.m_ImageList[0].SetFrame(0)
        self.m_Tip = None

    
    def SetLeftTime(self, leftTime):
        self.m_LeftTime = leftTime
        self.CreateLeftTimeCmd()

    
    def CreateLeftTimeCmd(self):
        self.ReleaseLeftTimeCmd()
        
        def reduce(obj):
            if obj.m_LeftTime <= 0:
                return None
            
            obj.m_LeftTime -= 1
            return ()

        self.m_LeftTimeCmd = self.CreatePyCommand(30, reduce)

    
    def ReleaseLeftTimeCmd(self):
        if getattr(self, 'm_LeftTimeCmd', None):
            self.m_LeftTimeCmd.Release()
            self.m_LeftTimeCmd = None
        

    
    def OnMessage(self, msgid):
        if msgid in (1, 2):
            import nethuodong
            if self.m_HuodongType == 1:
                nethuodong.CVipSignin.C2SOpenSigninDlg()
            elif self.m_HuodongType == 2:
                nethuodong.CZhuanZhuan.C2SZhuanZhuan()
