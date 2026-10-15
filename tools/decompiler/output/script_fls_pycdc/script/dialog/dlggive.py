# pycdc 交叉复核产物 · script.fls entry 4942
# co_filename(原始)='script/dialog/dlggive.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4942.pyc (Python 2.5)

import C_sys
import combdialog
import dialoguecommondata
import interface
import item
import misc
import style
import tipsclosemgr
import ui
import wrapinterface
import usermacro
import net2019double12shop
import itemdefine
GEMID = (25678, 25679, 26001, 26002, 26003, 26004, 26005, 26006, 26007, 26008, 26009, 26010, 26011, 26012, 26013, 26014, 26015, itemdefine.ID_GEM_RED, itemdefine.ID_GEM_BLUE, itemdefine.ID_GEM_YELLOW, itemdefine.ID_GEM_SUN, itemdefine.ID_GEM_MOON, itemdefine.ID_GEM_BLACK, itemdefine.ID_GEM_SARIRA, itemdefine.ID_GEM_XUEXI, itemdefine.ID_GEM_ZHOUSHU, itemdefine.ID_GEM_XIAN, itemdefine.ID_GEM_GUI, itemdefine.ID_GEM_YAO, itemdefine.ID_GEM_NIAN, itemdefine.ID_GEM_ZHI, itemdefine.ID_GEM_BUCHI)
BOOK_LIST = {
    '\xa5\xb2\xb1\xfe': None,
    '\xb0\xaa\xaf\xc5\xb3s\xc0\xbb': None,
    '\xb0\xaa\xaf\xc5\xa5\xb2\xb1\xfe': None,
    '\xb0\xaa\xaf\xc5\xb1j\xa7\xa7': None,
    '\xb0\xaa\xaf\xc5\xb1j\xa4O': None,
    '\xb0\xaa\xaf\xc5\xc6F\xb3q\xb3N': None,
    '\xb0\xaa\xaf\xc5\xb0\xbd\xc5\xa7': None,
    '\xb0\xaa\xaf\xc5\xaf\xab\xaf\xa7': None,
    '\xb2\xd7\xaf\xc5\xb3s\xc0\xbb': None,
    '\xb2\xd7\xaf\xc5\xaak\xb3N\xb3s\xc0\xbb': None,
    '\xb2\xd7\xaf\xc5\xc5X\xb0\xad\xb3N': None,
    '\xb2\xd7\xaf\xc5\xaf\xab\xb8\xf1': None,
    '\xb2\xd7\xaf\xc5\xa5\xb2\xb1\xfe': None,
    '\xb2\xd7\xaf\xc5\xa9\xaf\xb9B': None,
    '\xb2\xd7\xaf\xc5\xb1j\xa7\xa7': None,
    '\xb2\xd7\xaf\xc5\xb1j\xa4O': None,
    '\xb2\xd7\xaf\xc5\xc6F\xb3q\xb3N': None,
    '\xb2\xd7\xaf\xc5\xb0{\xc0\xbb': None,
    '\xb2\xd7\xaf\xc5\xb0\xbd\xc5\xa7': None,
    '\xb2\xd7\xaf\xc5\xc5]\xaak\xa4\xd1\xa5\xf7': None,
    '\xb2\xd7\xaf\xc5\xaf\xab\xaf\xa7': None,
    '\xc5]\xaak\xbc\xe7\xa4O': None,
    '\xa5\xcd\xa9R\xbc\xe7\xa4O': None,
    '\xacr\xa4\xfa\xbc\xb9\xabr': None,
    '\xacr\xa9\xca\xaa\xda\xad\xbb': None,
    '\xc5]\xaak\xacr\xa9G': None,
    '\xbbG\xbbk\xacr\xaf\xbb': None,
    '\xa7l\xa6\xe5\xa7\xf0\xc0\xbb': None,
    '\xc2\xed\xbb\xee': None,
    '\xad\xb8\xacP\xb6\xc3\xbbR': None,
    '\xbcC\xae\xf0\xa5|\xaeg': None,
    '\xb6\xc3\xbbR\xbd\xc4\xc0\xbb': None,
    '\xa4\xf4\xc0\xbb': None,
    '\xa4\xf5\xa7\xf0': None,
    '\xaf\xab\xbb@': None,
    '\xb8\xa8\xb9p': None,
    '\xa9\xc0\xa4O\xad\xb8\xbcu': None,
    '\xba\xeb\xaf\xab\xa5\xb4\xc0\xbb': None,
    '\xa4`\xc6F\xae\xf0\xbdb': None,
    '\xb0\xad\xa4\xf6\xad\xb8\xc0\xbb': None,
    '\xa7\xaf\xae\xf0\xc4\xf1\xc2\xb6': None,
    '\xc5]\xa4b\xa7\xeb\xc2Y': None,
    '\xafP\xaa\xa2\xc3z\xaf}': None,
    '\xa4\xd1\xb9p\xa6a\xa4\xf5': None,
    '\xb7N\xa9\xc0\xb5L\xb1`': None,
    '\xab\xd5\xad\xdf\xb0\xad\xa7P': None,
    '\xa7\xaf\xae\xf0\xbd\xc4\xa4\xd1': None,
    '\xb0\xad\xbb\xee\xa9\xca\xbd\xe8': None,
    '\xb0l\xc0\xbb': None,
    '\xae\xa3\xa9\xc6': None,
    '\xc4\xeb\xac\xb9': None,
    '\xb0\xbb\xb9\xee': None,
    '\xb4A\xaf\xba': None,
    '\xb1\xcb\xa8\xad\xa4@\xb7i': None,
    '\xb9j\xa4s\xa5\xb4\xa4\xfb': None,
    '\xc3~\xa4\xfd\xa5O': None,
    '\xb1M\xaa`\xb3s\xc0\xbb': None,
    '\xa6\xc3\xacV': None,
    '\xa8\xf3\xa6P\xa7\xf0\xc0\xbb': None,
    '\xaf\xe0\xb6q\xaai\xb0\xca': None,
    '\xaak\xb3N\xa5\xb2\xb1\xfe': None,
    '\xb0\xaa\xaf\xc5\xaak\xb3N\xa5\xb2\xb1\xfe': None,
    '\xb2\xd7\xaf\xc5\xaak\xb3N\xa5\xb2\xb1\xfe': None,
    '\xaf\xab\xa4\xa7\xa6g\xbc\xc4': None,
    '\xb0\xaa\xaf\xc5\xaf\xab\xa4\xa7\xa6g\xbc\xc4': None,
    '\xb2\xd7\xaf\xc5\xaf\xab\xa4\xa7\xa6g\xbc\xc4': None }
NONE_SHOUJUE_TIPS = '\xb1z\xa8S\xa6\xb3\xb5\xb9\xa4\xa9\xa5\xf4\xa6\xf3\xaa\xab\xab~\xa9\xce\xaa\xf7\xbf\xfa'
NO_ENOUGH_SHOUJUE_TIPS = '\xbd\xd0\xb5\xb9\xa4\xa9#Y5#n\xa5\xbb\xa5\xce\xa9\xf3\xa7I\xb4\xab\xaa\xba\xb5}\xa6\xb3\xafS\xae\xed\xc3~\xb3Z'
g_Give = None
g_NpcID = 0
g_ItemTips = None

def ModuleReset():
    global g_Give, g_NpcID, g_ItemTips
    g_Give = None
    g_NpcID = 0
    g_ItemTips = None


def GetGive():
    if g_Give:
        return g_Give
    


def OnShoujueSendCB(lstShoujue):
    if len(lstShoujue) <= 0:
        usermacro.PROMPT_MSG(NONE_SHOUJUE_TIPS)
    elif len(lstShoujue) < 5 or len(lstShoujue) > 5:
        usermacro.PROMPT_MSG(NO_ENOUGH_SHOUJUE_TIPS)
    elif len(lstShoujue) == 5:
        net2019double12shop.C2GSChangeShoujue(lstShoujue)
    


def CloseClientOpenGiveDlg():
    if g_Give and g_Give.GetIsClientOpen():
        CloseWindow()
    


def CheckEquipCanTask(oItem):
    '''
\t\xc0\xcb\xb4\xfa\xb8\xcb\xb3\xc6\xacO\xa7_\xa5i\xa5H\xb7\xed\xa7@\xb9D\xa8\xe3\xb4\xa3\xa5\xe6\xa5\xf4\xb0\xc8 \xa4K\xa8\xf6\xa1B\xba\xb2\xb7\xd2\xa4\xa4\xa1B\xc6^\xb4O\xc4_\xa5\xdb\xa4\xa3\xa5i\xb4\xa3\xa5\xe6\xa1B\xbc\xd2\xa8\xe3
\t:param oItem:
\t:return:
\t'''
    if oItem.GetExtInfo('Grossip') and oItem.GetExtInfo('Fenjie') and getattr(oItem, 'm_dGemList', None) or oItem.GetKey() & item.MARK_MODUL:
        return False
    
    return True


class _PetCheckBox(interface.CCheckBox):
    
    def RightUp(self):
        import dlggetinfo
        import hero
        dlggetinfo.ShowSummonInfo(self.GetParent().GetParent(), 20, 20, hero.g_ID, self.m_PetID, self.m_Shape, self.m_Name)



class _GivePetBox(interface.CCheckBox):
    
    def RightUp(self):
        if self.m_PetID != 0:
            import dlggetinfo
            import hero
            dlggetinfo.ShowSummonInfo(self.GetParent(), 20, 20, hero.g_ID, self.m_PetID, self.m_PetInfo[0], self.m_PetInfo[1])
        



class _CGiveItem(interface.CClickBox):
    
    def __init__(self, parent, x, y, igs_idx, mid):
        interface.CClickBox.__init__(self, parent, 146, 52, alpha = 0, msgid = mid)
        self.SetPos(x, y)
        
        try:
            give_list = parent.GetObject('give_list')
            give_list.m_Imagess[igs_idx].SetFrame(0)
            self.m_ParentBG = interface.CShadowObject(give_list.m_Imagess[igs_idx])
        except IndexError:
            return None

        self.m_Selected = False
        self.m_ItemType = 0
        self.m_ID = 0
        self.m_Icon = None
        self.m_Quantity = 0
        self.m_MaxQuantity = 0
        self.m_QuantityTxtObj = None
        self.m_EquipTypeTxt = None
        self.m_iItemShape = 0
        self.m_NameDesc = None
        self.m_QuantityDesc = None
        self.m_NameTxtObj = None

    
    def PushItem(self, it):
        import item
        self.m_ItemType = 1
        self.m_ID = it.m_ID
        self.m_iItemShape = it.m_Shape
        self.m_Icon = item.CreateItem44Image(self, it.m_Shape)
        self.m_Icon.SetPos(3, 3)
        self.m_MaxQuantity = it.m_Quantity
        import itemdata
        import itemdefine
        sName = ''
        if it.m_Shape == itemdefine.ITEM_PETNEIDAN:
            sName = it.GetExtName()
        
        if not sName:
            sName = itemdata.GetItemServerName(it)
            if not sName:
                sName = itemdata.GetData(it.m_Shape)[0]
            
        
        color = interface.COLOR_7
        self.m_NameDesc = interface.CTextObject(self, sName, interface.FontLT12_1, color, 0)
        self.m_NameDesc.SetPos(58, 10)
        self.ShowModelTips(it.GetKey() & item.MARK_MODUL != 0)

    
    def ShowModelTips(self, bShow):
        if bShow:
            self.m_EquipTypeTxt = interface.CTextObject(self, '\xbc\xd2\xa8\xe3', interface.FontST12E, [
                3357517,
                16777215], 0)
            self.m_EquipTypeTxt.SetZ(1)
            (iTxtW, iTxtH) = self.m_EquipTypeTxt.GetSize()
            tSpace = (2, 6)
            self.m_EquipTypeTxt.SetPos(50 - iTxtW - tSpace[0], tSpace[1])
        else:
            self.m_EquipTypeTxt = None

    
    def AddItemQuantity(self, quantity):
        self.m_Quantity += quantity
        if self.m_Quantity > self.m_MaxQuantity:
            self.m_Quantity = self.m_MaxQuantity
        
        if self.m_Quantity <= 0:
            self.PopItem()
            return None
        
        if self.m_Quantity >= 1:
            self.m_QuantityTxtObj = interface.CTextObject(self.m_Icon, '%3d' % self.m_Quantity, interface.FontLT14E_1, 16777215, 0)
            self.m_QuantityTxtObj.SetPos(20, 28)
        
        color = interface.COLOR_7
        self.m_QuantityDesc = interface.CTextObject(self, '\xbc\xc6\xb6q\xa1G%d' % self.m_Quantity, interface.FontLT12_1, color, 0)
        self.m_QuantityDesc.SetPos(58, 27)

    
    def PopItem(self):
        self.m_ItemType = 0
        self.m_Icon = None
        self.m_Quantity = 0
        self.m_MaxQuantity = 0
        self.m_QuantityTxtObj = None
        self.m_iItemShape = 0
        self.m_NameDesc = None
        self.m_QuantityDesc = None
        self.GetParent().PopItem(self.m_ID)
        self.m_ID = 0

    
    def PushPet(self, petid):
        import pet
        petobj = pet.GetPet(petid)
        if petobj is None:
            return None
        
        self.m_ItemType = 2
        self.m_ID = petid
        
        try:
            self.m_Icon = ui.CImage(self, 'photo/summon/%04d.igs' % petobj.m_Prop.m_Shape, 'misc')
        except:
            self.m_Icon = ui.CImage(self, 'photo/summon/0000.igs', 'misc')

        self.m_Icon.SetPos(3, 3)
        self.m_NameDesc = interface.CTextObject(self.m_Icon, petobj.m_Prop.m_Name, interface.FontLT14_3, interface.COLOR_1, 0)
        self.m_NameDesc.SetPos(58, 16)

    
    def PopPet(self):
        self.m_ItemType = 0
        self.m_Icon = None
        self.m_NameDesc = None
        self.GetParent().PopPet(self.m_ID)
        self.m_ID = 0

    
    def Enter(self):
        global g_ItemTips
        if tipsclosemgr.IsHandle():
            return None
        
        import item
        import dlggetinfo
        if getattr(self, 'm_ID', None):
            it = item.GetItem(self.m_ID)
            if it:
                g_ItemTips = dlggetinfo.ShowItemInfo(it)
                g_ItemTips.SetOwner(self)
                tipsclosemgr.Regist(g_ItemTips)
            
        
        if self.m_Selected:
            return None
        
        if self.m_ParentBG.Get():
            self.m_ParentBG.Get().SetFrame(2)
        

    
    def Leave(self):
        global g_ItemTips
        tipsclosemgr.CheckClose()
        g_ItemTips = None
        if self.m_Selected:
            return None
        
        if self.m_ParentBG.Get():
            self.m_ParentBG.Get().SetFrame(0)
        

    
    def SetCheck(self, flag):
        self.m_Selected = flag
        igs = self.m_ParentBG.Get()
        if igs is None:
            return None
        
        if flag:
            igs.SetFrame(1)
        else:
            igs.SetFrame(0)

    
    def GetShape(self):
        return self.m_iItemShape

    
    def GetID(self):
        return self.m_ID

    
    def GetItemQuantity(self):
        return self.m_Quantity



class CInterfaceItem(item.CInterfaceItem):
    
    def Enter(self):
        item.CInterfaceItem.Enter(self)
        taskid = getattr(self.GetParent(), 'm_TaskID', 0)
        if self.IsSubmitItem(taskid) and taskid not in (14259, 12820):
            self.m_EnterTips = wrapinterface.CTextTips(None, -1, '\xc2\xf9\xc0\xbb\xa5i\xaa\xbd\xb1\xb5\xa7\xb9\xa6\xa8\xa4W\xa5\xe6', interface.FontLT12_1, direct = 1)
            self.m_EnterTips.SetOwner(self)
        

    
    def Leave(self):
        item.CInterfaceItem.Leave(self)
        self.m_EnterTips = None

    
    def IsSubmitItem(self, taskid):
        import itemdata
        itemObj = self.GetItem()
        if not taskid and not itemObj or self.GetShadow():
            return False
        
        if itemdata.IsType(itemObj.m_Shape, 'equip') and not getattr(itemObj, 'm_IsMark', 0):
            return False
        
        return True



class CMyTipsBox(interface.CNotifyBox):
    
    def __init__(self, parent):
        (w, h) = parent.GetSize()
        interface.CNotifyBox.__init__(self, parent, w, h, color = 0, alpha = 0, msgid = 0)

    
    def Enter(self):
        par = self.G"()
        if not par:
            return None
        
        self.m_Tips = wrapinterface.CTextTips(None, -1, '\xc2\xf9\xc0\xbb\xa5i\xaa\xbd\xb1\xb5\xa7\xb9\xa6\xa8\xa4W\xa5\xe6', interface.FontLT12_1, direct = 1)
        self.m_Tips.SetOwner(par)
        par.Enter()

    
    def Leave(self):
        self.m_Tips = None
        par = self.G"()
        if not par:
            return None
        
        par.Leave()

    
    def MouseWheelDown(self, p):
        par = self.G"()
        if not par:
            return None
        
        par.MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        par = self.G"()
        if not par:
            return None
        
        par.MouseWheelUp(p)



class CImageBoxWithLock(wrapinterface.CImageBoxWithTips, interface.CBase):
    
    def LeftUp(self):
        import pet
        import netplayer
        if not hasattr(self, 'm_PetID') or not (self.m_PetID):
            return None
        
        if not pet.GetPet(self.m_PetID):
            return None
        
        netplayer.C2SPetUnLock([
            self.m_PetID])



class CGive(combdialog.CCombDialog):
    GTYPE_ITEM = 0
    GTYPE_PET = 1
    GTYPE_ALL = 2
    GTYPE_GIVE_BY_NAME = 3
    GTYPE_COMPATIBLE = 4
    GTYPE_EQUIP = 5
    GTYPE_RELIC = 6
    GTYPE_TREASURE = 7
    GTYPE_NOT_APPRAISAL_TREASURE = 8
    GTYPE_NOT_SOUL_BIND_PET = 9
    GTYPE_WEAPON = 10
    GTYPE_FAIRY = 11
    GTYPE_ANUBISI_STONE = 12
    GTYPE_FLOWER = 13
    sUIName = 'dialog/give.dlg'
    
    def __init__(self, npcname, isnpc = False, taskid = 0, npcid = 0, npctitle = '', bClientOpen = False, bCloseCashEdit = False, oClientSendCB = None):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel)
        import ratio
        if ratio.Is800x600():
            self.SetPos(120, 40)
        else:
            interface.Center(self)
        self.m_DlgHelpID = 5506
        self.m_TaskID = taskid
        self.m_NpcID = npcid
        self.m_IsNpc = isnpc
        self.m_bClientOpen = bClientOpen
        self.m_GiveType = 0
        self.m_GiveCall = None
        self.m_bShowDrugBox = False
        self.m_iGiveItemID = []
        self.m_oClientSendCB = None if oClientSendCB else None
        self.m_bIsCloseCashEdit = bCloseCashEdit
        self.m_CashEdit = None
        self.CreateNpcName(npcid, npcname)
        self.CreateNpcRelationTxt(npcid)
        self.CreateUnCloseBox()
        self.CreateGetItems()
        self.CreateInputEdit()
        self.CreateCashTxt()
        self.CreateinterfaceItems()
        import BlankFrame
        BlankFrame.DestroyBlank(self)
        self.UpdateBag(taskid)
        self.CreateShadow(npcname, npctitle)
        CloseOtherUI()
        self.InitSingle()
        self.InitDrugBag()
        import mdpropitem
        oPropItem = mdpropitem.GetModel()
        oPropItem.ssConnect(oPropItem.SS_UpdateBagChange, self.OnUpdateBagChange)

    
    def OnUpdateBagChange(self, *args):
        if self.m_TaskID:
            self.UpdateBag(self.m_TaskID)
        

    
    def GetIsClientOpen(self):
        return self.m_bClientOpen

    
    def InitDrugBag(self):
        import dlgpizza
        import task
        if task.CheckTaskNeedDrug(self.m_TaskID) and item.GetDragBagID():
            dlgpizza.ShowBagWithParent(item.GetDragBagID(), self, self.m_TaskID)
        

    
    def InitSingle(self):
        import commoncb
        commoncb.RegistCB(commoncb.USE_FLYITEM, self, 'CloseWindow')

    
    def CreateNpcName(self, npcid, npcname):
        import friend
        import wrapui
        import combmacro
        if not self.m_IsNpc:
            npcname = friend.GetShowName(npcid, npcname)
        
        (_, npcname, _) = wrapui.HandleLink(npcname)
        font = interface.FontLT14_10
        color = interface.COLOR_291
        self.m_NpcNameObj = combmacro.CTEXT(interface.CTextObject, 'npcname', self, npcname, font, color)

    
    def CreateShadow(self, npcname, npctitle):
        name2func = {
            '\xbb\xaf\xa4\xbd\xa9\xfa': ('\xb0]\xaf\xab', self.UpdateCaiShenBg),
            '\xc5\xb3\xa9w\xaev': ('', self.UpdateJianDing),
            '\xb2\xe2\xad\xb7\xa1P\xbc\xb3\xae\xd2': ('\xb8\xd1\xb8j\xaf\xe0\xa4\xe2', self.UpdateJieBang) }
        if self.m_IsNpc and name2func.get(npcname, None) and name2func[npcname][0] == npctitle:
            func = name2func[npcname][1]
            func()
        

    
    def UpdateJieBang(self):
        self.m_IsPetUnBand = True

    
    def UpdateJianDing(self):
        import itemdata
        for f, itf in self.m_InterfaceItems.items():
            if itf.m_Item and itemdata.IsType(itf.m_Item.m_Shape, 'equip') and itf.m_Item.m_Key & item.MARK_JIANDING == 0:
                itf.Enable(True)
                itf.ShowShadow(False)
                continue
            itf.Enable(False)
            itf.ShowShadow(True)
        

    
    def UpdateCaiShenBg(self):
        import caishendata
        for k, itf in self.m_InterfaceItems.items():
            if (itf.m_Item is None or caishendata.IsSale2CaiShen(itf.m_Item.m_Shape)) and itf.m_Item.m_Key & item.MARK_JINGPIN == 0 and itf.m_Item.m_Key & item.MARK_BOUND != 0:
                itf.Enable(True)
                itf.ShowShadow(False)
                if itf.m_Item:
                    if self.IsSpecialItem(itf.m_Item):
                        itf.Enable(False)
                        itf.ShowShadow(True)
                    
                
            itf.m_Item
            itf.Enable(False)
            itf.ShowShadow(True)
        

    
    def IsSpecialItem(self, itemObj):
        iFlag1 = itemObj.m_Shape in (25077, 25078)
        if itemObj.m_Shape in (70472, 70260, 72134):
            pass
        iFlag2 = getattr(itemObj, 'm_RecoverFlag', None) == 0
        if iFlag1 or iFlag2:
            return True
        
        return False

    
    def CreateNpcRelationTxt(self, npcid):
        import friend
        import hero
        if npcid == hero.GetHeroID():
            relation = '\xa6\xdb\xa4v'
            color = interface.COLOR_395
        elif friend.IsFriend(npcid, 0):
            relation = '\xa6n\xa4\xcd'
            color = interface.COLOR_395
        elif friend.IsFriend(npcid, 1):
            relation = '\xc1{\xae\xc9\xb9\xef\xb8\xdc'
            color = 16711935
        elif self.m_IsNpc or self.m_bClientOpen:
            relation = ''
        else:
            relation = '\xad\xaf\xa5\xcd\xa4H'
            color = interface.COLOR_394
        if self.m_NpcNameObj and relation:
            (x, y) = self.m_NpcNameObj.GetPos()
            (w, h) = self.m_NpcNameObj.GetSize()
            offsetx = style.GetInt('dialog/give.dlg', 'data_txt_offset')
            classtype = None if interface.IsNewStyle() else interface.COverstrikingTextObject
            self.m_RelationTxt = classtype(self, relation, interface.FontLT14_3, color, 0)
            self.m_RelationTxt.SetPos(x + w + offsetx, y)
        

    
    def CreateGetItems(self):
        self.m_GiveItems = []
        listobj = self.GetObject('give_list')
        if listobj:
            (x, y) = listobj.GetPos()
            for i in xrange(listobj.GetTotal()):
                it = _CGiveItem(self, x, y + i * 54, i, i + 50)
                self.m_GiveItems.append(it)
            
        

    
    def CreateInputEdit(self):
        import combmacro
        import wrapedit
        self.m_CashEdit = combmacro.CEDIT(wrapedit.CLimitNumberEdit, 'give_cash', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_CashEdit.m_IsMoney = True
        self.m_CashEdit.Active(True)
        self.m_CashEdit.SetLimit(9)

    
    def CreateCashTxt(self):
        import hero
        hero.CreateCombDlgCash('cash', 'Dlggive', (('m_Cash', 0, 0),), self)
        propItem = hero.g_Name2PropItem['m_Cash']
        propItem.AddRefreshCallbackWithID('editcash', self.OnCashRefresh)

    
    def CreateinterfaceItems(self):
        import combmacro
        self.m_InterfaceItems = { }
        combmacro.CITEMAREA(CInterfaceItem, 'itembox', self, item.ITEM_START, self.m_InterfaceItems, 100)
        combmacro.CITEMAREA(CInterfaceItem, 'fight_item_box', self, item.ITEM_FIGHT_START, self.m_InterfaceItems, 100)
        combmacro.CITEMAREA(CInterfaceItem, 'itembox2', self, item.ITEM_SCOPE, self.m_InterfaceItems, 100)
        item.AddInterfaceCallback(self.m_InterfaceItems, item.ITEM_NORMAL, oRefObj = self)

    
    def ReleaseInterfaceCallback(self):
        item.ReleaseInterfaceCallback(self.m_InterfaceItems, item.ITEM_NORMAL)

    
    def OnCashRefresh(self):
        import hero
        iMax = hero.g_Prop.m_Cash
        if iMax < 0:
            iMax = 0
        
        if self.m_CashEdit:
            self.m_CashEdit.SetMaxNum(iMax)
            if self.m_CashEdit.GetText():
                self.m_CashEdit.DoTextLimit()
                self.m_CashEdit.TextChange()
            
        

    
    def CreateUnCloseBox(self):
        
        class CUnCloseBox(interface.CClickBox):
            
            def RightUp(self):
                pass


        self.m_UnCloseBox = []
        ctrlLst = ('give_list', 'itembox', 'fight_item_box', 'itembox2', 'petlist')
        for name in ctrlLst:
            oWidget = self.GetObject(name)
            if oWidget:
                (w, h) = oWidget.GetSize()
                box = CUnCloseBox(oWidget, w, h, alpha = 0)
                box.SetZ(-1)
                self.m_UnCloseBox.append(box)
                continue
        

    
    def UpdateBag(self, taskid):
        '''
\t\tinit\xae\xc9\xbd\xd5\xa5\xce\xaa\xbaupdatebag\xae\xda\xbe\xda\xa5\xf4\xb0\xc8ID\xa8\xea\xb7s\xa4F\xa4@\xa6\xb8\xb9\xcf\xbc\xd0\xbbX\xaa\xa9
\t\tinit\xa4\xa7\xab\xe1\xbd\xd5\xa5\xce\xa4F\xa4@\xa6\xb8CreateShadow()\xa4\xe8\xaak\xa1A\xa8\xcf\xb1o\xb0]\xaf\xab\xa4\xa7\xc3\xfe\xb5\xb9\xa4\xa9\xac\xc9\xad\xb1\xaa\xba\xbbX\xaa\xa9\xa5i\xa5H\xa5\xbf\xb1`\xc5\xe3\xa5\xdc
\t\t\xa6b\xa8\xe4\xa5L\xa6a\xa4\xe8\xbd\xd5\xa5\xce\xa6\xb9\xb1\xb5\xa4f\xa1A\xadn\xaa`\xb7N\xb0\xb5\xad\xad\xa8\xee\xa1A\xc1\xd7\xa7K\xa7\xe2CreateShadow()\xb3\xd0\xab\xd8\xaa\xba\xbbX\xaa\xa9\xbb~\xa7R
\t\t:param taskid:
\t\t:return:
\t\t'''
        import hero
        import task
        import ignorebindshape
        import iteminterface
        import itemdata
        size = hero.g_Prop.m_BagMax
        lItemID = [ a.GetShape() for a in self.m_GiveItems ]
        bShowDrugBox = False
        for pos in self.m_InterfaceItems:
            if not pos - item.ITEM_SCOPE < size:
                pass
            valid = [] if pos <= pos else pos < item.ITEM_FIGHT_SCOPE
            iit = self.m_InterfaceItems[pos]
            it = iit.GetItem()
            if not (self.m_IsNpc) and it and it.m_Shape not in ignorebindshape.IgnoreBindshapeLst:
                if it.m_Key & item.MARK_BOUND != 0 or it.m_Key & item.MARK_JINGPIN != 0:
                    valid = False
                
            
            if it and taskid:
                if valid:
                    pass
                valid = task.IsTaskItem(taskid, it.m_Shape)
                if valid and iteminterface.IsEquip(it):
                    if not CheckEquipCanTask(it):
                        valid = False
                    
                
                if self.m_TaskID in (14257, 14258, 14259) and it.m_Shape in task.G)8NecessaryItems(self.m_TaskID):
                    valid = self.IsNeedJobDoubleItem(it.m_Shape, lItemID)
                
                if valid and itemdata.IsType(it.m_Shape, 'gem') and item.GetItemLevel(it) > 5:
                    valid = False
                
                if not bShowDrugBox and itemdata.IsType(it.m_Shape, 'drug'):
                    bShowDrugBox = True
                
            
            if not it:
                valid = False
            
            iit.Enable(valid)
            iit.ShowShadow(not valid)
            self.m_bShowDrugBox = bShowDrugBox
        

    
    def OnShiMenSwitchPage(self, taskid):
        import task
        bFristPage = False
        bSecondPage = False
        for pos in self.m_InterfaceItems:
            iit = self.m_InterfaceItems[pos]
            it = iit.GetItem()
            if it and taskid:
                if it.m_Shape in task.G)8NecessaryItems(self.m_TaskID):
                    if pos in xrange(item.ITEM_START, item.ITEM_SCOPE - 1) or pos in xrange(item.ITEM_FIGHT_START, item.ITEM_FIGHT_SCOPE):
                        bFristPage = True
                    
                    if pos in xrange(item.ITEM_SCOPE, item.ITEM_FIGHT_START):
                        bSecondPage = True
                    
                
            it.m_Shape in task.G)8NecessaryItems(self.m_TaskID)
        
        if not bFristPage and bSecondPage:
            if g_Give:
                g_Give.GetObject('btn_bag').LeftUp()
            
        

    
    def IsNeedJobDoubleItem(self, iShape, lItemID):
        import task
        iSingleItemCount = 0
        for iItemID in lItemID:
            if iItemID == iShape:
                iSingleItemCount += 1
                continue
        
        if iShape in lItemID:
            dNeedItem = task.GetNecessaryItemAmount(self.m_TaskID)
            if dNeedItem:
                if dNeedItem.get(iShape, 0) <= iSingleItemCount:
                    return False
                
            
        
        return True

    
    def IsChildDrugTask(self, itemObj, shapeList):
        import task
        if itemObj and self.m_TaskID in (10080, 10201):
            for shape in shapeList:
                if task.IsConformMedicine(shape, itemObj.m_Shape, itemObj.m_ID):
                    return True
                    continue
            
        
        return False

    
    def ShowClientOpenItem(self, iItemList):
        import hero
        iSize = hero.GetProp('m_BagMax', 0)
        for iPos in self.m_InterfaceItems:
            if not iPos - item.ITEM_SCOPE < iSize:
                if iPos <= iPos:
                    pass
                elif iPos < item.ITEM_FIGHT_SCOPE:
                    oIit = self.m_InterfaceItems[iPos]
                    oIt = oIit.GetItem()
                    if oIt and oIt.m_ID not in iItemList:
                        oIit.Enable(False)
                        oIit.ShowShadow(True)
                    elif oIt and oIt.m_ID in iItemList:
                        oIit.Enable(True)
                        oIit.ShowShadow(False)
                    
            oIt.m_ID in iItemList
        

    
    def ShowShadow(self, shapeList):
        import hero
        import task
        size = hero.g_Prop.m_BagMax
        for pos in self.m_InterfaceItems:
            if not pos - item.ITEM_SCOPE < size:
                if pos <= pos:
                    pass
                elif pos < item.ITEM_FIGHT_SCOPE:
                    iit = self.m_InterfaceItems[pos]
                    it = iit.GetItem()
                    if it and not task.IsShapeSatisfy(shapeList, it.m_Shape):
                        iit.Enable(False)
                        iit.ShowShadow(True)
                    
                    if self.IsChildDrugTask(it, shapeList):
                        iit.Enable(True)
                        iit.ShowShadow(False)
                    
            self.IsChildDrugTask(it, shapeList)
        

    
    def AddShadowByID(self, itemIDLst):
        import hero
        size = hero.g_Prop.m_BagMax
        for pos in self.m_InterfaceItems:
            if not pos - item.ITEM_SCOPE < size:
                if pos <= pos:
                    pass
                elif pos < item.ITEM_FIGHT_SCOPE:
                    iit = self.m_InterfaceItems[pos]
                    it = iit.GetItem()
                    if it and it.m_ID not in itemIDLst:
                        iit.Enable(False)
                        iit.ShowShadow(True)
                    
            it.m_ID not in itemIDLst
        

    
    def AddShadowByShape(self, iShapeLst, funcCB):
        import hero
        import misc
        size = hero.g_Prop.m_BagMax
        for pos in self.m_InterfaceItems:
            if not pos - item.ITEM_SCOPE < size:
                if pos <= pos:
                    pass
                elif pos < item.ITEM_FIGHT_SCOPE:
                    iit = self.m_InterfaceItems[pos]
                    it = iit.GetItem()
                    if it and it.m_Shape not in iShapeLst:
                        iit.Enable(False)
                        iit.ShowShadow(True)
                    else:
                        iit.Enable(True)
                        iit.ShowShadow(False)
            it.m_Shape not in iShapeLst
        
        self.m_GiveCall = misc.Functor(funcCB)

    
    def GetValidFlag(self, iShape, sType):
        import itemdata
        if sType not in ('mazeitem1',):
            return itemdata.IsType(iShape, sType)
        elif sType == 'mazeitem1':
            if not iShape in (71173, 14372) and itemdata.IsType(iShape, 'mazeitem2'):
                pass
            return itemdata.IsType(iShape, 'mazeitem1')
        elif sType == 'fairy':
            return itemdata.IsType(iShape, sType)
        elif sType == 'flower':
            return iShape in (25426, 30152, 30514, 72218)
        
        return False

    
    def ValidItem(self, sType):
        for iit in self.m_InterfaceItems.values():
            it = iit.GetItem()
            bIsTargetShape = None if it else False
            if it:
                pass
            iit.Enable(bIsTargetShape)
            if it:
                pass
            iit.ShowShadow(not bIsTargetShape)
        

    
    def ValidWeapon(self, sType):
        for iit in self.m_InterfaceItems.values():
            it = iit.GetItem()
            if it and self.GetValidFlag(it.m_Shape, sType):
                iit.Enable(True)
                iit.ShowShadow(False)
                continue
        

    
    def SetGiveType(self, iGiveType, callback = None):
        oItemBtn = self.GetObject('btn_item')
        oPetBtn = self.GetObject('btn_pet')
        self.m_GiveType = iGiveType
        if not self.m_IsNpc:
            oPetBtn.SetShow(False)
        
        if iGiveType in (CGive.GTYPE_PET, CGive.GTYPE_NOT_SOUL_BIND_PET):
            oPetBtn.LeftUp()
            oItemBtn.Enable(False)
            self.GetObject('btn_xingnang').SetShow(False)
            self.GetObject('btn_bag').SetShow(False)
        elif iGiveType in (CGive.GTYPE_ITEM, CGive.GTYPE_GIVE_BY_NAME, CGive.GTYPE_EQUIP, CGive.GTYPE_RELIC, CGive.GTYPE_TREASURE, CGive.GTYPE_NOT_APPRAISAL_TREASURE, CGive.GTYPE_FAIRY):
            oItemBtn.LeftUp()
            oPetBtn.Enable(False)
            self.GetObject('btn_xingnang').LeftUp()
            if self.m_bClientOpen and iGiveType == CGive.GTYPE_ITEM:
                self.SetShowObject('btn_item', False)
            
        elif iGiveType == CGive.GTYPE_COMPATIBLE:
            self.m_GiveCall = callback
            oPetBtn.LeftUp()
            oItemBtn.Enable(False)
            self.GetObject('btn_xingnang').SetShow(False)
            self.GetObject('btn_bag').SetShow(False)
        else:
            oItemBtn.LeftUp()
        if iGiveType == CGive.GTYPE_EQUIP:
            self.ValidItem('equip')
        elif iGiveType == CGive.GTYPE_RELIC:
            self.ValidItem('wenwu')
        elif iGiveType == CGive.GTYPE_TREASURE:
            self.ValidItem('mazeitem1')
        elif iGiveType == CGive.GTYPE_NOT_APPRAISAL_TREASURE:
            self.ValidItem('mazeitem2')
        elif iGiveType == CGive.GTYPE_WEAPON:
            self.ValidWeapon('weapon')
        elif iGiveType == CGive.GTYPE_FAIRY:
            self.ValidItem('fairy')
        elif iGiveType == CGive.GTYPE_ANUBISI_STONE:
            self.ValidItem('anubisi_stone')
        elif iGiveType == CGive.GTYPE_FLOWER:
            self.ValidItem('flower')
            self.CloseCashEdit()
        elif self.m_bIsCloseCashEdit:
            self.CloseCashEdit()
        

    
    def CloseCashEdit(self):
        '''
\t\tflower\xc3\xfe\xab\xac\xa4\xa3\xa4\xb9\xb3\\\xaa\xf7\xbf\xfa\xa5\xe6\xa9\xf6
\t\t:return:
\t\t'''
        if self.m_CashEdit:
            self.m_CashEdit.SetShow(False)
        

    
    def Refresh(self, taskid = 0):
        self._RefreshPetList(taskid)

    
    def PetItemAddTips(self, petobj, it):
        import pet
        import task
        if (petobj.m_Key & 64 == 0 and petobj.m_Prop.m_Grade != 0 and petobj.m_BirthKey & pet.MARK_ISCOLOR == 0 or petobj.m_BirthKey & pet.MARK_ISBAOBAO == 0 or petobj.m_Key & pet.MARK_SOUL_BINDED != 0) and petobj.m_BirthKey == 0:
            necessaryPet = task.g_NecessaryPets.get(self.m_TaskID)
            if necessaryPet and necessaryPet == [
                (petobj.m_Prop.m_Shape, 1)]:
                it.m_TipsBox = CMyTipsBox(it)
            
        

    
    def AddClientOpenItemList(self, iItemId):
        if iItemId not in self.m_iGiveItemID:
            self.m_iGiveItemID.append(iItemId)
        

    
    def RemoveClientOpenItemList(self, iItemId):
        if iItemId in self.m_iGiveItemID:
            self.m_iGiveItemID.remove(iItemId)
        

    
    def _RefreshPetList(self, taskid):
        import pet
        import task
        import petdata
        petlist = self.GetObject('petlist')
        pet_dct = task.GetAllPets()
        petlist.Clear()
        for i, petobj in enumerate(petlst):
            if (petobj.m_Key & 8 != 0) & (self.m_GiveType == 9):
                continue
            
            if getattr(self, 'm_IsPetUnBand', False) and petdata.GetData(petobj.m_Prop.m_Shape)['carry_grade'] > 65:
                continue
            
            item = petlist.AddTextItem('%s\xa1]%d\xaf\xc5\xa1^' % (getattr(petobj.m_Prop, 'm_Name'), getattr(petobj.m_Prop, 'm_Grade')))
            item.m_ID = petobj.m_ID
            self.DealLockPet(item, petobj)
            if isShowDoubleClickTips:
                self.PetItemAddTips(petobj, item)
            
            item.m_Give = False
            item.m_GiveTxtObj = None
        
        petlist.ResetItems()
        petlist.ResetScrollBar()

    
    def DealLockPet(self, oItem, petobj):
        import style
        if petobj.m_Key & 128 != 0:
            lock = CImageBoxWithLock(oItem, style.GetPath('common/itemlock.igs'), '\xa5l\xb3\xea\xc3~\xb8\xd1\xc2\xea', msgid = 100)
            (w, _) = oItem.GetSize()
            (x, y) = style.GetIntTuple('dialog/give.dlg', 'data_pet_pos')
            lock.SetPos(w - x, y)
            oItem.m_LockIgs = lock
            lock.m_PetID = petobj.m_ID
        elif getattr(oItem, 'm_LockIgs', None):
            oItem.m_LockIgs = None
        

    
    def PopItem(self, itemid):
        for iif in self.m_InterfaceItems.values():
            if iif:
                it = iif.GetItem()
                if it and it.m_ID == itemid:
                    iif.Select(False)
                    break
                
            it.m_ID == itemid
        
        if self.m_TaskID in (14257, 14258, 14259):
            self.UpdateBag(self.m_TaskID)
        
        import dlgpizza
        dlgpizza.CancelSelect(itemid)

    
    def _AddItemQuantity(self, iif, quantity):
        for box in self.m_GiveItems:
            if box.m_ItemType == 2:
                usermacro.PROMPT_MSG('\xaa\xab\xab~\xa9M\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xa6P\xae\xc9\xa4W\xac[')
                return None
                continue
        
        it = iif.GetItem()
        if not it:
            return None
        
        container = None
        if not iif.IsSelected():
            for box in self.m_GiveItems:
                if box.m_ItemType not in (1, 2):
                    container = box
                    break
                    continue
            else:
                return None
            container.PushItem(it)
            iif.Select(True)
            if self.m_bClientOpen:
                self.AddClientOpenItemList(it.m_ID)
            
        else:
            for box in self.m_GiveItems:
                if box.m_ID == it.m_ID:
                    container = box
                    break
                    continue
            
        if container:
            pass
        container.AddItemQuantity(quantity)

    
    def AddPet(self, petbox):
        if petbox.m_Give == True:
            return None
        
        for box in self.m_GiveItems:
            if box.m_ItemType == 1:
                usermacro.PROMPT_MSG('\xaa\xab\xab~\xa9M\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xa6P\xae\xc9\xa4W\xac[')
                return None
            
            if box.m_ItemType == 2:
                usermacro.PROMPT_MSG('\xa4@\xa6\xb8\xa5u\xaf\xe0\xb5\xb9\xa4\xa9\xa4@\xb0\xa6\xa5l\xb3\xea\xc3~')
                return None
                continue
        
        for box in self.m_GiveItems:
            if box.m_ItemType != 2:
                box.PushPet(petbox.m_ID)
                break
                continue
        
        petbox.m_Give = True
        txtobj = interface.CTextObject(petbox, '\xb5\xb9', interface.FontLT12_1, interface.COLOR_30)
        txtobj.SetPos(195, 2)
        petbox.m_GiveTxtObj = txtobj

    
    def PopPet(self, petid):
        petlist = self.GetObject('petlist')
        for petbox in petlist.m_Items:
            if petbox.m_ID == petid:
                petbox.m_Give = False
                petbox.m_GiveTxtObj = None
                break
                continue
        

    
    def _GetGiveItems(self):
        items = []
        for box in self.m_GiveItems:
            if box.m_ItemType == 1:
                items.append((box.m_ID, box.m_Quantity))
                continue
        
        return items

    
    def _GetGivePets(self):
        pets = []
        for box in self.m_GiveItems:
            if box.m_ItemType == 2:
                pets.append(box.m_ID)
            
            return pets
        

    
    def GetGivePets(self):
        return self._GetGivePets()

    
    def GetGiveItems(self):
        return self._GetGiveItems()

    
    def CheckGemLevel(self, pos):
        
        def GetGemLelve(info):
            import re
            pat = re.compile('\xb5\xa5\xaf\xc5 (\\d+)')
            mo = pat.match(info)
            if mo:
                return int(mo.group(1))
            else:
                return 0

        iif = self.m_InterfaceItems[pos]
        it = iif.GetItem()
        if it.m_Shape in GEMID and it.m_InfoExt:
            level = GetGemLelve(it.m_InfoExt)
            return level
        
        return 0

    
    def CheckYaoJueLevel(self, pos):
        iif = self.m_InterfaceItems[pos]
        it = iif.GetItem()
        if it.m_Shape != 25405:
            return None
        
        if not it.m_InfoExt:
            return None
        
        ext = it.m_InfoExt
        idx = ext.find('#K\xa1G')
        if idx > 0:
            name = ext[:idx]
            if name in BOOK_LIST:
                return name
            
        

    
    def ClickPetList(self, idx):
        petlist = self.GetObject('petlist')
        petbox = petlist.m_Items[idx]
        if petbox.m_Give == True:
            return None
        
        import pet
        petobj = pet.GetPet(petbox.m_ID)
        if petobj and petobj.m_Key & 128 != 0:
            usermacro.PROMPT_MSG('\xa4W\xc2\xea\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xb5\xb9\xa4\xa9')
            return None
        
        self.AddPet(petbox)

    
    def DoubleClickPetList(self, idx):
        import netnpc
        import pet
        petlist = self.GetObject('petlist')
        petbox = petlist.m_Items[idx]
        if not hasattr(petbox, 'm_TipsBox'):
            return None
        
        pid = petbox.m_ID
        if not g_NpcID:
            return None
        
        if not self.IsTaskEnableAutoGive():
            return None
        
        petobj = pet.GetPet(petbox.m_ID)
        if petobj and petobj.m_Key & 128 != 0:
            usermacro.PROMPT_MSG('\xa4W\xc2\xea\xaa\xba\xa5l\xb3\xea\xc3~\xa4\xa3\xaf\xe0\xb5\xb9\xa4\xa9')
            return None
        
        netnpc.C2SNpcGive(netnpc.GIVETYPE_PET, g_NpcID, 0, [
            pid])
        if self.m_CashEdit:
            self.m_CashEdit.Active(False)
        
        self.SetShow(False)

    
    def OnGiveItem(self, pos, bAll):
        import commondialog
        import itemdata
        if pos not in self.m_InterfaceItems:
            return None
        
        iif = self.m_InterfaceItems[pos]
        it = iif.GetItem()
        if it is None:
            return None
        
        
        def domake(dlg):
            self._AddItemQuantity(iif, quantity)

        quantity = (None, None, None) if bAll else 1
        level = int(self.CheckGemLevel(pos))
        yaoJueName = self.CheckYaoJueLevel(pos)
        specialGemLst = (26002, 26003, 26010, 26011, 26012, 26013, 26014, 26015, itemdefine.ID_GEM_BLUE, itemdefine.ID_GEM_YELLOW, itemdefine.ID_GEM_XIAN, itemdefine.ID_GEM_GUI, itemdefine.ID_GEM_ZHI, itemdefine.ID_GEM_YAO, itemdefine.ID_GEM_NIAN, itemdefine.ID_GEM_BUCHI)
        txt = None
        if self.m_GiveType == CGive.GTYPE_FAIRY and len(self._GetGiveItems()) >= 2:
            usermacro.PROMPT_MSG('\xa5u\xbb\xdd\xa8\xe2\xb0\xa6\xa4p\xba\xeb\xc6F\xa7Y\xa5i\xb6i\xa6\xe6\xb7\xd8\xbf\xf4')
            return None
        
        iGasLevel = it.GetGasLevel()
        if self.m_IsNpc and level > 1:
            if it.m_Shape not in specialGemLst or level >= 5:
                name = itemdata.GetData(it.m_Shape)[0]
                txt = '\xb1z\xb5\xb9\xa4\xa9\xaa\xba#R%s#n\xaa\xba\xb5\xa5\xaf\xc5\xac\xb0#R%d#n\xaf\xc5\xa1A\xbd\xd0\xb0\xdd\xacO\xa7_\xc4~\xc4\xf2?' % (name, level)
            
        elif iGasLevel >= 2 and itemdata.IsType(it.GetShape(), 'baigua'):
            sName = itemdata.GetData(it.GetShape())[0]
            import builddefine
            txt = '\xa7A\xb4\xa3\xa5\xe6\xaa\xba\xacO#R%s#n\xaa\xba%s\xa1A\xbdT\xbb{\xc4~\xc4\xf2\xb4\xa3\xa5\xe6\xb6\xdc?' % (builddefine.PinZhi2Gas[iGasLevel], sName)
        elif yaoJueName:
            txt = '\xb1z\xb5\xb9\xa4\xa9\xaa\xba\xacO#R\xc5]\xc3~\xadn\xb3Z\xa1P%s#n\xa1A\xacO\xa7_\xbdT\xa9w\xc4~\xc4\xf2?' % yaoJueName
        
        if txt:
            commondialog.ShowMessageBox(txt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (domake, None))
        else:
            self._AddItemQuantity(iif, quantity)

    
    def ClickOpenSend(self):
        if self.m_oClientSendCB:
            iGiveIDList = self.m_iGiveItemID
            if self.m_GiveType == CGive.GTYPE_PET:
                iGiveIDList = self._GetGivePets()
            
            self.m_oClientSendCB(iGiveIDList)
        

    
    def OnGive(self):
        
        try:
            if self.m_CashEdit:
                iCash = int(self.m_CashEdit.GetText())
            else:
                iCash = 0
        except ValueError:
            iCash = 0

        if iCash < 0:
            return None
        
        if self.m_bClientOpen:
            self.ClickOpenSend()
        elif self.GetItems(iCash):
            return None
        elif self.GetPets(iCash):
            return None
        else:
            self.GetCash(iCash)

    
    def GetItems(self, cash):
        import netnpc
        items = self._GetGiveItems()
        if (self.m_GiveType == 3 or self.m_GiveType == 10) and g_NpcID == 0:
            netnpc.C2SNpcGiveExt(0, cash, items)
            if self.m_CashEdit:
                self.m_CashEdit.Active(False)
            
            self.SetShow(False)
            return True
        
        if len(items) > 0:
            if self.m_GiveCall is not None and callable(self.m_GiveCall):
                self.m_GiveCall(g_NpcID, cash, items)
                self.m_GiveCall = None
            else:
                netnpc.C2SNpcGive(netnpc.GIVETYPE_ITEM, g_NpcID, cash, items)
            if self.m_CashEdit:
                self.m_CashEdit.Active(False)
            
            self.SetShow(False)
            return True
        
        return False

    
    def GetPets(self, cash):
        import misc
        
        def Ok(dlg):
            obj = dlg.m_ShadowObj.Get()
            if obj:
                obj.HandInPet(dlg.m_Cash)
            

        if self.CheckPetGrade0() and not misc.IsNationFightServer():
            import commondialog
            dlg = commondialog.ShowMessageBox('\xb7\xed\xabe\xa4W\xa5\xe6\xaa\xba\xa5l\xb3\xea\xc3~\xac\xb00\xaf\xc5\xaa\xba\xa5l\xb3\xea\xc3~\xc4_\xc4_\xa1A\xacO\xa7_\xc4~\xc4\xf2\xa1H', ('\xc4~\xc4\xf2', '\xa8\xfa\xae\xf8'), (Ok, None))
            dlg.m_ShadowObj = interface.CShadowObject(self)
            dlg.m_Cash = cash
            return True
        else:
            return self.HandInPet(cash)

    
    def CheckPetGrade0(self):
        import pet
        for box in self.m_GiveItems:
            if box.m_ItemType == 2:
                petobj = pet.GetPet(box.m_ID)
                if petobj is not None and petobj.m_Prop.m_Grade == 0:
                    return True
                
            petobj.m_Prop.m_Grade == 0
        
        return False

    
    def HandInPet(self, cash):
        import netnpc
        pets = self._GetGivePets()
        if len(pets) > 0:
            if self.m_GiveType == 4:
                if callable(self.m_GiveCall):
                    self.m_GiveCall(pets)
                
            else:
                netnpc.C2SNpcGive(netnpc.GIVETYPE_PET, g_NpcID, cash, pets)
            self.m_GiveCall = None
            if self.m_CashEdit:
                self.m_CashEdit.Active(False)
            
            self.SetShow(False)
            return True
        
        return False

    
    def GetCash(self, cash):
        import netnpc
        if cash < 1:
            usermacro.PROMPT_MSG('\xb1z\xa8S\xa6\xb3\xb5\xb9\xa4\xa9\xa5\xf4\xa6\xf3\xaa\xab\xab~\xa9\xce\xaa\xf7\xbf\xfa')
            return None
        
        netnpc.C2SNpcGive(netnpc.GIVETYPE_ITEM, g_NpcID, cash, [])
        if self.m_CashEdit:
            self.m_CashEdit.Active(False)
        
        self.SetShow(False)

    
    def OnSelectGoods(self):
        for pos, iif in self.m_InterfaceItems.iteritems():
            iif.SetShow(False)
        
        self.GetObject('btn_item').SetSelect(True)
        self.GetObject('btn_pet').SetSelect(False)
        self.GetObject('btn_xingnang').SetShow(True)
        self.GetObject('btn_bag').SetShow(True)
        self.GetObject('btn_xingnang').SetSelect(True)

    
    def OnSelectPet(self):
        for pos, iif in self.m_InterfaceItems.iteritems():
            iif.SetShow(False)
        
        self.GetObject('btn_item').SetSelect(False)
        self.GetObject('btn_pet').SetSelect(True)
        self.GetObject('btn_xingnang').SetShow(False)
        self.GetObject('btn_bag').SetShow(False)
        self.GetObject('itembox2').SetShow(False)

    
    def CloseWindow(self):
        CloseWindow()

    
    def OnCloseWindow(self):
        self.m_GiveCall = None
        if self.m_CashEdit:
            self.m_CashEdit.Active(False)
        
        import hero
        hero.ReleaseDlgItem('Dlggive', (('m_Cash',),))
        self.SetShow(False)

    
    def IsSingleGiveItem(self, itemShape):
        
        def IsMiJi(shape):
            if shape <= shape:
                pass
            elif not shape < 27971:
                pass
            return None if shape <= shape else shape < 43071

        
        def IsQimeng(shape):
            if shape <= shape:
                pass
            elif not shape < 28936:
                pass
            return None if shape <= shape else shape < 44036

        import itemdata
        if itemdata.IsType(itemShape, 'equip') and itemdata.IsType(itemShape, 'gem') and itemdata.IsType(itemShape, 'drug') and itemShape in (25405, 25425, 21413) and IsMiJi(itemShape) and IsQimeng(itemShape) or itemdata.IsType(itemShape, 'level2drug'):
            return True
        

    
    def IsTaskEnableAutoGive(self):
        if self.m_TaskID in (12820,):
            return False
        else:
            return True

    
    def CheckItemEnough(self):
        if self.m_TaskID not in (14257, 14258, 14259):
            return True
        
        import task
        dList = task.G)8NecessaryItems(self.m_TaskID)
        for oItem in self.m_GiveItems:
            iShape = oItem.GetShape()
            if iShape in dList:
                dList[iShape] = None
                continue
        
        for iShape, lItem in dList.iteritems():
            if lItem is not None:
                return False
                continue
        
        return True

    
    def DoubleClickItem(self, pos):
        import netnpc
        iit = self.m_InterfaceItems[pos]
        items = []
        if not iit.IsSubmitItem(self.m_TaskID) or not g_NpcID:
            return None
        
        itemID = iit.m_Item.m_ID
        itemShape = iit.m_Item.m_Shape
        if not self.CheckItemEnough() or not self.IsTaskEnableAutoGive():
            return None
        else:
            itemIDLst = { }
            for oItem in self.m_GiveItems:
                if len(items) >= 5:
                    break
                
                iId = oItem.GetID()
                if iId in itemIDLst:
                    continue
                
                itemIDLst[iId] = True
                iNum = item.GetItem(itemID).GetQuantity()
                if iId != 0:
                    items.append([
                        iId,
                        iNum])
                    continue
            
            itemQuantity = None if self.IsSingleGiveItem(itemShape) else iit.m_Item.m_Quantity
            if self.IsSingleGiveItem(itemShape):
                pass
            else:
                itemsLst = []
                itemKey = getattr(iit.m_Item, 'm_Key', 0)
                if len(items) < 5:
                    for it in item.g_Items[item.ITEM_NORMAL].values():
                        if len(itemsLst) == 5:
                            break
                        
                        if it.m_ID == itemID:
                            continue
                        
                        if it.m_ID in itemIDLst:
                            continue
                        
                        itemIDLst[it.m_ID] = True
                        if hasattr(it, 'm_Shape') and it.m_Shape == itemShape:
                            sKey = getattr(it, 'm_Key', 0)
                            itemsLst.append([
                                it.m_ID,
                                it.m_Quantity,
                                sKey])
                            continue
                    
                    itemsLst[1:].sort(key = (lambda x: x[2]))
                    for i in itemsLst:
                        if len(items) >= 5:
                            break
                        
                        items.append(i[:2])
                    
                
            netnpc.C2SNpcGive(netnpc.GIVETYPE_ITEM, g_NpcID, 0, items)
            if self.m_CashEdit:
                self.m_CashEdit.Active(False)
            
            self.SetShow(False)

    
    def Undercarriage(self, msgid):
        box = self.m_GiveItems[msgid - interface.RIGHT_BUTTON_MESSAGE - 50]
        if box.m_ItemType == 1:
            box.AddItemQuantity(-1)
        elif box.m_ItemType == 2:
            box.PopPet()
        else:
            return None
        for i in xrange(len(self.m_GiveItems)):
            self.m_GiveItems[i].SetCheck(False)
        
        if box.m_ItemType in (1, 2):
            box.SetCheck(True)
        

    
    def GroundingItem(self, msgid):
        t = C_sys.GetTime()
        if msgid >= interface.RIGHT_BUTTON_MESSAGE:
            pos = msgid - interface.RIGHT_BUTTON_MESSAGE - 100
            bAll = True
        else:
            pos = msgid - 100
            bAll = False
            if self.m_InterfaceItems[pos].IsSubmitItem(self.m_TaskID) and hasattr(self, 'm_LeftUpTime') and t - self.m_LeftUpTime < 2500:
                self.DoubleClickItem(pos)
            
        self.OnGiveItem(pos, bAll)
        self.m_LeftUpTime = t
        if self.m_TaskID in (14257, 14258, 14259):
            self.UpdateBag(self.m_TaskID)
        

    
    def GroundingPet(self, msgid):
        petlist = self.GetObject('petlist')
        if msgid - 501 >= len(petlist.m_Items):
            return None
        
        idx = msgid - 501
        t = C_sys.GetTime()
        petbox = petlist.m_Items[idx]
        if hasattr(petbox, 'm_TipsBox') and hasattr(self, 'm_LeftUpTime') and t - self.m_LeftUpTime < 5000:
            self.DoubleClickPetList(idx)
        else:
            self.ClickPetList(idx)
        self.m_LeftUpTime = t

    
    def CheckPetInfo(self, msgid):
        petlist = self.GetObject('petlist')
        idx = msgid - 501 - interface.RIGHT_BUTTON_MESSAGE
        if idx >= len(petlist.m_Items):
            return None
        
        petbox = petlist.m_Items[idx]
        petid = petbox.m_ID
        import pet
        import dlggetinfo
        import hero
        petobj = pet.GetPet(petid)
        if petobj is not None:
            dlggetinfo.ShowSummonInfo(self, 20, -20, hero.g_ID, petid, petobj.m_Prop.m_Shape, petobj.m_Prop.m_Name)
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.OnCloseWindow()
        elif msgid == 3:
            self.OnGive()
        elif msgid == 4:
            self.OnSelectGoods()
        elif msgid == 5:
            self.OnSelectPet()
        elif msgid <= msgid:
            pass
        elif msgid < 55:
            box = self.m_GiveItems[msgid - 50]
            if self.m_bClientOpen:
                self.RemoveClientOpenItemList(box.GetID())
            
            if box.m_ItemType == 1:
                box.PopItem()
            elif box.m_ItemType == 2:
                box.PopPet()
            
        elif msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid - interface.RIGHT_BUTTON_MESSAGE < 55:
            self.Undercarriage(msgid)
        elif msgid <= msgid:
            pass
        elif not msgid <= 300:
            if msgid - interface.RIGHT_BUTTON_MESSAGE <= msgid - interface.RIGHT_BUTTON_MESSAGE:
                pass
            elif msgid - interface.RIGHT_BUTTON_MESSAGE <= 300:
                self.GroundingItem(msgid)
            elif msgid <= msgid:
                pass
            elif msgid < interface.RIGHT_BUTTON_MESSAGE:
                self.GroundingPet(msgid)
            elif msgid >= interface.RIGHT_BUTTON_MESSAGE + 501:
                self.CheckPetInfo(msgid)
            



class CGreatMansGive(CGive):
    sUIName = 'dialog/activity/greatmans_give.dlg'
    m_oNoNameGiveCB = None
    
    def SetNoNameGiveCB(self, oNoNameGiveCB):
        if oNoNameGiveCB and not isinstance(oNoNameGiveCB, misc.Functor):
            oNoNameGiveCB = misc.Functor(oNoNameGiveCB)
        
        self.m_oNoNameGiveCB = oNoNameGiveCB

    
    def CreateNpcName(self, npcid, npcname):
        pass

    
    def CreateInputEdit(self):
        pass

    
    def CreateCashTxt(self):
        pass

    
    def CreateNpcRelationTxt(self, npcid):
        pass

    
    def GroundingItem(self, msgid):
        if msgid >= interface.RIGHT_BUTTON_MESSAGE:
            iPos = msgid - interface.RIGHT_BUTTON_MESSAGE - 100
            bAll = True
        else:
            iPos = msgid - 100
            bAll = False
        if iPos not in self.m_InterfaceItems:
            return None
        
        oIIF = self.m_InterfaceItems[iPos]
        oItem = oIIF.GetItem()
        if oItem is None:
            return None
        
        if self.m_iGiveItemID:
            if self.m_iGiveItemID[0] != oItem.GetID():
                usermacro.PROMPT_MSG('\xa4@\xa6\xb8\xa5u\xaf\xe0\xb4\xa3\xa5\xe6\xa4@\xa5\xf3\xb8\xcb\xb3\xc6')
            
            return None
        
        self.OnGiveItem(iPos, bAll)

    
    def GroundingPet(self, msgid):
        petlist = self.GetObject('petlist')
        if msgid - 501 >= len(petlist.m_Items):
            return None
        
        iPetIdx = msgid - 501
        if self.GetObject('petlist').m_Items[iPetIdx].m_Give:
            return None
        
        if self._GetGivePets():
            usermacro.PROMPT_MSG('\xa4@\xa6\xb8\xa5u\xaf\xe0\xb5\xb9\xa4\xa9\xa4@\xb0\xa6\xa5l\xb3\xea\xc3~')
            return None
        
        self.ClickPetList(iPetIdx)

    
    def ClickPetList(self, idx):
        petlist = self.GetObject('petlist')
        petbox = petlist.m_Items[idx]
        if petbox.m_Give == True:
            return None
        
        self.AddPet(petbox)

    
    def ValidItem(self, sType):
        for iit in self.m_InterfaceItems.values():
            it = iit.GetItem()
            bIsTargetShape = None if (it or self.GetValidFlag(it.m_Shape, sType)) and it.IsIdentify() else False
            if it:
                pass
            iit.Enable(bIsTargetShape)
            if it:
                pass
            iit.ShowShadow(not bIsTargetShape)
        

    
    def Undercarriage(self, msgid):
        box = self.m_GiveItems[msgid - interface.RIGHT_BUTTON_MESSAGE - 50]
        if self.m_bClientOpen:
            self.RemoveClientOpenItemList(box.GetID())
        
        if box.m_ItemType == 1:
            box.PopItem()
        elif box.m_ItemType == 2:
            box.PopPet()
        else:
            return None
        for i in xrange(len(self.m_GiveItems)):
            self.m_GiveItems[i].SetCheck(False)
        
        if box.m_ItemType in (1, 2):
            box.SetCheck(True)
        

    
    def OnMessage(self, msgid):
        if msgid == 2:
            if self.m_oNoNameGiveCB:
                if self.m_GiveType == CGive.GTYPE_PET:
                    iGiveIDList = self._GetGivePets()
                else:
                    iGiveIDList = self.m_iGiveItemID
                self.m_oNoNameGiveCB(iGiveIDList)
            
        else:
            CGive.OnMessage(self, msgid)



def Show(npcid, npcname = '', gtype = 0, taskid = 0, shapeList = None):
    global g_NpcID, g_Give
    if shapeList is None:
        shapeList = []
    
    g_NpcID = npcid
    import world
    pobj = world.GetObj(npcid)
    name = npcname
    if pobj and hasattr(pobj, 'm_PropName'):
        name = pobj.m_PropName
    
    if len(name) <= 0:
        LOG('Give Fail----->', npcid, pobj)
        return None
    
    title = ''
    if hasattr(pobj, 'm_PropTitle'):
        title = pobj.m_PropTitle
    
    import friend
    import player
    import misc
    if misc.IsInKuafuServer() and pobj and player.IsPlayer(pobj):
        npcid /= 10
    
    if pobj and player.IsPlayer(pobj) and not friend.IsFriend(npcid):
        sMsg = dialoguecommondata.GetDialogue('newgive', 1050)
        usermacro.MOVE_MSG(-1, 0, sMsg)
        usermacro.NORMAL_MSG(sMsg)
    
    isnpc = False
    if pobj:
        import npc
        isnpc = isinstance(pobj, npc.CNpc)
    
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(name, isnpc, taskid, npcid, title)
    g_Give.SetGiveType(gtype)
    g_Give.Refresh(taskid)
    g_Give.OnShiMenSwitchPage(taskid)
    if len(shapeList):
        g_Give.ShowShadow(shapeList)
    


def ShowClientGiveDlg(sNpcName = '', iType = 0, iTaskId = 0, iShapeList = None, oClientSendCB = None, bIsCloseCashEdit = False, oGiveCls = None):
    global g_Give
    if iShapeList is None:
        iShapeList = []
    
    sName = sNpcName
    if len(sName) <= 0:
        LOG('Give Fail----->', sName)
        return None
    
    isnpc = False
    ReleaseGiveInterfaceCallback()
    if not oGiveCls:
        oGiveCls = CGive
    
    g_Give = oGiveCls(sName, isnpc, iTaskId, bClientOpen = True, oClientSendCB = oClientSendCB, bCloseCashEdit = bIsCloseCashEdit)
    g_Give.SetGiveType(iType)
    g_Give.Refresh(iTaskId)
    g_Give.OnShiMenSwitchPage(iTaskId)
    g_Give.ShowClientOpenItem(iShapeList)


def AddShadowByID(itemIDLst):
    if g_Give and len(itemIDLst):
        g_Give.AddShadowByID(itemIDLst)
    


def NameGive(name):
    global g_NpcID, g_Give
    g_NpcID = 0
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(name)
    g_Give.Refresh()
    g_Give.SetGiveType(3)


def WeaponGive(name):
    global g_NpcID, g_Give
    g_NpcID = 0
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(name)
    g_Give.Refresh()
    g_Give.SetGiveType(10)


def TeamGive(userid, username):
    global g_NpcID, g_Give
    g_NpcID = userid
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(username, npcid = userid)
    g_Give.Refresh()
    g_Give.SetGiveType(0)


def CopyChildObject(oParent, sChild, dUpdateUIInfo):
    (UI_INFO, sOpenName) = combdialog.GetUIInfo(oParent.GetDlgPath())
    if not UI_INFO:
        LOG('py ui \xb2\xa7\xb1`')
    
    dAllUIInfoList = combdialog.TransformUI(sOpenName, UI_INFO)
    dUIInfo = None
    for dValue in dAllUIInfoList:
        if dValue.get('sName', None) == sChild:
            dUIInfo = misc.DeepCopy(dValue)
            break
            continue
    
    if not dUIInfo:
        return None
    
    dUIInfo.update(dUpdateUIInfo)
    sClassName = dUIInfo['sWidgetType']
    oCls = combdialog.GetClsObj(sClassName)
    oWidget = oCls(oParent, None, dUIInfo = dUIInfo)
    if hasattr(oWidget, 'SetUIRootNode'):
        oWidget.SetUIRootNode(oParent)
    
    if not hasattr(oParent, 'm_lstClonesDict'):
        oParent.m_lstClonesDict = { }
    
    oParent.m_lstClonesDict.setdefault(sChild, []).append(oWidget)
    return oWidget


def ShowPeopleElectionGiveDlg(iType, oClientSendCB, oNoNameClientSendCB):
    ShowClientGiveDlg(sNpcName = '\xb4\xa3\xa5\xe6\xaa\xab\xab~', iType = iType, oClientSendCB = oClientSendCB, bIsCloseCashEdit = True, oGiveCls = CGreatMansGive)
    g_Give.SetGiveType(iType)
    g_Give.SetNoNameGiveCB(oNoNameClientSendCB)
    g_Give.SetShowObject('btn_pet', False)
    g_Give.SetShowObject('btn_item', False)


def CallbackGive(name, callback):
    global g_Give
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(name, isnpc = True)
    g_Give.Refresh()
    g_Give.SetGiveType(4, callback)


def ShadowCallbackGive(sName, iTeamId, iShapeLst, funcCB):
    global g_NpcID, g_Give
    g_NpcID = iTeamId
    ReleaseGiveInterfaceCallback()
    g_Give = CGive(sName, npcid = iTeamId)
    g_Give.Refresh()
    g_Give.SetGiveType(0)
    g_Give.AddShadowByShape(iShapeLst, funcCB)


def RefreshLock(pid):
    if g_Give:
        g_Give.Refresh()
    


def CloseOtherUI():
    import dlgitem
    import dlgpetitem
    import dlgswap
    dlgitem.Show(False)
    dlgpetitem.CloseWindow()
    dlgswap.CloseWindow()
    import dlgflyflag
    dlgflyflag.CloseFlyDlg()


def CloseWindow():
    import dlgpizza
    dlgpizza.CloseTaskBag()
    if g_Give:
        g_Give.OnCloseWindow()
    


def ReleaseGiveInterfaceCallback():
    global g_Give
    if g_Give:
        g_Give.ReleaseInterfaceCallback()
        g_Give = None
