# pycdc 交叉复核产物 · script.fls entry 4433
# co_filename(原始)='script/dialog/dlgchildinfo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4433.pyc (Python 2.5)

import interface
import item
import combdialog
import combmacro
TYPE2CLASS = {
    1: '\xbcC\xb3N',
    2: '\xa4M\xaak',
    3: '\xbaj\xaak',
    4: '\xae\xb1\xaak',
    5: '\xb5\xa7\xaak',
    6: '\xbe\xa7\xbe\xc7',
    7: '\xb9D\xb3N',
    8: '\xa6\xf2\xbe\xc7',
    9: '\xb3\xb1\xb6\xa7',
    10: '\xa7\xc5\xb3N',
    11: '\xb7t\xbe\xb9',
    14: '\xb0\xad\xa8\xa6' }
POSITION = {
    'desc': None,
    'grade': ('txt_info', 0, 1),
    'hp': ('txt_info', 0, 2),
    'mp': ('txt_info', 0, 3),
    'fp': ('txt_info', 0, 4),
    'genre': ('txt_prop', 0, 0),
    'damage': ('txt_prop', 0, 1),
    'defense': ('txt_prop', 0, 2),
    'speed': ('txt_prop', 0, 3),
    'magDef': ('txt_prop', 0, 4),
    'str': ('txt_point', 0, 1),
    'con': ('txt_point', 0, 0),
    'mag': ('txt_point', 0, 2),
    'cha': ('txt_point', 0, 3),
    'dex': ('txt_point', 0, 4),
    'abilityAt': ('txt_apti', 0, 0),
    'abilityDf': ('txt_apti', 0, 1),
    'abilityCn': ('txt_apti', 0, 2),
    'abilityMg': ('txt_apti', 0, 3),
    'abilitySp': ('txt_apti', 0, 4) }
g_SummonInfos = { }
g_SInfoDialog = None
g_SummonExt = { }
g_ItemInfos = [
    { },
    { },
    { },
    { },
    { },
    { },
    { },
    { }]
g_ItemInfoTips = [
    [
        None,
        None],
    None,
    None,
    None,
    None,
    None,
    None,
    None]
g_SkillTip = None

def ModuleReset():
    global g_SummonInfos, g_SInfoDialog, g_SummonExt, g_ItemInfos, g_ItemInfoTips, g_SkillTip
    g_SummonInfos = { }
    g_SInfoDialog = None
    g_SummonExt = { }
    g_ItemInfos = [
        { },
        { },
        { },
        { },
        { },
        { },
        { },
        { }]
    g_ItemInfoTips = [
        [
            None,
            None],
        None,
        None,
        None,
        None,
        None,
        None,
        None]
    g_SkillTip = None


class CChildInfoDialog(combdialog.CCombDialog):
    
    def __init__(self, parent, x, y, pid, shape, name):
        combdialog.CCombDialog.__init__(self, parent, 'dialog/child/childsinfo.dlg')
        self.SetPos(x, y)
        self.m_DlgHelpID = 5519
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
        self.m_PID = pid
        self.m_Shape = shape
        nameColor = interface.COLOR_295
        nameClass = None if interface.IsNewStyle() else interface.CShadowText
        self.m_Name = combmacro.CIFTEXT(nameClass, 'txt_info', self, 0, 0, name, interface.FontLT14_3, nameColor)
        self.UpdatePhoto(shape, 0)
        self.m_Infos = None
        self.m_Items = []
        self.m_MagLines = []
        self.m_PhyLines = []

    
    def UpdateInfo(self, pid, sinfo):
        import newchilddefine
        import newchild
        if pid != self.m_PID:
            return None
        
        self.m_Infos = sinfo
        txtclass = self.GetTextCls()
        itemColor = interface.COLOR_295
        itemClass = None if interface.IsNewStyle() else interface.CShadowText
        for idx in POSITION.keys():
            v = POSITION[idx]
            if v is not None and sinfo[idx] is not None:
                (cname, x, y) = v
                txt = str(sinfo[idx])
                if idx == 'genre':
                    txt = TYPE2CLASS[sinfo[idx]]
                
                if cname == 'txt_apti':
                    color = newchilddefine.GetChildZZColor(int(txt))
                    itemobj = combmacro.CIFTEXT(txtclass, cname, self, x, y, txt, interface.FontLT14_3, color)
                else:
                    itemobj = combmacro.CIFTEXT(itemClass, cname, self, x, y, txt, interface.FontLT14_3, itemColor)
                self.m_Items.append(itemobj)
                continue
        
        lifeColor = interface.COLOR_295
        self.m_Items.append(combmacro.CIFTEXT(txtclass, 'txt_apti', self, 0, 5, '\xa5\xc3\xa5\xcd', interface.FontLT14_3, lifeColor))
        if interface.IsStyle1() or interface.IsStyle2():
            self.m_Items.append(combmacro.CIFTEXT(txtclass, 'txt_apti', self, 0, 6, str(sinfo['score']), interface.FontLT14_3, lifeColor))
        else:
            self.m_Items.append(combmacro.CIFTEXT(txtclass, 'txt_info', self, 0, 5, str(sinfo['score']), interface.FontLT14_3, lifeColor))
        self.DrawPhyResist([
            sinfo['resistLidi'],
            sinfo['resistLingqiao'],
            sinfo['resistQungong'],
            sinfo['resistPutong']])
        self.DrawMagResist([
            sinfo['resistXian'],
            sinfo['resistGui'],
            sinfo['resistYao'],
            sinfo['resistZhi'],
            sinfo['resistNian']])
        import dlgpet
        import copy
        import dlgpetbase
        box_skills = self.GetObject('box_skills')
        hfskill = copy.deepcopy(GetSummonExt(pid, 'm_HfSkillList'))
        (bx, by) = box_skills.GetPos()
        for idx, sk in enumerate(sinfo['skill']):
            (x, y) = box_skills.m_Imagess[idx].GetPos()
            if hfskill:
                iState = dlgpetbase.GetSkillState(sk, sinfo['skill'] + hfskill)
            else:
                iState = dlgpetbase.GetSkillState(sk, sinfo['skill'])
            si = dlgpet.CSkillIcon(self, bx + x + 3, by + y + 3, sk, False, iState = iState)
            if iState > 0:
                si.SetGrey()
            
            self.m_Items.append(si)
        
        self.UpdatePhoto(self.m_Shape, sinfo['desc'])

    
    def GetTextCls(self):
        if interface.IsStyle1():
            return interface.CBlackShadowText
        elif interface.IsStyle2():
            return interface.COverstrikingTextObject
        else:
            return interface.CTextObject

    
    def UpdateExt(self, pid):
        if pid != self.m_PID:
            return None
        
        import dlgpet
        import copy
        import dlgpetbase
        hfskill = copy.deepcopy(GetSummonExt(pid, 'm_HfSkillList'))
        pillskills = copy.deepcopy(self.m_Infos['skill'])
        box_skills = self.GetObject('box_skills')
        (bx, by) = box_skills.GetPos()
        if hfskill:
            for idx, sk in enumerate(hfskill):
                (x, y) = box_skills.m_Imagess[len(self.m_Infos['skill']) + idx].GetPos()
                if pillskills:
                    iState = dlgpetbase.GetSkillState(sk, hfskill + pillskills)
                else:
                    iState = dlgpetbase.GetSkillState(sk, hfskill)
                si = dlgpet.CSkillIcon(self, bx + x + 3, by + y + 3, sk, False, iState = iState)
                si.SetTag(True)
                if iState > 0:
                    si.SetGrey()
                
                self.m_Items.append(si)
            
        
        self.AddPillSkillIcon(pid, len(self.m_Infos['skill']) + len(hfskill))

    
    def AddPillSkillIcon(self, pid, iLen):
        import dlgchild
        import copy
        import dlgpet
        import newchild
        box_skills = self.GetObject('box_skills')
        (bx, by) = box_skills.GetPos()
        pillskills = copy.deepcopy(GetSummonExt(pid, 'm_PillSkills'))
        if pillskills:
            for idx, info in enumerate(pillskills):
                (skillID, value) = info
                (x, y) = box_skills.m_Imagess[iLen].GetPos()
                iLen += 1
                skillIcon = dlgchild.CSkillIcon(self, bx + x + 3, by + y + 3, skillID)
                skillIcon.SetPillValue(value)
                self.m_Items.append(skillIcon)
            
        
        for idx, sk in enumerate(self.m_Infos.get('iTalentList')):
            (x, y) = box_skills.m_Imagess[idx + iLen].GetPos()
            si = dlgpet.CSkillIcon(self, bx + x + 3, by + y + 3, sk, False)
            si.ShowTalentFlag(True)
            si.SetTempTalentInfo(newchild.GetTempTalentInfo(pid, sk))
            self.m_Items.append(si)
        

    
    def OnEnter(self, msgid):
        import wrapinterface
        if self.m_Infos:
            msg = ''
            if msgid == 1:
                _txts = ('\xa5P\xb3N\xa7\xdc\xa9\xca\xa1G', '\xb0\xad\xb3N\xa7\xdc\xa9\xca\xa1G', '\xa7\xaf\xb3N\xa7\xdc\xa9\xca\xa1G', '\xb4\xbc\xb3N\xa7\xdc\xa9\xca\xa1G', '\xa9\xc0\xb3N\xa7\xdc\xa9\xca\xa1G')
                _props = [
                    'resistXian',
                    'resistGui',
                    'resistYao',
                    'resistZhi',
                    'resistNian']
                for idx, v in enumerate(_props):
                    if idx > 0:
                        msg += '#r'
                    
                    msg += _txts[idx] + str(self.m_Infos[v])
                
                self.m_Tips = wrapinterface.CTextTips(self, -1, msg, interface.FontLT14_3, direct = 2, owner = self.m_MagBox)
            else:
                _txts = ('\xa4O\xbc\xc4\xa7\xdc\xa9\xca\xa1G', '\xc6F\xa5\xa9\xa7\xdc\xa9\xca\xa1G', '\xb8s\xa7\xf0\xa7\xdc\xa9\xca\xa1G', '\xb4\xb6\xb3q\xa7\xdc\xa9\xca\xa1G')
                _props = [
                    'resistLidi',
                    'resistLingqiao',
                    'resistQungong',
                    'resistPutong']
                for idx, v in enumerate(_props):
                    if idx > 0:
                        msg += '#r'
                    
                    msg += _txts[idx] + str(self.m_Infos[v])
                
                self.m_Tips = wrapinterface.CTextTips(self, -1, msg, interface.FontLT14_3, direct = 2, owner = self.m_PhyBox)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def DrawMagResist(self, props):
        self.MagResist = props
        import dlgpet
        self.m_MagLines = []
        _objs = ('loc_xian', 'loc_gui', 'loc_yao', 'loc_zhi', 'loc_nian')
        loc_origin = self.GetObject('loc_origin')
        (ox, oy) = loc_origin.GetPos()
        first = None
        prev = None
        for idx, s in enumerate(_objs):
            loc = self.GetObject(s)
            (lx, ly) = loc.GetPos()
            (x, y) = dlgpet.getmagp(ox, oy, lx, ly, props[idx])
            if prev:
                self.m_MagLines.append(interface.CLine(self, prev[0], prev[1], x, y, 16711680))
            
            if first is None:
                first = (x, y)
            
            prev = (x, y)
        
        self.m_MagLines.append(interface.CLine(self, prev[0], prev[1], first[0], first[1], 16711680))

    
    def DrawPhyResist(self, props):
        self.PhyResist = props
        import dlgpet
        self.m_PhyLines = []
        box_phy = self.GetObject('box_phy')
        (x, y) = box_phy.GetPos()
        (w, h) = box_phy.GetSize()
        w -= 2
        h -= 2
        pt = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
        ox = x + w / 2
        oy = y + h / 2
        first = None
        prev = None
        for idx, p in enumerate(pt):
            (lx, ly) = p
            (x, y) = dlgpet.getphyp(ox, oy, lx, ly, props[idx])
            if prev:
                self.m_PhyLines.append(interface.CLine(self, prev[0], prev[1], x, y, 16711680))
            
            if first is None:
                first = (x, y)
            
            prev = (x, y)
        
        self.m_PhyLines.append(interface.CLine(self, prev[0], prev[1], first[0], first[1], 16711680))

    
    def UpdatePhoto(self, shape, desc):
        import wrapinterface
        print 'UpdatePhoto'
        if hasattr(self, 'm_PetAni') and self.m_PetAni:
            self.m_PetAni.ReleaseAll()
        
        self.m_PetAni = wrapinterface.CPetAni(self, shape, desc, 0)
        box_icon = self.GetObject('box_icon')
        (x, y) = box_icon.GetPos()
        self.m_PetAni.SetPos(x + 7, y + 5)

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.SetShow(False)
        



def UpdateSummonAdvProp(pid):
    if g_SInfoDialog and g_SInfoDialog.m_PID == pid:
        import pet
        UpdateClientSummonInfo(pet.GetPet(pid))
    


def UpdateClientSummonInfo(pobj):
    sinfo = {
        'time': 0,
        'desc': pobj.m_Prop.m_Desc,
        'grade': pobj.m_Prop.m_Grade,
        'genre': pobj.m_Prop.m_Genre,
        'hpMax': pobj.m_Prop.m_HPMax,
        'mpMax': pobj.m_Prop.m_MPMax,
        'fpMax': pobj.m_Prop.m_FPMax,
        'damage': pobj.m_Prop.m_Damage,
        'defense': pobj.m_Prop.m_Defense,
        'speed': pobj.m_Prop.m_Speed,
        'magDef': pobj.m_Prop.m_Magdef,
        'str': pobj.m_Prop.m_Str,
        'con': pobj.m_Prop.m_Con,
        'mag': pobj.m_Prop.m_Mag,
        'cha': pobj.m_Prop.m_Cha,
        'dex': pobj.m_Prop.m_Dex,
        'point': pobj.m_Prop.m_Point,
        'life': pobj.m_Prop.m_Life,
        'abilityAt': pobj.m_Prop.Ability_Attack,
        'abilityDf': pobj.m_Prop.Ability_Defense,
        'abilityCn': pobj.m_Prop.Ability_Con,
        'abilityMg': pobj.m_Prop.Ability_Magic,
        'abilitySp': pobj.m_Prop.Ability_Speed,
        'resistLidi': pobj.m_Prop.Resist_Lidi,
        'resistLingqiao': pobj.m_Prop.Resist_Lingqiao,
        'resistQungong': pobj.m_Prop.Resist_Qungong,
        'resistPutong': pobj.m_Prop.Resist_Putong,
        'resistXian': pobj.m_Prop.Resist_Xian,
        'resistGui': pobj.m_Prop.Resist_Gui,
        'resistYao': pobj.m_Prop.Resist_Yao,
        'resistZhi': pobj.m_Prop.Resist_Zhi,
        'resistNian': pobj.m_Prop.Resist_Nian,
        'skill': pobj.m_Skills,
        'hp': pobj.m_Prop.m_HP,
        'mp': pobj.m_Prop.m_MP,
        'fp': pobj.m_Prop.m_FP }
    g_SInfoDialog.UpdateInfo(pobj.m_ID, sinfo)


def UpdateServerSummonInfo(pid, info):
    g_SummonInfos[pid] = info
    g_SInfoDialog.UpdateInfo(pid, info)


def AddSummonExt(petid, attr_name, value):
    if petid not in g_SummonExt:
        g_SummonExt[petid] = { }
    
    g_SummonExt[petid][attr_name] = value
    if g_SInfoDialog:
        g_SInfoDialog.UpdateExt(petid)
    


def GetSummonExt(petid, attr_name):
    
    try:
        return g_SummonExt[petid][attr_name]
    except:
        return None



def NewSummonInfo():
    import misc
    return [
        misc.Time(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        [],
        None,
        None,
        None]


def ShowKuafuChildInfo(parent, x, y, childID, shape, name):
    global g_SInfoDialog
    g_SInfoDialog = CChildInfoDialog(parent, x, y, childID, shape, name)


def ShowFakeSummonInfo(parent, x, y, shape, name, sinfo):
    global g_SInfoDialog
    g_SInfoDialog = CChildInfoDialog(parent, x, y, -1, shape, name)
    g_SInfoDialog.UpdateInfo(-1, sinfo)
    return g_SInfoDialog


def UpdateServerItemInfo(itype, oid, ext):
    import misc
    if itype == 0:
        it = item.GetItem(oid)
        if it:
            it.m_InfoExt = ext
        
    elif itype == 5:
        import dlgstorehouse
        oid = (oid - 1) + dlgstorehouse.STORE_START
        it = dlgstorehouse.GetSHItem(oid)
        if it:
            it.m_InfoExt = ext
        
        g_ItemInfos[itype][oid] = [
            misc.Time(),
            ext]
    else:
        g_ItemInfos[itype][oid] = [
            misc.Time(),
            ext]
    ul = []
    if type(g_ItemInfoTips[itype]) == list:
        ul = g_ItemInfoTips[itype]
    else:
        ul.append(g_ItemInfoTips[itype])
    for ts in ul:
        if ts:
            tips = ts.Get()
            if tips and tips.m_ItemID == oid:
                tips.Refresh(ext)
            
        tips.m_ItemID == oid
    


def NewItemInfo(id, shape, ext, parent, key = None):
    import wrapinterface
    import misc
    import itemdata
    (name, explain) = itemdata.GetData(shape)
    tip = None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, wrapinterface.CItemTips, shape, 'item', name, explain, ext, charcount = 32, key = key, parent = parent)
    tip.m_ItemID = id
    
    def docomp(obj, pos):
        import C_sys
        import key
        if C_sys.IsKeyDown(key.VK_CTRL) and obj.GetShow():
            if not hasattr(obj, 'm_CompTips') or obj.m_CompTips is None:
                import world
                it = item.GetItemWithPos(pos)
                obj.m_CompTips = ShowCompItemInfo(it)
                obj.SetAttach(obj.m_CompTips, 2)
                obj.m_CompTips.m_OwnerTips = interface.CShadowObject(obj)
            
        elif hasattr(obj, 'm_CompTips') and obj.m_CompTips:
            obj.SetAttach(None)
            obj.m_CompTips = None
        
        return (pos,)

    import itemdata
    pos = itemdata.GetEquipPos(shape)
    it = item.GetItemWithPos(pos)
    if it is not None and it.m_ID != id:
        tip.m_CompAni = tip.CreatePyCommand(5, docomp, pos)
    
    return tip


def ShowItemInfo(it, flag = 0):
    id = it.m_ID
    shape = it.m_Shape
    ext = None
    if hasattr(it, 'm_InfoExt'):
        ext = it.m_InfoExt
    else:
        it.m_InfoExt = None
        import netitem
        netitem.C2SItemString(it.m_ID, flag)
    iif = NewItemInfo(id, shape, ext, None, it.m_Key)
    g_ItemInfoTips[0][0] = interface.CShadowObject(iif)
    return iif


def ShowCompItemInfo(it):
    id = it.m_ID
    shape = it.m_Shape
    ext = None
    if hasattr(it, 'm_InfoExt'):
        ext = it.m_InfoExt
    else:
        it.m_InfoExt = None
        import netitem
        netitem.C2SItemString(it.m_ID, 0)
    import itemdata
    import wrapinterface
    (name, explain) = itemdata.GetData(shape)
    
    class CCompItemTips((wrapinterface.CItemTips,)):
        
        def ResetPosition(self):
            wrapinterface.CItemTips.ResetPosition(self)
            if hasattr(self, 'm_OwnerTips'):
                obj = self.m_OwnerTips.Get()
                if obj:
                    obj.ResetPosition()
                
            


    iif = CCompItemTips(shape, 'item', name, explain, ext, charcount = 32, key = it.m_Key)
    iif.m_ItemID = id
    g_ItemInfoTips[0][1] = interface.CShadowObject(iif)
    return iif


def ShowSHItemInfo(it):
    pos = it.m_Pos
    shape = it.m_Shape
    ext = None
    if hasattr(it, 'm_InfoExt'):
        ext = it.m_InfoExt
    else:
        it.m_InfoExt = None
        import netstorehouse
        import dlgstorehouse
        netstorehouse.C2SSHItemString(pos + 1 - dlgstorehouse.STORE_START)
    iif = NewItemInfo(pos, shape, ext, None, it.m_Key)
    g_ItemInfoTips[5] = interface.CShadowObject(iif)
    return iif


def ShowSaleItemInfo(shape, tid, gid):
    import misc
    import netplayer
    ext = None
    info = g_ItemInfos[1].get(gid)
    if info is None:
        g_ItemInfos[1][gid] = [
            misc.Time(),
            None]
        netplayer.C2SGetGoodsInfo(tid, gid)
    else:
        ext = info[1]
    iif = NewItemInfo(gid, shape, ext, None)
    g_ItemInfoTips[1] = interface.CShadowObject(iif)
    return iif


def ShowSaleSummonInfo(tid, pid, shape, name):
    global g_SInfoDialog
    g_SInfoDialog = CChildInfoDialog(interface.DialogPanel, 0, 0, pid, shape, name)
    interface.Center(g_SInfoDialog)
    import pet
    import misc
    pobj = pet.GetPet(pid)
    if pobj is None:
        info = g_SummonInfos.get(pid)
        if info is None:
            g_SummonInfos[pid] = NewSummonInfo()
            import netplayer
            netplayer.C2SGetGoodsInfo(tid, pid, 1)
        elif info['time'] + 60 < misc.Time():
            info['time'] = misc.Time()
            import netplayer
            netplayer.C2SGetGoodsInfo(tid, pid, 1)
        else:
            UpdateServerSummonInfo(pid, info)
    elif pobj.m_UpdateProp == False:
        import netpet
        netpet.C2SSummonView(pid)
    
    UpdateClientSummonInfo(pobj)


def ClearTradeItemInfo():
    g_ItemInfoTips[4] = None
    g_ItemInfos[4] = { }


def ShowFakeItem(shape, ext = None):
    import itemdata
    import wrapinterface
    (name, explain) = itemdata.GetData(shape)
    tip = wrapinterface.CItemTips(shape, 'item', name, explain, ext, charcount = 32)
    return tip


def ClearItemInfo(itype):
    g_ItemInfos[itype] = { }


def ShowShopItemInfo(pos, shape):
    import misc
    import netitemshop
    ext = None
    info = g_ItemInfos[6].get(pos)
    if info is None:
        g_ItemInfos[6][pos] = [
            misc.Time(),
            None]
        netitemshop.C2SGetItemInfo(pos)
    else:
        ext = info[1]
    iif = NewItemInfo(pos, shape, ext, None)
    g_ItemInfoTips[6] = interface.CShadowObject(iif)
    return iif


def ShowChatSkillInfo(skillnum, gslv, slv):
    global g_SkillTip, g_SkillTip, g_SkillTip
    import magicdata
    import petskill
    import specialdata
    import wrapinterface
    if skillnum in petskill.DATA:
        data = petskill.GetData(skillnum)
        g_SkillTip = wrapinterface.CChatSkillTips(data['name'], data['desc'])
        return None
    
    if skillnum in specialdata.DATA:
        data = specialdata.GetData(skillnum)
        info = '\xbb\xdd\xadn\xbc\xab\xab\xe3\xad\xc8\xa1G%d#r' % data['cost']
        info += '\xb3t\xb2v\xa1G%d%%#r' % data['speed']
        info += '\xbb\xa1\xa9\xfa\xa1G%s#r#r' % data['desc']
        info += '\xa4O\xbc\xc4\xa7\xdc\xa9\xca\xa1G%2d%%   \xc6F\xa5\xa9\xa7\xdc\xa9\xca\xa1G%2d%%#r' % (data['res_p'], data['res_d'])
        info += '\xb8s\xa7\xf0\xa7\xdc\xa9\xca\xa1G%2d%%   \xb4\xb6\xb3q\xa7\xdc\xa9\xca\xa1G%2d%%#r' % (data['res_m'], data['res_n'])
        g_SkillTip = wrapinterface.CChatSkillTips(data['name'], info)
        return None
    
    data = magicdata.GetData(skillnum)
    
    try:
        liupai = {
            11: '\xbcC\xb3N',
            12: '\xb5\xa7\xaak',
            13: '\xae\xb1\xaak',
            14: '\xa4M\xaak',
            15: '\xbaj\xb3N',
            16: '\xb7t\xbe\xb9',
            17: '\xb0\xad\xa8\xa6',
            21: '\xa6\xf2\xbe\xc7',
            22: '\xb9D\xaea',
            23: '\xbe\xa7\xbe\xc7',
            24: '\xa7\xc5\xb3N',
            25: '\xb3\xb1\xb6\xa7\xb3N',
            27: '\xa8\xe4\xa5\xa6' }[data['type']]
    except:
        liupai = '-'

    name = data['name']
    slvm = slv - 2
    if slvm < 0:
        slvm = 0
    
    costRate = 1
    maxslv = slv
    info = ''
    if data.get('invalid') == True:
        info = '\xa4@\xa4\xc1\xb3\xa3\xacO\xa5\xbc\xaa\xbe'
    else:
        powrate = eval(data['powrate'])
        if powrate == 0:
            powrate = '-'
        else:
            powrate = '%d%%' % powrate
        power = eval(data['pow'])
        if power == 0:
            power = '-'
        else:
            power = '%d' % power
        info += '\xacy\xac\xa3\xa1G%-10s \xab\xc2\xa4O\xa1G%s#r' % (liupai, power)
        if data['type'] != 27:
            info += '\xb5\xa5\xaf\xc5\xa1G%-10d \xb3t\xb2v\xa1G%d#r' % (slv, eval(data['speed']))
        else:
            info += '\xb5\xa5\xaf\xc5\xa1G%-10s \xb3t\xb2v\xa1G%d#r' % ('-', eval(data['speed']))
        info += '\xc3\xfe\xa7O\xa1G%-10s \xae\xc4\xb2v\xa1G%s#r' % (data['class'], powrate)
        
        try:
            ar = '%d' % eval(data['ar'])
        except:
            ar = '-'

        info += '\xa8t\xa7O\xa1G%-10s \xa9R\xa4\xa4\xa1G%s#r' % (data['stype'], ar)
        info += '#r'
        info += '#Y\xaa\xab\xb2z\xa7\xdc\xa9\xca#r#n'
        info += '#R\xb4\xb6\xb3q\xa7\xdc\xa9\xca\xa1G%-5s  \xa4O\xbc\xc4\xa7\xdc\xa9\xca\xa1G%-5s#r#n' % (str(data['res_n']) + '%', str(data['res_p']) + '%')
        info += '#R\xc6F\xa5\xa9\xa7\xdc\xa9\xca\xa1G%-5s  \xb8s\xa7\xf0\xa7\xdc\xa9\xca\xa1G%-5s#r#n' % (str(data['res_d']) + '%', str(data['res_m']) + '%')
        info += '#r'
        info += '#Y\xa8\xcf\xa5\xce\xae\xf8\xaf\xd3#r#n'
        info += '\xa7\xf0\xc0\xbb\xc2I\xa1G%-8d \xaak\xa4O\xa1G%d#r' % (data['at'], eval(data['mana']))
        if skillnum in (1428,) and 'effcount' in data and eval(data['effcount']) > eval(data['maxeffcount']):
            fpstr = data['fp']
            fpstr = fpstr.replace(data['effcount'], data['maxeffcount'])
            info += '\xa8\xbe\xbfm\xc2I\xa1G%-8d \xa4O\xb9D\xa1G%d#r' % (data['df'], eval(fpstr))
        else:
            info += '\xa8\xbe\xbfm\xc2I\xa1G%-8d \xa4O\xb9D\xa1G%d#r' % (data['df'], eval(data['fp']))
        info += '\xa4z\xc2Z\xc2I\xa1G%-8d#r' % data['dp']
        info += '#r'
        info += '\xbb\xa1\xa9\xfa\xa1G%s#r#r' % data['desc']
    g_SkillTip = wrapinterface.CChatSkillTips(name, info)
    interface.Center(g_SkillTip)


def ShowChatBaseSkillInfo(skillnum, lv, select_class):
    global g_SkillTip, g_SkillTip
    import xinfadata
    import skilldata
    import wrapinterface
    if select_class in (5, 6):
        data = xinfadata.GetData(skillnum)
        g_SkillTip = wrapinterface.CChatSkillTips(data['name'], data['desc'])
        return None
    
    data = skilldata.GetData(skillnum)
    name = data['name']
    info = '%d\xaf\xc5#r#r' % lv
    if data.get('invalid') == True:
        info = '\xa4@\xa4\xc1\xb3\xa3\xacO\xa5\xbc\xaa\xbe'
    else:
        info += data['desc']
    g_SkillTip = wrapinterface.CChatSkillTips(name, info)
    interface.Center(g_SkillTip)
