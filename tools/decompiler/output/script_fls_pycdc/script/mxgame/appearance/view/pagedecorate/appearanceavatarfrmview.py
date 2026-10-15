# pycdc 交叉复核产物 · script.fls entry 3714
# co_filename(原始)='script/mxgame/appearance/view/pagedecorate/appearanceavatarfrmview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3714.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: jiangweichao
\tappearanceavatarfrmview\xa3\xba\xd1\xd5\xd6\xb5\xb9\xdd - \xcd\xb7\xcf\xf1\xbf\xf2\xbd\xe7\xc3\xe6
================================================================================
'''
import appearancepagebase
import avatar
import chatbubbledata
import combdialog
import delegateappearanceavatarfrm
import interface
import newappearancecontext
import permission
import slot
import ui
import drawedge
import wrapinterface

def ShowAvatarFrmDlg(iSelectItem = 0):
    import appearancedefine
    newappearancecontext.Get().OpenAppDlg(appearancedefine.MAIN_PAGE_DECORATE, dExtendData = {
        'page': appearancedefine.SUB_PAGE_FRAME,
        'extend': {
            'select': iSelectItem } })


def ShowBubbleDlg():
    import appearancedefine
    newappearancecontext.Get().OpenAppDlg(appearancedefine.MAIN_PAGE_DECORATE, dExtendData = {
        'page': appearancedefine.SUB_PAGE_BUBBLE })


class CAppearanceAvatarFrm(appearancepagebase.CAppearancePageBase, combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_SelectAvatarFrmItem = 'SS_SelectAvatarFrmItem(dData)'
    SS_SelectBubbleItem = 'SS_SelectBubbleItem(dData)'
    SS_ClickUseItem = 'SS_ClickUseItem()'
    SS_ClickBuyItem = 'SS_ClickBuyItem()'
    SS_ClickRevertItem = 'SS_ClickRevertItem()'
    SS_ClickGiftItem = 'SS_ClickGiftItem()'
    
    def __init__(self, pContext, pMainDlg, iPage = 0):
        appearancepagebase.CAppearancePageBase.__init__(self, pContext, pMainDlg)
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog4/appearance_newstyle/decorate/decorate_zhuangshi.dlg')
        else:
            combdialog.CCombSubWnd.__init__(self, pMainDlg, 'dialog4/appearance_new/decorate/decorate_zhuangshi.dlg')
        self.ssInit()
        self.m_oTbView = self.GetObject('tbview')
        self.m_oChatSample = None
        self.m_oMapSample = None
        self.m_iSelItemIndex = -1
        self.m_oSelItemData = None
        self.m_iCurrentPage = iPage
        self.m_oTbView.SetDelegateNewCellOfData(self.TbDgtNewCellOfData)
        self.m_oTbView.SetDelegateUpdateCellOfData(self.TbDgtUpdateCellOfData)
        self.m_oTbView.SetShowRowLine(False)
        if permission.IsTestServerByNewYanzhiguan():
            self.m_oTbView.ResetTableType('LIST_APPEARANCE', None, False)
        else:
            self.m_oTbView.ResetTableType('LIST_STYLE_4', None, False)
        self.m_oTxtDecorateName = self.GetObject('txt_zhuangshiname')
        self.m_oTxtDecorateDay = self.GetObject('txt_zhuangshitime')
        self.m_oUseBtn = self.GetObject('btn_zhuangshiuse')
        self.m_oTxtDesc = self.GetObject('txt_zhuangshidesc')
        self.m_oImgTips = self.GetObject('img_tips')
        self.SetGiftBtnShow()
        self.CreateChatBubbleSample()
        self.m_pDelegate = delegateappearanceavatarfrm.CDelegateAvatarFrm(self, pContext)
        self.m_pDelegate.AfterInit(iPage)
        self.SetIgnoreEsc(True)
        self.InitDlg()

    
    def InitDlg(self):
        import permission
        oText = self.GetObject('txt_discount')
        if not permission.IsOpenQiXiAvatarDiscount() and oText:
            sTxt = '8\xa4\xeb23~25\xa4\xe9\xc1\xca\xb6R\xa1B\xc3\xd8\xb0e\xc0Y\xb9\xb3\xae\xd8\xa8\xc9\xa8\xfc8\xa7\xe9\xc0u\xb4f'
            oText.SetText(sTxt)
        

    
    def CreateChatBubbleSample(self):
        oLocChatSample = self.GetObject('loc_now')
        (iX, iY) = oLocChatSample.GetPos()
        (iW, iH) = oLocChatSample.GetSize()
        self.m_oChatSample = CChatSample(self, iW, iH, 0, 0)
        self.m_oChatSample.SetPos(iX, iY)

    
    def GetTableView(self):
        return self.m_oTbView

    
    def SetCurrentSelectItem(self, iIndex, oData, bUseEnable):
        self.m_iSelItemIndex = iIndex
        self.m_oSelItemData = oData
        self.SetDecorateNameAndDay(oData['name'], oData['day'], bUseEnable)

    
    def TbDgtNewCellOfData(self, oContainer, oData):
        oCell = CItemBox(oContainer, 100 + oData['idx'])
        oCell.SetClickCallback(self.OnSelectItemBox)
        return oCell

    
    def TbDgtUpdateCellOfData(self, oCell, oData, bReused):
        if oData['type'] == 0:
            oCell.CreateAvatarFrame(oData['id'])
        elif oData['type'] == 1:
            oCell.CreateBubble(oData['id'], oData['name'])
        else:
            oCell.ClearContent()
        bHaveMark = False
        if oData['type'] != -1:
            if oData['used']:
                oCell.SetUseMark(True)
                oCell.SetBuyMark(False)
                oCell.SetMark('')
                bHaveMark = True
            elif oData['day'] > 0 and self.m_iCurrentPage != 2:
                oCell.SetUseMark(False)
                oCell.SetBuyMark(True)
                oCell.SetMark('')
                bHaveMark = True
            elif self.m_iCurrentPage != 2:
                oCell.SetUseMark(False)
                oCell.SetBuyMark(False)
                oCell.SetMark(oData['mark'])
                bHaveMark = oData['mark'] is not None
            else:
                oCell.SetUseMark(False)
                oCell.SetBuyMark(False)
                oCell.SetMark('')
            oCell.SetData(oData)
            oCell.SetSelectable(True)
            oCell.SetIsSelected(oData['idx'] == self.m_iSelItemIndex)
        else:
            oCell.SetSelectable(False)
            oCell.SetIsSelected(False)
        if oData.get('bDiscount', False):
            pass
        oCell.SetDiscount(not bHaveMark)

    
    def ShowPage(self, iPage):
        if iPage == 0:
            self.GetObject('btn_touxiangkuang').LeftUp()
        elif iPage == 1:
            self.GetObject('btn_qipao').LeftUp()
        elif iPage == 2:
            self.GetObject('btn_wodezhuangshi').LeftUp()
        

    
    def GetTimeString(self, iTime):
        if self.m_iCurrentPage == 1:
            return '%d\xa4\xd1' % iTime
        else:
            iMin = iTime / 60
            iHour = iMin / 60
            iDay = iHour / 24
            if iDay:
                return '%d\xa4\xd1%d\xa4p\xae\xc9' % (iDay, iHour % 24)
            
            if iHour:
                return '%d\xa4p\xae\xc9%d\xa4\xc0\xc4\xc1' % (iHour, iMin % 60)
            
            return '%d\xa4\xc0\xc4\xc1' % iMin

    
    def SetDecorateNameAndDay(self, sName, iTime, bUseEnable = True, bBuyEnable = True):
        self.m_oTxtDecorateName.SetText(sName)
        if iTime == -1:
            self.m_oTxtDecorateDay.SetText('\xa5\xc3\xa4[')
            self.m_oUseBtn.SetText('\xa8\xcf\xa5\xce')
            self.m_oUseBtn.Enable(True)
        elif iTime:
            sTime = self.GetTimeString(iTime)
            self.m_oTxtDecorateDay.SetText(sTime)
            self.m_oTxtDecorateDay.SetShow(True)
            self.SetShowObject('txt_zhuangshitype', True)
        else:
            self.m_oTxtDecorateDay.SetShow(False)
            self.SetShowObject('txt_zhuangshitype', False)
        if iTime > 0:
            self.m_oUseBtn.SetText('\xa8\xcf\xa5\xce')
            self.m_oUseBtn.Enable(bUseEnable)
        else:
            self.m_oUseBtn.SetText('\xc1\xca\xb6R')
            self.m_oUseBtn.Enable(bBuyEnable)
        if sName == '\xbb\xf1\xb0\xc4\xa4\xf5':
            self.m_oImgTips.SetShow(True)
        else:
            self.m_oImgTips.SetShow(False)

    
    def SetDescText(self, dInfo, bDiscount):
        self.m_oTxtDesc.SetText(dInfo['desc'])
        self.SetPrice(dInfo, bDiscount)
        self.SetTime(dInfo)
        self.SetGetWay(dInfo)

    
    def SetPrice(self, dInfo, bDiscount):
        iPrice = dInfo['iPrice']
        bShowPrice = iPrice > 0
        if bShowPrice:
            self.GetObject('txt_price').SetText('%d\xa5@\xac\xc9\xb0^\xc4m\xab\xd7' % iPrice)
            self.GetObject('txt_oldprice').SetText('(%d#956)' % iPrice)
            self.GetObject('txt_newprice').SetText('%d#956' % dInfo['iNewPrice'])
        
        self.SetShowObject('txt_desc2', bShowPrice)
        if bShowPrice:
            pass
        self.SetShowObject('txt_price', not bDiscount)
        if bShowPrice:
            pass
        self.SetShowObject('txt_oldprice', bDiscount)
        if bShowPrice:
            pass
        self.SetShowObject('txt_newprice', bDiscount)
        if bShowPrice:
            pass
        self.SetShowObject('img_oldprice', bDiscount)
        self.SetShowObject('txt_discount', bDiscount)

    
    def SetTime(self, dInfo):
        iDay = dInfo['iDay']
        if iDay > 0:
            self.SetShowObject('txt_desc3', True)
            self.SetShowObject('txt_time', True)
            self.GetObject('txt_time').SetText('%d\xa4\xd1' % iDay)
        else:
            self.SetShowObject('txt_desc3', False)
            self.SetShowObject('txt_time', False)

    
    def SetGetWay(self, dInfo):
        sGetWay = dInfo['sGetWay']
        if sGetWay > 0:
            self.SetShowObject('txt_desc4', True)
            self.SetShowObject('txt_getway', True)
            self.GetObject('txt_getway').SetText(sGetWay)
        else:
            self.SetShowObject('txt_desc4', False)
            self.SetShowObject('txt_getway', False)

    
    def ShowMapSample(self, bShow, iBubbleType, sTxt):
        if bShow:
            if self.m_oMapSample is None:
                oLocMapPhoto = self.GetObject('loc_zhuangshishow')
                (iX, iY) = oLocMapPhoto.GetPos()
                (iW, iH) = oLocMapPhoto.GetSize()
                self.m_oMapSample = CMapSample(self, iW, iH, 0, 0)
                self.m_oMapSample.SetPos(iX, iY)
            
            self.m_oMapSample.SetShow(True)
            self.m_oMapSample.UpdateBubble(iBubbleType, sTxt)
        elif self.m_oMapSample:
            self.m_oMapSample.SetShow(False)
        

    
    def ShowChatSample(self, iAvatar, iBubble, sTxt):
        self.m_oChatSample.UpdateContent(iAvatar, iBubble, sTxt)

    
    def SetGiftBtnShow(self):
        self.GetObject('btn_give').SetShow(True)

    
    def OnSelectItemBox(self, oData):
        self.m_oSelItemData = oData
        self.m_iSelItemIndex = oData['idx']
        self.m_oTbView.Reload()
        bCanScroll = self.m_oTbView.GetCanScroll()
        self.m_oTbView.SetScorllBarShow(bCanScroll)
        if oData['type'] == 0:
            self.ssEmit(self.SS_SelectAvatarFrmItem, oData)
        elif oData['type'] == 1:
            self.ssEmit(self.SS_SelectBubbleItem, oData['id'])
        

    
    def GetSelectedItemData(self):
        return self.m_oSelItemData

    
    def RightUp(self):
        if hasattr(self.GetParent(), 'RightUp'):
            self.GetParent().RightUp()
        

    
    def VOpenPage(self, dExtend = None):
        self.m_pDelegate.OnOpenPage(dExtend)

    
    def VClose(self):
        self.m_pDelegate.OnClose()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 18:
            self.m_iSelItemIndex = -1
            self.m_oSelItemData = None
            self.ssEmit(self.SS_ClickRevertItem)
        elif iMsgID in (13, 19):
            if self.m_oSelItemData:
                iDay = self.m_oSelItemData['day']
                if iDay == -1 or iDay > 0:
                    self.ssEmit(self.SS_ClickUseItem)
                else:
                    self.ssEmit(self.SS_ClickBuyItem)
            
        elif iMsgID == 1:
            self.ssEmit(self.SS_ClickGiftItem)
        



class CChatSample(interface.CBoxObject):
    
    def __init__(self, *args):
        interface.CBoxObject.__init__(self, *args)
        self.m_oChatBubbleLeft = None
        self.m_oChatBubbleRight = None
        self.m_iStyle = 3

    
    def SetStyle(self, iStyle):
        self.m_iStyle = iStyle

    
    def UpdateContent(self, iAvatar, iBubble, sTxt):
        import avatar
        tAvatarArr = avatar.PhotoArr2Int(avatar.GetHeroPhoto())
        (iW, iH) = self.GetSize()
        self.m_oChatBubbleLeft = CChatSampleCell(self, iW, int(iH * 0.5), 0, 0)
        self.m_oChatBubbleLeft.CreateBubble(iBubble, sTxt, tAvatarArr, iAvatar, False, self.m_iStyle)
        (iBubbleW, iBubbleH) = self.m_oChatBubbleLeft.GetSize()
        self.m_oChatBubbleLeft.SetPos(0, (iH - iBubbleH) / 2)



class CChatAvatar(interface.CBoxObject):
    
    def __init__(self, oParent, iW, iH, tAvatarArr):
        interface.CBoxObject.__init__(self, oParent, iW, iH, 0, 0)
        (sP1, sP2, sP3, sP4) = tAvatarArr
        self.m_oAvatar = avatar.GetSmallImgBy4Int(self, long(sP1), long(sP2), long(sP3), long(sP4))



class CChatSampleCell(interface.CBoxObject):
    LINE_MARGINE = 8
    AVATAR_SIZE = 50
    
    def __init__(self, *args):
        interface.CBoxObject.__init__(self, *args)
        (self.m_iWidth, self.m_iHeight) = self.GetSize()
        self.m_oTxt = None
        self.m_oBubble = None
        self.m_oBubbleArrow = None
        self.m_oAvatar = None
        self.m_oAvatarFrame = None
        self.m_oAvatarBg = None

    
    def CreateBubble(self, iBubbleType, sContent, tAvatarArr, iAvatarFrm, bRight, iStyle = 3):
        import hero
        if iBubbleType == 0 or iBubbleType == -1:
            iBubbleType = None if bRight else -1
        
        if iAvatarFrm < 0:
            iAvatarFrm = 0
        
        sBubblePath = chatbubbledata.GetChatTalkBubblePath(iBubbleType)
        (iBubbleOffX, iBubbleOffY, iBubbleOffW, iBubbleOffH) = chatbubbledata.GetChatTalkBubbleOffPos(iBubbleType)
        iBubbleMinW = chatbubbledata.GetChatTalkBubbleMinWidth(iBubbleType)
        iAvatarW = self.AVATAR_SIZE + self.LINE_MARGINE
        iRichTxtMaxW = self.m_iWidth - iAvatarW - iBubbleOffW
        self.m_oTxt = wrapinterface.WrapRichText(self, iRichTxtMaxW, interface.FontLT14, sContent, 16777215)
        (iTxtContentW, iTxtContentH) = self.m_oTxt.GetSize()
        iBubbleW = \xde\xd2\xcb(iTxtContentW + iBubbleOffW, iBubbleMinW)
        iBubbleH = iTxtContentH + iBubbleOffH
        self.m_oBubble = ui.CBitmapFrame(self, iBubbleW, iBubbleH, sBubblePath, interface.UIPath)
        self.m_oAvatar = CChatAvatar(self, self.AVATAR_SIZE, self.AVATAR_SIZE, tAvatarArr)
        import avatarfrmdata
        if avatarfrmdata.IsOldAvatarFrm(iAvatarFrm):
            sMaskBgPath = 'combdialog4/\xd4\xd3\xcd\xbc/\xc1\xc4\xcc\xec\xb4\xb0\xbf\xda\xb1\xb3\xbe\xb0/\xc1\xc4\xcc\xec\xcd\xb7\xcf\xf1\xbf\xf2\xb5\xd7\xb0\xe5/%02d.png' % iStyle
            self.m_oAvatarBg = ui.CImage(self.m_oAvatar, sMaskBgPath, interface.UIPath)
            self.m_oAvatarBg.SetZ(2)
            interface.Center(self.m_oAvatarBg)
        
        if iAvatarFrm:
            dAvatarFrmInfo = avatarfrmdata.GetAvatarFrmInfo(iAvatarFrm)
            self.m_oAvatarFrame = ui.CImage(self.m_oAvatar, dAvatarFrmInfo['path'], interface.UIPath)
            self.m_oAvatarFrame.SetZ(3)
            interface.Center(self.m_oAvatarFrame, dAvatarFrmInfo['offsetx'], dAvatarFrmInfo['offsety'])
        
        avatar.UpdateAvatarPal(self.m_oAvatar.m_oAvatar, hero.GetHeroID())
        iX = iAvatarW
        iY = -(self.LINE_MARGINE)
        self.m_oBubble.SetPos(iX, iY + 10)
        self.m_oTxt.SetPos(iX + iBubbleOffX, iY + iBubbleOffY + 10)
        (iX, iY) = (0, 0)
        self.m_oAvatar.SetPos(iX, iY)



class CMapSample(interface.CBoxObject):
    
    def __init__(self, *args):
        interface.CBoxObject.__init__(self, *args)
        self.m_oMapCanvas = None
        self.m_oPlayer = None
        self.m_oBubble = None
        self.CreateMapPhoto()

    
    def CreateMapPhoto(self):
        '''\xb3\xd0\xab\xd8\xa6a\xb9\xcf\xb9\xcf\xa4\xf9\xa5H\xa4\xce\xa4H\xaa\xab\xa8v\xb9\xb3'''
        import map
        import hero
        import walker
        import ratio
        import war
        import copy
        iDHight = 75
        (iW, iH) = self.GetSize()
        self.m_oMapCanvas = interface.CCanvasObject(self, iW, iH)
        if not hero.GetProp('m_Shape'):
            return None
        
        dDesc = hero.GetProp('m_Desc')
        oDescCopy = copy.deepcopy(dDesc)
        if 'horse' in oDescCopy:
            del oDescCopy['horse']
        
        if 'track' in oDescCopy:
            del oDescCopy['track']
        
        self.m_oPlayer = walker.CreateFakeWalker(self.m_oMapCanvas, 1, hero.GetProp('m_Shape'), oDescCopy)
        oBack = map.GetGameMapObject()
        if oBack:
            self.m_oMapCanvas.BlitFrom(oBack, -(ratio.WINDOW_WIDTH - iW) / 2, -(ratio.WINDOW_HEIGHT / 2 - (self.m_oPlayer.GetAddonH() + iDHight)))
        else:
            oBack = war.GetBackGround()
            self.m_oMapCanvas.BlitTreeFrom(oBack, -(ratio.WINDOW_WIDTH - iW) / 2, -(ratio.WINDOW_HEIGHT / 2 - (self.m_oPlayer.GetAddonH() + iDHight)))
        if not oBack:
            oBack = interface.MainPanel
            self.m_oMapCanvas.BlitFrom(oBack, -(ratio.WINDOW_WIDTH - iW) / 2, -(ratio.WINDOW_HEIGHT / 2 - (self.m_oPlayer.GetAddonH() + iDHight)))
        
        self.m_oPlayer.SetPos(iW / 2, self.m_oPlayer.GetAddonH() + iDHight)

    
    def UpdateBubble(self, iType, sTxt):
        self.m_oBubble = CItemBox(self.m_oPlayer, 0, False)
        self.m_oBubble.SetSelectable(False)
        self.m_oBubble.SetPos(-55, -self.m_oPlayer.GetAddonH() - 36 - 10)
        self.m_oBubble.SetZ(201)
        self.m_oBubble.CreateBubble(iType, sTxt)



class CItemBox(combdialog.CCombSubWnd):
    
    def __init__(self, parent, iMsgid, bShowBg = True):
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombSubWnd.__init__(self, parent, 'dialog4/appearance_newstyle/decorate/decorate_itemnew.dlg')
        else:
            combdialog.CCombSubWnd.__init__(self, parent, 'dialog4/decorate/decorate_itemnew.dlg')
        self.m_oText = None
        self.m_oBubbleImgList = []
        self.m_oBubbleBox = None
        self.m_oBuyMark = None
        self.m_bIsSel = False
        self.m_bShowBg = bShowBg
        self.m_oUseMark = None
        self.m_oMark = None
        self.m_oAvatarFrm = None
        self.m_oSelBox = None
        self.m_oData = 0
        self.m_funcClickCallback = None
        self.m_bSelectable = True
        self.m_iMsgId = iMsgid
        if not self.m_bShowBg:
            self.GetObject('loc_bg').SetShow(False)
        
        self.SetShowObject('img_discount', False)
        self.SetSelectBoxShow(False)
        self.SetIgnoreEsc(True)

    
    def SetClickCallback(self, func):
        import misc
        self.m_funcClickCallback = misc.Functor(func)

    
    def SetSelectable(self, bSelectable):
        self.m_bSelectable = bSelectable

    
    def SetData(self, oData):
        self.m_oData = oData

    
    def SetIsSelected(self, bIsSel):
        self.m_bIsSel = bIsSel
        self.SetSelectBoxShow(self.m_bIsSel)

    
    def SetSelectBoxShow(self, bShow):
        if permission.IsTestServerByNewYanzhiguan():
            self.SetShowObject('frame_choose', bShow)
        elif self.m_oSelBox:
            self.m_oSelBox.SetShow(bShow)
        else:
            (iW, iH) = self.GetSize()
            self.m_oSelBox = ui.CFrame(self, iW, iH, 'combdialog/\xd0\xc2\xca\xd6\xd6\xb8\xd2\xfd\xb1\xdf\xbf\xf2/')
            self.m_oSelBox.SetShow(bShow)

    
    def ClearContent(self):
        self.m_oText = None
        self.m_oBubbleBox = None
        self.m_oBubbleImgList = []
        self.m_oAvatarFrm = None
        self.SetUseMark(False)
        self.SetBuyMark(False)
        self.SetMark('')

    
    def CreateAvatarFrame(self, iType):
        self.m_oText = None
        self.m_oBubbleBox = None
        self.m_oBubbleImgList = []
        import avatarfrmdata
        dAvatarFrmInfo = avatarfrmdata.GetAvatarFrmInfo(iType)
        if dAvatarFrmInfo:
            self.m_oAvatarFrm = ui.CImage(self, dAvatarFrmInfo['path'], interface.UIPath)
            interface.Center(self.m_oAvatarFrm)
        

    
    def CreateBubble(self, iType, sMsg):
        self.m_oAvatarFrm = None
        import wrapinterface
        iColor = chatbubbledata.GetSceneTalkBubbleColor(iType)
        if iType == 0:
            iColor = 16777215
        
        if self.m_oText is None:
            self.m_oText = wrapinterface.WrapRichText(self, 200, interface.FontLT14_19, sMsg, iColor)
        else:
            self.m_oText.SetText(sMsg)
        interface.Center(self.m_oText)
        (iTextW, iTextH) = self.m_oText.GetSize()
        iTextW += 6
        iTextH += 6
        self.m_oBubbleBox = interface.CBoxObject(self, iTextW, iTextH, 0, 0)
        interface.Center(self.m_oBubbleBox)
        (iMsgW, iMsgH) = self.m_oText.GetSize()
        sTopPath = chatbubbledata.GetSceneTalkBubblePath(iType)
        sPointPath = chatbubbledata.GetSenceTalkBubblePointPath(iType)
        if iType:
            oEdgeList = drawedge.DrawNewNinePalaceEdge(self.m_oBubbleBox, iType, sTopPath, iMsgW, iMsgH, sPointPath, True)
        elif chatbubbledata.IsNewNinePalace(sTopPath):
            oEdgeList = drawedge.DrawNewNinePalaceEdge(self.m_oBubbleBox, iType, sTopPath, iMsgW, iMsgH, sPointPath, True)
        else:
            oEdgeList = wrapinterface.DrawEdge(self.m_oBubbleBox, iTextW, iTextH, has_point = True)
        self.m_oBubbleImgList = oEdgeList

    
    def Enter(self):
        if self.m_bSelectable:
            self.SetSelectBoxShow(True)
        

    
    def Leave(self):
        if not self.m_bIsSel:
            self.SetSelectBoxShow(False)
        

    
    def LeftUp(self):
        if self.m_funcClickCallback is not None and self.m_bSelectable:
            self.m_funcClickCallback(self.m_oData)
        

    
    def LeftDown(self):
        pass

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def SetBuyMark(self, bIsBuy):
        if permission.IsTestServerByNewYanzhiguan():
            self.GetObject('img_had').SetShow(bIsBuy)
        elif bIsBuy:
            if self.m_oBuyMark is None:
                self.m_oBuyMark = ui.CImage(self, 'combdialog4/\xc1\xc4\xcc\xec\xc6\xb5\xb5\xc0/\xd2\xd1\xd3\xb5\xd3\xd0.png', interface.UIPath)
                self.m_oBuyMark.SetZ(1)
                self.m_oBuyMark.SetPos(-5, -5)
            else:
                self.m_oBuyMark.SetShow(True)
        elif self.m_oBuyMark:
            self.m_oBuyMark.SetShow(False)
        

    
    def SetUseMark(self, bIsUse):
        if permission.IsTestServerByNewYanzhiguan():
            self.GetObject('img_use').SetShow(bIsUse)
        elif bIsUse:
            self.m_oUseMark = ui.CImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/useing.png', interface.UIPath)
            self.m_oUseMark.SetZ(1)
            self.m_oUseMark.SetPos(-7, -7)
        else:
            self.m_oUseMark = None

    
    def SetMark(self, sMarkPath):
        if sMarkPath and len(sMarkPath) > 0:
            if permission.IsTestServerByNewYanzhiguan():
                self.m_oMark = ui.CImage(self.GetObject('loc_jiaobiao'), sMarkPath, interface.UIPath)
            else:
                self.m_oMark = ui.CImage(self, sMarkPath, interface.UIPath)
                self.m_oMark.SetZ(1)
                self.m_oMark.SetPos(-5, -5)
        else:
            self.m_oMark = None

    
    def SetDiscount(self, bShow):
        oImage = self.GetObject('img_discount')
        if oImage:
            oImage.SetShow(bShow)
            oImage.SetZ(1)
