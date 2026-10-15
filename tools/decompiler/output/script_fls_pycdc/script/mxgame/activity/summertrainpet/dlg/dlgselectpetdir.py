# pycdc 交叉复核产物 · script.fls entry 3486
# co_filename(原始)='script/mxgame/activity/summertrainpet/dlg/dlgselectpetdir.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3486.pyc (Python 2.5)

import combdialog
import wrapinterface
import trainpetdefines
import slot
import petcenterdefine
import interface
import petskill
import style
import ratio
import cursor

def SwitchShow(bShow):
    if bShow:
        CSelectPetDirDlg.OpenUI()
    else:
        CSelectPetDirDlg.CloseUI()

PHYSIC_ATTACK_PET = 2
MAGIC_ATTACK_PET = 4

class CSelectPetDirDlg(combdialog.CCombDialog, slot.ISignalSubject):
    sUIName = 'dialog/activity/peiyang/xuanze.dlg'
    SS_SelectPet = 'SS_SelectPet(iIndex)'
    SS_ConfirmSelect = 'SS_ConfirmSelect()'
    SS_ClickTuJianLink = 'SS_ClickTuJianLink'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.ssInit()
        self.m_dPetAni = {
            trainpetdefines.PHYSIC_ATTACK_PET: None,
            trainpetdefines.MAGIC_ATTACK_PET: None }
        self.m_oSkillIconList = []
        self.m_oDelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        import dgtselectpetdir
        self.m_oDelegateList = [
            dgtselectpetdir.CSelectPetDirDgt(self)]

    
    def RefreshPetModelView(self, dPhysicPetModelData, dMagicPetModelData):
        self.DrawPetPhoto(trainpetdefines.PHYSIC_ATTACK_PET, dPhysicPetModelData)
        self.DrawPetPhoto(trainpetdefines.MAGIC_ATTACK_PET, dMagicPetModelData)

    
    def DrawPetPhoto(self, iLocKey, dPetModelData):
        iShape = dPetModelData['iShape']
        dPetDesc = dPetModelData['dPetDesc']
        oPetAni = wrapinterface.CPetAni(self, iShape, dPetDesc, fps = 150, iIsUseNewRes = True)
        sLocPetUIName = 'loc_qian%s' % iLocKey
        oPetAni.SetPos(*self.GetObject(sLocPetUIName).GetPos())
        oPetAni.SetDir(dPetModelData['iPetDir'])
        self.m_dPetAni[iLocKey] = oPetAni

    
    def RefreshPetDataView(self, dPhysicPetData, dMagicPetData):
        self.m_oSkillIconList = []
        self.RefreshPetView(PHYSIC_ATTACK_PET, dPhysicPetData)
        self.RefreshPetView(MAGIC_ATTACK_PET, dMagicPetData)

    
    def RefreshPetView(self, iIndex, dPetData):
        self.GetObject('text_str%d' % iIndex).SetText(dPetData['sAttack'])
        self.GetObject('text_cha%d' % iIndex).SetText(dPetData['sDefense'])
        self.GetObject('text_con%d' % iIndex).SetText(dPetData['sCon'])
        self.GetObject('text_mag%d' % iIndex).SetText(dPetData['sMagic'])
        self.GetObject('text_dex%d' % iIndex).SetText(dPetData['sSpeed'])
        lstSkill = dPetData['lstSkill']
        self.SetPetSkillBox(iIndex, lstSkill)

    
    def SetPetSkillBox(self, iIndex, lSkillId):
        oSkillImg = self.GetObject('box_skills%d' % iIndex)
        (iImgX, iImgY) = oSkillImg.GetPos()
        for iIndex, iSkillID in enumerate(lSkillId):
            if not iSkillID:
                continue
            
            oParent = oSkillImg.m_Imagess[iIndex]
            (iX, iY) = oParent.GetPos()
            oSkillIcon = CSkillIcon(self, iImgX + iX + 3, iImgY + iY + 3, iSkillID, iIndex + 1)
            if iSkillID == petcenterdefine.SKILLID_SHOUJUE:
                oSkillIcon.SetImgGrey()
            
            self.m_oSkillIconList.append(oSkillIcon)
        

    
    def RefreshPetSelect(self, iSelectPetIndex):
        for iIndex in xrange(1, 3):
            self.GetObject('btn_gouxuan%d' % iIndex).SetSelect(iIndex == iSelectPetIndex)
        

    
    def CloseWindow(self):
        self.CloseUI()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.ssEmit(self.SS_SelectPet, trainpetdefines.PHYSIC_ATTACK_PET)
        elif iMsgID == 3:
            self.ssEmit(self.SS_ConfirmSelect)
        elif iMsgID == 4:
            self.ssEmit(self.SS_SelectPet, trainpetdefines.MAGIC_ATTACK_PET)
        elif iMsgID == 6:
            self.ssEmit(self.SS_ClickTuJianLink)
        



class CSkillIcon(interface.CClickBox):
    
    def __init__(self, oParent, iX, iY, iSkillId, iBoxIndex):
        interface.CClickBox.__init__(self, oParent, 0, 0, alpha = 0)
        self.m_iSkillID = iSkillId
        self.m_oImg = None
        self.m_oFlagIcon = None
        self.m_iBoxIndex = iBoxIndex
        self.m_oSkillTips = None
        self.SetPos(iX, iY)
        self.CreateImg()

    
    def CreateImg(self):
        import petskill
        import skilliconpath
        import item
        import ui as dMagicPetModelData
        if self.m_iSkillID == trainpetdefines.SKILLID_SHOUJUE:
            dData = trainpetdefines.SPECIALSKILL[self.m_iBoxIndex]
            self.m_oImg = item.CreateItem120StretchImage(self, dData['iShape'])
            self.m_oImg.SetScale(dData['iScale'])
            self.ShowExtraFlag(dData['bExtra'])
            self.SetSize(*self.m_oImg.GetSize())
        elif self.m_iBoxIndex == trainpetdefines.SHENGLING_FIVE_SKILLBOX_LOCK:
            dData = trainpetdefines.SPECIALSKILL[self.m_iBoxIndex]
            sPath = style.GetPath(dData['sPath'])
            self.m_oImg = dMagicPetModelData.CImage(self, style.GetPath(sPath), interface.UIPath)
        else:
            (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(petskill.GetShape(self.m_iSkillID))
            self.m_oImg = interface.CStretchImagesObject(self, sPath, sPack)
            self.SetSize(*self.m_oImg.GetSize())

    
    def SetImgCenter(self):
        interface.Center(self.m_oImg)

    
    def SetImgGrey(self):
        if self.m_oImg:
            pass
        self.m_oImg.SetGrey()
        if self.m_oFlagIcon:
            pass
        self.m_oFlagIcon.SetGrey()

    
    def ShowExtraFlag(self, bShow):
        if bShow:
            self.m_oFlagIcon = interface.CBitmapObject(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xb6\xee\xcd\xe2.png', interface.UIPath)
            self.m_oFlagIcon.SetZ(1)
        else:
            self.m_oFlagIcon = None

    
    def Enter(self):
        self.m_oSkillTips = CSkillTips(self.m_iSkillID, self.m_iBoxIndex)

    
    def Leave(self):
        if self.m_oSkillTips:
            self.m_oSkillTips = None
        



class CSkillTips(interface.CBoxObject, interface.CBase):
    TIPSWIDTH = 220
    TIPSHEIGHT = 100
    
    def __init__(self, iSkillId, iBoxIndex):
        interface.CBoxObject.__init__(self, interface.MainPanel, self.TIPSWIDTH, self.TIPSHEIGHT, 8224, 128)
        self.m_oNameText = None
        self.m_oSkillDescText = None
        self.m_iBoxIndex = iBoxIndex
        self.CreateInfo(iSkillId)
        self.ResetPos()
        self.Topmost()

    
    def CreateInfo(self, iSkillId):
        sColor = style.GetStr('dlgpet.CSkillTips', 'data_txt_color')
        if iSkillId == trainpetdefines.SKILLID_SHOUJUE:
            dData = trainpetdefines.SPECIALSKILL[self.m_iBoxIndex]
            sName = sColor + dData['sName']
            sDesc = dData['sDesc']
        elif self.m_iBoxIndex == trainpetdefines.SHENGLING_FIVE_SKILLBOX_LOCK:
            dData = None[trainpetdefines.SPECIALSKILL.m_iBoxIndex]
            sName = sColor + dData['sName']
            sDesc = dData['sDesc']
        else:
            dSkillData = petskill.GetData(iSkillId)
            sName = sColor + dSkillData['name'] + '(%s)' % [
                '\xb3Q\xb0\xca',
                '\xa5D\xb0\xca'][dSkillData['type'] != 0]
            sDesc = dSkillData['desc']
        self.m_oNameText = interface.CRichTextObject(self, 220, interface.FontLT18_1, sName)
        self.m_oNameText.SetPos(10, 10)
        self.m_oSkillDescText = interface.CRichTextObject(self, 190, interface.FontLT14_3, sDesc)
        self.m_oSkillDescText.SetPos(10, 28)

    
    def ResetPos(self):
        (iW, iH) = self.m_oSkillDescText.GetSize()
        if iH + 28 > self.TIPSHEIGHT:
            iH = iH + 28 + 4
            self.SetSize(self.TIPSWIDTH, iH)
        else:
            iH = self.TIPSHEIGHT
        (iX, iY) = cursor.GetPos()
        iX = iX - self.TIPSWIDTH / 2
        if iX < 0:
            iX = 0
        elif iX + self.TIPSWIDTH >= ratio.WINDOW_WIDTH:
            iX = 800 - self.TIPSWIDTH
        
        if iY + iH + 50 > ratio.WINDOW_HEIGHT:
            iY = iY - 50 - iH
        else:
            iY = iY + 50
        self.SetPos(iX, iY)
