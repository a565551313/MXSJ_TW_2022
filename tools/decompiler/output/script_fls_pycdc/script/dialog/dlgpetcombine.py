# pycdc 交叉复核产物 · script.fls entry 4002
# co_filename(原始)='script/dialog/dlgpetcombine.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4002.pyc (Python 2.5)

import C_sys
import combdialog
import interface
import pet
import style
import usermacro
import wrapinterface
g_PetChoose = None
g_PetCombineDlg = None
PET_ADV_STATE = (('Ability_Attack', 'att_abi1', 'att_abi2'), ('Ability_Defense', 'def_abi1', 'def_abi2'), ('Ability_Con', 'con_abi1', 'con_abi2'), ('Ability_Magic', 'mag_abi1', 'mag_abi2'), ('Ability_Speed', 'spe_abi1', 'spe_abi2'), ('m_Life', 'life1', 'life2'))

def ModuleReset():
    global g_PetChoose, g_PetCombineDlg
    g_PetChoose = None
    g_PetCombineDlg = None


class CPetChoose(combdialog.CCombDialog):
    
    def __init__(self, usedid):
        '''
\t\t:param usedid: \xa6C\xaa\xed,\xa6s\xa9\xf1\xa4w\xb8g\xa9\xf1\xa4J\xc3d\xaa\xab\xbf\xc4\xa6X\xac\xc9\xad\xb1\xaa\xba\xc3d\xaa\xabid
\t\t'''
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/petchoose.dlg')
        interface.Center(self)
        self.m_TipsText = interface.CTextObject(self.GetObject('msgs'), '\xbd\xd0\xbf\xef\xbe\xdc\xb1z\xadn\xa9\xf1\xa4J\xaa\xba\xa5l\xb3\xea\xc3~', interface.FontLT14_3, interface.COLOR_4)
        self.m_TipsText.SetPos(60, 20)
        self.m_UsedID = usedid
        self.m_PetList = self.GetObject('petlist')
        for i, petobj in enumerate(self.GetSuitPets()):
            it = self.m_PetList.AddTextItem(getattr(petobj.m_Prop, 'm_Name'))
            it.m_ID = petobj.m_ID
            if it.m_ID in self.m_UsedID:
                it.SetTextColor(16711680)
            
            it.m_Shape = getattr(petobj.m_Prop, 'm_Shape')
            it.m_Desc = getattr(petobj.m_Prop, 'm_Desc')
            it.m_Key = (petobj.m_BirthKey & 255) << 8 | petobj.m_Key & 255
        
        self.m_PetList.ResetItems()
        self.m_PetList.ResetScrollBar()
        self.m_PetAni = None
        self.m_SelectID = -1

    
    def GetAnotherCarryGrade(self):
        import petdata
        petobj = getattr(g_PetCombineDlg, 'GetAnotherPet()', None)
        if petobj and petdata.GetData(petobj.m_Prop.m_Shape)['carry_grade'] <= 55:
            return petdata.GetData(petobj.m_Prop.m_Shape)['carry_grade']
        

    
    def GetSuitPets(self):
        import pet
        import petdata
        petLst = []
        carrygrade = self.GetAnotherCarryGrade()
        for petobj in pet.g_Pets:
            newkey = petobj.m_BirthKey
            carrygrade2 = petdata.GetData(petobj.m_Prop.m_Shape)['carry_grade']
            if (petobj.m_Prop.m_Grade != 0 and newkey & pet.MARK_ISBAOBAO == 0 and petobj.m_Key & 128 != 0 and pet.IsSpecialSummon(newkey) or carrygrade is not None) and abs(carrygrade - carrygrade2) >= 30:
                continue
            
            petLst.append(petobj)
        
        return petLst

    
    def RefreshPetKey(self, pid, shape, desc, key):
        if self.m_SelectID != pid:
            return None
        
        if hasattr(self, 'm_PetAni') and self.m_PetAni:
            self.m_PetAni.ReleaseAll()
        
        for petbox in self.m_PetList.m_Items:
            if petbox.m_ID == pid:
                petbox.m_Key = key
                break
                continue
        
        import wrapinterface
        self.m_PetAni = wrapinterface(self.GetObject('petani'), shape, desc, key)
        self.m_PetAni.SetPos(5, 4)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.SetShow(False)
            g_PetCombineDlg.ReleaseAll(False)
        elif msgid <= msgid:
            pass
        elif msgid <= 120:
            if msgid - 101 >= len(self.m_PetList.m_Items):
                return None
            
            petbox = self.m_PetList.m_Items[msgid - 101]
            self.m_SelectID = petbox.m_ID
            self.RefreshPetKey(self.m_SelectID, petbox.m_Shape, petbox.m_Desc, petbox.m_Key)
            petobj = pet.GetPet(petbox.m_ID)
            if not petobj:
                return None
            
            if petobj.m_Key & 128 != 0:
                usermacro.PROMPT_MSG('\xa5[\xc2\xea\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xa6\xb9\xbe\xde\xa7@')
                return None
            
            if petobj.m_ID in self.m_UsedID:
                usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xbf\xef\xbe\xdc\xa6P\xa4@\xb0\xa6\xa5l\xb3\xea\xc3~')
                return None
            
            import netpet
            if not petobj.m_UpdateProp:
                netpet.C2SSummonView(petobj.m_ID)
            
            g_PetCombineDlg.ShowPetInfo(petobj)
            t = C_sys.GetTime()
            if hasattr(self, 'm_LeftUpTime') and hasattr(self, 'm_PrePid') and self.m_PrePid == petobj.m_ID:
                if t - self.m_LeftUpTime < 5000:
                    self.OnMessage(3)
                
            
            self.m_LeftUpTime = t
            self.m_PrePid = petobj.m_ID
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= 120:
            petlist = self.GetObject('petlist')
            idx = msgid - interface.RIGHT_BUTTON_MESSAGE - 101
            if idx >= len(petlist.m_Items):
                return None
            
            petbox = petlist.m_Items[idx]
            pet.ShowMyPet(petbox.m_ID)
        elif msgid == 3:
            petobj = pet.GetPet(self.m_SelectID)
            if petobj.m_Key & 128 != 0:
                usermacro.PROMPT_MSG('\xa5[\xc2\xea\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xa6\xb9\xbe\xde\xa7@')
                return None
            
            if petobj.m_ID in self.m_UsedID:
                usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xbf\xef\xbe\xdc\xa6P\xa4@\xb0\xa6\xa5l\xb3\xea\xc3~')
                return None
            
            import netpet
            netpet.C2SSummonCanCombin(petobj.m_ID)
        



class CPetCombineDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/petcombine.dlg')
        interface.Center(self)
        self.m_DlgHelpID = 5510
        self.m_opArea = 1
        self.m_SkillIcons = [
            [],
            []]
        self.m_PetObj1 = None
        self.m_PetObj2 = None
        self.ShowCombineRule()

    
    def ShowLinkDlg(self):
        import dlgnpc
        txt = '\xa1i\xa5l\xb3\xea\xc3~\xa6X\xa6\xa8\xa1j#r' + '\xc7\xe9\xa9\xf1\xa4J\xa8\xe2\xb0\xa6\xb3\xa3\xacO0\xaf\xc5\xc4_\xc4_\xaa\xba\xa5l\xb3\xea\xc3~\xa1A\xb6i\xa6\xe6\xb7\xd2\xa7\xaf\xa6X\xa6\xa8\xa1A\xb1N\xb7|\xb2\xa3\xa5\xcd\xa4@\xad\xd3\xb7s\xa5\xcd\xa5l\xb3\xea\xc3~\xa1A\xa5~\xa7\xce\xb1N\xacO\xb3o\xa8\xe2\xb0\xa6\xa5l\xb3\xea\xc3~\xa4\xa4\xc0H\xbe\xf7\xa4@\xba\xd8\xa1C#r' + '\xc7\xea\xb7\xd2\xa7\xaf\xa6X\xa6\xa8\xaa\xba\xa5l\xb3\xea\xc3~\xaa\xba\xb8\xea\xbd\xe8\xa9M\xa7\xde\xaf\xe0\xb1N\xb2\xa3\xa5\xcd\xa4@\xa9w\xaa\xba\xc0H\xbe\xf7\xc5\xdc\xa4\xc6\xa1A\xb8\xfb\xa4p\xb7\xa7\xb2v\xb7|\xa5X\xb2{\xb8\xea\xbd\xe8\xb6W\xb9L\xa5l\xb3\xea\xc3~\xa9T\xa6\xb3\xaa\xba\xb8\xea\xbd\xe8\xa4W\xad\xad\xa1A\xb8\xfb\xa4p\xb7\xa7\xb2v\xa5X\xb2{\xa7\xde\xaf\xe0\xbc\xc6\xb6q\xb6W\xb9L\xa5l\xb3\xea\xc3~\xa9T\xa6\xb3\xaa\xba\xa7\xde\xaf\xe0\xbc\xc6\xb6q\xa4W\xad\xad\xa1C#r' + '\xc7\xeb\xb0\xd1\xbe\xd4\xb5\xa5\xaf\xc5\xa1\xd855\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xb5L\xaak\xbbP\xa9M\xa5\xa6\xb0\xd1\xbe\xd4\xb5\xa5\xaf\xc5\xac\xdb\xaet30\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xb6i\xa6\xe6\xa6X\xa6\xa8#n#r' + '\xc7\xec\xb0\xd1\xbe\xd4\xb5\xa5\xaf\xc5\xa1\xd6\xa4H\xaa\xab\xb5\xa5\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xa1A\xa5u\xaf\xe0\xbbP\xa5t\xa4@\xad\xd3\xac\xdb\xa6P\xb0\xd1\xbe\xd4\xb5\xa5\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xb6i\xa6\xe6\xa6X\xa6\xa8#r' + '\xc7\xed\xb0\xd1\xbbP\xa6X\xa6\xa8\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa4\xa6\xb3\xb1M\xa6\xb3\xc4\xdd\xa9\xca\xaa\xba\xa1A\xabh\xa6X\xa6\xa8\xab\xe1\xaa\xba\xa5l\xb3\xea\xc3~\xa5\xb2\xa9w\xac\xb0\xb1M\xa6\xb3\xaa\xba\xa5l\xb3\xea\xc3~\xa1A\xa8\xc3\xbcW\xa5[30\xc2I\xa9\xd2\xa6\xb3\xb8\xea\xbd\xe8\xa1]\xa6b\xadp\xba\xe2\xa6X\xa6\xa8\xb8\xea\xbd\xe8\xae\xc9\xa1A\xa4\xa3\xb7|\xadp\xba\xe2\xb1M\xa6\xb3\xa1B\xa9\xc7\xaa\xab\xb9\xcf\xc5\xb3\xb5\xa5\xb8\xea\xbd\xe8\xa5[\xa6\xa8\xa1A\xb3o\xa8\xc7\xa5[\xa6\xa8\xb7|\xba\xe2\xa4J\xa6X\xa6\xa8\xab\xe1\xaa\xba\xa5l\xb3\xea\xc3~\xa8\xad\xa4W\xa1^'
        dlgnpc.ShowClientDlg(txt, '', None)

    
    def ShowCombineRule(self):
        obj = self.GetObject('txt_Link')
        (x, y) = obj.GetPos()
        (w, _) = obj.GetSize()
        text = '#u%s\xacd\xac\xdd\xa6X\xc3d\xb3W\xabh#n' % style.GetStr(self.GetDlgPath(), 'data_text_color')
        self.m_LinkText = interface.CClickRichText(self, x, y, w, text, 65280, 65280, interface.FontLT14_3, 50)

    
    def ShowPetInfo(self, petobj, extra_zz = 0):
        if self.m_opArea == 1:
            self.m_PetObj1 = petobj
        else:
            self.m_PetObj2 = petobj
        self.m_SkillIcons[self.m_opArea - 1] = []
        txtClass = None if interface.IsStyle1() else interface.CTextObject
        import combmacro
        namectrl = ('name1', 'name2')[self.m_opArea - 1]
        txtobj = combmacro.CTEXT(txtClass, namectrl, self, petobj.m_Prop.m_Name, interface.FontLT14_3, 16777215, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
        setattr(self, 'm_Name' + str(self.m_opArea), txtobj)
        
        def showzz(shadow, name, cname):
            import petzz
            ob = shadow.Get()
            if not ob:
                return None
            
            pobj = (ob.m_PetObj1, ob.m_PetObj2)[self.m_opArea - 1]
            if pobj:
                info = pobj.m_Name2PropItem[name].GetInfo()
                zzarr = petzz.GetData(pobj.m_Prop.m_Shape)
                (_mtype, _tz, _fz, _gz, _dz, _sz, _lift) = zzarr
                color = interface.COLOR_9
                dn = {
                    'Ability_Attack': _gz,
                    'Ability_Defense': _dz,
                    'Ability_Con': _tz,
                    'Ability_Magic': _fz,
                    'Ability_Speed': _sz }
                if _mtype != -1 and name in dn:
                    
                    try:
                        info = int(info)
                    except:
                        info = 0

                    if _mtype == 1:
                        _rate = 100 * info / dn[name]
                    else:
                        _rate = (info - _gz) / 50
                    if (_rate in range(100, 105) or _mtype == 0) and _rate == 0:
                        color = pet.GetZZColor(1)
                        txtinfo = pet.STRING_ZZ[1]
                    elif (_rate in range(105, 110) or _mtype == 0) and _rate in (1, 2):
                        color = pet.GetZZColor(2)
                        txtinfo = pet.STRING_ZZ[2]
                    elif (_rate in range(110, 115) or _mtype == 0) and _rate in (3, 4):
                        color = pet.GetZZColor(3)
                        txtinfo = pet.STRING_ZZ[3]
                    elif (_rate >= 115 or _mtype == 0) and _rate >= 5:
                        color = pet.GetZZColor(4)
                        txtinfo = pet.STRING_ZZ[4]
                    else:
                        color = pet.GetZZColor(0)
                        txtinfo = pet.STRING_ZZ[0]
                    (x, y) = ob.GetObject(cname).GetPos()
                    tmp = interface.CNotifyBox(ob, 54, 16, alpha = 0, msgid = 200 + len(ob.m_Tipslist))
                    tmp.m_Info = txtinfo
                    tmp.SetPos(x, y)
                    ob.m_Tipslist.append(tmp)
                
                if info != '':
                    if extra_zz == 0:
                        text = str(info)
                    else:
                        
                        try:
                            info = int(info)
                        except:
                            info = 0

                        text = '%s+%s' % (str(info - extra_zz), str(extra_zz))
                    txtobj = combmacro.CTEXT(txtClass, cname, ob, text, interface.FontLT14_3, color)
                    setattr(ob, name + str(self.m_opArea), txtobj)
                else:
                    setattr(ob, name + str(self.m_opArea), None)
                    setattr(ob, name + str(self.m_opArea) + '_tips', None)
            

        self.m_Tipslist = []
        for name, cname1, cname2 in PET_ADV_STATE:
            cname = (cname1, cname2)[self.m_opArea - 1]
            propitem = petobj.m_Name2PropItem[name]
            propitem.RemoveRefreshCallbackWithID('dlgpetcombine%d' % self.m_opArea)
            propitem.AddRefreshCallbackWithID('dlgpetcombine%d' % self.m_opArea, showzz, interface.CShadowObject(self), name, cname)
        
        shape = petobj.GetProp('m_Shape')
        desc = petobj.GetProp('m_Desc')
        key = (petobj.m_BirthKey & 255) << 8 | petobj.m_Key & 255
        self._ShowPetPhoto(shape, desc, key)
        self._ShowPetSkills(petobj)

    
    def _ShowPetPhoto(self, shape, desc, key):
        if self.m_opArea == 1:
            if hasattr(self, 'm_Ani1') and self.m_Ani1:
                self.m_Ani1.Release()
            
        elif hasattr(self, 'm_Ani2') and self.m_Ani2:
            self.m_Ani2.Release()
        
        if self.m_opArea == 1:
            self.m_Ani1 = wrapinterface.CPetAni(self, shape, desc, key)
            ani = self.m_Ani1
        else:
            self.m_Ani2 = wrapinterface.CPetAni(self, shape, desc, key)
            ani = self.m_Ani2
        (x, y) = self.GetObject(('petbox1', 'petbox2')[self.m_opArea - 1]).GetPos()
        ani.SetPos(x + 4, y + 2)

    
    def RefreshSkills(self, petid):
        petobj = pet.GetPet(petid)
        if petobj:
            self._ShowPetSkills(petobj)
        

    
    def _ShowPetSkills(self, petobj):
        obj = self.GetObject(('skillbox1', 'skillbox2')[self.m_opArea - 1])
        (x, y) = obj.GetPos()
        x = x + 3
        y = y + 3
        import dlgpet
        for i, sk in enumerate(petobj.m_Skills[:12]):
            img = obj.GetImage(i / 4, i % 4)
            (ix, iy) = img.GetPos()
            si = dlgpet.CSkillIcon(self, x + ix, y + iy, sk, i == petobj.m_BindSkill)
            si.SetTag(petobj.IsHFSkillIdx(i))
            self.m_SkillIcons[self.m_opArea - 1].append(si)
        

    
    def OnEnter(self, msgid):
        import wrapinterface
        if msgid >= 200:
            if self.m_Tipslist[msgid - 200].m_Info != '':
                self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_Tipslist[msgid - 200].m_Info, interface.FontLT14_3, direct = 0)
            
        elif msgid >= 20:
            idx = msgid - 20
            if hasattr(self, 'm_Stars') and idx in self.m_Stars:
                (img, box, times, maxi) = self.m_Stars[idx]
                if times < maxi:
                    tips = '\xad\xb8\xaa@\xb6i\xa4\xc6%d/%d' % (times, maxi)
                else:
                    tips = '\xa4w\xb9F\xad\xb8\xaa@\xb6i\xa4\xc6\xa4W\xad\xad%d/%d' % (times, maxi)
                self.m_Tips = wrapinterface.CTextTips(None, -1, tips, interface.FontLT14_3)
            
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def GetSelectedPetId(self):
        usedid = []
        if self.m_PetObj1:
            usedid.append(self.m_PetObj1.m_ID)
        
        if self.m_PetObj2:
            usedid.append(self.m_PetObj2.m_ID)
        
        return usedid

    
    def GetAnotherPet(self):
        if self.m_opArea == 1 and self.m_PetObj2:
            return self.m_PetObj2
        elif self.m_opArea == 2 and self.m_PetObj1:
            return self.m_PetObj1
        

    
    def ReleaseAll(self, flag = True):
        if flag:
            self.m_SkillIcons = [
                [],
                []]
            self.m_Name1 = None
            self.m_Name2 = None
            self.m_PetObj1 = None
            self.m_PetObj2 = None
            if hasattr(self, 'm_Ani1') and self.m_Ani1 is not None:
                self.m_Ani1.Release()
            
            if hasattr(self, 'm_Ani2') and self.m_Ani2 is not None:
                self.m_Ani2.Release()
            
            for name, _, _ in PET_ADV_STATE:
                setattr(self, name + '1', None)
                setattr(self, name + '2', None)
            
            return None
        
        if self.m_opArea == 2:
            self.m_SkillIcons[1] = []
            self.m_Name2 = None
            self.m_PetObj2 = None
            if hasattr(self, 'm_Ani2') and self.m_Ani2 is not None:
                self.m_Ani2.Release()
            
            for name, _, _ in PET_ADV_STATE:
                setattr(self, name + '2', None)
            
        else:
            self.m_SkillIcons[0] = []
            self.m_Name1 = None
            self.m_PetObj1 = None
            if hasattr(self, 'm_Ani1') and self.m_Ani1 is not None:
                self.m_Ani1.Release()
            
            for name, _, _ in PET_ADV_STATE:
                setattr(self, name + '1', None)
            

    
    def OnMessage(self, msgid):
        global g_PetChoose
        if msgid == 4:
            CloseWnd()
        elif msgid in (1, 2):
            self.m_opArea = msgid
            g_PetChoose = CPetChoose(self.GetSelectedPetId())
        elif msgid == 3:
            if not (self.m_PetObj1) or not (self.m_PetObj2):
                usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xbb\xdd\xadn\xa6X\xa6\xa8\xaa\xba\xa5l\xb3\xea\xc3~')
                return None
            
            import netpet
            netpet.C2SPetRefine(0, 1, self.m_PetObj1.m_ID, self.m_PetObj2.m_ID)
            self.ReleaseAll()
        elif msgid == 50:
            self.ShowLinkDlg()
        



def CloseWnd():
    if g_PetCombineDlg:
        g_PetCombineDlg.ReleaseAll()
        g_PetCombineDlg.SetShow(False)
    


def ShowSwitch():
    global g_PetCombineDlg
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpetcombinenew
        dlgpetcombinenew.ShowSwitch()
        return None
    
    g_PetCombineDlg = CPetCombineDlg()
