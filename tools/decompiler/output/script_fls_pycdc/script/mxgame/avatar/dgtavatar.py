# pycdc 交叉复核产物 · script.fls entry 455
# co_filename(原始)='script/mxgame/avatar/dgtavatar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_455.pyc (Python 2.5)

import avatar
import avatarcode
import avatardefine
import commondialog
import delegatebase
import dialoguecommondata
import dlgphoto
import hero
import item
import itemdefine
import mdavatar
import mdpropitem
import misc
import netplayerphoto
import permission
import rendertest
import usermacro

class CAvatarDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_iUsePhotoList = None
        self.m_iShowPhotoList = None
        self.m_iRealShowPhotoList = None
        self.m_iPerValidPhotoList = None
        self.m_iCurVer = None
        self.m_iCurPart = None
        self.m_iCurStowPage = 1
        self.m_iMaxStowPage = 1
        self.m_lCurSelectStowInfo = None
        self.m_bOpenChildren = False
        self.m_bOpenChristmas = False
        self.m_dAllPhotoList = []
        self.m_iTimeLimit = 90
        self.m_bIsExperience = False
        self.m_iItemID = 0
        self.m_iModel = 0
        self.m_dAvatarPalCase = { }
        self.m_iCurPalVerList = set()
        self.m_dPalCase = { }
        self.m_bFirstSlider = True
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetView(self):
        ''':rtype: dlgappearanceavatar.CAvatarDlg '''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        self.InitDlgSignal()
        self.InitModelSignal()
        import hero
        hero.AddRefreshCallback('%s_PhotoEffect' % id(self), (('m_PhotoEffect',),), self.OnPhotoEffectChange)
        hero.AddRefreshCallback('%s_Gold' % id(self), (('m_Gold',),), self.OnGoldChange)
        rendertest.ConnectChangeCB(self.OnRenderStateChange)
        self.OnRenderStateChange()
        self.InitDlg()

    
    def InitDlgSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_BuyAvatar, self.OnBuyAvatar)
        oView.ssConnect(oView.SS_UseAvatar, self.OnUseAvatar)
        oView.ssConnect(oView.SS_StowAvatar, self.OnStowAvatar)
        oView.ssConnect(oView.SS_BuyTicket, self.OnBuyTicket)
        oView.ssConnect(oView.SS_DelStow, self.OnDelStow)
        oView.ssConnect(oView.SS_RadomMatch, self.OnRadomMatch)
        oView.ssConnect(oView.SS_ResetAll, self.OnResetAll)
        oView.ssConnect(oView.SS_ResetPath, self.OnResetPath)
        oView.ssConnect(oView.SS_CloseWindow, self.OnCloseWindow)
        oView.ssConnect(oView.SS_AvatarSelect, self.OnAvatarSelect)
        oView.ssConnect(oView.SS_StowSelect, self.OnStowSelect)
        oView.ssConnect(oView.SS_ChangeStyle, self.OnChangeStyle)
        oView.ssConnect(oView.SS_ChangePart, self.OnChangePart)
        oView.ssConnect(oView.SS_PerStowPage, self.OnPerStowPage)
        oView.ssConnect(oView.SS_NxtStowPage, self.OnNxtStowPage)
        oView.ssConnect(oView.SS_SwitchPage, self.OnSwitchPage)
        oView.ssConnect(oView.SS_SelectAIPicture, self.OnSelectPicture)
        oView.ssConnect(oView.SS_OnHueSliderChange, self.OnHueSlider)
        oView.ssConnect(oView.SS_ResetPalChange, self.OnResetPalChange)
        oView.ssConnect(oView.SS_ClickPalBtn, self.OnClickPalBtn)

    
    def InitModelSignal(self):
        oModel = mdavatar.GetAvatarModel()
        oModel.ssConnect(oModel.SS_StowIntListChange, self.OnStowIntListChange)
        oModel.ssConnect(oModel.SS_PriceChange, self.OnPhotoPriceChange)
        oModel.ssConnect(oModel.SS_OpenChildrenStyle, self.OnOpenChildrenStyle)
        oModel.ssConnect(oModel.SS_OpenChristmasStyle, self.OnOpenChristmasStyle)
        oModel.ssConnect(oModel.SS_PhotoChange, self.OnPhotoChange)
        oModel.ssConnect(oModel.SS_TimeLimitChange, self.OnTimeLimitChange)
        oModel.ssConnect(oModel.SS_SetIsExperience, self.OnSetIsExperience)
        oModel.ssConnect(oModel.SS_AIAvatarChg, self.OnAIAvatarChange)
        oModel.ssConnect(oModel.SS_ImitateAvatar, self.RefreshImitateAvatar)
        oItemModel = mdpropitem.GetModel()
        oItemModel.ssConnect(oItemModel.SS_UpdateBagChangeRecommend, self.UpdateBagChangeRecommend)

    
    def InitDlg(self):
        self.InitPhotoList()
        oView = self.GetView()
        self.RefreshPhotoView(self.m_iShowPhotoList, self.GetSelectAvatarDesc())
        oView.SetShowChilerenBtn(False)
        oView.SetShowChristmasBtn(False)
        oView.SetCost(0)
        self.RefreshAvatarItemList(self.m_iShowPhotoList, avatardefine.IDX_Hair)
        oView.RefreshSpecialPartUI(self.m_iCurVer, self.m_iCurPart)
        self.ResetChestShow()
        self.SwitchToCurPage()
        self.RequestStowInfo()
        self.RequestOtherStyle()
        self.SetColorBlockWithDesc({
            avatar.DESC_AVATAR_HSV: self.GetSelectAvatarDesc() })
        self.ClearColorBlock()
        self.UpdateViewHsvShow()
        import netplayerphoto
        netplayerphoto.C2SPhotoPay()

    
    def InitPhotoList(self):
        import hero
        self.m_iUsePhotoList = self.ProcressPhotoList(avatar.GetHeroPhoto())
        if avatar.IsDefaultPhoto(self.m_iUsePhotoList) or not self.CheckPhotoCanBuy(self.m_iUsePhotoList):
            iIsMale = hero.GetProp('m_Sex', 1)
            if iIsMale == 1:
                self.m_iShowPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[avatardefine.DEFAULT_SHOW_MALE])
                self.m_iPerValidPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[avatardefine.DEFAULT_SHOW_MALE])
            else:
                self.m_iShowPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[avatardefine.DEFAULT_SHOW_FEMALE])
                self.m_iPerValidPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[avatardefine.DEFAULT_SHOW_FEMALE])
        else:
            self.m_iShowPhotoList = self.ProcressPhotoList(self.m_iUsePhotoList)
            self.m_iPerValidPhotoList = self.ProcressPhotoList(self.m_iUsePhotoList)
        for iPhotoID, tPhotoInfo in hero.GetPropPhotoArr().items():
            if CmpList(tPhotoInfo[1], self.m_iUsePhotoList):
                self.m_lCurSelectStowInfo = [
                    False,
                    iPhotoID]
                break
                continue
        

    
    def RequestStowInfo(self):
        import netplayerphoto
        netplayerphoto.C2SOpenStowPhoto()

    
    def RequestOtherStyle(self):
        import netplayerphoto
        netplayerphoto.C2SOpenChildren()
        netplayerphoto.C2SOpenChrismas()

    
    def RequestPrice(self, iPhotoList):
        import netplayerphoto
        (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        netplayerphoto.C2SGetPhotoPay(iVer / 100)

    
    def RefreshAvatarItemList(self, iPhotoList, iPartIdx):
        (iBody, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        iShowPhotoList = self.ProcressPhotoList(avatar.GetHeroPhoto())
        (_, iVer2) = avatar.GetRealBodyInfo(iShowPhotoList[avatardefine.IDX_Body])
        if self.m_bOpenChildren:
            bShowChildren = True
            bShowChristmas = False
        elif self.m_bOpenChristmas:
            bShowChristmas = True
            bShowChildren = False
        elif iVer in (avatardefine.STYLE_1500, avatardefine.STYLE_1600):
            bShowChristmas = True
            bShowChildren = False
        elif iVer in (avatardefine.STYLE_1300, avatardefine.STYLE_1400):
            bShowChildren = True
            bShowChristmas = False
        else:
            bShowChildren = False
            bShowChristmas = False
        self.GetView().RefreshAvatarItemList(iVer, iPartIdx, iPhotoList[iPartIdx], bShowChildren, bShowChristmas)
        self.m_iCurVer = iVer
        self.m_iCurPart = iPartIdx
        self.OnRenderStateChange()
        self.RequestPrice(iPhotoList)

    
    def OnRenderStateChange(self):
        if self.m_iCurVer in avatardefine.USE_RENDER_LIST:
            bAble = rendertest.IsRenderAble()
            if not bAble:
                pass
            self.GetView().SetOpenglTipsShow(not self.GetView().IsInChestPage())
        else:
            self.GetView().SetOpenglTipsShow(False)
        self.OnRenderStateChangeForChild()

    
    def OnRenderStateChangeForChild(self):
        import interface
        oTextObject = self.GetView().GetObject('txt_tips2')
        if self.m_iCurVer in (avatardefine.STYLE_1300,) and not self.GetView().IsInChestPage():
            self.m_oTempText = interface.CTextObject(self.GetView(), '6\xa4\xeb10\xa4\xe924:00\xab\xe1\xb5L\xaak\xc1\xca\xb6R', oTextObject.GetFont(), oTextObject.GetColor())
            self.m_oTempText.SetPos(82, 439)
        else:
            self.m_oTempText = None

    
    def OnAvatarSelect(self, iValue):
        self.RecordLastValidPhoto()
        self.m_iShowPhotoList[self.m_iCurPart] = iValue
        self.AmendRandomData(self.m_iShowPhotoList)
        self.RefreshPhotoView(self.m_iShowPhotoList, self.GetSelectAvatarDesc())
        self.SwitchToCurPage()
        self.RequestPrice(self.m_iShowPhotoList)
        self.ClearChestSelect()

    
    def OnStowSelect(self, bStow, iPhotoID, iPhotoIntList, dAvatarDesc):
        LOG_DEBUG('\xbf\xef\xbe\xdc\xa6\xac\xc2\xc3\xa6\xe7\xaaA', bStow, iPhotoID, iPhotoIntList, dAvatarDesc)
        self.m_lCurSelectStowInfo = [
            bStow,
            iPhotoID]
        self.RefreshPhotoView(avatar.Int2PhotoArr(*iPhotoIntList), dAvatarDesc)
        self.m_iShowPhotoList = self.ProcressPhotoList(avatar.Int2PhotoArr(*iPhotoIntList))
        self.RecordLastValidPhoto()
        self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
        (_, iVer) = avatar.GetRealBodyInfo(self.m_iShowPhotoList[avatardefine.IDX_Body])
        self.SetColorBlockWithDesc(dAvatarDesc)
        if bStow:
            self.SelectToColorBlockWithDesc(dAvatarDesc)
        else:
            self.ClearColorBlock()
        self.UpdateViewHsvShow()

    
    def OnChangeStyle(self, iVer):
        LOG_DEBUG('\xa7\xef\xc5\xdc\xad\xb7\xae\xe6', iVer)
        oView = self.GetView()
        oView.RefreshSpecialPartUI(iVer, self.m_iCurPart)
        (_, iMyVer) = avatar.GetRealBodyInfo(self.m_iUsePhotoList[avatardefine.IDX_Body])
        if iVer == iMyVer:
            self.RefreshPhotoView(self.m_iUsePhotoList, self.GetSelectAvatarDesc())
            self.m_iShowPhotoList = self.ProcressPhotoList(self.m_iUsePhotoList)
            self.RecordLastValidPhoto()
            self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
            oView.ClearStowSelect()
        elif iVer in avatardefine.STYLE_2_DEFAULT:
            self.RefreshPhotoView(avatardefine.STYLE_2_DEFAULT[iVer], self.GetSelectAvatarDesc())
            self.m_iShowPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[iVer])
            self.RecordLastValidPhoto()
            self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
            oView.ClearStowSelect()
        
        self.SwitchToCurPage()
        self.ClearChestSelect()
        self.UpdateViewHsvShow()

    
    def OnChangePart(self, iPartIdx):
        LOG_DEBUG('\xa7\xef\xc5\xdc\xb3\xa1\xa6\xec', iPartIdx)
        self.RefreshAvatarItemList(self.m_iShowPhotoList, iPartIdx)
        self.UpdateViewHsvShow()

    
    def OnBuyAvatar(self):
        LOG_DEBUG('\xc1\xca\xb6R\xc0Y\xb9\xb3')
        if not self.IsCanOps():
            return None
        
        iLeftTime = self.GetPhotoLeftTime(self.m_iRealShowPhotoList)
        if iLeftTime and iLeftTime > 0:
            tHavePhotoInfo = self.GetHavePhotoInfo(self.m_iRealShowPhotoList)
            if not tHavePhotoInfo:
                return None
            
            dAvatarDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
            dNewPalInfo = self.GetSelectAvatarDesc()
            for dHave in dAvatarDescList:
                if dNewPalInfo == dHave[avatar.DESC_AVATAR_HSV]:
                    usermacro.PROMPT_MSG('\xa7A\xa4w\xbe\xd6\xa6\xb3\xb8\xd3\xc0Y\xb9\xb3\xa4\xe8\xae\xd7')
                    return None
                    continue
            
        elif not self.CheckPhotoCanBuy(self.m_iRealShowPhotoList):
            usermacro.PROMPT_MSG('\xb8\xd3\xc0Y\xb9\xb3\xad\xb7\xae\xe6\xa4w\xa4U\xac[\xa1A\xb5L\xaak\xc4~\xc4\xf2\xa8\xcf\xa5\xce\xa1A\xbd\xd0\xc1\xca\xb6R\xa8\xe4\xa5L\xad\xb7\xae\xe6')
            return None
        elif iLeftTime == 0:
            self.BuyPhotoAgain()
        elif self.GetValidHeroPhotoNum() >= 7:
            self.BuyAndReplaceAvatar()
        else:
            self.BuyPhoto(self.GetPhotoPayIdx(), '')

    
    def OnOnlyBuyAvatarPal(self, iPhotoID, dNewPalInfo):
        iLeftTime = self.GetPhotoLeftTime(self.m_iRealShowPhotoList)
        iNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_PAL_TICKET)
        if iNum:
            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1007)
        else:
            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1008)
        sMsg = sMsg.replace('$price2', '200')
        sMsg = sMsg.replace('$count2', '1')
        sMsg = sMsg.replace('$day', str(iLeftTime))
        commondialog.ShowMessageBox(sMsg, ('\xbdT\xa9w\xc1\xca\xb6R', '\xa8\xfa\xae\xf8'), (misc.Functor(self.OnOnlyBuyAvatarPalPK, iPhotoID, bool(iNum), dNewPalInfo), None), bIsIgnoreCBSelfParameter = True)

    
    def OnOnlyBuyAvatarPalPK(self, iPhotoID, iBuyType, dNewPalInfo):
        netplayerphoto.C2SBuyPhotoPal(iPhotoID, iBuyType, dNewPalInfo)

    
    def OnUseAvatar(self):
        LOG_DEBUG('\xa8\xcf\xa5\xce\xc0Y\xb9\xb3')
        if not self.IsCanOps():
            return None
        
        import usermacro
        import netplayerphoto
        if self.m_lCurSelectStowInfo is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xa4\xa4\xbb\xdd\xadn\xa8\xcf\xa5\xce\xaa\xba\xc0Y\xb9\xb3')
            return None
        
        if not self.IsHasAvatar(self.m_iRealShowPhotoList):
            usermacro.PROMPT_MSG('\xa7A\xc1\xd9\xa8S\xbe\xd6\xa6\xb3\xb8\xd3\xc0Y\xb9\xb3')
            return None
        
        (bStow, iPhotoID) = self.m_lCurSelectStowInfo
        netplayerphoto.C2SUsePropPhotoN(iPhotoID)
        LOG_DEBUG('iPhotoID>', bStow, iPhotoID)
        usermacro.PROMPT_MSG('\xa4w\xb8g\xb1N\xc0Y\xb9\xb3\xb3]\xb8m\xac\xb0\xb7\xed\xabe\xa8\xcf\xa5\xce\xaa\xba\xc0Y\xb9\xb3')

    
    def OnStowAvatar(self):
        LOG_DEBUG('\xa6\xac\xc2\xc3\xc0Y\xb9\xb3')
        if not self.IsCanOps():
            return None
        
        if not self.CheckPhotoCanBuy(self.m_iRealShowPhotoList):
            usermacro.PROMPT_MSG('\xa7\xef\xc0Y\xb9\xb3\xad\xb7\xae\xe6\xa4w\xa4U\xac[\xa1A\xb5L\xaak\xc4~\xc4\xf2\xa8\xcf\xa5\xce\xa1A\xbd\xd0\xc1\xca\xb6R\xa8\xe4\xa5L\xad\xb7\xae\xe6')
            return None
        
        lStowIntList = []
        for iStowIntList, dPhotoDesc in mdavatar.GetAvatarModel().GetStowIntList():
            if self.CheckPhotoCanBuy(avatar.Int2PhotoArr(*iStowIntList)):
                lStowIntList.append((iStowIntList, dPhotoDesc))
                continue
        
        dTmp = { }
        iIdx = 0
        dPalCase = self.GetSelectAvatarDesc()
        dPalCase = misc.DeepCopy(dPalCase)
        for iPhotoIntList, dPhotoDesc in lStowIntList:
            dTmp[iIdx] = {
                'iPhotoIntList': avatar.Int2PhotoArr(*iPhotoIntList),
                'dPalCase': dPhotoDesc.get(avatar.DESC_AVATAR_HSV) }
            iIdx += 1
        
        if len(lStowIntList) < avatardefine.STOW_PHOTO_MAXIMUM:
            dTmp[iIdx] = {
                'iPhotoIntList': self.m_iRealShowPhotoList[:],
                'dPalCase': dPalCase }
            avatar.DoCommitStow(dTmp)
            self.DoReplaceStow(dTmp, True)
        else:
            LOG_DEBUG(dTmp)
            data = {
                'current': {
                    'iPhotoIntList': self.m_iRealShowPhotoList[:],
                    'dPalCase': dPalCase },
                'list': range(len(lStowIntList)),
                'callback': misc.Functor(self.OnReplaceStowCB) }
            data.update(dTmp)
            dlgphoto.Show(data)

    
    def OnBuyTicket(self):
        LOG_DEBUG('\xc1\xca\xb6R\xc0Y\xb9\xb3\xa8\xe9')
        import netappearance
        import appearancedefine
        netappearance.C2SOpenGiftDlg(appearancedefine.GIFT_TYPE_PHOTO, 0)

    
    def OnDelStow(self):
        LOG_DEBUG('\xa7R\xb0\xa3\xa6\xac\xc2\xc3')
        if not self.IsCanOps():
            return None
        
        import usermacro
        import commondialog
        import misc
        import hero
        if self.m_lCurSelectStowInfo is None:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa6\xac\xc2\xc3\xa4\xe8\xae\xd7')
            return None
        
        (bStow, iPhotoID) = self.m_lCurSelectStowInfo
        if bStow:
            commondialog.ShowMessageBox('\xb1z\xbf\xef\xbe\xdc\xa4F\xa7R\xb0\xa3\xa6\xb9\xc0Y\xb9\xb3\xa4\xe8\xae\xd7\xa1A\xa7R\xb0\xa3\xab\xe1\xb1N\xb5L\xaak\xab\xec\xb4_\xa1A\xbdT\xbb{\xadn\xa7R\xb0\xa3\xa6\xb9\xa4\xe8\xae\xd7\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.DoDelStow, iPhotoID), None))
        elif iPhotoID == avatardefine.DEFAULT_AVATAR_ID:
            usermacro.PROMPT_MSG('\xc0q\xbb{\xc0Y\xb9\xb3\xa4\xa3\xaf\xe0\xa7R\xb0\xa3')
            return None
        
        tPhotoInfoDict = hero.GetPropPhotoArr()
        iKeyList = tPhotoInfoDict.keys()
        if avatardefine.DEFAULT_AVATAR_ID not in iKeyList:
            hero.SetDefaultPropPhoto()
            tPhotoInfoDict = hero.GetPropPhotoArr()
            iKeyList = tPhotoInfoDict.keys()
        
        if len(iKeyList) == 1:
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xa8S\xa6\xb3\xc0Y\xb9\xb3\xa5i\xa5H\xa7R\xb0\xa3')
        
        if iPhotoID not in tPhotoInfoDict:
            LOG('\xbc\xc6\xbe\xda\xa6\xb3\xbb~', iPhotoID, tPhotoInfoDict)
            return None
        
        tPhotoInfo = tPhotoInfoDict[iPhotoID]
        if tPhotoInfo[0]:
            sTxt = '\xb8\xd3\xc0Y\xb9\xb3\xaa\xba\xb3\xd1\xbel\xa8\xcf\xa5\xce\xae\xc9\xb6\xa1\xac\xb0#Y%d#n\xa4\xd1\xa1A\xa7R\xb0\xa3\xab\xe1\xb1N\xb5L\xaak\xab\xec\xb4_\xa1A\xbdT\xbb{\xadn\xa7R\xb0\xa3\xa6\xb9\xc0Y\xb9\xb3\xb6\xdc\xa1H' % tPhotoInfo[0]
        else:
            sTxt = '\xb1z\xbf\xef\xbe\xdc\xa4F\xa7R\xb0\xa3\xa6\xb9\xc0Y\xb9\xb3\xa4\xe8\xae\xd7\xa1A\xa7R\xb0\xa3\xab\xe1\xb1N\xb5L\xaak\xab\xec\xb4_\xa1A\xbdT\xbb{\xadn\xa7R\xb0\xa3\xa6\xb9\xa4\xe8\xae\xd7\xb6\xdc\xa1H'
        commondialog.ShowMessageBox(sTxt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.DoDelPhoto, iPhotoID), None))

    
    def DoDelStow(self, iPhotoID, oDlg):
        LOG_DEBUG('>DoDelStow oDlg, iPhotoID>', oDlg, iPhotoID)
        lStowIntList = mdavatar.GetAvatarModel().GetStowIntList()
        dTmp = { }
        for iPhotoIntList, dPhotoDesc in enumerate(lStowIntList):
            if iIdx == iPhotoID:
                dTmp[iIdx] = {
                    'iPhotoIntList': [
                        0] * 16,
                    'dPalCase': { } }
                continue
            dTmp[iIdx] = {
                'iPhotoIntList': avatar.Int2PhotoArr(*iPhotoIntList),
                'dPalCase': misc.DeepCopy(dPhotoDesc.get(avatar.DESC_AVATAR_HSV, { })) }
        
        self.ClearChestSelect()
        avatar.DoCommitStow(dTmp)
        self.DoReplaceStow(dTmp, False)

    
    def DoDelPhoto(self, iPhotoID, oDlg):
        LOG_DEBUG('>DoDelPhoto oDlg, iPhotoID>', oDlg, iPhotoID)
        import netplayerphoto
        netplayerphoto.C2SDelCurPhoto(iPhotoID)
        self.ClearChestSelect()

    
    def OnRadomMatch(self):
        LOG_DEBUG('\xc0H\xbe\xf7\xb7f\xb0t')
        import avatarnewdata
        import random
        (_, iVer) = avatar.GetRealBodyInfo(self.m_iShowPhotoList[avatardefine.IDX_Body])
        iPhotoList = [
            None]
        for iPartIdx in range(1, 16):
            if iPartIdx == avatardefine.IDX_Body:
                iPhotoList.append(iVer / 100)
                continue
            sFileNameList = avatarnewdata.GetPartNameList(iVer, iPartIdx)
            if sFileNameList:
                sFileName = random.choice(sFileNameList)
                iValue = avatarnewdata.GetPartValueByName(sFileName, iPartIdx == avatardefine.IDX_Body)
                iPhotoList.append(iValue)
                continue
            iPhotoList.append(None)
        
        iPhotoList = self.AmendRandomData(iPhotoList)
        self.RefreshPhotoView(iPhotoList, self.GetSelectAvatarDesc())
        self.m_iShowPhotoList = self.ProcressPhotoList(iPhotoList)
        self.RecordLastValidPhoto()
        self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
        self.SwitchToCurPage()
        self.ClearChestSelect()

    
    def AmendRandomData(self, iPhotoList):
        import avatarnewdata
        (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        sHairList = avatarnewdata.GetPartNameList(iVer, avatardefine.IDX_Hair, True)
        iHairValue = iPhotoList[avatardefine.IDX_Hair]
        sHairName = sHairList[iPhotoList[avatardefine.IDX_Hair] - 1]
        sHairPartList = avatarnewdata.GetPartNameList(iVer, avatardefine.IDX_HairPath)
        sHairPartName = '%s_' % sHairName
        if sHairPartName in sHairPartList:
            iPhotoList[avatardefine.IDX_HairPath] = iHairValue
        else:
            iPhotoList[avatardefine.IDX_HairPath] = 0
        return iPhotoList

    
    def OnResetAll(self):
        LOG_DEBUG('\xad\xab\xb8m\xa5\xfe\xb3\xa1')
        (_, iVer) = avatar.GetRealBodyInfo(self.m_iShowPhotoList[avatardefine.IDX_Body])
        iPhotoList = avatardefine.STYLE_2_DEFAULT[iVer][:]
        iPhotoList = self.AmendRandomData(iPhotoList)
        self.RefreshPhotoView(iPhotoList, self.GetSelectAvatarDesc())
        self.m_iShowPhotoList = self.ProcressPhotoList(avatardefine.STYLE_2_DEFAULT[iVer])
        self.RecordLastValidPhoto()
        self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
        self.SwitchToCurPage()
        self.ClearChestSelect()

    
    def OnResetPath(self):
        LOG_DEBUG('\xad\xab\xb8m\xb3\xa1\xa6\xec')
        (_, iVer) = avatar.GetRealBodyInfo(self.m_iShowPhotoList[avatardefine.IDX_Body])
        iPhotoList = self.m_iShowPhotoList[:]
        iPhotoList[self.m_iCurPart] = avatardefine.STYLE_2_DEFAULT[iVer][self.m_iCurPart]
        iPhotoList = self.AmendRandomData(iPhotoList)
        self.RefreshPhotoView(iPhotoList, self.GetSelectAvatarDesc())
        self.m_iShowPhotoList = self.ProcressPhotoList(iPhotoList)
        self.RecordLastValidPhoto()
        self.RefreshAvatarItemList(self.m_iShowPhotoList, self.m_iCurPart)
        self.SwitchToCurPage()
        self.ClearChestSelect()

    
    def OnCloseWindow(self):
        import hero
        hero.RemoveRefreshCallback('%s_Gold' % id(self), (('m_Gold',),))
        hero.RemoveRefreshCallback('%s_PhotoEffect' % id(self), (('m_PhotoEffect',),))

    
    def OnStowIntListChange(self, tStowIntList):
        LOG_DEBUG('\xa6\xac\xc2\xc3\xc0Y\xb9\xb3\xbc\xc6\xbe\xda\xa7\xef\xc5\xdc', tStowIntList)
        self.ResetChestShow()
        self.RefreshStowBtn(self.m_iRealShowPhotoList, self.GetSelectAvatarDesc())

    
    def OnPhotoPriceChange(self, iGold, iPoint):
        LOG_DEBUG('\xc0Y\xb9\xb3\xbb\xf9\xae\xe6\xc5\xdc\xa4\xc6', iGold, iPoint)
        if self.IsHasAvatar(self.m_iRealShowPhotoList):
            iGold = iPoint = 0
        
        self.GetView().SetCost(iGold)

    
    def OnOpenChildrenStyle(self):
        LOG_DEBUG('\xb6}\xb1\xd2\xa8\xe0\xb5\xa3\xb8`\xad\xb7\xae\xe6')
        self.m_bOpenChildren = True
        self.GetView().SetShowChilerenBtn(True)

    
    def OnOpenChristmasStyle(self):
        LOG_DEBUG('\xb6}\xb1\xd2\xb8t\xbd\xcf\xb8`\xad\xb7\xae\xe6')
        self.m_bOpenChristmas = True
        self.GetView().SetShowChristmasBtn(True)

    
    def OnPhotoChange(self):
        import hero
        LOG_DEBUG('\xa8\xa4\xa6\xe2\xc0Y\xb9\xb3\xbc\xc6\xbe\xda\xa7\xef\xc5\xdc', hero.GetPropPhotoArr())
        self.m_iUsePhotoList = self.ProcressPhotoList(avatar.GetHeroPhoto())
        self.ResetChestShow()
        self.RefreshPhotoView(self.m_iRealShowPhotoList, self.GetSelectAvatarDesc())
        self.RequestPrice(self.m_iRealShowPhotoList)
        self.RefreshAvatarItemList(self.m_iRealShowPhotoList, self.m_iCurPart)

    
    def OnTimeLimitChange(self, iTime):
        LOG_DEBUG('\xae\xc9\xb6\xa1\xad\xad\xa8\xee\xb5o\xa5\xcd\xa7\xef\xc5\xdc', iTime)
        self.m_iTimeLimit = iTime

    
    def OnSetIsExperience(self, bIsExperience, iItemID, iModel):
        LOG_DEBUG('\xacO\xa7_\xac\xb0\xc5\xe9\xc5\xe7\xbc\xd2\xa6\xa1', bIsExperience, iItemID, iModel)
        self.m_bIsExperience = bIsExperience
        self.m_iItemID = iItemID
        self.m_iModel = iModel

    
    def OnAIAvatarChange(self):
        import usermacro
        iAIList = mdavatar.GetAvatarModel().GetAIList()
        if iAIList and self.m_iCurVer in avatardefine.AI_AVATAR:
            usermacro.PROMPT_MSG('\xa4\xc7\xb0t\xa6\xa8\xa5\\\xa1A\xa4w\xac\xb0\xa7A\xa5\xcd\xa6\xa8\xb4\xbc\xaf\xe0\xc0Y\xb9\xb3')
            LOG_DEBUG('\xa8\xea\xb7sAI\xc0Y\xb9\xb3\xa8q')
            self.RecordLastValidPhoto()
            for iIndex, iValue in enumerate(iAIList):
                if iValue is not None:
                    self.m_iShowPhotoList[iIndex] = iValue
                    continue
            
            self.AmendRandomData(self.m_iShowPhotoList)
            self.RefreshPhotoView(self.m_iShowPhotoList, self.GetSelectAvatarDesc())
            self.SwitchToCurPage()
            self.RequestPrice(self.m_iShowPhotoList)
            self.ClearChestSelect()
        

    
    def OnPhotoEffectChange(self):
        import hero
        iPhotoEffect = hero.GetProp('m_PhotoEffect', 0)
        LOG_DEBUG('\xafS\xae\xc4\xb3\xd1\xbel\xa4\xd1\xbc\xc6\xa7\xef\xc5\xdc', iPhotoEffect)
        if iPhotoEffect > 0:
            sTips = '\xafS\xae\xc4\xb3\xd1\xbel\xa4\xd1\xbc\xc6\xa1G%d\xa4\xd1' % iPhotoEffect / 86400
        else:
            sTips = ''
        self.GetView().SetTips(sTips)
        self.GetView().SetEffect(iPhotoEffect != 0)

    
    def OnGoldChange(self):
        import hero
        iGold = hero.GetProp('m_Gold', 0)
        self.GetView().SetGold(iGold)

    
    def OnPerStowPage(self):
        LOG_DEBUG('\xa4W\xa4@\xad\xb6')
        import usermacro
        if self.m_iCurStowPage <= 1:
            usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xa4W\xa4@\xad\xb6\xa4F')
            return None
        
        self.m_iCurStowPage -= 1
        dPhotoList = self.GetChestPhotoList(self.m_iCurStowPage)
        self.GetView().RefreshChest(dPhotoList, self.m_iCurStowPage, self.m_iMaxStowPage, self.GetChestSelectInfo())

    
    def OnNxtStowPage(self):
        LOG_DEBUG('\xa4U\xa4@\xad\xb6')
        import usermacro
        if self.m_iCurStowPage >= self.m_iMaxStowPage:
            usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xa4U\xa4@\xad\xb6\xa4F')
            return None
        
        self.m_iCurStowPage += 1
        dPhotoList = self.GetChestPhotoList(self.m_iCurStowPage)
        self.GetView().RefreshChest(dPhotoList, self.m_iCurStowPage, self.m_iMaxStowPage, self.GetChestSelectInfo())

    
    def OnSwitchPage(self, bCur):
        LOG_DEBUG('\xa4\xc1\xb4\xab\xa4\xc0\xad\xb6', bCur, self.GetView().IsInChestPage())
        self.RefreshBtnShow(self.m_iRealShowPhotoList, bCur)

    
    def OnReplaceStowCB(self, iIndex, dStowInfo):
        LOG_DEBUG('\xb4\xc0\xb4\xab\xa6\xac\xc2\xc3\xc0Y\xb9\xb3', iIndex, dStowInfo)
        self.DoReplaceStow(dStowInfo, True)

    
    def OnSelectPicture(self):
        import avataraiface
        avataraiface.AIFace()

    
    def BuyPhotoAgain(self):
        
        def Confirm(dlg):
            netplayerphoto.C2SPropPhotoContinue(dlg.m_iIndex, dlg.m_iType, dlg.m_iBuyType, iItemID = dlg.m_iItemID, iUsePal = dlg.m_iUsePal, dPalCase = dlg.m_dAvatarDesc)

        import commondialog
        import netplayerphoto
        import usermacro
        import itemdefine
        import item
        iPhotoID = self.GetPohotID(self.m_iRealShowPhotoList)
        if iPhotoID is None:
            usermacro.PROMPT_MSG('\xa7A\xc1\xd9\xa8S\xbe\xd6\xa6\xb3\xb8\xd3\xc0Y\xb9\xb3')
            return None
        
        oModel = mdavatar.GetAvatarModel()
        dAvatarDesc = self.GetSelectAvatarDesc()
        iBuyType = 1
        iPalColorNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_PAL_TICKET)
        bCanGetPal = iPalColorNum >= 1
        bUsePal = not CmpPal(dAvatarDesc, { })
        if self.m_bIsExperience:
            if bUsePal:
                if bCanGetPal:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1020)
                else:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1019)
            else:
                sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1018)
            sMsg = sMsg.replace('$day', str(self.m_iTimeLimit))
            sMsg = sMsg.replace('$price2', '200')
            sMsg = sMsg.replace('$count2', '1')
            sMsg = sMsg.replace('$count', '1')
            iType = self.m_iModel
            iItemID = self.m_iItemID
            bCanGetPal = 0
            dAvatarDesc = None
        else:
            dPrice = oModel.GetPhotoPrice()
            iNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_TICKET)
            bCanGet = iNum >= dPrice['iPoint']
            if iNum > 0:
                if bCanGet:
                    if bUsePal:
                        if bCanGetPal:
                            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1016)
                        else:
                            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1017)
                    else:
                        sMsg = '\xa5\xbb\xc0Y\xb9\xb3\xc4\xf2\xb6O\xbb\xdd\xadn#Y$count#n\xb1i\xc0Y\xb9\xb3\xa8\xe9\xa1A\xa6\xb3\xae\xc4\xb4\xc1\xac\xb090\xa4\xd1\xa1A\xa7A\xbdT\xbb{\xc4\xf2\xb6O\xb6\xdc\xa1H'
                    iBuyType = 2
                elif bUsePal:
                    if bCanGetPal:
                        sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1013)
                    else:
                        sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1014)
                else:
                    sMsg = '\xa7A\xb7\xed\xabe\xbe\xd6\xa6\xb3\xaa\xba\xc0Y\xb9\xb3\xa8\xe9\xbc\xc6\xb6q\xa4\xa3\xa8\xac, \xa5\xbb\xc0Y\xb9\xb3\xc4\xf2\xb6O\xbb\xdd\xadn#Y$price#n\xc2I\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa1A\xa6\xb3\xae\xc4\xb4\xc1\xac\xb090\xa4\xd1\xa1A\xa7A\xbdT\xbb{\xc4\xf2\xb6O\xb6\xdc\xa1H'
            elif bUsePal:
                if bCanGetPal:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1013)
                else:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1014)
            else:
                sMsg = '\xa5\xbb\xc0Y\xb9\xb3\xc4\xf2\xb6O\xbb\xdd\xadn#Y$price#n\xc2I\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa1A\xa6\xb3\xae\xc4\xb4\xc1\xac\xb090\xa4\xd1\xa1A\xa7A\xbdT\xbb{\xc4\xf2\xb6O\xb6\xdc\xa1H'
            iType = 0
            sMsg = sMsg.replace('$count2', '1')
            sMsg = sMsg.replace('$price2', '200')
            sMsg = sMsg.replace('$count', str(dPrice['iPoint']))
            sMsg = sMsg.replace('$price', str(dPrice['iGold']))
            sMsg = sMsg.replace('$day', '90')
            iItemID = 0
        dlg = commondialog.ShowMessageBox(sMsg, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (Confirm, None))
        dlg.m_iIndex = iPhotoID
        dlg.m_iType = iType
        dlg.m_iBuyType = iBuyType
        dlg.m_iItemID = iItemID
        dlg.m_iUsePal = bCanGetPal
        dlg.m_dAvatarDesc = dAvatarDesc

    
    def GetPohotID(self, iPhotoList):
        import hero
        tPhotoInfoDict = hero.GetPropPhotoArr()
        for iPhotoID, iPhotoInfoList in tPhotoInfoDict.items():
            if CmpList(iPhotoInfoList[1], iPhotoList):
                return iPhotoID
                continue
        

    
    def BuyAndReplaceAvatar(self):
        LOG_DEBUG('\xc1\xca\xb6R\xa8\xc3\xb4\xc0\xb4\xab\xb2{\xa6\xb3\xc0Y\xb9\xb3')
        iStowIdx = self.GetStowIndex()
        iPhotoList = avatar.CorrectSendAvatarList(self.m_iRealShowPhotoList)
        iStyle = iPhotoList[avatardefine.IDX_Body] / 100
        dInfo = {
            'current': iPhotoList,
            'dAvatarDesc': {
                avatar.DESC_AVATAR_HSV: self.GetSelectAvatarDesc() },
            'index2photo': self.GetIdx2PhotoID(),
            'photo2index': { },
            'stowidx': iStowIdx,
            'selstyle': iStyle,
            'selmodule': str(iPhotoList) }
        import dlgchangephoto
        dPrice = mdavatar.GetAvatarModel().GetPhotoPrice()
        bExperience = self.m_bIsExperience
        iUseDays = self.m_iTimeLimit
        iItemID = self.m_iItemID
        iModel = self.m_iModel
        dlgchangephoto.Show(dInfo, dPrice, bExperience, iUseDays, iItemID, iModel, self.OnBuyAndReplaceAvatar)

    
    def OnBuyAndReplaceAvatar(self, dInfo):
        self.BuyPhoto(dInfo['iPhotoIdx'], '\xc1\xca\xb6R\xa6\xb9\xc0Y\xb9\xb3\xb7|\xc2\xd0\xbb\\\xb7\xed\xabe\xaa\xba\xb2\xc4 #Y%d#n \xaeM\xc0Y\xb9\xb3\xa1I#r#r' % (dInfo['iIndex'] + 1))

    
    def BuyPhoto(self, iPhotoIdx, sAddText):
        LOG_DEBUG('\xc1\xca\xb6R\xc0Y\xb9\xb3')
        if self.CheckBuyChirstmas():
            return None
        
        import commondialog
        import misc
        import itemdefine
        import item
        iPhotoList = avatar.CorrectSendAvatarList(self.m_iRealShowPhotoList)
        dPrice = mdavatar.GetAvatarModel().GetPhotoPrice()
        dOrgPalCase = { }
        dDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if dDescList:
            dOrgPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        
        dAvatarDesc = self.GetSelectAvatarDesc()
        iBuyType = 1
        iPalColorNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_PAL_TICKET)
        bCanGetPal = iPalColorNum >= 1
        bUsePal = not CmpPal(dAvatarDesc, dOrgPalCase)
        if self.m_bIsExperience:
            if bUsePal:
                if bCanGetPal:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1010)
                else:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1011)
            else:
                sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1009)
            sMsg = sMsg.replace('$day', str(self.m_iTimeLimit))
            sMsg = sMsg.replace('$price2', '200')
            sMsg = sMsg.replace('$count2', '1')
            sMsg = sMsg.replace('$count', '1')
        else:
            iNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_TICKET)
            bCanGet = iNum >= dPrice['iPoint']
            if iNum > 0:
                if bCanGet:
                    if bUsePal:
                        if bCanGetPal:
                            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1005)
                        else:
                            sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1006)
                    else:
                        sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1004)
                    iBuyType = 2
                elif bUsePal:
                    if bCanGetPal:
                        sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1002)
                    else:
                        sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1003)
                else:
                    sMsg = '\xa7A\xb7\xed\xabe\xbe\xd6\xa6\xb3\xaa\xba\xc0Y\xb9\xb3\xa8\xe9\xbc\xc6\xb6q\xa4\xa3\xa8\xac\xa1A\xc1\xca\xb6R\xa6\xb9\xc0Y\xb9\xb3\xbb\xdd\xadn\xaa\xe1\xb6O#Y$price#n\xc2I\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa1A\xc1\xca\xb6R\xa6\xb3\xae\xc4\xb4\xc1\xac\xb090\xa4\xd1\xa1A\xa7A\xbdT\xbb{\xc1\xca\xb6R\xb6\xdc\xa1H'
            elif bUsePal:
                if bCanGetPal:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1002)
                else:
                    sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1003)
            else:
                sMsg = dialoguecommondata.GetDialogue('dlgavatar', 1001)
            sMsg = sMsg.replace('$count2', '1')
            sMsg = sMsg.replace('$price2', '200')
            sMsg = sMsg.replace('$count', str(dPrice['iPoint']))
            sMsg = sMsg.replace('$price', str(dPrice['iGold']))
            sMsg = sMsg.replace('$day', '90')
        sMsg = sAddText + sMsg
        sPhotoList = [ int(iEach) for iEach in iPhotoList ]
        sCopyLog = self.GetCopyLog(iPhotoList)
        oNormalBuy = misc.Functor(self.CommitNormalBuy, iPhotoList, iPhotoIdx, iPhotoList[avatardefine.IDX_Body] / 100, self.GetStowIndex(), str(sPhotoList), iBuyType, bCanGetPal, dAvatarDesc, sCopyLog)
        commondialog.ShowMessageBox(sMsg, ('\xbdT\xa9w\xc1\xca\xb6R', '\xa8\xfa\xae\xf8'), (oNormalBuy, None))

    
    def CommitNormalBuy(self, iPhotoList, iPhotoID, iStyle, iStowID, sLog, iBuyType, bCanGetPal, dAvatarDesc, sCopyLog, oDlg):
        import netplayerphoto
        if self.m_bIsExperience:
            isExp = self.m_iModel
            iItemID = self.m_iItemID
        else:
            isExp = 0
            iItemID = 0
        netplayerphoto.C2SPropPhoto(iPhotoList, iPhotoID, iStowID, iStyle, sLog, isfree = isExp, iBuyType = iBuyType, iItemID = iItemID, iUsePal = bCanGetPal, dPalCase = dAvatarDesc, sCopyLog = sCopyLog)

    
    def GetStowIndex(self):
        if not self.m_lCurSelectStowInfo:
            return 0
        
        (bStow, iPhotoID) = self.m_lCurSelectStowInfo
        if bStow:
            return iPhotoID + 1
        else:
            return 0

    
    def GetIdx2PhotoID(self):
        import hero
        dResult = { }
        tPhotoInfoDict = hero.GetPropPhotoArr()
        for iIdx, iPhotoID in enumerate(tPhotoInfoDict.keys()):
            if iPhotoID == avatardefine.DEFAULT_AVATAR_ID:
                continue
            
            dResult[iIdx] = iPhotoID
        
        return dResult

    
    def CheckBuyChirstmas(self):
        import itemdefine
        import item
        import netplayerphoto
        
        def Commit(oDlg):
            netplayerphoto.C2SPropPhoto(oDlg.m_Photoarr, oDlg.m_Index, oDlg.m_StowIndex, oDlg.m_SelectedStyle, oDlg.m_SelectModule, iModify = 0)

        (_, iVer) = avatar.GetRealBodyInfo(self.m_iRealShowPhotoList[avatardefine.IDX_Body])
        if item.HasItemsByShapes((itemdefine.ID_CHIRSTMAS_TICKET,)) and item.GetUnLockItemQuantity(itemdefine.ID_CHIRSTMAS_TICKET) and iVer in (avatardefine.STYLE_1500, avatardefine.STYLE_1600):
            iPhotoIdx = self.GetPhotoPayIdx()
            sTxt = '\xb1N\xa8\xcf\xa5\xce#Y\xb8t\xbd\xcf\xc0Y\xb9\xb3\xa7I\xb4\xab\xa8\xe9#n\xa7I\xb4\xab\xb8\xd3\xb8t\xbd\xcf\xc0Y\xb9\xb3\xa1A\xa7I\xb4\xab\xab\xe1\xa6\xb3\xae\xc4\xb4\xc1\xac\xb0#Y20\xa4\xd1#n\xa1A\xa7A\xbdT\xbb{\xa7I\xb4\xab\xb6\xdc\xa1H'
            import commondialog
            dlg = commondialog.ShowMessageBox(sTxt, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (Commit, None))
            dlg.m_Photoarr = avatar.CorrectSendAvatarList(self.m_iRealShowPhotoList)
            dlg.m_Index = iPhotoIdx
            dlg.m_SelectedStyle = dlg.m_Photoarr[avatardefine.IDX_Body] / 100
            dlg.m_SelectModule = str(dlg.m_Photoarr)
            dlg.m_StowIndex = self.GetStowIndex()
            return True
        
        return False

    
    def GetPhotoPayIdx(self):
        import hero
        tPhotoInfoDict = hero.GetPropPhotoArr()
        for iIdx, iPhotoID in enumerate(sorted(tPhotoInfoDict.keys())):
            tPhotoInfoList = tPhotoInfoDict[iPhotoID]
            if iPhotoID == avatardefine.DEFAULT_AVATAR_ID:
                continue
            
            if not self.CheckPhotoCanBuy(tPhotoInfoList[1]) and tPhotoInfoList[0] == 0:
                return iPhotoID
            
            if iIdx != iPhotoID:
                return iIdx
                continue
        
        return len(tPhotoInfoDict) - 1

    
    def DoReplaceStow(self, dStowInfo, bStow):
        lStowList = []
        for iKey in sorted(dStowInfo.keys()):
            dInfo = dStowInfo[iKey]
            tmp = dInfo['iPhotoIntList'][:]
            if tmp[avatardefine.IDX_Body] >= 100:
                tmp[avatardefine.IDX_Body] /= 100
            
            dAvatarDesc = {
                'dPalCase': dInfo['dPalCase'] }
            lStowList.append((avatar.PhotoArr2Int(tmp), dAvatarDesc))
        
        mdavatar.GetAvatarModel().SetStowIntList(lStowList)
        import usermacro
        if bStow:
            usermacro.PROMPT_MSG('\xc0Y\xb9\xb3\xa6\xac\xc2\xc3\xa6\xa8\xa5\\')
        

    
    def ProcressPhotoList(self, iPhotoList):
        if iPhotoList == avatardefine.XUAN_MEI_FLAG:
            return avatar.Int2PhotoArr(*avatardefine.STYLE_XUAN_MEI)
        else:
            return iPhotoList[:]

    
    def GetHeroPhotoIntList(self):
        import hero
        tPhotoInfoDict = hero.GetPropPhotoArr()
        tCurIntList = []
        if tPhotoInfoDict == avatardefine.XUAN_MEI_FLAG:
            dInfo = { }
            dInfo[avatardefine.KEY_PHOTO_ID] = 255
            dInfo[avatardefine.KEY_LEFT_TIME] = 255
            dInfo[avatardefine.KEY_PHOTO_INT_LIST] = avatar.PhotoArr2Int(avatar.GetDefaultPhoto())
            dInfo[avatardefine.KEY_PHOTO_IN_USE] = False
            dInfo[avatardefine.KEY_IS_STOW] = False
            dInfo[avatardefine.KEY_IS_DEFAULT] = True
            dInfo[avatardefine.KEY_PHOTO_PAL] = { }
            tCurIntList.append(dInfo)
        else:
            for iPhotoID, tInfo in tPhotoInfoDict.items():
                (iTime, iPhotoList, dAvartDesc) = tInfo
                bIsDeafult = avatar.IsDefaultPhoto(iPhotoList)
                if not self.CheckPhotoCanBuy(iPhotoList) and not bIsDeafult and self.GetPhotoLeftTime(iPhotoList) == 0:
                    continue
                
                if CmpList(avatar.PhotoArr2Int(iPhotoList), [
                    0,
                    0,
                    0,
                    0]):
                    continue
                
                dInfo = { }
                dInfo[avatardefine.KEY_PHOTO_ID] = iPhotoID
                dInfo[avatardefine.KEY_LEFT_TIME] = iTime
                dInfo[avatardefine.KEY_PHOTO_INT_LIST] = avatar.PhotoArr2Int(iPhotoList)
                dInfo[avatardefine.KEY_PHOTO_IN_USE] = CmpList(iPhotoList, avatar.GetHeroPhoto())
                dInfo[avatardefine.KEY_IS_STOW] = False
                dInfo[avatardefine.KEY_IS_DEFAULT] = bIsDeafult
                dInfo[avatardefine.KEY_PHOTO_PAL] = dAvartDesc
                tCurIntList.append(dInfo)
            
        return tCurIntList

    
    def ProcressStowList(self, lStowIntList):
        lResult = []
        for iPhotoIntList, dPhotoDesc in enumerate(lStowIntList):
            if CmpList(iPhotoIntList, [
                0,
                0,
                0,
                0]):
                continue
            
            if not self.CheckPhotoCanBuy(avatar.Int2PhotoArr(*iPhotoIntList)):
                continue
            
            dInfo = { }
            dInfo[avatardefine.KEY_PHOTO_ID] = iIdx
            dInfo[avatardefine.KEY_LEFT_TIME] = None
            dInfo[avatardefine.KEY_PHOTO_INT_LIST] = iPhotoIntList[:]
            dInfo[avatardefine.KEY_PHOTO_IN_USE] = False
            dInfo[avatardefine.KEY_IS_STOW] = True
            dInfo[avatardefine.KEY_IS_DEFAULT] = False
            dInfo[avatardefine.KEY_PHOTO_PAL] = dPhotoDesc
            lResult.append(dInfo)
        
        return lResult

    
    def IsOpenSpecial(self, iBody):
        oModel = mdavatar.GetAvatarModel()
        if iBody in avatardefine.CHILDREN_LIST and oModel.GetOpenChildren():
            return True
        elif iBody in avatardefine.CHRISTMAS_LIST and oModel.GetOpenChristmas():
            return True
        
        return False

    
    def IsSpecial(self, iBody):
        if iBody in avatardefine.CHILDREN_LIST or iBody in avatardefine.CHRISTMAS_LIST:
            return True
        
        return False

    
    def RefreshImitateAvatar(self, iPhotoList, dPhotoDesc):
        (iBody, _) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        if self.IsSpecial(iBody):
            if not self.IsOpenSpecial(iBody):
                usermacro.PROMPT_MSG('\xb8\xd3\xc0Y\xb9\xb3\xac\xb0\xad\xad\xa9w\xc0Y\xb9\xb3\xa1A\xb5L\xaak\xbc\xd2\xa5\xe9')
                return None
            
        
        iBody /= 100
        iHeroSex = hero.GetProp('m_Sex')
        iOtherSex = iBody % 2
        if iOtherSex == 0:
            iOtherSex = 2
        
        if iOtherSex != iHeroSex:
            usermacro.PROMPT_MSG('\xa4w\xac\xb0\xb1z\xa4\xc7\xb0t\xbbP\xb8\xd3\xb2\xa7\xa9\xca\xc0Y\xb9\xb3\xac\xdb\xa6P\xad\xb7\xae\xe6\xaa\xba\xc0Y\xb9\xb3')
            if iHeroSex == 1:
                iBody -= 1
            else:
                iBody += 1
            iPhotoList = self.ChangeDifferentSexImitate(iPhotoList, iBody)
        
        iPhotoList[avatardefine.IDX_Body] = iBody * 100
        mdavatar.GetAvatarModel().SetLogData(iPhotoList, iOtherSex, iBody)
        iPhotoList[avatardefine.IDX_Body] = iBody
        self.m_iShowPhotoList = self.ProcressPhotoList(iPhotoList)
        self.m_iPerValidPhotoList = self.ProcressPhotoList(iPhotoList)
        self.RefreshPhotoView(iPhotoList, dPhotoDesc)
        self.RefreshAvatarItemList(iPhotoList, avatardefine.IDX_Hair)
        self.GetView().RefreshSpecialPartUI(self.m_iCurVer, self.m_iCurPart)
        self.ResetColorBtn()
        self.m_dPalCase = avatardefine.COPY_DEFAULT_COLOR
        self.GetView().SetPhotoPalCase(avatardefine.COPY_DEFAULT_COLOR)
        self.SetColorBlockWithDesc({
            avatar.DESC_AVATAR_HSV: dPhotoDesc })
        self.GetView().SetPhotoPalCase(dPhotoDesc)
        self.UpdateHsvColorBlockShow()
        self.UpdateSlider()
        self.UpdateHsvCount()
        self.RefreshBugBtn(iPhotoList)
        self.SwitchColor(dPhotoDesc)

    
    def GetCopyLog(self, iNowPhotoList):
        import hero
        oModel = mdavatar.GetAvatarModel()
        if not oModel.GetIsCopy():
            return ''
        
        iChange = None if oModel.GetCopyPhotoList() != iNowPhotoList else 0
        return avatardefine.COPT_AVATAR_LOG % (hero.GetProp('m_Sex', 1), oModel.GetCopySex(), oModel.GetCopyStyle(), iChange)

    
    def ResetColorBtn(self):
        oView = self.GetView()
        for _, sBtnName in avatardefine.IDX_2_BTNNAME.iteritems():
            oView.SetBtnSelect(sBtnName, False)
        
        oView.SetBtnSelect('999', False)

    
    def SwitchColor(self, dPhotoDest):
        oView = self.GetView()
        for iIdx, _ in dPhotoDest.iteritems():
            if iIdx not in avatardefine.IDX_2_BTNNAME:
                continue
            
            sBtnName = avatardefine.IDX_2_BTNNAME[iIdx]
            oView.SetBtnSelect(sBtnName, False)
            oView.SwitchPalColor(sBtnName)
            if iIdx == avatardefine.IDX_Hair:
                oView.SetBtnSelect('999', False)
                continue
        

    
    def ChangeDifferentSexImitate(self, iPhotoList, iChangeBody):
        (iBody, _) = avatar.GetRealBodyInfo(iChangeBody)
        iDefaultList = misc.DeepCopy(avatardefine.STYLE_2_DEFAULT[iBody])
        iDefaultList[avatardefine.IDX_BG] = avatarcode.GetBeiJing(iBody, iPhotoList[avatardefine.IDX_BG])
        iDefaultList[avatardefine.IDX_Decoration2] = avatarcode.GetBianKuang(iBody, iPhotoList[avatardefine.IDX_Decoration2])
        return iDefaultList

    
    def RefreshPhotoView(self, iPhotoList, dPhotoDesc = None):
        oView = self.GetView()
        LOG_DEBUG('\xc5\xe3\xa5\xdc\xc0Y\xb9\xb3', iPhotoList, dPhotoDesc)
        self.m_iRealShowPhotoList = []
        for iValue in iPhotoList:
            if iValue is None:
                self.m_iRealShowPhotoList.append(0)
                continue
            self.m_iRealShowPhotoList.append(iValue)
        
        oView.SetPhoto(iPhotoList, dPhotoDesc)
        oView.EnableChangeBtn(not self.IsSpecialAvatar(iPhotoList))
        self.RefreshLeftTime(iPhotoList, dPhotoDesc)
        self.RefreshBugBtn(iPhotoList)
        self.RefreshStowBtn(iPhotoList, dPhotoDesc)
        self.RefreshUseBtn(iPhotoList, dPhotoDesc)
        self.RefreshBtnShow(iPhotoList, dPhotoDesc = dPhotoDesc)

    
    def GetHeroPalData(self):
        import hero
        import avatarpaldatamgr
        dPalCase = avatarpaldatamgr.GetAvatarFrmDataMgr().GetPalId(hero.GetRealID())
        return dPalCase

    
    def GetSelectAvatarDesc(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xb7\xed\xabe\xabO\xa6s\xaa\xba\xacV\xa6\xe2\xabH\xae\xa7
\t\t\xa6p\xaaG\xb3o\xa4@\xaeM\xa4\xe8\xae\xd7\xacO\xa4w\xb8g\xa6s\xa6b\xa8\xc3\xa5B\xa8S\xb9L\xb4\xc1\xaa\xba\xa1A\xa8\xba\xbb\xf2\xb4N\xc1\xd9\xad\xec\xa6\xa8\xc0q\xbb{\xacV\xa6\xe2
\t\t'''
        dPalCase = { }
        dDescList = self.GetPhotoAvatarDesc(self.m_iShowPhotoList)
        if dDescList:
            dPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        
        for iPart, iColor in self.m_dAvatarPalCase.get(self.m_iCurVer, { }).iteritems():
            if iPart not in self.m_iCurPalVerList:
                continue
            
            lTmp = [
                iPart]
            if iPart == avatardefine.IDX_Hair:
                lTmp.append(avatardefine.IDX_HairPath)
            elif iPart == avatardefine.IDX_Clothes and self.m_iCurVer in (avatardefine.STYLE_2500, avatardefine.STYLE_2600):
                lTmp.append(avatardefine.IDX_Headwear)
            
            for iEach in lTmp:
                dPalCase[iEach] = iColor
            
        
        return dPalCase

    
    def OnHueSlider(self, iPos):
        '''
\t\t\xb6i\xab\xd7\xb1\xf8\xb5o\xa5\xcd\xa7\xef\xaa\xed\xa6^\xbd\xd5
\t\t'''
        oView = self.GetView()
        bSelect = oView.GetObject('btn_select').GetSelect()
        if self.m_bFirstSlider and bSelect:
            usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('dlgavatar', 2001))
            self.m_bFirstSlider = False
        
        dDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if dDescList:
            dPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        else:
            dPalCase = { }
        self.SelectToColorBlock(dPalCase.get(self.m_iCurPart, 0) != iPos, self.m_iCurPart)
        self.SetCurHsvInfo(self.m_iCurPart, iPos)
        self.RefreshStowBtn(self.m_iRealShowPhotoList, self.GetSelectAvatarDesc())
        self.SwitchToCurPage()
        self.ClearChestSelect()
        self.UpdateViewHsvShow()

    
    def SetCurHsvInfo(self, iPart, iPos):
        if self.m_iCurVer not in self.m_dAvatarPalCase:
            self.m_dAvatarPalCase[self.m_iCurVer] = { }
        
        if iPart not in self.m_dAvatarPalCase[self.m_iCurVer]:
            self.m_dAvatarPalCase[self.m_iCurVer][iPart] = { }
        
        self.m_dAvatarPalCase[self.m_iCurVer][iPart] = iPos

    
    def OnResetPalChange(self):
        '''
\t\t\xa6p\xaaG\xc0Y\xb9\xb3\xa4w\xb8g\xbe\xd6\xa6\xb3\xa1A\xa7\xe2\xb7\xed\xabe\xb3\xa1\xa6\xec\xb3]\xb8m\xa6\xa8\xc0q\xbb{\xaa\xba\xacV\xa6\xe2\xa1A\xa7_\xabh\xb8m\xa6\xa80
\t\t'''
        iLeftTime = self.GetPhotoLeftTime(self.m_iRealShowPhotoList)
        dPalCase = { }
        dDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if dDescList:
            dPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        
        self.SetCurHsvInfo(self.m_iCurPart, dPalCase.get(self.m_iCurPart, 0))
        self.SelectToColorBlock(False, self.m_iCurPart)
        self.SwitchToCurPage()
        self.ClearChestSelect()
        self.UpdateViewHsvShow()

    
    def OnClickPalBtn(self, iPart, bShow):
        '''
\t\t\xac\xc9\xad\xb1\xa6^\xbd\xd5\xc2I\xc0\xbb\xacV\xa6\xe2\xab\xf6\xb6s
\t\t'''
        dDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if dDescList:
            dPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        else:
            dPalCase = { }
        if iPart == '999':
            iNowPart = self.m_iCurPart
        else:
            iNowPart = iPart
        iNowInfo = dPalCase.get(iNowPart, 0)
        iSelectVal = self.m_dAvatarPalCase.get(self.m_iCurVer, { }).get(iNowPart, 0)
        if iNowInfo == iSelectVal:
            usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('dlgavatar', 2004))
            return None
        
        if iPart == avatardefine.PALBTN_IDX_DICT['btn_select']:
            self.SelectToColorBlock(bShow, self.m_iCurPart)
        else:
            self.SelectToColorBlock(bShow, iPart)
        self.SwitchToCurPage()
        self.ClearChestSelect()
        self.UpdateViewHsvShow()

    
    def SelectToColorBlock(self, bShow, iPart):
        '''
\t\t\xb3]\xb8m\xadn\xa5\xcd\xae\xc4\xaa\xba\xc3C\xa6\xe2\xb2\xd5\xa5\xf3
\t\t'''
        for sKey, sValue in avatardefine.PALBTN_IDX_DICT.items():
            if iPart == sValue:
                if bShow:
                    self.m_iCurPalVerList.add(sValue)
                elif sValue in self.m_iCurPalVerList:
                    self.m_iCurPalVerList.remove(sValue)
                
            bShow
        

    
    def SelectToColorBlockWithDesc(self, dAvatarDesc):
        '''
\t\t\xae\xda\xbe\xdaDesc\xaa\xed\xb2{\xa8\xd3\xa7\xf3\xb7s\xab\xf6\xb6s\xbf\xef\xa4\xa4
\t\t'''
        dPalCase = { }
        dDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if dDescList:
            dPalCase = misc.DeepCopy(dDescList[0][avatar.DESC_AVATAR_HSV])
        
        dAvatarHsv = dAvatarDesc.get(avatar.DESC_AVATAR_HSV, { })
        for iPart in (avatardefine.IDX_Hair, avatardefine.IDX_Face2, avatardefine.IDX_Clothes):
            self.SelectToColorBlock(dAvatarHsv.get(iPart, 0) != dPalCase.get(iPart, 0), iPart)
        

    
    def ClearColorBlock(self):
        self.m_iCurPalVerList = set()

    
    def SetColorBlockWithDesc(self, dAvatarDesc):
        '''
\t\t\xae\xda\xbe\xdaDesc\xaa\xed\xb2{\xa8\xd3\xa7\xf3\xb7s\xbc\xc6\xbe\xda
\t\t'''
        dAvatarHsv = dAvatarDesc.get(avatar.DESC_AVATAR_HSV, { })
        for iPart in (avatardefine.IDX_Hair, avatardefine.IDX_Face2, avatardefine.IDX_Clothes):
            if iPart in dAvatarHsv:
                self.SetCurHsvInfo(iPart, dAvatarHsv[iPart])
                continue
        

    
    def UpdateHsvCount(self):
        iNum = item.GetItemNumNoLock(itemdefine.ID_AVATAR_PAL_TICKET)
        iNeed = 1
        if self.m_iCurPalVerList:
            if iNum < iNeed:
                sText = '#R%s#n/%s'
            else:
                sText = '%s/%s'
            sText %= (iNum, iNeed)
        else:
            sText = '%s/%s' % (iNum, 0)
        self.GetView().SetTicketNumText(sText)
        self.GetView().SetTicketNumShow(bool(self.m_iCurPalVerList))

    
    def UpdateViewHsvShow(self):
        '''
\t\t\xa7\xf3\xb7s\xacV\xa6\xe2\xaa\xba\xc1`\xb1\xb1\xa8\xe7\xbc\xc6
\t\t:return:
\t\t'''
        self.UpdateHsvColorBlockShow()
        self.UpdateSlider()
        self.RefreshAvatarPal()
        self.UpdateHsvCount()

    
    def UpdateHsvColorBlockShow(self):
        '''
\t\t\xae\xda\xbe\xda\xbc\xc6\xad\xc8\xa8\xd3\xa8\xea\xb7s\xac\xc9\xad\xb1\xaa\xed\xb2{
\t\t'''
        oView = self.GetView()
        if self.m_iCurVer in (avatardefine.STYLE_2900, avatardefine.STYLE_3000):
            oView.SetShowIdolType(True)
            for sKey, sValue in avatardefine.PALBTN_IDX_DICT.iteritems():
                if sValue == '999':
                    continue
                
                bShow = sValue in self.m_iCurPalVerList
                oBtn = oView.GetObject(sKey)
                if oBtn:
                    pass
                oBtn.SetSelect(bShow)
                if self.m_iCurPart == sValue:
                    oView.SelectCal(bShow)
                    continue
            
            oView.ShowPalImg(self.m_iCurPart in (avatardefine.IDX_Hair, avatardefine.IDX_Face2, avatardefine.IDX_Clothes))
        else:
            oView.SetShowIdolType(False)

    
    def UpdateSlider(self):
        '''
\t\t\xae\xda\xbe\xda\xbc\xc6\xad\xc8\xa8\xd3\xa8\xea\xb7s\xb7\xc6\xb0\xca\xb1\xf8\xaa\xba\xa6\xec\xb8m
\t\t'''
        iVal = self.m_dAvatarPalCase.get(self.m_iCurVer, { }).get(self.m_iCurPart, 0)
        self.GetView().SetHuePos(iVal)

    
    def RefreshAvatarPal(self):
        '''
\t\t\xae\xda\xbe\xda\xbc\xc6\xad\xc8\xa7\xf3\xb7s\xc0Y\xb9\xb3\xa8q\xacV\xa6\xe2\xbc\xc6\xbe\xda
\t\t'''
        if self.m_iCurPart is None:
            return None
        
        dPalCase = self.GetSelectAvatarDesc()
        self.m_dPalCase = dPalCase
        self.GetView().SetPhotoPalCase(dPalCase)
        self.RefreshBugBtn(self.m_iShowPhotoList)

    
    def GetValidHeroPhotoNum(self):
        import hero
        tPhotoInfoDict = hero.GetPropPhotoArr()
        iNum = 0
        for iPhotoID, iPhotoInfoList in tPhotoInfoDict.items():
            if avatar.IsDefaultPhoto(iPhotoInfoList[1]):
                iNum += 1
                continue
            if self.CheckPhotoCanBuy(iPhotoInfoList[1]):
                iNum += 1
                continue
            if self.IsHasAvatar(iPhotoInfoList[1]):
                iNum += 1
                continue
        
        return iNum

    
    def IsHasAvatar(self, iPhotoList):
        iLeftTime = self.GetPhotoLeftTime(iPhotoList)
        return iLeftTime

    
    def IsHasStowAvatar(self, iPhotoList, dNowDesc):
        lStowIntList = mdavatar.GetAvatarModel().GetStowIntList()
        bIn = False
        for iStowIntList, dPhotoDesc in lStowIntList:
            iCurIntList = avatar.PhotoArr2Int(iPhotoList)
            if iStowIntList[0] == iCurIntList[0] and iStowIntList[1] == iCurIntList[1] and iStowIntList[2] == iCurIntList[2] and iStowIntList[3] == iCurIntList[3] and dNowDesc == dPhotoDesc:
                bIn = True
                break
                continue
        
        return bIn

    
    def IsAvatarInUse(self, iPhotoList):
        (p1, p2, p3, p4) = avatar.PhotoArr2Int(iPhotoList)
        (xp1, xp2, xp3, xp4) = avatar.PhotoArr2Int(self.m_iUsePhotoList)
        if p1 == xp1 and p2 == xp2 and p3 == xp3:
            pass
        bIsUse = p4 == xp4
        return bIsUse

    
    def RefreshLeftTime(self, iPhotoList, dPhotoDesc):
        oView = self.GetView()
        iLeftTime = self.GetPhotoLeftTime(iPhotoList)
        if iLeftTime is None:
            sTime = '\xa5\xbc\xbe\xd6\xa6\xb3'
        elif iLeftTime == 0:
            sTime = '\xa4w\xb9L\xb4\xc1'
        elif iLeftTime == 255:
            sTime = '\xa5\xc3\xa4['
        else:
            sTime = '%d\xa4\xd1' % iLeftTime
        
        try:
            pass
        except:
            None(sTime)
            return None


    
    def GetPhotoLeftTime(self, iPhotoList):
        '''
\t\t\xc0\xf2\xa8\xfa\xb3\xd1\xbel\xae\xc9\xb6\xa1
\t\t'''
        tPhotoInfoList = hero.GetPropPhotoArr()
        if tPhotoInfoList == avatardefine.XUAN_MEI_FLAG:
            return 1
        else:
            iLastTime = None
            for iPhotoID, tPhotoInfo in tPhotoInfoList.items():
                if CmpList(iPhotoList, tPhotoInfo[1]):
                    if iLastTime is None:
                        iLastTime = tPhotoInfo[0]
                    else:
                        iLastTime = max(iLastTime, tPhotoInfo[0])
                iLastTime is None
            
            return iLastTime

    
    def GetHavePhotoInfo(self, iPhotoList):
        '''
\t\t\xc0\xf2\xa8\xfa\xa4w\xa6s\xa6b\xaa\xba\xc0Y\xb9\xb3\xbc\xc6\xbe\xda
\t\t'''
        tPhotoInfoList = hero.GetPropPhotoArr()
        if tPhotoInfoList == avatardefine.XUAN_MEI_FLAG:
            return None
        else:
            for iPhotoID, tPhotoInfo in tPhotoInfoList.items():
                if CmpList(iPhotoList, tPhotoInfo[1]):
                    return (iPhotoID, tPhotoInfo)
                    continue
            
            return None

    
    def GetPhotoAvatarDesc(self, iPhotoList):
        '''
\t\t\xc0\xf2\xa8\xfaDesc\xbc\xc6\xbe\xda\xa1A\xa7\xe4\xa8\xec\xa9\xd2\xa6\xb3\xa4w\xb8g\xa6s\xa6b\xaa\xba\xacV\xa6\xe2\xbc\xc6\xbe\xda
\t\t'''
        tPhotoInfoList = hero.GetPropPhotoArr()
        if tPhotoInfoList == avatardefine.XUAN_MEI_FLAG:
            return []
        else:
            dAvatarDescList = []
            for iPhotoID, tPhotoInfo in tPhotoInfoList.items():
                if CmpList(iPhotoList, tPhotoInfo[1]):
                    dAvatarDescList.append(tPhotoInfo[2])
                    continue
            
            return dAvatarDescList

    
    def RefreshBugBtn(self, iPhotoList):
        bHas = self.IsHasAvatar(iPhotoList)
        bCanBuy = self.CheckPhotoCanBuy(iPhotoList)
        if not bHas and bCanBuy:
            self.GetView().EnableBuyBtn(True)
        elif not CmpPal(self.m_dPalCase, self.GetHeroPalData()):
            self.GetView().EnableBuyBtn(True)
        else:
            self.GetView().EnableBuyBtn(False)

    
    def RefreshStowBtn(self, iPhotoList, dPhotoDesc):
        bHasStow = self.IsHasStowAvatar(iPhotoList, dPhotoDesc)
        bIsSpecial = self.IsSpecialAvatar(iPhotoList)
        bIsChilderen = self.IsChildrenAvatar(iPhotoList)
        bIsChristmas = self.IsChristmasAvatar(iPhotoList)
        if not bHasStow and bIsSpecial and bIsChilderen:
            pass
        bFlag = not bIsChristmas
        self.GetView().EnableStowBtn(bFlag)

    
    def RefreshUseBtn(self, iPhotoList, dPhotoDesc):
        self.GetView().EnableUseBtn(not self.IsAvatarInUse(iPhotoList))

    
    def RefreshBtnShow(self, iPhotoList, bCur = None, dPhotoDesc = None):
        oView = self.GetView()
        iLeftTime = self.GetPhotoLeftTime(self.m_iRealShowPhotoList)
        dSelectDescList = self.GetPhotoAvatarDesc(self.m_iRealShowPhotoList)
        if not dSelectDescList:
            dSelectDesc = { }
        else:
            dSelectDesc = dSelectDescList[0]
        if CmpDesc(dSelectDesc, dPhotoDesc):
            pass
        bHave = iLeftTime > 0
        LOG_DEBUG('\xb3\xd1\xbel\xae\xc9\xb6\xa1>', iLeftTime)
        if bCur is None:
            bCur = not oView.IsInChestPage()
        
        if bCur:
            oView.SetBuyAndStow()
        elif bHave:
            oView.SetUseAndDelStow()
        else:
            oView.SetBuyAndDelStow()
        import timer
        timer.Timer(0, self.OnRenderStateChangeForChild, 0)

    
    def GetChestPhotoList(self, iPage):
        return self.m_dAllPhotoList

    
    def InitAllPhotoList(self):
        oModel = mdavatar.GetAvatarModel()
        dStowIntList = self.ProcressStowList(oModel.GetStowIntList())
        dCurIntList = self.GetHeroPhotoIntList()
        dResultList = []
        dResultList.extend(dCurIntList)
        dResultList.extend(dStowIntList)
        self.m_dAllPhotoList = self.SortChestPhotoList(dResultList)

    
    def ResetChestShow(self):
        self.InitAllPhotoList()
        self.RefreshMaxPage()
        self.m_iCurStowPage = 1
        dPhotoList = self.GetChestPhotoList(self.m_iCurStowPage)
        self.GetView().RefreshChest(dPhotoList, self.m_iCurStowPage, self.m_iMaxStowPage, self.GetChestSelectInfo())

    
    def RefreshMaxPage(self):
        import math
        iSize = len(self.m_dAllPhotoList)
        iPageNum = self.GetView().STOW_PAGE_NUM
        self.m_iMaxStowPage = int(math.ceil(float(iSize) / iPageNum))

    
    def GetChestSelectInfo(self):
        import hero
        if self.m_lCurSelectStowInfo is None:
            return None
        else:
            (bStow, iPhotoID) = self.m_lCurSelectStowInfo
            if bStow:
                for iIdx, tPhotoIntList in enumerate(mdavatar.GetAvatarModel().GetStowIntList()):
                    if iIdx == iPhotoID:
                        return (bStow, tPhotoIntList)
                        continue
                
            else:
                for iID, tPhotoInfo in hero.GetPropPhotoArr().items():
                    if iID == iPhotoID:
                        return (bStow, (avatar.PhotoArr2Int(tPhotoInfo[1]), { }))
                        continue
                

    
    def ClearChestSelect(self):
        self.m_lCurSelectStowInfo = None
        self.GetView().ClearStowSelect()

    
    def IsSpecialAvatar(self, iPhotoList):
        if not self.IsXuanmeiAvatar(iPhotoList) and self.IsDefautlAvatar(iPhotoList):
            pass
        return self.IsOtherAvatar(iPhotoList)

    
    def IsXuanmeiAvatar(self, iPhotoList):
        (p1, p2, p3, p4) = avatar.PhotoArr2Int(iPhotoList)
        (xp1, xp2, xp3, xp4) = avatardefine.STYLE_XUAN_MEI
        if p1 == xp1 and p2 == xp2 and p3 == xp3:
            pass
        return p4 == xp4

    
    def IsDefautlAvatar(self, iPhotoList):
        (p1, p2, p3, p4) = avatar.PhotoArr2Int(iPhotoList)
        (xp1, xp2, xp3, xp4) = avatar.PhotoArr2Int(avatar.GetDefaultPhoto())
        if p1 == xp1 and p2 == xp2 and p3 == xp3:
            pass
        return p4 == xp4

    
    def IsOtherAvatar(self, iPhotoList):
        (p1, p2, p3, p4) = avatar.PhotoArr2Int(iPhotoList)
        if p1 == 232644061 and p2 == 232644061:
            pass
        return p3 & 268435200 == 250539520

    
    def IsChildrenAvatar(self, iPhotoList):
        (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        return iVer in (avatardefine.STYLE_1300, avatardefine.STYLE_1400)

    
    def IsChristmasAvatar(self, iPhotoList):
        (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        return iVer in (avatardefine.STYLE_1500, avatardefine.STYLE_1600)

    
    def IsCanOps(self):
        import misc
        import usermacro
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xa4\xa3\xa4\xb9\xb3\\\xc0Y\xb9\xb3\xac\xdb\xc3\xf6\xbe\xde\xa7@')
            return False
        
        return True

    
    def SwitchToCurPage(self):
        oView = self.GetView()
        if oView.IsInChestPage():
            oView.ShowCurPage()
            self.RefreshBtnShow(self.m_iRealShowPhotoList)
        

    
    def CheckPhotoCanBuy(self, iPhotoList):
        (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
        return iVer in avatardefine.CAN_BUY_STALE_LIST

    
    def RecordLastValidPhoto(self):
        import usermacro
        if not self.CheckPhotoCanBuy(self.m_iShowPhotoList):
            if not avatar.IsDefaultPhoto(self.m_iShowPhotoList):
                usermacro.PROMPT_MSG('\xb8\xd3\xc0Y\xb9\xb3\xad\xb7\xae\xe6\xa4w\xa4U\xac[\xa1A\xa6\xb3\xae\xc4\xb4\xc1\xa4\xba\xa4\xb4\xa5i\xc4~\xc4\xf2\xa8\xcf\xa5\xce\xa1C')
            
            self.m_iShowPhotoList = self.ProcressPhotoList(self.m_iPerValidPhotoList)
        else:
            self.m_iPerValidPhotoList = self.ProcressPhotoList(self.m_iShowPhotoList)

    
    def SortChestPhotoList(self, dPhotoInfoList):
        dResultList = []
        dDefaultPhotoInfo = None
        dUsingPhotoInfo = None
        dBuyPhotoList = []
        dStowPhotoList = []
        for dPhotoInfo in dPhotoInfoList:
            if dPhotoInfo[avatardefine.KEY_IS_DEFAULT]:
                if dPhotoInfo[avatardefine.KEY_PHOTO_IN_USE]:
                    dUsingPhotoInfo = dPhotoInfo
                else:
                    dDefaultPhotoInfo = dPhotoInfo
            dPhotoInfo[avatardefine.KEY_PHOTO_IN_USE]
            if dPhotoInfo[avatardefine.KEY_PHOTO_IN_USE]:
                dUsingPhotoInfo = dPhotoInfo
                continue
            if dPhotoInfo[avatardefine.KEY_IS_STOW]:
                dStowPhotoList.append(dPhotoInfo)
                continue
            dBuyPhotoList.append(dPhotoInfo)
        
        dBuyPhotoList.sort(key = (lambda dInfo: dInfo[avatardefine.KEY_LEFT_TIME]), reverse = True)
        dStowPhotoList.sort(key = (lambda dInfo: dInfo[avatardefine.KEY_LEFT_TIME]), reverse = True)
        if dUsingPhotoInfo:
            pass
        dResultList.append(dUsingPhotoInfo)
        dResultList.extend(dBuyPhotoList)
        dResultList.extend(dStowPhotoList)
        if dDefaultPhotoInfo:
            pass
        dResultList.append(dDefaultPhotoInfo)
        return dResultList

    
    def UpdateBagChangeRecommend(self, *args):
        self.UpdateHsvCount()



def CmpList(oList1, oList2):
    if not oList1 or not oList2:
        return False
    
    if len(oList1) != len(oList2):
        return False
    
    for iIdx, oValue1 in enumerate(oList1):
        if oValue1 != oList2[iIdx]:
            return False
            continue
    
    return True


def CmpDesc(dDesc1, dDesc2):
    if dDesc1 == dDesc2:
        return True
    
    if not dDesc1:
        dDesc1 = { }
    
    if not dDesc2:
        dDesc2 = { }
    
    return CmpPal(dDesc1.get(avatar.DESC_AVATAR_HSV, { }), dDesc2.get(avatar.DESC_AVATAR_HSV, { }))


def CmpPal(dPal1, dPal2):
    if dPal1 == dPal2:
        return True
    
    if not dPal1:
        dPal1 = { }
    
    if not dPal2:
        dPal2 = { }
    
    for iPart in (avatardefine.IDX_Hair, avatardefine.IDX_Face2, avatardefine.IDX_Clothes):
        if dPal1.get(iPart, 0) != dPal2.get(iPart, 0):
            return False
            continue
    
    return True


def GetPrice(iPhotoList):
    import hero
    iIsMale = hero.GetProp('m_Sex', 1)
    (_, iVer) = avatar.GetRealBodyInfo(iPhotoList[avatardefine.IDX_Body])
    if iVer in (avatardefine.STYLE_500, avatardefine.STYLE_600, avatardefine.STYLE_700, avatardefine.STYLE_800, avatardefine.STYLE_900, avatardefine.STYLE_1000, avatardefine.STYLE_1100, avatardefine.STYLE_1200, avatardefine.STYLE_1300, avatardefine.STYLE_1400, avatardefine.STYLE_1500, avatardefine.STYLE_1600):
        iGold = 300
        iPoint = 2
    elif iVer in (avatardefine.STYLE_1900, avatardefine.STYLE_2000):
        iGold = 450
        iPoint = 3
    elif iVer in (avatardefine.STYLE_2100, avatardefine.STYLE_2200):
        iGold = 600
        iPoint = 4
    else:
        iGold = 300
        iPoint = 2
    if iIsMale == 2:
        iGold = iGold * 4 / 5
    
    LOG_DEBUG('>>iGold, iPoint>', iGold, iPoint)
    return (iGold, iPoint)
