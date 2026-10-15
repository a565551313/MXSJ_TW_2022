# pycdc 交叉复核产物 · script.fls entry 4020
# co_filename(原始)='script/dialog/dlgnewpetrefine.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4020.pyc (Python 2.5)

import combdialog
import dlgpet
import interface
import item
import misc
import pet
import slot
import style
import trainpetdefines
import trainpetinterface
import ui
import usermacro
import wrapinterface
import dlgshenmoisland
BUYTYPE_MXGOLD = 1
BUYTYPE_XIANLIU = 2
g_PetRefineDlg = None
g_PetRefineMgr = None
g_bCanPetRefine = True

def ModuleReset():
    global g_PetRefineDlg, g_PetRefineMgr
    g_PetRefineDlg = None
    g_PetRefineMgr = None

PET_PROPS1 = (('m_Name', 'name'), ('m_Grade', 'grade'))
PET_APTI = (('Ability_Attack', 'txt_apti', 0), ('Ability_Con', 'txt_apti', 1), ('Ability_Speed', 'txt_apti', 2), ('Ability_Defense', 'txt_apti2', 0), ('Ability_Magic', 'txt_apti2', 1))
PET_ATTR = ('att_abi',)
PET_UPD = ('Update_Flag', 'Update_Max')
REFINEITEM1 = [
    70662,
    70663]
REFINEITEM2 = [
    25670,
    25671,
    25673,
    25913,
    25929]

def Show():
    global g_PetRefineDlg
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.ShowLianYaoDlg()
    elif not g_PetRefineDlg:
        g_PetRefineDlg = CPetRefineDlg()
    
    SetRefineItem()
    g_PetRefineDlg.SetShow(True)
    g_PetRefineDlg.Topmost()
    import dlgitem
    import dlgpetitem
    petid = getattr(dlgpetitem.g_PetItem, 'm_CurrPetID', None)
    if not petid:
        petid = getattr(dlgitem.g_ItemDialog, 'm_CurrPetID', None)
    
    if petid:
        g_PetRefineDlg.m_PID = petid
        g_PetRefineDlg.ChoosePetByID(petid)
    


def ResetPetRefine():
    global g_bCanPetRefine
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcpetrefine
        dlgpcpetrefine.ResetPetRefine()
    else:
        g_bCanPetRefine = True


def IsAllow():
    if g_PetRefineDlg:
        return True
    
    return False


def RefreshPet(petobj):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoRefreshPet(petobj)
    elif petobj and IsAllow():
        g_PetRefineDlg.RefreshPet(petobj)
    


def RefreshPetInfo(pid, extraZZ = 0):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoRefreshPetInfo(pid, 0)
    elif IsAllow():
        g_PetRefineDlg.RefreshPetInfo(pid, 0)
    


def RefreshPetSkill(petid):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoRefreshPetSkill(petid)
    elif IsAllow():
        g_PetRefineDlg.RefreshPetSkill(petid)
    


def SetRefineItem(itemid = None):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoSetRefineItem(itemid)
    elif itemid is None:
        it = item.FindItem(70662)
    else:
        it = item.GetItem(itemid)
    if IsAllow():
        iShape = getattr(it, 'm_Shape', 70662)
        if iShape in REFINEITEM1:
            g_PetRefineDlg.Active(3)
            g_PetRefineDlg.SetRefineItem(it, iShape)
        elif iShape in (25405,):
            g_PetRefineDlg.Active(4)
            g_PetRefineDlg.SetItemChoose(it, 1)
        elif iShape in REFINEITEM2:
            g_PetRefineDlg.Active(5)
            g_PetRefineDlg.SetItemChoose(it, 2)
        
    


def IsOwnedSkill(name):
    import petskill
    if g_PetRefineDlg.m_PetObj is not None:
        for sicon in g_PetRefineDlg.m_SkillIcons:
            if sicon.m_txtHf is not None:
                continue
            
            skname = petskill.GetData(sicon.m_SkillID)['name']
            if skname == name:
                return True
                continue
        
    
    return False


def ShowColorSelect(pid, shape, color1, color2, iType):
    print pid, '\xb5o\xb0e\xb9L\xa8\xd3\xaa\xbaid---------------------'
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoShowColorSelect(pid, shape, color1, color2, iType)
    elif IsAllow():
        g_PetRefineDlg.ShowColorSelect(pid, shape, color1, color2, iType)
    


def RefreshItem():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoRefreshItem()
    elif IsAllow():
        g_PetRefineDlg.RefreshRefineItem()
    


def RefreshBuy(isBuy):
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoRefreshBuy(isBuy)
    elif getattr(g_PetRefineDlg, 'm_ChkGold', None):
        g_PetRefineDlg.m_ChkGold.SetSelect(isBuy)
    


def GetPetRefineMgr():
    global g_PetRefineMgr
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcpetrefine
        return dlgpcpetrefine.GetPetRefineMgr()
    elif not g_PetRefineMgr:
        g_PetRefineMgr = CPetRefineMgr()
    
    return g_PetRefineMgr


def CloseBookDlg():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        dlgpetcenter.LianYaoCloseBookDlg()
    elif g_PetRefineDlg:
        g_PetRefineDlg.m_oSkillBookDlg = None
    


def IsNewSkillBookDlg():
    import dlgpetcenter
    if dlgpetcenter.IsTest():
        import dlgpcpetrefine
        return dlgpcpetrefine.IsNewSkillBookDlg()
    else:
        return True


class CPetRefineMgr(slot.ISignalSubject):
    SS_BookPrice = 'BookPrice(dPrice)'
    SS_OwnBook = 'OwnBook(dOwnBook)'
    
    def __init__(self):
        self.m_dPrice = { }
        self.m_dOwnBook = { }
        self.ssInit()

    
    def UpdateBookPrice(self, dPrice):
        if not self.m_dPrice:
            self.m_dPrice = dPrice
        else:
            for iSkillID, iPrice in dPrice.items():
                self.m_dPrice[iSkillID] = iPrice
            
        self.ssEmit(self.SS_BookPrice, self.m_dPrice)

    
    def UpdateOwnBook(self):
        import petskill
        self.m_dOwnBook = { }
        dBook = item.GetItemsByShape(25405)
        for itemobj in dBook.values():
            sExtName = itemobj.GetExtName()
            iSkillID = petskill.GetSkillID(sExtName)
            if iSkillID is not None:
                if iSkillID in self.m_dOwnBook:
                    self.m_dOwnBook[iSkillID].append(itemobj.m_ID)
                    continue
                
                self.m_dOwnBook[iSkillID] = [
                    itemobj.m_ID]
                continue
        
        self.ssEmit(self.SS_OwnBook, self.m_dOwnBook)

    
    def GetBookPrice(self):
        return self.m_dPrice

    
    def GetOwnBook(self):
        return self.m_dOwnBook



class CPetIcon(interface.CImageBox):
    
    def __init__(self, parent, fname, path, msgid):
        interface.CImageBox.__init__(self, parent, fname, path, msgid)
        import ui
        (iOffsetX, iOffsetY) = style.GetPos('dlgnewpetrefine.CPetIcon', 'select_img_offset')
        self.m_SelBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
        self.m_SelBox.SetPos(iOffsetX, iOffsetY)
        self.m_SelBox.SetShow(False)
        self.m_PosBox = ui.CImage(self, style.GetPath('common/select.igs'), interface.UIPath)
        self.m_PosBox.SetPos(iOffsetX, iOffsetY)
        self.m_PosBox.SetShow(False)

    
    def SetPetName(self, sName):
        self.m_PetName = sName

    
    def Enter(self):
        interface.CImageBox.Enter(self)
        self.m_PosBox.SetShow(True)
        if getattr(self, 'm_PetName', None):
            import wrapinterface
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, self.m_PetName, interface.FontLT14_3, direct = 1)
            self.m_TipsObj.SetOwner(self)
        

    
    def Leave(self):
        interface.CImageBox.Leave(self)
        self.m_PosBox.SetShow(False)
        self.m_TipsObj = None

    
    def LeftUp(self):
        if self.m_MsgID:
            par = self.GetParent().GetParent()
            if par and hasattr(par, 'OnMessage'):
                par.OnMessage(self.m_MsgID)
            
        

    
    def Select(self, sel):
        self.m_SelBox.SetShow(sel)

    
    def RightUp(self):
        pass

    
    def MouseWheelDown(self, p):
        par = self.GetParent().GetParent()
        if par and isinstance(par, combdialog.CList):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent().GetParent()
        if par and isinstance(par, combdialog.CList):
            par.MouseWheelUp(p)
        



class CItemInterface(interface.CClickBox):
    
    def __init__(self, parent, w, h, color = 0, alpha = 256, msgid = 0):
        interface.CClickBox.__init__(self, parent, w, h, color, alpha, msgid)
        self.m_ItemObj = None
        self.m_ItemImg = None
        self.m_InfoTxt = None

    
    def SetItem(self, itemobj):
        self.m_ItemObj = itemobj
        if itemobj is None:
            self.m_ItemImg = None
        else:
            self.m_ItemImg = item.CreateItem44Image(self, itemobj.m_Shape, 0)

    
    def GetItem(self):
        return self.m_ItemObj

    
    def SetInfoTxt(self, txt):
        self.m_InfoTxt = interface.CRichTextObject(self, 50, interface.FontLT14_3, txt, 0)
        self.m_InfoTxt.SetPos(28, 35)
        self.m_InfoTxt.SetZ(10)

    
    def SetTipsTxt(self, txt):
        self.m_TipsText = txt

    
    def Enter(self):
        interface.CClickBox.Enter(self)
        if hasattr(self, 'm_TipsText'):
            import wrapinterface
            self.m_Tips = wrapinterface.CTextTips(None, -1, self.m_TipsText, interface.FontLT14_3, direct = 1)
        

    
    def Leave(self):
        interface.CClickBox.Leave(self)
        if hasattr(self, 'm_TipsText'):
            self.m_Tips = None
        



class CSkillIcon(dlgpet.CSkillIcon):
    
    def LeftUp(self):
        par = self.GetParent()
        par.LeftUp()

    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if hasattr(par, 'MouseWheelDown'):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if hasattr(par, 'MouseWheelUp'):
            par.MouseWheelUp(p)
        



class CSkillInterface(interface.CClickBox):
    
    def __init__(self, parent, w, h, color = 0, alpha = 256, msgid = 0):
        interface.CClickBox.__init__(self, parent, w, h, color, alpha, msgid)
        self.m_ItemObj = None
        self.m_SkillObj = None
        self.m_SkillID = None

    
    def SetItem(self, itemobj):
        self.m_ItemObj = itemobj

    
    def SetSkill(self, skillID):
        if skillID:
            skillObj = CSkillIcon(self, 3, 3, skillID % 10000, skillID > 10000)
            self.m_SkillObj = skillObj
            self.m_SkillID = skillID % 10000
        else:
            self.m_SkillObj = None
            self.m_SkillID = None

    
    def GetSkillID(self):
        return self.m_SkillID

    
    def GetItem(self):
        return self.m_ItemObj



class CRefineItemChoose(combdialog.CCombDialog):
    
    class CInterfaceItem(item.CInterfaceItem):
        s_ShowExtItem = [
            25405]
        
        def SetItem(self, it):
            item.CInterfaceItem.SetItem(self, it)
            extName = None
            if it and it.m_Shape in self.s_ShowExtItem:
                extName = it.GetExtName()
            
            self.CreateExtName(extName)

        
        def CreateExtName(self, name):
            self.m_ExtNameTextLst = []
            if name:
                txtLst = []
                if len(name) < 8:
                    txtLst = [
                        name]
                
                if len(name) in (8, 10):
                    txtLst = [
                        name[:4],
                        name[4:]]
                elif len(name) >= 12:
                    txtLst = [
                        name[:6],
                        name[6:]]
                
                hSpace = 28
                color = 65280
                if IsOwnedSkill(name):
                    color = 16711680
                
                for txt in reversed(txtLst):
                    obj = interface.CTextObject(self.m_ItemImg, txt, interface.FontLT12E_1, color)
                    (w, h) = obj.GetSize()
                    obj.SetPos((44 - w) + 2, hSpace)
                    obj.SetZ(1000)
                    hSpace -= h
                    self.m_ExtNameTextLst.append(obj)
                
            

        
        def SetItemByPos(self, pos):
            pass

        
        def Refresh(self, pos):
            pass

        
        def LeftUp(self):
            
            try:
                dlg = self.GetParent().GetParent().GetParent()
            except:
                return None

            dlg.OnMessage(self.m_MsgID)

        
        def RightUp(self):
            pass

        
        def MouseWheelDown(self, p):
            par = self.GetParent().GetParent()
            if par and isinstance(par, combdialog.CList):
                None.combdialog.MouseWheelDown(p)
            

        
        def MouseWheelUp(self, p):
            par = self.GetParent().GetParent()
            if par and isinstance(par, combdialog.CList):
                par.MouseWheelUp(p)
            


    
    def __init__(self, shapeLst, iType):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/petrefineuseitem.dlg')
        self.m_ShapeLst = shapeLst
        self.m_Type = iType
        self.InitData()
        self.Refresh()
        interface.Center(self)
        self.Capture(1, 0)

    
    def InitData(self):
        self.m_List = self.GetObject('lst_item')
        self.m_ItemBox = self.GetObject('img_item')
        self.m_Data = []
        if self.m_List and self.m_ItemBox:
            for i in range(5):
                (x, y) = self.m_ItemBox.m_Imagess[i].GetPos()
                self.m_Data.append((x, y))
            
        
        if self.GetObject('lst_item'):
            self.GetObject('lst_item').ShowLine(False)
        

    
    def Refresh(self):
        self.SetItemLst()
        self.m_List.SetZ(self.m_ItemBox.GetZ() + 1)
        if len(self.m_Items) <= 20:
            self.CreateItemsList(4)
        else:
            self.CreateItemsList()

    
    def SetItemLst(self):
        itemLst = []
        for iShape in self.m_ShapeLst:
            itemLst.extend(item.GetItemsByShape(iShape).values())
        
        self.m_Items = itemLst

    
    def CreateItemsList(self, iNum = 0):
        if not self.m_List and self.m_ItemBox and self.m_Data:
            return None
        
        self.m_List.Clear()
        self.m_ItemInterfaces = []
        num = None if iNum == 0 else iNum
        for i in xrange(num):
            idx = i * 5
            self.AddListItem(self.m_Items[idx:idx + 5], idx)
        

    
    def AddListItem(self, itemLst, msgid):
        it = interface.CBoxObject(self.m_List, self.m_List.m_ItemWidth, self.m_List.m_ItemHeight, 0, 0)
        it.m_IconBG = []
        for i in xrange(5):
            imgClass = None if interface.IsNewStyle() else interface.CImagesObject
            bgObj = imgClass(it, self.m_ItemBox.m_FileName, interface.UIPath)
            bgObj.SetPos(self.m_Data[i][0], self.m_Data[i][1])
            bgObj.SetZ(1)
            it.m_IconBG.append(bgObj)
        
        for idx, itemobj in enumerate(itemLst):
            iif = CRefineItemChoose.CInterfaceItem(it, self.m_Data[idx][0], self.m_Data[idx][1], 101 + idx + msgid)
            iif.SetItem(itemobj)
            iif.SetZ(2)
            self.m_ItemInterfaces.append(iif)
        
        self.m_List.AddItem(it)
        self.m_List.ResetItems()
        self.m_List.ResetScrollBar()

    
    def DealCheats(self, itemobj):
        import itemdata
        name = itemdata.GetData(itemobj.m_Shape)[0]
        if '\xc5]\xc3~\xadn\xb3Z' in name and hasattr(itemobj, 'm_InfoExt') and itemobj.m_InfoExt:
            name = itemobj.m_InfoExt[:itemobj.m_InfoExt.find('#')]
        
        if IsOwnedSkill(name):
            usermacro.PROMPT_MSG('%s\xa4w\xb8g\xbe\xc7\xb7|#R%s#n\xa4F!' % (g_PetRefineDlg.m_PetObj.m_Prop.m_Name, name))
            return True
        
        return False

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.SetShow(False)
        elif msgid < msgid:
            pass
        elif msgid < 200:
            idx = msgid - 101
            if self.m_ItemInterfaces and len(self.m_ItemInterfaces) > idx:
                iif = self.m_ItemInterfaces[idx]
                itemobj = iif.GetItem()
                if self.DealCheats(itemobj):
                    return None
                
                if g_PetRefineDlg:
                    g_PetRefineDlg.SetItemChoose(itemobj, self.m_Type)
                    self.SetShow(False)
                
            
        



class CItemBox(interface.CImageCheckBox):
    
    def __init__(self, parent, filename, x, y, msgid = 0, width = 0, height = 0):
        interface.CImageCheckBox.__init__(self, parent, filename, x, y, msgid = msgid, width = width, height = height)

    
    def SetSkillIcon(self, iSkillid, iScale = 1):
        import style
        self.m_oSkillIcon = CSkillIcon(self, 3, 3, iSkillid % 10000, iSkillid > 10000)
        self.m_oSkillIcon.SetScale(iScale)
        tPos = style.GetIntTuple('dlgnewpetrefine.CItemBox', 'pos_oSkillIcon')
        self.m_oSkillIcon.SetPos(*tPos)

    
    def SetTxt(self, sTxt, font = None, color = None):
        if font == None:
            font = interface.FontLT12_1
        
        if color == None:
            color = interface.COLOR_1
        
        tPos = (55, 7)
        self.m_oTxt = interface.CTextObject(self, sTxt, font, color)
        self.m_oTxt.SetPos(*tPos)

    
    def SetClickCB(self, oFunc):
        self.m_oClickFunc = oFunc

    
    def SetRollCB(self, oFunc):
        self.m_oRollFunc = oFunc

    
    def LeftUp(self):
        bSelect = self.m_oClickFunc(self.m_MsgID)
        if bSelect:
            self.SetCheck(True)
        

    
    def MouseWheelDown(self, p):
        self.m_oRollFunc(p)

    
    def MouseWheelUp(self, p):
        self.m_oRollFunc(-p)



class CSkillBookDlg(combdialog.CCombDialog):
    
    def __init__(self, iPetID = None):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/summonrefine/petrefineuseitem.dlg')
        self.m_iPetID = iPetID
        self.m_iBuyType = BUYTYPE_MXGOLD
        self.m_iPage = 0
        self.Init()

    
    def Init(self):
        import hero
        import misc
        import commoncb
        oMgr = GetPetRefineMgr()
        self.m_dPrice = oMgr.GetBookPrice()
        self.m_dOwnBook = oMgr.GetOwnBook()
        self.InitBuyType()
        oPropitem = hero.g_Name2PropItem['m_ShenWuBi']
        oPropitem.AddRefreshCallbackWithID('UpdateMXGold', self.RefreshMxGold)
        commoncb.RegistCB(commoncb.REPUTE, self, 'RefreshXianLiu')
        self.SetBtnSelect()
        self.SwitchShow()
        oMgr.ssConnect(oMgr.SS_BookPrice, misc.Functor(self.RefreshPrice))
        oMgr.ssConnect(oMgr.SS_OwnBook, misc.Functor(self.RefreshOwnBook))

    
    def RefreshPrice(self, dPrice):
        self.m_dPrice = dPrice
        self.SortSkillBook()

    
    def RefreshOwnBook(self, dBook):
        self.m_dOwnBook = dBook
        self.SortSkillBook()

    
    def RefreshMxGold(self):
        import misc
        import hero
        sMXGold = misc.ChangeMoney(str(hero.GetProp('m_ShenWuBi')))
        self.m_oMxGold.SetText(sMXGold)

    
    def RefreshXianLiu(self, dRepute):
        import misc
        sXunzhang = misc.ChangeMoney(str(dRepute[16][1]))
        sShouhun = misc.ChangeMoney(str(dRepute[17][1]))
        self.m_oXunzhang.SetText(sXunzhang)
        self.m_oShouhun.SetText(sShouhun)

    
    def SetSelectPetID(self, ID):
        self.m_iPetID = ID
        self.SortSkillBook()

    
    def SetCloseCB(self, oFunc):
        self.m_CloseFunc = oFunc

    
    def SetSelectSkillCB(self, oFunc):
        self.m_SelectFunc = oFunc

    
    def InitBuyType(self):
        import misc
        import hero
        import dlgrepute
        import combmacro
        self.m_oBuyMode = combmacro.CTEXT(interface.CTextObject, 'buymode', self, '\xb9\xda\xb7Q\xb9\xf4', interface.FontLT14_3, interface.COLOR_346, align = interface.ALIGN_CENTER_MIDDLE)
        sMXGold = misc.ChangeMoney(str(hero.GetProp('m_ShenWuBi')))
        self.m_oMxGold = combmacro.CTEXT(interface.CTextObject, 'mxgold', self, sMXGold, interface.FontLT14_3, interface.COLOR_3)
        sXunzhang = misc.ChangeMoney(str(dlgrepute.GetRepute(16)[1]))
        sShouhun = misc.ChangeMoney(str(dlgrepute.GetRepute(17)[1]))
        self.m_oXunzhang = combmacro.CTEXT(interface.CTextObject, 'xunzhang', self, sXunzhang, interface.FontLT14_3, interface.COLOR_3)
        self.m_oShouhun = combmacro.CTEXT(interface.CTextObject, 'shouhun', self, sShouhun, interface.FontLT14_3, interface.COLOR_3)

    
    def SortSkillBook(self):
        if not hasattr(self, 'm_dPrice') or not hasattr(self, 'm_dOwnBook'):
            return None
        
        import skillbookdata
        import copy
        LowPriceList = sorted(self.m_dPrice.items(), cmp = (lambda x, y: cmp(x[1], y[1])))
        HighPriceList = sorted(self.m_dPrice.items(), cmp = (lambda x, y: cmp(x[1], y[1])), reverse = True)
        self.m_dSkillBook = { }
        petskillList = []
        oPet = pet.GetPet(self.m_iPetID)
        if oPet:
            petskillList = oPet.m_Skills
        
        for i in xrange(4):
            dData = copy.deepcopy(skillbookdata.GetData(i))
            Pricelist = HighPriceList
            if i == 0:
                Pricelist = LowPriceList
            
            self.m_dSkillBook[i] = []
            for iSkillid, iPrice in Pricelist:
                for v in dData.values():
                    if v['skillid'] == iSkillid:
                        v['price'] = iPrice
                        if v['skillid'] in petskillList:
                            v['price'] = '\xa4w\xbe\xc7\xb7|'
                        
                        self.m_dSkillBook[i].append(v)
                        continue
                
            
            for v in dData.values():
                if v['\xb5\xb2\xb4\xb9\xbfn\xa4\xc0'] == None:
                    self.m_dSkillBook[i].append(v)
                    continue
            
        
        for idx, DataList in self.m_dSkillBook.items():
            TempList = []
            for dValue in DataList:
                if dValue['skillid'] in self.m_dOwnBook.keys():
                    dValue['price'] = '\xa4w\xbe\xd6\xa6\xb3%d\xa5\xbb' % len(self.m_dOwnBook[dValue['skillid']])
                    TempList.insert(0, dValue)
                    continue
                TempList.append(dValue)
            
            self.m_dSkillBook[idx] = TempList
        
        self.ShowSkillBook()

    
    def GetUIData(self):
        import style
        PosList = []
        (x, y, _, _) = self.GetLocData('skilllist')
        for i in xrange(1, 3):
            (x1, y1, w, h) = self.GetLocData('cfm_box%d' % i)
            PosList.append((x1 - x, y1 - y, w, h))
            self.GetObject('cfm_box%d' % i).SetShow(False)
        
        oList = self.GetObject('skilllist')
        oList.ShowLine(False)
        oList.Clear()
        fname = self.GetObject('cfm_box1').m_FileName
        (width, hight) = self.GetObject('cfm_box1').GetSize()
        sMxGoldfname = style.GetStr(self.GetDlgPath(), 'smxgoldfname')
        return (oList, PosList, fname, width, hight, sMxGoldfname)

    
    def ShowSkillBook(self):
        if not hasattr(self, 'm_dSkillBook'):
            return None
        
        import math
        (oList, PosList, fname, width, hight, sMxGoldfname) = self.GetUIData()
        SkillBookList = []
        for dValue in self.m_dSkillBook[self.m_iPage]:
            if dValue.has_key('price'):
                SkillBookList.append(dValue)
                continue
        
        iLen = len(SkillBookList)
        iGroups = int(math.ceil(iLen / 2))
        for j in xrange(iGroups):
            self.CreateBox(j, SkillBookList, oList, PosList, fname, width, hight, sMxGoldfname)
        
        oList.ResetItems()
        oList.ResetScrollBar()
        self.SwitchShowPrice()

    
    def CreateBox(self, iGroup, SkillBookList, oList, PosList, fname, width, hight, sMxGoldfname):
        import combmacro
        import misc
        import style
        oBox = interface.CBoxObject(oList, oList.m_ItemWidth, oList.m_ItemHeight, 0, 0)
        oBox.m_IconBGList = []
        oBox.m_GoldImgList = []
        oBox.m_GoldTxtList = []
        oBox.m_XianLiuImgList = []
        oBox.m_XianLiuTxtList = []
        oBox.m_DescList = []
        for i in xrange(2):
            iKey = iGroup * 2 + i
            if iKey >= len(SkillBookList):
                continue
            
            dSkill = SkillBookList[iKey]
            iSkillid = dSkill.get('skillid')
            sSkillName = dSkill.get('name')
            Price = dSkill.get('price')
            sXun = misc.ChangeMoney(str(dSkill['\xb3\xd4\xb3\xb9\xbfn\xa4\xc0']))
            sShou = misc.ChangeMoney(str(dSkill['\xb5\xb2\xb4\xb9\xbfn\xa4\xc0']))
            iPoint = style.GetInt(self.GetDlgPath(), 'offx_mxgoldimg')
            offsetX = i * iPoint
            if type(Price) == int:
                oMxGoldImg = combmacro.CIMAGE(oBox, sMxGoldfname)
                y = style.GetInt(self.GetDlgPath(), 'y_mxgoldimg')
                MxGoldImgPos = (56 + offsetX, y)
                oMxGoldImg.SetPos(*MxGoldImgPos)
                oBox.m_GoldImgList.append(oMxGoldImg)
                oMxGoldTxt = interface.CTextObject(oBox, misc.ChangeMoney(str(Price)), interface.FontLT12_1, interface.COLOR_1)
                (x, y) = style.GetIntTuple(self.GetDlgPath(), 'pos_mxgoldtxt')
                MxGoldTxtPos = (x + offsetX, y)
                oMxGoldTxt.SetPos(*MxGoldTxtPos)
                oBox.m_GoldTxtList.append(oMxGoldTxt)
                oXunImg = combmacro.CIMAGE(oBox, 'emote/1000.igs')
                oXunImg.SetPos(60 + offsetX, 34)
                oShouImg = combmacro.CIMAGE(oBox, 'emote/1001.igs')
                oShouImg.SetPos(100 + offsetX, 34)
                oBox.m_XianLiuImgList.append((oXunImg, oShouImg))
                oXunTxt = interface.CTextObject(oBox, sXun, interface.FontLT12_1, interface.COLOR_1)
                (x, y) = style.GetIntTuple(self.GetDlgPath(), 'pos_xuntxt')
                XunTxtPos = (x + offsetX, y)
                oXunTxt.SetPos(*XunTxtPos)
                oShouTxt = interface.CTextObject(oBox, sShou, interface.FontLT12_1, interface.COLOR_1)
                (x, y) = style.GetIntTuple(self.GetDlgPath(), 'pos_shoutxt')
                ShouTxtPos = (x + offsetX, y)
                oShouTxt.SetPos(*ShouTxtPos)
                oBox.m_XianLiuTxtList.append((oXunTxt, oShouTxt))
            
            if type(Price) == str:
                color = 15565312
                if Price == '\xa4w\xbe\xc7\xb7|':
                    color = interface.COLOR_84
                
                oDesc = interface.CTextObject(oBox, Price, interface.FontLT12_1, color)
                oDesc.SetPos(60 + offsetX, 34)
                oBox.m_DescList.append(oDesc)
            
            oBtnImg = CItemBox(oBox, fname, PosList[i][0], PosList[i][1], msgid = iSkillid, width = width, height = hight)
            oBtnImg.SetSkillIcon(iSkillid, 0.78)
            oBtnImg.SetTxt(sSkillName)
            oBtnImg.SetClickCB(misc.Functor(self.OnSelectSkill))
            oBtnImg.SetRollCB(misc.Functor(self.OnRoll))
            oBox.m_IconBGList.append(oBtnImg)
        
        oList.AddItem(oBox)

    
    def SwitchShowPrice(self):
        oList = self.GetObject('skilllist')
        bShowMxGold = True
        if self.m_iBuyType == BUYTYPE_XIANLIU:
            bShowMxGold = False
        
        if oList.m_Items:
            for oBox in oList.m_Items:
                iLen = len(oBox.m_GoldImgList)
                for i in xrange(iLen):
                    oBox.m_GoldImgList[i].SetShow(bShowMxGold)
                    oBox.m_GoldTxtList[i].SetShow(bShowMxGold)
                    oBox.m_XianLiuImgList[i][0].SetShow(not bShowMxGold)
                    oBox.m_XianLiuImgList[i][1].SetShow(not bShowMxGold)
                    oBox.m_XianLiuTxtList[i][0].SetShow(not bShowMxGold)
                    oBox.m_XianLiuTxtList[i][1].SetShow(not bShowMxGold)
                
            
        

    
    def SwitchShow(self):
        import style
        txt = '\xb9\xda\xb7Q\xb9\xf4'
        tPos = style.GetIntTuple(self.GetDlgPath(), 'pos_obuymode')
        if self.m_iBuyType == BUYTYPE_XIANLIU:
            txt = '\xa5l\xb3\xea\xc3~\xbfn\xa4\xc0'
            tPos = style.GetIntTuple(self.GetDlgPath(), 'pos1_obuymode')
        
        self.m_oBuyMode.SetText(txt)
        self.m_oBuyMode.SetPos(*tPos)
        dUIName = {
            BUYTYPE_MXGOLD: ('mxgold_img', 'mxgold'),
            BUYTYPE_XIANLIU: ('xunzhang_img', 'xunzhang', 'shouhun_img', 'shouhun') }
        for tUIName in dUIName.values():
            for sName in tUIName:
                self.GetObject(sName).SetShow(False)
            
        
        for sName in dUIName[self.m_iBuyType]:
            self.GetObject(sName).SetShow(True)
        
        if self.m_iBuyType == BUYTYPE_MXGOLD:
            self.m_oMxGold.SetShow(True)
            self.m_oXunzhang.SetShow(False)
            self.m_oShouhun.SetShow(False)
        else:
            self.m_oMxGold.SetShow(False)
            self.m_oXunzhang.SetShow(True)
            self.m_oShouhun.SetShow(True)

    
    def SwitchBuyType(self):
        if self.m_iBuyType == BUYTYPE_MXGOLD:
            self.m_iBuyType = BUYTYPE_XIANLIU
        else:
            self.m_iBuyType = BUYTYPE_MXGOLD
        if hasattr(self, 'm_iSelectSkillID'):
            self.OnSelectSkill(self.m_iSelectSkillID, bChange = False)
        
        self.SwitchShow()
        self.SwitchShowPrice()

    
    def SetBtnSelect(self):
        dBtnName = {
            4: 'diji',
            5: 'gaoji',
            6: 'zhongji',
            7: 'teshu' }
        for objname in dBtnName.values():
            self.GetObject(objname).SetSelect(False)
        
        objname = dBtnName[self.m_iPage + 4]
        self.GetObject(objname).SetSelect(True)

    
    def OnSelectSkill(self, iSkillID, bChange = True):
        SpecialSkillList = [
            562]
        self.m_iSelectSkillID = iSkillID
        oList = self.GetObject('skilllist')
        if bChange:
            for oBox in oList.m_Items:
                iLen = len(oBox.m_IconBGList)
                for i in xrange(iLen):
                    oBox.m_IconBGList[i].SetCheck(False)
                
            
        
        oPet = pet.GetPet(self.m_iPetID)
        if oPet:
            import petdata
            PetSkillList = oPet.m_Skills
            iCarryGrade = petdata.GetData(oPet.GetProp('m_Shape'))['carry_grade']
            if not pet.IsShenShou(oPet.m_BirthKey):
                pass
            bShenShou = pet.IsXianShou(oPet.m_BirthKey)
            if iSkillID in PetSkillList:
                usermacro.PROMPT_MSG('\xb8\xd3\xa7\xde\xaf\xe0\xa4w\xbe\xc7\xb7|')
                return False
            
            if not bShenShou and iSkillID in SpecialSkillList and iCarryGrade < 85:
                usermacro.PROMPT_MSG('\xa5u\xaf\xe0\xb9\xef\xb0\xd1\xbe\xd4\xb5\xa5\xaf\xc5\xa1\xd985\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xa8\xcf\xa5\xce\xa1]\xaf\xab\xc3~\xa1B\xa5P\xc3~\xa4\xa3\xa8\xfc\xad\xad\xa8\xee\xa1^')
                return False
            
        
        iPrice = 0
        if self.m_iBuyType == BUYTYPE_MXGOLD and iSkillID in self.m_dPrice:
            iPrice = self.m_dPrice[iSkillID]
        
        self.m_SelectFunc(iSkillID, iPrice)
        return True

    
    def OnRoll(self, p):
        oBar = self.GetObject('skilllist').m_VScrollBar
        bp = oBar.GetPos()
        oBar.SetBarPos(bp + p)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.m_CloseFunc()
        
        if msgid in (2, 3):
            self.SwitchBuyType()
        
        if msgid in (4, 5, 6, 7):
            self.m_iPage = msgid - 4
            self.ShowSkillBook()
            self.SetBtnSelect()
        



class CPetRefineDlg(combdialog.CCombDialog):
    s_Type2Tips = {
        0: '\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xacV\xa6\xe2\xa4\xe8\xae\xd7',
        1: '\xa6\xb3\xa5\xbc\xbf\xef\xbe\xdc\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa1A\xbdT\xbb{\xa9\xce\xa9\xf1\xb1\xf3\xab\xe1\xa1A#r\xa4~\xaf\xe0\xa5\xcd\xa6\xa8\xb7s\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7' }
    
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
        self.m_oSkillBookDlg = None
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/newpetrefine.dlg')
        interface.Center(self)
        import misc
        self.m_DlgHelpID = 5510
        self.m_Switch = 0
        self.m_PID = None
        self.m_PetObj = None
        self.m_ItemObj = None
        self.m_ItemShape = None
        self.m_HaveColorItem = None
        self.m_NeedColorItem = None
        self.m_iLastWashType = 1
        oMgr = GetPetRefineMgr()
        self.m_dBook = oMgr.GetOwnBook()
        oMgr.ssConnect(oMgr.SS_OwnBook, misc.Functor(self.RefreshOwnSkillBook))
        self.InitShow()
        self.InitData()
        self.InitBtnTips()
        self.CreateCommondImg()
        self.RefreshPetLst()
        self.CreateItemInterface()
        self.SetBtnsEnable(False)
        self.m_IsPotential = False
        self.GetObject('xichong').SetSelect(True)
        self.GetObject('skillbook_desc2').SetShow(False)
        self.GetObject('skill_list').SetShow(False)
        self.OnSwitch(3)
        self.OnMessage(3)

    
    def Topmost(self):
        combdialog.CCombDialog.Topmost(self)
        if self.m_oSkillBookDlg:
            self.m_oSkillBookDlg.Topmost()
        

    
    def RefreshOwnSkillBook(self, dBook):
        self.m_dBook = dBook

    
    def InitShow(self):
        Data = [
            ('listbox', 'skillbox', 'm_SkillList', 'm_SkillBox'),
            ('listbox1', 'skillbox1', 'm_SkillList1', 'm_SkillBox1'),
            ('listbox2', 'img_pet', 'm_PetList', 'm_petBox')]
        for objname1, objname2, name1, name2 in Data:
            obj1 = self.GetObject(objname1)
            obj2 = self.GetObject(objname2)
            if obj1 and obj2:
                setattr(self, name1, obj1)
                setattr(self, name2, obj2)
                obj1.SetZ(obj2.GetZ() - 1)
                if objname2 == 'img_pet':
                    obj2.SetShow(False)
                
                for tt in obj1.m_Lines:
                    tt.SetShow(False)
                
        

    
    def InitData(self):
        self.m_Data = []
        self.m_SkillData = []
        self.m_FilePath = ''
        self.m_SkillPath = ''
        if getattr(self, 'm_petBox', None) and getattr(self, 'm_SkillBox', None):
            self.m_FilePath = self.m_petBox.m_FileName
            self.m_SkillPath = self.m_SkillBox.m_FileName
            for i in range(4):
                (x, y) = self.m_petBox.m_Imagess[i].GetPos()
                self.m_Data.append((x, y))
                (x1, y1) = self.m_SkillBox.m_Imagess[i].GetPos()
                self.m_SkillData.append((x1, y1))
            
        

    
    def CreateCommondImg(self):
        
        def doAni(obj, iFrame, frameAmount):
            iFrame = (iFrame + 1) % frameAmount
            obj.SetFrame(iFrame)
            return (iFrame, frameAmount)

        filename = style.GetPath('combdialog/\xd4\xd3\xcd\xbc/\xbc\xd3\xba\xc5\xc9\xc1.igs')
        Data = [
            ('skillbooks', 'm_Img1'),
            ('img_item1', 'm_Img2')]
        for objname, name in Data:
            ctrl = self.GetObject(objname)
            if ctrl:
                (w, h) = ctrl.GetSize()
                img = interface.CButton(ctrl, filename, 0, 0)
                (iw, ih) = img.GetSize()
                img.SetPos((w - iw) / 2, (h - ih) / 2)
                img.SetZ(0)
                setattr(self, name, img)
                frames = img.FrameAmount()
                img.CreatePyCommand(3, doAni, 0, frames)
                continue
        

    
    def InitBtnTips(self):
        Data = [
            ('img_Tips', '\xc7\xe9\xa8\xcf\xa5\xce\xc1\xd9\xb5\xa3\xa4\xa6\xa5i\xb1N\xbf\xef\xa4\xa4\xaa\xba\xa5l\xb3\xea\xc3~\xc5\xdc\xa6\xa80\xaf\xc5\xaa\xba\xc4_\xc4_\xaa\xac\xbaA\xa1A\xad\xab\xb7s\xa5\xcd\xa6\xa8\xa5l\xb3\xea\xc3~\xb8\xea\xbd\xe8\xa9M\xa7\xde\xaf\xe0#r\xc7\xea\xbf\xef\xbe\xdc3\xad\xbf\xbc\xc6\xb6q\xae\xf8\xaf\xd3\xc1\xd9\xb5\xa3\xa4\xa6\xaa\xba\xc5\xdc\xb2\xa7\xac~\xc3d\xa1A\xa5\xb2\xa9w\xa5i\xa5H\xb7\xd2\xa5X\xc5\xdc\xb2\xa7\xa5l\xb3\xea\xc3~#r\xa1]\xaa\xec\xa9l\xc3C\xa6\xe2\xa4\xa3\xa6P\xa1A\xb8\xea\xbd\xe8\xa4W\xad\xad\xa7\xf3\xb0\xaa\xa1A\xc1\xd9\xa6\xb3\xa4@\xa9w\xb7\xa7\xb2v\xc3B\xa5~\xbcW\xa5[\xa4@\xad\xd3\xa5l\xb3\xea\xc3~\xa7\xde\xaf\xe0\xa1^'),
            ('img_Tips2', '\xc7\xe9\xa9\xf1\xa4J\xb1m\xadi\xaaG\xa9\xce\xba\xbf\xb7\xea\xa5\xdb\xa5i\xa5H\xac\xb0\xbf\xef\xa4\xa4\xaa\xba\xc5\xdc\xb2\xa7\xa5l\xb3\xea\xc3~\xb6i\xa6\xe6\xacV\xa6\xe2#r\xc7\xea\xacV\xa6\xe2\xab\xe1\xa5i\xa5H\xb1q\xc0H\xbe\xf7\xc0\xf2\xb1o\xaa\xba2\xba\xd8\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa4\xa4\xbf\xef\xbe\xdc\xa4@\xba\xd8\xa7@\xac\xb0\xa5l\xb3\xea\xc3~\xaa\xba\xb7s\xc3C\xa6\xe2'),
            ('img_Tips3', '\xa4\xc4\xbf\xef\xab\xe1\xa1A\xa6p\xaaG\xb3\xd1\xbel\xaa\xba\xc1\xd9\xb5\xa3\xa4\xa6\xa4\xa3\xa8\xac\xa5H\xb6i\xa6\xe6\xa5\xbb\xa6\xb8\xac~\xc3d\xa1A#r\xabh\xa6\xdb\xb0\xca\xae\xf8\xaf\xd3\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xc1\xca\xb6R\xa4\xed\xaf\xca\xaa\xba\xc1\xd9\xb5\xa3\xa4\xa6')]
        for objname, tips in Data:
            btn = self.GetObject(objname)
            if btn:
                btn.m_TipsStr = tips
                btn.m_TipsDirect = 2
                continue
        

    
    def CreateItemInterface(self):
        Data = [
            ('img_item', 16, 'm_RefineInterface', CItemInterface),
            ('box_cheats', 14, 'm_CheatsInterface', CSkillInterface),
            ('img_item1', 15, 'm_ColorInterface', CItemInterface)]
        import combmacro
        for objname, msgid, sname, classType in Data:
            (x, y, w, h) = self.GetLocData(objname)
            iit = classType(self, w, h, 0, 0, msgid)
            iit.SetPos(x, y)
            if objname == 'img_item':
                iit.SetTipsTxt('\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa5i\xa5H\xa7\xf3\xb4\xab\xb9D\xa8\xe3')
            
            combmacro.BindObject(objname, self, iit)
            setattr(self, sname, iit)
        

    
    def SetBtnsEnable(self, iFlag):
        btnNameLst = [
            'left1',
            'right1',
            'btn_cons1',
            'left2',
            'right2',
            'btn_cons2',
            'btn_cancle']
        for objname in btnNameLst:
            btn = self.GetObject(objname)
            if btn:
                btn.Enable(iFlag)
                continue
        

    
    def Active(self, idx):
        ctrlDct = {
            3: 'xichong',
            4: 'dashu',
            5: 'ranse' }
        btn = self.GetObject(ctrlDct[idx])
        btn.SetSelect(True)
        self.OnSwitch(idx)
        self.OnMessage(idx)

    
    def CanRefreshSkill(self):
        lst = [
            'm_SkillList',
            'm_SkillBox',
            'm_SkillList1',
            'm_SkillBox1',
            'm_SkillData',
            'm_SkillPath']
        for name in lst:
            if not getattr(self, name, None):
                return False
                continue
        
        return True

    
    def SelectPet(self, petID, extraZZ = 0):
        petobj = pet.GetPet(petID)
        if not petobj:
            usermacro.PROMPT_MSG('\xb8\xd3\xa5l\xb3\xea\xc3~\xa4\xa3\xa6s\xa6b')
            return None
        
        self.RemoveDlgItem()
        self.m_PID = petobj.m_ID
        self.m_PetObj = petobj
        self.CreateDlgItem(petobj, extraZZ)
        self.RefreshNeedCount()
        self.RefreshColorNeed()
        self.ReleaseColorSelect()
        self.RefreshVariantBtn()
        self.ProcessPotential()

    
    def ProcessPotential(self):
        if self.m_IsPotential and self.GetObject('box_cheats').GetShow():
            self.GetObject('skillbook_desc').SetShow(False)
            self.GetObject('skillbook_desc2').SetShow(True)
            self.GetObject('skill_list').SetShow(True)
            self.RefershSkillTxt(self.m_PetObj)
        

    
    def RefershSkillTxt(self, petObj):
        import petdata
        import petskill
        Name2SkillIDList = {
            '\xb2\xd7\xaf\xc5\xa9R\xa4\xa4': 329,
            '\xb0\xaa\xaf\xc5\xb1j\xa4O': 219,
            '\xb0\xaa\xaf\xc5\xa8\xbe\xbfm': 220,
            '\xb0\xaa\xaf\xc5\xa9R\xa4\xa4': 229,
            '\xa9R\xa4\xa4': 129,
            '\xc6F\xb1\xd3': 116,
            '\xa8\xb3\xb1\xb6': 117,
            '\xb1j\xa7\xa7': 118,
            '\xa6\xd7\xad\xb9\xb2\xdf\xa9\xca': 515,
            '\xbd\xc4\xc0\xbb': 111,
            '\xb0\xaa\xaf\xc5\xbcz\xae\xda': 230,
            '\xb0\xaa\xaf\xc5\xc6F\xb3q\xb3N': 222 }
        iShape = petObj.m_Prop.m_Shape
        dPetData = petdata.GetData(iShape)
        skillNameList = dPetData.get('maySkillLst', [])
        if 'mustSkillName' in dPetData:
            skillNameList = [
                dPetData['mustSkillName']] + list(skillNameList)
        
        ridList = []
        skillIDList = []
        for name in skillNameList:
            if name in Name2SkillIDList:
                skillIDList.append(Name2SkillIDList[name])
                ridList.append(name)
                continue
        
        for skillID, skillDct in petskill.DATA.items():
            if skillDct['name'] in skillNameList and skillDct['name'] not in ridList:
                skillIDList.append(skillID)
                continue
        
        sSkillTxt = ''
        for iSkillID in skillIDList:
            if iSkillID not in petObj.m_Skills:
                sSkillTxt += '#c3CB371%s ' % petskill.GetData(iSkillID)['name']
                continue
        
        for iSkillID in skillIDList:
            if iSkillID in petObj.m_Skills:
                sSkillTxt += '#c999999%s ' % petskill.GetData(iSkillID)['name']
                continue
        
        self.GetObject('skill_list').SetText(sSkillTxt)

    
    def RefreshVariantBtn(self):
        if self.GetObject('xichong').IsSelected():
            key = (self.m_PetObj.m_Key & 65280) >> 8
            if key & pet.MARK_ISCOLOR != 0:
                if self.GetObject('chk_variant').IsSelected():
                    return None
                
                self.GetObject('chk_variant').LeftUp()
            elif self.GetObject('chk_variant').IsSelected():
                self.GetObject('chk_variant').LeftUp()
            
        

    
    def CreatePropItem(self, petobj):
        for petattr, objname in PET_PROPS1:
            items = []
            (x, y) = self.GetObject(objname).GetPos()
            items.append((petattr, x, y, interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
            petobj.ReleaseDlgItem('newpetrefine', items)
            petobj.CreateCombDlgItem(objname, 'newpetrefine', items, self)
        

    
    def ShowPetPhoto(self, petobj):
        import wrapinterface
        import misc
        if hasattr(self, 'm_Ani') and self.m_Ani:
            self.m_Ani.Release()
        
        shape = petobj.GetProp('m_Shape')
        desc = petobj.GetProp('m_Desc')
        key = (petobj.m_BirthKey & 255) << 8 | petobj.m_Key & 255
        lianyaotime = petobj.GetProp('m_Lianyao')
        tkey = 0
        if lianyaotime == 0:
            pass
        elif lianyaotime > misc.GetServerCurrentTime():
            tkey = tkey | 1
        else:
            tkey = tkey | 2
        self.m_Ani = wrapinterface.CPetAniWithUnlock(self, shape, desc, key, timekey = tkey)
        self.m_Ani.SetColorCompensate(petobj.GetProp('m_bIsColorCompensate'), self.m_PID)
        self.m_Ani.SetPetID(self.m_PID)
        (x, y) = self.GetObject('petbox').GetPos()
        self.m_Ani.SetPos(x + 4, y + 2)
        lianyaoinfo = self.m_Ani.GetLianyaoImgInfo()
        if lianyaoinfo:
            (w, h, lianyao_x, lianyao_y) = lianyaoinfo
            self.m_LianyaoNotifyBox = self.CClickNotifyBox(self, w, h, 0, 0, 151)
            self.m_LianyaoNotifyBox.SetPos(x + lianyao_x, y + lianyao_y)
        else:
            self.m_LianyaoNotifyBox = None

    
    def GetTipsInfo(self, info, _mtype, dn, _gz, name, pobj):
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

    
    def AdjustColor(self, name, info, initColor):
        color = initColor
        if name == 'm_Life':
            bShow = not ('\xa5\xc3\xa5\xcd' == info)
            self.GetObject('img_Tips').SetShow(bShow)
            self.m_TipsInfo[5].SetShow(bShow)
            if info != '\xa5\xc3\xa5\xcd' and int(info) < 50:
                color = 16711680
            
        
        return color

    
    def Showzz(self, shaw, name, cname, cid, extraZZ = 0):
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
                    (x, y) = ctrl.GetImage(0, cid).GetPos()
                    tmp = interface.CNotifyBox(ob, 54, 16, alpha = 0, msgid = 200 + len(ob.m_Tipslist))
                    tmp.m_Info = txtinfo
                    tmp.SetPos(x + x1, y + y1)
                    import combmacro
                    combmacro.BindObject(cname, self, tmp)
                    ob.m_Tipslist.append(tmp)
                
            
            if info:
                import combmacro
                color = self.AdjustColor(name, info, color)
                if extraZZ == 0:
                    text = str(info)
                else:
                    
                    try:
                        info = int(info)
                    except:
                        info = 0

                    text = '%s+%s' % (str(info - extraZZ), str(extraZZ))
                txtobj = combmacro.CreateIFTextWithObject(ctrl, (interface.CBlackShadowText, interface.CTextObject, interface.CTextObject, interface.CTextObject)[interface.STYLE], 0, cid, text, interface.FontLT14_3, color)
            else:
                txtobj = None
            setattr(ctrl, name, txtobj)
        

    
    def CreateZZItem(self, petobj, extraZZ = 0):
        self.m_Tipslist = []
        
        def showtips(shadow):
            dlg = shadow.Get()
            if not dlg:
                return None
            
            dlg.m_Tipslist = []
            for name, cname, cid in PET_APTI:
                dlg.Showzz(interface.CShadowObject(dlg), name, cname, cid, extraZZ)
            

        for name, cname, cid in PET_APTI:
            propitem = petobj.m_Name2PropItem[name]
            propitem.AddRefreshCallbackWithID('newpetrefine', showtips, interface.CShadowObject(self))
        
        
        def showupdate(shadow):
            showtips(shadow)
            dlg = shadow.Get()
            if dlg is None:
                return None
            
            petobj = pet.GetPet(dlg.m_PID)
            flag = petobj.m_Name2PropItem['Update_Flag'].GetInfo()
            maxi = petobj.m_Name2PropItem['Update_Max'].GetInfo()
            flag = int(flag)
            maxi = int(maxi)
            if flag % 16 == 0:
                dlg.ClearStar(-1)
            else:
                for i in range(1, 6):
                    dlg.ShowStar(i, (flag >> i * 4) % 16, (maxi >> i * 4) % 16)
                

        for propname in PET_UPD:
            propitem = petobj.m_Name2PropItem[propname]
            propitem.AddRefreshCallbackWithID('newpetrefine', showupdate, interface.CShadowObject(self))
        

    
    def ShowStar(self, idx, times, maxi):
        if idx % 2 == 0:
            obj = self.GetObject('txt_apti2')
            (ox, oy) = obj.GetPos()
            (ix, iy) = obj.GetImage(0, idx / 2 - 1).GetPos()
        else:
            obj = self.GetObject('txt_apti')
            (ox, oy) = obj.GetPos()
            (ix, iy) = obj.GetImage(0, idx / 2).GetPos()
        x = ox + ix + 46
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
        if not hasattr(obj, 'm_Real'):
            obj.m_Real = []
        
        obj.m_Real.append(interface.CShadowObject(img))
        obj.m_Real.append(interface.CShadowObject(box))
        img.SetShow(obj.GetShow())
        box.SetShow(obj.GetShow())
        self.m_Stars[idx] = (img, box, times, maxi)

    
    def RefreshSkill(self, petobj):
        if self.CanRefreshSkill():
            if petobj and len(petobj.m_Skills) < 13:
                self.CreateSkillIcon(petobj, 3)
            elif petobj and len(petobj.m_Skills) >= 13:
                self.CreateSkillIcon(petobj)
            
        

    
    def CreateSkillIcon(self, petobj, Num = 0):
        self.m_SkillList.Clear()
        self.m_SkillList1.Clear()
        self.m_SkillBox.SetShow(False)
        self.m_SkillBox1.SetShow(False)
        sklLst = []
        self.m_SkillIcons = []
        self.m_SkillIcons1 = []
        for idx, sk in enumerate(petobj.m_Skills):
            sklLst.append((idx, sk))
        
        num = None if Num == 0 else Num
        for i in xrange(num):
            idx = i * 4
            self.AddSkillItem(sklLst[idx:idx + 4], petobj, 1)
            self.AddSkillItem(sklLst[idx:idx + 4], petobj, 2)
        

    
    def AddSkillItem(self, sklLst, petobj, iType):
        import combmacro
        data = {
            1: (self.m_SkillList, self.m_SkillIcons),
            2: (self.m_SkillList1, self.m_SkillIcons1) }
        (skillLst, skillIcons) = data[iType]
        it = interface.CBoxObject(skillLst, skillLst.m_ItemWidth, skillLst.m_ItemHeight, 0, 0)
        it.m_IconBG = []
        for i in xrange(4):
            bgObj = combmacro.CIMAGE(it, self.m_SkillPath, interface.UIPath)
            bgObj.SetPos(self.m_SkillData[i][0], self.m_SkillData[i][1])
            bgObj.SetZ(1)
            it.m_IconBG.append(bgObj)
        
        for idx, sklData in enumerate(sklLst):
            (sklPos, sklID) = sklData
            skillObj = dlgpet.CSkillIcon(it, self.m_SkillData[idx][0] + 3, self.m_SkillData[idx][1] + 3, sklID, sklPos == petobj.m_BindSkill)
            skillObj.SetZ(2)
            skillObj.SetTag(petobj.IsHFSkillIdx(sklPos))
            skillObj.SetPillPos(petobj.GetPillSkillIdx(sklPos))
            skillObj.SetOwnerID(petobj.m_ID)
            skillIcons.append(skillObj)
        
        skillLst.AddItem(it)
        skillLst.ResetItems()
        skillLst.ResetScrollBar()

    
    def CreateDlgItem(self, petobj, extraZZ = 0):
        self.CreatePropItem(petobj)
        self.ShowPetPhoto(petobj)
        self.CreateZZItem(petobj, extraZZ)
        if petobj.m_UpdateProp == False:
            import netpet
            netpet.C2SSummonView(petobj.m_ID)
        
        self.RefreshSkill(petobj)

    
    def RemoveDlgItem(self):
        if self.m_PetObj:
            if getattr(self, 'm_Ani', None):
                self.m_Ani.Release()
                self.m_Ani = None
            
            for arr in PET_PROPS1:
                self.m_PetObj.ReleaseDlgItem('newpetrefine', ((arr[0], 0, 0),))
            
            for arr in PET_APTI:
                propitem = self.m_PetObj.m_Name2PropItem[arr[0]]
                propitem.RemoveRefreshCallbackWithID('newpetrefine')
            
            for propname in PET_UPD:
                propitem = self.m_PetObj.m_Name2PropItem[propname]
                propitem.RemoveRefreshCallbackWithID('newpetrefine')
            
            self.m_PID = None
            self.m_PetObj = None
            self.ClearSkill()
            self.RemovePointsStar()
            self.RefreshNeedCount()
            self.RefreshColorNeed()
            self.ReleaseColorSelect()
        

    
    def RemovePointsStar(self):
        self.ClearStar(-1)
        for name, cname, cid in PET_APTI:
            ctrl = self.GetObject(cname)
            setattr(ctrl, name, None)
        

    
    def ClearSkill(self):
        self.m_SkillIcons = []
        self.m_SkillIcons1 = []

    
    def ClearStar(self, idx):
        if hasattr(self, 'm_Stars') and idx in self.m_Stars:
            del self.m_Stars[idx]
        elif idx == -1:
            self.m_Stars = { }
        

    
    def OnEnter(self, msgid):
        import wrapinterface
        if msgid >= 200:
            if self.m_Tipslist[msgid - 200].m_Info != '':
                self.m_Tips = wrapinterface.CTextTips(self, -1, self.m_Tipslist[msgid - 200].m_Info, interface.FontLT14_3, direct = 0)
            
        elif msgid == 151:
            txt = None
            if self.m_PetObj:
                lianyao = self.m_PetObj.GetProp('m_Lianyao')
                txt = dlgpet.GetLianyaoTips(lianyao)
            
            if txt is not None:
                self.m_Tips = wrapinterface.CTextTips(self, -1, txt, interface.FontLT14_3, direct = 1)
            
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

    
    def RefreshPetLst(self):
        if pet.GetPetCount() <= 8:
            self.CreatePetsItem(2)
        else:
            self.CreatePetsItem()

    
    def CreatePetsItem(self, Num = 0):
        if not self.m_PetList and self.m_Data and self.m_FilePath:
            return None
        
        self.m_PetList.Clear()
        petLst = []
        self.m_PetIcons = []
        for pobj in pet.GetSortPets():
            petLst.insert(0, pobj)
        
        num = None if Num == 0 else Num
        for i in xrange(num):
            idx = i * 4
            self.AddListItem(petLst[idx:idx + 4], idx)
        

    
    def AddListItem(self, petLst, msgid):
        import style
        it = interface.CBoxObject(self.m_PetList, self.m_PetList.m_ItemWidth, self.m_PetList.m_ItemHeight, 0, 0)
        it.m_IconBG = []
        classtype = None if interface.IsIgsPath(self.m_FilePath) else interface.CBitmapObject
        for i in xrange(4):
            bgObj = classtype(it, self.m_FilePath, interface.UIPath)
            (offx, offy) = style.GetIntTuple(self.GetDlgPath(), 'offpos_bgObj')
            bgObj.SetPos(self.m_Data[i][0] + offx, self.m_Data[i][1] + offy)
            bgObj.SetZ(1)
            it.m_IconBG.append(bgObj)
        
        for idx, petobj in enumerate(petLst):
            icon = CPetIcon(it, 'photo/summon/%04d.igs' % petobj.m_Prop.m_Shape, 'misc', idx + msgid + 1)
            icon.SetPetName(petobj.m_Prop.m_Name)
            icon.SetPos(self.m_Data[idx][0] + 5, self.m_Data[idx][1] + 5)
            icon.m_PetID = petobj.m_ID
            icon.m_BirthKey = petobj.m_BirthKey
            icon.SetZ(2)
            self.m_PetIcons.append(icon)
        
        self.m_PetList.AddItem(it)
        self.m_PetList.ResetItems()
        self.m_PetList.ResetScrollBar()
        self.RefreshShadow()

    
    def RefreshShadow(self):
        if self.m_Switch == 3:
            self.ShadowPetIcon(False)
            self.ShadowPetIcon(True)
        elif self.m_Switch == 5:
            self.ShadowPetIcon2(False)
            self.ShadowPetIcon2(True)
        

    
    def BtnSelected(self, iMsgID):
        if iMsgID == 3:
            self.m_SkillBox.SetShow(False)
        

    
    def OnSelect(self, ctrl):
        self.OnSwitch(ctrl.m_MsgID)
        return True

    
    def OnSwitch(self, itype):
        activeFunc = {
            3: self.OnRefinePet,
            4: self.OnRefineSkill,
            5: self.OnRefineColor }
        func = activeFunc.get(self.m_Switch)
        if func:
            func(False)
        
        func = activeFunc.get(itype)
        if func:
            func(True)
        
        self.m_Switch = itype

    
    def ShadowPetIcon(self, iFlag):
        for icon in self.m_PetIcons:
            if iFlag and pet.IsSpecialSummon(icon.m_BirthKey):
                icon.SetGrey()
                continue
            icon.SetLight(8)
        

    
    def ShadowPetIcon2(self, iFlag):
        itemobj = self.m_ColorInterface.GetItem()
        if iFlag and itemobj:
            if itemobj.m_Shape in (25670, 25671, 25673, 25913):
                for icon in self.m_PetIcons:
                    if icon.m_BirthKey & pet.MARK_ISHOLYPET != 0 or icon.m_BirthKey & pet.MARK_ISXIANPET != 0:
                        icon.SetGrey()
                        continue
                
            elif itemobj.m_Shape == 25929:
                for icon in self.m_PetIcons:
                    if icon.m_BirthKey & pet.MARK_ISHOLYPET == 0 and icon.m_BirthKey & pet.MARK_ISXIANPET == 0:
                        icon.SetGrey()
                        continue
                
            
        else:
            for icon in self.m_PetIcons:
                icon.SetLight(8)
            

    
    def OnRefinePet(self, iFlag):
        self.GetObject('skillbook_desc').SetShow(False)
        self.GetObject('skillbook_desc2').SetShow(False)
        self.GetObject('skill_list').SetShow(False)
        if iFlag:
            if getattr(self, 'm_SkillIcons', None) and getattr(self, 'm_SkillBox', None):
                self.m_SkillList.SetZ(self.m_SkillBox.GetZ() + 1)
            elif not getattr(self, 'm_SkillIcons', None):
                self.m_SkillList.SetZ(self.m_SkillBox.GetZ() - 1)
            
            self.ShadowPetIcon(True)
        else:
            self.ShadowPetIcon(False)

    
    def OnRefineSkill(self, iFlag):
        self.GetObject('skillbook_desc').SetShow(True)
        self.GetObject('skillbook_desc2').SetShow(False)
        self.GetObject('skill_list').SetShow(False)
        if iFlag:
            if getattr(self, 'm_SkillIcons', None) and getattr(self, 'm_SkillBox1', None):
                self.m_SkillList1.SetZ(self.m_SkillBox1.GetZ() + 1)
            elif not getattr(self, 'm_SkillIcons', None):
                self.m_SkillList1.SetZ(self.m_SkillBox1.GetZ() - 1)
            
        

    
    def OnRefineColor(self, iFlag):
        self.GetObject('skillbook_desc').SetShow(False)
        self.GetObject('skillbook_desc2').SetShow(False)
        self.GetObject('skill_list').SetShow(False)
        if iFlag:
            self.ShadowPetIcon2(True)
        else:
            self.ShadowPetIcon2(False)

    
    def RefreshPet(self, petobj):
        self.RefreshPetLst()
        if self.m_PID:
            for pobj in self.m_PetIcons:
                if pobj.m_PetID == self.m_PID:
                    pobj.LeftUp()
                    return None
                    continue
            
        else:
            for pobj in self.m_PetIcons:
                if pobj.m_PetID == petobj.m_ID:
                    pobj.LeftUp()
                    return None
                    continue
            

    
    def RefreshPetInfo(self, pid, extraZZ = 0):
        self.RefreshPetLst()
        if self.m_PID and self.m_PID == pid:
            for obj in self.m_PetIcons:
                obj.Select(obj.m_PetID == pid)
            
            self.SelectPet(pid, extraZZ)
        

    
    def RefreshPetSkill(self, petid):
        if self.m_PID and self.m_PID == petid:
            petobj = pet.GetPet(petid)
            self.RefreshSkill(petobj)
            self.m_CheatsInterface.SetItem(None)
            self.m_CheatsInterface.SetSkill(None)
            self.m_IsPotential = False
            if self.GetObject('box_cheats').GetShow():
                self.GetObject('skillbook_desc').SetShow(True)
                self.GetObject('skillbook_desc2').SetShow(False)
                self.GetObject('skill_list').SetShow(False)
            
        

    
    def RefreshRefineItem(self):
        itemobj1 = self.m_CheatsInterface.GetItem()
        itemobj2 = self.m_ColorInterface.GetItem()
        itemLst = [
            itemobj1,
            itemobj2]
        for idx, itemobj in enumerate(itemLst):
            if itemobj and not item.GetItem(itemobj.m_ID):
                if idx + 1 in (2,) and item.FindItem(itemobj.m_Shape):
                    itemobj = item.FindItem(itemobj.m_Shape)
                else:
                    itemobj = None
                self.SetItemChoose(itemobj, idx + 1)
                continue
        
        if self.m_ItemObj and not item.GetItem(self.m_ItemObj.m_ID):
            iShape = self.m_ItemObj.m_Shape
            if iShape in REFINEITEM1:
                itemobj = item.FindItem(iShape)
                if itemobj:
                    self.SetRefineItem(itemobj, iShape)
                
            
        

    
    def SetRefineItem(self, itemobj, iShape):
        import itemdefine
        self.m_ItemObj = itemobj
        self.m_ItemShape = iShape
        if iShape == itemdefine.ID_ITEM_HUANTONG:
            self.m_iLastWashType = 1
        else:
            self.m_iLastWashType = 2
        self.m_RefineInterface.SetItem(itemobj)
        self.RefreshNeedCount()

    
    def GetPetRefineNeedCount(self, iFlag):
        needGoods = {
            0: 1,
            5: 2,
            10: 2,
            15: 2,
            25: 3,
            35: 3,
            45: 5,
            55: 6,
            65: 7,
            85: 7,
            105: 9,
            115: 12,
            120: 13,
            130: 15 }
        import petdata
        if self.m_PetObj:
            shape = self.m_PetObj.m_Prop.m_Shape
            carryGrade = petdata.GetData(shape)['carry_grade']
            bkey = getattr(self.m_PetObj, 'm_BirthKey', 0)
            needCount = needGoods.get(carryGrade, 1)
            if pet.IsSpecialSummon(bkey):
                needCount = 0
            
            if self.GetObject('chk_variant').IsSelected():
                if not iFlag:
                    needCount *= 3
                
            elif iFlag:
                needCount *= 3
            
        else:
            needCount = 0
        return needCount

    
    def RefreshNeedCount(self, iFlag = False):
        needCount = self.GetPetRefineNeedCount(iFlag)
        if not self.m_ItemShape:
            return None
        
        haveCount = item.GetItemNum(self.m_ItemShape)
        perfix = ''
        if needCount > haveCount:
            perfix = '#R'
        
        color = interface.COLOR_56
        self.m_NeedCountTxt = interface.CRichTextObject(self.GetObject('need_amount'), 200, interface.FontLT14_3, '\xae\xf8\xaf\xd3:%s%d#n/%d#n' % (perfix, haveCount, needCount), color)

    
    def GetNeedColorItem(self, iPetShape, iItemShape):
        import petdata
        if petdata.IsShenShou(iPetShape) or petdata.IsXianShou(iPetShape):
            return 0
        
        carrygrade = petdata.GetData(iPetShape)['carry_grade']
        if iItemShape == 25913:
            need = None if carrygrade >= 130 else 1
        elif iItemShape == 25673:
            need = None if carrygrade <= 90 else 0
        elif iItemShape == 25671:
            need = None if carrygrade <= 60 else 0
        elif iItemShape == 25670:
            need = None if carrygrade <= 40 else 0
        else:
            need = 0
        return need

    
    def GetNeedData(self):
        itemobj = self.m_ColorInterface.GetItem()
        self.m_HaveColorItem = None
        self.m_NeedColorItem = None
        if self.m_PetObj and itemobj:
            import petdata
            iPetShape = self.m_PetObj.m_Prop.m_Shape
            iItemShape = itemobj.m_Shape
            if iPetShape in (2910, 2920) and iItemShape in (25913,):
                self.m_HaveColorItem = item.GetItemNum(iItemShape)
                self.m_NeedColorItem = 2
            elif (petdata.IsShenShou(iPetShape) or petdata.IsXianShou(iPetShape)) and iItemShape in (25929,):
                self.m_HaveColorItem = item.GetItemNum(iItemShape)
                self.m_NeedColorItem = None if petdata.IsShenShou(iPetShape) else 20
            else:
                self.m_HaveColorItem = item.GetItemNum(iItemShape)
                self.m_NeedColorItem = self.GetNeedColorItem(iPetShape, iItemShape)
        
        return (self.m_HaveColorItem, self.m_NeedColorItem)

    
    def RefreshColorNeed(self):
        (haveCount, needCount) = self.GetNeedData()
        if haveCount is not None and needCount is not None:
            color = interface.COLOR_56
            perfix1 = None if needCount == 0 else ''
            perfix2 = None if needCount > haveCount else ''
            self.m_NeedColorTxt = interface.CRichTextObject(self.GetObject('need_amount2'), 200, interface.FontLT14_3, '\xae\xf8\xaf\xd3:%s%d#n/%s%d#n' % (perfix1, needCount, perfix2, haveCount), color)
        else:
            self.m_NeedColorTxt = None

    
    def HasDefaultSelect(self):
        btnNameLst = [
            'chk_color1',
            'chk_color2',
            'chk_color3',
            'chk_color4']
        for objname in btnNameLst:
            btn = self.GetObject(objname)
            if btn and btn.IsSelected():
                return True
                continue
        
        return False

    s_Cheats1 = '\xbd\xd0\xa9\xf1\xa4J\xc5]\xc3~\xadn\xb3Z'
    s_Cheats2 = '\xc2I\xc0\xbb\xa5\xaa\xa4\xe8\xb9\xcf\xbc\xd0\n\xa7\xf3\xb4\xab\xc5]\xc3~\xadn\xb3Z'
    
    def SetItemChoose(self, itemobj, iType):
        if iType == 1:
            import petskill
            if itemobj:
                extName = itemobj.GetExtName()
                if extName == '\xbc\xe7\xaf\xe0':
                    self.m_IsPotential = True
                else:
                    self.m_IsPotential = False
                skillID = petskill.GetSkillID(extName)
                if skillID is not None:
                    self.m_CheatsInterface.SetItem(itemobj)
                    self.m_CheatsInterface.SetSkill(skillID)
                    self.GetObject('txt_cheats').SetText(self.s_Cheats2)
                
            else:
                self.m_CheatsInterface.SetItem(None)
                self.m_CheatsInterface.SetSkill(None)
                self.GetObject('txt_cheats').SetText(self.s_Cheats1)
        elif iType == 2:
            self.ShadowPetIcon2(False)
            self.m_ColorInterface.SetItem(itemobj)
            if not self.HasDefaultSelect():
                self.GetObject('chk_color1').SetSelect(True)
            
            self.RefreshColorNeed()
            self.ShadowPetIcon2(True)
        elif iType == 3:
            self.SetRefineItem(itemobj, itemobj.m_Shape)
        

    
    def ShowColorSelect(self, pid, shape, color1, color2, iType):
        self.m_ColorPID = pid
        self.m_DirLeft = 0
        self.m_DirRight = 0
        self.ShowColorPetPhoto('box_1', shape, color1)
        self.ShowColorPetPhoto('box_2', shape, color2)
        self.ShowTips(iType)
        self.SetBtnsEnable(True)
        self.RefreshColorNeed()

    
    def ShowTips(self, iType):
        txtObj = self.GetObject('txt_Tips')
        (tW, _) = txtObj.GetSize()
        font = interface.FontLT14_10
        color = interface.COLOR_326
        if iType == 1:
            self.m_Tips = []
            txtLst = CPetRefineDlg.s_Type2Tips[iType].split('#r')
            y = 0
            if txtLst:
                for i in range(len(txtLst)):
                    tipsObj = interface.CTextObject(txtObj, txtLst[i], font, color, 0)
                    (txtW, txtH) = tipsObj.GetSize()
                    tipsObj.SetPos((tW - txtW) / 2, y)
                    y = y + txtH + 2
                    self.m_Tips.append(tipsObj)
                
            
        else:
            self.m_Tips = interface.CTextObject(txtObj, CPetRefineDlg.s_Type2Tips[iType], font, color, 0)
            (txtW, _) = self.m_Tips.GetSize()
            self.m_Tips.SetPos((tW - txtW) / 2, 10)

    
    def ShowColorPetPhoto(self, ctrl, shape, desc, key = 0):
        ani = getattr(self, 'm_Ani' + ctrl, None)
        if ani:
            ani.Release()
        
        ani = wrapinterface.CPetAni(self.GetObject(ctrl), shape, desc, key)
        ani.SetPos(4, 2)
        setattr(self, 'm_Ani' + ctrl, ani)

    
    def ReleaseColorSelect(self):
        self.m_Tips = None
        boxName = [
            'box_1',
            'box_2']
        for ctrl in boxName:
            ani = getattr(self, 'm_Ani' + ctrl, None)
            if ani:
                ani.Release()
                ani = None
                continue
        
        self.SetBtnsEnable(False)

    
    def GiveupSelect(self):
        import nethero
        import commondialog
        
        def SureGiveup(dlg):
            nethero.C2SPetColorSelect(getattr(self, 'm_ColorPID', 0), 0)
            print getattr(self, 'm_ColorPID', 0), '\xb3o\xacO\xa8\xfa\xae\xf8\xacV\xa6\xe2\xae\xc9\xb5o\xb0e\xaa\xbaid\xa1A00=-============='
            self.ReleaseColorSelect()

        msg = '\xa9\xf1\xb1\xf3\xacV\xa6\xe2\xb7|\xa8\xcf\xb1o\xa7A\xaa\xba\xa5l\xb3\xea\xc3~\xabO\xafd\xad\xec\xa8\xd3\xaa\xba\xc3C\xa6\xe2\xa1A\xa6P\xae\xc9#R\xae\xf8\xaf\xd3\xacV\xa6\xe2\xb9D\xa8\xe3#n\xa1C\xa6\xfd\xa4U\xa6\xb8\xacV\xa6\xe2\xae\xc9\xa1A\xacV\xa6\xe2\xa4\xe8\xae\xd7\xb7|\xad\xab\xb7s\xa5\xcd\xa6\xa8'
        commondialog.ShowMessageBox(msg, ('\xa9\xf1\xb1\xf3\xacV\xa6\xe2', '\xa8\xfa \xae\xf8'), (SureGiveup, None))

    
    def SetPhotoDirection(self, iType, idx):
        if iType == 0:
            self.m_DirLeft = (self.m_DirLeft + 8 * idx) % 32
            if hasattr(self, 'm_Anibox_1'):
                self.m_Anibox_1.SetDir(self.m_DirLeft)
            
        elif iType == 1:
            self.m_DirRight = (self.m_DirRight + 8 * idx) % 32
            if hasattr(self, 'm_Anibox_2'):
                self.m_Anibox_2.SetDir(self.m_DirRight)
            
        

    
    def IsEnableClick(self):
        import misc
        curTime = misc.Time()
        if g_bCanPetRefine:
            self.m_DelayTime = curTime
            return True
        elif hasattr(self, 'm_DelayTime'):
            if curTime - self.m_DelayTime <= curTime - self.m_DelayTime:
                pass
            elif curTime - self.m_DelayTime < 5:
                usermacro.PROMPT_MSG('\xbd\xd0\xa4\xc5\xc0W\xc1c\xbe\xde\xa7@')
                return False
            
        
        self.m_DelayTime = curTime
        return True

    
    def ConfirmRefine(self):
        global g_bCanPetRefine
        if dlgshenmoisland.IsShenmoHuodong():
            usermacro.PROMPT_MSG('\xb8\xf3\xaaA\xa4\xa3\xa4\xe4\xab\xf9\xb8\xd3\xa5\\\xaf\xe0\xa1A\xbd\xd0\xa6^\xa8\xec\xad\xec\xaaA\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if self.IsEnableClick():
            if not self.m_PetObj:
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xa5l\xb3\xea\xc3~')
                return None
            
            import netpet
            variant = self.GetObject('chk_variant').IsSelected()
            if not self.m_ItemObj:
                itemid = 0
            else:
                itemid = self.m_ItemObj.m_ID
            netpet.C2SPetRefine(1, 2, self.m_PetObj.m_ID, itemid, variant, self.m_iLastWashType, 0)
            g_bCanPetRefine = False
        

    
    def OnStudySkill(self):
        global g_bCanPetRefine
        if self.IsEnableClick():
            iSkllID = self.m_CheatsInterface.GetSkillID()
            if not self.m_PetObj:
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xa5l\xb3\xea\xc3~')
                return None
            
            if not iSkllID:
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xc5]\xc3~\xadn\xb3Z')
                return None
            
            iBookID = 0
            if iSkllID in self.m_dBook:
                iBookID = self.m_dBook[iSkllID][-1]
            
            import netpet
            if iBookID:
                netpet.C2SPetRefine(1, 2, self.m_PetObj.m_ID, iBookID, 0, 0)
            else:
                iBuyType = BUYTYPE_MXGOLD
                if self.m_iPrice == 0:
                    iBuyType = BUYTYPE_XIANLIU
                
                netpet.C2SStudySkill(self.m_PetObj.m_ID, iSkllID, self.m_iPrice, iBuyType)
                g_bCanPetRefine = False
        

    
    def ConfirmRColor(self):
        if self.IsEnableClick():
            itemobj = self.m_ColorInterface.GetItem()
            if not self.m_PetObj:
                usermacro.PROMPT_MSG('\xa5l\xb3\xea\xc3~\xa9\xce\xacV\xa6\xe2\xb9D\xa8\xe3\xa4\xa3\xa6s\xa6b')
                return None
            elif not itemobj:
                usermacro.PROMPT_MSG('\xbd\xd0\xa9\xf1\xa4J\xacV\xa6\xe2\xb9D\xa8\xe3')
                return None
            elif self.m_HaveColorItem is not None and self.m_NeedColorItem is not None and self.m_NeedColorItem > self.m_HaveColorItem:
                usermacro.PROMPT_MSG('\xacV\xa6\xe2\xb9D\xa8\xe3\xbc\xc6\xb6q\xa4\xa3\xa8\xac\xa1I')
                return None
            
            import netpet
            mode = 0
            if self.GetObject('chk_color1').IsSelected():
                mode = 1
            
            if self.GetObject('chk_color2').IsSelected():
                mode = 2
            
            if self.GetObject('chk_color3').IsSelected():
                mode = 3
            
            if self.GetObject('chk_color4').IsSelected():
                mode = 4
            
            netpet.C2SPetRefine(1, 3, self.m_PetObj.m_ID, itemobj.m_ID, 0, mode)
        

    
    def OpenItemDlg(self, iType):
        import style
        if IsNewSkillBookDlg() and iType == 1:
            import misc
            import netpet
            if not self.m_PetObj:
                usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xa5l\xb3\xea\xc3~')
                return None
            
            self.m_oSkillBookDlg = CSkillBookDlg(self.m_PID)
            (x, y) = self.GetPos()
            (offX, offY) = style.GetIntTuple(self.GetDlgPath(), 'offpos_oSkillBookDlg')
            self.m_oSkillBookDlg.SetPos(x + offX, y + offY)
            self.m_oSkillBookDlg.SetCloseCB(misc.Functor(self.CloseBookDlg))
            self.m_oSkillBookDlg.SetSelectSkillCB(self.OnSelectSkillBook)
            netpet.C2SGetPeice()
            return None
        
        Type2ShapeLst = {
            1: [
                25405],
            2: REFINEITEM2,
            3: REFINEITEM1 }
        shapeLst = Type2ShapeLst.get(iType, [])
        self.m_ItemChooseDlg = CRefineItemChoose(shapeLst, iType)

    
    def CloseBookDlg(self):
        self.m_oSkillBookDlg = None
        import netpet
        netpet.C2SClosePetRefine()

    
    def OnSelectSkillBook(self, iSkillID, iPrice = 0):
        self.m_iPrice = iPrice
        self.m_CheatsInterface.SetSkill(iSkillID)
        self.GetObject('txt_cheats').SetText(self.s_Cheats2)
        if iSkillID != 578:
            self.m_IsPotential = False
            self.GetObject('skillbook_desc').SetShow(True)
            self.GetObject('skillbook_desc2').SetShow(False)
            self.GetObject('skill_list').SetShow(False)
        else:
            self.m_IsPotential = True
            self.GetObject('skillbook_desc').SetShow(False)
            self.GetObject('skillbook_desc2').SetShow(True)
            self.GetObject('skill_list').SetShow(True)
            self.RefershSkillTxt(self.m_PetObj)

    
    def C2SConfirmColor(self, iType):
        import nethero
        nethero.C2SPetColorSelect(getattr(self, 'm_ColorPID', 0), iType)
        self.ReleaseColorSelect()

    
    def OnChoosePet(self, msgid):
        if self.m_PetIcons and len(self.m_PetIcons) >= msgid - 101:
            for icon in self.m_PetIcons:
                icon.Select(False)
            
            icon = self.m_PetIcons[msgid - 101]
            icon.Select(True)
            self.SelectPet(icon.m_PetID)
            if self.GetObject('ranse').IsSelected():
                self.GetOldRefine()
            
        

    
    def GetOldRefine(self):
        if not self.m_PetObj:
            return None
        
        import netpet
        netpet.C2SGetRefine(self.m_PetObj.m_ID)

    
    def ChoosePetByID(self, pid):
        for icon in self.m_PetIcons:
            icon.Select(False)
            if icon.m_PetID == pid:
                icon.Select(True)
            
            self.SelectPet(pid)
        

    
    def CloseWindow(self):
        global g_PetRefineDlg
        
        def Close(dlg):
            global g_PetRefineDlg
            g_PetRefineDlg = None

        if self.GetObject('btn_cancle').GetShow() and getattr(self, 'm_Tips', None):
            import commondialog
            commondialog.ShowMessageBox('\xb1z\xa6\xb3\xa5l\xb3\xea\xc3~\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa5\xbc\xbf\xef\xbe\xdc\xa1A\xacO\xa7_\xbdT\xbb{\xc3\xf6\xb3\xac\xa1H', ('\xbdT\xbb{', '\xa8\xfa\xae\xf8'), (Close, None))
        else:
            g_PetRefineDlg = None
        if self.m_oSkillBookDlg:
            self.CloseBookDlg()
        

    
    def IsableCancle(self):
        if not self.GetObject('chk_variant').IsSelected():
            return True
        
        num1 = self.m_PetObj.m_Key & 65280
        num2 = num1 >> 8
        if (self.m_PetObj.m_Key & 65280) >> 8 & pet.MARK_ISCOLOR != 0:
            usermacro.PROMPT_MSG('\xc5\xdc\xb2\xa7\xaa\xba\xa5l\xb3\xea\xc3~\xa5u\xa4\xb9\xb3\\\xc5\xdc\xb2\xa7\xb7\xd2\xa7\xaf')
            self.GetObject('chk_variant').SetSelect(False)
            return False
        
        return True

    
    def SwitchPage(self, iPage):
        if iPage == 3:
            if self.m_oSkillBookDlg:
                self.CloseBookDlg()
            
        elif IsNewSkillBookDlg() and iPage == 4:
            self.RemoveDlgItem()
            for obj in self.m_PetIcons:
                obj.Select(False)
            
        elif iPage == 5:
            self.GetOldRefine()
            if self.m_oSkillBookDlg:
                self.CloseBookDlg()
            
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid in (3, 4, 5):
            self.SwitchPage(msgid)
        elif msgid == 11:
            self.ConfirmRefine()
        elif msgid == 12:
            self.OnStudySkill()
        elif msgid == 13:
            self.ConfirmRColor()
        elif msgid == 14:
            self.OpenItemDlg(1)
        elif msgid == 15:
            self.OpenItemDlg(2)
        elif msgid == 16:
            self.OpenItemDlg(3)
        elif msgid == 26:
            if not self.m_PetObj:
                return None
            
            if self.IsableCancle():
                self.RefreshNeedCount(True)
            
        elif msgid == 34:
            self.SetPhotoDirection(0, 1)
        elif msgid == 35:
            self.SetPhotoDirection(0, -1)
        elif msgid == 36:
            self.C2SConfirmColor(1)
        elif msgid == 37:
            self.SetPhotoDirection(1, 1)
        elif msgid == 38:
            self.SetPhotoDirection(1, -1)
        elif msgid == 39:
            self.C2SConfirmColor(2)
        elif msgid == 40:
            self.GiveupSelect()
        elif msgid < msgid:
            pass
        elif msgid <= 150:
            self.OnChoosePet(msgid)
        elif msgid == 151:
            import netpet
            netpet.C2SCancelLianyao(self.m_PID)
