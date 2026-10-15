# pycdc 交叉复核产物 · script.fls entry 61
# co_filename(原始)='script/mxgame/xmxpintu/dlgxmxpintu.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_61.pyc (Python 2.5)

import interface
import combdialog
import dlgbeauty
import item
import usermacro
g_Dialog = None
g_DlgUploadInfo = None

def ModuleReset():
    global g_Dialog, g_DlgUploadInfo
    g_Dialog = None
    g_DlgUploadInfo = None


def Show(iPoint, iProgress, pintuList, doneList):
    global g_Dialog
    if not g_Dialog:
        g_Dialog = CPintuShenshouDlg()
    
    g_Dialog.RefreshData(iPoint, iProgress, pintuList, doneList)


def ShowUpload(iItemID, sName, sMobile, sGift, sAddress):
    global g_DlgUploadInfo
    g_DlgUploadInfo = CDlgUploadInfo(iItemID, sName, sMobile, sGift, sAddress)


def CloseUploadDialog():
    global g_DlgUploadInfo
    g_DlgUploadInfo = None


class CPintuShenshouDlg(combdialog.CCombDialog):
    POS = [
        (0, 0),
        (76, 0),
        (153, 0),
        (231, 0),
        (287, 0),
        (364, 0),
        (441, 0),
        (0, 55),
        (56, 76),
        (153, 55),
        (231, 76),
        (306, 55),
        (364, 76),
        (441, 55),
        (0, 152),
        (76, 131),
        (134, 152),
        (231, 131),
        (306, 152),
        (384, 131),
        (441, 152),
        (0, 207),
        (56, 228),
        (153, 207),
        (231, 228),
        (306, 207),
        (364, 228),
        (441, 207)]
    NEEDLIST = [
        7,
        14,
        21,
        28]
    MIN_LIGHT = 1
    MAX_LIGHT = 8
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/pintushenshou.dlg')
        interface.Center(self)
        self.CreateCardArea()
        self.CreateText()
        self.CreateReward()
        self.HideCtrl()
        self.m_Points = 0

    
    def CreateCardArea(self):
        import clickimage
        self.m_Pintu = []
        (bx, by, _, _) = self.GetLocData('img_bg')
        for i in range(28):
            (x, y) = self.POS[i]
            filename = 'combdialog3/\xd4\xd3\xcd\xbc/2018\xd0\xc2\xc3\xce\xcf\xeb\xd4\xcb\xd3\xaa\xbb\xee\xb6\xaf/%d.png' % (i + 1)
            oPintu = clickimage.CClickImage1(self, filename, 20 + i, bx + x, by + y)
            oPintu.SetLight(self.MIN_LIGHT)
            self.m_Pintu.append(oPintu)
        

    
    def CreateText(self):
        import misc
        if misc.IsTWServer():
            textList = [
                ('text_rule', 2)]
        else:
            textList = [
                ('text_rule', 2),
                ('text_detail', 3)]
        self.m_ClickTextList = []
        for sObjectName, iMsgID in textList:
            obj = self.GetObject(sObjectName)
            obj.SetShow(False)
            color = obj.GetColor()
            font = obj.GetFont()
            sText = obj.GetText()
            (x, y) = obj.GetPos()
            (w, h) = obj.GetSize()
            oText = interface.CClickRichText(self, x, y, w, '#u%s#n' % sText, color, color, font, msgid = iMsgID)
            self.m_ClickTextList.append(oText)
        

    
    def CreateReward(self):
        self.m_RewardList = []
        rewardInfo = (('img_done1', 'reward1', 70239, 10, 4, ''), ('img_done2', 'reward2', 30210, 2, 5, ''), ('img_done3', 'reward3', 72565, 1, 6, ''), ('img_done4', 'reward4', 72816, 1, 7, '\xb3\xd1\xbel\xa6\xb8\xbc\xc6\xa1G5'))
        for sDoneObjname, sObjname, iShape, iNum, iMsgid, sExt in rewardInfo:
            reward = item.CInterfaceFakeItem(self, 0, 0, iMsgid, interfaceitems = None)
            itemobj = item.CItem(-1, iShape, 0, iNum, 0, 0)
            itemobj.m_InfoExt = sExt
            reward.SetItem(itemobj)
            obj = self.GetObject(sObjname)
            doneobj = self.GetObject(sDoneObjname)
            doneobj.SetShow(False)
            z = doneobj.GetZ()
            reward.SetZ(z - 1)
            (ox, oy) = obj.GetPos()
            reward.SetPos(ox, oy)
            self.m_RewardList.append(reward)
        

    
    def HideCtrl(self):
        import misc
        if misc.IsTWServer():
            objNameLst = [
                'noname8',
                'text_detail',
                'text_progress']
            for sObjName in objNameLst:
                self.GetObject(sObjName).SetShow(False)
            
        

    
    def CreateRollAni(self, oParent, bFlash):
        if bFlash:
            oRollAni = interface.CSpriteObject(oParent, 'item44/select.spr', 'item')
            oRollAni.(1, 'animation')
            oRollAni.SetPos(21, 20)
        else:
            oRollAni = None
        oParent.m_RollAni = oRollAni

    
    def RefreshData(self, iPoint, iProgress, pintuList, doneList):
        self.m_Points = iPoint
        self.GetObject('text_chip').SetText(str(iPoint))
        self.GetObject('text_progress').SetText('%d/1000' % iProgress)
        self.m_HaveList = pintuList
        iHave = len(pintuList)
        for idx in pintuList:
            self.m_Pintu[idx].SetLight(self.MAX_LIGHT)
        
        self.m_DoneList = doneList
        for idx, iDone in enumerate(doneList):
            bDone = iDone > 0
            self.GetObject('img_done%d' % (idx + 1)).SetShow(bDone)
            if not bDone:
                pass
            bFlash = iHave >= self.NEEDLIST[idx]
            self.CreateRollAni(self.m_RewardList[idx], bFlash)
        

    
    def GetReward(self, idx):
        iDone = self.m_DoneList[idx]
        if iDone > 0:
            usermacro.PROMPT_MSG('\xa7A\xa4w\xbb\xe2\xa8\xfa\xb8\xd3\xbc\xfa\xc0y')
            return None
        
        iNeed = self.NEEDLIST[idx]
        iHave = len(self.m_HaveList)
        if iHave < iNeed:
            usermacro.PROMPT_MSG('\xbb\xdd\xc2I\xabG\xa6\xdc\xa4\xd6%d\xb1i\xab\xf7\xb9\xcf\xb8H\xa4\xf9\xa4~\xa5i\xbb\xe2\xa8\xfa' % iNeed)
            return None
        
        import netxmxpintu
        netxmxpintu.C2SGetReward(idx)

    
    def LightenPintu(self, idx):
        if len(self.m_HaveList) == 28:
            usermacro.PROMPT_MSG('\xb1z\xa4w\xb8g\xc2I\xabG\xa9\xd2\xa6\xb3\xab\xf7\xb9\xcf')
            return None
        
        if not self.m_Points:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xab\xf7\xb9\xcf\xb8H\xa4\xf9\xa4\xa3\xb0\xf7')
            return None
        
        if idx in self.m_HaveList:
            usermacro.PROMPT_MSG('\xb3o\xad\xd3\xa6\xec\xb8m\xa4w\xb8g\xc2I\xabG\xa4F')
            return None
        
        self.PingTuFadeIn(idx)
        self.m_HaveList.append(idx)
        self.m_Points -= 1
        self.GetObject('text_chip').SetText(str(self.m_Points))

    
    def PingTuFadeIn(self, idx):
        self.m_Pintu[idx].SetLight(self.MIN_LIGHT)
        
        def fadein(obj, light):
            if light > self.MAX_LIGHT:
                import netxmxpintu
                netxmxpintu.C2SShowPingTu(idx)
                return None
            
            obj.m_Pintu[idx].SetLight(light)
            light += 1
            return (light,)

        self.m_FadeInTimer = self.CreatePyCommand(3, fadein, 1)

    
    def ReleaseTimer(self):
        if hasattr(self, 'm_FadeInTimer'):
            self.m_FadeInTimer.Release()
            self.m_FadeInTimer = None
        

    
    def CloseWindow(self):
        global g_Dialog
        self.ReleaseTimer()
        if g_Dialog:
            g_Dialog = None
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            import netxmxpintu
            netxmxpintu.C2SLookRule()
        elif msgid == 3:
            import netxmxpintu
            netxmxpintu.C2SLookDetail()
        elif msgid <= msgid:
            pass
        elif msgid <= 7:
            self.GetReward(msgid - 4)
        elif msgid <= msgid:
            pass
        elif msgid <= 47:
            self.LightenPintu(msgid - 20)
        



class CDlgUploadInfo(dlgbeauty.CDlgUploadInfo):
    SPECIAL_SHAPE = (72907, 72908)
    SPECIAL_EXT = ('S\xbdX', 'M\xbdX', 'L\xbdX', 'XL\xbdX', 'XXL\xbdX', 'XXXL\xbdX')
    
    def __init__(self, iItemID, sName, sMobile, sGift, sAddress):
        import itemdata
        self.m_iItemID = iItemID
        self.m_sName = sName
        self.m_sMobile = sMobile
        self.m_sGift = sGift
        self.m_sAddress = sAddress
        self.m_iGiftShape = item.GetItemShapeByID(iItemID)
        self.m_sGiftName = itemdata.GetData(self.m_iGiftShape)[0]
        dlgbeauty.CDlgUploadInfo.__init__(self)

    
    def CreateEdits(self):
        import combmacro
        import ui
        import wrapinterface
        self.m_NameEdit = combmacro.CEDIT(interface.CEdit, 'edit_name', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_NameEdit.SetLimit(20)
        self.m_NameEdit.SetText(self.m_sName)
        self.m_PhoneEdit = combmacro.CEDIT(wrapinterface.CNumberEdit, 'edit_phone', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_PhoneEdit.SetLimit(11)
        self.m_PhoneEdit.SetText(self.m_sMobile)
        if self.m_iGiftShape in self.SPECIAL_SHAPE:
            self.m_GiftEdit = combmacro.CLISTBOX(interface.CListBox, 'edit_gift', self, interface.COLOR_5, interface.FontLT14_3)
            SPECIAL_SHAPE = self.m_GiftEdit.SetItemProp
            None(None, 16, 76)
            for sExt in self.SPECIAL_EXT:
                self.m_GiftEdit.AddTextItem('%s(%s)' % (self.m_sGiftName, sExt))
            
            self.m_GiftEdit.SetReadOnly(True)
            if self.m_sGift:
                self.m_GiftEdit.SetText(self.m_sGift)
            else:
                self.m_GiftEdit.SetText('\xbd\xd0\xbf\xef\xbe\xdc\xbdX\xbc\xc6')
        else:
            (x, y, w, h) = self.GetLocData('edit_gift')
            self.m_GiftEdit = ui.CTextObjext(self, w, h, self.m_sGiftName, interface.FontLT14_3, interface.COLOR_5, iAlign = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE)
            self.m_GiftEdit.SetPos(x, y)
        self.m_AddrEdit = combmacro.CEDIT(interface.CEdit, 'edit_addr', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_AddrEdit.SetLimit(60)
        self.m_AddrEdit.SetText(self.m_sAddress)

    
    def CloseWindow(self):
        global g_DlgUploadInfo
        g_DlgUploadInfo = None

    
    def UploadInfo(self):
        name = self.m_NameEdit.GetText()
        phone = self.m_PhoneEdit.GetText()
        gift = self.m_GiftEdit.GetText()
        addr = self.m_AddrEdit.GetText()
        if not name and phone and gift and addr:
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa7\xb9\xbe\xe3\xabH\xae\xa7')
            return None
        
        if gift == '\xbd\xd0\xbf\xef\xbe\xdc\xbdX\xbc\xc6':
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa6\xe7\xaaA\xbdX\xbc\xc6')
            return None
        
        import netxmxpintu
        netxmxpintu.C2SSubmitInfo(self.m_iItemID, name, phone, gift, addr)
