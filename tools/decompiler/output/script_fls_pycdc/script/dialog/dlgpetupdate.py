# pycdc 交叉复核产物 · script.fls entry 4232
# co_filename(原始)='script/dialog/dlgpetupdate.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4232.pyc (Python 2.5)

import c2spetuicom
import combdialog
import interface
import permission
import style
import ui
import usermacro
SPECIAL_PET = (2710, 2720, 2890, 2900, 2910, 2920, 2930, 2940, 2960)
g_PetUpdate = None
g_PetPromote = None
g_PetUseBlood = None

def ModuleReset():
    global g_PetUpdate, g_PetPromote, g_PetUseBlood
    g_PetUpdate = None
    g_PetPromote = None
    g_PetUseBlood = None


def ShowSwitch():
    global g_PetUpdate, g_PetUpdate
    if g_PetUpdate:
        g_PetUpdate.Release()
        g_PetUpdate = None
    else:
        g_PetUpdate = CPetUpdate()


def Refresh(sGen, sAdd, sCash, sFightCash = ''):
    if g_PetUpdate is None:
        ShowSwitch()
    
    g_PetUpdate.Refresh(sGen, sAdd, sCash, sFightCash)


def AddPet(petid):
    if g_PetUpdate and petid:
        g_PetUpdate.ReleasePet(True)
        g_PetUpdate.ReleasePet(False)
        g_PetUpdate.RefreshPet(petid, True)
    

PET_APTI = (('Ability_Attack', 0), ('Ability_Con', 1), ('Ability_Speed', 2), ('Ability_Defense', 3), ('Ability_Magic', 4))
PET_UPD = ('Update_Flag', 'Update_Max')

def GetZZGrade(shape, ability, ability_name):
    import petzz
    data = petzz.GetData(shape)
    (mtype, tz, fz, gz, dz, sz, lift) = data
    dn = {
        'Ability_Attack': gz,
        'Ability_Defense': dz,
        'Ability_Con': tz,
        'Ability_Magic': fz,
        'Ability_Speed': sz }
    if ability_name not in dn:
        return 0
    
    if mtype == -1:
        return 0
    else:
        
        try:
            ability = int(ability)
        except:
            ability = 0

        result = 0
        if ability > 0:
            if mtype == 1:
                rate = 100 * ability / dn[ability_name]
            else:
                rate = (ability - gz) / 50
            if rate <= rate:
                pass
            elif (rate < 105 or mtype == 0) and rate == 0:
                result = 2
            elif rate <= rate:
                pass
            elif (rate < 110 or mtype == 0) and rate in (1, 2):
                result = 3
            elif rate <= rate:
                pass
            elif (rate < 115 or mtype == 0) and rate in (3, 4):
                result = 4
            elif (rate >= 115 or mtype == 0) and rate >= 5:
                result = 5
            else:
                result = 1
        
        return result


def IndexTrans(index):
    return (0, 3, 1, 4, 2)[index]


class CNotifyText(combdialog.CTextFrame, interface.CClickObject):
    
    def __init__(self, parent, data, msgid):
        combdialog.CTextFrame.__init__(self, parent, data)
        interface.CClickObject.__init__(self, msgid)

    
    def Enter(self):
        self.GetParent().OnEnter(self.m_MsgID)

    
    def Leave(self):
        
        try:
            par = self.GetParent()
        except SystemError:
            return None

        if not par:
            return None
        
        par.OnLeave(self.m_MsgID)

    
    def LeftDown(self):
        self.GetParent().LeftDown()

    
    def LeftUp(self):
        pass

    
    def RightUp(self):
        self.GetParent().RightUp()



class CPetUpdate(combdialog.CCombDialog):
    IS_PROMOTE = False
    DLD_PATH = 'dialog/pet_update.dlg'
    NORPETTEXT = '\xa7K\xb6O\xb6i\n\xa4\xc6\xa9\xd2\xbb\xdd\n\xb0\xc6\xc3d\xb3\xcc\n\xa7C\xb8\xea\xbd\xe8'
    HASRPETTEXT = '\xb6i\xa4\xc6\xa9\xd2\n\xbb\xdd\xb0\xc6\xc3d\n\xb3\xcc\xa7C\xb8\xea\n\xbd\xe8    '
    KEYWORD = '\xbb\xdd\xb8\xc9\xa8\xac'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, self.DLD_PATH)
        interface.Center(self)
        self.m_Text2Sample = { }
        for i, text in ((1, '\xa5i\xb6i\xa4\xc6'), (2, self.KEYWORD), (3, '\xb6i\xa4\xc6\xba\xa1')):
            obj = self.GetObject('text_%d' % i)
            if obj:
                self.m_Text2Sample[text] = obj
                obj.SetShow(False)
                continue
        
        self.m_Pets = {
            0: None,
            1: None }
        self.GetObject('update').Enable(False)
        self.InitAttrNotifyBox()
        self.SetRightSideText(self.NORPETTEXT)
        self.m_Percent = None if self.IS_PROMOTE else 0.95

    
    def SetRightSideText(self, text_lst):
        self.m_NotifyText = []
        textobj = self.GetObject('text_location')
        if type(text_lst) == str:
            textobj.SetText(text_lst)
        else:
            textobj.SetText('')
            obj = self.GetObject('secondary_attr')
            (x, y) = obj.GetPos()
            (w, _) = obj.GetSize()
            for idx, text in enumerate(text_lst):
                img = obj.GetImage(0, idx)
                (ix, iy) = img.GetPos()
                (iw, ih) = img.GetSize()
                textobj = combdialog.CTextFrame(self, [
                    0,
                    0,
                    0,
                    1,
                    1,
                    5,
                    '\xa4\xe5\xa5\xbb'])
                if textobj:
                    (tw, th) = textobj.GetSize()
                    tx = x + ix + w + 2
                    ty = y + iy + (ih - th) / 2
                    offx = style.GetInt(self.GetDlgPath(), 'data_offset_x')
                    textobj.SetPos(tx + offx, ty)
                    if text in self.m_Text2Sample:
                        sample = self.m_Text2Sample[text]
                        textobj.m_Align = sample.m_Align
                        textobj.m_Color = sample.m_Color
                        textobj.m_Font = sample.m_Font
                        textobj.m_Space = sample.m_Space
                        textobj.SetText(text)
                    
                    self.m_NotifyText.append(textobj)
                    notifybox = interface.CNotifyBox(self, tw, th, 0, 0, 11 + idx)
                    notifybox.SetPos(tx, ty)
                    self.m_NotifyText.append(notifybox)
                    continue
            

    
    def InitAttrNotifyBox(self):
        self.m_NotifyBoxes = []
        if interface.IsNewStyle():
            pass
        else:
            for objname, msgid in (('noname5', 15), ('noname7', 14), ('noname8', 13), ('noname10', 12), ('noname11', 11)):
                frameobj = self.GetObject(objname)
                (w, h) = frameobj.GetSize()
                (x, y) = frameobj.GetPos()
                notifybox = interface.CNotifyBox(self, w, h, alpha = 0, msgid = msgid)
                notifybox.SetPos(x, y)
                None.m_NotifyBoxes.append(notifybox)
            

    
    def Refresh(self, sGen, sAdd, sCash, sFightCash):
        self.m_Gen = sGen
        self.m_Add = sAdd
        self.m_Cash = sCash
        self.m_FightCash = sFightCash

    
    def RefreshPet(self, petid, isleft = True):
        self.m_CashTxt = None
        self.m_GenTxt = None
        self.GetObject('update').Enable(False)
        if isleft:
            objname = 'pet_left'
            attr_name = 'main_attr'
            if self.m_Pets[1] is None:
                self.SetRightSideText(self.HASRPETTEXT)
            
        else:
            objname = 'pet_right'
            attr_name = 'secondary_attr'
        import wrapinterface
        import pet
        key = int(not isleft)
        if self.m_Pets[key]:
            prev = self.m_Pets[key].m_ID
            pobj = pet.GetPet(prev)
            self.m_Pets[key].ReleaseAll()
            if pobj and pobj.m_ID != petid:
                self.RemoveDlgItem(pobj)
            
        
        pobj = pet.GetPet(petid)
        obj = self.GetObject(objname)
        petani = wrapinterface.CPetAni(self, pobj.GetProp('m_Shape'), pobj.GetProp('m_Desc'), (pobj.m_BirthKey & 255) << 8 | pobj.m_Key & 255)
        petani.m_ID = petid
        (x, y) = obj.GetPos()
        petani.SetPos(x + 7, y + 5)
        self.m_Pets[key] = petani
        
        def UpdateAttr(shadow, objname, propname, petid, cid, isNeed = (None, False)):
            dlg = shadow.Get()
            if dlg:
                import pet
                dlgobj = dlg.GetObject(objname)
                if not hasattr(dlgobj, 'm_Prop2Txt'):
                    dlgobj.m_Prop2Txt = { }
                
                pobj = pet.GetPet(petid)
                if pobj:
                    info = int(pobj.m_Name2PropItem[propname].GetInfo())
                    key = pobj.m_Key
                    if key & 8 != 0 and not isleft and dlg.IsTianShiDlg():
                        info -= 30
                        if info < 0:
                            info = 0
                        
                    
                    if info:
                        dlgobj.m_Prop2Txt[propname] = dlg.SetAttr(pobj, propname, info, dlgobj, cid, isNeed)
                        if not isNeed and objname != 'secondary_attr' and dlg.m_Pets[1] is None:
                            UpdateAttr(shadow, 'secondary_attr', propname, petid, cid, True)
                        
                        if dlg.m_Pets[0] is not None and dlg.m_Pets[1] is not None:
                            dlg.SetRightSideText('')
                            dlg.ShowPossible()
                        
                    else:
                        dlgobj.m_Prop2Txt[propname] = None
                else:
                    dlgobj.m_Prop2Txt[propname] = None
            

        for name, cid in PET_APTI:
            propitem = pobj.m_Name2PropItem[name]
            propitem.AddRefreshCallbackWithID('PetUpdate', UpdateAttr, interface.CShadowObject(self), attr_name, name, petid, cid)
        
        
        def showupdate(shadow, petid):
            dlg = shadow.Get()
            if dlg is None:
                return None
            
            import pet
            pobj = pet.GetPet(petid)
            flag = pobj.m_Name2PropItem['Update_Flag'].GetInfo()
            maxi = pobj.m_Name2PropItem['Update_Max'].GetInfo()
            flag = int(flag)
            maxi = int(maxi)
            if flag % 16 == 1:
                for i in range(1, 6):
                    dlg.ShowStar(i, (flag >> i * 4) % 16, (maxi >> i * 4) % 16)
                
            else:
                dlg.ClearStar(-1)
            if dlg.m_Pets[0] is not None and dlg.m_Pets[1] is not None:
                dlg.SetRightSideText('')
                dlg.ShowPossible()
            

        if isleft:
            for propname in PET_UPD:
                propitem = pobj.m_Name2PropItem[propname]
                propitem.RemoveRefreshCallbackWithID('PetUpdate')
                propitem.AddRefreshCallbackWithID('PetUpdate', showupdate, interface.CShadowObject(self), petid)
            
        
        if pobj.m_UpdateProp == False:
            import netpet
            netpet.C2SSummonView(pobj.m_ID)
        

    
    def SetAttr(self, pobj, propname, info, dlgobj, cid, isNeed):
        import dlgpetbase
        if isNeed:
            info = int(int(info) * self.m_Percent)
        
        zzgrade = GetZZGrade(pobj.GetProp('m_Shape'), str(info), propname)
        (x1, y1) = dlgobj.GetPos()
        (x2, y2) = dlgobj.GetImage(0, cid).GetPos()
        import pet
        Idx2Color = dict(enumerate([
            interface.COLOR_9] + pet.GetZZColor()))
        if pet.IsTrainPet(pobj.GetProp('m_Shape', 0)):
            (iColor, _) = dlgpetbase.GetTipsInfo(propname, pobj)
        else:
            iColor = Idx2Color[zzgrade]
        txtClass = None if interface.IsStyle1() else interface.COverstrikingTextObject
        txtobj = txtClass(self, str(info), interface.FontLT14_3, iColor, 0)
        txtobj.SetPos(x1 + x2 + 12, y1 + y2 + 3)
        if isNeed:
            notifyobj = interface.CNotifyBox(self, 45, 18, alpha = 0, msgid = 18)
        else:
            notifyobj = interface.CNotifyBox(self, 45, 18, alpha = 0, msgid = zzgrade)
        notifyobj.SetPos(x1 + x2, y1 + y2)
        return (txtobj, notifyobj)

    
    def ShowPossible(self):
        mpetid = self.m_Pets[0].m_ID
        spetid = self.m_Pets[1].m_ID
        import pet
        mpet = pet.GetPet(mpetid)
        spet = pet.GetPet(spetid)
        if mpet is None or spet is None:
            return None
        
        flag = mpet.GetProp('Update_Flag')
        maxi = mpet.GetProp('Update_Max')
        lst = [
            None] * 5
        for _, i in PET_APTI:
            idx = IndexTrans(i)
            if self.IS_PROMOTE and flag % 16 != 1 or (flag >> (i + 1) * 4) % 16 < (maxi >> (i + 1) * 4) % 16:
                propname = PET_APTI[idx][0]
                minfo = mpet.GetProp(propname)
                sinfo = spet.GetProp(propname)
                key = spet.m_Key
                if key & 8 != 0 and self.IsTianShiDlg():
                    sinfo -= 30
                
                if int(sinfo) >= int(int(minfo) * self.m_Percent):
                    text = '\xa5i\xb6i\xa4\xc6'
                else:
                    text = self.KEYWORD
            else:
                text = '\xb6i\xa4\xc6\xba\xa1'
            lst[idx] = text
        
        self.SetRightSideText(lst)

    
    def ReleasePet(self, isleft):
        if isleft:
            petani = self.m_Pets[0]
            self.m_Pets[0] = None
            objname = 'main_attr'
            self.SetRightSideText(self.NORPETTEXT)
        else:
            petani = self.m_Pets[1]
            self.m_Pets[1] = None
            objname = 'secondary_attr'
            if self.m_Pets[0] is not None:
                self.SetRightSideText(self.HASRPETTEXT)
            
        obj = self.GetObject(objname)
        obj.m_Prop2Txt = { }
        if petani:
            petid = petani.m_ID
            petani.ReleaseAll()
            import pet
            pobj = pet.GetPet(petid)
            if pobj:
                self.RemoveDlgItem(pobj)
            
        

    
    def RemoveDlgItem(self, pobj):
        for arr, _ in PET_APTI:
            propitem = pobj.m_Name2PropItem[arr]
            propitem.RemoveRefreshCallbackWithID('PetUpdate')
        
        for propname in PET_UPD:
            propitem = pobj.m_Name2PropItem[propname]
            propitem.RemoveRefreshCallbackWithID('PetUpdate')
        

    
    def ShowStar(self, idx, times, maxi):
        obj = self.GetObject('main_attr')
        (ox, oy) = obj.GetPos()
        (ix, iy) = obj.GetImage(0, (0, 3, 1, 4, 2)[idx - 1]).GetPos()
        x = ox + ix + 55
        y = oy + iy + 3
        if times >= maxi:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xd0\xc71.igs')
        else:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xd0\xc72.igs')
        if not hasattr(self, 'm_Stars'):
            self.m_Stars = { }
        
        img = ui.CImage(self, star_path, interface.UIPath)
        offy = style.GetInt(self.GetDlgPath(), 'data_offset_y')
        img.SetPos(x, y + offy)
        (w, h) = img.GetSize()
        box = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 20 + idx)
        box.SetPos(x, y)
        self.m_Stars[idx] = (img, box, times, maxi)

    
    def ClearStar(self, idx):
        if idx in getattr(self, 'm_Stars', { }):
            del self.m_Stars[idx]
        elif idx == -1:
            self.m_Stars = { }
        

    
    def OnEnter(self, msgid):
        tips = None
        import wrapinterface
        if msgid <= msgid:
            pass
        elif msgid <= 15 and self.m_Pets[0]:
            (attr_name, _) = PET_APTI[msgid - 11]
            import pet
            pobj = pet.GetPet(self.m_Pets[0].m_ID)
            attr_value = pobj.m_Name2PropItem[attr_name].GetInfo()
            flag = pobj.m_Name2PropItem['Update_Flag'].GetInfo()
            tips = '\xb6i\xa4\xc6\xbb\xdd\xb9F\xa8\xec#G%i#n' % int(int(attr_value) * self.m_Percent)
        elif msgid == 16:
            tips = '\xba\xa1\xa8\xac\xa5D\xc3d\xb6i\xa4\xc6\xbb\xdd\xa8D'
        elif msgid == 17:
            tips = '\xa6\xb9\xb6\xb5\xb8\xea\xbd\xe8\xa4w\xb8g\xb6i\xa4\xc6\xba\xa1'
        elif msgid == 18:
            tips = '\xb0\xc6\xc3d\xa9\xd2\xbb\xdd\xb3\xcc\xa7C\xb8\xea\xbd\xe8'
        elif msgid >= 20:
            idx = msgid - 20
            if idx in getattr(self, 'm_Stars', { }):
                (img, box, times, maxi) = self.m_Stars[idx]
                if times < maxi:
                    tips = '\xad\xb8\xaa@\xb6i\xa4\xc6%d/%d' % (times, maxi)
                elif maxi == maxi:
                    pass
                elif maxi == 0:
                    tips = '\xa4w\xad\xb8\xaa@'
                else:
                    tips = '\xa4w\xb9F\xad\xb8\xaa@\xb6i\xa4\xc6\xa4W\xad\xad%d/%d' % (times, maxi)
            
        elif msgid < msgid:
            pass
        elif msgid <= 5:
            import pet
            tips = pet.STRING_ZZ[msgid - 1]
        
        if tips is not None:
            self.m_Tips = wrapinterface.CTextTips(None, -1, tips, interface.FontLT14_3)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def RightUp(self):
        self.OnLeave(0)
        self.OnMessage(2)

    
    def RefreshAbility(self, idx):
        pobj = self.m_Pets[0]
        if pobj is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xa5D\xc3d#n')
            return None
        
        mid = pobj.m_ID
        pobj = self.m_Pets[1]
        if pobj is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xb0\xc6\xc3d#n')
            return None
        
        sid = pobj.m_ID
        import pet
        import petdata
        mpet = pet.GetPet(mid)
        spet = pet.GetPet(sid)
        (attr, attrindex) = PET_APTI[idx]
        ma = '%d' % mpet.GetProp(attr)
        isa = spet.GetProp(attr)
        key = spet.m_Key
        if key & 8 != 0 and self.IsTianShiDlg():
            isa -= 30
            if isa <= 0:
                isa = 0
            
        
        sa = '%d' % isa
        lv = '%d' % petdata.GetData(mpet.GetProp('m_Shape'))['carry_grade']
        gen = self.m_Gen
        gen = gen.replace('$iGen1', sa)
        gen = gen.replace('$iGen2', ma)
        gen = gen.replace('$iSumLV', lv)
        v1 = eval(gen)
        if v1 >= 0:
            fight_cash = None
        else:
            fight_cash = self.m_FightCash
        sadd = self.m_Add
        sadd = sadd.replace('$iGen1', sa)
        sadd = sadd.replace('$iGen2', ma)
        sadd = sadd.replace('$iSumLV', lv)
        v2 = max(0, eval(sadd))
        cash = self.m_Cash
        cash = cash.replace('$iGen1', sa)
        cash = cash.replace('$iGen2', ma)
        cash = cash.replace('$iSumLV', lv)
        cash = cash.replace('$iXYSum', '%d' % int(mpet.GetProp('m_Shape') in SPECIAL_PET))
        v3 = eval(cash)
        if fight_cash:
            fight_cash = fight_cash.replace('$iGen1', sa)
            fight_cash = fight_cash.replace('$iGen2', ma)
            fight_cash = fight_cash.replace('$zzc', '%s' % int(int(ma) * self.m_Percent - int(sa)))
            fight_cash = fight_cash.replace('$iSumLV', lv)
            import petzz
            (_, tz, fz, gz, dz, sz, _) = petzz.GetData(mpet.GetProp('m_Shape'))
            fight_cash = fight_cash.replace('$iLimit', '%d' % int(1.17 * (gz, tz, sz, dz, fz)[idx] + 130))
            base_fc = 500000
            v4 = max(0, min(2000, eval(fight_cash) / base_fc + 1)) * 500000
        else:
            v4 = 0
        import combmacro
        self.m_GenTxt = combmacro.CTEXT(interface.CTextObject, 'gen', self, '%d' % v2, interface.FontLT14_3, interface.COLOR_12)
        self.m_CashTxt = combmacro.CTEXT(interface.CTextObject, 'cash', self, '%d' % v3, interface.FontLT14_3, interface.COLOR_12)
        self.m_FightCashTxt = combmacro.CTEXT(interface.CTextObject, 'fight_cash', self, '%d' % v4, interface.FontLT14_3, interface.COLOR_12)
        self.m_FightCashVal = v4
        self.GetObject('update').Enable(True)

    
    def DelayAutoSelect(self, petid):
        import pet
        pobj = pet.GetPet(petid)
        flag = pobj.GetProp('Update_Flag')
        maxi = pobj.GetProp('Update_Max')
        if not pobj.m_UpdateProp:
            return (petid,)
        
        if flag == 0 and maxi == 0:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xa5l\xb3\xea\xc3~\xa5\xbc\xad\xb8\xaa@\xb9L\xa1A\xb5L\xaak\xb6i\xa4\xc6')
            return None
        
        btnnames = ('sel1', 'sel3', 'sel5', 'sel2', 'sel4')
        i2index = {
            1: 1,
            2: 3,
            3: 5,
            4: 2,
            5: 4 }
        isDone = True
        for i in xrange(1, 6):
            index = i2index[i]
            btn = self.GetObject(btnnames[i - 1])
            btn.SetSelect(False)
            times = (flag >> index * 4) % 16
            maxs = (maxi >> index * 4) % 16
            if times < maxs:
                btn.SetSelect(True)
                if self.m_Pets[1]:
                    self.RefreshAbility(i - 1)
                
                isDone = False
                break
                continue
        
        if isDone:
            iPetShape = pobj.GetProp('m_Shape')
            if pet.IsTrainPet(iPetShape):
                sTips = '\xb8\xd3\xa5l\xb3\xea\xc3~\xa4\xa3\xa5i\xb6i\xa4\xc6'
            else:
                sTips = '\xa6\xb9\xa5l\xb3\xea\xc3~\xa4w\xad\xb8\xaa@\xb6i\xa4\xc6\xa7\xb9\xa5\xfe\xa1A\xa4\xa3\xa5i\xb6i\xa4\xc6\xa1I'
            usermacro.PROMPT_MSG(sTips)
        

    
    def OnMessage(self, msgid):
        if msgid == 2:
            ShowSwitch()
        elif msgid == 3:
            
            def DoDelayAutoSelect(obj, petid):
                obj.DelayAutoSelect(petid)

            
            def CallBack(pets):
                if len(pets) == 1:
                    petid = pets[0]
                    if self.m_Pets[1] and self.m_Pets[1].m_ID == petid:
                        usermacro.PROMPT_MSG('\xa5D\xc3d\xa4\xa3\xb1o\xbbP\xb0\xc6\xc3d\xac\xdb\xa6P')
                        return None
                    
                    self.RefreshPet(pets[0], True)
                    self.CreatePyCommand(10, DoDelayAutoSelect, petid)
                else:
                    usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xa5D\xc3d#n')

            import dlggive
            dlggive.CallbackGive('\xa9\xf1\xa4J\xa5D\xc3d', CallBack)
        elif msgid == 4:
            
            def CallBack(pets):
                if len(pets) == 1:
                    petid = pets[0]
                    if self.m_Pets[0] and self.m_Pets[0].m_ID == petid:
                        usermacro.PROMPT_MSG('\xb0\xc6\xc3d\xa4\xa3\xb1o\xbbP\xa5D\xc3d\xac\xdb\xa6P')
                        return None
                    
                    self.RefreshPet(petid, False)
                    slt = self.GetSelect()
                    if self.m_Pets[0] and slt:
                        self.RefreshAbility(slt - 1)
                    
                else:
                    usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xb0\xc6\xc3d#n')

            import dlggive
            dlggive.CallbackGive('\xa9\xf1\xa4J\xb0\xc6\xc3d', CallBack)
        elif msgid == 5:
            
            def Ok(dlg):
                C2SPetUpdate(dlg.m_MID, dlg.m_SID, dlg.m_Idx)

            pobj = self.m_Pets[0]
            if pobj is None:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xa5D\xc3d#n')
                return None
            
            mid = pobj.m_ID
            pobj = self.m_Pets[1]
            if pobj is None:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xb0\xc6\xc3d#n')
                return None
            
            sid = pobj.m_ID
            for i in range(1, 6):
                obj = self.GetObject('sel%d' % i)
                if obj and obj.m_Selected:
                    if getattr(self, 'm_FightCashVal', 0):
                        import commondialog
                        dlg = commondialog.ShowMessageBox('\xb8\xd3\xb0\xc6\xc3d\xa6\xb9\xb6\xb5\xb8\xea\xbd\xe8\xbb\xdd\xb8\xc9\xa8\xac\xa1A\xb1N\xa6\xa9\xb0\xa3#R%s#n\xa8\xe2\xa9\xe8\xa5\xce\xaa\xf7\xa1A\xacO\xa7_\xbdT\xbb{\xb8\xc9\xa8\xac\xa1H' % self.m_FightCashVal, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (Ok, None))
                        dlg.m_MID = mid
                        dlg.m_SID = sid
                        dlg.m_Idx = i
                    else:
                        C2SPetUpdate(mid, sid, i)
                    return None
                    continue
            
        elif msgid <= msgid:
            pass
        elif msgid <= 10:
            self.RefreshAbility(msgid - 6)
        else:
            print 'CPetUpdate::OnMessage %d' % msgid

    
    def GetSelect(self):
        btnnames = ('sel1', 'sel3', 'sel5', 'sel2', 'sel4')
        for i, objname in enumerate(btnnames):
            btn = self.GetObject(objname)
            if btn.IsSelected():
                return i + 1
                continue
        

    
    def IsTianShiDlg(self):
        return True



def C2SPetUpdate(main_pid, secondary_id, idx):
    print '\xad\xb8\xaa@ %s \xc4\xdd\xa9\xca' % {
        1: '\xa7\xf0',
        2: '\xa8\xbe',
        3: '\xc5\xe9',
        4: '\xaak',
        5: '\xb3t' }[idx]
    import net
    if permission.IsOpenUICom():
        netobj = c2spetuicom.GetPetUIComNetObj(8)
    else:
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_OPEN_UI)
        netobj.PacketAddI(94, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(main_pid, 4)
    netobj.PacketAddI(secondary_id, 4)
    netobj.PacketAddI(idx, 1)
    netobj.PacketSend()


def C2SGetUpdate(petid):
    import net
    if permission.IsOpenUICom():
        netobj = c2spetuicom.GetPetUIComNetObj(8)
    else:
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_OPEN_UI)
        netobj.PacketAddI(94, 1)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(petid, 4)
    netobj.PacketSend()


def ShowPromote():
    global g_PetPromote
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpetupdatenew
        dlgpetupdatenew.ShowPromote()
        return None
    
    if g_PetPromote:
        ClosePromote()
    else:
        g_PetPromote = CPetPromote()


def ClosePromote():
    global g_PetPromote
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.ClosePromote()
        return None
    
    g_PetPromote.Release()
    g_PetPromote = None


def AddPromotePet(main_pid, secondary_id):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.AddPromotePet(main_pid, secondary_id)
        return None
    
    if g_PetPromote:
        if secondary_id == 0:
            g_PetPromote.ReleasePet(False)
        elif secondary_id > 0:
            g_PetPromote.RefreshPromotePet(secondary_id, False)
        
        if main_pid == 0:
            g_PetPromote.ReleasePet(True)
        elif main_pid > 0:
            g_PetPromote.RefreshPromotePet(main_pid, True)
        
    


def SetCash(cash):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.SetCash(cash)
        return None
    
    if g_PetPromote:
        g_PetPromote.ShowCash(cash)
    


def SetPromoteZZ(zz):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.SetPromoteZZ(zz)
        return None
    
    if g_PetPromote:
        g_PetPromote.SetPromoteZZ(zz)
    


def SetMaxZZ(maxzz):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.SetMaxZZ(maxzz)
        return None
    
    if g_PetPromote:
        g_PetPromote.SetMaxZZ(maxzz)
    


def ChoiceZZ(zz):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.ChoiceZZ(zz)
        return None
    
    if g_PetPromote:
        for i in xrange(1, 6):
            obj = g_PetPromote.GetObject('sel%d' % i)
            obj.SetSelect(i == zz)
        
        g_PetPromote.m_Star = None
        g_PetPromote.m_Box = None
        g_PetPromote.m_Promp = zz
    


def SetArrange(down, up):
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.SetArrange(down, up)
        return None
    
    if g_PetPromote:
        g_PetPromote.ShowRange((down, up))
        g_PetPromote.SetCheck()
    


def PromoteOK():
    import dlgpetcenter
    import dlgpetupdatenew
    if dlgpetcenter.IsTest():
        dlgpetupdatenew.PromoteOK()
        return None
    
    if g_PetPromote:
        petid = g_PetPromote.m_Pets[0].m_ID
        g_PetPromote.ReleasePet(True)
        g_PetPromote.ReleasePet(False)
        g_PetPromote.RefreshPet(petid, True)
        g_PetPromote.ShowRange(None)
        for i in xrange(1, 6):
            obj = g_PetPromote.GetObject('sel%d' % i)
            obj.SetSelect(False)
        
        g_PetPromote.m_Promp = 0
        g_PetPromote.m_Star = None
        g_PetPromote.m_Box = None
    


class CPetPromote(CPetUpdate):
    IS_PROMOTE = True
    DLD_PATH = 'dialog/pet_prompt.dlg'
    NORPETTEXT = '\xa9\xf1\xa4J\xa5D\n\xc3d\xa7Y\xa5i\n\xacd\xac\xdd\xb0\xc6\n\xc3d\xa9\xd2\xbb\xdd\n\xb8\xea\xbd\xe8  '
    KEYWORD = '\xa5\xbc\xba\xa1\xa8\xac'
    
    def RefreshPet(self, petid, isleft = True):
        import nethero
        if isleft:
            nethero.C2SAddMainPet(petid)
        elif self.m_Pets[0] is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xa5D\xc3d#n')
            return None
        else:
            import pet
            import petdata
            mpet = pet.GetPet(self.m_Pets[0].m_ID)
            spet = pet.GetPet(petid)
            nethero.C2SAddPet(mpet.m_ID, petid)

    
    def RefreshPromotePet(self, petid, isleft = True):
        if isleft:
            if self.m_Pets[1]:
                self.ReleasePet(False)
            
            if self.m_Pets[0] and self.m_Pets[0].m_ID != petid:
                self.ShowCash(None)
            
            self.ShowRange(None)
            self.m_Star = None
            self.m_Box = None
        
        self.m_Promp = 0
        for i in xrange(1, 6):
            obj = self.GetObject('sel%d' % i)
            obj.SetSelect(False)
        
        self.GetObject('update').Enable(False)
        pet = self.m_Pets[{
            True: 0,
            False: 1 }[isleft]]
        CPetUpdate.RefreshPet(self, petid, isleft)
        self.ClickStar()

    
    def PromoteCheck(self, idx):
        import nethero
        pobj = self.m_Pets[0]
        if pobj is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xa5D\xc3d#n')
            return None
        
        mid = pobj.m_ID
        pobj = self.m_Pets[1]
        if pobj is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xb0\xc6\xc3d#n')
            return None
        
        sid = pobj.m_ID
        if idx:
            nethero.C2SChoiceZZ(mid, sid, idx)
        elif hasattr(self, 'm_Promp'):
            if self.m_Promp < self.m_Promp:
                pass
            elif self.m_Promp <= 5:
                nethero.C2SPromtePet(mid, sid, self.m_Promp)
            else:
                usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xbb\xdd\xadn\xb6i\xa4\xc6\xaa\xba\xb8\xea\xbd\xe8')

    
    def ShowRange(self, ranges):
        
        try:
            (x, y) = ranges
        except:
            self.m_RangeTxt = None
            return None

        import combmacro
        self.m_RangeTxt = combmacro.CTEXT(interface.CTextObject, 'gen', self, '%d~%d' % (x, y), interface.FontLT14_3, interface.COLOR_12)
        self.m_RangeTxt.m_Range = ranges

    
    def ShowCash(self, cash):
        if cash:
            import combmacro
            import wrapinterface
            self.m_CashTxt1 = combmacro.CEDIT(wrapinterface.CNumberEdit, 'cash', self, interface.COLOR_5, interface.FontLT14_3)
            self.m_CashTxt1.m_IsMoney = False
            self.m_CashTxt1.SetText('%d' % cash)
            self.m_CashTxt1.Enable(False)
        else:
            self.m_CashTxt1 = None

    
    def OnSelect(self, btn):
        return False

    
    def SetCheck(self):
        check = True
        if self.m_Pets[0] is None or self.m_Pets[1] is None:
            check = False
        else:
            for i in xrange(1, 6):
                obj = self.GetObject('sel%d' % i)
                if obj and obj.m_Selected:
                    break
                    continue
            else:
                check = False
        self.GetObject('update').Enable(check)
        if hasattr(self, 'm_MainZZ') and self.m_MainZZ:
            self.ShowZZStar(self.m_MainZZ)
        

    
    def ClickStar(self):
        if self.m_Pets[0] and self.m_Pets[1] and hasattr(self, 'm_MainZZ') and self.m_MainZZ:
            self.OnMessage({
                1: 6,
                2: 9,
                3: 7,
                4: 10,
                5: 8 }[self.m_MainZZ])
        

    
    def SetPromoteZZ(self, zz):
        self.m_MainZZ = zz

    
    def SetMaxZZ(self, zz):
        self.m_MaxZZ = zz

    
    def ShowZZStar(self, zz):
        pobj = self.m_Pets[0]
        if zz <= 0 and zz > 5 or pobj is None:
            return None
        
        import pet
        pobj = pet.GetPet(pobj.m_ID)
        if pobj is None:
            return None
        
        obj = self.GetObject('main_attr')
        (ox, oy) = obj.GetPos()
        idx = (0, 3, 1, 4, 2)[zz - 1]
        (ix, iy) = obj.GetImage(0, idx).GetPos()
        x = ox + ix + 40
        y = oy + iy + 3
        (attr_name, _) = PET_APTI[idx]
        info = int(pobj.m_Name2PropItem[attr_name].GetInfo())
        if info >= self.m_MaxZZ:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xbb\xc6\xd0\xc71.igs')
        else:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xbb\xc6\xd0\xc72.igs')
        self.m_Star = ui.CImage(self, star_path, interface.UIPath)
        self.m_Star.SetPos(x, y)
        (w, h) = self.m_Star.GetSize()
        (x, y) = self.m_Star.GetPos()
        self.m_Box = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 50)
        self.m_Box.SetPos(x, y)

    
    def DelayAutoSelect(self, petid):
        pass

    
    def IsTianShiDlg(self):
        return False

    
    def OnEnter(self, msgid):
        CPetUpdate.OnEnter(self, msgid)
        if msgid == 50:
            import wrapinterface
            self.m_Tips = wrapinterface.CTextTips(None, -1, '\xb6i\xa4\xc6', interface.FontLT14_3)
        

    
    def OnMessage(self, msgid):
        if msgid == 2:
            ClosePromote()
        elif msgid == 3:
            CPetUpdate.OnMessage(self, 3)
        elif msgid == 4:
            
            def CallBack(pets):
                if len(pets) == 1:
                    petid = pets[0]
                    if self.m_Pets[0] and self.m_Pets[0].m_ID == petid:
                        usermacro.PROMPT_MSG('\xb0\xc6\xc3d\xa4\xa3\xb1o\xbbP\xa5D\xc3d\xac\xdb\xa6P')
                        return None
                    
                    self.RefreshPet(petid, False)
                    slt = self.GetSelect()
                    if self.m_Pets[0] and slt:
                        self.PromoteCheck({
                            1: 1,
                            2: 3,
                            3: 5,
                            4: 2,
                            5: 4 }[slt])
                    
                else:
                    usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc#Y\xa4@\xad\xd3\xb0\xc6\xc3d#n')

            import dlggive
            dlggive.CallbackGive('\xa9\xf1\xa4J\xb0\xc6\xc3d', CallBack)
        elif msgid == 5:
            self.PromoteCheck(0)
        elif msgid <= msgid:
            pass
        elif msgid <= 10:
            self.PromoteCheck({
                6: 1,
                7: 3,
                8: 5,
                9: 2,
                10: 4 }[msgid])
            obj = self.GetObject('sel%d' % {
                6: 1,
                7: 3,
                8: 5,
                9: 2,
                10: 4 }[msgid])
            obj.SetSelect(False)
        else:
            print 'CPetPromote::OnMessage %d' % msgid
