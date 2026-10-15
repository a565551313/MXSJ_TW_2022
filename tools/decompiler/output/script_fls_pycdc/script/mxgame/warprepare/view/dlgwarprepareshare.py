# pycdc 交叉复核产物 · script.fls entry 1974
# co_filename(原始)='script/mxgame/warprepare/view/dlgwarprepareshare.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1974.pyc (Python 2.5)

import dlggetinfo
import interface
import combdialog
import item
import itemdefine
import iteminterface
import tipsclosemgr
import walker
import wrapinterface
g_bShowInfo = False
g_oInfoDialog = None

def ModuleReset():
    global g_bShowInfo, g_oInfoDialog
    g_bShowInfo = False
    g_oInfoDialog = None


def Show(iShape, dDesc, dAttr, lstEquips):
    global g_oInfoDialog, g_bShowInfo
    if g_bShowInfo:
        if not g_oInfoDialog:
            g_oInfoDialog = CWarPrepareShareDialog()
        
        g_oInfoDialog.SetData(iShape, dDesc, dAttr, lstEquips)
        g_bShowInfo = False
    


def ShowGmEquipInfo(iPlayerId, iShape, dDesc, dAttr, lstEquips, dPets):
    global g_oInfoDialog
    if not g_oInfoDialog:
        g_oInfoDialog = CWarPrepareShareDialog()
    
    g_oInfoDialog.SetData(iShape, dDesc, dAttr, lstEquips)
    g_oInfoDialog.CreateGmPetList(dPets)
    g_oInfoDialog.SetPlayerId(iPlayerId)


def SetForceShowInfo(bShow):
    global g_bShowInfo
    g_bShowInfo = bShow


class CWarPrepareShareDialog(combdialog.CCombDialog):
    EQUIP_LOC = {
        itemdefine.EQUIPPOS_CAP: ('loc_cap', '\xb4U\xa4l'),
        itemdefine.EQUIPPOS_WEAPON: ('loc_weapon', '\xaaZ\xbe\xb9'),
        itemdefine.EQUIPPOS_CLOTH: ('loc_cloth', '\xf1Z\xa5\xd2'),
        itemdefine.EQUIPPOS_SASH: ('loc_sash', '\xb8y\xb1a'),
        itemdefine.EQUIPPOS_CUFF: ('loc_cuff', '\xc5@\xb5\xc3'),
        itemdefine.EQUIPPOS_MAGIC: ('loc_special', '\xaak\xc4_'),
        itemdefine.EQUIPPOS_NECKLACE: ('loc_necklace', '\xb6\xb5\xc3\xec'),
        itemdefine.EQUIPPOS_RING: ('loc_ring', '\xa7\xd9\xab\xfc'),
        itemdefine.EQUIPPOS_SHOSE: ('loc_shoe', '\xbec\xa4l'),
        itemdefine.EQUIPPOS_SECONDWEAPON: ('loc_viceweapon', '\xb0\xc6\xaaZ\xbe\xb9') }
    EQUIP_FUMO_TEXT = {
        itemdefine.EQUIPPOS_WEAPON: 'text_fumo_weapon',
        itemdefine.EQUIPPOS_NECKLACE: 'text_fumo_necklace',
        itemdefine.EQUIPPOS_CAP: 'text_fumo_cap',
        itemdefine.EQUIPPOS_CUFF: 'text_fumo_cuff',
        itemdefine.EQUIPPOS_CLOTH: 'text_fumo_cloth',
        itemdefine.EQUIPPOS_SASH: 'text_fumo_sash',
        itemdefine.EQUIPPOS_SHOSE: 'text_fumo_shoe' }
    ATTRDICT = {
        'text_xian': ('Res10',),
        'text_gui': ('Res11',),
        'text_yao': ('Res12',),
        'text_zhi': ('Res13',),
        'text_nian': ('Res14',),
        'text_hp': ('HPMax', 'HPMax'),
        'text_mp': ('MPMax', 'MPMax'),
        'text_fp': ('FPMax', 'FPMax'),
        'text_att': ('Att',),
        'text_def': ('Def',),
        'text_spe': ('Spe',),
        'text_magdef': ('Magdef',) }
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/warprepare/prepare_share.dlg')
        interface.Center(self)
        self.m_oPlayerAni = None
        self.m_iPlayerId = 0
        self.m_dEquips = { }

    
    def SetData(self, iShape, dDesc, dAttr, lstEquips):
        dFumoMap = {
            '\xa7\xf0\xc0\xbb': '\xa7\xf0',
            '\xae\xf0\xa6\xe5': '\xa6\xe5',
            '\xa4O\xb9D': '\xa4O',
            '\xc6F\xa4O': '\xc6F',
            '\xa8\xbe\xbfm': '\xa8\xbe',
            '\xb3t\xab\xd7': '\xb3t',
            '\xaak\xa4O': '\xaak' }
        self.CreatePlayerAni(iShape, dDesc)
        for sTxtName, tAttrName in self.ATTRDICT.iteritems():
            oTxt = self.GetObject(sTxtName)
            lstAttrValue = []
            for sAttrName in tAttrName:
                lstAttrValue.append(str(dAttr[sAttrName]))
            
            oTxt.SetText('/'.join(lstAttrValue))
        
        for sUIName in self.EQUIP_FUMO_TEXT.itervalues():
            self.SetShowObject(sUIName, False)
        
        for tEquip in lstEquips:
            dEquip = {
                'iShape': tEquip[0],
                'iKey': tEquip[1],
                'sExt': tEquip[2] }
            iPos = iteminterface.GetEquipPosByShape(dEquip['iShape'])
            (sLocName, sTips) = self.EQUIP_LOC[iPos]
            (iX, iY) = self.GetObject(sLocName).GetPos()
            iZ = self.GetObject(sLocName).GetZ()
            self.m_dEquips[iPos] = CShareEquipItem(self, sTips)
            self.m_dEquips[iPos].SetItemInfo(dEquip)
            self.m_dEquips[iPos].SetPos(iX, iY)
            self.m_dEquips[iPos].SetZ(iZ + 1)
            sFumo = dlggetinfo.GetItemAttrDescByType(dEquip['sExt'], '\xaa\xfe\xc5]')
            if sFumo:
                lstFumo = sFumo.split(' ')
                if len(lstFumo) > 2:
                    sAttr = lstFumo[0]
                    sValue = lstFumo[1]
                    oFumoTxt = self.GetObject(self.EQUIP_FUMO_TEXT[iPos])
                    oFumoTxt.SetText('%s%s' % (dFumoMap.get(sAttr, sAttr), sValue))
                    oFumoTxt.SetShow(\xf8rue)
                
            len(lstFumo) > 2
        

    
    def CreatePlayerAni(self, iShape, dDesc):
        if 'horse' in dDesc:
            del dDesc['horse']
        
        if 'track' in dDesc:
            del dDesc['track']
        
        if 'fairy' in dDesc:
            dDesc['fairy'] = [
                dDesc['fairy'][0],
                [
                    0,
                    0]]
        
        if 'aura' in dDesc:
            del dDesc['aura']
        
        (x, y, w, h) = self.GetLocData('ani_Player')
        desc = dDesc
        import oldwalkerprocess
        if self.m_oPlayerAni:
            self.m_oPlayerAni.Release()
            self.m_oPlayerAni = None
        
        iShape = oldwalkerprocess.SpecialShape(0, iShape, desc)
        self.m_oPlayerAni = walker.CFakeRole(self, -1, iShape, desc)
        self.m_oPlayerAni.SetPos(x + w / 2, y + h - 30)
        self.m_oPlayerAni.SetDirection(3)
        self.m_oPlayerAni.SetZ(1000)
        self.m_oPlayerAni.SetButtonMessage(None)
        self.m_oPlayerAni.SetMouseMessage(None)

    
    def CloseWindow(self):
        global g_oInfoDialog
        g_oInfoDialog = None

    
    def SetPlayerId(self, iPlayerId):
        self.m_iPlayerId = iPlayerId

    
    def CreateGmPetList(self, lstPetDict):
        import listwidget
        import dlgpcattr
        oTableView = listwidget.CCombList(self, 4, 157, 169, 100)
        for iPetId, sPetInfo in lstPetDict.items():
            oItem = oTableView.AddBoxItem(dlgpcattr.CPetListItem)
            oItem.SetText(sPetInfo[0], sPetInfo[1])
            oItem.SetPetInfo(iPetId, sPetInfo[2])
        
        oTableView.ResetItems()
        oTableView.ResetScrollBar()
        self.m_oBox = interface.CBoxObject(self, 158, 171, 16777215, 255)
        (iX, iY) = interface.GetAttachPos(self.m_oBox, self.GetObject('noname'), {
            'lSpace': (0, 0),
            'lTargetAnchor': (1, 0),
            'lAttachAnchor': (0, 0) })
        (iPX, iPY) = self.GetPos()
        iX -= iPX
        iY -= iPY
        iY += 10
        self.m_oBox.SetPos(iX, iY)
        self.m_oBox.SetZ(-1)
        oTableView.SetPos(iX, iY)
        self.m_oTableView = oTableView

    
    def ClickGmPetItem(self, iMsgId):
        import netornament
        (iPetId, iType) = self.m_oTableView.m_Items[iMsgId].GetPetInfo()
        netornament.C2SGmOpenSummon(self.m_iPlayerId, iPetId, iType)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        
        if iMsgID > 100 + interface.RIGHT_BUTTON_MESSAGE:
            iMsgID -= interface.RIGHT_BUTTON_MESSAGE
            self.ClickGmPetItem(iMsgID - 101)
        



class CShareEquipItem(interface.CClickBox):
    
    def __init__(self, oParent, sTxt):
        interface.CClickBox.__init__(self, oParent, 44, 44, alpha = 0)
        self.m_dItem = None
        self.m_oImage = None
        self.m_sTxt = sTxt

    
    def SetItemInfo(self, dItem):
        if not dItem:
            self.m_oImage = None
        else:
            self.m_oImage = item.CreateItem44Image(self, dItem['iShape'], dItem['iKey'])
        self.m_dItem = dItem

    
    def Enter(self):
        if not self.m_dItem:
            oTips = wrapinterface.CTextTips(self.GetParent(), -1, self.m_sTxt, interface.FontLT14_3, direct = 1)
            oTips.SetOwner(self)
        else:
            oTips = dlggetinfo.ShowFakeItem(self.m_dItem['iShape'], self.m_dItem['sExt'], self.m_dItem['iKey'])
            oTips.SetOwner(self)
        tipsclosemgr.Regist(oTips)

    
    def Leave(self):
        tipsclosemgr.CheckClose()
