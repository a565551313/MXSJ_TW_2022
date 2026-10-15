# pycdc 交叉复核产物 · script.fls entry 4048
# co_filename(原始)='script/dialog/dlgpet.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4048.pyc (Python 2.5)

import combdialog
import combmacro
import cursor
import interface
import misc
import skilliconpath
import style
import ui
import usermacro
import walker
import wrapinterface
g_PetDialog = None
g_MergePetsInfo = { }
g_RestTimeInfo = { }
g_AutoObject = None
g_AutoTimer = None
g_SkillTips = None
g_Mutex = False
g_LianHuaTime = { }
g_RenamePetInfo = {
    'isSend': True,
    'petID': None,
    'petName': None }
g_PetPRops1 = ()

def ModuleReset():
    global g_PetDialog, g_MergePetsInfo, g_RestTimeInfo, g_AutoObject, g_AutoTimer, g_SkillTips, g_Mutex, g_LianHuaTime, g_PetPRops1, g_RenamePetInfo
    g_PetDialog = None
    g_MergePetsInfo = { }
    g_RestTimeInfo = { }
    g_AutoObject = None
    g_AutoTimer = None
    g_SkillTips = None
    g_Mutex = False
    g_LianHuaTime = { }
    g_PetPRops1 = ()
    g_RenamePetInfo = {
        'isSend': True,
        'petID': None,
        'petName': None }
    SetPetPROPS()
    CAutoAssignDlg.ResetClear()

PET_PROPS = (('m_Grade', 0, 0), ('m_HP', 0, 1), ('m_MP', 0, 2), ('m_FP', 0, 3), ('m_Damage', 0, 4), ('m_Defense', 0, 5), ('m_Magdef', 0, 6), ('m_Speed', 0, 7))

def SetPetPROPS():
    global g_PetPRops1, g_PetPRops1
    if interface.IsNewStyle():
        g_PetPRops1 = (('hfrm_Grade', 'm_Grade', interface.ALIGN_MIDDLE, 0, 0, 16777215), ('hfrm_HP', 'm_HP'), ('hfrm_MP', 'm_MP'), ('hfrm_FP', 'm_FP'), ('hfrm_Damage', 'm_Damage'), ('hfrm_Defense', 'm_Defense'), ('hfrm_Magdef', 'm_Magdef'), ('hfrm_Speed', 'm_Speed'))
    else:
        g_PetPRops1 = (('hfrm_Grade', 'm_Grade'), ('hfrm_HP', 'm_HP'), ('hfrm_MP', 'm_MP'), ('hfrm_FP', 'm_FP'), ('hfrm_Damage', 'm_Damage'), ('hfrm_Defense', 'm_Defense'), ('hfrm_Magdef', 'm_Magdef'), ('hfrm_Speed', 'm_Speed'))

SetPetPROPS()
PET_POINTS = (('m_Con', 0, 0, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE), ('m_Str', 0, 1, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE), ('m_Mag', 0, 2, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE), ('m_Cha', 0, 3, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE), ('m_Dex', 0, 4, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE), ('m_Point', 0, 5, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
PET_APTI = (('Ability_Attack', 'txt_apti', 0), ('Ability_Con', 'txt_apti', 1), ('Ability_Speed', 'txt_apti', 2), ('Ability_Defense', 'txt_apti2', 0), ('Ability_Magic', 'txt_apti2', 1), ('m_AttackType', 'txt_apti2', 2), ('m_Life', 'txt_apti2', 3))
PET_APTI1 = (('Ability_Attack', 'hrfm_Attack', 0), ('Ability_Con', 'hrfm_Con', 1), ('Ability_Speed', 'hrfm_Speed', 2), ('Ability_Defense', 'hrfm_Defense', 0), ('Ability_Magic', 'hrfm_Magic', 1), ('m_AttackType', 'hrfm_AttackType', 2), ('m_Life', 'hrfm_Life', 3))
PET_UPD = ('Update_Flag', 'Update_Max')
PET_MAGRESIST = (('Resist_Xian', 0, 0), ('Resist_Gui', 0, 0), ('Resist_Yao', 0, 0), ('Resist_Zhi', 0, 0), ('Resist_Nian', 0, 0))
PET_PHYRESIST = (('Resist_Lidi', 0, 0), ('Resist_Lingqiao', 0, 0), ('Resist_Qungong', 0, 0), ('Resist_Putong', 0, 0))

def GetRestTime():
    return g_RestTimeInfo


def GetMargePets():
    return g_MergePetsInfo


def getpoint(ox, oy, lx, ly, v):
    import math
    dist = math.sqrt((ly - oy) * (ly - oy) + (lx - ox) * (lx - ox))
    if v < -30:
        v = -30
    
    if v > 100:
        v = 100
    
    offset = dist * (v + 30) / 130
    y = int(oy + ((ly - oy) * offset + (dist - 1)) / dist)
    x = int(ox + ((lx - ox) * offset + (dist - 1)) / dist)
    return (x, y)


def getmagp(ox, oy, lx, ly, v):
    import math
    dist = math.sqrt((ly - oy) * (ly - oy) + (lx - ox) * (lx - ox))
    if v < -30:
        v = -30
    
    offset = (v + 30) / 70
    y = int(oy + (ly - oy) * offset)
    x = int(ox + (lx - ox) * offset)
    return (x, y)


def getphyp(ox, oy, lx, ly, v):
    import math
    dist = math.sqrt((ly - oy) * (ly - oy) + (lx - ox) * (lx - ox))
    if v < -50:
        v = -50
    
    offset = (v + 50) / 80
    y = int(oy + (ly - oy) * offset)
    x = int(ox + (lx - ox) * offset)
    return (x, y)

g_QiangLiSkill = (219, 298)

class CSkillTips(interface.CBoxObject, interface.CBase):
    TIPSWIDTH = 220
    TIPSHEIGHT = 100
    
    def __init__(self, skid, petid, pillSkillPos = None, ishuanhua = False, dTempTalentInfo = None, iState = 0):
        interface.CBoxObject.__init__(self, interface.MainPanel, self.TIPSWIDTH, self.TIPSHEIGHT, 8224, 128)
        self.CreateInfo(skid, petid, pillSkillPos, ishuanhua, dTempTalentInfo, iState)
        self.ResetPos()
        self.Topmost()

    
    def CreateInfo(self, skid, petid, pillSkillPos, ishuanhua, dTempTalentInfo, iState):
        import petskill
        import pet
        import pillskilldata
        import style
        import dlgpetbase
        skd = petskill.GetData(skid)
        sColor = style.GetStr('dlgpet.CSkillTips', 'data_txt_color')
        self.m_Name = interface.CRichTextObject(self, 220, interface.FontLT18_1, sColor + skd['name'] + '(%s)' % [
            '\xb3Q\xb0\xca',
            '\xa5D\xb0\xca'][skd['type'] != 0])
        self.m_Name.SetPos(10, 10)
        desc = skd['desc']
        if skid in (441, 442, 444, 572):
            number = self.CalValue(skid, petid)
            number = '#Y%d%%#n' % number
            desc = desc.replace('$num', number)
        
        pobj = pet.GetPet(petid)
        if pobj and skid in pillskilldata.PILLSKILLIDLST and pillSkillPos:
            pillDct = {
                1: 'm_Pill1Rest',
                2: 'm_Pill2Rest' }
            propName = pillDct.get(pillSkillPos, 'm_Pill1Rest')
            pillRest = pobj.GetProp(propName)
            desc += '#r#Y\xb3\xd1\xbel\xc6F\xae\xf0\xa1G%d' % pillRest
        
        if dTempTalentInfo:
            desc += pet.GetTempTalentDesc(dTempTalentInfo)
        
        desc += dlgpetbase.SKILL_GREYTIPS.get(iState, '')
        self.m_Info = interface.CRichTextObject(self, 190, interface.FontLT14_3, desc)
        self.m_Info.SetPos(10, 28)

    
    def ResetPos(self):
        import ratio
        (w, h) = self.m_Info.GetSize()
        if h + 28 > self.TIPSHEIGHT:
            h = h + 28 + 4
            self.SetSize(self.TIPSWIDTH, h)
        else:
            h = self.TIPSHEIGHT
        (x, y) = cursor.GetPos()
        x = x - self.TIPSWIDTH / 2
        if x < 0:
            x = 0
        elif x + self.TIPSWIDTH >= ratio.WINDOW_WIDTH:
            x = 800 - self.TIPSWIDTH
        
        if y + h + 50 > ratio.WINDOW_HEIGHT:
            y = y - 50 - h
        else:
            y = y + 50
        self.SetPos(x, y)

    
    def CalValue(self, skillId, petId):
        import pet
        petObj = pet.GetPet(petId)
        if not petObj:
            import dlggetinfo
            info = dlggetinfo.g_SummonInfos[petId]
            power = int(info['str'])
            magic = int(info['mag'])
            grade = int(info['grade'])
        else:
            power = petObj.GetProp('m_Str')
            magic = petObj.GetProp('m_Mag')
            grade = petObj.GetProp('m_Grade')
        if grade == 0:
            iRatio = 0
            return iRatio
        
        if skillId == 572:
            iRatio = int(max((power + magic) * 1 / grade - 3, 0) ** 1.5) * 100 / 15
            iRatio = min(iRatio, 60)
        elif skillId == 442:
            iRatio = max(power * 100 / (grade * 15) - 5, 0)
            iRatio = min(iRatio, 100)
        elif skillId == 441:
            iRatio = max(magic * 100 / (grade * 12) - 5, 0)
            iRatio = min(iRatio, 100)
        elif skillId == 444:
            iRatio = max((magic + power * 4 / 5) * 100 / (grade * 20) - 8, 0)
            iRatio = min(iRatio, 100)
        else:
            iRatio = None
        return iRatio



class CSkillIcon(interface.CStretchImagesObject, interface.CBase):
    
    def __init__(self, parent, x, y, skid, isbind = False, iState = 0):
        import petskill
        skd = petskill.GetData(skid)
        (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(petskill.GetShape(skid))
        interface.CStretchImagesObject.__init__(self, parent, sPath, sPack)
        if isbind:
            self.m_txtBind = interface.CTextObject(self, '\xb8j', interface.FontLT12E_1, self.GetColor())
            self.m_txtBind.SetPos(5, 5)
        
        self.SetPos(x, y)
        self.m_SkillID = skid
        self.m_IsHuanHua = False
        self.m_PetID = None
        self.m_dTempTalentInfo = None
        self.m_iState = iState
        self.Enable(True)

    
    def SetTempTalentInfo(self, dTempTalentInfo):
        self.m_dTempTalentInfo = dTempTalentInfo

    
    def ShowTalentFlag(self, bShow):
        if bShow:
            self.m_oFlagIcon = interface.CBitmapObject(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xcc\xec\xb8\xb3.png', interface.UIPath)
            self.m_oFlagIcon.SetZ(1)
        else:
            self.m_oFlagIcon = None

    
    def SetTag(self, bShow):
        if bShow:
            self.m_txtHf = interface.CTextObject(self, '\xb2\xc5', interface.FontLT12E_1, self.GetColor())
            self.m_txtHf.SetPos(5, 5)
        else:
            self.m_txtHf = None

    
    def GetColor(self):
        if interface.IsNewStyle():
            return [
                1221678,
                3158016]
        
        return [
            3211056,
            3158016]

    
    def SetOwnerID(self, petid):
        self.m_PetID = petid

    
    def SetIsHuanHua(self, ishuanhua = False):
        self.m_IsHuanHua = ishuanhua

    
    def SetPillPos(self, pos):
        if pos < pos:
            pass
        elif pos <= 2:
            self.m_PillPos = pos
        else:
            self.m_PillPos = None

    
    def Enter(self):
        global g_SkillTips, g_SkillTips
        if self.m_IsHuanHua:
            g_SkillTips = CSkillTips(self.m_SkillID, self.m_PetID, getattr(self, 'm_PillPos', None), True, dTempTalentInfo = self.m_dTempTalentInfo)
        else:
            g_SkillTips = CSkillTips(self.m_SkillID, self.m_PetID, getattr(self, 'm_PillPos', None), dTempTalentInfo = self.m_dTempTalentInfo, iState = self.m_iState)

    
    def Leave(self):
        global g_SkillTips
        if g_SkillTips:
            g_SkillTips = None
        

    
    def MouseWheelDown(self, p):
        par = self.GetParent().GetParent()
        if par and isinstance(par, combdialog.CList):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent().GetParent()
        if par and isinstance(par, combdialog.CList):
            par.MouseWheelUp(p)
        



class CChoiceBtn(interface.CButton):
    
    def __init__(self, parent, path, x, y, msgid = 0):
        interface.CButton.__init__(self, parent, path, x, y, msgid)
        self.m_Selected = False

    
    def Enter(self):
        interface.CButton.Enter(self)
        if self.FrameAmount() == 4:
            if self.m_Selected:
                self.SetFrame(3)
            else:
                self.SetFrame(1)
        

    
    def Leave(self):
        interface.CButton.Leave(self)
        if self.FrameAmount() == 4:
            if self.m_Selected:
                self.SetFrame(2)
            else:
                self.SetFrame(0)
        

    
    def LeftDown(self):
        interface.CButton.LeftDown(self)

    
    def LeftUp(self):
        self.GetParent().BtnSelect()

    
    def IsSelected(self):
        return self.m_Selected

    
    def SetSelect(self, bSelect):
        self.m_Selected = bSelect
        if self.m_Selected:
            self.SetFrame(2)
        else:
            self.SetFrame(0)



class CNumberEdit(interface.CEdit):
    
    def __init__(self, *args):
        interface.CEdit.__init__(self, *args)
        self.m_oUpdateObj = None

    
    def SetMaxNum(self, maxNum):
        self.m_MaxNum = maxNum

    
    def CheckOutMax(self):
        if hasattr(self, 'm_MaxNum') and self.m_MaxNum:
            
            try:
                number = int(self.GetText())
            except:
                number = 0

            if number > self.m_MaxNum:
                return True
            
        
        return False

    
    def SetColor(self, color):
        self.m_Color = color
        txt = self.GetText()
        if txt != '':
            self.SetText(txt)
        

    
    def SetUpdateObj(self, oObj):
        self.m_oUpdateObj = misc.WeakRef(oObj)

    
    def SetText(self, txt):
        self.Clear()
        for char in txt:
            interface.CEdit.AddChar(self, char)
        
        iTextLen = 0
        for ch in self.m_Data:
            iTextLen += ch[0].GetSize()[0]
        
        import combmacro
        self.SetSize(iTextLen, combmacro.GetFontSize(self.m_Font))
        if self.m_oUpdateObj and self.m_oUpdateObj.Get():
            interface.AlignObjects(self, self.m_oUpdateObj.Get(), interface.ALIGN_CENTER_MIDDLE)
        

    
    def DoCallback(self):
        parent = self.GetParent()
        if hasattr(parent, 'OnEditChange'):
            parent.OnEditChange(self)
        

    
    def AddChar(self, char):
        if char.isdigit():
            if char == char:
                pass
            elif char == '0':
                return None
            
            interface.CEdit.AddChar(self, char)
        
        if self.CheckOutMax():
            self.SetText(str(self.m_MaxNum))
        
        self.DoCallback()

    
    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        self.DoCallback()

    
    def LeftDown(self):
        interface.CEdit.LeftDown(self)
        self.SetSelect(0, 999)



class CAutoAssignDlg(combdialog.CAttachCombDialog):
    IDX2INFO = {
        1: ('m_TizhiEdit', 'edit_Tizhi', 10),
        2: ('m_LiliangEdit', 'edit_Liliang', 10),
        3: ('m_MagicEdit', 'edit_Magic', 10),
        4: ('m_MeiliEdit', 'edit_Meili', 10),
        5: ('m_MinjieEdit', 'edit_Minjie', 10) }
    s_NeedAutoAddPid = []
    
    def ResetClear(cls):
        cls.s_NeedAutoAddPid = []

    ResetClear = classmethod(ResetClear)
    
    def __init__(self, parent):
        combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/summon/autoassign.dlg')
        self.m_AttrIdxList = self.IDX2INFO.keys()
        self.m_AttrIdxList.sort()
        self.CreateEdits()
        self.CreateCheckBtn()
        self.m_LevelSelect = False
        self.m_ModifyEditLst = []
        (width, height) = parent.GetSize()
        (w, h) = self.GetSize()
        self.SetPos(width - 8, height - h)
        self.SetTipsShow(False)
        self.SetTipsZ()

    
    def RightUp(self):
        self.OnClose()

    
    def SetData(self, pid, data):
        self.m_Pid = pid
        self.m_Data = data
        self.m_ModifyEditLst = []
        self.Refresh()

    
    def Refresh(self):
        if self.m_Data is None:
            return None
        
        attrList = self.m_Data['attrList']
        if interface.IsNewStyle():
            color = interface.COLOR_5
        else:
            color = interface.COLOR_9
        for idx in self.m_AttrIdxList:
            attrName = self.IDX2INFO[idx][0]
            obj = getattr(self, attrName)
            obj.SetText(str(attrList[idx - 1]))
            obj.SetColor(color)
        
        bSelect = self.m_Data['bSelect']
        limitLevel = self.m_Data['limitLevel']
        self.m_CheckBtn.SetSelect(bSelect)
        self.m_LevelEdit.SetText(str(limitLevel))
        self.m_LevelEdit.SetColor(interface.COLOR_5)

    
    def CreateCheckBtn(self):
        (x, y) = self.GetObject('btn_Auto').GetPos()
        self.m_CheckBtn = CChoiceBtn(self, style.GetPath('combdialog\\\xb0\xb4\xc5\xa5\\\xd1\xa1\xd4\xf1.igs'), x, y)

    
    def CreateEdits(self):
        import combmacro
        for attrName, objName, maxNum in self.IDX2INFO.values():
            obj = combmacro.CEDIT(CNumberEdit, objName, self, 16777215, interface.FontLT14_3)
            obj.SetMaxNum(maxNum)
            obj.SetUpdateObj(self.GetObject(objName))
            setattr(self, attrName, obj)
        
        self.m_LevelEdit = combmacro.CEDIT(CNumberEdit, 'edit_Level', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_LevelEdit.SetMaxNum(163)
        self.m_LevelEdit.SetUpdateObj(self.GetObject('edit_Level'))
        self.m_LevelEdit.SetLeftDownCB(self.OnEditLeftDown)

    
    def SetTipsShow(self, bShow):
        self.GetObject('img_tips').SetShow(bShow)
        self.GetObject('text_tips').SetShow(bShow)
        self.GetObject('hloc_tips').SetShow(bShow)

    
    def SetTipsZ(self):
        iZ = 1
        self.GetObject('img_tips').SetZ(iZ)
        self.GetObject('text_tips').SetZ(iZ)
        self.GetObject('hloc_tips').SetZ(iZ)

    
    def OnEditLeftDown(self, oEdit):
        if self.m_Data['iSetAuto'] <= 0:
            self.SetTipsShow(True)
        

    
    def GetResult(self):
        total = 0
        for attrName, _, _ in self.IDX2INFO.values():
            obj = getattr(self, attrName)
            number = obj.GetNumber()
            total += number
        
        return total

    
    def OnEditChange(self, editObj):
        self.RecordModify(editObj)
        total = self.GetResult()
        if total > 10:
            editNum = editObj.GetNumber()
            num = max(0, 10 - total - editNum)
            editObj.SetText(str(num))
        else:
            for obj in self.m_ModifyEditLst:
                obj = obj.Get()
                obj.SetColor(16317440)
            

    
    def RecordModify(self, editObj):
        obj = interface.CShadowObject(editObj)
        if self.m_ModifyEditLst.count(obj) == 0:
            self.m_ModifyEditLst.append(obj)
        

    
    def CheckValid(self, point):
        import usermacro
        if point not in (5, 10):
            usermacro.PROMPT_MSG('*\xc4!\xf43#[\xd0%_X\xf9\xa9M\xbb\xdd\xadn\xac\xb05\xa9\xce10')
            return False
        
        return True

    
    def BtnSelect(self):
        bSelect = not self.m_CheckBtn.IsSelected()
        total = self.GetResult()
        self.m_CheckBtn.SetSelect(bSelect)

    
    def OnSave(self):
        import netpet
        import mainmenu
        attrList = []
        for idx in self.m_AttrIdxList:
            attrName = self.IDX2INFO[idx][0]
            obj = getattr(self, attrName)
            attrList.append(obj.GetNumber())
        
        bSelect = None if self.m_CheckBtn.IsSelected() else 0
        level = self.m_LevelEdit.GetNumber()
        netpet.C2SSetAutoPoint(self.m_Pid, attrList, bSelect, level)
        if mainmenu.IsWar():
            CAutoAssignDlg.AddNeedAutoAddPid(self.m_Pid)
        

    
    def AddNeedAutoAddPid(cls, pid):
        cls.s_NeedAutoAddPid.append(pid)

    AddNeedAutoAddPid = classmethod(AddNeedAutoAddPid)
    
    def AutoAdd(cls):
        import netpet
        for pid in cls.s_NeedAutoAddPid:
            netpet.C2SAutoAddPoint(pid)
        
        cls.s_NeedAutoAddPid = []

    AutoAdd = classmethod(AutoAdd)
    
    def OnCancel(self):
        import netpet
        dct = { }
        dct['attrList'] = [
            0,
            0,
            0,
            0,
            0]
        dct['bSelect'] = 0
        dct['limitLevel'] = 0
        self.SetData(self.m_Pid, dct)
        netpet.C2SCancelAuto(self.m_Pid)

    
    def OnAdd(self, idx):
        obj = self.GetAttrObj(idx)
        value = obj.GetNumber()
        value = min(value + 1, 10)
        obj.SetText(str(value))
        self.OnEditChange(obj)

    
    def OnSub(self, idx):
        obj = self.GetAttrObj(idx)
        value = obj.GetNumber()
        value = max(value - 1, 0)
        obj.SetText(str(value))
        self.OnEditChange(obj)

    
    def SetAttrValue(self, idx, value):
        obj = self.GetAttrObj(idx)
        obj.SetText(str(value))
        self.OnEditChange(obj)

    
    def GetAttrObj(self, idx):
        (propname, _, _) = self.IDX2INFO[idx + 1]
        return getattr(self, propname)

    
    def OnClose(self):
        self.GetParent().OnAutoAssignClose()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.OnClose()
        elif msgid == 2:
            pass
        elif msgid == 4:
            total = self.GetResult()
            if self.CheckValid(total):
                self.OnSave()
            
        elif msgid == 20:
            self.OnCancel()
        elif msgid == 22:
            self.SetTipsShow(False)
        elif msgid <= msgid:
            pass
        elif msgid < 10:
            self.OnSub(msgid - 5)
        elif msgid <= msgid:
            pass
        elif msgid < 15:
            self.OnAdd(msgid - 10)
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid - interface.RIGHT_BUTTON_MESSAGE < 10:
            self.SetAttrValue(msgid - interface.RIGHT_BUTTON_MESSAGE - 5, 0)
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid - interface.RIGHT_BUTTON_MESSAGE < 15:
            self.SetAttrValue(msgid - interface.RIGHT_BUTTON_MESSAGE - 10, 10)
        



class CPetcDialog(combdialog.CAttachCombDialog):
    ATTR_TIPS = [
        ('tips_aptiattr', '\xbcv\xc5T\xa5l\xb3\xea\xc3~\xaa\xba\xaa\xab\xb2z\xa7\xf0\xc0\xbb\xa4O', '\xa7\xf0\xc0\xbb\xb8\xea\xbd\xe8', '\xa7\xf0\xc0\xbb\xb8\xea\xbd\xe8\xb3\xcc\xa4j\xad\xc8'),
        ('tips_apticon', '\xbcv\xc5T\xa5l\xb3\xea\xc3~\xaa\xba\xae\xf0\xa6\xe5\xa4W\xad\xad', '\xc5\xe9\xa4O\xb8\xea\xbd\xe8', '\xc5\xe9\xa4O\xb8\xea\xbd\xe8\xb3\xcc\xa4j\xad\xc8'),
        ('tips_aptispe', '\xbcv\xc5T\xa5l\xb3\xea\xc3~\xaa\xba\xb3t\xab\xd7', '\xb3t\xab\xd7\xb8\xea\xbd\xe8', '\xb3t\xab\xd7\xb8\xea\xbd\xe8\xb3\xcc\xa4j\xad\xc8'),
        ('tips_aptidef', '\xbcv\xc5T\xa5l\xb3\xea\xc3~\xaa\xba\xaa\xab\xb2z\xa8\xbe\xbfm\xa4O', '\xa8\xbe\xbfm\xb8\xea\xbd\xe8', '\xa8\xbe\xbfm\xb8\xea\xbd\xe8\xb3\xcc\xa4j\xad\xc8'),
        ('tips_aptimag', '\xbcv\xc5T\xa5l\xb3\xea\xc3~\xaa\xba\xc6F\xa4O', '\xaak\xa4O\xb8\xea\xbd\xe8', '\xaak\xa4O\xb8\xea\xbd\xe8\xb3\xcc\xa4j\xad\xc8'),
        ('img_Tips', '\xb9\xd8\xa9R\xa1\xd550\xae\xc9\xa1A\xa5l\xb3\xea\xc3~\xb1N\xb5L\xaak\xb0\xd1\xbe\xd4#r\xa8C\xb0\xd1\xa5[\xa4@\xb3\xf5\xbe\xd4\xb0\xab\xb1\xbc1\xc2I\xb9\xd8\xa9R#r\xa8C\xa6\xba\xa4`\xa4@\xa6\xb8\xb1\xbc50\xc2I\xb9\xd8\xa9R#r\xa8\xcf\xa5\xce\xc0u\xbd\xe8\xa9_\xad\xbb\xaaG\xa5i\xa5H\xbcW\xa5[\xb9\xd8\xa9R', None, None)]
    
    def __init__(self, parent):
        self.m_PID = None
        combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/summon/attr.dlg')
        (w, h) = parent.GetSize()
        (sw, sh) = self.GetSize()
        offsetx = style.GetInt(self.GetDlgPath(), 'data_offset_x')
        self.SetPos(w - offsetx, h - sh)
        (x, _) = self.GetObject('loc_nian').GetPos()
        (_, y) = self.GetObject('loc_xian').GetPos()
        (x1, _) = self.GetObject('loc_gui').GetPos()
        (_, y1) = self.GetObject('loc_yao').GetPos()
        self.m_MagBox = interface.CNotifyBox(self, x1 - x, y1 - y, alpha = 0, msgid = 1)
        self.m_MagBox.SetPos(x, y)
        (x, y) = self.GetObject('box_phy').GetPos()
        (w, h) = self.GetObject('box_phy').GetSize()
        self.m_PhyBox = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 2)
        self.m_PhyBox.SetPos(x, y)
        self.InitListData()

    
    def InitPetaptitude(self):
        import petaptitudedata
        import pet
        import petdata
        self.m_TipsInfo = []
        oPetObj = pet.GetPet(self.m_PID)
        iShape = oPetObj.m_Prop.m_Shape
        dAptitudeDict = petaptitudedata.GetData(iShape)
        for name, txt, aptitude, maxaptitude in enumerate(self.ATTR_TIPS):
            (x, y, w, h) = self.GetLocData(name)
            tmp = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 90 + i)
            tmp.SetPos(x, y)
            tmp.Topmost()
            tmp.m_Info = txt
            self.m_TipsInfo.append(tmp)
        

    
    def InitListData(self):
        self.m_List = self.GetObject('listbox')
        if self.m_List:
            self.m_List.SetZ(self.GetObject('box_skills').GetZ() - 1)
            for tt in self.m_List.m_Lines:
                tt.SetShow(False)
            
        
        self.m_Data = []
        box_skills = self.GetObject('box_skills')
        for i in range(4):
            (x, y) = box_skills.m_Imagess[i].GetPos()
            self.m_Data.append((x, y))
        

    
    def Topmost(self):
        if hasattr(self, 'm_Frames'):
            combdialog.CCombDialog.Topmost(self)
        

    
    def GetTipsInfo(self, info, _mtype, dn, _gz, name, pobj):
        import pet
        import petdata
        specialtxtinfo = None
        if petdata.IsShenShou(pobj.m_Prop.m_Shape) or petdata.IsXianShou(pobj.m_Prop.m_Shape):
            tempInfo = info
            if pobj.m_Key & 64 != 0 and pobj.m_Key & 8 != 0:
                tempInfo -= 30
            
            desc = pobj.m_Prop.m_Desc
            for key in ('weapon', 'weapon2', 'weapon3'):
                if desc.get(key) and desc.get(key)[1]:
                    tempInfo -= 20
                    continue
            
            if pobj.m_Prop.Update_Flag % 16 != 0:
                tempInfo -= 20
            
            limit = 300
            if name in ('Ability_Magic', 'Ability_Attack'):
                limit += 50
            
            if tempInfo - dn[name] not in (limit, limit + 5):
                specialtxtinfo = '\xb8\xd3\xb8\xea\xbd\xe8\xa5i\xa5H\xa6b\xa9\xfa\xa4\xeb\xab\xb0(186,180)\xaf\xab\xc3~\xa4p\xad\xb8\xbd\xde\xb3B\xb4\xa3\xa4\xc9'
            
        
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
        if specialtxtinfo:
            return (color, specialtxtinfo)
        else:
            return (color, txtinfo)

    
    def Showzz(self, shaw, name, cname, cid):
        import pet
        import petzz
        ob = shaw.Get()
        if not ob:
            return None
        
        pobj = pet.GetPet(ob.m_PID)
        ctrl = ob.GetObject(cname)
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

                if info > 0:
                    (color, txtinfo) = self.GetTipsInfo(info, _mtype, dn, _gz, name, pobj)
                    (x1, y1) = ctrl.GetPos()
                    if isinstance(ctrl, combdialog.CImagesFrame):
                        (x, y) = ctrl.GetImage(0, cid).GetPos()
                    else:
                        (x, y) = (0, 0)
                    tmp = interface.CNotifyBox(ob, 54, 16, alpha = 0, msgid = 200 + len(ob.m_Tipslist))
                    tmp.m_Info = txtinfo
                    tmp.SetPos(x + x1, y + y1)
                    ob.m_Tipslist.append(tmp)
                
            
            if info:
                color = self.AdjustColor(name, info, color)
                txtclass = None if interface.IsStyle1() else interface.CTextObject
                if isinstance(ctrl, combdialog.CImagesFrame):
                    txtobj = combmacro.CreateIFTextWithObject(ctrl, txtclass, 0, cid, str(info), interface.FontLT14_3, color)
                else:
                    txtobj = combmacro.CreateTextWithObject(ctrl, txtclass, str(info), interface.FontLT14_3, color)
            else:
                txtobj = None
            setattr(ctrl, name, txtobj)
        

    
    def AdjustColor(self, name, info, initColor):
        color = initColor
        if name == 'm_Life':
            bShow = not ('\xa5\xc3\xa5\xcd' == info)
            self.GetObject('img_Tips').SetShow(bShow)
            self.m_TipsInfo[5].SetShow(bShow)
            if info != '\xa5\xc3\xa5\xcd' and int(info) < 50:
                color = 16711680
            
        
        if interface.IsNewStyle() and name in ('m_AttackType', 'm_Life'):
            color = interface.COLOR_1
        
        return color

    
    def CreateDlgItem(self, pobj):
        self.m_PID = pobj.m_ID
        self.InitPetaptitude()
        self.m_Tipslist = []
        for name, cname, cid in PET_APTI1:
            propitem = pobj.m_Name2PropItem[name]
            propitem.AddRefreshCallbackWithID('PetDlg', self.Showzz, interface.CShadowObject(self), name, cname, cid)
        
        
        def showtips(shadow):
            dlg = shadow.Get()
            if not dlg:
                return None
            
            dlg.m_Tipslist = []
            for name, cname, cid in PET_APTI1:
                dlg.Showzz(interface.CShadowObject(dlg), name, cname, cid)
            

        
        def showupdate(shadow):
            showtips(shadow)
            dlg = shadow.Get()
            if dlg is None:
                return None
            
            import pet
            pobj = pet.GetPet(dlg.m_PID)
            if not pobj:
                return None
            
            flag = pobj.m_Name2PropItem['Update_Flag'].GetInfo()
            maxi = pobj.m_Name2PropItem['Update_Max'].GetInfo()
            flag = int(flag)
            maxi = int(maxi)
            if flag % 16 == 0:
                dlg.ClearStar(-1)
            else:
                for i in range(1, 6):
                    dlg.ShowStar(i, (flag >> i * 4) % 16, (maxi >> i * 4) % 16)
                

        for propname in PET_UPD:
            propitem = pobj.m_Name2PropItem[propname]
            propitem.AddRefreshCallbackWithID('PetDlg', showupdate, interface.CShadowObject(self))
        
        for name, x, y in PET_MAGRESIST:
            propitem = pobj.m_Name2PropItem[name]
            propitem.AddRefreshCallbackWithID('PetDlg', self.RefreshMagResist)
        
        for name, x, y in PET_PHYRESIST:
            propitem = pobj.m_Name2PropItem[name]
            propitem.AddRefreshCallbackWithID('PetDlg', self.RefreshPhyResist)
        
        propitem = pobj.m_Name2PropItem['PromoteZZ']
        propitem.AddRefreshCallbackWithID('PetDlg', self.ShowPromote)
        propitem = pobj.m_Name2PropItem['PromoteMax']
        propitem.AddRefreshCallbackWithID('PetDlg', self.ShowPromote)
        if pobj.m_UpdateProp == False:
            import netpet
            netpet.C2SSummonView(pobj.m_ID)
        
        self.RefreshSkill()
        pobj.AddSkillCallback(self.RefreshSkill)

    
    def RemoveDlgItem(self, pobj):
        self.m_PID = None
        for arr in PET_APTI:
            propitem = pobj.m_Name2PropItem[arr[0]]
            propitem.RemoveRefreshCallbackWithID('PetDlg')
        
        for propname in PET_UPD:
            propitem = pobj.m_Name2PropItem[propname]
            propitem.RemoveRefreshCallbackWithID('PetDlg')
        
        for name, _, _ in PET_MAGRESIST:
            propitem = pobj.m_Name2PropItem[name]
            propitem.RemoveRefreshCallbackWithID('PetDlg')
        
        for name, _, _ in PET_PHYRESIST:
            propitem = pobj.m_Name2PropItem[name]
            propitem.RemoveRefreshCallbackWithID('PetDlg')
        
        propitem = pobj.m_Name2PropItem['PromoteZZ']
        propitem.RemoveRefreshCallbackWithID('PetDlg')
        propitem = pobj.m_Name2PropItem['PromoteMax']
        propitem.RemoveRefreshCallbackWithID('PetDlg')
        self.m_MagLines = []
        self.m_PhyLines = []
        self.ClearSkill()
        pobj.RemoveSkillCallback()
        self.RemovePointsStar()

    
    def RemovePointsStar(self):
        self.ClearStar(-1)
        for name, cname, cid in PET_APTI:
            ctrl = self.GetObject(cname)
            setattr(ctrl, name, None)
        

    
    def RefreshSkill(self):
        import pet
        pobj = pet.GetPet(self.m_PID)
        if pobj and len(pobj.m_Skills) < 13:
            self.CreateSkillIcon()
        elif pobj and len(pobj.m_Skills) >= 13:
            self.CreateSkillIcon2()
        

    
    def CreateSkillIcon(self):
        import pet
        pobj = pet.GetPet(self.m_PID)
        self.m_Icons = []
        if self.m_List:
            self.m_List.Clear()
            self.m_List.SetShow(False)
        
        box_skills = self.GetObject('box_skills')
        box_skills.SetShow(True)
        (bx, by) = box_skills.GetPos()
        for idx, sk in enumerate(pobj.m_Skills):
            
            try:
                (x, y) = box_skills.m_Imagess[idx].GetPos()
                skillObj = CSkillIcon(self, bx + x + 3, by + y + 3, sk, idx == pobj.m_BindSkill)
                skillObj.SetOwnerID(self.m_PID)
                skillObj.SetTag(pobj.IsHFSkillIdx(idx))
                skillObj.SetPillPos(pobj.GetPillSkillIdx(idx))
                self.m_Icons.append(skillObj)
            continue
            except IndexError:
                continue

            None<EXCEPTION MATCH>IndexError
        

    
    def CreateSkillIcon2(self):
        if not self.m_List:
            return None
        
        box_skills = self.GetObject('box_skills')
        box_skills.SetShow(False)
        self.m_List.Clear()
        self.m_List.SetShow(True)
        import pet
        pobj = pet.GetPet(self.m_PID)
        sklLst = []
        self.m_Icons = []
        for idx, sk in enumerate(pobj.m_Skills):
            sklLst.append((idx, sk))
        
        num = (len(pobj.m_Skills) - 1) / 4 + 1
        for i in xrange(num):
            idx = i * 4
            self.AddListItem(sklLst[idx:idx + 4])
        

    
    def AddListItem(self, sklLst):
        import combmacro
        it = interface.CBoxObject(self.m_List, self.m_List.m_ItemWidth, self.m_List.m_ItemHeight, 0, 0)
        it.m_IconBG = []
        filename = self.GetObject('box_skills').m_FileName
        for i in xrange(4):
            bgObj = combmacro.CIMAGE(it, filename, interface.UIPath)
            bgObj.SetPos(self.m_Data[i][0], self.m_Data[i][1])
            bgObj.SetZ(1)
            it.m_IconBG.append(bgObj)
        
        import pet
        pobj = pet.GetPet(self.m_PID)
        for idx, sklData in enumerate(sklLst):
            (sklPos, sklID) = sklData
            skillObj = CSkillIcon(it, self.m_Data[idx][0] + 3, self.m_Data[idx][1] + 3, sklID, sklPos == pobj.m_BindSkill)
            skillObj.SetZ(2)
            skillObj.SetOwnerID(self.m_PID)
            skillObj.SetTag(pobj.IsHFSkillIdx(sklPos))
            skillObj.SetPillPos(pobj.GetPillSkillIdx(sklPos))
            self.m_Icons.append(skillObj)
        
        self.m_List.AddItem(it)
        self.m_List.ResetItems()
        self.m_List.ResetScrollBar()

    
    def ClearSkill(self):
        self.m_Icons = []

    
    def ShowPromote(self):
        import pet
        pobj = pet.GetPet(self.m_PID)
        if pobj:
            prozz = pobj.m_Prop.PromoteZZ
            if prozz:
                if prozz % 2 == 0:
                    obj = self.GetObject('txt_apti2')
                    (ox, oy) = obj.GetPos()
                    (ix, iy) = obj.GetImage(0, prozz / 2 - 1).GetPos()
                else:
                    obj = self.GetObject('txt_apti')
                    (ox, oy) = obj.GetPos()
                    (ix, iy) = obj.GetImage(0, prozz / 2).GetPos()
                x = ox + ix + 34
                y = oy + iy + 3
                prop = (None, 'Ability_Attack', 'Ability_Defense', 'Ability_Con', 'Ability_Magic', 'Ability_Speed')[prozz]
                zz = pobj.m_Name2PropItem[prop].GetInfo()
                zz = int(zz)
                zzmax = pobj.m_Prop.PromoteMax
                if zz >= zzmax:
                    star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xbb\xc6\xd0\xc71.igs')
                else:
                    star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xbb\xc6\xd0\xc72.igs')
                img = ui.CImage(self, star_path, interface.UIPath)
                img.SetPos(x, y)
                (w, h) = img.GetSize()
                box = interface.CNotifyBox(self, w + 4, h + 4, alpha = 0, msgid = 199)
                box.SetPos(x - 2, y - 2)
                box.SetZ(100)
                self.m_Promote = (img, box)
            else:
                self.m_Promote = None
        

    
    def ShowStar(self, idx, times, maxi):
        if idx % 2 == 0:
            obj = self.GetObject('txt_apti2')
            (ox, oy) = obj.GetPos()
            (ix, iy) = obj.GetImage(0, idx / 2 - 1).GetPos()
        else:
            obj = self.GetObject('txt_apti')
            (ox, oy) = obj.GetPos()
            (ix, iy) = obj.GetImage(0, idx / 2).GetPos()
        x = ox + ix + 48
        y = oy + iy + 3
        if times >= maxi:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xd0\xc71.igs')
        else:
            star_path = style.GetPath('combdialog\\\xd4\xd3\xcd\xbc\\\xd0\xc72.igs')
        if not hasattr(self, 'm_Stars'):
            self.m_Stars = { }
        
        img = ui.CImage(self, star_path, interface.UIPath)
        img.SetPos(x, y)
        (w, h) = img.GetSize()
        box = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 20 + idx)
        box.SetPos(x, y)
        self.m_Stars[idx] = (img, box, times, maxi)

    
    def ClearStar(self, idx):
        if hasattr(self, 'm_Stars') and idx in self.m_Stars:
            del self.m_Stars[idx]
        elif idx == -1:
            self.m_Stars = { }
        

    
    def OnEnter(self, msgid):
        import pet
        import wrapinterface
        if msgid <= msgid:
            pass
        elif msgid < 100:
            obj = self.m_TipsInfo[msgid - 90]
            self.m_Tips = wrapinterface.CTextTips(self, -1, obj.m_Info, interface.FontLT14_3, direct = 0)
            self.m_Tips.SetOwner(obj)
            return None
        
        pobj = pet.GetPet(self.m_PID)

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def RefreshMagResist(self):
        import pet
        pobj = pet.GetPet(self.m_PID)
        if pobj:
            self.m_MagLines = []
            _objs = ('loc_xian', 'loc_gui', 'loc_yao', 'loc_zhi', 'loc_nian')
            _props = ('Resist_Xian', 'Resist_Gui', 'Resist_Yao', 'Resist_Zhi', 'Resist_Nian')
            loc_origin = self.GetObject('loc_origin')
            (ox, oy) = loc_origin.GetPos()
            color = interface.COLOR_248
            first = None
            prev = None
            num = style.GetInt(self.GetDlgPath(), 'data_line')
            for idx, s in enumerate(_objs):
                loc = self.GetObject(s)
                (lx, ly) = loc.GetPos()
                (x, y) = getmagp(ox, oy, lx, ly, pobj.GetProp(_props[idx]))
                if prev:
                    self.m_MagLines.append(interface.CLine(self, prev[0], prev[1], x, y, color, num))
                
                if first is None:
                    first = (x, y)
                
                prev = (x, y)
            
            self.m_MagLines.append(interface.CLine(self, prev[0], prev[1], first[0], first[1], color, num))
        

    
    def RefreshPhyResist(self):
        import pet
        pobj = pet.GetPet(self.m_PID)
        if pobj:
            self.m_PhyLines = []
            _props = ('Resist_Lidi', 'Resist_Lingqiao', 'Resist_Qungong', 'Resist_Putong')
            box_phy = self.GetObject('box_phy')
            (x, y) = box_phy.GetPos()
            (w, h) = box_phy.GetSize()
            (offw, offh) = style.GetIntTuple(self.GetDlgPath(), 'line_offpos')
            w += offw
            h += offh
            pt = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
            ox = x + w / 2
            oy = y + h / 2
            first = None
            prev = None
            color = interface.COLOR_248
            num = style.GetInt(self.GetDlgPath(), 'data_line')
            for idx, p in enumerate(pt):
                (lx, ly) = p
                (x, y) = getphyp(ox, oy, lx, ly, pobj.GetProp(_props[idx]))
                if prev:
                    self.m_PhyLines.append(interface.CLine(self, prev[0], prev[1], x, y, color, num))
                
                if first is None:
                    first = (x, y)
                
                prev = (x, y)
            
            self.m_PhyLines.append(interface.CLine(self, prev[0], prev[1], first[0], first[1], color, num))
        

    
    def ShowSwitch(self):
        combdialog.CAttachCombDialog.ShowSwitch(self)
        if self.GetShow():
            if hasattr(self, 'm_UpdateProp') and self.m_UpdateProp == False:
                import netpet
                netpet.C2SSummonView(self.m_ID)
            
        

    
    def RightUp(self):
        self.SetShow(False)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            pass
        



class CRenameNewDialog(combdialog.CCombDialog):
    
    def __init__(self, parent, pid, x, y):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/summon/summonrename.dlg')
        self.m_PID = pid
        self.SetPos(x, y)
        
        class CNameEdit(interface.CEdit):
            
            def MsgEnter(self):
                self.GetParent().OnMessage(1)


        self.m_Input = combmacro.CEDIT(CNameEdit, 'edt_rename', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_Input.SetLimit(12)
        import pet
        ob = pet.GetPet(pid)
        if ob:
            self.m_Input.SetText(ob.m_Prop.m_Name)
            self.m_Input.SetSelect(0, len(ob.m_Prop.m_Name))
        
        self.m_Input.Active(True)

    
    def CloseWindow(self):
        if hasattr(self, 'GetParent') and self.GetParent() is not None:
            self.GetParent().m_RenameDlg = None
        

    
    def SendPetRename(self, pID, petName):
        global g_RenamePetInfo, g_RenamePetInfo
        import mainmenu
        if mainmenu.IsWar():
            g_RenamePetInfo = {
                'isSend': False,
                'petID': pID,
                'petName': petName }
            usermacro.PROMPT_MSG('\xa6W\xa6r\xad\xd7\xa7\xef\xa7\xb9\xb2\xa6\xa1A\xbe\xd4\xb0\xab\xb5\xb2\xa7\xf4\xab\xe1\xa7Y\xa5\xcd\xae\xc4')
            return None
        else:
            g_RenamePetInfo = {
                'isSend': True,
                'petID': None,
                'petName': None }
            import netpet
            netpet.C2SRename(pID, petName)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            txt = self.m_Input.GetText()
            if len(txt) == 0:
                self.m_Warning = interface.CAutoHideText(self, '\xbd\xd0\xb6\xf1\xbcg\xa4\xba\xaee', interface.FontLT14_3, 16711680, 90)
                self.m_Warning.SetPos(25, 52)
                return None
            else:
                import pet
                import banword
                import petdata
                import usermacro
                import misc
                ob = pet.GetPet(self.m_PID)
                if ob:
                    d = petdata.GetData(ob.m_Prop.m_Shape)
                    if txt != d['name'] and not banword.IsValidName(txt):
                        usermacro.PROMPT_MSG('\xb1z\xa8\xfa\xaa\xba\xa6W\xa6r\xa4\xa4\xa5]\xa7t\xb1\xd3\xb7P\xa6r\xb2\xc5')
                        return None
                    
                    if misc.SearchUnicode(txt, '#') >= 0 or misc.SearchUnicode(txt, '\xa1\xad') >= 0:
                        usermacro.PROMPT_MSG('\xa5l\xb3\xea\xc3~\xa6W\xa6r\xa4\xa4\xa4\xa3\xaf\xe0\xa7t\xa6\xb3##')
                        return None
                    
                
            self.SendPetRename(self.m_PID, txt)
            self.OnMessage(2)
        elif msgid == 2:
            self.m_Input.Active(False)
            self.CloseWindow()
        elif msgid == 3:
            import pet
            ob = pet.GetPet(self.m_PID)
            if ob:
                import petdata
                d = petdata.GetData(ob.m_Prop.m_Shape)
                self.m_Input.SetText(d['name'])
            
        



class CFakeRole(walker.CFakeRole):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, realShape = None, iIsUseNewRes = None):
        walker.CFakeRole.__init__(self, parent, iObjID, iCharIdx, desc, realShape, iIsUseNewRes)
        self.m_PlayState = [
            'stand',
            'magic',
            'walk',
            'attack']
        if iCharIdx in (4024, 4025):
            self.m_PlayState = [
                'stand',
                'spestand',
                'magic',
                'walk',
                'attack']
        

    
    def LeftUp(self):
        state = self.GetNextState()
        if state == self.m_State:
            state = self.GetNextState()
        
        self.ReleaseMyTimer()
        self.SetState(state)
        
        def Delay(obj, tick):
            if tick > 0:
                return (tick - 1,)
            
            obj.SetState('stand')

        self.m_MyTimer = self.CreatePyCommand(30, Delay, 9)

    
    def GetNextState(self):
        if not hasattr(self, 'm_NowStateIdx'):
            self.m_NowStateIdx = 0
        
        iLen = len(self.m_PlayState)
        self.m_NowStateIdx = (self.m_NowStateIdx + 1) % iLen
        return self.m_PlayState[self.m_NowStateIdx]

    
    def ReleaseMyTimer(self):
        if getattr(self, 'm_MyTimer', None):
            self.m_MyTimer.Release()
            self.m_MyTimer = None
        



class CPetDialog(combdialog.CCombDialog):
    FourLiShape = [
        4006,
        4007,
        4014,
        2730,
        2750,
        4009,
        4011]
    FourMoShape = [
        4008,
        4012,
        2740,
        2760]
    FiveMei = [
        4010]
    CARRY_COUNT_2_STR = {
        5: 1,
        6: 2,
        7: 4,
        8: 8,
        9: 16,
        10: 24,
        11: 32 }
    
    class CClickNotifyBox(interface.CClickBox):
        
        def Enter(self):
            parent = self.GetParent()
            if parent:
                parent.OnEnter(self.m_MsgID)
            

        
        def Leave(self):
            
            try:
                parent = self.GetParent()
            except SystemError:
                return None

            if not parent:
                return None
            
            parent.OnLeave(self.m_MsgID)

        
        def LeftUp(self):
            parent = self.GetParent()
            if parent:
                parent.OnMessage(self.m_MsgID)
            


    
    def __init__(self):
        import ratio
        import hero
        import commoncb
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/summon/summon.dlg')
        if ratio.Is1024x768():
            (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_pos_1024x768')
        elif ratio.Is1366x768():
            (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_pos_1366x768')
        elif ratio.Is1366x708():
            x = 722
            y = ratio.GetYBy1366x768(57)
        elif ratio.Is1280x960():
            x = 636
            y = ratio.GetYBy1280x960(57)
        else:
            (x, y) = (40, 50)
        self.SetPos(x, y)
        self.m_FightPetID = None
        self.m_DlgHelpID = 5020
        self.m_Points = [
            0,
            0,
            0,
            0,
            0,
            0]
        self.m_BakPoints = [
            0,
            0,
            0,
            0,
            0,
            0]
        self.m_FightPoint = [
            0]
        self.m_PetcDialog = CPetcDialog(self)
        self.RefreshPets()
        _btns = ('btn_con_sub', 'btn_con_add', 'btn_str_sub', 'btn_str_add', 'btn_mag_sub', 'btn_mag_add', 'btn_cha_sub', 'btn_cha_add', 'btn_dex_sub', 'btn_dex_add')
        for i in _btns:
            self.GetObject(i).m_Button_Type = 1
        
        propitem = hero.g_Name2PropItem['m_SummonMax']
        propitem.AddRefreshCallbackWithID('PetDlg', self.ShowSummonNum)
        propitem = hero.g_Name2PropItem['m_Grade']
        propitem.AddRefreshCallbackWithID('PetDlg', self.RefreshUseExpShow)
        self.DrawTips()
        obj = self.GetObject('grade_tip')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        self.m_MLGNotify = interface.CNotifyBox(self, w, h, 0, 0, msgid = 98)
        self.m_MLGNotify.SetPos(x, y)
        self.GetObject('btn_tuijian').m_ParentNotify = True
        self.m_OnLookPet = None
        import dlgshenmoisland
        if dlgshenmoisland.IsShenmoHuodong():
            self.GetObject('btn_Auto').SetShow(False)
        
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneChange')

    
    def RefreshTips(self, pid):
        import pet
        import petdata
        obj = self.GetObject('grade_tip')
        (x, y) = obj.GetPos()
        if interface.IsOldStyle():
            fileName = '\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'
            self.m_oTips = combmacro.CIMAGE(self, fileName)
            self.m_oTips.SetPos(x, y)
        
        
        try:
            pobj = pet.GetPet(pid)
            shape = pobj.m_Prop.m_Shape
            if (petdata.IsShenShou(shape) and petdata.IsXianShou(shape) or petdata.IsZhenYingShou(shape)) and pobj.m_Prop.m_Grade < 6:
                obj.SetShow(False)
                if hasattr(self, 'm_oTips'):
                    self.m_oTips.SetShow(False)
                
            else:
                obj.SetShow(True)
                if hasattr(self, 'm_oTips'):
                    self.m_oTips.SetShow(True)
        except:
            LOG_EXC('dlgpet.RefreshTips\xa8\xea\xb7s\xb2\xa7\xb1`pid\xa1G%d' % pid)
        


    
    def RefreshUseExpShow(self):
        petID = getattr(self, 'm_SelPetID', None)
        self.RefreshUseExpWithID(petID)

    
    def RefreshUseExpWithID(self, petID):
        import hero
        import pet
        bShow = True
        if hero.g_Prop.m_Grade < 100 or not petID:
            bShow = False
        else:
            petObj = pet.GetPet(petID)
            if not petObj:
                bShow = False
            elif petObj.m_Prop.m_Grade >= hero.g_Prop.m_Grade + 3 or self.m_IsExpFull:
                bShow = False
            
        btn = self.GetObject('btn_SummonExp')
        btn.SetShow(bShow)
        btn.SetZ(1000)

    
    def OnButtonEnter(self, btn):
        if btn.m_MsgID == 17:
            import wrapinterface
            self.m_TuijianTips = wrapinterface.CTextTips(self, -1, '\xa8\xcf\xa5\xce\xa8t\xb2\xce\xb1\xc0\xaf\xf2\xa4\xe8\xae\xd7\xa4\xc0\xb0t\xc2I\xbc\xc6', interface.FontLT14_3, direct = 1, owner = btn)
        

    
    def OnButtonLeave(self, btn):
        self.m_TuijianTips = None

    
    def Topmost(self):
        if hasattr(self, 'm_Frames'):
            combdialog.CCombDialog.Topmost(self)
        

    
    def DrawTips(self):
        (x, y) = self.GetObject('txt_CarryCount').GetPos()
        (w, h) = self.GetObject('txt_CarryCount').GetSize()
        self.m_CarryCountBox = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 96)
        self.m_CarryCountBox.SetPos(x, y)
        msgid = 100
        self.m_TipsInfo = []
        tips = [
            '\xa5D\xadn\xbcv\xc5T\xae\xf0\xa6\xe5\xa4W\xad\xad',
            '\xbcv\xc5T\xaa\xab\xb2z\xa7\xf0\xc0\xbb\xa4O\xbbP\xa4O\xb9D\xad\xc8',
            '\xbcv\xc5T\xaak\xb3N\xa7\xf0\xc0\xbb\xa4O\xbbP\xaak\xa4O\xad\xc8',
            '\xbcv\xc5T\xa8\xbe\xbfm\xa4O\xa1A\xab\xec\xb4_\xc3\xfe\xbbP\xab\xca\xa6L\xc3\xfe\xaak\xb3N',
            '\xa5D\xadn\xbcv\xc5T\xb3t\xab\xd7',
            '\xa5i\xa6\xdb\xa5\xd1\xa4\xc0\xb0t\xaa\xba\xc4\xdd\xa9\xca\xc2I',
            '\xa5\xcd\xa9R\xad\xc8\xa4W\xad\xad',
            '\xaak\xa4O\xad\xc8\xa4W\xad\xad',
            '\xa4O\xb9D\xad\xc8\xa4W\xad\xad',
            '\xaa\xab\xb2z\xb6\xcb\xae`\xaa\xba\xbf\xe9\xa5X\xaf\xe0\xa4O',
            '\xaa\xab\xb2z\xb6\xcb\xae`\xaa\xba\xa9\xe8\xa7\xdc\xaf\xe0\xa4O',
            '\xaak\xb3N\xb6\xcb\xae`\xaa\xba\xbf\xe9\xa5X\xa9M\xa9\xe8\xa7\xdc\xaf\xe0\xa4O',
            '\xbe\xd4\xb0\xab\xa4\xa4\xa5X\xa4\xe2\xaa\xba\xa7\xd6\xbaC',
            '\xa4H\xaa\xab\xa8\xec\xb9F\xa6\xb9\xb5\xa5\xaf\xc5\xab\xe1\xa4~\xa5i\xa5H\xc4\xe2\xb1a']
        objLst = ('tip_Con', 'tip_Str', 'tip_Mag', 'tip_Cha', 'tip_Dex', 'tip_Point', 'tip_HP', 'tip_MP', 'tip_FP', 'tip_Att', 'tip_Def', 'tip_Magdef', 'tip_Spe', 'tip_Takegrade')
        for i, objName in enumerate(objLst):
            iBox = self.GetObject(objName)
            (x, y) = iBox.GetPos()
            (w, h) = iBox.GetSize()
            tmp = interface.CNotifyBox(self, w, h, alpha = 0, msgid = msgid)
            tmp.SetPos(x, y)
            tmp.m_Info = tips[i]
            tmp.SetZ(-1)
            self.m_TipsInfo.append(tmp)
            msgid += 1
        

    
    def BnEnter(self, msgid):
        import wrapinterface
        if msgid in (7, 13, 14, 15, 16):
            txt = '\xa5\xaa\xc1\xe4\xb3\xe6\xc0\xbb\xbcW\xa5[1\xc2I\xa1A\xab\xf6\xa6\xed\xa5[\xb3t\xa1A\xa5k\xc1\xe4\xc2I\xc0\xbb\xa5[\xa8\xec\xb3\xcc\xa4j'
        elif msgid in (8, 23, 22, 20, 19):
            txt = '\xa5\xaa\xc1\xe4\xb3\xe6\xc0\xbb\xb4\xee\xa4\xd6\xa4@\xc2I\xa1A\xab\xf6\xa6\xed\xa5[\xb3t\xa1A\xa5k\xc1\xe4\xc2I\xc0\xbb\xb4\xee\xa8\xec\xb3\xcc\xa4p'
        
        self.m_AddTips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 0)

    
    def BnLeave(self, msgid):
        self.m_AddTips = None
        self.ClearAutoAdd()

    
    def BnLeftUp(self, msgid):
        self.ClearAutoAdd()

    
    def BnLeftDown(self, msgid):
        
        def AutoAdd(obj, frame, msgid):
            if frame < 15:
                return (frame + 1, msgid)
            
            if frame < 75:
                obj.OnMessage(msgid)
                return (frame + 1, msgid)
            
            obj.OnMessage(msgid)
            obj.OnMessage(msgid)
            return (100, msgid)

        self.m_AutoCmd = self.CreatePyCommand(1, AutoAdd, 0, msgid)

    
    def ClearAutoAdd(self):
        if hasattr(self, 'm_AutoCmd') and self.m_AutoCmd:
            self.m_AutoCmd.Release()
            self.m_AutoCmd = None
        

    
    def ShowExpTips(self, pID):
        import hero
        import pet
        pObj = pet.GetPet(pID)
        if pObj is None:
            return None
        
        needExp = pObj.GetProp('m_ExpNext') - pObj.GetProp('m_Exp')
        if needExp < 0:
            needExp = 0
        
        txt = '\xa4\xc9\xaf\xc5\xa9\xd2\xbb\xdd\xb8g\xc5\xe7: #Y%d#n' % needExp
        if pObj.m_Prop.m_ExpNeed:
            txt += '#r\xad\xb8\xaa@\xb8\xc9\xa8\xac\xb8g\xc5\xe7\xa1G#Y%d#n' % pObj.m_Prop.m_ExpNeed
        
        if hero.g_Prop.m_SumCBExp > 0:
            txt += '#r\xa5l\xb3\xea\xc3~\xc0x\xb3\xc6\xb8g\xc5\xe7\xa1G#Y%d#n' % hero.g_Prop.m_SumCBExp
        
        if hero.GetProp('m_SumHFExp', 0) > 0:
            txt += '#r\xa5l\xb3\xea\xc3~\xa6X\xb0\xcf\xc0x\xb3\xc6\xb8g\xc5\xe7\xa1G#Y%d#n' % hero.GetProp('m_SumHFExp')
        
        self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 0)

    
    def OnEnter(self, msgid):
        import pet
        import hero
        import wrapinterface
        if msgid >= 100:
            if self.m_TipsInfo[msgid - 100].m_Info != '':
                self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_TipsInfo[msgid - 100].m_Info, interface.FontLT14_3, direct = 0)
            
        elif msgid == 99:
            summonList = self.GetObject('lst_summon')
            sel = combmacro.GetSelectedItemFromList(summonList)
            if sel:
                self.ShowExpTips(sel.m_PID)
            
        elif msgid == 98:
            summonList = self.GetObject('lst_summon')
            sel = combmacro.GetSelectedItemFromList(summonList)
            if sel:
                pobj = pet.GetPet(sel.m_PID)
                if pobj and hero.g_Prop.m_Grade >= 30:
                    lst = []
                    if pet.UseYX(pobj):
                        lst.append('\xa4\xb8\xaed\xa8\xcf\xa5\xce\xbc\xc6\xb6q\xa1G%d/%d' % (pobj.GetProp('m_YuanXiao'), pobj.GetProp('m_YuanXiaoMxNum')))
                    
                    if pet.UseMLG(pobj):
                        lst.append('\xc5]\xc6F\xaaG\xa8\xcf\xa5\xce\xb6q\xa1G%d/%d' % (pobj.GetProp('m_MoLingGuo'), pobj.GetProp('m_Grade') / 3 + 3))
                    
                    if pobj.GetProp('m_MaxShenXian') > 0:
                        lst.append('\xaf\xab\xa5P\xaaG\xa8\xcf\xa5\xce\xb6q\xa1G%d/%d' % (pobj.GetProp('m_ShenXian'), pobj.GetProp('m_MaxShenXian')))
                    
                    if lst:
                        msg = '#r'.join(lst)
                        self.m_Tips = wrapinterface.CTextTips(self, -1, msg, interface.FontLT14_3, direct = 0)
                    
                
            
        elif msgid == 96:
            summonMax = hero.g_Prop.m_SummonMax
            if summonMax < 12:
                carryCount = self.CARRY_COUNT_2_STR[summonMax]
                self.m_Tips = wrapinterface.CTextTips(self, -1, '\xa5i\xa5H\xa8\xcf\xa5\xce\xber\xb1s\xc4_\xa8\xe5\xbcW\xa5[\xc4\xe2\xb1a\xc4\xe6\xa6\xec#r\xb8\xd1\xc2\xea\xa4U\xa4@\xc4\xe6\xa6\xec\xbb\xdd\xadn\xa1G#G%d#n\xad\xd3\xber\xb1s\xc4_\xa8\xe5' % carryCount, interface.FontLT14_3, direct = 0)
            
        elif msgid == 30:
            selPetID = 0
            if hasattr(self, 'm_SelPetID') and self.m_SelPetID:
                selPetID = self.m_SelPetID
            
            txt = GetBindTips(self.m_Key, self.m_SelPetID)
            if txt is not None:
                self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
            
        elif msgid == 31:
            txt = GetBirthTips(self.m_Key)
            if txt is not None:
                self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
            
        elif msgid == 32:
            self.m_Tips = wrapinterface.CTextTips(self, -1, '\xb1N\xb3Q\xa7@\xac\xb0\xad\xb8\xaa@\xb6i\xa4\xc6\xaa\xba\xb0\xc6\xc3d\xb3Q\xa7]\xbe\xbd\xa1A#r\xb8\xd4\xb1\xa1\xa5i\xa8\xec\xa4\xd1\xaa\xc5\xadn\xb6\xeb\xaa\xba\xb1i\xa4\xd1\xaev\xb3B\xacd\xac\xdd#r\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa5i\xa8\xfa\xae\xf8\xb3Q\xa7]\xbe\xbd\xa5\xd3\xbd\xd0', interface.FontLT14_3, direct = 1)
        elif msgid == 33:
            self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_LianHuaTips, interface.FontLT14_3, direct = 1)
        elif msgid == 34:
            txt = None
            petID = getattr(self, 'm_SelPetID', None)
            if petID:
                lianyao = pet.GetPet(petID).GetProp('m_Lianyao')
                txt = GetLianyaoTips(lianyao)
            
            if txt is not None:
                self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
            
        elif msgid == 35:
            txt = None
            petID = getattr(self, 'm_SelPetID', None)
            if petID:
                tunshi = pet.GetPet(petID).GetProp('m_Tunshi')
                txt = GetTunshiTips(tunshi)
            
            if txt is not None:
                self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
            
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def RefreshJieBangTips(self, iCash, iTime):
        import misc
        if iCash:
            txt = '\xb8\xd1\xb8j\xa6\xa8\xa5\\\xab\xe1\xb3\xcc\xa7C\xa5\xe6\xa9\xf6\xbb\xf9\xae\xe6\xac\xb0#R%d#n\xa8\xe2\xb2{\xaa\xf7#r\xa6\xb9\xa5l\xb3\xea\xc3~\xb1N\xa6b#R%s#n\xab\xe1\xb8\xd1\xb0\xa3\xb8j\xa9w' % (iCash, misc.Int2TimeStr(iTime))
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
        

    
    def ShowSummonNum(self):
        import hero
        lst_summon = self.GetObject('lst_summon')
        color = interface.COLOR_5
        self.m_txtSummonNum = combmacro.CTEXT((interface.CBlackShadowText, interface.CTextObject, interface.CTextObject, interface.CTextObject)[interface.STYLE], 'txt_max', self, '%d/%d' % (len(lst_summon.m_Items), hero.g_Prop.m_SummonMax), interface.FontLT14_3, color, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)

    
    def RefreshExpInfo(self, petID):
        import pet
        import wrapinterface
        import dlgstate
        (x, y, w, h) = self.GetLocData('txt_exp')
        pObj = pet.GetPet(petID)
        if pObj is None:
            return None
        
        iExp = pObj.GetProp('m_Exp')
        iNextExp = pObj.GetProp('m_ExpNext')
        if iExp is None or iNextExp is None:
            return None
        
        filePath = style.GetStr(self.GetDlgPath(), 'data_exp_progress')
        (iOffsetX, iOffsetY) = style.GetIntTuple(self.GetDlgPath(), 'data_exp_progress')
        pX = x + iOffsetX
        pY = y + iOffsetY
        iW = style.GetInt(self.GetDlgPath(), 'data_exp_progress')
        self.m_ExpProgress = None(wrapinterface.CProgress, self + w.GetDlgPath, filePath)
        self.m_ExpProgress.SetPos(pX, pY)
        self.m_ExpProgress.SetRate(iExp * 1000 / iNextExp)
        self.m_ExpProgress.SetZ(-1)
        sExp = str(iExp)
        sNextExp = str(iNextExp)
        n = max(len(sExp), len(sNextExp))
        color = interface.COLOR_5
        expObj = dlgstate.GetTextClass()(self, '%s/' % sExp.rjust(n), interface.FontLT14_3, color, 0)
        netExpObj = dlgstate.GetTextClass()(self, '%s' % sNextExp.ljust(n), interface.FontLT14_3, color, 0)
        (expW, expH) = expObj.GetSize()
        totalW = expW + netExpObj.GetSize()[0]
        startX = x + ((w - totalW) + 1) / 2
        startY = y + ((h - expH) + 1) / 2
        expObj.SetPos(startX, startY)
        netExpObj.SetPos(startX + expW, startY)
        self.m_ExpTextObjs = (expObj, netExpObj)
        self.m_NotifyBox = combmacro.CNOTIFYBOX(interface.CNotifyBox, 'txt_exp', self, 99)
        self.ShowFullTxt(iExp, iNextExp)

    
    def ShowFullTxt(self, iExp, iNextExp):
        self.m_FullTxt = None
        self.m_IsExpFull = False
        if iExp >= 10 * iNextExp:
            self.m_IsExpFull = True
            color = interface.COLOR_301
            self.m_FullTxt = combmacro.CTEXT(interface.CShadowText, 'txt_exp', self, '\xba\xa1', interface.FontLT14_3, color, align = interface.ALIGN_RIGHT | interface.ALIGN_MIDDLE)
            if interface.IsNewStyle():
                (x, y) = self.m_FullTxt.GetPos()
                self.m_FullTxt.SetPos(x, y - 3)
            
        

    
    def CreateDlgItem(self, pobj):
        unBindTime = 0
        if hasattr(pobj, 'm_UnBindTime'):
            unBindTime = pobj.m_UnBindTime
        
        self.UpdatePhoto(pobj.m_ID, pobj.GetProp('m_Shape'), pobj.GetProp('m_Desc'), (pobj.m_BirthKey & 255) << 8 | pobj.m_Key & 255, unBindTime)
        pobj.CreateFuMoCombDlgItemSingle('PetDlg', g_PetPRops1, self)
        pobj.AddRefreshCallback('PetDlg', PET_POINTS, self.OnShowPoints, pobj.m_ID)
        pobj.AddRefreshCallback('PetPoint', (('m_Point',),), self.OnPointChange, pobj.m_ID)
        pobj.AddRefreshCallback('RefreshExpInfo', (('m_Exp',), ('m_ExpNext',)), self.RefreshExpInfo, pobj.m_ID)
        pobj.AddRefreshCallback('RefreshExpBuy', (('m_Grade',),), self.RefreshUseExpWithID, pobj.m_ID)
        self.RefreshTips(pobj.m_ID)
        self.m_PetcDialog.CreateDlgItem(pobj)

    
    def RemoveDlgItem(self, pobj):
        self.ClearPhoto()
        pobj.ReleaseDlgItem('PetDlg', PET_PROPS)
        pobj.RemoveRefreshCallback('PetDlg', PET_POINTS)
        pobj.RemoveRefreshCallback('PetPoint', (('m_Point',),))
        pobj.RemoveRefreshCallback('RefreshExpInfo', (('m_Exp',), ('m_ExpNext',)))
        pobj.RemoveRefreshCallback('RefreshExpBuy', (('m_Grade',),))
        self._removepoints()
        self.m_SelPetID = None
        self.RefreshUseExpShow()
        self.m_PetcDialog.RemoveDlgItem(pobj)

    
    def _removepoints(self):
        ctrl = self.GetObject('txt_point')
        for v in PET_POINTS:
            setattr(ctrl, v[0], None)
        
        self.m_PetCarryGrade = None

    
    def OnPointChange(self, pid):
        self.m_Points = [
            0,
            0,
            0,
            0,
            0,
            0]
        self.OnShowPoints(pid)

    
    def OnShowPoints(self, pid):
        import pet
        self.m_AssignTextList = []
        pObj = pet.GetPet(pid)
        if not pObj:
            return None
        
        txtCls = None if interface.IsStyle1() else interface.CTextObject
        ctrl = self.GetObject('txt_point')
        for name, x, y, align in enumerate(PET_POINTS[0:5]):
            iPoint = pObj.GetProp(name)
            iAssign = self.m_Points[idx]
            color = interface.COLOR_9
            if iAssign:
                xbase = style.GetInt(self.GetDlgPath(), 'data_assign_x')
                obj = combmacro.CreateIFTextWithObject(ctrl, txtCls, x, y, '+%d' % iAssign, interface.FontLT14_3, interface.COLOR_2, align = align, xbase = xbase)
                self.m_AssignTextList.append(obj)
            
            obj = combmacro.CreateIFTextWithObject(ctrl, txtCls, x, y, '%d' % iPoint, interface.FontLT14_3, color, align = align, xbase = -6)
            setattr(ctrl, name, obj)
            self.ShowPointBox(name, pObj)
        
        (name, x, y, align) = PET_POINTS[5]
        iAssign = self.m_Points[5]
        iPoint = pObj.GetProp(name)
        self.CheckShowBtn(iPoint, pObj)
        color = None if iAssign < 0 else interface.COLOR_9
        obj = combmacro.CTEXT(txtCls, 'loc_Point', self, str(iPoint + iAssign), interface.FontLT14_3, color, align = align)
        setattr(ctrl, name, obj)

    
    def GetDesc(self, pid):
        import time
        import misc
        if g_MergePetsInfo:
            desc = '%02d-%02d\xa5i\xb3Q\xa7]\xbe\xbd' % time.localtime(misc.GetServerCurrentTime() + g_MergePetsInfo[pid])[1:3]
            return desc
        

    
    def ShowMergeText(self):
        self.m_MergeTxt = None
        if hasattr(self, 'm_SelPetID') and self.m_SelPetID:
            petid = self.m_SelPetID
        else:
            petid = -1
        desc = ''
        if g_RestTimeInfo:
            for pid, showtype in g_RestTimeInfo.items():
                if pid == petid:
                    if showtype == 1:
                        desc = self.GetDesc(pid)
                        break
                    elif showtype == 2:
                        desc = '\xa5i\xb3Q\xa7]\xbe\xbd'
                        break
                    
                showtype == 1
            
            if desc:
                import clickimage
                (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_txt_pos')
                color = interface.COLOR_86
                self.m_MergeTxt = self.m_LianHuaTxt = clickimage.CClickText(self, x, y, desc, color, color, interface.FontLT12E_1, 32)
                self.m_MergeTxt.SetZ(100)
            else:
                self.m_MergeTxt = None
        

    
    def RefreshLianHuaText(self):
        import misc
        import time
        self.m_LianHuaTxt = None
        self.m_LianHuaTips = ''
        desc = ''
        if g_LianHuaTime:
            for pid, itime in g_LianHuaTime.items():
                if getattr(self, 'm_SelPetID', None) and pid == self.m_SelPetID:
                    curTime = misc.GetServerCurrentTime()
                    leaveTime = itime - curTime
                    if leaveTime > 0:
                        desc = '\xa5\xd3\xbd\xd0\xb7\xd2\xa4\xc6\xa4\xa4'
                        timeList = time.localtime(itime)
                        self.m_LianHuaTips = '%.2d-%.2d %.2d:%.2d \xa5i\xa5H\xad\xab\xb7s\xb7\xd2\xa4\xc6#r\xb3\xe6\xc0\xbb\xa5\xaa\xc1\xe4\xa8\xfa\xae\xf8\xa5\xd3\xbd\xd0' % timeList[1:5]
                        break
                    else:
                        desc = '\xa5i\xad\xab\xb7s\xb7\xd2\xa4\xc6'
                        self.m_LianHuaTips = '\xa5i\xa5H\xad\xab\xb7s\xb7\xd2\xa4\xc6#r\xb3\xe6\xc0\xbb\xa5\xaa\xc1\xe4\xa8\xfa\xae\xf8\xa5\xd3\xbd\xd0'
                        break
                leaveTime > 0
            
            if desc:
                import clickimage
                (x, y) = style.GetIntTuple(self.GetDlgPath(), 'data_txt_pos')
                if getattr(self, 'm_MergeTxt', None):
                    y += 15
                
                color = interface.COLOR_2
                self.m_LianHuaTxt = clickimage.CClickText(self, x, y, desc, color, color, interface.FontLT12E_1, 33)
                self.m_LianHuaTxt.SetZ(100)
            else:
                self.m_LianHuaTxt = None
        

    
    def CheckShowBtn(self, point, pobj):
        if pobj.m_Prop.m_Grade <= 60 and point > 0:
            pass
        self.GetObject('btn_tuijian').SetShow(point % 5 == 0)
        if point != 0:
            pass
        self.GetObject('btn_Sure').SetShow(self.m_Points[5] != 0)

    
    def ShowPointBox(self, name, pobj):
        import hero
        import pet
        if name == 'm_Point':
            if pobj == pet.GetActivatePet() and pobj.GetProp('m_Point') >= 10 and hero.g_Prop.m_Grade < 50:
                args = ('\xbf\xef\xbe\xdc#G\xa1i\xb1\xc0\xaf\xf2\xa1j#n\xa5i\xa5H\xac\xb0\xa5l\xb3\xea\xc3~\xa6\xdb\xb0\xca\xa4\xc0\xb0t\xc2I\xbc\xc6', 6, 60, 8, 150, 50)
                import wrapinterface
                self.m_PointBox = wrapinterface.CCombTipsBox(self.GetObject('btn_tuijian'), *args)
            
        

    
    def AddPet(self, pobj, autoselect = True):
        import pet
        lst_summon = self.GetObject('lst_summon')
        it = lst_summon.AddTextItem('%-12s%4d' % (pobj.m_Prop.m_Name, pobj.m_Prop.m_Grade))
        it.m_PID = pobj.m_ID
        if pet.GetActivatePet() == pobj:
            it.SetTextColor(interface.COLOR_228)
        
        lst_summon.ResetItems()
        lst_summon.ResetScrollBar()
        sel = combmacro.GetSelectedItemFromList(lst_summon)
        if sel is None and autoselect:
            it.Select(True)
            self.SelectPet(it.m_PID)
        
        if pet.GetActivatePet() == pobj:
            SetMutex()
            it.LeftUp()
            RefreshMutex()
        
        return it

    
    def RemovePet(self, pobj):
        import pet
        import dlgpetitem
        lst_summon = self.GetObject('lst_summon')
        sel = combmacro.GetSelectedItemFromList(lst_summon)
        if sel:
            ob = pet.GetPet(sel.m_PID)
            if ob:
                self.RemoveDlgItem(ob)
                if ob == pobj:
                    self.m_Points = [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0]
                    self.m_BakPoints = [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0]
                
            
        
        lst_summon.Clear()
        auto = True
        for p in pet.g_SortPets:
            if p.m_ID != pobj.m_ID:
                it = self.AddPet(p, auto)
                if not auto and p.m_ID == sel.m_PID:
                    it.Select(True)
                    self.SelectPet(it.m_PID)
                
            p.m_ID == sel.m_PID
        
        if dlgpetitem.g_PetItem and dlgpetitem.g_PetItem.GetShow():
            dlgpetitem.g_PetItem.RefreshPetInfo(pobj.m_ID, 2)
        

    
    def GetSelectPetID(self):
        summonList = self.GetObject('lst_summon')
        selItem = combmacro.GetSelectedItemFromList(summonList)
        if selItem:
            return selItem.m_PID
        

    
    def HidePet(self, flag):
        if flag:
            self.GetObject('btn_lookon').SetText('\xb8\xf2 \xc0H')
        else:
            self.GetObject('btn_lookon').SetText('\xc1\xf4 \xc2\xc3')

    
    def UpdatePet(self, pobj):
        import pet
        lst_summon = self.GetObject('lst_summon')
        for it in lst_summon.m_Items:
            if pet.GetActivatePet() and pet.GetActivatePet().m_ID == it.m_PID:
                it.SetTextColor(interface.COLOR_228)
            else:
                it.SetTextColor(interface.COLOR_88)
            if it.m_PID == pobj.m_ID:
                it.SetText('%-12s%4d' % (pobj.m_Prop.m_Name, pobj.m_Prop.m_Grade))
                if it.IsSelected():
                    import copy
                    self.m_Points = copy.deepcopy(self.m_BakPoints)
                    self.SelectPet(it.m_PID)
                
            it.IsSelected()
        

    
    def RefreshPets(self, petID = None):
        import pet
        lstObj = self.GetObject('lst_summon')
        lstObj.InitPosXLst([
            10,
            105])
        preLoc = -1
        if len(lstObj.m_Items) == len(pet.g_SortPets):
            if hasattr(lstObj, 'm_VScrollBar') and lstObj.m_VScrollBar:
                preLoc = lstObj.m_VScrollBar.GetPos()
            
        
        if pet.g_SortPets:
            if not petID:
                petID = self.GetSelectPetID()
            
            lstObj.Clear()
            for p in pet.g_SortPets:
                self.AddPet(p)
            
        
        if petID:
            for item in lstObj.m_Items:
                if item.m_PID == petID:
                    SetMutex()
                    item.LeftUp()
                    RefreshMutex()
                    continue
            
        
        if preLoc != -1:
            lstObj.m_VScrollBar.SetBarPos(preLoc)
        

    
    def UpdatePhoto(self, petID, shape, desc, key = None, itime = 0):
        import wrapinterface
        import pet
        import misc
        self.ClearPhoto()
        petobj = pet.GetPet(petID)
        LianyaoTime = petobj.GetProp('m_Lianyao')
        TunshiTime = petobj.GetProp('m_Tunshi')
        tkey = 0
        if LianyaoTime == 0:
            pass
        elif LianyaoTime > misc.GetServerCurrentTime():
            tkey = tkey | 1
        else:
            tkey = tkey | 2
        if TunshiTime == 0:
            pass
        elif TunshiTime > misc.GetServerCurrentTime():
            tkey = tkey | 4
        else:
            tkey = tkey | 8
        if getattr(self, 'm_PetAni', None):
            self.m_PetAni.m_Photo.ReleaseMyTimer()
        
        self.m_PetAni = wrapinterface.CPetAniWithUnlock(self, shape, desc, key, walkerClass = CFakeRole, unbandtime = itime, timekey = tkey)
        self.m_PetAni.SetColorCompensate(petobj.GetProp('m_bIsColorCompensate'), petID)
        self.m_PetAni.SetPetID(petID)
        self.m_PetAni.ReleaseRandomAni()
        box_icon = self.GetObject('box_icon')
        (x, y) = box_icon.GetPos()
        self.m_PetAni.SetPos(x + 7, y + 5)
        self.m_Key = key
        self.CreateNotifyBox()

    
    def CreateNotifyBox(self):
        bindinfo = self.m_PetAni.GetBindImgInfo()
        birthinfo = self.m_PetAni.GetBirthImgInfo()
        lianyaoinfo = self.m_PetAni.GetLianyaoImgInfo()
        tunshiinfo = self.m_PetAni.GetTunshiImgInfo()
        (x, y) = self.m_PetAni.GetPos()
        if bindinfo:
            (w, h, bind_x, bind_y) = bindinfo
            self.m_BindNotifyBox = interface.CNotifyBox(self, w, h, 0, 0, 30)
            self.m_BindNotifyBox.SetPos(x + bind_x, y + bind_y)
        
        if lianyaoinfo:
            (w, h, lianyao_x, lianyao_y) = lianyaoinfo
            self.m_LianyaoNotifyBox = self.CClickNotifyBox(self, w, h, 0, 0, 34)
            self.m_LianyaoNotifyBox.SetPos(x + lianyao_x, y + lianyao_y)
        
        if tunshiinfo:
            (w, h, tunshi_x, tunshi_y) = tunshiinfo
            self.m_TunshiNotifyBox = self.CClickNotifyBox(self, w, h, 0, 0, 35)
            self.m_TunshiNotifyBox.SetPos(x + tunshi_x, y + tunshi_y)
        
        if birthinfo:
            (w, h, birth_x, birth_y) = birthinfo
            self.m_BirthNotifyBox = interface.CNotifyBox(self, w, h, 0, 0, 31)
            self.m_BirthNotifyBox.SetPos(x + birth_x, y + birth_y)
        

    
    def CreateClickNotifyBox(self):
        (x, y) = self.m_PetAni.GetPos()
        lianyaoinfo = self.m_PetAni.GetLianyaoImgInfo()
        tunshiinfo = self.m_PetAni.GetTunshiImgInfo()
        if lianyaoinfo:
            (w, h, lianyao_x, lianyao_y) = lianyaoinfo
            self.m_LianyaoNotifyBox = self.CClickNotifyBox(self, w, h, 0, 0, 34)
            self.m_LianyaoNotifyBox.SetZ(100)
            self.m_LianyaoNotifyBox.SetPos(x + lianyao_x, y + lianyao_y)
        
        if tunshiinfo:
            (w, h, tunshi_x, tunshi_y) = tunshiinfo
            self.m_TunshiNotifyBox = self.CClickNotifyBox(self, w, h, 0, 0, 35)
            self.m_TunshiNotifyBox.SetZ(100)
            self.m_TunshiNotifyBox.SetPos(x + tunshi_x, y + tunshi_y)
        

    
    def ClearPhoto(self):
        if hasattr(self, 'm_PetAni') and self.m_PetAni:
            self.m_PetAni.ReleaseAll()
            self.m_PetAni = None
        
        if hasattr(self, 'm_BindNotifyBox') and self.m_BindNotifyBox:
            self.m_BindNotifyBox = None
        
        if hasattr(self, 'm_BirthNotifyBox') and self.m_BirthNotifyBox:
            self.m_BirthNotifyBox = None
        
        if hasattr(self, 'm_LianyaoNotifyBox') and self.m_LianyaoNotifyBox:
            self.m_LianyaoNotifyBox = None
        
        if hasattr(self, 'm_TunshiNotifyBox') and self.m_TunshiNotifyBox:
            self.m_TunshiNotifyBox = None
        

    
    def SelectPet(self, pid):
        import pet
        pobj = pet.GetPet(pid)
        if pobj:
            self.CreateDlgItem(pobj)
            _btns = ('btn_con_sub', 'btn_con_add', 'btn_str_sub', 'btn_str_add', 'btn_mag_sub', 'btn_mag_add', 'btn_cha_sub', 'btn_cha_add', 'btn_dex_sub', 'btn_dex_add')
            if pobj.m_Prop.m_Point > 0:
                for b in _btns:
                    self.GetObject(b).SetShow(True)
                
            else:
                for b in _btns:
                    self.GetObject(b).SetShow(False)
                
            import petdata
            carryGrade = petdata.GetData(pobj.m_Prop.m_Shape)['carry_grade']
            self.m_PetCarryGrade = combmacro.CTEXT((interface.CBlackShadowText, interface.CTextObject, interface.CTextObject, interface.CTextObject)[interface.STYLE], 'carry_limit', self, '%d' % carryGrade, interface.FontLT14_3, interface.COLOR_9, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
            if pet.GetActivatePet() == pobj:
                self.GetObject('btn_joinwar').SetText('\xa5\xf0 \xae\xa7')
            else:
                self.GetObject('btn_joinwar').SetText('\xb0\xd1 \xbe\xd4')
            if pet.IsLookon(pid):
                self.GetObject('btn_lookon').SetText('\xc1\xf4 \xc2\xc3')
            else:
                self.GetObject('btn_lookon').SetText('\xb8\xf2 \xc0H')
            self.m_SelPetID = pid
            self.ShowMergeText()
            self.RefreshLianHuaText()
            self.m_PetAni.CreateLianyaoTxt()
            self.m_PetAni.CreateTunshiTxt()
            self.CreateClickNotifyBox()
        

    
    def ShowSwitch(self):
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        pobj = None
        if sel:
            import pet
            pobj = pet.GetPet(sel.m_PID)
            self.OnShowPoints(sel.m_PID)
        
        if not self.GetShow() and pobj:
            pass
        elif sel:
            self.m_Points = [
                0] * 6
            self.m_BakPoints = [
                0] * 6
        
        flag = not self.GetShow()
        if flag and getattr(self, 'm_PetAni', None):
            self.m_PetAni.m_Photo.ReleaseMyTimer()
            self.m_PetAni.m_Photo.SetState('stand')
            self.m_PetAni.m_Photo.m_NowStateIdx = 0
        
        self.SetShow(flag)

    
    def AddAllPoints(self, idx):
        idx2attr = {
            7: 0,
            13: 1,
            14: 2,
            15: 3,
            16: 4 }
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if sel:
            import pet
            pobj = pet.GetPet(sel.m_PID)
            if pobj:
                if self.m_Points[5] + pobj.GetProp('m_Point') > 0 and self.m_Points[idx2attr[idx]] < 255:
                    if self.m_Points[idx2attr[idx]] + self.m_Points[5] + pobj.GetProp('m_Point') >= 255:
                        self.m_Points[5] -= 255 - self.m_Points[idx2attr[idx]]
                        self.m_Points[idx2attr[idx]] = 255
                    else:
                        self.m_Points[idx2attr[idx]] += self.m_Points[5] + pobj.GetProp('m_Point')
                        self.m_Points[5] = -1 * pobj.GetProp('m_Point')
                    self.OnShowPoints(sel.m_PID)
                    import copy
                    self.m_BakPoints = copy.deepcopy(self.m_Points)
                    self.GetObject('btn_tuijian').SetShow(False)
                    self.GetObject('btn_Sure').SetShow(True)
                
            
        

    
    def SubAllPoints(self, idx):
        idx2attr = {
            8: 0,
            23: 1,
            22: 2,
            20: 3,
            19: 4 }
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if sel:
            import pet
            pobj = pet.GetPet(sel.m_PID)
            if pobj:
                if self.m_Points[5] < 0 and self.m_Points[idx2attr[idx]] > 0:
                    self.m_Points[5] += self.m_Points[idx2attr[idx]]
                    self.m_Points[idx2attr[idx]] = 0
                    self.OnShowPoints(sel.m_PID)
                    import copy
                    self.m_BakPoints = copy.deepcopy(self.m_Points)
                    if self.m_Points == [
                        0,
                        0,
                        0,
                        0,
                        0,
                        0]:
                        point = pobj.GetProp('m_Point')
                        if pobj.m_Prop.m_Grade <= 60:
                            pass
                        self.GetObject('btn_tuijian').SetShow(point % 5 == 0)
                        self.GetObject('btn_Sure').SetShow(False)
                    else:
                        self.GetObject('btn_Sure').SetShow(True)
                
            
        

    
    def OpenAutoAssignDlg(self):
        import netpet
        itemObj = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if itemObj:
            netpet.C2SOpenAutoDlg(itemObj.m_PID)
        

    
    def CreateAutoAssign(self, pid, dataDict = None):
        if not dataDict and not getattr(self, 'm_AutoAssignDlg', None):
            return None
        
        self.m_AutoAssignDlg = CAutoAssignDlg(self)
        self.m_AutoAssignDlg.SetData(pid, dataDict)

    
    def IsAutoAssignShow(self):
        if hasattr(self, 'm_AutoAssignDlg') and self.m_AutoAssignDlg:
            return True
        
        return False

    
    def OnAutoAssignClose(self):
        self.m_AutoAssignDlg = None

    
    def OnPetSelect(self, idx):
        import pet
        import C_sys
        import key
        import netpet
        self.m_PointBox = None
        summonLst = self.GetObject('lst_summon')
        preItem = combmacro.GetSelectedItemFromList(summonLst)
        itemObj = summonLst.m_Items[idx]
        if preItem and preItem != itemObj:
            pObj = pet.GetPet(preItem.m_PID)
            if pObj:
                self.RemoveDlgItem(pObj)
            
        
        pObj = pet.GetPet(itemObj.m_PID)
        if pObj:
            if not itemObj.IsSelected():
                self.m_Points = [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0]
                self.m_BakPoints = [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0]
                self.SelectPet(itemObj.m_PID)
                if self.IsAutoAssignShow():
                    netpet.C2SOpenAutoDlg(itemObj.m_PID)
                
            
            if C_sys.IsKeyDown(key.VK_SHIFT) and self.GetShow():
                self.OnCopyPetInfo(pObj)
            
        

    
    def OnCopyPetInfo(self, petobj):
        import petdata
        import copylinkobj
        pID = petobj.m_ID
        shape = petobj.m_Prop.m_Shape
        data = petdata.GetData(shape)
        name = data.get('name', '')
        import kuafulink
        copylinkobj.CreateCopyLink(kuafulink.CLinkPet.CLIENT_TYPE, pID, shape, name)

    
    def ClearFightPoint(self):
        self.m_FightPoint = [
            0]
        self.m_FightPointID = None

    
    def SendPoint(self):
        import netpet
        if len(self.m_FightPoint) == 5 and max(self.m_FightPoint) > 0 and hasattr(self, 'm_FightPointID') and self.m_FightPointID:
            sumLstObj = self.GetObject('lst_summon')
            for itemObj in sumLstObj.m_Items:
                if itemObj.m_PID == self.m_FightPointID:
                    netpet.C2SAddPoint(self.m_FightPointID, self.m_FightPoint)
                    break
                    continue
            
        
        self.ClearFightPoint()
        self.m_BakPoints = [
            0,
            0,
            0,
            0,
            0,
            0]

    
    def OnCommitPoint(self):
        import mainmenu
        import usermacro
        import netpet
        total = 0
        for num in self.m_Points[:5]:
            total += num
        
        if total <= 0:
            return None
        
        selItem = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if selItem is None:
            return None
        
        netpet.C2SAddPoint(selItem.m_PID, self.m_Points[:5])
        self.ClearFightPoint()
        self.m_BakPoints = [
            0,
            0,
            0,
            0,
            0,
            0]

    
    def OnFreePet(self):
        import commondialog
        import pet
        import usermacro
        import petdata
        import chatoutput
        
        def sure(dlg):
            import netpet
            netpet.C2SSummonFree(dlg.m_PID)

        selItem = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if selItem:
            pObj = pet.GetPet(selItem.m_PID)
            if pObj:
                if pet.GetActivatePet() == pObj:
                    usermacro.PROMPT_MSG('\xb0\xd1\xbe\xd4\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xa5i\xa5H\xa9\xf1\xa5\xcd')
                    return None
                
                name = pObj.m_Prop.m_Name
                petData = petdata.GetData(pObj.GetProp('m_Shape'))
                if petData and petData['name'] != name:
                    txt = '\xa9\xf1\xa5\xcd\xabe\xbd\xd0\xa5\xfd\xa7\xe2\xa5l\xb3\xea\xc3~\xaa\xba\xa6W\xa6r\xa7\xef\xa6^\xa1u%s\xa1v' % petData['name']
                    usermacro.PROMPT_MSG(txt)
                    chatoutput.AddChat('#W%s#n' % txt)
                    return None
                
                (colorStr, lightStr) = style.GetStrTuple(self.GetDlgPath(), 'data_message_color')
                dlg = commondialog.ShowMessageBox('%s\xa9\xf1\xa5\xcd\xab\xe1\xa1A%s%s%s\xb1N\xa6^\xc2k\xa4j\xa6\xdb\xb5M\xa1A\xa7A\xbdT\xa9w\xa9\xf1\xa5\xcd\xb6\xdc\xa1H' % (colorStr, lightStr, name, colorStr), ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (sure, None), stopMove = False)
                dlg.m_PID = selItem.m_PID
            
        

    
    def OnSummonExp(self):
        import dlgminibuy
        import item
        import netcommon
        import pet
        import mainmenu
        if mainmenu.IsWar():
            import usermacro
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return None
        
        if not hasattr(self, 'm_SelPetID') and not (self.m_SelPetID) or not pet.GetPet(self.m_SelPetID):
            return None
        
        if hasattr(self, 'm_MiniExpBuy') and self.m_MiniExpBuy:
            self.m_MiniExpBuy.OnClose()
            return None
        
        amount = item.GetItemQuantity(25404)
        if amount == 0:
            self.m_MiniExpBuy = dlgminibuy.CSummonExpBuyDlg(self, 25404, '\xc3d\xaa\xab\xa7@\xbe\xd4\xa4\xdf\xb1o', 50000)
            self.m_MiniExpBuy.SetMaxMin(100, 0)
            self.m_MiniExpBuy.SetAmount(10)
        elif amount > 10:
            amount = 10
        
        netcommon.CS2UsePetXinde(self.m_SelPetID, amount)

    
    def OnMiniClose(self):
        self.m_MiniExpBuy = None

    
    def OnMiniBuy(self):
        import hero
        import dlgnpc
        import usermacro
        amount = self.m_MiniExpBuy.GetAmount()
        if amount <= 0:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xe9\xa4J\xc1\xca\xb6R\xbc\xc6\xb6q')
            return None
        
        
        def buy(msgid):
            if msgid == 1:
                import netcommon
                netcommon.C2SBuyItem(25404, amount)
            

        
        def commit(msgid):
            txt = None
            if msgid == 1:
                if hero.g_Prop.m_FightCash + hero.g_Prop.m_Cash < price:
                    txt = '\xa7A\xa8\xad\xa4W\xaa\xba\xa9\xe8\xa5\xce\xaa\xf7\xa9M\xb2{\xaa\xf7\xb3\xa3\xa4\xa3\xa8\xac\xa5H\xa7\xb9\xa6\xa8\xa5\xbb\xa6\xb8\xc1\xca\xb6R'
                elif hero.g_Prop.m_FightCash < price:
                    txt = '\xb7\xed\xabe\xa9\xe8\xa5\xce\xaa\xf7\xa4\xa3\xa8\xac\xa1A\xa4\xa3\xa8\xac\xb3\xa1\xa4\xc0\xacO\xa7_\xa8\xcf\xa5\xce\xb2{\xaa\xf7\xc1\xca\xb6R\xa1H\nQ\xbdT\xa9w'
                else:
                    buy(1)
            
            if txt:
                dlgnpc.ShowClientDlg(txt, '', buy)
            

        price = 50000 * amount
        txt = '\xbdT\xa9w\xaa\xe1\xb6O%d\xa9\xe8\xa5\xce\xaa\xf7\xc1\xca\xb6R%d\xa5\xbb\xc3d\xaa\xab\xa7@\xbe\xd4\xa4\xdf\xb1o\xb6\xdc\xa1H\nQ\xbdT\xa9w' % (price, amount)
        dlgnpc.ShowClientDlg(txt, '', commit)
        self.m_MiniExpBuy.ReleaseCallback()
        self.m_MiniExpBuy = None

    
    def OnListDoubleClick(self, idx):
        if CheckMutex():
            return None
        
        import C_sys
        summonLst = self.GetObject('lst_summon')
        curTime = C_sys.GetTime()
        if hasattr(self, 'm_LeftUpTime') and hasattr(self, 'm_CurIdx') and self.m_CurIdx == idx:
            if curTime - self.m_LeftUpTime < 5000:
                self.OnMessage(1)
            
        
        self.m_LeftUpTime = curTime
        self.m_CurIdx = idx

    
    def OnShowPet(self):
        import pet
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if not sel or self.BanShowPet():
            return None
        
        if pet.IsLookon(sel.m_PID):
            self.HidePet(True)
            pet.TakePet(sel.m_PID)
            self.m_OnLookPet = None
        elif self.m_OnLookPet:
            self.HidePet(True)
            pet.TakePet(self.m_OnLookPet)
        
        self.HidePet(False)
        pet.PutPet(sel.m_PID)
        self.m_OnLookPet = sel.m_PID

    
    def BanShowPet(self):
        import misc
        import new_maze
        import usermacro
        import mainmenu
        txt = None
        if misc.IsInKuafuServer():
            txt = '\xb7\xed\xabe\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xa6\xb9\xc3\xfe\xbe\xde\xa7@'
        elif new_maze.InNewHanghai():
            txt = '\xb7\xed\xabe\xac\xa1\xb0\xca\xb8T\xa4\xee\xa6\xb9\xc3\xfe\xbe\xde\xa7@'
        elif mainmenu.IsWar():
            txt = '\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0'
        
        if txt:
            usermacro.PROMPT_MSG(txt)
            return True
        

    
    def DoHidePet(self):
        import pet
        self.HidePet(True)
        pet.TakePet(self.m_PID)
        self.m_OnLookPet = None

    
    def OnCancelLianHua(self):
        import commondialog
        
        def Ok(dlg):
            obj = dlg.m_ShadowObj.Get()
            if obj:
                import netcommon
                if getattr(obj, 'm_SelPetID', None):
                    netcommon.C2SCancelLianHua(obj.m_SelPetID)
                
            

        dlg = commondialog.ShowMessageBox('\xbdT\xa9w\xadn\xa8\xfa\xae\xf8\xb7\xd2\xa4\xc6\xa5\xd3\xbd\xd0\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa7\xda\xc2I\xbf\xf9\xa4F'), (Ok, None))
        dlg.m_ShadowObj = interface.CShadowObject(self)

    
    def OnCancelHeavenTunshi(self):
        import commondialog
        import pet
        import netplayer
        if getattr(self, 'm_Tips', None):
            self.m_Tips = None
        
        
        def OK(dlg):
            obj = dlg.m_ShadowObj.Get()
            if obj:
                import netpet
                if getattr(obj, 'm_SelPetID', None):
                    netpet.C2SCancelHeavenTunshi(obj.m_SelPetID)
                
            

        if getattr(self, 'm_SelPetID', None):
            pid = self.m_SelPetID
            pobj = pet.GetPet(pid)
            if pobj:
                if getattr(pobj, 'm_Key', None) & 128 != 0:
                    netplayer.C2SPetUnLock([
                        pid])
                    return None
                else:
                    dlg = commondialog.ShowMessageBox('\xb1z\xb1N\xa8\xfa\xae\xf8\xb1M\xa6\xb3\xa5l\xb3\xea\xc3~\xb3Q\xa7]\xbe\xbd\xa5\xd3\xbd\xd0\xa1A\xbdT\xa9w\xa8\xfa\xae\xf8\xa5\xd3\xbd\xd0\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OK, None))
                    dlg.m_ShadowObj = interface.CShadowObject(self)
            
        

    
    def SetPetFight(self, iPetID):
        import netpet
        import mainmenu
        import pet
        LOG('[PET]dlgpet\xbe\xde\xa7@', iPetID, self.m_FightPetID)
        if mainmenu.IsRealWar():
            import usermacro
            if self.m_FightPetID and self.m_FightPetID == iPetID:
                usermacro.PROMPT_MSG('\xbe\xde\xa7@\xa4w\xa8\xfa\xae\xf8')
                self.m_FightPetID = 0
                return None
            
            self.m_FightPetID = iPetID
            oActivatePet = pet.GetActivatePet()
            if oActivatePet and oActivatePet.m_ID == iPetID:
                usermacro.PROMPT_MSG('\xc3d\xaa\xab\xa5\xf0\xae\xa7\xa6\xa8\xa5\\\xa1A\xbe\xd4\xb0\xab\xb5\xb2\xa7\xf4\xab\xe1\xa5\xcd\xae\xc4\xa1A\xa6A\xa6\xb8\xc2I\xc0\xbb\xa5i\xa8\xfa\xae\xf8\xbe\xde\xa7@')
            else:
                usermacro.PROMPT_MSG('\xc3d\xaa\xab\xb0\xd1\xbe\xd4\xa6\xa8\xa5\\\xa1A\xbe\xd4\xb0\xab\xb5\xb2\xa7\xf4\xab\xe1\xa5\xcd\xae\xc4\xa1A\xa6A\xa6\xb8\xc2I\xc0\xbb\xa5i\xa8\xfa\xae\xf8\xbe\xde\xa7@')
            return None
        
        netpet.C2SSetFight(iPetID)

    
    def OnSceneChange(self, *args):
        import pet
        if self.m_FightPetID:
            pobj = pet.GetPet(self.m_FightPetID)
            if pobj:
                self.SetPetFight(self.m_FightPetID)
                LOG('[PET]\xbe\xd4\xb0\xab\xb5\xb2\xa7\xf4\xa1A\xa8t\xb2\xce\xa6\xdb\xb0\xca\xa4\xc1\xb4\xab', self.m_FightPetID)
            
        
        self.m_FightPetID = 0

    
    def OnMessage(self, msgid):
        import nettask
        nettask.CloseTaskTips(4, msgid)
        if msgid == 2:
            self.m_RenameDlg = None
            self.SetShow(False)
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                self.m_Points = [
                    0] * 6
                self.OnShowPoints(sel.m_PID)
                self.m_BakPoints = [
                    0] * 6
            
        elif msgid == 1:
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                import main
                import pet
                pobj = pet.GetPet(sel.m_PID)
                if pobj and pobj.m_Key & 64 == 0:
                    
                    def _Sure(box):
                        self.SetPetFight(box.m_PID)

                    import petdata
                    carryGrade = petdata.GetData(pobj.m_Prop.m_Shape)['carry_grade']
                    if carryGrade <= 65:
                        txt = '\xbf\xef\xbe\xdc\xb0\xd1\xbe\xd4\xab\xe1\xa1A\xa5l\xb3\xea\xc3~\xb1N\xbbP\xa7A\xb8j\xa9w\xa1A\xa4\xa3\xaf\xe0\xa6A\xb6i\xa6\xe6\xa5\xe6\xa9\xf6\xa1B\xa5X\xb0\xe2\xaa\xba\xbe\xde\xa7@\xa1A\xa7A\xbdT\xa9w\xb0\xd1\xbe\xd4\xb6\xdc\xa1H'
                    else:
                        txt = '\xbf\xef\xbe\xdc\xb0\xd1\xbe\xd4\xab\xe1\xa1A\xa5l\xb3\xea\xc3~\xb1N\xbbP\xa7A\xb8j\xa9w\xa1A\xa4\xa3\xaf\xe0\xa6A\xa5\xe6\xa9\xf6\xa1B\xa5X\xb0\xe2\xb5\xb9\xa5L\xa4H\xa1A\xa7A\xbdT\xa9w\xb0\xd1\xbe\xd4\xb6\xdc\xa1H'
                    import commondialog
                    dlg = commondialog.ShowMessageBox(txt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (_Sure, None))
                    dlg.m_PID = sel.m_PID
                elif pobj:
                    self.SetPetFight(sel.m_PID)
                
            
        elif msgid == 4:
            if self.IsAutoAssignShow():
                self.OnAutoAssignClose()
            else:
                self.OpenAutoAssignDlg()
        elif msgid == 9:
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            import dlgpetitem
            if sel:
                dlgpetitem.ShowSwitch(sel.m_PID)
            else:
                dlgpetitem.ShowSwitch()
        elif msgid == 10:
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                if hasattr(self, 'm_RenameDlg') and self.m_RenameDlg and self.m_RenameDlg.GetShow():
                    self.m_RenameDlg.CloseWindow()
                else:
                    self.m_RenameDlg = CRenameNewDialog(self, sel.m_PID, 100, 200)
            
        elif msgid == 11:
            self.OnFreePet()
        elif msgid == 12:
            self.OnShowPet()
        elif msgid == 6:
            self.m_PetcDialog.ShowSwitch()
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            self.OnPetSelect(msgid - 101)
            self.OnListDoubleClick(msgid - 101)
        elif msgid in (7, 13, 14, 15, 16):
            _id2attr = {
                7: 0,
                13: 1,
                14: 2,
                15: 3,
                16: 4 }
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                import pet
                pobj = pet.GetPet(sel.m_PID)
                if pobj:
                    if self.m_Points[5] + pobj.GetProp('m_Point') > 0 and self.m_Points[_id2attr[msgid]] < 255:
                        self.m_Points[_id2attr[msgid]] += 1
                        self.m_Points[5] -= 1
                        self.OnShowPoints(sel.m_PID)
                        import copy
                        self.m_BakPoints = copy.deepcopy(self.m_Points)
                        self.GetObject('btn_tuijian').SetShow(False)
                        self.GetObject('btn_Sure').SetShow(True)
                    
                
            
        elif msgid in (8, 23, 22, 20, 19):
            _id2attr = {
                8: 0,
                23: 1,
                22: 2,
                20: 3,
                19: 4 }
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                import pet
                pobj = pet.GetPet(sel.m_PID)
                if pobj:
                    if self.m_Points[5] < 0 and self.m_Points[_id2attr[msgid]] > 0:
                        self.m_Points[_id2attr[msgid]] -= 1
                        self.m_Points[5] += 1
                        self.OnShowPoints(sel.m_PID)
                        import copy
                        self.m_BakPoints = copy.deepcopy(self.m_Points)
                        if self.m_Points == [
                            0,
                            0,
                            0,
                            0,
                            0,
                            0]:
                            point = pobj.GetProp('m_Point')
                            if pobj.m_Prop.m_Grade <= 60:
                                pass
                            self.GetObject('btn_tuijian').SetShow(point % 5 == 0)
                            self.GetObject('btn_Sure').SetShow(False)
                        else:
                            self.GetObject('btn_Sure').SetShow(True)
                            self.GetObject('btn_tuijian').SetShow(False)
                    
                
            
        elif msgid == 5:
            self.OnCommitPoint()
        elif msgid == 17:
            self.m_PointBox = None
            self.TuiJianPoints()
        elif msgid == 25:
            self.OnSummonExp()
        elif msgid == 32:
            self.OnCancelHeavenTunshi()
        elif msgid == 33:
            self.OnCancelLianHua()
        elif msgid == 34:
            import netpet
            netpet.C2SCancelLianyao(self.m_SelPetID)
        elif msgid == 35:
            import netpet
            netpet.C2SCancelTunshi(self.m_SelPetID)
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE + 50:
            idx = msgid - interface.RIGHT_BUTTON_MESSAGE
            if idx in (7, 13, 14, 15, 16):
                self.AddAllPoints(idx)
            elif idx in (8, 23, 22, 20, 19):
                self.SubAllPoints(idx)
            
        

    
    def TuiJianPoints(self):
        self.m_Points = [
            0,
            0,
            0,
            0,
            0,
            0]
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if sel:
            import pet
            pobj = pet.GetPet(sel.m_PID)
            if pobj:
                if pobj.m_Prop.m_Shape in self.FourLiShape:
                    self.m_Points[1] = (pobj.m_Prop.m_Point / 5) * 4
                    self.m_Points[0] = pobj.m_Prop.m_Point / 5
                elif pobj.m_Prop.m_Shape in self.FourMoShape:
                    self.m_Points[2] = (pobj.m_Prop.m_Point / 5) * 4
                    self.m_Points[0] = pobj.m_Prop.m_Point / 5
                elif pobj.m_Prop.m_Shape in self.FiveMei:
                    self.m_Points[3] = (pobj.m_Prop.m_Point / 5) * 5
                elif pobj.m_Prop.Ability_Attack >= pobj.m_Prop.Ability_Magic:
                    self.m_Points[1] = (pobj.m_Prop.m_Point / 5) * 4
                    self.m_Points[0] = pobj.m_Prop.m_Point / 5
                else:
                    self.m_Points[2] = (pobj.m_Prop.m_Point / 5) * 4
                    self.m_Points[0] = pobj.m_Prop.m_Point / 5
                self.m_Points[5] = pobj.m_Prop.m_Point % 5 - pobj.m_Prop.m_Point
            
            self.OnShowPoints(sel.m_PID)
            import copy
            self.m_BakPoints = copy.deepcopy(self.m_Points)
            self.GetObject('btn_tuijian').SetShow(False)
            self.GetObject('btn_Sure').SetShow(True)
        



def SetMutex():
    global g_Mutex
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        dlgpcattr.SetMutex()
    else:
        g_Mutex = True


def RefreshMutex():
    global g_Mutex
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        dlgpcattr.RefreshMutex()
    else:
        g_Mutex = False


def CheckMutex():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        return dlgpcattr.CheckMutex()
    else:
        return g_Mutex


def ShowPetDialog():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.ShowPetAttrDialog()
    elif g_PetDialog and g_PetDialog.GetShow():
        g_PetDialog.Topmost()
    else:
        ShowSwitch()


def ShowSwitch():
    global g_PetDialog
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.ShowSwitchPetAttrDlg()
    elif g_PetDialog:
        g_PetDialog.ShowSwitch()
        g_PetDialog.Topmost()
    else:
        g_PetDialog = CPetDialog()
        g_PetDialog.Topmost()
    (x, y) = g_PetDialog.GetPos()
    if x < -300:
        g_PetDialog.SetPos(-250, y)
    


def ShowAutoAssign(pid, dataDict = None):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.ShowPetAttrDlgAutoAssign(pid, dataDict)
    elif g_PetDialog:
        g_PetDialog.CreateAutoAssign(pid, dataDict)
    


def AddPet():
    '''
\t\xa9\xb9\xac\xc9\xad\xb1\xa4\xa4\xa5[\xa4J\xa4@\xad\xd3\xc3d\xaa\xab\xa1A\xb9\xea\xbb\xda\xa4W\xb4N\xacO\xb1qpet.py\xa4\xa4\xa8\xfa\xb1\xc6\xa7\xc7\xa6n\xa4F\xaa\xba\xa6C\xaa\xed\xa1A\xa8\xea\xa4@\xb9M\xac\xc9\xad\xb1
\t:return:
\t'''
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.PetAttrAddPet()
    elif g_PetDialog:
        selID = g_PetDialog.GetSelectPetID()
        g_PetDialog.RefreshPets(selID)
        g_PetDialog.ShowSummonNum()
    
    CheckSameID()


def CheckSameID():
    import pet
    oAllPetList = pet.GetSortChildAndPets()
    iIDList = []
    for oPet in oAllPetList:
        iPetID = oPet.GetID()
        if iPetID in iIDList:
            LOG_ERR('\xc3d\xaa\xab\xa4l\xa4k\xa6s\xa6b\xac\xdb\xa6PID')
            break
        
        iIDList.append(iPetID)
    


def RemovePet(pet):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.RemovePet(pet)
    elif pet and g_PetDialog:
        g_PetDialog.RemovePet(pet)
        g_PetDialog.ShowSummonNum()
    


def UpdatePet(pet, petid = None):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.UpdatePet(pet, petid)
    elif pet and g_PetDialog:
        g_PetDialog.RefreshPets(petid)
        g_PetDialog.UpdatePet(pet)
    


def SelectPet(petid):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.SelectPet(petid)
    else:
        ShowSwitch()
        g_PetDialog.SetShow(True)
        g_PetDialog.Topmost()
        lst_summon = g_PetDialog.GetObject('lst_summon')
        for item in lst_summon.m_Items:
            if item.m_PID == petid:
                SetMutex()
                item.LeftUp()
                RefreshMutex()
                continue
        


def RefreshJieBangTips(iCash, iTime):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.RefreshJieBangTips(iCash, iTime)
    elif g_PetDialog and g_PetDialog.GetShow():
        g_PetDialog.RefreshJieBangTips(iCash, iTime)
    


def GetBindTips(key, petid = 0):
    txt = None
    if key is not None:
        if key & 32 != 0:
            import netcommon
            netcommon.C2SGetPetJieBangTips(petid)
            return None
        elif key & 64 != 0:
            txt = '\xb8j\xa9w\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xa5\xce\xa9\xf3\xa5\xe6\xa9\xf6\xa1B\xa5X\xb0\xe2#r\xa9M\xa5\xe6\xa5I\xa5\xf4\xb0\xc8,\xb8j\xa9w\xa5i\xb8\xd1\xb0\xa3'
            if key & 8 != 0:
                txt = '\xb1M\xa6\xb3\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xa5\xce\xa9\xf3\xa5\xe6\xa9\xf6\xa1B\xa5X\xb0\xe2\xa9M\xa5\xe6\xa5I\xa5\xf4\xb0\xc8#r\xb1M\xa6\xb3\xb7|\xb4\xa3\xb0\xaa\xa6U\xb6\xb5\xb8\xea\xbd\xe8\xa5B\xb5L\xaak\xb8\xd1\xb0\xa3'
            
        
    
    return txt


def GetBirthTips(key):
    txt = None
    if key is not None:
        newkey = (key & 65280) >> 8
        import pet
        if newkey & pet.MARK_ISXIANPET != 0:
            txt = '\xac\xc3\xb5}\xa5l\xb3\xea\xc3~\xa1A\xa4\xd1\xa5\xcd\xa7\xde\xaf\xe0\xc0u\xa8q\xa1B\xa5\xc3\xa5\xcd#r\xa5i\xb3q\xb9L\xb6i\xad\xd7\xb4\xa3\xa4\xc9\xb8\xea\xbd\xe8'
        elif newkey & pet.MARK_ISHOLYPET != 0:
            txt = '\xac\xc3\xb5}\xa5l\xb3\xea\xc3~\xa1A\xa4\xd1\xa5\xcd\xa7\xde\xaf\xe0\xc0u\xa8q\xa1B\xa5\xc3\xa5\xcd#r\xa5i\xb3q\xb9L\xb6i\xad\xd7\xb4\xa3\xa4\xc9\xb8\xea\xbd\xe8'
        elif newkey & pet.MARK_ISXIYOUPET != 0:
            txt = '\xb5}\xa6\xb3\xaa\xba\xa5l\xb3\xea\xc3~\xa1A\xa5i\xb3q\xb9L\xb6i\xad\xd7\xb4\xa3\xb0\xaa\xb8\xea\xbd\xe8'
        elif newkey & pet.MARK_ISCOLOR != 0:
            txt = '\xc5\xdc\xb2\xa7\xaa\xba\xa5l\xb3\xea\xc3~\xc4_\xc4_\xa1A\xbe\xd6\xa6\xb3\xa7\xf3\xac\xb0\xb1j#r\xa4j\xaa\xba\xb8\xea\xbd\xe8\xbc\xe7\xa4O'
        elif newkey & pet.MARK_ISBAOBAO != 0:
            txt = '\xa5l\xb3\xea\xc3~\xc4_\xc4_\xa1A\xaa\xec\xa9l\xac\xb00\xaf\xc5\xa1A\xbe\xd6\xa6\xb3\xaa\xba#r\xc4\xdd\xa9\xca\xc2I\xa6h\xa9\xf3\xb3\xa5\xa5\xcd\xa5l\xb3\xea\xc3~'
        
    
    return txt


def GetLianyaoTips(iTime):
    import misc
    dTime = iTime - misc.GetServerCurrentTime()
    txt = None
    if iTime == 0:
        return None
    elif dTime > 0:
        txt = '#Y%d\xa4p\xae\xc9#n\xab\xe1\xa5i\xb6i\xa6\xe6\xb7\xd2\xa4\xc6#r\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xaa\xac\xbaA' % dTime / 3600
    elif dTime <= 0:
        txt = '\xa5i\xb6i\xa6\xe6\xb7\xd2\xa4\xc6#r\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xaa\xac\xbaA'
    
    return txt


def GetTunshiTips(iTime):
    import misc
    dTime = iTime - misc.GetServerCurrentTime()
    txt = None
    if iTime == 0:
        return None
    elif dTime > 0:
        if dTime < 3600:
            txt = '#Y%d\xa4\xc0\xc4\xc1#n\xab\xe1\xa5i\xb6i\xa6\xe6\xb6\xc7\xa9\xd3\xb3Q\xa7]\xbe\xbd#r\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xaa\xac\xbaA' % dTime / 60
        else:
            txt = '#Y%d\xa4p\xae\xc9#n\xab\xe1\xa5i\xb6i\xa6\xe6\xb6\xc7\xa9\xd3\xb3Q\xa7]\xbe\xbd#r\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xaa\xac\xbaA' % dTime / 3600
    elif dTime <= 0:
        txt = '\xa5i\xb6i\xa6\xe6\xb6\xc7\xa9\xd3\xb3Q\xa7]\xbe\xbd#r\xc2I\xc0\xbb\xa8\xfa\xae\xf8\xaa\xac\xbaA'
    
    return txt


def AddPetState(petID, iTime, lianhuaTime):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        dlgpcattr.AddPetState(petID, iTime, lianhuaTime)
    else:
        g_MergePetsInfo[petID] = iTime
        if lianhuaTime == -1:
            if petID in g_LianHuaTime:
                del g_LianHuaTime[petID]
            
        else:
            g_LianHuaTime[petID] = lianhuaTime
        StartAutoTimer()


def DoRefreshPetState():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.DoRefreshPetState()
    elif g_PetDialog and g_PetDialog.GetShow():
        g_PetDialog.ShowMergeText()
        g_PetDialog.RefreshLianHuaText()
        g_PetDialog.CreateClickNotifyBox()
        if getattr(g_PetDialog, 'm_PetAni'):
            g_PetDialog.m_PetAni.CreateLianyaoTxt()
            g_PetDialog.m_PetAni.CreateTunshiTxt()
        
    


def RefreshPetState(obj):
    SetMergePetType()
    DoRefreshPetState()
    return ()


def SetMergePetType():
    global g_RestTimeInfo
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        dlgpcattr.SetMergePetType()
    else:
        g_RestTimeInfo = { }
        if not g_MergePetsInfo:
            return None
        
        for petid, resttime in g_MergePetsInfo.items():
            if resttime == 0xFFFFFFFFL:
                g_MergePetsInfo.pop(petid)
                g_RestTimeInfo.pop(petid)
                continue
            if resttime == 0:
                g_RestTimeInfo[petid] = 2
                continue
            if resttime > 0:
                resttime -= 1
                g_MergePetsInfo[petid] = resttime
                g_RestTimeInfo[petid] = 1
                continue
        


def StartAutoTimer():
    global g_AutoObject, g_AutoTimer
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcattr
        dlgpcattr.StartAutoTimer()
    elif not g_AutoObject:
        g_AutoObject = interface.CBaseObject(None)
    
    if not g_AutoTimer:
        g_AutoTimer = g_AutoObject.CreatePyCommand(30, RefreshPetState)
    


def RefreshPetKey(pID):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.RefreshPetKey(pID)
    elif g_PetDialog and g_PetDialog.GetSelectPetID() == pID:
        g_PetDialog.SelectPet(pID)
