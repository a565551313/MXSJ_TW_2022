# pycdc 交叉复核产物 · script.fls entry 4163
# co_filename(原始)='script/mxgame/pet/lianyao/color/dlgpetcolor.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4163.pyc (Python 2.5)

import interface
import wrapinterface
import combdialog
import slot
import misc
import dlglianyao
import dgtlianyao
import dgtpetcolor
import dlgpetbase
import pet

class CColorDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_SelectPet = 'SS_SelectPet(iPetID)'
    SS_UseItemChg = 'SS_UseItemChg(oItem)'
    SS_ChgColor = 'SS_ChgColor()'
    SS_ConfirmColor = 'SS_ConfirmColor(iPos)'
    SS_GiveUp = 'SS_GiveUp()'
    SS_ItemBuy = 'SS_ItemBuy()'
    SS_ChangeChildColor = 'SS_ChangeChildColor(idx, iChange)'
    SS_ConfirmChildColor = 'SS_ConfirmChildColor()'
    SS_ClickPetModel = 'SS_ClickPetModel()'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/newsummon/str_color.dlg')
        self.ssInit()
        self.m_DelegateList = []
        self.m_oPetAni = None
        self.m_oChildColorAni = None
        self.m_oPetList = None
        self.m_oItemBox = None
        self.m_oChildItemBox = None
        self.m_oPetColorAni1 = None
        self.m_oPetColorAni2 = None
        self.m_iAniDir = 0
        self.m_lPartTxtObj = []
        self.m_iCurAniIdx = 0
        self.m_lAniState = []
        self.InitDlg()
        self.InitDelegate()
        self.SetChildFrameShow(False)

    
    def InitDlg(self):
        self.GetObject('hloc_pet_ani').SetZ(5)
        self.GetObject('hloc_ani2').SetZ(5)
        self.GetObject('hloc_ani1').SetZ(5)
        self.GetObject('hloc_ChildAni').SetZ(5)

    
    def InitPetList(self, iSelectPetID, oIsValidFunc):
        self.m_oPetList = dlgpetbase.CPetList(self, misc.Functor(self.OnSelectPet), iSelectPetID, oIsValidFunc, oSortFunc = pet.GetSortFunc())
        (x, y, _, _) = self.GetLocData('loc_petlist')
        self.m_oPetList.SetPos(x, y)

    
    def RefreshPetList(self, iSelectPetID):
        if self.m_oPetList:
            pass
        self.m_oPetList.SetSelectPet(iSelectPetID)

    
    def CreateItemBox(self, oFilterFunc, iShape = None):
        self.m_oItemBox = dlglianyao.CItemBox(self, oFilterFunc, misc.Functor(self.OnItemChgCB))
        if iShape:
            self.m_oItemBox.SetItem(iShape)
        
        oImg = self.GetObject('img_item')
        (x, y) = oImg.GetPos()
        oImg.SetShow(False)
        self.m_oItemBox.SetPos(x, y)

    
    def CreateChildItemBox(self):
        import makeitemicon
        oMaterialImg = makeitemicon.CBackItem(self)
        oImg = self.GetObject('img_ChildItem')
        (x, y) = oImg.GetPos()
        oMaterialImg.SetPos(x, y)
        oMaterialImg.AddClickAddCB(self.OnClickChildItem)
        self.m_oChildItemBox = oMaterialImg

    
    def SetItemAccessShape(self, iShape):
        if self.m_oItemBox:
            pass
        self.m_oItemBox.SetItemAccessShape(iShape)

    
    def SetUseItem(self, iShape):
        if self.m_oItemBox:
            pass
        self.m_oItemBox.SetItem(iShape)

    
    def GetUseItem(self):
        if self.m_oItemBox:
            iShape = self.m_oItemBox.GetShape()
            if iShape:
                oItemList = dgtlianyao.GetItemsWithShape(iShape)
                if oItemList:
                    oItem = oItemList[0]
                else:
                    oItem = None
            else:
                oItem = None
        else:
            oItem = None
        return oItem

    
    def SetEmpty(self):
        self.SetPetName('')
        self.SetPetGrade(0)
        self.SetScore(0)
        self.ClearPetAni()
        self.ClearPetColorAni()
        self.SetOpsBtnEnable(False)

    
    def SetCompensate(self, iCompensate, iShape):
        import newoldcharchangemgr
        oText = self.GetObject('txt_Compensate')
        oTips = self.GetObject('tips_Compensate')
        if iCompensate != 0 and newoldcharchangemgr.IsUseNewResWithShapeAndChar(iShape):
            if oText:
                pass
            oText.ReplaceText({
                '$num': str(iCompensate) })
            if oText:
                pass
            oText.SetShow(True)
            if oTips:
                pass
            oTips.SetShow(True)
        elif oText:
            pass
        oText.SetShow(False)
        if oTips:
            pass
        oTips.SetShow(False)

    
    def SetPetName(self, sName):
        self.GetObject('txt_name').SetText(sName)

    
    def SetScore(self, iScore):
        self.GetObject('txt_score').SetText(str(iScore))

    
    def SetPetGrade(self, iGrade):
        self.GetObject('txt_lv').SetText(str(iGrade))

    
    def SetNeed(self, sNeed):
        self.GetObject('rtxt_need').ReplaceText({
            '$n': sNeed })

    
    def SetChildNeed(self, iShape, iItemNum, iNeedNum):
        self.m_oChildItemBox.DelItemIcon()
        if iNeedNum > iItemNum:
            self.m_oChildItemBox.CreateNeedAddItemBtn(iShape, 0, 0)
            self.m_oChildItemBox.CreateBackNeedItemIcon(iShape, iItemNum, iNeedNum, True)
        else:
            self.m_oChildItemBox.CreateBackNeedItemIcon(iShape, iItemNum, iNeedNum, False)
        self.GetObject('rtxt_ChildNeed').ReplaceText({
            '$n': str(iNeedNum) })

    
    def RefreshItemNeed(self, iHasCnt, iNeedCnt):
        if self.m_oItemBox:
            pass
        self.m_oItemBox.SetEnough(iHasCnt, iNeedCnt)

    
    def CreatePetAni(self, oPet):
        import wrapinterface
        import misc
        shape = oPet.GetProp('m_Shape')
        desc = oPet.GetProp('m_Desc')
        ikey = (oPet.m_BirthKey & 255) << 8 | oPet.m_Key & 255
        iLianyaoTime = oPet.GetProp('m_Lianyao')
        if iLianyaoTime == 0:
            iTimeKey = 0
        elif iLianyaoTime > misc.GetServerCurrentTime():
            iTimeKey = 1
        else:
            iTimeKey = 2
        if self.m_oPetAni:
            self.m_oPetAni.Release()
        
        self.m_oPetAni = wrapinterface.CPetAniWithUnlock(self, shape, desc, ikey, timekey = iTimeKey)
        self.m_oPetAni.SetColorCompensate(oPet.GetProp('m_bIsColorCompensate'), oPet.GetID())
        self.m_oPetAni.SetPetID(oPet.GetID())
        self.m_oPetAni.CreateOrnamentImg()
        (x, y) = self.GetObject('loc_pet_ani').GetPos()
        self.m_oPetAni.SetPos(x, y)
        self.m_oPetAni.ReleaseRandomAni()
        self.m_lAniState = self.m_oPetAni.GetStateList()
        self.SetPetColorAni(self.GetCurAniIdx())

    
    def ClearPetAni(self):
        if self.m_oPetAni:
            self.m_oPetAni.Release()
        
        self.m_oPetAni = None

    
    def CreatePetColorAni(self, iShape, dDesc1, dDesc2):
        (x1, y1, _, _) = self.GetLocData('loc_ani1')
        if self.m_oPetColorAni1:
            self.m_oPetColorAni1.Release()
        
        self.m_oPetColorAni1 = wrapinterface.CPetAni(self, iShape, dDesc1)
        self.m_oPetColorAni1.SetPos(x1, y1)
        self.m_oPetColorAni1.ReleaseRandomAni()
        (x2, y2, _, _) = self.GetLocData('loc_ani2')
        if self.m_oPetColorAni2:
            self.m_oPetColorAni2.Release()
        
        self.m_oPetColorAni2 = wrapinterface.CPetAni(self, iShape, dDesc2)
        self.m_oPetColorAni2.SetPos(x2, y2)
        self.m_oPetColorAni2.ReleaseRandomAni()
        self.SetOpsBtnEnable(True)

    
    def CreateChildColorAni(self, iShape, dDesc):
        (x, y, _, _) = self.GetLocData('loc_ChildAni')
        if self.m_oChildColorAni:
            self.m_oChildColorAni.Release()
        
        self.m_oChildColorAni = wrapinterface.CPetAni(self, iShape, dDesc)
        self.m_oChildColorAni.SetPos(x, y)
        self.m_oChildColorAni.ReleaseRandomAni()

    
    def SetPetColorAniDirection(self, iIdx):
        if self.m_oPetColorAni1:
            pass
        if not (self.m_oPetColorAni2) and not (self.m_oChildColorAni):
            return None
        
        self.m_iAniDir = (self.m_iAniDir + 8 * iIdx) % 32
        if self.m_oPetColorAni1:
            pass
        self.m_oPetColorAni1.SetDir(self.m_iAniDir)
        if self.m_oPetColorAni2:
            pass
        self.m_oPetColorAni2.SetDir(self.m_iAniDir)
        if self.m_oPetAni:
            pass
        self.m_oPetAni.SetDir(self.m_iAniDir)
        if self.m_oChildColorAni:
            pass
        self.m_oChildColorAni.SetDir(self.m_iAniDir)

    
    def OnClickPetModel(self):
        self.ssEmit(self.SS_ClickPetModel)

    
    def GetCurAniIdx(self):
        return self.m_iCurAniIdx

    
    def SetPetColorAni(self, iIdx):
        self.m_iCurAniIdx = iIdx
        if not (self.m_oPetAni) or not (self.m_lAniState):
            return None
        
        lStat = self.m_lAniState
        iLen = len(lStat)
        iIdx = None if iIdx < len(lStat) else iLen - 1
        self.m_oPetAni.SetState(lStat[iIdx])
        if self.m_oPetColorAni1:
            pass
        self.m_oPetColorAni1.SetState(lStat[iIdx])
        if self.m_oPetColorAni2:
            pass
        self.m_oPetColorAni2.SetState(lStat[iIdx])
        if self.m_oChildColorAni:
            pass
        self.m_oChildColorAni.SetState(lStat[iIdx])

    
    def GetPetColorAniList(self):
        return self.m_lAniState

    
    def ClearPetColorAni(self):
        if self.m_oPetColorAni1:
            self.m_oPetColorAni1.Release()
            self.m_oPetColorAni1 = None
        
        if self.m_oPetColorAni2:
            self.m_oPetColorAni2.Release()
            self.m_oPetColorAni2 = None
        
        self.SetPetColorAni(0)
        self.SetOpsBtnEnable(False)
        self.SetColorTips(-1)

    
    def SetColorTips(self, iType):
        if iType == 0:
            self.GetObject('txt_tips').SetText('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xba\xd8\xacV\xa6\xe2\xa4\xe8\xae\xd7')
        elif iType == 1:
            self.GetObject('txt_tips').SetText('\xa6\xb3\xa5\xbc\xbf\xef\xbe\xdc\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa1A\xbdT\xbb{\xa9\xce\xa9\xf1\xb1\xf3\xab\xe1\xa1A\xa4~\xaf\xe0\xa5\xcd\xa6\xa8\xb7s\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7')
        else:
            self.GetObject('txt_tips').SetText('')

    
    def GetSelectType(self):
        if self.GetObject('chk_color1').IsSelected():
            return dgtpetcolor.CColorDelegate.PART_SELF
        elif self.GetObject('chk_color2').IsSelected():
            return dgtpetcolor.CColorDelegate.PART_DECORATE1
        elif self.GetObject('chk_color3').IsSelected():
            return dgtpetcolor.CColorDelegate.PART_DECORATE2
        else:
            return dgtpetcolor.CColorDelegate.PART_DECORATE3

    
    def SetChgPart(self, iType):
        if iType == dgtpetcolor.CColorDelegate.PART_SELF:
            self.GetObject('chk_color1').SetSelect(True)
        elif iType == dgtpetcolor.CColorDelegate.PART_DECORATE1:
            self.GetObject('chk_color2').SetSelect(True)
        elif iType == dgtpetcolor.CColorDelegate.PART_DECORATE2:
            self.GetObject('chk_color3').SetSelect(True)
        else:
            self.GetObject('chk_color4').SetSelect(True)

    
    def SetOpsBtnEnable(self, bEnable):
        sNameList = [
            'left1',
            'right2',
            'btn_cons1',
            'btn_cons2',
            'btn_cancle']
        for sName in sNameList:
            \xd7\xda\xd2 = self.GetObject(sName)
            if \xd7\xda\xd2:
                pass
            \xd7\xda\xd2.Enable(bEnable)
        

    
    def SetChildFrameShow(self, bIsChild):
        sChildNameList = [
            'img_ChildBg',
            'loc_ChildAni',
            'txt_ChildItem',
            'btn_ChildColor',
            'img_ChildItem',
            'rtxt_ChildNeed',
            'txt_ChildColorDesc',
            'txt_PartFrm1',
            'txt_PartFrm4',
            'txt_PartFrm5',
            'txt_PartFrm6',
            'hfrm_1',
            'hfrm_2',
            'hfrm_3',
            'hfrm_4',
            'hfrm_5',
            'hfrm_6',
            'loc_Part1',
            'loc_Part2',
            'loc_Part3',
            'loc_Part4',
            'loc_Part5',
            'loc_Part6',
            'btn_PartLeft1',
            'btn_PartLeft2',
            'btn_PartLeft3',
            'btn_PartLeft4',
            'btn_PartLeft5',
            'btn_PartLeft6',
            'btn_PartRight1',
            'btn_PartRight2',
            'btn_PartRight3',
            'btn_PartRight4',
            'btn_PartRight5',
            'btn_PartRight6',
            'txt_Compensate',
            'tips_Compensate',
            'frm_Bg_child',
            'left2',
            'right1',
            'hloc_ChildAni']
        sPetNameList = [
            'frm_Bg',
            'img_PetBg1',
            'img_PetBg2',
            'loc_ani1',
            'loc_ani2',
            'btn_cons1',
            'btn_cons2',
            'left1',
            'right2',
            'btn_cancle',
            'btn_Tips',
            'chk_color1',
            'chk_color2',
            'chk_color3',
            'chk_color4',
            'txt_Pet1',
            'txt_Pet2',
            'txt_Pet3',
            'txt_Pet4',
            'btn_color',
            'rtxt_need',
            'txt_tips',
            'rtxt_PetDesc',
            'txt_PetDesc1',
            'txt_PetDesc2',
            'hloc_ani1',
            'hloc_ani2']
        for sName in sChildNameList:
            \xd7\xda\xd2 = self.GetObject(sName)
            if \xd7\xda\xd2:
                pass
            \xd7\xda\xd2.SetShow(bIsChild)
        
        for sName in sPetNameList:
            \xd7\xda\xd2 = self.GetObject(sName)
            if \xd7\xda\xd2:
                pass
            \xd7\xda\xd2.SetShow(not bIsChild)
        
        if self.m_oItemBox:
            pass
        self.m_oItemBox.SetShow(not bIsChild)
        if self.m_oChildItemBox:
            pass
        self.m_oChildItemBox.SetShow(bIsChild)
        if self.m_oChildColorAni:
            pass
        self.m_oChildColorAni.SetShow(bIsChild)
        for \xd7\xda\xd2 in self.m_lPartTxtObj:
            \xd7\xda\xd2.SetShow(bIsChild)
        

    
    def RefreshChildColorView(self, lColor):
        import combmacro
        self.m_lPartTxtObj = []
        iLen = len(lColor)
        sNameList = [
            'btn_PartLeft%d',
            'btn_PartRight%d',
            'hfrm_%d',
            'txt_PartFrm%d']
        for idx in xrange(6):
            iRealIndex = idx + 1
            if idx < iLen:
                bShow = True
                self.m_lPartTxtObj.append(combmacro.CTEXT(interface.CTextObject, 'loc_Part%d' % iRealIndex, self, '%d' % lColor[idx], interface.FontLT14_3, interface.COLOR_5, align = interface.ALIGN_CENTER | interface.ALIGN_MIDDLE))
            else:
                bShow = False
            for sName in sNameList:
                \xd7\xda\xd2 = self.GetObject(sName % iRealIndex)
                if \xd7\xda\xd2:
                    pass
                \xd7\xda\xd2.SetShow(bShow)
            
        

    
    def OnSelectPet(self, iPetID):
        LOG_DEBUG('\xbf\xef\xa4\xa4\xc3d\xaa\xab', iPetID)
        self.ssEmit(self.SS_SelectPet, iPetID)

    
    def OnItemChgCB(self, oItem):
        self.ssEmit(self.SS_UseItemChg, oItem)

    
    def OnAddChildColor(self, idx):
        self.ssEmit(self.SS_ChangeChildColor, idx, 1)

    
    def OnDecChildColor(self, idx):
        self.ssEmit(self.SS_ChangeChildColor, idx, -1)

    
    def OnClickChildItem(self, dData):
        import mdconvenientpurchase
        import builddefine
        mdconvenientpurchase.OpenGetAccessDlg(dData[builddefine.KEY_NEED_SHAPE])

    
    def RightUp(self):
        oParent = self.GetParent()
        if oParent:
            pass
        oParent.RightUp()
        combdialog.CCombSubWnd.RightUp(self)

    
    def Hold(self):
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'Hold'):
            oParent.Hold()
        

    
    def LeftUp(self):
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'LeftUp'):
            oParent.LeftUp()
        

    
    def LeftDown(self):
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'LeftDown'):
            oParent.LeftDown()
        

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtpetcolor.CColorDelegate(self)]

    
    def ChgColor(self):
        self.ssEmit(self.SS_ChgColor)

    
    def TurnLeft(self):
        self.SetPetColorAniDirection(1)

    
    def TrunRight(self):
        self.SetPetColorAniDirection(-1)

    
    def Confirm(self, iPos):
        self.ssEmit(self.SS_ConfirmColor, iPos)

    
    def ConfirmChild(self):
        self.ssEmit(self.SS_ConfirmChildColor)

    
    def GiveUp(self):
        self.ssEmit(self.SS_GiveUp)

    
    def ItemBuy(self):
        self.ssEmit(self.SS_ItemBuy)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ChgColor()
        elif iMsgID == 2:
            self.Confirm(1)
        elif iMsgID == 3:
            self.Confirm(2)
        elif iMsgID in (4, 37):
            self.TurnLeft()
        elif iMsgID in (38, 7):
            self.TrunRight()
        elif iMsgID == 8:
            self.GiveUp()
        elif iMsgID == 9:
            self.ConfirmChild()
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID <= 26:
            self.OnDecChildColor(iMsgID - 21)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID <= 36:
            self.OnAddChildColor(iMsgID - 31)
        elif iMsgID in (39, 40, 41, 42):
            self.OnClickPetModel()
        


g_Test = None

def Test():
    global g_Test
    g_Test = CColorDlg(interface.DialogPanel)
    g_Test.SetPos(100, 100)
