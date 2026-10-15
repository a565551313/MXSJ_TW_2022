# pycdc 交叉复核产物 · script.fls entry 4449
# co_filename(原始)='script/dialog/dlgride.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4449.pyc (Python 2.5)

'''
\xd7\xf8\xc6\xef\xd4\xa4\xc0\xc0\xbd\xe7\xc3\xe6
'''
import time
import autofindpath
import chardefine
import charpath
import clickimage
import combdialog
import combmacro
import cursor
import descinterface
import guage
import hero
import interface
import item
import mdmxride
import itemdefine
import misc
import netride
import netstate
import netstatedefine
import ridedata
import ridedefine
import rideinterface
import seawar
import skilliconpath
import style
import ui
import usermacro
import walker
import wrapinterface
import permission
import tipsclosemgr
import mdrideskill
import rideskilldefines
g_DlgRide = None
g_Rebuild_Ride = None
g_RideInfoDlg = None
g_LinkType = 0
g_Type2EquipLst = { }
g_Type2LinkDesc = { }
g_FairyPal = 0
g_SkillTips = None
TYPE_NORMAL = 0
TYPE_FLY = 1
TYPE_MULTI = 2
TYPE_JUNIOR = 3
g_OldServer = [
    30003,
    411,
    412,
    111,
    3101,
    3102,
    3106,
    3110,
    3114,
    3118,
    3122,
    3301,
    3307,
    3201,
    3204,
    3208,
    3212,
    3216,
    3220,
    3225,
    3232,
    3238,
    3242,
    3244,
    3245,
    3246,
    3315,
    3324,
    3337,
    3343,
    3349,
    3353,
    3355,
    3359,
    3363,
    3365,
    3366,
    3367,
    3368,
    202,
    301]

def ModuleReset():
    global g_DlgRide, g_Rebuild_Ride, g_RideInfoDlg, g_LinkType, g_Type2EquipLst, g_Type2LinkDesc, g_FairyPal, g_SkillTips
    g_DlgRide = None
    g_Rebuild_Ride = None
    g_RideInfoDlg = None
    g_LinkType = 0
    g_Type2EquipLst = { }
    g_Type2LinkDesc = { }
    g_FairyPal = 0
    g_SkillTips = None


def UseHorse(iHorseID, iRideType):
    if misc.IsJingJiServer():
        usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xbe\xde\xa7@')
        return None
    
    if guage.IsDelaying():
        return None
    
    if not iHorseID:
        return None
    
    if seawar.InWar():
        return None
    
    if hero.InMultiHorse():
        usermacro.PROMPT_MSG('\xb1z\xa5\xbf\xc3M\xad\xbc\xa6h\xa4H\xa7\xa4\xc3M\xa1A\xbc\xc8\xae\xc9\xa4\xa3\xaf\xe0\xa4\xc1\xb4\xab\xa7\xa4\xc3M\xbc\xd2\xa6\xa1!')
        return None
    
    if hero.IsInEventPoint():
        usermacro.PROMPT_MSG('\xb7\xed\xabe\xa4\xa3\xa4\xb9\xb3\\\xa4\xc1\xb4\xab\xa7\xa4\xc3M\xbc\xd2\xa6\xa1\xa1A\xbd\xd0\xa8\xec\xb3\xb0\xa6a\xa4W\xa6A\xb8\xd5')
        return None
    
    autofindpath.StopAuto()
    oRideModel = mdmxride.GetMXRideInfoMgr()
    if iRideType in (ridedefine.RIDE_TYPE_FLY, ridedefine.RIDE_TYPE_TMPFLY, ridedefine.RIDE_TYPE_SPEFLY):
        if oRideModel.GetHaveHuaLing() or hero.GetProp('m_FlyState') in (1, 2):
            netride.C2GSActiveMode(iRideType, iHorseID)
        elif oRideModel.GetRideHorseShape() == iHorseID:
            netride.C2GSDelActive()
        else:
            netride.C2SChangeRideMode(iRideType, 2, iHorseID)
    elif iRideType == ridedefine.RIDE_TYPE_MULTI:
        if hero.GetProp('m_FlyState') in (1, 2):
            netride.C2GSActiveMode(iRideType, iHorseID)
        elif oRideModel.GetRideHorseShape() == iHorseID:
            netride.C2GSDelActive()
        else:
            netride.C2SChangeRideMode(iRideType, 2, iHorseID)
    elif oRideModel.GetHaveHuaLing():
        netride.C2GSActiveMode(iRideType, iHorseID)
    elif oRideModel.GetRideHorseShape() == iHorseID:
        netride.C2GSDelActive()
    else:
        netride.C2SChangeRideMode(iRideType, 2, iHorseID)


class CSkillTips(interface.CBoxObject, interface.CBase):
    TIPS_WIDTH = 300
    TIPS_HEIGHT = 210
    H = [
        10,
        10,
        40,
        5,
        5,
        5]
    SKILL_POS = (10, 120)
    
    def __init__(self, skid, iStyle = 0, oSkillPlan = None):
        interface.CBoxObject.__init__(self, interface.MainPanel, 1, 1, 8224, 144)
        import ridedatainfo
        if skid in ridedatainfo.DATA:
            self.m_SkdDict = ridedatainfo.DATA[skid]
        else:
            return None
        if skid / 100 < 4:
            skilltype = 1
        else:
            skilltype = 0
        self.SetTitle()
        self.SetSkillIcon(oSkillPlan, skilltype, iStyle)
        self.SetBackGround()

    
    def SetTitle(self):
        font = interface.FontLT14_17
        colorstr = style.GetStr('dlgride.CSkillTips', 'data_name_color')
        self.m_iAllHeight = 0
        self.m_Name = interface.CRichTextObject(self, self.TIPS_WIDTH - 20, font, colorstr + self.m_SkdDict['name'])
        (w, h) = self.m_Name.GetSize()
        self.m_Name.SetPos((self.TIPS_WIDTH - w) / 2, CSkillTips.H[0])
        self.m_iAllHeight += CSkillTips.H[0]
        self.m_iAllHeight += h
        infoColor = style.GetStr('dlgride.CSkillTips', 'data_info_color')
        infoText = infoColor + self.m_SkdDict['desc']
        self.m_Info = interface.CRichTextObject(self, self.TIPS_WIDTH - 20, interface.FontLT14_3, infoText)
        self.m_Info.SetPos(10, self.m_iAllHeight + CSkillTips.H[1])
        (w, h) = self.m_Info.GetSize()
        self.m_iAllHeight += CSkillTips.H[1]
        self.m_iAllHeight += h

    
    def SetSkillIcon(self, oSkillPlan, skilltype, skillstyle):
        import ridedatainfo
        self.m_oSkillPlan = oSkillPlan
        self.m_dSkillIcon = { }
        dct = ridedatainfo.DATA
        if skilltype:
            self.SetMainSkill(dct, skillstyle)
        else:
            self.SetSecSkill(dct)

    
    def SetMainSkill(self, dct, skillstyle):
        infoColor = style.GetStr('dlgride.CSkillTips', 'data_info_color')
        self.m_oTempTxt = interface.CRichTextObject(self, 280, interface.FontLT14_3, infoColor + '\xa4\xb9\xb3\\\xbe\xc7\xb2\xdf\xaa\xba\xb0\xc6\xa7\xde\xaf\xe0:')
        (w, h) = self.m_oTempTxt.GetSize()
        self.m_oTempTxt.SetPos((self.TIPS_WIDTH - w) / 2, self.m_iAllHeight + CSkillTips.H[2])
        self.m_iAllHeight += CSkillTips.H[2]
        self.m_iAllHeight += h
        i = 0
        temptype = self.m_SkdDict['type']
        nameColor = style.GetStr('dlgride.CSkillTips', 'data_name_color')
        for key, data in dct.items():
            if data['type'] == temptype and key / 100 > 3:
                self.m_dSkillIcon[key] = CSkillIcon(self, CSkillTips.SKILL_POS[0] + i * 65, self.m_iAllHeight + CSkillTips.H[3], key)
                self.m_dSkillIcon[key].SetSkillInfo(self.m_oSkillPlan)
                if skillstyle == 0:
                    
                    try:
                        if key not in secondskills[temptype]:
                            self.m_dSkillIcon[key].SetGrey()
                            name = infoColor + data['name']
                        else:
                            name = nameColor + data['name']
                    self.m_dSkillIcon[key].SetGrey()
                    name = infoColor + data['name']

                elif skillstyle == 1:
                    name = nameColor + data['name']
                
                self.m_dSkillIcon[key].name = interface.CRichTextObject(self, 65, interface.FontLT14_3, name)
                self.m_dSkillIcon[key].name.SetPos(CSkillTips.SKILL_POS[0] + i * 65, self.m_iAllHeight + CSkillTips.H[3] + CSkillTips.H[4])
                i += 1
                continue
        
        allw = i * 65
        x1 = CSkillTips.SKILL_POS[0] - (self.TIPS_WIDTH - allw) / 2
        for key, data in self.m_dSkillIcon.items():
            (iw, ih) = data.GetSize()
            (tw, th) = data.name.GetSize()
            data.SetPos(data.GetPos()[0] - x1, self.m_iAllHeight + CSkillTips.H[3])
            data.name.SetPos(data.GetPos()[0] - (tw - iw) / 2, self.m_iAllHeight + CSkillTips.H[3] + ih + CSkillTips.H[4])
        
        self.m_iAllHeight += CSkillTips.H[3] + ih + CSkillTips.H[4] + th + CSkillTips.H[5]

    
    def GetSkillTxtColor(self):
        if interface.IsStyle1():
            return ''
        elif interface.IsStyle2():
            return ''
        else:
            return '#cC6FFF8'

    
    def SetSecSkill(self, dct):
        tempColor = self.GetSkillTxtColor()
        self.m_oTempTxt = interface.CRichTextObject(self, 280, interface.FontLT14_3, tempColor + '\xb0\xf2\xa9\xf3:')
        (w, h) = self.m_oTempTxt.GetSize()
        self.m_oTempTxt.SetPos((self.TIPS_WIDTH - w) / 2, self.m_iAllHeight + CSkillTips.H[2])
        self.m_iAllHeight += CSkillTips.H[2]
        self.m_iAllHeight += h
        temptype = self.m_SkdDict['type']
        
        try:
            key = mainskills[temptype]
        except:
            None if self.m_oSkillPlan else self
            for i, data in dct.items():
                if data['type'] == temptype and i / 100 < 4:
                    key = i
                    break
                    continue
            

        self.m_dSkillIcon[key] = CSkillIcon(self, (self.TIPS_WIDTH - 60) / 2, self.m_iAllHeight + self.H[3], key)
        nameColor = style.GetStr('dlgride.CSkillTips', 'data_name_color')
        self.m_dSkillIcon[key].name = interface.CRichTextObject(self, 100, interface.FontLT14_3, nameColor + dct[key]['name'])
        (iw, ih) = self.m_dSkillIcon[key].GetSize()
        (tw, th) = self.m_dSkillIcon[key].name.GetSize()
        self.m_dSkillIcon[key].name.SetPos((self.TIPS_WIDTH - 60) / 2 - (tw - iw) / 2, self.m_iAllHeight + CSkillTips.H[3] + ih + CSkillTips.H[4])
        self.m_iAllHeight = self.m_iAllHeight + CSkillTips.H[3] + ih + CSkillTips.H[4] + th + CSkillTips.H[5]

    
    def SetBackGround(self):
        self.m_oBackGroud = interface.CBoxObject(self, self.TIPS_WIDTH, self.m_iAllHeight, 8224, 144)
        self.m_oLineList = []
        line = interface.CLine(self, 0, -1, self.TIPS_WIDTH, -1, 16777215, 1, 256)
        self.m_oLineList.append(line)
        line = interface.CLine(self, self.TIPS_WIDTH + 1, 0, self.TIPS_WIDTH + 1, self.m_iAllHeight, 16777215, 1, 256)
        self.m_oLineList.append(line)
        line = interface.CLine(self, self.TIPS_WIDTH, self.m_iAllHeight + 1, 0, self.m_iAllHeight + 1, 16777215, 1, 256)
        self.m_oLineList.append(line)
        line = interface.CLine(self, -1, self.m_iAllHeight, -1, 0, 16777215, 1, 256)
        self.m_oLineList.append(line)
        (x, y) = cursor.GetPos()
        x = x - self.TIPS_WIDTH / 2
        if x < 0:
            x = 0
        elif x + self.TIPS_WIDTH >= 800:
            x = 800 - self.TIPS_WIDTH
        
        if y + self.TIPS_HEIGHT + 50 > 600:
            y = y - 50 - self.TIPS_HEIGHT
        else:
            y = y + 50
        self.SetPos(x, y)
        self.Topmost()

    
    def IsCtrlNoRelease(self):
        return True



class CSkillIcon(interface.CClickBox):
    
    def __init__(self, parent, x, y, skid, iStyle = 0):
        interface.CClickBox.__init__(self, parent, 0, 0, 0, 0, msgid = 0)
        
        try:
            (offx, offy) = style.GetIntTuple('dlgride.CSkillIcon', 'data_bg_pos')
            (path, sPack) = skilliconpath.GetHorseSkillIconPath(skid, False)
            self.m_BGImg = ui.CImage(self, path, sPack)
            self.m_BGImg.SetPos(offx, offy)
            self.m_FilePath = path
            self.m_IsOK = True
        except:
            unknow_path = style.GetStr('dlgride.CSkillIcon', 'data_unknow_path')
            disable_path = style.GetStr('dlgride.CSkillIcon', 'data_disable_path')
            (iImgOffsetX, iImgOffsetY) = style.GetIntTuple('dlgride.CSkillIcon', 'data_unknow_img_offset')
            if interface.IsIgsPath(unknow_path):
                self.m_ClassType = interface.CImagesObject
            else:
                self.m_ClassType = interface.CBitmapObject
            if skid == 0:
                self.m_BGImg = self.m_ClassType(self, unknow_path, interface.UIPath)
                self.m_FilePath = unknow_path
            elif skid == 1:
                self.m_BGImg = self.m_ClassType(self, disable_path, interface.UIPath)
                self.m_FilePath = disable_path
            else:
                (path, sPack) = skilliconpath.GetHorseSkillIconPath(425)
                self.m_BGImg = ui.CImage(self, path, sPack)
                self.m_FilePath = path
            self.m_IsOK = False
            self.m_BGImg.SetPos(iImgOffsetX, iImgOffsetY)

        self.m_BGImg.SetZ(-1)
        (w, h) = self.m_BGImg.GetSize()
        self.m_Style = iStyle
        self.m_SkillID = skid
        self.m_oSkillPlan = None
        self.SetSize(w, h)
        self.SetPos(x, y)

    
    def SetSkillInfo(self, oSkillPlan):
        self.m_oSkillPlan = oSkillPlan

    
    def SetLight(self, *arg):
        self.m_BGImg.SetLight(*arg)

    
    def Enter(self):
        global g_SkillTips
        if not self.m_IsOK:
            return None
        
        if self.m_oSkillPlan:
            g_SkillTips = CSkillTips(self.m_SkillID, self.m_Style, self.m_oSkillPlan)
            if self.m_SkillID / 100 < 4:
                tipsclosemgr.Regist(g_SkillTips)
            
        

    
    def Leave(self):
        global g_SkillTips
        if not self.m_IsOK:
            return None
        
        tipsclosemgr.CheckClose()
        g_SkillTips = None

    
    def SetGrey(self):
        self.m_BGImg.SetGrey()



class CRideSkillDlg(combdialog.CAttachCombDialog):
    
    def __init__(self, parent, bShowRecommend):
        if permission.IsOpenRideRecommend():
            combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/ride/dlgrideskillnew.dlg')
        else:
            combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/ride/dlgrideskill.dlg')
        (w, h) = parent.GetSize()
        (sw, sh) = self.GetSize()
        self.SetPos(w - 8, h - sh)
        self.m_oSkillPlan = None
        self.updateskill()
        self.CreateImageTips()
        self.m_bShowRecommend = bShowRecommend
        self.SetRecommendBtnShow(bShowRecommend)

    
    def SetSkillPlan(self, oSkillPlan):
        self.m_oSkillPlan = oSkillPlan

    
    def SetRecommendBtnShow(self, bShow):
        self.SetShowObject('rtxt_recommend', bShow)

    
    def CreateImageTips(self):
        (x, y) = self.GetObject('loc_Tips').GetPos()
        obj = clickimage.CClickImage(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 10, x, y)
        self.m_ImgTips = obj

    
    def OnEnter(self, msgid):
        txt = None
        if msgid == 10:
            txt = '\xc2I\xc0\xbb\xacd\xac\xdd\xa9\xd2\xa6\xb3\xa7\xa4\xc3M\xa7\xde\xaf\xe0'
        
        if txt:
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def ShowData(self, data):
        self.m_Icons = { }
        box_main = self.GetObject('mainskill')
        box_second = self.GetObject('secondskill')
        for i in range(0, len(data)):
            if i not in data:
                continue
            
            igss = [
                box_main.m_Imagess[i],
                box_second.m_Imagess[2 * i],
                box_second.m_Imagess[2 * i + 1]]
            skills = data[i]
            for j in (0, 1, 2):
                img = igss[j]
                (mx, my) = img.GetParent().GetPos()
                (x, y) = img.GetPos()
                if skills[j] in (0, 1):
                    (dx, dy) = (0, 0)
                else:
                    (dx, dy) = (3, 3)
                (offx, offy) = style.GetIntTuple(self.GetDlgPath(), 'data_img_offset')
                dx = dx + offx
                dy = dy + offy
                icon = CSkillIcon(self, mx + x + dx, my + y + dy, skills[j])
                icon.SetSkillInfo(self.m_oSkillPlan)
                self.m_Icons[(i, j)] = icon
            
        

    
    def updateskill(self):
        if not self.m_oSkillPlan:
            return None
        
        self.ShowData(self.m_oSkillPlan.GetSkillList())

    
    def clearskill(self):
        data = {
            0: [
                1,
                1,
                1],
            1: [
                1,
                1,
                1],
            2: [
                1,
                1,
                1],
            3: [
                1,
                1,
                1],
            4: [
                1,
                1,
                1],
            5: [
                1,
                1,
                1] }
        self.ShowData(data)

    
    def RightUp(self):
        self.SetShow(False)

    
    def OpenRideSkillMainDlg(self, iMsgID):
        import dlgrideskillmain
        iPage = {
            10: rideskilldefines.PAGE_YULAN,
            1: rideskilldefines.PAGE_RECOMMEND }.get(iMsgID, rideskilldefines.PAGE_YULAN)
        mdrideskill.GetCRideSkillModel().SetShowRecommend(self.m_bShowRecommend)
        dlgrideskillmain.OpenPage(iPage)

    
    def OnMessage(self, msgid):
        import dlgrideskill
        if permission.IsOpenRideRecommend():
            if msgid in (1, 10):
                self.OpenRideSkillMainDlg(msgid)
            
        elif msgid == 10:
            dlgrideskill.Show()
        



class CRideitem(combdialog.CAttachCombDialog):
    
    def __init__(self, parent):
        combdialog.CAttachCombDialog.__init__(self, parent, 'dialog/ride/dlgitem.dlg')
        (w, h) = parent.GetSize()
        (sw, sh) = self.GetSize()
        self.SetPos(w - 8, h - sh)
        self.CreateItemArea()
        self.CheckValid()
        self.m_Boxs = [
            (self.GetObject('area_item1'), self.GetObject('area_fight')),
            (self.GetObject('area_item2'),)]
        self.GetObject('btn_Xingnang').LeftUp()

    
    def CreateItemArea(self):
        self.m_InterfaceItems = { }
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_item1', self, item.ITEM_START, self.m_InterfaceItems, 200)
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_fight', self, item.ITEM_FIGHT_START, self.m_InterfaceItems, 200)
        combmacro.CITEMAREA(item.CInterfaceItem, 'area_item2', self, item.ITEM_SCOPE, self.m_InterfaceItems, 200)
        item.AddInterfaceCallback(self.m_InterfaceItems, oRefObj = self)
        item.AddShadowCallback('DlgRideitem', interface.CShadowObject(self), 'RefershShadow')

    
    def ReleaseItemArea(self):
        item.ReleaseInterfaceCallback(self.m_InterfaceItems)

    
    def CheckValid(self):
        for iif in self.m_InterfaceItems.values():
            self.SetItem(iif)
        

    
    def SetItem(self, iif):
        if not iif:
            return None
        
        valid = False
        if iif.GetItem():
            it = iif.GetItem()
            import itemdata
            if itemdata.IsType(it.m_Shape, 'ride'):
                valid = True
            
        
        iif.Enable(valid)
        iif.ShowShadow(not valid)

    
    def RefershShadow(self):
        self.SetShadow(30, item.ITEM_START)
        self.SetShadow(10, item.ITEM_FIGHT_START)
        self.SetShadow(hero.g_Prop.m_BagMax, item.ITEM_SCOPE)

    
    def SetShadow(self, num, startidx):
        for i in range(num):
            pos = i + startidx
            iif = self.m_InterfaceItems.get(pos)
            self.SetItem(iif)
        

    
    def Switch(self, showType):
        for idx in range(2):
            bShow = showType == idx
            for box in self.m_Boxs[idx]:
                if box:
                    box.SetShow(bShow)
                
                if hasattr(box, 'm_Real'):
                    for real in box.m_Real:
                        ob = real.Get()
                        if ob:
                            ob.SetShow(bShow)
                            continue
                    
            
        

    
    def UseItem(self, pos):
        import itemdata
        import commondialog
        iCurRide = self.GetSelRideID()
        if not iCurRide:
            return None
        
        
        def OK(dlg):
            import netitem
            netitem.C2SItemUse(dlg.m_ItemID, dlg.m_RideID)

        iif = self.m_InterfaceItems[pos]
        if iif and iif.GetItem():
            it = iif.GetItem()
            if itemdata.IsType(it.m_Shape, 'ride'):
                sItemName = itemdata.GetData(it.m_Shape)[0]
                sRideName = ridedata.GetRideName(iCurRide)
                dlg = commondialog.ShowMessageBox('\xbdT\xa9w\xb9\xef#Y%s#n\xa8\xcf\xa5\xce%s\xb6\xdc\xa1H' % (sRideName, sItemName), ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OK, None))
                dlg.m_ItemID = it.m_ID
                dlg.m_RideID = iCurRide
            else:
                usermacro.PROMPT_MSG('\xabD\xa7\xa4\xc3M\xaa\xab\xab~!')
        

    
    def GetSelRideID(self):
        par = self.GetParent()
        return par.GetSelectHorseID()

    
    def OnMessage(self, msgid):
        if msgid in (1, 2):
            self.Switch(msgid - 1)
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid - interface.RIGHT_BUTTON_MESSAGE < 500 + item.ITEM_START:
            self.UseItem(msgid - interface.RIGHT_BUTTON_MESSAGE - 200)
        



class CEquipBox(interface.CBoxObject, interface.CBase):
    
    def __init__(self, parent, pos, shape, desc, num = 1):
        interface.CBoxObject.__init__(self, parent, 54, 53, 0, 0)
        self.MessageProcess()
        self.m_ItemImg = item.CreateItem44Image(self, shape)
        self.m_ItemImg.SetPos(5, 4)
        import ui
        self.m_SelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
        self.m_SelBox.SetPos(4, 3)
        self.m_SelBox.SetShow(False)
        self.m_Pos = pos
        self.m_Shape = shape
        self.m_Desc = desc
        self.m_Tip = None
        self.m_EquipBackground = None
        if num > 0:
            self.m_TextNum = interface.CTextObject(self, str(num), interface.FontLT14_3, 16776960, 0)
            (x, y) = self.GetSize()
            (tw, th) = self.m_TextNum.GetSize()
            self.m_TextNum.SetPos(x - 7 - tw, y - 5 - th)
            self.m_TextNum.SetZ(1)
        else:
            self.m_TextNum = None
        self.CreateEquipBack()

    
    def GetEquipPos(self):
        return self.m_Pos

    
    def CreateEquipBack(self):
        import style
        import ui
        sImgPath = style.GetStr('dlgride.CEquipBox.CreateEquipBack', 'data_bg_img')
        (ix, iy) = style.GetIntTuple('dlgride.CEquipBox.CreateEquipBack', 'data_bg_img')
        self.m_EquipBackground = ui.CImage(self, sImgPath, interface.UIPath)
        self.m_EquipBackground.SetPos(ix, iy)
        self.m_EquipBackground.SetZ(-1)

    
    def RefreshTipDesc(self, sDesc):
        if sDesc == self.m_Desc:
            return None
        else:
            self.m_Desc = sDesc
        if self.m_Tip:
            self.m_Tip.Refresh(sDesc)
        

    
    def Enter(self):
        import dlggetinfo
        import netride
        netride.C2GSResetRideEquipment(self.m_Pos)
        self.m_SelBox.SetShow(True)
        self.m_Tip = dlggetinfo.ShowFakeItem(self.m_Shape, self.m_Desc)
        self.m_Tip.SetOwner(self)

    
    def Leave(self):
        self.m_SelBox.SetShow(False)
        self.m_Tip = None



class CEquipBoxEx(CEquipBox):
    
    def __init__(self, parent, iPos, iShape, sDesc, iNum):
        CEquipBox.__init__(self, parent, iPos, iShape, sDesc, iNum)
        self.m_ItemImg = None
        self.m_TextNum = None
        self.m_oTips = None
        self.m_iShape = iShape
        self.m_iNum = iNum
        self.InitData()

    
    def InitData(self):
        import makeitemicon
        oItemImg = makeitemicon.CNeedItemIcon(self, self.m_iShape, 999)
        oItemImg.SetTextFont(interface.FontLT10E)
        oItemImg.AddEnterCB(self.Enter)
        oItemImg.AddLeaveCB(self.Leave)
        interface.Center(oItemImg)
        oItemImg.SetFreeze(True)
        self.m_iNeed = 0
        if getattr(self.GetParent(), 'GetCurNeedNum', None):
            self.m_iNeed = self.GetParent().GetCurNeedNum()
        
        if self.m_iNeed != 0:
            oItemImg.SetNeedTxt(self.m_iNum, self.m_iNeed)
        else:
            oItemImg.DelNeedTxt()
        self.m_ItemImg = oItemImg
        self.m_oAddBtn = CNeedAddItemBtn(self)
        self.m_oAddBtn.SetAddCB(self.OnClickBuyNeedItem)
        self.m_oAddBtn.SetPos(5, 4)
        self.m_oAddBtn.SetZ(10)
        if self.m_iNum >= self.m_iNeed:
            self.m_ItemImg.SetFreeze(False)
            self.m_oAddBtn.SetShow(False)
        

    
    def OnClickBuyNeedItem(self):
        import netitem
        import netopenui
        if not self.GetParent().CheckCurSelectedIsOnRide():
            usermacro.PROMPT_MSG('\xa5u\xaf\xe0\xb9\xef\xc3M\xad\xbc\xbc\xd2\xa6\xa1\xa4U\xa9M\xba\xeb\xc6F\xbc\xd2\xa6\xa1\xa4U\xa7\xa4\xc3M\xa8\xcf\xa5\xce\xa1I')
            return None
        
        oItemDict = item.GetItemsByShape(self.m_iShape)
        if oItemDict:
            oItem = oItemDict.values()[0]
            iItemID = oItem.GetID()
            netitem.C2SItemUse(iItemID)
        else:
            iNum = self.m_iNeed - self.m_iNum
            netopenui.C2SUseQuickBuy(self.m_Shape, iNum)

    
    def Enter(self):
        if self.m_iNum == 0:
            iMsgID = None if self.m_Shape == itemdefine.ID_ITEM_HORSE_DECORATE else 12
            self.GetParent().OnEnter(iMsgID)
        else:
            import dlggetinfo
            self.m_SelBox.SetShow(True)
            self.m_oTips = dlggetinfo.ShowFakeItem(self.m_Shape, self.m_Desc)
            self.m_oTips.SetOwner(self)

    
    def Leave(self):
        if self.m_iNum == 0:
            oParent = self.GetParent()
            if oParent:
                pass
            oParent.OnLeave(0)
        else:
            self.m_SelBox.SetShow(False)
            self.m_oTips = None



class CNeedAddItemBtn(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, iUIStyle = None):
        if iUIStyle is None:
            iUIStyle = ''
        
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog%s/equip/jiahao.dlg' % iUIStyle)
        self.SetIgnoreEsc(True)
        self.m_oCB = None
        self.GetObject('btn_add').m_Button_Type = 1

    
    def SetTips(self, sTips):
        self.GetObject('btn_add').SetTips(sTips)

    
    def SetAddCB(self, oCB, *args):
        self.m_oCB = misc.Functor(oCB, *args)

    
    def BnEnter(self, iMsgid):
        if self.GetParent() and hasattr(self.GetParent(), 'Enter'):
            self.GetParent().Enter()
        

    
    def BnLeave(self, iMsgid):
        if self.GetParent() and hasattr(self.GetParent(), 'Leave'):
            self.GetParent().Leave()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            if self.m_oCB and callable(self.m_oCB):
                self.m_oCB()
            
        



class CClickImage(clickimage.CClickImage):
    
    def GetPar(self):
        
        try:
            par = self.GetParent().GetParent().GetParent()
        except:
            par = None

        return par



class CRideDialog(combdialog.CCombDialog):
    ISFAIRYTYPE = (0, 1, 3, 4, 5, 200)
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/ride/dlgride.dlg')
        interface.Center(self)
        self.m_EquipBoxes = []
        self.m_bSWitchRideSkill = False
        self.m_EquipBoxes = []
        self.m_CurViewIdx = -1
        self.m_SelectRide = -1
        self.m_iCurSelRide = 0
        self.m_oDelayRefreshTimer = None
        self.SetShow(False)
        self.InitBtn()
        self.SetRideInfoType()
        self.CreateOtherDlg()
        self.CreateBornImgTips()
        self.CreateGradeNotifyBox()
        self.SetNotifyBox([
            'item1',
            'item2'])
        self.SetImageTip()
        self.RefreshRideLst()
        self.InitSignal()
        self.RefreshBtnGradeDown()

    
    def GetSelectHorseID(self):
        return self.m_iCurSelRide

    
    def CheckCurSelectedIsOnRide(self):
        if not self.m_iCurSelRide:
            return False
        
        return self.GetMXRideInfoMgr().GetRideHorseShape() == self.m_iCurSelRide

    
    def GetMXRideInfoMgr(self):
        return mdmxride.GetMXRideInfoMgr(mdmxride.SELF_TYPE)

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        import cursor
        if not hasattr(self, 'm_Desc') or self.m_Desc is None:
            return None
        
        if hasattr(self, 'm_LinkDct') and self.m_LinkDct:
            (x, y) = cursor.GetPos()
            (rx, ry) = self.m_Desc.GetScreenPos()
            clickID = self.m_Desc.ClickID(x - rx, y - ry)
            if clickID in self.m_LinkDct:
                self.m_LinkDct[clickID].OnLeftUp()
            
        

    
    def InitBtn(self):
        self.GetObject('btn_ExpAdd').SetZ(100)
        self.GetObject('btn_ExpAdd').SetTips('\xc2I\xc0\xbb\xc1\xca\xb6R\xa7\xa4\xc3M\xb8g\xc5\xe7')
        self.GetObject('btn_ExpAdd').m_ParentNotify = True
        bShow = misc.IsNationFightServer()
        self.GetObject('btn_mode').SetShow(not bShow)
        self.SetShowObject('btn_item', False)

    
    def InitSignal(self):
        import hero
        hero.AddPropCallBack('CRideDialog', 'm_Desc', self.RefreshPhoto)
        oModel = self.GetMXRideInfoMgr()
        oModel.ssConnect(oModel.SS_UpdateEquipInfoChange, self.OnEquipInfoChange)
        oModel.ssConnect(oModel.SS_SkillPlanInfoChange, self.OnSkillPlanInfoChange)
        oModel.ssConnect(oModel.SS_MaxSkillPlanChange, self.OnMaxSkillPlanChange)
        oModel.ssConnect(oModel.SS_CurSkillPlanChange, self.OnCurSkillPlanChange)
        oModel.ssConnect(oModel.SS_UpdateRideHorseType, self.OnUpdateRideHorseType)
        oModel.ssConnect(oModel.SS_UpdateRideHorseShape, self.OnUpdateRideHorseShape)

    
    def CreateGradeNotifyBox(self):
        (x, y, w, h) = self.GetLocData('txt_grade')
        self.m_TipsGrade = interface.CNotifyBox(self, w, h, 0, 0, 22)
        self.m_TipsGrade.SetPos(x, y)
        self.m_TipsGrade.Topmost()

    
    def CreateBornImgTips(self):
        img = self.GetObject('img_Tips')
        (x, y) = img.GetPos()
        y -= style.GetInt(self.GetDlgPath(), 'data_img_offset_y')
        obj = clickimage.CClickImage(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 24, x, y)
        self.m_BornImgTips = obj
        self.m_BornImgTips.SetShow(False)

    
    def SetImageTip(self):
        oImg = self.GetObject('img_Tips')
        (ix, iy) = oImg.GetPos()
        if hasattr(self, 'm_ExpText'):
            (ew, _) = self.m_ExpText.GetSize()
            (ex, ey) = self.m_ExpText.GetPos()
            oImg.SetPos(ew + ex + 8, iy)
        
        (x, y) = oImg.GetPos()
        obj = clickimage.CClickImage(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 10, x, y)
        self.m_ImgTips = obj

    
    def CheckBornImgShow(self):
        if not self.m_iCurSelRide:
            return None
        
        iRebirthGrade = self.GetRideRebthGrade()
        iRideGrade = self.GetRideGrade()
        iNormalGrade = self.GetRideNormalLevel()
        if iRebirthGrade > 0 and iRideGrade <= iRebirthGrade:
            self.m_BornImgTips.SetShow(True)
        elif iNormalGrade and iRideGrade < iNormalGrade:
            self.m_BornImgTips.SetShow(True)
        else:
            self.m_BornImgTips.SetShow(False)
        if hasattr(self, 'm_GradeText'):
            (ew, _) = self.m_GradeText.GetSize()
            (ex, ey) = self.m_GradeText.GetPos()
            iOffsetY = style.GetInt(self.GetDlgPath(), 'data_tips_offset_y')
            x = ew + ex + 8
            y = ey - iOffsetY
            self.m_BornImgTips.SetPos(x, y)
        

    
    def RefreshGrade(self):
        self.RefreshGradeExpText()
        self.CheckBornImgShow()
        self.RefreshBtnGradeDown()

    
    def SetRideInfoType(self):
        oModel = self.GetMXRideInfoMgr()
        iCurPlan = oModel.GetCurSkillPlan()
        iPrvPlan = oModel.GetPrvSkillPlan()
        iMaxPlan = oModel.GetMaxSkillPlan()
        if iPrvPlan == -1:
            iPrvPlan = iCurPlan
        
        self.m_CurViewIdx = iPrvPlan
        self.m_SelectRide = iCurPlan
        if iMaxPlan > 1:
            iShowNum = iMaxPlan
            bTxtShowFlag = True
        else:
            iShowNum = 0
            bTxtShowFlag = False
        self.GetObject('skillplantxt').SetShow(bTxtShowFlag)
        self.SetBtnTip('btn_review', '\xb9w\xc4\xfd')
        self.SetBtnTip('btn_select', '\xbf\xef\xbe\xdc')
        self.SwitchBtnState(iPrvPlan, iCurPlan, iShowNum)

    
    def SwitchBtnState(self, preview, select, maxnum):
        self.CheckBtnState('btn_review', preview, maxnum)
        self.CheckBtnState('btn_select', select, maxnum)

    
    def CheckBtnState(self, name, idx, maxidx):
        for i in xrange(3):
            btn = self.GetObject('%s%d' % (name, i))
            btn.SetShow(i < maxidx)
            btn.SetSelect(i == idx - 1)
            btn.SetZ(10)
        

    
    def SetBtnTip(self, name, txt):
        for i in xrange(3):
            btn = self.GetObject('%s%d' % (name, i))
            btn.m_TipsStr = '%s\xb2\xc4%s\xaeM\xa7\xa4\xc3M\xa4\xe8\xae\xd7' % (txt, [
                '\xa4@',
                '\xa4G',
                '\xa4T'][i])
            btn.m_TipsDirect = 2
        

    
    def OnPreViewSkill(self, iIdx):
        if self.m_CurViewIdx == iIdx:
            return None
        
        iCurPlan = self.GetMXRideInfoMgr().GetCurSkillPlan()
        iMaxPlan = self.GetMXRideInfoMgr().GetMaxSkillPlan()
        self.m_CurViewIdx = iIdx
        self.GetMXRideInfoMgr().SetPrvSkillPlan(iIdx)
        self.SwitchBtnState(iIdx, iCurPlan, iMaxPlan)
        self.RefreshDesc()
        self.RefreshGradeExpText()
        self.CheckBornImgShow()
        self.RefreshSkill()
        import dlgrideup
        dlgrideup.UpdateRide()

    
    def SelectRideSkill(self, iIdx):
        if self.m_SelectRide == iIdx:
            return None
        
        import commondialog
        iPrvPlan = self.GetMXRideInfoMgr().GetPrvSkillPlan()
        iCurPlan = self.GetMXRideInfoMgr().GetCurSkillPlan()
        iMaxPlan = self.GetMXRideInfoMgr().GetMaxSkillPlan()
        self.m_CurViewIdx = iIdx
        self.GetMXRideInfoMgr().SetPrvSkillPlan(iIdx)
        self.SwitchBtnState(iIdx, iCurPlan, iMaxPlan)
        self.RefreshDesc()
        self.RefreshGradeExpText()
        self.CheckBornImgShow()
        self.RefreshSkill()
        oDoSelect = misc.Functor(self.DoSelectRideSkill)
        oCancle = misc.Functor(self.CancleSelectRideSkill)
        dlg = commondialog.ShowMessageBox('\xa4\xc1\xb4\xab\xa7\xde\xaf\xe0\xa4\xe8\xae\xd7\xbb\xdd\xadn\xae\xf8\xaf\xd310\xb8U\xb2{\xaa\xf7\xa1A\xbdT\xa9w\xc4~\xc4\xf2\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (oDoSelect, oCancle))
        dlg.m_iIdx = iIdx
        dlg.m_iPrvPlan = iPrvPlan

    
    def DoSelectRideSkill(self, obj):
        import netride
        netride.C2SSelectRideInfo(obj.m_iIdx)
        self.SetSwitchRideSkill(True)

    
    def CancleSelectRideSkill(self, obj):
        iCurPlan = self.GetMXRideInfoMgr().GetCurSkillPlan()
        iMaxPlan = self.GetMXRideInfoMgr().GetMaxSkillPlan()
        self.m_CurViewIdx = obj.m_iPrvPlan
        self.GetMXRideInfoMgr().SetPrvSkillPlan(obj.m_iPrvPlan)
        self.SwitchBtnState(obj.m_iPrvPlan, iCurPlan, iMaxPlan)
        self.RefreshDesc()
        self.RefreshGradeExpText()
        self.CheckBornImgShow()
        self.RefreshSkill()
        self.SetSwitchRideSkill(False)

    
    def SetSwitchRideSkill(self, bStatus):
        self.m_bSWitchRideSkill = bStatus

    
    def RefreshPetEquip(self):
        self.m_EquipBoxes = []
        if self.m_CurViewIdx == -1:
            return None
        
        dAllEquipsInfo = self.GetMXRideInfoMgr().GetAllEquipInfo()
        self.DrawEquip(dAllEquipsInfo)

    
    def DrawEquip(self, dAllEquipsInfo):
        import netride
        self.m_EquipBoxes = []
        dPos2Name = {
            1: 'item1',
            2: 'item2' }
        dPos2Shape = {
            1: itemdefine.ID_ITEM_HORSE_DECORATE,
            2: itemdefine.ID_ITEM_HORSE_LIGHT }
        for iEquipPos in sorted(dPos2Name.keys()):
            if iEquipPos not in dAllEquipsInfo:
                dAllEquipsInfo[iEquipPos] = { }
                dAllEquipsInfo[iEquipPos]['iShape'] = dPos2Shape[iEquipPos]
                dAllEquipsInfo[iEquipPos]['sDesc'] = ''
                dAllEquipsInfo[iEquipPos]['iNum'] = 0
            
            dEquipInfo = dAllEquipsInfo[iEquipPos]
            (x, y, w, h) = self.GetLocData(dPos2Name[iEquipPos])
            sDesc = self.ChgEquipDesc(dEquipInfo['sDesc'], dEquipInfo['iNum'])
            oBox = CEquipBoxEx(self, iEquipPos, dEquipInfo['iShape'], sDesc, dEquipInfo['iNum'])
            (iBoxW, iBoxH) = oBox.GetSize()
            oBox.SetPos(x + (w - iBoxW) / 2, y + (h - iBoxH) / 2)
            self.m_EquipBoxes.append(oBox)
            if dEquipInfo['iNum'] > 0:
                netride.C2GSResetRideEquipment(iEquipPos)
                continue
        

    
    def ChgEquipDesc(self, sDesc, iNum):
        if not self.m_iCurSelRide:
            return sDesc
        
        iNeed = self.GetCurNeedNum()
        if iNum >= iNeed and '\xa1i\xb8\xcb\xb9\xa2\xae\xc4\xaaG\xa1j' in sDesc:
            iIdx = sDesc.find('\xa1i\xb8\xcb\xb9\xa2\xae\xc4\xaaG\xa1j')
            sDesc = sDesc[:iIdx] + '\xa1i\xb8\xcb\xb9\xa2\xae\xc4\xaaG\xa1j#B\xa4w\xbfE\xac\xa1#n'
        
        return sDesc

    
    def SetNotifyBox(self, sObjNameLst):
        self.m_NotifyBoxlst = []
        for iIdx, sObjName in enumerate(sObjNameLst):
            (x, y, w, h) = self.GetLocData(sObjName)
            oBox = interface.CNotifyBox(self, w, h, 0, 0, 11 + iIdx)
            oBox.SetPos(x, y)
            oBox.SetZ(-1)
            self.m_NotifyBoxlst.append(oBox)
        

    
    def GetCurNeedNum(self):
        iNum = ridedata.GetCurNeedNum(self.m_iCurSelRide)
        return iNum

    
    def GetRideRebthGrade(self):
        oPlan = self.GetMXRideInfoMgr().GetSkillPlan(self.m_CurViewIdx)
        if oPlan:
            iGrade = oPlan.GetRebirthGrade()
        else:
            iGrade = 0
        return iGrade

    
    def GetRideGrade(self):
        oPlan = self.GetMXRideInfoMgr().GetSkillPlan(self.m_CurViewIdx)
        if oPlan:
            return oPlan.GetGrade()
        else:
            return 0

    
    def GetRideExp(self):
        oPlan = self.GetMXRideInfoMgr().GetSkillPlan(self.m_CurViewIdx)
        if oPlan:
            return oPlan.GetExp()
        else:
            return 0

    
    def GetRideExpNext(self):
        oPlan = self.GetMXRideInfoMgr().GetSkillPlan(self.m_CurViewIdx)
        if oPlan:
            return oPlan.GetNxtExp()
        else:
            return 0

    
    def GetRideNormalLevel(self):
        return self.GetMXRideInfoMgr().GetNormalGrade()

    
    def CreateOtherDlg(self):
        self.m_SkillDlg = CRideSkillDlg(self, True)
        if not self.GetMXRideInfoMgr().IsOpenSkill():
            self.m_SkillDlg.SetShow(False)
        
        self.m_ItemDlg = CRideitem(self)
        self.m_ItemDlg.SetShow(False)

    
    def SwitchOtherDlgShow(self):
        if self.m_ItemDlg.GetShow():
            self.m_ItemDlg.SetShow(False)
        
        if self.GetMXRideInfoMgr().IsOpenSkill():
            self.m_SkillDlg.SetShow(True)
        

    
    def RefreshSkill(self):
        oModel = mdmxride.GetMXRideInfoMgr()
        oPlan = oModel.GetSkillPlan(oModel.GetPrvSkillPlan())
        self.m_SkillDlg.SetSkillPlan(oPlan)
        self.m_SkillDlg.updateskill()

    
    def SwitchItemDlgShow(self):
        self.m_SkillDlg.SetShow(False)
        self.m_ItemDlg.SetShow(not self.m_ItemDlg.GetShow())

    
    def SwitchSkillDlgShow(self):
        import mainmenu
        if not self.GetMXRideInfoMgr().IsOpenSkill() and not mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xb5\xa5\xaf\xc5\xb9F\xa8\xec60\xaf\xc5\xae\xc9\xa1A\xa5i\xb3q\xb9L\xa7\xa4\xc3M\xacD\xbe\xd4\xb8\xd1\xc2\xea\xa7\xa4\xc3M\xa7\xde\xaf\xe0')
            return None
        
        self.m_ItemDlg.SetShow(False)
        self.m_SkillDlg.SetShow(not self.m_SkillDlg.GetShow())

    
    def DelayRefreshRideLst(self):
        import timer
        if self.m_oDelayRefreshTimer:
            self.m_oDelayRefreshTimer.Release()
            self.m_oDelayRefreshTimer = None
        
        self.m_oDelayRefreshTimer = timer.Timer(0.1, self.RefreshRideLst)

    
    def RefreshRideLst(self):
        self.m_RideList = self.GetObject('lst_ride')
        self.m_RideList.Clear()
        for iRideType in [
            ridedefine.RIDE_TYPE_SPECIAL,
            ridedefine.RIDE_TYPE_JUNIOR,
            ridedefine.RIDE_TYPE_HIGHT,
            ridedefine.RIDE_TYPE_FLY,
            ridedefine.RIDE_TYPE_TMPFLY,
            ridedefine.RIDE_TYPE_MULTI,
            ridedefine.RIDE_TYPE_SPEFLY]:
            iShapeList = self.GetMXRideInfoMgr().GetOwnHorseShapeByType(iRideType)
            for iIdx, iShape in enumerate(iShapeList):
                oHorse = self.GetMXRideInfoMgr().GetHorse(iShape)
                sRideName = ridedata.GetRideName(iShape)
                oHorseItem = self.m_RideList.AddTextItem(sRideName)
                oHorseItem.m_iShape = iShape
                oHorseItem.m_iRideType = iRideType
                if iRideType == ridedefine.RIDE_TYPE_MULTI:
                    oHorseItem.m_AddBtn = wrapinterface.CButtonWithTips(oHorseItem, style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xd4\xf6\xbc\xd3.igs'), 0, 0, '\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa5i\xacd\xac\xdd\xa6h\xa4H\xa7\xa4\xc3M\xabH\xae\xa7', 0)
                    oHorseItem.m_AddBtn.SetLeftUpCB(misc.Functor(self.DoShowMultiRidePos))
                    interface.CenterRight(oHorseItem.m_AddBtn, offsetx = -2)
                    continue
                if iRideType == ridedefine.RIDE_TYPE_SPEFLY:
                    iRemainTime = oHorse.GetProp(oHorse.PROP_REMAIN_TIME, 0)
                    if iRemainTime > 0:
                        oHorseItem.m_ImgTips = CClickImage(oHorseItem, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 1000 + iShape, 0, 0)
                        interface.CenterRight(oHorseItem.m_ImgTips, offsetx = -2)
                    
                iRemainTime > 0
                if oHorse.GetProp(oHorse.PROP_REMAIN_TIME, 0):
                    oHorseItem.m_ImgTips = CClickImage(oHorseItem, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 2000 + iShape, 0, 0)
                    interface.CenterRight(oHorseItem.m_ImgTips, offsetx = -2)
                    continue
            
            if iRideType == ridedefine.RIDE_TYPE_SPEFLY and len(iShapeList) == 0 and self.CanExchangeXuanFuRide():
                oHorseItem = self.m_RideList.AddTextItem('')
                oHorseItem.m_iShape = None
                oHorseItem.m_iRideType = iRideType
                sFileName = style.GetPath('combdialog/\xb0\xb4\xc5\xa5/\xd4\xf6\xbc\xd3.igs')
                oHorseItem.m_ExchangeBtn = clickimage.CClickImage2(oHorseItem, sFileName, 51, 0, 0)
                interface.Center(oHorseItem.m_ExchangeBtn)
                oHorseItem.m_ImgXuanFuTips = CClickImage(oHorseItem, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 1000, 0, 0)
                interface.CenterRight(oHorseItem.m_ImgXuanFuTips, offsetx = -2)
                continue
        
        self.m_RideList.ResetItems()
        self.m_RideList.ResetScrollBar()
        self.SelDefaultItem()
        self.RefreshRideModeTxt()

    
    def CanExchangeXuanFuRide(self):
        oModel = self.GetMXRideInfoMgr()
        if not oModel.IsHaseHorse():
            return False
        
        iRideGradeCondition = self.GetRideGrade() >= 6
        iHeroGradeCondition = hero.GetProp('m_Grade', 0) >= 105
        if oModel.GetOwnHorseShapeByType(ridedefine.RIDE_TYPE_FLY) and iRideGradeCondition:
            pass
        return iHeroGradeCondition

    
    def RefreshRideModeTxt(self):
        oModel = self.GetMXRideInfoMgr()
        iMode = oModel.GetRideHorseType()
        iCurRide = oModel.GetRideHorseShape()
        for oItem in self.m_RideList.GetItems():
            if oItem.m_iShape == iCurRide:
                self.m_ActiveRideName = ridedata.GetRideName(iCurRide)
                if iMode == ridedefine.TYPE_RIDE_HORSE_FAIRY:
                    self.m_ActiveRideType = 1
                    sTxt = '\xba\xeb'
                elif iMode == ridedefine.TYPE_RIDE_HORSE_NOW:
                    self.m_ActiveRideType = 0
                    sTxt = '\xc3M'
                else:
                    self.m_ActiveRideType = 0
                    sTxt = ''
                self.m_RideModeTxt = interface.CTextObject(oItem, sTxt, interface.FontLT12_1, 16711680, 0)
                interface.TopLeft(self.m_RideModeTxt, offsetx = 2, offsety = 2)
                continue
        

    
    def OnListDoubleClick(self, msgid):
        iIdx = msgid - 101
        fCurTime = misc.Time()
        if hasattr(self, 'm_LeftUpTime') and hasattr(self, 'm_CurIdx') and self.m_CurIdx == iIdx:
            if fCurTime - self.m_LeftUpTime <= fCurTime - self.m_LeftUpTime:
                pass
            elif fCurTime - self.m_LeftUpTime < 0.5:
                self.SwitchRide(iIdx)
            
        
        self.m_LeftUpTime = fCurTime
        self.m_CurIdx = iIdx

    
    def OnSelectItem(self, iIdx, bCreateLink = True):
        import C_sys
        import key
        import copylinkobj
        import kuafulink
        if iIdx >= len(self.m_RideList.GetItems()):
            iIdx = 0
        
        oSelItem = self.m_RideList.GetItemByIndex(iIdx)
        if not oSelItem.m_iShape:
            return None
        
        self.m_iCurSelRide = oSelItem.m_iShape
        self.UpdatePhoto()
        self.RefreshPetEquip()
        self.RefreshDesc()
        self.RefreshGradeExpText()
        self.CheckBornImgShow()
        self.RefreshSkill()
        self.UpdateModeBtn()
        self.RefreshFairy(oSelItem.m_iRideType)
        if bCreateLink and C_sys.IsKeyDown(key.VK_SHIFT):
            sName = ridedata.GetRideName(oSelItem.m_iShape)
            copylinkobj.CreateCopyLink(kuafulink.CLinkRide.CLIENT_TYPE, self.m_CurViewIdx, sName, oSelItem.m_iRideType, 0, oSelItem.m_iShape)
        

    
    def ClearPhoto(self):
        self.m_RidePhoto = None

    
    def RefreshPhoto(self):
        self.UpdatePhoto()

    
    def UpdatePhoto(self, rideType = None):
        if not self.m_iCurSelRide:
            return None
        
        self.ClearPhoto()
        (iCharID, dDesc) = charpath.GetHeroShow()
        if 'track' in dDesc:
            del dDesc['track']
        
        oModel = self.GetMXRideInfoMgr()
        iShape = self.m_iCurSelRide
        oRide = oModel.GetHorse(iShape)
        if not oRide:
            return None
        
        bUseNew = charpath.GetResNewWithShapeDesc(iShape, dDesc)
        dDesc['horse'] = oRide.GetDesc(bUseNew)
        descinterface.SetHorseNewOldColorInfo(dDesc, oRide.GetNewColor(), oRide.GetOldColor())
        if self.IsFairyShow() and iShape in ridedefine.HORSE_SHAPE_2_FAIRY_ID:
            dDesc['fairy'][1] = [
                ridedefine.HORSE_SHAPE_2_FAIRY_ID[iShape],
                oModel.GetHorseFairyColor(iShape)]
            if 'horse' in dDesc:
                del dDesc['horse']
            
        else:
            dDesc['fairy'][1] = [
                0,
                0]
        self.m_RidePhoto = walker.CreateFakeWalker(self, 0, iCharID, dDesc)
        self.m_RidePhoto.Enable(False)
        self.m_RidePhoto.SetZ(1)
        (x, y, w, h) = self.GetLocData('img_ride')
        self.m_RidePhoto.SetPos(x + w / 2, y + h - 20)

    
    def IsFairyShow(self):
        (charIdx, charDesc) = charpath.GetHeroShow()
        fairyDesc = charDesc.get('fairy', [
            [
                0,
                0],
            [
                0,
                0]])
        return fairyDesc[1][0] != 0

    
    def RefreshGradeExpText(self):
        if not self.m_iCurSelRide:
            return None
        
        color = interface.COLOR_5
        txtgrade = self.GetObject('txt_grade')
        txtexp = self.GetObject('txt_exp')
        grade = str(self.GetRideGrade())
        self.m_GradeText = combmacro.CreateTextWithObject(txtgrade, interface.CShadowText, grade, interface.FontLT14_3, color, 0, interface.ALIGN_MIDDLE)
        expnext = self.GetRideExpNext()
        if expnext == 0:
            tempstr = '--'
        else:
            tempstr = str(expnext)
        desc = str(self.GetRideExp()) + '/' + tempstr
        self.m_ExpText = combmacro.CreateTextWithObject(txtexp, interface.CShadowText, desc, interface.FontLT14_3, color, 0, interface.ALIGN_MIDDLE)
        self.ShowExpProcess()

    
    def ShowExpProcess(self):
        if not self.m_iCurSelRide:
            return None
        
        (x, y, w, h) = self.GetLocData('txt_exp')
        exp = self.GetRideExp()
        if exp == None:
            return None
        
        expnext = self.GetRideExpNext()
        if None == None == expnext:
            expnext = 1
        
        sImgPath = style.GetStr(self.GetDlgPath(), 'data_exp_progress')
        (iOffsetX, iOffsetY) = style.GetIntTuple(self.GetDlgPath(), 'data_exp_progress')
        iWidth = style.GetInt(self.GetDlgPath(), 'data_exp_progress')
        self.m_ExpProgress = wrapinterface.CProgress(self, w + iWidth, sImgPath)
        self.m_ExpProgress.SetPos(x + iOffsetX, y + iOffsetY)
        self.m_ExpProgress.SetRate(exp * 1000 / expnext)
        self.m_ExpProgress.SetZ(-1)

    
    def RefreshDesc(self):
        oModel = self.GetMXRideInfoMgr()
        oPlan = oModel.GetSkillPlan(self.m_CurViewIdx)
        if oPlan:
            self.ShowDesc(oPlan.GetDescString())
        else:
            self.ShowDesc(None)

    
    def ShowDesc(self, desc):
        import wrapui
        iOpen = self.GetMXRideInfoMgr().IsOpenSkill()
        iGrade = hero.GetProp('m_Grade')
        if iGrade >= 60 and not iOpen:
            desc = '#r\xb3q\xb9L#s(50,[\xa7\xa4\xc3M\xacD\xbe\xd4], 20, 1)\xa5i\xa5H\xb8\xd1\xc2\xea\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xa1A\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xb9F\xa8\xec55\xaf\xc5\xae\xc9\xa5\xcd\xae\xc4'
        elif iGrade < 60:
            desc = '#r#R\xb5\xa5\xaf\xc5\xb9F\xa8\xec60\xaf\xc5\xae\xc9\xa1A\xa5i\xb8\xd1\xc2\xea\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xa1A\xa5B\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xb9F\xa8\xec55\xaf\xc5\xae\xc9\xa5\xcd\xae\xc4#n'
        
        self.m_RideDesc = desc
        if not desc:
            self.m_Desc = None
            return None
        
        if self.m_iCurSelRide:
            txt = '\xa7\xa4\xc3M\xc3\xfe\xab\xac\xa1G %s%s' % (ridedata.GetRideName(self.m_iCurSelRide), self.m_RideDesc)
        else:
            txt = self.m_RideDesc
        if misc.g_ServerID not in g_OldServer and hero.g_Prop.m_GradeLimit < 55:
            txt += '#r%s\xaaA\xb0\xc8\xbe\xb9\xa1\xd955\xaf\xc5\xa1A\xb0\xd1\xa5[\xac\xa1\xb0\xca\xa5i\xc0\xf2\xb1o\xb8g\xc5\xe7#n' % style.GetStr(self.GetDlgPath(), 'data_desc_color')
            if iGrade >= 60 and iOpen:
                txt += '%s\xa1A\xa5B\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xa5\xcd\xae\xc4\xa8\xc3\xbcW\xa5[\xbe\xd4\xa4O#n' % style.GetStr(self.GetDlgPath(), 'data_desc_color')
            
        
        txt = interface.Replace(txt)
        (txt, _, self.m_LinkDct) = wrapui.ReplaceLink(txt)
        self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, txt, interface.FontLT14_3, interface.COLOR_4)

    
    def UpdateModeBtn(self):
        oModeBtn = self.GetObject('btn_mode')
        if not self.m_iCurSelRide:
            oModeBtn.SetText('\xbc\xd2\xa6\xa1')
            return None
        
        oModel = self.GetMXRideInfoMgr()
        if oModel.GetHaveHuaLing():
            if rideinterface.GetHorseType(self.m_iCurSelRide) == ridedefine.RIDE_TYPE_MULTI:
                if oModel.GetRideHorseShape() == self.m_iCurSelRide:
                    oModeBtn.SetText('\xa8\xab\xb8\xf4')
                else:
                    oModeBtn.SetText('\xc3M\xad\xbc')
            else:
                oModeBtn.SetText('\xbc\xd2\xa6\xa1')
        elif oModel.GetRideHorseShape() == self.m_iCurSelRide:
            oModeBtn.SetText('\xa8\xab\xb8\xf4')
        else:
            oModeBtn.SetText('\xc3M\xad\xbc')

    
    def RefreshFairy(self, iRideType):
        import netride
        if self.IsFairyShow() and iRideType in CRideDialog.ISFAIRYTYPE:
            netride.C2SGetFairyDesc(iRideType)
        

    
    def AddRide(self):
        self.DelayRefreshRideLst()

    
    def DelRide(self):
        self.RefreshRideLst()

    
    def SelDefaultItem(self):
        self.m_LeftUpTime = 0
        oModel = self.GetMXRideInfoMgr()
        iRideShape = oModel.GetRideHorseShape()
        if self.m_iCurSelRide:
            for oItem in self.m_RideList.GetItems():
                if oItem.m_iShape and oItem.m_iShape == self.m_iCurSelRide:
                    oItem.LeftUp()
                    return None
                    continue
            
        elif iRideShape:
            for oItem in self.m_RideList.GetItems():
                if oItem.m_iShape and oItem.m_iShape == iRideShape:
                    oItem.LeftUp()
                    return None
                    continue
            
        elif len(self.m_RideList.GetItems()) > 0:
            self.m_RideList.GetItemByIndex(0).LeftUp()
        

    
    def ActiveRide(self):
        if not self.m_iCurSelRide:
            return None
        
        iType = rideinterface.GetHorseType(self.m_iCurSelRide)
        UseHorse(self.m_iCurSelRide, iType)

    
    def SwitchRide(self, idx):
        if not self.m_iCurSelRide:
            return None
        
        mdmxride.SwitchRide(self.m_iCurSelRide)

    
    def OnLevelUp(self):
        import commondialog
        if not self.m_iCurSelRide:
            return None
        
        if self.m_CurViewIdx != self.m_SelectRide:
            func = misc.Functor(self.DoLevelUp)
            sNum = [
                '\xa4@',
                '\xa4G',
                '\xa4T'][self.m_CurViewIdx - 1]
            commondialog.ShowMessageBox('\xa7A\xb7\xed\xabe\xb9w\xc4\xfd\xaa\xba\xacO\xb2\xc4#R%s#n\xaeM\xa4\xe8\xae\xd7\xa1A\xa7A\xbdT\xa9w\xadn\xb9\xef\xb3o\xaeM\xa4\xe8\xae\xd7\xa4\xc9\xaf\xc5\xb6\xdc\xa1H' % sNum, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (func, None))
        else:
            self.DoLevelUp(self)

    
    def DoLevelUp(self, obj):
        import netride
        netride.C2SGetRecommend(mdmxride.GetMXRideInfoMgr().GetCurSkillPlan())
        netride.C2GSRideUp(self.m_CurViewIdx)

    
    def OnBuyRideExp(self):
        import commondialog
        import netride
        if self.m_CurViewIdx == self.m_SelectRide:
            netride.C2SButRideExp(self.m_CurViewIdx)
            return None
        
        oFunc = misc.Functor(self.DoBuyRideExp)
        sNum = [
            '\xa4@',
            '\xa4G',
            '\xa4T'][self.m_CurViewIdx - 1]
        dlg = commondialog.ShowMessageBox('\xa7A\xb7\xed\xabe\xb9w\xc4\xfd\xaa\xba\xacO\xb2\xc4#R%s#n\xaeM\xa4\xe8\xae\xd7\xa1A\xa7A\xbdT\xa9w\xadn\xac\xb0\xb3o\xaeM\xa4\xe8\xae\xd7\xc1\xca\xb6R\xa7\xa4\xc3M\xb8g\xc5\xe7\xb6\xdc\xa1H' % sNum, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (oFunc, None))
        dlg.m_Idx = self.m_CurViewIdx

    
    def DoBuyRideExp(self, obj):
        import netride
        netride.C2SButRideExp(obj.m_Idx)

    
    def DoShowMultiRidePos(self):
        import multihorsemgr
        import hero
        if multihorsemgr.IsOnTeamateRide(hero.GetRealID()):
            usermacro.PROMPT_MSG('\xb1z\xa5\xbf\xa6b\xad\xbc\xc3M\xa6h\xa4H\xa7\xa4\xc3M\xa1A\xbc\xc8\xae\xc9\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xa6\xb9\xbe\xde\xa7@')
            return None
        
        iCurRide = self.GetMXRideInfoMgr().GetRideHorseShape()
        if not iCurRide and not (self.m_iCurSelRide) and iCurRide != self.m_iCurSelRide or rideinterface.GetHorseType(iCurRide) != ridedefine.RIDE_TYPE_MULTI:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xad\xbc\xc3M\xb8\xd3\xa7\xa4\xc3M\xa1A\xb5M\xab\xe1\xa6A\xb6i\xa6\xe6\xa6\xec\xb8m\xac\xdb\xc3\xf6\xbe\xde\xa7@')
            return None
        
        import mainmenu
        if mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xb8\xd3\xbe\xde\xa7@')
            return None
        
        import nethero
        nethero.C2SOpenMultiHorseUI(1)

    
    def OnPopMenu(self, iIdx):
        if misc.IsNationFightServer():
            usermacro.PROMPT_MSG('\xaa\xa7\xc5Q\xc1\xc9\xaaA\xa4\xa3\xa5i\xa7\xef\xc5\xdc\xa7\xa4\xc3M\xaa\xac\xbaA')
            return None
        
        if iIdx >= len(self.m_RideList.GetItems()):
            return None
        
        oItem = self.m_RideList.GetItemByIndex(iIdx)
        if oItem:
            oItem.LeftUp()
        
        if not hero.InMultiHorse():
            self.ShowPopMenu(iIdx)
        

    
    def ShowPopMenu(self, iIdx):
        if not self.m_iCurSelRide:
            return None
        
        iRideType = rideinterface.GetHorseType(self.m_iCurSelRide)
        import hero
        if hero.IsInEventPoint():
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xa4\xa3\xa4\xb9\xb3\\\xa4\xc1\xb4\xab\xa7\xa4\xc3M\xbc\xd2\xa6\xa1\xa1A\xbd\xd0\xa8\xec\xb3\xb0\xa6a\xa4W\xa6A\xb8\xd5')
            return None
        
        tAllMenu = [
            ('\xa8\xab\xb8\xf4', misc.Functor(ChangeWalkMode, iRideType), '\xa5u\xa6\xb3\xa6b\xabD\xa8\xab\xb8\xf4\xaa\xac\xbaA\xa4U\xa1A\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xae\xc4\xaaG\xa4~\xb7|\xa5\xcd\xae\xc4'),
            ('\xc3M\xad\xbc', misc.Functor(ChangeRideMode, iRideType, self.m_iCurSelRide), None),
            ('\xba\xeb\xc6F', misc.Functor(ChangeSpriteMode, iRideType, self.m_iCurSelRide), None)]
        tAllMenu = self.DealWithMenu(tAllMenu)
        import cursor
        (cx, cy) = cursor.GetPos()
        self.m_PopMenu = wrapinterface.CMenuList(interface.MainPanel, tAllMenu, cx, cy)
        self.m_PopMenu.m_Type = iRideType

    
    def DealWithMenu(self, tAllMenu):
        oModel = self.GetMXRideInfoMgr()
        iCurRide = oModel.GetRideHorseShape()
        iMode = oModel.GetRideHorseType()
        sRemoveSet = set()
        if iCurRide:
            if self.m_iCurSelRide == iCurRide:
                if iMode == ridedefine.TYPE_RIDE_HORSE_NOW:
                    sRemoveSet.add('\xc3M\xad\xbc')
                elif iMode == ridedefine.TYPE_RIDE_HORSE_FAIRY:
                    sRemoveSet.add('\xba\xeb\xc6F')
                
            else:
                sRemoveSet.add('\xa8\xab\xb8\xf4')
        else:
            sRemoveSet.add('\xa8\xab\xb8\xf4')
        if oModel.GetHaveHuaLing():
            if rideinterface.GetHorseType(self.m_iCurSelRide) == ridedefine.RIDE_TYPE_MULTI:
                sRemoveSet.add('\xba\xeb\xc6F')
            
        else:
            sRemoveSet.add('\xba\xeb\xc6F')
        for tInfo in tAllMenu[:]:
            if tInfo[0] in sRemoveSet:
                tAllMenu.remove(tInfo)
                continue
        
        return tAllMenu

    
    def OnEquipInfoChange(self):
        self.RefreshPetEquip()

    
    def OnSkillPlanInfoChange(self, iPlanID, sKey):
        if iPlanID != self.m_CurViewIdx:
            return None
        
        if sKey == ridedefine.KEY_RIDE_GRADE:
            self.RefreshGrade()
        elif sKey == ridedefine.KEY_RIDE_REBIRTH_GRIDE:
            self.RefreshGrade()
        elif sKey == ridedefine.KEY_RIDE_EXP:
            self.RefreshGrade()
        elif sKey == ridedefine.KEY_RIDE_STORAGE_EXP:
            self.RefreshGrade()
        elif sKey == ridedefine.KEY_RIDE_DESC:
            self.RefreshDesc()
        elif sKey == ridedefine.KEY_RIDE_SKILL:
            self.RefreshSkill()
        

    
    def OnMaxSkillPlanChange(self, iMax):
        self.SetRideInfoType()

    
    def OnCurSkillPlanChange(self, iCur):
        self.SetRideInfoType()
        self.SetSwitchRideSkill(False)

    
    def OnUpdateRideHorseType(self, iType):
        self.RefreshRideModeTxt()
        self.UpdateModeBtn()

    
    def OnUpdateRideHorseShape(self, iShape):
        self.RefreshRideModeTxt()
        self.UpdateModeBtn()

    
    def RefreshBtnGradeDown(self):
        iGrade = self.GetRideGrade()
        if not iGrade:
            self.SetShowObject('btn_lvdown', False)
        elif not self.GetObject('btn_lvdown').GetShow():
            self.SetShowObject('btn_lvdown', True)
        

    
    def OnEnter(self, iMsgID):
        if iMsgID in (22, 24):
            sText = None
            rebthgrade = self.GetRideRebthGrade()
            grade = self.GetRideGrade()
            normLevel = self.GetRideNormalLevel()
            if self.m_iCurSelRide and rebthgrade > 0 and grade <= rebthgrade:
                sText = '\xad\xab\xa5\xcd\xae\xc9\xb5\xa5\xaf\xc5\xa1G#Y$grade#n(\xa7\xa4\xc3M\xa4\xc9\xaf\xc5\xa8\xec#Y$grade#n\xae\xc9\xa1A\xad\xab\xa5\xcd\xb8g\xc5\xe7\xa5[\xa6\xa8\xae\xc4\xaaG\xb1N\xae\xf8\xa5\xa2)'.replace('$grade', str(rebthgrade))
            elif normLevel:
                if grade < normLevel:
                    sText = '\xae\xda\xbe\xda\xb7\xed\xabe\xaaA\xb0\xc8\xbe\xb9\xb5\xa5\xaf\xc5\xa1A\xa7\xa4\xc3M\xb5\xa5\xaf\xc5\xa7C\xa9\xf3#Y%d#n\xae\xc9\xa1A\xa5i\xc0\xf2\xb1o\xa4@\xa9w\xaa\xba\xa7\xa4\xc3M\xb8g\xc5\xe7\xa5[\xa6\xa8\xae\xc4\xaaG' % normLevel
                
            
            if sText:
                self.m_Tips = wrapinterface.CTextTips(None, -1, sText, interface.FontLT12_1, direct = 1)
                self.m_Tips.SetOwner(self.m_TipsGrade)
            else:
                self.m_Tips = None
        elif iMsgID == 10:
            oState = netstate.GetState(netstatedefine.ID_COMBINE_COMPENSATION_STATE)
            iCombineCompensationHorseExp = 0
            if oState:
                iCombineCompensationHorseExp = oState.GetCombineCompensationHorseExp(self.GetMXRideInfoMgr().GetCurSkillPlan())
            
            oPlan = self.GetMXRideInfoMgr().GetSkillPlan(self.m_CurViewIdx)
            sTxt = ''
            if oPlan:
                sExp = str(oPlan.GetStorageExp())
                if oPlan.GetStorageExp() > 0:
                    sTxt = '\xb7\xed\xabe\xa7\xa4\xc3M\xc0x\xb3\xc6\xb8g\xc5\xe7\xa1G#Y%s' % sExp
                
            
            if iCombineCompensationHorseExp > 0:
                sTxt = '%s#n#r\xa6X\xaaA\xa7\xa4\xc3M\xc0x\xb3\xc6\xb8g\xc5\xe7\xa1G#Y%s' % (sTxt, iCombineCompensationHorseExp)
            
            sTxt = '%s#n#r\xc2I\xc0\xbb\xb9\xcf\xbc\xd0\xacd\xac\xdd\xa7\xa4\xc3M\xb8g\xc5\xe7\xa4\xb6\xb2\xd0' % sTxt
            self.m_Tips = wrapinterface.CTextTips(None, -1, sTxt, interface.FontLT12_1, direct = 1)
        elif iMsgID in (11, 12):
            sText = self.GetEnterTxt(iMsgID)
            self.m_Tips = wrapinterface.CTextTips(self, -1, sText, interface.FontLT14_3, direct = 1)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 2000:
            iHorseShape = iMsgID - 1000
            sText = '\xa7I\xb4\xab\xad\xb8\xa6\xe6\xafS\xae\xed\xa7\xa4\xc3M\xa1]\xbd\xac\xb5\xd8\xa1B\xa4\xd1\xe6\xa2\xa1B\xaf}\xaa\xc5\xa1^'
            oHorse = self.GetMXRideInfoMgr().GetHorse(iHorseShape)
            if oHorse:
                iRemainTime = oHorse.GetProp(oHorse.PROP_REMAIN_TIME, 0)
                iNowTime = misc.GetServerTime()
                iDaySecond = 86400
                iRemainSecond = iRemainTime - iNowTime
                iRemainDay = iRemainSecond / iDaySecond
                if iRemainDay < 0:
                    iRemainDay = 0
                    sTimeTxt = '#Y%d#n\xa4\xd1' % iRemainDay
                elif iRemainDay == 0:
                    iRemainDay = iRemainSecond / 3600
                    sTimeTxt = '#Y%d#n\xa4p\xae\xc9' % iRemainDay
                else:
                    iRemainDay = iRemainDay
                    sTimeTxt = '#Y%d#n\xa4\xd1' % iRemainDay
                sText = '\xa7\xa4\xc3M\xb3\xd1\xbel\xae\xc9\xb6\xa1\xa1G%s' % sTimeTxt
            
            self.m_Tips = wrapinterface.CTextTips(self, -1, sText, interface.FontLT14_3, direct = 1)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 3000:
            iHorseShape = iMsgID - 2000
            oHorse = self.GetMXRideInfoMgr().GetHorse(iHorseShape)
            if oHorse:
                iRemainTime = oHorse.GetProp(oHorse.PROP_REMAIN_TIME, 0)
                iNowTime = misc.GetServerTime()
                iRemainTimeLst = time.localtime(iRemainTime)
                sText = 1000 if iNowTime < iRemainTime else '\xb1z\xaa\xba\xad\xb8\xa6\xe6\xa8t\xb2\xce\xa7K\xb6O\xc5\xe9\xc5\xe7\xa4w\xa8\xec\xb4\xc1'
                self.m_Tips = wrapinterface.CTextTips(self, -1, sText, interface.FontLT14_3, direct = 1)
            
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def GetEnterTxt(self, msgid):
        iNum = self.GetCurNeedNum()
        if msgid == 11:
            sItemName = '\xc2_\xaa\xf7\xa5O'
            sDecorate = '\xb8\xcb\xb9\xa2'
        else:
            sItemName = '\xa5_\xb7\xa5\xa5\xfa'
            sDecorate = '\xa5\xfa\xb5\xd8'
        sTxt = '\xa1i%s\xae\xc4\xaaG\xa1j\xa1]\xa5\xbc\xbfE\xac\xa1\xa1^#r\xa8\xcf\xa5\xce#Y%d#n\xa5\xf3%s\xb8H\xa4\xf9\xab\xe1\xa5i\xbfE\xac\xa1\xa7\xa4\xc3M%s#r' % (sDecorate, iNum, sItemName, sDecorate)
        sTxt += '\xa1i\xa5[\xa6\xa8\xae\xc4\xaaG\xa1j\xa1]\xa5\xbc\xbfE\xac\xa1\xa1^#r\xbcW\xa5[\xb0\xaa\xaf\xc5\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xc0\xf2\xb1o\xb2\xc4\xa4G\xaa\xfe\xc4\xdd\xa7\xde\xaf\xe0\xaa\xba\xb7\xa7\xb2v#Y5%%#n#r\xa1]\xbfE\xac\xa1\xbb\xdd\xadn\xa6A\xa8\xcf\xa5\xce#Y30#n\xa5\xf3%s\xb8H\xa4\xf9\xa1^' % sItemName
        return sTxt

    
    def OnItemEnter(self, it):
        if it.m_iRideType == ridedefine.RIDE_TYPE_MULTI:
            oRide = self.GetMXRideInfoMgr().GetHorse(it.m_iShape)
            if not oRide:
                return None
            
            iRemainTime = oRide.GetProp(oRide.PROP_REMAIN_TIME)
            if iRemainTime:
                self.m_ItemTips = wrapinterface.CTextTips(None, 130, '\xb8\xd3\xa7\xa4\xc3M\xb1N\xa9\xf3%d\xa4\xe9\xab\xe1\xa8\xec\xb4\xc1' % iRemainTime, interface.FontLT12_1, direct = 0, owner = it)
            
        

    
    def OnItemLeave(self, it):
        self.m_ItemTips = None

    
    def CloseWindow(self):
        global g_SkillTips
        self.SetShow(False)
        g_SkillTips = None
        import dlgrideup
        dlgrideup.CloseWindow()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.ActiveRide()
        elif msgid == 2:
            self.OnLevelUp()
        elif msgid == 3:
            self.CloseWindow()
        elif msgid == 4:
            self.SwitchItemDlgShow()
        elif msgid == 5:
            self.SwitchSkillDlgShow()
        elif msgid == 6:
            self.OnBuyRideExp()
        elif msgid == 7:
            import dlgtool_lycos_new
            dlgtool_lycos_new.ShowHelper('\xa7\xa4\xc3M\xa8t\xb2\xce')
        elif msgid in (8, 151):
            import appearancehorseview
            iRideHorseShape = mdmxride.GetMXRideInfoMgr().GetRideHorseShape()
            appearancehorseview.ShowHorseDlg(iShape = iRideHorseShape, bReloadToRow = True)
        elif msgid == 9:
            import netopenui
            netopenui.C2SOpenHorseDownGradeDlg()
        elif msgid in (40, 41, 42):
            self.OnPreViewSkill(msgid - 39)
        elif msgid in (45, 46, 47):
            self.SelectRideSkill(msgid - 44)
        elif msgid < msgid:
            pass
        elif msgid < 200:
            self.OnSelectItem(msgid - 101)
            self.OnListDoubleClick(msgid)
        elif msgid == 10 or msgid == interface.RIGHT_BUTTON_MESSAGE + 10:
            import dlgtool_lycos_new
            dlgtool_lycos_new.ShowHelper('\xa7\xa4\xc3M\xb8g\xc5\xe7')
        elif interface.RIGHT_BUTTON_MESSAGE + 100 < msgid:
            idx = msgid - interface.RIGHT_BUTTON_MESSAGE - 101
            self.OnPopMenu(idx)
        



class CRideInfoDlg(combdialog.CCombDialog):
    s_DialogPath = 'dialog/ride/dlgrideinfo.dlg'
    
    def __init__(self, desc, charidx):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, self.s_DialogPath)
        self.m_RidePhoto = None
        self.m_oSkillPlan = None
        self.m_dDesc = desc
        self.m_iCharidx = charidx
        self.m_iSelectHorseShape = descinterface.GetHorseID(desc)
        self.m_SkillDlg = CRideSkillDlg(self, False)
        self.InitDlg(desc, charidx)

    
    def InitDlg(self, dDesc, iCharIdx):
        self.SetRideInfoType()
        (x, y) = style.GetIntTuple('dialog/ride/dlgrideinfo.dlg', 'data_pos')
        self.SetPos(x, y)
        self.CreateGradeTips()
        self.CreatePhoto(dDesc, iCharIdx)
        self.SetPvHorseBtnShow()

    
    def SetPvHorseBtnShow(self):
        if self.m_iSelectHorseShape in chardefine.MULTI_HORSE:
            bShow = True
        else:
            bShow = False
        self.SetShowObject('txtbtn_mutiplayer', bShow)

    
    def UpdateSkillDlg(self):
        self.m_SkillDlg.updateskill()

    
    def SetSkillPlan(self, oSkillPlan):
        self.m_oSkillPlan = oSkillPlan
        self.m_SkillDlg.SetSkillPlan(oSkillPlan)

    
    def SetRideInfoType(self):
        oModel = mdmxride.GetMXRideInfoMgr()
        self.m_CurViewIdx = oModel.GetPrvSkillPlan()
        self.m_SelectRide = oModel.GetCurSkillPlan()

    
    def CreateGradeTips(self):
        (x, y, w, h) = self.GetLocData('txt_grade1')
        self.m_TipsGrade1 = interface.CNotifyBox(self, w, h, 0, 0, 21)
        self.m_TipsGrade1.SetPos(x, y)
        self.m_TipsGrade1.Topmost()
        (x, y, w, h) = self.GetLocData('txt_grade')
        self.m_TipsGrade = interface.CNotifyBox(self, w, h, 0, 0, 22)
        self.m_TipsGrade.SetPos(x, y)
        self.m_TipsGrade.Topmost()

    
    def CreatePhoto(self, desc, charidx):
        
        try:
            desc.pop('track')
        except KeyError:
            pass

        fairyLst = ridedata.GetFairyList()
        if 'horse' in desc and 'fairy' in desc and len(desc['fairy']) > 1 and desc['fairy'][1][0] in fairyLst:
            rideID = desc['horse'][0]
            if rideID:
                iFairy = ridedata.GetData(rideID)['fairyid']
                desc['fairy'][1][0] = iFairy
                desc['fairy'][1][1] = GetFairyPal()
            
            desc.pop('horse')
        
        import multihorsemgr
        desc = multihorsemgr.TransformSpeHorse(desc)
        self.m_RidePhoto = walker.CFakeRole(self, 0, charidx, desc)
        self.m_RidePhoto.Enable(False)
        (x, y, w, h) = self.GetLocData('img_ride')
        self.m_RidePhoto.SetPos(x + w / 2, y + h - 20)

    
    def OnEnter(self, obj):
        pass

    
    def OnLeave(self, obj):
        pass

    
    def ShowDesc(self, desc):
        import wrapui
        desc = interface.Replace(desc)
        (txt, _, self.m_LinkDct) = wrapui.ReplaceLink(desc)
        self.m_Desc = combmacro.CRICHTEXT(interface.CRichTextObject, 'desc', self, txt, interface.FontLT14_3, interface.COLOR_4)

    
    def ShowExp(self, exp):
        objname_show = (('txt_grade1', exp >= 0), (self.m_TipsGrade1, exp >= 0), ('txt_grade', exp <= 0), (self.m_TipsGrade, exp <= 0))
        for objname, isshow in objname_show:
            if isinstance(objname, str):
                obj = self.GetObject(objname)
            else:
                obj = objname
            obj.SetShow(isshow)
        
        if exp >= 0:
            self.m_GradeText = combmacro.CreateTextWithObject(self.GetObject('txt_grade1'), interface.CShadowText, str(self.m_oSkillPlan.GetGrade()), interface.FontLT14_3, interface.COLOR_5, 0, interface.ALIGN_MIDDLE)
            iNxtExp = self.m_oSkillPlan.GetNxtExp()
            if iNxtExp == 0:
                tempstr = '--'
            else:
                tempstr = str(iNxtExp)
            self.m_ExpText = combmacro.CreateTextWithObject(self.GetObject('txt_exp'), interface.CShadowText, str(self.m_oSkillPlan.GetExp()) + '/' + tempstr, interface.FontLT14_3, interface.COLOR_5, 0, interface.ALIGN_MIDDLE)
            iOffy = style.GetInt('dlgride.CRideInfoDlg', 'txt_offy')
            (x, y) = self.m_ExpText.GetPos()
            self.m_ExpText.SetPos(x, y + iOffy)
            self.ShowExpProcess()
        

    
    def ShowExpProcess(self):
        if not self.m_oSkillPlan:
            return None
        
        (x, y, w, h) = self.GetLocData('txt_exp')
        exp = self.m_oSkillPlan.GetExp()
        next = self.m_oSkillPlan.GetNxtExp()
        if next == 0:
            next = 1
        
        sDlgName = 'dialog/ride/dlgrideinfo.dlg'
        sImgPath = style.GetStr(sDlgName, 'data_exp_progress')
        (iOffsetX, iOffsetY) = style.GetIntTuple(sDlgName, 'data_exp_progress')
        iWidth = style.GetInt(sDlgName, 'data_exp_progress')
        self.m_ExpProgress = wrapinterface.CProgress(self, w + iWidth, sImgPath)
        self.m_ExpProgress.SetPos(x + iOffsetX, y + iOffsetY)
        self.m_ExpProgress.SetRate(exp * 1000 / next)
        self.m_ExpProgress.SetZ(-1)

    
    def LeftUp(self):
        combdialog.CCombDialog.LeftUp(self)
        import cursor
        if hasattr(self, 'm_LinkDct') and self.m_LinkDct:
            (x, y) = cursor.GetPos()
            (rx, ry) = self.m_Desc.GetScreenPos()
            clickID = self.m_Desc.ClickID(x - rx, y - ry)
            if clickID in self.m_LinkDct:
                self.m_LinkDct[clickID].OnLeftUp()
            
        

    
    def DrawPetEquip(self, equips):
        self.m_EquipBoxes = []
        pos2obj = {
            1: 'item1',
            2: 'item2' }
        for data in equips:
            if len(data) == 4:
                (pos, shape, desc, num) = data
            else:
                (pos, shape, desc) = data
                num = 1
            if pos not in (1, 2):
                continue
            
            obj = self.GetObject(pos2obj[pos])
            (x, y) = obj.GetPos()
            (w, h) = obj.GetSize()
            box = CEquipBox(self, pos, shape, desc, num)
            (iw, ih) = box.GetSize()
            box.SetPos(x + (w - iw) / 2, y + (h - ih) / 2)
            self.m_EquipBoxes.append(box)
        

    
    def OnMessage(self, msgid):
        global g_RideInfoDlg
        if msgid == 3:
            g_RideInfoDlg = None
        elif msgid == 4:
            import appearanceridepv
            appearanceridepv.OpenAutoSelectRidePreviewExDlg(self.m_iCharidx, self.m_dDesc)
        



class CRideUpInfoDlg(CRideInfoDlg):
    s_DialogPath = 'dialog/ride/dlgrideupinfo.dlg'
    
    class CRideClickBox(interface.CBoxObject, interface.CClickObject):
        
        def __init__(self, parent, w, h, color = 0, alpha = 256, msgid = 0):
            interface.CBoxObject.__init__(self, parent, w, h, color, alpha)
            interface.CClickObject.__init__(self, msgid)
            self.m_MsgID = msgid

        
        def Enter(self):
            self.GetParent().Enter1(self.m_MsgID)

        
        def Leave(self):
            
            try:
                parent = self.GetParent()
            except SystemError:
                return None

            if not parent:
                return None
            
            parent.Leave1()


    
    def __init__(self, desc, charidx):
        CRideInfoDlg.__init__(self, desc, charidx)

    
    def InitDlg(self, dDesc, iCharIdx):
        self.m_SkillIcons = []
        self.m_SkillTxt = []
        self.m_SkillClicks = []
        self.SetPos(150, 100)
        self.CreateGradeInfo()
        self.CreateImageTips()
        self.CreateRidePhoto(dDesc, iCharIdx)

    
    def CreateRidePhoto(self, desc, charidx):
        
        try:
            desc.pop('track')
        except KeyError:
            pass

        fairyLst = ridedata.GetFairyList()
        if 'horse' in desc and 'fairy' in desc and len(desc['fairy']) > 1 and desc['fairy'][1][0] in fairyLst:
            rideID = desc['horse'][0]
            if rideID:
                iFairy = ridedata.GetData(rideID)['fairyid']
                desc['fairy'][1][0] = iFairy
                desc['fairy'][1][1] = GetFairyPal()
            
            desc.pop('horse')
        
        self.m_RidePhoto = walker.CFakeRole(self, 0, charidx, desc)
        tempimg = self.GetObject('img_ride')
        (x, y) = tempimg.GetPos()
        (w, h) = tempimg.GetSize()
        self.m_RidePhoto.SetPos(x + w / 2, y + h - 20)

    
    def CreateGradeInfo(self):
        (x, y, w, h) = self.GetLocData('txt_grade1')
        self.m_TipsGrade1 = interface.CNotifyBox(self, w, h, 0, 0, 21)
        self.m_TipsGrade1.SetPos(x, y)
        self.m_TipsGrade1.Topmost()
        (x, y, w, h) = self.GetLocData('txt_grade')
        self.m_TipsGrade = interface.CNotifyBox(self, w, h, 0, 0, 22)
        self.m_TipsGrade.SetPos(x, y)
        self.m_TipsGrade.Topmost()

    
    def CreateImageTips(self):
        (x, y) = self.GetObject('loc_Tips').GetPos()
        obj = clickimage.CClickImage(self, style.GetPath('\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe.igs'), 10, x, y)
        self.m_ImgTips = obj

    
    def OnEnter(self, msgid):
        txt = None
        if msgid == 10:
            txt = '\xc2I\xc0\xbb\xacd\xb8\xdf\xa7\xa4\xc3M\xa7\xde\xaf\xe0\xa4\xb6\xb2\xd0'
        
        if txt:
            self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
        

    
    def OnLeave(self, msgid):
        self.m_Tips = None

    
    def Enter1(self, msgid):
        global g_SkillTips
        idx = msgid - 100
        skillid = idx
        g_SkillTips = CSkillTips(skillid, 0, self.m_oSkillPlan)

    
    def Leave1(self):
        global g_SkillTips
        if g_SkillTips:
            g_SkillTips = None
        

    
    def ShowDesc(self, desc):
        pass

    
    def RefreshUpSkills(self, skills):
        skillIcon = self.GetObject('skill_iocn')
        for i in range(4):
            skillIcon.m_Imagess[i].skillid = 0
        
        (mx, my) = skillIcon.GetPos()
        mi = 0
        si = 1
        for i, skill in enumerate(skills):
            if skill / 100 < 4:
                tempi = mi
                mi += 2
            else:
                tempi = si
                si += 2
            (x, y) = skillIcon.m_Imagess[tempi].GetPos()
            (w, h) = skillIcon.m_Imagess[tempi].GetSize()
            skillIcon.m_Imagess[tempi].skillid = skill
            (offx, offy) = style.GetIntTuple(self.GetDlgPath(), 'data_skill_icon_offset')
            tempiocn = CSkillIcon(self, mx + x + offx, my + y + offy, skill, 0)
            tempiocn.SetSkillInfo(self.m_oSkillPlan)
            tempiocn.SetZ(0)
            tempclick = self.CRideClickBox(self, w, h, 0, 0, 100 + skill)
            tempclick.SetPos(mx + x, my + y)
            tempclick.SetZ(5)
            import ridedatainfo
            temptxt = interface.CRichTextObject(self, 85, interface.FontLT14_3, ridedatainfo.DATA[skill]['name'], interface.COLOR_1)
            temptxt.SetPos(mx + x + 70, my + y + 28)
            self.m_SkillTxt.append(temptxt)
            self.m_SkillClicks.append(tempclick)
            self.m_SkillIcons.append(tempiocn)
        

    
    def OnMessage(self, msgid):
        global g_RideInfoDlg
        if msgid == 3:
            g_RideInfoDlg = None
        elif msgid == 10:
            import dlgtool_lycos_new
            dlgtool_lycos_new.ShowHelper('\xa7\xa4\xc3M\xa7\xde\xaf\xe0')
        



def ShowSwitch():
    global g_SkillTips
    if not ShowPrepare():
        return None
    
    if g_DlgRide.GetShow():
        g_DlgRide.Topmost()
        g_DlgRide.SwitchOtherDlgShow()
        g_DlgRide.SelDefaultItem()
    else:
        g_DlgRide.m_RideId2Exp = { }
        g_SkillTips = None
        import dlgrideup
        dlgrideup.CloseWindow()
    import sound
    import sounddefine
    if g_DlgRide.GetShow():
        sound.Play(sounddefine.PATH_OPENUI_SOUND)
    else:
        sound.Play(sounddefine.PATH_CLOSEUI_SOUND)


def ShowPrepare():
    global g_DlgRide
    import dlgladderrank
    if misc.IsNationFightServer():
        import dlgcharacterpreinstall
        dlgcharacterpreinstall.ShowZuoqi()
        return False
    
    if dlgladderrank.IsInRoom():
        usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
        return False
    
    if not (hero.g_Hero) or not mdmxride.GetMXRideInfoMgr().IsHaseHorse():
        return False
    
    import hidecatcat
    if hidecatcat.IsHideGameRunning():
        return False
    
    import acteyectrl
    if acteyectrl.GetActEyeCtrl().IsBegin():
        return False
    
    import ratio
    if ratio.Is1024x768():
        (x, y) = (180, 140)
    elif ratio.Is1366x768():
        (x, y) = (300, 140)
    elif ratio.Is1366x708():
        x = 300
        y = ratio.GetYBy1366x768(140)
    elif ratio.Is1280x960():
        x = 214
        y = ratio.GetYBy1280x960(140)
    else:
        (x, y) = style.GetIntTuple('dlgride.ShowPrepare', 'data_pos')
    if g_DlgRide is None:
        g_DlgRide = CRideDialog()
    
    g_DlgRide.SetShow(not g_DlgRide.GetShow())
    g_DlgRide.SetPos(x, y)
    g_DlgRide.SelDefaultItem()
    return True


def GetDlgRide():
    return g_DlgRide


def AddRide():
    if g_DlgRide:
        g_DlgRide.AddRide()
    


def RemoveRide():
    if not g_DlgRide:
        return None
    
    g_DlgRide.DelRide()


def UpdateRide():
    import dlgrideup
    dlgrideup.UpdateRide()


def RefreshByMulti():
    if g_DlgRide and g_DlgRide.GetShow():
        g_DlgRide.SelDefaultItem()
    


def GetLinkType():
    return g_LinkType


def SetLinkType(iType):
    global g_LinkType
    g_LinkType = iType


def GetLinkEquipLst(iType):
    return g_Type2EquipLst.get(iType)


def SetLinkEquipLst(iType, equipLst):
    g_Type2EquipLst[iType] = equipLst


def GetLinkDesc(iType):
    return g_Type2LinkDesc.get(iType)


def SetLinkDesc(iType, rideDesc):
    g_Type2LinkDesc[iType] = rideDesc


def SetFairyPal(iPal):
    global g_FairyPal
    g_FairyPal = iPal


def GetFairyPal():
    return g_FairyPal


def ChangeWalkMode(iRideType, *args):
    import netride
    netride.C2SChangeRideMode(iRideType, 1)


def ChangeRideMode(iRideType, iRideShape, *args):
    import netride
    netride.C2SChangeRideMode(iRideType, 2, iRideShape)


def ChangeSpriteMode(iRideType, iRideShape, *args):
    import netride
    netride.C2SChangeRideMode(iRideType, 3, iRideShape)
