# pycdc 交叉复核产物 · script.fls entry 351
# co_filename(原始)='script/dialog/dlgherochange.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_351.pyc (Python 2.5)

import avatar
import combdialog
import hero
import interface
import ui
SHAPE2NAME = {
    111: '\xb3p\xbb\xbb\xabL',
    112: '\xc5R\xc6E\xa4\xf5',
    121: '\xa4\xd1\xc2\xcd\xa4l',
    122: '\xb6\xb3\xb5L\xa4\xdf',
    131: '\xc3t\xb4\xf0\xa4l',
    132: '\xaa\xa2\xa6p\xad\xb7',
    211: '\xad\xe2\xaai\xbfP',
    212: '\xad\xb7\xb9a\xa8\xe0',
    221: '\xa5\xc9\xc3\xb9\xabb',
    222: '\xb2H\xb2M\xac\xee',
    231: '\xa4d\xa4\xdb\xbd\xba',
    232: '\xb5\xb5\xb9\xe4\xb5M' }
CLASS2SHAPE = {
    0: [
        (111, 112),
        (211, 212)],
    1: [
        (121, 122),
        (221, 222)],
    2: [
        (131, 132),
        (231, 232)] }
LIUPAI2NAME = {
    1001: '\xbcC\xaak',
    1002: '\xa4M\xaak',
    1003: '\xbaj\xaak',
    1004: '\xae\xb1\xaak',
    1005: '\xb5\xa7\xaak',
    1006: '\xbe\xa7\xaea',
    1007: '\xb9D\xaea',
    1008: '\xa6\xf2\xaea',
    1009: '\xb3\xb1\xb6\xa7',
    1010: '\xa7\xc5\xb3N',
    1011: '\xb7t\xbe\xb9',
    1014: '\xb0\xad\xa8\xa6' }
g_HeroChange = None

def ModuleReset():
    global g_HeroChange
    g_HeroChange = None


def Show(shapeInfoLst):
    global g_HeroChange
    g_HeroChange = CDlgHeroChange(shapeInfoLst)


class CDlgHeroChange(combdialog.CCombDialog):
    
    def __init__(self, shapeInfoLst):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/herochange.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_ShapeInfoLst = shapeInfoLst
        self.m_ChangeType = -1
        self.InitShapeInfo()
        self.CreateTipImg()
        self.InitButtonEnter()
        self.CreateCheckBtns()

    
    def CreateCheckBtns(self):
        import style
        path = style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xd1\xa1\xd4\xf1.igs')
        for i in range(2):
            (x, y) = self.GetObject('btn_check%d' % (i + 1)).GetPos()
            attr = 'm_CheckBtn%d' % (i + 1)
            btn = interface.CCheckButton(self, path, x, y, i + 2)
            setattr(self, attr, btn)
        
        self.m_CheckBtn1.LeftUp()

    
    def InitButtonEnter(self):
        for i in range(3):
            self.GetObject('btn_act%d' % (i + 1)).m_ParentNotify = True
        

    
    def HideChangeImg(self):
        for i in range(3):
            self.GetObject('img_change%d' % (i + 1)).SetShow(False)
            self.GetObject('herobox%d' % (i + 1)).SetShow(False)
        
        self.GetObject('box_change1').SetShow(False)
        self.GetObject('box_change2').SetShow(False)

    
    def InitShapeInfo(self):
        iShape = hero.g_Prop.m_Shape
        iClass = hero.g_Prop.m_Class
        \xe2\xd8\xee\xf3 = hero.g_Prop.m_Sex
        self.m_OwnShape = [
            iShape]
        self.m_TipTextLst = [
            self.GetText(iShape, iClass, (hero.g_Prop.m_Liupai, hero.g_Prop.m_SecondLiupai))]
        self.m_ConfirmTxt = [
            self.GetConfirmText(iShape, iClass, (hero.g_Prop.m_Liupai, hero.g_Prop.m_SecondLiupai))]
        self.m_ChangeShape = self.GetChangeShape(iClass, \xe2\xd8\xee\xf3, iShape)
        self.m_ChangeDct = { }
        self.m_CanChangeLst = [
            self.GetChangeShapeLst(iClass, \xe2\xd8\xee\xf3)]
        self.m_ColorLst = [
            hero.g_Prop.m_Desc['color']]
        if not self.m_ShapeInfoLst:
            return None
        
        for shape, classID, liuPaiLst, color in self.m_ShapeInfoLst:
            self.m_OwnShape.append(shape)
            self.m_TipTextLst.append(self.GetText(shape, classID, liuPaiLst))
            self.m_ConfirmTxt.append(self.GetConfirmText(shape, classID, liuPaiLst))
            self.m_CanChangeLst.append(self.GetChangeShapeLst(classID, \xe2\xd8\xee\xf3))
            self.m_ColorLst.append(color)
        

    
    class CImgWithTips(interface.CImagesObject, interface.CBase):
        
        def __init__(self, parent, fileName, tips):
            interface.CImagesObject.__init__(self, parent, fileName, interface.UIPath)
            self.MessageProcess()
            self.m_TipsStr = tips

        
        def Enter(self):
            import wrapinterface
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, self.m_TipsStr, interface.FontLT14_3)
            self.m_TipsObj.SetOwner(self)

        
        def Leave(self):
            self.m_TipsObj = None


    
    def CreateTipImg(self):
        obj = self.GetObject('box_tipimg')
        (x, y) = obj.GetPos()
        self.m_TipImg = self.CImgWithTips(self, '\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs', '\xc7\xe9\xa4\xc1\xb4\xab\xa9\xca\xa7O\xae\xc9\xa1A\xbb\xdd\xadn\xac\xb0\xa5\xbb\xa8\xa4\xa6\xe2\xa4U\xaa\xba#Y\xa9\xd2\xa6\xb3\xc2\xbe\xb7~#n#r\xb3\xa3\xa4\xc0\xa7O\xad\xab\xb7s\xbf\xef\xbe\xdc\xa4@\xad\xd3\xb7s\xaa\xba\xb3y\xab\xac#r\xc7\xea\xa4\xc1\xb4\xab\xa9\xca\xa7O\xab\xe1\xc0Y\xb9\xb3\xa5H\xa4\xce\xb3\xa1\xa4\xc0\xa9\xca\xa7O\xb1M\xc4\xdd\xba\xd9\xbf\xd7\xb1N#r#Y\xaa\xbd\xb1\xb5\xae\xf8\xa5\xa2#n\xa1A\xb5L\xaak\xab\xec\xb4_')
        self.m_TipImg.SetPos(x, y)

    
    def CheckBtnSelected(self, itype):
        btn = getattr(self, 'm_CheckBtn%d' % itype)
        btn.SetSelect(True)
        idx = None if itype == 1 else 1
        btn = getattr(self, 'm_CheckBtn%d' % idx)
        btn.SetSelect(False)

    
    def SetChangeType(self, itype = 1):
        self.CheckBtnSelected(itype)
        if self.m_ChangeType == itype:
            return None
        
        if itype == 2 and hero.g_Prop.m_IsMarried:
            import usermacro
            usermacro.PROMPT_MSG('\xa5u\xa6\xb3\xb3\xe6\xa8\xad\xaa\xb1\xaea\xa4~\xa5i\xa5H\xa4\xc1\xb4\xab\xa4\xa3\xa6P\xa9\xca\xa7O')
            self.m_CheckBtn1.LeftUp()
            return None
        
        self.m_ChangeType = itype
        self.InitDlg()

    
    def GetText(self, shape, classID, liuPaiLst):
        return '%s#r%s#r%s\xa1B%s' % (SHAPE2NAME[shape], hero.id2class(classID), LIUPAI2NAME[liuPaiLst[0]], LIUPAI2NAME[liuPaiLst[1]])

    
    def GetConfirmText(self, shape, classID, liuPaiLst):
        return '%s,%s,%s,%s' % (hero.id2class(classID), LIUPAI2NAME[liuPaiLst[0]], LIUPAI2NAME[liuPaiLst[1]], SHAPE2NAME[shape])

    
    def GetChangeShape(self, classID, \xe2\xd8\xee\xf3, shape):
        lst = CLASS2SHAPE[classID][\xe2\xd8\xee\xf3 - 1]
        for iShape in lst:
            if shape != iShape:
                return iShape
                continue
        

    
    def GetChangeShapeLst(self, classID, \xe2\xd8\xee\xf3):
        idx = None if \xe2\xd8\xee\xf3 == 2 else 2
        return CLASS2SHAPE[classID][idx - 1]

    
    class CAvatarWithTip(interface.CBoxObject, interface.CBase):
        
        def __init__(self, parent, photoarr, tip, idx, scale = 1):
            w = int(50 * scale)
            h = int(50 * scale)
            interface.CBoxObject.__init__(self, parent, w, h, 16777215, 0)
            self.m_PhotoImg = avatar.CSmallAvatarImg(self, photoarr, scale)
            self.MessageProcess()
            self.m_TipsStr = tip
            self.m_Idx = idx
            if idx >= 0:
                self.CreateChoosingImg()
                self.CreateEnterBG()
            

        
        def CreateEnterBG(self):
            self.m_EnterBG = ui.CImage(self, 'mainmenu/heroframe_hl.igs', interface.UIPath)
            self.m_EnterBG.SetZ(1000)
            self.m_EnterBG.SetShow(False)

        
        def CreateChoosingImg(self):
            self.m_ChoosingImg = ui.CImage(self, '\xd4\xd3\xcd\xbc/Choosing.igs', interface.UIPath)
            self.m_ChoosingImg.CreateCommand(10, 'animation')
            self.m_ChoosingImg.SetZ(100)
            (_, h) = self.GetSize()
            self.m_ChoosingImg.SetPos(0, h - 10)
            self.SetChoosing(False)

        
        def SetChoosing(self, isChoosing):
            if not getattr(self, 'm_ChoosingImg', None):
                return None
            
            self.m_ChoosingImg.SetShow(isChoosing)

        
        def ShowEnterBG(self, isShow):
            if not getattr(self, 'm_EnterBG', None):
                return None
            
            self.m_EnterBG.SetShow(isShow)

        
        def LeftUp(self):
            if self.m_Idx < 0:
                return None
            
            par = self.GetParent()
            par.ShowAvatarChange(self.m_Idx)

        
        def Enter(self):
            import wrapinterface
            if not self.m_TipsStr:
                return None
            
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, self.m_TipsStr, interface.FontLT14_3)
            self.m_TipsObj.SetOwner(self)
            self.ShowEnterBG(True)

        
        def Leave(self):
            self.ShowEnterBG(False)
            self.m_TipsObj = None


    
    def InitDlg(self):
        import style
        self.HideChangeImg()
        self.m_OwnPhotoImg = []
        self.m_ChangePhotoImg = []
        self.m_Change2Img = { }
        photo = avatar.GetHeroPhoto()
        for idx, shape in enumerate(self.m_OwnShape):
            if self.m_ChangeType == 1 and idx != 0:
                break
            
            if avatar.IsDefaultPhoto(photo):
                photo[3] = shape
            
            btnName = 'herobox%d' % (idx + 1)
            obj = self.GetObject(btnName)
            (x, y) = obj.GetPos()
            obj.SetShow(True)
            imgObj = self.CAvatarWithTip(self, photo, self.m_TipTextLst[idx], idx)
            (offx, offy) = style.GetIntTuple('dialog/herochange.dlg', 'data_initdlg_offset')
            x = x + offx
            y = y + offy
            imgObj.SetPos(x, y)
            if idx in self.m_ChangeDct:
                imgObj.LeftUp()
            
            self.m_OwnPhotoImg.append(imgObj)
        
        self.m_OwnPhotoImg[0].LeftUp()
        self.CreateGoldText()

    
    def CreateGoldText(self):
        import combmacro
        txt = '%s' % (2000, 5000)[self.m_ChangeType - 1]
        color = interface.COLOR_250
        self.m_GoldTxt = combmacro.CTEXT(interface.CTextObject, 'txt_Gold', self, txt, interface.FontLT16_2, color, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)

    
    class CAvatar(avatar.CSmallAvatarImg, interface.CBase):
        
        def __init__(self, parent, photoarr, idx, shape, scale = 1):
            avatar.CSmallAvatarImg.__init__(self, parent, photoarr, scale)
            self.MessageProcess()
            self.m_Idx = idx
            self.m_Shape = shape
            self.CreateConfirmImg()
            self.CreateEnterBG()

        
        def CreateEnterBG(self):
            self.m_EnterBG = ui.CImage(self, 'mainmenu/heroframe_hl.igs', interface.UIPath)
            self.m_EnterBG.SetZ(1000)
            self.m_EnterBG.SetShow(False)

        
        def CreateConfirmImg(self):
            self.m_ConfirmImg = ui.CImage(self, '\xd4\xd3\xcd\xbc/Done.igs', interface.UIPath)
            self.m_ConfirmImg.SetZ(100)
            (w, h) = self.GetSize()
            self.m_ConfirmImg.SetPos(w - 10, h - 10)
            self.SetConfirm(False)

        
        def Enter(self):
            import wrapinterface
            txt = SHAPE2NAME[self.m_Shape]
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3)
            self.m_TipsObj.SetOwner(self)
            self.m_EnterBG.SetShow(True)

        
        def Leave(self):
            self.m_TipsObj = None
            self.m_EnterBG.SetShow(False)

        
        def SetConfirm(self, isConfirm):
            if not getattr(self, 'm_ConfirmImg', None):
                return None
            
            self.m_ConfirmImg.SetShow(isConfirm)

        
        def LeftUp(self):
            par = self.GetParent()
            par.OnChangeAvatarClick(self.m_Idx, self.m_Shape)


    
    def ShowAvatarChange(self, idx):
        import style
        if len(self.m_OwnPhotoImg) > 1:
            for num, avatarImg in enumerate(self.m_OwnPhotoImg):
                avatarImg.SetChoosing(num == idx)
            
        
        shapeLst = None if self.m_ChangeType == 1 else self.m_CanChangeLst[idx]
        self.m_ChangePhotoImg = []
        for num, shape in enumerate(shapeLst):
            photo = avatar.GetShapeDefaultPhoto(shape)
            btnName = 'box_change%d' % (num + 1)
            obj = self.GetObject(btnName)
            (x, y) = obj.GetPos()
            obj.SetShow(True)
            imgObj = self.CAvatar(self, photo, idx, shape)
            (offx, offy) = style.GetIntTuple('dialog/herochange.dlg', 'data_initdlg_offset')
            x = x + offx
            y = y + offy
            imgObj.SetPos(x, y)
            self.m_ChangePhotoImg.append(imgObj)
        
        num = 0
        if self.m_ChangeType == 2:
            shape = self.m_ChangeDct.get(idx)
            for i, iShape in enumerate(shapeLst):
                if iShape == shape:
                    num = i
                    continue
            
        
        self.m_ChangePhotoImg[num].LeftUp()

    
    def OnChangeAvatarClick(self, idx, shape):
        self.ShowAni(idx, shape)
        self.ShowChange2Imge(idx, shape)
        if self.m_ChangeType == 2:
            self.m_ChangeDct[idx] = shape
            for img in self.m_ChangePhotoImg:
                img.SetConfirm(img.m_Shape == shape)
            
        

    
    def ShowChange2Imge(self, idx, shape):
        ownPhoto = avatar.GetHeroPhoto()
        if avatar.IsDefaultPhoto(ownPhoto):
            ownPhoto[3] = self.m_OwnShape[idx]
        
        infoLst = [
            (ownPhoto, 'box_own%s' % (idx + 1), self.m_TipTextLst[idx]),
            (avatar.GetShapeDefaultPhoto(shape), 'box_to%s' % (idx + 1), SHAPE2NAME[shape])]
        imgLst = []
        for photo, btnName, txt in infoLst:
            (x, y) = self.GetObject(btnName).GetPos()
            imgObj = self.CAvatarWithTip(self, photo, txt, -1, scale = 0.6)
            imgObj.SetPos(x, y)
            imgLst.append(imgObj)
        
        self.GetObject('img_change%d' % (idx + 1)).SetShow(True)
        self.m_Change2Img[idx] = imgLst

    
    def ShowAni(self, idx, shape):
        import walker
        self.m_Dir = 0
        (ownDesc, otherDesc) = self.Get2Desc(self.m_ColorLst[idx])
        aniDct = {
            'm_Ani1': (self.m_OwnShape[idx], ownDesc, 'img_Photo1'),
            'm_Ani2': (shape, otherDesc, 'img_Photo2') }
        for shape, desc, objName in aniDct.items():
            ani = walker.CFakeRole(self, 0, shape, desc)
            (x, y, w, h) = self.GetLocData(objName)
            ani.SetPos(x + w / 2, y + h - 20)
            setattr(self, attr, ani)
        

    
    def Get2Desc(self, color):
        import copy
        ownDesc = { }
        for sType, arr in hero.g_Prop.m_Desc.items():
            if sType in ('wing', 'weapon', 'fairy'):
                ownDesc[sType] = copy.deepcopy(arr)
                continue
        
        otherDesc = copy.deepcopy(ownDesc)
        ownDesc['color'] = color
        otherDesc['color'] = [
            0,
            0,
            0]
        return (ownDesc, otherDesc)

    
    def OnChange(self):
        needGold = None if self.m_ChangeType == 1 else 5000
        if hero.g_Prop.m_Gold < needGold:
            import usermacro
            usermacro.PROMPT_MSG('\xa7A\xb7\xed\xabe\xaa\xba\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa4\xa3\xa8\xac%d\xa1A\xb5L\xaak\xb6i\xa6\xe6\xa4\xc1\xb4\xab' % needGold)
            return None
        
        shapeLst = []
        if self.m_ChangeType == 1:
            shapeLst.append(self.m_ChangeShape)
            txt = '\xa4\xc1\xb4\xab\xab\xe1\xad\xec\xa6\xb3\xaa\xba\xb3y\xab\xac\xa9M\xacV\xa6\xe2\xa4\xe8\xae\xd7\xb1N\xa4\xa3\xabO\xafd\xa1A\xa6A\xa6\xb8\xa4\xc1\xb4\xab\xbb\xdd\xadn\xad\xab\xb7s\xc1\xca\xb6R\xa1A\xbdT\xa9w\xadn\xaa\xe1\xb6O#B2000#n\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xb1N\xb3y\xab\xac\xa4\xc1\xb4\xab\xac\xb0#B%s#n\xb6\xdc\xa1H' % SHAPE2NAME[self.m_ChangeShape]
        elif len(self.m_ChangeDct) < len(self.m_OwnShape):
            import usermacro
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xc1\xd9\xa6\xb3\xa8S\xa6\xb3\xbf\xef\xbe\xdc\xb7s\xb3y\xab\xac\xaa\xba\xc2\xbe\xb7~\xa1A\xbd\xd0\xa5\xfd\xb6i\xa6\xe6\xbf\xef\xbe\xdc')
            return None
        
        keyLst = sorted(self.m_ChangeDct.keys())
        txt = '\xbd\xd0\xb9\xef\xa8\xa4\xa6\xe2\xaa\xba\xc2\xe0\xb4\xab\xb6i\xa6\xe6\xb3\xcc\xab\xe1\xaa\xba\xbdT\xbb{#r'
        for idx in keyLst:
            shape = self.m_ChangeDct[idx]
            shapeLst.append(shape)
            txt += '#B%s#n \xa4\xc1\xb4\xab\xac\xb0 #B%s#n #r' % (self.m_ConfirmTxt[idx], SHAPE2NAME[shape])
        
        txt += '\xc2\xe0\xb4\xab\xa8\xa4\xa6\xe2\xab\xe1\xad\xec\xc0Y\xb9\xb3\xa1A\xacV\xa6\xe2\xa1A\xb3\xa1\xa4\xc0\xa9\xca\xa7O\xb1M\xc4\xdd\xba\xd9\xbf\xd7\xb1N\xaa\xbd\xb1\xb5\xa7R\xb0\xa3\xa1I#r\xbdT\xa9w\xadn\xaa\xe1\xb6O#B5000#n\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xb6i\xa6\xe6\xc2\xe0\xb4\xab\xb6\xdc\xa1H'
        
        def doChange(dlg):
            obj = dlg.m_ShadowObj.Get()
            import nethero
            nethero.C2SheroChange(obj.m_ChangeType, shapeLst)
            obj.CloseWindow()

        import commondialog
        dlg = commondialog.ShowMessageBox(interface.Replace(txt), ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (doChange, None))
        dlg.m_ShadowObj = interface.CShadowObject(self)

    
    def DoSpecialAct(self, idx):
        if not getattr(self, 'm_Ani1', None) and getattr(self, 'm_Ani2', None):
            return None
        
        if idx == 0:
            cDir = None if self.m_Ani1.m_State not in ('attack', 'magic') else 2
            self.m_Dir = (self.m_Dir + cDir) % 8
            self.m_Ani1.SetDirection(self.m_Dir * 4)
            self.m_Ani2.SetDirection(self.m_Dir * 4)
            return None
        
        state = ('attack', 'magic')[idx - 1]
        self.m_Ani1.SetState(state)
        self.m_Ani2.SetState(state)

    
    def OnButtonEnter(self, btn):
        txtInfo = {
            4: '\xb1\xdb\xc2\xe0',
            5: '\xa7\xf0\xc0\xbb',
            6: '\xacI\xaak' }
        txt = txtInfo.get(btn.m_MsgID)
        if not txt:
            return None
        
        import wrapinterface
        self.m_Tips = wrapinterface.CTextTips(None, -1, txt, interface.FontLT14_3)
        self.m_Tips.SetOwner(btn)

    
    def OnButtonLeave(self, btn):
        self.m_Tips = None

    
    def CloseWindow(self):
        global g_HeroChange
        g_HeroChange = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid in (2, 3):
            self.SetChangeType(msgid - 1)
        elif msgid in (4, 5, 6):
            self.DoSpecialAct(msgid - 4)
        elif msgid == 12:
            self.OnChange()
